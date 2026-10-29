from math import isclose

import pytest

from hls.sequential_allocation import run_fixed_policy, run_greedy_online_policy
from hls.static_assignment import StaticAllocationModel
from hls.temporal_allocation import (
    run_effectiveness_load_temporal_policy,
    run_fixed_temporal_policy,
    run_max_effectiveness_temporal_policy,
)


def test_temporal_runner_recovers_static_crossed_specialization_control():
    arrivals = tuple((float(index), task_type) for index, task_type in enumerate((0, 1) * 5))
    matrix = ((1.0, 0.2), (0.2, 1.0))
    static = StaticAllocationModel(1.0, 0.2, 0.2, 1.0).evaluate(0.5)
    temporal_fixed = run_fixed_temporal_policy(arrivals, matrix, (1.0, 1.0), 10.0, (0, 1))
    temporal_best = run_max_effectiveness_temporal_policy(arrivals, matrix, (1.0, 1.0), 10.0)
    sequential_fixed = run_fixed_policy((0, 1) * 5, matrix, (10, 10), (0, 1))
    sequential_greedy = run_greedy_online_policy((0, 1) * 5, matrix, (10, 10))

    assert isclose(temporal_fixed.mean_effectiveness, static.policy_values["agent_1_task_1__agent_2_task_2"])
    assert isclose(temporal_best.mean_effectiveness, sequential_greedy.mean_effectiveness)
    assert isclose(temporal_fixed.mean_effectiveness, sequential_fixed.mean_effectiveness)


def test_fcfs_single_server_capacity_recovers_on_completion_and_metrics_are_well_defined():
    result = run_max_effectiveness_temporal_policy(
        ((0.0, 0), (0.5, 0)), ((0.8,),), (1.0,), 1.5
    )
    first, second = result.decisions
    assert first.service_start == 0.0
    assert first.completion_time == 1.0
    assert second.workload_at_decision == 0.5
    assert second.service_start == 1.0
    assert second.completion_time == 2.0
    assert result.mean_waiting_time == 0.25
    assert result.p95_waiting_time == 0.5
    assert result.mean_response_time == 1.25
    assert result.p95_response_time == 1.5
    assert result.pending_work_at_horizon_by_agent == (0.5,)
    assert result.utilization_by_agent == (1.0,)
    assert result.makespan == 2.0


def test_fcfs_preserves_arrival_order_within_each_agent_queue():
    result = run_fixed_temporal_policy(
        ((0.0, 0), (0.1, 1), (0.2, 0)), ((0.5, 0.5),), (1.0, 2.0), 1.0, (0, 0)
    )
    assert [d.task_index for d in result.decisions] == [0, 1, 2]
    assert [d.service_start for d in result.decisions] == [0.0, 1.0, 3.0]
    assert [d.completion_time for d in result.decisions] == [1.0, 3.0, 4.0]


def test_p1_maximizes_total_effectiveness_when_all_tasks_complete():
    arrivals = ((0.0, 0), (0.0, 1), (0.1, 0), (0.1, 1))
    matrix = ((0.95, 0.3), (0.4, 0.85), (0.6, 0.55))
    p1 = run_max_effectiveness_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0)
    p2 = run_effectiveness_load_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0)
    taskwise_upper_bound = sum(max(row[k] for row in matrix) for _, k in arrivals)
    assert isclose(p1.total_effectiveness, taskwise_upper_bound)
    assert p1.total_effectiveness >= p2.total_effectiveness
    assert isclose(sum(p1.effectiveness_by_agent), p1.total_effectiveness)
    assert sum(p1.assigned_count_by_agent) == len(arrivals)
    assert all(
        (value is None) == (count == 0)
        for value, count in zip(p1.mean_effectiveness_by_agent, p1.assigned_count_by_agent)
    )


def test_p2_can_trade_effectiveness_for_lower_response_under_concentrated_burst():
    arrivals = tuple((0.0, 0) for _ in range(12))
    matrix = ((1.0, 0.2), (0.2, 1.0))
    p1 = run_max_effectiveness_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0)
    p2 = run_effectiveness_load_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0)
    assert p2.mean_response_time < p1.mean_response_time
    assert p2.total_effectiveness < p1.total_effectiveness


def test_homogeneity_and_dominance_can_make_fixed_and_p1_coincide():
    arrivals = ((0.0, 0), (0.0, 1), (0.1, 0), (0.1, 1))
    homogeneous = ((0.7, 0.4), (0.7, 0.4))
    p0_h = run_fixed_temporal_policy(arrivals, homogeneous, (1.0, 1.0), 1.0, (0, 0))
    p1_h = run_max_effectiveness_temporal_policy(arrivals, homogeneous, (1.0, 1.0), 1.0)
    assert tuple(d.agent_index for d in p0_h.decisions) == tuple(d.agent_index for d in p1_h.decisions)

    dominant = ((0.9, 0.8), (0.4, 0.2))
    p0_d = run_fixed_temporal_policy(arrivals, dominant, (1.0, 1.0), 1.0, (0, 0))
    p1_d = run_max_effectiveness_temporal_policy(arrivals, dominant, (1.0, 1.0), 1.0)
    assert tuple(d.agent_index for d in p0_d.decisions) == tuple(d.agent_index for d in p1_d.decisions)


def test_online_decisions_are_prefix_invariant_and_deterministic():
    matrix, service = ((0.9, 0.2), (0.2, 0.9)), (1.0, 1.0)
    prefix = ((0.0, 0), (0.0, 1), (0.2, 0))
    extension_a = prefix + ((0.3, 1),)
    extension_b = prefix + ((0.7, 0), (0.9, 1))
    for runner in (run_max_effectiveness_temporal_policy, run_effectiveness_load_temporal_policy):
        left = runner(extension_a, matrix, service, 2.0)
        right = runner(extension_b, matrix, service, 2.0)
        assert left.decisions[: len(prefix)] == right.decisions[: len(prefix)]
        assert left == runner(extension_a, matrix, service, 2.0)


def test_tie_breaking_is_lowest_agent_index_for_all_policies():
    arrivals = ((0.0, 0), (0.0, 1))
    matrix = ((0.5, 0.5), (0.5, 0.25))
    fixed = run_fixed_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0, (0, 0))
    p1 = run_max_effectiveness_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0)
    p2 = run_effectiveness_load_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0)
    assert tuple(x.agent_index for x in fixed.decisions) == (0, 0)
    assert tuple(x.agent_index for x in p1.decisions) == (0, 0)
    assert tuple(x.agent_index for x in p2.decisions) == (0, 0)


def test_tasks_are_conserved_and_every_task_completes_exactly_once():
    arrivals = ((0.0, 0), (0.1, 1), (0.2, 0), (0.3, 1))
    matrix = ((0.9, 0.2), (0.2, 0.9))
    for result in (
        run_fixed_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0, (0, 1)),
        run_max_effectiveness_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0),
        run_effectiveness_load_temporal_policy(arrivals, matrix, (1.0, 1.0), 1.0),
    ):
        assert len(result.decisions) == len(arrivals)
        assert [d.task_index for d in result.decisions] == list(range(len(arrivals)))
        assert all(d.completion_time >= d.service_start >= d.arrival_time for d in result.decisions)
        assert len({d.task_index for d in result.decisions}) == len(arrivals)


@pytest.mark.parametrize(
    "arrivals,matrix,service,horizon,mapping",
    [
        ((), ((0.5,),), (1.0,), 1.0, (0,)),
        (((0.0, 0),), (), (1.0,), 1.0, (0,)),
        (((0.0, 0),), ((0.5,), (0.4, 0.3)), (1.0,), 1.0, (0,)),
        (((0.0, 0),), ((0.5,),), (0.0,), 1.0, (0,)),
        (((1.0, 0),), ((0.5,),), (1.0,), 1.0, (0,)),
        (((0.2, 0), (0.1, 0)), ((0.5,),), (1.0,), 1.0, (0,)),
        (((0.0, 1),), ((0.5,),), (1.0,), 1.0, (0,)),
        (((0.0, 0),), ((0.5,),), (1.0,), 1.0, (1,)),
        (((0.0, 0),), ((float("nan"),),), (1.0,), 1.0, (0,)),
    ],
)
def test_invalid_temporal_inputs_are_rejected(arrivals, matrix, service, horizon, mapping):
    with pytest.raises(ValueError):
        run_fixed_temporal_policy(arrivals, matrix, service, horizon, mapping)


def test_load_policy_uses_current_work_only_and_service_recovery():
    arrivals = ((0.0, 0), (0.0, 0), (2.0, 0))
    result = run_effectiveness_load_temporal_policy(arrivals, ((1.0,), (0.9,)), (1.0,), 3.0)
    assert result.decisions[0].agent_index == 0
    assert result.decisions[1].agent_index == 1
    assert result.decisions[2].workload_at_decision == 0.0
    assert result.decisions[2].agent_index == 0
