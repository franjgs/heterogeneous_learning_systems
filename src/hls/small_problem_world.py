"""Frozen Small Problem World fixture over the validated problem geometry."""

from __future__ import annotations

from dataclasses import dataclass

from .discover_v0 import DEFAULT_HORIZON
from .finite_problem_belief import uniform_prior
from .problem_geometry import (
    Problem,
    change_magnitudes,
    historical_novelties,
    production_distance,
    representational_mismatches,
    validate_problem,
)


A: Problem = (0.8, 0.2)
A_PRIME: Problem = (0.7, 0.3)
B: Problem = (0.3, 0.7)
B_PRIME: Problem = (0.2, 0.8)
C: Problem = (0.5, 0.5)

HYPOTHESIS_REPERTOIRE: tuple[Problem, ...] = (A, C, B_PRIME)
UNIFORM_PRIOR = uniform_prior(len(HYPOTHESIS_REPERTOIRE))
HORIZON = DEFAULT_HORIZON

# Frozen temporal conventions.  The fixture itself does not execute a team.
BELIEF_RESETS_EACH_PROBLEM = True
POSTERIOR_CARRIES_BETWEEN_PROBLEMS = False
STATE_PERSISTS_BETWEEN_PROBLEMS = True


@dataclass(frozen=True)
class WorldStage:
    label: str
    problem: Problem


@dataclass(frozen=True)
class WorldDescriptor:
    stage_index: int
    label: str
    problem: Problem
    p: float
    change_magnitude: float | None
    historical_novelty: float | None
    representational_mismatch: float
    represented: bool


WORLD: tuple[WorldStage, ...] = (
    WorldStage("A", A),
    WorldStage("A'", A_PRIME),
    WorldStage("B", B),
    WorldStage("B'", B_PRIME),
    WorldStage("C", C),
    WorldStage("A", A),
)

UNIQUE_WORLD_PROBLEMS: tuple[WorldStage, ...] = WORLD[:5]


def validate_frozen_world() -> None:
    """Validate the fixture without normalizing or modifying its values."""
    if HORIZON != 3:
        raise AssertionError("the frozen Small Problem World requires the existing horizon H=3")
    for stage in WORLD:
        validate_problem(stage.problem)
    for hypothesis in HYPOTHESIS_REPERTOIRE:
        validate_problem(hypothesis)
    if len(set(stage.problem for stage in UNIQUE_WORLD_PROBLEMS)) != len(UNIQUE_WORLD_PROBLEMS):
        raise AssertionError("the five declared unique problems must remain distinct")
    if WORLD[-1].problem != WORLD[0].problem:
        raise AssertionError("the final stage must exactly recur to A")


def world_descriptors() -> tuple[WorldDescriptor, ...]:
    """Derive C_t, N_t, and M_t independently without combining them."""
    validate_frozen_world()
    problems = tuple(stage.problem for stage in WORLD)
    changes = change_magnitudes(problems)
    novelties = historical_novelties(problems)
    mismatches = representational_mismatches(problems, HYPOTHESIS_REPERTOIRE)
    return tuple(
        WorldDescriptor(
            stage_index=index + 1,
            label=stage.label,
            problem=stage.problem,
            p=stage.problem[0],
            change_magnitude=changes[index],
            historical_novelty=novelties[index],
            representational_mismatch=mismatches[index],
            represented=stage.problem in HYPOTHESIS_REPERTOIRE,
        )
        for index, stage in enumerate(WORLD)
    )


def pairwise_distance_matrix() -> tuple[tuple[float, ...], ...]:
    """Return the complete d_R matrix for A, A', B, B', and C."""
    validate_frozen_world()
    return tuple(
        tuple(production_distance(left.problem, right.problem) for right in UNIQUE_WORLD_PROBLEMS)
        for left in UNIQUE_WORLD_PROBLEMS
    )
