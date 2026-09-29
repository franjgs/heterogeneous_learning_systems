"""C3 scarce development resources for the G0 synthetic environment.

C3 adds trajectory-persistent development budgets without policy logic.
Resource availability is physical world state. Development consumes budget;
null development does not.

Budget consumption and objective development cost are distinct quantities.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .interfaces import DevelopmentDecision, Opportunity
from .state import WorldState


BUDGET_KEY = "development_budget"
C3_TOL = 1e-12


def with_development_budget(state: WorldState, budget: float) -> WorldState:
    if not math.isfinite(budget) or budget < 0.0:
        raise ValueError("development budget must be finite and non-negative")
    resources = dict(state.resources)
    resources[BUDGET_KEY] = float(budget)
    return WorldState(
        competence=state.competence,
        time=state.time,
        resources=tuple(sorted(resources.items())),
    )


def remaining_budget(state: WorldState) -> float:
    resources = dict(state.resources)
    try:
        return resources[BUDGET_KEY]
    except KeyError as error:
        raise ValueError(
            "development budget is not declared in world state"
        ) from error


@dataclass(frozen=True)
class BudgetedDevelopmentResources:
    """Finite development budget with a separate objective penalty.

    ``budget_per_development`` is the amount of the persistent C3 budget
    consumed by one non-null development action.

    ``objective_cost_per_development`` is the optional penalty subtracted
    from the optimization objective for that action. It is independent of
    budget consumption.
    """

    budget_per_development: float
    objective_cost_per_development: float = 0.0
    beta: float = 1.0

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.budget_per_development)
            or self.budget_per_development <= 0.0
        ):
            raise ValueError(
                "development budget consumption must be finite "
                "and strictly positive"
            )
        if (
            not math.isfinite(self.objective_cost_per_development)
            or self.objective_cost_per_development < 0.0
        ):
            raise ValueError(
                "objective development cost must be finite and non-negative"
            )
        if not math.isfinite(self.beta) or not 0.0 <= self.beta <= 1.0:
            raise ValueError("beta must lie in [0,1]")

    def development_cost(self, action: DevelopmentDecision) -> float:
        if action.is_null:
            return 0.0
        return self.objective_cost_per_development

    def development_is_admissible(
        self,
        state: WorldState,
        action: DevelopmentDecision,
        opportunity: Opportunity,
    ) -> bool:
        if action.is_null:
            return True
        return (
            opportunity.available
            and remaining_budget(state) + C3_TOL
            >= self.budget_per_development
        )

    def consume(
        self,
        state: WorldState,
        action: DevelopmentDecision,
    ) -> tuple[tuple[str, float], ...]:
        if action.is_null:
            return state.resources

        budget = remaining_budget(state)
        if budget + C3_TOL < self.budget_per_development:
            raise ValueError("development action exceeds remaining budget")

        resources = dict(state.resources)
        resources[BUDGET_KEY] = max(
            0.0,
            budget - self.budget_per_development,
        )
        return tuple(sorted(resources.items()))
