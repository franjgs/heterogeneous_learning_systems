"""Drift controls for the consolidated pre-experiment foundation manifest."""

import json
from hashlib import sha256
from pathlib import Path

import pytest

from hls.discover_v0 import (
    DEFAULT_HORIZON,
    DEFAULT_QUADRATURE_ORDER,
    DEFAULT_SIGMA,
    INDIVIDUAL_ACTIONS,
    JOINT_ACTIONS,
    N_AGENTS,
    N_CAPABILITIES,
    RHO,
)
from hls.small_problem_world import (
    BELIEF_RESETS_EACH_PROBLEM,
    HORIZON,
    HYPOTHESIS_REPERTOIRE,
    POSTERIOR_CARRIES_BETWEEN_PROBLEMS,
    STATE_PERSISTS_BETWEEN_PROBLEMS,
    UNIFORM_PRIOR,
    WORLD,
    world_descriptors,
)


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "results" / "foundations" / "HLS_PRE_EXPERIMENT_FOUNDATION.json"


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_identity_commits_and_source_artifacts_exist():
    manifest = _manifest()
    assert manifest["manifest_id"] == "hls-pre-experiment-foundation-v1"
    assert manifest["source_repository_head"] == "a315143"
    assert manifest["foundation_commits"] == {
        "mis_v2_capability_geometry": "b194241",
        "finite_problem_belief": "116a6f2",
        "problem_distance": "3e2dbea",
        "small_problem_world": "a315143",
    }
    for artifact in manifest["source_artifacts"]:
        path = ROOT / artifact["path"]
        assert path.is_file()
        assert sha256(path.read_bytes()).hexdigest() == artifact["sha256"]


def test_manifest_physics_constants_match_executable_sources():
    manifest = _manifest()
    dimensions = manifest["dimensions"]
    assert dimensions["agents"] == N_AGENTS == 3
    assert dimensions["capabilities"] == N_CAPABILITIES == 2
    assert dimensions["capability_bounds"] == [0.0, 1.0]
    assert dimensions["individual_actions"] == [list(action) for action in INDIVIDUAL_ACTIONS]
    assert dimensions["joint_actions"] == len(JOINT_ACTIONS) == 64
    assert manifest["production"]["rho"] == RHO == 0.5
    assert manifest["observation_and_discovery"]["sigma"] == DEFAULT_SIGMA == 0.1
    assert manifest["observation_and_discovery"]["fixed_state_dp_quadrature_order"] == DEFAULT_QUADRATURE_ORDER == 31
    assert manifest["observation_and_discovery"]["dynamic_mpc_quadrature_order"] == 3
    assert manifest["temporal_semantics"]["horizon_per_problem"] == DEFAULT_HORIZON == HORIZON == 3


def test_manifest_repertoire_prior_world_and_temporal_semantics_match_fixture():
    manifest = _manifest()
    representation = manifest["frozen_agent_representation"]
    frozen_world = manifest["frozen_small_problem_world"]
    temporal = manifest["temporal_semantics"]
    assert representation["Z_hat"] == [list(problem) for problem in HYPOTHESIS_REPERTOIRE]
    assert representation["prior"] == pytest.approx(UNIFORM_PRIOR)
    assert frozen_world["labels"] == [stage.label for stage in WORLD]
    assert frozen_world["true_problems"] == [list(stage.problem) for stage in WORLD]
    assert frozen_world["p_sequence"] == [stage.problem[0] for stage in WORLD]
    assert temporal["state_S_persists_between_problems"] is STATE_PERSISTS_BETWEEN_PROBLEMS
    assert temporal["belief_resets_between_problems"] is BELIEF_RESETS_EACH_PROBLEM
    assert temporal["posterior_carries_between_problems"] is POSTERIOR_CARRIES_BETWEEN_PROBLEMS


def test_manifest_world_descriptors_and_representation_flags_match_artifact_and_code():
    manifest = _manifest()
    artifact = json.loads(
        (ROOT / "results" / "foundations" / "small_problem_world_gate" / "control_summary.json").read_text()
    )
    rows = world_descriptors()
    expected = (
        (None, None, 0.0, True),
        (0.15, 0.15, 0.15, False),
        (0.40, 0.40, 0.15, False),
        (0.15, 0.15, 0.0, True),
        (0.39, 0.24, 0.0, True),
        (0.39, 0.0, 0.0, True),
    )
    for row, (change, novelty, mismatch, represented) in zip(rows, expected):
        if change is None:
            assert row.change_magnitude is None
        else:
            assert row.change_magnitude == pytest.approx(change)
        if novelty is None:
            assert row.historical_novelty is None
        else:
            assert row.historical_novelty == pytest.approx(novelty)
        assert row.representational_mismatch == pytest.approx(mismatch)
        assert row.represented is represented
    assert artifact["team_executions"] == 0
    assert manifest["frozen_small_problem_world"]["team_executions"] == 0
    assert manifest["frozen_small_problem_world"]["G00_G08_executed_in_this_world"] is False


def test_future_campaign_choices_remain_explicitly_unfrozen():
    manifest = _manifest()
    assert manifest["development"]["eta_for_future_campaign"] is None
    unfrozen = set(manifest["future_protocol_not_frozen"])
    assert {"eta campaign", "research campaign seeds", "final G00-G08 protocol", "primary outcome variables"} <= unfrozen
