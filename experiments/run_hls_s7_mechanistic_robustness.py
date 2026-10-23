"""Mechanistic decomposition and local robustness check for S7.

This is a finite exact evaluation of the existing T=4 S7 instance and a small
one-factor-at-a-time neighborhood. It does not alter S4 physical laws or add
decision policies.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from experiments.run_hls_s7_preparation_characterization import (
    make_characterization_case,
)
from hls.hls_lab_nk_production import evaluate_problem_nk, productive_outputs_nk
from hls.hls_lab_nk_teaching import TeachingEfficacyNK
from hls.synthetic.hls_s4_transfer_exact import _step
from hls.synthetic.hls_s7_uncertain_demand import (
    S7ExactResult,
    S7MarkovDemandCase,
    independent_tree_enumeration,
    solve_markov_bellman,
    solve_reactive_greedy,
)

RESULT = Path("results/experiments/hls_s7_mechanistic_robustness/results.json")
TOL = 1e-10
POLICIES = (
    ("J_A_bellman_no_transfer", True, False),
    ("J_B_bellman_transfer_optional", True, True),
    ("J_MA_reactive_no_transfer", False, False),
    ("J_MB_reactive_transfer_optional", False, True),
)


def _set_transition(case: S7MarkovDemandCase, *, p_xy: float | None = None,
                    p_yy: float | None = None) -> S7MarkovDemandCase:
    matrix = [list(row) for row in case.transition_probabilities]
    if p_xy is not None:
        matrix[0] = [1.0 - p_xy, p_xy]
    if p_yy is not None:
        matrix[1] = [1.0 - p_yy, p_yy]
    return replace(case, transition_probabilities=tuple(tuple(row) for row in matrix))


def sensitivity_configurations() -> tuple[tuple[str, S7MarkovDemandCase, dict], ...]:
    """Return a frozen center and eight symmetric, one-factor perturbations."""
    center = make_characterization_case("opportunity")
    rows: list[tuple[str, S7MarkovDemandCase, dict]] = [("center", center, {"changed_factor": None})]
    for value in (0.85, 0.95):
        rows.append((f"p_xy_{value:.3f}", _set_transition(center, p_xy=value),
                     {"changed_factor": "P(y|x)", "value": value,
                      "justification": "center ±0.05, symmetric and interior to [0,1]"}))
    for value in (0.925, 0.975):
        rows.append((f"p_yy_{value:.3f}", _set_transition(center, p_yy=value),
                     {"changed_factor": "P(y|y)", "value": value,
                      "justification": "center ±0.025, symmetric and interior to [0,1]"}))
    for value in (0.04, 0.06):
        eta = [list(row) for row in center.physical_case.profile.eta]
        eta[1][1] = value
        profile = replace(center.physical_case.profile,
                          eta=tuple(tuple(row) for row in eta))
        physical = replace(center.physical_case, profile=profile)
        rows.append((f"eta_B_y_{value:.3f}", replace(center, physical_case=physical),
                     {"changed_factor": "MIS-v2 eta(B,y)", "value": value,
                      "justification": "center 0.05 ±0.01; only the future bottleneck cell changes"}))
    for value in (0.7, 0.9):
        values = [[list(skill_row) for skill_row in row]
                  for row in center.physical_case.efficacy.values]
        values[0][1][1] = value
        efficacy = replace(center.physical_case.efficacy,
                           values=tuple(tuple(tuple(v) for v in row) for row in values))
        physical = replace(center.physical_case, efficacy=efficacy)
        rows.append((f"efficacy_A_B_y_{value:.3f}", replace(center, physical_case=physical),
                     {"changed_factor": "transfer efficacy A→B/y", "value": value,
                      "justification": "center 0.8 ±0.1; bounded to [0,1]"}))
    return tuple(rows)


def _action_dict(action) -> dict:
    return {
        "production": action.production,
        "teaching": None if action.teaching is None else asdict(action.teaching),
    }


def expected_policy_metrics(case: S7MarkovDemandCase, result: S7ExactResult) -> dict:
    """Exactly average existing CES/functionality/resource diagnostics over C5."""
    @lru_cache(maxsize=None)
    def metrics(time: int, competence: tuple[tuple[float, ...], ...], demand: int) -> tuple[float, ...]:
        if time == case.horizon:
            return (0.0,) * 11
        action = result.actions_by_state[(time, competence, demand)]
        problem = case.demand_states[demand]
        reward, next_competence = _step(case.physical_case, competence, problem, action)
        outputs = productive_outputs_nk(competence, action.production)
        service = evaluate_problem_nk(outputs, problem.requirements)
        raw_deficits = tuple(service.deficits)
        production_effort = sum(sum(row) for row in action.production)
        teaching_cost = 0.0 if action.teaching is None else 2.0 * action.teaching.effort
        current = (
            reward,
            float(service.success),
            float(not service.success),
            service.normalized_deficit,
            sum(raw_deficits),
            production_effort,
            teaching_cost,
            float(action.teaching is not None),
            production_effort + teaching_cost,
            *raw_deficits,
        )
        future = [0.0] * len(current)
        if time + 1 < case.horizon:
            for next_demand, probability in enumerate(case.transition_probabilities[demand]):
                if probability == 0.0:
                    continue
                downstream = metrics(time + 1, next_competence, next_demand)
                for index, value in enumerate(downstream):
                    future[index] += probability * value
        # The two fixed demand states have two raw deficit fields (x and y).
        return tuple(current[index] + future[index] for index in range(len(current)))

    initial = case.physical_case.organization.competence_initial
    expected = [0.0] * 11
    for demand, probability in enumerate(case.initial_probabilities):
        if probability == 0.0:
            continue
        row = metrics(0, initial, demand)
        for index, value in enumerate(row):
            expected[index] += probability * value
    ces, completed, failures, normalized, raw_total, productive, teaching_cost, lessons, total, deficit_x, deficit_y = expected
    if abs(ces - result.value) > TOL:
        raise AssertionError(f"metric replay CES {ces} differs from solver value {result.value}")
    return {
        "expected_cumulative_CES": ces,
        "expected_services_completed": completed,
        "expected_functional_failures": failures,
        "expected_cumulative_normalized_deficit": normalized,
        "expected_cumulative_raw_deficit_total": raw_total,
        "expected_cumulative_raw_deficit_by_skill": {"x": deficit_x, "y": deficit_y},
        "expected_productive_effort": productive,
        "expected_teaching_resource_consumption": teaching_cost,
        "expected_teaching_actions": lessons,
        "expected_total_resource_consumption": total,
    }


def _trace_demand_path(case: S7MarkovDemandCase, result: S7ExactResult,
                       demand_path: tuple[int, ...]) -> dict:
    """Replay one named demand branch to expose action/transition mechanisms."""
    if len(demand_path) != case.horizon:
        raise ValueError("demand path length must match the horizon")
    initial_probability = case.initial_probabilities[demand_path[0]]
    path_probability = initial_probability
    competence = case.physical_case.organization.competence_initial
    rows = []
    for time, demand_id in enumerate(demand_path):
        if time:
            path_probability *= case.transition_probabilities[demand_path[time - 1]][demand_id]
        problem = case.demand_states[demand_id]
        action = result.actions_by_state[(time, competence, demand_id)]
        reward, next_competence = _step(case.physical_case, competence, problem, action)
        outputs = productive_outputs_nk(competence, action.production)
        service = evaluate_problem_nk(outputs, problem.requirements)
        rows.append({
            "period": time,
            "demand_state": problem.problem_id,
            "competence_before": competence,
            "action": _action_dict(action),
            "immediate_CES": reward,
            "functional_success": service.success,
            "normalized_deficit": service.normalized_deficit,
            "raw_deficits": service.deficits,
            "competence_after": next_competence,
            "production_effort": sum(sum(row) for row in action.production),
            "teaching_resource_consumption": (
                0.0 if action.teaching is None else 2.0 * action.teaching.effort
            ),
        })
        competence = next_competence
    return {"demand_path": [case.demand_states[index].problem_id for index in demand_path],
            "path_probability": path_probability, "periods": rows}


def _solve_configuration(name: str, case: S7MarkovDemandCase, design: dict) -> dict:
    started = perf_counter()
    policy_results = {}
    for policy_name, bellman, transfer in POLICIES:
        result = (solve_markov_bellman(case, transfer_available=transfer)
                  if bellman else solve_reactive_greedy(case, transfer_available=transfer))
        policy_results[policy_name] = result
    duration = perf_counter() - started
    values = {name: result.value for name, result in policy_results.items()}
    ja = values["J_A_bellman_no_transfer"]
    jb = values["J_B_bellman_transfer_optional"]
    jma = values["J_MA_reactive_no_transfer"]
    jmb = values["J_MB_reactive_transfer_optional"]
    contrasts = {
        "planning_without_transfer_JA_minus_JMA": ja - jma,
        "planning_with_transfer_JB_minus_JMB": jb - jmb,
        "transfer_with_planning_JB_minus_JA": jb - ja,
        "transfer_without_planning_JMB_minus_JMA": jmb - jma,
        "interaction_I": (jb - ja) - (jmb - jma),
        "interaction_identity_check": (jb - jmb) - (ja - jma),
    }
    if contrasts["interaction_I"] < -TOL:
        raise AssertionError("optional transfer cannot lower exact Bellman value")
    metrics = {key: expected_policy_metrics(case, result)
               for key, result in policy_results.items()}
    initial = case.physical_case.organization.competence_initial
    initial_actions = {
        key: _action_dict(result.actions_by_state[(0, initial, 0)])
        for key, result in policy_results.items()
    }
    output = {
        "design": design,
        "exact_values": values,
        "decomposition": contrasts,
        "expected_functional_and_resource_metrics": metrics,
        "initial_decisions": initial_actions,
        "solver_diagnostics": {
            "states_visited_by_policy": {key: result.visited_states
                                          for key, result in policy_results.items()},
            "dominated_actions_pruned": {key: result.dominated_actions_pruned
                                         for key, result in policy_results.items()},
            "runtime_seconds_descriptive": duration,
        },
    }
    if name == "center":
        # Representative branches are fixed ex ante: persistent preparation
        # opportunity (x→y→y→y), delayed transition, and no transition.
        branch_paths = ((0, 1, 1, 1), (0, 0, 1, 1), (0, 0, 0, 0))
        output["mechanistic_demand_branches"] = {
            policy_name: {
                "x_y_y_y": _trace_demand_path(case, policy_results[policy_name], branch_paths[0]),
                "x_x_y_y": _trace_demand_path(case, policy_results[policy_name], branch_paths[1]),
                "x_x_x_x": _trace_demand_path(case, policy_results[policy_name], branch_paths[2]),
            }
            for policy_name, _, _ in POLICIES
        }
    output["policy_results"] = policy_results
    return output


def run() -> dict:
    sensitivity_rows = sensitivity_configurations()
    sensitivity = {}
    print("Fixed S7 local design:", flush=True)
    for name, case, design in sensitivity_rows:
        print(f"  solving {name}", flush=True)
        policy_rows = _solve_configuration(name, case, design)
        sensitivity[name] = {key: value for key, value in policy_rows.items()
                             if key != "policy_results"}
    print("Solving negative controls", flush=True)
    short_case = make_characterization_case("short_horizon")
    no_need_case = make_characterization_case("no_future_need")
    short = _solve_configuration("short_horizon_control", short_case,
                                 {"horizon": short_case.horizon,
                                  "transition": short_case.transition_probabilities,
                                  "purpose": "physically feasible preparation, shorter recovery horizon"})
    no_need = _solve_configuration("no_future_need_control", no_need_case,
                                   {"horizon": no_need_case.horizon,
                                    "transition": no_need_case.transition_probabilities,
                                    "purpose": "x absorbing; no future y requirement state is reached"})

    # Independent action construction / tree enumeration at the viable T=2 slice.
    validation_case = replace(make_characterization_case("opportunity"), horizon=2)
    independent_checks = {}
    for enabled in (False, True):
        exact = solve_markov_bellman(validation_case, transfer_available=enabled)
        exhaustive = independent_tree_enumeration(
            validation_case, transfer_available=enabled,
        )
        if abs(exact.value - exhaustive) > TOL:
            raise AssertionError("S7 robustness validation differs from independent tree enumeration")
        independent_checks[str(enabled)] = {
            "bellman": exact.value,
            "independent_tree_enumeration": exhaustive,
            "absolute_difference": abs(exact.value - exhaustive),
        }

    serial_sensitivity = {}
    for name, row in sensitivity.items():
        serial_sensitivity[name] = row
    result = {
        "experiment": "S7 mechanistic decomposition and local robustness",
        "date": "2026-10-22",
        "comparison_information": {
            "all_policies_observe": "current demand state, exact current competence state, the same physical transition laws, reward and complete feasible actions",
            "demand_law": "same initial distribution and Markov transition matrix in each paired policy comparison; Bellman uses the known matrix in continuation, reactive policy is defined to maximize only current CES and does not use future transition probabilities",
            "transfer_access": "Bellman and reactive variants with transfer have the same optional-teaching action catalog; without-transfer variants share the same MIS-only catalog",
            "objective": "cumulative existing CES; functional completion and resource metrics are diagnostics, not alternate objectives",
            "future_realization": "not revealed to the action selector; only current demand is observed",
            "information_fairness": "same state and model information is available to both policy classes; their use of future-demand probabilities differs by the intended planning mechanism. Both exact references know the true competence state, so these are oracle comparisons, not deployable hidden-competence policies.",
        },
        "sensitivity_protocol": {
            "method": "center plus symmetric one-factor-at-a-time perturbations; all other settings held fixed",
            "fixed_horizon": 4,
            "center": {"p_xy": 0.90, "p_yy": 0.95, "eta_B_y": 0.05, "efficacy_A_B_y": 0.80},
            "predeclared_perturbations": {
                "p_xy": [0.85, 0.95],
                "p_yy": [0.925, 0.975],
                "eta_B_y": [0.04, 0.06],
                "efficacy_A_B_y": [0.70, 0.90],
            },
            "justification": "Moderate symmetric local changes, interior to valid domains; eta perturbation is restricted to the bottleneck learner-skill cell; efficacy is restricted to the teaching relation used by the candidate action. No parameter chosen by maximizing policy differences.",
        },
        "sensitivity": serial_sensitivity,
        "negative_controls": {
            "short_horizon": {key: value for key, value in short.items()
                               if key != "policy_results"},
            "no_future_y_need": {key: value for key, value in no_need.items()
                                 if key != "policy_results"},
        },
        "independent_tree_validation_T2": independent_checks,
        "interpretation_scope": "Exact finite-case policy comparison and local robustness; it does not establish a general theorem, statistical robustness, or a deployable policy under hidden competence.",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    output = run()
    center = output["sensitivity"]["center"]
    print(json.dumps({
        "center_values": center["exact_values"],
        "center_decomposition": center["decomposition"],
        "sensitivity_values": {name: row["exact_values"]
                               for name, row in output["sensitivity"].items()},
        "controls": {
            name: row["exact_values"]
            for name, row in output["negative_controls"].items()
        },
    }, indent=2))
