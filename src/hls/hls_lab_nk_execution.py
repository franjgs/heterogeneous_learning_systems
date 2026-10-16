"""N×K production and MIS-v2 execution using Phase 1 geometry contracts.

The default path remains byte-schema compatible with Phase 2 production-only
P0 episodes. An explicitly enabled additive branch applies MIS-v2 after each
period's production and outcome evaluation. Teaching, P1/P2, competence
estimation, and environment generation remain unsupported here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .hls_lab_nk_geometry import (
    OrganizationConfigNK,
    OrganizationStateNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    enumerate_productive_action_entries_nk,
)
from .hls_lab_nk_production import (
    FunctionalResultNK,
    P0ProductionOnlyNK,
    ces_reward_nk,
    evaluate_problem_nk,
    productive_outputs_nk,
)
from .hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from .hls_lab_nk_teaching import (
    JointActionNK,
    TeachingActionNK,
    TeachingEfficacyNK,
    TeachingParametersNK,
    teaching_transition_nk,
    validate_joint_action_resources_nk,
)

TOL = 1e-12


@dataclass(frozen=True)
class NKProductionEpisodeRecord:
    period: int
    problem_id: str
    requirements: tuple[float, ...]
    competence_before: tuple[tuple[float, ...], ...]
    competence_after: tuple[tuple[float, ...], ...]
    action_id: int
    allocation: ProductiveAllocationNK
    individual_outputs: tuple[tuple[float, ...], ...]
    outputs: tuple[float, ...]
    functional_result: FunctionalResultNK
    ces_reward: float
    organization_effort_budget: float
    problem_effort_budget: float
    effective_collective_budget: float
    individual_effort_limits: tuple[float, ...]
    individual_effort_used: tuple[float, ...]
    productive_effort_used: float
    unused_collective_capacity: float


@dataclass(frozen=True)
class NKProductionRunResult:
    records: tuple[NKProductionEpisodeRecord, ...]
    final_state: OrganizationStateNK


@dataclass(frozen=True)
class NKLearningEpisodeRecord:
    """Learning-mode trace; production metrics retain the Phase 2 record."""

    production: NKProductionEpisodeRecord
    competence_increment: tuple[tuple[float, ...], ...]
    learning_eta: tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class NKLearningRunResult:
    records: tuple[NKLearningEpisodeRecord, ...]
    final_state: OrganizationStateNK


@dataclass(frozen=True)
class NKTeachingEpisodeRecord:
    production: NKProductionEpisodeRecord
    teaching_action: TeachingActionNK | None
    productive_effort_used: float
    teaching_resource_used: float
    total_resource_used: float
    individual_resource_used: tuple[float, ...]
    unused_collective_capacity: float
    competence_after_mis: tuple[tuple[float, ...], ...]
    mis_increment: tuple[tuple[float, ...], ...]
    competence_increment_from_teaching: tuple[tuple[float, ...], ...]
    teaching_efficacy: float | None


@dataclass(frozen=True)
class NKTeachingRunResult:
    records: tuple[NKTeachingEpisodeRecord, ...]
    final_state: OrganizationStateNK


def run_nk_production_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
    individual_learning: bool = False,
    learning_profile: LearningProfileNK | None = None,
    teaching_enabled: bool = False,
    teaching_efficacy: TeachingEfficacyNK | None = None,
    teaching_parameters: TeachingParametersNK = TeachingParametersNK(),
    explicit_actions: tuple[JointActionNK, ...] | None = None,
) -> NKProductionRunResult | NKLearningRunResult | NKTeachingRunResult:
    """Run deterministic P0 episodes over a caller-frozen exogenous sequence.

    P0 receives actual competence as its estimate at each decision (the
    perfect-information condition). By default, this remains the Phase 2
    frozen-competence path and retains its result/serialization contract.
    Setting ``individual_learning=True`` requires an N×K MIS-v2 profile and
    returns a learning trace with post-production competence transitions.
    Supplying ``explicit_actions`` opts into the N×K joint-action validation
    path. Teaching is never selected implicitly: each period explicitly names
    its productive allocation and optional directed teaching event. The joint
    path applies output, MIS-v2, then teaching, matching the legacy order.
    Neither path generates environment draws or observation updates.
    """
    if not problems:
        raise ValueError("problem sequence must be non-empty")
    initial = organization.initial_state()
    if learning_profile is not None:
        learning_profile.validate_dimensions(initial.n_agents, initial.n_skills)
    if teaching_enabled and explicit_actions is None:
        raise ValueError("teaching-enabled execution requires explicit complete actions")
    if explicit_actions is not None:
        if len(explicit_actions) != len(problems):
            raise ValueError("explicit_actions must contain one complete action per problem")
        if any(action.teaching is not None for action in explicit_actions) and not teaching_enabled:
            raise ValueError("teaching actions require teaching_enabled=True")
        if teaching_enabled:
            if teaching_efficacy is None:
                raise ValueError("teaching_enabled execution requires teaching_efficacy")
            teaching_efficacy.validate_identifiers(initial.agent_ids, initial.skill_ids)
        return _run_nk_explicit_sequence(
            organization, problems, explicit_actions,
            max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
            individual_learning=individual_learning,
            learning_profile=learning_profile,
            teaching_enabled=teaching_enabled,
            teaching_efficacy=teaching_efficacy,
            teaching_parameters=teaching_parameters,
        )
    if individual_learning:
        if learning_profile is None:
            raise ValueError("MIS-v2 ON requires a LearningProfileNK")
        return _run_nk_learning_sequence(
            organization, problems, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
            learning_profile=learning_profile,
        )
    # Phase 2 is explicitly an ORACLE/P0 control: estimates are aligned to
    # reality before the policy receives its decision state.
    state = OrganizationStateNK(initial.agent_ids, initial.skill_ids,
                                initial.competence_real, initial.competence_real)
    n, k = state.n_agents, state.n_skills
    records: list[NKProductionEpisodeRecord] = []
    policy = P0ProductionOnlyNK()
    for period, problem in enumerate(problems):
        if len(problem.requirements) != k:
            raise ValueError(f"problem {problem.problem_id} does not match organization K")
        entries = enumerate_productive_action_entries_nk(
            organization, problem, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        actions = tuple(action for _, action in entries)
        # N×K P0 is deliberately the perfect-information control. The
        # decision estimate equals reality and is never updated.
        selected_index, action = policy.choose(
            actions, state.competence_estimated, problem  # type: ignore[arg-type]
        )
        action_id = entries[selected_index][0]
        individual_outputs = tuple(tuple(action[i][skill] * state.competence_real[i][skill]
                                         for skill in range(k))
                                   for i in range(n))
        outputs = productive_outputs_nk(state.competence_real, action)
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)  # type: ignore[arg-type]
        individual_used = tuple(sum(row) for row in action)
        effort_used = sum(individual_used)
        effective_budget = min(organization.collective_effort_budget, problem.resource_budget)
        if (effort_used > effective_budget + TOL
                or any(individual_used[i] > organization.effort_limits[i] + TOL
                       for i in range(organization.initial_state().n_agents))):
            raise AssertionError("enumerated P0 action violates resource constraints")
        records.append(NKProductionEpisodeRecord(
            period=period, problem_id=problem.problem_id, requirements=problem.requirements,
            competence_before=state.competence_real, competence_after=state.competence_real,
            action_id=action_id, allocation=action, individual_outputs=individual_outputs,
            outputs=outputs, functional_result=functional, ces_reward=reward,
            organization_effort_budget=organization.collective_effort_budget,
            problem_effort_budget=problem.resource_budget,
            effective_collective_budget=effective_budget,
            individual_effort_limits=organization.effort_limits,
            individual_effort_used=individual_used,
            productive_effort_used=effort_used,
            unused_collective_capacity=max(0.0, effective_budget - effort_used),
        ))
    return NKProductionRunResult(tuple(records), state)


def _run_nk_explicit_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    actions: tuple[JointActionNK, ...],
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None,
    individual_learning: bool,
    learning_profile: LearningProfileNK | None,
    teaching_enabled: bool,
    teaching_efficacy: TeachingEfficacyNK | None,
    teaching_parameters: TeachingParametersNK,
) -> NKTeachingRunResult:
    initial = organization.initial_state()
    if individual_learning and learning_profile is None:
        raise ValueError("MIS-v2 ON requires a LearningProfileNK")
    if learning_profile is not None:
        learning_profile.validate_dimensions(initial.n_agents, initial.n_skills)
    state = OrganizationStateNK(
        initial.agent_ids, initial.skill_ids,
        initial.competence_real, initial.competence_real,
    )
    records: list[NKTeachingEpisodeRecord] = []
    for period, (problem, joint) in enumerate(zip(problems, actions)):
        if len(problem.requirements) != state.n_skills:
            raise ValueError(f"problem {problem.problem_id} does not match organization K")
        allocation = tuple(tuple(float(value) for value in row) for row in joint.production)
        if len(allocation) != state.n_agents or any(len(row) != state.n_skills for row in allocation):
            raise ValueError("explicit production allocation must have shape N×K")
        entries = enumerate_productive_action_entries_nk(
            organization, problem, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        try:
            action_id = next(identifier for identifier, candidate in entries if candidate == allocation)
        except StopIteration as exc:
            raise ValueError("explicit production allocation is not a feasible catalog action") from exc
        if joint.teaching is not None and not teaching_enabled:
            raise ValueError("teaching action supplied while teaching is disabled")
        if joint.teaching is not None and teaching_efficacy is None:
            raise ValueError("teaching efficacy is required for a teaching action")
        effective_budget = min(organization.collective_effort_budget, problem.resource_budget)
        individual_used, total_used, unused = validate_joint_action_resources_nk(
            allocation, joint.teaching,
            agent_ids=state.agent_ids,
            collective_budget=effective_budget,
            individual_limits=organization.effort_limits,
            efficacy=teaching_efficacy if joint.teaching is not None else None,
        )

        before = state.competence_real
        outputs = productive_outputs_nk(before, allocation)
        individual_outputs = tuple(tuple(
            allocation[i][skill] * before[i][skill] for skill in range(state.n_skills)
        ) for i in range(state.n_agents))
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)  # type: ignore[arg-type]
        post_mis = before
        mis_increment = tuple(tuple(0.0 for _ in range(state.n_skills)) for _ in range(state.n_agents))
        if individual_learning:
            assert learning_profile is not None
            post_mis = mis_v2_transition_nk(before, allocation, learning_profile, enabled=True)
            mis_increment = tuple(tuple(post_mis[i][k] - before[i][k]
                                       for k in range(state.n_skills))
                                  for i in range(state.n_agents))
        after = post_mis
        teaching_increment = tuple(tuple(0.0 for _ in range(state.n_skills))
                                   for _ in range(state.n_agents))
        resolved_efficacy: float | None = None
        if joint.teaching is not None:
            assert teaching_efficacy is not None
            transition = teaching_transition_nk(
                post_mis, joint.teaching, teaching_efficacy, teaching_parameters,
            )
            after = transition.competence_after
            teaching_increment = transition.competence_increment
            resolved_efficacy = transition.efficacy
        production = NKProductionEpisodeRecord(
            period=period, problem_id=problem.problem_id, requirements=problem.requirements,
            competence_before=before, competence_after=after,
            action_id=action_id, allocation=allocation, individual_outputs=individual_outputs,
            outputs=outputs, functional_result=functional, ces_reward=reward,
            organization_effort_budget=organization.collective_effort_budget,
            problem_effort_budget=problem.resource_budget,
            effective_collective_budget=effective_budget,
            individual_effort_limits=organization.effort_limits,
            individual_effort_used=tuple(sum(row) for row in allocation),
            productive_effort_used=sum(sum(row) for row in allocation),
            unused_collective_capacity=unused,
        )
        teaching_resource = 0.0 if joint.teaching is None else 2.0 * joint.teaching.effort
        records.append(NKTeachingEpisodeRecord(
            production=production, teaching_action=joint.teaching,
            productive_effort_used=production.productive_effort_used,
            teaching_resource_used=teaching_resource, total_resource_used=total_used,
            individual_resource_used=individual_used,
            unused_collective_capacity=unused,
            competence_after_mis=post_mis, mis_increment=mis_increment,
            competence_increment_from_teaching=teaching_increment,
            teaching_efficacy=resolved_efficacy,
        ))
        state = OrganizationStateNK(state.agent_ids, state.skill_ids, after, after)
    return NKTeachingRunResult(tuple(records), state)


def _run_nk_learning_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None,
    learning_profile: LearningProfileNK,
) -> NKLearningRunResult:
    """P0 episodes with post-production MIS-v2 and a persistent true state."""
    initial = organization.initial_state()
    state = OrganizationStateNK(
        initial.agent_ids, initial.skill_ids,
        initial.competence_real, initial.competence_real,
    )
    n, k = state.n_agents, state.n_skills
    policy = P0ProductionOnlyNK()
    records: list[NKLearningEpisodeRecord] = []
    for period, problem in enumerate(problems):
        if len(problem.requirements) != k:
            raise ValueError(f"problem {problem.problem_id} does not match organization K")
        entries = enumerate_productive_action_entries_nk(
            organization, problem, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        actions = tuple(action for _, action in entries)
        selected_index, action = policy.choose(actions, state.competence_estimated, problem)  # type: ignore[arg-type]
        action_id = entries[selected_index][0]

        # Output, success and CES use pre-learning competence. MIS-v2 is
        # applied below, so development first affects the next decision.
        individual_outputs = tuple(tuple(
            action[i][skill] * state.competence_real[i][skill] for skill in range(k)
        ) for i in range(n))
        outputs = productive_outputs_nk(state.competence_real, action)
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)  # type: ignore[arg-type]
        individual_used = tuple(sum(row) for row in action)
        effort_used = sum(individual_used)
        effective_budget = min(organization.collective_effort_budget, problem.resource_budget)
        if (effort_used > effective_budget + TOL
                or any(individual_used[i] > organization.effort_limits[i] + TOL for i in range(n))):
            raise AssertionError("enumerated P0 action violates resource constraints")

        competence_after = mis_v2_transition_nk(
            state.competence_real, action, learning_profile, enabled=True,
        )
        increments = tuple(tuple(
            competence_after[i][skill] - state.competence_real[i][skill]
            for skill in range(k)
        ) for i in range(n))
        production_record = NKProductionEpisodeRecord(
            period=period, problem_id=problem.problem_id, requirements=problem.requirements,
            competence_before=state.competence_real, competence_after=competence_after,
            action_id=action_id, allocation=action, individual_outputs=individual_outputs,
            outputs=outputs, functional_result=functional, ces_reward=reward,
            organization_effort_budget=organization.collective_effort_budget,
            problem_effort_budget=problem.resource_budget,
            effective_collective_budget=effective_budget,
            individual_effort_limits=organization.effort_limits,
            individual_effort_used=individual_used, productive_effort_used=effort_used,
            unused_collective_capacity=max(0.0, effective_budget - effort_used),
        )
        records.append(NKLearningEpisodeRecord(
            production=production_record,
            competence_increment=increments,
            learning_eta=learning_profile.eta,
        ))
        state = OrganizationStateNK(
            state.agent_ids, state.skill_ids, competence_after, competence_after,
        )
    return NKLearningRunResult(tuple(records), state)


def serialize_nk_production_result(result: NKProductionRunResult) -> str:
    """Stable JSON serialization for exact deterministic replay checks."""
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), allow_nan=False)


def serialize_nk_learning_result(result: NKLearningRunResult) -> str:
    """Stable JSON serialization for MIS-v2 ON trajectories."""
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), allow_nan=False)


def serialize_nk_teaching_result(result: NKTeachingRunResult) -> str:
    """Stable JSON serialization for explicit N×K joint-action trajectories."""
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), allow_nan=False)
