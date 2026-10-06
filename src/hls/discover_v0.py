"""DISCOVER-v0: numerical belief-state control over a fixed capability repertoire.

The module isolates a deliberately narrow question.  A known, fixed collective
capability matrix ``S`` determines which productive allocations are available.
The production function has one of two latent, fixed CES weight vectors.  There
is no competence transition, learning-by-doing, transfer, role, or HLS policy
mechanism in this model.

The UNKNOWN value is evaluated by finite-horizon belief-state dynamic
programming with deterministic Gauss--Hermite integration of the Gaussian
observation.  It is a converged numerical calculation, not an exact symbolic
DP.  CES, Gaussian Bayes updating, and belief-state DP are imported standard
machinery used as experimental instrumentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import exp, isclose, isfinite, log, pi, sqrt
from typing import Iterable

import numpy as np


EXACT_TOL = 1e-10
N_AGENTS = 3
N_CAPABILITIES = 2
RHO = 0.5
DEFAULT_SIGMA = 0.10
DEFAULT_HORIZON = 3
DEFAULT_QUADRATURE_ORDER = 31
DEFAULT_PRIOR = 0.5
THETA_1 = (0.8, 0.2)
THETA_2 = (0.2, 0.8)

IndividualAction = tuple[float, float]
JointAction = tuple[IndividualAction, IndividualAction, IndividualAction]
State = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]

INDIVIDUAL_ACTIONS: tuple[IndividualAction, ...] = (
    (0.0, 0.0),
    (0.0, 1.0),
    (0.5, 0.5),
    (1.0, 0.0),
)
JOINT_ACTIONS: tuple[JointAction, ...] = tuple(product(INDIVIDUAL_ACTIONS, repeat=N_AGENTS))  # type: ignore[arg-type]


def _validate_probability(value: float, *, name: str) -> None:
    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]")


def validate_state(state: State) -> None:
    if len(state) != N_AGENTS or any(len(row) != N_CAPABILITIES for row in state):
        raise ValueError("DISCOVER-v0 requires a 3-agent × 2-capability state")
    if not all(isfinite(value) and 0.0 <= value <= 1.0 for row in state for value in row):
        raise ValueError("competence entries must be finite and lie in [0, 1]")


def validate_action(action: JointAction) -> None:
    if len(action) != N_AGENTS:
        raise ValueError("joint action must specify one allocation for each agent")
    if any(candidate not in INDIVIDUAL_ACTIONS for candidate in action):
        raise ValueError("action is outside the declared discrete individual-action set")


def canonical_state(state: State) -> State:
    """Quotient only worker-label permutations by lexicographically sorting rows."""
    validate_state(state)
    return tuple(sorted(state))  # type: ignore[return-value]


def state_budget(state: State) -> float:
    validate_state(state)
    return sum(sum(row) for row in state)


def enumerate_canonical_states() -> tuple[State, ...]:
    """Enumerate the specified 0/.5/1 states with total competence exactly 3."""
    representatives: set[State] = set()
    for units in product(range(3), repeat=N_AGENTS * N_CAPABILITIES):
        if sum(units) != 6:
            continue
        state: State = tuple(
            (units[2 * agent] / 2.0, units[2 * agent + 1] / 2.0)
            for agent in range(N_AGENTS)
        )  # type: ignore[assignment]
        representatives.add(canonical_state(state))
    return tuple(sorted(representatives))


def production_inputs(state: State, action: JointAction) -> tuple[float, float]:
    """Return ``Y_k = sum_i x_ik s_ik`` for the fixed state and allocation."""
    validate_state(state)
    validate_action(action)
    return tuple(
        sum(action[agent][capability] * state[agent][capability] for agent in range(N_AGENTS))
        for capability in range(N_CAPABILITIES)
    )  # type: ignore[return-value]


def ces_reward(outputs: tuple[float, float], alpha: tuple[float, float], *, rho: float = RHO) -> float:
    """Evaluate the declared CES layer, ``(sum_k alpha_k Y_k^rho)^(1/rho)``."""
    if rho == 0.0 or not isfinite(rho):
        raise ValueError("rho must be finite and nonzero in DISCOVER-v0")
    if len(outputs) != 2 or len(alpha) != 2:
        raise ValueError("CES requires two outputs and two weights")
    if any(not isfinite(value) or value < 0.0 for value in outputs):
        raise ValueError("CES outputs must be finite and non-negative")
    if any(not isfinite(weight) or weight < 0.0 for weight in alpha) or not isclose(sum(alpha), 1.0, abs_tol=EXACT_TOL):
        raise ValueError("CES weights must be finite, non-negative, and sum to one")
    return sum(weight * output**rho for weight, output in zip(alpha, outputs)) ** (1.0 / rho)


def means(state: State, action: JointAction, *, theta_1: tuple[float, float] = THETA_1, theta_2: tuple[float, float] = THETA_2) -> tuple[float, float]:
    outputs = production_inputs(state, action)
    return ces_reward(outputs, theta_1), ces_reward(outputs, theta_2)


def _action_key(action: JointAction) -> str:
    return ";".join(f"{left:g},{right:g}" for left, right in action)


def _optimal_actions(values: dict[JointAction, float], *, tolerance: float = EXACT_TOL) -> tuple[JointAction, ...]:
    maximum = max(values.values())
    return tuple(sorted((action for action, value in values.items() if maximum - value <= tolerance), key=_action_key))


def bayes_update(belief: float, observation: float, mu_1: float, mu_2: float, sigma: float) -> float:
    """Exact two-type Gaussian Bayes update, evaluated in stable log-odds form."""
    _validate_probability(belief, name="belief")
    if not isfinite(observation) or not isfinite(mu_1) or not isfinite(mu_2) or not isfinite(sigma) or sigma <= 0.0:
        raise ValueError("observation, means, and positive sigma must be finite")
    if abs(mu_1 - mu_2) <= EXACT_TOL:
        return belief
    if belief <= 0.0:
        return 0.0
    if belief >= 1.0:
        return 1.0
    log_prior_odds = log(belief) - log1p_neg(belief)
    log_likelihood_ratio = ((observation - mu_2) ** 2 - (observation - mu_1) ** 2) / (2.0 * sigma**2)
    log_odds = log_prior_odds + log_likelihood_ratio
    if log_odds >= 0.0:
        return 1.0 / (1.0 + exp(-log_odds))
    odds = exp(log_odds)
    return odds / (1.0 + odds)


def log1p_neg(value: float) -> float:
    """Small helper avoiding a dependency on a global numerical convention."""
    return log(1.0 - value)


@lru_cache(maxsize=None)
def gaussian_quadrature_nodes(mean: float, sigma: float, order: int) -> tuple[tuple[float, float], ...]:
    """Nodes and weights for expectation under ``Normal(mean, sigma^2)``."""
    if order < 1:
        raise ValueError("quadrature order must be positive")
    nodes, weights = np.polynomial.hermite.hermgauss(order)
    return tuple((mean + sqrt(2.0) * sigma * float(node), float(weight) / sqrt(pi)) for node, weight in zip(nodes, weights))


@dataclass(frozen=True)
class PolicyValue:
    value: float
    first_actions: tuple[JointAction, ...]
    first_action_values: tuple[tuple[JointAction, float], ...]


def known_policy_value(
    state: State,
    alpha: tuple[float, float],
    *,
    horizon: int = DEFAULT_HORIZON,
) -> PolicyValue:
    """Solve the revealed-theta finite horizon on the declared action space."""
    if horizon < 1:
        raise ValueError("horizon must be at least one")
    action_rewards = {action: ces_reward(production_inputs(state, action), alpha) for action in JOINT_ACTIONS}
    best_actions = _optimal_actions(action_rewards)
    best_reward = max(action_rewards.values())
    return PolicyValue(
        value=horizon * best_reward,
        first_actions=best_actions,
        first_action_values=tuple(sorted(((action, horizon * reward) for action, reward in action_rewards.items()), key=lambda item: _action_key(item[0]))),
    )


def known_value_bruteforce(state: State, alpha: tuple[float, float], *, horizon: int) -> float:
    """Independent exhaustive action-sequence enumeration for small-horizon controls."""
    if horizon < 1:
        raise ValueError("horizon must be at least one")
    rewards = {action: ces_reward(production_inputs(state, action), alpha) for action in JOINT_ACTIONS}
    return max(sum(rewards[action] for action in sequence) for sequence in product(JOINT_ACTIONS, repeat=horizon))


def known_expected_value(
    state: State,
    *,
    horizon: int = DEFAULT_HORIZON,
    prior: float = DEFAULT_PRIOR,
    theta_1: tuple[float, float] = THETA_1,
    theta_2: tuple[float, float] = THETA_2,
) -> float:
    _validate_probability(prior, name="prior")
    return prior * known_policy_value(state, theta_1, horizon=horizon).value + (1.0 - prior) * known_policy_value(state, theta_2, horizon=horizon).value


def _expectation_over_observation(
    belief: float,
    mu_1: float,
    mu_2: float,
    sigma: float,
    order: int,
    continuation,
) -> float:
    value = 0.0
    for mean, mixture_weight in ((mu_1, belief), (mu_2, 1.0 - belief)):
        if mixture_weight == 0.0:
            continue
        for observation, quadrature_weight in gaussian_quadrature_nodes(mean, sigma, order):
            value += mixture_weight * quadrature_weight * continuation(bayes_update(belief, observation, mu_1, mu_2, sigma))
    return value


def unknown_policy_value(
    state: State,
    *,
    horizon: int = DEFAULT_HORIZON,
    prior: float = DEFAULT_PRIOR,
    sigma: float = DEFAULT_SIGMA,
    quadrature_order: int = DEFAULT_QUADRATURE_ORDER,
    theta_1: tuple[float, float] = THETA_1,
    theta_2: tuple[float, float] = THETA_2,
) -> PolicyValue:
    """Numerically solve the finite belief-state DP using Gauss--Hermite integration."""
    validate_state(state)
    _validate_probability(prior, name="prior")
    if horizon < 1 or not isfinite(sigma) or sigma <= 0.0:
        raise ValueError("horizon must be positive and sigma must be finite and positive")
    action_means = {action: means(state, action, theta_1=theta_1, theta_2=theta_2) for action in JOINT_ACTIONS}
    # The 64 declared allocations remain the policy space.  Grouping identical
    # likelihood/reward pairs only removes redundant numerical DP evaluations;
    # the complete tied action set is restored in ``action_values`` below.
    mean_groups: dict[tuple[float, float], list[JointAction]] = {}
    for action, pair in action_means.items():
        mean_groups.setdefault(pair, []).append(action)

    if theta_1 == theta_2:
        static_values = {action: horizon * pair[0] for action, pair in action_means.items()}
        return PolicyValue(
            value=max(static_values.values()),
            first_actions=_optimal_actions(static_values),
            first_action_values=tuple(sorted(static_values.items(), key=lambda item: _action_key(item[0]))),
        )

    @lru_cache(maxsize=None)
    def value_at(remaining: int, belief_key: float) -> float:
        belief = float(belief_key)
        if remaining == 0:
            return 0.0
        values = pair_action_values(remaining, belief)
        return max(values.values())

    def pair_action_values(remaining: int, belief: float) -> dict[tuple[float, float], float]:
        pair_values: dict[tuple[float, float], float] = {}
        for mu_1, mu_2 in mean_groups:
            immediate = belief * mu_1 + (1.0 - belief) * mu_2
            future = 0.0 if remaining == 1 else _expectation_over_observation(
                belief,
                mu_1,
                mu_2,
                sigma,
                quadrature_order,
                lambda posterior: value_at(remaining - 1, posterior),
            )
            pair_values[(mu_1, mu_2)] = immediate + future
        return pair_values

    first_pair_values = pair_action_values(horizon, prior)
    first_values = {action: first_pair_values[pair] for action, pair in action_means.items()}
    return PolicyValue(
        value=max(first_values.values()),
        first_actions=_optimal_actions(first_values),
        first_action_values=tuple(sorted(first_values.items(), key=lambda item: _action_key(item[0]))),
    )


def unknown_value_bruteforce(
    state: State,
    *,
    horizon: int,
    prior: float,
    sigma: float,
    quadrature_order: int,
    theta_1: tuple[float, float] = THETA_1,
    theta_2: tuple[float, float] = THETA_2,
) -> float:
    """Uncached independent recursion for small-horizon DP validation."""
    action_means = {action: means(state, action, theta_1=theta_1, theta_2=theta_2) for action in JOINT_ACTIONS}

    def recurse(remaining: int, belief: float) -> float:
        if remaining == 0:
            return 0.0
        candidates = []
        for mu_1, mu_2 in action_means.values():
            immediate = belief * mu_1 + (1.0 - belief) * mu_2
            future = 0.0 if remaining == 1 else _expectation_over_observation(
                belief, mu_1, mu_2, sigma, quadrature_order, lambda posterior: recurse(remaining - 1, posterior)
            )
            candidates.append(immediate + future)
        return max(candidates)

    return recurse(horizon, prior)


@dataclass(frozen=True)
class DiscoverEvaluation:
    state: State
    known_value: float
    unknown_value: float
    discovery_cost: float
    known_theta_1: PolicyValue
    known_theta_2: PolicyValue
    unknown: PolicyValue


def evaluate_state(
    state: State,
    *,
    horizon: int = DEFAULT_HORIZON,
    prior: float = DEFAULT_PRIOR,
    sigma: float = DEFAULT_SIGMA,
    quadrature_order: int = DEFAULT_QUADRATURE_ORDER,
    theta_1: tuple[float, float] = THETA_1,
    theta_2: tuple[float, float] = THETA_2,
) -> DiscoverEvaluation:
    known_1 = known_policy_value(state, theta_1, horizon=horizon)
    known_2 = known_policy_value(state, theta_2, horizon=horizon)
    known = prior * known_1.value + (1.0 - prior) * known_2.value
    unknown = unknown_policy_value(
        state,
        horizon=horizon,
        prior=prior,
        sigma=sigma,
        quadrature_order=quadrature_order,
        theta_1=theta_1,
        theta_2=theta_2,
    )
    cost = known - unknown.value
    if cost < -EXACT_TOL:
        raise AssertionError("known-theta value must weakly dominate unknown-theta value")
    return DiscoverEvaluation(state, known, unknown.value, max(0.0, cost), known_1, known_2, unknown)


def capability_dual(state: State) -> State:
    validate_state(state)
    return tuple((row[1], row[0]) for row in state)  # type: ignore[return-value]


def labelled_state_count() -> int:
    return sum(1 for units in product(range(3), repeat=6) if sum(units) == 6)
