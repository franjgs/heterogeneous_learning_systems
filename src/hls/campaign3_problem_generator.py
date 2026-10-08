"""Generator-only primitives for the Campaign 3 PGCG foundation gate."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

import numpy as np

from hls.problem_geometry import production_distance


LOWER = 0.2
UPPER = 0.8
HYPOTHESES_P = (0.8, 0.5, 0.2)


def reflect(values: np.ndarray | float, lower: float = LOWER, upper: float = UPPER):
    """Reflect real values into a closed interval, including repeated overshoots."""
    if not lower < upper:
        raise ValueError("reflection interval must have positive width")
    array = np.asarray(values, dtype=float)
    width = upper - lower
    folded = np.mod(array - lower, 2.0 * width)
    result = lower + np.where(folded <= width, folded, 2.0 * width - folded)
    return float(result) if np.ndim(values) == 0 else result


def move(p, sigma: float, innovations):
    if sigma <= 0.0:
        raise ValueError("MOVE sigma must be positive")
    raw = np.asarray(p, dtype=float) + sigma * np.asarray(innovations, dtype=float)
    return reflect(raw), (raw < LOWER) | (raw > UPPER)


def simplex_lattice_degree4() -> tuple[tuple[float, float, float], ...]:
    return tuple((i / 4, j / 4, k / 4) for i in range(5) for j in range(5 - i) for k in [4 - i - j])


def executable_compositions() -> tuple[tuple[float, float, float], ...]:
    return tuple(composition for composition in simplex_lattice_degree4() if composition != (0.0, 0.0, 1.0))


def nominal_kernels(sigmas: Iterable[float]) -> tuple[tuple[float, float, float, float | None], ...]:
    kernels = []
    for stay, movement, returning in executable_compositions():
        if movement == 0.0:
            kernels.append((stay, movement, returning, None))
        else:
            kernels.extend((stay, movement, returning, float(sigma)) for sigma in sigmas)
    return tuple(kernels)


def select_scales(sigmas: tuple[float, ...], medians: tuple[float, ...]) -> tuple[int, int, int]:
    """Maximin adjacent log separation, lexicographic-index tie break."""
    if len(sigmas) != len(medians) or len(sigmas) < 3 or any(value <= 0 for value in medians):
        raise ValueError("scale selection requires aligned positive medians")
    scored = []
    for triple in combinations(range(len(sigmas)), 3):
        i, j, k = triple
        score = min(np.log(medians[j] / medians[i]), np.log(medians[k] / medians[j]))
        scored.append((float(score), triple))
    maximum = max(score for score, _ in scored)
    return min(triple for score, triple in scored if np.isclose(score, maximum, rtol=0.0, atol=1e-15))


def eligible_returns(history: Iterable[float]) -> tuple[float, ...]:
    values = tuple(float(value) for value in history)
    if not values:
        raise ValueError("RETURN requires a current problem")
    current = values[-1]
    return tuple(sorted({value for value in values[:-1] if value != current}))


@dataclass(frozen=True)
class Transition:
    p_next: float
    mechanism: str
    return_unavailable: bool
    renormalized: bool
    reflected: bool


def generator_transition(
    history: Iterable[float], kernel: tuple[float, float, float, float | None], rng: np.random.Generator
) -> Transition:
    values = tuple(float(value) for value in history)
    if not values:
        raise ValueError("history must contain p_1")
    stay, movement, returning, sigma = kernel
    if min(stay, movement, returning) < 0 or not np.isclose(stay + movement + returning, 1.0):
        raise ValueError("kernel probabilities must be nonnegative and sum to one")
    returns = eligible_returns(values)
    unavailable = not returns
    weights = np.array([stay, movement, returning if returns else 0.0], dtype=float)
    total = float(weights.sum())
    if total <= 0.0:
        raise ValueError("kernel is structurally non-initializable at this history")
    renormalized = unavailable and returning > 0.0
    mechanism_index = int(rng.choice(3, p=weights / total))
    if mechanism_index == 0:
        return Transition(values[-1], "STAY", unavailable, renormalized, False)
    if mechanism_index == 1:
        if sigma is None:
            raise ValueError("MOVE-positive kernel requires sigma")
        raw = values[-1] + float(sigma) * float(rng.normal())
        return Transition(float(reflect(raw)), "MOVE", unavailable, renormalized, raw < LOWER or raw > UPPER)
    return Transition(float(rng.choice(np.asarray(returns))), "RETURN", unavailable, renormalized, False)


def descriptor_rows(history: tuple[float, ...]):
    changes = [None] + [production_distance(history[j - 1], history[j]) for j in range(1, len(history))]
    novelties = [None] + [min(production_distance(history[j], prior) for prior in history[:j]) for j in range(1, len(history))]
    mismatches = [min(production_distance(value, hypothesis) for hypothesis in HYPOTHESES_P) for value in history]
    return changes, novelties, mismatches
