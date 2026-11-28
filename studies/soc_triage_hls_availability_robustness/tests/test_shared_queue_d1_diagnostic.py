from types import SimpleNamespace

import pytest

from studies.soc_triage_hls_availability_robustness.run_shared_queue_d1_diagnostic import (
    _confusion,
    _quantiles,
)


def test_confusion_matrix_uses_need_as_truth_and_recommendation_as_prediction():
    cases = {
        "tp": SimpleNamespace(need_l2=True, recommended_l2=True),
        "fn": SimpleNamespace(need_l2=True, recommended_l2=False),
        "fp": SimpleNamespace(need_l2=False, recommended_l2=True),
        "tn": SimpleNamespace(need_l2=False, recommended_l2=False),
    }
    assert _confusion(cases) == {"TP": 1, "FP": 1, "TN": 1, "FN": 1}


def test_quantile_summary_is_reproducible_and_handles_empty_samples():
    summary = _quantiles([0, 1, 2, 3, 4])
    assert summary["mean"] == pytest.approx(2)
    assert summary["p50"] == pytest.approx(2)
    assert summary["p90"] == pytest.approx(3.6)
    assert summary["p95"] == pytest.approx(3.8)
    assert summary["max"] == 4
    assert _quantiles([])["mean"] is None
