"""Materialize the team-free Campaign 1 test-range design gate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.campaign1_test_range import (  # noqa: E402
    CONTAMINATION_STATUS,
    FUTURE_ETA,
    FUTURE_PRIMARY_CONDITION,
    FUTURE_PROBE_CONFIGURATIONS,
    HISTORIES,
    HISTORY_LABELS,
    INTENDED_CONTRASTS,
    POINTS,
    POINTS_P,
    TEAM_EXECUTIONS,
    history_steps,
    pairwise_distance_matrix,
    problem_multiset,
    recurrence_locations,
    transition_multiset,
    validate_test_range,
)
from hls.discover_v0 import DEFAULT_HORIZON, DEFAULT_SIGMA  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

OUT = ROOT / "results" / "foundations" / "campaign1_test_range_gate"


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    validate_test_range()
    OUT.mkdir(parents=True, exist_ok=True)
    labels = tuple(POINTS)
    matrix = pairwise_distance_matrix()
    _write_csv(OUT / "pairwise_distances.csv", [
        {"point": label, "p": POINTS_P[label], **{other: matrix[i][j] for j, other in enumerate(labels)}}
        for i, label in enumerate(labels)
    ])

    step_rows = []
    history_rows = []
    for scenario_id in HISTORIES:
        steps = history_steps(scenario_id)
        step_rows.extend({
            "scenario_id": scenario_id, "step": row.step, "point": row.label,
            "p": row.problem[0], "problem": _json(row.problem), "C_t": row.change,
            "N_t": row.novelty, "M_t": row.mismatch, "represented": row.represented,
            "exact_recurrence": row.exact_recurrence,
        } for row in steps)
        history_rows.append({
            "scenario_id": scenario_id, "labels": _json(HISTORY_LABELS[scenario_id]),
            "p_sequence": _json(tuple(p[0] for p in HISTORIES[scenario_id])),
            "problem_multiset": _json(problem_multiset(scenario_id)),
            "transition_sequence": _json(tuple(row.change for row in steps[1:])),
            "transition_multiset": _json(transition_multiset(scenario_id)),
            "start": steps[0].label, "end": steps[-1].label,
            "recurrence_locations": _json(recurrence_locations(scenario_id)),
            "represented_steps": _json(tuple(row.represented for row in steps)),
            "contamination_status": CONTAMINATION_STATUS[scenario_id],
        })
    _write_csv(OUT / "history_steps.csv", step_rows)
    _write_csv(OUT / "histories.csv", history_rows)

    manifest = {
        "manifest_id": "campaign1-test-range-gate-v1",
        "status": "pre-results geometry fixture; Campaign 1 not executed",
        "selection_basis": "problem geometry only; no team performance, adaptive trajectory outcome, or seed-dependent result used",
        "source_head_before_gate": "a899c14",
        "foundation_commit": "20106d3",
        "campaign0_closure_commit": "a899c14",
        "problem_points": POINTS,
        "hypothesis_repertoire": HYPOTHESIS_REPERTOIRE,
        "uniform_prior": UNIFORM_PRIOR,
        "histories": {key: value for key, value in HISTORY_LABELS.items()},
        "descriptors": {
            key: [{"C_t": s.change, "N_t": s.novelty, "M_t": s.mismatch, "represented": s.represented} for s in history_steps(key)]
            for key in HISTORIES
        },
        "intended_contrasts": INTENDED_CONTRASTS,
        "future_probe_configurations": FUTURE_PROBE_CONFIGURATIONS,
        "future_primary_condition": FUTURE_PRIMARY_CONDITION,
        "future_frozen_parameters": {"eta": FUTURE_ETA, "rho": 0.5, "sigma": DEFAULT_SIGMA, "horizon": DEFAULT_HORIZON},
        "candidate_controls_not_executed_or_replication_frozen": ["NO-DEVELOP", "KNOWN-z oracle"],
        "contamination_status": CONTAMINATION_STATUS,
        "team_executions": TEAM_EXECUTIONS,
        "campaign1_performance_artifacts": 0,
        "empirically_unknown": [
            "value or irrelevance of adaptation", "help or liability from previous development",
            "configuration sensitivity or insensitivity", "performance ordering", "Campaign 1 PASS/PARTIAL/FAIL",
        ],
    }
    with (OUT / "pre_experiment_manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
