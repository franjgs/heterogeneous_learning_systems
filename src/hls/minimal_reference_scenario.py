"""Deterministic implementation of the documented minimal HLS reference scenario.

This is deliberately not a G0 extension.  It represents exactly two workers,
two task/competence types, two periods, and the two joint assignments declared
in ``HLS_MINIMAL_REFERENCE_SCENARIO.md``.  Learning by doing is a direct
consequence of the period-0 allocation; there is no development action.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from math import isfinite
from typing import Literal


EXACT_TOL = 32.0 * 2.220446049250313e-16
State = tuple[tuple[float, float], tuple[float, float]]
Demand = tuple[float, float]
Action = Literal["E", "D"]


class LearningRule(str, Enum):
    """The only period-0 learning-by-doing realizations used by this scenario."""

    NONE = "none"
    DIMINISHING = "diminishing"
    HOMOGENEOUS_LINEAR = "homogeneous_linear"


# These exhaust the one-to-one assignments only in this 2-worker x 2-task
# reference instance.  They are not an HLS-wide action-space restriction.
ASSIGNMENTS: dict[Action, tuple[int, int]] = {
    "E": (0, 1),  # w1 -> A, w2 -> B
    "D": (1, 0),  # w1 -> B, w2 -> A
}


def _validate_state(state: State) -> None:
    if len(state) != 2 or any(len(row) != 2 for row in state):
        raise ValueError("the minimal reference scenario requires a 2x2 state")
    if not all(isfinite(value) and 0.0 <= value <= 1.0 for row in state for value in row):
        raise ValueError("competence values must be finite and lie in [0, 1]")


def _validate_demand(demand: Demand) -> None:
    if len(demand) != 2 or not all(isfinite(value) and value >= 0.0 for value in demand):
        raise ValueError("demand must contain two finite non-negative weights")
    if abs(sum(demand) - 1.0) > EXACT_TOL:
        raise ValueError("demand weights must sum to one")


@dataclass(frozen=True)
class MinimalReferenceScenario:
    """One policy-neutral 2-worker x 2-task x 2-period world.

    ``learning_scale`` belongs to the common world transition, never to an
    action or policy.  For each worker's actually assigned task, the
    diminishing rule applies ``s + q(1-s)^2``, with saturation at one.  The
    common law makes the value of the B opportunity recipient-dependent in the
    reference parameters; it is not a general HLS learning law.
    """

    state_0: State
    demand_0: Demand
    demand_1: Demand
    beta: float
    learning_rule: LearningRule = LearningRule.NONE
    learning_scale: float = 0.0

    def __post_init__(self) -> None:
        _validate_state(self.state_0)
        _validate_demand(self.demand_0)
        _validate_demand(self.demand_1)
        if not isinstance(self.learning_rule, LearningRule):
            raise ValueError("learning_rule must be a LearningRule")
        if not isfinite(self.beta) or self.beta < 0.0:
            raise ValueError("beta must be finite and non-negative")
        if not isfinite(self.learning_scale) or self.learning_scale < 0.0:
            raise ValueError("learning_scale must be finite and non-negative")

    def with_beta(self, beta: float) -> "MinimalReferenceScenario":
        """Return the same world physics evaluated with another future weight."""
        return replace(self, beta=beta)

    def present_reward(self, action: Action) -> float:
        """Return the demand-weighted period-0 reward of a joint assignment."""
        return assignment_reward(self.state_0, action, self.demand_0)

    def transition(self, action: Action) -> State:
        """Return ``S_1 = F(S_0, a_0)`` from assigned-task experience.

        Capacity is encoded by the two bijective joint assignments: each worker
        serves exactly one type in each period.  Thus each competence update
        belongs to the worker who actually executes that type; the B recipient
        is determined by the organization/use action itself.
        """
        if action not in ASSIGNMENTS:
            raise ValueError("action must be E or D")
        if self.learning_rule is LearningRule.NONE:
            return self.state_0

        rows = [list(row) for row in self.state_0]
        for worker, task in enumerate(ASSIGNMENTS[action]):
            current = rows[worker][task]
            if self.learning_rule is LearningRule.DIMINISHING:
                updated = current + self.learning_scale * (1.0 - current) ** 2
            elif self.learning_rule is LearningRule.HOMOGENEOUS_LINEAR:
                updated = current + self.learning_scale
            else:  # Defensive guard for future invalid enum-like input.
                raise ValueError("unknown learning rule")
            rows[worker][task] = min(1.0, updated)
        return tuple(tuple(row) for row in rows)  # type: ignore[return-value]

    def terminal_value(self, state: State) -> float:
        """Optimize period-1 organization over this instance's two assignments."""
        _validate_state(state)
        return max(assignment_reward(state, action, self.demand_1) for action in ASSIGNMENTS)

    def evaluate(self) -> "ScenarioEvaluation":
        """Evaluate both actions without any policy-specific world physics."""
        state_e = self.transition("E")
        state_d = self.transition("D")
        reward_e = self.present_reward("E")
        reward_d = self.present_reward("D")
        value_e = self.terminal_value(state_e)
        value_d = self.terminal_value(state_d)
        total_e = reward_e + self.beta * value_e
        total_d = reward_d + self.beta * value_d
        loss = reward_e - reward_d
        gain = value_d - value_e
        return ScenarioEvaluation(
            state_e=state_e,
            state_d=state_d,
            reward_e=reward_e,
            reward_d=reward_d,
            value_e=value_e,
            value_d=value_d,
            total_e=total_e,
            total_d=total_d,
            loss=loss,
            gain=gain,
        )


def assignment_reward(state: State, action: Action, demand: Demand) -> float:
    """Evaluate one capacity-feasible joint assignment against a demand vector."""
    _validate_state(state)
    _validate_demand(demand)
    try:
        assigned_types = ASSIGNMENTS[action]
    except KeyError as error:
        raise ValueError("action must be E or D") from error
    return sum(demand[task] * state[worker][task] for worker, task in enumerate(assigned_types))


@dataclass(frozen=True)
class ScenarioEvaluation:
    """All quantities used by the documented T6 instance."""

    state_e: State
    state_d: State
    reward_e: float
    reward_d: float
    value_e: float
    value_d: float
    total_e: float
    total_d: float
    loss: float
    gain: float

    @property
    def total_difference(self) -> float:
        """Return ``J(D)-J(E)``."""
        return self.total_d - self.total_e

    def optimal_actions(self) -> tuple[Action, ...]:
        """Return all maximizing actions; ties deliberately retain both actions."""
        maximum = max(self.total_e, self.total_d)
        actions: list[Action] = []
        if abs(self.total_e - maximum) <= EXACT_TOL:
            actions.append("E")
        if abs(self.total_d - maximum) <= EXACT_TOL:
            actions.append("D")
        return tuple(actions)


def identity_residual(scenario: MinimalReferenceScenario) -> float:
    """Numerically check ``J(D)-J(E) = -L + beta G`` at machine precision."""
    evaluation = scenario.evaluate()
    return evaluation.total_difference - (-evaluation.loss + scenario.beta * evaluation.gain)


REFERENCE_STATE: State = ((0.65, 0.40), (0.70, 0.50))
REFERENCE_DEMAND_0: Demand = (0.50, 0.50)
REFERENCE_DEMAND_1: Demand = (0.00, 1.00)


def reference_configurations() -> dict[str, MinimalReferenceScenario]:
    """Return the deterministic S0--S3 and negative-control configurations.

    The boundary beta is calculated from simulated ``L`` and ``G`` of the
    common diminishing-return world; ``G`` is never an input parameter.
    """
    common = MinimalReferenceScenario(
        state_0=REFERENCE_STATE,
        demand_0=REFERENCE_DEMAND_0,
        demand_1=REFERENCE_DEMAND_1,
        beta=0.25,
        learning_rule=LearningRule.DIMINISHING,
        learning_scale=1.5,
    )
    common_evaluation = common.evaluate()
    if common_evaluation.gain <= 0.0:
        raise RuntimeError("the reference development world must have positive simulated G")
    boundary_beta = common_evaluation.loss / common_evaluation.gain
    return {
        "S0_static": MinimalReferenceScenario(
            state_0=REFERENCE_STATE,
            demand_0=REFERENCE_DEMAND_0,
            demand_1=REFERENCE_DEMAND_0,
            beta=0.25,
        ),
        "S1_adaptive_fixed": MinimalReferenceScenario(
            state_0=REFERENCE_STATE,
            demand_0=REFERENCE_DEMAND_0,
            demand_1=REFERENCE_DEMAND_1,
            beta=0.25,
        ),
        "S2_decision_equivalent": common,
        "boundary": common.with_beta(boundary_beta),
        "S3_decision_relevant": common.with_beta(0.50),
        "negative_homogeneous_linear": MinimalReferenceScenario(
            state_0=((0.75, 0.90), (0.70, 0.95)),
            demand_0=REFERENCE_DEMAND_0,
            demand_1=REFERENCE_DEMAND_1,
            beta=0.50,
            learning_rule=LearningRule.HOMOGENEOUS_LINEAR,
            learning_scale=0.20,
        ),
    }
