"""Reference gate for C4 competence interactions."""

from __future__ import annotations

import pytest

from hls.synthetic.c2 import diagnose_geometry
from hls.synthetic.c3 import (
    BudgetedDevelopmentResources,
    remaining_budget,
    with_development_budget,
)
from hls.synthetic.c4 import CoupledDevelopmentKernel
from hls.synthetic.interfaces import DevelopmentDecision, NULL_DEVELOPMENT, Opportunity
from hls.synthetic.state import WorldState


LEARNERS = {"M1": 0, "M2": 1, "M3": 2}
COMPETENCES = {1: 0, 2: 1, 3: 2, 4: 3}


def _state() -> WorldState:
    return WorldState((
        (0.80, 0.40, 0.30, 0.20),
        (0.30, 0.80, 0.50, 0.20),
        (0.40, 0.30, 0.80, 0.20),
    ))


def _kernel(gamma):
    return CoupledDevelopmentKernel(
        LEARNERS,
        COMPETENCES,
        {0: 4, 1: 4},
        eta=0.5,
        gamma=gamma,
    )


def test_gamma_zero_recovers_independent_development():
    s0 = _state()
    kernel = _kernel({})
    s1 = kernel.transition(
        s0, Opportunity(True), DevelopmentDecision("M1", 4)
    )

    assert s1.competence[0][3] == pytest.approx(0.60)

    for i in range(3):
        for k in range(4):
            if (i, k) != (0, 3):
                assert s1.competence[i][k] == pytest.approx(
                    s0.competence[i][k]
                )


def test_positive_gamma_produces_transfer():
    s0 = _state()
    kernel = _kernel({
        ("M1", 4, "M1", 1): 0.5,
    })

    s1 = kernel.transition(
        s0, Opportunity(True), DevelopmentDecision("M1", 4)
    )

    # Direct: .20 + .5*(1-.20) = .60
    assert s1.competence[0][3] == pytest.approx(0.60)

    # Transfer: .80 + .5*.5*(1-.80) = .85
    assert s1.competence[0][0] == pytest.approx(0.85)


def test_negative_gamma_produces_interference():
    s0 = _state()
    kernel = _kernel({
        ("M1", 4, "M1", 1): -0.5,
    })

    s1 = kernel.transition(
        s0, Opportunity(True), DevelopmentDecision("M1", 4)
    )

    # Interference: .80 - .5*.5*.80 = .60
    assert s1.competence[0][0] == pytest.approx(0.60)


def test_cross_learner_transfer_is_representable():
    s0 = _state()
    kernel = _kernel({
        ("M1", 4, "M2", 2): 0.5,
    })

    s1 = kernel.transition(
        s0, Opportunity(True), DevelopmentDecision("M1", 4)
    )

    assert s1.competence[1][1] == pytest.approx(0.85)


def test_multiple_interactions_use_pretransition_state():
    s0 = _state()
    kernel = _kernel({
        ("M1", 4, "M1", 1): 0.5,
        ("M1", 4, "M2", 2): -0.5,
        ("M1", 4, "M3", 3): 1.0,
    })

    s1 = kernel.transition(
        s0, Opportunity(True), DevelopmentDecision("M1", 4)
    )

    assert s1.competence[0][0] == pytest.approx(0.85)
    assert s1.competence[1][1] == pytest.approx(0.60)
    assert s1.competence[2][2] == pytest.approx(0.90)


def test_null_action_has_no_competence_interaction():
    s0 = _state()
    kernel = _kernel({
        ("M1", 4, "M2", 2): 1.0,
    })

    s1 = kernel.transition(s0, Opportunity(True), NULL_DEVELOPMENT)

    assert s1.time == 1
    assert s1.competence == s0.competence


def test_no_opportunity_allows_only_null():
    s0 = _state()
    kernel = _kernel({
        ("M1", 4, "M2", 2): 1.0,
    })

    assert kernel.admissible_actions(
        s0, Opportunity(False)
    ) == (NULL_DEVELOPMENT,)


def test_c1_c2_c3_c4_composition_gate():
    """Repeated evolution + portfolio + scarcity + interaction."""
    resources = BudgetedDevelopmentResources(1.0)
    kernel = _kernel({
        # Developing M1 competence 4 transfers to M2 competence 2.
        ("M1", 4, "M2", 2): 0.5,
    })

    s0 = with_development_budget(_state(), 1.0)

    g0 = diagnose_geometry(s0.competence, coverage_threshold=0.75)
    assert g0.n_learners == 3
    assert g0.n_competences == 4

    action = DevelopmentDecision("M1", 4)
    opportunity = Opportunity(True)

    assert resources.development_is_admissible(
        s0, action, opportunity
    )

    physical_s1 = kernel.transition(s0, opportunity, action)

    s1 = WorldState(
        physical_s1.competence,
        time=physical_s1.time,
        resources=resources.consume(s0, action),
    )

    # C1: competence evolved through a transition.
    assert s1.competence != s0.competence

    # C2: collective M=3,K=4 geometry remains well-defined.
    g1 = diagnose_geometry(s1.competence, coverage_threshold=0.75)
    assert g1.n_learners == 3
    assert g1.n_competences == 4

    # C3: scarce resource has been consumed.
    assert remaining_budget(s1) == pytest.approx(0.0)

    # C4: another coordinate changed because of development interaction.
    assert s1.competence[1][1] > s0.competence[1][1]

    # Exhausted C3 resource prevents another development despite C4 physics.
    assert not resources.development_is_admissible(
        s1, DevelopmentDecision("M2", 4), opportunity
    )


@pytest.mark.parametrize("gamma", [-1.01, 1.01, float("inf"), float("nan")])
def test_invalid_gamma_rejected(gamma):
    with pytest.raises(ValueError):
        _kernel({
            ("M1", 4, "M2", 2): gamma,
        })


def test_unknown_gamma_coordinate_rejected():
    with pytest.raises(ValueError):
        _kernel({
            ("UNKNOWN", 4, "M2", 2): 0.5,
        })
