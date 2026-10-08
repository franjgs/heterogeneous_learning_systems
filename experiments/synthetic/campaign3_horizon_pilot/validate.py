"""Integrity validation for the frozen initial J=12 horizon pilot."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
FREEZE = ROOT / "results" / "foundations" / "campaign3_horizon_pilot" / "pre_execution_horizon_pilot.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def reader(path: Path):
    opener = gzip.open if path.name.endswith(".gz") else open
    return opener(path, "rt", encoding="utf-8", newline="")


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    completion = json.loads((OUT / "raw_completion.json").read_text())
    manifest = json.loads((OUT / "execution_manifest.json").read_text())
    expected_counts = {"histories": 840, "states": 30_240, "branches": 1_572_480, "pairs": 1_179_360}
    assert completion["counts"] == expected_counts
    assert completion["expected_counts"] == expected_counts
    for metadata in completion["persisted_file_metadata"].values():
        matching = [path for path in OUT.iterdir() if path.is_file() and digest(path) == metadata["sha256"]]
        assert len(matching) == 1

    expected_teams = tuple(freeze["team_design"]["s_pilot_ids"])
    expected_kernels = tuple(freeze["generator_design"]["phi_pilot_ids"])
    expected_cells = {(team, kernel) for team in expected_teams for kernel in expected_kernels}
    histories = []
    with reader(OUT / "factual_histories.csv") as handle:
        histories = list(csv.DictReader(handle))
    assert len(histories) == 840
    keys = [(row["team_id"], row["kernel_id"], int(row["replicate"])) for row in histories]
    assert len(keys) == len(set(keys))
    assert {(team, kernel) for team, kernel, _ in keys} == expected_cells
    assert Counter((team, kernel) for team, kernel, _ in keys) == Counter({cell: 5 for cell in expected_cells})
    assert {replicate for _, _, replicate in keys} == set(range(5))
    assert all(row["factual_source_policy"] == "Q11" and int(row["J"]) == 12 for row in histories)
    assert all(len(json.loads(row["problems"])) == 12 for row in histories)
    history_by_id = {row["history_id"]: row for row in histories}

    state_count_by_history = Counter()
    state_mu_by_history = defaultdict(float)
    state_epsilon = {}
    state_problem = {}
    with reader(OUT / "factual_states.csv.gz") as handle:
        for row in csv.DictReader(handle):
            history_id = row["history_id"]
            state_id = int(row["state_id"])
            assert row["team_id"] in expected_teams and row["kernel_id"] in expected_kernels
            assert row["factual_action_id"] == row["action_Q11"]
            assert 1 <= int(row["problem_index"]) <= 12 and 1 <= int(row["decision"]) <= 3
            assert int(row["remaining"]) == 4 - int(row["decision"])
            state_count_by_history[history_id] += 1
            state_mu_by_history[history_id] += float(row["mu_true"])
            state_epsilon[state_id] = float(row["epsilon"])
            state_problem[state_id] = int(row["problem_index"])
    assert set(state_count_by_history.values()) == {36}
    max_factual_sum_error = max(
        abs(state_mu_by_history[history_id] - float(row["factual_cumulative_mu_true"]))
        for history_id, row in history_by_id.items()
    )
    assert max_factual_sum_error < 1e-10

    branch_counts = Counter()
    branch_keys = set()
    first_epsilon_error = 0.0
    observation_error = 0.0
    with reader(OUT / "counterfactual_branch_returns.csv.gz") as handle:
        for row in csv.DictReader(handle):
            state_id = int(row["state_id"])
            ell = int(row["ell"])
            expected_max = 12 - state_problem[state_id]
            assert 0 <= ell <= expected_max
            key = (state_id, row["initial_mode"], row["continuation"], ell)
            assert key not in branch_keys
            branch_keys.add(key)
            branch_counts[state_id] += 1
            first_epsilon_error = max(first_epsilon_error, abs(float(row["first_epsilon"]) - state_epsilon[state_id]))
            observation_error = max(
                observation_error,
                abs(float(row["first_observation"]) - float(row["first_mu_true"]) - 0.1 * float(row["first_epsilon"])),
            )
    assert all(branch_counts[state_id] == 8 * (13 - problem) for state_id, problem in state_problem.items())
    assert first_epsilon_error == 0.0
    assert observation_error < 2e-15

    pair_counts = Counter()
    pair_keys = set()
    reconstruction_error = 0.0
    delta_reconstruction = {}
    with reader(OUT / "counterfactual_pairs.csv.gz") as handle:
        for row in csv.DictReader(handle):
            state_id = int(row["state_id"])
            ell = int(row["ell"])
            expected_max = 12 - state_problem[state_id]
            assert 0 <= ell <= expected_max
            key = (state_id, row["mode"], row["continuation"], ell)
            assert key not in pair_keys
            pair_keys.add(key)
            pair_counts[state_id] += 1
            delta = float(row["Delta"])
            reconstruction_error = max(reconstruction_error, abs(delta - (float(row["G_mode"]) - float(row["G_Q00"]))))
            previous_key = (state_id, row["mode"], row["continuation"], ell - 1)
            if ell == 0:
                assert row["delta"] == ""
            else:
                reconstruction_error = max(reconstruction_error, abs(float(row["delta"]) - (delta - delta_reconstruction[previous_key])))
            delta_reconstruction[key] = delta
    assert all(pair_counts[state_id] == 6 * (13 - problem) for state_id, problem in state_problem.items())
    assert reconstruction_error < 2e-14

    assert manifest["heldout_execution"] is False
    assert manifest["gate_1_analysis"] is False and manifest["gate_2_analysis"] is False
    assert manifest["escalation_histories"] == 0 and completion["escalation_histories_generated"] == 0
    validation = {
        "passed": True,
        "counts": expected_counts,
        "cells": len(expected_cells),
        "replicates_per_cell": 5,
        "replicate_indices": list(range(5)),
        "J": 12,
        "factual_source": "Q11",
        "team_ids": list(expected_teams),
        "kernel_ids": list(expected_kernels),
        "max_factual_mu_sum_error": max_factual_sum_error,
        "max_first_epsilon_error": first_epsilon_error,
        "max_observation_construction_error": observation_error,
        "max_pair_reconstruction_error": reconstruction_error,
        "all_eligible_states_treated": True,
        "problem_boundary_censoring_valid": True,
        "zero_imputation": False,
        "heldout_execution": False,
        "gate_1_analysis": False,
        "gate_2_analysis": False,
        "escalation_histories": 0,
        "raw_artifact_sha256": {
            name: digest(OUT / filename)
            for name, filename in {
                "histories": "factual_histories.csv",
                "states": "factual_states.csv.gz",
                "branches": "counterfactual_branch_returns.csv.gz",
                "pairs": "counterfactual_pairs.csv.gz",
            }.items()
        },
    }
    dump(OUT / "raw_validation.json", validation)
    print(json.dumps(validation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
