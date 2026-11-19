"""Reconstruct HLS-A L1 decision snapshots and same-analyst local contrasts."""
import copy, csv, json, random, statistics, sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_allocation import AllocationSession,HLSAConfig,hlsa_pressure,_dispatch_d1,_dispatch_local_priority
from studies.soc_human_ai_organization.run_a0_baseline_congestion import _roster
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H
HERE=Path(__file__).resolve().parent;cfg=json.loads((HERE/'config/soc_hlsa_pilot.json').read_text());out=ROOT/'results/soc_hlsa_pilot'
l1,_,s1,_=_roster([0,1,2,3,4,5]); rows=[]; candidates=[]
for sc in cfg['scenarios']:
 base=REFERENCE.scenario_config(arrival_rate_per_h=cfg['base_capacity_alerts_per_h']*sc['base_rho']);base=replace(base,horizon=24.)
 if 'burst_window_h' in sc: a,b=sc['burst_window_h'];base=replace(base,burst_window=(a,b,sc['burst_rho']/sc['base_rho']))
 if 'shift_h' in sc:base=replace(base,arrival_rate_shift_after=sc['shift_h'],arrival_rate_after=cfg['base_capacity_alerts_per_h']*sc['after_rho'])
 for seed in cfg['seeds']:
  generated=generate_alerts(base,seed);alerts=tuple(x.routed.alert for x in generated if x.routed.alert.arrival<24)
  session=AllocationSession(alerts,l1,BASE_SERVICE_L1_H,admission_horizon=24,drain_period=24,random_seed=seed,service_by_analyst_class=s1)
  mode='D1'; conf=HLSAConfig(2.,3.);prev=0.
  while (t:=session.next_event_time()) is not None:
   session.advance_to(t)
   if t>=48:break
   if not session.can_dispatch():continue
   free=session.available_analysts();pending=session.pending;z=hlsa_pressure(pending,session.analysts,session.running,session.dispatching,session._service_time)
   old=mode
   if mode=='D1' and z>=conf.high:mode='P1'
   elif mode=='P1' and z<=conf.low:mode='D1'
   d1=_dispatch_d1(free,pending,t,session._service_time,copy.deepcopy(session.order_rng))
   p1=_dispatch_local_priority(free,pending,t,session._service_time)
   dp=tuple((a.analyst_id,x.alert_id) for a,x in d1);pp=tuple((a.analyst_id,x.alert_id) for a,x in p1)
   if dp!=pp:
    # Compare selected alerts as two-task sequences on the same analyst; this is a local diagnostic, not episode gain.
    val={}
    for name,pairs in [('D1',d1),('P1',p1)]:
     total=0.
     for analyst,alert in pairs:
      q=alert
      p=analyst.competence[q.task_class]*(1-.35*next(x.difficulty for x in generated if x.routed.alert.alert_id==q.alert_id))
      total+=p*int(t+session._service_time(analyst,q)<=q.deadline)
     val[name]=total
    two_delta=''
    if len(free)==1 and len(d1)==len(p1)==1 and d1[0][1].alert_id!=p1[0][1].alert_id:
     analyst=free[0]; lookup={x.routed.alert.alert_id:x for x in generated}
     def two_value(first):
      first_job=analyst.competence[first.task_class]*(1-.35*lookup[first.alert_id].difficulty)*int(t+session._service_time(analyst,first)<=first.deadline)
      finish=t+session._service_time(analyst,first)
      second_jobs=[]
      for nxt in pending.values():
       if nxt.alert_id!=first.alert_id and nxt.task_class in analyst.eligible_classes:
        v=analyst.competence[nxt.task_class]*(1-.35*lookup[nxt.alert_id].difficulty)*int(finish+session._service_time(analyst,nxt)<=nxt.deadline)
        second_jobs.append(v)
      return first_job+(max(second_jobs) if second_jobs else 0.)
     two_delta=two_value(p1[0][1])-two_value(d1[0][1])
    candidates.append(dict(scenario=sc['name'],seed=seed,time_h=t,z=z,mode=mode,n_pending=len(pending),n_free=len(free),d1=json.dumps(dp),p1=json.dumps(pp),d1_value=val['D1'],p1_value=val['P1'],delta=val['P1']-val['D1'],two_service_delta=two_delta))
   rows.append(dict(scenario=sc['name'],seed=seed,time_h=t,z=z,mode=mode,switched=mode!=old,n_pending=len(pending),n_free=len(free),occupied=len(session.running),
    pending_state=json.dumps([dict(id=x.alert_id,cls=x.task_class,deadline=x.deadline,slack=x.deadline-t,eligible=[a.analyst_id for a in free if x.task_class in a.eligible_classes],service={a.analyst_id:session._service_time(a,x) for a in free if x.task_class in a.eligible_classes},competence={a.analyst_id:a.competence[x.task_class] for a in free if x.task_class in a.eligible_classes}) for x in pending.values()]),d1=json.dumps(dp),p1=json.dumps(pp)))
   session.dispatch(mode)
for name,data in [('diagnostic_epochs.csv',rows),('diagnostic_disagreements.csv',candidates)]:
 with (out/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=data[0].keys());w.writeheader();w.writerows(data)
print('epochs',len(rows),'disagreements',len(candidates))
for sc in cfg['scenarios']:
 rr=[x for x in rows if x['scenario']==sc['name']];dd=[x for x in candidates if x['scenario']==sc['name']]
 p1n=sum(x['mode']=='P1' for x in rr);p1v=sum(x['p1_value']>x['d1_value'] for x in dd);d1v=sum(x['p1_value']<x['d1_value'] for x in dd)
 print(sc['name'],'epochs',len(rr),'P1%',round(100*p1n/len(rr),1),'disagree%',round(100*len(dd)/len(rr),1),'local_P1_better',p1v,'D1_better',d1v,'mean_delta',round(statistics.mean([x['delta'] for x in dd]),4) if dd else None)
