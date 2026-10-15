"""Engineering acceptance tests for the additive HLS v1 teaching cycle."""

import pytest

from experiments.synthetic.hls_lab_v1.integrated_demo import (
    EFFICACY, INITIAL_A, INITIAL_B, LEARNING, PARAMETERS, _problem, run_demo,
)
from hls.discover_v0 import JOINT_ACTIONS
from hls.hls_lab_dynamic import LearningProfile, advance_team
from hls.hls_lab_v1 import ProblemSpec, make_team
from hls.hls_lab_v1_integrated import (
    IntegratedAction, IntegratedDecisionView, OrganizationMemory,
    P0ProductionOnly, P1FixedTeaching, P2AdaptiveTeaching, TeachingEfficacy,
    TeachingEvent, TeachingParameters, compare_integrated_policies,
    enumerate_feasible_integrated_actions, run_integrated_sequence,
    serialize_integrated_result,
)


def _efficacy(value: float) -> TeachingEfficacy:
    rows = [[[0.0, 0.0] for _ in range(3)] for _ in range(3)]
    rows[0][1][1] = value
    return TeachingEfficacy(tuple(tuple(tuple(pair) for pair in row) for row in rows))


def _long_problem(problem_id="x", requirements=(0.0, 0.5), budget=2.0):
    return _problem(problem_id, requirements, "test")


def test_joint_action_enforces_shared_and_individual_resources():
    problem = ProblemSpec("budget", (0.5, 0.5), 1.5, max_effort_per_expert=1.25)
    actions = enumerate_feasible_integrated_actions(problem, teaching_effort=0.25)
    assert all(action.production in JOINT_ACTIONS for action in actions)
    for action in actions:
        production = sum(sum(row) for row in action.production)
        teaching = 0 if action.teaching is None else 2 * action.teaching.effort
        assert production + teaching <= problem.resource_budget + 1e-12
        loads = [sum(row) for row in action.production]
        if action.teaching:
            loads[action.teaching.instructor] += action.teaching.effort
            loads[action.teaching.learner] += action.teaching.effort
        assert max(loads) <= problem.max_effort_per_expert + 1e-12
        assert action.teaching is None or action.teaching.instructor != action.teaching.learner
    assert any(action.teaching is None for action in actions)
    assert any(action.teaching is not None for action in actions)
    with pytest.raises(ValueError):
        TeachingEvent(0, 0, 1, 0.25)


def test_teaching_is_real_resource_use_and_can_displace_production():
    problem = ProblemSpec("displace", (0.5, 0.0), 1.0, max_effort_per_expert=1.25)
    actions = enumerate_feasible_integrated_actions(problem, teaching_effort=0.25)
    no_lesson_max = max(sum(sum(row) for row in a.production) for a in actions if a.teaching is None)
    lesson_max = max(sum(sum(row) for row in a.production) for a in actions if a.teaching is not None)
    assert no_lesson_max > lesson_max
    run = run_integrated_sequence(
        make_team(((0.2, 0.1), (0.2, 0.1), (0.9, 0.2))),
        (_long_problem("displace", (0.5, 0.0), 1.0),),
        P1FixedTeaching((0, 1, 1)), learning=LearningProfile(((0.1, 0.1),) * 3),
        teaching_efficacy=_efficacy(0.8), parameters=PARAMETERS, individual_learning=False,
    )
    row = run.records[0]
    assert row.total_resource_used == pytest.approx(row.production_effort + row.teaching_effort)
    assert row.resource_cost == pytest.approx(row.total_resource_used * 0.2)


def test_teaching_changes_future_competence_and_mis_is_separate():
    initial = make_team(((0.2, 0.4), (0.1, 0.05), (0.5, 0.1)))
    lesson = run_integrated_sequence(
        initial, (_long_problem("learn", (0.0, 0.2)),), P1FixedTeaching((0, 1, 1)),
        learning=LearningProfile(((0.05, 0.05),) * 3), teaching_efficacy=_efficacy(0.9),
        parameters=TeachingParameters(effort=0.25, outcome_noise_sd=0.0,
                                     production_observation_noise_sd=0.0),
        individual_learning=False,
    )
    assert lesson.final_team.experts[1].competence_real[1] > initial.experts[1].competence_real[1]
    assert lesson.records[0].teaching_gain_real is not None
    assert lesson.records[0].competence_real_after[0][0] == initial.real_matrix[0][0]

    no_lesson = run_integrated_sequence(
        initial, (_long_problem("mis", (0.0, 0.2)),), P0ProductionOnly(),
        learning=LearningProfile(((0.05, 0.05),) * 3), teaching_efficacy=_efficacy(0.9),
        parameters=TeachingParameters(production_observation_noise_sd=0.0), individual_learning=True,
    )
    production = no_lesson.records[0].action.production
    expected = advance_team(initial, production, LearningProfile(((0.05, 0.05),) * 3),
                            enabled=True, update_estimated=False)
    assert no_lesson.records[0].competence_real_after == expected.real_matrix
    assert no_lesson.records[0].action.teaching is None


def test_noisy_formative_observations_change_p2_future_decision_not_private_gain():
    problems = tuple(_long_problem("repeated", (0.0, 0.9), 2.0) for _ in range(3))
    policy = P2AdaptiveTeaching(((0, 1, 1),))
    params = TeachingParameters(transfer_rate=0.8, effort=0.25, outcome_noise_sd=0.0,
                                production_observation_noise_sd=0.0,
                                efficacy_threshold=0.35, target_competence=0.99)
    initial = make_team(((0.2, 0.3), (0.2, 0.05), (0.8, 0.2)))
    good = run_integrated_sequence(initial, problems, policy,
                                   learning=LearningProfile(((0.01, 0.01),) * 3),
                                   teaching_efficacy=_efficacy(0.9), parameters=params,
                                   individual_learning=False, seed=5)
    bad = run_integrated_sequence(initial, problems, policy,
                                  learning=LearningProfile(((0.01, 0.01),) * 3),
                                  teaching_efficacy=_efficacy(0.0), parameters=params,
                                  individual_learning=False, seed=5)
    assert good.records[0].teaching_observation != bad.records[0].teaching_observation
    assert good.records[1].action.teaching is not None
    assert bad.records[1].action.teaching is None
    assert not hasattr(good.records[0].action, "teaching_gain_real")
    assert not hasattr(IntegratedDecisionView, "competence_real")
    assert not hasattr(IntegratedDecisionView, "teaching_efficacy")


def test_zero_effort_production_observation_does_not_update_competence_posterior():
    class NoProduction:
        name = "NO_PRODUCTION"

        def choose(self, view, memory, parameters):
            return next(action for action in view.feasible_actions
                        if action.production == ((0.0, 0.0),) * 3 and action.teaching is None)

    run = run_integrated_sequence(
        make_team(((0.2, 0.3), (0.4, 0.5), (0.6, 0.7))),
        (_long_problem("zero", (0.0, 0.5), 1.0),), NoProduction(),
        learning=LearningProfile(((0.1, 0.1),) * 3), teaching_efficacy=_efficacy(0.5),
        parameters=TeachingParameters(production_observation_noise_sd=0.0), individual_learning=True,
    )
    assert run.records[0].competence_estimated_after == run.records[0].competence_estimated_before
    assert run.records[0].competence_real_after == run.records[0].competence_real_before


def test_policies_cannot_access_hidden_truth_and_receipt_is_reproducible():
    class InspectPolicy:
        name = "INSPECT"
        seen = None

        def choose(self, view, memory, parameters):
            self.seen = (view, memory, parameters)
            return P0ProductionOnly().choose(view, memory, parameters)

    p = _long_problem("same", (0.0, 0.3))
    policy = InspectPolicy()
    kwargs = dict(learning=LearningProfile(((0.02, 0.03),) * 3),
                  teaching_efficacy=_efficacy(0.7), parameters=PARAMETERS,
                  individual_learning=True, seed=123)
    a = run_integrated_sequence(INITIAL_A, (p, p), policy, **kwargs)
    view = policy.seen[0]
    assert not hasattr(view, "competence_real")
    assert not hasattr(view, "teaching_gain_real")
    assert not hasattr(view, "teaching_efficacy")
    b = run_integrated_sequence(INITIAL_A, (p, p), InspectPolicy(), **kwargs)
    assert serialize_integrated_result(a) == serialize_integrated_result(b)


def test_p1_and_p2_can_choose_not_to_teach_and_p0_never_teaches():
    p = _long_problem("no-need", (0.0, 0.1))
    kwargs = dict(learning=LEARNING, teaching_efficacy=EFFICACY,
                  parameters=PARAMETERS, individual_learning=False)
    p0 = run_integrated_sequence(INITIAL_A, (p,), P0ProductionOnly(), **kwargs)
    p2 = run_integrated_sequence(INITIAL_A, (p,), P2AdaptiveTeaching(((0, 1, 1),)), **kwargs)
    assert p0.records[0].action.teaching is None
    assert p2.records[0].action.teaching is None


def test_demo_has_beneficial_and_harmful_conditions_without_forcing_policy_winner():
    demo = run_demo()
    scenarios = {item["scenario"]: item for item in demo["scenarios"]}
    a = {row["policy"]: row for row in scenarios["A_LONG_RECURRENT_DEMAND"]["policies"]}
    b = {row["policy"]: row for row in scenarios["B_SHORT_MISMATCHED_DEMAND"]["policies"]}
    assert a["P2_ADAPTIVE_TEACHING"]["ces_reward_sum"] > a["P0_PRODUCTION_ONLY"]["ces_reward_sum"]
    assert a["P2_ADAPTIVE_TEACHING"]["successes"] > a["P0_PRODUCTION_ONLY"]["successes"]
    assert b["P1_FIXED_TEACHING"]["ces_reward_sum"] < b["P0_PRODUCTION_ONLY"]["ces_reward_sum"]


def test_matched_policies_share_exogenous_inputs_but_evolve_independently():
    sequence = tuple(_long_problem("changing" if i < 2 else "return",
                                   (0.4, 0.0) if i < 2 else (0.0, 0.3)) for i in range(4))
    runs = compare_integrated_policies(INITIAL_A, sequence,
                                       (P0ProductionOnly(), P1FixedTeaching((0, 1, 1)),
                                        P2AdaptiveTeaching(((0, 1, 1),))),
                                       learning=LEARNING, teaching_efficacy=EFFICACY,
                                       parameters=PARAMETERS, seed=77)
    assert all([r.problem_id for r in run.records] == [p.problem.problem_id for p in sequence]
               for run in runs)
    assert len({run.final_team.real_matrix for run in runs}) > 1
    from hls.hls_lab_dynamic import indexed_normal_innovation
    residuals = []
    for run in runs:
        row = run.records[0]
        residuals.append(tuple(tuple(
            row.individual_observations[i][k]
            - row.action.production[i][k] * row.competence_real_before[i][k]
            for k in range(2)) for i in range(3)))
    expected = tuple(tuple(
        PARAMETERS.production_observation_noise_sd
        * indexed_normal_innovation(77, 0, 0, i, k)
        for k in range(2)) for i in range(3))
    expected_flat = tuple(value for row in expected for value in row)
    assert all(tuple(value for row in residual for value in row) == pytest.approx(expected_flat)
               for residual in residuals)
