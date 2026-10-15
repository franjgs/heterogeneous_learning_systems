"""Factorial identification and mechanism-accounting checks for HLS Campaign 2."""

import csv
import gzip
import json
from copy import deepcopy
from dataclasses import asdict, fields, replace

import pytest

from experiments.synthetic.hls_campaign2 import teaching_mis_assignment as campaign
from hls.hls_lab_dynamic import advance_team
from hls.hls_lab_v1_integrated import IntegratedDecisionView, P0ProductionOnly


@pytest.fixture(scope="module")
def paired():
    return campaign.run_quadruple("B_enabling_candidate", campaign.SEEDS[0])


def test_registered_protocol_and_competitive_policy_are_fixed():
    assert campaign.CONDITIONS == {"C00": (False, False), "C10": (True, False),
                                   "C01": (False, True), "C11": (True, True)}
    assert len(campaign.SEEDS) == len(set(campaign.SEEDS)) == 10
    assert len(campaign.SCENARIOS) == 3
    assert campaign.RELATION == (0, 1, 0)


def test_branch_snapshots_are_equal_complete_and_independent(paired):
    runs, _, _ = paired
    initial = deepcopy(runs["C00"].snapshots[0])
    for run in runs.values():
        assert run.snapshots[0] == initial
        assert run.snapshots[-1] is not run.snapshots[0]
    assert runs["C10"].snapshots[0] is not runs["C11"].snapshots[0]
    assert runs["C00"].snapshots[0] == initial


def test_runner_calls_differ_only_by_two_declared_interventions(monkeypatch):
    original = campaign.run_integrated_sequence
    calls = []
    def inspect(team, problems, policy, **kwargs):
        calls.append((team, problems, policy, kwargs.copy()))
        return original(team, problems, policy, **kwargs)
    monkeypatch.setattr(campaign, "run_integrated_sequence", inspect)
    campaign.run_quadruple("A_substitution_candidate", campaign.FIXTURE_SEED, deterministic=True)
    baseline = calls[0]
    for team, problems, policy, kwargs in calls:
        assert team == baseline[0] and problems is baseline[1]
        assert policy == P0ProductionOnly()
        for key in kwargs.keys() - {"individual_learning", "first_action_override"}:
            assert kwargs[key] == baseline[3][key]
    assert calls[1][3]["first_action_override"] == calls[3][3]["first_action_override"]
    assert calls[0][3]["first_action_override"] == calls[2][3]["first_action_override"]


def test_teaching_once_and_common_continuation(paired):
    runs, _, _ = paired
    for condition, run in runs.items():
        teaching, _ = campaign.CONDITIONS[condition]
        assert (run.records[0].action.teaching is not None) == teaching
        assert all(r.action.teaching is None for r in run.records[1:])
        assert run.policy == "P0_PRODUCTION_ONLY"
    assert runs["C10"].records[0].action == runs["C11"].records[0].action
    assert runs["C00"].records[0].action == runs["C01"].records[0].action


def test_environment_identical_exogenous_and_reproducible(paired):
    runs, problems, _ = paired
    expected = [(p.problem.problem_id, p.problem.requirements) for p in problems]
    assert all([(r.problem_id, r.requirements) for r in run.records] == expected for run in runs.values())
    assert problems == campaign.environment("B_enabling_candidate", campaign.SEEDS[0])
    changed = campaign.environment("C_demand_change", campaign.SEEDS[0])
    assert [p.problem.requirements for p in changed[:12]] == [(1.0, 0.0)]*12
    assert [p.problem.requirements for p in changed[12:]] == [(0.0, 1.0)]*12


def test_indexed_observation_innovations_are_common_across_actions(paired):
    runs, _, parameters = paired
    for period in range(campaign.HORIZON):
        residuals = []
        for run in runs.values():
            record = run.records[period]
            residuals.append([(record.individual_observations[i][k] - record.individual_outputs[i][k])
                              / parameters.production_observation_noise_sd
                              for i in range(3) for k in range(2)])
        for residual in residuals[1:]:
            assert residual == pytest.approx(residuals[0], abs=1e-12)


def test_mis_off_and_no_learning_preserve_true_competencies(paired):
    runs, _, _ = paired
    for r in runs["C00"].records:
        assert r.competence_real_before == r.competence_real_after
    for condition in ("C00", "C10"):
        run = runs[condition]
        for t, r in enumerate(run.records):
            mis = advance_team(run.snapshots[t].team, r.action.production,
                               campaign.LEARNING, enabled=False, update_estimated=False)
            assert mis.real_matrix == r.competence_real_before
            if t > 0:
                assert r.competence_real_after == r.competence_real_before


def test_direct_gain_uses_target_only_and_is_logged_separately(paired):
    runs, problems, _ = paired
    rows = campaign.mechanism_rows("B_enabling_candidate", campaign.SEEDS[0], "test", runs, problems)
    assert len(rows) == 4*campaign.HORIZON
    for condition in ("C10", "C11"):
        record = runs[condition].records[0]
        assert record.teaching_gain_real == pytest.approx(.75*.25*.85*(1-.20))
        after_mis = advance_team(runs[condition].snapshots[0].team, record.action.production,
            campaign.LEARNING, enabled=condition == "C11", update_estimated=False)
        for i in range(3):
            for k in range(2):
                extra = record.teaching_gain_real if (i,k) == (1,0) else 0
                assert record.competence_real_after[i][k] == pytest.approx(after_mis.real_matrix[i][k]+extra)


def test_zero_efficacy_has_no_direct_gain_but_pays_resources():
    runs, _, _ = campaign.run_quadruple("B_enabling_candidate", campaign.FIXTURE_SEED,
                                       deterministic=True, efficacy=0.0)
    for condition in ("C10", "C11"):
        record = runs[condition].records[0]
        assert record.teaching_gain_real == 0.0
        assert record.teaching_effort == .5
    assert runs["C10"].final_team.real_matrix == runs["C00"].final_team.real_matrix


def test_resource_accounting_includes_both_participants_and_residual(paired):
    runs, problems, _ = paired
    for run in runs.values():
        for r, p in zip(run.records, problems):
            assert r.total_resource_used == r.production_effort+r.teaching_effort
            assert r.total_resource_used <= p.problem.resource_budget+1e-12
            assert r.resource_cost == pytest.approx(.2*r.total_resource_used)
            for i in range(3):
                load = sum(r.action.production[i])
                if r.action.teaching is not None and i in (0,1):
                    load += .25
                assert load <= 1+1e-12
    assert runs["C10"].records[0].production_effort == 1
    assert runs["C00"].records[0].production_effort == 2


def test_production_policy_observes_estimates_not_private_truth(monkeypatch):
    permitted = {f.name for f in fields(IntegratedDecisionView)}
    assert not {"true_competencies", "teaching_efficacy", "latent_states", "condition", "mis_enabled"} & permitted
    original = P0ProductionOnly.choose
    seen = []
    def inspect(self, view, memory, parameters):
        assert set(asdict(view)) == permitted
        seen.append(view)
        return original(self, view, memory, parameters)
    monkeypatch.setattr(P0ProductionOnly, "choose", inspect)
    campaign.run_quadruple("B_enabling_candidate", campaign.FIXTURE_SEED, deterministic=True)
    # Same observed problem, different admissible estimated competence order:
    # P0 can respond without accessing private truth or a teaching label.
    view = seen[0]
    altered = replace(view, estimated_competencies=((.9,.2),(.5,.2),(.1,.8)))
    assert original(P0ProductionOnly(), altered, campaign.OrganizationMemory(), campaign.PARAMETERS).production != original(
        P0ProductionOnly(), view, campaign.OrganizationMemory(), campaign.PARAMETERS).production


def test_reproducibility_and_json_serialization(paired):
    runs, _, _ = paired
    again, _, _ = campaign.run_quadruple("B_enabling_candidate", campaign.SEEDS[0])
    assert runs == again
    initial = asdict(runs["C00"].snapshots[0])
    assert json.loads(campaign.encode(initial))["next_period"] == 0


def test_interaction_arithmetic_and_stable_break_even(paired):
    runs, _, _ = paired
    row = campaign.summarize_quadruple("B_enabling_candidate", campaign.SEEDS[0], runs, "test")
    r = {c: sum(x.ces_reward for x in result.records) for c,result in runs.items()}
    assert row["interaction"] == pytest.approx((r["C11"]-r["C01"])-(r["C10"]-r["C00"]))
    assert campaign.stable_break_even([-1, 2, -2, 2]) == 3
    assert campaign.stable_break_even([-1, 0]) == "NA"
    assert campaign.stable_break_even([0, 1]) == "NA"


def test_output_round_trip_and_preparation_is_nonexperimental(tmp_path):
    campaign.prepare(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["protocol.json"]
    assert json.loads((tmp_path/"protocol.json").read_text())["configuration"] == json.loads(campaign.encode(campaign.protocol()))
    path = tmp_path/"rows.csv.gz"
    rows = [{"direct": .25, "mis": 0.0}]
    campaign.write_csv(path, rows)
    with gzip.open(path,"rt") as stream:
        assert list(csv.DictReader(stream)) == [{"direct": "0.25", "mis": "0.0"}]


def test_mechanism_analysis_matches_individual_traces(paired, tmp_path):
    from experiments.synthetic.hls_campaign2.analyze_teaching_mis import analyze_rows
    runs, problems, _ = paired
    rows = campaign.mechanism_rows("B_enabling_candidate", campaign.SEEDS[0], "noisy", runs, problems)
    path = tmp_path/"rows.csv.gz"
    campaign.write_csv(path, rows)
    with gzip.open(path, "rt") as stream:
        summaries, contrasts = analyze_rows(list(csv.DictReader(stream)))
    by_condition = {r["condition"]: r for r in summaries}
    assert by_condition["C11"]["direct_teaching_gain"] == pytest.approx(runs["C11"].records[0].teaching_gain_real)
    assert by_condition["C11"]["learner_target_mis_gain"] == pytest.approx(
        runs["C11"].final_team.real_matrix[1][0] - .20 - runs["C11"].records[0].teaching_gain_real)
    assert by_condition["C10"]["learner_target_mis_gain"] == 0
    assert len(contrasts) == 2
    assert all(r["production_effort"]+r["teaching_effort"]+r["unused_capacity"] == 48 for r in summaries)


def test_saved_campaign_quadruples_and_metrics_are_consistent():
    from experiments.synthetic.hls_campaign2.analyze_teaching_mis import read_traces, validate_rows
    rows = read_traces(campaign.OUTPUT)
    validated = validate_rows(rows)
    assert validated["unique_quadruples"] == 34
    assert validated["trace_rows"] == 3264
    with (campaign.OUTPUT/"paired_outcomes.csv").open() as stream:
        outcomes = list(csv.DictReader(stream))
    assert len(outcomes) == 33
    for row in outcomes:
        assert float(row["interaction"]) == pytest.approx(
            (float(row["R11"])-float(row["R01"]))-(float(row["R10"])-float(row["R00"])))
    with (campaign.OUTPUT/"interaction_summary.csv").open() as stream:
        summary = list(csv.DictReader(stream))
    assert {int(r["n"]) for r in summary} == {10}
    for row in summary:
        data = [float(r["interaction"]) for r in outcomes if r["kind"] == "noisy" and r["scenario"] == row["scenario"]]
        assert float(row["interaction_mean"]) == pytest.approx(sum(data)/len(data))
    # H3 comparison shares the entire observed/physical prefix before demand changes.
    b_prefix = {(r["seed"], r["kind"], r["condition"], r["period"]):
                {k:v for k,v in r.items() if k != "scenario"}
                for r in rows if r["scenario"] == "B_enabling_candidate"
                and r["kind"] != "zero_efficacy" and int(r["period"]) < 12}
    for r in rows:
        if r["scenario"] == "C_demand_change" and int(r["period"]) < 12:
            key = (r["seed"],r["kind"],r["condition"],r["period"])
            assert {k:v for k,v in r.items() if k != "scenario"} == b_prefix[key]
