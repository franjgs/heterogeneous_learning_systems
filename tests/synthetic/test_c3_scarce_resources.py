"""Reference gate for C3 scarce development resources."""

from __future__ import annotations

import pytest

from hls.synthetic.c2 import diagnose_geometry
from hls.synthetic.c3 import (
    BudgetedDevelopmentResources,
    remaining_budget,
    with_development_budget,
)
from hls.synthetic.components import ScheduledSaturatingDevelopmentKernel
from hls.synthetic.interfaces import (
    DevelopmentDecision,
    NULL_DEVELOPMENT,
    Opportunity,
)
from hls.synthetic.state import WorldState


def _initial_state(budget: float) -> WorldState:
    state = WorldState((
        (0.90, 0.30, 0.40, 0.20),
        (0.30, 0.90, 0.40, 0.20),
        (0.40, 0.40, 0.90, 0.20),
    ))
    return with_development_budget(state, budget)


def _kernel():
    return ScheduledSaturatingDevelopmentKernel(
        {"M1": 0, "M2": 1, "M3": 2},
        {1: 0, 2: 1, 3: 2, 4: 3},
        {0: 4, 1: 4},
        eta=0.5,
    )


def test_budget_is_physical_world_state():
    s = _initial_state(1.0)
    assert remaining_budget(s) == pytest.approx(1.0)
    assert dict(s.resources) == {"development_budget": 1.0}


def test_null_action_never_consumes_budget():
    resources = BudgetedDevelopmentResources(1.0)
    s = _initial_state(1.0)
    assert resources.consume(s, NULL_DEVELOPMENT) == s.resources


def test_development_requires_opportunity_and_budget():
    resources = BudgetedDevelopmentResources(1.0)
    s = _initial_state(1.0)
    action = DevelopmentDecision("M1", 4)

    assert resources.development_is_admissible(s, action, Opportunity(True))
    assert not resources.development_is_admissible(s, action, Opportunity(False))

    empty = _initial_state(0.0)
    assert not resources.development_is_admissible(
        empty, action, Opportunity(True)
    )


def test_development_consumes_budget_exactly_once():
    resources = BudgetedDevelopmentResources(1.0)
    s = _initial_state(2.0)
    action = DevelopmentDecision("M1", 4)

    new_resources = resources.consume(s, action)
    next_state = s.advanced(s.competence, resources=new_resources)

    assert remaining_budget(next_state) == pytest.approx(1.0)


def test_budget_persists_when_competence_changes():
    s = _initial_state(1.0)
    kernel = _kernel()
    action = DevelopmentDecision("M1", 4)

    evolved = kernel.transition(s, Opportunity(True), action)

    assert evolved.time == 1
    assert remaining_budget(evolved) == pytest.approx(1.0)


def test_one_unit_budget_blocks_second_development():
    resource_model = BudgetedDevelopmentResources(1.0)
    kernel = _kernel()
    available = Opportunity(True)

    s0 = _initial_state(1.0)
    d0 = DevelopmentDecision("M1", 4)

    assert resource_model.development_is_admissible(s0, d0, available)

    physical_s1 = kernel.transition(s0, available, d0)
    consumed = resource_model.consume(s0, d0)
    s1 = WorldState(
        physical_s1.competence,
        time=physical_s1.time,
        resources=consumed,
    )

    assert remaining_budget(s1) == pytest.approx(0.0)

    d1 = DevelopmentDecision("M2", 4)
    assert not resource_model.development_is_admissible(s1, d1, available)
    assert resource_model.development_is_admissible(
        s1, NULL_DEVELOPMENT, available
    )


def test_two_unit_budget_allows_two_developments():
    resource_model = BudgetedDevelopmentResources(1.0)
    kernel = _kernel()
    available = Opportunity(True)

    s0 = _initial_state(2.0)

    d0 = DevelopmentDecision("M1", 4)
    physical_s1 = kernel.transition(s0, available, d0)
    s1 = WorldState(
        physical_s1.competence,
        time=physical_s1.time,
        resources=resource_model.consume(s0, d0),
    )

    d1 = DevelopmentDecision("M2", 4)
    assert resource_model.development_is_admissible(s1, d1, available)

    physical_s2 = kernel.transition(s1, available, d1)
    s2 = WorldState(
        physical_s2.competence,
        time=physical_s2.time,
        resources=resource_model.consume(s1, d1),
    )

    assert remaining_budget(s2) == pytest.approx(0.0)


def test_c1_c2_c3_composition_gate():
    """Repeated evolution + collective geometry + scarce persistent resources."""
    resource_model = BudgetedDevelopmentResources(1.0)
    kernel = _kernel()
    available = Opportunity(True)

    s0 = _initial_state(1.0)
    g0 = diagnose_geometry(s0.competence, coverage_threshold=0.75)
    assert g0.n_learners == 3
    assert g0.n_competences == 4
    assert 3 in g0.uncovered_tasks

    d0 = DevelopmentDecision("M1", 4)
    physical_s1 = kernel.transition(s0, available, d0)
    s1 = WorldState(
        physical_s1.competence,
        time=physical_s1.time,
        resources=resource_model.consume(s0, d0),
    )

    g1 = diagnose_geometry(s1.competence, coverage_threshold=0.75)
    assert s1.competence != s0.competence
    assert g1.n_learners == 3
    assert g1.n_competences == 4

    # C3 now changes the physically admissible continuation:
    # competence can evolve again under C1, but the exhausted resource
    # prevents a second non-null development.
    assert remaining_budget(s1) == pytest.approx(0.0)
    assert not resource_model.development_is_admissible(
        s1, DevelopmentDecision("M2", 4), available
    )


@pytest.mark.parametrize("budget", [-1.0, float("inf"), float("nan")])
def test_invalid_budget_rejected(budget):
    with pytest.raises(ValueError):
        _initial_state(budget)


@pytest.mark.parametrize("cost", [0.0, -1.0, float("inf"), float("nan")])
def test_invalid_development_cost_rejected(cost):
    with pytest.raises(ValueError):
        BudgetedDevelopmentResources(cost)


def test_g0_composes_c3_budget_consumption_with_c4_competence_transition():
    """G0 must compose C4 competence physics with persistent C3 resources."""
    from hls.synthetic.c3 import (
        BudgetedDevelopmentResources,
        remaining_budget,
        with_development_budget,
    )
    from hls.synthetic.c4 import CoupledDevelopmentKernel
    from hls.synthetic.components import (
        A1MixtureOpportunityKernel,
        BoundedMatrixCompetence,
        CompetenceRewardModel,
        ContractInformationModel,
        FiniteTaskSequence,
    )
    from hls.synthetic.environment import SyntheticEnvironment
    from hls.synthetic.interfaces import DevelopmentDecision
    from hls.synthetic.randomness import SeededRandomSource

    learners = {"M1": 0, "M2": 1, "M3": 2}
    competences = {1: 0, 2: 1, 3: 2}

    initial_matrix = (
        (0.8, 0.4, 0.2),
        (0.4, 0.8, 0.2),
        (0.4, 0.2, 0.8),
    )

    competence_model = BoundedMatrixCompetence(initial_matrix)

    development = CoupledDevelopmentKernel(
        learners,
        competences,
        {0: 2, 1: 3},
        eta=0.5,
        gamma={
            ("M1", 2, "M1", 1): 0.25,
            ("M1", 2, "M1", 3): 0.25,
        },
    )

    resources = BudgetedDevelopmentResources(
        budget_per_development=1.0,
        beta=1.0,
    )

    environment = SyntheticEnvironment(
        tasks=FiniteTaskSequence((1, 2)),
        competence=competence_model,
        opportunities=A1MixtureOpportunityKernel(
            {1: 1.0, 2: 1.0},
            {
                ("M1", 1): 1.0,
                ("M2", 1): 1.0,
                ("M3", 1): 1.0,
                ("M1", 2): 1.0,
                ("M2", 2): 1.0,
                ("M3", 2): 1.0,
            },
            rho=0.0,
        ),
        development=development,
        reward=CompetenceRewardModel(learners, competences),
        resources=resources,
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )

    # Inject the preregistered persistent development budget into S0.
    s0 = with_development_budget(environment.initial_state(), 2.0)

    d0 = DevelopmentDecision("M1", 2)

    record0 = environment.sample_transition(
        s0,
        operational_action="M1",
        development_action=d0,
    )
    s1 = record0.next_state

    # C4 happened.
    assert s1.competence != s0.competence
    assert s1.competence[0][1] > s0.competence[0][1]
    assert s1.competence[0][0] > s0.competence[0][0]
    assert s1.competence[0][2] > s0.competence[0][2]

    # C3 happened in the SAME transition.
    assert remaining_budget(s1) == 1.0

    d1 = DevelopmentDecision("M2", 3)

    record1 = environment.sample_transition(
        s1,
        operational_action="M1",
        development_action=d1,
    )
    s2 = record1.next_state

    assert remaining_budget(s2) == 0.0

    # A third non-null development is now physically inadmissible.
    assert not resources.development_is_admissible(
        s2,
        DevelopmentDecision("M3", 3),
        record1.opportunity,
    )


def test_budget_consumption_is_distinct_from_objective_cost():
    """One budget unit may be consumed without imposing objective penalty."""
    from hls.synthetic.c3 import (
        BudgetedDevelopmentResources,
        remaining_budget,
        with_development_budget,
    )
    from hls.synthetic.interfaces import DevelopmentDecision, Opportunity
    from hls.synthetic.state import WorldState

    resources = BudgetedDevelopmentResources(
        budget_per_development=1.0,
        objective_cost_per_development=0.0,
        beta=1.0,
    )
    state = with_development_budget(
        WorldState(((0.5,),)),
        1.0,
    )
    action = DevelopmentDecision("M1", 1)

    assert resources.development_is_admissible(
        state, action, Opportunity(True)
    )
    assert resources.development_cost(action) == 0.0

    consumed = resources.consume(state, action)
    next_state = state.advanced(
        state.competence,
        resources=consumed,
    )

    assert remaining_budget(next_state) == 0.0
    assert not resources.development_is_admissible(
        next_state, action, Opportunity(True)
    )
