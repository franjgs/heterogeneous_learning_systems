from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import experiments.run_hls_learning_mechanism_comparison as experiment
from hls.hls_lab_nk_nembhard import (
    NembhardDirectStateNK,
    advance_nembhard_experience_nk,
    nembhard_productive_outputs_nk,
)
from hls.hls_lab_nk_learning import mis_v2_transition_nk
from hls.linucb import alpha_from_delta


def test_nembhard_profile_calibration_matches_initial_mis_competence():
    zero_effort = tuple((0.0,) * 3 for _ in experiment.AGENTS)
    state = NembhardDirectStateNK.zeros(3, 3)
    _, productivity = nembhard_productive_outputs_nk(
        zero_effort, state, experiment.NEMBHARD_PROFILE,
    )
    assert tuple(value for row in productivity for value in row) == pytest.approx(
        tuple(value for row in experiment.INITIAL_COMPETENCE for value in row)
    )
    assert all(0.0 <= value <= 1.0 for row in productivity for value in row)


def test_both_mechanisms_update_only_the_assigned_agent_task():
    task, agent = 1, 2
    allocation = experiment.actions_for_task(task)[agent]
    mis_after = mis_v2_transition_nk(
        experiment.INITIAL_COMPETENCE, allocation, experiment.LEARNING, enabled=True,
    )
    assert mis_after[agent][task] > experiment.INITIAL_COMPETENCE[agent][task]
    assert all(mis_after[i][k] == experiment.INITIAL_COMPETENCE[i][k]
               for i in range(3) for k in range(3) if (i, k) != (agent, task))

    direct_before = NembhardDirectStateNK.zeros(3, 3)
    direct_after = advance_nembhard_experience_nk(direct_before, allocation)
    assert direct_after.experience[agent][task] == 1.0
    assert sum(map(sum, direct_after.experience)) == 1.0


def test_fixed_and_reactive_organizations_share_replay_and_feasible_resources():
    tasks = experiment.make_demand_trajectory(seed=7, horizon=30)
    alpha = alpha_from_delta(0.05)
    for mechanism in experiment.MECHANISMS:
        fixed = experiment.run_episode(mechanism, "FIXED_SPECIALIZED", tasks, alpha)
        reactive = experiment.run_episode(mechanism, "REACTIVE_P0", tasks, alpha)
        repeat = experiment.run_episode(mechanism, "LINUCB", tasks, alpha)
        repeat_again = experiment.run_episode(mechanism, "LINUCB", tasks, alpha)
        assert fixed["trace"] == experiment.run_episode(
            mechanism, "FIXED_SPECIALIZED", tasks, alpha,
        )["trace"]
        assert repeat["trace"] == repeat_again["trace"]
        assert fixed["total_resource_used"] == reactive["total_resource_used"] == 30.0
        assert fixed["trace"] == reactive["trace"]
        assert all(row["resource_used"] == 1.0 for row in fixed["trace"])
        assert all(0.0 <= row["reward_effective_output"] <= 1.0 for row in repeat["trace"])
        assert all(len(row["linucb_coefficients_after"]) == 3
                   for row in repeat["trace"])


def test_c5_demand_path_is_reproducible_and_has_all_phases():
    first = experiment.make_demand_trajectory(19, 90)
    assert first == experiment.make_demand_trajectory(19, 90)
    assert len(first) == 90
    assert set(first) == {0, 1, 2}
