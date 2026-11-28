"""JSON scenario loader and adapter to the existing seeded HLS generator.

Legacy scenarios still provide Alert records to ``request_for``. V2 can call
``generate_trace`` and ``triage_scenario_for`` for one configured execution.
No campaign module is imported or mutated.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from math import isfinite, isclose
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from hls.rq1_allocation import Alert, Analyst, HLSBConfig
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    Calendar, CONTINUOUS, TimeScale,
)
from studies.soc_triage_hls_availability_robustness.execution_api import (
    AnalystResource, DeadlineConfig, EnvironmentRealization, OrganizationConfig,
    PolicyConfig, SimulationRequest, SimulationSettings, TeamConfig,
)
from studies.soc_triage_hls_availability_robustness.triage_execution import (
    FLOW_MODES, HISTORICAL_L1_THEN_L2, TriageScenario,
)


class ScenarioConfigError(ValueError):
    """Invalid or unresolved external scenario configuration."""


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class ClassifierOperatingPoint:
    id: str
    algorithm: str
    features: str
    p_detection: float
    p_false_alarm: float
    balanced_accuracy: float


@dataclass(frozen=True)
class LoadedScenario:
    scenario_id: str
    description: str
    generation: Mapping
    organization: OrganizationConfig
    policies: Mapping
    settings: SimulationSettings
    seed_count: int
    seed_start: int
    experiment: Mapping
    organization_reference: str | None = None
    demand_profile: Mapping | None = None
    cost_model: Mapping | None = None
    flow_mode: str = HISTORICAL_L1_THEN_L2

    def classifier_point(self, classifier_id: str | None = None) -> ClassifierOperatingPoint:
        selected = classifier_id or self.generation["classifier_default"]
        try:
            return self.generation["classifiers"][selected]
        except KeyError as exc:
            raise ScenarioConfigError(f"unknown configured classifier {selected!r}") from exc

    def generate_trace(self, seed: int):
        """Generate a seeded trace through the existing HLS alert generator."""
        if self.generation["generator_reference"] != "ia_l1_l2_simulation.generate_alerts":
            raise ScenarioConfigError("this scenario references a historical generator; no generic trace adapter is available")
        from hls.ia_l1_l2_simulation import ScenarioConfig, generate_alerts

        demand = self.demand_profile
        if demand is None:
            raise ScenarioConfigError("the configured generator requires demand_profile")
        regimes = tuple(demand["regimes"])
        horizon = self.settings.admission_horizon
        if not regimes or regimes[0]["start_h"] != 0 or regimes[-1]["end_h"] != horizon:
            raise ScenarioConfigError("demand regimes must cover [0, admission_horizon]")
        if any(a["end_h"] != b["start_h"] for a, b in zip(regimes, regimes[1:])):
            raise ScenarioConfigError("demand regimes must be contiguous for this generator")
        classes = tuple(demand["class_mix"])
        class_mix = tuple(float(demand["class_mix"][k]) for k in classes)
        if not classes or any(not isfinite(x) or x < 0 for x in class_mix) or not isclose(sum(class_mix), 1.0, abs_tol=1e-9):
            raise ScenarioConfigError("demand_profile.class_mix must be nonnegative and sum to one")
        for name in ("prevalence_by_class", "sensitivity_by_class", "false_positive_rate_by_class"):
            values = demand.get(name, {})
            if set(values) != set(classes) or any(not isfinite(float(v)) or not 0 <= float(v) <= 1 for v in values.values()):
                raise ScenarioConfigError(f"demand_profile.{name} must cover classes with probabilities in [0,1]")
        severity_mix = demand.get("severity_mix", {})
        severity_order = tuple(demand.get("severity_order", ("low", "medium", "high")))
        if len(severity_order) != 3 or len(set(severity_order)) != 3 or set(severity_mix) != set(severity_order) or any(
                not isfinite(float(v)) or float(v) < 0 for v in severity_mix.values()) or not isclose(
                sum(float(v) for v in severity_mix.values()), 1.0, abs_tol=1e-9):
            raise ScenarioConfigError("demand_profile.severity_mix must define its three severity_order categories and sum to one")
        point = self.classifier_point()
        if any(not isclose(float(demand["sensitivity_by_class"][k]), point.p_detection, abs_tol=1e-12) or
               not isclose(float(demand["false_positive_rate_by_class"][k]), point.p_false_alarm, abs_tol=1e-12)
               for k in classes):
            raise ScenarioConfigError("demand classifier rates must match the selected classifier operating point")
        rate_maps = [dict(r["arrival_rate_by_class"]) for r in regimes]
        totals = [sum(row.values()) for row in rate_maps]
        if any(set(row) != set(classes) or any(not isfinite(float(x)) or float(x) < 0 for x in row.values())
               for row in rate_maps) or any(not isfinite(total) or total <= 0 for total in totals):
            raise ScenarioConfigError("configured generator requires positive arrival rates in each regime")
        for row, total in zip(rate_maps, totals):
            if set(row) != set(classes) or any(abs(row[k] / total - demand["class_mix"][k]) > 1e-9 for k in classes):
                raise ScenarioConfigError("existing generator requires a fixed class mix across demand regimes")

        burst = shift_after = rate_after = None
        if len(regimes) == 2:
            shift_after, rate_after = regimes[1]["start_h"], totals[1]
        elif len(regimes) == 3:
            if totals[1] < totals[0]:
                raise ScenarioConfigError("the middle regime must be a pulse at least as intense as baseline")
            burst = (regimes[1]["start_h"], regimes[1]["end_h"], totals[1] / totals[0])
            shift_after, rate_after = regimes[2]["start_h"], totals[2]
        elif len(regimes) != 1:
            raise ScenarioConfigError("existing generator supports one regime, one rate shift, or one pulse plus recovery")

        params = self.generation["parameters"]
        need = tuple(float(demand["prevalence_by_class"][k]) for k in classes)
        difficulty_shapes = tuple(float(x) for x in params.get("difficulty_distribution_beta", (2.0, 2.0)))
        q0 = params.get("reference_escalation_difficulty_threshold")
        if q0 is not None:
            q0 = float(q0)
            if difficulty_shapes != (2.0, 2.0):
                raise ScenarioConfigError("difficulty-threshold routing currently requires the configured Beta(2,2) difficulty distribution")
            implied_prevalence = (1.0 - q0) ** 2 * (1.0 + 2.0 * q0)
            if any(not isclose(value, implied_prevalence, rel_tol=1e-10, abs_tol=1e-12)
                   for value in need):
                raise ScenarioConfigError("prevalence_by_class must equal the Beta(2,2) upper-tail probability implied by q0")
        deadlines = self.settings.deadlines.offsets_by_severity_h
        if set(deadlines) != set(severity_order):
            raise ScenarioConfigError("severity_order categories must match deadlines.offsets_by_severity_h")
        return generate_alerts(ScenarioConfig(
            horizon=horizon, arrival_rate=totals[0], classes=classes,
            class_probabilities=class_mix,
            severity_probabilities=tuple(float(demand["severity_mix"][k]) for k in severity_order),
            severity_categories=severity_order,
            escalation_probability_by_class=need,
            deadline_by_severity=tuple((k, float(deadlines[k])) for k in severity_order),
            burst_window=burst, arrival_rate_shift_after=shift_after,
            arrival_rate_after=rate_after,
            ai_sensitivity=point.p_detection, ai_false_positive_rate=point.p_false_alarm,
            difficulty_beta=difficulty_shapes,
            reference_escalation_difficulty_threshold=q0,
        ), int(seed))

    def triage_scenario_for(self, seed: int, *, policy: str | Mapping[str, str] | None = None):
        """Build the triage orchestration input and return it with its source trace."""
        if self.flow_mode not in FLOW_MODES:
            raise ScenarioConfigError(f"unsupported flow_mode {self.flow_mode!r}")
        rows = self.generate_trace(seed)
        params = self.generation["parameters"]
        for key in ("alpha", "beta", "gamma"):
            config_key = "difficulty_service_beta" if key == "beta" else key
            if key in (self.demand_profile or {}) and not isclose(
                    float(params.get(config_key, 1.0 if key in {"alpha", "gamma"} else 0.0)),
                    float(self.demand_profile[key]), abs_tol=1e-12):
                raise ScenarioConfigError(f"generation.parameters and demand_profile disagree on {key}")
        policies = {}
        if isinstance(policy, Mapping) and set(policy) - {"L1", "L2"}:
            raise ScenarioConfigError("policy mapping may contain only L1 and/or L2")
        for level in ("L1", "L2"):
            spec = self.policies[level]
            name = policy.get(level, spec["default"]) if isinstance(policy, Mapping) else (policy or spec["default"])
            if name not in spec["available"]:
                raise ScenarioConfigError(f"policy {name!r} is not available for {level}")
            policies[level] = PolicyConfig(name, spec["waps"] if name == "WAPS" else None)
        inputs = TriageScenario(
            alerts=tuple(row.routed.alert for row in rows), organization=self.organization,
            policies=policies,
            settings=SimulationSettings(self.settings.admission_horizon,
                self.settings.evaluation_horizon, int(seed), self.settings.time_scale,
                self.settings.deadlines),
            reference_escalation_by_alert={row.routed.alert.alert_id: bool(row.true_escalation_need) for row in rows},
            recommendation_l2_by_alert={row.routed.alert.alert_id: bool(row.routed.soctra_recommendation) for row in rows},
            difficulty_by_alert={row.routed.alert.alert_id: float(row.difficulty) for row in rows},
            alpha=float(params.get("alpha", 1.0)),
            difficulty_service_beta=float(params.get("difficulty_service_beta", 0.0)),
            gamma=float(params.get("gamma", 1.0)),
        )
        return inputs, rows

    def request_for(self, level: str, alerts, *, seed: int | None = None,
                    policy: str | None = None, environment: EnvironmentRealization | None = None,
                    severity_by_alert: Mapping[str, str] | None = None) -> SimulationRequest:
        """Build an existing SimulationRequest from generated Alert records.

        In ``severity_map`` mode, severity labels are supplied as a separate
        sidecar keyed by alert ID; Alert itself is not extended. Otherwise its
        absolute deadline is preserved as generated.
        """
        level = level.upper()
        if level not in self.policies:
            raise ScenarioConfigError(f"no policies configured for level {level!r}")
        policy_name = policy or self.policies[level]["default"]
        if policy_name not in self.policies[level]["available"]:
            raise ScenarioConfigError(f"policy {policy_name!r} is not available for {level}")
        waps = self.policies[level].get("waps") if policy_name == "WAPS" else None
        rows = tuple(alerts)
        deadline_spec = self.generation["deadline_mode"]
        if deadline_spec["mode"] == "severity_map":
            if severity_by_alert is None:
                raise ScenarioConfigError(
                    "severity_by_alert is required when deadlines.mode is 'severity_map'"
                )
            offsets = deadline_spec["offsets_by_severity_h"]
            if set(severity_by_alert) != {a.alert_id for a in rows}:
                raise ScenarioConfigError("severity_by_alert must cover exactly the supplied alerts")
            unknown = set(severity_by_alert.values()) - set(offsets)
            if unknown:
                raise ScenarioConfigError(f"unknown severities in severity_by_alert: {sorted(unknown)}")
            rows = tuple(Alert(a.alert_id, a.arrival, a.task_class,
                               a.arrival + offsets[severity_by_alert[a.alert_id]]) for a in rows)
        elif deadline_spec["mode"] == "explicit_by_alert":
            explicit = deadline_spec["absolute_by_alert"]
            rows = tuple(Alert(a.alert_id, a.arrival, a.task_class, explicit[a.alert_id])
                         if a.alert_id in explicit else a for a in rows)
        return SimulationRequest(
            rows, self.organization, level, PolicyConfig(policy_name, waps),
            SimulationSettings(self.settings.admission_horizon,
                               self.settings.evaluation_horizon,
                               self.seed_start if seed is None else seed,
                               self.settings.time_scale, self.settings.deadlines),
            environment,
        )


_DAYS = {"mon": 0, "monday": 0, "tue": 1, "tuesday": 1, "wed": 2,
         "wednesday": 2, "thu": 3, "thursday": 3, "fri": 4, "friday": 4,
         "sat": 5, "saturday": 5, "sun": 6, "sunday": 6}


def _object(value, label):
    if not isinstance(value, dict):
        raise ScenarioConfigError(f"{label} must be a JSON object")
    return value


def _positive(value, label, *, zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ScenarioConfigError(f"{label} must be a finite number")
    if value < 0 if zero else value <= 0:
        raise ScenarioConfigError(f"{label} must be {'nonnegative' if zero else 'positive'}")
    return float(value)


def _historical_campaign():
    return Path(__file__).resolve().parents[1] / "soc_triage_hls_q1_integration_evidence" / "config" / "primary_campaign.json"


def _resolve_classifier_refs(generation):
    classifier = _object(generation.get("classifier"), "generation.classifier")
    ref = classifier.get("reference")
    if ref != "q1_primary_campaign.classifiers":
        raise ScenarioConfigError(f"unsupported classifier reference {ref!r}")
    try:
        historic = json.loads(_historical_campaign().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioConfigError(f"cannot read historical operating points: {exc}") from exc
    points = {p["id"]: ClassifierOperatingPoint(p["id"], p["algorithm"], p["features"],
               float(p["pD"]), float(p["pFA"]), float(p["BA"])) for p in historic["classifiers"]}
    options = classifier.get("options", [])
    if not options or len(options) != len(set(options)) or set(options) - set(points):
        raise ScenarioConfigError("classifier.options must contain unique known historical IDs")
    default = classifier.get("default")
    if default not in options:
        raise ScenarioConfigError("generation.classifier.default must be one of options")
    return MappingProxyType({"classifier_default": default,
                             "classifiers": MappingProxyType({key: points[key] for key in options})})


def _calendar(spec, label):
    spec = _object(spec, label)
    kind = spec.get("kind")
    if kind == "continuous":
        if set(spec) - {"kind"}:
            raise ScenarioConfigError(f"{label}: continuous calendar takes no other fields")
        return CONTINUOUS
    if kind != "weekly":
        raise ScenarioConfigError(f"{label}.kind must be continuous or weekly")
    windows = spec.get("windows")
    if not isinstance(windows, list) or not windows:
        raise ScenarioConfigError(f"{label}.windows must be a nonempty list")
    parsed = []
    for i, item in enumerate(windows):
        item = _object(item, f"{label}.windows[{i}]")
        day = item.get("day")
        day = _DAYS.get(day.lower()) if isinstance(day, str) else day
        start, end = item.get("start_h"), item.get("end_h")
        if isinstance(day, bool) or not isinstance(day, int) or day not in range(7):
            raise ScenarioConfigError(f"{label}.windows[{i}].day must be Mon..Sun or integer 0..6")
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x) for x in (start, end)):
            raise ScenarioConfigError(f"{label}.windows[{i}] start_h/end_h must be finite numbers")
        parsed.append((day, float(start), float(end)))
    try:
        return Calendar(tuple(parsed), float(spec.get("hours_per_day", 24)))
    except (TypeError, ValueError) as exc:
        raise ScenarioConfigError(f"{label}: {exc}") from exc


def load_scenario(path: str | Path) -> LoadedScenario:
    """Read, validate and resolve one JSON scenario without random draws."""
    path = Path(path)
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioConfigError(f"cannot load scenario {path}: {exc}") from exc
    config = _object(config, "root")
    if config.get("schema_version") != 1:
        raise ScenarioConfigError("schema_version must equal 1")
    scenario_id = config.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise ScenarioConfigError("scenario_id must be a nonempty string")
    description = str(config.get("description", ""))
    flow_mode = config.get("flow_mode", HISTORICAL_L1_THEN_L2)
    if flow_mode not in FLOW_MODES:
        raise ScenarioConfigError(f"flow_mode must be one of {sorted(FLOW_MODES)}")

    demand_profile = config.get("demand_profile")
    if demand_profile is not None:
        demand_profile = _freeze(_object(demand_profile, "demand_profile"))
    cost_model = config.get("cost_model")
    if cost_model is not None:
        cost_model = _freeze(_object(cost_model, "cost_model"))

    gen = _object(config.get("generation"), "generation")
    generator = _object(gen.get("generator"), "generation.generator").get("reference")
    if generator not in {"run_primary_campaign._primary_trace",
                         "ia_l1_l2_simulation.generate_alerts"}:
        raise ScenarioConfigError(f"unsupported generator reference {generator!r}")
    resolved = dict(_resolve_classifier_refs(gen))
    prevalence = _object(gen.get("prevalence"), "generation.prevalence")
    if prevalence.get("reference") not in {"q1_primary_campaign.prevalence.pi",
                                             "demand_profile.prevalence_by_class"}:
        raise ScenarioConfigError("unsupported generation.prevalence reference")
    historic = json.loads(_historical_campaign().read_text(encoding="utf-8"))
    resolved.update({"generator_reference": generator, "classifier_reference": "q1_primary_campaign.classifiers",
                     "prevalence_reference": prevalence["reference"],
                     "prevalence_pi": float(historic["prevalence"]["pi"]),
                     "need_reference": str(gen.get("need_reference", "synthetic_hidden_need")),
                     "deadline_mode": _object(config.get("deadlines"), "deadlines")})
    if prevalence["reference"] == "demand_profile.prevalence_by_class":
        if demand_profile is None:
            raise ScenarioConfigError("synthetic prevalence reference requires demand_profile")
        mix, by_class = demand_profile.get("class_mix", {}), demand_profile.get("prevalence_by_class", {})
        if set(mix) != set(by_class):
            raise ScenarioConfigError("class_mix and prevalence_by_class must have identical classes")
        resolved["prevalence_pi"] = sum(float(mix[k]) * float(by_class[k]) for k in mix)
    params = _object(gen.get("parameters", {}), "generation.parameters")
    resolved["parameters"] = _freeze(params)

    organization_cfg = _object(config.get("organization"), "organization")
    analyst_specs = organization_cfg.get("analysts")
    teams_cfg = _object(organization_cfg.get("teams"), "organization.teams")
    service_model = _object(organization_cfg.get("service_model", {}), "organization.service_model")
    base_service = service_model.get("base_service_h")
    demand_classes = (set(demand_profile.get("class_mix", {})) if demand_profile is not None else set())
    if not isinstance(analyst_specs, list) or not analyst_specs:
        raise ScenarioConfigError("organization.analysts must be a nonempty list")
    resources, levels = [], {}
    for i, spec in enumerate(analyst_specs):
        spec = _object(spec, f"organization.analysts[{i}]")
        aid, level = spec.get("id"), spec.get("level")
        if not isinstance(aid, str) or not aid.strip() or level not in {"L1", "L2"}:
            raise ScenarioConfigError(f"analyst {i} needs a nonempty id and level L1/L2")
        eligible = spec.get("eligible_classes")
        configured_competence = _object(spec.get("competence"), f"analyst {aid}.competence")
        if not isinstance(eligible, list) or not eligible or len(eligible) != len(set(eligible)):
            raise ScenarioConfigError(f"analyst {aid}.eligible_classes must be a nonempty unique list")
        eligible = set(eligible)
        if configured_competence and any(value is None for value in configured_competence.values()):
            universe = demand_classes or set(configured_competence)
            if set(configured_competence) != universe:
                raise ScenarioConfigError(f"analyst {aid}: competence with null values must cover the full task-class universe")
            declared_eligible = {key for key, value in configured_competence.items() if value is not None}
            if declared_eligible != eligible:
                raise ScenarioConfigError(f"analyst {aid}: non-null competence keys must equal eligible_classes")
        elif set(configured_competence) != eligible:
            raise ScenarioConfigError(f"analyst {aid}: competence keys must equal eligible_classes")
        competence = {key: configured_competence[key] for key in eligible}

        configured_service = spec.get("service_h")
        duration_factors = spec.get("duration_factor_by_class")
        if base_service is not None and duration_factors is not None:
            level_base = _object(base_service.get(level), f"organization.service_model.base_service_h.{level}")
            duration_factors = _object(duration_factors, f"analyst {aid}.duration_factor_by_class")
            if set(level_base) != (demand_classes or set(level_base)) or set(duration_factors) != eligible:
                raise ScenarioConfigError(f"analyst {aid}: base service must cover task classes and duration factors must cover eligibility")
            service = {key: _positive(level_base[key], f"analyst {aid}.base_service_h.{key}") *
                       _positive(duration_factors[key], f"analyst {aid}.duration_factor_by_class.{key}")
                       for key in eligible}
            if configured_service is not None:
                stated = _object(configured_service, f"analyst {aid}.service_h")
                if set(stated) != eligible or any(not isclose(float(stated[key]), service[key], rel_tol=1e-12, abs_tol=1e-12)
                                                  for key in eligible):
                    raise ScenarioConfigError(f"analyst {aid}.service_h must equal base_service_h[level,class] times duration_factor_by_class")
        else:
            if configured_service is None:
                raise ScenarioConfigError(f"analyst {aid} requires service_h or base service plus duration factors")
            service = _object(configured_service, f"analyst {aid}.service_h")
            if set(service) != eligible:
                raise ScenarioConfigError(f"analyst {aid}: service keys must equal eligibility")
        analyst = Analyst(aid, frozenset(eligible), competence)
        calendar = _calendar(spec.get("calendar"), f"analyst {aid}.calendar")
        forecast = spec.get("forecast_service_h", service)
        resources.append(AnalystResource(analyst, service, calendar, forecast))
        levels.setdefault(level, []).append(aid)
    if set(teams_cfg) != set(levels):
        raise ScenarioConfigError("organization.teams must define exactly the levels used by analysts")
    teams = []
    for level, ids in levels.items():
        configured = teams_cfg[level]
        if not isinstance(configured, list) or configured != ids:
            raise ScenarioConfigError(f"organization.teams.{level} must list its analysts in declaration order: {ids}")
        teams.append(TeamConfig(level, tuple(configured)))
    organization = OrganizationConfig(tuple(resources), tuple(teams))

    if demand_classes:
        for level in ("L1", "L2"):
            covered = set().union(*(set(resource.analyst.eligible_classes)
                                    for resource in organization.resources_for(level)))
            missing = demand_classes - covered
            if missing:
                raise ScenarioConfigError(f"team {level} has no eligible analyst for task classes: {sorted(missing)}")
        qualification_contract = _object(organization_cfg.get("qualification_contract", {}),
                                         "organization.qualification_contract")
        if qualification_contract.get("l2_all_classes_eligible", False):
            if any(set(resource.analyst.eligible_classes) != demand_classes
                   for resource in organization.resources_for("L2")):
                raise ScenarioConfigError("qualification contract requires every L2 analyst to be eligible for every configured class")

    policy_cfg = _object(config.get("policies"), "policies")
    policies = {}
    for level in levels:
        item = _object(policy_cfg.get(level), f"policies.{level}")
        available, default = item.get("available"), item.get("default")
        if not isinstance(available, list) or not available or len(available) != len(set(available)) or set(available) - {"D1", "P1", "WAPS"}:
            raise ScenarioConfigError(f"policies.{level}.available must contain unique D1/P1/WAPS values")
        if default not in available:
            raise ScenarioConfigError(f"policies.{level}.default must be listed in available")
        waps = None
        if "WAPS" in available:
            w = _object(item.get("waps"), f"policies.{level}.waps")
            try:
                waps = HLSBConfig(float(w["window_h"]), float(w["low"]), float(w["high"]), float(w["capacity_per_h"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise ScenarioConfigError(f"invalid policies.{level}.waps: {exc}") from exc
        policies[level] = MappingProxyType({"default": default, "available": tuple(available), "waps": waps})

    time_cfg = _object(config.get("time"), "time")
    experiment = _object(config.get("experiment"), "experiment")
    seed_start, seed_count = experiment.get("seed_start"), experiment.get("seed_count")
    if isinstance(seed_start, bool) or not isinstance(seed_start, int):
        raise ScenarioConfigError("experiment.seed_start must be an integer")
    if isinstance(seed_count, bool) or not isinstance(seed_count, int) or seed_count <= 0:
        raise ScenarioConfigError("experiment.seed_count must be a positive integer")
    deadline_cfg = resolved["deadline_mode"]
    mode = deadline_cfg.get("mode")
    if mode not in {"severity_map", "provided_absolute", "explicit_by_alert"}:
        raise ScenarioConfigError("deadlines.mode must be severity_map, provided_absolute or explicit_by_alert")
    offsets = deadline_cfg.get("offsets_by_severity_h", {})
    if mode == "severity_map":
        if not isinstance(offsets, dict) or not offsets:
            raise ScenarioConfigError("severity_map requires offsets_by_severity_h")
        offsets = {str(k): _positive(v, f"deadlines.{k}", zero=True) for k, v in offsets.items()}
    absolute_by_alert = deadline_cfg.get("absolute_by_alert", {})
    if mode == "explicit_by_alert":
        if not isinstance(absolute_by_alert, dict) or any(
                not isinstance(aid, str) or not aid for aid in absolute_by_alert):
            raise ScenarioConfigError("explicit_by_alert requires an object keyed by nonempty alert IDs")
        absolute_by_alert = {aid: _positive(value, f"deadlines.absolute_by_alert.{aid}", zero=True)
                             for aid, value in absolute_by_alert.items()}
    deadlines = DeadlineConfig(offsets)
    try:
        settings = SimulationSettings(_positive(time_cfg["admission_horizon"], "time.admission_horizon"),
            _positive(time_cfg["evaluation_horizon"], "time.evaluation_horizon"),
            seed_start,
            TimeScale(_positive(time_cfg.get("scale", 1), "time.scale")), deadlines)
    except (KeyError, TypeError, ValueError) as exc:
        raise ScenarioConfigError(f"invalid time/settings: {exc}") from exc
    resolved["deadline_mode"] = _freeze({"mode": mode, "offsets_by_severity_h": offsets,
        "absolute_by_alert": absolute_by_alert})
    return LoadedScenario(scenario_id, description, _freeze(resolved), organization,
        MappingProxyType(policies), settings, seed_count, seed_start, _freeze(experiment),
        organization_cfg.get("resource_reference"), demand_profile, cost_model, flow_mode)
