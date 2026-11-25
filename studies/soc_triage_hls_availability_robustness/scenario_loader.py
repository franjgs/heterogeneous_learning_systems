"""Optional JSON scenario loader for SOCTRA-HLS execution_api objects.

The loader resolves metadata and immutable resources only. Alert generation stays
with the referenced historical generator; callers pass its Alert records to
``LoadedScenario.request_for``. No campaign module is imported or mutated.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from math import isfinite
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

    def classifier_point(self, classifier_id: str | None = None) -> ClassifierOperatingPoint:
        selected = classifier_id or self.generation["classifier_default"]
        try:
            return self.generation["classifiers"][selected]
        except KeyError as exc:
            raise ScenarioConfigError(f"unknown configured classifier {selected!r}") from exc

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
        if deadline_spec["mode"] == "severity_map" and severity_by_alert is not None:
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

    gen = _object(config.get("generation"), "generation")
    generator = _object(gen.get("generator"), "generation.generator").get("reference")
    if generator != "run_primary_campaign._primary_trace":
        raise ScenarioConfigError(f"unsupported generator reference {generator!r}")
    resolved = dict(_resolve_classifier_refs(gen))
    prevalence = _object(gen.get("prevalence"), "generation.prevalence")
    if prevalence.get("reference") != "q1_primary_campaign.prevalence.pi":
        raise ScenarioConfigError("generation.prevalence must reference the historical Q1 prevalence")
    historic = json.loads(_historical_campaign().read_text(encoding="utf-8"))
    resolved.update({"generator_reference": generator, "classifier_reference": "q1_primary_campaign.classifiers",
                     "prevalence_reference": prevalence["reference"],
                     "prevalence_pi": float(historic["prevalence"]["pi"]),
                     "need_reference": str(gen.get("need_reference", "synthetic_hidden_need")),
                     "deadline_mode": _object(config.get("deadlines"), "deadlines")})
    params = _object(gen.get("parameters", {}), "generation.parameters")
    resolved["parameters"] = _freeze(params)

    organization_cfg = _object(config.get("organization"), "organization")
    analyst_specs = organization_cfg.get("analysts")
    teams_cfg = _object(organization_cfg.get("teams"), "organization.teams")
    if not isinstance(analyst_specs, list) or not analyst_specs:
        raise ScenarioConfigError("organization.analysts must be a nonempty list")
    resources, levels = [], {}
    for i, spec in enumerate(analyst_specs):
        spec = _object(spec, f"organization.analysts[{i}]")
        aid, level = spec.get("id"), spec.get("level")
        if not isinstance(aid, str) or not aid.strip() or level not in {"L1", "L2"}:
            raise ScenarioConfigError(f"analyst {i} needs a nonempty id and level L1/L2")
        eligible = spec.get("eligible_classes")
        competence = _object(spec.get("competence"), f"analyst {aid}.competence")
        service = _object(spec.get("service_h"), f"analyst {aid}.service_h")
        if not isinstance(eligible, list) or not eligible or len(eligible) != len(set(eligible)):
            raise ScenarioConfigError(f"analyst {aid}.eligible_classes must be a nonempty unique list")
        if set(service) != set(eligible) or not set(eligible).issubset(competence):
            raise ScenarioConfigError(f"analyst {aid}: service keys and competence must cover eligibility")
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
        organization_cfg.get("resource_reference"))
