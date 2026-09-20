from __future__ import annotations

import numpy as np

from hls.b1_empirical_interaction import (
    cluster_competence_profiles,
    delta_vector,
    gamma_value,
    normalized_confusion_profiles,
    select_transfer_indices,
    stratified_four_way_indices,
)


def test_confusion_profiles_are_row_normalized() -> None:
    profiles = normalized_confusion_profiles(
        [0, 0, 1, 1, 2, 2], [0, 1, 1, 1, 2, 0], n_classes=3
    )
    assert profiles.shape == (3, 3)
    assert np.allclose(profiles.sum(axis=1), 1.0)
    assert np.allclose(profiles[0], [0.5, 0.5, 0.0])


def test_clustering_and_transfer_selection_are_reproducible() -> None:
    profiles = np.eye(4)
    first = cluster_competence_profiles(profiles, n_clusters=2)
    second = cluster_competence_profiles(profiles, n_clusters=2)
    assert np.array_equal(first, second)
    labels = np.repeat(np.arange(4), 5)
    selected_a = select_transfer_indices(labels, [1, 2], budget=4, seed=17)
    selected_b = select_transfer_indices(labels, [1, 2], budget=4, seed=17)
    assert np.array_equal(selected_a, selected_b)
    assert len(selected_a) == 4
    assert set(labels[selected_a]).issubset({1, 2})


def test_gamma_delta_and_split_have_expected_semantics() -> None:
    assert abs(gamma_value(0.8, 0.7, 0.6, 0.65) - 0.15) <= 1e-12
    assert np.allclose(delta_vector([0.8, 0.4], [0.5, 0.5]), [0.3, -0.1])

    labels = np.repeat(np.arange(10), 10)
    splits = stratified_four_way_indices(labels, seed=3)
    all_indices = [set(values.tolist()) for values in splits.values()]
    assert sum(map(len, all_indices)) == len(labels)
    assert len(set.union(*all_indices)) == len(labels)
    assert all_indices[0].isdisjoint(all_indices[1])
    assert all_indices[0].isdisjoint(all_indices[2])
    assert all_indices[0].isdisjoint(all_indices[3])
