"""Independent deterministic event simulator for the first SOCTRA-HLS RQ1 study.

This module does not import or alter the historical HLS-02 temporal engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from math import isfinite
import random
from typing import Hashable, Mapping, Sequence


ClassId = Hashable
Policy = str
ORGANIZATIONAL_ACTIONS = ("C0P0", "C0P1", "C1P0", "C1P1", "C2P0", "C2P1")
SOC_POLICY_NAMES = ("D1", "P1", "P2", "P3", "P4", "P5")


@dataclass(frozen=True)
class HLSAConfig:
    low: float = 1.0
    high: float = 2.0
    initial_mode: str = "D1"

    def __post_init__(self):
        if not (isfinite(self.low) and isfinite(self.high) and 0 <= self.low < self.high):
            raise ValueError("HLS-A requires finite thresholds 0 <= low < high")
        if self.initial_mode not in {"D1", "P1"}:
            raise ValueError("HLS-A initial_mode must be D1 or P1")


@dataclass(frozen=True)
class HLSBConfig:
    window_h: float
    low: float
    high: float
    capacity_per_h: float

    def __post_init__(self):
        if not (isfinite(self.window_h) and self.window_h > 0 and
                isfinite(self.capacity_per_h) and self.capacity_per_h > 0 and
                isfinite(self.low) and isfinite(self.high) and 0 <= self.low < self.high):
            raise ValueError("invalid HLS-B window, capacity or hysteresis")


@dataclass(frozen=True)
class HLSADecision:
    time: float
    mode: str
    pressure: float
    pending: int
    occupied: int
    switched: bool


def hlsa_pressure(pending, analysts, running, dispatching, service_time):
    """Maximum class-specific occupied fraction plus queued service equivalents."""
    if not pending:
        return 0.0
    values = []
    busy = set(running) | set(dispatching)
    for task_class in {alert.task_class for alert in pending.values()}:
        eligible = [a for a in analysts if task_class in a.eligible_classes]
        if not eligible:
            continue
        reference = sum(service_time(a, next(x for x in pending.values()
                                                  if x.task_class == task_class)) for a in eligible) / len(eligible)
        work = sum(min(service_time(a, x) for a in eligible)
                   for x in pending.values() if x.task_class == task_class)
        values.append(sum(a.analyst_id in busy for a in eligible) / len(eligible)
                      + work / (len(eligible) * reference))
    return max(values, default=0.0)


@dataclass(frozen=True)
class B3Config:
    """Fixed, transparent thresholds for the rule-based adaptive controller."""

    min_queue_per_free_analyst: float = 1.0
    min_deadline_pressure: float = 0.25
    min_competence_spread: float = 0.20
    max_latency_to_mean_service: float = 0.50
    use_load_signal: bool = True
    use_competence_signal: bool = True


@dataclass(frozen=True)
class Alert:
    alert_id: str
    arrival: float
    task_class: ClassId
    deadline: float


@dataclass(frozen=True)
class Analyst:
    analyst_id: str
    eligible_classes: frozenset[ClassId]
    competence: Mapping[ClassId, float]


@dataclass(frozen=True)
class Assignment:
    alert_id: str
    analyst_id: str
    start: float
    completion: float
    competence: float


@dataclass(frozen=True)
class D1Candidate:
    alert_id: str
    service_duration: float
    deadline: float
    remaining_slack: float
    deadline_risk: float
    own_competence: float
    eligible_peers: int
    projected_on_time: bool


@dataclass(frozen=True)
class D1Decision:
    """Auditable local choice; peer information is eligibility only."""

    time: float
    analyst_id: str
    alert_id: str
    deadline_risk: float
    own_competence: float
    eligible_peers: int
    queue_alert_ids: tuple[str, ...] = ()
    available_analyst_ids: tuple[str, ...] = ()
    candidates: tuple[D1Candidate, ...] = ()
    occupied_specialists: tuple[tuple[str, str, float], ...] = ()
    baseline_alert_id: str | None = None
    review_activated: bool = False


@dataclass(frozen=True)
class D1DispatchSnapshot:
    """Same-state local choices and ideal joint matching for diagnosis only."""

    time: float
    queue_alert_ids: tuple[str, ...]
    available_analyst_ids: tuple[str, ...]
    d1_pairs: tuple[tuple[str, str], ...]
    joint_oracle_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Metrics:
    cutoff: float
    admitted: int
    completed_within_sla: int
    fraction_within_sla: float
    completed_late: int
    pending: int
    mean_wait_accrued: float
    mean_response_completed: float | None
    utilization_by_analyst: tuple[tuple[str, float], ...]
    modeled_quality_per_admitted: float


@dataclass(frozen=True)
class SimulationResult:
    policy: Policy
    admission_horizon: float
    drain_period: float
    coordination_latency: float
    at_horizon: Metrics
    after_drain: Metrics
    assignments: tuple[Assignment, ...]
    selected_strategy_counts: tuple[tuple[str, int], ...]
    strategy_switches: int
    coordination_person_time: float
    coordination_latency_total: float = 0.0
    coordination_resource: float = 0.0
    dispatch_decisions: int = 0
    hlsa_history: tuple[HLSADecision, ...] = ()


def simulate(
    alerts: Sequence[Alert],
    analysts: Sequence[Analyst],
    service_by_class: Mapping[ClassId, float],
    *,
    policy: Policy,
    admission_horizon: float,
    drain_period: float = 0.0,
    random_seed: int = 0,
    coordination_latency: float = 0.0,
    coordination_edge_cost: float = 0.0,
    b3_config: B3Config = B3Config(),
    service_by_analyst_class: Mapping[str, Mapping[ClassId, float]] | None = None,
    forecast_service_by_analyst_class: Mapping[str, Mapping[ClassId, float]] | None = None,
    realized_scale_by_alert: Mapping[str, float] | None = None,
    hlsa_config: HLSAConfig = HLSAConfig(),
    hlsb_config: HLSBConfig | None = None,
    diagnostic_trace: list[dict] | None = None,
) -> SimulationResult:
    """Run one fixed policy on arrivals in [0, admission_horizon).

    At each event time, all arrivals are incorporated, all analysts finishing
    at that time are released, then dispatch occurs. Metrics at H are captured
    before a new dispatch at H; with a positive drain, pending alerts are
    dispatched after that snapshot. A completion exactly at a deadline is on
    time. A completion exactly at a metric cutoff is included in that snapshot.
    """
    legacy_policies = {"B0", "B0-R", "B0-F", "B1", "B2", "B3"}
    experimental_policies = {"T", "Q", "C"}
    if policy not in {*legacy_policies, *SOC_POLICY_NAMES, *experimental_policies, "HLS-A", "HLS-B"}:
        raise ValueError(f"policy must be one of {tuple(sorted(legacy_policies | set(SOC_POLICY_NAMES) | experimental_policies))}")
    if policy == "HLS-B" and hlsb_config is None:
        raise ValueError("HLS-B requires a capacity and window configuration")
    if not isinstance(random_seed, int) or isinstance(random_seed, bool):
        raise ValueError("random_seed must be an integer")
    _finite_nonnegative(admission_horizon, "admission_horizon", strictly_positive=True)
    _finite_nonnegative(drain_period, "drain_period")
    _finite_nonnegative(coordination_latency, "coordination_latency")
    _finite_nonnegative(coordination_edge_cost, "coordination_edge_cost")
    _validate_b3_config(b3_config)
    applied_coordination_latency = coordination_latency if policy in {"B1", "B2", "B3", "P4", "P5", "C"} else 0.0
    alert_rows = tuple(alerts)
    analyst_rows = tuple(analysts)
    services = dict(service_by_class)
    individual_services = {key: dict(value) for key, value in (service_by_analyst_class or {}).items()}
    forecast_input = {key: dict(value) for key, value in
                      (forecast_service_by_analyst_class or {}).items()}
    realized_scales = dict(realized_scale_by_alert or {})
    if (set(realized_scales) - {a.alert_id for a in alert_rows} or
            any(not isfinite(float(v)) or float(v) <= 0 for v in realized_scales.values())):
        raise ValueError("realized service scales must be finite, positive, and refer to known alerts")
    _validate(alert_rows, analyst_rows, services, individual_services)
    _validate(alert_rows, analyst_rows, services, forecast_input)
    forecast_services = {
        analyst.analyst_id: {
            task_class: forecast_input.get(analyst.analyst_id, {}).get(
                task_class,
                individual_services.get(analyst.analyst_id, {}).get(task_class,
                                                                     services[task_class]),
            )
            for task_class in analyst.eligible_classes
        }
        for analyst in analyst_rows
    }

    def service_time(analyst: Analyst, alert: Alert) -> float:
        return forecast_services[analyst.analyst_id].get(alert.task_class, services[alert.task_class])

    def effective_service_time(analyst: Analyst, alert: Alert) -> float:
        base = individual_services.get(analyst.analyst_id, {}).get(alert.task_class,
                                                                  services[alert.task_class])
        return base * float(realized_scales.get(alert.alert_id, 1.0))

    ordered_analysts = tuple(sorted(analyst_rows, key=lambda a: a.analyst_id))
    admitted = tuple(sorted(
        (a for a in alert_rows if a.arrival < admission_horizon),
        key=lambda a: (a.arrival, a.alert_id),
    ))
    by_id = {a.alert_id: a for a in admitted}
    arrivals_by_time: dict[float, list[Alert]] = {}
    for alert in admitted:
        arrivals_by_time.setdefault(alert.arrival, []).append(alert)

    pending: dict[str, Alert] = {}
    running: dict[str, Assignment] = {}
    dispatching: dict[str, tuple[Analyst, Alert, float]] = {}
    assignments: list[Assignment] = []
    busy_intervals: dict[str, list[tuple[float, float]]] = {
        a.analyst_id: [] for a in ordered_analysts
    }
    arrived_times = sorted(arrivals_by_time)
    arrival_cursor = 0
    now = 0.0
    order_rng = random.Random(random_seed)
    strategy_counts = {name: 0 for name in ("B0", "B1", "B2")}
    strategy_history: list[str] = []
    hlsa_history: list[HLSADecision] = []
    hlsa_mode = hlsa_config.initial_mode
    hlsb_mode = "D1"
    observed_arrivals: list[float] = []
    coordination_person_time = 0.0
    coordination_latency_total = 0.0
    coordination_resource = 0.0
    dispatch_decisions = 0
    horizon_metrics: Metrics | None = None
    drain_end = admission_horizon + drain_period

    # Include H as an event boundary even when no alert arrives or completes.
    while True:
        next_arrival = arrived_times[arrival_cursor] if arrival_cursor < len(arrived_times) else None
        next_completion = min((job.completion for job in running.values()), default=None)
        next_dispatch_start = min((plan[2] for plan in dispatching.values()), default=None)
        candidates = [v for v in (next_arrival, next_completion, next_dispatch_start) if v is not None]
        if horizon_metrics is None and now < admission_horizon:
            candidates.append(admission_horizon)
        if drain_period > 0 and now < drain_end:
            candidates.append(drain_end)
        if not candidates:
            break
        now = min(candidates)
        if now > drain_end:
            now = drain_end

        # Event semantics: arrivals, then completions, then one dispatch epoch.
        if arrival_cursor < len(arrived_times) and arrived_times[arrival_cursor] == now:
            for alert in arrivals_by_time[now]:
                pending[alert.alert_id] = alert
                observed_arrivals.append(now)
            arrival_cursor += 1
        finished = [aid for aid, job in running.items() if job.completion == now]
        for aid in finished:
            del running[aid]

        # A coordinated plan starts exactly once when its dispatch latency ends.
        ready_to_start = [aid for aid, plan in dispatching.items() if plan[2] == now]
        for aid in ready_to_start:
            analyst, alert, start = dispatching.pop(aid)
            assignment = Assignment(
                alert.alert_id, analyst.analyst_id, start,
                start + effective_service_time(analyst, alert), analyst.competence[alert.task_class],
            )
            running[analyst.analyst_id] = assignment
            assignments.append(assignment)
            busy_intervals[analyst.analyst_id].append((start, assignment.completion))

        if now == admission_horizon and horizon_metrics is None:
            horizon_metrics = _metrics(
                admission_horizon, admitted, assignments, ordered_analysts,
                busy_intervals, by_id,
            )

        if now >= drain_end:
            break
        if now == admission_horizon and drain_period == 0:
            break

        free = [
            a for a in ordered_analysts
            if a.analyst_id not in running and a.analyst_id not in dispatching
        ]
        if free and pending:
            strategy = policy
            if policy == "HLS-A":
                pressure = hlsa_pressure(pending, ordered_analysts, running, dispatching, service_time)
                previous = hlsa_mode
                if hlsa_mode == "D1" and pressure >= hlsa_config.high:
                    hlsa_mode = "P1"
                elif hlsa_mode == "P1" and pressure <= hlsa_config.low:
                    hlsa_mode = "D1"
                strategy = hlsa_mode
                hlsa_history.append(HLSADecision(now, strategy, pressure, len(pending),
                                                 len(running) + len(dispatching), strategy != previous))
            elif policy == "HLS-B":
                estimate = sum(now-hlsb_config.window_h < arrival <= now
                               for arrival in observed_arrivals) / hlsb_config.window_h
                pressure = estimate / hlsb_config.capacity_per_h
                previous = hlsb_mode
                if hlsb_mode == "D1" and pressure >= hlsb_config.high:
                    hlsb_mode = "P1"
                elif hlsb_mode == "P1" and pressure <= hlsb_config.low:
                    hlsb_mode = "D1"
                strategy = hlsb_mode
                hlsa_history.append(HLSADecision(now, strategy, pressure, len(pending),
                                                 len(running) + len(dispatching), strategy != previous))
            diagnostic_row = None
            if diagnostic_trace is not None and policy == "HLS-A":
                preview_rng = random.Random()
                preview_rng.setstate(order_rng.getstate())
                d1_preview = _dispatch_d1(free, pending, now, service_time, preview_rng)
                p1_preview = _dispatch_local_priority(free, pending, now, service_time)
                def pairs(proposal):
                    return tuple((a.analyst_id, x.alert_id) for a, x in proposal)
                delta = None
                if len(free) == 1 and len(d1_preview) == len(p1_preview) == 1:
                    analyst = free[0]
                    first_d = d1_preview[0][1]
                    first_p = p1_preview[0][1]
                    if first_d.alert_id != first_p.alert_id:
                        def value(first, second):
                            duration = service_time(analyst, first)
                            return (analyst.competence[first.task_class] *
                                    int(now + duration <= first.deadline) +
                                    analyst.competence[second.task_class] *
                                    int(now + duration + service_time(analyst, second) <= second.deadline))
                        delta = value(first_p, first_d) - value(first_d, first_p)
                diagnostic_row = dict(time=now, mode=strategy, z=pressure,
                    free=tuple(a.analyst_id for a in free), occupied=tuple(sorted(running)),
                    pending=tuple((x.alert_id, x.task_class, x.deadline, x.arrival) for x in pending.values()),
                    feasible=tuple((a.analyst_id, x.alert_id, service_time(a, x),
                                    a.competence[x.task_class], x.deadline-now-service_time(a, x))
                                   for a in free for x in pending.values() if x.task_class in a.eligible_classes),
                    d1=pairs(d1_preview), p1=pairs(p1_preview), delta_v=delta)
            if policy == "B3":
                strategy = _choose_b3_strategy(
                    free, pending, services, now, coordination_latency, b3_config, forecast_services,
                )
                strategy_counts[strategy] += 1
                strategy_history.append(strategy)
            strategy_latency = coordination_latency if strategy in {"B1", "B2", "C"} else 0.0
            dispatch_resource = 0.0
            if strategy == "D1":
                selected = _dispatch_d1(free, pending, now, service_time, order_rng)
            elif strategy in {"B0", "B0-R", "B0-F"}:
                selected = _dispatch_b0(free, pending, strategy, order_rng)
            elif strategy in {"P1", "P2", "P3", "P4", "P5"}:
                selected, strategy_latency, dispatch_resource = _dispatch_soc_policy(
                    strategy, free, pending, services, now, service_time,
                    forecast_services, order_rng, coordination_latency,
                    coordination_edge_cost,
                )
            elif strategy in {"T", "Q"}:
                selected = (_dispatch_local_priority(free, pending, now, service_time)
                            if strategy == "T" else
                            _dispatch_local_competence(free, pending, now, service_time))
            elif strategy == "C":
                selected = _dispatch_central_sequential(
                    free, pending, now, service_time, strategy_latency,
                )
            else:
                selected = _dispatch_coordinated(
                    free, pending, services, now, strategy, strategy_latency, forecast_services
                )
            if selected and strategy in {"P4", "P5", "C"} and strategy_latency:
                coordination_latency_total += strategy_latency
            if selected:
                dispatch_decisions += 1
                coordination_resource += dispatch_resource
                if strategy == "C":
                    coordination_resource += coordination_edge_cost * sum(
                        alert.task_class in analyst.eligible_classes
                        for analyst in free for alert in pending.values()
                    )
            if diagnostic_row is not None:
                diagnostic_row["executed"] = pairs(selected)
                diagnostic_trace.append(diagnostic_row)
            for analyst, alert in selected:
                # The matching is one-to-one; remove before scheduling to make
                # duplicate assignment impossible even under defensive checks.
                if alert.alert_id not in pending or analyst.analyst_id in running:
                    raise RuntimeError("duplicate or stale assignment produced by dispatcher")
                del pending[alert.alert_id]
                if strategy_latency > 0:
                    coordination_person_time += strategy_latency
                    if analyst.analyst_id in dispatching:
                        raise RuntimeError("analyst already has a coordinated dispatch in progress")
                    dispatching[analyst.analyst_id] = (
                        analyst, alert, now + strategy_latency,
                    )
                else:
                    assignment = Assignment(
                        alert.alert_id, analyst.analyst_id, now,
                        now + effective_service_time(analyst, alert), analyst.competence[alert.task_class],
                    )
                    running[analyst.analyst_id] = assignment
                    assignments.append(assignment)
                    busy_intervals[analyst.analyst_id].append((now, assignment.completion))

    if horizon_metrics is None:
        # This occurs only when H=0, which validation disallows, or an unusual
        # empty-event path; retain a deterministic boundary calculation.
        horizon_metrics = _metrics(
            admission_horizon, admitted, assignments, ordered_analysts,
            busy_intervals, by_id,
        )
    final_metrics = _metrics(
        drain_end, admitted, assignments, ordered_analysts,
        busy_intervals, by_id,
    )
    return SimulationResult(
        policy, admission_horizon, drain_period, applied_coordination_latency,
        horizon_metrics, final_metrics,
        tuple(sorted(assignments, key=lambda x: (x.start, x.analyst_id, x.alert_id))),
        tuple((name, strategy_counts[name]) for name in ("B0", "B1", "B2")),
        sum(left != right for left, right in zip(strategy_history, strategy_history[1:])),
        coordination_person_time,
        coordination_latency_total,
        coordination_resource,
        dispatch_decisions,
        tuple(hlsa_history),
    )


class AllocationSession:
    """Incremental execution of the RQ1 event engine.

    The fixed-policy ``simulate`` API remains unchanged. This session exposes
    its event clock and dispatch boundary so a caller can pause, inspect only
    the current state, choose B0/B1/B2, and resume. It shares the established
    dispatchers and metric function with ``simulate``.
    """

    def __init__(self, alerts: Sequence[Alert], analysts: Sequence[Analyst],
                 service_by_class: Mapping[ClassId, float], *, admission_horizon: float,
                 drain_period: float = 0.0, random_seed: int = 0,
                 coordination_latency: float = 0.0, b3_config: B3Config = B3Config(),
                 service_by_analyst_class: Mapping[str, Mapping[ClassId, float]] | None = None,
                 roster_schedule: Sequence[tuple[float, Sequence[str]]] = (),
                 coordination_edge_cost: float = 0.0, coordination_screen_cost: float = 0.0,
                 diagnostic_d1: bool = False):
        _finite_nonnegative(admission_horizon, "admission_horizon", strictly_positive=True)
        _finite_nonnegative(drain_period, "drain_period")
        _finite_nonnegative(coordination_latency, "coordination_latency")
        _finite_nonnegative(coordination_edge_cost, "coordination_edge_cost")
        _finite_nonnegative(coordination_screen_cost, "coordination_screen_cost")
        _validate_b3_config(b3_config)
        if not isinstance(random_seed, int) or isinstance(random_seed, bool):
            raise ValueError("random_seed must be an integer")
        self.horizon = admission_horizon
        self.drain_period = drain_period
        self.drain_end = admission_horizon + drain_period
        self.coordination_latency = coordination_latency
        self.coordination_edge_cost = coordination_edge_cost
        self.coordination_screen_cost = coordination_screen_cost
        self.diagnostic_d1 = bool(diagnostic_d1)
        self.b3_config = b3_config
        self.analysts = tuple(sorted(analysts, key=lambda a: a.analyst_id))
        known_ids = {a.analyst_id for a in self.analysts}
        self._active_analyst_ids = set(known_ids)
        schedule = sorted((float(t), tuple(ids)) for t, ids in roster_schedule)
        if len({t for t, _ in schedule}) != len(schedule):
            raise ValueError("roster schedule times must be unique")
        if any(not isfinite(t) or t < 0 or t > self.drain_end for t, _ in schedule):
            raise ValueError("roster schedule times must lie within the episode")
        if any(len(ids) != len(set(ids)) or not set(ids) <= known_ids for _, ids in schedule):
            raise ValueError("roster schedule must contain unique known analyst IDs")
        self._roster_schedule = {t: set(ids) for t, ids in schedule}
        self.services = dict(service_by_class)
        self.individual_services = {key: dict(value) for key, value in (service_by_analyst_class or {}).items()}
        self._validate_alert_set(alerts)
        _validate(alerts, self.analysts, self.services, self.individual_services)
        self.alerts: dict[str, Alert] = {}
        self.pending: dict[str, Alert] = {}
        self.running: dict[str, Assignment] = {}
        self.dispatching: dict[str, tuple[Analyst, Alert, float]] = {}
        self.assignments: list[Assignment] = []
        self.d1_decisions: list[D1Decision] = []
        self.d1l_review_count = 0
        self.d1s_review_count = 0
        self.d1_dispatch_snapshots: list[D1DispatchSnapshot] = []
        self.busy_intervals: dict[str, list[tuple[float, float]]] = {a.analyst_id: [] for a in self.analysts}
        self.arrivals: dict[float, list[Alert]] = {}
        self.now = 0.0
        self.order_rng = random.Random(random_seed)
        self.strategy_counts = {name: 0 for name in ("B0", "B1", "B2")}
        self.strategy_history: list[str] = []
        self.coordination_person_time = 0.0
        self.coordination_latency_total = 0.0
        self.coordination_resource = 0.0
        self.dispatch_decisions = 0
        self.organization_action_counts = {name: 0 for name in ORGANIZATIONAL_ACTIONS}
        self.organization_action_history: list[str] = []
        self._processed_time: float | None = None
        self._finished_at_now: list[Assignment] = []
        self.arrived_at_now: tuple[Alert, ...] = ()
        self._finalized = False
        for alert in alerts:
            if alert.arrival < self.horizon:
                self.add_alert(alert)

    def _validate_alert_set(self, alerts: Sequence[Alert]) -> None:
        ids = [a.alert_id for a in alerts]
        if len(ids) != len(set(ids)):
            raise ValueError("alert IDs must be unique")
        if any(a.arrival >= self.horizon for a in alerts):
            raise ValueError("initial alert arrivals must precede admission_horizon")

    def add_alert(self, alert: Alert) -> None:
        """Add a newly generated/revealed arrival without exposing later work."""
        if self._finalized or alert.alert_id in self.alerts:
            raise ValueError("session is finalized or alert ID is already present")
        if alert.arrival < self.now or alert.arrival > self.drain_end:
            raise ValueError("new alert arrival must be current/future and no later than drain end")
        if alert.task_class not in self.services:
            raise ValueError("service_by_class must define the new alert class")
        if not isfinite(alert.deadline) or not isfinite(alert.arrival):
            raise ValueError("alert times must be finite")
        self.alerts[alert.alert_id] = alert
        self.arrivals.setdefault(alert.arrival, []).append(alert)

    def next_event_time(self) -> float | None:
        if self._finalized:
            return None
        candidates = [*self.arrivals.keys()]
        candidates.extend(job.completion for job in self.running.values())
        candidates.extend(plan[2] for plan in self.dispatching.values())
        candidates.extend(t for t in self._roster_schedule if t >= self.now)
        if self.horizon > self.now:
            candidates.append(self.horizon)
        if self.drain_end > self.now:
            candidates.append(self.drain_end)
        future = [time for time in candidates if time >= self.now]
        return min(future) if future else None

    def advance_to(self, time: float) -> tuple[Assignment, ...]:
        """Advance clock and process arrivals/completions at ``time`` once."""
        if time < self.now or not isfinite(time):
            raise ValueError("event clock must advance monotonically with finite values")
        repeated_epoch = self._processed_time == time
        self.now = time
        if not repeated_epoch:
            self._finished_at_now = []
        just_arrived = sorted(self.arrivals.pop(time, []), key=lambda a: (a.arrival, a.alert_id))
        self.arrived_at_now = tuple(just_arrived)
        for alert in just_arrived:
            self.pending[alert.alert_id] = alert
        finished_ids = [aid for aid, job in self.running.items() if job.completion == time]
        for aid in finished_ids:
            self._finished_at_now.append(self.running.pop(aid))
        ready = [aid for aid, plan in self.dispatching.items() if plan[2] == time]
        for aid in ready:
            analyst, alert, start = self.dispatching.pop(aid)
            completion = start + self._service_time(analyst, alert)
            assignment = Assignment(alert.alert_id, aid, start, completion, analyst.competence[alert.task_class])
            self.running[aid] = assignment
            self.assignments.append(assignment)
            self.busy_intervals[aid].append((start, completion))
        # Staffing changes are applied at the event boundary before dispatch.
        if time in self._roster_schedule:
            self._active_analyst_ids = set(self._roster_schedule.pop(time))
        self._processed_time = time
        if time >= self.drain_end:
            self._finalized = True
        return tuple(self._finished_at_now)

    def _service_time(self, analyst: Analyst, alert: Alert) -> float:
        value = self.individual_services.get(analyst.analyst_id, {}).get(alert.task_class,
                                                                         self.services[alert.task_class])
        if not isfinite(value) or value <= 0:
            raise ValueError("analyst-specific service duration must be finite and positive")
        return value

    def can_dispatch(self) -> bool:
        if self._finalized or self.now >= self.drain_end or not self.pending:
            return False
        free = self.available_analysts()
        return any(alert.task_class in analyst.eligible_classes
                   for alert in self.pending.values() for analyst in free)

    def available_analysts(self) -> tuple[Analyst, ...]:
        unavailable = set(self.running) | set(self.dispatching)
        return tuple(a for a in self.analysts
                     if a.analyst_id in self._active_analyst_ids and a.analyst_id not in unavailable)

    def dispatch(self, policy: Policy) -> tuple[str, ...]:
        """Apply one policy at current time; return selected alert IDs."""
        if policy not in {"B0", "B1", "B2", "B3", "D1", "D1-L", "D1-S", "P1", "P2", "P3", "P4", "P5", "T", "Q", "C"}:
            raise ValueError("unknown dispatch policy")
        free = self.available_analysts()
        if not free or not self.pending or self._finalized:
            return ()
        strategy = policy
        if policy == "B3":
            strategy = _choose_b3_strategy(free, self.pending, self.services, self.now,
                                           self.coordination_latency, self.b3_config,
                                           self.individual_services)
            self.strategy_counts[strategy] += 1
            self.strategy_history.append(strategy)
        latency = self.coordination_latency if strategy in {"B1", "B2", "C"} else 0.0
        resource = 0.0
        if strategy in {"D1", "D1-L", "D1-S"}:
            local_correction = strategy in {"D1-L", "D1-S"}
            queue_ids = tuple(sorted(self.pending))
            available_ids = tuple(a.analyst_id for a in free)
            joint_pairs = []
            occupied_specialists = ()
            if self.diagnostic_d1:
                # Diagnostic oracle only: exact current-state matching that
                # never feeds an assignment back into the frozen D1 decision.
                joint_pairs = _dispatch_coordinated(
                    free, self.pending, self.services, self.now, "B2", 0.0,
                    self.individual_services,
                )
                occupied_specialists = tuple(
                    (analyst_id, job.alert_id, job.completion)
                    for analyst_id, job in self.running.items()
                    if any(job_alert.task_class in next(
                        a for a in self.analysts if a.analyst_id == analyst_id
                    ).eligible_classes for job_alert in self.pending.values())
                )
            selected = _dispatch_d1(free, self.pending, self.now,
                                    self._service_time, self.order_rng,
                                    self.d1_decisions if self.diagnostic_d1 else None,
                                    queue_ids=queue_ids,
                                    occupied_specialists=occupied_specialists,
                                    local_correction=local_correction,
                                    selective_correction=strategy == "D1-S",
                                    review_counter=self)
            if self.diagnostic_d1:
                self.d1_dispatch_snapshots.append(D1DispatchSnapshot(
                    self.now, queue_ids, available_ids,
                    tuple((a.analyst_id, x.alert_id) for a, x in selected),
                    tuple((a.analyst_id, x.alert_id) for a, x in joint_pairs),
                ))
        elif strategy in {"P1", "P2", "P3", "P4", "P5"}:
            selected, latency, resource = _dispatch_soc_policy(
                strategy, free, self.pending, self.services, self.now,
                self._service_time, self.individual_services, self.order_rng,
                self.coordination_latency, self.coordination_edge_cost,
            )
        elif strategy in {"T", "Q"}:
            selected = (_dispatch_local_priority(free, self.pending, self.now, self._service_time)
                        if strategy == "T" else
                        _dispatch_local_competence(free, self.pending, self.now, self._service_time))
        elif strategy == "C":
            selected = _dispatch_central_sequential(
                free, self.pending, self.now, self._service_time, latency,
            )
        elif strategy == "B0":
            selected = _dispatch_b0(free, self.pending, "B0", self.order_rng)
        else:
            selected = _dispatch_coordinated(free, self.pending, self.services, self.now,
                                             strategy, latency, self.individual_services)
        if selected and strategy in {"B1", "B2"}:
            self.coordination_latency_total += latency
            self.coordination_resource += self.coordination_edge_cost * sum(
                alert.task_class in analyst.eligible_classes
                for analyst in free for alert in self.pending.values()
            )
        elif selected and strategy in {"P4", "P5", "C"}:
            self.coordination_latency_total += latency
            if strategy == "C":
                resource = self.coordination_edge_cost * sum(
                    alert.task_class in analyst.eligible_classes
                    for analyst in free for alert in self.pending.values()
                )
            self.coordination_resource += resource
        if selected:
            self.dispatch_decisions += 1
        ids = []
        for analyst, alert in selected:
            if alert.alert_id not in self.pending or analyst.analyst_id in self.running or analyst.analyst_id in self.dispatching:
                raise RuntimeError("duplicate or stale assignment produced by dispatcher")
            del self.pending[alert.alert_id]
            ids.append(alert.alert_id)
            if latency:
                self.coordination_person_time += latency
                self.dispatching[analyst.analyst_id] = (analyst, alert, self.now + latency)
            else:
                completion = self.now + self._service_time(analyst, alert)
                assignment = Assignment(alert.alert_id, analyst.analyst_id, self.now, completion,
                                        analyst.competence[alert.task_class])
                self.running[analyst.analyst_id] = assignment
                self.assignments.append(assignment)
                self.busy_intervals[analyst.analyst_id].append((self.now, completion))
        return tuple(ids)

    def preview_organization(self, action: str, *, coordination_latency_override: float | None = None):
        """Pure proposal preview for mechanism diagnostics on the current state."""
        if action not in ORGANIZATIONAL_ACTIONS:
            raise ValueError(f"action must be one of {ORGANIZATIONAL_ACTIONS}")
        if coordination_latency_override is not None:
            _finite_nonnegative(coordination_latency_override, "coordination_latency_override")
        free = self.available_analysts()
        if not free or not self.pending or self._finalized:
            return {"pairs": (), "edges": 0, "screened": 0, "resource": 0.0, "latency": 0.0}
        pairs, edges, screened, resource, latency = _dispatch_organization(
            action, free, self.pending, self.services, self.now, self.individual_services,
            self.coordination_edge_cost, self.coordination_screen_cost,
        )
        if action[1] != "0" and coordination_latency_override is not None:
            latency = coordination_latency_override
        return {"pairs": tuple(pairs), "edges": edges, "screened": screened,
                "resource": resource, "latency": latency}

    def dispatch_organization(self, action: str, *, coordination_latency_override: float | None = None) -> tuple[str, ...]:
        """Apply one C0/C1/C2 × P0/P1 assignment decision at the current event."""
        proposal = self.preview_organization(action, coordination_latency_override=coordination_latency_override)
        free = self.available_analysts()
        if not free or not self.pending or self._finalized:
            return ()
        selected = list(proposal["pairs"])
        inspected_edges = int(proposal["edges"])
        screened_alerts = int(proposal["screened"])
        resource = float(proposal["resource"])
        latency = float(proposal["latency"])
        self.organization_action_counts[action] += 1
        self.organization_action_history.append(action)
        if selected:
            self.coordination_resource += resource
            self.coordination_latency_total += latency
            self.coordination_person_time += latency * len(selected)
        ids = []
        for analyst, alert in selected:
            if alert.alert_id not in self.pending or analyst.analyst_id in self.running or analyst.analyst_id in self.dispatching:
                raise RuntimeError("duplicate or stale organizational assignment")
            del self.pending[alert.alert_id]
            ids.append(alert.alert_id)
            if latency:
                self.dispatching[analyst.analyst_id] = (analyst, alert, self.now + latency)
            else:
                completion = self.now + self._service_time(analyst, alert)
                assignment = Assignment(alert.alert_id, analyst.analyst_id, self.now, completion,
                                        analyst.competence[alert.task_class])
                self.running[analyst.analyst_id] = assignment
                self.assignments.append(assignment)
                self.busy_intervals[analyst.analyst_id].append((self.now, completion))
        return tuple(ids)

    def metrics(self, cutoff: float) -> Metrics:
        admitted = tuple(sorted(self.alerts.values(), key=lambda a: (a.arrival, a.alert_id)))
        return _metrics(cutoff, admitted, self.assignments, self.analysts,
                        self.busy_intervals, self.alerts)

    def result(self, policy: str) -> SimulationResult:
        if not self._finalized:
            raise RuntimeError("session has not reached its drain boundary")
        return SimulationResult(
            policy, self.horizon, self.drain_period,
            self.coordination_latency if policy in {"B1", "B2", "B3", "P4", "P5", "C"} else 0.0,
            self.metrics(self.horizon), self.metrics(self.drain_end),
            tuple(sorted(self.assignments, key=lambda x: (x.start, x.analyst_id, x.alert_id))),
            tuple((name, self.strategy_counts[name]) for name in ("B0", "B1", "B2")),
            sum(a != b for a, b in zip(self.strategy_history, self.strategy_history[1:])),
            self.coordination_person_time,
            self.coordination_latency_total,
            self.coordination_resource,
            self.dispatch_decisions,
        )


def _validate_b3_config(config: B3Config) -> None:
    for name in ("min_queue_per_free_analyst", "min_deadline_pressure", "min_competence_spread", "max_latency_to_mean_service"):
        value = getattr(config, name)
        if not isfinite(value) or value < 0:
            raise ValueError(f"B3Config.{name} must be finite and nonnegative")
    if config.min_deadline_pressure > 1 or config.min_competence_spread > 1:
        raise ValueError("B3 deadline pressure and competence spread thresholds must be at most one")


def _choose_b3_strategy(
    free: Sequence[Analyst],
    pending: Mapping[str, Alert],
    services: Mapping[ClassId, float],
    now: float,
    coordination_latency: float,
    config: B3Config,
    individual_services: Mapping[str, Mapping[ClassId, float]] | None = None,
) -> str:
    """Choose a fixed dispatcher using only the current queue and roster."""
    individual_services = individual_services or {}
    service = lambda analyst, alert: individual_services.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
    feasible_pairs = [(analyst, alert) for alert in pending.values() for analyst in free if alert.task_class in analyst.eligible_classes]
    mean_service = (sum(service(analyst, alert) for analyst, alert in feasible_pairs) / len(feasible_pairs)
                    if feasible_pairs else sum(services[a.task_class] for a in pending.values()) / len(pending))
    if coordination_latency / mean_service > config.max_latency_to_mean_service:
        return "B0"
    if config.use_load_signal and len(pending) / len(free) < config.min_queue_per_free_analyst:
        return "B0"
    eligible_alerts = [
        alert for alert in pending.values()
        if any(alert.task_class in analyst.eligible_classes for analyst in free)
    ]
    if not eligible_alerts:
        return "B0"
    urgent = sum(
        1 for alert in eligible_alerts
        if min(
            alert.deadline - now - service(analyst, alert) - coordination_latency
            for analyst in free if alert.task_class in analyst.eligible_classes
        ) <= 0
    ) / len(eligible_alerts)
    if urgent < config.min_deadline_pressure:
        return "B0"
    if config.use_competence_signal:
        scores = [
            analyst.competence[alert.task_class]
            for alert in eligible_alerts for analyst in free
            if alert.task_class in analyst.eligible_classes
        ]
        if scores and max(scores) - min(scores) >= config.min_competence_spread:
            return "B2"
    return "B1"


def _dispatch_b0(
    free: Sequence[Analyst], pending: Mapping[str, Alert], policy: str, order_rng: random.Random
) -> list[tuple[Analyst, Alert]]:
    result = []
    remaining = dict(pending)
    order = list(free)
    if policy == "B0-R":
        order_rng.shuffle(order)
    elif policy == "B0-F":
        order.sort(key=lambda a: (len(a.eligible_classes), a.analyst_id))
    else:
        order.sort(key=lambda a: a.analyst_id)
    for analyst in order:
        candidates = [a for a in remaining.values() if a.task_class in analyst.eligible_classes]
        if candidates:
            chosen = min(candidates, key=lambda a: (a.deadline, a.arrival, a.alert_id))
            result.append((analyst, chosen))
            del remaining[chosen.alert_id]
    return result


def _dispatch_soc_policy(
    policy: str,
    free: Sequence[Analyst],
    pending: Mapping[str, Alert],
    services: Mapping[ClassId, float],
    now: float,
    service_time,
    individual_services: Mapping[str, Mapping[ClassId, float]],
    order_rng: random.Random,
    coordination_latency: float,
    coordination_edge_cost: float,
) -> tuple[list[tuple[Analyst, Alert]], float, float]:
    """Shared active SOC policy interface; returns pairs, latency, resource cost.

    P1-P3 are sequential local selectors. P4 always uses current-state matching.
    P5 uses P3 unless P4 strictly increases the lexicographic pair
    (predicted on-time completions, total assignments), with coordination
    latency included in the P4 prediction. No scalar weights or future events
    enter the decision.
    """
    if policy == "P1":
        return _dispatch_local_priority(free, pending, now, service_time), 0.0, 0.0
    if policy == "P2":
        return _dispatch_local_competence(free, pending, now, service_time), 0.0, 0.0
    if policy == "P3":
        return _dispatch_local_capacity(free, pending, now, service_time), 0.0, 0.0
    if policy not in {"P4", "P5"}:
        raise ValueError(f"unknown active SOC policy: {policy}")

    joint = _dispatch_coordinated(
        free, pending, services, now, "B1", coordination_latency,
        individual_services,
    )
    edge_count = sum(
        alert.task_class in analyst.eligible_classes
        for analyst in free for alert in pending.values()
    )
    resource_cost = edge_count * coordination_edge_cost if joint else 0.0
    if policy == "P4":
        return joint, coordination_latency if joint else 0.0, resource_cost

    local = _dispatch_local_capacity(free, pending, now, service_time)
    local_outcome = _predicted_assignment_outcome(local, now, 0.0, service_time)
    joint_outcome = _predicted_assignment_outcome(
        joint, now, coordination_latency, service_time,
    )
    if joint_outcome > local_outcome:
        return joint, coordination_latency if joint else 0.0, resource_cost
    return local, 0.0, 0.0


def _predicted_assignment_outcome(pairs, now, latency, service_time) -> tuple[int, int]:
    on_time = sum(
        now + latency + service_time(analyst, alert) <= alert.deadline
        for analyst, alert in pairs
    )
    return int(on_time), len(pairs)


def _dispatch_local_priority(free, pending, now, service_time):
    """P1: local sequential selection by least post-service slack."""
    remaining = dict(pending)
    selected = []
    for analyst in sorted(free, key=lambda row: row.analyst_id):
        candidates = [a for a in remaining.values() if a.task_class in analyst.eligible_classes]
        if not candidates:
            continue
        alert = min(candidates, key=lambda a: (
            a.deadline - now - service_time(analyst, a),
            a.deadline, a.arrival, a.alert_id,
        ))
        selected.append((analyst, alert))
        del remaining[alert.alert_id]
    return selected


def _dispatch_local_competence(free, pending, now, service_time):
    """P2: local sequential selection by own competence, then temporal slack."""
    remaining = dict(pending)
    selected = []
    for analyst in sorted(free, key=lambda row: row.analyst_id):
        candidates = [a for a in remaining.values() if a.task_class in analyst.eligible_classes]
        if not candidates:
            continue
        alert = min(candidates, key=lambda a: (
            -analyst.competence[a.task_class],
            a.deadline - now - service_time(analyst, a),
            a.deadline, a.arrival, a.alert_id,
        ))
        selected.append((analyst, alert))
        del remaining[alert.alert_id]
    return selected


def _dispatch_central_sequential(free, pending, now, service_time, coordination_latency=0.0):
    """Greedy central pair selection; one decision epoch, no batch optimizer.

    Pair priority is lexicographic: (1) predicted on-time completion, (2)
    least nonnegative slack if on time / least lateness if late, (3) higher
    assigned-analyst competence, (4) shorter service, then stable IDs. After
    choosing a pair, its analyst and alert are removed before the next choice.
    """
    remaining_alerts = dict(pending)
    remaining_analysts = list(sorted(free, key=lambda row: row.analyst_id))
    selected = []
    while remaining_analysts and remaining_alerts:
        feasible = []
        for analyst in remaining_analysts:
            for alert in remaining_alerts.values():
                if alert.task_class not in analyst.eligible_classes:
                    continue
                duration = service_time(analyst, alert)
                slack = alert.deadline - now - coordination_latency - duration
                on_time = slack >= 0
                temporal_distance = slack if on_time else -slack
                key = (
                    -int(on_time), temporal_distance,
                    -analyst.competence[alert.task_class], duration,
                    alert.deadline, alert.arrival, alert.alert_id, analyst.analyst_id,
                )
                feasible.append((key, analyst, alert))
        if not feasible:
            break
        _, analyst, alert = min(feasible, key=lambda row: row[0])
        selected.append((analyst, alert))
        del remaining_alerts[alert.alert_id]
        remaining_analysts.remove(analyst)
    return selected


def _dispatch_local_capacity(free, pending, now, service_time):
    """P3: protect scarce eligibility, then own competence, then temporal slack."""
    remaining = dict(pending)
    selected = []
    remaining_analysts = list(sorted(free, key=lambda row: row.analyst_id))
    while remaining_analysts:
        analyst = remaining_analysts.pop(0)
        candidates = [a for a in remaining.values() if a.task_class in analyst.eligible_classes]
        if not candidates:
            continue
        def key(alert):
            alternatives = sum(
                alert.task_class in peer.eligible_classes
                for peer in remaining_analysts
            )
            return (alternatives, -analyst.competence[alert.task_class],
                    alert.deadline - now - service_time(analyst, alert),
                    alert.deadline, alert.arrival, alert.alert_id)
        alert = min(candidates, key=key)
        selected.append((analyst, alert))
        del remaining[alert.alert_id]
    return selected


def _dispatch_d1(free, pending, now, service_time, order_rng, trace=None,
                 *, queue_ids=(), occupied_specialists=(), local_correction=False,
                 selective_correction=False,
                 review_counter=None):
    """Sequential decentralized choice using risk, own skill, then peer coverage.

    Peers' exact competence is never consulted. Their eligible classes are the
    public, coarse specialty profile. Each selected alert is removed at once.
    """
    remaining = dict(pending)
    order = list(free)
    order_rng.shuffle(order)
    result = []
    for analyst in order:
        candidates = [alert for alert in remaining.values()
                      if alert.task_class in analyst.eligible_classes]
        if not candidates:
            continue

        def candidate_row(alert):
            duration = service_time(analyst, alert)
            slack = alert.deadline - now
            risk = min(1.0, max(0.0, (duration - slack) / duration))
            peer_count = sum(
                alert.task_class in peer.eligible_classes
                for peer in free if peer.analyst_id != analyst.analyst_id
            )
            return D1Candidate(alert.alert_id, duration, alert.deadline, slack,
                               risk, analyst.competence[alert.task_class], peer_count,
                               now + duration <= alert.deadline)

        candidate_rows = tuple(candidate_row(alert) for alert in candidates)

        def choice_key(alert):
            row = next(c for c in candidate_rows if c.alert_id == alert.alert_id)
            # Maximize urgency and own competence; at a tie, cover scarce
            # specialty first, then use stable deadline/arrival/ID ordering.
            return (-row.deadline_risk, -row.own_competence, row.eligible_peers,
                    alert.deadline, alert.arrival, alert.alert_id)

        baseline_choice = min(candidates, key=choice_key)
        chosen = baseline_choice
        baseline_row = next(c for c in candidate_rows if c.alert_id == baseline_choice.alert_id)
        viable_alternatives = [alert for alert in candidates
                               if alert.alert_id != baseline_choice.alert_id
                               and next(c for c in candidate_rows if c.alert_id == alert.alert_id).projected_on_time]
        reviewed = bool(local_correction and not baseline_row.projected_on_time and viable_alternatives)
        if reviewed:
            # Local review: select the viable candidate with least post-service
            # slack (greatest urgency), then own competence and stable tie keys.
            chosen = min(viable_alternatives, key=lambda alert: (
                alert.deadline - now - service_time(analyst, alert),
                -analyst.competence[alert.task_class], alert.deadline,
                alert.arrival, alert.alert_id,
            ))
            if selective_correction:
                alternative_row = next(c for c in candidate_rows if c.alert_id == chosen.alert_id)
                # Pareto screen on directly comparable, analyst-local quantities:
                # accept only when the viable alternative is no slower and no
                # less competent than D1's original choice.
                reviewed = (alternative_row.own_competence >= baseline_row.own_competence
                            and alternative_row.service_duration <= baseline_row.service_duration)
                if not reviewed:
                    chosen = baseline_choice
            if reviewed and review_counter is not None:
                if selective_correction:
                    review_counter.d1s_review_count += 1
                else:
                    review_counter.d1l_review_count += 1
        duration = service_time(analyst, chosen)
        risk = min(1.0, max(0.0, (duration - (chosen.deadline - now)) / duration))
        peers = sum(chosen.task_class in peer.eligible_classes
                    for peer in free if peer.analyst_id != analyst.analyst_id)
        result.append((analyst, chosen))
        if trace is not None:
            trace.append(D1Decision(now, analyst.analyst_id, chosen.alert_id,
                                    risk, analyst.competence[chosen.task_class], peers,
                                    tuple(queue_ids), tuple(a.analyst_id for a in free),
                                    candidate_rows, tuple(occupied_specialists),
                                    baseline_choice.alert_id, reviewed))
        del remaining[chosen.alert_id]
    return result


def _dispatch_organization(
    action: str,
    free: Sequence[Analyst],
    pending: Mapping[str, Alert],
    services: Mapping[ClassId, float],
    now: float,
    individual_services: Mapping[str, Mapping[ClassId, float]],
    edge_cost: float,
    screen_cost: float,
) -> tuple[list[tuple[Analyst, Alert]], int, int, float, float]:
    """Return assignments plus reviewed eligible edges and screened alerts."""
    level, priority = int(action[1]), action[2:]
    if level == 0:
        if priority == "P0":
            return _dispatch_b0(free, pending, "B0", random.Random(0)), 0, 0, 0.0, 0.0
        return _dispatch_local_balanced(free, pending, services, now, individual_services), 0, 0, 0.0, 0.0

    urgent: dict[str, Alert] = {}
    screened = 0
    if level == 1:
        # C1 only coordinates tasks with minimum eligible service slack no
        # larger than mean feasible service; other tasks remain local.
        feasible_services = [
            individual_services.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
            for analyst in free for alert in pending.values()
            if alert.task_class in analyst.eligible_classes
        ]
        mean_service = sum(feasible_services) / len(feasible_services) if feasible_services else 0.0
        urgent = {
            alert_id: alert for alert_id, alert in pending.items()
            if min((alert.deadline - now
                    - individual_services.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
                    for analyst in free if alert.task_class in analyst.eligible_classes),
                   default=float("inf")) <= mean_service
        }
        screened = len(pending)
    else:
        urgent = dict(pending)

    edges = sum(alert.task_class in analyst.eligible_classes
                for analyst in free for alert in urgent.values())
    resource = edge_cost * edges + screen_cost * screened

    def assign(latency: float) -> list[tuple[Analyst, Alert]]:
        coordinated = (_dispatch_coordinated(free, urgent, services, now,
                                             priority, latency, individual_services)
                       if urgent else [])
        used_analysts = {analyst.analyst_id for analyst, _ in coordinated}
        used_alerts = {alert.alert_id for _, alert in coordinated}
        remaining_free = [analyst for analyst in free if analyst.analyst_id not in used_analysts]
        remaining_pending = {alert_id: alert for alert_id, alert in pending.items() if alert_id not in used_alerts}
        local = (_dispatch_b0(remaining_free, remaining_pending, "B0", random.Random(0))
                 if priority == "P0" else
                 _dispatch_local_balanced(remaining_free, remaining_pending, services, now + latency, individual_services))
        return coordinated + local

    # The coordination effort is parallelized over analysts available at this
    # decision. Latency and total effort therefore remain separate measures.
    latency = resource / len(free) if resource and free else 0.0
    selected = assign(latency)
    return selected, edges, screened, resource, latency


def _dispatch_local_balanced(
    free: Sequence[Analyst], pending: Mapping[str, Alert],
    services: Mapping[ClassId, float], now: float,
    individual_services: Mapping[str, Mapping[ClassId, float]],
) -> list[tuple[Analyst, Alert]]:
    remaining = dict(pending)
    feasible_service = [
        individual_services.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
        for analyst in free for alert in remaining.values()
        if alert.task_class in analyst.eligible_classes
    ]
    max_service = max(feasible_service, default=1.0)
    result = []
    for analyst in sorted(free, key=lambda a: a.analyst_id):
        candidates = [alert for alert in remaining.values()
                      if alert.task_class in analyst.eligible_classes]
        if not candidates:
            continue
        def utility(alert: Alert) -> tuple[float, float, str]:
            service = individual_services.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
            on_time = float(now + service <= alert.deadline)
            speed = 1.0 - service / max_service
            competence = analyst.competence[alert.task_class]
            score = 0.60 * competence + 0.25 * on_time + 0.15 * speed
            return score, -alert.deadline, alert.alert_id
        selected = max(candidates, key=utility)
        result.append((analyst, selected))
        del remaining[selected.alert_id]
    return result


def _dispatch_coordinated(
    free: Sequence[Analyst],
    pending: Mapping[str, Alert],
    services: Mapping[ClassId, float],
    now: float,
    policy: str,
    coordination_latency: float = 0.0,
    individual_services: Mapping[str, Mapping[ClassId, float]] | None = None,
) -> list[tuple[Analyst, Alert]]:
    """Lexicographic maximum-weight bipartite matching via min-cost flow.

    Priority vector for B1: on-time count, assignment count, nearest-deadline
    rank, then deterministic graph traversal. B2 inserts modeled on-time
    competence after on-time count and before assignment count. Optimization
    is local to this dispatch instant and has no future-arrival look-ahead.
    """
    agents = tuple(sorted(free, key=lambda a: a.analyst_id))
    individual_services = individual_services or {}
    tasks = tuple(sorted(pending.values(), key=lambda a: (a.deadline, a.arrival, a.alert_id)))
    if not agents or not tasks:
        return []

    # Residual graph edges store [to, reverse-index, capacity, cost-vector,
    # original metadata]. Lexicographic vector costs avoid arbitrary scalar
    # constants when translating the ordered objectives.
    if policy not in {"B1", "B2", "P0", "P1"}:
        raise ValueError("coordinated priority must be B1, B2, P0 or P1")
    dim = 4 if policy in {"B1", "P0"} else (3 if policy == "P1" else 5)
    zero = tuple(0.0 for _ in range(dim))
    source = 0
    agent_base = 1
    task_base = agent_base + len(agents)
    sink = task_base + len(tasks)
    graph: list[list[list[object]]] = [[] for _ in range(sink + 1)]

    def add_edge(u: int, v: int, cap: int, cost: tuple[float, ...], meta: object = None) -> list[object]:
        forward: list[object] = [v, len(graph[v]), cap, cost, meta]
        reverse: list[object] = [u, len(graph[u]), 0, tuple(-x for x in cost), None]
        graph[u].append(forward)
        graph[v].append(reverse)
        return forward

    for ix, analyst in enumerate(agents):
        add_edge(source, agent_base + ix, 1, zero)
        add_edge(agent_base + ix, sink, 1, zero, (analyst, None))  # unused analyst
    for jx in range(len(tasks)):
        add_edge(task_base + jx, sink, 1, zero)

    rank = {a.alert_id: ix for ix, a in enumerate(tasks)}
    max_service = max((individual_services.get(a.analyst_id, {}).get(task.task_class, services[task.task_class])
                       for a in agents for task in tasks if task.task_class in a.eligible_classes),
                      default=1.0)
    assignment_edges: list[list[object]] = []
    for ix, analyst in enumerate(agents):
        for alert in tasks:
            if alert.task_class not in analyst.eligible_classes:
                continue
            service_time = individual_services.get(analyst.analyst_id, {}).get(alert.task_class, services[alert.task_class])
            on_time = now + coordination_latency + service_time <= alert.deadline
            if policy in {"B1", "P0"}:
                utility = (float(on_time), 1.0, -float(rank[alert.alert_id]), -float(ix * (len(tasks) + 1) + rank[alert.alert_id]))
            elif policy == "P1":
                speed = 1.0 - service_time / max_service
                score = (0.60 * analyst.competence[alert.task_class]
                         + 0.25 * float(on_time) + 0.15 * speed)
                utility = (score, 1.0, -float(ix * (len(tasks) + 1) + rank[alert.alert_id]))
            else:
                competence = analyst.competence[alert.task_class] if on_time else 0.0
                utility = (float(on_time), competence, 1.0, -float(rank[alert.alert_id]), -float(ix * (len(tasks) + 1) + rank[alert.alert_id]))
            edge = add_edge(
                agent_base + ix, task_base + rank[alert.alert_id], 1,
                tuple(-x for x in utility), (analyst, alert),
            )
            assignment_edges.append(edge)

    # Initial shortest-path potentials (the unflowed network is acyclic apart
    # from zero-capacity reverse edges); then reduced-cost Dijkstra per unit.
    potentials = _initial_potentials(graph, source, zero)
    for _ in agents:
        dist: list[tuple[float, ...] | None] = [None] * len(graph)
        prev: list[tuple[int, int] | None] = [None] * len(graph)
        dist[source] = zero
        heap: list[tuple[tuple[float, ...], int]] = [(zero, source)]
        while heap:
            distance, u = heappop(heap)
            if dist[u] != distance:
                continue
            for edge_ix, edge in enumerate(graph[u]):
                if int(edge[2]) <= 0:
                    continue
                v = int(edge[0])
                reduced = tuple(x + p_u - p_v for x, p_u, p_v in zip(edge[3], potentials[u], potentials[v]))  # type: ignore[arg-type]
                candidate = tuple(a + b for a, b in zip(distance, reduced))
                if dist[v] is None or candidate < dist[v]:
                    dist[v] = candidate
                    prev[v] = (u, edge_ix)
                    heappush(heap, (candidate, v))
        if prev[sink] is None:
            raise RuntimeError("matching flow could not route an analyst skip")
        for node, value in enumerate(dist):
            if value is not None:
                potentials[node] = tuple(a + b for a, b in zip(potentials[node], value))
        node = sink
        while node != source:
            u, edge_ix = prev[node]  # type: ignore[misc]
            edge = graph[u][edge_ix]
            edge[2] = int(edge[2]) - 1
            reverse = graph[node][int(edge[1])]
            reverse[2] = int(reverse[2]) + 1
            node = u

    selected = []
    for edge in assignment_edges:
        if int(edge[2]) == 0:
            analyst, alert = edge[4]  # type: ignore[misc]
            selected.append((analyst, alert))
    return sorted(selected, key=lambda pair: (pair[0].analyst_id, pair[1].alert_id))


def _initial_potentials(
    graph: Sequence[Sequence[Sequence[object]]], source: int, zero: tuple[float, ...]
) -> list[tuple[float, ...]]:
    distances: list[tuple[float, ...] | None] = [None] * len(graph)
    distances[source] = zero
    for _ in range(len(graph) - 1):
        changed = False
        for u, edges in enumerate(graph):
            if distances[u] is None:
                continue
            for edge in edges:
                if int(edge[2]) <= 0:
                    continue
                v = int(edge[0])
                candidate = tuple(a + b for a, b in zip(distances[u], edge[3]))  # type: ignore[arg-type]
                if distances[v] is None or candidate < distances[v]:
                    distances[v] = candidate
                    changed = True
        if not changed:
            break
    return [distance if distance is not None else zero for distance in distances]


def _metrics(
    cutoff: float,
    admitted: Sequence[Alert],
    assignments: Sequence[Assignment],
    analysts: Sequence[Analyst],
    busy_intervals: Mapping[str, Sequence[tuple[float, float]]],
    alert_lookup: Mapping[str, Alert],
) -> Metrics:
    assignment_by_alert = {item.alert_id: item for item in assignments}
    completed = [
        item for item in assignments if item.completion <= cutoff
    ]
    on_time = [item for item in completed if item.completion <= alert_lookup[item.alert_id].deadline]
    late_count = len(completed) - len(on_time)
    pending_count = len(admitted) - len(completed)
    wait_values = []
    for alert in admitted:
        assignment = assignment_by_alert.get(alert.alert_id)
        stop = min(cutoff, assignment.start) if assignment is not None else cutoff
        wait_values.append(max(0.0, stop - alert.arrival))
    response = [item.completion - alert_lookup[item.alert_id].arrival for item in completed]
    utilization = []
    for analyst in analysts:
        busy = sum(max(0.0, min(end, cutoff) - max(start, 0.0)) for start, end in busy_intervals[analyst.analyst_id])
        utilization.append((analyst.analyst_id, busy / cutoff if cutoff > 0 else 0.0))
    total_quality = sum(item.competence for item in on_time)
    return Metrics(
        cutoff=cutoff,
        admitted=len(admitted),
        completed_within_sla=len(on_time),
        fraction_within_sla=len(on_time) / len(admitted) if admitted else 0.0,
        completed_late=late_count,
        pending=pending_count,
        mean_wait_accrued=sum(wait_values) / len(wait_values) if wait_values else 0.0,
        mean_response_completed=sum(response) / len(response) if response else None,
        utilization_by_analyst=tuple(utilization),
        modeled_quality_per_admitted=total_quality / len(admitted) if admitted else 0.0,
    )


def _validate(alerts: Sequence[Alert], analysts: Sequence[Analyst], services: Mapping[ClassId, float],
              individual_services: Mapping[str, Mapping[ClassId, float]] | None = None) -> None:
    individual_services = individual_services or {}
    ids = [alert.alert_id for alert in alerts]
    if len(ids) != len(set(ids)) or any(not isinstance(value, str) or not value for value in ids):
        raise ValueError("alert IDs must be unique, non-empty strings")
    analyst_ids = [analyst.analyst_id for analyst in analysts]
    if len(analyst_ids) != len(set(analyst_ids)) or any(not isinstance(value, str) or not value for value in analyst_ids):
        raise ValueError("analyst IDs must be unique, non-empty strings")
    if any(not isfinite(a.arrival) or a.arrival < 0 or not isfinite(a.deadline) for a in alerts):
        raise ValueError("alert times must be finite; arrivals must be nonnegative")
    if any(a.task_class not in services for a in alerts):
        raise ValueError("service_by_class must define every alert class")
    if any(not isfinite(value) or value <= 0 for value in services.values()):
        raise ValueError("service durations must be finite and positive")
    analyst_map = {a.analyst_id: a for a in analysts}
    if not set(individual_services).issubset(analyst_map):
        raise ValueError("analyst-specific service map contains an unknown analyst")
    for analyst_id, values in individual_services.items():
        if not set(values).issubset(analyst_map[analyst_id].eligible_classes):
            raise ValueError("analyst-specific service map contains an ineligible class")
        if any(not isfinite(value) or value <= 0 for value in values.values()):
            raise ValueError("analyst-specific service durations must be finite and positive")
    for analyst in analysts:
        if any(not isfinite(analyst.competence.get(k, float("nan"))) or not 0 <= analyst.competence[k] <= 1
               for k in analyst.eligible_classes):
            raise ValueError("eligible analyst-class competence must be defined in [0, 1]")
    if any(not set(a.eligible_classes).issubset(a.competence) for a in analysts):
        raise ValueError("competence must be defined for every eligible class")
def _finite_nonnegative(value: float, name: str, *, strictly_positive: bool = False) -> None:
    if not isfinite(value) or value < 0 or (strictly_positive and value == 0):
        adjective = "positive" if strictly_positive else "nonnegative"
        raise ValueError(f"{name} must be finite and {adjective}")
