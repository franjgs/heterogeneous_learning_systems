import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.run_hls_rq1_learning_organization import (
    HORIZON,
    INITIAL_COMPETENCE,
    LEARNING_ETA,
    TASKS,
    allocation_for,
    build_model,
    generate_trajectories,
    next_competence,
    run_episode,
    task_score,
)
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk


def test_c5_trajectory_replays_for_same_seed():
    _, _, _, environment, _ = build_model()
    first = generate_trajectories(environment, (123,))
    second = generate_trajectories(environment, (123,))
    assert first == second
    assert len(first[0]) == HORIZON
    assert set(first[0]) == set(TASKS)


def test_competence_update_matches_existing_mis_v2_transition():
    organization, learning, _, _, _ = build_model()
    allocation = allocation_for(1, (3, 0.5))
    expected = mis_v2_transition_nk(
        INITIAL_COMPETENCE, allocation, LearningProfileNK(LEARNING_ETA), enabled=True,
    )
    assert next_competence(INITIAL_COMPETENCE, allocation, learning) == expected
    assert expected[3][1] > INITIAL_COMPETENCE[3][1]
    assert expected[0] == INITIAL_COMPETENCE[0]
    assert organization.collective_effort_budget == pytest.approx(1.0)


def test_replay_is_deterministic_and_all_actions_conserve_resources():
    organization, learning, problems, environment, actions = build_model()
    trajectory = generate_trajectories(environment, (456,))[0]
    mapping = (actions[0], actions[2], actions[4])
    probabilities = tuple(
        tuple(environment.process.distributions[t][task] for task in TASKS)
        for t in range(HORIZON)
    )
    first = run_episode(trajectory, "ANTICIPATORY", mapping, organization,
                        problems, actions, learning, probabilities)
    second = run_episode(trajectory, "ANTICIPATORY", mapping, organization,
                         problems, actions, learning, probabilities)
    assert first == second
    assert len(first["trace"]) == HORIZON
    for index, row in enumerate(first["trace"]):
        task_index = TASKS.index(row["task"])
        action = ("ABCDE".index(row["assigned_agent"]), row["effort"])
        allocation = allocation_for(task_index, action)
        assert sum(map(sum, allocation)) <= organization.collective_effort_budget + 1e-12
        assert all(sum(agent_row) <= organization.effort_limits[i] + 1e-12
                   for i, agent_row in enumerate(allocation))
        expected_reward, expected_success, _ = task_score(
            row["competence_before"], task_index, action, problems[task_index],
        )
        assert row["reward"] == pytest.approx(expected_reward)
        assert row["success"] is expected_success
        if index + 1 < HORIZON:
            assert first["trace"][index + 1]["competence_before"] == row["competence_after"]
