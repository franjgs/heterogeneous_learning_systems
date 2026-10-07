"""Frozen policy restrictions: closed loops and Q11-reference counterfactuals."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.synthetic.campaign1.run import CONFIG_BY_ID
from hls.campaign1_protocol import CONFIGURATION_IDS, PARAMETERS, SCENARIO_IDS, SEEDS, validate_protocol
from hls.campaign1_test_range import CONTAMINATION_STATUS, HISTORIES, history_steps
from hls.discover_develop_v2 import mis_v2_transition
from hls.discover_v0 import DEFAULT_SIGMA, EXACT_TOL, JOINT_ACTIONS, ces_reward, production_inputs
from hls.finite_problem_belief import (
    ProspectivePolicyMode, canonical_model, expected_reward, finite_bayes_update,
    hypothesis_means, prospective_action_values,
)
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR

OUT = ROOT / "results/diagnostics/strategy_discrimination_gate"
MODE_BY_ID = dict(zip(("Q00", "Q10", "Q01", "Q11"), ProspectivePolicyMode))
PAIRS = tuple(combinations(MODE_BY_ID, 2))


def packed(value):
    return json.dumps(value, separators=(",", ":"))


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def design_manifest():
    """Written before execution; no result-dependent design decisions."""
    freeze = ROOT / "results/foundations/policy_ablation/pre_experiment_policy_ablation.json"
    frozen = json.loads(freeze.read_text())
    if frozen["validation"]["Q11_maximum_absolute_discrepancy"] != 0:
        raise AssertionError("Q11 prerequisite regression missing")
    subprocess.run(["git", "merge-base", "--is-ancestor", "3cf4eec", "HEAD"], cwd=ROOT, check=True)
    validate_protocol()
    return {
        "gate_id": "strategy-discrimination-gate-v1", "is_campaign2": False,
        "initial_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "policy_ablation_commit": "3cf4eec", "audit_commit": "7f0df6f",
        "scenario_ids": SCENARIO_IDS, "configurations": CONFIGURATION_IDS,
        "seeds": SEEDS, "policies": {k: v.name for k, v in MODE_BY_ID.items()},
        "parameters": PARAMETERS,
        "expected_counts": {"closed_loop_runs": 1280, "real_decisions": 23040,
            "primary_reference_states": 5760, "primary_nonterminal_states": 3840,
            "paired_state_policy_rows": 23040, "pairwise_state_rows": 34560},
        "primary_state_rule": "all real pre-decision states visited by Q11; no outcome selection",
        "secondary_union_audit": "not run: optional additional all-policy-state evaluation increases cost; primary covers every Q11 state",
        "action_distance": "sum_i,k abs(Xa[i,k]-Xb[i,k]); exact equality also retained",
        "tie_definition": "mutual tolerance optimality: each chosen action is within EXACT_TOL of the other operator maximum",
        "tie_tolerance": EXACT_TOL,
        "opportunity_cost": "g(left action)-g(right action) on exactly the same Q11 reference state; raw signed values retained",
        "crn": "Random(seed), one gauss(0,1) draw per real step, same stream across all scenarios/configurations/policies",
        "real_transitions": "every policy calls unchanged finite_bayes_update and mis_v2_transition(enabled=True)",
        "performance": "sum of mu_true; observed reward used for inference only",
        "classification_criteria": {
            "PASS": "non-trivial interpretable nonterminal divergence beyond ties, structural variation, useful nulls; no required performance winner",
            "PARTIAL": "genuine but sparse, concentrated, single-pattern-dominated or weak discrimination",
            "FAIL": "essential action equivalence, tie/numerical artifacts, or failed operator isolation"},
        "source_hashes": {str(p.relative_to(ROOT)): file_hash(p) for p in [
            freeze, ROOT / "src/hls/finite_problem_belief.py", ROOT / "src/hls/discover_develop_v2.py",
            ROOT / "src/hls/discover_v0.py", ROOT / "src/hls/campaign1_test_range.py",
            ROOT / "results/campaigns/campaign1_test_range/runs.csv",
            ROOT / "results/campaigns/campaign1_test_range/trajectories.csv"]},
    }


@lru_cache(maxsize=2048)
def evaluate(state, belief, remaining, policy_id):
    # Exact memoization only; no rounding or state coarsening.
    information, development = MODE_BY_ID[policy_id].value
    values = prospective_action_values(state, belief, HYPOTHESIS_REPERTOIRE,
        remaining=remaining, eta=PARAMETERS["eta"],
        anticipate_information=information, anticipate_development=development)
    maximum = max(values.values())
    action = next(x for x in JOINT_ACTIONS if abs(values[x] - maximum) <= EXACT_TOL)
    return action, maximum, values


def action_l1(left, right):
    return sum(abs(a-b) for lr, rr in zip(left, right) for a, b in zip(lr, rr))


def pattern(actions):
    a, i, d, c = (actions[k] for k in MODE_BY_ID)
    if a == i == d == c:
        return "ALL_SAME"
    if i == a and d == a and c != a:
        return "COUPLED_ONLY"
    if i != a and d == a:
        return "INFORMATION_SENSITIVE"
    if i == a and d != a:
        return "DEVELOPMENT_SENSITIVE"
    if i != a and d != a:
        return "BOTH_SINGLE_ABLATIONS_CHANGE"
    return "OTHER_MIXED"


def counterfactual_rows(key, state, belief, remaining):
    evaluated = {p: evaluate(state, belief, remaining, p) for p in MODE_BY_ID}
    actions = {p: result[0] for p, result in evaluated.items()}
    g = {p: expected_reward(belief, hypothesis_means(state, a, HYPOTHESIS_REPERTOIRE)) for p, a in actions.items()}
    rows, pairs = [], []
    for p, (a, maximum, values) in evaluated.items():
        rows.append({**key, "reference_policy": "Q11", "terminal": remaining == 1,
            "policy": p, "action": packed(a), "selected_objective": values[a],
            "maximum_objective": maximum, "immediate_g": g[p],
            "state_before": packed(state), "belief_before": packed(belief),
            "pattern": pattern(actions),
            **{f"objective_of_{other}_action": values[actions[other]] for other in MODE_BY_ID}})
    for left, right in PAIRS:
        la, lm, lv = evaluated[left]
        ra, rm, rv = evaluated[right]
        lregret = lm - lv[ra]
        rregret = rm - rv[la]
        pairs.append({**key, "terminal": remaining == 1,
            "policy_pair": left + "_" + right, "exact_different": la != ra,
            "action_l1": action_l1(la, ra),
            "left_regret_of_right": lregret, "right_regret_of_left": rregret,
            "mutual_tie_equivalent": lregret <= EXACT_TOL and rregret <= EXACT_TOL,
            "beyond_mutual_tie": la != ra and (lregret > EXACT_TOL or rregret > EXACT_TOL),
            "both_reject_alternative": lregret > EXACT_TOL and rregret > EXACT_TOL,
            "immediate_left_minus_right": g[left] - g[right]})
    if remaining == 1 and len(set(actions.values())) != 1:
        raise AssertionError("terminal collapse failure")
    return rows, pairs


def run_task(task):
    scenario, configuration, seed = task
    runs, trajectories, decisions, comparisons = [], [], [], []
    model, reset_prior = canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    descriptors = history_steps(scenario)
    for policy_id in MODE_BY_ID:
        state, rng, cumulative = CONFIG_BY_ID[configuration], Random(seed), 0.0
        exposure = [[0.0, 0.0] for _ in range(3)]
        problem_performance = []
        for problem_index, true_problem in enumerate(HISTORIES[scenario]):
            belief, problem_total = reset_prior, 0.0
            descriptor = descriptors[problem_index]
            for step in range(3):
                key = {"scenario_id": scenario, "configuration_id": configuration, "seed": seed,
                    "problem_index": problem_index, "within_problem_step": step,
                    "p": true_problem[0], "represented": descriptor.represented}
                remaining = 3-step
                if policy_id == "Q11":
                    cf, cp = counterfactual_rows(key, state, belief, remaining)
                    decisions.extend(cf); comparisons.extend(cp)
                action = evaluate(state, belief, remaining, policy_id)[0]
                predicted = hypothesis_means(state, action, model)
                mu_true = ces_reward(production_inputs(state, action), true_problem)
                innovation = rng.gauss(0.0, 1.0)
                observed = mu_true + DEFAULT_SIGMA * innovation
                posterior = finite_bayes_update(belief, observed, predicted, DEFAULT_SIGMA)
                next_state = mis_v2_transition(state, action, enabled=True, eta=PARAMETERS["eta"])
                exposure_before = packed(exposure)
                for i in range(3):
                    for k in range(2):
                        exposure[i][k] += action[i][k]
                cumulative += mu_true; problem_total += mu_true
                trajectories.append({**key, "policy": policy_id, "point": descriptor.label,
                    "true_problem": packed(true_problem), "C_t": descriptor.change,
                    "N_t": descriptor.novelty, "M_t": descriptor.mismatch,
                    "belief_before": packed(belief), "belief_after": packed(posterior),
                    "state_before": packed(state), "state_after": packed(next_state),
                    "action": packed(action), "exposure_before": exposure_before,
                    "exposure_after": packed(exposure),
                    "development_increment": packed(tuple(tuple(next_state[i][k]-state[i][k] for k in range(2)) for i in range(3))),
                    "mu_true": mu_true, "observed_reward": observed,
                    "noise_innovation": innovation, "cumulative_performance": cumulative})
                state, belief = next_state, posterior
            problem_performance.append(problem_total)
        runs.append({"scenario_id": scenario, "configuration_id": configuration, "seed": seed,
            "policy": policy_id, "cumulative_performance": cumulative,
            "problem_performance": packed(problem_performance),
            "last_problem_performance": problem_performance[-1],
            "last_problem_is_initial_recurrence": HISTORIES[scenario][-1] == HISTORIES[scenario][0],
            "final_state": packed(state), "final_exposure": packed(exposure),
            "contamination_status": CONTAMINATION_STATUS[scenario]})
    return runs, trajectories, decisions, comparisons


def main(workers):
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "closed_loop_runs.csv").exists():
        raise RuntimeError("gate results already exist; refuse silent regeneration")
    manifest = design_manifest()
    (OUT / "execution_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
    tasks = [(s,c,seed) for s in SCENARIO_IDS for c in CONFIGURATION_IDS for seed in SEEDS]
    accumulated = [[], [], [], []]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for n, result in enumerate(executor.map(run_task, tasks, chunksize=1), 1):
            for dest, rows in zip(accumulated, result):
                dest.extend(rows)
            if n % 20 == 0:
                print(f"Completed {n}/{len(tasks)} scenario/configuration/seed blocks", flush=True)
    for filename, rows in zip(("closed_loop_runs.csv", "closed_loop_trajectories.csv",
                              "paired_state_decisions.csv", "paired_state_comparisons.csv"), accumulated):
        write_csv(OUT / filename, rows)
    print("Execution complete; historical regression and integrity validation required before interpretation", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    main(parser.parse_args().workers)
