"""Mathematical and regression controls for MIS-v2."""

from math import isclose

from hls.discover_develop_v0 import DISCOVER_DEVELOP, DISCOVER_ONLY, STATIC_KNOWN, mis_transition, run_sequence
from hls.discover_develop_v2 import (
    capability_after_binary_exposure,
    capability_after_exposure,
    eta_to_lambda,
    mis_v2_transition,
    run_sequence_v2,
)
from hls.discover_v0 import THETA_1, THETA_2


ETA_GRID = (0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 0.90)
STATE = ((0.0, 0.25), (0.5, 0.75), (1.0, 0.5))


def test_r1_r4_boundedness_no_exposure_positive_development_and_mastery():
    for eta in ETA_GRID:
        rate = eta_to_lambda(eta)
        for capability in (0.0, 0.1, 0.5, 0.9, 1.0):
            assert capability_after_exposure(capability, 0.0, rate=rate) == capability
            developed = capability_after_exposure(capability, 1.0, rate=rate)
            assert 0.0 <= developed <= 1.0
            assert developed > capability if capability < 1.0 else developed == 1.0


def test_r5_gain_is_strictly_diminishing_in_prior_capability():
    for eta in ETA_GRID:
        rate = eta_to_lambda(eta)
        gains = [capability_after_exposure(s, 0.5, rate=rate) - s for s in (0.0, 0.25, 0.5, 0.75, 0.99)]
        assert all(left > right for left, right in zip(gains, gains[1:]))


def test_r6_finite_exposure_never_creates_instant_mastery_or_a_clamp():
    for eta in ETA_GRID:
        value = capability_after_exposure(0.0, 1.0, rate=eta_to_lambda(eta))
        assert isclose(value, eta, abs_tol=1e-15) and value < 1.0
    old = mis_transition(((0.0, 0.0),) * 3, ((1.0, 0.0), (0.0, 0.0), (0.0, 0.0)), enabled=True)
    new = mis_v2_transition(((0.0, 0.0),) * 3, ((1.0, 0.0), (0.0, 0.0), (0.0, 0.0)), enabled=True, eta=0.5)
    assert old[0][0] == 1.0 and new[0][0] == 0.5


def test_r7_exposure_composition_consistency():
    for eta in ETA_GRID:
        rate = eta_to_lambda(eta)
        for capability in (0.0, 0.2, 0.7, 0.99):
            split = capability_after_exposure(capability_after_exposure(capability, 0.3, rate=rate), 0.7, rate=rate)
            whole = capability_after_exposure(capability, 1.0, rate=rate)
            assert isclose(split, whole, rel_tol=0.0, abs_tol=2e-15)


def test_binary_eta_and_exponential_lambda_forms_are_equivalent():
    for eta in ETA_GRID:
        for capability in (0.0, 0.25, 0.5, 0.9, 1.0):
            exponential = capability_after_exposure(capability, 1.0, rate=eta_to_lambda(eta))
            assert isclose(exponential, capability_after_binary_exposure(capability, eta=eta), abs_tol=1e-15)


def test_repeated_exposure_approaches_mastery_asymptotically():
    rate = eta_to_lambda(0.2)
    values = [capability_after_exposure(0.0, exposure, rate=rate) for exposure in (1.0, 2.0, 5.0, 10.0, 20.0)]
    assert all(left < right < 1.0 for left, right in zip(values, values[1:]))
    assert values[-1] > 0.98


def test_only_exercised_cells_change_and_no_clipping_is_used():
    action = ((0.0, 0.0), (0.5, 0.5), (0.0, 1.0))
    after = mis_v2_transition(STATE, action, enabled=True, eta=0.35)
    assert after[0] == STATE[0]
    assert after[2][0] == STATE[2][0]
    assert STATE[1][0] < after[1][0] < 1.0 and STATE[1][1] < after[1][1] < 1.0
    assert STATE[2][1] < after[2][1] < 1.0


def test_develop_off_exactly_reproduces_frozen_prototype():
    sequence = (THETA_1, THETA_2)
    for mode in (DISCOVER_ONLY, STATIC_KNOWN):
        old = run_sequence(STATE, sequence, mode=mode, seed=17)
        new = run_sequence_v2(STATE, sequence, mode=mode, eta=0.35, seed=17)
        assert old == new


def test_discover_policy_has_no_true_theta_leakage_under_v2():
    left = run_sequence_v2(STATE, (THETA_1,), mode=DISCOVER_DEVELOP, eta=0.35, seed=19)
    right = run_sequence_v2(STATE, (THETA_2,), mode=DISCOVER_DEVELOP, eta=0.35, seed=19)
    assert left[0].belief_before == right[0].belief_before == 0.5
    assert left[0].action == right[0].action
