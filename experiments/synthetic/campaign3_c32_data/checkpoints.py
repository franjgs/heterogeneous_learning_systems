"""Transactional checkpoint storage for Campaign 3 C3.2."""

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_checkpoint(directory, index, csv_payload, manifest):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    final = directory / f"batch_{index:04d}"

    if final.exists():
        raise RuntimeError(f"Checkpoint already exists: {final}")

    temporary = Path(tempfile.mkdtemp(
        prefix=f".pending_batch_{index:04d}_",
        dir=directory,
    ))

    try:
        csv_path = temporary / "targets.csv"
        manifest_path = temporary / "manifest.json"

        with csv_path.open("wb") as f:
            f.write(csv_payload)
            f.flush()
            os.fsync(f.fileno())

        expected = hashlib.sha256(csv_payload).hexdigest()

        if manifest["targets_sha256"] != expected:
            raise RuntimeError("Manifest hash mismatch")

        with manifest_path.open("w") as f:
            json.dump(manifest, f, sort_keys=True, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())

        os.rename(temporary, final)
        return final

    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def verify_checkpoint(directory, index):
    final = Path(directory) / f"batch_{index:04d}"

    if not final.exists():
        return None

    if not final.is_dir():
        raise RuntimeError(f"Invalid checkpoint path: {final}")

    csv_path = final / "targets.csv"
    manifest_path = final / "manifest.json"

    if not csv_path.is_file() or not manifest_path.is_file():
        raise RuntimeError(f"Incomplete checkpoint: {final}")

    manifest = json.loads(manifest_path.read_text())

    if sha256(csv_path) != manifest.get("targets_sha256"):
        raise RuntimeError(f"Corrupted checkpoint: {final}")

    return csv_path, manifest
