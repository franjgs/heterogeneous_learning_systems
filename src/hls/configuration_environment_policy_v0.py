"""Deterministic configuration × environment × policy diagnostic for HLS v0.

This module is intentionally a small, standalone instrument.  It does not
modify G3/G3-H physics or define an HLS mechanism.  It reuses the canonical
MIS diminishing learning-by-doing increment for a single assigned worker and
task, then compares a fair greedy-use policy class with finite-horizon dynamic
programming under fully known task sequences.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import isfinite
from typing import Literal

from .g3_organizational_value import learning_increment
from .minimal_reference_scenario import EXACT_TOL


Agent = int
Task = int
State = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
PolicyName = Literal["GREEDY_USE", "JOINT_DP"]


GENERALIST: State = ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5))
SPECIALIST: State = ((1.0, 0.0), (0.0, 1.0), (0.5, 0.5))
DIVERSE: State = ((0.8, 0.2), (0.2, 0.8), (0.5, 0.5))

CONFIGURATIONS: dict[str, State] = {
    "GENERALIST": GENERALIST,
    "SPECIALIST": SPECIALIST,
    "DIVERSE": DIVERSE,
}

# Explicit known sequences: 0 is task/capability A, 1 is B.
ENVIRONMENTS: dict[str, tuple[Task, ...]] = {
    "E0_STABLE_BALANCED": (0, 1, 0, 1, 0, 1),
    "E1_STABLE_SKEWED": (0, 0, 0, 0, 1, 0),
    "E2_SHIFT": (0, 0, 0, 1, 1, 1),
}


def _validate_state(state: State) -> None:
    if len(state) != 3 or any(len(row) != 2 for row in state):
        raise ValueError("v0 requires a 3-agent x 2-capability state")
    if not all(isfinite(value) and 0.0 <= value <= 1.0 for row in state for value in row):
        raise ValueError("competence values must be finite and lie in [0, 1]")


def _validate_task(task: Task) -> None:
    if task not in (0, 1):
        raise ValueError("task must be 0 (A) or 1 (B)")


def total_budget(state: State) -> float:
    """Return total initial competence, the sole equal-resource budget in v0."""
    _validate_state(state)
    return sum(sum(row) for row in state)


def reward(state: State, agent: Agent, task: Task) -> float:
    """Immediate deterministic utility of assigning ``agent`` to ``task``."""
    _validate_state(state)
    if agent not in (0, 1, 2):
        raise ValueError("agent must be 0, 1, or 2")
    _validate_task(task)
    return state[agent][task]


def transition(state: State, agent: Agent, task: Task, learning_scale: float) -> State:
    """Apply the canonical MIS increment only to the competence actually used.

    ``learning_scale=0`` is the exact development-disabled ablation.
    """
    current = reward(state, agent, task)  # validates state, agent, and task
    increment = learning_increment(current, learning_scale)
    rows = [list(row) for row in state]
    rows[agent][task] += increment
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def optimal_actions(values: dict[Agent, float], *, tolerance: float = EXACT_TOL) -> tuple[Agent, ...]:
    """Return the complete optimal set in label order, independent of iteration."""
    maximum = max(values.values())
    return tuple(agent for agent in sorted(values) if maximum - values[agent] <= tolerance)


@dataclass(frozen=True)
class PolicyEvaluation:
    policy: PolicyName
    value: float
    first_actions: tuple[Agent, ...]
    greedy_tie_steps: int


def evaluate_policy(
    state: State,
    sequence: tuple[Task, ...],
    learning_scale: float,
    policy: PolicyName,
) -> PolicyEvaluation:
    """Evaluate a policy class exactly over a fully known finite sequence.

    GREEDY_USE is the strongest fair greedy class: at each time it restricts
    action to the complete immediate-reward optimum set, then chooses the
    continuation-maximizing member only to resolve an exact reward tie.  It
    never sacrifices current reward.  JOINT_DP maximizes over all agents.
    """
    _validate_state(state)
    if not isfinite(learning_scale) or learning_scale < 0.0:
        raise ValueError("learning_scale must be finite and non-negative")
    if policy not in ("GREEDY_USE", "JOINT_DP"):
        raise ValueError("unknown policy")
    if not sequence:
        raise ValueError("sequence must be non-empty")
    for task in sequence:
        _validate_task(task)

    @lru_cache(maxsize=None)
    def value_at(time: int, current: State) -> float:
        if time == len(sequence):
            return 0.0
        task = sequence[time]
        immediate = {agent: reward(current, agent, task) for agent in range(3)}
        candidates = optimal_actions(immediate) if policy == "GREEDY_USE" else (0, 1, 2)
        return max(
            immediate[agent] + value_at(time + 1, transition(current, agent, task, learning_scale))
            for agent in candidates
        )

    first_task = sequence[0]
    immediate = {agent: reward(state, agent, first_task) for agent in range(3)}
    candidates = optimal_actions(immediate) if policy == "GREEDY_USE" else (0, 1, 2)
    action_values = {
        agent: immediate[agent] + value_at(1, transition(state, agent, first_task, learning_scale))
        for agent in candidates
    }

    # Count time steps on the value-maximizing policy envelope that have a
    # current greedy tie. It is diagnostic only; class value is tie-fair.
    @lru_cache(maxsize=None)
    def tie_count_at(time: int, current: State) -> int:
        if time == len(sequence):
            return 0
        task = sequence[time]
        immediate_here = {agent: reward(current, agent, task) for agent in range(3)}
        allowed = optimal_actions(immediate_here) if policy == "GREEDY_USE" else (0, 1, 2)
        continuation_values = {
            agent: immediate_here[agent]
            + value_at(time + 1, transition(current, agent, task, learning_scale))
            for agent in allowed
        }
        best = optimal_actions(continuation_values)
        return int(policy == "GREEDY_USE" and len(allowed) > 1) + min(
            tie_count_at(time + 1, transition(current, agent, task, learning_scale)) for agent in best
        )

    return PolicyEvaluation(
        policy=policy,
        value=value_at(0, state),
        first_actions=optimal_actions(action_values),
        greedy_tie_steps=tie_count_at(0, state),
    )


def brute_force_joint_value(state: State, sequence: tuple[Task, ...], learning_scale: float) -> float:
    """Independent exhaustive recursion for tiny-horizon DP test controls."""
    _validate_state(state)
    if not sequence:
        return 0.0
    task = sequence[0]
    return max(
        reward(state, agent, task) + brute_force_joint_value(transition(state, agent, task, learning_scale), sequence[1:], learning_scale)
        for agent in range(3)
    )


@dataclass(frozen=True)
class MatrixPoint:
    configuration: str
    environment: str
    development_enabled: bool
    learning_scale: float
    greedy: PolicyEvaluation
    joint_dp: PolicyEvaluation

    @property
    def management_value(self) -> float:
        return self.joint_dp.value - self.greedy.value


def evaluate_matrix(*, learning_scale: float = 0.5, development_enabled: bool = True) -> tuple[MatrixPoint, ...]:
    """Evaluate all three configurations and environments under both policies."""
    effective_scale = learning_scale if development_enabled else 0.0
    rows = []
    for configuration, state in CONFIGURATIONS.items():
        for environment, sequence in ENVIRONMENTS.items():
            greedy = evaluate_policy(state, sequence, effective_scale, "GREEDY_USE")
            joint = evaluate_policy(state, sequence, effective_scale, "JOINT_DP")
            if joint.value + EXACT_TOL < greedy.value:
                raise AssertionError("dynamic programming must weakly dominate the greedy policy class")
            rows.append(
                MatrixPoint(
                    configuration=configuration,
                    environment=environment,
                    development_enabled=development_enabled,
                    learning_scale=effective_scale,
                    greedy=greedy,
                    joint_dp=joint,
                )
            )
    return tuple(rows)


def configuration_rankings(rows: tuple[MatrixPoint, ...], policy: PolicyName) -> dict[str, tuple[str, ...]]:
    """Rank configurations by value for each environment, retaining exact ties."""
    rankings: dict[str, tuple[str, ...]] = {}
    for environment in ENVIRONMENTS:
        values = {
            row.configuration: row.greedy.value if policy == "GREEDY_USE" else row.joint_dp.value
            for row in rows
            if row.environment == environment
        }
        rankings[environment] = tuple(sorted(values, key=lambda configuration: (-values[configuration], configuration)))
    return rankings
