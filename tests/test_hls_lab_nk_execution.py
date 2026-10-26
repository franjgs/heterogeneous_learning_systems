"""Acceptance tests for production-only N×K execution and dimensioned P0."""

import hashlib
import pytest

from hls.discover_v0 import JOINT_ACTIONS, ces_reward
from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_v1 import ProblemSpec, make_team
from hls.hls_lab_v1_integrated import (
    IntegratedProblem, P0ProductionOnly, TeachingEfficacy,
    TeachingParameters, run_integrated_sequence,
)
from hls.hls_lab_nk_execution import (
    run_nk_production_sequence,
    serialize_nk_production_result,
)
from hls.hls_lab_nk_production import (
    choose_p0_action_nk,
    ces_reward_nk,
    evaluate_problem_nk,
    p0_rank_nk,
    productive_outputs_nk,
)
from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    ProblemSpecNK,
    enumerate_productive_action_entries_nk,
    enumerate_productive_allocations_nk,
)


def _organization(n, k, *, competence=None, limits=None, budget=3.0, estimate=None):
    if competence is None:
        competence = tuple(tuple(0.2 + 0.1 * ((i + j) % 5) for j in range(k)) for i in range(n))
    return OrganizationConfigNK(
        tuple(f"A{i}" for i in range(n)), tuple(f"S{i}" for i in range(k)),
        competence, tuple(limits or (1.0,) * n), budget, estimate,
    )


def _effort_catalog(n, k):
    zero = (0.0,) * k
    one_per_skill = tuple(tuple(1.0 if j == skill else 0.0 for j in range(k))
                          for skill in range(k))
    return tuple((zero, *one_per_skill) for _ in range(n))


@pytest.mark.parametrize("n,k,budget", [(1, 1, 1.0), (2, 2, 2.0), (3, 2, 3.0), (4, 3, 3.0)])
def test_production_episode_runs_supported_geometries_and_freezes_competencies(n, k, budget):
    config = _organization(n, k, budget=budget)
    problems = (
        ProblemSpecNK("ordinary", tuple(0.2 for _ in range(k)), budget),
        ProblemSpecNK("infeasible", tuple(2.0 for _ in range(k)), budget),
    )
    run = run_nk_production_sequence(
        config, problems, max_candidates=(4**n if k == 2 else (k + 1) ** n),
        per_agent_effort_choices=None if k == 2 else _effort_catalog(n, k),
    )
    assert len(run.records) == 2
    assert all(row.competence_before == config.competence_initial == row.competence_after
               for row in run.records)
    assert all(len(row.outputs) == k and len(row.allocation) == n for row in run.records)
    assert all(tuple(sum(agent_row[skill] for agent_row in row.individual_outputs)
                      for skill in range(k)) == row.outputs for row in run.records)
    assert all(row.productive_effort_used <= row.effective_collective_budget + 1e-12
               for row in run.records)
    assert all(row.individual_effort_used[i] <= config.effort_limits[i] + 1e-12
               for row in run.records for i in range(n))
    assert all(row.unused_collective_capacity >= 0 for row in run.records)


def test_additive_production_matches_hand_calculation_and_individual_outputs():
    competence = ((0.8, 0.0), (0.2, 1.0))
    allocation = ((0.5, 0.5), (1.0, 0.0))
    assert productive_outputs_nk(competence, allocation) == (0.6000000000000001, 0.0)
    assert tuple(sum(row[k] for row in ((0.4, 0.0), (0.2, 0.0))) for k in range(2)) == (0.6000000000000001, 0.0)


def test_individual_effort_limits_and_effective_shared_budget_are_accounted_separately():
    config = _organization(2, 2, competence=((1.0, 0.0), (0.5, 1.0)),
                           limits=(0.5, 1.0), budget=1.25)
    problem = ProblemSpecNK("caps", (0.4, 0.2), 0.75)
    choices = (((0.0, 0.0), (0.5, 0.0)), ((0.0, 0.0), (0.5, 0.5), (1.0, 0.0)))
    result = run_nk_production_sequence(config, (problem,), max_candidates=6,
                                        per_agent_effort_choices=choices)
    row = result.records[0]
    assert row.organization_effort_budget == 1.25
    assert row.problem_effort_budget == row.effective_collective_budget == 0.75
    assert row.productive_effort_used == sum(row.individual_effort_used)
    assert row.unused_collective_capacity == pytest.approx(0.75 - row.productive_effort_used)
    assert row.outputs == productive_outputs_nk(config.competence_initial, row.allocation)


def test_feasibility_boundary_success_deficit_and_zero_effort_controls():
    config = _organization(1, 1, competence=((0.5,),), limits=(1.0,), budget=1.0)
    choices = (((0.0,), (1.0,)),)
    below = ProblemSpecNK("below", (0.5 + 1e-6,), 1.0)
    exact = ProblemSpecNK("exact", (0.5,), 1.0)
    above = ProblemSpecNK("above", (0.5 - 1e-6,), 1.0)
    runs = [run_nk_production_sequence(config, (problem,), max_candidates=2,
                                      per_agent_effort_choices=choices).records[0]
            for problem in (below, exact, above)]
    assert [row.functional_result.success for row in runs] == [False, True, True]
    assert runs[0].functional_result.normalized_deficit > 0
    assert runs[1].functional_result.normalized_deficit == 0
    assert evaluate_problem_nk((0.0, 0.0), (0.0, 0.1)).deficits == (0.0, 0.1)


def test_p0_uses_success_then_deficit_margin_effort_and_first_catalog_tie_not_ces():
    problem = ProblemSpecNK("rank", (0.5, 0.5), 2.0, ces_weights=(0.99, 0.01))
    comp = ((1.0, 1.0),)
    fail = ((1.0, 0.0),)
    success = ((0.5, 0.5),)
    assert p0_rank_nk(success, comp, problem) > p0_rank_nk(fail, comp, problem)

    # Equal success/margin; P0 preserves the first tie even though the later
    # allocation has greater CES under these weights.
    tie_problem = ProblemSpecNK("tie", (0.5, 0.5), 1.0, ces_weights=(0.99, 0.01))
    first, later = ((0.5, 0.0),), ((0.0, 0.5),)
    idx, chosen = choose_p0_action_nk((first, later), ((1.0, 1.0),), tie_problem)
    assert idx == 0 and chosen == first
    assert ces_reward_nk((0.5, 0.0), tie_problem.ces_weights) > ces_reward_nk(
        (0.0, 0.5), tie_problem.ces_weights
    )

    # Deficit and then margin are the second/third criteria.
    deficit_problem = ProblemSpecNK("deficit", (0.8, 0.8), 1.0)
    worse_deficit, better_deficit = ((0.8, 0.2),), ((0.6, 0.6),)
    assert p0_rank_nk(better_deficit, ((1.0, 1.0),), deficit_problem) > p0_rank_nk(
        worse_deficit, ((1.0, 1.0),), deficit_problem
    )
    margin_problem = ProblemSpecNK("margin", (0.5, 0.5), 1.0)
    lower_margin, higher_margin = ((0.6, 0.9),), ((0.7, 0.7),)
    assert p0_rank_nk(higher_margin, ((1.0, 1.0),), margin_problem) > p0_rank_nk(
        lower_margin, ((1.0, 1.0),), margin_problem
    )

    # Effort is the final ranking term; extra effort in a zero-competence
    # coordinate cannot improve production and must lose the tie.
    effort_problem = ProblemSpecNK("effort", (0.2, 0.0), 2.0)
    low, high = ((0.2, 0.0),), ((0.2, 0.5),)
    assert p0_rank_nk(low, ((1.0, 0.0),), effort_problem) > p0_rank_nk(
        high, ((1.0, 0.0),), effort_problem
    )


def test_ces_generalization_is_exactly_legacy_for_two_skills():
    for outputs, weights in (((0.0, 0.4), (0.5, 0.5)), ((0.7, 0.2), (0.8, 0.2)), ((1.0, 0.0), (1.0, 0.0))):
        assert ces_reward_nk(outputs, weights) == ces_reward(outputs, weights)


def test_nk_p0_matches_legacy_3x2_decisions_and_outcomes_for_same_inputs():
    competence = ((0.2, 0.4), (0.1, 0.05), (0.95, 0.1))
    config = _organization(3, 2, competence=competence, limits=(1.0,) * 3, budget=3.0)
    cases = (("skill1", (0.0, 0.6), 3.0), ("skill0", (0.75, 0.0), 3.0),
             ("mixed", (0.3, 0.2), 1.5))
    for name, requirements, budget in cases:
        nk_problem = ProblemSpecNK(name, requirements, budget)
        nk = run_nk_production_sequence(config, (nk_problem,), max_candidates=64).records[0]
        legacy_problem = ProblemSpec(name, requirements, budget, max_effort_per_expert=1.0)
        zeros = tuple(tuple((0.0, 0.0) for _ in range(3)) for _ in range(3))
        efficacy = TeachingEfficacy(zeros)
        legacy = run_integrated_sequence(
            make_team(competence), (IntegratedProblem(legacy_problem),), P0ProductionOnly(),
            learning=LearningProfile(((0.1, 0.1),) * 3), teaching_efficacy=efficacy,
            parameters=TeachingParameters(production_observation_noise_sd=0.0),
            individual_learning=False, organizational_learning=False,
        ).records[0]
        assert JOINT_ACTIONS[nk.action_id] == legacy.action.production
        assert nk.outputs == legacy.outputs
        assert nk.functional_result.success == legacy.functional_result.success
        assert nk.functional_result.normalized_deficit == legacy.functional_result.normalized_deficit
        assert nk.functional_result.margin == legacy.functional_result.margin
        assert nk.ces_reward == legacy.ces_reward
        assert nk.productive_effort_used == legacy.production_effort


def test_catalogue_identifiers_survive_budget_filtering_and_3x2_catalogue_stays_64():
    config = _organization(3, 2, budget=3.0)
    problem = ProblemSpecNK("filtered", (0.2, 0.2), 1.0)
    entries = enumerate_productive_action_entries_nk(config, problem, max_candidates=64)
    actions = enumerate_productive_allocations_nk(config, problem, max_candidates=64)
    assert len(actions) < 64
    assert tuple(action for _, action in entries) == actions
    assert tuple(action_id for action_id, _ in entries) == tuple(
        i for i, action in enumerate(JOINT_ACTIONS)
        if sum(map(sum, action)) <= 1.0 + 1e-12
    )


def test_replay_serialization_and_frozen_state_are_deterministic():
    config = _organization(2, 2, competence=((0.0, 1.0), (0.4, 0.7)),
                           estimate=((1.0, 0.0), (0.1, 0.1)), budget=2.0)
    problems = (ProblemSpecNK("p1", (0.3, 0.2), 1.0, (0.8, 0.2)),
                ProblemSpecNK("p2", (0.1, 0.5), 2.0, (0.25, 0.75)))
    kwargs = dict(max_candidates=9, per_agent_effort_choices=_effort_catalog(2, 2))
    first = run_nk_production_sequence(config, problems, **kwargs)
    second = run_nk_production_sequence(config, problems, **kwargs)
    assert serialize_nk_production_result(first) == serialize_nk_production_result(second)
    assert hashlib.sha256(serialize_nk_production_result(first).encode()).hexdigest() == (
        "957b748589b9b58db2aab2dad2080316188d208b878aead120a8e1f8fb571566"
    )
    assert all(row.competence_before == row.competence_after for row in first.records)
    assert first.records[0].individual_effort_limits == (1.0, 1.0)
    different_estimate = _organization(2, 2, competence=config.competence_initial,
                                       estimate=((0.0, 0.0), (1.0, 1.0)), budget=2.0)
    changed_info = run_nk_production_sequence(different_estimate, problems, **kwargs)
    assert first.records == changed_info.records
    assert first.final_state == changed_info.final_state
    assert first.final_state.competence_estimated == first.final_state.competence_real


def test_zero_effort_and_resource_conservation_are_explicit():
    config = _organization(1, 1, competence=((0.0,),), limits=(0.0,), budget=0.0)
    problem = ProblemSpecNK("zero", (0.5,), 0.0)
    row = run_nk_production_sequence(config, (problem,), max_candidates=2,
                                    per_agent_effort_choices=(((0.0,), (0.5,)),)).records[0]
    assert row.allocation == ((0.0,),)
    assert row.outputs == (0.0,)
    assert row.productive_effort_used == row.unused_collective_capacity == 0.0
    assert row.functional_result.success is False


def test_dimension_mismatch_and_invalid_ces_weights_fail_closed():
    config = _organization(1, 2)
    with pytest.raises(ValueError, match="does not match organization K"):
        run_nk_production_sequence(config, (ProblemSpecNK("bad", (0.2,), 1.0),), max_candidates=1,
                                   per_agent_effort_choices=(((0.0, 0.0),),))
    with pytest.raises(ValueError, match="ces_weights"):
        ProblemSpecNK("bad-weights", (0.2, 0.2), 1.0, (0.4, 0.4))
