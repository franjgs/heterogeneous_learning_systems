from __future__ import annotations

import math

from experiments.run_hls_s3b_e1 import (
    BASE, BREAKPOINTS, CALIBRATION, HORIZON, MATCHINGS, N, PAIRS, TRANSIENT,
    W_LONG, W_REF, calibration_matching, evaluate_seed, exact_matching,
    matrix_at, mean_pair, oracle_matching,
)
from hls.nonstationary_assignment import PairwiseBanditEstimator


def test_predeclared_matrices_have_expected_b1_and_b2_optima_and_margins():
    assert HORIZON == 10_000
    assert (W_REF, W_LONG) == (1214, 2428)
    assert mean_pair(BASE) == (0, 0)
    assert mean_pair(TRANSIENT) == (2, 0)
    assert oracle_matching(BASE) == ((0, 0), (1, 1), (2, 2))
    assert oracle_matching(TRANSIENT) == ((0, 2), (1, 1), (2, 0))
    base_values = sorted(sum(BASE[i][k] for i, k in matching) for matching in MATCHINGS)
    transient_values = sorted(sum(TRANSIENT[i][k] for i, k in matching) for matching in MATCHINGS)
    assert math.isclose(base_values[-1] - base_values[-2], 0.45)
    assert math.isclose(transient_values[-1] - transient_values[-2], 0.05)
    assert exact_matching(BASE) == oracle_matching(BASE)
    assert exact_matching(TRANSIENT) == oracle_matching(TRANSIENT)
    assert matrix_at(BREAKPOINTS[0]) == TRANSIENT
    assert matrix_at(BREAKPOINTS[1]) == BASE


def test_calibration_is_common_and_partial_feedback_is_one_edge_per_period():
    assert len(PAIRS) == 9
    assert [calibration_matching(t) for t in range(CALIBRATION)] == [
        ((0, 0), (1, 1), (2, 2)),
        ((0, 2), (1, 0), (2, 1)),
        ((0, 1), (1, 2), (2, 0)),
    ] * 3
    revealed = []
    for t in range(CALIBRATION):
        matching = calibration_matching(t)
        revealed.append(sorted(matching)[t // 3])
    assert sorted(revealed) == sorted(PAIRS)


def test_pairwise_prefix_statistics_match_direct_history_scan():
    for method in ("ucb1", "sw_ucb"):
        model = PairwiseBanditEstimator(2, 2, method=method, window=3, xi=2.0)
        rows = {pair: [] for pair in ((0, 0), (0, 1), (1, 0), (1, 1))}
        for t, pair, reward in ((0, (0, 0), 1), (1, (1, 1), 0),
                                (3, (0, 0), 0), (4, (0, 1), 1),
                                (7, (0, 0), 1)):
            model.update(t, (pair,), {pair: reward})
            rows[pair].append((t, reward))
        t = 8
        diagnostics = model.diagnostic_matrix(t)
        for i in range(2):
            for k in range(2):
                pair = (i, k)
                history = rows[pair]
                valid = history if method == "ucb1" else [
                    item for item in history if t - 3 <= item[0] < t
                ]
                count = len(valid)
                assert diagnostics[i][k]["observations_used"] == count
                if count:
                    mean = sum(x[1] for x in valid) / count
                    assert math.isclose(diagnostics[i][k]["estimated_mean"], mean)
                    if method == "ucb1":
                        bonus = math.sqrt(2 * math.log(max(2, t + 1)) / count)
                    else:
                        bonus = math.sqrt(2 * math.log(max(2, min(t + 1, 3))) / count)
                    assert math.isclose(diagnostics[i][k]["index"], mean + bonus)


def test_one_paired_seed_reproducible_and_respects_feedback_contract():
    first = evaluate_seed(8200)
    second = evaluate_seed(8200)
    for result in (first, second):
        for policy in result["policies"].values():
            policy.pop("runtime_seconds")
    assert first == second
    assert set(first["policies"]) == {
        "B1/UCB1", "B1/SW-UCB-Wref", "B2-Semi/UCB1",
        "B2-Semi/SW-UCB-Wref", "B2-Semi/SW-UCB-Wlong",
        "B2-Partial/UCB1", "B2-Partial/SW-UCB-Wref",
    }
    for key, trace in first["traces"].items():
        assert all(len(trace[field]) == HORIZON for field in (
            "expected_reward", "realized_reward", "expected_regret", "action_id",
            "feedback_mask", "feedback_success_mask", "executed_success_mask"))
        assert all(value >= 0 for value in trace["expected_regret"])
        modality = first["policies"][key]["modality"]
        for period, (action, mask) in enumerate(zip(trace["action_id"], trace["feedback_mask"])):
            if modality == "B1":
                selected_mask = 1 << action
                assert mask == selected_mask
            elif modality == "B2-Semi":
                assert len(MATCHINGS[action]) == 3
                expected_mask = sum(1 << (i * 3 + k) for i, k in MATCHINGS[action])
                assert mask == expected_mask
            else:
                assert mask.bit_count() == 1
                observed_edge = next(edge for edge in range(9) if mask & (1 << edge))
                assert observed_edge in {i * 3 + k for i, k in MATCHINGS[action]}
        for t in range(HORIZON):
            success = trace["feedback_success_mask"][t]
            observed = trace["feedback_mask"][t]
            assert success & ~observed == 0
            assert trace["realized_reward"][t] == trace["executed_success_mask"][t].bit_count()
            action = trace["action_id"][t]
            matrix = matrix_at(t)
            if modality == "B1":
                chosen = ((action // 3, action % 3),)
                oracle = (mean_pair(matrix),)
                actual = matrix[chosen[0][0]][chosen[0][1]]
                optimum = matrix[oracle[0][0]][oracle[0][1]]
            else:
                chosen = MATCHINGS[action]
                oracle = oracle_matching(matrix)
                actual = sum(matrix[i][k] for i, k in chosen)
                optimum = sum(matrix[i][k] for i, k in oracle)
            assert math.isclose(trace["expected_reward"][t], actual, abs_tol=1e-6)
            assert math.isclose(trace["expected_regret"][t], optimum - actual, abs_tol=1e-6)

