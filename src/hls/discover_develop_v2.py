"""DISCOVER x DEVELOP with the MIS-v2 exponential capability-gap law."""

from __future__ import annotations

from math import exp, isfinite, log1p
from random import Random

from .discover_develop_v0 import (
    DEVELOP_KNOWN,
    DISCOVER_DEVELOP,
    DISCOVER_ONLY,
    MODES,
    STATIC_KNOWN,
    Step,
)
from .discover_v0 import (
    DEFAULT_PRIOR,
    DEFAULT_SIGMA,
    JOINT_ACTIONS,
    N_AGENTS,
    N_CAPABILITIES,
    State,
    THETA_1,
    bayes_update,
    gaussian_quadrature_nodes,
    means,
    unknown_policy_value,
    validate_action,
    validate_state,
)


def eta_to_lambda(eta: float) -> float:
    """Convert one-unit remaining-gap closure eta to an exposure rate."""
    if not isfinite(eta) or not 0.0 < eta < 1.0:
        raise ValueError("eta must be finite and lie strictly inside (0, 1)")
    return -log1p(-eta)


def capability_after_exposure(capability: float, exposure: float, *, rate: float) -> float:
    """Return 1 - (1-s) exp(-rate*x), without clipping or saturation clamps."""
    if not isfinite(capability) or not 0.0 <= capability <= 1.0:
        raise ValueError("capability must be finite and lie in [0, 1]")
    if not isfinite(exposure) or exposure < 0.0:
        raise ValueError("exposure must be finite and non-negative")
    if not isfinite(rate) or rate <= 0.0:
        raise ValueError("rate must be finite and positive")
    if exposure == 0.0:
        return capability
    return 1.0 - (1.0 - capability) * exp(-rate * exposure)


def capability_after_binary_exposure(capability: float, *, eta: float) -> float:
    """Equivalent one-standard-exposure form s + eta(1-s)."""
    if not isfinite(capability) or not 0.0 <= capability <= 1.0:
        raise ValueError("capability must be finite and lie in [0, 1]")
    eta_to_lambda(eta)
    return capability + eta * (1.0 - capability)


def mis_v2_transition(state: State, action, *, enabled: bool, eta: float) -> State:
    """Apply MIS-v2 to each objectively exercised individual-capability cell."""
    validate_state(state)
    validate_action(action)
    rate = eta_to_lambda(eta)
    if not enabled:
        return state
    return tuple(
        tuple(capability_after_exposure(state[i][k], action[i][k], rate=rate) for k in range(N_CAPABILITIES))
        for i in range(N_AGENTS)
    )  # type: ignore[return-value]


def _reward(state: State, action, belief: float) -> float:
    mu_1, mu_2 = means(state, action)
    return belief * mu_1 + (1.0 - belief) * mu_2


def _best_immediate(state: State, belief: float):
    values = {action: _reward(state, action, belief) for action in JOINT_ACTIONS}
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= 1e-10), maximum


def choose_dynamic_action_v2(state: State, belief: float, *, remaining: int, develop: bool, eta: float):
    """Frozen two-step MPC with only its capability transition replaced."""
    values = {}
    for action in JOINT_ACTIONS:
        immediate = _reward(state, action, belief)
        if remaining == 1:
            values[action] = immediate
            continue
        next_state = mis_v2_transition(state, action, enabled=develop, eta=eta)
        mu_1, mu_2 = means(state, action)
        future = 0.0
        for mean, probability in ((mu_1, belief), (mu_2, 1.0 - belief)):
            for observation, weight in gaussian_quadrature_nodes(mean, DEFAULT_SIGMA, 3):
                posterior = bayes_update(belief, observation, mu_1, mu_2, DEFAULT_SIGMA)
                future += probability * weight * _best_immediate(next_state, posterior)[1]
        values[action] = immediate + future
    best = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - best) <= 1e-10), best


def run_sequence_v2(
    initial_state: State,
    thetas: tuple[tuple[float, float], ...],
    *,
    mode: str,
    eta: float,
    horizon: int = 3,
    seed: int = 20261006,
) -> tuple[Step, ...]:
    """Run the frozen prototype with MIS-v2 as its sole physics intervention."""
    if mode not in MODES or horizon < 1:
        raise ValueError("invalid mode or horizon")
    eta_to_lambda(eta)
    rng, state, cumulative, rows = Random(seed), initial_state, 0.0, []
    for problem_id, theta in enumerate(thetas):
        known = mode in (DEVELOP_KNOWN, STATIC_KNOWN)
        develop = mode in (DISCOVER_DEVELOP, DEVELOP_KNOWN)
        belief = 1.0 if known and theta == THETA_1 else 0.0 if known else DEFAULT_PRIOR
        for step_id in range(horizon):
            remaining = horizon - step_id
            before = state
            if mode == DISCOVER_ONLY:
                action = unknown_policy_value(state, horizon=remaining, prior=belief).first_actions[0]
            elif mode == STATIC_KNOWN:
                action = _best_immediate(state, belief)[0]
            else:
                action = choose_dynamic_action_v2(state, belief, remaining=remaining, develop=develop, eta=eta)[0]
            mu_1, mu_2 = means(state, action)
            true_mu = mu_1 if theta == THETA_1 else mu_2
            observed = true_mu + DEFAULT_SIGMA * rng.gauss(0.0, 1.0)
            after_belief = belief if known else bayes_update(belief, observed, mu_1, mu_2, DEFAULT_SIGMA)
            state = mis_v2_transition(state, action, enabled=develop, eta=eta)
            cumulative += true_mu
            rows.append(
                Step(problem_id, step_id, "theta1" if theta == THETA_1 else "theta2", belief, after_belief,
                     before, state, action, true_mu, observed, cumulative, mode)
            )
            belief = after_belief
    return tuple(rows)
