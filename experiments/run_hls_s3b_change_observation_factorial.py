#!/usr/bin/env python3
"""Small paired S3b factorial: competence-change interval × feedback availability."""

from __future__ import annotations

import gzip
import json
import math
import random
import statistics
import time
from collections import deque
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_e1 import (
    BASE, CALIBRATION, CALIBRATION_PERMUTATIONS, HORIZON, K, MATCH_ID,
    MATCHINGS, N, PAIRS, TRANSIENT, exact_matching, oracle_matching,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator

OUT_DIR = Path("results/experiments/hls_s3b_change_observation_factorial")
SUMMARY_PATH = OUT_DIR / "results.json"
TRACE_PATH = OUT_DIR / "period_traces.jsonl.gz"
SEEDS = tuple(range(8200, 8230))
CHANGE_INTERVALS = {"infrequent": 2_500, "frequent": 500}
OBSERVATION_PROBABILITIES = {"high": 0.75, "low": 0.25}
POLICIES = ("UCB1", "SW-UCB")
XI = 2.0
WINDOW = round(4 * math.sqrt(HORIZON * math.log(HORIZON)))
RECOVERY_RUN = 20
RECOVERY_SEARCH = 1_000
CRITICAL_PAIRS = ((0, 0), (0, 2), (1, 1), (2, 0), (2, 2))


def regime_index(period: int, interval: int) -> int:
    return period // interval


def matrix_at(period: int, interval: int):
    return BASE if regime_index(period, interval) % 2 == 0 else TRANSIENT


def change_times(interval: int) -> tuple[int, ...]:
    return tuple(range(interval, HORIZON, interval))


def matching_id(matching) -> int:
    return MATCH_ID[tuple(sorted(matching))]


def calibration_matching(period: int):
    permutation = CALIBRATION_PERMUTATIONS[period % len(CALIBRATION_PERMUTATIONS)]
    return tuple(sorted((permutation[k], k) for k in range(K)))


def generate_randomness(seed: int):
    reward_rng = random.Random(seed ^ 0xA17E5B)
    opportunity_rng = random.Random(seed ^ 0x0B5E7A)
    reward_uniforms = tuple(tuple(tuple(reward_rng.random() for _ in range(K))
                                  for _ in range(N)) for _ in range(HORIZON))
    opportunity_uniforms = tuple(tuple(tuple(opportunity_rng.random() for _ in range(K))
                                       for _ in range(N)) for _ in range(HORIZON))
    return reward_uniforms, opportunity_uniforms


def opportunity_mask(uniforms, probability: float) -> int:
    return sum((1 << (i * K + k)) for i, k in PAIRS if uniforms[i][k] < probability)


def _regime_label(period: int, interval: int) -> str:
    return "base" if regime_index(period, interval) % 2 == 0 else "transient"


def _recovery_lag(actions: list[int], oracle_ids: list[int], boundary: int,
                  next_boundary: int) -> int | None:
    stop = min(next_boundary - RECOVERY_RUN + 1, boundary + RECOVERY_SEARCH)
    for start in range(boundary, stop):
        target = oracle_ids[start]
        if all(actions[t] == target for t in range(start, start + RECOVERY_RUN)):
            return start - boundary
    return None


def run_episode(seed: int, interval: int, opportunity_probability: float,
                policy: str, reward_uniforms, opportunity_uniforms) -> dict:
    method = "ucb1" if policy == "UCB1" else "sw_ucb"
    estimator = PairwiseBanditEstimator(N, K, method=method, window=WINDOW, xi=XI)
    executions = {pair: 0 for pair in PAIRS}
    observations = {pair: 0 for pair in PAIRS}
    opportunities = {pair: 0 for pair in PAIRS}
    by_regime = {"base": {pair: 0 for pair in PAIRS},
                 "transient": {pair: 0 for pair in PAIRS}}
    opportunities_by_regime = {"base": {pair: 0 for pair in PAIRS},
                               "transient": {pair: 0 for pair in PAIRS}}
    estimate_sq_error = {pair: 0.0 for pair in PAIRS}
    estimate_count = {pair: 0 for pair in PAIRS}
    age_sum = {pair: 0.0 for pair in PAIRS}
    age_count = {pair: 0 for pair in PAIRS}
    last_observation_period = {pair: None for pair in PAIRS}
    history_by_regime = {pair: {"base": 0, "transient": 0} for pair in PAIRS}
    recent_counts = {pair: 0 for pair in PAIRS}
    window_by_regime = {pair: {"base": deque(), "transient": deque()} for pair in PAIRS}
    information_sums = {pair: {name: 0.0 for name in (
        "recent", "compatible_full", "older_compatible_full",
        "compatible_retained", "incompatible_retained", "recent_retained")}
        for pair in PAIRS}
    boundaries = change_times(interval)
    boundary_set = set(boundaries)
    assignment_ids, observed_masks = [], []
    expected_rewards, realized_rewards, oracle_rewards, regrets, optimal_flags = [], [], [], [], []
    for period in range(HORIZON):
        interval_index = regime_index(period, interval)
        label = _regime_label(period, interval)
        if period in boundary_set:
            recent_counts = {pair: 0 for pair in PAIRS}
        matrix = matrix_at(period, interval)
        available_mask = opportunity_mask(opportunity_uniforms[period], opportunity_probability)
        for i, k in PAIRS:
            if available_mask & (1 << (i * K + k)):
                opportunities[(i, k)] += 1
                opportunities_by_regime[label][(i, k)] += 1
            for regime in ("base", "transient"):
                queue = window_by_regime[(i, k)][regime]
                while queue and queue[0] < period - WINDOW:
                    queue.popleft()
            if (i, k) == (2, 0):
                compatible_full = history_by_regime[(i, k)][label]
                compatible_retained = len(window_by_regime[(i, k)][label])
            else:
                compatible_full = sum(history_by_regime[(i, k)].values())
                compatible_retained = sum(len(queue) for queue in window_by_regime[(i, k)].values())
            retained = (sum(history_by_regime[(i, k)].values()) if method == "ucb1"
                        else sum(len(queue) for queue in window_by_regime[(i, k)].values()))
            information_sums[(i, k)]["recent"] += recent_counts[(i, k)]
            information_sums[(i, k)]["compatible_full"] += compatible_full
            information_sums[(i, k)]["older_compatible_full"] += max(
                0, compatible_full - recent_counts[(i, k)])
            information_sums[(i, k)]["compatible_retained"] += compatible_retained
            information_sums[(i, k)]["incompatible_retained"] += retained - compatible_retained
            information_sums[(i, k)]["recent_retained"] += min(
                recent_counts[(i, k)], retained)
        estimates = estimator.empirical_mean_matrix(period)
        for i, k in PAIRS:
            estimate_sq_error[(i, k)] += (estimates[i][k] - matrix[i][k]) ** 2
            estimate_count[(i, k)] += 1
            last_seen = last_observation_period[(i, k)]
            if last_seen is not None:
                age_sum[(i, k)] += period - last_seen
                age_count[(i, k)] += 1

        matching = calibration_matching(period) if period < CALIBRATION else exact_matching(estimator.score_matrix(period))
        matching = tuple(sorted(matching))
        assert len(matching) == N and len({i for i, _ in matching}) == N
        assert len({k for _, k in matching}) == K
        assignment_ids.append(matching_id(matching))
        oracle = oracle_matching(matrix)
        value = sum(matrix[i][k] for i, k in matching)
        oracle_value = sum(matrix[i][k] for i, k in oracle)
        realised = sum(float(reward_uniforms[period][i][k] < matrix[i][k])
                       for i, k in matching)
        expected_rewards.append(value)
        realized_rewards.append(realised)
        oracle_rewards.append(oracle_value)
        regrets.append(oracle_value - value)
        optimal_flags.append(float(matching == tuple(sorted(oracle))))

        feedback_edges, feedback = [], {}
        observed_mask = 0
        for i, k in matching:
            pair = (i, k)
            executions[pair] += 1
            bit = 1 << (i * K + k)
            if available_mask & bit:
                reward = float(reward_uniforms[period][i][k] < matrix[i][k])
                feedback_edges.append(pair)
                feedback[pair] = reward
                observed_mask |= bit
                observations[pair] += 1
                by_regime[label][pair] += 1
                last_observation_period[pair] = period
                history_by_regime[pair][label] += 1
                recent_counts[pair] += 1
                window_by_regime[pair][label].append(period)
        assert set(feedback_edges).issubset(set(matching))
        assert all(available_mask & (1 << (i * K + k)) for i, k in feedback_edges)
        assert math.isclose(regrets[-1], oracle_rewards[-1] - expected_rewards[-1], abs_tol=1e-12)
        observed_masks.append(observed_mask)
        # The estimator sees only executed edges whose feedback was available.
        estimator.update(period, feedback_edges, feedback)

    oracle_ids = [matching_id(oracle_matching(matrix_at(t, interval))) for t in range(HORIZON)]
    recovery = []
    for index, boundary in enumerate(boundaries):
        end = boundaries[index + 1] if index + 1 < len(boundaries) else HORIZON
        recovery.append(_recovery_lag(assignment_ids, oracle_ids, boundary, end))

    final_matrix = matrix_at(HORIZON - 1, interval)
    current_regime_start = boundaries[-1] if boundaries else 0
    pair_information = {}
    for pair in PAIRS:
        history = estimator.observations[pair]
        assert len(history) == observations[pair]
        compatible_total = sum(final_matrix[pair[0]][pair[1]] == matrix_at(obs.period, interval)[pair[0]][pair[1]]
                               for obs in history)
        retained = [obs for obs in history if method == "ucb1" or obs.period >= HORIZON - WINDOW]
        retained_compatible = sum(final_matrix[pair[0]][pair[1]] == matrix_at(obs.period, interval)[pair[0]][pair[1]]
                                  for obs in retained)
        current_regime_observations = sum(obs.period >= current_regime_start for obs in history)
        pair_information[f"{pair[0]},{pair[1]}"] = {
            "opportunities": opportunities[pair], "executions": executions[pair],
            "observations": observations[pair],
            "observation_per_opportunity": observations[pair] / opportunities[pair] if opportunities[pair] else None,
            "observation_per_execution": observations[pair] / executions[pair] if executions[pair] else None,
            "observations_by_competence_regime": {
                regime: by_regime[regime][pair] for regime in ("base", "transient")},
            "opportunities_by_competence_regime": {
                regime: opportunities_by_regime[regime][pair] for regime in ("base", "transient")},
            "mean_observations_from_current_regime_at_decision": information_sums[pair]["recent"] / HORIZON,
            "mean_compatible_observations_in_full_history_at_decision": information_sums[pair]["compatible_full"] / HORIZON,
            "mean_older_compatible_observations_at_decision": information_sums[pair]["older_compatible_full"] / HORIZON,
            "mean_compatible_observations_retained_at_decision": information_sums[pair]["compatible_retained"] / HORIZON,
            "mean_incompatible_observations_retained_at_decision": information_sums[pair]["incompatible_retained"] / HORIZON,
            "mean_current_regime_observations_retained_at_decision": information_sums[pair]["recent_retained"] / HORIZON,
            "observations_since_last_change_at_end": current_regime_observations,
            "compatible_observations_in_full_history_at_end": compatible_total,
            "observations_retained_by_estimator_at_end": len(retained),
            "compatible_observations_retained_at_end": retained_compatible,
            "incompatible_observations_retained_at_end": len(retained) - retained_compatible,
            "mean_age_at_decisions_when_previously_observed": age_sum[pair] / age_count[pair] if age_count[pair] else None,
            "mean_estimation_squared_error": estimate_sq_error[pair] / estimate_count[pair],
            "final_last_observation_age": HORIZON - 1 - history[-1].period if history else None,
        }

    per_regime = {}
    for label in ("base", "transient"):
        indices = [t for t in range(HORIZON) if _regime_label(t, interval) == label]
        per_regime[label] = {"expected_reward": sum(expected_rewards[t] for t in indices),
                             "expected_regret": sum(regrets[t] for t in indices),
                             "optimal_rate": statistics.fmean(optimal_flags[t] for t in indices)}
    mean_margins = {"base": 0.45, "transient": 0.05}
    assert sum(executions.values()) == N * HORIZON
    assert sum(observations.values()) == sum(len(estimator.observations[pair]) for pair in PAIRS)
    regime_blocks = {
        state: sum(_regime_label(t, interval) == state and (t == 0 or _regime_label(t - 1, interval) != state)
                   for t in range(HORIZON))
        for state in ("base", "transient")
    }
    return {
        "seed": seed, "interval": interval, "opportunity_probability": opportunity_probability,
        "policy": policy,
        "expected_reward": sum(expected_rewards), "realized_reward": sum(realized_rewards),
        "oracle_expected_reward": sum(oracle_rewards), "expected_regret": sum(regrets),
        "optimal_rate": statistics.fmean(optimal_flags),
        "assignment_changes": sum(a != b for a, b in zip(assignment_ids, assignment_ids[1:])),
        "regimes": per_regime, "recovery_lags": recovery,
        "opportunities_per_pair": {f"{i},{k}": opportunities[(i, k)] for i, k in PAIRS},
        "regime_blocks_by_competence_state": regime_blocks,
        "pair_information": pair_information,
        "expected_rho_opportunity_per_stability_interval": opportunity_probability * interval,
        "actual_matching_margins": mean_margins,
        "trace": {"assignment_id": assignment_ids, "observed_mask": observed_masks,
                  "expected_reward": expected_rewards, "realized_reward": realized_rewards,
                  "oracle_reward": oracle_rewards, "expected_regret": regrets,
                  "optimal": optimal_flags},
    }


def _ci(values):
    mean = statistics.fmean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    half = student_t.ppf(0.975, len(values) - 1) * sd / math.sqrt(len(values)) if len(values) > 1 else 0.0
    return {"n": len(values), "mean": mean, "sd": sd, "ci95": [mean - half, mean + half]}


def summarize(episodes: list[dict]) -> dict:
    cells = {}
    for interval_name, interval in CHANGE_INTERVALS.items():
        for availability_name, probability in OBSERVATION_PROBABILITIES.items():
            for policy in POLICIES:
                key = f"{interval_name}/{availability_name}/{policy}"
                rows = [row for row in episodes if row["interval"] == interval
                        and row["opportunity_probability"] == probability and row["policy"] == policy]
                metrics = ("expected_reward", "realized_reward", "oracle_expected_reward",
                           "expected_regret", "optimal_rate", "assignment_changes",
                           "expected_rho_opportunity_per_stability_interval")
                cells[key] = {metric: _ci([row[metric] for row in rows]) for metric in metrics}
                cells[key]["regimes"] = {
                    regime: {metric: _ci([row["regimes"][regime][metric] for row in rows])
                             for metric in ("expected_reward", "expected_regret", "optimal_rate")}
                    for regime in ("base", "transient")}
                cells[key]["pair_information"] = {
                    f"{i},{k}": {
                        field: _ci([row["pair_information"][f"{i},{k}"][field]
                                    for row in rows if row["pair_information"][f"{i},{k}"][field] is not None])
                        for field in ("opportunities", "executions", "observations",
                                      "observation_per_opportunity", "observation_per_execution",
                                      "mean_observations_from_current_regime_at_decision",
                                      "mean_compatible_observations_in_full_history_at_decision",
                                      "mean_older_compatible_observations_at_decision",
                                      "mean_compatible_observations_retained_at_decision",
                                      "mean_incompatible_observations_retained_at_decision",
                                      "mean_current_regime_observations_retained_at_decision",
                                      "observations_since_last_change_at_end",
                                      "compatible_observations_in_full_history_at_end",
                                      "observations_retained_by_estimator_at_end",
                                      "compatible_observations_retained_at_end",
                                      "incompatible_observations_retained_at_end",
                                      "mean_age_at_decisions_when_previously_observed",
                                      "mean_estimation_squared_error")
                    } for i, k in PAIRS}
                for i, k in PAIRS:
                    pair_key = f"{i},{k}"
                    cells[key]["pair_information"][pair_key]["opportunities_by_competence_regime"] = {
                        regime: _ci([row["pair_information"][pair_key]["opportunities_by_competence_regime"][regime]
                                     for row in rows]) for regime in ("base", "transient")}
                    cells[key]["pair_information"][pair_key]["observations_by_competence_regime"] = {
                        regime: _ci([row["pair_information"][pair_key]["observations_by_competence_regime"][regime]
                                     for row in rows]) for regime in ("base", "transient")}
                cells[key]["recovery_lag_summary"] = {
                    "mean_observed_lag": statistics.fmean(
                        lag for row in rows for lag in row["recovery_lags"] if lag is not None),
                    "not_recovered_within_regime_or_search_limit": sum(
                        lag is None for row in rows for lag in row["recovery_lags"]),
                    "event_count": sum(len(row["recovery_lags"]) for row in rows),
                }
                for i, k in PAIRS:
                    pair_key = f"{i},{k}"
                    cells[key]["pair_information"][pair_key]["mean_effective_observations_per_stability_interval"] = {
                        regime: _ci([
                            row["pair_information"][pair_key]["observations_by_competence_regime"][regime]
                            / (HORIZON // (2 * interval))
                            for row in rows
                        ]) for regime in ("base", "transient")
                    }

    paired = {}
    for interval_name, interval in CHANGE_INTERVALS.items():
        for availability_name, probability in OBSERVATION_PROBABILITIES.items():
            by_seed = {}
            for row in episodes:
                if row["interval"] == interval and row["opportunity_probability"] == probability:
                    by_seed.setdefault(row["seed"], {})[row["policy"]] = row
            for metric in ("expected_regret", "expected_reward", "optimal_rate"):
                paired[f"{interval_name}/{availability_name}/SW_minus_UCB/{metric}"] = _ci([
                    by_seed[seed]["SW-UCB"][metric] - by_seed[seed]["UCB1"][metric]
                    for seed in SEEDS
                ])

    lookup = {(row["interval"], row["opportunity_probability"], row["seed"], row["policy"]): row
              for row in episodes}
    def policy_contrast(interval, probability, seed):
        return {policy: lookup[(interval, probability, seed, policy)] for policy in POLICIES}

    for availability_name, probability in OBSERVATION_PROBABILITIES.items():
        for metric in ("expected_regret", "expected_reward", "optimal_rate"):
            paired[f"frequency_effect_on_SW_minus_UCB/{availability_name}/{metric}"] = _ci([
                (policy_contrast(CHANGE_INTERVALS["frequent"], probability, seed)["SW-UCB"][metric]
                 - policy_contrast(CHANGE_INTERVALS["frequent"], probability, seed)["UCB1"][metric])
                - (policy_contrast(CHANGE_INTERVALS["infrequent"], probability, seed)["SW-UCB"][metric]
                   - policy_contrast(CHANGE_INTERVALS["infrequent"], probability, seed)["UCB1"][metric])
                for seed in SEEDS])
    for interval_name, interval in CHANGE_INTERVALS.items():
        for policy in POLICIES:
            for metric in ("expected_regret", "expected_reward", "optimal_rate"):
                paired[f"availability_effect_low_minus_high/{interval_name}/{policy}/{metric}"] = _ci([
                    lookup[(interval, OBSERVATION_PROBABILITIES["low"], seed, policy)][metric]
                    - lookup[(interval, OBSERVATION_PROBABILITIES["high"], seed, policy)][metric]
                    for seed in SEEDS])
    for availability_name, probability in OBSERVATION_PROBABILITIES.items():
        for policy in POLICIES:
            for metric in ("expected_regret", "expected_reward", "optimal_rate"):
                paired[f"frequency_effect_frequent_minus_infrequent/{availability_name}/{policy}/{metric}"] = _ci([
                    lookup[(CHANGE_INTERVALS["frequent"], probability, seed, policy)][metric]
                    - lookup[(CHANGE_INTERVALS["infrequent"], probability, seed, policy)][metric]
                    for seed in SEEDS])
    for metric in ("expected_regret", "expected_reward", "optimal_rate"):
        paired[f"factorial_interaction_frequency_x_availability/{metric}"] = _ci([
            ((policy_contrast(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["high"], seed)["SW-UCB"][metric]
              - policy_contrast(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["high"], seed)["UCB1"][metric])
             - (policy_contrast(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["high"], seed)["SW-UCB"][metric]
                - policy_contrast(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["high"], seed)["UCB1"][metric]))
            - ((policy_contrast(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["low"], seed)["SW-UCB"][metric]
                - policy_contrast(CHANGE_INTERVALS["frequent"], OBSERVATION_PROBABILITIES["low"], seed)["UCB1"][metric])
               - (policy_contrast(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["low"], seed)["SW-UCB"][metric]
                  - policy_contrast(CHANGE_INTERVALS["infrequent"], OBSERVATION_PROBABILITIES["low"], seed)["UCB1"][metric]))
            for seed in SEEDS])
    return {"cells": cells, "paired_contrasts": paired}


def main() -> None:
    started = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    traces = gzip.open(TRACE_PATH, "wt", encoding="utf-8")
    episodes = []
    for seed in SEEDS:
        reward_uniforms, opportunity_uniforms = generate_randomness(seed)
        # The same base uniform mask is thresholded at p=.75/.25, so high and
        # low opportunities are nested and paired for every pair-period.
        for interval_name, interval in CHANGE_INTERVALS.items():
            for availability_name, probability in OBSERVATION_PROBABILITIES.items():
                for policy in POLICIES:
                    row = run_episode(seed, interval, probability, policy,
                                      reward_uniforms, opportunity_uniforms)
                    trace = row.pop("trace")
                    traces.write(json.dumps({"seed": seed, "change_frequency": interval_name,
                                             "observation_availability": availability_name,
                                             "policy": policy, **trace}, separators=(",", ":")) + "\n")
                    episodes.append(row)
    traces.close()
    summary = summarize(episodes)
    # Validate invariant oracle values across observation conditions.
    for interval in CHANGE_INTERVALS.values():
        for seed in SEEDS:
            rows = [row for row in episodes if row["seed"] == seed and row["interval"] == interval]
            oracle_values = {round(row["oracle_expected_reward"], 10) for row in rows}
            assert len(oracle_values) == 1
    result = {
        "experiment": "HLS-S3b changes x exogenous observation-opportunity factorial",
        "date": "2026-10-21",
        "design": {
            "agents": N, "tasks": K, "modality": "B2 full one-to-one matching (same feasible action set in all cells)",
            "horizon": HORIZON, "seeds": list(SEEDS),
            "competence_base": BASE, "competence_transient": TRANSIENT,
            "change_interval_by_level": CHANGE_INTERVALS,
            "schedule": "deterministic recurrent alternation base/transient; transitions at multiples of interval",
            "availability_probability_by_level": OBSERVATION_PROBABILITIES,
            "observation_rule": "for every pair-period, an exogenous shared uniform determines feedback availability; policy does not see masks before action; selected reward is observed iff its pair-period mask is available",
            "reward": "Bernoulli(c_ik(t)); realized reward contributes whether or not feedback is observed",
            "reward_stream": "random.Random(seed XOR 0xA17E5B), period-agent-task",
            "opportunity_stream": "random.Random(seed XOR 0x0B5E7A), period-agent-task; nested p=.25/.75 thresholds",
            "calibration": f"first {CALIBRATION} periods use the predeclared E1 three-matching cycle; counts in performance and are subject to same observation mask",
            "algorithms": {"UCB1": "PairwiseBanditEstimator; empirical mean + sqrt(2 log(max(2,t+1))/n)",
                           "SW-UCB": f"same estimator; period-global W={WINDOW}, xi={XI}; empirical window mean + sqrt(xi log(max(2,min(t+1,W))/n))"},
            "oracles": "exact maximum true-mean complete matching by six-permutation enumeration; independent of feedback availability",
            "stability_intervals": {"infrequent": 2_500, "frequent": 500},
            "rho_definition": "rho_opportunity = p_observe * stability_interval; not a performance law; effective observations are separately measured from executed-and-observed pairs",
            "lambda_rho_interpretation": "p_observe is the exogenous per-pair opportunity rate; lambda_effective_ik is estimated from observations actually obtained after execution, and rho_effective is its mean count per stability interval",
            "hypothesis_status": "the factorial levels were fixed before execution, but no directional rejection criterion was frozen before the campaign; directional hypothesis assessment is exploratory",
            "exploratory_directional_hypothesis": "frequent changes with high opportunity availability may improve SW-UCB relative to UCB1 more than frequent changes with low availability; assessed by the difference-in-differences of paired regret SW-UCB minus UCB1",
            "critical_pairs": [list(pair) for pair in CRITICAL_PAIRS],
            "matching_values_and_margins": {"base": {"optimum": 1.70, "margin_to_second": 0.45},
                                             "transient": {"optimum": 1.75, "margin_to_second": 0.05}},
        },
        "validation": {
            "same_feasible_actions_all_cells": True,
            "observation_masks_exogenous_and_hidden_before_action": True,
            "rewards_count_even_without_feedback": True,
            "oracle_independent_of_observation_probability": True,
            "only_selected_available_feedback_updates_estimators": True,
            "no_competence_information_passed_to_estimators": True,
        },
        "summary": summary, "episodes": episodes,
        "artifacts": {"period_traces": str(TRACE_PATH)},
        "runtime_seconds": time.perf_counter() - started,
    }
    SUMMARY_PATH.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({"summary": summary, "runtime_seconds": result["runtime_seconds"],
                      "artifacts": result["artifacts"]}, indent=2))


if __name__ == "__main__":
    main()
