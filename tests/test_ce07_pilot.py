import numpy as np

from hls import ce04
from hls.ce04 import Task
from hls.ce07_pilot import PERMUTATION_STREAM, agent_permutation, matched_potential_digest, _ce07_runtime
from hls.ce07_structure import competence_matrices, rename_agent_rows


def test_label_permutation_is_seeded_independent_and_a_valid_bijection():
    first = agent_permutation(30010)
    assert first == agent_permutation(30010)
    assert sorted(first) == list(range(12))
    assert len({agent_permutation(s) for s in (30010, 30011, 30012)}) == 3
    assert PERMUTATION_STREAM == 707


def test_potential_table_pairing_digest_is_reproducible_without_simulation():
    a, b = competence_matrices()
    p = agent_permutation(30010)
    qa, qb = rename_agent_rows(a, p), rename_agent_rows(b, p)
    tasks = (Task(0, .2, 0, 0, 3.2), Task(1, .8, 2, 0, 3.8))
    x = matched_potential_digest(30010, tasks, qa, qb)
    assert x == matched_potential_digest(30010, tasks, qa, qb)
    assert len(x) == 64


def test_tie_instrumentation_calls_original_selector_and_restores_ce04():
    a, b = competence_matrices()
    original_comp = ce04.competency_matrix
    original_choose = ce04._choose_with_tie
    events = []
    q = rename_agent_rows(b, agent_permutation(30010))
    with _ce07_runtime({"CE07_A": q}, events):
        scores = list(q[:, 0])
        eligible = list(range(12))
        priority = np.arange(12)[::-1]
        actual = ce04._choose_with_tie(scores, eligible, priority)
        expected = original_choose(scores, eligible, priority)
        assert actual == expected
        assert len(events) == 1
        assert events[0]["exact_tie_candidates"] == np.flatnonzero(q[:, 0] == .9).tolist()
    assert ce04.competency_matrix is original_comp
    assert ce04._choose_with_tie is original_choose
