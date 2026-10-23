#!/usr/bin/env python3
"""Bounded matched-matrix comparison for joint HLS bipartite assignment."""

from __future__ import annotations

import itertools
import json
import random
import statistics
import time
from pathlib import Path

import scipy

from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK


OUTPUT = Path("results/experiments/hls_hungarian_assignment/results.json")
AGENTS = ("agent_0", "agent_1", "agent_2")
TASKS = ("task_0", "task_1", "task_2")
HORIZON = 12
SEEDS = tuple(range(20261020, 20261030))
ORG = OrganizationConfigNK(
    AGENTS, TASKS, ((0.5, 0.5, 0.5),) * 3,
    (1.0, 1.0, 1.0), 3.0,
)
PROBLEM = ProblemSpecNK("three simultaneous tasks", (1.0, 1.0, 1.0), 3.0)
OPTIMIZER = HungarianAssignmentOptimizerNK()


def reward_matrices(seed: int, horizon: int = HORIZON):
    rng = random.Random(seed)
    return tuple(
        tuple(tuple(rng.randint(1, 100) / 100.0 for _ in TASKS) for _ in AGENTS)
        for _ in range(horizon)
    )


def greedy_assignment(values):
    n, k = len(values), len(values[0])
    edges = sorted(
        ((float(values[i][j]), i, j) for i in range(n) for j in range(k)),
        key=lambda edge: (-edge[0], edge[1], edge[2]),
    )
    selected = []
    used_agents, used_tasks = set(), set()
    for value, agent, task in edges:
        if len(selected) == min(n, k, int(ORG.collective_effort_budget)):
            break
        if ORG.effort_limits[agent] < 1.0 or agent in used_agents or task in used_tasks:
            continue
        selected.append((agent, task, value))
        used_agents.add(agent)
        used_tasks.add(task)
    return tuple((i, j) for i, j, _ in selected)


def best_fixed_mapping(matrices):
    start = time.perf_counter()
    candidates = []
    for permutation in itertools.permutations(range(len(AGENTS))):
        value = sum(matrix[agent][task]
                    for matrix in matrices for task, agent in enumerate(permutation))
        candidates.append((value, permutation))
    best_value = max(value for value, _ in candidates)
    mapping = min(permutation for value, permutation in candidates
                  if abs(value - best_value) <= 1e-12)
    return mapping, time.perf_counter() - start


def _as_dict_matches(matches):
    return [{"agent": AGENTS[i], "task": TASKS[j]} for i, j in matches]


def run_episode(seed: int):
    matrices = reward_matrices(seed)
    fixed_mapping, fixed_fit_seconds = best_fixed_mapping(matrices)
    totals = {"HUNGARIAN": 0.0, "GREEDY": 0.0, "BEST_FIXED": 0.0}
    resources = {name: 0 for name in totals}
    timings = {name: 0.0 for name in totals}
    trace = []
    exhaustive_checks = 0
    for period, matrix in enumerate(matrices):
        optimal = OPTIMIZER.optimize(matrix, ORG, PROBLEM)
        timings["HUNGARIAN"] += optimal.elapsed_seconds
        hungarian = optimal.matches
        greedy_start = time.perf_counter()
        greedy = greedy_assignment(matrix)
        timings["GREEDY"] += time.perf_counter() - greedy_start
        fixed = tuple((agent, task) for task, agent in enumerate(fixed_mapping))
        assignments = {"HUNGARIAN": hungarian, "GREEDY": greedy, "BEST_FIXED": fixed}
        for policy, matches in assignments.items():
            totals[policy] += sum(matrix[i][j] for i, j in matches)
            resources[policy] += len(matches)
        enumerated_best = max(
            sum(matrix[permutation[task]][task] for task in range(len(TASKS)))
            for permutation in itertools.permutations(range(len(AGENTS)))
        )
        if abs(optimal.objective_value - enumerated_best) > 1e-12:
            raise AssertionError("assignment backend disagrees with exhaustive 3×3 enumeration")
        exhaustive_checks += 1
        trace.append({
            "period": period,
            "reward_matrix_agent_by_task": [list(row) for row in matrix],
            "assignments": {name: _as_dict_matches(matches) for name, matches in assignments.items()},
            "rewards": {name: sum(matrix[i][j] for i, j in matches)
                        for name, matches in assignments.items()},
            "resource_use": {name: len(matches) for name, matches in assignments.items()},
            "agent_resource_use": {
                name: [sum(i == agent for i, _ in matches) for agent in range(len(AGENTS))]
                for name, matches in assignments.items()
            },
            "task_assignment_count": {
                name: [sum(j == task for _, j in matches) for task in range(len(TASKS))]
                for name, matches in assignments.items()
            },
            "hungarian_elapsed_seconds": optimal.elapsed_seconds,
        })
    timings["BEST_FIXED"] = fixed_fit_seconds
    return {
        "seed": seed,
        "fixed_task_to_agent_mapping": {TASKS[j]: AGENTS[fixed_mapping[j]] for j in range(len(TASKS))},
        "cumulative_reward": totals,
        "resource_use": resources,
        "timing_seconds": timings,
        "exhaustive_optimality_checks": exhaustive_checks,
        "trace": trace,
    }


def run_experiment():
    replications = [run_episode(seed) for seed in SEEDS]
    policies = ("HUNGARIAN", "GREEDY", "BEST_FIXED")
    summary = {
        policy: {
            "mean_cumulative_reward": statistics.fmean(rep["cumulative_reward"][policy] for rep in replications),
            "sd_cumulative_reward": statistics.stdev(rep["cumulative_reward"][policy] for rep in replications),
            "mean_resource_use": statistics.fmean(rep["resource_use"][policy] for rep in replications),
            "mean_computation_seconds_per_episode": statistics.fmean(rep["timing_seconds"][policy] for rep in replications),
            "computation_timing_scope": ("episode-level offline permutation search over 3! maps"
                                         if policy == "BEST_FIXED" else "sum of per-period decisions"),
        }
        for policy in policies
    }
    paired = {}
    for left, right in (("HUNGARIAN", "GREEDY"), ("HUNGARIAN", "BEST_FIXED"),
                        ("GREEDY", "BEST_FIXED")):
        values = [rep["cumulative_reward"][left] - rep["cumulative_reward"][right]
                  for rep in replications]
        paired[f"{left}_minus_{right}"] = {
            "mean": statistics.fmean(values),
            "sd": statistics.stdev(values),
            "per_seed": values,
        }
    return {
        "experiment": "HLS N×K joint assignment: SciPy linear-sum solver vs greedy and best fixed mapping",
        "ontology": {
            "A_scenario": "Three simultaneous task types and three agents; each edge has an explicit exogenous reward; one unit per match; constant competence and no learning.",
            "B_mechanisms": "No capability-transition mechanism is active; competence fields remain constant and rewards are exogenous assignment values.",
            "C_organization": "Joint per-period maximum-weight bipartite matching via SciPy linear_sum_assignment; compared with deterministic global-edge greedy and best episode-level fixed permutation.",
        },
        "configuration": {
            "agents": list(AGENTS), "tasks": list(TASKS),
            "horizon_matrices_per_seed": HORIZON, "seeds": list(SEEDS),
            "reward_generation": "Python random.Random(seed), independent uniform integer in [1,100] divided by 100 for each agent-task edge and period.",
            "competence": "constant placeholder 0.5; not used to generate rewards",
            "resource_contract": "same N×K geometry: individual limit 1, collective/problem budget 3; each selected edge consumes one resource; no agent/task may be used twice per period.",
            "objective": "maximize sum of selected edge rewards; assignments may remain unmatched if optional maximum-reward objective prefers it.",
            "fixed_baseline": "best of all 3! task-to-agent one-to-one mappings over the full 12-matrix episode; offline optimized within the declared fixed class. Its timing includes this per-episode map fit, not the subsequent lookup.",
            "greedy_baseline": "sort all current-period edges by descending reward, tie by agent then task index, accept if both endpoints remain unused and resource permits.",
            "solver": "scipy.optimize.linear_sum_assignment; SciPy modified Jonker–Volgenant backend solving the linear assignment objective, not a literal implementation of Kuhn's 1955 procedure.",
            "scipy_version": scipy.__version__,
        },
        "summary": summary,
        "paired_comparisons": paired,
        "replications": replications,
        "limitations": [
            "This validates a discrete unit-effort one-to-one matching restriction, not arbitrary fractional N×K allocations.",
            "Rewards are synthetic, additive, fully observed, and exogenous; no CES complementarity, learning, transfer, uncertainty, or real task execution is represented.",
            "The fixed baseline is optimized with full episode knowledge, while Hungarian and greedy react to each current matrix; this is deliberately a strong static reference.",
            "SciPy's backend is an equivalent linear-sum assignment optimizer based on modified Jonker–Volgenant, not a code-level reproduction of Kuhn's Hungarian steps.",
            "Timing is local diagnostic data and is not a hardware-independent performance claim.",
        ],
    }


def main():
    result = run_experiment()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    for policy, metrics in result["summary"].items():
        print(f"{policy}: reward={metrics['mean_cumulative_reward']:.4f} "
              f"(SD {metrics['sd_cumulative_reward']:.4f}), "
              f"resources={metrics['mean_resource_use']:.1f}, "
              f"seconds/episode={metrics['mean_computation_seconds_per_episode']:.6f}")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
