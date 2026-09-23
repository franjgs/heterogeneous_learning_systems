import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "experiments/pilots/b22_opportunity_value/analyze_portfolio_bridge.py"
SPEC = importlib.util.spec_from_file_location("b22_portfolio_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)


def rescue_fixture(weight=5):
    f0 = {domain: 0.8 for domain in bridge.DOMAINS}
    deep = {domain: 0.7 for domain in bridge.DOMAINS}
    fi = {domain: 0.78 for domain in bridge.DOMAINS}
    fj = {domain: 0.78 for domain in bridge.DOMAINS}
    fij = {domain: 0.9 for domain in bridge.DOMAINS}
    return bridge.bridge_quantities(f0, fi, fj, fij, deep, "photo", "art_painting", 0.0, weight)


def test_delta_v_gamma_H_and_exact_identity():
    result = rescue_fixture()
    assert result["DeltaV_i"] == pytest.approx(-0.02)
    assert result["DeltaV_j"] == pytest.approx(-0.02)
    assert result["DeltaV_ij"] == pytest.approx(0.10)
    assert result["Gamma_oper"] == pytest.approx(0.14)
    assert result["H_i"] == pytest.approx(-0.20)
    assert result["H_j"] == pytest.approx(-0.20)
    assert result["H_ij"] == pytest.approx(0.30)
    assert result["H_ij"] == pytest.approx(result["H_i"] + result["H_j"] + result["B_Gamma"])


def test_portfolio_rescue_is_strict_and_sequential_values_are_consistent():
    result = rescue_fixture()
    assert result["portfolio_rescue"] is True
    assert result["interaction_needed"] is True
    assert result["H_j_given_i"] == pytest.approx(result["H_ij"] - result["H_i"])
    assert result["H_i_given_j"] == pytest.approx(result["H_ij"] - result["H_j"])
    assert result["H_j_given_i"] > 0 and result["H_i_given_j"] > 0
    boundary = rescue_fixture(weight=2)
    assert boundary["H_ij"] == pytest.approx(0.0)
    assert boundary["portfolio_rescue"] is False


def test_frontier_thresholds_characterize_joint_only_value():
    result = rescue_fixture()
    assert result["B_star"] == pytest.approx(2.0)
    assert result["B_star"] < 5
    assert np.isnan(result["B_star_i"]) and np.isnan(result["B_star_j"])


def test_counts_do_not_treat_B_copies_as_distinct_learned_states():
    rows = []
    for weight in bridge.FUTURE_WEIGHTS:
        row = {column: np.nan for column in bridge.RAW_COLUMNS}
        row.update(seed=0, N=25, pair="photo-art_painting", B=weight, c=0.0, portfolio_rescue=True)
        rows.append(row)
    raw = pd.DataFrame(rows, columns=bridge.RAW_COLUMNS)
    audit = {"candidate_analytical_rows": 1800, "candidate_states": 90, "compatible_analytical_rows": 4, "compatible_states": 1}
    summary = bridge.summarize(raw, audit).set_index("metric").value
    assert summary["portfolio_rescues"] == 4
    assert summary["unique_states_with_rescue"] == 1


def test_existing_b21_b22_fail_counterfactual_compatibility():
    b21 = ROOT / "results/pilots/b21_pacs_factorial"
    if not (b21 / "factorial_results.csv").exists():
        pytest.skip("original B2.1 result CSVs are not present in this checkout")
    compatibility, cells, audit = bridge.audit_compatibility(
        b21, ROOT / "results/pilots/b22_opportunity_value"
    )
    assert audit["test_closed"] is True
    assert audit["equal_F0_seeds"] == 0
    assert audit["equal_D_seeds"] == 0
    assert audit["equal_singletons"] == 0
    assert audit["compatible_states"] == 0
    assert not cells.compatible.any()
    assert len(compatibility[compatibility.kind == "singleton"]) == 60


def test_current_analysis_halts_without_training_or_test(tmp_path):
    source = MODULE_PATH.read_text()
    assert "import torch" not in source
    assert "TEST" not in pd.read_csv(ROOT / "results/pilots/b22_opportunity_value/raw_results.csv").columns
    b21 = ROOT / "results/pilots/b21_pacs_factorial"
    if not (b21 / "factorial_results.csv").exists():
        pytest.skip("original B2.1 result CSVs are not present in this checkout")
    audit = bridge.run(b21, ROOT / "results/pilots/b22_opportunity_value", tmp_path)
    assert audit["compatible_analytical_rows"] == 0
    assert pd.read_csv(tmp_path / "portfolio_bridge_raw.csv").empty
    assert "HALTED — COUNTERFACTUAL INCOMPATIBILITY" in (tmp_path / "portfolio_bridge.md").read_text()
