"""C4 competence-interaction capability for G0.

A development action has a direct bounded update on its target competence and
may induce signed effects on other learner/competence coordinates through a
declared Gamma interaction map.

Gamma = 0 recovers independent development.
Gamma > 0 represents transfer.
Gamma < 0 represents interference.

This module defines world physics only.  It contains no policy logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Hashable, Mapping

from .interfaces import DevelopmentDecision, NULL_DEVELOPMENT, Opportunity
from .state import WorldState


Coordinate = tuple[Hashable, Hashable]
InteractionKey = tuple[Hashable, Hashable, Hashable, Hashable]


@dataclass(frozen=True)
class CoupledDevelopmentKernel:
    """Bounded development with signed cross-competence interactions.

    Direct update:
        c' = c + eta * (1-c)

    For each declared Gamma coefficient associated with the selected
    (recipient, target) action:

        gamma > 0:
            x' = x + gamma * eta * (1-x)

        gamma < 0:
            x' = x + gamma * eta * x

    Thus positive interaction transfers development toward the upper bound,
    while negative interaction produces bounded interference toward zero.
    """

    learner_indices: Mapping[Hashable, int]
    competence_indices: Mapping[Hashable, int]
    target_by_time: Mapping[int, Hashable]
    eta: float
    gamma: Mapping[InteractionKey, float]

    def __post_init__(self) -> None:
        if not math.isfinite(self.eta) or not 0.0 <= self.eta <= 1.0:
            raise ValueError("eta must lie in [0,1]")

        learners = dict(self.learner_indices)
        competences = dict(self.competence_indices)
        targets = dict(self.target_by_time)
        gamma = dict(self.gamma)

        if not targets or any(time < 0 for time in targets):
            raise ValueError("development schedule must contain non-negative times")
        if any(target not in competences for target in targets.values()):
            raise ValueError("scheduled target competence is not indexed")

        for key, coefficient in gamma.items():
            if len(key) != 4:
                raise ValueError("Gamma keys must contain four coordinates")
            src_learner, src_comp, dst_learner, dst_comp = key
            if src_learner not in learners or dst_learner not in learners:
                raise ValueError("Gamma references an unknown learner")
            if src_comp not in competences or dst_comp not in competences:
                raise ValueError("Gamma references an unknown competence")
            if not math.isfinite(coefficient) or not -1.0 <= coefficient <= 1.0:
                raise ValueError("Gamma coefficients must lie in [-1,1]")

        object.__setattr__(self, "learner_indices", MappingProxyType(learners))
        object.__setattr__(self, "competence_indices", MappingProxyType(competences))
        object.__setattr__(self, "target_by_time", MappingProxyType(targets))
        object.__setattr__(self, "gamma", MappingProxyType(gamma))

    def admissible_actions(
        self,
        state: WorldState,
        opportunity: Opportunity,
    ) -> tuple[DevelopmentDecision, ...]:
        if not opportunity.available:
            return (NULL_DEVELOPMENT,)
        try:
            target = self.target_by_time[state.time]
        except KeyError as error:
            raise ValueError("development target is unidentified for this time") from error

        return (NULL_DEVELOPMENT,) + tuple(
            DevelopmentDecision(learner, target)
            for learner in self.learner_indices
        )

    def transition(
        self,
        state: WorldState,
        opportunity: Opportunity,
        action: DevelopmentDecision,
    ) -> WorldState:
        if action not in self.admissible_actions(state, opportunity):
            raise ValueError("development action is not admissible")

        if action.is_null:
            return state.advanced(state.competence)

        recipient = action.recipient
        target = action.competence

        updated = [list(row) for row in state.competence]

        # Direct development.
        i = self.learner_indices[recipient]
        k = self.competence_indices[target]
        current = updated[i][k]
        updated[i][k] = current + self.eta * (1.0 - current)

        # Signed cross-coordinate interactions are computed from the
        # pre-transition state, avoiding order-dependent Gamma effects.
        for (
            src_learner,
            src_comp,
            dst_learner,
            dst_comp,
        ), coefficient in self.gamma.items():
            if src_learner != recipient or src_comp != target:
                continue

            di = self.learner_indices[dst_learner]
            dk = self.competence_indices[dst_comp]

            # Do not double-update the direct target itself.
            if di == i and dk == k:
                continue

            old = state.competence[di][dk]

            if coefficient >= 0.0:
                effect = coefficient * self.eta * (1.0 - old)
            else:
                effect = coefficient * self.eta * old

            updated[di][dk] = min(1.0, max(0.0, old + effect))

        return state.advanced(tuple(tuple(row) for row in updated))


def interaction_effect(
    before: WorldState,
    after: WorldState,
    learner_index: int,
    competence_index: int,
) -> float:
    """Signed observed change of one coordinate."""
    return (
        after.competence[learner_index][competence_index]
        - before.competence[learner_index][competence_index]
    )
