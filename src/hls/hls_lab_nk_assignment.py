"""One-to-one N×K assignment using SciPy's linear-sum-assignment solver.

This is an organization component for the discrete unit-effort matching
subproblem. It does not replace the general fractional N×K action catalog.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import floor, isfinite
from time import perf_counter
from typing import Sequence

import scipy
from scipy.optimize import linear_sum_assignment

from .hls_lab_nk_geometry import (
    OrganizationConfigNK,
    OrganizationResourcesNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    validate_productive_allocation_nk,
)

TOL = 1e-12
ResourcesNK = OrganizationConfigNK | OrganizationResourcesNK


@dataclass(frozen=True)
class BipartiteAssignmentResultNK:
    allocation: ProductiveAllocationNK
    matches: tuple[tuple[int, int], ...]
    objective_value: float
    resource_used: float
    elapsed_seconds: float
    maximize: bool
    solver: str = "scipy.optimize.linear_sum_assignment"
    scipy_version: str = scipy.__version__


class HungarianAssignmentOptimizerNK:
    """Optimize unit assignments subject to one-to-one/resource constraints.

    For maximum reward, assignments are optional and the optimizer considers
    every feasible cardinality from zero to the unit-resource limit. For
    minimum cost, every vertex on the smaller side must be matched, following
    the conventional rectangular assignment problem; infeasible coverage is
    reported instead of silently dropping agents/tasks.

    SciPy's maintained ``linear_sum_assignment`` backend solves the same
    linear assignment optimization problem using a modified Jonker–Volgenant
    implementation. It is not a source-code implementation of Kuhn's 1955
    Hungarian procedure; this component integrates the published assignment
    formulation with a trusted equivalent optimizer.
    """

    name = "HUNGARIAN_LINEAR_ASSIGNMENT_NK"

    def optimize(
        self,
        values: Sequence[Sequence[float]],
        organization: ResourcesNK,
        problem: ProblemSpecNK,
        *,
        maximize: bool = True,
    ) -> BipartiteAssignmentResultNK:
        """Return a feasible unit matching maximizing rewards or minimizing costs."""
        matrix = self._validate(values, organization, problem)
        n, k = len(organization.agent_ids), len(organization.skill_ids)
        budget = min(organization.collective_effort_budget, problem.resource_budget)
        eligible_agents = tuple(i for i, limit in enumerate(organization.effort_limits)
                                if limit + TOL >= 1.0)
        max_cardinality = min(n, k, len(eligible_agents), floor(budget + TOL))
        if not maximize:
            required = min(n, k)
            if max_cardinality < required:
                raise ValueError("minimum-cost full assignment exceeds the unit resource budget")
            cardinalities = (required,)
        else:
            cardinalities = tuple(range(max_cardinality + 1))

        start = perf_counter()
        candidates: list[tuple[float, tuple[tuple[int, int], ...]]] = []
        for cardinality in cardinalities:
            matches = self._solve_exact_cardinality(
                matrix, cardinality, eligible_agents, maximize=maximize,
            )
            if matches is None:
                continue
            value = sum(matrix[i][j] for i, j in matches)
            candidates.append((value, matches))
        if not candidates:
            raise ValueError("no feasible one-to-one assignment exists")

        # Stable tie rule: objective first, then fewer resources for optional
        # reward maximization, then lexicographic edge order.
        if maximize:
            best_value = max(value for value, _ in candidates)
            tied = [(value, edges) for value, edges in candidates
                    if abs(value - best_value) <= TOL]
            _, selected = min(tied, key=lambda item: (len(item[1]), item[1]))
        else:
            best_value = min(value for value, _ in candidates)
            tied = [(value, edges) for value, edges in candidates
                    if abs(value - best_value) <= TOL]
            _, selected = min(tied, key=lambda item: item[1])

        allocation = [[0.0] * k for _ in range(n)]
        for agent, task in selected:
            allocation[agent][task] = 1.0
        allocation_tuple = tuple(tuple(row) for row in allocation)
        if not validate_productive_allocation_nk(allocation_tuple, organization, problem):
            raise AssertionError("assignment optimizer returned an action outside the N×K resource contract")
        if (len({i for i, _ in selected}) != len(selected)
                or len({j for _, j in selected}) != len(selected)):
            raise AssertionError("assignment optimizer violated one-to-one matching")
        return BipartiteAssignmentResultNK(
            allocation=allocation_tuple,
            matches=selected,
            objective_value=sum(matrix[i][j] for i, j in selected),
            resource_used=float(len(selected)),
            elapsed_seconds=perf_counter() - start,
            maximize=maximize,
        )

    @staticmethod
    def _validate(values, organization, problem) -> tuple[tuple[float, ...], ...]:
        try:
            matrix = tuple(tuple(float(value) for value in row) for row in values)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("assignment values must be a numeric N×K matrix") from exc
        n, k = len(organization.agent_ids), len(organization.skill_ids)
        if len(problem.requirements) != k:
            raise ValueError("problem task dimension must match organization skill dimension")
        if len(matrix) != n or any(len(row) != k for row in matrix):
            raise ValueError(f"assignment values must have shape {n}×{k}")
        if any(not isfinite(value) for row in matrix for value in row):
            raise ValueError("assignment values must be finite")
        return matrix

    @staticmethod
    def _solve_exact_cardinality(
        values: tuple[tuple[float, ...], ...],
        cardinality: int,
        eligible_agents: tuple[int, ...],
        *,
        maximize: bool,
    ) -> tuple[tuple[int, int], ...] | None:
        if cardinality == 0:
            return ()
        n, k = len(values), len(values[0])
        # A perfect assignment in this augmented square matrix contains
        # exactly ``cardinality`` real-agent/real-task edges. Dummy-to-dummy
        # edges are forbidden; dummy agents/tasks represent unmatched vertices.
        size = n + k - cardinality
        forbidden = float("-inf") if maximize else float("inf")
        objective = [[forbidden] * size for _ in range(size)]
        eligible = set(eligible_agents)
        for agent in range(n):
            for task in range(k):
                if agent in eligible:
                    objective[agent][task] = values[agent][task]
            for dummy_task in range(k, size):
                objective[agent][dummy_task] = 0.0
        for dummy_agent in range(n, size):
            for task in range(k):
                objective[dummy_agent][task] = 0.0
        try:
            rows, cols = linear_sum_assignment(objective, maximize=maximize)
        except ValueError:
            return None
        matches = tuple(sorted((int(agent), int(task))
                               for agent, task in zip(rows, cols)
                               if agent < n and task < k))
        if len(matches) != cardinality:
            return None
        return matches
