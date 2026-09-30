"""Bellman decomposition of the relevant-demand persistence diagnostic.

Goal
----
Explain the exact Bellman mechanism behind the increase of the maximum local
routing-inversion gain observed for L = 0,1,2,3.

For each L:
1. build exactly the world from audit_demand_persistence.py;
2. select exactly the same max-G_inv target as
   audit_persistence_reachability.py;
3. identify the immediate-reward-optimal and exact-HLS-optimal routing actions;
4. decompose their Q values into:
       immediate reward
       opportunity probability
       optimal conditional value for O=0
       optimal conditional value for O=1
5. enumerate the development decisions producing those conditional values;
6. verify exactly
       Q_hls - Q_greedy
         = (R_hls - R_greedy)
           + (p_hls - p_greedy) (V1 - V0)
   whenever the conditional opportunity content is executor-independent;
7. inspect the recurrence of
       D_L = V1 - V0.

This script does not search parameters, modify world physics, or extend the
persistence ladder beyond L=0,1,2,3.
"""

from __future__ import annotations

from dataclasses import dataclass

import audit_demand_persistence as adp

from hls.synthetic.exact import (
    EXACT_TOL,
    _admissible_development_actions,
    _physical_next_state,
    _task,
    solve_exact_hls,
)
from hls.synthetic.interfaces import Opportunity


TAIL_LENGTHS = (0, 1, 2, 3)


@dataclass(frozen=True)
class DevelopmentBranch:
    decision: object
    next_state: object
    continuation: float
    cost: float
    value: float


def continuation_value(problem, state):
    """Exact HLS continuation, including terminal convention."""
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


def select_target(world):
    """Exactly reproduce the target selection of persistence reachability."""
    problem = world.problem
    physical = adp.physically_reachable_states(world)

    candidates = []

    for state in physical:
        if state.time >= problem.horizon:
            continue

        gain = adp.routing_inversion_gain(world, state)

        if gain > EXACT_TOL:
            candidates.append((state, gain))

    if not candidates:
        return None, None, 0

    max_gain = max(gain for _, gain in candidates)

    maximizers = [
        (state, gain)
        for state, gain in candidates
        if abs(gain - max_gain) <= EXACT_TOL
    ]

    maximizers.sort(
        key=lambda item: (
            item[0].time,
            repr(item[0].competence),
            repr(item[0].resources),
        )
    )

    target, gain = maximizers[0]

    return target, gain, len(maximizers)


def reward_and_probability(world, state, action):
    problem = world.problem
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

    return reward, probability


def development_branches(world, state, available):
    """Enumerate exact post-routing development values conditional on O."""
    problem = world.problem
    environment = problem.environment
    opportunity = Opportunity(available)

    branches = []

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

        continuation = continuation_value(
            problem,
            next_state,
        )

        cost = environment.resources.development_cost(
            decision
        )

        value = (
            -cost
            + environment.resources.beta * continuation
        )

        branches.append(
            DevelopmentBranch(
                decision=decision,
                next_state=next_state,
                continuation=continuation,
                cost=cost,
                value=value,
            )
        )

    if not branches:
        raise RuntimeError(
            "No admissible development actions on conditional branch"
        )

    return tuple(branches)


def optimal_branches(branches):
    best = max(branch.value for branch in branches)

    return tuple(
        branch
        for branch in branches
        if abs(branch.value - best) <= EXACT_TOL
    )


def conditional_value(branches):
    return max(branch.value for branch in branches)


def print_branch_set(available, branches):
    optimal = optimal_branches(branches)
    optimal_decisions = {
        branch.decision
        for branch in optimal
    }

    print(f"  O={int(available)}")
    print(
        f"    V{int(available)} = "
        f"{conditional_value(branches):.12f}"
    )

    for branch in branches:
        marker = "*" if branch.decision in optimal_decisions else " "

        print(
            f"    {marker} d={branch.decision}"
        )
        print(
            f"        next competence="
            f"{branch.next_state.competence}"
        )
        print(
            f"        next resources="
            f"{branch.next_state.resources}"
        )
        print(
            f"        continuation="
            f"{branch.continuation:.12f}"
        )
        print(
            f"        cost="
            f"{branch.cost:.12f}"
        )
        print(
            f"        branch value="
            f"{branch.value:.12f}"
        )


def main():
    print("RQ0 persistence Bellman decomposition")
    print("-------------------------------------")
    print(
        "Fixed physics; L=0,1,2,3 only; "
        "same max-G_inv target selection as reachability audit."
    )
    print()

    records = []

    for tail_length in TAIL_LENGTHS:
        world = adp.build_world(tail_length)
        problem = world.problem

        target, gain, n_maximizers = select_target(world)

        if target is None:
            print(f"L={tail_length}: no routing inversion")
            continue

        solution = solve_exact_hls(
            problem,
            initial_state=target,
        )

        task = _task(problem, target)

        routing_data = {}

        for action in problem.operational_actions:
            reward, probability = reward_and_probability(
                world,
                target,
                action,
            )

            routing_data[action] = (
                reward,
                probability,
                solution.action_values[action],
            )

        best_reward = max(
            item[0]
            for item in routing_data.values()
        )

        greedy_actions = tuple(
            action
            for action, (reward, _, _) in routing_data.items()
            if abs(reward - best_reward) <= EXACT_TOL
        )

        best_q = max(
            item[2]
            for item in routing_data.values()
        )

        hls_actions = tuple(
            action
            for action, (_, _, q_value) in routing_data.items()
            if abs(q_value - best_q) <= EXACT_TOL
        )

        # The conditional development problem depends on state and O,
        # not on the executor, under the current G0 semantics.
        false_branches = development_branches(
            world,
            target,
            False,
        )

        true_branches = development_branches(
            world,
            target,
            True,
        )

        v0 = conditional_value(false_branches)
        v1 = conditional_value(true_branches)
        delta_v = v1 - v0

        print("=" * 100)
        print(
            f"L={tail_length}, H={problem.horizon}, "
            f"target t={target.time}, task={task}"
        )
        print(f"competence={target.competence}")
        print(f"resources={target.resources}")
        print(f"max-G_inv tied states={n_maximizers}")
        print(f"reported G_inv={gain:.12f}")
        print()

        print("Routing actions")
        print("---------------")

        for action in problem.operational_actions:
            reward, probability, q_value = routing_data[action]

            labels = []

            if action in greedy_actions:
                labels.append("GREEDY")
            if action in hls_actions:
                labels.append("HLS")

            label = ",".join(labels) if labels else "-"

            reconstructed = (
                reward
                + (1.0 - probability) * v0
                + probability * v1
            )

            print(
                f"{action}: "
                f"R={reward:.12f} "
                f"p={probability:.12f} "
                f"Q={q_value:.12f} "
                f"Q_reconstructed={reconstructed:.12f} "
                f"[{label}]"
            )

            if abs(q_value - reconstructed) > 10 * EXACT_TOL:
                raise RuntimeError(
                    f"L={tail_length}, action={action}: "
                    "Bellman reconstruction failed: "
                    f"Q={q_value:.12f}, "
                    f"reconstructed={reconstructed:.12f}"
                )

        print()
        print("Conditional development branches")
        print("--------------------------------")

        print_branch_set(False, false_branches)
        print_branch_set(True, true_branches)

        print()
        print("Opportunity-value decomposition")
        print("-------------------------------")
        print(f"V0      = {v0:.12f}")
        print(f"V1      = {v1:.12f}")
        print(f"D_L     = {delta_v:.12f}")

        # Compare every HLS-optimal action against every greedy action.
        pair_rows = []

        for hls_action in hls_actions:
            for greedy_action in greedy_actions:
                if hls_action == greedy_action:
                    continue

                r_h, p_h, q_h = routing_data[hls_action]
                r_g, p_g, q_g = routing_data[greedy_action]

                delta_r = r_h - r_g
                delta_p = p_h - p_g
                q_difference = q_h - q_g

                reconstructed_difference = (
                    delta_r + delta_p * delta_v
                )

                print()
                print(
                    f"Pair: HLS={hls_action}, "
                    f"GREEDY={greedy_action}"
                )
                print(
                    f"Delta_R = R_HLS-R_GREEDY = "
                    f"{delta_r:.12f}"
                )
                print(
                    f"Delta_p = p_HLS-p_GREEDY = "
                    f"{delta_p:.12f}"
                )
                print(
                    f"Delta_p * D_L            = "
                    f"{delta_p * delta_v:.12f}"
                )
                print(
                    f"Q_HLS-Q_GREEDY            = "
                    f"{q_difference:.12f}"
                )
                print(
                    f"Bellman reconstruction    = "
                    f"{reconstructed_difference:.12f}"
                )

                if (
                    abs(
                        q_difference
                        - reconstructed_difference
                    )
                    > 10 * EXACT_TOL
                ):
                    raise RuntimeError(
                        f"L={tail_length}: pairwise Bellman "
                        "difference reconstruction failed"
                    )

                pair_rows.append(
                    (
                        hls_action,
                        greedy_action,
                        delta_r,
                        delta_p,
                        q_difference,
                    )
                )

        records.append(
            (
                tail_length,
                delta_v,
                v0,
                v1,
                tuple(
                    branch.decision
                    for branch in optimal_branches(false_branches)
                ),
                tuple(
                    branch.decision
                    for branch in optimal_branches(true_branches)
                ),
                tuple(hls_actions),
                tuple(greedy_actions),
                tuple(pair_rows),
            )
        )

    print()
    print("=" * 100)
    print("D_L recurrence audit")
    print("--------------------")
    print(
        f"{'L':>3} "
        f"{'V0':>16} "
        f"{'V1':>16} "
        f"{'D_L':>16} "
        f"{'increment':>16} "
        f"{'ratio':>16}"
    )
    print("-" * 90)

    previous_d = None
    previous_increment = None

    for (
        tail_length,
        delta_v,
        v0,
        v1,
        _,
        _,
        _,
        _,
        _,
    ) in records:

        increment = None
        ratio = None

        if previous_d is not None:
            increment = delta_v - previous_d

        if (
            increment is not None
            and previous_increment is not None
            and abs(previous_increment) > EXACT_TOL
        ):
            ratio = increment / previous_increment

        increment_text = (
            f"{increment:.12f}"
            if increment is not None
            else "--"
        )

        ratio_text = (
            f"{ratio:.12f}"
            if ratio is not None
            else "--"
        )

        print(
            f"{tail_length:>3} "
            f"{v0:>16.12f} "
            f"{v1:>16.12f} "
            f"{delta_v:>16.12f} "
            f"{increment_text:>16} "
            f"{ratio_text:>16}"
        )

        if increment is not None:
            previous_increment = increment

        previous_d = delta_v

    print()
    print("Optimal-branch signature")
    print("------------------------")

    for (
        tail_length,
        delta_v,
        _,
        _,
        opt_false,
        opt_true,
        hls_actions,
        greedy_actions,
        _,
    ) in records:
        print(
            f"L={tail_length}: "
            f"HLS={hls_actions}, "
            f"GREEDY={greedy_actions}, "
            f"O0-opt={opt_false}, "
            f"O1-opt={opt_true}, "
            f"D={delta_v:.12f}"
        )

    print()
    print("Interpretation guard")
    print("--------------------")
    print(
        "A constant numerical increment ratio alone does not prove a "
        "Bellman recurrence for arbitrary L."
    )
    print(
        "The branch signatures and successor values above must be used "
        "to derive any claimed recurrence from the actual transition "
        "semantics."
    )


if __name__ == "__main__":
    main()
