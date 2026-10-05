"""Reproducible adversarial existence search within fixed G3-H physics.

The sampler is deliberately a transparent interior random search.  It is not
an estimator of regime prevalence and introduces no mechanism beyond the
existing G3-H evaluator.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log1p
from random import Random
from time import perf_counter
from typing import Literal

from .g3_h_organizational_value import G3HLearningProfile
from .g3_h_regime_map import G3HPointEvaluation, REGIME_TOL, evaluate_point
from .g3_organizational_value import G3State


SearchCondition = Literal["homogeneous", "heterogeneous"]
INTERIOR_EPSILON = 1e-6


@dataclass(frozen=True)
class SearchResult:
    """Best objective values from one fixed-condition random search stage."""

    condition: SearchCondition
    seed: int
    samples: int
    runtime_seconds: float
    state_min: float
    state_max: float
    eta_min: float
    eta_max: float
    best_use: G3HPointEvaluation
    best_local: G3HPointEvaluation
    positive_use_count: int
    positive_local_count: int


def _interior_state(rng: Random) -> G3State:
    width = 1.0 - 2.0 * INTERIOR_EPSILON
    values = tuple(INTERIOR_EPSILON + width * rng.random() for _ in range(6))
    return ((values[0], values[1]), (values[2], values[3]), (values[4], values[5]))


def _eta(rng: Random) -> float:
    """Sample an exponential variable with support on the admissible ``[0, inf)`` domain."""
    return -log1p(-rng.random())


def _learning_profile(rng: Random, condition: SearchCondition) -> G3HLearningProfile:
    if condition == "homogeneous":
        eta = _eta(rng)
        return (eta, eta, eta)
    return (_eta(rng), _eta(rng), _eta(rng))


def search(
    *,
    condition: SearchCondition,
    samples: int,
    seed: int,
) -> SearchResult:
    """Maximise both raw regrets over a transparent fixed-seed interior sample."""
    if samples <= 0:
        raise ValueError("samples must be positive")
    rng = Random(seed)
    start = perf_counter()
    best_use = None
    best_local = None
    state_min = float("inf")
    state_max = float("-inf")
    eta_min = float("inf")
    eta_max = float("-inf")
    positive_use_count = 0
    positive_local_count = 0
    for _ in range(samples):
        state = _interior_state(rng)
        profile = _learning_profile(rng, condition)
        evaluation = evaluate_point(state, profile)
        state_min = min(state_min, *(value for row in state for value in row))
        state_max = max(state_max, *(value for row in state for value in row))
        eta_min = min(eta_min, *profile)
        eta_max = max(eta_max, *profile)
        positive_use_count += evaluation.regret_use > REGIME_TOL
        positive_local_count += evaluation.regret_local > REGIME_TOL
        if best_use is None or evaluation.regret_use > best_use.regret_use:
            best_use = evaluation
        if best_local is None or evaluation.regret_local > best_local.regret_local:
            best_local = evaluation
    assert best_use is not None and best_local is not None
    return SearchResult(
        condition=condition,
        seed=seed,
        samples=samples,
        runtime_seconds=perf_counter() - start,
        state_min=state_min,
        state_max=state_max,
        eta_min=eta_min,
        eta_max=eta_max,
        best_use=best_use,
        best_local=best_local,
        positive_use_count=positive_use_count,
        positive_local_count=positive_local_count,
    )


def positive(result: SearchResult) -> bool:
    """Return whether either existence objective exceeds the project tolerance."""
    return result.best_use.regret_use > REGIME_TOL or result.best_local.regret_local > REGIME_TOL


def local_refinement(
    center: G3HPointEvaluation,
    *,
    condition: SearchCondition,
    samples: int,
    seed: int,
    state_radius: float = 0.01,
    eta_fraction_radius: float = 0.05,
) -> SearchResult:
    """Check a finite neighbourhood of a positive candidate without changing physics."""
    if samples <= 0 or state_radius <= 0.0 or eta_fraction_radius <= 0.0:
        raise ValueError("refinement parameters must be positive")
    rng = Random(seed)
    start = perf_counter()
    best_use = None
    best_local = None
    state_min = float("inf")
    state_max = float("-inf")
    eta_min = float("inf")
    eta_max = float("-inf")
    positive_use_count = 0
    positive_local_count = 0
    for _ in range(samples):
        state_values = tuple(
            min(1.0 - INTERIOR_EPSILON, max(INTERIOR_EPSILON, value + rng.uniform(-state_radius, state_radius)))
            for row in center.state
            for value in row
        )
        state: G3State = ((state_values[0], state_values[1]), (state_values[2], state_values[3]), (state_values[4], state_values[5]))
        if condition == "homogeneous":
            eta = max(0.0, center.learning_profile[0] * (1.0 + rng.uniform(-eta_fraction_radius, eta_fraction_radius)))
            profile: G3HLearningProfile = (eta, eta, eta)
        else:
            profile = tuple(
                max(0.0, eta * (1.0 + rng.uniform(-eta_fraction_radius, eta_fraction_radius)))
                for eta in center.learning_profile
            )  # type: ignore[assignment]
        evaluation = evaluate_point(state, profile)
        state_min = min(state_min, *state_values)
        state_max = max(state_max, *state_values)
        eta_min = min(eta_min, *profile)
        eta_max = max(eta_max, *profile)
        positive_use_count += evaluation.regret_use > REGIME_TOL
        positive_local_count += evaluation.regret_local > REGIME_TOL
        if best_use is None or evaluation.regret_use > best_use.regret_use:
            best_use = evaluation
        if best_local is None or evaluation.regret_local > best_local.regret_local:
            best_local = evaluation
    assert best_use is not None and best_local is not None
    return SearchResult(
        condition=condition,
        seed=seed,
        samples=samples,
        runtime_seconds=perf_counter() - start,
        state_min=state_min,
        state_max=state_max,
        eta_min=eta_min,
        eta_max=eta_max,
        best_use=best_use,
        best_local=best_local,
        positive_use_count=positive_use_count,
        positive_local_count=positive_local_count,
    )
