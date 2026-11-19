"""Targeted P4 dispatch multiplicity audit on the paired main traces."""
import collections,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from hls.ia_l1_l2_simulation import generate_alerts
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_human_ai_organization import run_a0_baseline_congestion as a0
from studies.soc_human_ai_organization.soc_parametric_baseline import REFERENCE,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H
cfg=json.loads((Path(__file__).parent/'config/soc_policy_comparison.json').read_text());out=[]
for sc in cfg['scenarios'][:4]:
 l1,l2,s1,s2=a0._roster(sc['active_l1_indices']);settings=REFERENCE.scenario_config(arrival_rate_per_h=sc['arrival_rate_per_h']);settings=type(settings)(**{**settings.__dict__,'horizon':24.})
 for seed in range(cfg['seed_base'],cfg['seed_base']+cfg['seed_count']):
  alerts=generate_alerts(settings,seed)
  for policy in ('P4','P5'):
   res=simulate_l1_l2(tuple(r.routed for r in alerts),l1,l2,BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,policy=policy,admission_horizon=24.,drain_period=24.,coordination_latency=0.,decision_mode='hypothetical_recommendation_acceptance',random_seed=seed,l1_service_by_analyst_class=s1,l2_service_by_analyst_class=s2)
   for pool,stage in [('L1',res.l1_simulation),('L2',res.l2_simulation)]:
    groups=collections.Counter(j.start for j in stage.assignments)
    out.append(dict(scenario=sc['name'],seed=seed,policy=policy,pool=pool,groups=len(groups),multi_groups=sum(n>=2 for n in groups.values()),multi_assignments=sum(n for n in groups.values() if n>=2)))
p=ROOT/'results/soc_policy_comparison/matching_diagnostics.csv'
with p.open('w') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
for sc in cfg['scenarios'][:4]:
 for policy in ('P4','P5'):
  g=[x for x in out if x['scenario']==sc['name'] and x['policy']==policy]
  print(sc['name'],policy,'multi_groups',sum(x['multi_groups'] for x in g),'multi_assignments',sum(x['multi_assignments'] for x in g),flush=True)
