#!/usr/bin/env python3
"""Garivier–Moulines D-UCB reproduction and S3b matching adaptation."""

from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_long_horizon import (
    CALIBRATION_ASSIGNMENTS, CALIBRATION_PERIODS, CONDITIONS as HISTORICAL,
    EVAL_SEEDS as HISTORICAL_SEEDS, HORIZON as HISTORICAL_HORIZON,
    evaluate as historical_evaluate, means_at as historical_means, paired_uniforms,
    permutation_id, rewards_at as historical_rewards, solve as exact_matching,
    matches_from_permutation,
)
from hls.nonstationary_assignment import GarivierMoulinesPairwiseEstimator

OUT = Path("results/experiments/hls_s3b_discounted_ucb/results.json")
PAPER_HORIZON = 10_000
PAPER_BREAKPOINTS = (3_000, 5_000)
SEEDS = tuple(range(8100, 8150))
N = K = 3
XI = 0.5
B = 1.0
PAPER_GAMMA = 1.0 - 1.0 / (4.0 * math.sqrt(PAPER_HORIZON))
PAPER_WINDOW = round(4.0 * math.sqrt(PAPER_HORIZON * math.log(PAPER_HORIZON)))
PAPER_MEANS = tuple(
    (0.5, 0.3, 0.4 if t < 3_000 or t >= 5_000 else 0.9)
    for t in range(PAPER_HORIZON)
)
POLICIES = ("UCB1", "D_UCB", "SW_UCB")

# Predeclared heterogeneous 3x3 adaptation: one .4 edge temporarily rises to .9.
HLS_BASE = ((0.8, 0.05, 0.05), (0.05, 0.8, 0.05), (0.4, 0.05, 0.1))
HLS_TRANSIENT = ((0.8, 0.05, 0.05), (0.05, 0.8, 0.05), (0.9, 0.05, 0.1))
HLS_BREAKPOINTS = (3_000, 5_000)
HLS_SEEDS = tuple(range(8200, 8230))


def gamma_for(horizon: int) -> float:
    """Section 5 simulation choice: gamma = 1 - 1/(4 sqrt(T))."""
    return 1.0 - 1.0 / (4.0 * math.sqrt(horizon))


def window_for(horizon: int) -> int:
    """Section 5 SW-UCB choice: tau = 4 sqrt(T log T), clipped to T."""
    return min(horizon, max(1, round(4.0 * math.sqrt(horizon * math.log(horizon)))) )


def _paper_reward(t: int, arm: int) -> float:
    return PAPER_MEANS[t][arm]


def _block_means(values: list[float], *, offset: int = 0, block: int = 100):
    return [statistics.fmean(values[start - offset:min(start + block - offset, len(values))])
            for start in range(offset, offset + len(values), block)]


def _paired_contrast(episodes, left: str, right: str, metric: str,
                     nested: str = "policies"):
    return _ci([ep[nested][left][metric] - ep[nested][right][metric] for ep in episodes])


def _enumerate_hls_optimum(matrix):
    import itertools
    candidates = []
    for permutation in itertools.permutations(range(N)):
        matching = matches_from_permutation(permutation)
        value = sum(matrix[i][k] for i, k in matching)
        candidates.append((value, permutation_id(matching), matching))
    optimum = max(value for value, _, _ in candidates)
    winners = [(ident, matching) for value, ident, matching in candidates
               if math.isclose(value, optimum, rel_tol=0.0, abs_tol=1e-12)]
    return {"value": optimum, "unique": len(winners) == 1,
            "matching": [list(edge) for edge in winners[0][1]],
            "assignment_id": winners[0][0], "candidate_count": len(candidates)}


def run_bandit_seed(seed: int) -> dict:
    rng = random.Random(seed)
    potential = tuple(tuple(rng.random() for _ in range(3)) for _ in range(PAPER_HORIZON))
    estimators = {
        "UCB1": GarivierMoulinesPairwiseEstimator(3, 1, method="ucb1", xi=XI, reward_bound=B),
        "D_UCB": GarivierMoulinesPairwiseEstimator(
            3, 1, method="d_ucb", gamma=PAPER_GAMMA, xi=XI, reward_bound=B),
        "SW_UCB": GarivierMoulinesPairwiseEstimator(
            3, 1, method="sw_ucb", window=PAPER_WINDOW, xi=XI, reward_bound=B),
    }
    selected = {name: [] for name in POLICIES}
    rewards = {name: [] for name in POLICIES}
    regret = {name: [] for name in POLICIES}
    for t in range(PAPER_HORIZON):
        for name, model in estimators.items():
            if t < 3:
                arm = t  # Article Algorithm 1–3 initialization, one pull per arm.
            else:
                arm = max(range(3), key=lambda i: model.score_matrix(t)[i][0])
            outcome = float(potential[t][arm] < _paper_reward(t, arm))
            selected[name].append(arm)
            rewards[name].append(outcome)
            best_mean = max(PAPER_MEANS[t])
            regret[name].append(best_mean - _paper_reward(t, arm))
            model.update(t, ((arm, 0),), {(arm, 0): outcome})
    regimes = ((0, 3_000), (3_000, 5_000), (5_000, PAPER_HORIZON))
    policies = {}
    for name in POLICIES:
        arm_series = selected[name]
        policies[name] = {
            "cumulative_realized_reward": sum(rewards[name]),
            "cumulative_expected_reward": sum(
                _paper_reward(t, arm_series[t]) for t in range(PAPER_HORIZON)),
            "cumulative_expected_regret": sum(regret[name]),
            "optimal_action_rate": statistics.fmean(
                float(arm_series[t] == max(range(3), key=lambda i: PAPER_MEANS[t][i]))
                for t in range(PAPER_HORIZON)),
            "arm_selection_counts": [arm_series.count(i) for i in range(3)],
            "arm_1_selection_fraction_by_regime": [
                statistics.fmean(float(arm == 0) for arm in arm_series[start:end])
                for start, end in regimes],
            "expected_regret_by_regime": [sum(regret[name][start:end])
                                          for start, end in regimes],
            "expected_regret_mean_per_100_periods": _block_means(regret[name]),
            "first_optimal_action_lag_after_changes": [
                _first_optimal_lag(arm_series, boundary, optimal_arm)
                for boundary, optimal_arm in ((3_000, 2), (5_000, 0))],
            "sustained_optimal_recovery_lag_20_rounds": [
                _sustained_lag(arm_series, boundary, optimal_arm,
                               PAPER_BREAKPOINTS[index + 1] if index + 1 < len(PAPER_BREAKPOINTS)
                               else PAPER_HORIZON)
                for index, (boundary, optimal_arm) in enumerate(((3_000, 2), (5_000, 0)))],
        }
    return {"seed": seed, "policies": policies}


def _first_optimal_lag(actions, boundary: int, target_arm: int):
    return next((t - boundary for t in range(boundary, min(boundary + 1_000, len(actions)))
                 if actions[t] == target_arm), None)


def _sustained_lag(actions, boundary: int, target, regime_end: int, *,
                   run_length: int = 20, offset: int = 0):
    first = max(0, boundary - offset)
    last = min(len(actions) - run_length, regime_end - offset - run_length,
               boundary - offset + 1_000)
    if last < first:
        return None
    return next((start + offset - boundary
                 for start in range(first, last + 1)
                 if all(actions[t] == target for t in range(start, start + run_length))), None)


def _hls_matrix(period: int):
    if period < HLS_BREAKPOINTS[0] or period >= HLS_BREAKPOINTS[1]:
        return HLS_BASE
    return HLS_TRANSIENT


def _permutations():
    import itertools
    return tuple(matches_from_permutation(p) for p in itertools.permutations(range(N)))


def _hls_evaluate(seed: int) -> dict:
    rng = random.Random(seed ^ 0xD0C0A7)
    potentials = tuple(tuple(tuple(rng.random() for _ in range(K)) for _ in range(N))
                       for _ in range(PAPER_HORIZON))
    models = {
        "UCB1_MATCHING": GarivierMoulinesPairwiseEstimator(N, K, method="ucb1", xi=XI),
        "D_UCB_MATCHING": GarivierMoulinesPairwiseEstimator(
            N, K, method="d_ucb", gamma=PAPER_GAMMA, xi=XI),
        "SW_UCB_MATCHING": GarivierMoulinesPairwiseEstimator(
            N, K, method="sw_ucb", window=PAPER_WINDOW, xi=XI),
    }
    histories = {name: {"reward": [], "realized": [], "regret": [], "optimal": [], "assignments": []}
                 for name in models}
    regimes = {name: {} for name in models}
    matchings = _permutations()
    baseline_optimum = _enumerate_hls_optimum(HLS_BASE)
    transient_optimum = _enumerate_hls_optimum(HLS_TRANSIENT)
    if not baseline_optimum["unique"] or not transient_optimum["unique"]:
        raise AssertionError("the canonical HLS matrix must have unique exhaustive optima")
    for period in range(PAPER_HORIZON):
        means = _hls_matrix(period)
        oracle = exact_matching(means)
        oracle_id = permutation_id(oracle)
        oracle_reward = sum(means[i][k] for i, k in oracle)
        if oracle_id != (transient_optimum["assignment_id"] if HLS_BREAKPOINTS[0] <= period < HLS_BREAKPOINTS[1]
                         else baseline_optimum["assignment_id"]):
            raise AssertionError("solver disagrees with independent exhaustive matching")
        outcomes = tuple(tuple(float(potentials[period][i][k] < means[i][k]) for k in range(K))
                         for i in range(N))
        if period < CALIBRATION_PERIODS:
            chosen = matches_from_permutation((period % 3, (period + 1) % 3, (period + 2) % 3))
            choices = {name: chosen for name in models}
        else:
            choices = {name: exact_matching(model.score_matrix(period))
                       for name, model in models.items()}
        regime = ("baseline_before" if period < HLS_BREAKPOINTS[0] else
                  "transient" if period < HLS_BREAKPOINTS[1] else "baseline_after")
        for name, selected in choices.items():
            if period < CALIBRATION_PERIODS:
                continue
            expected = sum(means[i][k] for i, k in selected)
            realized = sum(outcomes[i][k] for i, k in selected)
            values = histories[name]
            values["reward"].append(expected)
            values["realized"].append(realized)
            values["regret"].append(oracle_reward - expected)
            values["optimal"].append(permutation_id(selected) == oracle_id)
            values["assignments"].append(permutation_id(selected))
            regimes[name].setdefault(regime, {"reward": [], "regret": [], "optimal": []})
            regimes[name][regime]["reward"].append(expected)
            regimes[name][regime]["regret"].append(oracle_reward - expected)
            regimes[name][regime]["optimal"].append(permutation_id(selected) == oracle_id)
        for name, model in models.items():
            selected = choices[name]
            model.update(period, selected,
                         {(i, k): outcomes[i][k] for i, k in selected})
    policy_out = {}
    boundaries = HLS_BREAKPOINTS
    for name, values in histories.items():
        policy_out[name] = {
            "cumulative_expected_reward": sum(values["reward"]),
            "cumulative_realized_reward": sum(values["realized"]),
            "cumulative_expected_regret": sum(values["regret"]),
            "optimal_matching_rate": statistics.fmean(values["optimal"]),
            "selection_counts_by_edge": {
                f"{i},{k}": sum((encoded // (N + 1) ** k) % (N + 1) == i + 1
                                 for encoded in values["assignments"])
                for i in range(N) for k in range(K)},
            "regime_summary": {
                regime: {"mean_expected_reward_per_period": statistics.fmean(v["reward"]),
                         "mean_expected_regret_per_period": statistics.fmean(v["regret"]),
                         "optimal_matching_rate": statistics.fmean(v["optimal"])}
                for regime, v in regimes[name].items()},
            "expected_regret_mean_per_100_periods": _block_means(
                values["regret"], offset=CALIBRATION_PERIODS),
            "first_optimal_matching_lag_after_changes": [
                _first_matching_lag(values["assignments"], b, permutation_id(
                    exact_matching(_hls_matrix(b)))) for b in boundaries],
            "sustained_optimal_matching_recovery_lag_20_rounds": [
                _sustained_lag(values["assignments"], b, permutation_id(
                    exact_matching(_hls_matrix(b))),
                    PAPER_BREAKPOINTS[index + 1] if index + 1 < len(HLS_BREAKPOINTS)
                    else PAPER_HORIZON, run_length=20, offset=CALIBRATION_PERIODS)
                for index, b in enumerate(HLS_BREAKPOINTS)],
        }
        policy_out[name].pop("assignment_ids", None)
    return {"seed": seed, "policies": policy_out,
            "enumerated_optima": {"baseline": baseline_optimum,
                                  "transient": transient_optimum},
            "oracle_expected_reward": (PAPER_HORIZON - CALIBRATION_PERIODS) * 1.7 + 2_000 * 0.05,
            "oracle_ids_by_regime": {"before": permutation_id(exact_matching(HLS_BASE)),
                                     "transient": permutation_id(exact_matching(HLS_TRANSIENT)),
                                     "after": permutation_id(exact_matching(HLS_BASE))}}


def _first_matching_lag(encoded_assignments, boundary, target_id):
    start = max(CALIBRATION_PERIODS, boundary)
    end = min(boundary + 1_000, PAPER_HORIZON)
    return next((t - boundary for t in range(start, end)
                 if encoded_assignments[t - CALIBRATION_PERIODS] == target_id), None)


def _historical_evaluate(condition: str, seed: int) -> dict:
    """Run D-UCB on the unchanged H=2400 historical S3b trajectory."""
    uniforms = paired_uniforms(seed)
    model = GarivierMoulinesPairwiseEstimator(
        N, K, method="d_ucb", gamma=gamma_for(HISTORICAL_HORIZON), xi=XI)
    # Replay common nine-period calibration exactly as the original campaign.
    for t, selected in enumerate(CALIBRATION_ASSIGNMENTS):
        means = historical_means(condition, t)
        outcomes = historical_rewards(means, uniforms[t])
        model.update(t, selected, {(i, k): outcomes[i][k] for i, k in selected})
    totals = {key: [] for key in ("expected", "realized", "regret", "optimal")}
    by_regime = {}
    assignments = []
    for t in range(CALIBRATION_PERIODS, HISTORICAL_HORIZON):
        means = historical_means(condition, t)
        outcomes = historical_rewards(means, uniforms[t])
        selected = exact_matching(model.score_matrix(t))
        oracle = exact_matching(means)
        oracle_value = sum(means[i][k] for i, k in oracle)
        value = sum(means[i][k] for i, k in selected)
        realized = sum(outcomes[i][k] for i, k in selected)
        totals["expected"].append(value)
        totals["realized"].append(realized)
        totals["regret"].append(oracle_value - value)
        totals["optimal"].append(permutation_id(selected) == permutation_id(oracle))
        assignments.append(permutation_id(selected))
        regime = sum(t >= b for b in HISTORICAL[condition]["switches"])
        by_regime.setdefault(str(regime), {"expected": [], "regret": [], "optimal": []})
        by_regime[str(regime)]["expected"].append(value)
        by_regime[str(regime)]["regret"].append(oracle_value - value)
        by_regime[str(regime)]["optimal"].append(totals["optimal"][-1])
        model.update(t, selected, {(i, k): outcomes[i][k] for i, k in selected})
    return {"seed": seed,
            "cumulative_expected_reward": sum(totals["expected"]),
            "cumulative_realized_reward": sum(totals["realized"]),
            "cumulative_expected_regret": sum(totals["regret"]),
            "optimal_matching_rate": statistics.fmean(totals["optimal"]),
            "regime_summary": {r: {"mean_expected_reward": statistics.fmean(v["expected"]),
                                    "mean_expected_regret": statistics.fmean(v["regret"]),
                                    "optimal_assignment_rate": statistics.fmean(v["optimal"])}
                               for r, v in by_regime.items()},
            "gamma": gamma_for(HISTORICAL_HORIZON)}


def _ci(values):
    values = tuple(float(value) for value in values)
    mean = statistics.fmean(values)
    if len(values) < 2:
        return {"mean": mean, "sd": 0.0, "ci95": [mean, mean]}
    sd = statistics.stdev(values)
    half = student_t.ppf(0.975, len(values) - 1) * sd / math.sqrt(len(values))
    return {"mean": mean, "sd": sd, "ci95": [mean - half, mean + half]}


def _summary(episodes, policies):
    result = {}
    for policy in policies:
        sample = episodes[0]["policies"][policy]
        optimal_field = ("optimal_matching_rate" if "optimal_matching_rate" in sample
                         else "optimal_action_rate")
        result[policy] = {key: _ci([ep["policies"][policy][field] for ep in episodes])
                          for key, field in (("expected_reward", "cumulative_expected_reward"),
                                             ("expected_regret", "cumulative_expected_regret"),
                                             ("realized_reward", "cumulative_realized_reward"),
                                             ("optimal_rate", optimal_field))}
    return result


def _contrasts(episodes, policies, metric):
    return {f"{left}_minus_{right}": _paired_contrast(episodes, left, right, metric)
            for left, right in ((policies[1], policies[0]),
                                (policies[2], policies[0]),
                                (policies[1], policies[2]))}


def run():
    bandit = [run_bandit_seed(seed) for seed in SEEDS]
    hls = [_hls_evaluate(seed) for seed in HLS_SEEDS]
    historical = {}
    old_path = Path("results/experiments/hls_s3b_long_horizon/results.json")
    original = json.loads(old_path.read_text(encoding="utf-8"))
    for condition in HISTORICAL:
        episodes = [_historical_evaluate(condition, seed) for seed in HISTORICAL_SEEDS]
        old_eps = {row["seed"]: row for row in original["conditions"][condition]["episodes"]}
        # Strict paired replay check against the exact historical common stream.
        check_seed = HISTORICAL_SEEDS[0]
        rerun = historical_evaluate(condition, check_seed)
        reference = old_eps[check_seed]
        replay_checks = {}
        for policy in ("UCB1_MATCHING", "SW_UCB_MATCHING", "GLR_CUCB"):
            actual_record = rerun["policies"][policy]
            reference_record = reference["policies"][policy]
            assert math.isclose(actual_record["cumulative_expected_reward"],
                                reference_record["cumulative_expected_reward"],
                                rel_tol=0.0, abs_tol=1e-12)
            replay_checks[policy] = "exact cumulative expected-reward replay on seed 9300; compact historical artifact omits assignment traces"
        historical[condition] = {
            "configuration": {"horizon": HISTORICAL_HORIZON,
                              "breakpoints": list(HISTORICAL[condition]["switches"]),
                              "regime_shifts": list(HISTORICAL[condition]["shifts"]),
                              "gamma": gamma_for(HISTORICAL_HORIZON), "xi": XI},
            "discounted_ucb_summary": {
                key: _ci([ep[field] for ep in episodes])
                for key, field in (("expected_reward", "cumulative_expected_reward"),
                                   ("expected_regret", "cumulative_expected_regret"),
                                   ("realized_reward", "cumulative_realized_reward"),
                                   ("optimal_rate", "optimal_matching_rate"))},
            "existing_comparator_summaries": original["conditions"][condition]["summary"]["policies"],
            "paired_expected_reward_differences_vs_existing_results": {
                policy: _ci([ep["cumulative_expected_reward"]
                             - old_eps[ep["seed"]]["policies"][policy]["cumulative_expected_reward"]
                             for ep in episodes])
                for policy in ("UCB1_MATCHING", "SW_UCB_MATCHING", "GLR_CUCB")},
            "episodes": episodes,
            "reproduction_note": replay_checks,
        }

    result = {
        "experiment": "HLS-S3b-Garivier-Moulines-discounted-UCB",
        "date": "2026-10-21",
        "reference": {"citation": "Garivier & Moulines (2008), On Upper-Confidence Bound Policies for Non-Stationary Bandit Problems",
                      "url": "https://arxiv.org/abs/0805.3415",
                      "paper_experiment": {"arms": 3, "horizon": PAPER_HORIZON,
                          "breakpoints": list(PAPER_BREAKPOINTS),
                          "means": {"arm1": 0.5, "arm2": 0.3,
                                    "arm3": {"outside": 0.4, "during": 0.9}},
                          "parameters": {"xi": XI, "B": B,
                              "gamma": PAPER_GAMMA, "window_tau": PAPER_WINDOW,
                              "window_expression": "4*sqrt(T*log(T))"},
                          "original_comparators": ["UCB-1", "EXP3.S", "D-UCB", "SW-UCB"],
                          "reproduced_comparators": list(POLICIES),
                          "replicate_count_in_article": "not specified in the article text/figure"},
                      "parameter_note": "Section 5 simulation xi=1/2; paper theorems assume xi>1/2. Section 5 uses gamma=1-1/(4 sqrt(T)) for D-UCB. Its SW-UCB window is tau=4 sqrt(T log T)."},
        "reproduction": {"seeds": list(SEEDS), "summary": _summary(bandit, POLICIES),
                         "paired_expected_regret_differences": _contrasts(
                             bandit, POLICIES, "cumulative_expected_regret"),
                         "episodes": bandit},
        "hls_inspired_3x3": {"horizon": PAPER_HORIZON, "seeds": list(HLS_SEEDS),
             "breakpoints": list(HLS_BREAKPOINTS),
             "competence_before_and_after": [list(row) for row in HLS_BASE],
             "competence_during_transient": [list(row) for row in HLS_TRANSIENT],
             "gamma": PAPER_GAMMA, "window": PAPER_WINDOW, "xi": XI,
             "matching_optima": {"baseline": permutation_id(exact_matching(HLS_BASE)),
                                 "transient": permutation_id(exact_matching(HLS_TRANSIENT))},
             "summary": _summary(hls, ("UCB1_MATCHING", "D_UCB_MATCHING", "SW_UCB_MATCHING")),
             "paired_expected_regret_differences": _contrasts(
                 hls, ("UCB1_MATCHING", "D_UCB_MATCHING", "SW_UCB_MATCHING"),
                 "cumulative_expected_regret"),
             "episodes": hls},
        "historical_s3b": historical,
        "limitations": [
            "The article's EXP3.S comparator is not reimplemented; this is a reproduction of its UCB-family comparison, not every curve in Figure 1.",
            "The paper does not provide random seeds or a stated Monte Carlo replicate count, so numerical equality is not expected.",
            "D-UCB+matching applies per-edge indices to a multiple-play assignment oracle; single-play regret guarantees do not automatically transfer.",
            "Historical UCB1/SW-UCB baselines retain their pre-existing HLS parameters (xi=2); comparisons to D-UCB are descriptive and not parameter-matched.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"paper": result["reproduction"]["summary"],
                      "hls": result["hls_inspired_3x3"]["summary"],
                      "historical_d_ucb": {k: v["discounted_ucb_summary"]
                                           for k, v in historical.items()}}, indent=2))


if __name__ == "__main__":
    run()
