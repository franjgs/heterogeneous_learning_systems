"""Exact diagnostics for finite-horizon synthetic HLS problems.

Diagnostics are observational only. They do not alter world physics,
optimization semantics, or campaign definitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

from .exact import (
    EXACT_TOL,
    ExactProblem,
    _admissible_development_actions,
    _branch_value,
    _optimal_set,
    _physical_next_state,
    _task,
    _terminal_value,
)
from .interfaces import DevelopmentDecision, Opportunity
from .state import WorldState


@dataclass(frozen=True)
class ReachableHLSStateAudit:
    """Routing audit for one state reachable under an optimal HLS policy."""

    state: WorldState
    task: Hashable
    immediate_rewards: tuple[tuple[Hashable, float], ...]
    hls_action_values: tuple[tuple[Hashable, float], ...]
    greedy_actions: frozenset[Hashable]
    hls_actions: frozenset[Hashable]

    @property
    def common_actions(self) -> frozenset[Hashable]:
        return self.greedy_actions & self.hls_actions

    @property
    def has_greedy_hls_action(self) -> bool:
        return bool(self.common_actions)

    @property
    def all_hls_actions_are_greedy(self) -> bool:
        return self.hls_actions <= self.greedy_actions

    def alignment_margin(self, problem: ExactProblem) -> float | None:
        """Minimum p(a)-p(b) over strictly reward-ordered action pairs.

        Positive means every strict reward preference is aligned with
        opportunity probability. Zero is the alignment boundary. Negative
        means at least one strict reward ordering is opportunity-reversed.
        """
        environment = problem.environment
        rewards = dict(self.immediate_rewards)

        probabilities = {
            action: environment.opportunities.probability(
                self.state,
                self.task,
                action,
                (),
            )
            for action in problem.operational_actions
        }

        margins = [
            probabilities[a] - probabilities[b]
            for a in problem.operational_actions
            for b in problem.operational_actions
            if rewards[a] > rewards[b] + EXACT_TOL
        ]

        return min(margins) if margins else None

    def reducibility_margin(self) -> float | None:
        """HLS Q-value gap protecting greedy routing from non-greedy actions.

        Positive means every non-greedy action is strictly below the best
        greedy HLS Q-value. None means every action is immediately greedy.
        """
        q_values = dict(self.hls_action_values)

        non_greedy = [
            action
            for action in q_values
            if action not in self.greedy_actions
        ]
        if not non_greedy:
            return None

        best_greedy = max(
            q_values[action]
            for action in self.greedy_actions
        )

        return min(
            best_greedy - q_values[action]
            for action in non_greedy
        )


@dataclass(frozen=True)
class HLSReachabilityAudit:
    """Audit over all states reachable through optimal HLS choices."""

    states: tuple[ReachableHLSStateAudit, ...]

    @property
    def intersection_property_holds(self) -> bool:
        return all(state.has_greedy_hls_action for state in self.states)

    @property
    def subset_property_holds(self) -> bool:
        return all(state.all_hls_actions_are_greedy for state in self.states)


def _state_key(state: WorldState):
    return state.competence, state.time, state.resources


def audit_optimal_hls_reachability(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> HLSReachabilityAudit:
    """Audit every non-terminal state reachable under optimal HLS choices.

    At each reachable state:
      1. compute exact HLS Q-values for every operational action;
      2. retain every optimal operational action;
      3. for each positive-probability opportunity branch, retain every
         development decision maximizing exact continuation value;
      4. recurse to all resulting states.

    Thus ties are preserved both in routing and development.
    """

    environment = problem.environment
    start = (
        environment.initial_state()
        if initial_state is None
        else initial_state
    )

    value_cache: dict[object, float] = {}

    def value(state: WorldState) -> float:
        key = _state_key(state)
        if key in value_cache:
            return value_cache[key]

        if state.time == problem.horizon:
            result = _terminal_value(problem, state)
        elif state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")
        else:
            values = {
                action: _branch_value(problem, state, action, value)
                for action in problem.operational_actions
            }
            result = max(values.values())

        value_cache[key] = result
        return result

    audits: list[ReachableHLSStateAudit] = []
    visited: set[object] = set()

    def visit(state: WorldState) -> None:
        if state.time == problem.horizon:
            return
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        key = _state_key(state)
        if key in visited:
            return
        visited.add(key)

        task = _task(problem, state)

        rewards = {
            action: environment.reward.operational_reward(
                state,
                task,
                action,
            )
            for action in problem.operational_actions
        }

        q_values = {
            action: _branch_value(
                problem,
                state,
                action,
                value,
            )
            for action in problem.operational_actions
        }

        greedy = _optimal_set(rewards)
        hls = _optimal_set(q_values)

        audits.append(
            ReachableHLSStateAudit(
                state=state,
                task=task,
                immediate_rewards=tuple(rewards.items()),
                hls_action_values=tuple(q_values.items()),
                greedy_actions=greedy,
                hls_actions=hls,
            )
        )

        # Follow every optimal routing action.
        for action in hls:
            probability = environment.opportunities.probability(
                state,
                task,
                action,
                (),
            )

            for available, weight in (
                (False, 1.0 - probability),
                (True, probability),
            ):
                # Zero-probability branches are not reachable.
                if weight <= EXACT_TOL:
                    continue

                opportunity = Opportunity(available)
                decisions = _admissible_development_actions(
                    problem,
                    state,
                    opportunity,
                )

                if not decisions:
                    raise ValueError(
                        "world exposes no resource-admissible "
                        "development action"
                    )

                decision_values: dict[DevelopmentDecision, float] = {}

                for decision in decisions:
                    next_state = _physical_next_state(
                        problem,
                        state,
                        opportunity,
                        decision,
                    )
                    decision_values[decision] = (
                        -environment.resources.development_cost(decision)
                        + environment.resources.beta * value(next_state)
                    )

                best = max(decision_values.values())

                # Preserve every development tie belonging to an optimal
                # HLS continuation.
                for decision, decision_value in decision_values.items():
                    if abs(decision_value - best) <= EXACT_TOL:
                        next_state = _physical_next_state(
                            problem,
                            state,
                            opportunity,
                            decision,
                        )
                        visit(next_state)

    visit(start)

    return HLSReachabilityAudit(tuple(audits))
