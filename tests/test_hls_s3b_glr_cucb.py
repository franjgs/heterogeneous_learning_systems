import math

import pytest

from hls.glr_cucb import GLRCUCB, bernoulli_kl, glr_statistic, glr_threshold


def test_bernoulli_kl_and_glr_match_closed_form():
    assert bernoulli_kl(0.5, 0.5) == 0.0
    assert glr_statistic([0.0, 0.0, 1.0, 1.0]) == pytest.approx(4 * math.log(2))


def test_threshold_is_valid_and_increases_with_confidence_requirement():
    assert glr_threshold(20, 0.01) > glr_threshold(20, 0.1)
    assert glr_threshold(40, 0.01) > glr_threshold(20, 0.01)


def test_detector_does_not_alarm_on_constant_sequence():
    model = GLRCUCB(1, 1, horizon=300, epsilon=.2, delta=20/300, seed=4)
    for t in range(100):
        model.update(t, ((0, 0),), {(0, 0): 1.0 if t % 2 == 0 else 0.0})
    assert model.detections == []


def test_detector_alarms_on_large_known_bernoulli_change_and_global_resets():
    model = GLRCUCB(1, 2, horizon=300, epsilon=.2, delta=20/300, seed=4,
                    initial_history={(0, 1): [(0, 1.0), (1, 1.0), (2, 1.0)]})
    for t in range(40):
        model.update(t, ((0, 0),), {(0, 0): 0.0})
    before = model.tau
    for t in range(40, 90):
        model.update(t, ((0, 0),), {(0, 0): 1.0})
        if model.detections:
            break
    assert model.detections
    assert model.tau > before
    assert model._samples[(0, 0)] == []
    assert model._samples[(0, 1)] == []


def test_partial_feedback_and_matching_exploration_are_reproducible():
    matchings = [((0, 0), (1, 1), (2, 2)), ((0, 1), (1, 2), (2, 0))]
    a = GLRCUCB(3, 3, horizon=300, epsilon=.2, delta=.05, seed=10)
    b = GLRCUCB(3, 3, horizon=300, epsilon=.2, delta=.05, seed=10)
    assert a.forced_arm(1) == b.forced_arm(1)
    edge = a.forced_arm(1)
    selected_a = a.forced_matching(edge, matchings)
    selected_b = b.forced_matching(edge, matchings)
    assert selected_a == selected_b and edge in selected_a
    a.update(1, selected_a, {pair: 1.0 for pair in selected_a})
    b.update(1, selected_b, {pair: 1.0 for pair in selected_b})
    with pytest.raises(ValueError):
        a.update(2, ((0, 0),), {})
    assert a.score_matrix(2) == b.score_matrix(2)


def test_only_bernoulli_feedback_is_accepted():
    model = GLRCUCB(1, 1, horizon=10, epsilon=.2, delta=.1, seed=0)
    with pytest.raises(ValueError):
        model.update(0, ((0, 0),), {(0, 0): .3})


def test_matching_scores_use_only_observed_history_and_ucb_formula():
    model = GLRCUCB(1, 1, horizon=20, epsilon=.2, delta=.1, seed=0,
                    initial_history={(0, 0): [(0, 0.0), (1, 1.0)]})
    # Warm-start clock is at t=1, so elapsed=1 and the published bonus is zero.
    assert model.score_matrix(2)[0][0] == pytest.approx(.5)
