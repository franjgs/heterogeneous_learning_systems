import json
import random
from pathlib import Path

import pytest

from hls.rq1_allocation import Alert
from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend, ContinuousBackend
from studies.soc_triage_hls_availability_robustness.scenario_loader import (
    ScenarioConfigError, load_scenario,
)


ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "config"


@pytest.mark.parametrize("name", [
    "HISTORICAL_REFERENCE.json", "SYNTHETIC_SOC_24x7.json",
    "SYNTHETIC_SOC_MIXED_SHIFTS.json",
])
def test_loads_examples_and_builds_immutable_explicit_resources(name):
    scenario = load_scenario(CONFIG / name)
    assert scenario.scenario_id
    assert scenario.classifier_point().p_detection > 0
    assert scenario.generation["prevalence_pi"] == pytest.approx(19 / 14449)
    assert scenario.organization.resources_for("L1")
    assert scenario.organization.resources_for("L2")
    with pytest.raises(TypeError):
        scenario.generation["new"] = "mutation"
    with pytest.raises(TypeError):
        scenario.organization.resources_for("L1")[0].service_by_class["x"] = 1


def test_mixed_calendars_keep_individual_and_overnight_windows():
    scenario = load_scenario(CONFIG / "SYNTHETIC_SOC_MIXED_SHIFTS.json")
    by_id = {r.analyst.analyst_id: r for r in scenario.organization.analysts}
    assert len(by_id["day-1"].calendar.windows) == 7
    assert len(by_id["expert-a"].calendar.windows) == 5
    assert by_id["expert-a"].calendar != by_id["expert-b"].calendar
    assert (6, 21.0, 5.0) in by_id["expert-c"].calendar.windows


def test_reference_organization_has_continuous_l1_roster_fixed_l2_8x5_and_cost_metadata():
    scenario = load_scenario(CONFIG / "SOC_REFERENCE_ORGANIZATION_V1.json")
    l1, l2 = scenario.organization.resources_for("L1"), scenario.organization.resources_for("L2")
    assert len(l1) == 5 and len(l2) == 3
    # The calendar API's week starts Monday 00:00. Check full coverage without
    # requiring any single individual to be continuously available.
    for slot in range(7 * 24):
        t = slot + .5
        assert sum(resource.calendar.available(t) for resource in l1) == 1
    assert [sum(end - start for _, start, end in r.calendar.windows) for r in l1] == [40, 32, 32, 32, 32]
    for resource in l2:
        assert len(resource.calendar.windows) == 5
        assert all((day, start, end) == (day, 9.0, 17.0)
                   for day, start, end in resource.calendar.windows)
        assert sum(end - start for _, start, end in resource.calendar.windows) == 40
    assert dict(scenario.settings.deadlines.offsets_by_severity_h) == {"high": 1, "medium": 4, "low": 12}
    assert scenario.cost_model["normalization"]["L2"] > scenario.cost_model["normalization"]["L1"]
    person_cost = scenario.cost_model["hourly_cost_units_by_analyst"]
    assert all(person_cost[r.analyst.analyst_id] == 1.0 for r in l1)
    assert all(person_cost[r.analyst.analyst_id] == 1.8 for r in l2)
    assert sum(sum(end - start for _, start, end in r.calendar.windows) for r in l1) == 168
    assert sum(sum(end - start for _, start, end in r.calendar.windows) for r in l2) == 120
    scheduled_cost = {level: sum(person_cost[r.analyst.analyst_id] *
                                 sum(end - start for _, start, end in r.calendar.windows)
                                 for r in scenario.organization.resources_for(level))
                      for level in ("L1", "L2")}
    assert scheduled_cost == {"L1": 168, "L2": 216}
    assert scenario.demand_profile["regimes"][1]["name"] == "overload_pulse"
    # Demand/cost remain metadata and do not alter historical compatibility data.
    assert scenario.generation["parameters"]["difficulty_service_beta"] == 0


def test_v2_json_generates_seeded_trace_and_builds_configured_single_investigation_flow():
    scenario = load_scenario(CONFIG / "SOC_REFERENCE_ORGANIZATION_V2.json")
    assert scenario.flow_mode == "triage_single_investigation"
    assert scenario.generation["prevalence_pi"] == pytest.approx(.1)
    first = scenario.generate_trace(998001)
    again = scenario.generate_trace(998001)
    assert first == again
    assert len(first) == 476
    triage, source_rows = scenario.triage_scenario_for(998001)
    assert source_rows == first
    assert triage.alpha == .5 and triage.difficulty_service_beta == 0 and triage.gamma == 1
    l2_factor = (.1 * .8421 + (1 - .1) * .045 * .5) / (.1 * .8421 + (1 - .1) * .045)
    for resource in scenario.organization.resources_for("L2"):
        for task_class, actual in resource.service_by_class.items():
            assert resource.forecast_service_by_class[task_class] == pytest.approx(actual * l2_factor)
    assert triage.recommendation_l2_by_alert == {
        row.routed.alert.alert_id: row.routed.soctra_recommendation for row in first
    }
    assert triage.reference_escalation_by_alert == {
        row.routed.alert.alert_id: row.true_escalation_need for row in first
    }


def test_historical_scenario_json_defaults_to_legacy_flow_selector():
    scenario = load_scenario(CONFIG / "HISTORICAL_REFERENCE.json")
    assert scenario.flow_mode == "historical_l1_then_l2"


def test_reference_organization_keeps_natural_deadline_when_route_is_l2():
    scenario = load_scenario(CONFIG / "SOC_REFERENCE_ORGANIZATION_V1.json")
    alert = Alert("saturday-night", 143.75, "portfolio_top5", 999.0)
    request = scenario.request_for("L2", (alert,), severity_by_alert={"saturday-night": "high"})
    assert request.alerts[0].arrival == 143.75
    assert request.alerts[0].deadline == 144.75
    assert request.alerts[0].deadline - request.alerts[0].arrival == 1.0


def test_reference_weekend_l2_route_is_calendar_infeasible_without_pausing_sla():
    from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import assess_deadline_feasibility

    scenario = load_scenario(CONFIG / "SOC_REFERENCE_ORGANIZATION_V1.json")
    alerts = (Alert("weekend-escalation", 143.75, "portfolio_top5", 999.0),)
    request = scenario.request_for("L1", alerts,
        severity_by_alert={"weekend-escalation": "high"})
    report = assess_deadline_feasibility(request,
        l2_required_by_alert={"weekend-escalation": True}, route_basis="scenario_route",
        severity_by_alert={"weekend-escalation": "high"})
    task = report.tasks[0]
    assert task.optimistic_intrinsically_infeasible is False
    assert task.calendar_infeasible is True
    assert task.calendar_earliest_completion > request.alerts[0].deadline
    assert request.alerts[0].deadline - request.alerts[0].arrival == 1.0


def test_reference_weekday_morning_l2_route_can_be_calendar_feasible():
    from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import assess_deadline_feasibility

    scenario = load_scenario(CONFIG / "SOC_REFERENCE_ORGANIZATION_V1.json")
    alert = Alert("weekday-escalation", 9.125, "portfolio_top5", 999.0)
    request = scenario.request_for("L1", (alert,), severity_by_alert={"weekday-escalation": "high"})
    report = assess_deadline_feasibility(request,
        l2_required_by_alert={"weekday-escalation": True}, route_basis="scenario_route",
        severity_by_alert={"weekday-escalation": "high"})
    task = report.tasks[0]
    assert task.optimistic_intrinsically_infeasible is False
    assert task.calendar_infeasible is False
    assert task.calendar_earliest_completion <= request.alerts[0].deadline


def test_historical_reference_resolves_published_point_and_historical_deadline_values():
    scenario = load_scenario(CONFIG / "HISTORICAL_REFERENCE.json")
    assert scenario.classifier_point().id == "standardized_lightgbm_apc_symmetric"
    assert scenario.generation["classifiers"]["standardized_lsensemble_apc_symmetric"].p_false_alarm == .0743
    assert dict(scenario.settings.deadlines.offsets_by_severity_h) == {"high": 1, "medium": 4, "low": 12}
    assert len(scenario.organization.resources_for("L1")) == 6
    assert len(scenario.organization.resources_for("L2")) == 3
    assert "soc_parametric_baseline.build_roster" in scenario.organization_reference


def test_requests_work_with_both_existing_backends_and_severity_deadlines_are_sidecar():
    scenario = load_scenario(CONFIG / "SYNTHETIC_SOC_24x7.json")
    alerts = (Alert("x", 1.0, "portfolio_top5", 100.0),)
    request = scenario.request_for("L2", alerts, severity_by_alert={"x": "high"})
    assert request.alerts[0].deadline == 13.0
    assert alerts[0].deadline == 100.0  # caller's generated trace is unchanged
    continuous = ContinuousBackend().run(request)
    calendar = CalendarBackend().run(request)
    assert continuous.native_result is not None
    assert calendar.native_result is not None


def test_severity_map_requires_sidecar_and_computes_absolute_deadlines():
    scenario = load_scenario(CONFIG / "SYNTHETIC_SOC_24x7.json")
    alerts = (Alert("a", 2.0, "portfolio_top5", 100.0),
              Alert("b", 4.0, "portfolio_top5", 100.0))
    with pytest.raises(ScenarioConfigError, match="severity_by_alert is required"):
        scenario.request_for("L2", alerts)
    request = scenario.request_for("L2", alerts,
                                   severity_by_alert={"a": "high", "b": "low"})
    assert [a.deadline for a in request.alerts] == [14.0, 76.0]


def test_severity_map_requires_exact_alert_ids_and_known_severities():
    scenario = load_scenario(CONFIG / "SYNTHETIC_SOC_24x7.json")
    alerts = (Alert("a", 2.0, "portfolio_top5", 100.0),
              Alert("b", 4.0, "portfolio_top5", 100.0))
    with pytest.raises(ScenarioConfigError, match="cover exactly"):
        scenario.request_for("L2", alerts, severity_by_alert={"a": "high"})
    with pytest.raises(ScenarioConfigError, match="unknown severities"):
        scenario.request_for("L2", alerts,
                             severity_by_alert={"a": "urgent", "b": "low"})


def _load_with_deadline_mode(tmp_path, mode, **deadline_fields):
    raw = json.loads((CONFIG / "SYNTHETIC_SOC_24x7.json").read_text())
    raw["deadlines"] = {"mode": mode, **deadline_fields}
    path = tmp_path / f"{mode}.json"
    path.write_text(json.dumps(raw))
    return load_scenario(path)


def test_provided_absolute_preserves_generated_deadlines(tmp_path):
    scenario = _load_with_deadline_mode(tmp_path, "provided_absolute")
    alerts = (Alert("a", 2.0, "portfolio_top5", 30.0),)
    request = scenario.request_for("L2", alerts)
    assert request.alerts == alerts


def test_explicit_by_alert_keeps_existing_absolute_deadline_behavior(tmp_path):
    scenario = _load_with_deadline_mode(
        tmp_path, "explicit_by_alert", absolute_by_alert={"a": 19.0}
    )
    alerts = (Alert("a", 2.0, "portfolio_top5", 30.0),
              Alert("b", 4.0, "portfolio_top5", 35.0))
    request = scenario.request_for("L2", alerts)
    assert [a.deadline for a in request.alerts] == [19.0, 35.0]


def test_loading_historical_reference_does_not_mutate_historical_configuration():
    historical_json = (ROOT.parent / "soc_triage_hls_q1_integration_evidence" /
                       "config" / "primary_campaign.json")
    before = historical_json.read_bytes()
    first = load_scenario(CONFIG / "HISTORICAL_REFERENCE.json")
    second = load_scenario(CONFIG / "HISTORICAL_REFERENCE.json")
    assert historical_json.read_bytes() == before
    assert first.organization == second.organization
    assert first.settings == second.settings


def test_scenarios_are_independent_and_loader_does_not_consume_randomness_or_change_campaign_globals():
    state = random.getstate()
    loaded_a = load_scenario(CONFIG / "SYNTHETIC_SOC_24x7.json")
    loaded_b = load_scenario(CONFIG / "SYNTHETIC_SOC_MIXED_SHIFTS.json")
    assert random.getstate() == state
    assert loaded_a is not loaded_b
    assert loaded_a.settings is not loaded_b.settings
    assert len(loaded_a.organization.resources_for("L1")) != len(loaded_b.organization.resources_for("L1"))


def test_invalid_configuration_reports_clear_error(tmp_path):
    raw = json.loads((CONFIG / "SYNTHETIC_SOC_24x7.json").read_text())
    raw["organization"]["analysts"][0]["service_h"]["portfolio_top5"] = 0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(raw))
    with pytest.raises((ScenarioConfigError, ValueError), match="positive|service"):
        load_scenario(path)


def test_unknown_generator_classifier_and_policy_references_are_rejected(tmp_path):
    original = json.loads((CONFIG / "SYNTHETIC_SOC_24x7.json").read_text())
    for section, value in [("generator", "unknown"), ("classifier", "unknown")]:
        raw = json.loads(json.dumps(original))
        if section == "generator":
            raw["generation"]["generator"]["reference"] = value
        else:
            raw["generation"]["classifier"]["default"] = value
        path = tmp_path / f"{section}.json"
        path.write_text(json.dumps(raw))
        with pytest.raises(ScenarioConfigError):
            load_scenario(path)

    raw = json.loads(json.dumps(original))
    raw["policies"]["L2"]["default"] = "P2"
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ScenarioConfigError, match="default"):
        load_scenario(path)
