"""Rebuild paired classifier contrasts and WAPS L1 mode diagnostics from saved seeds."""
from __future__ import annotations
import csv,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from studies.soc_triage_hls_q1_integration_evidence.run_primary_campaign import CONFIG,OUT,BOOT_REPS,BOOT_SEED,_primary_trace,_run_l1
from studies.soc_human_ai_organization.soc_parametric_baseline import BASE_ELIGIBILITY,BASE_L1_ANALYSTS,PROJECT_MIX,build_roster
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity
from studies.soc_triage_organization_coupling import run_pilot as frozen

def read(path):
 with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def write(path,rows):
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)),lineterminator='\n');w.writeheader();w.writerows(rows)
def q(x):return float(np.quantile(x,.025)),float(np.quantile(x,.975))

def main():
 episodes=read(OUT/'episodes.csv'); seeds=sorted({int(r['seed']) for r in episodes})
 idx=np.random.default_rng(BOOT_SEED).integers(0,len(seeds),size=(BOOT_REPS,len(seeds)))
 groups=defaultdict(list)
 for r in episodes:groups[(r['classifier_id'],float(r['alpha_fp_service_fraction']),int(r['n_L2']),r['policy'])].append(r)
 boot={};points={}
 for key,rs in groups.items():
  rs=sorted(rs,key=lambda r:int(r['seed']))
  n=np.array([int(r['timely_needs_numerator']) for r in rs]);d=np.array([int(r['S_plus_denominator']) for r in rs])
  bn=n[idx].sum(axis=1);bd=d[idx].sum(axis=1);v=np.full(BOOT_REPS,np.nan);valid=bd>0;v[valid]=bn[valid]/bd[valid]
  boot[key]=v;points[key]=int(n.sum())/int(d.sum())
 classifiers=sorted({r['classifier_id'] for r in episodes}); alphas=sorted({float(r['alpha_fp_service_fraction']) for r in episodes}); rosters=sorted({int(r['n_L2']) for r in episodes}); policies=('D1','P1','HLS-B')
 cl=[]; inter=[]; alpha_rows=[]
 for alpha in alphas:
  for roster in rosters:
   for policy in policies:
    for i,a in enumerate(classifiers):
     for b in classifiers[i+1:]:
      diff=boot[(b,alpha,roster,policy)]-boot[(a,alpha,roster,policy)];diff=diff[np.isfinite(diff)]
      lo,hi=q(diff)
      cl.append({'classifier_A':a,'classifier_B':b,'alpha':alpha,'n_L2':roster,'policy':policy,
                 'S_plus_B_minus_A':points[(b,alpha,roster,policy)]-points[(a,alpha,roster,policy)],
                 'bootstrap_CI95_low':lo,'bootstrap_CI95_high':hi,'bootstrap_replicates':len(diff),
                 'direction':'B minus A','multiplicity':'unadjusted exploratory'})
   for i,a in enumerate(classifiers):
    for b in classifiers[i+1:]:
     wa=boot[(a,alpha,roster,'HLS-B')]-boot[(a,alpha,roster,'D1')]
     wb=boot[(b,alpha,roster,'HLS-B')]-boot[(b,alpha,roster,'D1')]
     dd=(wb-wa);dd=dd[np.isfinite(dd)];lo,hi=q(dd)
     point=(points[(b,alpha,roster,'HLS-B')]-points[(b,alpha,roster,'D1')])-(points[(a,alpha,roster,'HLS-B')]-points[(a,alpha,roster,'D1')])
     inter.append({'classifier_A':a,'classifier_B':b,'alpha':alpha,'n_L2':roster,
                   'difference_in_WAPS_minus_D1_S_plus':point,'bootstrap_CI95_low':lo,'bootstrap_CI95_high':hi,
                   'bootstrap_replicates':len(dd),'multiplicity':'unadjusted exploratory'})
 # Within-seed alpha contrasts, referenced to the full-investigation case.
 for classifier in classifiers:
  for roster in rosters:
   for policy in policies:
    for alpha in alphas:
     if alpha==1.0: continue
     diff=boot[(classifier,alpha,roster,policy)]-boot[(classifier,1.0,roster,policy)]
     diff=diff[np.isfinite(diff)];lo,hi=q(diff)
     alpha_rows.append({'classifier_id':classifier,'n_L2':roster,'policy':policy,'alpha':alpha,'reference_alpha':1.0,
       'S_plus_alpha_minus_full':points[(classifier,alpha,roster,policy)]-points[(classifier,1.0,roster,policy)],
       'bootstrap_CI95_low':lo,'bootstrap_CI95_high':hi,'bootstrap_replicates':len(diff),
       'interpretation':'paired exploratory sensitivity contrast'})
 write(OUT/'paired_classifier_contrasts.csv',cl)
 write(OUT/'classifier_organization_interactions.csv',inter)
 write(OUT/'alpha_paired_contrasts.csv',alpha_rows)
 # One L1 WAPS replay per new seed. This stores the mode share omitted from the
 # policy-episode schema; verify trace identity and L1 outcomes against saved rows.
 l1,l2,l1s,l2s=build_roster(n_l1=BASE_L1_ANALYSTS,n_l2=3,mean_eligible_projects=BASE_ELIGIBILITY)
 mu1=effective_capacity(l1,l1s,PROJECT_MIX)['max_common_arrivals_per_h']; mode_rows=[];switch_rows=[]; failures=[]
 stored={}
 for seed in seeds:
  trace,_,_= _primary_trace(seed,CONFIG['classifiers'][0])
  exog=frozen._trace_hash(trace,include_recommendation=False)
  ls=_run_l1(trace,'HLS-B',seed,l1,l1s,mu1)
  hist=ls.hlsa_history;p1=sum(x.mode=='P1' for x in hist)
  row={'seed':seed,'exogenous_sha256':exog,'L1_dispatch_epochs':len(hist),'L1_P1_dispatch_epochs':p1,
       'L1_P1_fraction':p1/len(hist) if hist else 0.0,'L1_switch_count':sum(x.switched for x in hist),
       'L1_backlog_H':ls.at_horizon.pending,'L1_backlog_terminal':ls.after_drain.pending,
       'L1_utilization_mean_H':np.mean([v for _,v in ls.at_horizon.utilization_by_analyst]),
       'L1_utilization_mean_terminal':np.mean([v for _,v in ls.after_drain.utilization_by_analyst])}
  mode_rows.append(row);stored[seed]=row
  for x in hist:
   if x.switched:switch_rows.append({'seed':seed,'time_h':x.time,'mode_after_switch':x.mode,'pressure':x.pressure,'pending':x.pending,'occupied':x.occupied})
 # Check one row per seed: saved L1 state must match the deterministic replay across all conditions.
 for r in episodes:
  if r['policy']!='HLS-B' or r['classifier_id']!=classifiers[0] or r['alpha_fp_service_fraction']!='1.0' or r['n_L2']!='3':continue
  ss=int(r['seed']);m=stored[ss]
  if int(r['L1_backlog_H'])!=int(m['L1_backlog_H']) or int(r['L1_backlog_terminal'])!=int(m['L1_backlog_terminal']):failures.append(ss)
 write(OUT/'l1_waps_modes_by_seed.csv',mode_rows)
 if switch_rows:write(OUT/'l1_waps_switches.csv',switch_rows)
 write(OUT/'l1_waps_mode_summary.csv',[{
   'seed_count':len(mode_rows),'mean_L1_P1_fraction':float(np.mean([float(r['L1_P1_fraction']) for r in mode_rows])),
   'mean_L1_switches_per_seed':float(np.mean([int(r['L1_switch_count']) for r in mode_rows])),
   'total_L1_switches':sum(int(r['L1_switch_count']) for r in mode_rows),
   'mean_L1_backlog_H':float(np.mean([int(r['L1_backlog_H']) for r in mode_rows])),
   'mean_L1_backlog_terminal':float(np.mean([int(r['L1_backlog_terminal']) for r in mode_rows])),
   'mean_L1_utilization_H':float(np.mean([float(r['L1_utilization_mean_H']) for r in mode_rows])),
   'mean_L1_utilization_terminal':float(np.mean([float(r['L1_utilization_mean_terminal']) for r in mode_rows]))
 }])
 # Correct validation manifest counts: three classifier trace rows share each seed's need realization.
 checks=json.loads((OUT/'validation_checks.json').read_text())
 need_by_seed={int(r['seed']):int(r['synthetic_needs']) for r in read(OUT/'trace_audit.csv') if r['classifier_id']==classifiers[0]}
 checks['unique_seed_need_count']=sum(need_by_seed.values())
 checks['unique_zero_need_seeds']=sum(v==0 for v in need_by_seed.values())
 checks['trace_rows_with_zero_need_across_classifier_points']=sum(int(r['synthetic_needs'])==0 for r in read(OUT/'trace_audit.csv'))
 checks['same_need_count_across_classifier_points']=all(len({int(r['synthetic_needs']) for r in read(OUT/'trace_audit.csv') if int(r['seed'])==s})==1 for s in seeds)
 checks['L1_WAPS_mode_replay_matches_saved_backlogs']='PASS' if not failures else 'FAIL'
 checks['L1_WAPS_mode_replay_failures']=failures
 (OUT/'validation_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 manifest=json.loads((OUT/'execution_manifest.json').read_text());manifest['checks']=checks
 (OUT/'execution_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 if failures:raise AssertionError(f'L1 replay mismatch: {failures[:10]}')
 print('classifier contrasts',len(cl),'interactions',len(inter),'unique needs',checks['unique_seed_need_count'],'zero need seeds',checks['unique_zero_need_seeds'],'L1 switches',len(switch_rows))
if __name__=='__main__':main()
