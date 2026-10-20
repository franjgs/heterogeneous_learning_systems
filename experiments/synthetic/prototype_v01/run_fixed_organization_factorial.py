"""Run the deterministic CE-03 fixed/adaptive/intertemporal factorial.

This writes only to a new result namespace. It never edits the historical
two-policy v0.1 artifacts.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.configuration_environment_policy_v0 import CONFIGURATIONS, EXACT_TOL  # noqa: E402
from hls.configuration_environment_policy_v01 import (  # noqa: E402
    ENABLED_LEARNING_SCALE,
    GRID_LEVELS,
    environment_specs,
    evaluate_sweep,
)

OUTPUT = ROOT / "results" / "experiments" / "configuration_environment_factorial_v01_fixed"
HISTORICAL = ROOT / "results" / "foundations" / "configuration_environment_performance_v01"
SOURCES = (
    ROOT / "src" / "hls" / "configuration_environment_policy_v0.py",
    ROOT / "src" / "hls" / "configuration_environment_policy_v01.py",
    Path(__file__).resolve(),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    if not rows:
        raise ValueError(f"refusing to write an empty table: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        fieldnames = list(dict.fromkeys(key for row in rows for key in row))
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(f"output already exists; refusing to overwrite: {OUTPUT}")
    specs = environment_specs()
    points = {
        (enabled, point.configuration, point.environment): point
        for enabled in (True, False)
        for point in evaluate_sweep(
            learning_scale=ENABLED_LEARNING_SCALE,
            development_enabled=enabled,
            specifications=specs,
        )
    }
    if len(points) != 750:
        raise AssertionError(f"expected 750 configuration/environment/learning cells, got {len(points)}")

    ledger: list[dict[str, object]] = []
    regimes: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    interactions: list[dict[str, object]] = []
    policies = ("FIXED_BEST", "GREEDY_USE", "JOINT_DP")
    value = lambda p, policy: {
        "FIXED_BEST": p.fixed_best.value,
        "GREEDY_USE": p.greedy.value,
        "JOINT_DP": p.joint_dp.value,
    }[policy]

    for (enabled, configuration, spec), point in sorted(
        points.items(), key=lambda item: (item[0][2], item[0][1], not item[0][0])
    ):
        sequence = "".join("A" if task == 0 else "B" for task in point.diagnostics.sequence)
        base = {
            "environment": spec.identifier,
            "nu": spec.nu,
            "chi": spec.chi,
            "rho": spec.rho,
            "configuration": configuration,
            "sequence": sequence,
            "learning": "ON" if enabled else "OFF",
            "learning_scale": point.learning_scale,
            "horizon": len(point.diagnostics.sequence),
            "first_half_A": point.diagnostics.first_half_a_count,
            "second_half_A": point.diagnostics.second_half_a_count,
            "aggregate_A": point.diagnostics.aggregate_a_count,
            "requested_shift": point.diagnostics.requested_shift,
            "effective_shift": point.diagnostics.effective_shift,
            "adjacent_same_pairs": point.diagnostics.adjacent_same_pairs,
        }
        vals = {policy: value(point, policy) for policy in policies}
        if point.joint_dp.value + EXACT_TOL < point.fixed_best.value:
            raise AssertionError("FIXED_BEST exceeds JOINT_DP beyond frozen EXACT_TOL")
        for policy in policies:
            ledger.append(
                base
                | {
                    "policy": policy,
                    "cumulative_reward": vals[policy],
                    "fixed_agent_0_reward": point.fixed_candidates[0].value,
                    "fixed_agent_1_reward": point.fixed_candidates[1].value,
                    "fixed_agent_2_reward": point.fixed_candidates[2].value,
                    "fixed_best_agents": "|".join(map(str, point.fixed_best.first_actions)),
                }
            )
        adaptive_gain = point.greedy.value - point.fixed_best.value
        planning_gain = point.joint_dp.value - point.greedy.value
        regimes.append(
            base
            | {
                "fixed_best_value": point.fixed_best.value,
                "greedy_value": point.greedy.value,
                "joint_dp_value": point.joint_dp.value,
                "adaptive_minus_fixed": adaptive_gain,
                "planning_minus_adaptive": planning_gain,
                "fixed_sufficient_within_frozen_tolerance": abs(adaptive_gain) <= EXACT_TOL,
                "adaptive_strict_gain_beyond_frozen_tolerance": adaptive_gain > EXACT_TOL,
                "planning_strict_gain_beyond_frozen_tolerance": planning_gain > EXACT_TOL,
                "dominance_roundoff_within_frozen_tolerance": point.fixed_best.value > point.joint_dp.value,
            }
        )

    for configuration in sorted(CONFIGURATIONS):
        for enabled in (True, False):
            selected = [p for (e, c, _), p in points.items() if e == enabled and c == configuration]
            for policy in policies:
                vals = [value(p, policy) for p in selected]
                summaries.append(
                    {
                        "configuration": configuration,
                        "learning": "ON" if enabled else "OFF",
                        "policy": policy,
                        "environment_count": len(vals),
                        "grid_macro_mean": sum(vals) / len(vals),
                        "grid_min": min(vals),
                        "grid_max": max(vals),
                        "interpretation": "descriptive equal-weight finite grid; not population prevalence",
                    }
                )

    # Paired algebraic decomposition of organization and learning effects.
    for spec in specs:
        for configuration in sorted(CONFIGURATIONS):
            on = points[(True, configuration, spec)]
            off = points[(False, configuration, spec)]
            for policy in policies:
                interactions.append(
                    {
                        "interaction": "learning_value_by_policy",
                        "environment": spec.identifier,
                        "nu": spec.nu,
                        "chi": spec.chi,
                        "rho": spec.rho,
                        "configuration": configuration,
                        "policy": policy,
                        "value_ON_minus_OFF": value(on, policy) - value(off, policy),
                    }
                )
            for policy in ("GREEDY_USE", "JOINT_DP"):
                on_adv = value(on, policy) - value(on, "FIXED_BEST")
                off_adv = value(off, policy) - value(off, "FIXED_BEST")
                interactions.append(
                    {
                        "interaction": "learning_by_organization_advantage",
                        "environment": spec.identifier,
                        "nu": spec.nu,
                        "chi": spec.chi,
                        "rho": spec.rho,
                        "configuration": configuration,
                        "policy": policy,
                        "organization_advantage_ON": on_adv,
                        "organization_advantage_OFF": off_adv,
                        "difference_in_advantage_ON_minus_OFF": on_adv - off_adv,
                    }
                )

    OUTPUT.mkdir(parents=True)
    table_paths = {
        "policy_ledger": OUTPUT / "policy_ledger.csv",
        "configuration_summary": OUTPUT / "configuration_summary.csv",
        "organizational_regimes": OUTPUT / "organizational_regimes.csv",
        "organization_learning_interactions": OUTPUT / "organization_learning_interactions.csv",
    }
    write_csv(ledger, table_paths["policy_ledger"])
    write_csv(summaries, table_paths["configuration_summary"])
    write_csv(regimes, table_paths["organizational_regimes"])
    write_csv(interactions, table_paths["organization_learning_interactions"])
    summary = {
        "experiment_id": "configuration_environment_factorial_v01_fixed",
        "scope": "deterministic finite-grid factorial using frozen v0/v0.1 physics and transitions",
        "grid_levels": list(GRID_LEVELS),
        "environment_count": len(specs),
        "configuration_count": len(CONFIGURATIONS),
        "organization_policies": list(policies),
        "learning_conditions": ["ON", "OFF"],
        "horizon": 16,
        "policy_evaluations": len(ledger),
        "configuration_environment_learning_cells": len(points),
        "fixedbest_dominance_roundoff_count": sum(
            r["dominance_roundoff_within_frozen_tolerance"] for r in regimes
        ),
        "fixedbest_dominance_tolerance": EXACT_TOL,
        "finite_grid_means_are_not_population_prevalence": True,
        "artifacts": {key: path.name for key, path in table_paths.items()},
    }
    summary_path = OUTPUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "protocol": "HLS CE-03 configuration × environment × organization × learning factorial v0.1",
        "command": "python experiments/synthetic/prototype_v01/run_fixed_organization_factorial.py",
        "repository_commit_at_run": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_dirty_at_run": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "execution_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in SOURCES},
        "historical_reference_sha256": {
            name: sha256(HISTORICAL / name) for name in ("points.csv", "manifest.json", "summary.json")
        },
        "parameters": {
            "configurations": list(CONFIGURATIONS),
            "environment_grid_per_axis": list(GRID_LEVELS),
            "environment_count": len(specs),
            "policies": list(policies),
            "learning_scale_on": ENABLED_LEARNING_SCALE,
            "learning_scale_off": 0.0,
            "horizon": 16,
            "reward": "existing v0 individual competence reward, summed over tasks",
            "transition": "existing v0 canonical MIS learning_increment",
            "fixed_best": "retrospective maximum over three constant-agent assignments; not online",
            "dominance_check": f"FIXED_BEST <= JOINT_DP + {EXACT_TOL} (frozen EXACT_TOL)",
        },
        "row_counts": {
            "policy_evaluations": len(ledger),
            "cells": len(points),
            "environment_configuration_pairs": len(specs) * len(CONFIGURATIONS),
        },
        "output_sha256": {key: sha256(path) for key, path in table_paths.items()}
        | {"summary.json": sha256(summary_path)},
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
