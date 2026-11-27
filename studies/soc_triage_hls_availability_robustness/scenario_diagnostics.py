"""Policy-independent deadline, capacity and queue diagnostics.

These functions consume immutable scenario objects and optional evaluator-only
sidecars. They never invoke a dispatcher or alter a SimulationRequest.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from statistics import mean
from types import MappingProxyType
from typing import Mapping, Sequence

from hls.rq1_allocation import Alert
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity
from studies.soc_triage_hls_availability_robustness.availability_engine import Calendar, CONTINUOUS
from studies.soc_triage_hls_availability_robustness.execution_api import (
    EnvironmentRealization, OrganizationConfig, SimulationRequest,
)
from studies.soc_triage_hls_availability_robustness.triage_execution import (
    FLOW_MODES, HISTORICAL_L1_THEN_L2, TRIAGE_SINGLE_INVESTIGATION,
)


def _quantile(values: Sequence[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * p
    lo = int(index)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)


def _calendar_completion(calendar: Calendar, start: float, work: float) -> float:
    """Earliest completion after start, consuming work only while available."""
    t, remaining = float(start), float(work)
    if remaining <= 1e-12:
        return t
    # Weekly calendars guarantee a change within one week; the guard catches
    # invalid/no-availability calendars without silently inventing capacity.
    for _ in range(10000):
        if calendar.available(t):
            boundary = calendar.next_change(t)
            available = boundary - t
            if remaining <= available + 1e-12:
                return t + remaining
            remaining -= available
        t = calendar.next_change(t)
    raise ValueError("calendar has no usable work window for requested service")


@dataclass(frozen=True)
class AlertDeadlineDiagnostic:
    alert_id: str
    task_class: str
    severity: str
    route: str
    slack_h: float
    optimistic_min_service_h: float
    optimistic_slack_h: float
    optimistic_intrinsically_infeasible: bool
    optimistic_l1_analyst_id: str | None
    optimistic_l2_analyst_id: str | None
    calendar_earliest_completion: float | None
    calendar_slack_h: float | None
    calendar_infeasible: bool | None
    calendar_l1_analyst_id: str | None
    calendar_l2_analyst_id: str | None


@dataclass(frozen=True)
class FeasibilityGroup:
    by: str
    key: str
    count: int
    infeasible_count: int
    infeasible_fraction: float
    minimum_slack_h: float
    slack_quantiles_h: tuple[tuple[str, float | None], ...]
    calendar_infeasible_count: int | None
    calendar_infeasible_fraction: float | None
    calendar_slack_quantiles_h: tuple[tuple[str, float | None], ...] | None


@dataclass(frozen=True)
class DeadlineFeasibilityReport:
    route_basis: str
    tasks: tuple[AlertDeadlineDiagnostic, ...]
    infeasible_count: int
    infeasible_fraction: float
    calendar_infeasible_count: int | None
    calendar_infeasible_fraction: float | None
    groups: tuple[FeasibilityGroup, ...]


def assess_deadline_feasibility(
    request: SimulationRequest,
    *,
    l2_required_by_alert: Mapping[str, bool],
    route_basis: str,
    severity_by_alert: Mapping[str, str] | None = None,
    environment: EnvironmentRealization | None = None,
    include_calendars: bool = True,
    flow_mode: str = HISTORICAL_L1_THEN_L2,
) -> DeadlineFeasibilityReport:
    """Compute zero-queue lower bounds and earliest calendar-respecting completion.

    ``route_basis`` must identify whether L2 requirements mean the scenario's
    true need labels or the simulated recommendation path. This is evaluator
    analysis; the mapping is never passed to a policy.
    """
    if route_basis not in {"true_need", "simulated_route", "scenario_route"}:
        raise ValueError("route_basis must explicitly name true_need or a simulated/scenario route")
    if flow_mode not in FLOW_MODES:
        raise ValueError(f"flow_mode must be one of {sorted(FLOW_MODES)}")
    alerts = tuple(a for a in request.alerts if a.arrival < request.settings.admission_horizon)
    ids = {a.alert_id for a in alerts}
    if set(l2_required_by_alert) != ids or any(not isinstance(v, bool) for v in l2_required_by_alert.values()):
        raise ValueError("l2_required_by_alert must contain a boolean for each admitted alert")
    if severity_by_alert is not None and set(severity_by_alert) != ids:
        raise ValueError("severity_by_alert must cover exactly the admitted alerts")
    env = environment if environment is not None else request.environment
    if env is not None and env.difficulty_service_beta > 0 and set(env.difficulty_by_alert or {}) != ids:
        raise ValueError("difficulty realization must cover each admitted alert")
    if env is not None and env.service_scale_by_alert is not None and set(env.service_scale_by_alert) - ids:
        raise ValueError("service-scale realization contains unknown alert IDs")
    scale = request.settings.time_scale.factor
    l1 = request.organization.resources_for("L1")
    l2 = request.organization.resources_for("L2") if any(l2_required_by_alert.values()) else ()
    rows = []
    for alert in alerts:
        q = float((env.difficulty_by_alert or {}).get(alert.alert_id, 0.5)) if env else 0.5
        beta = env.difficulty_service_beta if env else 0.0
        difficulty_factor = 1.0 + beta * (q - 0.5)
        need_l2 = l2_required_by_alert[alert.alert_id]
        eligible_l1 = [r for r in l1 if alert.task_class in r.analyst.eligible_classes]
        eligible_l2 = [r for r in l2 if alert.task_class in r.analyst.eligible_classes] if need_l2 else []
        direct_l2 = flow_mode == TRIAGE_SINGLE_INVESTIGATION and need_l2
        if (not direct_l2 and not eligible_l1) or (need_l2 and not eligible_l2):
            raise ValueError(f"no eligible professional for alert {alert.alert_id!r} on required route")
        def l1_service(resource):
            multiplier = (float((env.service_scale_by_alert or {}).get(alert.alert_id, 1.0))
                          if env and flow_mode == TRIAGE_SINGLE_INVESTIGATION else 1.0)
            return resource.service_by_class[alert.task_class] * difficulty_factor * multiplier * scale
        min_l1 = (min(eligible_l1, key=lambda r: (l1_service(r), r.analyst.analyst_id))
                  if eligible_l1 and not direct_l2 else None)
        optimistic_work = l1_service(min_l1) if min_l1 is not None else 0.0
        min_l2 = None
        if need_l2:
            alpha = float((env.service_scale_by_alert or {}).get(alert.alert_id, 1.0)) if env else 1.0
            def l2_service(resource):
                return resource.service_by_class[alert.task_class] * difficulty_factor * alpha * scale
            min_l2 = min(eligible_l2, key=lambda r: (l2_service(r), r.analyst.analyst_id))
            if direct_l2:
                optimistic_work = l2_service(min_l2)
            else:
                optimistic_work += l2_service(min_l2)
        slack = (alert.deadline - alert.arrival) * scale
        optimistic_slack = slack - optimistic_work
        l1_finish = l2_finish = None
        l1_calendar_id = l2_calendar_id = None
        if include_calendars:
            def earliest(resources, start, service_fn):
                candidates = []
                for resource in resources:
                    calendar = (resource.calendar or CONTINUOUS).scaled(scale)
                    finish = _calendar_completion(calendar, start * scale, service_fn(resource))
                    candidates.append((finish, resource.analyst.analyst_id))
                return min(candidates)
            if not direct_l2:
                l1_finish, l1_calendar_id = earliest(eligible_l1, alert.arrival, l1_service)
            if need_l2:
                assert min_l2 is not None
                # L2 receives the alert only after L1 service, with its own
                # earliest eligible calendar. The original alert deadline stays fixed.
                alpha = float((env.service_scale_by_alert or {}).get(alert.alert_id, 1.0)) if env else 1.0
                l2_finish, l2_calendar_id = earliest(
                    eligible_l2, (alert.arrival if direct_l2 else l1_finish / scale),
                    lambda r: r.service_by_class[alert.task_class] * difficulty_factor * alpha * scale,
                )
            calendar_finish = l2_finish if need_l2 else l1_finish
            calendar_slack = alert.deadline * scale - calendar_finish
            calendar_bad = calendar_slack < -1e-12
        else:
            calendar_finish = calendar_slack = calendar_bad = None
        route = (("L2" if need_l2 else "L1") if flow_mode == TRIAGE_SINGLE_INVESTIGATION
                 else ("L1+L2" if need_l2 else "L1"))
        rows.append(AlertDeadlineDiagnostic(
            alert.alert_id, str(alert.task_class), str((severity_by_alert or {}).get(alert.alert_id, "unspecified")),
            route, slack, optimistic_work, optimistic_slack, optimistic_slack < -1e-12,
            min_l1.analyst.analyst_id if min_l1 else None, min_l2.analyst.analyst_id if min_l2 else None,
            calendar_finish, calendar_slack, calendar_bad, l1_calendar_id, l2_calendar_id,
        ))
    groups = []
    for dimension, getter in (
        ("severity", lambda x: x.severity), ("class", lambda x: x.task_class),
        ("route", lambda x: x.route),
    ):
        for key in sorted({getter(x) for x in rows}):
            selected = [x for x in rows if getter(x) == key]
            slacks = [x.optimistic_slack_h for x in selected]
            nbad = sum(x.optimistic_intrinsically_infeasible for x in selected)
            calendar_values = [x.calendar_slack_h for x in selected if x.calendar_slack_h is not None]
            calendar_bad = sum(bool(x.calendar_infeasible) for x in selected) if include_calendars else None
            groups.append(FeasibilityGroup(
                dimension, key, len(selected), nbad, nbad / len(selected), min(slacks),
                tuple((label, _quantile(slacks, p)) for label, p in (("p10", .1), ("p50", .5), ("p90", .9))),
                calendar_bad, calendar_bad / len(selected) if include_calendars else None,
                (tuple((label, _quantile(calendar_values, p))
                       for label, p in (("p10", .1), ("p50", .5), ("p90", .9)))
                 if include_calendars else None),
            ))
    bad = sum(x.optimistic_intrinsically_infeasible for x in rows)
    calendar_bad = sum(bool(x.calendar_infeasible) for x in rows) if include_calendars else None
    return DeadlineFeasibilityReport(
        route_basis, tuple(rows), bad, bad / len(rows) if rows else 0.0,
        calendar_bad, calendar_bad / len(rows) if include_calendars and rows else (0.0 if include_calendars else None),
        tuple(groups),
    )


@dataclass(frozen=True)
class DemandRegime:
    """Piecewise-constant offered incoming rate; maps are alerts/hour by class."""
    name: str
    start_h: float
    end_h: float
    arrival_rate_by_class: Mapping[str, float]
    # If supplied, these are realized routed L2 rates and mean effective
    # L2 multipliers by class (from an existing trace, not a new generator).
    realized_l2_rate_by_class: Mapping[str, float] | None = None
    realized_l2_service_factor_by_class: Mapping[str, float] | None = None
    realized_l1_service_factor_by_class: Mapping[str, float] | None = None
    realized_l1_rate_by_class: Mapping[str, float] | None = None

    def __post_init__(self):
        if not self.name or not isfinite(self.start_h) or not isfinite(self.end_h) or self.start_h < 0 or self.end_h <= self.start_h:
            raise ValueError("demand regime needs a name and finite 0 <= start_h < end_h")
        for name, values in (("arrival rates", self.arrival_rate_by_class),
                             ("realized L1 rates", self.realized_l1_rate_by_class or {}),
                             ("realized L2 rates", self.realized_l2_rate_by_class or {}),
                             ("realized L2 factors", self.realized_l2_service_factor_by_class or {}),
                             ("realized L1 factors", self.realized_l1_service_factor_by_class or {})):
            if any(not k or not isfinite(float(v)) or float(v) < 0 for k, v in values.items()):
                raise ValueError(f"{name} must be finite nonnegative class mappings")
        if (self.realized_l2_rate_by_class is None) != (self.realized_l2_service_factor_by_class is None):
            raise ValueError("realized L2 rate and service-factor maps must be supplied together")
        if self.realized_l2_rate_by_class is not None and set(self.realized_l2_rate_by_class) - set(self.arrival_rate_by_class):
            raise ValueError("realized L2 classes must appear in the incoming class-rate map")
        if self.realized_l1_service_factor_by_class is not None and set(self.realized_l1_service_factor_by_class) - set(self.arrival_rate_by_class):
            raise ValueError("realized L1 factor classes must appear in the incoming class-rate map")
        for name in ("arrival_rate_by_class", "realized_l1_rate_by_class", "realized_l2_rate_by_class",
                     "realized_l2_service_factor_by_class", "realized_l1_service_factor_by_class"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, MappingProxyType(dict(value)))


@dataclass(frozen=True)
class CapacityDemandProfile:
    regimes: tuple[DemandRegime, ...]
    prevalence_by_class: Mapping[str, float] | None = None
    sensitivity_by_class: Mapping[str, float] | None = None
    false_positive_rate_by_class: Mapping[str, float] | None = None
    alpha: float = 1.0
    beta: float = 0.0
    # Optional E[q|class,need] and E[q|class,no-need]. With no map the
    # synthetic independent Beta(2,2) model has both means at 0.5.
    difficulty_mean_by_class_and_need: Mapping[str, tuple[float, float]] | None = None
    gamma: float = 1.0
    flow_mode: str = HISTORICAL_L1_THEN_L2

    def __post_init__(self):
        object.__setattr__(self, "regimes", tuple(self.regimes))
        if not self.regimes:
            raise ValueError("at least one demand regime is required")
        ordered = sorted(self.regimes, key=lambda regime: (regime.start_h, regime.end_h))
        if len({regime.name for regime in ordered}) != len(ordered):
            raise ValueError("demand regime names must be unique")
        if any(left.end_h > right.start_h for left, right in zip(ordered, ordered[1:])):
            raise ValueError("demand regimes must not overlap")
        expected_maps = (self.prevalence_by_class, self.sensitivity_by_class, self.false_positive_rate_by_class)
        if any(value is not None for value in expected_maps) and not all(value is not None for value in expected_maps):
            raise ValueError("prevalence, sensitivity and false-positive maps are all required for expected L2 rates")
        classes = set(self.prevalence_by_class or {}) or {
            k for regime in self.regimes for k in regime.arrival_rate_by_class
        }
        if not classes:
            raise ValueError("demand regimes must define at least one task class")
        if self.prevalence_by_class is not None and (
            set(self.sensitivity_by_class) != set(self.prevalence_by_class) or
            set(self.false_positive_rate_by_class) != set(self.prevalence_by_class)
        ):
            raise ValueError("prevalence, sensitivity and false-positive maps must cover the same classes")
        for name, values in (("prevalence", self.prevalence_by_class or {}),
                             ("sensitivity", self.sensitivity_by_class or {}),
                             ("false-positive rate", self.false_positive_rate_by_class or {})):
            if any(not isfinite(float(x)) or not 0 <= float(x) <= 1 for x in values.values()):
                raise ValueError(f"{name} values must be in [0,1]")
        if not isfinite(self.alpha) or not 0 < self.alpha <= 1:
            raise ValueError("alpha must be in (0,1]")
        if not isfinite(self.beta) or not 0 <= self.beta < 2:
            raise ValueError("beta must satisfy 0 <= beta < 2")
        if not isfinite(self.gamma) or self.gamma < 1:
            raise ValueError("gamma must be finite and at least 1")
        if self.flow_mode not in FLOW_MODES:
            raise ValueError(f"flow_mode must be one of {sorted(FLOW_MODES)}")
        for name in ("prevalence_by_class", "sensitivity_by_class", "false_positive_rate_by_class"):
            value = getattr(self, name)
            if value is not None:
                object.__setattr__(self, name, MappingProxyType(dict(value)))
        if self.difficulty_mean_by_class_and_need is not None:
            object.__setattr__(self, "difficulty_mean_by_class_and_need",
                               MappingProxyType(dict(self.difficulty_mean_by_class_and_need)))
            if set(self.difficulty_mean_by_class_and_need) != classes:
                raise ValueError("difficulty means must cover all classes")
            for pair in self.difficulty_mean_by_class_and_need.values():
                if len(pair) != 2 or any(not isfinite(float(v)) or not 0 <= float(v) <= 1 for v in pair):
                    raise ValueError("difficulty means require (need, no-need) values in [0,1]")
            if self.prevalence_by_class is None and any(
                regime.realized_l1_service_factor_by_class is None for regime in self.regimes
            ):
                raise ValueError("class-conditional difficulty means require prevalence for expected L1 work")
        for regime in self.regimes:
            if not set(regime.arrival_rate_by_class) <= classes:
                raise ValueError("regime classes must have prevalence/classifier parameters")
            if regime.realized_l2_rate_by_class is None and self.prevalence_by_class is None:
                raise ValueError("expected L2 rates require prevalence and classifier probabilities")


@dataclass(frozen=True)
class RegimeCapacity:
    regime: str
    start_h: float
    end_h: float
    level: str
    capacity_per_h: float | None
    offered_rate_per_h: float
    relative_load: float | None
    load_status: str
    demand_basis: str
    unstaffed_classes: tuple[str, ...]
    analyst_utilization_at_capacity: tuple[tuple[str, float], ...]
    bottleneck_analysts: tuple[str, ...]
    offered_l1_work_h_per_h: float
    offered_l2_work_h_per_h: float


@dataclass(frozen=True)
class CapacityReport:
    regimes: tuple[RegimeCapacity, ...]
    alpha: float
    beta: float
    assumptions: tuple[str, ...]


def _calendar_capacity_fraction(calendar: Calendar | None) -> float:
    if calendar is None:
        return 1.0
    day, week = calendar.hours_per_day, calendar.hours_per_day * 7
    intervals = []
    for d, start, end in calendar.windows:
        a = d * day + start
        b = d * day + end + (day if end <= start else 0.0)
        if b <= week:
            intervals.append((a, b))
        else:
            intervals.extend(((a, week), (0.0, b - week)))
    intervals.sort()
    total = 0.0
    if intervals:
        lo, hi = intervals[0]
        for a, b in intervals[1:]:
            if a <= hi:
                hi = max(hi, b)
            else:
                total += hi - lo
                lo, hi = a, b
        total += hi - lo
    return min(1.0, total / week)


def realized_demand_regime(name: str, start_h: float, end_h: float, alerts: Sequence[Alert], *,
                           l2_route_by_alert: Mapping[str, bool],
                           true_need_by_alert: Mapping[str, bool],
                           difficulty_by_alert: Mapping[str, float], alpha: float, beta: float,
                           gamma: float = 1.0,
                           flow_mode: str = HISTORICAL_L1_THEN_L2,
                           route_basis: str = "simulated_route") -> DemandRegime:
    """Build empirical rates and mean effective service multipliers from a trace.

    The route, true-need and difficulty maps are evaluator-only, and explicitly
    describe what path was measured. No generator or policy is invoked.
    """
    if route_basis not in {"simulated_route", "true_need", "scenario_route"}:
        raise ValueError("route_basis must name simulated_route, scenario_route or true_need")
    if not isfinite(start_h) or not isfinite(end_h) or end_h <= start_h:
        raise ValueError("trace window must have finite end_h > start_h")
    if not isfinite(alpha) or not 0 < alpha <= 1 or not isfinite(beta) or not 0 <= beta < 2 or not isfinite(gamma) or gamma < 1:
        raise ValueError("alpha must be in (0,1], beta in [0,2), and gamma >= 1")
    if flow_mode not in FLOW_MODES:
        raise ValueError(f"flow_mode must be one of {sorted(FLOW_MODES)}")
    rows = tuple(a for a in alerts if start_h <= a.arrival < end_h)
    ids = {a.alert_id for a in rows}
    for label, values in (("route", l2_route_by_alert), ("need", true_need_by_alert),
                          ("difficulty", difficulty_by_alert)):
        if set(values) != ids:
            raise ValueError(f"{label} map must cover the selected trace alerts exactly")
    if any(not isinstance(l2_route_by_alert[x], bool) or not isinstance(true_need_by_alert[x], bool) for x in ids):
        raise ValueError("route and need sidecars must contain booleans")
    if any(not isfinite(float(difficulty_by_alert[x])) or not 0 <= float(difficulty_by_alert[x]) <= 1 for x in ids):
        raise ValueError("difficulty values must be in [0,1]")
    routes = true_need_by_alert if route_basis == "true_need" else l2_route_by_alert
    incoming, routed, l1_routed, l1_factors, l2_factors = {}, {}, {}, {}, {}
    for alert in rows:
        task_class = str(alert.task_class)
        incoming[task_class] = incoming.get(task_class, 0) + 1
        f_q = 1 + beta * (float(difficulty_by_alert[alert.alert_id]) - .5)
        path_l2 = bool(routes[alert.alert_id])
        if flow_mode == HISTORICAL_L1_THEN_L2 or not path_l2:
            l1_routed[task_class] = l1_routed.get(task_class, 0) + 1
            l1_m = (gamma if flow_mode == TRIAGE_SINGLE_INVESTIGATION and
                    true_need_by_alert[alert.alert_id] and not path_l2 else 1.0)
            l1_factors.setdefault(task_class, []).append(l1_m * f_q)
        if routes[alert.alert_id]:
            routed[task_class] = routed.get(task_class, 0) + 1
            m = 1.0 if true_need_by_alert[alert.alert_id] else alpha
            l2_factors.setdefault(task_class, []).append(m * f_q)
    duration = end_h - start_h
    return DemandRegime(
        name=name, start_h=start_h, end_h=end_h,
        arrival_rate_by_class={k: count / duration for k, count in incoming.items()},
        realized_l2_rate_by_class={k: count / duration for k, count in routed.items()},
        realized_l2_service_factor_by_class={k: mean(values) for k, values in l2_factors.items()},
        realized_l1_service_factor_by_class={k: mean(values) for k, values in l1_factors.items()},
        realized_l1_rate_by_class={k: count / duration for k, count in l1_routed.items()},
    )


def assess_capacity(organization: OrganizationConfig, profile: CapacityDemandProfile) -> CapacityReport:
    """Estimate class-constrained fluid capacity and load for each demand regime.

    Capacity uses the existing eligibility-constrained LP. Ratios above one mark
    structural overload for the given stationary regime; below one is not an SLA
    or stability guarantee for a finite trace.
    """
    if not isinstance(organization, OrganizationConfig) or not isinstance(profile, CapacityDemandProfile):
        raise TypeError("organization and profile must use the explicit scenario types")
    l1 = organization.resources_for("L1")
    l2 = organization.resources_for("L2")
    classes = tuple(sorted(profile.prevalence_by_class or {
        k for regime in profile.regimes for k in regime.arrival_rate_by_class
    }))
    base_l1 = {r.analyst.analyst_id: dict(r.service_by_class) for r in l1}
    base_l2 = {r.analyst.analyst_id: dict(r.service_by_class) for r in l2}
    # Expected recommended L2 service per routed alert. Under the synthetic
    # independence model E[f]=1. Optional conditional means represent dependence.
    service_factor = {}
    route_probability = {}
    l1_route_probability = {}
    l1_service_factor = {}
    for k in classes:
        if profile.prevalence_by_class is None:
            route_probability[k] = 0.0
            service_factor[k] = 1.0
            l1_route_probability[k] = 1.0
            l1_service_factor[k] = 1.0
            continue
        pi = float(profile.prevalence_by_class[k])
        pd = float(profile.sensitivity_by_class[k])
        pfa = float(profile.false_positive_rate_by_class[k])
        p_route = pi * pd + (1.0 - pi) * pfa
        route_probability[k] = p_route
        if profile.difficulty_mean_by_class_and_need is None:
            mean_q_need = mean_q_no_need = 0.5
        else:
            mean_q_need, mean_q_no_need = map(float, profile.difficulty_mean_by_class_and_need[k])
        ef_need = 1.0 + profile.beta * (mean_q_need - 0.5)
        ef_no_need = 1.0 + profile.beta * (mean_q_no_need - 0.5)
        numerator = pi * pd * ef_need + (1.0 - pi) * pfa * profile.alpha * ef_no_need
        service_factor[k] = numerator / p_route if p_route > 0 else 1.0
        p_l1 = (1.0 - pi) * (1.0 - pfa) + pi * (1.0 - pd)
        l1_route_probability[k] = 1.0 if profile.flow_mode == HISTORICAL_L1_THEN_L2 else p_l1
        if profile.difficulty_mean_by_class_and_need is None:
            mean_q_need = mean_q_no_need = 0.5
        else:
            mean_q_need, mean_q_no_need = map(float, profile.difficulty_mean_by_class_and_need[k])
        ef_need = 1.0 + profile.beta * (mean_q_need - 0.5)
        ef_no_need = 1.0 + profile.beta * (mean_q_no_need - 0.5)
        if profile.flow_mode == HISTORICAL_L1_THEN_L2:
            numerator_l1 = pi * ef_need + (1.0 - pi) * ef_no_need
            denominator_l1 = 1.0
        else:
            # L1 receives TN and FN only; gamma scales FN investigation effort.
            numerator_l1 = pi * (1.0 - pd) * profile.gamma * ef_need + (1.0 - pi) * (1.0 - pfa) * ef_no_need
            denominator_l1 = p_l1
        l1_service_factor[k] = numerator_l1 / denominator_l1 if denominator_l1 > 0 else 1.0
    results = []
    assumptions = ["Fluid LP; fractional assignment; one analyst-hour of work per available analyst-hour.",
                   "Expected L2 routing uses class-specific prevalence, sensitivity and false-positive rate.",
                   "Default difficulty factors have mean 1 (Beta(2,2), independent of need and recommendation).",
                   "A capacity ratio is pressure, not a stability or deadline guarantee."]
    assumptions.append(f"L1 routing/service uses flow_mode={profile.flow_mode}; gamma={profile.gamma:g} for FN effort.")
    if profile.difficulty_mean_by_class_and_need is not None:
        assumptions[2] = "Difficulty dependence uses caller-supplied E[q|class,need/no-need]; recommendation is conditionally independent of difficulty within need strata."
    for regime in profile.regimes:
        incoming = {k: float(regime.arrival_rate_by_class.get(k, 0.0)) for k in classes}
        incoming_l1 = ({k: incoming[k] * l1_route_probability[k] for k in classes}
                       if regime.realized_l1_rate_by_class is None else
                       {k: float(regime.realized_l1_rate_by_class.get(k, 0.0)) for k in classes})
        rate1 = sum(incoming_l1.values())
        share1 = {k: incoming_l1[k] / rate1 for k in classes} if rate1 else {k: 1.0 / len(classes) for k in classes}
        l1_factor = dict(l1_service_factor)
        if regime.realized_l1_service_factor_by_class is not None:
            l1_factor.update(regime.realized_l1_service_factor_by_class)
        class_service1 = {aid: {k: value * l1_factor[k] for k, value in m.items() if k in classes}
                          for aid, m in base_l1.items()}
        if regime.realized_l2_rate_by_class is None:
            incoming_l2 = {k: incoming[k] * route_probability[k] for k in classes}
            active_l2_factor = service_factor
            basis = "expected_classifier"
        else:
            incoming_l2 = {k: float(regime.realized_l2_rate_by_class.get(k, 0.0)) for k in classes}
            active_l2_factor = {k: float(regime.realized_l2_service_factor_by_class.get(k, 1.0))
                                for k in classes}
            basis = "realized_trace"
        l2_service = {aid: {k: value * active_l2_factor[k] for k, value in m.items() if k in classes}
                      for aid, m in base_l2.items()}
        rate2 = sum(incoming_l2.values())
        share2 = {k: incoming_l2[k] / rate2 for k in classes} if rate2 else {k: 1.0 / len(classes) for k in classes}
        def capacity_or_unstaffed(resources, services, shares):
            unstaffed = tuple(k for k in classes if shares[k] > 0 and
                              not any(k in r.analyst.eligible_classes for r in resources))
            if unstaffed:
                return {"max_common_arrivals_per_h": 0.0,
                        "fluid_utilization_at_capacity": [(r.analyst.analyst_id, 0.0) for r in resources]}, unstaffed
            result = effective_capacity(
                [r.analyst for r in resources], services, shares, classes=classes,
                capacity_by_analyst={r.analyst.analyst_id: _calendar_capacity_fraction(r.calendar)
                                     for r in resources},
            )
            return result, ()
        capacity1, unstaffed1 = (capacity_or_unstaffed(l1, class_service1, share1)
                                 if rate1 else (None, ()))
        capacity2, _ = (capacity_or_unstaffed(l2, l2_service, share2)
                        if rate2 else (None, ()))
        unstaffed1 = tuple(k for k in classes if incoming_l1[k] > 0 and not any(k in r.analyst.eligible_classes for r in l1))
        unstaffed2 = tuple(k for k in classes if incoming_l2[k] > 0 and not any(k in r.analyst.eligible_classes for r in l2))
        cap1 = float(capacity1["max_common_arrivals_per_h"]) if capacity1 else None
        cap2 = float(capacity2["max_common_arrivals_per_h"]) if capacity2 else None
        rho1 = rate1 / cap1 if cap1 and cap1 > 0 else (float("inf") if rate1 else None)
        rho2 = rate2 / cap2 if cap2 and cap2 > 0 else (float("inf") if rate2 else None)
        def status(rho, unstaffed):
            if rho is None:
                return "no_demand"
            if unstaffed:
                return "infeasible_eligibility"
            return "structural_overload" if rho > 1.0 + 1e-9 else "capacity_sufficient_mean"
        # Offered hours use the same average-eligible service convention as the
        # existing Q1 workload audit; LP capacity remains the assignment test.
        offered1 = sum(incoming_l1[k] * mean([base_l1[r.analyst.analyst_id][k] for r in l1
                                          if k in r.analyst.eligible_classes]) * l1_factor[k]
                       for k in classes if any(k in r.analyst.eligible_classes for r in l1))
        offered2 = sum(incoming_l2[k] * mean([base_l2[r.analyst.analyst_id][k] for r in l2
                                             if k in r.analyst.eligible_classes]) * active_l2_factor[k]
                       for k in classes if incoming_l2[k] and any(k in r.analyst.eligible_classes for r in l2))
        l1_basis = ("realized_trace" if regime.realized_l1_rate_by_class is not None else
                    "expected_negative_route" if profile.flow_mode == TRIAGE_SINGLE_INVESTIGATION else
                    "incoming_rate_by_class")
        results.extend((
            RegimeCapacity(regime.name, regime.start_h, regime.end_h, "L1", cap1, rate1, rho1, status(rho1, unstaffed1), l1_basis,
                           unstaffed1, tuple(capacity1["fluid_utilization_at_capacity"]) if capacity1 else (),
                           tuple(aid for aid, utilization in capacity1["fluid_utilization_at_capacity"] if utilization >= 1 - 1e-8) if capacity1 else (),
                           offered1, 0.0),
            RegimeCapacity(regime.name, regime.start_h, regime.end_h, "L2", cap2, rate2, rho2, status(rho2, unstaffed2), basis,
                           unstaffed2, tuple(capacity2["fluid_utilization_at_capacity"]) if capacity2 else (),
                           tuple(aid for aid, utilization in capacity2["fluid_utilization_at_capacity"] if utilization >= 1 - 1e-8) if capacity2 else (),
                           0.0, offered2),
        ))
    return CapacityReport(tuple(results), profile.alpha, profile.beta, tuple(assumptions))


@dataclass(frozen=True)
class QueueObservation:
    time_h: float
    queue_l1: int
    queue_l2: int
    pending_work_l1_h: float
    pending_work_l2_h: float


@dataclass(frozen=True)
class RecoveryAssessment:
    status: str
    recovery_time_h: float | None
    criterion: str
    evaluated_observations: int


def classify_regime_pressure(capacity: RegimeCapacity,
                             observations: Sequence[QueueObservation], *,
                             queue_threshold: int = 0,
                             pending_work_threshold_h: float = 0.0) -> str:
    """Separate steady structural pressure from temporal queue congestion."""
    if capacity.load_status == "infeasible_eligibility":
        return "infeasible_eligibility"
    if capacity.load_status == "no_demand":
        return "no_demand"
    if capacity.load_status == "structural_overload":
        return "structural_overload"
    if queue_threshold < 0 or not isfinite(pending_work_threshold_h) or pending_work_threshold_h < 0:
        raise ValueError("queue and pending-work thresholds must be finite and nonnegative")
    window = [x for x in observations if capacity.start_h <= x.time_h < capacity.end_h]
    if any((x.queue_l1 if capacity.level == "L1" else x.queue_l2) > queue_threshold or
           (x.pending_work_l1_h if capacity.level == "L1" else x.pending_work_l2_h) > pending_work_threshold_h
           for x in window):
        return "temporal_congestion_with_mean_capacity"
    return "capacity_sufficient_no_observed_congestion"


def assess_queue_recovery(observations: Sequence[QueueObservation], *, after_h: float,
                          queue_threshold: int = 0, pending_work_threshold_h: float = 0.0,
                          sustain_h: float = 0.0) -> RecoveryAssessment:
    """Find first sampled recovery point after a pulse using explicit thresholds.

    Recovery means both queues and both pending-work amounts remain at or below
    thresholds for observations spanning at least ``sustain_h``. This is a
    sampled-data criterion, not a continuous-time assertion between samples.
    """
    rows = tuple(sorted(observations, key=lambda x: x.time_h))
    if any(not isfinite(x.time_h) or min(x.queue_l1, x.queue_l2) < 0 or
           min(x.pending_work_l1_h, x.pending_work_l2_h) < 0 for x in rows):
        raise ValueError("queue observations must have finite times and nonnegative measures")
    if (not isfinite(after_h) or queue_threshold < 0 or
        not isfinite(pending_work_threshold_h) or pending_work_threshold_h < 0 or
        not isfinite(sustain_h) or sustain_h < 0):
        raise ValueError("recovery time and thresholds must be finite and nonnegative")
    if len({x.time_h for x in rows}) != len(rows):
        raise ValueError("queue observations must have unique sample times")
    eligible = [x for x in rows if x.time_h >= after_h]
    for i, first in enumerate(eligible):
        if (first.queue_l1 > queue_threshold or first.queue_l2 > queue_threshold or
                first.pending_work_l1_h > pending_work_threshold_h or
                first.pending_work_l2_h > pending_work_threshold_h):
            continue
        end = first.time_h + sustain_h
        window = [x for x in eligible[i:] if x.time_h <= end]
        if window and window[-1].time_h >= end and all(
            x.queue_l1 <= queue_threshold and x.queue_l2 <= queue_threshold and
            x.pending_work_l1_h <= pending_work_threshold_h and
            x.pending_work_l2_h <= pending_work_threshold_h for x in window
        ):
            return RecoveryAssessment("recovered", first.time_h,
                                      f"both queues <= {queue_threshold}; pending work <= {pending_work_threshold_h} h for {sustain_h} h on sampled observations",
                                      len(window))
    return RecoveryAssessment("not_observed_recovered", None,
                              f"both queues <= {queue_threshold}; pending work <= {pending_work_threshold_h} h for {sustain_h} h on sampled observations",
                              len(eligible))
