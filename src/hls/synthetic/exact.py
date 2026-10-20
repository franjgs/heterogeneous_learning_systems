"""Policy-neutral exact finite-horizon solvers for synthetic HLS worlds.

This module generalizes the exact dynamic recursion first exercised by C1.
It contains no RQ0 campaign parameters and no reference-world-specific logic.

Three comparison architectures are represented:

HLS
    Operational routing and development are optimized jointly through exact
    continuation value.

Strong SEP
    Routing is restricted to actions maximizing immediate operational reward.
    Conditional on that routing choice and realized opportunity, development
    is optimized exactly. Routing ties are preserved as value bounds.

SEP-Omega
    Routing receives exact continuation value. It therefore provides the
    constructive reducibility boundary and is solved independently from HLS.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from types import MappingProxyType
from typing import Hashable, Mapping

from .c5 import MarkovTaskDemand, NonStationaryTaskDemand, StationaryTaskDemand
from .environment import SyntheticEnvironment
from .interfaces import DevelopmentDecision, Opportunity, TaskProcess
from .state import WorldState


EXACT_TOL = 1e-12


@dataclass(frozen=True)
class ExactProblem:
    """Finite-horizon exact synthetic-world problem."""

    environment: SyntheticEnvironment
    operational_actions: tuple[Hashable, ...]
    horizon: int
    terminal_task: Hashable
    demand_process: TaskProcess | None = None

    def __post_init__(self) -> None:
        if not self.operational_actions:
            raise ValueError("at least one operational action is required")
        if self.horizon < 1:
            raise ValueError("horizon must be positive")


@dataclass(frozen=True)
class ExactDynamicSolution:
    value: float
    optimal_actions: frozenset[Hashable]
    action_values: Mapping[Hashable, float]


@dataclass(frozen=True)
class ExactStrongSEPSolution:
    value_min: float
    value_max: float
    immediate_optimal_actions: frozenset[Hashable]
    action_value_bounds: Mapping[Hashable, tuple[float, float]]


def _optimal_set(
    values: Mapping[Hashable, float],
) -> frozenset[Hashable]:
    best = max(values.values())
    return frozenset(
        action
        for action, value in values.items()
        if abs(value - best) <= EXACT_TOL
    )


def _task(problem: ExactProblem, state: WorldState):
    """Resolve the task exactly.

    Exact solvers require task_at semantics. Stochastic task demand belongs
    to a separate exact integration problem and is not silently sampled here.
    """
    return problem.environment.tasks.task_at(
        state.time,
        state,
        (),
    )


def _terminal_value(
    problem: ExactProblem,
    state: WorldState,
) -> float:
    environment = problem.environment
    return max(
        environment.reward.operational_reward(
            state,
            problem.terminal_task,
            action,
        )
        for action in problem.operational_actions
    )


def _physical_next_state(
    problem: ExactProblem,
    state: WorldState,
    opportunity: Opportunity,
    decision: DevelopmentDecision,
) -> WorldState:
    """Apply G0 development and persistent resource physics exactly."""
    environment = problem.environment

    if not environment.resources.development_is_admissible(
        state,
        decision,
        opportunity,
    ):
        raise ValueError("development action violates resource semantics")

    developed = environment.development.transition(
        state,
        opportunity,
        decision,
    )
    resources = environment.resources.consume(state, decision)

    next_state = WorldState(
        competence=developed.competence,
        time=developed.time,
        resources=resources,
    )
    environment.competence.validate(next_state)
    return next_state


def _admissible_development_actions(
    problem: ExactProblem,
    state: WorldState,
    opportunity: Opportunity,
) -> tuple[DevelopmentDecision, ...]:
    environment = problem.environment
    return tuple(
        decision
        for decision in environment.development.admissible_actions(
            state,
            opportunity,
        )
        if environment.resources.development_is_admissible(
            state,
            decision,
            opportunity,
        )
    )


def _branch_value(
    problem: ExactProblem,
    state: WorldState,
    action: Hashable,
    continuation,
) -> float:
    environment = problem.environment
    task = _task(problem, state)

    reward = environment.reward.operational_reward(
        state,
        task,
        action,
    )
    probability = environment.opportunities.probability(
        state,
        task,
        action,
        (),
    )

    expected = 0.0

    for available, weight in (
        (False, 1.0 - probability),
        (True, probability),
    ):
        if weight <= 0.0:
            continue

        opportunity = Opportunity(available)
        decisions = _admissible_development_actions(
            problem,
            state,
            opportunity,
        )

        if not decisions:
            raise ValueError(
                "world exposes no resource-admissible development action"
            )

        development_values = []

        for decision in decisions:
            next_state = _physical_next_state(
                problem,
                state,
                opportunity,
                decision,
            )
            development_values.append(
                -environment.resources.development_cost(decision)
                + environment.resources.beta * continuation(next_state)
            )

        expected += weight * max(development_values)

    return reward + expected


def _branch_bounds(
    problem: ExactProblem,
    state: WorldState,
    action: Hashable,
    continuation,
) -> tuple[float, float]:
    """Propagate strong-SEP bounds without resolving routing ties."""
    environment = problem.environment
    task = _task(problem, state)

    reward = environment.reward.operational_reward(
        state,
        task,
        action,
    )
    probability = environment.opportunities.probability(
        state,
        task,
        action,
        (),
    )

    expected_min = 0.0
    expected_max = 0.0

    for available, weight in (
        (False, 1.0 - probability),
        (True, probability),
    ):
        if weight <= 0.0:
            continue

        opportunity = Opportunity(available)
        decisions = _admissible_development_actions(
            problem,
            state,
            opportunity,
        )

        if not decisions:
            raise ValueError(
                "world exposes no resource-admissible development action"
            )

        development_bounds = []

        for decision in decisions:
            next_state = _physical_next_state(
                problem,
                state,
                opportunity,
                decision,
            )
            downstream_min, downstream_max = continuation(next_state)
            cost = environment.resources.development_cost(decision)

            development_bounds.append(
                (
                    -cost
                    + environment.resources.beta * downstream_min,
                    -cost
                    + environment.resources.beta * downstream_max,
                )
            )

        expected_min += weight * max(
            bound[0] for bound in development_bounds
        )
        expected_max += weight * max(
            bound[1] for bound in development_bounds
        )

    return reward + expected_min, reward + expected_max


def solve_exact_hls(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> ExactDynamicSolution:
    """Solve the exact joint HLS recursion."""

    def value(state: WorldState) -> float:
        if state.time == problem.horizon:
            return _terminal_value(problem, state)
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        values = {
            action: _branch_value(
                problem,
                state,
                action,
                value,
            )
            for action in problem.operational_actions
        }
        return max(values.values())

    state = (
        problem.environment.initial_state()
        if initial_state is None
        else initial_state
    )

    action_values = {
        action: _branch_value(
            problem,
            state,
            action,
            value,
        )
        for action in problem.operational_actions
    }

    return ExactDynamicSolution(
        value=max(action_values.values()),
        optimal_actions=_optimal_set(action_values),
        action_values=action_values,
    )


def solve_exact_strong_sep(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> ExactStrongSEPSolution:
    """Solve strong SEP with exact development and unresolved routing ties."""

    def bounds(state: WorldState) -> tuple[float, float]:
        if state.time == problem.horizon:
            terminal = _terminal_value(problem, state)
            return terminal, terminal
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        task = _task(problem, state)
        rewards = {
            action: problem.environment.reward.operational_reward(
                state,
                task,
                action,
            )
            for action in problem.operational_actions
        }

        immediate = _optimal_set(rewards)

        action_bounds = {
            action: _branch_bounds(
                problem,
                state,
                action,
                bounds,
            )
            for action in immediate
        }

        return (
            min(pair[0] for pair in action_bounds.values()),
            max(pair[1] for pair in action_bounds.values()),
        )

    state = (
        problem.environment.initial_state()
        if initial_state is None
        else initial_state
    )

    task = _task(problem, state)
    rewards = {
        action: problem.environment.reward.operational_reward(
            state,
            task,
            action,
        )
        for action in problem.operational_actions
    }

    immediate = _optimal_set(rewards)

    action_bounds = {
        action: _branch_bounds(
            problem,
            state,
            action,
            bounds,
        )
        for action in immediate
    }

    return ExactStrongSEPSolution(
        value_min=min(pair[0] for pair in action_bounds.values()),
        value_max=max(pair[1] for pair in action_bounds.values()),
        immediate_optimal_actions=immediate,
        action_value_bounds=action_bounds,
    )


def solve_exact_sep_omega(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> ExactDynamicSolution:
    """Solve SEP-Omega independently with exact continuation information."""

    def value(state: WorldState) -> float:
        if state.time == problem.horizon:
            return _terminal_value(problem, state)
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        values = {
            action: _branch_value(
                problem,
                state,
                action,
                value,
            )
            for action in problem.operational_actions
        }
        return max(values.values())

    state = (
        problem.environment.initial_state()
        if initial_state is None
        else initial_state
    )

    action_values = {
        action: _branch_value(
            problem,
            state,
            action,
            value,
        )
        for action in problem.operational_actions
    }

    return ExactDynamicSolution(
        value=max(action_values.values()),
        optimal_actions=_optimal_set(action_values),
        action_values=action_values,
    )


# The stochastic-demand APIs below are an optional extension. The established
# deterministic `task_at` recursion above is intentionally left unchanged.


@dataclass(frozen=True)
class DemandExecutablePolicy:
    """Executable finite-horizon decisions keyed only by current observations.

    Operation is keyed by `(WorldState, current_task)`. Development is keyed
    additionally by the action and the opportunity outcome, which is only
    queried after that outcome has been observed.
    """

    operational_decisions: Mapping[tuple[WorldState, Hashable], Hashable]
    development_decisions: Mapping[
        tuple[WorldState, Hashable, Hashable, bool], DevelopmentDecision
    ]
    static_routing: Mapping[Hashable, Hashable] | None = None
    tie_coordination: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "operational_decisions",
            MappingProxyType(dict(self.operational_decisions)),
        )
        object.__setattr__(
            self,
            "development_decisions",
            MappingProxyType(dict(self.development_decisions)),
        )
        if self.static_routing is not None:
            object.__setattr__(
                self, "static_routing", MappingProxyType(dict(self.static_routing))
            )

    def choose_operational_action(
        self, state: WorldState, task: Hashable
    ) -> Hashable:
        if self.static_routing is not None:
            return self.static_routing[task]
        return self.operational_decisions[(state, task)]

    def choose_development_action(
        self,
        state: WorldState,
        task: Hashable,
        operational_action: Hashable,
        opportunity: Opportunity,
    ) -> DevelopmentDecision:
        return self.development_decisions[
            (state, task, operational_action, opportunity.available)
        ]


@dataclass(frozen=True)
class DemandPolicySolution:
    """Expected value and executable policy under a finite C5 demand law."""

    value: float
    policy: DemandExecutablePolicy
    initial_task_values: tuple[tuple[Hashable, float], ...]


@dataclass(frozen=True)
class StaticRoutingCandidate:
    routing: tuple[tuple[Hashable, Hashable], ...]
    value: float


@dataclass(frozen=True)
class BestStaticRoutingSolution:
    value: float
    routing: tuple[tuple[Hashable, Hashable], ...]
    policy: DemandExecutablePolicy
    candidates: tuple[StaticRoutingCandidate, ...]


def _demand_model(problem: ExactProblem):
    demand = problem.demand_process or problem.environment.tasks
    if not isinstance(
        demand,
        (StationaryTaskDemand, NonStationaryTaskDemand, MarkovTaskDemand),
    ):
        raise TypeError(
            "stochastic exact policies require a supported finite C5 demand process"
        )
    return demand


def _demand_distribution(
    demand,
    time: int,
    previous_task: Hashable | None,
) -> Mapping[Hashable, float]:
    if isinstance(demand, StationaryTaskDemand):
        return demand.distribution
    if isinstance(demand, NonStationaryTaskDemand):
        try:
            return demand.distributions[time]
        except KeyError as error:
            raise ValueError(
                f"non-stationary demand has no distribution for period {time}"
            ) from error
    if isinstance(demand, MarkovTaskDemand):
        if time == 0:
            return demand.initial_distribution
        if previous_task not in demand.transitions:
            raise ValueError("Markov demand needs the previous observed task")
        return demand.transitions[previous_task]
    raise TypeError("unsupported demand process")


def demand_task_catalog(problem: ExactProblem) -> tuple[Hashable, ...]:
    """Return tasks appearing in the finite horizon, in stable catalog order."""
    demand = _demand_model(problem)
    if isinstance(demand, StationaryTaskDemand):
        distributions = (demand.distribution,)
    elif isinstance(demand, NonStationaryTaskDemand):
        distributions = tuple(
            demand.distributions[time] for time in range(problem.horizon)
        )
    else:
        distributions = (demand.initial_distribution, *demand.transitions.values())
    tasks = []
    for distribution in distributions:
        for task, probability in distribution.items():
            if probability > 0.0 and task not in tasks:
                tasks.append(task)
    if not tasks:
        raise ValueError("demand process has no positive-probability task")
    return tuple(tasks)


def _demand_policy_solution(
    problem: ExactProblem,
    *,
    mode: str,
    fixed_routing: Mapping[Hashable, Hashable] | None = None,
    initial_state: WorldState | None = None,
) -> DemandPolicySolution:
    if not problem.operational_actions:
        raise ValueError("at least one operational action is required")
    if mode not in {"hls", "strong_sep", "myopic", "fixed"}:
        raise ValueError("unknown stochastic policy mode")

    demand = _demand_model(problem)
    environment = problem.environment
    task_catalog = demand_task_catalog(problem)
    if mode == "fixed":
        if fixed_routing is None or set(fixed_routing) != set(task_catalog):
            raise ValueError("fixed routing must cover exactly the demand task catalog")
        if any(action not in problem.operational_actions for action in fixed_routing.values()):
            raise ValueError("fixed routing contains an infeasible operational action")

    operational_decisions: dict[tuple[WorldState, Hashable], Hashable] = {}
    development_decisions: dict[
        tuple[WorldState, Hashable, Hashable, bool], DevelopmentDecision
    ] = {}

    def continuation_value(next_state: WorldState, task: Hashable) -> float:
        if next_state.time == problem.horizon:
            return _terminal_value(problem, next_state)
        if next_state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")
        return value(next_state, task)

    @lru_cache(maxsize=None)
    def value(state: WorldState, task: Hashable) -> float:
        if state.time == problem.horizon:
            return _terminal_value(problem, state)
        if state.time > problem.horizon:
            raise ValueError("state lies beyond declared horizon")

        rewards = {
            action: environment.reward.operational_reward(state, task, action)
            for action in problem.operational_actions
        }
        immediate_best = max(rewards.values())
        immediate_actions = tuple(
            action
            for action in problem.operational_actions
            if abs(rewards[action] - immediate_best) <= EXACT_TOL
        )

        if mode == "fixed":
            candidate_actions = (fixed_routing[task],)  # type: ignore[index]
        elif mode == "strong_sep" or mode == "myopic":
            candidate_actions = immediate_actions
        else:
            candidate_actions = problem.operational_actions

        action_values: dict[Hashable, float] = {}
        for action in candidate_actions:
            reward = rewards[action]
            probability = environment.opportunities.probability(
                state, task, action, ()
            )
            if not 0.0 <= probability <= 1.0:
                raise ValueError("opportunity probability must lie in [0, 1]")
            expected_future = 0.0
            for available, weight in (
                (False, 1.0 - probability),
                (True, probability),
            ):
                if weight <= 0.0:
                    continue
                opportunity = Opportunity(available)
                decisions = _admissible_development_actions(
                    problem, state, opportunity
                )
                if not decisions:
                    raise ValueError(
                        "world exposes no resource-admissible development action"
                    )
                development_values: list[tuple[float, DevelopmentDecision]] = []
                for decision in decisions:
                    next_state = _physical_next_state(
                        problem, state, opportunity, decision
                    )
                    if next_state.time == problem.horizon:
                        future = _terminal_value(problem, next_state)
                    else:
                        distribution = _demand_distribution(
                            demand, next_state.time, task
                        )
                        future = sum(
                            task_probability
                            * continuation_value(next_state, next_task)
                            for next_task, task_probability in distribution.items()
                            if task_probability > 0.0
                        )
                    development_values.append(
                        (
                            -environment.resources.development_cost(decision)
                            + environment.resources.beta * future,
                            decision,
                        )
                    )

                if mode == "myopic":
                    # Preserve admissible-action order on ties; G0's null action
                    # is first, so an immediate-only policy does not develop.
                    selected_development = min(
                        (item[1] for item in development_values),
                        key=lambda decision: environment.resources.development_cost(decision),
                    )
                    selected_value = next(
                        item[0]
                        for item in development_values
                        if item[1] == selected_development
                    )
                else:
                    best_development = max(item[0] for item in development_values)
                    selected_value, selected_development = next(
                        item
                        for item in development_values
                        if abs(item[0] - best_development) <= EXACT_TOL
                    )
                development_decisions[(state, task, action, available)] = (
                    selected_development
                )
                expected_future += weight * selected_value
            action_values[action] = reward + expected_future

        if mode == "hls":
            best_action_value = max(action_values.values())
            selected_action = next(
                action
                for action in problem.operational_actions
                if action in action_values
                and abs(action_values[action] - best_action_value) <= EXACT_TOL
            )
        elif mode == "fixed":
            selected_action = candidate_actions[0]
        elif mode == "strong_sep":
            # Canonical SEP permits selection only inside the immediate-reward
            # argmax set. The CE-approved tie rule uses continuation there and
            # is therefore explicitly recorded as coordination information.
            best_action_value = max(action_values.values())
            selected_action = next(
                action
                for action in immediate_actions
                if abs(action_values[action] - best_action_value) <= EXACT_TOL
            )
        else:
            # Strong-SEP resolves immediate routing ties by the declared
            # operational catalog order; myopic routing never uses continuation.
            selected_action = immediate_actions[0]
        operational_decisions[(state, task)] = selected_action
        return action_values[selected_action]

    state = (
        environment.initial_state()
        if initial_state is None
        else initial_state
    )
    if state.time != 0:
        raise ValueError("stochastic exact policies must start at period zero")
    initial_distribution = _demand_distribution(demand, 0, None)
    initial_task_values = tuple(
        (task, value(state, task))
        for task, probability in initial_distribution.items()
        if probability > 0.0
    )
    expected_value = sum(
        probability * value(state, task)
        for task, probability in initial_distribution.items()
        if probability > 0.0
    )
    return DemandPolicySolution(
        value=expected_value,
        policy=DemandExecutablePolicy(
            operational_decisions,
            development_decisions,
            fixed_routing,
            (
                "continuation value only among immediate-reward maximizers"
                if mode == "strong_sep"
                else None
            ),
        ),
        initial_task_values=initial_task_values,
    )


def solve_demand_exact_hls(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> DemandPolicySolution:
    """Solve and return an executable nonclairvoyant HLS policy."""
    return _demand_policy_solution(
        problem, mode="hls", initial_state=initial_state
    )


def solve_demand_exact_strong_sep(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> DemandPolicySolution:
    """Executable strong-SEP with strongest admissible continuation tie rule.

    Routing remains inside the canonical immediate-reward argmax set. Where
    that set has multiple actions, continuation value selects the best tied
    action; the resulting coordination restriction is recorded on the policy.
    """
    return _demand_policy_solution(
        problem, mode="strong_sep", initial_state=initial_state
    )


def solve_demand_myopic(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> DemandPolicySolution:
    """Executable current-reward policy with null-first cost ties."""
    return _demand_policy_solution(
        problem, mode="myopic", initial_state=initial_state
    )


def solve_demand_best_static_routing(
    problem: ExactProblem,
    *,
    initial_state: WorldState | None = None,
) -> BestStaticRoutingSolution:
    """Globally optimize a stationary task-to-action map under the demand law.

    For each fixed routing map, development remains state-responsive and is
    optimized by exact continuation. The map is selected before any test-path
    realization, so this is a strong nonclairvoyant static-routing baseline.
    """
    tasks = demand_task_catalog(problem)
    candidates: list[StaticRoutingCandidate] = []
    solutions: list[DemandPolicySolution] = []
    for actions in product(problem.operational_actions, repeat=len(tasks)):
        routing = dict(zip(tasks, actions))
        solution = _demand_policy_solution(
            problem,
            mode="fixed",
            fixed_routing=routing,
            initial_state=initial_state,
        )
        candidates.append(
            StaticRoutingCandidate(tuple(routing.items()), solution.value)
        )
        solutions.append(solution)
    best_value = max(candidate.value for candidate in candidates)
    best_index = next(
        index
        for index, candidate in enumerate(candidates)
        if abs(candidate.value - best_value) <= EXACT_TOL
    )
    selected = candidates[best_index]
    return BestStaticRoutingSolution(
        value=selected.value,
        routing=selected.routing,
        policy=solutions[best_index].policy,
        candidates=tuple(candidates),
    )
