"""Registered, bounded preflight for the first HLS Q1 campaign.

This script runs only diagnostic samples. It does not execute the 960-run
main campaign. All generated problem paths are frozen before organization
evaluation and reused across paired architecture/MIS arms.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path
from random import Random
from typing import Any

from hls.discover_v0 import JOINT_ACTIONS, production_inputs
from hls.hls_lab_dynamic import DemandRegime, LearningProfile, advance_team
from hls.hls_lab_v1 import ProblemSpec, evaluate_problem, make_team
from hls.hls_lab_v1_environment import (
    ExogenousEnvironmentConfig,
    EnvironmentTrajectory,
    generate_environment_trajectory,
)
from hls.hls_lab_v1_integrated import (
    IntegratedProblem,
    P0ProductionOnly,
    TeachingEfficacy,
    TeachingParameters,
    run_integrated_sequence,
)
from hls.synthetic.c5 import MarkovTaskDemand, StationaryTaskDemand


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results/diagnostics/hls_q1_preflight"
PROTOCOL = ROOT / "results/diagnostics/hls_q1_preflight/preregistration.json"
DOC = ROOT / "docs/experiments/HLS_Q1_PREFLIGHT.md"
REGISTERED_DOC_SHA256 = "7fcfb9a900e522356531d02ef1fa65bc619643e798c3373a7031b39bdc4572ce"
PI = (0.4, 0.4, 0.2)
LABELS = ("skill0", "skill1", "joint")
ARCH = {
    "homogeneous": ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)),
    "tilted": ((0.6, 0.4), (0.4, 0.6), (0.5, 0.5)),
}
LEARNING = LearningProfile(((0.1, 0.1), (0.1, 0.1), (0.1, 0.1)))
ETA_OFF = LearningProfile(((0.1, 0.1), (0.1, 0.1), (0.1, 0.1)))
DIFFICULTY = {
    "easy": ((0.5, 0.0), (0.0, 0.5), (0.25, 0.25)),
    "near_boundary": ((1.05, 0.0), (0.0, 1.05), (0.55, 0.55)),
    "learnable": ((1.3348, 0.0), (0.0, 1.3348), (0.6924, 0.6924)),
}
CES_WEIGHTS = ((1.0, 0.0), (0.0, 1.0), (0.5, 0.5))
DEMAND_SEEDS = {"iid": range(2026101600, 2026101800),
                "markov": range(2026101800, 2026102000)}
OUTCOME_SEEDS = {"iid": range(2026102100, 2026102112),
                 "markov": range(2026102200, 2026102212)}
TASK_ID = {label: i for i, label in enumerate(LABELS)}


def _process(family: str):
    if family == "iid":
        return StationaryTaskDemand(dict(zip(LABELS, PI)))
    transitions = {
        LABELS[i]: {LABELS[j]: (0.8 if i == j else 0.0) + 0.2 * PI[j]
                    for j in range(3)}
        for i in range(3)
    }
    return MarkovTaskDemand(dict(zip(LABELS, PI)), transitions)


def _requirements_for_stratum(stratum: str):
    return DIFFICULTY[stratum]


def _config(family: str, stratum: str, *, budget: float = 2.0, horizon: int = 24):
    requirements = _requirements_for_stratum(stratum)
    emissions = {
        LABELS[i]: DemandRegime(LABELS[i], (requirements[i],), (1.0,))
        for i in range(3)
    }
    return ExogenousEnvironmentConfig(_process(family), emissions, horizon,
                                      resource_budget=budget)


def _weighted_trajectory(trajectory: EnvironmentTrajectory) -> EnvironmentTrajectory:
    weighted = tuple(replace(item, ces_weights=CES_WEIGHTS[TASK_ID[label]])
                     for item, label in zip(trajectory.problems, trajectory.latent_states))
    return EnvironmentTrajectory(trajectory.seed, weighted, trajectory.latent_states)


def _trajectory_hash(trajectory: EnvironmentTrajectory) -> str:
    value = [int(TASK_ID[label]) for label in trajectory.latent_states]
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def _close_tree(left, right, tol=1e-12):
    if isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):
        return len(left) == len(right) and all(_close_tree(a, b, tol) for a, b in zip(left, right))
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(left, right, rel_tol=0.0, abs_tol=tol)
    return left == right


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frontier(team_matrix, requirements, budget=2.0, cap=1.0):
    spec = ProblemSpec("frontier", requirements, budget, max_effort_per_expert=cap)
    rows = []
    active = [k for k, value in enumerate(requirements) if value > 0]
    for action_id, action in enumerate(JOINT_ACTIONS):
        effort = sum(sum(row) for row in action)
        if effort > budget + 1e-12 or any(sum(row) > cap + 1e-12 for row in action):
            continue
        outputs = production_inputs(team_matrix, action)
        level = min(outputs[k] / requirements[k] for k in active)
        success = evaluate_problem(outputs, requirements).success
        rows.append({"action_id": action_id, "action": action,
                     "outputs": outputs, "effort": effort,
                     "success": success, "level": level})
    return rows


def _frontier_level(team_matrix, orientation: int, budget=2.0, cap=1.0):
    req = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0))[orientation]
    rows = _frontier(team_matrix, req, budget, cap)
    return max(row["level"] for row in rows)


def feasibility_diagnostics() -> dict[str, Any]:
    frontiers: dict[str, list[float]] = {}
    action_tables = []
    for name, matrix in ARCH.items():
        frontiers[name] = []
        for task_idx, label in enumerate(LABELS):
            orient = ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0))[task_idx]
            rows = _frontier(matrix, orient)
            frontier = max(row["level"] for row in rows)
            frontiers[name].append(frontier)
            for stratum, req in zip(DIFFICULTY, DIFFICULTY.values()):
                problem_req = req[task_idx]
                cases = _frontier(matrix, problem_req)
                success_rows = [row for row in cases if row["success"]]
                active = [k for k, value in enumerate(problem_req) if value > 0]
                # Since registered vectors are λ*w with w in {e0,e1,(1,1)},
                # the normalized frontier is directly comparable to λ.
                target = max(problem_req[k] for k in active)
                action_tables.append({
                    "architecture": name, "task": label, "stratum": stratum,
                    "requirements": problem_req, "frontier": frontier,
                    "distance_frontier_minus_requirement": frontier - target,
                    "max_active_output": max(min(row["outputs"][k] for k in active)
                                              for row in cases),
                    "successful_action_count": len(success_rows),
                    "feasible_action_count": len(cases),
                    "resource_min": min(row["effort"] for row in cases),
                    "resource_max": max(row["effort"] for row in cases),
                    "resource_effort_counts": dict(Counter(str(row["effort"]) for row in cases)),
                    "successful_effort_min": (min(row["effort"] for row in success_rows)
                                               if success_rows else None),
                    "successful_effort_max": (max(row["effort"] for row in success_rows)
                                               if success_rows else None),
                    "successful_resource_effort_counts": dict(Counter(
                        str(row["effort"]) for row in success_rows)),
                    "successful_action_ids": [row["action_id"] for row in success_rows],
                })
    witness_teams = {}
    for name, matrix in ARCH.items():
        team = make_team(matrix)
        for t in range(24):
            action = [(0.0, 0.0)] * 3
            action[t % 3] = (1.0, 0.0)
            action[(t + 1) % 3] = (0.0, 1.0)
            team = advance_team(team, tuple(action), LEARNING, enabled=True)
        witness_teams[name] = team.real_matrix
    witness_frontiers = {
        name: [_frontier_level(matrix, i) for i in range(3)]
        for name, matrix in witness_teams.items()
    }
    return {"initial_frontiers": frontiers, "witness_competences": witness_teams,
            "witness_frontiers": witness_frontiers, "action_feasibility": action_tables}


def _run_lengths(labels: tuple[str, ...]):
    runs = []
    start = 0
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[start]:
            runs.append((labels[start], i - start))
            start = i
    return runs


def demand_diagnostics() -> dict[str, Any]:
    result = {}
    for family, seeds in DEMAND_SEEDS.items():
        paths = []
        repeat_ok = True
        task_counts = Counter()
        transition_counts = Counter()
        run_lengths = {label: [] for label in LABELS}
        hashes = set()
        for seed in seeds:
            trajectory = generate_environment_trajectory(
                _config(family, "near_boundary"), seed=seed)
            labels = tuple(trajectory.latent_states)
            repeat = generate_environment_trajectory(
                _config(family, "near_boundary"), seed=seed)
            repeat_ok &= trajectory == repeat
            hashes.add(_trajectory_hash(trajectory))
            task_counts.update(labels)
            for left, right in zip(labels, labels[1:]):
                transition_counts[(left, right)] += 1
            for label, length in _run_lengths(labels):
                run_lengths[label].append(length)
            paths.append(labels)
        total = sum(task_counts.values())
        total_transitions = sum(transition_counts.values())
        run_summary = {}
        for label, values in run_lengths.items():
            run_summary[label] = {
                "count": len(values),
                "mean": statistics.mean(values) if values else None,
                "median": statistics.median(values) if values else None,
                "p90_nearest_rank": sorted(values)[math.ceil(0.9 * len(values)) - 1]
                if values else None,
            }
        result[family] = {
            "paths": len(paths), "horizon": 24,
            "distinct_paths": len(hashes), "repeat_seed_reproducible": repeat_ok,
            "task_counts": dict(task_counts),
            "empirical_task_frequencies": {k: task_counts[k] / total for k in LABELS},
            "transitions": {f"{a}->{b}": transition_counts[(a, b)]
                            for a in LABELS for b in LABELS},
            "lag_one_same_task": sum(transition_counts[(x, x)] for x in LABELS) / total_transitions,
            "run_lengths_by_task": run_summary,
        }
    return result


def _bootstrap_mean(values: list[float], rng: Random, n: int = 10_000) -> tuple[float, float]:
    means = []
    for _ in range(n):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(statistics.mean(sample))
    means.sort()
    return means[math.floor(0.025 * n)], means[math.floor(0.975 * n)]


def primary_task_effect_diagnostic():
    """Evaluate one near-boundary context per task to test mean-effect structure."""
    by_task = {}
    for task_index, label in enumerate(LABELS):
        problem = IntegratedProblem(
            ProblemSpec(f"near-{label}", DIFFICULTY["near_boundary"][task_index], 2.0),
            CES_WEIGHTS[task_index], label,
        )
        for architecture, matrix in ARCH.items():
            result = run_integrated_sequence(
                make_team(matrix), (problem,), P0ProductionOnly(), learning=LEARNING,
                teaching_efficacy=_zero_efficacy(),
                parameters=TeachingParameters(production_observation_noise_sd=0.0,
                                              outcome_noise_sd=0.0),
                individual_learning=False, organizational_learning=False, seed=0,
            )
            record = result.records[0]
            by_task.setdefault(label, {})[architecture] = {
                "ces": record.ces_reward,
                "success": record.functional_result.success,
                "action_id": record.production_action_id,
                "estimate_before": record.competence_estimated_before,
                "estimate_after": record.competence_estimated_after,
            }
    return by_task


def outcome_diagnostics():
    rows = []
    demand_paths = {}
    paired_primary: dict[str, list[float]] = {"iid": [], "markov": []}
    path_distinct = {family: set() for family in OUTCOME_SEEDS}
    for family, seeds in OUTCOME_SEEDS.items():
        for seed in seeds:
            for stratum in DIFFICULTY:
                trajectory = _weighted_trajectory(generate_environment_trajectory(
                    _config(family, stratum), seed=seed))
                path_hash = _trajectory_hash(trajectory)
                path_distinct[family].add(path_hash)
                demand_paths[f"{family}:{seed}:{stratum}"] = {
                    "hash": path_hash, "task_labels": trajectory.latent_states,
                    "requirements": tuple(item.problem.requirements for item in trajectory.problems),
                }
                for mis_on in (False, True):
                    arm_results = {}
                    for architecture, initial in ARCH.items():
                        result = run_integrated_sequence(
                            make_team(initial), trajectory.problems, P0ProductionOnly(),
                            learning=LEARNING, teaching_efficacy=_zero_efficacy(),
                            parameters=TeachingParameters(
                                production_observation_noise_sd=0.0,
                                outcome_noise_sd=0.0,
                            ), individual_learning=mis_on,
                            organizational_learning=False, seed=seed,
                        )
                        records = result.records
                        if (tuple(record.requirements for record in records) !=
                                tuple(item.problem.requirements for item in trajectory.problems)
                                or any(record.action.teaching is not None for record in records)):
                            raise AssertionError("matched demand or no-teaching contract was violated")
                        for item, record in zip(trajectory.problems, records):
                            if (not math.isclose(record.total_resource_used,
                                                 record.production_effort + record.teaching_effort,
                                                 rel_tol=0.0, abs_tol=1e-12)
                                    or record.total_resource_used > item.problem.resource_budget + 1e-12):
                                raise AssertionError("resource trace violates the shared-budget contract")
                            expected_team = advance_team(
                                make_team(record.competence_real_before), record.action.production,
                                LEARNING, enabled=mis_on,
                            )
                            if not _close_tree(record.competence_real_after,
                                               expected_team.real_matrix):
                                raise AssertionError("competence transition differs from declared MIS-v2 control")
                        values = {
                            "ces": sum(record.ces_reward for record in records),
                            "successes": sum(int(record.functional_result.success) for record in records),
                            "resource_used": sum(record.total_resource_used for record in records),
                            "unused_capacity": sum(
                                item.problem.resource_budget - record.total_resource_used
                                for item, record in zip(trajectory.problems, records)),
                            "action_ids": tuple(record.production_action_id for record in records),
                            "production_actions": tuple(record.action.production for record in records),
                            "ces_path": tuple(record.cumulative_ces_reward for record in records),
                            "success_path": tuple(record.functional_result.success for record in records),
                            "competence_before": tuple(record.competence_real_before for record in records),
                            "competence_after": tuple(record.competence_real_after for record in records),
                            "estimate_before": tuple(record.competence_estimated_before for record in records),
                            "estimate_after": tuple(record.competence_estimated_after for record in records),
                            "observations": tuple(record.individual_observations for record in records),
                            "effort_path": tuple(record.production_effort for record in records),
                            "teaching_effort": sum(record.teaching_effort for record in records),
                        }
                        arm_results[architecture] = values
                        rows.append({
                            "family": family, "seed": seed, "stratum": stratum,
                            "mis_on": mis_on, "architecture": architecture,
                            "demand_path_hash": path_hash, **values,
                        })
                    if stratum == "near_boundary" and not mis_on:
                        paired_primary[family].append(
                            arm_results["tilted"]["ces"] - arm_results["homogeneous"]["ces"])
    if set(path_distinct) != {"iid", "markov"}:
        raise AssertionError("unexpected demand families")
    rng = Random(20261016)
    iid_mean = statistics.mean(paired_primary["iid"])
    markov_mean = statistics.mean(paired_primary["markov"])
    theta = markov_mean - iid_mean
    bootstrap = []
    for _ in range(10_000):
        iid = statistics.mean([paired_primary["iid"][rng.randrange(12)] for _ in range(12)])
        markov = statistics.mean([paired_primary["markov"][rng.randrange(12)] for _ in range(12)])
        bootstrap.append(markov - iid)
    bootstrap.sort()
    primary = {
        "estimand": "mean(tilted-homogeneous | Markov, near-boundary, MIS OFF) - mean(tilted-homogeneous | IID, near-boundary, MIS OFF)",
        "iid_architecture_effects": paired_primary["iid"],
        "markov_architecture_effects": paired_primary["markov"],
        "iid_mean": iid_mean, "markov_mean": markov_mean, "theta_estimate": theta,
        "theta_seed_cluster_bootstrap_95_percentile_ci":
            [bootstrap[250], bootstrap[9749]],
    }
    primary_task_effects = primary_task_effect_diagnostic()
    task_deltas = {
        label: task["tilted"]["ces"] - task["homogeneous"]["ces"]
        for label, task in primary_task_effects.items()
    }
    primary["one_period_task_specific_architecture_effects"] = primary_task_effects
    primary["one_period_task_effects_are_equal"] = max(task_deltas.values()) - min(task_deltas.values()) <= 1e-12
    primary["mis_off_estimates_unchanged_in_registered_runs"] = all(
        _close_tree(row["estimate_before"], row["estimate_after"])
        for row in rows if not row["mis_on"])
    primary["identified_structural_mean_interaction"] = (
        "ZERO_IN_EXPECTATION_FROM_COMMON_STATIONARY_MARGINALS_AND_FROZEN_STATE"
        if primary["mis_off_estimates_unchanged_in_registered_runs"] else
        "NOT_ESTABLISHED_BY_PREFLIGHT")
    sensitivity = {}
    for family, subset in ((family, [r for r in rows if r["family"] == family])
                           for family in OUTCOME_SEEDS):
        conditions = {}
        for stratum in DIFFICULTY:
            for mis_on in (False, True):
                for architecture in ARCH:
                    group = [r for r in subset if r["stratum"] == stratum
                             and r["mis_on"] == mis_on and r["architecture"] == architecture]
                    conditions[f"{stratum}|MIS_{'ON' if mis_on else 'OFF'}|{architecture}"] = {
                        "n": len(group),
                        "distinct_action_paths": len({r["action_ids"] for r in group}),
                        "distinct_ces_paths": len({r["ces_path"] for r in group}),
                        "distinct_success_paths": len({r["success_path"] for r in group}),
                        "distinct_final_ces": len({r["ces"] for r in group}),
                        "distinct_estimate_paths": len({r["estimate_after"] for r in group}),
                        "distinct_resource_totals": len({r["resource_used"] for r in group}),
                        "success_total": sum(r["successes"] for r in group),
                        "decision_total": sum(len(r["action_ids"]) for r in group),
                        "mean_ces": statistics.mean(r["ces"] for r in group),
                        "mean_success_rate": statistics.mean(r["successes"] / 24 for r in group),
                        "mean_resource_used": statistics.mean(r["resource_used"] for r in group),
                        "mean_unused_capacity": statistics.mean(r["unused_capacity"] for r in group),
                        "mean_final_competence": tuple(
                            statistics.mean(r["competence_after"][-1][i][k]
                                            for r in group for i in range(3))
                            for k in range(2)),
                    }
        sensitivity[family] = conditions
    return rows, demand_paths, primary, sensitivity, {
        family: len(paths) for family, paths in path_distinct.items()
    }


def _zero_efficacy():
    return TeachingEfficacy(tuple(
        tuple((0.0, 0.0) for _ in range(3)) for _ in range(3)
    ))


def equivalence_control():
    horizon = 24
    problems = tuple(ProblemSpec("skill0-control", (0.2, 0.0), 3.0,
                                 max_effort_per_expert=1.0) for _ in range(horizon))
    summary = {}
    raw = {}
    for mis_on in (False, True):
        arms = {}
        for architecture, matrix in ARCH.items():
            result = run_integrated_sequence(
                make_team(matrix), tuple(IntegratedProblem(problem, (1.0, 0.0), "skill0")
                                         for problem in problems),
                P0ProductionOnly(), learning=LEARNING, teaching_efficacy=_zero_efficacy(),
                parameters=TeachingParameters(production_observation_noise_sd=0.0,
                                              outcome_noise_sd=0.0),
                individual_learning=mis_on, organizational_learning=False, seed=77,
            )
            arms[architecture] = {
                "ces": tuple(r.ces_reward for r in result.records),
                "outputs": tuple(r.outputs for r in result.records),
                "success": tuple(r.functional_result.success for r in result.records),
                "competences": tuple(r.competence_real_after for r in result.records),
                "effort": tuple(r.total_resource_used for r in result.records),
                "actions": tuple(r.production_action_id for r in result.records),
            }
        passed = all(_close_tree(arms["homogeneous"][field], arms["tilted"][field])
                     for field in ("ces", "outputs", "success", "effort"))
        if mis_on:
            for field in ("competences",):
                h_totals = [sum(arms["homogeneous"][field][t][i][0] for i in range(3))
                            for t in range(horizon)]
                tilted_totals = [sum(arms["tilted"][field][t][i][0] for i in range(3))
                                 for t in range(horizon)]
                passed &= all(abs(a - b) <= 1e-12 for a, b in zip(h_totals, tilted_totals))
        summary[f"MIS_{'ON' if mis_on else 'OFF'}"] = {
            "pass": passed,
            "action_paths_equal": arms["homogeneous"]["actions"] == arms["tilted"]["actions"],
            "outputs_equal_within_1e-12": _close_tree(arms["homogeneous"]["outputs"],
                                                       arms["tilted"]["outputs"]),
            "ces_equal_within_1e-12": _close_tree(arms["homogeneous"]["ces"],
                                                   arms["tilted"]["ces"]),
            "success_equal": arms["homogeneous"]["success"] == arms["tilted"]["success"],
            "resource_equal": arms["homogeneous"]["effort"] == arms["tilted"]["effort"],
            "skill0_competence_totals_equal": all(
                abs(sum(arms["homogeneous"]["competences"][t][i][0] for i in range(3))
                    - sum(arms["tilted"]["competences"][t][i][0] for i in range(3))) <= 1e-12
                for t in range(horizon)),
        }
        raw[f"MIS_{'ON' if mis_on else 'OFF'}"] = arms
    return summary, raw


def run_preflight(output_dir: Path = OUT):
    if not PROTOCOL.exists() or not DOC.exists():
        raise RuntimeError("pre-registration files must exist before diagnostics")
    protocol = json.loads(PROTOCOL.read_text())
    if protocol["status"] != "REGISTERED_BEFORE_DIAGNOSTICS":
        raise RuntimeError("protocol is not registered")
    feasibility = feasibility_diagnostics()
    demand = demand_diagnostics()
    outcome_rows, paths, primary, sensitivity, distinct = outcome_diagnostics()
    equivalence, equivalence_raw = equivalence_control()
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "protocol": protocol["protocol"],
        "registered_document_sha256": REGISTERED_DOC_SHA256,
        "registered_json_sha256": _sha(PROTOCOL),
        "architecture_checks": {
            "agents": {name: len(matrix) for name, matrix in ARCH.items()},
            "skill_totals": {name: [sum(row[k] for row in matrix) for k in range(2)]
                             for name, matrix in ARCH.items()},
            "agent_totals": {name: [sum(row) for row in matrix] for name, matrix in ARCH.items()},
            "learning_eta": LEARNING.eta,
            "budget": 2.0, "per_agent_cap": 1.0,
            "information": "full-information initial estimates; same contract",
            "policy": "P0ProductionOnly",
            "all_architecture_invariants_exact": (
                tuple(sum(row[k] for row in ARCH["homogeneous"]) for k in range(2)) ==
                tuple(sum(row[k] for row in ARCH["tilted"]) for k in range(2)) == (1.5, 1.5)
                and tuple(sum(row) for row in ARCH["homogeneous"]) ==
                tuple(sum(row) for row in ARCH["tilted"]) == (1.0, 1.0, 1.0)
                and LEARNING.eta == ((0.1, 0.1),) * 3
            ),
        },
        "theoretical_demand": {
            "pi": PI,
            "transition_matrix": [[(0.8 if i == j else 0.0) + 0.2 * PI[j]
                                   for j in range(3)] for i in range(3)],
            "stationarity_residual": [
                sum(PI[i] * ((0.8 if i == j else 0.0) + 0.2 * PI[j]) for i in range(3)) - PI[j]
                for j in range(3)],
            "iid_lag1_same": sum(p * p for p in PI),
            "markov_lag1_same": 0.8 + 0.2 * sum(p * p for p in PI),
            "iid_per_type_expected_run_mean": {LABELS[i]: 1 / (1 - PI[i]) for i in range(3)},
            "markov_per_type_expected_run_mean": {
                LABELS[i]: 1 / (1 - ((0.8 + 0.2 * PI[i]))) for i in range(3)},
        },
        "demand_diagnostics": demand,
        "feasibility_diagnostics": feasibility,
        "primary_preflight_estimand": primary,
        "outcome_sensitivity": sensitivity,
        "distinct_outcome_demand_paths": distinct,
        "equivalence_control": equivalence,
        "statuses": {},
    }
    # The registered gates are mechanical and independent of whether a
    # treatment estimate is positive, negative, or zero.
    arch_pass = (summary["architecture_checks"]["skill_totals"]["homogeneous"] ==
                 summary["architecture_checks"]["skill_totals"]["tilted"] == [1.5, 1.5]
                 and summary["architecture_checks"]["agent_totals"]["homogeneous"] ==
                 summary["architecture_checks"]["agent_totals"]["tilted"] == [1.0, 1.0, 1.0])
    demand_pass = all(row["repeat_seed_reproducible"] and row["distinct_paths"] >= 190
                      for row in demand.values()) and (
                          demand["markov"]["lag_one_same_task"] > demand["iid"]["lag_one_same_task"])
    initial = feasibility["initial_frontiers"]
    witness = feasibility["witness_frontiers"]
    feasible_pass = (
        initial["homogeneous"] == [1.0, 1.0, 0.5]
        and initial["tilted"] == [1.1, 1.1, 0.6]
        and all(witness[name][i] > DIFFICULTY["learnable"][i][i if i < 2 else 0]
                for name in ARCH for i in range(3))
    )
    outcome_pass = all(n == 12 for n in distinct.values())
    output_path_variation = any(
        info["distinct_ces_paths"] > 1 or info["distinct_success_paths"] > 1
        for family_info in sensitivity.values() for info in family_info.values())
    mis_off_frozen = all(
        all(before == after for before, after in zip(row["competence_before"],
                                                      row["competence_after"]))
        for row in outcome_rows if not row["mis_on"])
    mis_on_changed = any(
        before != after
        for row in outcome_rows if row["mis_on"]
        for before, after in zip(row["competence_before"], row["competence_after"]))
    primary_null_structural = primary["mis_off_estimates_unchanged_in_registered_runs"]
    resource_pass = all(
        math.isclose(row["resource_used"] + row["unused_capacity"], 2.0 * 24,
                     rel_tol=0.0, abs_tol=1e-12)
        for row in outcome_rows)
    equivalence_pass = all(row["pass"] for row in equivalence.values())
    summary["statuses"] = {
        "architecture_matching": "PASS" if arch_pass else "FAIL",
        "demand_process": "PASS" if demand_pass else "FAIL",
        "productive_feasibility": "PASS" if feasible_pass else "FAIL",
        "outcome_sensitivity": ("PASS" if outcome_pass and output_path_variation
                                else "INCONCLUSIVE" if outcome_pass else "FAIL"),
        "equivalence_control": "PASS" if equivalence_pass else "FAIL",
        "resource_accounting": "PASS" if resource_pass else "FAIL",
        "registered_primary_estimand": "FAIL_STRUCTURALLY_NULL" if primary_null_structural else "INCONCLUSIVE",
        "mis_v2_controls": "PASS" if equivalence_pass and mis_off_frozen and mis_on_changed else "FAIL",
        "statistical_registration": "PASS",
        "main_campaign": "NO_GO_AS_REGISTERED" if primary_null_structural else "HOLD_PENDING_CE_REVIEW",
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (output_dir / "demand_paths.json").write_text(json.dumps(paths, indent=2, sort_keys=True) + "\n")
    with (output_dir / "trajectory_summary.csv").open("w", newline="") as handle:
        fields = ["family", "seed", "stratum", "mis_on", "architecture",
                  "demand_path_hash", "ces", "successes", "resource_used",
                  "unused_capacity", "action_ids", "ces_path", "success_path",
                  "competence_before", "competence_after", "estimate_before", "estimate_after",
                  "observations", "production_actions", "effort_path", "teaching_effort"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in outcome_rows:
            writer.writerow({key: json.dumps(value, separators=(",", ":"))
                             if isinstance(value, (tuple, list, dict)) else value
                             for key, value in row.items()})
    (output_dir / "equivalence_control.json").write_text(
        json.dumps({"summary": equivalence, "arms": equivalence_raw}, indent=2, sort_keys=True) + "\n")
    manifest = {
        "protocol": protocol["protocol"], "registered_protocol_sha256": _sha(PROTOCOL),
        "registered_document_sha256": REGISTERED_DOC_SHA256,
        "runner_sha256": _sha(Path(__file__)),
        "source_sha256": {
            str(path.relative_to(ROOT)): _sha(path) for path in (
                ROOT / "src/hls/hls_lab_v1_environment.py",
                ROOT / "src/hls/hls_lab_v1_integrated.py",
                ROOT / "src/hls/hls_lab_dynamic.py",
                ROOT / "src/hls/discover_v0.py",
                ROOT / "src/hls/synthetic/c5.py",
            )},
        "outputs_sha256": {path.name: _sha(path) for path in output_dir.iterdir()
                            if path.is_file() and path.name != "manifest.json"},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    result = run_preflight(args.output_dir)
    print(json.dumps(result["statuses"], sort_keys=True))
    print(f"primary theta={result['primary_preflight_estimand']['theta_estimate']:.6f}; "
          f"95% seed-cluster bootstrap CI="
          f"{result['primary_preflight_estimand']['theta_seed_cluster_bootstrap_95_percentile_ci']}")


if __name__ == "__main__":
    main()
