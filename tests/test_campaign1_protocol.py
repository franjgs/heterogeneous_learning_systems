"""Pre-results validation of the frozen Campaign 1 execution protocol."""

import inspect
import json
from pathlib import Path

from experiments.synthetic.capability_geometry_gate.run import CONFIGURATIONS
from hls.campaign1_protocol import (
    ASSESSMENT_CRITERIA,
    CONDITION_SEMANTICS,
    CONDITIONS,
    CONFIGURATION_IDS,
    EMPIRICALLY_UNKNOWN,
    PARAMETERS,
    PERFORMANCE_ARTIFACTS,
    PERFORMANCE_DEFINITION,
    RUNS_PER_CONDITION,
    SCENARIO_IDS,
    SEEDS,
    TEAM_EXECUTIONS,
    TOTAL_RUNS,
    TRAJECTORY_ARTIFACTS,
    validate_protocol,
)
from hls.campaign1_test_range import HISTORIES, INTENDED_CONTRASTS
from hls.discover_v0 import DEFAULT_HORIZON, DEFAULT_SIGMA, N_AGENTS, N_CAPABILITIES, RHO
from hls.finite_problem_belief import finite_choose_dynamic_action_v2


EXPECTED_STATES = {
    "G00": ((0.5, 0.5), (0.5, 0.5), (0.5, 0.5)),
    "G04": ((0.25, 0.75), (0.625, 0.375), (0.625, 0.375)),
    "G05": ((0.0, 1.0), (0.5, 0.5), (1.0, 0.0)),
    "G07": ((0.0, 1.0), (0.5, 0.0), (1.0, 0.5)),
}


def test_protocol_exact_cardinality_and_run_count():
    validate_protocol()
    assert len(SCENARIO_IDS) == 8 and SCENARIO_IDS == tuple(HISTORIES)
    assert CONFIGURATION_IDS == ("G00", "G04", "G05", "G07")
    assert SEEDS == tuple(range(10))
    assert CONDITIONS == ("FULL", "NO-DEVELOP", "KNOWN-Z")
    assert RUNS_PER_CONDITION == 8 * 4 * 10 == 320
    assert TOTAL_RUNS == 3 * 320 == 960


def test_probe_states_resolve_exactly_to_existing_canonical_configurations():
    canonical = {row["configuration_id"]: row["state"] for row in CONFIGURATIONS}
    assert {identifier: canonical[identifier] for identifier in CONFIGURATION_IDS} == EXPECTED_STATES


def test_frozen_parameters_match_current_implementation():
    assert PARAMETERS == {
        "N": N_AGENTS, "K": N_CAPABILITIES, "rho": RHO,
        "sigma": DEFAULT_SIGMA, "eta": 0.35, "horizon_per_problem": DEFAULT_HORIZON,
    }
    assert PARAMETERS == {"N": 3, "K": 2, "rho": .5, "sigma": .10, "eta": .35, "horizon_per_problem": 3}


def test_conditions_are_exact_and_no_develop_uses_same_existing_mpc_primitive():
    assert CONDITION_SEMANTICS["FULL"]["selector"] == "finite_choose_dynamic_action_v2(develop=True)"
    assert CONDITION_SEMANTICS["NO-DEVELOP"]["selector"] == "finite_choose_dynamic_action_v2(develop=False)"
    assert "develop" in inspect.signature(finite_choose_dynamic_action_v2).parameters
    assert CONDITION_SEMANTICS["KNOWN-Z"]["existing_control"] == "DEVELOP_KNOWN"
    assert "DISCOVER_ONLY" in CONDITION_SEMANTICS["NO-DEVELOP"]["warning"]


def test_performance_and_control_interpretation_are_frozen_without_predictions():
    assert "mu_true" in PERFORMANCE_DEFINITION
    assert "not substituted" in PERFORMANCE_DEFINITION
    assert set(ASSESSMENT_CRITERIA) == {"PASS", "PARTIAL", "FAIL"}
    assert len(EMPIRICALLY_UNKNOWN) == 13
    assert "which configuration performs best" in EMPIRICALLY_UNKNOWN
    assert set(INTENDED_CONTRASTS) == {
        "persistence_representation", "ordered_displacement",
        "recurrence_displacement", "developmental_history_return",
    }


def test_protocol_freeze_has_no_execution_or_results():
    assert TEAM_EXECUTIONS == PERFORMANCE_ARTIFACTS == TRAJECTORY_ARTIFACTS == 0
    out = Path("results/foundations/campaign1_protocol")
    assert not (out / "runs.csv").exists()
    assert not (out / "trajectories.csv").exists()
    assert not (out / "performance.csv").exists()


def test_materialized_manifest_matches_protocol_and_fixture():
    path = Path("results/foundations/campaign1_protocol/pre_experiment_protocol.json")
    manifest = json.loads(path.read_text())
    assert tuple(manifest["scenario_ids"]) == SCENARIO_IDS
    assert tuple(manifest["configuration_ids"]) == CONFIGURATION_IDS
    assert tuple(manifest["conditions"]) == CONDITIONS
    assert tuple(manifest["seeds"]) == SEEDS
    assert manifest["run_matrix"]["total_runs"] == TOTAL_RUNS
    assert not manifest["run_matrix"]["known_z_no_develop_included"]
    assert manifest["scenario_sequences"] == {
        key: [problem[0] for problem in HISTORIES[key]] for key in SCENARIO_IDS
    }
    assert manifest["team_executions"] == 0
    assert manifest["campaign1_performance_artifacts"] == 0
    assert manifest["campaign1_trajectory_artifacts"] == 0
