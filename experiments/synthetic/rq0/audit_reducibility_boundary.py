"""Audit the routing-reducibility boundary in the frozen RQ0-A/B worlds.

This is a diagnostic experiment, not a new campaign and not a parameter sweep.

For every physically reachable non-terminal state in each of the nine
preregistered worlds, classify reward/opportunity ordering and determine
whether any reward-opportunity conflict is strong enough to invert HLS routing.

No RQ0 world parameter is changed.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import permutations

from hls.synthetic.exact import (
    EXACT_TOL,
    _admissible_development_actions,
    _physical_next_state,
    _task,
    solve_exact_hls,
)
from hls.synthetic.interfaces import DevelopmentDecision, Opportunity
from hls.synthetic.rq0_campaign import worlds
from hls.synthetic.state import WorldState


@dataclass(frozen=True)
class Predecessor:
    state: WorldState
    operational_action: object
    opportunity: bool
    development_action: DevelopmentDecision


@dataclass(frozen=True)
class PairAudit:
    preferred_now: object
    alternative: object
    reward_gap: float
    opportunity_advantage: float
    q_difference: float

    @property
    def misaligned(self) -> bool:
        return (
            self.reward_gap > EXACT_TOL
            and self.opportunity_advantage > EXACT_TOL
        )

    @property
    def routing_inverted(self) -> bool:
        return self.misaligned and self.q_difference > EXACT_TOL


def _state_key(state: WorldState):
    return (
        state.time,
        state.competence,
        state.resources,
    )


def reachable_states(world):
    """Enumerate all physically reachable states, independent of policy.

    Branches with zero probability are not physically reachable.
    Operational actions and all resource-admissible development decisions
    are otherwise explored exhaustively.
    """
    problem = world.problem
    initial = world.initial_state

    levels = defaultdict(dict)
    levels[initial.time][_state_key(initial)] = initial

    predecessor = {_state_key(initial): None}

    for time in range(initial.time, problem.horizon):
        for state in tuple(levels[time].values()):
            task = _task(problem, state)

            for action in problem.operational_actions:
                probability = problem.environment.opportunities.probability(
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
                        key = _state_key(next_state)

                        if key not in levels[next_state.time]:
                            levels[next_state.time][key] = next_state
                            predecessor[key] = Predecessor(
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


def _reward_and_probability(world, state):
    problem = world.problem
    task = _task(problem, state)

    rewards = {}
    probabilities = {}

    for action in problem.operational_actions:
        rewards[action] = problem.environment.reward.operational_reward(
            state,
            task,
            action,
        )
        probabilities[action] = problem.environment.opportunities.probability(
            state,
            task,
            action,
            (),
        )

    return rewards, probabilities


def audit_state(world, state):
    """Audit all ordered action pairs with a strict immediate reward order."""
    solution = solve_exact_hls(
        world.problem,
        initial_state=state,
    )
    rewards, probabilities = _reward_and_probability(world, state)

    audits = []

    for preferred_now, alternative in permutations(
        world.problem.operational_actions, 2
    ):
        reward_gap = rewards[preferred_now] - rewards[alternative]

        if reward_gap <= EXACT_TOL:
            continue

        opportunity_advantage = (
            probabilities[alternative] - probabilities[preferred_now]
        )

        # Positive means HLS prefers the immediately inferior alternative.
        q_difference = (
            solution.action_values[alternative]
            - solution.action_values[preferred_now]
        )

        audits.append(
            PairAudit(
                preferred_now=preferred_now,
                alternative=alternative,
                reward_gap=reward_gap,
                opportunity_advantage=opportunity_advantage,
                q_difference=q_difference,
            )
        )

    return tuple(audits)


def classification(audits):
    if any(audit.routing_inverted for audit in audits):
        return "ROUTING_INVERTED"
    if any(audit.misaligned for audit in audits):
        return "MISALIGNED"
    return "ALIGNED"


def reconstruct_path(state, predecessor):
    path = []
    current = state

    while True:
        pred = predecessor[_state_key(current)]
        if pred is None:
            break
        path.append(pred)
        current = pred.state

    return tuple(reversed(path))


def print_counterexample(world, state, audits, predecessor):
    relevant = [
        audit
        for audit in audits
        if audit.misaligned
    ]

    if not relevant:
        return

    print()
    print("=" * 78)
    print(f"{world.configuration.name}: t={state.time}")
    print(f"competence={state.competence}")
    print(f"resources={state.resources}")
    print(f"classification={classification(audits)}")

    for audit in relevant:
        print(
            f"  {audit.preferred_now}>{audit.alternative}: "
            f"reward_gap={audit.reward_gap:.10f}  "
            f"opportunity_advantage={audit.opportunity_advantage:.10f}  "
            f"Q_alt-Q_now={audit.q_difference:.10f}"
        )

    path = reconstruct_path(state, predecessor)

    print("path:")
    if not path:
        print("  INITIAL STATE")
    else:
        for step, pred in enumerate(path):
            print(
                f"  t={pred.state.time}: "
                f"a={pred.operational_action}, "
                f"O={int(pred.opportunity)}, "
                f"d={pred.development_action}"
            )


def main():
    print(
        f"{'configuration':<18}"
        f"{'reachable':>11}"
        f"{'nonterm':>10}"
        f"{'aligned':>10}"
        f"{'misaligned':>13}"
        f"{'inverted':>11}"
    )
    print("-" * 73)

    global_misaligned = 0
    global_inverted = 0

    details = []

    for world in worlds():
        states, predecessor = reachable_states(world)

        counts = {
            "ALIGNED": 0,
            "MISALIGNED": 0,
            "ROUTING_INVERTED": 0,
        }

        nonterminal = [
            state
            for state in states
            if state.time < world.problem.horizon
        ]

        for state in nonterminal:
            audits = audit_state(world, state)
            label = classification(audits)
            counts[label] += 1

            if label != "ALIGNED":
                details.append(
                    (world, state, audits, predecessor)
                )

        global_misaligned += counts["MISALIGNED"]
        global_inverted += counts["ROUTING_INVERTED"]

        print(
            f"{world.configuration.name:<18}"
            f"{len(states):>11}"
            f"{len(nonterminal):>10}"
            f"{counts['ALIGNED']:>10}"
            f"{counts['MISALIGNED']:>13}"
            f"{counts['ROUTING_INVERTED']:>11}"
        )

    print()
    print(
        "TOTAL boundary states: "
        f"misaligned={global_misaligned}, "
        f"routing_inverted={global_inverted}"
    )

    for world, state, audits, predecessor in details:
        print_counterexample(
            world,
            state,
            audits,
            predecessor,
        )


if __name__ == "__main__":
    main()
