from __future__ import annotations

import math

import pytest

from experiments.run_hls_s3b_e1 import evaluate_seed
from experiments.run_hls_s3b_observation_subsidy import (
    evaluate_treatment,
    _select_subsidy_edge,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator


def test_extra_observation_keeps_same_timestamp_and_counts_as_sample():
    model = PairwiseBanditEstimator(2, 2, method="sw_ucb", window=1, xi=2.0)
    model.update(0, ((0, 0),), {(0, 0): 0.0})
    model.update_additional_observation(0, (0, 0), 1.0)

    current = model.diagnostic_matrix(1)
    assert len(model.observations[(0, 0)]) == 2
    assert [item.period for item in model.observations[(0, 0)]] == [0, 0]
    assert current[0][0]["observations_used"] == 2
    assert math.isclose(current[0][0]["estimated_mean"], 0.5)

    expired = model.diagnostic_matrix(2)
    assert expired[0][0]["observations_used"] == 0

    with pytest.raises(ValueError):
        model.update_additional_observation(0, (0, 1), 1.0)


def test_subsidy_selection_rules_are_uniform_on_their_declared_sets():
    optimal = ((0, 2), (1, 1), (2, 0))
    assert [_select_subsidy_edge("uniform", rank, optimal) for rank in range(9)] == [
        (i, k) for i in range(3) for k in range(3)
    ]
    assert [_select_subsidy_edge("directed", rank, optimal) for rank in range(9)] == [
        (0, 2), (1, 1), (2, 0), (0, 2), (1, 1), (2, 0),
        (0, 2), (1, 1), (2, 0),
    ]


def test_no_subsidy_reproduces_s3b_e1_sw_ucb_for_one_seed():
    episode, trace = evaluate_treatment(8200, "none")
    reference = evaluate_seed(8200)["traces"]["B2-Semi/SW-UCB-Wref"]
    assert trace["action_id"] == reference["action_id"]
    assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in
               zip(trace["expected_reward"], reference["expected_reward"]))
    assert trace["realized_reward"] == reference["realized_reward"]
    assert all(math.isclose(a, b, abs_tol=1e-6) for a, b in
               zip(trace["expected_regret"], reference["expected_regret"]))
    assert episode["subsidy_observations_total"] == 0


def test_subsidy_is_not_used_for_the_current_period_decision():
    uniform, uniform_trace = evaluate_treatment(8200, "uniform")
    directed, directed_trace = evaluate_treatment(8200, "directed")
    assert uniform["treatment"] == "uniform"
    assert directed["treatment"] == "directed"
    # Both treatments begin with the same fixed calibration action; treatment
    # information is delivered only after each current action is committed.
    assert uniform_trace["action_id"][0] == directed_trace["action_id"][0]
    assert uniform_trace["expected_reward"][0] == directed_trace["expected_reward"][0]
    assert uniform_trace["realized_reward"][0] == directed_trace["realized_reward"][0]
    assert uniform["regimes"]["base_pre"]["periods"] == 2_991
    assert uniform["subsidy_observations_total"] == 10_000
    assert directed["subsidy_observations_total"] == 10_000
