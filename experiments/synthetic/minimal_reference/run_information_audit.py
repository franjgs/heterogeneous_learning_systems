"""Write reproducible information-audit artifacts for the fixed Phase-V family."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.minimal_reference_information_audit import run_information_audit  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "minimal_reference_information_audit"
AUDIT_PATH = ROOT / "src" / "hls" / "minimal_reference_information_audit.py"
SCENARIO_PATH = ROOT / "src" / "hls" / "minimal_reference_scenario.py"
VALIDATION_PATH = ROOT / "src" / "hls" / "minimal_reference_validation.py"
RUNNER_PATH = Path(__file__).resolve()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate_manifest(output: Path = OUTPUT) -> bool:
    manifest = json.loads((output / "manifest.json").read_text())
    expected = {
        "audit_sha256": _sha256(AUDIT_PATH),
        "scenario_sha256": _sha256(SCENARIO_PATH),
        "validation_sha256": _sha256(VALIDATION_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "summary_sha256": _sha256(output / "summary.json"),
    }
    return all(manifest[key] == value for key, value in expected.items())


def run(output: Path = OUTPUT) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    summary = run_information_audit()
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest = {
        "experiment_id": "minimal_reference_phase_v_information_audit",
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "command": "python experiments/synthetic/minimal_reference/run_information_audit.py",
        "deterministic": True,
        "seeds": None,
        "audit_sha256": _sha256(AUDIT_PATH),
        "scenario_sha256": _sha256(SCENARIO_PATH),
        "validation_sha256": _sha256(VALIDATION_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "summary_sha256": _sha256(summary_path),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    assert validate_manifest(output)
    return summary


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
