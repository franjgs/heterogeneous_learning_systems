"""Write checksums and execution provenance after phase-two outputs exist."""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "results" / "soc_triage_classifier_operating_impact"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    files = [
        HERE / "config" / "phase2.json",
        HERE / "config" / "classifier_points.json",
        HERE / "run_phase2.py",
        HERE / "summarize_phase2.py",
        HERE / "test_phase2.py",
        ROOT / "src/hls/ia_l1_l2_simulation.py",
        ROOT / "src/hls/rq1_l1_l2.py",
        ROOT / "src/hls/rq1_allocation.py",
        ROOT / "studies/soc_human_ai_organization/soc_parametric_baseline.py",
        ROOT / "studies/soc_triage_organization_coupling/run_pilot.py",
    ]
    outputs = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "reproducibility_manifest.json")
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()
    except Exception as exc:
        head, status = None, [f"git metadata unavailable: {exc}"]
    data = {
        "study": "SOCTRA-HLS classifier operational impact phase 2",
        "pilot_reference_commit": "df80a78e413c88f7cf22b807e8ee27f4e556a726",
        "repository_head_at_manifest_generation": head,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "input_code_and_configuration_sha256": {str(p.relative_to(ROOT)): sha(p) for p in files if p.exists()},
        "output_sha256": {p.name: sha(p) for p in outputs},
        "workspace_status_at_manifest_generation": status,
        "note": "Workspace status is recorded for provenance; unrelated pre-existing engine edits are not staged by this study. Compare source hashes when reproducing.",
    }
    (OUT / "reproducibility_manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote manifest for {len(outputs)} result artifacts and {len(files)} source/config files")


if __name__ == "__main__":
    main()
