"""MIS-v2 dimension generalization and N×K learning episode tests."""

import hashlib

import pytest

from hls.hls_lab_dynamic import (
    CompetenceInformationMode,
    LearningProfile,
    advance_team,
    make_dynamic_team,
)
from hls.hls_lab_nk_execution import (
    NKLearningRunResult,
    run_nk_production_sequence,
    serialize_nk_learning_result,
    serialize_nk_production_result,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_production import productive_outputs_nk
from hls.hls_lab_v1 import ProblemSpec, make_team
from hls.hls_lab_v1_integrated import (
    IntegratedProblem,
    P0ProductionOnly,
    TeachingEfficacy,
    TeachingParameters,
    run_integrated_sequence,
)


def _config(n, k, *, competence=None, limits=None, budget=None, estimate=None):
    competence = competence or tuple(
        tuple(0.15 + 0.08 * ((i + j) % 7) for j in range(k)) for i in range(n)
    )
    return OrganizationConfigNK(
        tuple(f"A{i}" for i in range(n)), tuple(f"S{j}" for j in range(k)), competence,
        tuple(limits or (1.0,) * n), float(n if budget is None else budget), estimate,
    )


def _catalog(n, k):
    zero = (0.0,) * k
    axes = tuple(tuple(1.0 if j == skill else 0.0 for j in range(k)) for skill in range(k))
    return tuple((zero, *axes) for _ in range(n))


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (3, 2), (4, 3)])
def test_learning_runner_persists_competence_across_same_and_changed_demand(n, k):
    config = _config(n, k, limits=(0.5,) + (1.0,) * (n - 1), budget=min(2.0, float(n)))
    problems = (
        ProblemSpecNK("repeat-a", tuple(0.15 for _ in range(k)), 2.0),
        ProblemSpecNK("repeat-b", tuple(0.15 for _ in range(k)), 2.0),
        ProblemSpecNK("changed", tuple(0.05 if j % 2 else 0.3 for j in range(k)), 2.0),
    )
    eta = tuple(tuple(0.08 + 0.01 * ((i + j) % 4) for j in range(k)) for i in range(n))
    kwargs = dict(max_candidates=(k + 1) ** n, per_agent_effort_choices=_catalog(n, k))
    run = run_nk_production_sequence(
        config, problems, learning_profile=LearningProfileNK(eta), individual_learning=True, **kwargs,
    )
    assert isinstance(run, NKLearningRunResult)
    assert len(run.records) == 3
    for t, row in enumerate(run.records):
        record = row.production
        assert record.competence_before == (config.competence_initial if t == 0
                                             else run.records[t - 1].production.competence_after)
        assert record.outputs == productive_outputs_nk(record.competence_before, record.allocation)
        assert record.competence_after == tuple(
            tuple(record.competence_before[i][j] + row.competence_increment[i][j]
                  for j in range(k)) for i in range(n)
        )
        assert record.competence_after == mis_v2_transition_nk(
            record.competence_before, record.allocation, LearningProfileNK(eta),
        )
        assert record.productive_effort_used <= record.effective_collective_budget + 1e-12
        assert all(0.0 <= value <= 1.0 for agent in record.competence_after for value in agent)
    replay = run_nk_production_sequence(
        config, problems, learning_profile=LearningProfileNK(eta), individual_learning=True, **kwargs,
    )
    assert serialize_nk_learning_result(run) == serialize_nk_learning_result(replay)
    assert hashlib.sha256(serialize_nk_learning_result(run).encode()).digest() == hashlib.sha256(
        serialize_nk_learning_result(replay).encode()
    ).digest()


def test_mis_off_preserves_phase2_record_and_serialization_contract():
    config = _config(2, 2, competence=((0.2, 0.6), (0.8, 0.3)), budget=2.0)
    problems = (ProblemSpecNK("p1", (0.2, 0.3), 1.5), ProblemSpecNK("p2", (0.3, 0.1), 2.0))
    kwargs = dict(max_candidates=9, per_agent_effort_choices=_catalog(2, 2))
    phase2 = run_nk_production_sequence(config, problems, **kwargs)
    explicit_off = run_nk_production_sequence(
        config, problems, individual_learning=False, learning_profile=LearningProfileNK(((0.2, 0.3), (0.1, 0.4))),
        **kwargs,
    )
    assert type(phase2) is type(explicit_off)
    assert phase2 == explicit_off
    assert serialize_nk_production_result(phase2) == serialize_nk_production_result(explicit_off)
    assert all(row.competence_before == row.competence_after for row in explicit_off.records)
    assert explicit_off.final_state.competence_real == config.competence_initial

    eta = LearningProfileNK(((0.2, 0.3), (0.1, 0.4)))
    on = run_nk_production_sequence(
        config, problems, individual_learning=True, learning_profile=eta, **kwargs,
    )
    assert isinstance(on, NKLearningRunResult)
    assert tuple(row.problem_id for row in explicit_off.records) == tuple(
        row.production.problem_id for row in on.records
    )
    # The first decision/outcome is matched because both modes start from the
    # same competence matrix; only post-production MIS-v2 can then diverge.
    assert on.records[0].production.competence_before == explicit_off.records[0].competence_before
    assert on.records[0].production.action_id == explicit_off.records[0].action_id
    assert on.records[0].production.allocation == explicit_off.records[0].allocation
    assert on.records[0].production.outputs == explicit_off.records[0].outputs
    assert on.records[0].production.competence_after != on.records[0].production.competence_before
    assert explicit_off.final_state.competence_real == config.competence_initial


def test_mis_on_requires_profile_and_applies_only_after_current_production():
    config = _config(1, 1, competence=((0.2,),), limits=(1.0,), budget=1.0)
    problem = ProblemSpecNK("one", (0.1,), 1.0)
    kwargs = dict(max_candidates=2, per_agent_effort_choices=(((0.0,), (1.0,)),))
    with pytest.raises(ValueError, match="requires a LearningProfileNK"):
        run_nk_production_sequence(config, (problem,), individual_learning=True, **kwargs)
    run = run_nk_production_sequence(
        config, (problem, problem), individual_learning=True,
        learning_profile=LearningProfileNK(((0.2,),)), **kwargs,
    )
    first, second = (row.production for row in run.records)
    assert first.outputs == productive_outputs_nk(config.competence_initial, first.allocation)
    assert second.competence_before == first.competence_after
    assert second.outputs == productive_outputs_nk(first.competence_after, second.allocation)


def test_nk_three_by_two_transition_matches_authoritative_legacy_advance_team():
    real = ((0.1, 0.4), (0.5, 0.0), (1.0, 0.75))
    effort = ((0.0, 0.5), (0.25, 1.0), (0.75, 0.0))
    eta = ((0.1, 0.2), (0.15, 0.3), (0.25, 0.05))
    nk_after = mis_v2_transition_nk(real, effort, LearningProfileNK(eta))
    legacy_profile = LearningProfile(eta)  # type: ignore[arg-type]
    legacy_team = make_dynamic_team(real, information_mode=CompetenceInformationMode.ORACLE)
    legacy_after = advance_team(legacy_team, effort, legacy_profile, enabled=True,
                                update_estimated=False)
    assert nk_after == tuple(expert.competence_real for expert in legacy_after.experts)


def test_nk_three_by_two_learning_runner_matches_legacy_production_and_transition():
    real = ((0.2, 0.4), (0.1, 0.05), (0.95, 0.1))
    eta = ((0.1, 0.2), (0.15, 0.3), (0.25, 0.05))
    config = _config(3, 2, competence=real, budget=3.0)
    nk_problem = ProblemSpecNK("mixed", (0.3, 0.2), 1.5)
    nk = run_nk_production_sequence(
        config, (nk_problem,), max_candidates=64,
        individual_learning=True, learning_profile=LearningProfileNK(eta),
    ).records[0].production
    zeros = tuple(tuple((0.0, 0.0) for _ in range(3)) for _ in range(3))
    legacy = run_integrated_sequence(
        make_team(real), (IntegratedProblem(ProblemSpec("mixed", (0.3, 0.2), 1.5)),),
        P0ProductionOnly(), learning=LearningProfile(eta), teaching_efficacy=TeachingEfficacy(zeros),
        parameters=TeachingParameters(production_observation_noise_sd=0.0),
        individual_learning=True, organizational_learning=False,
    ).records[0]
    assert nk.allocation == legacy.action.production
    assert nk.outputs == legacy.outputs
    assert nk.functional_result.success == legacy.functional_result.success
    assert nk.functional_result.deficits == legacy.functional_result.deficits
    assert nk.functional_result.normalized_deficit == legacy.functional_result.normalized_deficit
    assert nk.functional_result.margin == legacy.functional_result.margin
    assert nk.ces_reward == legacy.ces_reward
    assert nk.productive_effort_used == legacy.production_effort
    assert nk.competence_after == legacy.competence_real_after
