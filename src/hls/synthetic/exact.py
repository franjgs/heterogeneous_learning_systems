"""Policy-neutral exact finite-horizon solvers for synthetic HLS worlds.

This module generalizes the exact dynamic recursion first exercised by C1.
It contains no RQ0 campaign parameters and no reference-world-specific logic.

Three comparison architectures are represented:

HLS
    Operational routing and development are optimized jointly through exact
    continuation value.

Strong SEP
    Routing is restricted to actions maximizing immediate operational reward.
    Conditional on that routing choice and realized opportunity, development
    is optimized exactly. Routing ties are preserved as value bounds.

SEP-Omega
    Routing receives exact continuation value. It therefore provides the
    constructive reducibility boundary and is solved independently from HLS.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping, Sequence

from .environment import SyntheticEnvironment
from .interfaces import DevelopmentDecision, Opportunity
from .state import WorldState


EXACT_TOL = 1e-12


@dataclass(frozen=True)
class ExactProblem:
    """Finite-horizon exact synthetic-world problem."""

    environment: SyntheticEnvironment
    operational_actions: tuple[Hashable, ...]
    horizon: int
    terminal_task: Hashable

    def __post_init__(self) -> None:
        if not self.operational_actions:
            raise ValueError("at least one operational action is required")
        if self.horizon < 1:
            raise ValueError("horizon must be positive")


@dataclass(frozen=True)
class ExactDynamicSolution:
    value: float
    optimal_actions: frozenset[Hashable]
    action_values: Mapping[Hashable, float]


@dataclass(frozen=True)
class ExactStrongSEPSolution:
    value_min: float
    value_max: float
    immediate_optimal_actions: frozenset[Hashable]
    action_value_bounds: Mapping[Hashable, tuple[float, float]]


def _optimal_set(
    values: Mapping[Hashable, float],
) -> frozenset[Hashable]:
    best = max(values.values())
    return frozenset(
        action
        for action, value in values.items()
        if abs(value - best) <= EXACT_TOL
    )


def _task(problem: ExactProblem, state: WorldState):
    """Resolve the task exactly.

    Exact solvers require task_at semantics. Stochastic task demand belongs
    to a separate exact integration problem and is not silently sampled here.
    """
    return problem.environment.tasks.task_at(
        state.time,
        state,
        (),
    )


def _terminal_value(
    problem: ExactProblem,
    state: WorldState,
) -> float:
    environment = problem.environment
    return max(
        environment.reward.operational_reward(
            state,
            problem.terminal_task,
            action,
        )
        for action in problem.operational_actions
    )


def _physical_next_state(
    problem: ExactProblem,
    state: WorldState,
    opportunity: Opportunity,
    decision: DevelopmentDecision,
) -> WorldState:
    """Apply G0 development and persistent resource physics exactly."""
    environment = problem.environment

    if not environment.resources.development_is_admissible(
        state,
        decision,
        opportunity,
    ):
        raise ValueError("development action violates resource semantics")

    developed = environment.development.transition(
        state,
        opportunity,
        decision,
    )
    resources = environment.resources.consume(state, decision)

    next_state = WorldState(
        competence=developed.competence,
        time=developed.time,
        resources=resources,
    )
    environment.competence.validate(next_state)
    return next_state


def _admissible_development_actions(
    problem: ExactProblem,
    state: WorldState,
    opportunity: Opportunity,
) -> tuple[DevelopmentDecision, ...]:
    environment = problem.environment
    return tuple(
        decision
        for decision in environment.development.admissible_actions(
            state,
            opportunity,
        )
        if environment.resources.development_is_admissible(
            state,
            decision,
            opportunity,
        )
    )


def _branch_value(
    problem: ExactProblem,
    state: WorldState,
    action: Hashable,
    continuation,
) -> float:
    environment = problem.environment
    task = _task(problem, state)

    reward = environment.reward.operational_reward(
        state,
        task,
        action,
    )
    probability = environment.opportunities.probability(
        state,
        task,
        action,
        (),
    )

    expected = 0.0

    for available, weight in (
        (False, 1.0 - probability),
        (True, probability),
    ):
        if weight <= 0.0:
            continue

        opportunity = Opportunity(available)
        decisions = _admissible_development_actions(
            problem,
            state,
            opportunity,
        )

        if not decisions:
            raise ValueError(
                "world exposes no resource-admissible development action"
            )

        development_values = []

        for decision in decisions:
            next_state = _physical_next_state(
                problem,
                state,
                opportunity,
                decision,
            )
            development_values.append(
                -environment.resources.development_cost(decision)
                + environment.resources.beta * continuation(next_state)
            )

        expected += weight * max(development_values)

    return reward + expected


def _branch_bounds(
    problem: ExactProblem,
    state: WorldState,
    action: Hashable,
    continuation,
) -> tuple[float, float]:
    """Propagate strong-SEP bounds without resolving routing ties."""
    environment = problem.environment
    task = _task(problem, state)

    reward = environment.reward.operational_reward(
        state,
        task,
        action,
    )
    probability = environment.opportunities.probability(
        state,
        task,
        action,
        (),
    )

    expected_min = 0.0
    expected_max = 0.0

    for available, weight in (
        (False, 1.0 - probability),
        (True, probability),
    ):
        if weight <= 0.0:
            continue

        opportunity = Opportunity(available)
        decisions = _admissible_development_actions(
            problem,
            state,
            opportunity,
        )

        if not decisions:
            raise ValueError(
                "world exposes no resource-admissible development action"
            )

        development_bounds = []

        for decision in decisions:
            next_state = _physical_next_state(
                problem,
                state,
                opportunity,
                decision,
            )
            downstream_min, downstream_max = continuation(next_state)
            cost = environment.resources.development_cost(decision)

            development_bounds.append(
                (
                    -cost
                    + environment.resources.beta * downstream_min,
                    -cost
                    + environment.resources.beta * downstream_max,
                )
            )

        expected_min += weight * max(
            bound[0] for bound in development_bounds
        )
        expected_max += weight * max(
            bound[1] for bound in development_bounds
        )

    return reward + expected_min, reward + expected_max


def solve_exact_hls(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> ExactDynamicSolution:
    """Solve the exact joint HLS recursion."""

    def value(state: WorldState) -> float:
        if state.time == problem.horizon:
            return _terminal_value(problem, state)
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        values = {
            action: _branch_value(
                problem,
                state,
                action,
                value,
            )
            for action in problem.operational_actions
        }
        return max(values.values())

    state = (
        problem.environment.initial_state()
        if initial_state is None
        else initial_state
    )

    action_values = {
        action: _branch_value(
            problem,
            state,
            action,
            value,
        )
        for action in problem.operational_actions
    }

    return ExactDynamicSolution(
        value=max(action_values.values()),
        optimal_actions=_optimal_set(action_values),
        action_values=action_values,
    )


def solve_exact_strong_sep(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> ExactStrongSEPSolution:
    """Solve strong SEP with exact development and unresolved routing ties."""

    def bounds(state: WorldState) -> tuple[float, float]:
        if state.time == problem.horizon:
            terminal = _terminal_value(problem, state)
            return terminal, terminal
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        task = _task(problem, state)
        rewards = {
            action: problem.environment.reward.operational_reward(
                state,
                task,
                action,
            )
            for action in problem.operational_actions
        }

        immediate = _optimal_set(rewards)

        action_bounds = {
            action: _branch_bounds(
                problem,
                state,
                action,
                bounds,
            )
            for action in immediate
        }

        return (
            min(pair[0] for pair in action_bounds.values()),
            max(pair[1] for pair in action_bounds.values()),
        )

    state = (
        problem.environment.initial_state()
        if initial_state is None
        else initial_state
    )

    task = _task(problem, state)
    rewards = {
        action: problem.environment.reward.operational_reward(
            state,
            task,
            action,
        )
        for action in problem.operational_actions
    }

    immediate = _optimal_set(rewards)

    action_bounds = {
        action: _branch_bounds(
            problem,
            state,
            action,
            bounds,
        )
        for action in immediate
    }

    return ExactStrongSEPSolution(
        value_min=min(pair[0] for pair in action_bounds.values()),
        value_max=max(pair[1] for pair in action_bounds.values()),
        immediate_optimal_actions=immediate,
        action_value_bounds=action_bounds,
    )


def solve_exact_sep_omega(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> ExactDynamicSolution:
    """Solve SEP-Omega independently with exact continuation information."""

    def value(state: WorldState) -> float:
        if state.time == problem.horizon:
            return _terminal_value(problem, state)
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        values = {
            action: _branch_value(
                problem,
                state,
                action,
                value,
            )
            for action in problem.operational_actions
        }
        return max(values.values())

    state = (
        problem.environment.initial_state()
        if initial_state is None
        else initial_state
    )

    action_values = {
        action: _branch_value(
            problem,
            state,
            action,
            value,
        )
        for action in problem.operational_actions
    }

    return ExactDynamicSolution(
        value=max(action_values.values()),
        optimal_actions=_optimal_set(action_values),
        action_values=action_values,
    )
