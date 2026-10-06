"""Reproducibly run the exhaustive DISCOVER-v0 fixed-repertoire diagnostic."""

from __future__ import annotations

import csv
import hashlib
import json
from math import isclose
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.discover_v0 import (  # noqa: E402
    DEFAULT_HORIZON,
    DEFAULT_PRIOR,
    DEFAULT_QUADRATURE_ORDER,
    DEFAULT_SIGMA,
    RHO,
    THETA_1,
    THETA_2,
    capability_dual,
    enumerate_canonical_states,
    evaluate_state,
    labelled_state_count,
    means,
    production_inputs,
    state_budget,
    unknown_policy_value,
)
from hls.discover_v0_geometry import action_information_geometry, pareto_frontier  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "discover_v0"
MODULE = ROOT / "src" / "hls" / "discover_v0.py"
RUNNER = Path(__file__).resolve()
CONVERGENCE_ORDERS = (15, 23, 31)
CONVERGENCE_STATE_INDICES = (0, 15, 30)
LOW_NOISE_QUADRATURE_ORDER = 11


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _action_text(action: tuple[tuple[float, float], ...]) -> str:
    return ";".join(f"({left:g},{right:g})" for left, right in action)


def _state_text(state: tuple[tuple[float, float], ...]) -> str:
    return ";".join(f"({left:g},{right:g})" for left, right in state)


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _configuration_rows(evaluations):
    rows = []
    for index, evaluation in enumerate(evaluations):
        rows.append(
            {
                "configuration_id": f"S{index:03d}",
                "state": _state_text(evaluation.state),
                "s11": evaluation.state[0][0],
                "s12": evaluation.state[0][1],
                "s21": evaluation.state[1][0],
                "s22": evaluation.state[1][1],
                "s31": evaluation.state[2][0],
                "s32": evaluation.state[2][1],
                "budget": state_budget(evaluation.state),
                "V_K": evaluation.known_value,
                "V_U": evaluation.unknown_value,
                "C_D": evaluation.discovery_cost,
                "known_theta1_actions": "|".join(_action_text(action) for action in evaluation.known_theta_1.first_actions),
                "known_theta2_actions": "|".join(_action_text(action) for action in evaluation.known_theta_2.first_actions),
                "unknown_initial_actions": "|".join(_action_text(action) for action in evaluation.unknown.first_actions),
            }
        )
    return rows


def _action_rows(evaluations):
    rows = []
    for state_index, evaluation in enumerate(evaluations):
        unknown_values = dict(evaluation.unknown.first_action_values)
        known_1_values = dict(evaluation.known_theta_1.first_action_values)
        known_2_values = dict(evaluation.known_theta_2.first_action_values)
        for action in sorted(unknown_values, key=_action_text):
            outputs = production_inputs(evaluation.state, action)
            mu_1, mu_2 = means(evaluation.state, action)
            rows.append(
                {
                    "configuration_id": f"S{state_index:03d}",
                    "action": _action_text(action),
                    "Y1": outputs[0],
                    "Y2": outputs[1],
                    "mu_theta1": mu_1,
                    "mu_theta2": mu_2,
                    "known_theta1_action_value": known_1_values[action],
                    "known_theta2_action_value": known_2_values[action],
                    "unknown_initial_action_value": unknown_values[action],
                    "known_theta1_optimal": action in evaluation.known_theta_1.first_actions,
                    "known_theta2_optimal": action in evaluation.known_theta_2.first_actions,
                    "unknown_initial_optimal": action in evaluation.unknown.first_actions,
                }
            )
    return rows


def _pair_rows(evaluations):
    rows = []
    for left_index, left in enumerate(evaluations):
        for right_index in range(left_index + 1, len(evaluations)):
            right = evaluations[right_index]
            rows.append(
                {
                    "configuration_a": f"S{left_index:03d}",
                    "configuration_b": f"S{right_index:03d}",
                    "Delta_VK": abs(left.known_value - right.known_value),
                    "Delta_CD": abs(left.discovery_cost - right.discovery_cost),
                    "V_K_a": left.known_value,
                    "V_K_b": right.known_value,
                    "C_D_a": left.discovery_cost,
                    "C_D_b": right.discovery_cost,
                }
            )
    return rows


def _geometry_action_rows(evaluations, geometries):
    rows = []
    for state_index, (evaluation, geometry) in enumerate(zip(evaluations, geometries)):
        for item in geometry:
            rows.append(
                {
                    "configuration_id": f"S{state_index:03d}",
                    "action": _action_text(item.action),
                    "mu_theta1": item.mu_theta1,
                    "mu_theta2": item.mu_theta2,
                    "reward_prior": item.reward_prior,
                    "d": item.discriminability,
                    "KL": item.kl,
                    "production_gap": item.production_gap,
                    "pareto_production_information": item.pareto_optimal,
                    "production_retention_of_max": item.production_retention,
                    "discriminability_retention_of_max": item.discriminability_retention,
                    "immediate_production_optimal": item.production_gap <= 1e-10,
                    "unknown_initial_optimal": item.action in evaluation.unknown.first_actions,
                    "known_theta1_initial_optimal": item.action in evaluation.known_theta_1.first_actions,
                    "known_theta2_initial_optimal": item.action in evaluation.known_theta_2.first_actions,
                    "uninformative": isclose(item.mu_theta1, item.mu_theta2, abs_tol=1e-10),
                }
            )
    return rows


def _join_numbers(items):
    return "|".join(f"{item:.12g}" for item in items)


def _geometry_configuration_rows(evaluations, geometries):
    rows = []
    for state_index, (evaluation, geometry) in enumerate(zip(evaluations, geometries)):
        frontier = pareto_frontier(geometry)
        max_d = max(item.discriminability for item in geometry)
        production_best = tuple(item for item in geometry if item.production_gap <= 1e-10)
        max_d_actions = tuple(item for item in geometry if max_d - item.discriminability <= 1e-10)
        unknown_actions = tuple(item for item in geometry if item.action in evaluation.unknown.first_actions)
        rows.append(
            {
                "configuration_id": f"S{state_index:03d}",
                "state": _state_text(evaluation.state),
                "V_K": evaluation.known_value,
                "V_U": evaluation.unknown_value,
                "C_D": evaluation.discovery_cost,
                "max_d": max_d,
                "max_KL": max(item.kl for item in geometry),
                "pareto_action_count": len(frontier),
                "pareto_unique_point_count": len({(item.reward_prior, item.discriminability) for item in frontier}),
                "pareto_production_gaps": _join_numbers(tuple(item.production_gap for item in frontier)),
                "immediate_production_actions": "|".join(_action_text(item.action) for item in production_best),
                "d_at_immediate_production": _join_numbers(tuple(item.discriminability for item in production_best)),
                "KL_at_immediate_production": _join_numbers(tuple(item.kl for item in production_best)),
                "max_d_actions": "|".join(_action_text(item.action) for item in max_d_actions),
                "production_gap_at_max_d": _join_numbers(tuple(item.production_gap for item in max_d_actions)),
                "unknown_initial_actions": "|".join(_action_text(item.action) for item in unknown_actions),
                "unknown_initial_reward_prior": _join_numbers(tuple(item.reward_prior for item in unknown_actions)),
                "unknown_initial_d": _join_numbers(tuple(item.discriminability for item in unknown_actions)),
                "unknown_initial_KL": _join_numbers(tuple(item.kl for item in unknown_actions)),
                "unknown_initial_production_gap": _join_numbers(tuple(item.production_gap for item in unknown_actions)),
                "known_theta1_initial_actions": "|".join(_action_text(action) for action in evaluation.known_theta_1.first_actions),
                "known_theta2_initial_actions": "|".join(_action_text(action) for action in evaluation.known_theta_2.first_actions),
            }
        )
    return rows


def _pair_diagnostic_rows(config_rows):
    rows = []
    for left_index, left in enumerate(config_rows):
        for right in config_rows[left_index + 1 :]:
            rows.append(
                {
                    "configuration_a": left["configuration_id"],
                    "configuration_b": right["configuration_id"],
                    "Delta_VK": abs(float(left["V_K"]) - float(right["V_K"])),
                    "Delta_CD": abs(float(left["C_D"]) - float(right["C_D"])),
                    "Delta_max_d": abs(float(left["max_d"]) - float(right["max_d"])),
                    "Delta_d_at_immediate_production": abs(float(left["d_at_immediate_production"].split("|")[0]) - float(right["d_at_immediate_production"].split("|")[0])),
                    "Delta_pareto_unique_point_count": abs(int(left["pareto_unique_point_count"]) - int(right["pareto_unique_point_count"])),
                    "V_K_a": left["V_K"],
                    "V_K_b": right["V_K"],
                    "C_D_a": left["C_D"],
                    "C_D_b": right["C_D"],
                    "max_d_a": left["max_d"],
                    "max_d_b": right["max_d"],
                    "unknown_initial_d_a": left["unknown_initial_d"],
                    "unknown_initial_d_b": right["unknown_initial_d"],
                    "unknown_initial_production_gap_a": left["unknown_initial_production_gap"],
                    "unknown_initial_production_gap_b": right["unknown_initial_production_gap"],
                }
            )
    return rows


def _mean_number(cell: object) -> float:
    values = [float(value) for value in str(cell).split("|")]
    return sum(values) / len(values)


def _average_ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and isclose(ordered[end][1], ordered[start][1], abs_tol=1e-12):
            end += 1
        average = (start + 1 + end) / 2.0
        for index, _ in ordered[start:end]:
            ranks[index] = average
        start = end
    return ranks


def _correlation(left: list[float], right: list[float]) -> float | None:
    if len(set(left)) < 2 or len(set(right)) < 2:
        return None
    return float(np.corrcoef(left, right)[0, 1])


def _geometry_summary(config_rows, pair_rows):
    cost = [float(row["C_D"]) for row in config_rows]
    fields = {
        "max_d": [float(row["max_d"]) for row in config_rows],
        "d_at_immediate_production": [_mean_number(row["d_at_immediate_production"]) for row in config_rows],
        "unknown_initial_d": [_mean_number(row["unknown_initial_d"]) for row in config_rows],
        "unknown_initial_production_gap": [_mean_number(row["unknown_initial_production_gap"]) for row in config_rows],
        "pareto_unique_point_count": [float(row["pareto_unique_point_count"]) for row in config_rows],
    }
    correlations = {
        name: {"pearson": _correlation(cost, values), "spearman": _correlation(_average_ranks(cost), _average_ranks(values))}
        for name, values in fields.items()
    }
    return {
        "scope": "descriptive full-repertoire geometry; correlations are not causal or inferential claims",
        "configuration_count": len(config_rows),
        "action_count_per_configuration": 64,
        "pair_count": len(pair_rows),
        "CD_correlations": correlations,
        "CD_ranking_descending": [row["configuration_id"] for row in sorted(config_rows, key=lambda row: float(row["C_D"]), reverse=True)],
        "max_d_ranking_descending": [row["configuration_id"] for row in sorted(config_rows, key=lambda row: float(row["max_d"]), reverse=True)],
    }


def _ablation_rows(evaluations):
    rows = []
    for index, evaluation in enumerate(evaluations):
        state = evaluation.state
        horizon_one = evaluate_state(state, horizon=1)
        identical_theta = evaluate_state(state, theta_1=THETA_1, theta_2=THETA_1)
        # The low-noise limit is an ablation diagnostic.  Its independently
        # recorded order is lower because posterior concentration makes it
        # inexpensive; it does not define the production UNKNOWN value.
        low_noise = evaluate_state(state, sigma=1e-4, quadrature_order=LOW_NOISE_QUADRATURE_ORDER)
        rows.append(
            {
                "configuration_id": f"S{index:03d}",
                "V_K_base": evaluation.known_value,
                "V_U_base": evaluation.unknown_value,
                "C_D_base": evaluation.discovery_cost,
                "V_K_h1": horizon_one.known_value,
                "V_U_h1": horizon_one.unknown_value,
                "C_D_h1": horizon_one.discovery_cost,
                "C_D_identical_theta": identical_theta.discovery_cost,
                "C_D_sigma_1e-4": low_noise.discovery_cost,
                "sigma_1e-4_quadrature_order": LOW_NOISE_QUADRATURE_ORDER,
                "revealed_theta1_value": evaluation.known_theta_1.value,
                "revealed_theta2_value": evaluation.known_theta_2.value,
            }
        )
    return rows


def _convergence_rows(states, evaluations):
    rows = []
    for index in CONVERGENCE_STATE_INDICES:
        state = states[index]
        previous = None
        for order in CONVERGENCE_ORDERS:
            value = evaluations[index].unknown_value if order == DEFAULT_QUADRATURE_ORDER else unknown_policy_value(state, quadrature_order=order).value
            rows.append(
                {
                    "configuration_id": f"S{index:03d}",
                    "quadrature_order": order,
                    "V_U": value,
                    "abs_change_from_previous_order": "" if previous is None else abs(value - previous),
                }
            )
            previous = value
    return rows


def run(*, output: Path = OUTPUT) -> dict[str, object]:
    """Evaluate every canonical state and write the complete auditable ledger."""
    states = enumerate_canonical_states()
    evaluations = tuple(evaluate_state(state) for state in states)
    geometries = tuple(action_information_geometry(state) for state in states)
    config_rows = _configuration_rows(evaluations)
    action_rows = _action_rows(evaluations)
    pair_rows = _pair_rows(evaluations)
    geometry_action_rows = _geometry_action_rows(evaluations, geometries)
    geometry_config_rows = _geometry_configuration_rows(evaluations, geometries)
    pair_diagnostic_rows = _pair_diagnostic_rows(geometry_config_rows)
    ablation_rows = _ablation_rows(evaluations)
    convergence_rows = _convergence_rows(states, evaluations)
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "configurations": output / "configurations.csv",
        "actions": output / "actions.csv",
        "pair_frontier": output / "pair_frontier.csv",
        "ablations": output / "ablations.csv",
        "convergence": output / "convergence.csv",
        "action_information_geometry": output / "action_information_geometry.csv",
        "configuration_information_geometry": output / "configuration_information_geometry.csv",
        "pair_diagnostics": output / "pair_diagnostics.csv",
    }
    _write_csv(config_rows, paths["configurations"])
    _write_csv(action_rows, paths["actions"])
    _write_csv(pair_rows, paths["pair_frontier"])
    _write_csv(ablation_rows, paths["ablations"])
    _write_csv(convergence_rows, paths["convergence"])
    _write_csv(geometry_action_rows, paths["action_information_geometry"])
    _write_csv(geometry_config_rows, paths["configuration_information_geometry"])
    _write_csv(pair_diagnostic_rows, paths["pair_diagnostics"])
    final_changes = [float(row["abs_change_from_previous_order"]) for row in convergence_rows if row["quadrature_order"] == CONVERGENCE_ORDERS[-1]]
    summary = {
        "experiment_id": "discover_v0",
        "scope": "fixed-repertoire DISCOVER cost; CES, Bayes, and numerical belief-state DP are purchased standard tools, not HLS mechanisms",
        "parameters": {
            "agents": 3,
            "capabilities": 2,
            "competence_grid": [0.0, 0.5, 1.0],
            "budget": 3.0,
            "individual_actions": [list(action) for action in ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.5, 0.5))],
            "joint_action_count": 64,
            "rho": RHO,
            "theta1_alpha": THETA_1,
            "theta2_alpha": THETA_2,
            "prior_theta1": DEFAULT_PRIOR,
            "sigma": DEFAULT_SIGMA,
            "horizon": DEFAULT_HORIZON,
            "quadrature_order": DEFAULT_QUADRATURE_ORDER,
            "convergence_orders": CONVERGENCE_ORDERS,
            "convergence_state_indices": CONVERGENCE_STATE_INDICES,
            "low_noise_ablation_quadrature_order": LOW_NOISE_QUADRATURE_ORDER,
        },
        "labelled_state_count": labelled_state_count(),
        "canonical_state_count": len(states),
        "V_K_range": [min(item.known_value for item in evaluations), max(item.known_value for item in evaluations)],
        "V_U_range": [min(item.unknown_value for item in evaluations), max(item.unknown_value for item in evaluations)],
        "C_D_range": [min(item.discovery_cost for item in evaluations), max(item.discovery_cost for item in evaluations)],
        "pair_count": len(pair_rows),
        "max_final_quadrature_change": max(final_changes),
        "artifact_files": {name: path.name for name, path in paths.items()},
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    geometry_summary_path = output / "information_geometry_summary.json"
    geometry_summary_path.write_text(json.dumps(_geometry_summary(geometry_config_rows, pair_diagnostic_rows), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "command": "python experiments/synthetic/discover_v0/run_discover_v0.py",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "module_sha256": _sha256(MODULE),
        "runner_sha256": _sha256(RUNNER),
        "artifact_sha256": {name: _sha256(path) for name, path in paths.items()} | {"summary": _sha256(summary_path), "information_geometry_summary": _sha256(geometry_summary_path)},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
