from __future__ import annotations

import math

import pytest

from experiments.run_hls_s3b_nonstationary_unknown_assignment import (
    CONDITIONS,
    HORIZON,
    N,
    K,
    evaluate,
    matches_from_id,
    permutation_id,
    solve,
    window_for,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator


def test_estimators_accept_feedback_only_for_selected_edges():
    model = PairwiseBanditEstimator(2, 2, method="ucb1", window=4)
    selected = ((0, 0), (1, 1))
    model.update(0, selected, {(0, 0): 1.0, (1, 1): 0.0})
    assert len(model.observations[(0, 0)]) == 1
    assert model.observations[(0, 1)] == ()
    with pytest.raises(ValueError, match="exactly the selected"):
        model.update(1, ((0, 1),), {(0, 1): 0.5, (1, 0): 0.5})
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        model.update(1, ((0, 1),), {(0, 1): 1.1})


def test_ucb1_keeps_old_observations_but_sw_window_expires_them():
    ucb = PairwiseBanditEstimator(2, 2, method="ucb1", window=2)
    sw = PairwiseBanditEstimator(2, 2, method="sw_ucb", window=2)
    ucb.update(0, ((0, 0),), {(0, 0): 1.0})
    sw.update(0, ((0, 0),), {(0, 0): 1.0})
    ucb.update(1, ((1, 1),), {(1, 1): 0.0})
    sw.update(1, ((1, 1),), {(1, 1): 0.0})
    # At global period 3, observation at period 0 is outside [1, 3).
    assert ucb.score_matrix(3)[0][0] != 2.0 + math.sqrt(2 * math.log(4))
    assert sw.score_matrix(3)[0][0] == 2.0 + math.sqrt(2 * math.log(4))


def test_recent_mean_has_no_exploration_bonus_and_neutral_empty_window_prior():
    recent = PairwiseBanditEstimator(2, 2, method="recent_mean", window=2)
    recent.update(0, ((0, 0),), {(0, 0): 1.0})
    recent.update(1, ((1, 1),), {(1, 1): 0.0})
    scores = recent.score_matrix(2)
    assert scores[0][0] == 1.0
    assert scores[0][1] == 0.5


def test_all_conditions_change_optimal_matching_as_declared_and_windows_bounded():
    for condition, spec in CONDITIONS.items():
        assignments = []
        for shift in spec["shifts"]:
            matrix = tuple(tuple(0.8 if k == (i + shift) % K else 0.2
                                 for k in range(K)) for i in range(N))
            assignments.append(permutation_id(solve(matrix)))
        if spec["breakpoints"]:
            assert len(set(assignments)) > 1
        assert 1 <= window_for(condition) <= HORIZON
    assert window_for("S3b-0_stationary") == HORIZON
    assert window_for("S3b-1_abrupt") == 83
    assert window_for("S3b-2_recurrent") == 41


def test_paired_episode_is_reproducible_and_regret_nonnegative():
    first = evaluate("S3b-1_abrupt", 9300)
    second = evaluate("S3b-1_abrupt", 9300)
    assert first == second
    for policy, result in first["policies"].items():
        assert result["cumulative_expected_regret"] >= -1e-10
        assert len(result["assignment_ids"]) == HORIZON - 9
        for index in result["assignment_ids"]:
            matches = matches_from_id(index)
            assert len({i for i, _ in matches}) == len(matches)
            assert len({k for _, k in matches}) == len(matches)
            assert all(0 <= i < N and 0 <= k < K for i, k in matches)


def test_stationary_sw_ucb_reduces_to_ucb1_with_full_window():
    result = evaluate("S3b-0_stationary", 9300)
    assert (result["policies"]["UCB1_MATCHING"]["assignment_ids"]
            == result["policies"]["SW_UCB_MATCHING"]["assignment_ids"])


def test_global_mean_uses_all_selected_feedback_without_bonus():
    global_mean = PairwiseBanditEstimator(2, 2, method="global_mean", window=2)
    global_mean.update(0, ((0, 0),), {(0, 0): 1.0})
    global_mean.update(1, ((1, 1),), {(1, 1): 0.0})
    global_mean.update(5, ((0, 1),), {(0, 1): 1.0})
    scores = global_mean.score_matrix(6)
    diagnostics = global_mean.diagnostic_matrix(6)
    assert scores[0][0] == 1.0  # old observation retained beyond window=2
    assert diagnostics[0][0]["observations_used"] == 1
    assert diagnostics[0][0]["exploration_bonus"] == 0.0
    assert diagnostics[1][0]["observations_used"] == 0
    assert diagnostics[1][0]["exploration_bonus"] == 0.0
    assert global_mean.observations[(0, 1)][0].reward == 1.0
    assert global_mean.observations[(1, 0)] == ()


def test_factorial_contrasts_follow_seed_paired_definitions():
    from experiments.run_hls_s3b_factorial_ablation import factorial_contrasts

    result = factorial_contrasts({
        "GLOBAL_MEAN_MATCHING": [10.0, 12.0],
        "UCB1_MATCHING": [12.0, 13.0],
        "RECENT_MEAN_MATCHING": [8.0, 11.0],
        "SW_UCB_MATCHING": [9.0, 15.0],
    })
    assert result["bonus_global"]["paired_seed_differences"] == [2.0, 1.0]
    assert result["bonus_window"]["paired_seed_differences"] == [1.0, 4.0]
    assert result["window_without_bonus"]["paired_seed_differences"] == [-2.0, -1.0]
    assert result["window_with_bonus"]["paired_seed_differences"] == [-3.0, 2.0]
    assert result["interaction"]["paired_seed_differences"] == [-1.0, 3.0]


def test_factorial_reuses_original_calibration_and_reproduces_existing_policy():
    import json
    from pathlib import Path

    from experiments.run_hls_s3b_factorial_ablation import evaluate_one

    condition, seed = "S3b-1_abrupt", 9300
    actual = evaluate_one(condition, seed)
    original = json.loads(Path(
        "results/experiments/hls_s3b_nonstationary_unknown_assignment/results.json"
    ).read_text(encoding="utf-8"))
    reference = next(row for row in original["conditions"][condition]["episodes"]
                     if row["seed"] == seed)
    assert actual["calibration_assignment_ids"] == reference["calibration_assignment_ids"]
    for policy in ("UCB1_MATCHING", "SW_UCB_MATCHING", "RECENT_MEAN_MATCHING"):
        assert actual["policies"][policy]["assignment_ids"] == reference["policies"][policy]["assignment_ids"]
        assert actual["policies"][policy]["cumulative_expected_reward"] == pytest.approx(
            reference["policies"][policy]["cumulative_expected_reward"], abs=1e-12)

