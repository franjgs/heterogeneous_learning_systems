"""Materialize Campaign 1 protocol provenance without executing Campaign 1."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.synthetic.capability_geometry_gate.run import CONFIGURATIONS  # noqa: E402
from hls.campaign1_protocol import (  # noqa: E402
    ASSESSMENT_CRITERIA,
    CONDITION_SEMANTICS,
    CONDITIONS,
    CONFIGURATION_IDS,
    CRN_POLICY,
    EMPIRICALLY_UNKNOWN,
    PARAMETERS,
    PERFORMANCE_ARTIFACTS,
    PERFORMANCE_DEFINITION,
    PRIMARY_OUTPUTS,
    PROTOCOL_ID,
    RETAINED_TRAJECTORY_VARIABLES,
    RUNS_PER_CONDITION,
    SCENARIO_IDS,
    SEEDS,
    SOURCE_TEST_RANGE_COMMIT,
    TEAM_EXECUTIONS,
    TOTAL_RUNS,
    TRAJECTORY_ARTIFACTS,
    validate_protocol,
)
from hls.campaign1_test_range import (  # noqa: E402
    CONTAMINATION_STATUS,
    HISTORIES,
    INTENDED_CONTRASTS,
)
from hls.small_problem_world import (  # noqa: E402
    BELIEF_RESETS_EACH_PROBLEM,
    HYPOTHESIS_REPERTOIRE,
    STATE_PERSISTS_BETWEEN_PROBLEMS,
    UNIFORM_PRIOR,
)

OUT = ROOT / "results" / "foundations" / "campaign1_protocol"


def main() -> None:
    validate_protocol()
    configurations = {row["configuration_id"]: row["state"] for row in CONFIGURATIONS}
    selected = {identifier: configurations[identifier] for identifier in CONFIGURATION_IDS}
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "protocol_id": PROTOCOL_ID,
        "status": "FROZEN PRE-RESULTS; CAMPAIGN 1 NOT EXECUTED",
        "provenance_boundary": "everything through this protocol commit is pre-results design",
        "test_range_commit": SOURCE_TEST_RANGE_COMMIT,
        "test_range_manifest": "results/foundations/campaign1_test_range_gate/pre_experiment_manifest.json",
        "foundation_commit": "20106d3",
        "campaign0_closure_commit": "a899c14",
        "scenario_ids": SCENARIO_IDS,
        "scenario_sequences": {key: tuple(problem[0] for problem in HISTORIES[key]) for key in SCENARIO_IDS},
        "configuration_ids": CONFIGURATION_IDS,
        "configuration_states": selected,
        "conditions": CONDITIONS,
        "condition_semantics": CONDITION_SEMANTICS,
        "parameters": PARAMETERS,
        "seeds": SEEDS,
        "common_random_numbers": CRN_POLICY,
        "run_matrix": {
            "scenarios": len(SCENARIO_IDS), "configurations": len(CONFIGURATION_IDS),
            "seeds": len(SEEDS), "conditions": len(CONDITIONS),
            "runs_per_condition": RUNS_PER_CONDITION, "total_runs": TOTAL_RUNS,
            "known_z_no_develop_included": False,
        },
        "problem_representation": {"Z_hat": HYPOTHESIS_REPERTOIRE, "prior": UNIFORM_PRIOR},
        "temporal_semantics": {
            "belief_resets_between_problems": BELIEF_RESETS_EACH_PROBLEM,
            "capability_persists_between_problems": STATE_PERSISTS_BETWEEN_PROBLEMS,
        },
        "performance_definition": PERFORMANCE_DEFINITION,
        "retained_trajectory_variables": RETAINED_TRAJECTORY_VARIABLES,
        "primary_outputs": PRIMARY_OUTPUTS,
        "controlled_contrasts": INTENDED_CONTRASTS,
        "mechanistic_control_interpretation": {
            "FULL_vs_NO-DEVELOP": "diagnostic association with capability development; not an additive causal decomposition",
            "FULL_vs_KNOWN-Z": "diagnostic association with imperfect problem knowledge/DISCOVER; not an additive causal decomposition",
        },
        "assessment_criteria": ASSESSMENT_CRITERIA,
        "empirically_unknown_before_execution": EMPIRICALLY_UNKNOWN,
        "campaign0_contamination_provenance": CONTAMINATION_STATUS,
        "selection_uses_performance_or_seed_results": False,
        "team_executions": TEAM_EXECUTIONS,
        "campaign1_performance_artifacts": PERFORMANCE_ARTIFACTS,
        "campaign1_trajectory_artifacts": TRAJECTORY_ARTIFACTS,
    }
    with (OUT / "pre_experiment_protocol.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
