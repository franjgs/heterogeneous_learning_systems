#!/usr/bin/env python3
"""Closed-loop randomized information subsidy for S3b B2-Semi."""

from __future__ import annotations

import gzip
import json
import math
import random
import statistics
import time
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_e1 import (
    BASE, BREAKPOINTS, CALIBRATION, HORIZON, MATCHINGS, N, PAIRS, TRANSIENT,
    W_REF, _rng_uniforms, calibration_matching, exact_matching, matrix_at,
    oracle_matching,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator


OUT = Path("results/experiments/hls_s3b_observation_subsidy")
SUMMARY = OUT / "results.json"
TRACES = OUT / "period_traces.jsonl.gz"
SEEDS = tuple(range(8200, 8230))
XI = 2.0
TREATMENTS = ("uniform", "directed")
REGIMES = (("base_pre", 9, 3_000), ("transient", 3_000, 5_000),
           ("base_post", 5_000, HORIZON))
POST_CHANGE_WINDOWS = ((3_000, 3_200), (5_000, 5_200))


def _potential_subsidy_uniforms(seed: int):
    rng = random.Random(seed ^ 0x51B51D1)
    return tuple(tuple(rng.random() for _ in PAIRS) for _ in range(HORIZON))


def _subsidy_ranks(seed: int):
    rng = random.Random(seed ^ 0x5E1EC7)
    return tuple(rng.randrange(len(PAIRS)) for _ in range(HORIZON))


def _select_subsidy_edge(treatment: str, rank: int, optimal_matching):
    if treatment == "uniform":
        return PAIRS[rank]
    if treatment == "directed":
        return tuple(sorted(optimal_matching))[rank % N]
    if treatment == "none":
        return None
    raise ValueError("unknown subsidy treatment")


def evaluate_treatment(seed: int, treatment: str):
    """Run one closed-loop arm; `none` exists only for the regression test."""
    if treatment not in {"uniform", "directed", "none"}:
        raise ValueError("unknown treatment")
    task_uniforms = _rng_uniforms(seed)
    subsidy_uniforms = _potential_subsidy_uniforms(seed)
    subsidy_ranks = _subsidy_ranks(seed)
    model = PairwiseBanditEstimator(N, N, method="sw_ucb", window=W_REF, xi=XI)
    expected_reward = []
    realized_reward = []
    expected_regret = []
    action_ids = []
    endogenous_masks = []
    subsidy_edges = []
    subsidy_rewards = []
    mse_global = []
    mse_optimal_edges = []
    empty_window_pairs = []
    pair_diagnostics = []
    started = time.perf_counter()

    for period in range(HORIZON):
        competencies = matrix_at(period)
        diagnostics = model.diagnostic_matrix(period)
        scores = tuple(tuple(cell["index"] for cell in row) for row in diagnostics)
        if period < CALIBRATION:
            selected = calibration_matching(period)
        else:
            selected = exact_matching(scores)

        true_optimal = oracle_matching(competencies)
        optimal_edges = set(true_optimal)
        estimate_errors = [
            (diagnostics[i][k]["estimated_mean"] - competencies[i][k]) ** 2
            for i, k in PAIRS
        ]
        mse_global.append(statistics.fmean(estimate_errors))
        mse_optimal_edges.append(statistics.fmean(
            (diagnostics[i][k]["estimated_mean"] - competencies[i][k]) ** 2
            for i, k in optimal_edges
        ))
        empty_window_pairs.append(sum(
            diagnostics[i][k]["observations_used"] == 0 for i, k in PAIRS
        ))
        pair_diagnostics.append(tuple(tuple(
            diagnostics[i][k]["observations_used"] for k in range(N)
        ) for i in range(N)))

        feedback = {}
        realized = 0
        mask = 0
        for i, k in selected:
            reward = int(task_uniforms[period][i][k] < competencies[i][k])
            feedback[(i, k)] = reward
            realized += reward
            mask |= 1 << (i * N + k)

        actual_expected = sum(competencies[i][k] for i, k in selected)
        oracle_expected = sum(competencies[i][k] for i, k in true_optimal)
        expected_reward.append(actual_expected)
        realized_reward.append(realized)
        expected_regret.append(max(0.0, oracle_expected - actual_expected))
        action_ids.append(MATCHINGS.index(tuple(sorted(selected))))
        endogenous_masks.append(mask)

        # Ordinary semi-bandit feedback first, then one extra sample with the
        # same global timestamp. The latter cannot influence this period's action.
        model.update(period, selected, feedback)
        extra_pair = _select_subsidy_edge(
            treatment, subsidy_ranks[period], true_optimal
        )
        subsidy_edges.append(-1 if extra_pair is None else extra_pair[0] * N + extra_pair[1])
        if extra_pair is None:
            subsidy_rewards.append(-1)
        else:
            i, k = extra_pair
            extra_reward = int(
                subsidy_uniforms[period][i * N + k] < competencies[i][k]
            )
            model.update_additional_observation(period, extra_pair, extra_reward)
            subsidy_rewards.append(extra_reward)

    final_diagnostics = model.diagnostic_matrix(HORIZON)
    runtime = time.perf_counter() - started
    endogenous_counts = {f"{i},{k}": sum(
        bool(mask & (1 << (i * N + k))) for mask in endogenous_masks
    ) for i, k in PAIRS}
    subsidy_counts = {f"{i},{k}": subsidy_edges.count(i * N + k) for i, k in PAIRS}
    total_counts = {pair: endogenous_counts[pair] + subsidy_counts[pair]
                    for pair in endogenous_counts}
    window_counts = {f"{i},{k}": final_diagnostics[i][k]["observations_used"]
                     for i, k in PAIRS}
    optimal_flags = [
        MATCHINGS[action_ids[t]] == oracle_matching(matrix_at(t))
        for t in range(HORIZON)
    ]

    regimes = {}
    for name, start, end in REGIMES:
        regimes[name] = {
            "periods": end - start,
            "expected_reward": sum(expected_reward[start:end]),
            "realized_reward": sum(realized_reward[start:end]),
            "expected_regret": sum(expected_regret[start:end]),
            "optimal_matching_rate": statistics.fmean(optimal_flags[start:end]),
            "mse_global_mean": statistics.fmean(mse_global[start:end]),
            "mse_optimal_edges_mean": statistics.fmean(mse_optimal_edges[start:end]),
            "empty_pair_windows_per_period": statistics.fmean(empty_window_pairs[start:end]),
            "endogenous_observations_by_pair": {},
            "subsidy_observations_by_pair": {},
            "mean_recent_observations_by_pair": {},
        }
        for i, k in PAIRS:
            pair = f"{i},{k}"
            regimes[name]["endogenous_observations_by_pair"][pair] = sum(
                bool(endogenous_masks[t] & (1 << (i * N + k)))
                for t in range(start, end)
            )
            regimes[name]["subsidy_observations_by_pair"][pair] = sum(
                subsidy_edges[t] == i * N + k for t in range(start, end)
            )
            regimes[name]["mean_recent_observations_by_pair"][pair] = statistics.fmean(
                pair_diagnostics[t][i][k] for t in range(start, end)
            )
    post_change = {
        f"{start}:{end}": {
            "expected_regret": sum(expected_regret[start:end]),
            "optimal_matching_rate": statistics.fmean(optimal_flags[start:end]),
        }
        for start, end in POST_CHANGE_WINDOWS
    }

    episode = {
        "seed": seed,
        "treatment": treatment,
        "window": W_REF,
        "xi": XI,
        "cumulative_expected_reward": sum(expected_reward),
        "cumulative_realized_reward": sum(realized_reward),
        "cumulative_expected_regret": sum(expected_regret),
        "optimal_matching_rate": statistics.fmean(optimal_flags),
        "endogenous_observations_total": sum(endogenous_counts.values()),
        "subsidy_observations_total": sum(subsidy_counts.values()),
        "total_observations_by_pair": total_counts,
        "endogenous_observations_by_pair": endogenous_counts,
        "subsidy_observations_by_pair": subsidy_counts,
        "window_observations_at_horizon_by_pair": window_counts,
        "mean_recent_observations_by_pair": {
            f"{i},{k}": statistics.fmean(pair_diagnostics[t][i][k]
                                          for t in range(HORIZON))
            for i, k in PAIRS
        },
        "empty_pair_window_periods_by_pair": {
            f"{i},{k}": sum(pair_diagnostics[t][i][k] == 0 for t in range(HORIZON))
            for i, k in PAIRS
        },
        "regimes": regimes,
        "post_change_windows": post_change,
        "runtime_seconds": runtime,
    }
    trace = {
        "expected_reward": expected_reward,
        "realized_reward": realized_reward,
        "expected_regret": expected_regret,
        "action_id": action_ids,
        "endogenous_feedback_mask": endogenous_masks,
        "subsidy_pair_id": subsidy_edges,
        "subsidy_reward": subsidy_rewards,
        "mse_global": mse_global,
        "mse_optimal_edges": mse_optimal_edges,
        "empty_window_pair_count": empty_window_pairs,
    }
    return episode, trace


def _ci(values):
    values = tuple(float(x) for x in values)
    mean = statistics.fmean(values)
    if len(values) < 2:
        return {"n": len(values), "mean": mean, "sd": None, "ci95": [None, None]}
    sd = statistics.stdev(values)
    half = float(student_t.ppf(0.975, len(values) - 1)) * sd / math.sqrt(len(values))
    return {"n": len(values), "mean": mean, "sd": sd,
            "ci95": [mean - half, mean + half]}


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    episodes = {treatment: [] for treatment in TREATMENTS}
    with gzip.open(TRACES, "wt", encoding="utf-8") as stream:
        for seed in SEEDS:
            row = {"seed": seed, "treatments": {}}
            for treatment in TREATMENTS:
                episode, trace = evaluate_treatment(seed, treatment)
                episodes[treatment].append(episode)
                row["treatments"][treatment] = {"summary": episode, "trace": trace}
            stream.write(json.dumps(row, separators=(",", ":")) + "\n")

    summary = {
        "experiment": "hls_s3b_observation_subsidy",
        "title": "S3b closed-loop intervention on information distribution",
        "reference": "S3b-E1 B2-Semi; SW-UCB, xi=2, W=1214",
        "design": {
            "agents": N, "tasks": N, "horizon": HORIZON,
            "seeds": list(SEEDS), "breakpoints": list(BREAKPOINTS),
            "base_matrix": BASE, "transient_matrix": TRANSIENT,
            "calibration_periods": CALIBRATION, "xi": XI, "window": W_REF,
            "endogenous_feedback": "one Bernoulli outcome for each of three executed pairs",
            "subsidy_budget": "one extra Bernoulli observation per period in both arms",
            "uniform_rule": "uniform over all nine pairs; common rank 0..8",
            "directed_rule": "uniform over three true-optimal matching pairs; common rank modulo 3",
            "additional_observation_timestamp": "same global period; no time advance",
            "common_random_numbers": "task reward potentials, subsidy selection ranks, subsidy potential outcomes paired by seed",
            "subsidy_is_oracular": True,
        },
        "treatments": {},
        "paired_contrasts": {},
        "artifacts": {"period_traces": str(TRACES)},
    }
    for treatment, rows in episodes.items():
        metrics = ("cumulative_expected_reward", "cumulative_realized_reward",
                   "cumulative_expected_regret", "optimal_matching_rate",
                   "runtime_seconds")
        summary["treatments"][treatment] = {
            metric: _ci(row[metric] for row in rows) for metric in metrics
        }
        summary["treatments"][treatment]["regimes"] = {
            name: {metric: _ci(row["regimes"][name][metric] for row in rows)
                   for metric in ("expected_reward", "realized_reward", "expected_regret",
                                  "optimal_matching_rate", "mse_global_mean",
                                  "mse_optimal_edges_mean", "empty_pair_windows_per_period")}
            for name, _, _ in REGIMES
        }
        summary["treatments"][treatment]["subsidy_observations_by_pair_mean"] = {
            pair: statistics.fmean(row["subsidy_observations_by_pair"][pair] for row in rows)
            for pair in rows[0]["subsidy_observations_by_pair"]
        }
        summary["treatments"][treatment]["endogenous_observations_by_pair_mean"] = {
            pair: statistics.fmean(row["endogenous_observations_by_pair"][pair] for row in rows)
            for pair in rows[0]["endogenous_observations_by_pair"]
        }
        summary["treatments"][treatment]["total_observations_by_pair_mean"] = {
            pair: statistics.fmean(row["total_observations_by_pair"][pair] for row in rows)
            for pair in rows[0]["total_observations_by_pair"]
        }
        summary["treatments"][treatment]["observations_by_pair_and_regime_mean"] = {
            name: {
                source: {
                    pair: statistics.fmean(row["regimes"][name][source][pair] for row in rows)
                    for pair in rows[0]["regimes"][name][source]
                }
                for source in ("endogenous_observations_by_pair", "subsidy_observations_by_pair")
            }
            for name, _, _ in REGIMES
        }
        summary["treatments"][treatment]["mean_recent_observations_by_pair"] = {
            pair: statistics.fmean(row["mean_recent_observations_by_pair"][pair] for row in rows)
            for pair in rows[0]["mean_recent_observations_by_pair"]
        }
    summary["paired_contrasts"]["directed_minus_uniform_regret"] = _ci(
        directed["cumulative_expected_regret"] - uniform["cumulative_expected_regret"]
        for directed, uniform in zip(episodes["directed"], episodes["uniform"])
    )
    summary["paired_contrasts"]["delta_L_uniform_minus_directed_regret"] = _ci(
        uniform["cumulative_expected_regret"] - directed["cumulative_expected_regret"]
        for uniform, directed in zip(episodes["uniform"], episodes["directed"])
    )
    for metric in ("cumulative_expected_reward", "optimal_matching_rate"):
        summary["paired_contrasts"][f"directed_minus_uniform_{metric}"] = _ci(
            directed[metric] - uniform[metric]
            for directed, uniform in zip(episodes["directed"], episodes["uniform"])
        )
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": str(SUMMARY), "traces": str(TRACES),
        "regret_uniform": summary["treatments"]["uniform"]["cumulative_expected_regret"],
        "regret_directed": summary["treatments"]["directed"]["cumulative_expected_regret"],
        "pi_estimand_delta_uniform_minus_directed": summary["paired_contrasts"]["delta_L_uniform_minus_directed_regret"],
    }, indent=2))


if __name__ == "__main__":
    run()
