#!/usr/bin/env python3
"""HLS-E2.0: exact finite-horizon DP for two rested Nembhard agents.

No external dependencies; no access to, or changes in, the HLS repository.
Reward is instantaneous productivity before increasing the chosen agent's experience.
"""
import argparse
import csv
import json
import random
from functools import lru_cache
from pathlib import Path


def productivity(k, p, r, d):
    return k * (d + p) / (d + p + r)


def evaluate(params, horizon, include_path=False):
    """Returns exact OPT, greedy, fixed-best-initial, and policy paths."""
    agents = params['agents']
    start = [agent['d0'] for agent in agents]
    table = [[productivity(a['k'], a['p'], a['r'], a['d0'] + n)
              for n in range(horizon + 1)] for a in agents]

    @lru_cache(None)
    def value(a, b):
        t = a + b
        if t == horizon:
            return 0.0
        return max(table[0][a] + value(a + 1, b),
                   table[1][b] + value(a, b + 1))

    opt = value(0, 0)
    a = b = 0
    opt_path = []
    for t in range(horizon):
        va = table[0][a] + value(a + 1, b)
        vb = table[1][b] + value(a, b + 1)
        if va >= vb:
            a += 1
            opt_path.append(0)
        else:
            b += 1
            opt_path.append(1)

    a = b = 0
    greedy = 0.0
    greedy_path = []
    for t in range(horizon):
        if table[0][a] >= table[1][b]:
            greedy += table[0][a]
            a += 1
            greedy_path.append(0)
        else:
            greedy += table[1][b]
            b += 1
            greedy_path.append(1)

    fixed_agent = 0 if table[0][0] >= table[1][0] else 1
    fixed = sum(table[fixed_agent][t] for t in range(horizon))
    out = dict(horizon=horizon, opt=opt, greedy=greedy, fixed=fixed,
               gain_opt_vs_greedy=opt-greedy,
               gain_opt_vs_fixed=opt-fixed,
               gain_pct_vs_greedy=100*(opt-greedy)/greedy if greedy else None,
               gain_pct_vs_fixed=100*(opt-fixed)/fixed if fixed else None,
               greedy_switches=sum(x != y for x,y in zip(greedy_path,greedy_path[1:])),
               opt_switches=sum(x != y for x,y in zip(opt_path,opt_path[1:])),
               fixed_agent=fixed_agent)
    if include_path:
        out.update(opt_path=opt_path,greedy_path=greedy_path,
                   initial_productivities=[x[0] for x in table],
                   final_opt_counts=[opt_path.count(0),opt_path.count(1)])
    return out


def experiment(n, seed, horizons):
    rng = random.Random(seed)
    rows = []
    for idx in range(n):
        # Log-uniform independent k,p,r, plus varying initial experience.
        agents=[]
        for _ in range(2):
            agents.append(dict(k=rng.uniform(0.5,3.0),
                               p=10**rng.uniform(-1,1),
                               r=10**rng.uniform(-1,1.5),
                               d0=rng.choice([0.,0.,0.,1.,5.,10.,20.])))
        params=dict(agents=agents)
        for horizon in horizons:
            res=evaluate(params,horizon)
            rows.append(dict(case=idx,parameters=params,**res))
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cases',type=int,default=1000)
    parser.add_argument('--seed',type=int,default=20261017)
    parser.add_argument('--horizons',type=int,nargs='+',default=[20,60,120])
    parser.add_argument('--output',type=Path,default=Path('hls_e2_0_results.json'))
    args=parser.parse_args()
    rows=experiment(args.cases,args.seed,args.horizons)
    summary={}
    for horizon in args.horizons:
        subset=[x for x in rows if x['horizon']==horizon]
        top=max(subset,key=lambda x:x['gain_opt_vs_greedy'])
        top_fixed=max(subset,key=lambda x:x['gain_opt_vs_fixed'])
        summary[str(horizon)]=dict(cases=len(subset),
            opt_beats_greedy=sum(x['gain_opt_vs_greedy']>1e-8 for x in subset),
            opt_beats_fixed=sum(x['gain_opt_vs_fixed']>1e-8 for x in subset),
            greedy_beats_fixed=sum(x['greedy']-x['fixed']>1e-8 for x in subset),
            largest_opt_greedy_gain=top,
            largest_opt_fixed_gain=top_fixed)
    payload=dict(model='Two rested agents; one skill; unit effort; full productivity reward; no switching cost',
                 sampling='Seeded exploratory random search, NOT population inference',
                 seed=args.seed,cases=args.cases,horizons=args.horizons,summary=summary)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    print(json.dumps(payload,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
