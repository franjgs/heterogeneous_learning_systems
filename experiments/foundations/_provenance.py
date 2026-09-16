"""Minimal, deterministic provenance records for foundation experiments."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_output(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def write_result_bundle(
    *,
    root: Path,
    experiment_dir: Path,
    result_dir: Path,
    run_file: Path,
    output: dict,
) -> None:
    """Write metrics plus the uniform manifest required by repository policy."""
    result_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = result_dir / "metrics.json"
    metrics_path.write_text(json.dumps(output, indent=2) + "\n")

    config_path = experiment_dir / "config.json"
    helper_path = Path(__file__).resolve()
    config = json.loads(config_path.read_text())
    experiment_ids = config.get("experiment_ids") or [
        config["experiment_id"]
    ]

    status = output.get("status")
    if status is None:
        status = "REPRODUCED" if output.get("passed") else "FAILED"

    manifest = {
        "schema_version": 1,
        "experiment_ids": experiment_ids,
        "kind": config["kind"],
        "status": status,
        "source_citekeys": config["source_citekeys"],
        "command": (
            f"python {run_file.relative_to(root).as_posix()}"
        ),
        "repository_commit": _git_output(root, "rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(
            _git_output(root, "status", "--porcelain")
        ),
        "config": {
            "path": config_path.relative_to(root).as_posix(),
            "sha256": _sha256(config_path),
        },
        "code": [
            {
                "path": run_file.relative_to(root).as_posix(),
                "sha256": _sha256(run_file),
            },
            {
                "path": helper_path.relative_to(root).as_posix(),
                "sha256": _sha256(helper_path),
            },
        ],
        "results": [
            {
                "path": metrics_path.relative_to(root).as_posix(),
                "sha256": _sha256(metrics_path),
            }
        ],
    }
    (result_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
