import pytest
import importlib.util
from pathlib import Path

from hls.g2_dynamic import (
    D0,
    D1,
    D2,
    EXACT_TOL,
    d2_closed_form,
    d2_regime,
    demand_sweep,
    efficient_frontier,
    terminal_value,
)


def test_d0_no_evolution_has_identical_future_states_sets_frontiers_and_values() -> None:
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        evaluation = D0.evaluate(p)
        assert evaluation.action_1.future_state == evaluation.action_2.future_state
        assert evaluation.action_1.attainable == evaluation.action_2.attainable
        assert evaluation.action_1.frontier == evaluation.action_2.frontier
        assert evaluation.action_1.terminal_value == pytest.approx(evaluation.action_2.terminal_value)
        assert evaluation.delta_dev == pytest.approx(0.0)


def test_d1_future_states_match_the_ground_truth() -> None:
    evaluation = D1.evaluate(0.5)
    assert evaluation.action_1.future_state == ((0.5, 0.8), (0.8, 0.4))
    assert evaluation.action_2.future_state == ((0.4, 0.8), (0.8, 0.4))
    assert evaluation.action_1.future_state != evaluation.action_2.future_state


def test_d1_attainable_sets_change_but_efficient_frontier_is_the_same() -> None:
    evaluation = D1.evaluate(0.5)
    assert set(evaluation.action_1.attainable.values()) != set(evaluation.action_2.attainable.values())
    assert evaluation.action_1.frontier == ((0.8, 0.8),)
    assert evaluation.action_2.frontier == ((0.8, 0.8),)


def test_d1_is_a_t4_null_with_equal_terminal_value_for_all_demand_mixtures() -> None:
    for evaluation in demand_sweep(D1, points=101):
        assert evaluation.action_1.terminal_value == pytest.approx(0.8)
        assert evaluation.action_2.terminal_value == pytest.approx(0.8)
        assert evaluation.delta_dev == pytest.approx(0.0)


def test_d2_future_states_and_efficient_frontiers_match_the_ground_truth() -> None:
    evaluation = D2.evaluate(0.5)
    assert evaluation.action_1.future_state == ((1.0, 0.8), (0.8, 0.6))
    assert evaluation.action_2.future_state == ((0.7, 0.8), (0.8, 0.6))
    assert evaluation.action_1.frontier == ((1.0, 0.8),)
    assert evaluation.action_2.frontier == ((0.8, 0.8),)


def test_d2_attainable_sets_match_the_ground_truth() -> None:
    evaluation = D2.evaluate(0.5)
    assert evaluation.action_1.attainable == {
        "11": (1.0, 0.8),
        "12": (1.0, 0.6),
        "21": (0.8, 0.8),
        "22": (0.8, 0.6),
    }
    assert evaluation.action_2.attainable == {
        "11": (0.7, 0.8),
        "12": (0.7, 0.6),
        "21": (0.8, 0.8),
        "22": (0.8, 0.6),
    }


def test_d2_present_reward_difference_is_minus_point_one() -> None:
    evaluation = D2.evaluate(0.5)
    assert evaluation.action_1.present_reward == pytest.approx(0.7)
    assert evaluation.action_2.present_reward == pytest.approx(0.8)
    assert evaluation.delta_r == pytest.approx(-0.1)


def test_d2_terminal_value_and_development_value_closed_forms() -> None:
    for evaluation in demand_sweep(D2, points=101):
        p = evaluation.p
        assert evaluation.action_1.terminal_value == pytest.approx(0.8 + 0.2 * p)
        assert evaluation.action_2.terminal_value == pytest.approx(0.8)
        assert evaluation.delta_dev == pytest.approx(0.2 * p)


def test_d2_total_value_closed_form() -> None:
    for evaluation in demand_sweep(D2, points=101):
        _, expected_dev, expected_total = d2_closed_form(evaluation.p)
        assert evaluation.delta_dev == pytest.approx(expected_dev)
        assert evaluation.delta_j == pytest.approx(expected_total)


def test_d2_t5_boundary_is_exactly_zero() -> None:
    assert D2.evaluate(0.0).delta_dev == pytest.approx(0.0)
    assert D2.evaluate(0.01).delta_dev > 0.0


def test_d2_t6_indifference_boundary_is_exactly_one_half() -> None:
    assert D2.evaluate(0.49).delta_j < 0.0
    assert D2.evaluate(0.5).delta_j == pytest.approx(0.0)
    assert D2.evaluate(0.51).delta_j > 0.0


@pytest.mark.parametrize(
    ("p", "expected_t5", "expected_t6"),
    (
        (0.0, "T5_null_equal_future_value", "T6_static_sufficiency"),
        (0.25, "T5_positive_development_value", "T6_tradeoff_without_reversal"),
        (0.5, "T5_positive_development_value", "T6_intertemporal_indifference"),
        (0.75, "T5_positive_development_value", "T6_decision_reversal"),
        (1.0, "T5_positive_development_value", "T6_decision_reversal"),
    ),
)
def test_d2_documented_t5_t6_regimes(p: float, expected_t5: str, expected_t6: str) -> None:
    assert d2_regime(p) == (expected_t5, expected_t6)


def test_frontier_deduplicates_and_removes_dominated_outcomes() -> None:
    outcomes = {"a": (0.8, 0.8), "b": (0.8, 0.8), "c": (0.7, 0.8), "d": (0.8, 0.7)}
    assert efficient_frontier(outcomes) == ((0.8, 0.8),)
    assert terminal_value(((0.8, 0.8),), 0.3) == pytest.approx(0.8)


def test_invalid_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        D2.evaluate(-0.01)
    with pytest.raises(ValueError):
        D2.evaluate_action(3, 0.5)
    with pytest.raises(ValueError):
        demand_sweep(D2, points=1)


def test_exact_tolerance_is_small_enough_for_ground_truth_checks() -> None:
    assert EXACT_TOL < 1e-10


def test_g2_runner_writes_hash_validated_reproducible_artifacts(tmp_path: Path) -> None:
    runner_path = Path("experiments/synthetic/g2/run_g2.py")
    spec = importlib.util.spec_from_file_location("g2_runner", runner_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = module.run(tmp_path)
    assert summary["d2_sweep"]["p_v_star"] == 0.0
    assert summary["d2_sweep"]["p_j_star"] == 0.5
    assert module.validate_manifest(tmp_path)
