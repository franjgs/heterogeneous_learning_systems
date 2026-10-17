"""End-to-end tests for the estimate-based Nembhard Direct router."""

from dataclasses import fields
from random import Random

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
from hls.hls_lab_nk_nembhard_adaptive import (
    NembhardAdaptiveDecisionViewNK,
    NembhardAdaptiveRouterConfigNK,
    NembhardAdaptiveRouterNK,
    initialize_productivity_estimator_nk,
    observe_nembhard_work_outputs_nk,
    update_productivity_estimator_nk,
)
from hls.hls_lab_nk_nembhard_router import NembhardOracleDecisionViewNK, NembhardOracleRouterNK
from hls.synthetic.c5 import StationaryTaskDemand


def _units():
    return NembhardOutputUnitContract("effort/period", "period", "work", "output", "output")


def _organization(n, k, *, competence=None, budget=None):
    return OrganizationConfigNK(
        tuple(f"a{i}" for i in range(n)), tuple(f"s{j}" for j in range(k)),
        competence or tuple((0.0,) * k for _ in range(n)), (1.0,) * n,
        float(n if budget is None else budget),
    )


def _profile(kmat):
    n, k = len(kmat), len(kmat[0])
    return NembhardDirectProfileNK(
        tuple(tuple(row) for row in kmat),
        tuple((1.0,) * k for _ in range(n)),
        tuple((1.0,) * k for _ in range(n)),
    )


def _choices(n, k):
    zero = (0.0,) * k
    one = (1.0,) + (0.0,) * (k - 1)
    return tuple((zero, one) for _ in range(n))


def _run(org, problems, profile, config, *, choices=None, **extra):
    return run_nk_production_sequence(
        org, problems, max_candidates=2 ** len(org.agent_ids),
        per_agent_effort_choices=choices or _choices(len(org.agent_ids), len(org.skill_ids)),
        mechanism_id="nembhard_direct", router_id="nembhard_adaptive",
        nembhard_execution=NembhardDirectExecutionNK(profile, (), _units()),
        adaptive_router_config=config, **extra,
    )


def test_productivity_estimator_updates_mean_variance_and_independent_cells():
    initial = initialize_productivity_estimator_nk(2, 2, ((0.0, 2.0), (3.0, 4.0)))
    updated = update_productivity_estimator_nk(
        initial,
        ((1.0, 0.0), (2.0, 1e-12)),
        ((2.0, None), (-4.0, 100.0)),
        minimum_observation_work=1e-9,
    )
    assert updated.means == ((2.0, 2.0), (0.0, 4.0))
    assert updated.counts == ((1, 0), (1, 0))
    assert updated.sample_variances == ((None, None), (None, None))
    assert initial.counts == ((0, 0), (0, 0))


def test_estimator_running_statistics_and_negative_noise_clip():
    state = initialize_productivity_estimator_nk(1, 1)
    state = update_productivity_estimator_nk(state, ((1.0,),), ((2.0,),), minimum_observation_work=1e-9)
    state = update_productivity_estimator_nk(state, ((1.0,),), ((4.0,),), minimum_observation_work=1e-9)
    assert state.means == ((3.0,),)
    assert state.sample_variances == ((2.0,),)
    clipped = update_productivity_estimator_nk(state, ((1.0,),), ((-8.0,),), minimum_observation_work=1e-9)
    assert clipped.means == ((2.0,),)
    assert clipped.counts == ((3,),)


def test_observation_is_deterministic_and_zero_work_is_unobserved():
    args = dict(work=((1.0, 0.0),), true_work_outputs=((0.7, 0.0),), noise_stddev=0.2)
    first = observe_nembhard_work_outputs_nk(**args, rng=Random(9))
    replay = observe_nembhard_work_outputs_nk(**args, rng=Random(9))
    assert first == replay
    assert first[0][1] is None


def test_decision_view_contains_no_true_productivity_or_hls_competence():
    view_fields = {field.name for field in fields(NembhardAdaptiveDecisionViewNK)}
    assert not ({"profile", "true_productivity", "competence", "actual_competence"} & view_fields)

    org = _organization(2, 1, competence=((0.0,), (1.0,)), budget=1.0)
    problem = ProblemSpecNK("hidden", (0.1,), 1.0)
    config = NembhardAdaptiveRouterConfigNK(initial_productivity_estimate=((0.9,), (0.1,)))
    high_for_first = _run(org, (problem,), _profile(((0.1,), (0.9,))), config)
    high_for_second = _run(org, (problem,), _profile(((0.9,), (0.1,))), config)
    assert high_for_first.records[0].allocation == high_for_second.records[0].allocation
    assert high_for_first.records[0].allocation == ((1.0,), (0.0,))
    assert high_for_first.records[0].outputs != high_for_second.records[0].outputs


def test_initial_latent_experience_is_not_exposed_and_prediction_uses_estimate():
    org = _organization(2, 1, budget=1.0)
    problem = ProblemSpecNK("initial", (0.1,), 1.0)
    profile = _profile(((1.0,), (0.8,)))
    initial = NembhardDirectStateNK(((3.0,), (2.0,)))
    # P(3)=4/5, P(2)=3/4 for the configured p=r=1 curve.
    config = NembhardAdaptiveRouterConfigNK(initial_productivity_estimate=((0.8,), (0.75,)))
    execution = NembhardDirectExecutionNK(profile, (), _units(), initial)
    run = run_nk_production_sequence(
        org, (problem,), max_candidates=4, per_agent_effort_choices=_choices(2, 1),
        mechanism_id="nembhard_direct", router_id="nembhard_adaptive",
        nembhard_execution=execution, adaptive_router_config=config,
    )
    record = run.records[0]
    assert record.router_observable_experience == ((0.0,), (0.0,))
    assert record.router_predicted_outputs == pytest.approx(record.outputs)
    assert record.experience_before == ((3.0,), (2.0,))
    assert record.router_id == "nembhard_adaptive"


def test_adaptive_router_changes_decision_after_observation():
    org = _organization(2, 1, budget=1.0)
    problems = (ProblemSpecNK("p0", (0.1,), 1.0), ProblemSpecNK("p1", (0.1,), 1.0))
    profile = _profile(((0.1,), (0.9,)))
    config = NembhardAdaptiveRouterConfigNK(initial_productivity_estimate=((0.8,), (0.1,)))
    result = _run(org, problems, profile, config)
    assert result.records[0].allocation == ((1.0,), (0.0,))
    assert result.records[1].allocation == ((0.0,), (1.0,))
    assert result.records[0].adaptive_observations[0][0] == pytest.approx(0.05)
    assert result.records[1].adaptive_estimator_before.means[0][0] == pytest.approx(0.05)


def test_adaptive_decision_can_differ_from_oracle_under_imperfect_information():
    org = _organization(2, 1, budget=1.0)
    problem = ProblemSpecNK("imperfect", (0.1,), 1.0)
    profile = _profile(((0.1,), (0.9,)))
    estimates = ((0.9,), (0.1,))
    adaptive = _run(org, (problem,), profile, NembhardAdaptiveRouterConfigNK(
        initial_productivity_estimate=estimates,
    ))
    oracle = NembhardOracleRouterNK().choose(
        NembhardOracleDecisionViewNK(
            OrganizationResourcesNK.from_organization(org), problem,
            NembhardDirectStateNK.zeros(2, 1), profile,
        ), max_candidates=4, per_agent_effort_choices=_choices(2, 1),
    )
    assert adaptive.records[0].allocation == ((1.0,), (0.0,))
    assert oracle.allocation == ((0.0,), (1.0,))


@pytest.mark.parametrize(("n", "k"), ((1, 1), (2, 2), (3, 2), (4, 3)))
def test_adaptive_router_general_nk_is_reproducible_and_feasible(n, k):
    org = _organization(n, k, budget=1.0)
    problem = ProblemSpecNK("nk", (0.1,) * k, 1.0)
    config = NembhardAdaptiveRouterConfigNK(
        epsilon=0.35, exploration_seed=21, observation_noise_stddev=0.05,
        observation_seed=33, initial_productivity_estimate=0.2,
    )
    first = _run(org, (problem,) * 3, _profile(tuple((0.8,) * k for _ in range(n))), config)
    replay = _run(org, (problem,) * 3, _profile(tuple((0.8,) * k for _ in range(n))), config)
    assert first == replay
    for record in first.records:
        assert sum(record.individual_effort_used) <= record.effective_collective_budget + 1e-12
        assert record.router_predicted_outputs is not None
        assert record.adaptive_estimator_before is not None
        assert record.adaptive_estimator_after is not None
        assert record.experience_after == tuple(
            tuple(record.experience_before[i][j] + record.experience_increment[i][j]
                  for j in range(k)) for i in range(n)
        )


def test_epsilon_zero_never_explores_and_nonzero_seed_replays():
    org = _organization(2, 1, budget=1.0)
    problem = ProblemSpecNK("p", (0.2,), 1.0)
    profile = _profile(((0.3,), (0.8,)))
    greedy = _run(org, (problem,) * 5, profile, NembhardAdaptiveRouterConfigNK())
    assert not any(record.router_exploratory for record in greedy.records)
    explore_config = NembhardAdaptiveRouterConfigNK(epsilon=1.0, exploration_seed=8)
    a = _run(org, (problem,) * 5, profile, explore_config)
    b = _run(org, (problem,) * 5, profile, explore_config)
    assert a == b
    assert all(record.router_exploratory for record in a.records)


def test_adaptive_integrates_generated_demand_and_serializes_replay():
    org = _organization(2, 2, budget=1.0)
    p = ProblemSpecNK("type", (0.1, 0.1), 1.0)
    environment = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"steady": 1.0}),
        {"steady": DemandRegimeNK("steady", (p,), (1.0,))},
        horizon=3, resource_budget=1.0,
    )
    profile = _profile(((0.7, 0.6), (0.4, 0.9)))
    config = NembhardAdaptiveRouterConfigNK(epsilon=0.2, exploration_seed=17)
    kwargs = dict(environment=environment, environment_seed=25)
    first = _run(org, None, profile, config, **kwargs)
    replay = _run(org, None, profile, config, **kwargs)
    assert isinstance(first, NKEnvironmentRunResult)
    assert first == replay
    assert serialize_nk_nembhard_direct_result(first.execution) == \
        serialize_nk_nembhard_direct_result(replay.execution)


def test_invalid_adaptive_router_configurations_fail_closed():
    with pytest.raises(ValueError):
        NembhardAdaptiveRouterConfigNK(epsilon=1.1)
    with pytest.raises(ValueError):
        NembhardAdaptiveRouterConfigNK(initial_productivity_estimate=-1.0)
    with pytest.raises(ValueError, match="requires adaptive_router_config"):
        run_nk_production_sequence(
            _organization(1, 1), (ProblemSpecNK("p", (0.1,), 1.0),),
            max_candidates=2, mechanism_id="nembhard_direct", router_id="nembhard_adaptive",
            nembhard_execution=NembhardDirectExecutionNK(_profile(((1.0,),)), (), _units()),
        )
