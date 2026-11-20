"""Paired development pilot for repeated nominal load changes. No tuning."""
import csv, hashlib, json, statistics, sys, time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import HLSBConfig
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,PROJECT_MIX
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity,routed_l2_shares
HERE=Path(__file__).resolve().parent; C=json.loads((HERE/'config/soc_hls_nonstationary.json').read_text()); OUT=ROOT/'results/soc_hls_nonstationary'; OUT.mkdir(exist_ok=True)
l1,l2,s1,s2=_roster([0,1,2,3,4,5]); mu1=effective_capacity(l1,s1,PROJECT_MIX)['max_common_arrivals_per_h']; _,mix2=routed_l2_shares(); mu2=effective_capacity(l2,s2,mix2)['max_common_arrivals_per_h']
assert C['seed_base']>=261200000 and C['seed_count']==4
rows=[]; cohorts=[]; transitions=[]; histories=[]
def mean(xs): return statistics.mean(xs) if xs else 0.
for duration in C['regime_lengths_h']:
 for order in C['orders']:
  name=f"{int(duration)}h_{order}"; count=int(C['horizon_h']/duration); assert count*duration==C['horizon_h'] and count%2==0
  schedule=tuple((i*duration, ('D1' if (i+(order=='overload_first'))%2==0 else 'P1')) for i in range(count))
  for seed in range(C['seed_base'],C['seed_base']+C['seed_count']):
   generated=[]
   for i,(start,mode) in enumerate(schedule):
    rate=mu1*(C['rho_moderate'] if mode=='D1' else C['rho_overload'])
    config=replace(REFERENCE.scenario_config(arrival_rate_per_h=rate),horizon=duration)
    for j,x in enumerate(generate_alerts(config,seed*100+i)):
     a=x.routed.alert; a=replace(a,alert_id=f'{i:02d}-{j:08d}',arrival=a.arrival+start,deadline=a.deadline+start)
     generated.append(replace(x,routed=replace(x.routed,alert=a)))
   generated=tuple(generated); fingerprint=tuple((x.routed.alert.alert_id,x.routed.alert.arrival,x.routed.alert.task_class,x.routed.alert.deadline,x.routed.soctra_recommendation,x.difficulty) for x in generated); trace=hashlib.sha256(repr(fingerprint).encode()).hexdigest(); n=len(generated)
   for policy in ('D1','P1','HLS-B','NOMINAL-REF'):
    kw=dict(policy=policy,admission_horizon=24.,drain_period=24.,coordination_latency=0.,coordination_edge_cost=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2,nominal_regimes=schedule)
    if policy=='HLS-B': kw.update(hlsb_l1_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu1),hlsb_l2_config=HLSBConfig(**C['hlsb'],capacity_per_h=mu2))
    sim=simulate_l1_l2(tuple(x.routed for x in generated),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
    first={a.alert_id:a for a in sim.l1_simulation.assignments}; second={a.alert_id:a for a in sim.l2_simulation.assignments}; route={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
    finals=[(x,second.get(x.routed.alert.alert_id) if route[x.routed.alert.alert_id] else first.get(x.routed.alert.alert_id)) for x in generated]
    def score(group):
     return sum(a.competence*(1-.35*x.difficulty) for x,a in group if a and a.completion<=48 and a.completion<=x.routed.alert.deadline)/len(group)
    assert len(first)==n and len(set(first))==n
    hist=sim.l1_simulation.hlsa_history
    rows.append(dict(scenario=name,duration_h=duration,order=order,seed=seed,policy=policy,trace_sha256=trace,admitted=n,expected_arrivals=mu1*1.125*24,R_per_admitted=score(finals),completed=sum(bool(a and a.completion<=48) for _,a in finals),pending=n-sum(bool(a and a.completion<=48) for _,a in finals),switches=sum(e.switched for e in hist)))
    for e in hist: histories.append(dict(scenario=name,seed=seed,policy=policy,time_h=e.time,mode=e.mode,estimate=e.pressure,pending=e.pending,busy=e.occupied,switched=e.switched))
    for i,(start,mode) in enumerate(schedule):
     group=[(x,a) for x,a in finals if start<=x.routed.alert.arrival<start+duration]
     cohorts.append(dict(scenario=name,seed=seed,policy=policy,regime_index=i,regime=mode,admitted=len(group),R_per_admitted=score(group)))
    for i,(start,mode) in enumerate(schedule[1:],1):
     pending=[x for x in generated if x.routed.alert.arrival<start and (x.routed.alert.alert_id not in first or first[x.routed.alert.alert_id].start>=start)]
     active=[a for a in first.values() if a.start<start<a.completion]
     by_class={c:sum(1 for x in pending if x.routed.alert.task_class==c) for c in sorted({x.routed.alert.task_class for x in generated})}
     work_by_class={c:sum(BASE_SERVICE_L1_H[x.routed.alert.task_class] for x in pending if x.routed.alert.task_class==c) for c in by_class}
     l2_pending=[a for a in first.values() if route[a.alert_id] and a.completion<start and (a.alert_id not in second or second[a.alert_id].start>=start)]
     next_mode=next((e for e in hist if e.time>=start and e.mode==mode),None)
     transitions.append(dict(scenario=name,seed=seed,policy=policy,time_h=start,new_regime=mode,queue_l1=len(pending),queue_l2=len(l2_pending),active_l1=len(active),pending_by_class=json.dumps(by_class,sort_keys=True),work_l1_h_by_class=json.dumps(work_by_class,sort_keys=True),first_matching_decision_h=next_mode.time if next_mode else '',delay_h=next_mode.time-start if next_mode else ''))
  print(name,'complete',flush=True)
for filename,data in [('episodes.csv',rows),('cohorts.csv',cohorts),('transitions.csv',transitions),('modes.csv',histories)]:
 with (OUT/filename).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
(OUT/'metadata.json').write_text(json.dumps(dict(config=C,mu_l1=mu1,mu_l2=mu2,policy_episodes=len(rows)),indent=2))
print('saved',len(rows),'policy episodes',flush=True)
