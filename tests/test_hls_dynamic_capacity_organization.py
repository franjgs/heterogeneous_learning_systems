import numpy as np
import pytest

from hls.dynamic_capacity_organization import (
    cascade_predictions, fit_escalation_threshold, fit_router_price, irt_route,
    majority_vote, paired_stratified_bootstrap_delta, per_task_accuracy,
    select_train_validation_tradeoff_pair, sequential_cascade_cost, static_model_by_task,
)


def test_cascade_escalates_only_below_validation_threshold():
    threshold = fit_escalation_threshold([0.1, 0.2, 0.8, 0.9], 0.5)
    pred, escalated = cascade_predictions(
        ["A", "B", "C", "D"], [0.1, 0.2, 0.8, 0.9],
        ["D", "D", "A", "A"], threshold.threshold,
    )
    assert escalated.tolist() == [True, True, False, False]
    assert pred.tolist() == ["D", "D", "C", "D"]
    assert threshold.validation_escalation_rate == 0.5


def test_sequential_cascade_charges_initial_and_activated_fallback():
    costs = sequential_cascade_cost([0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [False, True, True])
    assert costs.tolist() == pytest.approx([0.1, 0.7, 0.9])


def test_sequential_cascade_rejects_invalid_costs():
    with pytest.raises(ValueError, match="finite and non-negative"):
        sequential_cascade_cost([0.1], [-0.5], [True])


def test_static_task_selector_uses_only_supplied_training_outcomes():
    selected, mapping = static_model_by_task(
        ["x", "x", "y", "y"],
        np.asarray([[1, 0], [0, 1], [0, 1], [0, 1]]),
        ["x", "y", "x"], ["fast", "deep"],
    )
    assert mapping == {"x": "fast", "y": "deep"}
    assert selected.tolist() == [0, 1, 0]


def test_static_selector_rejects_unseen_test_task():
    with pytest.raises(ValueError, match="no training examples"):
        static_model_by_task(["x"], np.asarray([[1, 0]]), ["y"], ["a", "b"])


def test_irt_router_and_validation_price_are_deterministic():
    q = np.asarray([[0.8, 0.9], [0.6, 0.7]])
    c = np.asarray([[1.0, 3.0], [1.0, 3.0]])
    assert irt_route(q, c, 0).tolist() == [1, 1]
    price_a, cost_a = fit_router_price(q, c, 0.0)
    price_b, cost_b = fit_router_price(q, c, 0.0)
    assert (price_a, cost_a) == (price_b, cost_b)
    assert cost_a == 1.0


def test_plurality_vote_uses_declared_tie_break_answer():
    answers = np.asarray([["A", "B", "B"], ["A", "B", "C"], ["D", "D", "A"]])
    assert majority_vote(answers, tie_break_model_index=0).tolist() == ["B", "A", "D"]


def test_paired_stratified_bootstrap_is_reproducible_and_paired():
    first = [1, 0, 1, 1, 0, 1]
    second = [0, 0, 1, 0, 0, 1]
    tasks = ["x", "x", "x", "y", "y", "y"]
    a = paired_stratified_bootstrap_delta(first, second, tasks, n_boot=500, seed=7)
    b = paired_stratified_bootstrap_delta(first, second, tasks, n_boot=500, seed=7)
    assert a == b
    assert a[0] == pytest.approx(1 / 3)
    assert a[1] <= a[0] <= a[2]


def test_task_accuracy_is_reported_separately():
    assert per_task_accuracy(["A", "B", "C"], ["A", "A", "C"], ["x", "x", "y"]) == {
        "x": 0.5, "y": 1.0,
    }


def test_pair_selection_requires_train_and_validation_quality_cost_tradeoff():
    models = ["small", "middle", "large"]
    pair = select_train_validation_tradeoff_pair(
        models,
        {"small": 0.30, "middle": 0.45, "large": 0.60},
        {"small": 0.2, "middle": 0.4, "large": 0.8},
        {"small": 0.32, "middle": 0.47, "large": 0.57},
        {"small": 0.21, "middle": 0.42, "large": 0.82},
    )
    assert pair == ("small", "large")


def test_pair_selection_does_not_use_test_or_select_non_tradeoff():
    models = ["small", "large"]
    pair = select_train_validation_tradeoff_pair(
        models,
        {"small": 0.3, "large": 0.6},
        {"small": 0.8, "large": 0.4},
        {"small": 0.3, "large": 0.6},
        {"small": 0.8, "large": 0.4},
    )
    assert pair is None
