from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments/foundations/b3_adaptive_development/analyze.py"
SPEC = importlib.util.spec_from_file_location("b3_adaptive", PATH)
assert SPEC and SPEC.loader
b3 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = b3
SPEC.loader.exec_module(b3)


def test_exact_grids_and_inventory_count():
    assert b3.SEEDS == (0, 1, 2, 3, 4)
    assert b3.N_VALUES == (25, 50, 100)
    assert b3.COSTS == (0.0, 0.02, 0.05, 0.10, 0.15)
    assert b3.HORIZONS == (1, 2, 5, 10)
    assert b3.STATES_REQUIRED == 190


def test_argmax_and_literal_conservative_tie_breaking():
    assert b3.select_action({"0": 0.0, "STD": -1.0, "O50": -2.0, "REP": -3.0}) == "0"
    assert b3.select_action({"0": 0.0, "STD": 0.0, "O50": 0.0, "REP": 0.0}) == "0"
    assert b3.select_action({"0": 0.0, "STD": 1.0, "O50": 1.0, "REP": 1.0}) == "REP"
    assert b3.select_action({"0": 0.0, "STD": 1.0, "O50": 1.0, "REP": 0.5}) == "O50"


def test_delta_zero_and_kappa_identity():
    scores = {d: 0.5 for d in b3.DOMAINS}
    assert b3.operational_value(scores, scores, 0.1) == pytest.approx(0.5)
    assert b3.kappa_star(0.2, 0.1, 5) == pytest.approx(0.9)
    assert b3.kappa_star(0.2, -0.1, 5) == pytest.approx(1.0)


def test_real_provenance_and_validation_only_tables():
    scores, audit = b3.audit_and_load()
    assert audit["states_found"] == audit["states_required"] == 190
    assert audit["provenance_mismatches"] == 0
    values = b3.action_value_table(scores)
    assert len(values) == 1200
    assert values.test_metrics_used.eq(False).all()
    assert values.evaluation_split.eq("validation").all()
    assert values.loc[values.action == "0", "DeltaV"].abs().max() <= 1e-12
    choices = b3.adaptive_choice_table(values, scores)
    surface = b3.adaptive_surface(choices)
    assert len(choices) == 300
    assert len(surface) == 1200
    assert surface.isna().sum().sum() == 0


def test_source_has_no_training_or_test_metric_input():
    source = PATH.read_text()
    assert "optimizer.step(" not in source
    assert ".backward(" not in source
    assert "model.train(" not in source
    assert "test_metrics.csv" not in source
    assert "confirmatory_test" not in source


def test_support_uses_seed_replication_not_analytical_rows():
    choices = pd.DataFrame([
        {"seed": seed, "target_domain": "photo", "N": 25, "c": 0.0,
         "DeltaV_adaptive": 0.1 if seed < 4 else 0.0}
        for seed in b3.SEEDS
    ])
    surface = pd.DataFrame([
        {"seed": seed, "target_domain": "photo", "N": 25, "c": 0.0, "h": 1,
         "rho": 0.0, "kappa_star_adaptive": 0.1 if seed < 4 else -0.1,
         "adaptive_divergence_positive_width": seed < 4}
        for seed in b3.SEEDS
    ])
    delta, cells, viable = b3.support_and_viability(choices, surface)
    assert delta[0]["positive_seeds"] == 4
    assert cells[0]["seeds_with_any_positive_kappa_region"] == 4
    assert cells[0]["common_4of5_positive_width"] is True
    assert viable is True
