"""Run the reproducible finite Phase-V adversarial audit for fixed G3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.g3_information_audit import run_g3_information_audit  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "g3_information_audit"
AUDIT = ROOT / "src" / "hls" / "g3_information_audit.py"
GROUND_TRUTH = ROOT / "src" / "hls" / "g3_organizational_value.py"
RUNNER = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate_manifest(output: Path = OUTPUT) -> bool:
    manifest = json.loads((output / "manifest.json").read_text())
    expected = {
        "audit_sha256": _sha256(AUDIT),
        "ground_truth_sha256": _sha256(GROUND_TRUTH),
        "runner_sha256": _sha256(RUNNER),
        "summary_sha256": _sha256(output / "summary.json"),
    }
    return all(manifest[key] == value for key, value in expected.items())


def run(output: Path = OUTPUT) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    summary = run_g3_information_audit()
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest = {
        "experiment_id": "g3_phase_v_adversarial_information_audit",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "command": "python experiments/synthetic/g3/run_information_audit.py",
        "deterministic": True,
        "audit_sha256": _sha256(AUDIT),
        "ground_truth_sha256": _sha256(GROUND_TRUTH),
        "runner_sha256": _sha256(RUNNER),
        "summary_sha256": _sha256(summary_path),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    assert validate_manifest(output)
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
