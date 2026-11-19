from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "studies" / "soc_human_ai_organization"))

import soc_parametric_baseline as baseline  # noqa: E402


def test_reference_configuration_has_explicit_units_and_valid_probabilities():
    config = baseline.REFERENCE
    assert config.time_unit == "hour"
    assert config.horizon_h == 24
    assert abs(sum(config.project_probabilities) - 1.0) < 1e-12
    assert abs(sum(config.priority_probabilities) - 1.0) < 1e-12
    assert len(config.project_names) == len(config.escalation_need_by_project) == 3
    assert all(hours > 0 for _, hours in config.sla_deadline_h)
    assert all(hours > 0 for _, hours in config.l1_service_h + config.l2_service_h)


def test_reference_eligibility_overlaps_and_covers_each_project():
    l1, l2, l1_service, l2_service = baseline.build_roster()
    for project in baseline.PROJECTS:
        assert sum(project in analyst.eligible_classes for analyst in l1) >= 4
        assert all(project in analyst.eligible_classes for analyst in l2)
    assert all(len(analyst.eligible_classes) >= 2 for analyst in l1)
    assert set(l1_service) == {analyst.analyst_id for analyst in l1}
    assert set(l2_service) == {analyst.analyst_id for analyst in l2}


def test_d1_episode_is_reproducible_and_conserves_alerts():
    first = baseline.run_d1_episode(261119001)
    second = baseline.run_d1_episode(261119001)
    assert first == second
    assert first["admitted"] == first["completed"] + first["pending"]
    assert first["pending"] == 0
    assert 0.0 <= first["quality_model"] <= 1.0
    assert first["backlog_l1_end"] + first["backlog_l2_end"] == first["pending"]
    assert first["n_l1"] == baseline.REFERENCE.n_l1
    assert first["n_l2"] == baseline.REFERENCE.n_l2
    assert set(first["sla_by_priority"]) == set(baseline.PRIORITIES)
    assert set(first["sla_by_project"]) == set(baseline.PROJECTS)
    assert sum(first[f"admitted_priority_{key}"] for key in baseline.PRIORITIES) == first["admitted"]
    assert sum(first[f"admitted_project_{key}"] for key in baseline.PROJECTS) == first["admitted"]


def test_sensitivity_comparison_uses_frozen_d1_and_reference_points():
    assert set(baseline.SWEEPS) == {
        "arrival_rate_per_h", "n_l1",
        "mean_eligible_projects_per_l1", "sla_multiplier",
    }
    assert baseline.BASE_POINTS["arrival_rate_per_h"] == baseline.REFERENCE.arrival_rate_per_h
    assert baseline.BASE_POINTS["n_l1"] == baseline.REFERENCE.n_l1
    assert baseline.BASE_POINTS["mean_eligible_projects_per_l1"] == baseline.REFERENCE.mean_eligible_projects_per_l1
    assert baseline.BASE_POINTS["sla_multiplier"] == 1.0
    assert baseline.PRIMARY_METRIC == "sla_terminal"
