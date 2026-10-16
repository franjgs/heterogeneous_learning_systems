"""Dimension-independent additive production, evaluation and legacy P0 rules."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite

from .discover_v0 import RHO
from .hls_lab_nk_geometry import ProblemSpecNK, ProductiveAllocationNK

TOL = 1e-12


@dataclass(frozen=True)
class FunctionalResultNK:
    success: bool
    deficits: tuple[float, ...]
    normalized_deficit: float
    margin: float


def productive_outputs_nk(
    competence: tuple[tuple[float, ...], ...],
    allocation: ProductiveAllocationNK,
) -> tuple[float, ...]:
    """Compute the existing additive production equation, in agent order."""
    if not competence or len(competence) != len(allocation):
        raise ValueError("competence and allocation must have the same non-zero N")
    k = len(competence[0])
    if not k or any(len(row) != k for row in competence):
        raise ValueError("competence must be a non-empty rectangular N×K matrix")
    if any(len(row) != k for row in allocation):
        raise ValueError("allocation must have the same K as competence")
    if any(not isfinite(value) or not 0 <= value <= 1
           for row in competence for value in row):
        raise ValueError("competence values must be finite and lie in [0, 1]")
    if any(not isfinite(value) or value < 0 for row in allocation for value in row):
        raise ValueError("productive effort must be finite and non-negative")
    return tuple(sum(allocation[i][skill] * competence[i][skill]
                     for i in range(len(competence))) for skill in range(k))


def evaluate_problem_nk(
    outputs: tuple[float, ...], requirements: tuple[float, ...]
) -> FunctionalResultNK:
    """Generalize v1's success/deficit/margin observer dimensionally."""
    if not outputs or len(outputs) != len(requirements):
        raise ValueError("outputs and requirements must be equal non-empty K-vectors")
    if (any(not isfinite(value) or value < 0 for value in outputs)
            or any(not isfinite(value) or value < 0 for value in requirements)
            or not any(requirements)):
        raise ValueError("outputs and requirements must be finite non-negative vectors with a positive requirement")
    deficits = tuple(max(0.0, requirement - output)
                     for output, requirement in zip(outputs, requirements))
    active = tuple(i for i, requirement in enumerate(requirements) if requirement > 0)
    normalized_deficit = sum(deficits[i] / requirements[i] for i in active)
    margin = min(outputs[i] - requirements[i] for i in active)
    success = all(outputs[i] + TOL >= requirements[i] for i in active)
    return FunctionalResultNK(success, deficits, normalized_deficit, margin)


def ces_reward_nk(
    outputs: tuple[float, ...],
    weights: tuple[float, ...],
    *,
    rho: float = RHO,
) -> float:
    """Dimension-generic form of DISCOVER-v0's CES definition."""
    if not outputs or len(outputs) != len(weights):
        raise ValueError("outputs and CES weights must be equal non-empty K-vectors")
    if not isfinite(rho) or rho == 0:
        raise ValueError("rho must be finite and nonzero")
    if any(not isfinite(value) or value < 0 for value in outputs):
        raise ValueError("CES outputs must be finite and non-negative")
    if (any(not isfinite(weight) or weight < 0 for weight in weights)
            or not isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-10)):
        raise ValueError("CES weights must be finite, non-negative and sum to one")
    return sum(weight * output**rho for weight, output in zip(weights, outputs)) ** (1.0 / rho)


def p0_rank_nk(
    allocation: ProductiveAllocationNK,
    estimated_competencies: tuple[tuple[float, ...], ...],
    problem: ProblemSpecNK,
) -> tuple[float, float, float, float]:
    """Exact legacy P0 lexicographic ordering; CES is not part of the score."""
    outputs = productive_outputs_nk(estimated_competencies, allocation)
    result = evaluate_problem_nk(outputs, problem.requirements)
    effort = sum(sum(row) for row in allocation)
    return (int(result.success), -result.normalized_deficit, result.margin, -effort)


def choose_p0_action_nk(
    feasible_actions: tuple[ProductiveAllocationNK, ...],
    estimated_competencies: tuple[tuple[float, ...], ...],
    problem: ProblemSpecNK,
) -> tuple[int, ProductiveAllocationNK]:
    """Select the first action attaining the best legacy P0 tuple."""
    if not feasible_actions:
        raise ValueError("P0 requires at least one feasible productive action")
    ranked = tuple((p0_rank_nk(action, estimated_competencies, problem), index, action)
                   for index, action in enumerate(feasible_actions))
    best_rank = max(row[0] for row in ranked)
    _, action_id, action = next(row for row in ranked if row[0] == best_rank)
    return action_id, action


@dataclass(frozen=True)
class P0ProductionOnlyNK:
    """Dimension-independent implementation of the existing P0 ranking."""

    name: str = "P0_PRODUCTION_ONLY_NK"

    def choose(
        self,
        feasible_actions: tuple[ProductiveAllocationNK, ...],
        estimated_competencies: tuple[tuple[float, ...], ...],
        problem: ProblemSpecNK,
    ) -> tuple[int, ProductiveAllocationNK]:
        return choose_p0_action_nk(feasible_actions, estimated_competencies, problem)
