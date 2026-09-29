"""Acceptance tests for C2 collective portfolio geometry."""

from __future__ import annotations

import pytest

from hls.synthetic.c2 import (
    diagnose_geometry,
    reference_matrices,
    reference_models,
    relabel_competence,
)


def test_reference_worlds_are_genuine_m3_k4_g0_models():
    models = reference_models()
    assert len(models) == 6
    for model in models.values():
        state = model.initial_state()
        assert state.n_learners == 3
        assert state.n_competences == 4
        model.validate(state)


def test_dominance_reference():
    g = diagnose_geometry(reference_matrices()["dominance"])
    assert g.globally_dominant == frozenset({0})
    assert g.dominated_learners == frozenset({1, 2})
    assert g.has_global_dominance


def test_redundancy_reference():
    g = diagnose_geometry(reference_matrices()["redundancy"])
    assert (0, 1) in g.redundant_pairs
    assert g.has_redundancy


def test_specialization_reference():
    g = diagnose_geometry(reference_matrices()["specialization"])
    assert g.has_specialization
    assert g.specialist_tasks[0] == frozenset({0})
    assert g.specialist_tasks[1] == frozenset({1})
    assert g.specialist_tasks[2] == frozenset({2, 3})


def test_complementarity_reference():
    g = diagnose_geometry(
        reference_matrices()["complementarity"],
        coverage_threshold=0.75,
    )
    assert g.collective_coverage == 1.0
    assert not g.globally_dominant
    assert g.has_collective_complementarity
    assert not g.uncovered_tasks


def test_collective_gap_reference():
    g = diagnose_geometry(
        reference_matrices()["collective_gap"],
        coverage_threshold=0.75,
    )
    assert g.uncovered_tasks == frozenset({3})
    assert g.collective_coverage == pytest.approx(0.75)


def test_mixed_reference_is_not_globally_dominated():
    g = diagnose_geometry(reference_matrices()["mixed_nondominated"])
    assert not g.globally_dominant
    assert not g.dominated_learners
    assert g.has_collective_complementarity


@pytest.mark.parametrize("name", list(reference_matrices()))
def test_learner_relabeling_preserves_scalar_geometry(name):
    matrix = reference_matrices()[name]
    original = diagnose_geometry(matrix)
    relabeled = diagnose_geometry(
        relabel_competence(matrix, learner_order=(2, 0, 1))
    )

    assert relabeled.n_learners == original.n_learners
    assert relabeled.n_competences == original.n_competences
    assert relabeled.task_best == pytest.approx(original.task_best)
    assert relabeled.collective_coverage == pytest.approx(
        original.collective_coverage
    )
    assert len(relabeled.globally_dominant) == len(original.globally_dominant)
    assert len(relabeled.dominated_learners) == len(original.dominated_learners)
    assert len(relabeled.redundant_pairs) == len(original.redundant_pairs)
    assert relabeled.has_specialization == original.has_specialization
    assert (
        relabeled.has_collective_complementarity
        == original.has_collective_complementarity
    )


@pytest.mark.parametrize("name", list(reference_matrices()))
def test_task_relabeling_preserves_collective_properties(name):
    matrix = reference_matrices()[name]
    original = diagnose_geometry(matrix)
    relabeled = diagnose_geometry(
        relabel_competence(matrix, competence_order=(3, 1, 0, 2))
    )

    assert sorted(relabeled.task_best) == pytest.approx(
        sorted(original.task_best)
    )
    assert relabeled.collective_coverage == pytest.approx(
        original.collective_coverage
    )
    assert len(relabeled.globally_dominant) == len(original.globally_dominant)
    assert len(relabeled.dominated_learners) == len(original.dominated_learners)
    assert len(relabeled.redundant_pairs) == len(original.redundant_pairs)
    assert relabeled.has_specialization == original.has_specialization
    assert (
        relabeled.has_collective_complementarity
        == original.has_collective_complementarity
    )


def test_geometry_is_derived_not_stored():
    matrix = (
        (0.9, 0.2, 0.2),
        (0.2, 0.9, 0.2),
        (0.2, 0.2, 0.9),
    )
    g = diagnose_geometry(matrix)
    assert g.has_specialization
    assert g.has_collective_complementarity
    assert not g.has_global_dominance


def test_invalid_relabeling_rejected():
    matrix = reference_matrices()["dominance"]
    with pytest.raises(ValueError):
        relabel_competence(matrix, learner_order=(0, 0, 2))
    with pytest.raises(ValueError):
        relabel_competence(matrix, competence_order=(0, 1, 2, 2))


def test_invalid_coverage_threshold_rejected():
    with pytest.raises(ValueError):
        diagnose_geometry(reference_matrices()["dominance"], coverage_threshold=1.1)


def test_c1_c2_composition_repeated_evolution_m3_k4():
    """C1+C2 gate: repeated endogenous evolution on a genuine M=3,K=4 portfolio.

    This is a capability-composition test, not an HLS-vs-SEP experiment.
    It verifies that the existing G0 development semantics can evolve a
    collective C2 geometry over two successive cycles, with the second
    admissible development set derived from the already-evolved state.
    """
    from hls.synthetic.components import ScheduledSaturatingDevelopmentKernel
    from hls.synthetic.interfaces import DevelopmentDecision, Opportunity
    from hls.synthetic.state import WorldState

    learners = {"M1": 0, "M2": 1, "M3": 2}
    competences = {1: 0, 2: 1, 3: 2, 4: 3}

    initial = WorldState((
        (0.90, 0.30, 0.40, 0.20),
        (0.30, 0.90, 0.40, 0.20),
        (0.40, 0.40, 0.90, 0.20),
    ))

    kernel = ScheduledSaturatingDevelopmentKernel(
        learners,
        competences,
        {0: 4, 1: 4},
        eta=0.5,
    )

    available = Opportunity(True)

    # First endogenous competence transition: develop M1 on competence 4.
    admissible0 = kernel.admissible_actions(initial, available)
    d0 = DevelopmentDecision("M1", 4)
    assert d0 in admissible0

    s1 = kernel.transition(initial, available, d0)

    assert s1.time == 1
    expected_s1 = (
        (0.90, 0.30, 0.40, 0.60),
        (0.30, 0.90, 0.40, 0.20),
        (0.40, 0.40, 0.90, 0.20),
    )
    for actual, expected in zip(s1.competence, expected_s1):
        assert actual == pytest.approx(expected)

    # The second cycle acts on the already evolved collective state.
    admissible1 = kernel.admissible_actions(s1, available)
    d1 = DevelopmentDecision("M2", 4)
    assert d1 in admissible1

    s2 = kernel.transition(s1, available, d1)

    assert s2.time == 2
    expected_s2 = (
        (0.90, 0.30, 0.40, 0.60),
        (0.30, 0.90, 0.40, 0.60),
        (0.40, 0.40, 0.90, 0.20),
    )
    for actual, expected in zip(s2.competence, expected_s2):
        assert actual == pytest.approx(expected)

    # C2 diagnosis is applied independently after each C1-style transition.
    g0 = diagnose_geometry(initial.competence, coverage_threshold=0.75)
    g1 = diagnose_geometry(s1.competence, coverage_threshold=0.75)
    g2 = diagnose_geometry(s2.competence, coverage_threshold=0.75)

    assert g0.n_learners == g1.n_learners == g2.n_learners == 3
    assert g0.n_competences == g1.n_competences == g2.n_competences == 4

    # Competence 4 begins as a collective gap.
    assert 3 in g0.uncovered_tasks

    # Repeated evolution changes the collective state without changing shape.
    assert initial.competence != s1.competence
    assert s1.competence != s2.competence

    # No hidden two-learner assumption in the development kernel:
    # every learner remains an admissible recipient at both cycles.
    recipients0 = {
        action.recipient for action in admissible0 if not action.is_null
    }
    recipients1 = {
        action.recipient for action in admissible1 if not action.is_null
    }
    assert recipients0 == {"M1", "M2", "M3"}
    assert recipients1 == {"M1", "M2", "M3"}

