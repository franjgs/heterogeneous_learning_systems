"""Reproducible development comparison; never uses nominal rho in a policy."""
import csv,hashlib,json,statistics,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSAConfig,HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;cfg=json.loads((HERE/'config/soc_hlsb_development.json').read_text());out=ROOT/'results/soc_hlsb_development';out.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu1=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];_,mix2=routed_l2_shares();mu2=effective_capacity(l2,s2,mix2)['max_common_arrivals_per_h']
rows=[];modes=[]
for sc in cfg['scenarios']:
 base=replace(REFERENCE.scenario_config(arrival_rate_per_h=mu1*sc['base_rho']),horizon=cfg['horizon_h'])
 if 'shift_h' in sc:base=replace(base,arrival_rate_shift_after=sc['shift_h'],arrival_rate_after=mu1*sc['after_rho'])
 for seed in cfg['seeds']:
  generated=generate_alerts(base,seed);admitted=[x for x in generated if x.routed.alert.arrival<24];fingerprint=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation) for x in admitted);trace_sha=hashlib.sha256(repr(fingerprint).encode()).hexdigest()
  for label,variant in [('D1',None),('P1',None),('HLS-A',None)]+[(f"HLS-B_{x['window_h']}_{x['low']}_{x['high']}",x) for x in cfg['candidates']]:
   policy='HLS-B' if variant else label
   kw=dict(policy=policy,admission_horizon=24.,drain_period=24.,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2,hlsa_config=HLSAConfig(2.,3.))
   if variant:kw.update(hlsb_l1_config=HLSBConfig(**variant,capacity_per_h=mu1),hlsb_l2_config=HLSBConfig(**variant,capacity_per_h=mu2))
   sim=simulate_l1_l2(tuple(x.routed for x in generated),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
   first={a.alert_id:a for a in sim.l1_simulation.assignments};second={a.alert_id:a for a in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
   final=[(x,second.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else first.get(x.routed.alert.alert_id)) for x in admitted]
   n=len(admitted);R=sum(a.competence*(1-.35*x.difficulty) for x,a in final if a and a.completion<=48 and a.completion<=x.routed.alert.deadline)
   history=sim.l1_simulation.hlsa_history;switches=sum(x.switched for x in history)
   for x in history:modes.append(dict(scenario=sc['name'],seed=seed,policy=label,time_h=x.time,mode=x.mode,rho_est=x.pressure,switched=x.switched))
   rows.append(dict(scenario=sc['name'],seed=seed,policy=label,trace_sha256=trace_sha,admitted=n,R_per_admitted=R/n,sla=sum(a is not None and a.completion<=48 and a.completion<=x.routed.alert.deadline for x,a in final)/n,quality_completed=statistics.mean(a.competence*(1-.35*x.difficulty) for x,a in final if a and a.completion<=48),switches=switches,p1_share=sum(x.mode=='P1' for x in history)/len(history) if history else 0.,trace_count=len(fingerprint)))
 print(sc['name'],'complete',flush=True)
for name,data in [('episodes.csv',rows),('modes.csv',modes)]:
 with (out/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
(out/'capacity.json').write_text(json.dumps(dict(l1_capacity_per_h=mu1,l2_capacity_per_h=mu2,l2_mix=mix2),indent=2))
for sc in cfg['scenarios']:
 for label in sorted(set(x['policy'] for x in rows)):
  group=[x for x in rows if x['scenario']==sc['name'] and x['policy']==label]
  print(sc['name'],label,round(statistics.mean(x['R_per_admitted'] for x in group),4),round(statistics.mean(x['switches'] for x in group),2),flush=True)
