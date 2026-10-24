"""Derive paired contrasts and cost summaries from a completed HLS-CE-03 run.

This post-processing utility never trains or invokes models. It verifies the
campaign artifact against its run-time manifest before writing separate
derived summaries, leaving the raw campaign files untouched.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
from scipy.stats import t


DEFAULT_RESULTS = Path("results/experiments/hls_ce03_h3_transfer")
CONTROL = "control1_and_control2_identical_hard_label_refit"
T3 = "T3_interactions"


def _paired_summary(values: list[float], confidence: float = 0.95) -> dict[str, float | int]:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or len(data) != 20 or not np.isfinite(data).all():
        raise ValueError("expected exactly 20 finite paired seed-level contrasts")
    mean = float(np.mean(data))
    sd = float(np.std(data, ddof=1))
    half = float(t.ppf(0.5 + confidence / 2, df=len(data) - 1) * sd / np.sqrt(len(data)))
    return {
        "n_seeds": len(data), "mean": mean, "median": float(np.median(data)), "sd": sd,
        "ci95_low": mean - half, "ci95_high": mean + half,
        "positive_seeds": int(np.sum(data > 0)), "negative_seeds": int(np.sum(data < 0)),
        "zero_seeds": int(np.sum(data == 0)),
    }


def _verify_artifact(results_dir: Path, raw: dict) -> dict:
    manifest = json.loads((results_dir / "manifest.json").read_text())
    result_bytes = (results_dir / "results.json").read_bytes()
    if hashlib.sha256(result_bytes).hexdigest() != manifest["result_sha256"]:
        raise ValueError("raw results.json does not match its recorded SHA-256")
    config_bytes = json.dumps(raw["configuration"], sort_keys=True).encode()
    if hashlib.sha256(config_bytes).hexdigest() != manifest["config_sha256"]:
        raise ValueError("result configuration does not match its recorded SHA-256")
    if raw.get("status") != "CAMPAIGN_EXECUTED":
        raise ValueError("results artifact does not identify a completed campaign")
    seeds = [int(run["seed"]) for run in raw["runs"]]
    if seeds != list(range(20)):
        raise ValueError("campaign must contain seeds 0 through 19 exactly once and in order")
    return manifest


def analyze(results_dir: Path = DEFAULT_RESULTS) -> dict:
    raw_path = results_dir / "results.json"
    raw = json.loads(raw_path.read_text())
    manifest = _verify_artifact(results_dir, raw)
    rows = []
    for run in raw["runs"]:
        seed = int(run["seed"])
        individual_distilled = run["A1_individual_test_metrics_after_distillation"][T3]["accuracy"]
        individual_control = run["control_test_metrics_A1"][CONTROL][T3]["accuracy"]
        individual_initial = run["A1_individual_test_metrics_before"][T3]["accuracy"]
        conditions = run["conditions_test"]
        c0 = conditions["C0_no_transfer_fixed_O0"]["weighted_accuracy"]
        c1 = conditions["C1_transfer_fixed_O0"]["weighted_accuracy"]
        c2 = conditions["C2_transfer_readapted_O1"]["weighted_accuracy"]
        cost = run["costs_seconds"]
        control_cost = run["controls"][CONTROL]
        transfer = run["transfer"]
        rows.append({
            "seed": seed,
            "A_transfer_vs_refit_A1_T3": individual_distilled - individual_control,
            "B_distilled_vs_initial_A1_T3_descriptive": individual_distilled - individual_initial,
            "C_fixed_collective_C1_minus_C0": c1 - c0,
            "D_reorganization_C2_minus_C1": c2 - c1,
            "E_total_collective_C2_minus_C0": c2 - c0,
            "initial_training_total_seconds": cost["initial_fit_total"],
            "initial_A1_training_seconds": cost["initial_fit_by_agent"]["A1_logistic"],
            "initial_A2_training_seconds": cost["initial_fit_by_agent"]["A2_random_forest"],
            "initial_A3_training_seconds": cost["initial_fit_by_agent"]["A3_mlp"],
            "distillation_student_fit_seconds": transfer["student_fit_seconds"],
            "no_distillation_refit_seconds": control_cost["fit_seconds"],
            "teacher_inference_seconds": transfer["teacher_inference_seconds"],
            "full_transfer_seconds": transfer["total_transfer_seconds"],
            "distillation_optimizer_iterations": transfer["student_optimizer_iterations"],
            "no_distillation_optimizer_iterations": control_cost["optimizer_iterations"],
            "student_fit_seconds_minus_refit_seconds": transfer["student_fit_seconds"] - control_cost["fit_seconds"],
            "optimizer_iterations_distillation_minus_refit": transfer["student_optimizer_iterations"] - control_cost["optimizer_iterations"],
            "O0": json.dumps(run["O0_initial_validation_optimum"], sort_keys=True),
            "O1": json.dumps(run["O1_post_transfer_validation_optimum"], sort_keys=True),
        })

    contrast_names = {
        "A_transfer_vs_refit_A1_T3": "A: distilled A1 minus hard-label refit without distillation on T3",
        "B_distilled_vs_initial_A1_T3_descriptive": "B: distilled A1 minus initial A1 on T3 (descriptive)",
        "C_fixed_collective_C1_minus_C0": "C: fixed-organization collective C1 minus C0 under O0",
        "D_reorganization_C2_minus_C1": "D: reorganization C2 minus C1",
        "E_total_collective_C2_minus_C0": "E: total collective change C2 minus C0",
    }
    summary = {name: _paired_summary([row[name] for row in rows]) for name in contrast_names}
    summary["costs"] = {
        name: _paired_summary([row[name] for row in rows])
        for name in (
            "initial_training_total_seconds", "distillation_student_fit_seconds",
            "no_distillation_refit_seconds", "teacher_inference_seconds", "full_transfer_seconds",
            "distillation_optimizer_iterations", "no_distillation_optimizer_iterations",
            "initial_A1_training_seconds", "initial_A2_training_seconds", "initial_A3_training_seconds",
            "student_fit_seconds_minus_refit_seconds",
            "optimizer_iterations_distillation_minus_refit",
        )
    }
    a = summary["A_transfer_vs_refit_A1_T3"]
    c = summary["C_fixed_collective_C1_minus_C0"]
    summary["H3"] = {
        "point_signs_both_satisfied": a["mean"] > 0 and c["mean"] < 0,
        "statistical_support_by_prespecified_95pct_intervals": a["ci95_low"] > 0 and c["ci95_high"] < 0,
        "interpretation": "Both point signs are required; statistical support additionally requires the paired-seed 95% CI for A to be wholly positive and for C wholly negative. This is not proof of broad generality.",
    }
    return {
        "experiment": raw["experiment"],
        "raw_results_file": "results.json (preserved unchanged)",
        "raw_results_sha256": manifest["result_sha256"],
        "campaign_commit": manifest["git_head"],
        "seeds": manifest["seeds"],
        "environment": manifest["environment"],
        "execution_command": "python experiments/synthetic/hls_ce03_h3_transfer.py --run-campaign",
        "analysis_command": "python experiments/synthetic/analyze_hls_ce03_h3_results.py",
        "contrasts": contrast_names,
        "summary": summary,
        "notes": {
            "paired_unit": "seed (20 paired seed-level contrasts)",
            "C2_C3": "C3 is an alias of C2, counted once.",
            "cost": "Measured wall-clock time and observed optimizer iterations; no effective-cost equivalence is claimed.",
        },
        "per_seed": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()
    analysis = analyze(args.results_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "derived_analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    with (args.output_dir / "paired_contrasts_by_seed.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(analysis["per_seed"][0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(analysis["per_seed"])
    derived_path = args.output_dir / "derived_analysis.json"
    per_seed_path = args.output_dir / "paired_contrasts_by_seed.csv"
    analysis_manifest = {
        "raw_results_sha256": analysis["raw_results_sha256"],
        "derived_analysis_sha256": hashlib.sha256(derived_path.read_bytes()).hexdigest(),
        "paired_contrasts_csv_sha256": hashlib.sha256(per_seed_path.read_bytes()).hexdigest(),
        "analysis_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "analysis_environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "command": "python experiments/synthetic/analyze_hls_ce03_h3_results.py",
    }
    (args.output_dir / "analysis_manifest.json").write_text(
        json.dumps(analysis_manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(analysis["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
