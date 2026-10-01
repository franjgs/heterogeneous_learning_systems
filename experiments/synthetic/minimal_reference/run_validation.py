"""Run the deterministic Phase-V validation of the minimal reference scenario."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.minimal_reference_validation import run_validation  # noqa: E402


OUTPUT = ROOT / "results" / "foundations" / "minimal_reference_validation"
MODEL_PATH = ROOT / "src" / "hls" / "minimal_reference_scenario.py"
VALIDATION_PATH = ROOT / "src" / "hls" / "minimal_reference_validation.py"
RUNNER_PATH = Path(__file__).resolve()
BASELINE_COMMIT = "68169de"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _write_csv(rows, path: Path) -> None:
    serialized = [row.as_dict() for row in rows]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(serialized[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(serialized)


def validate_manifest(output: Path = OUTPUT) -> bool:
    """Validate the generated artifact hashes without rerunning the sweep."""
    manifest = json.loads((output / "manifest.json").read_text())
    expected = {
        "model_sha256": _sha256(MODEL_PATH),
        "validation_sha256": _sha256(VALIDATION_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "summary_sha256": _sha256(output / "summary.json"),
        "worlds_sha256": _sha256(output / "worlds.csv"),
    }
    return all(manifest[key] == value for key, value in expected.items())


def run(output: Path = OUTPUT) -> dict[str, object]:
    """Write machine-readable rows, summary, and provenance manifest."""
    output.mkdir(parents=True, exist_ok=True)
    rows, summary = run_validation()
    summary = dict(summary)
    worlds_path = output / "worlds.csv"
    summary_path = output / "summary.json"
    _write_csv(rows, worlds_path)
    summary["interpretation"] = {
        "identity": "Delta_J=-L+beta*G is an imported T6 identity checked numerically.",
        "computational_result": "Counts and robustness describe only this declared deterministic grid.",
        "non_claims": [
            "No real-world prevalence inference.",
            "No general HLS policy superiority claim.",
            "No irreducibility claim relative to dynamic programming or optimization.",
            "No universal necessity claim from construction-scoped ablations.",
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest = {
        "experiment_id": "minimal_reference_phase_v",
        "baseline_commit": BASELINE_COMMIT,
        "repository_commit_at_run": _git("rev-parse", "HEAD"),
        "working_tree_dirty_at_run": bool(_git("status", "--porcelain")),
        "command": "python experiments/synthetic/minimal_reference/run_validation.py",
        "deterministic": True,
        "seeds": None,
        "model_sha256": _sha256(MODEL_PATH),
        "validation_sha256": _sha256(VALIDATION_PATH),
        "runner_sha256": _sha256(RUNNER_PATH),
        "summary_sha256": _sha256(summary_path),
        "worlds_sha256": _sha256(worlds_path),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    assert validate_manifest(output)
    return summary


def main() -> None:
    summary = run()
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
