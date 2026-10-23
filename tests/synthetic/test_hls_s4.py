from math import isclose

from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.synthetic.hls_s4 import (
    _assignment_catalog,
    _bellman,
    _exhaustive,
    _reactive,
    canonical_cases,
    evaluate_case,
    investment_family,
    validate_case,
)


def test_s4_mis_v2_updates_only_executed_agent_task_cells():
    state = ((0.525, 0.175), (0.525, 0.175))
    profile = LearningProfileNK(((0.15, 0.15), (0.25, 0.25)))
    after = mis_v2_transition_nk(state, ((0.0, 0.0), (1.0, 0.0)), profile)
    assert after[0] == state[0]
    assert after[1][1] == state[1][1]
    assert after[1][0] == 0.64375


def test_s4_reactive_is_exactly_immediate_optimal_and_feasible():
    case = canonical_cases()[1]
    result = _reactive(case)
    for period, row in enumerate(result.periods):
        feasible = _assignment_catalog(case.demands[period], len(case.initial))
        assert row.assignment in feasible
        assert row.reward == sum(row.competence_before[i][k] for i, k in row.assignment)
        assert row.reward == max(
            sum(row.competence_before[i][k] for i, k in assignment)
            for assignment in feasible
        )


def test_s4_bellman_equals_independent_sequence_enumeration():
    for case in canonical_cases():
        bellman_value, _ = _bellman(case)
        exhaustive_value, _ = _exhaustive(case)
        assert abs(bellman_value - exhaustive_value) < 1e-12


def test_s4_case_a_has_no_planning_gap_and_case_b_has_exact_gap():
    case_a, case_b = (evaluate_case(case) for case in canonical_cases())
    assert case_a.reactive.reward == case_a.bellman.reward == case_a.exhaustive.reward == 0.7
    assert case_b.bellman.reward > case_b.reactive.reward
    assert abs(case_b.bellman.reward - case_b.exhaustive.reward) < 1e-12
    assert abs((case_b.bellman.reward - case_b.reactive.reward) - 0.2148187500000005) < 1e-12
    # Both actions at t=0 are immediate maximizers; the continuation-aware
    # policy changes the tie resolution, not current-period reward.
    assert case_b.bellman.periods[0].reward == case_b.reactive.periods[0].reward


def test_s4_case_b_contains_lower_immediate_action_with_useful_exposure():
    case = canonical_cases()[1]
    profile = LearningProfileNK(case.eta)
    # At t=0, sending only agent 1 to task 0 yields .525 rather than .700,
    # but develops that cell for the three future task-0 periods.
    state_after = mis_v2_transition_nk(
        case.initial, ((0.0, 0.0), (1.0, 0.0)), profile,
    )
    assert case.initial[1][0] < sum(case.initial[i][k] for i, k in ((0, 0), (1, 1)))
    assert state_after[1][0] == 0.64375
    assert state_after[1][0] > case.initial[0][0]


def test_s4_is_deterministic_and_exposure_matches_executed_assignments():
    case = canonical_cases()[1]
    first, second = evaluate_case(case), evaluate_case(case)
    for policy_name in ("reactive", "bellman", "exhaustive"):
        a, b = getattr(first, policy_name), getattr(second, policy_name)
        assert a.reward == b.reward
        assert tuple(row.assignment for row in a.periods) == tuple(row.assignment for row in b.periods)
        assert tuple(row.competence_after for row in a.periods) == tuple(row.competence_after for row in b.periods)
        for row in a.periods:
            assert sum(sum(values) for values in row.cumulative_exposure) == sum(
                len(previous.assignment) for previous in a.periods[:row.period + 1]
            )
            assert len({agent for agent, _ in row.assignment}) == len(row.assignment)
            assert len({task for _, task in row.assignment}) == len(row.assignment)


def test_s4_original_case_b_gap_disappears_against_best_myopic():
    report = validate_case(canonical_cases()[1])
    assert abs(report.bellman.reward - report.best_myopic.reward) < 1e-12
    assert isclose(report.best_myopic.reward, 2.876171875, abs_tol=1e-12)
    assert report.bellman.reward > report.reactive.reward
    assert report.bellman_strictly_suboptimal_periods == ()
    assert report.tie_counts == (2, 1, 1, 1)
    assert report.exhaustive_best_myopic_value == report.best_myopic.reward


def test_s4_investment_horizon_family_has_strict_planning_gap():
    reports = tuple(validate_case(case) for case in investment_family())
    assert all(isclose(actual, expected, abs_tol=1e-12) for actual, expected in zip(
        (report.best_myopic.reward for report in reports),
        (0.525, 1.12125, 1.7780625, 2.486353125),
    ))
    assert all(isclose(actual, expected, abs_tol=1e-12) for actual, expected in zip(
        (report.bellman.reward for report in reports),
        (0.525, 1.125, 1.84375, 2.6328125),
    ))
    assert reports[0].bellman.reward == reports[0].best_myopic.reward
    for report in reports[1:]:
        assert report.bellman.reward > report.best_myopic.reward
        assert report.bellman.reward == report.exhaustive.reward
        assert report.best_myopic.reward == report.exhaustive_best_myopic_value
        assert report.bellman_strictly_suboptimal_periods == (0,)
        assert report.bellman.periods[0].reward < report.reactive.periods[0].reward


def test_s4_frozen_competence_removes_strict_advantage():
    case = investment_family()[-1]
    report = validate_case(case, learning_enabled=False)
    assert report.reactive.reward == report.best_myopic.reward == report.bellman.reward
    assert report.bellman.reward == report.exhaustive.reward
    assert report.bellman_strictly_suboptimal_periods == ()


def test_s4_best_myopic_never_selects_strictly_suboptimal_action():
    for case in (canonical_cases()[1], *investment_family()):
        report = validate_case(case)
        for period, row in enumerate(report.best_myopic.periods):
            actions = _assignment_catalog(case.demands[period], len(case.initial))
            maximum = max(sum(row.competence_before[i][k] for i, k in action)
                          for action in actions)
            assert row.reward >= maximum - 1e-12
