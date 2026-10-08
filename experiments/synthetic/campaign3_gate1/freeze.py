"""Freeze Gate 1 analysis semantics before inspecting Gate 1 outcomes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
OUT = ROOT / "results" / "diagnostics" / "campaign3_gate1"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    closure = json.loads((PILOT / "horizon_pilot_closure.json").read_text())
    validation = json.loads((PILOT / "raw_validation.json").read_text())
    if closure["operational_temporal_assessment"]["ell"] != 11:
        raise RuntimeError("Gate 1 requires the CE-closed operational ell=11")
    if not validation["passed"]:
        raise RuntimeError("Gate 1 requires validated pilot data")
    OUT.mkdir(parents=True, exist_ok=False)
    freeze = {
        "artifact_type": "campaign3_gate1_pre_analysis_freeze",
        "prerequisite_horizon_closure_commit": "b485b1b91b4531d84eb121b1e20c6cf8baf20db8",
        "purpose": "continuation sensitivity of local mode value",
        "state_source": "Q11 factual states from the frozen development-only initial J=12 horizon pilot",
        "conditional_scope": "h ~ d_Q11",
        "team_ids": validation["team_ids"],
        "kernel_ids": validation["kernel_ids"],
        "histories": 840,
        "eligible_state_rule": "j(t)+11<=12",
        "eligible_problem_indices": [1],
        "eligible_states": 2520,
        "operational_ell": 11,
        "tau": {
            "definition": "number of real mu_true rewards from the current decision through e(j(t)+11), inclusive",
            "formula": "tau=3*(ell+1)-(decision-1), with ell=11",
            "values": [36, 35, 34],
            "inputs": ["known problem index", "known within-problem decision", "frozen ell", "three decisions per problem"],
            "privileged_future_information": False,
        },
        "initial_modes": ["Q00", "Q10", "Q01", "Q11"],
        "continuation_probes": ["Q00", "Q11"],
        "continuation_interpretation": "contrasting probes; not bounds, extrema, envelope, or approximation to all continuations",
        "mode_tie_break": {
            "mode_order": ["Q00", "Q10", "Q01", "Q11"],
            "tolerance": 1e-10,
            "rule": "first mode in frozen order within tolerance of maximum realized Y",
        },
        "ranking": {
            "deterministic_order": "descending Y; values tied within 1e-10 use frozen mode order",
            "stability": "exact deterministic rank agreement plus six pairwise sign/tie comparisons",
        },
        "advantages": "A_m^c=Y_m^c-Y_Q00^c for m in Q10,Q01,Q11",
        "regrets": {
            "R_00_to_11": "Y_best11^11-Y_best00^11",
            "R_11_to_00": "Y_best00^00-Y_best11^00",
            "units": "absolute natural mu_true performance units",
            "normalized_R_over_D": False,
            "materiality_threshold": None,
        },
        "minimum_analysis": ["best-mode/ranking stability", "sign stability", "absolute regret distributions", "tau dependence"],
        "uncertainty": {
            "cluster_unit": "complete base history/seed",
            "bootstrap_indices": "campaign3_horizon_pilot/initial_j12/bootstrap_history_indices.npy",
            "B": 2000,
            "seed": 20261013,
            "significance_tests": False,
        },
        "source_sha256": {
            name: digest(PILOT / name)
            for name in (
                "horizon_pilot_closure.json",
                "raw_validation.json",
                "counterfactual_branch_returns.csv.gz",
                "factual_states.csv.gz",
                "bootstrap_history_indices.npy",
            )
        },
        "firewalls": {
            "heldout_execution": False,
            "gate_2": False,
            "predictor_training": False,
            "metacontroller_training": False,
            "true_world_explanatory_variables": False,
            "horizon_reopened": False,
        },
    }
    (OUT / "pre_analysis_gate1.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
