"""N×K P0/P1/P2 acceptance and historical-decision regressions."""

from math import prod

import pytest

from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_nk_execution import run_nk_production_sequence
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import (
    EfficacyEstimateNK,
    NKDecisionView,
    OrganizationMemoryNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
    TeachingPolicyParametersNK,
    enumerate_feasible_joint_actions_nk,
)
from hls.hls_lab_nk_production import P0ProductionOnlyNK
from hls.hls_lab_nk_teaching import (
    JointActionNK,
    TeachingActionNK,
    TeachingEfficacyNK,
    TeachingParametersNK,
)
from hls.hls_lab_v1 import ProblemSpec, TeamState, ExpertState
from hls.hls_lab_v1_integrated import (
    IntegratedAction,
    IntegratedProblem,
    P0ProductionOnly,
    P1FixedTeaching,
    P2AdaptiveTeaching,
    TeachingEvent,
    TeachingEfficacy,
    TeachingParameters,
    enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)


def _org(n, k, competence, budget=3.0, limits=None):
    return OrganizationConfigNK(
        tuple(f"A{i}" for i in range(n)), tuple(f"S{j}" for j in range(k)),
        competence, tuple(limits or (1.0,) * n), budget,
    )


def _efficacy(org, default=0.5, overrides=()):
    n, k = len(org.agent_ids), len(org.skill_ids)
    rows = [[[0.0 for _ in range(k)] for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                for skill in range(k):
                    rows[i][j][skill] = default
    for teacher, learner, skill, value in overrides:
        rows[teacher][learner][skill] = value
    return TeachingEfficacyNK(
        org.agent_ids, org.skill_ids,
        tuple(tuple(tuple(cell) for cell in row) for row in rows),
    )


def _legacy_efficacy(values):
    return TeachingEfficacy(tuple(tuple(tuple(pair) for pair in row) for row in values))


def _effort_choices(n, k):
    zero = (0.0,) * k
    vectors = tuple(tuple(0.5 if j == skill else 0.0 for j in range(k)) for skill in range(k))
    return tuple((zero, *vectors) for _ in range(n))


def _convert_joint(action):
    teaching = action.teaching
    return IntegratedAction(
        action.production,
        None if teaching is None else TeachingEvent(
            int(teaching.teacher_id[1:]), int(teaching.learner_id[1:]),
            int(teaching.skill_id[1:]), teaching.effort,
        ),
    )


def test_generalized_3x2_joint_catalog_preserves_508_legacy_order():
    org = _org(3, 2, ((0.8, 0.2), (0.3, 0.4), (0.6, 0.7)), budget=3.0,
               limits=(1.25,) * 3)
    problem = ProblemSpecNK("catalog", (0.7, 0.5), 3.0)
    efficacy = _efficacy(org)
    joint = enumerate_feasible_joint_actions_nk(
        org, problem, max_candidates=832, teaching_enabled=True,
        teaching_efficacy=efficacy, teaching_effort=0.25,
    )
    legacy_problem = ProblemSpec("catalog", (0.7, 0.5), 3.0, max_effort_per_expert=1.25)
    legacy = enumerate_feasible_integrated_actions(legacy_problem, teaching_effort=0.25)
    assert len(joint) == len(legacy) == 508
    assert tuple(_convert_joint(action) for action in joint) == legacy
    with pytest.raises(ValueError, match="joint action catalog requires 832 candidates"):
        enumerate_feasible_joint_actions_nk(
            org, problem, max_candidates=831, teaching_enabled=True,
            teaching_efficacy=efficacy, teaching_effort=0.25,
        )


@pytest.mark.parametrize("policy_kind", ["p1", "p2"])
@pytest.mark.parametrize("mis", [False, True])
def test_3x2_policies_match_legacy_actions_with_perfect_information(policy_kind, mis):
    competence = ((0.2, 0.4), (0.1, 0.05), (0.95, 0.1))
    org = _org(3, 2, competence, budget=3.0, limits=(1.25,) * 3)
    efficacy_values = [[[0.0, 0.0] for _ in range(3)] for _ in range(3)]
    efficacy_values[0][1][1] = 0.8
    efficacy_values[1][2][0] = 0.6
    efficacy_nk = TeachingEfficacyNK(
        org.agent_ids, org.skill_ids,
        tuple(tuple(tuple(pair) for pair in row) for row in efficacy_values),
    )
    relation = (0, 1, 1)
    nk_relation = ("A0", "A1", "S1")
    nk_policy = P1FixedTeachingNK(nk_relation) if policy_kind == "p1" else P2AdaptiveTeachingNK((nk_relation, ("A1", "A2", "S0")))
    legacy_policy = P1FixedTeaching(relation) if policy_kind == "p1" else P2AdaptiveTeaching((relation, (1, 2, 0)))
    params = TeachingParametersNK(transfer_rate=0.4)
    policy_params = TeachingPolicyParametersNK(effort=0.25, efficacy_prior_mean=0.5,
                                               efficacy_threshold=0.35, target_competence=0.7)
    nk_problems = tuple(ProblemSpecNK(f"p{i}", req, 3.0, (0.5, 0.5))
                        for i, req in enumerate(((0.0, 0.9), (0.0, 0.9), (0.5, 0.0))))
    old_problems = tuple(IntegratedProblem(
        ProblemSpec(f"p{i}", req, 3.0, max_effort_per_expert=1.25), (0.5, 0.5)
    ) for i, req in enumerate(((0.0, 0.9), (0.0, 0.9), (0.5, 0.0))))
    eta = ((0.1, 0.12), (0.09, 0.08), (0.11, 0.1))
    nk = run_nk_production_sequence(
        org, nk_problems, max_candidates=832,
        individual_learning=mis, learning_profile=LearningProfileNK(eta),
        teaching_enabled=True, teaching_efficacy=efficacy_nk,
        teaching_parameters=params, policy_parameters=policy_params, policy=nk_policy,
    )
    team = TeamState(tuple(ExpertState(f"A{i}", row, row) for i, row in enumerate(competence)))
    old = run_integrated_sequence(
        team, old_problems, legacy_policy,
        learning=LearningProfile(eta), teaching_efficacy=_legacy_efficacy(efficacy_values),
        parameters=TeachingParameters(
            transfer_rate=0.4, effort=0.25, outcome_noise_sd=0.0,
            production_observation_noise_sd=0.0, competence_prior_variance=0.0,
            efficacy_prior_mean=0.5, efficacy_threshold=0.35, target_competence=0.7,
        ), individual_learning=mis, organizational_learning=True,
    )
    assert len(nk.records) == len(old.records)
    for nk_row, old_row in zip(nk.records, old.records):
        assert _convert_joint(JointActionNK(nk_row.production.allocation, nk_row.teaching_action)) == old_row.action
        assert nk_row.production.outputs == pytest.approx(old_row.outputs)
        assert nk_row.production.functional_result.success == old_row.functional_result.success
        assert nk_row.production.ces_reward == pytest.approx(old_row.ces_reward)
        assert nk_row.total_resource_used == pytest.approx(old_row.total_resource_used)
        for got, expected in zip(nk_row.production.competence_after, old_row.competence_real_after):
            assert got == pytest.approx(expected)
    for got, expected in zip(nk.final_state.competence_real, old.final_team.real_matrix):
        assert got == pytest.approx(expected)


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (3, 2), (4, 3)])
def test_policies_execute_nk_geometries_and_keep_p0_production_only(n, k):
    competence = tuple(tuple(0.1 + 0.05 * ((i + j) % 5) for j in range(k)) for i in range(n))
    org = _org(n, k, competence, budget=min(float(n), 2.0), limits=(1.0,) * n)
    problem = ProblemSpecNK("all", tuple(0.8 for _ in range(k)), 2.0)
    choices = None if k == 2 else _effort_choices(n, k)
    production_bound = (4**n if k == 2 and choices is None else
                        prod(len(agent_choices) for agent_choices in choices)
                        if choices is not None else (k + 1)**n)
    max_candidates = production_bound * (1 + n * (n - 1) * k)
    efficacy = _efficacy(org)
    p0 = run_nk_production_sequence(
        org, (problem,), max_candidates=max_candidates, per_agent_effort_choices=choices,
        teaching_enabled=True, teaching_efficacy=efficacy, policy=P0ProductionOnlyNK(),
    )
    assert p0.records[0].policy_name == "P0_PRODUCTION_ONLY_NK"
    assert p0.records[0].teaching_action is None
    assert p0.records[0].total_resource_used == p0.records[0].productive_effort_used
    if n > 1:
        relation = (org.agent_ids[0], org.agent_ids[1], org.skill_ids[0])
        p1 = run_nk_production_sequence(
            org, (problem,), max_candidates=max_candidates, per_agent_effort_choices=choices,
            teaching_enabled=True, teaching_efficacy=efficacy,
            policy=P1FixedTeachingNK(relation),
        )
        p2 = run_nk_production_sequence(
            org, (problem,), max_candidates=max_candidates, per_agent_effort_choices=choices,
            teaching_enabled=True, teaching_efficacy=efficacy,
            policy=P2AdaptiveTeachingNK((relation,)),
        )
        for run in (p1, p2):
            row = run.records[0]
            assert row.total_resource_used <= 2.0 + 1e-12
            assert row.unused_collective_capacity >= 0
            assert row.teaching_action is None or row.teaching_action.teacher_id != row.teaching_action.learner_id
    else:
        with pytest.raises(ValueError, match="distinct teacher and learner"):
            P1FixedTeachingNK((org.agent_ids[0], org.agent_ids[0], org.skill_ids[0]))
        with pytest.raises(ValueError, match="non-empty unique relation"):
            P2AdaptiveTeachingNK(())


def test_p2_rule_success_unseen_threshold_tie_and_disabled_teaching_fallback():
    org = _org(3, 2, ((0.2, 0.2), (0.1, 0.1), (0.1, 0.1)), budget=3.0)
    problem = ProblemSpecNK("need", (0.0, 0.9), 2.0)
    efficacy = _efficacy(org, overrides=((0, 1, 1, 0.8), (0, 2, 1, 0.8)))
    relations = (("A0", "A2", "S1"), ("A0", "A1", "S1"))
    p2 = P2AdaptiveTeachingNK(relations)
    run = run_nk_production_sequence(
        org, (problem,), max_candidates=832, teaching_enabled=True,
        teaching_efficacy=efficacy, policy=p2,
        policy_parameters=TeachingPolicyParametersNK(effort=0.25, target_competence=0.99),
    )
    # Both relations are initially unseen; configured exploration order wins.
    assert run.records[0].teaching_action.learner_id == "A2"
    # With teaching disabled, the historical absence-of-feasible-lesson path
    # falls back to the same production-only decision.
    disabled = run_nk_production_sequence(
        org, (problem,), max_candidates=64, teaching_enabled=False,
        policy=p2,
    )
    p0 = run_nk_production_sequence(org, (problem,), max_candidates=64,
                                    policy=P0ProductionOnlyNK())
    assert disabled.records[0].teaching_action is None
    assert disabled.records[0].production.allocation == p0.records[0].production.allocation

    # A successful best production action suppresses teaching, even for unseen relations.
    easy = ProblemSpecNK("easy", (0.0, 0.1), 2.0)
    easy_run = run_nk_production_sequence(
        org, (easy,), max_candidates=832, teaching_enabled=True,
        teaching_efficacy=efficacy, policy=p2,
    )
    assert easy_run.records[0].teaching_action is None


def test_adaptive_memory_uses_observed_normalized_gain_not_private_tensor():
    org = _org(2, 2, ((0.2, 0.2), (0.1, 0.05)), budget=2.0)
    efficacy = _efficacy(org, overrides=((0, 1, 1, 0.9),))
    problems = tuple(ProblemSpecNK(f"p{i}", (0.0, 0.9), 2.0) for i in range(3))
    run = run_nk_production_sequence(
        org, problems, max_candidates=9 * (1 + 4),
        per_agent_effort_choices=_effort_choices(2, 2),
        teaching_enabled=True, teaching_efficacy=efficacy,
        policy=P2AdaptiveTeachingNK((("A0", "A1", "S1"),)),
        policy_parameters=TeachingPolicyParametersNK(effort=0.25, target_competence=0.99),
        teaching_parameters=TeachingParametersNK(transfer_rate=0.8),
    )
    first = run.records[0]
    assert first.formative_efficacy_observation == pytest.approx(0.9)
    assert first.efficacy_memory_after[0].mean == pytest.approx(0.9)
    assert run.records[1].efficacy_memory_before == run.records[1 - 1].efficacy_memory_after
    # Decision view has no private tensor or true-state field.
    assert not hasattr(NKDecisionView, "teaching_efficacy")
    assert not hasattr(NKDecisionView, "competence_real")


def test_p2_seen_relation_ties_use_legacy_numeric_index_order():
    org = _org(2, 2, ((0.1, 0.1), (0.1, 0.1)), budget=2.0)
    problem = ProblemSpecNK("tie", (0.0, 0.9), 2.0)
    efficacy = _efficacy(org)
    actions = enumerate_feasible_joint_actions_nk(
        org, problem, max_candidates=80, teaching_enabled=True,
        teaching_efficacy=efficacy, teaching_effort=0.25,
    )
    view = NKDecisionView(
        0, 1, problem.problem_id, org.agent_ids, org.skill_ids,
        problem.requirements, org.competence_initial, actions,
    )
    low = ("A0", "A1", "S1")  # legacy indices (0, 1, 1)
    high = ("A1", "A0", "S1") # legacy indices (1, 0, 1)
    memory = OrganizationMemoryNK((EfficacyEstimateNK(high, 1, 0.8),
                                   EfficacyEstimateNK(low, 1, 0.8)))
    policy = P2AdaptiveTeachingNK((high, low))
    chosen = policy.choose(view, memory, TeachingPolicyParametersNK(target_competence=0.99))
    assert (chosen.teaching.teacher_id, chosen.teaching.learner_id,
            chosen.teaching.skill_id) == low


def test_policies_receive_observable_view_and_memory_not_private_configuration():
    org = _org(2, 2, ((0.2, 0.2), (0.1, 0.1)), budget=2.0)
    problem = ProblemSpecNK("observe", (0.2, 0.2), 2.0)

    class CapturePolicy:
        name = "CAPTURE"
        seen = None

        def choose(self, view, memory, parameters):
            self.seen = (view, memory, parameters)
            return next(action for action in view.feasible_actions if action.teaching is None)

    policy = CapturePolicy()
    run_nk_production_sequence(
        org, (problem,), max_candidates=64, teaching_enabled=False, policy=policy,
    )
    view, memory, _ = policy.seen
    assert view.estimated_competencies == org.competence_initial
    assert not hasattr(view, "competence_real")
    assert not hasattr(view, "teaching_efficacy")
    assert not hasattr(view, "competence_initial")
    assert not hasattr(memory, "teaching_efficacy")
    assert not hasattr(policy, "organization")


def test_policies_decline_below_threshold_and_when_no_matching_action_is_feasible():
    org = _org(2, 2, ((0.2, 0.2), (0.1, 0.05)), budget=0.5, limits=(0.5, 0.5))
    efficacy = _efficacy(org, overrides=((0, 1, 1, 0.0),))
    problem = ProblemSpecNK("tight", (0.0, 0.9), 0.5)
    p2 = P2AdaptiveTeachingNK((("A0", "A1", "S1"),))
    run = run_nk_production_sequence(
        org, (problem, problem), max_candidates=80, teaching_enabled=True,
        teaching_efficacy=efficacy, policy=p2,
        policy_parameters=TeachingPolicyParametersNK(effort=0.25, efficacy_threshold=0.35,
                                                     target_competence=0.99),
    )
    # First event is the prescribed unseen probe; after its zero signal, P2 declines.
    assert run.records[0].teaching_action is not None
    assert run.records[1].teaching_action is None
    assert P2AdaptiveTeachingNK((("A0", "A1", "S1"),)).name == "P2_ADAPTIVE_TEACHING"


def test_organizational_learning_toggle_preserves_legacy_p2_unseen_behavior():
    org = _org(2, 2, ((0.2, 0.2), (0.1, 0.05)), budget=2.0)
    efficacy = _efficacy(org, overrides=((0, 1, 1, 0.9),))
    problem = ProblemSpecNK("repeat", (0.0, 0.9), 2.0)
    p2 = P2AdaptiveTeachingNK((("A0", "A1", "S1"),))
    no_update = run_nk_production_sequence(
        org, (problem, problem), max_candidates=80,
        teaching_enabled=True, teaching_efficacy=efficacy,
        policy=p2, organizational_learning=False,
        policy_parameters=TeachingPolicyParametersNK(target_competence=0.99),
    )
    assert all(row.teaching_action is not None for row in no_update.records)
    assert all(not row.organization_updated for row in no_update.records)
    with_update = run_nk_production_sequence(
        org, (problem, problem), max_candidates=80,
        teaching_enabled=True, teaching_efficacy=efficacy,
        policy=p2, organizational_learning=True,
        policy_parameters=TeachingPolicyParametersNK(target_competence=0.99),
    )
    assert with_update.records[0].teaching_action is not None
    assert with_update.records[1].teaching_action is not None
    assert all(row.organization_updated for row in with_update.records)


@pytest.mark.parametrize("bad", [
    lambda: P1FixedTeachingNK(("unknown", "A1", "S0")),
    lambda: P2AdaptiveTeachingNK((("A0", "A1", "missing"),)),
])
def test_bad_relation_ids_fail_at_decision_not_as_a_silent_fallback(bad):
    org = _org(2, 2, ((0.2, 0.2), (0.1, 0.1)))
    policy = bad()
    with pytest.raises(ValueError, match="unknown agent or skill"):
        run_nk_production_sequence(
            org, (ProblemSpecNK("p", (0.2, 0.2), 2.0),),
            max_candidates=64, policy=policy,
        )
