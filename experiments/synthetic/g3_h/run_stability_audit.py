"""Targeted theorem-falsification audit for strong condition C in G3-H."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from random import Random
from time import perf_counter

from hls.g3_h_regime_map import REGIME_TOL, evaluate_point
from hls.g3_h_stability_audit import condition_c, continuation_head
from hls.g3_organizational_value import G3A_ASSIGNMENTS, reward_g3a


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "results/foundations/g3_h_stability_audit"
SCALES = (0.0001, 0.003, 0.03, 0.3, 1.0, 3.0, 10.0, 100.0)
REGIONS = (("low", 1e-9, 0.12), ("intermediate", 0.05, 0.95), ("near_saturation", 0.88, 1.0 - 1e-9))


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with (OUTPUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def label(action: tuple[int, int]) -> str:
    return f"({action[0] + 1},{action[1] + 1})"


def competitor_margin(evaluation) -> float:
    """C margin excluding y=bar, whose self-comparison makes raw C margin zero."""
    values = []
    for record in evaluation.actions:
        for optimizer in evaluation.optimal_use:
            for alternative in G3A_ASSIGNMENTS:
                if alternative != optimizer:
                    values.append(reward_g3a(record.successor, optimizer) - reward_g3a(record.successor, alternative))
    return min(values)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    start = perf_counter()
    summaries: list[dict[str, object]] = []
    boundaries: list[dict[str, object]] = []
    best = {"homogeneous": None, "heterogeneous": None}
    # This is an adversarial, stratified stress test, not a prevalence sample.
    per_cell = 300
    for condition, seed in (("homogeneous", 20261009), ("heterogeneous", 20261010)):
        rng = Random(seed)
        for region, lower, upper in REGIONS:
            for scale in SCALES:
                stable = unique = positive = 0
                max_regret = 0.0
                for _ in range(per_cell):
                    flat = [rng.uniform(lower, upper) for _ in range(6)]
                    state = ((flat[0], flat[1]), (flat[2], flat[3]), (flat[4], flat[5]))
                    if condition == "homogeneous":
                        profile = (scale, scale, scale)
                    else:
                        profile = tuple(scale * 10.0 ** rng.uniform(-1.0, 1.0) for _ in range(3))
                    evaluation = evaluate_point(state, profile)
                    audit = condition_c(evaluation)
                    if not audit.holds:
                        continue
                    stable += 1
                    unique += len(evaluation.optimal_use) == 1
                    max_regret = max(max_regret, evaluation.regret_use)
                    if best[condition] is None or evaluation.regret_use > best[condition].regret_use:
                        best[condition] = evaluation
                    positive += evaluation.regret_use > REGIME_TOL
                    cmargin = competitor_margin(evaluation)
                    if cmargin <= 0.002:
                        boundaries.append({
                            "condition": condition, "region": region, "eta_scale": scale,
                            "state": json.dumps(flat), "eta": json.dumps(profile),
                            "condition_c_holds": audit.holds, "condition_c_raw_margin": audit.margin,
                            "competitor_margin": cmargin,
                            "A_U": json.dumps([label(a) for a in sorted(evaluation.optimal_use)]),
                            "A_Q": json.dumps([label(a) for a in sorted(evaluation.optimal_dynamic)]),
                            "regret_U": evaluation.regret_use,
                        })
                summaries.append({
                    "condition": condition, "region": region, "eta_scale": scale,
                    "draws": per_cell, "C_stable": stable, "unique_USE_within_stable": unique,
                    "positive_regret_U_within_stable": positive, "max_regret_U_within_stable": max_regret,
                })
    write_csv("stable_search_summary.csv", summaries)
    write_csv("boundary_search.csv", boundaries)
    best_rows = {}
    for condition, evaluation in best.items():
        assert evaluation is not None
        audit = condition_c(evaluation)
        h = {label(a.action): continuation_head(evaluation.state, a.action, evaluation.learning_profile) for a in evaluation.actions}
        best_rows[condition] = {
            "state": evaluation.state, "eta": evaluation.learning_profile,
            "condition_c": audit.holds, "raw_margin": audit.margin, "competitor_margin": competitor_margin(evaluation),
            "A_U": [label(a) for a in sorted(evaluation.optimal_use)],
            "A_L": [label(a) for a in sorted(evaluation.optimal_local)],
            "A_Q": [label(a) for a in sorted(evaluation.optimal_dynamic)],
            "regret_U": evaluation.regret_use, "regret_L": evaluation.regret_local, "H": h,
        }
    summary = {
        "primary_condition": "C: all current USE optimizers remain reward-optimal after every one-step endogenous transition",
        "q_reduction": "Q_S(x)=R(S,x)-V(S)+H(x), H(x)=max_y[R(F(S,x),y)+V(F(F(S,x),y))]",
        "necessary_comparison_for_u": "H(x)-H(u) <= R(S,u)-R(S,x) for every x",
        "important_margin_note": "min over all y includes y=a_bar, hence the raw C margin is always <= 0 and equals 0 whenever C holds; competitor_margin excludes y=a_bar.",
        "per_cell": per_cell, "scales": SCALES, "regions": REGIONS,
        "best_stable_examples": best_rows, "runtime_seconds": perf_counter() - start,
    }
    (OUTPUT / "audit_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "seeds": {"homogeneous": 20261009, "heterogeneous": 20261010},
        "state_sampling": "uniform independently within each declared competence region", "heterogeneous_eta": "scale * 10^Uniform(-1,1)",
        "tolerance": REGIME_TOL, "purpose": "falsification of C, not prevalence estimation",
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
