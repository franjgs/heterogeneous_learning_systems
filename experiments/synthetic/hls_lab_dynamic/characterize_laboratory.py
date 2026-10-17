"""Small paired pilot characterizing existing HLS dynamic policies only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from random import Random
from time import time

from hls.hls_lab_dynamic import (
    CompetenceInformationMode as Info,
    DemandRegime,
    DiscoverBeliefPolicy,
    LearningProfile,
    UncertainProblem,
    generate_uncertain_problems,
    run_belief_sequence,
)
from hls.hls_lab_v1 import ExploreThenGreedy, GreedyAdaptive, OrganizationState, ProblemSpec, make_team

SEEDS = tuple(range(4))
N_PROBLEMS = 8
SIGMA = 0.08
SKILL_SIGMA = 0.06
PRIOR = 0.5
BOOTSTRAPS = 2000
BOOTSTRAP_SEED = 20261015

EAST = DemandRegime("east", ((0.65, 0.15), (0.15, 0.65), (0.35, 0.35)), (0.5, 0.25, 0.25))
WEST = DemandRegime("west", ((0.15, 0.65), (0.65, 0.15), (0.35, 0.35)), (0.25, 0.5, 0.25))
SAME = DemandRegime("stationary", ((0.65, 0.15), (0.15, 0.65), (0.35, 0.35)), (0.4, 0.3, 0.3))

SIMILAR = ((0.55, 0.45), (0.55, 0.45), (0.55, 0.45))
HETEROGENEOUS = ((0.82, 0.18), (0.18, 0.82), (0.50, 0.50))
PARTIAL_ESTIMATE = ((0.55, 0.45), (0.55, 0.45), (0.55, 0.45))
SLOW = LearningProfile(((0.03, 0.03),) * 3)
FAST = LearningProfile(((0.25, 0.25),) * 3)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sequence(seed: int, changing: bool, n: int = N_PROBLEMS):
    schedule = ((SAME, n),) if not changing else ((EAST, n // 2), (WEST, n - n // 2))
    generated = generate_uncertain_problems(
        schedule, problem_seed=91000 + seed, environment_seed=92000 + seed,
        prior=PRIOR, budget=3.0,
    )
    # Existing observer only: unit cost per effort is recorded but does not
    # enter actions, CES reward, or competence transitions.
    return tuple(UncertainProblem(replace(item.problem, resource_cost_per_unit=1.0), item.theta)
                 for item in generated)


def execute(policy, seed, problems, team_kind, mode, learning, li, horizon,
            *, lo=False, org_state=None):
    real = SIMILAR if team_kind == "similar" else HETEROGENEOUS
    info_mode = Info(mode)
    team = make_team(real) if info_mode == Info.ORACLE else make_team(real)
    if info_mode != Info.ORACLE:
        from hls.hls_lab_dynamic import make_dynamic_team
        team = make_dynamic_team(real, information_mode=info_mode,
                                 estimated_competencies=PARTIAL_ESTIMATE)
    return run_belief_sequence(
        team, problems, policy, learning=learning, decision_horizon=horizon,
        individual_learning=li, organizational_learning=lo,
        prior=PRIOR, sigma=SIGMA, noise_seed=93000 + seed,
        competence_observation_sigma=SKILL_SIGMA,
        competence_noise_seed=94000 + seed,
        information_mode=info_mode, initial_organization_state=org_state,
        competence_estimator="three_point",
    )


def summarize(result, block, scenario, seed, phase="sequence"):
    records = result.records
    n = len(records)
    real_error = [abs(x - y) for r in records
                  for row_x, row_y in zip(r.episode.estimated_before, r.episode.competence_before)
                  for x, y in zip(row_x, row_y)]
    if scenario.startswith("switching"):
        boundary = n // 2 if block == "organization_train_eval" else N_PROBLEMS // 2
    else:
        boundary = None
    first = [r for r in records if boundary is None or r.problem_episode < boundary]
    second = [r for r in records if boundary is not None and r.problem_episode >= boundary]
    return {
        "block": block, "scenario": scenario, "phase": phase,
        "policy": result.policy, "seed": seed,
        "decisions": n,
        "functional_success_rate": sum(r.episode.success for r in records) / n,
        "cumulative_ces_mu_true": result.cumulative_true_expected_reward,
        "resource_cost": sum(r.episode.resource_cost for r in records),
        "effort": sum(r.episode.effort for r in records),
        "mean_estimation_absolute_error": sum(real_error) / len(real_error) if real_error else 0.0,
        "organization_updates": result.final_organization.update_count,
        "unique_actions": len({r.episode.action_id for r in records}),
        "first_segment_mean_reward": sum(r.true_expected_reward for r in first) / max(len(first), 1),
        "second_segment_mean_reward": sum(r.true_expected_reward for r in second) / len(second) if second else "",
    }


def decision_rows(result, block, scenario, seed, phase="sequence"):
    updates = 0
    for r in result.records:
        e = r.episode
        updates += int(e.organization_updated)
        yield {
            "block": block, "scenario": scenario, "phase": phase, "policy": result.policy,
            "seed": seed, "problem_episode": r.problem_episode,
            "decision_in_problem": r.decision_in_problem,
            "problem_id": e.problem_id, "environment": r.true_environment_type,
            "belief_before": r.belief_before, "belief_after": r.belief_after,
            "action_id": e.action_id, "success": int(e.success),
            "mu_true": r.true_expected_reward, "resource_cost": e.resource_cost,
            "effort": e.effort, "competence_real_before": json.dumps(e.competence_before),
            "competence_real_after": json.dumps(e.competence_after),
            "competence_estimated_before": json.dumps(e.estimated_before),
            "competence_estimated_after": json.dumps(e.estimated_after),
            "organization_updated_this_decision": int(e.organization_updated),
            "organization_updates_after": updates,
            "organization_theta_before": json.dumps(e.organization_theta_before),
            "organization_theta_after": json.dumps(e.organization_theta_after),
            "organization_action_changed": int(e.organization_action_changed),
        }


def paired_ci(differences, seed):
    rng = Random(seed)
    n = len(differences)
    means = []
    for _ in range(BOOTSTRAPS):
        means.append(sum(differences[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return sum(differences) / n, means[int(.025 * BOOTSTRAPS)], means[int(.975 * BOOTSTRAPS)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path,
                        default=Path("results/experiments/hls_dynamic_characterization"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    summaries, decisions = [], []
    paired: dict[tuple, dict[int, dict[str, float]]] = {}

    def add(block, scenario, seed, arm, result):
        summaries.append(summarize(result, block, scenario, seed, arm.get("phase", "sequence")))
        decisions.extend(decision_rows(result, block, scenario, seed, arm.get("phase", "sequence")))
        return result

    # Planning/information contrast: one-factor scenarios around a declared base.
    plan_cases = [
        ("stationary_similar", False, "similar", "slow"),
        ("switching_similar", True, "similar", "slow"),
        ("stationary_heterogeneous", False, "heterogeneous", "slow"),
        ("switching_heterogeneous", True, "heterogeneous", "slow"),
    ]
    for name, changing, team_kind, rate_name in plan_cases:
        learning = FAST if rate_name == "fast" else SLOW
        for horizon in (1, 3):
            scenario = f"{name}_H{horizon}"
            for seed in SEEDS:
                problems = sequence(seed, changing)
                arms = [
                    ("GREEDY_ORACLE_LI_OFF", GreedyAdaptive(), "ORACLE", False),
                    ("DISCOVER_ORACLE_LI_OFF", DiscoverBeliefPolicy(), "ORACLE", False),
                    ("GREEDY_PARTIAL_STATIC_LI_OFF", GreedyAdaptive(), "PARTIAL_STATIC", False),
                    ("GREEDY_PARTIAL_LEARNING_LI_OFF", GreedyAdaptive(), "PARTIAL_LEARNING", False),
                    ("GREEDY_ORACLE_LI_ON", GreedyAdaptive(), "ORACLE", True),
                    ("GREEDY_ORACLE_LI_OFF_FAST", GreedyAdaptive(), "ORACLE", False),
                    ("GREEDY_ORACLE_LI_ON_FAST", GreedyAdaptive(), "ORACLE", True),
                ]
                by_arm = {}
                for name_arm, policy, mode, li in arms:
                    arm_learning = FAST if name_arm.endswith("FAST") else learning
                    result = add("factorial_contrasts", scenario, seed,
                                 {"phase": name_arm},
                                 execute(policy, seed, problems, team_kind, mode,
                                         arm_learning, li, horizon))
                    by_arm[name_arm] = result
                for lhs, rhs, contrast in (
                    ("DISCOVER_ORACLE_LI_OFF", "GREEDY_ORACLE_LI_OFF", "planning_minus_greedy"),
                    ("GREEDY_PARTIAL_STATIC_LI_OFF", "GREEDY_ORACLE_LI_OFF", "partial_static_minus_oracle"),
                    ("GREEDY_PARTIAL_LEARNING_LI_OFF", "GREEDY_PARTIAL_STATIC_LI_OFF", "partial_updated_minus_static"),
                    ("GREEDY_ORACLE_LI_ON", "GREEDY_ORACLE_LI_OFF", "individual_learning_on_minus_off"),
                    ("GREEDY_ORACLE_LI_ON_FAST", "GREEDY_ORACLE_LI_OFF_FAST", "individual_fast_learning_on_minus_off"),
                ):
                    key = (scenario, contrast)
                    left, right = by_arm[lhs], by_arm[rhs]
                    paired.setdefault(key, {})[seed] = {
                        "reward": left.cumulative_true_expected_reward - right.cumulative_true_expected_reward,
                        "success": sum(r.episode.success for r in left.records) - sum(r.episode.success for r in right.records),
                        "cost": sum(r.episode.resource_cost for r in left.records) - sum(r.episode.resource_cost for r in right.records),
                        "effort": sum(r.episode.effort for r in left.records) - sum(r.episode.effort for r in right.records),
                    }
                fast_learning_key = (scenario, "fast_on_minus_slow_on")
                paired.setdefault(fast_learning_key, {})[seed] = {
                    "reward": by_arm["GREEDY_ORACLE_LI_ON_FAST"].cumulative_true_expected_reward - by_arm["GREEDY_ORACLE_LI_ON"].cumulative_true_expected_reward,
                    "success": sum(r.episode.success for r in by_arm["GREEDY_ORACLE_LI_ON_FAST"].records) - sum(r.episode.success for r in by_arm["GREEDY_ORACLE_LI_ON"].records),
                    "cost": sum(r.episode.resource_cost for r in by_arm["GREEDY_ORACLE_LI_ON_FAST"].records) - sum(r.episode.resource_cost for r in by_arm["GREEDY_ORACLE_LI_ON"].records),
                    "effort": sum(r.episode.effort for r in by_arm["GREEDY_ORACLE_LI_ON_FAST"].records) - sum(r.episode.effort for r in by_arm["GREEDY_ORACLE_LI_ON"].records),
                }

    # Organizational learning control: identical fixed task context and LI-off.
    # Train at least one full arm sweep; then evaluate with theta frozen.
    from hls.discover_v0 import THETA_1
    org_problem = UncertainProblem(ProblemSpec("org-context", (0.35, 0.35), 3.0, resource_cost_per_unit=1.0), THETA_1)
    org_team = "heterogeneous"
    for changing in (False, True):
        scenario = "org_switching" if changing else "org_stationary"
        # Each context receives a complete 64-arm training sweep. Evaluation
        # then switches contexts, so the tabular policy is tested on both.
        east_task = UncertainProblem(ProblemSpec("org-east", (0.65, 0.15), 3.0, resource_cost_per_unit=1.0), THETA_1)
        west_task = UncertainProblem(ProblemSpec("org-west", (0.15, 0.65), 3.0, resource_cost_per_unit=1.0), THETA_1)
        for seed in SEEDS:
            train = ((east_task,) * 64 + (west_task,) * 64) if changing else (org_problem,) * 64
            evaluation = ((east_task,) * 16 + (west_task,) * 16) if changing else (org_problem,) * 32
            org_evaluations = {}
            for learns in (False, True):
                policy = ExploreThenGreedy()
                initial = OrganizationState()
                trained = execute(policy, seed, train, org_team, "ORACLE", SLOW,
                                  False, 1, lo=learns, org_state=initial)
                frozen_state = trained.final_organization
                evaluated = execute(policy, seed, evaluation, org_team, "ORACLE", SLOW,
                                    False, 1, lo=False, org_state=frozen_state)
                add("organization_train_eval", scenario, seed,
                    {"phase": f"TRAIN_LO_{'ON' if learns else 'OFF'}"}, trained)
                add("organization_train_eval", scenario, seed,
                    {"phase": f"EVAL_LO_{'ON' if learns else 'OFF'}"}, evaluated)
                org_evaluations[learns] = evaluated
            left, right = org_evaluations[True], org_evaluations[False]
            paired.setdefault((scenario, "organizational_update_eval"), {})[seed] = {
                "reward": left.cumulative_true_expected_reward - right.cumulative_true_expected_reward,
                "success": sum(r.episode.success for r in left.records) - sum(r.episode.success for r in right.records),
                "cost": sum(r.episode.resource_cost for r in left.records) - sum(r.episode.resource_cost for r in right.records),
                "effort": sum(r.episode.effort for r in left.records) - sum(r.episode.effort for r in right.records),
            }

    run_csv = args.output_dir / "run_summary.csv"
    with run_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(summaries)
    decision_csv = args.output_dir / "decision_traces.csv"
    with decision_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(decisions[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(decisions)

    contrasts = []
    for (scenario, contrast), by_seed in sorted(paired.items()):
        for outcome in ("reward", "success", "cost", "effort"):
            mean, lo, hi = paired_ci([by_seed[s][outcome] for s in SEEDS], BOOTSTRAP_SEED)
            contrasts.append({"scenario": scenario, "contrast": contrast, "outcome": outcome,
                              "mean_paired_difference": mean, "bootstrap_95_low": lo,
                              "bootstrap_95_high": hi, "paired_seeds": len(SEEDS),
                              "bootstrap_replicates": BOOTSTRAPS})
    contrast_path = args.output_dir / "paired_contrasts.csv"
    with contrast_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(contrasts[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(contrasts)
    manifest = {
        "protocol": "hls-dynamic-characterization-pilot-v1",
        "created_unix": time(), "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "python": sys.version, "platform": platform.platform(), "seeds": list(SEEDS),
        "problems_per_sequence": N_PROBLEMS, "horizons": [1, 3],
        "sigma": SIGMA, "skill_observation_sigma": SKILL_SIGMA, "belief_prior": PRIOR,
        "bootstrap_seed": BOOTSTRAP_SEED, "bootstrap_replicates": BOOTSTRAPS,
        "no_new_policy_or_physics": True,
        "source_hashes": {p: sha(Path(p)) for p in (
            "src/hls/hls_lab_dynamic.py", "src/hls/hls_lab_v1.py",
            "experiments/synthetic/hls_lab_dynamic/characterize_laboratory.py")},
        "artifact_sha256": {p.name: sha(p) for p in (run_csv, decision_csv, contrast_path)},
        "runs": len(summaries), "decisions": len(decisions),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output_dir": str(args.output_dir), **manifest}, sort_keys=True))


if __name__ == "__main__":
    main()
