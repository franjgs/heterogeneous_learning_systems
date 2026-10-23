from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments.run_hls_hungarian_assignment import greedy_assignment, run_episode
from experiments.run_hls_s2a_static_demand import run_s2a
from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK


def _instance(n=3, k=3, budget=3.0, limits=None):
    return (
        OrganizationConfigNK(
            tuple(f"a{i}" for i in range(n)),
            tuple(f"t{j}" for j in range(k)),
            tuple(tuple(0.5 for _ in range(k)) for _ in range(n)),
            tuple(limits or (1.0,) * n), budget,
        ),
        ProblemSpecNK("simultaneous", (1.0,) * k, budget),
    )


def _enumerate_matchings(values, budget, limits):
    n, k = len(values), len(values[0])
    edge_list = [(i, j) for i in range(n) for j in range(k) if limits[i] >= 1.0]
    feasible = []
    for count in range(min(n, k, math.floor(budget + 1e-12)) + 1):
        for edges in itertools.combinations(edge_list, count):
            if len({i for i, _ in edges}) == count and len({j for _, j in edges}) == count:
                feasible.append((sum(values[i][j] for i, j in edges), tuple(sorted(edges))))
    return feasible


def test_solver_matches_exhaustive_enumeration_on_small_rectangular_cases():
    optimizer = HungarianAssignmentOptimizerNK()
    cases = (
        ([[10, 9, 0], [9, 0, 0], [0, 8, 8]], 3.0, (1, 1, 1)),
        ([[3, 8, 2], [9, 1, 4]], 2.0, (1, 1)),
        ([[2, 6], [7, 3], [5, 4]], 1.7, (1, 1, 1)),
        ([[-3, -1], [-2, -4]], 2.0, (1, 1)),
        ([[4, 100], [7, 9]], 2.0, (0.5, 1.0)),
    )
    for values, budget, limits in cases:
        org, problem = _instance(len(values), len(values[0]), budget, limits)
        result = optimizer.optimize(values, org, problem)
        exhaustive = _enumerate_matchings(values, budget, limits)
        expected_value = max(value for value, _ in exhaustive)
        assert result.objective_value == pytest.approx(expected_value)
        assert len(result.matches) == len({i for i, _ in result.matches})
        assert len(result.matches) == len({j for _, j in result.matches})
        assert result.resource_used <= budget + 1e-12
        assert all(limits[i] >= 1 for i, _ in result.matches)


def test_joint_solver_beats_greedy_counterexample_and_matches_hls_action_contract():
    values = ((10, 9, 0), (9, 0, 0), (0, 8, 8))
    org, problem = _instance()
    result = HungarianAssignmentOptimizerNK().optimize(values, org, problem)
    assert result.objective_value == 26
    assert result.matches == ((0, 1), (1, 0), (2, 2))
    assert sum(map(sum, result.allocation)) == 3
    assert all(sum(row) <= 1 for row in result.allocation)
    assert all(sum(result.allocation[i][j] for i in range(3)) <= 1 for j in range(3))


def test_s1_canonical_static_competence_matrix_exact_greedy_and_exhaustive():
    # Agent-specialization matrix C. Greedy first takes (a0,t0)=1.0 and
    # blocks the globally better reassignment (a0,t1),(a1,t0),(a2,t2).
    competence = (
        (1.0, 0.9, 0.0),
        (0.9, 0.0, 0.0),
        (0.0, 0.8, 0.8),
    )
    org = OrganizationConfigNK(
        ("a0", "a1", "a2"),
        ("t0", "t1", "t2"),
        competence,
        (1.0, 1.0, 1.0),
        3.0,
    )
    problem = ProblemSpecNK("S1-static-canonical", (1.0, 1.0, 1.0), 3.0)

    optimizer = HungarianAssignmentOptimizerNK()
    exact = optimizer.optimize(competence, org, problem)
    repeat = optimizer.optimize(competence, org, problem)
    exhaustive = _enumerate_matchings(competence, 3.0, (1.0, 1.0, 1.0))
    exhaustive_best = max(value for value, _ in exhaustive)
    exhaustive_optima = [edges for value, edges in exhaustive if value == pytest.approx(2.6)]
    greedy = greedy_assignment(competence)
    greedy_repeat = greedy_assignment(competence)
    greedy_reward = sum(competence[i][j] for i, j in greedy)

    assert exact.matches == ((0, 1), (1, 0), (2, 2))
    assert exact.objective_value == pytest.approx(2.6)
    assert exhaustive_best == pytest.approx(exact.objective_value)
    assert exhaustive_optima == [exact.matches]
    assert repeat.matches == exact.matches
    assert repeat.objective_value == exact.objective_value
    assert greedy == ((0, 0), (2, 1), (1, 2))
    assert greedy_repeat == greedy
    assert greedy_reward == pytest.approx(1.8)
    assert greedy_reward < exact.objective_value
    assert len({i for i, _ in exact.matches}) == len(exact.matches)
    assert len({j for _, j in exact.matches}) == len(exact.matches)
    assert len(exact.matches) <= 3
    assert len({i for i, _ in greedy}) == len(greedy)
    assert len({j for _, j in greedy}) == len(greedy)
    assert len(greedy) <= 3


def test_s2a_variable_demand_per_period_optimum_equals_global_enumeration():
    first = run_s2a()
    second = run_s2a()

    def without_timings(value):
        if isinstance(value, dict):
            return {key: without_timings(item) for key, item in value.items()
                    if not key.endswith("_seconds") and key != "timings_descriptive_seconds"}
        if isinstance(value, (tuple, list)):
            return type(value)(without_timings(item) for item in value)
        return value

    assert without_timings(first) == without_timings(second)
    assert first["demands"] == ((1, 1, 1), (2, 0, 1), (3, 1, 0), (0, 0, 0))
    assert first["horizon_reward"]["exact_per_period"] == pytest.approx(8.0)
    assert first["horizon_reward"]["global_exhaustive_optimum"] == pytest.approx(8.0)
    assert first["horizon_reward"]["exact_minus_global_enumeration"] == pytest.approx(0.0)
    assert first["horizon_reward"]["greedy_per_period"] == pytest.approx(7.2)
    assert first["horizon_reward"]["global_sequences_enumerated"] == 84388

    periods = first["periods"]
    assert periods[0]["exact_reward"] == pytest.approx(2.6)
    assert periods[1]["exact_reward"] == pytest.approx(2.7)
    assert periods[2]["exact_reward"] == pytest.approx(2.7)
    assert periods[3]["exact_assignments"] == ()
    assert periods[3]["exact_resource_use"] == periods[3]["greedy_resource_use"] == 0
    assert periods[2]["available_work_units"] == 4 > 3
    assert sum(periods[2]["exact_demand_unserved"].values()) > 0

    competence = first["matrix_C_agent_by_task"]
    for period in periods:
        demand = period["demand_by_task"]
        for policy in ("exact", "greedy"):
            assignments = period[f"{policy}_assignments"]
            served = period[f"{policy}_demand_satisfied"]
            assert len(assignments) <= 3
            assert len({row["agent"] for row in assignments}) == len(assignments)
            assert len({row["unit"] for row in assignments}) == len(assignments)
            assert all(served[task] <= demand[task] for task in demand)
            assert period[f"{policy}_demand_unserved"] == {
                task: demand[task] - served[task] for task in demand
            }
        assert period["competence_unchanged"] == competence
        assert period["exact_reward"] >= period["greedy_reward"]


def test_cost_minimization_requires_complete_smaller_side_assignment():
    values = ((8, 1, 6), (2, 7, 4))
    org, problem = _instance(2, 3, 2.0)
    result = HungarianAssignmentOptimizerNK().optimize(
        values, org, problem, maximize=False,
    )
    assert result.objective_value == 3
    assert len(result.matches) == 2
    with pytest.raises(ValueError, match="resource budget"):
        poor_org, poor_problem = _instance(2, 3, 1.0)
        HungarianAssignmentOptimizerNK().optimize(
            values, poor_org, poor_problem, maximize=False,
        )


@pytest.mark.parametrize("values", [(), ((1, 2),), ((1,), (2, 3)), ((math.nan, 1), (1, 1))])
def test_invalid_reward_matrices_are_rejected(values):
    org, problem = _instance()
    with pytest.raises(ValueError):
        HungarianAssignmentOptimizerNK().optimize(values, org, problem)


def test_reproducible_ties_and_empty_feasible_resource_budget():
    org, problem = _instance(2, 2, 0.0)
    optimizer = HungarianAssignmentOptimizerNK()
    first = optimizer.optimize(((1, 1), (1, 1)), org, problem)
    second = optimizer.optimize(((1, 1), (1, 1)), org, problem)
    assert first.matches == second.matches == ()
    assert first.allocation == second.allocation == ((0.0, 0.0), (0.0, 0.0))


def test_bounded_experiment_episode_replays_decisions_and_rewards():
    first = run_episode(20261020)
    second = run_episode(20261020)
    assert first["fixed_task_to_agent_mapping"] == second["fixed_task_to_agent_mapping"]
    assert first["cumulative_reward"] == second["cumulative_reward"]
    assert first["resource_use"] == second["resource_use"]
    assert [{key: value for key, value in row.items() if key != "hungarian_elapsed_seconds"}
            for row in first["trace"]] == [
        {key: value for key, value in row.items() if key != "hungarian_elapsed_seconds"}
        for row in second["trace"]
    ]
