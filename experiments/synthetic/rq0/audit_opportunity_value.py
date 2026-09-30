"""Audit opportunity value at the RQ0 routing-reducibility boundary.

Diagnostic only.  This experiment does not modify G0 physics, policy
semantics, the exact solver, or the preregistered RQ0-A/B campaign.

For the clean horizon extensions H=2,3,4 of B*, with B=H-1, it tests the
executor-independent opportunity-value decomposition

    Q(S,b) - Q(S,a)
      = -(R_a - R_b) + (p_b - p_a) * DeltaV(S)

for every physically reachable reward/opportunity-conflict state, where

    R_a > R_b,
    p_b > p_a,

and

    DeltaV(S) = V_1(S) - V_0(S)

is the optimal continuation-value increment from an available development
opportunity.

The normalized boundary ratio is

    chi = (p_b - p_a) * DeltaV / (R_a - R_b).

Thus chi > 1 is exactly the routing-inversion condition under the audited
executor-independent opportunity semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from math import inf

from hls.synthetic.exact import (
    _terminal_value,
    EXACT_TOL,
    _admissible_development_actions,
    _physical_next_state,
    _task,
    solve_exact_hls,
)
from hls.synthetic.interfaces import Opportunity

# Reuse the already constructed clean B* horizon extensions and exhaustive
# physical reachability logic.  This file is diagnostic; it must not define
# a second, potentially inconsistent horizon-extension world family.
from audit_horizon_boundary import (
    build_diagnostic_world,
    reachable_states,
)


@dataclass(frozen=True)
class ConflictAudit:
    horizon: int
    state: object
    preferred_now: object
    alternative: object
    reward_gap: float
    probability_gap: float
    value_no_opportunity: float
    value_opportunity: float
    delta_v: float
    q_difference: float
    reconstructed_q_difference: float
    chi: float

    @property
    def inverted(self) -> bool:
        return self.q_difference > EXACT_TOL


def _conditional_development_value(world, state, available: bool) -> float:
    """Optimal post-routing continuation conditional on opportunity outcome.

    This is the term inside the Bernoulli expectation in the exact HLS
    recursion, excluding the current operational reward.

    Crucially, no operational action is passed here.  If this function
    correctly reconstructs every Q difference, the current world semantics
    have executor-independent opportunity content conditional on O.
    """
    problem = world.problem
    environment = problem.environment
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

    values = []

    for decision in decisions:
        next_state = _physical_next_state(
            problem,
            state,
            opportunity,
            decision,
        )

        if next_state.time == problem.horizon:
            continuation = _terminal_value(
                problem,
                next_state,
            )
        else:
            continuation = solve_exact_hls(
                problem,
                initial_state=next_state,
            ).value

        values.append(
            -environment.resources.development_cost(decision)
            + environment.resources.beta * continuation
        )

    return max(values)


def _reward_probability_maps(world, state):
    problem = world.problem
    environment = problem.environment
    task = _task(problem, state)

    rewards = {}
    probabilities = {}

    for action in problem.operational_actions:
        rewards[action] = environment.reward.operational_reward(
            state,
            task,
            action,
        )
        probabilities[action] = environment.opportunities.probability(
            state,
            task,
            action,
            (),
        )

    return rewards, probabilities


def audit_conflicts(world, horizon):
    """Audit all reachable strict reward/opportunity conflicts."""
    states, _ = reachable_states(world)

    audits = []

    for state in states:
        if state.time >= world.problem.horizon:
            continue

        solution = solve_exact_hls(
            world.problem,
            initial_state=state,
        )

        rewards, probabilities = _reward_probability_maps(
            world,
            state,
        )

        v0 = _conditional_development_value(
            world,
            state,
            False,
        )
        v1 = _conditional_development_value(
            world,
            state,
            True,
        )
        delta_v = v1 - v0

        for preferred_now, alternative in permutations(
            world.problem.operational_actions,
            2,
        ):
            reward_gap = (
                rewards[preferred_now]
                - rewards[alternative]
            )
            probability_gap = (
                probabilities[alternative]
                - probabilities[preferred_now]
            )

            if reward_gap <= EXACT_TOL:
                continue
            if probability_gap <= EXACT_TOL:
                continue

            q_difference = (
                solution.action_values[alternative]
                - solution.action_values[preferred_now]
            )

            reconstructed = (
                -reward_gap
                + probability_gap * delta_v
            )

            if abs(q_difference - reconstructed) > 1e-10:
                raise AssertionError(
                    "executor-independent opportunity-value decomposition "
                    "does not reconstruct exact Q difference: "
                    f"H={horizon}, t={state.time}, "
                    f"{preferred_now}>{alternative}, "
                    f"exact={q_difference:.16g}, "
                    f"reconstructed={reconstructed:.16g}"
                )

            chi = (
                probability_gap * delta_v / reward_gap
            )

            audits.append(
                ConflictAudit(
                    horizon=horizon,
                    state=state,
                    preferred_now=preferred_now,
                    alternative=alternative,
                    reward_gap=reward_gap,
                    probability_gap=probability_gap,
                    value_no_opportunity=v0,
                    value_opportunity=v1,
                    delta_v=delta_v,
                    q_difference=q_difference,
                    reconstructed_q_difference=reconstructed,
                    chi=chi,
                )
            )

    return tuple(audits)


def _print_maximizer(audit):
    print()
    print("Boundary maximizer")
    print("------------------")
    print(
        f"H={audit.horizon}, "
        f"t={audit.state.time}, "
        f"{audit.preferred_now}>{audit.alternative}"
    )
    print(f"competence={audit.state.competence}")
    print(f"resources={audit.state.resources}")
    print(f"Delta_R={audit.reward_gap:.10f}")
    print(f"Delta_p={audit.probability_gap:.10f}")
    print(f"V0={audit.value_no_opportunity:.10f}")
    print(f"V1={audit.value_opportunity:.10f}")
    print(f"Delta_V={audit.delta_v:.10f}")
    print(f"chi={audit.chi:.10f}")
    print(f"Q_alt-Q_now={audit.q_difference:.10f}")
    print(
        "reconstructed_Qdiff="
        f"{audit.reconstructed_q_difference:.10f}"
    )


def main():
    print("RQ0 opportunity-value diagnostic")
    print(
        "Fixed B* geometry/physics; clean horizon extension; B=H-1"
    )
    print()

    print(
        f"{'H':>3}"
        f"{'conflicts':>12}"
        f"{'max_DeltaV':>15}"
        f"{'max_chi':>15}"
        f"{'inverted':>11}"
        f"{'max_Qdiff':>15}"
    )
    print("-" * 71)

    all_audits = []

    for horizon in (2, 3, 4):
        world = build_diagnostic_world(horizon, horizon - 1)
        audits = audit_conflicts(world, horizon)
        all_audits.extend(audits)

        if audits:
            max_delta_v = max(a.delta_v for a in audits)
            max_chi = max(a.chi for a in audits)
            inverted = sum(a.inverted for a in audits)
            max_qdiff = max(a.q_difference for a in audits)
        else:
            max_delta_v = float("nan")
            max_chi = float("nan")
            inverted = 0
            max_qdiff = float("nan")

        print(
            f"{horizon:>3}"
            f"{len(audits):>12}"
            f"{max_delta_v:>15.10f}"
            f"{max_chi:>15.10f}"
            f"{inverted:>11}"
            f"{max_qdiff:>15.10f}"
        )

    if not all_audits:
        print()
        print("No strict reward/opportunity conflicts found.")
        return

    maximizer = max(
        all_audits,
        key=lambda audit: audit.chi,
    )
    _print_maximizer(maximizer)

    max_chi = maximizer.chi

    print()
    print("Diagnostic conclusion")
    print("---------------------")

    if max_chi > 1.0 + EXACT_TOL:
        print(
            "C1-C5 cross the routing-inversion boundary: "
            "executor-independent opportunity content is sufficient "
            "in at least one audited reachable state."
        )
    elif abs(max_chi - 1.0) <= EXACT_TOL:
        print(
            "C1-C5 reach the routing-inversion boundary within "
            "numerical tolerance."
        )
    else:
        print(
            "No audited conflict crosses the routing-inversion boundary."
        )
        print(
            f"Observed supremum over H=2,3,4: chi={max_chi:.10f} < 1."
        )
        print(
            "This is evidence of reducibility over the audited horizon "
            "family, not yet a global impossibility theorem for C1-C5."
        )


if __name__ == "__main__":
    main()
