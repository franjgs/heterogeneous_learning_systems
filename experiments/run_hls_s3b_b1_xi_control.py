#!/usr/bin/env python3
"""Paired xi control on the historical three-arm S3b B1 instance."""

from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

from scipy.stats import t as student_t

from hls.nonstationary_assignment import GarivierMoulinesPairwiseEstimator
from experiments.run_hls_s3b_discounted_ucb import (
    B, PAPER_BREAKPOINTS, PAPER_HORIZON, PAPER_MEANS, PAPER_WINDOW, SEEDS,
)

OUT = Path("results/experiments/hls_s3b_b1_xi_control/results.json")
XIS = (0.5, 2.0)
POLICIES = ("UCB1", "SW_UCB")
REGIMES = (("pre_change", 0, 3_000), ("transient", 3_000, 5_000),
           ("post_change", 5_000, PAPER_HORIZON))


def _ci(values: list[float]) -> dict:
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = (student_t.ppf(0.975, len(values) - 1) * sd / math.sqrt(len(values))
            if len(values) > 1 else 0.0)
    return {"n": len(values), "mean": mean, "sd": sd,
            "ci95": [mean - half, mean + half]}


def _recovery_lag(actions: list[int], boundary: int, target: int,
                  end: int, run_length: int = 20) -> int | None:
    last = min(end - run_length, boundary + 1_000)
    for start in range(boundary, last + 1):
        if all(action == target for action in actions[start:start + run_length]):
            return start - boundary
    return None


def run_seed(seed: int) -> dict:
    # This is exactly the historical potential-reward stream; all four cells
    # see the same potential Bernoulli outcome for each period and arm.
    rng = random.Random(seed)
    potential = tuple(tuple(rng.random() for _ in range(3))
                      for _ in range(PAPER_HORIZON))
    cells = {}
    for xi in XIS:
        for policy in POLICIES:
            method = "ucb1" if policy == "UCB1" else "sw_ucb"
            estimator = GarivierMoulinesPairwiseEstimator(
                3, 1, method=method,
                window=PAPER_WINDOW if method == "sw_ucb" else None,
                xi=xi, reward_bound=B)
            actions, realized, expected, regret, optimal = [], [], [], [], []
            for period in range(PAPER_HORIZON):
                if period < 3:
                    arm = period
                else:
                    arm = max(range(3), key=lambda i: estimator.score_matrix(period)[i][0])
                mean = PAPER_MEANS[period][arm]
                outcome = float(potential[period][arm] < mean)
                actions.append(arm)
                realized.append(outcome)
                expected.append(mean)
                regret.append(max(PAPER_MEANS[period]) - mean)
                optimal.append(float(arm == max(range(3), key=lambda i: PAPER_MEANS[period][i])) )
                estimator.update(period, ((arm, 0),), {(arm, 0): outcome})

            phase = {}
            for name, start, end in REGIMES:
                phase[name] = {
                    "expected_reward": sum(expected[start:end]),
                    "expected_regret": sum(regret[start:end]),
                    "optimal_rate": statistics.fmean(optimal[start:end]),
                }
            cells[f"xi={xi}/{policy}"] = {
                "expected_reward": sum(expected),
                "realized_reward": sum(realized),
                "expected_regret": sum(regret),
                "optimal_rate": statistics.fmean(optimal),
                "recovery_lag_20_after_changes": [
                    _recovery_lag(actions, 3_000, 2, 5_000),
                    _recovery_lag(actions, 5_000, 0, PAPER_HORIZON),
                ],
                "regimes": phase,
            }
    return {"seed": seed, "cells": cells}


def _summarize(episodes: list[dict]) -> dict:
    summaries = {}
    for xi in XIS:
        for policy in POLICIES:
            key = f"xi={xi}/{policy}"
            rows = [episode["cells"][key] for episode in episodes]
            metrics = ("expected_reward", "realized_reward", "expected_regret", "optimal_rate")
            summaries[key] = {metric: _ci([row[metric] for row in rows]) for metric in metrics}
            summaries[key]["recovery_lag_20_after_changes"] = {
                str(index): _ci([row["recovery_lag_20_after_changes"][index]
                                 if row["recovery_lag_20_after_changes"][index] is not None
                                 else 1_001 for row in rows])
                for index in range(2)
            }
            summaries[key]["regimes"] = {
                name: {metric: _ci([row["regimes"][name][metric] for row in rows])
                       for metric in ("expected_reward", "expected_regret", "optimal_rate")}
                for name, _, _ in REGIMES
            }

    contrasts = {}
    definitions = {
        "SW_minus_UCB_at_xi_0.5": ("xi=0.5/SW_UCB", "xi=0.5/UCB1"),
        "SW_minus_UCB_at_xi_2": ("xi=2.0/SW_UCB", "xi=2.0/UCB1"),
        "UCB_xi2_minus_xi05": ("xi=2.0/UCB1", "xi=0.5/UCB1"),
        "SW_xi2_minus_xi05": ("xi=2.0/SW_UCB", "xi=0.5/SW_UCB"),
    }
    for name, (left, right) in definitions.items():
        contrasts[name] = {}
        for metric in ("expected_reward", "expected_regret", "optimal_rate"):
            contrasts[name][metric] = _ci([
                episode["cells"][left][metric] - episode["cells"][right][metric]
                for episode in episodes
            ])
    contrasts["change_in_SW_advantage_xi2_minus_xi05"] = {}
    for metric in ("expected_reward", "expected_regret", "optimal_rate"):
        contrasts["change_in_SW_advantage_xi2_minus_xi05"][metric] = _ci([
            (episode["cells"]["xi=2.0/SW_UCB"][metric]
             - episode["cells"]["xi=2.0/UCB1"][metric])
            - (episode["cells"]["xi=0.5/SW_UCB"][metric]
               - episode["cells"]["xi=0.5/UCB1"][metric])
            for episode in episodes
        ])
    return {"cells": summaries, "paired_contrasts": contrasts}


def main() -> None:
    episodes = [run_seed(seed) for seed in SEEDS]
    historical = json.loads(Path(
        "results/experiments/hls_s3b_discounted_ucb/results.json").read_text())["reproduction"]
    # xi=.5 must reproduce the existing historical summaries exactly up to
    # floating-point summation tolerance before interpreting the crossover.
    for policy, old_name in (("UCB1", "UCB1"), ("SW_UCB", "SW_UCB")):
        for metric, old_metric in (("expected_reward", "cumulative_expected_reward"),
                                   ("expected_regret", "cumulative_expected_regret")):
            for episode in episodes:
                old_episode = next(row for row in historical["episodes"]
                                   if row["seed"] == episode["seed"])
                assert math.isclose(episode["cells"][f"xi=0.5/{policy}"][metric],
                                    old_episode["policies"][old_name][old_metric],
                                    rel_tol=0.0, abs_tol=1e-8)

    # Same t,n must make xi=2's bonus exactly twice xi=.5's bonus.
    low = GarivierMoulinesPairwiseEstimator(1, 1, method="ucb1", xi=0.5)
    high = GarivierMoulinesPairwiseEstimator(1, 1, method="ucb1", xi=2.0)
    for model in (low, high):
        model.update(0, ((0, 0),), {(0, 0): 1.0})
    low_bonus = low.score_matrix(1)[0][0] - 1.0
    high_bonus = high.score_matrix(1)[0][0] - 1.0
    assert math.isclose(high_bonus / low_bonus, 2.0, rel_tol=1e-12)

    result = {
        "experiment": "HLS-S3b-B1 exploration-coefficient control",
        "configuration": {
            "arms": 3, "horizon": PAPER_HORIZON, "seeds": list(SEEDS),
            "means": {"base": [0.5, 0.3, 0.4], "transient_arm3": 0.9,
                      "transient_periods": [3_000, 5_000]},
            "initialization": "force arm 0, 1, 2 once in periods 0, 1, 2; count all periods",
            "window": PAPER_WINDOW,
            "xi": list(XIS), "reward_bound": B,
            "ucb_formula": "mean + B*sqrt(xi*log(max(2,t+1))/n)",
            "sw_formula": "window_mean + B*sqrt(xi*log(max(2,min(t+1,W)))/n)",
            "randomness": "random.Random(seed), period-arm potential uniforms shared by all four cells",
            "reward": "Bernoulli(mean); expected regret uses true means, not realized rewards",
            "oracles": "instantaneous maximum arm mean",
        },
        "validation": {
            "xi_0.5_matches_historical_per_seed": True,
            "same_potential_stream_all_cells": True,
            "confidence_bonus_ratio_xi2_over_xi05": high_bonus / low_bonus,
            "historical_reference": "results/experiments/hls_s3b_discounted_ucb/results.json",
        },
        "summary": _summarize(episodes), "episodes": episodes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"path": str(OUT), "summary": result["summary"],
                      "validation": result["validation"]}, indent=2))


if __name__ == "__main__":
    main()
