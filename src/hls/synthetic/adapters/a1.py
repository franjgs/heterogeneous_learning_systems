"""Exact A1 configuration and evaluator for the G0 general skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping

from hls.a1a import A1aWorld

from ..components import (
    A1MixtureOpportunityKernel,
    A1ResourceModel,
    A1SaturatingDevelopmentKernel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
    FiniteTaskSequence,
)
from ..environment import SyntheticEnvironment
from ..interfaces import (
    DevelopmentDecision,
    InformationContract,
    Opportunity,
    PolicyView,
)
from ..randomness import SeededRandomSource


A1_TOL = 1e-12
A1_LEARNERS = ("M1", "M2")


@dataclass(frozen=True)
class ExactPolicySolution:
    value: float
    optimal_actions: frozenset[Hashable]


@dataclass(frozen=True)
class ExactStrongSEPSolution:
    value_min: float
    value_max: float
    immediate_optimal_actions: frozenset[Hashable]


@dataclass(frozen=True)
class A1ExactEvaluation:
    no_opportunity_value: float
    opportunity_value: float
    optimal_development_actions: frozenset[DevelopmentDecision]
    opportunity_probabilities: Mapping[Hashable, float]
    continuation_values: Mapping[Hashable, float]
    operational_rewards: Mapping[Hashable, float]
    total_values: Mapping[Hashable, float]
    hls: ExactPolicySolution
    strong_sep: ExactStrongSEPSolution
    sep_omega: ExactPolicySolution

    @property
    def delta_j_cons(self) -> float:
        return self.hls.value - self.strong_sep.value_max


def _optimal_set(values: Mapping[Hashable, float], tol: float) -> frozenset[Hashable]:
    best = max(values.values())
    return frozenset(key for key, value in values.items() if abs(value - best) <= tol)


def a1_information_contracts() -> tuple[
    InformationContract, InformationContract, InformationContract
]:
    """Return joint, strong-SEP, and SEP-Omega information contracts."""
    joint = InformationContract(
        name="joint",
        reveal_continuation_values=True,
        coordinate_operational_and_development_value=True,
    )
    strong_sep = InformationContract(name="separate_immediate")
    sep_omega = InformationContract(
        name="separate_sufficient_continuation",
        reveal_continuation_values=True,
        coordinate_operational_and_development_value=True,
    )
    return joint, strong_sep, sep_omega


def build_a1_environment(world: A1aWorld) -> SyntheticEnvironment:
    """Express one frozen A1a physical world through the seven G0 blocks."""
    learners = {name: index for index, name in enumerate(A1_LEARNERS)}
    tasks = {1: 0, 2: 1}
    baseline = {
        task: value
        for task, value in enumerate(world.opportunity_baseline, start=1)
        if value is not None
    }
    executor = {
        (A1_LEARNERS[learner_index], task): value
        for learner_index, row in enumerate(world.executor_opportunity)
        for task, value in enumerate(row, start=1)
        if value is not None
    }
    return SyntheticEnvironment(
        tasks=FiniteTaskSequence((world.q0, world.q1)),
        competence=BoundedMatrixCompetence(world.competence),
        opportunities=A1MixtureOpportunityKernel(baseline, executor, world.rho),
        development=A1SaturatingDevelopmentKernel(
            learner_indices=learners,
            competence_indices=tasks,
            target_competence=world.q1,
            eta=world.eta,
        ),
        reward=CompetenceRewardModel(learners, tasks),
        resources=A1ResourceModel(world.kappa, world.beta),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )


def _joint_choice(view: PolicyView, tol: float) -> ExactPolicySolution:
    rewards = view.rewards()
    continuations = view.continuations()
    totals = {action: rewards[action] + continuations[action] for action in rewards}
    return ExactPolicySolution(max(totals.values()), _optimal_set(totals, tol))


def _strong_sep_choice(
    view: PolicyView,
    continuation_values: Mapping[Hashable, float],
    tol: float,
) -> ExactStrongSEPSolution:
    rewards = view.rewards()
    immediate_actions = _optimal_set(rewards, tol)
    totals = {
        action: rewards[action] + continuation_values[action]
        for action in immediate_actions
    }
    return ExactStrongSEPSolution(
        value_min=min(totals.values()),
        value_max=max(totals.values()),
        immediate_optimal_actions=immediate_actions,
    )


def _sep_omega_choice(view: PolicyView, tol: float) -> ExactPolicySolution:
    rewards = view.rewards()
    continuations = view.continuations()
    totals = {action: rewards[action] + continuations[action] for action in rewards}
    return ExactPolicySolution(max(totals.values()), _optimal_set(totals, tol))


def evaluate_a1_exact(
    environment: SyntheticEnvironment,
    *,
    tol: float = A1_TOL,
) -> A1ExactEvaluation:
    """Integrate A1's Bernoulli opportunity exactly, without sampling."""
    state = environment.initial_state()
    q0 = environment.tasks.task_at(0, state, ())
    q1 = environment.tasks.task_at(1, state, ())
    reward = environment.reward
    resources = environment.resources
    development = environment.development
    opportunity_yes = Opportunity(True)

    terminal_now = max(
        reward.operational_reward(state, q1, learner) for learner in A1_LEARNERS
    )
    n_value = resources.beta * terminal_now
    development_values: dict[DevelopmentDecision, float] = {}
    for action in development.admissible_actions(state, opportunity_yes):
        next_state = development.transition(state, opportunity_yes, action)
        terminal = max(
            reward.operational_reward(next_state, q1, learner)
            for learner in A1_LEARNERS
        )
        development_values[action] = (
            -resources.development_cost(action) + resources.beta * terminal
        )
    d_value = max(development_values.values())
    optimal_development = frozenset(
        action
        for action, value in development_values.items()
        if abs(value - d_value) <= tol
    )

    probabilities = {
        learner: environment.opportunities.probability(state, q0, learner, ())
        for learner in A1_LEARNERS
    }
    continuations = {
        learner: n_value + probabilities[learner] * (d_value - n_value)
        for learner in A1_LEARNERS
    }
    rewards = {
        learner: reward.operational_reward(state, q0, learner)
        for learner in A1_LEARNERS
    }
    totals = {
        learner: rewards[learner] + continuations[learner]
        for learner in A1_LEARNERS
    }
    joint_contract, sep_contract, omega_contract = a1_information_contracts()
    joint_view = environment.information.view(
        joint_contract, state, q0, rewards, continuations
    )
    sep_view = environment.information.view(
        sep_contract, state, q0, rewards, continuations
    )
    omega_view = environment.information.view(
        omega_contract, state, q0, rewards, continuations
    )
    return A1ExactEvaluation(
        no_opportunity_value=n_value,
        opportunity_value=d_value,
        optimal_development_actions=optimal_development,
        opportunity_probabilities=probabilities,
        continuation_values=continuations,
        operational_rewards=rewards,
        total_values=totals,
        hls=_joint_choice(joint_view, tol),
        strong_sep=_strong_sep_choice(sep_view, continuations, tol),
        sep_omega=_sep_omega_choice(omega_view, tol),
    )


def analytical_regime(margin: float, *, tol: float = A1_TOL) -> str:
    if margin < -tol:
        return "LESS"
    if margin > tol:
        return "GREATER"
    return "BOUNDARY"


def observed_regime(delta_j_cons: float, *, tol: float = A1_TOL) -> str:
    if delta_j_cons < -tol:
        return "NEGATIVE_UNEXPECTED"
    if delta_j_cons > tol:
        return "STRICT_ADVANTAGE"
    return "NO_ADVANTAGE"
