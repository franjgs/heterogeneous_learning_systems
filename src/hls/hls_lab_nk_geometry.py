"""Dimension-independent HLS Laboratory Phase 1 state and action geometry.

This module validates N×K organization/problem shapes and enumerates declared
productive allocations. It intentionally does not implement episode execution,
policies, learning transitions, teaching, or environment emission.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import isclose, isfinite, prod

from .discover_v0 import INDIVIDUAL_ACTIONS, JOINT_ACTIONS

TOL = 1e-12
CompetenceMatrixNK = tuple[tuple[float, ...], ...]
ProductiveAllocationNK = tuple[tuple[float, ...], ...]

def _validated_identifiers(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    values = tuple(values)
    if not values or any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f"{name} must contain non-empty strings")
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must be unique")
    return values


def _validated_nk_matrix(
    values: tuple[tuple[float, ...], ...], n: int, k: int, name: str,
    *, competence: bool,
) -> CompetenceMatrixNK:
    try:
        matrix = tuple(tuple(float(value) for value in row) for row in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric N×K matrix") from exc
    if len(matrix) != n or any(len(row) != k for row in matrix):
        raise ValueError(f"{name} must have shape {n}×{k}")
    for row in matrix:
        for value in row:
            if not isfinite(value) or (not 0 <= value <= 1 if competence else value < 0):
                domain = "[0, 1]" if competence else "finite and non-negative"
                raise ValueError(f"{name} values must be {domain}")
    return matrix


@dataclass(frozen=True)
class OrganizationStateNK:
    """Dimension-independent snapshot; it does not imply N×K execution support.

    Real competence and organizational estimates remain separate. When an
    estimate is omitted, the historical v1 perfect-information convention is
    used explicitly; no N×K policy currently consumes this state.
    """

    agent_ids: tuple[str, ...]
    skill_ids: tuple[str, ...]
    competence_real: CompetenceMatrixNK
    competence_estimated: CompetenceMatrixNK | None = None

    def __post_init__(self) -> None:
        agents = _validated_identifiers(self.agent_ids, "agent_ids")
        skills = _validated_identifiers(self.skill_ids, "skill_ids")
        real = _validated_nk_matrix(self.competence_real, len(agents), len(skills),
                                    "competence_real", competence=True)
        estimated = real if self.competence_estimated is None else _validated_nk_matrix(
            self.competence_estimated, len(agents), len(skills),
            "competence_estimated", competence=True,
        )
        object.__setattr__(self, "agent_ids", agents)
        object.__setattr__(self, "skill_ids", skills)
        object.__setattr__(self, "competence_real", real)
        object.__setattr__(self, "competence_estimated", estimated)

    @property
    def n_agents(self) -> int:
        return len(self.agent_ids)

    @property
    def n_skills(self) -> int:
        return len(self.skill_ids)


@dataclass(frozen=True)
class OrganizationConfigNK:
    """Validated N×K initial organization and resource configuration."""

    agent_ids: tuple[str, ...]
    skill_ids: tuple[str, ...]
    competence_initial: CompetenceMatrixNK
    effort_limits: tuple[float, ...]
    collective_effort_budget: float
    competence_estimated_initial: CompetenceMatrixNK | None = None

    def __post_init__(self) -> None:
        agents = _validated_identifiers(self.agent_ids, "agent_ids")
        skills = _validated_identifiers(self.skill_ids, "skill_ids")
        initial = _validated_nk_matrix(self.competence_initial, len(agents), len(skills),
                                       "competence_initial", competence=True)
        estimates = None if self.competence_estimated_initial is None else _validated_nk_matrix(
            self.competence_estimated_initial, len(agents), len(skills),
            "competence_estimated_initial", competence=True,
        )
        try:
            limits = tuple(float(value) for value in self.effort_limits)
        except (TypeError, ValueError) as exc:
            raise ValueError("effort_limits must contain one numeric limit per agent") from exc
        if len(limits) != len(agents) or any(not isfinite(value) or value < 0 for value in limits):
            raise ValueError("effort_limits must have length N and be finite non-negative values")
        try:
            shared_budget = float(self.collective_effort_budget)
        except (TypeError, ValueError) as exc:
            raise ValueError("collective_effort_budget must be finite and non-negative") from exc
        if not isfinite(shared_budget) or shared_budget < 0:
            raise ValueError("collective_effort_budget must be finite and non-negative")
        object.__setattr__(self, "agent_ids", agents)
        object.__setattr__(self, "skill_ids", skills)
        object.__setattr__(self, "competence_initial", initial)
        object.__setattr__(self, "competence_estimated_initial", estimates)
        object.__setattr__(self, "effort_limits", limits)
        object.__setattr__(self, "collective_effort_budget", shared_budget)

    def initial_state(self) -> OrganizationStateNK:
        """Return a fresh immutable state with real and estimated values apart."""
        return OrganizationStateNK(self.agent_ids, self.skill_ids, self.competence_initial,
                                   self.competence_estimated_initial)


@dataclass(frozen=True)
class OrganizationResourcesNK:
    """Decision-facing organization geometry without competence fields.

    This view is useful for policies whose physical state is not HLS
    competence (for example, the Nembhard productivity router).
    """

    agent_ids: tuple[str, ...]
    skill_ids: tuple[str, ...]
    effort_limits: tuple[float, ...]
    collective_effort_budget: float

    def __post_init__(self) -> None:
        agents = _validated_identifiers(self.agent_ids, "agent_ids")
        skills = _validated_identifiers(self.skill_ids, "skill_ids")
        try:
            limits = tuple(float(value) for value in self.effort_limits)
            budget = float(self.collective_effort_budget)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("resource limits and budget must be numeric") from exc
        if len(limits) != len(agents) or any(not isfinite(value) or value < 0 for value in limits):
            raise ValueError("effort_limits must have length N and be finite non-negative values")
        if not isfinite(budget) or budget < 0:
            raise ValueError("collective_effort_budget must be finite and non-negative")
        object.__setattr__(self, "agent_ids", agents)
        object.__setattr__(self, "skill_ids", skills)
        object.__setattr__(self, "effort_limits", limits)
        object.__setattr__(self, "collective_effort_budget", budget)

    @classmethod
    def from_organization(cls, organization: OrganizationConfigNK) -> "OrganizationResourcesNK":
        return cls(organization.agent_ids, organization.skill_ids,
                   organization.effort_limits, organization.collective_effort_budget)


@dataclass(frozen=True)
class ProblemSpecNK:
    """K-dimensional requirements, CES weights and shared effort cap."""

    problem_id: str
    requirements: tuple[float, ...]
    resource_budget: float
    ces_weights: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.problem_id, str) or not self.problem_id.strip():
            raise ValueError("problem_id must be non-empty")
        try:
            requirements = tuple(float(value) for value in self.requirements)
        except (TypeError, ValueError) as exc:
            raise ValueError("requirements must be a numeric K-vector") from exc
        if (not requirements or any(not isfinite(value) or value < 0 for value in requirements)
                or not any(value > 0 for value in requirements)):
            raise ValueError("requirements must be a non-empty finite non-negative vector, not all zero")
        try:
            budget = float(self.resource_budget)
        except (TypeError, ValueError) as exc:
            raise ValueError("resource_budget must be finite and non-negative") from exc
        if not isfinite(budget) or budget < 0:
            raise ValueError("resource_budget must be finite and non-negative")
        try:
            weights = ((1.0 / len(requirements),) * len(requirements)
                       if self.ces_weights is None else tuple(float(value) for value in self.ces_weights))
        except (TypeError, ValueError) as exc:
            raise ValueError("ces_weights must be a numeric K-vector") from exc
        if (len(weights) != len(requirements)
                or any(not isfinite(value) or value < 0 for value in weights)
                or not isclose(sum(weights), 1.0, rel_tol=0.0, abs_tol=1e-10)):
            raise ValueError("ces_weights must be a K-vector of finite non-negative values summing to one")
        object.__setattr__(self, "requirements", requirements)
        object.__setattr__(self, "resource_budget", budget)
        object.__setattr__(self, "ces_weights", weights)


def validate_productive_allocation_nk(
    allocation: ProductiveAllocationNK,
    organization: OrganizationConfigNK | OrganizationResourcesNK,
    problem: ProblemSpecNK,
) -> bool:
    """Return whether allocation respects shape, actor limits and both budgets."""
    if len(problem.requirements) != len(organization.skill_ids):
        return False
    try:
        action = _validated_nk_matrix(allocation, len(organization.agent_ids),
                                      len(organization.skill_ids), "allocation", competence=False)
    except (TypeError, ValueError):
        return False
    total = sum(sum(row) for row in action)
    return (total <= min(organization.collective_effort_budget, problem.resource_budget) + TOL
            and all(sum(row) <= organization.effort_limits[i] + TOL
                    for i, row in enumerate(action)))


def enumerate_productive_allocations_nk(
    organization: OrganizationConfigNK | OrganizationResourcesNK,
    problem: ProblemSpecNK,
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
) -> tuple[ProductiveAllocationNK, ...]:
    """Enumerate feasible actions in declared catalog order, without truncation."""
    return tuple(action for _, action in enumerate_productive_action_entries_nk(
        organization, problem, max_candidates=max_candidates,
        per_agent_effort_choices=per_agent_effort_choices,
    ))


def enumerate_productive_action_entries_nk(
    organization: OrganizationConfigNK | OrganizationResourcesNK,
    problem: ProblemSpecNK,
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
) -> tuple[tuple[int, ProductiveAllocationNK], ...]:
    """Return ``(catalog_id, allocation)`` for each feasible candidate.

    For K=2 the legacy DISCOVER individual choices are the default. For other
    K the caller must supply one ordered vector catalog per agent. The return
    identifier is the index in the full unfiltered catalog; ordering is
    catalog order then Cartesian product order. ``max_candidates`` is a
    caller-declared guard on that full catalog, not a silent action limit.
    """
    if not isinstance(max_candidates, int) or isinstance(max_candidates, bool) or max_candidates < 1:
        raise ValueError("max_candidates must be a positive integer")
    n, k = len(organization.agent_ids), len(organization.skill_ids)
    if len(problem.requirements) != k:
        raise ValueError(f"problem requirements have K={len(problem.requirements)}; organization has K={k}")
    if per_agent_effort_choices is None:
        if k != 2:
            raise ValueError("K != 2 requires an explicit per_agent_effort_choices catalog")
        choices = tuple(tuple(tuple(float(value) for value in vector)
                              for vector in INDIVIDUAL_ACTIONS) for _ in range(n))
    else:
        if len(per_agent_effort_choices) != n:
            raise ValueError(f"per_agent_effort_choices must contain N={n} agent catalogs")
        choices = tuple(tuple(tuple(float(value) for value in vector) for vector in catalog)
                        for catalog in per_agent_effort_choices)
    for index, catalog in enumerate(choices):
        if not catalog or len(set(catalog)) != len(catalog):
            raise ValueError(f"agent {organization.agent_ids[index]} effort catalog must be non-empty and unique")
        if any(len(vector) != k for vector in catalog):
            raise ValueError(f"agent {organization.agent_ids[index]} effort vectors must have K={k} entries")
        if any(not isfinite(value) or not 0 <= value <= 1 for vector in catalog for value in vector):
            raise ValueError("effort choices must be finite values in [0, 1]")
    candidate_count = prod(len(catalog) for catalog in choices)
    if candidate_count > max_candidates:
        raise ValueError(
            f"productive action catalog requires {candidate_count} candidates, "
            f"exceeding max_candidates={max_candidates}; no actions were truncated"
        )
    # The canonical historical tuple is used directly for 3×2 to make its
    # ordering/identifiers an explicit compatibility boundary.
    if (n, k) == (3, 2) and per_agent_effort_choices is None:
        candidates = JOINT_ACTIONS
    else:
        candidates = product(*choices)
    result = tuple((candidate_id,
                    tuple(tuple(float(value) for value in row) for row in allocation))
                   for candidate_id, allocation in enumerate(candidates)
                   if validate_productive_allocation_nk(allocation, organization, problem))
    if not result:
        raise ValueError(f"problem {problem.problem_id} has no feasible N×K productive allocation")
    return result
