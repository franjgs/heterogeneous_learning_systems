"""Deterministic, bounded one-skill stress test for the competence estimator."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from math import sqrt
from pathlib import Path
from random import Random

from hls.discover_develop_v2 import capability_after_exposure, eta_to_lambda
from hls.hls_lab_dynamic import (
    SkillPosterior,
    initialize_competence_estimator,
    predict_skill_posterior_after_mis,
    update_skill_posterior,
)
from hls import hls_lab_dynamic


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prior(mean: float, variance: float) -> SkillPosterior:
    return initialize_competence_estimator(((mean, mean),) * 3, variance)[0][0]


def summarize(rows: list[tuple[float, float, float]]) -> dict[str, float | int]:
    """Rows are (truth, posterior mean, posterior variance)."""
    errors = [estimate - truth for truth, estimate, _ in rows]
    return {
        "n": len(rows),
        "mean_absolute_error": sum(abs(e) for e in errors) / len(errors),
        "bias_estimate_minus_truth": sum(errors) / len(errors),
        "rmse": sqrt(sum(e * e for e in errors) / len(errors)),
        "mean_posterior_variance": sum(v for _, _, v in rows) / len(rows),
        "mean_final_estimate": sum(e for _, e, _ in rows) / len(rows),
        "mean_final_truth": sum(t for t, _, _ in rows) / len(rows),
    }


def run(output_dir: Path) -> dict:
    seed_base = 20261014
    runs: dict[str, list[tuple[float, float, float]]] = {}
    trajectories: dict[str, list[list[tuple[float, float, float]]]] = {}

    # A. Exact, constant skill; one noiseless measurement.
    p = prior(0.40, 0.04)
    truth, effort = 0.72, 0.50
    p = update_skill_posterior(p, effort, effort * truth, 0.0)
    runs["A_constant_noiseless"] = [(truth, p.mean, p.variance)]
    trajectories["A_constant_noiseless"] = [[(truth, p.mean, p.variance)]]

    # B. Constant skill with Gaussian noise; support does not include truth.
    rows, paths = [], []
    for rep in range(128):
        truth, p = 0.72, prior(0.40, 0.04)
        rng = Random(seed_base + rep)
        path = []
        for _ in range(60):
            effort = 1.0
            y = effort * truth + 0.10 * rng.gauss(0.0, 1.0)
            p = update_skill_posterior(p, effort, y, 0.10)
            path.append((truth, p.mean, p.variance))
        rows.append((truth, p.mean, p.variance))
        paths.append(path)
    runs["B_constant_noisy"] = rows
    trajectories["B_constant_noisy"] = paths

    # C. MIS-v2 growth; observe before learning, then predict using public eta.
    rows, paths = [], []
    eta, effort, sigma = 0.20, 0.40, 0.03
    rate = eta_to_lambda(eta)
    for rep in range(128):
        truth, p = 0.25, prior(0.40, 0.04)
        rng = Random(seed_base + 1000 + rep)
        path = []
        for _ in range(30):
            y = effort * truth + sigma * rng.gauss(0.0, 1.0)
            p = update_skill_posterior(p, effort, y, sigma)
            p = predict_skill_posterior_after_mis(p, effort, eta)
            truth = capability_after_exposure(truth, effort, rate=rate)
            path.append((truth, p.mean, p.variance))
        rows.append((truth, p.mean, p.variance))
        paths.append(path)
    runs["C_mis_growth_observed"] = rows
    trajectories["C_mis_growth_observed"] = paths

    # D. No observations for 30 steps; known deterministic public MIS profile.
    truth, p = 0.60, prior(0.60, 0.04)
    eta, effort, rate = 0.15, 0.10, eta_to_lambda(0.15)
    path = []
    for _ in range(30):
        p = predict_skill_posterior_after_mis(p, effort, eta)
        truth = capability_after_exposure(truth, effort, rate=rate)
        path.append((truth, p.mean, p.variance))
    runs["D_no_observation_public_mis_prediction"] = [(truth, p.mean, p.variance)]
    trajectories["D_no_observation_public_mis_prediction"] = [path]

    # E. Grossly misspecified initial estimate, then repeated noisy observations.
    rows, paths = [], []
    for rep in range(128):
        truth, p = 0.95, prior(0.05, 0.002)
        rng = Random(seed_base + 2000 + rep)
        path = []
        for _ in range(20):
            y = truth + 0.05 * rng.gauss(0.0, 1.0)
            p = update_skill_posterior(p, 1.0, y, 0.05)
            path.append((truth, p.mean, p.variance))
        rows.append((truth, p.mean, p.variance))
        paths.append(path)
    runs["E_bad_initial_estimate"] = rows
    trajectories["E_bad_initial_estimate"] = paths

    # F. Small effort weakens the observation SNR; 50 repeated measurements.
    rows, paths = [], []
    for rep in range(128):
        truth, p = 0.72, prior(0.40, 0.04)
        rng = Random(seed_base + 3000 + rep)
        path = []
        for _ in range(50):
            effort = 0.05
            y = effort * truth + 0.05 * rng.gauss(0.0, 1.0)
            p = update_skill_posterior(p, effort, y, 0.05)
            path.append((truth, p.mean, p.variance))
        rows.append((truth, p.mean, p.variance))
        paths.append(path)
    runs["F_small_effort"] = rows
    trajectories["F_small_effort"] = paths

    result = {
        "classification": "bounded estimator validation; not an organizational experiment",
        "estimator": "existing bounded three-support Bayesian posterior; unchanged",
        "credible_intervals": "not implemented; coverage is not defined or assessed",
        "seed_base": seed_base,
        "replicates": 128,
        "scenario_configuration": {
            "A_constant_noiseless": {"truth": 0.72, "prior_mean": 0.40, "prior_variance": 0.04, "effort": 0.50, "noise_sd": 0.0, "observations": 1},
            "B_constant_noisy": {"truth": 0.72, "prior_mean": 0.40, "prior_variance": 0.04, "effort": 1.0, "noise_sd": 0.10, "observations": 60, "replicates": 128},
            "C_mis_growth_observed": {"initial_truth": 0.25, "prior_mean": 0.40, "prior_variance": 0.04, "effort": 0.40, "eta": 0.20, "noise_sd": 0.03, "observe_then_predict_steps": 30, "replicates": 128},
            "D_no_observation_public_mis_prediction": {"initial_truth": 0.60, "prior_mean": 0.60, "prior_variance": 0.04, "effort": 0.10, "eta": 0.15, "no_observation_prediction_steps": 30},
            "E_bad_initial_estimate": {"truth": 0.95, "prior_mean": 0.05, "prior_variance": 0.002, "effort": 1.0, "noise_sd": 0.05, "observations": 20, "replicates": 128},
            "F_small_effort": {"truth": 0.72, "prior_mean": 0.40, "prior_variance": 0.04, "effort": 0.05, "noise_sd": 0.05, "observations": 50, "replicates": 128},
        },
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "git_head_at_execution": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "scenarios": {name: summarize(rows) for name, rows in runs.items()},
        "convergence_by_observation_or_prediction_step": {
            name: [summarize([path[step] for path in paths])
                   for step in range(len(paths[0]))]
            for name, paths in trajectories.items()
        },
        "source_sha256": {
            "hls_lab_dynamic.py": digest(Path(hls_lab_dynamic.__file__)),
            "validate_competence_estimator.py": digest(Path(__file__)),
        },
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    target = output_dir / "validation.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["validation_sha256"] = digest(target)
    # The report hash is emitted on stdout by main; do not self-hash the file.
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("results/diagnostics/hls_competence_estimator_validation"),
    )
    result = run(parser.parse_args().output_dir)
    print(json.dumps({
        "output": "validation.json",
        "validation_sha256": result["validation_sha256"],
        "scenarios": result["scenarios"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
