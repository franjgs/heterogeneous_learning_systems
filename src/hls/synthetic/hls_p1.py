"""Small exact MIS-v2 pilot comparing fixed, reactive and anticipatory rules.

This is a bounded experiment module, not a change to the canonical N×K
execution path. Productive effort is the MIS-v2 exposure and consumes the
same constrained resource; there is no separate teaching/development action.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from math import isclose
from typing import Callable

from ..hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from ..hls_lab_nk_production import productive_outputs_nk
from ..hls_lab_nk_geometry import ProductiveAllocationNK

Competence = tuple[tuple[float, ...], ...]
Task = str
Action = ProductiveAllocationNK


@dataclass(frozen=True)
class P1Scenario:
    scenario_id: str
    initial_competence: Competence
    eta: tuple[tuple[float, ...], ...]
    requirements: tuple[tuple[float, ...], ...]
    probabilities_by_period: tuple[tuple[float, ...], ...]
    effort_choices: tuple[tuple[float, ...], ...]
    individual_budget: float
    collective_budget: float
    task_weights: tuple[float, ...]
    learning_enabled: bool = True

    def __post_init__(self) -> None:
        h = len(self.probabilities_by_period)
        if not self.scenario_id or h < 1:
            raise ValueError("scenario requires an id and positive horizon")
        n = len(self.initial_competence)
        k = len(self.requirements[0]) if self.requirements else 0
        if (not n or not k or any(len(row) != k for row in self.initial_competence)
                or len(self.eta) != n or any(len(row) != k for row in self.eta)
                or len(self.requirements) != 2 or any(len(row) != k for row in self.requirements)
                or any(len(choice) != k for choice in self.effort_choices)
                or len(self.task_weights) != k):
            raise ValueError("inconsistent agent/task/skill dimensions")
        if any(value <= 0 for row in self.requirements for value in row):
            raise ValueError("all task skill requirements must be positive")
        if any(len(row) != 2 or any(value < 0 for value in row)
               or not isclose(sum(row), 1.0, abs_tol=1e-12) for row in self.probabilities_by_period):
            raise ValueError("each period must define a two-task probability distribution")
        if any(value < 0 for choice in self.effort_choices for value in choice):
            raise ValueError("effort choices must be non-negative")
        if (any(value < 0 for value in self.task_weights)
                or not isclose(sum(self.task_weights), 1.0, abs_tol=1e-12)):
            raise ValueError("task weights must be non-negative and sum to one")
        if self.individual_budget <= 0 or self.collective_budget <= 0:
            raise ValueError("resource budgets must be positive")
        if not isinstance(self.learning_enabled, bool):
            raise ValueError("learning_enabled must be a boolean")
        LearningProfileNK(self.eta).validate_dimensions(n, k)

    @property
    def horizon(self) -> int:
        return len(self.probabilities_by_period)

    @property
    def tasks(self) -> tuple[Task, Task]:
        return ("x", "y")

    @property
    def action_catalog(self) -> tuple[Action, ...]:
        n = len(self.initial_competence)
        all_agent_allocations = tuple(product(self.effort_choices, repeat=n))
        actions = tuple(
            tuple(tuple(float(row[k]) for k in range(len(self.task_weights))) for row in rows)
            for rows in all_agent_allocations
            if all(sum(row) <= self.individual_budget + 1e-12 for row in rows)
            and sum(sum(row) for row in rows) <= self.collective_budget + 1e-12
        )
        return actions

    def task_index(self, task: Task) -> int:
        if task not in self.tasks:
            raise ValueError(f"unknown task {task!r}")
        return self.tasks.index(task)


@dataclass(frozen=True)
class Policy:
    policy_id: str
    action_for: Callable[[int, Task, Competence], int]
    fixed_mapping: tuple[int, int] | None = None


def default_scenarios() -> tuple[P1Scenario, ...]:
    """The bounded, preregistered stationary and distribution-shift cases."""
    efforts = ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5),
               (1.0, 0.0), (0.0, 1.0), (0.5, 0.5))
    initial = ((0.85, 0.15), (0.20, 0.20))
    eta = ((0.15, 0.15), (0.25, 0.25))
    requirements = ((0.65, 0.12), (0.12, 0.65))
    return (
        P1Scenario("stationary", initial, eta, requirements,
                    ((0.5, 0.5),) * 4, efforts, 1.0, 2.0, (0.5, 0.5)),
        P1Scenario("changing", initial, eta, requirements,
                    ((0.8, 0.2), (0.8, 0.2), (0.2, 0.8), (0.2, 0.8)),
                    efforts, 1.0, 2.0, (0.5, 0.5)),
    )


def task_performance(scenario: P1Scenario, competence: Competence,
                     action: Action, task: Task) -> tuple[float, bool, tuple[float, ...]]:
    """Weighted capped requirement fulfilment; success is separately reported."""
    outputs = productive_outputs_nk(competence, action)
    requirements = scenario.requirements[scenario.task_index(task)]
    score = sum(weight * min(output / req, 1.0)
                for weight, output, req in zip(scenario.task_weights, outputs, requirements))
    success = all(output + 1e-12 >= req for output, req in zip(outputs, requirements))
    return score, success, outputs


def next_competence(scenario: P1Scenario, competence: Competence,
                    action: Action) -> Competence:
    return mis_v2_transition_nk(
        competence, action, LearningProfileNK(scenario.eta),
        enabled=scenario.learning_enabled,
    )


def demand_paths(scenario: P1Scenario):
    """Return every finite demand path with its exact exogenous probability."""
    paths = [((), 1.0)]
    for probabilities in scenario.probabilities_by_period:
        paths = [(path + (task,), probability * probabilities[index])
                 for path, probability in paths
                 for index, task in enumerate(scenario.tasks)
                 if probabilities[index] > 0]
    return tuple(paths)


def _expected_fixed_value(scenario: P1Scenario, mapping: tuple[int, int],
                          actions: tuple[Action, ...]) -> float:
    @lru_cache(maxsize=None)
    def value(t: int, competence: Competence) -> float:
        if t == scenario.horizon:
            return 0.0
        total = 0.0
        for task_index, probability in enumerate(scenario.probabilities_by_period[t]):
            if probability == 0:
                continue
            action = actions[mapping[task_index]]
            score, _, _ = task_performance(scenario, competence, action,
                                            scenario.tasks[task_index])
            total += probability * (score + value(t + 1, next_competence(scenario, competence, action)))
        return total
    return value(0, scenario.initial_competence)


def solve_fixed_opt(scenario: P1Scenario) -> tuple[tuple[int, int], float, int]:
    """Globally enumerate the stationary task→action class."""
    actions = scenario.action_catalog
    if not actions:
        raise ValueError("empty feasible action catalog")
    best_map: tuple[int, int] | None = None
    best_value = float("-inf")
    for mapping in product(range(len(actions)), repeat=2):
        value = _expected_fixed_value(scenario, mapping, actions)
        if value > best_value + 1e-12:
            best_map, best_value = mapping, value
    assert best_map is not None
    return best_map, best_value, len(actions) ** 2


def solve_hls_anticipatory(scenario: P1Scenario):
    """Exact nonclairvoyant finite-horizon DP over demand distributions."""
    actions = scenario.action_catalog
    explored = 0

    @lru_cache(maxsize=None)
    def value(t: int, task_index: int, competence: Competence) -> float:
        nonlocal explored
        explored += 1
        if t == scenario.horizon:
            return 0.0
        task = scenario.tasks[task_index]
        best = float("-inf")
        for action in actions:
            score, _, _ = task_performance(scenario, competence, action, task)
            after = next_competence(scenario, competence, action)
            continuation = 0.0
            if t + 1 < scenario.horizon:
                for next_index, probability in enumerate(scenario.probabilities_by_period[t + 1]):
                    if probability:
                        continuation += probability * value(t + 1, next_index, after)
            best = max(best, score + continuation)
        return best

    def policy_action(t: int, task: Task, competence: Competence) -> int:
        if t == scenario.horizon - 1:
            return max(range(len(actions)), key=lambda i: task_performance(
                scenario, competence, actions[i], task)[0])
        task_index = scenario.task_index(task)
        values = []
        for action in actions:
            score, _, _ = task_performance(scenario, competence, action, task)
            after = next_competence(scenario, competence, action)
            continuation = sum(
                probability * value(t + 1, next_index, after)
                for next_index, probability in enumerate(scenario.probabilities_by_period[t + 1])
                if probability
            )
            values.append(score + continuation)
        return max(range(len(values)), key=lambda i: values[i])

    expected = sum(
        probability * value(0, task_index, scenario.initial_competence)
        for task_index, probability in enumerate(scenario.probabilities_by_period[0])
        if probability
    )
    return Policy("HLS_ANTICIPATORY", policy_action), expected, explored


def solve_reactive(scenario: P1Scenario) -> Policy:
    actions = scenario.action_catalog

    def choose(t: int, task: Task, competence: Competence) -> int:
        del t
        return max(range(len(actions)), key=lambda i: task_performance(
            scenario, competence, actions[i], task)[0])
    return Policy("REACTIVE", choose)


def build_policies(scenario: P1Scenario):
    actions = scenario.action_catalog
    mapping, fixed_value, fixed_candidates = solve_fixed_opt(scenario)
    fixed = Policy("FIXED_OPT", lambda t, task, competence:
                   mapping[scenario.task_index(task)], mapping)
    reactive = solve_reactive(scenario)
    anticipatory, hls_value, states = solve_hls_anticipatory(scenario)
    return actions, {
        fixed.policy_id: fixed,
        reactive.policy_id: reactive,
        anticipatory.policy_id: anticipatory,
    }, {"fixed_expected_value": fixed_value,
        "fixed_policy_candidates": fixed_candidates,
        "fixed_mapping": mapping,
        "anticipatory_expected_value": hls_value,
        "anticipatory_states_explored": states}


def run_path(scenario: P1Scenario, policy: Policy, actions: tuple[Action, ...],
             path: tuple[Task, ...], probability: float) -> dict:
    competence = scenario.initial_competence
    records = []
    for t, task in enumerate(path):
        action_index = policy.action_for(t, task, competence)
        action = actions[action_index]
        score, success, outputs = task_performance(scenario, competence, action, task)
        after = next_competence(scenario, competence, action)
        records.append({
            "period": t, "task": task, "action_index": action_index,
            "allocation": action, "outputs": outputs,
            "requirements": scenario.requirements[scenario.task_index(task)],
            "performance_score": score, "functional_success": success,
            "competence_before": competence, "competence_after": after,
            "mis_exposure": action,
            "resource_used": sum(sum(row) for row in action),
            "development_resource_cost": 0.0,
        })
        competence = after
    return {
        "policy_id": policy.policy_id, "demand_path": path,
        "path_probability": probability,
        "cumulative_functional_performance": sum(row["performance_score"] for row in records),
        "success_periods": sum(row["functional_success"] for row in records),
        "development_exposure": sum(row["resource_used"] for row in records),
        "resource_consumption": sum(row["resource_used"] for row in records),
        "final_competence": competence, "trace": records,
    }


def evaluate_scenario(scenario: P1Scenario) -> dict:
    actions, policies, solution = build_policies(scenario)
    paths = demand_paths(scenario)
    episodes = [run_path(scenario, policy, actions, path, probability)
                for path, probability in paths for policy in policies.values()]
    summaries = {}
    for policy_id in policies:
        rows = [row for row in episodes if row["policy_id"] == policy_id]
        expected = sum(row["path_probability"] * row["cumulative_functional_performance"]
                       for row in rows)
        expected_success = sum(row["path_probability"] * row["success_periods"]
                               for row in rows) / scenario.horizon
        summaries[policy_id] = {
            "expected_cumulative_functional_performance": expected,
            "expected_success_rate": expected_success,
            "expected_development_exposure": sum(
                row["path_probability"] * row["development_exposure"] for row in rows),
            "expected_resource_consumption": sum(
                row["path_probability"] * row["resource_consumption"] for row in rows),
        }
    return {
        "scenario_id": scenario.scenario_id,
        "horizon": scenario.horizon,
        "task_probabilities_by_period": scenario.probabilities_by_period,
        "initial_competence": scenario.initial_competence,
        "eta": scenario.eta,
        "learning_enabled": scenario.learning_enabled,
        "requirements": dict(zip(scenario.tasks, scenario.requirements)),
        "effort_choices": scenario.effort_choices,
        "individual_budget": scenario.individual_budget,
        "collective_budget": scenario.collective_budget,
        "task_weights": scenario.task_weights,
        "feasible_action_count": len(actions),
        "policy_solution": solution,
        "policy_summaries": summaries,
        "exact_path_count": len(paths),
        "paired_episodes": episodes,
    }
