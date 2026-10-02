"""Controls for the finite G3 information audit, not a G3 physics test."""

from hls.g3_information_audit import audit_regime


def test_full_exact_information_reconstructs_d_and_the_oracle_order_on_a_small_grid() -> None:
    result = audit_regime("g3a", values=(0.0, 0.5, 1.0), scales=(0.0, 0.5, 2.0))
    exact = result["representations"]["full_exact"]
    assert result["max_direct_algebraic_residual"] <= 1e-12
    assert exact["d_collision_classes"] == 0
    assert exact["ranking_collision_classes"] == 0
    assert exact["regret_total"] == 0.0


def test_poor_amount_information_has_detectable_value_and_ranking_collisions() -> None:
    result = audit_regime("g3b", values=(0.0, 0.5, 1.0), scales=(0.0, 0.5, 2.0))
    amount = result["representations"]["amount"]
    assert amount["d_collision_classes"] > 0
    assert amount["ranking_collision_classes"] > 0
    assert amount["d_counterexample"] is not None
    assert amount["ranking_counterexample"] is not None


def test_dual_audit_has_the_same_exact_reconstruction_control() -> None:
    result = audit_regime("dual", values=(0.0, 0.5, 1.0), scales=(0.0, 0.5, 2.0))
    exact = result["representations"]["full_exact"]
    assert exact["d_collision_classes"] == 0
    assert exact["oracle_development_value_recovered"] == 1.0
