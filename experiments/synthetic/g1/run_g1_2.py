"""Run the deterministic bicriterion G1.2 static ground-truth experiments."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g1_static import (  # noqa: E402
    CANONICAL_G12_SCENARIOS,
    EXACT_TOL,
    G12Model,
    ResourceEffectivenessPoint,
)


OUTPUT = ROOT / "results" / "foundations" / "g1_static"
MODEL_PATH = ROOT / "src" / "hls" / "g1_static.py"
RUNNER_PATH = Path(__file__).resolve()
P_HALF = .5
B_MAX = 1.0  # Fixed: every canonical resource coordinate is at most 0.8.
BUDGET_SWEEP_POINTS = 1001
OPERATING_P_POINTS = 101
OPERATING_B_POINTS = 201
MAP_SCENARIOS = (
    "S2_g11_embedded_equal_resource",
    "S3_bicriterion_tradeoff",
    "S4_geometric_expansion_null",
    "S5_bounded_gain_window",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _point(point: ResourceEffectivenessPoint) -> dict[str, float]:
    return {"R": point.resource, "Y": point.effectiveness}


def _model_definition(model: G12Model) -> dict[str, dict[str, float]]:
    return {
        "M1_q1": {"y": model.y11, "r": model.r11},
        "M1_q2": {"y": model.y12, "r": model.r12},
        "M2_q1": {"y": model.y21, "r": model.r21},
        "M2_q2": {"y": model.y22, "r": model.r22},
    }


def _breakpoints(model: G12Model, p: float) -> list[float]:
    return sorted(
        {
            *(point.resource for point in model.one_hull(p)),
            *(point.resource for point in model.route_hull(p)),
        }
    )


def _budget_rows() -> list[dict[str, object]]:
    rows = []
    for name, model in CANONICAL_G12_SCENARIOS.items():
        for index in range(BUDGET_SWEEP_POINTS):
            budget = B_MAX * index / (BUDGET_SWEEP_POINTS - 1)
            evaluation = model.evaluate(P_HALF, budget)
            rows.append(_row(name, evaluation))
    return rows


def _operating_rows() -> list[dict[str, object]]:
    rows = []
    for name in MAP_SCENARIOS:
        model = CANONICAL_G12_SCENARIOS[name]
        for p_index in range(OPERATING_P_POINTS):
            p = p_index / (OPERATING_P_POINTS - 1)
            for b_index in range(OPERATING_B_POINTS):
                budget = B_MAX * b_index / (OPERATING_B_POINTS - 1)
                rows.append(_row(name, model.evaluate(p, budget)))
    return rows


def _row(name: str, evaluation) -> dict[str, object]:
    return {
        "scenario": name,
        "p": evaluation.p,
        "B": evaluation.budget,
        "ONE_feasible": evaluation.y_one is not None,
        "ROUTE_feasible": evaluation.y_route is not None,
        "common_feasible": evaluation.delta_y is not None,
        "Y_ONE": evaluation.y_one,
        "Y_ROUTE": evaluation.y_route,
        "Delta_Y": evaluation.delta_y,
    }


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _s5_closed_form(budget: float) -> float | None:
    if budget < .25:
        return None
    if budget <= .40:
        return 5.0 / 12.0 * (budget - .25)
    if budget <= .65:
        return .25 * (.65 - budget)
    return 0.0


def _summary(budget_rows: list[dict[str, object]], operating_rows: list[dict[str, object]]) -> dict[str, object]:
    summaries: dict[str, object] = {}
    all_common_deltas = []
    for name, model in CANONICAL_G12_SCENARIOS.items():
        evaluation = model.evaluate(P_HALF, B_MAX)
        maximum = model.maximum_gain(P_HALF)
        scenario_rows = [row for row in budget_rows if row["scenario"] == name]
        deltas = [float(row["Delta_Y"]) for row in scenario_rows if row["Delta_Y"] is not None]
        all_common_deltas.extend(deltas)
        summaries[name] = {
            "matrix": _model_definition(model),
            "p": P_HALF,
            "deterministic_points": {
                key: _point(value) for key, value in model.policy_points(P_HALF).items()
            },
            "one_upper_hull": [_point(point) for point in evaluation.one_hull],
            "route_upper_hull": [_point(point) for point in evaluation.route_hull],
            "breakpoints": _breakpoints(model, P_HALF),
            "maximum_delta_y": None if maximum is None else maximum.delta_y,
            "maximizing_budget": None if maximum is None else maximum.budget,
            "positive_gain_budget_intervals": [list(item) for item in model.positive_gain_intervals(P_HALF)],
            "D": model.determinant_d,
            "parallelogram_area_at_p_half": model.parallelogram_area(P_HALF),
            "parallelogram_closed_form_at_p_half": model.parallelogram_area_closed_form(P_HALF),
            "minimum_delta_y_on_budget_grid": min(deltas) if deltas else None,
        }

    s2 = CANONICAL_G12_SCENARIOS["S2_g11_embedded_equal_resource"]
    s2_errors = []
    for index in range(OPERATING_P_POINTS):
        p = index / (OPERATING_P_POINTS - 1)
        value = s2.evaluate(p, .5).delta_y
        assert value is not None
        s2_errors.append(abs(value - .8 * min(p, 1.0 - p)))
    s5 = CANONICAL_G12_SCENARIOS["S5_bounded_gain_window"]
    s5_errors = []
    for row in budget_rows:
        if row["scenario"] != "S5_bounded_gain_window":
            continue
        expected = _s5_closed_form(float(row["B"]))
        observed = row["Delta_Y"]
        if expected is None:
            assert observed is None
        else:
            assert observed is not None
            s5_errors.append(abs(float(observed) - expected))

    common_map_deltas = [
        float(row["Delta_Y"]) for row in operating_rows if row["Delta_Y"] is not None
    ]
    return {
        "experiment_id": "G1.2",
        "description": "static bicriterion effectiveness-resource two-agent/two-task ground truth",
        "deterministic": True,
        "seeds": None,
        "tolerance": EXACT_TOL,
        "grid": {
            "diagnostic_p": P_HALF,
            "budget_max": B_MAX,
            "budget_sweep_points": BUDGET_SWEEP_POINTS,
            "operating_p_points": OPERATING_P_POINTS,
            "operating_budget_points": OPERATING_B_POINTS,
            "operating_map_scenarios": list(MAP_SCENARIOS),
        },
        "positive_gain_interval_semantics": "Each [start, end] denotes the open interval (start, end); null end denotes persistence after saturation.",
        "scenarios": summaries,
        "verification": {
            "s2_max_abs_closed_form_error": max(s2_errors),
            "s5_max_abs_closed_form_error": max(s5_errors),
            "minimum_delta_y_budget_grid": min(all_common_deltas),
            "minimum_delta_y_operating_map": min(common_map_deltas),
            "maximum_monotonicity_violation": max(0.0, -min(all_common_deltas + common_map_deltas)),
            "maximum_parallelogram_identity_error": max(
                model.parallelogram_identity_error(index / (OPERATING_P_POINTS - 1))
                for model in CANONICAL_G12_SCENARIOS.values()
                for index in range(OPERATING_P_POINTS)
            ),
            "maximum_parallelogram_area_formula_error": max(
                abs(model.parallelogram_area(P_HALF) - model.parallelogram_area_closed_form(P_HALF))
                for model in CANONICAL_G12_SCENARIOS.values()
            ),
        },
    }


def _write_figures(budget_rows: list[dict[str, object]], operating_rows: list[dict[str, object]], output: Path) -> tuple[Path, ...]:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/hls-g1-matplotlib")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    s5 = [row for row in budget_rows if row["scenario"] == "S5_bounded_gain_window"]
    figure, axis = plt.subplots(figsize=(7, 4.5))
    axis.plot([row["B"] for row in s5], [row["Y_ONE"] for row in s5], label="Y_ONE*")
    axis.plot([row["B"] for row in s5], [row["Y_ROUTE"] for row in s5], label="Y_ROUTE*")
    axis.plot([row["B"] for row in s5], [row["Delta_Y"] for row in s5], label="Delta_Y")
    for budget in (.25, .40, .65):
        axis.axvline(budget, color="black", linestyle="--", linewidth=.8)
    axis.set(xlabel="B", ylabel="effectiveness / gain", title="G1.2 S5 bounded organizational-gain window")
    axis.legend()
    figure.tight_layout()
    budget_path = output / "g1_2_s5_budget_window.png"
    figure.savefig(budget_path, dpi=160)
    plt.close(figure)

    s5_map = [row for row in operating_rows if row["scenario"] == "S5_bounded_gain_window"]
    p_values = sorted({float(row["p"]) for row in s5_map})
    b_values = sorted({float(row["B"]) for row in s5_map})
    gain = np.full((len(b_values), len(p_values)), np.nan)
    by_pair = {(float(row["p"]), float(row["B"])): row for row in s5_map}
    for b_index, budget in enumerate(b_values):
        for p_index, p in enumerate(p_values):
            value = by_pair[(p, budget)]["Delta_Y"]
            if value is not None:
                gain[b_index, p_index] = float(value)
    figure, axis = plt.subplots(figsize=(7, 4.5))
    image = axis.pcolormesh(p_values, b_values, gain, shading="nearest")
    figure.colorbar(image, ax=axis, label="Delta_Y")
    axis.set(xlabel="p = P(q1)", ylabel="B", title="G1.2 S5 operating map (sampled)")
    figure.tight_layout()
    map_path = output / "g1_2_s5_operating_map.png"
    figure.savefig(map_path, dpi=160)
    plt.close(figure)

    figure, axes = plt.subplots(2, 3, figsize=(10, 6), sharex=True, sharey=True)
    for axis, (name, model) in zip(axes.flat, CANONICAL_G12_SCENARIOS.items()):
        points = model.policy_points(P_HALF)
        one = model.one_hull(P_HALF)
        route = model.route_hull(P_HALF)
        axis.scatter([point.resource for point in one], [point.effectiveness for point in one], label="ONE", marker="o")
        axis.scatter([point.resource for point in route], [point.effectiveness for point in route], label="ROUTE", marker="x")
        axis.plot([point.resource for point in one], [point.effectiveness for point in one])
        axis.plot([point.resource for point in route], [point.effectiveness for point in route])
        for label, point in points.items():
            axis.annotate(label, (point.resource, point.effectiveness), fontsize=7)
        axis.set_title(name.split("_", 1)[0])
    axes[0, 0].legend(fontsize=8)
    figure.supxlabel("R")
    figure.supylabel("Y")
    figure.suptitle("G1.2 canonical upper frontiers at p=0.5")
    figure.tight_layout()
    frontier_path = output / "g1_2_canonical_frontiers.png"
    figure.savefig(frontier_path, dpi=160)
    plt.close(figure)
    return budget_path, map_path, frontier_path


def run(output: Path = OUTPUT) -> dict[str, object]:
    """Write fixed G1.2 diagnostics, operating maps, figures, and provenance."""
    output.mkdir(parents=True, exist_ok=True)
    budget_rows = _budget_rows()
    operating_rows = _operating_rows()
    budget_path = output / "g1_2_budget_sweep.csv"
    map_path = output / "g1_2_operating_map.csv"
    _write_csv(budget_rows, budget_path)
    _write_csv(operating_rows, map_path)
    summary = _summary(budget_rows, operating_rows)
    summary_path = output / "g1_2_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    figures = _write_figures(budget_rows, operating_rows, output)
    manifest = {
        "experiment_id": "G1.2",
        "command": "python experiments/synthetic/g1/run_g1_2.py",
        "model_sha256": _sha256(MODEL_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "budget_sweep_sha256": _sha256(budget_path),
        "operating_map_sha256": _sha256(map_path),
        "summary_sha256": _sha256(summary_path),
        "figure_sha256": {path.name: _sha256(path) for path in figures},
        "deterministic": True,
        "seeds": None,
    }
    (output / "g1_2_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main() -> None:
    summary = run()
    for name, value in summary["scenarios"].items():
        print(
            f"{name}: max_delta={value['maximum_delta_y']} "
            f"B*={value['maximizing_budget']} intervals={value['positive_gain_budget_intervals']}"
        )


if __name__ == "__main__":
    main()
