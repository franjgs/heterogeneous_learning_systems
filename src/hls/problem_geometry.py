"""Team-independent geometry of the continuous HLS problem world."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Iterable


PROBLEM_TOLERANCE = 1e-10
OUTPUT_ENVELOPE = 3.0

Problem = tuple[float, float]
ProblemLike = Problem | float


def validate_problem(problem: Problem) -> Problem:
    """Validate a point of Delta^1 without silently normalizing it."""
    if len(problem) != 2:
        raise ValueError("a problem must contain exactly two capability weights")
    if any(not isfinite(value) or value < 0.0 for value in problem):
        raise ValueError("problem weights must be finite and non-negative")
    if not isclose(sum(problem), 1.0, rel_tol=0.0, abs_tol=PROBLEM_TOLERANCE):
        raise ValueError("problem weights must sum to one")
    return tuple(float(value) for value in problem)  # type: ignore[return-value]


def problem_from_p(p: float) -> Problem:
    """Construct z(p)=(p,1-p) for p in the closed unit interval."""
    if not isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError("p must be finite and lie in [0, 1]")
    return validate_problem((float(p), 1.0 - float(p)))


def _parameter(problem: ProblemLike) -> float:
    if isinstance(problem, (int, float)):
        return problem_from_p(float(problem))[0]
    return validate_problem(problem)[0]


def production_distance(left: ProblemLike, right: ProblemLike) -> float:
    """Closed-form normalized production-surface sup distance for rho=0.5."""
    p, q = _parameter(left), _parameter(right)
    return abs(p - q) * (1.0 + abs(p + q - 1.0))


@dataclass(frozen=True)
class NumericalSupremum:
    """Independent grid estimate of the original supremum definition."""

    distance: float
    output: tuple[float, float]
    absolute_reward_difference: float
    resolution: int


def numerical_production_supremum(
    left: ProblemLike,
    right: ProblemLike,
    *,
    resolution: int = 250,
) -> NumericalSupremum:
    """Evaluate the original supremum on a full triangular output lattice.

    This validator intentionally does not call ``production_distance``.  It
    evaluates both rho=.5 production surfaces directly at every lattice point
    satisfying Y1>=0, Y2>=0, and Y1+Y2<=3.
    """
    if resolution < 1:
        raise ValueError("resolution must be positive")
    p, q = _parameter(left), _parameter(right)
    scale = OUTPUT_ENVELOPE / resolution
    maximum = -1.0
    location = (0.0, 0.0)
    for first_index in range(resolution + 1):
        first = first_index * scale
        for second_index in range(resolution + 1 - first_index):
            second = second_index * scale
            root_first = first**0.5
            root_second = second**0.5
            reward_p = (p * root_first + (1.0 - p) * root_second) ** 2
            reward_q = (q * root_first + (1.0 - q) * root_second) ** 2
            discrepancy = abs(reward_p - reward_q)
            if discrepancy > maximum:
                maximum = discrepancy
                location = (first, second)
    return NumericalSupremum(maximum / OUTPUT_ENVELOPE, location, maximum, resolution)


def change_magnitudes(problems: Iterable[Problem]) -> tuple[float | None, ...]:
    """C_t: distance from the immediately preceding true problem."""
    sequence = tuple(validate_problem(problem) for problem in problems)
    if not sequence:
        return ()
    return (None,) + tuple(production_distance(sequence[index], sequence[index - 1]) for index in range(1, len(sequence)))


def historical_novelties(problems: Iterable[Problem]) -> tuple[float | None, ...]:
    """N_t: minimum distance to a previously encountered true problem."""
    sequence = tuple(validate_problem(problem) for problem in problems)
    if not sequence:
        return ()
    return (None,) + tuple(
        min(production_distance(sequence[index], previous) for previous in sequence[:index])
        for index in range(1, len(sequence))
    )


def representational_mismatches(
    problems: Iterable[Problem], hypotheses: Iterable[Problem]
) -> tuple[float, ...]:
    """M_t: distance from true problem to the finite represented repertoire."""
    sequence = tuple(validate_problem(problem) for problem in problems)
    represented = tuple(validate_problem(problem) for problem in hypotheses)
    if not represented:
        raise ValueError("representational mismatch requires a non-empty hypothesis set")
    return tuple(min(production_distance(problem, hypothesis) for hypothesis in represented) for problem in sequence)
