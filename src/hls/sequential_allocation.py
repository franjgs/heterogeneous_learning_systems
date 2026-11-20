"""Deterministic sequential allocation with fixed effectiveness and capacity.

Effectiveness is a deterministic contribution to the objective, not a latent
competence measurement or an observed task success. The exact offline policy
enumerates assignments and is intended for small finite instances.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import fsum, isfinite
from typing import Sequence


GLOBAL_CAPACITY_EXHAUSTED = "global_capacity_exhausted"
FIXED_AGENT_EXHAUSTED = "fixed_agent_exhausted"
OFFLINE_OPTIMAL_REJECTION = "offline_optimal_rejection"


@dataclass(frozen=True)
class TaskDecision:
    """Decision and contribution for one task in the input sequence."""

    task_index: int
    task_type: int
    agent_index: int | None
    effectiveness: float
    rejection_reason: str | None


@dataclass(frozen=True)
class AllocationResult:
    """Policy output and collective metrics over all received tasks."""

    policy: str
    decisions: tuple[TaskDecision, ...]
    initial_capacities: tuple[int, ...]
    remaining_capacities: tuple[int, ...]
    total_effectiveness: float
    mean_effectiveness: float

    @property
    def assigned_count(self) -> int:
        return sum(decision.agent_index is not None for decision in self.decisions)

    @property
    def rejected_count(self) -> int:
        return len(self.decisions) - self.assigned_count

    @property
    def rejection_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for decision in self.decisions:
            if decision.rejection_reason is not None:
                counts[decision.rejection_reason] = counts.get(decision.rejection_reason, 0) + 1
        return counts


def run_fixed_policy(
    task_types: Sequence[int],
    effectiveness: Sequence[Sequence[float]],
    capacities: Sequence[int],
    type_to_agent: Sequence[int],
) -> AllocationResult:
    """Apply a predeclared task-type-to-agent mapping with no reassignment.

    If the designated agent is exhausted while other agents retain capacity,
    the task is rejected with ``fixed_agent_exhausted``. Once all capacity is
    exhausted, rejection is classified as ``global_capacity_exhausted``.
    """
    tasks, matrix, initial = _validate_inputs(task_types, effectiveness, capacities)
    mapping = tuple(type_to_agent)
    n_agents, n_types = len(matrix), len(matrix[0])
    if len(mapping) != n_types:
        raise ValueError("type_to_agent must contain one agent for each task type")
    if any(not _is_integer(agent) or not 0 <= agent < n_agents for agent in mapping):
        raise ValueError("type_to_agent contains an invalid agent index")

    remaining = list(initial)
    decisions: list[TaskDecision] = []
    for index, task_type in enumerate(tasks):
        agent = mapping[task_type]
        if remaining[agent] > 0:
            remaining[agent] -= 1
            decisions.append(TaskDecision(index, task_type, agent, matrix[agent][task_type], None))
        else:
            reason = GLOBAL_CAPACITY_EXHAUSTED if not any(remaining) else FIXED_AGENT_EXHAUSTED
            decisions.append(TaskDecision(index, task_type, None, 0.0, reason))
    return _result("fixed", decisions, initial, remaining)


def run_greedy_online_policy(
    task_types: Sequence[int],
    effectiveness: Sequence[Sequence[float]],
    capacities: Sequence[int],
) -> AllocationResult:
    """Assign each current task to the best-capacity agent; ties use low ID.

    The decision rule receives the current task type and remaining capacities
    only. It does not inspect future task types.
    """
    tasks, matrix, initial = _validate_inputs(task_types, effectiveness, capacities)
    remaining = list(initial)
    decisions: list[TaskDecision] = []
    for index, task_type in enumerate(tasks):
        feasible = [agent for agent, capacity in enumerate(remaining) if capacity > 0]
        if not feasible:
            decisions.append(TaskDecision(index, task_type, None, 0.0, GLOBAL_CAPACITY_EXHAUSTED))
            continue
        # max() is stable on equal keys, so the lowest agent index wins ties.
        agent = max(feasible, key=lambda candidate: matrix[candidate][task_type])
        remaining[agent] -= 1
        decisions.append(TaskDecision(index, task_type, agent, matrix[agent][task_type], None))
    return _result("greedy_online", decisions, initial, remaining)


def run_optimal_offline_policy(
    task_types: Sequence[int],
    effectiveness: Sequence[Sequence[float]],
    capacities: Sequence[int],
) -> AllocationResult:
    """Enumerate all capacity-feasible assignments and return an exact maximum.

    Agent indices are considered in ascending order and rejection last. Sums
    are compared exactly as rational values of the supplied Python numeric
    entries (floats are interpreted as their exact binary values). Among
    equal-valued optima, the lexicographically first action sequence is kept.
    Complexity is exponential in sequence length; this policy is for small
    deterministic benchmark instances, not a general production optimizer.
    """
    tasks, matrix, initial = _validate_inputs(task_types, effectiveness, capacities)
    remaining = list(initial)
    choices: list[int | None] = []
    best_choices: tuple[int | None, ...] | None = None
    # Compare supplied Python numeric values exactly as represented, avoiding
    # path-ranking changes caused by floating-point accumulation order.
    exact_matrix = tuple(tuple(Fraction.from_float(float(value)) for value in row) for row in matrix)
    best_value: Fraction | None = None

    def enumerate_from(task_index: int, value: Fraction) -> None:
        nonlocal best_choices, best_value
        if task_index == len(tasks):
            if best_value is None or value > best_value:
                best_value = value
                best_choices = tuple(choices)
            return

        task_type = tasks[task_index]
        for agent, capacity in enumerate(remaining):
            if capacity <= 0:
                continue
            remaining[agent] -= 1
            choices.append(agent)
            enumerate_from(task_index + 1, value + exact_matrix[agent][task_type])
            choices.pop()
            remaining[agent] += 1
        choices.append(None)
        enumerate_from(task_index + 1, value)
        choices.pop()

    enumerate_from(0, Fraction(0))
    assert best_choices is not None

    remaining = list(initial)
    decisions: list[TaskDecision] = []
    for index, (task_type, agent) in enumerate(zip(tasks, best_choices)):
        if agent is None:
            reason = GLOBAL_CAPACITY_EXHAUSTED if not any(remaining) else OFFLINE_OPTIMAL_REJECTION
            decisions.append(TaskDecision(index, task_type, None, 0.0, reason))
        else:
            remaining[agent] -= 1
            decisions.append(TaskDecision(index, task_type, agent, matrix[agent][task_type], None))
    return _result("optimal_offline", decisions, initial, remaining)


def _validate_inputs(
    task_types: Sequence[int],
    effectiveness: Sequence[Sequence[float]],
    capacities: Sequence[int],
) -> tuple[tuple[int, ...], tuple[tuple[float, ...], ...], tuple[int, ...]]:
    tasks = tuple(task_types)
    if not tasks:
        raise ValueError("task sequence must not be empty")
    if not effectiveness:
        raise ValueError("at least one agent is required")
    matrix = tuple(tuple(row) for row in effectiveness)
    if not matrix[0]:
        raise ValueError("at least one task type is required")
    n_types = len(matrix[0])
    if any(len(row) != n_types for row in matrix):
        raise ValueError("effectiveness matrix must be rectangular")
    for row in matrix:
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError("effectiveness values must be finite numbers in [0, 1]")
    if len(capacities) != len(matrix):
        raise ValueError("one initial capacity is required per agent")
    initial = tuple(capacities)
    if any(not _is_integer(capacity) or capacity < 0 for capacity in initial):
        raise ValueError("capacities must be non-negative integers")
    if any(not _is_integer(task) or not 0 <= task < n_types for task in tasks):
        raise ValueError("task sequence contains an invalid task type")
    return tasks, matrix, initial


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _result(
    policy: str,
    decisions: list[TaskDecision],
    initial: tuple[int, ...],
    remaining: list[int],
) -> AllocationResult:
    total = fsum(decision.effectiveness for decision in decisions)
    return AllocationResult(
        policy=policy,
        decisions=tuple(decisions),
        initial_capacities=initial,
        remaining_capacities=tuple(remaining),
        total_effectiveness=total,
        mean_effectiveness=total / len(decisions),
    )
