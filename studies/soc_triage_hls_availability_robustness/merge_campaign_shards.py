"""Merge disjoint seed shards, validate the 400-block pairing, and recompute global CIs."""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"src"),str(ROOT)]
from studies.soc_triage_hls_availability_robustness.run_availability_campaign import (
    CONFIG, OUT, CUTOFF, _summarize, _write,
)

INTS={"seed","n_L2","admitted","true_need_count","TP","FP","FN","TN",
      "S_plus_numerator","S_plus_denominator","L1_backlog_H","L1_backlog_cutoff",
      "L2_backlog_H","L2_backlog_cutoff","L2_completed_tasks","L2_completed_late",
      "WAPS_switch_count","available_hours_per_l2"}
STRINGS={"classifier_id","policy","calendar","trace_hash","exogenous_hash",
         "recommendation_hash","need_hash","l1_assignment_hash"}

def _load(path):
    rows=[]
    for raw in csv.DictReader(path.open(encoding="utf-8")):
        c={"classifier_id":raw["classifier_id"],"rho_L1":float(raw["rho_L1"]),
           "alpha":float(raw["alpha"]),"n_L2":int(raw["n_L2"]),"policy":raw["policy"],
           "calendar":raw["calendar"],"seed":int(raw["seed"])}
        row={"condition":c}
        for k,v in raw.items():
            if k in c: continue
            if k in STRINGS: row[k]=v
            elif v=="": row[k]=""
            elif k in INTS: row[k]=int(float(v))
            else:
                try: row[k]=float(v)
                except ValueError: row[k]=v
        rows.append(row)
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("shards",nargs="+",type=Path)
    p.add_argument("--output-dir",type=Path,default=OUT)
    p.add_argument("--expected-seeds",type=int,default=int(CONFIG["seed_blocks"]))
    args=p.parse_args()
    out=args.output_dir if args.output_dir.is_absolute() else ROOT/args.output_dir
    rows=[]; trace=[]; seed_sets=[]
    for d0 in args.shards:
        d=d0 if d0.is_absolute() else ROOT/d0
        checks=json.loads((d/"validation_checks.json").read_text())
        if checks["status"]!="PASS": raise ValueError(f"failed shard {d}")
        rs=_load(d/"episodes.csv"); rows.extend(rs)
        seed_sets.append(set(r["condition"]["seed"] for r in rs))
        trace.extend(csv.DictReader((d/"trace_audit.csv").open(encoding="utf-8")))
    seeds=sorted({r["condition"]["seed"] for r in rows})
    if len(seeds)!=args.expected_seeds or len(seeds)!=sum(len(x) for x in seed_sets):
        raise ValueError(f"seed coverage mismatch: unique={len(seeds)} shard sum={sum(len(x) for x in seed_sets)}")
    if any(seed_sets[i]&seed_sets[j] for i in range(len(seed_sets)) for j in range(i)):
        raise ValueError("seed shards overlap")
    expected=len(seeds)*len(CONFIG["classifiers"])*len(CONFIG["rho_L1"])*len(CONFIG["alpha"])*len(CONFIG["n_L2"])*len(CONFIG["policies"])*len(CONFIG["calendar_conditions"])
    if len(rows)!=expected: raise ValueError(f"episode rows {len(rows)} != {expected}")
    paired={}
    for r in rows:
        c=r["condition"]; k=(c["classifier_id"],c["rho_L1"],c["alpha"],c["n_L2"],c["policy"],c["seed"])
        paired.setdefault(k,[]).append(r)
    for k,vals in paired.items():
        if len(vals)!=2 or len({x["trace_hash"] for x in vals})!=1 or len({x["l1_assignment_hash"] for x in vals})!=1:
            raise ValueError(f"calendar pairing failed for {k}")
        if len({(x["admitted"],x["TP"],x["FP"],x["FN"],x["TN"],x["S_plus_denominator"]) for x in vals})!=1:
            raise ValueError(f"confusion pairing failed for {k}")
        if any(x["max_deadline_admitted_h"]>CUTOFF for x in vals): raise ValueError(f"deadline beyond cutoff {k}")
    trace_groups={}
    for r in trace:
        trace_groups.setdefault((float(r["rho_L1"]),int(r["seed"])),[]).append(r)
    for k,vals in trace_groups.items():
        if len({r["exogenous_sha256"] for r in vals})!=1 or len({r["need_sha256"] for r in vals})!=1:
            raise ValueError(f"classifier exogenous/need pairing failed for {k}")
    upstream={}
    for r in rows:
        c=r["condition"]
        upstream.setdefault((c["rho_L1"],c["seed"],c["policy"]),[]).append(r)
    for k,vals in upstream.items():
        if len({r["l1_assignment_hash"] for r in vals})!=1:
            raise ValueError(f"L1 assignment changed across classifier/alpha/roster/calendar: {k}")
    summaries,calendar_contrasts,factor_contrasts=_summarize(
        rows,int(CONFIG["bootstrap"]["replicates"]),int(CONFIG["bootstrap"]["seed"]))
    out.mkdir(parents=True,exist_ok=True)
    exported=[]
    for r in sorted(rows,key=lambda x:tuple(x["condition"][k] for k in ("classifier_id","rho_L1","alpha","n_L2","policy","calendar","seed"))):
        exported.append({**r["condition"],**{k:v for k,v in r.items() if k!="condition"}})
    _write(out/"episodes.csv",exported)
    _write(out/"trace_audit.csv",trace)
    _write(out/"summary_by_condition.csv",summaries)
    _write(out/"paired_calendar_contrasts.csv",calendar_contrasts)
    _write(out/"paired_factor_contrasts.csv",factor_contrasts)
    checks={"status":"PASS","episode_rows":len(rows),"seed_blocks":len(seeds),
        "seed_range":[seeds[0],seeds[-1]],"trace_audit_rows":len(trace),
        "all_calendar_pair_checks":"PASS","all_deadlines_mature":True,
        "bootstrap_unit":"seed block","bootstrap_replicates":CONFIG["bootstrap"]["replicates"],
        "bootstrap_seed":CONFIG["bootstrap"]["seed"],"admission_h":CONFIG["admission_horizon_h"],
        "cutoff_h":CUTOFF,"terminal_drain_h":0,"shards":[str(x) for x in args.shards]}
    (out/"validation_checks.json").write_text(json.dumps(checks,indent=2)+"\n")
    (out/"execution_manifest.json").write_text(json.dumps({
        "config":CONFIG,"checks":checks,"synthetic_only":True,
        "regression_source_commit":"9772abae1bfcd2c810760e68ecd8fba107d320f0",
        "campaign_code_commit":"d088a7994104994f03ce919b070883fbc8e28859",
        "analysis_code":"merge_campaign_shards.py; seed-block bootstrap"
    },indent=2)+"\n")
    print(f"merged {len(rows)} condition-seed episodes across {len(seeds)} paired seed blocks")

if __name__=="__main__": main()
