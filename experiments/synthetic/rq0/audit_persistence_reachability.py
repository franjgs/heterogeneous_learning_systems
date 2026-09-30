"""Exact reachability barrier along the relevant-demand persistence intervention.

Goal
----
For each preregistered diagnostic persistence level L = 0,1,2,3:

1. build exactly the world used by audit_demand_persistence.py;
2. enumerate physically reachable non-terminal states;
3. select the routing-inverted state with maximum local inversion gain G_inv;
4. solve the exact constrained-reachability problem for that state;
5. compare G_inv with the exact global reachability cost

       C_reach = J_HLS(S0) - J^{->S}.

This is a causal diagnostic for RQ0.  It does not search world parameters,
modify physics, or optimize for positive integration value.
"""

from __future__ import annotations

import audit_demand_persistence as adp
import audit_constrained_reachability as acr

from hls.synthetic.exact import EXACT_TOL, solve_exact_hls


TAIL_LENGTHS = (0, 1, 2, 3)


def main():
    print("RQ0 persistence/reachability-barrier diagnostic")
    print("-----------------------------------------------")
    print(
        "Fixed: s=0.5, eta=0.5, gamma=0, rho=0.5, beta=1"
    )
    print(
        "For each L: target = physically reachable routing inversion "
        "with maximum local G_inv."
    )
    print()

    print(
        f"{'L':>3} "
        f"{'H':>3} "
        f"{'t*':>3} "
        f"{'G_inv':>14} "
        f"{'J_HLS':>14} "
        f"{'J^->S':>14} "
        f"{'C_reach':>14} "
        f"{'G/C':>12} "
        f"{'P_reach':>12}"
    )
    print("-" * 110)

    rows = []

    for tail_length in TAIL_LENGTHS:
        world = adp.build_world(tail_length)
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
            print(
                f"{tail_length:>3} "
                f"{problem.horizon:>3} "
                f"{'--':>3} "
                f"{'--':>14} "
                f"{'--':>14} "
                f"{'--':>14} "
                f"{'--':>14} "
                f"{'--':>12} "
                f"{'--':>12}"
            )
            continue

        # Primary target: maximum local routing-inversion gain.
        #
        # Deterministic secondary ordering is used only if several states
        # have the same gain within numerical tolerance.
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

        baseline = solve_exact_hls(
            problem,
            initial_state=world.initial_state,
        ).value

        constrained = acr.constrained_value(
            world,
            target,
        )

        if constrained is None:
            raise RuntimeError(
                f"L={tail_length}: maximum-G_inv target is physically "
                "reachable but constrained solver declared it infeasible"
            )

        cost = baseline - constrained.value

        if cost > EXACT_TOL:
            ratio = gain / cost
        elif abs(cost) <= EXACT_TOL:
            ratio = float("inf")
        else:
            raise RuntimeError(
                f"L={tail_length}: negative reachability cost "
                f"{cost:.12g}"
            )

        print(
            f"{tail_length:>3} "
            f"{problem.horizon:>3} "
            f"{target.time:>3} "
            f"{gain:>14.10f} "
            f"{baseline:>14.10f} "
            f"{constrained.value:>14.10f} "
            f"{cost:>14.10f} "
            f"{ratio:>12.8f} "
            f"{constrained.reach_probability:>12.8f}"
        )

        rows.append(
            (
                tail_length,
                target,
                gain,
                baseline,
                constrained.value,
                cost,
                ratio,
                constrained.reach_probability,
                len(maximizers),
            )
        )

    print()
    print("Target details")
    print("--------------")

    for (
        tail_length,
        target,
        gain,
        baseline,
        constrained_value,
        cost,
        ratio,
        reach_probability,
        n_maximizers,
    ) in rows:
        print()
        print(f"L={tail_length}, H={tail_length + 3}")
        print(f"t*={target.time}")
        print(f"competence={target.competence}")
        print(f"resources={target.resources}")
        print(f"max-G_inv tied states={n_maximizers}")
        print(f"G_inv={gain:.12f}")
        print(f"C_reach={cost:.12f}")
        print(f"G_inv/C_reach={ratio:.12f}")
        print(f"P_reach={reach_probability:.12f}")

    print()
    print("RQ0 interpretation guard")
    print("------------------------")
    print(
        "This experiment asks whether increasing persistence of future "
        "relevant demand closes the exact global reachability barrier "
        "for the strongest local routing inversion."
    )
    print(
        "G_inv increasing is not by itself evidence of integration value."
    )
    print(
        "The key diagnostic is the evolution of G_inv/C_reach and whether "
        "C_reach reaches zero."
    )
    print(
        "No additional L values or world parameters should be introduced "
        "from this script merely to obtain a favorable HLS result."
    )


if __name__ == "__main__":
    main()
