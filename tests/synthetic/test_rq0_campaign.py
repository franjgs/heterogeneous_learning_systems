"""Reference gate for the frozen preregistered RQ0-A/B campaign."""

import pytest

from hls.synthetic.c3 import remaining_budget
from hls.synthetic.rq0_campaign import (
    BASELINE_OPPORTUNITY,
    CONFIGURATIONS,
    ETA,
    HORIZON,
    TARGET_BY_TIME,
    TERMINAL_TASK,
    competence_matrix,
    world_by_name,
    worlds,
)


EXPECTED = {
    "B*":             (0.5, 1,  0.00, 0.5),
    "REDUNDANT":      (0.0, 1,  0.00, 0.5),
    "FREE_RESOURCE":  (0.5, 2,  0.00, 0.5),
    "NO_COUPLING":    (0.5, 1,  0.00, 0.0),
    "INTERFERENCE":   (0.5, 1, -0.25, 0.5),
    "TRANSFER":       (0.5, 1, +0.25, 0.5),
    "SPECIALIZED":    (1.0, 1,  0.00, 0.5),
    "MAX_COUPLING":   (0.5, 1,  0.00, 1.0),
    "NO_DEVELOPMENT": (0.5, 0,  0.00, 0.5),
}


def test_exactly_nine_frozen_configurations():
    assert len(CONFIGURATIONS) == 9
    assert {c.name for c in CONFIGURATIONS} == set(EXPECTED)

    for c in CONFIGURATIONS:
        assert (c.s, c.budget, c.gamma, c.rho) == EXPECTED[c.name]


def test_frozen_competence_geometries():
    expected_r = (
        (.60, .60, .60),
        (.60, .60, .60),
        (.60, .60, .60),
    )
    for actual, expected in zip(competence_matrix(0.0), expected_r):
        assert actual == pytest.approx(expected)

    expected_c = (
        (.75, .525, .525),
        (.525, .75, .525),
        (.525, .525, .75),
    )
    for actual, expected in zip(competence_matrix(.5), expected_c):
        assert actual == pytest.approx(expected)

    expected_s = (
        (.90, .45, .45),
        (.45, .90, .45),
        (.45, .45, .90),
    )
    for actual, expected in zip(competence_matrix(1.0), expected_s):
        assert actual == pytest.approx(expected)


def test_frozen_common_semantics():
    assert HORIZON == 2
    assert TERMINAL_TASK == 3
    assert ETA == pytest.approx(.75)
    assert TARGET_BY_TIME == {0: 2, 1: 3}
    assert BASELINE_OPPORTUNITY == {1: .5, 2: .5}


def test_all_worlds_are_executable_exact_problem_specs():
    built = worlds()

    assert len(built) == 9

    for world in built:
        assert world.problem.environment is world.environment
        assert world.problem.horizon == 2
        assert world.problem.terminal_task == 3
        assert tuple(world.problem.operational_actions) == ("M1", "M2", "M3")
        assert remaining_budget(world.initial_state) == pytest.approx(
            world.configuration.budget
        )


def test_b_star_is_exactly_preregistered():
    world = world_by_name("B*")
    c = world.configuration

    assert (c.s, c.budget, c.gamma, c.rho) == (.5, 1, 0.0, .5)


def test_rho_zero_removes_executor_dependence():
    world = world_by_name("NO_COUPLING")
    state = world.initial_state

    for task in (1, 2):
        probabilities = [
            world.environment.opportunities.probability(
                state, task, learner, ()
            )
            for learner in ("M1", "M2", "M3")
        ]
        assert probabilities == pytest.approx([.5, .5, .5])


def test_redundant_geometry_removes_executor_dependence():
    world = world_by_name("REDUNDANT")
    state = world.initial_state

    for task in (1, 2):
        probabilities = [
            world.environment.opportunities.probability(
                state, task, learner, ()
            )
            for learner in ("M1", "M2", "M3")
        ]
        assert probabilities[0] == pytest.approx(probabilities[1])
        assert probabilities[1] == pytest.approx(probabilities[2])


def test_c4_topology_matches_section_14_13():
    world = world_by_name("TRANSFER")
    gamma = dict(world.environment.development.gamma)

    # 3 learners x 3 possible source competences x 2 other competences.
    assert len(gamma) == 18

    for learner in ("M1", "M2", "M3"):
        for source in (1, 2, 3):
            for destination in (1, 2, 3):
                key = (learner, source, learner, destination)
                if source == destination:
                    assert key not in gamma
                else:
                    assert gamma[key] == pytest.approx(.25)

    # No inter-learner interaction.
    assert all(src_learner == dst_learner
               for src_learner, _, dst_learner, _ in gamma)


def test_gamma_zero_exactly_removes_c4_interactions():
    assert dict(world_by_name("B*").environment.development.gamma) == {}
