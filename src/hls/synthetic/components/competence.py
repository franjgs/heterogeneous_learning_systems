"""Competence-state implementations."""

from __future__ import annotations

from dataclasses import dataclass

from ..state import CompetenceMatrix, WorldState


@dataclass(frozen=True)
class BoundedMatrixCompetence:
    """Bounded scalar competence matrix with arbitrary M and K."""

    initial: CompetenceMatrix
    lower: float = 0.0
    upper: float = 1.0

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("competence lower bound exceeds upper bound")
        self.validate(WorldState(self.initial))

    def initial_state(self) -> WorldState:
        return WorldState(self.initial)

    def validate(self, state: WorldState) -> None:
        if (
            state.n_learners != len(self.initial)
            or state.n_competences != len(self.initial[0])
        ):
            raise ValueError("competence state shape differs from the declared model")
        if any(
            not self.lower <= value <= self.upper
            for row in state.competence
            for value in row
        ):
            raise ValueError("competence lies outside declared bounds")
