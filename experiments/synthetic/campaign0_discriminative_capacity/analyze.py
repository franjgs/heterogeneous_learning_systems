"""Reproduce compact derived trajectory cases from frozen Campaign 0 raw data."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "results" / "diagnostics" / "campaign0_discriminative_capacity"
CASES = (
    ("order_divergence_G00", "G00", "H0", 0),
    ("order_divergence_G00", "G00", "H1", 0),
    ("descriptor_matched_G05_G07", "G05", "H0", 0),
    ("descriptor_matched_G05_G07", "G07", "H0", 0),
    ("order_divergence_G05", "G05", "H0", 0),
    ("order_divergence_G05", "G05", "H1", 0),
    ("order_null_G07", "G07", "H0", 0),
    ("order_null_G07", "G07", "H1", 0),
    ("order_near_convergence_G04", "G04", "H0", 0),
    ("order_near_convergence_G04", "G04", "H1", 0),
)


def main() -> None:
    trajectories = pd.read_csv(OUT / "trajectories.csv")
    rows = []
    for case, team, history, seed in CASES:
        selected = trajectories[(trajectories.team == team) & (trajectories.history == history) & (trajectories.seed == seed)]
        for problem_index, group in selected.groupby("problem_index", sort=True):
            rows.append({
                "case": case, "team": team, "history": history, "seed": seed,
                "problem_index": int(problem_index), "p": float(group.iloc[0].p),
                "problem_performance": float(group.mu_true.sum()),
                "S_problem_start": group.iloc[0].S_before,
                "actions": "|".join(group.action),
                "development_increments": "|".join(group.development_increment),
                "S_problem_end": group.iloc[-1].S_after,
                "belief_end": group.iloc[-1].belief_after,
            })
    path = OUT / "representative_trajectories.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    summary = json.loads((OUT / "manifest.json").read_text())
    summary["analysis"]["classification"] = "PASS"
    summary["analysis"]["classification_basis"] = (
        "Capability-state path dependence is directly observed; final-A mean ranking differs between "
        "content-matched H0/H1, with the dominant per-seed ranking pattern reversing 8/10 versus 2/10."
    )
    summary["analysis"]["representative_case_policy"] = (
        "Seed 0 was used uniformly for readable causal traces; cases include divergence, descriptor-matched "
        "G05/G07, exact order-null G07, and near-convergent G04."
    )
    (OUT / "manifest.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
