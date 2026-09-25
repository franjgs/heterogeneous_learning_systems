"""Frozen B5 post-run analysis using VALIDATION scores only."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RUN_PATH = Path(__file__).with_name("run.py")


def _load_run():
    spec = importlib.util.spec_from_file_location("b5_run_for_analysis", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B5 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


b5 = _load_run()


def value(scores, deep, cost):
    return float(sum(max(scores[d], deep[d] - cost) for d in b5.DOMAINS) / 4)


def run_analysis(output_dir: Path, b23_output: Path, b24_output: Path):
    parent_analyzer = b5._load_module("b5_final_b24_analysis", b5.B24_ANALYZE_PATH)
    parent_scores, audit = parent_analyzer.compatibility_audit(b24_output, b23_output)
    progress = json.loads((output_dir / "progress.json").read_text())
    metrics, valuations = [], []
    for spec in b5.b24.plan_cases():
        artifact_id = f"GREP_s{spec.seed}_{spec.domain}_n{spec.n}"
        record = progress["fits"].get(artifact_id, {})
        path = Path(str(record.get("path", "")))
        if record.get("status") != "complete" or not path.is_file() or b5.sha256_file(path) != record.get("sha256"):
            raise RuntimeError(f"missing/corrupt GREP {artifact_id}")
        payload = b5.b24.b23.load_checkpoint(path)
        if payload.get("evaluation_split") != "validation" or payload.get("TEST_STATUS") != b5.TEST_STATUS:
            raise RuntimeError(f"invalid GREP provenance {artifact_id}")
        f0 = parent_scores[("F0", spec.seed, spec.n, spec.domain)]
        deep = parent_scores[("D", spec.seed, spec.n, spec.domain)]
        rep = parent_scores[("REP", spec.seed, spec.n, spec.domain)]
        grep = payload["scores"]
        ideal = {d: rep[d] if d == spec.domain else max(rep[d], f0[d]) for d in b5.DOMAINS}
        metrics.append({
            "seed": spec.seed, "target_domain": spec.domain, "N": spec.n,
            "local_GREP": grep[spec.domain] - f0[spec.domain],
            "cross_GREP": sum(grep[d] - f0[d] for d in b5.DOMAINS if d != spec.domain),
            "local_REP": rep[spec.domain] - f0[spec.domain],
            "cross_REP": sum(rep[d] - f0[d] for d in b5.DOMAINS if d != spec.domain),
            "projected_steps": payload["projected_steps"], "total_steps": payload["steps"],
            "projection_rate": payload["projection_rate"], "training_time": payload["training_time"],
            **{f"DeltaS_GREP_{d}": grep[d] - f0[d] for d in b5.DOMAINS},
        })
        for cost in b5.COSTS:
            v0 = value(f0, deep, cost)
            dv_rep = value(rep, deep, cost) - v0
            dv_grep = value(grep, deep, cost) - v0
            dv_ideal = value(ideal, deep, cost) - v0
            denominator = dv_ideal - dv_rep
            valuations.append({
                "seed": spec.seed, "target_domain": spec.domain, "N": spec.n, "c": cost,
                "rho": f0[spec.domain] - (deep[spec.domain] - cost),
                "DeltaV_REP": dv_rep, "DeltaV_GREP": dv_grep,
                "DeltaV_GREP_minus_REP": dv_grep - dv_rep,
                "DeltaV_IDEAL": dv_ideal,
                "recovery": (dv_grep - dv_rep) / denominator if denominator > 0 else np.nan,
            })
    metrics, valuations = pd.DataFrame(metrics), pd.DataFrame(valuations)
    seed_means = metrics.groupby("seed", as_index=False).agg(
        mean_cross_GREP=("cross_GREP", "mean"), mean_local_GREP=("local_GREP", "mean"),
        mean_cross_REP=("cross_REP", "mean"), mean_local_REP=("local_REP", "mean"),
    )
    a = int((seed_means.mean_cross_GREP >= 0).sum())
    b = int((seed_means.mean_local_GREP >= 0).sum())
    cross_improved = int((seed_means.mean_cross_GREP > seed_means.mean_cross_REP).sum())
    structures = []
    for (domain, n), group in valuations.groupby(["target_domain", "N"]):
        support = group.groupby("c").DeltaV_GREP.apply(lambda x: int((x > 0).sum()))
        structures.append({"target_domain": domain, "N": n, "all_costs_4of5": bool((support >= 4).all())})
    c_count = sum(row["all_costs_4of5"] for row in structures)
    surface_rows = []
    for row in valuations.itertuples(index=False):
        for horizon in b5.HORIZONS:
            surface_rows.append({**row._asdict(), "h": horizon, "kappa_star": horizon * row.DeltaV_GREP - max(row.rho, 0)})
    surface = pd.DataFrame(surface_rows)
    cell_support = surface.groupby(["c", "h", "seed"]).kappa_star.max().gt(0).groupby(["c", "h"]).sum()
    d_count = int((cell_support >= 4).sum())
    positive = a >= 4 and b >= 4 and c_count >= 1 and d_count >= 1
    null = c_count == 0 and d_count == 0 and cross_improved < 4
    classification = "POSITIVE" if positive else ("NULL" if null else "INCONCLUSIVE")
    summary = {
        "technical_status": "PASS", "classification": classification,
        "TEST_STATUS": b5.TEST_STATUS, "provenance": "PASS",
        "cross_nonnegative_seeds": a, "local_nonnegative_seeds": b,
        "cross_improved_vs_REP_seeds": cross_improved,
        "value_structures_4of5_all_costs": c_count,
        "integration_cells_4of5": d_count, "parent_compatibility": audit,
    }
    b5.b24.atomic_csv(output_dir / "raw_metrics.csv", metrics)
    b5.b24.atomic_csv(output_dir / "value_surface.csv", surface)
    b5.b24.atomic_csv(output_dir / "seed_summary.csv", seed_means)
    b5.atomic_json(output_dir / "summary.json", summary)
    return summary
