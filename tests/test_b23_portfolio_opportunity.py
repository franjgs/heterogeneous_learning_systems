import importlib.util
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments/pilots/b23_portfolio_opportunity/run.py"
ANALYZE_PATH = ROOT / "experiments/pilots/b23_portfolio_opportunity/analyze.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b23 = load("b23_run", RUN_PATH)
analysis = load("b23_analysis_test", ANALYZE_PATH)


def scores(offset=0.0):
    return {domain: 0.60 + 0.02 * index + offset for index, domain in enumerate(b23.DOMAINS)}


def test_frozen_grid_counts():
    singletons, joints = b23.plan_specs()
    b23.validate_counts()
    assert b23.SEEDS == (0, 1, 2, 3, 4)
    assert b23.N_VALUES == (25, 50, 100)
    assert b23.DOMAINS == ("photo", "art_painting", "cartoon", "sketch")
    assert b23.COSTS == (0.00, 0.02, 0.05, 0.10, 0.15)
    assert b23.FUTURE_WEIGHTS == (1, 2, 5, 10)
    assert b23.KAPPA == 0
    assert len(b23.domain_pairs()) == 6
    assert len(singletons) == 60
    assert len(joints) == 90
    assert b23.TOTAL_OPPORTUNITIES == 60
    assert b23.TOTAL_FITS == 160
    assert b23.TOTAL_PRIMARY_ROWS == 1800
    assert b23.TOTAL_DOSE_ROWS == 450


@pytest.mark.parametrize("n,steps,exposures", [(25, 6, 96), (50, 12, 192), (100, 21, 336)])
def test_frozen_singleton_joint_and_midpoint_dose(n, steps, exposures):
    assert b23.dose(n) == (steps, exposures)
    ids_i = tuple(range(n))
    ids_j = tuple(range(1000, 1000 + n))
    singleton = b23.singleton_schedule(0, n, "photo", ids_i)
    joint = b23.joint_schedule(b23.JointSpec(1, 0, n, "photo", "sketch"), ids_i, ids_j)
    assert len(singleton) == steps
    assert sum(len(batch) for batch in singleton) == exposures
    assert len(joint) == 2 * steps
    assert all(sum(item["domain"] == "photo" for item in batch) == 8 for batch in joint)
    assert all(sum(item["domain"] == "sketch" for item in batch) == 8 for batch in joint)
    midpoint = [item for batch in joint[:steps] for item in batch]
    final = [item for batch in joint for item in batch]
    assert sum(item["domain"] == "photo" for item in midpoint) == exposures // 2
    assert sum(item["domain"] == "sketch" for item in midpoint) == exposures // 2
    assert sum(item["domain"] == "photo" for item in final) == exposures
    assert sum(item["domain"] == "sketch" for item in final) == exposures


def test_shared_exposures_have_identical_augmentation_seeds():
    ids = tuple(range(25))
    singleton = [item for batch in b23.singleton_schedule(2, 25, "photo", ids) for item in batch]
    joint = [item for batch in b23.joint_schedule(b23.JointSpec(1, 2, 25, "photo", "sketch"), ids, tuple(range(100, 125))) for item in batch]
    joint_i = [item for item in joint if item["domain"] == "photo"]
    assert [(x["sample_id"], x["exposure"]) for x in singleton] == [(x["sample_id"], x["exposure"]) for x in joint_i]
    assert [b23.augmentation_seed(2, 25, x["sample_id"], x["exposure"]) for x in singleton] == [b23.augmentation_seed(2, 25, x["sample_id"], x["exposure"]) for x in joint_i]


def test_seed64_is_stable_and_identifier_sensitive():
    assert b23.seed64("training", 1, 25) == b23.seed64("training", 1, 25)
    assert b23.seed64("opportunity", 1, "photo") != b23.seed64("opportunity", 1, "sketch")
    assert b23.deterministic_fixture() == b23.deterministic_fixture()


def test_regression_raw_first_singleton_seed_exceeds_numpy_range_but_adapter_is_valid():
    failed_seed = b23.derived_training_seed(0, 25)
    assert failed_seed == 6117803925591946225
    assert failed_seed > 2**32 - 1
    with pytest.raises(ValueError, match="Seed must be between"):
        np.random.seed(failed_seed)
    assert b23.b20.numpy_compatible_seed(failed_seed) == failed_seed % (2**32)
    assert 0 <= b23.b20.numpy_compatible_seed(failed_seed) <= 2**32 - 1

    b23.seed_everything(failed_seed)
    first = (random.random(), float(np.random.random()), float(torch.rand(())))
    b23.seed_everything(failed_seed)
    second = (random.random(), float(np.random.random()), float(torch.rand(())))
    assert first == second


def test_all_b23_training_seeds_are_deterministic_numpy_valid_and_collision_free():
    coordinates = [(seed, n) for seed in b23.SEEDS for n in b23.N_VALUES]
    declared = {coordinates_: b23.derived_training_seed(*coordinates_) for coordinates_ in coordinates}
    numpy_seeds = {coordinates_: b23.derived_rng_seeds(*coordinates_)["numpy"] for coordinates_ in coordinates}
    assert len(set(declared.values())) == len(coordinates) == 15
    assert len(set(numpy_seeds.values())) == len(coordinates)
    assert all(0 <= value <= (1 << 63) - 1 for value in declared.values())
    assert all(0 <= value <= 2**32 - 1 for value in numpy_seeds.values())
    for value in declared.values():
        b23.b20.seed_everything(value)
    assert declared == {coordinates_: b23.derived_training_seed(*coordinates_) for coordinates_ in coordinates}
    assert numpy_seeds == {coordinates_: b23.derived_rng_seeds(*coordinates_)["numpy"] for coordinates_ in coordinates}


def test_singletons_joints_and_midpoints_share_only_protocol_declared_seed_groups():
    singletons, joints = b23.plan_specs()
    for spec in singletons:
        assert b23.derived_training_seed(spec.seed, spec.n) == b23.seed64("training", spec.seed, spec.n)
    for spec in joints:
        joint_seed = b23.derived_training_seed(spec.seed, spec.n)
        assert joint_seed == b23.seed64("training", spec.seed, spec.n)
        assert b23.derived_rng_seeds(spec.seed, spec.n)["torch"] == joint_seed
    assert len({b23.derived_training_seed(spec.seed, spec.n) for spec in singletons + joints}) == 15

    step_seeds = {
        b23.step_seed(seed, n, step)
        for seed in b23.SEEDS
        for n in b23.N_VALUES
        for step in range(1, 2 * b23.dose(n)[0] + 1)
    }
    assert len(step_seeds) == sum(2 * b23.dose(n)[0] for n in b23.N_VALUES) * len(b23.SEEDS) == 390
    assert all(0 <= value <= (1 << 63) - 1 for value in step_seeds)


def test_all_derived_seed_namespaces_are_range_valid_and_noncolliding():
    training = {b23.derived_training_seed(seed, n) for seed in b23.SEEDS for n in b23.N_VALUES}
    opportunity = {b23.seed64("opportunity", seed, domain) for seed in b23.SEEDS for domain in b23.DOMAINS}
    steps = {
        b23.step_seed(seed, n, step)
        for seed in b23.SEEDS for n in b23.N_VALUES
        for step in range(1, 2 * b23.dose(n)[0] + 1)
    }
    augmentation = set()
    for seed in b23.SEEDS:
        for n in b23.N_VALUES:
            for domain_index, domain in enumerate(b23.DOMAINS):
                ids = tuple(seed * 100000 + domain_index * 1000 + index for index in range(n))
                for item in (item for batch in b23.singleton_schedule(seed, n, domain, ids) for item in batch):
                    augmentation.add(b23.augmentation_seed(seed, n, item["sample_id"], item["exposure"]))
    assert tuple(map(len, (training, opportunity, steps, augmentation))) == (15, 20, 390, 12480)
    all_seeds = training | opportunity | steps | augmentation
    assert len(all_seeds) == 15 + 20 + 390 + 12480
    assert all(0 <= value <= (1 << 63) - 1 for value in all_seeds)


def test_first_singleton_model_initializes_with_corrected_seed_without_training():
    training_seed = b23.derived_training_seed(0, 25)
    first = b23.b20.make_model("fast", training_seed, torch.device("cpu"), pretrained=False)
    state = first.state_dict()
    reproduced = b23.b20.make_model("fast", training_seed, torch.device("cpu"), pretrained=False)
    reproduced.load_state_dict(state)
    assert b23.state_dict_fingerprint(first) == b23.state_dict_fingerprint(reproduced)


def test_seed_fix_preserves_all_base_seed_values_and_restart_contract(tmp_path):
    old_header = {"protocol": b23.PROTOCOL_ID, "implementation_sha256": b23.SCIENTIFIC_IMPLEMENTATION_SHA256}
    manifest = b23.ArtifactManifest(tmp_path / "manifest.json", old_header)
    for seed in b23.SEEDS:
        for name, training_seed in (("F0", seed + 2500), ("D", seed + 30000)):
            assert b23.b20.numpy_compatible_seed(training_seed) == training_seed
            path = tmp_path / f"{name}_s{seed}.pt"
            path.write_bytes(f"{name}-{seed}".encode())
            manifest.record(f"{name}_s{seed}", b23.artifact_record(path, name, {"seed": seed}))
    corrected_header = old_header | {"derived_seed_scheme": b23.DERIVED_SEED_SCHEME}
    reopened = b23.ArtifactManifest(tmp_path / "manifest.json", corrected_header)
    assert reopened.data["header"]["derived_seed_scheme"] == b23.DERIVED_SEED_SCHEME
    assert reopened.data["header"]["provenance_migrations"][0]["migration"] == "B2.3-derived-seed-range-fix"
    assert sum(
        reopened.valid_file(f"{name}_s{seed}", {"artifact_type": name, "seed": seed}) is not None
        for seed in b23.SEEDS for name in ("F0", "D")
    ) == 10


def test_seed_scheme_migration_rejects_any_preexisting_derived_state(tmp_path):
    old_header = {"protocol": b23.PROTOCOL_ID, "implementation_sha256": b23.SCIENTIFIC_IMPLEMENTATION_SHA256}
    manifest = b23.ArtifactManifest(tmp_path / "manifest.json", old_header)
    manifest.record("Fi_s0_photo_n25", {"artifact_type": "singleton", "status": "complete"})
    with pytest.raises(RuntimeError, match="provenance differs"):
        b23.ArtifactManifest(
            tmp_path / "manifest.json",
            old_header | {"derived_seed_scheme": b23.DERIVED_SEED_SCHEME},
        )


def test_opportunity_selection_is_nested_and_order_independent():
    frame = pd.DataFrame({"sample_id": range(120), "domain": ["photo"] * 120})
    ordered = b23.opportunity_order(frame, 3, "photo")
    reordered = b23.opportunity_order(frame.sample(frac=1, random_state=7), 3, "photo")
    assert ordered == reordered
    assert len(ordered) == 100
    assert ordered[:25] == ordered[:50][:25]


def test_opportunity_envelope_is_immutable_and_hash_checked(tmp_path):
    spec = b23.OpportunitySpec(0, "photo", 25, tuple(range(25)))
    rows = [{"sample_id": i, "relative_path": f"{i}.jpg", "domain": "photo", "pseudo_label": i % 7} for i in range(25)]
    payload = b23.opportunity_payload(spec, tuple(range(100)), rows, "deep")
    path = tmp_path / "op.json"
    digest = b23.write_envelope(path, payload)
    loaded, loaded_digest = b23.read_envelope(path)
    assert loaded == payload and loaded_digest == digest
    damaged = json.loads(path.read_text())
    damaged["payload"]["samples"][0]["pseudo_label"] = 6
    path.write_text(json.dumps(damaged))
    with pytest.raises(RuntimeError, match="corrupt"):
        b23.read_envelope(path)


def test_cpu_only_and_closed_split_surface(monkeypatch):
    assert b23.require_cpu("cpu").type == "cpu"
    with pytest.raises(ValueError, match="CPU ONLY"):
        b23.require_cpu("mps")
    with pytest.raises(ValueError, match="CPU ONLY"):
        b23.require_cpu("cuda")
    assert "test" not in b23.DevelopmentSplits.__dataclass_fields__

    class Guarded(dict):
        def __getitem__(self, key):
            if key.lower() == "test":
                raise AssertionError("closed split accessed")
            return super().__getitem__(key)

    monkeypatch.setattr(b23.b20, "stratified_splits", lambda frame, seed: Guarded(base=[1], transfer=[2], validation=[3], test=[4]))
    assert b23.development_splits(pd.DataFrame(), 0) == b23.DevelopmentSplits((1,), (2,), (3,))


def test_math_and_strict_primary_event():
    f0 = scores(0.0)
    deep = scores(-0.03)
    fi = scores(0.005)
    fj = scores(0.006)
    fij = scores(0.03)
    row = analysis.primary_row(0, 25, "photo", "sketch", 0.0, 10, f0, deep, fi, fj, fij)
    assert row["V_F0"] == pytest.approx(np.mean(list(f0.values())))
    assert row["DeltaV_i"] == pytest.approx(0.005)
    assert row["DeltaV_j"] == pytest.approx(0.006)
    assert row["DeltaV_ij"] == pytest.approx(0.03)
    assert row["Gamma_oper"] == pytest.approx(0.019)
    assert row["H_ij"] == pytest.approx(row["H_i"] + row["H_j"] + 10 * row["Gamma_oper"], abs=1e-12)
    assert row["H_j_given_i"] == pytest.approx(row["H_ij"] - row["H_i"])
    assert row["H_i_given_j"] == pytest.approx(row["H_ij"] - row["H_j"])
    assert row["portfolio_rescue"] == (row["rho_i"] > 0 and row["rho_j"] > 0 and row["H_i"] < 0 and row["H_j"] < 0 and row["H_ij"] > 0)


def test_compute_dose_definition():
    row = analysis.dose_row(0, 25, "photo", "sketch", 0.02, scores(), scores(-0.05), scores(0.04), scores(0.01))
    assert row["D_dose"] == pytest.approx(row["DeltaV_ij"] - row["DeltaV_ij_CM"])


def test_continuation_thresholds_only_use_positive_denominators():
    f0, deep = scores(), scores(-0.03)
    row = analysis.primary_row(0, 25, "photo", "sketch", 0.0, 1, f0, deep, scores(0.01), scores(-0.01), scores(0.03))
    table = analysis.threshold_table(pd.DataFrame([row]))
    assert set(table.threshold) == {"B_star_joint", "B_star_i"}
    assert (table.value > 0).all()


def synthetic_primary(rescue_seeds=()):
    rows = []
    for seed in b23.SEEDS:
        for n in b23.N_VALUES:
            for domain_i, domain_j in b23.domain_pairs():
                for cost in b23.COSTS:
                    for future_weight in b23.FUTURE_WEIGHTS:
                        rescue = seed in rescue_seeds and (n, domain_i, domain_j, cost, future_weight) == (25, "photo", "art_painting", 0.0, 1)
                        rows.append({"seed": seed, "N": n, "pair": f"{domain_i}__{domain_j}", "c": cost, "B": future_weight, "portfolio_rescue": rescue})
    return pd.DataFrame(rows)


@pytest.mark.parametrize("seeds,expected", [((), "NULL"), ((0,), "INCONCLUSIVE"), ((0, 1, 2), "POSITIVE")])
def test_frozen_classification(seeds, expected):
    classification, cells = analysis.classify(synthetic_primary(seeds))
    assert classification == expected
    assert len(cells) == 360


def test_restart_reuses_only_complete_hash_valid_artifacts(tmp_path):
    data = tmp_path / "state.bin"
    data.write_bytes(b"valid")
    manifest = b23.ArtifactManifest(tmp_path / "manifest.json", {"protocol": b23.PROTOCOL_ID})
    manifest.record("x", b23.artifact_record(data, "singleton", {"seed": 0}))
    assert manifest.valid_file("x", {"artifact_type": "singleton", "seed": 0}) == data
    data.write_bytes(b"corrupt")
    assert manifest.valid_file("x", {"artifact_type": "singleton", "seed": 0}) is None
    manifest.data["artifacts"]["x"]["status"] = "incomplete"
    assert manifest.valid_file("x", {"artifact_type": "singleton", "seed": 0}) is None


def test_restart_header_ignores_only_operational_metadata(tmp_path):
    path = tmp_path / "manifest.json"
    original = {"protocol": b23.PROTOCOL_ID, "scientific": "frozen", "git_commit": "old", "command": ["old"]}
    manifest = b23.ArtifactManifest(path, original)
    manifest.record("marker", {"status": "complete"})

    changed_operational = original | {"git_commit": "new", "command": ["new"]}
    reopened = b23.ArtifactManifest(path, changed_operational)
    assert "marker" in reopened.data["artifacts"]

    changed_scientific = changed_operational | {"scientific": "changed"}
    with pytest.raises(RuntimeError, match="provenance differs"):
        b23.ArtifactManifest(path, changed_scientific)


def test_b23_scientific_hashes_are_frozen_across_timing_only_edits():
    assert b23.SCIENTIFIC_IMPLEMENTATION_SHA256 == "37769e98591520dc979796b480958eb48c941dc328be28a57d9659c8339300be"
    assert b23.SCIENTIFIC_ANALYSIS_SHA256 == "677f1b7a5425e1bfc177d440ae9230b45afd1fb3f7c26f672f650025ba7cf6d6"
    assert b23.SCIENTIFIC_B20_RUNNER_SHA256 == "64dd4a2d642efd9f6e5970444d96250f96dbe6672671d18d7adc9398a5ae091c"


def test_genealogy_metadata_rejects_sequential_parent_by_exact_hash(tmp_path):
    checkpoint = tmp_path / "state.pt"
    torch.save({"value": 1}, checkpoint)
    manifest = b23.ArtifactManifest(tmp_path / "manifest.json", {"protocol": b23.PROTOCOL_ID})
    manifest.record("Fi", b23.artifact_record(checkpoint, "singleton", {"parent_f0_sha256": "f0"}))
    assert manifest.valid_file("Fi", {"artifact_type": "singleton", "parent_f0_sha256": "f0"}) == checkpoint
    assert manifest.valid_file("Fi", {"artifact_type": "singleton", "parent_f0_sha256": "another-derived-state"}) is None


def test_dry_run_and_analyze_only_guards_never_train_or_query_teacher(monkeypatch, tmp_path):
    called = []
    assert b23.execute_training(False, lambda: called.append("trained")) is None
    assert called == []
    with pytest.raises(RuntimeError, match="incomplete"):
        analysis.run_analysis(tmp_path)
    assert called == []


def test_analyze_only_branches_before_dataset_or_training(monkeypatch, tmp_path):
    calls = []

    class Analyzer:
        @staticmethod
        def run_analysis(output_dir, started):
            calls.append(output_dir)

    monkeypatch.setattr(b23, "_load_module", lambda *args: Analyzer)
    monkeypatch.setattr(b23, "execute_full", lambda *args: (_ for _ in ()).throw(AssertionError("training entered")))
    monkeypatch.setattr(b23.pd, "read_csv", lambda *args: (_ for _ in ()).throw(AssertionError("dataset read")))
    b23.main(["--device", "cpu", "--analyze-only", "--output-dir", str(tmp_path)])
    assert calls == [tmp_path]


def test_dry_run_counts_without_teacher_inference(monkeypatch, tmp_path, capsys):
    rows = []
    transfer = []
    sample_id = 0
    for domain in b23.DOMAINS:
        for _ in range(100):
            rows.append({"sample_id": sample_id, "domain": domain})
            transfer.append(sample_id)
            sample_id += 1
    frame = pd.DataFrame(rows)
    splits = {seed: b23.DevelopmentSplits((), tuple(transfer), ()) for seed in b23.SEEDS}
    monkeypatch.setattr(b23, "teacher_labels", lambda *args: (_ for _ in ()).throw(AssertionError("teacher queried")))
    b23.dry_run(frame, splits, None, tmp_path)
    output = capsys.readouterr().out
    assert "160 total fits" in output
    assert "1800 primary analytical rows" in output
    assert "No training or teacher inference executed" in output


def test_final_summary_has_scientific_counts(tmp_path):
    primary = synthetic_primary((0,))
    classification, cells = analysis.classify(primary)
    text = analysis.final_summary(classification, {"test": "CLOSED", "compatible": True, "evaluations": 250}, primary, cells, tmp_path, 1.0)
    assert "B2.3 complete" in text
    assert "Fits: 160/160" in text
    assert "Primary rows: 1800/1800" in text
    assert "Classification: INCONCLUSIVE" in text


def test_complete_synthetic_genealogy_passes_compatibility_audit(tmp_path):
    header = {
        "protocol_id": b23.PROTOCOL_ID, "device": "cpu", "test_used": False, "deterministic_algorithms": True,
        "protocol_sha256": b23.sha256_file(b23.PROTOCOL_PATH), "config_sha256": b23.sha256_file(b23.CONFIG_PATH),
        "implementation_sha256": b23.SCIENTIFIC_IMPLEMENTATION_SHA256, "analysis_sha256": b23.SCIENTIFIC_ANALYSIS_SHA256,
        "b20_runner_sha256": b23.SCIENTIFIC_B20_RUNNER_SHA256, "split_library_sha256": b23.sha256_file(b23.B20_LIBRARY_PATH),
        "dataset_revision": b23.DATASET_REVISION, "dataset_sha256": b23.DATASET_SHA256,
        "derived_seed_scheme": b23.DERIVED_SEED_SCHEME,
    }
    manifest = b23.ArtifactManifest(tmp_path / "run_manifest.json", header)
    split_rows = []
    base_sha = {}
    deep_sha = {}
    validation_hash = {}
    tiny_state = {"weight": torch.tensor([1.0])}
    fingerprint = b23.state_dict_fingerprint(tiny_state)
    for seed in b23.SEEDS:
        base_ids = [seed * 10000 + 8000]
        validation_ids = [seed * 10000 + 9000]
        transfer_ids = []
        for domain_index, domain in enumerate(b23.DOMAINS):
            transfer_ids.extend(seed * 10000 + domain_index * 100 + offset for offset in range(100))
        split_rows += [{"seed": seed, "sample_id": value, "role": "BASE"} for value in base_ids]
        split_rows += [{"seed": seed, "sample_id": value, "role": "TRANSFER"} for value in transfer_ids]
        split_rows += [{"seed": seed, "sample_id": value, "role": "VALIDATION"} for value in validation_ids]
        validation_hash[seed] = b23.sha256_json(validation_ids)
        for name, training_ids in (("F0", base_ids), ("D", base_ids + transfer_ids)):
            payload = {
                "model_state": tiny_state, "model_fingerprint": fingerprint, "scores": scores(0.0 if name == "F0" else 0.05),
                "training_ids": training_ids, "training_ids_sha256": b23.sha256_json(training_ids),
                "validation_ids_sha256": validation_hash[seed], "evaluation_split": "validation", "test_used": False,
            }
            path = tmp_path / f"{name}_s{seed}.pt"
            b23.save_checkpoint(path, payload)
            manifest.record(f"{name}_s{seed}", b23.artifact_record(path, name, {"seed": seed}))
        base_sha[seed] = manifest.data["artifacts"][f"F0_s{seed}"]["sha256"]
        deep_sha[seed] = manifest.data["artifacts"][f"D_s{seed}"]["sha256"]
    pd.DataFrame(split_rows).to_csv(tmp_path / "split_manifest.csv", index=False)

    opportunity_hash = {}
    opportunity_ids = {}
    for seed in b23.SEEDS:
        for domain_index, domain in enumerate(b23.DOMAINS):
            ids = tuple(seed * 10000 + domain_index * 100 + offset for offset in range(100))
            maximum_spec = b23.OpportunitySpec(seed, domain, 100, ids)
            maximum_rows = [{"sample_id": value, "relative_path": f"{value}.jpg", "domain": domain, "pseudo_label": value % 7} for value in ids]
            maximum = b23.opportunity_payload(maximum_spec, ids, maximum_rows, deep_sha[seed])
            maximum["teacher_query_count"] = 100
            maximum_path = tmp_path / f"opmax_s{seed}_{domain}.json"
            b23.write_envelope(maximum_path, maximum)
            manifest.record(f"opmax_s{seed}_{domain}", b23.artifact_record(maximum_path, "opportunity_max", {"seed": seed, "domain": domain}))
            for n in b23.N_VALUES:
                spec = b23.OpportunitySpec(seed, domain, n, ids[:n])
                payload = b23.opportunity_payload(spec, ids, maximum_rows[:n], deep_sha[seed])
                path = tmp_path / f"{spec.artifact_id}.json"
                digest = b23.write_envelope(path, payload)
                manifest.record(spec.artifact_id, b23.artifact_record(path, "opportunity", {"seed": seed, "domain": domain, "N": n}))
                opportunity_hash[(seed, domain, n)] = digest
                opportunity_ids[(seed, domain, n)] = ids[:n]

    singletons, joints = b23.plan_specs()
    for spec in singletons:
        steps, exposures = b23.dose(spec.n)
        schedule = b23.singleton_schedule(spec.seed, spec.n, spec.domain, opportunity_ids[(spec.seed, spec.domain, spec.n)])
        payload = {
            "model_state": tiny_state, "model_fingerprint": fingerprint, "scores": scores(0.01),
            "parent_f0_sha256": base_sha[spec.seed], "deep_sha256": deep_sha[spec.seed],
            "opportunity_sha256": opportunity_hash[(spec.seed, spec.domain, spec.n)],
            "steps": steps, "batch_size": 16, "total_exposures": exposures, "schedule_sha256": b23.sha256_json(schedule),
            "validation_ids_sha256": validation_hash[spec.seed], "evaluation_split": "validation", "test_used": False,
            "training_seed": b23.derived_training_seed(spec.seed, spec.n),
            "rng_seeds": b23.derived_rng_seeds(spec.seed, spec.n), "seed_scheme": b23.DERIVED_SEED_SCHEME,
        }
        path = tmp_path / f"{spec.artifact_id}.pt"
        b23.save_checkpoint(path, payload)
        manifest.record(spec.artifact_id, b23.artifact_record(path, "singleton", {"seed": spec.seed, "domain": spec.domain, "N": spec.n}))

    for spec in joints:
        steps, exposures = b23.dose(spec.n)
        schedule = b23.joint_schedule(spec, opportunity_ids[(spec.seed, spec.domain_i, spec.n)], opportunity_ids[(spec.seed, spec.domain_j, spec.n)])
        common = {
            "model_state": tiny_state, "model_fingerprint": fingerprint, "trajectory_id": spec.artifact_id,
            "parent_f0_sha256": base_sha[spec.seed],
            "opportunity_i_sha256": opportunity_hash[(spec.seed, spec.domain_i, spec.n)],
            "opportunity_j_sha256": opportunity_hash[(spec.seed, spec.domain_j, spec.n)],
            "schedule_sha256": b23.sha256_json(schedule), "validation_ids_sha256": validation_hash[spec.seed],
            "evaluation_split": "validation", "test_used": False,
            "training_seed": b23.derived_training_seed(spec.seed, spec.n),
            "rng_seeds": b23.derived_rng_seeds(spec.seed, spec.n), "seed_scheme": b23.DERIVED_SEED_SCHEME,
        }
        optimizer_state = {"state": {}, "param_groups": []}
        rng_state = {"torch": torch.tensor([1], dtype=torch.uint8)}
        cm_payload = common | {
            "step": steps, "exposures_i": exposures // 2, "exposures_j": exposures // 2, "scores": scores(0.015),
            "optimizer_state": optimizer_state, "rng_state": rng_state,
            "optimizer_state_sha256": b23.sha256_torch_object(optimizer_state), "rng_state_sha256": b23.sha256_torch_object(rng_state),
        }
        cm_path = tmp_path / f"{spec.artifact_id}_CM.pt"
        b23.save_checkpoint(cm_path, cm_payload)
        manifest.record(spec.artifact_id + "_CM", b23.artifact_record(cm_path, "joint_cm", {"seed": spec.seed, "N": spec.n, "domain_i": spec.domain_i, "domain_j": spec.domain_j}))
        final_payload = common | {
            "steps": 2 * steps, "batch_size": 16, "exposures_i": exposures, "exposures_j": exposures,
            "deep_sha256": deep_sha[spec.seed], "midpoint_sha256": manifest.data["artifacts"][spec.artifact_id + "_CM"]["sha256"], "scores": scores(0.03),
        }
        final_path = tmp_path / f"{spec.artifact_id}.pt"
        b23.save_checkpoint(final_path, final_payload)
        manifest.record(spec.artifact_id, b23.artifact_record(final_path, "joint", {"seed": spec.seed, "N": spec.n, "domain_i": spec.domain_i, "domain_j": spec.domain_j}))

    compatible_scores, audit = analysis.compatibility_audit(tmp_path)
    assert audit == {"compatible": True, "evaluations": 250, "test": "CLOSED"}
    assert len(compatible_scores) == 250
    primary, dose, changes = analysis.expand(compatible_scores)
    assert (len(primary), len(dose), len(changes)) == (1800, 450, 90)
    result = analysis.run_analysis(tmp_path)
    assert result["classification"] in {"POSITIVE", "NULL", "INCONCLUSIVE"}
    assert pd.read_csv(tmp_path / "state_metrics.csv").shape[0] == 250
    assert pd.read_csv(tmp_path / "primary_results.csv").shape[0] == 1800
    assert pd.read_csv(tmp_path / "compute_dose.csv").shape[0] == 450
    assert (tmp_path / "base_states.jsonl").is_file()
    assert (tmp_path / "opportunities.jsonl").is_file()
    assert (tmp_path / "development_states.jsonl").is_file()
