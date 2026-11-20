"""Select the joint symmetric/asymmetric Pareto frontiers; no simulation."""
from __future__ import annotations
import csv, json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/"src")]
from studies.soc_triage_classifier_operating_impact.run_phase2 import _service_means  # noqa:E402
from studies.soc_triage_organization_coupling import run_pilot  # noqa:E402
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa:E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa:E402
 BASE_ELIGIBILITY,BASE_L1_ANALYSTS,PROJECTS,PROJECT_MIX,build_roster)

BASE=Path(__file__).resolve().parent
OUT=ROOT/"results"/"soc_triage_classifier_operating_impact_source_audit"
INVENTORY=OUT/"classifier_inventory_72.csv"
CONFIG=json.loads((BASE/"config"/"phase2.json").read_text())

def read_csv(p):
 with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def write_csv(p,rows):
 with p.open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 points=read_csv(INVENTORY)
 old=json.loads((BASE/"config"/"classifier_points.json").read_text())["points"]
 selected={k:set(v) for k,v in CONFIG["simulation_selection"].items()}
 old_by_id={p["id"]:p for p in old}
 roster={}
 for n in (3,):
  l1,l2,l1s,l2s=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=n,mean_eligible_projects=BASE_ELIGIBILITY)
  roster[n]=(l1,l2,l1s,l2s,effective_capacity(l1,l1s,PROJECT_MIX)["max_common_arrivals_per_h"],
             effective_capacity(l2,l2s,PROJECT_MIX)["max_common_arrivals_per_h"],_service_means(l2,l2s))
 out=[]
 for label in ("original","standardized"):
  pool=[p for p in points if p["label_definition"]==label]
  for p in pool:
   dominated=any(float(o["pD"])>=float(p["pD"]) and float(o["pFA"])<=float(p["pFA"]) and
     (float(o["pD"])>float(p["pD"]) or float(o["pFA"])<float(p["pFA"])) for o in pool if o["id"]!=p["id"])
   if dominated:continue
   legacy_pi=float(CONFIG["prevalence_scenarios"]["original_test_exact_audited"]["pi"]) if label=="original" else float(CONFIG["prevalence_scenarios"]["standardized_article_test_table2_inferred"]["pi"])
   pdf_pi=40/14449 if label=="original" else 19/14449
   oldmatch=next((q for q in old if q["label_definition"]==label and q["algorithm"]==p["algorithm"] and q["features"]==p["features"] and float(q["pD"])==float(p["pD"]) and float(q["pFA"])==float(p["pFA"])),None)
   was_simulated=bool(oldmatch and oldmatch["id"] in selected[label])
   cap=roster[3]
   row={k:p[k] for k in ("id","algorithm","features","label_definition","cost_regime","pD","pFA","BA_published","BNB","source_table","pdf_page")}
   rerun=bool(was_simulated and abs(legacy_pi-pdf_pi)>1e-12)
   row.update({"joint_frontier":"true","legacy_phase2_pi_for_direct_pairing":legacy_pi,
      "pdf_table1_test_pi_implied":pdf_pi,"prior_operating_point_id":oldmatch["id"] if oldmatch else "",
      "prior_phase2_simulated":str(was_simulated).lower(),"prior_pi_matches_pdf_primary":str(was_simulated and not rerun).lower(),
      "new_simulation_required_for_pdf_primary":"true" if (not was_simulated or rerun) else "false",
      "reason_for_new_episode":"missing operating point" if not was_simulated else ("original prior pi differs from PDF-implied primary pi" if rerun else "reusable matched prevalence and seed configuration"),
      "analytical_capacity_roster":"6 L1 / 3 L2","mu_L1_per_h":cap[4],"mu_L2_per_h":cap[5]})
   for pname,pi in (("legacy_pairing",legacy_pi),("pdf_table1",pdf_pi)):
    q,mix=run_pilot._expected_route_mix(tuple(pi for _ in PROJECTS),float(p["pD"]),float(p["pFA"]))
    service=_service_means(cap[1],cap[3])
    q_pdf=q
    row[pname+"_prevalence"]=pi
    row[pname+"_recommendations_per_1000"]=1000*q
    row[pname+"_L2_jobs_per_h_at_rho085"]=cap[4]*.85*q
    row[pname+"_L2_jobs_per_h_at_rho125"]=cap[4]*1.25*q
    row[pname+"_offered_rho_L2_at_rho085_nL2_3"]=cap[4]*.85*q/cap[5]
    row[pname+"_offered_rho_L2_at_rho125_nL2_3"]=cap[4]*1.25*q/cap[5]
   row["next_campaign_seed_cohort_use"]=("reuse matched phase2 episodes" if was_simulated and not rerun else "use seed IDs 272600000-272600039 on a harmonized PDF-prevalence trace cohort; keyed common recommendation uniforms")
   out.append(row)
 out.sort(key=lambda r:(r["label_definition"],r["cost_regime"],float(r["pFA"])))
 write_csv(OUT/"joint_pareto_frontier_13.csv",out)
 print("joint_frontier",len(out),"previously_simulated_frontier",sum(r["prior_phase2_simulated"]=="true" for r in out),"new_or_harmonized_runs_at_pdf_prevalence",sum(r["new_simulation_required_for_pdf_primary"]=="true" for r in out))
 for r in out:print(r["label_definition"],r["id"],"old_sim",r["prior_phase2_simulated"],"run_pdf",r["new_simulation_required_for_pdf_primary"],"q",round(float(r["pdf_table1_recommendations_per_1000"]),2),"L2/h",round(float(r["pdf_table1_L2_jobs_per_h_at_rho085"]),3),round(float(r["pdf_table1_L2_jobs_per_h_at_rho125"]),3))
if __name__=="__main__":main()
