"""Exact mechanistic audit of anticipatory selection in central S7 without transfer."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from itertools import product
from math import isclose
from pathlib import Path

from experiments.run_hls_s7_preparation_characterization import make_characterization_case
from hls.hls_lab_nk_production import productive_outputs_nk
from hls.performance_evaluation import EvaluationProfile, PerformanceEvaluator
from hls.synthetic.hls_s4_transfer_exact import _step
from hls.synthetic.hls_s7_uncertain_demand import (
    TOL,
    S7ExactResult,
    _state_cases,
    positive_competence_gain,
    replay_markov_policy,
    select_current_demand_myopic_action,
    solve_current_demand_myopic,
    solve_markov_bellman,
    solve_reactive_greedy,
    solve_best_myopic,
)
from hls.synthetic.s7_pef_adapter import adapt_s7_episode


RESULT = Path("results/experiments/hls_s7_anticipatory_selection_audit/results.json")
POLICIES = ("A", "MA", "BMA", "CDM")


def _path_probability(case, path: tuple[int, ...]) -> float:
    result = case.initial_probabilities[path[0]]
    for current, following in zip(path, path[1:]):
        result *= case.transition_probabilities[current][following]
    return result


def _action_record(action) -> dict:
    teaching = action.teaching
    return {
        "production": action.production,
        "teaching": None if teaching is None else asdict(teaching),
    }


def _delta(before, after) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(after[i][k] - before[i][k] for k in range(len(before[i])))
                 for i in range(len(before)))


def _gain_summary(before, after) -> dict:
    matrix = _delta(before, after)
    return {
        "delta_competence_matrix": matrix,
        "net_delta_total": sum(sum(row) for row in matrix),
        "positive_gain_total": positive_competence_gain(before, after),
        "positive_gain_by_agent": tuple(sum(max(0.0, value) for value in row)
                                         for row in matrix),
        "positive_gain_by_task": tuple(
            sum(max(0.0, matrix[i][k]) for i in range(len(matrix)))
            for k in range(len(matrix[0]))
        ),
    }


def _occupancy_and_records(case, results, paths):
    occupancy = {policy: defaultdict(float) for policy in results}
    state_rows: dict[tuple, dict] = {}
    branch_records = {policy: [] for policy in results}
    pef_metrics = {}
    state_cases = _state_cases(case, transfer_available=False, efficacy=None)
    evaluator = PerformanceEvaluator()
    profile = EvaluationProfile(
        profile_id="s7_anticipatory_selection_v1", scenario_id="S7",
        configuration_id="opportunity_T4_C5",
        application_domain="synthetic_workforce",
        organizational_problem="anticipatory competence development under Markov demand",
        decision_objective={policy: "cumulative_CES" for policy in results},
        constraints="central S7 production and shared resource constraints; teaching unavailable",
        primary_metrics=("ces_cumulative", "functional_success_rate",
                         "functional_deficit_cumulative"),
        secondary_metrics=("production_cumulative", "resource_usage:productive_effort",
                           "resource_usage:teaching_effort", "resource_usage:total_effort"),
        diagnostic_fields=("competence_state", "decision_action", "observed_demand",
                           "episode_branch_probability"),
        information_regime="current competence and current demand observed; future demand law known to Bellman only",
        temporal_horizon=case.horizon,
        aggregation_rules="exact expectation over all C5 paths, one demanded service per period",
        demand_distribution_id="S7-central-C5-initial-and-transition-matrix-v1",
        resource_units={"productive_effort": "effort", "teaching_effort": "effort",
                        "total_effort": "effort"},
    )
    evaluator.register_profile(profile)

    for policy, result in results.items():
        episodes = []
        for path in paths:
            probability = _path_probability(case, path)
            replay = replay_markov_policy(case, result, path)
            for row in replay:
                key = (row["period"], row["competence_before"], row["demand_state"])
                occupancy[policy][key] += probability
                physical, actions = state_cases[row["demand_state"]]
                problem = case.demand_states[row["demand_state"]]
                evaluated = []
                for action in actions:
                    reward, successor = _step(physical, row["competence_before"],
                                              problem, action)
                    evaluated.append((action, reward, successor))
                maximum = max(reward for _, reward, _ in evaluated)
                tie_count = sum(maximum - reward <= TOL for _, reward, _ in evaluated)
                gains = _gain_summary(row["competence_before"], row["competence_after"])
                state_row = state_rows.setdefault(key, {
                    "period": row["period"], "demand_state": problem.problem_id,
                    "competence_before": row["competence_before"],
                    "admissible_action_count": len(actions),
                    "maximum_immediate_CES": maximum,
                    "primary_tie_action_count": tie_count,
                    "policies": {},
                })
                state_row["policies"][policy] = {
                    "action": _action_record(row["action"]),
                    "immediate_CES": row["reward"],
                    **gains,
                }
            records = adapt_s7_episode(
                case, policy,
                "-".join(case.demand_states[index].problem_id for index in path),
                path, probability, replay,
                information_regime=profile.information_regime,
                decision_objective="cumulative_CES",
                provenance_prefix="results/experiments/hls_s7_anticipatory_selection_audit",
            )
            episodes.append(records)
            branch_records[policy].append({
                "demand_path": [case.demand_states[index].problem_id for index in path],
                "probability": probability,
                "periods": [asdict(record) for record in records],
            })
        evaluated = evaluator.evaluate_weighted_episodes(profile.profile_id, policy, episodes)
        pef_metrics[policy] = {key: asdict(value) for key, value in evaluated.items()}

    return profile, occupancy, state_rows, branch_records, pef_metrics


def _q_value(case, bellman_values, state, action):
    time, competence, demand_state = state
    physical, _ = _state_cases(case, transfer_available=False, efficacy=None)[demand_state]
    immediate, successor = _step(physical, competence,
                                 case.demand_states[demand_state], action)
    continuation = 0.0
    if time + 1 < case.horizon:
        continuation = sum(
            probability * bellman_values[(time + 1, successor, next_state)]
            for next_state, probability in enumerate(
                case.transition_probabilities[demand_state])
        )
    return immediate, continuation, immediate + continuation, successor


def _first_common_divergences(case, left, right, bellman_values, paths, left_id, right_id):
    grouped = {}
    for path in paths:
        probability = _path_probability(case, path)
        competence_left = competence_right = case.physical_case.organization.competence_initial
        for time, demand_state in enumerate(path):
            state_left = (time, competence_left, demand_state)
            state_right = (time, competence_right, demand_state)
            if state_left != state_right:
                break
            action_left = left.actions_by_state[state_left]
            action_right = right.actions_by_state[state_right]
            if action_left != action_right:
                key = (state_left, action_left, action_right)
                grouped[key] = grouped.get(key, 0.0) + probability
                break
            physical, _ = _state_cases(case, transfer_available=False, efficacy=None)[demand_state]
            _, competence_left = _step(physical, competence_left,
                                       case.demand_states[demand_state], action_left)
            _, competence_right = _step(physical, competence_right,
                                        case.demand_states[demand_state], action_right)
    rows = []
    for (state, action_left, action_right), probability in sorted(
            grouped.items(), key=lambda item: (item[0][0][0], item[0][0][2], item[0][0][1])):
        time, competence, demand_state = state
        physical, actions = _state_cases(case, transfer_available=False, efficacy=None)[demand_state]
        problem = case.demand_states[demand_state]
        evaluated = []
        for action in actions:
            immediate, successor = _step(physical, competence, problem, action)
            evaluated.append((action, immediate, successor))
        left_immediate, left_cont, left_q, left_successor = _q_value(
            case, bellman_values=bellman_values, state=state, action=action_left)
        right_immediate, right_cont, right_q, right_successor = _q_value(
            case, bellman_values=bellman_values, state=state, action=action_right)
        left_gain = _gain_summary(competence, left_successor)
        right_gain = _gain_summary(competence, right_successor)
        learning_matrix_equal = all(
            abs(left_gain["delta_competence_matrix"][i][k]
                - right_gain["delta_competence_matrix"][i][k]) <= TOL
            for i in range(len(competence)) for k in range(len(competence[i])))
        demanded_skills = tuple(k for k, req in enumerate(problem.requirements) if req > 0)
        categories = []
        if abs(left_immediate - right_immediate) <= TOL:
            left_total = left_gain["net_delta_total"]
            right_total = right_gain["net_delta_total"]
            learning_matrix_equal = all(
                abs(left_gain["delta_competence_matrix"][i][k]
                    - right_gain["delta_competence_matrix"][i][k]) <= TOL
                for i in range(len(competence)) for k in range(len(competence[i])))
            if abs(left_total - right_total) > TOL:
                categories.append("TYPE_I_same_immediate_CES_different_total_learning")
            if (abs(left_total - right_total) <= TOL
                    and not learning_matrix_equal):
                categories.append("TYPE_II_same_total_learning_different_distribution")
            if learning_matrix_equal and action_left != action_right:
                categories.append("TYPE_III_equivalent_learning_other_physical_effect")
        else:
            categories.append("TYPE_IV_strict_immediate_CES_sacrifice_by_left_policy")
        rows.append({
            "period": time, "demand": problem.problem_id,
            "competence_state": competence,
            "first_divergence_probability_mass": probability,
            "actions": {left_id: _action_record(action_left),
                        right_id: _action_record(action_right)},
            "immediate_CES": {left_id: left_immediate, right_id: right_immediate},
            "CES_difference_left_minus_right": left_immediate - right_immediate,
            "primary_tie": abs(left_immediate - right_immediate) <= TOL,
            "learning": {left_id: left_gain, right_id: right_gain},
            "learning_total_net_difference_left_minus_right": (
                left_gain["net_delta_total"] - right_gain["net_delta_total"]),
            "learning_distribution_differs": not learning_matrix_equal,
            "increment_difference_left_minus_right": _delta(right_successor, left_successor),
            "successor_competence": {left_id: left_successor, right_id: right_successor},
            "production_output_by_task": {
                left_id: productive_outputs_nk(competence, action_left.production),
                right_id: productive_outputs_nk(competence, action_right.production),
            },
            "productive_effort_by_agent": {
                left_id: tuple(sum(row) for row in action_left.production),
                right_id: tuple(sum(row) for row in action_right.production),
            },
            "resource_use": {
                left_id: sum(sum(agent) for agent in action_left.production),
                right_id: sum(sum(agent) for agent in action_right.production),
            },
            "future_demand_distribution": case.transition_probabilities[demand_state],
            "demanded_skill_indices_from_current_requirements": demanded_skills,
            "Q_B": {
                left_id: {"immediate": left_immediate, "continuation": left_cont, "total": left_q},
                right_id: {"immediate": right_immediate, "continuation": right_cont, "total": right_q},
                "Q_difference_left_minus_right": left_q - right_q,
                "continuation_difference_left_minus_right": left_cont - right_cont,
            },
            "classification": categories,
        })
    return rows


def _performance_difference(case, result_bellman, comparison, occupancy):
    values = result_bellman.value_by_state
    terms = []
    for state, mass in occupancy.items():
        action = comparison.actions_by_state[state]
        immediate, continuation, q_value, _ = _q_value(case, values, state, action)
        advantage = values[state] - q_value
        terms.append({
            "state": state, "occupancy_probability": mass,
            "V_B": values[state], "Q_B_selected_policy_action": q_value,
            "immediate_CES": immediate, "continuation_under_Bellman": continuation,
            "Bellman_advantage": advantage, "weighted_advantage": mass * advantage,
        })
    total = sum(row["weighted_advantage"] for row in terms)
    return {
        "identity": "J_Bellman - J_policy = E_policy[sum_t(V_B(s_t)-Q_B(s_t,a_t))]",
        "J_Bellman_minus_policy": result_bellman.value - comparison.value,
        "occupancy_weighted_advantage_sum": total,
        "residual": result_bellman.value - comparison.value - total,
        "max_abs_term_advantage": max((abs(row["Bellman_advantage"]) for row in terms), default=0.0),
        "state_terms": terms,
    }


def run() -> dict:
    case = make_characterization_case("opportunity")
    if case.horizon != 4:
        raise AssertionError("audit must use central S7 T=4")
    all_paths = tuple(product(range(len(case.demand_states)), repeat=case.horizon))
    paths = tuple(path for path in all_paths if _path_probability(case, path) > 0.0)
    path_probabilities = tuple(_path_probability(case, path) for path in paths)
    if not isclose(sum(path_probabilities), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError("C5 branch probabilities must sum to one")

    # Preserve the historical pruned Bellman policy/value; the unpruned solve
    # only supplies V_B on every state reachable under alternative actions.
    bellman = solve_markov_bellman(case, transfer_available=False)
    bellman_full = solve_markov_bellman(case, transfer_available=False,
                                        prune_dominated=False)
    policies: dict[str, S7ExactResult] = {
        "A": bellman,
        "MA": solve_reactive_greedy(case, transfer_available=False),
        "BMA": solve_best_myopic(case, transfer_available=False),
        "CDM": solve_current_demand_myopic(case, transfer_available=False),
    }
    if abs(bellman.value - bellman_full.value) > 1e-10:
        raise AssertionError("unpruned Bellman value differs from historical exact Bellman")
    # Use the unpruned value table for all counterfactual states, keeping A's
    # actual selected actions identical to the historical solver.
    policies["A"] = S7ExactResult(
        bellman.value, bellman.visited_states, False, bellman.actions_by_state,
        bellman.dominated_actions_pruned, bellman_full.value_by_state,
    )

    # Aggregate exact state occupancy and evaluate all four policies with PEF.
    profile, occupancy, state_rows, branch_records, policy_metrics = _occupancy_and_records(
        case, policies, paths,
    )
    for policy in policies:
        for period in range(case.horizon):
            mass = sum(value for (t, _, _), value in occupancy[policy].items() if t == period)
            if abs(mass - 1.0) > 1e-10:
                raise AssertionError(f"state occupancy for {policy}, t={period} sums to {mass}")

    # Restore raw solver results in case records are consumed by any later code.
    values = {key: policy_metrics[key]["ces_cumulative"]["value"] for key in POLICIES}
    historical = {"A": 3.1628653621, "MA": 3.0346209871, "BMA": 3.0444737839}
    if any(abs(values[key] - expected) > 1e-10 for key, expected in historical.items()):
        raise AssertionError(f"historical values did not reproduce: {values}")
    if abs(policies["CDM"].value - values["CDM"]) > 1e-10:
        raise AssertionError("CDM PEF CES differs from its exact policy value")

    divergences = {
        "A_vs_BMA": _first_common_divergences(case, policies["A"], policies["BMA"],
                                                policies["A"].value_by_state,
                                                paths, "A_Bellman", "BMA_BEST_MYOPIC"),
        "A_vs_CDM": _first_common_divergences(case, policies["A"], policies["CDM"],
                                               policies["A"].value_by_state,
                                               paths, "A_Bellman", "CDM"),
        "BMA_vs_CDM": _first_common_divergences(case, policies["BMA"], policies["CDM"],
                                                 policies["A"].value_by_state,
                                                 paths, "BMA_BEST_MYOPIC", "CDM"),
    }
    for rows in divergences.values():
        for row in rows:
            q = row["Q_B"]
            expected_q_diff = (row["CES_difference_left_minus_right"]
                               + q["continuation_difference_left_minus_right"])
            if abs(expected_q_diff - q["Q_difference_left_minus_right"]) > 1e-10:
                raise AssertionError("Q difference does not decompose into immediate and continuation values")
    performance_identity = {
        policy: _performance_difference(case, policies["A"], policies[policy], occupancy[policy])
        for policy in ("MA", "BMA", "CDM")
    }
    if any(abs(row["residual"]) > 1e-9 for row in performance_identity.values()):
        raise AssertionError("Bellman performance-difference identity failed")

    # Add Q diagnostics at every state common to Bellman and BEST-MYOPIC.
    q_on_common_states = []
    for state in sorted(set(occupancy["A"]) & set(occupancy["BMA"])):
        action_a = policies["A"].actions_by_state[state]
        action_b = policies["BMA"].actions_by_state[state]
        if action_a == action_b:
            continue
        a_immediate, a_continuation, a_q, a_successor = _q_value(
            case, policies["A"].value_by_state, state, action_a)
        b_immediate, b_continuation, b_q, b_successor = _q_value(
            case, policies["A"].value_by_state, state, action_b)
        q_on_common_states.append({
            "state": state,
            "occupancy_A": occupancy["A"][state],
            "occupancy_BMA": occupancy["BMA"][state],
            "actions_differ": True,
            "actions": {"A": _action_record(action_a), "BMA": _action_record(action_b)},
            "immediate_CES": {"A": a_immediate, "BMA": b_immediate},
            "increment_matrices": {"A": _gain_summary(state[1], a_successor),
                                   "BMA": _gain_summary(state[1], b_successor)},
            "Q_B": {"A": {"immediate": a_immediate, "continuation": a_continuation,
                           "total": a_q},
                   "BMA": {"immediate": b_immediate, "continuation": b_continuation,
                           "total": b_q},
                   "Q_difference_A_minus_BMA": a_q - b_q,
                   "continuation_difference_A_minus_BMA": a_continuation - b_continuation},
        })
        if abs(a_q - policies["A"].value_by_state[state]) > 1e-10:
            raise AssertionError("Bellman selected-action Q differs from V_B at a reachable state")

    for state, row in state_rows.items():
        row["primary_tie_by_policy"] = {
            policy: abs(row["maximum_immediate_CES"] - details["immediate_CES"]) <= TOL
            for policy, details in row["policies"].items()
        }
        row["action_coincidence"] = {
            f"{left}_equals_{right}": row["policies"][left]["action"]
            == row["policies"][right]["action"]
            for left, right in (("A", "MA"), ("A", "BMA"), ("A", "CDM"),
                                ("BMA", "CDM"))
            if left in row["policies"] and right in row["policies"]
        }
        for policy in ("MA", "BMA", "CDM"):
            if policy in row["policies"] and (
                    row["maximum_immediate_CES"]
                    - row["policies"][policy]["immediate_CES"] > TOL):
                raise AssertionError(f"reactive policy {policy} selected non-maximal current CES at {state}")

    period_summary = []
    for policy in POLICIES:
        for period in range(case.horizon):
            mass = sum(row["probability"] for row in branch_records[policy]
                       for record in row["periods"] if record["period"] == period)
            # Period means are computed from episode records with branch weights.
            records = [(branch["probability"], branch["periods"][period])
                       for branch in branch_records[policy]]
            mean_comp_after = []
            n_agents = len(records[0][1]["competence_state"]["after"])
            n_tasks = len(records[0][1]["competence_state"]["after"][0])
            mean_comp_after = [[0.0] * n_tasks for _ in range(n_agents)]
            mean_delta = [[0.0] * n_tasks for _ in range(n_agents)]
            reward = production = 0.0
            for weight, record in records:
                reward += weight * record["ces"]
                production += weight * sum(record["output"])
                before = record["competence_state"]["before"]
                after = record["competence_state"]["after"]
                for i in range(n_agents):
                    for k in range(n_tasks):
                        mean_comp_after[i][k] += weight * after[i][k]
                        mean_delta[i][k] += weight * (after[i][k] - before[i][k])
            period_summary.append({"policy": policy, "period": period,
                                   "state_probability_sum": sum(
                                       value for (t, _, _), value in occupancy[policy].items()
                                       if t == period),
                                   "expected_CES": reward, "expected_production": production,
                                   "expected_delta_competence_matrix": mean_delta,
                                   "expected_competence_after": mean_comp_after})

    result = {
        "experiment": "S7 anticipatory selection audit: Bellman vs myopic tie-breaks, no transfer",
        "design": {
            "scenario": "central S7 opportunity, T=4, C5 Markov demand",
            "initial_competence": case.physical_case.organization.competence_initial,
            "initial_competence": case.physical_case.organization.competence_initial,
            "demand_states": [problem.problem_id for problem in case.demand_states],
            "initial_probabilities": case.initial_probabilities,
            "transition_probabilities": case.transition_probabilities,
            "full_path_combinations": len(all_paths),
            "positive_probability_reachable_branches": len(paths),
            "branch_probability_sum": sum(path_probabilities),
            "transfer": False,
            "CDM_rule": "maximize immediate CES; within absolute tolerance 1e-12, maximize positive competence increments only for skill coordinates with positive requirements in current observed demand; remaining ties canonical action key",
            "future_demand_information": "used by Bellman optimization only; unavailable to MA, BMA, and CDM selectors",
            "BMA_rule": "maximize immediate CES; ties maximize total positive immediate competence increment; canonical action key for remaining ties",
        },
        "profile": asdict(profile),
        "policies": policy_metrics,
        "pairwise_CES_differences": {
            "A_minus_BMA": values["A"] - values["BMA"],
            "A_minus_CDM": values["A"] - values["CDM"],
            "BMA_minus_CDM": values["BMA"] - values["CDM"],
        },
        "state_occupancy_and_decisions": [
            {**row, "state": state,
             "occupancy_probability_by_policy": {
                 policy: occupancy[policy].get(state, 0.0) for policy in POLICIES},
             "reachable_under_policies": [policy for policy in POLICIES
                                          if occupancy[policy].get(state, 0.0) > 0.0]}
            for state, row in sorted(state_rows.items(),
                                     key=lambda item: (item[0][0], item[0][2], item[0][1]))
        ],
        "first_divergences_on_shared_trajectories": divergences,
        "Q_B_on_common_reachable_divergent_states": q_on_common_states,
        "bellman_performance_difference_identity": performance_identity,
        "expected_period_summary": period_summary,
        "branch_records": branch_records,
        "validation": {
            "historical_A_MA_BMA_reproduced": True,
            "branch_probabilities_sum_to_one": abs(sum(path_probabilities) - 1.0) <= 1e-12,
            "occupancy_sums_to_one_each_period": True,
            "bellman_unpruned_value_matches_historical": abs(bellman.value - bellman_full.value) <= 1e-10,
            "reactive_policies_maximize_immediate_CES": True,
            "Q_immediate_plus_continuation_consistent": True,
            "Bellman_selected_Q_equals_V_on_shared_divergences": True,
            "performance_difference_identity_holds": all(
                abs(row["residual"]) <= 1e-9 for row in performance_identity.values()),
            "PEF_provenance_and_units_present": all(
                metric["status"] == "VALID" and metric["provenance"] and metric["unit"]
                for metrics in policy_metrics.values() for metric in metrics.values()),
        },
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    output = run()
    print(json.dumps({
        "policy_CES": {key: value["ces_cumulative"]["value"]
                       for key, value in output["policies"].items()},
        "differences": output["pairwise_CES_differences"],
        "performance_identity_residuals": {
            key: value["residual"]
            for key, value in output["bellman_performance_difference_identity"].items()},
    }, indent=2))
