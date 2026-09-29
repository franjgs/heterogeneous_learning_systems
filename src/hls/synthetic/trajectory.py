"""Immutable trajectory records for sampled or exact synthetic worlds."""

from __future__ import annotations

from dataclasses import dataclass

from .interfaces import DevelopmentDecision, OperationalAction, Opportunity, Task
from .state import WorldState


@dataclass(frozen=True)
class TransitionRecord:
    state: WorldState
    task: Task
    operational_action: OperationalAction
    opportunity: Opportunity
    development_action: DevelopmentDecision
    operational_reward: float
    development_cost: float
    next_state: WorldState


@dataclass(frozen=True)
class Trajectory:
    transitions: tuple[TransitionRecord, ...] = ()

    def append(self, transition: TransitionRecord) -> "Trajectory":
        return Trajectory(self.transitions + (transition,))
