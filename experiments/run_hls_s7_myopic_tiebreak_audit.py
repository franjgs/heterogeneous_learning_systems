"""BEST-MYOPIC audit on the existing central S7 T=4 instance."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict
from itertools import combinations, product
from math import isclose
from pathlib import Path
from typing import Mapping

from experiments.run_hls_s7_preparation_characterization import make_characterization_case
from hls.performance_evaluation import EvaluationProfile, PerformanceEvaluator
from hls.synthetic.hls_s4_transfer_exact import _step
from hls.synthetic.hls_s7_uncertain_demand import (
    TOL,
    S7ExactResult,
    _state_cases,
    audit_myopic_tiebreaks,
    positive_competence_gain,
    replay_markov_policy,
    select_best_myopic_action,
    solve_best_myopic,
    solve_markov_bellman,
    solve_reactive_greedy,
)
from hls.synthetic.s7_pef_adapter import adapt_s7_episode


RESULT = Path("results/experiments/hls_s7_myopic_tiebreak_audit/results.json")
POLICIES = {
    "A": {"kind": "bellman", "transfer": False},
    "B": {"kind": "bellman", "transfer": True},
    "MA": {"kind": "legacy_myopic", "transfer": False},
    "MB": {"kind": "legacy_myopic", "transfer": True},
    "BMA": {"kind": "best_myopic", "transfer": False},
    "BMB": {"kind": "best_myopic", "transfer": True},
}
METRICS = (
    "original_reward_cumulative", "ces_cumulative", "functional_success_rate",
    "functional_deficit_cumulative", "production_cumulative",
    "resource_usage:productive_effort", "resource_usage:teaching_effort",
    "resource_usage:teaching_resource", "resource_usage:total_effort",
    "teaching_actions_cumulative",
)
HISTORICAL_CES = {
    "A": 3.1628653621,
    "B": 3.1743777327,
    "MA": 3.0346209871,
    "MB": 3.0346209871,
}


def _path_probability(case, path: tuple[int, ...]) -> float:
    probability = case.initial_probabilities[path[0]]
    for current, following in zip(path, path[1:]):
        probability *= case.transition_probabilities[current][following]
    return probability


def _action_data(action) -> dict:
    return {"production": action.production,
            "teaching": None if action.teaching is None else asdict(action.teaching)}


def _period_summary(episodes, horizon: int) -> list[dict]:
    names = ("ces", "production", "success", "raw_deficit", "productive_effort",
             "teaching_effort", "teaching_resource", "total_effort", "teaching_actions")
    rows = []
    for period in range(horizon):
        totals = dict.fromkeys(names, 0.0)
        competence = None
        for probability, records in episodes:
            row = records[period]
            totals["ces"] += probability * row.ces
            totals["production"] += probability * sum(row.output)
            totals["success"] += probability * float(row.success)
            totals["raw_deficit"] += probability * sum(row.deficit)
            for metric in names:
                if metric in row.resource_usage:
                    totals[metric] += probability * row.resource_usage[metric]
            totals["teaching_actions"] += probability * row.teaching_action_count
            after = row.competence_state["after"]
            if competence is None:
                competence = [[0.0] * len(line) for line in after]
            for i, line in enumerate(after):
                for k, value in enumerate(line):
                    competence[i][k] += probability * value
        rows.append({"period": period, **totals, "expected_competence_after": competence})
    return rows


def _solve(case, policy_id: str, transfer: bool) -> S7ExactResult:
    kind = POLICIES[policy_id]["kind"]
    if kind == "bellman":
        return solve_markov_bellman(case, transfer_available=transfer)
    if kind == "legacy_myopic":
        return solve_reactive_greedy(case, transfer_available=transfer)
    return solve_best_myopic(case, transfer_available=transfer)


def _bellman_sacrifice_audit(case, result: S7ExactResult, *, transfer: bool,
                             occupancy: Mapping[tuple, float]) -> dict:
    """Exact one-state action replacement Q comparison under Bellman continuation."""
    state_cases = _state_cases(case, transfer_available=transfer, efficacy=None)
    rows = []
    for state in sorted(result.actions_by_state, key=lambda s: (s[0], s[2], s[1])):
        time, competence, demand_state = state
        if time >= case.horizon:
            continue
        physical, actions = state_cases[demand_state]
        demand = case.demand_states[demand_state]
        evaluated = []
        for action in actions:
            immediate, successor = _step(physical, competence, demand, action)
            evaluated.append((action, immediate, successor))
        max_immediate = max(reward for _, reward, _ in evaluated)
        bellman_action = result.actions_by_state[state]
        bellman_immediate, bellman_successor = next(
            (reward, successor) for action, reward, successor in evaluated
            if action == bellman_action
        )
        if max_immediate - bellman_immediate <= TOL:
            continue
        best_action, _, _, best_gain = select_best_myopic_action(competence, evaluated)

        def q_value(immediate, successor):
            if time + 1 >= case.horizon:
                return immediate
            continuation = sum(
                probability * result.value_by_state[(time + 1, successor, next_state)]
                for next_state, probability in enumerate(case.transition_probabilities[demand_state])
            )
            return immediate + continuation

        best_immediate, best_successor = next(
            (reward, successor) for action, reward, successor in evaluated
            if action == best_action
        )
        q_bellman = q_value(bellman_immediate, bellman_successor)
        q_myopic_then_bellman = q_value(best_immediate, best_successor)
        state_probability = occupancy.get(state, 0.0)
        rows.append({
            "period": time,
            "demand": demand.problem_id,
            "competence_state": competence,
            "state_probability_under_bellman": state_probability,
            "bellman_action": _action_data(bellman_action),
            "best_myopic_action": _action_data(best_action),
            "maximum_immediate_CES": max_immediate,
            "bellman_immediate_CES": bellman_immediate,
            "best_myopic_immediate_CES": best_immediate,
            "immediate_CES_sacrifice": max_immediate - bellman_immediate,
            "bellman_positive_competence_gain": positive_competence_gain(
                competence, bellman_successor),
            "best_myopic_positive_competence_gain": best_gain,
            "bellman_Q_if_followed_by_Bellman": q_bellman,
            "best_myopic_action_Q_if_followed_by_Bellman": q_myopic_then_bellman,
            "local_Q_advantage_of_Bellman_action": q_bellman - q_myopic_then_bellman,
            "occupancy_weighted_one_step_Q_advantage": state_probability * (
                q_bellman - q_myopic_then_bellman),
            "successor_competence_difference_Bellman_minus_BEST_MYOPIC": tuple(
                tuple(bellman_successor[i][k] - best_successor[i][k]
                      for k in range(len(competence[i])))
                for i in range(len(competence))
            ),
        })
    return {
        "strict_immediate_sacrifice_state_count": len(rows),
        "occupancy_weighted_one_step_Q_advantage_sum": sum(
            row["occupancy_weighted_one_step_Q_advantage"] for row in rows),
        "interpretation": "one-step replacements at Bellman occupancy, then Bellman continuation; not an additive full-policy causal decomposition",
        "states": rows,
    }


def run() -> dict:
    case = make_characterization_case("opportunity")
    if case.horizon != 4:
        raise AssertionError("audit is restricted to the central S7 T=4 instance")
    paths = tuple(product(range(len(case.demand_states)), repeat=case.horizon))
    branches = tuple((path, _path_probability(case, path)) for path in paths)
    probability_sum = sum(probability for _, probability in branches)
    if not isclose(probability_sum, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError("complete demand tree probabilities must sum to one")

    evaluator = PerformanceEvaluator()
    profile = EvaluationProfile(
        profile_id="s7_myopic_tiebreak_audit_v1", scenario_id="S7",
        configuration_id="opportunity_T4_C5", application_domain="synthetic_workforce",
        organizational_problem="myopic tie-breaking versus intertemporal planning",
        decision_objective={policy: "cumulative_CES" for policy in POLICIES},
        constraints="central S7 production, teaching and shared resource constraints",
        primary_metrics=("ces_cumulative", "functional_success_rate",
                         "functional_deficit_cumulative"),
        secondary_metrics=("production_cumulative", "resource_usage:productive_effort",
                           "resource_usage:teaching_effort", "resource_usage:teaching_resource",
                           "resource_usage:total_effort", "teaching_actions_cumulative"),
        diagnostic_fields=("competence_state", "decision_action", "observed_demand",
                           "episode_branch_probability"),
        information_regime="current_demand_and_true_competence_known_to_exact_reference; future_demand_law_known_to_Bellman_only",
        temporal_horizon=case.horizon,
        aggregation_rules="one demanded task-period service; exact expectation over complete C5 demand branches",
        demand_distribution_id="S7-central-C5-initial-and-transition-matrix-v1",
        resource_units={"productive_effort": "effort", "teaching_effort": "effort",
                        "teaching_resource": "effort_resource", "total_effort": "effort_resource"},
    )
    evaluator.register_profile(profile)

    solved = {}
    policy_metrics = {}
    summaries = {}
    branch_records = {}
    occupancies = {policy: defaultdict(float) for policy in ("A", "B")}
    for policy, config in POLICIES.items():
        result = _solve(case, policy, config["transfer"])
        solved[policy] = result
        episodes = []
        rows = []
        for path, probability in branches:
            replay = replay_markov_policy(case, result, path)
            for period, row in enumerate(replay):
                state = (period, row["competence_before"], row["demand_state"])
                if policy in occupancies:
                    occupancies[policy][state] += probability
            records = adapt_s7_episode(
                case, policy,
                "-".join(case.demand_states[index].problem_id for index in path),
                path, probability, replay, information_regime=profile.information_regime,
                decision_objective="cumulative_CES",
                provenance_prefix="results/experiments/hls_s7_myopic_tiebreak_audit/policy_replay",
            )
            episodes.append(records)
            rows.append({"episode_id": records[0].episode_id,
                         "demand_path": [case.demand_states[i].problem_id for i in path],
                         "probability": probability,
                         "period_records": [asdict(record) for record in records]})
        evaluated = evaluator.evaluate_weighted_episodes(profile.profile_id, policy, episodes)
        policy_metrics[policy] = {key: asdict(value) for key, value in evaluated.items()}
        summaries[policy] = _period_summary(
            [(records[0].branch_probability, records) for records in episodes], case.horizon)
        branch_records[policy] = rows

    tie_audits = {}
    for legacy, best, transfer in (("MA", "BMA", False), ("MB", "BMB", True)):
        rows = audit_myopic_tiebreaks(case, solved[legacy], solved[best],
                                      transfer_available=transfer)
        tie_audits[legacy] = {
            "states_audited": len(rows),
            "states_with_tie": sum(row["tied_action_count"] > 1 for row in rows),
            "states_where_selected_action_differs": sum(row["selected_actions_differ"] for row in rows),
            "tie_class_counts_nonexclusive": dict(Counter(
                tie_class for row in rows if row["tied_action_count"] > 1
                for tie_class in row["tie_classes"])),
            "decisions": [
                {**row, "legacy_action": _action_data(row["legacy_action"]),
                 "best_myopic_action": _action_data(row["best_myopic_action"])}
                for row in rows
            ],
        }

    pairwise = {}
    interactions = {}
    for metric in profile.metrics:
        value = {policy: policy_metrics[policy][metric]["value"] for policy in POLICIES}
        unit = policy_metrics["A"][metric]["unit"]
        pairwise[metric] = {
            f"{left}_minus_{right}": {"value": value[left] - value[right], "unit": unit}
            for left, right in combinations(POLICIES, 2)
        }
        interactions[metric] = {
            "planning_Bellman_minus_BEST_MYOPIC_without_transfer": value["A"] - value["BMA"],
            "planning_Bellman_minus_BEST_MYOPIC_with_transfer": value["B"] - value["BMB"],
            "transfer_Bellman": value["B"] - value["A"],
            "transfer_BEST_MYOPIC": value["BMB"] - value["BMA"],
            "planning_by_transfer_interaction": (value["B"] - value["BMB"])
                                                - (value["A"] - value["BMA"]),
            "unit": unit,
        }

    ces = {policy: policy_metrics[policy]["ces_cumulative"]["value"] for policy in POLICIES}
    decomposition = {
        "without_transfer": {
            "D0_historical_Bellman_minus_legacy_myopic": ces["A"] - ces["MA"],
            "D1_Bellman_minus_BEST_MYOPIC": ces["A"] - ces["BMA"],
            "T0_BEST_MYOPIC_minus_legacy_myopic": ces["BMA"] - ces["MA"],
        },
        "with_transfer": {
            "D0T_historical_Bellman_minus_legacy_myopic": ces["B"] - ces["MB"],
            "D1T_Bellman_minus_BEST_MYOPIC": ces["B"] - ces["BMB"],
            "TT_BEST_MYOPIC_minus_legacy_myopic": ces["BMB"] - ces["MB"],
        },
    }
    for key, row in decomposition.items():
        if key == "without_transfer":
            d0, d1, tie = ("D0_historical_Bellman_minus_legacy_myopic",
                           "D1_Bellman_minus_BEST_MYOPIC",
                           "T0_BEST_MYOPIC_minus_legacy_myopic")
        else:
            d0, d1, tie = ("D0T_historical_Bellman_minus_legacy_myopic",
                           "D1T_Bellman_minus_BEST_MYOPIC",
                           "TT_BEST_MYOPIC_minus_legacy_myopic")
        row["identity_residual"] = row[d0] - row[d1] - row[tie]
        if abs(row["identity_residual"]) > 1e-10:
            raise AssertionError(f"tie-break accounting identity failed: {key}")

    sacrifice = {
        "A_without_transfer": _bellman_sacrifice_audit(
            case, solved["A"], transfer=False, occupancy=occupancies["A"]),
        "B_with_transfer": _bellman_sacrifice_audit(
            case, solved["B"], transfer=True, occupancy=occupancies["B"]),
    }
    historical_differences = {key: abs(ces[key] - target)
                              for key, target in HISTORICAL_CES.items()}
    if max(historical_differences.values()) > 1e-10:
        raise AssertionError(f"historical policy values changed: {historical_differences}")
    return {
        "experiment": "S7 BEST-MYOPIC tie-break audit",
        "design": {
            "instance": "central S7 preparation opportunity",
            "horizon": case.horizon,
            "demand_states": [problem.problem_id for problem in case.demand_states],
            "initial_probabilities": case.initial_probabilities,
            "transition_probabilities": case.transition_probabilities,
            "branch_count": len(branches),
            "branch_probability_sum": probability_sum,
            "myopic_primary_tolerance": TOL,
            "best_myopic_secondary_criterion": "sum of positive immediate competence increments after existing MIS-v2 and optional transfer transitions",
            "remaining_ties": "canonical lexicographic action key; independent of catalog order",
            "information": "same current true competence and current demand as historical exact S7 references; BEST-MYOPIC does not inspect future demand law or Bellman values",
        },
        "policy_definitions": POLICIES,
        "profile": asdict(profile),
        "policies": policy_metrics,
        "expected_period_summaries": summaries,
        "branch_records": branch_records,
        "myopic_tie_audit": tie_audits,
        "decomposition_CES": decomposition,
        "pairwise_differences": pairwise,
        "planning_transfer_interactions": interactions,
        "bellman_strict_immediate_sacrifice": sacrifice,
        "historical_policy_CES_absolute_differences": historical_differences,
        "validation": {
            "all_16_branch_probabilities_sum_to_one": isclose(probability_sum, 1.0, abs_tol=1e-12),
            "legacy_four_values_reproduced": max(historical_differences.values()) <= 1e-10,
            "CES_maximizing_best_myopic": True,
            "decomposition_identities_hold": all(abs(row["identity_residual"]) <= 1e-10
                                                   for row in decomposition.values()),
            "HLS_PEF_provenance_present": all(
                metric["status"] == "VALID" and metric["provenance"]
                for values in policy_metrics.values() for metric in values.values()),
        },
    }


if __name__ == "__main__":
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(run(), indent=2, ensure_ascii=False) + "\n")
    print(RESULT)
