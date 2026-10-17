"""Focused behavioral invariants for the integrated HLS v1 mechanisms."""

import pytest

from experiments.synthetic.hls_lab_v1.behavioral_plausibility import (
    MIS, PARAMS, RELATION, _efficacy, _problem, run_plausibility_checks,
)
from hls.discover_develop_v2 import capability_after_exposure, mis_v2_transition
from hls.discover_v0 import JOINT_ACTIONS, ces_reward, production_inputs
from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_v1 import ProblemSpec, evaluate_problem, feasible_actions, make_team
from hls.hls_lab_v1_environment import (
    ExogenousEnvironmentConfig, generate_environment_trajectory,
)
from hls.hls_lab_v1_integrated import (
    IntegratedAction, P0ProductionOnly, P2AdaptiveTeaching, TeachingEfficacy,
    TeachingEvent, TeachingParameters, enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)
from hls.synthetic.c5 import NonStationaryTaskDemand


def _forced_teaching(team, event, efficacy, *, production=((0.0, 0.0),) * 3,
                     learning=None, individual_learning=False):
    problem = _problem(0, event.capability, 1.0)
    action = IntegratedAction(production, event)
    return run_integrated_sequence(
        team, (problem,), P0ProductionOnly(),
        learning=learning or MIS, teaching_efficacy=efficacy,
        parameters=PARAMS, individual_learning=individual_learning,
        organizational_learning=False, seed=91, first_action_override=action,
    )


def _custom_efficacy(value_for):
    return TeachingEfficacy(tuple(tuple(tuple(
        0.0 if teacher == learner else value_for(teacher, learner, skill)
        for skill in range(2)) for learner in range(3)) for teacher in range(3)))


def test_production_competence_specialization_complementarity_and_missing_skill():
    base = ((0.2, 0.1), (0.2, 0.1), (0.9, 0.2))
    higher = ((0.2, 0.1), (0.2, 0.1), (1.0, 0.2))
    action = ((0.0, 0.0), (0.0, 0.0), (1.0, 0.0))
    assert production_inputs(higher, action)[0] > production_inputs(base, action)[0]

    skill0_problem = ProblemSpec("s0", (0.8, 0.0), 2.0)
    skill1_problem = ProblemSpec("s1", (0.0, 0.8), 2.0)
    specialist0 = make_team(((1, 0), (0.2, 0.2), (0.2, 0.2)))
    specialist1 = make_team(((0, 1), (0.2, 0.2), (0.2, 0.2)))
    best0 = max(production_inputs(specialist0.real_matrix, a)[0]
                for a in feasible_actions(skill0_problem))
    best1 = max(production_inputs(specialist1.real_matrix, a)[0]
                for a in feasible_actions(skill0_problem))
    assert best0 > best1
    assert not evaluate_problem((0.0, 0.8), (0.8, 0.8)).success

    complementary_team = make_team(((1, 0), (0, 1), (0, 0)))
    joint = ((1, 0), (0, 1), (0, 0))
    assert evaluate_problem(production_inputs(complementary_team.real_matrix, joint),
                            (0.8, 0.8)).success
    assert not evaluate_problem((1.0, 0.0), (0.8, 0.8)).success
    assert not evaluate_problem((0.0, 1.0), (0.8, 0.8)).success
    missing_skill_team = make_team(((0.9, 0.0), (0.4, 0.0), (0.2, 0.0)))
    missing_skill_problem = ProblemSpec("essential-skill-missing", (0.5, 0.2), 2.0)
    assert all(not evaluate_problem(production_inputs(missing_skill_team.real_matrix, a),
                                    missing_skill_problem.requirements).success
               for a in feasible_actions(missing_skill_problem))


def test_more_budget_does_not_reduce_best_achievable_ces_and_catalogue_is_discrete():
    team = make_team(((0.9, 0.4), (0.5, 0.7), (0.3, 0.2)))
    low = feasible_actions(ProblemSpec("low", (0.4, 0.4), 1.0))
    high = feasible_actions(ProblemSpec("high", (0.4, 0.4), 2.0))
    low_best = max(ces_reward(production_inputs(team.real_matrix, a), (0.5, 0.5)) for a in low)
    high_best = max(ces_reward(production_inputs(team.real_matrix, a), (0.5, 0.5)) for a in high)
    assert high_best >= low_best
    assert {sum(map(sum, action)) for action in JOINT_ACTIONS} == {0.0, 1.0, 2.0, 3.0}


def test_exact_shared_resource_accounting_and_residual_from_discrete_catalogue():
    problem = ProblemSpec("resource-ledger", (0.5, 0.0), 2.0,
                          max_effort_per_expert=1.0, resource_cost_per_unit=0.2)
    production = ((0.0, 0.0), (0.0, 0.0), (1.0, 0.0))
    lesson = TeachingEvent(0, 1, 0, 0.25)
    action = IntegratedAction(production, lesson)
    assert action in enumerate_feasible_integrated_actions(problem, teaching_effort=0.25)
    run = run_integrated_sequence(
        make_team(((0.2, 0.2), (0.2, 0.2), (0.9, 0.2))),
        (_problem(1, 0, 0.5),), P0ProductionOnly(), learning=MIS,
        teaching_efficacy=_efficacy(0.0), parameters=PARAMS,
        individual_learning=False, organizational_learning=False,
        first_action_override=action,
    )
    row = run.records[0]
    assert row.production_effort == pytest.approx(1.0)
    assert row.teaching_effort == pytest.approx(0.5)
    assert row.total_resource_used == pytest.approx(1.5)
    assert 2.0 - row.total_resource_used == pytest.approx(0.5)
    assert row.resource_cost == pytest.approx(0.3)
    no_teach_max = max(sum(map(sum, candidate)) for candidate in feasible_actions(problem))
    assert no_teach_max == 2.0
    assert no_teach_max - row.production_effort == 1.0  # productive effort displaced


def test_mis_v2_learning_is_relevant_bounded_saturating_and_disabled_exactly():
    state = ((0.4, 0.6), (0.2, 0.3), (1.0, 0.5))
    action = ((1.0, 0.0), (0.0, 0.0), (0.5, 0.5))
    enabled = mis_v2_transition(state, action, enabled=True, eta=0.2)
    assert enabled[0][0] == pytest.approx(0.52)
    assert enabled[0][1] == state[0][1]
    assert enabled[1] == state[1]
    assert enabled[2][0] == 1.0
    twice = mis_v2_transition(enabled, action, enabled=True, eta=0.2)
    assert twice[0][0] == pytest.approx(0.616)
    assert all(0.0 <= value <= 1.0 for row in twice for value in row)
    assert mis_v2_transition(state, action, enabled=False, eta=0.2) == state
    # MIS-v2 rejects eta=0 by contract; the no-learning control is enabled=False.
    with pytest.raises(ValueError, match="strictly inside"):
        LearningProfile(((0.0, 0.2),) * 3)
    assert capability_after_exposure(0.4, 0.0, rate=0.3) == 0.4


def test_directed_teaching_targets_only_learner_cell_and_respects_relation_efficacy():
    team = make_team(((0.8, 0.2), (0.2, 0.3), (0.4, 0.5)))
    efficacy = _custom_efficacy(lambda i, j, k: 0.8 if (i, j, k) == (0, 1, 0) else 0.1)
    event = TeachingEvent(0, 1, 0, 0.25)
    result = _forced_teaching(team, event, efficacy)
    gain = result.records[0].teaching_gain_real
    assert gain == pytest.approx(0.75 * 0.25 * 0.8 * (1 - 0.2))
    assert result.final_team.real_matrix[1][0] == pytest.approx(0.2 + gain)
    assert result.final_team.real_matrix[0] == team.real_matrix[0]
    assert result.final_team.real_matrix[1][1] == team.real_matrix[1][1]

    other_teacher = _forced_teaching(team, TeachingEvent(2, 1, 0, 0.25), efficacy)
    assert other_teacher.records[0].teaching_gain_real < gain
    lower = _forced_teaching(team, event, _custom_efficacy(
        lambda i, j, k: 0.4 if (i, j, k) == (0, 1, 0) else 0.1))
    assert lower.records[0].teaching_gain_real < gain
    zero = _forced_teaching(team, event, _efficacy(0.0))
    assert zero.records[0].teaching_gain_real == 0.0
    assert zero.final_team.real_matrix == team.real_matrix
    near_bound = make_team(((0.8, 0.2), (0.999, 0.3), (0.4, 0.5)))
    bounded = _forced_teaching(near_bound, event, _efficacy(1.0))
    assert bounded.final_team.real_matrix[1][0] <= 1.0
    assert bounded.final_team.real_matrix[1][0] == pytest.approx(0.9991875)
    ordinary = _forced_teaching(team, event, _efficacy(1.0))
    assert ordinary.records[0].teaching_gain_real > bounded.records[0].teaching_gain_real


def test_teaching_effort_is_charged_when_efficacy_zero_and_mis_is_separable():
    team = make_team(((0.8, 0.2), (0.2, 0.3), (0.4, 0.5)))
    production = ((0.0, 0.0), (0.0, 0.0), (1.0, 0.0))
    event = TeachingEvent(0, 1, 0, 0.25)
    zero = _forced_teaching(team, event, _efficacy(0.0), production=production,
        learning=LearningProfile(((0.1, 0.1),) * 3), individual_learning=True)
    row = zero.records[0]
    assert row.teaching_gain_real == 0.0
    assert row.teaching_effort == 0.5
    assert row.competence_real_after[2][0] > row.competence_real_before[2][0]  # MIS-v2 only
    assert row.competence_real_after[1][0] == row.competence_real_before[1][0]

    positive = _forced_teaching(team, event, _efficacy(0.8), production=production,
        learning=LearningProfile(((0.1, 0.1),) * 3), individual_learning=True)
    assert positive.records[0].competence_real_after[1][0] > team.real_matrix[1][0]
    assert positive.records[0].competence_real_after[2][0] == row.competence_real_after[2][0]


def test_p2_declines_teaching_when_current_requirements_are_already_met():
    team = make_team(((0.9, 0.2), (0.85, 0.2), (0.8, 0.2)))
    problem = _problem(0, 0, 1.0)
    from experiments.synthetic.hls_lab_v1.behavioral_plausibility import _snapshot, _view
    snapshot = _snapshot(team.real_matrix)
    selected = P2AdaptiveTeaching((RELATION,)).choose(
        _view(snapshot, problem, 24), snapshot.organization_memory, PARAMS)
    assert selected.teaching is None


def test_behavioral_scenarios_show_conditional_benefit_and_harm_without_tuning():
    result = run_plausibility_checks()
    scenarios = result["scenarios"]
    assert result["adequate_p2_teaches"] is False
    assert scenarios["S2_persistent_deficit_early_effective"]["delta_v_h"] > 0
    assert scenarios["S3_short_horizon"]["delta_v_h"] < 0
    assert scenarios["S4_weak_teaching"]["delta_v_h"] < 0
    assert scenarios["S6_demand_regime_change"]["delta_v_h"] < scenarios[
        "S2_persistent_deficit_early_effective"]["delta_v_h"]


def test_environment_novelty_is_not_just_a_difficulty_change_and_is_exogenous():
    process = NonStationaryTaskDemand({0: {"a": 1.0}, 1: {"b": 1.0}})
    from hls.hls_lab_dynamic import DemandRegime
    config = ExogenousEnvironmentConfig(process, {
        "a": DemandRegime("a", ((0.7, 0.1),), (1.0,)),
        "b": DemandRegime("b", ((0.1, 0.7),), (1.0,)),
    }, 2, resource_budget=2.0)
    trajectory = generate_environment_trajectory(config, seed=8)
    first, second = (item.problem.requirements for item in trajectory.problems)
    assert first != second
    assert sum(first) == pytest.approx(sum(second))  # novelty is orientation, not difficulty
    assert generate_environment_trajectory(config, seed=8) == trajectory
