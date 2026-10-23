#!/usr/bin/env python3
"""Deterministic S2a reference: independently optimal matching per period."""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
try:
    from experiments.run_hls_hungarian_assignment import greedy_assignment
except ModuleNotFoundError:  # Direct ``python experiments/...`` invocation.
    from run_hls_hungarian_assignment import greedy_assignment


OUTPUT = Path("results/experiments/hls_s2a_static_demand/results.json")
AGENTS = ("a0", "a1", "a2")
TASKS = ("t0", "t1", "t2")
COMPETENCE = ((1.0, 0.9, 0.0), (0.9, 0.0, 0.0), (0.0, 0.8, 0.8))
DEMANDS = ((1, 1, 1), (2, 0, 1), (3, 1, 0), (0, 0, 0))
CAPACITY = 3


def enumerate_matchings(matrix: tuple[tuple[float, ...], ...]):
    """Enumerate every feasible optional one-to-one agent/unit matching."""
    n = len(matrix)
    m = len(matrix[0]) if n else 0
    edges = tuple((i, j) for i in range(n) for j in range(m))
    actions = []
    for count in range(min(n, m, CAPACITY) + 1):
        for selected in itertools.combinations(edges, count):
            if (len({i for i, _ in selected}) == count
                    and len({j for _, j in selected}) == count):
                reward = sum(matrix[i][j] for i, j in selected)
                actions.append((reward, selected))
    return tuple(actions)


def _expanded_problem(demand: tuple[int, ...]):
    units = tuple(task for task, count in enumerate(demand) for _ in range(count))
    if not units:
        return units, (), None, None
    matrix = tuple(tuple(COMPETENCE[i][task] for task in units) for i in range(len(AGENTS)))
    unit_ids = tuple(f"{TASKS[task]}_unit{index}" for index, task in enumerate(units))
    organization = OrganizationConfigNK(
        AGENTS,
        unit_ids,
        matrix,
        (1.0,) * len(AGENTS),
        float(CAPACITY),
    )
    problem = ProblemSpecNK("S2a-current-demand", (1.0,) * len(units), float(CAPACITY))
    return units, matrix, organization, problem


def run_s2a():
    optimizer = HungarianAssignmentOptimizerNK()
    periods = []
    global_action_sets = []
    exact_total = 0.0
    greedy_total = 0.0
    timings = {"period_solver_seconds": 0.0, "period_greedy_seconds": 0.0,
               "global_enumeration_seconds": 0.0}

    for period, demand in enumerate(DEMANDS):
        units, matrix, organization, problem = _expanded_problem(demand)
        if units:
            started = time.perf_counter()
            exact_result = optimizer.optimize(matrix, organization, problem)
            solver_seconds = time.perf_counter() - started
            started = time.perf_counter()
            greedy_edges = greedy_assignment(matrix)
            greedy_seconds = time.perf_counter() - started
            actions = enumerate_matchings(matrix)
            exact_edges = exact_result.matches
            exact_reward = exact_result.objective_value
            greedy_reward = sum(matrix[i][j] for i, j in greedy_edges)
        else:
            # ProblemSpecNK requires a nonempty task dimension. With no demand,
            # the feasible action set is the singleton empty assignment.
            solver_seconds = greedy_seconds = 0.0
            exact_edges = greedy_edges = ()
            exact_reward = greedy_reward = 0.0
            actions = ((0.0, ()),)

        if not units:
            unit_ids = ()
        else:
            unit_ids = tuple(f"{TASKS[task]}_unit{index}" for index, task in enumerate(units))

        def encode(edges):
            return tuple({"agent": AGENTS[i], "task": TASKS[units[j]], "unit": unit_ids[j]}
                         for i, j in edges)

        def served_counts(edges):
            served = [0] * len(TASKS)
            for _, unit_index in edges:
                served[units[unit_index]] += 1
            return tuple(served)

        exact_served = served_counts(exact_edges)
        greedy_served = served_counts(greedy_edges)
        if any(count > limit for count, limit in zip(exact_served, demand)):
            raise AssertionError("exact assignment exceeded task demand")
        if any(count > limit for count, limit in zip(greedy_served, demand)):
            raise AssertionError("greedy assignment exceeded task demand")
        if (len({i for i, _ in exact_edges}) != len(exact_edges)
                or len({j for _, j in exact_edges}) != len(exact_edges)
                or len(exact_edges) > CAPACITY):
            raise AssertionError("exact assignment violated per-period capacity")
        if (len({i for i, _ in greedy_edges}) != len(greedy_edges)
                or len({j for _, j in greedy_edges}) != len(greedy_edges)
                or len(greedy_edges) > CAPACITY):
            raise AssertionError("greedy assignment violated per-period capacity")
        exhaustive_best = max(value for value, _ in actions)
        if abs(exact_reward - exhaustive_best) > 1e-12:
            raise AssertionError("per-period solver disagrees with exhaustive enumeration")
        if greedy_reward > exact_reward + 1e-12:
            raise AssertionError("greedy exceeded exact optimum")

        exact_total += exact_reward
        greedy_total += greedy_reward
        timings["period_solver_seconds"] += solver_seconds
        timings["period_greedy_seconds"] += greedy_seconds
        global_action_sets.append(actions)
        periods.append({
            "period": period,
            "demand_by_task": dict(zip(TASKS, demand)),
            "available_work_units": len(units),
            "exact_assignments": encode(exact_edges),
            "greedy_assignments": encode(greedy_edges),
            "exact_reward": exact_reward,
            "greedy_reward": greedy_reward,
            "exact_demand_satisfied": dict(zip(TASKS, exact_served)),
            "greedy_demand_satisfied": dict(zip(TASKS, greedy_served)),
            "exact_demand_unserved": dict(zip(TASKS, (demand[k] - exact_served[k] for k in range(len(TASKS))))),
            "greedy_demand_unserved": dict(zip(TASKS, (demand[k] - greedy_served[k] for k in range(len(TASKS))))),
            "exact_resource_use": len(exact_edges),
            "greedy_resource_use": len(greedy_edges),
            "solver_seconds": solver_seconds,
            "greedy_seconds": greedy_seconds,
            "competence_unchanged": COMPETENCE,
        })

    started = time.perf_counter()
    global_best_reward = float("-inf")
    global_best_plan = None
    global_sequences_checked = 0
    for period_actions in itertools.product(*global_action_sets):
        global_sequences_checked += 1
        value = sum(reward for reward, _ in period_actions)
        if value > global_best_reward:
            global_best_reward = value
            global_best_plan = tuple(edges for _, edges in period_actions)
    timings["global_enumeration_seconds"] = time.perf_counter() - started
    if abs(exact_total - global_best_reward) > 1e-12:
        raise AssertionError("per-period exact policy disagrees with horizon enumeration")

    return {
        "experiment": "HLS-S2a-static-competence-variable-demand",
        "matrix_C_agent_by_task": COMPETENCE,
        "agents": AGENTS,
        "tasks": TASKS,
        "demands": DEMANDS,
        "capacity_per_period": CAPACITY,
        "periods": tuple(periods),
        "horizon_reward": {
            "exact_per_period": exact_total,
            "greedy_per_period": greedy_total,
            "global_exhaustive_optimum": global_best_reward,
            "exact_minus_global_enumeration": exact_total - global_best_reward,
            "greedy_gap": exact_total - greedy_total,
            "global_sequences_enumerated": global_sequences_checked,
        },
        "global_exhaustive_plan": global_best_plan,
        "timings_descriptive_seconds": timings,
        "assumptions": {
            "competencies_and_reward_known_constant": True,
            "periods_independent_and_resources_renewed": True,
            "current_demand_observed_before_decision": True,
            "future_demand_unobserved_and_not_needed": True,
            "no_learning_transfer_backlog_switching_cost_or_intertemporal_budget": True,
        },
    }


def main():
    result = run_s2a()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), **result["horizon_reward"],
                      "periods": [{"demand": p["demand_by_task"],
                                   "exact_reward": p["exact_reward"],
                                   "greedy_reward": p["greedy_reward"]}
                                  for p in result["periods"]]}, indent=2))


if __name__ == "__main__":
    main()
