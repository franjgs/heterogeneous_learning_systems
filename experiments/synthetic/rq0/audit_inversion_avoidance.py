"""Explain why physically reachable routing inversions are HLS-optimal unreachable.

Diagnostic world:
    H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5.

This script does not search parameters or modify world physics.

For every physically reachable ROUTING_INVERTED state it:
1. enumerates every positive-probability physical path from S0 to that state;
2. evaluates each routing decision against exact HLS Q values;
3. evaluates each development decision against the exact optimal conditional
   post-routing development value;
4. identifies the first point where the path ceases to be HLS-optimal;
5. classifies that first divergence as ROUTING or DEVELOPMENT.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import audit_horizon_boundary as hb

from hls.synthetic.exact import (
    EXACT_TOL,
    _admissible_development_actions,
    _physical_next_state,
    _task,
    solve_exact_hls,
)
from hls.synthetic.interfaces import DevelopmentDecision, Opportunity
from hls.synthetic.state import WorldState


HORIZON = 3
BUDGET = 2
ETA = 0.5


@dataclass(frozen=True)
class Step:
    state: WorldState
    operational_action: object
    opportunity: bool
    development_action: DevelopmentDecision
    next_state: WorldState


@dataclass(frozen=True)
class Divergence:
    kind: str
    time: int
    chosen_action: object | None
    optimal_actions: tuple[object, ...]
    chosen_value: float
    optimal_value: float
    loss: float


def state_key(state):
    return state.time, state.competence, state.resources


def build_world():
    old_eta = hb.ETA
    try:
        hb.ETA = ETA
        return hb.build_diagnostic_world(HORIZON, BUDGET)
    finally:
        hb.ETA = old_eta


def terminal_value(problem, state):
    environment = problem.environment
    return max(
        environment.reward.operational_reward(
            state,
            problem.terminal_task,
            action,
        )
        for action in problem.operational_actions
    )


def hls_value(problem, state):
    if state.time == problem.horizon:
        return terminal_value(problem, state)

    return solve_exact_hls(
        problem,
        initial_state=state,
    ).value


def development_values(problem, state, available):
    """Exact conditional post-routing values for all admissible decisions."""
    environment = problem.environment
    opportunity = Opportunity(available)

    values = {}

    for decision in _admissible_development_actions(
        problem,
        state,
        opportunity,
    ):
        next_state = _physical_next_state(
            problem,
            state,
            opportunity,
            decision,
        )

        values[decision] = (
            -environment.resources.development_cost(decision)
            + environment.resources.beta
            * hls_value(problem, next_state)
        )

    if not values:
        raise ValueError(
            "world exposes no resource-admissible development action"
        )

    return values


def physically_reachable_paths(world):
    """Enumerate all positive-probability physical paths from S0.

    Returns
    -------
    states_by_level
        Unique physically reachable states.
    paths_to
        Every physical path reaching each state.
    """
    problem = world.problem
    environment = problem.environment

    initial = world.initial_state

    states_by_level = defaultdict(dict)
    states_by_level[initial.time][state_key(initial)] = initial

    paths_to = defaultdict(list)
    paths_to[state_key(initial)].append(tuple())

    for time in range(initial.time, problem.horizon):
        current_states = tuple(states_by_level[time].values())

        for state in current_states:
            task = _task(problem, state)
            source_paths = tuple(paths_to[state_key(state)])

            for action in problem.operational_actions:
                probability = environment.opportunities.probability(
                    state,
                    task,
                    action,
                    (),
                )

                for available, branch_probability in (
                    (False, 1.0 - probability),
                    (True, probability),
                ):
                    if branch_probability <= EXACT_TOL:
                        continue

                    opportunity = Opportunity(available)

                    for decision in _admissible_development_actions(
                        problem,
                        state,
                        opportunity,
                    ):
                        next_state = _physical_next_state(
                            problem,
                            state,
                            opportunity,
                            decision,
                        )

                        key = state_key(next_state)
                        states_by_level[next_state.time][key] = next_state

                        step = Step(
                            state=state,
                            operational_action=action,
                            opportunity=available,
                            development_action=decision,
                            next_state=next_state,
                        )

                        for path in source_paths:
                            paths_to[key].append(path + (step,))

    return states_by_level, paths_to


def routing_inverted(world, state):
    """Whether exact HLS routing excludes all immediate-reward maximizers."""
    problem = world.problem
    environment = problem.environment
    task = _task(problem, state)

    solution = solve_exact_hls(
        problem,
        initial_state=state,
    )

    rewards = {
        action: environment.reward.operational_reward(
            state,
            task,
            action,
        )
        for action in problem.operational_actions
    }

    best_reward = max(rewards.values())

    greedy = frozenset(
        action
        for action, reward in rewards.items()
        if abs(reward - best_reward) <= EXACT_TOL
    )

    # Strong condition: HLS has no immediately greedy optimal action.
    return greedy.isdisjoint(solution.optimal_actions)


def first_divergence(world, path):
    """Find first routing/development choice not compatible with exact HLS."""
    problem = world.problem

    for step in path:
        # --------------------------------------------------------
        # Routing decision
        # --------------------------------------------------------
        solution = solve_exact_hls(
            problem,
            initial_state=step.state,
        )

        q_values = solution.action_values
        optimal_q = max(q_values.values())
        chosen_q = q_values[step.operational_action]

        if chosen_q < optimal_q - EXACT_TOL:
            optimal_actions = tuple(
                action
                for action, value in q_values.items()
                if abs(value - optimal_q) <= EXACT_TOL
            )

            return Divergence(
                kind="ROUTING",
                time=step.state.time,
                chosen_action=step.operational_action,
                optimal_actions=optimal_actions,
                chosen_value=chosen_q,
                optimal_value=optimal_q,
                loss=optimal_q - chosen_q,
            )

        # --------------------------------------------------------
        # Development decision, conditional on realized O
        # --------------------------------------------------------
        d_values = development_values(
            problem,
            step.state,
            step.opportunity,
        )

        optimal_d = max(d_values.values())
        chosen_d = d_values[step.development_action]

        if chosen_d < optimal_d - EXACT_TOL:
            optimal_decisions = tuple(
                decision
                for decision, value in d_values.items()
                if abs(value - optimal_d) <= EXACT_TOL
            )

            return Divergence(
                kind="DEVELOPMENT",
                time=step.state.time,
                chosen_action=step.development_action,
                optimal_actions=optimal_decisions,
                chosen_value=chosen_d,
                optimal_value=optimal_d,
                loss=optimal_d - chosen_d,
            )

    return None


def print_path(path):
    for step in path:
        print(
            f"    t={step.state.time}: "
            f"a={step.operational_action}, "
            f"O={int(step.opportunity)}, "
            f"d={step.development_action}"
        )


def main():
    world = build_world()
    problem = world.problem

    levels, paths_to = physically_reachable_paths(world)

    inverted_states = []

    for time in range(problem.horizon):
        for state in levels[time].values():
            if routing_inverted(world, state):
                inverted_states.append(state)

    print("RQ0 inversion-avoidance diagnostic")
    print("----------------------------------")
    print("H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5")
    print()
    print(
        f"physically reachable routing-inverted states = "
        f"{len(inverted_states)}"
    )
    print()

    total_paths = 0
    routing_first = 0
    development_first = 0
    fully_optimal = 0

    for index, target in enumerate(inverted_states, 1):
        paths = paths_to[state_key(target)]
        total_paths += len(paths)

        print("=" * 78)
        print(
            f"INVERTED STATE {index}/{len(inverted_states)} "
            f"(t={target.time})"
        )
        print(f"competence={target.competence}")
        print(f"resources={target.resources}")
        print(f"physical paths={len(paths)}")
        print()

        best_loss = None
        best_record = None

        local_counts = {
            "ROUTING": 0,
            "DEVELOPMENT": 0,
            "NONE": 0,
        }

        for path_number, path in enumerate(paths, 1):
            divergence = first_divergence(world, path)

            if divergence is None:
                local_counts["NONE"] += 1
                fully_optimal += 1
                loss = 0.0
            else:
                local_counts[divergence.kind] += 1

                if divergence.kind == "ROUTING":
                    routing_first += 1
                elif divergence.kind == "DEVELOPMENT":
                    development_first += 1

                loss = divergence.loss

            if best_loss is None or loss < best_loss:
                best_loss = loss
                best_record = (
                    path_number,
                    path,
                    divergence,
                )

        print(
            "first-divergence counts: "
            f"ROUTING={local_counts['ROUTING']}, "
            f"DEVELOPMENT={local_counts['DEVELOPMENT']}, "
            f"NONE={local_counts['NONE']}"
        )

        path_number, path, divergence = best_record

        print()
        print("Closest physical path to HLS optimality")
        print(f"  path #{path_number}")
        print_path(path)

        print()

        if divergence is None:
            print("  first divergence: NONE")
        else:
            print(
                f"  first divergence: {divergence.kind} "
                f"at t={divergence.time}"
            )
            print(f"  chosen={divergence.chosen_action}")
            print(f"  optimal={divergence.optimal_actions}")
            print(
                f"  chosen value={divergence.chosen_value:.12f}"
            )
            print(
                f"  optimal value={divergence.optimal_value:.12f}"
            )
            print(
                f"  exact loss={divergence.loss:.12f}"
            )

        print()

    print("=" * 78)
    print("GLOBAL AVOIDANCE SUMMARY")
    print("------------------------")
    print(f"inverted states = {len(inverted_states)}")
    print(f"physical paths to them = {total_paths}")
    print(f"first divergence ROUTING = {routing_first}")
    print(f"first divergence DEVELOPMENT = {development_first}")
    print(f"fully HLS-optimal paths = {fully_optimal}")

    print()
    print("Interpretation")
    print("--------------")

    if fully_optimal:
        print(
            "At least one routing-inverted state is reachable through "
            "a fully HLS-optimal path. This contradicts the previous "
            "optimal-reachability audit and must be investigated."
        )
    elif development_first and not routing_first:
        print(
            "All paths to routing inversion are excluded first by "
            "development decisions: HLS avoids the later routing conflict "
            "through earlier competence management."
        )
    elif routing_first and not development_first:
        print(
            "All paths to routing inversion are excluded first by routing: "
            "the conflict requires an earlier routing sacrifice that is "
            "already suboptimal."
        )
    elif routing_first and development_first:
        print(
            "Both mechanisms occur: some paths are excluded first by routing "
            "and others by development. Inspect the minimum-loss paths above."
        )
    else:
        print(
            "No classified path found; inspect reachability logic."
        )


if __name__ == "__main__":
    main()
