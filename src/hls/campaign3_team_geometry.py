"""Pure quotient geometry for Campaign 3 team-space design characterization."""

from __future__ import annotations

from itertools import permutations
from math import isfinite
from typing import Iterable

import numpy as np


TEAM_TOLERANCE = 1e-12
ROW_PERMUTATIONS = tuple(permutations(range(3)))
Team = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]


def validate_team(team: Iterable[Iterable[float]]) -> Team:
    rows = tuple(tuple(float(value) for value in row) for row in team)
    if len(rows) != 3 or any(len(row) != 2 for row in rows):
        raise ValueError("team must be a 3x2 matrix")
    if any(not isfinite(value) or value < 0.0 or value > 1.0 for row in rows for value in row):
        raise ValueError("team entries must be finite and lie in [0,1]")
    if any(abs(sum(row[k] for row in rows) - 1.5) > TEAM_TOLERANCE for k in range(2)):
        raise ValueError("each capability column must sum to 1.5")
    return rows  # type: ignore[return-value]


def canonical_team(team: Iterable[Iterable[float]]) -> Team:
    """Lexicographically least row-major flattening over all common row permutations."""
    rows = validate_team(team)
    candidates = [tuple(rows[index] for index in permutation) for permutation in ROW_PERMUTATIONS]
    return min(candidates, key=lambda candidate: tuple(value for row in candidate for value in row))  # type: ignore[return-value]


def team_distance(left: Iterable[Iterable[float]], right: Iterable[Iterable[float]]) -> float:
    a, b = np.asarray(validate_team(left)), np.asarray(validate_team(right))
    return float(min(np.linalg.norm(a - b[list(permutation)], ord="fro") for permutation in ROW_PERMUTATIONS))


def _radical_inverse(indices: np.ndarray, base: int) -> np.ndarray:
    values = np.zeros(len(indices), dtype=float)
    factor = 1.0 / base
    work = indices.copy()
    while np.any(work):
        values += factor * (work % base)
        work //= base
        factor /= base
    return values


def shifted_halton(count: int, seed: int) -> np.ndarray:
    """Four-dimensional Halton sequence with a seeded Cranley-Patterson shift."""
    if count < 1:
        raise ValueError("count must be positive")
    indices = np.arange(1, count + 1, dtype=np.int64)
    points = np.column_stack([_radical_inverse(indices, base) for base in (2, 3, 5, 7)])
    shift = np.random.default_rng(seed).uniform(size=4)
    return np.mod(points + shift, 1.0)


def constrained_pool(raw_count: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Filter low-discrepancy coordinates through the exact two column slices."""
    raw = shifted_halton(raw_count, seed)
    valid = ((raw[:, 0] + raw[:, 1] >= 0.5) & (raw[:, 0] + raw[:, 1] <= 1.5)
             & (raw[:, 2] + raw[:, 3] >= 0.5) & (raw[:, 2] + raw[:, 3] <= 1.5))
    coordinates = raw[valid]
    teams = np.empty((len(coordinates), 3, 2), dtype=float)
    teams[:, 0, 0], teams[:, 1, 0] = coordinates[:, 0], coordinates[:, 1]
    teams[:, 2, 0] = 1.5 - coordinates[:, 0] - coordinates[:, 1]
    teams[:, 0, 1], teams[:, 1, 1] = coordinates[:, 2], coordinates[:, 3]
    teams[:, 2, 1] = 1.5 - coordinates[:, 2] - coordinates[:, 3]
    canonical = np.asarray([canonical_team(team) for team in teams])
    flattened = canonical.reshape(len(canonical), 6)
    _, first = np.unique(flattened, axis=0, return_index=True)
    return teams, canonical[np.sort(first)]


def distances_to_team(pool: np.ndarray, team: np.ndarray) -> np.ndarray:
    return np.min(
        np.stack([np.linalg.norm(pool - team[list(permutation)], axis=(1, 2)) for permutation in ROW_PERMUTATIONS]),
        axis=0,
    )


def pairwise_distances(teams: np.ndarray) -> np.ndarray:
    values = []
    for index in range(len(teams) - 1):
        values.extend(distances_to_team(teams[index + 1 :], teams[index]))
    return np.asarray(values)


def farthest_point_sequence(pool: np.ndarray, anchors: np.ndarray, total: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Anchor-initialized deterministic farthest-point selection."""
    if total < len(anchors):
        raise ValueError("total cannot be smaller than anchor count")
    selected = [np.asarray(team) for team in anchors]
    nearest = np.full(len(pool), np.inf)
    for team in selected:
        nearest = np.minimum(nearest, distances_to_team(pool, team))
    insertion = [float("nan")] * len(selected)
    radii = [float(nearest.max())]
    while len(selected) < total:
        maximum = float(nearest.max())
        tied = np.flatnonzero(nearest == maximum)
        chosen = min(tied, key=lambda index: tuple(pool[index].ravel()))
        team = pool[chosen].copy()
        selected.append(team)
        insertion.append(maximum)
        nearest = np.minimum(nearest, distances_to_team(pool, team))
        radii.append(float(nearest.max()))
    return np.asarray(selected), np.asarray(insertion), np.asarray(radii)


def boundary_clearance(teams: np.ndarray) -> np.ndarray:
    return np.min(np.minimum(teams, 1.0 - teams), axis=(1, 2))
