#!/usr/bin/env python3
"""Passive detectability audit for the archived S3b GLR-CUCB protocol."""

from __future__ import annotations

import json
import random
import statistics
from pathlib import Path

from experiments.run_hls_s3b_glr_cucb import (
    BASELINES, EVAL_SEEDS, HORIZON, ORIGINAL, OUT as GLR_ARCHIVE, POLICIES, _detection_summary,
    ci, evaluate, parameters,
)
from experiments.run_hls_s3b_nonstationary_unknown_assignment import (
    OUT as BASELINE_ORIGINAL,
)
from hls.glr_cucb import GLRCUCB

OUT = Path("results/experiments/hls_s3b_glr_detectability/results.json")
CONTROL_SEEDS = tuple(range(41000, 41100))
POST_LENGTHS = (10, 25, 50, 100)
PRE_LENGTH = 60
CONTROL_EFFECTS = {
    "stationary_0.50_to_0.50": (0.50, 0.50),
    "small_0.45_to_0.55": (0.45, 0.55),
    "moderate_0.30_to_0.70": (0.30, 0.70),
    "hls_0.20_to_0.80": (0.20, 0.80),
    "large_0.10_to_0.90": (0.10, 0.90),
}


def _bernoulli(rng, p):
    return float(rng.random() < p)


def controlled_detector_test(*, pre_length=PRE_LENGTH, effects=CONTROL_EFFECTS):
    """Run fixed, seeded Bernoulli sequences using the unmodified detector."""
    delta = parameters()["delta_glr"]
    effects_out = {}
    for label, (before, after) in effects.items():
        if before == after:
            continue
        horizon_rows = {str(length): [] for length in POST_LENGTHS}
        for seed in CONTROL_SEEDS:
            rng = random.Random(seed)
            model = GLRCUCB(1, 1, horizon=HORIZON, epsilon=0.195001,
                            delta=delta, seed=seed)
            alarms = []
            for t in range(pre_length):
                model.update(t, ((0, 0),), {(0, 0): _bernoulli(rng, before)})
                if model.detections:
                    alarms.append(t)
            pre_alarm = bool(alarms)
            detect_period = None
            snapshots = {}
            for post_n in range(1, max(POST_LENGTHS) + 1):
                t = pre_length + post_n - 1
                model.update(t, ((0, 0),), {(0, 0): _bernoulli(rng, after)})
                stat, threshold, _ = model.last_statistics[(0, 0)]
                snapshots[post_n] = (stat, threshold)
                if model.detections and not pre_alarm:
                    detect_period = post_n
                    # GLR-CUCB globally reset after the first alarm; stop this path.
                    break
            for length in POST_LENGTHS:
                observed_n = min(length, detect_period or length)
                last_stat, last_threshold = snapshots[observed_n]
                horizon_rows[str(length)].append({
                    "seed": seed,
                    "detected_by_post_observation": (
                        detect_period is not None and detect_period <= length),
                    "detection_delay_post_observations": detect_period,
                    "pre_change_false_alarm": pre_alarm,
                    "last_statistic": last_stat,
                    "last_threshold": last_threshold,
                    "statistic_at_horizon": last_stat,
                    "threshold_at_horizon": last_threshold,
                    "last_stat_threshold_ratio": (last_stat / last_threshold
                                                   if last_threshold else None),
                })
        effects_out[label] = {}
        for length, rows in horizon_rows.items():
            delays = [r["detection_delay_post_observations"] for r in rows
                      if r["detection_delay_post_observations"] is not None
                      and r["detection_delay_post_observations"] <= int(length)]
            ratios = [r["last_stat_threshold_ratio"] for r in rows]
            effects_out[label][length] = {
                "seeds": len(rows),
                "detection_rate": statistics.fmean(r["detected_by_post_observation"]
                                                   for r in rows),
                "false_alarm_rate_before_change": statistics.fmean(
                    r["pre_change_false_alarm"] for r in rows),
                "mean_delay_given_detection": statistics.fmean(delays) if delays else None,
                "mean_final_stat_threshold_ratio": statistics.fmean(ratios),
                "max_final_stat_threshold_ratio": max(ratios),
                "median_final_stat_threshold_ratio": statistics.median(ratios),
            }

    stationary_rows = []
    for seed in CONTROL_SEEDS:
        rng = random.Random(seed ^ 0x5157)
        model = GLRCUCB(1, 1, horizon=HORIZON, epsilon=0.195001,
                        delta=delta, seed=seed)
        peak_ratio = 0.0
        for t in range(pre_length + max(POST_LENGTHS)):
            model.update(t, ((0, 0),), {(0, 0): _bernoulli(rng, 0.5)})
            statistic, threshold, _ = model.last_statistics[(0, 0)]
            peak_ratio = max(peak_ratio, statistic / threshold)
        statistic, threshold, n = model.last_statistics[(0, 0)]
        stationary_rows.append({"seed": seed, "false_alarm": bool(model.detections),
                                "maximum_observation_count": n,
                                "last_statistic": statistic, "threshold": threshold,
                                "maximum_stat_threshold_ratio": peak_ratio})
    return {
        "protocol": {"seeds": list(CONTROL_SEEDS), "pre_change_observations": pre_length,
                     "post_change_horizons": list(POST_LENGTHS), "delta": delta,
                     "threshold_unchanged": True,
                     "exploration_irrelevant_to_detector_only_stream": True},
        "stationary_false_alarm_control": {
            "false_alarm_rate": statistics.fmean(r["false_alarm"] for r in stationary_rows),
            "mean_max_stat_threshold_ratio": statistics.fmean(
                r["maximum_stat_threshold_ratio"] for r in stationary_rows),
            "max_stat_threshold_ratio": max(r["maximum_stat_threshold_ratio"]
                                            for r in stationary_rows),
        },
        "changes": effects_out,
    }


def _aggregate_pair_diagnostics(episodes, condition):
    pair_rows = {}
    for i in range(3):
        for k in range(3):
            pair = [episode["glr_detectability"]["pairs"][i * 3 + k]
                    for episode in episodes]
            peak_ratios = [r["peak_glr"]["ratio"] if r["peak_glr"] else 0.0 for r in pair]
            item = {
                "pair": [i, k],
                "mean_selected_evaluation_periods": statistics.fmean(
                    r["selected_evaluation_periods"] for r in pair),
                "selected_evaluation_periods_min_max": [
                    min(r["selected_evaluation_periods"] for r in pair),
                    max(r["selected_evaluation_periods"] for r in pair)],
                "mean_max_glr": statistics.fmean(
                    r["peak_glr"]["statistic"] if r["peak_glr"] else 0.0 for r in pair),
                "mean_max_threshold": statistics.fmean(
                    r["peak_glr"]["threshold"] if r["peak_glr"] else 0.0 for r in pair),
                "mean_max_stat_threshold_ratio": statistics.fmean(peak_ratios),
                "max_stat_threshold_ratio": max(peak_ratios),
                "fraction_episodes_ratio_ge_1": statistics.fmean(x >= 1 for x in peak_ratios),
            }
            pair_rows[f"{i},{k}"] = item
    return pair_rows


def _change_event_summary(episodes):
    grouped = {}
    for episode in episodes:
        for pair_row in episode["glr_detectability"]["pairs"]:
            for change in pair_row.get("changes", []):
                key = str(change["boundary_period"])
                grouped.setdefault(key, []).append((pair_row["pair"], change))
    out = {}
    for boundary, rows in grouped.items():
        changed = [(pair, row) for pair, row in rows if row["absolute_mean_change"] > 0]
        relevant = [(pair, row) for pair, row in changed
                    if row["in_old_optimal_matching"] or row["in_new_optimal_matching"]]
        ratios = [row["peak_after_change"]["ratio"] if row["peak_after_change"] else 0.0
                  for _, row in changed]
        observations = [row["post_change_observations_before_next_change"]
                        for _, row in changed]
        out[boundary] = {
            "episodes": len(episodes), "pair_change_records": len(rows),
            "changed_pair_records": len(changed), "unchanged_pair_records": len(rows) - len(changed),
            "changed_pairs_per_episode_mean": len(changed) / len(episodes),
            "globally_optimal_matching_changed_in_every_episode": all(
                row["globally_optimal_matching_changed"]
                for episode in episodes
                for pair_row in episode["glr_detectability"]["pairs"]
                for row in pair_row.get("changes", []) if str(row["boundary_period"]) == boundary),
            "changed_pairs_in_old_or_new_optimum": len(relevant),
            "post_change_observations_changed_pair_mean_min_max": [
                statistics.fmean(observations), min(observations), max(observations)],
            "max_peak_stat_threshold_ratio_on_changed_pairs": max(ratios, default=0.0),
            "changed_pair_records_reaching_threshold": sum(r >= 1 for r in ratios),
            "max_peak_stat_threshold_ratio_all_pairs": max((
                row["peak_after_change"]["ratio"] if row["peak_after_change"] else 0.0
                for _, row in rows), default=0.0),
        }
    return out


def run():
    original = json.loads(GLR_ARCHIVE.read_text(encoding="utf-8"))
    baseline_original = json.loads(BASELINE_ORIGINAL.read_text(encoding="utf-8"))
    output_conditions = {}
    diagnostic_noninterference = {"episodes": 0, "all_policy_sequences_identical": True,
                                  "max_abs_reward_difference": 0.0}
    reproduction = {name: {"episodes": 0, "assignments_identical": True,
                           "max_abs_expected_reward_difference": 0.0}
                    for name in (*BASELINES, "GLR_CUCB")}
    reproduction["GLR_CUCB"]["assignments_identical"] = None
    reproduction["GLR_CUCB"]["reward_and_alarm_metrics_identical"] = True
    for condition in original["conditions"]:
        episodes = []
        old_by_seed = {episode["seed"]: episode
                       for episode in original["conditions"][condition]["episodes"]}
        baseline_by_seed = {episode["seed"]: episode for episode in
                            baseline_original["conditions"][condition]["episodes"]}
        for seed in EVAL_SEEDS:
            episode = evaluate(condition, seed, diagnostic_trace=True)
            untraced = evaluate(condition, seed, diagnostic_trace=False)
            diagnostic_noninterference["episodes"] += 1
            for policy in POLICIES:
                traced_policy = episode["policies"][policy]
                plain_policy = untraced["policies"][policy]
                difference = abs(traced_policy["cumulative_expected_reward"] -
                                 plain_policy["cumulative_expected_reward"])
                diagnostic_noninterference["max_abs_reward_difference"] = max(
                    difference, diagnostic_noninterference["max_abs_reward_difference"])
                if (traced_policy["assignment_ids"] != plain_policy["assignment_ids"]
                        or difference > 1e-10):
                    diagnostic_noninterference["all_policy_sequences_identical"] = False
                    raise AssertionError(f"diagnostic altered policy: {condition}/{seed}/{policy}")
            old = old_by_seed[seed]
            old_baseline = baseline_by_seed[seed]
            if episode["calibration_assignment_ids"] != old_baseline["calibration_assignment_ids"]:
                raise AssertionError("calibration differs from archived run")
            for policy in BASELINES:
                newp, oldp = episode["policies"][policy], old_baseline["policies"][policy]
                diff = abs(newp["cumulative_expected_reward"] -
                           oldp["cumulative_expected_reward"])
                reproduction[policy]["episodes"] += 1
                reproduction[policy]["max_abs_expected_reward_difference"] = max(
                    diff, reproduction[policy]["max_abs_expected_reward_difference"])
                if (newp["assignment_ids"] != oldp["assignment_ids"] or diff > 1e-10):
                    reproduction[policy]["assignments_identical"] = False
                    raise AssertionError(f"reproduction mismatch: {condition}/{seed}/{policy}")
            new_glr, old_glr = episode["policies"]["GLR_CUCB"], old["policies"]["GLR_CUCB"]
            diff = abs(new_glr["cumulative_expected_reward"] -
                       old_glr["cumulative_expected_reward"])
            reproduction["GLR_CUCB"]["episodes"] += 1
            reproduction["GLR_CUCB"]["max_abs_expected_reward_difference"] = max(
                diff, reproduction["GLR_CUCB"]["max_abs_expected_reward_difference"])
            if diff > 1e-10 or new_glr["detection_count"] != old_glr["detection_count"]:
                reproduction["GLR_CUCB"]["reward_and_alarm_metrics_identical"] = False
                raise AssertionError(f"GLR scalar reproduction mismatch: {condition}/{seed}")
            reproduction["GLR_CUCB"]["assignment_sequence_reproduced"] = (
                "not verifiable: archived GLR episodes do not store assignment IDs")
            episodes.append(episode)
        if any(ep["policies"]["GLR_CUCB"]["detection_count"] for ep in episodes):
            raise AssertionError("the diagnostic rerun changed original GLR alarm count")
        output_conditions[condition] = {
            "change_periods": original["conditions"][condition]["change_periods"],
            "glr_rewards_and_alarms_match_original": True,
            "change_detectability_summary": _change_event_summary(episodes),
            "detectability_summary_by_pair": _aggregate_pair_diagnostics(episodes, condition),
            "per_seed_pair_traces": [{"seed": ep["seed"],
                                      "pairs": ep["glr_detectability"]["pairs"]}
                                     for ep in episodes],
            "selection_and_detection_summary": _detection_summary(episodes, condition),
        }
    if not all(reproduction[name]["assignments_identical"] for name in BASELINES):
        raise AssertionError("diagnostic execution must reproduce every archived policy")
    result = {
        "experiment": "HLS-S3b-GLR-detectability-diagnostic",
        "article": "Zhou et al. (AAAI 2020), arXiv:1908.10402v4",
        "protocol_reference": str(ORIGINAL),
        "parameterization": parameters(),
        "diagnostic_is_passive": True,
        "baseline_reproduction": reproduction,
        "diagnostic_noninterference": diagnostic_noninterference,
        "conditions": output_conditions,
        "controlled_detector_only": controlled_detector_test(),
        "hls_effect_matched_pre_observations": controlled_detector_test(
            pre_length=15, effects={"hls_0.20_to_0.80": CONTROL_EFFECTS["hls_0.20_to_0.80"]}),
        "notes": [
            "True means and change points are used only by this evaluator, never by GLR-CUCB.",
            "Pair GLR statistics are recomputed from the exact current detector history plus the just-observed selected feedback; this does not update policy state.",
            "Pair statistics are only new at an observation of that pair, matching the detector's update schedule.",
            "Change relevance is determined by exact pre/post optimal matching under the known synthetic means.",
            "All original S3b result files are read-only and preserved.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps({"result_path": str(OUT),
                      "baseline_reproduction": result["baseline_reproduction"],
                      "controlled_detector_only": result["controlled_detector_only"],
                      "conditions": {name: {
                          "max_ratio": max(pair["max_stat_threshold_ratio"]
                                           for pair in item["detectability_summary_by_pair"].values()),
                          "pair_mean_ratios": {key: value["mean_max_stat_threshold_ratio"]
                                               for key, value in item["detectability_summary_by_pair"].items()}}
                          for name, item in result["conditions"].items()}}, indent=2))
