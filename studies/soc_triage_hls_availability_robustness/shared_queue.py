"""Shared junior/senior organization adapter using the existing HLS policies.

The native engine receives one common analyst pool and one pending-alert map.
Project and investigation kind are encoded in task classes solely to express
eligibility; policy implementations are delegated unchanged to rq1_allocation
or availability_engine.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from math import isfinite
from pathlib import Path
import random
import sys
from types import MappingProxyType
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from hls.rq1_allocation import Alert, Analyst, HLSBConfig, simulate as simulate_continuous
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, Calendar, simulate as simulate_calendar,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import (
    LoadedScenario, load_scenario,
)
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity


DEFAULT_CONFIG = ROOT / "studies/soc_triage_hls_availability_robustness/config/SOC_SHARED_QUEUE_JUNIOR_SENIOR_SOCTRA_V1.json"
ORDINARY = "ordinary"
SPECIALIZED = "specialized"
RESEARCH_TYPES = (ORDINARY, SPECIALIZED)


def task_class(project: str, research_type: str) -> str:
    if not project or research_type not in RESEARCH_TYPES:
        raise ValueError("project and a recognized research type are required")
    return f"{project}::{research_type}"


def split_task_class(value: str) -> tuple[str, str]:
    try:
        project, research_type = value.rsplit("::", 1)
    except ValueError as exc:
        raise ValueError(f"invalid shared task class {value!r}") from exc
    if not project or research_type not in RESEARCH_TYPES:
        raise ValueError(f"invalid shared task class {value!r}")
    return project, research_type


@dataclass(frozen=True)
class SharedOrganization:
    resources: tuple
    role_by_analyst: Mapping[str, str]
    queue_name: str = "shared_alert_queue"

    def __post_init__(self):
        resources = tuple(self.resources)
        roles = dict(self.role_by_analyst)
        resource_ids = [r.analyst.analyst_id for r in resources]
        ids = set(resource_ids)
        if (not resources or len(ids) != len(resources) or set(roles) != ids or
                any(x not in {"junior", "senior"} for x in roles.values())):
            raise ValueError("shared organization needs one junior/senior role per analyst")
        if not self.queue_name:
            raise ValueError("shared queue must have a name")
        for resource in resources:
            role = roles[resource.analyst.analyst_id]
            types = {split_task_class(k)[1] for k in resource.analyst.eligible_classes}
            if role == "junior" and types != {ORDINARY}:
                raise ValueError("juniors may only be eligible for ordinary investigations")
            if role == "senior" and types != set(RESEARCH_TYPES):
                raise ValueError("seniors must be eligible for ordinary and specialized work")
        object.__setattr__(self, "resources", resources)
        object.__setattr__(self, "role_by_analyst", MappingProxyType(roles))

    @property
    def analysts(self) -> tuple[Analyst, ...]:
        return tuple(r.analyst for r in self.resources)

    def role(self, analyst_id: str) -> str:
        return self.role_by_analyst[analyst_id]


@dataclass(frozen=True)
class SharedQueueScenario:
    scenario_id: str
    description: str
    source: LoadedScenario
    organization: SharedOrganization
    policy_default: str
    available_policies: tuple[str, ...]
    hlsb: HLSBConfig
    prevalence_by_project: Mapping[str, float]
    config_path: Path

    @property
    def demand_profile(self) -> Mapping:
        return self.source.demand_profile


@dataclass(frozen=True)
class AlertContext:
    project: str
    severity: str
    difficulty: float
    need_l2: bool
    recommended_l2: bool
    research_type: str


@dataclass(frozen=True)
class SharedTrace:
    alerts: tuple[Alert, ...]
    context_by_alert: Mapping[str, AlertContext]

    def __post_init__(self):
        alerts = tuple(self.alerts)
        contexts = dict(self.context_by_alert)
        ids = {a.alert_id for a in alerts}
        if len(ids) != len(alerts) or set(contexts) != ids:
            raise ValueError("shared trace requires unique alerts and one context per alert")
        object.__setattr__(self, "alerts", alerts)
        object.__setattr__(self, "context_by_alert", MappingProxyType(contexts))


@dataclass(frozen=True)
class SLAGroupMetric:
    severity: str
    research_type: str
    arrivals: int
    completed_within_sla: int
    completed_late: int
    pending: int


@dataclass(frozen=True)
class SharedExecutionResult:
    policy: str
    native_result: object
    assignments: tuple
    queue_length_at_cutoff: int
    maximum_queue_length: int
    pending_at_cutoff: int
    arrivals_by_type: Mapping[str, int]
    closures_by_type: Mapping[str, int]
    offered_work_by_type_h: Mapping[str, float]
    service_work_by_role_type_h: Mapping[str, float]
    utilization_by_analyst: Mapping[str, float]
    utilization_by_role: Mapping[str, float]
    mean_wait_h: float | None
    mean_service_h: float | None
    mean_resolution_h: float | None
    sla_by_severity_type: tuple[SLAGroupMetric, ...]
    expected_quality_by_type: Mapping[str, float | None]
    investigation_count_by_alert: Mapping[str, int]


def _calendar(spec: Mapping | None, fallback: Calendar | None) -> Calendar:
    if spec is None or spec.get("kind") == "inherit":
        return fallback or CONTINUOUS
    if spec.get("kind") == "continuous":
        return CONTINUOUS
    if spec.get("kind") == "weekly":
        windows = tuple((int(d), float(a), float(b)) for d, a, b in spec.get("windows", ()))
        return Calendar(windows, float(spec.get("hours_per_day", 24.0)))
    raise ValueError("calendar kind must be inherit, continuous or weekly")


def _routing_probabilities(p: float, sensitivity: float, fpr: float) -> dict[str, float]:
    return {"TP": p * sensitivity, "FN": p * (1 - sensitivity),
            "FP": (1 - p) * fpr, "TN": (1 - p) * (1 - fpr)}


def _conditional_mean(values: Mapping[str, float], q_need: float,
                      q_ordinary: float, labels: Sequence[str]) -> float:
    mass = sum(values[x] for x in labels)
    if mass <= 0:
        return 0.5
    return sum(values[x] * (q_need if x in {"TP", "FN"} else q_ordinary)
               for x in labels) / mass


def _beta22_conditional_means(prevalence: float) -> tuple[float, float]:
    q0 = _q0_for_prevalence(prevalence)
    first_moment_need = .5 - 2 * q0 ** 3 + 1.5 * q0 ** 4
    mean_need = first_moment_need / prevalence
    mean_ordinary = (.5 - prevalence * mean_need) / (1 - prevalence)
    return mean_need, mean_ordinary


def load_shared_scenario(path: str | Path = DEFAULT_CONFIG) -> SharedQueueScenario:
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("schema_version") != 1:
        raise ValueError("unsupported shared-queue config schema")
    source_path = (path.parent / cfg["source_scenario_config"]).resolve()
    source = load_scenario(source_path)
    org_cfg = cfg["organization"]
    if source.flow_mode != "triage_single_investigation":
        raise ValueError("shared queue requires the source's single-investigation triage flow")
    if (org_cfg.get("investigations_per_alert") != 1 or
            org_cfg.get("transfer_between_types") is not False):
        raise ValueError("shared organization requires exactly one investigation and no transfers")
    expected_severity = {"critical": 21937 / 156981, "high": 87545 / 156981,
                         "medium": 47499 / 156981}
    if (tuple(source.demand_profile["severity_order"]) != tuple(expected_severity) or
            any(abs(float(source.demand_profile["severity_mix"][k]) - v) > 1e-12
                for k, v in expected_severity.items()) or
            dict(source.settings.deadlines.offsets_by_severity_h) !=
            {"critical": 1.0, "high": 4.0, "medium": 12.0}):
        raise ValueError("shared reference must retain SOCTRA severity proportions and synthetic deadlines")
    juniors, seniors = tuple(org_cfg["junior_ids"]), tuple(org_cfg["senior_ids"])
    if not juniors or not seniors or set(juniors) & set(seniors):
        raise ValueError("shared organization must list distinct, nonempty junior and senior profiles")
    old_by_id = {r.analyst.analyst_id: r for r in source.organization.analysts}
    if set(juniors + seniors) != set(old_by_id):
        raise ValueError("shared role IDs must cover the source roster exactly")
    projects = tuple(source.demand_profile["class_mix"])
    demand = source.demand_profile
    params = source.generation["parameters"]
    alpha, beta, gamma = (float(params.get("alpha", 1.0)),
                          float(params.get("difficulty_service_beta", 0.0)),
                          float(params.get("gamma", 1.0)))
    if not (0 < alpha <= 1 and 0 <= beta < 2 and gamma >= 1):
        raise ValueError("source alpha/beta/gamma are outside the supported model range")
    configured_p = cfg["organization"].get("prevalence_by_class")
    if configured_p is None:
        configured_p = demand["prevalence_by_class"]
    if set(configured_p) != set(projects):
        raise ValueError("shared prevalence_by_class must cover every source project")
    p = {k: float(configured_p[k]) for k in projects}
    if any(not isfinite(value) or not 0 < value < 1 for value in p.values()):
        raise ValueError("shared need prevalence values must be in (0,1)")
    if max(p.values()) - min(p.values()) > 1e-12:
        raise ValueError("the current q-threshold complexity model requires one shared prevalence across projects")
    sens = {k: float(demand["sensitivity_by_class"][k]) for k in projects}
    fpr = {k: float(demand["false_positive_rate_by_class"][k]) for k in projects}
    source_means = demand.get("difficulty_mean_by_class_and_need", {})
    source_p = demand["prevalence_by_class"]
    means = {k: (tuple(float(v) for v in source_means[k])
                 if abs(p[k] - float(source_p[k])) < 1e-12 and k in source_means
                 else _beta22_conditional_means(p[k])) for k in projects}
    role_ids = {"junior": juniors, "senior": seniors}
    resources = []
    role_by_id = {}
    for role, ids in role_ids.items():
        for aid in ids:
            old = old_by_id[aid]
            project_eligible = projects if role == "senior" else tuple(
                k for k in projects if k in old.analyst.eligible_classes)
            if not project_eligible:
                raise ValueError(f"{role} profile {aid} has no eligible project")
            labels = tuple(task_class(k, t) for k in project_eligible
                           for t in ((ORDINARY,) if role == "junior" else RESEARCH_TYPES))
            competence, service, forecast = {}, {}, {}
            for project in project_eligible:
                base = float(old.service_by_class[project])
                skill = float(old.analyst.competence[project])
                routing = _routing_probabilities(p[project], sens[project], fpr[project])
                q_need, q_ordinary = means[project]
                type_specs = [(ORDINARY, ("TN", "FN")),
                              (SPECIALIZED, ("TP", "FP"))]
                for kind, cells in type_specs:
                    if kind == SPECIALIZED and role == "junior":
                        continue
                    key = task_class(project, kind)
                    conditional_q = _conditional_mean(routing, q_need, q_ordinary, cells)
                    route_mass = sum(routing[cell] for cell in cells)
                    # For this recommendation class, average the existing error
                    # work factors over its confusion cells; hidden labels remain
                    # unavailable to the assignment policy.
                    if kind == ORDINARY:
                        route_factor = ((routing["TN"] + routing["FN"] * gamma) / route_mass
                                        if route_mass else 1.0)
                    else:
                        route_factor = ((routing["TP"] + routing["FP"] * alpha) / route_mass
                                        if route_mass else 1.0)
                    competence[key] = skill
                    service[key] = base
                    forecast[key] = base * (1 + beta * (conditional_q - .5)) * route_factor
            calendar_overrides = cfg.get("calendar_by_analyst", {})
            calendar = _calendar(calendar_overrides.get(aid), old.calendar)
            analyst = Analyst(aid, frozenset(labels), competence)
            from studies.soc_triage_hls_availability_robustness.execution_api import AnalystResource
            resources.append(AnalystResource(analyst, service, calendar, forecast))
            role_by_id[aid] = role
    organization = SharedOrganization(tuple(resources), role_by_id,
                                      str(org_cfg.get("queue_name", "shared_alert_queue")))
    policies = tuple(cfg["policy"]["available"])
    if not policies or set(policies) - {"D1", "P1", "HLS-B"} or len(policies) != len(set(policies)):
        raise ValueError("available policies must be unique D1/P1/HLS-B names")
    default = cfg["policy"]["default"]
    if default not in policies:
        raise ValueError("default policy must be listed as available")
    hc = cfg["policy"]["hlsb"]
    hlsb = HLSBConfig(float(hc["window_h"]), float(hc["low"]),
                      float(hc["high"]), float(hc["capacity_per_h"]))
    return SharedQueueScenario(str(cfg["scenario_id"]), str(cfg["description"]),
                               source, organization, default, policies, hlsb,
                               MappingProxyType(p), path)


def build_shared_trace(rows: Sequence, organization: SharedOrganization) -> SharedTrace:
    """Map generated source alerts to exactly one recommended investigation type."""
    alerts, contexts = [], {}
    for row in rows:
        original = row.routed.alert
        project = str(original.task_class)
        recommendation = bool(row.routed.soctra_recommendation)
        kind = SPECIALIZED if recommendation else ORDINARY
        alert = Alert(original.alert_id, original.arrival,
                      task_class(project, kind), original.deadline)
        if not any(alert.task_class in r.analyst.eligible_classes
                   for r in organization.resources):
            raise ValueError(f"no eligible shared professional for {alert.task_class}")
        alerts.append(alert)
        contexts[alert.alert_id] = AlertContext(
            project, str(row.severity), float(row.difficulty),
            bool(row.true_escalation_need), recommendation, kind,
        )
    return SharedTrace(tuple(alerts), contexts)


def _q0_for_prevalence(prevalence: float) -> float:
    """Invert the source Beta(2,2) survival curve without changing its shape."""
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        survival = (1 - mid) ** 2 * (1 + 2 * mid)
        if survival > prevalence:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def generate_shared_trace(scenario: SharedQueueScenario, seed: int) -> SharedTrace:
    """Use the source trace generator and configurable global need prevalence.

    When the configured prevalence equals the source, its exact seeded trace is
    returned. For a different global prevalence, arrival/project/severity/q
    draws are kept and only need/classifier draws are regenerated at the same
    configured operating point.
    """
    source_p = scenario.source.demand_profile["prevalence_by_class"]
    if all(abs(scenario.prevalence_by_project[k] - float(source_p[k])) < 1e-12
           for k in scenario.prevalence_by_project):
        rows = scenario.source.generate_trace(seed)
    else:
        from dataclasses import replace as replace_dataclass
        from hls.ia_l1_l2_simulation import SimulatedAlert
        from hls.rq1_l1_l2 import RoutedAlert
        rows = scenario.source.generate_trace(seed)
        p = next(iter(scenario.prevalence_by_project.values()))
        shapes = tuple(float(x) for x in scenario.source.generation["parameters"].get(
            "difficulty_distribution_beta", (2.0, 2.0)))
        if shapes != (2.0, 2.0):
            raise ValueError("prevalence override requires the existing Beta(2,2) q distribution")
        q0 = _q0_for_prevalence(p)
        demand = scenario.source.demand_profile
        rng = random.Random(int(seed) ^ 0x51C07A)
        changed = []
        for row in rows:
            project = row.routed.alert.task_class
            need = row.difficulty >= q0
            sensitivity = float(demand["sensitivity_by_class"][project])
            fpr = float(demand["false_positive_rate_by_class"][project])
            recommended = rng.random() < (sensitivity if need else fpr)
            routed = RoutedAlert(row.routed.alert, need, recommended)
            changed.append(replace_dataclass(row, routed=routed, true_escalation_need=need))
        rows = tuple(changed)
    return build_shared_trace(rows, scenario.organization)


def _base_services(organization: SharedOrganization) -> tuple[dict, dict, dict]:
    all_classes = tuple(dict.fromkeys(k for r in organization.resources
                                      for k in r.analyst.eligible_classes))
    fallback = {key: next(r.service_by_class[key] for r in organization.resources
                          if key in r.service_by_class) for key in all_classes}
    actual = {r.analyst.analyst_id: dict(r.service_by_class) for r in organization.resources}
    forecast = {r.analyst.analyst_id: dict(r.forecast_service_by_class)
                for r in organization.resources}
    return fallback, actual, forecast


def _service_scales(trace: SharedTrace, scenario: SharedQueueScenario) -> dict[str, float]:
    params = scenario.source.generation["parameters"]
    alpha = float(params.get("alpha", 1.0))
    gamma = float(params.get("gamma", 1.0))
    beta = float(params.get("difficulty_service_beta", 0.0))
    result = {}
    for alert in trace.alerts:
        ctx = trace.context_by_alert[alert.alert_id]
        error = (alpha if ctx.recommended_l2 and not ctx.need_l2 else
                 gamma if not ctx.recommended_l2 and ctx.need_l2 else 1.0)
        result[alert.alert_id] = error * (1 + beta * (ctx.difficulty - .5))
    return result


def _scheduled_hours(calendar: Calendar, horizon: float) -> float:
    if horizon <= 0:
        return 0.0
    total = 0.0
    t = 0.0
    for _ in range(10000):
        if t >= horizon - 1e-10:
            break
        nxt = min(horizon, calendar.next_change(t))
        if nxt <= t + 1e-10:
            raise ValueError("calendar next_change did not advance")
        if calendar.available((t + nxt) / 2):
            total += nxt - t
        t = nxt
    else:
        raise ValueError("calendar availability integration exceeded its boundary guard")
    return total


def _weekly_availability_fraction(calendar: Calendar) -> float:
    return _scheduled_hours(calendar, 168.0) / 168.0


def _result_metrics(scenario: SharedQueueScenario, trace: SharedTrace,
                    policy: str, native, *, calendar_backend: bool) -> SharedExecutionResult:
    horizon = scenario.source.settings.evaluation_horizon
    admission = scenario.source.settings.admission_horizon
    factor = scenario.source.settings.time_scale.factor
    assignments = tuple(native.assignments)
    by_alert = {a.alert_id: a for a in assignments}
    if len(by_alert) != len(assignments):
        raise RuntimeError("native execution assigned an alert more than once")
    admitted = {a.alert_id: a for a in trace.alerts if a.arrival < admission}
    contexts = trace.context_by_alert
    role_work = {f"{role}_{kind}": 0.0 for role in ("junior", "senior")
                 for kind in RESEARCH_TYPES}
    analyst_work = {r.analyst.analyst_id: 0.0 for r in scenario.organization.resources}
    work_by_alert = {aid: 0.0 for aid in admitted}
    if calendar_backend:
        for aid, analyst_id, start, end in native.work_segments:
            start, end = start / factor, end / factor
            amount = max(0.0, min(horizon, end) - max(0.0, start))
            if aid in work_by_alert:
                work_by_alert[aid] += amount
                analyst_work[analyst_id] += amount
                ctx = contexts[aid]
                role_work[f"{scenario.organization.role(analyst_id)}_{ctx.research_type}"] += amount
    else:
        for assignment in assignments:
            start, completion = assignment.start / factor, assignment.completion / factor
            amount = max(0.0, min(horizon, completion) - start)
            if assignment.alert_id in work_by_alert:
                work_by_alert[assignment.alert_id] = amount
                analyst_work[assignment.analyst_id] += amount
                ctx = contexts[assignment.alert_id]
                role_work[f"{scenario.organization.role(assignment.analyst_id)}_{ctx.research_type}"] += amount
    utilization = {}
    by_id = {r.analyst.analyst_id: r for r in scenario.organization.resources}
    for aid, work in analyst_work.items():
        capacity = _scheduled_hours(by_id[aid].calendar or CONTINUOUS, horizon)
        utilization[aid] = work / capacity if capacity else 0.0
    role_util = {}
    for role in ("junior", "senior"):
        ids = [aid for aid, value in scenario.organization.role_by_analyst.items() if value == role]
        cap = sum(_scheduled_hours(by_id[aid].calendar or CONTINUOUS, horizon) for aid in ids)
        role_util[role] = sum(analyst_work[aid] for aid in ids) / cap if cap else 0.0

    # Offered work uses each alert's type-conditional mean service across its
    # eligible staff. It is not an assignment or a second resource capacity.
    offered = {kind: 0.0 for kind in RESEARCH_TYPES}
    for alert in admitted.values():
        eligible = [r for r in scenario.organization.resources
                    if alert.task_class in r.analyst.eligible_classes]
        offered[contexts[alert.alert_id].research_type] += sum(
            r.forecast_service_by_class[alert.task_class] for r in eligible) / len(eligible)

    starts = {aid: assignment.start / factor for aid, assignment in by_alert.items()}
    events = []
    for alert in admitted.values():
        events.append((alert.arrival, 1))
        if alert.alert_id in starts:
            events.append((starts[alert.alert_id], -1))
    queue = peak = 0
    for time in sorted({t for t, _ in events}):
        delta = sum(v for t, v in events if t == time)
        queue += delta
        peak = max(peak, queue)
    queue_at_cutoff = sum(a.arrival <= horizon and
                          (a.alert_id not in starts or starts[a.alert_id] > horizon)
                          for a in admitted.values())
    completed = {aid: a for aid, a in by_alert.items() if a.completion <= horizon}
    pending = len(admitted) - len(completed)
    wait, services, resolutions = [], [], []
    quality_sum = {kind: 0.0 for kind in RESEARCH_TYPES}
    quality_n = {kind: 0 for kind in RESEARCH_TYPES}
    closes = {kind: 0 for kind in RESEARCH_TYPES}
    sla_groups = []
    for severity in scenario.source.demand_profile["severity_order"]:
        for kind in RESEARCH_TYPES:
            subset = [a for a in admitted.values()
                      if contexts[a.alert_id].severity == severity and
                      contexts[a.alert_id].research_type == kind]
            on_time = late = still_pending = 0
            for alert in subset:
                assignment = by_alert.get(alert.alert_id)
                if assignment is None or assignment.completion / factor > horizon:
                    still_pending += 1
                    continue
                closes[kind] += 1
                resolutions.append(assignment.completion / factor - alert.arrival)
                wait.append(assignment.start / factor - alert.arrival)
                services.append(work_by_alert[alert.alert_id])
                if assignment.completion / factor <= alert.deadline:
                    on_time += 1
                else:
                    late += 1
                q = contexts[alert.alert_id].difficulty
                quality_sum[kind] += max(0.0, min(1.0, assignment.competence * (1 - .35 * q)))
                quality_n[kind] += 1
            sla_groups.append(SLAGroupMetric(severity, kind, len(subset), on_time, late, still_pending))
    counts = {kind: sum(ctx.research_type == kind for aid, ctx in contexts.items()
                        if aid in admitted) for kind in RESEARCH_TYPES}
    counts_closed = {kind: closes[kind] for kind in RESEARCH_TYPES}
    quality = {kind: (quality_sum[kind] / quality_n[kind] if quality_n[kind] else None)
               for kind in RESEARCH_TYPES}
    investigation_count = {aid: int(aid in by_alert) for aid in admitted}
    return SharedExecutionResult(
        policy, native, assignments, queue_at_cutoff, peak, pending,
        MappingProxyType(counts), MappingProxyType(counts_closed),
        MappingProxyType(offered), MappingProxyType(role_work),
        MappingProxyType(utilization), MappingProxyType(role_util),
        sum(wait) / len(wait) if wait else None,
        sum(services) / len(services) if services else None,
        sum(resolutions) / len(resolutions) if resolutions else None,
        tuple(sla_groups), MappingProxyType(quality),
        MappingProxyType(investigation_count),
    )


def run_shared_policy(scenario: SharedQueueScenario, trace: SharedTrace, *,
                      policy: str | None = None, calendar_backend: bool = False,
                      seed: int | None = None) -> SharedExecutionResult:
    policy = policy or scenario.policy_default
    if policy not in scenario.available_policies:
        raise ValueError(f"policy {policy!r} is not configured for this shared scenario")
    fallback, actual, forecast = _base_services(scenario.organization)
    scales = _service_scales(trace, scenario)
    resources = scenario.organization.resources
    analysts = tuple(r.analyst for r in resources)
    factor = scenario.source.settings.time_scale.factor
    alerts = tuple(Alert(a.alert_id, a.arrival * factor, a.task_class,
                         a.deadline * factor) for a in trace.alerts)
    actual_scaled = {aid: {k: v * factor for k, v in values.items()}
                     for aid, values in actual.items()}
    forecast_scaled = {aid: {k: v * factor for k, v in values.items()}
                       for aid, values in forecast.items()}
    scaled_scales = scales
    hlsb = HLSBConfig(scenario.hlsb.window_h * factor, scenario.hlsb.low,
                      scenario.hlsb.high, scenario.hlsb.capacity_per_h / factor)
    if calendar_backend:
        calendars = {r.analyst.analyst_id: (r.calendar or CONTINUOUS).scaled(factor)
                     for r in resources}
        native = simulate_calendar(
            alerts, analysts, forecast_scaled, calendars,
            horizon=scenario.source.settings.evaluation_horizon * factor,
            policy="WAPS" if policy == "HLS-B" else policy,
            seed=scenario.source.settings.seed if seed is None else seed,
            waps_config=hlsb if policy == "HLS-B" else None,
            actual_service=actual_scaled,
            realized_scale_by_alert=scaled_scales,
        )
        return _result_metrics(scenario, trace, policy, native, calendar_backend=True)
    native = simulate_continuous(
        alerts, analysts, {k: v * factor for k, v in fallback.items()},
        policy=policy, admission_horizon=scenario.source.settings.admission_horizon * factor,
        drain_period=(scenario.source.settings.evaluation_horizon -
                      scenario.source.settings.admission_horizon) * factor,
        random_seed=scenario.source.settings.seed if seed is None else seed,
        service_by_analyst_class=actual_scaled,
        forecast_service_by_analyst_class=forecast_scaled,
        realized_scale_by_alert=scaled_scales,
        hlsb_config=hlsb if policy == "HLS-B" else None,
    )
    return _result_metrics(scenario, trace, policy, native, calendar_backend=False)


@dataclass(frozen=True)
class SharedCapacityReport:
    maximum_arrivals_per_h: float
    class_mix_by_project_and_type: Mapping[str, float]
    offered_work_by_type_h_per_h: Mapping[str, float]
    utilization_by_analyst_at_capacity: Mapping[str, float]
    method: str = "single shared-resource fractional LP with per-analyst hours and type/project eligibility"


def assess_shared_capacity(scenario: SharedQueueScenario) -> SharedCapacityReport:
    """Run one capacity LP over all project×type classes and all analysts."""
    demand = scenario.source.demand_profile
    projects = tuple(demand["class_mix"])
    classes, shares, work = [], {}, {ORDINARY: 0.0, SPECIALIZED: 0.0}
    for project in projects:
        p = float(scenario.prevalence_by_project[project])
        se = float(demand["sensitivity_by_class"][project])
        fpr = float(demand["false_positive_rate_by_class"][project])
        routing = _routing_probabilities(p, se, fpr)
        q_need, q_ordinary = _beta22_conditional_means(p)
        for kind, cells in ((ORDINARY, ("TN", "FN")),
                            (SPECIALIZED, ("TP", "FP"))):
            key = task_class(project, kind)
            route = sum(routing[c] for c in cells)
            classes.append(key)
            shares[key] = float(demand["class_mix"][project]) * route
            work[kind] += shares[key]
    total = sum(shares.values())
    shares = {k: v / total for k, v in shares.items()}
    services = {r.analyst.analyst_id: dict(r.forecast_service_by_class)
                for r in scenario.organization.resources}
    result = effective_capacity(
        list(scenario.organization.analysts), services, shares, classes=tuple(classes),
        capacity_by_analyst={r.analyst.analyst_id:
                             _weekly_availability_fraction(r.calendar or CONTINUOUS)
                             for r in scenario.organization.resources},
    )
    return SharedCapacityReport(
        float(result["max_common_arrivals_per_h"]), MappingProxyType(shares),
        MappingProxyType(work),
        MappingProxyType(dict(result["fluid_utilization_at_capacity"])),
    )
