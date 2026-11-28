import pandas as pd

from tools.prepare_soctra_dataset import label_stats, transition


def test_label_stats_uses_negative_over_positive_imbalance():
    stats = label_stats(pd.Series([False, False, True, True]))
    assert stats["positive"] == 2
    assert stats["negative"] == 2
    assert stats["prevalence"] == 0.5
    assert stats["imbalance_ratio_negative_over_positive"] == 1.0


def test_transition_counts_boolean_changes():
    before = pd.Series([False, True, False], index=[10, 11, 12])
    after = pd.Series([True, False, False], index=[10, 11, 12])
    result = transition(before, after)
    assert result["false_to_true"] == 1
    assert result["true_to_false"] == 1
    assert result["unchanged"] == 1
    assert result["rows_not_in_both_stages"] == 0
    assert result["matrix_before_false_after_true"] == 1
