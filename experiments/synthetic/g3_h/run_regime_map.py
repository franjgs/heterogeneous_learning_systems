"""Run the deterministic Phase-I G3-H USE/local/oracle regime map."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g3_h_regime_map import (  # noqa: E402
    REGIME_TOL,
    controlled_learning_profiles,
    evaluate_point,
    grid_states,
    summarize_regrets,
)


OUTPUT = ROOT / "results" / "foundations" / "g3_h_regime_map"
CORE = ROOT / "src" / "hls" / "g3_organizational_value.py"
G3H = ROOT / "src" / "hls" / "g3_h_organizational_value.py"
REGIME_MAP = ROOT / "src" / "hls" / "g3_h_regime_map.py"
RUNNER = Path(__file__).resolve()
CANONICAL_STATE = ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8))
CANONICAL_PROFILE = (0.4, 0.6, 0.4)
PHASE_I_VALUES = (0.0, 0.5, 1.0)
SMOKE_VALUES = (0.0, 0.5)
ETA = 0.4
DELTA = 0.2


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _action(action: tuple[int, int]) -> list[int]:
    return [action[0] + 1, action[1] + 1]


def _actions(actions: frozenset[tuple[int, int]]) -> str:
    return json.dumps([_action(action) for action in sorted(actions)])


def _state_columns(prefix: str, state) -> dict[str, float]:
    return {
        f"{prefix}_w1_a": state[0][0],
        f"{prefix}_w1_b": state[0][1],
        f"{prefix}_w2_a": state[1][0],
        f"{prefix}_w2_b": state[1][1],
        f"{prefix}_w3_a": state[2][0],
        f"{prefix}_w3_b": state[2][1],
    }


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    if not rows:
        raise ValueError("cannot write an empty result table")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _profiles() -> tuple[tuple[float, float, float], ...]:
    profiles = set(controlled_learning_profiles(ETA, DELTA))
    profiles.add(CANONICAL_PROFILE)
    return tuple(sorted(profiles))


def _states(values: tuple[float, ...]):
    seen = set()
    for state in grid_states(values):
        if state not in seen:
            seen.add(state)
            yield state
    if CANONICAL_STATE not in seen:
        yield CANONICAL_STATE


def _canonical_hard_gate() -> None:
    evaluation = evaluate_point(CANONICAL_STATE, CANONICAL_PROFILE)
    actions = {item.action: item for item in evaluation.actions}
    xa, xb = (1, 2), (2, 0)
    tolerance = REGIME_TOL
    expected = ((actions[xa].local_value, 1.210), (actions[xb].local_value, 1.236), (actions[xa].dynamic_value, 2.732444), (actions[xb].dynamic_value, 2.6638784))
    if any(abs(actual - target) > tolerance for actual, target in expected):
        raise AssertionError("canonical G3-H value gate failed")
    if not (actions[xa].local_value < actions[xb].local_value and actions[xa].dynamic_value > actions[xb].dynamic_value):
        raise AssertionError("canonical G3-H ranking-inversion gate failed")


def run(*, output: Path = OUTPUT, values: tuple[float, ...] = PHASE_I_VALUES) -> dict[str, object]:
    """Write auditable point/action tables for the declared deterministic grid."""
    _canonical_hard_gate()
    start = perf_counter()
    profiles = _profiles()
    states = tuple(_states(values))
    point_rows: list[dict[str, object]] = []
    action_rows: list[dict[str, object]] = []
    evaluations = []
    for state_index, state in enumerate(states):
        for profile_index, profile in enumerate(profiles):
            point_id = f"s{state_index:04d}_e{profile_index:02d}"
            evaluation = evaluate_point(state, profile)
            evaluations.append(evaluation)
            point_row: dict[str, object] = {
                "point_id": point_id,
                "eta_1": profile[0],
                "eta_2": profile[1],
                "eta_3": profile[2],
                "A_U_star": _actions(evaluation.optimal_use),
                "A_L_star": _actions(evaluation.optimal_local),
                "A_Q_star": _actions(evaluation.optimal_dynamic),
                "regime": evaluation.regime,
                "R2_REVERSION": evaluation.r2_reversion,
                "J_star": evaluation.j_star,
                "J_U": evaluation.j_use,
                "J_L": evaluation.j_local,
                "regret_U": evaluation.regret_use,
                "regret_L": evaluation.regret_local,
            }
            point_row.update(_state_columns("s", state))
            point_rows.append(point_row)
            for observation in evaluation.actions:
                action_row: dict[str, object] = {
                    "point_id": point_id,
                    "action_a_worker_1based": observation.action[0] + 1,
                    "action_b_worker_1based": observation.action[1] + 1,
                    "R": observation.reward,
                    "D": observation.development,
                    "M": observation.local_value,
                    "Q": observation.dynamic_value,
                    "operational_gap": observation.operational_gap,
                }
                action_row.update(_state_columns("successor", observation.successor))
                action_rows.append(action_row)

    runtime_seconds = perf_counter() - start
    regimes = ("R0_USE_SUFFICIENT", "R1_LOCAL_NECESSARY_SUFFICIENT", "R2_LOCAL_INSUFFICIENT")
    summary = {
        "experiment_id": "g3_h_regime_map_v0",
        "description": "diagnostic USE/local USE-DEVELOP/closed G3-H oracle cartography",
        "deterministic": True,
        "tolerance": REGIME_TOL,
        "runtime_seconds": runtime_seconds,
        "configuration": {
            "state_grid_values": list(values),
            "canonical_state_added": list(list(row) for row in CANONICAL_STATE),
            "eta": ETA,
            "delta": DELTA,
            "learning_profiles": [list(profile) for profile in profiles],
            "worker_permutations_included": True,
            "state_symmetries_quotiented": False,
        },
        "points": len(evaluations),
        "action_rows": len(action_rows),
        "counts": {regime: sum(item.regime == regime for item in evaluations) for regime in regimes},
        "r2_reversion_count": sum(item.r2_reversion for item in evaluations),
        "regrets": {
            regime: {
                "regret_U": summarize_regrets(item.regret_use for item in evaluations if item.regime == regime),
                "regret_L": summarize_regrets(item.regret_local for item in evaluations if item.regime == regime),
            }
            for regime in regimes
        },
        "ties": {
            "U_points": sum(len(item.optimal_use) > 1 for item in evaluations),
            "L_points": sum(len(item.optimal_local) > 1 for item in evaluations),
            "Q_points": sum(len(item.optimal_dynamic) > 1 for item in evaluations),
        },
    }
    output.mkdir(parents=True, exist_ok=True)
    points_path = output / "point_results.csv"
    actions_path = output / "action_audit.csv"
    summary_path = output / "summary.json"
    _write_csv(point_rows, points_path)
    _write_csv(action_rows, actions_path)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "experiment_id": summary["experiment_id"],
        "command": "python experiments/synthetic/g3_h/run_regime_map.py",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "g3_core_sha256": _sha256(CORE),
        "g3h_evaluator_sha256": _sha256(G3H),
        "regime_map_sha256": _sha256(REGIME_MAP),
        "runner_sha256": _sha256(RUNNER),
        "point_results_sha256": _sha256(points_path),
        "action_audit_sha256": _sha256(actions_path),
        "summary_sha256": _sha256(summary_path),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="run the smaller transparent smoke grid")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    summary = run(output=args.output, values=SMOKE_VALUES if args.smoke else PHASE_I_VALUES)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
