"""Paired, exploratory sizing runs for the SOC D1/P1-P5 study.

Outputs are aggregate-only local artifacts. This script uses synthetic arrivals
and the existing simulators; it does not read SOCTRA records or tune a policy.
Run from the repository root with ``python studies/soc_human_ai_organization/calibrate_a1_scenarios.py``.
"""
from __future__ import annotations

import argparse
import csv
from functools import lru_cache
import json
import math
from pathlib import Path
import statistics
import sys
import time
from collections.abc import Mapping

from scipy.optimize import linprog
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from hls.ia_l1_l2_simulation import ScenarioConfig, SimulatedAlert, generate_alerts  # noqa: E402
from hls.rq1_allocation import (  # noqa: E402
    AllocationSession,
    Analyst,
    SOC_POLICY_NAMES,
    _dispatch_local_capacity,
    _dispatch_soc_policy,
)
from hls.rq1_l1_l2 import RoutedAlert, simulate_l1_l2  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    AI_FALSE_POSITIVE_RATE,
    AI_SENSITIVITY,
    BASE_DEADLINES_H,
    BASE_ELIGIBILITY,
    BASE_L1_ANALYSTS,
    BASE_L2_ANALYSTS,
    BASE_SERVICE_L1_H,
    BASE_SERVICE_L2_H,
    ELIGIBILITY_LEVELS,
    ESCALATION_NEED_BY_PROJECT,
    L1_COMPETENCE,
    L1_SPEED,
    L2_COMPETENCE,
    L2_SPEED,
    PRIORITIES,
    PRIORITY_PROBABILITIES,
    PROJECTS,
    PROJECT_MIX,
    build_roster,
)


CONFIG_PATH = Path(__file__).with_name("config") / "a1_calibration.json"
POLICIES = SOC_POLICY_NAMES


def read_config(path: Path = CONFIG_PATH) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if tuple(config["policies"]) != tuple(POLICIES):
        raise ValueError(f"policy list must be exactly {POLICIES}")
    return config


def build_scenario(config: dict, *, rate: float, deadline_multiplier: float = 1.0,
                   escalation_multiplier: float = 1.0,
                   burst: tuple[float, float, float] | None = None) -> ScenarioConfig:
    deadlines = tuple((name, hours * deadline_multiplier) for name, hours in BASE_DEADLINES_H)
    escalation = tuple(min(1.0, value * escalation_multiplier) for value in ESCALATION_NEED_BY_PROJECT)
    if burst and config["burst_control"]["expected_total_arrivals_held_constant"]:
        duration, multiplier = burst[1] - burst[0], burst[2]
        rate = rate * 24.0 / (24.0 + duration * (multiplier - 1.0))
    return ScenarioConfig(
        horizon=config["model"]["admission_horizon_h"],
        arrival_rate=rate,
        classes=PROJECTS,
        class_probabilities=PROJECT_MIX,
        severity_probabilities=PRIORITY_PROBABILITIES,
        escalation_probability_by_class=escalation,
        deadline_by_severity=deadlines,
        burst_window=burst,
        ai_sensitivity=AI_SENSITIVITY,
        ai_false_positive_rate=AI_FALSE_POSITIVE_RATE,
        difficulty_beta=tuple(config["model"]["difficulty_beta_assumed"]),
    )


def build_team(*, eligibility_level: float = BASE_ELIGIBILITY,
               homogeneous_competence: bool = False,
               homogeneous_speed: bool = False):
    """Build the fixed reference roster or a controlled homogeneity ablation."""
    l1, l2, l1_service, l2_service = build_roster(
        BASE_L1_ANALYSTS, BASE_L2_ANALYSTS, eligibility_level,
    )
    if homogeneous_competence:
        l1 = tuple(Analyst(a.analyst_id, a.eligible_classes,
                           {k: 0.80 for k in a.eligible_classes}) for a in l1)
        l2 = tuple(Analyst(a.analyst_id, a.eligible_classes,
                           {k: 0.80 for k in a.eligible_classes}) for a in l2)
    if homogeneous_speed:
        l1_service = {
            a.analyst_id: {k: BASE_SERVICE_L1_H[k] for k in a.eligible_classes}
            for a in l1
        }
        l2_service = {
            a.analyst_id: {k: BASE_SERVICE_L2_H[k] for k in a.eligible_classes}
            for a in l2
        }
    return l1, l2, l1_service, l2_service


def effective_capacity(analysts, service_by_analyst_class, class_shares, *,
                       classes=None, capacity_by_analyst=None) -> dict:
    """Fluid LP: maximize arrival rate under class mix, eligibility and staff time.

    The historical three-argument interface retains its original SOC classes and
    one service-hour per analyst-hour. Generic diagnostics may supply another
    class vocabulary and available fractions (for example, a weekly calendar).
    """
    classes = tuple(PROJECTS if classes is None else classes)
    if isinstance(class_shares, Mapping):
        shares = tuple(float(class_shares[task_class]) for task_class in classes)
    else:
        shares = tuple(float(value) for value in class_shares)
        if len(shares) != len(classes):
            raise ValueError("class_shares length must match classes")
    capacities_by_analyst = capacity_by_analyst or {}
    eligible_edges = [
        (i, k) for i, analyst in enumerate(analysts)
        for k, task_class in enumerate(classes)
        if task_class in analyst.eligible_classes
    ]
    n_edges = len(eligible_edges)
    objective = [0.0] * n_edges + [-1.0]
    equalities, targets = [], []
    for k, share in enumerate(shares):
        equalities.append([float(kk == k) for _, kk in eligible_edges] + [-share])
        targets.append(0.0)
    capacities, limits = [], []
    for i, analyst in enumerate(analysts):
        capacities.append([
            service_by_analyst_class[analyst.analyst_id][classes[k]] if ii == i else 0.0
            for ii, k in eligible_edges
        ] + [0.0])
        capacity = float(capacities_by_analyst.get(analyst.analyst_id, 1.0))
        if not math.isfinite(capacity) or capacity < 0:
            raise ValueError("capacity_by_analyst values must be finite and nonnegative")
        limits.append(capacity)
    solution = linprog(
        objective, A_ub=capacities, b_ub=limits,
        A_eq=equalities, b_eq=targets,
        bounds=[(0.0, None)] * (n_edges + 1), method="highs",
    )
    if not solution.success:
        raise RuntimeError(f"capacity LP failed: {solution.message}")
    rate = float(solution.x[-1])
    utilizations = []
    for i, analyst in enumerate(analysts):
        workload = sum(
            solution.x[e] * service_by_analyst_class[analyst.analyst_id][classes[k]]
            for e, (ii, k) in enumerate(eligible_edges) if ii == i
        )
        cap = float(capacities_by_analyst.get(analyst.analyst_id, 1.0))
        utilizations.append((analyst.analyst_id, workload / cap if cap else 0.0))
    return {"max_common_arrivals_per_h": rate, "class_shares": list(shares),
            "fluid_utilization_at_capacity": utilizations,
            "method": "fractional flow LP; each analyst has one service-hour per hour"}


def routed_l2_shares(class_shares=PROJECT_MIX,
                     need=ESCALATION_NEED_BY_PROJECT) -> tuple[float, tuple[float, ...]]:
    """Return expected recommendation probability per input alert and routed mix."""
    probs = tuple(p * AI_SENSITIVITY + (1.0 - p) * AI_FALSE_POSITIVE_RATE for p in need)
    weighted = tuple(class_shares[k] * probs[k] for k in range(len(class_shares)))
    routed_share = sum(weighted)
    return routed_share, tuple(value / routed_share for value in weighted)


def expected_workloads(rate: float, class_shares, need, l1_service, l2_service,
                       l1_analysts, l2_analysts) -> dict:
    routed_fraction, routed_mix = routed_l2_shares(class_shares, need)
    l1_minutes_per_hour = sum(
        rate * class_shares[k] * sum(
            l1_service[a.analyst_id][PROJECTS[k]] for a in l1_analysts
            if PROJECTS[k] in a.eligible_classes
        ) / sum(PROJECTS[k] in a.eligible_classes for a in l1_analysts)
        for k in range(len(PROJECTS))
    )
    l2_rate = rate * routed_fraction
    l2_work = sum(
        l2_rate * routed_mix[k] * sum(
            l2_service[a.analyst_id][PROJECTS[k]] for a in l2_analysts
            if PROJECTS[k] in a.eligible_classes
        ) / sum(PROJECTS[k] in a.eligible_classes for a in l2_analysts)
        for k in range(len(PROJECTS))
    )
    return {"expected_l1_offered_analyst_hours_per_h": l1_minutes_per_hour,
            "expected_l2_recommendations_per_h": l2_rate,
            "expected_l2_offered_analyst_hours_per_h": l2_work,
            "expected_recommendation_fraction": routed_fraction,
            "routed_class_mix": list(routed_mix)}


def matching_count(free, pending) -> tuple[int, int]:
    """Count maximum-cardinality feasible one-to-one assignments in current state."""
    classes = tuple(PROJECTS)
    counts = tuple(sum(a.task_class == task for a in pending.values()) for task in classes)
    ids = tuple(sorted(free, key=lambda a: a.analyst_id))

    @lru_cache(None)
    def visit(i, used):
        if i == len(ids):
            return 0, 1
        best, ways = visit(i + 1, used)  # leave this analyst idle
        analyst = ids[i]
        for k, task_class in enumerate(classes):
            if task_class not in analyst.eligible_classes or used[k] >= counts[k]:
                continue
            nxt = list(used)
            choices = counts[k] - used[k]
            nxt[k] += 1
            size, count = visit(i + 1, tuple(nxt))
            size += 1
            count *= choices
            if size > best:
                best, ways = size, count
            elif size == best:
                ways += count
        return best, ways

    return visit(0, (0,) * len(classes))


def _proposal_metrics(pairs, now, service_time):
    return (sum(now + service_time(a, x) <= x.deadline for a, x in pairs),
            len(pairs), sum(a.competence[x.task_class] for a, x in pairs))


def inspect_stage(alerts, analysts, services, analyst_services, *, horizon, drain,
                  seed, latency=0.0, edge_cost=0.0) -> list[dict]:
    """Run D1 with read-only same-state P3/P4 previews and event diagnostics."""
    session = AllocationSession(
        alerts, analysts, services, admission_horizon=horizon, drain_period=drain,
        random_seed=seed, coordination_latency=latency,
        coordination_edge_cost=edge_cost, diagnostic_d1=True,
        service_by_analyst_class=analyst_services,
    )
    rows = []
    while not session._finalized:
        event = session.next_event_time()
        if event is None:
            break
        session.advance_to(event)
        if not session.can_dispatch():
            continue
        free = session.available_analysts()
        pending = dict(session.pending)
        edge_count = sum(x.task_class in a.eligible_classes for a in free for x in pending.values())
        eligible_per_alert = [sum(x.task_class in a.eligible_classes for a in free)
                              for x in pending.values()]
        max_size, max_ways = matching_count(free, pending)
        service = session._service_time
        p3, _, _ = _dispatch_soc_policy(
            "P3", free, pending, session.services, session.now, service,
            session.individual_services, session.order_rng, latency, edge_cost,
        )
        p4, _, _ = _dispatch_soc_policy(
            "P4", free, pending, session.services, session.now, service,
            session.individual_services, session.order_rng, latency, edge_cost,
        )
        p3_metrics = _proposal_metrics(p3, session.now, service)
        p4_metrics = _proposal_metrics(p4, session.now + latency, service)
        p3_pairs = {(a.analyst_id, x.alert_id) for a, x in p3}
        p4_pairs = {(a.analyst_id, x.alert_id) for a, x in p4}
        alert_competence_spreads = []
        for alert in pending.values():
            values = [a.competence[alert.task_class] for a in free
                      if alert.task_class in a.eligible_classes]
            if len(values) > 1:
                alert_competence_spreads.append(max(values) - min(values))
        pending_classes = {x.task_class for x in pending.values()}
        free_counts = {task: sum(task in a.eligible_classes for a in free)
                       for task in pending_classes}
        occupied_counts = {
            task: sum(task in next(a for a in session.analysts if a.analyst_id == aid).eligible_classes
                      for aid in session.running)
            for task in pending_classes
        }
        blocking = 0
        for analyst, selected in p3:
            for task in pending_classes - {selected.task_class}:
                if task in analyst.eligible_classes and free_counts.get(task) == 1:
                    blocking += 1
                    break
        rows.append({
            "time_h": session.now,
            "free_analysts": len(free),
            "pending_alerts": len(pending),
            "eligible_edges": edge_count,
            "alerts_with_multiple_eligible_analysts": sum(x > 1 for x in eligible_per_alert),
            "classes_with_pending_and_one_free_eligible": sum(free_counts[k] == 1 for k in pending_classes),
            "occupied_analyst_pending_class_eligibility_edges": sum(occupied_counts.values()),
            "max_feasible_simultaneous_assignments": max_size,
            "max_cardinality_assignment_alternatives": max_ways,
            "mean_competence_range_over_multi_eligible_alerts": (
                statistics.mean(alert_competence_spreads) if alert_competence_spreads else 0.0
            ),
            "max_competence_range_over_multi_eligible_alerts": (
                max(alert_competence_spreads, default=0.0)
            ),
            "p3_p4_pairing_differs": p3_pairs != p4_pairs,
            "p4_strictly_improves_p3_on_time_count_or_cardinality": p4_metrics[:2] > p3_metrics[:2],
            "p3_predicted_on_time": p3_metrics[0],
            "p4_predicted_on_time": p4_metrics[0],
            "p3_assignments": p3_metrics[1],
            "p4_assignments": p4_metrics[1],
            "p3_predicted_competence_sum": p3_metrics[2],
            "p4_predicted_competence_sum": p4_metrics[2],
            "p3_potential_specialist_blocking_choices": blocking,
        })
        session.dispatch("D1")
    return rows


def run_cell(config: dict, cell: dict, seeds: list[int], *, drain: float | None = None,
             policies: tuple[str, ...] = POLICIES) -> tuple[list[dict], list[dict]]:
    l1, l2, l1_services, l2_services = build_team(
        eligibility_level=cell.get("eligibility_level", BASE_ELIGIBILITY),
        homogeneous_competence=cell.get("competence") == "homogeneous",
        homogeneous_speed=cell.get("speed") == "homogeneous",
    )
    base_capacity = cell.get("capacity_l1", config.get("capacity_l1_alerts_per_h"))
    rate = cell.get("arrival_rate_per_h")
    if rate is None:
        rate = base_capacity * cell.get("load_multiplier", 1.0)
    burst = cell.get("burst_window")
    scenario = build_scenario(
        config, rate=rate, deadline_multiplier=cell.get("deadline_multiplier", 1.0),
        escalation_multiplier=cell.get("escalation_multiplier", 1.0),
        burst=tuple(burst) if burst else None,
    )
    drain_h = config["model"].get("candidate_drain_h", 24.0) if drain is None else drain
    episode_rows, diagnostic_rows = [], []
    for seed in seeds:
        generated = generate_alerts(scenario, seed)
        routed = tuple(row.routed for row in generated)
        for policy in policies:
            start = time.perf_counter()
            result = simulate_l1_l2(
                routed, l1, l2, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
                policy=policy, admission_horizon=scenario.horizon,
                drain_period=drain_h, coordination_latency=cell.get("latency_h", 0.0),
                coordination_edge_cost=cell.get("edge_cost_units", 0.0),
                decision_mode="hypothetical_recommendation_acceptance",
                random_seed=seed, l1_service_by_analyst_class=l1_services,
                l2_service_by_analyst_class=l2_services,
            )
            elapsed = time.perf_counter() - start
            h, end = result.at_horizon, result.after_drain
            l1_jobs = {job.alert_id: job for job in result.l1_simulation.assignments}
            l2_jobs = {job.alert_id: job for job in result.l2_simulation.assignments}
            route = {item.alert_id: item.scenario_routing_decision for item in result.escalation_records}

            def expected_resolution(cutoff):
                values = []
                for alert_row in generated:
                    alert = alert_row.routed.alert
                    job = l2_jobs.get(alert.alert_id) if route.get(alert.alert_id, False) else l1_jobs.get(alert.alert_id)
                    if job is not None and job.completion <= cutoff:
                        values.append(job.competence * (1.0 - 0.35 * alert_row.difficulty))
                return (statistics.mean(values) if values else 0.0,
                        sum(values) / h.admitted if h.admitted else 0.0,
                        len(values))

            expected_h, expected_h_per_admitted, completed_h = expected_resolution(scenario.horizon)
            expected_end, expected_end_per_admitted, completed_end = expected_resolution(scenario.horizon + drain_h)
            episode_rows.append({
                "scenario_id": cell["id"], "seed": seed, "policy": policy,
                "arrival_rate_per_h": rate, "load_multiplier_l1_fluid": rate / base_capacity,
                "deadline_multiplier": cell.get("deadline_multiplier", 1.0),
                "eligibility_level": cell.get("eligibility_level", BASE_ELIGIBILITY),
                "competence_profile": cell.get("competence", "heterogeneous"),
                "speed_profile": cell.get("speed", "heterogeneous"),
                "escalation_multiplier": cell.get("escalation_multiplier", 1.0),
                "coordination_latency_h": cell.get("latency_h", 0.0),
                "coordination_edge_cost_units": cell.get("edge_cost_units", 0.0),
                "horizon_h": scenario.horizon, "drain_h": drain_h,
                "admitted": h.admitted,
                "sla_fraction_at_h": h.fraction_within_sla,
                "completed_at_h": h.completed_within_sla + h.completed_late,
                "expected_resolution_quality_completed_at_h": expected_h,
                "expected_correct_per_admitted_at_h": expected_h_per_admitted,
                "expected_quality_completed_count_at_h": completed_h,
                "pending_at_h": h.pending, "l1_backlog_at_h": h.l1_backlog,
                "l2_backlog_at_h": h.l2_backlog,
                "mean_wait_accrued_at_h": h.mean_wait_accrued,
                "sla_fraction_after_drain": end.fraction_within_sla,
                "completed_after_drain": end.completed_within_sla + end.completed_late,
                "expected_resolution_quality_completed_after_drain": expected_end,
                "expected_correct_per_admitted_after_drain": expected_end_per_admitted,
                "expected_quality_completed_count_after_drain": completed_end,
                "completed_within_sla_after_drain": end.completed_within_sla,
                "completed_late_after_drain": end.completed_late,
                "pending_after_drain": end.pending,
                "l1_backlog_after_drain": end.l1_backlog,
                "l2_backlog_after_drain": end.l2_backlog,
                "mean_wait_accrued_after_drain": end.mean_wait_accrued,
                "mean_response_completed_after_drain": end.mean_response_completed,
                "modeled_sla_conditioned_quality_per_admitted": end.modeled_quality_per_admitted,
                "mean_l1_utilization_at_h": statistics.mean(
                    value for name, value in h.utilization_by_analyst if name.startswith("L1:")
                ) if any(name.startswith("L1:") for name, _ in h.utilization_by_analyst) else 0.0,
                "mean_l2_utilization_at_h": statistics.mean(
                    value for name, value in h.utilization_by_analyst if name.startswith("L2:")
                ) if any(name.startswith("L2:") for name, _ in h.utilization_by_analyst) else 0.0,
                "coordination_person_time": result.coordination_person_time,
                "coordination_latency_total_h": (
                    result.l1_simulation.coordination_latency_total
                    + result.l2_simulation.coordination_latency_total
                ),
                "coordination_resource_units": (
                    result.l1_simulation.coordination_resource
                    + result.l2_simulation.coordination_resource
                ),
                "runtime_seconds": elapsed,
            })
        # One independent D1-state audit per seed; proposals are read-only.
        base_row = episode_rows[-len(policies)]
        D = drain_h
        l1_diag = inspect_stage(
            tuple(row.routed.alert for row in generated), l1, BASE_SERVICE_L1_H, l1_services,
            horizon=scenario.horizon, drain=D, seed=seed,
            latency=cell.get("latency_h", 0.0), edge_cost=cell.get("edge_cost_units", 0.0),
        )
        l1_session = _run_d1_session(
            tuple(row.routed.alert for row in generated), l1, BASE_SERVICE_L1_H, l1_services,
            horizon=scenario.horizon, drain=D, seed=seed,
        )
        d1_jobs = {job.alert_id: job for job in l1_session.assignments}
        routed_l2 = []
        for row in generated:
            job = d1_jobs.get(row.routed.alert.alert_id)
            if bool(row.routed.soctra_recommendation) and job is not None and job.completion < scenario.horizon + D:
                original = row.routed.alert
                routed_l2.append(type(original)(original.alert_id, job.completion,
                                                original.task_class, original.deadline))
        l2_diag = inspect_stage(
            tuple(routed_l2), l2, BASE_SERVICE_L2_H, l2_services,
            horizon=scenario.horizon + D, drain=0.0, seed=seed,
            latency=cell.get("latency_h", 0.0), edge_cost=cell.get("edge_cost_units", 0.0),
        )
        for level, rows in (("L1", l1_diag), ("L2", l2_diag)):
            for row in rows:
                diagnostic_rows.append({"scenario_id": cell["id"], "seed": seed,
                                        "level": level, **row})
    return episode_rows, diagnostic_rows


def _run_d1_session(alerts, analysts, services, individual_services, *, horizon, drain, seed):
    session = AllocationSession(
        alerts, analysts, services, admission_horizon=horizon, drain_period=drain,
        random_seed=seed, service_by_analyst_class=individual_services,
    )
    while not session._finalized:
        event = session.next_event_time()
        if event is None:
            break
        session.advance_to(event)
        if session.can_dispatch():
            session.dispatch("D1")
    return session


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def paired_summary(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    groups = {}
    for row in rows:
        groups.setdefault(row["scenario_id"], {}).setdefault(row["policy"], []).append(row)
    metrics = (
        "sla_fraction_at_h", "sla_fraction_after_drain",
        "modeled_sla_conditioned_quality_per_admitted", "pending_after_drain",
        "l1_backlog_after_drain", "l2_backlog_after_drain",
        "mean_wait_accrued_after_drain", "coordination_person_time",
        "coordination_latency_total_h", "coordination_resource_units",
    )
    means, differences_out = [], []
    for scenario, policies in sorted(groups.items()):
        by_policy = {p: {x["seed"]: x for x in values} for p, values in policies.items()}
        baseline = by_policy["D1"]
        for policy in POLICIES:
            values = policies[policy]
            means.append({
                "scenario_id": scenario, "policy": policy, "n_seeds": len(values),
                **{f"mean_{metric}": statistics.mean(float(x[metric]) for x in values)
                   for metric in metrics},
            })
        for policy in POLICIES[1:]:
            common = sorted(set(baseline) & set(by_policy[policy]))
            for metric in metrics[:7]:
                differences = [float(by_policy[policy][seed][metric]) - float(baseline[seed][metric])
                               for seed in common]
                mean = statistics.mean(differences)
                if len(differences) > 1:
                    half = student_t.ppf(0.975, len(differences) - 1) * statistics.stdev(differences) / math.sqrt(len(differences))
                else:
                    half = float("nan")
                differences_out.append({
                    "scenario_id": scenario, "comparison": f"{policy}-D1",
                    "metric": metric, "n_seeds": len(differences),
                    "paired_mean_difference": mean, "ci95_low": mean - half,
                    "ci95_high": mean + half,
                    "paired_sd": statistics.stdev(differences) if len(differences) > 1 else None,
                    "method": "paired Student-t interval",
                })
    return means, differences_out


def proposed_cells(config: dict) -> tuple[list[dict], list[dict], list[dict]]:
    l1, l2, l1s, l2s = build_team()
    p, need = PROJECT_MIX, ESCALATION_NEED_BY_PROJECT
    cap1 = effective_capacity(l1, l1s, p)["max_common_arrivals_per_h"]
    _, route_mix = routed_l2_shares(p, need)
    cap2 = effective_capacity(l2, l2s, route_mix)["max_common_arrivals_per_h"]
    route_rate, _ = routed_l2_shares(p, need)
    cap_incoming_l2 = cap2 / route_rate
    config["capacity_l1_alerts_per_h"] = cap1
    config["capacity_l2_escalations_per_h"] = cap2
    config["capacity_l2_equivalent_incoming_alerts_per_h"] = cap_incoming_l2

    core = [{"id": f"load_{m:.2f}C", "load_multiplier": m}
            for m in config["capacity_load_multipliers"]]
    core.extend({"id": f"deadline_{m:.2f}x_at_0.85C", "load_multiplier": 0.85,
                 "deadline_multiplier": m}
                for m in config["deadline_multipliers"] if m != 1.0)
    mechanisms = [
        # Boundary stress cell, deliberately kept out of the core load/deadline
        # sweep. It checks whether tight deadlines plus overload produce a
        # non-ceiling, non-floor SLA regime; it is not a plausible GMV estimate.
        {"id": "severe_overload_tight_deadlines_stress", "load_multiplier": 1.5,
         "deadline_multiplier": 0.1},
        {"id": "competence_homogeneous_at_0.85C_tight", "load_multiplier": 0.85,
         "deadline_multiplier": 0.5, "competence": "homogeneous"},
        {"id": "speed_homogeneous_at_0.85C_tight", "load_multiplier": 0.85,
         "deadline_multiplier": 0.5, "speed": "homogeneous"},
        {"id": "eligibility_homogeneous_at_0.85C_tight", "load_multiplier": 0.85,
         "deadline_multiplier": 0.5, "eligibility_level": 3.0},
        {"id": "eligibility_restricted_at_0.85C_tight", "load_multiplier": 0.85,
         "deadline_multiplier": 0.5, "eligibility_level": 1.5},
        {"id": "l2_escalation_stress_at_0.65C", "load_multiplier": 0.65,
         "deadline_multiplier": 0.5,
         "escalation_multiplier": config["l2_stress_escalation_multiplier"]},
        {"id": "two_hour_threefold_burst_at_0.65C", "load_multiplier": 0.65,
         "deadline_multiplier": 0.5,
         "burst_window": [8.0, 10.0, config["burst_control"]["rate_multiplier"]]},
    ]
    latency_cost = [
        {"id": f"coord_latency_{lat:.2f}h_cost_{cost:.1f}", "load_multiplier": 0.85,
         "deadline_multiplier": 0.5, "latency_h": lat, "edge_cost_units": cost}
        for lat in config["coordination_latency_h"]
        for cost in config["coordination_edge_cost_units"]
    ]
    drain = [{"id": f"drain_{hours:g}h_at_1.25C_tight", "load_multiplier": 1.25,
              "deadline_multiplier": 0.5, "drain_h": hours}
             for hours in config["drain_sweep_h"]]
    capacity = [
        {"pool": "L1", "capacity": cap1, "unit": "incoming alerts/h", **effective_capacity(l1, l1s, p)},
        {"pool": "L2", "capacity": cap2, "unit": "recommended/escalated alerts/h", **effective_capacity(l2, l2s, route_mix)},
    ]
    return core, mechanisms + latency_cost, drain


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--quick", action="store_true", help="3 seeds and only low/near/overload plus one mechanism cell")
    args = parser.parse_args()
    started = time.perf_counter()
    config = read_config(args.config)
    output_dir = (ROOT / config["output_dir"] if args.output_dir is None
                  else args.output_dir.resolve())
    output_dir.mkdir(parents=True, exist_ok=True)
    core_cells, mechanism_cells, drain_cells = proposed_cells(config)
    if args.quick:
        core_cells = [core_cells[i] for i in (0, 2, 4)]
        mechanism_cells = mechanism_cells[:1]
        drain_cells = []
    all_rows, diagnostics = [], []
    for cell in core_cells:
        seeds = list(range(config["core_paired_seeds"]["base"],
                           config["core_paired_seeds"]["base"] + (3 if args.quick else config["core_paired_seeds"]["count"])))
        rows, diag = run_cell(config, cell, seeds)
        all_rows.extend(rows)
        diagnostics.extend({"seed_set": "core", **row} for row in diag)
    for cell in mechanism_cells:
        seeds = list(range(config["mechanism_paired_seeds"]["base"],
                           config["mechanism_paired_seeds"]["base"] + (3 if args.quick else config["mechanism_paired_seeds"]["count"])))
        rows, diag = run_cell(config, cell, seeds)
        all_rows.extend(rows)
        diagnostics.extend({"seed_set": "mechanism", **row} for row in diag)
    drain_rows = []
    for cell in drain_cells:
        seeds = list(range(config["mechanism_paired_seeds"]["base"],
                           config["mechanism_paired_seeds"]["base"] + config["drain_check_seeds"]))
        rows, _ = run_cell(config, cell, seeds, drain=cell["drain_h"],
                           policies=tuple(config["drain_check_policies"]))
        drain_rows.extend(rows)
    means, differences = paired_summary(all_rows)
    _write_csv(output_dir / "episode_metrics.csv", all_rows)
    _write_csv(output_dir / "policy_means.csv", means)
    _write_csv(output_dir / "paired_differences_vs_d1.csv", differences)
    _write_csv(output_dir / "dispatch_opportunities.csv", diagnostics)
    _write_csv(output_dir / "drain_sensitivity.csv", drain_rows)
    (output_dir / "run_config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    runtime = {
        "episode_policy_runs": len(all_rows) + len(drain_rows),
        "diagnostic_dispatch_rows": len(diagnostics),
        "wall_clock_seconds": time.perf_counter() - started,
        "wall_clock_minutes": (time.perf_counter() - started) / 60,
        "capacity_estimates": config.get("capacity_l1_alerts_per_h"),
        "interpretation": "exploratory calibration; not confirmatory policy comparison",
    }
    (output_dir / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(runtime, indent=2))


if __name__ == "__main__":
    main()
