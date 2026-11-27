"""Post-process the pre-registered NEW MODEL profile-D confirmatory run."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

from scipy.stats import t as student_t


POLICIES = ("D1", "P1", "WAPS")
COHORTS = ("ordinary", "overload_pulse", "recovery")
HORIZON_H = 360.0


def mean_sd(values):
    return {"mean": statistics.mean(values), "sample_sd": statistics.stdev(values)}


def paired(values, control_mean):
    n = len(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(n)
    df = n - 1
    t_stat = mean / se
    critical = student_t.ppf(0.975, df)
    return {
        "n_episodes": n,
        "mean_difference": mean,
        "sample_sd": sd,
        "ci95_two_sided_t": [mean - critical * se, mean + critical * se],
        "t_statistic": t_stat,
        "degrees_of_freedom": df,
        "p_one_sided_greater": float(student_t.sf(t_stat, df)),
        "positive_episodes": sum(value > 0 for value in values),
        "negative_episodes": sum(value < 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "relative_to_control_mean": mean / control_mean,
    }


def validate(rows, seeds):
    lookup = {(row["policy"], row["seed"]): row for row in rows}
    assert len(rows) == len(seeds) * len(POLICIES)
    assert set(lookup) == {(policy, seed) for policy in POLICIES for seed in seeds}
    for seed in seeds:
        triplet = [lookup[policy, seed] for policy in POLICIES]
        for field in ("exogenous_trace_sha256", "environment_realization_sha256"):
            assert len({row[field] for row in triplet}) == 1, (seed, field)
        for field in ("alerts", "confusion_counts", "route_counts"):
            assert len({json.dumps(row[field], sort_keys=True) for row in triplet}) == 1
        for row in triplet:
            assert sum(row["investigation_counts"].values()) == row["alerts"]
            assert row["status_counts"].get("pending", 0) == 0
            assert row["route_counts"]["L2"] == row["confusion_counts"]["TP"] + row["confusion_counts"]["FP"]
            assert row["route_counts"]["L1"] == row["confusion_counts"]["TN"] + row["confusion_counts"]["FN"]
    return lookup


def hlsb_state_fractions(rows):
    totals = {level: {"D1": 0.0, "P1": 0.0} for level in ("L1", "L2")}
    counts = {level: 0 for level in ("L1", "L2")}
    for row in rows:
        for level in ("L1", "L2"):
            events = sorted((event for event in row["hlsb_switches"] if event["level"] == level),
                            key=lambda event: event["time"])
            mode, last = "D1", 0.0
            counts[level] += len(events)
            for event in events:
                at = min(HORIZON_H, max(last, float(event["time"])))
                totals[level][mode] += at - last
                mode, last = event["mode"], at
            totals[level][mode] += HORIZON_H - last
    denominator = len(rows) * HORIZON_H
    return {
        level: {"switch_events": counts[level],
                "state_hours_per_episode_mean": {mode: hours / len(rows) for mode, hours in state.items()},
                "state_fraction_of_360h": {mode: hours / denominator for mode, hours in state.items()}}
        for level, state in totals.items()
    }


def analyze(payload):
    rows, seeds = payload["runs"], payload["seeds"]
    lookup = validate(rows, seeds)
    policy = {}
    for name in POLICIES:
        subset = [lookup[name, seed] for seed in seeds]
        fields = ("R_over_N", "sla_fraction_on_time", "sla_fraction_late", "sla_fraction_pending",
                  "quality_mean_completed", "mean_response_completed_h", "mean_wait_to_start_h")
        policy[name] = {field: mean_sd([row[field] for row in subset]) for field in fields}
        policy[name]["mean_alerts"] = statistics.mean(row["alerts"] for row in subset)
        policy[name]["mean_status_counts"] = {
            status: statistics.mean(row["status_counts"].get(status, 0) for row in subset)
            for status in ("completed_within_sla", "completed_late", "pending")}

    primary = {}
    for control in ("D1", "P1"):
        differences = [lookup["WAPS", seed]["R_over_N"] - lookup[control, seed]["R_over_N"]
                       for seed in seeds]
        primary[f"WAPS - {control}"] = paired(
            differences, policy[control]["R_over_N"]["mean"])

    cohorts = {}
    for cohort in COHORTS:
        stratum = f"regime:{cohort}"
        cohorts[cohort] = {name: {
            metric: mean_sd([lookup[name, seed]["strata"][stratum][metric] for seed in seeds])
            for metric in ("R_over_N", "sla_fraction_on_time", "sla_fraction_late",
                           "sla_fraction_pending", "quality_mean_completed", "mean_wait_to_start_h")
        } for name in POLICIES}
        cohorts[cohort]["mean_alerts"] = statistics.mean(
            lookup["D1", seed]["strata"][stratum]["n"] for seed in seeds)
        cohorts[cohort]["paired"] = {}
        for control in ("D1", "P1"):
            for metric in ("R_over_N", "sla_fraction_on_time"):
                diff = [lookup["WAPS", seed]["strata"][stratum][metric]
                        - lookup[control, seed]["strata"][stratum][metric] for seed in seeds]
                cohorts[cohort]["paired"][f"WAPS - {control}: {metric}"] = {
                    **mean_sd(diff),
                    "ci95_two_sided_t": [
                        statistics.mean(diff) - student_t.ppf(.975, len(diff)-1) * statistics.stdev(diff) / math.sqrt(len(diff)),
                        statistics.mean(diff) + student_t.ppf(.975, len(diff)-1) * statistics.stdev(diff) / math.sqrt(len(diff))],
                    "positive_episodes": sum(x > 0 for x in diff),
                    "negative_episodes": sum(x < 0 for x in diff),
                    "ties": sum(x == 0 for x in diff),
                }

    unique = [lookup["D1", seed] for seed in seeds]
    mean_alerts = statistics.mean(row["alerts"] for row in unique)
    confusion = {key: statistics.mean(row["confusion_counts"][key] for row in unique)
                 for key in ("TP", "FP", "TN", "FN")}
    queues = {}
    for policy_name in POLICIES:
        subset = [lookup[policy_name, seed] for seed in seeds]
        queues[policy_name] = {
            level: {
                "mean_episode_max_queued": statistics.mean(
                    max(point[level]["queued"] for point in row["queue_trajectory"]) for row in subset),
                "peak_mean_hourly_queue": max(
                    point[f"{level}_queued_mean"]
                    for point in payload["queue_trajectory_mean_across_seeds"][policy_name]),
            } for level in ("L1", "L2")}

    return {
        "classification": "pre-registered confirmatory analysis of NEW MODEL; no exploratory episodes included",
        "config_sha256": payload["config_sha256"],
        "organization_sha256": payload["organization_sha256"],
        "seeds": seeds,
        "n_seeds": len(seeds),
        "n_episodes": len(rows),
        "integrity": {"paired_trace_and_environment_identity": True,
                      "one_investigation_each_alert": True,
                      "direct_routes_consistent_with_triage": True,
                      "pending_episodes": sum(row["status_counts"].get("pending", 0) for row in rows),
                      "mean_alert_count_per_episode": mean_alerts,
                      "mean_confusion_counts_per_trace": confusion},
        "policy_means_sd": policy,
        "primary_intersection_union_tests": primary,
        "cohorts_by_arrival_regime": cohorts,
        "mean_queue_diagnostics": queues,
        "hlsb_state_occupancy": hlsb_state_fractions([lookup["WAPS", seed] for seed in seeds]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.results.read_text())
    result = analyze(payload)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "n_seeds": result["n_seeds"],
                      "n_episodes": result["n_episodes"], "primary": result["primary_intersection_union_tests"]}, indent=2))


if __name__ == "__main__":
    main()
