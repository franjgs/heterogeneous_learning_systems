"""Describe frozen C3.2 allocation clock associations without changing it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "foundations" / "campaign3_c32_data"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    allocation = OUT / "history_clock_assignment.csv"
    target = OUT / "clock_association_diagnostics.json"
    if target.exists():
        raise RuntimeError("refusing to overwrite frozen allocation diagnostic")
    values = pd.read_csv(allocation)
    diagnostics = {}
    for dimension in ("behavior", "team_id", "kernel_id", "replicate"):
        diagnostics[dimension] = {}
        for partition, frame in values.groupby("partition"):
            grouped = frame.groupby([dimension, "selected_clock"]).size().unstack(fill_value=0)
            diagnostics[dimension][partition] = {
                "categories": int(len(grouped)),
                "per_category_clock_min": int(grouped.min(axis=1).min()),
                "per_category_clock_max": int(grouped.max(axis=1).max()),
                "zero_category_clock_cells": int((grouped == 0).sum().sum()),
            }
    payload = {
        "artifact_type": "campaign3_c32_data_allocation_clock_association_diagnostic",
        "allocation_sha256": digest(allocation),
        "description": "Descriptive residual clock associations induced by deterministic identifier-only hash allocation; no target data used and no allocation modified.",
        "partition_replicate_confounding": "intentional: replicate identifiers define partitions, so replicate has one category per partition.",
        "diagnostics": diagnostics,
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
