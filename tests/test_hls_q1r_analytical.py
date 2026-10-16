"""Exact, two-period check of the Q1-R architecture × demand × MIS interaction.

This is a mathematical diagnostic over all demand paths, not a campaign or
Monte Carlo estimate. It deliberately calls the current P0/MIS-v2 runner.
"""

from itertools import product

import pytest

from hls.hls_lab_dynamic import LearningProfile
from hls.hls_lab_v1 import ProblemSpec, make_team
from hls.hls_lab_v1_integrated import (
    IntegratedProblem,
    P0ProductionOnly,
    TeachingEfficacy,
    TeachingParameters,
    run_integrated_sequence,
)


ARCHITECTURES = {
    "G": ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)),
    "H": ((0.6, 0.4), (0.4, 0.6), (0.5, 0.5)),
}
PATHS = tuple(product((0, 1), repeat=2))
TASKS = (
    IntegratedProblem(ProblemSpec("skill-0", (0.1, 0.0), 2.0, 1.0), (1.0, 0.0), "skill-0"),
    IntegratedProblem(ProblemSpec("skill-1", (0.0, 0.1), 2.0, 1.0), (0.0, 1.0), "skill-1"),
)
LEARNING = LearningProfile(((0.1, 0.1), (0.1, 0.1), (0.1, 0.1)))
NO_TEACHING = TeachingEfficacy(tuple(
    tuple((0.0, 0.0) if instructor == learner else (0.5, 0.5)
          for learner in range(3))
    for instructor in range(3)
))
PARAMETERS = TeachingParameters(production_observation_noise_sd=0.0)


def _path_probability(path, demand):
    # Both processes start from stationary pi=(1/2, 1/2). Markov persistence
    # is P(same)=0.8; IID has P(same)=0.5.
    if demand == "iid":
        return 0.25
    return 0.4 if path[0] == path[1] else 0.1


def _path_reward(architecture, path, *, mis):
    result = run_integrated_sequence(
        make_team(ARCHITECTURES[architecture]),
        tuple(TASKS[task] for task in path),
        P0ProductionOnly(),
        learning=LEARNING,
        teaching_efficacy=NO_TEACHING,
        parameters=PARAMETERS,
        individual_learning=mis,
        organizational_learning=False,
    )
    return result.records[-1].cumulative_ces_reward, result


def _expected_reward(architecture, demand, *, mis):
    return sum(
        _path_probability(path, demand) * _path_reward(architecture, path, mis=mis)[0]
        for path in PATHS
    )


def test_exact_q1r_enumeration_has_zero_theta_off_and_nonzero_theta_on():
    # Architecture matching: equal per-skill and per-agent totals.
    for skill in range(2):
        assert sum(row[skill] for row in ARCHITECTURES["G"]) == pytest.approx(1.5)
        assert sum(row[skill] for row in ARCHITECTURES["H"]) == pytest.approx(1.5)
    assert tuple(map(sum, ARCHITECTURES["G"])) == pytest.approx((1.0, 1.0, 1.0))
    assert tuple(map(sum, ARCHITECTURES["H"])) == pytest.approx((1.0, 1.0, 1.0))

    values = {
        (architecture, demand, mis): _expected_reward(architecture, demand, mis=mis)
        for architecture in ("G", "H")
        for demand in ("iid", "markov")
        for mis in (False, True)
    }
    deltas = {
        (demand, mis): values["H", demand, mis] - values["G", demand, mis]
        for demand in ("iid", "markov")
        for mis in (False, True)
    }
    theta_off = deltas["markov", False] - deltas["iid", False]
    theta_on = deltas["markov", True] - deltas["iid", True]

    assert values["G", "iid", False] == pytest.approx(2.0)
    assert values["H", "iid", False] == pytest.approx(2.2)
    assert values["G", "markov", False] == pytest.approx(2.0)
    assert values["H", "markov", False] == pytest.approx(2.2)
    assert theta_off == pytest.approx(0.0, abs=1e-12)

    assert values["G", "iid", True] == pytest.approx(2.05)
    assert values["H", "iid", True] == pytest.approx(2.245)
    assert values["G", "markov", True] == pytest.approx(2.08)
    assert values["H", "markov", True] == pytest.approx(2.272)
    assert deltas["iid", True] == pytest.approx(0.195)
    assert deltas["markov", True] == pytest.approx(0.192)
    assert theta_on == pytest.approx(-0.003)

    # Independent pathwise check of the repeated-vs-switched-task mechanism.
    same_gap = (
        _path_reward("H", (0, 0), mis=True)[0]
        - _path_reward("G", (0, 0), mis=True)[0]
    )
    switched_gap = (
        _path_reward("H", (0, 1), mis=True)[0]
        - _path_reward("G", (0, 1), mis=True)[0]
    )
    assert same_gap == pytest.approx(0.19)
    assert switched_gap == pytest.approx(0.20)


def test_zero_mis_freezes_true_competencies_in_q1r_fixture():
    for architecture in ARCHITECTURES:
        _, result = _path_reward(architecture, (0, 0), mis=False)
        assert result.records[0].competence_real_after == ARCHITECTURES[architecture]
        assert result.records[1].competence_real_after == ARCHITECTURES[architecture]
