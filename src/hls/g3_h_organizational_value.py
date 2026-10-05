"""Exact heterogeneous-learning extension of the documented G3a physics.

G3-H changes only G3's common learning scale into a fixed scale for each
worker.  Reward, feasible assignments, the G3a terminal operator, and the MIS
learning increment are imported from :mod:`hls.g3_organizational_value`.
"""

from __future__ import annotations

from math import isfinite

from .g3_organizational_value import (
    G3A_ASSIGNMENTS,
    G3State,
    G3aAction,
    learning_increment,
    reward_g3a,
    value_g3a_direct,
)


G3HLearningProfile = tuple[float, float, float]


def _validate_learning_profile(learning_profile: G3HLearningProfile) -> None:
    if len(learning_profile) != 3:
        raise ValueError("G3-H requires exactly one learning scale per worker")
    if not all(isfinite(scale) and scale >= 0.0 for scale in learning_profile):
        raise ValueError("G3-H learning scales must be finite and non-negative")


def transition_g3h(state: G3State, action: G3aAction, learning_profile: G3HLearningProfile) -> G3State:
    """Apply the MIS increment to G3a's two executed competences using ``eta_i``."""
    _validate_learning_profile(learning_profile)
    # ``reward_g3a`` performs the canonical G3 state and action validation.
    reward_g3a(state, action)
    rows = [list(row) for row in state]
    for worker, task in ((action[0], 0), (action[1], 1)):
        rows[worker][task] += learning_increment(rows[worker][task], learning_profile[worker])
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def development_g3h(state: G3State, action: G3aAction, learning_profile: G3HLearningProfile) -> float:
    """Return the canonical G3a development value ``V(F(S,a))-V(S)``."""
    return value_g3a_direct(transition_g3h(state, action, learning_profile)) - value_g3a_direct(state)


def local_value_g3h(state: G3State, action: G3aAction, learning_profile: G3HLearningProfile) -> float:
    """Return G3-H's local use--development value ``M_S(a)=R(S,a)+D(S,a)``."""
    return reward_g3a(state, action) + development_g3h(state, action, learning_profile)


def dynamic_value_g3h(state: G3State, action: G3aAction, learning_profile: G3HLearningProfile) -> float:
    """Return the closed G3-H one-additional-opportunity oracle ``Q_S(a)``."""
    successor = transition_g3h(state, action, learning_profile)
    return local_value_g3h(state, action, learning_profile) + max(
        local_value_g3h(successor, future_action, learning_profile)
        for future_action in G3A_ASSIGNMENTS
    )
