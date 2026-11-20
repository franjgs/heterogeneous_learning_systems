"""Complete-episode operating-domain sweep with common exogenous traces."""
import csv,hashlib,json,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;C=json.loads((HERE/'config/soc_hls_operating_regions.json').read_text());OUT=ROOT/'results/soc_hls_operating_regions';OUT.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];_,mix2=routed_l2_shares();mu2=effective_capacity(l2,s2,mix2)['max_common_arrivals_per_h']
H=C['admission_h'];D=C['drain_h'];episodes=[];cohorts=[];priority=[];modes=[];series=[];manifest=[]
def make_trace(profile,seed,deadline_map=None):
 start=C['pulse_start_h'];end=start+profile['duration_h'];segments=((0,start,C['rho_normal']),(start,end,profile['rho_high']),(end,H,profile['rho_recovery']))
 out=[]
 for i,(lo,hi,rho) in enumerate(segments):
  cfg=replace(REFERENCE.scenario_config(arrival_rate_per_h=mu*rho),horizon=hi-lo,deadline_by_severity=tuple((k,(deadline_map or C['deadline_h'])[k]) for k in ('low','medium','high')))
  for j,x in enumerate(generate_alerts(cfg,seed*100+i)):
   a=x.routed.alert;a=replace(a,alert_id=f'{i:02d}-{j:08d}',arrival=a.arrival+lo,deadline=a.deadline+lo)
   out.append(replace(x,routed=replace(x.routed,alert=a)))
 return tuple(sorted(out,key=lambda z:(z.routed.alert.arrival,z.routed.alert.alert_id)))
for p in C['profiles']:
 for seed in range(C['seed_base'],C['seed_base']+C['seed_count']):
  gen=make_trace(p,seed);adm=[x for x in gen if x.routed.alert.arrival<H];finger=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation,x.severity,x.difficulty) for x in adm);digest=hashlib.sha256(repr(finger).encode()).hexdigest();manifest.append(dict(profile=p['name'],seed=seed,hash=digest,admitted=len(adm)))
  for pol in ('D1','P1','HLS-B'):
   kw=dict(policy=pol,admission_horizon=H,drain_period=D,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
   if pol=='HLS-B':kw.update(hlsb_l1_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu),hlsb_l2_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu2))
   sim=simulate_l1_l2(tuple(x.routed for x in gen),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
   l1j={x.alert_id:x for x in sim.l1_simulation.assignments};l2j={x.alert_id:x for x in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
   finals={x.routed.alert.alert_id:(l2j.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else l1j.get(x.routed.alert.alert_id)) for x in adm}
   def calc(group,cut):
    done=[x for x in group if finals[x.routed.alert.alert_id] and finals[x.routed.alert.alert_id].completion<=cut]
    timely=[x for x in done if finals[x.routed.alert.alert_id].completion<=x.routed.alert.deadline]
    return len(done),len(timely),sum(finals[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in timely)/len(group),sum(finals[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in done)/len(done) if done else 0.,sum(finals[x.routed.alert.alert_id].completion for x in done)/len(done) if done else 0.
   for cut in (H,H+D):
    done,ontime,rn,q,fc=calc(adm,cut);m=sim.at_horizon if cut==H else sim.after_drain
    episodes.append(dict(profile=p['name'],design_group=p['design_group'],rho_high=p['rho_high'],duration_h=p['duration_h'],rho_recovery=p['rho_recovery'],B=(p['rho_high']-1)*p['duration_h'],Gamma=(p['rho_high']-1)*p['duration_h']/((1-C['rho_normal'])*(H-C['pulse_start_h']-p['duration_h'])) if H>C['pulse_start_h']+p['duration_h'] else '',seed=seed,policy=pol,cutoff_h=cut,trace_sha256=digest,admitted=len(adm),completed=done,pending=len(adm)-done,RN=rn,SLA=ontime/len(adm),quality_completed=q,mean_completion_h=fc,l1_backlog=m.l1_backlog,l2_backlog=m.l2_backlog))
   for co,lo,hi in (('pre',0,C['pulse_start_h']),('pulse',C['pulse_start_h'],C['pulse_start_h']+p['duration_h']),('post',C['pulse_start_h']+p['duration_h'],H)):
    group=[x for x in adm if lo<=x.routed.alert.arrival<hi];done,on,rn,q,fc=calc(group,H+D);cohorts.append(dict(profile=p['name'],seed=seed,policy=pol,cohort=co,start_h=lo,end_h=hi,n=len(group),RN=rn,SLA=on/len(group)))
   for severity in ('high','medium','low'):
    group=[x for x in adm if x.severity==severity];done,on,rn,q,fc=calc(group,H+D);priority.append(dict(profile=p['name'],seed=seed,policy=pol,priority=severity,n=len(group),RN=rn,SLA=on/len(group),quality_completed=q))
   hist=sim.l1_simulation.hlsa_history
   for z in hist:modes.append(dict(profile=p['name'],seed=seed,policy=pol,time_h=z.time,mode=z.mode,switched=z.switched,pressure=z.pressure,pending=z.pending,occupied=z.occupied))
   for i in range(49):
    t=i*.5;q1=[x for x in adm if x.routed.alert.arrival<t and (x.routed.alert.alert_id not in l1j or l1j[x.routed.alert.alert_id].start>=t)]
    q2=[x for x in adm if route[x.routed.alert.alert_id] and x.routed.alert.alert_id in l1j and l1j[x.routed.alert.alert_id].completion<t and (x.routed.alert.alert_id not in l2j or l2j[x.routed.alert.alert_id].start>=t)]
    work1=sum(BASE_SERVICE_L1_H[x.routed.alert.task_class] for x in q1);work2=sum(BASE_SERVICE_L2_H[x.routed.alert.task_class] for x in q2)
    busy1=sum(any(a.analyst_id==w.analyst_id and a.start<t<a.completion for a in l1j.values()) for w in l1);busy2=sum(any(a.analyst_id==w.analyst_id and a.start<t<a.completion for a in l2j.values()) for w in l2)
    series.append(dict(profile=p['name'],seed=seed,policy=pol,time_h=t,rho=C['rho_normal'] if t<4 or t>=4+p['duration_h'] else p['rho_high'],queue_l1=len(q1),queue_l2=len(q2),work_l1_h=work1,work_l2_h=work2,occupied_l1=busy1,occupied_l2=busy2))
  print(p['name'],seed,'complete',flush=True)
for f,data in [('episodes.csv',episodes),('cohorts.csv',cohorts),('priority.csv',priority),('timeseries.csv',series),('modes.csv',modes)]:
 with (OUT/f).open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'metadata.json').write_text(json.dumps(dict(config=C,mu_l1=mu,mu_l2=mu2,episodes=len(episodes),seed_design='same seed ids across scenarios; paired within scenario only; scenario-level inference does not pool profiles'),indent=2))
print('saved',len(episodes),'cutoff rows',len(series),'series rows',flush=True)
