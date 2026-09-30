"""Exact audit of the eta=0.5 routing-inversion world.

Diagnostic only.  This is not part of the preregistered RQ0-A/B campaign.

World:
    H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5.

Questions:
1. Are routing-inverted states reachable under an exact HLS-optimal policy
   from the initial state?
2. Does the local routing inversion propagate to
       J_HLS > J_SEP,max
   at the initial state?
3. Does SEP-Omega reconstruct the HLS solution?
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import audit_horizon_boundary as hb

from hls.synthetic.exact import (
    EXACT_TOL,
    _admissible_development_actions,
    _branch_value,
    _optimal_set,
    _physical_next_state,
    _task,
    solve_exact_hls,
    solve_exact_sep_omega,
    solve_exact_strong_sep,
)
from hls.synthetic.interfaces import DevelopmentDecision, Opportunity
from hls.synthetic.state import WorldState


HORIZON = 3
BUDGET = 2
ETA = 0.5


@dataclass(frozen=True)
class OptimalPredecessor:
    state: WorldState
    operational_action: object
    opportunity: bool
    development_action: DevelopmentDecision


def state_key(state):
    return state.time, state.competence, state.resources


def build_world():
    """Use the horizon diagnostic builder, changing only eta."""
    old_eta = hb.ETA
    try:
        hb.ETA = ETA
        return hb.build_diagnostic_world(HORIZON, BUDGET)
    finally:
        hb.ETA = old_eta


def continuation_value(problem, state):
    """Exact HLS value, including the terminal convention."""
    if state.time == problem.horizon:
        environment = problem.environment
        return max(
            environment.reward.operational_reward(
                state,
                problem.terminal_task,
                action,
            )
            for action in problem.operational_actions
        )

    return solve_exact_hls(
        problem,
        initial_state=state,
    ).value


def optimal_development_actions(problem, state, opportunity):
    """Development decisions maximizing exact post-routing continuation."""
    environment = problem.environment

    decisions = _admissible_development_actions(
        problem,
        state,
        opportunity,
    )

    values = {}

    for decision in decisions:
        next_state = _physical_next_state(
            problem,
            state,
            opportunity,
            decision,
        )

        values[decision] = (
            -environment.resources.development_cost(decision)
            + environment.resources.beta
            * continuation_value(problem, next_state)
        )

    best = max(values.values())

    return tuple(
        decision
        for decision, value in values.items()
        if abs(value - best) <= EXACT_TOL
    )


def optimal_reachable_states(world):
    """All states reachable through any exact HLS-optimal continuation.

    Preserve:
    - routing ties,
    - positive-probability opportunity branches,
    - development ties.
    """
    problem = world.problem
    environment = problem.environment

    levels = defaultdict(dict)
    initial = world.initial_state

    levels[initial.time][state_key(initial)] = initial
    predecessor = {state_key(initial): None}

    for time in range(initial.time, problem.horizon):
        for state in tuple(levels[time].values()):
            solution = solve_exact_hls(
                problem,
                initial_state=state,
            )

            task = _task(problem, state)

            for action in solution.optimal_actions:
                probability = environment.opportunities.probability(
                    state,
                    task,
                    action,
                    (),
                )

                for available, weight in (
                    (False, 1.0 - probability),
                    (True, probability),
                ):
                    if weight <= EXACT_TOL:
                        continue

                    opportunity = Opportunity(available)

                    for decision in optimal_development_actions(
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

                        if key not in levels[next_state.time]:
                            levels[next_state.time][key] = next_state
                            predecessor[key] = OptimalPredecessor(
                                state=state,
                                operational_action=action,
                                opportunity=available,
                                development_action=decision,
                            )

    states = tuple(
        state
        for time in sorted(levels)
        for state in levels[time].values()
    )

    return states, predecessor


def reward_optimal_actions(world, state):
    problem = world.problem
    environment = problem.environment
    task = _task(problem, state)

    rewards = {
        action: environment.reward.operational_reward(
            state,
            task,
            action,
        )
        for action in problem.operational_actions
    }

    return _optimal_set(rewards), rewards


def classify_optimal_state(world, state):
    """Return exact routing/reward information at one state."""
    solution = solve_exact_hls(
        world.problem,
        initial_state=state,
    )

    greedy, rewards = reward_optimal_actions(world, state)

    inverted = not solution.optimal_actions.issubset(greedy)

    return inverted, greedy, solution.optimal_actions, rewards, solution


def reconstruct_path(state, predecessor):
    path = []
    current = state

    while predecessor[state_key(current)] is not None:
        pred = predecessor[state_key(current)]
        path.append(pred)
        current = pred.state

    return tuple(reversed(path))


def print_path(state, predecessor):
    path = reconstruct_path(state, predecessor)

    if not path:
        print("  INITIAL STATE")
        return

    for pred in path:
        print(
            f"  t={pred.state.time}: "
            f"a={pred.operational_action}, "
            f"O={int(pred.opportunity)}, "
            f"d={pred.development_action}"
        )


def main():
    world = build_world()
    problem = world.problem

    print("RQ0 eta=0.5 exact non-separability audit")
    print("----------------------------------------")
    print(
        "H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5"
    )
    print()

    # ------------------------------------------------------------
    # Global initial-state values
    # ------------------------------------------------------------

    hls = solve_exact_hls(
        problem,
        initial_state=world.initial_state,
    )

    sep = solve_exact_strong_sep(
        problem,
        initial_state=world.initial_state,
    )

    omega = solve_exact_sep_omega(
        problem,
        initial_state=world.initial_state,
    )

    delta_cons = hls.value - sep.value_max
    delta_omega = hls.value - omega.value

    print("Initial-state exact values")
    print("--------------------------")
    print(f"J_HLS       = {hls.value:.12f}")
    print(f"J_SEP_min   = {sep.value_min:.12f}")
    print(f"J_SEP_max   = {sep.value_max:.12f}")
    print(f"J_SEP-Omega = {omega.value:.12f}")
    print(f"Delta_cons  = {delta_cons:.12f}")
    print(f"Delta_Omega = {delta_omega:.12f}")
    print()

    # ------------------------------------------------------------
    # HLS-optimal reachability
    # ------------------------------------------------------------

    states, predecessor = optimal_reachable_states(world)

    nonterminal = tuple(
        state
        for state in states
        if state.time < problem.horizon
    )

    inverted_states = []

    print("HLS-optimal reachability")
    print("------------------------")
    print(f"reachable states             = {len(states)}")
    print(f"reachable nonterminal states = {len(nonterminal)}")

    for state in nonterminal:
        (
            inverted,
            greedy,
            hls_actions,
            rewards,
            solution,
        ) = classify_optimal_state(world, state)

        if inverted:
            inverted_states.append(
                (state, greedy, hls_actions, rewards, solution)
            )

    print(
        "routing-inverted states      = "
        f"{len(inverted_states)}"
    )
    print()

    # ------------------------------------------------------------
    # Detailed exact counterexamples
    # ------------------------------------------------------------

    if inverted_states:
        print("OPTIMAL-REACHABLE ROUTING INVERSION FOUND")
        print("=========================================")

        for (
            state,
            greedy,
            hls_actions,
            rewards,
            solution,
        ) in inverted_states:

            print()
            print("=" * 78)
            print(f"t={state.time}")
            print(f"competence={state.competence}")
            print(f"resources={state.resources}")
            print(f"greedy_actions={sorted(greedy)}")
            print(f"HLS_actions={sorted(hls_actions)}")

            print("rewards:")
            for action in problem.operational_actions:
                print(
                    f"  {action}: {rewards[action]:.12f}"
                )

            print("Q_HLS:")
            for action in problem.operational_actions:
                print(
                    f"  {action}: "
                    f"{solution.action_values[action]:.12f}"
                )

            print("optimal path from S0:")
            print_path(state, predecessor)

    else:
        print("NO optimal-reachable routing inversion.")

    print()
    print("Verdict")
    print("-------")

    if inverted_states:
        print(
            "LOCAL: routing non-separability is reached under "
            "an exact HLS-optimal continuation."
        )
    else:
        print(
            "LOCAL: the physically reachable inversion does not lie "
            "on an exact HLS-optimal continuation."
        )

    if delta_cons > EXACT_TOL:
        print(
            "GLOBAL: J_HLS > J_SEP_max."
        )
        print(
            "The local routing non-separability propagates to positive "
            "conservative integration value from S0."
        )
    elif abs(delta_cons) <= EXACT_TOL:
        print(
            "GLOBAL: J_HLS = J_SEP_max within exact tolerance."
        )
        print(
            "The local inversion does not produce conservative "
            "integration value from S0."
        )
    else:
        print(
            "GLOBAL: J_HLS < J_SEP_max."
        )

    if abs(delta_omega) <= EXACT_TOL:
        print(
            "SEP-Omega reconstructs HLS exactly."
        )
    else:
        print(
            "SEP-Omega does not reconstruct HLS exactly."
        )


if __name__ == "__main__":
    main()
