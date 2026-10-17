"""Tests for the perfect-information Nembhard productivity router."""

import pytest

from hls.hls_lab_nk_environment import DemandRegimeNK, ExogenousEnvironmentConfigNK
from hls.hls_lab_nk_execution import (
    NKEnvironmentRunResult,
    run_nk_production_sequence,
    serialize_nk_nembhard_direct_result,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, OrganizationResourcesNK, ProblemSpecNK
from hls.hls_lab_nk_nembhard import (
    NembhardDirectExecutionNK,
    NembhardDirectProfileNK,
    NembhardDirectStateNK,
    NembhardOutputUnitContract,
)
from hls.hls_lab_nk_nembhard_router import (
    NembhardOracleDecisionViewNK,
    NembhardOracleRouterNK,
)
from hls.synthetic.c5 import StationaryTaskDemand


def _units():
    return NembhardOutputUnitContract("effort/period", "period", "work", "output", "output")


def _organization(n, k, *, competence=None, budget=None):
    return OrganizationConfigNK(
        tuple(f"a{i}" for i in range(n)), tuple(f"s{j}" for j in range(k)),
        competence or tuple((0.0,) * k for _ in range(n)),
        (1.0,) * n, float(n if budget is None else budget),
    )


def _profile(n, k, *, kval=1.0, pval=1.0, rval=1.0):
    return NembhardDirectProfileNK(
        tuple((kval,) * k for _ in range(n)),
        tuple((pval,) * k for _ in range(n)),
        tuple((rval,) * k for _ in range(n)),
    )


def _binary_choices(n, k):
    zero = (0.0,) * k
    one = (1.0,) + (0.0,) * (k - 1)
    return tuple((zero, one) for _ in range(n))


def test_router_uses_hand_calculated_productivity_and_p0_functional_rank():
    org = _organization(2, 1, budget=1.0)
    problem = ProblemSpecNK("manual", (0.4,), 1.0)
    profile = NembhardDirectProfileNK(((0.7,), (1.0,)), ((1.0,), (0.0,)), ((1.0,), (1.0,)))
    router = NembhardOracleRouterNK()

    low = router.choose(
        NembhardOracleDecisionViewNK(
            resources=OrganizationResourcesNK.from_organization(org),
            problem=problem,
            experience=NembhardDirectStateNK(((0.0,), (0.0,))),
            profile=profile,
        ),
        max_candidates=4,
        per_agent_effort_choices=_binary_choices(2, 1),
    )
    assert low.allocation == ((1.0,), (0.0,))
    assert low.predicted_outputs == pytest.approx((0.35,))
    assert low.rank == pytest.approx((0, -0.125, -0.05, -1.0))
    assert low.feasible_candidate_count == 3


def test_router_changes_assignment_when_true_experience_changes():
    org = _organization(2, 1, budget=1.0)
    problem = ProblemSpecNK("switch", (0.4,), 1.0)
    profile = NembhardDirectProfileNK(((0.7,), (1.0,)), ((1.0,), (0.0,)), ((1.0,), (1.0,)))
    router = NembhardOracleRouterNK()

    def choose(experience):
        return router.choose(
            NembhardOracleDecisionViewNK(OrganizationResourcesNK.from_organization(org),
                                         problem, experience, profile),
            max_candidates=4,
            per_agent_effort_choices=_binary_choices(2, 1),
        )

    initially = choose(NembhardDirectStateNK(((0.0,), (0.0,))))
    experienced = choose(NembhardDirectStateNK(((0.0,), (1.0,))))
    assert initially.allocation == ((1.0,), (0.0,))
    assert experienced.allocation == ((0.0,), (1.0,))
    assert experienced.predicted_outputs == pytest.approx((0.5,))


def test_router_ties_keep_first_feasible_catalogue_entry():
    org = _organization(2, 1, budget=1.0)
    profile = _profile(2, 1)
    router = NembhardOracleRouterNK()
    decision = router.choose(
        NembhardOracleDecisionViewNK(
            OrganizationResourcesNK.from_organization(org),
            ProblemSpecNK("tie", (0.2,), 1.0),
            NembhardDirectStateNK.zeros(2, 1),
            profile,
        ),
        max_candidates=4,
        per_agent_effort_choices=_binary_choices(2, 1),
    )
    # Cartesian catalog order is (zero,zero), (zero,one), (one,zero), ...
    assert decision.catalog_action_id == 1
    assert decision.allocation == ((0.0,), (1.0,))


@pytest.mark.parametrize(("n", "k"), ((1, 1), (2, 2), (4, 3)))
def test_oracle_runner_handles_general_nk_and_is_deterministic(n, k):
    org = _organization(n, k, budget=1.0)
    problem = ProblemSpecNK("nk", (0.1,) * k, 1.0)
    config = NembhardDirectExecutionNK(_profile(n, k), (), _units())
    kwargs = dict(
        max_candidates=2**n,
        per_agent_effort_choices=_binary_choices(n, k),
        mechanism_id="nembhard_direct",
        router_id="nembhard_oracle",
        nembhard_execution=config,
    )
    first = run_nk_production_sequence(org, (problem, problem), **kwargs)
    replay = run_nk_production_sequence(org, (problem, problem), **kwargs)
    assert first == replay
    assert first.router_id == "nembhard_oracle"
    assert all(row.router_id == "nembhard_oracle" for row in first.records)
    assert all(row.outputs == row.router_predicted_outputs for row in first.records)
    assert first.records[0].experience_after == first.records[1].experience_before


def test_router_rejects_competence_leakage_by_using_only_nembhard_state():
    problem = ProblemSpecNK("same", (0.2,), 1.0)
    config = NembhardDirectExecutionNK(_profile(2, 1), (), _units())
    common = dict(max_candidates=4, per_agent_effort_choices=_binary_choices(2, 1),
                  mechanism_id="nembhard_direct", router_id="nembhard_oracle",
                  nembhard_execution=config)
    low = _organization(2, 1, competence=((0.0,), (0.0,)), budget=1.0)
    high = _organization(2, 1, competence=((1.0,), (1.0,)), budget=1.0)
    assert run_nk_production_sequence(low, (problem,), **common) == \
        run_nk_production_sequence(high, (problem,), **common)


def test_oracle_can_choose_differently_from_a_fixed_assignment():
    org = _organization(2, 1, budget=1.0)
    problem = ProblemSpecNK("fixed-vs-oracle", (0.3,), 1.0)
    profile = NembhardDirectProfileNK(((0.2,), (1.0,)), ((1.0,), (1.0,)), ((1.0,), (1.0,)))
    state = NembhardDirectStateNK(((0.0,), (0.0,)))
    explicit = NembhardDirectExecutionNK(profile, (((1.0,), (0.0,)),), _units(), state)
    oracle = NembhardDirectExecutionNK(profile, (), _units(), state)
    fixed_run = run_nk_production_sequence(
        org, (problem,), max_candidates=4, mechanism_id="nembhard_direct",
        nembhard_execution=explicit,
    )
    oracle_run = run_nk_production_sequence(
        org, (problem,), max_candidates=4, per_agent_effort_choices=_binary_choices(2, 1),
        mechanism_id="nembhard_direct", router_id="nembhard_oracle",
        nembhard_execution=oracle,
    )
    assert fixed_run.records[0].allocation != oracle_run.records[0].allocation
    assert oracle_run.records[0].outputs == oracle_run.records[0].router_predicted_outputs


def test_oracle_integrates_with_frozen_generated_demand():
    org = _organization(2, 2, budget=1.0)
    p = ProblemSpecNK("type", (0.1, 0.1), 1.0)
    environment = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"steady": 1.0}),
        {"steady": DemandRegimeNK("steady", (p,), (1.0,))},
        horizon=3,
        resource_budget=1.0,
    )
    config = NembhardDirectExecutionNK(_profile(2, 2), (), _units())
    kwargs = dict(max_candidates=4, per_agent_effort_choices=_binary_choices(2, 2),
                  environment=environment, environment_seed=19,
                  mechanism_id="nembhard_direct", router_id="nembhard_oracle",
                  nembhard_execution=config)
    run = run_nk_production_sequence(org, **kwargs)
    replay = run_nk_production_sequence(org, **kwargs)
    assert isinstance(run, NKEnvironmentRunResult)
    assert run == replay
    assert len(run.execution.records) == 3
    assert serialize_nk_nembhard_direct_result(run.execution) == \
        serialize_nk_nembhard_direct_result(replay.execution)


def test_nembhard_router_cannot_be_selected_for_mis_v2():
    with pytest.raises(ValueError, match="router_id"):
        run_nk_production_sequence(
            _organization(1, 1), (ProblemSpecNK("p", (0.1,), 1.0),),
            max_candidates=1, router_id="nembhard_oracle",
        )
