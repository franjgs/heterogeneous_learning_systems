"""Cost--development Pareto ledgers over the frozen G3-H action set.

This is a descriptive, purchased multiobjective representation.  It changes
neither G3-H physics nor the existing local and look-ahead evaluators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .g3_h_organizational_value import (
    G3HLearningProfile,
    development_g3h,
    dynamic_value_g3h,
    local_value_g3h,
    transition_g3h,
)
from .g3_organizational_value import G3A_ASSIGNMENTS, G3State, G3aAction, reward_g3a
from .minimal_reference_scenario import EXACT_TOL


@dataclass(frozen=True)
class CostDevelopmentAction:
    """One frozen G3-H action represented by current cost and development."""

    action: G3aAction
    reward: float
    cost: float
    development: float
    local_value: float
    dynamic_value: float
    successor: G3State
    pareto_dominated: bool


@dataclass(frozen=True)
class CostDevelopmentFrontier:
    """Exact finite action ledger and its cost--development nondominated set."""

    state: G3State
    learning_profile: G3HLearningProfile
    operational_value: float
    actions: tuple[CostDevelopmentAction, ...]
    frontier_actions: frozenset[G3aAction]
    free_development: float
    maximum_development: float
    development_requiring_sacrifice: float
    minimum_cost_of_maximum_development: float


def _nondominated(
    costs: dict[G3aAction, float],
    developments: dict[G3aAction, float],
    tolerance: float,
) -> frozenset[G3aAction]:
    """Keep actions for which no action is weakly cheaper and more developmental."""
    retained: set[G3aAction] = set()
    for action in costs:
        dominated = False
        for other in costs:
            if other == action:
                continue
            weakly_better = costs[other] <= costs[action] + tolerance and developments[other] >= developments[action] - tolerance
            strictly_better = costs[other] < costs[action] - tolerance or developments[other] > developments[action] + tolerance
            if weakly_better and strictly_better:
                dominated = True
                break
        if not dominated:
            retained.add(action)
    return frozenset(retained)


def evaluate_cost_development_frontier(
    state: G3State,
    learning_profile: G3HLearningProfile,
    *,
    actions: Sequence[G3aAction] = G3A_ASSIGNMENTS,
    tolerance: float = EXACT_TOL,
) -> CostDevelopmentFrontier:
    """Evaluate the exact Pareto set under lower current cost / higher ``D``."""
    if tolerance < 0.0:
        raise ValueError("tolerance must be non-negative")
    if set(actions) != set(G3A_ASSIGNMENTS) or len(actions) != len(G3A_ASSIGNMENTS):
        raise ValueError("actions must enumerate every G3a assignment exactly once")

    rewards = {action: reward_g3a(state, action) for action in actions}
    operational_value = max(rewards.values())
    costs = {action: operational_value - reward for action, reward in rewards.items()}
    developments = {action: development_g3h(state, action, learning_profile) for action in actions}
    frontier_actions = _nondominated(costs, developments, tolerance)
    zero_cost = tuple(action for action, cost in costs.items() if cost <= tolerance)
    maximum_development = max(developments.values())
    max_development_actions = tuple(
        action for action, development in developments.items() if maximum_development - development <= tolerance
    )
    observations = tuple(
        CostDevelopmentAction(
            action=action,
            reward=rewards[action],
            cost=costs[action],
            development=developments[action],
            local_value=local_value_g3h(state, action, learning_profile),
            dynamic_value=dynamic_value_g3h(state, action, learning_profile),
            successor=transition_g3h(state, action, learning_profile),
            pareto_dominated=action not in frontier_actions,
        )
        for action in actions
    )
    free_development = max(developments[action] for action in zero_cost)
    minimum_cost = min(costs[action] for action in max_development_actions)
    return CostDevelopmentFrontier(
        state=state,
        learning_profile=learning_profile,
        operational_value=operational_value,
        actions=observations,
        frontier_actions=frontier_actions,
        free_development=free_development,
        maximum_development=maximum_development,
        development_requiring_sacrifice=maximum_development - free_development,
        minimum_cost_of_maximum_development=minimum_cost,
    )

