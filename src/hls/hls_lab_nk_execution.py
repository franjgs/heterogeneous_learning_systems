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


def run_nk_production_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
    individual_learning: bool = False,
    learning_profile: LearningProfileNK | None = None,
) -> NKProductionRunResult | NKLearningRunResult:
    """Run deterministic P0 episodes over a caller-frozen exogenous sequence.

    P0 receives actual competence as its estimate at each decision (the
    perfect-information condition). By default, this remains the Phase 2
    frozen-competence path and retains its result/serialization contract.
    Setting ``individual_learning=True`` requires an N×K MIS-v2 profile and
    returns a learning trace with post-production competence transitions.
    Neither path performs teaching, environment draws, or observation updates.
    """
    if not problems:
        raise ValueError("problem sequence must be non-empty")
    initial = organization.initial_state()
    if learning_profile is not None:
        learning_profile.validate_dimensions(initial.n_agents, initial.n_skills)
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
