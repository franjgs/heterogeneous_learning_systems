from studies.soc_triage_hls_availability_robustness.run_policy_pilot import (
    DEFAULT_SEEDS, POLICIES, run_pilot,
)


def test_policy_pilot_pairs_exogenous_trace_and_preserves_single_investigation():
    assert len(DEFAULT_SEEDS) == 10
    assert len(set(DEFAULT_SEEDS)) == 10
    assert not set(DEFAULT_SEEDS) & set(range(711000000, 711000400))

    result = run_pilot(seeds=(DEFAULT_SEEDS[0],))
    assert len(result["runs"]) == 3
    by_policy = {row["policy"]: row for row in result["runs"]}
    assert set(by_policy) == set(POLICIES)
    assert len({row["exogenous_trace_sha256"] for row in result["runs"]}) == 1
    assert len({row["environment_realization_sha256"] for row in result["runs"]}) == 1
    reference = by_policy["D1"]
    for row in result["runs"]:
        assert row["alerts"] == reference["alerts"]
        assert row["confusion_counts"] == reference["confusion_counts"]
        assert row["route_counts"] == reference["route_counts"]
        assert {int(key): value for key, value in row["investigation_counts"].items()} == {1: row["alerts"]}
        assert row["status_counts"]["completed_within_sla"] + row["status_counts"]["completed_late"] + row["status_counts"]["pending"] == row["alerts"]
        assert row["route_counts"]["L2"] == row["confusion_counts"]["TP"] + row["confusion_counts"]["FP"]
        assert row["route_counts"]["L1"] == row["confusion_counts"]["TN"] + row["confusion_counts"]["FN"]
    assert by_policy["WAPS"]["hlsb_switch_count_by_level"]
    assert result["paired_differences"]["P1 - D1"]["R_over_N"]["n"] == 1
