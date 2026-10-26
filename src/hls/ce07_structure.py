"""CE-07 structures and pre-pilot validation, isolated from the CE-04 runner."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Iterable

import numpy as np


N_AGENTS = 12
N_FUNCTIONS = 4
HIGH = 0.9
LOW = 0.6
MARGINAL_EXACT = Fraction(27, 40)


def competence_matrices() -> tuple[np.ndarray, np.ndarray]:
    """Return the protocol's exact A/B competence matrices, rows=agents."""
    a = np.full((N_AGENTS, N_FUNCTIONS), LOW, dtype=float)
    a[:3, :] = HIGH
    b = np.full((N_AGENTS, N_FUNCTIONS), LOW, dtype=float)
    for family in range(N_FUNCTIONS):
        b[family * 3:(family + 1) * 3, family] = HIGH
    return a, b


def rename_agent_rows(matrix: np.ndarray, new_to_old: Iterable[int]) -> np.ndarray:
    """Relabel rows; permutation[new_index] gives the previous physical agent."""
    q = np.asarray(matrix)
    p = np.asarray(tuple(new_to_old), dtype=int)
    if q.ndim != 2 or p.shape != (q.shape[0],) or sorted(p.tolist()) != list(range(q.shape[0])):
        raise ValueError("new_to_old must be a permutation with one entry per agent")
    return q[p].copy()


def inverse_permutation(new_to_old: Iterable[int]) -> np.ndarray:
    p = np.asarray(tuple(new_to_old), dtype=int)
    if p.ndim != 1 or sorted(p.tolist()) != list(range(p.size)):
        raise ValueError("new_to_old must be a permutation")
    inverse = np.empty_like(p)
    inverse[p] = np.arange(p.size)
    return inverse


def validate_structures(a: np.ndarray, b: np.ndarray) -> dict:
    """Fail closed unless matrices meet the CE-07 structural invariants."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != (N_AGENTS, N_FUNCTIONS) or b.shape != a.shape:
        raise AssertionError("CE-07 matrices must both have shape 12×4")
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise AssertionError("competences must be finite")
    if not np.isin(a, [LOW, HIGH]).all() or not np.isin(b, [LOW, HIGH]).all():
        raise AssertionError("matrices must contain only approved h/l values")
    # Fraction arithmetic certifies the exact rational marginal, without
    # mistaking binary floating-point representation for scientific mismatch.
    expected = Fraction(3, 12) * Fraction(9, 10) + Fraction(9, 12) * Fraction(3, 5)
    if expected != MARGINAL_EXACT:
        raise AssertionError("internal marginal calculation is inconsistent")
    for name, q in (("A", a), ("B", b)):
        if any(Fraction(int(np.count_nonzero(q[:, k] == HIGH)), 12) * Fraction(9, 10) +
               Fraction(int(np.count_nonzero(q[:, k] == LOW)), 12) * Fraction(3, 5) != MARGINAL_EXACT
               for k in range(N_FUNCTIONS)):
            raise AssertionError(f"{name} does not have exact 27/40 marginal in every function")
        if not np.all(q.max(axis=0) == HIGH):
            raise AssertionError(f"{name} has a different maximum competence")
    profiles_a = Counter(map(tuple, a.tolist()))
    profiles_b = Counter(map(tuple, b.tolist()))
    if profiles_a == profiles_b:
        raise AssertionError("A and B are equivalent by agent-row permutation")
    if sorted(np.count_nonzero(a == HIGH, axis=1).tolist()) != [0] * 9 + [4] * 3:
        raise AssertionError("A row-profile multiset differs from the approved structure")
    if sorted(np.count_nonzero(b == HIGH, axis=1).tolist()) != [1] * 12:
        raise AssertionError("B row-profile multiset differs from the approved structure")
    return {"shape": [N_AGENTS, N_FUNCTIONS], "marginal_exact": "27/40",
            "marginal_float": 0.675, "maxima": [HIGH] * N_FUNCTIONS,
            "A_row_profile_counts": {"4_high": 3, "0_high": 9},
            "B_row_profile_counts": {"1_high": 12},
            "not_equivalent_by_agent_permutation": True}


@dataclass(frozen=True)
class CE07Config:
    seed_ids: tuple[int, int, int]
    n_agents: int = N_AGENTS
    n_functions: int = N_FUNCTIONS
    high: float = HIGH
    low: float = LOW
    horizon: float = 400.0
    arrival_rate_per_agent: float = 0.55
    task_family_probabilities: tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)
    deadline_slack: float = 3.0
    service_mean: float = 1.25
    service_cv: float = 0.30
    policy: str = "P1"
    learning: bool = False
    cooperation: bool = False
    paired_demand_and_potential_outcomes: bool = True

    def __post_init__(self):
        if len(self.seed_ids) != 3 or len(set(self.seed_ids)) != 3:
            raise ValueError("provide exactly three distinct pilot seed IDs; CE has not fixed their values")
        if self.n_agents != 12 or self.n_functions != 4 or self.policy != "P1":
            raise ValueError("configuration differs from the approved CE-07 protocol")
        if self.learning or self.cooperation:
            raise ValueError("learning and cooperation are excluded in CE-07")

    def to_dict(self) -> dict:
        result = asdict(self)
        result["seed_ids"] = list(self.seed_ids)
        result["marginal_exact"] = "27/40"
        result["organization_matrices"] = {"A": "3 rows [h,h,h,h], 9 rows [l,l,l,l]",
            "B": "3 rows high only F1; 3 high only F2; 3 high only F3; 3 high only F4"}
        return result
