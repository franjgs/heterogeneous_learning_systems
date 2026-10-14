"""Paired A-F comparison of the historical and grid skill estimators."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from math import exp, sqrt
from pathlib import Path
from random import Random
from time import perf_counter

from hls.discover_develop_v2 import capability_after_exposure, eta_to_lambda
from hls.hls_lab_dynamic import (
    SkillPosterior, initialize_competence_estimator,
    predict_skill_posterior_after_mis, update_skill_posterior,
)


def digest(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes())
    return h.hexdigest()


def prior(mean: float, variance: float, estimator: str, points: int) -> SkillPosterior:
    return initialize_competence_estimator(
        ((mean, mean),) * 3, variance,
        estimator=estimator, grid_points=points,
    )[0][0]


def credible_interval(p: SkillPosterior, mass: float = 0.90) -> tuple[float, float]:
    pairs = sorted(zip(p.support, p.weights))
    tail = (1.0 - mass) / 2.0
    def quantile(q: float) -> float:
        cumulative = 0.0
        for x, weight in pairs:
            cumulative += weight
            if cumulative + 1e-15 >= q:
                return x
        return pairs[-1][0]
    return quantile(tail), quantile(1.0 - tail)


def metric(rows: list[tuple[float, SkillPosterior]]) -> dict[str, float | int]:
    errors = [p.mean - truth for truth, p in rows]
    covered = [lo <= truth <= hi for truth, p in rows
               for lo, hi in (credible_interval(p),)]
    return {
        "n": len(rows),
        "mae": sum(abs(e) for e in errors) / len(errors),
        "bias_estimate_minus_truth": sum(errors) / len(errors),
        "rmse": sqrt(sum(e * e for e in errors) / len(errors)),
        "mean_posterior_variance": sum(p.variance for _, p in rows) / len(rows),
        "credible_90_coverage": sum(covered) / len(covered),
    }


def run_scenario(name: str, estimator: str, points: int, seed_base: int):
    rows: list[tuple[float, SkillPosterior]] = []
    started = perf_counter()
    if name == "A_constant_noiseless":
        truth, p = 0.72, prior(0.40, 0.04, estimator, points)
        p = update_skill_posterior(p, 0.5, 0.5 * truth, 0.0)
        rows = [(truth, p)]
    elif name in {"B_constant_noisy", "E_bad_initial_estimate", "F_small_effort"}:
        if name == "B_constant_noisy":
            truth, mean, var, effort, sigma, n, offset = 0.72, 0.40, 0.04, 1.0, 0.10, 60, 0
        elif name == "E_bad_initial_estimate":
            truth, mean, var, effort, sigma, n, offset = 0.95, 0.05, 0.002, 1.0, 0.05, 20, 2000
        else:
            truth, mean, var, effort, sigma, n, offset = 0.72, 0.40, 0.04, 0.05, 0.05, 50, 3000
        for rep in range(128):
            p = prior(mean, var, estimator, points)
            rng = Random(seed_base + offset + rep)
            for _ in range(n):
                y = effort * truth + sigma * rng.gauss(0.0, 1.0)
                p = update_skill_posterior(p, effort, y, sigma)
            rows.append((truth, p))
    elif name == "C_mis_growth_observed":
        eta, effort, sigma = 0.20, 0.40, 0.03
        rate = eta_to_lambda(eta)
        for rep in range(128):
            truth, p = 0.25, prior(0.40, 0.04, estimator, points)
            rng = Random(seed_base + 1000 + rep)
            for _ in range(30):
                y = effort * truth + sigma * rng.gauss(0.0, 1.0)
                p = update_skill_posterior(p, effort, y, sigma)
                p = predict_skill_posterior_after_mis(p, effort, eta)
                truth = capability_after_exposure(truth, effort, rate=rate)
            rows.append((truth, p))
    elif name == "D_no_observation_public_mis_prediction":
        truth, p, eta, effort = 0.60, prior(0.60, 0.04, estimator, points), 0.15, 0.10
        rate = eta_to_lambda(eta)
        for _ in range(30):
            p = predict_skill_posterior_after_mis(p, effort, eta)
            truth = capability_after_exposure(truth, effort, rate=rate)
        rows = [(truth, p)]
    else:
        raise ValueError(name)
    elapsed = perf_counter() - started
    return metric(rows), elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path,
                        default=Path("results/diagnostics/hls_competence_estimator_grid_comparison"))
    parser.add_argument("--grid-points", type=int, default=101)
    args = parser.parse_args()
    if args.grid_points < 3:
        parser.error("--grid-points must be >= 3")
    scenarios = (
        "A_constant_noiseless", "B_constant_noisy", "C_mis_growth_observed",
        "D_no_observation_public_mis_prediction", "E_bad_initial_estimate",
        "F_small_effort",
    )
    output = {name: {} for name in scenarios}
    seed_base = 20261014
    for scenario in scenarios:
        for estimator in ("three_point", "grid"):
            result, seconds = run_scenario(scenario, estimator, args.grid_points, seed_base)
            output[scenario][estimator] = {**result, "elapsed_seconds": seconds}
    args.output_dir.mkdir(parents=True, exist_ok=False)
    artifact = args.output_dir / "comparison.json"
    artifact.write_text(json.dumps({
        "scope": "bounded A-F estimator comparison; no organization experiment",
        "seed_base": seed_base,
        "replicate_seed_ranges": {"B": "base+0..127", "C": "base+1000..1127",
                                  "E": "base+2000..2127", "F": "base+3000..3127"},
        "grid_points": args.grid_points,
        "interval": "equal-tailed discrete 90% posterior interval",
        "python": sys.version,
        "platform": platform.platform(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source_sha256": {"hls_lab_dynamic.py": digest(Path("src/hls/hls_lab_dynamic.py")),
                          "runner": digest(Path(__file__))},
        "results": output,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": str(artifact), "sha256": digest(artifact), "results": output}, sort_keys=True))


if __name__ == "__main__":
    main()
