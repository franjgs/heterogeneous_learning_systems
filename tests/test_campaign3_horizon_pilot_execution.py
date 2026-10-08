"""Result-integrity controls for the initial frozen J=12 horizon pilot."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[1]
OUT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
FREEZE = ROOT / "results" / "foundations" / "campaign3_horizon_pilot" / "pre_execution_horizon_pilot.json"
EXPECTED_TEAMS = ("G00", "G04", "G05", "G07", "F01", "F02", "F03", "F04")
EXPECTED_KERNELS = (
    "K01", "K02", "K03", "K05", "K06", "K07", "K10", "K11", "K13", "K15",
    "K16", "K17", "K20", "K21", "K23", "K25", "K26", "K27", "K31", "K32", "K33",
)


def load(name):
    return json.loads((OUT / name).read_text())


def rows(name):
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_execution_counts_factorial_and_factual_source():
    validation = load("raw_validation.json")
    assert validation["passed"] is True
    assert validation["counts"] == {"histories": 840, "states": 30240, "branches": 1572480, "pairs": 1179360}
    assert validation["cells"] == 168 and validation["replicates_per_cell"] == 5
    assert validation["replicate_indices"] == list(range(5))
    assert validation["J"] == 12 and validation["factual_source"] == "Q11"
    assert tuple(validation["team_ids"]) == EXPECTED_TEAMS
    assert tuple(validation["kernel_ids"]) == EXPECTED_KERNELS


def test_raw_integrity_crn_outcome_boundary_and_no_zero_imputation():
    validation = load("raw_validation.json")
    assert validation["max_factual_mu_sum_error"] == 0.0
    assert validation["max_first_epsilon_error"] == 0.0
    assert validation["max_observation_construction_error"] <= 3e-16
    assert validation["max_pair_reconstruction_error"] == 0.0
    assert validation["all_eligible_states_treated"] is True
    assert validation["problem_boundary_censoring_valid"] is True
    assert validation["zero_imputation"] is False
    for label, expected in validation["raw_artifact_sha256"].items():
        filename = {"histories": "factual_histories.csv", "states": "factual_states.csv.gz",
                    "branches": "counterfactual_branch_returns.csv.gz", "pairs": "counterfactual_pairs.csv.gz"}[label]
        assert digest(OUT / filename) == expected


def test_nested_windows_available_state_counts_and_l11_early_state_only():
    common = rows("common_support_summary.csv")
    available = rows("available_state_summary.csv")
    assert {int(row["window_L"]) for row in common} == {2, 5, 11}
    states = {2: 25200, 5: 17640, 11: 2520}
    problems = {2: list(range(1, 11)), 5: list(range(1, 8)), 11: [1]}
    for row in common:
        window = int(row["window_L"])
        assert int(row["histories"]) == 840
        assert int(row["factual_states"]) == states[window]
        assert json.loads(row["contributing_problem_indices"]) == problems[window]
        if window == 11:
            assert row["window_label"] == "EARLY-STATE DIAGNOSTIC"
    for row in available:
        ell = int(row["ell"])
        assert row["analysis"] == "SECONDARY AVAILABLE-STATE ANALYSIS"
        assert int(row["factual_states"]) == 2520 * (12 - ell)
        assert json.loads(row["contributing_problem_indices"]) == list(range(1, 13 - ell))


def test_bootstrap_is_history_level_frozen_and_reproducible():
    manifest = load("analysis_manifest.json")
    indices = np.load(OUT / "bootstrap_history_indices.npy", allow_pickle=False)
    expected = np.random.default_rng(20261013).integers(0, 840, size=(2000, 840))
    assert indices.shape == (2000, 840)
    assert np.array_equal(indices, expected)
    assert manifest["bootstrap"]["cluster"] == "complete base history/seed"
    assert manifest["bootstrap"]["B"] == 2000 and manifest["bootstrap"]["seed"] == 20261013
    assert digest(OUT / "bootstrap_history_indices.npy") == manifest["bootstrap"]["indices_sha256"]


def test_classification_extension_and_firewalls():
    classification = load("pilot_classification.json")
    decision = load("j12_to_j18_decision.json")
    summary = load("analysis_summary.json")
    assert classification["classification"] == "PERSISTENT BOUNDARY EVOLUTION"
    assert classification["decision"] == "AUTHORIZE J=18; DO NOT INCREASE REPLICATION"
    assert decision["authorization"] == "J=18"
    assert decision["replication_5_to_10_authorized"] is False
    assert decision["frozen_J18_common_support_windows"] == [2, 5, 17]
    assert decision["J18_histories_generated"] == 0
    assert summary["next_step_under_frozen_rule"] == "J=18"
    assert summary["escalation_histories_generated"] == 0
    assert all(load(name).get("heldout_execution", False) is False for name in ("execution_manifest.json", "raw_validation.json", "analysis_manifest.json", "j12_to_j18_decision.json"))
    assert all(load(name).get("gate_1_analysis", False) is False for name in ("execution_manifest.json", "raw_validation.json", "analysis_manifest.json", "j12_to_j18_decision.json"))
    assert all(load(name).get("gate_2_analysis", False) is False for name in ("execution_manifest.json", "raw_validation.json", "analysis_manifest.json", "j12_to_j18_decision.json"))


def test_preregistration_artifact_is_unchanged_and_no_result_overwrite():
    freeze = json.loads(FREEZE.read_text())
    execution = load("execution_manifest.json")
    assert digest(FREEZE) == execution["pre_execution_manifest_sha256"]
    assert execution["preregistration_commit"] == "a984893eb2f5c1f863707d43ae911e5a0c29692d"
    assert freeze["temporal_design"]["nested_common_support_windows"] == [2, 5, 11]


def test_ce_pragmatic_closure_preserves_result_without_temporal_extension():
    closure = load("horizon_pilot_closure.json")
    assert closure["classification_preserved"] == "PERSISTENT BOUNDARY EVOLUTION"
    assert closure["closed_at_J"] == 12
    assert closure["operational_temporal_assessment"]["ell"] == 11
    assert closure["operational_temporal_assessment"]["status"] == "pragmatic C3 development engineering choice"
    assert {"optimal horizon", "saturation horizon", "true horizon", "temporal stabilization"}.issubset(
        closure["operational_temporal_assessment"]["not_claimed"]
    )
    assert closure["J18_histories_generated"] == 0
    assert closure["J24_histories_generated"] == 0
    assert closure["replicates_5_to_9_generated"] == 0
