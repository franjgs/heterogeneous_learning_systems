import importlib.util
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments/pilots/b22_opportunity_value/run.py"
SPEC = importlib.util.spec_from_file_location("b22_run", RUN_PATH)
assert SPEC and SPEC.loader
b22 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = b22
SPEC.loader.exec_module(b22)


def signatures():
    return b22.RunSignatures("protocol", "config", "manifest", "implementation")


def spec(n=25, domain="photo", seed=0, number=1):
    return b22.UpdateSpec(number, seed, domain, n, tuple(range(n)), seed + n + b22.DOMAINS.index(domain))


def valid_record(update=None):
    update = update or spec()
    f0 = {domain: 0.70 + 0.01 * index for index, domain in enumerate(b22.DOMAINS)}
    fk = {domain: value + (0.02 if domain == update.domain else 0.005) for domain, value in f0.items()}
    deep = {domain: 0.72 + 0.01 * index for index, domain in enumerate(b22.DOMAINS)}
    f0_fingerprint = "f0-fingerprint"
    return {
        "metadata": b22.expected_update_metadata(update, signatures()),
        "parent_state": "F0",
        "initial_f0_fingerprint": f0_fingerprint,
        "Fk_fingerprint": "fk-fingerprint",
        "F0_scores": f0,
        "Fk_scores": fk,
        "D_scores": deep,
        "fast_trajectory": b22.fast_trajectory_record(update, f0_fingerprint, update.n),
        "deep_trajectory": {
            "action": "D",
            "development_action": 1,
            "selected_ids": list(update.selected_ids),
            "selected_ids_sha256": b22.ids_fingerprint(update.selected_ids),
            "teacher_query_count": update.n,
            "pseudo_label_count": update.n,
            "student_updated": True,
            "parent_state": "F0",
        },
        "update_seconds": 1.0,
        "test_used": False,
        "evaluated_split": "validation",
    }


def full_records():
    records = {}
    number = 0
    for seed in b22.SEEDS:
        for n in b22.N_VALUES:
            for domain in b22.DOMAINS:
                number += 1
                update = spec(n=n, domain=domain, seed=seed, number=number)
                records[update.update_id] = valid_record(update)
    return records


def synthetic_plan_inputs():
    rows = []
    splits = {}
    sample_id = 0
    for seed in b22.SEEDS:
        transfer = []
        for domain in b22.DOMAINS:
            for _ in range(100):
                rows.append({"sample_id": sample_id, "domain": domain})
                transfer.append(sample_id)
                sample_id += 1
        splits[seed] = b22.DevelopmentSplits((), tuple(transfer), ())
    return pd.DataFrame(rows), splits


def test_frozen_grid_and_plan_cardinality():
    frame, splits = synthetic_plan_inputs()
    plan = b22.build_plan(frame, splits)
    assert b22.SEEDS == (0, 1, 2, 3, 4)
    assert b22.DOMAINS == ("photo", "art_painting", "cartoon", "sketch")
    assert b22.N_VALUES == (25, 50, 100)
    assert b22.COSTS == (0.00, 0.02, 0.05, 0.10, 0.15)
    assert b22.FUTURE_WEIGHTS == (1, 2, 5, 10)
    assert b22.KAPPA == 0.0
    assert len(plan) == 60
    assert len({item.update_id for item in plan}) == 60
    assert all(len(item.selected_ids) == item.n for item in plan)


def test_development_splits_have_no_test_surface():
    assert "test" not in b22.DevelopmentSplits.__dataclass_fields__


def test_development_split_builder_never_accesses_test(monkeypatch):
    class SplitMap(dict):
        def __getitem__(self, key):
            if key == "test":
                raise AssertionError("TEST accessed")
            return super().__getitem__(key)

    monkeypatch.setattr(
        b22.b20,
        "stratified_splits",
        lambda frame, seed: SplitMap(base=np.array([1]), transfer=np.array([2]), validation=np.array([3]), test=np.array([4])),
    )
    visible = b22.development_splits(pd.DataFrame(), 0)
    assert visible == b22.DevelopmentSplits((1,), (2,), (3,))


def test_cpu_only():
    assert b22.require_cpu("cpu").type == "cpu"
    with pytest.raises(ValueError, match="CPU ONLY"):
        b22.require_cpu("mps")


def test_timing_edits_do_not_change_frozen_scientific_fingerprint():
    assert b22.implementation_fingerprint() == b22.SCIENTIFIC_IMPLEMENTATION_SHA256
    assert b22.SCIENTIFIC_IMPLEMENTATION_SHA256 == "96956e2179e9a48540efcbdff463a4cc0a08378e66dc7efb4df80307e00d3cf8"


def test_fast_trajectory_cannot_query_teacher():
    record = b22.fast_trajectory_record(spec(), "f0", 25)
    assert record["operational_example_count"] == 25
    assert record["teacher_query_count"] == 0
    assert record["pseudo_label_count"] == 0
    assert record["student_updated"] is False
    assert record["initial_f0_fingerprint"] == record["final_fingerprint"]
    with pytest.raises(RuntimeError, match="expected 25"):
        b22.fast_trajectory_record(spec(), "f0", 24)


def test_deep_trajectory_uses_exactly_n_pseudo_labels():
    update = spec(n=25)
    selected = pd.DataFrame({"sample_id": list(update.selected_ids), "domain": [update.domain] * update.n, "label": [0] * update.n})
    calls = []

    def teacher(frame):
        calls.extend(frame.sample_id.tolist())
        return [3] * len(frame)

    opportunity, record = b22.deep_opportunity_record(update, selected, teacher)
    assert calls == list(update.selected_ids)
    assert len(opportunity) == update.n
    assert opportunity.label.tolist() == [3] * update.n
    assert record["teacher_query_count"] == update.n
    assert record["pseudo_label_count"] == update.n
    assert record["parent_state"] == "F0"


def test_deep_trajectory_rejects_wrong_count_and_ids():
    update = spec(n=25)
    selected = pd.DataFrame({"sample_id": list(update.selected_ids), "domain": [update.domain] * update.n, "label": [0] * update.n})
    with pytest.raises(RuntimeError, match="expected 25"):
        b22.deep_opportunity_record(update, selected, lambda frame: [1] * 24)
    wrong = selected.copy()
    wrong.loc[0, "sample_id"] = 999
    with pytest.raises(RuntimeError, match="selected IDs"):
        b22.deep_opportunity_record(update, wrong, lambda frame: [1] * 25)


def test_artifact_requires_direct_f0_parent_and_matching_provenance():
    update = spec()
    record = valid_record(update)
    b22.validate_update_artifact(record, update, signatures())
    sequential = json.loads(json.dumps(record))
    sequential["parent_state"] = "F_photo"
    with pytest.raises(RuntimeError, match="sequential"):
        b22.validate_update_artifact(sequential, update, signatures())
    wrong_seed = replace(update, seed=1)
    with pytest.raises(RuntimeError, match="incompatible"):
        b22.validate_update_artifact(record, wrong_seed, signatures())


def test_train_from_f0_copies_the_exact_parent(monkeypatch, tmp_path):
    f0 = torch.nn.Linear(2, 2)
    original = b22.state_dict_fingerprint(f0)

    def fake_train(model, *args, **kwargs):
        assert model is not f0
        assert b22.state_dict_fingerprint(model) == original
        with torch.no_grad():
            model.weight.add_(1.0)
        return model, [], 0.0

    monkeypatch.setattr(b22, "train_model", fake_train)
    model, _, _, parent = b22.train_from_f0(
        f0,
        pd.DataFrame(),
        spec(),
        {"fast": {"learning_rate": 0.001, "momentum": 0.9}},
        tmp_path,
        torch.device("cpu"),
    )
    assert parent == original
    assert b22.state_dict_fingerprint(f0) == original
    assert b22.state_dict_fingerprint(model) != original


def test_rho_value_delta_omega_h_and_decomposition():
    row = b22.analytical_row(valid_record(), cost=0.02, future_weight=5)
    f0 = {domain: row[f"F0_ba_{domain}"] for domain in b22.DOMAINS}
    fk = {domain: row[f"Fk_ba_{domain}"] for domain in b22.DOMAINS}
    deep = {domain: row[f"D_ba_{domain}"] for domain in b22.DOMAINS}
    expected_rho = f0["photo"] - (deep["photo"] - 0.02)
    expected_v0 = np.mean([max(f0[d], deep[d] - 0.02) for d in b22.DOMAINS])
    expected_vk = np.mean([max(fk[d], deep[d] - 0.02) for d in b22.DOMAINS])
    assert row["rho"] == pytest.approx(expected_rho)
    assert row["V_F0"] == pytest.approx(expected_v0)
    assert row["V_Fk"] == pytest.approx(expected_vk)
    assert row["DeltaV"] == pytest.approx(expected_vk - expected_v0)
    assert row["Omega"] == pytest.approx(5 * row["DeltaV"])
    assert row["H"] == pytest.approx(-row["rho"] + row["Omega"])
    contributions = sum(row[f"DeltaV_contribution_{domain}"] for domain in b22.DOMAINS)
    assert row["DeltaV"] == pytest.approx(contributions, abs=b22.NUMERIC_TOLERANCE)
    assert row["DeltaV"] == pytest.approx(row["DeltaV_local"] + row["DeltaV_cross"], abs=b22.NUMERIC_TOLERANCE)
    assert row["integration_changes_decision"] == (row["rho"] > 0 and row["H"] > 0)
    assert row["integration_changes_decision"] == (row["rho"] > 0 and 5 * row["DeltaV"] > row["rho"])


def test_full_analytical_grid_has_1200_rows_without_retraining():
    raw = b22.expand_grid(full_records())
    assert len(raw) == 1200
    assert raw[["seed", "domain", "N", "c", "B"]].drop_duplicates().shape[0] == 1200


def test_postprocessing_outputs_are_complete_and_automatic(tmp_path):
    raw = b22.expand_grid(full_records())
    aggregate, regions = b22.aggregate_results(raw)
    cases = b22.representative_cases(raw)
    classification = b22.classify_outcome(raw, regions)
    assert len(aggregate) == 4 * 3 * 5 * 4
    assert len(regions) == len(aggregate)
    assert set(aggregate.n_seeds) == {5}
    assert classification in {"POSITIVE", "NULL", "INCONCLUSIVE"}
    assert {"largest_H_with_rho_positive", "smallest_H_with_rho_positive"}.issubset(set(cases.case))
    summary = b22.analysis_summary(raw, aggregate, classification)
    assert "Q1" in summary and "Q7" in summary and "TEST remained closed" in summary
    b22.generate_figures(raw, cases, tmp_path)
    assert {path.name for path in (tmp_path / "figures").iterdir()} == {
        "decision_region_by_N.png",
        "H_vs_B_representative.png",
        "deltaV_local_cross.png",
    }


def test_restart_skips_valid_updates_and_force_repeats(tmp_path):
    update = spec()
    record = valid_record(update)
    update_dir = tmp_path / "updates"
    update_dir.mkdir()
    (update_dir / f"{update.update_id}.json").write_text(json.dumps(record))
    loaded = b22.load_completed_updates(tmp_path, [update], signatures(), force=False)
    assert list(loaded) == [update.update_id]
    assert b22.load_completed_updates(tmp_path, [update], signatures(), force=True) == {}


def test_base_checkpoint_round_trip_validates_metadata(monkeypatch, tmp_path):
    model = torch.nn.Linear(2, 2)
    scores = {domain: 0.5 for domain in b22.DOMAINS}
    metadata = b22._base_metadata("fast", 0, signatures())
    path = tmp_path / "fast_seed0.pt"
    b22.save_base_checkpoint(path, model, scores, metadata, 3.0)
    monkeypatch.setattr(b22.b20, "make_model", lambda *args, **kwargs: torch.nn.Linear(2, 2))
    loaded, loaded_scores, seconds = b22.load_base_checkpoint(path, "fast", 0, signatures(), torch.device("cpu"))
    assert b22.state_dict_fingerprint(loaded) == b22.state_dict_fingerprint(model)
    assert loaded_scores == scores
    assert seconds == 3.0


def test_incompatible_restart_is_not_reused(tmp_path):
    update = spec()
    record = valid_record(update)
    record["metadata"]["protocol_id"] = "wrong"
    update_dir = tmp_path / "updates"
    update_dir.mkdir()
    (update_dir / f"{update.update_id}.json").write_text(json.dumps(record))
    with pytest.raises(RuntimeError, match="use --force"):
        b22.load_completed_updates(tmp_path, [update], signatures(), force=False)


def test_dry_run_guard_never_calls_training():
    called = False

    def train():
        nonlocal called
        called = True

    assert b22.execute_training_phase(True, train) is None
    assert called is False
    b22.execute_training_phase(False, train)
    assert called is True


def test_classification_uses_two_seed_reproducibility():
    raw = pd.DataFrame({"integration_changes_decision": [True]})
    regions = pd.DataFrame({"integration_reproducible": [False], "noncompensating_reproducible": [True]})
    assert b22.classify_outcome(raw, regions) == "INCONCLUSIVE"
    regions.loc[0, "integration_reproducible"] = True
    assert b22.classify_outcome(raw, regions) == "POSITIVE"
    raw.loc[0, "integration_changes_decision"] = False
    regions.loc[0, "integration_reproducible"] = False
    assert b22.classify_outcome(raw, regions) == "NULL"


def completed_raw():
    return pd.read_csv(ROOT / "results/pilots/b22_opportunity_value/raw_results.csv")


def test_completed_results_reproduce_frozen_counts_and_no_test():
    output = ROOT / "results/pilots/b22_opportunity_value"
    audit = b22.b22_analysis.audit_results(
        completed_raw(), None, output / "run_metadata.json", b22.b22_analysis.FROZEN_COUNTS
    )
    assert audit["classification"] == "INCONCLUSIVE"
    assert audit["test"] == "CLOSED"
    assert {key: audit[key] for key in b22.b22_analysis.FROZEN_COUNTS} == b22.b22_analysis.FROZEN_COUNTS


def test_delta_v_summary_deduplicates_B_and_competence_changes_decompose():
    raw = completed_raw()
    delta = b22.b22_analysis.delta_v_summaries(raw)
    global_rows = delta[delta.scope == "global"]
    assert set(global_rows.metric) == {"DeltaV", "DeltaV_local", "DeltaV_cross"}
    assert set(global_rows.n) == {300}
    detail, summary = b22.b22_analysis.competence_change_summaries(raw)
    assert len(detail) == 60 * 4
    assert len(summary[summary.scope == "matrix_all_N"]) == 4 * 4
    updates = raw.sort_values(["c", "B"]).drop_duplicates(["seed", "domain", "N"])
    for row in updates.itertuples(index=False):
        observed = detail[
            (detail.seed == row.seed) & (detail.intervention_domain == row.domain) & (detail.N == row.N)
        ]
        expected = sum(getattr(row, f"Fk_ba_{domain}") - getattr(row, f"F0_ba_{domain}") for domain in b22.DOMAINS)
        assert observed.DeltaS.sum() == pytest.approx(expected)


def test_final_summary_formatter_uses_calculated_counts():
    audit = {
        "classification": "INCONCLUSIVE", "updates": 60, "rows": 1200, "favorable": 4,
        "noncompensating": 800, "reproducible_favorable_cells": 0, "cells": 240,
        "decision_changes": 4, "positive_cross_domain_cases": 0, "frontier_checks": 1200,
        "test": "CLOSED",
    }
    rendered = b22.final_summary(audit, 8 * 3600 + 10 * 60 + 14, b22.DEFAULT_OUTPUT)
    assert "Classification: INCONCLUSIVE" in rendered
    assert "4 / 1200" in rendered
    assert "0 / 240" in rendered
    assert "Total elapsed: 08:10:14" in rendered
    assert "b22_diagnostic.md" in rendered


def test_analyze_only_never_enters_training(monkeypatch):
    called = {"analysis": False}

    def forbidden(*args, **kwargs):
        raise AssertionError("analyze-only entered a model/training path")

    def completed(*args, **kwargs):
        called["analysis"] = True
        return {}

    monkeypatch.setattr(b22, "ensure_base_models", forbidden)
    monkeypatch.setattr(b22, "run_one_update", forbidden)
    monkeypatch.setattr(b22, "write_completed_analysis", completed)
    monkeypatch.setattr(b22, "historical_signatures", lambda *args: signatures())
    monkeypatch.setattr(b22, "load_completed_updates", lambda *args: {str(i): {} for i in range(60)})
    monkeypatch.setattr(b22, "expand_grid", lambda *args: completed_raw())
    class NoTiming:
        def header(self, *args, **kwargs): pass
        def adopt_completed(self, *args, **kwargs): pass
        def phase(self, *args, **kwargs): pass
        def record_auxiliary(self, *args, **kwargs): pass
        def finish(self, *args, **kwargs): pass
    monkeypatch.setattr(b22, "ExperimentTimingLogger", lambda *args, **kwargs: NoTiming())
    b22.main(["--device", "cpu", "--analyze-only"])
    assert called["analysis"]
