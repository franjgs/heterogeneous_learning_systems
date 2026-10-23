#!/usr/bin/env python3
"""Run the original S2a route and evaluate its two policies through HLS-PEF."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from experiments.run_hls_s2a_static_demand import run_s2a
from hls.experiment_contract import ExperimentRun
from hls.performance_evaluation import PerformanceEvaluator
from hls.synthetic.s7_pef_adapter import adapt_s7_pilot_artifact_to_experiment_run
from hls.synthetic.s2a_pef_adapter import (
    CONFIGURATION_ID,
    POLICY_IDS,
    PROFILE_ID,
    adapt_s2a_policy,
    s2a_evaluation_profile,
)


RESULT = Path("results/experiments/hls_s2a_pef_integration/results.json")
S7_REFERENCE = Path("results/experiments/hls_pef_s7_pilot/results.json")


def run() -> dict[str, Any]:
    """Execute the original function once; adaptation/evaluation are downstream."""
    source = run_s2a()
    profile = s2a_evaluation_profile()
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)

    runs: dict[str, ExperimentRun] = {}
    policy_results: dict[str, dict] = {}
    pef_results: dict[str, dict] = {}
    for policy_id in POLICY_IDS:
        run_record, records = adapt_s2a_policy(
            source,
            policy_id,
            source_pointer=f"{RESULT.as_posix()}#/source_runner_result/periods",
        )
        # Assert the common serializer can consume and restore the full envelope.
        restored = ExperimentRun.from_json(run_record.to_json())
        if restored.to_json() != run_record.to_json():
            raise AssertionError(f"ExperimentRun round-trip changed {policy_id}")
        runs[policy_id] = run_record
        policy_results[policy_id] = {
            "run_id": run_record.run_id,
            "mechanism_id": run_record.mechanism_id,
            "policy_id": run_record.policy_id,
            "horizon_reward": run_record.mechanism_results["horizon_reward"],
            "assignment_count": run_record.mechanism_results["assignment_count"],
            "period_diagnostics": [
                {
                    "period": record.period,
                    **record.available_metadata,
                    "original_reward": record.original_reward,
                    "resource_usage": record.resource_usage,
                }
                for record in records
            ],
        }
        evaluated = evaluator.evaluate(PROFILE_ID, policy_id, records)
        pef_results[policy_id] = {key: asdict(value) for key, value in evaluated.items()}

    comparison = {
        "exact_minus_greedy_original_reward": asdict(PerformanceEvaluator.compare(
            evaluator.evaluate(
                PROFILE_ID, "exact",
                adapt_s2a_policy(source, "exact", source_pointer="original_runner_result")[1],
            )["original_reward_cumulative"],
            evaluator.evaluate(
                PROFILE_ID, "greedy",
                adapt_s2a_policy(source, "greedy", source_pointer="original_runner_result")[1],
            )["original_reward_cumulative"],
        )),
        "same_configuration": True,
        "same_constraints_objective_units_horizon_and_information": True,
        "interpretation": "deterministic integration check for this S2a instance; not a general policy claim",
    }

    # This sequence enumeration is performed by the source runner as an
    # independent optimality check. It is not an executable policy record.
    validation = {
        "role": "optimality_validation_reference_not_policy",
        "method": "exhaustive Cartesian enumeration of feasible per-period matchings",
        "global_exhaustive_optimum": source["horizon_reward"]["global_exhaustive_optimum"],
        "global_exhaustive_plan": source["global_exhaustive_plan"],
        "sequences_enumerated": source["horizon_reward"]["global_sequences_enumerated"],
        "exact_matches_reference": (
            source["horizon_reward"]["exact_per_period"]
            == source["horizon_reward"]["global_exhaustive_optimum"]
        ),
    }

    # S7 historically emitted common PEF records but not ExperimentRun.
    # Convert one already-stored policy result to the common envelope as a
    # structural reuse check; do not rerun or overwrite the S7 pilot.
    if not S7_REFERENCE.is_file():
        raise FileNotFoundError(f"stored S7 integration reference not found: {S7_REFERENCE}")
    s7_artifact = json.loads(S7_REFERENCE.read_text())
    s7_run = adapt_s7_pilot_artifact_to_experiment_run(
        s7_artifact, "A", source_pointer=S7_REFERENCE.as_posix(),
    )
    if ExperimentRun.from_json(s7_run.to_json()).to_json() != s7_run.to_json():
        raise AssertionError("stored S7 ExperimentRun envelope failed JSON round-trip")
    cross_scenario_contract_check = {
        "s2a_schema_version": runs["exact"].schema_version,
        "s7_schema_version": s7_run.schema_version,
        "same_experiment_run_type": type(runs["exact"]) is type(s7_run),
        "s2a_pef_profile_id": PROFILE_ID,
        "s7_pef_profile_id": s7_artifact["profile"]["profile_id"],
        "s7_policy_id": s7_run.policy_id,
        "s7_event_count": len(s7_run.events),
        "s7_source_artifact_preserved": S7_REFERENCE.as_posix(),
        "reused_shared_types": ["ExperimentRun", "EvaluationProfile", "EvaluationRecord",
                                "EvaluationResult", "PerformanceEvaluator"],
        "scenario_specific_metrics_remain_distinct": True,
        "s7_experiment_rerun": False,
    }

    source_periods = [
        {key: value for key, value in period.items() if not key.endswith("_seconds")}
        for period in source["periods"]
    ]
    source_summary = {
        "experiment": source["experiment"],
        "agents": source["agents"],
        "tasks": source["tasks"],
        "competence_matrix_agent_by_task": source["matrix_C_agent_by_task"],
        "demands": source["demands"],
        "capacity_per_period": source["capacity_per_period"],
        "horizon_reward": source["horizon_reward"],
        "periods": source_periods,
        "assumptions": source["assumptions"],
    }
    return {
        "experiment": "HLS-S2a common-contract and PEF vertical slice",
        "execution_source": "experiments.run_hls_s2a_static_demand.run_s2a",
        "execution_mode": "fresh deterministic execution; original runner function called once",
        "configuration_id": CONFIGURATION_ID,
        "profile": asdict(profile),
        "policies_compared": list(POLICY_IDS),
        "policy_results": policy_results,
        "experiment_runs": {key: value.to_dict() for key, value in runs.items()},
        "pef_results": pef_results,
        "comparisons": comparison,
        "optimality_validation": validation,
        "cross_scenario_contract_check": cross_scenario_contract_check,
        "source_runner_result": source_summary,
        "provenance": {
            "source_runner": "experiments/run_hls_s2a_static_demand.py::run_s2a",
            "source_artifact_preserved": "results/experiments/hls_s2a_static_demand/results.json",
            "new_integration_artifact": RESULT.as_posix(),
            "random_seeds": [],
            "randomness": "none; deterministic finite instance",
            "software_revision": None,
            "note": "revision not inferred; descriptive timing fields excluded from this artifact",
        },
        "validation": {
            "source_result_reconciled_by_adapter": True,
            "experiment_run_json_round_trip": True,
            "pef_reward_reproduced": {
                policy: pef_results[policy]["original_reward_cumulative"]["value"]
                == policy_results[policy]["horizon_reward"]
                for policy in POLICY_IDS
            },
            "non_applicable_metrics_have_no_numeric_value": all(
                pef_results[policy][metric]["status"] == "NOT_APPLICABLE"
                and pef_results[policy][metric]["value"] is None
                for policy in POLICY_IDS
                for metric in ("ces_cumulative", "functional_success_rate",
                               "functional_deficit_cumulative", "production_cumulative")
            ),
            "global_enumeration_is_not_registered_as_policy": True,
        },
    }


if __name__ == "__main__":
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(run(), indent=2, ensure_ascii=False) + "\n")
    print(RESULT)
