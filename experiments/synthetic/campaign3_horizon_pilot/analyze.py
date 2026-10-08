"""Preregistered temporal analysis for the initial J=12 horizon pilot."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
FREEZE = ROOT / "results" / "foundations" / "campaign3_horizon_pilot" / "pre_execution_horizon_pilot.json"
WINDOWS = (2, 5, 11)
MODES = ("Q10", "Q01", "Q11")
CONTINUATIONS = ("Q00", "Q11")
QUANTILES = (0.10, 0.25, 0.50, 0.75, 0.90)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def interval(history_values: np.ndarray, bootstrap_indices: np.ndarray) -> tuple[float, float]:
    draws = history_values[bootstrap_indices].mean(axis=1)
    return tuple(float(value) for value in np.quantile(draws, (0.025, 0.975)))


def summarize(frame: pd.DataFrame, bootstrap_indices: np.ndarray, prefix: dict[str, object]):
    delta_values = frame["Delta"].to_numpy(dtype=float)
    history_delta = frame.groupby("history_id", sort=True)["Delta"].mean().to_numpy(dtype=float)
    if len(history_delta) != 840:
        raise RuntimeError("every temporal aggregate must retain all 840 histories")
    delta_low, delta_high = interval(history_delta, bootstrap_indices)
    quantiles = np.quantile(delta_values, QUANTILES)
    row = {
        **prefix,
        "histories": 840,
        "factual_states": len(frame),
        "paired_counterfactual_observations": len(frame),
        "mean_Delta": float(delta_values.mean()),
        "mean_Delta_ci_low": delta_low,
        "mean_Delta_ci_high": delta_high,
        "median_Delta": float(np.median(delta_values)),
        **{f"Delta_q{int(q*100):02d}": float(value) for q, value in zip(QUANTILES, quantiles, strict=True)},
    }
    delta_contribution = frame["delta"].dropna().to_numpy(dtype=float)
    if len(delta_contribution):
        history_contribution = frame.groupby("history_id", sort=True)["delta"].mean().to_numpy(dtype=float)
        contribution_low, contribution_high = interval(history_contribution, bootstrap_indices)
        row.update(
            mean_delta=float(delta_contribution.mean()),
            mean_delta_ci_low=contribution_low,
            mean_delta_ci_high=contribution_high,
        )
    else:
        row.update(mean_delta="", mean_delta_ci_low="", mean_delta_ci_high="")
    return row


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    validation = json.loads((OUT / "raw_validation.json").read_text())
    if not validation["passed"]:
        raise RuntimeError("raw validation must pass before analysis")
    pairs = pd.read_csv(
        OUT / "counterfactual_pairs.csv.gz",
        usecols=["history_id", "problem_index", "decision", "mode", "continuation", "ell", "Delta", "delta"],
    )
    if len(pairs) != 1_179_360:
        raise RuntimeError("counterfactual-pair count changed")
    rng = np.random.default_rng(int(freeze["uncertainty"]["bootstrap_seed"]))
    bootstrap_indices = rng.integers(0, 840, size=(int(freeze["uncertainty"]["B"]), 840))
    np.save(OUT / "bootstrap_history_indices.npy", bootstrap_indices, allow_pickle=False)

    common_rows = []
    for window in WINDOWS:
        population = pairs[(pairs.problem_index + window <= 12) & (pairs.ell <= window)]
        expected_problem_indices = tuple(range(1, 13 - window))
        if tuple(sorted(population.problem_index.unique())) != expected_problem_indices:
            raise RuntimeError(f"common-support problem indices failed for L={window}")
        for continuation in CONTINUATIONS:
            for mode in MODES:
                for ell in range(window + 1):
                    frame = population[
                        (population.continuation == continuation)
                        & (population["mode"] == mode)
                        & (population.ell == ell)
                    ]
                    common_rows.append(summarize(frame, bootstrap_indices, {
                        "analysis": "PRIMARY NESTED COMMON-SUPPORT",
                        "window_L": window,
                        "window_label": "EARLY-STATE DIAGNOSTIC" if window == 11 else "short" if window == 2 else "intermediate",
                        "contributing_problem_indices": packed_indices(expected_problem_indices),
                        "continuation": continuation,
                        "mode": mode,
                        "ell": ell,
                    }))
    common_path = OUT / "common_support_summary.csv"
    write_csv(common_path, common_rows)

    available_rows = []
    for continuation in CONTINUATIONS:
        for mode in MODES:
            for ell in range(12):
                frame = pairs[
                    (pairs.problem_index + ell <= 12)
                    & (pairs.continuation == continuation)
                    & (pairs["mode"] == mode)
                    & (pairs.ell == ell)
                ]
                available_rows.append(summarize(frame, bootstrap_indices, {
                    "analysis": "SECONDARY AVAILABLE-STATE ANALYSIS",
                    "continuation": continuation,
                    "mode": mode,
                    "ell": ell,
                    "contributing_problem_indices": packed_indices(tuple(range(1, 13 - ell))),
                }))
    available_path = OUT / "available_state_summary.csv"
    write_csv(available_path, available_rows)

    manifest = {
        "artifact_type": "campaign3_horizon_pilot_initial_j12_preregistered_analysis",
        "raw_validation_sha256": digest(OUT / "raw_validation.json"),
        "counterfactual_pairs_sha256": digest(OUT / "counterfactual_pairs.csv.gz"),
        "analysis_code_sha256": digest(Path(__file__)),
        "primary": "three separately reported nested common-support windows",
        "windows": [2, 5, 11],
        "L11_label": "EARLY-STATE DIAGNOSTIC",
        "secondary": "SECONDARY AVAILABLE-STATE ANALYSIS",
        "bootstrap": {
            "cluster": "complete base history/seed",
            "B": 2000,
            "seed": 20261013,
            "interval": "two-sided 95% percentile",
            "indices_sha256": digest(OUT / "bootstrap_history_indices.npy"),
        },
        "rows": {"common_support_summary": len(common_rows), "available_state_summary": len(available_rows)},
        "sha256": {
            common_path.name: digest(common_path),
            available_path.name: digest(available_path),
        },
        "gate_1_analysis": False,
        "gate_2_analysis": False,
        "heldout_execution": False,
        "escalation_histories": 0,
    }
    dump(OUT / "analysis_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


def packed_indices(values: tuple[int, ...]) -> str:
    return json.dumps(values, separators=(",", ":"))


if __name__ == "__main__":
    main()
