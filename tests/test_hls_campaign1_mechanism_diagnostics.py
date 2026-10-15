from experiments.synthetic.hls_campaign1.analyze_mechanisms import (
    interaction_analysis,
    temporal_analysis,
)


def _summary(policy, li, ces):
    return {
        "demand": "stationary", "initial_deficit": "high",
        "teaching_effectiveness": "high", "horizon": "short",
        "seed": "1", "individual_learning": li, "policy": policy,
        "ces_reward_sum": str(ces),
    }


def test_learning_interaction_is_difference_of_paired_policy_deltas():
    rows = [
        _summary("P0_PRODUCTION_ONLY", "False", 10),
        _summary("P2_ADAPTIVE_TEACHING", "False", 12),
        _summary("P0_PRODUCTION_ONLY", "True", 8),
        _summary("P2_ADAPTIVE_TEACHING", "True", 13),
    ]
    raw, _ = interaction_analysis(rows)
    assert len(raw) == 1
    assert raw[0]["delta_off"] == 2
    assert raw[0]["delta_on"] == 5
    assert raw[0]["interaction_on_minus_off"] == 3


def test_temporal_analysis_detects_break_even_and_no_teaching():
    rows = []
    for period, p0, p2, taught in ((0, 1.0, 0.0, True), (1, 1.0, 1.0, False),
                                    (2, 1.0, 3.0, False)):
        for policy, ces, teaching in (("P0_PRODUCTION_ONLY", p0, "NA"),
                                      ("P2_ADAPTIVE_TEACHING", p2, "0:1:0" if taught else "NA")):
            rows.append({"demand": "stationary", "initial_deficit": "low",
                         "teaching_effectiveness": "high", "horizon": "short",
                         "seed": "1", "individual_learning": "False",
                         "policy": policy, "period": str(period),
                         "ces_reward": str(ces), "teaching_relation": teaching})
    temporal, by_seed, _summaries = temporal_analysis(rows)
    assert [r["cumulative_delta"] for r in temporal] == [-1.0, -1.0, 1.0]
    assert len(by_seed) == 1
    assert by_seed[0]["break_even_period"] == 2
    assert by_seed[0]["teaching_occurred"] is True


def test_temporal_analysis_marks_policy_ties_without_teaching():
    rows = []
    for period in range(2):
        for policy in ("P0_PRODUCTION_ONLY", "P2_ADAPTIVE_TEACHING"):
            rows.append({"demand": "stationary", "initial_deficit": "low",
                         "teaching_effectiveness": "low", "horizon": "short",
                         "seed": "2", "individual_learning": "False",
                         "policy": policy, "period": str(period), "ces_reward": "1",
                         "teaching_relation": "NA"})
    _, by_seed, _summaries = temporal_analysis(rows)
    assert by_seed[0]["final_cumulative_delta"] == 0
    assert by_seed[0]["teaching_occurred"] is False
    assert by_seed[0]["initial_disadvantage"] is False
