from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from experiments.run_hls_s4_pef_integration import run
from experiments.run_hls_s4_transfer_exact import make_case
from hls.experiment_contract import ExperimentRun
from hls.performance_evaluation import PerformanceEvaluator, Status
from hls.synthetic.hls_s4_transfer_exact import ExactResult, solve_bellman
from hls.synthetic.s4_pef_adapter import (
    POLICY_IDS,
    adapt_s4_policy,
    s4_evaluation_profiles,
)


HISTORICAL = Path("results/experiments/hls_s4_transfer_exact/results.json")
SOLVER_SOURCE = Path("src/hls/synthetic/hls_s4_transfer_exact.py")


@pytest.fixture(scope="module")
def integration():
    return run()


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_lists(value):
    if isinstance(value, tuple):
        return [_json_lists(item) for item in value]
    if isinstance(value, list):
        return [_json_lists(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_lists(item) for key, item in value.items()}
    return value


def test_T1_regression_rewards_and_reference_values(integration):
    assert integration["regression_checks"]["A_reward"] == pytest.approx(1.9175000000000004, abs=1e-12)
    assert integration["regression_checks"]["B_reward"] == pytest.approx(1.9175000000000004, abs=1e-12)
    assert integration["regression_checks"]["A_B_reward_difference"] == pytest.approx(0.0, abs=1e-12)


def test_T2_T3_actions_and_competence_states_match_historical_reference(integration):
    original = json.loads(HISTORICAL.read_text())
    for policy in POLICY_IDS:
        current = integration["policy_results"][policy]["periods"]
        stored = original[policy]["periods"]
        assert len(current) == len(stored) == 3
        for left, right in zip(current, stored):
            assert _json_lists(left["action"]["production"]) == right["action"]["production"]
            assert _json_lists(left["action"]["teaching"]) == right["action"]["teaching"]
            assert _json_lists(left["competence_before"]) == right["competence_before"]
            assert _json_lists(left["competence_after_mis"]) == right["competence_after_mis"]
            assert _json_lists(left["competence_after"]) == right["competence_after"]


def test_T4_T5_T6_physical_output_functional_service_and_deficit(integration):
    for policy in POLICY_IDS:
        rows = integration["policy_results"][policy]["periods"]
        expected = ((1.05, 0.0), (0.0, 0.35), (0.0, 0.5175))
        for row, output in zip(rows, expected):
            assert row["outputs"] == pytest.approx(output, abs=1e-12)
        metrics = integration["policy_results"][policy]["evaluations"]
        for profile in ("s4_collective_basic_v1", "s4_collective_resources_diagnostics_v1"):
            evaluated = metrics[profile]
            assert evaluated["functional_success_rate"]["value"] == pytest.approx(1 / 3)
            assert evaluated["functional_deficit_cumulative"]["value"] == pytest.approx(0.5325)


def test_T7_resources_reconcile(integration):
    for policy in POLICY_IDS:
        result = integration["policy_results"][policy]["evaluations"]["s4_collective_resources_diagnostics_v1"]
        assert result["resource_usage:productive_effort"]["value"] == pytest.approx(6.0)
        assert result["resource_usage:teaching_effort"]["value"] == pytest.approx(0.0)
        assert result["resource_usage:teaching_resource"]["value"] == pytest.approx(0.0)
        assert result["resource_usage:total_resource"]["value"] == pytest.approx(6.0)
        assert result["teaching_actions_cumulative"]["value"] == pytest.approx(0.0)


def test_T8_T9_experiment_run_v1_and_round_trip(integration):
    for policy in POLICY_IDS:
        run_record = ExperimentRun.from_dict(integration["experiment_runs"][policy])
        assert run_record.schema_version == "hls-experiment-run/1.0"
        assert run_record.configuration["scenario_id"] == "S4"
        assert run_record.policy_id == policy
        assert ExperimentRun.from_json(run_record.to_json()).to_json() == run_record.to_json()
        assert len(run_record.events) == 9


def test_T10_pef_is_independent_and_reproduces_run_metrics(integration):
    for policy in POLICY_IDS:
        run_record = ExperimentRun.from_dict(integration["experiment_runs"][policy])
        names = {item.name: item.value for item in run_record.metrics}
        assert names["original_reward_cumulative"] == pytest.approx(1.9175000000000004)
        assert names["ces_cumulative"] == pytest.approx(1.9175000000000004)
        assert names["production_cumulative"] == pytest.approx(1.9175000000000004)
        assert names["functional_success_rate"] == pytest.approx(1 / 3)
        assert names["functional_deficit_cumulative"] == pytest.approx(0.5325)


def test_T11_profiles_only_select_metrics_and_do_not_mutate_execution():
    case = make_case()
    solution = solve_bellman(case, transfer_available=False)
    source_before = (solution.actions, solution.periods, solution.value)
    run_record, records = adapt_s4_policy(
        case, solution, "A", transfer_available=False, source_pointer="in-memory-test",
    )
    before = (run_record.to_json(), tuple(asdict(row) for row in records), source_before)
    evaluator = PerformanceEvaluator()
    profiles = s4_evaluation_profiles()
    for profile in profiles:
        evaluator.register_profile(profile)
        evaluator.evaluate(profile.profile_id, "A", records)
    after = (run_record.to_json(), tuple(asdict(row) for row in records),
             (solution.actions, solution.periods, solution.value))
    assert after == before
    assert set(profiles[0].metrics).issubset(profiles[1].metrics)


def test_T12_A_B_comparison_is_compatible_and_zero(integration):
    for profile in integration["profiles"]:
        comparison = integration["comparisons_A_minus_B"][profile]
        assert comparison["original_reward_cumulative"]["value"] == pytest.approx(0.0, abs=1e-12)
        assert comparison["original_reward_cumulative"]["status"] == Status.VALID.value
        assert comparison["original_reward_cumulative"]["unit"] == "declared_reward"


def test_T13_information_regime_and_transfer_interpretation_are_explicit(integration):
    for policy in POLICY_IDS:
        run_record = ExperimentRun.from_dict(integration["experiment_runs"][policy])
        assert run_record.information_available["policy_view"] == "exact true competence state"
        assert "complete deterministic sequence known" in run_record.information_available["demand"]
        assert integration["policy_results"][policy]["transfer_selected"] is False


def test_T14_available_metrics_are_valid_and_keep_reward_production_distinct(integration):
    for policy in POLICY_IDS:
        for profile in integration["policy_results"][policy]["evaluations"].values():
            assert all(metric["status"] == Status.VALID.value for metric in profile.values())
        metrics = integration["policy_results"][policy]["evaluations"]["s4_collective_basic_v1"]
        assert metrics["original_reward_cumulative"]["metric_id"] != metrics["production_cumulative"]["metric_id"]
        assert metrics["original_reward_cumulative"]["unit"] == "declared_reward"
        assert metrics["production_cumulative"]["unit"] == "output"


def test_T15_s2a_s4_s7_reuse_common_types_without_metric_equivalence(integration):
    check = integration["cross_scenario_contract_check"]
    assert all(check["shared_types"].values())
    assert check["s2a"]["recomputed_original_reward"] == pytest.approx(8.0)
    assert check["s2a"]["physical_metrics_keep_s2a_availability"]["production_cumulative"] == "NOT_APPLICABLE"
    assert check["s7"]["recomputed_ces"] is not None
    assert check["historical_s2a_s7_rerun"] is False


def test_T16_integration_does_not_modify_solver_source(integration):
    assert integration["provenance"]["solver_source_sha256_before"] == integration["provenance"]["solver_source_sha256_after"]
    assert _digest(SOLVER_SOURCE) == integration["provenance"]["solver_source_sha256_after"]


def test_T17_runner_is_reproducible():
    first = run()
    second = run()
    assert first == second


def test_T18_adapter_rejects_invalid_policy_and_incomplete_result():
    case = make_case()
    result = solve_bellman(case, transfer_available=False)
    with pytest.raises(ValueError, match="unsupported"):
        adapt_s4_policy(case, result, "MA", transfer_available=False, source_pointer="test")
    with pytest.raises(ValueError, match="source pointer"):
        adapt_s4_policy(case, result, "A", transfer_available=False, source_pointer="")
    short_result = ExactResult(result.value, result.actions[:2], result.periods[:2], result.visited_states)
    with pytest.raises(ValueError, match="T=3"):
        adapt_s4_policy(case, short_result, "A", transfer_available=False, source_pointer="test")


def test_historical_s4_artifact_is_not_modified(integration):
    assert Path("results/experiments/hls_s4_transfer_exact/results.json").is_file()
    assert integration["provenance"]["historical_reference"] == HISTORICAL.as_posix()
    hashes = integration["provenance"]
    assert hashes["historical_artifact_sha256_before"] == hashes["historical_artifact_sha256_after"]
