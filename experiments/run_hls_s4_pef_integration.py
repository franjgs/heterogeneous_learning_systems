#!/usr/bin/env python3
"""Run the frozen exact S4 reference and evaluate it with shared HLS-PEF."""

from __future__ import annotations

import json
from hashlib import sha256
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from experiments.run_hls_s4_transfer_exact import make_case
from experiments.run_hls_s2a_static_demand import run_s2a
from hls.experiment_contract import ExperimentRun
from hls.performance_evaluation import (
    EvaluationProfile,
    EvaluationRecord,
    PerformanceEvaluator,
    Status,
)
from hls.synthetic.hls_s4_transfer_exact import solve_bellman
from hls.synthetic.s2a_pef_adapter import adapt_s2a_policy
from hls.synthetic.s4_pef_adapter import (
    POLICY_IDS,
    adapt_s4_policy,
    s4_evaluation_profiles,
)
from hls.synthetic.s7_pef_adapter import adapt_s7_pilot_artifact_to_experiment_run


RESULT = Path("results/experiments/hls_s4_pef_integration/results.json")
S2A_REFERENCE = Path("results/experiments/hls_s2a_pef_integration/results.json")
S7_REFERENCE = Path("results/experiments/hls_pef_s7_pilot/results.json")
S4_HISTORICAL_REFERENCE = Path("results/experiments/hls_s4_transfer_exact/results.json")
S4_SOLVER_SOURCE = Path("src/hls/synthetic/hls_s4_transfer_exact.py")


def _profile_from_dict(data: Mapping[str, Any]) -> EvaluationProfile:
    row = dict(data)
    for name in ("primary_metrics", "secondary_metrics", "diagnostic_metrics", "diagnostic_fields"):
        row[name] = tuple(row.get(name, ()))
    row["metric_availability"] = {
        key: Status(value) for key, value in row.get("metric_availability", {}).items()
    }
    return EvaluationProfile(**row)


def _s7_record(raw: Mapping[str, Any]) -> EvaluationRecord:
    row = dict(raw)
    for name in ("output", "requirements", "deficit"):
        if row.get(name) is not None:
            row[name] = tuple(row[name])
    row["field_status"] = {
        key: Status(value) for key, value in row.get("field_status", {}).items()
    }
    return EvaluationRecord(**row)


def _cross_scenario_reuse_check() -> dict[str, Any]:
    """Rehydrate S2a/S7 stored routes and evaluate with their own semantics."""
    if not S2A_REFERENCE.is_file() or not S7_REFERENCE.is_file():
        raise FileNotFoundError("stored S2a and S7 integration references are required")
    s2a_artifact = json.loads(S2A_REFERENCE.read_text(encoding="utf-8"))
    s7_artifact = json.loads(S7_REFERENCE.read_text(encoding="utf-8"))

    s2a_run = ExperimentRun.from_dict(s2a_artifact["experiment_runs"]["exact"])
    s2a_profile = _profile_from_dict(s2a_artifact["profile"])
    # The stored integration artifact omits source-only fields not needed for
    # its saved evaluations. Reuse the original deterministic source function
    # to produce a complete in-memory result; no artifact is written or changed.
    s2a_source = run_s2a()
    _, s2a_records = adapt_s2a_policy(s2a_source, "exact")
    s2a_evaluator = PerformanceEvaluator()
    s2a_evaluator.register_profile(s2a_profile)
    s2a_metrics = s2a_evaluator.evaluate(s2a_profile.profile_id, "exact", s2a_records)
    if s2a_metrics["original_reward_cumulative"].value != 8.0:
        raise AssertionError("S2a stored run no longer evaluates under its own profile")

    s7_run = adapt_s7_pilot_artifact_to_experiment_run(
        s7_artifact, "A", source_pointer=S7_REFERENCE.as_posix(),
    )
    s7_profile = _profile_from_dict(s7_artifact["profile"])
    s7_episodes = tuple(
        tuple(_s7_record(row) for row in branch["period_records"])
        for branch in s7_artifact["branch_records"]["A"]
    )
    s7_evaluator = PerformanceEvaluator()
    s7_evaluator.register_profile(s7_profile)
    s7_metrics = s7_evaluator.evaluate_weighted_episodes(
        s7_profile.profile_id, "A", s7_episodes,
    )
    expected_s7 = s7_artifact["policies"]["A"]["ces_cumulative"]["value"]
    if abs(s7_metrics["ces_cumulative"].value - expected_s7) > 1e-12:
        raise AssertionError("S7 stored records no longer evaluate under their own profile")

    return {
        "shared_types": {
            "ExperimentRun": type(s2a_run) is type(s7_run) is ExperimentRun,
            "EvaluationProfile": type(s2a_profile) is type(s7_profile) is EvaluationProfile,
            "EvaluationRecord": all(type(row) is EvaluationRecord for row in s2a_records)
                and all(type(row) is EvaluationRecord for episode in s7_episodes for row in episode),
            "PerformanceEvaluator": type(s2a_evaluator) is type(s7_evaluator) is PerformanceEvaluator,
        },
        "s2a": {
            "scenario_id": s2a_profile.scenario_id,
            "run_schema": s2a_run.schema_version,
            "profile_id": s2a_profile.profile_id,
            "recomputed_original_reward": s2a_metrics["original_reward_cumulative"].value,
            "physical_metrics_keep_s2a_availability": {
                metric: s2a_metrics[metric].status.value
                for metric in ("ces_cumulative", "functional_success_rate",
                               "functional_deficit_cumulative", "production_cumulative")
            },
        },
        "s7": {
            "scenario_id": s7_profile.scenario_id,
            "run_schema": s7_run.schema_version,
            "profile_id": s7_profile.profile_id,
            "recomputed_ces": s7_metrics["ces_cumulative"].value,
            "branch_records_evaluated": len(s7_episodes),
        },
        "s4": {
            "scenario_id": "S4",
            "run_schema": "hls-experiment-run/1.0",
            "profile_ids": [profile.profile_id for profile in s4_evaluation_profiles()],
        },
        "interpretation": "shared structures and evaluator are reused; scenario-specific metrics and units remain distinct",
        "historical_s2a_s7_rerun": False,
    }


def run() -> dict[str, Any]:
    historical_hashes_before = {
        "s2a": sha256(S2A_REFERENCE.read_bytes()).hexdigest(),
        "s4": sha256(S4_HISTORICAL_REFERENCE.read_bytes()).hexdigest(),
        "s7": sha256(S7_REFERENCE.read_bytes()).hexdigest(),
    }
    solver_hash_before = sha256(S4_SOLVER_SOURCE.read_bytes()).hexdigest()
    case = make_case()
    profiles = s4_evaluation_profiles()
    evaluator = PerformanceEvaluator()
    for profile in profiles:
        evaluator.register_profile(profile)

    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True,
    ).stdout.strip()
    git_status = subprocess.run(
        ["git", "status", "--porcelain"], check=True, capture_output=True, text=True,
    ).stdout
    working_tree_clean = not git_status.strip()
    run_records: dict[str, ExperimentRun] = {}
    record_sets: dict[str, tuple[EvaluationRecord, ...]] = {}
    solutions: dict[str, Any] = {}
    evaluations: dict[str, dict[str, dict]] = {}

    for policy_id in POLICY_IDS:
        transfer_available = policy_id == "B"
        solution = solve_bellman(case, transfer_available=transfer_available)
        solutions[policy_id] = solution
        run_record, records = adapt_s4_policy(
            case,
            solution,
            policy_id,
            transfer_available=transfer_available,
            source_pointer=f"{RESULT.as_posix()}#/policies/{policy_id}/solver_result",
            software_revision=revision if working_tree_clean else None,
        )
        restored = ExperimentRun.from_json(run_record.to_json())
        if restored.to_json() != run_record.to_json():
            raise AssertionError(f"S4 ExperimentRun JSON round-trip changed policy {policy_id}")
        run_records[policy_id] = run_record
        record_sets[policy_id] = records
        source_snapshot = (
            run_record.to_json(),
            [asdict(record) for record in records],
            [asdict(action) for action in solution.actions],
            solution.value,
        )
        evaluations[policy_id] = {}
        for profile in profiles:
            computed = evaluator.evaluate(profile.profile_id, policy_id, records)
            evaluations[policy_id][profile.profile_id] = {
                key: asdict(value) for key, value in computed.items()
            }
        if source_snapshot != (
            run_record.to_json(),
            [asdict(record) for record in records],
            [asdict(action) for action in solution.actions],
            solution.value,
        ):
            raise AssertionError("profile evaluation mutated S4 source run, records, or decisions")

    comparisons: dict[str, dict[str, dict]] = {}
    for profile in profiles:
        comparisons[profile.profile_id] = {}
        for metric_id in profile.metrics:
            left = evaluator.evaluate(profile.profile_id, "A", record_sets["A"])[metric_id]
            right = evaluator.evaluate(profile.profile_id, "B", record_sets["B"])[metric_id]
            comparisons[profile.profile_id][metric_id] = asdict(
                PerformanceEvaluator.compare(left, right)
            )

    policy_results = {}
    for policy_id in POLICY_IDS:
        solution = solutions[policy_id]
        transfer_selected = any(row.action.teaching is not None for row in solution.periods)
        policy_results[policy_id] = {
            "solver_value": solution.value,
            "visited_states": solution.visited_states,
            "transfer_available": policy_id == "B",
            "transfer_selected": transfer_selected,
            "actions": [asdict(action) for action in solution.actions],
            "periods": [asdict(row) for row in solution.periods],
            "experiment_run_id": run_records[policy_id].run_id,
            "evaluations": evaluations[policy_id],
        }

    cross_check = _cross_scenario_reuse_check()
    historical_hashes_after = {
        "s2a": sha256(S2A_REFERENCE.read_bytes()).hexdigest(),
        "s4": sha256(S4_HISTORICAL_REFERENCE.read_bytes()).hexdigest(),
        "s7": sha256(S7_REFERENCE.read_bytes()).hexdigest(),
    }
    if historical_hashes_after != historical_hashes_before:
        raise AssertionError("integration changed a historical S2a, S4, or S7 result artifact")
    solver_hash_after = sha256(S4_SOLVER_SOURCE.read_bytes()).hexdigest()
    if solver_hash_after != solver_hash_before:
        raise AssertionError("S4 solver source changed during integration run")
    if not all(cross_check["shared_types"].values()):
        raise AssertionError("S2a/S4/S7 did not reuse the common contract and PEF classes")
    result = {
        "experiment": "HLS-S4 N×K ExperimentRun v1 / HLS-PEF integration",
        "execution_source": "experiments.run_hls_s4_transfer_exact.make_case + hls.synthetic.hls_s4_transfer_exact.solve_bellman",
        "execution_mode": "fresh deterministic exact reference; historical writer not invoked",
        "configuration_id": "s4_exact_transfer_reference_T3_v1",
        "profiles": {profile.profile_id: asdict(profile) for profile in profiles},
        "policies_compared": list(POLICY_IDS),
        "experiment_runs": {policy: run_records[policy].to_dict() for policy in POLICY_IDS},
        "policy_results": policy_results,
        "comparisons_A_minus_B": comparisons,
        "profile_invariance": {
            "same_source_runs_and_records_used_for_both_profiles": True,
            "evaluation_mutated_source_records": False,
            "interpretation": "profiles select metrics/diagnostics only; they do not enter solver decisions",
        },
        "cross_scenario_contract_check": cross_check,
        "provenance": {
            "source_factory": "experiments.run_hls_s4_transfer_exact.make_case",
            "source_solver": "hls.synthetic.hls_s4_transfer_exact.solve_bellman",
            "historical_reference": "results/experiments/hls_s4_transfer_exact/results.json",
            "new_integration_artifact": RESULT.as_posix(),
            "random_seeds": [],
            "randomness": "none; deterministic finite-horizon exact instance",
            "software_revision": revision if working_tree_clean else None,
            "base_git_revision": revision,
            "working_tree_clean": working_tree_clean,
            "source_sha256": {
                "solver": solver_hash_after,
                "adapter": sha256(Path("src/hls/synthetic/s4_pef_adapter.py").read_bytes()).hexdigest(),
                "runner": sha256(Path(__file__).read_bytes()).hexdigest(),
            },
            "historical_artifact_sha256_before": historical_hashes_before,
            "historical_artifact_sha256_after": historical_hashes_after,
            "solver_source_sha256_before": solver_hash_before,
            "solver_source_sha256_after": solver_hash_after,
            "source_result_pointer": "new artifact policies/A|B/solver_result",
        },
        "regression_checks": {
            "A_reward": solutions["A"].value,
            "B_reward": solutions["B"].value,
            "expected_reward_each": 1.9175000000000004,
            "functional_success_rate_each": 1.0 / 3.0,
            "functional_deficit_each": 0.5325,
            "productive_effort_each": sum(row.productive_effort for row in solutions["A"].periods),
            "teaching_effort_each": sum(
                0.0 if row.action.teaching is None else row.action.teaching.effort
                for row in solutions["A"].periods
            ),
            "teaching_resource_each": sum(row.teaching_resource for row in solutions["A"].periods),
            "total_resource_each": sum(row.total_resource for row in solutions["A"].periods),
            "A_B_reward_difference": solutions["A"].value - solutions["B"].value,
            "neither_policy_selected_teaching": all(
                not policy_results[policy]["transfer_selected"] for policy in POLICY_IDS
            ),
            "comparison_difference_zero_within_1e-12": abs(
                comparisons[profiles[0].profile_id]["original_reward_cumulative"]["value"]
            ) <= 1e-12,
        },
    }
    return result


if __name__ == "__main__":
    output = run()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(RESULT)
