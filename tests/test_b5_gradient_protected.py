from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "experiments/foundations/b5_gradient_protected/run.py"
SPEC = importlib.util.spec_from_file_location("b5_test_run", PATH)
assert SPEC and SPEC.loader
b5 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = b5
SPEC.loader.exec_module(b5)


def test_projection_conflict_and_no_conflict():
    combined, audit = b5.project_gradients((torch.tensor([1.0, 0.0]),), (torch.tensor([-1.0, 1.0]),))
    assert audit["projected"] is True
    assert audit["dot_before"] < 0
    assert audit["dot_after"] >= -b5.PROJECTION_TOLERANCE
    expected_proj = torch.tensor([0.5, 0.5])
    assert torch.allclose(combined[0], expected_proj + torch.tensor([-1.0, 1.0]), atol=1e-7)
    combined, audit = b5.project_gradients((torch.tensor([1.0]),), (torch.tensor([2.0]),))
    assert audit["projected"] is False
    assert torch.equal(combined[0], torch.tensor([3.0]))
    assert combined[0].dtype == torch.float32


def _legacy_float32_projection_dot_after(grad_opp, grad_mem):
    dot = sum((go.double() * gm.double()).sum() for go, gm in zip(grad_opp, grad_mem, strict=True))
    norm_mem_sq = sum((gm.double() ** 2).sum() for gm in grad_mem)
    coefficient = dot / (norm_mem_sq + b5.PROJECTION_EPS)
    projected = tuple(
        go - coefficient.to(go.dtype) * gm
        for go, gm in zip(grad_opp, grad_mem, strict=True)
    )
    return float(sum((gp.double() * gm.double()).sum() for gp, gm in zip(projected, grad_mem, strict=True)))


def test_realistic_float32_cancellation_is_removed():
    generator = torch.Generator().manual_seed(1)
    memory = torch.randn(100_000, generator=generator, dtype=torch.float32)
    opportunity = torch.randn(100_000, generator=generator, dtype=torch.float32) - 0.01 * memory
    legacy_dot_after = _legacy_float32_projection_dot_after((opportunity,), (memory,))
    assert legacy_dot_after < -b5.PROJECTION_TOLERANCE
    combined, audit = b5.project_gradients((opportunity,), (memory,))
    assert audit["projected"] is True
    assert audit["dot_after"] >= -b5.PROJECTION_TOLERANCE
    assert combined[0].dtype == torch.float32


def test_observed_scale_cancellation_across_parameter_tensors():
    generator = torch.Generator().manual_seed(3)
    memory = tuple(torch.randn(size, generator=generator, dtype=torch.float32) for size in (250_000, 350_000, 400_000))
    opportunity = tuple(
        torch.randn(tensor.shape, generator=generator, dtype=torch.float32) - 0.01 * tensor
        for tensor in memory
    )
    legacy_dot_after = _legacy_float32_projection_dot_after(opportunity, memory)
    assert legacy_dot_after < -4.77839116053147e-7
    combined, audit = b5.project_gradients(opportunity, memory)
    assert audit["dot_after"] >= -b5.PROJECTION_TOLERANCE
    assert all(gradient.dtype == torch.float32 for gradient in combined)


def test_projection_first_order_memory_direction():
    combined, audit = b5.project_gradients((torch.tensor([1.0, -2.0]),), (torch.tensor([-3.0, 1.0]),))
    memory_dot_combined = float((combined[0].double() * torch.tensor([-3.0, 1.0]).double()).sum())
    assert audit["dot_after"] >= -b5.PROJECTION_TOLERANCE
    assert memory_dot_combined >= -b5.PROJECTION_TOLERANCE


def test_optimizer_uses_exact_combined_gradient():
    parameter = torch.nn.Parameter(torch.tensor([1.0, 2.0]))
    optimizer = torch.optim.SGD([parameter], lr=0.1, momentum=0.0)
    combined, _ = b5.project_gradients((torch.tensor([1.0, 0.0]),), (torch.tensor([-1.0, 1.0]),))
    before = parameter.detach().clone()
    parameter.grad = combined[0].clone()
    optimizer.step()
    assert torch.allclose(parameter.detach(), before - 0.1 * combined[0])


def test_frozen_counts_cpu_and_default_dry_run():
    assert {n: b5.b24.dose(n)[0] for n in b5.N_VALUES} == {25: 6, 50: 12, 100: 21}
    assert b5.TOTAL_STEPS == 780
    args = b5.parse_args([])
    assert not args.run_full and not args.smoke_case and args.device == "cpu"
    with pytest.raises(SystemExit):
        b5.parse_args(["--device", "mps"])


def test_parent_provenance_and_no_test_training_inputs():
    audit = b5.audit_parent_artifacts(b5.DEFAULT_B23_OUTPUT, b5.DEFAULT_B24_OUTPUT)
    assert audit["families"] == 60
    assert audit["provenance"] == "PASS"
    source = PATH.read_text()
    assert "test_metrics.csv" not in source
    assert "protection_manifest" not in source
    assert "accept_block" not in source
    assert "validation" not in source[source.index("def train_grep"):source.index("def load_context")].lower()


def test_restart_provenance_fields_are_frozen():
    audit = {"families": 60, "provenance": "PASS"}
    prereg = b5.preregistration(audit)
    assert prereg["projection_eps"] == 1e-12
    assert prereg["projection_tolerance"] == 1e-7
    assert prereg["projection_numerics"] == b5.PROJECTION_NUMERICS
    assert prereg["TEST_STATUS"] == b5.TEST_STATUS
    assert prereg["status"] == "FROZEN_BEFORE_FULL_RUN"
