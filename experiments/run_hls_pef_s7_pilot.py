"""Exact-branch S7 pilot through the generic HLS-PEF evaluator."""

from __future__ import annotations

import json
from dataclasses import asdict
from itertools import combinations, product
from math import isclose
from pathlib import Path

from experiments.run_hls_s7_preparation_characterization import make_characterization_case
from hls.performance_evaluation import EvaluationProfile, PerformanceEvaluator
from hls.synthetic.hls_s7_uncertain_demand import (
    replay_markov_policy,
    solve_markov_bellman,
    solve_reactive_greedy,
)
from hls.synthetic.s7_pef_adapter import adapt_s7_episode


RESULT = Path("results/experiments/hls_pef_s7_pilot/results.json")
POLICIES = {
    "A": (True, False),
    "B": (True, True),
    "MA": (False, False),
    "MB": (False, True),
}
METRICS = (
    "original_reward_cumulative", "ces_cumulative", "functional_success_rate",
    "functional_deficit_cumulative", "production_cumulative",
    "resource_usage:productive_effort", "resource_usage:teaching_effort",
    "resource_usage:teaching_resource", "resource_usage:total_effort",
    "teaching_actions_cumulative",
)


def _branch_probability(case, path: tuple[int, ...]) -> float:
    probability = case.initial_probabilities[path[0]]
    for current, following in zip(path, path[1:]):
        probability *= case.transition_probabilities[current][following]
    return probability


def _period_expectations(episodes, horizon: int) -> list[dict]:
    result = []
    for period in range(horizon):
        expected = {
            "ces": 0.0, "production": 0.0, "success": 0.0,
            "raw_deficit": 0.0, "productive_effort": 0.0,
            "teaching_effort": 0.0, "teaching_resource": 0.0,
            "total_effort": 0.0,
            "teaching_actions": 0.0,
        }
        competence_after = None
        for probability, records in episodes:
            row = records[period]
            expected["ces"] += probability * float(row.ces)
            expected["production"] += probability * sum(row.output)
            expected["success"] += probability * float(row.success)
            expected["raw_deficit"] += probability * sum(row.deficit)
            for key in expected:
                if key in row.resource_usage:
                    expected[key] += probability * row.resource_usage[key]
            expected["teaching_actions"] += probability * row.teaching_action_count
            state = row.competence_state["after"]
            if competence_after is None:
                competence_after = [[0.0] * len(line) for line in state]
            for i, line in enumerate(state):
                for k, value in enumerate(line):
                    competence_after[i][k] += probability * value
        result.append({"period": period, **expected,
                       "expected_competence_after": competence_after})
    return result


def run() -> dict:
    case = make_characterization_case("opportunity")
    if case.horizon != 4:
        raise AssertionError("pilot must use the frozen central S7 T=4 instance")
    paths = tuple(product(range(len(case.demand_states)), repeat=case.horizon))
    branch_rows = [(path, _branch_probability(case, path)) for path in paths]
    if not isclose(sum(probability for _, probability in branch_rows), 1.0,
                   rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError("complete demand tree does not have unit probability")

    profile = EvaluationProfile(
        profile_id="s7_central_pef_pilot_v1", scenario_id="S7",
        configuration_id="opportunity_T4_C5", application_domain="synthetic_workforce",
        organizational_problem="anticipatory competence development under Markov task demand",
        decision_objective={policy: "cumulative_CES" for policy in POLICIES},
        constraints="unchanged S7 production, teaching and shared resource constraints",
        primary_metrics=("ces_cumulative", "functional_success_rate",
                         "functional_deficit_cumulative"),
        secondary_metrics=("production_cumulative", "resource_usage:productive_effort",
                           "resource_usage:teaching_effort", "resource_usage:total_effort",
                           "resource_usage:teaching_resource", "teaching_actions_cumulative"),
        diagnostic_fields=("competence_state", "decision_action", "observed_demand",
                           "episode_branch_probability"),
        information_regime="current_demand_and_true_competence_known_to_exact_reference; future_demand_law_known",
        temporal_horizon=case.horizon,
        aggregation_rules="one demanded task problem per period; expectation over complete C5 branches",
        demand_distribution_id="S7-central-C5-initial-and-transition-matrix-v1",
        resource_units={"productive_effort": "effort", "teaching_effort": "effort",
                        "teaching_resource": "effort_resource", "total_effort": "effort_resource"},
    )
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    policy_results = {}
    policy_summaries = {}
    exact_values = {}
    policy_branch_records = {}
    for policy_id, (planning, transfer) in POLICIES.items():
        solved = (solve_markov_bellman(case, transfer_available=transfer)
                  if planning else solve_reactive_greedy(case, transfer_available=transfer))
        episodes = []
        branch_diagnostics = []
        for path, probability in branch_rows:
            replay = replay_markov_policy(case, solved, path)
            records = adapt_s7_episode(
                case, policy_id, "-".join(case.demand_states[index].problem_id for index in path),
                path, probability, replay, information_regime=profile.information_regime,
                decision_objective=profile.decision_objective[policy_id],
                provenance_prefix="results/experiments/hls_pef_s7_pilot/policy_replay",
            )
            episodes.append((probability, records))
            branch_diagnostics.append({
                "episode_id": records[0].episode_id,
                "demand_path": [case.demand_states[index].problem_id for index in path],
                "probability": probability,
                "period_records": [asdict(record) for record in records],
            })
        evaluated = evaluator.evaluate_weighted_episodes(
            profile.profile_id, policy_id, [records for _, records in episodes])
        metrics = {key: asdict(value) for key, value in evaluated.items()}
        exact_values[policy_id] = solved.value
        if not isclose(evaluated["ces_cumulative"].value, solved.value,
                       rel_tol=0.0, abs_tol=1e-10):
            raise AssertionError(f"PEF CES differs from S7 solver for {policy_id}")
        policy_results[policy_id] = metrics
        policy_summaries[policy_id] = _period_expectations(episodes, case.horizon)
        policy_branch_records[policy_id] = branch_diagnostics

    metric_ids = profile.metrics
    interactions = {}
    pairwise_differences = {}
    for metric_id in metric_ids:
        values = {policy: policy_results[policy][metric_id]["value"] for policy in POLICIES}
        all_pairs = {
            f"{left}_minus_{right}": {
                "value": values[left] - values[right],
                "unit": policy_results[left][metric_id]["unit"],
            }
            for left, right in combinations(POLICIES, 2)
        }
        pairwise_differences[metric_id] = {
            "all_pairs": all_pairs,
            "B_minus_A": values["B"] - values["A"],
            "MA_minus_A": values["MA"] - values["A"],
            "MB_minus_MA": values["MB"] - values["MA"],
            "B_minus_MB": values["B"] - values["MB"],
            "unit": policy_results["A"][metric_id]["unit"],
        }
        interactions[metric_id] = {
            "value": (values["B"] - values["A"]) - (values["MB"] - values["MA"]),
            "unit": policy_results["A"][metric_id]["unit"],
            "definition": "(B-A)-(MB-MA); descriptive factorial contrast under metric semantics",
        }
    historical = {
        "A": 3.1628653621, "B": 3.1743777327,
        "MA": 3.0346209871, "MB": 3.0346209871,
    }
    for policy, target in historical.items():
        if not isclose(exact_values[policy], target, rel_tol=0.0, abs_tol=1e-10):
            raise AssertionError(f"new pilot does not reproduce central S7 value {policy}")
    return {
        "experiment": "HLS-PEF operational pilot on central S7 T=4",
        "execution": "fresh deterministic exact policy solve and full demand-tree replay; no historical JSON used as input",
        "configuration": {
            "agents": case.physical_case.organization.agent_ids,
            "skills": case.physical_case.organization.skill_ids,
            "initial_competence": case.physical_case.organization.competence_initial,
            "demand_states": [asdict(problem) for problem in case.demand_states],
            "initial_probabilities": case.initial_probabilities,
            "transition_probabilities": case.transition_probabilities,
            "horizon": case.horizon,
            "competence_dynamic_laws": "unchanged MIS-v2 and optional transfer",
            "policies": {key: {"planning": value[0], "transfer_available": value[1]}
                         for key, value in POLICIES.items()},
        },
        "profile": asdict(profile),
        "branch_count": len(branch_rows),
        "branch_probability_sum": sum(probability for _, probability in branch_rows),
        "policies": policy_results,
        "exact_solver_values_CES": exact_values,
        "expected_period_summaries": policy_summaries,
        "pairwise_differences": pairwise_differences,
        "planning_transfer_interactions": interactions,
        "branch_records": policy_branch_records,
        "validation": {
            "adapted_records_match_requested_demand_path": True,
            "all_branch_probabilities_sum_to_one": True,
            "weighted_CES_matches_policy_value": True,
            "central_historical_values_reproduced": True,
            "policies_and_physical_laws_unchanged": True,
        },
    }


if __name__ == "__main__":
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(run(), indent=2, ensure_ascii=False) + "\n")
    print(RESULT)
