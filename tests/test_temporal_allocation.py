from math import isclose

import pytest

from hls.sequential_allocation import run_fixed_policy, run_greedy_online_policy
from hls.static_assignment import StaticAllocationModel
from hls.temporal_allocation import (
    run_effectiveness_load_temporal_policy,
    run_fixed_temporal_policy,
    run_max_effectiveness_temporal_policy,
)
from studies.temporal_task_allocation import (
    SENSITIVITY_AGENT_COUNTS,
    SENSITIVITY_DEMANDS,
    SENSITIVITY_EFFECTIVENESS,
    SENSITIVITY_HORIZONS,
    SENSITIVITY_SERVICE_TIMES,
    SENSITIVITY_TASK_COUNT,
    _fixed_mapping_variants,
    _peak_window_load,
    _sensitivity_arrivals,
    _sensitivity_matrix,
    run_sensitivity,
    scenarios,
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
    assert result.pending_task_count_by_agent == (1,)
    assert result.pending_task_count == 1
    assert result.pending_work_at_horizon_by_agent == (0.5,)
    assert result.utilization_by_agent == (1.0,)
    assert result.makespan == 2.0


def test_pending_count_is_integer_and_work_includes_active_residual_and_queued_jobs():
    result = run_max_effectiveness_temporal_policy(
        tuple((0.0, 0) for _ in range(4)), ((1.0,),), (1.0,), 1.5
    )
    assert result.pending_task_count_by_agent == (3,)
    assert isinstance(result.pending_task_count, int)
    assert result.pending_task_count == 3
    # One active task has 0.5 time left; two tasks are waiting, each 1.0.
    assert result.pending_work_at_horizon_by_agent == (2.5,)
    assert result.pending_work_at_horizon == 2.5


def test_pending_metrics_are_measured_at_horizon_and_exclude_jobs_completed_at_horizon():
    result = run_max_effectiveness_temporal_policy(
        ((0.0, 0),), ((1.0,),), (1.0,), 1.0
    )
    assert result.decisions[0].completion_time == 1.0
    assert result.pending_task_count == 0
    assert result.pending_work_at_horizon == 0.0


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


def test_sensitivity_profiles_have_declared_marginals_and_dominance_control():
    for profile in tuple(SENSITIVITY_EFFECTIVENESS)[:3]:
        for n_agents in SENSITIVITY_AGENT_COUNTS:
            matrix = _sensitivity_matrix(profile, n_agents)
            assert all(isclose(sum(row[k] for row in matrix) / n_agents, 0.6) for k in range(2))
    dominant = _sensitivity_matrix("H3_agent_dominance", 4)
    assert all(dominant[0][k] > dominant[i][k] for i in range(1, 4) for k in range(2))
    assert tuple(max(row[k] for row in dominant) for k in range(2)) == (0.9, 0.8)


def test_sensitivity_demand_traces_preserve_task_volume_and_encode_declared_shapes():
    horizon = 48.0
    traces = {profile: _sensitivity_arrivals(profile, horizon) for profile in SENSITIVITY_DEMANDS}
    assert all(len(trace) == SENSITIVITY_TASK_COUNT for trace in traces.values())
    assert all(sum(service[k] for _, k in trace) == 48.0 for trace in traces.values() for service in (SENSITIVITY_SERVICE_TIMES,))
    for profile in ("D0_distributed", "D1_balanced_bursts", "D3_mixture_shift"):
        assert sum(k == 0 for _, k in traces[profile]) == 24
        assert sum(k == 1 for _, k in traces[profile]) == 24
    assert all(k == 0 for _, k in traces["D2_class_concentrated_bursts"])
    assert _peak_window_load(traces["D1_balanced_bursts"], horizon, 2) > _peak_window_load(traces["D0_distributed"], horizon, 2)
    assert _sensitivity_arrivals("D3_mixture_shift", horizon)[23][1] == 0
    assert _sensitivity_arrivals("D3_mixture_shift", horizon)[24][1] == 1


def test_fixed_sensitivity_mappings_are_predeclared_and_nominal_mix_is_explicit():
    matrix = _sensitivity_matrix("H2_marked_specialization", 4)
    mappings = _fixed_mapping_variants("H2_marked_specialization", matrix)
    assert mappings["P0_class_responsibility"] == (0, 1)
    assert mappings["P0_fixed_duty_roster"] == (0, 1)
    assert mappings["P0_nominal_mix_owner_75_25"] == (0, 0)


def test_original_six_p0_p1_matches_remain_deliberate_controls():
    for scenario in scenarios():
        fixed = run_fixed_temporal_policy(
            scenario.arrivals, scenario.effectiveness, scenario.service_times,
            scenario.horizon, scenario.type_to_agent,
        )
        p1 = run_max_effectiveness_temporal_policy(
            scenario.arrivals, scenario.effectiveness,
            scenario.service_times, scenario.horizon,
        )
        assert tuple(d.agent_index for d in fixed.decisions) == tuple(
            d.agent_index for d in p1.decisions
        )


def test_sensitivity_grid_pairs_all_policies_and_repeats_exactly():
    first = run_sensitivity()
    second = run_sensitivity()
    assert first == second
    assert first["cells"] == 4 * 4 * 2 * len(SENSITIVITY_HORIZONS) == 96
    contrasts = first["contrasts"]
    assert sum(row["contrast"] == "P2-P1" for row in contrasts) == 96
    for baseline in (
        "P0_class_responsibility",
        "P0_fixed_duty_roster",
        "P0_nominal_mix_owner_75_25",
    ):
        assert sum(row["contrast"] == f"P1-{baseline}" for row in contrasts) == 96
        assert sum(row["contrast"] == f"P2-{baseline}" for row in contrasts) == 96
    for row in contrasts:
        if row["contrast"] == "P2-P1":
            assert row["delta_effectiveness_mean"] <= 1e-12
    rows = first["policy_rows"]
    assert all(row["pending_tasks"] >= 0 and row["pending_work"] >= 0 for row in rows)
    assert all(0 <= value <= 1 for row in rows for value in row["utilization"])
    assert all(sum(row["assigned_count_by_agent"]) == SENSITIVITY_TASK_COUNT for row in rows)
    assert all(isclose(sum(row["effectiveness_by_agent"]), row["effectiveness_total"]) for row in rows)
