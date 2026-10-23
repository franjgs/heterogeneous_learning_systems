#!/usr/bin/env python3
"""Offline, common-history diagnostic replay for HLS-S3b.

The replay conditions UCB1 and SW-UCB estimators on the same pair-level
observations from the recorded B2-Semi/UCB1 trajectories in S3b-E1. Decisions
are diagnostic only and never affect later observations.
"""

from __future__ import annotations

import gzip
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_e1 import (
    BREAKPOINTS,
    HORIZON,
    K,
    MATCHINGS,
    N,
    PAIRS,
    TRANSIENT,
    BASE,
    W_REF,
    XI,
    exact_matching,
    matrix_at,
    oracle_matching,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator


SOURCE = Path("results/experiments/hls_s3b_e1/period_traces.jsonl.gz")
OUT = Path("results/experiments/hls_s3b_offline_replay/results.json")
TRACE_OUT = OUT.parent / "period_traces.jsonl.gz"
SOURCE_POLICY = "B2-Semi/UCB1"
METHODS = ("UCB1", "SW-UCB")
RULES = ("UCB1_mean", "UCB1_index", "SW-UCB_mean", "SW-UCB_index")
REGIMES = {
    "base_pre": (0, BREAKPOINTS[0]),
    "transient": (BREAKPOINTS[0], BREAKPOINTS[1]),
    "base_post": (BREAKPOINTS[1], HORIZON),
    "pre_change_1": (BREAKPOINTS[0] - 200, BREAKPOINTS[0]),
    "post_change_1": (BREAKPOINTS[0], BREAKPOINTS[0] + 200),
    "pre_change_2": (BREAKPOINTS[1] - 200, BREAKPOINTS[1]),
    "post_change_2": (BREAKPOINTS[1], BREAKPOINTS[1] + 200),
}


def decode_feedback(feedback_mask: int, success_mask: int, n: int = N, k: int = K):
    """Decode only observed edge outcomes from the registered bit masks."""
    if success_mask & ~feedback_mask:
        raise ValueError("success mask contains an unobserved edge")
    return {
        (i, task): float(bool(success_mask & (1 << (i * k + task))))
        for i in range(n) for task in range(k)
        if feedback_mask & (1 << (i * k + task))
    }


def mean_ci(values):
    values = tuple(float(x) for x in values)
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = (student_t.ppf(0.975, len(values) - 1) * sd / math.sqrt(len(values))
            if len(values) > 1 else 0.0)
    return {"mean": mean, "sd": sd, "ci95": [mean - half, mean + half]}


def _sum_matching(matrix, matching):
    return sum(matrix[i][k] for i, k in matching)


def replay_events(truth_matrices, events, *, window=W_REF, xi=XI):
    """Replay one fixed event stream through both estimators and four rules.

    Each event is ``(observed_pairs, feedback_by_pair)`` for its period.
    The decisions produced at t are diagnostic and do not alter event t or
    any subsequent event.
    """
    if len(truth_matrices) != len(events):
        raise ValueError("one fixed observation event is required per period")
    models = {
        "UCB1": PairwiseBanditEstimator(N, K, method="ucb1", window=HORIZON, xi=xi),
        "SW-UCB": PairwiseBanditEstimator(N, K, method="sw_ucb", window=window, xi=xi),
    }
    result = {
        rule: {"regret": [], "reward": [], "optimal": [], "matching": [],
               "bonus_switch": []}
        for rule in RULES
    }
    mse = {method: [] for method in METHODS}
    relevant_mse = {method: [] for method in METHODS}
    pair_mse = {method: {f"{i},{k}": [] for i, k in PAIRS} for method in METHODS}
    diagnostics = {method: {"bonus_sum": 0.0, "bonus_count": 0,
                            "bonus_max": 0.0, "observations_used": [0] * (N * K),
                            "last_age_sum": [0] * (N * K), "last_age_n": [0] * (N * K),
                            "bonus_pair_sum": [0.0] * (N * K),
                            "bonus_pair_n": [0] * (N * K),
                            "empty_window_count": [0] * (N * K),
                            "selected_by_bonus": [0] * (N * K),
                            "mean_index_disagreement": 0, "period_count": 0}
                  for method in METHODS}

    for period, (truth, event) in enumerate(zip(truth_matrices, events)):
        oracle = oracle_matching(truth)
        oracle_value = _sum_matching(truth, oracle)
        matrices = {}
        for method, model in models.items():
            detail = model.diagnostic_matrix(period)
            means = tuple(tuple(cell["estimated_mean"] for cell in row) for row in detail)
            indices = tuple(tuple(cell["index"] for cell in row) for row in detail)
            mean_matching = exact_matching(means)
            index_matching = exact_matching(indices)
            matrices[(method, "mean")] = (means, mean_matching)
            matrices[(method, "index")] = (indices, index_matching)

            cell_errors = [(means[i][k] - truth[i][k]) ** 2 for i, k in PAIRS]
            mse[method].append(statistics.fmean(cell_errors))
            relevant_mse[method].append(statistics.fmean(
                (means[i][k] - truth[i][k]) ** 2 for i, k in oracle))
            for i, k in PAIRS:
                pair_mse[method][f"{i},{k}"].append((means[i][k] - truth[i][k]) ** 2)

            diag = diagnostics[method]
            diag["period_count"] += 1
            for i, k in PAIRS:
                cell = detail[i][k]
                used = cell["observations_used"]
                diag["observations_used"][i * K + k] += used
                if cell["last_observation_age"] is not None:
                    diag["last_age_sum"][i * K + k] += cell["last_observation_age"]
                    diag["last_age_n"][i * K + k] += 1
                bonus = cell["exploration_bonus"]
                if bonus is not None:
                    diag["bonus_sum"] += bonus
                    diag["bonus_count"] += 1
                    diag["bonus_max"] = max(diag["bonus_max"], bonus)
                    diag["bonus_pair_sum"][i * K + k] += bonus
                    diag["bonus_pair_n"][i * K + k] += 1
                elif method == "SW-UCB":
                    diag["empty_window_count"][i * K + k] += 1
            if mean_matching != index_matching:
                diag["mean_index_disagreement"] += 1
                chosen_by_bonus = set(index_matching) - set(mean_matching)
                for i, k in chosen_by_bonus:
                    diag["selected_by_bonus"][i * K + k] += 1

        for method in METHODS:
            mean_matching = matrices[(method, "mean")][1]
            index_matching = matrices[(method, "index")][1]
            for suffix, matching in (("mean", mean_matching), ("index", index_matching)):
                name = f"{method}_{suffix}"
                value = _sum_matching(truth, matching)
                result[name]["reward"].append(value)
                result[name]["regret"].append(max(0.0, oracle_value - value))
                result[name]["optimal"].append(matching == oracle)
                result[name]["matching"].append(MATCHINGS.index(matching))
            result[f"{method}_index"]["bonus_switch"].append(
                mean_matching != index_matching)

        observed_pairs, feedback = event
        if set(observed_pairs) != set(feedback):
            raise ValueError("event observations and feedback keys differ")
        for model in models.values():
            model.update(period, observed_pairs, feedback)

    for method in METHODS:
        diag = diagnostics[method]
        diag["mean_bonus"] = diag["bonus_sum"] / diag["bonus_count"] if diag["bonus_count"] else None
        diag["max_bonus"] = diag["bonus_max"]
        diag["bonus_changed_decision_rate"] = diag["mean_index_disagreement"] / len(events)
        diag["pairs"] = {
            f"{i},{k}": {
                "mean_observations_used_per_decision": diag["observations_used"][i * K + k] / len(events),
                "mean_last_observation_age": (
                    diag["last_age_sum"][i * K + k] / diag["last_age_n"][i * K + k]
                    if diag["last_age_n"][i * K + k] else None),
                "times_selected_only_by_index": diag["selected_by_bonus"][i * K + k],
                "mean_observed_bonus": (
                    diag["bonus_pair_sum"][i * K + k] / diag["bonus_pair_n"][i * K + k]
                    if diag["bonus_pair_n"][i * K + k] else None),
                "empty_window_fraction": diag["empty_window_count"][i * K + k] / len(events),
            }
            for i, k in PAIRS
        }
        for key in ("observations_used", "last_age_sum", "last_age_n", "selected_by_bonus",
                    "bonus_pair_sum", "bonus_pair_n", "empty_window_count",
                    "bonus_sum", "bonus_count", "bonus_max", "mean_index_disagreement",
                    "period_count"):
            diag.pop(key, None)

    return {"decisions": result, "mse": mse, "oracle_matching_mse": relevant_mse,
            "pair_mse": pair_mse,
            "diagnostics": diagnostics}


def _load_replay_source():
    seeds = []
    with gzip.open(SOURCE, "rt", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            trace = row["policies"][SOURCE_POLICY]
            if len(trace["feedback_mask"]) != HORIZON:
                raise ValueError(f"seed {row['seed']} has an unexpected horizon")
            events = []
            for t, (mask, success) in enumerate(zip(trace["feedback_mask"],
                                                     trace["feedback_success_mask"])):
                feedback = decode_feedback(mask, success)
                action_id = trace["action_id"][t]
                executed = set(MATCHINGS[action_id])
                if set(feedback) != executed:
                    raise ValueError(f"seed {row['seed']} period {t}: B2-Semi mask != executed matching")
                if sum(feedback.values()) != trace["realized_reward"][t]:
                    raise ValueError(f"seed {row['seed']} period {t}: observed outcomes != registered realized reward")
                events.append((tuple(sorted(feedback)), feedback))
            seeds.append((row["seed"], events))
    return seeds


def _aggregate_seed(seed, replay):
    summaries = {}
    for rule, series in replay["decisions"].items():
        summaries[rule] = {
            "expected_reward": sum(series["reward"]),
            "expected_regret": sum(series["regret"]),
            "optimal_rate": statistics.fmean(series["optimal"]),
        }
        for regime, (start, end) in REGIMES.items():
            if end <= len(series["regret"]):
                summaries[rule].setdefault("by_regime", {})[regime] = {
                    "expected_regret": sum(series["regret"][start:end]),
                    "optimal_rate": statistics.fmean(series["optimal"][start:end]),
                }
    return {"seed": seed, "decisions": summaries,
            "mse": {method: statistics.fmean(values) for method, values in replay["mse"].items()},
            "oracle_matching_mse": {method: statistics.fmean(values)
                                     for method, values in replay["oracle_matching_mse"].items()},
            "mse_by_regime": {
                method: {regime: statistics.fmean(values[start:end])
                         for regime, (start, end) in REGIMES.items()}
                for method, values in replay["mse"].items()},
            "oracle_matching_mse_by_regime": {
                method: {regime: statistics.fmean(values[start:end])
                         for regime, (start, end) in REGIMES.items()}
                for method, values in replay["oracle_matching_mse"].items()},
            "pair_mse": {method: {pair: statistics.fmean(values)
                                   for pair, values in by_pair.items()}
                         for method, by_pair in replay["pair_mse"].items()},
            "bonus_diagnostics": replay["diagnostics"]}


def _mean_by_regime(seed_rows, rule, regime, metric):
    return [row["decisions"][rule]["by_regime"][regime][metric] for row in seed_rows]


def run():
    seeds = _load_replay_source()
    if not seeds:
        raise ValueError("no replay source seeds found")
    if len({seed for seed, _ in seeds}) != len(seeds):
        raise ValueError("duplicate source seeds")
    seed_rows = []
    trace_rows = []
    all_rule_series = {rule: [] for rule in RULES}
    for seed, events in seeds:
        truth = [matrix_at(t) for t in range(HORIZON)]
        replay = replay_events(truth, events)
        seed_rows.append(_aggregate_seed(seed, replay))
        trace_rows.append({
            "seed": seed,
            "source_configuration": SOURCE_POLICY,
            "decisions": {rule: {
                "matching_id": values["matching"],
                "expected_reward": values["reward"],
                "diagnostic_regret": values["regret"],
                "optimal": values["optimal"],
                "bonus_changed_mean_matching": values["bonus_switch"],
            } for rule, values in replay["decisions"].items()},
            "mse_by_period": replay["mse"],
            "oracle_matching_mse_by_period": replay["oracle_matching_mse"],
            "source_observations": str(SOURCE),
        })
        for rule, values in replay["decisions"].items():
            all_rule_series[rule].append(values)

    performance = {}
    for rule, per_seed in all_rule_series.items():
        performance[rule] = {
            "expected_regret": mean_ci([sum(x["regret"]) for x in per_seed]),
            "expected_reward": mean_ci([sum(x["reward"]) for x in per_seed]),
            "optimal_rate": mean_ci([statistics.fmean(x["optimal"]) for x in per_seed]),
            "by_regime": {
                regime: {
                    "expected_regret": mean_ci([sum(x["regret"][start:end]) for x in per_seed]),
                    "optimal_rate": mean_ci([statistics.fmean(x["optimal"][start:end]) for x in per_seed]),
                } for regime, (start, end) in REGIMES.items()
            },
        }

    mse_summary = {
        method: mean_ci([row["mse"][method] for row in seed_rows])
        for method in METHODS
    }
    mse_summary["SW-UCB_minus_UCB1_paired"] = mean_ci([
        row["mse"]["SW-UCB"] - row["mse"]["UCB1"] for row in seed_rows])
    mse_summary["oracle_matching_pairs"] = {
        method: mean_ci([row["oracle_matching_mse"][method] for row in seed_rows])
        for method in METHODS
    }
    mse_summary["oracle_matching_pairs_SW_minus_UCB1_paired"] = mean_ci([
        row["oracle_matching_mse"]["SW-UCB"] - row["oracle_matching_mse"]["UCB1"]
        for row in seed_rows])
    mse_summary["by_regime"] = {
        regime: {
            method: mean_ci([row["mse_by_regime"][method][regime] for row in seed_rows])
            for method in METHODS
        } | {"SW-UCB_minus_UCB1_paired": mean_ci([
            row["mse_by_regime"]["SW-UCB"][regime] - row["mse_by_regime"]["UCB1"][regime]
            for row in seed_rows])}
        for regime in REGIMES
    }
    mse_summary["oracle_matching_pairs_by_regime"] = {
        regime: {
            method: mean_ci([row["oracle_matching_mse_by_regime"][method][regime]
                             for row in seed_rows])
            for method in METHODS
        } | {"SW-UCB_minus_UCB1_paired": mean_ci([
            row["oracle_matching_mse_by_regime"]["SW-UCB"][regime]
            - row["oracle_matching_mse_by_regime"]["UCB1"][regime]
            for row in seed_rows])}
        for regime in REGIMES
    }
    mse_summary["by_pair"] = {
        pair: {
            method: mean_ci([row["pair_mse"][method][pair] for row in seed_rows])
            for method in METHODS
        } | {"SW-UCB_minus_UCB1_paired": mean_ci([
            row["pair_mse"]["SW-UCB"][pair] - row["pair_mse"]["UCB1"][pair]
            for row in seed_rows])}
        for pair in (f"{i},{k}" for i, k in PAIRS)
    }
    contrasts = {}
    for lhs, rhs, label in (
        ("UCB1_mean", "SW-UCB_mean", "SW_mean_minus_UCB_mean"),
        ("UCB1_index", "SW-UCB_index", "SW_index_minus_UCB_index"),
        ("UCB1_mean", "UCB1_index", "UCB1_index_minus_mean"),
        ("SW-UCB_mean", "SW-UCB_index", "SW_index_minus_mean"),
    ):
        contrasts[label] = mean_ci([
            row["decisions"][rhs]["expected_regret"] - row["decisions"][lhs]["expected_regret"]
            for row in seed_rows])
    by_regime_contrasts = {}
    for regime in REGIMES:
        by_regime_contrasts[regime] = {}
        for lhs, rhs, label in (
            ("UCB1_mean", "SW-UCB_mean", "SW_mean_minus_UCB_mean"),
            ("UCB1_index", "SW-UCB_index", "SW_index_minus_UCB_index"),
            ("UCB1_mean", "UCB1_index", "UCB1_index_minus_mean"),
            ("SW-UCB_mean", "SW-UCB_index", "SW_index_minus_mean"),
        ):
            a = _mean_by_regime(seed_rows, lhs, regime, "expected_regret")
            b = _mean_by_regime(seed_rows, rhs, regime, "expected_regret")
            by_regime_contrasts[regime][label] = mean_ci([y - x for x, y in zip(a, b)])

    observation_counts = {f"{i},{k}": 0 for i, k in PAIRS}
    observation_counts_by_regime = {regime: {f"{i},{k}": 0 for i, k in PAIRS}
                                    for regime in REGIMES}
    for _, events in seeds:
        for t, (pairs, _) in enumerate(events):
            for i, k in pairs:
                observation_counts[f"{i},{k}"] += 1
                for regime, (start, end) in REGIMES.items():
                    if start <= t < end:
                        observation_counts_by_regime[regime][f"{i},{k}"] += 1
    n_seeds = len(seeds)
    observation_counts = {key: value / n_seeds for key, value in observation_counts.items()}
    observation_counts_by_regime = {
        regime: {key: value / n_seeds for key, value in rows.items()}
        for regime, rows in observation_counts_by_regime.items()
    }

    result = {
        "experiment": "HLS-S3b offline common-history diagnostic replay",
        "status": "diagnostic replay; not closed-loop policy evaluation",
        "source": {
            "artifact": str(SOURCE), "experiment": "HLS-S3b-E1",
            "configuration": SOURCE_POLICY, "seeds": [seed for seed, _ in seeds],
            "horizon": HORIZON, "feedback": "three individual Bernoulli outcomes from each executed B2-Semi matching",
            "competence_regimes": {"base": BASE, "transient": TRANSIENT,
                                   "breakpoints": list(BREAKPOINTS)},
            "selection_reason": "Factorial artifact has aggregate expected/realized reward and observation masks but no pair-level Bernoulli success outcomes; E1 trace has the pair-level outcomes needed for a valid common-history replay. B2-Semi/UCB1 is a representative full-feedback 3x3 history, retained as a fixed source stream for both estimators.",
            "source_history_limitation": "All histories were generated by the original B2-Semi/UCB1 closed-loop organization; replay results are conditional on these UCB1-origin histories and are not an unbiased sample of histories generated by SW-UCB.",
        },
        "replay": {
            "estimators": {
                "UCB1": "existing per-pair full-history mean plus sqrt(2 log(max(2,t+1))/n)",
                "SW-UCB": f"existing per-pair global-period window W={W_REF}, xi={XI}; empirical mean over observations in [t-W,t)",
            },
            "diagnostic_decisions": RULES,
            "shared_input": "For each seed, both estimators receive exactly the same observed pair/reward events at original periods; diagnostic decisions never affect subsequent input.",
            "decision_information": "Estimators use only past replay events. True competence matrices are used after decision construction only to calculate MSE and expected reward/regret.",
            "mse_timing": "Estimate at period t is evaluated against the competence matrix at t before period-t feedback is delivered.",
            "bonus_effect": "Within each estimator and frozen history, index-matching versus mean-matching expected-regret difference is the immediate local effect of substituting index scores for empirical means; it excludes future feedback consequences.",
            "regimes": {key: list(value) for key, value in REGIMES.items()},
        },
        "summary": {"n_seeds": n_seeds, "mean_cumulative_metrics": performance,
                    "mse": mse_summary, "paired_regret_contrasts": contrasts,
                    "paired_regret_contrasts_by_regime": by_regime_contrasts,
                    "mean_observations_per_pair": observation_counts,
                    "mean_observations_per_pair_by_period_window": observation_counts_by_regime,
                    "mean_bonus_change_decision_rate": {
                        method: mean_ci([row["bonus_diagnostics"][method]["bonus_changed_decision_rate"]
                                         for row in seed_rows]) for method in METHODS},
                    "mean_bonus_and_max_bonus": {
                        method: {
                            "mean_bonus": mean_ci([row["bonus_diagnostics"][method]["mean_bonus"]
                                                   for row in seed_rows]),
                            "mean_max_bonus": mean_ci([row["bonus_diagnostics"][method]["max_bonus"]
                                                       for row in seed_rows]),
                            "pairs": {
                                pair: {
                                    "mean_observations_used_per_decision": mean_ci([
                                        row["bonus_diagnostics"][method]["pairs"][pair]["mean_observations_used_per_decision"]
                                        for row in seed_rows]),
                                    "mean_last_observation_age": mean_ci([
                                        row["bonus_diagnostics"][method]["pairs"][pair]["mean_last_observation_age"]
                                        for row in seed_rows if row["bonus_diagnostics"][method]["pairs"][pair]["mean_last_observation_age"] is not None]),
                                    "times_selected_only_by_index_mean": statistics.fmean([
                                        row["bonus_diagnostics"][method]["pairs"][pair]["times_selected_only_by_index"]
                                        for row in seed_rows]),
                                    "mean_observed_bonus": mean_ci([
                                        row["bonus_diagnostics"][method]["pairs"][pair]["mean_observed_bonus"]
                                        for row in seed_rows
                                        if row["bonus_diagnostics"][method]["pairs"][pair]["mean_observed_bonus"] is not None]),
                                    "empty_window_fraction": mean_ci([
                                        row["bonus_diagnostics"][method]["pairs"][pair]["empty_window_fraction"]
                                        for row in seed_rows]),
                                } for pair in (f"{i},{k}" for i, k in PAIRS)
                            },
                        } for method in METHODS
                    },
                    "matching_frequencies_by_regime": {
                        rule: {
                            regime: {
                                str(matching_id): statistics.fmean([
                                    series["matching"][start:end].count(matching_id) / (end - start)
                                    for series in all_rule_series[rule]])
                                for matching_id in range(len(MATCHINGS))
                            }
                            for regime, (start, end) in REGIMES.items()
                        } for rule in RULES
                    },
                    "true_optimal_matching_margins": {
                        regime: {
                            "mean": (lambda values: statistics.fmean(values))([
                                sorted((_sum_matching(matrix_at(t), m) for m in MATCHINGS), reverse=True)[0]
                                - sorted((_sum_matching(matrix_at(t), m) for m in MATCHINGS), reverse=True)[1]
                                for t in range(start, end)])
                        } for regime, (start, end) in REGIMES.items()
                    },
                    "seed_results": seed_rows},
        "limits": [
            "This is a diagnostic replay conditioned on an existing UCB1-generated action/feedback trajectory, not a closed-loop policy comparison.",
            "The E1 environment has one transient competence regime followed by a return to baseline; factorial recurrent-regime pair-level outcomes were not saved and were not reconstructed.",
            "MSE and expected decision regret are evaluated descriptively on the same frozen histories; their association does not establish general causal mediation.",
            "The local index-versus-mean contrast identifies only the immediate decision effect on the frozen history, not future effects through altered observation acquisition.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(TRACE_OUT, "wt", encoding="utf-8") as stream:
        for row in trace_rows:
            stream.write(json.dumps(row, separators=(",", ":")) + "\n")
    result["replay"]["period_traces"] = str(TRACE_OUT)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    out = run()
    print(json.dumps({
        "output": str(OUT),
        "mse": out["summary"]["mse"],
        "regret": {name: value["expected_regret"]
                   for name, value in out["summary"]["mean_cumulative_metrics"].items()},
        "contrasts": out["summary"]["paired_regret_contrasts"],
    }, indent=2))
