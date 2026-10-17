"""N×K competence-observation and estimator compatibility checks."""

import pytest

from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_nk_estimation import (
    CompetenceObservationParametersNK,
    initialize_competence_posterior_nk,
    posterior_mean_matrix_nk,
    posterior_variance_matrix_nk,
)
from hls.hls_lab_nk_execution import (
    NKInformationRunResult,
    run_nk_production_sequence,
    serialize_nk_information_result,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import (
    NKDecisionView,
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
)
from hls.hls_lab_nk_teaching import TeachingEfficacyNK, TeachingParametersNK
from hls.hls_lab_nk_teaching import JointActionNK
from hls.hls_lab_nk_learning import mis_v2_transition_nk
from hls.hls_lab_nk_teaching import TeachingActionNK, teaching_transition_nk
from hls.hls_lab_v1 import ExpertState, ProblemSpec, TeamState
from hls.hls_lab_v1_integrated import (
    IntegratedProblem,
    P0ProductionOnly,
    P1FixedTeaching,
    P2AdaptiveTeaching,
    TeachingEfficacy,
    TeachingParameters,
    run_integrated_sequence,
)


def _org(n, k, actual, estimate=None):
    return OrganizationConfigNK(
        tuple(f"A{i}" for i in range(n)), tuple(f"S{j}" for j in range(k)),
        actual, (1.0,) * n, float(n), estimate,
    )


def _efficacy(org, efficacy=0.6):
    n, k = len(org.agent_ids), len(org.skill_ids)
    tensor = tuple(tuple(tuple(
        0.0 if teacher == learner else efficacy for _ in range(k)
    ) for learner in range(n)) for teacher in range(n))
    return TeachingEfficacyNK(org.agent_ids, org.skill_ids, tensor)


def _legacy_efficacy(efficacy):
    return TeachingEfficacy(efficacy.values)


def _old_team(org):
    estimate = org.competence_estimated_initial or org.competence_initial
    return TeamState(tuple(
        ExpertState(agent, org.competence_initial[i], estimate[i])
        for i, agent in enumerate(org.agent_ids)
    ))


def _legacy_problems(problems):
    return tuple(IntegratedProblem(
        ProblemSpec(problem.problem_id, problem.requirements,
                    problem.resource_budget, max_effort_per_expert=1.0),
        problem.ces_weights,
    ) for problem in problems)


def _choices(n, k):
    zero = (0.0,) * k
    active = tuple(tuple(1.0 if j == skill else 0.0 for j in range(k))
                   for skill in range(k))
    return tuple((zero, *active) for _ in range(n))


def test_generic_posterior_initialization_matches_historical_grid_prior():
    estimates = ((0.0, 0.2, 0.73), (0.5, 0.9, 1.0))
    params = CompetenceObservationParametersNK(competence_prior_variance=0.04)
    posterior = initialize_competence_posterior_nk(estimates, params)
    for got, expected in zip(posterior_mean_matrix_nk(posterior), estimates):
        assert got == pytest.approx(expected, abs=1e-12)
    variances = posterior_variance_matrix_nk(posterior)
    for i, row in enumerate(estimates):
        for k, value in enumerate(row):
            assert variances[i][k] == pytest.approx(min(0.04, value * (1 - value)), abs=1e-12)


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (3, 2), (4, 3)])
@pytest.mark.parametrize("mode", ["perfect", "imperfect"])
def test_information_modes_support_required_nk_shapes_and_replay(n, k, mode):
    actual = tuple(tuple(0.15 + 0.11 * ((i + 2 * j) % 6) for j in range(k)) for i in range(n))
    estimates = tuple(tuple(min(1.0, value + 0.07) for value in row) for row in actual)
    org = _org(n, k, actual, estimates)
    problems = tuple(ProblemSpecNK(f"p{t}", tuple(0.2 + 0.1 * j for j in range(k)), float(n))
                    for t in range(3))
    kwargs = dict(max_candidates=4**n if k == 2 else (k + 1)**n,
                  per_agent_effort_choices=None if k == 2 else _choices(n, k),
                  policy=P0ProductionOnlyPolicyNK(), information_mode=mode,
                  information_seed=817, individual_learning=True,
                  learning_profile=LearningProfileNK(tuple(tuple(0.12 for _ in range(k))
                                                            for _ in range(n))))
    first = run_nk_production_sequence(org, problems, **kwargs)
    second = run_nk_production_sequence(org, problems, **kwargs)
    assert isinstance(first, NKInformationRunResult)
    assert first == second
    assert serialize_nk_information_result(first) == serialize_nk_information_result(second)
    for record in first.records:
        assert record.competence_actual_before == record.production.competence_before
        assert record.competence_actual_after == record.production.competence_after
        if mode == "perfect":
            assert record.competence_estimated_before == record.competence_actual_before
            assert record.competence_estimated_after == record.competence_actual_after
            assert record.competence_variance_after is None
        else:
            assert record.competence_variance_after is not None
    assert first.final_state.competence_real == first.records[-1].competence_actual_after


def test_zero_effort_noise_does_not_turn_imperfect_mode_into_perfect_information():
    org = _org(2, 2, ((0.9, 0.1), (0.1, 0.9)), ((0.2, 0.8), (0.8, 0.2)))
    problem = ProblemSpecNK("no-exposure", (0.0, 0.8), 0.0)
    result = run_nk_production_sequence(
        org, (problem,), max_candidates=16, information_mode="imperfect",
        policy=P0ProductionOnlyPolicyNK(),
        observation_parameters=CompetenceObservationParametersNK(
            production_observation_noise_sd=0.0,
        ),
    )
    row = result.records[0]
    assert row.production_observations == ((0.0, 0.0), (0.0, 0.0))
    for got, expected in zip(row.competence_estimated_before, org.competence_estimated_initial):
        assert got == pytest.approx(expected)
    for got, expected in zip(row.competence_estimated_after, row.competence_estimated_before):
        assert got == pytest.approx(expected)
    assert row.competence_actual_after == org.competence_initial


def test_production_uses_actual_state_and_policy_view_excludes_actual_state():
    class ViewCheckingP0(P0ProductionOnlyPolicyNK):
        def choose(self, view, memory, parameters):
            assert not hasattr(view, "competence_actual")
            assert not hasattr(view, "competence_real")
            return super().choose(view, memory, parameters)

    actual = ((0.8,),)
    problem = ProblemSpecNK("one", (0.2,), 0.5)
    action = JointActionNK(((0.5,),))
    catalog = (((0.0,), (0.5,)),)
    results = []
    for estimate in (((0.1,),), ((0.9,),)):
        org = _org(1, 1, actual, estimate)
        results.append(run_nk_production_sequence(
            org, (problem,), max_candidates=2,
            per_agent_effort_choices=catalog,
            explicit_actions=(action,), information_mode="imperfect",
            observation_parameters=CompetenceObservationParametersNK(
                production_observation_noise_sd=0.0,
            ),
        ))
    first, second = results
    assert first.records[0].production.outputs == second.records[0].production.outputs == (0.4,)
    assert first.records[0].competence_estimated_before != second.records[0].competence_estimated_before
    # Automatic policy access receives only the declared estimated matrix.
    run_nk_production_sequence(
        _org(1, 1, actual, ((0.1,),)), (problem,), max_candidates=2,
        per_agent_effort_choices=catalog, policy=ViewCheckingP0(),
        information_mode="imperfect",
    )


@pytest.mark.parametrize("mis", [False, True])
@pytest.mark.parametrize("teaching", [False, True])
def test_four_learning_teaching_switches_preserve_actual_transition_composition(mis, teaching):
    org = _org(2, 1, ((0.4,), (0.15,)))
    efficacy = _efficacy(org, 0.7)
    profile = LearningProfileNK(((0.2,), (0.1,)))
    lesson = TeachingActionNK("A0", "A1", "S0", 0.1)
    action = JointActionNK(((0.5,), (0.0,)), lesson if teaching else None)
    problem = ProblemSpecNK("switches", (0.1,), 1.0)
    result = run_nk_production_sequence(
        org, (problem,), max_candidates=27,
        per_agent_effort_choices=(((0.0,), (0.5,), (1.0,)),) * 2,
        explicit_actions=(action,), information_mode="imperfect",
        individual_learning=mis, learning_profile=profile,
        teaching_enabled=teaching,
        teaching_efficacy=efficacy,
        teaching_parameters=TeachingParametersNK(0.4),
        observation_parameters=CompetenceObservationParametersNK(
            production_observation_noise_sd=0.01,
        ),
        information_seed=19,
    )
    expected = org.competence_initial
    if mis:
        expected = mis_v2_transition_nk(expected, action.production, profile)
    if teaching:
        expected = teaching_transition_nk(
            expected, lesson, efficacy, TeachingParametersNK(0.4),
        ).competence_after
    for got, value in zip(result.records[0].competence_actual_after, expected):
        assert got == pytest.approx(value)
    assert result.records[0].competence_after_mis == (
        mis_v2_transition_nk(org.competence_initial, action.production, profile)
        if mis else org.competence_initial
    )


@pytest.mark.parametrize("policy_kind", ["P1", "P2"])
def test_explicit_perfect_information_policies_match_legacy_3x2(policy_kind):
    actual = ((0.2, 0.4), (0.1, 0.05), (0.95, 0.1))
    org = _org(3, 2, actual, actual)
    efficacy = _efficacy(org, 0.55)
    problems = tuple(ProblemSpecNK(f"pi{i}", req, 3.0, (0.5, 0.5)) for i, req in enumerate(
        ((0.0, 0.9), (0.0, 0.9), (0.5, 0.0))))
    nk_relation = ("A0", "A1", "S1")
    generic_policy = P1FixedTeachingNK(nk_relation) if policy_kind == "P1" else P2AdaptiveTeachingNK((nk_relation,))
    legacy_policy = P1FixedTeaching((0, 1, 1)) if policy_kind == "P1" else P2AdaptiveTeaching(((0, 1, 1),))
    learning = LearningProfileNK(((0.1, 0.12), (0.09, 0.08), (0.11, 0.1)))
    generic = run_nk_production_sequence(
        org, problems, max_candidates=832, policy=generic_policy,
        information_mode="perfect", individual_learning=True,
        learning_profile=learning, teaching_enabled=True,
        teaching_efficacy=efficacy,
    )
    legacy = run_integrated_sequence(
        _old_team(org), _legacy_problems(problems), legacy_policy,
        learning=LearningProfile(learning.eta),
        teaching_efficacy=_legacy_efficacy(efficacy),
        parameters=TeachingParameters(
            production_observation_noise_sd=0.0,
            competence_prior_variance=0.0,
        ), individual_learning=True, organizational_learning=True,
    )
    for got, expected in zip(generic.records, legacy.records):
        assert got.action.production == expected.action.production
        assert (got.action.teaching is None) == (expected.action.teaching is None)
        assert got.production.outputs == expected.outputs
        assert got.competence_actual_after == expected.competence_real_after
        for got_row, expected_row in zip(
            got.competence_estimated_after, expected.competence_estimated_after,
        ):
            assert got_row == pytest.approx(expected_row, abs=1e-12)


def test_imperfect_nk_3x2_matches_authoritative_legacy_production_estimator_and_random_streams():
    actual = ((0.25, 0.7), (0.55, 0.2), (0.8, 0.45))
    estimate = ((0.35, 0.6), (0.45, 0.3), (0.75, 0.4))
    org = _org(3, 2, actual, estimate)
    problems = tuple(ProblemSpecNK(f"p{t}", req, 2.0, (0.6, 0.4)) for t, req in enumerate(
        ((0.1, 0.8), (0.7, 0.2), (0.3, 0.6))))
    learning = LearningProfileNK(((0.12, 0.2), (0.15, 0.09), (0.1, 0.18)))
    observation = CompetenceObservationParametersNK(
        production_observation_noise_sd=0.02, competence_prior_variance=0.04,
    )
    generic = run_nk_production_sequence(
        org, problems, max_candidates=64, policy=P0ProductionOnlyPolicyNK(),
        individual_learning=True, learning_profile=learning,
        information_mode="imperfect", observation_parameters=observation,
        information_seed=501,
    )
    legacy = run_integrated_sequence(
        _old_team(org), _legacy_problems(problems), P0ProductionOnly(),
        learning=LearningProfile(learning.eta),
        teaching_efficacy=TeachingEfficacy(tuple(tuple(tuple(0.0 for _ in range(2))
                                                     for _ in range(3)) for _ in range(3))),
        parameters=TeachingParameters(
            production_observation_noise_sd=observation.production_observation_noise_sd,
            competence_prior_variance=observation.competence_prior_variance,
        ), individual_learning=True, organizational_learning=False, seed=501,
    )
    for got, expected in zip(generic.records, legacy.records):
        assert got.action.production == expected.action.production
        assert got.production_observations == expected.individual_observations
        assert got.competence_estimated_before == expected.competence_estimated_before
        assert got.competence_estimated_after == expected.competence_estimated_after
        assert got.competence_actual_after == expected.competence_real_after
        assert got.production.outputs == expected.outputs
        assert got.production.ces_reward == expected.ces_reward


@pytest.mark.parametrize("policy_kind", ["P1", "P2"])
def test_imperfect_nk_teaching_and_mis_match_legacy_decision_memory_and_estimator(policy_kind):
    actual = ((0.2, 0.7), (0.1, 0.25), (0.85, 0.15))
    estimate = ((0.3, 0.6), (0.2, 0.3), (0.8, 0.2))
    org = _org(3, 2, actual, estimate)
    efficacy = _efficacy(org, 0.65)
    problems = tuple(ProblemSpecNK(f"p{i}", req, 3.0, (0.5, 0.5)) for i, req in enumerate(
        ((0.0, 0.9), (0.0, 0.9), (0.5, 0.0))))
    learning = LearningProfileNK(((0.1, 0.12), (0.09, 0.08), (0.11, 0.1)))
    obs = CompetenceObservationParametersNK(
        production_observation_noise_sd=0.015, outcome_noise_sd=0.02,
        competence_prior_variance=0.04,
    )
    generic_policy = (P1FixedTeachingNK(("A0", "A1", "S1")) if policy_kind == "P1"
                      else P2AdaptiveTeachingNK((("A0", "A1", "S1"),)))
    legacy_policy = (P1FixedTeaching((0, 1, 1)) if policy_kind == "P1"
                     else P2AdaptiveTeaching(((0, 1, 1),)))
    generic = run_nk_production_sequence(
        org, problems, max_candidates=832,
        policy=generic_policy,
        individual_learning=True, learning_profile=learning,
        teaching_enabled=True, teaching_efficacy=efficacy,
        teaching_parameters=TeachingParametersNK(0.4),
        information_mode="imperfect", observation_parameters=obs,
        information_seed=73,
    )
    legacy_values = tuple(tuple(tuple(pair) for pair in row) for row in efficacy.values)
    legacy = run_integrated_sequence(
        _old_team(org), _legacy_problems(problems), legacy_policy,
        learning=LearningProfile(learning.eta), teaching_efficacy=TeachingEfficacy(legacy_values),
        parameters=TeachingParameters(
            transfer_rate=0.4, effort=0.25,
            outcome_noise_sd=obs.outcome_noise_sd,
            production_observation_noise_sd=obs.production_observation_noise_sd,
            competence_prior_variance=obs.competence_prior_variance,
        ), individual_learning=True, organizational_learning=True, seed=73,
    )
    for got, expected in zip(generic.records, legacy.records):
        assert got.action.production == expected.action.production
        if got.action.teaching is not None:
            assert (got.action.teaching.teacher_id, got.action.teaching.learner_id,
                    got.action.teaching.skill_id) == ("A0", "A1", "S1")
        if expected.action.teaching is not None:
            assert got.action.teaching is not None
        assert (got.action.teaching is None) == (expected.action.teaching is None)
        assert got.production_observations == expected.individual_observations
        assert got.teaching_observation == pytest.approx(expected.teaching_observation)
        assert got.competence_actual_after == expected.competence_real_after
        assert got.competence_estimated_before == expected.competence_estimated_before
        assert got.competence_estimated_after == expected.competence_estimated_after
        assert got.production.ces_reward == expected.ces_reward
        expected_memory = tuple(
            ((f"A{item.relation[0]}", f"A{item.relation[1]}", f"S{item.relation[2]}"),
             item.count, item.mean)
            for item in expected.efficacy_estimates_after
        )
        actual_memory = tuple((item.relation, item.count, item.mean)
                              for item in got.efficacy_memory_after)
        assert len(actual_memory) == len(expected_memory)
        for actual_item, expected_item in zip(actual_memory, expected_memory):
            assert actual_item[:2] == expected_item[:2]
            assert actual_item[2] == pytest.approx(expected_item[2])
