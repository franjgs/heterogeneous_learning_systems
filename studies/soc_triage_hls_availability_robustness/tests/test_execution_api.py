import pytest

from hls.rq1_allocation import Alert, Analyst, HLSBConfig, simulate as simulate_original
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17, Calendar, TimeScale, simulate as simulate_calendar_original,
)
from studies.soc_triage_hls_availability_robustness.execution_api import (
    AnalystResource, CalendarBackend, ContinuousBackend, DeadlineConfig,
    EnvironmentRealization, OrganizationConfig, PolicyConfig, SimulationRequest,
    SimulationSettings, TeamConfig,
)


def build_request(*, policy="D1", calendar=CONTINUOUS, admission=24, evaluation=40,
                  scale=1.0, service=3.0, environment=None, analysts=None, level="L2"):
    analysts = analysts or [Analyst("L2-A", frozenset({"x"}), {"x": .8})]
    resources = tuple(AnalystResource(a, {"x": service}, calendar) for a in analysts)
    org = OrganizationConfig(resources, (TeamConfig(level, tuple(a.analyst_id for a in analysts)),))
    waps = HLSBConfig(4, 1.05, 1.2, .4) if policy == "WAPS" else None
    return SimulationRequest(
        (Alert("a", 16, "x", 32), Alert("b", 18, "x", 42)), org, level,
        PolicyConfig(policy, waps),
        SimulationSettings(admission, evaluation, 17, TimeScale(scale),
                           DeadlineConfig({"high": 12, "medium": 24, "low": 72})),
        environment,
    )


def test_config_is_deeply_immutable_and_supports_arbitrary_team_sizes():
    competence = {"x": 0.0}
    actual = {"x": 2.0}
    analyst = Analyst("a", frozenset({"x"}), competence)
    resource = AnalystResource(analyst, actual, CONTINUOUS)
    competence["x"] = .9
    actual["x"] = 99
    assert resource.analyst.competence["x"] == 0.0
    assert resource.service_by_class["x"] == 2.0
    with pytest.raises(TypeError):
        resource.service_by_class["x"] = 4
    analysts = [Analyst(f"L1-{i}", frozenset({"x"}), {"x": .5}) for i in range(3)]
    analysts += [Analyst(f"L2-{i}", frozenset({"x"}), {"x": .7}) for i in range(2)]
    resources = tuple(AnalystResource(a, {"x": 1.0}, CONTINUOUS) for a in analysts)
    org = OrganizationConfig(resources, (TeamConfig("L1", tuple(a.analyst_id for a in analysts[:3])),
                                         TeamConfig("L2", tuple(a.analyst_id for a in analysts[3:]))))
    assert len(org.resources_for("L1")) == 3
    assert len(org.resources_for("L2")) == 2


@pytest.mark.parametrize("factory", [
    lambda: AnalystResource(Analyst("a", frozenset({"x"}), {}), {"x": 1.0}),
    lambda: AnalystResource(Analyst("a", frozenset({"x"}), {"x": .5}), {"y": 1.0}),
    lambda: AnalystResource(Analyst("a", frozenset({"x"}), {"x": .5}), {"x": 0.0}),
    lambda: AnalystResource(Analyst("a", frozenset({"x"}), {"x": 1.1}), {"x": 1.0}),
    lambda: TeamConfig("L3", ("a",)),
    lambda: PolicyConfig("new-policy"),
    lambda: DeadlineConfig({"high": -1}),
])
def test_invalid_resource_and_policy_configurations_are_rejected(factory):
    with pytest.raises(ValueError):
        factory()


def test_organization_rejects_duplicate_ids_and_incoherent_membership():
    a = AnalystResource(Analyst("a", frozenset({"x"}), {"x": .5}), {"x": 1})
    with pytest.raises(ValueError, match="globally unique"):
        OrganizationConfig((a, a), (TeamConfig("L1", ("a",)),))
    with pytest.raises(ValueError, match="unknown analysts"):
        OrganizationConfig((a,), (TeamConfig("L1", ("missing",)),))
    with pytest.raises(ValueError, match="multiple teams"):
        OrganizationConfig((a,), (TeamConfig("L1", ("a",)), TeamConfig("L2", ("a",))))


def test_request_rejects_horizon_deadline_policy_scale_and_unstaffed_class():
    request = build_request()
    with pytest.raises(ValueError, match="later than"):
        SimulationSettings(10, 10, 1, TimeScale(), DeadlineConfig({}))
    with pytest.raises(ValueError, match="finite and positive"):
        SimulationSettings(10, 20, 1, TimeScale(float("inf")), DeadlineConfig({}))
    with pytest.raises(ValueError, match="recognized|D1|P1|WAPS"):
        PolicyConfig("UNKNOWN")
    wrong = (Alert("bad", 1, "y", 5),)
    with pytest.raises(ValueError, match="no L2 analyst"):
        SimulationRequest(wrong, request.organization, "L2", request.policy,
                          request.settings)


@pytest.mark.parametrize("policy", ["D1", "P1", "WAPS"])
def test_continuous_adapter_matches_historical_engine_native_result(policy):
    request = build_request(calendar=None, policy=policy)
    roster = tuple(r.analyst for r in request.resources)
    services = {r.analyst.analyst_id: dict(r.service_by_class) for r in request.resources}
    baseline = simulate_original(
        request.alerts, roster, {"x": 3.0}, policy="HLS-B" if policy == "WAPS" else policy,
        admission_horizon=request.settings.admission_horizon,
        drain_period=request.settings.evaluation_horizon-request.settings.admission_horizon,
        random_seed=request.settings.seed, service_by_analyst_class=services,
        hlsb_config=request.policy.waps,
    )
    result = ContinuousBackend().run(request)
    assert result.native_result == baseline
    assert result.assignments == baseline.assignments
    assert result.tasks_by_alert["a"].analyst_id == baseline.assignments[0].analyst_id
    assert result.tasks_by_alert["a"].start == baseline.assignments[0].start
    assert result.tasks_by_alert["a"].completion == baseline.assignments[0].completion
    assert result.tasks_by_alert["a"].status is None
    assert result.tasks_by_alert["a"].effective_work is None
    assert result.tasks_by_alert["a"].remaining_work is None
    assert result.work_segments is None  # not exposed by the historical result type
    assert result.tasks_by_alert["a"].suspension is None


@pytest.mark.parametrize("policy", ["D1", "P1", "WAPS"])
def test_calendar_adapter_matches_native_calendar_result_and_preserves_pause_state(policy):
    request = build_request(calendar=WEEKDAY_9_TO_17, admission=24, evaluation=40,
                            service=3.0, policy=policy)
    roster = tuple(r.analyst for r in request.resources)
    forecast = {r.analyst.analyst_id: dict(r.forecast_service_by_class) for r in request.resources}
    actual = {r.analyst.analyst_id: dict(r.service_by_class) for r in request.resources}
    calendars = {r.analyst.analyst_id: r.calendar for r in request.resources}
    admitted = tuple(a for a in request.alerts if a.arrival < 24)
    baseline = simulate_calendar_original(admitted, roster, forecast, calendars,
                                          horizon=40, policy=policy, seed=17,
                                          actual_service=actual, waps_config=request.policy.waps)
    result = CalendarBackend().run(request)
    assert result.native_result == baseline
    assert result.assignments == baseline.assignments
    assert tuple(result.tasks_by_alert) == tuple(e.alert_id for e in baseline.episodes)
    task = result.tasks_by_alert["a"]
    assert task.status == baseline.episodes[0].status
    assert task.analyst_id == "L2-A"
    assert task.effective_work == dict(baseline.work_done_by_alert)["a"]
    assert task.suspension == baseline.episodes[0].suspension_h
    assert result.work_segments == tuple(
        type(result.work_segments[0])(aid, analyst_id, start, end)
        for aid, analyst_id, start, end in baseline.work_segments
    )


def test_uniform_scaling_is_applied_consistently_by_both_adapters():
    base = build_request(calendar=WEEKDAY_9_TO_17, admission=24, evaluation=40,
                         service=3.0, scale=1.0)
    scaled = build_request(calendar=WEEKDAY_9_TO_17, admission=24, evaluation=40,
                           service=3.0, scale=60.0)
    # Exercise a task begun during a shift; scaled calendar boundaries and service
    # must retain the same assignment and normalized task state.
    a = CalendarBackend().run(base)
    b = CalendarBackend().run(scaled)
    assert [(x.alert_id, x.analyst_id, x.start, x.completion) for x in a.assignments] == [
        (x.alert_id, x.analyst_id, x.start/60, x.completion/60) for x in b.assignments
    ]
    c = ContinuousBackend().run(build_request(calendar=None, scale=1.0))
    d = ContinuousBackend().run(build_request(calendar=None, scale=60.0))
    assert [(x.alert_id, x.analyst_id, x.start, x.completion) for x in c.assignments] == [
        (x.alert_id, x.analyst_id, x.start/60, x.completion/60) for x in d.assignments
    ]


def test_hidden_need_is_environment_only_for_continuous_dispatch(monkeypatch):
    from studies.soc_triage_hls_q1_integration_evidence import fp_workload_engine as hidden_engine

    request = build_request(calendar=CONTINUOUS, environment=EnvironmentRealization(
        {"a": .5, "b": 1.0}, {"a": False, "b": True}))
    seen = []
    original = hidden_engine._dispatch_d1

    def spy(*args, **kwargs):
        seen.append((args, kwargs))
        assert len(args) == 5
        assert not any(isinstance(arg, dict) and arg == request.environment.hidden_need_by_alert
                       for arg in args)
        return original(*args, **kwargs)

    monkeypatch.setattr(hidden_engine, "_dispatch_d1", spy)
    result = ContinuousBackend().run(request)
    assert result.native_result.assignments
    assert seen


def test_hidden_need_is_not_forwarded_to_calendar_dispatch(monkeypatch):
    from studies.soc_triage_hls_availability_robustness import availability_engine

    request = build_request(calendar=WEEKDAY_9_TO_17, environment=EnvironmentRealization(
        {"a": .5, "b": 1.0}, {"a": False, "b": True}))
    seen = []
    original = availability_engine._dispatch_d1

    def spy(*args, **kwargs):
        seen.append((args, kwargs))
        assert len(args) == 5
        assert not any(isinstance(arg, dict) and arg == request.environment.hidden_need_by_alert
                       for arg in args)
        return original(*args, **kwargs)

    monkeypatch.setattr(availability_engine, "_dispatch_d1", spy)
    CalendarBackend().run(request)
    assert seen


def test_calendar_backend_requires_explicit_per_analyst_calendar():
    request = build_request(calendar=None)
    with pytest.raises(ValueError, match="requires a calendar"):
        CalendarBackend().run(request)


def test_admission_and_evaluation_horizons_are_distinct_and_deadline_equality_is_on_time():
    request = build_request(calendar=WEEKDAY_9_TO_17, admission=24, evaluation=40,
                            service=3.0)
    alerts = (Alert("a", 16, "x", 35), Alert("after-admission", 30, "x", 45))
    request = SimulationRequest(alerts, request.organization, "L2", request.policy,
                                request.settings)
    result = CalendarBackend().run(request)
    assert set(result.tasks_by_alert) == {"a"}
    assert result.tasks_by_alert["a"].completion == 35
    assert result.tasks_by_alert["a"].status == "completed"

