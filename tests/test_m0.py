import math
from argparse import Namespace

import pytest

from experiments.m0.sweep_regimes import regime, resolved_delta_min
from hls.m0 import (
    M0Config,
    RegionM0,
    discount_factor_sum,
    expected_intervention_value,
    frequency_gap_score,
    intervention_regret,
    rank_interventions_by_frequency_gap,
    rank_interventions_by_value,
    region_margin,
    routing_margin,
    strict_rank_reversal,
    successful_operational_gain,
    validate_canonical_m0_regions,
)


def config() -> M0Config:
    return M0Config(k_cheap=0.0, k_expensive=1.0, lambda_cost=0.15, H=1, gamma=1.0)


def region(delta: float, **overrides: float) -> RegionM0:
    values = dict(
        p=0.5,
        q_cheap=0.0,
        q_expensive=delta,
        learnability=1.0,
        gain=0.18,
        training_cost=0.0,
    )
    values.update(overrides)
    return RegionM0(**values)


def test_margin_matches_quality_gap_minus_cost_advantage() -> None:
    model = config()
    target = region(0.30)
    assert region_margin(target, model) == pytest.approx(0.30 - 0.15)
    assert routing_margin(0.30, model.cost_advantage) == pytest.approx(0.15)


def test_discount_sum_at_gamma_one_is_horizon() -> None:
    assert discount_factor_sum(7, 1.0) == 7.0


def test_discount_sum_at_gamma_below_one_is_geometric_sum() -> None:
    assert discount_factor_sum(4, 0.5) == pytest.approx((1 - 0.5**4) / (1 - 0.5))


def test_no_switching_has_zero_successful_operational_gain() -> None:
    assert successful_operational_gain(p=0.5, g=0.15, margin=0.15) == 0.0
    assert successful_operational_gain(p=0.5, g=0.10, margin=0.15) == 0.0


def test_switching_gain_is_probability_times_excess_over_margin() -> None:
    assert successful_operational_gain(p=0.5, g=0.18, margin=0.05) == pytest.approx(0.065)


def test_documented_rank_reversal_example() -> None:
    regions = [region(0.30), region(0.20)]
    model = config()
    assert frequency_gap_score(0.5, 0.30) > frequency_gap_score(0.5, 0.20)
    assert rank_interventions_by_frequency_gap(regions) == 0
    assert rank_interventions_by_value(regions, model) == 1
    assert intervention_regret(regions, model) == pytest.approx(0.05)


def test_perfect_gap_closure_cancels_quality_gap_from_value() -> None:
    model = M0Config(k_cheap=0.0, k_expensive=1.0, lambda_cost=0.15, H=3, gamma=0.5)
    target = region(0.30, gain=0.30, learnability=0.8, training_cost=0.04)
    expected = -0.04 + discount_factor_sum(3, 0.5) * 0.5 * 0.8 * 0.15
    assert expected_intervention_value(
        target.p,
        target.learnability,
        target.gain,
        region_margin(target, model),
        target.training_cost,
        model.H,
        model.gamma,
    ) == pytest.approx(expected)


def test_zero_learnability_leaves_immediate_training_cost() -> None:
    assert expected_intervention_value(0.5, 0.0, 0.18, 0.05, 0.07, 4, 0.9) == pytest.approx(-0.07)


def test_zero_horizon_benefit_is_not_permitted_in_m0() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        discount_factor_sum(0, 1.0)


def test_frequency_gap_can_be_value_optimal() -> None:
    regions = [region(0.20, gain=0.05), region(0.30, gain=0.30)]
    model = config()
    assert rank_interventions_by_frequency_gap(regions) == 1
    assert rank_interventions_by_value(regions, model) == 1


def test_regret_is_nonnegative_and_zero_for_shared_optimum() -> None:
    regions = [region(0.20, gain=0.05), region(0.30, gain=0.30)]
    regret = intervention_regret(regions, config())
    assert regret >= 0.0
    assert math.isclose(regret, 0.0)


def test_invalid_region_probability_total_is_rejected() -> None:
    regions = [region(0.20, p=0.4), region(0.30, p=0.4)]
    with pytest.raises(ValueError, match="sum"):
        rank_interventions_by_value(regions, config())


def test_canonical_m0_rejects_a_region_where_the_cheap_model_already_routes() -> None:
    regions = [region(0.15), region(0.20)]
    with pytest.raises(ValueError, match="m_z > 0"):
        validate_canonical_m0_regions(regions, config())


def test_canonical_sweep_rejects_delta_min_at_or_below_cost_advantage() -> None:
    args = Namespace(cost_advantage=0.15, delta_min=0.15)
    with pytest.raises(ValueError, match="delta_min > cost_advantage"):
        resolved_delta_min(args)


def test_switchable_and_non_switchable_classification() -> None:
    assert regime(0.20, cost_advantage=0.15, gain=0.18) == "switchable"
    assert regime(0.33, cost_advantage=0.15, gain=0.18) == "non_switchable"


def test_strict_rank_reversal_requires_no_ties() -> None:
    model = config()
    assert strict_rank_reversal([region(0.30), region(0.20)], model)
    assert not strict_rank_reversal([region(0.20), region(0.20)], model)
