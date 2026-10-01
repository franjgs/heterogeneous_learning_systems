"""Run the deterministic D0/D1/D2 validation for the G2 dynamic ground truth."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g2_dynamic import D0, D1, D2, EXACT_TOL, d2_closed_form, d2_regime, demand_sweep  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "g2_dynamic"
MODEL_PATH = ROOT / "src" / "hls" / "g2_dynamic.py"
RUNNER_PATH = Path(__file__).resolve()
SWEEP_POINTS = 101


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _state(state: tuple[tuple[float, float], tuple[float, float]]) -> list[list[float]]:
    return [list(row) for row in state]


def _outcomes(evaluation) -> dict[str, list[float]]:
    return {policy: list(outcome) for policy, outcome in evaluation.attainable.items()}


def _d0_d1_d2_summary() -> dict[str, object]:
    d0 = D0.evaluate(0.5)
    d1 = D1.evaluate(0.5)
    d2 = D2.evaluate(0.5)
    return {
        "experiment_id": "G2",
        "description": "deterministic 2-agent/2-task/2-period T4--T6 ground truth",
        "deterministic": True,
        "seeds": None,
        "tolerance": EXACT_TOL,
        "d0": {
            "state_0": _state(D0.state_0),
            "learning_rates": list(D0.learning_rates),
            "future_state_action_1": _state(d0.action_1.future_state),
            "future_state_action_2": _state(d0.action_2.future_state),
            "frontier_action_1": [list(point) for point in d0.action_1.frontier],
            "frontier_action_2": [list(point) for point in d0.action_2.frontier],
            "delta_dev": d0.delta_dev,
        },
        "d1": {
            "state_0": _state(D1.state_0),
            "learning_rates": list(D1.learning_rates),
            "future_state_action_1": _state(d1.action_1.future_state),
            "future_state_action_2": _state(d1.action_2.future_state),
            "attainable_action_1": _outcomes(d1.action_1),
            "attainable_action_2": _outcomes(d1.action_2),
            "frontier_action_1": [list(point) for point in d1.action_1.frontier],
            "frontier_action_2": [list(point) for point in d1.action_2.frontier],
            "value_action_1": d1.action_1.terminal_value,
            "value_action_2": d1.action_2.terminal_value,
            "delta_dev": d1.delta_dev,
        },
        "d2_at_p_half": {
            "state_0": _state(D2.state_0),
            "learning_rates": list(D2.learning_rates),
            "future_state_action_1": _state(d2.action_1.future_state),
            "future_state_action_2": _state(d2.action_2.future_state),
            "attainable_action_1": _outcomes(d2.action_1),
            "attainable_action_2": _outcomes(d2.action_2),
            "frontier_action_1": [list(point) for point in d2.action_1.frontier],
            "frontier_action_2": [list(point) for point in d2.action_2.frontier],
            "delta_r": d2.delta_r,
            "delta_dev": d2.delta_dev,
            "delta_j": d2.delta_j,
        },
    }


def _d2_rows() -> tuple[list[dict[str, object]], dict[str, float]]:
    rows = []
    max_errors = {"delta_r": 0.0, "delta_dev": 0.0, "delta_j": 0.0}
    for evaluation in demand_sweep(D2, points=SWEEP_POINTS):
        expected_r, expected_dev, expected_j = d2_closed_form(evaluation.p)
        t5_regime, t6_regime = d2_regime(evaluation.p)
        max_errors["delta_r"] = max(max_errors["delta_r"], abs(evaluation.delta_r - expected_r))
        max_errors["delta_dev"] = max(max_errors["delta_dev"], abs(evaluation.delta_dev - expected_dev))
        max_errors["delta_j"] = max(max_errors["delta_j"], abs(evaluation.delta_j - expected_j))
        rows.append(
            {
                "p": evaluation.p,
                "V_action_1": evaluation.action_1.terminal_value,
                "V_action_2": evaluation.action_2.terminal_value,
                "Delta_R": evaluation.delta_r,
                "Delta_dev": evaluation.delta_dev,
                "Delta_J": evaluation.delta_j,
                "Delta_R_closed_form": expected_r,
                "Delta_dev_closed_form": expected_dev,
                "Delta_J_closed_form": expected_j,
                "T5_regime": t5_regime,
                "T6_regime": t6_regime,
            }
        )
    return rows, max_errors


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_manifest(output: Path = OUTPUT) -> bool:
    """Validate the hashes written by ``run`` without re-running the model."""
    manifest = json.loads((output / "g2_manifest.json").read_text())
    expected = {
        "model_sha256": _sha256(MODEL_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "summary_sha256": _sha256(output / "g2_summary.json"),
        "sweep_sha256": _sha256(output / "g2_d2_sweep.csv"),
    }
    return all(manifest[key] == value for key, value in expected.items())


def run(output: Path = OUTPUT) -> dict[str, object]:
    """Write G2 summary, D2 demand sweep, and reproducibility manifest."""
    output.mkdir(parents=True, exist_ok=True)
    summary = _d0_d1_d2_summary()
    rows, max_errors = _d2_rows()
    sweep_path = output / "g2_d2_sweep.csv"
    _write_csv(rows, sweep_path)
    summary["d2_sweep"] = {
        "points": SWEEP_POINTS,
        "p_v_star": 0.0,
        "p_j_star": 0.5,
        "maximum_absolute_errors": max_errors,
    }
    summary_path = output / "g2_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest = {
        "experiment_id": "G2",
        "command": "python experiments/synthetic/g2/run_g2.py",
        "model_sha256": _sha256(MODEL_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "summary_sha256": _sha256(summary_path),
        "sweep_sha256": _sha256(sweep_path),
        "deterministic": True,
        "seeds": None,
    }
    (output / "g2_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    assert validate_manifest(output)
    return summary


def main() -> None:
    summary = run()
    errors = summary["d2_sweep"]["maximum_absolute_errors"]
    print(f"G2 D0/D1/D2 complete; maximum closed-form errors: {errors}")


if __name__ == "__main__":
    main()
