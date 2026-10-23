#!/usr/bin/env python3
"""S3b: paired bandit-to-matching evaluation under exogenous drift."""

from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

from scipy.stats import t as student_t

from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.nonstationary_assignment import (
    PairObservation,
    PairwiseBanditEstimator,
    fixed_score_matrix_from_observations,
)

OUT = Path("results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json")
N = K = 3
HORIZON = 300
CALIBRATION_PERIODS = 9
EVAL_SEEDS = tuple(range(9300, 9330))
AGENTS = tuple(f"agent_{i}" for i in range(N))
TASKS = tuple(f"task_{k}" for k in range(K))
CALIBRATION_PERMUTATIONS = ((0, 1, 2), (1, 2, 0), (2, 0, 1))
POLICIES = ("UCB1_MATCHING", "SW_UCB_MATCHING", "RECENT_MEAN_MATCHING",
            "FIXED_LEARNED", "DYNAMIC_ORACLE")
ASSIGNER = HungarianAssignmentOptimizerNK()
ORG = OrganizationConfigNK(AGENTS, TASKS, ((0.5,) * K,) * N, (1.0,) * N, float(N))
PROBLEM = ProblemSpecNK("S3b-all-tasks", (1.0,) * K, float(N))

# Common amplitude [0.2, 0.8] in every condition. Only the regime schedule
# changes; each regime makes a different one-to-one assignment uniquely optimal.
CONDITIONS = {
    "S3b-0_stationary": {"switches": (), "shifts": (0,), "breakpoints": 0},
    "S3b-1_abrupt": {"switches": (150,), "shifts": (0, 1), "breakpoints": 1},
    "S3b-2_recurrent": {"switches": (60, 120, 180, 240),
                        "shifts": (0, 1, 2, 0, 1), "breakpoints": 4},
}


def window_for(condition: str) -> int:
    """Garivier–Moulines order choice, rounded, using known breakpoint bound."""
    changes = CONDITIONS[condition]["breakpoints"]
    if changes == 0:
        return HORIZON
    # Their bounded-reward recommendation is tau = 2 B sqrt(T log(T)/Upsilon_T).
    # Reward range is [0,1], so B=1. This is a protocol-informed setting,
    # not a learned estimate of future change times.
    return max(1, min(HORIZON, round(2.0 * math.sqrt(HORIZON * math.log(HORIZON) / changes))))


def regime_shift(condition: str, period: int) -> int:
    spec = CONDITIONS[condition]
    regime = sum(period >= boundary for boundary in spec["switches"])
    return spec["shifts"][regime]


def competence_matrix(condition: str, period: int) -> tuple[tuple[float, ...], ...]:
    shift = regime_shift(condition, period)
    return tuple(tuple(0.8 if k == (i + shift) % K else 0.2 for k in range(K))
                 for i in range(N))


def potential_uniforms(seed: int):
    rng = random.Random(seed ^ 0x5B3B)
    return tuple(tuple(tuple(rng.random() for _ in range(K)) for _ in range(N))
                 for _ in range(HORIZON))


def reward_matrix(means, uniforms):
    return tuple(tuple(float(uniforms[i][k] < means[i][k]) for k in range(K))
                 for i in range(N))


def matches_from_permutation(permutation):
    return tuple(sorted((permutation[k], k) for k in range(K)))


def permutation_id(matches):
    mapping = [None] * K
    for i, k in matches:
        mapping[k] = i
    # Base-4 encoding allows optional assignments: 0 means unassigned and
    # 1..N identify the assigned agent for that task.
    return sum((0 if agent is None else agent + 1) * (N + 1) ** task
               for task, agent in enumerate(mapping))


def matches_from_id(encoded: int):
    mapping = []
    for task in range(K):
        digit = (encoded // (N + 1) ** task) % (N + 1)
        if digit:
            mapping.append((digit - 1, task))
    return tuple(mapping)


def solve(scores):
    matches = ASSIGNER.optimize(scores, ORG, PROBLEM).matches
    if (len({i for i, _ in matches}) != len(matches)
            or len({k for _, k in matches}) != len(matches)):
        raise AssertionError("assignment violated one-to-one feasibility")
    return matches


def common_calibration(condition: str, uniforms):
    """Nine shared matchings expose every pair three times."""
    selected = []
    calibration_trace = []
    observations = {(i, k): [] for i in range(N) for k in range(K)}
    calibration_matchings = tuple(CALIBRATION_PERMUTATIONS[index % 3]
                                  for index in range(CALIBRATION_PERIODS))
    for period, permutation in enumerate(calibration_matchings):
        matches = matches_from_permutation(permutation)
        means = competence_matrix(condition, period)
        outcomes = reward_matrix(means, uniforms[period])
        feedback = {pair: outcomes[pair[0]][pair[1]] for pair in matches}
        selected.append(permutation_id(matches))
        calibration_trace.append({"period": period, "assignment_id": permutation_id(matches),
                                  "expected_reward": sum(means[i][k] for i, k in matches),
                                  "realized_reward": sum(feedback.values())})
        for pair, reward in feedback.items():
            observations[pair].append((period, reward))
    return selected, observations, calibration_trace


def _estimator(method, window, history):
    model = PairwiseBanditEstimator(N, K, method=method, window=window, xi=2.0)
    for period in range(CALIBRATION_PERIODS):
        matches = matches_from_permutation(CALIBRATION_PERMUTATIONS[period % 3])
        obs = {pair: observation.reward for pair, rows in history.items()
               for observation in rows if observation.period == period}
        model.update(period, matches, obs)
    return model


def evaluate(condition: str, seed: int):
    uniforms = potential_uniforms(seed)
    calibration_ids, raw_history, calibration_trace = common_calibration(condition, uniforms)
    history = {pair: tuple(PairObservation(t, r) for t, r in rows)
               for pair, rows in raw_history.items()}
    window = window_for(condition)
    models = {
        "UCB1_MATCHING": _estimator("ucb1", HORIZON, history),
        "SW_UCB_MATCHING": _estimator("sw_ucb", window, history),
        "RECENT_MEAN_MATCHING": _estimator("recent_mean", window, history),
    }
    fixed_scores = fixed_score_matrix_from_observations(N, K, history)
    fixed_matches = solve(fixed_scores)

    segment_records = {p: {} for p in POLICIES}
    records = {p: {"expected_reward": [], "realized_reward": [], "regret": [], "resource_use": [],
                   "assignment_ids": [], "optimal_match": [], "index_divergence": []}
               for p in POLICIES}
    boundaries = CONDITIONS[condition]["switches"]
    recovery = {p: [] for p in POLICIES if p != "DYNAMIC_ORACLE"}

    for period in range(CALIBRATION_PERIODS, HORIZON):
        means = competence_matrix(condition, period)
        outcomes = reward_matrix(means, uniforms[period])
        oracle_matches = solve(means)
        oracle_id = permutation_id(oracle_matches)
        oracle_value = sum(means[i][k] for i, k in oracle_matches)
        choices = {"FIXED_LEARNED": fixed_matches, "DYNAMIC_ORACLE": oracle_matches}
        mean_ids = {}
        for policy, model in models.items():
            choices[policy] = solve(model.score_matrix(period))
            mean_ids[policy] = permutation_id(solve(model.empirical_mean_matrix(period)))

        for policy, matches in choices.items():
            expected = sum(means[i][k] for i, k in matches)
            realized = sum(outcomes[i][k] for i, k in matches)
            expected_regret = oracle_value - expected
            if expected_regret < -1e-12:
                raise AssertionError("policy exceeded the expected-reward oracle")
            records[policy]["expected_reward"].append(expected)
            records[policy]["realized_reward"].append(realized)
            records[policy]["regret"].append(max(0.0, expected_regret))
            records[policy]["resource_use"].append(len(matches))
            segment = sum(period >= boundary for boundary in boundaries)
            segment_records[policy].setdefault(segment, {"expected_reward": [], "realized_reward": [], "regret": []})
            segment_records[policy][segment]["expected_reward"].append(expected)
            segment_records[policy][segment]["realized_reward"].append(realized)
            segment_records[policy][segment]["regret"].append(max(0.0, expected_regret))
            current_id = permutation_id(matches)
            records[policy]["assignment_ids"].append(current_id)
            records[policy]["optimal_match"].append(current_id == oracle_id)
            if policy in models:
                records[policy]["index_divergence"].append(current_id != mean_ids[policy])
        # Only selected outcomes enter a learning policy's history.
        for policy, model in models.items():
            matches = choices[policy]
            model.update(period, matches,
                         {(i, k): outcomes[i][k] for i, k in matches})

    for boundary in boundaries:
        for policy in recovery:
            ids = records[policy]["assignment_ids"]
            # Evaluation sequence begins at period 3; recovery is zero if it
            # already matches immediately after the change, otherwise the
            # number of periods until first exact optimal matching. Censor at
            # next change/end of horizon and report the censor explicitly.
            start = max(0, boundary - CALIBRATION_PERIODS)
            stop = min(HORIZON - CALIBRATION_PERIODS,
                       next((b - CALIBRATION_PERIODS for b in boundaries if b > boundary),
                            HORIZON - CALIBRATION_PERIODS))
            means_at = competence_matrix(condition, boundary)
            optimum_id = permutation_id(solve(means_at))
            lag = next((idx - start for idx in range(start, stop)
                        if ids[idx] == optimum_id), None)
            recovery[policy].append({"boundary_period": boundary,
                                     "lag_periods": lag,
                                     "censored_after": stop - start if lag is None else None})

    policy_output = {}
    for policy, values in records.items():
        policy_output[policy] = {
            "cumulative_expected_reward": sum(values["expected_reward"]),
            "cumulative_realized_reward": sum(values["realized_reward"]),
            "cumulative_expected_regret": sum(values["regret"]),
            "cumulative_resource_units": sum(values["resource_use"]),
            "mean_expected_regret_per_period": statistics.fmean(values["regret"]),
            "optimal_assignment_rate": statistics.fmean(values["optimal_match"]),
            "assignment_ids": values["assignment_ids"],
            "expected_reward_by_period": values["expected_reward"],
            "expected_regret_by_period": values["regret"],
        }
        if policy in models:
            policy_output[policy]["index_vs_mean_assignment_divergence_rate"] = statistics.fmean(
                values["index_divergence"])
            policy_output[policy]["observations_per_pair_at_end"] = [
                len(models[policy].observations[(i, k)]) for i in range(N) for k in range(K)
            ]
    return {
        "seed": seed,
        "window_periods": window,
        "calibration_assignment_ids": calibration_ids,
        "common_calibration_trace": calibration_trace,
        "fixed_mapping_id": permutation_id(fixed_matches),
        "policies": policy_output,
        "by_regime": {policy: {str(segment): {
            "periods": len(values["expected_reward"]),
            "expected_reward": sum(values["expected_reward"]),
            "realized_reward": sum(values["realized_reward"]),
            "expected_regret": sum(values["regret"]),
        } for segment, values in regimes.items()} for policy, regimes in segment_records.items()},
        "recovery": recovery,
    }


def confidence_interval(values):
    values = tuple(float(v) for v in values)
    mean = statistics.fmean(values)
    if len(values) < 2:
        return [mean, mean]
    half = float(student_t.ppf(0.975, len(values) - 1)) * statistics.stdev(values) / math.sqrt(len(values))
    return [mean - half, mean + half]


def run_experiment():
    conditions = {}
    for condition in CONDITIONS:
        episodes = [evaluate(condition, seed) for seed in EVAL_SEEDS]
        summaries = {}
        for policy in POLICIES:
            rows = [episode["policies"][policy] for episode in episodes]
            expected = [row["cumulative_expected_reward"] for row in rows]
            realized = [row["cumulative_realized_reward"] for row in rows]
            regret = [row["cumulative_expected_regret"] for row in rows]
            summaries[policy] = {
                "expected_reward_mean": statistics.fmean(expected),
                "expected_reward_sd": statistics.stdev(expected),
                "expected_reward_95ci": confidence_interval(expected),
                "realized_reward_mean": statistics.fmean(realized),
                "realized_reward_sd": statistics.stdev(realized),
                "resource_units_mean": statistics.fmean(row["cumulative_resource_units"] for row in rows),
                "expected_regret_mean": statistics.fmean(regret),
                "expected_regret_sd": statistics.stdev(regret),
                "expected_regret_95ci": confidence_interval(regret),
                "optimal_assignment_rate": statistics.fmean(row["optimal_assignment_rate"] for row in rows),
                "switch_frequency_per_297_periods": statistics.fmean(
                    sum(a != b for a, b in zip(row["assignment_ids"], row["assignment_ids"][1:]))
                    for row in rows),
                "expected_reward_mean_by_period": [statistics.fmean(
                    episode["policies"][policy]["expected_reward_by_period"][t] for episode in episodes)
                    for t in range(HORIZON - CALIBRATION_PERIODS)],
                "expected_regret_mean_by_period": [statistics.fmean(
                    episode["policies"][policy]["expected_regret_by_period"][t] for episode in episodes)
                    for t in range(HORIZON - CALIBRATION_PERIODS)],
            }
            if policy in ("UCB1_MATCHING", "SW_UCB_MATCHING", "RECENT_MEAN_MATCHING"):
                summaries[policy]["index_vs_mean_assignment_divergence_rate"] = statistics.fmean(
                    episode["policies"][policy]["index_vs_mean_assignment_divergence_rate"]
                    for episode in episodes)
        pair_differences = {}
        for policy in POLICIES[:-1]:
            diffs = [episodes[s]["policies"]["DYNAMIC_ORACLE"]["cumulative_expected_reward"]
                     - episodes[s]["policies"][policy]["cumulative_expected_reward"]
                     for s in range(len(episodes))]
            pair_differences[f"oracle_minus_{policy}"] = {
                "mean": statistics.fmean(diffs), "sd": statistics.stdev(diffs),
                "95ci": confidence_interval(diffs)}
        for left_index, left in enumerate(POLICIES[:-1]):
            for right in POLICIES[left_index + 1:]:
                diffs = [episodes[s]["policies"][left]["cumulative_expected_reward"]
                         - episodes[s]["policies"][right]["cumulative_expected_reward"]
                         for s in range(len(episodes))]
                pair_differences[f"{left}_minus_{right}"] = {
                    "mean": statistics.fmean(diffs), "sd": statistics.stdev(diffs),
                    "95ci": confidence_interval(diffs)}
        for episode in episodes:
            for policy in POLICIES:
                episode["policies"][policy].pop("expected_reward_by_period")
                episode["policies"][policy].pop("expected_regret_by_period")
        conditions[condition] = {
            "window_periods": window_for(condition),
            "regime_switch_periods": CONDITIONS[condition]["switches"],
            "unique_optimal_assignments_by_regime": [
                permutation_id(solve(tuple(tuple(0.8 if k == (i + shift) % K else 0.2
                                                   for k in range(K)) for i in range(N))))
                for shift in CONDITIONS[condition]["shifts"]],
            "summaries": summaries,
            "mean_by_regime": {
                policy: {
                    segment: {
                        metric: statistics.fmean(
                            episode["by_regime"][policy][segment][metric]
                            for episode in episodes)
                        for metric in ("expected_reward", "realized_reward", "expected_regret")
                    }
                    for segment in episodes[0]["by_regime"][policy]
                }
                for policy in POLICIES
            },
            "paired_policy_differences": pair_differences,
            "recovery_lags": {policy: [entry for episode in episodes
                                        for entry in episode["recovery"][policy]]
                              for policy in episodes[0]["recovery"]},
            "episodes": episodes,
        }
    return {
        "experiment": "HLS-S3b-nonstationary-unknown-pair-rewards",
        "protocol": {"agents": AGENTS, "tasks": TASKS, "horizon_periods_including_calibration": HORIZON,
                     "calibration_periods_common": CALIBRATION_PERIODS,
                     "calibration_observations_per_pair": CALIBRATION_PERIODS // 3,
                     "separate_calibration_seeds": "none; the forced common calibration is embedded in each evaluation trajectory",
                     "evaluation_periods": HORIZON - CALIBRATION_PERIODS,
                     "evaluation_seeds": EVAL_SEEDS,
                     "rewards": "pre-generated paired Bernoulli potential outcomes per pair-period; policies observe selected edges only",
                     "demand": "all three task types available once per period",
                     "competence_range": [0.2, 0.8], "amplitude": 0.6,
                     "reward_budget_per_period": 3,
                     "policy_information": "past selected pair rewards and current period; no true competence, unselected reward, or future regime",
                     "assignment_id_encoding": "base-4 integer sum(digit_k*4**k), digit 0=unassigned, digit i+1=agent_i assigned to task_k"},
        "methods": {
            "UCB1_MATCHING": "empirical mean + sqrt(2 log(t+1)/n); all-time per-pair history",
            "SW_UCB_MATCHING": "Garivier-Moulines window mean + sqrt(xi log(min(t+1,W))/n_window); global-period window; xi=2 to match UCB1 confidence scale; unseen-in-window pair gets finite optimistic sentinel",
            "RECENT_MEAN_MATCHING": "window empirical means only, no explicit confidence exploration bonus; unseen-in-window prior=0.5",
            "FIXED_LEARNED": "max-weight matching of common 9-period calibration means (three observations per pair), then frozen",
            "DYNAMIC_ORACLE": "max-weight matching on true current means; evaluator-only reference"},
        "window_selection": {condition: {"W": window_for(condition), "rule": "round(2*sqrt(T*log(T)/Upsilon_T)) when breakpoints known; W=T for stationary"}
                             for condition in CONDITIONS},
        "conditions": conditions,
        "limitations": [
            "Per-pair indices followed by simultaneous matching are an HLS multiple-play combinatorial adaptation, not the original single-play UCB regret setting.",
            "The nine-period common calibration is an explicit forced exploration prelude with three observations per pair; performance summaries exclude it, while its selected assignments and outcomes are logged separately.",
            "Fixed regime schedules and known breakpoint counts are synthetic protocol assumptions; policies do not observe true means or future switch times.",
            "Expected regret uses true means only in evaluator code; it is not fed to policies.",
        ],
    }


def main():
    result = run_experiment()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({condition: {policy: {
        "expected_reward_mean": summary["expected_reward_mean"],
        "expected_regret_mean": summary["expected_regret_mean"],
        "optimal_assignment_rate": summary["optimal_assignment_rate"],
    } for policy, summary in data["summaries"].items()}
        for condition, data in result["conditions"].items()}, indent=2))


if __name__ == "__main__":
    main()
