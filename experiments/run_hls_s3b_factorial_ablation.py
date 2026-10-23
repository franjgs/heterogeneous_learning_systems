#!/usr/bin/env python3
"""Paired 2x2 history-by-exploration ablation for the existing HLS S3b."""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_nonstationary_unknown_assignment import (
    CALIBRATION_PERIODS,
    CONDITIONS,
    EVAL_SEEDS,
    HORIZON,
    K,
    N,
    _estimator,
    common_calibration,
    competence_matrix,
    matches_from_id,
    permutation_id,
    potential_uniforms,
    reward_matrix,
    solve,
)
from hls.nonstationary_assignment import PairObservation


OUT = Path("results/experiments/hls_s3b_factorial_ablation/results.json")
ORIGINAL = Path("results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json")
POLICY_METHODS = {
    "GLOBAL_MEAN_MATCHING": "global_mean",
    "UCB1_MATCHING": "ucb1",
    "RECENT_MEAN_MATCHING": "recent_mean",
    "SW_UCB_MATCHING": "sw_ucb",
}
FACTORIAL_ORDER = ("GLOBAL_MEAN_MATCHING", "UCB1_MATCHING",
                   "RECENT_MEAN_MATCHING", "SW_UCB_MATCHING")
BASE_POLICIES = ("UCB1_MATCHING", "SW_UCB_MATCHING", "RECENT_MEAN_MATCHING")
CHANGE_WINDOW_BEFORE = 5
CHANGE_WINDOW_AFTER = 10


def _mean_ci(values):
    values = tuple(float(x) for x in values)
    mean = statistics.fmean(values)
    if len(values) < 2:
        return {"mean": mean, "sd": 0.0, "ci95": [mean, mean]}
    half = student_t.ppf(0.975, len(values) - 1) * statistics.stdev(values) / math.sqrt(len(values))
    return {"mean": mean, "sd": statistics.stdev(values),
            "ci95": [mean - half, mean + half]}


def factorial_contrasts(rewards_by_policy):
    """Paired seed-level 2x2 contrasts; positive values follow the formulas in the protocol."""
    gf = rewards_by_policy["GLOBAL_MEAN_MATCHING"]
    gu = rewards_by_policy["UCB1_MATCHING"]
    wf = rewards_by_policy["RECENT_MEAN_MATCHING"]
    wu = rewards_by_policy["SW_UCB_MATCHING"]
    if not (len(gf) == len(gu) == len(wf) == len(wu)):
        raise ValueError("all factorial cells must use the same paired seeds")
    vectors = {
        "bonus_global": [u - f for u, f in zip(gu, gf)],
        "bonus_window": [u - f for u, f in zip(wu, wf)],
        "window_without_bonus": [f - g for f, g in zip(wf, gf)],
        "window_with_bonus": [w - g for w, g in zip(wu, gu)],
        "interaction": [(w - f) - (u - g) for w, f, u, g in zip(wu, wf, gu, gf)],
    }
    return {name: {**_mean_ci(values), "paired_seed_differences": values}
            for name, values in vectors.items()}


class _Aggregate:
    def __init__(self):
        self.total = defaultdict(float)
        self.count = defaultdict(int)

    def add(self, values):
        for key, value in values.items():
            if value is not None:
                self.total[key] += float(value)
                self.count[key] += 1

    def result(self):
        return {key: self.total[key] / self.count[key]
                for key in self.total}


def evaluate_one(condition: str, seed: int, *, diagnostic_aggregates=None):
    uniforms = potential_uniforms(seed)
    calibration_ids, raw_history, _ = common_calibration(condition, uniforms)
    history = {pair: tuple(PairObservation(t, r) for t, r in rows)
               for pair, rows in raw_history.items()}
    window = CONDITIONS[condition]["breakpoints"]
    window = (HORIZON if window == 0 else
              max(1, min(HORIZON, round(2.0 * math.sqrt(
                  HORIZON * math.log(HORIZON) / window)))))
    models = {name: _estimator(method, window, history)
              for name, method in POLICY_METHODS.items()}
    rows = {name: {"expected": [], "realized": [], "regret": [], "ids": [],
                   "optimal": [], "resource": [], "index_divergence": []}
            for name in FACTORIAL_ORDER}
    oracle_expected = []
    switch_periods = CONDITIONS[condition]["switches"]
    boundaries = {period: idx for idx, period in enumerate(switch_periods)}

    for period in range(CALIBRATION_PERIODS, HORIZON):
        means = competence_matrix(condition, period)
        outcomes = reward_matrix(means, uniforms[period])
        oracle_matches = solve(means)
        oracle_id = permutation_id(oracle_matches)
        oracle_value = sum(means[i][k] for i, k in oracle_matches)
        oracle_expected.append(oracle_value)
        for policy, model in models.items():
            selected = solve(model.score_matrix(period))
            mean_selected = solve(model.empirical_mean_matrix(period))
            selected_set = set(selected)
            identifier = permutation_id(selected)
            expected = sum(means[i][k] for i, k in selected)
            realized = sum(outcomes[i][k] for i, k in selected)
            record = rows[policy]
            record["expected"].append(expected)
            record["realized"].append(realized)
            record["regret"].append(oracle_value - expected)
            record["ids"].append(identifier)
            record["optimal"].append(identifier == oracle_id)
            record["resource"].append(len(selected))
            record["index_divergence"].append(
                permutation_id(selected) != permutation_id(mean_selected))

            if diagnostic_aggregates is not None:
                regime = sum(period >= boundary for boundary in switch_periods)
                diag = model.diagnostic_matrix(period)
                for i in range(N):
                    for k in range(K):
                        d = diag[i][k]
                        vals = {
                            "observations_used": d["observations_used"],
                            "observations_in_window": d["observations_in_window"],
                            "observations_discarded": d["observations_discarded"],
                            "estimated_mean": d["estimated_mean"],
                            "exploration_bonus": d["exploration_bonus"],
                            "index": d["index"],
                            "last_observation_age": d["last_observation_age"],
                            "selected": int((i, k) in selected_set),
                        }
                        diagnostic_aggregates[(condition, policy, "regime", regime, i, k)].add(vals)
                        for boundary, event_index in boundaries.items():
                            delta = period - boundary
                            if -CHANGE_WINDOW_BEFORE <= delta <= CHANGE_WINDOW_AFTER:
                                diagnostic_aggregates[(condition, policy, "change", event_index,
                                                       delta, i, k)].add(vals)
        for policy, model in models.items():
            selected = matches_from_id(rows[policy]["ids"][-1])
            model.update(period, selected,
                         {(i, k): outcomes[i][k] for i, k in selected})

    results = {}
    for policy, record in rows.items():
        ids = record["ids"]
        results[policy] = {
            "cumulative_expected_reward": sum(record["expected"]),
            "cumulative_expected_regret": sum(record["regret"]),
            "cumulative_realized_reward": sum(record["realized"]),
            "resource_units": sum(record["resource"]),
            "optimal_assignment_rate": statistics.fmean(record["optimal"]),
            "switch_count": sum(a != b for a, b in zip(ids, ids[1:])),
            "index_vs_mean_assignment_divergence_rate": statistics.fmean(
                record["index_divergence"]),
            "assignment_ids": ids,
            "expected_reward_by_period": record["expected"],
            "expected_regret_by_period": record["regret"],
            "observations_per_pair_at_end": [len(models[policy].observations[(i, k)])
                                             for i in range(N) for k in range(K)],
        }
    return {"seed": seed, "window_periods": window,
            "calibration_assignment_ids": calibration_ids,
            "oracle_expected_reward": sum(oracle_expected), "policies": results}


def run_experiment():
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    diagnostics = defaultdict(_Aggregate)
    output_conditions = {}
    reproduction = {name: {"episodes": 0, "max_abs_reward_difference": 0.0,
                           "assignment_id_sequences_match": True}
                    for name in BASE_POLICIES}

    for condition in CONDITIONS:
        episodes = []
        switch_periods = CONDITIONS[condition]["switches"]
        original_episodes = original["conditions"][condition]["episodes"]
        original_by_seed = {episode["seed"]: episode for episode in original_episodes}
        for seed in EVAL_SEEDS:
            episode = evaluate_one(condition, seed, diagnostic_aggregates=diagnostics)
            reference = original_by_seed[seed]
            if episode["calibration_assignment_ids"] != reference["calibration_assignment_ids"]:
                raise AssertionError(f"calibration differs from original for {condition}/{seed}")
            for policy in BASE_POLICIES:
                new = episode["policies"][policy]
                old = reference["policies"][policy]
                difference = abs(new["cumulative_expected_reward"] -
                                 old["cumulative_expected_reward"])
                reproduction[policy]["max_abs_reward_difference"] = max(
                    reproduction[policy]["max_abs_reward_difference"], difference)
                reproduction[policy]["episodes"] += 1
                if new["assignment_ids"] != old["assignment_ids"]:
                    reproduction[policy]["assignment_id_sequences_match"] = False
                    raise AssertionError(f"{policy} assignment sequence changed in {condition}/{seed}")
                if difference > 1e-10:
                    raise AssertionError(f"{policy} reward changed in {condition}/{seed}: {difference}")
            episodes.append(episode)

        summaries = {}
        for policy in FACTORIAL_ORDER:
            values = [episode["policies"][policy] for episode in episodes]
            assignment_counts = defaultdict(int)
            for episode in episodes:
                for assignment_id in episode["policies"][policy]["assignment_ids"]:
                    assignment_counts[str(assignment_id)] += 1
            total_assignments = len(episodes) * (HORIZON - CALIBRATION_PERIODS)
            summaries[policy] = {
                "expected_reward": _mean_ci([v["cumulative_expected_reward"] for v in values]),
                "expected_regret": _mean_ci([v["cumulative_expected_regret"] for v in values]),
                "realized_reward": _mean_ci([v["cumulative_realized_reward"] for v in values]),
                "resource_units_mean": statistics.fmean(v["resource_units"] for v in values),
                "optimal_assignment_rate": statistics.fmean(v["optimal_assignment_rate"] for v in values),
                "switch_count_mean": statistics.fmean(v["switch_count"] for v in values),
                "assignment_frequency": {
                    assignment_id: {"count": count, "rate": count / total_assignments}
                    for assignment_id, count in sorted(assignment_counts.items(), key=lambda item: int(item[0]))
                },
                "index_vs_mean_assignment_divergence_rate": statistics.fmean(
                    v["index_vs_mean_assignment_divergence_rate"] for v in values),
                "expected_reward_mean_by_period": [statistics.fmean(
                    e["policies"][policy]["expected_reward_by_period"][t] for e in episodes)
                    for t in range(HORIZON - CALIBRATION_PERIODS)],
                "expected_regret_mean_by_period": [statistics.fmean(
                    e["policies"][policy]["expected_regret_by_period"][t] for e in episodes)
                    for t in range(HORIZON - CALIBRATION_PERIODS)],
                "observations_per_pair_mean": [statistics.fmean(
                    e["policies"][policy]["observations_per_pair_at_end"][edge]
                    for e in episodes) for edge in range(N * K)],
            }
        rewards = {policy: [episode["policies"][policy]["cumulative_expected_reward"]
                            for episode in episodes] for policy in FACTORIAL_ORDER}
        contrasts = factorial_contrasts(rewards)
        by_regime = {}
        for policy in FACTORIAL_ORDER:
            by_regime[policy] = {}
            for regime in range(len(CONDITIONS[condition]["shifts"])):
                start = max(CALIBRATION_PERIODS, (switch_periods[regime - 1]
                            if regime > 0 else CALIBRATION_PERIODS))
                end = switch_periods[regime] if regime < len(switch_periods) else HORIZON
                indices = range(start - CALIBRATION_PERIODS, end - CALIBRATION_PERIODS)
                by_regime[policy][str(regime)] = {
                    "periods_per_seed": len(indices),
                    "expected_reward_mean": statistics.fmean(
                        sum(e["policies"][policy]["expected_reward_by_period"][i] for i in indices)
                        for e in episodes),
                    "expected_regret_mean": statistics.fmean(
                        sum(e["policies"][policy]["expected_regret_by_period"][i] for i in indices)
                        for e in episodes),
                }
        output_conditions[condition] = {
            "window_periods": episodes[0]["window_periods"],
            "regime_switch_periods": CONDITIONS[condition]["switches"],
            "summaries": summaries,
            "factorial_contrasts": contrasts,
            "by_regime": by_regime,
            "recovery_lags": _recovery_summary(episodes, condition),
            "diagnostics": _format_diagnostics(diagnostics, condition),
            "episodes": [{"seed": e["seed"], "policies": {
                p: {key: value for key, value in e["policies"][p].items()
                    if key not in {"expected_reward_by_period", "expected_regret_by_period"}}
                for p in FACTORIAL_ORDER}} for e in episodes],
        }

    output = {
        "experiment": "HLS-S3b factorial ablation: history x exploration",
        "protocol": {
            "reference_original_results": str(ORIGINAL),
            "horizon_including_calibration": HORIZON,
            "calibration_periods": CALIBRATION_PERIODS,
            "evaluation_periods": HORIZON - CALIBRATION_PERIODS,
            "seeds": list(EVAL_SEEDS),
            "policies": POLICY_METHODS,
            "factorial_order": FACTORIAL_ORDER,
            "diagnostics_scope": "diagnostics averaged across seeds by regime and within [-5,+10] periods around each change, separately per edge",
            "exploration_influence_measure": "fraction of periods where index-based matching differs from matching on the same model's empirical-mean matrix; diagnostic only, not causal regret",
            "potential_outcomes": "same pre-generated pair-period Bernoulli uniforms as original S3b; unselected outcomes remain inaccessible to policies",
        },
        "original_policy_reproduction": reproduction,
        "conditions": output_conditions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    return output


def _recovery_summary(episodes, condition):
    boundaries = CONDITIONS[condition]["switches"]
    out = {}
    for policy in FACTORIAL_ORDER:
        lags = []
        censored = 0
        for episode in episodes:
            ids = episode["policies"][policy]["assignment_ids"]
            for idx, boundary in enumerate(boundaries):
                start = boundary - CALIBRATION_PERIODS
                stop_period = boundaries[idx + 1] if idx + 1 < len(boundaries) else HORIZON
                stop = stop_period - CALIBRATION_PERIODS
                optimum = permutation_id(solve(competence_matrix(condition, boundary)))
                lag = next((j - start for j in range(start, stop) if ids[j] == optimum), None)
                if lag is None:
                    censored += 1
                else:
                    lags.append(lag)
        out[policy] = {"mean_lag_uncensored": statistics.fmean(lags) if lags else None,
                       "uncensored_events": len(lags), "censored_events": censored}
    return out


def _format_diagnostics(aggregates, condition):
    output = {"by_regime_and_pair": [], "around_changes_and_pair": []}
    for key, aggregate in aggregates.items():
        if key[0] != condition:
            continue
        _, policy, kind, index, *edge = key
        row = {"policy": policy, "agent": edge[-2], "task": edge[-1], **aggregate.result()}
        if kind == "regime":
            row["regime"] = index
            output["by_regime_and_pair"].append(row)
        else:
            row["change_index"] = index
            row["periods_from_change"] = edge[0]
            row["agent"] = edge[1]
            row["task"] = edge[2]
            output["around_changes_and_pair"].append(row)
    return output


if __name__ == "__main__":
    result = run_experiment()
    print(f"Wrote {OUT}")
    for condition, values in result["conditions"].items():
        print(condition)
        for policy, summary in values["summaries"].items():
            print(f"  {policy}: {summary['expected_reward']['mean']:.2f} "
                  f"(95% CI {summary['expected_reward']['ci95'][0]:.2f}, "
                  f"{summary['expected_reward']['ci95'][1]:.2f})")
