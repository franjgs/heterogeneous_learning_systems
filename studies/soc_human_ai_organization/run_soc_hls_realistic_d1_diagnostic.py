"""D1-only profile qualification before the paired policy pilot."""
import csv,json,sys,hashlib
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity
HERE=Path(__file__).resolve().parent;C=json.loads((HERE/'config/soc_hls_realistic_dynamics.json').read_text());OUT=ROOT/'results/soc_hls_realistic_dynamics';OUT.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];rows=[];series=[]
for p in C['profiles']:
 for seed in range(C['seed_base'],C['seed_base']+C['seed_count']):
  gen=[]
  for i,(a,b,rho) in enumerate(p['segments']):
   cfg=replace(REFERENCE.scenario_config(arrival_rate_per_h=mu*rho),horizon=b-a)
   for j,x in enumerate(generate_alerts(cfg,seed*100+i)):
    alert=x.routed.alert;alert=replace(alert,alert_id=f'{i:02d}-{j:08d}',arrival=alert.arrival+a,deadline=alert.deadline+a)
    gen.append(replace(x,routed=replace(x.routed,alert=alert)))
  sim=simulate_l1_l2(tuple(x.routed for x in gen),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,policy='D1',admission_horizon=C['horizon_h'],drain_period=C['drain_h'],coordination_latency=0.,random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2,decision_mode='hypothetical_recommendation_acceptance')
  first={x.alert_id:x for x in sim.l1_simulation.assignments};second={x.alert_id:x for x in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records};alerts=[x for x in gen if x.routed.alert.arrival<C['horizon_h']]
  l1jobs={x.alert_id:x for x in sim.l1_simulation.assignments};l2jobs={x.alert_id:x for x in sim.l2_simulation.assignments};routes={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
  rn=sum((l2jobs.get(x.routed.alert.alert_id) if routes[x.routed.alert.alert_id] else l1jobs.get(x.routed.alert.alert_id)).competence*(1-.35*x.difficulty) for x in alerts if (l2jobs.get(x.routed.alert.alert_id) if routes[x.routed.alert.alert_id] else l1jobs.get(x.routed.alert.alert_id)) and (l2jobs.get(x.routed.alert.alert_id) if routes[x.routed.alert.alert_id] else l1jobs.get(x.routed.alert.alert_id)).completion<=72 and (l2jobs.get(x.routed.alert.alert_id) if routes[x.routed.alert.alert_id] else l1jobs.get(x.routed.alert.alert_id)).completion<=x.routed.alert.deadline)/len(alerts)
  rows.append(dict(profile=p['name'],seed=seed,admitted=len(alerts),pending_H=sim.at_horizon.pending,backlog_HD=sim.after_drain.pending,l1_backlog_H=sim.at_horizon.l1_backlog,l2_backlog_H=sim.at_horizon.l2_backlog,l1_backlog_HD=sim.after_drain.l1_backlog,l2_backlog_HD=sim.after_drain.l2_backlog,rn=rn,sla=sim.after_drain.fraction_within_sla))
  for t in range(37):
   q=[x for x in alerts if x.routed.alert.arrival<t and (x.routed.alert.alert_id not in first or first[x.routed.alert.alert_id].start>=t)]
   work=sum(BASE_SERVICE_L1_H[x.routed.alert.task_class] for x in q)
   active=sum(any(a.analyst_id==who and a.start<t<a.completion for a in first.values()) for who in [x.analyst_id for x in l1])
   expired=sum(x.routed.alert.deadline<=t for x in q)
   series.append(dict(profile=p['name'],seed=seed,time_h=t,queue_l1=len(q),pending_work_l1_h=work,active_l1=active,l1_occupancy=active/len(l1),expired_pending=expired))
  print(p['name'],seed,'D1 diagnostic complete',flush=True)
for fn,data in [('d1_diagnostic.csv',rows),('d1_timeseries.csv',series)]:
 with (OUT/fn).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
print('D1-only profiles qualified')
