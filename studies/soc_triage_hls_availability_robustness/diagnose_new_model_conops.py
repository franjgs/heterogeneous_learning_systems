"""Run and summarize one seeded CONOPS organizational diagnostic.

This is a single technical episode, not a campaign. It reuses the configured
trace generator, the common triage executor, CalendarBackend (continuous
calendars in this profile), and the existing eligibility-constrained LP.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import isclose
from pathlib import Path
import sys
from statistics import mean, median

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend  # noqa: E402
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (  # noqa: E402
    CapacityDemandProfile, DemandRegime, assess_capacity,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow  # noqa: E402


DEFAULT_CONFIG = Path(__file__).with_name("config") / "SOC_NEW_MODEL_CONOPS_REFERENCE.json"
DEFAULT_OUTPUT = Path(__file__).with_name("results") / "soc_new_model_conops" / "seed_2026112801.json"


def _summary(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0}
    waits = [x["wait_h"] for x in rows if x["wait_h"] is not None]
    responses = [x["response_h"] for x in rows if x["response_h"] is not None]
    services = [x["service_h"] for x in rows if x["service_h"] is not None]
    return {
        "n": n,
        "sla": {
            "within": sum(x["status"] == "completed_within_sla" for x in rows),
            "late": sum(x["status"] == "completed_late" for x in rows),
            "pending": sum(x["status"] == "pending" for x in rows),
        },
        "service_h": {"sum": sum(services), "mean": mean(services) if services else None},
        "wait_h": {"mean": mean(waits) if waits else None,
                   "median": median(waits) if waits else None,
                   "p90": sorted(waits)[int(.9 * (len(waits) - 1))] if waits else None},
        "response_h": {"mean": mean(responses) if responses else None,
                       "median": median(responses) if responses else None,
                       "p90": sorted(responses)[int(.9 * (len(responses) - 1))] if responses else None},
        "mean_q": mean(x["q"] for x in rows),
        "mean_modeled_quality": mean(x["modeled_quality"] for x in rows),
        "timely_modeled_quality_sum": sum(
            x["modeled_quality"] for x in rows if x["status"] == "completed_within_sla"
        ),
    }


def run_diagnostic(config_path: str | Path = DEFAULT_CONFIG, seed: int | None = None) -> dict:
    config_path = Path(config_path)
    scenario = load_scenario(config_path)
    seed = scenario.seed_start if seed is None else int(seed)
    triage, trace = scenario.triage_scenario_for(seed)
    result = run_triage_flow(triage, flow_mode=scenario.flow_mode,
                             backend=CalendarBackend())
    demand = scenario.demand_profile
    classes = tuple(demand["class_mix"])
    regime = demand["regimes"][0]
    profile = CapacityDemandProfile(
        regimes=(DemandRegime(regime["name"], regime["start_h"], regime["end_h"],
                              regime["arrival_rate_by_class"]),),
        prevalence_by_class=demand["prevalence_by_class"],
        sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"],
        alpha=demand["alpha"], beta=demand["beta"],
        difficulty_mean_by_class_and_need=demand.get("difficulty_mean_by_class_and_need"),
        gamma=demand["gamma"], flow_mode=scenario.flow_mode,
    )
    capacity = assess_capacity(scenario.organization, profile)

    by_id = {row.routed.alert.alert_id: row for row in trace}
    outcome_by_id = {row.alert_id: row for row in result.outcomes}
    resource_by_id = {r.analyst.analyst_id: r for r in scenario.organization.analysts}
    assignment_by_id = {
        assignment.alert_id: (level, assignment)
        for level, stage in result.stage_results.items()
        for assignment in stage.assignments
    }
    records = []
    for alert_id, row in by_id.items():
        outcome = outcome_by_id[alert_id]
        level, assignment = assignment_by_id[alert_id]
        task = result.stage_results[level].tasks_by_alert[alert_id]
        resource = resource_by_id[assignment.analyst_id]
        q = float(row.difficulty)
        modeled_quality = float(assignment.competence) * (1.0 - 0.35 * q)
        records.append({
            "alert_id": alert_id,
            "class": str(row.routed.alert.task_class),
            "severity": row.severity,
            "complex": q >= float(scenario.generation["parameters"]["reference_escalation_difficulty_threshold"]),
            "q": q,
            "reference_l2": bool(row.true_escalation_need),
            "recommend_l2": bool(row.routed.soctra_recommendation),
            "confusion": outcome.confusion,
            "level": level,
            "analyst": assignment.analyst_id,
            "arrival_h": float(row.routed.alert.arrival),
            "deadline_h": float(row.routed.alert.deadline),
            "start_h": task.start,
            "completion_h": task.completion,
            "service_h": task.effective_work,
            "wait_h": None if task.start is None else task.start - row.routed.alert.arrival,
            "response_h": None if task.completion is None else task.completion - row.routed.alert.arrival,
            "suspension_h": task.suspension,
            "status": outcome.status,
            "investigation_count": outcome.investigation_count,
            "modeled_quality": modeled_quality,
            "eligible_classes": sorted(resource.analyst.eligible_classes),
        })

    groupings = {}
    for key_fields in (("level",), ("confusion",), ("class",), ("severity",),
                       ("complex",), ("level", "confusion"), ("level", "class"),
                       ("level", "severity"), ("level", "complex")):
        groups = defaultdict(list)
        for row in records:
            key = tuple(row[field] for field in key_fields)
            groups[key].append(row)
        groupings["+".join(key_fields)] = [
            {**{field: value for field, value in zip(key_fields, key)}, **_summary(rows)}
            for key, rows in sorted(groups.items(), key=lambda x: str(x[0]))
        ]

    horizon = float(scenario.settings.admission_horizon)
    levels = {}
    queue_series = []
    for level in ("L1", "L2"):
        rows = [x for x in records if x["level"] == level]
        stages = result.stage_results[level]
        segments = stages.work_segments or ()
        resources = scenario.organization.resources_for(level)
        analyst_util = {}
        for resource in resources:
            aid = resource.analyst.analyst_id
            active_in_admission = sum(max(0.0, min(end, horizon) - max(start, 0.0))
                                      for segment in segments if segment.analyst_id == aid
                                      for start, end in ((segment.start, segment.end),))
            analyst_util[aid] = {
                "active_work_h_during_admission": active_in_admission,
                "available_work_h_during_admission": horizon,
                "utilization_during_admission": active_in_admission / horizon,
            }
        total_admission_work = sum(x["active_work_h_during_admission"] for x in analyst_util.values())
        levels[level] = {
            "assigned_alerts": len(rows),
            "route_rate_per_h": len(rows) / horizon,
            "effective_service_work_h_terminal": sum(x["service_h"] or 0.0 for x in rows),
            "team_available_work_h_during_admission": len(resources) * horizon,
            "aggregate_utilization_during_admission": total_admission_work / (len(resources) * horizon),
            "mean_wait_h": _summary(rows)["wait_h"]["mean"],
            "mean_response_h": _summary(rows)["response_h"]["mean"],
            "mean_service_h": _summary(rows)["service_h"]["mean"],
            "sla": _summary(rows)["sla"],
            "analyst_utilization": analyst_util,
            "dispatch_epochs": getattr(stages.native_result, "dispatch_epochs", None),
            "policy": triage.policies[level].name,
        }

    def work_served_by(t: float, segment_rows) -> dict[str, float]:
        out = defaultdict(float)
        for segment in segment_rows:
            out[segment.alert_id] += max(0.0, min(t, segment.end) - segment.start)
        return out

    time_step = 0.25
    for step in range(int(round(scenario.settings.evaluation_horizon / time_step)) + 1):
        hour = step * time_step
        observation = {"time_h": hour}
        for level in ("L1", "L2"):
            tasks = result.stage_results[level].tasks_by_alert
            stage_segments = result.stage_results[level].work_segments or ()
            served = work_served_by(float(hour), stage_segments)
            queue = [aid for aid, task in tasks.items()
                     if by_id[aid].routed.alert.arrival <= hour and
                     (task.start is None or task.start > hour)]
            observation[f"queue_{level}"] = len(queue)
            # Exact active residual for started alerts plus forecast-service lower-bound
            # estimate for alerts still waiting (no future analyst choice is imputed).
            residual = 0.0
            for aid, task in tasks.items():
                if by_id[aid].routed.alert.arrival > hour or (task.completion is not None and task.completion <= hour):
                    continue
                alert = by_id[aid].routed.alert
                q = float(by_id[aid].difficulty)
                f_q = 1.0 + triage.difficulty_service_beta * (q - 0.5)
                if task.start is None or task.start > hour:
                    eligible = [r for r in scenario.organization.resources_for(level)
                                if alert.task_class in r.analyst.eligible_classes]
                    residual += min(r.forecast_service_by_class[alert.task_class] for r in eligible)
                else:
                    assigned = resource_by_id[task.analyst_id]
                    required = assigned.service_by_class[alert.task_class] * f_q
                    residual += max(0.0, required - served.get(aid, 0.0))
            observation[f"pending_work_{level}_h"] = residual
        queue_series.append(observation)

    confusion = Counter(x["confusion"] for x in records)
    route_counts = Counter(x["level"] for x in records)
    trace_serialized = [{k: x[k] for k in ("alert_id", "class", "severity", "q", "reference_l2",
                                          "recommend_l2", "arrival_h", "deadline_h")}
                        for x in records]
    trace_hash = hashlib.sha256(json.dumps(trace_serialized, sort_keys=True,
                                           separators=(",", ":")).encode()).hexdigest()
    capacities = []
    for row in capacity.regimes:
        capacities.append({
            "level": row.level,
            "rate_in_per_h": row.offered_rate_per_h,
            "capacity_assignable_alerts_per_h": row.capacity_per_h,
            "relative_load": row.relative_load,
            "status": row.load_status,
            "offered_work_h_per_h": (row.offered_l1_work_h_per_h if row.level == "L1"
                                      else row.offered_l2_work_h_per_h),
            "bottleneck_analysts": list(row.bottleneck_analysts),
            "uncovered_classes": list(row.unstaffed_classes),
        })
    return {
        "scenario_id": scenario.scenario_id,
        "config_path": config_path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "seed": seed,
        "trace_sha256": trace_hash,
        "flow_mode": scenario.flow_mode,
        "policies": {level: triage.policies[level].name for level in ("L1", "L2")},
        "admission_h": scenario.settings.admission_horizon,
        "evaluation_h": scenario.settings.evaluation_horizon,
        "arrival_intensity_total_per_h": demand["arrival_intensity_total_per_h"],
        "generated_alerts": len(records),
        "observed_total_arrival_rate_per_admission_h": len(records) / scenario.settings.admission_horizon,
        "confusion_counts": {key: confusion.get(key, 0) for key in ("TP", "FP", "TN", "FN")},
        "route_counts": {key: route_counts.get(key, 0) for key in ("L1", "L2")},
        "investigation_count_distribution": dict(Counter(x["investigation_count"] for x in records)),
        "overall": _summary(records),
        "by_group": groupings,
        "capacity_lp": {"assumptions": list(capacity.assumptions), "levels": capacities},
        "observed_levels": levels,
        "mean_recommendation_rate_expected": sum(
            demand["class_mix"][k] * (
                demand["prevalence_by_class"][k] * demand["sensitivity_by_class"][k]
                + (1 - demand["prevalence_by_class"][k]) * demand["false_positive_rate_by_class"][k]
            ) for k in classes
        ),
        "queue_series_15min": queue_series,
        "queue_series_interval_h": time_step,
        "records": records,
        "validation": {
            "trace_count_matches_outcomes": len(records) == len(result.outcomes),
            "exactly_one_investigation_each": all(x["investigation_count"] == 1 for x in records),
            "route_matches_recommendation": all(x["level"] == ("L2" if x["recommend_l2"] else "L1") for x in records),
            "deadline_offsets_preserved": all(isclose(
                x["deadline_h"] - x["arrival_h"],
                scenario.settings.deadlines.offsets_by_severity_h[x["severity"]],
                rel_tol=0.0, abs_tol=1e-12,
            ) for x in records),
            "all_calendars_continuous": all(r.calendar.available(0) and r.calendar.available(167.9)
                                             for r in scenario.organization.analysts),
            "no_suspensions": all((x["suspension_h"] or 0.0) == 0.0 for x in records),
            "no_pending_at_cutoff": sum(x["status"] == "pending" for x in records) == 0,
            "TP_FP_only_L2": all(x["level"] == "L2" for x in records if x["confusion"] in {"TP", "FP"}),
            "TN_FN_only_L1": all(x["level"] == "L1" for x in records if x["confusion"] in {"TN", "FN"}),
        },
        "notes": [
            "Synthetic historical-reference prevalence is the standardized test-label proxy 19/14449, not objective specialization need.",
            "Observed one-episode confusion counts are stochastic; q0 calibrates the population mean, not the finite-trace count.",
            "Queue counts are exact from arrivals and recorded service starts. Queued-work estimates use the minimum eligible forecast service; started-task residuals use recorded work segments and the environment's realized q.",
            "Utilization denominators are per-person continuously available hours during the 168-hour admission horizon; service completed during drain is reported separately in terminal work.",
            "Modeled quality per assignment is competence*(1-0.35*q), a synthetic proxy, not empirical correctness.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run_diagnostic(args.config, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "scenario_id", "seed", "generated_alerts", "confusion_counts", "route_counts",
        "capacity_lp", "observed_levels", "overall", "validation",
    )}, indent=2, ensure_ascii=False, sort_keys=True))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
