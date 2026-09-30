"""One-factor audit of the RQ0 routing-reducibility boundary.

Diagnostic experiment following the B-REDUCIBLE initial RQ0-A/B campaign.

Question:
Can already implemented G0+C1--C5 mechanisms cross the analytically
identified routing boundary

    chi = Delta_p * Delta_V / Delta_R = 1

without adding a new simulator capability?

Three one-factor interventions are evaluated around the clean H=3 extension
of B*:

    rho : opportunity coupling
    eta : development strength
    s   : portfolio specialization

All other world semantics are held fixed.

This is a causal boundary diagnostic, not a blind parameter search and not
a new RQ0 campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

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
    _terminal_value,
    solve_exact_hls,
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

from audit_horizon_boundary import (
    DiagnosticConfiguration,
    DiagnosticWorld,
    cyclic_schedule,
    reachable_states,
)


HORIZON = 3
BUDGET = 2
GAMMA = 0.0

BASE_S = 0.5
BASE_ETA = 0.75
BASE_RHO = 0.5

BASELINE_OPPORTUNITY = {1: 0.5, 2: 0.5, 3: 0.5}
BUDGET_PER_DEVELOPMENT = 1.0

# Deliberately simple one-dimensional diagnostic ladders.
# These are not an optimization grid.
RHO_VALUES = (0.0, 0.25, 0.5, 0.75, 1.0)
ETA_VALUES = (0.25, 0.5, 0.75, 1.0)
S_VALUES = (0.0, 0.25, 0.5, 0.75, 1.0)


@dataclass(frozen=True)
class ConflictAudit:
    factor: str
    factor_value: float
    state: WorldState
    preferred_now: object
    alternative: object
    delta_r: float
    delta_p: float
    v0: float
    v1: float
    delta_v: float
    chi: float
    q_difference: float

    @property
    def inverted(self) -> bool:
        return self.q_difference > EXACT_TOL


def executor_values(initial_competence):
    return {
        (learner, task):
            initial_competence[
                LEARNER_INDICES[learner]
            ][TASK_INDICES[task]]
        for learner in LEARNERS
        for task in TASKS
    }


def build_factor_world(
    *,
    s: float = BASE_S,
    eta: float = BASE_ETA,
    rho: float = BASE_RHO,
) -> DiagnosticWorld:
    """Build the clean H=3, B=2 diagnostic world with one-factor variation."""
    operational_tasks, terminal_task, target_by_time = cyclic_schedule(HORIZON)
    initial_competence = competence_matrix(s)

    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence(operational_tasks),
        competence=BoundedMatrixCompetence(initial_competence),
        opportunities=A1MixtureOpportunityKernel(
            BASELINE_OPPORTUNITY,
            executor_values(initial_competence),
            rho=rho,
        ),
        development=CoupledDevelopmentKernel(
            LEARNER_INDICES,
            TASK_INDICES,
            target_by_time,
            eta=eta,
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
        float(BUDGET),
    )

    problem = ExactProblem(
        environment=environment,
        operational_actions=LEARNERS,
        horizon=HORIZON,
        terminal_task=terminal_task,
    )

    return DiagnosticWorld(
        configuration=DiagnosticConfiguration(
            horizon=HORIZON,
            budget=BUDGET,
            operational_tasks=operational_tasks,
            terminal_task=terminal_task,
            target_by_time=target_by_time,
        ),
        environment=environment,
        initial_state=initial_state,
        problem=problem,
    )


def conditional_development_value(
    world,
    state,
    available: bool,
) -> float:
    """Optimal post-routing value conditional on opportunity outcome."""
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


def audit_world(world, factor, factor_value):
    states, _ = reachable_states(world)
    audits = []

    for state in states:
        if state.time >= world.problem.horizon:
            continue

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

        probabilities = {
            action: environment.opportunities.probability(
                state,
                task,
                action,
                (),
            )
            for action in problem.operational_actions
        }

        solution = solve_exact_hls(
            problem,
            initial_state=state,
        )

        # Conditional opportunity values are executor-independent under
        # the current G0 semantics, so compute them once per state.
        v0 = conditional_development_value(
            world,
            state,
            False,
        )
        v1 = conditional_development_value(
            world,
            state,
            True,
        )
        delta_v = v1 - v0

        for preferred_now, alternative in permutations(
            problem.operational_actions,
            2,
        ):
            delta_r = (
                rewards[preferred_now]
                - rewards[alternative]
            )

            if delta_r <= EXACT_TOL:
                continue

            delta_p = (
                probabilities[alternative]
                - probabilities[preferred_now]
            )

            # We only audit genuine reward/opportunity conflicts.
            if delta_p <= EXACT_TOL:
                continue

            chi = delta_p * delta_v / delta_r

            q_difference = (
                solution.action_values[alternative]
                - solution.action_values[preferred_now]
            )

            # Internal consistency check of the derived factorization:
            #
            # Q_b - Q_a = -Delta_R + Delta_p * Delta_V.
            reconstructed = (
                -delta_r
                + delta_p * delta_v
            )

            if abs(q_difference - reconstructed) > 1e-10:
                raise AssertionError(
                    "Q factorization failed: "
                    f"observed={q_difference}, "
                    f"reconstructed={reconstructed}"
                )

            audits.append(
                ConflictAudit(
                    factor=factor,
                    factor_value=factor_value,
                    state=state,
                    preferred_now=preferred_now,
                    alternative=alternative,
                    delta_r=delta_r,
                    delta_p=delta_p,
                    v0=v0,
                    v1=v1,
                    delta_v=delta_v,
                    chi=chi,
                    q_difference=q_difference,
                )
            )

    return tuple(audits)


def world_for(factor, value):
    if factor == "rho":
        return build_factor_world(rho=value)
    if factor == "eta":
        return build_factor_world(eta=value)
    if factor == "s":
        return build_factor_world(s=value)
    raise ValueError(factor)


def summarize(factor, value, audits):
    if not audits:
        return {
            "factor": factor,
            "value": value,
            "conflicts": 0,
            "max_delta_v": float("nan"),
            "max_chi": float("nan"),
            "inverted": 0,
            "max_qdiff": float("nan"),
        }

    return {
        "factor": factor,
        "value": value,
        "conflicts": len(audits),
        "max_delta_v": max(a.delta_v for a in audits),
        "max_chi": max(a.chi for a in audits),
        "inverted": sum(a.inverted for a in audits),
        "max_qdiff": max(a.q_difference for a in audits),
    }


def main():
    experiments = (
        ("rho", RHO_VALUES),
        ("eta", ETA_VALUES),
        ("s", S_VALUES),
    )

    print("RQ0 one-factor routing-boundary diagnostic")
    print(
        "Fixed H=3, B=2, gamma=0; "
        "vary one implemented G0+C1-C5 factor at a time"
    )
    print()

    print(
        f"{'factor':<8}"
        f"{'value':>8}"
        f"{'conflicts':>12}"
        f"{'max_DeltaV':>15}"
        f"{'max_chi':>13}"
        f"{'inverted':>11}"
        f"{'max_Qdiff':>15}"
    )
    print("-" * 82)

    all_audits = []

    for factor, values in experiments:
        for value in values:
            world = world_for(factor, value)
            audits = audit_world(
                world,
                factor,
                value,
            )
            all_audits.extend(audits)
            row = summarize(
                factor,
                value,
                audits,
            )

            if row["conflicts"] == 0:
                print(
                    f"{factor:<8}"
                    f"{value:>8.2f}"
                    f"{0:>12}"
                    f"{'--':>15}"
                    f"{'--':>13}"
                    f"{0:>11}"
                    f"{'--':>15}"
                )
            else:
                print(
                    f"{factor:<8}"
                    f"{value:>8.2f}"
                    f"{row['conflicts']:>12}"
                    f"{row['max_delta_v']:>15.10f}"
                    f"{row['max_chi']:>13.10f}"
                    f"{row['inverted']:>11}"
                    f"{row['max_qdiff']:>15.10f}"
                )

    print()

    if not all_audits:
        print("No reward/opportunity conflicts found.")
        return

    boundary = max(
        all_audits,
        key=lambda audit: audit.chi,
    )

    print("Global boundary maximizer")
    print("-------------------------")
    print(
        f"factor={boundary.factor}, "
        f"value={boundary.factor_value}"
    )
    print(
        f"H={HORIZON}, "
        f"t={boundary.state.time}"
    )
    print(
        f"{boundary.preferred_now}>"
        f"{boundary.alternative}"
    )
    print(f"competence={boundary.state.competence}")
    print(f"resources={boundary.state.resources}")
    print(f"Delta_R={boundary.delta_r:.10f}")
    print(f"Delta_p={boundary.delta_p:.10f}")
    print(f"V0={boundary.v0:.10f}")
    print(f"V1={boundary.v1:.10f}")
    print(f"Delta_V={boundary.delta_v:.10f}")
    print(f"chi={boundary.chi:.10f}")
    print(f"Q_alt-Q_now={boundary.q_difference:.10f}")

    inverted = [
        audit
        for audit in all_audits
        if audit.inverted
    ]

    print()
    print("Routing-boundary verdict")
    print("------------------------")

    if not inverted:
        print("NO ROUTING INVERSION FOUND")
        print(
            f"max_chi={boundary.chi:.10f} < 1"
        )
        print(
            "No one-factor intervention crossed the routing "
            "reducibility boundary."
        )
    else:
        first = min(
            inverted,
            key=lambda audit: (
                ("rho", "eta", "s").index(audit.factor),
                audit.factor_value,
                audit.state.time,
            ),
        )

        print("ROUTING INVERSION FOUND")
        print(
            f"factor={first.factor}, "
            f"value={first.factor_value}"
        )
        print(
            f"t={first.state.time}, "
            f"{first.preferred_now}>"
            f"{first.alternative}"
        )
        print(f"Delta_R={first.delta_r:.10f}")
        print(f"Delta_p={first.delta_p:.10f}")
        print(f"Delta_V={first.delta_v:.10f}")
        print(f"chi={first.chi:.10f}")
        print(
            f"Q_alt-Q_now={first.q_difference:.10f}"
        )


if __name__ == "__main__":
    main()
