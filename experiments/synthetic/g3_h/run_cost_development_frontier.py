"""Audit cost--development Pareto ledgers on already-retained G3-H evidence.

This runner reads no random population generator.  It re-evaluates the
canonical point and the retained structural-autopsy points under frozen G3-H.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g3_h_cost_development_frontier import evaluate_cost_development_frontier  # noqa: E402
from hls.g3_h_regime_map import evaluate_point  # noqa: E402


CANONICAL_STATE = ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8))
CANONICAL_PROFILE = (0.4, 0.6, 0.4)
SOURCE = ROOT / "results" / "foundations" / "g3_h_structural_autopsy" / "diagnostic_points.csv"
DEFAULT_OUTPUT = ROOT / "results" / "foundations" / "g3_h_cost_development_frontier"


def _decode_vector(value: str) -> tuple[float, ...]:
    return tuple(float(item) for item in json.loads(value))


def _state(value: str) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    flat = _decode_vector(value)
    return ((flat[0], flat[1]), (flat[2], flat[3]), (flat[4], flat[5]))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _summary(values: list[float]) -> dict[str, float]:
    return {"min": min(values), "median": median(values), "max": max(values)}


def _records() -> list[dict[str, object]]:
    records = [{"source": "canonical_g3_h", "condition": "heterogeneous", "state": CANONICAL_STATE, "profile": CANONICAL_PROFILE}]
    with SOURCE.open(newline="") as handle:
        for row in csv.DictReader(handle):
            records.append({
                "source": "structural_autopsy_retained",
                "condition": row["condition"],
                "state": _state(row["state"]),
                "profile": _decode_vector(row["eta"]),
            })
    return records


def _nearest_cross_label_pair(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """Find a descriptive, not causal, matched contrast within each eta condition."""
    positive = [row for row in rows if float(row["regret_use"]) > 1e-12]
    null = [row for row in rows if float(row["regret_use"]) <= 1e-12]
    candidates: list[tuple[float, dict[str, object], dict[str, object]]] = []
    for left in positive:
        for right in null:
            if left["condition"] != right["condition"]:
                continue
            # Development scale and profile moments are deliberately the only
            # matching coordinates; frontier geometry is left to differ.
            distance = abs(float(left["dmax"]) - float(right["dmax"]))
            distance += abs(float(left["eta_mean"]) - float(right["eta_mean"]))
            distance += abs(float(left["eta_spread"]) - float(right["eta_spread"]))
            candidates.append((distance, left, right))
    if not candidates:
        return None
    distance, left, right = min(candidates, key=lambda item: item[0])
    return {"matching_distance_dmax_eta_moments": distance, "positive_regret": left, "zero_regret": right}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)

    points: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    for point_id, record in enumerate(_records()):
        state = record["state"]
        profile = record["profile"]
        frontier = evaluate_cost_development_frontier(state, profile)  # type: ignore[arg-type]
        oracle = evaluate_point(state, profile)  # type: ignore[arg-type]
        point = {
            "point_id": point_id,
            "source": record["source"],
            "condition": record["condition"],
            "state": json.dumps(state),
            "eta": json.dumps(profile),
            "eta_mean": sum(profile) / 3.0,  # type: ignore[arg-type]
            "eta_spread": max(profile) - min(profile),  # type: ignore[arg-type]
            "operational_value": frontier.operational_value,
            "d0": frontier.free_development,
            "dmax": frontier.maximum_development,
            "delta_d": frontier.development_requiring_sacrifice,
            "c_dmax": frontier.minimum_cost_of_maximum_development,
            "frontier_size": len(frontier.frontier_actions),
            "regret_use": oracle.regret_use,
            "regret_local": oracle.regret_local,
            "old_oracle_label": oracle.regime,
        }
        points.append(point)
        for action in frontier.actions:
            actions.append({
                "point_id": point_id,
                "condition": record["condition"],
                "action": str((action.action[0] + 1, action.action[1] + 1)),
                "R": action.reward,
                "c": action.cost,
                "D": action.development,
                "M": action.local_value,
                "Q_oracle_label": action.dynamic_value,
                "successor": json.dumps(action.successor),
                "pareto_dominated": action.pareto_dominated,
            })

    with (output / "frontier_points.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(points[0]))
        writer.writeheader(); writer.writerows(points)
    with (output / "frontier_actions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(actions[0]))
        writer.writeheader(); writer.writerows(actions)

    pair = _nearest_cross_label_pair(points)
    with (output / "matched_comparisons.json").open("w") as handle:
        json.dump({"method": "nearest cross-regret pair matched only on Dmax and eta moments; descriptive, not a causal intervention", "best_pair": pair}, handle, indent=2)

    by_condition: dict[str, dict[str, object]] = {}
    for condition in sorted({str(point["condition"]) for point in points}):
        subset = [point for point in points if point["condition"] == condition]
        by_condition[condition] = {
            "points": len(subset),
            "positive_use_regret": sum(float(point["regret_use"]) > 1e-12 for point in subset),
            "old_oracle_labels": dict(Counter(str(point["old_oracle_label"]) for point in subset)),
            "d0": _summary([float(point["d0"]) for point in subset]),
            "dmax": _summary([float(point["dmax"]) for point in subset]),
            "delta_d": _summary([float(point["delta_d"]) for point in subset]),
            "c_dmax": _summary([float(point["c_dmax"]) for point in subset]),
            "regret_use": _summary([float(point["regret_use"]) for point in subset]),
        }
    summary = {
        "experiment_id": "g3_h_cost_development_frontier_existing_evidence_audit",
        "scope": "canonical state plus retained structural-autopsy points; no new sampling",
        "interpretation_limit": "Q is only an oracle label. Matched contrasts are descriptive coupled comparisons, not Beam-1-only interventions.",
        "points": len(points), "actions": len(actions), "by_condition": by_condition,
    }
    with (output / "summary.json").open("w") as handle:
        json.dump(summary, handle, indent=2)
    manifest = {
        "command": "python experiments/synthetic/g3_h/run_cost_development_frontier.py",
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": _sha256(SOURCE),
        "frontier_module_sha256": _sha256(ROOT / "src" / "hls" / "g3_h_cost_development_frontier.py"),
        "points": len(points), "actions": len(actions),
    }
    with (output / "manifest.json").open("w") as handle:
        json.dump(manifest, handle, indent=2)


if __name__ == "__main__":
    main()
