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
                  scale=1.0, service=3.0, forecast_service=None, environment=None,
                  analysts=None, level="L2", alerts=None):
    analysts = analysts or [Analyst("L2-A", frozenset({"x"}), {"x": .8})]
    forecast_service = service if forecast_service is None else forecast_service
    resources = tuple(AnalystResource(a, {"x": service}, calendar,
                                      {"x": forecast_service}) for a in analysts)
    org = OrganizationConfig(resources, (TeamConfig(level, tuple(a.analyst_id for a in analysts)),))
    waps = HLSBConfig(4, 1.05, 1.2, .4) if policy == "WAPS" else None
    return SimulationRequest(
        tuple(alerts or (Alert("a", 16, "x", 32), Alert("b", 18, "x", 42))), org, level,
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
    with pytest.raises(ValueError, match="precede"):
        SimulationSettings(11, 10, 1, TimeScale(), DeadlineConfig({}))
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

    def spy(free, pending, now, service_time, rng, *args, **kwargs):
        seen.append(now)
        assert all(type(alert) is Alert for alert in pending.values())
        assert not any(isinstance(value, dict) and value == request.environment.hidden_need_by_alert
                       for value in (free, pending, kwargs))
        for analyst in free:
            for alert in pending.values():
                assert service_time(analyst, alert) == request.resources[0].forecast_service_by_class["x"]
        return original(free, pending, now, service_time, rng, *args, **kwargs)

    monkeypatch.setattr(availability_engine, "_dispatch_d1", spy)
    CalendarBackend().run(request)
    assert seen


def test_beta_zero_preserves_historical_alpha_service_on_both_backends():
    env = EnvironmentRealization(
        {"a": .25, "b": 1.0}, {"a": False, "b": True},
        {"a": .9, "b": .1}, difficulty_service_beta=0.0,
    )
    request = build_request(calendar=CONTINUOUS, service=4.0, environment=env)
    assert dict(env.realized_scales_for(("a", "b"))) == {"a": .25, "b": 1.0}
    continuous = ContinuousBackend().run(request)
    calendar = CalendarBackend().run(request)
    for result in (continuous, calendar):
        durations = {job.alert_id: job.completion - job.start for job in result.assignments}
        assert durations == {"a": 1.0, "b": 4.0}


def test_beta_changes_effective_service_but_not_forecast_or_dispatch():
    analysts = [Analyst("fast", frozenset({"x"}), {"x": .8}),
                Analyst("slow", frozenset({"x"}), {"x": .8})]
    alerts = (Alert("hard", 0, "x", 20), Alert("easy", 0, "x", 20))

    def run(beta, difficulty):
        env = EnvironmentRealization(
            hidden_need_by_alert={"hard": True, "easy": True},
            difficulty_by_alert=difficulty,
            difficulty_service_beta=beta,
        )
        request = build_request(calendar=CONTINUOUS, admission=1, evaluation=20,
                                service=2.0, forecast_service=2.0, environment=env,
                                analysts=analysts, alerts=alerts)
        return ContinuousBackend().run(request)

    zero = run(0.0, {"hard": .9, "easy": .1})
    positive = run(1.0, {"hard": .9, "easy": .1})
    zero_map = {a.alert_id: (a.analyst_id, a.start) for a in zero.assignments}
    positive_map = {a.alert_id: (a.analyst_id, a.start) for a in positive.assignments}
    assert positive_map == zero_map
    durations = {a.alert_id: a.completion - a.start for a in positive.assignments}
    assert durations == {"hard": pytest.approx(2.8), "easy": pytest.approx(1.2)}


def test_alpha_and_difficulty_multiply_once_for_l2_and_match_continuous_engines():
    env = EnvironmentRealization(
        {"fp": .25, "tp": 1.0}, {"fp": False, "tp": True},
        {"fp": .75, "tp": .75}, difficulty_service_beta=1.0,
    )
    request = build_request(calendar=CONTINUOUS, admission=1, evaluation=20,
                            service=4.0, forecast_service=4.0, environment=env,
                            alerts=(Alert("fp", 0, "x", 12), Alert("tp", 0, "x", 12)))
    assert dict(env.realized_scales_for(("fp", "tp"))) == {"fp": .3125, "tp": 1.25}
    continuous = ContinuousBackend().run(request)
    calendar = CalendarBackend().run(request)
    expected = {"fp": 1.25, "tp": 5.0}
    for result in (continuous, calendar):
        durations = {job.alert_id: job.completion - job.start for job in result.assignments}
        assert durations == expected
    assert [(x.alert_id, x.analyst_id, x.start, x.completion) for x in continuous.assignments] == [
        (x.alert_id, x.analyst_id, x.start, x.completion) for x in calendar.assignments
    ]

    l1_env = EnvironmentRealization(difficulty_by_alert={"fp": .75},
                                    difficulty_service_beta=1.0)
    l1_request = build_request(calendar=CONTINUOUS, admission=1, evaluation=20,
                               service=4.0, environment=l1_env,
                               analysts=[Analyst("L1-A", frozenset({"x"}), {"x": .8})],
                               level="L1", alerts=(Alert("fp", 0, "x", 12),))
    l1_result = ContinuousBackend().run(l1_request)
    assert l1_result.assignments[0].completion == 5.0  # difficulty only; no L2 alpha


def test_calendar_suspension_preserves_composed_work_and_original_deadline():
    env = EnvironmentRealization(
        {"late-fp": .25}, {"late-fp": False}, {"late-fp": 1.0},
        difficulty_service_beta=1.0,
    )
    alert = Alert("late-fp", 112, "x", 120)
    request = build_request(calendar=WEEKDAY_9_TO_17, admission=120, evaluation=180,
                            service=4.0, environment=env, alerts=(alert,))
    result = CalendarBackend().run(request)
    task = result.tasks_by_alert["late-fp"]
    assert task.completion == pytest.approx(177.5)
    assert task.effective_work == pytest.approx(1.5)
    assert task.suspension == pytest.approx(64.0)
    assert task.status == "completed_late"
    assert result.native_result.episodes[0].deadline == 120
    assert result.work_segments == (
        type(result.work_segments[0])("late-fp", "L2-A", 112, 113),
        type(result.work_segments[0])("late-fp", "L2-A", 177, 177.5),
    )


def test_difficulty_maps_remain_environment_only_for_both_dispatchers(monkeypatch):
    from studies.soc_triage_hls_q1_integration_evidence import fp_workload_engine
    from studies.soc_triage_hls_availability_robustness import availability_engine

    env = EnvironmentRealization({"a": .25, "b": 1.0}, {"a": False, "b": True},
                                 {"a": .9, "b": .1}, difficulty_service_beta=1.0)
    request = build_request(calendar=CONTINUOUS, environment=env)
    excluded = (env.hidden_need_by_alert, env.difficulty_by_alert,
                env.service_scale_by_alert, env.realized_scales_for(("a", "b")))
    seen = []

    for module, backend in ((fp_workload_engine, ContinuousBackend()),
                            (availability_engine, CalendarBackend())):
        original = module._dispatch_d1

        def spy(*args, _original=original, **kwargs):
            free, pending, _, forecast, _ = args
            assert all(forecast(analyst, alert) == 3.0
                       for analyst in free for alert in pending.values())
            assert not any(value is not None and any(arg is value for arg in args)
                           for value in excluded)
            assert not any(isinstance(arg, dict) and any(arg == value for value in excluded)
                           for arg in args)
            seen.append(True)
            return _original(*args, **kwargs)

        monkeypatch.setattr(module, "_dispatch_d1", spy)
        backend.run(request)
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

