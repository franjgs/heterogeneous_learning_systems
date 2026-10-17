"""Integration tests for the explicitly selected N×K Nembhard adaptation."""

import pytest

from hls.hls_lab_nk_execution import (
    NKEnvironmentRunResult,
    NKNembhardDirectRunResult,
    run_nk_production_sequence,
    serialize_nk_nembhard_direct_result,
    serialize_nk_production_result,
    serialize_nk_learning_result,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_environment import DemandRegimeNK, ExogenousEnvironmentConfigNK
from hls.synthetic.c5 import StationaryTaskDemand
from hls.hls_lab_nk_nembhard import (
    NembhardDirectExecutionNK,
    NembhardDirectProfileNK,
    NembhardDirectStateNK,
    NembhardOutputUnitContract,
)


def organization(n, k, *, competence=None, limits=None, budget=None):
    competence = competence or tuple((0.0,) * k for _ in range(n))
    return OrganizationConfigNK(
        tuple(f"A{i}" for i in range(n)), tuple(f"S{i}" for i in range(k)),
        competence, tuple(limits or (1.0,) * n), float(budget if budget is not None else n),
    )


def profile(n, k, *, kval=10.0, pval=0.0, rval=10.0):
    return NembhardDirectProfileNK(
        tuple((kval,) * k for _ in range(n)),
        tuple((pval,) * k for _ in range(n)),
        tuple((rval,) * k for _ in range(n)),
    )


def units():
    return NembhardOutputUnitContract(
        effort_intensity_unit="work_per_period",
        duration_unit="period",
        exposure_unit="work_unit",
        output_unit="task_output_unit",
        requirement_unit="task_output_unit",
    )


def test_explicit_mis_v2_selector_is_byte_identical_to_default_without_learning():
    org = organization(2, 2, competence=((0.2, 0.6), (0.8, 0.1)), budget=2.0)
    problems = (ProblemSpecNK("x", (0.2, 0.3), 2.0), ProblemSpecNK("y", (0.4, 0.1), 1.0))
    kwargs = dict(max_candidates=16)
    implicit = run_nk_production_sequence(org, problems, **kwargs)
    explicit = run_nk_production_sequence(org, problems, mechanism_id="mis_v2", **kwargs)
    assert serialize_nk_production_result(implicit) == serialize_nk_production_result(explicit)


def test_explicit_mis_v2_selector_is_byte_identical_to_default_with_mis_learning():
    org = organization(2, 2, competence=((0.2, 0.6), (0.8, 0.1)), budget=2.0)
    problems = (ProblemSpecNK("x", (0.2, 0.3), 2.0), ProblemSpecNK("y", (0.4, 0.1), 1.0))
    kwargs = dict(max_candidates=16, individual_learning=True,
                  learning_profile=LearningProfileNK(((0.2, 0.3), (0.1, 0.4))))
    implicit = run_nk_production_sequence(org, problems, **kwargs)
    explicit = run_nk_production_sequence(org, problems, mechanism_id="mis_v2", **kwargs)
    assert serialize_nk_learning_result(implicit) == serialize_nk_learning_result(explicit)


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (3, 2), (4, 3)])
def test_nembhard_direct_supports_nk_geometry_and_separate_experience(n, k):
    org = organization(n, k, competence=tuple((1.0,) * k for _ in range(n)), budget=n)
    problem = ProblemSpecNK("generic", tuple(1.0 for _ in range(k)), float(n))
    allocation = tuple(tuple(1.0 if skill == 0 else 0.0 for skill in range(k))
                       for _ in range(n))
    config = NembhardDirectExecutionNK(profile(n, k), (allocation,), units())
    run = run_nk_production_sequence(org, (problem,), max_candidates=1,
                                     mechanism_id="nembhard_direct", nembhard_execution=config)
    assert isinstance(run, NKNembhardDirectRunResult)
    assert run.mechanism_id == "nembhard_direct_v0.1_hls_adaptation"
    assert run.records[0].experience_before == tuple((0.0,) * k for _ in range(n))
    assert run.records[0].experience_after[0][0] == 1.0
    assert all(run.records[0].experience_after[i][j] == 1.0
               for i in range(n) for j in range(k) if j == 0)


def test_nembhard_production_uses_preperiod_experience_then_updates():
    org = organization(1, 1, competence=((0.0,),), budget=1.0)
    problem = ProblemSpecNK("manual", (4.0,), 1.0)
    allocation = ((0.5,),)
    direct_profile = NembhardDirectProfileNK(((12.0,),), ((3.0,),), ((9.0,),))
    config = NembhardDirectExecutionNK(
        direct_profile, (allocation, allocation), units(),
        initial_state=NembhardDirectStateNK(((2.0,),)), period_duration=2.0,
    )
    run = run_nk_production_sequence(org, (problem, problem), max_candidates=1,
                                     mechanism_id="nembhard_direct", nembhard_execution=config)
    first, second = run.records
    assert first.productivity_before[0][0] == pytest.approx(12 * 5 / 14)
    assert first.outputs == (pytest.approx(12 * 5 / 14),)
    assert first.experience_increment == ((1.0,),)
    assert first.experience_after == ((3.0,),)
    assert second.productivity_before[0][0] == pytest.approx(12 * 6 / 15)
    assert second.outputs == (pytest.approx(12 * 6 / 15),)
    assert second.experience_after == ((4.0,),)
    assert first.effective_work_used == 1.0
    # The HLS effort budget constrains intensity, not e*duration.
    assert first.productive_effort_used == 0.5
    assert first.unused_collective_capacity == pytest.approx(0.5)


def test_competence_fields_do_not_drive_nembhard_output_or_state():
    problems = (ProblemSpecNK("p", (1.0, 1.0), 2.0),)
    allocation = (((0.5, 0.5),),)
    config = NembhardDirectExecutionNK(profile(1, 2, kval=4.0, pval=1.0), allocation, units())
    low = organization(1, 2, competence=((0.0, 0.0),), budget=2.0)
    high = organization(1, 2, competence=((1.0, 1.0),), budget=2.0)
    a = run_nk_production_sequence(low, problems, max_candidates=1,
                                   mechanism_id="nembhard_direct", nembhard_execution=config)
    b = run_nk_production_sequence(high, problems, max_candidates=1,
                                   mechanism_id="nembhard_direct", nembhard_execution=config)
    assert a.records == b.records
    assert a.final_experience == b.final_experience


def test_exposure_updates_are_independent_by_agent_and_skill():
    org = organization(2, 2, budget=1.0)
    problem = ProblemSpecNK("independent", (0.1, 0.1), 1.0)
    allocation = (((0.0, 0.0), (0.0, 1.0)),)
    direct_profile = NembhardDirectProfileNK(
        ((2.0, 4.0), (6.0, 8.0)),
        ((0.0, 0.0), (0.0, 0.0)),
        ((1.0, 1.0), (1.0, 1.0)),
    )
    config = NembhardDirectExecutionNK(direct_profile, allocation, units())
    run = run_nk_production_sequence(org, (problem,), max_candidates=1,
                                     mechanism_id="nembhard_direct", nembhard_execution=config)
    assert run.final_experience == ((0.0, 0.0), (0.0, 1.0))
    assert run.records[0].productivity_before == ((0.0, 0.0), (0.0, 0.0))
    assert run.records[0].outputs == (0.0, 0.0)


def test_nembhard_resource_accounting_rejects_infeasible_allocations():
    org = organization(2, 2, limits=(0.25, 0.5), budget=0.6)
    problem = ProblemSpecNK("limits", (0.1, 0.1), 0.5)
    invalid_allocations = (((0.5, 0.0), (0.0, 0.0)),)
    config = NembhardDirectExecutionNK(profile(2, 2), invalid_allocations, units())
    with pytest.raises(ValueError, match="infeasible"):
        run_nk_production_sequence(org, (problem,), max_candidates=1,
                                   mechanism_id="nembhard_direct", nembhard_execution=config)


def test_nembhard_rejects_incompatible_units_and_unknown_or_mixed_mechanisms():
    with pytest.raises(ValueError, match="must match"):
        NembhardOutputUnitContract("work_per_period", "period", "work", "meters", "items")
    org = organization(1, 1)
    problem = ProblemSpecNK("p", (0.1,), 1.0)
    config = NembhardDirectExecutionNK(profile(1, 1), (((1.0,),),), units())
    with pytest.raises(ValueError, match="mechanism_id"):
        run_nk_production_sequence(org, (problem,), max_candidates=1,
                                   nembhard_execution=config)
    with pytest.raises(ValueError, match="MIS-v2, teaching"):
        run_nk_production_sequence(org, (problem,), max_candidates=1,
                                   mechanism_id="nembhard_direct", nembhard_execution=config,
                                   individual_learning=True,
                                   learning_profile=LearningProfileNK(((0.2,),)))
    with pytest.raises(ValueError, match="mechanism_id"):
        run_nk_production_sequence(org, (problem,), max_candidates=1,
                                   mechanism_id="unknown")


def test_nembhard_trace_json_is_reproducible_and_contains_mechanism_contract():
    org = organization(2, 2, limits=(0.5, 0.75), budget=1.25)
    problems = (ProblemSpecNK("one", (0.2, 0.2), 1.0, (0.7, 0.3)),
                ProblemSpecNK("two", (0.2, 0.2), 1.25))
    allocations = (((0.5, 0.0), (0.0, 0.5)), ((0.25, 0.0), (0.0, 0.75)))
    config = NembhardDirectExecutionNK(profile(2, 2), allocations, units())
    a = run_nk_production_sequence(org, problems, max_candidates=1,
                                   mechanism_id="nembhard_direct", nembhard_execution=config)
    b = run_nk_production_sequence(org, problems, max_candidates=1,
                                   mechanism_id="nembhard_direct", nembhard_execution=config)
    assert serialize_nk_nembhard_direct_result(a) == serialize_nk_nembhard_direct_result(b)
    assert '"mechanism_id":"nembhard_direct_v0.1_hls_adaptation"' in serialize_nk_nembhard_direct_result(a)
    assert a.records[0].productive_effort_used == 1.0
    assert a.records[0].unused_collective_capacity == 0.0


def test_generated_exogenous_demand_dispatches_to_nembhard_and_replays():
    org = organization(1, 1, budget=1.0)
    environment = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"steady": 1.0}),
        {"steady": DemandRegimeNK(
            "steady", (ProblemSpecNK("task", (0.2,), 1.0),), (1.0,),
        )},
        horizon=2,
    )
    direct = NembhardDirectExecutionNK(
        profile(1, 1, kval=2.0, pval=1.0), (((0.5,),), ((0.5,),)), units(),
    )
    first = run_nk_production_sequence(
        org, max_candidates=1, environment=environment, environment_seed=33,
        mechanism_id="nembhard_direct", nembhard_execution=direct,
    )
    replay = run_nk_production_sequence(
        org, max_candidates=1, environment=environment, environment_seed=33,
        mechanism_id="nembhard_direct", nembhard_execution=direct,
    )
    assert isinstance(first, NKEnvironmentRunResult)
    assert first == replay
    assert isinstance(first.execution, NKNembhardDirectRunResult)
    assert tuple(record.problem_id for record in first.execution.records) == tuple(
        problem.problem_id for problem in first.trajectory.problems
    )


def test_nembhard_config_rejects_bad_profile_dimensions_and_duration():
    with pytest.raises(ValueError, match="identical"):
        NembhardDirectProfileNK(((1.0,),), ((0.0,), (0.0,)), ((1.0,),))
    with pytest.raises(ValueError, match="strictly positive"):
        NembhardDirectExecutionNK(profile(1, 1), (((0.5,),),), units(), period_duration=0.0)
    with pytest.raises(ValueError, match="strictly positive"):
        NembhardDirectExecutionNK(profile(1, 1), (((0.5,),),), units(), period_duration=True)
    with pytest.raises(ValueError, match="non-empty rectangular"):
        NembhardDirectStateNK(((0.0, 1.0), (0.1,)))
