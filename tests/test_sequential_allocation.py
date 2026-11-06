from itertools import product
from fractions import Fraction
from math import isclose

import pytest

from hls.sequential_allocation import (
    FIXED_AGENT_EXHAUSTED,
    GLOBAL_CAPACITY_EXHAUSTED,
    OFFLINE_OPTIMAL_REJECTION,
    run_fixed_policy,
    run_greedy_online_policy,
    run_optimal_offline_policy,
)
from hls.static_assignment import StaticAllocationModel


def test_unrestricted_capacity_matches_crossed_static_allocation_controls():
    matrix = ((1.0, 0.2), (0.2, 1.0))
    tasks = (0, 1) * 5
    capacities = (10, 10)
    static = StaticAllocationModel(1.0, 0.2, 0.2, 1.0).evaluate(0.5)

    same_agent_1 = run_fixed_policy(tasks, matrix, capacities, (0, 0))
    taskwise = run_fixed_policy(tasks, matrix, capacities, (0, 1))
    same_agent_2 = run_fixed_policy(tasks, matrix, capacities, (1, 1))
    reversed_taskwise = run_fixed_policy(tasks, matrix, capacities, (1, 0))
    greedy = run_greedy_online_policy(tasks, matrix, capacities)

    assert isclose(same_agent_1.mean_effectiveness, static.policy_values["same_agent_1"])
    assert isclose(taskwise.mean_effectiveness, static.policy_values["agent_1_task_1__agent_2_task_2"])
    assert isclose(reversed_taskwise.mean_effectiveness, static.policy_values["agent_2_task_1__agent_1_task_2"])
    assert isclose(same_agent_2.mean_effectiveness, static.policy_values["same_agent_2"])
    assert isclose(greedy.mean_effectiveness, static.best_taskwise_effectiveness)
    assert isclose(greedy.mean_effectiveness, 1.0)
    assert isclose(static.best_same_agent_effectiveness, 0.6)


def test_unrestricted_capacity_matches_static_null_controls():
    homogeneous = ((0.7, 0.4), (0.7, 0.4))
    homogeneous_tasks = (0,) * 37 + (1,) * 63
    homogeneous_static = StaticAllocationModel(0.7, 0.4, 0.7, 0.4).evaluate(0.37)
    homogeneous_seq = run_greedy_online_policy(homogeneous_tasks, homogeneous, (100, 100))
    assert homogeneous_static.allocation_gain == 0.0
    assert isclose(homogeneous_seq.mean_effectiveness, 0.511)

    dominated = ((0.9, 0.8), (0.4, 0.2))
    dominated_tasks = (0,) * 4 + (1,) * 6
    dominated_static = StaticAllocationModel(0.9, 0.8, 0.4, 0.2).evaluate(0.4)
    dominated_seq = run_greedy_online_policy(dominated_tasks, dominated, (10, 10))
    assert dominated_static.allocation_gain == 0.0
    assert isclose(dominated_seq.mean_effectiveness, dominated_static.best_taskwise_effectiveness)


def test_online_greedy_can_be_suboptimal_under_capacity_constraints():
    tasks = (0, 1)
    matrix = ((1.0, 0.8), (0.9, 0.0))
    capacities = (1, 1)
    fixed = run_fixed_policy(tasks, matrix, capacities, (0, 1))
    greedy = run_greedy_online_policy(tasks, matrix, capacities)
    offline = run_optimal_offline_policy(tasks, matrix, capacities)

    assert isclose(fixed.total_effectiveness, 1.0)
    assert isclose(greedy.total_effectiveness, 1.0)
    assert isclose(offline.total_effectiveness, 1.7)
    assert isclose(offline.mean_effectiveness, 0.85)  # both received tasks are denominator
    assert offline.total_effectiveness >= fixed.total_effectiveness
    assert offline.total_effectiveness >= greedy.total_effectiveness
    assert tuple(d.agent_index for d in offline.decisions) == (1, 0)


def test_fixed_policy_rejection_is_distinguished_from_global_saturation():
    matrix = ((0.5, 0.5), (0.5, 0.5))
    induced = run_fixed_policy((0, 1), matrix, (1, 1), (0, 0))
    assert induced.decisions[0].agent_index == 0
    assert induced.decisions[1].agent_index is None
    assert induced.decisions[1].rejection_reason == FIXED_AGENT_EXHAUSTED
    assert induced.remaining_capacities == (0, 1)

    saturated = run_greedy_online_policy((0, 1), matrix, (1, 0))
    assert saturated.decisions[0].agent_index == 0
    assert saturated.decisions[1].agent_index is None
    assert saturated.decisions[1].rejection_reason == GLOBAL_CAPACITY_EXHAUSTED


def test_conservation_and_capacity_hold_for_all_policies():
    tasks = (0, 1, 0, 1, 0)
    matrix = ((0.8, 0.3), (0.6, 0.9))
    capacities = (1, 2)
    results = (
        run_fixed_policy(tasks, matrix, capacities, (0, 1)),
        run_greedy_online_policy(tasks, matrix, capacities),
        run_optimal_offline_policy(tasks, matrix, capacities),
    )
    for result in results:
        assert len(result.decisions) == len(tasks)
        assert result.assigned_count + result.rejected_count == len(tasks)
        assert result.remaining_capacities == tuple(
            initial - sum(d.agent_index == i for d in result.decisions)
            for i, initial in enumerate(capacities)
        )
        assert all(capacity >= 0 for capacity in result.remaining_capacities)
        assert isclose(result.total_effectiveness, sum(d.effectiveness for d in result.decisions))
        assert isclose(result.mean_effectiveness, result.total_effectiveness / len(tasks))


def test_greedy_prefix_decisions_do_not_depend_on_future_tasks():
    matrix = ((0.9, 0.2, 0.8), (0.5, 0.9, 0.4))
    capacities = (2, 2)
    prefix = (0, 1)
    first = run_greedy_online_policy(prefix + (2,), matrix, capacities)
    second = run_greedy_online_policy(prefix + (0, 0, 2), matrix, capacities)
    assert first.decisions[: len(prefix)] == second.decisions[: len(prefix)]


def test_greedy_ties_choose_the_lowest_agent_index():
    result = run_greedy_online_policy((0,), ((0.5,), (0.5,)), (1, 1))
    assert result.decisions[0].agent_index == 0


def test_offline_optimum_matches_independent_exhaustive_enumerator():
    tasks = (0, 1, 0)
    matrix = ((0.7, 0.2), (0.4, 0.9))
    capacities = (1, 1)
    observed = run_optimal_offline_policy(tasks, matrix, capacities)

    candidate_values = []
    for assignment in product((0, 1, None), repeat=len(tasks)):
        used = [assignment.count(agent) for agent in range(len(capacities))]
        if any(used[i] > capacities[i] for i in range(len(capacities))):
            continue
        candidate_values.append(sum(
            (Fraction(0) if agent is None else Fraction.from_float(float(matrix[agent][task_type]))
             for agent, task_type in zip(assignment, tasks)),
            Fraction(0),
        ))
    assert isclose(observed.total_effectiveness, max(candidate_values))


def test_offline_tie_break_is_deterministic_and_documented():
    result = run_optimal_offline_policy((0,), ((0.5,), (0.5,)), (1, 1))
    assert result.decisions[0].agent_index == 0


def test_offline_oracle_can_reject_now_to_reserve_capacity_for_a_better_future_task():
    result = run_optimal_offline_policy((0, 1), ((0.0, 1.0),), (1,))
    assert result.decisions[0].agent_index is None
    assert result.decisions[0].rejection_reason == OFFLINE_OPTIMAL_REJECTION
    assert result.decisions[1].agent_index == 0
    assert result.total_effectiveness == 1.0


@pytest.mark.parametrize(
    "args",
    [
        ((), ((0.5,),), (1,)),
        ((0,), (), (1,)),
        ((0,), ((0.5,),), (-1,)),
        ((0,), ((0.5,),), (1, 1)),
        ((1,), ((0.5,),), (1,)),
        ((False,), ((0.5,),), (1,)),
        ((0,), ((float("nan"),),), (1,)),
        ((0,), ((1.01,),), (1,)),
        ((0,), ((0.5,), (0.4, 0.3)), (1, 1)),
    ],
)
def test_invalid_problem_inputs_are_rejected(args):
    with pytest.raises(ValueError):
        run_greedy_online_policy(*args)


def test_invalid_fixed_mapping_is_rejected():
    with pytest.raises(ValueError):
        run_fixed_policy((0,), ((0.5,),), (1,), (1,))
    with pytest.raises(ValueError):
        run_fixed_policy((0,), ((0.5,),), (1,), (False,))


def test_all_policies_are_exactly_reproducible():
    inputs = ((0, 1, 0), ((0.6, 0.2), (0.4, 0.9)), (1, 2))
    assert run_fixed_policy(*inputs, (0, 1)) == run_fixed_policy(*inputs, (0, 1))
    assert run_greedy_online_policy(*inputs) == run_greedy_online_policy(*inputs)
    assert run_optimal_offline_policy(*inputs) == run_optimal_offline_policy(*inputs)
