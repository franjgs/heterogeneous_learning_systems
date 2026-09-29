"""Composition root for policy-neutral synthetic HLS worlds."""

from __future__ import annotations

from dataclasses import dataclass

from .interfaces import (
    CompetenceModel,
    DevelopmentDecision,
    DevelopmentKernel,
    InformationModel,
    Opportunity,
    OpportunityKernel,
    OperationalAction,
    RandomSource,
    ResourceModel,
    RewardModel,
    TaskProcess,
)
from .state import WorldState
from .trajectory import Trajectory, TransitionRecord


@dataclass(frozen=True)
class SyntheticEnvironment:
    """A world assembled from seven replaceable Theta components.

    Policy implementations are deliberately absent. The environment exposes
    physical semantics and information views but never branches on policy name.
    """

    tasks: TaskProcess
    competence: CompetenceModel
    opportunities: OpportunityKernel
    development: DevelopmentKernel
    reward: RewardModel
    resources: ResourceModel
    information: InformationModel
    randomness: RandomSource

    def __post_init__(self) -> None:
        self.competence.validate(self.competence.initial_state())

    def initial_state(self) -> WorldState:
        return self.competence.initial_state()

    def task_at(
        self,
        state: WorldState,
        trajectory: Trajectory = Trajectory(),
    ):
        """Resolve deterministic or stochastic task demand using G0 randomness."""
        sampler = getattr(self.tasks, "sample_task", None)
        if sampler is not None:
            return sampler(
                state.time,
                state,
                trajectory.transitions,
                self.randomness,
            )
        return self.tasks.task_at(
            state.time,
            state,
            trajectory.transitions,
        )

    def sample_transition(
        self,
        state: WorldState,
        operational_action: OperationalAction,
        development_action: DevelopmentDecision,
        trajectory: Trajectory = Trajectory(),
    ) -> TransitionRecord:
        """Sample one transition through the declared kernels.

        Exact A1 evaluation does not call this method; it integrates the
        Bernoulli opportunity analytically.
        """
        self.competence.validate(state)
        task = self.task_at(state, trajectory)
        probability = self.opportunities.probability(
            state, task, operational_action, trajectory.transitions
        )
        opportunity = Opportunity(self.randomness.random() < probability)
        admissible = self.development.admissible_actions(state, opportunity)
        if development_action not in admissible:
            raise ValueError("development action is not admissible")
        if not self.resources.development_is_admissible(
            state, development_action, opportunity
        ):
            raise ValueError("development action violates resource semantics")
        developed_state = self.development.transition(
            state, opportunity, development_action
        )
        next_resources = self.resources.consume(
            state, development_action
        )
        next_state = WorldState(
            competence=developed_state.competence,
            time=developed_state.time,
            resources=next_resources,
        )
        self.competence.validate(next_state)
        return TransitionRecord(
            state=state,
            task=task,
            operational_action=operational_action,
            opportunity=opportunity,
            development_action=development_action,
            operational_reward=self.reward.operational_reward(
                state, task, operational_action
            ),
            development_cost=self.resources.development_cost(development_action),
            next_state=next_state,
        )
