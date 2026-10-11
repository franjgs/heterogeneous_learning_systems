#!/usr/bin/env python3
"""Verify C3.2 counterfactual reproducibility across worker counts."""

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json

import pandas as pd

from experiments.synthetic.campaign3_c32_data import targets


def canonical(rows):
    frame = pd.DataFrame(
        row for state_rows in rows for row in state_rows
    )
    return frame.sort_values(
        ["history_id", "continuation", "initial_mode"]
    ).reset_index(drop=True)


def digest(frame):
    payload = frame.to_csv(index=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main():
    selected = sorted(
        targets.tasks(None, "TRAIN"),
        key=lambda x: str(x["history_id"])
    )[:2]

    print("Evaluando 2 estados con un worker...", flush=True)

    serial = canonical([
        targets.target_rows(task) for task in selected
    ])

    print("Evaluando los mismos estados con dos workers...", flush=True)

    with ProcessPoolExecutor(max_workers=2) as pool:
        parallel = canonical(
            list(pool.map(targets.target_rows, selected))
        )

    pd.testing.assert_frame_equal(
        serial,
        parallel,
        check_exact=True,
    )

    serial_hash = digest(serial)
    parallel_hash = digest(parallel)

    assert serial_hash == parallel_hash

    print(json.dumps({
        "result": "PASS",
        "states": len(selected),
        "conceptual_labels": len(serial),
        "serial_sha256": serial_hash,
        "parallel_sha256": parallel_hash,
        "identical": True,
    }, indent=2))


if __name__ == "__main__":
    main()
