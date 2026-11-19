"""Exact-engine HLS-A diagnostic on the frozen development seeds."""
import csv, json, sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSAConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H
HERE=Path(__file__).resolve().parent;cfg=json.loads((HERE/'config/soc_hlsa_pilot.json').read_text());out=ROOT/'results/soc_hlsa_pilot';out.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);rows=[]; checks=[]
old={(x['scenario'],int(x['seed'])):x for x in csv.DictReader((out/'episodes.csv').open()) if x['policy']=='HLS-A_2.0_3.0'}
for sc in cfg['scenarios']:
 if sc['name']=='steady_085':continue
 base=replace(REFERENCE.scenario_config(arrival_rate_per_h=cfg['base_capacity_alerts_per_h']*sc['base_rho']),horizon=24.)
 if 'burst_window_h' in sc:a,b=sc['burst_window_h'];base=replace(base,burst_window=(a,b,sc['burst_rho']/sc['base_rho']))
 if 'shift_h' in sc:base=replace(base,arrival_rate_shift_after=sc['shift_h'],arrival_rate_after=cfg['base_capacity_alerts_per_h']*sc['after_rho'])
 for seed in cfg['seeds']:
  gen=generate_alerts(base,seed);meta={x.routed.alert.alert_id:x for x in gen};l1trace=[];l2trace=[]
  kw=dict(policy='HLS-A',admission_horizon=24.,drain_period=24.,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2,hlsa_config=HLSAConfig(2.,3.))
  args=(tuple(x.routed for x in gen),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H)
  sim=simulate_l1_l2(*args,**kw,l1_diagnostic_trace=l1trace,l2_diagnostic_trace=l2trace)
  plain=simulate_l1_l2(*args,**kw)
  assert sim==plain
  assert len(l1trace)==len(sim.l1_simulation.hlsa_history) and len(l2trace)==len(sim.l2_simulation.hlsa_history)
  first={x.alert_id:x for x in sim.l1_simulation.assignments};second={x.alert_id:x for x in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records};admitted=[x for x in gen if x.routed.alert.arrival<24]
  rn=sum(j.competence*(1-.35*x.difficulty)*int(j.completion<=x.routed.alert.deadline) for x in admitted for j in [second.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else first.get(x.routed.alert.alert_id)] if j and j.completion<=48)/len(admitted)
  assert abs(rn-float(old[(sc['name'],seed)]['R_per_admitted']))<1e-12
  checks.append(dict(scenario=sc['name'],seed=seed,l1_epochs=len(l1trace),l2_epochs=len(l2trace),rn=rn))
  for pool,trace in [('L1',l1trace),('L2',l2trace)]:
   for item in trace:
    item=dict(item);item['scenario']=sc['name'];item['seed']=seed;item['pool']=pool
    item['priorities']={aid:meta[aid].severity for aid,_,_,_ in item['pending']}
    rows.append(item)
with (out/'direct_diagnostic.jsonl').open('w') as f:
 for item in rows:f.write(json.dumps(item)+'\n')
with (out/'direct_equivalence.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=checks[0].keys());w.writeheader();w.writerows(checks)
print('verified episodes',len(checks),'direct epochs',len(rows),'L1',sum(x['pool']=='L1' for x in rows),'L2',sum(x['pool']=='L2' for x in rows))
