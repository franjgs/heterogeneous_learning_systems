"""Tests for the isolated direct-experience productivity curve."""

import math

import pytest

from hls.mechanisms.nembhard_direct import (
    DirectExperienceParameters,
    advance_direct_experience,
    direct_productivity,
    direct_productivity_many,
    evaluate_direct_exposure,
)


def test_direct_productivity_matches_manual_values_and_initial_experience():
    parameters = DirectExperienceParameters(
        asymptotic_productivity=10.0,
        prior_experience=2.0,
        experience_scale=8.0,
    )
    assert direct_productivity(0.0, parameters) == pytest.approx(2.0)
    assert direct_productivity(6.0, parameters) == pytest.approx(5.0)
    assert direct_productivity(10.0, parameters) == pytest.approx(6.0)


def test_zero_prior_and_zero_exposure_have_zero_initial_productivity():
    parameters = DirectExperienceParameters(3.5, 0.0, 2.0)
    assert direct_productivity(0.0, parameters) == 0.0
    assert direct_productivity(4.0, parameters) == pytest.approx(3.5 * 4.0 / 6.0)


def test_productivity_is_increasing_concave_and_bounded_below_asymptote():
    parameters = DirectExperienceParameters(7.0, 1.5, 5.0)
    values = [direct_productivity(float(d), parameters) for d in range(21)]
    increments = [right - left for left, right in zip(values, values[1:])]
    assert all(right > left for left, right in zip(values, values[1:]))
    assert all(right < left for left, right in zip(increments, increments[1:]))
    assert all(0.0 <= value < parameters.asymptotic_productivity for value in values)
    assert direct_productivity(1e12, parameters) == pytest.approx(7.0, rel=1e-10)


@pytest.mark.parametrize("prior,scale,expected_exposure", [(0.0, 4.0, 4.0), (2.0, 8.0, 6.0), (4.0, 4.0, 0.0)])
def test_scale_is_total_effective_exposure_at_half_asymptote(
    prior, scale, expected_exposure
):
    parameters = DirectExperienceParameters(12.0, prior, scale)
    # The threshold D = r - p belongs to the non-negative exposure domain.
    assert expected_exposure == scale - prior
    assert direct_productivity(expected_exposure, parameters) == pytest.approx(6.0)


def test_r_below_prior_means_half_threshold_is_outside_nonnegative_domain():
    parameters = DirectExperienceParameters(12.0, 5.0, 3.0)
    assert direct_productivity(0.0, parameters) > 6.0
    assert direct_productivity(0.0, parameters) == pytest.approx(7.5)


def test_experience_update_and_before_after_helper_are_explicit_and_pure():
    parameters = DirectExperienceParameters(10.0, 2.0, 8.0)
    assert advance_direct_experience(6.0, 2.0) == 8.0
    assert advance_direct_experience(6.0, 0.0) == 6.0
    result = evaluate_direct_exposure(6.0, 2.0, parameters)
    assert result.experience_before == 6.0
    assert result.experience_after == 8.0
    assert result.productivity_before == pytest.approx(5.0)
    assert result.productivity_after == pytest.approx(10.0 * 10.0 / 18.0)
    assert result.productivity_after > result.productivity_before


def test_zero_exposure_preserves_productivity_and_vector_evaluation_is_deterministic():
    parameters = DirectExperienceParameters(8.0, 1.0, 3.0)
    assert evaluate_direct_exposure(2.0, 0.0, parameters).productivity_before == (
        evaluate_direct_exposure(2.0, 0.0, parameters).productivity_after
    )
    exposures = (0.0, 1.0, 4.0)
    result = direct_productivity_many(exposures, parameters)
    assert result == tuple(direct_productivity(d, parameters) for d in exposures)
    assert result == direct_productivity_many(exposures, parameters)


@pytest.mark.parametrize(
    "k,p,r",
    [(-1.0, 0.0, 1.0), (1.0, -1.0, 1.0), (1.0, 0.0, 0.0), (1.0, 0.0, -1.0),
     (math.nan, 0.0, 1.0), (1.0, math.inf, 1.0)],
)
def test_invalid_parameters_are_rejected(k, p, r):
    with pytest.raises(ValueError):
        DirectExperienceParameters(k, p, r)


@pytest.mark.parametrize("experience", [-1.0, math.nan, math.inf, -math.inf])
def test_invalid_exposure_is_rejected(experience):
    parameters = DirectExperienceParameters(1.0, 0.0, 1.0)
    with pytest.raises(ValueError):
        direct_productivity(experience, parameters)


@pytest.mark.parametrize("current,increment", [(0.0, -1.0), (-1.0, 0.0), (math.inf, 0.0), (1e308, 1e308)])
def test_invalid_experience_updates_are_rejected(current, increment):
    with pytest.raises(ValueError):
        advance_direct_experience(current, increment)


def test_evaluations_have_no_shared_mutable_state_and_large_finite_input_is_stable():
    parameters = DirectExperienceParameters(2.0, 1e308, 1e308)
    first = direct_productivity(1e308, parameters)
    second = direct_productivity(0.0, parameters)
    assert first == pytest.approx(2.0 * 2.0 / 3.0)
    assert second == pytest.approx(1.0)
    assert direct_productivity(1e308, parameters) == first
