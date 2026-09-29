"""Preregistered RQ0-A/B campaign worlds.

This module is an executable specification of the frozen protocol in
docs/experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md, Section 14.

It defines exactly the nine preregistered initial configurations.  It does
not run the campaign, compute HLS/SEP results, perform parameter search, or
adapt any parameter to observed performance.
"""

from __future__ import annotations

from dataclasses import dataclass

from .c3 import BudgetedDevelopmentResources, with_development_budget
from .c4 import CoupledDevelopmentKernel
from .components import (
    A1MixtureOpportunityKernel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
    FiniteTaskSequence,
)
from .environment import SyntheticEnvironment
from .exact import ExactProblem
from .randomness import SeededRandomSource
from .state import WorldState


LEARNERS = ("M1", "M2", "M3")
TASKS = (1, 2, 3)

LEARNER_INDICES = {learner: i for i, learner in enumerate(LEARNERS)}
TASK_INDICES = {task: i for i, task in enumerate(TASKS)}

HORIZON = 2
OPERATIONAL_TASKS = (1, 2)
TERMINAL_TASK = 3

ETA = 0.75
BASELINE_OPPORTUNITY = {1: 0.5, 2: 0.5}
TARGET_BY_TIME = {0: 2, 1: 3}

BUDGET_PER_DEVELOPMENT = 1.0
BETA = 1.0


@dataclass(frozen=True)
class RQ0Configuration:
    """One of the nine frozen RQ0-A/B configurations."""

    name: str
    s: float
    budget: int
    gamma: float
    rho: float


@dataclass(frozen=True)
class RQ0World:
    """Executable world and exact problem for one frozen configuration."""

    configuration: RQ0Configuration
    environment: SyntheticEnvironment
    initial_state: WorldState
    problem: ExactProblem


def competence_matrix(s: float) -> tuple[tuple[float, ...], ...]:
    """Return the preregistered C2 portfolio geometry C(s)."""
    if not 0.0 <= s <= 1.0:
        raise ValueError("specialization s must lie in [0,1]")

    diagonal = 0.60 + 0.30 * s
    off_diagonal = 0.60 - 0.15 * s

    return tuple(
        tuple(
            diagonal if i == j else off_diagonal
            for j in range(3)
        )
        for i in range(3)
    )


def _interaction_map(gamma: float):
    """Frozen C4 topology from Section 14.13.

    Development of competence k for learner Mi applies gamma to every other
    competence coordinate of the same learner.  No inter-learner interaction
    is present.

    gamma=0 exactly recovers independent development.
    """
    if gamma not in (-0.25, 0.0, 0.25):
        raise ValueError("RQ0-A/B gamma must be one of {-0.25,0,+0.25}")

    if gamma == 0.0:
        return {}

    interaction = {}
    for learner in LEARNERS:
        for source_competence in TASKS:
            for destination_competence in TASKS:
                if destination_competence != source_competence:
                    interaction[
                        (
                            learner,
                            source_competence,
                            learner,
                            destination_competence,
                        )
                    ] = gamma

    return interaction


def _executor_values(
    initial_competence: tuple[tuple[float, ...], ...],
) -> dict[tuple[str, int], float]:
    """Freeze e_iq from initial competence for operational tasks q=1,2."""
    return {
        (learner, task): initial_competence[
            LEARNER_INDICES[learner]
        ][TASK_INDICES[task]]
        for learner in LEARNERS
        for task in OPERATIONAL_TASKS
    }


def build_world(configuration: RQ0Configuration) -> RQ0World:
    """Instantiate one preregistered RQ0-A/B configuration."""
    if configuration.budget not in (0, 1, 2):
        raise ValueError("RQ0-A/B budget must be one of {0,1,2}")
    if configuration.gamma not in (-0.25, 0.0, 0.25):
        raise ValueError("RQ0-A/B gamma must be one of {-0.25,0,+0.25}")
    if configuration.rho not in (0.0, 0.5, 1.0):
        raise ValueError("RQ0-A/B rho must be one of {0,0.5,1}")

    initial_competence = competence_matrix(configuration.s)

    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence(OPERATIONAL_TASKS),
        competence=BoundedMatrixCompetence(initial_competence),
        opportunities=A1MixtureOpportunityKernel(
            BASELINE_OPPORTUNITY,
            _executor_values(initial_competence),
            rho=configuration.rho,
        ),
        development=CoupledDevelopmentKernel(
            LEARNER_INDICES,
            TASK_INDICES,
            TARGET_BY_TIME,
            eta=ETA,
            gamma=_interaction_map(configuration.gamma),
        ),
        reward=CompetenceRewardModel(
            LEARNER_INDICES,
            TASK_INDICES,
        ),
        resources=BudgetedDevelopmentResources(
            budget_per_development=BUDGET_PER_DEVELOPMENT,
            beta=BETA,
        ),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )

    initial_state = with_development_budget(
        environment.initial_state(),
        float(configuration.budget),
    )

    problem = ExactProblem(
        environment=environment,
        operational_actions=LEARNERS,
        horizon=HORIZON,
        terminal_task=TERMINAL_TASK,
    )

    return RQ0World(
        configuration=configuration,
        environment=environment,
        initial_state=initial_state,
        problem=problem,
    )


CONFIGURATIONS = (
    RQ0Configuration("B*",             0.5, 1,  0.00, 0.5),
    RQ0Configuration("REDUNDANT",      0.0, 1,  0.00, 0.5),
    RQ0Configuration("FREE_RESOURCE",  0.5, 2,  0.00, 0.5),
    RQ0Configuration("NO_COUPLING",    0.5, 1,  0.00, 0.0),
    RQ0Configuration("INTERFERENCE",   0.5, 1, -0.25, 0.5),
    RQ0Configuration("TRANSFER",       0.5, 1, +0.25, 0.5),
    RQ0Configuration("SPECIALIZED",    1.0, 1,  0.00, 0.5),
    RQ0Configuration("MAX_COUPLING",   0.5, 1,  0.00, 1.0),
    RQ0Configuration("NO_DEVELOPMENT", 0.5, 0,  0.00, 0.5),
)


def configurations() -> tuple[RQ0Configuration, ...]:
    """Return exactly the nine preregistered configurations."""
    return CONFIGURATIONS


def worlds() -> tuple[RQ0World, ...]:
    """Instantiate exactly the nine preregistered worlds."""
    return tuple(build_world(configuration) for configuration in CONFIGURATIONS)


def world_by_name(name: str) -> RQ0World:
    """Instantiate one preregistered world by its canonical name."""
    matches = [configuration for configuration in CONFIGURATIONS
               if configuration.name == name]
    if len(matches) != 1:
        raise KeyError(name)
    return build_world(matches[0])
