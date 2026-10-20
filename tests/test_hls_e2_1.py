import math

import pytest

from experiments.hls_e2.hls_e2_1 import (
    DEFAULT_TOLERANCE,
    Model,
    build_scenarios,
    demand_sequences,
    evaluate_myopic,
    evaluate_sequence,
    exhaustive_optimum,
    optimize_best_static,
    optimize_dynamic,
    parameter_profiles,
    run_study,
)


def test_dynamic_programming_matches_independent_exhaustive_search():
    for profile in parameter_profiles().values():
        for demands in (("taskA", "taskB", "taskA", "taskB", "taskA", "taskB"),
                        ("taskA",) * 6):
            dp = optimize_dynamic(profile, demands)
            brute = exhaustive_optimum(profile, demands)
            assert dp["reward"] == pytest.approx(brute["reward"], abs=DEFAULT_TOLERANCE)


def test_exhaustive_validator_rejects_long_horizon():
    with pytest.raises(ValueError, match="T <= 6"):
        exhaustive_optimum(next(iter(parameter_profiles().values())), ("taskA",) * 7)


def test_best_static_enumerates_and_optimizes_all_task_mappings():
    model = parameter_profiles()["asymmetric_learning"]
    result = optimize_best_static(model, ("taskA", "taskB") * 6)
    assert result["mappings_evaluated"] == 4
    assert result["reward"] == max(row["reward"] for row in result["all_mapping_rewards"])
    assert len(result["mapping"]) == 2


def test_demand_orders_share_multiset_but_not_sequence():
    sequences = demand_sequences()
    assert sorted(sequences["alternating"]) == sorted(sequences["clustered"])
    assert sequences["alternating"] != sequences["clustered"]
    assert sequences["changing_frequency"].count("taskA") == 8
    assert sequences["changing_frequency"].count("taskB") == 4


def test_period_reward_uses_pre_transition_experience_and_experience_is_endogenous():
    model = parameter_profiles()["asymmetric_learning"]
    result = evaluate_sequence(model, ("taskA", "taskA"), (0, 0))
    row0, row1 = result["trajectory"]
    assert row0["reward"] == row0["productivity_before"][0][0]
    assert row0["experience_after"][0][0] == row0["experience_before"][0][0] + 1
    assert row1["experience_before"] == row0["experience_after"]
    assert row1["productivity_before"][0][0] > row0["productivity_before"][0][0]
    assert result["final_experience"][0][0] == 2


def test_myopic_uses_true_current_productivity_and_deterministic_ties():
    model = parameter_profiles()["homogeneous"]
    result = evaluate_myopic(model, ("taskA", "taskB"))
    assert result["allocations"] == [0, 0]


def test_parameter_domain_and_dimensions_are_checked():
    with pytest.raises(ValueError, match="2×2"):
        Model(k=((1.0,), (1.0,)), p=((1.0, 1.0),) * 2,
              r=((1.0, 1.0),) * 2, d0=((0, 0),) * 2)
    with pytest.raises(ValueError):
        Model(k=((1.0, 1.0),) * 2, p=((1.0, 1.0),) * 2,
              r=((1.0, 1.0),) * 2, d0=((0, -1),) * 2)


def test_study_has_no_dynamic_advantage_in_declared_independent_skill_model():
    result = run_study()
    assert result["scenario_count"] == 33
    assert result["positive_case_count"] == 0
    assert result["validation_results"]["dp_matches_independent_exhaustive_search"]
    assert result["validation_results"]["reward_matches_reported_trajectory"]
    assert result["validation_results"]["all_dynamic_paths_stationary_by_task_type"]
    for scenario in result["scenarios"]:
        assert math.isclose(scenario["dynamic_vs_static_gap"], 0.0, abs_tol=DEFAULT_TOLERANCE)
        assert scenario["policies"]["OPT-DYNAMIC"]["states_explored"] > 0
