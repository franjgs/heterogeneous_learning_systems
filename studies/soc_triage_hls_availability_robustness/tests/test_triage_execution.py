from dataclasses import replace

import pytest

from hls.rq1_allocation import Alert, Analyst, HLSBConfig
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17, Calendar,
)
from studies.soc_triage_hls_availability_robustness.execution_api import (
    AnalystResource, CalendarBackend, ContinuousBackend, DeadlineConfig,
    OrganizationConfig, PolicyConfig, SimulationSettings, TeamConfig, TimeScale,
)
from studies.soc_triage_hls_availability_robustness.triage_execution import (
    HISTORICAL_L1_THEN_L2, TRIAGE_SINGLE_INVESTIGATION, TriageScenario,
    run_triage_flow,
)


def make_scenario(alerts, need, rec, difficulty, *, alpha=.5, beta=0, gamma=1,
                  l1_calendar=CONTINUOUS, l2_calendar=CONTINUOUS,
                  l1_service=1, l2_service=2, cutoff=30, admission=20, seed=19,
                  policy="D1"):
    l1 = Analyst("L1-A", frozenset({"x"}), {"x": .6})
    l2 = Analyst("L2-A", frozenset({"x"}), {"x": .9})
    resources = (
        AnalystResource(l1, {"x": l1_service}, l1_calendar),
        AnalystResource(l2, {"x": l2_service}, l2_calendar),
    )
    organization = OrganizationConfig(resources, (
        TeamConfig("L1", ("L1-A",)), TeamConfig("L2", ("L2-A",)),
    ))
    policy_config = PolicyConfig(policy, HLSBConfig(4, 1.05, 1.2, .5)
                                  if policy == "WAPS" else None)
    return TriageScenario(
        tuple(alerts), organization,
        {"L1": policy_config, "L2": policy_config},
        SimulationSettings(admission, cutoff, seed, TimeScale(), DeadlineConfig({})),
        need, rec, difficulty, alpha, beta, gamma,
    )


def test_single_flow_routes_tp_fp_tn_fn_once_and_composes_alpha_beta_gamma():
    alerts = tuple(Alert(aid, 0, "x", 20) for aid in ("tp", "fp", "tn", "fn"))
    scenario = make_scenario(
        alerts,
        {"tp": True, "fp": False, "tn": False, "fn": True},
        {"tp": True, "fp": True, "tn": False, "fn": False},
        {"tp": .9, "fp": .75, "tn": .1, "fn": .6},
        beta=1, gamma=2,
    )
    result = run_triage_flow(scenario, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                             backend=ContinuousBackend())
    outcomes = {x.alert_id: x for x in result.outcomes}
    assert {x: outcomes[x].confusion for x in outcomes} == {
        "tp": "TP", "fp": "FP", "tn": "TN", "fn": "FN",
    }
    assert {x: outcomes[x].final_investigation_level for x in outcomes} == {
        "tp": "L2", "fp": "L2", "tn": "L1", "fn": "L1",
    }
    assert all(x.investigation_count == 1 for x in outcomes.values())
    assert set(result.stage_results["L1"].tasks_by_alert) == {"tn", "fn"}
    assert set(result.stage_results["L2"].tasks_by_alert) == {"tp", "fp"}
    durations = {a.alert_id: a.completion - a.start
                 for stage in result.stage_results.values() for a in stage.assignments}
    assert durations == {
        "tp": pytest.approx(2.8),       # 2 * [1 + (.9-.5)]
        "fp": pytest.approx(1.25),      # 2 * alpha * [1 + (.75-.5)]
        "tn": pytest.approx(.6),        # 1 * [1 + (.1-.5)]
        "fn": pytest.approx(2.2),       # 1 * gamma * [1 + (.6-.5)]
    }


def test_gamma_one_is_neutral_and_gamma_does_not_change_route():
    alert = (Alert("fn", 0, "x", 10),)
    base = make_scenario(alert, {"fn": True}, {"fn": False}, {"fn": .7}, gamma=1)
    raised = replace(base, gamma=1.8)
    one = run_triage_flow(base, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                          backend=ContinuousBackend())
    two = run_triage_flow(raised, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                          backend=ContinuousBackend())
    assert one.outcomes[0].route_level == two.outcomes[0].route_level == "L1"
    assert one.outcomes[0].investigation_count == two.outcomes[0].investigation_count == 1
    assert one.stage_results["L1"].assignments[0].completion == pytest.approx(1.0)
    assert two.stage_results["L1"].assignments[0].completion == pytest.approx(1.8)


@pytest.mark.parametrize("backend_kind", ["continuous", "calendar"])
@pytest.mark.parametrize("policy", ["D1", "P1", "WAPS"])
def test_environment_labels_and_realized_scale_do_not_reach_dispatcher(
        monkeypatch, backend_kind, policy):
    from hls import rq1_allocation
    from studies.soc_triage_hls_availability_robustness import availability_engine

    alerts = (Alert("fp", 0, "x", 10), Alert("fn", 0, "x", 10))
    scenario = make_scenario(alerts, {"fp": False, "fn": True},
                             {"fp": True, "fn": False}, {"fp": .8, "fn": .2},
                             beta=1, gamma=2, policy=policy)
    seen = []
    def spy_for(original):
        def spy(free, pending, now, service_time, *args, **kwargs):
            seen.extend(pending.values())
            for alert in pending.values():
                assert set(vars(alert)) == {"alert_id", "arrival", "task_class", "deadline"}
            return original(free, pending, now, service_time, *args, **kwargs)
        return spy

    # The selected backend uses only its native policy callbacks; wrapping all
    # callbacks keeps the test independent of whether WAPS selects D1 or P1.
    monkeypatch.setattr(rq1_allocation, "_dispatch_d1", spy_for(rq1_allocation._dispatch_d1))
    monkeypatch.setattr(rq1_allocation, "_dispatch_local_priority",
                        spy_for(rq1_allocation._dispatch_local_priority))
    monkeypatch.setattr(availability_engine, "_dispatch_d1",
                        spy_for(availability_engine._dispatch_d1))
    monkeypatch.setattr(availability_engine, "_dispatch_local_priority",
                        spy_for(availability_engine._dispatch_local_priority))
    backend = ContinuousBackend() if backend_kind == "continuous" else CalendarBackend()
    run_triage_flow(scenario, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                    backend=backend)
    assert seen
    assert {a.alert_id for a in seen} == {"fp", "fn"}


def test_sla_outcomes_include_late_and_pending_without_censoring_work():
    alerts = (Alert("on-time", 0, "x", 2), Alert("late", 0, "x", .5),
              Alert("pending", 0, "x", 3))
    scenario = make_scenario(alerts, {x.alert_id: False for x in alerts},
                             {x.alert_id: False for x in alerts},
                             {x.alert_id: .5 for x in alerts}, l1_service=1,
                             cutoff=2, admission=1)
    result = run_triage_flow(scenario, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                             backend=ContinuousBackend())
    # The tight-deadline task finishes late; another task remains pending at
    # the cutoff. Neither is counted as an on-time finalization.
    by_id = {x.alert_id: x for x in result.outcomes}
    assert by_id["on-time"].status == "completed_within_sla"
    assert by_id["late"].status == "completed_late"
    assert by_id["pending"].status == "pending"
    assert by_id["late"].deadline == .5
    assert result.status_counts == {"completed_within_sla": 1,
                                    "completed_late": 1, "pending": 1}


def test_calendar_l1_coverage_and_l2_weekday_delay_preserve_natural_deadline():
    alert = (Alert("weekend", 120, "x", 121),)
    scenario = make_scenario(alert, {"weekend": True}, {"weekend": True},
                             {"weekend": .5}, l1_calendar=CONTINUOUS,
                             l2_calendar=WEEKDAY_9_TO_17, cutoff=180, admission=168)
    result = run_triage_flow(scenario, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                             backend=CalendarBackend())
    outcome = result.outcomes[0]
    assert outcome.final_investigation_level == "L2"
    assert outcome.deadline == 121
    assert outcome.status == "completed_late"
    l2 = result.stage_results["L2"].tasks_by_alert["weekend"]
    assert l2.start == 177
    assert l2.completion == 179


def test_rotating_l1_individual_shifts_cover_sunday_night():
    from studies.soc_triage_hls_availability_robustness.availability_engine import Calendar

    windows = {f"L1-{i}": [] for i in range(5)}
    for slot in range(21):
        day, shift = divmod(slot, 3)
        windows[f"L1-{slot % 5}"].append((day, shift * 8, (shift + 1) * 8))
    l1_resources = tuple(
        AnalystResource(Analyst(aid, frozenset({"x"}), {"x": .6}),
                        {"x": .2}, Calendar(tuple(rows)))
        for aid, rows in windows.items()
    )
    l2_resource = AnalystResource(
        Analyst("L2-A", frozenset({"x"}), {"x": .9}), {"x": .2}, WEEKDAY_9_TO_17)
    org = OrganizationConfig(l1_resources + (l2_resource,), (
        TeamConfig("L1", tuple(windows)), TeamConfig("L2", ("L2-A",)),
    ))
    for hour in range(168):
        assert any(r.calendar.available(hour + .5) for r in l1_resources)
    assert sum(len(v) for v in windows.values()) == 21
    assert all(32 <= 8 * len(v) <= 40 for v in windows.values())
    alert = (Alert("sunday-night", 145, "x", 146),)
    scenario = TriageScenario(
        alert, org, {"L1": PolicyConfig("D1"), "L2": PolicyConfig("D1")},
        SimulationSettings(168, 180, 5, TimeScale(), DeadlineConfig({})),
        {"sunday-night": False}, {"sunday-night": False}, {"sunday-night": .5}, 1.0,
    )
    result = run_triage_flow(scenario, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                             backend=CalendarBackend())
    outcome = result.outcomes[0]
    assert outcome.final_investigation_level == "L1"
    assert outcome.analyst_id == "L1-3"
    assert outcome.completion == pytest.approx(145.2)
    assert outcome.status == "completed_within_sla"


def test_legacy_flow_can_mix_continuous_l1_and_calendar_l2_backends():
    alert = (Alert("weekend", 120, "x", 121),)
    scenario = make_scenario(alert, {"weekend": True}, {"weekend": True},
                             {"weekend": .5}, l1_service=.1, l2_service=2,
                             l2_calendar=WEEKDAY_9_TO_17, cutoff=180, admission=168)
    result = run_triage_flow(
        scenario, flow_mode=HISTORICAL_L1_THEN_L2,
        backend={"L1": ContinuousBackend(), "L2": CalendarBackend()},
    )
    assert result.stage_results["L1"].assignments[0].completion == pytest.approx(120.1)
    assert result.stage_results["L2"].tasks_by_alert["weekend"].start == 177
    assert result.stage_results["L2"].tasks_by_alert["weekend"].completion == 179
    assert result.outcomes[0].status == "completed_late"


def test_calendar_suspension_retains_work_and_sla_clock():
    two_shifts = Calendar(((0, 9, 10), (1, 9, 10)))
    alert = (Alert("long-fn", 9, "x", 10),)
    scenario = make_scenario(alert, {"long-fn": True}, {"long-fn": False},
                             {"long-fn": .5}, gamma=1.5,
                             l1_calendar=two_shifts, l1_service=1,
                             cutoff=40, admission=20)
    result = run_triage_flow(scenario, flow_mode=TRIAGE_SINGLE_INVESTIGATION,
                             backend=CalendarBackend())
    task = result.stage_results["L1"].tasks_by_alert["long-fn"]
    assert task.effective_work == pytest.approx(1.5)
    assert task.suspension == pytest.approx(23)
    assert task.completion == pytest.approx(33.5)
    assert result.outcomes[0].deadline == 10
    assert result.outcomes[0].status == "completed_late"


def test_historical_flow_keeps_l1_then_l2_order_and_original_deadline():
    alerts = (Alert("a-positive", 0, "x", .5), Alert("b-negative", 0, "x", 10))
    scenario = make_scenario(alerts, {"a-positive": True, "b-negative": False},
                             {"a-positive": True, "b-negative": False},
                             {"a-positive": .5, "b-negative": .5},
                             l1_service=1, l2_service=2, cutoff=10, admission=5)
    result = run_triage_flow(scenario, flow_mode=HISTORICAL_L1_THEN_L2,
                             backend=ContinuousBackend())
    l1 = {a.alert_id: a for a in result.stage_results["L1"].assignments}
    l2 = {a.alert_id: a for a in result.stage_results["L2"].assignments}
    assert l1["a-positive"].completion == 1
    assert "b-negative" not in l2
    assert l2["a-positive"].start == 1
    assert l2["a-positive"].completion == 3
    out = {x.alert_id: x for x in result.outcomes}
    assert out["a-positive"].deadline == .5
    assert out["a-positive"].status == "completed_late"
    assert out["a-positive"].investigation_count == 2


def test_triage_orchestrator_adds_no_random_stream_to_historical_backends(monkeypatch):
    from hls import rq1_allocation

    alerts = (Alert("a-positive", 0, "x", .5), Alert("b-negative", 0, "x", 10))
    scenario = make_scenario(alerts, {"a-positive": True, "b-negative": False},
                             {"a-positive": True, "b-negative": False},
                             {"a-positive": .5, "b-negative": .5},
                             l1_service=1, l2_service=2, cutoff=10, admission=5)
    original = rq1_allocation.random.Random
    created = []

    def tracked(seed=None):
        created.append(seed)
        return original(seed)

    monkeypatch.setattr(rq1_allocation.random, "Random", tracked)
    run_triage_flow(scenario, flow_mode=HISTORICAL_L1_THEN_L2,
                    backend=ContinuousBackend())
    # The two existing stage engines each initialize their seeded RNG once;
    # the orchestrator itself draws none.
    assert created == [scenario.settings.seed, scenario.settings.seed]


def test_flow_mode_must_be_explicit_and_validated():
    scenario = make_scenario((), {}, {}, {})
    with pytest.raises(ValueError, match="flow_mode"):
        run_triage_flow(scenario, flow_mode="automatic", backend=ContinuousBackend())
