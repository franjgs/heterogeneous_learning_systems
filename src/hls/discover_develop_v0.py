"""Small DISCOVER x DEVELOP prototype using frozen DISCOVER-v0 and MIS physics."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random

from .discover_v0 import (
    DEFAULT_PRIOR, DEFAULT_SIGMA, JOINT_ACTIONS, State, THETA_1, THETA_2,
    bayes_update, means, production_inputs, unknown_policy_value,
)

# Canonical MIS reference: MinimalReferenceScenario.reference_configurations()
# uses LearningRule.DIMINISHING with learning_scale=1.5.
MIS_LEARNING_SCALE = 1.5

DISCOVER_DEVELOP = "discover_develop"
DISCOVER_ONLY = "discover_only"
DEVELOP_KNOWN = "develop_known"
STATIC_KNOWN = "static_known"
MODES = (DISCOVER_DEVELOP, DISCOVER_ONLY, DEVELOP_KNOWN, STATIC_KNOWN)


def mis_transition(state: State, action, *, enabled: bool) -> State:
    """Dimensionally lift canonical MIS to fractional exercised effort x[i,k]."""
    if not enabled:
        return state
    rows = [list(row) for row in state]
    for worker, allocation in enumerate(action):
        for capability, effort in enumerate(allocation):
            current = rows[worker][capability]
            rows[worker][capability] = min(1.0, current + effort * MIS_LEARNING_SCALE * (1.0 - current) ** 2)
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def _reward(state: State, action, belief: float) -> float:
    mu_1, mu_2 = means(state, action)
    return belief * mu_1 + (1.0 - belief) * mu_2


def _best_immediate(state: State, belief: float):
    values = {action: _reward(state, action, belief) for action in JOINT_ACTIONS}
    maximum = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - maximum) <= 1e-10), maximum


def choose_dynamic_action(state: State, belief: float, *, remaining: int, develop: bool):
    """Standard two-step receding-horizon Bellman look-ahead for dynamic S.

    Exact full H=3 belief/S branching is intractable in this deliberately
    minimal continuous-observation prototype.  This is not a local score: it
    evaluates the Gaussian-Bayes expectation of the next optimal decision on
    the action-induced MIS state, then replans at the next decision.
    """
    values = {}
    for action in JOINT_ACTIONS:
        immediate = _reward(state, action, belief)
        if remaining == 1:
            values[action] = immediate
            continue
        next_state = mis_transition(state, action, enabled=develop)
        mu_1, mu_2 = means(state, action)
        # Deterministic three-node Gauss--Hermite rule is sufficient only as a
        # control policy evaluator here; observation realization remains seeded.
        from .discover_v0 import gaussian_quadrature_nodes
        future = 0.0
        for mean, probability in ((mu_1, belief), (mu_2, 1.0 - belief)):
            for observation, weight in gaussian_quadrature_nodes(mean, DEFAULT_SIGMA, 3):
                posterior = bayes_update(belief, observation, mu_1, mu_2, DEFAULT_SIGMA)
                future += probability * weight * _best_immediate(next_state, posterior)[1]
        values[action] = immediate + future
    best = max(values.values())
    return next(action for action in JOINT_ACTIONS if abs(values[action] - best) <= 1e-10), best


@dataclass(frozen=True)
class Step:
    problem_id: int
    step_id: int
    true_theta: str
    belief_before: float
    belief_after: float
    state_before: State
    state_after: State
    action: tuple
    expected_reward_true: float
    observed_reward: float
    cumulative_expected_reward: float
    mode: str


def run_sequence(initial_state: State, thetas: tuple[tuple[float, float], ...], *, mode: str, horizon: int = 3, seed: int = 20261006) -> tuple[Step, ...]:
    """Run fixed true-theta problems; DISCOVER modes never receive true theta."""
    if mode not in MODES or horizon < 1:
        raise ValueError("invalid mode or horizon")
    rng, state, cumulative, rows = Random(seed), initial_state, 0.0, []
    for problem_id, theta in enumerate(thetas):
        known, develop = mode in (DEVELOP_KNOWN, STATIC_KNOWN), mode in (DISCOVER_DEVELOP, DEVELOP_KNOWN)
        belief = 1.0 if known and theta == THETA_1 else 0.0 if known else DEFAULT_PRIOR
        for step_id in range(horizon):
            remaining = horizon - step_id
            before = state
            if mode == DISCOVER_ONLY:
                action = unknown_policy_value(state, horizon=remaining, prior=belief).first_actions[0]
            elif mode == STATIC_KNOWN:
                action = _best_immediate(state, belief)[0]
            else:
                action = choose_dynamic_action(state, belief, remaining=remaining, develop=develop)[0]
            mu_1, mu_2 = means(state, action)
            true_mu = mu_1 if theta == THETA_1 else mu_2
            observed = true_mu + DEFAULT_SIGMA * rng.gauss(0.0, 1.0)
            after_belief = belief if known else bayes_update(belief, observed, mu_1, mu_2, DEFAULT_SIGMA)
            state = mis_transition(state, action, enabled=develop)
            cumulative += true_mu
            rows.append(Step(problem_id, step_id, "theta1" if theta == THETA_1 else "theta2", belief, after_belief, before, state, action, true_mu, observed, cumulative, mode))
            belief = after_belief
    return tuple(rows)
