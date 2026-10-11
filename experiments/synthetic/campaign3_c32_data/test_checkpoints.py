"""Tests for transactional checkpoint publication."""

import hashlib
import json
import tempfile
from pathlib import Path

from experiments.synthetic.campaign3_c32_data.checkpoints import (
    write_checkpoint,
    verify_checkpoint,
)


def main():
    payload = b"history_id,raw_mc_G\nh001,1.25\n"

    manifest = {
        "batch_index": 0,
        "targets_sha256": hashlib.sha256(payload).hexdigest(),
    }

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # No existe todavía ningún checkpoint.
        assert verify_checkpoint(root, 0) is None

        # Simulamos una escritura interrumpida.
        abandoned = root / ".pending_batch_0000_interrupted"
        abandoned.mkdir()
        (abandoned / "targets.csv").write_bytes(b"incomplete")

        # El directorio incompleto no debe considerarse válido.
        assert verify_checkpoint(root, 0) is None

        # Publicamos un checkpoint completo.
        final = write_checkpoint(root, 0, payload, manifest)

        assert final.is_dir()

        csv_path, recovered = verify_checkpoint(root, 0)

        assert csv_path.read_bytes() == payload
        assert recovered == manifest

        # No debe permitirse sobrescribir un checkpoint existente.
        try:
            write_checkpoint(root, 0, payload, manifest)
        except RuntimeError:
            pass
        else:
            raise AssertionError("Checkpoint overwrite was allowed")

        print(json.dumps({
            "result": "PASS",
            "atomic_publication": True,
            "abandoned_staging_ignored": True,
            "existing_checkpoint_protected": True,
            "sha256": recovered["targets_sha256"],
        }, indent=2))


if __name__ == "__main__":
    main()
