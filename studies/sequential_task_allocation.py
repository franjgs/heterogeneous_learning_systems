"""Run deterministic controls for the finite sequential allocation study."""
from __future__ import annotations

import json
from math import isclose

from hls.sequential_allocation import (
    run_fixed_policy,
    run_greedy_online_policy,
    run_optimal_offline_policy,
)
from hls.static_assignment import StaticAllocationModel


def _summary(result) -> dict[str, object]:
    return {
        "policy": result.policy,
        "total_effectiveness": result.total_effectiveness,
        "mean_over_received_tasks": result.mean_effectiveness,
        "assigned": result.assigned_count,
        "rejected": result.rejected_count,
        "rejection_causes": result.rejection_counts,
        "agent_sequence": [decision.agent_index for decision in result.decisions],
        "remaining_capacities": result.remaining_capacities,
    }


def run() -> dict[str, object]:
    """Execute small exact controls; this is not a stochastic campaign."""
    crossed_matrix = ((1.0, 0.2), (0.2, 1.0))
    crossed_tasks = (0, 1) * 5
    crossed_capacities = (10, 10)
    crossed_static = StaticAllocationModel(1.0, 0.2, 0.2, 1.0).evaluate(0.5)
    crossed_mappings = {
        "same_agent_1": (0, 0),
        "agent_1_task_1__agent_2_task_2": (0, 1),
        "agent_2_task_1__agent_1_task_2": (1, 0),
        "same_agent_2": (1, 1),
    }
    crossed_values = {
        name: run_fixed_policy(crossed_tasks, crossed_matrix, crossed_capacities, mapping).mean_effectiveness
        for name, mapping in crossed_mappings.items()
    }
    assert all(isclose(crossed_values[name], value) for name, value in crossed_static.policy_values.items())
    crossed_greedy = run_greedy_online_policy(crossed_tasks, crossed_matrix, crossed_capacities)
    assert isclose(crossed_greedy.mean_effectiveness, crossed_static.best_taskwise_effectiveness)

    homogeneous_model = StaticAllocationModel(0.7, 0.4, 0.7, 0.4)
    homogeneous_tasks = (0,) * 37 + (1,) * 63
    homogeneous_result = run_greedy_online_policy(
        homogeneous_tasks, ((0.7, 0.4), (0.7, 0.4)), (100, 100)
    )
    homogeneous_static = homogeneous_model.evaluate(0.37)
    assert homogeneous_static.allocation_gain == 0.0
    assert isclose(homogeneous_result.mean_effectiveness, homogeneous_static.best_taskwise_effectiveness)

    dominance_model = StaticAllocationModel(0.9, 0.8, 0.4, 0.2)
    dominance_tasks = (0,) * 4 + (1,) * 6
    dominance_result = run_greedy_online_policy(
        dominance_tasks, ((0.9, 0.8), (0.4, 0.2)), (10, 10)
    )
    dominance_static = dominance_model.evaluate(0.4)
    assert dominance_static.allocation_gain == 0.0
    assert isclose(dominance_result.mean_effectiveness, dominance_static.best_taskwise_effectiveness)

    limited_tasks = (0, 1)
    limited_matrix = ((1.0, 0.8), (0.9, 0.0))
    limited_capacities = (1, 1)
    limited = {
        "fixed": _summary(run_fixed_policy(limited_tasks, limited_matrix, limited_capacities, (0, 1))),
        "greedy_online": _summary(run_greedy_online_policy(limited_tasks, limited_matrix, limited_capacities)),
        "optimal_offline": _summary(run_optimal_offline_policy(limited_tasks, limited_matrix, limited_capacities)),
    }
    assert isclose(limited["optimal_offline"]["total_effectiveness"], 1.7)
    assert limited["optimal_offline"]["total_effectiveness"] >= limited["greedy_online"]["total_effectiveness"]

    policy_rejection = run_fixed_policy(
        (0, 1), ((0.5, 0.5), (0.5, 0.5)), (1, 1), (0, 0)
    )
    global_saturation = run_greedy_online_policy(
        (0, 1), ((0.5, 0.5), (0.5, 0.5)), (1, 0)
    )
    assert policy_rejection.rejection_counts == {"fixed_agent_exhausted": 1}
    assert global_saturation.rejection_counts == {"global_capacity_exhausted": 1}

    return {
        "study": "sequential-deterministic-task-allocation-under-finite-capacity",
        "interpretation": "deterministic benchmark controls; not empirical evidence or a CE-04 reproduction",
        "static_compatibility": {
            "crossed_specialization": {
                "static_policy_values": crossed_static.policy_values,
                "sequential_fixed_mapping_values": crossed_values,
                "best_same_agent": crossed_static.best_same_agent_effectiveness,
                "best_taskwise": crossed_static.best_taskwise_effectiveness,
                "greedy_online": crossed_greedy.mean_effectiveness,
            },
            "homogeneous_null": {
                "static_gain": homogeneous_static.allocation_gain,
                "sequential_greedy_mean": homogeneous_result.mean_effectiveness,
            },
            "taskwise_dominance_null": {
                "static_gain": dominance_static.allocation_gain,
                "sequential_greedy_mean": dominance_result.mean_effectiveness,
            },
        },
        "capacity_limited_greedy_suboptimality": limited,
        "rejection_causes": {
            "fixed_policy_while_other_agent_has_capacity": _summary(policy_rejection),
            "global_capacity_exhaustion": _summary(global_saturation),
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
