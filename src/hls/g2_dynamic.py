"""Exact 2-agent/2-task/2-period dynamic ground truth for G2.

G2 realizes only the D0, D1, and D2 controls specified in
``docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md``.  It is deliberately separate
from G0: this is the minimal analytical T4--T6 reference, not an extension of
the RQ0 synthetic framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping


EXACT_TOL = 1e-12
POLICIES = ("11", "12", "21", "22")
State = tuple[tuple[float, float], tuple[float, float]]
Outcome = tuple[float, float]


def _validate_state(state: State) -> None:
    if len(state) != 2 or any(len(row) != 2 for row in state):
        raise ValueError("G2 requires a 2-agent/2-task competence state")
    if not all(isfinite(value) for row in state for value in row):
        raise ValueError("competence values must be finite")


def _validate_probability(p: float) -> None:
    if not isfinite(p) or not 0.0 <= p <= 1.0:
        raise ValueError("demand probability must lie in [0, 1]")


def _validate_action(action: int) -> None:
    if action not in (1, 2):
        raise ValueError("G2 action must be agent 1 or 2")


def _validate_learning_rates(learning_rates: tuple[float, float]) -> None:
    if len(learning_rates) != 2 or not all(isfinite(value) for value in learning_rates):
        raise ValueError("G2 requires two finite learning rates")


def transition(state: State, action: int, learning_rates: tuple[float, float]) -> State:
    """Apply G2 deterministic learning by doing for the period-0 q1 action.

    Only the q1 competence of the selected agent changes; competence saturates
    at one exactly as specified by G2.
    """
    _validate_state(state)
    _validate_action(action)
    _validate_learning_rates(learning_rates)
    rows = [list(row) for row in state]
    learner = action - 1
    rows[learner][0] = min(1.0, rows[learner][0] + learning_rates[learner])
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def present_reward(state: State, action: int) -> float:
    """Return R_0(a_0)=s_{a_0,1,0}."""
    _validate_state(state)
    _validate_action(action)
    return state[action - 1][0]


def attainable_outcomes(state: State) -> Mapping[str, Outcome]:
    """Return the four terminal task-dependent routing outcomes."""
    _validate_state(state)
    return {
        "11": (state[0][0], state[0][1]),
        "12": (state[0][0], state[1][1]),
        "21": (state[1][0], state[0][1]),
        "22": (state[1][0], state[1][1]),
    }


def efficient_frontier(outcomes: Mapping[str, Outcome]) -> tuple[Outcome, ...]:
    """Return non-dominated outcomes, deduplicated and lexicographically sorted."""
    unique = sorted(set(outcomes.values()))
    frontier = []
    for candidate in unique:
        dominated = any(
            other != candidate
            and other[0] >= candidate[0] - EXACT_TOL
            and other[1] >= candidate[1] - EXACT_TOL
            and (other[0] > candidate[0] + EXACT_TOL or other[1] > candidate[1] + EXACT_TOL)
            for other in unique
        )
        if not dominated:
            frontier.append(candidate)
    return tuple(frontier)


def terminal_value(frontier: tuple[Outcome, ...], p: float) -> float:
    """Return V(S;p) over the supplied efficient terminal frontier."""
    _validate_probability(p)
    if not frontier:
        raise ValueError("a terminal frontier cannot be empty")
    return max(p * q1 + (1.0 - p) * q2 for q1, q2 in frontier)


@dataclass(frozen=True)
class ActionEvaluation:
    """Complete period-0 action and induced period-1 terminal evaluation."""

    action: int
    present_reward: float
    future_state: State
    attainable: Mapping[str, Outcome]
    frontier: tuple[Outcome, ...]
    terminal_value: float


@dataclass(frozen=True)
class G2Evaluation:
    """Comparison of actions 1 and 2 at one future-demand mixture."""

    p: float
    action_1: ActionEvaluation
    action_2: ActionEvaluation
    delta_r: float
    delta_dev: float
    delta_j: float


@dataclass(frozen=True)
class G2Scenario:
    """A fixed D0/D1/D2 state and learning-rate specification."""

    name: str
    state_0: State
    learning_rates: tuple[float, float]

    def __post_init__(self) -> None:
        _validate_state(self.state_0)
        _validate_learning_rates(self.learning_rates)

    def evaluate_action(self, action: int, p: float) -> ActionEvaluation:
        future_state = transition(self.state_0, action, self.learning_rates)
        attainable = attainable_outcomes(future_state)
        frontier = efficient_frontier(attainable)
        return ActionEvaluation(
            action=action,
            present_reward=present_reward(self.state_0, action),
            future_state=future_state,
            attainable=attainable,
            frontier=frontier,
            terminal_value=terminal_value(frontier, p),
        )

    def evaluate(self, p: float) -> G2Evaluation:
        _validate_probability(p)
        action_1 = self.evaluate_action(1, p)
        action_2 = self.evaluate_action(2, p)
        delta_r = action_1.present_reward - action_2.present_reward
        delta_dev = action_1.terminal_value - action_2.terminal_value
        return G2Evaluation(
            p=p,
            action_1=action_1,
            action_2=action_2,
            delta_r=delta_r,
            delta_dev=delta_dev,
            delta_j=delta_r + delta_dev,
        )


# D0 accepts arbitrary S0 in theory.  This fixed D2-state representative makes
# its no-evolution identity executable without adding a fourth scenario.
D0 = G2Scenario(
    name="D0_no_evolution",
    state_0=((0.7, 0.8), (0.8, 0.6)),
    learning_rates=(0.0, 0.0),
)
D1 = G2Scenario(
    name="D1_learning_frontier_null",
    state_0=((0.4, 0.8), (0.8, 0.4)),
    learning_rates=(0.1, 0.0),
)
D2 = G2Scenario(
    name="D2_capability_value_coupling",
    state_0=((0.7, 0.8), (0.8, 0.6)),
    learning_rates=(0.3, 0.0),
)
CANONICAL_SCENARIOS = {scenario.name: scenario for scenario in (D0, D1, D2)}


def d2_closed_form(p: float) -> tuple[float, float, float]:
    """Return the documented ``(Delta_R, Delta_dev, Delta_J)`` identities."""
    _validate_probability(p)
    return (-0.1, 0.2 * p, -0.1 + 0.2 * p)


def d2_regime(p: float) -> tuple[str, str]:
    """Return documented T5 and T6 regime labels for D2 at demand mixture ``p``."""
    _validate_probability(p)
    if abs(p) <= EXACT_TOL:
        t5 = "T5_null_equal_future_value"
    else:
        t5 = "T5_positive_development_value"

    if abs(p) <= EXACT_TOL:
        t6 = "T6_static_sufficiency"
    elif p < 0.5 - EXACT_TOL:
        t6 = "T6_tradeoff_without_reversal"
    elif abs(p - 0.5) <= EXACT_TOL:
        t6 = "T6_intertemporal_indifference"
    else:
        t6 = "T6_decision_reversal"
    return t5, t6


def demand_sweep(scenario: G2Scenario, points: int = 101) -> tuple[G2Evaluation, ...]:
    """Evaluate an inclusive deterministic future-demand sweep on [0, 1]."""
    if points < 2:
        raise ValueError("a demand sweep needs at least two points")
    return tuple(scenario.evaluate(index / (points - 1)) for index in range(points))
