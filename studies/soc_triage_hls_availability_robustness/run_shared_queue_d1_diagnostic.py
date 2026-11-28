"""Run and persist one reproducible D1 diagnostic for the shared-queue CONOPS.

This is a single seeded diagnostic execution, not a policy comparison or sweep.
The JSON artifact includes the synthetic input trace, assignments and queue
events so the organizational state can be reconstructed after the run.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
import platform
from typing import Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from studies.soc_triage_hls_availability_robustness.shared_queue import (  # noqa: E402
    ORDINARY,
    SPECIALIZED,
    assess_shared_capacity,
    generate_shared_trace,
    load_shared_scenario,
    run_shared_policy,
    split_task_class,
)
from studies.soc_triage_hls_availability_robustness.availability_engine import (  # noqa: E402
    CONTINUOUS,
)
from studies.soc_human_ai_organization.calibrate_a1_scenarios import (  # noqa: E402
    effective_capacity,
)


DEFAULT_OUTPUT = ROOT / "studies/soc_triage_hls_availability_robustness/results/SOC_SHARED_QUEUE_D1_DIAGNOSTIC_SEED_2026112801.json"


def _quantiles(values):
    if not values:
        return {"mean": None, "p50": None, "p90": None, "p95": None, "max": None}
    ordered = sorted(float(x) for x in values)
    def q(p):
        index = (len(ordered) - 1) * p
        lo, hi = int(index), min(int(index) + 1, len(ordered) - 1)
        return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)
    return {"mean": statistics.fmean(ordered), "p50": q(.50), "p90": q(.90),
            "p95": q(.95), "max": ordered[-1]}


def _confusion(contexts: Mapping):
    counts = Counter()
    for ctx in contexts.values():
        key = ("TP" if ctx.need_l2 and ctx.recommended_l2 else
               "FN" if ctx.need_l2 else
               "FP" if ctx.recommended_l2 else "TN")
        counts[key] += 1
    return {key: counts[key] for key in ("TP", "FP", "TN", "FN")}


def _queue_ledger(scenario, trace, result):
    horizon = scenario.source.settings.evaluation_horizon
    alerts = {a.alert_id: a for a in trace.alerts}
    assignments = {a.alert_id: a for a in result.assignments}
    arrival_at, start_at, complete_at = defaultdict(list), defaultdict(list), defaultdict(list)
    for alert in trace.alerts:
        if alert.arrival < scenario.source.settings.admission_horizon:
            arrival_at[alert.arrival].append(alert.alert_id)
    for assignment in result.assignments:
        if assignment.start <= horizon:
            start_at[assignment.start].append(assignment.alert_id)
        if assignment.completion <= horizon:
            complete_at[assignment.completion].append(assignment.alert_id)
    times = sorted({0.0, horizon, *arrival_at, *start_at, *complete_at})
    pending, busy = set(), {}
    events, timeline, bottlenecks = [], [], []
    queue_integral = Counter()
    max_queue = 0
    for index, now in enumerate(times):
        arrived = sorted(arrival_at.get(now, ()))
        for aid in arrived:
            pending.add(aid)
            events.append({"time_h": now, "event": "arrival", "alert_id": aid,
                           "queue_length_after": len(pending)})
            max_queue = max(max_queue, len(pending))
        completed = sorted(complete_at.get(now, ()))
        for aid in completed:
            assignment = assignments[aid]
            busy.pop(assignment.analyst_id, None)
            events.append({"time_h": now, "event": "completion", "alert_id": aid,
                           "analyst_id": assignment.analyst_id,
                           "queue_length_after": len(pending)})
        started = sorted(start_at.get(now, ()))
        for aid in started:
            pending.discard(aid)
            assignment = assignments[aid]
            busy[assignment.analyst_id] = aid
            events.append({"time_h": now, "event": "assignment_start", "alert_id": aid,
                           "analyst_id": assignment.analyst_id,
                           "queue_length_after": len(pending)})
        by_type = Counter(trace.context_by_alert[aid].research_type for aid in pending)
        free_juniors = [aid for aid, role in scenario.organization.role_by_analyst.items()
                        if role == "junior" and aid not in busy]
        free_seniors = [aid for aid, role in scenario.organization.role_by_analyst.items()
                        if role == "senior" and aid not in busy]
        specialized_pending = sorted(aid for aid in pending
                                    if trace.context_by_alert[aid].research_type == SPECIALIZED)
        timeline.append({"time_h": now, "queue_length": len(pending),
                         "ordinary_pending": by_type[ORDINARY],
                         "specialized_pending": by_type[SPECIALIZED],
                         "free_juniors": free_juniors, "free_seniors": free_seniors,
                         "busy_analysts": dict(busy)})
        if specialized_pending and not free_seniors and free_juniors:
            bottlenecks.append({"start_h": now, "specialized_alert_ids": specialized_pending,
                                "free_junior_ids": free_juniors,
                                "busy_senior_alerts": {aid: busy[aid] for aid, role in
                                    scenario.organization.role_by_analyst.items()
                                    if role == "senior" and aid in busy}})
        if index + 1 < len(times):
            end = times[index + 1]
            duration = max(0.0, end - now)
            queue_integral["all"] += len(pending) * duration
            queue_integral[ORDINARY] += by_type[ORDINARY] * duration
            queue_integral[SPECIALIZED] += by_type[SPECIALIZED] * duration
            if specialized_pending and not free_seniors and free_juniors:
                bottlenecks[-1]["end_h"] = end
                bottlenecks[-1]["duration_h"] = duration
    occupied_periods = []
    for assignment in result.assignments:
        ctx = trace.context_by_alert[assignment.alert_id]
        occupied_periods.append({"analyst_id": assignment.analyst_id,
                                 "role": scenario.organization.role(assignment.analyst_id),
                                 "alert_id": assignment.alert_id,
                                 "research_type": ctx.research_type,
                                 "start_h": assignment.start,
                                 "completion_h": assignment.completion})
    wait_while_senior_unavailable = Counter()
    for item in bottlenecks:
        start, end = item["start_h"], item.get("end_h", item["start_h"])
        for aid in item["specialized_alert_ids"]:
            alert = alerts[aid]
            assignment = assignments.get(aid)
            wait_end = assignment.start if assignment else horizon
            wait_while_senior_unavailable[aid] += max(0.0, min(end, wait_end) - max(start, alert.arrival))
    return {
        "events": events,
        "queue_timeline_after_dispatch": timeline,
        "queue_max_length_including_arrival_epochs": max_queue,
        "queue_area_alert_hours": dict(queue_integral),
        "time_weighted_mean_queue_length": queue_integral["all"] / horizon if horizon else 0,
        "senior_unavailable_while_junior_free_intervals": bottlenecks,
        "specialized_wait_hours_overlapping_those_intervals": dict(wait_while_senior_unavailable),
        "occupied_periods": occupied_periods,
    }


def _capacity_comparison(scenario):
    pooled = assess_shared_capacity(scenario)
    demand = scenario.source.demand_profile
    projects = tuple(demand["class_mix"])
    org = scenario.organization
    results = {}
    fractions = {ORDINARY: {}, SPECIALIZED: {}}
    role_resources = {
        "junior": [r for r in org.resources if org.role(r.analyst.analyst_id) == "junior"],
        "senior": [r for r in org.resources if org.role(r.analyst.analyst_id) == "senior"],
    }
    for project in projects:
        p = scenario.prevalence_by_project[project]
        se = float(demand["sensitivity_by_class"][project])
        fpr = float(demand["false_positive_rate_by_class"][project])
        ordinary = p * (1 - se) + (1 - p) * (1 - fpr)
        specialized = p * se + (1 - p) * fpr
        fractions[ORDINARY][project] = float(demand["class_mix"][project]) * ordinary
        fractions[SPECIALIZED][project] = float(demand["class_mix"][project]) * specialized
    separate_caps = {}
    for kind, role in ((ORDINARY, "junior"), (SPECIALIZED, "senior")):
        classes = tuple(f"{p}::{kind}" for p in projects)
        mass = sum(fractions[kind].values())
        shares = {f"{p}::{kind}": fractions[kind][p] / mass for p in projects}
        resources = role_resources[role]
        services = {r.analyst.analyst_id: {
            f"{project}::{kind}": r.forecast_service_by_class[f"{project}::{kind}"]
            for project in projects if f"{project}::{kind}" in r.analyst.eligible_classes
        } for r in resources}
        capacity = effective_capacity([r.analyst for r in resources], services,
                                      shares, classes=classes,
                                      capacity_by_analyst={r.analyst.analyst_id:
                                          sum(end - start for _, start, end in
                                              (r.calendar or CONTINUOUS).windows) / 168
                                          for r in resources})
        separate_caps[kind] = {
            "routed_fraction_of_all_alerts": mass,
            "routed_task_capacity_per_h": capacity["max_common_arrivals_per_h"],
            "implied_total_alert_capacity_per_h": capacity["max_common_arrivals_per_h"] / mass,
        }
    separate_system = min(x["implied_total_alert_capacity_per_h"]
                          for x in separate_caps.values())
    source_rate = float(demand["arrival_intensity_total_per_h"])
    return {
        "shared_pool_lp": {
            "maximum_total_alerts_per_h": pooled.maximum_arrivals_per_h,
            "source_rate_per_h": source_rate,
            "source_rate_as_fraction_of_capacity": source_rate / pooled.maximum_arrivals_per_h,
            "utilization_by_analyst_at_capacity": dict(pooled.utilization_by_analyst_at_capacity),
            "method": pooled.method,
        },
        "previous_separate_pool_theoretical_reference": {
            "ordinary_pool": separate_caps[ORDINARY],
            "specialized_pool": separate_caps[SPECIALIZED],
            "system_maximum_total_alerts_per_h": separate_system,
            "pooled_capacity_multiple_of_separated": pooled.maximum_arrivals_per_h / separate_system,
            "interpretation": "Analytical LP only, with the same profiles and route mix; no second simulation or policy comparison.",
        },
    }


def build_diagnostic(scenario, trace, result):
    if result.policy != "D1":
        raise ValueError("diagnostic accepts only D1")
    alerts = {a.alert_id: a for a in trace.alerts}
    contexts = trace.context_by_alert
    assignments = {x.alert_id: x for x in result.assignments}
    if len(assignments) != len(result.assignments):
        raise RuntimeError("duplicate alert investigations in D1 result")
    horizon = scenario.source.settings.evaluation_horizon
    admission = scenario.source.settings.admission_horizon
    people = {}
    resources = {r.analyst.analyst_id: r for r in scenario.organization.resources}
    def active_work(assignment, cutoff):
        if assignment is None:
            return 0.0
        return max(0.0, min(assignment.completion, cutoff) - max(assignment.start, 0.0))

    for aid, resource in resources.items():
        own = [x for x in result.assignments if x.analyst_id == aid]
        role = scenario.organization.role(aid)
        project_counts, severity_counts, type_counts = Counter(), Counter(), Counter()
        work_project, work_severity, work_type = Counter(), Counter(), Counter()
        assigned_competence, modeled_quality = [], []
        for assignment in own:
            ctx = contexts[assignment.alert_id]
            project_counts[ctx.project] += 1
            severity_counts[ctx.severity] += 1
            type_counts[ctx.research_type] += 1
            hours = active_work(assignment, horizon)
            work_project[ctx.project] += hours
            work_severity[ctx.severity] += hours
            work_type[ctx.research_type] += hours
            assigned_competence.append(assignment.competence)
            modeled_quality.append(max(0.0, min(1.0,
                assignment.competence * (1 - .35 * ctx.difficulty))))
        base_profile = {split_task_class(k)[0] + "::" + split_task_class(k)[1]: v
                        for k, v in resource.service_by_class.items()}
        forecast_profile = {k: v for k, v in resource.forecast_service_by_class.items()}
        people[aid] = {
            "role": role,
            "eligibility": sorted(resource.analyst.eligible_classes),
            "competence_by_project_and_type": dict(resource.analyst.competence),
            "base_service_h_by_project_and_type_at_q_0_5": base_profile,
            "expected_forecast_service_h_by_type_project": forecast_profile,
            "investigations": len(own),
            "investigations_completed_by_cutoff": sum(x.completion <= horizon for x in own),
            "active_work_h": sum(active_work(x, horizon) for x in own),
            "active_work_h_during_admission": sum(active_work(x, admission) for x in own),
            "utilization_admission_window": sum(active_work(x, admission) for x in own) / admission,
            "utilization_evaluation_window": sum(active_work(x, horizon) for x in own) / horizon,
            "investigations_by_project": dict(project_counts),
            "investigations_by_severity": dict(severity_counts),
            "investigations_by_research_type": dict(type_counts),
            "active_work_h_by_project": dict(work_project),
            "active_work_h_by_severity": dict(work_severity),
            "active_work_h_by_research_type": dict(work_type),
            "mean_assigned_competence": statistics.fmean(assigned_competence) if own else None,
            "mean_modelled_correctness": statistics.fmean(modeled_quality) if own else None,
        }

    alert_rows, sla_late_rows = [], []
    work_quantities = {"ordinary": 0.0, "specialized": 0.0}
    for aid, alert in alerts.items():
        ctx = contexts[aid]
        assignment = assignments.get(aid)
        if assignment:
            service = active_work(assignment, horizon)
            started = assignment.start <= horizon
            wait = (assignment.start - alert.arrival if started else
                    max(0.0, horizon - alert.arrival))
            completed = assignment.completion <= horizon
            total = assignment.completion - alert.arrival if completed else None
            status = ("pending" if not completed else
                      "within_sla" if assignment.completion <= alert.deadline else "late")
            work_quantities[ctx.research_type] += service
        else:
            service = total = None
            wait = max(0.0, horizon - alert.arrival)
            status = "pending"
        profile = [r.forecast_service_by_class[alert.task_class]
                   for r in scenario.organization.resources
                   if alert.task_class in r.analyst.eligible_classes]
        expected_offered = statistics.fmean(profile) if profile else None
        alert_rows.append({
            "alert_id": aid, "project": ctx.project, "severity": ctx.severity,
            "difficulty_q": ctx.difficulty, "need_l2_reference": ctx.need_l2,
            "recommended_l2": ctx.recommended_l2, "investigation_type": ctx.research_type,
            "arrival_h": alert.arrival, "deadline_absolute_h": alert.deadline,
            "assigned_analyst_id": assignment.analyst_id if assignment else None,
            "assigned_role": scenario.organization.role(assignment.analyst_id) if assignment else None,
            "start_h": assignment.start if assignment and assignment.start <= horizon else None,
            "completion_h": (assignment.completion if assignment and
                             assignment.completion <= horizon else None),
            "planned_completion_h": assignment.completion if assignment else None,
            "wait_h": wait, "active_service_h": service, "resolution_total_h": total,
            "sla_status": status, "expected_offered_service_h_mean_eligible": expected_offered,
            "competence": assignment.competence if assignment else None,
            "modelled_correctness_probability": (max(0.0, min(1.0,
                assignment.competence * (1 - .35 * ctx.difficulty))) if assignment else None),
            "investigation_count": int(assignment is not None),
        })
        if status == "late":
            budget = alert.deadline - alert.arrival
            cause = ("service_exceeds_entire_deadline_budget" if service > budget
                     else "waiting_consumed_service_margin")
            sla_late_rows.append({"alert_id": aid, "severity": ctx.severity,
                                  "investigation_type": ctx.research_type,
                                  "wait_h": wait, "service_h": service,
                                  "resolution_h": total, "deadline_budget_h": budget,
                                  "lateness_h": total - budget, "primary_decomposition": cause})

    by_project_severity = Counter((ctx.project, ctx.severity) for ctx in contexts.values())
    by_project_type = Counter((ctx.project, ctx.research_type) for ctx in contexts.values())
    by_severity_type = Counter((ctx.severity, ctx.research_type) for ctx in contexts.values())
    assignment_competence = defaultdict(list)
    role_assignment_counts = defaultdict(Counter)
    for assignment in result.assignments:
        if assignment.start > horizon:
            continue
        ctx = contexts[assignment.alert_id]
        assignment_competence[(ctx.project, ctx.research_type)].append(assignment.competence)
        role_assignment_counts[(ctx.project, ctx.research_type)][
            scenario.organization.role(assignment.analyst_id)] += 1
    specialization_by_project_type = {}
    for project in scenario.source.demand_profile["class_mix"]:
        for kind in (ORDINARY, SPECIALIZED):
            key = f"{project}|{kind}"
            task = f"{project}::{kind}"
            eligible = [r for r in scenario.organization.resources
                        if task in r.analyst.eligible_classes]
            available_comp = [float(r.analyst.competence[task]) for r in eligible]
            available_service = [float(r.service_by_class[task]) for r in eligible]
            available_forecast = [float(r.forecast_service_by_class[task]) for r in eligible]
            assigned = assignment_competence[(project, kind)]
            specialization_by_project_type[key] = {
                "eligible_professionals": len(eligible),
                "eligible_roles": dict(Counter(scenario.organization.role(r.analyst.analyst_id)
                                               for r in eligible)),
                "competence_available_min": min(available_comp) if available_comp else None,
                "competence_available_median": statistics.median(available_comp) if available_comp else None,
                "competence_available_max": max(available_comp) if available_comp else None,
                "mean_competence_assigned_by_D1": statistics.fmean(assigned) if assigned else None,
                "assigned_professionals_by_role": dict(role_assignment_counts[(project, kind)]),
                "base_service_h_q_0_5_min_median_max": ([min(available_service), statistics.median(available_service), max(available_service)] if available_service else []),
                "expected_forecast_service_h_min_median_max": ([min(available_forecast), statistics.median(available_forecast), max(available_forecast)] if available_forecast else []),
                "interpretation": "Competence/service range describes modeled profiles; assignment averages are D1 outcomes, not observed human performance.",
            }
    by_confusion = _confusion(contexts)
    queue = _queue_ledger(scenario, trace, result)
    senior_unavailable_wait = queue["specialized_wait_hours_overlapping_those_intervals"]
    for row in sla_late_rows:
        row["wait_h_without_free_senior_while_junior_free"] = senior_unavailable_wait.get(
            row["alert_id"], 0.0)
    waits = [a["wait_h"] for a in alert_rows if a["wait_h"] is not None]
    services = [a["active_service_h"] for a in alert_rows if a["active_service_h"] is not None]
    resolutions = [a["resolution_total_h"] for a in alert_rows if a["resolution_total_h"] is not None]
    executed_total = sum(work_quantities.values())
    staff_count = len(scenario.organization.resources)
    by_analyst_assignments = defaultdict(list)
    for assignment in result.assignments:
        by_analyst_assignments[assignment.analyst_id].append(assignment)
    nonoverlap = all(
        left.completion <= right.start
        for rows in by_analyst_assignments.values()
        for left, right in zip(sorted(rows, key=lambda x: (x.start, x.completion)),
                               sorted(rows, key=lambda x: (x.start, x.completion))[1:])
    )
    type_matches_triage = all(
        (contexts[alert.alert_id].research_type == SPECIALIZED) ==
        contexts[alert.alert_id].recommended_l2 for alert in trace.alerts
    )
    eligibility_holds = all(
        alert.task_class in resources[assignment.analyst_id].analyst.eligible_classes
        and not (scenario.organization.role(assignment.analyst_id) == "junior" and
                 contexts[assignment.alert_id].research_type == SPECIALIZED)
        for assignment in result.assignments
        for alert in (alerts[assignment.alert_id],)
    )
    deadline_offsets = scenario.source.settings.deadlines.offsets_by_severity_h
    deadlines_preserved = all(
        abs(alert.deadline - (alert.arrival + deadline_offsets[contexts[alert.alert_id].severity])) < 1e-9
        for alert in trace.alerts
    )
    individual_assignment_count = sum(row["investigations"] for row in people.values())
    individual_work_total = sum(row["active_work_h"] for row in people.values())
    validation = {
        "single_shared_queue": scenario.organization.queue_name == "shared_alert_queue",
        "one_assignment_per_alert": len(assignments) == len(trace.alerts) and
                                     len(assignments) == len(result.assignments) and
                                     set(assignments).issubset(alerts),
        "no_duplicate_or_second_investigation": len(assignments) == len(set(assignments)),
        "no_transfers_or_reescalations": len(assignments) <= len(trace.alerts),
        "junior_specialized_assignments": sum(
            1 for assignment in result.assignments
            if scenario.organization.role(assignment.analyst_id) == "junior" and
            contexts[assignment.alert_id].research_type == SPECIALIZED),
        "all_assignments_eligible": eligibility_holds,
        "no_analyst_overlap": nonoverlap,
        "one_investigation_type_matches_recommendation": type_matches_triage,
        "deadlines_unchanged_from_severity_offsets": deadlines_preserved,
        "individual_and_aggregate_assignment_counts_match": individual_assignment_count == len(result.assignments),
        "individual_and_aggregate_work_h_match": abs(individual_work_total - executed_total) < 1e-8,
        "pending_alerts_at_cutoff": result.pending_at_cutoff,
    }
    validation["all_checks_pass"] = (
        validation["single_shared_queue"] and validation["one_assignment_per_alert"] and
        validation["no_duplicate_or_second_investigation"] and
        validation["no_transfers_or_reescalations"] and
        validation["junior_specialized_assignments"] == 0 and
        validation["all_assignments_eligible"] and validation["no_analyst_overlap"] and
        validation["one_investigation_type_matches_recommendation"] and
        validation["deadlines_unchanged_from_severity_offsets"] and
        validation["individual_and_aggregate_assignment_counts_match"] and
        validation["individual_and_aggregate_work_h_match"] and
        validation["pending_alerts_at_cutoff"] == 0
    )
    if not validation["all_checks_pass"]:
        raise AssertionError(f"shared queue diagnostic validation failed: {validation}")
    return {
        "scenario_id": scenario.scenario_id,
        "configuration_path": str(scenario.config_path.relative_to(ROOT)),
        "policy": "D1",
        "seed": scenario.source.settings.seed,
        "admission_horizon_h": admission,
        "evaluation_horizon_h": horizon,
        "queue_name": scenario.organization.queue_name,
        "roster": {"junior": 5, "senior": 3, "total": 8,
                   "availability": "all individual calendars 24x7"},
        "model": {"investigations_per_alert": 1, "transfers": False,
                  "source_prevalence_by_project": dict(scenario.source.demand_profile["prevalence_by_class"]),
                  "configured_prevalence_by_project": dict(scenario.prevalence_by_project),
                  "sensitivity_by_project": dict(scenario.source.demand_profile["sensitivity_by_class"]),
                  "fpr_by_project": dict(scenario.source.demand_profile["false_positive_rate_by_class"]),
                  "alpha": float(scenario.source.generation["parameters"].get("alpha", 1)),
                  "difficulty_service_beta": float(scenario.source.generation["parameters"].get("difficulty_service_beta", 0)),
                  "gamma": float(scenario.source.generation["parameters"].get("gamma", 1)),
                  "severity_mix": dict(scenario.source.demand_profile["severity_mix"]),
                  "deadlines_by_severity_h": dict(scenario.source.settings.deadlines.offsets_by_severity_h),
                  "project_mix": dict(scenario.source.demand_profile["class_mix"])},
        "demand": {
            "generated_alerts": len(alert_rows),
            "admitted_alerts": sum(a["arrival_h"] < admission for a in alert_rows),
            "realized_arrival_intensity_per_h": sum(a["arrival_h"] < admission for a in alert_rows) / admission,
            "counts_by_project": dict(Counter(c.project for c in contexts.values())),
            "counts_by_severity": dict(Counter(c.severity for c in contexts.values())),
            "counts_by_project_severity": {f"{k[0]}|{k[1]}": v for k, v in by_project_severity.items()},
            "counts_by_project_research_type": {f"{k[0]}|{k[1]}": v for k, v in by_project_type.items()},
            "counts_by_severity_research_type": {f"{k[0]}|{k[1]}": v for k, v in by_severity_type.items()},
            "confusion_counts": by_confusion,
            "confusion_fractions": {key: value / len(alert_rows) if alert_rows else 0
                                    for key, value in by_confusion.items()},
            "realized_need_l2_prevalence": (by_confusion["TP"] + by_confusion["FN"]) / len(alert_rows),
            "realized_l2_recommendation_fraction": (by_confusion["TP"] + by_confusion["FP"]) / len(alert_rows),
            "ordinary_investigations": sum(c.research_type == ORDINARY for c in contexts.values()),
            "specialized_investigations": sum(c.research_type == SPECIALIZED for c in contexts.values()),
            "offered_work_h_by_type_expected_mean_eligible": dict(result.offered_work_by_type_h),
            "executed_work_h_by_type": work_quantities,
        },
        "individual_analysts": people,
        "aggregate": {
            "investigations_assigned": len(assignments),
            "pending_at_evaluation_cutoff": result.pending_at_cutoff,
            "queue_length_at_evaluation_cutoff": result.queue_length_at_cutoff,
            "maximum_queue_length": queue["queue_max_length_including_arrival_epochs"],
            "utilization_by_analyst": dict(result.utilization_by_analyst),
            "utilization_by_role": dict(result.utilization_by_role),
            "utilization_global_evaluation_horizon": executed_total / (staff_count * horizon),
            "utilization_global_admission_horizon": executed_total / (staff_count * admission),
            "executed_work_h_by_role_and_type": dict(result.service_work_by_role_type_h),
            "closures_by_type": dict(result.closures_by_type),
            "work_offered_minus_executed_h_by_type": {
                kind: result.offered_work_by_type_h[kind] - work_quantities[kind]
                for kind in (ORDINARY, SPECIALIZED)},
            "wait_h": _quantiles(waits), "active_service_h": _quantiles(services),
            "resolution_total_h": _quantiles(resolutions),
            "sla_by_severity_and_type": [vars(x) for x in result.sla_by_severity_type],
            "late_alert_causes": sla_late_rows,
            "modelled_correctness_probability_by_type": dict(result.expected_quality_by_type),
            "competence_and_speed_by_project_type": specialization_by_project_type,
        },
        "validation": validation,
        "capacity": _capacity_comparison(scenario),
        "queue_diagnostics": queue,
        "alerts": alert_rows,
    }


def run_once(output: str | Path = DEFAULT_OUTPUT, *, seed: int | None = None) -> dict:
    scenario = load_shared_scenario()
    if scenario.policy_default != "D1":
        raise ValueError("diagnostic configuration default must be D1")
    if seed is None:
        seed = scenario.source.settings.seed
    trace = generate_shared_trace(scenario, seed)
    result = run_shared_policy(scenario, trace, policy="D1")
    report = build_diagnostic(scenario, trace, result)
    report["seed"] = seed
    source_config = scenario.source
    report["reproducibility"] = {
        "python_version": platform.python_version(),
        "shared_config_sha256": sha256(scenario.config_path.read_bytes()).hexdigest(),
        "source_scenario_config_sha256": sha256(
            (scenario.config_path.parent / "SOC_NEW_MODEL_CONOPS_REFERENCE_SOCTRA_SEVERITY_V1.json").read_bytes()
        ).hexdigest(),
        "runner_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_scenario_id": source_config.scenario_id,
        "seed": seed,
        "policy": "D1",
    }
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                   encoding="utf-8")
    return report


def main() -> None:
    report = run_once()
    print(json.dumps({"output": str(DEFAULT_OUTPUT),
                      "seed": report["seed"],
                      "generated": report["demand"]["generated_alerts"],
                      "confusion": report["demand"]["confusion_counts"],
                      "sla": report["aggregate"]["sla_by_severity_and_type"],
                      "capacity": report["capacity"]}, indent=2))


if __name__ == "__main__":
    main()
