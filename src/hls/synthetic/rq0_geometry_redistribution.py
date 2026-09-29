"""Frozen exact RQ0 family varying only zero-sum T2 competence redistribution.

This configuration layer reuses the already frozen mean-preserving opportunity
primitives from ``rq0_opportunity_coupling``.  It adds no G0 physics and does
not modify the prior lambda-family module or its provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping

from .components import (
    A1MixtureOpportunityKernel,
    A1ResourceModel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
    FiniteTaskSequence,
    ScheduledSaturatingDevelopmentKernel,
)
from .diagnostics import audit_optimal_hls_reachability
from .environment import SyntheticEnvironment
from .exact import (
    EXACT_TOL,
    ExactProblem,
    _physical_next_state,
    _task,
    solve_exact_hls,
    solve_exact_sep_omega,
    solve_exact_strong_sep,
)
from .interfaces import DevelopmentDecision, Opportunity
from .randomness import SeededRandomSource
from .rq0_opportunity_coupling import (
    BETA,
    EPSILON,
    ETA,
    KAPPA,
    LEARNERS,
    LEARNER_INDICES,
    MEAN_OPPORTUNITY,
    TARGET_BY_TIME,
    TASKS,
    TASK_INDICES,
    TERMINAL_TASK,
    CouplingWorld,
    _development_branch,
    executor_values,
    sep_admissible_hls_exists,
)
from .state import WorldState


TASK_SEQUENCE = (1, 2)
LAMBDA = 1.0
ALPHA_GRID = tuple(index / 20.0 for index in range(21))


@dataclass(frozen=True)
class DevelopmentSuccessor:
    available: bool
    decision: DevelopmentDecision
    competence: tuple[tuple[float, ...], ...]


@dataclass(frozen=True)
class GeometryNodeEvaluation:
    state: WorldState
    task: Hashable
    rewards: Mapping[Hashable, float]
    q_values: Mapping[Hashable, float]
    greedy_actions: frozenset[Hashable]
    hls_actions: frozenset[Hashable]
    opportunity_probabilities: Mapping[Hashable, float]
    w0: float
    w1: float
    d_star: float
    optimal_development_o0: frozenset[DevelopmentDecision]
    optimal_development_o1: frozenset[DevelopmentDecision]
    successors: tuple[DevelopmentSuccessor, ...]


@dataclass(frozen=True)
class GeometryEvaluation:
    alpha: float
    competence: tuple[tuple[float, ...], ...]
    j_hls: float
    j_sep_min: float
    j_sep_max: float
    j_sep_omega: float
    phi: float
    hls_initial_actions: frozenset[Hashable]
    sep_initial_actions: frozenset[Hashable]
    sep_admissible_hls_exists: bool
    regime: str
    root_delta_r: float
    root_delta_p: float
    root_local_identity_residual: float
    nodes: tuple[GeometryNodeEvaluation, ...]


def _validate_alpha(alpha: float) -> None:
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must lie in [0, 1]")


def competence_matrix(alpha: float) -> tuple[tuple[float, float], ...]:
    """The frozen zero-sum redistribution of T2 competence."""
    _validate_alpha(alpha)
    return (
        (0.80, 0.80 - 0.20 * alpha),
        (0.60, 0.60 + 0.20 * alpha),
    )


def build_world(alpha: float) -> CouplingWorld:
    """Build a world where alpha changes only the competence matrix."""
    competence = competence_matrix(alpha)
    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence(TASK_SEQUENCE),
        competence=BoundedMatrixCompetence(competence),
        opportunities=A1MixtureOpportunityKernel(
            MEAN_OPPORTUNITY,
            executor_values(),
            rho=LAMBDA,
        ),
        development=ScheduledSaturatingDevelopmentKernel(
            LEARNER_INDICES,
            TASK_INDICES,
            TARGET_BY_TIME,
            ETA,
        ),
        reward=CompetenceRewardModel(LEARNER_INDICES, TASK_INDICES),
        resources=A1ResourceModel(kappa=KAPPA, beta=BETA),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )
    return CouplingWorld(
        lambda_value=LAMBDA,
        environment=environment,
        problem=ExactProblem(
            environment=environment,
            operational_actions=LEARNERS,
            horizon=len(TASK_SEQUENCE),
            terminal_task=TERMINAL_TASK,
        ),
    )


def _development_successors(
    problem: ExactProblem,
    state: WorldState,
    available: bool,
    decisions: frozenset[DevelopmentDecision],
) -> tuple[DevelopmentSuccessor, ...]:
    opportunity = Opportunity(available)
    return tuple(
        DevelopmentSuccessor(
            available=available,
            decision=decision,
            competence=_physical_next_state(
                problem, state, opportunity, decision
            ).competence,
        )
        for decision in sorted(
            decisions,
            key=lambda item: (str(item.recipient), str(item.competence)),
        )
    )


def _node_evaluation(problem: ExactProblem, state: WorldState) -> GeometryNodeEvaluation:
    task = _task(problem, state)
    hls = solve_exact_hls(problem, initial_state=state)
    rewards = {
        action: problem.environment.reward.operational_reward(state, task, action)
        for action in problem.operational_actions
    }
    best_reward = max(rewards.values())
    greedy = frozenset(
        action
        for action, reward in rewards.items()
        if abs(reward - best_reward) <= EXACT_TOL
    )
    probabilities = {
        action: problem.environment.opportunities.probability(state, task, action, ())
        for action in problem.operational_actions
    }
    w0, development_o0 = _development_branch(problem, state, False)
    w1, development_o1 = _development_branch(problem, state, True)
    successors = (
        _development_successors(problem, state, False, development_o0)
        + _development_successors(problem, state, True, development_o1)
    )
    return GeometryNodeEvaluation(
        state=state,
        task=task,
        rewards=rewards,
        q_values=hls.action_values,
        greedy_actions=greedy,
        hls_actions=hls.optimal_actions,
        opportunity_probabilities=probabilities,
        w0=w0,
        w1=w1,
        d_star=w1 - w0,
        optimal_development_o0=development_o0,
        optimal_development_o1=development_o1,
        successors=successors,
    )


def evaluate_alpha(alpha: float) -> GeometryEvaluation:
    """Exact evaluation of one frozen alpha point; no sampling."""
    world = build_world(alpha)
    initial = world.environment.initial_state()
    hls = solve_exact_hls(world.problem, initial_state=initial)
    sep = solve_exact_strong_sep(world.problem, initial_state=initial)
    omega = solve_exact_sep_omega(world.problem, initial_state=initial)
    audit = audit_optimal_hls_reachability(world.problem, initial_state=initial)
    nodes = tuple(
        _node_evaluation(world.problem, item.state)
        for item in sorted(
            audit.states,
            key=lambda item: (
                item.state.time,
                repr(item.state.competence),
                item.state.resources,
            ),
        )
    )
    root = next(node for node in nodes if node.state.time == 0)
    delta_r = root.rewards["M1"] - root.rewards["M2"]
    delta_p = (
        root.opportunity_probabilities["M2"]
        - root.opportunity_probabilities["M1"]
    )
    local_residual = (
        root.q_values["M2"]
        - root.q_values["M1"]
        - (-delta_r + delta_p * root.d_star)
    )
    phi = hls.value - sep.value_max
    compatible = sep_admissible_hls_exists(world.problem)
    if phi > EXACT_TOL and not compatible:
        regime = "HLS_INTEGRATED"
    elif abs(phi) <= EXACT_TOL and compatible:
        regime = "SEP_REDUCIBLE"
    else:
        regime = "REQUIRES_INVESTIGATION"
    return GeometryEvaluation(
        alpha=alpha,
        competence=competence_matrix(alpha),
        j_hls=hls.value,
        j_sep_min=sep.value_min,
        j_sep_max=sep.value_max,
        j_sep_omega=omega.value,
        phi=phi,
        hls_initial_actions=hls.optimal_actions,
        sep_initial_actions=sep.immediate_optimal_actions,
        sep_admissible_hls_exists=compatible,
        regime=regime,
        root_delta_r=delta_r,
        root_delta_p=delta_p,
        root_local_identity_residual=local_residual,
        nodes=nodes,
    )


def run_grid() -> tuple[GeometryEvaluation, ...]:
    """Evaluate the single frozen 21-point alpha grid in declaration order."""
    return tuple(evaluate_alpha(alpha) for alpha in ALPHA_GRID)
