"""Exact constrained reachability audit for physically reachable routing inversions.

Diagnostic world:
    H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5.

For every physically reachable ROUTING_INVERTED state S^dagger, solve exactly

    J^{->S^dagger}
        = max_pi J(pi)
          subject to P_pi(reach S^dagger) > 0.

The corresponding exact reachability cost is

    C_reach(S^dagger)
        = J_HLS(S0) - J^{->S^dagger}.

This differs fundamentally from the path diagnostics in
audit_reachability_cost.py.  Here the policy is unconstrained on branches
that do not lead to the target and can act optimally there.  The constraint
only requires the target to remain reachable with positive probability.

No parameters are searched and world physics are not modified.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import audit_inversion_avoidance as aia
import audit_reachability_cost as arc

from hls.synthetic.exact import (
    EXACT_TOL,
    _admissible_development_actions,
    _physical_next_state,
    _task,
    solve_exact_hls,
)
from hls.synthetic.interfaces import Opportunity


@dataclass(frozen=True)
class ConstrainedResult:
    value: float
    reach_probability: float
    action: object | None = None


def opportunity_probability(problem, state, action) -> float:
    """Probability that an opportunity is available after routing action."""
    environment = problem.environment
    task = _task(problem, state)

    return environment.opportunities.probability(
        state,
        task,
        action,
        (),
    )


def terminal_value(problem, state) -> float:
    """Exact terminal value, obtained from the canonical exact solver."""
    return solve_exact_hls(
        problem,
        initial_state=state,
    ).value


def constrained_value(world, target):
    """Solve max J subject to positive probability of reaching target.

    The target is considered reached as soon as the exact WorldState equals
    target.  Once reached, the continuation is the unconstrained exact HLS
    optimum.

    Before target time, each routing action is followed by the stochastic
    opportunity outcome and then an opportunity-contingent development
    decision.  For each opportunity branch we may choose its development
    action independently, exactly as in the original HLS recursion.

    A routing action is feasible for the constrained problem iff the induced
    policy has strictly positive probability of reaching the target.
    """

    problem = world.problem
    environment = problem.environment
    target_key = aia.state_key(target)

    @lru_cache(maxsize=None)
    def recurse(state):
        # ------------------------------------------------------------
        # Constraint already satisfied: use exact unconstrained HLS
        # continuation from here onward.
        # ------------------------------------------------------------
        if aia.state_key(state) == target_key:
            return ConstrainedResult(
                value=solve_exact_hls(
                    problem,
                    initial_state=state,
                ).value,
                reach_probability=1.0,
                action=None,
            )

        # ------------------------------------------------------------
        # Cannot reach a target in the past, or horizon exhausted
        # without satisfying the constraint.
        # ------------------------------------------------------------
        if state.time >= target.time:
            return None

        best = None

        for action in problem.operational_actions:
            task = _task(problem, state)

            immediate_reward = (
                environment.reward.operational_reward(
                    state,
                    task,
                    action,
                )
            )

            p_available = opportunity_probability(
                problem,
                state,
                action,
            )

            branch_specs = (
                (False, 1.0 - p_available),
                (True, p_available),
            )

            expected_continuation = 0.0
            total_reach_probability = 0.0
            feasible = True

            for available, branch_probability in branch_specs:
                if branch_probability <= EXACT_TOL:
                    continue

                opportunity = Opportunity(available)

                decisions = _admissible_development_actions(
                    problem,
                    state,
                    opportunity,
                )

                if not decisions:
                    raise ValueError(
                        "world exposes no resource-admissible "
                        "development action"
                    )

                branch_candidates = []

                for decision in decisions:
                    next_state = _physical_next_state(
                        problem,
                        state,
                        opportunity,
                        decision,
                    )

                    child = recurse(next_state)

                    if child is None:
                        # This development action does not preserve
                        # positive-probability reachability on this branch.
                        #
                        # It can still be used if the target is reached via
                        # another stochastic branch.  Its unconstrained value
                        # must therefore remain available.
                        unconstrained = solve_exact_hls(
                            problem,
                            initial_state=next_state,
                        ).value

                        branch_candidates.append(
                            (
                                -environment.resources.development_cost(
                                    decision
                                )
                                + environment.resources.beta
                                * unconstrained,
                                0.0,
                                decision,
                            )
                        )
                    else:
                        branch_candidates.append(
                            (
                                -environment.resources.development_cost(
                                    decision
                                )
                                + environment.resources.beta
                                * child.value,
                                child.reach_probability,
                                decision,
                            )
                        )

                # Keep all branch-local candidates for now.  The subtle
                # point is that a branch need not itself reach the target:
                # positive reachability may be supplied by another branch.
                #
                # We therefore first select the best unconstrained candidate
                # and the best target-preserving candidate separately.
                best_any = max(
                    branch_candidates,
                    key=lambda item: item[0],
                )

                preserving = [
                    item
                    for item in branch_candidates
                    if item[1] > EXACT_TOL
                ]

                best_preserving = (
                    max(preserving, key=lambda item: item[0])
                    if preserving
                    else None
                )

                # Save both possibilities; combination across O=0/O=1 is
                # handled below.
                if available:
                    true_any = best_any
                    true_preserving = best_preserving
                    p_true = branch_probability
                else:
                    false_any = best_any
                    false_preserving = best_preserving
                    p_false = branch_probability

            # --------------------------------------------------------
            # Combine the two stochastic branches.
            #
            # At least one positive-probability branch must preserve
            # reachability.  Other branches are free to use their exact
            # best continuation.
            # --------------------------------------------------------
            combinations = []

            false_options = []
            true_options = []

            if 'p_false' in locals():
                false_options.append(false_any)
                if (
                    false_preserving is not None
                    and false_preserving != false_any
                ):
                    false_options.append(false_preserving)
            else:
                p_false = 0.0
                false_options.append((0.0, 0.0, None))

            if 'p_true' in locals():
                true_options.append(true_any)
                if (
                    true_preserving is not None
                    and true_preserving != true_any
                ):
                    true_options.append(true_preserving)
            else:
                p_true = 0.0
                true_options.append((0.0, 0.0, None))

            for false_choice in false_options:
                for true_choice in true_options:
                    reach_probability = (
                        p_false * false_choice[1]
                        + p_true * true_choice[1]
                    )

                    if reach_probability <= EXACT_TOL:
                        continue

                    continuation = (
                        p_false * false_choice[0]
                        + p_true * true_choice[0]
                    )

                    total_value = (
                        immediate_reward + continuation
                    )

                    combinations.append(
                        ConstrainedResult(
                            value=total_value,
                            reach_probability=reach_probability,
                            action=action,
                        )
                    )

            # Clean branch-local temporaries before next routing action.
            for name in (
                'p_false',
                'p_true',
                'false_any',
                'true_any',
                'false_preserving',
                'true_preserving',
            ):
                if name in locals():
                    del locals()[name]

            if not combinations:
                feasible = False

            if feasible:
                action_best = max(
                    combinations,
                    key=lambda result: result.value,
                )

                if (
                    best is None
                    or action_best.value > best.value + EXACT_TOL
                ):
                    best = action_best
                elif (
                    best is not None
                    and abs(action_best.value - best.value) <= EXACT_TOL
                    and action_best.reach_probability
                    > best.reach_probability
                ):
                    # Value is the objective.  Reach probability is only
                    # a deterministic tie-breaker.
                    best = action_best

        return best

    return recurse(world.initial_state)


def main():
    world = aia.build_world()
    problem = world.problem

    levels, paths_to = aia.physically_reachable_paths(world)

    inverted_states = []

    for time in range(problem.horizon):
        for state in levels[time].values():
            if aia.routing_inverted(world, state):
                inverted_states.append(state)

    baseline = solve_exact_hls(
        problem,
        initial_state=world.initial_state,
    ).value

    print("RQ0 exact constrained-reachability diagnostic")
    print("---------------------------------------------")
    print("H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5")
    print()
    print(
        "Constraint: P_pi(reach S^dagger) > 0; "
        "all non-target branches remain optimally controlled."
    )
    print()
    print(f"J_HLS(S0) = {baseline:.12f}")
    print()

    rows = []

    for index, target in enumerate(inverted_states, 1):
        result = constrained_value(world, target)

        if result is None:
            raise RuntimeError(
                "physically reachable target was declared infeasible "
                "by constrained recursion"
            )

        cost = baseline - result.value
        gain = arc.inversion_gain(world, target)

        ratio = (
            gain / cost
            if cost > EXACT_TOL
            else float("inf")
        )

        paths = paths_to[aia.state_key(target)]

        print("=" * 78)
        print(
            f"INVERTED STATE {index}/{len(inverted_states)} "
            f"(t={target.time})"
        )
        print(f"competence={target.competence}")
        print(f"resources={target.resources}")
        print(f"physical paths={len(paths)}")
        print()
        print(f"J_HLS(S0)              = {baseline:.12f}")
        print(f"J^->S                  = {result.value:.12f}")
        print(
            f"P_reach under optimizer = "
            f"{result.reach_probability:.12f}"
        )
        print(f"C_reach                = {cost:.12f}")
        print(f"local inversion gain   = {gain:.12f}")
        print(f"gain / C_reach         = {ratio:.12f}")
        print()

        rows.append(
            (
                index,
                result.value,
                result.reach_probability,
                cost,
                gain,
                ratio,
            )
        )

    print("=" * 78)
    print("SUMMARY")
    print("-------")
    print(
        f"{'state':>5} "
        f"{'J_constraint':>16} "
        f"{'P_reach':>14} "
        f"{'C_reach':>14} "
        f"{'gain':>14} "
        f"{'gain/C':>14}"
    )
    print("-" * 86)

    for (
        index,
        value,
        probability,
        cost,
        gain,
        ratio,
    ) in rows:
        print(
            f"{index:>5} "
            f"{value:>16.10f} "
            f"{probability:>14.10f} "
            f"{cost:>14.10f} "
            f"{gain:>14.10f} "
            f"{ratio:>14.10f}"
        )

    print()
    print("Interpretation")
    print("--------------")

    if all(row[3] > EXACT_TOL for row in rows):
        print(
            "Every physically reachable routing inversion has a strictly "
            "positive exact reachability cost from S0."
        )

    if all(row[4] < row[3] - EXACT_TOL for row in rows):
        print(
            "For every target, the local routing-inversion gain is smaller "
            "than the exact global value sacrificed to make that target "
            "reachable."
        )
        print(
            "Thus the observed local inversions are economically dominated "
            "from S0 in this diagnostic world."
        )
    else:
        print(
            "At least one target is not separated from its local inversion "
            "gain by the exact constrained reachability cost; inspect the "
            "state-level results before drawing a structural conclusion."
        )

    print()
    print(
        "This is an exact constrained-policy calculation for the fixed "
        "eta=0.5 diagnostic world.  It is not a claim that G0+C1-C5 is "
        "globally reducible."
    )


if __name__ == "__main__":
    main()
