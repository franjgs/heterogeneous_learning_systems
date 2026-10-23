"""Semantic characterization of the stored deterministic S4 N×K reference.

These tests call the existing case factory and exact solvers but never invoke
the writer in run_hls_s4_transfer_exact.run(), so historical artifacts stay
untouched. No permanent S4 adapter is implemented here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from experiments.run_hls_s4_transfer_exact import make_case
from experiments.run_hls_pef_retrospective import run as evaluate_historical_pef
from hls.experiment_contract import ExperimentEvent, ExperimentRun, MetricValue, UnitDeclaration
from hls.hls_lab_nk_production import (
    ces_reward_nk,
    evaluate_problem_nk,
    productive_outputs_nk,
)
from hls.synthetic.hls_s4_transfer_exact import solve_bellman


S4_RESULT = Path("results/experiments/hls_s4_transfer_exact/results.json")


@pytest.fixture(scope="module")
def historical():
    return json.loads(S4_RESULT.read_text())


@pytest.fixture(scope="module")
def case_and_solutions():
    case = make_case()
    return case, {
        policy: solve_bellman(case, transfer_available=(policy == "B"))
        for policy in ("A", "B")
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_s4_exact_reference_reproduces_original_rewards_and_preserves_artifact(
    historical, case_and_solutions,
):
    before = _sha256(S4_RESULT)
    case, solutions = case_and_solutions
    assert case.organization.agent_ids == ("A", "B")
    assert case.organization.skill_ids == ("x", "y")
    assert tuple(problem.problem_id for problem in case.problems) == ("task-x", "task-y", "task-y")
    for policy in ("A", "B"):
        assert solutions[policy].value == pytest.approx(historical[policy]["value"], abs=1e-12)
        assert len(solutions[policy].periods) == historical["design"]["horizon"] == 3
        assert [row.reward for row in solutions[policy].periods] == pytest.approx(
            [row["reward"] for row in historical[policy]["periods"]], abs=1e-12,
        )
        for solved_row, stored_row in zip(solutions[policy].periods, historical[policy]["periods"]):
            assert all(actual == pytest.approx(expected, abs=1e-12)
                       for actual_row, expected_row in zip(
                           solved_row.action.production, stored_row["action"]["production"]
                       )
                       for actual, expected in zip(actual_row, expected_row))
            assert (None if solved_row.action.teaching is None else asdict(solved_row.action.teaching)) == stored_row["action"]["teaching"]
            assert all(actual == pytest.approx(expected, abs=1e-12)
                       for actual_row, expected_row in zip(
                           solved_row.competence_before, stored_row["competence_before"]
                       )
                       for actual, expected in zip(actual_row, expected_row))
            assert all(actual == pytest.approx(expected, abs=1e-12)
                       for actual_row, expected_row in zip(
                           solved_row.competence_after, stored_row["competence_after"]
                       )
                       for actual, expected in zip(actual_row, expected_row))
    assert solutions["A"].value == pytest.approx(1.9175, abs=1e-12)
    assert solutions["B"].value == pytest.approx(1.9175, abs=1e-12)
    assert _sha256(S4_RESULT) == before


def test_output_is_derived_from_individual_effort_and_competence(
    historical, case_and_solutions,
):
    case, _ = case_and_solutions
    for policy in ("A", "B"):
        for row in historical[policy]["periods"]:
            action = row["action"]["production"]
            competence = row["competence_before"]
            individual_output = tuple(
                tuple(action[i][k] * competence[i][k] for k in range(len(case.organization.skill_ids)))
                for i in range(len(case.organization.agent_ids))
            )
            aggregate = productive_outputs_nk(competence, action)
            assert aggregate == pytest.approx(row["outputs"], abs=1e-12)
            assert tuple(sum(individual_output[i][k] for i in range(len(individual_output)))
                         for k in range(len(case.organization.skill_ids))) == pytest.approx(
                             row["outputs"], abs=1e-12,
                         )


def test_functional_success_and_deficit_are_not_inferred_from_positive_output(
    historical, case_and_solutions,
):
    case, _ = case_and_solutions
    rows = historical["A"]["periods"]
    verified = []
    for row in rows:
        result = evaluate_problem_nk(tuple(row["outputs"]), case.problems[row["period"]].requirements)
        assert result.success is row["success"]
        assert result.deficits == pytest.approx(row["deficits"], abs=1e-12)
        verified.append((row["outputs"], case.problems[row["period"]].requirements,
                         result.success, result.deficits))
    # Period 0: positive output and all active requirements met.
    assert verified[0][0][0] > 0 and verified[0][2] is True
    # Period 1: positive y output but below the y requirement; service fails.
    assert verified[1][0][1] == pytest.approx(0.35)
    assert verified[1][1][1] == pytest.approx(0.7)
    assert verified[1][2] is False
    assert verified[1][3][1] == pytest.approx(0.35)


def test_reward_is_ces_and_stays_distinct_from_output_and_service_fields(
    historical, case_and_solutions,
):
    case, _ = case_and_solutions
    for policy in ("A", "B"):
        for row in historical[policy]["periods"]:
            weights = case.problems[row["period"]].ces_weights
            expected_reward = ces_reward_nk(tuple(row["outputs"]), weights)
            assert row["reward"] == pytest.approx(expected_reward, abs=1e-12)
            # The stored result keeps a K-vector of physical output, a separate
            # scalar CES reward, and a separate Boolean/deficit functional result.
            assert len(row["outputs"]) == len(case.organization.skill_ids)
            assert isinstance(row["reward"], (float, int))
            assert isinstance(row["success"], bool)
            assert len(row["deficits"]) == len(case.organization.skill_ids)
    assert historical["design"]["reward"].startswith("existing CES")


def test_resource_accounting_matches_action_and_active_shared_capacity(historical):
    budget = min(historical["design"]["collective_budget"], 2.0)
    for policy in ("A", "B"):
        for row in historical[policy]["periods"]:
            productive = sum(sum(agent_row) for agent_row in row["action"]["production"])
            teaching_action = row["action"]["teaching"]
            teaching = 0.0 if teaching_action is None else 2.0 * teaching_action["effort"]
            assert row["productive_effort"] == pytest.approx(productive)
            assert row["teaching_resource"] == pytest.approx(teaching)
            assert row["total_resource"] == pytest.approx(productive + teaching)
            assert row["unused_resource"] == pytest.approx(max(0.0, budget - productive - teaching))
    assert all(row["total_resource"] == pytest.approx(2.0)
               and row["unused_resource"] == pytest.approx(0.0)
               for row in historical["A"]["periods"])


def test_existing_pef_recalculation_preserves_s4_metrics_and_units(historical):
    result = evaluate_historical_pef()
    for policy in ("A", "B"):
        metrics = result["s4"]["policies"][policy]
        assert metrics["original_reward_cumulative"]["value"] == pytest.approx(
            historical[policy]["value"], abs=1e-12,
        )
        assert metrics["ces_cumulative"]["value"] == pytest.approx(
            historical[policy]["value"], abs=1e-12,
        )
        assert metrics["functional_success_rate"]["value"] == pytest.approx(1 / 3)
        assert metrics["functional_deficit_cumulative"]["value"] == pytest.approx(0.5325)
        assert metrics["production_cumulative"]["value"] == pytest.approx(1.9175)
        assert metrics["resource_usage:productive_effort"]["value"] == pytest.approx(6.0)
        assert metrics["resource_usage:total_resource"]["value"] == pytest.approx(6.0)
        assert all(metric["status"] == "VALID" for metric in metrics.values())
        assert metrics["original_reward_cumulative"]["unit"] == "declared_reward"
        assert metrics["ces_cumulative"]["unit"] == "CES_output"
        assert metrics["functional_success_rate"]["unit"] == "fraction"
        assert metrics["functional_success_rate"]["aggregation"] == "successes/demanded_periods"
        assert metrics["functional_success_rate"]["temporal_horizon"] == 3
        assert metrics["functional_deficit_cumulative"]["unit"] == "output"
        assert metrics["resource_usage:productive_effort"]["unit"] == "effort"


def test_experiment_run_v1_can_carry_s4_semantics_without_new_fields(historical):
    rows = historical["A"]["periods"]
    events = []
    for row in rows:
        period = row["period"]
        events.append(ExperimentEvent(
            len(events), "decision", "s4_exact_bellman",
            {"production_effort": row["action"]["production"],
             "teaching_action": row["action"]["teaching"]}, period,
        ))
        events.append(ExperimentEvent(
            len(events), "execution", "s4_exact_bellman",
            {"output": row["outputs"], "requirements": historical["design"]["requirements"][period],
             "success": row["success"], "deficit": row["deficits"],
             "reward": row["reward"], "resources": {
                 "productive_effort": row["productive_effort"],
                 "teaching_resource": row["teaching_resource"],
                 "total_resource": row["total_resource"],
             }, "competence_before": row["competence_before"],
             "competence_after": row["competence_after"]}, period,
        ))
    run = ExperimentRun(
        schema_version="hls-experiment-run/1.0",
        run_id="s4-semantic-characterization-A",
        mechanism_id="finite_horizon_bellman",
        policy_id="A",
        configuration={"scenario_id": "S4", "configuration_id": "transfer_exact_T3",
                       "organizational_problem_id": "NK_production_with_optional_transfer"},
        initial_conditions={"competence": historical["design"]["initial_competence"],
                            "demand_sequence": historical["design"]["demand_sequence"]},
        random_seeds=(),
        information_available={"policy_view": "full true competence and deterministic demand sequence"},
        observation_model={"mode": "deterministic; exact-state reference"},
        software_revision=None,
        units=(UnitDeclaration("output", "model_output", "Scenario output scale; no external physical unit is declared."),
               UnitDeclaration("effort", "effort", "Abstract scenario effort resource.")),
        events=tuple(events),
        metrics=(MetricValue("original_reward_cumulative", historical["A"]["value"],
                             "CES_output", "S4 original cumulative CES objective.", "higher"),),
        mechanism_results={"periods": rows},
        metadata={"evaluation_profile_id": "s4_exact", "source": str(S4_RESULT),
                  "role": "temporary compatibility characterization; not a permanent adapter"},
    )
    restored = ExperimentRun.from_json(run.to_json())
    assert restored.to_json() == run.to_json()
    assert len(restored.events) == 6
    assert restored.events[1].data["success"] is True
