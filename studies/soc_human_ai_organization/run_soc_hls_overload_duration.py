"""Paired complete-episode policy comparison; no snapshots or branches."""
import csv,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;C=json.loads((HERE/'config/soc_hls_overload_duration.json').read_text());OUT=ROOT/'results/soc_hls_overload_duration'
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];_,mix2=routed_l2_shares();mu2=effective_capacity(l2,s2,mix2)['max_common_arrivals_per_h']
def trace(duration,seed):
 out=[]
 for i,(a,b,rho) in enumerate(((0,4,.85),(4,4+duration,1.25),(4+duration,24,.85))):
  cfg=__import__('dataclasses').replace(REFERENCE.scenario_config(arrival_rate_per_h=mu*rho),horizon=b-a)
  for j,x in enumerate(generate_alerts(cfg,seed*100+i)):
   al=x.routed.alert;al=__import__('dataclasses').replace(al,alert_id=f'{i:02d}-{j:08d}',arrival=al.arrival+a,deadline=al.deadline+a)
   out.append(__import__('dataclasses').replace(x,routed=__import__('dataclasses').replace(x.routed,alert=al)))
 return tuple(sorted(out,key=lambda x:(x.routed.alert.arrival,x.routed.alert.alert_id)))
episodes=[];cohorts=[];series=[];modes=[]
for d in C['durations_h']:
 for seed in range(C['seed_base'],C['seed_base']+C['seed_count']):
  gen=trace(d,seed);adm=[x for x in gen if x.routed.alert.arrival<24];fp=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation,x.difficulty) for x in adm);digest=hashlib.sha256(repr(fp).encode()).hexdigest();n=len(adm)
  old=next(x for x in csv.DictReader((OUT/'trace_manifest.json').open()) ) if False else None
  for policy in ('D1','P1','HLS-B'):
   kw=dict(policy=policy,admission_horizon=24.,drain_period=24.,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
   if policy=='HLS-B':kw.update(hlsb_l1_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu),hlsb_l2_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu2))
   sim=simulate_l1_l2(tuple(x.routed for x in gen),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
   a={z.alert_id:z for z in sim.l1_simulation.assignments};b={z.alert_id:z for z in sim.l2_simulation.assignments};route={z.alert_id:z.scenario_routing_decision for z in sim.escalation_records};final={x.routed.alert.alert_id:(b.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else a.get(x.routed.alert.alert_id)) for x in adm}
   assert len(a)==len(sim.l1_simulation.assignments) and len(set(a))==len(a)
   def metrics(cut,group):
    done=[x for x in group if final[x.routed.alert.alert_id] and final[x.routed.alert.alert_id].completion<=cut]
    on=[x for x in done if final[x.routed.alert.alert_id].completion<=x.routed.alert.deadline]
    rn=sum(final[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in on)/len(group)
    quality=sum(final[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in done)/len(done) if done else 0
    return len(done),len(on),rn,quality
   for cut in (24.,48.):
    done,on,rn,q=metrics(cut,adm)
    episodes.append(dict(duration_h=d,seed=seed,policy=policy,cutoff_h=cut,trace_sha256=digest,admitted=n,completed=done,pending=n-done,RN=rn,SLA=on/n,quality_completed=q,mean_completion_h=sum(final[x.routed.alert.alert_id].completion for x in [z for z in adm if final[z.routed.alert.alert_id] and final[z.routed.alert.alert_id].completion<=cut])/done if done else 0,l1_backlog=sim.at_horizon.l1_backlog if cut==24 else sim.after_drain.l1_backlog,l2_backlog=sim.at_horizon.l2_backlog if cut==24 else sim.after_drain.l2_backlog))
   for ci,(lo,hi,label) in enumerate(((0,4,'pre'),(4,4+d,'pulse'),(4+d,24,'post'))):
    group=[x for x in adm if lo<=x.routed.alert.arrival<hi];done,on,rn,q=metrics(48.,group)
    cohorts.append(dict(duration_h=d,seed=seed,policy=policy,cohort=label,start_h=lo,end_h=hi,admitted=len(group),completed=done,RN=rn,SLA=on/len(group)))
   hist=sim.l1_simulation.hlsa_history
   for z in hist:modes.append(dict(duration_h=d,seed=seed,policy=policy,time_h=z.time,mode=z.mode,switched=z.switched,pending=z.pending,occupied=z.occupied,pressure=z.pressure))
   for t in [i/2 for i in range(97)]:
    q1=[x for x in adm if x.routed.alert.arrival<t and (x.routed.alert.alert_id not in a or a[x.routed.alert.alert_id].start>=t)]
    q2=[x for x in adm if route[x.routed.alert.alert_id] and x.routed.alert.alert_id in a and a[x.routed.alert.alert_id].completion<t and (x.routed.alert.alert_id not in b or b[x.routed.alert.alert_id].start>=t)]
    busy1=sum(any(z.analyst_id==w.analyst_id and z.start<t<z.completion for z in a.values()) for w in l1);busy2=sum(any(z.analyst_id==w.analyst_id and z.start<t<z.completion for z in b.values()) for w in l2)
    work1=sum(BASE_SERVICE_L1_H[x.routed.alert.task_class] for x in q1);work2=sum(BASE_SERVICE_L2_H[x.routed.alert.task_class] for x in q2)
    series.append(dict(duration_h=d,seed=seed,policy=policy,time_h=t,rho=.85 if t<4 or t>=4+d else 1.25,queue_l1=len(q1),queue_l2=len(q2),work_l1_h=work1,work_l2_h=work2,active_l1=busy1,active_l2=busy2))
  print('duration',d,'seed',seed,'complete',flush=True)
for f,rows in [('episodes.csv',episodes),('cohorts.csv',cohorts),('timeseries.csv',series),('modes.csv',modes)]:
 with (OUT/f).open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print('saved',len(episodes),'episode cutoff rows',len(series),'series rows',flush=True)
