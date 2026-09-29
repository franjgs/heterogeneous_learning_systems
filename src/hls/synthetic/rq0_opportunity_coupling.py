"""Frozen exact RQ0 family varying only routing--opportunity coupling.

This module composes existing G0 components and evaluates them through the
existing exact solvers.  It adds no world physics and contains no result-based
configuration branches.
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
    _admissible_development_actions,
    _physical_next_state,
    _terminal_value,
    _task,
    solve_exact_hls,
    solve_exact_sep_omega,
    solve_exact_strong_sep,
)
from .interfaces import DevelopmentDecision, Opportunity
from .randomness import SeededRandomSource
from .state import WorldState


LEARNERS = ("M1", "M2")
TASKS = (1, 2)
LEARNER_INDICES = {learner: index for index, learner in enumerate(LEARNERS)}
TASK_INDICES = {task: index for index, task in enumerate(TASKS)}

# Frozen independently of the observed lambda results.  Values reuse the C1
# reference topology and the .5 RQ0 baseline; EPSILON is the declared,
# non-extreme symmetric design choice documented in the protocol.
INITIAL_COMPETENCE = ((0.80, 0.80), (0.60, 0.60))
TASK_SEQUENCE = (1, 2)
TERMINAL_TASK = 1
TARGET_BY_TIME = {0: 2, 1: 1}
ETA = 0.75
KAPPA = 0.0
BETA = 1.0
MEAN_OPPORTUNITY = {1: 0.50, 2: 0.50}
EPSILON = {1: 0.50, 2: 0.50}
LAMBDA_GRID = tuple(index / 20.0 for index in range(21))


@dataclass(frozen=True)
class CouplingWorld:
    """One physical world in the frozen lambda family."""

    lambda_value: float
    environment: SyntheticEnvironment
    problem: ExactProblem


@dataclass(frozen=True)
class NodeEvaluation:
    """Exact HLS-node quantities over an HLS-optimal positive-probability tree."""

    state: WorldState
    task: Hashable
    greedy_actions: frozenset[Hashable]
    hls_actions: frozenset[Hashable]
    opportunity_probabilities: Mapping[Hashable, float]
    w0: float
    w1: float
    d_star: float


@dataclass(frozen=True)
class CouplingEvaluation:
    lambda_value: float
    j_hls: float
    j_sep_min: float
    j_sep_max: float
    j_sep_omega: float
    phi: float
    hls_initial_actions: frozenset[Hashable]
    sep_initial_actions: frozenset[Hashable]
    sep_admissible_hls_exists: bool
    regime: str
    nodes: tuple[NodeEvaluation, ...]


def _validate_lambda(lambda_value: float) -> None:
    if not 0.0 <= lambda_value <= 1.0:
        raise ValueError("lambda must lie in [0, 1]")


def executor_values() -> dict[tuple[str, int], float]:
    """Return the fixed, mean-preserving executor primitives."""
    return {
        (learner, task): MEAN_OPPORTUNITY[task]
        + (-0.5 if learner == "M1" else 0.5) * EPSILON[task]
        for learner in LEARNERS
        for task in TASKS
    }


def build_world(lambda_value: float) -> CouplingWorld:
    """Build a family member; lambda is its only varying primitive."""
    _validate_lambda(lambda_value)
    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence(TASK_SEQUENCE),
        competence=BoundedMatrixCompetence(INITIAL_COMPETENCE),
        opportunities=A1MixtureOpportunityKernel(
            MEAN_OPPORTUNITY,
            executor_values(),
            rho=lambda_value,
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
        lambda_value=lambda_value,
        environment=environment,
        problem=ExactProblem(
            environment=environment,
            operational_actions=LEARNERS,
            horizon=len(TASK_SEQUENCE),
            terminal_task=TERMINAL_TASK,
        ),
    )


def _development_branch(
    problem: ExactProblem,
    state: WorldState,
    available: bool,
) -> tuple[float, frozenset[DevelopmentDecision]]:
    """Exact conditional branch value under the existing HLS recursion."""
    opportunity = Opportunity(available)
    values: dict[DevelopmentDecision, float] = {}
    for decision in _admissible_development_actions(problem, state, opportunity):
        next_state = _physical_next_state(problem, state, opportunity, decision)
        continuation = (
            _terminal_value(problem, next_state)
            if next_state.time == problem.horizon
            else solve_exact_hls(problem, initial_state=next_state).value
        )
        values[decision] = (
            -problem.environment.resources.development_cost(decision)
            + problem.environment.resources.beta * continuation
        )
    best = max(values.values())
    return best, frozenset(
        decision
        for decision, value in values.items()
        if abs(value - best) <= EXACT_TOL
    )


def _node_evaluation(problem: ExactProblem, state: WorldState) -> NodeEvaluation:
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
    w0, _ = _development_branch(problem, state, False)
    w1, _ = _development_branch(problem, state, True)
    return NodeEvaluation(
        state=state,
        task=task,
        greedy_actions=greedy,
        hls_actions=hls.optimal_actions,
        opportunity_probabilities=probabilities,
        w0=w0,
        w1=w1,
        d_star=w1 - w0,
    )


def sep_admissible_hls_exists(problem: ExactProblem) -> bool:
    """Whether one exact HLS-optimal policy is greedy at every reached node."""
    cache: dict[WorldState, bool] = {}

    def compatible(state: WorldState) -> bool:
        if state.time == problem.horizon:
            return True
        if state in cache:
            return cache[state]

        node = _node_evaluation(problem, state)
        for action in node.hls_actions & node.greedy_actions:
            probability = node.opportunity_probabilities[action]
            action_is_compatible = True
            for available, weight in ((False, 1.0 - probability), (True, probability)):
                if weight <= EXACT_TOL:
                    continue
                branch_value, optimal_development = _development_branch(
                    problem, state, available
                )
                del branch_value
                opportunity = Opportunity(available)
                if not any(
                    compatible(
                        _physical_next_state(problem, state, opportunity, decision)
                    )
                    for decision in optimal_development
                ):
                    action_is_compatible = False
                    break
            if action_is_compatible:
                cache[state] = True
                return True

        cache[state] = False
        return False

    return compatible(problem.environment.initial_state())


def evaluate_lambda(lambda_value: float) -> CouplingEvaluation:
    """Evaluate one frozen point exactly; no sampling or parameter adaptation."""
    world = build_world(lambda_value)
    initial = world.environment.initial_state()
    hls = solve_exact_hls(world.problem, initial_state=initial)
    sep = solve_exact_strong_sep(world.problem, initial_state=initial)
    omega = solve_exact_sep_omega(world.problem, initial_state=initial)
    audit = audit_optimal_hls_reachability(world.problem, initial_state=initial)
    nodes = tuple(
        _node_evaluation(world.problem, item.state)
        for item in sorted(
            audit.states,
            key=lambda item: (item.state.time, repr(item.state.competence), item.state.resources),
        )
    )
    phi = hls.value - sep.value_max
    compatible = sep_admissible_hls_exists(world.problem)

    if phi > EXACT_TOL and not compatible:
        regime = "HLS_INTEGRATED"
    elif abs(phi) <= EXACT_TOL and compatible:
        regime = "SEP_REDUCIBLE"
    else:
        regime = "REQUIRES_INVESTIGATION"

    return CouplingEvaluation(
        lambda_value=lambda_value,
        j_hls=hls.value,
        j_sep_min=sep.value_min,
        j_sep_max=sep.value_max,
        j_sep_omega=omega.value,
        phi=phi,
        hls_initial_actions=hls.optimal_actions,
        sep_initial_actions=sep.immediate_optimal_actions,
        sep_admissible_hls_exists=compatible,
        regime=regime,
        nodes=nodes,
    )


def run_grid() -> tuple[CouplingEvaluation, ...]:
    """Evaluate the single frozen grid in declaration order."""
    return tuple(evaluate_lambda(lambda_value) for lambda_value in LAMBDA_GRID)
