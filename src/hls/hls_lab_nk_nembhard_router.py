"""Perfect-information P0-style router for Nembhard Direct productivity.

This is an HLS oracle baseline, not a learned router and not a reproduction of
MixLLM. It sees the true Nembhard experience state and productivity profile.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .hls_lab_nk_geometry import (
    OrganizationResourcesNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    enumerate_productive_action_entries_nk,
)
from .hls_lab_nk_nembhard import (
    NembhardDirectProfileNK,
    NembhardDirectStateNK,
    nembhard_productive_outputs_nk,
)
from .hls_lab_nk_production import FunctionalResultNK, evaluate_problem_nk, functional_effort_rank_nk


@dataclass(frozen=True)
class NembhardOracleDecisionViewNK:
    """Information supplied to the oracle, with no HLS competence matrix."""

    resources: OrganizationResourcesNK
    problem: ProblemSpecNK
    experience: NembhardDirectStateNK
    profile: NembhardDirectProfileNK
    period_duration: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.resources, OrganizationResourcesNK):
            raise TypeError("resources must be OrganizationResourcesNK")
        if not isinstance(self.problem, ProblemSpecNK):
            raise TypeError("problem must be ProblemSpecNK")
        if not isinstance(self.experience, NembhardDirectStateNK):
            raise TypeError("experience must be NembhardDirectStateNK")
        if not isinstance(self.profile, NembhardDirectProfileNK):
            raise TypeError("profile must be NembhardDirectProfileNK")
        if (self.experience.n_agents, self.experience.n_skills) != (
            len(self.resources.agent_ids), len(self.resources.skill_ids)
        ):
            raise ValueError("experience dimensions must match resource geometry")
        self.profile.validate_dimensions(len(self.resources.agent_ids), len(self.resources.skill_ids))
        if len(self.problem.requirements) != len(self.resources.skill_ids):
            raise ValueError("problem dimension must match resource geometry")
        if isinstance(self.period_duration, bool):
            raise ValueError("period_duration must be finite and positive")
        try:
            duration = float(self.period_duration)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("period_duration must be finite and positive") from exc
        if not isfinite(duration) or duration <= 0:
            raise ValueError("period_duration must be finite and positive")
        object.__setattr__(self, "period_duration", duration)


@dataclass(frozen=True)
class NembhardOracleDecisionNK:
    """Selected feasible allocation plus auditable current-period diagnostics."""

    router_id: str
    catalog_action_id: int
    allocation: ProductiveAllocationNK
    predicted_outputs: tuple[float, ...]
    predicted_functional_result: FunctionalResultNK
    rank: tuple[float, float, float, float]
    feasible_candidate_count: int


@dataclass(frozen=True)
class NembhardOracleRouterNK:
    """Deterministic functional-first router with perfect Nembhard information."""

    router_id: str = "nembhard_oracle"

    def __post_init__(self) -> None:
        if self.router_id != "nembhard_oracle":
            raise ValueError("router_id must be 'nembhard_oracle'")

    def choose(
        self,
        view: NembhardOracleDecisionViewNK,
        *,
        max_candidates: int,
        per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
    ) -> NembhardOracleDecisionNK:
        entries = enumerate_productive_action_entries_nk(
            view.resources,
            view.problem,
            max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        ranked = []
        for catalog_id, allocation in entries:
            outputs, _ = nembhard_productive_outputs_nk(
                allocation,
                view.experience,
                view.profile,
                period_duration=view.period_duration,
            )
            effort = sum(sum(row) for row in allocation)
            rank = functional_effort_rank_nk(outputs, view.problem.requirements, effort)
            ranked.append((rank, catalog_id, allocation, outputs))
        # max() is stable for equal keys: the earliest feasible catalogue entry wins.
        rank, catalog_id, allocation, outputs = max(ranked, key=lambda row: row[0])
        return NembhardOracleDecisionNK(
            router_id=self.router_id,
            catalog_action_id=catalog_id,
            allocation=allocation,
            predicted_outputs=outputs,
            predicted_functional_result=evaluate_problem_nk(outputs, view.problem.requirements),
            rank=rank,
            feasible_candidate_count=len(entries),
        )
