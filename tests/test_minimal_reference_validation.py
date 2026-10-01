"""Permanent invariants for the fixed Phase-V minimal-reference validation."""

import importlib.util
from pathlib import Path

from hls.minimal_reference_validation import (
    CLASS_TOL,
    boundary_probes,
    evaluate_primitives,
    primary_primitives,
    run_validation,
)


def test_primary_grid_is_deterministic_and_has_changing_demand_only() -> None:
    first = primary_primitives()
    second = primary_primitives()
    assert first == second
    assert len(first) == 221_184
    assert all(item.present_a != item.future_a for item in first)


def test_primary_grid_derives_identity_and_contains_positive_s2_and_s3_regions() -> None:
    rows, summary = run_validation()
    assert summary["maximum_absolute_identity_residual"] <= CLASS_TOL
    assert summary["positive_S2_region"]
    assert summary["positive_S3_region"]
    assert summary["regime_counts"]["S2_positive_G_no_reversal"] > 0
    assert summary["regime_counts"]["S3_decision_relevant"] > 0
    assert summary["counterexample_search"]["classification_contradictions"] == 0
    assert summary["counterexample_search"]["competence_change_without_positive_G"] > 0


def test_derived_boundary_probes_are_exact_controls_not_primitive_g_values() -> None:
    rows = evaluate_primitives(primary_primitives())
    probes = boundary_probes(rows)
    assert len(probes) == 20
    assert all(probe.regime == "boundary" for probe in probes)
    assert all(abs(probe.delta_j) <= CLASS_TOL for probe in probes)
    _, summary = run_validation()
    assert len(summary["boundary_probes"]["details"]) == 20


def test_ablations_and_local_robustness_have_the_declared_scoped_controls() -> None:
    _, summary = run_validation()
    ablations = summary["ablations"]
    assert ablations["no_competence_evolution"]["max_abs_G"] <= CLASS_TOL
    assert ablations["recipient_neutral_B_control"]["max_abs_G"] <= CLASS_TOL
    assert ablations["audited_homogeneous_linear_control"]["G"] == 0.0
    assert summary["local_robustness"]["S2_positive_G_no_reversal"]["all_preserved"]
    assert summary["local_robustness"]["S3_decision_relevant"]["all_preserved"]
    assert len(summary["local_robustness"]["S2_positive_G_no_reversal"]["seeds"]) == 5
    assert len(summary["local_robustness"]["S3_decision_relevant"]["seeds"]) == 5


def test_runner_writes_hash_validated_reproducible_artifacts(tmp_path: Path) -> None:
    runner_path = Path("experiments/synthetic/minimal_reference/run_validation.py")
    spec = importlib.util.spec_from_file_location("minimal_reference_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = module.run(tmp_path)
    assert summary["positive_S2_region"]
    assert summary["positive_S3_region"]
    assert module.validate_manifest(tmp_path)
