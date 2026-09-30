"""Causal diagnostic of future relevant-demand persistence for RQ0.

Question
--------
Can persistence of future demand for a competence already created turn a
physically reachable local routing inversion into an HLS-optimal-reachable
routing inversion, without changing G0 physics or any other world parameter?

Fixed:
    M=3, K=3
    s=0.5
    eta=0.5
    gamma=0
    rho=0.5
    beta=1

Intervention:
    Preserve the diagnostic prefix that produced the eta=0.5 local inversion,
    then append L additional operational demands for task 3.

The development target during the persistence tail remains task 3.  Thus this
is a diagnostic intervention on persistence of relevant demand, not a new
development mechanism.

This is not a parameter search for HLS advantage.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import audit_horizon_boundary as hb
import audit_eta05_nonseparability as eta05

from hls.synthetic.c3 import (
    BudgetedDevelopmentResources,
    with_development_budget,
)
from hls.synthetic.c4 import CoupledDevelopmentKernel
from hls.synthetic.components import (
    A1MixtureOpportunityKernel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
    FiniteTaskSequence,
)
from hls.synthetic.environment import SyntheticEnvironment
from hls.synthetic.exact import (
    EXACT_TOL,
    ExactProblem,
    _admissible_development_actions,
    _physical_next_state,
    _task,
    solve_exact_hls,
    solve_exact_strong_sep,
)
from hls.synthetic.interfaces import Opportunity
from hls.synthetic.randomness import SeededRandomSource
from hls.synthetic.rq0_campaign import (
    BETA,
    LEARNERS,
    LEARNER_INDICES,
    TASKS,
    TASK_INDICES,
    competence_matrix,
)
from hls.synthetic.state import WorldState


S = 0.5
ETA = 0.5
GAMMA = 0.0
RHO = 0.5

# Keep enough budget that persistence is not confounded with an arbitrarily
# tighter resource constraint as the horizon grows.
#
# One development opportunity per operational cycle is the non-binding
# analogue of the earlier H=3, B=2 diagnostic.
BASE_PREFIX_BUDGET = 2

TAIL_LENGTHS = (0, 1, 2, 3)

BASELINE_OPPORTUNITY = {
    1: 0.5,
    2: 0.5,
    3: 0.5,
}

BUDGET_PER_DEVELOPMENT = 1.0


@dataclass(frozen=True)
class PersistenceWorld:
    tail_length: int
    environment: SyntheticEnvironment
    initial_state: WorldState
    problem: ExactProblem


def state_key(state):
    return state.time, state.competence, state.resources


def executor_values(initial_competence):
    return {
        (learner, task):
            initial_competence[
                LEARNER_INDICES[learner]
            ][
                TASK_INDICES[task]
            ]
        for learner in LEARNERS
        for task in TASKS
    }


def build_world(tail_length: int) -> PersistenceWorld:
    """Build the eta=.5 world plus a task-3 persistence tail.

    L=0 reproduces the H=3 eta=.5 diagnostic:
        operational tasks = (1, 2, 3)
        terminal task     = 1

    For L>0:
        operational tasks = (1, 2, 3, 3, ..., 3)
        terminal task     = 1

    The first two development targets remain exactly those of the original
    cyclic construction:
        t=0 -> task 2
        t=1 -> task 3

    From t=2 onward, development continues to target task 3.  Therefore the
    competence whose future relevance is being extended is also the competence
    exposed to the existing development physics.
    """
    if tail_length < 0:
        raise ValueError("tail_length must be non-negative")

    operational_tasks = (1, 2, 3) + (3,) * tail_length
    horizon = len(operational_tasks)

    # Preserve the old H=3 terminal convention.  Only the operational
    # persistence tail is manipulated.
    terminal_task = 1

    # Preserve exactly the eta=.5 H=3 diagnostic prefix.
    #
    # cyclic_schedule(3) gives:
    #   operational tasks = (1, 2, 3)
    #   terminal task     = 1
    #   targets           = {0: 2, 1: 3, 2: 1}
    #
    # Only cycles appended by the persistence intervention target task 3.
    target_by_time = {
        0: 2,
        1: 3,
        2: 1,
    }

    for time in range(3, horizon):
        target_by_time[time] = 3

    initial_competence = competence_matrix(S)

    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence(operational_tasks),
        competence=BoundedMatrixCompetence(initial_competence),
        opportunities=A1MixtureOpportunityKernel(
            BASELINE_OPPORTUNITY,
            executor_values(initial_competence),
            rho=RHO,
        ),
        development=CoupledDevelopmentKernel(
            LEARNER_INDICES,
            TASK_INDICES,
            target_by_time,
            eta=ETA,
            gamma={},
        ),
        reward=CompetenceRewardModel(
            LEARNER_INDICES,
            TASK_INDICES,
        ),
        resources=BudgetedDevelopmentResources(
            budget_per_development=BUDGET_PER_DEVELOPMENT,
            beta=BETA,
        ),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )

    # Preserve B=2 at L=0 and add one unit for every added cycle.
    # This prevents the intervention from silently increasing scarcity.
    budget = BASE_PREFIX_BUDGET + tail_length

    initial_state = with_development_budget(
        environment.initial_state(),
        float(budget),
    )

    problem = ExactProblem(
        environment=environment,
        operational_actions=LEARNERS,
        horizon=horizon,
        terminal_task=terminal_task,
    )

    return PersistenceWorld(
        tail_length=tail_length,
        environment=environment,
        initial_state=initial_state,
        problem=problem,
    )


def physically_reachable_states(world):
    """Enumerate all positive-probability physically reachable states."""
    problem = world.problem
    environment = problem.environment

    levels = defaultdict(dict)
    initial = world.initial_state
    levels[initial.time][state_key(initial)] = initial

    for time in range(initial.time, problem.horizon):
        for state in tuple(levels[time].values()):
            task = _task(problem, state)

            for action in problem.operational_actions:
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

                        levels[next_state.time][
                            state_key(next_state)
                        ] = next_state

    return tuple(
        state
        for time in sorted(levels)
        for state in levels[time].values()
    )


def continuation_value(problem, state):
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


def optimal_development_actions(problem, state, available):
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
            * continuation_value(problem, next_state)
        )

    best = max(values.values())

    return tuple(
        decision
        for decision, value in values.items()
        if abs(value - best) <= EXACT_TOL
    )


def optimal_reachable_states(world):
    """All states reachable under any exact HLS-optimal continuation."""
    problem = world.problem
    environment = problem.environment

    levels = defaultdict(dict)
    initial = world.initial_state

    levels[initial.time][state_key(initial)] = initial

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

                    for decision in optimal_development_actions(
                        problem,
                        state,
                        available,
                    ):
                        next_state = _physical_next_state(
                            problem,
                            state,
                            Opportunity(available),
                            decision,
                        )

                        levels[next_state.time][
                            state_key(next_state)
                        ] = next_state

    return tuple(
        state
        for time in sorted(levels)
        for state in levels[time].values()
    )


def routing_inversion_gain(world, state):
    """HLS advantage over the best immediate-reward-optimal routing action.

    Positive iff every immediate-reward-optimal action is strictly worse
    than the best exact HLS action.
    """
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

    greedy = tuple(
        action
        for action, reward in rewards.items()
        if abs(reward - best_reward) <= EXACT_TOL
    )

    best_hls = max(solution.action_values.values())
    best_greedy_q = max(
        solution.action_values[action]
        for action in greedy
    )

    gain = best_hls - best_greedy_q

    if gain <= EXACT_TOL:
        return 0.0

    return gain


def main():
    print("RQ0 relevant-demand persistence diagnostic")
    print("------------------------------------------")
    print(
        "Fixed: s=0.5, eta=0.5, gamma=0, rho=0.5, beta=1"
    )
    print(
        "Intervention: append L operational task-3 demands; "
        "all other physics fixed."
    )
    print()

    print(
        f"{'L':>3} "
        f"{'H':>3} "
        f"{'reachable':>10} "
        f"{'inverted':>9} "
        f"{'opt_inv':>8} "
        f"{'max_Ginv':>13} "
        f"{'J_HLS':>14} "
        f"{'J_SEP_max':>14} "
        f"{'Delta_cons':>13}"
    )
    print("-" * 96)

    first_optimal_inversion = None
    first_positive_delta = None

    for tail_length in TAIL_LENGTHS:
        world = build_world(tail_length)
        problem = world.problem

        physical = physically_reachable_states(world)
        optimal = optimal_reachable_states(world)

        physical_nonterminal = tuple(
            state
            for state in physical
            if state.time < problem.horizon
        )

        optimal_nonterminal = tuple(
            state
            for state in optimal
            if state.time < problem.horizon
        )

        inverted = tuple(
            (state, routing_inversion_gain(world, state))
            for state in physical_nonterminal
            if routing_inversion_gain(world, state) > EXACT_TOL
        )

        opt_inverted = tuple(
            (state, routing_inversion_gain(world, state))
            for state in optimal_nonterminal
            if routing_inversion_gain(world, state) > EXACT_TOL
        )

        max_gain = max(
            (gain for _, gain in inverted),
            default=0.0,
        )

        hls = solve_exact_hls(
            problem,
            initial_state=world.initial_state,
        )

        sep = solve_exact_strong_sep(
            problem,
            initial_state=world.initial_state,
        )

        delta_cons = hls.value - sep.value_max

        print(
            f"{tail_length:>3} "
            f"{problem.horizon:>3} "
            f"{len(physical):>10} "
            f"{len(inverted):>9} "
            f"{len(opt_inverted):>8} "
            f"{max_gain:>13.10f} "
            f"{hls.value:>14.10f} "
            f"{sep.value_max:>14.10f} "
            f"{delta_cons:>13.10f}"
        )

        if opt_inverted and first_optimal_inversion is None:
            first_optimal_inversion = (
                tail_length,
                opt_inverted,
            )

        if (
            delta_cons > EXACT_TOL
            and first_positive_delta is None
        ):
            first_positive_delta = (
                tail_length,
                delta_cons,
            )

    print()
    print("Boundary summary")
    print("----------------")

    if first_optimal_inversion is None:
        print(
            "No HLS-optimal-reachable routing inversion found "
            "on the tested persistence ladder."
        )
    else:
        tail_length, states = first_optimal_inversion
        best_state, best_gain = max(
            states,
            key=lambda item: item[1],
        )

        print(
            "First HLS-optimal-reachable routing inversion:"
        )
        print(f"  L={tail_length}")
        print(f"  t={best_state.time}")
        print(f"  competence={best_state.competence}")
        print(f"  resources={best_state.resources}")
        print(f"  G_inv={best_gain:.12f}")

    if first_positive_delta is None:
        print(
            "No positive conservative integration value found "
            "on the tested persistence ladder."
        )
    else:
        tail_length, delta = first_positive_delta
        print(
            "First positive conservative integration value:"
        )
        print(f"  L={tail_length}")
        print(f"  Delta_cons={delta:.12f}")

    print()
    print("Interpretation guard")
    print("--------------------")
    print(
        "The primary boundary is optimal-reachable routing inversion, "
        "not positive Delta_cons."
    )
    print(
        "A positive Delta_cons, if observed, is a subsequent consequence "
        "to be audited rather than the target used to construct the world."
    )


if __name__ == "__main__":
    main()
