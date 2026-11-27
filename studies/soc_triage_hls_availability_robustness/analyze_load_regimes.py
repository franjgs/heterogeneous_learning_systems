"""Diagnose one seeded demand-regime episode without changing simulation logic."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend  # noqa: E402
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (  # noqa: E402
    CapacityDemandProfile, DemandRegime, assess_capacity,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario  # noqa: E402
from studies.soc_triage_hls_availability_robustness.triage_execution import run_triage_flow  # noqa: E402

DEFAULT_CONFIG = Path(__file__).with_name("config") / "SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json"


def diagnose(config: str | Path = DEFAULT_CONFIG, seed: int | None = None) -> dict:
    scenario = load_scenario(config)
    selected_seed = scenario.seed_start if seed is None else int(seed)
    triage, trace = scenario.triage_scenario_for(selected_seed)
    result = run_triage_flow(triage, flow_mode=scenario.flow_mode, backend=CalendarBackend())
    alerts = {x.alert_id: x for x in triage.alerts}
    trace_by_id = {x.routed.alert.alert_id: x for x in trace}
    stage_by_id = {
        aid: (level, task)
        for level, stage in result.stage_results.items()
        for aid, task in stage.tasks_by_alert.items()
    }
    segments = tuple(
        segment
        for stage in result.stage_results.values()
        for segment in (stage.work_segments or ())
    )

    def state_at(time_h: float, level: str) -> dict:
        queue = owned = remaining = 0.0
        for aid, (route, task) in stage_by_id.items():
            if route != level or alerts[aid].arrival > time_h:
                continue
            if task.completion is not None and task.completion <= time_h:
                continue
            if task.start is None or task.start > time_h:
                queue += 1
            else:
                owned += 1
                resource = next(
                    r for r in scenario.organization.resources_for(level)
                    if r.analyst.analyst_id == task.analyst_id
                )
                ref = triage.reference_escalation_by_alert[aid]
                rec = triage.recommendation_l2_by_alert[aid]
                multiplier = (triage.alpha if level == "L2" and rec and not ref else
                              triage.gamma if level == "L1" and ref and not rec else 1.0)
                q = triage.difficulty_by_alert[aid]
                difficulty_factor = 1.0 + triage.difficulty_service_beta * (q - 0.5)
                required = resource.service_by_class[alerts[aid].task_class] * difficulty_factor * multiplier
                done = sum(max(0.0, min(time_h, x.end) - x.start)
                           for x in segments if x.alert_id == aid)
                remaining += max(0.0, required - done)
        return {"queued_alerts": int(queue), "owned_unfinished_alerts": int(owned),
                "remaining_work_of_owned_h": remaining}

    regimes = tuple(scenario.demand_profile["regimes"])
    outcome_by_id = {x.alert_id: x for x in result.outcomes}
    per_regime = []
    for regime in regimes:
        name, start, end = regime["name"], float(regime["start_h"]), float(regime["end_h"])
        rows = [x for x in trace if start <= x.routed.alert.arrival < end]
        confusions = Counter()
        routes = Counter()
        by_class = Counter()
        for row in rows:
            aid = row.routed.alert.alert_id
            reference = triage.reference_escalation_by_alert[aid]
            recommendation = triage.recommendation_l2_by_alert[aid]
            confusion = ("TP" if reference and recommendation else
                         "FN" if reference else "FP" if recommendation else "TN")
            confusions[confusion] += 1
            routes["L2" if recommendation else "L1"] += 1
            by_class[str(row.routed.alert.task_class)] += 1
        work_by_level = {level: sum(
            (stage_by_id[x.routed.alert.alert_id][1].effective_work or 0.0)
            for x in rows
            if x.routed.alert.alert_id in stage_by_id and
            stage_by_id[x.routed.alert.alert_id][0] == level
        ) for level in ("L1", "L2")}
        interval_h = end - start
        staff_hours = {level: len(scenario.organization.resources_for(level)) * interval_h
                       for level in ("L1", "L2")}
        segments_worked = {level: sum(
            max(0.0, min(end, x.end) - max(start, x.start))
            for x in segments
            if x.analyst_id in {r.analyst.analyst_id for r in scenario.organization.resources_for(level)}
        ) for level in ("L1", "L2")}
        hourly_queue_max = {}
        for level in ("L1", "L2"):
            samples = [(t, state_at(t, level)["queued_alerts"])
                       for t in range(int(start), int(end) + 1)]
            maximum = max((n for _, n in samples), default=0)
            hourly_queue_max[level] = {
                "max_sampled_hourly_queue": maximum,
                "first_hour_at_max": next((t for t, n in samples if n == maximum), None),
            }
        cohort_outcomes = [outcome_by_id[x.routed.alert.alert_id] for x in rows]
        cohort_status = Counter(x.status for x in cohort_outcomes)
        cohort_completions = [x.completion for x in cohort_outcomes if x.completion is not None]
        per_regime.append({
            "name": name, "start_h": start, "end_h": end, "duration_h": interval_h,
            "configured_arrival_rates_by_class_per_h": dict(regime["arrival_rate_by_class"]),
            "configured_total_arrival_rate_per_h": sum(regime["arrival_rate_by_class"].values()),
            "realized_alerts": len(rows), "realized_total_rate_per_h": len(rows) / interval_h,
            "realized_routes": dict(routes),
            "realized_route_rates_per_h": {k: v / interval_h for k, v in routes.items()},
            "realized_confusion": {k: confusions.get(k, 0) for k in ("TP", "FP", "TN", "FN")},
            "sla_status_by_arrival_cohort": {k: cohort_status.get(k, 0) for k in ("completed_within_sla", "completed_late", "pending")},
            "latest_completion_h_of_arrival_cohort": max(cohort_completions) if cohort_completions else None,
            "realized_class_counts": dict(by_class),
            "realized_effective_work_by_arrival_cohort_h": work_by_level,
            "work_executed_in_interval_h_by_level": segments_worked,
            "available_staff_hours_by_level": staff_hours,
            "realized_utilization_by_level": {k: segments_worked[k] / staff_hours[k] for k in staff_hours},
            "hourly_queue": hourly_queue_max,
            "boundary_state_start": {level: state_at(start, level) for level in ("L1", "L2")},
            "boundary_state_end": {level: state_at(end, level) for level in ("L1", "L2")},
        })

    demand = scenario.demand_profile
    capacity_profile = CapacityDemandProfile(
        regimes=tuple(DemandRegime(r["name"], r["start_h"], r["end_h"],
                                   r["arrival_rate_by_class"])
                      for r in regimes),
        prevalence_by_class=demand["prevalence_by_class"],
        sensitivity_by_class=demand["sensitivity_by_class"],
        false_positive_rate_by_class=demand["false_positive_rate_by_class"],
        alpha=triage.alpha, beta=triage.difficulty_service_beta,
        gamma=triage.gamma, flow_mode=scenario.flow_mode,
    )
    capacity = assess_capacity(scenario.organization, capacity_profile)
    capacity_rows = [{
        "regime": row.regime, "level": row.level,
        "assignable_route_capacity_per_h": row.capacity_per_h,
        "expected_offered_route_rate_per_h": row.offered_rate_per_h,
        "relative_load": row.relative_load,
        "expected_work_h_person_per_h": row.offered_l1_work_h_per_h + row.offered_l2_work_h_per_h,
        "unstaffed_classes": list(row.unstaffed_classes),
        "binding_analysts_at_capacity": list(row.bottleneck_analysts),
    } for row in capacity.regimes]

    outcomes = result.outcomes
    late = [x for x in outcomes if x.status == "completed_late"]
    completed = [x for x in outcomes if x.completion is not None]
    return {
        "scenario_id": scenario.scenario_id, "config": str(config), "seed": selected_seed,
        "flow_mode": scenario.flow_mode, "policy": "per-level-configured-default",
        "admission_horizon_h": scenario.settings.admission_horizon,
        "evaluation_cutoff_h": result.cutoff, "generated_and_admitted_alerts": len(trace),
        "confusion_counts": dict(Counter(x.confusion for x in outcomes)),
        "route_counts": dict(Counter(x.final_investigation_level for x in outcomes)),
        "investigation_count_distribution": dict(Counter(x.investigation_count for x in outcomes)),
        "sla_status_counts": dict(result.status_counts),
        "late_by_route": dict(Counter(x.final_investigation_level for x in late)),
        "late_by_confusion": dict(Counter(x.confusion for x in late)),
        "late_by_severity": dict(Counter(trace_by_id[x.alert_id].severity for x in late)),
        "response_time_mean_h": sum(x.completion - alerts[x.alert_id].arrival
                                    for x in completed) / len(completed) if completed else None,
        "mean_pre_service_wait_h_by_level": {
            level: sum(task.start - alerts[aid].arrival for aid, (route, task) in stage_by_id.items()
                       if route == level and task.start is not None) /
                   max(1, sum(route == level and task.start is not None
                              for route, task in stage_by_id.values()))
            for level in ("L1", "L2")
        },
        "suspension_total_h_by_level": {
            level: sum(task.suspension or 0.0 for route, task in stage_by_id.values() if route == level)
            for level in ("L1", "L2")
        },
        "capacity_by_regime": capacity_rows,
        "realized_regimes": per_regime,
        "queue_snapshots_h": {
            str(t): {level: state_at(float(t), level) for level in ("L1", "L2")}
            for t in range(0, int(scenario.settings.admission_horizon) + 1, 6)
        },
        "recovery_check": {
            "criterion": "At recovery end, queued alerts and exact residual work of already assigned tasks are no greater than at pulse start; both queues are zero.",
            "state_at_pulse_start_h": {level: state_at(float(regimes[1]["start_h"]), level)
                                        for level in ("L1", "L2")},
            "state_at_recovery_end_h": {level: state_at(float(regimes[-1]["end_h"]), level)
                                         for level in ("L1", "L2")},
        },
        "caveat": "Queue work for not-yet-assigned alerts is represented by queue count, not fabricated realized service hours. Remaining-work hours are exact only for assigned unfinished tasks.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    print(json.dumps(diagnose(args.config, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
