"""Execute the frozen initial J=12 Campaign 3 horizon pilot."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign2_prospective_adaptation.artifact_io import persist_tables  # noqa: E402
from experiments.synthetic.strategy_discrimination_gate.run import MODE_BY_ID  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.campaign1_protocol import PARAMETERS  # noqa: E402
from hls.campaign3_problem_generator import descriptor_rows, generator_transition  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

PREREG_COMMIT = "a984893eb2f5c1f863707d43ae911e5a0c29692d"
FREEZE = ROOT / "results" / "foundations" / "campaign3_horizon_pilot"
OUT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
FILES = {
    "histories": "factual_histories.csv",
    "states": "factual_states.csv.gz",
    "branches": "counterfactual_branch_returns.csv.gz",
    "pairs": "counterfactual_pairs.csv.gz",
}
ACTION_IDS = {action: index for index, action in enumerate(JOINT_ACTIONS)}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=200_000)
def select_action(state, belief, remaining: int, mode_id: str):
    return planner.choose_prospective_action(
        state,
        belief,
        HYPOTHESIS_REPERTOIRE,
        remaining=remaining,
        policy_mode=MODE_BY_ID[mode_id],
        eta=PARAMETERS["eta"],
    )[0]


def generate_history(task: dict[str, object]):
    problem_rng = np.random.default_rng(int(task["physical_problem_seed"]))
    noise_rng = np.random.default_rng(int(task["observation_noise_seed"]))
    p_values = [float(problem_rng.uniform(0.2, 0.8))]
    mechanisms = ["INITIAL"]
    transition_flags = [{"return_unavailable": None, "renormalized": None, "reflected": None}]
    kernel = task["kernel"]
    for _ in range(11):
        transition = generator_transition(p_values, kernel, problem_rng)
        p_values.append(transition.p_next)
        mechanisms.append(transition.mechanism)
        transition_flags.append({
            "return_unavailable": transition.return_unavailable,
            "renormalized": transition.renormalized,
            "reflected": transition.reflected,
        })
    innovations = tuple(float(value) for value in noise_rng.standard_normal(36))
    return tuple(p_values), tuple(mechanisms), tuple(transition_flags), innovations


def rollout(
    state,
    belief,
    problems,
    innovations,
    *,
    start_problem: int,
    start_step: int,
    forced_action,
    continuation: str,
):
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    current_state, current_belief = state, belief
    cumulative = 0.0
    returns = []
    action_ids = []
    first_real = None
    first = True
    for problem_index in range(start_problem, 12):
        if problem_index > start_problem:
            current_belief = prior
        first_step = start_step if problem_index == start_problem else 0
        true_problem = (problems[problem_index], 1.0 - problems[problem_index])
        for step in range(first_step, 3):
            global_step = 3 * problem_index + step
            if first:
                action = forced_action
            else:
                action = select_action(current_state, current_belief, 3 - step, continuation)
            real = theory._real_decision(
                current_state, current_belief, action, true_problem, innovations[global_step], model
            )
            if first:
                first_real = real
                first = False
            action_ids.append(ACTION_IDS[action])
            cumulative += real.mu_true
            current_state, current_belief = real.state_after, real.belief_after
        returns.append(cumulative)
    assert first_real is not None
    action_hash = hashlib.sha256(packed(action_ids).encode("ascii")).hexdigest()
    return tuple(returns), first_real, action_hash


def execute_history(task: dict[str, object]):
    history_rows, state_rows, branch_rows, pair_rows = [], [], [], []
    problems, mechanisms, flags, innovations = generate_history(task)
    changes, novelties, mismatches = descriptor_rows(problems)
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    state = task["team"]
    factual_total = 0.0
    history_index = int(task["history_index"])
    history_id = str(task["base_history_id"])

    for problem_index, p in enumerate(problems):
        belief = prior
        true_problem = (p, 1.0 - p)
        for step in range(3):
            global_step = 3 * problem_index + step
            state_id = history_index * 36 + global_step
            actions = {mode: select_action(state, belief, 3 - step, mode) for mode in MODE_BY_ID}
            factual_action = actions["Q11"]

            # Evaluate the full problem-indexed return once per unique first
            # action and continuation; exact duplicates are then materialized
            # for every conceptual mode/continuation branch.
            branch_by_key = {}
            for continuation in ("Q00", "Q11"):
                by_action = {}
                for mode in ("Q00", "Q10", "Q01", "Q11"):
                    action = actions[mode]
                    action_id = ACTION_IDS[action]
                    if action_id not in by_action:
                        by_action[action_id] = rollout(
                            state,
                            belief,
                            problems,
                            innovations,
                            start_problem=problem_index,
                            start_step=step,
                            forced_action=action,
                            continuation=continuation,
                        )
                    branch_by_key[(mode, continuation)] = by_action[action_id]

            for continuation in ("Q00", "Q11"):
                baseline = branch_by_key[("Q00", continuation)][0]
                for mode in ("Q00", "Q10", "Q01", "Q11"):
                    returns, first_real, action_hash = branch_by_key[(mode, continuation)]
                    for ell, value in enumerate(returns):
                        branch_rows.append({
                            "state_id": state_id,
                            "history_id": history_id,
                            "team_id": task["team_id"],
                            "kernel_id": task["kernel_id"],
                            "replicate": task["replicate"],
                            "problem_index": problem_index + 1,
                            "decision": step + 1,
                            "initial_mode": mode,
                            "continuation": continuation,
                            "ell": ell,
                            "first_action_id": ACTION_IDS[actions[mode]],
                            "G": value,
                            "first_mu_true": first_real.mu_true,
                            "first_observation": first_real.observation,
                            "first_epsilon": first_real.epsilon,
                            "branch_action_sequence_sha256": action_hash,
                        })
                for mode in ("Q10", "Q01", "Q11"):
                    returns = branch_by_key[(mode, continuation)][0]
                    previous = None
                    for ell, (value, base) in enumerate(zip(returns, baseline, strict=True)):
                        delta_total = value - base
                        pair_rows.append({
                            "state_id": state_id,
                            "history_id": history_id,
                            "team_id": task["team_id"],
                            "kernel_id": task["kernel_id"],
                            "replicate": task["replicate"],
                            "problem_index": problem_index + 1,
                            "decision": step + 1,
                            "mode": mode,
                            "continuation": continuation,
                            "ell": ell,
                            "mode_action_id": ACTION_IDS[actions[mode]],
                            "reference_action_id": ACTION_IDS[actions["Q00"]],
                            "action_divergent": actions[mode] != actions["Q00"],
                            "G_mode": value,
                            "G_Q00": base,
                            "Delta": delta_total,
                            "delta": "" if previous is None else delta_total - previous,
                        })
                        previous = delta_total

            real = theory._real_decision(
                state, belief, factual_action, true_problem, innovations[global_step], model
            )
            state_rows.append({
                "state_id": state_id,
                "history_id": history_id,
                "team_id": task["team_id"],
                "kernel_id": task["kernel_id"],
                "replicate": task["replicate"],
                "simulator_seed": task["simulator_seed"],
                "problem_index": problem_index + 1,
                "decision": step + 1,
                "remaining": 3 - step,
                "p": p,
                "C": "" if changes[problem_index] is None else changes[problem_index],
                "N": "" if novelties[problem_index] is None else novelties[problem_index],
                "M": mismatches[problem_index],
                "state_before": packed(state),
                "belief_before": packed(belief),
                **{f"action_{mode}": ACTION_IDS[action] for mode, action in actions.items()},
                "factual_action_id": ACTION_IDS[factual_action],
                "epsilon": innovations[global_step],
                "mu_true": real.mu_true,
                "observation": real.observation,
                "belief_after": packed(real.belief_after),
                "state_after": packed(real.state_after),
            })
            factual_total += real.mu_true
            state, belief = real.state_after, real.belief_after

    history_rows.append({
        "history_index": history_index,
        "history_id": history_id,
        "team_id": task["team_id"],
        "kernel_id": task["kernel_id"],
        "replicate": task["replicate"],
        "simulator_seed": task["simulator_seed"],
        "physical_problem_seed": task["physical_problem_seed"],
        "observation_noise_seed": task["observation_noise_seed"],
        "other_exogenous_seed": task["other_exogenous_seed"],
        "problems": packed(problems),
        "mechanisms": packed(mechanisms),
        "transition_flags": packed(flags),
        "observation_innovations": packed(innovations),
        "factual_source_policy": "Q11",
        "J": 12,
        "factual_cumulative_mu_true": factual_total,
        "final_state": packed(state),
    })
    return {"histories": history_rows, "states": state_rows, "branches": branch_rows, "pairs": pair_rows}


def load_tasks() -> list[dict[str, object]]:
    design = {(row["team_id"], row["kernel_id"]): row for row in read_csv(FREEZE / "pilot_design.csv")}
    allocation = [row for row in read_csv(FREEZE / "seed_allocation.csv") if row["allocation"] == "initial"]
    tasks = []
    for history_index, row in enumerate(allocation):
        design_row = design[(row["team_id"], row["kernel_id"])]
        sigma = design_row["sigma"]
        tasks.append({
            "history_index": history_index,
            "team_id": row["team_id"],
            "kernel_id": row["kernel_id"],
            "replicate": int(row["replicate"]),
            "base_history_id": row["base_history_id"],
            "simulator_seed": int(row["simulator_seed"]),
            "physical_problem_seed": int(row["physical_problem_seed"]),
            "observation_noise_seed": int(row["observation_noise_seed"]),
            "other_exogenous_seed": int(row["other_exogenous_seed"]),
            "team": tuple(tuple(float(design_row[f"s{i}{k}"]) for k in (1, 2)) for i in (1, 2, 3)),
            "kernel": (
                float(design_row["alpha_stay"]),
                float(design_row["alpha_move"]),
                float(design_row["alpha_return"]),
                None if sigma == "" else float(sigma),
            ),
        })
    if len(tasks) != 840:
        raise RuntimeError("frozen initial allocation must contain 840 histories")
    return tasks


def preflight() -> dict:
    subprocess.run(["git", "merge-base", "--is-ancestor", PREREG_COMMIT, "HEAD"], cwd=ROOT, check=True)
    freeze = json.loads((FREEZE / "pre_execution_horizon_pilot.json").read_text())
    if freeze["execution_status"]["pilot_histories_generated"] != 0:
        raise RuntimeError("pre-execution freeze is contaminated")
    if OUT.exists():
        raise RuntimeError("refusing to overwrite horizon-pilot output")
    return freeze


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    freeze = preflight()
    tasks = load_tasks()
    OUT.mkdir(parents=True)
    manifest_path = OUT / "execution_manifest.json"
    dump(manifest_path, {
        "artifact_type": "campaign3_horizon_pilot_initial_j12_execution",
        "preregistration_commit": PREREG_COMMIT,
        "code_base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "execution_code_sha256": digest(Path(__file__)),
        "pre_execution_manifest_sha256": digest(FREEZE / "pre_execution_horizon_pilot.json"),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "design": freeze["size"],
        "J": 12,
        "factual_source": "Q11",
        "initial_modes": ["Q00", "Q10", "Q01", "Q11"],
        "continuations": ["Q00", "Q11"],
        "performance": "mu_true",
        "CRN": freeze["crn_semantics"],
        "heldout_execution": False,
        "gate_1_analysis": False,
        "gate_2_analysis": False,
        "escalation_histories": 0,
    })

    def progress(results):
        for completed, result in enumerate(results, 1):
            yield result
            if completed % 20 == 0:
                print(f"histories {completed}/{len(tasks)}", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        counts, metadata = persist_tables(
            progress(pool.map(execute_history, tasks, chunksize=1)), OUT, FILES
        )
    expected = {"histories": 840, "states": 30_240, "branches": 1_572_480, "pairs": 1_179_360}
    if counts != expected:
        raise IOError(f"raw count mismatch: {counts} != {expected}")
    dump(OUT / "raw_completion.json", {
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
        "expected_counts": expected,
        "persisted_file_metadata": metadata,
        "sha256": {path.name: digest(path) for path in OUT.iterdir() if path.is_file()},
        "escalation_histories_generated": 0,
    })
    print(json.dumps(counts, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
