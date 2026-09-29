"""Reference gate for C5 dynamic task demand."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from hls.synthetic.c5 import (
    MarkovTaskDemand,
    NonStationaryTaskDemand,
    StationaryTaskDemand,
)
from hls.synthetic.randomness import SeededRandomSource
from hls.synthetic.state import WorldState


STATE = WorldState(((0.8, 0.4), (0.5, 0.7)))


@dataclass(frozen=True)
class _Record:
    task: object


def test_stationary_degenerate_control():
    q = StationaryTaskDemand({1: 1.0, 2: 0.0})
    rng = SeededRandomSource(123)
    assert [q.sample_task(t, STATE, (), rng) for t in range(10)] == [1] * 10


def test_stationary_is_reproducible_under_same_seed():
    q = StationaryTaskDemand({1: 0.3, 2: 0.7})
    a = SeededRandomSource(17)
    b = SeededRandomSource(17)

    xa = [q.sample_task(t, STATE, (), a) for t in range(20)]
    xb = [q.sample_task(t, STATE, (), b) for t in range(20)]

    assert xa == xb


def test_nonstationary_distribution_changes_with_time():
    q = NonStationaryTaskDemand({
        0: {1: 1.0, 2: 0.0},
        1: {1: 0.0, 2: 1.0},
    })
    rng = SeededRandomSource(0)

    assert q.sample_task(0, STATE, (), rng) == 1
    assert q.sample_task(1, STATE, (), rng) == 2


def test_nonstationary_missing_time_rejected():
    q = NonStationaryTaskDemand({0: {1: 1.0}})
    with pytest.raises(IndexError):
        q.sample_task(1, STATE, (), SeededRandomSource(0))


def test_markov_uses_previous_realized_task():
    q = MarkovTaskDemand(
        initial_distribution={1: 1.0, 2: 0.0},
        transitions={
            1: {1: 0.0, 2: 1.0},
            2: {1: 1.0, 2: 0.0},
        },
    )
    rng = SeededRandomSource(0)

    q0 = q.sample_task(0, STATE, (), rng)
    q1 = q.sample_task(1, STATE, (_Record(q0),), rng)
    q2 = q.sample_task(2, STATE, (_Record(q0), _Record(q1)), rng)

    assert (q0, q1, q2) == (1, 2, 1)


def test_markov_requires_history_after_initial_time():
    q = MarkovTaskDemand(
        {1: 1.0},
        {1: {1: 1.0}},
    )
    with pytest.raises(ValueError):
        q.sample_task(1, STATE, (), SeededRandomSource(0))


@pytest.mark.parametrize(
    "distribution",
    [
        {},
        {1: -0.1, 2: 1.1},
        {1: 0.2, 2: 0.2},
        {1: float("nan")},
        {1: float("inf")},
    ],
)
def test_invalid_distribution_rejected(distribution):
    with pytest.raises(ValueError):
        StationaryTaskDemand(distribution)


def test_invalid_markov_task_set_rejected():
    with pytest.raises(ValueError):
        MarkovTaskDemand(
            {1: 0.5, 2: 0.5},
            {1: {1: 1.0}, 2: {1: 0.5, 2: 0.5}},
        )


def test_c5_regimes_are_distinct_capabilities():
    stationary = StationaryTaskDemand({1: 0.5, 2: 0.5})
    nonstationary = NonStationaryTaskDemand({
        0: {1: 1.0, 2: 0.0},
        1: {1: 0.0, 2: 1.0},
    })
    markov = MarkovTaskDemand(
        {1: 0.5, 2: 0.5},
        {
            1: {1: 0.9, 2: 0.1},
            2: {1: 0.1, 2: 0.9},
        },
    )

    assert stationary.__class__ is not nonstationary.__class__
    assert markov.__class__ is not stationary.__class__


def _environment_with_tasks(tasks, seed=0):
    from hls.synthetic import SyntheticEnvironment
    from hls.synthetic.components import (
        A1MixtureOpportunityKernel,
        A1ResourceModel,
        BoundedMatrixCompetence,
        CompetenceRewardModel,
        ContractInformationModel,
        ScheduledSaturatingDevelopmentKernel,
    )
    from hls.synthetic.randomness import SeededRandomSource

    learners = {"M1": 0, "M2": 1}
    task_indices = {1: 0, 2: 1}

    return SyntheticEnvironment(
        tasks=tasks,
        competence=BoundedMatrixCompetence(((0.8, 0.4), (0.5, 0.7))),
        opportunities=A1MixtureOpportunityKernel(
            {1: 0.0, 2: 0.0},
            {
                ("M1", 1): 0.0,
                ("M2", 1): 0.0,
                ("M1", 2): 0.0,
                ("M2", 2): 0.0,
            },
            rho=1.0,
        ),
        development=ScheduledSaturatingDevelopmentKernel(
            learners, task_indices, {0: 1, 1: 2}, eta=0.5
        ),
        reward=CompetenceRewardModel(learners, task_indices),
        resources=A1ResourceModel(kappa=0.0, beta=1.0),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(seed),
    )


def test_environment_preserves_finite_deterministic_task_sequence():
    from hls.synthetic.components import FiniteTaskSequence
    from hls.synthetic.trajectory import Trajectory

    env = _environment_with_tasks(FiniteTaskSequence((1, 2)))
    trajectory = Trajectory()

    s0 = env.initial_state()
    assert env.task_at(s0, trajectory) == 1

    # Only time matters here; no transition needs to be sampled.
    s1 = s0.advanced(s0.competence)
    assert env.task_at(s1, trajectory) == 2


def test_environment_samples_stationary_c5_demand():
    from hls.synthetic.trajectory import Trajectory

    env = _environment_with_tasks(
        StationaryTaskDemand({1: 0.0, 2: 1.0}),
        seed=123,
    )

    assert env.task_at(env.initial_state(), Trajectory()) == 2


def test_environment_samples_nonstationary_c5_demand():
    from hls.synthetic.trajectory import Trajectory

    env = _environment_with_tasks(
        NonStationaryTaskDemand({
            0: {1: 1.0, 2: 0.0},
            1: {1: 0.0, 2: 1.0},
        }),
        seed=123,
    )

    trajectory = Trajectory()
    s0 = env.initial_state()
    s1 = s0.advanced(s0.competence)

    assert env.task_at(s0, trajectory) == 1
    assert env.task_at(s1, trajectory) == 2


def test_environment_markov_demand_uses_realized_trajectory_history():
    from hls.synthetic.interfaces import NULL_DEVELOPMENT
    from hls.synthetic.trajectory import Trajectory

    env = _environment_with_tasks(
        MarkovTaskDemand(
            initial_distribution={1: 1.0, 2: 0.0},
            transitions={
                1: {1: 0.0, 2: 1.0},
                2: {1: 1.0, 2: 0.0},
            },
        ),
        seed=123,
    )

    trajectory = Trajectory()
    s0 = env.initial_state()

    # q0 is deterministically task 1.
    record0 = env.sample_transition(
        s0,
        operational_action="M1",
        development_action=NULL_DEVELOPMENT,
        trajectory=trajectory,
    )
    assert record0.task == 1

    trajectory1 = trajectory.append(record0)

    # Markov Q now conditions on the actually recorded q0.
    assert env.task_at(record0.next_state, trajectory1) == 2

