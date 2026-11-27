"""Paired exploratory D1/P1/WAPS pilot on the frozen V2_24X7 load profile."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import json
from math import sqrt
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend  # noqa: E402
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow  # noqa: E402


CONFIG = Path(__file__).with_name("config") / "SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json"
POLICIES = ("D1", "P1", "WAPS")
DEFAULT_SEEDS = tuple(range(2026112701, 2026112711))
T_CRIT_95_DF9 = 2.262157162740992


def _digest(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def _service_metrics(start: float, end: float, segments: Iterable) -> float:
    return sum(max(0.0, min(end, segment.end) - max(start, segment.start))
               for segment in segments)


def _run_one(scenario, seed: int, policy: str) -> dict:
    triage, trace = scenario.triage_scenario_for(seed, policy=policy)
    execution = run_triage_flow(triage, flow_mode=scenario.flow_mode,
                                backend=CalendarBackend())
    trace_rows = {row.routed.alert.alert_id: row for row in trace
                  if row.routed.alert.arrival < scenario.settings.admission_horizon}
    alerts = {alert.alert_id: alert for alert in triage.alerts
              if alert.arrival < scenario.settings.admission_horizon}
    outcomes = {item.alert_id: item for item in execution.outcomes}
    assignments = {item.alert_id: item for stage in execution.stage_results.values()
                   for item in stage.assignments}
    tasks = {aid: task for stage in execution.stage_results.values()
             for aid, task in stage.tasks_by_alert.items()}
    segments_by_level = {
        level: stage.work_segments or ()
        for level, stage in execution.stage_results.items()
    }
    eligible_ids = {level: {r.analyst.analyst_id for r in scenario.organization.resources_for(level)}
                    for level in ("L1", "L2")}

    exogenous = []
    for aid, alert in sorted(alerts.items()):
        row = trace_rows[aid]
        exogenous.append((aid, alert.arrival, alert.task_class, row.severity, alert.deadline,
                          row.difficulty, bool(row.true_escalation_need),
                          bool(row.routed.soctra_recommendation)))
    exogenous_hash = _digest(exogenous)
    environment_rows = []
    for aid in sorted(alerts):
        reference = triage.reference_escalation_by_alert[aid]
        recommendation = triage.recommendation_l2_by_alert[aid]
        scale = (triage.alpha if recommendation and not reference else
                 triage.gamma if reference and not recommendation else 1.0)
        environment_rows.append((aid, triage.difficulty_by_alert[aid], scale))
    environment_hash = _digest(environment_rows)
    confusion = Counter(outcome.confusion for outcome in execution.outcomes)
    routes = Counter(outcome.final_investigation_level for outcome in execution.outcomes)
    status = Counter(outcome.status for outcome in execution.outcomes)
    on_time_quality = sum(assignments[aid].competence for aid, outcome in outcomes.items()
                          if outcome.status == "completed_within_sla" and aid in assignments)
    completed_quality = [assignments[aid].competence for aid, outcome in outcomes.items()
                         if outcome.status != "pending" and aid in assignments]
    response = [outcome.completion - alerts[aid].arrival for aid, outcome in outcomes.items()
                if outcome.completion is not None]
    waits = [task.start - alerts[aid].arrival for aid, task in tasks.items()
             if task.start is not None and aid in alerts]
    result = {
        "seed": seed,
        "policy": policy,
        "alerts": len(alerts),
        "exogenous_trace_sha256": exogenous_hash,
        "environment_realization_sha256": environment_hash,
        "confusion_counts": {key: confusion.get(key, 0) for key in ("TP", "FP", "TN", "FN")},
        "route_counts": {key: routes.get(key, 0) for key in ("L1", "L2")},
        "status_counts": {key: status.get(key, 0) for key in
                          ("completed_within_sla", "completed_late", "pending")},
        "investigation_counts": dict(Counter(x.investigation_count for x in execution.outcomes)),
        "quality_on_time_sum": on_time_quality,
        "R_over_N": on_time_quality / len(alerts) if alerts else 0.0,
        "quality_mean_completed": sum(completed_quality) / len(completed_quality) if completed_quality else None,
        "sla_fraction_on_time": status.get("completed_within_sla", 0) / len(alerts) if alerts else 0.0,
        "sla_fraction_late": status.get("completed_late", 0) / len(alerts) if alerts else 0.0,
        "sla_fraction_pending": status.get("pending", 0) / len(alerts) if alerts else 0.0,
        "mean_response_completed_h": sum(response) / len(response) if response else None,
        "mean_wait_to_start_h": sum(waits) / len(waits) if waits else None,
        "work_done_by_level_h": {
            level: sum(task.effective_work or 0.0 for task in stage.tasks_by_alert.values())
            for level, stage in execution.stage_results.items()
        },
        "mean_wait_h_by_level": {
            level: (sum(task.start - alerts[aid].arrival for aid, task in stage.tasks_by_alert.items()
                        if task.start is not None and aid in alerts) /
                    sum(task.start is not None and aid in alerts for aid, task in stage.tasks_by_alert.items()))
            if any(task.start is not None and aid in alerts for aid, task in stage.tasks_by_alert.items()) else 0.0
            for level, stage in execution.stage_results.items()
        },
        "utilization_by_level_and_regime": {},
        "strata": {},
        "queue_trajectory": [],
        "hlsb_switches": [],
        "hlsb_switch_count_by_level": {},
        # Post-run observability only: exact dispatch-mode counts are returned by
        # the existing engine and do not participate in any policy decision.
        "dispatch_epochs_by_level": {},
        "p1_dispatch_epochs_by_level": {},
        "parameters": {
            level: {"policy": triage.policies[level].name,
                    "waps": asdict(triage.policies[level].waps)
                    if triage.policies[level].waps is not None else None}
            for level in ("L1", "L2")
        },
    }
    assert len(alerts) == len(execution.outcomes)
    assert all(x.investigation_count == 1 for x in execution.outcomes)
    assert all((outcomes[aid].final_investigation_level == "L2") ==
               triage.recommendation_l2_by_alert[aid] for aid in outcomes)
    for level in ("L1", "L2"):
        expected_ids = {aid for aid in outcomes
                        if triage.recommendation_l2_by_alert[aid] == (level == "L2")}
        assert set(execution.stage_results[level].tasks_by_alert) == expected_ids
    assert all(outcomes[aid].deadline == alerts[aid].deadline for aid in outcomes)
    assert all(outcome.analyst_id in eligible_ids[outcome.final_investigation_level]
               for outcome in execution.outcomes if outcome.analyst_id is not None)
    assert sum(result["status_counts"].values()) == len(alerts)
    assert result["route_counts"]["L2"] == result["confusion_counts"]["TP"] + result["confusion_counts"]["FP"]
    assert result["route_counts"]["L1"] == result["confusion_counts"]["TN"] + result["confusion_counts"]["FN"]

    regimes = scenario.demand_profile["regimes"]
    route_by_id = {aid: outcome.final_investigation_level for aid, outcome in outcomes.items()}
    severity_by_id = {aid: row.severity for aid, row in trace_rows.items()}
    confusion_by_id = {aid: outcome.confusion for aid, outcome in outcomes.items()}
    for regime in regimes:
        begin, end = regime["start_h"], regime["end_h"]
        cohort = [aid for aid, alert in alerts.items() if begin <= alert.arrival < end]
        cohort_status = Counter(outcomes[aid].status for aid in cohort)
        qsum = sum(assignments[aid].competence for aid in cohort
                   if outcomes[aid].status == "completed_within_sla" and aid in assignments)
        result["strata"][f"regime:{regime['name']}"] = _stratum(cohort, outcomes, assignments, tasks, alerts, qsum)
        for field, mapping in (("level", route_by_id), ("class", {aid: str(a.task_class) for aid, a in alerts.items()}),
                               ("severity", severity_by_id), ("confusion", confusion_by_id)):
            for value in sorted(set(mapping[aid] for aid in cohort)):
                members = [aid for aid in cohort if mapping[aid] == value]
                score = sum(assignments[aid].competence for aid in members
                            if outcomes[aid].status == "completed_within_sla" and aid in assignments)
                result["strata"][f"regime:{regime['name']}|{field}:{value}"] = _stratum(
                    members, outcomes, assignments, tasks, alerts, score)
        for level in ("L1", "L2"):
            denominator = len(scenario.organization.resources_for(level)) * (end - begin)
            result["utilization_by_level_and_regime"][regime["name"] + ":" + level] = (
                _service_metrics(begin, end, segments_by_level.get(level, ())) / denominator
                if denominator else 0.0)

    all_ids = list(outcomes)
    for field, mapping in (("level", route_by_id),
                           ("class", {aid: str(a.task_class) for aid, a in alerts.items()}),
                           ("severity", severity_by_id),
                           ("confusion", confusion_by_id)):
        for value in sorted(set(mapping[aid] for aid in all_ids)):
            members = [aid for aid in all_ids if mapping[aid] == value]
            score = sum(assignments[aid].competence for aid in members
                        if outcomes[aid].status == "completed_within_sla" and aid in assignments)
            result["strata"][f"{field}:{value}"] = _stratum(
                members, outcomes, assignments, tasks, alerts, score)

    # Queue/work-in-service states use only observed assignments and execution
    # records. Unassigned queue service is not fabricated from hidden future work.
    for t in range(0, int(scenario.settings.admission_horizon) + 1):
        by_level = {}
        for level in ("L1", "L2"):
            aids = [aid for aid, outcome in outcomes.items() if outcome.final_investigation_level == level
                    and alerts[aid].arrival <= t]
            queued = sum(aid not in tasks or tasks[aid].start is None or tasks[aid].start > t
                         for aid in aids)
            active = [aid for aid in aids if aid in tasks and tasks[aid].start is not None
                      and tasks[aid].start <= t and _predicted_completion(aid, tasks[aid], assignments) > t]
            residual = sum(_predicted_completion(aid, tasks[aid], assignments) - t for aid in active)
            by_level[level] = {"queued": queued, "in_service": len(active),
                               "assigned_residual_work_h": residual}
        result["queue_trajectory"].append({"time_h": t, **by_level})

    for level, stage in execution.stage_results.items():
        decisions = stage.policy_decisions or ()
        result["hlsb_switch_count_by_level"][level] = len(decisions)
        result["hlsb_switches"].extend({"level": level, **asdict(item)} for item in decisions)
        native = stage.native_result
        result["dispatch_epochs_by_level"][level] = int(getattr(native, "dispatch_epochs", 0))
        result["p1_dispatch_epochs_by_level"][level] = int(getattr(native, "p1_dispatch_epochs", 0))
    return result


def _stratum(ids, outcomes, assignments, tasks, alerts, quality_on_time_sum):
    n = len(ids)
    statuses = Counter(outcomes[aid].status for aid in ids)
    complete = [outcomes[aid].completion - alerts[aid].arrival for aid in ids
                if outcomes[aid].completion is not None]
    waits = [tasks[aid].start - alerts[aid].arrival for aid in ids
             if aid in tasks and tasks[aid].start is not None]
    qualities = [assignments[aid].competence for aid in ids
                 if outcomes[aid].status != "pending" and aid in assignments]
    return {
        "n": n,
        "completed_within_sla": statuses.get("completed_within_sla", 0),
        "completed_late": statuses.get("completed_late", 0),
        "pending": statuses.get("pending", 0),
        "R_over_N": quality_on_time_sum / n if n else 0.0,
        "sla_fraction_on_time": statuses.get("completed_within_sla", 0) / n if n else 0.0,
        "sla_fraction_late": statuses.get("completed_late", 0) / n if n else 0.0,
        "sla_fraction_pending": statuses.get("pending", 0) / n if n else 0.0,
        "quality_mean_completed": sum(qualities) / len(qualities) if qualities else None,
        "mean_response_completed_h": sum(complete) / len(complete) if complete else None,
        "mean_wait_to_start_h": sum(waits) / len(waits) if waits else None,
    }


def _predicted_completion(alert_id, task, assignments):
    if alert_id in assignments:
        return assignments[alert_id].completion
    if task.start is not None and task.effective_work is not None and task.remaining_work is not None:
        return task.start + task.effective_work + task.remaining_work
    return float("inf")


def run_pilot(config: str | Path = CONFIG, seeds=DEFAULT_SEEDS) -> dict:
    scenario = load_scenario(config)
    config_document = json.loads(Path(config).read_text())
    rows = []
    for seed in seeds:
        seed_rows = [_run_one(scenario, int(seed), policy) for policy in POLICIES]
        if (len({row["exogenous_trace_sha256"] for row in seed_rows}) != 1 or
                len({row["environment_realization_sha256"] for row in seed_rows}) != 1):
            raise AssertionError(f"exogenous trace mismatch for seed {seed}")
        reference = seed_rows[0]
        for row in seed_rows[1:]:
            for key in ("alerts", "confusion_counts", "route_counts"):
                if row[key] != reference[key]:
                    raise AssertionError(f"paired policy mismatch for {key}, seed {seed}")
        rows.extend(seed_rows)
    by_policy = {policy: [row for row in rows if row["policy"] == policy] for policy in POLICIES}
    global_metrics = ("R_over_N", "sla_fraction_on_time", "sla_fraction_late",
                      "sla_fraction_pending", "quality_mean_completed",
                      "mean_response_completed_h", "mean_wait_to_start_h")
    policy_summary = {}
    strata_summary = {}
    for policy, policy_rows in by_policy.items():
        policy_summary[policy] = {}
        for metric in global_metrics:
            values = [row[metric] for row in policy_rows if row[metric] is not None]
            policy_summary[policy][metric] = _mean_sd(values)
        strata_summary[policy] = {}
        common_strata = set.intersection(*(set(row["strata"]) for row in policy_rows))
        for stratum in sorted(common_strata):
            strata_summary[policy][stratum] = {}
            for metric in global_metrics:
                values = [row["strata"][stratum][metric] for row in policy_rows
                          if row["strata"][stratum][metric] is not None]
                strata_summary[policy][stratum][metric] = _mean_sd(values)
    pairwise = {}
    pairs = (("P1", "D1"), ("WAPS", "D1"), ("WAPS", "P1"))
    pair_metrics = ("R_over_N", "sla_fraction_on_time", "mean_response_completed_h",
                    "mean_wait_to_start_h")
    lookup = {(row["policy"], row["seed"]): row for row in rows}
    for left, right in pairs:
        label = f"{left} - {right}"
        pairwise[label] = {}
        for metric in pair_metrics:
            differences = [lookup[left, seed][metric] - lookup[right, seed][metric]
                           for seed in seeds
                           if lookup[left, seed][metric] is not None and lookup[right, seed][metric] is not None]
            pairwise[label][metric] = _paired_summary(differences)
        for regime in ("ordinary", "overload_pulse", "recovery"):
            for metric in ("R_over_N", "sla_fraction_on_time", "sla_fraction_late",
                           "mean_response_completed_h", "mean_wait_to_start_h"):
                differences = [lookup[left, seed]["strata"][f"regime:{regime}"][metric] -
                               lookup[right, seed]["strata"][f"regime:{regime}"][metric]
                               for seed in seeds
                               if lookup[left, seed]["strata"][f"regime:{regime}"][metric] is not None
                               and lookup[right, seed]["strata"][f"regime:{regime}"][metric] is not None]
                pairwise[label][f"regime:{regime}:{metric}"] = _paired_summary(differences)
        stratum_keys = sorted(set.intersection(*(set(lookup[policy, seed]["strata"])
                                                  for policy in (left, right) for seed in seeds)))
        for stratum in stratum_keys:
            for metric in ("R_over_N", "sla_fraction_on_time"):
                differences = [lookup[left, seed]["strata"][stratum][metric] -
                               lookup[right, seed]["strata"][stratum][metric]
                               for seed in seeds]
                pairwise[label][f"stratum:{stratum}:{metric}"] = _paired_summary(differences)

    queue_summary = {}
    for policy in POLICIES:
        policy_rows = by_policy[policy]
        queue_summary[policy] = []
        for index, point in enumerate(policy_rows[0]["queue_trajectory"]):
            item = {"time_h": point["time_h"]}
            for level in ("L1", "L2"):
                for metric in ("queued", "in_service", "assigned_residual_work_h"):
                    vals = [row["queue_trajectory"][index][level][metric] for row in policy_rows]
                    item[f"{level}_{metric}_mean"] = sum(vals) / len(vals)
            queue_summary[policy].append(item)

    return {
        "schema_version": 1,
        "config": str(Path(config)),
        "config_sha256": hashlib.sha256(Path(config).read_bytes()).hexdigest(),
        "organization_sha256": _digest(config_document["organization"]),
        "flow_mode": scenario.flow_mode,
        "backend": "CalendarBackend",
        "policies": list(POLICIES),
        "seeds": [int(seed) for seed in seeds],
        "seed_selection": "fixed before execution; disjoint from historical 711000000-711000399 and documented 998001, 910000, 920000, 930000 seed bases",
        "policy_summary_mean_sd_across_seeds": policy_summary,
        "strata_summary_mean_sd_across_seeds": strata_summary,
        "paired_differences": pairwise,
        "queue_trajectory_mean_across_seeds": queue_summary,
        "runs": rows,
    }


def _mean_sd(values):
    if not values:
        return {"n": 0, "mean": None, "sd": None}
    mean = sum(values) / len(values)
    sd = sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1)) if len(values) > 1 else 0.0
    return {"n": len(values), "mean": mean, "sd": sd}


def _paired_summary(differences):
    summary = _mean_sd(differences)
    mean, sd, n = summary["mean"], summary["sd"], summary["n"]
    half = T_CRIT_95_DF9 * sd / sqrt(n) if n == 10 else None
    summary.update({
        "descriptive_95_percent_t_interval": [mean - half, mean + half] if half is not None else None,
        "left_better_count": sum(value > 1e-12 for value in differences),
        "right_better_count": sum(value < -1e-12 for value in differences),
        "ties_within_1e-12": sum(abs(value) <= 1e-12 for value in differences),
    })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS)
    args = parser.parse_args()
    payload = run_pilot(args.config, args.seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "runs": len(payload["runs"]),
                      "seeds": payload["seeds"], "config_sha256": payload["config_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
