"""C2 collective portfolio geometry for the G0 synthetic environment.

C2 adds policy-neutral construction and diagnosis of competence geometries with
arbitrary M and K.  Geometry labels are never stored in the generated world:
diagnostics are derived independently from the competence matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .components import BoundedMatrixCompetence
from .state import CompetenceMatrix, WorldState


C2_TOL = 1e-12


@dataclass(frozen=True)
class PortfolioGeometry:
    """Derived collective properties of a competence matrix."""

    n_learners: int
    n_competences: int
    task_best: tuple[float, ...]
    task_best_sets: tuple[frozenset[int], ...]
    globally_dominant: frozenset[int]
    dominated_learners: frozenset[int]
    redundant_pairs: frozenset[tuple[int, int]]
    specialist_tasks: tuple[frozenset[int], ...]
    uncovered_tasks: frozenset[int]
    collective_coverage: float

    @property
    def has_global_dominance(self) -> bool:
        return bool(self.globally_dominant)

    @property
    def has_redundancy(self) -> bool:
        return bool(self.redundant_pairs)

    @property
    def has_specialization(self) -> bool:
        winners = set()
        for best in self.task_best_sets:
            if len(best) == 1:
                winners.update(best)
        return len(winners) >= 2

    @property
    def has_collective_complementarity(self) -> bool:
        """No single learner attains the collective best on every task."""
        return not self.globally_dominant and self.n_competences > 1


def _validate_threshold(threshold: float) -> None:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("coverage threshold must lie in [0,1]")


def diagnose_geometry(
    competence: CompetenceMatrix,
    *,
    coverage_threshold: float = 0.75,
    tol: float = C2_TOL,
) -> PortfolioGeometry:
    """Derive portfolio geometry directly from C, independently of its origin."""
    _validate_threshold(coverage_threshold)
    state = WorldState(competence)
    matrix = state.competence
    m = state.n_learners
    k = state.n_competences

    task_best = tuple(max(matrix[i][j] for i in range(m)) for j in range(k))
    task_best_sets = tuple(
        frozenset(
            i for i in range(m)
            if abs(matrix[i][j] - task_best[j]) <= tol
        )
        for j in range(k)
    )

    # Weak Pareto dominance across all competence dimensions, with at least
    # one strict dimension.  Equality is redundancy, not dominance.
    dominated = set()
    for victim in range(m):
        for challenger in range(m):
            if challenger == victim:
                continue
            weak = all(
                matrix[challenger][j] >= matrix[victim][j] - tol
                for j in range(k)
            )
            strict = any(
                matrix[challenger][j] > matrix[victim][j] + tol
                for j in range(k)
            )
            if weak and strict:
                dominated.add(victim)
                break

    # A globally dominant learner attains the portfolio maximum on every task.
    globally_dominant = frozenset(
        i for i in range(m)
        if all(i in task_best_sets[j] for j in range(k))
    )

    redundant_pairs = frozenset(
        (i, j)
        for i, j in combinations(range(m), 2)
        if all(abs(matrix[i][q] - matrix[j][q]) <= tol for q in range(k))
    )

    specialist_tasks = tuple(
        frozenset(
            j for j in range(k)
            if len(task_best_sets[j]) == 1 and i in task_best_sets[j]
        )
        for i in range(m)
    )

    uncovered = frozenset(
        j for j, best in enumerate(task_best)
        if best < coverage_threshold - tol
    )
    coverage = sum(best >= coverage_threshold - tol for best in task_best) / k

    return PortfolioGeometry(
        n_learners=m,
        n_competences=k,
        task_best=task_best,
        task_best_sets=task_best_sets,
        globally_dominant=globally_dominant,
        dominated_learners=frozenset(dominated),
        redundant_pairs=redundant_pairs,
        specialist_tasks=specialist_tasks,
        uncovered_tasks=uncovered,
        collective_coverage=coverage,
    )


def relabel_competence(
    competence: CompetenceMatrix,
    *,
    learner_order: tuple[int, ...] | None = None,
    competence_order: tuple[int, ...] | None = None,
) -> CompetenceMatrix:
    """Physically relabel learners and/or competence dimensions."""
    state = WorldState(competence)
    m, k = state.n_learners, state.n_competences

    learner_order = learner_order or tuple(range(m))
    competence_order = competence_order or tuple(range(k))

    if sorted(learner_order) != list(range(m)):
        raise ValueError("learner_order must be a permutation")
    if sorted(competence_order) != list(range(k)):
        raise ValueError("competence_order must be a permutation")

    return tuple(
        tuple(competence[i][j] for j in competence_order)
        for i in learner_order
    )


def reference_matrices() -> dict[str, CompetenceMatrix]:
    """Exact M=3, K=4 reference geometries for the C2 acceptance gate."""
    return {
        # M1 is best on every task; M2 and M3 are Pareto dominated.
        "dominance": (
            (0.90, 0.90, 0.90, 0.90),
            (0.70, 0.80, 0.60, 0.70),
            (0.60, 0.70, 0.80, 0.60),
        ),

        # M1 and M2 are exactly redundant.
        "redundancy": (
            (0.80, 0.70, 0.60, 0.50),
            (0.80, 0.70, 0.60, 0.50),
            (0.40, 0.50, 0.80, 0.90),
        ),

        # Different learners uniquely lead different competence dimensions.
        "specialization": (
            (0.95, 0.30, 0.40, 0.35),
            (0.30, 0.95, 0.35, 0.40),
            (0.40, 0.35, 0.95, 0.90),
        ),

        # Full collective coverage at threshold .75, but no learner covers all.
        "complementarity": (
            (0.90, 0.85, 0.30, 0.25),
            (0.25, 0.30, 0.90, 0.85),
            (0.60, 0.55, 0.60, 0.55),
        ),

        # Task/competence 4 is weak for the complete portfolio.
        "collective_gap": (
            (0.90, 0.40, 0.40, 0.50),
            (0.40, 0.90, 0.40, 0.55),
            (0.40, 0.40, 0.90, 0.60),
        ),

        # Mixed non-dominated geometry: no learner globally dominates.
        "mixed_nondominated": (
            (0.90, 0.55, 0.70, 0.45),
            (0.65, 0.90, 0.45, 0.70),
            (0.50, 0.60, 0.90, 0.80),
        ),
    }


def reference_models() -> dict[str, BoundedMatrixCompetence]:
    """Expose C2 reference geometries through the existing G0 competence model."""
    return {
        name: BoundedMatrixCompetence(matrix)
        for name, matrix in reference_matrices().items()
    }
