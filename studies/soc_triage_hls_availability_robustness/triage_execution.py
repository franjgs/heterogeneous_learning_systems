"""Triage-to-investigation orchestration over the existing execution backends.

This module routes environment-generated recommendations; it implements no
policy, classifier, or event loop. ``historical_l1_then_l2`` preserves the
former two-stage experiment flow. ``triage_single_investigation`` dispatches
one investigation directly to the recommended level.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from types import MappingProxyType
from typing import Mapping, Sequence

from hls.rq1_allocation import Alert
from studies.soc_triage_hls_availability_robustness.execution_api import (
    EnvironmentRealization, ExecutionBackend, ExecutionResult, OrganizationConfig,
    PolicyConfig, SimulationRequest, SimulationSettings, TaskExecution,
)

HISTORICAL_L1_THEN_L2 = "historical_l1_then_l2"
TRIAGE_SINGLE_INVESTIGATION = "triage_single_investigation"
FLOW_MODES = frozenset({HISTORICAL_L1_THEN_L2, TRIAGE_SINGLE_INVESTIGATION})


def _immutable(values: Mapping, name: str) -> Mapping:
    if not isinstance(values, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return MappingProxyType(dict(values))


@dataclass(frozen=True)
class TriageScenario:
    alerts: tuple[Alert, ...]
    organization: OrganizationConfig
    policies: Mapping[str, PolicyConfig]
    settings: SimulationSettings
    reference_escalation_by_alert: Mapping[str, bool]
    recommendation_l2_by_alert: Mapping[str, bool]
    difficulty_by_alert: Mapping[str, float]
    alpha: float
    difficulty_service_beta: float = 0.0
    gamma: float = 1.0

    def __post_init__(self):
        alerts = tuple(self.alerts)
        ids = {a.alert_id for a in alerts}
        if len(ids) != len(alerts) or any(not isinstance(a, Alert) for a in alerts):
            raise ValueError("alerts must be unique existing Alert records")
        reference = _immutable(self.reference_escalation_by_alert, "reference_escalation_by_alert")
        recommendation = _immutable(self.recommendation_l2_by_alert, "recommendation_l2_by_alert")
        difficulty = _immutable(self.difficulty_by_alert, "difficulty_by_alert")
        for name, values in (("reference_escalation_by_alert", reference),
                             ("recommendation_l2_by_alert", recommendation),
                             ("difficulty_by_alert", difficulty)):
            if set(values) != ids:
                raise ValueError(f"{name} must cover exactly the supplied alerts")
        if any(not isinstance(x, bool) for x in reference.values()):
            raise ValueError("reference escalation values must be booleans")
        if any(not isinstance(x, bool) for x in recommendation.values()):
            raise ValueError("recommendation values must be booleans")
        if any(not isfinite(float(x)) or not 0 <= float(x) <= 1 for x in difficulty.values()):
            raise ValueError("difficulty values must be finite and in [0,1]")
        alpha, beta, gamma = map(float, (self.alpha, self.difficulty_service_beta, self.gamma))
        if not isfinite(alpha) or not 0 < alpha <= 1:
            raise ValueError("alpha must be finite and in (0,1]")
        if not isfinite(beta) or not 0 <= beta < 2:
            raise ValueError("difficulty_service_beta must be finite and in [0,2)")
        if not isfinite(gamma) or gamma < 1:
            raise ValueError("gamma must be finite and at least 1")
        policies = _immutable(self.policies, "policies")
        if set(policies) != {"L1", "L2"} or any(not isinstance(p, PolicyConfig) for p in policies.values()):
            raise ValueError("policies must contain PolicyConfig values for L1 and L2")
        # Validate that both teams exist before beginning either stage.
        self.organization.resources_for("L1")
        self.organization.resources_for("L2")
        object.__setattr__(self, "alerts", alerts)
        object.__setattr__(self, "reference_escalation_by_alert", reference)
        object.__setattr__(self, "recommendation_l2_by_alert", recommendation)
        object.__setattr__(self, "difficulty_by_alert", difficulty)
        object.__setattr__(self, "policies", policies)
        object.__setattr__(self, "alpha", alpha)
        object.__setattr__(self, "difficulty_service_beta", beta)
        object.__setattr__(self, "gamma", gamma)


@dataclass(frozen=True)
class AlertOutcome:
    alert_id: str
    route_level: str
    final_investigation_level: str
    confusion: str
    status: str  # completed_within_sla | completed_late | pending
    completion: float | None
    deadline: float
    analyst_id: str | None
    investigation_count: int


@dataclass(frozen=True)
class TriageExecutionResult:
    flow_mode: str
    outcomes: tuple[AlertOutcome, ...]
    stage_results: Mapping[str, ExecutionResult]
    cutoff: float

    def __post_init__(self):
        object.__setattr__(self, "outcomes", tuple(self.outcomes))
        object.__setattr__(self, "stage_results", MappingProxyType(dict(self.stage_results)))

    @property
    def status_counts(self) -> Mapping[str, int]:
        counts = {"completed_within_sla": 0, "completed_late": 0, "pending": 0}
        for outcome in self.outcomes:
            counts[outcome.status] += 1
        return MappingProxyType(counts)

    @property
    def status_fractions(self) -> Mapping[str, float]:
        n = len(self.outcomes)
        return MappingProxyType({key: value / n if n else 0.0
                                 for key, value in self.status_counts.items()})


def _confusion(reference: bool, recommendation: bool) -> str:
    if reference and recommendation:
        return "TP"
    if reference:
        return "FN"
    if recommendation:
        return "FP"
    return "TN"


def _stage_scales(scenario: TriageScenario, alerts: Sequence[Alert], level: str,
                  flow_mode: str) -> EnvironmentRealization | None:
    scales = {}
    for alert in alerts:
        ref = scenario.reference_escalation_by_alert[alert.alert_id]
        rec = scenario.recommendation_l2_by_alert[alert.alert_id]
        if flow_mode == HISTORICAL_L1_THEN_L2:
            # The old L1 stage is always a complete investigation; its old FN
            # behavior is intentionally preserved (no gamma factor).
            scale = (scenario.alpha if level == "L2" and not ref else 1.0)
        else:
            scale = (scenario.alpha if level == "L2" and not ref else
                     scenario.gamma if level == "L1" and ref and not rec else 1.0)
        scales[alert.alert_id] = scale
    hidden_need = ({a.alert_id: scenario.reference_escalation_by_alert[a.alert_id]
                    for a in alerts}
                   if flow_mode == HISTORICAL_L1_THEN_L2 and level == "L2" else None)
    if (hidden_need is None and scenario.difficulty_service_beta == 0 and
            all(x == 1.0 for x in scales.values())):
        return None
    return EnvironmentRealization(
        service_scale_by_alert=scales,
        hidden_need_by_alert=hidden_need,
        difficulty_by_alert={a.alert_id: scenario.difficulty_by_alert[a.alert_id] for a in alerts},
        difficulty_service_beta=scenario.difficulty_service_beta,
    )


def _stage_request(scenario: TriageScenario, alerts: Sequence[Alert], level: str,
                   settings: SimulationSettings, flow_mode: str) -> SimulationRequest:
    rows = tuple(alerts)
    env = _stage_scales(scenario, rows, level, flow_mode)
    return SimulationRequest(rows, scenario.organization, level, scenario.policies[level],
                             settings, env)


def _task_from_result(result: ExecutionResult, alert: Alert) -> TaskExecution:
    return result.tasks_by_alert.get(alert.alert_id, TaskExecution(alert.alert_id))


def _outcome_status(task: TaskExecution, deadline: float, cutoff: float) -> str:
    if task.completion is None or task.completion > cutoff:
        return "pending"
    return "completed_within_sla" if task.completion <= deadline else "completed_late"


def run_triage_flow(scenario: TriageScenario, *, flow_mode: str,
                    backend: ExecutionBackend | Mapping[str, ExecutionBackend]) -> TriageExecutionResult:
    """Execute the explicitly selected workflow with an existing backend.

    All input traces and recommendation draws are supplied by the caller; this
    function consumes no random numbers except the selected backend's unchanged
    policy event loop.
    """
    if flow_mode not in FLOW_MODES:
        raise ValueError(f"flow_mode must be one of {sorted(FLOW_MODES)}")
    if isinstance(backend, Mapping):
        if set(backend) != {"L1", "L2"}:
            raise ValueError("backend mapping must define exactly L1 and L2")
        backends = dict(backend)
    else:
        backends = {"L1": backend, "L2": backend}
    if any(not callable(getattr(item, "run", None)) for item in backends.values()):
        raise TypeError("backend values must implement the existing execution backend interface")
    settings = scenario.settings
    factor = settings.time_scale.factor
    cutoff = settings.evaluation_horizon * factor
    admitted = tuple(a for a in scenario.alerts if a.arrival < settings.admission_horizon)
    stage_results: dict[str, ExecutionResult] = {}
    tasks_by_id: dict[str, TaskExecution] = {}
    final_levels: dict[str, str] = {}
    investigation_counts: dict[str, int] = {}

    if flow_mode == TRIAGE_SINGLE_INVESTIGATION:
        for level in ("L1", "L2"):
            rows = tuple(a for a in admitted
                         if scenario.recommendation_l2_by_alert[a.alert_id] == (level == "L2"))
            request = _stage_request(scenario, rows, level, settings, flow_mode)
            result = backends[level].run(request)
            stage_results[level] = result
            for alert in rows:
                tasks_by_id[alert.alert_id] = _task_from_result(result, alert)
                final_levels[alert.alert_id] = level
                investigation_counts[alert.alert_id] = 1
    else:
        l1_request = _stage_request(scenario, admitted, "L1", settings, flow_mode)
        l1 = backends["L1"].run(l1_request)
        stage_results["L1"] = l1
        l1_tasks = {a.alert_id: _task_from_result(l1, a) for a in admitted}
        l2_input: list[Alert] = []
        for alert in admitted:
            task = l1_tasks[alert.alert_id]
            completion = task.completion
            if (scenario.recommendation_l2_by_alert[alert.alert_id] and
                    completion is not None and completion < cutoff):
                l2_input.append(Alert(alert.alert_id, completion / factor,
                                      alert.task_class, alert.deadline / factor))
        # A second historical stage can start after the original admission
        # window and even after its deadline. Equality means no drain at cutoff.
        l2_settings = replace(settings, admission_horizon=settings.evaluation_horizon)
        l2_request = _stage_request(scenario, l2_input, "L2", l2_settings, flow_mode)
        l2 = backends["L2"].run(l2_request)
        stage_results["L2"] = l2
        for alert in admitted:
            first = l1_tasks[alert.alert_id]
            if alert.alert_id in l2.tasks_by_alert:
                tasks_by_id[alert.alert_id] = l2.tasks_by_alert[alert.alert_id]
                final_levels[alert.alert_id] = "L2"
                investigation_counts[alert.alert_id] = 2
            else:
                tasks_by_id[alert.alert_id] = first
                final_levels[alert.alert_id] = "L1"
                investigation_counts[alert.alert_id] = 1

    outcomes = []
    for alert in admitted:
        task = tasks_by_id[alert.alert_id]
        recommendation = scenario.recommendation_l2_by_alert[alert.alert_id]
        outcomes.append(AlertOutcome(
            alert.alert_id,
            "L2" if recommendation else "L1",
            final_levels[alert.alert_id],
            _confusion(scenario.reference_escalation_by_alert[alert.alert_id], recommendation),
            _outcome_status(task, alert.deadline * factor, cutoff),
            task.completion, alert.deadline * factor, task.analyst_id,
            investigation_counts[alert.alert_id],
        ))
    return TriageExecutionResult(flow_mode, tuple(outcomes), stage_results, cutoff)
