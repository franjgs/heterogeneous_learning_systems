from dataclasses import replace

import pytest

from experiments.run_hls_s7_uncertain_demand import make_case
from experiments.run_hls_s7_preparation_characterization import make_characterization_case
from hls.synthetic.hls_s7_uncertain_demand import (
    independent_tree_enumeration,
    replay_markov_policy,
    solve_markov_bellman,
    solve_reactive_greedy,
)
from hls.synthetic.hls_s4_transfer_exact import _step, action_catalogs


@pytest.mark.parametrize("transfer", [False, True])
def test_markov_bellman_matches_independent_exhaustive_contingent_tree(transfer):
    case = make_case(2)
    exact = solve_markov_bellman(case, transfer_available=transfer)
    enumerated = independent_tree_enumeration(case, transfer_available=transfer)
    assert exact.value == pytest.approx(enumerated, abs=1e-10)


def test_optional_transfer_cannot_reduce_exact_expected_value():
    case = make_case(3)
    without = solve_markov_bellman(case, transfer_available=False)
    with_optional = solve_markov_bellman(case, transfer_available=True)
    assert with_optional.value >= without.value - 1e-10


def test_exact_stochastic_planning_is_not_worse_than_immediate_reactive_rule():
    case = make_case(3)
    for transfer in (False, True):
        planned = solve_markov_bellman(case, transfer_available=transfer)
        reactive = solve_reactive_greedy(case, transfer_available=transfer)
        assert planned.value >= reactive.value - 1e-10


def test_replay_uses_current_observed_demand_and_reconstructs_state():
    case = make_case(3)
    policy = solve_markov_bellman(case, transfer_available=True)
    path = (0, 1, 1)
    rows = replay_markov_policy(case, policy, path)
    assert tuple(row["problem_id"] for row in rows) == tuple(
        case.demand_states[index].problem_id for index in path
    )
    assert rows[0]["competence_after"] == rows[1]["competence_before"]
    assert rows[1]["competence_after"] == rows[2]["competence_before"]
    assert all(row["reward"] >= 0.0 for row in rows)


def test_stochastic_case_rejects_invalid_probability_rows():
    case = make_case(2)
    with pytest.raises(ValueError, match="sum to one"):
        replace(case, transition_probabilities=((0.9, 0.2), (0.1, 0.9)))


def test_markov_case_rejects_bad_horizon():
    case = make_case(2)
    with pytest.raises(ValueError, match="horizon"):
        replace(case, horizon=0)


def test_s7_preparation_opportunity_changes_decision_and_collective_value():
    case = make_characterization_case("opportunity")
    bellman_a = solve_markov_bellman(case, transfer_available=False)
    bellman_b = solve_markov_bellman(case, transfer_available=True)
    myopic_b = solve_reactive_greedy(case, transfer_available=True)

    assert bellman_b.value == pytest.approx(3.1743777327025406, abs=1e-10)
    assert bellman_a.value == pytest.approx(3.1628653621, abs=1e-10)
    assert myopic_b.value == pytest.approx(3.0346209871, abs=1e-10)
    assert bellman_b.value > bellman_a.value > myopic_b.value

    initial = case.physical_case.organization.competence_initial
    planned_action = bellman_b.actions_by_state[(0, initial, 0)]
    myopic_action = myopic_b.actions_by_state[(0, initial, 0)]
    assert planned_action.teaching is not None
    assert (planned_action.teaching.teacher_id,
            planned_action.teaching.learner_id,
            planned_action.teaching.skill_id) == ("A", "B", "y")
    assert myopic_action.teaching is None

    problem_x = case.demand_states[0]
    _, prepared = _step(case.physical_case, initial, problem_x, planned_action)
    _, unprepared = _step(
        case.physical_case, initial, problem_x,
        replace(planned_action, teaching=None),
    )
    assert prepared[1][1] == pytest.approx(0.08)
    assert unprepared[1][1] == pytest.approx(0.0)

    prepared_trace = replay_markov_policy(case, bellman_b, (0, 1, 1, 1))
    unprepared_trace = replay_markov_policy(case, bellman_a, (0, 1, 1, 1))
    assert prepared_trace[1]["reward"] == pytest.approx(0.98)
    assert unprepared_trace[1]["reward"] == pytest.approx(0.9)


def test_s7_preparation_controls_separate_short_horizon_and_no_future_need():
    short = make_characterization_case("short_horizon")
    short_a = solve_markov_bellman(short, transfer_available=False)
    short_b = solve_markov_bellman(short, transfer_available=True)
    short_m = solve_reactive_greedy(short, transfer_available=True)
    short_initial = short.physical_case.organization.competence_initial
    assert short_b.value == pytest.approx(short_a.value, abs=1e-10)
    assert short_b.actions_by_state[(0, short_initial, 0)].teaching is None
    assert short_m.actions_by_state[(0, short_initial, 0)].teaching is None
    # A lesson is physically feasible and changes B/y, but the short horizon
    # cannot recover its immediate production cost.
    feasible = action_catalogs(
        replace(short.physical_case,
                problems=(short.demand_states[0],) * short.horizon),
        transfer_available=True,
    )[0]
    assert any(action.teaching is not None for action in feasible)

    no_need = make_characterization_case("no_future_need")
    no_need_a = solve_markov_bellman(no_need, transfer_available=False)
    no_need_b = solve_markov_bellman(no_need, transfer_available=True)
    no_need_m = solve_reactive_greedy(no_need, transfer_available=True)
    assert no_need_b.value == pytest.approx(no_need_a.value, abs=1e-10)
    assert no_need_b.value == pytest.approx(no_need_m.value, abs=1e-10)
    assert no_need_b.actions_by_state[
        (0, no_need.physical_case.organization.competence_initial, 0)
    ].teaching is None


@pytest.mark.parametrize("transfer", [False, True])
def test_s7_characterization_small_horizon_matches_independent_tree_and_pruning(transfer):
    case = replace(make_characterization_case("opportunity"), horizon=2)
    exact = solve_markov_bellman(case, transfer_available=transfer)
    unpruned = solve_markov_bellman(
        case, transfer_available=transfer, prune_dominated=False,
    )
    enumerated = independent_tree_enumeration(case, transfer_available=transfer)
    assert exact.value == pytest.approx(unpruned.value, abs=1e-10)
    assert exact.value == pytest.approx(enumerated, abs=1e-10)
