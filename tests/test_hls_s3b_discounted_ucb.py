from __future__ import annotations

import math

import pytest

from hls.nonstationary_assignment import GarivierMoulinesPairwiseEstimator


def test_discounted_statistics_decay_every_global_period_and_only_selected_edges_update():
    model = GarivierMoulinesPairwiseEstimator(
        2, 1, method="d_ucb", gamma=0.5, xi=0.5)
    model.update(0, ((0, 0),), {(0, 0): 1.0})
    model.update(1, ((1, 0),), {(1, 0): 0.0})
    assert model.discounted_statistics[(0, 0)] == pytest.approx((0.5, 0.5))
    assert model.discounted_statistics[(1, 0)] == pytest.approx((0.0, 1.0))
    assert len(model.observations[(0, 0)]) == 1
    assert model.observations[(1, 0)][0].reward == 0.0


def test_discounted_index_matches_published_expression():
    model = GarivierMoulinesPairwiseEstimator(
        2, 1, method="d_ucb", gamma=0.5, xi=0.5, reward_bound=1.0)
    model.update(0, ((0, 0),), {(0, 0): 1.0})
    model.update(1, ((1, 0),), {(1, 0): 0.0})
    matrix = model.score_matrix(2)
    n_gamma = sum(count for _, count in model.discounted_statistics.values())
    s, count = model.discounted_statistics[(0, 0)]
    expected = s / count + 2 * math.sqrt(0.5 * math.log(n_gamma) / count)
    assert matrix[0][0] == pytest.approx(expected)


def test_unobserved_discounted_arm_is_optimistic_and_updates_require_observed_feedback():
    model = GarivierMoulinesPairwiseEstimator(2, 1, method="d_ucb", gamma=0.9)
    model.update(0, ((0, 0),), {(0, 0): 0.0})
    assert math.isinf(model.score_matrix(1)[1][0])
    with pytest.raises(ValueError, match="exactly the unique selected"):
        model.update(1, ((1, 0),), {(0, 0): 1.0})


def test_paper_ucb_and_sliding_window_confidence_expressions():
    ucb = GarivierMoulinesPairwiseEstimator(1, 1, method="ucb1", xi=0.5)
    ucb.update(0, ((0, 0),), {(0, 0): 1.0})
    assert ucb.score_matrix(1)[0][0] == pytest.approx(1 + math.sqrt(0.5 * math.log(2)))

    sw = GarivierMoulinesPairwiseEstimator(1, 1, method="sw_ucb", window=2, xi=0.5)
    sw.update(0, ((0, 0),), {(0, 0): 1.0})
    sw.update(1, (), {})
    assert sw.score_matrix(2)[0][0] == pytest.approx(1 + math.sqrt(0.5 * math.log(2)))
    sw.update(2, (), {})
    assert math.isinf(sw.score_matrix(3)[0][0])


def test_reproduction_protocol_parameters_and_hls_matching_change():
    from experiments.run_hls_s3b_discounted_ucb import (
        HLS_BASE, HLS_TRANSIENT, PAPER_GAMMA, PAPER_WINDOW,
        exact_matching, permutation_id,
    )

    assert PAPER_GAMMA == pytest.approx(0.9975)
    assert PAPER_WINDOW == 1214
    assert permutation_id(exact_matching(HLS_BASE)) != permutation_id(exact_matching(HLS_TRANSIENT))
