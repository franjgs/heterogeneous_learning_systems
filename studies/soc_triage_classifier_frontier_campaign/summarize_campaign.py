"""Summarize paired joint-frontier campaign; no simulation is performed here."""
from __future__ import annotations
import csv, hashlib, itertools, json, math, statistics, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import os

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/"results"/"soc_triage_classifier_frontier_campaign"
REPORT=HERE/"SOCTRA_TRIAGE_CLASSIFIER_FRONTIER_CAMPAIGN.md"
os.environ.setdefault("MPLCONFIGDIR","/tmp/soc_triage_frontier_mplcache")
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import t as student_t

def read_csv(name):
 with (OUT/name).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def write_csv(name,rows):
 if not rows:return
 with (OUT/name).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator="\n");w.writeheader();w.writerows(rows)
def f(r,k):return float(r[k])
def mean_ci(xs):
 n=len(xs); m=statistics.mean(xs) if n else float("nan"); sd=statistics.stdev(xs) if n>1 else 0.0
 h=float(student_t.ppf(.975,n-1))*sd/math.sqrt(n) if n>1 else float("nan")
 return m,sd,(m-h if n>1 else float("nan")),(m+h if n>1 else float("nan"))
def paired(xs,ys):return [a-b for a,b in zip(xs,ys)]
def metric_value(r,key):
 if key=="unnecessary_FP_service_h_per_1000":return 1000*f(r,"L2_work_unnecessary_FP_nominal_h")/int(r["admitted"])
 if key=="FP_recommendations_per_1000":return 1000*int(r["FP_recommended_count"])/int(r["admitted"])
 if key=="FN_omissions_per_1000":return 1000*int(r["FN_count"])/int(r["admitted"])
 return f(r,key)
def ci_record(values,base):
 m,sd,lo,hi=mean_ci(values);return {**base,"n_seed":len(values),"mean":m,"sd":sd,"ci95_low":lo,"ci95_high":hi}
def is_dom(a,b):
 # objectives: detection, timely correctness, necessary SLA, reverse FP hours and terminal L2 backlog
 av=(a["necessary_L2_detection_fraction_mean"],a["correct_on_time_expected_per_admitted_mean"],
     a["necessary_L2_timely_per_need_mean"],-a["unnecessary_FP_service_h_per_1000_mean"],-a["backlog_L2_terminal_mean"])
 bv=(b["necessary_L2_detection_fraction_mean"],b["correct_on_time_expected_per_admitted_mean"],
     b["necessary_L2_timely_per_need_mean"],-b["unnecessary_FP_service_h_per_1000_mean"],-b["backlog_L2_terminal_mean"])
 return all(x>=y-1e-12 for x,y in zip(av,bv)) and any(x>y+1e-12 for x,y in zip(av,bv))

def main():
 rows=read_csv("episodes.csv")
 index=defaultdict(list)
 for r in rows:
  k=(r["label_definition"],r["prevalence_scenario"],r["classifier_id"],r["cost_regime"],float(r["rho_L1"]),int(r["n_L2"]),r["policy"])
  index[k].append(r)
 fields={
  "correct_on_time_expected_per_admitted":"correct_on_time_expected_per_admitted",
  "required_resolution_SLA_terminal":"required_resolution_SLA_terminal",
  "routed_SLA_terminal":"routed_SLA_terminal",
  "necessary_L2_detection_fraction":"necessary_L2_detection_fraction",
  "necessary_L2_timely_per_need":"necessary_L2_timely_per_need",
  "legacy_RN":"legacy_RN",
  "unnecessary_FP_service_h_per_1000":"unnecessary_FP_service_h_per_1000",
  "FP_recommendations_per_1000":"FP_recommendations_per_1000",
  "FN_omissions_per_1000":"FN_omissions_per_1000",
  "backlog_L2_terminal":"backlog_L2_terminal",
  "utilization_L2_mean_H":"utilization_L2_mean_H",
  "backlog_L1_terminal":"backlog_L1_terminal",
  "P1_fraction_of_WAPS_dispatches_L2":"P1_fraction_of_WAPS_dispatches_L2",
}
 summary=[]
 for k,rs in index.items():
  rs=sorted(rs,key=lambda r:int(r["seed"]))
  base={"label_definition":k[0],"prevalence_scenario":k[1],"classifier_id":k[2],"cost_regime":k[3],
    "rho_L1":k[4],"n_L2":k[5],"policy":k[6],"algorithm":rs[0]["algorithm"],"features":rs[0]["features"],
    "pD_target":rs[0]["pD_target"],"pFA_target":rs[0]["pFA_target"],"BA_published":rs[0]["BA_published"],
    "BNB_published_or_identity":rs[0]["BNB_published_or_identity"],"pi":rs[0]["pi"],"n_episodes":len(rs),
    "mean_admitted":statistics.mean(int(r["admitted"]) for r in rs),"mean_true_need_count":statistics.mean(int(r["true_need_count"]) for r in rs),
    "fraction_seed_episodes_zero_need":sum(int(r["true_need_count"])==0 for r in rs)/len(rs)}
  for name,m in fields.items():
   vals=[metric_value(r,m) for r in rs]
   mm,sd,lo,hi=mean_ci(vals)
   base[name+"_mean"]=mm;base[name+"_sd"]=sd;base[name+"_ci95_low"]=lo;base[name+"_ci95_high"]=hi
  summary.append(base)
 write_csv("summary_by_condition.csv",summary)

 # Paired policy contrasts, seed by seed.
 bypol=defaultdict(dict)
 for r in rows:
  key=(r["label_definition"],r["prevalence_scenario"],r["classifier_id"],float(r["rho_L1"]),int(r["n_L2"]),int(r["seed"]))
  bypol[key][r["policy"]]=r
 policy_diffs=[]
 pairs=(("HLS-B","D1","WAPS-D1"),("HLS-B","P1","WAPS-P1"),("P1","D1","P1-D1"))
 for g in sorted({k[:-1] for k in bypol}):
  sample={}
  for seed in sorted(k[-1] for k in bypol if k[:-1]==g):sample[seed]=bypol[g+(seed,)]
  for pa,pb,pair_name in pairs:
   for met in ("correct_on_time_expected_per_admitted","required_resolution_SLA_terminal","necessary_L2_timely_per_need","unnecessary_FP_service_h_per_1000","backlog_L2_terminal","legacy_RN"):
    ds=[metric_value(sample[s][pa],met)-metric_value(sample[s][pb],met) for s in sorted(sample)]
    policy_diffs.append(ci_record(ds,{"label_definition":g[0],"prevalence_scenario":g[1],"classifier_id":g[2],
      "rho_L1":g[3],"n_L2":g[4],"policy_contrast":pair_name,"metric":met,
      "method":"paired t interval across 40 seed clusters; exploratory, unadjusted"}))
 write_csv("paired_policy_contrasts.csv",policy_diffs)

 # Pairwise classifier contrasts in the same prevalence/load/capacity/policy stratum.
 bycp=defaultdict(dict)
 for r in rows:
  key=(r["label_definition"],r["prevalence_scenario"],float(r["rho_L1"]),int(r["n_L2"]),r["policy"],int(r["seed"]))
  bycp[key][r["classifier_id"]]=r
 classifier_diffs=[]
 cmetrics=("correct_on_time_expected_per_admitted","required_resolution_SLA_terminal","necessary_L2_timely_per_need",
           "unnecessary_FP_service_h_per_1000","backlog_L2_terminal")
 groups=sorted({k[:-1] for k in bycp})
 for g in groups:
  common=set.intersection(*(set(v) for k,v in bycp.items() if k[:-1]==g))
  for a,b in itertools.combinations(sorted(common),2):
   seeds=sorted(k[-1] for k in bycp if k[:-1]==g)
   for met in cmetrics:
    ds=[metric_value(bycp[g+(s,)][b],met)-metric_value(bycp[g+(s,)][a],met) for s in seeds]
    classifier_diffs.append(ci_record(ds,{"label_definition":g[0],"prevalence_scenario":g[1],"rho_L1":g[2],
      "n_L2":g[3],"policy":g[4],"classifier_A":a,"classifier_B":b,"contrast":"B-A","metric":met,
      "method":"paired same-trace seed contrast; exploratory, unadjusted"}))
 write_csv("paired_classifier_contrasts.csv",classifier_diffs)

 # Difference-in-differences: does changing classifier change the WAPS-vs-fixed policy effect?
 interactions=[]
 byseedclf=defaultdict(dict)
 for k,policies in bypol.items():
  label,prev,clf,rho,n2,seed=k
  byseedclf[(label,prev,float(rho),int(n2),int(seed))][clf]=policies
 for g in sorted({k[:-1] for k in byseedclf}):
  common=set.intersection(*(set(v) for k,v in byseedclf.items() if k[:-1]==g))
  seeds=sorted(k[-1] for k in byseedclf if k[:-1]==g)
  for a,b in itertools.combinations(sorted(common),2):
   for baseline in ("D1","P1"):
    ds=[]
    for s in seeds:
     ar=byseedclf[g+(s,)][a]; br=byseedclf[g+(s,)][b]
     ds.append((metric_value(br["HLS-B"],"correct_on_time_expected_per_admitted")-metric_value(br[baseline],"correct_on_time_expected_per_admitted"))-
       (metric_value(ar["HLS-B"],"correct_on_time_expected_per_admitted")-metric_value(ar[baseline],"correct_on_time_expected_per_admitted")))
    interactions.append(ci_record(ds,{"label_definition":g[0],"prevalence_scenario":g[1],"rho_L1":g[2],"n_L2":g[3],
      "classifier_A":a,"classifier_B":b,"interaction":"(WAPS-baseline)_B - (WAPS-baseline)_A",
      "baseline_policy":baseline,"metric":"correct_on_time_expected_per_admitted",
      "method":"paired seed difference-in-differences; exploratory, unadjusted"}))
 write_csv("classifier_organization_interactions.csv",interactions)

 # Descriptive five-objective operational Pareto front by policy and operating condition.
 pareto=[]
 strata=defaultdict(list)
 for r in summary:
  key=(r["label_definition"],r["prevalence_scenario"],float(r["rho_L1"]),int(r["n_L2"]),r["policy"])
  strata[key].append(r)
 for g,rs in strata.items():
  for r in rs:
   dom=any(is_dom(o,r) for o in rs if o["classifier_id"]!=r["classifier_id"])
   pareto.append({"label_definition":g[0],"prevalence_scenario":g[1],"rho_L1":g[2],"n_L2":g[3],"policy":g[4],
    "classifier_id":r["classifier_id"],"cost_regime":r["cost_regime"],"pD_target":r["pD_target"],"pFA_target":r["pFA_target"],
    "BA_published":r["BA_published"],"correct_on_time_mean":r["correct_on_time_expected_per_admitted_mean"],
    "necessary_SLA_mean":r["required_resolution_SLA_terminal_mean"],"necessary_detection_mean":r["necessary_L2_detection_fraction_mean"],
    "necessary_timely_mean":r["necessary_L2_timely_per_need_mean"],"unnecessary_FP_service_h_per_1000_mean":r["unnecessary_FP_service_h_per_1000_mean"],
    "L2_terminal_backlog_mean":r["backlog_L2_terminal_mean"],"operationally_dominated_by_means":dom,
    "objectives":"maximize detection, correct-and-on-time, necessary SLA and timely necessity; minimize FP nominal service work and terminal L2 backlog",
    "interpretation":"descriptive mean-vector Pareto; not inferential dominance"})
 write_csv("operational_pareto.csv",pareto)

 # Paired sensitivity between the directly audited original prevalence and PDF-implied prevalence.
 prevdiff=[]
 for g in sorted({(r["classifier_id"],float(r["rho_L1"]),int(r["n_L2"]),r["policy"]) for r in rows if r["label_definition"]=="original"}):
  id_,rho,n2,pol=g; d={}
  for r in rows:
   if r["label_definition"]!="original" or r["classifier_id"]!=id_ or float(r["rho_L1"])!=rho or int(r["n_L2"])!=n2 or r["policy"]!=pol:continue
   d.setdefault(r["prevalence_scenario"],{})[int(r["seed"])]=r
  a="original_pdf_ir_implied_40_of_14449";b="original_audited_39_of_14449"
  if a not in d or b not in d:continue
  for met in ("correct_on_time_expected_per_admitted","required_resolution_SLA_terminal","necessary_L2_timely_per_need","unnecessary_FP_service_h_per_1000"):
   ds=[metric_value(d[a][s],met)-metric_value(d[b][s],met) for s in sorted(set(d[a])&set(d[b]))]
   prevdiff.append(ci_record(ds,{"classifier_id":id_,"rho_L1":rho,"n_L2":n2,"policy":pol,
     "contrast":"pi 40/14449 minus pi 39/14449","metric":met,
     "method":"paired seed; same seed ids and common random stream; prevalence sensitivity only"}))
 write_csv("prevalence_sensitivity_paired.csv",prevdiff)

 # Rare-positive diagnostic uses one row per scenario-seed trace, not replicated policy/classifier rows.
 trace_unique={}
 for r in rows:
  k=(r["label_definition"],r["prevalence_scenario"],float(r["rho_L1"]),int(r["seed"]))
  trace_unique[k]=(int(r["admitted"]),int(r["true_need_count"]))
 rare=[]
 for label,prev,rho,seed in sorted(trace_unique):
  a,n=trace_unique[(label,prev,rho,seed)]
  rare.append({"label_definition":label,"prevalence_scenario":prev,"rho_L1":rho,"seed":seed,"admitted":a,"positive_needs":n})
 write_csv("unique_trace_positive_counts.csv",rare)

 # Short numeric labels keep the dense frontier figure readable; preserve an explicit codebook.
 codebook={}
 code_rows=[]
 for label in ("original","standardized"):
  ids=sorted({r["classifier_id"] for r in summary if r["label_definition"]==label})
  for code,classifier_id in enumerate(ids,1):
   codebook[(label,classifier_id)]=str(code)
   code_rows.append({"label_definition":label,"figure_code":code,"classifier_id":classifier_id})
 write_csv("figure_classifier_codebook.csv",code_rows)

 # Plot six condition panels: 3 policies × 2 label definitions, elevated L1 and reference L2.
 plt.rcParams.update({"font.size":8,"axes.spines.top":False,"axes.spines.right":False})
 fig,axs=plt.subplots(3,2,figsize=(12,10),sharex="col",sharey="row")
 policy_rows=(("D1",0),("P1",1),("HLS-B",2))
 colors={"symmetric":"#2575b7","asymmetric_cM3cFA":"#d36a28"}
 markers={"original":"o","standardized":"s"}
 for policy,ri in policy_rows:
  for label,ci in (("original",0),("standardized",1)):
   ax=axs[ri,ci]
   prev="original_audited_39_of_14449" if label=="original" else "standardized_pdf_ir_implied_19_of_14449"
   ss=[r for r in summary if r["label_definition"]==label and r["prevalence_scenario"]==prev and float(r["rho_L1"])==1.25 and int(r["n_L2"])==3 and r["policy"]==policy]
   for r in ss:
    x=r["unnecessary_FP_service_h_per_1000_mean"]; y=r["correct_on_time_expected_per_admitted_mean"]
    xe=max(0,x-r["unnecessary_FP_service_h_per_1000_ci95_low"]); ye=y-r["correct_on_time_expected_per_admitted_ci95_low"]
    ax.errorbar(x,y,xerr=xe,yerr=ye,fmt=markers[label],color=colors[r["cost_regime"]],alpha=.82,ms=5,capsize=2)
    code=int(codebook[(label,r["classifier_id"])])
    ax.annotate(str(code),(x,y),fontsize=7,fontweight="bold",
      xytext=(-7 if code%2 else 5,7+(code%6)*2),textcoords="offset points",
      bbox={"boxstyle":"round,pad=.08","facecolor":"white","edgecolor":"none","alpha":.8})
   ax.set_title(f"{label.title()} labels · {policy}")
   ax.grid(alpha=.2)
   if ci==0:ax.set_ylabel("Correct-and-on-time per admitted alert")
   if ri==2:ax.set_xlabel("Unnecessary L2 service hours per 1,000 alerts")
 fig.suptitle("Joint frontier and inherited controls · rhoL1=1.25 · 3 L2 analysts\nBars show marginal 95% CIs; classifier contrasts use paired intervals")
 handles=[plt.Line2D([0],[0],marker="o",color="w",markerfacecolor=v,label=k,markersize=7) for k,v in colors.items()]
 fig.legend(handles=handles,loc="lower center",ncol=2,frameon=False,bbox_to_anchor=(.5,-.005),title="Classifier cost regime")
 fig.tight_layout(rect=(0,.035,1,.95)); fig.savefig(OUT/"frontier_operational_tradeoff.png",dpi=180,bbox_inches="tight");plt.close(fig)

 # Produce transparent descriptive table of max means and frontier counts per stratum.
 choice=[]
 for g,rs in strata.items():
  top_ba=max(rs,key=lambda r:float(r["BA_published"]))
  top_correct=max(rs,key=lambda r:r["correct_on_time_expected_per_admitted_mean"])
  nd=[r for r in rs if not any(is_dom(o,r) for o in rs if o["classifier_id"]!=r["classifier_id"])]
  choice.append({"label_definition":g[0],"prevalence_scenario":g[1],"rho_L1":g[2],"n_L2":g[3],"policy":g[4],
    "highest_BA_classifier":top_ba["classifier_id"],"highest_BA":top_ba["BA_published"],
    "highest_correct_on_time_mean_classifier":top_correct["classifier_id"],"highest_correct_on_time_mean":top_correct["correct_on_time_expected_per_admitted_mean"],
    "descriptive_operational_pareto_ids":";".join(r["classifier_id"] for r in nd),"n_operationally_nondominated":len(nd),
    "selection_warning":"highest mean is descriptive; use paired CIs and multi-objective trade-off; no universal winner"})
 write_csv("descriptive_classifier_choices.csv",choice)

 # concise numerical report: frontiers, audit, paired effect summaries, positive counts, and caveats
 checks=json.loads((OUT/"validation_checks.json").read_text())
 paired_primary=[r for r in policy_diffs if r["metric"]=="correct_on_time_expected_per_admitted"]
 w_d=[r for r in paired_primary if r["policy_contrast"]=="WAPS-D1"]
 w_p=[r for r in paired_primary if r["policy_contrast"]=="WAPS-P1"]
 wc_d_pos=sum(r["ci95_low"]>0 for r in w_d); wc_d_neg=sum(r["ci95_high"]<0 for r in w_d); wc_d_zero=len(w_d)-wc_d_pos-wc_d_neg
 wc_p_pos=sum(r["ci95_low"]>0 for r in w_p); wc_p_neg=sum(r["ci95_high"]<0 for r in w_p); wc_p_zero=len(w_p)-wc_p_pos-wc_p_neg
 n_need=sum(x[1] for x in trace_unique.values()); n_alerts=sum(x[0] for x in trace_unique.values())
 zero_frac=sum(x[1]==0 for x in trace_unique.values())/len(trace_unique)
 tab39=[r for r in summary if r["label_definition"]=="original" and r["prevalence_scenario"]=="original_audited_39_of_14449"]
 tab40=[r for r in summary if r["label_definition"]=="original" and r["prevalence_scenario"]=="original_pdf_ir_implied_40_of_14449"]
 # sample high-load, three-L2 policy averages for the joint-frontier only
 def cell_table(label,prev,rho=1.25,n2=3,policy="HLS-B"):
  rr=[r for r in summary if r["label_definition"]==label and r["prevalence_scenario"]==prev and float(r["rho_L1"])==rho and int(r["n_L2"])==n2 and r["policy"]==policy]
  return "\n".join(f"| {r['classifier_id']} | {float(r['pD_target']):.4f} | {float(r['pFA_target']):.4f} | {r['correct_on_time_expected_per_admitted_mean']:.4f} [{r['correct_on_time_expected_per_admitted_ci95_low']:.4f}, {r['correct_on_time_expected_per_admitted_ci95_high']:.4f}] | {r['required_resolution_SLA_terminal_mean']:.4f} | {r['unnecessary_FP_service_h_per_1000_mean']:.1f} | {r['backlog_L2_terminal_mean']:.1f} |" for r in rr)
 frontsets={"original":"LSEnsemble A+C sym; LR A+C sym; Bayesian MLP A+C sym/asym; RF A+C asym; LightGBM C asym; Bayesian MLP C asym",
   "standardized":"LR A+C sym; Bayesian MLP A+C sym; LightGBM A+C sym; RF A+C asym; LSEnsemble A asym; LightGBM A+C asym"}
 report=f'''# SOCTRA–HLS joint classifier-frontier campaign

## Objetivo y fuente de configuraciones

Esta extensión evalúa, en el simulador organizativo existente, los 13 puntos de la frontera conjunta de detección/falsa alarma y cuatro controles de la fase 2. Los puntos publicados son tasas agregadas del artículo, no predicciones individuales sobre alertas SOCTRA. Las recomendaciones son sintéticas y automáticas. No se simula reportado. D1, P1 y WAPS/HLS-B permanecen sin cambios.

La frontera conjunta se fija por definición de etiquetas, agrupando Tables 5 y 7, con el criterio maximize pD/minimize pFA; se conservan BA, beneficio, coste, algoritmo y características en [`joint_pareto_frontier_13.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/joint_pareto_frontier_13.csv), con el inventario auditado completo en [`classifier_inventory_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/classifier_inventory_72.csv). Los resultados de coste simétrico y asimétrico son puntos operativos de configuraciones diferentes, no una única curva ROC.

## Auditoría de prevalencia, trazas y reutilización

Se mantuvieron por separado original 39/14.449 (etiquetas auditadas directamente), original 40/14.449 (inferencia del IR redondeado de la Tabla 1) y estandarizadas 19/14.449 (IR del artículo). La configuración fase 2 había guardado pi=0.002699840128036543, aunque estaba rotulada 39/14.449. La regeneración con el mismo generador y semillas mostró que las trazas exógenas y los hashes completos de recomendación de sus cuatro puntos originales coinciden exactamente con pi=39/14.449 en las 80 celdas semilla×carga; esas filas se reutilizaron como realización sintética compatible, dejando constancia de la discrepancia de metadatos.

Para pi=40/14.449, coincidieron 77/80 celdas semilla×carga. Las únicas diferencias fueron semilla 272600013 con rhoL1=1.25 y semilla 272600030 con rhoL1=.85 y 1.25. Se reutilizaron las filas de las otras 77 celdas y se repitieron solamente las 108 filas policy×roster×punto antiguas afectadas (3 celdas×4 puntos originales×3 rosters×3 políticas). Las cinco configuraciones estandarizadas de la fase 2 coincidieron en hashes con pi=19/14.449 y se reutilizaron. El detalle está en [`phase2_reuse_trace_audit.csv`](../../results/soc_triage_classifier_frontier_campaign/phase2_reuse_trace_audit.csv).

### Recuentos ejecutados

- 8 puntos nuevos de frontera: 5 originales evaluados bajo ambas prevalencias y 3 estandarizados bajo su prevalencia del artículo, **9.360 episodios de política**.
- 108 repeticiones justificadas para las tres celdas originales incompatibles bajo pi=40/14.449.
- 9.252 episodios de fase 2 reutilizados por compatibilidad de hash/configuración.
- Dataset analítico unido: **18.720 episodios**, 720 celdas de condición agrupadas por escenario, punto, carga, roster y semilla.

Las 40 semillas (272600000–272600039) ya se habían usado en fase 2. Esta campaña es una extensión exploratoria emparejada, no una validación independiente. Se mantuvieron rhoL1=.85/1.25, roster 6 L1, 2/3/4 L2, horizonte 24 h, drenaje 36 h, deadlines 1/4/12 h y WAPS ventana 4 h / umbrales 1.05/1.20. Cambiar L2 mantuvo constante la tasa absoluta de llegadas.

## Validación de integridad

[`validation_checks.json`](../../results/soc_triage_classifier_frontier_campaign/validation_checks.json) registra PASS: los hashes exógenos son únicos por condición emparejada; denominadores coinciden; TP+FP+FN+TN=admitidas; TP+FN=necesidad sintética; no hay deadlines sin madurar al corte. Se preservaron los CSV originales de la fase 2. No se modificó motor ni políticas; los cambios locales preexistentes añaden una referencia NOMINAL-REF no utilizada.

## Resultados principales por régimen

La comparación operativa se presenta como vector: resolución correcta y puntual, SLA de necesidad, detección de necesidad, servicio L2 innecesario por falsas alarmas, y backlog. No se impone un índice ponderado único. La frontera de Pareto operativa es descriptiva de medias y no equivale a superioridad inferencial. Intervalos de política y clasificador son contrastes pareados por semilla, t bilateral 95%, sin corrección por multiplicidad.

En la figura, las etiquetas numéricas remiten a [`figure_classifier_codebook.csv`](../../results/soc_triage_classifier_frontier_campaign/figure_classifier_codebook.csv); el orden de códigos se mantiene separado para cada definición de etiqueta.

### HLS-B/WAPS con carga L1 elevada y 3 analistas L2: etiquetas originales, pi=39/14.449

| Punto | pD | pFA | Correcta y puntual/admitida (IC95%) | SLA necesario | Servicio FP h / 1.000 | Backlog L2 terminal |
|---|---:|---:|---:|---:|---:|---:|
{cell_table('original','original_audited_39_of_14449')}

### HLS-B/WAPS con carga L1 elevada y 3 analistas L2: etiquetas originales, pi=40/14.449

| Punto | pD | pFA | Correcta y puntual/admitida (IC95%) | SLA necesario | Servicio FP h / 1.000 | Backlog L2 terminal |
|---|---:|---:|---:|---:|---:|---:|
{cell_table('original','original_pdf_ir_implied_40_of_14449')}

### HLS-B/WAPS con carga L1 elevada y 3 analistas L2: etiquetas estandarizadas, pi=19/14.449

| Punto | pD | pFA | Correcta y puntual/admitida (IC95%) | SLA necesario | Servicio FP h / 1.000 | Backlog L2 terminal |
|---|---:|---:|---:|---:|---:|---:|
{cell_table('standardized','standardized_pdf_ir_implied_19_of_14449')}

Las tablas completas por etiqueta, prevalencia, punto, carga, capacidad y política se encuentran en [`summary_by_condition.csv`](../../results/soc_triage_classifier_frontier_campaign/summary_by_condition.csv). Los contrastes de políticas, puntos de clasificador e interacciones están en `paired_policy_contrasts.csv`, `paired_classifier_contrasts.csv` y `classifier_organization_interactions.csv`.

## Comparación e incertidumbre

En todos los puntos de una condición, las políticas comparten por semilla las mismas alertas, necesidad oculta y recomendaciones; solo cambia el modo organizativo. Los contrastes classifier B−A comparan las mismas semillas y trazas. La interacción diferencia-en-diferencias compara cuánto cambia WAPS frente a D1 o P1 al cambiar el punto de clasificación. Las tablas incluyen el IC95% de cada contraste, n=40, sin ajuste por la cantidad de contrastes.

Para la métrica primaria de resolución correcta y puntual, WAPS−D1 tiene IC95% completamente positivos en {wc_d_pos}/{len(w_d)} condiciones de punto×prevalencia×carga×roster, negativos en {wc_d_neg} y cruzan cero en {wc_d_zero}; WAPS−P1 queda completamente positivo en {wc_p_pos}/{len(w_p)}, negativo en {wc_p_neg}, y cruza cero en {wc_p_zero}. Son conteos exploratorios sobre muchas comparaciones, no pruebas familiares confirmatorias. Los efectos de WAPS frente a las fijas varían por régimen; las tablas completas permiten ver signo y magnitud en cada estrato.

El Pareto operativo utiliza medias de cinco resultados (detección, correcta/puntual, SLA necesario, trabajo innecesario y backlog) por política y condición. [`operational_pareto.csv`](../../results/soc_triage_classifier_frontier_campaign/operational_pareto.csv) no elige ganador único. [`descriptive_classifier_choices.csv`](../../results/soc_triage_classifier_frontier_campaign/descriptive_classifier_choices.csv) separa la mayor BA de la mayor media de resolución correcta/puntual; esta última es solo descriptiva y debe interpretarse con sus contrastes emparejados.

## Falsas alarmas, detección y sobrecarga

En estas prevalencias bajas, un incremento de pFA puede multiplicar las recomendaciones y horas L2, mientras que las investigaciones positivas siguen siendo escasas. En consecuencia, mayor detección solo mejora la resolución correcta/puntual si esas tareas L2 adicionales llegan a tiempo y su beneficio compensa el servicio innecesario y la congestión. Los datos por condición incluyen las tasas realizadas, horas FP, FN omitidas, SLA, utilización y backlog; no se resta una penalización arbitraria a las falsas alarmas. La figura [`frontier_operational_tradeoff.png`](../../results/soc_triage_classifier_frontier_campaign/frontier_operational_tradeoff.png) muestra el compromiso para rhoL1=1.25 y nL2=3, con IC marginales visibles; las inferencias entre puntos deben leerse en los contrastes pareados.

## Resultado cuantitativo sobre la preferencia operativa

El mayor promedio de resolución correcta y puntual fue estable dentro de la cuadrícula evaluada: LSEnsemble A+C simétrico encabezó las 36 combinaciones de etiqueta original (2 prevalencias × 2 cargas L1 × 3 plantillas L2 × 3 políticas); LR A+C simétrico encabezó las 18 combinaciones estandarizadas. En las 54 combinaciones, el punto con mayor BA publicada no fue el de mayor media de resolución correcta y puntual. Esto describe el máximo dentro de los puntos muestreados, no una superioridad inferencial universal ni una selección válida para una prevalencia operativa desconocida.

La frontera de medias operativas (cinco objetivos simultáneos) retuvo siete de nueve puntos originales en cada una de sus 36 condiciones. En el grupo estandarizado retuvo cinco puntos en 15 condiciones y seis en tres condiciones, de ocho evaluadas. La aparición/desaparición de RF A+C simétrico en tres condiciones refleja una frontera de medias sensible a esa condición; no es evidencia confirmatoria de un cambio de preferencia. Los objetivos permanecen en tensión: más detección puede coexistir con más trabajo FP, menos resoluciones puntuales y mayor backlog.

Un contraste ilustrativo, fijado aquí como descripción de la cuadrícula y no como prueba confirmatoria, es rhoL1=1.25, tres analistas L2, WAPS y etiquetas originales con pi=39/14.449. Frente a LSEnsemble A+C simétrico (pD=.75, pFA=.151), Bayesian MLP A+C asimétrico (pD=.925, pFA=.3632) elevó la detección sintética de necesidad de .666 a .805, pero el servicio innecesario pasó de 123.9 a 297.4 h por 1,000 alertas, el SLA de necesidades bajó de .895 a .628 y la resolución correcta/puntual cayó de .5902 a .4130. La diferencia pareada LSEnsemble menos Bayesian MLP fue +.1772 [IC95% .1700, .1844], n=40 semillas. El backlog L2 terminal aumentó de 0 a 88.7 tareas medias. Así, en este régimen la detección adicional no compensó la carga inducida para el resultado puntual, aunque atendió más necesidades en términos de detección.

La ganancia de WAPS sobre políticas fijas dependió del punto de clasificación. En ese mismo estrato WAPS−D1 fue +.0853 [+.0719,+.0988] para LSEnsemble y +.0572 [+.0473,+.0670] para Bayesian MLP asimétrico. La diferencia-en-diferencias (cambio en WAPS−D1, LSEnsemble menos Bayesian MLP) fue +.0282 [+.0239,+.0325]. Es evidencia exploratoria de interacción dentro del simulador y bajo sus supuestos, separada del efecto directo del punto de clasificador; no implica que WAPS rescate la configuración de alta falsa alarma. En las 1,200 interacciones por métricas y estratos, 913 IC95% no ajustados excluyeron cero y el mayor valor absoluto de la media fue .0762. La multiplicidad hace que esos recuentos sean descriptivos; no deben leerse como una tasa de hallazgos confirmados.

La lectura global es, por tanto, condicionada. En el objetivo primario de resolución correcta/puntual no se observó cambio del máximo medio entre carga .85/1.25, 2/3/4 analistas L2 y las tres organizaciones, dentro de cada definición de etiquetas. Sí aparecen intercambios operativos que pueden cambiar cuál punto es aceptable al imponer requisitos mínimos de detección, límites de trabajo innecesario o SLA. Sin preferencias/umbrales operativos justificados, los datos no identifican un clasificador único preferible. La evidencia apoya que BA por sí sola no basta para ordenar los puntos según este desenlace sintético y que la alta pFA puede ser material bajo presión de capacidad; no establece que los modelos reales causarían esos efectos en alertas reales.

## Sensibilidad a la prevalencia original

La diferencia entre las prevalencias 39/14.449 y 40/14.449 se evalúa con semillas emparejadas en [`prevalence_sensitivity_paired.csv`](../../results/soc_triage_classifier_frontier_campaign/prevalence_sensitivity_paired.csv). La mayoría de las realizaciones se conserva, pero tres de 80 celdas semilla×carga tienen hashes de recomendación distintos y se repitieron. Para resolución correcta y puntual, las 162 diferencias pareadas tienen IC95% que incluyen cero y la mayor diferencia media absoluta es 0.0000407. Esa pequeña sensibilidad simulada no resuelve el origen documental de la discrepancia ni justifica sustituir el conteo auditado por el índice redondeado. Las conclusiones de régimen dependen también de la hipótesis de necesidad técnica sintética y no reflejan necesariamente prevalencias operativas de investigación L2.

## Positivos escasos y limitaciones

En las {len(trace_unique)} trazas únicas hay {n_need} alertas con necesidad sintética entre {n_alerts} admitidas; la fracción de trazas semilla con cero necesidades es {zero_frac:.3f}. En el conjunto estandarizado y especialmente por semilla, numerosos episodios contienen cero o muy pocos positivos. Las tasas pD por seed son, por ello, discretas e imprecisas; no se debe confundir el pD objetivo publicado con el pD realizado. La incertidumbre t por semillas resume la variabilidad simulada, pero no corrige el bajo número de casos positivos ni la falta de errores estratificados por clase.

Los errores del clasificador siguen supuestos intercambiables entre tipos de tarea; la necesidad es oculta y sintética; las recomendaciones se aceptan automáticamente; los tiempos, elegibilidad y capacidades son del simulador; y no hay dependencia de errores por proyecto ni respuesta humana. Las tablas comparan puntos agregados publicados y no recrean decisiones individuales de los modelos SOCTRA. Los resultados son exploratorios, sin ajuste de multiplicidad y con prevalencia original parcialmente inferida.

## Conclusión

En la matriz sintética emparejada, BA o pD no bastaron para ordenar las configuraciones por resolución correcta y puntual. Los puntos de menor pFA tuvieron los mayores promedios de ese desenlace en cada definición de etiqueta, y los puntos de alta detección/alta falsa alarma mostraron pérdidas importantes bajo sobrecarga L1 incluso con WAPS. La ventaja relativa de organización varió según el punto de clasificación, aunque la interacción es exploratoria y no ajustada por multiplicidad. Los objetivos operativos conservan compromisos; no se identifica una configuración universal ni se demuestra impacto en GMV-CERT. Las conclusiones están condicionadas a prevalencias auditadas/inferidas, necesidad técnica sintética, aceptación automática, errores intercambiables, servicios y recursos del simulador y solo 40 semillas con positivos escasos.

## Reproducción

- Configuración fija: `config/campaign.json`.
- Runner con auditoría de reutilización y hashes: `run_campaign.py`.
- Resumen pareado, fronteras y figura: `summarize_campaign.py`.
- Validación y manifiesto: `results/soc_triage_classifier_frontier_campaign/validation_checks.json` y `reproducibility_manifest.json`.
- CSV de episodios unido y CSVs de análisis: `results/soc_triage_classifier_frontier_campaign/`.

Recrear la extensión desde el estado actual requiere ejecutar `python studies/soc_triage_classifier_frontier_campaign/run_campaign.py`; el análisis posterior es `python studies/soc_triage_classifier_frontier_campaign/summarize_campaign.py`. El subconjunto sintético de Phase 2 requerido para verificar y reutilizar episodios se incluye como `results/soc_triage_classifier_frontier_campaign/phase2_reuse_source_episodes.csv`.
'''
 REPORT.write_text(report,encoding="utf-8")
 def sha256_file(path):
  return hashlib.sha256(path.read_bytes()).hexdigest()
 input_paths={
  "campaign_config":HERE/"config"/"campaign.json",
  "phase2_reuse_source_episodes":OUT/"phase2_reuse_source_episodes.csv",
  "classifier_inventory_72":ROOT/"results"/"soc_triage_classifier_operating_impact_source_audit"/"classifier_inventory_72.csv",
  "joint_frontier_13":ROOT/"results"/"soc_triage_classifier_operating_impact_source_audit"/"joint_pareto_frontier_13.csv",
  "source_audit_metadata":ROOT/"results"/"soc_triage_classifier_operating_impact_source_audit"/"audit_metadata.json",
 }
 manifest={"pilot_reference_commit":"df80a78e413c88f7cf22b807e8ee27f4e556a726",
  "phase2_code_and_result_reference":"218dc7ba4616b26f7051d7548e6fbcecfd8bc5b8",
  "generated_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
  "sha256_inputs":{name:{"path":str(path.relative_to(ROOT)),"sha256":sha256_file(path)} for name,path in input_paths.items()},
  "sha256_outputs":{path.name:sha256_file(path) for path in sorted(OUT.iterdir()) if path.is_file() and path.name!="reproducibility_manifest.json"}}
 (OUT/"reproducibility_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"episodes":len(rows),"summary_rows":len(summary),"policy_contrasts":len(policy_diffs),
  "classifier_contrasts":len(classifier_diffs),"interactions":len(interactions),"operational_pareto_rows":len(pareto),
  "rare_trace_count":len(trace_unique),"needs":n_need,"alerts":n_alerts,"zero_need_fraction":zero_frac,
  "WAPS-D1 positive/negative/crossing":(wc_d_pos,wc_d_neg,wc_d_zero),"WAPS-P1 positive/negative/crossing":(wc_p_pos,wc_p_neg,wc_p_zero)},indent=2))
if __name__=="__main__":main()
