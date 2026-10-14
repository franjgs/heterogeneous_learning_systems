"""Focused tests for the additive nonstationary HLS v1 extension."""

import pytest

from hls.discover_develop_v2 import capability_after_exposure, eta_to_lambda
from hls.discover_v0 import JOINT_ACTIONS
from hls.hls_lab_dynamic import (
    DemandRegime,
    LearningProfile,
    advance_team,
    compare_organizations,
    generate_problems,
)
from hls.hls_lab_v1 import ExploreThenGreedy, GreedyAdaptive, make_team


TEAM = ((0.82, 0.12), (0.18, 0.76), (0.35, 0.28))
RATES = LearningProfile(((0.10, 0.20), (0.70, 0.30), (0.40, 0.60)))


def test_dynamic_problem_stream_is_reproducible_and_regime_changes():
    low = DemandRegime("low-first-axis", ((0.7, 0.0), (0.0, 0.7)), (0.9, 0.1))
    high = DemandRegime("high-first-axis", ((0.7, 0.0), (0.0, 0.7)), (0.1, 0.9))
    schedule = ((low, 20), (high, 20))
    first = generate_problems(schedule, seed=410)
    assert first == generate_problems(schedule, seed=410)
    assert len(first) == 40
    first_axis_early = sum(p.requirements == (0.7, 0.0) for p in first[:20])
    first_axis_late = sum(p.requirements == (0.7, 0.0) for p in first[20:])
    assert first_axis_early > first_axis_late


def test_cell_rates_reuse_mis_v2_exponential_law_and_li_off_freezes_skills():
    team = make_team(TEAM)
    action = JOINT_ACTIONS[37]
    updated = advance_team(team, action, RATES, enabled=True)
    for i in range(3):
        for k in range(2):
            expected = capability_after_exposure(
                TEAM[i][k], action[i][k], rate=eta_to_lambda(RATES.eta[i][k])
            )
            assert updated.experts[i].competence_real[k] == pytest.approx(expected)
    frozen = advance_team(team, action, RATES, enabled=False)
    assert frozen.real_matrix == team.real_matrix
    assert frozen.experts[0].experience != team.experts[0].experience


def test_paired_policies_share_external_problems_and_evolve_own_histories():
    east = DemandRegime("east", ((0.8, 0.0), (0.0, 0.8)), (0.85, 0.15))
    west = DemandRegime("west", ((0.8, 0.0), (0.0, 0.8)), (0.15, 0.85))
    problems = generate_problems(((east, 18), (west, 18)), seed=52, budget=1.0)
    initial = make_team(TEAM)
    adaptive, learned = compare_organizations(
        initial,
        problems,
        ((GreedyAdaptive(), False), (ExploreThenGreedy(), True)),
        learning=RATES,
        seed=52,
    )

    assert len(adaptive.records) == len(learned.records) == 36
    assert [r.problem_id for r in adaptive.records] == [r.problem_id for r in learned.records]
    assert [r.requirements for r in adaptive.records] == [r.requirements for r in learned.records]
    assert all(r.budget == 1.0 for r in adaptive.records + learned.records)
    assert all(r.action in JOINT_ACTIONS for r in adaptive.records + learned.records)
    assert adaptive.records[0].competence_before == learned.records[0].competence_before == TEAM
    assert adaptive.final_organization.update_count == 0
    assert learned.final_organization.update_count == 36
    assert adaptive.final_team != learned.final_team
    assert adaptive.final_team != initial and learned.final_team != initial
    assert adaptive.records[-1].cumulative_successes == sum(r.success for r in adaptive.records)
    assert learned.records[-1].cumulative_successes == sum(r.success for r in learned.records)
    assert adaptive.records[-1].competence_after == adaptive.final_team.real_matrix
    assert learned.records[-1].competence_after == learned.final_team.real_matrix


def test_learning_profile_requires_three_by_two_eta_values():
    with pytest.raises(ValueError):
        LearningProfile(((0.2, 0.3), (0.2, 0.3)))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        LearningProfile(((0.2, 0.3), (0.2, 0.3), (0.2, 1.0)))
