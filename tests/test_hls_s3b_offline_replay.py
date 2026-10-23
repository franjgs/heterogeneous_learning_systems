from __future__ import annotations

from experiments.run_hls_s3b_offline_replay import decode_feedback, replay_events
from experiments.run_hls_s3b_e1 import MATCHINGS


def test_decode_feedback_never_invents_unobserved_outcomes():
    # Edges (0,0) and (2,2) observed; only (2,2) succeeded.
    assert decode_feedback((1 << 0) | (1 << 8), 1 << 8) == {
        (0, 0): 0.0,
        (2, 2): 1.0,
    }


def test_common_history_updates_both_estimators_and_replays_deterministically():
    truth = [
        ((0.8, 0.1, 0.1), (0.1, 0.8, 0.1), (0.4, 0.1, 0.1)),
        ((0.8, 0.1, 0.1), (0.1, 0.8, 0.1), (0.9, 0.1, 0.1)),
        ((0.8, 0.1, 0.1), (0.1, 0.8, 0.1), (0.4, 0.1, 0.1)),
    ]
    events = []
    for t, matching_id in enumerate((0, 1, 0)):
        pairs = MATCHINGS[matching_id]
        feedback = {pair: float((t + pair[0] + pair[1]) % 2) for pair in pairs}
        events.append((pairs, feedback))

    first = replay_events(truth, events, window=2, xi=2.0)
    second = replay_events(truth, events, window=2, xi=2.0)
    assert first == second
    assert set(first["decisions"]) == {
        "UCB1_mean", "UCB1_index", "SW-UCB_mean", "SW-UCB_index"
    }
    # Both estimators see the same three events for each executed pair.
    assert first["diagnostics"]["UCB1"]["pairs"]["0,0"][
        "mean_observations_used_per_decision"] == first["diagnostics"]["SW-UCB"][
        "pairs"]["0,0"]["mean_observations_used_per_decision"]
    assert all(len(row["regret"]) == 3 for row in first["decisions"].values())


def test_future_observation_cannot_change_prior_period_decision():
    truth = [((0.8, 0.1, 0.1), (0.1, 0.8, 0.1), (0.4, 0.1, 0.1))] * 2
    first_pairs = MATCHINGS[0]
    second_pairs = MATCHINGS[1]
    initial = (first_pairs, {pair: 0.0 for pair in first_pairs})
    future_a = (second_pairs, {pair: 0.0 for pair in second_pairs})
    future_b = (second_pairs, {pair: 1.0 for pair in second_pairs})
    result_a = replay_events(truth, [initial, future_a], window=2)
    result_b = replay_events(truth, [initial, future_b], window=2)
    for rule in result_a["decisions"]:
        assert result_a["decisions"][rule]["matching"][0] == result_b["decisions"][rule]["matching"][0]

