import numpy as np
import inspect

from hls.contextual_capacity_selection import DCSLAConfig, DCSLASelector, choose_dcs_config


def test_selector_uses_local_accuracy_and_is_deterministic():
    questions = ["apple fruit tree", "apple fruit sweet", "engine motor car", "engine motor road"]
    tasks = ["biology", "biology", "physics", "physics"]
    outcomes = np.asarray([[1, 0], [1, 0], [0, 1], [0, 1]], dtype=np.uint8)
    selector = DCSLASelector(DCSLAConfig(k=1, ngram_range=(1, 1), task_weight=1), ["A", "B"])
    selector.fit(questions, tasks, outcomes, ["q1", "q2", "q3", "q4"])
    first = selector.predict_one("apple fruit ripe", "biology")
    second = selector.predict_one("apple fruit ripe", "biology")
    assert first["selected_model"] == "A"
    for key in ("selected_model", "selected_model_index", "local_accuracy",
                "neighbor_query_ids", "neighbor_similarity"):
        assert first[key] == second[key]
    assert first["local_accuracy"] == [1.0, 0.0]


def test_task_feature_unknown_at_training_is_not_inferred():
    questions = ["shared words red", "shared words blue"]
    outcomes = np.asarray([[1, 0], [0, 1]], dtype=np.uint8)
    selector = DCSLASelector(DCSLAConfig(k=1, ngram_range=(1, 1), task_weight=2), ["A", "B"])
    selector.fit(questions, [None, None], outcomes, ["q1", "q2"])
    assert selector.task_to_index == {}
    assert selector.predict_one("shared words red", "biology")["selected_model"] == "A"
    assert "correct" not in inspect.signature(selector.predict_one).parameters


def test_validation_only_vocabulary_cannot_enter_fitted_feature_map():
    selector = DCSLASelector(DCSLAConfig(1, (1, 1), 0), ["A", "B"])
    selector.fit(["training vocabulary alpha"], ["biology"],
                 np.asarray([[1, 0]], dtype=np.uint8), ["train-1"])
    assert "validationonlytoken" not in selector.vectorizer.vocabulary_
    transformed = selector.transform(["validationonlytoken"], ["biology"])
    assert transformed.shape[1] == selector.training_matrix.shape[1]


def test_validation_config_ties_have_declared_deterministic_order():
    candidates = [
        (DCSLAConfig(3, (1, 2), 0.5), 0.75),
        (DCSLAConfig(7, (1, 2), 0.5), 0.75),
        (DCSLAConfig(7, (1, 1), 1.0), 0.75),
        (DCSLAConfig(7, (1, 1), 0.0), 0.75),
    ]
    assert choose_dcs_config(candidates) == DCSLAConfig(7, (1, 1), 0.0)


def test_selector_rejects_bad_outcomes_and_empty_context():
    selector = DCSLASelector(DCSLAConfig(1, (1, 1), 0), ["A", "B"])
    try:
        selector.fit(["question"], [None], np.asarray([[1, 2]]), ["q1"])
    except ValueError as exc:
        assert "binary" in str(exc)
    else:
        raise AssertionError("non-binary model outcomes must be rejected")
    try:
        DCSLASelector._clean_text("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("empty query text must be rejected")
