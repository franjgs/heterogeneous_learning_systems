"""Run the joint classifier frontier extension and reuse only hash-matched episodes.

This script leaves the Phase 2 result files untouched. It reuses Phase 2 rows
only after regenerating target-prevalence traces and verifying their hashes.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/"src")]
from studies.soc_triage_classifier_operating_impact import run_phase2 as phase2  # noqa:E402
from studies.soc_triage_classifier_operating_impact.select_joint_frontier import read_csv  # noqa:E402
from studies.soc_triage_organization_coupling import run_pilot as frozen  # noqa:E402
from studies.soc_human_ai_organization.soc_parametric_baseline import PROJECTS  # noqa:E402

HERE=Path(__file__).resolve().parent
CONFIG=json.loads((HERE/"config"/"campaign.json").read_text())
INV=ROOT/"results"/"soc_triage_classifier_operating_impact_source_audit"/"classifier_inventory_72.csv"
OLD_EP=ROOT/CONFIG["reuse_audit"]["source_episode_csv"]
OUT=ROOT/"results"/"soc_triage_classifier_frontier_campaign"
POLICIES=tuple(CONFIG["simulation"]["policies"])
OLD_CFG=phase2.CONFIG

def write_csv(path,rows):
    if not rows: raise ValueError(f"refusing to write empty {path}")
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def old_points_by_source():
    return {p["id"]:p for p in phase2._points()}

def map_old_to_inventory(old_point,inventory):
    found=[p for p in inventory if p["label_definition"]==old_point["label_definition"]
      and p["cost_regime"]=="symmetric" and p["algorithm"]==old_point["algorithm"]
      and p["features"]==old_point["features"] and float(p["pD"])==float(old_point["pD"])
      and float(p["pFA"])==float(old_point["pFA"])]
    if len(found)!=1: raise AssertionError(f"old point does not map uniquely: {old_point['id']}")
    return found[0]

def prevalence(name,spec):
    pi=float(spec["pi"])
    return {"name":name,"label_definition":spec["label_definition"],"pi":pi,
      "need_by_class":tuple(pi for _ in PROJECTS),"definition":spec["definition"]}

def make_trace(pi_spec,rho,seed,point):
    return frozen._make_trace(rho_l1=float(rho),seed=int(seed),
      prevalence={"need_by_class":tuple(float(pi_spec["pi"]) for _ in PROJECTS)},point=point)[0]

def source_rows():
    with OLD_EP.open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    return rows

def audit_hash_reuse(old_rows,oldpoints,inventory,seed_values,rhos):
    old_original=CONFIG["reused_phase2_original_points"]
    old_standard=CONFIG["reused_phase2_standardized_points"] if "reused_phase2_standardized_points" in CONFIG else [
      "std_lr_ac","std_bayesian_mlp_ac","std_lightgbm_ac","std_lightgbm_c","std_rf_ac"]
    selected={"original":old_original,"standardized":old_standard}
    scen_map={"original":"original_test_exact_audited","standardized":"standardized_article_test_table2_inferred"}
    target_names={
      "original_audited_39_of_14449":"original_audited_39_of_14449",
      "original_pdf_ir_implied_40_of_14449":"original_pdf_ir_implied_40_of_14449",
      "standardized_pdf_ir_implied_19_of_14449":"standardized_pdf_ir_implied_19_of_14449"}
    trace_catalog={}; mismatch_cells={"original_audited_39_of_14449":set(),"original_pdf_ir_implied_40_of_14449":set(),
      "standardized_pdf_ir_implied_19_of_14449":set()}
    checks=[]
    for outname,raw in CONFIG["prevalence_scenarios"].items():
      if outname=="original_audited_39_of_14449": oldlabel="original"
      elif outname=="original_pdf_ir_implied_40_of_14449": oldlabel="original"
      else: oldlabel="standardized"
      if outname=="original_audited_39_of_14449" or outname=="original_pdf_ir_implied_40_of_14449":
        source_scenario=scen_map["original"]
      else: source_scenario=scen_map["standardized"]
      pi_spec={"pi":float(raw["pi"])}
      target_rows=[r for r in old_rows if r["prevalence_scenario"]==source_scenario]
      for seed in seed_values:
       for rho in rhos:
        for oldid in selected[oldlabel]:
         op=oldpoints[oldid]
         trace=make_trace(pi_spec,rho,seed,op)
         exog=frozen._trace_hash(trace,include_recommendation=False)
         full=frozen._trace_hash(trace,include_recommendation=True)
         key=(outname,int(seed),float(rho),oldid)
         trace_catalog[key]=(exog,full,trace)
         match=[r for r in target_rows if r["classifier_id"]==oldid and int(r["seed"])==int(seed)
           and float(r["rho_L1"])==float(rho)]
         if len(match)!=9: raise AssertionError(f"expected nine policy×roster rows for {key}, got {len(match)}")
         hashes={(r["exogenous_sha256"],r["trace_sha256"]) for r in match}
         if hashes!={(exog,full)}:
          mismatch_cells[outname].add((int(seed),float(rho)))
         else:
          for r in match:
           if abs(float(r["pi"])-float(OLD_CFG["prevalence_scenarios"][source_scenario]["pi"]))>1e-15:
            raise AssertionError("phase2 source row prevalence does not match its stored config")
         checks.append({"target_prevalence_scenario":outname,"source_prevalence_scenario":source_scenario,
           "label_definition":oldlabel,"seed":int(seed),"rho_L1":float(rho),"prior_classifier_id":oldid,
           "target_pi":float(raw["pi"]),"phase2_stored_pi":float(OLD_CFG["prevalence_scenarios"][source_scenario]["pi"]),
           "exogenous_sha256_target":exog,"trace_sha256_target":full,
           "source_rows_checked":len(match),"exact_full_trace_match":hashes=={(exog,full)}})
    # The directly audited count must match all 80 original scenario-seed traces;
    # article-implied original prevalence differs only at the recorded three cells.
    expected40={(int(x["seed"]),float(x["rho_l1"])) for x in CONFIG["reuse_audit"]["pdf_implied_40_mismatch_scenario_seed_cells"]}
    if mismatch_cells["original_audited_39_of_14449"]:
      raise AssertionError(f"39/14449 trace unexpectedly differs: {mismatch_cells['original_audited_39_of_14449']}")
    if mismatch_cells["original_pdf_ir_implied_40_of_14449"]!=expected40:
      raise AssertionError(f"40/14449 mismatch set changed: {mismatch_cells['original_pdf_ir_implied_40_of_14449']}")
    if mismatch_cells["standardized_pdf_ir_implied_19_of_14449"]:
      raise AssertionError("standardized prevalence traces unexpectedly differ")
    return trace_catalog,checks,mismatch_cells

def normalize_reused(row,invpoint,scenario,pi,*,source_scenario,note):
    out=dict(row)
    out.update({"label_definition":invpoint["label_definition"],"prevalence_scenario":scenario,"pi":float(pi),
      "classifier_id":invpoint["id"],"table":invpoint["source_table"],"pdf_page":invpoint["pdf_page"],
      "algorithm":invpoint["algorithm"],"features":invpoint["features"],"cost_regime":invpoint["cost_regime"],
      "pD_target":float(invpoint["pD"]),"pFA_target":float(invpoint["pFA"]),
      "BA_published":float(invpoint["BA_published"]),"BNB_published_or_identity":float(invpoint["BNB"]),
      "phase2_classifier_id":row["classifier_id"],"source_prevalence_scenario":source_scenario,
      "episode_provenance":"reused Phase 2 episode; exogenous and recommendation trace hashes verified at target pi",
      "reuse_note":note})
    return out

def simulate_point(point,prev,rho,seed,n_l2):
    simpoint={**point,"pD":float(point["pD"]),"pFA":float(point["pFA"]),
      "BA_published":float(point["BA_published"]),"table":int(point["source_table"])}
    trace=make_trace({"pi":prev["pi"]},rho,seed,simpoint)
    outputs=[]; switchrows=[]
    for policy in POLICIES:
      row,switches=phase2._run_one(trace,simpoint,prev,float(rho),int(n_l2),policy,int(seed))
      row.update({"cost_regime":point["cost_regime"],"BNB_published_or_identity":float(point["BNB"]),
        "pdf_page":int(point["pdf_page"]),"episode_provenance":"new simulation in joint frontier campaign",
        "phase2_classifier_id":""})
      outputs.append(row)
      for sw in switches:
        switchrows.append({**sw,"classifier_id":point["id"],"label_definition":point["label_definition"],
          "prevalence_scenario":prev["name"],"pi":prev["pi"],"rho_L1":rho,"n_L2":n_l2,"seed":seed,"policy":policy})
    return trace,outputs,switchrows

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    inventory=read_csv(INV)
    points={p["id"]:p for p in inventory}
    if len(points)!=72: raise AssertionError("expected the audited 72-point inventory")
    oldpoints=old_points_by_source(); oldrows=source_rows()
    sim=CONFIG["simulation"]; seeds=range(int(sim["seed_base"]),int(sim["seed_base"])+int(sim["n_seeds"]))
    rhos=tuple(float(x) for x in sim["rho_l1"]); l2s=tuple(int(x) for x in sim["l2_analyst_counts"])
    trace_catalog,hash_checks,mismatches=audit_hash_reuse(oldrows,oldpoints,inventory,seeds,rhos)
    write_csv(OUT/"phase2_reuse_trace_audit.csv",hash_checks)
    if not trace_catalog: raise AssertionError("empty trace audit")

    episodes=[]; reused=0; executed=0; rerun=0; switches=[]
    oldby={(r["prevalence_scenario"],r["classifier_id"],float(r["rho_L1"]),int(r["seed"]),r["policy"],int(r["n_L2"])):r for r in oldrows}
    # Reuse old runs where the target realization, operating point and simulation settings match.
    for target_name,spec in CONFIG["prevalence_scenarios"].items():
      label=spec["label_definition"]; pi=float(spec["pi"])
      source_scenario=("original_test_exact_audited" if label=="original" else "standardized_article_test_table2_inferred")
      for oldid in (CONFIG["reused_phase2_original_points"] if label=="original" else
        ["std_lr_ac","std_bayesian_mlp_ac","std_lightgbm_ac","std_lightgbm_c","std_rf_ac"]):
       op=oldpoints[oldid]; invpoint=map_old_to_inventory(op,inventory)
       for seed in seeds:
        for rho in rhos:
         exog,full,_=trace_catalog[(target_name,int(seed),float(rho),oldid)]
         # Target compatibility is determined by full trace hash, not the scenario label or pi field.
         compatible=any(c["seed"]==int(seed) and c["rho_L1"]==float(rho) and
            c["prior_classifier_id"]==oldid and c["target_prevalence_scenario"]==target_name and
            c["exact_full_trace_match"] for c in hash_checks)
         if not compatible: continue
         for n_l2 in l2s:
          for policy in POLICIES:
           raw=oldby[(source_scenario,oldid,float(rho),int(seed),policy,int(n_l2))]
           if raw["exogenous_sha256"]!=exog or raw["trace_sha256"]!=full:
            raise AssertionError("hash mismatch while reusing prior episode")
           episodes.append(normalize_reused(raw,invpoint,target_name,pi,source_scenario=source_scenario,
             note="regenerated target trace and recommendation hash match exactly"))
           reused+=1

    # Run exactly the eight missing joint-frontier points across their label-specific prevalence scenarios.
    new_ids=CONFIG["new_frontier_points"]
    new_points=[points[i] for i in new_ids]
    # The joint-frontier selection is recalculated from the audited inventory before execution.
    for label in ("original","standardized"):
      pool=[p for p in inventory if p["label_definition"]==label]
      front={p["id"] for p in pool if not any(float(q["pD"])>=float(p["pD"]) and float(q["pFA"])<=float(p["pFA"])
          and (float(q["pD"])>float(p["pD"]) or float(q["pFA"])<float(p["pFA"])) for q in pool if q["id"]!=p["id"])}
      included={p["id"] for p in pool if p["id"] in new_ids}
      already={map_old_to_inventory(oldpoints[oid],inventory)["id"] for oid in
        (CONFIG["reused_phase2_original_points"] if label=="original" else ["std_lr_ac","std_bayesian_mlp_ac","std_lightgbm_ac","std_lightgbm_c","std_rf_ac"])}
      missing=front-already
      if included!=missing:
        raise AssertionError(f"predeclared new points do not equal missing joint frontier for {label}: {included} != {missing}")

    progress_total=sum((2 if p["label_definition"]=="original" else 1) for p in new_points)*len(seeds)*len(rhos)*len(l2s)*len(POLICIES)
    for point in new_points:
      applicable=[(name,spec) for name,spec in CONFIG["prevalence_scenarios"].items() if spec["label_definition"]==point["label_definition"]]
      for prevname,spec in applicable:
       prev=prevalence(prevname,spec)
       for seed in seeds:
        for rho in rhos:
         for n_l2 in l2s:
          trace,rows,sw=simulate_point(point,prev,rho,seed,n_l2)
          exog=frozen._trace_hash(trace,include_recommendation=False)
          full=frozen._trace_hash(trace,include_recommendation=True)
          for row in rows:
           if row["exogenous_sha256"]!=exog or row["trace_sha256"]!=full:
            raise AssertionError("new simulated output trace hashes do not match the common input trace")
           row.update({"prevalence_scenario":prevname,"pi":prev["pi"],"classifier_id":point["id"],
             "label_definition":point["label_definition"],"algorithm":point["algorithm"],"features":point["features"],
             "cost_regime":point["cost_regime"],"pD_target":float(point["pD"]),"pFA_target":float(point["pFA"]),
             "pdf_page":int(point["pdf_page"])})
           episodes.append(row); executed+=1
          switches.extend(sw)
       print(f"completed new frontier point {point['id']} ({executed}/{progress_total} simulated policy episodes)",flush=True)

    # Correct only the prior original-label episode cells whose pi=40 trace hash differs.
    mismatch_cells=mismatches["original_pdf_ir_implied_40_of_14449"]
    rerun_points=[oldpoints[x] for x in CONFIG["reused_phase2_original_points"]]
    n_rerun_expected=len(mismatch_cells)*len(rerun_points)*len(l2s)*len(POLICIES)
    for seed,rho in sorted(mismatch_cells):
      prev=prevalence("original_pdf_ir_implied_40_of_14449",CONFIG["prevalence_scenarios"]["original_pdf_ir_implied_40_of_14449"])
      for op in rerun_points:
       invpoint=map_old_to_inventory(op,inventory)
       # Build once, then run all three existing L2 roster sizes and policies for this mismatched seed/load.
       simpoint={**invpoint,"pD":float(invpoint["pD"]),"pFA":float(invpoint["pFA"]),"BA_published":float(invpoint["BA_published"]),"table":int(invpoint["source_table"])}
       trace=make_trace({"pi":prev["pi"]},rho,seed,simpoint)
       for n_l2 in l2s:
        for policy in POLICIES:
         row,sw=phase2._run_one(trace,simpoint,prev,rho,n_l2,policy,seed)
         row.update({"classifier_id":invpoint["id"],"label_definition":"original","algorithm":invpoint["algorithm"],
           "features":invpoint["features"],"cost_regime":"symmetric","pD_target":float(invpoint["pD"]),
           "pFA_target":float(invpoint["pFA"]),"BNB_published_or_identity":float(invpoint["BNB"]),
           "pdf_page":int(invpoint["pdf_page"]),"episode_provenance":"targeted rerun: Phase 2 trace differs at PDF-implied prevalence",
           "phase2_classifier_id":op["id"]})
         episodes.append(row);rerun+=1
         for x in sw:switches.append({**x,"classifier_id":invpoint["id"],"label_definition":"original",
           "prevalence_scenario":prev["name"],"pi":prev["pi"],"rho_L1":rho,"n_L2":n_l2,"seed":seed,"policy":policy})
    if rerun!=n_rerun_expected: raise AssertionError(f"expected {n_rerun_expected} targeted repeats; got {rerun}")
    if executed!=progress_total: raise AssertionError(f"simulated {executed}, expected {progress_total}")

    # Add the targeted repeats to the targeted output without duplicating reusable rows for the same key.
    # Remove reused pi=40 rows for exactly the mismatched seed/load cells before append.
    filtered=[]
    for row in episodes:
      if row["prevalence_scenario"]=="original_pdf_ir_implied_40_of_14449" and row.get("episode_provenance","").startswith("reused") and (int(row["seed"]),float(row["rho_L1"])) in mismatch_cells:
       continue
      filtered.append(row)
    episodes=filtered
    write_csv(OUT/"episodes.csv",episodes)
    if switches: write_csv(OUT/"waps_switches.csv",switches)

    # Structural checks: all expected row keys, identical counts and exogenous traces by matched cell.
    by_cond={}
    for row in episodes:
      k=(row["prevalence_scenario"],row["label_definition"],float(row["rho_L1"]),int(row["seed"]),int(row["n_L2"]))
      by_cond.setdefault(k,[]).append(row)
    trace_fail=[]; denominator_fail=[]; confusion_fail=[]; deadline_fail=[]
    for k,rs in by_cond.items():
      ids={r["classifier_id"] for r in rs}
      expected_points=9 if k[1]=="original" else 8
      if len(rs)!=expected_points*len(POLICIES):
       denominator_fail.append((k,len(rs),expected_points*len(POLICIES)))
      exog={r["exogenous_sha256"] for r in rs}
      admitted={int(r["admitted"]) for r in rs}
      if len(exog)!=1: trace_fail.append((k,len(exog)))
      if len(admitted)!=1: denominator_fail.append((k,sorted(admitted)))
      for r in rs:
       if int(r["TP"])+int(r["FP"])+int(r["FN"])+int(r["TN"])!=int(r["admitted"]): confusion_fail.append(k)
       if int(r["TP_count"])+int(r["FN_count"])!=int(r["true_need_count"]): confusion_fail.append(k)
       if float(r["max_deadline_h"])>float(r["terminal_cutoff_h"]): deadline_fail.append(k)
    validation={"status":"PASS" if not (trace_fail or denominator_fail or confusion_fail or deadline_fail) else "FAIL",
      "inventory_rows":len(inventory),"joint_frontier_points":13,"new_frontier_points_simulated":len(new_ids),
      "reused_phase2_rows_before_targeted_repeat_filter":reused,"simulated_new_frontier_policy_episodes":executed,
      "targeted_policy_episode_repeats":rerun,"targeted_mismatch_seed_rho_cells":sorted([[s,r] for s,r in mismatch_cells]),
      "merged_episode_rows":len(episodes),"matched_condition_cells":len(by_cond),"trace_failures":trace_fail[:25],
      "denominator_failures":denominator_fail[:25],"confusion_failures":len(confusion_fail),"deadline_failures":deadline_fail[:25],
      "prevalence_note":"39/14449 directly audited and 40/14449 PDF-IR implied remain separate; original legacy Phase 2 pi is neither exact value",
      "policy_engine_note":"No motor or policy edits in this campaign; pre-existing worktree edits add unrelated NOMINAL-REF only and were not invoked",
      "no_reported_classifier":True}
    (OUT/"validation_checks.json").write_text(json.dumps(validation,indent=2)+"\n")
    manifest={"study_config":str((HERE/"config"/"campaign.json").relative_to(ROOT)),"phase2_source_csv":str(OLD_EP.relative_to(ROOT)),
      "inventory_csv":str(INV.relative_to(ROOT)),"generated_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "seed_base":sim["seed_base"],"n_seeds":sim["n_seeds"],"sha256":{}}
    for f in OUT.iterdir():
      if f.is_file() and f.name not in {"reproducibility_manifest.json"}: manifest["sha256"][f.name]=digest(f)
    (OUT/"reproducibility_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    if validation["status"]!="PASS": raise AssertionError("campaign output validations failed")
    print(json.dumps({"validation":validation,"reused":reused,"new_frontier":executed,"targeted_reruns":rerun,"merged":len(episodes)},indent=2),flush=True)

if __name__=="__main__":run()
