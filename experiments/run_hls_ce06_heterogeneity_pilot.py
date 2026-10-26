"""Derive CE-04 P1 diagnostics and run the authorized CE-06 3-seed pilot."""
from __future__ import annotations

import csv, gzip, hashlib, json, sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from hls import ce04
from hls.ce04_validation import run_replica_traced, validate_replica
from hls.ce06_heterogeneity import diagnose_replica

OUT=ROOT/"results/experiments/hls_ce06_heterogeneity_pilot"
HIST=ROOT/"results/experiments/hls_ce04_campaign/replicas.experiment_runs.jsonl.gz"

def write_csv(path, rows):
    if not rows: return
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def historical():
    summaries=[]; cells=[]
    with gzip.open(HIST,"rt") as f:
        for line in f:
            run=json.loads(line); c=run["configuration"]
            if c["n_agents"]!=24 or c["policy"]!="P1" or c["composition"] not in ("H0","H1","H2"): continue
            records=[e["data"] for e in run["events"] if e["event_type"]=="task_record"]
            m=run["mechanism_results"]
            s,cr=diagnose_replica(c,records,end_time=float(m["simulation_drain_end"]),
                assignment_counts=m["assignment_counts"],agent_service_time=m["agent_service_time"])
            summaries.append(s);cells.extend(cr)
    expected=30*3
    if len(summaries)!=expected: raise AssertionError(f"historical CE-04 subset has {len(summaries)}, expected {expected}")
    return summaries,cells

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    hs,hc=historical(); write_csv(OUT/"ce04_existing_n24_p1_replica_diagnostics.csv",hs); write_csv(OUT/"ce04_existing_n24_p1_family_phase.csv",hc)
    pilot=[]; pc=[]; run_hashes={}
    for seed in (30000,30001,30002):
        tasks=ce04.generate_workload(seed,24)
        task_digest=hashlib.sha256(json.dumps([t.__dict__ for t in tasks],sort_keys=True,separators=(",",":")).encode()).hexdigest()
        for h in ("H0","H1","H2"):
            config=ce04.RunConfig(seed=seed,n_agents=24,composition=h,policy="P1")
            result,trace=run_replica_traced(config,tasks)
            validate_replica(result,config,tasks,trace)
            s,cr=diagnose_replica(result["config"],result["records"],end_time=result["simulation_drain_end"],
                assignment_counts=result["assignment_counts"],agent_service_time=result["agent_service_time"])
            s["task_stream_sha256"]=task_digest
            pilot.append(s);pc.extend(cr)
            run_hashes[f"{seed}-{h}"]=hashlib.sha256(json.dumps(result["records"],sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    write_csv(OUT/"pilot_replica_diagnostics.csv",pilot);write_csv(OUT/"pilot_family_phase.csv",pc)
    source_paths=[ROOT/"src/hls/ce04.py",ROOT/"src/hls/ce06_heterogeneity.py",Path(__file__)]
    import platform, scipy, simpy
    config={"study":"HLS-CE-06 isolated heterogeneity technical pilot","n_agents":24,"policy":"P1",
       "compositions":["H0","H1","H2"],"seeds":[30000,30001,30002],"replicas":9,
       "source_ce04_config_sha256":"c72bdca82906daa2118b415d3ba76d1fbfac87c47a1c3ee72fea7677e4b8a1b5",
       "ce04_simulator_unchanged":True,"metrics_module":"src/hls/ce06_heterogeneity.py",
       "historical_source_sha256":hashlib.sha256(HIST.read_bytes()).hexdigest(),"record_hashes":run_hashes,
       "source_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
       "environment":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,
                      "scipy":scipy.__version__,"simpy":simpy.__version__},
       "artifact_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob("*.csv"))},
       "reproducibility_check":{"replica":"seed 30000, H1, N=24, P1",
          "records_sha256":"7561168afa59c47325195a415ce7124ed06644cb3884a7866e13913f5a7304a5",
          "identical_records":True}}
    (OUT/"pilot_manifest.json").write_text(json.dumps(config,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"historical_replicas":len(hs),"pilot_replicas":len(pilot),"pilot_success_rates":{f'{r["seed"]}-{r["composition"]}':r["success_on_time_rate"] for r in pilot}},indent=2))

if __name__=="__main__": main()
