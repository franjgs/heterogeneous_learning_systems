from __future__ import annotations

from dataclasses import replace

import pytest

from experiments.run_hls_s2a_pef_integration import run as run_integrated_s2a
from experiments.run_hls_s2a_static_demand import run_s2a
from hls.experiment_contract import ExperimentRun
from hls.performance_evaluation import (
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator, Status,
)
from hls.synthetic.s2a_pef_adapter import (
    CONFIGURATION_ID,
    ORGANIZATIONAL_PROBLEM_ID,
    PROFILE_ID,
    adapt_s2a_policy,
    s2a_evaluation_profile,
)
from hls.synthetic.s7_pef_adapter import adapt_s7_pilot_artifact_to_experiment_run


S7_PILOT_RESULT = "results/experiments/hls_pef_s7_pilot/results.json"


def test_integration_reproduces_original_runner_values_and_exhaustive_reference():
    result = run_integrated_s2a()
    original = result["source_runner_result"]
    assert original["horizon_reward"]["exact_per_period"] == pytest.approx(8.0)
    assert original["horizon_reward"]["greedy_per_period"] == pytest.approx(7.2)
    assert original["horizon_reward"]["global_exhaustive_optimum"] == pytest.approx(8.0)
    assert original["horizon_reward"]["global_sequences_enumerated"] == 84_388
    assert result["optimality_validation"]["role"] == "optimality_validation_reference_not_policy"
    assert result["optimality_validation"]["exact_matches_reference"] is True
    assert result["policies_compared"] == ["exact", "greedy"]


def test_original_runner_result_is_not_mutated_and_timing_is_not_exported():
    source = run_s2a()
    before = repr(source)
    run_id_before = source["horizon_reward"]["exact_per_period"]
    adapt_s2a_policy(source, "exact")
    assert repr(source) == before
    integrated = run_integrated_s2a()
    assert "timings_descriptive_seconds" not in integrated["source_runner_result"]
    assert source["horizon_reward"]["exact_per_period"] == run_id_before


def test_profile_and_pef_results_preserve_reward_and_non_applicability():
    result = run_integrated_s2a()
    profile = result["profile"]
    assert profile["profile_id"] == PROFILE_ID
    assert profile["primary_metrics"] == ("original_reward_cumulative",)
    assert result["pef_results"]["exact"]["original_reward_cumulative"]["value"] == pytest.approx(8.0)
    assert result["pef_results"]["greedy"]["original_reward_cumulative"]["value"] == pytest.approx(7.2)
    for policy_id in ("exact", "greedy"):
        for metric_id in ("ces_cumulative", "functional_success_rate",
                          "functional_deficit_cumulative", "production_cumulative"):
            metric = result["pef_results"][policy_id][metric_id]
            assert metric["status"] == Status.NOT_APPLICABLE.value
            assert metric["value"] is None


def test_exact_minus_greedy_comparison_is_compatible_and_has_declared_units():
    result = run_integrated_s2a()
    difference = result["comparisons"]["exact_minus_greedy_original_reward"]
    assert difference["value"] == pytest.approx(0.8)
    assert difference["unit"] == "declared_reward"
    assert difference["status"] == Status.VALID.value
    assert result["comparisons"]["same_configuration"] is True


def test_experiment_run_records_identity_provenance_and_structured_diagnostics():
    result = run_integrated_s2a()
    exact = ExperimentRun.from_dict(result["experiment_runs"]["exact"])
    greedy = ExperimentRun.from_dict(result["experiment_runs"]["greedy"])
    assert exact.run_id != greedy.run_id
    assert exact.configuration["scenario_id"] == "S2a"
    assert exact.configuration["organizational_problem_id"] == ORGANIZATIONAL_PROBLEM_ID
    assert exact.metadata["evaluation_profile_id"] == PROFILE_ID
    assert exact.random_seeds == ()
    assert exact.software_revision is None
    assert [event.event_type for event in exact.events] == [
        "decision", "execution", "decision", "execution",
        "decision", "execution", "decision", "execution",
    ]
    assert exact.events[-1].data["assignment_count"] == 0
    assert exact.to_json() == ExperimentRun.from_json(exact.to_json()).to_json()


def test_global_enumeration_is_not_a_policy_or_policy_run():
    result = run_integrated_s2a()
    assert set(result["experiment_runs"]) == {"exact", "greedy"}
    assert "global_enumeration" not in result["pef_results"]
    assert result["optimality_validation"]["sequences_enumerated"] == 84_388


def test_s2a_and_stored_s7_use_common_run_and_pef_structures():
    import json
    from pathlib import Path

    result = run_integrated_s2a()
    s7_artifact = json.loads(Path(S7_PILOT_RESULT).read_text())
    s7_run = adapt_s7_pilot_artifact_to_experiment_run(s7_artifact, "A")
    s2a_run = ExperimentRun.from_dict(result["experiment_runs"]["exact"])

    profile_data = s7_artifact["profile"]
    s7_profile = EvaluationProfile(
        **{
            **profile_data,
            "primary_metrics": tuple(profile_data["primary_metrics"]),
            "secondary_metrics": tuple(profile_data["secondary_metrics"]),
            "diagnostic_metrics": tuple(profile_data["diagnostic_metrics"]),
            "diagnostic_fields": tuple(profile_data["diagnostic_fields"]),
        }
    )
    assert type(s2a_run) is type(s7_run) is ExperimentRun
    assert s2a_run.schema_version == s7_run.schema_version
    assert s7_profile.profile_id == profile_data["profile_id"]
    assert s7_profile.temporal_horizon == 4
    assert len(s7_run.events) == s7_artifact["branch_count"] * 4
    assert result["cross_scenario_contract_check"]["s7_experiment_rerun"] is False
    assert s7_run.metadata["conversion_scope"].endswith("no S7 rerun")

    s2a_records = adapt_s2a_policy(run_s2a(), "exact")[1]
    s7_episodes = []
    for branch in s7_artifact["branch_records"]["A"]:
        s7_episodes.append(tuple(
            EvaluationRecord(
                **{
                    **raw,
                    "output": None if raw["output"] is None else tuple(raw["output"]),
                    "requirements": None if raw["requirements"] is None else tuple(raw["requirements"]),
                    "deficit": None if raw["deficit"] is None else tuple(raw["deficit"]),
                    "field_status": {key: Status(value) for key, value in raw["field_status"].items()},
                }
            )
            for raw in branch["period_records"]
        ))
    assert all(type(record) is EvaluationRecord for record in s2a_records)
    assert all(type(record) is EvaluationRecord for episode in s7_episodes for record in episode)
    shared_evaluator = PerformanceEvaluator()
    shared_evaluator.register_profile(s7_profile)
    s7_recomputed = shared_evaluator.evaluate_weighted_episodes(
        s7_profile.profile_id, "A", s7_episodes,
    )
    assert s7_recomputed["ces_cumulative"].value == pytest.approx(
        s7_artifact["policies"]["A"]["ces_cumulative"]["value"], abs=1e-12,
    )


def test_incomplete_source_result_is_rejected_by_adapter():
    with pytest.raises(ValueError, match="incomplete S2a runner result"):
        adapt_s2a_policy({"experiment": "HLS-S2a-static-competence-variable-demand"}, "exact")


def test_adapter_rejects_reward_or_demand_mismatch_instead_of_guessing():
    source = run_s2a()
    corrupted = dict(source)
    periods = list(source["periods"])
    periods[0] = dict(periods[0], exact_reward=periods[0]["exact_reward"] + 1.0)
    corrupted["periods"] = periods
    with pytest.raises(ValueError, match="reward does not match assignments"):
        adapt_s2a_policy(corrupted, "exact")


def test_pure_adapter_and_evaluator_leave_source_decisions_untouched():
    import copy

    source = run_s2a()
    frozen = copy.deepcopy(source)
    _, records = adapt_s2a_policy(source, "exact")
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(s2a_evaluation_profile())
    evaluated = evaluator.evaluate(PROFILE_ID, "exact", records)
    assert evaluated["original_reward_cumulative"].value == pytest.approx(8.0)
    assert source == frozen


def test_pef_comparison_rejects_different_configuration():
    source = run_s2a()
    profile = s2a_evaluation_profile()
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    _, records = adapt_s2a_policy(source, "exact")
    left = evaluator.evaluate(PROFILE_ID, "exact", records)["original_reward_cumulative"]
    right = replace(
        left,
        configuration_id="other-S2a-config",
    )
    with pytest.raises(ValueError, match="incompatible"):
        PerformanceEvaluator.compare(left, right)


def test_deterministic_integration_output_repeats_exactly():
    first, second = run_integrated_s2a(), run_integrated_s2a()
    assert first == second
    assert first["configuration_id"] == CONFIGURATION_ID


def test_experiment_run_deserializer_rejects_incomplete_or_unknown_schema():
    run = ExperimentRun.from_dict(run_integrated_s2a()["experiment_runs"]["exact"])
    import json

    payload = json.loads(run.to_json())
    incomplete = dict(payload)
    incomplete.pop("run_id")
    with pytest.raises(ValueError, match="fields mismatch"):
        ExperimentRun.from_dict(incomplete)
    unsupported = dict(payload, schema_version="hls-experiment-run/2.0")
    with pytest.raises(ValueError, match="unsupported ExperimentRun schema"):
        ExperimentRun.from_dict(unsupported)
