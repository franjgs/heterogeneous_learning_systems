"""Execute the minimal development-only Campaign 3 Gate 2 factual audit."""

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
from hls.campaign3_problem_generator import generator_transition  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

GATE1_COMMIT = "f336be8"
TEAM_SPLIT = ROOT / "results" / "foundations" / "campaign3_team_split" / "team_split.csv"
KERNEL_SPLIT = ROOT / "results" / "foundations" / "campaign3_generator_split" / "kernel_split.csv"
OUT = ROOT / "results" / "diagnostics" / "campaign3_gate2"
BEHAVIORS = ("D00", "D10", "D01", "D11", "DbetaU")
MODES = ("Q00", "Q10", "Q01", "Q11")
FIXED_MODE = {"D00": "Q00", "D10": "Q10", "D01": "Q01", "D11": "Q11"}
ACTION_IDS = {action: index for index, action in enumerate(JOINT_ACTIONS)}
FILES = {"histories": "factual_histories.csv.gz", "states": "factual_states.csv.gz"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**63 - 1)


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@lru_cache(maxsize=300_000)
def select_action(state, belief, remaining: int, mode_id: str):
    return planner.choose_prospective_action(
        state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining,
        policy_mode=MODE_BY_ID[mode_id], eta=PARAMETERS["eta"],
    )[0]


def diagnostic_actions(state, belief, remaining: int):
    """Evaluate every mode; use the frozen terminal-collapse identity at H=1."""
    if remaining == 1:
        action = select_action(state, belief, remaining, "Q00")
        return {mode: action for mode in MODES}
    return {mode: select_action(state, belief, remaining, mode) for mode in MODES}


def make_tasks() -> list[dict[str, object]]:
    teams = [row for row in read_rows(TEAM_SPLIT) if row["partition"] == "development"]
    kernels = [row for row in read_rows(KERNEL_SPLIT) if row["split_role"] == "development"]
    if len(teams) != 20 or len(kernels) != 21:
        raise RuntimeError("frozen development split mismatch")
    tasks = []
    for team in teams:
        matrix = tuple(tuple(float(team[f"s{i}{k}"]) for k in (1, 2)) for i in (1, 2, 3))
        for kernel in kernels:
            sigma = kernel["sigma"]
            parameters = (
                float(kernel["alpha_stay"]), float(kernel["alpha_move"]),
                float(kernel["alpha_return"]), None if sigma == "" else float(sigma),
            )
            for replicate in range(5):
                namespace = ("campaign3_gate2_v1", team["team_id"], kernel["kernel_id"], replicate)
                seeds = {
                    "problem_seed": stable_seed(*namespace, "problem"),
                    "noise_seed": stable_seed(*namespace, "noise"),
                    "other_seed": stable_seed(*namespace, "other"),
                    "beta_mode_seed": stable_seed(*namespace, "beta_mode"),
                }
                for behavior in BEHAVIORS:
                    tasks.append({
                        "history_index": len(tasks), "history_id": ":".join(map(str, (*namespace, behavior))),
                        "team_id": team["team_id"], "kernel_id": kernel["kernel_id"],
                        "replicate": replicate, "behavior": behavior, "team": matrix,
                        "kernel": parameters, **seeds,
                    })
    if len(tasks) != 10_500:
        raise RuntimeError("Gate 2 task count mismatch")
    return tasks


def generate_exogenous(task: dict[str, object]):
    problem_rng = np.random.default_rng(int(task["problem_seed"]))
    noise_rng = np.random.default_rng(int(task["noise_seed"]))
    problems = [float(problem_rng.uniform(0.2, 0.8))]
    for _ in range(11):
        problems.append(generator_transition(problems, task["kernel"], problem_rng).p_next)
    return tuple(problems), tuple(float(x) for x in noise_rng.standard_normal(36))


def execute_history(task: dict[str, object]):
    problems, innovations = generate_exogenous(task)
    beta_rng = np.random.default_rng(int(task["beta_mode_seed"]))
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    state = task["team"]
    state_rows = []
    selected_modes = []
    for problem_index, p in enumerate(problems):
        belief = prior
        true_problem = (p, 1.0 - p)
        for step in range(3):
            global_step = 3 * problem_index + step
            before_state, before_belief = state, belief
            actions = diagnostic_actions(before_state, before_belief, 3 - step)
            behavior = str(task["behavior"])
            factual_mode = FIXED_MODE.get(behavior)
            if factual_mode is None:
                factual_mode = MODES[int(beta_rng.integers(0, 4))]
            selected_modes.append(factual_mode)
            factual_action = actions[factual_mode]
            real = theory._real_decision(
                before_state, before_belief, factual_action, true_problem, innovations[global_step], model
            )
            state_rows.append({
                "state_id": int(task["history_index"]) * 36 + global_step,
                "history_id": task["history_id"], "team_id": task["team_id"],
                "kernel_id": task["kernel_id"], "replicate": task["replicate"],
                "behavior": behavior, "problem_index": problem_index + 1, "decision": step + 1,
                "clock": global_step + 1, "tau": 36 - global_step,
                "state_before": packed(before_state), "belief_before": packed(before_belief),
                **{f"action_{mode}": ACTION_IDS[action] for mode, action in actions.items()},
                "K_X": len(set(actions.values())), "factual_mode": factual_mode,
                "factual_action_id": ACTION_IDS[factual_action],
                "state_after": packed(real.state_after), "belief_after": packed(real.belief_after),
            })
            state, belief = real.state_after, real.belief_after
    history_row = {
        "history_index": task["history_index"], "history_id": task["history_id"],
        "team_id": task["team_id"], "kernel_id": task["kernel_id"],
        "replicate": task["replicate"], "behavior": task["behavior"],
        "problem_seed": task["problem_seed"], "noise_seed": task["noise_seed"],
        "other_seed": task["other_seed"], "beta_mode_seed": task["beta_mode_seed"],
        "problem_stream_sha256": hashlib.sha256(packed(problems).encode()).hexdigest(),
        "noise_stream_sha256": hashlib.sha256(packed(innovations).encode()).hexdigest(),
        "selected_modes": packed(selected_modes), "J": 12, "state_count": 36,
    }
    return {"histories": [history_row], "states": state_rows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    subprocess.run(["git", "merge-base", "--is-ancestor", GATE1_COMMIT, "HEAD"], cwd=ROOT, check=True)
    if OUT.exists():
        raise RuntimeError("refusing to overwrite Gate 2 output")
    tasks = make_tasks()
    OUT.mkdir(parents=True)
    dump(OUT / "execution_manifest.json", {
        "artifact_type": "campaign3_gate2_minimal_hybrid_state_coverage",
        "prerequisite_gate1_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "design": {"teams": 20, "kernels": 21, "replicates": 5, "behaviors": list(BEHAVIORS), "histories": 10500, "states": 378000, "J": 12},
        "seed_namespace": "campaign3_gate2_v1/team_id/kernel_id/replicate/stream",
        "CRN": "problem/noise/other seeds identical across behavior policies within team/kernel/replicate; beta mode seed is separate",
        "diagnostic_modes": list(MODES), "counterfactual_value_targets": 0,
        "selector_observable": ["S", "b", "tau"], "heldout_execution": False,
        "gate_2_only": True, "predictor_or_metacontroller_training": False,
        "source_sha256": {"team_split.csv": digest(TEAM_SPLIT), "kernel_split.csv": digest(KERNEL_SPLIT)},
    })

    def progress(results):
        for count, result in enumerate(results, 1):
            yield result
            if count % 100 == 0:
                print(f"histories {count}/{len(tasks)}", flush=True)

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        counts, metadata = persist_tables(progress(pool.map(execute_history, tasks, chunksize=1)), OUT, FILES)
    expected = {"histories": 10500, "states": 378000}
    if counts != expected:
        raise IOError(f"persisted counts {counts} != {expected}")
    dump(OUT / "raw_completion.json", {
        "finished_utc": datetime.now(timezone.utc).isoformat(), "counts": counts,
        "persisted_file_metadata": metadata,
        "sha256": {name: digest(OUT / name) for name in FILES.values()},
        "counterfactual_value_targets": 0, "heldout_execution": False,
    })
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
