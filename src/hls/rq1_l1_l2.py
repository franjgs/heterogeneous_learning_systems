"""Minimal two-level RQ1 replay with explicit escalation provenance."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from .rq1_allocation import Alert, Analyst, B3Config, Metrics, SimulationResult, simulate


@dataclass(frozen=True)
class RoutedAlert:
    alert: Alert
    historical_escalation_label: bool | None
    soctra_recommendation: bool | None = None


@dataclass(frozen=True)
class EscalationRecord:
    alert_id: str
    historical_label: bool | None
    recommendation: bool | None
    observed_effective_analyst_decision: bool | None
    scenario_routing_decision: bool
    entered_l2: bool


@dataclass(frozen=True)
class EndToEndMetrics:
    cutoff: float
    admitted: int
    completed_within_sla: int
    fraction_within_sla: float
    completed_late: int
    pending: int
    l1_backlog: int
    l2_backlog: int
    mean_wait_accrued: float
    mean_response_completed: float | None
    utilization_by_analyst: tuple[tuple[str, float], ...]
    modeled_quality_per_admitted: float


@dataclass(frozen=True)
class L1L2Result:
    policy: str
    decision_mode: str
    horizon: float
    drain_period: float
    l1_simulation: SimulationResult
    l2_simulation: SimulationResult
    at_horizon: EndToEndMetrics
    after_drain: EndToEndMetrics
    escalation_records: tuple[EscalationRecord, ...]
    coordination_person_time: float
    selected_strategy_counts: tuple[tuple[str, int], ...]


def simulate_l1_l2(
    alerts: Sequence[RoutedAlert],
    l1_analysts: Sequence[Analyst],
    l2_analysts: Sequence[Analyst],
    l1_service_by_class: Mapping[object, float],
    l2_service_by_class: Mapping[object, float],
    *,
    policy: str,
    admission_horizon: float,
    drain_period: float,
    coordination_latency: float,
    decision_mode: str = "historical_label_reference",
    b3_config: B3Config = B3Config(0.75, 0.25, 0.15, 0.25),
    random_seed: int = 0,
    l1_service_by_analyst_class: Mapping[str, Mapping[object, float]] | None = None,
    l2_service_by_analyst_class: Mapping[str, Mapping[object, float]] | None = None,
) -> L1L2Result:
    """Run L1 then L2 with fixed routing decisions and same policy at both pools.

    ``historical_label_reference`` uses the historical escalation label only as
    an exogenous, fixed routing proxy. ``hypothetical_recommendation_acceptance``
    treats a matched out-of-sample recommendation as accepted for this scenario;
    it does not describe observed human behavior.
    """
    if decision_mode not in {
        "historical_label_reference", "hypothetical_recommendation_acceptance"
    }:
        raise ValueError("unknown escalation decision mode")
    if not isfinite(admission_horizon) or admission_horizon <= 0:
        raise ValueError("admission_horizon must be finite and positive")
    if not isfinite(drain_period) or drain_period < 0:
        raise ValueError("drain_period must be finite and nonnegative")
    if not isfinite(coordination_latency) or coordination_latency < 0:
        raise ValueError("coordination_latency must be finite and nonnegative")
    route_decisions = {}
    for row in alerts:
        if decision_mode == "historical_label_reference":
            decision = row.historical_escalation_label
        else:
            decision = row.soctra_recommendation
        if decision is None:
            raise ValueError(f"missing escalation input for alert {row.alert.alert_id}")
        route_decisions[row.alert.alert_id] = decision

    source_alerts = tuple(row.alert for row in alerts)
    l1 = simulate(
        source_alerts, l1_analysts, l1_service_by_class,
        policy=policy, admission_horizon=admission_horizon,
        drain_period=drain_period, coordination_latency=coordination_latency,
        b3_config=b3_config, random_seed=random_seed,
        service_by_analyst_class=l1_service_by_analyst_class,
    )
    source_by_id = {row.alert.alert_id: row for row in alerts}
    l1_jobs = {job.alert_id: job for job in l1.assignments}
    drain_end = admission_horizon + drain_period
    forwarded = []
    for alert_id, decision in route_decisions.items():
        job = l1_jobs.get(alert_id)
        if decision and job is not None and job.completion < drain_end:
            original = source_by_id[alert_id].alert
            forwarded.append(Alert(alert_id, job.completion, original.task_class, original.deadline))

    l2 = simulate(
        forwarded, l2_analysts, l2_service_by_class,
        policy=policy, admission_horizon=drain_end,
        drain_period=0.0, coordination_latency=coordination_latency,
        b3_config=b3_config, random_seed=random_seed,
        service_by_analyst_class=l2_service_by_analyst_class,
    )
    l2_jobs = {job.alert_id: job for job in l2.assignments}
    admitted = tuple(row.alert for row in alerts if row.alert.arrival < admission_horizon)
    effective_records = tuple(
        EscalationRecord(
            alert_id=row.alert.alert_id,
            historical_label=row.historical_escalation_label,
            recommendation=row.soctra_recommendation,
            observed_effective_analyst_decision=None,
            scenario_routing_decision=route_decisions[row.alert.alert_id],
            entered_l2=(
                row.alert.alert_id in l1_jobs
                and l1_jobs[row.alert.alert_id].completion <= drain_end
                and route_decisions[row.alert.alert_id]
            ),
        )
        for row in alerts
    )

    def metrics(cutoff: float) -> EndToEndMetrics:
        l1_backlog = 0
        l2_backlog = 0
        waits = []
        responses = []
        on_time = 0
        late = 0
        quality = 0.0
        for alert in admitted:
            first = l1_jobs.get(alert.alert_id)
            first_done = first is not None and first.completion <= cutoff
            if not first_done:
                l1_backlog += 1
            final = None
            if first_done:
                if route_decisions[alert.alert_id]:
                    second = l2_jobs.get(alert.alert_id)
                    if second is not None and second.completion <= cutoff:
                        final = second
                    else:
                        l2_backlog += 1
                else:
                    final = first
            first_start = first.start if first is not None else cutoff
            waits.append(max(0.0, min(first_start, cutoff) - alert.arrival))
            if first_done and route_decisions[alert.alert_id]:
                second = l2_jobs.get(alert.alert_id)
                second_start = second.start if second is not None else cutoff
                waits[-1] += max(0.0, min(second_start, cutoff) - first.completion)
            if final is None:
                continue
            responses.append(final.completion - alert.arrival)
            if final.completion <= alert.deadline:
                on_time += 1
                quality += final.competence
            else:
                late += 1
        util = []
        for prefix, stage in (("L1", l1), ("L2", l2)):
            for analyst_id, value in stage_metrics_at(stage, cutoff):
                util.append((f"{prefix}:{analyst_id}", value))
        n = len(admitted)
        completed = on_time + late
        return EndToEndMetrics(
            cutoff=cutoff, admitted=n,
            completed_within_sla=on_time,
            fraction_within_sla=on_time / n if n else 0.0,
            completed_late=late, pending=n - completed,
            l1_backlog=l1_backlog, l2_backlog=l2_backlog,
            mean_wait_accrued=sum(waits) / n if n else 0.0,
            mean_response_completed=sum(responses) / len(responses) if responses else None,
            utilization_by_analyst=tuple(util),
            modeled_quality_per_admitted=quality / n if n else 0.0,
        )

    counts = {
        name: dict(l1.selected_strategy_counts).get(name, 0)
        + dict(l2.selected_strategy_counts).get(name, 0)
        for name in ("B0", "B1", "B2")
    }
    return L1L2Result(
        policy=policy, decision_mode=decision_mode,
        horizon=admission_horizon, drain_period=drain_period,
        l1_simulation=l1, l2_simulation=l2,
        at_horizon=metrics(admission_horizon), after_drain=metrics(drain_end),
        escalation_records=effective_records,
        coordination_person_time=l1.coordination_person_time + l2.coordination_person_time,
        selected_strategy_counts=tuple((name, counts[name]) for name in ("B0", "B1", "B2")),
    )


def stage_metrics_at(result: SimulationResult, cutoff: float) -> tuple[tuple[str, float], ...]:
    """Recompute per-analyst service utilization at a requested shared cutoff."""
    # The RQ1 engine has snapshots at H and H+D; convert its stored intervals
    # directly so the L2 horizon extension does not distort H measurements.
    busy: dict[str, float] = {name: 0.0 for name, _ in result.at_horizon.utilization_by_analyst}
    for job in result.assignments:
        if job.analyst_id in busy:
            busy[job.analyst_id] += max(0.0, min(cutoff, job.completion) - max(0.0, job.start))
    return tuple((name, value / cutoff if cutoff else 0.0) for name, value in busy.items())
