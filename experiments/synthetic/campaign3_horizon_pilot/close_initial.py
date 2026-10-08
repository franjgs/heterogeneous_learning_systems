"""Close the initial J=12 evidence and authorize—but never execute—J=18."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "campaigns" / "campaign3_horizon_pilot" / "initial_j12"
FREEZE = ROOT / "results" / "foundations" / "campaign3_horizon_pilot" / "pre_execution_horizon_pilot.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(row, name):
    return float(row[name])


def main() -> None:
    freeze = json.loads(FREEZE.read_text())
    validation_path = OUT / "raw_validation.json"
    analysis_manifest_path = OUT / "analysis_manifest.json"
    common_path = OUT / "common_support_summary.csv"
    available_path = OUT / "available_state_summary.csv"
    validation = json.loads(validation_path.read_text())
    analysis_manifest = json.loads(analysis_manifest_path.read_text())
    if not validation["passed"] or analysis_manifest["windows"] != [2, 5, 11]:
        raise RuntimeError("validated preregistered evidence is required")
    common = read_csv(common_path)
    available = read_csv(available_path)
    long_boundary = [
        row for row in common
        if int(row["window_L"]) == 11 and int(row["ell"]) in (9, 10, 11)
    ]
    evidence = [{
        "continuation": row["continuation"],
        "mode": row["mode"],
        "ell": int(row["ell"]),
        "mean_Delta": number(row, "mean_Delta"),
        "mean_Delta_ci": [number(row, "mean_Delta_ci_low"), number(row, "mean_Delta_ci_high")],
        "mean_delta": number(row, "mean_delta"),
        "mean_delta_ci": [number(row, "mean_delta_ci_low"), number(row, "mean_delta_ci_high")],
    } for row in long_boundary]
    hashes = {
        "pre_execution_horizon_pilot.json": digest(FREEZE),
        "raw_validation.json": digest(validation_path),
        "analysis_manifest.json": digest(analysis_manifest_path),
        "common_support_summary.csv": digest(common_path),
        "available_state_summary.csv": digest(available_path),
    }
    created = datetime.now(timezone.utc).isoformat()
    classification = {
        "artifact_type": "campaign3_horizon_pilot_initial_j12_classification",
        "created_utc": created,
        "classification": "PERSISTENT BOUNDARY EVOLUTION",
        "frozen_rule_applied": True,
        "current_J": 12,
        "histories_per_cell": 5,
        "windows": [2, 5, 11],
        "decision": "AUTHORIZE J=18; DO NOT INCREASE REPLICATION",
        "rationale": [
            "At the L=11 early-state boundary, multiple consecutive marginal contributions continue coherently rather than appearing as one isolated terminal fluctuation.",
            "Under Q00 continuation, Q10/Q01/Q11 retain positive boundary accumulation with history-level intervals above zero at ell=9..11.",
            "Under Q11 continuation, Q01 continues positive accumulation while Q10 and Q11 show coherent late-range decreases; temporal evolution therefore remains present under both probes.",
            "The evidence is sufficiently precise to distinguish persistent boundary evolution from insufficient temporal precision.",
        ],
        "not_inferred": [
            "mode superiority", "continuation superiority", "continuation robustness",
            "state-space coverage", "Gate 1 conclusions", "Gate 2 conclusions",
        ],
        "boundary_evidence": evidence,
        "evidence_sha256": hashes,
        "escalation_histories_generated": 0,
    }
    classification_path = OUT / "pilot_classification.json"
    dump(classification_path, classification)

    decision = {
        "artifact_type": "campaign3_horizon_pilot_pre_extension_decision",
        "created_utc": created,
        "authorization": "J=18",
        "classification": "PERSISTENT BOUNDARY EVOLUTION",
        "current_J": 12,
        "current_histories_per_cell": 5,
        "authorized_histories_per_cell": 5,
        "replication_5_to_10_authorized": False,
        "authorized_next_J": 18,
        "future_histories_must_be_fresh_and_independent": True,
        "inspected_J12_histories_may_be_extended": False,
        "frozen_J18_common_support_windows": [2, 5, 17],
        "window_derivation": {
            "short": 2,
            "intermediate": 5,
            "full_range_early_state": "J-1=17; first-problem states only",
            "outcome_dependent_selection": False,
        },
        "unchanged_design": {
            "s_pilot": freeze["team_design"]["s_pilot_ids"],
            "phi_pilot": freeze["generator_design"]["phi_pilot_ids"],
            "factual_state_source": "Q11",
            "initial_modes": ["Q00", "Q10", "Q01", "Q11"],
            "continuations": ["Q00", "Q11"],
            "CRN_semantics": freeze["crn_semantics"]["identifier"],
        },
        "evidence_sha256": {**hashes, "pilot_classification.json": digest(classification_path)},
        "J18_histories_generated": 0,
        "heldout_execution": False,
        "gate_1_analysis": False,
        "gate_2_analysis": False,
    }
    decision_path = OUT / "j12_to_j18_decision.json"
    dump(decision_path, decision)

    sample_sizes = {
        "common_support": {
            "L2": {"problem_indices": list(range(1, 11)), "histories": 840, "factual_states": 25_200, "paired_rows_per_curve": 25_200, "paired_rows_all_curves_and_ell": 453_600},
            "L5": {"problem_indices": list(range(1, 8)), "histories": 840, "factual_states": 17_640, "paired_rows_per_curve": 17_640, "paired_rows_all_curves_and_ell": 635_040},
            "L11": {"problem_indices": [1], "histories": 840, "factual_states": 2_520, "paired_rows_per_curve": 2_520, "paired_rows_all_curves_and_ell": 181_440, "label": "EARLY-STATE DIAGNOSTIC"},
        },
        "available_state": {
            str(ell): {
                "problem_indices": list(range(1, 13 - ell)),
                "histories": 840,
                "factual_states": 2_520 * (12 - ell),
                "paired_rows_per_curve": 2_520 * (12 - ell),
                "paired_rows_all_six_curves": 15_120 * (12 - ell),
            }
            for ell in range(12)
        },
    }
    summary = {
        "artifact_type": "campaign3_horizon_pilot_initial_j12_summary",
        "classification": classification["classification"],
        "next_step_under_frozen_rule": "J=18",
        "raw_counts": validation["counts"],
        "conceptual_counts": {
            "factual_histories": 840,
            "factual_decision_states": 30_240,
            "initial_mode_by_continuation_branch_starts": 241_920,
            "mode_vs_Q00_pair_starts": 181_440,
            "problem_indexed_branch_return_rows": 1_572_480,
            "problem_indexed_pair_rows": 1_179_360,
        },
        "sample_sizes": sample_sizes,
        "bootstrap": analysis_manifest["bootstrap"],
        "development_result": {
            "mode": "Q01",
            "neutral_summary": "The Q01 contrast continued to accumulate at the L=11 boundary under both continuation probes; accumulation was much larger under Q00 continuation than under Q11 continuation.",
            "no_mode_or_continuation_ranking_inferred": True,
        },
        "sha256": {
            **hashes,
            "pilot_classification.json": digest(classification_path),
            "j12_to_j18_decision.json": digest(decision_path),
        },
        "escalation_histories_generated": 0,
    }
    dump(OUT / "analysis_summary.json", summary)
    print(json.dumps({"classification": summary["classification"], "next": summary["next_step_under_frozen_rule"], "counts": summary["raw_counts"]}, indent=2))


if __name__ == "__main__":
    main()
