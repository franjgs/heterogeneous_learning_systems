"""Frozen post-run B4 analysis; VALIDATION only and training-free."""

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
    spec = importlib.util.spec_from_file_location("b4_run_for_analysis", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B4 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


b4 = _load_run()


def operational_value(scores, deep, cost):
    return float(sum(max(scores[d], deep[d] - cost) for d in b4.DOMAINS) / 4)


def run_analysis(output_dir: Path, b23_output: Path, b24_output: Path) -> dict[str, object]:
    b24_analysis = b4._load_module("b4_final_b24_analysis", b4.B24_ANALYZE_PATH)
    parent_scores, audit = b24_analysis.compatibility_audit(b24_output, b23_output)
    progress = json.loads((output_dir / "progress.json").read_text())
    metric_rows, value_rows = [], []
    for spec in b4.b24.plan_cases():
        artifact_id = f"PREP_s{spec.seed}_{spec.domain}_n{spec.n}"
        record = progress["fits"].get(artifact_id, {})
        path = Path(str(record.get("path", "")))
        if record.get("status") != "complete" or not path.is_file() or b4.sha256_file(path) != record.get("sha256"):
            raise RuntimeError(f"missing/corrupt PREP state {artifact_id}")
        payload = b4.b24.b23.load_checkpoint(path)
        if payload.get("evaluation_split") != "validation" or payload.get("TEST_STATUS") != b4.TEST_STATUS:
            raise RuntimeError(f"invalid PREP evaluation provenance {artifact_id}")
        f0 = parent_scores[("F0", spec.seed, spec.n, spec.domain)]
        deep = parent_scores[("D", spec.seed, spec.n, spec.domain)]
        rep = parent_scores[("REP", spec.seed, spec.n, spec.domain)]
        prep = payload["scores"]
        ideal = {d: (rep[d] if d == spec.domain else max(rep[d], f0[d])) for d in b4.DOMAINS}
        local = prep[spec.domain] - f0[spec.domain]
        cross = sum(prep[d] - f0[d] for d in b4.DOMAINS if d != spec.domain)
        metric_rows.append({
            "seed": spec.seed, "target_domain": spec.domain, "N": spec.n,
            "DeltaS_local_PREP": local, "DeltaS_cross_PREP": cross,
            "DeltaS_local_REP": rep[spec.domain] - f0[spec.domain],
            "DeltaS_cross_REP": sum(rep[d] - f0[d] for d in b4.DOMAINS if d != spec.domain),
            "accepted_blocks": payload["accepted_blocks"], "rejected_blocks": payload["rejected_blocks"],
            **payload["timing"],
            **{f"S_PREP_{d}": prep[d] for d in b4.DOMAINS},
            **{f"DeltaS_PREP_{d}": prep[d] - f0[d] for d in b4.DOMAINS},
            **{f"DeltaS_REP_{d}": rep[d] - f0[d] for d in b4.DOMAINS},
        })
        rho_by_cost = {c: f0[spec.domain] - (deep[spec.domain] - c) for c in b4.COSTS}
        for cost in b4.COSTS:
            v0 = operational_value(f0, deep, cost)
            delta_rep = operational_value(rep, deep, cost) - v0
            delta_prep = operational_value(prep, deep, cost) - v0
            delta_ideal = operational_value(ideal, deep, cost) - v0
            denominator = delta_ideal - delta_rep
            value_rows.append({
                "seed": spec.seed, "target_domain": spec.domain, "N": spec.n, "c": cost,
                "rho": rho_by_cost[cost], "DeltaV_REP": delta_rep,
                "DeltaV_PREP": delta_prep, "DeltaV_IDEAL": delta_ideal,
                "recovery": (delta_prep - delta_rep) / denominator if denominator > 0 else np.nan,
            })
    metrics, values = pd.DataFrame(metric_rows), pd.DataFrame(value_rows)
    if len(metrics) != 60 or len(values) != 300 or metrics.isna().any().any():
        raise RuntimeError("B4 analytical cardinality/NaN failure")
    seed_means = metrics.groupby("seed", as_index=False).agg(
        mean_cross=("DeltaS_cross_PREP", "mean"), mean_local=("DeltaS_local_PREP", "mean")
    )
    protection_seeds = int((seed_means.mean_cross >= 0).sum())
    learning_seeds = int((seed_means.mean_local >= 0).sum())
    structure_rows = []
    for (domain, n), group in values.groupby(["target_domain", "N"]):
        by_cost = group.groupby("c").DeltaV_PREP.apply(lambda x: int((x > 0).sum()))
        structure_rows.append({"target_domain": domain, "N": n, "all_costs_4of5": bool((by_cost >= 4).all())})
    value_structures = sum(bool(x["all_costs_4of5"]) for x in structure_rows)
    surface_rows = []
    for row in values.itertuples(index=False):
        for h in b4.HORIZONS:
            surface_rows.append({**row._asdict(), "h": h, "kappa_star": h * row.DeltaV_PREP - max(row.rho, 0)})
    surface = pd.DataFrame(surface_rows)
    cell_support = surface.groupby(["c", "h", "seed"]).kappa_star.max().gt(0).groupby(["c", "h"]).sum()
    integration_cells = int((cell_support >= 4).sum())
    positive = protection_seeds >= 4 and learning_seeds >= 4 and value_structures >= 1 and integration_cells >= 1
    null = value_structures == 0 and integration_cells == 0
    classification = "POSITIVE" if positive else ("NULL" if null else "INCONCLUSIVE")
    summary = {
        "technical_status": "PASS", "classification": classification,
        "TEST_STATUS": b4.TEST_STATUS, "provenance": "PASS",
        "protection_nonnegative_seeds": protection_seeds,
        "learning_nonnegative_seeds": learning_seeds,
        "value_structures_4of5_all_costs": value_structures,
        "integration_cells_4of5": integration_cells,
        "fits": 60, "validation_evaluations": 60,
        "parent_compatibility": audit,
    }
    b4.b24.atomic_csv(output_dir / "raw_metrics.csv", metrics)
    b4.b24.atomic_csv(output_dir / "value_surface.csv", surface)
    b4.b24.atomic_csv(output_dir / "seed_summary.csv", seed_means)
    b4.atomic_json(output_dir / "summary.json", summary)
    return summary
