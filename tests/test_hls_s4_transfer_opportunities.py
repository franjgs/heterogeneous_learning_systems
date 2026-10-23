"""Focused validation for S4 transfer-opportunity calibration/evaluation."""

import pytest

from experiments.run_hls_s4_transfer_opportunities import (
    CALIBRATION_SEEDS,
    EVAL_SEEDS,
    TRAIN_SEEDS,
    calibrate,
    execute,
    opportunity_diagnostics,
    problems_for_seed,
    scenario,
    summarize,
)
from hls.hls_lab_nk_policies import (
    NKDecisionView,
    P0ProductionOnlyPolicyNK,
    P1FixedTeachingNK,
    P2AdaptiveTeachingNK,
)
from experiments.run_hls_s4_transfer_interaction import RELATIONS


def test_calibration_is_policy_independent_and_selects_physical_potential():
    selected, calibration = calibrate()
    assert selected == pytest.approx(.05)
    assert set(CALIBRATION_SEEDS).isdisjoint(TRAIN_SEEDS)
    assert set(CALIBRATION_SEEDS).isdisjoint(EVAL_SEEDS)
    assert set(TRAIN_SEEDS).isdisjoint(EVAL_SEEDS)
    assert calibration["method"].startswith("ordered deterministic candidate screen")
    assert all(row["criteria_pass"] is False for row in calibration["candidates"][:-1])
    assert calibration["candidates"][-1]["criteria_pass"] is True
    assert calibration["candidates"][-1]["initial_max_y_output_no_lesson"] < .70
    assert calibration["candidates"][-1]["one_lesson_gain_at_initial_B_y"] > 0
    assert calibration["candidates"][-1]["cumulative_ces_difference_lesson_minus_no_lesson_mean"] > 0
    assert sum(row["difference"] > 0 for row in
               calibration["candidates"][-1]["cumulative_ces_difference_by_calibration_seed"]) >= 8


def test_calibrated_physics_and_demand_preserve_feasible_teaching_costs():
    setup = scenario(.05)
    assert setup["environment"].horizon == 24
    assert setup["environment"].resource_budget == pytest.approx(2.0)
    assert setup["organization"].effort_limits == (1.0, 1.0)
    assert setup["learning"].eta[1][1] == pytest.approx(.05)
    assert setup["environment"].emissions["y"].problems[0].requirements == (0.0, .70)
    assert setup["efficacy"].values[0][1][1] == pytest.approx(.80)
    assert setup["teaching_parameters"].transfer_rate == pytest.approx(.4)
    assert NKDecisionView.__dataclass_fields__.get("competence_real") is None
    assert NKDecisionView.__dataclass_fields__.get("teaching_efficacy") is None


def test_existing_policies_share_demand_and_respect_resources_in_calibration_scenario():
    setup = scenario(.05)
    problems = problems_for_seed(setup, 44200)
    opportunities = opportunity_diagnostics(setup, problems)
    assert opportunities["periods_with_any_feasible_lesson"] == 24
    assert opportunities["periods_with_feasible_current_skill_lesson"] == 24
    assert all(row["feasible_current_skill_lesson_actions"] > 0
               for row in opportunities["per_period"])
    policies = (
        P0ProductionOnlyPolicyNK(),
        P1FixedTeachingNK(RELATIONS[0]),
        P2AdaptiveTeachingNK(RELATIONS),
    )
    runs = [execute(setup, problems, policy) for policy in policies]
    expected_ids = tuple(problem.problem_id for problem in problems)
    for run in runs:
        assert tuple(row.production.problem_id for row in run.records) == expected_ids
        assert all(row.total_resource_used <= 2.0 + 1e-12 for row in run.records)
        assert all(row.unused_collective_capacity >= -1e-12 for row in run.records)
        assert run.records[0].competence_actual_before == setup["organization"].competence_initial
        assert run.records[-1].competence_actual_after == run.final_state.competence_real
    assert all(row.action.teaching is None for row in runs[0].records)
    assert summarize(runs[0])["teaching_effort"] == pytest.approx(0.0)
    assert summarize(runs[2])["lessons"] >= 0


def test_closed_loop_replays_deterministically_for_fixed_policy_and_seed():
    setup = scenario(.05)
    problems = problems_for_seed(setup, 44201)
    policy = P2AdaptiveTeachingNK(RELATIONS)
    first = execute(setup, problems, policy)
    second = execute(setup, problems, policy)
    assert first == second

