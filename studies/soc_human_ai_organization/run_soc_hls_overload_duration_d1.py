"""D1-only physical qualification for the overload-duration sweep."""
import csv,json,sys,hashlib
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;C=json.loads((HERE/'config/soc_hls_overload_duration.json').read_text());OUT=ROOT/'results/soc_hls_overload_duration';OUT.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h']
def trace(duration,seed):
 bounds=[(0,4,.85),(4,4+duration,1.25),(4+duration,24,.85)];out=[]
 for i,(a,b,rho) in enumerate(bounds):
  cfg=replace(REFERENCE.scenario_config(arrival_rate_per_h=mu*rho),horizon=b-a)
  for j,x in enumerate(generate_alerts(cfg,seed*100+i)):
   al=x.routed.alert;al=replace(al,alert_id=f'{i:02d}-{j:08d}',arrival=al.arrival+a,deadline=al.deadline+a)
   out.append(replace(x,routed=replace(x.routed,alert=al)))
 return tuple(sorted(out,key=lambda x:(x.routed.alert.arrival,x.routed.alert.alert_id)))
diag=[];series=[];fingerprints=[]
for d in C['durations_h']:
 for seed in range(C['seed_base'],C['seed_base']+C['seed_count']):
  gen=trace(d,seed);adm=[x for x in gen if x.routed.alert.arrival<24];fp=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation,x.difficulty) for x in adm);hashv=hashlib.sha256(repr(fp).encode()).hexdigest();fingerprints.append((d,seed,hashv,len(adm)))
  sim=simulate_l1_l2(tuple(x.routed for x in gen),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,policy='D1',admission_horizon=24.,drain_period=24.,coordination_latency=0.,random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2,decision_mode='hypothetical_recommendation_acceptance')
  aa={x.alert_id:x for x in sim.l1_simulation.assignments};bb={x.alert_id:x for x in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
  finals={x.routed.alert.alert_id:(bb.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else aa.get(x.routed.alert.alert_id)) for x in adm}
  run=sim.after_drain
  rn=sum((bb.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else aa.get(x.routed.alert.alert_id)).competence*(1-.35*x.difficulty) for x in adm if (bb.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else aa.get(x.routed.alert.alert_id)) and (bb.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else aa.get(x.routed.alert.alert_id)).completion<=48 and (bb.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else aa.get(x.routed.alert.alert_id)).completion<=x.routed.alert.deadline)/len(adm)
  pulse=[x for x in adm if 4<=x.routed.alert.arrival<4+d]
  pulse_done=sum(bool(finals[x.routed.alert.alert_id] and finals[x.routed.alert.alert_id].completion<=72) for x in pulse)
  diag.append(dict(duration_h=d,seed=seed,trace_sha256=hashv,admitted=len(adm),pulse_arrivals=len(pulse),pulse_expected=mu*1.25*d,pending_H=sim.at_horizon.pending,pending_HD=run.pending,l1_backlog_H=sim.at_horizon.l1_backlog,l2_backlog_H=sim.at_horizon.l2_backlog,l1_backlog_HD=run.l1_backlog,l2_backlog_HD=run.l2_backlog,rn=rn,sla=run.fraction_within_sla))
  for t in [x/2 for x in range(97)]:
   # At H+D, no later arrivals; queued tasks remain visibly pending.
   l1q=[x for x in adm if x.routed.alert.arrival<t and (x.routed.alert.alert_id not in aa or aa[x.routed.alert.alert_id].start>=t)]
   l2q=[x for x in adm if route[x.routed.alert.alert_id] and x.routed.alert.alert_id in aa and aa[x.routed.alert.alert_id].completion<t and (x.routed.alert.alert_id not in bb or bb[x.routed.alert.alert_id].start>=t)]
   def recoverable(rows,service,roster):
    ok=0;expired=0
    for x in rows:
     a=x.routed.alert
     if a.deadline<=t:expired+=1;continue
     fastest=min((service.get(w.analyst_id,{}).get(a.task_class,float('inf')) for w in roster if a.task_class in w.eligible_classes),default=float('inf'))
     ok+=a.deadline>=t+fastest
    return ok,expired
   r1,e1=recoverable(l1q,s1,l1);r2,e2=recoverable(l2q,s2,l2)
   active1=sum(any(a.analyst_id==w.analyst_id and a.start<t<a.completion for a in aa.values()) for w in l1);active2=sum(any(a.analyst_id==w.analyst_id and a.start<t<a.completion for a in bb.values()) for w in l2)
   work1=sum(BASE_SERVICE_L1_H[x.routed.alert.task_class] for x in l1q);work2=sum(BASE_SERVICE_L2_H[x.routed.alert.task_class] for x in l2q)
   series.append(dict(duration_h=d,seed=seed,time_h=t,rho=(.85 if t<4 or t>=4+d else 1.25),queue_l1=len(l1q),queue_l2=len(l2q),work_l1_h=work1,work_l2_h=work2,active_l1=active1,active_l2=active2,recoverable_l1=r1,expired_l1=e1,recoverable_l2=r2,expired_l2=e2))
  print(d,seed,'D1 diagnostic complete',flush=True)
for f,rows in [('d1.csv',diag),('d1_timeseries.csv',series)]:
 with (OUT/f).open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(OUT/'trace_manifest.json').write_text(json.dumps([dict(duration_h=d,seed=s,sha256=h,n=n) for d,s,h,n in fingerprints],indent=2))
(OUT/'physical_metadata.json').write_text(json.dumps(dict(mu_l1=mu,expected_arrivals_by_duration={str(d):mu*(.85*24+.4*d) for d in C['durations_h']},config=C),indent=2))
