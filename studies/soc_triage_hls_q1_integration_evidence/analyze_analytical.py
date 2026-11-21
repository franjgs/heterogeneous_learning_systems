"""Reproducible offered-load projections for the prespecified alpha grid."""
from __future__ import annotations
import csv,json,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from studies.soc_triage_hls_q1_integration_evidence.run_primary_campaign import CONFIG,OUT,ALPHAS,PI
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity
from studies.soc_human_ai_organization.soc_parametric_baseline import BASE_ELIGIBILITY,BASE_L1_ANALYSTS,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECTS,PROJECT_MIX,build_roster

def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n');w.writeheader();w.writerows(rows)

def run():
 rows=[]
 for point in CONFIG['classifiers']:
  pi=PI; q=pi*point['pD']+(1-pi)*point['pFA']
  counts={'TP_per_1000':1000*pi*point['pD'],'FP_per_1000':1000*(1-pi)*point['pFA'],
          'FN_per_1000':1000*pi*(1-point['pD']),'TN_per_1000':1000*(1-pi)*(1-point['pFA'])}
  lam1=effective_capacity(build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=3,mean_eligible_projects=BASE_ELIGIBILITY)[0],
                          build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=3,mean_eligible_projects=BASE_ELIGIBILITY)[2],PROJECT_MIX)['max_common_arrivals_per_h']*float(CONFIG['simulation']['rho_L1'])
  for alpha in ALPHAS:
   for n_l2 in CONFIG['simulation']['n_L2']:
    l1,l2,l1s,l2s=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=n_l2,mean_eligible_projects=BASE_ELIGIBILITY)
    mix=tuple(PROJECT_MIX)
    factors={}
    for k in PROJECTS:
     qk=pi*point['pD']+(1-pi)*point['pFA']
     factors[k]=(pi*point['pD']+(1-pi)*point['pFA']*alpha)/qk if qk else 1.0
    expected={a.analyst_id:{k:l2s[a.analyst_id][k]*factors[k] for k in a.eligible_classes} for a in l2}
    mu=effective_capacity(l2,expected,mix)['max_common_arrivals_per_h']
    service_mean={k:statistics.mean(l2s[a.analyst_id][k] for a in l2 if k in a.eligible_classes) for k in PROJECTS}
    necessary=sum(counts['TP_per_1000']*PROJECT_MIX[i]*service_mean[k] for i,k in enumerate(PROJECTS))
    unnecessary=sum(counts['FP_per_1000']*PROJECT_MIX[i]*service_mean[k]*alpha for i,k in enumerate(PROJECTS))
    omitted=sum(counts['FN_per_1000']*PROJECT_MIX[i]*service_mean[k] for i,k in enumerate(PROJECTS))
    rows.append({**{k:v for k,v in point.items() if k in ['id','algorithm','features','pD','pFA','BA']},
       'label_definition':'standardized','pi':pi,'alpha':alpha,'rho_L1':CONFIG['simulation']['rho_L1'],'lambda_L1_per_h':lam1,
       'n_L2':n_l2,'q_expected':q,'recommendations_per_1000':1000*q,**counts,
       'TP_L2_work_offered_h_per_1000':necessary,'FP_unnecessary_work_h_per_1000':unnecessary,
       'FN_omitted_work_h_per_1000':omitted,'TP_work_per_hour':lam1*necessary/1000,
       'FP_work_per_hour':lam1*unnecessary/1000,'FN_work_omitted_per_hour':lam1*omitted/1000,
       'mu_L2_effective_per_h_alpha_adjusted':mu,'rho_L2_offered':lam1*q/mu,
       'capacity_interpretation':'fractional-flow mean offered-load marker; not an SLA guarantee'})
 write(OUT/'analytic_workload_by_alpha.csv',rows)
 print('wrote',len(rows),'analytical conditions')
if __name__=='__main__':run()
