import json
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from hls.b2_pacs_calibration import (
    CLASSES,
    DOMAINS,
    domain_gaps,
    domain_metrics,
    select_base_fraction,
    stratified_splits,
    validate_disjoint_splits,
    validate_manifest,
)


def load_pacs_runner():
    path = Path(__file__).resolve().parents[1] / "experiments/pilots/b2_pacs_calibration/run.py"
    spec = importlib.util.spec_from_file_location("b2_pacs_calibration_run", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def toy_manifest(repeats=20):
    rows = []
    sample_id = 0
    for domain in DOMAINS:
        for label, class_name in enumerate(CLASSES):
            for _ in range(repeats):
                rows.append(
                    {
                        "sample_id": sample_id,
                        "domain": domain,
                        "label": label,
                        "class_name": class_name,
                        "sha256": f"hash-{sample_id}",
                        "relative_path": f"{domain}/{class_name}/{sample_id}.jpg",
                    }
                )
                sample_id += 1
    return pd.DataFrame(rows)


def test_manifest_has_expected_domains_and_classes():
    manifest = toy_manifest()
    validate_manifest(manifest)
    assert set(manifest.domain) == set(DOMAINS)
    assert set(manifest.class_name) == set(CLASSES)


def test_stratified_splits_are_disjoint_complete_and_reasonably_balanced():
    manifest = toy_manifest()
    splits = stratified_splits(manifest, seed=7)
    validate_disjoint_splits(splits, set(manifest.sample_id))
    expected_counts = {
        name: round(len(manifest) * frac)
        for name, frac in {
            "base": 0.50,
            "transfer": 0.20,
            "validation": 0.15,
            "test": 0.15,
        }.items()
    }
    assert all(abs(len(splits[name]) - expected_counts[name]) <= 1 for name in splits)
    for _, cell in manifest.groupby(["domain", "label"]):
        cell_ids = set(cell.sample_id)
        cell_counts = [len(cell_ids.intersection(set(splits[name]))) for name in splits]
        expected = [len(cell_ids) * frac for frac in (0.50, 0.20, 0.15, 0.15)]
        assert all(abs(observed - target) <= 1 for observed, target in zip(cell_counts, expected))
    assert not (set(splits["test"]) & set(splits["base"]))
    assert not (set(splits["test"]) & set(splits["transfer"]))


def test_base_fraction_is_seed_reproducible_and_excludes_nonbase():
    manifest = toy_manifest()
    splits = stratified_splits(manifest, seed=4)
    selected_a = select_base_fraction(manifest, splits["base"], 0.25, seed=9)
    selected_b = select_base_fraction(manifest, splits["base"], 0.25, seed=9)
    assert np.array_equal(selected_a, selected_b)
    assert set(selected_a).issubset(set(splits["base"]))
    assert not set(selected_a).intersection(set(splits["transfer"]))


def test_domain_balanced_accuracy_and_accuracy():
    y = np.tile(np.array([0, 1, 1, 0]), 4)
    pred = np.tile(np.array([0, 0, 1, 1]), 4)
    domains = np.repeat(np.array(DOMAINS), 4)
    result = domain_metrics(y, pred, domains)
    assert result["photo"]["balanced_accuracy"] == pytest.approx(0.5)
    assert result["photo"]["accuracy"] == pytest.approx(0.5)
    assert result["photo"]["n"] == 4
    assert result["sketch"]["balanced_accuracy"] == pytest.approx(0.5)
    assert result["sketch"]["accuracy"] == pytest.approx(0.5)


def test_domain_gaps_are_deep_minus_fast():
    fast = {domain: 0.5 for domain in DOMAINS}
    deep = {domain: 0.7 for domain in DOMAINS}
    assert all(value == pytest.approx(0.2) for value in domain_gaps(deep, fast).values())


def test_manifest_rejects_duplicate_hash_or_bad_domain():
    manifest = toy_manifest()
    manifest.loc[1, "sha256"] = manifest.loc[0, "sha256"]
    with pytest.raises(ValueError, match="byte-identical image"):
        validate_manifest(manifest)
    manifest = toy_manifest()
    manifest.loc[0, "domain"] = "other"
    with pytest.raises(ValueError, match="four PACS domains"):
        validate_manifest(manifest)


def test_generated_pacs_manifest_and_split_outputs_are_consistent():
    root = Path(__file__).resolve().parents[1] / "results/pilots/b2_pacs_calibration"
    manifest = pd.read_csv(root / "dataset_manifest.csv")
    audit = json.loads((root / "dataset_audit.json").read_text())
    splits = pd.read_csv(root / "split_manifest.csv")
    validate_manifest(manifest)
    assert len(manifest) == audit["rows"] == 9991
    assert audit["image_audit"]["corrupt_or_unreadable"] == 0
    assert audit["image_audit"]["duplicate_rows_by_exact_sha256"] == 0
    assert manifest.sha256.nunique() == len(manifest)
    for seed, seed_rows in splits.groupby("seed"):
        assert set(seed_rows.split) == {"base", "transfer", "validation", "test"}
        assert not seed_rows.sample_id.duplicated().any()
        assert set(seed_rows.sample_id) == set(manifest.sample_id)
        assert seed_rows.groupby("split").size().to_dict() == {
            "base": 4995,
            "test": 1499,
            "transfer": 1998,
            "validation": 1499,
        }


def test_explicit_device_selection_and_cpu_compatibility(monkeypatch):
    runner = load_pacs_runner()
    monkeypatch.setattr(runner.torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(runner.torch.backends.mps, "is_available", lambda: True)
    assert str(runner.resolve_device("auto", allow_cpu=False)) == "cuda"
    assert str(runner.resolve_device("cpu", allow_cpu=False)) == "cpu"
    assert str(runner.resolve_device("mps", allow_cpu=False)) == "mps"

    monkeypatch.setattr(runner.torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(runner.torch.backends.mps, "is_available", lambda: False)
    with pytest.raises(SystemExit, match="MPS was requested"):
        runner.resolve_device("mps", allow_cpu=False)
    with pytest.raises(SystemExit, match="compute-blocked by CPU-only hardware"):
        runner.resolve_device("auto", allow_cpu=False)
    assert str(runner.resolve_device("auto", allow_cpu=True)) == "cpu"
