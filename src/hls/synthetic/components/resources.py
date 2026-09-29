"""Cost and resource-admissibility models."""

from __future__ import annotations

from dataclasses import dataclass
import math

from ..interfaces import DevelopmentDecision, Opportunity
from ..state import WorldState


@dataclass(frozen=True)
class A1ResourceModel:
    """Minimal A1 development cost and discount semantics."""

    kappa: float
    beta: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.kappa) or self.kappa < 0.0:
            raise ValueError("kappa must be finite and non-negative")
        if not math.isfinite(self.beta) or not 0.0 <= self.beta <= 1.0:
            raise ValueError("beta must lie in [0, 1]")

    def development_cost(self, action: DevelopmentDecision) -> float:
        return 0.0 if action.is_null else self.kappa

    def development_is_admissible(
        self,
        state: WorldState,
        action: DevelopmentDecision,
        opportunity: Opportunity,
    ) -> bool:
        del state
        return action.is_null or opportunity.available
