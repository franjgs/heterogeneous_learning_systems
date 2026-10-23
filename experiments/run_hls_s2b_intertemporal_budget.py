#!/usr/bin/env python3
"""Exact S2b comparison with a single non-renewing horizon budget."""

from __future__ import annotations

import itertools
import json
import time
from functools import lru_cache
from pathlib import Path

try:
    from experiments.run_hls_s2a_static_demand import (
        AGENTS, COMPETENCE, DEMANDS, TASKS, CAPACITY,
        _expanded_problem, enumerate_matchings,
    )
except ModuleNotFoundError:  # Direct ``python experiments/...`` invocation.
    from run_hls_s2a_static_demand import (
        AGENTS, COMPETENCE, TASKS, CAPACITY,
        _expanded_problem, enumerate_matchings,
    )
from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import ProblemSpecNK


OUTPUT = Path("results/experiments/hls_s2b_intertemporal_budget/results.json")
DEMANDS = ((0, 1, 0), (1, 0, 0))
CASES = {"A_sufficient_budget": 3, "B_shared_budget_binding": 1,
         "zero_budget_control": 0}
TOL = 1e-12


def _actions_by_period():
    actions = []
    metadata = []
    for demand in DEMANDS:
        units, matrix, _, _ = _expanded_problem(demand)
        if units:
            period_actions = enumerate_matchings(matrix)
        else:
            period_actions = ((0.0, ()),)
        actions.append(period_actions)
        metadata.append((units, matrix))
    return tuple(actions), tuple(metadata)


def solve_bellman(budget: int):
    action_sets, _ = _actions_by_period()
    horizon = len(DEMANDS)

    @lru_cache(maxsize=None)
    def value(t: int, remaining: int) -> float:
        if t == horizon:
            return 0.0
        return max(
            reward + value(t + 1, remaining - len(edges))
            for reward, edges in action_sets[t]
            if len(edges) <= remaining
        )

    decisions = []
    remaining = budget
    for t, actions in enumerate(action_sets):
        feasible = [(reward + value(t + 1, remaining - len(edges)), reward, edges)
                    for reward, edges in actions if len(edges) <= remaining]
        best_value = max(item[0] for item in feasible)
        _, reward, edges = min(
            (item for item in feasible if abs(item[0] - best_value) <= TOL),
            key=lambda item: (len(item[2]), item[2]),
        )
        decisions.append((reward, edges, remaining))
        remaining -= len(edges)
    return value(0, budget), tuple(decisions), value.cache_info().currsize


def enumerate_global(budget: int):
    """Independent full-horizon enumeration; does not call the Bellman solver."""
    action_sets, _ = _actions_by_period()
    total_sequences = 0
    feasible_sequences = 0
    best_reward = float("-inf")
    best_plan = None
    for plan in itertools.product(*action_sets):
        total_sequences += 1
        used = sum(len(edges) for _, edges in plan)
        if used > budget:
            continue
        feasible_sequences += 1
        reward = sum(value for value, _ in plan)
        tie_key = (used, tuple(edges for _, edges in plan))
        if (reward > best_reward + TOL
                or (abs(reward - best_reward) <= TOL
                    and (best_plan is None or tie_key < best_plan[0]))):
            best_reward = reward
            best_plan = (tie_key, tuple((value, edges) for value, edges in plan))
    return best_reward, best_plan[1], total_sequences, feasible_sequences


def run_case(name: str, budget: int):
    optimizer = HungarianAssignmentOptimizerNK()
    periods = []
    remaining = budget
    elapsed = 0.0

    for t, demand in enumerate(DEMANDS):
        units, matrix, organization, _ = _expanded_problem(demand)
        if units and remaining > 0:
            problem = ProblemSpecNK(
                f"S2b-period-{t}", (1.0,) * len(units),
                float(min(remaining, CAPACITY)),
            )
            started = time.perf_counter()
            result = optimizer.optimize(matrix, organization, problem)
            elapsed += time.perf_counter() - started
            edges = result.matches
            reward = result.objective_value
            available_actions = enumerate_matchings(matrix)
            myopic_value = max(
                value for value, action in available_actions if len(action) <= remaining
            )
            if abs(reward - myopic_value) > TOL:
                raise AssertionError("myopic solver did not optimize its constrained period")
        else:
            edges = ()
            reward = 0.0
            available_actions = ((0.0, ()),)
            myopic_value = 0.0

        unit_ids = tuple(f"{TASKS[task]}_unit{index}" for index, task in enumerate(units))
        assignments = tuple({"agent": AGENTS[i], "task": TASKS[units[j]],
                             "unit": unit_ids[j]} for i, j in edges)
        served = [0] * len(TASKS)
        for _, unit_index in edges:
            served[units[unit_index]] += 1
        unserved = [demand[k] - served[k] for k in range(len(TASKS))]
        if (any(x < 0 for x in unserved) or len(edges) > CAPACITY
                or len(edges) > remaining
                or len({i for i, _ in edges}) != len(edges)
                or len({j for _, j in edges}) != len(edges)):
            raise AssertionError("myopic policy produced an infeasible action")
        after = remaining - len(edges)
        periods.append({
            "period": t,
            "demand_by_task": dict(zip(TASKS, demand)),
            "budget_before": remaining,
            "assignments": assignments,
            "reward": reward,
            "immediate_optimum_given_budget": myopic_value,
            "units_executed": len(edges),
            "budget_after": after,
            "demand_satisfied": dict(zip(TASKS, served)),
            "demand_unserved": dict(zip(TASKS, unserved)),
        })
        remaining = after

    return {
        "name": name,
        "initial_budget": budget,
        "periods": tuple(periods),
        "reward": sum(period["reward"] for period in periods),
        "budget_consumed": budget - remaining,
        "budget_remaining": remaining,
        "solver_seconds_descriptive": elapsed,
    }


def run_s2b():
    output_cases = {}
    for name, budget in CASES.items():
        myopic = run_case(name, budget)
        bellman_value, bellman_decisions, dp_states = solve_bellman(budget)
        enum_value, enum_plan, total_seq, feasible_seq = enumerate_global(budget)

        bellman_periods = []
        remaining = budget
        for t, (reward, edges, before) in enumerate(bellman_decisions):
            if before != remaining or len(edges) > remaining:
                raise AssertionError("Bellman reconstruction has inconsistent budget state")
            units, _, _, _ = _expanded_problem(DEMANDS[t])
            ids = tuple(f"{TASKS[task]}_unit{index}" for index, task in enumerate(units))
            served = [0] * len(TASKS)
            for _, unit_index in edges:
                served[units[unit_index]] += 1
            unserved = [DEMANDS[t][k] - served[k] for k in range(len(TASKS))]
            bellman_periods.append({
                "period": t,
                "demand_by_task": dict(zip(TASKS, DEMANDS[t])),
                "budget_before": remaining,
                "assignments": tuple({"agent": AGENTS[i], "task": TASKS[units[j]],
                                      "unit": ids[j]} for i, j in edges),
                "reward": reward,
                "units_executed": len(edges),
                "budget_after": remaining - len(edges),
                "demand_satisfied": dict(zip(TASKS, served)),
                "demand_unserved": dict(zip(TASKS, unserved)),
            })
            remaining -= len(edges)
        if abs(bellman_value - enum_value) > TOL:
            raise AssertionError("Bellman value disagrees with full-horizon enumeration")
        if bellman_value + TOL < myopic["reward"]:
            raise AssertionError("Bellman value fell below the feasible myopic policy")

        if name == "A_sufficient_budget" and abs(bellman_value - myopic["reward"]) > TOL:
            raise AssertionError("sufficient-budget control should have no planning gap")
        if name == "B_shared_budget_binding" and not bellman_value > myopic["reward"] + TOL:
            raise AssertionError("binding-budget case should exhibit a planning gap")

        output_cases[name] = {
            "budget": budget,
            "myopic": myopic,
            "bellman": {"reward": bellman_value, "budget_consumed": budget - remaining,
                        "budget_remaining": remaining, "periods": tuple(bellman_periods),
                        "reachable_dp_states": dp_states},
            "global_exhaustive": {
                "reward": enum_value,
                "plan": tuple({"period": t, "reward": reward, "edges": edges}
                              for t, (reward, edges) in enumerate(enum_plan)),
                "cartesian_sequences_examined": total_seq,
                "budget_feasible_sequences": feasible_seq,
            },
            "bellman_minus_myopic": bellman_value - myopic["reward"],
            "bellman_minus_enumeration": bellman_value - enum_value,
        }

    return {
        "experiment": "HLS-S2b-shared-intertemporal-budget",
        "matrix_C_agent_by_task": COMPETENCE,
        "agents": AGENTS,
        "tasks": TASKS,
        "demands": DEMANDS,
        "per_period_agent_capacity": 1,
        "global_resource_budget_nonrenewing": True,
        "competence_constant": True,
        "cases": output_cases,
        "assumptions": {
            "demand_sequence_known_to_both_policies": True,
            "myopic_rule_uses_current_period_only": True,
            "both_use_same_public_C_and_per_period_feasible_actions": True,
            "no_learning_transfer_switching_cost_or_other_temporal_constraint": True,
        },
    }


def main():
    result = run_s2b()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = {
        name: {"myopic": case["myopic"]["reward"],
               "bellman": case["bellman"]["reward"],
               "enumeration": case["global_exhaustive"]["reward"],
               "gap": case["bellman_minus_myopic"],
               "myopic_budget_path": [p["budget_after"] for p in case["myopic"]["periods"]],
               "bellman_budget_path": [p["budget_after"] for p in case["bellman"]["periods"]]}
        for name, case in result["cases"].items()
    }
    print(json.dumps({"output": str(OUTPUT), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
