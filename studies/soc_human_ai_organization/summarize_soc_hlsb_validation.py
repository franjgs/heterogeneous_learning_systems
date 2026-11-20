"""Predeclared paired statistics for the frozen HLS-B validation."""
import csv,json,math,statistics
from pathlib import Path
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/soc_hlsb_validation'
rows=list(csv.DictReader((OUT/'episodes.csv').open()));scenarios=('steady_100','steady_125','moderate_overload','overload_recovery');seeds=range(261190000,261190100);policies=('D1','P1','HLS-A','HLS-B')
index={(r['scenario'],int(r['seed']),r['policy'],float(r['cutoff_h'])):r for r in rows}
assert len(index)==3200
for sc in scenarios:
 for seed in seeds:
  group=[index[sc,seed,p,48.] for p in policies]
  assert len({(r['trace_sha256'],r['admitted']) for r in group})==1
def ci(x):
 m=statistics.mean(x);sd=statistics.stdev(x);half=t.ppf(.975,len(x)-1)*sd/math.sqrt(len(x));return dict(mean=m,sd=sd,ci_low=m-half,ci_high=m+half,positive=sum(v>0 for v in x),negative=sum(v<0 for v in x))
def delta(sc,against):
 x=[float(index[sc,s,'HLS-B',48.]['R_per_admitted'])-float(index[sc,s,against,48.]['R_per_admitted']) for s in seeds];res=ci(x);res['p_two_sided']=2*t.sf(abs(res['mean']/(res['sd']/10)),99);return res
primary=ci([statistics.mean(float(index[sc,s,'HLS-B',48.]['R_per_admitted'])-float(index[sc,s,'D1',48.]['R_per_admitted']) for sc in scenarios) for s in seeds]);primary['t']=primary['mean']/(primary['sd']/10);primary['p_one_sided']=t.sf(primary['t'],99)
secondary={f'{sc}:B-{p}':delta(sc,p) for sc in scenarios for p in ('D1','P1','HLS-A')}
order=sorted(secondary,key=lambda k:secondary[k]['p_two_sided']);running=0.
for rank,key in enumerate(order):running=max(running,min(1.,(len(order)-rank)*secondary[key]['p_two_sided']));secondary[key]['holm_p']=running
means={sc:{p:{metric:statistics.mean(float(index[sc,s,p,cut][metric]) for s in seeds) for metric,cut in [('R_per_admitted',48.),('sla',48.),('quality_completed',48.),('wait_l1_mean_h',48.),('queue_l1_mean',24.),('queue_l2_mean',24.),('util_l1',24.),('util_l2',24.),('p1_decision_share',48.),('switches',48.),('R_H',24.),('sla_H',24.)] if metric not in ('R_H','sla_H')} for p in policies} for sc in scenarios}
for sc in scenarios:
 for p in policies:
  means[sc][p]['R_H']=statistics.mean(float(index[sc,s,p,24.]['R_per_admitted']) for s in seeds)
  means[sc][p]['sla_H']=statistics.mean(float(index[sc,s,p,24.]['sla']) for s in seeds)
result=dict(primary=primary,secondary=secondary,means=means)
(OUT/'statistics.json').write_text(json.dumps(result,indent=2))
print('PRIMARY',primary)
for sc in scenarios:print(sc,'D1',round(means[sc]['D1']['R_per_admitted'],4),'P1',round(means[sc]['P1']['R_per_admitted'],4),'A',round(means[sc]['HLS-A']['R_per_admitted'],4),'B',round(means[sc]['HLS-B']['R_per_admitted'],4),'B-D1',round(secondary[f'{sc}:B-D1']['mean'],4))
