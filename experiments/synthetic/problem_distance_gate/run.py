"""Reproducible validation gate for team-independent problem distance."""

from __future__ import annotations

import csv
import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.problem_geometry import (  # noqa: E402
    change_magnitudes,
    historical_novelties,
    numerical_production_supremum,
    problem_from_p,
    production_distance,
    representational_mismatches,
)


OUT = ROOT / "results" / "foundations" / "problem_distance_gate"
VALIDATION_P = (0.0, 0.01, 0.1, 0.2, 0.4, 0.49, 0.5, 0.51, 0.6, 0.7, 0.8, 0.9, 0.99, 1.0)
TRIANGLE_P = tuple(index / 40 for index in range(41))
NUMERICAL_RESOLUTION = 250
HYPOTHESES = tuple(problem_from_p(p) for p in (0.8, 0.5, 0.2))


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _sequence_rows(name: str, parameters: tuple[float, ...]) -> list[dict]:
    problems = tuple(problem_from_p(p) for p in parameters)
    changes = change_magnitudes(problems)
    novelties = historical_novelties(problems)
    mismatches = representational_mismatches(problems, HYPOTHESES)
    return [
        {
            "control": name,
            "t": index + 1,
            "p": parameter,
            "problem": json.dumps(problem, separators=(",", ":")),
            "change_magnitude_C_t": changes[index],
            "historical_novelty_N_t": novelties[index],
            "representational_mismatch_M_t": mismatches[index],
        }
        for index, (parameter, problem) in enumerate(zip(parameters, problems))
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    grid_rows: list[dict] = []
    maximum_error = 0.0
    endpoint_failures = 0
    endpoint_selection_failures = 0
    for p, q in product(VALIDATION_P, repeat=2):
        analytic = production_distance(p, q)
        numerical = numerical_production_supremum(p, q, resolution=NUMERICAL_RESOLUTION)
        error = abs(analytic - numerical.distance)
        maximum_error = max(maximum_error, error)
        pure_endpoint = numerical.output in ((0.0, 3.0), (3.0, 0.0))
        expected_endpoint = (
            "either"
            if p + q == 1.0 or p == q
            else "Y1"
            if p + q > 1.0
            else "Y2"
        )
        correct_endpoint = (
            p == q
            or expected_endpoint == "either" and pure_endpoint
            or expected_endpoint == "Y1" and numerical.output == (3.0, 0.0)
            or expected_endpoint == "Y2" and numerical.output == (0.0, 3.0)
        )
        if p != q and not pure_endpoint:
            endpoint_failures += 1
        if p != q and not correct_endpoint:
            endpoint_selection_failures += 1
        grid_rows.append(
            {
                "p": p,
                "q": q,
                "absolute_parameter_gap": abs(p - q),
                "analytic_distance": analytic,
                "numerical_distance": numerical.distance,
                "absolute_error": error,
                "argmax_Y1": numerical.output[0],
                "argmax_Y2": numerical.output[1],
                "pure_endpoint": pure_endpoint,
                "expected_endpoint": expected_endpoint,
                "correct_endpoint": correct_endpoint,
                "degenerate_equal_surfaces": p == q,
            }
        )

    maximum_triangle_excess = 0.0
    for p, q, r in product(TRIANGLE_P, repeat=3):
        excess = production_distance(p, r) - production_distance(p, q) - production_distance(q, r)
        maximum_triangle_excess = max(maximum_triangle_excess, excess)
    maximum_exchange_error = max(
        abs(production_distance(p, q) - production_distance(1.0 - p, 1.0 - q))
        for p, q in product(VALIDATION_P, repeat=2)
    )
    equal_gap_groups: dict[float, list[dict]] = {}
    for row in grid_rows:
        equal_gap_groups.setdefault(round(row["absolute_parameter_gap"], 12), []).append(row)
    varying_equal_gap_groups = {
        gap: max(row["analytic_distance"] for row in rows) - min(row["analytic_distance"] for row in rows)
        for gap, rows in equal_gap_groups.items()
        if max(row["analytic_distance"] for row in rows) - min(row["analytic_distance"] for row in rows) > 1e-12
    }

    sequences = []
    sequences.extend(_sequence_rows("exact_recurrence", (0.8, 0.2, 0.8)))
    sequences.extend(_sequence_rows("novel_exactly_represented", (0.8, 0.5)))
    sequences.extend(_sequence_rows("novel_unrepresented", (0.8, 0.63)))
    sequences.extend(_sequence_rows("recurrent_unrepresented", (0.63, 0.8, 0.63)))

    summary = {
        "definition": "(1/3) sup_{Y1>=0,Y2>=0,Y1+Y2<=3} |R_p(Y)-R_q(Y)|",
        "closed_form": "|p-q|[1+|p+q-1|]",
        "validation_pairs": len(grid_rows),
        "numerical_method": "full deterministic triangular output lattice",
        "numerical_resolution": NUMERICAL_RESOLUTION,
        "output_lattice_points_per_pair": (NUMERICAL_RESOLUTION + 1) * (NUMERICAL_RESOLUTION + 2) // 2,
        "maximum_analytic_numerical_error": maximum_error,
        "nonidentical_endpoint_failures": endpoint_failures,
        "nonidentical_endpoint_selection_failures": endpoint_selection_failures,
        "triangle_grid_points_per_axis": len(TRIANGLE_P),
        "triangle_triples": len(TRIANGLE_P) ** 3,
        "maximum_triangle_excess": maximum_triangle_excess,
        "maximum_capability_exchange_error": maximum_exchange_error,
        "equal_gap_groups_with_distance_variation": len(varying_equal_gap_groups),
        "maximum_within_equal_gap_distance_spread": max(varying_equal_gap_groups.values()),
        "distance_range_on_validation_grid": [
            min(row["analytic_distance"] for row in grid_rows),
            max(row["analytic_distance"] for row in grid_rows),
        ],
        "equal_parameter_gap_diagnostic": [
            {"p": 0.8, "q": 0.7, "absolute_parameter_gap": 0.1, "distance": production_distance(0.8, 0.7)},
            {"p": 0.5, "q": 0.4, "absolute_parameter_gap": 0.1, "distance": production_distance(0.5, 0.4)},
        ],
        "first_descriptor_convention": {"C_1": None, "N_1": None, "M_1": "defined from Z_hat"},
        "hypothesis_repertoire_for_sequence_controls": HYPOTHESES,
    }

    _write_csv(OUT / "distance_grid.csv", grid_rows)
    _write_csv(OUT / "sequence_controls.csv", sequences)
    with (OUT / "control_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
