"""Run the deterministic HLS configuration × environment × policy prototype."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.configuration_environment_policy_v0 import (  # noqa: E402
    CONFIGURATIONS,
    ENVIRONMENTS,
    configuration_rankings,
    evaluate_matrix,
    total_budget,
)


OUTPUT = ROOT / "results" / "foundations" / "configuration_environment_policy_v0"
MODULE = ROOT / "src" / "hls" / "configuration_environment_policy_v0.py"
RUNNER = Path(__file__).resolve()
LEARNING_SCALE = 0.5


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _write_csv(rows: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(*, output: Path = OUTPUT, learning_scale: float = LEARNING_SCALE) -> dict[str, object]:
    """Write primary learning and exact no-development ablation tables."""
    enabled = evaluate_matrix(learning_scale=learning_scale, development_enabled=True)
    disabled = evaluate_matrix(learning_scale=learning_scale, development_enabled=False)
    matrix_rows: list[dict[str, object]] = []
    management_rows: list[dict[str, object]] = []
    for condition, evaluations in (("learning_enabled", enabled), ("learning_disabled", disabled)):
        for point in evaluations:
            for policy, evaluation in (("GREEDY_USE", point.greedy), ("JOINT_DP", point.joint_dp)):
                matrix_rows.append(
                    {
                        "condition": condition,
                        "configuration": point.configuration,
                        "environment": point.environment,
                        "policy": policy,
                        "value": evaluation.value,
                        "first_actions_0based": json.dumps(evaluation.first_actions),
                        "greedy_tie_steps": evaluation.greedy_tie_steps,
                    }
                )
            management_rows.append(
                {
                    "condition": condition,
                    "configuration": point.configuration,
                    "environment": point.environment,
                    "J_GREEDY": point.greedy.value,
                    "J_DP": point.joint_dp.value,
                    "Delta_J_management": point.management_value,
                }
            )
    output.mkdir(parents=True, exist_ok=True)
    matrix_path = output / "matrix.csv"
    management_path = output / "management_value.csv"
    _write_csv(matrix_rows, matrix_path)
    _write_csv(management_rows, management_path)
    summary = {
        "experiment_id": "configuration_environment_policy_v0",
        "scope": "deterministic fully-known 3-agent x 2-capability diagnostic; not a new HLS mechanism",
        "learning_law": "canonical MIS d_eta(s)=min(eta*(1-s)^2, 1-s)",
        "learning_scale_enabled": learning_scale,
        "environments": {name: list(sequence) for name, sequence in ENVIRONMENTS.items()},
        "configurations": {name: [list(row) for row in state] for name, state in CONFIGURATIONS.items()},
        "budgets": {name: total_budget(state) for name, state in CONFIGURATIONS.items()},
        "rankings": {
            "learning_enabled": {
                policy: configuration_rankings(enabled, policy) for policy in ("GREEDY_USE", "JOINT_DP")
            },
            "learning_disabled": {
                policy: configuration_rankings(disabled, policy) for policy in ("GREEDY_USE", "JOINT_DP")
            },
        },
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "command": "python experiments/synthetic/prototype_v0/run_configuration_environment_policy.py",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "module_sha256": _sha256(MODULE),
        "runner_sha256": _sha256(RUNNER),
        "matrix_sha256": _sha256(matrix_path),
        "management_value_sha256": _sha256(management_path),
        "summary_sha256": _sha256(summary_path),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--learning-scale", type=float, default=LEARNING_SCALE)
    args = parser.parse_args()
    summary = run(output=args.output, learning_scale=args.learning_scale)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
