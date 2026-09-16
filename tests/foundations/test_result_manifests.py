import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "foundations"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_every_foundation_result_has_consistent_manifest():
    result_dirs = sorted(
        path.parent for path in RESULTS.glob("*/metrics.json")
    )
    assert len(result_dirs) == 11

    for result_dir in result_dirs:
        metrics = json.loads((result_dir / "metrics.json").read_text())
        manifest_path = result_dir / "manifest.json"
        assert manifest_path.exists(), result_dir
        manifest = json.loads(manifest_path.read_text())

        assert manifest["schema_version"] == 1
        assert manifest["kind"] == metrics["kind"]
        assert manifest["status"] == metrics["status"]
        assert manifest["source_citekeys"] == metrics["source_citekeys"]
        assert manifest["experiment_ids"] == (
            metrics.get("experiment_ids") or [metrics["experiment_id"]]
        )

        config_path = ROOT / manifest["config"]["path"]
        assert sha256(config_path) == manifest["config"]["sha256"]

        for code in manifest["code"]:
            assert sha256(ROOT / code["path"]) == code["sha256"]
        for result in manifest["results"]:
            assert sha256(ROOT / result["path"]) == result["sha256"]
