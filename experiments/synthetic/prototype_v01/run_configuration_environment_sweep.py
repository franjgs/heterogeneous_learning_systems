"""Run the deterministic known-environment configuration × environment sweep."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.configuration_environment_policy_v0 import CONFIGURATIONS, total_budget  # noqa: E402
from hls.configuration_environment_policy_v01 import (  # noqa: E402
    ENABLED_LEARNING_SCALE,
    GRID_LEVELS,
    argmax_configurations,
    environment_specs,
    evaluate_sweep,
    paired_development_rows,
    pairwise_interactions,
)


OUTPUT = ROOT / "results" / "foundations" / "configuration_environment_performance_v01"
MODULES = (
    ROOT / "src" / "hls" / "configuration_environment_policy_v0.py",
    ROOT / "src" / "hls" / "configuration_environment_policy_v01.py",
)
RUNNER = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _write_csv(rows: tuple[dict[str, object], ...], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _management_map(rows: tuple[dict[str, object], ...]) -> tuple[dict[str, object], ...]:
    answer = []
    for row in rows:
        answer.append(
            {
                "environment": row["environment"],
                "nu": row["nu"],
                "chi": row["chi"],
                "rho": row["rho"],
                "configuration": row["configuration"],
                "M": row["M"],
                "M0": row["M0"],
                "L": row["L"],
            }
        )
    return tuple(answer)


def run(*, output: Path = OUTPUT, learning_scale: float = ENABLED_LEARNING_SCALE) -> dict[str, object]:
    """Execute the full 125-environment, ON/OFF development sweep."""
    specifications = environment_specs()
    enabled = evaluate_sweep(learning_scale=learning_scale, development_enabled=True, specifications=specifications)
    disabled = evaluate_sweep(learning_scale=learning_scale, development_enabled=False, specifications=specifications)
    point_rows = paired_development_rows(enabled, disabled)
    interaction_rows = pairwise_interactions(enabled, disabled)
    map_rows = argmax_configurations(enabled) + argmax_configurations(disabled)
    management_rows = _management_map(point_rows)

    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "points": output / "points.csv",
        "interactions": output / "interactions.csv",
        "regime_maps": output / "regime_maps.csv",
        "management_maps": output / "management_maps.csv",
    }
    _write_csv(point_rows, paths["points"])
    _write_csv(interaction_rows, paths["interactions"])
    _write_csv(map_rows, paths["regime_maps"])
    _write_csv(management_rows, paths["management_maps"])

    ranking_changed = sum(
        enabled_row["ranking"] != disabled_row["ranking"]
        for enabled_row, disabled_row in zip(argmax_configurations(enabled), argmax_configurations(disabled), strict=True)
    )
    summary = {
        "experiment_id": "configuration_environment_performance_v01",
        "scope": "deterministic fully-known characterization ledger; not an HLS mechanism or theorem",
        "baseline_physics": "prototype-v0 reward and canonical MIS transition",
        "learning_scale_enabled": learning_scale,
        "learning_disabled_scale": 0.0,
        "grid": {"nu": list(GRID_LEVELS), "chi": list(GRID_LEVELS), "rho": list(GRID_LEVELS)},
        "horizon": 16,
        "environment_count": len(specifications),
        "configuration_count": len(CONFIGURATIONS),
        "budgets": {name: total_budget(state) for name, state in CONFIGURATIONS.items()},
        "rankings_changed_by_development": ranking_changed,
        "max_management_value": max(row["M"] for row in point_rows),
        "max_learning_value": max(row["L"] for row in point_rows),
        "max_abs_interaction": max(abs(row["I"]) for row in interaction_rows),
        "artifact_files": {name: path.name for name, path in paths.items()},
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "command": "python experiments/synthetic/prototype_v01/run_configuration_environment_sweep.py",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "module_sha256": {path.name: _sha256(path) for path in MODULES},
        "runner_sha256": _sha256(RUNNER),
        "artifact_sha256": {name: _sha256(path) for name, path in paths.items()} | {"summary": _sha256(summary_path)},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
