"""Focused controls for the frozen DISCOVER-v0 sequential audit."""

from __future__ import annotations

import pytest

from hls.discover_v0 import THETA_1, THETA_2, capability_dual, evaluate_state
from hls.discover_v0_sequential import SequentialDiscoverAudit

S001 = ((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))


def test_bellman_and_cost_voi_identities_hold_at_visited_nodes() -> None:
    audit = SequentialDiscoverAudit(S001)
    nodes, _ = audit.audit()
    assert nodes
    for _, decision in nodes:
        assert decision.bellman_residual == pytest.approx(0.0, abs=1e-10)
        assert decision.baseline_residual == pytest.approx(0.0, abs=1e-10)


def test_horizon_one_has_zero_operational_voi() -> None:
    audit = SequentialDiscoverAudit(S001, horizon=1)
    nodes, _ = audit.audit()
    assert all(decision.future == pytest.approx(0.0) and decision.noinfo == pytest.approx(0.0) and decision.voi == pytest.approx(0.0) for _, decision in nodes)


def test_identical_types_remove_information_voi_and_discovery_cost() -> None:
    audit = SequentialDiscoverAudit(S001, theta_1=THETA_1, theta_2=THETA_1)
    nodes, _ = audit.audit()
    assert all(decision.voi == pytest.approx(0.0, abs=1e-10) for _, decision in nodes)
    for _, decision in nodes:
        children = audit.child_nodes(decision)
        assert all(belief == pytest.approx(decision.belief) for belief, _ in children)
        assert sum(mass for _, mass in children) == pytest.approx(1.0)
    assert evaluate_state(S001, theta_1=THETA_1, theta_2=THETA_1).discovery_cost == pytest.approx(0.0, abs=1e-10)


def test_reproducibility_and_value_agreement() -> None:
    first, second = SequentialDiscoverAudit(S001), SequentialDiscoverAudit(S001)
    assert first.value(first.horizon, first.prior) == pytest.approx(evaluate_state(S001).unknown_value)
    assert first.audit() == second.audit()


def test_capability_theta_duality_preserves_sequential_value() -> None:
    original = SequentialDiscoverAudit(S001)
    dual = SequentialDiscoverAudit(capability_dual(S001), theta_1=THETA_2, theta_2=THETA_1)
    assert dual.value(dual.horizon, dual.prior) == pytest.approx(original.value(original.horizon, original.prior))
