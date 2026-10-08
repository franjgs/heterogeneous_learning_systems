"""Freeze the Campaign 3 horizon-pilot protocol without executing it."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.campaign3_horizon_pilot import (  # noqa: E402
    BOOTSTRAP_REPLICATES,
    BOOTSTRAP_SEED,
    CONTINUATION_PROBES,
    EXOGENOUS_STREAMS,
    FACTUAL_STATE_SOURCE,
    INITIAL_REPLICATES,
    INTERVENTION_MODES,
    J_PILOT,
    KNOWN_PRIOR_C3_SEEDS,
    NESTED_WINDOWS,
    PROTOCOL_ID,
    RESERVED_REPLICATES,
    S_PILOT,
    SEED_DOMAIN,
    TEMPORAL_EXTENSION_SEQUENCE,
    TERMINAL_OUTCOME,
    allocate_seed,
    common_support_problem_indices,
)

TEAM_DIR = ROOT / "results" / "foundations" / "campaign3_team_split"
KERNEL_DIR = ROOT / "results" / "foundations" / "campaign3_generator_split"
OUT = ROOT / "results" / "foundations" / "campaign3_horizon_pilot"
DOC = ROOT / "docs" / "experiments" / "CAMPAIGN_3_HORIZON_PILOT.md"
MODULE = ROOT / "src" / "hls" / "campaign3_horizon_pilot.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    team_csv = TEAM_DIR / "team_split.csv"
    team_manifest_path = TEAM_DIR / "pre_performance_team_split.json"
    kernel_csv = KERNEL_DIR / "kernel_split.csv"
    kernel_manifest_path = KERNEL_DIR / "pre_history_generator_split.json"
    team_manifest = json.loads(team_manifest_path.read_text())
    kernel_manifest = json.loads(kernel_manifest_path.read_text())
    team_rows = read_csv(team_csv)
    kernel_rows = read_csv(kernel_csv)
    teams = {row["team_id"]: row for row in team_rows}
    kernels = {row["kernel_id"]: row for row in kernel_rows}
    phi_pilot = tuple(kernel_manifest["phi_dev"])

    if tuple(team_manifest["s_dev_ids"][:8]) != S_PILOT:
        raise RuntimeError("S_pilot is not the frozen size-eight S_dev prefix")
    if not set(S_PILOT).issubset(team_manifest["s_dev_ids"]):
        raise RuntimeError("S_pilot is not a subset of S_dev")
    if set(S_PILOT) & set(team_manifest["s_heldout_ids"]):
        raise RuntimeError("held-out team entered S_pilot")
    if len(phi_pilot) != 21 or set(phi_pilot) & set(kernel_manifest["phi_heldout"]):
        raise RuntimeError("Phi_pilot does not equal the disjoint frozen Phi_dev")

    design_rows: list[dict[str, object]] = []
    for team_id in S_PILOT:
        team = teams[team_id]
        for kernel_id in phi_pilot:
            kernel = kernels[kernel_id]
            design_rows.append({
                "cell_id": f"{team_id}__{kernel_id}",
                "team_id": team_id,
                **{name: team[name] for name in ("s11", "s12", "s21", "s22", "s31", "s32")},
                "kernel_id": kernel_id,
                **{name: kernel[name] for name in ("alpha_stay", "alpha_move", "alpha_return", "sigma")},
                "histories_initial": 5,
                "histories_reserved_maximum": 10,
                "J_pilot": J_PILOT,
                "factual_state_source": FACTUAL_STATE_SOURCE,
            })
    if len(design_rows) != 168:
        raise RuntimeError("pilot design must contain exactly 168 cells")

    allocations = [
        asdict(allocate_seed(team_id, kernel_id, replicate))
        for team_id in S_PILOT
        for kernel_id in phi_pilot
        for replicate in INITIAL_REPLICATES + RESERVED_REPLICATES
    ]
    seeds = [row["simulator_seed"] for row in allocations]
    identities = [row["base_history_id"] for row in allocations]
    if len(allocations) != 1_680 or len(set(seeds)) != len(seeds) or len(set(identities)) != len(identities):
        raise RuntimeError("seed allocation is incomplete or contains a collision")
    if set(seeds) & KNOWN_PRIOR_C3_SEEDS:
        raise RuntimeError("pilot seed collides with a known prior Campaign 3 seed")

    OUT.mkdir(parents=True, exist_ok=True)
    design_path = OUT / "pilot_design.csv"
    seeds_path = OUT / "seed_allocation.csv"
    write_csv(design_path, design_rows)
    write_csv(seeds_path, allocations)

    source_artifacts = (team_csv, team_manifest_path, kernel_csv, kernel_manifest_path)
    generated_artifacts = (design_path, seeds_path)
    manifest = {
        "artifact_type": "pre_execution_campaign3_horizon_pilot",
        "protocol_id": PROTOCOL_ID,
        "status": "FROZEN LOCALLY; NOT EXECUTED",
        "purpose": "development-only temporal diagnostic",
        "creation_provenance": {
            "team_split_commit": "6eab252661081cd0fa727dd4b2233171e6d63787",
            "generator_split_commit": "ed07fde",
            "source_artifact_sha256": {str(path.relative_to(ROOT)): digest(path) for path in source_artifacts},
            "freeze_code_sha256": {
                str(Path(__file__).resolve().relative_to(ROOT)): digest(Path(__file__).resolve()),
                str(MODULE.relative_to(ROOT)): digest(MODULE),
                str(DOC.relative_to(ROOT)): digest(DOC),
            },
        },
        "team_design": {
            "s_pilot_ids": list(S_PILOT),
            "matrix_source": str(team_csv.relative_to(ROOT)),
            "subset_of_s_dev": True,
            "disjoint_s_heldout": True,
        },
        "generator_design": {
            "phi_pilot_ids": list(phi_pilot),
            "kernel_source": str(kernel_csv.relative_to(ROOT)),
            "equals_phi_dev": True,
            "disjoint_phi_heldout": True,
        },
        "size": {
            "teams": 8,
            "kernels": 21,
            "cells": 168,
            "histories_per_cell_initial": 5,
            "initial_base_histories": 840,
            "histories_per_cell_reserved_maximum": 10,
            "reserved_maximum_base_histories": 1680,
        },
        "temporal_design": {
            "J_pilot": J_PILOT,
            "ell_definition": "future problems included after the current-problem remainder",
            "outcome": "G_t(ell)=sum mu_true from current decision through end of problem j(t)+ell",
            "censoring": "eligible iff j(t)+ell<=J; unavailable future rewards are never imputed as zero",
            "nested_common_support_windows": list(NESTED_WINDOWS),
            "nested_window_problem_indices": {str(L): list(common_support_problem_indices(L)) for L in NESTED_WINDOWS},
            "secondary_analysis": "SECONDARY AVAILABLE-STATE ANALYSIS; support may change with ell",
            "campaign2_two_reward_endpoint_is_distinct": True,
        },
        "policy_semantics": {
            "factual_state_source": FACTUAL_STATE_SOURCE,
            "intervene_at": "all temporally eligible factual decision states",
            "intervention_modes": list(INTERVENTION_MODES),
            "continuation_probes": list(CONTINUATION_PROBES),
            "single_current_decision_intervention": True,
            "eight_combinations_are_not_permanent_strategies": True,
        },
        "seed_allocation": {
            "mapping": "first 32 big-endian bits of SHA-256 over canonical JSON tuple",
            "namespace": PROTOCOL_ID,
            "seed_domain": SEED_DOMAIN,
            "identity_inputs": ["protocol_id", "team_id", "kernel_id", "replicate"],
            "initial_replicate_indices": list(INITIAL_REPLICATES),
            "reserved_replicate_indices": list(RESERVED_REPLICATES),
            "known_prior_c3_seeds_excluded": sorted(KNOWN_PRIOR_C3_SEEDS),
        },
        "crn_semantics": {
            "identifier": "campaign3_horizon_pilot_crn_v1",
            "streams": list(EXOGENOUS_STREAMS),
            "stream_mapping": "mode-independent SHA-256 substream seed from base-history simulator seed and stream name",
            "branch_rule": "clone complete pre-action simulator and exogenous RNG states; restore identical future exogenous states for every initial-mode/continuation branch from the same factual h_t",
            "shared": ["future physical problems", "future observation-noise innovations", "all other exogenous simulator randomness"],
            "endogenous_divergence_preserved": ["actions", "beliefs", "capabilities", "subsequent policy decisions"],
        },
        "uncertainty": {
            "cluster_unit": "complete base history/seed",
            "bootstrap": "nonparametric clustered bootstrap; retain all observations from each resampled history",
            "B": BOOTSTRAP_REPLICATES,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "interval": "two-sided 95% percentile descriptive interval",
            "required_summaries": ["mean Delta + bootstrap interval", "mean delta + bootstrap interval", "median Delta", "distribution quantiles", "history count", "state count"],
        },
        "decision_procedure": {
            "classifications": ["STABILIZATION", "INSUFFICIENT TEMPORAL PRECISION", "PERSISTENT BOUNDARY EVOLUTION", TERMINAL_OUTCOME],
            "replication_escalation": "only global 5->10 for INSUFFICIENT TEMPORAL PRECISION; decision artifact required first; >10 prohibited",
            "temporal_extension_sequence": list(TEMPORAL_EXTENSION_SEQUENCE),
            "extension_rule": "fresh independent histories only; pre-extension artifact and outcome-independent windows required before J=18 or J=24",
            "maximum_J": 24,
            "terminal_outcome": TERMINAL_OUTCOME,
        },
        "firewalls": {
            "gate_1": "no continuation superiority, invariance, regret, or ranking inference",
            "gate_2": "no state/action/outcome coverage claim and no additional factual state-source policies",
            "heldout": "held-out IDs read only for disjointness; no held-out execution, debugging, stopping, interpretation, or horizon choice",
        },
        "execution_status": {
            "pilot_histories_generated": 0,
            "scientific_agents_executed": 0,
            "pilot_rewards_or_outcomes_inspected": 0,
            "heldout_performance_information_accessed": 0,
            "gate_1_started": False,
            "gate_2_started": False,
        },
        "generated_artifact_sha256": {str(path.relative_to(ROOT)): digest(path) for path in generated_artifacts},
    }
    manifest_path = OUT / "pre_execution_horizon_pilot.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
