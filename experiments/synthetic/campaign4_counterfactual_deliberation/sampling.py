"""C4 deterministic, outcome-blind, probability-known sampling. No simulations."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

POLICIES = ('FAST','DEEP','META_VOC_50','RANDOM_50')
DOMAINS = ('G1','G2','G3','G4')
SEED = 'HLS-C4-SAMPLE-v1-20261012'
SOURCE_SHA = 'b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498'

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def priority(*parts):
    return hashlib.sha256('|'.join(map(str,(SEED,*parts))).encode()).hexdigest()

def select(source:Path, out:Path):
    if sha(source)!=SOURCE_SHA:raise ValueError('Frozen C3 trajectories hash mismatch')
    d=pd.read_csv(source)
    d=d[d.policy.isin(POLICIES)&d.remaining.isin((2,3))].copy()
    d['block']=((d.clock-1)//9)+1
    assert d.groupby(['history_id','policy','block','remaining']).size().eq(3).all()
    rows=[];longrows=[];audit=[]
    for domain in DOMAINS:
        for block in range(1,5):
            cell=d[(d.domain==domain)&(d.block==block)]
            histories=sorted(cell.history_id.unique(),key=lambda h:(priority('history',domain,block,h),h))
            assert len(histories)>=50
            selected_histories=histories[:50]
            # Exact 25 per remaining, policy quotas (7,6,6,6), rotating which policy receives 7.
            labels=[]
            for h in (2,3):
                for j,p in enumerate(POLICIES):
                    q=7 if j==((block+int(domain[1:])+h)%4) else 6
                    labels.extend([(h,p,q)]*q)
            assert len(labels)==50
            # Random permutation of quota labels, independent of observed states and outcomes.
            label_keys=sorted(range(50),key=lambda k:(priority('label',domain,block,k),k))
            permuted=[labels[k] for k in label_keys]
            chosen=[]
            for history,(remaining,policy,quota) in zip(selected_histories,permuted):
                candidates=cell[(cell.history_id==history)&(cell.policy==policy)&(cell.remaining==remaining)]
                assert len(candidates)==3
                picked=min(candidates.to_dict('records'),key=lambda x:(priority('clock',domain,block,history,policy,remaining,x['clock']),x['clock']))
                picked['state_id']=hashlib.sha256(f"{history}|{policy}|{picked['clock']}".encode()).hexdigest()[:24]
                picked['inclusion_probability']=quota/(3*len(histories))
                picked['sampling_weight']=1/picked['inclusion_probability']
                picked['quota_in_cell']=quota
                chosen.append(picked)
            assert len(chosen)==50 and len(set(x['history_id'] for x in chosen))==50
            rows.extend(chosen)
            long_ids=set(x['state_id'] for x in sorted(chosen,key=lambda x:(priority('long',domain,block,x['state_id']),x['state_id']))[:10])
            for x in chosen:
                if x['state_id'] in long_ids:
                    y=x.copy();y['long_conditional_probability']=0.2;y['long_inclusion_probability']=y['inclusion_probability']*0.2;y['long_sampling_weight']=1/y['long_inclusion_probability'];longrows.append(y)
            audit.append({'domain':domain,'block':block,'n_histories':len(histories),'selected_histories':50,'selected_states':50,'selected_long':10,'candidate_rows':len(cell)})
    assert len(rows)==800 and len(longrows)==160
    out.mkdir(parents=True,exist_ok=False)
    selected=pd.DataFrame(rows);long=pd.DataFrame(longrows)
    selected.to_csv(out/'selected_states.csv.gz',index=False,compression='gzip')
    long.to_csv(out/'long_states.csv.gz',index=False,compression='gzip')
    pd.DataFrame(audit).to_csv(out/'sampling_audit.csv',index=False)
    manifest={'protocol':'HLS-C4-SAMPLE-v1','seed':SEED,'source_sha256':SOURCE_SHA,'selection_is_outcome_blind':True,'n':len(rows),'n_long':len(longrows),'sampling_unit':'history within domain x 9-clock block','inclusion_probability':'quota(domain,block,remaining,policy)/(3*n_histories(domain))','long_probability':'0.2 * inclusion_probability','files_sha256':{p.name:sha(p) for p in out.iterdir()}}
    (out/'sampling_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'states':len(rows),'long_states':len(longrows),'output':str(out)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--trajectories',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();select(a.trajectories,a.output)
