from hls.rq1_allocation import Alert, Analyst, SOC_POLICY_NAMES, simulate


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
