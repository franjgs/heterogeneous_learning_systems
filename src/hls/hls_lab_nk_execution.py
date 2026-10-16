"""Production-only N×K execution using the Phase 1 geometry contracts.

This additive path intentionally supports only frozen-competence,
perfect-information P0 episodes. It reuses the Phase 1 state, problem,
allocation validator and ordered catalogue; it does not generalize MIS-v2,
teaching, P1/P2, estimation, or environment generation.
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


def run_nk_production_sequence(
    organization: OrganizationConfigNK,
    problems: tuple[ProblemSpecNK, ...],
    *,
    max_candidates: int,
    per_agent_effort_choices: tuple[tuple[tuple[float, ...], ...], ...] | None = None,
) -> NKProductionRunResult:
    """Run deterministic P0 episodes over a caller-frozen exogenous sequence.

    P0 receives the actual competence matrix as a perfect-information estimate,
    exactly as the legacy v1 control does. No competence transition, teaching,
    environment draw, or observation update occurs in this execution path.
    """
    if not problems:
        raise ValueError("problem sequence must be non-empty")
    initial = organization.initial_state()
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


def serialize_nk_production_result(result: NKProductionRunResult) -> str:
    """Stable JSON serialization for exact deterministic replay checks."""
    return json.dumps(asdict(result), sort_keys=True, separators=(",", ":"), allow_nan=False)
