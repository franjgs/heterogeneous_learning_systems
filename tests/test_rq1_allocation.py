from hls.rq1_allocation import Alert, Analyst, B3Config, simulate, AllocationSession


def analyst(name, classes, competence=None):
    competence = competence or {task_class: 0.7 for task_class in classes}
    return Analyst(name, frozenset(classes), competence)


def run(alerts, analysts, policy="B0", service=None, horizon=10, drain=0):
    classes = {a.task_class for a in alerts} | {k for x in analysts for k in x.eligible_classes}
    service = service or {task_class: 1.0 for task_class in classes}
    return simulate(alerts, analysts, service, policy=policy,
                    admission_horizon=horizon, drain_period=drain)


def test_one_alert_one_analyst_and_drain_metrics():
    alerts = [Alert("a", 0, "x", 2)]
    team = [analyst("n1", {"x"})]
    result = run(alerts, team, "B0", horizon=0.5, drain=2)
    assert result.at_horizon.admitted == 1
    assert result.at_horizon.pending == 1
    assert result.after_drain.completed_within_sla == 1
    assert result.after_drain.mean_response_completed == 1
    assert result.after_drain.modeled_quality_per_admitted == 0.7


def test_two_analysts_process_multiple_alerts_without_double_assignment():
    alerts = [Alert(str(i), 0, "x", 20) for i in range(5)]
    result = run(alerts, [analyst("a", {"x"}), analyst("b", {"x"})], "B1", horizon=3, drain=5)
    ids = [job.alert_id for job in result.assignments]
    assert len(ids) == len(set(ids)) == 5
    assert result.after_drain.admitted == 5
    assert result.after_drain.completed_within_sla == 5


def test_project_eligibility_is_enforced():
    alerts = [Alert("a", 0, "x", 5), Alert("b", 0, "y", 5)]
    team = [analyst("a", {"x"}), analyst("b", {"y"})]
    result = run(alerts, team, "B1", horizon=2)
    assigned = {job.alert_id: job.analyst_id for job in result.assignments}
    assert assigned == {"a": "a", "b": "b"}


def test_identical_deadlines_use_reproducible_alert_tie_order():
    alerts = [Alert("z", 0, "x", 5), Alert("a", 0, "x", 5)]
    team = [analyst("n", {"x"})]
    first = run(alerts, team, "B0", horizon=1, drain=2)
    second = run(list(reversed(alerts)), team, "B0", horizon=1, drain=2)
    assert first.assignments == second.assignments
    assert first.assignments[0].alert_id == "a"


def test_simultaneous_arrival_and_completion_releases_analyst_before_dispatch():
    alerts = [Alert("first", 0, "x", 10), Alert("second", 1, "x", 10)]
    result = run(alerts, [analyst("n", {"x"})], "B0", horizon=3)
    assert [(x.alert_id, x.start, x.completion) for x in result.assignments] == [
        ("first", 0, 1), ("second", 1, 2)
    ]


def test_overdue_alert_is_still_processed_and_counted_late():
    result = run([Alert("late", 0, "x", -1)], [analyst("n", {"x"})], "B1", horizon=2)
    assert len(result.assignments) == 1
    assert result.at_horizon.completed_late == 1
    assert result.at_horizon.completed_within_sla == 0


def test_empty_system_and_no_eligible_analyst_are_valid():
    empty = run([], [analyst("n", {"x"})], "B2", horizon=2, drain=1)
    assert empty.at_horizon.admitted == empty.at_horizon.pending == 0
    assert empty.at_horizon.fraction_within_sla == 0
    isolated = run([Alert("a", 0, "x", 5)], [analyst("n", {"y"})], "B1", horizon=2, drain=1)
    assert not isolated.assignments
    assert isolated.after_drain.pending == 1


def test_reproducibility_and_conservation():
    alerts = [Alert(f"a{i}", i * 0.1, "x", 4) for i in range(8)]
    team = [analyst("b", {"x"}), analyst("a", {"x"})]
    first = run(alerts, team, "B2", horizon=1, drain=5)
    second = run(alerts, team, "B2", horizon=1, drain=5)
    assert first == second
    assert first.after_drain.admitted == first.after_drain.completed_within_sla + first.after_drain.completed_late + first.after_drain.pending
    assert len({job.alert_id for job in first.assignments}) == len(first.assignments)


def test_b0_and_b1_are_equivalent_in_one_analyst_trivial_case():
    alerts = [Alert("a", 0, "x", 2), Alert("b", 0.1, "x", 3)]
    team = [analyst("n", {"x"})]
    b0 = run(alerts, team, "B0", horizon=1, drain=3)
    b1 = run(alerts, team, "B1", horizon=1, drain=3)
    assert b0.assignments == b1.assignments


def test_b1_can_differ_from_b0_to_satisfy_more_deadlines():
    alerts = [Alert("x", 0, "x", 0.5), Alert("y", 0, "y", 1.5)]
    team = [analyst("a-flex", {"x", "y"}), analyst("b-x", {"x"})]
    b0 = run(alerts, team, "B0", horizon=2)
    b1 = run(alerts, team, "B1", horizon=2)
    assert b0.at_horizon.completed_within_sla == 0
    assert b1.at_horizon.completed_within_sla == 1
    assert b1.at_horizon.completed_late == 1
    b1_map = {job.analyst_id: job.alert_id for job in b1.assignments}
    assert b1_map == {"a-flex": "y", "b-x": "x"}


def test_b2_can_choose_different_assignment_without_changing_sla_count():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5)]
    team = [
        Analyst("a", frozenset({"x", "y"}), {"x": 0.2, "y": 0.95}),
        Analyst("b", frozenset({"x", "y"}), {"x": 0.95, "y": 0.2}),
    ]
    b1 = run(alerts, team, "B1", horizon=2)
    b2 = run(alerts, team, "B2", horizon=2)
    assert {x.analyst_id: x.alert_id for x in b1.assignments} != {x.analyst_id: x.alert_id for x in b2.assignments}
    assert b2.at_horizon.completed_within_sla == b1.at_horizon.completed_within_sla == 2
    assert b2.at_horizon.modeled_quality_per_admitted > b1.at_horizon.modeled_quality_per_admitted


def test_b2_does_not_improve_sla_count_when_all_assignments_are_on_time():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5)]
    team = [
        Analyst("a", frozenset({"x", "y"}), {"x": 0.2, "y": 0.95}),
        Analyst("b", frozenset({"x", "y"}), {"x": 0.95, "y": 0.2}),
    ]
    b1 = run(alerts, team, "B1", horizon=2)
    b2 = run(alerts, team, "B2", horizon=2)
    assert b2.at_horizon.completed_within_sla == b1.at_horizon.completed_within_sla


def test_d1_uses_own_duration_risk_and_competence_before_peer_specialty_tie_break():
    alerts = [Alert("urgent-x", 0, "x", 0.5), Alert("capable-y", 0, "y", 8),
              Alert("weak-z", 0, "z", 8)]
    team = [Analyst("analyst", frozenset({"x", "y", "z"}), {"x": 0.5, "y": 0.9, "z": 0.2})]
    result = simulate(alerts, team, {"x": 1, "y": 2, "z": 1}, policy="D1",
                      admission_horizon=1, drain_period=2, random_seed=23)
    assert result.assignments[0].alert_id == "urgent-x"  # service-aware SLA risk
    assert result.assignments[1].alert_id == "capable-y"  # own competence breaks equal-risk tie


def test_d1_uses_general_peer_eligibility_without_exact_peer_competence():
    team = [
        Analyst("generalist", frozenset({"x", "y"}), {"x": 0.8, "y": 0.8}),
        Analyst("x-specialist", frozenset({"x"}), {"x": 0.99}),
    ]
    alerts = [Alert("x1", 0, "x", 5), Alert("y1", 0, "y", 5)]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=0, diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1")
    assigned = {row.alert_id: row.analyst_id for row in session.assignments}
    # X's peer is known only to be eligible for X; the generalist covers Y.
    assert assigned == {"x1": "x-specialist", "y1": "generalist"}
    assert len({row.alert_id for row in session.assignments}) == 2


def test_d1_crossed_competencies_are_resolved_by_individual_choices_not_matching():
    team = [
        Analyst("x-strong", frozenset({"x", "y"}), {"x": 0.95, "y": 0.30}),
        Analyst("y-strong", frozenset({"x", "y"}), {"x": 0.30, "y": 0.95}),
    ]
    alerts = [Alert("x-task", 0, "x", 5), Alert("y-task", 0, "y", 5)]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=17, diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1")
    assert len({decision.alert_id for decision in session.d1_decisions}) == 2
    assert session.d1_decisions[0].own_competence == 0.95
    assert session.d1_decisions[1].own_competence == 0.95


def test_d1_trace_captures_current_alternatives_and_busy_specialist_without_hidden_labels():
    team = [analyst("x-specialist", {"x"}), analyst("y-generalist", {"y"})]
    alerts = [Alert("x-first", 0, "x", 5), Alert("x-wait", 0.2, "x", 5),
              Alert("y-wait", 0.2, "y", 5)]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=9, diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1")
    session.advance_to(0.2)
    session.dispatch("D1")
    decision = session.d1_decisions[-1]
    assert decision.queue_alert_ids == ("x-wait", "y-wait")
    assert decision.occupied_specialists == (("x-specialist", "x-first", 1.0),)
    assert {candidate.alert_id for candidate in decision.candidates} == {"y-wait"}
    assert not hasattr(decision, "true_escalation_need")
    assert session.d1_dispatch_snapshots[-1].time == 0.2
    plain = AllocationSession(alerts, team, {"x": 1, "y": 1},
                              admission_horizon=1, random_seed=9)
    plain.advance_to(0)
    plain.dispatch("D1")
    plain.advance_to(0.2)
    plain.dispatch("D1")
    assert plain.assignments == session.assignments
    assert plain.d1_dispatch_snapshots == []


def test_d1l_replaces_only_irrecoverable_choice_and_keeps_it_pending():
    alerts = [Alert("doomed", 0, "x", 0.01), Alert("viable-low", 0, "y", 2),
              Alert("viable-high", 0, "z", 2)]
    team = [Analyst("a", frozenset({"x", "y", "z"}),
                    {"x": 0.5, "y": 0.6, "z": 0.9})]
    original = run(alerts, team, "D1", service={"x": 1, "y": 1, "z": 1},
                   horizon=3, drain=2)
    session = AllocationSession(alerts, team, {"x": 1, "y": 1, "z": 1},
                                admission_horizon=3, drain_period=2,
                                random_seed=0, diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1-L")
    assert session.assignments[0].alert_id == "viable-high"
    assert "doomed" in session.pending  # review does not discard impossible work
    assert session.d1l_review_count == 1
    assert session.d1_decisions[0].baseline_alert_id == "doomed"
    assert session.d1_decisions[0].alert_id == "viable-high"
    assert session.d1_decisions[0].review_activated
    session.advance_to(1)
    session.dispatch("D1-L")
    session.advance_to(2)
    session.dispatch("D1-L")
    assert any(job.alert_id == "doomed" for job in session.assignments)
    assert original.assignments[0].alert_id == "doomed"


def test_d1l_does_not_review_when_no_alternative_can_meet_sla():
    alerts = [Alert("a", 0, "x", 0.01), Alert("b", 0, "y", 0.02)]
    team = [Analyst("n", frozenset({"x", "y"}), {"x": 0.9, "y": 0.8})]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=2,
                                diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1-L")
    assert session.d1_decisions[0].alert_id == session.d1_decisions[0].baseline_alert_id
    assert not session.d1_decisions[0].review_activated
    assert session.d1l_review_count == 0


def test_d1s_rejects_viable_switch_that_reduces_own_competence():
    alerts = [Alert("urgent", 0, "x", 0.1), Alert("viable", 0, "y", 2)]
    team = [Analyst("n", frozenset({"x", "y"}), {"x": 0.9, "y": 0.5})]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=2,
                                diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1-S")
    decision = session.d1_decisions[0]
    assert decision.alert_id == decision.baseline_alert_id == "urgent"
    assert not decision.review_activated
    assert session.d1s_review_count == 0
    assert "viable" in session.pending


def test_d1s_accepts_viable_switch_when_competence_and_duration_do_not_worsen():
    alerts = [Alert("urgent", 0, "x", 0.1), Alert("viable", 0, "y", 2)]
    team = [Analyst("n", frozenset({"x", "y"}), {"x": 0.8, "y": 0.8})]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=2,
                                diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1-S")
    decision = session.d1_decisions[0]
    assert decision.alert_id == "viable"
    assert decision.baseline_alert_id == "urgent"
    assert decision.review_activated
    assert session.d1s_review_count == 1


def test_d1s_rejects_viable_switch_that_is_slower_for_same_analyst():
    alerts = [Alert("urgent", 0, "x", 0.1), Alert("viable", 0, "y", 2)]
    team = [Analyst("n", frozenset({"x", "y"}), {"x": 0.8, "y": 0.8})]
    session = AllocationSession(alerts, team, {"x": 1, "y": 1},
                                admission_horizon=1, random_seed=2,
                                service_by_analyst_class={"n": {"x": 0.5, "y": 1.0}},
                                diagnostic_d1=True)
    session.advance_to(0)
    session.dispatch("D1-S")
    decision = session.d1_decisions[0]
    assert decision.alert_id == decision.baseline_alert_id == "urgent"
    assert not decision.review_activated
    assert session.d1s_review_count == 0


def test_d1_simultaneous_order_is_seeded_and_finite_queue_does_not_starve():
    alerts = [Alert(f"x{i}", i * 0.25, "x", 10) for i in range(8)]
    team = [analyst("a", {"x"}), analyst("b", {"x"})]
    first = run(alerts, team, "D1", horizon=3, drain=10)
    second = run(alerts, team, "D1", horizon=3, drain=10)
    assert first == second
    assert len(first.assignments) == len(alerts)
    assert len({row.alert_id for row in first.assignments}) == len(alerts)


def test_d1_honors_restricted_eligibility_and_processes_each_alert_once():
    alerts = [Alert("x", 0, "x", 3), Alert("y", 0, "y", 3), Alert("z", 0, "z", 3)]
    team = [analyst("x-only", {"x"}), analyst("yz", {"y", "z"})]
    result = run(alerts, team, "D1", horizon=1, drain=4)
    assignments = {row.alert_id: row.analyst_id for row in result.assignments}
    assert assignments["x"] == "x-only"
    assert assignments["y"] == assignments["z"] == "yz"
    assert result.after_drain.admitted == 3
    assert result.after_drain.pending == 0


def test_b0_randomized_order_is_seeded_and_still_uses_local_edf():
    alerts = [Alert("later", 0, "x", 5), Alert("earlier", 0, "x", 2)]
    team = [analyst("n", {"x"})]
    first = simulate(alerts, team, {"x": 1.0}, policy="B0-R",
                     admission_horizon=1, drain_period=2, random_seed=17)
    second = simulate(alerts, team, {"x": 1.0}, policy="B0-R",
                      admission_horizon=1, drain_period=2, random_seed=17)
    assert first == second
    assert first.assignments[0].alert_id == "earlier"


def test_b0_randomized_order_can_change_which_analyst_claims_shared_work():
    alerts = [Alert("x", 0, "x", 0.5), Alert("y", 0, "y", 1.5)]
    team = [analyst("a-flex", {"x", "y"}), analyst("b-x", {"x"})]
    outcomes = {
        tuple((job.alert_id, job.analyst_id) for job in simulate(
            alerts, team, {"x": 1.0, "y": 1.0}, policy="B0-R",
            admission_horizon=2, random_seed=seed,
        ).assignments)
        for seed in range(12)
    }
    assert len(outcomes) > 1


def test_b0_f_dispatches_least_flexible_analysts_first_but_keeps_edf():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5)]
    team = [analyst("a-flex", {"x", "y"}), analyst("b-x", {"x"})]
    result = run(alerts, team, "B0-F", horizon=2)
    start_by_agent = {job.analyst_id: (job.alert_id, job.start) for job in result.assignments}
    assert start_by_agent == {"a-flex": ("y", 0), "b-x": ("x", 0)}


def test_b0_random_seed_must_be_integer():
    alerts = [Alert("x", 0, "x", 2)]
    team = [analyst("n", {"x"})]
    try:
        simulate(alerts, team, {"x": 1}, policy="B0-R", admission_horizon=1, random_seed=1.5)
    except ValueError as exc:
        assert "random_seed" in str(exc)
    else:
        raise AssertionError("non-integer randomized-control seed should be rejected")


def test_coordinated_matching_reaches_declared_lexicographic_objective():
    from itertools import product
    from hls.rq1_allocation import _dispatch_coordinated

    team = [
        Analyst("a", frozenset({"x", "y"}), {"x": 0.2, "y": 0.9}),
        Analyst("b", frozenset({"x"}), {"x": 0.8}),
    ]
    alerts = {
        "x1": Alert("x1", 0, "x", 0.8),
        "x2": Alert("x2", 0, "x", 3.0),
        "y": Alert("y", 0, "y", 1.0),
    }
    services = {"x": 0.5, "y": 0.75}
    ordered = sorted(alerts.values(), key=lambda a: (a.deadline, a.arrival, a.alert_id))
    rank = {alert.alert_id: ix for ix, alert in enumerate(ordered)}

    for policy in ("B1", "B2"):
        actual = _dispatch_coordinated(team, alerts, services, 0, policy)

        def objective(pairs):
            on_time = sum(0 + services[alert.task_class] <= alert.deadline for _, alert in pairs)
            assigned = len(pairs)
            competence = sum(
                analyst.competence[alert.task_class]
                for analyst, alert in pairs
                if services[alert.task_class] <= alert.deadline
            )
            deadline_preference = -sum(rank[alert.alert_id] for _, alert in pairs)
            return (on_time, assigned, deadline_preference) if policy == "B1" else (
                on_time, competence, assigned, deadline_preference
            )

        choices = []
        for analyst in team:
            choices.append([None] + [a for a in ordered if a.task_class in analyst.eligible_classes])
        feasible = []
        for candidate in product(*choices):
            assigned_alerts = [alert.alert_id for alert in candidate if alert is not None]
            if len(assigned_alerts) != len(set(assigned_alerts)):
                continue
            feasible.append(tuple((team[ix], alert) for ix, alert in enumerate(candidate) if alert is not None))
        assert objective(actual) == max(objective(candidate) for candidate in feasible)


def test_asymmetric_specialists_and_generalists_obey_eligibility():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5)]
    team = [
        analyst("a-general", {"x", "y"}),
        analyst("b-special-x", {"x"}),
        analyst("c-special-y", {"y"}),
    ]
    result = run(alerts, team, "B0-F", horizon=2)
    assert {job.alert_id: job.analyst_id for job in result.assignments} == {
        "x": "b-special-x", "y": "c-special-y",
    }


def test_zero_coordination_latency_preserves_b1_and_b2_assignments():
    alerts = [Alert("x", 0, "x", 5), Alert("y", 0, "y", 5)]
    team = [
        Analyst("a", frozenset({"x", "y"}), {"x": 0.2, "y": 0.95}),
        Analyst("b", frozenset({"x", "y"}), {"x": 0.95, "y": 0.2}),
    ]
    for policy in ("B1", "B2"):
        original = simulate(alerts, team, {"x": 1, "y": 1}, policy=policy, admission_horizon=2)
        explicit_zero = simulate(
            alerts, team, {"x": 1, "y": 1}, policy=policy,
            admission_horizon=2, coordination_latency=0,
        )
        assert original == explicit_zero


def test_positive_coordination_latency_delays_service_and_counts_as_wait():
    result = simulate(
        [Alert("a", 0, "x", 5)], [analyst("n", {"x"})], {"x": 1},
        policy="B1", admission_horizon=3, coordination_latency=0.5,
    )
    assert result.assignments[0].start == 0.5
    assert result.assignments[0].completion == 1.5
    assert result.after_drain.mean_response_completed == 1.5
    assert result.coordination_latency == 0.5


def test_one_joint_decision_charges_latency_once_for_all_assigned_analysts():
    alerts = [Alert("a", 0, "x", 5), Alert("b", 0, "x", 5)]
    team = [analyst("a1", {"x"}), analyst("a2", {"x"})]
    result = simulate(
        alerts, team, {"x": 1}, policy="B1", admission_horizon=3,
        coordination_latency=0.5,
    )
    assert {job.start for job in result.assignments} == {0.5}


def test_arrival_simultaneous_with_latency_end_is_added_before_next_dispatch():
    alerts = [Alert("first", 0, "x", 10), Alert("second", 1, "y", 10)]
    team = [analyst("a-x", {"x"}), analyst("b-y", {"y"})]
    result = simulate(
        alerts, team, {"x": 1, "y": 1}, policy="B1",
        admission_horizon=4, drain_period=2, coordination_latency=1,
    )
    starts = {job.alert_id: job.start for job in result.assignments}
    assert starts == {"first": 1, "second": 2}


def test_latency_runs_conserve_tasks_and_do_not_duplicate_reservations():
    alerts = [Alert(f"a{i}", 0, "x", 10) for i in range(7)]
    team = [analyst("a", {"x"}), analyst("b", {"x"})]
    first = simulate(
        alerts, team, {"x": 1}, policy="B2", admission_horizon=2,
        drain_period=8, coordination_latency=0.25, random_seed=3,
    )
    second = simulate(
        alerts, team, {"x": 1}, policy="B2", admission_horizon=2,
        drain_period=8, coordination_latency=0.25, random_seed=3,
    )
    assert first == second
    ids = [job.alert_id for job in first.assignments]
    assert len(ids) == len(set(ids))
    assert first.after_drain.admitted == (
        first.after_drain.completed_within_sla
        + first.after_drain.completed_late
        + first.after_drain.pending
    )


def test_latency_is_ignored_by_decentralized_policies():
    alerts = [Alert("a", 0, "x", 4)]
    team = [analyst("n", {"x"})]
    plain = simulate(alerts, team, {"x": 1}, policy="B0", admission_horizon=3)
    charged = simulate(
        alerts, team, {"x": 1}, policy="B0", admission_horizon=3,
        coordination_latency=2,
    )
    assert plain == charged


def test_b3_uses_only_current_state_and_selects_among_existing_dispatchers():
    alerts = [Alert("x", 0, "x", 0.5), Alert("y", 0, "y", 0.5)]
    team = [
        Analyst("a", frozenset({"x", "y"}), {"x": 0.95, "y": 0.2}),
        Analyst("b", frozenset({"x", "y"}), {"x": 0.2, "y": 0.95}),
    ]
    config = B3Config(0, 0, 0.2, 1)
    result = simulate(
        alerts, team, {"x": 1, "y": 1}, policy="B3",
        admission_horizon=2, b3_config=config,
    )
    assert dict(result.selected_strategy_counts) == {"B0": 0, "B1": 0, "B2": 1}
    # Adding a future alert cannot alter the first dispatch's observable choice.
    extended = simulate(
        [*alerts, Alert("future", 3, "x", 10)], team, {"x": 1, "y": 1},
        policy="B3", admission_horizon=2, b3_config=config,
    )
    assert extended.assignments[:2] == result.assignments


def test_b3_ablations_and_coordination_cost_are_explicit_and_reproducible():
    alerts = [Alert("x", 0, "x", 0.5), Alert("y", 0, "y", 0.5)]
    team = [
        Analyst("a", frozenset({"x", "y"}), {"x": 0.7, "y": 0.7}),
        Analyst("b", frozenset({"x", "y"}), {"x": 0.7, "y": 0.7}),
    ]
    config = B3Config(0, 0, 0.2, 1)
    first = simulate(
        alerts, team, {"x": 1, "y": 1}, policy="B3", admission_horizon=2,
        coordination_latency=0.25, b3_config=config,
    )
    second = simulate(
        alerts, team, {"x": 1, "y": 1}, policy="B3", admission_horizon=2,
        coordination_latency=0.25, b3_config=config,
    )
    assert first == second
    assert dict(first.selected_strategy_counts) == {"B0": 0, "B1": 1, "B2": 0}
    assert first.coordination_person_time == 0.5

    no_competence = simulate(
        alerts, team, {"x": 1, "y": 1}, policy="B3", admission_horizon=2,
        b3_config=B3Config(0, 0, 0, 1, use_competence_signal=False),
    )
    assert dict(no_competence.selected_strategy_counts)["B1"] == 1


def test_b3_load_gate_and_latency_cap_can_select_zero_cost_b0():
    alerts = [Alert("x", 0, "x", 0.5)]
    team = [analyst("a", {"x"})]
    config = B3Config(2, 0, 0, 0.1)
    result = simulate(
        alerts, team, {"x": 1}, policy="B3", admission_horizon=2,
        coordination_latency=0.5, b3_config=config,
    )
    assert dict(result.selected_strategy_counts)["B0"] == 1
    assert result.coordination_person_time == 0


def test_b3_tracks_deterministic_policy_switches_between_decisions():
    alerts = [Alert("ordinary", 0, "x", 10), Alert("urgent", 0.5, "y", 0.6)]
    team = [analyst("a-x", {"x"}), analyst("b-y", {"y"})]
    result = simulate(
        alerts, team, {"x": 1, "y": 1}, policy="B3", admission_horizon=2,
        b3_config=B3Config(1, 0.25, 0.2, 0.5),
    )
    assert dict(result.selected_strategy_counts) == {"B0": 1, "B1": 1, "B2": 0}
    assert result.strategy_switches == 1
