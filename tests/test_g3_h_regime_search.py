"""Reproducibility and domain controls for the G3-H existence sampler."""

from hls.g3_h_regime_search import INTERIOR_EPSILON, search


def test_homogeneous_search_is_reproducible_and_preserves_equal_learning_rates() -> None:
    first = search(condition="homogeneous", samples=20, seed=912)
    second = search(condition="homogeneous", samples=20, seed=912)
    assert first.best_use == second.best_use
    assert first.best_local == second.best_local
    assert (first.state_min, first.state_max, first.eta_min, first.eta_max) == (
        second.state_min, second.state_max, second.eta_min, second.eta_max
    )
    assert (first.positive_use_count, first.positive_local_count) == (
        second.positive_use_count, second.positive_local_count
    )
    assert first.state_min >= INTERIOR_EPSILON
    assert first.state_max <= 1.0 - INTERIOR_EPSILON
    assert len(set(first.best_use.learning_profile)) == 1
    assert len(set(first.best_local.learning_profile)) == 1


def test_heterogeneous_search_remains_within_the_canonical_domains() -> None:
    result = search(condition="heterogeneous", samples=20, seed=913)
    assert result.state_min >= INTERIOR_EPSILON
    assert result.state_max <= 1.0 - INTERIOR_EPSILON
    assert result.eta_min >= 0.0
    assert result.eta_max >= result.eta_min
