"""Exact finite two-agent, two-task, two-period competence-development model.

This model separates action-induced state change, efficient collective outcomes
and future value. It is one analytical construction, not a universal dynamic
HLS framework.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

TOLERANCE = 1e-12
CompetenceMatrix = tuple[tuple[float, float], tuple[float, float]]
TaskPerformancePair = tuple[float, float]
ASSIGNMENTS = (
    "agent_1_for_both_tasks",
    "agent_1_task_1__agent_2_task_2",
    "agent_2_task_1__agent_1_task_2",
    "agent_2_for_both_tasks",
)


def _validate_matrix(matrix: CompetenceMatrix) -> None:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("this finite model requires two agents and two tasks")
    if not all(isfinite(value) for row in matrix for value in row):
        raise ValueError("competence entries must be finite")


def _validate_probability(task_1_probability: float) -> None:
    if not isfinite(task_1_probability) or not 0 <= task_1_probability <= 1:
        raise ValueError("future task-1 probability must lie in [0, 1]")


def _validate_agent(agent_id: int) -> None:
    if agent_id not in (1, 2):
        raise ValueError("selected agent must be 1 or 2")


def apply_learning_by_doing(
    initial_competence: CompetenceMatrix,
    selected_agent: int,
    competence_increments: tuple[float, float],
) -> CompetenceMatrix:
    """Increase the selected agent's task-1 competence, capped at one."""
    _validate_matrix(initial_competence)
    _validate_agent(selected_agent)
    if len(competence_increments) != 2 or not all(isfinite(x) for x in competence_increments):
        raise ValueError("one finite learning increment is required per agent")
    updated = [list(row) for row in initial_competence]
    row = selected_agent - 1
    updated[row][0] = min(1.0, updated[row][0] + competence_increments[row])
    return tuple(tuple(row) for row in updated)  # type: ignore[return-value]


def current_task_reward(matrix: CompetenceMatrix, selected_agent: int) -> float:
    """Use task-1 competence as current-period reward in this model."""
    _validate_matrix(matrix)
    _validate_agent(selected_agent)
    return matrix[selected_agent - 1][0]


def terminal_assignment_outcomes(matrix: CompetenceMatrix) -> Mapping[str, TaskPerformancePair]:
    """Return terminal task-performance pairs for all four assignments."""
    _validate_matrix(matrix)
    return {
        "agent_1_for_both_tasks": (matrix[0][0], matrix[0][1]),
        "agent_1_task_1__agent_2_task_2": (matrix[0][0], matrix[1][1]),
        "agent_2_task_1__agent_1_task_2": (matrix[1][0], matrix[0][1]),
        "agent_2_for_both_tasks": (matrix[1][0], matrix[1][1]),
    }


def nondominated_outcomes(outcomes: Mapping[str, TaskPerformancePair]) -> tuple[TaskPerformancePair, ...]:
    """Deduplicate and retain Pareto-nondominated two-task outcomes."""
    unique = sorted(set(outcomes.values()))
    return tuple(
        candidate for candidate in unique
        if not any(
            other != candidate
            and other[0] >= candidate[0] - TOLERANCE
            and other[1] >= candidate[1] - TOLERANCE
            and (other[0] > candidate[0] + TOLERANCE or other[1] > candidate[1] + TOLERANCE)
            for other in unique
        )
    )


def demand_weighted_future_performance(
    efficient_outcomes: tuple[TaskPerformancePair, ...], task_1_probability: float
) -> float:
    """Maximize expected terminal task performance under a task mixture."""
    _validate_probability(task_1_probability)
    if not efficient_outcomes:
        raise ValueError("at least one efficient outcome is required")
    return max(task_1_probability * first + (1 - task_1_probability) * second
               for first, second in efficient_outcomes)


@dataclass(frozen=True)
class AgentChoiceEvaluation:
    selected_agent: int
    current_reward: float
    competence_after_action: CompetenceMatrix
    attainable_terminal_outcomes: Mapping[str, TaskPerformancePair]
    efficient_terminal_outcomes: tuple[TaskPerformancePair, ...]
    future_performance: float


@dataclass(frozen=True)
class DevelopmentComparison:
    future_task_1_probability: float
    agent_1_choice: AgentChoiceEvaluation
    agent_2_choice: AgentChoiceEvaluation
    immediate_value_difference: float
    future_development_value_difference: float
    total_value_difference: float


@dataclass(frozen=True)
class TwoPeriodCompetenceModel:
    """A fixed initial competence matrix and action-induced increments."""
    name: str
    initial_competence: CompetenceMatrix
    competence_increments: tuple[float, float]

    def __post_init__(self) -> None:
        _validate_matrix(self.initial_competence)
        if len(self.competence_increments) != 2 or not all(isfinite(x) for x in self.competence_increments):
            raise ValueError("one finite learning increment is required per agent")

    def evaluate_agent_choice(self, selected_agent: int, task_1_probability: float) -> AgentChoiceEvaluation:
        post_action = apply_learning_by_doing(
            self.initial_competence, selected_agent, self.competence_increments
        )
        outcomes = terminal_assignment_outcomes(post_action)
        frontier = nondominated_outcomes(outcomes)
        return AgentChoiceEvaluation(
            selected_agent=selected_agent,
            current_reward=current_task_reward(self.initial_competence, selected_agent),
            competence_after_action=post_action,
            attainable_terminal_outcomes=outcomes,
            efficient_terminal_outcomes=frontier,
            future_performance=demand_weighted_future_performance(frontier, task_1_probability),
        )

    def compare_choices(self, task_1_probability: float) -> DevelopmentComparison:
        _validate_probability(task_1_probability)
        first = self.evaluate_agent_choice(1, task_1_probability)
        second = self.evaluate_agent_choice(2, task_1_probability)
        immediate = first.current_reward - second.current_reward
        future = first.future_performance - second.future_performance
        return DevelopmentComparison(task_1_probability, first, second, immediate, future, immediate + future)


NO_LEARNING_CONTROL = TwoPeriodCompetenceModel(
    "no_learning_control", ((0.7, 0.8), (0.8, 0.6)), (0.0, 0.0)
)
FRONTIER_NULL_UNDER_LEARNING = TwoPeriodCompetenceModel(
    "frontier_null_under_learning", ((0.4, 0.8), (0.8, 0.4)), (0.1, 0.0)
)
DEVELOPMENT_VALUE_REVERSAL = TwoPeriodCompetenceModel(
    "development_value_reversal", ((0.7, 0.8), (0.8, 0.6)), (0.3, 0.0)
)
REFERENCE_DYNAMIC_CASES = {
    model.name: model for model in (NO_LEARNING_CONTROL, FRONTIER_NULL_UNDER_LEARNING, DEVELOPMENT_VALUE_REVERSAL)
}


def value_reversal_closed_form(task_1_probability: float) -> tuple[float, float, float]:
    """Return exact immediate, future and total differences for this instance."""
    _validate_probability(task_1_probability)
    return (-0.1, 0.2 * task_1_probability, -0.1 + 0.2 * task_1_probability)
