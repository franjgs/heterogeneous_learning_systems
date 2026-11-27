import pytest

from hls.rq1_allocation import Alert, Analyst
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17, TimeScale,
)
from studies.soc_triage_hls_availability_robustness.execution_api import (
    AnalystResource, DeadlineConfig, EnvironmentRealization, OrganizationConfig,
    PolicyConfig, SimulationRequest, SimulationSettings, TeamConfig,
)
from studies.soc_triage_hls_availability_robustness.scenario_diagnostics import (
    CapacityDemandProfile, DemandRegime, QueueObservation, assess_capacity,
    assess_deadline_feasibility, assess_queue_recovery, classify_regime_pressure,
    realized_demand_regime,
)


def request(alerts, l1, l2, *, horizon=200):
    resources = tuple(l1 + l2)
    org = OrganizationConfig(
        resources,
        (TeamConfig("L1", tuple(x.analyst.analyst_id for x in l1)),
         TeamConfig("L2", tuple(x.analyst.analyst_id for x in l2))),
    )
    return SimulationRequest(
        tuple(alerts), org, "L1", PolicyConfig("D1"),
        SimulationSettings(horizon, horizon + 24, 3, TimeScale(), DeadlineConfig()),
    )


def resource(aid, level, classes, service, calendar=CONTINUOUS):
    return AnalystResource(Analyst(aid, frozenset(classes), {k: .8 for k in classes}),
                           service, calendar)


def profile(regimes, *, alpha=1, beta=0, pi=None, pd=None, pfa=None, qmeans=None):
    classes = {k for regime in regimes for k in regime.arrival_rate_by_class}
    pi = pi or {k: 1.0 for k in classes}
    pd = pd or {k: 1.0 for k in pi}
    pfa = pfa or {k: 0.0 for k in pi}
    return CapacityDemandProfile(tuple(regimes), pi, pd, pfa, alpha, beta, qmeans)


def test_deadline_lower_bound_uses_only_eligible_resources_and_route_stages():
    l1 = [resource("l1-fast", "L1", ["x"], {"x": 1.0}),
          resource("l1-slow", "L1", ["x"], {"x": 2.0}),
          resource("wrong-class", "L1", ["y"], {"y": .01})]
    l2 = [resource("l2-specialist", "L2", ["x"], {"x": 2.0})]
    alerts = (Alert("one-stage", 0, "x", 1.5), Alert("two-stage", 2, "x", 4.5))
    req = request(alerts, l1, l2)
    report = assess_deadline_feasibility(
        req, l2_required_by_alert={"one-stage": False, "two-stage": True},
        route_basis="simulated_route", severity_by_alert={"one-stage": "high", "two-stage": "low"},
    )
    one, two = report.tasks
    assert (one.optimistic_min_service_h, one.optimistic_slack_h) == (1.0, .5)
    assert one.optimistic_l1_analyst_id == "l1-fast"
    assert not one.optimistic_intrinsically_infeasible
    assert (two.optimistic_min_service_h, two.optimistic_slack_h) == (3.0, -.5)
    assert two.route == "L1+L2" and two.optimistic_intrinsically_infeasible
    assert report.infeasible_count == 1
    assert report.calendar_infeasible_count == 1
    assert any(g.by == "route" and g.key == "L1+L2" and g.infeasible_count == 1 for g in report.groups)
    assert req.alerts == alerts  # original absolute deadlines are untouched

    without_schedules = assess_deadline_feasibility(
        req, l2_required_by_alert={"one-stage": False, "two-stage": True},
        route_basis="simulated_route", include_calendars=False,
    )
    assert without_schedules.calendar_infeasible_count is None


def test_beta_and_alpha_change_effective_stage_work_without_moving_deadline():
    l1 = [resource("l1", "L1", ["x"], {"x": 1.0})]
    l2 = [resource("l2", "L2", ["x"], {"x": 2.0})]
    alert = Alert("fp", 0, "x", 2.0)
    req = request((alert,), l1, l2)
    env = EnvironmentRealization({"fp": .25}, {"fp": False}, {"fp": .9}, 1.0)
    report = assess_deadline_feasibility(
        req, l2_required_by_alert={"fp": True}, route_basis="simulated_route", environment=env,
    )
    row = report.tasks[0]
    assert row.optimistic_min_service_h == pytest.approx(1.4 + 2.0 * 1.4 * .25)
    assert row.optimistic_slack_h == pytest.approx(2.0 - 2.1)
    assert row.calendar_infeasible is True
    assert req.alerts[0].deadline == 2.0


def test_calendar_bound_honors_weekday_turns_while_optimistic_bound_does_not():
    l1 = [resource("l1", "L1", ["x"], {"x": 1.0}, WEEKDAY_9_TO_17)]
    l2 = [resource("l2", "L2", ["x"], {"x": 1.0}, WEEKDAY_9_TO_17)]
    alert = Alert("friday", 112, "x", 115)  # Fri 16:00; deadline Saturday 03:00
    req = request((alert,), l1, l2, horizon=150)
    result = assess_deadline_feasibility(
        req, l2_required_by_alert={"friday": True}, route_basis="scenario_route",
    ).tasks[0]
    assert result.optimistic_min_service_h == 2.0
    assert result.optimistic_slack_h == 1.0
    assert result.calendar_earliest_completion == 178.0  # Monday 10:00, following week
    assert result.calendar_slack_h == -63.0
    assert result.calendar_infeasible


def test_capacity_lp_reports_load_calendar_fraction_and_specialization_bottleneck():
    l1 = [resource("x-specialist", "L1", ["x"], {"x": 1.0}),
          resource("y-specialist", "L1", ["y"], {"y": 1.0})]
    l2 = [resource("x-l2", "L2", ["x"], {"x": 1.0}),
          resource("y-l2", "L2", ["y"], {"y": 1.0})]
    org = request((), l1, l2).organization
    regimes = (DemandRegime("steady", 0, 10, {"x": .1, "y": .1}),
               DemandRegime("pulse", 10, 15, {"x": 1, "y": 3}),
               DemandRegime("recovery", 15, 25, {"x": .1, "y": .1}))
    report = assess_capacity(org, profile(regimes))
    rows = {(x.regime, x.level): x for x in report.regimes}
    assert rows["steady", "L1"].relative_load == pytest.approx(.1)
    assert rows["pulse", "L1"].load_status == "structural_overload"
    assert rows["recovery", "L1"].load_status == "capacity_sufficient_mean"
    assert rows["pulse", "L1"].analyst_utilization_at_capacity

    restricted = request((), [l1[0]], [l2[0]]).organization
    failed = assess_capacity(restricted, profile((DemandRegime("mixed", 0, 1, {"x": .5, "y": .5}),)))
    assert next(x for x in failed.regimes if x.level == "L1").unstaffed_classes == ("y",)
    assert next(x for x in failed.regimes if x.level == "L1").load_status == "infeasible_eligibility"


def test_expected_l2_load_includes_classifier_alpha_and_conditional_beta():
    l1 = [resource("l1", "L1", ["x"], {"x": 1.0})]
    l2 = [resource("l2", "L2", ["x"], {"x": 1.0})]
    org = request((), l1, l2).organization
    regime = DemandRegime("steady", 0, 1, {"x": 1.0})
    base = profile((regime,), alpha=.25, beta=0, pi={"x": .2}, pd={"x": .5}, pfa={"x": .1})
    correlated = profile((regime,), alpha=.25, beta=1, pi={"x": .2}, pd={"x": .5}, pfa={"x": .1},
                         qmeans={"x": (.9, .6)})
    report0 = assess_capacity(org, base)
    report1 = assess_capacity(org, correlated)
    l2_0 = next(x for x in report0.regimes if x.level == "L2")
    l2_1 = next(x for x in report1.regimes if x.level == "L2")
    assert l2_0.offered_rate_per_h == pytest.approx(.18)
    assert l2_0.offered_l2_work_h_per_h == pytest.approx(.12)
    assert l2_1.offered_l2_work_h_per_h == pytest.approx(.162)
    full_alpha = assess_capacity(org, profile((regime,), alpha=1, pi={"x": .2}, pd={"x": .5}, pfa={"x": .1}))
    assert next(x for x in full_alpha.regimes if x.level == "L2").offered_l2_work_h_per_h == pytest.approx(.18)


def test_realized_profile_preserves_class_need_route_and_difficulty_correlations():
    alerts = (Alert("tp", 1, "x", 9), Alert("fp", 2, "x", 10))
    regime = realized_demand_regime(
        "trace", 0, 4, alerts,
        l2_route_by_alert={"tp": True, "fp": True},
        true_need_by_alert={"tp": True, "fp": False},
        difficulty_by_alert={"tp": .9, "fp": .6}, alpha=.25, beta=1,
    )
    assert regime.arrival_rate_by_class == {"x": .5}
    assert regime.realized_l2_rate_by_class == {"x": .5}
    assert regime.realized_l1_service_factor_by_class == {"x": 1.25}
    assert regime.realized_l2_service_factor_by_class["x"] == pytest.approx((1.4 + .25 * 1.1) / 2)
    org = request((), [resource("l1", "L1", ["x"], {"x": 1.0})],
                  [resource("l2", "L2", ["x"], {"x": 1.0})]).organization
    realized_capacity = assess_capacity(org, CapacityDemandProfile((regime,), alpha=.25, beta=1))
    row = next(x for x in realized_capacity.regimes if x.level == "L2")
    assert row.demand_basis == "realized_trace"
    assert row.offered_rate_per_h == pytest.approx(.5)
    assert row.offered_l2_work_h_per_h == pytest.approx(.5 * (1.4 + .275) / 2)


def test_calendar_capacity_is_available_time_fraction_and_recovery_is_configurable():
    l1 = [resource("l1", "L1", ["x"], {"x": 1.0}, WEEKDAY_9_TO_17)]
    l2 = [resource("l2", "L2", ["x"], {"x": 1.0}, WEEKDAY_9_TO_17)]
    org = request((), l1, l2).organization
    result = assess_capacity(org, profile((DemandRegime("steady", 0, 24, {"x": .1}),)))
    l1_capacity = next(x for x in result.regimes if x.level == "L1")
    assert l1_capacity.capacity_per_h == pytest.approx(40 / 168)
    assert classify_regime_pressure(l1_capacity, (QueueObservation(4, 2, 0, 1.0, 0.0),)) == "temporal_congestion_with_mean_capacity"
    observations = (QueueObservation(10, 4, 1, 3.0, 1.0),
                    QueueObservation(11, 0, 0, 0.0, 0.0),
                    QueueObservation(12, 0, 0, 0.0, 0.0))
    recovered = assess_queue_recovery(observations, after_h=10, sustain_h=1)
    assert recovered.status == "recovered" and recovered.recovery_time_h == 11
    not_yet = assess_queue_recovery(observations[:2], after_h=10, sustain_h=1)
    assert not_yet.status == "not_observed_recovered"


def test_diagnostics_do_not_change_dispatch_or_request():
    l1 = [resource("l1", "L1", ["x"], {"x": 1.0})]
    l2 = [resource("l2", "L2", ["x"], {"x": 1.0})]
    req = request((Alert("a", 0, "x", 3),), l1, l2, horizon=5)
    from studies.soc_triage_hls_availability_robustness.execution_api import ContinuousBackend
    before = ContinuousBackend().run(req)
    assess_deadline_feasibility(req, l2_required_by_alert={"a": False}, route_basis="scenario_route")
    assess_capacity(req.organization, profile((DemandRegime("one", 0, 5, {"x": .2}),)))
    after = ContinuousBackend().run(req)
    assert before.native_result == after.native_result
    assert req.alerts == (Alert("a", 0, "x", 3),)
