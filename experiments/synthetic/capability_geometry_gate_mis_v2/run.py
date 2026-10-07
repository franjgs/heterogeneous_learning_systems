"""Exact capability-geometry replication under the preregistered MIS-v2 grid."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.synthetic.capability_geometry_gate.run import (  # noqa: E402
    BUDGET_BY_CAPABILITY,
    CONFIGURATIONS,
    ENVIRONMENTS,
    SEED,
    SEEDS,
    column_sums,
    geometry_descriptors,
)
from hls.discover_develop_v0 import (  # noqa: E402
    DEVELOP_KNOWN,
    DISCOVER_DEVELOP,
    DISCOVER_ONLY,
    MODES,
    STATIC_KNOWN,
)
from hls.discover_develop_v2 import eta_to_lambda, run_sequence_v2  # noqa: E402
from hls.discover_v0 import N_AGENTS, N_CAPABILITIES, evaluate_state  # noqa: E402

OUT = ROOT / "results" / "foundations" / "capability_geometry_gate_mis_v2"
ETA_GRID = (0.05, 0.10, 0.20, 0.35, 0.50, 0.70, 0.90)
CONTROL_IDS = {"G00", "G06", "G07", "G08"}
REFERENCE_SEED = SEED


def _text(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def _write(rows: list[dict], filename: str) -> None:
    with (OUT / filename).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _run_task(task):
    eta, config, environment, sequence, mode, seed = task
    steps = run_sequence_v2(config["state"], sequence, mode=mode, eta=eta, seed=seed)
    rewards = [step.expected_reward_true for step in steps]
    changed = [i for i in range(1, len(steps)) if steps[i].problem_id != steps[i - 1].problem_id and steps[i].true_theta != steps[i - 1].true_theta]
    summary = {
        "eta": eta, "lambda": eta_to_lambda(eta), "configuration_id": config["configuration_id"],
        "family": config["family"], "alpha": config["alpha"], "environment": environment,
        "mode": mode, "seed": seed, "performance": steps[-1].cumulative_expected_reward,
        "early_performance": sum(rewards[:3]), "late_performance": sum(rewards[-3:]),
        "post_change_reward": "" if not changed else sum(rewards[i] for i in changed) / len(changed),
        "assignment_changes": sum(steps[i].action != steps[i - 1].action for i in range(1, len(steps))),
        "final_S": _text(steps[-1].state_after),
    }
    trajectories = []
    for step in steps:
        delta = tuple(tuple(step.state_after[i][k] - step.state_before[i][k] for k in range(N_CAPABILITIES)) for i in range(N_AGENTS))
        trajectories.append(
            {
                "eta": eta, "lambda": eta_to_lambda(eta), "configuration_id": config["configuration_id"],
                "family": config["family"], "alpha": config["alpha"], "environment": environment,
                "mode": mode, "seed": seed, "problem_index": step.problem_id, "step_index": step.step_id,
                "true_theta_evaluation_only": step.true_theta, "belief_pre": step.belief_before,
                "belief_post": step.belief_after, "S_pre": _text(step.state_before),
                "assignment": _text(step.action), "capability_exercised": _text(step.action),
                "production": step.expected_reward_true, "observed_reward": step.observed_reward,
                "development_increment": _text(delta), "S_post": _text(step.state_after),
                "cumulative_performance": step.cumulative_expected_reward,
            }
        )
    return summary, trajectories


def _clone_eta(summary: dict, trajectories: list[dict], eta: float):
    cloned_summary = {**summary, "eta": eta, "lambda": eta_to_lambda(eta)}
    cloned_trajectories = [{**row, "eta": eta, "lambda": eta_to_lambda(eta)} for row in trajectories]
    return cloned_summary, cloned_trajectories


def main(*, workers: int = 1) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    vks = {config["configuration_id"]: evaluate_state(config["state"]).known_value for config in CONFIGURATIONS}
    configurations, descriptors = [], []
    for config in CONFIGURATIONS:
        state = config["state"]
        common = {"configuration_id": config["configuration_id"], "family": config["family"], "alpha": config["alpha"]}
        configurations.append({**common, "B_1": column_sums(state)[0], "B_2": column_sums(state)[1], "state": _text(state)})
        descriptors.append({**common, **geometry_descriptors(state), "initial_V_K": vks[config["configuration_id"]]})
    environments = [
        {"environment": name, "theta_sequence": "|".join("theta1" if theta[0] > theta[1] else "theta2" for theta in sequence), "problems": len(sequence), "horizon_per_problem": 3}
        for name, sequence in ENVIRONMENTS.items()
    ]
    eta_rows = [
        {
            "eta": eta, "lambda": eta_to_lambda(eta),
            "rate_band": "slow" if eta <= 0.10 else "moderate" if eta <= 0.50 else "fast",
            "s0_0_after_one": eta,
            "s0_0_1_after_one": 0.1 + eta * 0.9,
            "s0_0_5_after_one": 0.5 + eta * 0.5,
            "s0_0_9_after_one": 0.9 + eta * 0.1,
            "design_status": "preregistered sensitivity point; not calibrated",
        }
        for eta in ETA_GRID
    ]

    tasks = []
    for eta in ETA_GRID:
        for config in CONFIGURATIONS:
            for environment, sequence in ENVIRONMENTS.items():
                modes = (DISCOVER_DEVELOP, DEVELOP_KNOWN) if config["configuration_id"] in CONTROL_IDS else (DISCOVER_DEVELOP,)
                for mode in modes:
                    for seed in SEEDS:
                        tasks.append((eta, config, environment, sequence, mode, seed))
    # No-development controls are eta-invariant. Compute them once, then label
    # exact copies for every preregistered eta rather than waste DP evaluations.
    static_tasks = [
        (ETA_GRID[0], config, environment, sequence, mode, seed)
        for config in CONFIGURATIONS if config["configuration_id"] in CONTROL_IDS
        for environment, sequence in ENVIRONMENTS.items()
        for mode in (DISCOVER_ONLY, STATIC_KNOWN)
        for seed in SEEDS
    ]
    all_tasks = tasks + static_tasks
    if workers == 1:
        computed = map(_run_task, all_tasks)
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        computed = executor.map(_run_task, all_tasks, chunksize=1)
    runs, trajectories = [], []
    for summary, rows in computed:
        summary["initial_V_K"] = vks[summary["configuration_id"]]
        runs.append(summary)
        trajectories.extend(rows)
        if summary["mode"] in (DISCOVER_ONLY, STATIC_KNOWN):
            for eta in ETA_GRID[1:]:
                cloned_summary, cloned_rows = _clone_eta(summary, rows, eta)
                cloned_summary["initial_V_K"] = summary["initial_V_K"]
                runs.append(cloned_summary)
                trajectories.extend(cloned_rows)
    if workers != 1:
        executor.shutdown()
    runs.sort(key=lambda row: (row["eta"], row["configuration_id"], row["environment"], row["mode"], row["seed"]))
    trajectories.sort(key=lambda row: (row["eta"], row["configuration_id"], row["environment"], row["mode"], row["seed"], row["problem_index"], row["step_index"]))

    main_runs = [row for row in runs if row["mode"] == DISCOVER_DEVELOP]
    regime = []
    for eta in ETA_GRID:
        for environment in ENVIRONMENTS:
            cells = []
            for config in CONFIGURATIONS:
                samples = [row for row in main_runs if row["eta"] == eta and row["environment"] == environment and row["configuration_id"] == config["configuration_id"]]
                values = [float(row["performance"]) for row in samples]
                cells.append(
                    {
                        "eta": eta, "lambda": eta_to_lambda(eta), "environment": environment,
                        "configuration_id": config["configuration_id"], "family": config["family"], "alpha": config["alpha"],
                        "mean_performance": sum(values) / len(values), "min_performance": min(values), "max_performance": max(values),
                        "initial_V_K": vks[config["configuration_id"]], "seeds": len(SEEDS),
                    }
                )
            for rank, row in enumerate(sorted(cells, key=lambda item: (-item["mean_performance"], item["configuration_id"])), 1):
                regime.append({"rank": rank, "winner": rank == 1, **row})

    pairs = []
    descriptor_by_id = {row["configuration_id"]: row for row in descriptors}
    for eta in ETA_GRID:
        for left, right in combinations(CONFIGURATIONS, 2):
            dl, dr = descriptor_by_id[left["configuration_id"]], descriptor_by_id[right["configuration_id"]]
            row = {
                "eta": eta, "configuration_a": left["configuration_id"], "configuration_b": right["configuration_id"],
                "Delta_V_K": abs(float(dl["initial_V_K"]) - float(dr["initial_V_K"])),
                "Delta_heterogeneity": abs(float(dl["between_agent_heterogeneity"]) - float(dr["between_agent_heterogeneity"])),
                "Delta_overlap": abs(float(dl["within_person_overlap"]) - float(dr["within_person_overlap"])),
                "same_B_1": True, "same_B_2": True,
            }
            for environment in ENVIRONMENTS:
                pa = next(x["mean_performance"] for x in regime if x["eta"] == eta and x["environment"] == environment and x["configuration_id"] == left["configuration_id"])
                pb = next(x["mean_performance"] for x in regime if x["eta"] == eta and x["environment"] == environment and x["configuration_id"] == right["configuration_id"])
                row[f"performance_a_{environment}"] = pa
                row[f"performance_b_{environment}"] = pb
                row[f"Delta_performance_{environment}"] = abs(float(pa) - float(pb))
            pairs.append(row)
    pairs.sort(key=lambda row: (row["eta"], row["Delta_V_K"], -row["Delta_heterogeneity"], row["configuration_a"], row["configuration_b"]))

    interior_ids = {
        config["configuration_id"] for config in CONFIGURATIONS
        if all(0.0 < value < 1.0 for row in config["state"] for value in row)
    }
    interior = []
    for eta in ETA_GRID:
        for environment in ENVIRONMENTS:
            cells = [row for row in regime if row["eta"] == eta and row["environment"] == environment and row["configuration_id"] in interior_ids]
            for rank, row in enumerate(sorted(cells, key=lambda item: (-item["mean_performance"], item["configuration_id"])), 1):
                interior.append({"interior_rank": rank, "interior_winner": rank == 1, **row})

    old_regime = list(csv.DictReader((ROOT / "results/foundations/capability_geometry_gate/regime_map.csv").open()))
    comparison = []
    for eta in ETA_GRID:
        for environment in ENVIRONMENTS:
            old = next(row for row in old_regime if row["environment"] == environment and row["winner"] == "True")
            new = next(row for row in regime if row["eta"] == eta and row["environment"] == environment and row["winner"])
            comparison.append(
                {
                    "eta": eta, "environment": environment, "mis_v1_winner": old["configuration_id"],
                    "mis_v1_performance": old["mean_performance"], "mis_v2_winner": new["configuration_id"],
                    "mis_v2_performance": new["mean_performance"], "winner_survives": old["configuration_id"] == new["configuration_id"],
                }
            )

    representative = [
        row for row in main_runs
        if row["seed"] == REFERENCE_SEED and (
            any(m["eta"] == row["eta"] and m["environment"] == row["environment"] and m["configuration_id"] == row["configuration_id"] and m["winner"] for m in regime)
            or (row["configuration_id"] in {"G00", "G06"} and row["environment"] == "alternating_1212")
        )
    ]

    _write(eta_rows, "eta_grid.csv")
    _write(configurations, "configurations.csv")
    _write(environments, "environments.csv")
    _write(runs, "runs.csv")
    _write(trajectories, "trajectories.csv")
    _write(pairs, "matched_pairs.csv")
    _write(regime, "regime_map_by_eta.csv")
    _write(descriptors, "geometry_descriptors.csv")
    _write(representative, "representative_cases.csv")
    _write(comparison, "mis_v1_vs_v2.csv")
    _write(interior, "interior_geometry_check.csv")
    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "parent_head": "9fc68a5", "mis_v1_results_preserved": True, "eta_grid": ETA_GRID,
                "seeds": SEEDS, "N": N_AGENTS, "K": N_CAPABILITIES, "B_k": BUDGET_BY_CAPABILITY,
                "configurations": len(CONFIGURATIONS), "environments": len(ENVIRONMENTS),
                "main_executions": len(ETA_GRID) * len(CONFIGURATIONS) * len(ENVIRONMENTS) * len(SEEDS),
                "total_run_rows": len(runs), "trajectory_rows": len(trajectories),
                "controls": sorted(CONTROL_IDS), "interior_configurations": sorted(interior_ids),
                "only_physics_change": "MIS-v1 capability transition -> MIS-v2 exponential capability-gap transition",
            }, indent=2,
        ) + "\n", encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    main(workers=args.workers)
