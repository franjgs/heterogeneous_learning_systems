"""Contract tests for exogenous environment/problem generation."""

from dataclasses import replace

import pytest

from hls.discover_v0 import production_inputs
from hls.hls_lab_dynamic import DemandRegime, LearningProfile
from hls.hls_lab_v1 import evaluate_problem, make_team
from hls.hls_lab_v1_environment import (
    ExogenousEnvironmentConfig,
    generate_environment_trajectory,
)
from hls.hls_lab_v1_integrated import (
    P0ProductionOnly,
    P1FixedTeaching,
    TeachingEfficacy,
    TeachingParameters,
    compare_integrated_policies,
)
from hls.synthetic.c5 import MarkovTaskDemand, NonStationaryTaskDemand, StationaryTaskDemand


SPECIALIST_0 = DemandRegime("specialist-0", ((0.7, 0.1),), (1.0,))
SPECIALIST_1 = DemandRegime("specialist-1", ((0.1, 0.7),), (1.0,))
COMPLEMENTARY = DemandRegime("complementary", ((0.5, 0.5),), (1.0,))


def _switching_config(horizon=8):
    process = MarkovTaskDemand(
        {"early": 1.0, "late": 0.0},
        {"early": {"early": 0.0, "late": 1.0},
         "late": {"early": 0.0, "late": 1.0}},
    )
    return ExogenousEnvironmentConfig(
        process,
        {"early": SPECIALIST_0, "late": SPECIALIST_1},
        horizon,
        resource_budget=2.0,
    )


def test_frozen_environment_is_reproducible_and_exogenous_to_team_state():
    config = _switching_config()
    first = generate_environment_trajectory(config, seed=817)
    repeated = generate_environment_trajectory(config, seed=817)
    # The generator interface has no organization/team argument; arbitrary
    # policy-side state cannot enter the already generated trajectory.
    unrelated_team = make_team(((1.0, 0.0), (0.0, 1.0), (0.2, 0.2)))
    after_team_change = generate_environment_trajectory(config, seed=817)
    assert first == repeated == after_team_change
    assert len(first.problems) == config.horizon
    assert unrelated_team.real_matrix != make_team(((0.1, 0.1),) * 3).real_matrix


def test_two_policies_receive_identical_frozen_exogenous_trajectory():
    trajectory = generate_environment_trajectory(_switching_config(), seed=41)
    team = make_team(((0.7, 0.2), (0.2, 0.7), (0.3, 0.3)))
    efficacy = TeachingEfficacy(tuple(
        tuple((0.0, 0.0) if i == j else (0.4, 0.4) for j in range(3))
        for i in range(3)
    ))
    policies = (P0ProductionOnly(), P1FixedTeaching((0, 1, 0)))
    results = compare_integrated_policies(
        team, trajectory.problems, policies,
        learning=LearningProfile(((0.1, 0.1),) * 3),
        teaching_efficacy=efficacy,
        parameters=TeachingParameters(outcome_noise_sd=0.0),
        seed=19,
    )
    for result in results:
        assert tuple(record.problem_id for record in result.records) == tuple(
            problem.problem.problem_id for problem in trajectory.problems
        )
        assert tuple(record.requirements for record in result.records) == tuple(
            problem.problem.requirements for problem in trajectory.problems
        )


def test_policy_view_never_contains_latent_environment_state():
    class InspectingPolicy:
        name = "INSPECTING"

        def choose(self, view, memory, parameters):
            assert not hasattr(view, "latent_state")
            assert not hasattr(view, "environment_state")
            assert not hasattr(view, "theta")
            return P0ProductionOnly().choose(view, memory, parameters)

    trajectory = generate_environment_trajectory(_switching_config(2), seed=2)
    efficacy = TeachingEfficacy(tuple(
        tuple((0.0, 0.0) if i == j else (0.2, 0.2) for j in range(3))
        for i in range(3)
    ))
    compare_integrated_policies(
        make_team(((0.4, 0.2), (0.2, 0.4), (0.2, 0.2))),
        trajectory.problems, (InspectingPolicy(),),
        learning=LearningProfile(((0.1, 0.1),) * 3),
        teaching_efficacy=efficacy, seed=3,
    )


def test_problem_families_have_structural_requirements_and_regimes():
    config = _switching_config(6)
    trajectory = generate_environment_trajectory(config, seed=5)
    assert trajectory.latent_states == ("early", "late", "late", "late", "late", "late")
    assert trajectory.problems[0].problem.requirements[0] > trajectory.problems[0].problem.requirements[1]
    assert all(p.problem.requirements[1] > p.problem.requirements[0]
               for p in trajectory.problems[1:])
    # Regime change is in the emitted demand distribution, not merely a label.
    assert trajectory.problems[0].problem.requirements != trajectory.problems[1].problem.requirements

    recurrent_process = MarkovTaskDemand(
        {"repeat": 1.0}, {"repeat": {"repeat": 1.0}}
    )
    recurrent = generate_environment_trajectory(
        ExogenousEnvironmentConfig(recurrent_process, {"repeat": COMPLEMENTARY}, 5), seed=9
    )
    assert len({p.problem.requirements for p in recurrent.problems}) == 1
    assert recurrent.problems[0].problem.requirements == (0.5, 0.5)

    # Novelty is operational: this requirement vector has not occurred earlier.
    vectors = [p.problem.requirements for p in trajectory.problems]
    assert vectors[1] not in vectors[:1]


def test_complementary_task_requires_both_competence_dimensions():
    team = make_team(((1.0, 0.0), (0.0, 1.0), (0.0, 0.0)))
    joint_outputs = production_inputs(team.real_matrix, ((1, 0), (0, 1), (0, 0)))
    assert evaluate_problem(joint_outputs, (0.8, 0.8)).success
    assert not evaluate_problem((1.0, 0.0), (0.8, 0.8)).success
    assert not evaluate_problem((0.0, 1.0), (0.8, 0.8)).success


def test_teaching_cannot_rewrite_frozen_future_problems():
    trajectory = generate_environment_trajectory(_switching_config(5), seed=101)
    before = trajectory.problems
    team = make_team(((0.7, 0.2), (0.2, 0.7), (0.3, 0.3)))
    efficacy = TeachingEfficacy(tuple(
        tuple((0.0, 0.0) if i == j else (0.5, 0.5) for j in range(3))
        for i in range(3)
    ))
    result = compare_integrated_policies(
        team, trajectory.problems, (P1FixedTeaching((0, 1, 1)),),
        learning=LearningProfile(((0.01, 0.01),) * 3),
        teaching_efficacy=efficacy,
        parameters=TeachingParameters(outcome_noise_sd=0.0), seed=71,
    )[0]
    assert any(record.action.teaching is not None for record in result.records)
    # Teaching executes only after the trajectory has been generated and
    # cannot mutate that frozen environment output.
    assert isinstance(trajectory.problems, tuple)
    assert trajectory.problems is before
    assert len(trajectory.problems) == 5
    assert tuple(trajectory.latent_states[1:]) == ("late",) * 4


def test_environment_configuration_is_frozen_and_validated():
    config = _switching_config(3)
    with pytest.raises(TypeError):
        config.emissions["late"] = SPECIALIST_0
    with pytest.raises(ValueError):
        replace(config, resource_budget=float("nan"))


def test_existing_stationary_and_time_varying_c5_processes_are_reused():
    stationary = generate_environment_trajectory(
        ExogenousEnvironmentConfig(
            StationaryTaskDemand({"steady": 1.0}),
            {"steady": COMPLEMENTARY}, 3,
        ),
        seed=12,
    )
    assert stationary.latent_states == ("steady",) * 3
    assert all(item.problem.requirements == (0.5, 0.5) for item in stationary.problems)

    time_varying = generate_environment_trajectory(
        ExogenousEnvironmentConfig(
            NonStationaryTaskDemand({
                0: {"skill0": 1.0}, 1: {"skill1": 1.0}, 2: {"skill1": 1.0},
            }),
            {"skill0": SPECIALIST_0, "skill1": SPECIALIST_1}, 3,
        ),
        seed=12,
    )
    assert time_varying.latent_states == ("skill0", "skill1", "skill1")
    assert tuple(item.problem.requirements for item in time_varying.problems) == (
        (0.7, 0.1), (0.1, 0.7), (0.1, 0.7),
    )
    with pytest.raises(ValueError, match="no distribution"):
        ExogenousEnvironmentConfig(
            NonStationaryTaskDemand({0: {"skill0": 1.0}}),
            {"skill0": SPECIALIST_0}, 2,
        )
