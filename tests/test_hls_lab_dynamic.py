"""Focused tests for the additive nonstationary HLS v1 extension."""

import pytest

from hls.discover_develop_v2 import capability_after_exposure, eta_to_lambda
from hls.discover_v0 import JOINT_ACTIONS
from hls.hls_lab_dynamic import (
    CompetenceInformationMode,
    DemandRegime,
    DiscoverBeliefPolicy,
    LearningProfile,
    UncertainProblem,
    advance_team,
    compare_belief_policies,
    compare_organizations,
    generate_problems,
    make_dynamic_team,
    run_belief_sequence,
    run_dynamic_sequence,
)
from hls.hls_lab_v1 import (
    ExploreThenGreedy,
    ExpertState,
    GreedyAdaptive,
    ProblemSpec,
    TeamState,
    make_team,
)
from hls.discover_v0 import THETA_1, THETA_2


TEAM = ((0.82, 0.12), (0.18, 0.76), (0.35, 0.28))
RATES = LearningProfile(((0.10, 0.20), (0.70, 0.30), (0.40, 0.60)))


def test_dynamic_problem_stream_is_reproducible_and_regime_changes():
    low = DemandRegime("low-first-axis", ((0.7, 0.0), (0.0, 0.7)), (0.9, 0.1))
    high = DemandRegime("high-first-axis", ((0.7, 0.0), (0.0, 0.7)), (0.1, 0.9))
    schedule = ((low, 20), (high, 20))
    first = generate_problems(schedule, seed=410)
    assert first == generate_problems(schedule, seed=410)
    assert len(first) == 40
    first_axis_early = sum(p.requirements == (0.7, 0.0) for p in first[:20])
    first_axis_late = sum(p.requirements == (0.7, 0.0) for p in first[20:])
    assert first_axis_early > first_axis_late


def test_cell_rates_reuse_mis_v2_exponential_law_and_li_off_freezes_skills():
    team = make_team(TEAM)
    action = JOINT_ACTIONS[37]
    updated = advance_team(team, action, RATES, enabled=True)
    for i in range(3):
        for k in range(2):
            expected = capability_after_exposure(
                TEAM[i][k], action[i][k], rate=eta_to_lambda(RATES.eta[i][k])
            )
            assert updated.experts[i].competence_real[k] == pytest.approx(expected)
    frozen = advance_team(team, action, RATES, enabled=False)
    assert frozen.real_matrix == team.real_matrix
    assert frozen.experts[0].experience != team.experts[0].experience


def test_paired_policies_share_external_problems_and_evolve_own_histories():
    east = DemandRegime("east", ((0.8, 0.0), (0.0, 0.8)), (0.85, 0.15))
    west = DemandRegime("west", ((0.8, 0.0), (0.0, 0.8)), (0.15, 0.85))
    problems = generate_problems(((east, 18), (west, 18)), seed=52, budget=1.0)
    initial = make_team(TEAM)
    adaptive, learned = compare_organizations(
        initial,
        problems,
        ((GreedyAdaptive(), False), (ExploreThenGreedy(), True)),
        learning=RATES,
        seed=52,
    )

    assert len(adaptive.records) == len(learned.records) == 36
    assert [r.problem_id for r in adaptive.records] == [r.problem_id for r in learned.records]
    assert [r.requirements for r in adaptive.records] == [r.requirements for r in learned.records]
    assert all(r.budget == 1.0 for r in adaptive.records + learned.records)
    assert all(r.action in JOINT_ACTIONS for r in adaptive.records + learned.records)
    assert adaptive.records[0].competence_before == learned.records[0].competence_before == TEAM
    assert adaptive.final_organization.update_count == 0
    assert learned.final_organization.update_count == 36
    assert adaptive.final_team != learned.final_team
    assert adaptive.final_team != initial and learned.final_team != initial
    assert adaptive.records[-1].cumulative_successes == sum(r.success for r in adaptive.records)
    assert learned.records[-1].cumulative_successes == sum(r.success for r in learned.records)
    assert adaptive.records[-1].competence_after == adaptive.final_team.real_matrix
    assert learned.records[-1].competence_after == learned.final_team.real_matrix


def test_learning_profile_requires_three_by_two_eta_values():
    with pytest.raises(ValueError):
        LearningProfile(((0.2, 0.3), (0.2, 0.3)))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        LearningProfile(((0.2, 0.3), (0.2, 0.3), (0.2, 1.0)))


def test_belief_execution_reuses_discover_and_resets_at_problem_boundaries():
    initial = make_team(TEAM)
    problems = (
        UncertainProblem(ProblemSpec("A", (0.35, 0.0), 3.0), THETA_1),
        UncertainProblem(ProblemSpec("B", (0.0, 0.35), 3.0), THETA_2),
    )
    policy = DiscoverBeliefPolicy(sigma=0.03, quadrature_order=3)
    run = run_belief_sequence(
        initial, problems, policy, learning=RATES,
        decision_horizon=2, individual_learning=True,
        prior=0.5, sigma=0.03, noise_seed=12,
    )

    assert len(run.records) == 4
    assert [r.decision_in_problem for r in run.records] == [0, 1, 0, 1]
    assert run.records[0].belief_before == pytest.approx(0.5)
    assert run.records[0].belief_after != pytest.approx(0.5)
    assert run.records[0].belief_after == pytest.approx(run.records[1].belief_before)
    assert run.records[2].belief_before == pytest.approx(0.5)
    assert run.records[2].belief_after == pytest.approx(run.records[3].belief_before)
    assert run.records[0].true_environment_type == "theta1"
    assert run.records[2].true_environment_type == "theta2"
    assert run.records[0].episode.competence_after == run.records[1].episode.competence_before
    assert run.records[1].episode.competence_after == run.records[2].episode.competence_before
    assert not hasattr(run.records[0].episode, "theta")


def test_real_and_estimated_competencies_remain_separate_and_h1_is_compatible():
    real = ((0.7, 0.2), (0.2, 0.7), (0.3, 0.3))
    estimate = ((0.6, 0.25), (0.25, 0.65), (0.35, 0.25))
    initial = TeamState(tuple(
        ExpertState(f"E{i}", real[i], estimate[i]) for i in range(3)
    ))
    problem = ProblemSpec("known-task", (0.25, 0.0), 3.0)
    policy = GreedyAdaptive()
    old_run = run_dynamic_sequence(
        initial, (problem,), policy, learning=RATES,
        individual_learning=True, seed=9,
    )
    hidden = (UncertainProblem(problem, THETA_1),)
    new_run = run_belief_sequence(
        initial, hidden, policy, learning=RATES, decision_horizon=1,
        individual_learning=True, noise_seed=9, seed=9,
        information_mode=CompetenceInformationMode.PARTIAL,
    )
    old_step, new_step = old_run.records[0], new_run.records[0].episode
    assert new_step.action == old_step.action
    assert new_step.outputs == old_step.outputs
    assert new_step.competence_before == real
    assert new_step.estimated_before == estimate
    assert new_step.competence_after != new_step.estimated_after


def test_oracle_and_partial_team_construction_are_explicit_and_separate():
    real = ((0.8, 0.2), (0.2, 0.8), (0.4, 0.4))
    estimate = ((0.3, 0.7), (0.7, 0.3), (0.5, 0.5))
    oracle = make_dynamic_team(
        real, information_mode=CompetenceInformationMode.ORACLE
    )
    partial = make_dynamic_team(
        real, information_mode=CompetenceInformationMode.PARTIAL,
        estimated_competencies=estimate,
    )
    assert oracle.real_matrix == oracle.estimated_matrix == real
    assert partial.real_matrix == real
    assert partial.estimated_matrix == estimate
    with pytest.raises(ValueError, match="explicit initial estimate"):
        make_dynamic_team(real, information_mode=CompetenceInformationMode.PARTIAL)


def test_partial_information_policy_receives_no_real_competencies_and_does_not_fake_update():
    real = ((0.8, 0.2), (0.2, 0.8), (0.4, 0.4))
    estimate = ((0.3, 0.7), (0.7, 0.3), (0.5, 0.5))
    initial = make_dynamic_team(
        real, information_mode=CompetenceInformationMode.PARTIAL,
        estimated_competencies=estimate,
    )

    class InspectingPolicy:
        name = "inspect_estimate_only"

        def choose(self, view, state):
            assert view.estimated_competencies == estimate
            assert not hasattr(view, "competence_real")
            assert not hasattr(view, "true_environment_type")
            return view.feasible_actions[-1]

    item = UncertainProblem(ProblemSpec("partial", (0.2, 0.0), 3.0), THETA_1)
    run = run_belief_sequence(
        initial, (item,), InspectingPolicy(), learning=RATES,
        decision_horizon=1, individual_learning=True,
        noise_seed=20, information_mode=CompetenceInformationMode.PARTIAL,
    )
    assert run.information_mode == "PARTIAL"
    assert run.final_team.real_matrix != real
    assert run.final_team.estimated_matrix == estimate
    assert run.records[0].episode.estimated_before == estimate
    assert run.records[0].episode.competence_before == real


def test_action_choices_change_observed_reward_information_under_shared_streams():
    real = ((0.85, 0.2), (0.2, 0.8), (0.4, 0.35))
    estimate = ((0.3, 0.7), (0.7, 0.3), (0.5, 0.5))
    initial = make_dynamic_team(
        real, information_mode=CompetenceInformationMode.PARTIAL,
        estimated_competencies=estimate,
    )
    items = tuple(
        UncertainProblem(ProblemSpec("same", (0.2, 0.2), 3.0), theta)
        for theta in (THETA_1, THETA_2, THETA_1)
    )
    runs = compare_belief_policies(
        initial, items,
        (GreedyAdaptive(), DiscoverBeliefPolicy(sigma=0.03, quadrature_order=3)),
        learning=LearningProfile(((0.2, 0.2), (0.2, 0.2), (0.2, 0.2))),
        decision_horizon=2, sigma=0.03, noise_seed=44, seed=2,
        information_mode=CompetenceInformationMode.PARTIAL,
    )
    greedy, discover = runs
    assert [r.observation_noise for r in greedy.records] == [
        r.observation_noise for r in discover.records
    ]
    assert [r.episode.action for r in greedy.records] != [
        r.episode.action for r in discover.records
    ]
    assert [r.belief_after for r in greedy.records] != [
        r.belief_after for r in discover.records
    ]
    assert greedy.final_team.real_matrix != discover.final_team.real_matrix
    assert greedy.final_team.estimated_matrix == discover.final_team.estimated_matrix == estimate


def test_paired_discover_policies_share_problem_and_noise_streams():
    problem = UncertainProblem(ProblemSpec("paired", (0.3, 0.0), 3.0), THETA_2)
    runs = compare_belief_policies(
        make_team(TEAM), (problem,),
        (DiscoverBeliefPolicy(quadrature_order=3), GreedyAdaptive()),
        learning=RATES, decision_horizon=2, sigma=0.1,
        noise_seed=85, seed=3,
    )
    assert len(runs) == 2
    assert [r.observation_noise for r in runs[0].records] == [
        r.observation_noise for r in runs[1].records
    ]
    assert all(r.problem_episode == 0 for result in runs for r in result.records)
    assert all(r.episode.problem_id == "paired" for result in runs for r in result.records)
    assert all(r.episode.action in JOINT_ACTIONS for result in runs for r in result.records)
