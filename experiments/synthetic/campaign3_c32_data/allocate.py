"""Freeze the C3.2-DATA one-state-per-history allocation before labels exist."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE2 = ROOT / "results" / "diagnostics" / "campaign3_gate2"
OUT = ROOT / "results" / "foundations" / "campaign3_c32_data"
SEED = "campaign3_c32_data_clock_v1:20261010"
PARTITIONS = {0: "TRAIN", 1: "TRAIN", 2: "TRAIN", 3: "VALIDATION", 4: "DEVELOPMENT_TEST"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rank(history_id: str) -> str:
    return hashlib.sha256(f"{SEED}|{history_id}".encode()).hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="refuse by default to overwrite a frozen allocation")
    args = parser.parse_args()
    assignment = OUT / "history_clock_assignment.csv"
    manifest = OUT / "allocation_manifest.json"
    if assignment.exists() or manifest.exists():
        if not args.force:
            raise RuntimeError("frozen allocation already exists; refusing overwrite")
        raise RuntimeError("--force is intentionally disabled for the frozen allocation")
    import pandas as pd

    histories_path = GATE2 / "factual_histories.csv.gz"
    states_path = GATE2 / "factual_states.csv.gz"
    histories = pd.read_csv(histories_path)
    states = pd.read_csv(states_path, usecols=["history_id", "clock", "state_id"])
    if len(histories) != 10_500 or len(states) != 378_000:
        raise RuntimeError("Gate 2 factual inputs have unexpected counts")
    if histories.history_id.nunique() != 10_500 or states.groupby("history_id").size().ne(36).any():
        raise RuntimeError("one complete 36-state trajectory is required per history")
    if set(histories.replicate) != set(PARTITIONS):
        raise RuntimeError("expected factual replicate identifiers 0..4")
    histories = histories.copy()
    histories["partition"] = histories.replicate.map(PARTITIONS)
    histories["_rank"] = histories.history_id.map(rank)
    histories["selected_clock"] = 0
    for partition, group in histories.groupby("partition", sort=False):
        ordered = group.sort_values(["_rank", "history_id"])
        histories.loc[ordered.index, "selected_clock"] = [(index % 36) + 1 for index in range(len(ordered))]
    state_lookup = states.set_index(["history_id", "clock"])["state_id"]
    histories["selected_state_id"] = [
        int(state_lookup[(row.history_id, row.selected_clock)]) for row in histories.itertuples()
    ]
    columns = ["history_id", "team_id", "kernel_id", "behavior", "replicate", "partition", "selected_clock", "selected_state_id"]
    result = histories[columns].sort_values("history_id").reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=False)
    result.to_csv(assignment, index=False, lineterminator="\n")
    partition_counts = result.partition.value_counts().to_dict()
    clock_counts = {name: group.selected_clock.value_counts().sort_index().to_dict() for name, group in result.groupby("partition")}
    by_dimension = {
        dimension: {
            partition: group.groupby(dimension).size().to_dict()
            for partition, group in result.groupby("partition")
        }
        for dimension in ("behavior", "team_id", "kernel_id", "replicate")
    }
    invariants = {
        "allocation_rows": len(result), "one_row_per_history": result.history_id.nunique() == len(result),
        "partition_counts": partition_counts, "clock_counts": clock_counts,
        "state_lookup_unique": result.selected_state_id.nunique() == len(result),
        "expected_partition_counts": {"TRAIN": 6300, "VALIDATION": 2100, "DEVELOPMENT_TEST": 2100},
    }
    if partition_counts != invariants["expected_partition_counts"]:
        raise RuntimeError("partition count mismatch")
    if any(count != 175 for count in clock_counts["TRAIN"].values()):
        raise RuntimeError("TRAIN clock balance mismatch")
    if any(count not in (58, 59) for partition in ("VALIDATION", "DEVELOPMENT_TEST") for count in clock_counts[partition].values()):
        raise RuntimeError("validation/test clock balance mismatch")
    dump(manifest, {
        "artifact_type": "campaign3_c32_data_frozen_allocation", "protocol_version": "C3.2-DATA-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "randomization": {"method": "SHA-256 hash permutation of history_id", "seed": SEED, "clocks": list(range(1, 37)), "cyclic_assignment": True},
        "replicate_partition": {str(key): value for key, value in PARTITIONS.items()},
        "gate2_input_sha256": {"factual_histories.csv.gz": digest(histories_path), "factual_states.csv.gz": digest(states_path)},
        "assignment_sha256": digest(assignment), "invariants": invariants, "residual_associations": by_dimension,
        "cross_behavior_dependence": "Gate 2 sources share problem/noise streams within team_id/kernel_id/replicate; partitioning by replicate keeps each paired-source cluster in one partition.",
        "targets_generated": 0,
    })
    print(json.dumps(invariants, sort_keys=True))


if __name__ == "__main__":
    main()
