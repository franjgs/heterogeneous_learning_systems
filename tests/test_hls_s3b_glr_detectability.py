from experiments.run_hls_s3b_glr_cucb import evaluate


def test_diagnostic_trace_is_passive_and_reproduces_policy_decisions():
    condition, seed = "S3b-1_abrupt", 9300
    plain = evaluate(condition, seed)
    traced = evaluate(condition, seed, diagnostic_trace=True)
    assert "glr_detectability" not in plain
    assert traced["glr_detectability"]["detector_alarm_count"] == 0
    assert len(traced["glr_detectability"]["pairs"]) == 9
    for policy in plain["policies"]:
        assert plain["policies"][policy]["assignment_ids"] == traced["policies"][policy]["assignment_ids"]
        assert (plain["policies"][policy]["cumulative_expected_reward"]
                == traced["policies"][policy]["cumulative_expected_reward"])


def test_diagnostic_pair_trace_reports_change_relevance_and_observation_counts():
    result = evaluate("S3b-1_abrupt", 9301, diagnostic_trace=True)
    pairs = result["glr_detectability"]["pairs"]
    assert all(pair["changes"][0]["boundary_period"] == 150 for pair in pairs)
    assert all(pair["changes"][0]["absolute_mean_change"] == 0.0
               or abs(pair["changes"][0]["absolute_mean_change"] - 0.6) < 1e-12
               for pair in pairs)
    assert sum(pair["changes"][0]["absolute_mean_change"] > 0.59 for pair in pairs) == 6
    assert all(pair["changes"][0]["globally_optimal_matching_changed"] for pair in pairs)
    assert all(pair["changes"][0]["post_change_observations_before_next_change"] >= 0
               for pair in pairs)
