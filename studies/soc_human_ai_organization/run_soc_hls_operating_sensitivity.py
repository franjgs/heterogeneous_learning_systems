"""Selected SLA and staffing sensitivities on complete paired episodes."""
import csv,hashlib,json,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX,build_roster
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;C=json.loads((HERE/'config/soc_hls_operating_sensitivity.json').read_text());OUT=ROOT/'results/soc_hls_operating_sensitivity';OUT.mkdir(exist_ok=True)
base_l1,base_l2,base_s1,base_s2=_roster([0,1,2,3,4,5]);base_mu=effective_capacity(base_l1,base_s1,PROJECT_MIX)['max_common_arrivals_per_h'];_,route_mix=routed_l2_shares();base_mu2=effective_capacity(base_l2,base_s2,route_mix)['max_common_arrivals_per_h'];H=C['horizon_h'];D=C['drain_h'];episodes=[];strata=[];manifest=[]
def run_case(kind,case,deadline_map=None,team=None):
 if team:
  l1,l2,s1,s2=build_roster(team['n_l1'],team['n_l2'],2.5)
 else:l1,l2,s1,s2=base_l1,base_l2,base_s1,base_s2
 mu1=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];mu2=effective_capacity(l2,s2,route_mix)['max_common_arrivals_per_h']
 for duration in C['selected_durations_h']:
  profile=f'nom_r125_d{duration}'
  for seed in range(C['seed_base'],C['seed_base']+C['seed_count']):
   gen=[]
   for i,(lo,hi,rho0) in enumerate(((0,4,.85),(4,4+duration,1.25),(4+duration,24,.85))):
    rho=rho0 if not team else (base_mu*rho0/mu1)
    rate=base_mu*rho0
    deadlines=deadline_map or dict(zip(('low','medium','high'),(12.,4.,1.)))
    cfg=replace(REFERENCE.scenario_config(arrival_rate_per_h=rate),horizon=hi-lo,deadline_by_severity=tuple(deadlines.items()))
    for j,x in enumerate(generate_alerts(cfg,seed*100+i)):
     al=x.routed.alert;al=replace(al,alert_id=f'{i:02d}-{j:08d}',arrival=al.arrival+lo,deadline=al.deadline+lo)
     gen.append(replace(x,routed=replace(x.routed,alert=al)))
   gen=tuple(sorted(gen,key=lambda x:(x.routed.alert.arrival,x.routed.alert.alert_id)));adm=[x for x in gen if x.routed.alert.arrival<H]
   # Exogenous hash excludes deadline so alternative SLA configs can be verified as identical.
   fp=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.soctra_recommendation,x.severity,x.difficulty) for x in adm);digest=hashlib.sha256(repr(fp).encode()).hexdigest();manifest.append(dict(kind=kind,case=case['name'],duration_h=duration,seed=seed,hash=digest,n=len(adm)))
   for pol in ('D1','P1','HLS-B'):
    kw=dict(policy=pol,admission_horizon=H,drain_period=D,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
    if pol=='HLS-B':kw.update(hlsb_l1_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu1),hlsb_l2_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu2))
    sim=simulate_l1_l2(tuple(x.routed for x in gen),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw);a={x.alert_id:x for x in sim.l1_simulation.assignments};b={x.alert_id:x for x in sim.l2_simulation.assignments};rt={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
    final={x.routed.alert.alert_id:(b.get(x.routed.alert.alert_id) if rt[x.routed.alert.alert_id] else a.get(x.routed.alert.alert_id)) for x in adm}
    def calc(group,cut):
     done=[x for x in group if final[x.routed.alert.alert_id] and final[x.routed.alert.alert_id].completion<=cut];on=[x for x in done if final[x.routed.alert.alert_id].completion<=x.routed.alert.deadline]
     rn=sum(final[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in on)/len(group);quality=sum(final[x.routed.alert.alert_id].competence*(1-.35*x.difficulty) for x in done)/len(done) if done else 0
     return len(done),len(on)/len(group),rn,quality
    done,sla,rn,q=calc(adm,48.)
    run=dict(kind=kind,case=case['name'],case_axis=case.get('axis','staffing'),duration_h=duration,seed=seed,policy=pol,trace_hash=digest,admitted=len(adm),completed=done,pending=len(adm)-done,RN=rn,SLA=sla,quality_completed=q,n_l1=len(l1),n_l2=len(l2),mu_l1=mu1,mu_l2=mu2,rho_normal=.85*base_mu/mu1,rho_pulse=1.25*base_mu/mu1)
    if kind=='sla':run.update(T0=case['T0'],f_high=case['f_high'],f_low=case['f_low'])
    episodes.append(run)
    for priority_name in ('high','medium','low'):
     g=[x for x in adm if x.severity==priority_name];_,ss,rr,qq=calc(g,48.);strata.append(dict(kind=kind,case=case['name'],duration_h=duration,seed=seed,policy=pol,priority=priority_name,n=len(g),SLA=ss,RN=rr,quality_completed=qq))
  print(kind,case['name'],'d',duration,'complete',flush=True)
for sla in C['sla_sets']:
 deadline={'high':sla['T0'],'medium':sla['T0']*sla['f_high'],'low':sla['T0']*sla['f_low']}
 run_case('sla',sla,deadline_map=deadline)
for team in C['teams']:run_case('staff',team,team=team)
for f,rows in [('episodes.csv',episodes),('priority.csv',strata)]:
 with (OUT/f).open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'metadata.json').write_text(json.dumps(dict(config=C,base_mu_l1=base_mu,base_mu_l2=base_mu2,episodes=len(episodes),note='same physical arrival rate across teams; rho recalculated per capacity; SLA hashes omit deadlines only'),indent=2))
print('saved',len(episodes),'sensitivity episode rows',flush=True)
