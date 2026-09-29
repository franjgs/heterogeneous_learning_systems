"""Exact C1 reference worlds on the G0 synthetic environment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .components import (
    A1MixtureOpportunityKernel,
    A1ResourceModel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
    FiniteTaskSequence,
    ScheduledSaturatingDevelopmentKernel,
)
from .environment import SyntheticEnvironment
from .interfaces import DevelopmentDecision, NULL_DEVELOPMENT, Opportunity
from .randomness import SeededRandomSource
from .state import WorldState


C1_TOL = 1e-12
LEARNERS = ("M1", "M2")
TASKS = (1, 2)


@dataclass(frozen=True)
class Intervention:
    operational_action: str
    development_action: DevelopmentDecision


@dataclass(frozen=True)
class C1ReferenceWorld:
    name: str
    environment: SyntheticEnvironment
    terminal_task: int
    interventions: tuple[Intervention, Intervention]


@dataclass(frozen=True)
class DynamicSolution:
    value: float
    optimal_actions: frozenset[str]
    action_values: Mapping[str, float]


@dataclass(frozen=True)
class StrongSEPSolution:
    value_min: float
    value_max: float
    immediate_optimal_actions: frozenset[str]
    action_value_bounds: Mapping[str, tuple[float, float]]


@dataclass(frozen=True)
class C1Links:
    state_effect: bool
    decision_effect: bool
    second_order_effect: bool

    @property
    def genuine(self) -> bool:
        return self.state_effect and self.decision_effect and self.second_order_effect


@dataclass(frozen=True)
class C1Evaluation:
    hls: DynamicSolution
    sep: StrongSEPSolution
    sep_omega: DynamicSolution
    links: C1Links

    @property
    def delta_j_cons(self) -> float:
        return self.hls.value - self.sep.value_max


def _optimal_set(values: Mapping[str, float]) -> frozenset[str]:
    best = max(values.values())
    return frozenset(action for action, value in values.items() if abs(value - best) <= C1_TOL)


def _terminal_value(environment: SyntheticEnvironment, state: WorldState, task: int) -> float:
    return max(environment.reward.operational_reward(state, task, learner) for learner in LEARNERS)


def _branch_value(
    environment: SyntheticEnvironment,
    state: WorldState,
    action: str,
    continuation: Callable[[WorldState], float],
) -> float:
    task = environment.tasks.task_at(state.time, state, ())
    reward = environment.reward.operational_reward(state, task, action)
    probability = environment.opportunities.probability(state, task, action, ())
    expected = 0.0
    for available, weight in ((False, 1.0 - probability), (True, probability)):
        if weight <= 0.0:
            continue
        opportunity = Opportunity(available)
        development_values = []
        for decision in environment.development.admissible_actions(state, opportunity):
            next_state = environment.development.transition(state, opportunity, decision)
            development_values.append(
                -environment.resources.development_cost(decision)
                + environment.resources.beta * continuation(next_state)
            )
        expected += weight * max(development_values)
    return reward + expected


def _branch_bounds(
    environment: SyntheticEnvironment,
    state: WorldState,
    action: str,
    continuation: Callable[[WorldState], tuple[float, float]],
) -> tuple[float, float]:
    """Propagate lower/upper SEP values without resolving routing ties."""
    task = environment.tasks.task_at(state.time, state, ())
    reward = environment.reward.operational_reward(state, task, action)
    probability = environment.opportunities.probability(state, task, action, ())
    expected_min = 0.0
    expected_max = 0.0
    for available, weight in ((False, 1.0 - probability), (True, probability)):
        if weight <= 0.0:
            continue
        opportunity = Opportunity(available)
        development_bounds = []
        for decision in environment.development.admissible_actions(state, opportunity):
            next_state = environment.development.transition(state, opportunity, decision)
            downstream_min, downstream_max = continuation(next_state)
            cost = environment.resources.development_cost(decision)
            development_bounds.append(
                (
                    -cost + environment.resources.beta * downstream_min,
                    -cost + environment.resources.beta * downstream_max,
                )
            )
        expected_min += weight * max(bound[0] for bound in development_bounds)
        expected_max += weight * max(bound[1] for bound in development_bounds)
    return reward + expected_min, reward + expected_max


def solve_hls(world: C1ReferenceWorld) -> DynamicSolution:
    environment = world.environment

    def value(state: WorldState) -> float:
        if state.time == 2:
            return _terminal_value(environment, state, world.terminal_task)
        return max(_branch_value(environment, state, action, value) for action in LEARNERS)

    state = environment.initial_state()
    action_values = {action: _branch_value(environment, state, action, value) for action in LEARNERS}
    return DynamicSolution(max(action_values.values()), _optimal_set(action_values), action_values)


def solve_strong_sep(world: C1ReferenceWorld) -> StrongSEPSolution:
    environment = world.environment

    def sep_bounds(state: WorldState) -> tuple[float, float]:
        if state.time == 2:
            terminal = _terminal_value(environment, state, world.terminal_task)
            return terminal, terminal
        task = environment.tasks.task_at(state.time, state, ())
        rewards = {a: environment.reward.operational_reward(state, task, a) for a in LEARNERS}
        immediate = _optimal_set(rewards)
        action_bounds = {
            action: _branch_bounds(environment, state, action, sep_bounds)
            for action in immediate
        }
        return (
            min(bounds[0] for bounds in action_bounds.values()),
            max(bounds[1] for bounds in action_bounds.values()),
        )

    state = environment.initial_state()
    task = environment.tasks.task_at(0, state, ())
    rewards = {a: environment.reward.operational_reward(state, task, a) for a in LEARNERS}
    immediate = _optimal_set(rewards)
    action_bounds = {
        action: _branch_bounds(environment, state, action, sep_bounds)
        for action in immediate
    }
    return StrongSEPSolution(
        min(bounds[0] for bounds in action_bounds.values()),
        max(bounds[1] for bounds in action_bounds.values()),
        immediate,
        action_bounds,
    )


def solve_sep_omega(world: C1ReferenceWorld) -> DynamicSolution:
    """Independently solve routing supplied with exact recursive continuation."""
    environment = world.environment

    def coordinated_value(state: WorldState) -> float:
        if state.time == 2:
            return _terminal_value(environment, state, world.terminal_task)
        values = {a: _branch_value(environment, state, a, coordinated_value) for a in LEARNERS}
        return max(values.values())

    state = environment.initial_state()
    action_values = {
        action: _branch_value(environment, state, action, coordinated_value)
        for action in LEARNERS
    }
    return DynamicSolution(max(action_values.values()), _optimal_set(action_values), action_values)


def _apply_intervention(world: C1ReferenceWorld, intervention: Intervention) -> WorldState:
    environment = world.environment
    state = environment.initial_state()
    task = environment.tasks.task_at(0, state, ())
    probability = environment.opportunities.probability(
        state, task, intervention.operational_action, ()
    )
    if probability not in (0.0, 1.0):
        raise ValueError("C1 link audit requires deterministic reference opportunities")
    opportunity = Opportunity(bool(probability))
    return environment.development.transition(
        state, opportunity, intervention.development_action
    )


def _cycle_one_hls_actions(world: C1ReferenceWorld, state: WorldState) -> frozenset[str]:
    environment = world.environment

    def terminal(next_state: WorldState) -> float:
        return _terminal_value(environment, next_state, world.terminal_task)

    values = {action: _branch_value(environment, state, action, terminal) for action in LEARNERS}
    return _optimal_set(values)


def evaluate_links(world: C1ReferenceWorld) -> C1Links:
    left, right = world.interventions
    left_state, right_state = _apply_intervention(world, left), _apply_intervention(world, right)
    state_effect = left_state.competence != right_state.competence
    left_actions = _cycle_one_hls_actions(world, left_state)
    right_actions = _cycle_one_hls_actions(world, right_state)
    decision_effect = left_actions != right_actions
    second_order = False
    if decision_effect:
        environment = world.environment
        task = environment.tasks.task_at(1, left_state, ())
        for state in (left_state, right_state):
            probabilities = {
                action: environment.opportunities.probability(state, task, action, ())
                for action in LEARNERS
            }
            if abs(probabilities["M1"] - probabilities["M2"]) > C1_TOL:
                second_order = True
    return C1Links(state_effect, decision_effect, second_order)


def evaluate_world(world: C1ReferenceWorld) -> C1Evaluation:
    return C1Evaluation(
        hls=solve_hls(world),
        sep=solve_strong_sep(world),
        sep_omega=solve_sep_omega(world),
        links=evaluate_links(world),
    )


def relabel_world(world: C1ReferenceWorld) -> C1ReferenceWorld:
    """Physically exchange learner labels without changing the world."""
    old = world.environment
    competence = old.competence.initial
    baseline = dict(old.opportunities.baseline)
    executor = dict(old.opportunities.executor_values)
    swap = {"M1": "M2", "M2": "M1"}
    learners = {"M1": 0, "M2": 1}
    tasks = {1: 0, 2: 1}
    environment = SyntheticEnvironment(
        tasks=old.tasks,
        competence=BoundedMatrixCompetence((competence[1], competence[0])),
        opportunities=A1MixtureOpportunityKernel(
            baseline,
            {(swap[actor], task): value for (actor, task), value in executor.items()},
            old.opportunities.rho,
        ),
        development=ScheduledSaturatingDevelopmentKernel(
            learners, tasks, dict(old.development.target_by_time), old.development.eta
        ),
        reward=CompetenceRewardModel(learners, tasks),
        resources=old.resources,
        information=old.information,
        randomness=SeededRandomSource(0),
    )
    interventions = tuple(
        Intervention(
            swap[item.operational_action],
            item.development_action
            if item.development_action.is_null
            else DevelopmentDecision(
                swap[item.development_action.recipient],
                item.development_action.competence,
            ),
        )
        for item in world.interventions
    )
    return C1ReferenceWorld(
        world.name + "_relabeled", environment, world.terminal_task, interventions  # type: ignore[arg-type]
    )


def _make_world(
    name: str,
    competence: tuple[tuple[float, float], tuple[float, float]],
    *,
    eta: float,
    task1_executor: tuple[float, float],
    task2_executor: tuple[float, float],
    interventions: tuple[Intervention, Intervention],
) -> C1ReferenceWorld:
    learners = {"M1": 0, "M2": 1}
    tasks = {1: 0, 2: 1}
    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence((1, 2)),
        competence=BoundedMatrixCompetence(competence),
        opportunities=A1MixtureOpportunityKernel(
            {1: 0.0, 2: 0.0},
            {
                ("M1", 1): task1_executor[0],
                ("M2", 1): task1_executor[1],
                ("M1", 2): task2_executor[0],
                ("M2", 2): task2_executor[1],
            },
            rho=1.0,
        ),
        development=ScheduledSaturatingDevelopmentKernel(
            learners, tasks, {0: 2, 1: 1}, eta
        ),
        reward=CompetenceRewardModel(learners, tasks),
        resources=A1ResourceModel(kappa=0.0, beta=1.0),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )
    return C1ReferenceWorld(name, environment, terminal_task=1, interventions=interventions)


def reference_worlds() -> dict[str, C1ReferenceWorld]:
    null = NULL_DEVELOPMENT
    develop_m1_task2 = DevelopmentDecision("M1", 2)
    develop_m2_task2 = DevelopmentDecision("M2", 2)
    base = ((0.8, 0.8), (0.6, 0.6))
    return {
        "R1_no_evolution": _make_world(
            "R1_no_evolution", base, eta=0.0,
            task1_executor=(0.0, 1.0), task2_executor=(0.0, 1.0),
            interventions=(Intervention("M1", null), Intervention("M2", develop_m2_task2)),
        ),
        "R2_evolution_no_decision_feedback": _make_world(
            "R2_evolution_no_decision_feedback", base, eta=0.75,
            task1_executor=(1.0, 1.0), task2_executor=(1.0, 1.0),
            interventions=(Intervention("M1", null), Intervention("M1", develop_m1_task2)),
        ),
        "R3_decision_feedback_no_second_order": _make_world(
            "R3_decision_feedback_no_second_order", base, eta=0.75,
            task1_executor=(0.0, 1.0), task2_executor=(1.0, 1.0),
            interventions=(Intervention("M1", null), Intervention("M2", develop_m2_task2)),
        ),
        "R4_recursive_value_neutral_boundary": _make_world(
            "R4_recursive_value_neutral_boundary", ((0.8, 0.8), (0.56, 0.56)), eta=0.75,
            task1_executor=(0.0, 1.0), task2_executor=(0.0, 1.0),
            interventions=(Intervention("M1", null), Intervention("M2", develop_m2_task2)),
        ),
        "R5_recursive_strict_value": _make_world(
            "R5_recursive_strict_value", base, eta=0.75,
            task1_executor=(0.0, 1.0), task2_executor=(0.0, 1.0),
            interventions=(Intervention("M1", null), Intervention("M2", develop_m2_task2)),
        ),
    }
