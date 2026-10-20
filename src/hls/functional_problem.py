"""Policy-independent functional assessment layered over frozen production."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping

from .discover_v0 import JOINT_ACTIONS, State, production_inputs


REQUIREMENT_TOL = 1e-12

# Frozen, balanced generalist reference used only to set a common functional
# threshold. It is not an evaluated policy or a campaign-derived estimate.
REFERENCE_TEAM: State = ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5))


@dataclass(frozen=True)
class RequirementEvaluation:
    met: bool
    deficits: tuple[float, float]
    normalized_total_deficit: float


@dataclass(frozen=True)
class FunctionalObservation:
    problem_id: int
    problem_weights: tuple[float, float]
    requirements: tuple[float, float]
    outputs: tuple[float, float]
    evaluation: RequirementEvaluation
    effort: float


def balanced_reference_requirements() -> tuple[float, float]:
    """Maximize the jointly attainable equal requirement on reference G00."""
    level = max(
        min(production_inputs(REFERENCE_TEAM, action))
        for action in JOINT_ACTIONS
    )
    return (level, level)


REFERENCE_REQUIREMENTS = balanced_reference_requirements()


def maximum_feasible_level(
    orientation: Iterable[float], *, team: State = REFERENCE_TEAM
) -> float:
    """Largest L for which r=L*z is reachable by at least one joint action."""
    z = tuple(float(value) for value in orientation)
    if len(z) != 2 or any(not isfinite(value) or value <= 0.0 for value in z):
        raise ValueError("orientation must contain two finite positive weights")
    if abs(sum(z) - 1.0) > REQUIREMENT_TOL:
        raise ValueError("orientation weights must sum to one")
    return max(
        min(output / weight for output, weight in zip(production_inputs(team, action), z))
        for action in JOINT_ACTIONS
    )


def common_feasible_level(
    orientations: Iterable[Iterable[float]], *, team: State = REFERENCE_TEAM
) -> float:
    """Maximize a shared requirement total while keeping every orientation feasible."""
    levels = tuple(maximum_feasible_level(z, team=team) for z in orientations)
    if not levels:
        raise ValueError("at least one problem orientation is required")
    return min(levels)


def requirements_from_orientation(
    orientation: Iterable[float], level: float
) -> tuple[float, float]:
    """Set r=L*z; z sets requirement direction, never threshold semantics."""
    z = tuple(float(value) for value in orientation)
    if len(z) != 2 or any(not isfinite(value) or value <= 0.0 for value in z):
        raise ValueError("orientation must contain two finite positive weights")
    if abs(sum(z) - 1.0) > REQUIREMENT_TOL:
        raise ValueError("orientation weights must sum to one")
    if not isfinite(level) or level <= 0.0:
        raise ValueError("requirement level must be finite and positive")
    return (level * z[0], level * z[1])


def evaluate_requirements(
    outputs: Iterable[float], requirements: Iterable[float]
) -> RequirementEvaluation:
    """Assess two-dimensional threshold satisfaction without changing reward.

    Deficit in each dimension is ``max(requirement - output, 0)``. The scalar
    normalized deficit is the mean of dimension-wise deficits divided by the
    corresponding positive requirement. Binary satisfaction permits only the
    fixed numerical tolerance ``REQUIREMENT_TOL``.
    """
    y = tuple(float(value) for value in outputs)
    r = tuple(float(value) for value in requirements)
    if len(y) != 2 or len(r) != 2:
        raise ValueError("outputs and requirements must each have length two")
    if any(not isfinite(value) or value < 0.0 for value in y):
        raise ValueError("outputs must be finite and non-negative")
    if any(not isfinite(value) or value <= 0.0 for value in r):
        raise ValueError("requirements must be finite and positive")
    deficits = tuple(max(required - output, 0.0) for output, required in zip(y, r))
    normalized = sum(deficit / required for deficit, required in zip(deficits, r)) / 2.0
    met = all(output + REQUIREMENT_TOL >= required for output, required in zip(y, r))
    return RequirementEvaluation(met, deficits, normalized)  # type: ignore[arg-type]


def assigned_effort(action) -> float:
    """Return total assigned agent-effort; this is not an economic cost."""
    return float(sum(sum(float(value) for value in row) for row in action))


def observe_trajectory_requirements(
    steps: Iterable[object], requirements_by_problem: Mapping[tuple[float, float], tuple[float, float]]
) -> tuple[FunctionalObservation, ...]:
    """Annotate recorded finite-belief steps without entering their simulator loop.

    The input records must expose ``problem_id``, ``true_problem``,
    ``state_before`` and ``action``. This post-hoc observer cannot affect policy,
    belief, reward, or capability transitions.
    """
    from .discover_v0 import production_inputs

    normalized = {tuple(problem): tuple(req) for problem, req in requirements_by_problem.items()}
    observations = []
    for step in steps:
        problem = tuple(step.true_problem)
        if problem not in normalized:
            raise ValueError(f"no functional requirements registered for problem {problem}")
        requirements = normalized[problem]
        outputs = production_inputs(step.state_before, step.action)
        observations.append(FunctionalObservation(
            int(step.problem_id), problem, requirements, outputs,
            evaluate_requirements(outputs, requirements), assigned_effort(step.action),
        ))
    return tuple(observations)
