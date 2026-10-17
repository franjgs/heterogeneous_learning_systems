"""Engineering acceptance tests for the additive HLS v1 teaching cycle."""

import hashlib
import json

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


def test_historical_3x2_reference_trace_bytes_and_catalog_order():
    """Pin pre-NxK 3x2 catalog, decisions, outcomes and serialized traces."""
    assert len(JOINT_ACTIONS) == 64
    catalog_digest = hashlib.sha256(
        json.dumps(JOINT_ACTIONS, separators=(",", ":")).encode()
    ).hexdigest()
    assert catalog_digest == "b219314cb6a27267c81ec5a4213630ee888cc7bb0d771ce6c7aa2b2f8f2f5381"
    assert JOINT_ACTIONS[0] == ((0.0, 0.0),) * 3
    assert JOINT_ACTIONS[-1] == ((1.0, 0.0),) * 3

    problems = tuple(
        [_problem("baseline-skill1", (0.0, 0.6), "baseline") for _ in range(2)]
        + [_problem("baseline-skill0", (0.75, 0.0), "baseline")]
    )
    feasible = enumerate_feasible_integrated_actions(
        problems[0].problem, teaching_effort=PARAMETERS.effort
    )
    feasible_digest = hashlib.sha256(json.dumps(
        feasible, default=lambda value: value.__dict__, sort_keys=True,
        separators=(",", ":"),
    ).encode()).hexdigest()
    assert len(feasible) == 508
    assert feasible_digest == "9ebc8196031c3cc49513d3367525b4bfbbdaba34ff1594a861877ffb957e277d"
    runs = compare_integrated_policies(
        INITIAL_A,
        problems,
        (P0ProductionOnly(), P1FixedTeaching((0, 1, 1)),
         P2AdaptiveTeaching(((0, 1, 1),))),
        learning=LEARNING,
        teaching_efficacy=EFFICACY,
        parameters=PARAMETERS,
        seed=20261016,
    )
    expected = {
        "P0_PRODUCTION_ONLY": (
            "96948a980759a77de84e1595a5627ebe8cdcfadcbcbce3111ed4e3d97c262e0b",
            (21, 21, 63), (False, False, True), (3.0, 3.0, 3.0),
            (0.1375, 0.13756125, 0.31250000000000006),
        ),
        "P1_FIXED_TEACHING": (
            "eb8d310fe7115bfcbf18d31f719f4500ded142e85424e4d7034dd677a9d2db0c",
            (17, 20, 51), (False, True, True), (2.5, 2.5, 2.5),
            (0.12500000000000003, 0.15764, 0.28750000000000003),
        ),
        "P2_ADAPTIVE_TEACHING": (
            "cbf7603f39cd436214cfd300760ca86cb9441f30c35fa5e3cd0771824bf34b4b",
            (17, 21, 63), (False, True, True), (2.5, 3.0, 3.0),
            (0.12500000000000003, 0.18266250000000003, 0.31250000000000006),
        ),
    }
    assert {run.policy for run in runs} == set(expected)
    for run in runs:
        digest, action_ids, success, resources, rewards = expected[run.policy]
        assert hashlib.sha256(serialize_integrated_result(run).encode()).hexdigest() == digest
        assert tuple(JOINT_ACTIONS.index(row.action.production) for row in run.records) == action_ids
        expected_teaching = {
            "P0_PRODUCTION_ONLY": (False, False, False),
            "P1_FIXED_TEACHING": (True, True, True),
            "P2_ADAPTIVE_TEACHING": (True, False, False),
        }[run.policy]
        assert tuple(row.action.teaching is not None for row in run.records) == expected_teaching
        assert tuple(row.functional_result.success for row in run.records) == success
        assert tuple(row.total_resource_used for row in run.records) == resources
        assert tuple(row.ces_reward for row in run.records) == pytest.approx(rewards)


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
