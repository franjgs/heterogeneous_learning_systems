"""N×K adapters for the historical HLS Laboratory P0/P1/P2 rules.

This module changes policy dimensions and action representation only. The
decision scores, fixed relation rule, P2 exploration/threshold rule and
first-candidate tie behavior remain those of ``hls_lab_v1_integrated``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, prod
from typing import Protocol

from .hls_lab_nk_geometry import (
    OrganizationConfigNK,
    ProblemSpecNK,
    enumerate_productive_action_entries_nk,
)
from .hls_lab_nk_production import p0_rank_nk
from .hls_lab_nk_teaching import (
    JointActionNK,
    TeachingActionNK,
    TeachingEfficacyNK,
    validate_joint_action_resources_nk,
)

TOL = 1e-12
TeachingRelationNK = tuple[str, str, str]  # teacher ID, learner ID, skill ID


@dataclass(frozen=True)
class TeachingPolicyParametersNK:
    """Policy parameters already present in legacy ``TeachingParameters``."""

    effort: float = 0.25
    efficacy_prior_mean: float = 0.5
    efficacy_threshold: float = 0.35
    target_competence: float = 0.7

    def __post_init__(self) -> None:
        values = (self.effort, self.efficacy_prior_mean,
                  self.efficacy_threshold, self.target_competence)
        try:
            effort, prior, threshold, target = (float(value) for value in values)
        except (TypeError, ValueError) as exc:
            raise ValueError("teaching policy parameters must be numeric") from exc
        if not isfinite(effort) or not 0.0 < effort <= 1.0:
            raise ValueError("teaching effort must lie in (0, 1]")
        if any(not isfinite(value) or not 0.0 <= value <= 1.0
               for value in (prior, threshold, target)):
            raise ValueError("efficacy prior, threshold and target must lie in [0, 1]")
        object.__setattr__(self, "effort", effort)
        object.__setattr__(self, "efficacy_prior_mean", prior)
        object.__setattr__(self, "efficacy_threshold", threshold)
        object.__setattr__(self, "target_competence", target)


@dataclass(frozen=True)
class EfficacyEstimateNK:
    relation: TeachingRelationNK
    count: int
    mean: float

    def __post_init__(self) -> None:
        if self.count < 1 or not isinstance(self.count, int):
            raise ValueError("efficacy observation count must be a positive integer")
        if not isfinite(self.mean) or not 0.0 <= self.mean <= 1.0:
            raise ValueError("efficacy estimate must lie in [0, 1]")


@dataclass(frozen=True)
class OrganizationMemoryNK:
    """P2's running-mean memory of observed formative efficacy signals."""

    efficacy: tuple[EfficacyEstimateNK, ...] = ()

    def __post_init__(self) -> None:
        relations = tuple(row.relation for row in self.efficacy)
        if len(set(relations)) != len(relations):
            raise ValueError("organization memory cannot duplicate a relation")

    def estimate(self, relation: TeachingRelationNK, prior: float) -> float:
        row = next((item for item in self.efficacy if item.relation == relation), None)
        return prior if row is None else row.mean

    def count(self, relation: TeachingRelationNK) -> int:
        row = next((item for item in self.efficacy if item.relation == relation), None)
        return 0 if row is None else row.count

    def update(self, relation: TeachingRelationNK, signal: float) -> "OrganizationMemoryNK":
        if not isfinite(signal):
            raise ValueError("formative efficacy signal must be finite")
        old = next((item for item in self.efficacy if item.relation == relation), None)
        count = 0 if old is None else old.count
        mean = 0.0 if old is None else old.mean
        count += 1
        value = min(1.0, max(0.0, signal))
        updated = EfficacyEstimateNK(relation, count, mean + (value - mean) / count)
        rows = [item for item in self.efficacy if item.relation != relation]
        rows.append(updated)
        # IDs do not determine the legacy tie order; agent/skill indices do.
        return OrganizationMemoryNK(tuple(rows))


@dataclass(frozen=True)
class NKDecisionView:
    """Policy-visible state only; efficacy truth is deliberately excluded."""

    period: int
    periods_remaining: int
    problem_id: str
    agent_ids: tuple[str, ...]
    skill_ids: tuple[str, ...]
    requirements: tuple[float, ...]
    estimated_competencies: tuple[tuple[float, ...], ...]
    feasible_actions: tuple[JointActionNK, ...]


class NKCoordinationPolicy(Protocol):
    name: str

    def choose(
        self,
        view: NKDecisionView,
        memory: OrganizationMemoryNK,
        parameters: TeachingPolicyParametersNK,
    ) -> JointActionNK: ...


@dataclass(frozen=True)
class P0ProductionOnlyPolicyNK:
    """Common-interface adapter for legacy P0's production-only ranking."""

    name: str = "P0_PRODUCTION_ONLY"

    def choose(self, view, memory, parameters) -> JointActionNK:
        del memory, parameters
        return _best(view)


def _production_rank(view: NKDecisionView, action: JointActionNK):
    return p0_rank_nk(action.production, view.estimated_competencies,
                      ProblemSpecNK(view.problem_id, view.requirements, 0.0))


def _best(view: NKDecisionView, *, relation: TeachingRelationNK | None = None) -> JointActionNK:
    if relation is None:
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is None)
    else:
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is not None
                           and (action.teaching.teacher_id, action.teaching.learner_id,
                                action.teaching.skill_id) == relation)
    if not candidates:
        raise ValueError("no feasible action in requested class")
    # max() intentionally keeps the first catalogue action on ties, matching
    # the historical _best_action/_best_production helpers.
    return max(candidates, key=lambda action: _production_rank(view, action))


def _relation_indices(
    relation: TeachingRelationNK, view: NKDecisionView
) -> tuple[int, int, int]:
    if len(relation) != 3:
        raise ValueError("teaching relation must be (teacher_id, learner_id, skill_id)")
    try:
        teacher = view.agent_ids.index(relation[0])
        learner = view.agent_ids.index(relation[1])
        skill = view.skill_ids.index(relation[2])
    except ValueError as exc:
        raise ValueError(f"unknown agent or skill in teaching relation {relation!r}") from exc
    if teacher == learner:
        raise ValueError("teaching relation requires distinct teacher and learner")
    return teacher, learner, skill


@dataclass(frozen=True)
class P1FixedTeachingNK:
    relation: TeachingRelationNK
    name: str = "P1_FIXED_TEACHING"

    def __post_init__(self) -> None:
        if len(self.relation) != 3 or any(not isinstance(value, str) or not value.strip()
                                          for value in self.relation):
            raise ValueError("P1 relation must contain non-empty teacher, learner and skill IDs")
        if self.relation[0] == self.relation[1]:
            raise ValueError("teaching relation requires distinct teacher and learner")

    def choose(self, view, memory, parameters) -> JointActionNK:
        del memory, parameters
        _relation_indices(self.relation, view)
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is not None
                           and (action.teaching.teacher_id, action.teaching.learner_id,
                                action.teaching.skill_id) == self.relation)
        return (max(candidates, key=lambda action: _production_rank(view, action))
                if candidates else _best(view))


@dataclass(frozen=True)
class P2AdaptiveTeachingNK:
    relations: tuple[TeachingRelationNK, ...]
    name: str = "P2_ADAPTIVE_TEACHING"

    def __post_init__(self) -> None:
        if not self.relations or len(set(self.relations)) != len(self.relations):
            raise ValueError("P2 requires a non-empty unique relation list")

    def choose(self, view, memory, parameters) -> JointActionNK:
        indices = {relation: _relation_indices(relation, view)
                   for relation in self.relations}
        best_production = _best(view)
        if _production_rank(view, best_production)[0] == 1:
            return best_production
        eligible = tuple(relation for relation in self.relations
                         if view.requirements[indices[relation][2]] > 0
                         and view.estimated_competencies[indices[relation][1]][indices[relation][2]]
                         < parameters.target_competence)
        unseen = tuple(relation for relation in eligible if memory.count(relation) == 0)
        if unseen:
            selected = unseen[0]
        elif eligible:
            selected = max(
                eligible,
                key=lambda relation: (
                    memory.estimate(relation, parameters.efficacy_prior_mean),
                    tuple(-index for index in indices[relation]),
                ),
            )
            if memory.estimate(selected, parameters.efficacy_prior_mean) < parameters.efficacy_threshold:
                selected = None
        else:
            selected = None
        if selected is None:
            return best_production
        candidates = tuple(action for action in view.feasible_actions
                           if action.teaching is not None
                           and (action.teaching.teacher_id, action.teaching.learner_id,
                                action.teaching.skill_id) == selected)
        return (max(candidates, key=lambda action: _production_rank(view, action))
                if candidates else best_production)


def _raw_joint_candidate_count(
    organization: OrganizationConfigNK,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None,
) -> int:
    if per_agent_effort_choices is None:
        if len(organization.skill_ids) != 2:
            raise ValueError("K != 2 requires explicit effort choices")
        per_agent_counts = (4,) * len(organization.agent_ids)
    else:
        if len(per_agent_effort_choices) != len(organization.agent_ids):
            raise ValueError("per_agent_effort_choices must contain one catalog per agent")
        per_agent_counts = tuple(len(catalog) for catalog in per_agent_effort_choices)
    production_count = prod(per_agent_counts)
    n, k = len(organization.agent_ids), len(organization.skill_ids)
    return production_count * (1 + n * (n - 1) * k)


def enumerate_feasible_joint_actions_nk(
    organization: OrganizationConfigNK,
    problem: ProblemSpecNK,
    *,
    max_candidates: int,
    teaching_enabled: bool,
    teaching_efficacy: TeachingEfficacyNK | None,
    teaching_effort: float,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
) -> tuple[JointActionNK, ...]:
    """Enumerate no-lesson then directed one-lesson actions in legacy order."""
    if not isinstance(max_candidates, int) or isinstance(max_candidates, bool) or max_candidates < 1:
        raise ValueError("max_candidates must be a positive integer")
    if teaching_enabled:
        if teaching_efficacy is None:
            raise ValueError("teaching-enabled policy execution requires efficacy")
        teaching_efficacy.validate_identifiers(organization.agent_ids, organization.skill_ids)
        if not isfinite(teaching_effort) or teaching_effort <= 0:
            raise ValueError("teaching_effort must be finite and positive")
        candidate_count = _raw_joint_candidate_count(organization, per_agent_effort_choices)
    else:
        candidate_count = _raw_joint_candidate_count(organization, per_agent_effort_choices)
        candidate_count //= 1 + len(organization.agent_ids) * (len(organization.agent_ids) - 1) * len(organization.skill_ids)
    if candidate_count > max_candidates:
        raise ValueError(
            f"joint action catalog requires {candidate_count} candidates, "
            f"exceeding max_candidates={max_candidates}; no actions were truncated"
        )
    production_entries = enumerate_productive_action_entries_nk(
        organization, problem, max_candidates=max_candidates,
        per_agent_effort_choices=per_agent_effort_choices,
    )
    budget = min(organization.collective_effort_budget, problem.resource_budget)
    output: list[JointActionNK] = []
    relations = ()
    if teaching_enabled:
        assert teaching_efficacy is not None
        relations = tuple(
            TeachingActionNK(organization.agent_ids[teacher], organization.agent_ids[learner],
                             organization.skill_ids[skill], teaching_effort)
            for teacher in range(len(organization.agent_ids))
            for learner in range(len(organization.agent_ids)) if learner != teacher
            for skill in range(len(organization.skill_ids))
        )
    for _, allocation in production_entries:
        loads, _, _ = validate_joint_action_resources_nk(
            allocation, None, agent_ids=organization.agent_ids,
            collective_budget=budget, individual_limits=organization.effort_limits,
        )
        del loads
        output.append(JointActionNK(allocation))
        if teaching_enabled:
            assert teaching_efficacy is not None
            for event in relations:
                try:
                    validate_joint_action_resources_nk(
                        allocation, event, agent_ids=organization.agent_ids,
                        collective_budget=budget, individual_limits=organization.effort_limits,
                        efficacy=teaching_efficacy,
                    )
                except ValueError:
                    continue
                output.append(JointActionNK(allocation, event))
    if not output:
        raise ValueError("problem has no feasible joint actions")
    return tuple(output)


def formative_efficacy_signal_nk(
    *,
    competence_after_mis: float,
    observed_teaching_gain: float,
    transfer_rate: float,
    effort: float,
    prior_mean: float,
) -> float:
    """Apply the legacy zero-noise gain normalization used by P2 memory."""
    denominator = transfer_rate * effort * (1.0 - competence_after_mis)
    return prior_mean if denominator <= TOL else observed_teaching_gain / denominator
