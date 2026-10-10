"""Generate C3.2 raw Monte-Carlo counterfactual targets from frozen allocation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_gate2.run import ACTION_IDS, diagnostic_actions, stable_seed  # noqa: E402
from experiments.synthetic.strategy_discrimination_gate.run import MODE_BY_ID  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.campaign1_protocol import PARAMETERS  # noqa: E402
from hls.campaign3_problem_generator import generator_transition  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

FOUNDATION = ROOT / "results" / "foundations" / "campaign3_c32_data"
GATE2 = ROOT / "results" / "diagnostics" / "campaign3_gate2"
SPLIT = ROOT / "results" / "foundations" / "campaign3_generator_split" / "kernel_split.csv"
MODES = ("Q00", "Q10", "Q01", "Q11")
CONTINUATIONS = ("Q00", "Q11")
ELL = 11


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


@lru_cache(maxsize=300_000)
def select_action(state, belief, remaining: int, mode: str):
    return planner.choose_prospective_action(
        state, belief, HYPOTHESIS_REPERTOIRE, remaining=remaining,
        policy_mode=MODE_BY_ID[mode], eta=PARAMETERS["eta"],
    )[0]


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def kernel_map() -> dict[str, tuple[float, float, float, float | None]]:
    answer = {}
    for row in rows(SPLIT):
        if row["split_role"] == "development":
            answer[row["kernel_id"]] = (
                float(row["alpha_stay"]), float(row["alpha_move"]), float(row["alpha_return"]),
                None if row["sigma"] == "" else float(row["sigma"]),
            )
    if len(answer) != 21:
        raise RuntimeError("frozen development kernel map invalid")
    return answer


def realized_prefix(problem_seed: int, kernel, current_problem_zero: int) -> tuple[float, ...]:
    """Recreate p_1..p_j from the Gate-2 factual generator draw."""
    rng = np.random.default_rng(problem_seed)
    values = [float(rng.uniform(0.2, 0.8))]
    while len(values) <= current_problem_zero:
        values.append(generator_transition(values, kernel, rng).p_next)
    return tuple(values)


def conditional_future(history_prefix: tuple[float, ...], kernel, seed: int) -> tuple[float, ...]:
    """Fresh conditional generator draw: preserve prefix, draw exactly ell future problems."""
    rng = np.random.default_rng(seed)
    values = list(history_prefix)
    future = []
    for _ in range(ELL):
        transition = generator_transition(values, kernel, rng)
        values.append(transition.p_next)
        future.append(transition.p_next)
    return tuple(future)


def rollout(state, belief, current_p: float, future_p: tuple[float, ...], eps: tuple[float, ...], *, step: int, forced_action, continuation: str):
    """One raw CRN-paired realization through current remainder plus ell problems."""
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    current_state, current_belief = state, belief
    reward = 0.0
    action_ids = []
    noise_index = 0
    sequence = (current_p,) + future_p
    first = True
    for relative_problem, p in enumerate(sequence):
        if relative_problem:
            current_belief = prior
        first_step = step if relative_problem == 0 else 0
        for within_problem in range(first_step, 3):
            if first:
                action = forced_action
                first = False
            else:
                action = select_action(current_state, current_belief, 3 - within_problem, continuation)
            real = theory._real_decision(
                current_state, current_belief, action, (p, 1.0 - p), eps[noise_index], model
            )
            reward += real.mu_true
            action_ids.append(ACTION_IDS[action])
            current_state, current_belief = real.state_after, real.belief_after
            noise_index += 1
    expected_noise = (3 - step) + 3 * ELL
    if noise_index != expected_noise:
        raise RuntimeError("incorrect ell=11 reward horizon")
    return reward, tuple(action_ids), current_state, current_belief


def target_rows(task: dict[str, object]) -> list[dict[str, object]]:
    state = tuple(tuple(float(x) for x in row) for row in json.loads(task["state_before"]))
    belief = tuple(float(x) for x in json.loads(task["belief_before"]))
    clock, problem_index, decision = int(task["clock"]), int(task["problem_index"]), int(task["decision"])
    step = decision - 1
    kernel = task["kernel"]
    prefix = realized_prefix(int(task["problem_seed"]), kernel, problem_index - 1)
    if len(prefix) != problem_index:
        raise RuntimeError("physical prefix reconstruction failed")
    future_seed = stable_seed("campaign3_c32_data_v1", task["history_id"], clock, "conditional_future")
    noise_seed = stable_seed("campaign3_c32_data_v1", task["history_id"], clock, "counterfactual_noise")
    future = conditional_future(prefix, kernel, future_seed)
    eps = tuple(float(x) for x in np.random.default_rng(noise_seed).standard_normal((3 - step) + 3 * ELL))
    actions = diagnostic_actions(state, belief, 3 - step)
    for mode in MODES:
        if ACTION_IDS[actions[mode]] != int(task[f"action_{mode}"]):
            raise RuntimeError("recomputed frozen mode action differs from Gate 2 diagnostic action")
    by_continuation: dict[tuple[str, int], tuple[float, tuple[int, ...]]] = {}
    for continuation in CONTINUATIONS:
        for action in dict.fromkeys(actions.values()):
            value, sequence, _, _ = rollout(
                state, belief, prefix[-1], future, eps, step=step, forced_action=action, continuation=continuation
            )
            by_continuation[(continuation, ACTION_IDS[action])] = (value, sequence)
    result = []
    for continuation in CONTINUATIONS:
        baseline = by_continuation[(continuation, ACTION_IDS[actions["Q00"]])][0]
        for mode in MODES:
            value, action_sequence = by_continuation[(continuation, ACTION_IDS[actions[mode]])]
            result.append({
                "history_id": task["history_id"], "selected_state_id": task["selected_state_id"],
                "partition": task["partition"], "team_id": task["team_id"], "kernel_id": task["kernel_id"],
                "behavior": task["behavior"], "replicate": task["replicate"], "clock": clock,
                "initial_mode": mode, "continuation": continuation, "ell": ELL,
                "initial_action_id": ACTION_IDS[actions[mode]], "K_X": len(set(actions.values())),
                "raw_mc_G": value, "advantage_vs_Q00": value - baseline,
                "future_problem_seed": future_seed, "counterfactual_noise_seed": noise_seed,
                "future_problem_sha256": hashlib.sha256(packed(future).encode()).hexdigest(),
                "noise_sha256": hashlib.sha256(packed(eps).encode()).hexdigest(),
                "action_sequence_sha256": hashlib.sha256(packed(action_sequence).encode()).hexdigest(),
            })
    return result


def tasks(limit: int | None, partition: str | None = None) -> list[dict[str, object]]:
    allocation = pd.read_csv(FOUNDATION / "history_clock_assignment.csv").sort_values("history_id")
    selected = pd.read_csv(GATE2 / "factual_states.csv.gz")
    selected = selected.merge(allocation[["history_id", "selected_clock", "selected_state_id", "partition"]], on="history_id")
    selected = selected[(selected.clock == selected.selected_clock) & (selected.state_id == selected.selected_state_id)].copy()
    histories = pd.read_csv(GATE2 / "factual_histories.csv.gz", usecols=["history_id", "problem_seed"])
    selected = selected.merge(histories, on="history_id", validate="one_to_one")
    if len(selected) != 10_500:
        raise RuntimeError("allocation must select exactly one factual state per history")
    if partition is not None:
        selected = selected[selected.partition == partition].copy()
    if limit is not None:
        selected = selected.iloc[:limit]
    kernels = kernel_map()
    output = []
    for row in selected.to_dict("records"):
        row["kernel"] = kernels[row["kernel_id"]]
        output.append(row)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show frozen design; default behavior")
    parser.add_argument("--smoke", action="store_true", help="run two deterministic diagnostic labels in a separate directory")
    parser.add_argument("--execute", action="store_true", help="generate a bounded explicit subset")
    parser.add_argument("--full", action="store_true", help="allow all 10,500 selected states only with --execute")
    parser.add_argument("--limit", type=int, help="selected-state limit for --execute")
    parser.add_argument("--partition", choices=("TRAIN", "VALIDATION", "DEVELOPMENT_TEST"), help="write one frozen allocation partition")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if not (args.dry_run or args.smoke or args.execute):
        args.dry_run = True
    if args.full and not args.execute:
        parser.error("--full requires --execute")
    if args.execute and args.limit is None and not args.full:
        parser.error("--execute requires --limit, or explicit --full")
    if sum(bool(value) for value in (args.dry_run, args.smoke, args.execute)) != 1:
        parser.error("choose exactly one execution mode")
    if args.dry_run:
        print(json.dumps({"selected_states": 10500, "conceptual_labels": 84000, "ell": ELL, "default_launches_targets": False}))
        return
    available = 2 if args.smoke else (2100 if args.partition in ("VALIDATION", "DEVELOPMENT_TEST") else 6300 if args.partition == "TRAIN" else 10_500)
    limit = 2 if args.smoke else (available if args.full else args.limit)
    if limit > available:
        parser.error("--limit exceeds selected allocation scope")
    if args.smoke:
        out = ROOT / "results" / "diagnostics" / "campaign3_c32_data_smoke"
    elif args.partition:
        out = ROOT / "results" / "campaigns" / "campaign3_c32_data" / args.partition.lower()
    else:
        out = ROOT / "results" / "campaigns" / "campaign3_c32_data"
    if out.exists():
        raise RuntimeError("refusing to overwrite target output")
    selected_tasks = tasks(limit, args.partition)
    if args.workers == 1:
        generated = [target_rows(task) for task in selected_tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            generated = list(pool.map(target_rows, selected_tasks, chunksize=1))
    flattened = [row for rows_ in generated for row in rows_]
    result = pd.DataFrame(flattened).sort_values(["history_id", "continuation", "initial_mode"])
    expected = limit * 8
    if len(result) != expected:
        raise RuntimeError("conceptual target count mismatch")
    if not (result[result.initial_mode == "Q00"].advantage_vs_Q00.abs() == 0.0).all():
        raise RuntimeError("Q00 advantage must be exactly zero")
    out.mkdir(parents=True)
    table = out / "raw_mc_targets.csv.gz"
    result.to_csv(table, index=False, compression="gzip")
    manifest = {
        "artifact_type": "campaign3_c32_data_raw_mc_target_generation", "smoke": args.smoke,
        "selected_states": limit, "partition": args.partition, "conceptual_labels": expected, "ell": ELL,
        "actual_rollouts": int(sum(2 * rows_[0]["K_X"] for rows_ in generated)),
        "future_draw": "fresh conditional generator continuation given realized physical prefix",
        "CRN": "identical future problem sequence and observation innovations for all modes/continuations within selected state",
        "allocation_sha256": digest(FOUNDATION / "history_clock_assignment.csv"),
        "targets_sha256": digest(table), "target_interpretation": "single raw Monte-Carlo realization; not exact conditional expectation",
    }
    (out / "execution_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
