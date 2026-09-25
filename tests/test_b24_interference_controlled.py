from __future__ import annotations

import importlib.util
import copy
import sys
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments/pilots/b24_interference_controlled/run.py"
ANALYZE_PATH = ROOT / "experiments/pilots/b24_interference_controlled/analyze.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b24 = load("test_b24_run", RUN_PATH)
analysis = load("test_b24_analysis", ANALYZE_PATH)


def synthetic_lookup(per_domain: int = 180) -> pd.DataFrame:
    rows = []
    sample_id = 0
    for domain in b24.DOMAINS:
        for index in range(per_domain):
            rows.append(
                {
                    "sample_id": sample_id,
                    "domain": domain,
                    "label": index % 7,
                    "relative_path": f"{domain}/{index}.jpg",
                }
            )
            sample_id += 1
    return pd.DataFrame(rows).set_index("sample_id", drop=False)


def synthetic_replay(spec: b24.CaseSpec, lookup: pd.DataFrame) -> dict[str, object]:
    f0_ids = tuple(int(value) for value in lookup.sample_id)
    ids = b24.replay_ids(f0_ids, lookup, spec.seed, spec.domain, spec.n)
    return b24.replay_payload(spec, ids, lookup, "f0", "split")


def synthetic_opportunity_ids(spec: b24.CaseSpec) -> tuple[int, ...]:
    return tuple(100_000 + spec.seed * 10_000 + index for index in range(spec.n))


def test_frozen_grid_counts_and_doses():
    b24.validate_counts()
    cases = b24.plan_cases()
    assert len(cases) == 60
    assert len({case.key for case in cases}) == 60
    assert b24.TOTAL_STD_REUSED == 60
    assert b24.TOTAL_O50_FITS == 60
    assert b24.TOTAL_MIXED_FITS == 60
    assert b24.TOTAL_NEW_FITS == 120
    assert b24.TOTAL_NEW_EVALUATIONS == 180
    assert b24.TOTAL_METHOD_STATES == 240
    assert b24.TOTAL_METHOD_VALUE_ROWS == 1200
    assert b24.TOTAL_PRIMARY_CONTRAST_ROWS == 300
    assert {n: b24.dose(n) for n in b24.N_VALUES} == {25: (6, 96), 50: (12, 192), 100: (21, 336)}


def test_cpu_only_and_protocol_has_no_test_surface():
    assert b24.require_cpu("cpu").type == "cpu"
    with pytest.raises(ValueError, match="CPU ONLY"):
        b24.require_cpu("mps")
    with pytest.raises(ValueError, match="CPU ONLY"):
        b24.require_cpu("cuda")
    assert "test" not in b24.CaseSpec.__dataclass_fields__


def test_replay_is_deterministic_balanced_nested_and_f0_only():
    lookup = synthetic_lookup()
    f0_ids = tuple(int(value) for value in lookup.sample_id)
    for seed in b24.SEEDS:
        for target in b24.DOMAINS:
            selected = {}
            for n in b24.N_VALUES:
                first = b24.replay_ids(f0_ids, lookup, seed, target, n)
                second = b24.replay_ids(tuple(reversed(f0_ids)), lookup, seed, target, n)
                assert first == second
                assert len(first) == len(set(first)) == n
                assert set(first).issubset(f0_ids)
                assert all(lookup.loc[value, "domain"] != target for value in first)
                counts = pd.Series([lookup.loc[value, "domain"] for value in first]).value_counts()
                assert counts.max() - counts.min() <= 1
                selected[n] = set(first)
            assert selected[25] < selected[50] < selected[100]


@pytest.mark.parametrize("n", b24.N_VALUES)
def test_o50_rep_exactly_share_opportunity_projection_rng_and_dose(n):
    spec = b24.CaseSpec(1, 2, "photo", n)
    lookup = synthetic_lookup()
    replay = synthetic_replay(spec, lookup)
    opportunity_ids = synthetic_opportunity_ids(spec)
    o50, mixed = b24.build_schedules(spec, opportunity_ids, replay)
    steps, exposures = b24.dose(n)
    rep = mixed[:steps]
    assert len(o50) == len(rep) == steps and len(mixed) == 2 * steps
    assert b24.informative_opportunity_entries(o50) == b24.informative_opportunity_entries(rep)
    assert len(b24.informative_opportunity_entries(o50)) == exposures // 2
    assert len(b24.informative_opportunity_entries(mixed)) == exposures
    assert sum(entry["role"] == "opportunity_duplicate" for batch in o50 for entry in batch) == exposures // 2
    assert sum(entry["role"] == "replay" for batch in rep for entry in batch) == exposures // 2
    assert sum(entry["role"] == "replay" for batch in mixed for entry in batch) == exposures
    assert {entry["sample_id"] for batch in o50 for entry in batch if entry["role"] == "opportunity"} == set(opportunity_ids)
    assert {entry["sample_id"] for batch in rep for entry in batch if entry["role"] == "replay"} == set(replay["sample_ids"])
    for left, right in zip(o50, rep, strict=True):
        for position in range(16):
            if left[position]["role"] == "opportunity":
                assert left[position] == right[position]
                entry = left[position]
                assert b24.b23.augmentation_seed(spec.seed, n, entry["sample_id"], entry["exposure"]) == b24.b23.augmentation_seed(
                    spec.seed, n, right[position]["sample_id"], right[position]["exposure"]
                )
    assert [b24.b23.step_seed(spec.seed, n, step) for step in range(1, steps + 1)] == [
        b24.b23.step_seed(spec.seed, n, step) for step in range(1, steps + 1)
    ]


def test_o50_duplicates_exact_augmented_tensors_without_new_transform(monkeypatch):
    lookup = synthetic_lookup(10)
    builder = b24.ScheduledBatchBuilder(lookup, {int(value): int(value) % 7 for value in lookup.sample_id}, Path("."), 0, 25)
    calls = []

    def fake_tensor(entry):
        calls.append((entry["sample_id"], entry["exposure"]))
        return torch.full((1, 2, 2), float(entry["sample_id"] + entry["exposure"]))

    monkeypatch.setattr(builder, "_tensor", fake_tensor)
    originals = [
        {"sample_id": value, "exposure": 1, "domain": "photo", "role": "opportunity"}
        for value in range(8)
    ]
    duplicates = [{**entry, "role": "opportunity_duplicate"} for entry in originals]
    images, labels = builder.batch(originals + duplicates)
    assert len(calls) == 8
    assert torch.equal(images[:8], images[8:])
    assert torch.equal(labels[:8], labels[8:])


def test_schedule_audits_distinguish_information_from_processed_slots():
    spec = b24.CaseSpec(1, 0, "sketch", 25)
    lookup = synthetic_lookup()
    replay = synthetic_replay(spec, lookup)
    o50, mixed = b24.build_schedules(spec, synthetic_opportunity_ids(spec), replay)
    o50_audit = b24.schedule_audit(spec, "O50", o50, "op", None)
    rep_audit = b24.schedule_audit(spec, "REP", mixed[:6], "op", "replay")
    rep2_audit = b24.schedule_audit(spec, "REP2", mixed, "op", "replay")
    assert (o50_audit["steps"], o50_audit["processed_slots"], o50_audit["informative_opportunity_exposures"], o50_audit["duplicate_opportunity_slots"], o50_audit["replay_exposures"]) == (6, 96, 48, 48, 0)
    assert (rep_audit["steps"], rep_audit["processed_slots"], rep_audit["informative_opportunity_exposures"], rep_audit["duplicate_opportunity_slots"], rep_audit["replay_exposures"]) == (6, 96, 48, 0, 48)
    assert (rep2_audit["steps"], rep2_audit["processed_slots"], rep2_audit["informative_opportunity_exposures"], rep2_audit["replay_exposures"]) == (12, 192, 96, 96)
    assert o50_audit["opportunity_projection_sha256"] == rep_audit["opportunity_projection_sha256"]


def test_replay_payload_has_only_observed_ground_truth_and_no_teacher_query():
    spec = b24.CaseSpec(1, 0, "cartoon", 25)
    lookup = synthetic_lookup()
    replay = synthetic_replay(spec, lookup)
    assert replay["selection_uses_labels"] is False
    assert replay["test_used"] is False
    assert all(row["label_provenance"] == "F0_observed_ground_truth" for row in replay["samples"])
    assert all("pseudo_label" not in row for row in replay["samples"])
    assert all(row["domain"] != spec.domain for row in replay["samples"])


def test_artifact_restart_reuses_valid_and_rejects_corrupt_or_incomplete(tmp_path):
    header = {"protocol_id": b24.PROTOCOL_ID, "test_used": False}
    store = b24.ArtifactStore(tmp_path / "manifest.json", header)
    valid = tmp_path / "valid.bin"
    valid.write_bytes(b"valid")
    store.record("x", b24.artifact_record(valid, "O50", {"seed": 0}))
    reopened = b24.ArtifactStore(tmp_path / "manifest.json", header)
    assert reopened.valid_file("x", {"artifact_type": "O50", "seed": 0}) == valid
    valid.write_bytes(b"corrupt")
    assert reopened.valid_file("x", {"artifact_type": "O50", "seed": 0}) is None
    reopened.data["artifacts"]["y"] = {"artifact_type": "REP", "status": "running", "path": str(valid)}
    assert reopened.valid_file("y", {"artifact_type": "REP"}) is None


def test_rep_and_rep2_genealogy_is_one_trajectory():
    spec = b24.CaseSpec(3, 1, "art_painting", 50)
    steps, _ = b24.dose(spec.n)
    trajectory = f"mixed_s{spec.seed}_{spec.domain}_n{spec.n}"
    rep = {"trajectory_id": trajectory, "step": steps, "parent_f0_sha256": "f0"}
    rep2 = {"trajectory_id": trajectory, "step": 2 * steps, "parent_f0_sha256": "f0", "rep_checkpoint_sha256": "rep"}
    assert rep["trajectory_id"] == rep2["trajectory_id"]
    assert rep2["step"] == 2 * rep["step"]
    assert rep["parent_f0_sha256"] == rep2["parent_f0_sha256"]


def test_midpoint_restart_reproduces_uninterrupted_final_state(monkeypatch):
    class TinyBatches:
        def __init__(self, *args, **kwargs):
            pass

        def batch(self, entries):
            values = torch.tensor([[float(entry["sample_id"]), float(entry["exposure"])] for entry in entries])
            labels = torch.tensor([int(entry["sample_id"]) % 2 for entry in entries])
            return values, labels

    training_seed = b24.b23.derived_training_seed(0, 25)
    torch.manual_seed(training_seed)
    base = torch.nn.Linear(2, 2)
    f0_state = {key: value.detach().clone() for key, value in base.state_dict().items()}
    monkeypatch.setattr(b24, "ScheduledBatchBuilder", TinyBatches)
    monkeypatch.setattr(
        b24.b23.b20,
        "make_model",
        lambda kind, seed, device, pretrained=False: torch.nn.Linear(2, 2),
    )
    schedule = [
        [{"sample_id": index + offset, "exposure": index + 1, "role": "opportunity"} for offset in range(16)]
        for index in range(4)
    ]
    midpoint = {}

    def save_midpoint(model, optimizer, rng_state, step):
        midpoint.update(
            {
                "model_state": {key: value.detach().clone() for key, value in model.state_dict().items()},
                    "optimizer_state": copy.deepcopy(optimizer.state_dict()),
                    "rng_state": copy.deepcopy(rng_state),
                "step": step,
            }
        )

    config = {"fast": {"learning_rate": 0.001, "momentum": 0.9}}
    labels = {value: value % 2 for value in range(32)}
    lookup = pd.DataFrame()
    uninterrupted, _ = b24.train_scheduled(
        f0_state, schedule, labels, lookup, Path("."), 0, 25, config,
        midpoint_step=2, midpoint_callback=save_midpoint,
    )
    resumed, _ = b24.train_scheduled(
        f0_state, schedule, labels, lookup, Path("."), 0, 25, config, resume=midpoint,
    )
    assert b24.b23.state_dict_fingerprint(uninterrupted) == b24.b23.state_dict_fingerprint(resumed)


def test_operational_value_and_preregistered_classification_math():
    scores = {domain: 0.6 + index * 0.01 for index, domain in enumerate(b24.DOMAINS)}
    deep = {domain: 0.59 for domain in b24.DOMAINS}
    value, route, contributions = analysis.operational_value(scores, deep, 0.02)
    assert value == pytest.approx(sum(contributions.values()))
    assert route == "F,F,F,F"
    assert analysis.classify_values(pd.Series([0.1, 0.2, 0.3, 0.4, -0.01]))[0] == "POSITIVE"
    assert analysis.classify_values(pd.Series([-0.1, -0.2, -0.3, -0.4, 0.01]))[0] == "NULL"
    assert analysis.classify_values(pd.Series([0.1, 0.2, 0.3, -0.1, -0.2]))[0] == "INCONCLUSIVE"
    assert analysis.classify_values(pd.Series([1e-14] * 5))[0] == "NULL"


def test_method_tables_compute_rep_minus_o50_without_posthoc_quantities():
    scores = {}
    base = {domain: 0.5 for domain in b24.DOMAINS}
    deep = {domain: 0.45 for domain in b24.DOMAINS}
    for spec in b24.plan_cases():
        scores[("F0", spec.seed, spec.n, spec.domain)] = base
        scores[("D", spec.seed, spec.n, spec.domain)] = deep
        scores[("STD", spec.seed, spec.n, spec.domain)] = {domain: 0.51 for domain in b24.DOMAINS}
        scores[("O50", spec.seed, spec.n, spec.domain)] = {domain: 0.49 for domain in b24.DOMAINS}
        rep = {domain: 0.52 for domain in b24.DOMAINS}
        scores[("REP", spec.seed, spec.n, spec.domain)] = rep
        scores[("REP2", spec.seed, spec.n, spec.domain)] = {domain: 0.53 for domain in b24.DOMAINS}
    states, values, competence = analysis.method_tables(scores)
    contrasts = analysis.contrast_table(values, competence)
    assert len(states) == 240 and len(values) == 1200 and len(competence) == 60 and len(contrasts) == 300
    assert np.allclose(competence.DeltaI, -0.09)
    assert np.allclose(competence.DeltaL, 0.03)
    assert np.allclose(contrasts.DeltaQ, 0.03)
    assert not any("Gamma" in column or "rescue" in column.lower() for column in contrasts.columns)


def test_dry_run_never_trains_or_queries_teacher(monkeypatch, tmp_path, capsys):
    lookup = synthetic_lookup()
    f0_payload = {"training_ids": list(map(int, lookup.sample_id)), "scores": {domain: 0.5 for domain in b24.DOMAINS}}
    f0_record = {"sha256": "f0"}
    split = pd.DataFrame(
        [{"seed": seed, "sample_id": int(value), "role": "BASE"} for seed in b24.SEEDS for value in lookup.sample_id]
    )
    monkeypatch.setattr(b24, "parent_audit", lambda output: ({}, {"compatible": True, "test": "CLOSED"}))
    monkeypatch.setattr(b24, "load_parent_context", lambda manifest, output: (lookup.reset_index(drop=True), lookup, {}, {"split": split, "sha256": "split"}))
    monkeypatch.setattr(b24, "parent_checkpoint", lambda manifest, artifact: (f0_payload, f0_record))
    monkeypatch.setattr(
        b24,
        "parent_opportunity",
        lambda manifest, spec: (
            {"sample_ids": list(synthetic_opportunity_ids(spec)), "samples": []}, "op", {},
        ),
    )
    monkeypatch.setattr(b24, "parent_std", lambda manifest, spec: ({}, {}))
    monkeypatch.setattr(b24, "validate_image_root", lambda frame, root: None)
    monkeypatch.setattr(b24, "train_scheduled", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("trained")))
    monkeypatch.setattr(b24.b23, "teacher_labels", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("queried D")))
    image_root = tmp_path / "images"
    image_root.mkdir()
    args = Namespace(
        device="cpu", image_root=image_root, manifest=tmp_path / "manifest.csv",
        b23_output=tmp_path / "b23", output_dir=tmp_path / "b24", dry_run=True,
        analyze_only=False, force=False,
    )
    b24.dry_run(args)
    output = capsys.readouterr().out
    assert "120 new fits planned" in output
    assert "TEST remains closed" in output
    assert not (tmp_path / "b24").exists()


def test_analyze_only_delegates_without_training(monkeypatch, tmp_path):
    called = []
    monkeypatch.setattr(
        b24,
        "_load_module",
        lambda name, path: SimpleNamespace(run_analysis=lambda output, parent: called.append((output, parent))),
    )
    monkeypatch.setattr(b24, "train_scheduled", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("trained")))
    args = Namespace(
        device="cpu", image_root=None, manifest=tmp_path / "manifest.csv",
        b23_output=tmp_path / "b23", output_dir=tmp_path / "b24", dry_run=False,
        analyze_only=True, force=False,
    )
    b24.run(args)
    assert called == [(tmp_path / "b24", tmp_path / "b23")]
