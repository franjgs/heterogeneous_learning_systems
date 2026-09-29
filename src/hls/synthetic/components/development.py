"""Competence-development kernels."""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Hashable, Mapping

from ..interfaces import DevelopmentDecision, NULL_DEVELOPMENT, Opportunity
from ..state import WorldState


@dataclass(frozen=True)
class A1SaturatingDevelopmentKernel:
    """A1 bounded update c'=c+eta(1-c), with transferable opportunity."""

    learner_indices: Mapping[Hashable, int]
    competence_indices: Mapping[Hashable, int]
    target_competence: Hashable
    eta: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.eta) or not 0.0 <= self.eta <= 1.0:
            raise ValueError("eta must lie in [0, 1]")
        learners = dict(self.learner_indices)
        competences = dict(self.competence_indices)
        if self.target_competence not in competences:
            raise ValueError("target competence is not indexed")
        object.__setattr__(self, "learner_indices", MappingProxyType(learners))
        object.__setattr__(self, "competence_indices", MappingProxyType(competences))

    def admissible_actions(
        self,
        state: WorldState,
        opportunity: Opportunity,
    ) -> tuple[DevelopmentDecision, ...]:
        del state
        if not opportunity.available:
            return (NULL_DEVELOPMENT,)
        return (NULL_DEVELOPMENT,) + tuple(
            DevelopmentDecision(learner, self.target_competence)
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
        learner_index = self.learner_indices[action.recipient]
        competence_index = self.competence_indices[action.competence]
        updated = [list(row) for row in state.competence]
        current = updated[learner_index][competence_index]
        updated[learner_index][competence_index] = current + self.eta * (1.0 - current)
        matrix = tuple(tuple(row) for row in updated)
        return state.advanced(matrix)


@dataclass(frozen=True)
class ScheduledSaturatingDevelopmentKernel:
    """The A1 update with a declared target competence for each cycle."""

    learner_indices: Mapping[Hashable, int]
    competence_indices: Mapping[Hashable, int]
    target_by_time: Mapping[int, Hashable]
    eta: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.eta) or not 0.0 <= self.eta <= 1.0:
            raise ValueError("eta must lie in [0, 1]")
        learners = dict(self.learner_indices)
        competences = dict(self.competence_indices)
        targets = dict(self.target_by_time)
        if not targets or any(time < 0 for time in targets):
            raise ValueError("development schedule must contain non-negative times")
        if any(target not in competences for target in targets.values()):
            raise ValueError("scheduled target competence is not indexed")
        object.__setattr__(self, "learner_indices", MappingProxyType(learners))
        object.__setattr__(self, "competence_indices", MappingProxyType(competences))
        object.__setattr__(self, "target_by_time", MappingProxyType(targets))

    def admissible_actions(
        self, state: WorldState, opportunity: Opportunity
    ) -> tuple[DevelopmentDecision, ...]:
        if not opportunity.available:
            return (NULL_DEVELOPMENT,)
        try:
            target = self.target_by_time[state.time]
        except KeyError as error:
            raise ValueError("development target is unidentified for this time") from error
        return (NULL_DEVELOPMENT,) + tuple(
            DevelopmentDecision(learner, target) for learner in self.learner_indices
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
        learner_index = self.learner_indices[action.recipient]
        competence_index = self.competence_indices[action.competence]
        updated = [list(row) for row in state.competence]
        current = updated[learner_index][competence_index]
        updated[learner_index][competence_index] = current + self.eta * (1.0 - current)
        return state.advanced(tuple(tuple(row) for row in updated))
