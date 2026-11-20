"""Rebuild the SOCTRA escalation inventory from the supplied journal PDF.

This is a transcription/audit script only. It does not run simulations.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from studies.soc_triage_classifier_operating_impact.run_phase2 import _service_means  # noqa: E402
from studies.soc_triage_organization_coupling import run_pilot  # noqa: E402
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity  # noqa: E402
from studies.soc_human_ai_organization.soc_parametric_baseline import (  # noqa: E402
    BASE_ELIGIBILITY, BASE_L1_ANALYSTS, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
    PROJECTS, PROJECT_MIX, build_roster,
)

HERE = Path(__file__).resolve().parent
PDF = Path.home() / "Downloads" / "SOCTRA_JournalArticle_2026.pdf"
OLD = json.loads((HERE / "config" / "classifier_points.json").read_text())
OUT = ROOT / "results" / "soc_triage_classifier_operating_impact_source_audit"

# Table 5 (PDF p. 39): each tuple is BA, pFA, pD; original then standardized.
SYMMETRIC = {
    "A": {
        "LR": ((.7424,.3402,.8250),(.8380,.0082,.6842)),
        "RF": ((.7393,.2714,.7500),(.8595,.1231,.8421)),
        "XGBoost": ((.6785,.2430,.6000),(.8359,.0124,.6842)),
        "LightGBM": ((.6992,.3516,.7500),(.8643,.0608,.7895)),
        "Bayesian MLP": ((.7849,.2301,.8000),(.8332,.0177,.6842)),
        "LSEnsemble": ((.7581,.2839,.8000),(.8751,.0919,.8421)),
    },
    "C": {
        "LR": ((.7257,.2486,.7000),(.7300,.3294,.7895)),
        "RF": ((.7257,.2486,.7000),(.7438,.3545,.8421)),
        "XGBoost": ((.7257,.2486,.7000),(.7500,.3421,.8421)),
        "LightGBM": ((.7234,.2531,.7000),(.7448,.4051,.8947)),
        "Bayesian MLP": ((.7257,.2486,.7000),(.7314,.3793,.8421)),
        "LSEnsemble": ((.7378,.2743,.7500),(.7509,.3404,.8421)),
    },
    "A+C": {
        "LR": ((.7975,.2050,.8000),(.8381,.0081,.6842)),
        "RF": ((.7941,.1618,.7500),(.8465,.1491,.8421)),
        "XGBoost": ((.7588,.2074,.7250),(.8353,.0136,.6842)),
        "LightGBM": ((.7918,.1664,.7500),(.8986,.0450,.8421)),
        "Bayesian MLP": ((.8222,.2056,.8500),(.8444,.0154,.7042)),
        "LSEnsemble": ((.7995,.1510,.7500),(.8839,.0743,.8421)),
    },
}

# Table 7 (PDF p. 41): each tuple is published BNB, BA, pFA, pD;
# original then standardized. BNB is transcribed, never reconstructed.
ASYMMETRIC = {
    "A": {
        "LR": ((.8201,.6902,.5696,.9500),(.8808,.7615,.4770,1.0000)),
        "RF": ((.7942,.6635,.5980,.9250),(.8656,.8365,.2218,.8947)),
        "XGBoost": ((.7807,.5864,.8023,.9750),(.8783,.8092,.3290,.9474)),
        "LightGBM": ((.7892,.6533,.6184,.9250),(.8449,.7424,.4626,.9474)),
        "Bayesian MLP": ((.8020,.6539,.6422,.9500),(.7595,.8347,.0148,.6842)),
        "LSEnsemble": ((.7633,.5267,.9466,1.0000),(.9063,.8477,.2695,.9649)),
    },
    "C": {
        "LR": ((.8112,.6975,.5301,.9250),(.8234,.6468,.7064,1.0000)),
        "RF": ((.7924,.6097,.7556,.9750),(.7988,.5976,.8047,1.0000)),
        "XGBoost": ((.7974,.5947,.8105,1.0000),(.8297,.6593,.6814,1.0000)),
        "LightGBM": ((.8306,.6862,.6025,.9750),(.8819,.7639,.4723,1.0000)),
        "Bayesian MLP": ((.8077,.6154,.7692,1.0000),(.7581,.5162,.9676,1.0000)),
        "LSEnsemble": ((.8050,.6100,.7800,1.0000),(.8033,.6065,.7870,1.0000)),
    },
    "A+C": {
        "LR": ((.8297,.7344,.4562,.9250),(.7850,.7804,.2286,.7895)),
        "RF": ((.8305,.7111,.5279,.9500),(.9121,.8768,.1938,.9474)),
        "XGBoost": ((.8236,.6972,.5557,.9500),(.8741,.8007,.3459,.9474)),
        "LightGBM": ((.8183,.6616,.6519,.9750),(.9162,.8324,.3351,1.0000)),
        "Bayesian MLP": ((.8530,.7809,.3632,.9250),(.7648,.7928,.1512,.7368)),
        "LSEnsemble": ((.8281,.7063,.5374,.9500),(.8972,.8294,.3060,.9649)),
    },
}

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        w.writeheader(); w.writerows(rows)

def build_inventory() -> list[dict]:
    rows=[]
    for costs, data, table, page in (("symmetric",SYMMETRIC,5,39),("asymmetric_cM3cFA",ASYMMETRIC,7,41)):
        for feat, models in data.items():
            for alg, labelvals in models.items():
                for label, vals in zip(("original","standardized"),labelvals):
                    if costs == "symmetric":
                        ba,pfa,pd=vals; bnb=ba; bnb_source="BA; equals normalized Bayes benefit under equal costs, per article definition"
                    else:
                        bnb,ba,pfa,pd=vals; bnb_source="published Table 7 value"
                    calc=(pd+1-pfa)/2
                    if abs(calc-ba) > .00011:
                        raise AssertionError((costs,feat,alg,label,calc,ba))
                    rows.append({"id":f"{label}_{alg.lower().replace(' ','_')}_{feat.lower().replace('+','p')}_{costs}",
                        "algorithm":alg,"features":feat,"label_definition":label,"cost_regime":costs,
                        "pD":f"{pd:.4f}","pFA":f"{pfa:.4f}","BA_published":f"{ba:.4f}",
                        "BNB":f"{bnb:.4f}","BNB_provenance":bnb_source,"source_table":table,
                        "pdf_page":page,"source_pdf":"~/Downloads/SOCTRA_JournalArticle_2026.pdf"})
    assert len(rows)==72 and len({r['id'] for r in rows})==72
    return rows

def dominance(p, pool):
    return any(float(o['pD'])>=float(p['pD']) and float(o['pFA'])<=float(p['pFA']) and
               (float(o['pD'])>float(p['pD']) or float(o['pFA'])<float(p['pFA'])) for o in pool if o['id']!=p['id'])

def main():
    rows=build_inventory()
    pdf_hash=hashlib.sha256(PDF.read_bytes()).hexdigest()
    (OUT).mkdir(parents=True,exist_ok=True)
    write_csv(OUT/'classifier_inventory_72.csv',rows)
    pareto=[]
    for label in ('original','standardized'):
      for cost in ('symmetric','asymmetric_cM3cFA'):
        pool=[p for p in rows if p['label_definition']==label and p['cost_regime']==cost]
        for p in pool:
          peers=[x for x in pool if x['pD']==p['pD'] and x['pFA']==p['pFA']]
          pareto.append({**p,"dominated":dominance(p,pool),"equivalent_count":len(peers),
             "frontier_group":f"{label}|{cost}","rule":"maximize pD, minimize pFA; compare only within label and cost regime"})
    write_csv(OUT/'statistical_pareto_72.csv',pareto)

    # Exact test prevalences from published Table 1 are counts implied by its N and IR;
    # keep the independently audited original 39-count and full historical sensitivity.
    prevalences={
      "original_pdf_test_implied_40_of_14449":("original",40/14449,"PDF Table 1 test IR 360.23; integer count implied for N=14449"),
      "original_audited_test_39_of_14449":("original",39/14449,"prior SOCTRA data audit; conflicts with PDF Table 1 rounded IR implication"),
      "original_historical_210_of_63410":("original",210/63410,"prior audit full historical population; sensitivity only"),
      "standardized_pdf_test_implied_19_of_14449":("standardized",19/14449,"PDF Table 1 test IR 759.47; integer count implied for N=14449"),
    }
    l1,l2base,l1s,l2sbase=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=3,mean_eligible_projects=BASE_ELIGIBILITY)
    mu_l1=effective_capacity(l1,l1s,PROJECT_MIX)["max_common_arrivals_per_h"]
    load=[]
    for pname,(label,pi,pidef) in prevalences.items():
      for n_l2 in (2,3,4):
        l1,l2,l1s,l2s=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=n_l2,mean_eligible_projects=BASE_ELIGIBILITY)
        service=_service_means(l2,l2s)
        for p in rows:
          if p['label_definition']!=label: continue
          pd,pfa=float(p['pD']),float(p['pFA'])
          need=tuple(pi for _ in PROJECTS)
          q,mix=run_pilot._expected_route_mix(need,pd,pfa)
          mu_l2=effective_capacity(l2,l2s,mix)["max_common_arrivals_per_h"]
          mean_service=sum(w*service[k] for w,k in zip(mix,PROJECTS))
          for rho in (.85,1.25):
            lam=mu_l1*rho
            tp=pi*pd; fp=(1-pi)*pfa; fn=pi*(1-pd); tn=(1-pi)*(1-pfa)
            load.append({"classifier_id":p['id'],"label_definition":label,"cost_regime":p['cost_regime'],
              "prevalence_scenario":pname,"pi":pi,"prevalence_definition":pidef,"rho_L1":rho,
              "n_L1":6,"n_L2":n_l2,"mu_L1_per_h":mu_l1,"lambda_L1_per_h":lam,"mu_L2_mix_specific_per_h":mu_l2,
              "pD":pd,"pFA":pfa,"BA":p['BA_published'],"BNB":p['BNB'],
              "q_recommendation_fraction":q,"recommendations_per_1000":1000*q,
              "TP_per_1000":1000*tp,"FP_per_1000":1000*fp,"FN_per_1000":1000*fn,"TN_per_1000":1000*tn,
              "L2_offered_recommendations_per_h":lam*q,"rho_L2_offered":lam*q/mu_l2,
              "mean_L2_service_h_per_routed_task":mean_service,
              "L2_recommended_work_h_per_input_hour":lam*q*mean_service,
              "L2_necessary_TP_work_h_per_input_hour":lam*tp*mean_service,
              "L2_unnecessary_FP_work_h_per_input_hour":lam*fp*mean_service,
              "L2_necessary_FN_work_omitted_h_per_input_hour":lam*fn*mean_service,
              "interpretation":"fluid offered-load calculation under automatic acceptance and class-exchangeable errors; not simulated utilization/SLA"})
    write_csv(OUT/'analytic_load_72.csv',load)

    old=OLD['points']; overlap=[]
    by_key={(p['label_definition'],p['algorithm'],p['features']):p for p in rows if p['cost_regime']=='symmetric'}
    for op in old:
      key=(op['label_definition'],op['algorithm'],op['features'])
      match=by_key.get(key)
      exact=match is not None and float(match['pD'])==float(op['pD']) and float(match['pFA'])==float(op['pFA']) and float(match['BA_published'])==float(op['BA_published'])
      overlap.append({"prior_id":op['id'],"prior_source_table":op['table'],"label_definition":op['label_definition'],
        "features":op['features'],"algorithm":op['algorithm'],"pD":op['pD'],"pFA":op['pFA'],
        "matches_pdf_symmetric_operating_point":exact,
        "match_id":match['id'] if exact else ""})
    write_csv(OUT/'prior_25_crosswalk.csv',overlap)
    metadata={"n_inventory":len(rows),"pdf_sha256":pdf_hash,"pdf_bytes":PDF.stat().st_size,
      "pdf_primary_source":"local supplied PDF; Table 5 p.39 and Table 7 p.41; no web sources used to fill values",
      "latex_crosscheck":"~/Downloads/Alert_Triage_No_Authors.tex; supporting consistency check only",
      "n_old_points_matching_symmetric_operating_point":sum(x['matches_pdf_symmetric_operating_point'] for x in overlap),
      "n_old_points":len(overlap),"simulations_run":False,
      "capacity_method":"existing phase2 analytical method: frozen roster, fractional-flow effective_capacity, composition derived from homogeneous prevalence; no policy/simulator execution"}
    (OUT/'audit_metadata.json').write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))
    for grp in sorted({x['frontier_group'] for x in pareto}):
      front=[x for x in pareto if x['frontier_group']==grp and not x['dominated']]
      print(grp, len(front), '; '.join(f"{x['id']} pD={x['pD']} pFA={x['pFA']} eq={x['equivalent_count']}" for x in front))
    print('analytic rows',len(load),'old point exact matches',sum(x['matches_pdf_symmetric_operating_point'] for x in overlap))

if __name__=='__main__': main()
