"""Write SHA-256 inventory for the Q1 integration study and local outputs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "studies/soc_triage_hls_q1_integration_evidence"
RESULTS = ROOT / "results/soc_triage_hls_q1_integration_evidence"
TEST = ROOT / "tests/test_soc_triage_hls_q1_fp_workload.py"
OUT = RESULTS / "file_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    files = [
        *[p for p in STUDY.rglob("*") if p.is_file() and "__pycache__" not in p.parts],
        TEST,
        *[p for p in RESULTS.rglob("*") if p.is_file() and p != OUT],
    ]
    entries = []
    for path in sorted(set(files)):
        entries.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    document = {
        "format": "sha256-file-inventory-v1",
        "base_commit": "cc0880d8f56cb3aa05ff29f55f493441ec01206a",
        "branch": "research/soctra-hls-q1-integration-evidence",
        "files": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(entries)} files")


if __name__ == "__main__":
    main()
