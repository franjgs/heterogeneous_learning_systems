"""Read-only postprocessing of D1 trajectories; synthetic A0 diagnostics."""
from __future__ import annotations
import sys, json, itertools, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from studies.soc_human_ai_organization import run_a0_baseline_congestion as base

def order_loss(t, sj, sk, dj, dk, pj, pk):
    forward=pj*(t+sj<=dj)+pk*(t+sj+sk<=dk)
    reverse=pk*(t+sk<=dk)+pj*(t+sk+sj<=dj)
    return max(0.,reverse-forward)

def diagnose(alerts, analysts, services, assignments, meta, cutoff):
    jobs=list(assignments); job_by_id={j.alert_id:j for j in jobs}; aa={a.alert_id:a for a in alerts}; roster={a.analyst_id:a for a in analysts}
    selected=set(); decisions=[]; exchanges=[]
    for job in jobs:
        t=job.start; j=aa[job.alert_id]; i=roster[job.analyst_id]
        pending=[a for a in alerts if a.arrival<=t and a.alert_id not in selected]
        candidates=[a for a in pending if a.task_class in i.eligible_classes and a.alert_id!=j.alert_id]
        sj=services[i.analyst_id][j.task_class]
        def p(a): return i.competence[a.task_class]*(1-.35*meta[a.alert_id].difficulty)
        losses=[]; inversions=0; inversion_gain=0
        for k in candidates:
            sk=services[i.analyst_id][k.task_class]
            loss=order_loss(t,sj,sk,j.deadline,k.deadline,p(j),p(k))
            inv=k.deadline-t-sk < j.deadline-t-sj
            inversions+=inv; inversion_gain+=bool(inv and loss>1e-12)
            losses.append((loss,k.alert_id,inv))
        best=max(losses,default=(0.,'',False))
        free=[a for a in analysts if not any(x.analyst_id==a.analyst_id and x.start<=t<x.completion for x in jobs if x.alert_id in selected)]
        peers=[a for a in free if a.analyst_id!=i.analyst_id and j.task_class in a.eligible_classes]
        dependent=[a for a in pending if a.alert_id!=j.alert_id and a.task_class in i.eligible_classes and not any(a.task_class in x.eligible_classes for x in free if x.analyst_id!=i.analyst_id)]
        decisions.append(dict(time=t,analyst=i.analyst_id,alert=j.alert_id,alternatives=len(candidates),inversion=bool(inversions),inversion_with_gain=bool(inversion_gain),loss=best[0],alternative=best[1],specialist_conflict=bool(peers and dependent)))
        selected.add(j.alert_id)
    for x,y in itertools.combinations(jobs,2):
        if x.start!=y.start: continue
        i,k=roster[x.analyst_id],roster[y.analyst_id]; a,b=aa[x.alert_id],aa[y.alert_id]
        if b.task_class not in i.eligible_classes or a.task_class not in k.eligible_classes: continue
        def u(i,a): return i.competence[a.task_class]*(1-.35*meta[a.alert_id].difficulty)*(x.start+services[i.analyst_id][a.task_class]<=a.deadline)
        exchanges.append(max(0.,u(i,b)+u(k,a)-u(i,a)-u(k,b)))
    times=sorted({0.,cutoff}|{a.arrival for a in alerts if a.arrival<cutoff}|{v for j in jobs for v in (j.start,j.completion) if v<cutoff})
    duration=dict(idle=0.,blocked=0.,critical_blocked=0.,whole_team_critical=0.)
    for t,end in zip(times,times[1:]):
        busy={j.analyst_id for j in jobs if j.start<=t<j.completion}
        pending=[a for a in alerts if a.arrival<=t and (a.alert_id not in job_by_id or job_by_id[a.alert_id].start>t)]
        blocked=[a for a in pending if any(a.task_class in i.eligible_classes for i in analysts) and not any(i.analyst_id not in busy and a.task_class in i.eligible_classes for i in analysts)]
        critical=any(meta[a.alert_id].severity=='high' for a in blocked)
        duration['idle']+=(end-t)*any(i.analyst_id not in busy and a.task_class in i.eligible_classes for i in analysts for a in pending)
        duration['blocked']+=(end-t)*bool(blocked)
        duration['critical_blocked']+=(end-t)*critical
        duration['whole_team_critical']+=(end-t)*(critical and len(busy)==len(analysts))
    return decisions,exchanges,duration

def run():
    out=ROOT/'results/soc_a0_weaknesses'; out.mkdir(parents=True,exist_ok=True)
    rows=[]; traces=[]
    for rho in (.85,1.,1.25):
      for seed in range(base.SEED_BASE,base.SEED_BASE+6):
        l1,l2,s1,s2=base._roster(list(range(6)))
        scenario=base.REFERENCE.scenario_config(arrival_rate_per_h=base.CONFIG['base_l1_capacity_per_hour']*rho)
        scenario=type(scenario)(**{**scenario.__dict__,'horizon':base.HORIZON})
        generated=base.generate_alerts(scenario,seed); meta={r.routed.alert.alert_id:r for r in generated}
        result=base.simulate_l1_l2(tuple(r.routed for r in generated),l1,l2,base.BASE_SERVICE_L1_H,base.BASE_SERVICE_L2_H,policy='D1',admission_horizon=base.HORIZON,drain_period=base.DRAIN,coordination_latency=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
        first={j.alert_id:j for j in result.l1_simulation.assignments}; second={j.alert_id:j for j in result.l2_simulation.assignments}
        routes={r.alert_id:r.scenario_routing_decision for r in result.escalation_records}
        from hls.rq1_allocation import Alert
        a1=[r.routed.alert for r in generated]
        a2=[Alert(a.alert_id,first[a.alert_id].completion,a.task_class,a.deadline) for a in a1 if routes.get(a.alert_id) and a.alert_id in first and first[a.alert_id].completion<48]
        for pool,alerts,analysts,services,jobs in [('L1',a1,l1,s1,result.l1_simulation.assignments),('L2',a2,l2,s2,result.l2_simulation.assignments)]:
          d,e,_=diagnose(alerts,analysts,services,jobs,meta,48.)
          for row in d: traces.append(dict(rho=rho,seed=seed,pool=pool,**row))
          for cut in (24.,48.):
            _,_,dur=diagnose(alerts,analysts,services,jobs,meta,cut)
            rows.append(dict(rho=rho,seed=seed,pool=pool,cutoff=cut,decisions=len(d),alternatives=sum(x['alternatives']>0 for x in d),inversions=sum(x['inversion'] for x in d),inversions_with_gain=sum(x['inversion_with_gain'] for x in d),positive_order=sum(x['loss']>1e-12 for x in d),mean_positive_loss=statistics.mean([x['loss'] for x in d if x['loss']>1e-12]) if any(x['loss']>1e-12 for x in d) else 0.,swap_pairs=len(e),positive_swap=sum(x>1e-12 for x in e),specialist_conflicts=sum(x['specialist_conflict'] for x in d),**dur))
        for cut in (24.,48.):
          finals=[(r,(second if routes.get(r.routed.alert.alert_id) else first).get(r.routed.alert.alert_id)) for r in generated]
          completed=[(r,j) for r,j in finals if j and j.completion<=cut]
          rvalue=sum(j.competence*(1-.35*r.difficulty)*(j.completion<=r.routed.alert.deadline) for r,j in completed)
          rows.append(dict(rho=rho,seed=seed,pool='terminal',cutoff=cut,admitted=len(generated),completed=len(completed),pending=len(generated)-len(completed),R=rvalue,R_per_admitted=rvalue/len(generated),SLA=sum(j.completion<=r.routed.alert.deadline for r,j in completed)/len(generated),quality_completed=statistics.mean(j.competence*(1-.35*r.difficulty) for r,j in completed)))
    import csv
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (out/'episodes.csv').open('w') as f:
      w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    base._csv(out/'decisions.csv',traces)
    summary=[]
    for rho in (.85,1.,1.25):
      for pool in ('L1','L2','terminal'):
       for cut in (24.,48.):
        group=[r for r in rows if r['rho']==rho and r['pool']==pool and r['cutoff']==cut]
        summary.append(dict(rho=rho,pool=pool,cutoff=cut,**{k:statistics.mean(r[k] for r in group) for k in group[0] if k not in ('rho','pool','cutoff','seed')}))
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))
if __name__=='__main__': run()
