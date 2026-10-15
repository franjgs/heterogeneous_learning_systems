from dataclasses import fields

import pytest

from experiments.synthetic.hls_campaign1.run import (
    DEMAND_RELATIONS, LEARNING, PARAMETERS, _efficacy, _environment,
    _initial_team, _policy,
)
from hls.hls_lab_v1_integrated import (
    IntegratedAction, OrganizationSnapshot, P0ProductionOnly,
    P2AdaptiveTeaching, TeachingEvent, enumerate_feasible_integrated_actions,
    run_integrated_sequence,
)
from experiments.synthetic.hls_campaign1.counterfactual_teaching import _view


def _setup():
    problems, _ = _environment("changing", 24, 2026101511)
    team = _initial_team("high")
    replay = run_integrated_sequence(
        team, problems, _policy("P2_ADAPTIVE_TEACHING"), learning=LEARNING,
        teaching_efficacy=_efficacy(0.85), parameters=PARAMETERS,
        individual_learning=False, organizational_learning=True, seed=2026101511,
    )
    return problems, replay.snapshots[2]


def test_snapshot_is_complete_independent_and_continuable():
    problems, snapshot = _setup()
    policy = P2AdaptiveTeaching(DEMAND_RELATIONS)
    a = run_integrated_sequence(snapshot.team, problems[2:], policy, learning=LEARNING,
        teaching_efficacy=_efficacy(0.85), parameters=PARAMETERS,
        individual_learning=False, seed=2026101511, initial_snapshot=snapshot)
    b = run_integrated_sequence(snapshot.team, problems[2:], policy, learning=LEARNING,
        teaching_efficacy=_efficacy(0.85), parameters=PARAMETERS,
        individual_learning=False, seed=2026101511,
        initial_snapshot=OrganizationSnapshot(snapshot.team, snapshot.competence_posterior,
                                               snapshot.organization_memory, snapshot.next_period))
    assert a.records == b.records
    assert a.records[0].period == 2
    assert snapshot.next_period == 2
    assert a.snapshots[0] is not b.snapshots[0]
    assert a.snapshots[-1] is not snapshot


def test_policy_view_does_not_expose_private_competencies_or_efficacy():
    problems, snapshot = _setup()
    view = _view(snapshot, problems[2].problem, problems[2].demand_label, 22)
    names = {item.name for item in fields(view)}
    assert "competence_real" not in names
    assert "teaching_efficacy" not in names
    assert "competence_real" not in vars(view)


def test_zero_intervention_branches_are_identical_and_preserve_resources():
    problems, snapshot = _setup()
    suffix = problems[2:]
    view = _view(snapshot, suffix[0].problem, suffix[0].demand_label, len(suffix))
    action = P0ProductionOnly().choose(view, snapshot.organization_memory, PARAMETERS)
    assert action.teaching is None
    kwargs = dict(learning=LEARNING, teaching_efficacy=_efficacy(0.85),
                  parameters=PARAMETERS, individual_learning=False, seed=2026101511,
                  initial_snapshot=snapshot, first_action_override=action)
    left = run_integrated_sequence(snapshot.team, suffix, P2AdaptiveTeaching(DEMAND_RELATIONS), **kwargs)
    right = run_integrated_sequence(snapshot.team, suffix, P2AdaptiveTeaching(DEMAND_RELATIONS), **kwargs)
    assert left.records == right.records
    for row, problem in zip(left.records, suffix):
        assert row.total_resource_used <= problem.problem.resource_budget + 1e-12
        assert row.total_resource_used == pytest.approx(row.production_effort + row.teaching_effort)


def test_snapshot_teaching_and_no_teaching_branches_share_exogenous_suffix():
    problems, snapshot = _setup()
    suffix = problems[2:]
    view = _view(snapshot, suffix[0].problem, suffix[0].demand_label, len(suffix))
    candidate = (0, 1, 1)
    teaching = next(action for action in enumerate_feasible_integrated_actions(
        suffix[0].problem, teaching_effort=PARAMETERS.effort)
        if action.teaching is not None and action.teaching.relation == candidate)
    no_teaching = P0ProductionOnly().choose(view, snapshot.organization_memory, PARAMETERS)
    kwargs = dict(learning=LEARNING, teaching_efficacy=_efficacy(0.85),
                  parameters=PARAMETERS, individual_learning=False, seed=2026101511,
                  initial_snapshot=snapshot)
    p = P2AdaptiveTeaching(DEMAND_RELATIONS)
    a = run_integrated_sequence(snapshot.team, suffix, p, first_action_override=no_teaching, **kwargs)
    b = run_integrated_sequence(snapshot.team, suffix, p, first_action_override=teaching, **kwargs)
    assert [x.problem_id for x in a.records] == [x.problem_id for x in b.records]
    assert a.records[0].competence_real_before == b.records[0].competence_real_before
    assert a.records[0].competence_estimated_before == b.records[0].competence_estimated_before
    assert b.records[0].teaching_effort == pytest.approx(0.5)
