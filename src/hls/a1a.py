"""Exact T=2 solver for the frozen A1a analytical reference worlds.

The authoritative specification is Section 20 of
``docs/experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md``.  This module
contains no sampling, fitted quantities, or scientific parameter sweeps.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
import math
from typing import Mapping


DEFAULT_ABS_TOL = 1e-12


class Learner(str, Enum):
    """The two A1a learners."""

    M1 = "M1"
    M2 = "M2"


LEARNERS = (Learner.M1, Learner.M2)
CompetenceState = tuple[tuple[float, float], tuple[float, float]]
OptionalOpportunityMatrix = tuple[
    tuple[float | None, float | None],
    tuple[float | None, float | None],
]


@dataclass(frozen=True)
class DevelopmentAction:
    """A null action or development of one learner on one task."""

    recipient: Learner | None
    task: int | None

    @property
    def is_null(self) -> bool:
        return self.recipient is None and self.task is None

    def __post_init__(self) -> None:
        if (self.recipient is None) != (self.task is None):
            raise ValueError("recipient and task must both be set or both be null")
        if self.task is not None and self.task not in (1, 2):
            raise ValueError("development task must be 1 or 2")


NULL_DEVELOPMENT = DevelopmentAction(None, None)


@dataclass(frozen=True)
class A1aWorld:
    """Immutable primitive description of one frozen A1a physical world."""

    competence: CompetenceState
    q0: int
    q1: int
    opportunity_baseline: tuple[float | None, float | None]
    executor_opportunity: OptionalOpportunityMatrix
    rho: float
    eta: float
    kappa: float
    beta: float

    def __post_init__(self) -> None:
        _validate_state(self.competence)
        if self.q0 not in (1, 2) or self.q1 not in (1, 2):
            raise ValueError("q0 and q1 must be task 1 or 2")
        if len(self.opportunity_baseline) != 2:
            raise ValueError("opportunity_baseline must contain two task entries")
        if len(self.executor_opportunity) != 2 or any(
            len(row) != 2 for row in self.executor_opportunity
        ):
            raise ValueError("executor_opportunity must be a 2x2 matrix")
        for value in self.opportunity_baseline:
            if value is not None:
                _validate_unit_interval("opportunity baseline", value)
        for row in self.executor_opportunity:
            for value in row:
                if value is not None:
                    _validate_unit_interval("executor opportunity", value)
        _validate_unit_interval("rho", self.rho)
        _validate_unit_interval("eta", self.eta)
        _validate_unit_interval("beta", self.beta)
        if not math.isfinite(float(self.kappa)) or self.kappa < 0:
            raise ValueError("kappa must be finite and non-negative")


@dataclass(frozen=True)
class DevelopmentEvaluation:
    """Exact maximization over development actions after an opportunity."""

    value: float
    optimal_actions: frozenset[DevelopmentAction]
    action_values: Mapping[DevelopmentAction, float]


@dataclass(frozen=True)
class PolicySolution:
    """Solution of HLS or SEP-Omega with complete per-action diagnostics."""

    optimal_value: float
    optimal_operational_actions: frozenset[Learner]
    selected_operational_action: Learner
    operational_rewards: Mapping[Learner, float]
    opportunity_probabilities: Mapping[Learner, float]
    continuation_values: Mapping[Learner, float]
    total_values: Mapping[Learner, float]
    optimal_development_actions: frozenset[DevelopmentAction]
    no_opportunity_value: float
    opportunity_value: float


@dataclass(frozen=True)
class StrongSEPSolution:
    """Strong SEP solution: immediate routing, then optimal development."""

    value: float | None
    value_min: float
    value_max: float
    immediate_optimal_actions: frozenset[Learner]
    expected_total_values: Mapping[Learner, float]
    operational_rewards: Mapping[Learner, float]
    opportunity_probabilities: Mapping[Learner, float]
    continuation_values: Mapping[Learner, float]
    optimal_development_actions: frozenset[DevelopmentAction]
    no_opportunity_value: float
    opportunity_value: float


@dataclass(frozen=True)
class ImmediateActionComparison:
    """Derived comparison of one immediate optimum with one alternative."""

    immediate_optimum: Learner
    alternative: Learner
    delta_R: float
    delta_G: float


@dataclass(frozen=True)
class GeneralDiagnostics:
    """Diagnostics whose immediate optima are derived from world rewards."""

    immediate_optimal_actions: frozenset[Learner]
    comparisons: tuple[ImmediateActionComparison, ...]


def _validate_unit_interval(name: str, value: float) -> None:
    if not math.isfinite(float(value)) or not 0 <= value <= 1:
        raise ValueError(f"{name} must lie in [0, 1]")


def _validate_state(state: CompetenceState) -> None:
    if len(state) != 2 or any(len(row) != 2 for row in state):
        raise ValueError("competence state must be 2x2")
    for row in state:
        for value in row:
            _validate_unit_interval("competence", value)


def _learner_index(learner: Learner) -> int:
    return LEARNERS.index(learner)


def _task_index(task: int) -> int:
    if task not in (1, 2):
        raise ValueError("task must be 1 or 2")
    return task - 1


def operational_reward(
    world: A1aWorld,
    learner: Learner,
    task: int,
    state: CompetenceState | None = None,
) -> float:
    """Return A1a operational reward c_ik, with no operational cost."""
    current = world.competence if state is None else state
    _validate_state(current)
    return current[_learner_index(learner)][_task_index(task)]


def opportunity_probability(world: A1aWorld, learner: Learner, task: int) -> float:
    """Return the frozen mixture (1-rho)*ebar_k + rho*e_ik."""
    learner_index = _learner_index(learner)
    task_index = _task_index(task)
    baseline = world.opportunity_baseline[task_index]
    executor_value = world.executor_opportunity[learner_index][task_index]
    if baseline is None or executor_value is None:
        raise ValueError(f"opportunity primitives for task {task} are unidentified")
    probability = (1.0 - world.rho) * baseline + world.rho * executor_value
    _validate_unit_interval("derived opportunity probability", probability)
    return probability


def development_cost(world: A1aWorld, action: DevelopmentAction) -> float:
    """Return zero for null development and kappa otherwise."""
    return 0.0 if action.is_null else world.kappa


def development_transition(
    world: A1aWorld,
    state: CompetenceState,
    action: DevelopmentAction,
) -> CompetenceState:
    """Apply the bounded A1a development transition to one selected entry."""
    _validate_state(state)
    if action.is_null:
        return state
    assert action.recipient is not None and action.task is not None
    recipient_index = _learner_index(action.recipient)
    task_index = _task_index(action.task)
    updated = [list(row) for row in state]
    competence = state[recipient_index][task_index]
    updated[recipient_index][task_index] = competence + world.eta * (1.0 - competence)
    result: CompetenceState = (tuple(updated[0]), tuple(updated[1]))  # type: ignore[assignment]
    _validate_state(result)
    return result


def terminal_value(world: A1aWorld, state: CompetenceState) -> float:
    """Return max_i c_i,q1 for the frozen deterministic terminal task."""
    _validate_state(state)
    return max(operational_reward(world, learner, world.q1, state) for learner in LEARNERS)


def no_opportunity_value(world: A1aWorld, state: CompetenceState | None = None) -> float:
    """Return N=beta*V1(S)."""
    current = world.competence if state is None else state
    return world.beta * terminal_value(world, current)


def admissible_development_actions(world: A1aWorld) -> tuple[DevelopmentAction, ...]:
    """Enumerate null and both possible recipients for terminal-task learning."""
    return (
        NULL_DEVELOPMENT,
        DevelopmentAction(Learner.M1, world.q1),
        DevelopmentAction(Learner.M2, world.q1),
    )


def optimal_set(
    values: Mapping[object, float],
    *,
    abs_tol: float = DEFAULT_ABS_TOL,
) -> frozenset[object]:
    """Return every maximizer within an explicit strict numerical tolerance."""
    if not values:
        raise ValueError("cannot select an optimum from an empty mapping")
    if abs_tol < 0:
        raise ValueError("abs_tol must be non-negative")
    best = max(values.values())
    return frozenset(key for key, value in values.items() if abs(value - best) <= abs_tol)


def opportunity_value(
    world: A1aWorld,
    state: CompetenceState | None = None,
    *,
    abs_tol: float = DEFAULT_ABS_TOL,
) -> DevelopmentEvaluation:
    """Enumerate development actions and return D and all optimal actions."""
    current = world.competence if state is None else state
    action_values = {
        action: -development_cost(world, action)
        + world.beta * terminal_value(world, development_transition(world, current, action))
        for action in admissible_development_actions(world)
    }
    actions = optimal_set(action_values, abs_tol=abs_tol)
    return DevelopmentEvaluation(
        value=max(action_values.values()),
        optimal_actions=frozenset(actions),  # type: ignore[arg-type]
        action_values=action_values,
    )


def continuation_value(
    world: A1aWorld,
    learner: Learner,
    *,
    state: CompetenceState | None = None,
) -> float:
    """Integrate Bernoulli opportunity exactly: G=gD+(1-g)N."""
    current = world.competence if state is None else state
    no_opportunity = no_opportunity_value(world, current)
    with_opportunity = opportunity_value(world, current)
    return _continuation_from_components(
        world,
        learner,
        no_opportunity=no_opportunity,
        with_opportunity=with_opportunity.value,
    )


def _continuation_from_components(
    world: A1aWorld,
    learner: Learner,
    *,
    no_opportunity: float,
    with_opportunity: float,
) -> float:
    """Combine world-derived opportunity branches without resampling."""
    probability = opportunity_probability(world, learner, world.q0)
    return probability * with_opportunity + (1.0 - probability) * no_opportunity


def _selected_action(actions: frozenset[Learner]) -> Learner:
    """Choose a deterministic display action without discarding the full set."""
    return next(learner for learner in LEARNERS if learner in actions)


def _world_diagnostics(
    world: A1aWorld,
) -> tuple[
    DevelopmentEvaluation,
    float,
    dict[Learner, float],
    dict[Learner, float],
    dict[Learner, float],
]:
    development = opportunity_value(world)
    no_opportunity = no_opportunity_value(world)
    rewards = {
        learner: operational_reward(world, learner, world.q0) for learner in LEARNERS
    }
    probabilities = {
        learner: opportunity_probability(world, learner, world.q0)
        for learner in LEARNERS
    }
    continuations = {
        learner: _continuation_from_components(
            world,
            learner,
            no_opportunity=no_opportunity,
            with_opportunity=development.value,
        )
        for learner in LEARNERS
    }
    return development, no_opportunity, rewards, probabilities, continuations


def solve_hls(world: A1aWorld, *, abs_tol: float = DEFAULT_ABS_TOL) -> PolicySolution:
    """Enumerate HLS operational actions using immediate plus future value."""
    development, no_opportunity, rewards, probabilities, continuations = (
        _world_diagnostics(world)
    )
    totals = {
        learner: rewards[learner] + continuations[learner] for learner in LEARNERS
    }
    actions = optimal_set(totals, abs_tol=abs_tol)
    typed_actions = frozenset(actions)  # type: ignore[arg-type]
    return PolicySolution(
        optimal_value=max(totals.values()),
        optimal_operational_actions=typed_actions,
        selected_operational_action=_selected_action(typed_actions),
        operational_rewards=rewards,
        opportunity_probabilities=probabilities,
        continuation_values=continuations,
        total_values=totals,
        optimal_development_actions=development.optimal_actions,
        no_opportunity_value=no_opportunity,
        opportunity_value=development.value,
    )


def solve_strong_sep(
    world: A1aWorld,
    *,
    abs_tol: float = DEFAULT_ABS_TOL,
) -> StrongSEPSolution:
    """Route only by immediate reward, then solve development exactly.

    Every immediate-reward maximizer is retained.  ``value_min`` and
    ``value_max`` expose all tie resolutions; ``value`` is available only when
    that interval is numerically degenerate.
    """
    development, no_opportunity, rewards, probabilities, continuations = (
        _world_diagnostics(world)
    )
    immediate_actions = frozenset(
        optimal_set(rewards, abs_tol=abs_tol)  # type: ignore[arg-type]
    )
    expected_totals = {
        learner: rewards[learner] + continuations[learner]
        for learner in immediate_actions
    }
    value_min = min(expected_totals.values())
    value_max = max(expected_totals.values())
    value = value_min if abs(value_max - value_min) <= abs_tol else None
    return StrongSEPSolution(
        value=value,
        value_min=value_min,
        value_max=value_max,
        immediate_optimal_actions=immediate_actions,
        expected_total_values=expected_totals,
        operational_rewards=rewards,
        opportunity_probabilities=probabilities,
        continuation_values=continuations,
        optimal_development_actions=development.optimal_actions,
        no_opportunity_value=no_opportunity,
        opportunity_value=development.value,
    )


def solve_sep_omega(
    world: A1aWorld,
    *,
    abs_tol: float = DEFAULT_ABS_TOL,
) -> PolicySolution:
    """Solve the HLS objective given exact sufficient continuation information.

    In A1a, SEP-Omega and HLS mathematically optimize the same ``r(a)+G(a)``
    objective.  This separate entry point is a reducibility consistency check,
    not evidence of an independent competing algorithm.
    """
    development, no_opportunity, rewards, probabilities, continuations = (
        _world_diagnostics(world)
    )
    totals = {
        learner: rewards[learner] + continuations[learner] for learner in LEARNERS
    }
    actions = frozenset(optimal_set(totals, abs_tol=abs_tol))  # type: ignore[arg-type]
    return PolicySolution(
        optimal_value=max(totals.values()),
        optimal_operational_actions=actions,
        selected_operational_action=_selected_action(actions),
        operational_rewards=rewards,
        opportunity_probabilities=probabilities,
        continuation_values=continuations,
        total_values=totals,
        optimal_development_actions=development.optimal_actions,
        no_opportunity_value=no_opportunity,
        opportunity_value=development.value,
    )


def reference_worlds() -> dict[str, A1aWorld]:
    """Construct frozen worlds A--E and alias F to E's physical world."""
    base = A1aWorld(
        competence=((0.80, 0.50), (0.70, 0.20)),
        q0=1,
        q1=2,
        opportunity_baseline=(0.50, None),
        executor_opportunity=((0.20, None), (0.90, None)),
        rho=0.0,
        eta=0.80,
        kappa=0.02,
        beta=1.0,
    )
    world_e = replace(base, rho=0.75)
    return {
        "A": replace(base, eta=0.0, rho=1.0),
        "B": base,
        "C": replace(base, rho=0.25),
        "D": replace(base, rho=float(Fraction(50, 133))),
        "E": world_e,
        "F": world_e,
    }


def reference_diagnostics(world: A1aWorld) -> dict[str, float]:
    """Return diagnostics defined specifically for frozen worlds A--F.

    Those worlds define ``h=M1`` and ``s=M2``.  General primitive sweeps must
    use :func:`general_diagnostics`, which derives immediate optima.
    """
    h, s = Learner.M1, Learner.M2
    diagnostics = general_diagnostics(world)
    if diagnostics.immediate_optimal_actions != frozenset({h}):
        raise ValueError("reference diagnostics require unique immediate optimum M1")
    comparison = next(
        item
        for item in diagnostics.comparisons
        if item.immediate_optimum == h and item.alternative == s
    )
    return {
        "delta_R": comparison.delta_R,
        "delta_G": comparison.delta_G,
    }


def general_diagnostics(
    world: A1aWorld,
    *,
    abs_tol: float = DEFAULT_ABS_TOL,
) -> GeneralDiagnostics:
    """Derive immediate optima and compare each with non-optimal alternatives."""
    _, _, rewards, _, continuations = _world_diagnostics(world)
    immediate_actions = frozenset(
        optimal_set(rewards, abs_tol=abs_tol)  # type: ignore[arg-type]
    )
    comparisons = tuple(
        ImmediateActionComparison(
            immediate_optimum=optimum,
            alternative=alternative,
            delta_R=rewards[optimum] - rewards[alternative],
            delta_G=continuations[alternative] - continuations[optimum],
        )
        for optimum in LEARNERS
        if optimum in immediate_actions
        for alternative in LEARNERS
        if alternative not in immediate_actions
    )
    return GeneralDiagnostics(
        immediate_optimal_actions=immediate_actions,
        comparisons=comparisons,
    )
