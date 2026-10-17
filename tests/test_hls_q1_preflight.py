"""Preflight contract tests; these do not run the main Q1 campaign."""

import json
from pathlib import Path

from experiments.synthetic.hls_lab_v1.q1_preflight import (
    ARCH,
    DIFFICULTY,
    LEARNING,
    LABELS,
    PI,
    _config,
    _process,
    equivalence_control,
    feasibility_diagnostics,
    primary_task_effect_diagnostic,
)
from hls.hls_lab_v1_environment import generate_environment_trajectory


ROOT = Path(__file__).resolve().parents[1]


def test_architecture_matching_changes_only_competence_redistribution():
    homogeneous, tilted = ARCH["homogeneous"], ARCH["tilted"]
    assert len(homogeneous) == len(tilted) == 3
    assert tuple(sum(row[k] for row in homogeneous) for k in range(2)) == (1.5, 1.5)
    assert tuple(sum(row[k] for row in tilted) for k in range(2)) == (1.5, 1.5)
    assert tuple(map(sum, homogeneous)) == tuple(map(sum, tilted)) == (1.0, 1.0, 1.0)
    assert LEARNING.eta == ((0.1, 0.1),) * 3


def test_iid_and_markov_share_stationary_marginals_but_markov_is_persistent():
    process = _process("markov")
    p = process.transitions
    for destination, probability in zip(LABELS, PI):
        stationary = sum(PI[i] * p[LABELS[i]][destination] for i in range(3))
        assert abs(stationary - probability) < 1e-12
    iid_same = sum(p * p for p in PI)
    markov_same = sum(PI[i] * process.transitions[LABELS[i]][LABELS[i]] for i in range(3))
    assert abs(iid_same - 0.36) < 1e-12
    assert abs(markov_same - 0.872) < 1e-12
    assert markov_same > iid_same


def test_predeclared_demand_paths_are_seed_reproducible_and_not_policy_conditioned():
    config = _config("markov", "near_boundary", horizon=24)
    first = generate_environment_trajectory(config, seed=2026102200)
    repeated = generate_environment_trajectory(config, seed=2026102200)
    assert first == repeated
    assert len(first.problems) == 24
    assert all(item.problem.resource_budget == 2.0 for item in first.problems)
    assert not any(hasattr(item, "latent_state") for item in first.problems)


def test_frontier_controls_have_registered_feasibility_classes():
    result = feasibility_diagnostics()
    assert result["initial_frontiers"] == {
        "homogeneous": [1.0, 1.0, 0.5], "tilted": [1.1, 1.1, 0.6],
    }
    rows = result["action_feasibility"]
    for architecture in ARCH:
        easy = [x for x in rows if x["architecture"] == architecture and x["stratum"] == "easy"]
        boundary = [x for x in rows if x["architecture"] == architecture and x["stratum"] == "near_boundary"]
        learnable = [x for x in rows if x["architecture"] == architecture and x["stratum"] == "learnable"]
        assert all(x["successful_action_count"] > 0 for x in easy)
        assert all(x["successful_action_count"] == 0 for x in learnable)
        assert all(x["resource_min"] >= 0 and x["resource_max"] <= 2.0 for x in rows
                   if x["architecture"] == architecture)
        if architecture == "homogeneous":
            assert all(x["successful_action_count"] == 0 for x in boundary)
        else:
            assert all(x["successful_action_count"] > 0 for x in boundary)
        assert all(result["witness_frontiers"][architecture][i] >
                   max(DIFFICULTY["learnable"][i]) for i in range(3))


def test_equivalence_control_passes_with_mis_frozen_and_enabled():
    summary, _ = equivalence_control()
    assert summary["MIS_OFF"]["pass"]
    assert summary["MIS_ON"]["pass"]
    assert summary["MIS_OFF"]["outputs_equal_within_1e-12"]
    assert summary["MIS_ON"]["skill0_competence_totals_equal"]


def test_registered_primary_block_has_task_invariant_architecture_effect():
    rows = primary_task_effect_diagnostic()
    effects = [row["tilted"]["ces"] - row["homogeneous"]["ces"]
               for row in rows.values()]
    assert all(abs(effect - 0.1) < 1e-12 for effect in effects)
    for row in rows.values():
        for arm in row.values():
            shift = max(abs(arm["estimate_after"][i][k] - arm["estimate_before"][i][k])
                        for i in range(3) for k in range(2))
            assert shift <= 1e-12


def test_registration_is_explicitly_separate_from_main_campaign():
    protocol = json.loads((ROOT / "results/diagnostics/hls_q1_preflight/preregistration.json").read_text())
    assert protocol["status"] == "REGISTERED_BEFORE_DIAGNOSTICS"
    assert protocol["main_campaign_authorized"] is False
    assert protocol["outcome_diagnostic"]["total_trajectories"] == 288
    assert protocol["acceptance"]["minimum_effect_threshold"] is None
