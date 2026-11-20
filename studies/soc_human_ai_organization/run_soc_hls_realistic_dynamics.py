"""Complete paired episodes for three demand perturbation profiles."""
import csv,hashlib,json,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2,stage_metrics_at
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;C=json.loads((HERE/'config/soc_hls_realistic_dynamics.json').read_text());OUT=ROOT/'results/soc_hls_realistic_dynamics';OUT.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu1=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];_,mix2=routed_l2_shares();mu2=effective_capacity(l2,s2,mix2)['max_common_arrivals_per_h']
H=C['horizon_h'];D=C['drain_h'];seeds=range(C['seed_base'],C['seed_base']+C['seed_count']);episodes=[];cohorts=[];series=[];modes=[];traces={}
def rho_at(profile,t):
 return next(r for a,b,r in profile['segments'] if a<=t<b)
for profile in C['profiles']:
 for seed in seeds:
  generated=[]
  for ix,(start,end,rho) in enumerate(profile['segments']):
   cfg=replace(REFERENCE.scenario_config(arrival_rate_per_h=mu1*rho),horizon=end-start)
   for j,x in enumerate(generate_alerts(cfg,seed*100+ix)):
    a=x.routed.alert;a=replace(a,alert_id=f'{ix:02d}-{j:08d}',arrival=a.arrival+start,deadline=a.deadline+start)
    generated.append(replace(x,routed=replace(x.routed,alert=a)))
  generated=tuple(sorted(generated,key=lambda x:(x.routed.alert.arrival,x.routed.alert.alert_id)))
  admitted=[x for x in generated if x.routed.alert.arrival<H]
  fingerprint=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation,x.difficulty) for x in admitted)
  trace=hashlib.sha256(repr(fingerprint).encode()).hexdigest();traces[(profile['name'],seed)]=trace
  for policy in ('D1','P1','HLS-B'):
   kw=dict(policy=policy,admission_horizon=H,drain_period=D,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
   if policy=='HLS-B':kw.update(hlsb_l1_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu1),hlsb_l2_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu2))
   sim=simulate_l1_l2(tuple(x.routed for x in generated),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
   first={a.alert_id:a for a in sim.l1_simulation.assignments};second={a.alert_id:a for a in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
   finals={x.routed.alert.alert_id:(second.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else first.get(x.routed.alert.alert_id)) for x in admitted};n=len(admitted)
   def rn(cut,group=admitted):
    return sum(finals[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in group if finals[x.routed.alert.alert_id] and finals[x.routed.alert.alert_id].completion<=cut and finals[x.routed.alert.alert_id].completion<=x.routed.alert.deadline)/len(group)
   for cut in (H,H+D):
    ontime=[x for x in admitted if finals[x.routed.alert.alert_id] and finals[x.routed.alert.alert_id].completion<=cut and finals[x.routed.alert.alert_id].completion<=x.routed.alert.deadline]
    done=[x for x in admitted if finals[x.routed.alert.alert_id] and finals[x.routed.alert.alert_id].completion<=cut]
    episodes.append(dict(profile=profile['name'],seed=seed,policy=policy,cutoff_h=cut,trace_sha256=trace,admitted=n,completed=len(done),pending=n-len(done),rn=rn(cut),sla=len(ontime)/n,quality_completed=sum(finals[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in done)/len(done) if done else 0,mean_completion_h=sum(finals[x.routed.alert.alert_id].completion for x in done)/len(done) if done else 0))
   for seg_i,(start,end,rho) in enumerate(profile['segments']):
    group=[x for x in admitted if start<=x.routed.alert.arrival<end]
    cohorts.append(dict(profile=profile['name'],seed=seed,policy=policy,segment=seg_i,rho=rho,start_h=start,end_h=end,admitted=len(group),rn=rn(H+D,group)))
   history=sim.l1_simulation.hlsa_history
   for e in history:modes.append(dict(profile=profile['name'],seed=seed,policy=policy,time_h=e.time,mode=e.mode,estimate=e.pressure,switched=e.switched,pending=e.pending,occupied=e.occupied))
   for t in range(0,int(H+D)+1):
    queued=[x for x in admitted if x.routed.alert.arrival<t and (x.routed.alert.alert_id not in first or first[x.routed.alert.alert_id].start>=t)]
    work=sum(BASE_SERVICE_L1_H[x.routed.alert.task_class] for x in queued)
    active=sum(a.start<t<a.completion for a in first.values())
    l2q=sum(1 for aid,yes in route.items() if yes and aid in first and first[aid].completion<t and (aid not in second or second[aid].start>=t))
    l1busy=sum(any(a.analyst_id==who and a.start<t<a.completion for a in first.values()) for who in [a.analyst_id for a in l1]);l1util=l1busy/len(l1)
    l2busy=sum(any(a.analyst_id==who and a.start<t<a.completion for a in second.values()) for who in [a.analyst_id for a in l2]);l2util=l2busy/len(l2)
    sla_recoverable=sum(x.routed.alert.deadline>t for x in queued)
    expired=len(queued)-sla_recoverable
    mode=next((e.mode for e in reversed(history) if e.time<=t),'D1')
    series.append(dict(profile=profile['name'],seed=seed,policy=policy,time_h=t,rho=rho_at(profile,t) if t<H else 0,queue_l1=len(queued),work_l1_h=work,active_l1=active,queue_l2=l2q,l1_occupancy=l1util,l2_occupancy=l2util,recoverable=sla_recoverable,expired=expired,mode=mode))
  print(profile['name'],'seed',seed,'complete',flush=True)
for fn,data in [('episodes.csv',episodes),('cohorts.csv',cohorts),('timeseries.csv',series),('modes.csv',modes)]:
 with (OUT/fn).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
assert len(set(traces.values()))==len(traces)
(OUT/'metadata.json').write_text(json.dumps(dict(config=C,mu_l1=mu1,mu_l2=mu2,trace_pairs=len(traces),policy_episodes=len(episodes)),indent=2))
print('saved',len(episodes),'cut rows,',len(series),'time rows',flush=True)
