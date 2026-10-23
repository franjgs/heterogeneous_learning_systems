"""Exact finite-horizon reference for the S4 MIS-v2/transfer instance.

This is a narrowly scoped benchmark, not a policy. It reuses the laboratory's
physical transitions, reward, action feasibility and resource validation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from itertools import product

from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    validate_productive_allocation_nk,
)
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_policies import enumerate_feasible_joint_actions_nk
from hls.hls_lab_nk_production import (
    ces_reward_nk,
    evaluate_problem_nk,
    productive_outputs_nk,
)
from hls.hls_lab_nk_teaching import (
    JointActionNK,
    TeachingActionNK,
    TeachingEfficacyNK,
    TeachingParametersNK,
    teaching_transition_nk,
    validate_joint_action_resources_nk,
)

Competence = tuple[tuple[float, ...], ...]
TOL = 1e-12


@dataclass(frozen=True)
class ExactTransferCase:
    organization: OrganizationConfigNK
    problems: tuple[ProblemSpecNK, ...]
    profile: LearningProfileNK
    efficacy: TeachingEfficacyNK
    teaching_parameters: TeachingParametersNK
    teaching_effort: float
    effort_choices: tuple[tuple[tuple[float, ...], ...], ...]


@dataclass(frozen=True)
class PeriodResult:
    period: int
    problem_id: str
    action: JointActionNK
    outputs: tuple[float, ...]
    reward: float
    success: bool
    deficits: tuple[float, ...]
    competence_before: Competence
    competence_after_mis: Competence
    competence_after: Competence
    mis_increment: Competence
    transfer_increment: Competence
    productive_effort: float
    teaching_resource: float
    total_resource: float
    unused_resource: float


@dataclass(frozen=True)
class ExactResult:
    value: float
    actions: tuple[JointActionNK, ...]
    periods: tuple[PeriodResult, ...]
    visited_states: int


def _zero_efficacy(efficacy: TeachingEfficacyNK) -> TeachingEfficacyNK:
    n, k = efficacy.n_agents, efficacy.n_skills
    return TeachingEfficacyNK(
        efficacy.agent_ids, efficacy.skill_ids,
        tuple(tuple(tuple(0.0 for _ in range(k)) for _ in range(n))
              for _ in range(n)),
    )


def action_catalogs(case: ExactTransferCase, *, transfer_available: bool,
                    efficacy: TeachingEfficacyNK | None = None
                    ) -> tuple[tuple[JointActionNK, ...], ...]:
    """Use the full existing feasible catalog, including every no-lesson action."""
    active_efficacy = case.efficacy if efficacy is None else efficacy
    return tuple(
        enumerate_feasible_joint_actions_nk(
            case.organization, problem, max_candidates=216,
            teaching_enabled=transfer_available,
            teaching_efficacy=active_efficacy if transfer_available else None,
            teaching_effort=case.teaching_effort,
            per_agent_effort_choices=case.effort_choices,
        )
        for problem in case.problems
    )


def _step(case: ExactTransferCase, competence: Competence,
          problem: ProblemSpecNK, action: JointActionNK,
          *, efficacy: TeachingEfficacyNK | None = None) -> tuple[float, Competence]:
    effective_efficacy = case.efficacy if efficacy is None else efficacy
    validate_joint_action_resources_nk(
        action.production, action.teaching,
        agent_ids=case.organization.agent_ids,
        collective_budget=min(case.organization.collective_effort_budget,
                              problem.resource_budget),
        individual_limits=case.organization.effort_limits,
        efficacy=effective_efficacy if action.teaching is not None else None,
    )
    outputs = productive_outputs_nk(competence, action.production)
    reward = ces_reward_nk(outputs, problem.ces_weights)
    after_mis = mis_v2_transition_nk(competence, action.production, case.profile)
    after = after_mis
    if action.teaching is not None:
        after = teaching_transition_nk(
            after_mis, action.teaching, effective_efficacy,
            case.teaching_parameters,
        ).competence_after
    return reward, after


def solve_bellman(case: ExactTransferCase, *, transfer_available: bool,
                  efficacy: TeachingEfficacyNK | None = None) -> ExactResult:
    catalogs = action_catalogs(case, transfer_available=transfer_available,
                               efficacy=efficacy)
    choices: dict[tuple[int, Competence], JointActionNK] = {}

    @lru_cache(maxsize=None)
    def value(period: int, competence: Competence) -> float:
        if period == len(case.problems):
            return 0.0
        problem = case.problems[period]
        best = float("-inf")
        for action in catalogs[period]:
            reward, next_competence = _step(
                case, competence, problem, action, efficacy=efficacy,
            )
            candidate = reward + value(period + 1, next_competence)
            if candidate > best + TOL:
                best = candidate
                choices[(period, competence)] = action
        return best

    start = case.organization.competence_initial
    optimum = value(0, start)
    actions: list[JointActionNK] = []
    competence = start
    for period, problem in enumerate(case.problems):
        action = choices[(period, competence)]
        actions.append(action)
        _, competence = _step(case, competence, problem, action,
                              efficacy=efficacy)
    periods = replay_actions(case, tuple(actions), efficacy=efficacy)
    return ExactResult(optimum, tuple(actions), periods, value.cache_info().currsize)


def replay_actions(case: ExactTransferCase, actions: tuple[JointActionNK, ...],
                   *, efficacy: TeachingEfficacyNK | None = None
                   ) -> tuple[PeriodResult, ...]:
    if len(actions) != len(case.problems):
        raise ValueError("one action is required for every period")
    active_efficacy = case.efficacy if efficacy is None else efficacy
    competence = case.organization.competence_initial
    rows: list[PeriodResult] = []
    for period, (problem, action) in enumerate(zip(case.problems, actions)):
        validate_joint_action_resources_nk(
            action.production, action.teaching,
            agent_ids=case.organization.agent_ids,
            collective_budget=min(case.organization.collective_effort_budget,
                                  problem.resource_budget),
            individual_limits=case.organization.effort_limits,
            efficacy=active_efficacy if action.teaching is not None else None,
        )
        before = competence
        outputs = productive_outputs_nk(before, action.production)
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)
        after_mis = mis_v2_transition_nk(before, action.production, case.profile)
        after = after_mis
        transfer_increment = tuple(tuple(0.0 for _ in row) for row in before)
        if action.teaching is not None:
            transition = teaching_transition_nk(
                after_mis, action.teaching, active_efficacy,
                case.teaching_parameters,
            )
            after = transition.competence_after
            transfer_increment = transition.competence_increment
        productive_effort = sum(sum(row) for row in action.production)
        teaching_resource = (0.0 if action.teaching is None
                             else 2.0 * action.teaching.effort)
        budget = min(case.organization.collective_effort_budget,
                     problem.resource_budget)
        total_resource = productive_effort + teaching_resource
        rows.append(PeriodResult(
            period, problem.problem_id, action, outputs, reward,
            functional.success, functional.deficits, before, after_mis, after,
            tuple(tuple(after_mis[i][k] - before[i][k]
                        for k in range(len(before[i])))
                  for i in range(len(before))),
            transfer_increment, productive_effort, teaching_resource,
            total_resource, max(0.0, budget - total_resource),
        ))
        competence = after
    return tuple(rows)


def independent_action_catalogs(
    case: ExactTransferCase, *, transfer_available: bool,
    efficacy: TeachingEfficacyNK | None = None,
) -> tuple[tuple[JointActionNK, ...], ...]:
    """Rebuild feasible actions from raw effort vectors, not Bellman catalogs."""
    active_efficacy = case.efficacy if efficacy is None else efficacy
    n, k = len(case.organization.agent_ids), len(case.organization.skill_ids)
    per_agent = case.effort_choices
    period_catalogs: list[tuple[JointActionNK, ...]] = []
    relations = tuple(
        TeachingActionNK(case.organization.agent_ids[i],
                         case.organization.agent_ids[j],
                         case.organization.skill_ids[skill],
                         case.teaching_effort)
        for i in range(n) for j in range(n) if j != i
        for skill in range(k)
    ) if transfer_available else ()

    for problem in case.problems:
        raw: list[JointActionNK] = []
        for production in product(*per_agent):
            allocation: ProductiveAllocationNK = tuple(
                tuple(float(value) for value in row) for row in production
            )
            if not validate_productive_allocation_nk(allocation, case.organization, problem):
                continue
            raw.append(JointActionNK(allocation))
            for lesson in relations:
                try:
                    validate_joint_action_resources_nk(
                        allocation, lesson, agent_ids=case.organization.agent_ids,
                        collective_budget=min(case.organization.collective_effort_budget,
                                              problem.resource_budget),
                        individual_limits=case.organization.effort_limits,
                        efficacy=active_efficacy,
                    )
                except ValueError:
                    continue
                raw.append(JointActionNK(allocation, lesson))
        period_catalogs.append(tuple(raw))

    return tuple(period_catalogs)


def independent_exhaustive(case: ExactTransferCase, *, transfer_available: bool,
                           efficacy: TeachingEfficacyNK | None = None
                           ) -> tuple[float, tuple[JointActionNK, ...],
                                      float | None, tuple[JointActionNK, ...]]:
    """Enumerate full action sequences independently of the Bellman catalog."""
    period_catalogs = independent_action_catalogs(
        case, transfer_available=transfer_available, efficacy=efficacy,
    )
    best_value = float("-inf")
    best_path: tuple[JointActionNK, ...] = ()
    best_lesson_value: float | None = None
    best_lesson_path: tuple[JointActionNK, ...] = ()
    for path in product(*period_catalogs):
        competence = case.organization.competence_initial
        total = 0.0
        for problem, action in zip(case.problems, path):
            reward, competence = _step(case, competence, problem, action,
                                       efficacy=efficacy)
            total += reward
        if any(action.teaching is not None for action in path):
            if (best_lesson_value is None or
                    total > best_lesson_value + TOL):
                best_lesson_value, best_lesson_path = total, path
        if total > best_value + TOL:
            best_value, best_path = total, path
    return best_value, best_path, best_lesson_value, best_lesson_path


def result_to_dict(result: ExactResult) -> dict:
    return {
        "value": result.value,
        "visited_states": result.visited_states,
        "actions": [asdict(row.action) for row in result.periods],
        "periods": [asdict(row) for row in result.periods],
    }

