"""Analyze only the CE-04 E3-addendum confirmatory contrasts.

The independent unit is a seed-level replica. This script does not inspect
task rows as independent observations and does not select policies.
"""
from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np
from scipy.stats import ttest_1samp

from hls.ce04 import holm_adjust, paired_bootstrap, tost_equivalence


ROOT = Path("results/experiments/hls_ce04_campaign")
OUTPUT = ROOT / "confirmatory_analysis.json"
SCALES = (12, 24, 48)
SEEDS = tuple(range(1000, 1030))


def load_metrics() -> dict[tuple[int, int, str, str], dict]:
    indexed = {}
    with (ROOT / "replica_metrics.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (int(row["seed"]), int(row["n_agents"]), row["composition"], row["policy"])
            if key in indexed:
                raise ValueError(f"duplicate replica {key}")
            indexed[key] = row
    expected = {(s, n, h, p) for s in SEEDS for n in SCALES
                for h in ("H0", "H1", "H2") for p in ("P0", "P1", "P2", "P3")}
    if set(indexed) != expected:
        raise ValueError(f"campaign matrix mismatch: missing={len(expected-set(indexed))}, extra={len(set(indexed)-expected)}")
    return indexed


def main() -> None:
    metrics = load_metrics()
    rates = {key: float(row["success_on_time_rate"]) for key, row in metrics.items()}

    def rate(seed: int, n: int, h: str, p: str) -> float:
        return rates[(seed, n, h, p)]

    vectors: dict[str, list[float]] = {}
    labels: dict[str, dict] = {}
    for n in SCALES:
        for cid, label in (
            ("C1", "H2-H0 under P1"),
            ("C2", "P1-P0 under H2"),
            ("C3", "P2-P1 under H2"),
            ("C4", "P3-P2 under H2"),
            ("C5", "(H2-H0 under P3) - (H2-H0 under P0)"),
        ):
            vals = []
            for s in SEEDS:
                if cid == "C1": d = rate(s,n,"H2","P1") - rate(s,n,"H0","P1")
                elif cid == "C2": d = rate(s,n,"H2","P1") - rate(s,n,"H2","P0")
                elif cid == "C3": d = rate(s,n,"H2","P2") - rate(s,n,"H2","P1")
                elif cid == "C4": d = rate(s,n,"H2","P3") - rate(s,n,"H2","P2")
                else:
                    d = ((rate(s,n,"H2","P3")-rate(s,n,"H0","P3"))
                         -(rate(s,n,"H2","P0")-rate(s,n,"H0","P0")))
                vals.append(d)
            name = f"{cid}_N{n}"
            vectors[name] = vals
            labels[name] = {"contrast": cid, "scale": n, "definition": label}

    # The protocol calls for comparing effects across scales. Use adjacent
    # scale differences, matching the existing CE-04 scale-comparison convention.
    for cid in ("C1", "C2", "C3", "C4", "C5"):
        for low, high in ((12,24),(24,48)):
            name = f"{cid}_N{high}-N{low}"
            vectors[name] = [a-b for a,b in zip(vectors[f"{cid}_N{high}"],vectors[f"{cid}_N{low}"])]
            labels[name] = {"contrast": f"scale difference in {cid}", "scales": [low,high],
                            "definition": f"{cid} at N={high} minus {cid} at N={low}"}

    names = list(vectors)
    raw_p = []
    raw_tost = []
    results = {}
    for index, name in enumerate(names):
        vals_pp = np.asarray(vectors[name], dtype=float) * 100.0
        boot = paired_bootstrap(vectors[name], seed=20261026+index, n_resamples=10_000)
        ttest_p = float(ttest_1samp(vals_pp, popmean=0.0).pvalue)
        tost = tost_equivalence(vals_pp/100.0, margin=.02)
        tost_p = max(tost["p_lower"], tost["p_upper"])
        raw_p.append(ttest_p); raw_tost.append(tost_p)
        results[name] = {
            **labels[name],
            "mean_pp": float(vals_pp.mean()),
            "sd_pp": float(vals_pp.std(ddof=1)),
            "bootstrap_ci95_pp": [100*x for x in boot["ci95"]],
            "seed_level_differences_pp": vals_pp.tolist(),
            "positive_seeds": int((vals_pp>0).sum()),
            "negative_seeds": int((vals_pp<0).sum()),
            "zero_seeds": int((vals_pp==0).sum()),
            "p_paired_t_raw": ttest_p,
            "tost_margin_pp": 2.0,
            "tost_p_raw": tost_p,
        }
    p_adj = holm_adjust(raw_p)
    tost_adj = holm_adjust(raw_tost)
    for name, p, tp in zip(names,p_adj,tost_adj):
        results[name]["p_holm"] = p
        results[name]["tost_p_holm"] = tp
        results[name]["equivalent_with_holm_0_05"] = bool(tp < .05)

    # Purely descriptive sensitivity summaries: averages are first computed
    # within each independent seed, then averaged over the 30 seeds.
    task_phase = {}
    with gzip.open(ROOT/"replicas.experiment_runs.jsonl.gz","rt",encoding="utf-8") as handle:
      run_count = 0
      for line in handle:
        run = json.loads(line)
        cfg = run["configuration"]
        key = (int(cfg["seed"]),int(cfg["n_agents"]),cfg["composition"],cfg["policy"])
        if key not in metrics or key in task_phase:
            raise ValueError(f"duplicate or unexpected ExperimentRun {key}")
        mr = run["mechanism_results"]
        task_phase[key] = {
            "by_task": [a/b if b else None for a,b in zip(mr["success_by_task"],mr["arrivals_by_task"])],
            "by_phase": [a/b if b else None for a,b in zip(mr["success_by_phase"],mr["arrivals_by_phase"])],
        }
        run_count += 1
    if run_count != 1080 or set(task_phase) != set(metrics):
        raise ValueError(f"expected 1,080 aligned ExperimentRun records; got {run_count}")
    descriptive = {}
    for n in SCALES:
        for h in ("H0","H1","H2"):
            for p in ("P0","P1","P2","P3"):
                cells=[(s,n,h,p) for s in SEEDS]
                rows=[metrics[x] for x in cells]
                descriptive[f"N{n}_{h}_{p}"]={
                    "mean_replica_success_rate":float(np.mean([float(x["success_on_time_rate"]) for x in rows])),
                    "mean_replica_rejection_fraction":float(np.mean([float(x["n_rejected"])/float(x["n_arrivals"]) for x in rows])),
                    "mean_replica_latency_mean":float(np.mean([float(x["latency_mean"]) for x in rows])),
                    "mean_replica_service_time_per_success":float(np.mean([float(x["service_time_per_success"]) for x in rows if x["service_time_per_success"] not in ("",None)])),
                    "task_success_rates_mean_by_seed":[float(np.mean([task_phase[x]["by_task"][k] for x in cells])) for k in range(4)],
                    "phase_success_rates_mean_by_seed":[float(np.mean([task_phase[x]["by_phase"][k] for x in cells])) for k in range(3)],
                }

    output={"analysis_scope":"Only CE-04 addendum C1-C5 at each scale and adjacent-scale differences; no other confirmatory contrasts.",
            "unit":"independent seed-level replicate; paired within seed and scale",
            "bootstrap":{"method":"paired percentile bootstrap over 30 seed differences","resamples":10000,"seed_base":20261026},
            "multiple_testing":{"method":"Holm step-down","family":"all 25 contrasts (15 C1-C5-by-scale + 10 adjacent-scale differences)","equivalence_family":"same 25 contrasts"},
            "practical_equivalence_margin_pp":2.0,"scale_comparisons":"adjacent N=24−12 and N=48−24 for each C1-C5",
            "contrasts":results,"descriptive_sensitivity_no_inference":descriptive}
    OUTPUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print(f"wrote {OUTPUT}; {len(results)} predeclared contrast summaries; 10,000 bootstrap draws each")


if __name__ == "__main__":
    main()
