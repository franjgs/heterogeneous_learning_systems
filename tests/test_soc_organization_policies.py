from hls.rq1_allocation import AllocationSession, Alert, Analyst, SOC_POLICY_NAMES, simulate


def _analyst(name, classes, competence=None):
    competence = competence or {task_class: 0.7 for task_class in classes}
    return Analyst(name, frozenset(classes), competence)


def _run(alerts, team, policy, services, *, seed=17, latency=0.0, edge_cost=0.0):
    return simulate(
        alerts, team, services, policy=policy, admission_horizon=2.0,
        drain_period=8.0, random_seed=seed,
        coordination_latency=latency, coordination_edge_cost=edge_cost,
    )


def test_active_soc_policy_inventory_is_minimal_and_includes_frozen_d1():
    assert SOC_POLICY_NAMES == ("D1", "P1", "P2", "P3", "P4", "P5")


def test_t_and_q_are_explicit_aliases_for_p1_and_p2_without_changing_them():
    alerts = [Alert("urgent", 0, "x", 2), Alert("loose", 0, "x", 8)]
    team = [_analyst("a", {"x"})]
    assert _run(alerts, team, "T", {"x": 1}).assignments == _run(alerts, team, "P1", {"x": 1}).assignments
    assert _run(alerts, team, "Q", {"x": 1}).assignments == _run(alerts, team, "P2", {"x": 1}).assignments


def test_c_selects_on_time_pair_when_t_selects_an_irrecoverably_late_alert():
    alerts = [Alert("late", 0, "x", 0.5), Alert("viable", 0, "x", 5)]
    team = [_analyst("a", {"x"}, {"x": 0.7})]
    assert _run(alerts, team, "T", {"x": 1}).assignments[0].alert_id == "late"
    result = _run(alerts, team, "C", {"x": 1})
    assert result.assignments[0].alert_id == "viable"


def test_c_uses_global_pair_information_and_pays_one_epoch_latency():
    alerts = [Alert("x", 0, "x", 2)]
    team = [_analyst("a-slow", {"x"}, {"x": 0.7}), _analyst("b-fast", {"x"}, {"x": 0.7})]
    services = {"x": 1}
    individual = {"a-slow": {"x": 2}, "b-fast": {"x": 0.5}}
    result = simulate(alerts, team, services, policy="C", admission_horizon=2,
                      drain_period=8, coordination_latency=0.25,
                      service_by_analyst_class=individual)
    assert result.assignments[0].analyst_id == "b-fast"
    assert result.assignments[0].start == 0.25
    assert result.coordination_latency_total == 0.25
    assert result.coordination_person_time == 0.25


def test_c_is_sequential_feasible_and_deterministic_with_multiple_pairs():
    alerts = [Alert("x", 0, "x", 8), Alert("y", 0, "y", 8), Alert("z", 0, "x", 8)]
    team = [_analyst("a", {"x", "y"}), _analyst("b", {"x"})]
    first = _run(alerts, team, "C", {"x": 1, "y": 1})
    second = _run(alerts, team, "C", {"x": 1, "y": 1})
    assert first == second
    assert len({job.alert_id for job in first.assignments}) == len(first.assignments)
    by_id = {a.analyst_id: a for a in team}
    alerts_by_id = {a.alert_id: a for a in alerts}
    assert all(alerts_by_id[j.alert_id].task_class in by_id[j.analyst_id].eligible_classes
               for j in first.assignments)
    assert len([j for j in first.assignments if j.start == 0]) == 2
    assert first.dispatch_decisions == 2


def test_c_empty_and_single_analyst_cases_and_latency_harm():
    empty = _run([], [_analyst("a", {"x"})], "C", {"x": 1})
    assert empty.assignments == ()
    one = simulate([Alert("x", 0, "x", 1.1)], [_analyst("a", {"x"})], {"x": 1},
                   policy="C", admission_horizon=1, drain_period=2,
                   coordination_latency=0.2)
    zero = simulate([Alert("x", 0, "x", 1.1)], [_analyst("a", {"x"})], {"x": 1},
                    policy="C", admission_horizon=1, drain_period=2)
    assert one.after_drain.completed_late == 1
    assert zero.after_drain.completed_within_sla == 1
    assert one.coordination_latency_total == 0.2


def test_c_equal_priority_ties_are_deterministic():
    alerts = [Alert("b", 0, "x", 5), Alert("a", 0, "x", 5)]
    team = [_analyst("z", {"x"}), _analyst("a", {"x"})]
    first = _run(alerts, team, "C", {"x": 1})
    second = _run(alerts, team, "C", {"x": 1})
    assert first.assignments == second.assignments


def test_p1_selects_smallest_predicted_post_service_slack():
    alerts = [Alert("later", 0, "x", 5), Alert("urgent", 0, "x", 2)]
    result = _run(alerts, [_analyst("a", {"x"})], "P1", {"x": 1})
    assert result.assignments[0].alert_id == "urgent"


def test_p2_prefers_own_competence_then_uses_temporal_slack():
    alerts = [Alert("strong", 0, "x", 5), Alert("weak", 0, "y", 1)]
    team = [_analyst("a", {"x", "y"}, {"x": 0.95, "y": 0.2})]
    result = _run(alerts, team, "P2", {"x": 1, "y": 1})
    assert result.assignments[0].alert_id == "strong"


def test_p3_preserves_scarce_eligibility_for_the_specialist():
    alerts = [Alert("shared-x", 0, "x", 5), Alert("flex-only-y", 0, "y", 5)]
    team = [
        _analyst("a-generalist", {"x", "y"}),
        _analyst("b-x-specialist", {"x"}),
    ]
    result = _run(alerts, team, "P3", {"x": 1, "y": 1})
    assert {job.analyst_id: job.alert_id for job in result.assignments} == {
        "a-generalist": "flex-only-y", "b-x-specialist": "shared-x",
    }


def test_p4_uses_joint_matching_to_maximize_predicted_on_time_assignments():
    alerts = [Alert("urgent-x", 0, "x", 1.5), Alert("slack-y", 0, "y", 3)]
    team = [
        _analyst("a", {"x", "y"}),
        _analyst("b", {"x", "y"}),
    ]
    services = {"x": 1, "y": 1}
    individual = {"a": {"x": 2, "y": 1}, "b": {"x": 1, "y": 2}}
    result = simulate(
        alerts, team, services, policy="P4", admission_horizon=2,
        service_by_analyst_class=individual,
    )
    assert {job.analyst_id: job.alert_id for job in result.assignments} == {
        "a": "slack-y", "b": "urgent-x",
    }
    assert result.at_horizon.completed_within_sla == 2


def test_p5_uses_local_p3_when_matching_does_not_improve_predicted_outcome():
    alerts = [Alert("only", 0, "x", 5)]
    team = [_analyst("a", {"x"}), _analyst("b", {"x"})]
    result = _run(alerts, team, "P5", {"x": 1}, latency=0.1, edge_cost=3)
    assert result.assignments[0].analyst_id == "a"
    assert result.assignments[0].start == 0
    assert result.coordination_latency_total == 0
    assert result.coordination_resource == 0


def test_p5_selects_matching_only_for_strict_predicted_improvement():
    alerts = [Alert("urgent-x", 0, "x", 1.5), Alert("slack-y", 0, "y", 3)]
    team = [_analyst("a", {"x", "y"}), _analyst("b", {"x", "y"})]
    services = {"x": 1, "y": 1}
    individual = {"a": {"x": 2, "y": 1}, "b": {"x": 1, "y": 2}}
    result = simulate(
        alerts, team, services, policy="P5", admission_horizon=2,
        service_by_analyst_class=individual, coordination_latency=0.0,
        coordination_edge_cost=0.5,
    )
    assert {job.analyst_id: job.alert_id for job in result.assignments} == {
        "a": "slack-y", "b": "urgent-x",
    }
    assert result.coordination_resource == 2.0


def test_p5_applies_positive_latency_once_when_selecting_matching():
    alerts = [Alert("urgent-x", 0, "x", 1.7), Alert("slack-y", 0, "y", 3.2)]
    team = [_analyst("a", {"x", "y"}), _analyst("b", {"x", "y"})]
    services = {"x": 1, "y": 1}
    individual = {"a": {"x": 2, "y": 1}, "b": {"x": 1, "y": 2}}
    result = simulate(
        alerts, team, services, policy="P5", admission_horizon=2,
        service_by_analyst_class=individual, coordination_latency=0.1,
        coordination_edge_cost=0.5,
    )
    assert {job.start for job in result.assignments} == {0.1}
    assert result.coordination_latency_total == 0.1
    assert result.coordination_person_time == 0.2
    assert result.coordination_resource == 2.0


def test_coordination_latency_is_applied_once_per_dispatch_and_delays_service():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5)]
    team = [_analyst("a", {"x"}), _analyst("b", {"y"})]
    result = _run(alerts, team, "P4", {"x": 1, "y": 1}, latency=0.25, edge_cost=2)
    assert {job.start for job in result.assignments} == {0.25}
    assert result.coordination_latency_total == 0.25
    assert result.coordination_person_time == 0.5
    assert result.coordination_resource == 4.0


def test_active_policies_preserve_alerts_eligibility_and_reproducibility():
    alerts = [
        Alert("x0", 0, "x", 0.1), Alert("y0", 0, "y", 8),
        Alert("x1", 0.2, "x", 8), Alert("z0", 0.3, "z", 8),
    ]
    team = [
        _analyst("a", {"x", "y"}, {"x": 0.8, "y": 0.9}),
        _analyst("b", {"x", "z"}, {"x": 0.7, "z": 0.95}),
    ]
    for policy in SOC_POLICY_NAMES:
        first = simulate(alerts, team, {"x": 1, "y": 1, "z": 1}, policy=policy,
                         admission_horizon=1, drain_period=8, random_seed=31)
        second = simulate(alerts, team, {"x": 1, "y": 1, "z": 1}, policy=policy,
                          admission_horizon=1, drain_period=8, random_seed=31)
        assert first == second
        assigned = [job.alert_id for job in first.assignments]
        assert len(assigned) == len(set(assigned))
        assert first.after_drain.admitted == (
            first.after_drain.completed_within_sla
            + first.after_drain.completed_late
            + first.after_drain.pending
        )
        alert_by_id = {alert.alert_id: alert for alert in alerts}
        analyst_by_id = {analyst.analyst_id: analyst for analyst in team}
        assert all(alert_by_id[job.alert_id].task_class in analyst_by_id[job.analyst_id].eligible_classes
                   for job in first.assignments)


def test_d1_frozen_dispatch_remains_reproducible_and_nonpreemptive():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5), Alert("later", 0.5, "x", 5)]
    team = [_analyst("a", {"x", "y"}), _analyst("b", {"x", "y"})]
    first = _run(alerts, team, "D1", {"x": 1, "y": 1}, seed=17)
    second = _run(alerts, team, "D1", {"x": 1, "y": 1}, seed=17)
    assert first == second
    initial = [job for job in first.assignments if job.start == 0]
    assert len(initial) == 2
    assert all(job.completion == job.start + 1 for job in first.assignments)


def test_immediate_dispatch_removes_edges_after_single_new_alert():
    session = AllocationSession(
        [Alert("one", 0.0, "x", 5.0)],
        [_analyst("a", {"x"}), _analyst("b", {"x"})],
        {"x": 1.0}, admission_horizon=2.0,
    )
    assert session.next_event_time() == 0.0
    session.advance_to(0.0)
    assert session.dispatch("P1") == ("one",)
    assert not any(
        alert.task_class in analyst.eligible_classes
        for alert in session.pending.values()
        for analyst in session.available_analysts()
    )


def test_simultaneous_arrivals_and_completions_can_create_multi_matching_state():
    session = AllocationSession(
        [
            Alert("initial-x", 0.0, "x", 10.0),
            Alert("initial-y", 0.0, "y", 10.0),
            Alert("batch-x", 1.0, "x", 10.0),
            Alert("batch-y", 1.0, "y", 10.0),
        ],
        [_analyst("a", {"x", "y"}), _analyst("b", {"x", "y"})],
        {"x": 1.0, "y": 1.0}, admission_horizon=2.0,
    )
    session.advance_to(0.0)
    assert len(session.dispatch("P1")) == 2
    assert not session.pending

    assert session.next_event_time() == 1.0
    completed = session.advance_to(1.0)
    assert len(completed) == 2
    assert {alert.alert_id for alert in session.arrived_at_now} == {"batch-x", "batch-y"}
    assert len(session.available_analysts()) == 2
    assert len(session.pending) == 2

    selected = session.dispatch("P4")
    assert set(selected) == {"batch-x", "batch-y"}
