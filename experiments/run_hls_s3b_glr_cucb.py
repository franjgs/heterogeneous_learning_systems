#!/usr/bin/env python3
"""Final paired S3b comparison including Zhou et al.'s GLR-CUCB."""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from scipy.stats import t as student_t

from experiments.run_hls_s3b_nonstationary_unknown_assignment import (
    CALIBRATION_PERIODS, CALIBRATION_PERMUTATIONS, CONDITIONS, EVAL_SEEDS,
    HORIZON, K, N, _estimator, common_calibration, competence_matrix,
    matches_from_id, matches_from_permutation, permutation_id, potential_uniforms, reward_matrix,
    solve,
)
from hls.glr_cucb import GLRCUCB, glr_statistic, glr_threshold
from hls.nonstationary_assignment import PairObservation

OUT = Path("results/experiments/hls_s3b_glr_cucb/results.json")
ORIGINAL = Path("results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json")
POLICIES = ("UCB1_MATCHING", "SW_UCB_MATCHING", "RECENT_MEAN_MATCHING", "GLR_CUCB")
BASELINES = POLICIES[:3]
MATCHINGS = tuple(matches_from_permutation(p) for p in __import__("itertools").permutations(range(N)))


def parameters():
    # Paper's synthetic-experiment prescriptions; same finite HLS horizon/base arms.
    epsilon = 0.5 * math.sqrt((N * K - 1) * math.log(HORIZON) / HORIZON)
    delta = 20.0 / HORIZON
    return {"epsilon_uniform_exploration": epsilon, "delta_glr": delta,
            "confidence_index": "mean + sqrt(3 log(t-tau)/(2 n))",
            "threshold": "paper beta(n,delta), using the cited Q upper bound",
            "restart": "global, all arm histories reset after any detected arm"}


def ci(values):
    vals = tuple(float(v) for v in values)
    mean = statistics.fmean(vals)
    half = student_t.ppf(0.975, len(vals)-1) * statistics.stdev(vals) / math.sqrt(len(vals))
    return {"mean": mean, "sd": statistics.stdev(vals), "ci95": [mean-half, mean+half]}


def evaluate(condition, seed, *, diagnostic_trace=False):
    uniforms = potential_uniforms(seed)
    calibration_ids, raw_history, calibration_trace = common_calibration(condition, uniforms)
    history = {pair: tuple(PairObservation(t, r) for t, r in rows)
               for pair, rows in raw_history.items()}
    window = __import__("experiments.run_hls_s3b_nonstationary_unknown_assignment",
                        fromlist=["window_for"]).window_for(condition)
    models = {
        "UCB1_MATCHING": _estimator("ucb1", HORIZON, history),
        "SW_UCB_MATCHING": _estimator("sw_ucb", window, history),
        "RECENT_MEAN_MATCHING": _estimator("recent_mean", window, history),
        "GLR_CUCB": GLRCUCB(N, K, horizon=HORIZON,
                            epsilon=parameters()["epsilon_uniform_exploration"],
                            delta=parameters()["delta_glr"], seed=seed + 17000,
                            initial_history={pair: tuple((o.period, o.reward) for o in rows)
                                             for pair, rows in history.items()}),
    }
    rows = {name: {"expected": [], "realized": [], "regret": [], "ids": [],
                   "optimal": [], "resource": [], "forced": [], "forced_regret": []}
            for name in POLICIES}
    oracle_values = []
    # Passive audit data: this observer only reads the detector's current
    # samples and the feedback already generated for the chosen matching.
    glr_audit = _new_glr_audit(condition) if diagnostic_trace else None
    for period in range(CALIBRATION_PERIODS, HORIZON):
        means = competence_matrix(condition, period)
        outcomes = reward_matrix(means, uniforms[period])
        oracle = solve(means)
        oracle_id = permutation_id(oracle)
        oracle_value = sum(means[i][k] for i, k in oracle)
        oracle_values.append(oracle_value)
        for name, model in models.items():
            if name == "GLR_CUCB":
                forced_arm = model.forced_arm(period)
                selected = (model.forced_matching(forced_arm, MATCHINGS)
                            if forced_arm is not None else solve(model.score_matrix(period)))
                rows[name]["forced"].append(forced_arm is not None)
            else:
                selected = solve(model.score_matrix(period))
            identifier = permutation_id(selected)
            expected = sum(means[i][k] for i, k in selected)
            realized = sum(outcomes[i][k] for i, k in selected)
            r = rows[name]
            r["expected"].append(expected)
            r["realized"].append(realized)
            r["regret"].append(oracle_value - expected)
            r["ids"].append(identifier)
            r["optimal"].append(identifier == oracle_id)
            r["resource"].append(len(selected))
            if oracle_value - expected < -1e-12:
                raise AssertionError("expected regret became negative")
            r["forced_regret"].append((oracle_value - expected)
                                      if name == "GLR_CUCB" and r["forced"][-1] else 0.0)
        for name, model in models.items():
            selected = matches_from_id(rows[name]["ids"][-1])
            feedback = {(i, k): outcomes[i][k] for i, k in selected}
            if name == "GLR_CUCB" and glr_audit is not None:
                _observe_glr_audit(glr_audit, model, period, selected, feedback,
                                   condition)
            model.update(period, selected, feedback)

    result = {}
    for name, r in rows.items():
        result[name] = {
            "cumulative_expected_reward": sum(r["expected"]),
            "cumulative_expected_regret": sum(r["regret"]),
            "cumulative_realized_reward": sum(r["realized"]),
            "resource_units": sum(r["resource"]),
            "optimal_assignment_rate": statistics.fmean(r["optimal"]),
            "assignment_ids": r["ids"], "expected_reward_by_period": r["expected"],
            "expected_regret_by_period": r["regret"],
        }
        if name == "GLR_CUCB":
            result[name]["forced_exploration_periods"] = sum(r["forced"])
            result[name]["forced_exploration_rate"] = statistics.fmean(r["forced"])
            result[name]["expected_regret_during_forced_exploration"] = sum(r["forced_regret"])
            result[name]["detections"] = model.detections
            result[name]["detection_count"] = len(model.detections)
            result[name]["observations_per_pair_after_last_reset"] = [
                len(model._samples[(i, k)]) for i in range(N) for k in range(K)]
    output = {"seed": seed, "window_periods": window,
            "calibration_assignment_ids": calibration_ids,
            "calibration_trace": calibration_trace,
            "oracle_expected_reward": sum(oracle_values), "policies": result}
    if glr_audit is not None:
        output["glr_detectability"] = _finalize_glr_audit(
            glr_audit, models["GLR_CUCB"], condition)
    return output


def _new_glr_audit(condition):
    return {"selected_periods": {(i, k): [] for i in range(N) for k in range(K)},
            "peaks": {(i, k): None for i in range(N) for k in range(K)},
            "peaks_by_regime": {(i, k): {} for i in range(N) for k in range(K)},
            "condition": condition}


def _observe_glr_audit(audit, model, period, selected, feedback, condition):
    """Compute diagnostics on the exact pre-update stream; never feeds policy."""
    selected = set(selected)
    for pair in selected:
        audit["selected_periods"][pair].append(period)
    regime = sum(period >= boundary for boundary in CONDITIONS[condition]["switches"])
    for i in range(N):
        for k in range(K):
            pair = (i, k)
            samples = list(model._samples[pair])
            if pair in selected:
                samples.append(float(feedback[pair]))
            n = len(samples)
            if n < 2 or pair not in selected:
                continue
            statistic = glr_statistic(samples)
            threshold = glr_threshold(n, model.delta)
            record = {"period": period, "n": n, "statistic": statistic,
                      "threshold": threshold,
                      "ratio": statistic / threshold if threshold else math.inf}
            previous = audit["peaks"][pair]
            if previous is None or record["ratio"] > previous["ratio"]:
                audit["peaks"][pair] = record
            old_regime = audit["peaks_by_regime"][pair].get(regime)
            if old_regime is None or record["ratio"] > old_regime["ratio"]:
                audit["peaks_by_regime"][pair][regime] = record


def _finalize_glr_audit(audit, model, condition):
    switches = CONDITIONS[condition]["switches"]
    out = {"time_basis": "global periods; counts include common calibration",
           "pairs": []}
    for i in range(N):
        for k in range(K):
            pair = (i, k)
            selected_periods = audit["selected_periods"][pair]
            row = {"pair": [i, k], "selected_evaluation_periods": len(selected_periods),
                   "selection_rate": len(selected_periods) / (HORIZON - CALIBRATION_PERIODS),
                   "total_episode_observations_including_calibration": len(selected_periods) + 3,
                   "observations_at_end_after_last_reset": len(model._samples[pair]),
                   "peak_glr": audit["peaks"][pair], "max_by_regime": []}
            for regime in range(len(switches) + 1):
                start = 0 if regime == 0 else switches[regime - 1]
                end = HORIZON if regime == len(switches) else switches[regime]
                times = [*range(0, CALIBRATION_PERIODS)]
                # Every calibration period is a selected edge in exactly one matching;
                # reconstruct pairwise calibration observations from the common protocol.
                calibration_count = sum(
                    pair in matches_from_permutation(
                        CALIBRATION_PERMUTATIONS[t % len(CALIBRATION_PERMUTATIONS)])
                    for t in range(CALIBRATION_PERIODS) if start <= t < end)
                eval_count = sum(start <= t < end for t in selected_periods)
                row["max_by_regime"].append({"regime": regime, "start": start, "end_exclusive": end,
                    "observations_in_regime": calibration_count + eval_count,
                    "peak": _compact_peak(audit["peaks_by_regime"][pair].get(regime))})
            for index, boundary in enumerate(switches):
                end = switches[index + 1] if index + 1 < len(switches) else HORIZON
                before_start = switches[index - 1] if index else 0
                before_count = sum(before_start <= t < boundary
                                   for t in selected_periods)
                calibration_count = sum(
                    pair in matches_from_permutation(
                        CALIBRATION_PERMUTATIONS[t % len(CALIBRATION_PERMUTATIONS)])
                    for t in range(CALIBRATION_PERIODS) if before_start <= t < boundary)
                after_count = sum(boundary <= t < end for t in selected_periods)
                before_means = competence_matrix(condition, boundary - 1)
                after_means = competence_matrix(condition, boundary)
                before_matching = set(solve(before_means))
                after_matching = set(solve(after_means))
                row.setdefault("changes", []).append({
                    "boundary_period": boundary,
                    "pre_change_observations_since_prior_regime": before_count,
                    "pre_change_observations_including_calibration": before_count + calibration_count,
                    "post_change_observations_before_next_change": after_count,
                    "mean_before": before_means[i][k], "mean_after": after_means[i][k],
                    "absolute_mean_change": abs(after_means[i][k] - before_means[i][k]),
                    "in_old_optimal_matching": pair in before_matching,
                    "in_new_optimal_matching": pair in after_matching,
                    "globally_optimal_matching_changed": before_matching != after_matching,
                    "peak_after_change": _compact_peak(
                        audit["peaks_by_regime"][pair].get(index + 1))})
            row["peak_glr"] = _compact_peak(row["peak_glr"])
            out["pairs"].append(row)
    out["max_statistic_events"] = sum(
        len(audit["selected_periods"][pair]) for pair in audit["selected_periods"])
    out["detector_alarm_count"] = len(model.detections)
    return out


def _compact_peak(record):
    if record is None:
        return None
    return {key: record[key] for key in
            ("period", "n", "statistic", "threshold", "ratio")}


def run():
    original = json.loads(ORIGINAL.read_text(encoding="utf-8"))
    conditions_out = {}
    reproduction = {name: {"episodes": 0, "max_abs_reward_difference": 0.0,
                           "assignment_sequences_identical": True} for name in BASELINES}
    for condition in CONDITIONS:
        episodes = []
        old_by_seed = {e["seed"]: e for e in original["conditions"][condition]["episodes"]}
        for seed in EVAL_SEEDS:
            episode = evaluate(condition, seed)
            old = old_by_seed[seed]
            if episode["calibration_assignment_ids"] != old["calibration_assignment_ids"]:
                raise AssertionError("common calibration changed")
            for policy in BASELINES:
                newp, oldp = episode["policies"][policy], old["policies"][policy]
                diff = abs(newp["cumulative_expected_reward"] - oldp["cumulative_expected_reward"])
                reproduction[policy]["episodes"] += 1
                reproduction[policy]["max_abs_reward_difference"] = max(
                    reproduction[policy]["max_abs_reward_difference"], diff)
                if newp["assignment_ids"] != oldp["assignment_ids"] or diff > 1e-10:
                    reproduction[policy]["assignment_sequences_identical"] = False
                    raise AssertionError(f"baseline reproduction failed: {condition}/{seed}/{policy}")
            episodes.append(episode)
        summaries = {}
        for policy in POLICIES:
            summaries[policy] = {
                "expected_reward": ci([e["policies"][policy]["cumulative_expected_reward"] for e in episodes]),
                "expected_regret": ci([e["policies"][policy]["cumulative_expected_regret"] for e in episodes]),
                "realized_reward": ci([e["policies"][policy]["cumulative_realized_reward"] for e in episodes]),
                "optimal_assignment_rate_mean": statistics.fmean(
                    e["policies"][policy]["optimal_assignment_rate"] for e in episodes),
                "resource_units_mean": statistics.fmean(e["policies"][policy]["resource_units"] for e in episodes),
            }
            if policy == "GLR_CUCB":
                counts = [e["policies"][policy]["detection_count"] for e in episodes]
                summaries[policy]["detections_per_seed_mean"] = statistics.fmean(counts)
                summaries[policy]["forced_exploration_periods_mean"] = statistics.fmean(
                    e["policies"][policy]["forced_exploration_periods"] for e in episodes)
                summaries[policy]["expected_regret_during_forced_exploration_mean"] = statistics.fmean(
                    e["policies"][policy]["expected_regret_during_forced_exploration"]
                    for e in episodes)
            summaries[policy]["expected_reward_mean_by_period"] = [statistics.fmean(
                e["policies"][policy]["expected_reward_by_period"][t] for e in episodes)
                for t in range(HORIZON - CALIBRATION_PERIODS)]
            summaries[policy]["expected_regret_mean_by_period"] = [statistics.fmean(
                e["policies"][policy]["expected_regret_by_period"][t] for e in episodes)
                for t in range(HORIZON - CALIBRATION_PERIODS)]
            counts = defaultdict(int)
            for e in episodes:
                for aid in e["policies"][policy]["assignment_ids"]:
                    counts[str(aid)] += 1
            summaries[policy]["assignment_frequency"] = {
                key: {"count": value, "rate": value / (len(episodes) * (HORIZON-CALIBRATION_PERIODS))}
                for key, value in sorted(counts.items(), key=lambda item: int(item[0]))}
        paired = {}
        for comparator in ("UCB1_MATCHING", "SW_UCB_MATCHING", "RECENT_MEAN_MATCHING"):
            diffs = [e["policies"]["GLR_CUCB"]["cumulative_expected_reward"] -
                     e["policies"][comparator]["cumulative_expected_reward"] for e in episodes]
            paired[f"GLR_CUCB_minus_{comparator}"] = ci(diffs)
        conditions_out[condition] = {
            "window_periods": episodes[0]["window_periods"],
            "change_periods": list(CONDITIONS[condition]["switches"]),
            "summaries": summaries, "paired_expected_reward_differences": paired,
            "by_regime": _by_regime(episodes, condition),
            "recovery_lags": _recovery(episodes, condition),
            "change_detection": _detection_summary(episodes, condition),
            "episodes": [{"seed": e["seed"], "policies": {
                p: {k: v for k, v in e["policies"][p].items()
                    if k not in {"assignment_ids", "expected_reward_by_period", "expected_regret_by_period"}}
                for p in POLICIES}} for e in episodes],
        }
    output = {
        "experiment": "HLS-S3b-final-GLR-CUCB",
        "reference": "Zhou et al. AAAI 2020, arXiv:1908.10402v4",
        "protocol": {"N": N, "K": K, "horizon": HORIZON,
                     "calibration_periods": CALIBRATION_PERIODS,
                     "evaluation_periods": HORIZON-CALIBRATION_PERIODS,
                     "seeds": list(EVAL_SEEDS), "paired_potential_rewards": True,
                     "initialization_adaptation": "common 9-round calibration carried as GLR prehistory; detector clock starts at its end",
                     "reward": "sum of Bernoulli edge rewards; expected reward is sum of current edge means",
                     "parameterization": parameters()},
        "baseline_reproduction": reproduction,
        "conditions": conditions_out,
        "limitations": [
            "Matching-oracle integration is an HLS adaptation; paper guarantees are not asserted for this finite initialized protocol.",
            "GLR-CUCB global restarts reset all edge histories; forced exploration selects a random perfect matching containing the scheduled edge.",
            "The threshold uses the paper-cited conservative upper bound for Q, not numerical inversion of Q.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _by_regime(episodes, condition):
    bounds = (CALIBRATION_PERIODS,) + tuple(CONDITIONS[condition]["switches"]) + (HORIZON,)
    out = {}
    for policy in POLICIES:
        out[policy] = {}
        for j in range(len(bounds)-1):
            start, end = max(bounds[j], CALIBRATION_PERIODS), bounds[j+1]
            if start >= end:
                continue
            out[policy][str(j)] = {
                "periods": end-start,
                "expected_reward_mean": statistics.fmean(sum(
                    e["policies"][policy]["expected_reward_by_period"][t-CALIBRATION_PERIODS]
                    for t in range(start, end)) for e in episodes),
                "expected_regret_mean": statistics.fmean(sum(
                    e["policies"][policy]["expected_regret_by_period"][t-CALIBRATION_PERIODS]
                    for t in range(start, end)) for e in episodes),
            }
    return out


def _recovery(episodes, condition):
    boundaries = CONDITIONS[condition]["switches"]
    out = {policy: [] for policy in POLICIES}
    for boundary_index, boundary in enumerate(boundaries):
        end = boundaries[boundary_index + 1] if boundary_index + 1 < len(boundaries) else HORIZON
        optimum_id = permutation_id(solve(competence_matrix(condition, boundary)))
        for policy in POLICIES:
            lags = []
            for episode in episodes:
                ids = episode["policies"][policy]["assignment_ids"]
                start_idx = boundary - CALIBRATION_PERIODS
                end_idx = end - CALIBRATION_PERIODS
                found = next((j - start_idx for j in range(start_idx, end_idx)
                              if ids[j] == optimum_id), None)
                lags.append(found)
            observed = [x for x in lags if x is not None]
            out[policy].append({"boundary_period": boundary,
                                "recovered_fraction": len(observed) / len(lags),
                                "mean_lag_when_recovered": statistics.fmean(observed) if observed else None,
                                "censored_count": len(lags) - len(observed),
                                "censor_at_periods": end-boundary})
    return out


def _detection_summary(episodes, condition):
    switches = CONDITIONS[condition]["switches"]
    all_events = [(ep["seed"], event) for ep in episodes
                  for event in ep["policies"]["GLR_CUCB"]["detections"]]
    matched_delays = []
    false_alarms = 0
    for _, event in all_events:
        prior = [switch for switch in switches if switch <= event["period"]]
        if prior and (not switches or event["period"] < next(
                (switch for switch in switches if switch > prior[-1]), HORIZON)):
            matched_delays.append(event["period"] - prior[-1])
        else:
            false_alarms += 1
    return {"mean_alarms_per_seed": len(all_events) / len(episodes),
            "alarms_total": len(all_events), "false_alarms_total": false_alarms,
            "false_alarms_per_seed": false_alarms / len(episodes),
            "matched_change_delays_periods": matched_delays,
            "mean_matched_delay_periods": statistics.fmean(matched_delays) if matched_delays else None,
            "real_change_count_per_seed": len(switches),
            "classification_note": "An alarm after a true breakpoint is counted as matched to the most recent breakpoint; this temporal attribution is descriptive, not a causal detector-validity test."}


if __name__ == "__main__":
    result = run()
    print(json.dumps({"result_path": str(OUT), "baseline_reproduction": result["baseline_reproduction"],
                      "summaries": {c: x["summaries"] for c, x in result["conditions"].items()}}, indent=2))
