from __future__ import annotations

import pytest

from hls.hls_lab_v1 import ExpertState, ProblemSpec, TeamState
from hls.hls_lab_v1_integrated import (
    IntegratedAction,
    IntegratedProblem,
    P0ProductionOnly,
    TeachingEfficacy,
    TeachingEvent,
    TeachingParameters,
    run_integrated_sequence,
)
from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_nk_execution import (
    run_nk_production_sequence,
    serialize_nk_teaching_result,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_teaching import (
    JointActionNK,
    TeachingActionNK,
    TeachingEfficacyNK,
    TeachingParametersNK,
    teaching_transition_nk,
    validate_joint_action_resources_nk,
)


def efficacy(agents, skills, value=0.5):
    n, k = len(agents), len(skills)
    return TeachingEfficacyNK(
        tuple(agents), tuple(skills),
        tuple(tuple(tuple(0.0 if i == j else value for _ in range(k))
                    for j in range(n)) for i in range(n)),
    )


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (3, 2), (4, 3)])
def test_transition_generalizes_over_nk_and_touches_only_target(n, k):
    agents = tuple(f"a{i}" for i in range(n))
    skills = tuple(f"s{x}" for x in range(k))
    state = tuple(tuple(0.2 + 0.05 * i for _ in range(k)) for i in range(n))
    if n == 1:
        tensor = efficacy(agents, skills)
        assert all(tensor.values[0][0][x] == 0 for x in range(k))
        with pytest.raises(ValueError, match="distinct"):
            TeachingActionNK(agents[0], agents[0], skills[0], 0.2)
        return
    action = TeachingActionNK(agents[-1], agents[0], skills[-1], 0.4)
    result = teaching_transition_nk(state, action, efficacy(agents, skills))
    assert result.competence_gain == pytest.approx(0.4 * 0.4 * 0.5 * (1 - state[0][-1]))
    assert result.competence_increment[0][-1] == pytest.approx(result.competence_gain)
    assert sum(sum(row) for row in result.competence_increment) == pytest.approx(result.competence_gain)
    for i in range(n):
        for skill in range(k):
            if (i, skill) != (0, k - 1):
                assert result.competence_after[i][skill] == state[i][skill]


@pytest.mark.parametrize("teacher_c", [0.0, 0.25, 0.3, 1.0])
def test_legacy_equation_uses_relationship_efficacy_not_teacher_competence(teacher_c):
    state = ((teacher_c,), (0.25,))
    action = TeachingActionNK("teacher", "learner", "s", 0.5)
    result = teaching_transition_nk(
        state, action, efficacy(("teacher", "learner"), ("s",), 0.8),
        TeachingParametersNK(transfer_rate=0.5),
    )
    assert result.competence_gain == pytest.approx(0.5 * 0.5 * 0.8 * 0.75)


@pytest.mark.parametrize("learner_c,teaching_efficacy,expected", [
    (0.0, 1.0, 0.4), (1.0, 1.0, 0.0), (0.4, 0.0, 0.0),
])
def test_teaching_boundaries_and_zero_efficacy(learner_c, teaching_efficacy, expected):
    state = ((0.9,), (learner_c,))
    result = teaching_transition_nk(
        state, TeachingActionNK("t", "l", "s", 1.0),
        efficacy(("t", "l"), ("s",), teaching_efficacy),
    )
    assert result.competence_gain == pytest.approx(expected)
    assert 0 <= result.competence_after[1][0] <= 1


def test_teaching_contract_validation():
    with pytest.raises(ValueError, match="shape"):
        TeachingEfficacyNK(("a", "b"), ("s",), (((0,),), ((0,),)))
    with pytest.raises(ValueError, match="self-teaching"):
        TeachingEfficacyNK(("a",), ("s",), (((0.1,),),))
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        efficacy(("a", "b"), ("s",), 1.1)
    with pytest.raises(ValueError, match="unknown"):
        teaching_transition_nk(((0.2,), (0.3,)), TeachingActionNK("x", "b", "s", 0.2),
                               efficacy(("a", "b"), ("s",)))
    with pytest.raises(ValueError, match="unknown"):
        teaching_transition_nk(((0.2,), (0.3,)), TeachingActionNK("a", "b", "x", 0.2),
                               efficacy(("a", "b"), ("s",)))
    with pytest.raises(ValueError, match="shape"):
        teaching_transition_nk(((0.2, 0.3), (0.4, 0.5)),
                               TeachingActionNK("a", "b", "s", 0.2),
                               efficacy(("a", "b"), ("s",)))
    with pytest.raises(ValueError, match="positive"):
        TeachingActionNK("a", "b", "s", 0)
    with pytest.raises(ValueError, match="distinct"):
        TeachingActionNK("a", "a", "s", 0.1)


def test_resource_accounting_charges_both_teaching_participants():
    loads, total, unused = validate_joint_action_resources_nk(
        ((0.5,), (0.5,)), TeachingActionNK("a", "b", "s", 0.25),
        agent_ids=("a", "b"), collective_budget=2.0,
        individual_limits=(1.0, 1.0), efficacy=efficacy(("a", "b"), ("s",)),
    )
    assert loads == pytest.approx((0.75, 0.75))
    assert total == pytest.approx(1.5)
    assert unused == pytest.approx(0.5)
    _, zero_efficacy_cost, _ = validate_joint_action_resources_nk(
        ((0.5,), (0.5,)), TeachingActionNK("a", "b", "s", 0.25),
        agent_ids=("a", "b"), collective_budget=2.0,
        individual_limits=(1.0, 1.0), efficacy=efficacy(("a", "b"), ("s",), 0.0),
    )
    assert zero_efficacy_cost == total  # efficacy never discounts resource use
    with pytest.raises(ValueError, match="collective"):
        validate_joint_action_resources_nk(
            ((0.5,), (0.5,)), TeachingActionNK("a", "b", "s", 0.5),
            agent_ids=("a", "b"), collective_budget=1.5,
            individual_limits=(2.0, 2.0), efficacy=efficacy(("a", "b"), ("s",)),
        )
    with pytest.raises(ValueError, match="individual"):
        validate_joint_action_resources_nk(
            ((0.5,), (0.5,)), TeachingActionNK("a", "b", "s", 0.3),
            agent_ids=("a", "b"), collective_budget=3,
            individual_limits=(0.7, 1.0), efficacy=efficacy(("a", "b"), ("s",)),
        )


def org():
    return OrganizationConfigNK(
        ("t", "l"), ("s0", "s1"), ((0.8, 0.2), (0.3, 0.4)),
        (1.0, 1.0), 2.0,
    )


def choices():
    vectors = ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5))
    return (vectors, vectors)


def problem(resource=2.0):
    return ProblemSpecNK("p", (0.2, 0.2), resource, (0.5, 0.5))


def actions(event):
    return (JointActionNK(((0.5, 0.0), (0.0, 0.5)), event),)


def test_explicit_episode_mechanism_switches_order_and_traces():
    org0 = org()
    problems = (problem(),)
    efficacy_config = efficacy(org0.agent_ids, org0.skill_ids, 0.75)
    event = TeachingActionNK("t", "l", "s0", 0.25)
    joint = actions(event)
    kwargs = dict(max_candidates=9, per_agent_effort_choices=choices(),
                  explicit_actions=joint, teaching_enabled=True,
                  teaching_efficacy=efficacy_config)
    frozen = run_nk_production_sequence(org0, problems, **{
        **kwargs, "teaching_enabled": False, "teaching_efficacy": None,
        "explicit_actions": actions(None),
    })
    mis = run_nk_production_sequence(
        org0, problems, **{**kwargs, "teaching_enabled": False,
                           "teaching_efficacy": None, "explicit_actions": actions(None),
                           "individual_learning": True,
                           "learning_profile": LearningProfileNK(((0.2, 0.3), (0.4, 0.5)))},
    )
    teach = run_nk_production_sequence(org0, problems, **kwargs)
    both = run_nk_production_sequence(
        org0, problems, **{**kwargs, "individual_learning": True,
                           "learning_profile": LearningProfileNK(((0.2, 0.3), (0.4, 0.5)))},
    )
    assert frozen.final_state.competence_real == org0.competence_initial
    assert mis.records[0].production.competence_after != org0.competence_initial
    assert teach.records[0].competence_after_mis == org0.competence_initial
    assert teach.records[0].competence_increment_from_teaching[1][0] > 0
    assert both.records[0].competence_after_mis == mis.records[0].production.competence_after
    expected_after_teaching = teaching_transition_nk(
        mis.records[0].production.competence_after, event, efficacy_config,
    ).competence_after
    assert both.final_state.competence_real == expected_after_teaching
    assert teach.records[0].production.outputs == pytest.approx((0.4, 0.2))
    assert teach.records[0].teaching_resource_used == pytest.approx(0.5)
    assert teach.records[0].total_resource_used == pytest.approx(1.5)
    assert teach.records[0].unused_collective_capacity == pytest.approx(0.5)
    assert serialize_nk_teaching_result(teach) == serialize_nk_teaching_result(
        run_nk_production_sequence(org0, problems, **kwargs)
    )


def test_teaching_validation_rejects_missing_or_infeasible_actions():
    with pytest.raises(ValueError, match="explicit complete"):
        run_nk_production_sequence(org(), (problem(),), max_candidates=9, teaching_enabled=True)
    with pytest.raises(ValueError, match="teaching_enabled"):
        run_nk_production_sequence(org(), (problem(),), max_candidates=9,
                                  explicit_actions=actions(TeachingActionNK("t", "l", "s0", 0.2)))
    with pytest.raises(ValueError, match="collective"):
        run_nk_production_sequence(
            org(), (problem(resource=1.0),), max_candidates=9,
            per_agent_effort_choices=choices(), teaching_enabled=True,
            teaching_efficacy=efficacy(org().agent_ids, org().skill_ids),
            explicit_actions=actions(TeachingActionNK("t", "l", "s0", 0.25)),
        )


def test_zero_efficacy_episode_still_charges_teaching_resources():
    organization = org()
    event = TeachingActionNK("t", "l", "s0", 0.25)
    run = run_nk_production_sequence(
        organization, (problem(),), max_candidates=9,
        per_agent_effort_choices=choices(), teaching_enabled=True,
        teaching_efficacy=efficacy(organization.agent_ids, organization.skill_ids, 0.0),
        explicit_actions=(JointActionNK(((0.0, 0.0), (0.0, 0.0)), event),),
    )
    row = run.records[0]
    assert row.productive_effort_used == 0.0
    assert row.teaching_resource_used == pytest.approx(0.5)
    assert row.total_resource_used == pytest.approx(0.5)
    assert row.unused_collective_capacity == pytest.approx(1.5)
    assert row.competence_increment_from_teaching == ((0.0, 0.0), (0.0, 0.0))
    assert run.final_state.competence_real == organization.competence_initial


def test_generalized_teaching_matches_legacy_3x2_transition_and_episode():
    initial = ((0.8, 0.2), (0.3, 0.4), (0.6, 0.7))
    agents = ("a0", "a1", "a2")
    skills = ("s0", "s1")
    efficacy_values = [[[0.0, 0.0] for _ in agents] for _ in agents]
    efficacy_values[0][1][0] = 0.7
    efficacy_nk = TeachingEfficacyNK(
        agents, skills,
        tuple(tuple(tuple(pair) for pair in row) for row in efficacy_values),
    )
    action_nk = JointActionNK(
        ((0.0, 0.0), (0.0, 0.0), (0.5, 0.5)),
        TeachingActionNK("a0", "a1", "s0", 0.25),
    )
    eta = ((0.2, 0.2),) * 3
    generic = run_nk_production_sequence(
        OrganizationConfigNK(agents, skills, initial, (1.0,) * 3, 2.0),
        (ProblemSpecNK("same", (0.2, 0.2), 2.0, (0.5, 0.5)),),
        max_candidates=64,
        explicit_actions=(action_nk,), teaching_enabled=True,
        teaching_efficacy=efficacy_nk,
        individual_learning=True, learning_profile=LearningProfileNK(eta),
    )

    team = TeamState(tuple(ExpertState(agent, row, row) for agent, row in zip(agents, initial)))
    efficacy_legacy = TeachingEfficacy(
        tuple(tuple(tuple(pair) for pair in row) for row in efficacy_values)
    )
    event = TeachingEvent(0, 1, 0, 0.25)
    legacy = run_integrated_sequence(
        team,
        (IntegratedProblem(ProblemSpec("same", (0.2, 0.2), 2.0), (0.5, 0.5)),),
        policy=P0ProductionOnly(),
        learning=LearningProfile(eta), teaching_efficacy=efficacy_legacy,
        parameters=TeachingParameters(transfer_rate=0.4, effort=0.25,
                                      outcome_noise_sd=0.0,
                                      production_observation_noise_sd=0.0),
        individual_learning=True,
        first_action_override=IntegratedAction(action_nk.production,
                                               event),
    )
    generic_record = generic.records[0]
    legacy_record = legacy.records[0]
    assert generic_record.production.outputs == pytest.approx(legacy_record.outputs)
    assert generic_record.production.functional_result.success == legacy_record.functional_result.success
    assert generic_record.production.ces_reward == pytest.approx(legacy_record.ces_reward)
    assert generic_record.productive_effort_used == pytest.approx(legacy_record.production_effort)
    assert generic_record.competence_increment_from_teaching[1][0] == pytest.approx(
        legacy_record.teaching_gain_real
    )
    expected_post_mis = mis_v2_transition_nk(initial, action_nk.production,
                                            LearningProfileNK(eta))
    assert generic_record.competence_after_mis == expected_post_mis
    for generic_row, legacy_row in zip(generic.final_state.competence_real,
                                       legacy_record.competence_real_after):
        assert generic_row == pytest.approx(legacy_row)
    assert generic_record.teaching_resource_used == pytest.approx(legacy_record.teaching_effort)
    assert generic_record.total_resource_used == pytest.approx(legacy_record.total_resource_used)
