"""Predeclared paired D1/P1 confirmatory campaign; no simulator modifications."""
from __future__ import annotations
import csv, hashlib, json, math, statistics, sys, time
from pathlib import Path
from dataclasses import replace
ROOT=Path(__file__).resolve().parents[2]; sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from scipy.stats import t as student_t
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import Analyst
from hls.rq1_l1_l2 import simulate_l1_l2, stage_metrics_at
from studies.soc_human_ai_organization import run_a0_baseline_congestion as a0
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H
HERE=Path(__file__).resolve().parent; CFG=json.loads((HERE/'config/soc_confirmatory.json').read_text())
H=float(CFG['admission_horizon_h']); D=float(CFG['drain_h']); RATE=float(CFG['base_l1_capacity_per_hour']); OUT=ROOT/CFG['output_dir'];OUT.mkdir(parents=True,exist_ok=True)
def save(name,rows):
 if not rows:return
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
def spread(roster,g):
 classes=sorted({k for a in roster for k in a.eligible_classes})
 means={k:statistics.mean(a.competence[k] for a in roster if k in a.eligible_classes) for k in classes}
 result=[]
 for a in roster:
  comp={k:(means[k]+g*(v-means[k]) if k in a.eligible_classes else v) for k,v in a.competence.items()}
  if any(not 0<=v<=1 for v in comp.values()):raise ValueError('competence outside [0,1]')
  result.append(Analyst(a.analyst_id,a.eligible_classes,comp))
 return tuple(result)
def ci(values):
 m=statistics.mean(values);sd=statistics.stdev(values);rad=student_t.ppf(.975,len(values)-1)*sd/math.sqrt(len(values))
 return m,sd,m-rad,m+rad
scenarios=[dict(name='rho_125_primary',rho=CFG['primary_rho'],deadline=1.,spread=1.,family='primary')]
scenarios += [dict(name=f'rho_{rho:.2f}_secondary',rho=rho,deadline=1.,spread=1.,family='load') for rho in CFG['secondary_rho']]
scenarios += [dict(name=f'deadline_{g:.2f}',rho=CFG['primary_rho'],deadline=g,spread=1.,family='robustness') for g in CFG['deadline_multipliers']]
scenarios += [dict(name=f'competence_{g:.2f}',rho=CFG['primary_rho'],deadline=1.,spread=g,family='robustness') for g in CFG['competence_spread_multipliers']]
assert len(scenarios)==9
seeds=list(range(CFG['seed_base'],CFG['seed_base']+CFG['seed_count']))
assert len(seeds)==len(set(seeds))==100 and not set(seeds)&(set(range(261140000,261140030))|set(range(261132000,261132020)))
rows=[];strata=[];start=time.perf_counter()
for sc in scenarios:
 l1base,l2base,s1,s2=a0._roster(CFG['l1_roster_indices'])
 l1,l2=spread(l1base,sc['spread']),spread(l2base,sc['spread'])
 config=REFERENCE.scenario_config(arrival_rate_per_h=RATE*sc['rho'],sla_multiplier=sc['deadline'])
 config=replace(config,horizon=H)
 for seed in seeds:
  generated=generate_alerts(config,seed)
  admitted=[r for r in generated if r.routed.alert.arrival<H]
  fingerprint=hashlib.sha256(json.dumps([(r.routed.alert.alert_id,r.routed.alert.arrival,r.routed.alert.task_class,r.routed.alert.deadline,r.severity,r.difficulty,r.routed.soctra_recommendation) for r in admitted],sort_keys=True).encode()).hexdigest()
  exogenous=hashlib.sha256(json.dumps([(r.routed.alert.alert_id,r.routed.alert.arrival,r.routed.alert.task_class,r.severity,r.difficulty,r.routed.soctra_recommendation) for r in admitted],sort_keys=True).encode()).hexdigest()
  for policy in ('D1','P1'):
   sim=simulate_l1_l2(tuple(r.routed for r in generated),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,policy=policy,admission_horizon=H,drain_period=D,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
   first={j.alert_id:j for j in sim.l1_simulation.assignments};second={j.alert_id:j for j in sim.l2_simulation.assignments};route={r.alert_id:r.scenario_routing_decision for r in sim.escalation_records}
   assert len(first)==len(sim.l1_simulation.assignments) and len(second)==len(sim.l2_simulation.assignments)
   finals=[];l1busy={a.analyst_id:[] for a in l1}
   for j in first.values():l1busy[j.analyst_id].append((j.start,j.completion))
   for r in admitted:
    aid=r.routed.alert.alert_id
    finals.append((r,second.get(aid) if route.get(aid) else first.get(aid)))
   for cut in (H,H+D):
    done=[(r,j) for r,j in finals if j and j.completion<=cut]
    assert len(done)+sum(j is None or j.completion>cut for _,j in finals)==len(admitted)
    sla=sum(j.completion<=r.routed.alert.deadline for r,j in done)
    value=sum(j.competence*(1-.35*r.difficulty)*(j.completion<=r.routed.alert.deadline) for r,j in done)
    waits=[max(0.,min(first[r.routed.alert.alert_id].start if r.routed.alert.alert_id in first else cut,cut)-r.routed.alert.arrival) for r in admitted]
    q1=a0._queue_profile([r.routed.alert.arrival for r in admitted],[j.start for j in first.values()],cut)
    l2arr=[first[aid].completion for aid,escalate in route.items() if escalate and aid in first and first[aid].completion<cut]
    q2=a0._queue_profile(l2arr,[j.start for j in second.values()],cut)
    util1=[v for _,v in stage_metrics_at(sim.l1_simulation,cut)];util2=[v for _,v in stage_metrics_at(sim.l2_simulation,cut)]
    high=[r for r in admitted if r.severity=='high'];highblocked=0;highwaitbusy=0.
    for r in high:
     a=r.routed.alert;eligible=[i.analyst_id for i in l1 if a.task_class in i.eligible_classes]
     if eligible and all(any(x<=a.arrival<y for x,y in l1busy[i]) for i in eligible):highblocked+=1
     waitend=min(cut,first[a.alert_id].start if a.alert_id in first else cut)
     highwaitbusy+=a0._all_busy_duration(eligible,l1busy,a.arrival,waitend)
    rows.append(dict(scenario=sc['name'],family=sc['family'],rho=sc['rho'],deadline_multiplier=sc['deadline'],competence_spread=sc['spread'],seed=seed,policy=policy,cutoff_h=cut,trace_sha256=fingerprint,exogenous_sha256=exogenous,admitted=len(admitted),completed=len(done),pending=len(admitted)-len(done),R=value,R_per_admitted=value/len(admitted),sla=sla/len(admitted),quality_completed=statistics.mean(j.competence*(1-.35*r.difficulty) for r,j in done) if done else 0.,wait_l1_mean_h=statistics.mean(waits),wait_l1_p95_h=a0._quantile(waits,.95),queue_l1_mean=q1['queue_mean_time_weighted'],queue_l1_peak=q1['queue_peak'],queue_l2_mean=q2['queue_mean_time_weighted'],queue_l2_peak=q2['queue_peak'],util_l1=statistics.mean(util1),util_l2=statistics.mean(util2),high_arrivals=len(high),high_all_eligible_busy_at_arrival=highblocked,high_wait_all_eligible_busy_h=highwaitbusy))
    for kind in ('priority','class'):
     groups=sorted({r.severity if kind=='priority' else r.routed.alert.task_class for r in admitted})
     for group in groups:
      members=[(r,j) for r,j in finals if (r.severity if kind=='priority' else r.routed.alert.task_class)==group]
      completed=[(r,j) for r,j in members if j and j.completion<=cut]
      strata.append(dict(scenario=sc['name'],family=sc['family'],seed=seed,policy=policy,cutoff_h=cut,kind=kind,group=group,admitted=len(members),completed=len(completed),sla=sum(j.completion<=r.routed.alert.deadline for r,j in completed)/len(members),R_per_admitted=sum(j.competence*(1-.35*r.difficulty)*(j.completion<=r.routed.alert.deadline) for r,j in completed)/len(members)))
 print(sc['name'],'finished',round(time.perf_counter()-start,1),flush=True)
save('episodes.csv',rows);save('strata.csv',strata)
paired=[];summary=[]
metrics=['R_per_admitted','sla','quality_completed','wait_l1_mean_h','wait_l1_p95_h','queue_l1_mean','queue_l1_peak','queue_l2_mean','queue_l2_peak','util_l1','util_l2','pending','completed','high_all_eligible_busy_at_arrival','high_wait_all_eligible_busy_h']
for sc in scenarios:
 for cut in (H,H+D):
  base={r['seed']:r for r in rows if r['scenario']==sc['name'] and r['policy']=='D1' and r['cutoff_h']==cut}
  alt={r['seed']:r for r in rows if r['scenario']==sc['name'] and r['policy']=='P1' and r['cutoff_h']==cut}
  assert set(base)==set(alt)==set(seeds)
  for seed in seeds:
   b,a=base[seed],alt[seed]
   assert b['trace_sha256']==a['trace_sha256'] and b['admitted']==a['admitted']
   paired.append(dict(scenario=sc['name'],seed=seed,cutoff_h=cut,trace_sha256=b['trace_sha256'],R_D1=b['R_per_admitted'],R_P1=a['R_per_admitted'],delta_R=a['R_per_admitted']-b['R_per_admitted'],sla_D1=b['sla'],sla_P1=a['sla'],delta_sla=a['sla']-b['sla']))
  for metric in metrics:
   x=[alt[k][metric]-base[k][metric] for k in seeds]
   dm,ds,lo,hi=ci(x)
   for pol,group in [('D1',base),('P1',alt)]:
    mean,sd,ml,mh=ci([group[k][metric] for k in seeds])
    summary.append(dict(scenario=sc['name'],family=sc['family'],rho=sc['rho'],deadline_multiplier=sc['deadline'],competence_spread=sc['spread'],cutoff_h=cut,metric=metric,policy=pol,mean=mean,sd=sd,mean_ci_low=ml,mean_ci_high=mh,delta_p1_d1=dm,delta_sd=ds,delta_ci_low=lo,delta_ci_high=hi,positive_n=sum(v>0 for v in x),negative_n=sum(v<0 for v in x),equal_n=sum(v==0 for v in x)))
save('paired.csv',paired);save('summary.csv',summary)
primary=[r['delta_R'] for r in paired if r['scenario']=='rho_125_primary' and r['cutoff_h']==H+D]
mean,sd,lo,hi=ci(primary);tstat=mean/(sd/math.sqrt(len(primary)));p=float(student_t.sf(tstat,len(primary)-1))
secondary=[]
for sc in scenarios[1:]:
 x=[r['delta_R'] for r in paired if r['scenario']==sc['name'] and r['cutoff_h']==H+D]
 m,s,l,h=ci(x);stat=m/(s/math.sqrt(len(x)));pv=2*float(student_t.sf(abs(stat),len(x)-1))
 secondary.append(dict(scenario=sc['name'],delta=m,ci_low=l,ci_high=h,p_two_sided=pv))
order=sorted(range(len(secondary)),key=lambda i:secondary[i]['p_two_sided']);running=0.
for rank,i in enumerate(order):
 running=max(running,min(1.,(len(order)-rank)*secondary[i]['p_two_sided']))
 secondary[i]['holm_adjusted_p']=running
(OUT/'test_results.json').write_text(json.dumps(dict(primary=dict(n=100,mean_delta=mean,sd_delta=sd,ci_low=lo,ci_high=hi,t=tstat,df=99,p_one_sided=p,positive_n=sum(v>0 for v in primary),negative_n=sum(v<0 for v in primary),relative_effect=mean/statistics.mean(r['R_D1'] for r in paired if r['scenario']=='rho_125_primary' and r['cutoff_h']==H+D)),secondary=secondary),indent=2))
(OUT/'run_metadata.json').write_text(json.dumps(dict(config=CFG,scenarios=scenarios,episode_policy_runs=len(rows)//2,runtime_s=time.perf_counter()-start,source='run_soc_confirmatory.py',paired_trace_check=True),indent=2))
print('PRIMARY',json.dumps(json.loads((OUT/'test_results.json').read_text())['primary']),flush=True)
