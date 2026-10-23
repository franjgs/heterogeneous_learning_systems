"""Small exact S4 instances using the canonical N×K MIS-v2 transition.

This module is deliberately limited to deterministic one-unit bipartite
assignment. It does not add a learning law or alter the general N×K runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from time import perf_counter
from typing import TypeAlias

from hls.hls_lab_nk_assignment import HungarianAssignmentOptimizerNK
from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
)
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk

Competence: TypeAlias = tuple[tuple[float, ...], ...]
Assignment: TypeAlias = tuple[tuple[int, int], ...]
Demand: TypeAlias = tuple[bool, ...]
IMMEDIATE_TOL = 1e-12


@dataclass(frozen=True)
class S4Case:
    name: str
    initial: Competence
    eta: tuple[tuple[float, ...], ...]
    demands: tuple[Demand, ...]

    def __post_init__(self) -> None:
        n, k = len(self.initial), len(self.initial[0])
        if not self.demands or any(len(row) != k for row in self.demands):
            raise ValueError("S4 demands must be a non-empty horizon × K sequence")
        LearningProfileNK(self.eta).validate_dimensions(n, k)


@dataclass(frozen=True)
class S4Period:
    period: int
    demand: Demand
    assignment: Assignment
    reward: float
    competence_before: Competence
    competence_after: Competence
    cumulative_exposure: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class S4PolicyResult:
    policy: str
    reward: float
    periods: tuple[S4Period, ...]


@dataclass(frozen=True)
class S4CaseResult:
    case: S4Case
    reactive: S4PolicyResult
    bellman: S4PolicyResult
    exhaustive: S4PolicyResult
    bellman_value: float
    exhaustive_value: float
    bellman_seconds: float
    exhaustive_seconds: float


@dataclass(frozen=True)
class S4ValidationResult:
    case: S4Case
    learning_enabled: bool
    reactive: S4PolicyResult
    best_myopic: S4PolicyResult
    bellman: S4PolicyResult
    exhaustive: S4PolicyResult
    exhaustive_best_myopic_value: float
    tie_counts: tuple[int, ...]
    bellman_strictly_suboptimal_periods: tuple[int, ...]


def _assignment_catalog(demand: Demand, n_agents: int) -> tuple[Assignment, ...]:
    """All partial one-to-one matchings using only currently demanded tasks."""
    k = len(demand)
    choices = tuple((-1, *(task for task in range(k) if demand[task]))
                    for _ in range(n_agents))
    actions = set()
    for selected in product(*choices):
        tasks = tuple(task for task in selected if task >= 0)
        if len(tasks) == len(set(tasks)):
            actions.add(tuple((agent, task) for agent, task in enumerate(selected) if task >= 0))
    return tuple(sorted(actions, key=lambda action: (len(action), action)))


def _allocation(assignment: Assignment, n: int, k: int) -> ProductiveAllocationNK:
    values = [[0.0] * k for _ in range(n)]
    for agent, task in assignment:
        values[agent][task] = 1.0
    return tuple(tuple(row) for row in values)


def _reward(state: Competence, assignment: Assignment) -> float:
    return sum(state[agent][task] for agent, task in assignment)


def _transition(
    state: Competence, assignment: Assignment, profile: LearningProfileNK,
    *, learning_enabled: bool = True,
) -> Competence:
    return mis_v2_transition_nk(
        state, _allocation(assignment, len(state), len(state[0])), profile,
        enabled=learning_enabled,
    )


def _simulate(
    case: S4Case, policy: str, assignments: tuple[Assignment, ...], *,
    learning_enabled: bool = True,
) -> S4PolicyResult:
    state = case.initial
    n, k = len(state), len(state[0])
    profile = LearningProfileNK(case.eta)
    exposures = [[0] * k for _ in range(n)]
    rows: list[S4Period] = []
    total = 0.0
    for period, (demand, assignment) in enumerate(zip(case.demands, assignments)):
        catalog = set(_assignment_catalog(demand, n))
        if assignment not in catalog:
            raise ValueError(f"infeasible assignment at period {period}: {assignment}")
        before = state
        reward = _reward(before, assignment)
        allocation = _allocation(assignment, n, k)
        state = mis_v2_transition_nk(before, allocation, profile, enabled=learning_enabled)
        for agent, task in assignment:
            exposures[agent][task] += 1
        total += reward
        rows.append(S4Period(period, demand, assignment, reward, before, state,
                             tuple(tuple(row) for row in exposures)))
    return S4PolicyResult(policy, total, tuple(rows))


def _reactive(case: S4Case, *, learning_enabled: bool = True) -> S4PolicyResult:
    """Exact immediate optimizer; solver's stable tie rule is retained."""
    n, k = len(case.initial), len(case.initial[0])
    organization = OrganizationConfigNK(
        tuple(f"agent-{i}" for i in range(n)), tuple(f"task-{j}" for j in range(k)),
        case.initial, (1.0,) * n, float(min(n, k)),
    )
    optimizer = HungarianAssignmentOptimizerNK()
    state = case.initial
    assignments = []
    for demand in case.demands:
        problem = ProblemSpecNK("S4", tuple(1.0 if available else 0.0 for available in demand),
                                float(min(n, k)))
        scores = tuple(tuple(state[i][j] if demand[j] else 0.0 for j in range(k))
                       for i in range(n))
        result = optimizer.optimize(scores, organization, problem, maximize=True)
        assignment = tuple(result.matches)
        if abs(result.objective_value - _reward(state, assignment)) > 1e-12:
            raise AssertionError("existing assignment solver and S4 reward disagree")
        assignments.append(assignment)
        state = _transition(state, assignment, LearningProfileNK(case.eta),
                            learning_enabled=learning_enabled)
    return _simulate(case, "REACTIVE_FIXED_TIEBREAK", tuple(assignments),
                     learning_enabled=learning_enabled)


def _bellman(
    case: S4Case, *, learning_enabled: bool = True,
) -> tuple[float, tuple[Assignment, ...]]:
    profile = LearningProfileNK(case.eta)
    n = len(case.initial)

    @lru_cache(maxsize=None)
    def value(period: int, state: Competence) -> tuple[float, tuple[Assignment, ...]]:
        if period == len(case.demands):
            return 0.0, ()
        best_value = float("-inf")
        best_path: tuple[Assignment, ...] = ()
        for assignment in _assignment_catalog(case.demands[period], n):
            next_state = _transition(state, assignment, profile,
                                     learning_enabled=learning_enabled)
            future, future_path = value(period + 1, next_state)
            candidate = _reward(state, assignment) + future
            if candidate > best_value + 1e-12:
                best_value, best_path = candidate, (assignment,) + future_path
        return best_value, best_path

    return value(0, case.initial)


def _exhaustive(
    case: S4Case, *, learning_enabled: bool = True, myopic_only: bool = False,
    tolerance: float = IMMEDIATE_TOL,
) -> tuple[float, tuple[Assignment, ...]]:
    """Independent sequence enumeration; deliberately does not call Bellman."""
    n = len(case.initial)
    # Rebuild every period's legal matchings from raw agent choices rather
    # than calling the Bellman action-catalog helper.
    catalogs = []
    for demand in case.demands:
        period_actions: list[Assignment] = []
        for choices in product((-1, *range(len(demand))), repeat=n):
            assigned = tuple(task for task in choices if task >= 0)
            if (len(assigned) == len(set(assigned))
                    and all(task < 0 or demand[task] for task in choices)):
                period_actions.append(tuple((agent, task) for agent, task in enumerate(choices)
                                            if task >= 0))
        catalogs.append(tuple(period_actions))
    best_reward = float("-inf")
    best_path: tuple[Assignment, ...] = ()
    for path in product(*catalogs):
        state = case.initial
        total = 0.0
        admissible = True
        for period, assignment in enumerate(path):
            if myopic_only:
                # Compute the immediate maximum directly from this exhaustive
                # enumerator's independently constructed period catalog.
                immediate_max = max(_reward(state, candidate)
                                    for candidate in catalogs[period])
                if _reward(state, assignment) < immediate_max - tolerance:
                    admissible = False
                    break
            total += _reward(state, assignment)
            state = _transition(state, assignment, LearningProfileNK(case.eta),
                                learning_enabled=learning_enabled)
        if not admissible:
            continue
        if total > best_reward + 1e-12:
            best_reward, best_path = total, tuple(path)
    return best_reward, best_path


def _best_myopic(
    case: S4Case, *, learning_enabled: bool = True,
    tolerance: float = IMMEDIATE_TOL,
) -> tuple[float, tuple[Assignment, ...]]:
    """Maximize continuation subject to immediate-optimal actions at every state."""
    profile = LearningProfileNK(case.eta)
    n = len(case.initial)

    @lru_cache(maxsize=None)
    def value(period: int, state: Competence) -> tuple[float, tuple[Assignment, ...]]:
        if period == len(case.demands):
            return 0.0, ()
        actions = _assignment_catalog(case.demands[period], n)
        immediate_max = max(_reward(state, action) for action in actions)
        allowed = tuple(action for action in actions
                        if _reward(state, action) >= immediate_max - tolerance)
        best_value = float("-inf")
        best_path: tuple[Assignment, ...] = ()
        for assignment in allowed:
            next_state = _transition(state, assignment, profile,
                                     learning_enabled=learning_enabled)
            future, future_path = value(period + 1, next_state)
            candidate = _reward(state, assignment) + future
            if candidate > best_value + 1e-12:
                best_value, best_path = candidate, (assignment,) + future_path
        return best_value, best_path

    return value(0, case.initial)


def _path_diagnostics(
    case: S4Case, path: tuple[Assignment, ...], *, learning_enabled: bool,
    tolerance: float = IMMEDIATE_TOL,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    state = case.initial
    profile = LearningProfileNK(case.eta)
    ties: list[int] = []
    suboptimal: list[int] = []
    for period, (demand, assignment) in enumerate(zip(case.demands, path)):
        actions = _assignment_catalog(demand, len(case.initial))
        values = tuple(_reward(state, action) for action in actions)
        maximum = max(values)
        ties.append(sum(abs(value - maximum) <= tolerance for value in values))
        if _reward(state, assignment) < maximum - tolerance:
            suboptimal.append(period)
        state = _transition(state, assignment, profile,
                             learning_enabled=learning_enabled)
    return tuple(ties), tuple(suboptimal)


def validate_case(
    case: S4Case, *, learning_enabled: bool = True,
    tolerance: float = IMMEDIATE_TOL,
) -> S4ValidationResult:
    """Compare fixed-tie myopia, best tie-aware myopia and unrestricted DP."""
    reactive = _reactive(case, learning_enabled=learning_enabled)
    best_myopic_value, best_myopic_path = _best_myopic(
        case, learning_enabled=learning_enabled, tolerance=tolerance,
    )
    bellman_value, bellman_path = _bellman(case, learning_enabled=learning_enabled)
    exhaustive_value, exhaustive_path = _exhaustive(
        case, learning_enabled=learning_enabled,
    )
    exhaustive_myopic_value, _ = _exhaustive(
        case, learning_enabled=learning_enabled, myopic_only=True,
        tolerance=tolerance,
    )
    if abs(bellman_value - exhaustive_value) > 1e-12:
        raise AssertionError("Bellman and global exhaustive values differ")
    if abs(best_myopic_value - exhaustive_myopic_value) > 1e-12:
        raise AssertionError("BEST-MYOPIC and restricted exhaustive values differ")
    if (bellman_value < best_myopic_value - 1e-12
            or best_myopic_value < reactive.reward - 1e-12):
        raise AssertionError("expected Bellman >= BEST-MYOPIC >= fixed-tie reactive")
    ties, suboptimal = _path_diagnostics(
        case, bellman_path, learning_enabled=learning_enabled, tolerance=tolerance,
    )
    return S4ValidationResult(
        case, learning_enabled, reactive,
        _simulate(case, "BEST_MYOPIC", best_myopic_path,
                  learning_enabled=learning_enabled),
        _simulate(case, "BELLMAN_EXACT", bellman_path,
                  learning_enabled=learning_enabled),
        _simulate(case, "EXHAUSTIVE_GLOBAL", exhaustive_path,
                  learning_enabled=learning_enabled),
        exhaustive_myopic_value, ties, suboptimal,
    )


def canonical_cases() -> tuple[S4Case, S4Case]:
    """Cases use the already-recorded P1 competence and MIS-v2 profiles.

    A is a one-period terminal control. B keeps the same initial state and
    rates, then changes only the predeclared deterministic demand sequence.
    """
    initial = ((0.525, 0.175), (0.525, 0.175))
    eta = ((0.15, 0.15), (0.25, 0.25))
    both = (True, True)
    task_x = (True, False)
    return (
        S4Case("A_no_future_return", initial, eta, (both,)),
        S4Case("B_future_x_demand", initial, eta, (both, task_x, task_x, task_x)),
    )


def investment_family() -> tuple[S4Case, ...]:
    """Short horizon family satisfying a transparent one-task condition.

    Only the horizon varies. Competence 0.525 is an existing HLS value;
    0.500 is a neutral initial value, while eta=0.15/0.25 are the previously
    used heterogeneous MIS-v2 rates. A is the currently better/slower learner.
    """
    initial = ((0.525, 0.175), (0.500, 0.175))
    eta = ((0.15, 0.15), (0.25, 0.25))
    task_x = (True, False)
    return tuple(
        S4Case(f"investment_horizon_{horizon}", initial, eta,
               tuple(task_x for _ in range(horizon)))
        for horizon in (1, 2, 3, 4)
    )


def evaluate_case(case: S4Case) -> S4CaseResult:
    started = perf_counter()
    bellman_value, bellman_path = _bellman(case)
    bellman_seconds = perf_counter() - started
    started = perf_counter()
    exhaustive_value, exhaustive_path = _exhaustive(case)
    exhaustive_seconds = perf_counter() - started
    if abs(bellman_value - exhaustive_value) > 1e-12:
        raise AssertionError("Bellman and independent exhaustive values differ")
    return S4CaseResult(
        case, _reactive(case), _simulate(case, "BELLMAN_EXACT", bellman_path),
        _simulate(case, "EXHAUSTIVE_OPTIMUM", exhaustive_path),
        bellman_value, exhaustive_value, bellman_seconds, exhaustive_seconds,
    )


def result_dict(result: S4CaseResult) -> dict:
    def policy_dict(policy: S4PolicyResult) -> dict:
        return {
            "name": policy.policy,
            "reward": policy.reward,
            "periods": [
                {
                    "period": row.period,
                    "demand": list(row.demand),
                    "assignment": [list(edge) for edge in row.assignment],
                    "immediate_reward": row.reward,
                    "competence_before": [list(values) for values in row.competence_before],
                    "competence_after": [list(values) for values in row.competence_after],
                    "cumulative_exposure": [list(values) for values in row.cumulative_exposure],
                }
                for row in policy.periods
            ],
        }
    return {
        "case": result.case.name,
        "initial_competence": [list(row) for row in result.case.initial],
        "eta": [list(row) for row in result.case.eta],
        "demand": [list(row) for row in result.case.demands],
        "reward_definition": "sum of pre-transition competence c[i,k,t] for assigned pairs",
        "transition": "existing mis_v2_transition_nk, after reward, binary exposure 1 for executed pairs",
        "bellman_value": result.bellman_value,
        "exhaustive_value": result.exhaustive_value,
        "bellman_seconds": result.bellman_seconds,
        "exhaustive_seconds": result.exhaustive_seconds,
        "reactive": policy_dict(result.reactive),
        "bellman": policy_dict(result.bellman),
        "exhaustive": policy_dict(result.exhaustive),
    }


def validation_dict(result: S4ValidationResult) -> dict:
    def policy_dict(policy: S4PolicyResult) -> dict:
        return {
            "name": policy.policy,
            "reward": policy.reward,
            "periods": [
                {
                    "period": row.period,
                    "assignment": [list(edge) for edge in row.assignment],
                    "immediate_reward": row.reward,
                    "competence_before": [list(values) for values in row.competence_before],
                    "competence_after": [list(values) for values in row.competence_after],
                }
                for row in policy.periods
            ],
        }
    return {
        "case": result.case.name,
        "learning_enabled": result.learning_enabled,
        "initial_competence": [list(row) for row in result.case.initial],
        "eta": [list(row) for row in result.case.eta],
        "demand": [list(row) for row in result.case.demands],
        "immediate_tolerance": IMMEDIATE_TOL,
        "reactive": policy_dict(result.reactive),
        "best_myopic": policy_dict(result.best_myopic),
        "bellman": policy_dict(result.bellman),
        "exhaustive_global": policy_dict(result.exhaustive),
        "exhaustive_best_myopic_value": result.exhaustive_best_myopic_value,
        "bellman_minus_best_myopic": result.bellman.reward - result.best_myopic.reward,
        "bellman_optimal_path_tie_counts": list(result.tie_counts),
        "bellman_strictly_suboptimal_periods": list(result.bellman_strictly_suboptimal_periods),
    }
