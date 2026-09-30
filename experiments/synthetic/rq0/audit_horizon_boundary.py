"""Diagnostic horizon extension of the frozen central RQ0-B world."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import permutations

from hls.synthetic.c3 import (
    BudgetedDevelopmentResources,
    remaining_budget,
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
from hls.synthetic.interfaces import DevelopmentDecision, Opportunity
from hls.synthetic.randomness import SeededRandomSource
from hls.synthetic.rq0_campaign import (
    BETA,
    ETA,
    LEARNERS,
    LEARNER_INDICES,
    TASKS,
    TASK_INDICES,
    competence_matrix,
)
from hls.synthetic.state import WorldState


S = 0.5
GAMMA = 0.0
RHO = 0.5

BASELINE_OPPORTUNITY = {1: 0.5, 2: 0.5, 3: 0.5}
BUDGET_PER_DEVELOPMENT = 1.0

DIAGNOSTIC_LADDER = (
    (2, 1),
    (3, 2),
    (4, 3),
)


@dataclass(frozen=True)
class DiagnosticConfiguration:
    horizon: int
    budget: int
    operational_tasks: tuple[int, ...]
    terminal_task: int
    target_by_time: dict[int, int]


@dataclass(frozen=True)
class DiagnosticWorld:
    configuration: DiagnosticConfiguration
    environment: SyntheticEnvironment
    initial_state: WorldState
    problem: ExactProblem


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


def cyclic_schedule(horizon: int):
    sequence = tuple(TASKS[t % len(TASKS)] for t in range(horizon + 1))
    operational_tasks = sequence[:-1]
    terminal_task = sequence[-1]
    target_by_time = {t: sequence[t + 1] for t in range(horizon)}
    return operational_tasks, terminal_task, target_by_time


def executor_values(initial_competence):
    return {
        (learner, task):
            initial_competence[LEARNER_INDICES[learner]][TASK_INDICES[task]]
        for learner in LEARNERS
        for task in TASKS
    }


def build_diagnostic_world(horizon: int, budget: int) -> DiagnosticWorld:
    operational_tasks, terminal_task, target_by_time = cyclic_schedule(horizon)
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

    return DiagnosticWorld(
        configuration=DiagnosticConfiguration(
            horizon=horizon,
            budget=budget,
            operational_tasks=operational_tasks,
            terminal_task=terminal_task,
            target_by_time=target_by_time,
        ),
        environment=environment,
        initial_state=initial_state,
        problem=problem,
    )


def _state_key(state):
    return state.time, state.competence, state.resources


def reachable_states(world):
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
                    state, task, action, ()
                )

                for available, branch_probability in (
                    (False, 1.0 - probability),
                    (True, probability),
                ):
                    if branch_probability <= EXACT_TOL:
                        continue

                    opportunity = Opportunity(available)

                    for decision in _admissible_development_actions(
                        problem, state, opportunity
                    ):
                        next_state = _physical_next_state(
                            problem, state, opportunity, decision
                        )
                        key = _state_key(next_state)

                        if key not in levels[next_state.time]:
                            levels[next_state.time][key] = next_state
                            predecessor[key] = Predecessor(
                                state,
                                action,
                                available,
                                decision,
                            )

    states = tuple(
        state
        for time in sorted(levels)
        for state in levels[time].values()
    )
    return states, predecessor


def reward_and_probability(world, state):
    problem = world.problem
    task = _task(problem, state)

    rewards = {}
    probabilities = {}

    for action in problem.operational_actions:
        rewards[action] = problem.environment.reward.operational_reward(
            state, task, action
        )
        probabilities[action] = problem.environment.opportunities.probability(
            state, task, action, ()
        )

    return rewards, probabilities


def audit_state(world, state):
    solution = solve_exact_hls(world.problem, initial_state=state)
    rewards, probabilities = reward_and_probability(world, state)
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
        q_difference = (
            solution.action_values[alternative]
            - solution.action_values[preferred_now]
        )

        audits.append(
            PairAudit(
                preferred_now,
                alternative,
                reward_gap,
                opportunity_advantage,
                q_difference,
            )
        )

    return tuple(audits)


def classification(audits):
    if any(a.routing_inverted for a in audits):
        return "ROUTING_INVERTED"
    if any(a.misaligned for a in audits):
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


def print_state_detail(world, state, audits, predecessor):
    relevant = [a for a in audits if a.misaligned]
    if not relevant:
        return

    print()
    print("=" * 88)
    print(
        f"H={world.configuration.horizon}, "
        f"B={world.configuration.budget}, "
        f"t={state.time}, "
        f"remaining_B={remaining_budget(state):.1f}"
    )
    print(f"competence={state.competence}")
    print(f"classification={classification(audits)}")

    for audit in relevant:
        print(
            f"  {audit.preferred_now}>{audit.alternative}: "
            f"Delta_R={audit.reward_gap:.10f}  "
            f"Delta_p={audit.opportunity_advantage:.10f}  "
            f"Q_alt-Q_now={audit.q_difference:.10f}"
        )

    print("path:")
    path = reconstruct_path(state, predecessor)

    if not path:
        print("  INITIAL STATE")
    else:
        for pred in path:
            print(
                f"  t={pred.state.time}: "
                f"a={pred.operational_action}, "
                f"O={int(pred.opportunity)}, "
                f"d={pred.development_action}"
            )


def main():
    print("RQ0 horizon-boundary diagnostic")
    print(
        f"Fixed: s={S}, eta={ETA}, gamma={GAMMA}, rho={RHO}; B=H-1"
    )
    print()

    print(
        f"{'H':>3}{'B':>4}{'reachable':>12}{'nonterm':>10}"
        f"{'aligned':>10}{'misaligned':>13}{'inverted':>11}"
        f"{'min_Qdiff':>14}{'max_Qdiff':>14}{'J_HLS-J_SEP':>15}"
    )
    print("-" * 106)

    details = []

    for horizon, budget in DIAGNOSTIC_LADDER:
        world = build_diagnostic_world(horizon, budget)
        states, predecessor = reachable_states(world)

        nonterminal = [
            state for state in states
            if state.time < horizon
        ]

        counts = {
            "ALIGNED": 0,
            "MISALIGNED": 0,
            "ROUTING_INVERTED": 0,
        }
        misaligned_qdiffs = []

        for state in nonterminal:
            audits = audit_state(world, state)
            label = classification(audits)
            counts[label] += 1

            relevant = [a for a in audits if a.misaligned]

            if relevant:
                misaligned_qdiffs.extend(
                    a.q_difference for a in relevant
                )
                details.append((world, state, audits, predecessor))

        hls = solve_exact_hls(
            world.problem,
            initial_state=world.initial_state,
        )
        sep = solve_exact_strong_sep(
            world.problem,
            initial_state=world.initial_state,
        )

        delta_j_cons = hls.value - sep.value_max

        if misaligned_qdiffs:
            min_text = f"{min(misaligned_qdiffs):.10f}"
            max_text = f"{max(misaligned_qdiffs):.10f}"
        else:
            min_text = "-"
            max_text = "-"

        print(
            f"{horizon:>3}{budget:>4}"
            f"{len(states):>12}{len(nonterminal):>10}"
            f"{counts['ALIGNED']:>10}"
            f"{counts['MISALIGNED']:>13}"
            f"{counts['ROUTING_INVERTED']:>11}"
            f"{min_text:>14}{max_text:>14}"
            f"{delta_j_cons:>15.10f}"
        )

    print()
    print("MISALIGNED / ROUTING_INVERTED states")

    for world, state, audits, predecessor in details:
        print_state_detail(world, state, audits, predecessor)


if __name__ == "__main__":
    main()
