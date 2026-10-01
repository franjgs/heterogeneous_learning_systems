"""Run the deterministic equal-resource G1.1 static ground-truth sweep."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g1_static import EXACT_TOL, G11Model, demand_sweep  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "g1_static"
MODEL_PATH = ROOT / "src" / "hls" / "g1_static.py"
RUNNER_PATH = Path(__file__).resolve()
POINTS = 1001

SCENARIOS = {
    "homogeneous": G11Model(y11=.7, y12=.4, y21=.7, y22=.4),
    "dominance": G11Model(y11=.9, y12=.8, y21=.4, y22=.2),
    "symmetric_crossed": G11Model(y11=1.0, y12=.2, y21=.2, y22=1.0),
    "asymmetric_crossed": G11Model(y11=.9, y12=.5, y21=.3, y22=.9),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, model in SCENARIOS.items():
        for evaluation in demand_sweep(model, points=POINTS):
            rows.append(
                {
                    "scenario": name,
                    "p": evaluation.p,
                    "Y11": evaluation.policy_values["11"],
                    "Y12": evaluation.policy_values["12"],
                    "Y21": evaluation.policy_values["21"],
                    "Y22": evaluation.policy_values["22"],
                    "Y_ONE": evaluation.y_one,
                    "Y_ROUTE": evaluation.y_route,
                    "Delta_Y": evaluation.delta_y,
                    "Delta_Y_closed_form": evaluation.delta_y_closed_form,
                }
            )
    return rows


def _write_figure(rows: list[dict[str, object]], output: Path) -> Path:
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/hls-g1-matplotlib")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    crossed = [row for row in rows if row["scenario"] == "symmetric_crossed"]
    figure, axis = plt.subplots(figsize=(7, 4.5))
    axis.plot([row["p"] for row in crossed], [row["Y_ONE"] for row in crossed], label="Y_ONE*")
    axis.plot([row["p"] for row in crossed], [row["Y_ROUTE"] for row in crossed], label="Y_ROUTE*")
    axis.plot([row["p"] for row in crossed], [row["Delta_Y"] for row in crossed], label="Delta_Y")
    axis.axvline(.5, color="black", linestyle="--", linewidth=.8, label="p*=0.5")
    axis.set(xlabel="p = P(q=1)", ylabel="expected effectiveness", title="G1.1 symmetric crossed specialization")
    axis.legend()
    figure.tight_layout()
    path = output / "g1_1_symmetric_crossed.png"
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return path


def run(output: Path = OUTPUT) -> dict[str, object]:
    """Write the four fixed G1.1 diagnostic sweeps and exact verification."""
    output.mkdir(parents=True, exist_ok=True)
    rows = _rows()
    csv_path = output / "g1_1_demand_sweep.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    figure_path = _write_figure(rows, output)
    verification: dict[str, dict[str, float | None]] = {}
    for name, model in SCENARIOS.items():
        sweep = demand_sweep(model, points=POINTS)
        closed_errors = [
            abs(item.delta_y - item.delta_y_closed_form)
            for item in sweep
            if item.delta_y_closed_form is not None
        ]
        observed = max(sweep, key=lambda item: item.delta_y)
        verification[name] = {
            "max_abs_closed_form_error": max(closed_errors) if closed_errors else None,
            "observed_max_p": observed.p,
            "observed_max_gain": observed.delta_y,
            "analytical_p_star": model.switching_probability(),
            "analytical_max_gain": model.maximum_gain(),
        }

    summary = {
        "experiment_id": "G1.1",
        "description": "equal-resource static two-agent/two-task ground truth",
        "points_per_scenario": POINTS,
        "exact_tolerance": EXACT_TOL,
        "deterministic": True,
        "seeds": None,
        "scenarios": {
            name: {"y11": model.y11, "y12": model.y12, "y21": model.y21, "y22": model.y22}
            for name, model in SCENARIOS.items()
        },
        "verification": verification,
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest = {
        "experiment_id": "G1.1",
        "command": "python experiments/synthetic/g1/run_g1_1.py",
        "model_sha256": _sha256(MODEL_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "demand_sweep_sha256": _sha256(csv_path),
        "summary_sha256": _sha256(summary_path),
        "figure_sha256": _sha256(figure_path),
        "deterministic": True,
        "seeds": None,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    summary = run()
    for name, result in summary["verification"].items():
        print(
            f"{name}: error={result['max_abs_closed_form_error']} "
            f"p_max={result['observed_max_p']} gain_max={result['observed_max_gain']}"
        )


if __name__ == "__main__":
    main()
