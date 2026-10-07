"""Materialize and validate the frozen Small Problem World fixture."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.problem_geometry import production_distance  # noqa: E402
from hls.small_problem_world import (  # noqa: E402
    A,
    A_PRIME,
    B,
    BELIEF_RESETS_EACH_PROBLEM,
    B_PRIME,
    C,
    HORIZON,
    HYPOTHESIS_REPERTOIRE,
    POSTERIOR_CARRIES_BETWEEN_PROBLEMS,
    STATE_PERSISTS_BETWEEN_PROBLEMS,
    UNIFORM_PRIOR,
    UNIQUE_WORLD_PROBLEMS,
    WORLD,
    pairwise_distance_matrix,
    validate_frozen_world,
    world_descriptors,
)


OUT = ROOT / "results" / "foundations" / "small_problem_world_gate"


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def main() -> None:
    validate_frozen_world()
    OUT.mkdir(parents=True, exist_ok=True)
    descriptors = world_descriptors()
    world_rows = [
        {
            "stage_index": row.stage_index,
            "stage": row.label,
            "true_theta": _json(row.problem),
            "p": row.p,
            "change_magnitude_C_t": row.change_magnitude,
            "historical_novelty_N_t": row.historical_novelty,
            "representational_mismatch_M_t": row.representational_mismatch,
            "represented": row.represented,
            "Z_hat": _json(HYPOTHESIS_REPERTOIRE),
            "prior": _json(UNIFORM_PRIOR),
            "horizon": HORIZON,
        }
        for row in descriptors
    ]
    with (OUT / "world.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(world_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(world_rows)

    labels = tuple(stage.label for stage in UNIQUE_WORLD_PROBLEMS)
    matrix = pairwise_distance_matrix()
    matrix_rows = [
        {"stage": label, **{other: matrix[index][column] for column, other in enumerate(labels)}}
        for index, label in enumerate(labels)
    ]
    with (OUT / "pairwise_distances.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("stage",) + labels, lineterminator="\n")
        writer.writeheader()
        writer.writerows(matrix_rows)

    summary = {
        "world_labels": [stage.label for stage in WORLD],
        "world_p": [stage.problem[0] for stage in WORLD],
        "Z_hat": HYPOTHESIS_REPERTOIRE,
        "uniform_prior": UNIFORM_PRIOR,
        "horizon_per_problem": HORIZON,
        "belief_resets_each_problem": BELIEF_RESETS_EACH_PROBLEM,
        "posterior_carries_between_problems": POSTERIOR_CARRIES_BETWEEN_PROBLEMS,
        "state_persists_between_problems": STATE_PERSISTS_BETWEEN_PROBLEMS,
        "represented_stages": [row.label for row in descriptors if row.represented],
        "unrepresented_stages": [row.label for row in descriptors if not row.represented],
        "controls": {
            "symmetric_local_distance_A_A_prime": production_distance(A, A_PRIME),
            "symmetric_local_distance_B_B_prime": production_distance(B, B_PRIME),
            "cross_region_distance_A_prime_B": production_distance(A_PRIME, B),
            "mismatch_A_prime": descriptors[1].representational_mismatch,
            "mismatch_B": descriptors[2].representational_mismatch,
            "C_novelty": descriptors[4].historical_novelty,
            "C_mismatch": descriptors[4].representational_mismatch,
            "final_A_novelty": descriptors[5].historical_novelty,
            "final_A_change": descriptors[5].change_magnitude,
            "capability_exchange_A_prime_B": A_PRIME == tuple(reversed(B)),
            "capability_exchange_A_B_prime": A == tuple(reversed(B_PRIME)),
        },
        "scientific_status": "deliberately constructed experimental fixture; not an empirical problem distribution",
        "team_executions": 0,
    }
    with (OUT / "control_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
