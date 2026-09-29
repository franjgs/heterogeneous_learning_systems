"""Operational reward models."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Hashable, Mapping

from ..state import WorldState


@dataclass(frozen=True)
class CompetenceRewardModel:
    """A1 reward R(S,q,a)=c_aq as one replaceable RewardModel."""

    learner_indices: Mapping[Hashable, int]
    task_indices: Mapping[Hashable, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "learner_indices", MappingProxyType(dict(self.learner_indices)))
        object.__setattr__(self, "task_indices", MappingProxyType(dict(self.task_indices)))

    def operational_reward(
        self,
        state: WorldState,
        task: Hashable,
        operational_action: Hashable,
    ) -> float:
        return state.competence[
            self.learner_indices[operational_action]
        ][self.task_indices[task]]
