"""Run exactly the six authorized CE-07 technical-pilot simulations."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import simpy

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from hls import ce04
from hls.ce07_pilot import (agent_permutation, canonical_sha256,
    matched_potential_digest, run_ce07_replica)
from hls.ce07_structure import competence_matrices, rename_agent_rows, validate_structures

OUT=ROOT/"results/experiments/hls_ce07_technical_pilot"
SEEDS=(30010,30011,30012)

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def task_digest(tasks) -> str:
    return canonical_sha256([t.__dict__ for t in tasks])

def main():
    if len(SEEDS)!=3 or len(set(SEEDS))!=3:
        raise AssertionError("pilot requires exactly three unique seeds")
    base_a,base_b=competence_matrices()
    structural_validation=validate_structures(base_a,base_b)
    summaries=[]; all_ties=[]; pair_audits=[]
    observed_seed_streams=[]
    for seed in SEEDS:
        permutation=agent_permutation(seed,12)
        q_a=rename_agent_rows(base_a,permutation)
        q_b=rename_agent_rows(base_b,permutation)
        task_tuple=ce04.generate_workload(seed,12,horizon=400.0)
        d_hash=task_digest(task_tuple)
        potential_hash=matched_potential_digest(seed,task_tuple,q_a,q_b)
        observed_seed_streams.append((d_hash,potential_hash))
        outputs={}
        for org,q in (("A",q_a),("B",q_b)):
            result,audit,used_permutation=run_ce07_replica(seed,org,task_tuple)
            if tuple(used_permutation)!=tuple(permutation):
                raise AssertionError("A/B did not use the same physical-agent permutation")
            if result["n_arrivals"]!=len(task_tuple):
                raise AssertionError("replica arrivals differ from matched demand")
            if result["config"]["n_agents"]!=12 or result["config"]["policy"]!="P1":
                raise AssertionError("replica configuration changed from CE-07 protocol")
            records=result["records"]
            admitted=[r for r in records if r["selected_agent"] is not None]
            selected_q=[float(q[int(r["selected_agent"]),int(r["family"])]) for r in admitted]
            waits=[float(r["service_start"]-r["arrival"]) for r in admitted]
            mean_util=float(np.mean(result["agent_utilization"]))
            summary={"seed":seed,"organization":org,"n_agents":12,"n_functions":4,
                "policy":"P1","arrivals":result["n_arrivals"],"admitted":result["n_admitted"],
                "rejected":result["n_rejected"],"success_on_time":result["n_success_on_time"],
                "success_on_time_rate":result["success_on_time_rate"],
                "selected_competence_mean":float(np.mean(selected_q)) if selected_q else None,
                "selected_competence_median":float(np.median(selected_q)) if selected_q else None,
                "wait_mean":float(np.mean(waits)) if waits else None,
                "wait_p95":float(np.quantile(waits,.95)) if waits else None,
                "late_admitted":result["n_late"],"utilization_mean":mean_util,
                "utilization_p95":float(np.quantile(result["agent_utilization"],.95)),
                "utilization_max":float(np.max(result["agent_utilization"])),
                "exact_tie_decisions":audit["validation"]["exact_tie_calls"],
                "tie_decision_calls":audit["validation"]["p1_tie_calls"],
                "demand_sha256":d_hash,"matched_potential_sha256":potential_hash,
                "record_sha256":canonical_sha256(records),
                "permutation_new_slot_to_profile_id":list(permutation),
                "permutation_seed_sequence":[seed,12,707]}
            summaries.append(summary)
            admitted_iter=iter(admitted)
            for tie in audit["tie_events"]:
                rec=next(admitted_iter)
                if len(tie["exact_tie_candidates"])>1:
                    all_ties.append({"seed":seed,"organization":org,
                        "task_id":rec["task_id"],"family":rec["family"],
                        "candidate_slots":tie["exact_tie_candidates"],
                        "candidate_profile_ids":[permutation[i] for i in tie["exact_tie_candidates"]],
                        "selected_slot":tie["selected_agent_slot"],
                        "selected_profile_id":permutation[tie["selected_agent_slot"]],
                        "selected_priority_rank":tie["selected_priority_rank"],
                        "best_score":tie["best_score"]})
            outputs[org]=result
        ra,rb=outputs["A"],outputs["B"]
        task_rows=lambda r:[(x["task_id"],x["arrival"],x["family"],x["deadline"]) for x in r["records"]]
        if task_rows(ra)!=task_rows(rb): raise AssertionError("A/B demand pair differs")
        pair_audits.append({"seed":seed,"same_permutation":True,"same_demand":True,
            "same_service_and_common_correctness_potential_table":True,
            "demand_sha256":d_hash,"matched_potential_sha256":potential_hash,
            "A_minus_B_success_rate":ra["success_on_time_rate"]-rb["success_on_time_rate"],
            "A_B_admitted_counts":[ra["n_admitted"],rb["n_admitted"]],
            "A_B_arrivals":[ra["n_arrivals"],rb["n_arrivals"]]})
    if len(summaries)!=6: raise AssertionError("pilot must contain exactly six simulations")
    if len(set(SEEDS))!=len(observed_seed_streams): raise AssertionError("seed contamination")
    common_config={"N":12,"K":4,"h":0.9,"l":0.6,"marginal_exact":"27/40",
        "horizon":400,"arrival_rate_per_agent":0.55,"task_families":"four equiprobable stationary",
        "service":{"distribution":"CE-04 lognormal","mean":1.25,"CV":0.30},
        "deadline_slack":3.0,"queue":"one FCFS queue and one active service per agent",
        "policy":"unchanged CE-04 P1; q_ik * F_i","learning":False,"cooperation":False,
        "organizations":["A","B"],"seeds":list(SEEDS),"simulations":6,
        "agent_permutation_stream":[12,707],"same_permutation_A_B_per_seed":True}
    config_sha=canonical_sha256(common_config)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"configuration.json").write_text(json.dumps({**common_config,"scientific_config_sha256":config_sha},indent=2,sort_keys=True)+"\n")
    (OUT/"replica_results.json").write_text(json.dumps(summaries,indent=2,sort_keys=True,allow_nan=False)+"\n")
    (OUT/"paired_validation.json").write_text(json.dumps({"structure_validation":structural_validation,
        "pairs":pair_audits,"all_six_validated":True,"simulations":6},indent=2,sort_keys=True)+"\n")
    (OUT/"exact_tie_decisions.json").write_text(json.dumps(all_ties,indent=2,sort_keys=True,allow_nan=False)+"\n")
    sources=["src/hls/ce04.py","src/hls/ce04_validation.py","src/hls/ce07_structure.py",
             "src/hls/ce07_pilot.py","experiments/run_hls_ce07_technical_pilot.py"]
    manifest={"study":"HLS-CE-07.3 technical pilot","base_commit":"b6e17cdab4d2a41e7e93c63e4eb8f566d90a8801",
        "execution_commit":__import__("subprocess").check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "configuration_sha256":config_sha,"source_sha256":{x:sha_bytes((ROOT/x).read_bytes()) for x in sources},
        "environment":{"python":sys.version,"platform":platform.platform(),"numpy":np.__version__,
            "scipy":scipy.__version__,"simpy":simpy.__version__},
        "permutations_by_seed":{str(x["seed"]):x["permutation_new_slot_to_profile_id"] for x in summaries if x["organization"]=="A"},
        "artifact_sha256":{p.name:sha_bytes(p.read_bytes()) for p in sorted(OUT.glob("*.json"))},
        "status":"6/6 simulations validated; descriptive technical pilot only"}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"simulations":len(summaries),"configuration_sha256":config_sha,
        "results":[{"seed":x["seed"],"organization":x["organization"],"success":x["success_on_time_rate"],
                    "exact_ties":x["exact_tie_decisions"],"wait":x["wait_mean"]} for x in summaries]},indent=2))

if __name__=="__main__": main()
