"""Finite problem beliefs over the continuous DISCOVER problem world.

The true problem and the controller's hypothesis family are deliberately
different objects.  A true problem determines production and observations;
the finite model determines predictions, Bayesian beliefs, and UNKNOWN
decisions.  Historical binary modules remain unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import exp, isclose, isfinite, log
from random import Random
from typing import Iterable

from .discover_develop_v0 import DEVELOP_KNOWN, DISCOVER_DEVELOP, DISCOVER_ONLY, MODES, STATIC_KNOWN
from .discover_develop_v2 import mis_v2_transition
from .discover_v0 import (
    DEFAULT_HORIZON,
    DEFAULT_QUADRATURE_ORDER,
    DEFAULT_SIGMA,
    EXACT_TOL,
    JOINT_ACTIONS,
    JointAction,
    PolicyValue,
    State,
    ces_reward,
    gaussian_quadrature_nodes,
    production_inputs,
    validate_state,
)


Problem = tuple[float, float]
HypothesisSet = tuple[Problem, ...]
BeliefVector = tuple[float, ...]


def validate_problem(problem: Problem) -> Problem:
    """Validate a point of the current problem simplex without normalizing it."""
    if len(problem) != 2:
        raise ValueError("a problem must contain exactly two capability weights")
    if any(not isfinite(value) or value < 0.0 for value in problem):
        raise ValueError("problem weights must be finite and non-negative")
    if not isclose(sum(problem), 1.0, rel_tol=0.0, abs_tol=EXACT_TOL):
        raise ValueError("problem weights must sum to one")
    return tuple(float(value) for value in problem)  # type: ignore[return-value]


def validate_belief(belief: Iterable[float], size: int) -> BeliefVector:
    """Validate a finite probability vector without silently normalizing it."""
    values = tuple(float(value) for value in belief)
    if size < 1 or len(values) != size:
        raise ValueError("belief length must equal the non-empty hypothesis count")
    if any(not isfinite(value) or value < 0.0 for value in values):
        raise ValueError("belief probabilities must be finite and non-negative")
    if not isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=EXACT_TOL):
        raise ValueError("belief probabilities must sum to one")
    return values


def uniform_prior(size: int) -> BeliefVector:
    if size < 1:
        raise ValueError("hypothesis count must be positive")
    return (1.0 / size,) * size


def canonical_model(
    hypotheses: Iterable[Problem], prior: Iterable[float] | None = None
) -> tuple[HypothesisSet, BeliefVector]:
    """Return a deterministic hypothesis order and the correspondingly permuted prior.

    Descending first-coordinate order preserves the historical theta1/theta2
    ordering while making input permutations observationally irrelevant.
    Duplicate hypotheses are rejected because they do not define distinct
    elements of a finite hypothesis set.
    """
    raw_hypotheses = tuple(validate_problem(problem) for problem in hypotheses)
    if not raw_hypotheses:
        raise ValueError("the hypothesis set must be non-empty")
    raw_prior = uniform_prior(len(raw_hypotheses)) if prior is None else validate_belief(prior, len(raw_hypotheses))
    indexed = sorted(zip(raw_hypotheses, raw_prior), key=lambda item: (-item[0][0], -item[0][1]))
    ordered = tuple(problem for problem, _ in indexed)
    if len(set(ordered)) != len(ordered):
        raise ValueError("hypotheses must be distinct")
    ordered_prior = tuple(probability for _, probability in indexed)
    return ordered, validate_belief(ordered_prior, len(ordered))


def hypothesis_means(state: State, action: JointAction, hypotheses: HypothesisSet) -> tuple[float, ...]:
    outputs = production_inputs(state, action)
    return tuple(ces_reward(outputs, problem) for problem in hypotheses)


def expected_reward(belief: BeliefVector, predicted_means: tuple[float, ...]) -> float:
    validated = validate_belief(belief, len(predicted_means))
    if any(not isfinite(value) for value in predicted_means):
        raise ValueError("predicted means must be finite")
    return sum(probability * mean for probability, mean in zip(validated, predicted_means))


def finite_bayes_update(
    belief: BeliefVector,
    observation: float,
    predicted_means: tuple[float, ...],
    sigma: float = DEFAULT_SIGMA,
) -> BeliefVector:
    """Stable finite Gaussian Bayes update over the declared hypotheses only."""
    prior = validate_belief(belief, len(predicted_means))
    if not isfinite(observation) or not isfinite(sigma) or sigma <= 0.0:
        raise ValueError("observation and positive sigma must be finite")
    if any(not isfinite(mean) for mean in predicted_means):
        raise ValueError("predicted means must be finite")
    if len(prior) == 1:
        return (1.0,)
    if max(predicted_means) - min(predicted_means) <= EXACT_TOL:
        return prior
    log_weights = tuple(
        -float("inf") if probability == 0.0 else log(probability) - 0.5 * ((observation - mean) / sigma) ** 2
        for probability, mean in zip(prior, predicted_means)
    )
    maximum = max(log_weights)
    weights = tuple(0.0 if value == -float("inf") else exp(value - maximum) for value in log_weights)
    total = sum(weights)
    if not isfinite(total) or total <= 0.0:
        raise ArithmeticError("finite Bayes normalization failed")
    posterior = tuple(weight / total for weight in weights)
    return validate_belief(posterior, len(prior))


def _action_key(action: JointAction) -> str:
    return ";".join(f"{left:g},{right:g}" for left, right in action)


def _optimal_actions(values: dict[JointAction, float]) -> tuple[JointAction, ...]:
    maximum = max(values.values())
    return tuple(sorted((action for action, value in values.items() if maximum - value <= EXACT_TOL), key=_action_key))


def finite_unknown_policy_value(
    state: State,
    hypotheses: Iterable[Problem],
    *,
    prior: Iterable[float] | None = None,
    horizon: int = DEFAULT_HORIZON,
    sigma: float = DEFAULT_SIGMA,
    quadrature_order: int = DEFAULT_QUADRATURE_ORDER,
) -> PolicyValue:
    """Finite-horizon belief-state DP for an arbitrary finite hypothesis set."""
    validate_state(state)
    model, initial_belief = canonical_model(hypotheses, prior)
    if horizon < 1 or not isfinite(sigma) or sigma <= 0.0:
        raise ValueError("horizon and sigma must be positive")
    action_means = {action: hypothesis_means(state, action, model) for action in JOINT_ACTIONS}
    mean_groups: dict[tuple[float, ...], list[JointAction]] = {}
    for action, predicted in action_means.items():
        mean_groups.setdefault(predicted, []).append(action)

    @lru_cache(maxsize=None)
    def value_at(remaining: int, belief: BeliefVector) -> float:
        if remaining == 0:
            return 0.0
        return max(group_values(remaining, belief).values())

    def group_values(remaining: int, belief: BeliefVector) -> dict[tuple[float, ...], float]:
        values: dict[tuple[float, ...], float] = {}
        for predicted in mean_groups:
            immediate = expected_reward(belief, predicted)
            future = 0.0
            if remaining > 1:
                for probability, mean in zip(belief, predicted):
                    if probability == 0.0:
                        continue
                    for observation, weight in gaussian_quadrature_nodes(mean, sigma, quadrature_order):
                        posterior = finite_bayes_update(belief, observation, predicted, sigma)
                        future += probability * weight * value_at(remaining - 1, posterior)
            values[predicted] = immediate + future
        return values

    first_group_values = group_values(horizon, initial_belief)
    first_values = {action: first_group_values[predicted] for action, predicted in action_means.items()}
    return PolicyValue(
        value=max(first_values.values()),
        first_actions=_optimal_actions(first_values),
        first_action_values=tuple(sorted(first_values.items(), key=lambda item: _action_key(item[0]))),
    )


def _best_immediate(state: State, belief: BeliefVector, hypotheses: HypothesisSet) -> tuple[JointAction, float]:
    values = {
        action: expected_reward(belief, hypothesis_means(state, action, hypotheses))
        for action in JOINT_ACTIONS
    }
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= EXACT_TOL), maximum


def _best_true_immediate(state: State, problem: Problem) -> tuple[JointAction, float]:
    values = {action: ces_reward(production_inputs(state, action), problem) for action in JOINT_ACTIONS}
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= EXACT_TOL), maximum


def finite_choose_dynamic_action_v2(
    state: State,
    belief: BeliefVector,
    hypotheses: HypothesisSet,
    *,
    remaining: int,
    develop: bool,
    eta: float,
) -> tuple[JointAction, float]:
    """The frozen two-step MPC with only scalar belief generalized to finite M."""
    model, current_belief = canonical_model(hypotheses, belief)
    values: dict[JointAction, float] = {}
    for action in JOINT_ACTIONS:
        predicted = hypothesis_means(state, action, model)
        immediate = expected_reward(current_belief, predicted)
        if remaining == 1:
            values[action] = immediate
            continue
        next_state = mis_v2_transition(state, action, enabled=develop, eta=eta)
        future = 0.0
        for probability, mean in zip(current_belief, predicted):
            if probability == 0.0:
                continue
            for observation, weight in gaussian_quadrature_nodes(mean, DEFAULT_SIGMA, 3):
                posterior = finite_bayes_update(current_belief, observation, predicted, DEFAULT_SIGMA)
                future += probability * weight * _best_immediate(next_state, posterior, model)[1]
        values[action] = immediate + future
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= EXACT_TOL), maximum


def _known_dynamic_action_v2(
    state: State, problem: Problem, *, remaining: int, develop: bool, eta: float
) -> tuple[JointAction, float]:
    """Known oracle MPC evaluated directly at the true problem, without a belief."""
    values: dict[JointAction, float] = {}
    for action in JOINT_ACTIONS:
        immediate = ces_reward(production_inputs(state, action), problem)
        if remaining == 1:
            values[action] = immediate
        else:
            next_state = mis_v2_transition(state, action, enabled=develop, eta=eta)
            values[action] = immediate + _best_true_immediate(next_state, problem)[1]
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= EXACT_TOL), maximum


@dataclass(frozen=True)
class FiniteBeliefStep:
    problem_id: int
    step_id: int
    true_problem: Problem
    belief_before: BeliefVector | None
    belief_after: BeliefVector | None
    state_before: State
    state_after: State
    action: JointAction
    true_mean: float
    observed_reward: float
    cumulative_reward: float
    mode: str


def run_finite_problem_sequence(
    initial_state: State,
    true_problems: Iterable[Problem],
    hypotheses: Iterable[Problem],
    *,
    prior: Iterable[float] | None = None,
    mode: str,
    eta: float,
    horizon: int = DEFAULT_HORIZON,
    seed: int = 20261006,
) -> tuple[FiniteBeliefStep, ...]:
    """Run problems with continuous world truth and a reset finite agent belief."""
    if mode not in MODES or horizon < 1:
        raise ValueError("invalid mode or horizon")
    validate_state(initial_state)
    model, reset_prior = canonical_model(hypotheses, prior)
    world_problems = tuple(validate_problem(problem) for problem in true_problems)
    rng, state, cumulative, rows = Random(seed), initial_state, 0.0, []
    for problem_id, true_problem in enumerate(world_problems):
        known = mode in (DEVELOP_KNOWN, STATIC_KNOWN)
        develop = mode in (DISCOVER_DEVELOP, DEVELOP_KNOWN)
        belief: BeliefVector | None = None if known else reset_prior
        for step_id in range(horizon):
            remaining = horizon - step_id
            before = state
            if mode == DISCOVER_ONLY:
                assert belief is not None
                action = finite_unknown_policy_value(
                    state, model, prior=belief, horizon=remaining
                ).first_actions[0]
            elif mode == DISCOVER_DEVELOP:
                assert belief is not None
                action = finite_choose_dynamic_action_v2(
                    state, belief, model, remaining=remaining, develop=True, eta=eta
                )[0]
            elif mode == STATIC_KNOWN:
                action = _best_true_immediate(state, true_problem)[0]
            else:
                action = _known_dynamic_action_v2(
                    state, true_problem, remaining=remaining, develop=True, eta=eta
                )[0]
            true_mean = ces_reward(production_inputs(state, action), true_problem)
            observed = true_mean + DEFAULT_SIGMA * rng.gauss(0.0, 1.0)
            if belief is None:
                after_belief = None
            else:
                predicted = hypothesis_means(state, action, model)
                after_belief = finite_bayes_update(belief, observed, predicted, DEFAULT_SIGMA)
            state = mis_v2_transition(state, action, enabled=develop, eta=eta)
            cumulative += true_mean
            rows.append(
                FiniteBeliefStep(
                    problem_id, step_id, true_problem, belief, after_belief, before,
                    state, action, true_mean, observed, cumulative, mode
                )
            )
            belief = after_belief
    return tuple(rows)
