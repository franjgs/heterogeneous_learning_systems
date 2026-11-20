"""Paired A0 scenarios for frozen D1/P1-P5; synthetic, local results only."""
from __future__ import annotations
import csv, hashlib, json, statistics, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_l1_l2 import simulate_l1_l2, stage_metrics_at
from studies.soc_human_ai_organization import run_a0_baseline_congestion as a0
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H
from scipy.stats import t as student_t
CFG=json.loads((Path(__file__).parent/'config/soc_policy_comparison.json').read_text())
POLICIES=CFG['policies']; H=24.; D=24.; OUT=ROOT/CFG['output_dir']; OUT.mkdir(parents=True,exist_ok=True)
def write(name,rows):
    if not rows:return
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
def stats(v):
    n=len(v); mean=statistics.mean(v);sd=statistics.stdev(v) if n>1 else 0.;rad=student_t.ppf(.975,n-1)*sd/(n**.5) if n>1 else 0.
    return mean,sd,mean-rad,mean+rad
rows=[]; strata=[]; t0=time.perf_counter()
for scenario in CFG['scenarios']:
    l1,l2,s1,s2=a0._roster(scenario['active_l1_indices'])
    rate=scenario['arrival_rate_per_h']; name=scenario['name']
    settings=REFERENCE.scenario_config(arrival_rate_per_h=rate)
    settings=type(settings)(**{**settings.__dict__,'horizon':H})
    for seed in range(CFG['seed_base'],CFG['seed_base']+CFG['seed_count']):
        generated=generate_alerts(settings,seed)
        admitted=[r for r in generated if r.routed.alert.arrival<H]
        fingerprint=hashlib.sha256(json.dumps([(r.routed.alert.alert_id,r.routed.alert.arrival,r.routed.alert.task_class,r.routed.alert.deadline,r.severity,r.difficulty,r.routed.soctra_recommendation) for r in admitted],sort_keys=True).encode()).hexdigest()
        for phase in ('zero','costed'):
            for policy in POLICIES:
                latency=CFG['costed_latency_h'] if phase=='costed' and policy in ('P4','P5') else 0.
                edge=CFG['costed_edge_units'] if phase=='costed' and policy in ('P4','P5') else 0.
                sim=simulate_l1_l2(tuple(r.routed for r in generated),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,policy=policy,admission_horizon=H,drain_period=D,coordination_latency=latency,coordination_edge_cost=edge,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
                j1={x.alert_id:x for x in sim.l1_simulation.assignments};j2={x.alert_id:x for x in sim.l2_simulation.assignments};routes={x.alert_id:x.scenario_routing_decision for x in sim.escalation_records}
                if len(j1)!=len(set(j1)) or len(j2)!=len(set(j2)):raise AssertionError('duplicate assignment')
                if any(a.task_class not in next(i for i in l1 if i.analyst_id==j1[a.alert_id].analyst_id).eligible_classes for a in (r.routed.alert for r in admitted) if a.alert_id in j1):raise AssertionError('ineligible L1')
                finals=[]
                for r in admitted:
                    aid=r.routed.alert.alert_id; job=j2.get(aid) if routes.get(aid) else j1.get(aid)
                    finals.append((r,job))
                for cut in (H,H+D):
                    completed=[(r,j) for r,j in finals if j is not None and j.completion<=cut]
                    if len(completed)+sum(j is None or j.completion>cut for _,j in finals)!=len(admitted):raise AssertionError('conservation')
                    sla=sum(j.completion<=r.routed.alert.deadline for r,j in completed)
                    value=sum(j.competence*(1-.35*r.difficulty)*(j.completion<=r.routed.alert.deadline) for r,j in completed)
                    q1=a0._queue_profile([r.routed.alert.arrival for r in admitted],[j.start for j in j1.values()],cut)
                    l2arr=[j1[aid].completion for aid,route in routes.items() if route and aid in j1 and j1[aid].completion<cut]
                    q2=a0._queue_profile(l2arr,[j.start for j in j2.values()],cut)
                    waits=[min(j1[r.routed.alert.alert_id].start,cut)-r.routed.alert.arrival if r.routed.alert.alert_id in j1 else cut-r.routed.alert.arrival for r in admitted]
                    util1=[v for _,v in stage_metrics_at(sim.l1_simulation,cut)];util2=[v for _,v in stage_metrics_at(sim.l2_simulation,cut)]
                    row=dict(scenario=name,series=scenario['series'],seed=seed,phase=phase,policy=policy,cutoff_h=cut,trace_sha256=fingerprint,admitted=len(admitted),completed=len(completed),pending=len(admitted)-len(completed),R=value,R_per_admitted=value/len(admitted),sla=sla/len(admitted),quality_completed=statistics.mean([j.competence*(1-.35*r.difficulty) for r,j in completed]) if completed else 0.,mean_wait_l1_h=statistics.mean(waits),p95_wait_l1_h=a0._quantile(waits,.95),queue_l1_mean=q1['queue_mean_time_weighted'],queue_l1_peak=q1['queue_peak'],queue_l2_mean=q2['queue_mean_time_weighted'],queue_l2_peak=q2['queue_peak'],util_l1=statistics.mean(util1),util_l2=statistics.mean(util2),coordination_person_time=sim.coordination_person_time,coordination_latency_h=sim.l1_simulation.coordination_latency_total+sim.l2_simulation.coordination_latency_total,coordination_resource_units=sim.l1_simulation.coordination_resource+sim.l2_simulation.coordination_resource,dispatch_epochs=sim.l1_simulation.dispatch_decisions+sim.l2_simulation.dispatch_decisions)
                    rows.append(row)
                    for kind in ('priority','class'):
                        groups=sorted({r.severity if kind=='priority' else r.routed.alert.task_class for r in admitted})
                        for group in groups:
                            subset=[(r,j) for r,j in finals if (r.severity if kind=='priority' else r.routed.alert.task_class)==group]
                            done=[(r,j) for r,j in subset if j is not None and j.completion<=cut]
                            strata.append(dict(scenario=name,seed=seed,phase=phase,policy=policy,cutoff_h=cut,kind=kind,group=group,admitted=len(subset),sla=sum(j.completion<=r.routed.alert.deadline for r,j in done)/len(subset) if subset else 0.,R_per_admitted=sum(j.competence*(1-.35*r.difficulty)*(j.completion<=r.routed.alert.deadline) for r,j in done)/len(subset) if subset else 0.))
    print(name,'done',round(time.perf_counter()-t0,1),flush=True)
write('episodes.csv',rows);write('strata.csv',strata)
summary=[];paired=[]
metrics=['R_per_admitted','sla','quality_completed','mean_wait_l1_h','p95_wait_l1_h','queue_l1_mean','queue_l1_peak','queue_l2_mean','queue_l2_peak','util_l1','util_l2','pending','completed','coordination_person_time','coordination_latency_h','coordination_resource_units','dispatch_epochs']
for sc in CFG['scenarios']:
 for phase in ('zero','costed'):
  for cut in (H,H+D):
   base={r['seed']:r for r in rows if r['scenario']==sc['name'] and r['phase']==phase and r['cutoff_h']==cut and r['policy']=='D1'}
   for pol in POLICIES:
    group=sorted([r for r in rows if r['scenario']==sc['name'] and r['phase']==phase and r['cutoff_h']==cut and r['policy']==pol],key=lambda x:x['seed'])
    assert len(group)==len(base)==CFG['seed_count']
    assert all(r['trace_sha256']==base[r['seed']]['trace_sha256'] and r['admitted']==base[r['seed']]['admitted'] for r in group)
    for metric in metrics:
     v=[r[metric] for r in group];diff=[r[metric]-base[r['seed']][metric] for r in group]
     m,sd,lo,hi=stats(v);dm,ds,dlo,dhi=stats(diff)
     summary.append(dict(scenario=sc['name'],series=sc['series'],phase=phase,cutoff_h=cut,policy=pol,metric=metric,mean=m,sd=sd,ci_low=lo,ci_high=hi,delta_d1=dm,delta_sd=ds,delta_ci_low=dlo,delta_ci_high=dhi,win_frequency=sum(x>0 for x in diff)/len(diff)))
write('summary.csv',summary)
(OUT/'run_metadata.json').write_text(json.dumps(dict(config=CFG,runner='run_soc_policy_comparison.py',runtime_s=round(time.perf_counter()-t0,2),episode_rows=len(rows),trace_validation='SHA256 equal within scenario and seed'),indent=2))
