"""Focused checks for the predeclared S4 mechanism-interaction protocol."""

import pytest

from experiments.run_hls_s4_transfer_interaction import (
    CELLS,
    RELATIONS,
    check_action_catalogs,
    controlled_actions,
    design,
    execute,
    factorial_contrast,
    problems_for_seed,
    summarize,
)
from hls.hls_lab_nk_policies import NKDecisionView, P0ProductionOnlyPolicyNK, P1FixedTeachingNK, P2AdaptiveTeachingNK


def test_disabled_transfer_preserves_joint_action_catalog_and_charges():
    setup = design()
    check_action_catalogs(setup)
    problems = problems_for_seed(setup, 43000)
    actions = controlled_actions(problems)
    runs = {cell: execute(setup, problems, cell, actions=actions) for cell, _, _ in CELLS}
    first = runs["00"].records
    for run in runs.values():
        assert tuple(row.action for row in run.records) == actions
        assert tuple(row.total_resource_used for row in run.records) == tuple(
            row.total_resource_used for row in first)
        assert all(row.teaching_resource_used == pytest.approx(.5) for row in run.records)
        assert all(row.total_resource_used <= 2.0 for row in run.records)
        assert run.records[0].production.ces_reward == pytest.approx(first[0].production.ces_reward)


def test_same_cell_mis_teaching_overlap_matches_existing_laws():
    setup = design()
    problem = setup["environment"].emissions["y"].problems[0]
    action = controlled_actions((problem,))
    rows = {cell: execute(setup, (problem,), cell, actions=action).records[0]
            for cell, _, _ in CELLS}
    c = {cell: row.competence_actual_after[1][1] for cell, row in rows.items()}
    h = .4 * .25 * .8
    assert c["00"] == pytest.approx(.2)
    assert c["01"] - c["00"] == pytest.approx((1 - .2) * h)
    assert c["11"] - c["10"] == pytest.approx((1 - c["10"]) * h)
    assert c["11"] - c["10"] - c["01"] + c["00"] == pytest.approx(
        -(c["10"] - c["00"]) * h)
    assert rows["00"].mis_increment[1][1] == 0.0
    assert rows["10"].teaching_increment[1][1] == 0.0


def test_closed_loop_policies_have_same_demand_and_allowed_information():
    setup = design()
    problems = problems_for_seed(setup, 43001)
    assert "competence_real" not in NKDecisionView.__dataclass_fields__
    assert "teaching_efficacy" not in NKDecisionView.__dataclass_fields__
    policies = (P0ProductionOnlyPolicyNK(), P1FixedTeachingNK(RELATIONS[0]),
                P2AdaptiveTeachingNK(RELATIONS))
    runs = [execute(setup, problems, "11", policy=policy) for policy in policies]
    assert all(tuple(row.production.problem_id for row in run.records)
               == tuple(problem.problem_id for problem in problems) for run in runs)
    assert all(row.action.teaching is None for row in runs[0].records)
    assert all(row.total_resource_used <= 2.0 for run in runs for row in run.records)
    assert all(row.competence_estimated_before == row.competence_actual_before
               for run in runs for row in run.records)
    assert runs[0] == execute(setup, problems, "11", policy=policies[0])


def test_factorial_contrast_uses_matched_seed_rows():
    rows = [
        {"00": {"ces": 1}, "10": {"ces": 2}, "01": {"ces": 3}, "11": {"ces": 5}},
        {"00": {"ces": 2}, "10": {"ces": 4}, "01": {"ces": 5}, "11": {"ces": 8}},
    ]
    assert factorial_contrast(rows, "ces")["mean"] == pytest.approx(1.0)


def test_each_factorial_cell_keeps_expected_transition_and_resource_conservation():
    setup = design()
    problems = problems_for_seed(setup, 43002)
    results = {cell: summarize(execute(setup, problems, cell,
                                       actions=controlled_actions(problems)))
               for cell, _, _ in CELLS}
    assert results["00"]["final_competence"] == setup["organization"].competence_initial
    assert results["10"]["final_competence"][1][1] > .2
    assert results["01"]["final_competence"][1][1] > .2
    assert results["11"]["final_competence"][1][1] >= max(
        results["10"]["final_competence"][1][1],
        results["01"]["final_competence"][1][1],
    )
    assert len({result["total_effort"] for result in results.values()}) == 1
