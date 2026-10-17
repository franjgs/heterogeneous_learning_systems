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
    ProductivityEstimateCellNK,
    _normalize_welford_dispersion,
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


def test_first_welford_observation_does_not_treat_prior_mean_as_a_sample():
    # This valid noisy-work observation reproduced the interruption: using
    # the generic count=1 formula from prior mean 0.6 rounds mean_new one ULP
    # above x and yields m2=-2.3696655208094487e-16.
    work = 0.5
    observed_output = 0.8336012378255072
    observed_productivity = observed_output / work
    delta = observed_productivity - 0.6
    rounded_mean = 0.6 + delta / 1
    rounded_m2 = delta * (observed_productivity - rounded_mean)
    assert rounded_m2 == pytest.approx(-2.3696655208094487e-16, abs=1e-30)

    initial = initialize_productivity_estimator_nk(1, 1, 0.6)
    updated = update_productivity_estimator_nk(
        initial, ((work,),), ((observed_output,),), minimum_observation_work=1e-9,
    )
    assert updated.means == ((observed_productivity,),)
    assert updated.counts == ((1,),)
    assert updated.cells[0][0].m2 == 0.0


def test_welford_roundoff_tolerance_is_scale_aware_and_rejects_material_negative():
    observed = 1.6672024756510144
    delta = observed - 0.6
    mean_new = 1.6672024756510146
    delta_after = observed - mean_new
    residue = delta * delta_after
    assert residue < 0.0
    assert _normalize_welford_dispersion(
        residue, mean_old=0.6, observed=observed, mean_new=mean_new,
        delta=delta, delta_after=delta_after, m2_old=0.0, increment=residue,
    ) == 0.0
    with pytest.raises(ValueError, match="materially negative"):
        _normalize_welford_dispersion(
            -1e-6, mean_old=0.6, observed=observed, mean_new=mean_new,
            delta=delta, delta_after=delta_after, m2_old=0.0, increment=-1e-6,
        )


def test_estimator_rejects_nonfinite_and_materially_invalid_states():
    with pytest.raises(ValueError):
        ProductivityEstimateCellNK(0.5, 1, -1e-8)
    with pytest.raises(ValueError):
        ProductivityEstimateCellNK(0.5, 1, float("nan"))
    with pytest.raises(ValueError):
        ProductivityEstimateCellNK(0.5, 1, float("inf"))
    state = initialize_productivity_estimator_nk(1, 1)
    for bad in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(ValueError):
            state.cells[0][0].update(bad)


def test_constant_close_and_long_observation_sequences_keep_valid_dispersion():
    cell = ProductivityEstimateCellNK(1.0)
    for value in (1.0,) * 100 + (1.0 + 1e-12, 1.0 - 1e-12):
        cell = cell.update(value)
        assert cell.m2 >= 0.0
    assert cell.observation_count == 102
    assert cell.sample_variance == pytest.approx(2e-26, rel=0.1, abs=1e-28)
    for index in range(10_000):
        cell = cell.update(0.9 + (index % 7) * 1e-12)
    assert cell.observation_count == 10_102
    assert cell.m2 >= 0.0 and cell.sample_variance is not None


def test_adaptive_episode_accepts_roundoff_sensitive_first_productivity_observation():
    observed_productivity = 1.6672024756510144
    org = _organization(1, 1, budget=0.5)
    problem = ProblemSpecNK("roundoff", (0.1,), 0.5)
    choices = (((0.0,), (0.5,)),)
    result = _run(
        org, (problem,), _profile(((2.0 * observed_productivity,),)),
        NembhardAdaptiveRouterConfigNK(initial_productivity_estimate=0.6),
        choices=choices,
    )
    record = result.records[0]
    assert record.allocation == ((0.5,),)
    assert record.adaptive_observations[0][0] == pytest.approx(
        0.5 * observed_productivity)
    assert record.adaptive_estimator_after.cells[0][0].m2 == 0.0


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
