"""Regression and generality gates for the policy-neutral exact solver."""

import pytest

from hls.synthetic.c1 import (
    reference_worlds,
    solve_hls,
    solve_sep_omega,
    solve_strong_sep,
)
from hls.synthetic.exact import (
    ExactProblem,
    solve_exact_hls,
    solve_exact_sep_omega,
    solve_exact_strong_sep,
)


@pytest.mark.parametrize("world_name", sorted(reference_worlds()))
def test_general_exact_solver_reproduces_c1_hls(world_name):
    world = reference_worlds()[world_name]

    old = solve_hls(world)

    problem = ExactProblem(
        environment=world.environment,
        operational_actions=("M1", "M2"),
        horizon=2,
        terminal_task=world.terminal_task,
    )
    new = solve_exact_hls(problem)

    assert new.value == pytest.approx(old.value)
    assert new.optimal_actions == old.optimal_actions

    for action in ("M1", "M2"):
        assert new.action_values[action] == pytest.approx(
            old.action_values[action]
        )


@pytest.mark.parametrize("world_name", sorted(reference_worlds()))
def test_general_exact_solver_reproduces_c1_strong_sep(world_name):
    world = reference_worlds()[world_name]

    old = solve_strong_sep(world)

    problem = ExactProblem(
        environment=world.environment,
        operational_actions=("M1", "M2"),
        horizon=2,
        terminal_task=world.terminal_task,
    )
    new = solve_exact_strong_sep(problem)

    assert new.value_min == pytest.approx(old.value_min)
    assert new.value_max == pytest.approx(old.value_max)
    assert (
        new.immediate_optimal_actions
        == old.immediate_optimal_actions
    )

    for action in old.action_value_bounds:
        assert new.action_value_bounds[action][0] == pytest.approx(
            old.action_value_bounds[action][0]
        )
        assert new.action_value_bounds[action][1] == pytest.approx(
            old.action_value_bounds[action][1]
        )


@pytest.mark.parametrize("world_name", sorted(reference_worlds()))
def test_general_exact_solver_reproduces_c1_sep_omega(world_name):
    world = reference_worlds()[world_name]

    old = solve_sep_omega(world)

    problem = ExactProblem(
        environment=world.environment,
        operational_actions=("M1", "M2"),
        horizon=2,
        terminal_task=world.terminal_task,
    )
    new = solve_exact_sep_omega(problem)

    assert new.value == pytest.approx(old.value)
    assert new.optimal_actions == old.optimal_actions

    for action in ("M1", "M2"):
        assert new.action_values[action] == pytest.approx(
            old.action_values[action]
        )


def test_exact_solver_supports_m3_with_persistent_budget_and_c4():
    """Generality gate: M=3 exact recursion with C3+C4 world physics."""
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
        ExactProblem,
        solve_exact_hls,
        solve_exact_sep_omega,
        solve_exact_strong_sep,
    )
    from hls.synthetic.randomness import SeededRandomSource

    learners = {"M1": 0, "M2": 1, "M3": 2}
    competences = {1: 0, 2: 1, 3: 2}

    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence((1, 2)),
        competence=BoundedMatrixCompetence((
            (0.90, 0.30, 0.30),
            (0.30, 0.90, 0.30),
            (0.30, 0.30, 0.90),
        )),
        opportunities=A1MixtureOpportunityKernel(
            {1: 1.0, 2: 1.0},
            {
                ("M1", 1): 1.0, ("M2", 1): 1.0, ("M3", 1): 1.0,
                ("M1", 2): 1.0, ("M2", 2): 1.0, ("M3", 2): 1.0,
            },
            rho=0.0,
        ),
        development=CoupledDevelopmentKernel(
            learners,
            competences,
            {0: 2, 1: 3},
            eta=0.5,
            gamma={},
        ),
        reward=CompetenceRewardModel(learners, competences),
        resources=BudgetedDevelopmentResources(
            budget_per_development=1.0,
            beta=1.0,
        ),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )

    s0 = with_development_budget(
        environment.initial_state(),
        1.0,
    )

    problem = ExactProblem(
        environment=environment,
        operational_actions=("M1", "M2", "M3"),
        horizon=2,
        terminal_task=3,
    )

    hls = solve_exact_hls(problem, initial_state=s0)
    sep = solve_exact_strong_sep(problem, initial_state=s0)
    omega = solve_exact_sep_omega(problem, initial_state=s0)

    # All three learners genuinely participate in the exact action space.
    assert set(hls.action_values) == {"M1", "M2", "M3"}

    # The constructive reducibility boundary remains exact.
    assert omega.value == pytest.approx(hls.value)

    # Strong SEP returns a well-defined interval.
    assert sep.value_min <= sep.value_max

    # All exact values are finite and the recursion completed successfully.
    assert hls.value == pytest.approx(float(hls.value))
    assert sep.value_min == pytest.approx(float(sep.value_min))
    assert sep.value_max == pytest.approx(float(sep.value_max))
