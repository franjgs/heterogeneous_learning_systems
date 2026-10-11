#!/usr/bin/env python3
"""Isolated integration test for the C3.2 incremental executor."""

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from experiments.synthetic.campaign3_c32_data import run_incremental as runner


def main():
    original_selected_tasks = runner.selected_tasks
    original_partition_counts = runner.PARTITION_COUNTS.copy()

    two_tasks = original_selected_tasks("TRAIN")[:2]

    with tempfile.TemporaryDirectory(prefix="c32_incremental_test_") as tmp:
        temporary_root = Path(tmp)

        def small_selection(partition):
            assert partition == "TRAIN"
            return two_tasks

        args = SimpleNamespace(
            partition="TRAIN",
            workers=2,
            batch_size=2,
            max_batches=1,
            diagnostic=True,
            dry_run=False,
            consolidate=False,
        )

        with (
            patch.object(runner, "DIAGNOSTIC", temporary_root),
            patch.object(runner, "selected_tasks", small_selection),
        ):
            print("1. Ejecutando dos estados...", flush=True)
            runner.execute(args)

            directory = temporary_root / "train"
            csv_path = directory / "batch_0000" / "targets.csv"
            manifest_path = directory / "batch_0000" / "manifest.json"

            assert csv_path.exists()
            assert manifest_path.exists()

            first_hash = runner.digest(csv_path)

            print("2. Verificando reanudación...", flush=True)
            runner.execute(args)

            assert runner.digest(csv_path) == first_hash

            print("3. Consolidando...", flush=True)
            runner.consolidate(args)

            output = directory / "raw_mc_targets.csv"
            consolidation = directory / "consolidation_manifest.json"

            assert output.exists()
            assert consolidation.exists()

            frame = pd.read_csv(output)
            manifest = json.loads(consolidation.read_text())

            assert len(frame) == 16
            assert frame.selected_state_id.nunique() == 2
            assert not frame.duplicated(
                ["history_id", "initial_mode", "continuation"]
            ).any()

            assert manifest["targets_sha256"] == runner.digest(output)
            assert manifest["selected_states"] == 2
            assert manifest["conceptual_labels"] == 16
            assert manifest["batch_count"] == 1

            print(json.dumps({
                "result": "PASS",
                "states": 2,
                "labels": 16,
                "batch_sha256": first_hash,
                "consolidated_sha256": runner.digest(output),
                "temporary_directory_cleaned": True,
            }, indent=2))


if __name__ == "__main__":
    main()
