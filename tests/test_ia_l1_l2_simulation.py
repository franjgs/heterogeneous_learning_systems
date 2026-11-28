from hls.rq1_allocation import Alert, Analyst, AllocationSession, simulate
from hls.ia_l1_l2_simulation import B4EpisodeEnv, ScenarioConfig, generate_alerts, run_episode


def _pools():
    classes = frozenset({"class_0", "class_1", "class_2"})
    l1 = (Analyst("l1a", classes, {k: 0.8 for k in classes}),)
    l2 = (Analyst("l2a", classes, {k: 0.9 for k in classes}),)
    service = {k: 0.002 for k in classes}
    return l1, l2, service


def test_generator_reproducibility_and_configured_confusion_matrix():
    config = ScenarioConfig(
        horizon=1.0, arrival_rate=100, ai_sensitivity=1.0,
        ai_false_positive_rate=0.0,
        escalation_probability_by_class=(1.0, 1.0, 1.0),
        ai_sensitivity_by_severity=(1.0, 1.0, 1.0),
        ai_false_positive_by_severity=(0.0, 0.0, 0.0),
    )
    first = generate_alerts(config, 42)
    second = generate_alerts(config, 42)
    assert first == second
    assert first
    assert all(row.true_escalation_need and row.routed.soctra_recommendation for row in first)
    mixed = generate_alerts(ScenarioConfig(
        horizon=1.0, arrival_rate=1000,
        escalation_probability_by_class=(0.5, 0.5, 0.5),
        ai_sensitivity=1.0, ai_false_positive_rate=0.0,
    ), 53)
    assert any(row.true_escalation_need for row in mixed)
    assert any(not row.true_escalation_need for row in mixed)
    assert all(row.routed.soctra_recommendation == row.true_escalation_need for row in mixed)


def test_reference_escalation_can_be_derived_from_difficulty_threshold_without_extra_draws():
    base = ScenarioConfig(horizon=1.0, arrival_rate=500,
                          escalation_probability_by_class=(0.2, 0.5, 0.8))
    threshold = 0.75
    routed = ScenarioConfig(horizon=1.0, arrival_rate=500,
                            escalation_probability_by_class=(0.2, 0.5, 0.8),
                            reference_escalation_difficulty_threshold=threshold)
    base_trace = generate_alerts(base, 771)
    routed_trace = generate_alerts(routed, 771)
    assert len(base_trace) == len(routed_trace)
    assert [(a.routed.alert, a.difficulty) for a in base_trace] == [
        (a.routed.alert, a.difficulty) for a in routed_trace
    ]
    assert all(row.true_escalation_need == (row.difficulty >= threshold)
               for row in routed_trace)
    assert [row.severity for row in base_trace] == [row.severity for row in routed_trace]


def test_hidden_reference_not_in_observation_and_actions_b0_b1_b2_run():
    l1, l2, service = _pools()
    config = ScenarioConfig(horizon=0.2, arrival_rate=80)
    for action, policy in enumerate(("B0", "B1", "B2")):
        env = B4EpisodeEnv(config, l1, l2, service, service, drain_period=0.1)
        obs, _ = env.reset(seed=11)
        assert "true_escalation_need" not in obs
        decisions = 0
        while True:
            obs, reward, terminated, truncated, info = env.step((action + decisions) % 3)
            decisions += 1
            assert not truncated
            assert info["decision_index"] == decisions
            assert "true_escalation_need" not in obs
            assert "historical_label" not in info
            if terminated:
                break
            assert "elapsed_time" in info
        assert decisions > 1
        assert "sla_fraction" in info
        assert info["admitted"] == info["completed"] + info["pending"]
        assert len({job.alert_id for job in env._l1.assignments}) == len(env._l1.assignments)
        assert len({job.alert_id for job in env._l2.assignments}) == len(env._l2.assignments)


def test_terminal_sla_uses_l2_final_completion_for_escalated_alerts():
    l1 = (Analyst("l1", frozenset({"x"}), {"x": 0.8}),)
    l2 = (Analyst("l2", frozenset({"x"}), {"x": 0.9}),)
    config = ScenarioConfig(
        horizon=0.2, arrival_rate=35, classes=("x",),
        class_probabilities=(1.0,), escalation_probability_by_class=(0.5,),
        ai_sensitivity=1.0, ai_false_positive_rate=1.0,
        deadline_by_severity=(("low", 0.03), ("medium", 0.03), ("high", 0.03)),
    )
    env = B4EpisodeEnv(config, l1, l2, {"x": 0.005}, {"x": 0.04}, drain_period=0.5)
    env.reset(seed=12)
    while True:
        _, _, terminated, truncated, info = env.step_fixed("D1")
        assert not truncated
        if terminated:
            break
    l1_jobs = {j.alert_id: j for j in env._l1.assignments}
    l2_jobs = {j.alert_id: j for j in env._l2.assignments}
    expected_final_ontime = sum(
        (l2_jobs[aid].completion if env._routing[aid] else l1_jobs[aid].completion)
        <= env._all_alerts[aid].deadline
        for aid in env._resolved
    )
    naive_first_stage_ontime = sum(
        l1_jobs[aid].completion <= env._all_alerts[aid].deadline
        for aid in env._resolved
    )
    assert any(env._routing.values())
    assert naive_first_stage_ontime > expected_final_ontime
    assert info["completed_within_sla"] == expected_final_ontime
    assert info["sla_fraction"] == expected_final_ontime / info["admitted"]


def test_fixed_seed_episode_and_reward_are_reproducible():
    l1, l2, service = _pools()
    config = ScenarioConfig(horizon=0.3, arrival_rate=50, burst_window=(0.1, 0.2, 3.0))
    a = run_episode(config, 7, policy="B1", l1_analysts=l1, l2_analysts=l2,
                    l1_service_by_class=service, l2_service_by_class=service, drain_period=0.2)
    b = run_episode(config, 7, policy="B1", l1_analysts=l1, l2_analysts=l2,
                    l1_service_by_class=service, l2_service_by_class=service, drain_period=0.2)
    assert a == b


def test_fixed_b3_episode_control_remains_available():
    l1, l2, service = _pools()
    outcome = run_episode(ScenarioConfig(horizon=0.3, arrival_rate=80), 12,
                          policy="B3", l1_analysts=l1, l2_analysts=l2,
                          l1_service_by_class=service, l2_service_by_class=service,
                          drain_period=0.2)
    assert outcome.policy == "B3"
    assert sum(value for _, value in outcome.simulation.selected_strategy_counts) > 0


def test_service_speed_can_vary_independently_of_competence():
    eligible = frozenset({"class_0"})
    analysts = (
        Analyst("a-slow", eligible, {"class_0": 0.8}),
        Analyst("b-fast", eligible, {"class_0": 0.8}),
    )
    result = simulate(
        (Alert("one", 0.0, "class_0", 10.0), Alert("two", 0.0, "class_0", 10.0)),
        analysts, {"class_0": 1.0}, policy="B0", admission_horizon=1.0,
        service_by_analyst_class={"a-slow": {"class_0": 5.0}, "b-fast": {"class_0": 0.1}},
    )
    completion = {row.analyst_id: row.completion for row in result.assignments}
    assert completion == {"a-slow": 5.0, "b-fast": 0.1}


def test_resumable_session_matches_existing_fixed_policy_engine():
    l1, _, service = _pools()
    alerts = tuple(Alert(f"a{i}", i * 0.02, "class_0", 1.0) for i in range(8))
    expected = simulate(alerts, l1, service, policy="B1", admission_horizon=0.2,
                        drain_period=0.3, coordination_latency=0.001, random_seed=8)
    session = AllocationSession(alerts, l1, service, admission_horizon=0.2,
                                drain_period=0.3, coordination_latency=0.001, random_seed=8)
    while not session._finalized:
        event_time = session.next_event_time()
        assert event_time is not None
        session.advance_to(event_time)
        if session.can_dispatch():
            session.dispatch("B1")
    actual = session.result("B1")
    assert actual.assignments == expected.assignments
    assert actual.at_horizon == expected.at_horizon
    assert actual.after_drain == expected.after_drain


def test_new_observations_are_bounded_and_arrival_history_is_causal():
    l1, l2, service = _pools()
    env = B4EpisodeEnv(ScenarioConfig(horizon=1.0, arrival_rate=100), l1, l2,
                       service, service, drain_period=0.1)
    obs, _ = env.reset(seed=71)
    assert {"arrival_rate_recent_norm", "arrival_rate_previous_norm", "arrival_rate_trend_norm",
            "l1_competence_dispersion", "l2_competence_dispersion"} <= obs.keys()
    assert all(0.0 <= value <= 1.0 for value in obs.values())
    assert env._observed_arrival_times
    assert all(time <= env._l1.now for time in env._observed_arrival_times)
    assert len(env._observed_arrival_times) < len(env._admitted)
    before = env._observation()
    env._admitted = (*env._admitted, env._admitted[-1])  # hidden future total changes; observable state does not
    assert env._observation() == before


def test_competence_dispersion_tracks_available_team_composition():
    eligible = frozenset({"class_0", "class_1", "class_2"})
    analysts = (
        Analyst("L1-team0-0", eligible, {k: 0.7 for k in eligible}),
        Analyst("L1-team0-1", eligible, {k: 0.7 for k in eligible}),
        Analyst("L1-team1-0", eligible, {"class_0": 0.95, "class_1": 0.55, "class_2": 0.40}),
        Analyst("L1-team1-1", eligible, {"class_0": 0.45, "class_1": 0.90, "class_2": 0.65}),
    )
    l2 = (Analyst("l2", eligible, {k: 0.8 for k in eligible}),)
    service = {k: 0.002 for k in eligible}
    env = B4EpisodeEnv(ScenarioConfig(horizon=0.2, arrival_rate=80), analysts, l2,
                       service, service, drain_period=0.1,
                       l1_roster_schedule=((0.0, ("L1-team0-0", "L1-team0-1")),
                                           (0.1, ("L1-team1-0", "L1-team1-1"))))
    env.reset(seed=91)
    assert env._l1.available_analysts() == analysts[:2]
    assert env._observation()["l1_competence_dispersion"] == 0.0
    env._l1.advance_to(0.1)
    assert env._l1.available_analysts() == analysts[2:]
    assert env._observation()["l1_competence_dispersion"] > 0.0


def test_piecewise_arrival_rate_generator_reproducible_and_validated():
    config = ScenarioConfig(horizon=1.0, arrival_rate=24,
                            arrival_rate_shift_after=0.5, arrival_rate_after=180)
    first = generate_alerts(config, 131)
    assert first == generate_alerts(config, 131)
    before = sum(row.routed.alert.arrival < 0.5 for row in first)
    after = sum(row.routed.alert.arrival >= 0.5 for row in first)
    assert after > before


def test_organizational_actions_are_operational_and_keep_cost_measures_separate():
    classes = frozenset({"class_0", "class_1", "class_2"})
    l1 = (
        Analyst("a-fast", classes, {k: 0.55 for k in classes}),
        Analyst("b-slow", classes, {k: 0.95 for k in classes}),
    )
    l2 = (Analyst("l2", classes, {k: 0.8 for k in classes}),)
    service = {k: 0.1 for k in classes}
    session = AllocationSession(
        (Alert("known-arrival", 0.0, "class_0", 0.3),), l1, service,
        admission_horizon=1.0, drain_period=0.2, coordination_edge_cost=0.02,
        coordination_screen_cost=0.002,
    )
    session.advance_to(0.0)
    proposal = session.preview_organization("C2P1", coordination_latency_override=0.05)
    assert proposal["resource"] == 0.04
    assert proposal["latency"] == 0.05
    assert len(session.pending) == 1 and not session.assignments
    session.dispatch_organization("C2P1", coordination_latency_override=0.05)
    while not session._finalized:
        event = session.next_event_time()
        assert event is not None
        session.advance_to(event)
        if session.can_dispatch():
            session.dispatch_organization("C0P0")
    assigned = [j for j in session.assignments if j.alert_id == "known-arrival"]
    assert len(assigned) == 1
    assert assigned[0].analyst_id == "b-slow"
    assert assigned[0].start == 0.05
    assert session.coordination_resource > 0
    assert session.coordination_latency_total == 0.05
    assert session.coordination_resource != session.coordination_person_time
    assert session.organization_action_counts["C2P1"] > 0


def test_adaptive_organizational_controller_uses_observable_queue_state_only():
    from hls.ia_l1_l2_simulation import adaptive_organizational_action

    low = {"l1_backlog_norm": 0.0, "l2_backlog_norm": 0.0,
           "l1_available_fraction": 1.0, "l2_available_fraction": 1.0,
           "deadline_pressure_l1": 0.0, "deadline_pressure_l2": 0.0,
           "l1_competence_dispersion": 0.0, "l2_competence_dispersion": 0.0}
    urgent = dict(low, deadline_pressure_l1=0.5)
    loaded = dict(low, l1_backlog_norm=0.08, l1_competence_dispersion=0.3)
    assert adaptive_organizational_action(low) == "C0P0"
    assert adaptive_organizational_action(urgent) == "C1P0"
    assert adaptive_organizational_action(loaded) == "C2P1"
    assert "true_escalation_need" not in low


def test_six_organizational_actions_run_complete_paired_episodes():
    l1, l2, service = _pools()
    config = ScenarioConfig(horizon=0.15, arrival_rate=160,
                            escalation_probability_by_class=(0.15, 0.15, 0.15))
    outcomes = []
    for action in B4EpisodeEnv.organizational_actions:
        env = B4EpisodeEnv(config, l1, l2, service, service, drain_period=0.2,
                           coordination_edge_cost=0.0004,
                           coordination_screen_cost=0.00004)
        env.reset(seed=812)
        while True:
            _, _, terminated, truncated, info = env.step_fixed_organization(action)
            assert not truncated
            assert "true_escalation_need" not in env._observation()
            if terminated:
                break
        assert info["admitted"] == info["completed"] + info["pending"]
        assert len({j.alert_id for j in env._l1.assignments}) == len(env._l1.assignments)
        assert len({j.alert_id for j in env._l2.assignments}) == len(env._l2.assignments)
        assert all(j.start >= env._all_alerts[j.alert_id].arrival for j in (*env._l1.assignments, *env._l2.assignments))
        assert info["organization_action_counts"][action] > 0
        outcomes.append((info["admitted"], info["sla_fraction"], info["coordination_resource"],
                         info["coordination_latency_total"], info["completed"], info["pending"]))
    assert len({row[0] for row in outcomes}) == 1
    assert len(outcomes) == 6
