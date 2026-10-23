"""Read existing S4/S7 JSON and validate HLS-PEF without simulation."""

from __future__ import annotations

import json
from dataclasses import asdict
from math import isclose
from pathlib import Path

from hls.performance_evaluation import (
    EvaluationProfile,
    EvaluationRecord,
    PerformanceEvaluator,
    Status,
)


S4 = Path("results/experiments/hls_s4_transfer_exact/results.json")
S7_PREP = Path("results/experiments/hls_s7_preparation_characterization/results.json")
S7_MECH = Path("results/experiments/hls_s7_mechanistic_robustness/results.json")
RESULT = Path("results/experiments/hls_pef_retrospective/results.json")
METRICS = (
    "original_reward_cumulative", "ces_cumulative", "functional_success_rate",
    "functional_deficit_cumulative", "production_cumulative",
    "resource_usage:productive_effort", "resource_usage:teaching_resource",
    "resource_usage:total_resource",
)


def _as_dict(value):
    return asdict(value)


def run() -> dict:
    evaluator = PerformanceEvaluator()
    s4_data = json.loads(S4.read_text())
    s7_prep = json.loads(S7_PREP.read_text())
    s7_mech = json.loads(S7_MECH.read_text())

    s4_profile = EvaluationProfile(
        "s4_exact", "S4", "transfer_exact_T3", "synthetic_workforce",
        "MIS-v2 production with optional teaching", {"A": "CES", "B": "CES"},
        "same physical resource constraints; B permits optional teaching",
        METRICS[:5], METRICS[5:], information_regime="full_state_known",
        temporal_horizon=s4_data["design"]["horizon"],
        demand_distribution_id="deterministic:x-y-y",
        resource_units={"productive_effort": "effort", "teaching_resource": "effort",
                        "total_resource": "effort"},
    )
    evaluator.register_profile(s4_profile)
    s4_results = {}
    for policy in ("A", "B"):
        period_rows = s4_data[policy]["periods"]
        records = tuple(EvaluationRecord(
            "S4", "transfer_exact_T3", policy, row["period"],
            demand=row["problem_id"], output=tuple(row["outputs"]),
            requirements=tuple(s4_data["design"]["requirements"][row["period"]]),
            success=row["success"], deficit=tuple(row["deficits"]),
            resource_usage={"productive_effort": row["productive_effort"],
                            "teaching_resource": row["teaching_resource"],
                            "total_resource": row["total_resource"]},
            original_reward=row["reward"], ces=row["reward"],
            provenance=f"{S4}#/{policy}/periods/{index}",
            available_metadata={"reward_definition": "CES per /design/reward"},
        ) for index, row in enumerate(period_rows))
        evaluated = evaluator.evaluate("s4_exact", policy, records)
        assert isclose(evaluated["original_reward_cumulative"].value,
                       s4_data[policy]["value"], abs_tol=1e-10)
        assert isclose(evaluated["ces_cumulative"].value,
                       s4_data[policy]["value"], abs_tol=1e-10)
        s4_results[policy] = {key: _as_dict(value) for key, value in evaluated.items()}
    s4_ces_a = evaluator.import_historical(
        "s4_exact", "A", "ces_cumulative", s4_data["A"]["value"],
        f"{S4}#/A/value")
    s4_ces_b = evaluator.import_historical(
        "s4_exact", "B", "ces_cumulative", s4_data["B"]["value"],
        f"{S4}#/B/value")
    s4_difference = evaluator.compare(s4_ces_b, s4_ces_a)

    center = s7_mech["sensitivity"]["center"]
    prep = s7_prep["cases"]["opportunity"]
    mapping = {
        "A": ("J_A_bellman_no_transfer", "J_A_bellman_without_transfer"),
        "B": ("J_B_bellman_transfer_optional", "J_B_bellman_transfer_optional"),
        "MA": ("J_MA_reactive_no_transfer", "J_M_reactive_without_transfer"),
        "MB": ("J_MB_reactive_transfer_optional", "J_M_reactive_transfer_optional"),
    }
    s7_profile = EvaluationProfile(
        "s7_center", "S7", "opportunity_T4_C5", "synthetic_workforce",
        "unknown future Markov demand with endogenous competence", dict.fromkeys(mapping, "CES"),
        "same production resources; optional teaching for B/MB",
        METRICS[:5], METRICS[5:], information_regime="full_state_and_known_demand_law",
        temporal_horizon=prep["design"]["horizon"],
        demand_distribution_id="C5:opportunity:initial_and_transitions_in_prep_design",
        resource_units={"productive_effort": "effort", "teaching_resource": "effort",
                        "total_resource": "effort"},
    )
    evaluator.register_profile(s7_profile)
    s7_objects = {}
    s7_results = {}
    for policy, (mechanistic_key, prep_key) in mapping.items():
        stored_value = prep["exact_values"][prep_key]
        expected = center["expected_functional_and_resource_metrics"][mechanistic_key]
        assert isclose(stored_value, center["exact_values"][mechanistic_key], abs_tol=1e-10)
        assert isclose(stored_value, expected["expected_cumulative_CES"], abs_tol=1e-10)
        imported = {
            "original_reward_cumulative": evaluator.import_historical(
                "s7_center", policy, "original_reward_cumulative", stored_value,
                f"{S7_PREP}#/cases/opportunity/exact_values/{prep_key}"),
            "ces_cumulative": evaluator.import_historical(
                "s7_center", policy, "ces_cumulative", expected["expected_cumulative_CES"],
                f"{S7_MECH}#/sensitivity/center/expected_functional_and_resource_metrics/{mechanistic_key}/expected_cumulative_CES"),
            "functional_success_rate": evaluator.import_historical(
                "s7_center", policy, "functional_success_rate",
                expected["expected_services_completed"] / s7_profile.temporal_horizon,
                f"{S7_MECH}#/sensitivity/center/expected_functional_and_resource_metrics/{mechanistic_key}/expected_services_completed",
                note="stored_exact_expected_count_divided_by_declared_horizon; not_recomputed_from_paths"),
            "functional_deficit_cumulative": evaluator.import_historical(
                "s7_center", policy, "functional_deficit_cumulative",
                expected["expected_cumulative_raw_deficit_total"],
                f"{S7_MECH}#/sensitivity/center/expected_functional_and_resource_metrics/{mechanistic_key}/expected_cumulative_raw_deficit_total"),
            "production_cumulative": evaluator.unavailable(
                "s7_center", policy, "production_cumulative", Status.NOT_RECORDED,
                "full expected output by skill was not stored; illustrated branches are incomplete",
                f"{S7_MECH}#/sensitivity/center"),
        }
        for metric, historical_key in (
            ("resource_usage:productive_effort", "expected_productive_effort"),
            ("resource_usage:teaching_resource", "expected_teaching_resource_consumption"),
            ("resource_usage:total_resource", "expected_total_resource_consumption"),
        ):
            imported[metric] = evaluator.import_historical(
                "s7_center", policy, metric, expected[historical_key],
                f"{S7_MECH}#/sensitivity/center/expected_functional_and_resource_metrics/{mechanistic_key}/{historical_key}")
        s7_objects[policy] = imported
        s7_results[policy] = {key: _as_dict(value) for key, value in imported.items()}
    contrasts = {
        "planning_without_transfer": evaluator.compare(s7_objects["A"]["ces_cumulative"], s7_objects["MA"]["ces_cumulative"]),
        "planning_with_transfer": evaluator.compare(s7_objects["B"]["ces_cumulative"], s7_objects["MB"]["ces_cumulative"]),
        "transfer_with_planning": evaluator.compare(s7_objects["B"]["ces_cumulative"], s7_objects["A"]["ces_cumulative"]),
        "transfer_without_planning": evaluator.compare(s7_objects["MB"]["ces_cumulative"], s7_objects["MA"]["ces_cumulative"]),
    }
    interaction = contrasts["transfer_with_planning"].value - contrasts["transfer_without_planning"].value
    historical = center["decomposition"]
    for name, key in (
        ("planning_without_transfer", "planning_without_transfer_JA_minus_JMA"),
        ("planning_with_transfer", "planning_with_transfer_JB_minus_JMB"),
        ("transfer_with_planning", "transfer_with_planning_JB_minus_JA"),
        ("transfer_without_planning", "transfer_without_planning_JMB_minus_JMA"),
    ):
        assert isclose(contrasts[name].value, historical[key], abs_tol=1e-10)
    assert isclose(interaction, historical["interaction_I"], abs_tol=1e-10)
    return {
        "validation": "read_only_historical_json; no simulation or policy execution",
        "sources": [str(S4), str(S7_PREP), str(S7_MECH)],
        "s4": {"profile": _as_dict(s4_profile), "policies": s4_results,
               "transfer_difference_CES": _as_dict(s4_difference)},
        "s7": {"profile": _as_dict(s7_profile), "policies": s7_results,
               "contrasts_CES": {key: _as_dict(value) for key, value in contrasts.items()},
               "interaction_CES": interaction,
               "historical_aggregate_only": True},
    }


if __name__ == "__main__":
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(run(), indent=2, ensure_ascii=False) + "\n")
    print(RESULT)
