"""Derived production--information geometry for the frozen DISCOVER-v0 model.

This module does not alter the CES layer, action repertoire, Bayesian update,
or belief-state control.  It only exposes action-level quantities already
implicit in the fixed model for audit and reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from .discover_v0 import (
    DEFAULT_PRIOR,
    DEFAULT_SIGMA,
    EXACT_TOL,
    JOINT_ACTIONS,
    JointAction,
    State,
    THETA_1,
    THETA_2,
    means,
)


@dataclass(frozen=True)
class ActionInformation:
    """Existing one-action production and Gaussian-discrimination quantities."""

    action: JointAction
    mu_theta1: float
    mu_theta2: float
    reward_prior: float
    discriminability: float
    kl: float
    production_gap: float
    pareto_optimal: bool
    production_retention: float
    discriminability_retention: float


def action_information_geometry(
    state: State,
    *,
    prior: float = DEFAULT_PRIOR,
    sigma: float = DEFAULT_SIGMA,
    theta_1: tuple[float, float] = THETA_1,
    theta_2: tuple[float, float] = THETA_2,
) -> tuple[ActionInformation, ...]:
    """Return the complete 64-action production--information ledger.

    Pareto dominance maximizes both prior reward and discriminability.  Equal
    points are retained: the model's action repertoire, rather than a quotient
    over tied allocations, is the audited object.
    """
    if not 0.0 <= prior <= 1.0:
        raise ValueError("prior must lie in [0, 1]")
    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    raw = []
    for action in JOINT_ACTIONS:
        mu_1, mu_2 = means(state, action, theta_1=theta_1, theta_2=theta_2)
        reward = prior * mu_1 + (1.0 - prior) * mu_2
        discriminability = abs(mu_1 - mu_2) / sigma
        raw.append((action, mu_1, mu_2, reward, discriminability, discriminability**2 / 2.0))
    max_reward = max(item[3] for item in raw)
    max_d = max(item[4] for item in raw)
    result = []
    for action, mu_1, mu_2, reward, discriminability, kl in raw:
        dominated = any(
            other_reward >= reward - EXACT_TOL
            and other_d >= discriminability - EXACT_TOL
            and (other_reward > reward + EXACT_TOL or other_d > discriminability + EXACT_TOL)
            for _, _, _, other_reward, other_d, _ in raw
        )
        result.append(
            ActionInformation(
                action=action,
                mu_theta1=mu_1,
                mu_theta2=mu_2,
                reward_prior=reward,
                discriminability=discriminability,
                kl=kl,
                production_gap=max_reward - reward,
                pareto_optimal=not dominated,
                production_retention=1.0 if isclose(max_reward, 0.0, abs_tol=EXACT_TOL) else reward / max_reward,
                discriminability_retention=1.0 if isclose(max_d, 0.0, abs_tol=EXACT_TOL) else discriminability / max_d,
            )
        )
    return tuple(result)


def pareto_frontier(items: tuple[ActionInformation, ...]) -> tuple[ActionInformation, ...]:
    """Return all retained action-level Pareto points in deterministic order."""
    return tuple(item for item in items if item.pareto_optimal)


def action_information_by_action(items: tuple[ActionInformation, ...]) -> dict[JointAction, ActionInformation]:
    """Index an audited complete ledger without changing its action set."""
    return {item.action: item for item in items}
