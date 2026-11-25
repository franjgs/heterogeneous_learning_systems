"""Immutable scenario inputs and thin adapters for existing HLS engines.

This module deliberately does not implement an event loop or dispatch policy.
The engine-native result is retained on every ``ExecutionResult``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from hls.rq1_allocation import (
    Alert, Analyst, Assignment, HLSADecision, HLSBConfig,
    simulate as simulate_continuous,
)
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    Calendar, CONTINUOUS,
    TimeScale, simulate as simulate_calendar,
)


def _frozen_map(values: Mapping) -> Mapping:
    return MappingProxyType(dict(values))


def _validate_positive_map(name: str, values: Mapping, *, allow_zero: bool = False) -> Mapping:
    frozen = _frozen_map(values)
    for key, value in frozen.items():
        if not isinstance(value, (int, float)) or not isfinite(float(value)):
            raise ValueError(f"{name}[{key!r}] must be finite")
        invalid = float(value) < 0 if allow_zero else float(value) <= 0
        if invalid:
            bound = "nonnegative" if allow_zero else "positive"
            raise ValueError(f"{name}[{key!r}] must be {bound}")
    return frozen


def _validate_competence(values: Mapping) -> Mapping:
    frozen = _frozen_map(values)
    for key, value in frozen.items():
        if not isinstance(value, (int, float)) or not isfinite(float(value)) or not 0 <= value <= 1:
            raise ValueError(f"competence[{key!r}] must be finite and in [0,1]")
    return frozen


@dataclass(frozen=True)
class AnalystResource:
    """One immutable analyst resource; ``Analyst`` remains the domain model.

    Service maps must cover exactly the analyst's eligible classes. Forecast
    service defaults to the same immutable values as actual service. A calendar
    may be absent for a continuous-only roster; CalendarBackend requires it.
    """

    analyst: Analyst
    service_by_class: Mapping
    calendar: Calendar | None = None
    forecast_service_by_class: Mapping | None = None

    def __post_init__(self):
        if not isinstance(self.analyst, Analyst) or not self.analyst.analyst_id:
            raise ValueError("analyst must be an existing Analyst with a nonempty ID")
        eligible = frozenset(self.analyst.eligible_classes)
        competence = _validate_competence(self.analyst.competence)
        actual = _validate_positive_map("service_by_class", self.service_by_class)
        forecast = _validate_positive_map(
            "forecast_service_by_class",
            self.service_by_class if self.forecast_service_by_class is None
            else self.forecast_service_by_class,
        )
        if not eligible:
            raise ValueError("analyst eligibility must contain at least one class")
        if set(competence) != eligible:
            raise ValueError("competence keys must match analyst eligibility exactly")
        if set(actual) != eligible or set(forecast) != eligible:
            raise ValueError("actual and forecast service keys must match eligibility exactly")
        # Freeze the nested mapping in Analyst too; frozen dataclasses alone are shallow.
        analyst = Analyst(self.analyst.analyst_id, eligible, competence)
        calendar = self.calendar
        if calendar is not None:
            if not isinstance(calendar, Calendar):
                raise ValueError("calendar must be a Calendar or None")
            if not isfinite(float(calendar.hours_per_day)) or calendar.hours_per_day <= 0:
                raise ValueError("calendar hours_per_day must be finite and positive")
            try:
                calendar = Calendar(tuple((int(d), float(a), float(b))
                                          for d, a, b in calendar.windows),
                                    float(calendar.hours_per_day))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid analyst calendar: {exc}") from exc
        object.__setattr__(self, "analyst", analyst)
        object.__setattr__(self, "service_by_class", actual)
        object.__setattr__(self, "forecast_service_by_class", forecast)
        object.__setattr__(self, "calendar", calendar)


@dataclass(frozen=True)
class TeamConfig:
    level: str
    analyst_ids: tuple[str, ...]

    def __post_init__(self):
        ids = tuple(self.analyst_ids)
        if self.level not in {"L1", "L2"}:
            raise ValueError("team level must be L1 or L2")
        if not ids or any(not isinstance(x, str) or not x for x in ids):
            raise ValueError("a team must contain nonempty analyst IDs")
        if len(ids) != len(set(ids)):
            raise ValueError("team analyst IDs must be unique")
        object.__setattr__(self, "analyst_ids", ids)


@dataclass(frozen=True)
class OrganizationConfig:
    analysts: tuple[AnalystResource, ...]
    teams: tuple[TeamConfig, ...]

    def __post_init__(self):
        analysts, teams = tuple(self.analysts), tuple(self.teams)
        ids = [r.analyst.analyst_id for r in analysts]
        if len(ids) != len(set(ids)):
            raise ValueError("analyst IDs must be globally unique")
        if len({t.level for t in teams}) != len(teams):
            raise ValueError("organization may define at most one team per level")
        known, assigned = set(ids), []
        for team in teams:
            unknown = set(team.analyst_ids) - known
            if unknown:
                raise ValueError(f"team {team.level} references unknown analysts: {sorted(unknown)}")
            assigned.extend(team.analyst_ids)
        if len(assigned) != len(set(assigned)):
            raise ValueError("an analyst cannot belong to multiple teams")
        if set(assigned) != known:
            raise ValueError("every configured analyst must belong to exactly one team")
        object.__setattr__(self, "analysts", analysts)
        object.__setattr__(self, "teams", teams)

    def resources_for(self, level: str) -> tuple[AnalystResource, ...]:
        team = next((t for t in self.teams if t.level == level), None)
        if team is None:
            raise ValueError(f"organization has no {level} team")
        by_id = {r.analyst.analyst_id: r for r in self.analysts}
        return tuple(by_id[aid] for aid in team.analyst_ids)


@dataclass(frozen=True)
class PolicyConfig:
    name: str
    waps: HLSBConfig | None = None

    def __post_init__(self):
        if self.name not in {"D1", "P1", "WAPS"}:
            raise ValueError("policy must be D1, P1 or WAPS")
        if (self.name == "WAPS") != (self.waps is not None):
            raise ValueError("WAPS requires HLSBConfig; other policies do not take it")


@dataclass(frozen=True)
class DeadlineConfig:
    """Optional metadata for configured natural-time offsets.

    Alert.deadline remains the authoritative absolute deadline passed to an
    engine; this type never rewrites or derives it.
    """

    offsets_by_severity_h: Mapping = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "offsets_by_severity_h",
                           _validate_positive_map("deadline offset", self.offsets_by_severity_h,
                                                  allow_zero=True))


@dataclass(frozen=True)
class SimulationSettings:
    admission_horizon: float
    evaluation_horizon: float
    seed: int
    time_scale: TimeScale
    deadlines: DeadlineConfig

    def __post_init__(self):
        for name, value in (("admission_horizon", self.admission_horizon),
                            ("evaluation_horizon", self.evaluation_horizon)):
            if not isfinite(float(value)) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        if self.admission_horizon <= 0:
            raise ValueError("admission_horizon must be positive")
        if self.evaluation_horizon <= self.admission_horizon:
            raise ValueError("evaluation_horizon must be later than admission_horizon")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool):
            raise ValueError("seed must be an integer")
        if not isinstance(self.time_scale, TimeScale) or not isfinite(self.time_scale.factor) or self.time_scale.factor <= 0:
            raise ValueError("time_scale must be finite and positive")
        if not isinstance(self.deadlines, DeadlineConfig):
            raise ValueError("deadlines must be a DeadlineConfig")


@dataclass(frozen=True)
class EnvironmentRealization:
    """Environment-only service realization; never passed to a dispatcher."""

    service_scale_by_alert: Mapping[str, float] | None = None
    hidden_need_by_alert: Mapping[str, bool] | None = None

    def __post_init__(self):
        if self.service_scale_by_alert is not None:
            scales = _frozen_map(self.service_scale_by_alert)
            for aid, value in scales.items():
                if not aid or not isfinite(float(value)) or not 0 < value <= 1:
                    raise ValueError("service scales must be finite, in (0,1], and keyed by alert ID")
            object.__setattr__(self, "service_scale_by_alert", scales)
        if self.hidden_need_by_alert is not None:
            needs = _frozen_map(self.hidden_need_by_alert)
            if any(not aid or not isinstance(value, bool) for aid, value in needs.items()):
                raise ValueError("hidden need must contain booleans keyed by alert ID")
            object.__setattr__(self, "hidden_need_by_alert", needs)


@dataclass(frozen=True)
class SimulationRequest:
    alerts: tuple[Alert, ...]
    organization: OrganizationConfig
    level: str
    policy: PolicyConfig
    settings: SimulationSettings
    environment: EnvironmentRealization | None = None

    def __post_init__(self):
        alerts = tuple(self.alerts)
        if self.level not in {"L1", "L2"}:
            raise ValueError("request level must be L1 or L2")
        if not isinstance(self.organization, OrganizationConfig):
            raise ValueError("organization must be an OrganizationConfig")
        resources = self.organization.resources_for(self.level)
        if not resources:
            raise ValueError(f"{self.level} team must contain an analyst")
        if not isinstance(self.policy, PolicyConfig) or not isinstance(self.settings, SimulationSettings):
            raise ValueError("policy and settings must use the explicit config types")
        if self.environment is not None and not isinstance(self.environment, EnvironmentRealization):
            raise ValueError("environment must be an EnvironmentRealization or None")
        if any(not isinstance(a, Alert) for a in alerts):
            raise ValueError("alerts must use the existing Alert type")
        if len({a.alert_id for a in alerts}) != len(alerts):
            raise ValueError("alert IDs must be unique")
        if any(not a.alert_id or not isfinite(a.arrival) or a.arrival < 0 or
               not isfinite(a.deadline) or a.deadline < a.arrival for a in alerts):
            raise ValueError("alerts require IDs and finite arrival-relative natural-time deadlines")
        for alert in alerts:
            eligible = [r for r in resources if alert.task_class in r.analyst.eligible_classes]
            if alert.arrival < self.settings.admission_horizon and not eligible:
                raise ValueError(f"no {self.level} analyst is eligible for {alert.task_class!r}")
        admitted_ids = {a.alert_id for a in alerts if a.arrival < self.settings.admission_horizon}
        if self.environment is not None:
            for name in ("service_scale_by_alert", "hidden_need_by_alert"):
                values = getattr(self.environment, name)
                if values is not None and set(values) != admitted_ids:
                    raise ValueError(f"{name} must cover exactly the admitted alerts")
            has_realization = (self.environment.service_scale_by_alert is not None or
                               self.environment.hidden_need_by_alert is not None)
            if has_realization and (self.environment.service_scale_by_alert is None or
                                    self.environment.hidden_need_by_alert is None):
                # The historical hidden-work engine requires both maps for validation.
                # CalendarBackend itself only consumes service scales.
                pass
        object.__setattr__(self, "alerts", alerts)

    @property
    def resources(self) -> tuple[AnalystResource, ...]:
        return self.organization.resources_for(self.level)


@dataclass(frozen=True)
class TaskExecution:
    """Per-alert view; None means the selected native engine did not expose it."""

    alert_id: str
    analyst_id: str | None = None
    start: float | None = None
    completion: float | None = None
    effective_work: float | None = None
    remaining_work: float | None = None
    suspension: float | None = None
    status: str | None = None


@dataclass(frozen=True)
class WorkSegment:
    alert_id: str
    analyst_id: str
    start: float
    end: float


@dataclass(frozen=True)
class ExecutionResult:
    assignments: tuple[Assignment, ...]
    tasks_by_alert: Mapping[str, TaskExecution]
    work_segments: tuple[WorkSegment, ...] | None
    policy_decisions: tuple[HLSADecision, ...] | None
    native_result: Any = field(compare=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, "assignments", tuple(self.assignments))
        object.__setattr__(self, "tasks_by_alert", _frozen_map(self.tasks_by_alert))
        if self.work_segments is not None:
            object.__setattr__(self, "work_segments", tuple(self.work_segments))
        if self.policy_decisions is not None:
            object.__setattr__(self, "policy_decisions", tuple(self.policy_decisions))


@runtime_checkable
class ExecutionBackend(Protocol):
    def run(self, request: SimulationRequest) -> ExecutionResult: ...


def _scaled_inputs(request: SimulationRequest):
    """Create scaled copies; inputs and engine implementations remain untouched."""
    factor = request.settings.time_scale.factor
    alerts = tuple(Alert(a.alert_id, a.arrival * factor, a.task_class, a.deadline * factor)
                   for a in request.alerts)
    resources = request.resources
    analysts = tuple(r.analyst for r in resources)
    actual = {r.analyst.analyst_id: {k: v * factor for k, v in r.service_by_class.items()}
              for r in resources}
    forecast = {r.analyst.analyst_id: {k: v * factor for k, v in r.forecast_service_by_class.items()}
                for r in resources}
    calendars = {r.analyst.analyst_id: (r.calendar or CONTINUOUS).scaled(factor)
                 for r in resources}
    cfg = request.policy.waps
    if cfg is not None:
        cfg = HLSBConfig(cfg.window_h * factor, cfg.low, cfg.high, cfg.capacity_per_h / factor)
    return alerts, analysts, actual, forecast, calendars, cfg, factor


def _service_by_class(resources: Sequence[AnalystResource]) -> dict:
    result = {}
    for resource in resources:
        for task_class, value in resource.service_by_class.items():
            result.setdefault(task_class, value)
    return result


def _continuous_task_view(alerts, assignments):
    by_assignment = {a.alert_id: a for a in assignments}
    tasks = {}
    for alert in alerts:
        job = by_assignment.get(alert.alert_id)
        # The allocation engine has no task-level status/work ledger. Preserve
        # fields directly available in Assignment; leave the rest unavailable.
        tasks[alert.alert_id] = TaskExecution(
            alert.alert_id,
            job.analyst_id if job is not None else None,
            job.start if job is not None else None,
            job.completion if job is not None else None,
        )
    return tasks


class ContinuousBackend:
    """Delegate to the historical fixed-policy engine; never executes calendars."""

    def run(self, request: SimulationRequest) -> ExecutionResult:
        if not isinstance(request, SimulationRequest):
            raise TypeError("request must be a SimulationRequest")
        alerts, analysts, actual, forecast, _calendars, waps, factor = _scaled_inputs(request)
        admitted = tuple(a for a in alerts if a.arrival < request.settings.admission_horizon * factor)
        policy = "HLS-B" if request.policy.name == "WAPS" else request.policy.name
        environment = request.environment
        if environment is not None and (environment.service_scale_by_alert is not None or
                                        environment.hidden_need_by_alert is not None):
            if environment.service_scale_by_alert is None or environment.hidden_need_by_alert is None:
                raise ValueError("continuous hidden-work execution requires both environment maps")
            from studies.soc_triage_hls_q1_integration_evidence.fp_workload_engine import (
                simulate_l2_hidden_work,
            )
            scales = environment.service_scale_by_alert
            needs = environment.hidden_need_by_alert
            native = simulate_l2_hidden_work(
                admitted, needs, analysts, actual, forecast, scales,
                policy=policy, horizon=request.settings.evaluation_horizon * factor,
                seed=request.settings.seed, hlsb_config=waps,
            )
            assignments = native.assignments
            decisions = tuple(native.switches) if request.policy.name == "WAPS" else None
        else:
            if actual != forecast:
                raise ValueError("different actual/forecast service requires environment realization")
            native = simulate_continuous(
                alerts, analysts, _service_by_class(request.resources),
                policy=policy,
                admission_horizon=request.settings.admission_horizon * factor,
                drain_period=(request.settings.evaluation_horizon-
                             request.settings.admission_horizon) * factor,
                random_seed=request.settings.seed,
                service_by_analyst_class=actual,
                hlsb_config=waps,
            )
            assignments = native.assignments
            decisions = tuple(native.hlsa_history) if request.policy.name == "WAPS" else None
        tasks = _continuous_task_view(admitted, assignments)
        return ExecutionResult(tuple(assignments), tasks, None, decisions, native)


class CalendarBackend:
    """Delegate to the existing weekly-calendar event engine."""

    def run(self, request: SimulationRequest) -> ExecutionResult:
        if not isinstance(request, SimulationRequest):
            raise TypeError("request must be a SimulationRequest")
        resources = request.resources
        missing = [r.analyst.analyst_id for r in resources if r.calendar is None]
        if missing:
            raise ValueError(f"CalendarBackend requires a calendar for every analyst: {missing}")
        alerts, analysts, actual, forecast, calendars, waps, factor = _scaled_inputs(request)
        admitted = tuple(a for a in alerts if a.arrival < request.settings.admission_horizon * factor)
        env = request.environment
        scales = None if env is None else env.service_scale_by_alert
        # hidden_need_by_alert is deliberately not forwarded; the dispatcher
        # sees alerts, roster, and ex-ante service only.
        native = simulate_calendar(
            admitted, analysts, forecast, calendars,
            horizon=request.settings.evaluation_horizon * factor,
            policy=request.policy.name, seed=request.settings.seed,
            waps_config=waps, actual_service=actual,
            realized_scale_by_alert=scales,
        )
        episodes = {e.alert_id: e for e in native.episodes}
        assignments = {a.alert_id: a for a in native.assignments}
        work = dict(native.work_done_by_alert)
        states = {
            aid: TaskExecution(e.alert_id,
                               e.analyst_id or (assignments[aid].analyst_id if aid in assignments else None),
                               e.start, e.completion,
                               work.get(aid),
                               None if e.status == "queued" else e.remaining_service_h,
                               e.suspension_h, e.status)
            for aid, e in episodes.items()
        }
        segments = tuple(WorkSegment(aid, analyst_id, start, end)
                         for aid, analyst_id, start, end in native.work_segments)
        decisions = tuple(native.switches) if request.policy.name == "WAPS" else None
        return ExecutionResult(tuple(native.assignments), states, segments, decisions, native)


def _finite_positive(value: float, label: str) -> None:
    if not isfinite(float(value)) or value <= 0:
        raise ValueError(f"{label} must be finite and positive")

