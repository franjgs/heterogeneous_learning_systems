from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments/foundations/b4_protected_development/run.py"
SPEC = importlib.util.spec_from_file_location("b4_test_run", PATH)
assert SPEC and SPEC.loader
b4 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = b4
SPEC.loader.exec_module(b4)


def test_frozen_counts_and_blocks():
    assert b4.TOTAL_FITS == 60
    assert b4.TOTAL_VALIDATION_EVALUATIONS == 60
    assert {n: b4.b24.dose(n)[0] for n in b4.N_VALUES} == {25: 6, 50: 12, 100: 21}
    assert b4.TOTAL_CANDIDATE_BLOCKS == 780
    assert b4.PROTECTION_PER_DOMAIN == 28
    assert b4.PROTECTION_TOTAL == 112


def test_zero_epsilon_acceptance_uses_f0_reference():
    reference = {d: 0.5 for d in b4.DOMAINS}
    assert b4.accept_block(reference, reference, "photo")
    lower = dict(reference)
    lower["cartoon"] -= 1e-9
    assert not b4.accept_block(reference, lower, "photo")
    local = dict(reference)
    local["photo"] -= 1e-9
    assert not b4.accept_block(reference, local, "photo")


def test_rejected_block_restores_model_and_optimizer_bitwise():
    torch.manual_seed(1)
    model = torch.nn.Linear(3, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
    snapshot = b4.snapshot_training_state(model, optimizer)
    loss = model(torch.ones(2, 3)).sum()
    loss.backward()
    optimizer.step()
    assert not b4.nested_equal(model.state_dict(), snapshot[0])
    b4.restore_training_state(model, optimizer, snapshot)
    assert b4.nested_equal(model.state_dict(), snapshot[0])
    assert b4.nested_equal(optimizer.state_dict(), snapshot[1])


def test_protection_manifest_is_train_only_balanced_and_deterministic():
    first = b4.build_protection_manifest(b4.DEFAULT_MANIFEST, b4.DEFAULT_B23_OUTPUT, b4.DEFAULT_B24_OUTPUT)
    second = b4.build_protection_manifest(b4.DEFAULT_MANIFEST, b4.DEFAULT_B23_OUTPUT, b4.DEFAULT_B24_OUTPUT)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["TEST_STATUS"] == b4.TEST_STATUS
    for seed in b4.SEEDS:
        samples = first["sets"][str(seed)]["samples"]
        assert len(samples) == 112
        counts = {}
        for sample in samples:
            counts[(sample["domain"], sample["label"])] = counts.get((sample["domain"], sample["label"]), 0) + 1
        assert set(counts.values()) == {4}


def test_default_is_dry_run_cpu_only_and_no_test_api():
    args = b4.parse_args([])
    assert not args.run_full and not args.smoke_case
    try:
        b4.parse_args(["--device", "mps"])
    except SystemExit:
        pass
    else:
        raise AssertionError("MPS was not rejected")
    source = PATH.read_text()
    assert "test_metrics.csv" not in source
    assert "optimizer.step()" in source  # PREP implementation exists.


def test_restart_requires_hash_valid_complete_fit(tmp_path):
    payload = {"x": torch.tensor([1])}
    path = tmp_path / "state.pt"
    torch.save(payload, path)
    record = {"status": "complete", "sha256": b4.sha256_file(path)}
    assert record["sha256"] == b4.sha256_file(path)
    torch.save({"x": torch.tensor([2])}, path)
    assert record["sha256"] != b4.sha256_file(path)
