"""Diagnostic regime classification over the fixed G3-H ground truth.

This module does not introduce a policy or a new HLS mechanism.  It compares
current use, local organization-development value, and the closed G3-H
look-ahead oracle on complete tolerance-aware optimal action sets.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from statistics import median
from typing import Iterable, Literal, Sequence

from .g3_h_organizational_value import (
    G3HLearningProfile,
    development_g3h,
    dynamic_value_g3h,
    local_value_g3h,
    transition_g3h,
)
from .g3_organizational_value import G3A_ASSIGNMENTS, G3State, G3aAction, reward_g3a
from .minimal_reference_scenario import EXACT_TOL


REGIME_TOL = EXACT_TOL
Regime = Literal["R0_USE_SUFFICIENT", "R1_LOCAL_NECESSARY_SUFFICIENT", "R2_LOCAL_INSUFFICIENT"]


@dataclass(frozen=True)
class G3HActionEvaluation:
    """Auditable values for one current G3-H action."""

    action: G3aAction
    reward: float
    development: float
    local_value: float
    dynamic_value: float
    successor: G3State
    operational_gap: float


@dataclass(frozen=True)
class G3HPointEvaluation:
    """Complete, order-independent classification of one state/profile point."""

    state: G3State
    learning_profile: G3HLearningProfile
    actions: tuple[G3HActionEvaluation, ...]
    optimal_use: frozenset[G3aAction]
    optimal_local: frozenset[G3aAction]
    optimal_dynamic: frozenset[G3aAction]
    regime: Regime
    r2_reversion: bool
    j_star: float
    j_use: float
    j_local: float
    regret_use: float
    regret_local: float


def _optimal_actions(values: dict[G3aAction, float], tolerance: float) -> frozenset[G3aAction]:
    maximum = max(values.values())
    return frozenset(action for action, value in values.items() if maximum - value <= tolerance)


def _zero_if_close(value: float, tolerance: float) -> float:
    if abs(value) <= tolerance:
        return 0.0
    if value < 0.0:
        raise AssertionError("regret cannot be materially negative")
    return value


def evaluate_point(
    state: G3State,
    learning_profile: G3HLearningProfile,
    *,
    actions: Sequence[G3aAction] = G3A_ASSIGNMENTS,
    tolerance: float = REGIME_TOL,
) -> G3HPointEvaluation:
    """Evaluate all three decision levels without selecting an arbitrary argmax."""
    if tolerance < 0.0:
        raise ValueError("tolerance must be non-negative")
    if set(actions) != set(G3A_ASSIGNMENTS) or len(actions) != len(G3A_ASSIGNMENTS):
        raise ValueError("actions must enumerate every G3a assignment exactly once")

    preliminary = []
    use_values: dict[G3aAction, float] = {}
    local_values: dict[G3aAction, float] = {}
    dynamic_values: dict[G3aAction, float] = {}
    for action in actions:
        reward = reward_g3a(state, action)
        development = development_g3h(state, action, learning_profile)
        local = local_value_g3h(state, action, learning_profile)
        dynamic = dynamic_value_g3h(state, action, learning_profile)
        successor = transition_g3h(state, action, learning_profile)
        use_values[action] = reward
        local_values[action] = local
        dynamic_values[action] = dynamic
        preliminary.append((action, reward, development, local, dynamic, successor))

    use_optimal = _optimal_actions(use_values, tolerance)
    local_optimal = _optimal_actions(local_values, tolerance)
    dynamic_optimal = _optimal_actions(dynamic_values, tolerance)
    use_intersects = bool(use_optimal & dynamic_optimal)
    local_intersects = bool(local_optimal & dynamic_optimal)
    if use_intersects:
        regime: Regime = "R0_USE_SUFFICIENT"
    elif local_intersects:
        regime = "R1_LOCAL_NECESSARY_SUFFICIENT"
    else:
        regime = "R2_LOCAL_INSUFFICIENT"

    j_star = max(dynamic_values.values())
    j_use = max(dynamic_values[action] for action in use_optimal)
    j_local = max(dynamic_values[action] for action in local_optimal)
    observations = tuple(
        G3HActionEvaluation(
            action=action,
            reward=reward,
            development=development,
            local_value=local,
            dynamic_value=dynamic,
            successor=successor,
            operational_gap=max(use_values.values()) - reward,
        )
        for action, reward, development, local, dynamic, successor in preliminary
    )
    return G3HPointEvaluation(
        state=state,
        learning_profile=learning_profile,
        actions=observations,
        optimal_use=use_optimal,
        optimal_local=local_optimal,
        optimal_dynamic=dynamic_optimal,
        regime=regime,
        r2_reversion=use_intersects and not local_intersects,
        j_star=j_star,
        j_use=j_use,
        j_local=j_local,
        regret_use=_zero_if_close(j_star - j_use, tolerance),
        regret_local=_zero_if_close(j_star - j_local, tolerance),
    )


def grid_states(values: Sequence[float]) -> Iterable[G3State]:
    """Yield the transparent Cartesian grid over the six G3-H state entries."""
    for flat in product(values, repeat=6):
        yield ((flat[0], flat[1]), (flat[2], flat[3]), (flat[4], flat[5]))


def controlled_learning_profiles(
    eta: float,
    delta: float,
    *,
    include_permutations: bool = True,
) -> tuple[G3HLearningProfile, ...]:
    """Return homogeneous and controlled ``(eta-delta, eta, eta+delta)`` profiles."""
    profile = (eta - delta, eta, eta + delta)
    if min(profile) < 0.0:
        raise ValueError("eta - delta must be non-negative")
    profiles: set[G3HLearningProfile] = {(eta, eta, eta)}
    if include_permutations:
        from itertools import permutations

        profiles.update(permutations(profile))
    else:
        profiles.add(profile)
    return tuple(sorted(profiles))


def summarize_regrets(values: Iterable[float]) -> dict[str, float | None]:
    """Return raw-regret summary statistics without normalisation."""
    collected = tuple(values)
    if not collected:
        return {"min": None, "median": None, "max": None}
    return {"min": min(collected), "median": median(collected), "max": max(collected)}
