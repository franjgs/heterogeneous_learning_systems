"""Frozen 100-seed HLS-B validation. Read config; never tune from outputs."""
import csv,hashlib,json,statistics,sys,time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSAConfig,HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2,stage_metrics_at
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster,_queue_profile
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent;cfg=json.loads((HERE/'config/soc_hlsb_validation.json').read_text());out=ROOT/cfg['output_dir'];out.mkdir(exist_ok=True)
seeds=list(range(cfg['seed_base'],cfg['seed_base']+cfg['seed_count']));assert len(seeds)==len(set(seeds))==100 and not set(seeds)&(set(range(261140000,261140030))|set(range(261132000,261132020))|set(range(261160000,261160100))|set(range(261170000,261170006))|set(range(261180000,261180006)))
l1,l2,s1,s2=_roster([0,1,2,3,4,5]);mu1=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h'];_,mix2=routed_l2_shares();mu2=effective_capacity(l2,s2,mix2)['max_common_arrivals_per_h']
rows=[];strata=[];modes=[];start=time.perf_counter()
for sc in cfg['scenarios']:
 base=replace(REFERENCE.scenario_config(arrival_rate_per_h=mu1*sc['base_rho']),horizon=24.)
 if 'shift_h' in sc:base=replace(base,arrival_rate_shift_after=sc['shift_h'],arrival_rate_after=mu1*sc['after_rho'])
 for seed in seeds:
  generated=generate_alerts(base,seed);adm=[x for x in generated if x.routed.alert.arrival<24];trace=hashlib.sha256(repr(tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation) for x in adm)).encode()).hexdigest()
  def cohort(x):
   t=x.routed.alert.arrival
   if 'shift_h' not in sc:return 'all'
   if sc['name']=='moderate_overload':return 'moderate_0_8' if t<8 else 'overload_8_24'
   return 'overload_0_12' if t<12 else 'recovery_12_24'
  for policy in ('D1','P1','HLS-A','HLS-B'):
   kw=dict(policy=policy,admission_horizon=24.,drain_period=24.,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2,hlsa_config=HLSAConfig(**cfg['hlsa']))
   if policy=='HLS-B':kw.update(hlsb_l1_config=HLSBConfig(**cfg['hlsb'],capacity_per_h=mu1),hlsb_l2_config=HLSBConfig(**cfg['hlsb'],capacity_per_h=mu2))
   sim=simulate_l1_l2(tuple(x.routed for x in generated),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
   first={a.alert_id:a for a in sim.l1_simulation.assignments};second={a.alert_id:a for a in sim.l2_simulation.assignments};route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records};assert len(first)==len(sim.l1_simulation.assignments) and len(second)==len(sim.l2_simulation.assignments)
   finals=[(x,second.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else first.get(x.routed.alert.alert_id)) for x in adm]
   hist=sim.l1_simulation.hlsa_history
   for event in hist:modes.append(dict(scenario=sc['name'],seed=seed,policy=policy,time_h=event.time,mode=event.mode,estimate=event.pressure,switched=event.switched))
   for cut in (24.,48.):
    done=[(x,a) for x,a in finals if a and a.completion<=cut];n=len(adm);ontime=[(x,a) for x,a in done if a.completion<=x.routed.alert.deadline];R=sum(a.competence*(1-.35*x.difficulty) for x,a in ontime)
    waits=[max(0.,min(first[x.routed.alert.alert_id].start if x.routed.alert.alert_id in first else cut,cut)-x.routed.alert.arrival) for x in adm]
    q1=_queue_profile([x.routed.alert.arrival for x in adm],[a.start for a in first.values()],cut)
    l2arr=[first[aid].completion for aid,flag in route.items() if flag and aid in first and first[aid].completion<cut]
    q2=_queue_profile(l2arr,[a.start for a in second.values()],cut)
    rows.append(dict(scenario=sc['name'],seed=seed,policy=policy,cutoff_h=cut,trace_sha256=trace,admitted=n,completed=len(done),pending=n-len(done),R_per_admitted=R/n,sla=len(ontime)/n,quality_completed=statistics.mean(a.competence*(1-.35*x.difficulty) for x,a in done),wait_l1_mean_h=statistics.mean(waits),wait_l1_p95_h=sorted(waits)[int(.95*(n-1))],queue_l1_mean=q1['queue_mean_time_weighted'],queue_l2_mean=q2['queue_mean_time_weighted'],queue_l1_peak=q1['queue_peak'],queue_l2_peak=q2['queue_peak'],util_l1=statistics.mean(v for _,v in stage_metrics_at(sim.l1_simulation,cut)),util_l2=statistics.mean(v for _,v in stage_metrics_at(sim.l2_simulation,cut)),switches=sum(e.switched for e in hist),p1_decision_share=sum(e.mode=='P1' for e in hist)/len(hist) if hist else 0.))
    for kind in ('priority','cohort'):
     groups=sorted({x.severity if kind=='priority' else cohort(x) for x in adm})
     for group in groups:
      members=[(x,a) for x,a in finals if (x.severity if kind=='priority' else cohort(x))==group];eligible=[(x,a) for x,a in members if a and a.completion<=cut and a.completion<=x.routed.alert.deadline]
      strata.append(dict(scenario=sc['name'],seed=seed,policy=policy,cutoff_h=cut,kind=kind,group=group,admitted=len(members),R_per_admitted=sum(a.competence*(1-.35*x.difficulty) for x,a in eligible)/len(members),sla=len(eligible)/len(members)))
 print(sc['name'],'complete',round(time.perf_counter()-start,1),flush=True)
for name,data in [('episodes.csv',rows),('strata.csv',strata),('modes.csv',modes)]:
 with (out/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
(out/'metadata.json').write_text(json.dumps(dict(config=cfg,mu_l1=mu1,mu_l2=mu2,policy_episodes=len(rows)//2,runtime_s=time.perf_counter()-start),indent=2))
print('saved',len(rows),'cutoff rows',flush=True)
