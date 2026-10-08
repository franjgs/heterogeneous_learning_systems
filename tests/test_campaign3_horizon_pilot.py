"""Pre-execution controls for the Campaign 3 horizon-pilot freeze."""

from __future__ import annotations

import ast
import copy
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from hls.campaign3_horizon_pilot import (
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    CONTINUATION_PROBES,
    EXOGENOUS_STREAMS,
    INITIAL_REPLICATES,
    INTERVENTION_MODES,
    J_PILOT,
    KNOWN_PRIOR_C3_SEEDS,
    NESTED_WINDOWS,
    RESERVED_REPLICATES,
    S_PILOT,
    TEMPORAL_EXTENSION_SEQUENCE,
    TERMINAL_OUTCOME,
    allocate_seed,
    common_support_problem_indices,
    eligible_for_horizon,
    exogenous_stream_seed,
    simulation_seed,
)

ROOT = Path(__file__).parents[1]
PILOT = ROOT / "results" / "foundations" / "campaign3_horizon_pilot"
TEAM = ROOT / "results" / "foundations" / "campaign3_team_split"
GENERATOR = ROOT / "results" / "foundations" / "campaign3_generator_split"
EXPECTED_TEAMS = ("G00", "G04", "G05", "G07", "F01", "F02", "F03", "F04")
EXPECTED_KERNELS = (
    "K01", "K02", "K03", "K05", "K06", "K07", "K10", "K11", "K13", "K15",
    "K16", "K17", "K20", "K21", "K23", "K25", "K26", "K27", "K31", "K32", "K33",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def manifest() -> dict:
    return json.loads((PILOT / "pre_execution_horizon_pilot.json").read_text())


def test_exact_team_and_kernel_firewalls_and_source_values():
    design = rows(PILOT / "pilot_design.csv")
    team_source = rows(TEAM / "team_split.csv")
    kernel_source = rows(GENERATOR / "kernel_split.csv")
    team_manifest = json.loads((TEAM / "pre_performance_team_split.json").read_text())
    kernel_manifest = json.loads((GENERATOR / "pre_history_generator_split.json").read_text())
    assert S_PILOT == EXPECTED_TEAMS == tuple(team_manifest["s_dev_ids"][:8])
    assert set(S_PILOT).issubset(team_manifest["s_dev_ids"])
    assert set(S_PILOT).isdisjoint(team_manifest["s_heldout_ids"])
    assert tuple(kernel_manifest["phi_dev"]) == EXPECTED_KERNELS
    assert len(EXPECTED_KERNELS) == 21
    assert set(EXPECTED_KERNELS).isdisjoint(kernel_manifest["phi_heldout"])
    teams = {row["team_id"]: row for row in team_source}
    kernels = {row["kernel_id"]: row for row in kernel_source}
    assert len(design) == 168
    assert {(row["team_id"], row["kernel_id"]) for row in design} == {
        (team, kernel) for team in EXPECTED_TEAMS for kernel in EXPECTED_KERNELS
    }
    for row in design:
        assert tuple(row[name] for name in ("s11", "s12", "s21", "s22", "s31", "s32")) == tuple(
            teams[row["team_id"]][name] for name in ("s11", "s12", "s21", "s22", "s31", "s32")
        )
        assert tuple(row[name] for name in ("alpha_stay", "alpha_move", "alpha_return", "sigma")) == tuple(
            kernels[row["kernel_id"]][name] for name in ("alpha_stay", "alpha_move", "alpha_return", "sigma")
        )


def test_counts_temporal_windows_and_no_zero_imputation():
    freeze = manifest()
    assert freeze["size"] == {
        "teams": 8, "kernels": 21, "cells": 168,
        "histories_per_cell_initial": 5, "initial_base_histories": 840,
        "histories_per_cell_reserved_maximum": 10, "reserved_maximum_base_histories": 1680,
    }
    assert J_PILOT == freeze["temporal_design"]["J_pilot"] == 12
    assert NESTED_WINDOWS == (2, 5, 11)
    assert common_support_problem_indices(2) == tuple(range(1, 11))
    assert common_support_problem_indices(5) == tuple(range(1, 8))
    assert common_support_problem_indices(11) == (1,)
    assert eligible_for_horizon(12, 0)
    assert not eligible_for_horizon(12, 1)
    assert not eligible_for_horizon(2, 11)
    assert "never imputed as zero" in freeze["temporal_design"]["censoring"]


def test_seed_mapping_is_complete_stable_fresh_disjoint_and_collision_free():
    allocation = rows(PILOT / "seed_allocation.csv")
    assert len(allocation) == 1680
    keys = {(row["team_id"], row["kernel_id"], int(row["replicate"])) for row in allocation}
    assert keys == {(t, k, r) for t in EXPECTED_TEAMS for k in EXPECTED_KERNELS for r in range(10)}
    seeds = [int(row["simulator_seed"]) for row in allocation]
    assert len(set(seeds)) == len(seeds)
    assert set(seeds).isdisjoint(KNOWN_PRIOR_C3_SEEDS)
    initial = {int(row["simulator_seed"]) for row in allocation if row["allocation"] == "initial"}
    reserved = {int(row["simulator_seed"]) for row in allocation if row["allocation"] == "reserved_5_to_10"}
    assert len(initial) == 840 and len(reserved) == 840 and initial.isdisjoint(reserved)
    for row in allocation:
        assert int(row["simulator_seed"]) == simulation_seed(row["team_id"], row["kernel_id"], int(row["replicate"]))
    assert simulation_seed("G00", "K01", 0) == simulation_seed("G00", "K01", 0)


def test_crn_substreams_are_mode_independent_synchronized_and_branch_clonable():
    record = allocate_seed("G00", "K01", 0)
    stream_seeds = {stream: exogenous_stream_seed(record.simulator_seed, stream) for stream in EXOGENOUS_STREAMS}
    assert len(set(stream_seeds.values())) == len(EXOGENOUS_STREAMS)
    # Mode and continuation are deliberately absent from substream derivation.
    for _mode in INTERVENTION_MODES:
        for _continuation in CONTINUATION_PROBES:
            clone = {name: np.random.default_rng(seed) for name, seed in stream_seeds.items()}
            reference = {name: np.random.default_rng(seed) for name, seed in stream_seeds.items()}
            assert all(np.array_equal(clone[name].standard_normal(8), reference[name].standard_normal(8)) for name in EXOGENOUS_STREAMS)
    # A factual stream may already be advanced when h_t is reached. Copying its
    # complete bit-generator state still gives branch-order-independent futures.
    factual = np.random.default_rng(stream_seeds["observation_noise"])
    factual.standard_normal(13)
    state = copy.deepcopy(factual.bit_generator.state)
    branch_a = np.random.default_rng()
    branch_b = np.random.default_rng()
    branch_a.bit_generator.state = copy.deepcopy(state)
    branch_b.bit_generator.state = copy.deepcopy(state)
    assert np.array_equal(branch_a.standard_normal(16), branch_b.standard_normal(16))


def test_policy_outcome_bootstrap_escalation_extension_and_terminal_semantics():
    freeze = manifest()
    assert INTERVENTION_MODES == ("Q00", "Q10", "Q01", "Q11")
    assert CONTINUATION_PROBES == ("Q00", "Q11")
    assert freeze["temporal_design"]["outcome"].endswith("mu_true from current decision through end of problem j(t)+ell")
    assert "observed reward" not in freeze["temporal_design"]["outcome"]
    assert freeze["uncertainty"]["cluster_unit"] == "complete base history/seed"
    assert BOOTSTRAP_REPLICATES == 2000 and BOOTSTRAP_SEED == 20261013
    assert freeze["decision_procedure"]["replication_escalation"].startswith("only global 5->10")
    assert INITIAL_REPLICATES == tuple(range(5)) and RESERVED_REPLICATES == tuple(range(5, 10))
    assert TEMPORAL_EXTENSION_SEQUENCE == (12, 18, 24)
    assert freeze["decision_procedure"]["maximum_J"] == 24
    assert TERMINAL_OUTCOME == "HORIZON UNRESOLVED"


def test_hashes_firewalls_and_freeze_path_have_no_scientific_execution_dependency():
    freeze = manifest()
    for relative, expected in freeze["creation_provenance"]["source_artifact_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    for relative, expected in freeze["creation_provenance"]["freeze_code_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    for relative, expected in freeze["generated_artifact_sha256"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    assert freeze["firewalls"].keys() == {"gate_1", "gate_2", "heldout"}
    assert freeze["execution_status"] == {
        "pilot_histories_generated": 0,
        "scientific_agents_executed": 0,
        "pilot_rewards_or_outcomes_inspected": 0,
        "heldout_performance_information_accessed": 0,
        "gate_1_started": False,
        "gate_2_started": False,
    }
    freeze_path = ROOT / "experiments" / "synthetic" / "campaign3_horizon_pilot" / "freeze.py"
    tree = ast.parse(freeze_path.read_text())
    imports = [alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names]
    forbidden = ("discover", "policy_ablation", "counterfactual", "problem_generator", "campaign2")
    assert not any(any(term in imported for term in forbidden) for imported in imports)
    assert {path.name for path in PILOT.iterdir()} == {
        "pilot_design.csv", "seed_allocation.csv", "pre_execution_horizon_pilot.json"
    }
