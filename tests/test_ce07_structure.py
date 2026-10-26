from collections import Counter

import numpy as np
import pytest

from hls.ce04 import _choose_with_tie, generate_workload, potential_correct, potential_service
from hls.ce06_heterogeneity import gini
from hls.ce07_structure import (CE07Config, competence_matrices, inverse_permutation,
                                rename_agent_rows, validate_structures)


def test_ce07_matrices_have_exact_marginals_maxima_and_different_row_multisets():
    a, b = competence_matrices()
    result = validate_structures(a, b)
    assert result["marginal_exact"] == "27/40"
    assert np.allclose(a.sum(axis=0), np.full(4, 8.1), rtol=0, atol=1e-14)
    assert np.allclose(b.sum(axis=0), np.full(4, 8.1), rtol=0, atol=1e-14)
    assert np.array_equal(a.max(axis=0), b.max(axis=0))
    assert Counter(map(tuple, a.tolist())) != Counter(map(tuple, b.tolist()))


def test_row_renaming_preserves_structure_invariants():
    a, b = competence_matrices()
    p = np.array([8, 1, 9, 2, 10, 3, 11, 4, 0, 5, 6, 7])
    assert validate_structures(rename_agent_rows(a, p), rename_agent_rows(b, p))["marginal_exact"] == "27/40"
    assert np.allclose(rename_agent_rows(a, p).sum(axis=0), a.sum(axis=0), rtol=0, atol=1e-14)
    with pytest.raises(ValueError):
        rename_agent_rows(a, [0] * 12)


def test_p1_decisions_are_equivariant_when_tie_priority_is_renamed_too():
    a, b = competence_matrices()
    p = np.array([1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    inv = inverse_permutation(p)
    q = b[:, 0]
    f = np.ones(12)
    scores = q * f
    rank = np.array([1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    eligible = list(range(12))
    original = _choose_with_tie(scores, eligible, rank)
    q_new, f_new, rank_new = q[p], f[p], rank[p]
    eligible_new = inv[np.asarray(eligible)].tolist()
    renamed = _choose_with_tie(q_new * f_new, eligible_new, rank_new)
    assert int(p[renamed]) == original


def test_fixed_index_tie_priority_is_not_invariant_under_matrix_only_rename():
    # B's F1 top group has three equal scores. Swapping physical agents 0 and
    # 1 while leaving the slot-based priority vector fixed changes the winner.
    _, b = competence_matrices()
    p = np.array([1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    rank = np.arange(12)
    q = b[:, 0]
    winner = _choose_with_tie(q, list(range(12)), rank)
    renamed_winner = _choose_with_tie(q[p], list(range(12)), rank)
    assert winner == 0
    assert renamed_winner == 0
    assert p[renamed_winner] != winner


def test_consistent_permutation_preserves_aggregate_metrics_and_paired_streams():
    a, b = competence_matrices()
    p = np.array([8, 1, 9, 2, 10, 3, 11, 4, 0, 5, 6, 7])
    # The CE-04 workload is composition-independent, and service/correctness
    # draws are keyed by seed, N, task, and agent identity.
    assert generate_workload(41, 12) == generate_workload(41, 12)
    assert potential_service(41, 12, 17, 2) == potential_service(41, 12, 17, 2)
    qlo, qhi = .6, .9
    assert int(potential_correct(41, 12, 17, 2, qlo)) <= int(potential_correct(41, 12, 17, 2, qhi))
    counts = np.arange(1, 13)
    outcomes = np.array([1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1])
    assert outcomes.sum() == outcomes[p].sum()
    assert np.isclose(gini(counts), gini(counts[p]))
    assert np.allclose(a[p].sum(axis=0), a.sum(axis=0), rtol=0, atol=1e-14)
    assert np.allclose(b[p].sum(axis=0), b.sum(axis=0), rtol=0, atol=1e-14)


def test_pilot_configuration_requires_three_ce_selected_distinct_seeds():
    config = CE07Config(seed_ids=(11, 12, 13))
    assert config.to_dict()["marginal_exact"] == "27/40"
    with pytest.raises(ValueError):
        CE07Config(seed_ids=(11, 11, 13))
