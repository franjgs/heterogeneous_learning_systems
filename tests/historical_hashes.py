"""Small helpers for verifying frozen inputs against immutable Git history."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_in_git_history(relative_path: str, expected_sha256: str) -> bool:
    """Return whether a tracked historical blob has the recorded content hash.

    Frozen experiment manifests describe source at execution time. The current
    working file may have evolved; checking Git blobs preserves that distinction
    without changing the frozen manifest or its recorded digest.
    """
    commits = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", relative_path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for commit in commits:
        blob = subprocess.run(
            ["git", "show", f"{commit}:{relative_path}"],
            cwd=ROOT,
            capture_output=True,
        )
        if blob.returncode == 0 and hashlib.sha256(blob.stdout).hexdigest() == expected_sha256:
            return True
    return False


def missing_recorded_artifacts(manifest_path: Path) -> list[str]:
    """List complete artifacts absent from a local historical run manifest."""
    if not manifest_path.is_file():
        return [str(manifest_path)]
    data = json.loads(manifest_path.read_text())
    return sorted(
        artifact_id
        for artifact_id, record in data.get("artifacts", {}).items()
        if record.get("status") == "complete"
        and record.get("path")
        and not Path(record["path"]).is_file()
    )
