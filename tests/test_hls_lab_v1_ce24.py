"""Small deterministic checks for the CE-24 protocol and exported records."""

import csv
import hashlib
import json

from hls.discover_v0 import JOINT_ACTIONS, production_inputs
from hls.hls_lab_v1 import (
    ExploreThenGreedy, FixedRouting, GreedyAdaptive, complementarity_class,
    evaluate_problem, feasible_actions, run_sequence,
)
from experiments.synthetic.hls_lab_v1.ce24 import (
    REFERENCE_TEAM, exact_context_oracle, experiment_results,
    make_evaluation_sequence, make_training_sequence, problem,
)


def test_predeclared_domain_has_correct_feasibility_and_no_saturation():
    expected = {"A": (10, [48]), "B": (10, [4]), "C": (37, [52]), "D": (10, [])}
    for kind, (count, successful_ids) in expected.items():
        item = problem(kind)
        actions = feasible_actions(item)
        observed = [JOINT_ACTIONS.index(action) for action in actions
                    if evaluate_problem(production_inputs(REFERENCE_TEAM.real_matrix, action),
                                        item.requirements).success]
        assert len(actions) == count
        assert observed == successful_ids
        assert all(action in JOINT_ACTIONS for action in actions)
    assert complementarity_class(REFERENCE_TEAM, problem("A")) == "single_sufficient"
    assert complementarity_class(REFERENCE_TEAM, problem("B")) == "single_sufficient"
    assert complementarity_class(REFERENCE_TEAM, problem("C")) == "team_only"
    assert complementarity_class(REFERENCE_TEAM, problem("D")) == "none_feasible"


def test_training_exhausts_all_legal_actions_under_learning_and_no_learning_repeats_first():
    sequence = make_training_sequence()
    assert len(sequence) == 20
    assert [sum(p.problem_id == kind for p in sequence) for kind in ("A", "B")] == [10, 10]
    learner = ExploreThenGreedy()
    learned = run_sequence(REFERENCE_TEAM, sequence, learner, eta=0.35,
                           individual_learning=False, organizational_learning=True)
    control = run_sequence(REFERENCE_TEAM, sequence, learner, eta=0.35,
                           individual_learning=False, organizational_learning=False)
    for kind in ("A", "B"):
        rows = [row for row in learned.records if row.problem_id == kind]
        assert len({row.action_id for row in rows}) == 10
        assert {row.action_id for row in rows} == {
            JOINT_ACTIONS.index(a) for a in feasible_actions(problem(kind))}
        control_rows = [row for row in control.records if row.problem_id == kind]
        assert {row.action_id for row in control_rows} == {0}
    assert not control.final_organization.values
    assert control.final_organization.update_count == 0


def test_frozen_evaluation_persists_theta_and_resets_competencies():
    learner = ExploreThenGreedy()
    trained = run_sequence(REFERENCE_TEAM, make_training_sequence(), learner,
                           eta=0.35, individual_learning=False,
                           organizational_learning=True)
    eval_run = run_sequence(REFERENCE_TEAM, make_evaluation_sequence(), learner,
                            eta=0.35, individual_learning=False,
                            organizational_learning=False,
                            initial_organization_state=trained.final_organization)
    assert eval_run.records[0].organization_theta_before == trained.final_organization.values
    assert all(row.organization_theta_before == row.organization_theta_after
               for row in eval_run.records)
    assert not any(row.organization_updated for row in eval_run.records)
    assert eval_run.final_team.real_matrix == REFERENCE_TEAM.real_matrix


def test_fixed_and_informed_reference_use_exact_same_problem_constraints():
    sequence = make_evaluation_sequence()
    oracle = exact_context_oracle()
    fixed_run = run_sequence(REFERENCE_TEAM, sequence, FixedRouting(oracle), eta=0.35,
                             individual_learning=False)
    greedy_run = run_sequence(REFERENCE_TEAM, sequence, GreedyAdaptive(), eta=0.35,
                              individual_learning=False)
    assert [row.problem_id for row in fixed_run.records] == [row.problem_id for row in greedy_run.records]
    assert [row.action for row in fixed_run.records] == [row.action for row in greedy_run.records]
    for run in (fixed_run, greedy_run):
        for row, item in zip(run.records, sequence):
            assert row.action in feasible_actions(item)
            assert row.budget == item.resource_budget


def test_exported_experiment_is_small_complete_and_reproducible(tmp_path):
    out_a, out_b = tmp_path / "a", tmp_path / "b"
    rows_a, summaries_a, manifest_a = experiment_results(output_dir=out_a)
    rows_b, summaries_b, _ = experiment_results(output_dir=out_b)
    assert len(rows_a) == len(rows_b) == 240
    assert len(summaries_a) == len(summaries_b) == 18
    for name in ("episodes.jsonl", "summary.csv", "problem_metrics.csv"):
        file_a, file_b = out_a / name, out_b / name
        assert file_a.read_bytes() == file_b.read_bytes()
        assert hashlib.sha256(file_a.read_bytes()).hexdigest() == manifest_a["output_sha256"][name]
    parsed = [json.loads(line) for line in (out_a / "episodes.jsonl").read_text().splitlines()]
    assert len(parsed) == 240
    assert {row["phase"] for row in parsed} == {"TRAIN", "EVAL_RESET", "EVAL_CARRYOVER"}
    with (out_a / "summary.csv").open(newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 18
    assert manifest_a["seed_recorded_only_not_consumed"] == 20261014
    assert "no statistical intervals" in manifest_a["metric_note"].lower()
