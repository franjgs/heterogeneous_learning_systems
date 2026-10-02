"""Deterministic controls for the Phase-V minimal-information audit."""

import importlib.util
from pathlib import Path

import pytest

from hls.minimal_reference_information_audit import (
    AlgebraicPrimitives,
    algebraic_action,
    algebraic_primitives,
    algebraic_region,
    audit_representation,
    audit_worlds,
    common_decision_information,
    future_feature,
    representation_key,
    run_information_audit,
    scalar_delta_j,
    scalar_m,
    sign_tol,
)
from hls.minimal_reference_scenario import LearningRule, MinimalReferenceScenario, reference_configurations
from hls.minimal_reference_validation import PrimitiveWorld, evaluate_primitives, primary_primitives


def _scenario(*, future_a: float = 0.0, scale: float = 1.5, beta: float = 0.5) -> MinimalReferenceScenario:
    return MinimalReferenceScenario(
        state_0=((0.65, 0.40), (0.70, 0.50)),
        demand_0=(0.50, 0.50),
        demand_1=(future_a, 1.0 - future_a),
        beta=beta,
        learning_rule=LearningRule.DIMINISHING,
        learning_scale=scale,
    )


def test_phi_definitions_are_constructed_from_transition_not_oracle_evaluation(monkeypatch) -> None:
    scenario = _scenario()
    monkeypatch.setattr(MinimalReferenceScenario, "evaluate", lambda self: (_ for _ in ()).throw(AssertionError("leakage")))
    assert future_feature(scenario, "phi0") == ()
    assert len(future_feature(scenario, "phi1")) == 2
    assert len(future_feature(scenario, "phi2")) == 8
    assert len(future_feature(scenario, "phi3")) == 10
    assert len(future_feature(scenario, "phi_alg")) == 3
    assert algebraic_primitives(scenario).g_alg == pytest.approx(0.065)
    with pytest.raises(AssertionError, match="leakage"):
        future_feature(scenario, "phi_oracle")


def test_algebraic_regions_and_boundaries_follow_the_declared_piecewise_identity() -> None:
    region_a = AlgebraicPrimitives(h=2.0, u=0.5, v=1.0, alpha=0.0, epsilon=0.0, gamma=0.0, delta=0.0)
    region_b = AlgebraicPrimitives(h=-1.0, u=0.5, v=0.3, alpha=0.0, epsilon=0.0, gamma=0.0, delta=0.0)
    region_c = AlgebraicPrimitives(h=0.0, u=0.5, v=0.8, alpha=0.0, epsilon=0.0, gamma=0.0, delta=0.0)
    assert algebraic_region(region_a) == "A_h_ge_v"
    assert region_a.g_alg == pytest.approx(-region_a.u)
    assert algebraic_region(region_b) == "B_h_le_negative_u"
    assert region_b.g_alg == pytest.approx(region_b.v)
    assert algebraic_region(region_c) == "C_negative_u_lt_h_lt_v"
    assert region_c.g_alg == pytest.approx(region_c.v - region_c.u - region_c.h)
    assert algebraic_region(AlgebraicPrimitives(0.4, 0.2, 0.4, 0, 0, 0, 0)) == "boundary_h_equals_v"
    assert algebraic_region(AlgebraicPrimitives(-0.2, 0.2, 0.5, 0, 0, 0, 0)) == "boundary_h_equals_negative_u"


def test_scalar_rule_uses_only_h_u_v_and_matches_beta_boundary_and_perturbations(monkeypatch) -> None:
    scenario = reference_configurations()["S3_decision_relevant"]
    values = algebraic_primitives(scenario)
    loss = scenario.present_reward("E") - scenario.present_reward("D")
    assert scalar_m(values.h, values.u, values.v) > 0.0
    beta_boundary = loss / scalar_m(values.h, values.u, values.v)
    monkeypatch.setattr(MinimalReferenceScenario, "terminal_value", lambda self, state: (_ for _ in ()).throw(AssertionError("leakage")))
    assert scalar_delta_j(loss, beta_boundary, values.h, values.u, values.v) == pytest.approx(0.0)
    assert sign_tol(scalar_delta_j(loss, beta_boundary * (1.0 - 1e-4), values.h, values.u, values.v)) == -1
    assert sign_tol(scalar_delta_j(loss, beta_boundary * (1.0 + 1e-4), values.h, values.u, values.v)) == 1


def test_scalar_rule_matches_oracle_at_boundary_without_leakage() -> None:
    scenario = reference_configurations()["S3_decision_relevant"]
    values = algebraic_primitives(scenario)
    loss = scenario.present_reward("E") - scenario.present_reward("D")
    beta_boundary = loss / scalar_m(values.h, values.u, values.v)
    for multiplier, expected in ((1.0 - 1e-4, -1), (1.0, 0), (1.0 + 1e-4, 1)):
        candidate = scenario.with_beta(beta_boundary * multiplier)
        candidate_values = algebraic_primitives(candidate)
        scalar_sign = sign_tol(scalar_delta_j(loss, candidate.beta, candidate_values.h, candidate_values.u, candidate_values.v))
        exact_sign = sign_tol(candidate.evaluate().total_difference)
        assert scalar_sign == expected == exact_sign


def test_phi0_to_phi3_have_the_declared_information_boundaries() -> None:
    base = _scenario(future_a=0.0, scale=1.5)
    changed_demand = _scenario(future_a=0.75, scale=1.5)
    changed_learning = _scenario(future_a=0.0, scale=0.5)
    assert common_decision_information(base) == common_decision_information(changed_demand)
    assert representation_key(base, "phi0") == representation_key(changed_demand, "phi0")
    assert representation_key(base, "phi1") == representation_key(changed_demand, "phi1")
    assert representation_key(base, "phi2") == representation_key(changed_demand, "phi2")
    assert representation_key(base, "phi3") != representation_key(changed_demand, "phi3")
    assert representation_key(base, "phi1") != representation_key(changed_learning, "phi1")
    assert representation_key(base, "phi2") != representation_key(changed_learning, "phi2")


def test_synthetic_collision_is_detected_with_positive_inevitable_regret() -> None:
    # Same S0, P0, beta, and therefore phi0; distinct learning intensities
    # change the oracle action in this known pair from the validated grid.
    worlds = audit_worlds(evaluate_primitives((
        PrimitiveWorld(0.50, 0.45, 0.20, 0.50, 0.80, 0.00, 1.00, 0.875),
        PrimitiveWorld(0.50, 0.45, 0.20, 0.50, 0.80, 0.00, 1.50, 0.875),
    )))
    report = audit_representation(worlds, "phi0")
    collision = report["collision_audit"]
    assert report["classes"] == 1
    assert collision["incompatible_oracle_decision_classes"] == 1
    assert collision["unavoidable_positive_regret_classes"] == 1
    assert collision["unavoidable_regret_total"] == pytest.approx(0.009375)
    assert collision["minimal_incompatible_examples"]


def test_oracle_control_recovers_oracle_value_and_regret_accounting_is_consistent() -> None:
    summary = run_information_audit()
    oracle = summary["representations"]["phi_oracle"]
    recoverable = oracle["recoverable_value"]
    assert oracle["collision_audit"]["incompatible_oracle_decision_classes"] == 0
    assert recoverable["regret_total"] == pytest.approx(0.0)
    assert recoverable["oracle_agreement"] == pytest.approx(1.0)
    assert recoverable["rule_total_value"] == pytest.approx(recoverable["oracle_total_value"])
    assert recoverable["oracle_gain_over_myopic"] == pytest.approx(
        recoverable["rule_gain_over_myopic"]
    )


def test_complete_audit_is_reproducible_and_retains_s2_s3_strata() -> None:
    first = run_information_audit()
    second = run_information_audit()
    assert first == second
    assert first["worlds"] == 221_184
    algebra = first["algebraic_validation"]
    assert algebra["maximum_absolute_G_residual"] <= 1e-12
    assert algebra["maximum_absolute_DeltaJ_residual"] <= 1e-12
    assert not algebra["counterexamples"]
    phi_alg = first["representations"]["phi_alg"]
    assert phi_alg["analytic_rule"]["oracle_agreement"] == pytest.approx(1.0)
    assert phi_alg["analytic_rule"]["regret_total"] == pytest.approx(0.0)
    assert phi_alg["G_reconstruction_audit"]["determines_G_on_audited_grid"]
    for name in ("alg_h", "alg_u", "alg_v", "alg_hu", "alg_hv", "alg_uv", "alg_h_v_minus_u", "alg_v_minus_u", "alg_h_plus_u"):
        assert name in first["representations"]
    scalar = first["scalar_decision_validation"]
    assert scalar["grid"]["formal_domain_L_gt_0_beta_gt_0"]["disagreements"] == 0
    # The extreme continuous stratum deliberately exposes reproducible
    # double-precision cancellation counterexamples; they must be retained.
    continuous = scalar["continuous"]["formal_domain_L_gt_0_beta_gt_0"]
    assert continuous["disagreements"] > 0
    assert continuous["counterexamples"]
    assert scalar["adversarial"]["decision_boundary_beta_equals_L_over_m"]["worlds"] > 0
    assert scalar["limit_cases"]["all_sign_agree"]
    for report in first["representations"].values():
        assert report["strata_under_global_information_rule"]["S2_positive_G_no_reversal"]["worlds"] > 0
        assert report["strata_under_global_information_rule"]["S3_decision_relevant"]["worlds"] > 0


def test_runner_writes_hash_validated_reproducible_artifacts(tmp_path: Path) -> None:
    runner_path = Path("experiments/synthetic/minimal_reference/run_information_audit.py")
    spec = importlib.util.spec_from_file_location("minimal_reference_information_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = module.run(tmp_path)
    assert summary["representations"]["phi_oracle"]["recoverable_value"]["regret_total"] == pytest.approx(0.0)
    assert summary["representations"]["phi_alg"]["analytic_rule"]["regret_total"] == pytest.approx(0.0)
    assert module.validate_manifest(tmp_path)
