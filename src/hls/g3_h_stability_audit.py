"""Focused audit of condition C within the fixed G3-H evaluator.

Condition C is deliberately the strong all-optimizer condition used by the
previous structural autopsy.  It is not the weaker existential condition.
"""

from __future__ import annotations

from dataclasses import dataclass

from .g3_h_organizational_value import G3HLearningProfile, transition_g3h
from .g3_h_regime_map import G3HPointEvaluation, REGIME_TOL
from .g3_organizational_value import G3A_ASSIGNMENTS, G3aAction, reward_g3a, value_g3a_direct


@dataclass(frozen=True)
class StabilityCAudit:
    """All-optimizer first-successor stability and its exact raw margin."""

    holds: bool
    margin: float
    witness_optimizer: G3aAction
    witness_present_action: G3aAction
    witness_alternative: G3aAction


def condition_c(evaluation: G3HPointEvaluation, *, tolerance: float = REGIME_TOL) -> StabilityCAudit:
    """Evaluate C: every current USE optimizer remains optimal after every F(S,x)."""
    if tolerance < 0.0:
        raise ValueError("tolerance must be non-negative")
    margin = float("inf")
    witness: tuple[G3aAction, G3aAction, G3aAction] | None = None
    for present in evaluation.actions:
        for optimizer in evaluation.optimal_use:
            for alternative in G3A_ASSIGNMENTS:
                difference = reward_g3a(present.successor, optimizer) - reward_g3a(present.successor, alternative)
                if difference < margin:
                    margin = difference
                    witness = (optimizer, present.action, alternative)
    assert witness is not None
    return StabilityCAudit(
        holds=margin >= -tolerance,
        margin=margin,
        witness_optimizer=witness[0],
        witness_present_action=witness[1],
        witness_alternative=witness[2],
    )


def continuation_head(
    state: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    present_action: G3aAction,
    profile: G3HLearningProfile,
) -> float:
    """H(x)=max_y[R(F(S,x),y)+V(F(F(S,x),y))], used only for the proof audit."""
    successor = transition_g3h(state, present_action, profile)
    return max(
        reward_g3a(successor, future) + value_g3a_direct(transition_g3h(successor, future, profile))
        for future in G3A_ASSIGNMENTS
    )


def cancelled_dynamic_value(
    state: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    present_action: G3aAction,
    profile: G3HLearningProfile,
) -> float:
    """Independent expansion Q=R(S,x)-V(S)+H(x)."""
    return reward_g3a(state, present_action) - value_g3a_direct(state) + continuation_head(state, present_action, profile)
