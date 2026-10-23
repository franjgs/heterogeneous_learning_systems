#!/usr/bin/env python3
"""Predeclared long-horizon S3b comparison (H=2400, paired seeds)."""

from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_nonstationary_unknown_assignment import (
    CALIBRATION_PERIODS, CALIBRATION_PERMUTATIONS, K, N, _estimator,
    matches_from_id, matches_from_permutation, permutation_id, solve,
)
from hls.glr_cucb import GLRCUCB
from hls.nonstationary_assignment import PairObservation, PairwiseBanditEstimator


OUT = Path("results/experiments/hls_s3b_long_horizon/results.json")
HORIZON = 2400
EVAL_SEEDS = tuple(range(9300, 9330))
AGENT_COUNT = N * K
POLICIES = ("UCB1_MATCHING", "SW_UCB_MATCHING", "GLR_CUCB")
BASE_ARMS = N * K
CALIBRATION_ASSIGNMENTS = tuple(
    matches_from_permutation(CALIBRATION_PERMUTATIONS[t % 3])
    for t in range(CALIBRATION_PERIODS)
)

# Frozen before evaluation. Time is an abstract operating cycle, not a claim
# about a measured industrial duration. Regimes preserve the original .2/.8
# matrices and cyclic specialization shifts; only the requested schedule changes.
CONDITIONS = {
    "S3b-L0_stationary": {"switches": (), "shifts": (0,), "breakpoints": 0},
    "S3b-L1_abrupt": {"switches": (1200,), "shifts": (0, 1), "breakpoints": 1},
    "S3b-L2_recurrent": {
        "switches": (600, 1200, 1800), "shifts": (0, 1, 2, 0), "breakpoints": 3,
    },
}


def sw_window(condition: str) -> int:
    """Predeclared Garivier–Moulines order choice, B=1 and known change count."""
    m = CONDITIONS[condition]["breakpoints"]
    if m == 0:
        return HORIZON
    return max(1, min(HORIZON, round(2.0 * math.sqrt(HORIZON * math.log(HORIZON) / m))))


def glr_parameters() -> dict:
    """Theorem-derived unknown-segment-count setting; common to all regimes.

    Zhou et al. Corollary 4.3 uses delta=1/T and
    p=sqrt(K log(T)/T) when the number of segments is unknown. K here is the
    number of base arms (nine agent-task pairs), not agent or task count.
    This avoids giving the policy the scenario's change count or locations.
    """
    return {
        "epsilon_uniform_exploration": math.sqrt(BASE_ARMS * math.log(HORIZON) / HORIZON),
        "delta_glr": 1.0 / HORIZON,
        "base_arm_count": BASE_ARMS,
        "segment_count_assumption": "unknown; same theorem-derived setting in all conditions",
        "confidence_index": "mean + sqrt(3 log(t-tau)/(2 n))",
        "threshold": "paper beta(n,delta), implementation's cited conservative Q upper bound",
        "restart": "global after any pair detector signals",
    }


def shift_at(condition: str, period: int) -> int:
    spec = CONDITIONS[condition]
    return spec["shifts"][sum(period >= b for b in spec["switches"])]


def means_at(condition: str, period: int) -> tuple[tuple[float, ...], ...]:
    shift = shift_at(condition, period)
    return tuple(tuple(0.8 if k == (i + shift) % K else 0.2 for k in range(K))
                 for i in range(N))


def paired_uniforms(seed: int):
    """Same RNG stream/edge order as original S3b, extended to H=2400."""
    rng = random.Random(seed ^ 0x5B3B)
    return tuple(tuple(tuple(rng.random() for _ in range(K)) for _ in range(N))
                 for _ in range(HORIZON))


def rewards_at(means, uniforms):
    return tuple(tuple(float(uniforms[i][k] < means[i][k]) for k in range(K))
                 for i in range(N))


def initial_history(condition: str, uniforms):
    history = {(i, k): [] for i in range(N) for k in range(K)}
    calibration_ids = []
    for t, selected in enumerate(CALIBRATION_ASSIGNMENTS):
        means = means_at(condition, t)
        outcomes = rewards_at(means, uniforms[t])
        calibration_ids.append(permutation_id(selected))
        for i, k in selected:
            history[(i, k)].append(PairObservation(t, outcomes[i][k]))
    return history, calibration_ids


def _new_model(policy: str, condition: str, seed: int, history):
    hist = {pair: tuple(rows) for pair, rows in history.items()}
    if policy == "UCB1_MATCHING":
        return _estimator("ucb1", HORIZON, hist)
    if policy == "SW_UCB_MATCHING":
        return _estimator("sw_ucb", sw_window(condition), hist)
    h = {pair: tuple((o.period, o.reward) for o in rows) for pair, rows in history.items()}
    params = glr_parameters()
    return GLRCUCB(N, K, horizon=HORIZON,
                   epsilon=params["epsilon_uniform_exploration"],
                   delta=params["delta_glr"], seed=seed + 17000,
                   initial_history=h)


def _regime_index(condition: str, t: int) -> int:
    return sum(t >= b for b in CONDITIONS[condition]["switches"])


def evaluate(condition: str, seed: int):
    uniforms = paired_uniforms(seed)
    history, calibration_ids = initial_history(condition, uniforms)
    models = {policy: _new_model(policy, condition, seed, history) for policy in POLICIES}
    rows = {policy: {key: [] for key in ("expected", "realized", "regret", "ids", "optimal", "forced")}
            for policy in POLICIES}
    regimes = {policy: defaultdict(lambda: {key: [] for key in ("expected", "regret", "optimal")})
               for policy in POLICIES}
    for t in range(CALIBRATION_PERIODS, HORIZON):
        means = means_at(condition, t)
        outcomes = rewards_at(means, uniforms[t])
        oracle = solve(means)
        oracle_id = permutation_id(oracle)
        oracle_value = sum(means[i][k] for i, k in oracle)
        selected_by_policy = {}
        for policy, model in models.items():
            forced_arm = model.forced_arm(t) if policy == "GLR_CUCB" else None
            selected = (model.forced_matching(forced_arm, _all_perfect_matchings())
                        if forced_arm is not None else solve(model.score_matrix(t)))
            selected_by_policy[policy] = selected
            ident = permutation_id(selected)
            expected = sum(means[i][k] for i, k in selected)
            realized = sum(outcomes[i][k] for i, k in selected)
            regret = oracle_value - expected
            if regret < -1e-12:
                raise AssertionError("policy exceeded expected-reward oracle")
            r = rows[policy]
            r["expected"].append(expected)
            r["realized"].append(realized)
            r["regret"].append(max(0.0, regret))
            r["ids"].append(ident)
            r["optimal"].append(ident == oracle_id)
            r["forced"].append(forced_arm is not None)
            s = regimes[policy][_regime_index(condition, t)]
            s["expected"].append(expected)
            s["regret"].append(max(0.0, regret))
            s["optimal"].append(ident == oracle_id)
        for policy, model in models.items():
            selected = selected_by_policy[policy]
            model.update(t, selected, {(i, k): outcomes[i][k] for i, k in selected})

    policy_records = {}
    for policy, values in rows.items():
        policy_records[policy] = {
            "cumulative_expected_reward": sum(values["expected"]),
            "cumulative_realized_reward": sum(values["realized"]),
            "cumulative_expected_regret": sum(values["regret"]),
            "optimal_assignment_rate": statistics.fmean(values["optimal"]),
            "resource_units": (HORIZON - CALIBRATION_PERIODS) * N,
            "expected_reward_by_period": values["expected"],
            "expected_regret_by_period": values["regret"],
            "assignment_ids": values["ids"],
            "regime_summary": {
                str(regime): {"periods": len(v["expected"]),
                              "mean_expected_reward": statistics.fmean(v["expected"]),
                              "mean_expected_regret": statistics.fmean(v["regret"]),
                              "optimal_assignment_rate": statistics.fmean(v["optimal"])}
                for regime, v in regimes[policy].items()
            },
        }
        if policy == "GLR_CUCB":
            forced = values["forced"]
            dets = models[policy].detections
            policy_records[policy].update({
                "forced_exploration_periods": sum(forced),
                "forced_exploration_rate": statistics.fmean(forced),
                "expected_regret_on_forced_periods": sum(
                    regret for regret, is_forced in zip(values["regret"], forced) if is_forced),
                "detections": dets,
                "detection_count": len(dets),
                "observations_per_pair_at_end": [len(models[policy]._samples[i, k])
                                                  for i in range(N) for k in range(K)],
            })
    return {"seed": seed, "calibration_assignment_ids": calibration_ids,
            "window_periods": sw_window(condition), "policies": policy_records}


_MATCHINGS = None


def _all_perfect_matchings():
    global _MATCHINGS
    if _MATCHINGS is None:
        import itertools
        _MATCHINGS = tuple(matches_from_permutation(p) for p in itertools.permutations(range(N)))
    return _MATCHINGS


def ci(values):
    xs = tuple(float(x) for x in values)
    mean = statistics.fmean(xs)
    sd = statistics.stdev(xs)
    half = student_t.ppf(0.975, len(xs) - 1) * sd / math.sqrt(len(xs))
    return {"mean": mean, "sd": sd, "ci95": [mean - half, mean + half]}


def summarize(episodes):
    policies_out = {}
    for policy in POLICIES:
        items = [episode["policies"][policy] for episode in episodes]
        policies_out[policy] = {
            "expected_reward": ci([x["cumulative_expected_reward"] for x in items]),
            "expected_regret": ci([x["cumulative_expected_regret"] for x in items]),
            "realized_reward": ci([x["cumulative_realized_reward"] for x in items]),
            "optimal_assignment_rate": ci([x["optimal_assignment_rate"] for x in items]),
        }
        if policy == "GLR_CUCB":
            for key in ("detection_count", "forced_exploration_periods",
                        "expected_regret_on_forced_periods"):
                policies_out[policy][key] = ci([x[key] for x in items])
    paired = {}
    for a, b in (("GLR_CUCB", "UCB1_MATCHING"), ("GLR_CUCB", "SW_UCB_MATCHING"),
                 ("SW_UCB_MATCHING", "UCB1_MATCHING")):
        paired[f"{a}_minus_{b}_expected_reward"] = ci([
            ep["policies"][a]["cumulative_expected_reward"] -
            ep["policies"][b]["cumulative_expected_reward"] for ep in episodes])
        paired[f"{a}_minus_{b}_expected_regret"] = ci([
            ep["policies"][a]["cumulative_expected_regret"] -
            ep["policies"][b]["cumulative_expected_regret"] for ep in episodes])
    # Across-seed mean regret trajectory, compactly retained for temporal inspection.
    trajectory = {p: [statistics.fmean(ep["policies"][p]["expected_regret_by_period"][t]
                                      for ep in episodes)
                      for t in range(HORIZON - CALIBRATION_PERIODS)] for p in POLICIES}
    return {"policies": policies_out, "paired_differences": paired,
            "mean_expected_regret_by_evaluation_period": trajectory}


def summarize_regimes(episodes):
    output = {}
    for policy in POLICIES:
        regime_ids = sorted({regime for ep in episodes
                             for regime in ep["policies"][policy]["regime_summary"]}, key=int)
        output[policy] = {}
        for regime in regime_ids:
            stats = [ep["policies"][policy]["regime_summary"][regime] for ep in episodes]
            output[policy][regime] = {
                "periods_per_seed": stats[0]["periods"],
                "mean_expected_reward_per_period": ci([x["mean_expected_reward"] for x in stats]),
                "mean_expected_regret_per_period": ci([x["mean_expected_regret"] for x in stats]),
                "optimal_assignment_rate": ci([x["optimal_assignment_rate"] for x in stats]),
            }
    return output


def compact_episode(episode):
    """Retain seed-level evidence, not repeated full-period arrays."""
    compact = {"seed": episode["seed"], "policies": {}}
    for policy, record in episode["policies"].items():
        compact["policies"][policy] = {
            key: value for key, value in record.items()
            if key not in {"expected_reward_by_period", "expected_regret_by_period", "assignment_ids"}
        }
        if policy == "GLR_CUCB":
            compact["policies"][policy]["detections"] = [
                {key: event[key] for key in ("period", "arms", "statistics", "thresholds", "samples")}
                for event in record["detections"]]
    return compact


def analyze_detections(condition: str, episodes):
    boundaries = CONDITIONS[condition]["switches"]
    events = [(ep["seed"], event) for ep in episodes
              for event in ep["policies"]["GLR_CUCB"]["detections"]]
    matched = []
    for boundary in boundaries:
        end = next((b for b in boundaries if b > boundary), HORIZON)
        per_seed = []
        for ep in episodes:
            event = next((event for event in ep["policies"]["GLR_CUCB"]["detections"]
                          if boundary <= event["period"] < end), None)
            per_seed.append(None if event is None else event["period"] - boundary)
        delays = [d for d in per_seed if d is not None]
        matched.append({"change_period": boundary, "seed_detections": len(delays),
                        "seeds": len(episodes),
                        "detection_rate": len(delays) / len(episodes),
                        "mean_delay_conditional_on_detection": statistics.fmean(delays) if delays else None,
                        "undetected_seeds": len(episodes) - len(delays)})
    return {"alarm_events_total": len(events), "alarms_per_seed": len(events) / len(episodes),
            "changes": matched,
            "stationary_false_alarm_seeds": (sum(bool(ep["policies"]["GLR_CUCB"]["detections"])
                                                   for ep in episodes) if not boundaries else None),
            "post_detection_assignment_change": _post_detection_assignment_change(condition, episodes)}


def _post_detection_assignment_change(condition, episodes):
    observations = []
    lags = (0, 1, 5, 10, 25, 50)
    for ep in episodes:
        ids = ep["policies"]["GLR_CUCB"]["assignment_ids"]
        for event in ep["policies"]["GLR_CUCB"]["detections"]:
            # The assignment at period d+1 is the first policy decision after its reset.
            idx = event["period"] + 1 - CALIBRATION_PERIODS
            if 0 <= idx < len(ids):
                prior = ids[idx - 1] if idx else ep["calibration_assignment_ids"][-1]
                next_change = next((b for b in CONDITIONS[condition]["switches"]
                                    if b > event["period"]), HORIZON)
                optimal_at_lag = {}
                for lag in lags:
                    decision_period = event["period"] + 1 + lag
                    decision_idx = decision_period - CALIBRATION_PERIODS
                    if decision_period < next_change and decision_idx < len(ids):
                        optimal_id = permutation_id(solve(means_at(condition, decision_period)))
                        optimal_at_lag[str(lag)] = ids[decision_idx] == optimal_id
                observations.append({"changed": ids[idx] != prior,
                                     "assignment_id_after": ids[idx],
                                     "period_after_detection": event["period"] + 1,
                                     "optimal_at_lags": optimal_at_lag,
                                     "optimal_within_1": any(optimal_at_lag.get(str(lag), False)
                                                              for lag in (0, 1)),
                                     "optimal_within_10": any(optimal_at_lag.get(str(lag), False)
                                                               for lag in (0, 1, 5, 10)),
                                     "optimal_within_50": any(optimal_at_lag.get(str(lag), False)
                                                               for lag in lags)} )
    return {"events_with_following_decision": len(observations),
            "fraction_followed_by_assignment_change": (statistics.fmean(x["changed"] for x in observations)
                                                        if observations else None),
            "fraction_optimal_at_lag": {
                str(lag): (statistics.fmean(x["optimal_at_lags"][str(lag)] for x in observations
                                           if str(lag) in x["optimal_at_lags"])
                           if any(str(lag) in x["optimal_at_lags"] for x in observations) else None)
                for lag in lags},
            "fraction_reaching_optimal_matching_within": {
                str(lag): (statistics.fmean(x[key] for x in observations) if observations else None)
                for lag, key in ((1, "optimal_within_1"), (10, "optimal_within_10"),
                                 (50, "optimal_within_50"))},
            "events": observations}


def run():
    scenarios = {}
    for condition in CONDITIONS:
        episodes = [evaluate(condition, seed) for seed in EVAL_SEEDS]
        summaries = summarize(episodes)
        detection_summary = analyze_detections(condition, episodes)
        detection_summary["post_detection_assignment_change"].pop("events", None)
        scenarios[condition] = {
            "configuration": {"breakpoints": list(CONDITIONS[condition]["switches"]),
                              "regime_shifts": list(CONDITIONS[condition]["shifts"]),
                              "sw_window_periods": sw_window(condition)},
            "summary": summaries,
            "regime_summaries": summarize_regimes(episodes),
            "glr_diagnostics": detection_summary,
            "episodes": [compact_episode(episode) for episode in episodes],
        }
    params = glr_parameters()
    result = {
        "experiment": "HLS-S3b-long-horizon-organizational-evaluation",
        "pre_evaluation_protocol": "locked in runner before evaluation; no test-seed tuning",
        "date": "2026-10-21",
        "protocol": {"agents": N, "tasks": K, "base_arms": BASE_ARMS,
                     "horizon_total_including_calibration": HORIZON,
                     "abstract_cycle_interpretation": True,
                     "calibration_periods_common": CALIBRATION_PERIODS,
                     "evaluation_periods": HORIZON - CALIBRATION_PERIODS,
                     "seeds": list(EVAL_SEEDS), "paired_potential_rewards": True,
                     "reward_model": "independent Bernoulli(c[i,k,t]); potential uniforms common by seed/time/edge",
                     "feedback": "only selected matching edges",
                     "capacity": "one edge per agent and task; exact assignment solver",
                     "policy_information": "public task/agent identities, clock and own selected-edge feedback only; no true means or breakpoints",
                     "original_rng_stream": "same seed xor 0x5B3B and edge draw order as original, extended from 300 to 2400",
                     "policies": list(POLICIES),
                     "sw_ucb": {"rule": "W=round(2 sqrt(T log(T)/M)), clipped to [1,T]; M is predeclared number of changes; stationary W=T",
                                "reward_range_B": 1},
                     "glr_cucb": params},
        "conditions": scenarios,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({name: data["summary"]["policies"] for name, data in scenarios.items()}, indent=2))


if __name__ == "__main__":
    run()
