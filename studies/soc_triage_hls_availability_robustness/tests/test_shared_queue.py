from dataclasses import replace
from types import MappingProxyType

import pytest

from hls.rq1_allocation import HLSBConfig, simulate
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17,
)
from studies.soc_triage_hls_availability_robustness.shared_queue import (
    AlertContext,
    ORDINARY,
    SPECIALIZED,
    SharedOrganization,
    SharedTrace,
    _service_scales,
    assess_shared_capacity,
    build_shared_trace,
    generate_shared_trace,
    load_shared_scenario,
    run_shared_policy,
    task_class,
)


@pytest.fixture
def scenario():
    return load_shared_scenario()


def test_configuration_is_one_shared_pool_with_explicit_junior_senior_eligibility(scenario):
    org = scenario.organization
    assert org.queue_name == "shared_alert_queue"
    assert len(org.resources) == 8
    for resource in org.resources:
        kinds = {key.rsplit("::", 1)[1] for key in resource.analyst.eligible_classes}
        if org.role(resource.analyst.analyst_id) == "junior":
            assert kinds == {ORDINARY}
        else:
            assert kinds == {ORDINARY, SPECIALIZED}
    assert set(scenario.available_policies) == {"D1", "P1", "HLS-B"}


def test_need_prevalence_is_a_configurable_shared_scenario_parameter(scenario):
    scenario = replace(scenario, prevalence_by_project=MappingProxyType({
        project: .05 for project in scenario.prevalence_by_project
    }))
    trace = generate_shared_trace(scenario, 2026112801)
    need_rate = sum(x.need_l2 for x in trace.context_by_alert.values()) / len(trace.alerts)
    assert need_rate == pytest.approx(.05, abs=.02)
    assert all(context.need_l2 == (context.difficulty >= .86465)
               for context in trace.context_by_alert.values())


def test_trace_adapter_preserves_ids_arrivals_deadlines_and_triage_recommendations(scenario):
    source_rows = scenario.source.generate_trace(901)
    trace = build_shared_trace(source_rows, scenario.organization)
    source_by_id = {row.routed.alert.alert_id: row for row in source_rows}
    for alert in trace.alerts:
        source = source_by_id[alert.alert_id]
        context = trace.context_by_alert[alert.alert_id]
        assert alert.arrival == source.routed.alert.arrival
        assert alert.deadline == source.routed.alert.deadline
        assert context.project == source.routed.alert.task_class
        assert context.recommended_l2 == source.routed.soctra_recommendation
        assert (context.research_type == SPECIALIZED) == context.recommended_l2


@pytest.mark.parametrize("policy", ["D1", "P1", "HLS-B"])
def test_shared_backend_delegates_same_policy_over_one_roster_and_one_alert_queue(scenario, policy):
    trace = generate_shared_trace(scenario, 2026112801)
    assert {x.research_type for x in trace.context_by_alert.values()} == {ORDINARY, SPECIALIZED}
    result = run_shared_policy(scenario, trace, policy=policy)
    # One native result and one assignment stream: no L1 stage/transfer stage.
    assert result.policy == policy
    assert len(result.assignments) == len(trace.alerts)
    assert set(result.investigation_count_by_alert.values()) == {1}
    assert result.arrivals_by_type[ORDINARY] + result.arrivals_by_type[SPECIALIZED] == len(trace.alerts)
    analyst_by_id = {r.analyst.analyst_id: r for r in scenario.organization.resources}
    alert_by_id = {a.alert_id: a for a in trace.alerts}
    for assignment in result.assignments:
        alert = alert_by_id[assignment.alert_id]
        analyst = analyst_by_id[assignment.analyst_id].analyst
        assert alert.task_class in analyst.eligible_classes
        assert assignment.completion >= assignment.start
        assert assignment.alert_id in result.investigation_count_by_alert
    by_analyst = {}
    for assignment in result.assignments:
        by_analyst.setdefault(assignment.analyst_id, []).append(assignment)
    for rows in by_analyst.values():
        rows.sort(key=lambda x: x.start)
        assert all(a.completion <= b.start for a, b in zip(rows, rows[1:]))
    assert result.service_work_by_role_type_h["junior_specialized"] == 0
    assert result.service_work_by_role_type_h["senior_ordinary"] > 0
    assert result.service_work_by_role_type_h["senior_specialized"] > 0


@pytest.mark.parametrize("policy", ["D1", "P1", "HLS-B"])
def test_continuous_shared_adapter_matches_direct_frozen_engine_call(scenario, policy):
    trace = generate_shared_trace(scenario, 2026112801)
    actual = run_shared_policy(scenario, trace, policy=policy).native_result
    org = scenario.organization
    resources = org.resources
    classes = tuple(dict.fromkeys(k for r in resources for k in r.analyst.eligible_classes))
    fallback = {k: next(r.service_by_class[k] for r in resources if k in r.service_by_class)
                for k in classes}
    factor = scenario.source.settings.time_scale.factor
    actual_services = {r.analyst.analyst_id: {k: v * factor for k, v in r.service_by_class.items()}
                       for r in resources}
    forecast = {r.analyst.analyst_id: {k: v * factor for k, v in r.forecast_service_by_class.items()}
                for r in resources}
    expected = simulate(
        tuple(replace(a, arrival=a.arrival * factor, deadline=a.deadline * factor)
              for a in trace.alerts), tuple(r.analyst for r in resources),
        {k: v * factor for k, v in fallback.items()}, policy=policy,
        admission_horizon=scenario.source.settings.admission_horizon * factor,
        drain_period=(scenario.source.settings.evaluation_horizon -
                      scenario.source.settings.admission_horizon) * factor,
        random_seed=scenario.source.settings.seed,
        service_by_analyst_class=actual_services,
        forecast_service_by_analyst_class=forecast,
        realized_scale_by_alert=_service_scales(trace, scenario),
        hlsb_config=(HLSBConfig(scenario.hlsb.window_h * factor, scenario.hlsb.low,
                                scenario.hlsb.high, scenario.hlsb.capacity_per_h / factor)
                     if policy == "HLS-B" else None),
    )
    assert actual.assignments == expected.assignments
    assert actual.at_horizon == expected.at_horizon
    assert actual.after_drain == expected.after_drain


@pytest.mark.parametrize("policy", ["D1", "P1", "HLS-B"])
def test_calendar_backend_uses_each_senior_calendar_and_keeps_absolute_deadline(scenario, policy):
    resources = tuple(replace(r, calendar=(WEEKDAY_9_TO_17
                          if scenario.organization.role(r.analyst.analyst_id) == "senior"
                          else CONTINUOUS)) for r in scenario.organization.resources)
    org = SharedOrganization(resources, scenario.organization.role_by_analyst)
    scenario = replace(scenario, organization=org)
    cls = task_class("portfolio_top5", SPECIALIZED)
    from hls.rq1_allocation import Alert
    alert = Alert("special-1", 0.0, cls, 1.0)
    trace = SharedTrace((alert,), {"special-1": AlertContext(
        "portfolio_top5", "critical", .5, True, True, SPECIALIZED)})
    result = run_shared_policy(scenario, trace, policy=policy, calendar_backend=True)
    assert len(result.assignments) == 1
    assert result.assignments[0].start == pytest.approx(9.0)
    assert result.assignments[0].completion > alert.deadline
    critical_specialized = next(x for x in result.sla_by_severity_type
                                if x.severity == "critical" and x.research_type == SPECIALIZED)
    assert critical_specialized.completed_late == 1
    assert all(r.calendar == CONTINUOUS for r in org.resources
               if org.role(r.analyst.analyst_id) == "junior")


def test_capacity_lp_uses_one_combined_pool_and_shared_per_analyst_constraints(scenario):
    report = assess_shared_capacity(scenario)
    assert report.maximum_arrivals_per_h > 0
    assert sum(report.class_mix_by_project_and_type.values()) == pytest.approx(1)
    assert len(report.utilization_by_analyst_at_capacity) == len(scenario.organization.resources)
    assert all(0 <= value <= 1 + 1e-8
               for value in report.utilization_by_analyst_at_capacity.values())
    assert "single shared-resource" in report.method


def test_shared_capacity_lp_counts_calendar_availability_once(scenario):
    resources = tuple(replace(r, calendar=(WEEKDAY_9_TO_17
                          if scenario.organization.role(r.analyst.analyst_id) == "senior"
                          else CONTINUOUS)) for r in scenario.organization.resources)
    scenario = replace(scenario, organization=SharedOrganization(
        resources, scenario.organization.role_by_analyst))
    capacity = assess_shared_capacity(scenario)
    assert 0 < capacity.maximum_arrivals_per_h < assess_shared_capacity(
        load_shared_scenario()).maximum_arrivals_per_h
