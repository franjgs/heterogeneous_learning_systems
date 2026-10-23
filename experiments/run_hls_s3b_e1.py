#!/usr/bin/env python3
"""HLS-S3b-E1: paired UCB1/SW-UCB comparison across information modalities."""

from __future__ import annotations

import gzip
import itertools
import json
import math
import random
import statistics
import time
from pathlib import Path

from scipy.stats import t as student_t

from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.nonstationary_assignment import PairwiseBanditEstimator

OUT = Path("results/experiments/hls_s3b_e1")
SUMMARY = OUT / "results.json"
TRACES = OUT / "period_traces.jsonl.gz"
N = K = 3
HORIZON = 10_000
SEEDS = tuple(range(8200, 8230))
BREAKPOINTS = (3_000, 5_000)
CALIBRATION = 9
XI = 2.0
W_REF = round(4 * math.sqrt(HORIZON * math.log(HORIZON)))
W_LONG = min(HORIZON, 2 * W_REF)
BASE = ((0.80, 0.05, 0.05), (0.05, 0.80, 0.05), (0.40, 0.05, 0.10))
TRANSIENT = ((0.80, 0.05, 0.05), (0.05, 0.80, 0.05), (0.90, 0.05, 0.10))
CALIBRATION_PERMUTATIONS = ((0, 1, 2), (1, 2, 0), (2, 0, 1))
REGIMES = (("base_pre", 0, 3_000), ("transient", 3_000, 5_000),
           ("base_post", 5_000, HORIZON))
POST_CHANGE_WINDOWS = ((3_000, 3_200), (5_000, 5_200))
PERMUTATIONS = tuple(itertools.permutations(range(N)))
MATCHINGS = tuple(tuple(sorted((permutation[k], k) for k in range(K)))
                  for permutation in PERMUTATIONS)
MATCH_ID = {matching: index for index, matching in enumerate(MATCHINGS)}
PAIRS = tuple((i, k) for i in range(N) for k in range(K))
ASSIGNER = HungarianAssignmentOptimizerNK()
ORG = OrganizationConfigNK(tuple(f"a{i}" for i in range(N)), tuple(f"t{k}" for k in range(K)),
                           ((0.5,) * K,) * N, (1.0,) * N, float(N))
PROBLEM = ProblemSpecNK("S3b-E1", (1.0,) * K, float(N))


def matrix_at(period: int):
    return TRANSIENT if BREAKPOINTS[0] <= period < BREAKPOINTS[1] else BASE


def exact_matching(values):
    """Use the existing assignment optimizer; enumerate six matchings for ties/check."""
    result = ASSIGNER.optimize(values, ORG, PROBLEM, maximize=True)
    candidates = [(sum(values[i][k] for i, k in matching), matching)
                  for matching in MATCHINGS]
    optimum = max(value for value, _ in candidates)
    if not math.isclose(result.objective_value, optimum, rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("assignment solver differs from exhaustive 3x3 optimum")
    tied = [matching for value, matching in candidates
            if math.isclose(value, optimum, rel_tol=0.0, abs_tol=1e-12)]
    selected = min(tied)
    if len(selected) != K or len({i for i, _ in selected}) != K or len({k for _, k in selected}) != K:
        raise AssertionError("B2 action is not a complete one-to-one matching")
    return selected


def oracle_matching(values):
    """Independent six-permutation evaluator for the true-mean oracle."""
    return min((matching for matching in MATCHINGS),
               key=lambda matching: (-sum(values[i][k] for i, k in matching), matching))


def mean_pair(values):
    return min(PAIRS, key=lambda pair: (-values[pair[0]][pair[1]], pair))


def calibration_matching(period: int):
    permutation = CALIBRATION_PERMUTATIONS[period % 3]
    return tuple(sorted((permutation[k], k) for k in range(K)))


def _rng_uniforms(seed: int):
    rng = random.Random(seed ^ 0xD0C0A7)
    return tuple(tuple(tuple(rng.random() for _ in range(K)) for _ in range(N))
                 for _ in range(HORIZON))


def _partial_ranks(seed: int):
    rng = random.Random(seed ^ 0xB2F33D)
    return tuple(rng.randrange(K) for _ in range(HORIZON))


def configurations():
    return (
        {"key": "B1/UCB1", "modality": "B1", "method": "ucb1", "window": HORIZON},
        {"key": "B1/SW-UCB-Wref", "modality": "B1", "method": "sw_ucb", "window": W_REF},
        {"key": "B2-Semi/UCB1", "modality": "B2-Semi", "method": "ucb1", "window": HORIZON},
        {"key": "B2-Semi/SW-UCB-Wref", "modality": "B2-Semi", "method": "sw_ucb", "window": W_REF},
        {"key": "B2-Semi/SW-UCB-Wlong", "modality": "B2-Semi", "method": "sw_ucb", "window": W_LONG},
        {"key": "B2-Partial/UCB1", "modality": "B2-Partial", "method": "ucb1", "window": HORIZON},
        {"key": "B2-Partial/SW-UCB-Wref", "modality": "B2-Partial", "method": "sw_ucb", "window": W_REF},
    )


def evaluate_seed(seed: int):
    uniforms = _rng_uniforms(seed)
    partial_ranks = _partial_ranks(seed)
    episodes = {}
    traces = {}
    for config in configurations():
        modality, method, window = config["modality"], config["method"], config["window"]
        model = PairwiseBanditEstimator(N, K, method=method, window=window, xi=XI)
        expected, realized, regret, action_ids, feedback_masks, success_masks = [], [], [], [], [], []
        executed_success_masks = []
        expected_by_period, regret_by_period = [], []
        period_diagnostics = []
        started = time.perf_counter()
        previous_action = None
        for t in range(HORIZON):
            means = matrix_at(t)
            outcomes = tuple(tuple(int(uniforms[t][i][k] < means[i][k]) for k in range(K))
                             for i in range(N))
            oracle_pair = mean_pair(means)
            oracle_match = oracle_matching(means)
            if modality == "B1":
                if t < CALIBRATION:
                    selected = (PAIRS[t],)
                    decision_info = None
                else:
                    decision_info = model.diagnostic_matrix(t)
                    index_matrix = tuple(tuple(cell["index"] for cell in row)
                                         for row in decision_info)
                    selected = (min(PAIRS, key=lambda pair: (-index_matrix[pair[0]][pair[1]], pair)),)
                action_id = selected[0][0] * K + selected[0][1]
                decision_value = means[selected[0][0]][selected[0][1]]
                oracle_value = means[oracle_pair[0]][oracle_pair[1]]
                optimal = selected[0] == oracle_pair
                mean_action = None
                if decision_info is not None:
                    estimate_matrix = model.empirical_mean_matrix(t)
                    mean_action = min(PAIRS, key=lambda pair: (-estimate_matrix[pair[0]][pair[1]], pair))
                    index_matrix = tuple(tuple(cell["index"] for cell in row) for row in decision_info)
            else:
                if t < CALIBRATION:
                    matching = calibration_matching(t)
                    decision_info = None
                else:
                    decision_info = model.diagnostic_matrix(t)
                    index_matrix = tuple(tuple(cell["index"] for cell in row)
                                         for row in decision_info)
                    matching = exact_matching(index_matrix)
                selected = matching
                action_id = MATCH_ID[matching]
                decision_value = sum(means[i][k] for i, k in matching)
                oracle_value = sum(means[i][k] for i, k in oracle_match)
                optimal = matching == oracle_match
                mean_action = None
                if decision_info is not None:
                    estimate_matrix = model.empirical_mean_matrix(t)
                    mean_action = exact_matching(estimate_matrix)
                    index_matrix = tuple(tuple(cell["index"] for cell in row) for row in decision_info)

            realized_value = sum(outcomes[i][k] for i, k in selected)
            period_expected = decision_value
            period_regret = max(0.0, oracle_value - decision_value)
            if t < CALIBRATION:
                feedback_edges = selected
                if modality == "B2-Partial":
                    cycle_rank = t // 3
                    feedback_edges = (sorted(selected)[cycle_rank],)
            elif modality == "B2-Partial":
                feedback_edges = (sorted(selected)[partial_ranks[t]],)
            else:
                feedback_edges = selected

            mask = 0
            successes = 0
            feedback = {}
            for i, k in feedback_edges:
                bit = 1 << (i * K + k)
                mask |= bit
                value = outcomes[i][k]
                feedback[(i, k)] = value
                if value:
                    successes |= bit
            executed_successes = sum(1 << (i * K + k) for i, k in selected
                                     if outcomes[i][k])
            selected_mask = sum(1 << (i * K + k) for i, k in selected)
            if realized_value != executed_successes.bit_count():
                raise AssertionError("recorded realized reward disagrees with executed Bernoulli outcomes")
            if mask & ~selected_mask or successes & ~mask or successes & ~executed_successes:
                raise AssertionError("feedback contains an unexecuted/unobserved reward")
            model.update(t, feedback_edges, feedback)

            expected.append(round(period_expected, 6))
            realized.append(realized_value)
            regret.append(round(period_regret, 6))
            expected_by_period.append(period_expected)
            regret_by_period.append(period_regret)
            action_ids.append(action_id)
            feedback_masks.append(mask)
            success_masks.append(successes)
            executed_success_masks.append(executed_successes)
            if decision_info is not None and (t % 100 == 0 or t in {2_999, 3_000, 3_199, 3_200, 4_999, 5_000, 5_199, 5_200}):
                estimate = tuple(tuple(cell["estimated_mean"] for cell in row)
                                 for row in decision_info)
                indices = tuple(tuple(cell["index"] for cell in row) for row in decision_info)
                bonuses = tuple(tuple(-1.0 if cell["exploration_bonus"] is None
                                      else cell["exploration_bonus"] for cell in row)
                                for row in decision_info)
                used = tuple(tuple(cell["observations_used"] for cell in row)
                             for row in decision_info)
                discarded = tuple(tuple(cell["observations_discarded"] for cell in row)
                                   for row in decision_info)
                age = tuple(tuple(-1 if cell["last_observation_age"] is None
                                  else cell["last_observation_age"] for cell in row)
                            for row in decision_info)
                period_diagnostics.append({"period": t, "estimated_means": estimate,
                                           "indices": indices, "bonuses": bonuses,
                                           "observations_used": used, "observations_discarded": discarded,
                                           "last_observation_age": age,
                                           "index_vs_mean_action_differs": mean_action != selected[0] if modality == "B1" else mean_action != selected})
            previous_action = action_id

        elapsed = time.perf_counter() - started
        regimes = {}
        for name, start, end in REGIMES:
            regimes[name] = _segment_summary(expected_by_period, realized, regret, action_ids,
                                             modality, start, end, means_at=matrix_at)
        windows = {}
        for start, end in POST_CHANGE_WINDOWS:
            windows[f"{start}:{end}"] = _segment_summary(expected_by_period, realized, regret,
                                                          action_ids, modality, start, end,
                                                          means_at=matrix_at)
        observation_counts = {f"{i},{k}": sum(bool(mask & (1 << (i * K + k)))
                                                for mask in feedback_masks) for i, k in PAIRS}
        feedback_by_regime = {}
        selections_by_regime = {}
        for name, start, end in REGIMES:
            feedback_by_regime[name] = {
                f"{i},{k}": sum(bool(feedback_masks[t] & (1 << (i * K + k)))
                                for t in range(start, end)) for i, k in PAIRS}
            selections_by_regime[name] = {
                f"{i},{k}": sum((action_ids[t] == i * K + k) if modality == "B1" else
                                (MATCHINGS[action_ids[t]] and (i, k) in MATCHINGS[action_ids[t]])
                                for t in range(start, end)) for i, k in PAIRS}
        selection_counts = {f"{i},{k}": sum(
            ((action == i * K + k) if modality == "B1" else
             ((1 << (i * K + k)) & sum(1 << (aa * K + kk) for aa, kk in MATCHINGS[action])) != 0)
            for action in action_ids) for i, k in PAIRS}
        chosen_edges_by_period = [((action // K, action % K),) if modality == "B1"
                                  else MATCHINGS[action] for action in action_ids]
        optimal_flags = []
        for t, chosen in enumerate(chosen_edges_by_period):
            means = matrix_at(t)
            optimal_flags.append(chosen[0] == mean_pair(means) if modality == "B1"
                                 else chosen == oracle_matching(means))
        changes = sum(action_ids[t] != action_ids[t - 1] for t in range(1, HORIZON))
        recovery = []
        for boundary, next_boundary in ((3_000, 5_000), (5_000, HORIZON)):
            run = next((start for start in range(boundary, next_boundary - 19)
                        if all(optimal_flags[t] for t in range(start, start + 20))), None)
            recovery.append(None if run is None else run - boundary)
        current_error_sum = 0.0
        current_error_n = 0
        feedback_age_sums = [0.0] * 9
        feedback_age_counts = [0] * 9
        window_count_sums = [0.0] * 9
        window_count_n = 0
        for snapshot in period_diagnostics:
            t = snapshot["period"]
            truth = matrix_at(t)
            for i, k in PAIRS:
                current_error_sum += (snapshot["estimated_means"][i][k] - truth[i][k]) ** 2
                current_error_n += 1
                age = snapshot["last_observation_age"][i][k]
                if age >= 0:
                    feedback_age_sums[i * K + k] += age
                    feedback_age_counts[i * K + k] += 1
                window_count_sums[i * K + k] += snapshot["observations_used"][i][k]
            window_count_n += 1
        episodes[config["key"]] = {
            "modality": modality, "method": method, "window": window,
            "cumulative_expected_reward": round(sum(expected_by_period), 6),
            "cumulative_realized_reward": sum(realized),
            "cumulative_expected_regret": round(sum(regret_by_period), 6),
            "calibration_expected_reward": round(sum(expected_by_period[:CALIBRATION]), 6),
            "evaluation_expected_reward": round(sum(expected_by_period[CALIBRATION:]), 6),
            "calibration_expected_regret": round(sum(regret_by_period[:CALIBRATION]), 6),
            "evaluation_expected_regret": round(sum(regret_by_period[CALIBRATION:]), 6),
            "optimal_decision_rate": statistics.fmean(optimal_flags),
            "assignment_changes": changes,
            "recovery_lag_20_consecutive_optimal": recovery,
            "selection_counts_by_pair": selection_counts,
            "selection_counts_by_pair_and_regime": selections_by_regime,
            "feedback_observations_by_pair": observation_counts,
            "feedback_observations_by_pair_and_regime": feedback_by_regime,
            "regimes": regimes, "post_change_windows": windows,
            "mean_estimation_mse_at_diagnostic_snapshots": current_error_sum / current_error_n,
            "bonus_changed_action_frequency_at_diagnostic_snapshots": statistics.fmean(
                float(item["index_vs_mean_action_differs"]) for item in period_diagnostics),
            "mean_observations_used_at_snapshots_by_pair": {
                f"{i},{k}": window_count_sums[i * K + k] / window_count_n
                for i, k in PAIRS},
            "mean_age_of_last_observation_at_snapshots_by_pair": {
                f"{i},{k}": (feedback_age_sums[i * K + k] / feedback_age_counts[i * K + k]
                              if feedback_age_counts[i * K + k] else None) for i, k in PAIRS},
            "diagnostic_sample_periods": [x["period"] for x in period_diagnostics],
            "runtime_seconds": elapsed,
        }
        traces[config["key"]] = {
            "expected_reward": expected, "realized_reward": realized,
            "expected_regret": regret, "action_id": action_ids,
            "feedback_mask": feedback_masks, "feedback_success_mask": success_masks,
            "executed_success_mask": executed_success_masks,
            "diagnostics": period_diagnostics,
        }
    return {"seed": seed, "policies": episodes, "traces": traces}


def _segment_summary(expected, realized, regret, action_ids, modality, start, end, *, means_at):
    if modality == "B1":
        optimal = []
        for t in range(start, end):
            action = action_ids[t]
            pair = (action // K, action % K)
            optimal.append(pair == mean_pair(means_at(t)))
    else:
        optimal = [MATCHINGS[action_ids[t]] == oracle_matching(means_at(t))
                   for t in range(start, end)]
    return {"periods": end - start,
            "expected_reward": round(sum(expected[start:end]), 6),
            "realized_reward": sum(realized[start:end]),
            "expected_regret": round(sum(regret[start:end]), 6),
            "optimal_decision_rate": statistics.fmean(optimal),
            "mean_expected_reward_per_period": statistics.fmean(expected[start:end]),
            "mean_regret_per_period": statistics.fmean(regret[start:end])}


def paired_ci(values):
    values = tuple(float(x) for x in values)
    if not values:
        return {"n": 0, "mean": None, "sd": None, "ci95": [None, None]}
    mean = statistics.fmean(values)
    if len(values) < 2:
        return {"n": len(values), "mean": mean, "sd": None, "ci95": [None, None]}
    sd = statistics.stdev(values)
    half = float(student_t.ppf(0.975, len(values) - 1)) * sd / math.sqrt(len(values))
    return {"n": len(values), "mean": mean, "sd": sd, "ci95": [mean - half, mean + half]}


def _summarize(episodes):
    keys = tuple(episodes[0]["policies"])
    policies = {}
    for key in keys:
        rows = [episode["policies"][key] for episode in episodes]
        policies[key] = {
            "modality": rows[0]["modality"], "method": rows[0]["method"], "window": rows[0]["window"],
            **{metric: paired_ci(row[metric] for row in rows) for metric in (
                "cumulative_expected_reward", "cumulative_realized_reward",
                "cumulative_expected_regret", "evaluation_expected_reward",
                "evaluation_expected_regret", "optimal_decision_rate", "assignment_changes",
                "mean_estimation_mse_at_diagnostic_snapshots",
                "bonus_changed_action_frequency_at_diagnostic_snapshots", "runtime_seconds")},
            "regimes": {name: {metric: paired_ci(row["regimes"][name][metric] for row in rows)
                                for metric in ("expected_reward", "realized_reward", "expected_regret",
                                               "optimal_decision_rate", "mean_regret_per_period")}
                        for name, _, _ in REGIMES},
            "post_change_windows": {name: {metric: paired_ci(row["post_change_windows"][name][metric]
                                                               for row in rows)
                                            for metric in ("expected_regret", "optimal_decision_rate")}
                                    for name in ("3000:3200", "5000:5200")},
            "recovery_lag_20_consecutive_optimal": {
                str(index): paired_ci(row["recovery_lag_20_consecutive_optimal"][index]
                                      for row in rows if row["recovery_lag_20_consecutive_optimal"][index] is not None)
                for index in (0, 1)},
            "feedback_observations_by_pair_mean": {
                pair: statistics.fmean(row["feedback_observations_by_pair"][pair] for row in rows)
                for pair in rows[0]["feedback_observations_by_pair"]},
            "selection_counts_by_pair_mean": {
                pair: statistics.fmean(row["selection_counts_by_pair"][pair] for row in rows)
                for pair in rows[0]["selection_counts_by_pair"]},
            "mean_age_by_pair": {
                pair: statistics.fmean(row["mean_age_of_last_observation_at_snapshots_by_pair"][pair]
                                       for row in rows if row["mean_age_of_last_observation_at_snapshots_by_pair"][pair] is not None)
                for pair in rows[0]["mean_age_of_last_observation_at_snapshots_by_pair"]},
            "mean_observations_used_by_pair": {
                pair: statistics.fmean(row["mean_observations_used_at_snapshots_by_pair"][pair]
                                       for row in rows)
                for pair in rows[0]["mean_observations_used_at_snapshots_by_pair"]},
        }

    contrasts = {}
    for left, right, label in (
        ("B1/SW-UCB-Wref", "B1/UCB1", "B1_SW_minus_UCB"),
        ("B2-Semi/SW-UCB-Wref", "B2-Semi/UCB1", "B2-Semi_SWref_minus_UCB"),
        ("B2-Partial/SW-UCB-Wref", "B2-Partial/UCB1", "B2-Partial_SWref_minus_UCB"),
        ("B2-Semi/UCB1", "B2-Partial/UCB1", "B2-Semi_minus_Partial_UCB"),
        ("B2-Semi/SW-UCB-Wref", "B2-Partial/SW-UCB-Wref", "B2-Semi_minus_Partial_SWref"),
        ("B2-Semi/SW-UCB-Wlong", "B2-Semi/SW-UCB-Wref", "B2-Semi_SWlong_minus_SWref"),
    ):
        contrasts[label] = {}
        for metric in ("cumulative_expected_reward", "cumulative_expected_regret",
                       "evaluation_expected_regret", "optimal_decision_rate"):
            contrasts[label][metric] = paired_ci(
                episode["policies"][left][metric] - episode["policies"][right][metric]
                for episode in episodes)
    return {"policies": policies, "paired_contrasts": contrasts}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    overall_start = time.perf_counter()
    episodes = []
    with gzip.open(TRACES, "wt", encoding="utf-8", compresslevel=6) as stream:
        for seed in SEEDS:
            episode = evaluate_seed(seed)
            episodes.append({"seed": episode["seed"], "policies": episode["policies"]})
            stream.write(json.dumps({"seed": seed, "policies": episode["traces"]},
                                    separators=(",", ":")) + "\n")
            print(f"completed seed {seed}", flush=True)
    summary = _summarize(episodes)
    payload = {
        "experiment": "HLS-S3b-E1",
        "title": "Interaction between learning, information and organization",
        "reference_specification": "engineering register, 2026-10-21, E1.1",
        "protocol": {
            "agents": N, "tasks": K, "horizon_including_calibration": HORIZON,
            "evaluation_periods": HORIZON - CALIBRATION, "seeds": list(SEEDS),
            "breakpoints": list(BREAKPOINTS), "base_matrix": BASE,
            "transient_matrix": TRANSIENT, "calibration_periods": CALIBRATION,
            "calibration_B1": "each of 9 pairs once in lexicographic order",
            "calibration_B2": "three matching cycle repeated three times",
            "B2_partial_calibration_rank": "cycle repetition index 0,1,2",
            "reward_potential_stream": "random.Random(seed XOR 0xD0C0A7), order period-agent-task",
            "partial_feedback_stream": "random.Random(seed XOR 0xB2F33D), one rank in 0,1,2 per period",
            "window_reference": W_REF, "window_long": W_LONG, "xi": XI,
            "tiebreak": "lexicographically smallest maximum-score matching; solver value verified by six-permutation enumeration",
            "B1_oracle": "maximum true-mean pair each period",
            "B2_oracle": "maximum true-mean full matching each period",
            "trace_encoding": "period index implicit; action ids and observed/success edge masks; compressed JSONL sidecar",
        },
        "policy_definitions": {
            "B1": "select one of nine agent-task pairs; observe only its Bernoulli reward",
            "B2-Semi": "execute a complete matching; observe each of the three individual Bernoulli rewards",
            "B2-Partial": "execute same complete matching; observe one executed edge, selected by pre-generated rank",
            "UCB1": "existing PairwiseBanditEstimator; mean over full pair history plus sqrt(2 log(max(2,t+1))/n)",
            "SW-UCB": "existing PairwiseBanditEstimator; global-period window and xi=2 confidence bonus",
            "adaptation_note": "Per-edge indices composed with multi-play choice/matching are HLS experimental adaptations; no single-play regret guarantee is asserted.",
        },
        "condition_checks": {
            "base_oracle_matching": [[0, 0], [1, 1], [2, 2]],
            "base_oracle_value": 1.7,
            "transient_oracle_matching": [[0, 2], [1, 1], [2, 0]],
            "transient_oracle_value": 1.75,
            "base_matching_margin": 0.45,
            "transient_matching_margin": 0.05,
            "B1_oracle_expected_total": 8_200.0,
            "B2_oracle_expected_total": 17_100.0,
            "B1_base_best_mean": 0.8,
            "B1_transient_best_mean": 0.9,
        },
        "summary": summary,
        "episodes": episodes,
        "artifacts": {"period_traces": str(TRACES)},
        "total_runtime_seconds": time.perf_counter() - overall_start,
        "limitations": [
            "B1 E1 has nine candidate pairs and is not an exact reproduction of the prior three-arm B1 result.",
            "B1 and B2 use different action sets and reward scales; absolute regret is not compared across modalities.",
            "B2-Semi versus B2-Partial is a closed-loop feedback-protocol contrast; histories and later actions diverge.",
            "SW-UCB xi=2 is the predeclared E1 common confidence scale, not a claim that the compositional B2 method inherits original single-play guarantees.",
            "The scenario is synthetic and does not represent empirically calibrated cycle durations.",
        ],
    }
    SUMMARY.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {SUMMARY}; traces {TRACES}; elapsed={payload['total_runtime_seconds']:.2f}s")


if __name__ == "__main__":
    main()
