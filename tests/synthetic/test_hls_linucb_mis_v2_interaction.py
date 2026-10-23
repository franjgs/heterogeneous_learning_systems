from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from experiments.run_hls_linucb_mis_v2_interaction import (
    AGENTS,
    INITIAL_COMPETENCE,
    TASKS,
    _actions_for_task,
    _common_trajectory,
    _linucb_contexts,
    _run_policy,
)
from hls.hls_lab_nk_geometry import ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_production import P0ProductionOnlyNK
from hls.linucb import alpha_from_delta


def test_c5_and_outcome_shocks_replay_for_a_seed():
    first = _common_trajectory(17, 30)
    assert first == _common_trajectory(17, 30)
    assert len(first["tasks"]) == len(first["outcome_uniforms"]) == 30
    assert set(first["tasks"]) == {0, 1, 2}


def test_context_exposes_current_task_and_all_three_current_competencies():
    contexts = _linucb_contexts(1, INITIAL_COMPETENCE)
    assert contexts == (contexts[0],) * len(AGENTS)
    assert contexts[0] == pytest.approx((0, 1, 0, 0.20, 0.85, 0.20))


def test_reactive_selector_uses_existing_p0_current_production_rule():
    task = 2
    actions = _actions_for_task(task)
    problem = ProblemSpecNK("task_2", (0.0, 0.0, 0.90), 1.0)
    competence = ((0.2, 0.3, 0.51), (0.3, 0.2, 0.83), (0.5, 0.4, 0.61))
    action_id, action = P0ProductionOnlyNK().choose(actions, competence, problem)
    assert action_id == 1
    assert action[1][task] == 1.0


def test_mis_v2_changes_only_the_assigned_agent_task_cell():
    action = _actions_for_task(1)[2]
    profile = LearningProfileNK(((0.15,) * 3,) * 3)
    updated = mis_v2_transition_nk(INITIAL_COMPETENCE, action, profile, enabled=True)
    assert updated[2][1] > INITIAL_COMPETENCE[2][1]
    assert updated[0] == INITIAL_COMPETENCE[0]
    assert updated[1] == INITIAL_COMPETENCE[1]
    assert mis_v2_transition_nk(INITIAL_COMPETENCE, action, profile, enabled=False) == INITIAL_COMPETENCE


def test_linucb_and_controls_share_task_path_resources_and_learning_opportunity():
    trajectory = _common_trajectory(23, 18)
    alpha = alpha_from_delta(0.05)
    assert _run_policy(trajectory, "LINUCB", True, alpha)["trace"] == _run_policy(
        trajectory, "LINUCB", True, alpha,
    )["trace"]
    evolving = {
        name: _run_policy(trajectory, name, True, alpha)
        for name in ("LINUCB", "FIXED_SPECIALIZED", "REACTIVE_P0")
    }
    constant = {
        name: _run_policy(trajectory, name, False, alpha)
        for name in ("LINUCB", "FIXED_SPECIALIZED", "REACTIVE_P0")
    }
    task_paths = {
        tuple(row["task"] for row in result["trace"])
        for condition in (evolving, constant)
        for result in condition.values()
    }
    assert len(task_paths) == 1
    for condition in (evolving, constant):
        assert all(len(result["trace"]) == 18 for result in condition.values())
        assert {result["resource_used"] for result in condition.values()} == {18.0}
        for result in condition.values():
            assert sum(result["selected_agent_counts"]) == 18
    assert evolving["LINUCB"]["trace"][0]["task"] == constant["LINUCB"]["trace"][0]["task"]
    assert evolving["LINUCB"]["trace"][0]["context"] == constant["LINUCB"]["trace"][0]["context"]
    first_task = int(evolving["FIXED_SPECIALIZED"]["trace"][0]["task"][-1])
    assert evolving["FIXED_SPECIALIZED"]["trace"][0]["selected_agent"] == f"agent_{first_task}"
    assert evolving["FIXED_SPECIALIZED"]["trace"][0]["updated_cell_after"][2] > INITIAL_COMPETENCE[first_task][first_task]
    assert constant["FIXED_SPECIALIZED"]["trace"][0]["updated_cell_after"][2] == INITIAL_COMPETENCE[first_task][first_task]
    assert tuple(tuple(row) for row in evolving["FIXED_SPECIALIZED"]["trace"][1]["competence_before"]) == (
        mis_v2_transition_nk(
            INITIAL_COMPETENCE,
            _actions_for_task(first_task)[first_task],
            LearningProfileNK(((0.15,) * 3,) * 3),
        )
    )
    # LinUCB emits the unmodified disjoint-model coefficient trace each period.
    row = evolving["LINUCB"]["trace"][0]
    assert len(row["linucb_scores_before"]) == 3
    assert len(row["linucb_coefficients_after"]) == 3
    assert all(len(coefficients) == 6 for coefficients in row["linucb_coefficients_after"])
