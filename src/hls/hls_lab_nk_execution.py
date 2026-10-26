"""N×K production, mechanism and optional environment execution.

The default path remains byte-schema compatible with Phase 2 production-only
P0 episodes. An explicitly enabled additive branch applies MIS-v2 after each
period's production and outcome evaluation. Existing Phase 1–3D execution
contracts are retained. Optional environment generation freezes a trajectory
first and then invokes the same sequence runner; explicit-sequence callers
remain supported unchanged.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from random import Random

from .hls_lab_nk_geometry import (
    OrganizationConfigNK,
    OrganizationStateNK,
    OrganizationResourcesNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    enumerate_productive_action_entries_nk,
    validate_productive_allocation_nk,
)
from .hls_lab_nk_production import (
    FunctionalResultNK,
    P0ProductionOnlyNK,
    ces_reward_nk,
    evaluate_problem_nk,
    productive_outputs_nk,
)
from .hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from .hls_lab_nk_nembhard import (
    NembhardDirectExecutionNK,
    NembhardDirectStateNK,
    NembhardDirectProfileNK,
    NembhardOutputUnitContract,
    advance_nembhard_experience_nk,
    nembhard_productive_outputs_nk,
)
from .hls_lab_nk_nembhard_router import (
    NembhardOracleDecisionViewNK,
    NembhardOracleRouterNK,
)
from .hls_lab_nk_nembhard_adaptive import (
    NembhardAdaptiveDecisionViewNK,
    NembhardAdaptiveRouterConfigNK,
    NembhardAdaptiveRouterNK,
    ProductivityEstimatorStateNK,
    initialize_productivity_estimator_nk,
    observe_nembhard_work_outputs_nk,
    update_productivity_estimator_nk,
)
from .hls_lab_nk_estimation import (
    CompetenceObservationParametersNK,
    CompetencePosteriorNK,
    assimilate_production_observations_nk,
    initialize_competence_posterior_nk,
    posterior_mean_matrix_nk,
    posterior_variance_matrix_nk,
    predict_mis_v2_nk,
)
from .hls_lab_nk_teaching import (
    JointActionNK,
    TeachingActionNK,
    TeachingEfficacyNK,
    TeachingParametersNK,
    teaching_transition_nk,
    validate_joint_action_resources_nk,
)
from .hls_lab_nk_policies import (
    NKDecisionView,
    OrganizationMemoryNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    P0ProductionOnlyPolicyNK,
    TeachingPolicyParametersNK,
    enumerate_feasible_joint_actions_nk,
    formative_efficacy_signal_nk,
)
from .hls_lab_nk_environment import (
    EnvironmentTrajectoryNK,
    ExogenousEnvironmentConfigNK,
    generate_environment_trajectory_nk,
)
from .hls_lab_dynamic import indexed_normal_innovation
from .hls_lab_v1_integrated import _push_posterior, _training_noise

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
    policy_name: str
    joint_action_id: int | None
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
    formative_efficacy_observation: float | None
    efficacy_memory_before: tuple
    efficacy_memory_after: tuple
    organization_updated: bool


@dataclass(frozen=True)
class NKTeachingRunResult:
    records: tuple[NKTeachingEpisodeRecord, ...]
    final_state: OrganizationStateNK


@dataclass(frozen=True)
class NKInformationEpisodeRecord:
    """Trace with actual, estimated and observed competence kept distinct."""

    period: int
    policy_name: str
    action_id: int | None
    joint_action_id: int | None
    action: JointActionNK
    competence_actual_before: tuple[tuple[float, ...], ...]
    competence_estimated_before: tuple[tuple[float, ...], ...]
    competence_variance_before: tuple[tuple[float, ...], ...] | None
    production_observations: tuple[tuple[float, ...], ...]
    production: NKProductionEpisodeRecord
    teaching_observation: float | None
    mis_increment: tuple[tuple[float, ...], ...]
    competence_after_mis: tuple[tuple[float, ...], ...]
    teaching_increment: tuple[tuple[float, ...], ...]
    competence_actual_after: tuple[tuple[float, ...], ...]
    competence_estimated_after: tuple[tuple[float, ...], ...]
    competence_variance_after: tuple[tuple[float, ...], ...] | None
    estimation_error: tuple[tuple[float, ...], ...]
    efficacy_memory_before: tuple
    efficacy_memory_after: tuple
    organization_updated: bool
    productive_effort_used: float
    teaching_resource_used: float
    total_resource_used: float
    unused_collective_capacity: float


@dataclass(frozen=True)
class NKInformationRunResult:
    information_mode: str
    records: tuple[NKInformationEpisodeRecord, ...]
    final_state: OrganizationStateNK
    final_posterior: CompetencePosteriorNK | None
    final_policy_memory: OrganizationMemoryNK


@dataclass(frozen=True)
class NKEnvironmentRunResult:
    """Generated exogenous path and the unchanged sequence-runner result.

    Environment latent states and regime labels are experimenter-facing
    metadata in ``trajectory``.  They are generated before the policy runner
    starts and are never part of its decision view.
    """

    trajectory: EnvironmentTrajectoryNK
    execution: NKProductionRunResult | NKLearningRunResult | NKTeachingRunResult | NKInformationRunResult | NKNembhardDirectRunResult


@dataclass(frozen=True)
class NKNembhardDirectEpisodeRecord:
    mechanism_id: str
    period: int
    problem_id: str
    requirements: tuple[float, ...]
    ces_weights: tuple[float, ...]
    allocation: ProductiveAllocationNK
    duration: float
    experience_before: tuple[tuple[float, ...], ...]
    productivity_before: tuple[tuple[float, ...], ...]
    individual_outputs: tuple[tuple[float, ...], ...]
    outputs: tuple[float, ...]
    experience_increment: tuple[tuple[float, ...], ...]
    experience_after: tuple[tuple[float, ...], ...]
    functional_result: FunctionalResultNK
    ces_reward: float
    organization_effort_budget: float
    problem_effort_budget: float
    effective_collective_budget: float
    individual_effort_limits: tuple[float, ...]
    individual_effort_used: tuple[float, ...]
    productive_effort_used: float
    effective_work_used: float
    unused_collective_capacity: float
    router_id: str | None = None
    router_action_id: int | None = None
    router_candidate_count: int | None = None
    router_rank: tuple[float, float, float, float] | None = None
    router_predicted_outputs: tuple[float, ...] | None = None
    router_exploratory: bool | None = None
    adaptive_estimator_before: ProductivityEstimatorStateNK | None = None
    adaptive_estimator_after: ProductivityEstimatorStateNK | None = None
    adaptive_observations: tuple[tuple[float | None, ...], ...] | None = None
    router_observable_experience: tuple[tuple[float, ...], ...] | None = None


@dataclass(frozen=True)
class NKNembhardDirectRunResult:
    mechanism_id: str
    agent_ids: tuple[str, ...]
    skill_ids: tuple[str, ...]
    effort_intensity_unit: str
    duration_unit: str
    exposure_unit: str
    output_unit: str
    requirement_unit: str
    initial_experience: tuple[tuple[float, ...], ...]
    final_experience: tuple[tuple[float, ...], ...]
    profile_k: tuple[tuple[float, ...], ...]
    profile_p: tuple[tuple[float, ...], ...]
    profile_r: tuple[tuple[float, ...], ...]
    records: tuple[NKNembhardDirectEpisodeRecord, ...]
    router_id: str | None = None
    adaptive_router_config: NembhardAdaptiveRouterConfigNK | None = None
    final_productivity_estimator: ProductivityEstimatorStateNK | None = None


def run_nk_production_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...] | None = None,
    *,
    max_candidates: int,
    environment: ExogenousEnvironmentConfigNK | None = None,
    environment_seed: int | None = None,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
    individual_learning: bool = False,
    organizational_learning: bool = True,
    learning_profile: LearningProfileNK | None = None,
    teaching_enabled: bool = False,
    teaching_efficacy: TeachingEfficacyNK | None = None,
    teaching_parameters: TeachingParametersNK = TeachingParametersNK(),
    explicit_actions: tuple[JointActionNK, ...] | None = None,
    policy: P0ProductionOnlyPolicyNK | P1FixedTeachingNK | P2AdaptiveTeachingNK | None = None,
    policy_parameters: TeachingPolicyParametersNK = TeachingPolicyParametersNK(),
    initial_policy_memory: OrganizationMemoryNK | None = None,
    information_mode: str | None = None,
    observation_parameters: CompetenceObservationParametersNK = CompetenceObservationParametersNK(),
    information_seed: int = 0,
    mechanism_id: str = "mis_v2",
    nembhard_execution: NembhardDirectExecutionNK | None = None,
    router_id: str | None = None,
    adaptive_router_config: NembhardAdaptiveRouterConfigNK | None = None,
) -> NKProductionRunResult | NKLearningRunResult | NKTeachingRunResult | NKInformationRunResult | NKEnvironmentRunResult | NKNembhardDirectRunResult:
    """Run episodes over either a frozen sequence or generated environment.

    P0 receives actual competence as its estimate at each decision (the
    perfect-information condition). By default, this remains the Phase 2
    frozen-competence path and retains its result/serialization contract.
    Setting ``individual_learning=True`` requires an N×K MIS-v2 profile and
    returns a learning trace with post-production competence transitions.
    Supplying ``explicit_actions`` retains the N×K controlled-action path.
    Supplying a legacy P0/P1/P2 policy opts into automatic feasible joint
    action generation; P0 remains production-only. The historical default
    ``information_mode=None`` keeps the Phase 1–3C result contracts. Explicit
    ``perfect`` or ``imperfect`` modes use the information-aware trace and the
    existing scalar estimator, observation distributions, indexed random
    streams, and transition timing. The explicit-sequence path generates no
    environmental random draws.
    Generated demand is frozen first and then passed through exactly this
    explicit-sequence path. Existing callers need not adopt an environment.

    The explicit selector ``mechanism_id="mis_v2"`` follows this same
    historical path as the default. ``mechanism_id="nembhard_direct"`` opts
    into the separate direct-experience branch. It accepts explicit
    allocations or ``router_id="nembhard_oracle"`` / ``"nembhard_adaptive"``.
    The adaptive route estimates productivity from post-production
    observations and has independent exploration/noise streams. Neither
    automatic route uses HLS competence, P0/P1/P2, MIS-v2 or teaching.
    """
    if not isinstance(mechanism_id, str) or mechanism_id not in {"mis_v2", "nembhard_direct"}:
        raise ValueError("mechanism_id must be 'mis_v2' or 'nembhard_direct'")
    if mechanism_id == "mis_v2" and nembhard_execution is not None:
        raise ValueError("nembhard_execution requires mechanism_id='nembhard_direct'")
    if router_id is not None and (mechanism_id != "nembhard_direct" or router_id not in {"nembhard_oracle", "nembhard_adaptive"}):
        raise ValueError("router_id must be omitted, 'nembhard_oracle', or 'nembhard_adaptive' with mechanism_id='nembhard_direct'")
    if adaptive_router_config is not None and not isinstance(adaptive_router_config, NembhardAdaptiveRouterConfigNK):
        raise TypeError("adaptive_router_config must be NembhardAdaptiveRouterConfigNK")
    if router_id == "nembhard_adaptive" and adaptive_router_config is None:
        raise ValueError("nembhard_adaptive requires adaptive_router_config")
    if router_id != "nembhard_adaptive" and adaptive_router_config is not None:
        raise ValueError("adaptive_router_config requires router_id='nembhard_adaptive'")
    if mechanism_id == "nembhard_direct":
        if nembhard_execution is None:
            raise ValueError("Nembhard Direct requires nembhard_execution configuration")
        if not isinstance(nembhard_execution, NembhardDirectExecutionNK):
            raise TypeError("nembhard_execution must be NembhardDirectExecutionNK")
        if (individual_learning or learning_profile is not None or teaching_enabled
                or teaching_efficacy is not None or explicit_actions is not None
                or policy is not None or initial_policy_memory is not None
                or information_mode is not None
                or (router_id is None and per_agent_effort_choices is not None)
                or not organizational_learning
                or teaching_parameters != TeachingParametersNK()
                or policy_parameters != TeachingPolicyParametersNK()
                or observation_parameters != CompetenceObservationParametersNK()
                or information_seed != 0):
            raise ValueError(
                "Nembhard Direct does not accept MIS-v2, teaching, P0/P1/P2, "
                "competence estimation or their policy controls"
            )
        if router_id in {"nembhard_oracle", "nembhard_adaptive"} and nembhard_execution.allocations:
            raise ValueError(f"{router_id} selects allocations; supply an empty allocations tuple")
        if router_id is None and not nembhard_execution.allocations:
            raise ValueError("explicit Nembhard execution requires allocations")
    if environment is not None:
        if problems is not None:
            raise ValueError("supply either problems or environment, not both")
        if environment_seed is None:
            raise ValueError("environment_seed is required with an environment")
        trajectory = generate_environment_trajectory_nk(environment, seed=environment_seed)
        execution = run_nk_production_sequence(
            organization, trajectory.problems, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
            individual_learning=individual_learning,
            organizational_learning=organizational_learning,
            learning_profile=learning_profile,
            teaching_enabled=teaching_enabled,
            teaching_efficacy=teaching_efficacy,
            teaching_parameters=teaching_parameters,
            explicit_actions=explicit_actions,
            policy=policy,
            policy_parameters=policy_parameters,
            initial_policy_memory=initial_policy_memory,
            information_mode=information_mode,
            observation_parameters=observation_parameters,
            information_seed=information_seed,
            mechanism_id=mechanism_id,
            nembhard_execution=nembhard_execution,
            router_id=router_id,
            adaptive_router_config=adaptive_router_config,
        )
        return NKEnvironmentRunResult(trajectory, execution)
    if environment_seed is not None:
        raise ValueError("environment_seed requires an environment")
    if not problems:
        raise ValueError("problem sequence must be non-empty")
    if mechanism_id == "nembhard_direct":
        assert nembhard_execution is not None
        return _run_nk_nembhard_direct_sequence(
            organization, problems, nembhard_execution,
            max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
            router_id=router_id,
            adaptive_router_config=adaptive_router_config,
        )
    initial = organization.initial_state()
    if information_mode is not None:
        if information_mode not in {"perfect", "imperfect"}:
            raise ValueError("information_mode must be 'perfect' or 'imperfect'")
        if not isinstance(information_seed, int):
            raise ValueError("information_seed must be an integer")
        if policy is not None and explicit_actions is not None:
            raise ValueError("policy selection and explicit_actions are mutually exclusive")
        return _run_nk_information_sequence(
            organization, problems, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
            individual_learning=individual_learning,
            organizational_learning=organizational_learning,
            learning_profile=learning_profile,
            teaching_enabled=teaching_enabled,
            teaching_efficacy=teaching_efficacy,
            teaching_parameters=teaching_parameters,
            explicit_actions=explicit_actions,
            policy=policy,
            policy_parameters=policy_parameters,
            initial_policy_memory=initial_policy_memory,
            information_mode=information_mode,
            observation_parameters=observation_parameters,
            seed=information_seed,
        )
    if learning_profile is not None:
        learning_profile.validate_dimensions(initial.n_agents, initial.n_skills)
    if policy is not None and explicit_actions is not None:
        raise ValueError("policy selection and explicit_actions are mutually exclusive")
    if policy is not None:
        return _run_nk_policy_sequence(
            organization, problems, policy,
            max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
            individual_learning=individual_learning,
            organizational_learning=organizational_learning,
            learning_profile=learning_profile,
            teaching_enabled=teaching_enabled,
            teaching_efficacy=teaching_efficacy,
            teaching_parameters=teaching_parameters,
            policy_parameters=policy_parameters,
            initial_policy_memory=initial_policy_memory,
        )
    if initial_policy_memory is not None:
        raise ValueError("initial_policy_memory requires a coordination policy")
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


def _run_nk_information_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    *,
    max_candidates: int,
    per_agent_effort_choices,
    individual_learning: bool,
    organizational_learning: bool,
    learning_profile: LearningProfileNK | None,
    teaching_enabled: bool,
    teaching_efficacy: TeachingEfficacyNK | None,
    teaching_parameters: TeachingParametersNK,
    explicit_actions: tuple[JointActionNK, ...] | None,
    policy: P0ProductionOnlyPolicyNK | P1FixedTeachingNK | P2AdaptiveTeachingNK | None,
    policy_parameters: TeachingPolicyParametersNK,
    initial_policy_memory: OrganizationMemoryNK | None,
    information_mode: str,
    observation_parameters: CompetenceObservationParametersNK,
    seed: int,
) -> NKInformationRunResult:
    """Information-aware extension; the legacy default runner is untouched."""
    initial = organization.initial_state()
    n, k = initial.n_agents, initial.n_skills
    if any(len(problem.requirements) != k for problem in problems):
        raise ValueError("every problem must match organization K")
    if individual_learning:
        if learning_profile is None:
            raise ValueError("MIS-v2 ON requires a LearningProfileNK")
        learning_profile.validate_dimensions(n, k)
    if learning_profile is not None:
        learning_profile.validate_dimensions(n, k)
    if explicit_actions is not None and len(explicit_actions) != len(problems):
        raise ValueError("explicit_actions must contain one complete action per problem")
    if explicit_actions is not None and any(
        action.teaching is not None and not teaching_enabled for action in explicit_actions
    ):
        raise ValueError("teaching actions require teaching_enabled=True")

    selected_policy = policy or P0ProductionOnlyPolicyNK()
    policy_can_teach = not isinstance(selected_policy, P0ProductionOnlyPolicyNK)
    available_teaching = teaching_enabled and policy_can_teach
    if explicit_actions is not None:
        available_teaching = teaching_enabled
    if available_teaching:
        if teaching_efficacy is None:
            raise ValueError("teaching-enabled execution requires teaching_efficacy")
        teaching_efficacy.validate_identifiers(initial.agent_ids, initial.skill_ids)
    elif any(action.teaching is not None for action in explicit_actions or ()):
        if teaching_efficacy is None:
            raise ValueError("teaching actions require teaching_efficacy")
        teaching_efficacy.validate_identifiers(initial.agent_ids, initial.skill_ids)
    if initial_policy_memory is not None and policy is None:
        raise ValueError("initial_policy_memory requires a coordination policy")

    if information_mode == "perfect":
        actual = initial.competence_real
        posterior = None
    else:
        actual = initial.competence_real
        posterior = initialize_competence_posterior_nk(
            initial.competence_estimated, observation_parameters,
        )
    estimate = actual if posterior is None else posterior_mean_matrix_nk(posterior)
    state = OrganizationStateNK(initial.agent_ids, initial.skill_ids, actual, estimate)
    memory = initial_policy_memory or OrganizationMemoryNK()
    records: list[NKInformationEpisodeRecord] = []

    for period, problem in enumerate(problems):
        supplied_action = None if explicit_actions is None else explicit_actions[period]
        catalog_teaching_effort = (
            policy_parameters.effort if supplied_action is None or supplied_action.teaching is None
            else supplied_action.teaching.effort
        )
        production_entries = enumerate_productive_action_entries_nk(
            organization, problem, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        actions = enumerate_feasible_joint_actions_nk(
            organization, problem, max_candidates=max_candidates,
            teaching_enabled=available_teaching,
            teaching_efficacy=teaching_efficacy if available_teaching else None,
            teaching_effort=catalog_teaching_effort,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        if explicit_actions is None:
            view = NKDecisionView(
                period=period, periods_remaining=len(problems) - period,
                problem_id=problem.problem_id, agent_ids=state.agent_ids,
                skill_ids=state.skill_ids, requirements=problem.requirements,
                estimated_competencies=state.competence_estimated,
                feasible_actions=actions,
            )
            action = selected_policy.choose(view, memory, policy_parameters)
            if action not in actions:
                raise ValueError("policy returned an infeasible joint action")
            joint_action_id = actions.index(action)
        else:
            action = supplied_action
            if action not in actions:
                raise ValueError("explicit joint action is not feasible in this information-mode run")
            joint_action_id = None
        try:
            action_id = next(identifier for identifier, allocation in production_entries
                             if allocation == action.production)
        except StopIteration as exc:
            raise ValueError("selected production allocation is not in the feasible catalogue") from exc

        allocation = action.production
        effective_budget = min(organization.collective_effort_budget, problem.resource_budget)
        individual_used, total_used, unused = validate_joint_action_resources_nk(
            allocation, action.teaching, agent_ids=state.agent_ids,
            collective_budget=effective_budget, individual_limits=organization.effort_limits,
            efficacy=teaching_efficacy if action.teaching is not None else None,
        )
        actual_before = state.competence_real
        estimated_before = state.competence_estimated
        variance_before = None if posterior is None else posterior_variance_matrix_nk(posterior)

        # Production and outcomes always use actual pre-transition competence.
        outputs = productive_outputs_nk(actual_before, allocation)
        individual_outputs = tuple(tuple(
            allocation[i][skill] * actual_before[i][skill] for skill in range(k)
        ) for i in range(n))
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)  # type: ignore[arg-type]
        production_effort = sum(sum(row) for row in allocation)
        teaching_effort = 0.0 if action.teaching is None else 2.0 * action.teaching.effort

        observations = tuple(tuple(
            allocation[i][skill] * actual_before[i][skill]
            + observation_parameters.production_observation_noise_sd
            * indexed_normal_innovation(seed, period, 0, i, skill)
            for skill in range(k)
        ) for i in range(n))

        post_mis = actual_before
        mis_increment = tuple(tuple(0.0 for _ in range(k)) for _ in range(n))
        if individual_learning:
            assert learning_profile is not None
            post_mis = mis_v2_transition_nk(actual_before, allocation, learning_profile)
            mis_increment = tuple(tuple(post_mis[i][skill] - actual_before[i][skill]
                                        for skill in range(k)) for i in range(n))
        if posterior is not None:
            posterior = assimilate_production_observations_nk(
                posterior, allocation, observations,
                observation_parameters.production_observation_noise_sd,
            )
            if individual_learning:
                assert learning_profile is not None
                posterior = predict_mis_v2_nk(posterior, allocation, learning_profile.eta)

        teaching_observation = None
        teaching_increment = tuple(tuple(0.0 for _ in range(k)) for _ in range(n))
        memory_before = memory.efficacy
        actual_after = post_mis
        organization_updated = False
        if action.teaching is not None:
            assert teaching_efficacy is not None
            transition = teaching_transition_nk(
                post_mis, action.teaching, teaching_efficacy, teaching_parameters,
            )
            actual_after = transition.competence_after
            teaching_increment = transition.competence_increment
            learner, skill = transition.learner_index, transition.skill_index
            teaching_observation = (
                transition.competence_gain
                + observation_parameters.outcome_noise_sd
                * _training_noise(seed, period, transition.teacher_index, learner, skill)
            )
            estimate_after_mis = (post_mis if posterior is None
                                  else posterior_mean_matrix_nk(posterior))
            signal = formative_efficacy_signal_nk(
                competence_after_mis=estimate_after_mis[learner][skill],
                observed_teaching_gain=teaching_observation,
                transfer_rate=teaching_parameters.transfer_rate,
                effort=action.teaching.effort,
                prior_mean=policy_parameters.efficacy_prior_mean,
            )
            if organizational_learning:
                relation = (action.teaching.teacher_id, action.teaching.learner_id,
                            action.teaching.skill_id)
                memory = memory.update(relation, signal)
                organization_updated = True
                if posterior is not None:
                    efficacy_estimate = memory.estimate(
                        relation, policy_parameters.efficacy_prior_mean,
                    )
                    posterior_rows = [list(row) for row in posterior]
                    posterior_rows[learner][skill] = _push_posterior(
                        posterior_rows[learner][skill], efficacy_estimate,
                        teaching_parameters.transfer_rate, action.teaching.effort,
                    )
                    posterior = tuple(tuple(row) for row in posterior_rows)

        estimate_after = (actual_after if posterior is None
                          else posterior_mean_matrix_nk(posterior))
        variance_after = None if posterior is None else posterior_variance_matrix_nk(posterior)
        error = tuple(tuple(estimate_after[i][skill] - actual_after[i][skill]
                            for skill in range(k)) for i in range(n))
        state = OrganizationStateNK(state.agent_ids, state.skill_ids,
                                    actual_after, estimate_after)
        individual_used_period = tuple(sum(row) for row in allocation)
        production_record = NKProductionEpisodeRecord(
            period=period, problem_id=problem.problem_id,
            requirements=problem.requirements, competence_before=actual_before,
            competence_after=actual_after, action_id=action_id,
            allocation=allocation, individual_outputs=individual_outputs,
            outputs=outputs, functional_result=functional, ces_reward=reward,
            organization_effort_budget=organization.collective_effort_budget,
            problem_effort_budget=problem.resource_budget,
            effective_collective_budget=effective_budget,
            individual_effort_limits=organization.effort_limits,
            individual_effort_used=individual_used_period,
            productive_effort_used=production_effort,
            unused_collective_capacity=unused,
        )
        records.append(NKInformationEpisodeRecord(
            period=period, policy_name=selected_policy.name if explicit_actions is None else "EXPLICIT_ACTION",
            action_id=action_id, joint_action_id=joint_action_id, action=action,
            competence_actual_before=actual_before,
            competence_estimated_before=estimated_before,
            competence_variance_before=variance_before,
            production_observations=observations, production=production_record,
            teaching_observation=teaching_observation, mis_increment=mis_increment,
            competence_after_mis=post_mis, teaching_increment=teaching_increment,
            competence_actual_after=actual_after,
            competence_estimated_after=estimate_after,
            competence_variance_after=variance_after,
            estimation_error=error, efficacy_memory_before=memory_before,
            efficacy_memory_after=memory.efficacy,
            organization_updated=organization_updated,
            productive_effort_used=production_effort,
            teaching_resource_used=teaching_effort,
            total_resource_used=total_used,
            unused_collective_capacity=unused,
        ))
    return NKInformationRunResult(
        information_mode, tuple(records), state, posterior, memory,
    )


def _run_nk_policy_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    policy: P0ProductionOnlyPolicyNK | P1FixedTeachingNK | P2AdaptiveTeachingNK,
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None,
    individual_learning: bool,
    organizational_learning: bool,
    learning_profile: LearningProfileNK | None,
    teaching_enabled: bool,
    teaching_efficacy: TeachingEfficacyNK | None,
    teaching_parameters: TeachingParametersNK,
    policy_parameters: TeachingPolicyParametersNK,
    initial_policy_memory: OrganizationMemoryNK | None,
) -> NKTeachingRunResult:
    initial = organization.initial_state()
    if individual_learning and learning_profile is None:
        raise ValueError("MIS-v2 ON requires a LearningProfileNK")
    if learning_profile is not None:
        learning_profile.validate_dimensions(initial.n_agents, initial.n_skills)
    # P0 remains production-only even when the teaching mechanism is available.
    policies_can_teach = not isinstance(policy, P0ProductionOnlyPolicyNK)
    available_teaching = teaching_enabled and policies_can_teach
    if available_teaching:
        if teaching_efficacy is None:
            raise ValueError("teaching-enabled P1/P2 execution requires teaching_efficacy")
        teaching_efficacy.validate_identifiers(initial.agent_ids, initial.skill_ids)
    state = OrganizationStateNK(initial.agent_ids, initial.skill_ids,
                                initial.competence_real, initial.competence_real)
    memory = initial_policy_memory or OrganizationMemoryNK()
    records: list[NKTeachingEpisodeRecord] = []
    for period, problem in enumerate(problems):
        if len(problem.requirements) != state.n_skills:
            raise ValueError(f"problem {problem.problem_id} does not match organization K")
        production_entries = enumerate_productive_action_entries_nk(
            organization, problem, max_candidates=max_candidates,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        actions = enumerate_feasible_joint_actions_nk(
            organization, problem, max_candidates=max_candidates,
            teaching_enabled=available_teaching,
            teaching_efficacy=teaching_efficacy if available_teaching else None,
            teaching_effort=policy_parameters.effort,
            per_agent_effort_choices=per_agent_effort_choices,
        )
        view = NKDecisionView(
            period=period, periods_remaining=len(problems) - period,
            problem_id=problem.problem_id, agent_ids=state.agent_ids,
            skill_ids=state.skill_ids, requirements=problem.requirements,
            estimated_competencies=state.competence_estimated,
            feasible_actions=actions,
        )
        selected = policy.choose(view, memory, policy_parameters)
        if selected not in actions:
            raise ValueError("policy returned an infeasible joint action")
        joint_id = actions.index(selected)
        try:
            action_id = next(identifier for identifier, allocation in production_entries
                             if allocation == selected.production)
        except StopIteration as exc:
            raise AssertionError("selected production action is absent from its catalog") from exc

        allocation = selected.production
        effective_budget = min(organization.collective_effort_budget, problem.resource_budget)
        individual_used, total_used, unused = validate_joint_action_resources_nk(
            allocation, selected.teaching,
            agent_ids=state.agent_ids, collective_budget=effective_budget,
            individual_limits=organization.effort_limits,
            efficacy=teaching_efficacy if selected.teaching is not None else None,
        )
        before = state.competence_real
        outputs = productive_outputs_nk(before, allocation)
        individual_outputs = tuple(tuple(
            allocation[i][skill] * before[i][skill] for skill in range(state.n_skills)
        ) for i in range(state.n_agents))
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)  # type: ignore[arg-type]
        post_mis = before
        mis_increment = tuple(tuple(0.0 for _ in range(state.n_skills))
                              for _ in range(state.n_agents))
        if individual_learning:
            assert learning_profile is not None
            post_mis = mis_v2_transition_nk(before, allocation, learning_profile, enabled=True)
            mis_increment = tuple(tuple(post_mis[i][k] - before[i][k]
                                        for k in range(state.n_skills))
                                  for i in range(state.n_agents))
        after = post_mis
        teaching_increment = tuple(tuple(0.0 for _ in range(state.n_skills))
                                   for _ in range(state.n_agents))
        resolved_efficacy = formative_observation = None
        memory_before = memory.efficacy
        if selected.teaching is not None:
            assert teaching_efficacy is not None
            transition = teaching_transition_nk(
                post_mis, selected.teaching, teaching_efficacy, teaching_parameters,
            )
            after = transition.competence_after
            teaching_increment = transition.competence_increment
            resolved_efficacy = transition.efficacy
            # The legacy teaching observation defaults to zero added noise.
            # Its normalized signal is a relation-specific observation, not a
            # direct policy read of the private efficacy tensor.
            learner, skill = transition.learner_index, transition.skill_index
            formative_observation = formative_efficacy_signal_nk(
                competence_after_mis=post_mis[learner][skill],
                observed_teaching_gain=transition.competence_gain,
                transfer_rate=teaching_parameters.transfer_rate,
                effort=selected.teaching.effort,
                prior_mean=policy_parameters.efficacy_prior_mean,
            )
            relation = (selected.teaching.teacher_id, selected.teaching.learner_id,
                        selected.teaching.skill_id)
            if organizational_learning:
                memory = memory.update(relation, formative_observation)
        organization_updated = organizational_learning and selected.teaching is not None

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
        teaching_resource = 0.0 if selected.teaching is None else 2.0 * selected.teaching.effort
        records.append(NKTeachingEpisodeRecord(
            policy_name=policy.name, joint_action_id=joint_id,
            production=production, teaching_action=selected.teaching,
            productive_effort_used=production.productive_effort_used,
            teaching_resource_used=teaching_resource, total_resource_used=total_used,
            individual_resource_used=individual_used,
            unused_collective_capacity=unused, competence_after_mis=post_mis,
            mis_increment=mis_increment,
            competence_increment_from_teaching=teaching_increment,
            teaching_efficacy=resolved_efficacy,
            formative_efficacy_observation=formative_observation,
            efficacy_memory_before=memory_before, efficacy_memory_after=memory.efficacy,
            organization_updated=organization_updated,
        ))
        state = OrganizationStateNK(state.agent_ids, state.skill_ids, after, after)
    return NKTeachingRunResult(tuple(records), state)


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
            policy_name="EXPLICIT_ACTION", joint_action_id=None,
            production=production, teaching_action=joint.teaching,
            productive_effort_used=production.productive_effort_used,
            teaching_resource_used=teaching_resource, total_resource_used=total_used,
            individual_resource_used=individual_used,
            unused_collective_capacity=unused,
            competence_after_mis=post_mis, mis_increment=mis_increment,
            competence_increment_from_teaching=teaching_increment,
            teaching_efficacy=resolved_efficacy,
            formative_efficacy_observation=None,
            efficacy_memory_before=(), efficacy_memory_after=(),
            organization_updated=False,
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


def _run_nk_nembhard_direct_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    configuration: NembhardDirectExecutionNK,
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None,
    router_id: str | None,
    adaptive_router_config: NembhardAdaptiveRouterConfigNK | None,
) -> NKNembhardDirectRunResult:
    """Execute explicit, oracle, or estimate-based Nembhard allocations.

    ``organization`` supplies agent/skill identifiers and existing effort
    limits/budgets only. Its competence matrices are not read by this path.
    """
    n, k = len(organization.agent_ids), len(organization.skill_ids)
    configuration.profile.validate_dimensions(n, k)
    if router_id is None and len(configuration.allocations) != len(problems):
        raise ValueError("Nembhard allocations must contain one allocation per problem")
    if router_id is not None and router_id not in {"nembhard_oracle", "nembhard_adaptive"}:
        raise ValueError("unsupported Nembhard router_id")
    state = configuration.initial_state or NembhardDirectStateNK.zeros(n, k)
    state.validate_dimensions(n, k)
    units = configuration.unit_contract
    records: list[NKNembhardDirectEpisodeRecord] = []

    router = NembhardOracleRouterNK() if router_id == "nembhard_oracle" else None
    adaptive_router = NembhardAdaptiveRouterNK() if router_id == "nembhard_adaptive" else None
    if adaptive_router is not None and adaptive_router_config is None:
        raise ValueError("nembhard_adaptive requires adaptive_router_config")
    adaptive_estimator = None
    observation_rng = exploration_rng = None
    # Decision-visible D is reconstructed only from assignments executed in
    # this run. A caller-supplied latent initial D is not exposed as an
    # observable history.
    observable_experience = [[0.0] * k for _ in range(n)]
    previous_allocations: list[ProductiveAllocationNK] = []
    if adaptive_router_config is not None:
        adaptive_estimator = initialize_productivity_estimator_nk(
            n, k, adaptive_router_config.initial_productivity_estimate,
        )
        observation_rng = Random(adaptive_router_config.observation_seed)
        exploration_rng = Random(adaptive_router_config.exploration_seed)
    for period, problem in enumerate(problems):
        if len(problem.requirements) != k:
            raise ValueError(f"problem {problem.problem_id} does not match organization K")
        decision = None
        adaptive_decision = None
        estimator_before = adaptive_estimator
        observable_experience_before = tuple(tuple(row) for row in observable_experience)
        if router is None:
            if adaptive_router is None:
                allocation = configuration.allocations[period]
            else:
                assert adaptive_estimator is not None and adaptive_router_config is not None
                assert exploration_rng is not None
                adaptive_decision = adaptive_router.choose(
                    NembhardAdaptiveDecisionViewNK(
                        resources=OrganizationResourcesNK.from_organization(organization),
                        problem=problem,
                        estimator=adaptive_estimator,
                        previous_allocations=tuple(previous_allocations),
                        observable_experience=observable_experience_before,
                        period_duration=configuration.period_duration,
                    ),
                    epsilon=adaptive_router_config.epsilon,
                    rng=exploration_rng,
                    max_candidates=max_candidates,
                    per_agent_effort_choices=per_agent_effort_choices,
                )
                allocation = adaptive_decision.allocation
        else:
            decision = router.choose(
                NembhardOracleDecisionViewNK(
                    resources=OrganizationResourcesNK.from_organization(organization),
                    problem=problem,
                    experience=state,
                    profile=configuration.profile,
                    period_duration=configuration.period_duration,
                ),
                max_candidates=max_candidates,
                per_agent_effort_choices=per_agent_effort_choices,
            )
            allocation = decision.allocation
        if not validate_productive_allocation_nk(allocation, organization, problem):
            raise ValueError(f"Nembhard allocation at period {period} is infeasible")
        effort_by_agent = tuple(sum(row) for row in allocation)
        effort_used = sum(effort_by_agent)
        effective_budget = min(organization.collective_effort_budget, problem.resource_budget)
        if effort_used > effective_budget + TOL or any(
            effort_by_agent[i] > organization.effort_limits[i] + TOL for i in range(n)
        ):
            raise AssertionError("validated Nembhard allocation violates resource constraints")

        experience_before = state.experience
        outputs, productivity = nembhard_productive_outputs_nk(
            allocation, state, configuration.profile,
            period_duration=configuration.period_duration,
        )
        individual_outputs = tuple(tuple(
            allocation[i][skill] * productivity[i][skill] * configuration.period_duration
            for skill in range(k)
        ) for i in range(n))
        functional = evaluate_problem_nk(outputs, problem.requirements)
        reward = ces_reward_nk(outputs, problem.ces_weights)  # type: ignore[arg-type]

        next_state = advance_nembhard_experience_nk(
            state, allocation, period_duration=configuration.period_duration,
        )
        adaptive_observations = None
        if adaptive_router is not None:
            assert adaptive_estimator is not None
            assert adaptive_router_config is not None and observation_rng is not None
            work = tuple(tuple(value * configuration.period_duration for value in row)
                         for row in allocation)
            adaptive_observations = observe_nembhard_work_outputs_nk(
                work,
                individual_outputs,
                noise_stddev=adaptive_router_config.observation_noise_stddev,
                rng=observation_rng,
            )
            adaptive_estimator = update_productivity_estimator_nk(
                adaptive_estimator,
                work,
                adaptive_observations,
                minimum_observation_work=adaptive_router_config.minimum_observation_work,
            )
            previous_allocations.append(allocation)
            for i in range(n):
                for skill in range(k):
                    observable_experience[i][skill] += work[i][skill]
        increments = tuple(tuple(next_state.experience[i][skill] - experience_before[i][skill]
                                 for skill in range(k)) for i in range(n))
        records.append(NKNembhardDirectEpisodeRecord(
            mechanism_id="nembhard_direct_v0.1_hls_adaptation",
            period=period,
            problem_id=problem.problem_id,
            requirements=problem.requirements,
            ces_weights=problem.ces_weights,  # type: ignore[arg-type]
            allocation=allocation,
            duration=configuration.period_duration,
            experience_before=experience_before,
            productivity_before=productivity,
            individual_outputs=individual_outputs,
            outputs=outputs,
            experience_increment=increments,
            experience_after=next_state.experience,
            functional_result=functional,
            ces_reward=reward,
            organization_effort_budget=organization.collective_effort_budget,
            problem_effort_budget=problem.resource_budget,
            effective_collective_budget=effective_budget,
            individual_effort_limits=organization.effort_limits,
            individual_effort_used=effort_by_agent,
            productive_effort_used=effort_used,
            effective_work_used=effort_used * configuration.period_duration,
            unused_collective_capacity=max(0.0, effective_budget - effort_used),
            router_id=(decision.router_id if decision is not None else
                       None if adaptive_decision is None else adaptive_decision.router_id),
            router_action_id=(decision.catalog_action_id if decision is not None else
                              None if adaptive_decision is None else adaptive_decision.catalog_action_id),
            router_candidate_count=(decision.feasible_candidate_count if decision is not None else
                                    None if adaptive_decision is None else adaptive_decision.feasible_candidate_count),
            router_rank=(decision.rank if decision is not None else
                         None if adaptive_decision is None else adaptive_decision.rank),
            router_predicted_outputs=(decision.predicted_outputs if decision is not None else
                                      None if adaptive_decision is None else adaptive_decision.predicted_outputs),
            router_exploratory=(None if adaptive_decision is None else adaptive_decision.exploratory),
            adaptive_estimator_before=estimator_before,
            adaptive_estimator_after=adaptive_estimator,
            adaptive_observations=adaptive_observations,
            router_observable_experience=(observable_experience_before
                                          if adaptive_router is not None else None),
        ))
        state = next_state

    return NKNembhardDirectRunResult(
        mechanism_id="nembhard_direct_v0.1_hls_adaptation",
        agent_ids=organization.agent_ids,
        skill_ids=organization.skill_ids,
        effort_intensity_unit=units.effort_intensity_unit,
        duration_unit=units.duration_unit,
        exposure_unit=units.exposure_unit,
        output_unit=units.output_unit,
        requirement_unit=units.requirement_unit,
        initial_experience=(configuration.initial_state.experience
                            if configuration.initial_state is not None
                            else NembhardDirectStateNK.zeros(n, k).experience),
        final_experience=state.experience,
        profile_k=configuration.profile.asymptotic_productivity,
        profile_p=configuration.profile.prior_experience,
        profile_r=configuration.profile.experience_scale,
        records=tuple(records),
        router_id=router_id,
        adaptive_router_config=adaptive_router_config,
        final_productivity_estimator=adaptive_estimator,
    )


_SerializableNKResult = (
    NKProductionRunResult
    | NKLearningRunResult
    | NKTeachingRunResult
    | NKInformationRunResult
    | NKNembhardDirectRunResult
)


def _serialize_nk_result(result: _SerializableNKResult) -> str:
    """Encode an N×K result using the shared replay-stable JSON contract."""
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), allow_nan=False)


def serialize_nk_production_result(result: NKProductionRunResult) -> str:
    """Stable JSON serialization for exact deterministic replay checks."""
    return _serialize_nk_result(result)


def serialize_nk_learning_result(result: NKLearningRunResult) -> str:
    """Stable JSON serialization for MIS-v2 ON trajectories."""
    return _serialize_nk_result(result)


def serialize_nk_teaching_result(result: NKTeachingRunResult) -> str:
    """Stable JSON serialization for explicit N×K joint-action trajectories."""
    return _serialize_nk_result(result)


def serialize_nk_information_result(result: NKInformationRunResult) -> str:
    """Stable JSON serialization for explicit perfect/imperfect-information runs."""
    return _serialize_nk_result(result)


def serialize_nk_nembhard_direct_result(result: NKNembhardDirectRunResult) -> str:
    """Stable JSON serialization for Nembhard Direct adapted trajectories."""
    return _serialize_nk_result(result)
