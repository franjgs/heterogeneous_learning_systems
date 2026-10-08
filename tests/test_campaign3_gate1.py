from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "diagnostics" / "campaign3_gate1"
PILOT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
SPEC = importlib.util.spec_from_file_location("campaign3_gate1_analyze", ROOT / "experiments" / "synthetic" / "campaign3_gate1" / "analyze.py")
assert SPEC and SPEC.loader
ANALYZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZE)
CONTINUATIONS, MODES = ANALYZE.CONTINUATIONS, ANALYZE.MODES
deterministic_ranking = ANALYZE.deterministic_ranking


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_design_and_source_integrity() -> None:
    freeze = json.loads((OUT / "pre_analysis_gate1.json").read_text())
    manifest = json.loads((OUT / "analysis_manifest.json").read_text())
    assert freeze["team_ids"] == ["G00", "G04", "G05", "G07", "F01", "F02", "F03", "F04"]
    assert len(freeze["kernel_ids"]) == 21
    assert (freeze["histories"], freeze["eligible_states"]) == (840, 2520)
    assert freeze["initial_modes"] == list(MODES)
    assert freeze["continuation_probes"] == list(CONTINUATIONS)
    assert manifest["source_branch_sha256"] == sha256(PILOT / "counterfactual_branch_returns.csv.gz")
    assert (manifest["branch_rows_used"], manifest["eligible_states"]) == (20160, 2520)
    assert manifest["state_source"] == "h ~ d_Q11"


def test_all_eligible_states_modes_and_continuations() -> None:
    branches = pd.read_csv(PILOT / "counterfactual_branch_returns.csv.gz")
    eligible = branches[(branches.problem_index == 1) & (branches.ell == 11)]
    assert len(eligible) == 2520 * 4 * 2
    assert eligible.state_id.nunique() == 2520
    assert set(eligible.initial_mode) == set(MODES)
    assert set(eligible.continuation) == set(CONTINUATIONS)
    assert not eligible.duplicated(["state_id", "initial_mode", "continuation"]).any()


def test_tau_and_temporal_accumulation_are_frozen() -> None:
    diagnostics = pd.read_csv(OUT / "gate1_state_diagnostics.csv")
    assert set(diagnostics.problem_index) == {1}
    assert set(diagnostics.tau) == {34, 35, 36}
    assert (diagnostics.tau == 36 - (diagnostics.decision - 1)).all()
    assert diagnostics.groupby("tau").size().to_dict() == {34: 840, 35: 840, 36: 840}


def test_advantage_best_mode_and_regret_reconstruction() -> None:
    tolerance = json.loads((OUT / "pre_analysis_gate1.json").read_text())["mode_tie_break"]["tolerance"]
    branches = pd.read_csv(PILOT / "counterfactual_branch_returns.csv.gz")
    branches = branches[(branches.problem_index == 1) & (branches.ell == 11)]
    wide = branches.pivot(index="state_id", columns=["continuation", "initial_mode"], values="G")
    diagnostics = pd.read_csv(OUT / "gate1_state_diagnostics.csv").set_index("state_id")
    for state_id in wide.index:
        values = {c: {m: wide.loc[state_id, (c, m)] for m in MODES} for c in CONTINUATIONS}
        best = {c: deterministic_ranking(values[c], tolerance)[0] for c in CONTINUATIONS}
        row = diagnostics.loc[state_id]
        for continuation in CONTINUATIONS:
            for mode in ("Q10", "Q01", "Q11"):
                assert np.isclose(row[f"A_{mode}_{continuation}"], values[continuation][mode] - values[continuation]["Q00"])
        assert row.best_Q00_continuation == best["Q00"]
        assert row.best_Q11_continuation == best["Q11"]
        assert np.isclose(row.R_00_to_11, values["Q11"][best["Q11"]] - values["Q11"][best["Q00"]])
        assert np.isclose(row.R_11_to_00, values["Q00"][best["Q00"]] - values["Q00"][best["Q11"]])


def test_tie_order_bootstrap_and_firewalls() -> None:
    assert deterministic_ranking({mode: 1.0 for mode in MODES}, 1e-10) == MODES
    near = {"Q00": 1.0, "Q10": 1.0 + 5e-11, "Q01": 0.0, "Q11": -1.0}
    assert deterministic_ranking(near, 1e-10)[:2] == ("Q00", "Q10")
    freeze = json.loads((OUT / "pre_analysis_gate1.json").read_text())
    manifest = json.loads((OUT / "analysis_manifest.json").read_text())
    classification = json.loads((OUT / "gate1_classification.json").read_text())
    indices = np.load(PILOT / "bootstrap_history_indices.npy", allow_pickle=False)
    assert indices.shape == (2000, 840)
    assert freeze["uncertainty"]["cluster_unit"] == "complete base history/seed"
    assert freeze["uncertainty"]["B"] == 2000
    assert not manifest["normalized_regret_metric"] and manifest["materiality_threshold"] is None
    assert not manifest["heldout_execution"] and not manifest["gate_2"]
    assert not manifest["predictor_or_metacontroller_training"]
    assert classification["classification"] == "PARTIAL LOCAL STRUCTURE"
    assert classification["decision"] == "GO CONDITIONED TO C3.2"


def test_output_hashes() -> None:
    manifest = json.loads((OUT / "analysis_manifest.json").read_text())
    for name, expected in manifest["sha256"].items():
        assert sha256(OUT / name) == expected
