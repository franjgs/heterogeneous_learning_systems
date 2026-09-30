"""Sprint 0 PACS competence-dynamics screen (N=50 only).

Scientific authority: docs/experimental_foundations/SPRINT0_PACS_COMPETENCE_GATE.md
Reuses B2.3/B2.4 machinery. TEST has no API surface here.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn

ROOT=Path(__file__).resolve().parents[3]
B24_RUN=ROOT/"experiments/pilots/b24_interference_controlled/run.py"
B24_ANALYZE=ROOT/"experiments/pilots/b24_interference_controlled/analyze.py"
PROTOCOL=ROOT/"docs/experimental_foundations/SPRINT0_PACS_COMPETENCE_GATE.md"
DEFAULT_B23=ROOT/"results/pilots/b23_portfolio_opportunity"
DEFAULT_B24=ROOT/"results/pilots/b24_interference_controlled"
DEFAULT_MANIFEST=ROOT/"results/pilots/b2_pacs_calibration/dataset_manifest.csv"
DEFAULT_OUTPUT=ROOT/"results/pilots/sprint0_pacs_competence_gate"
SCOPES=("H","LB"); N_SCREEN=50

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
    m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m
b24=loadmod("sprint0_b24",B24_RUN)
b24a=loadmod("sprint0_b24a",B24_ANALYZE)

def cases():
    return [b24.CaseSpec(i+1,s,d,N_SCREEN) for i,(s,d) in enumerate((s,d) for s in b24.SEEDS for d in b24.DOMAINS)]

def o50_schedule(spec, opportunity_ids):
    steps, exposures=b24.dose(spec.n)
    opp=b24.opportunity_exposure_sequence(spec,tuple(opportunity_ids),exposures)
    out=[]
    for step in range(steps):
        half=opp[step*b24.HALF_BATCH:(step+1)*b24.HALF_BATCH]
        originals=[dict(x) for x in half]
        duplicates=[{**x,"role":"opportunity_duplicate"} for x in half]
        out.append(originals+duplicates if step%2==0 else duplicates+originals)
    if len(out)!=steps or any(len(x)!=b24.BATCH_SIZE for x in out): raise RuntimeError("bad O50 schedule")
    return out

def set_scope(model, scope):
    for p in model.parameters(): p.requires_grad=False
    if scope=="H":
        prefixes=("classifier.",)
    elif scope=="LB":
        prefixes=("features.18.","classifier.")
    else: raise ValueError(scope)
    names=[]
    for name,p in model.named_parameters():
        if name.startswith(prefixes):
            p.requires_grad=True; names.append(name)
    if not names: raise RuntimeError(f"empty trainable scope {scope}")
    if scope=="LB" and not any(n.startswith("features.18.") for n in names):
        raise RuntimeError("MobileNetV2 last block features.18 not found")
    return names

def train(f0_state,schedule,labels,lookup,image_root,spec,config,scope):
    seed=b24.b23.derived_training_seed(spec.seed,spec.n)
    b24.seed_everything(seed)
    model=b24.b23.b20.make_model("fast",seed,torch.device("cpu"),pretrained=False)
    model.load_state_dict(f0_state)
    names=set_scope(model,scope)
    opt=torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
        lr=float(config["fast"]["learning_rate"]),momentum=float(config["fast"]["momentum"]),weight_decay=0)
    batches=b24.ScheduledBatchBuilder(lookup,labels,image_root,spec.seed,spec.n)
    model.train(); started=time.perf_counter()
    for idx,entries in enumerate(schedule):
        torch.manual_seed(b24.b23.step_seed(spec.seed,spec.n,idx+1))
        images,targets=batches.batch(entries)
        opt.zero_grad(set_to_none=True)
        loss=nn.functional.cross_entropy(model(images),targets); loss.backward(); opt.step()
        print(f"{scope} seed={spec.seed} domain={spec.domain} step {idx+1}/{len(schedule)} loss={float(loss):.6f}",flush=True)
    return model,names,time.perf_counter()-started

def positive(vals):
    vals=[float(x) for x in vals]
    return sum(x>0 for x in vals)>=4 and float(np.mean(vals))>0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--device",default="cpu")
    ap.add_argument("--image-root",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,default=DEFAULT_MANIFEST)
    ap.add_argument("--b23-output",type=Path,default=DEFAULT_B23)
    ap.add_argument("--b24-output",type=Path,default=DEFAULT_B24)
    ap.add_argument("--output-dir",type=Path,default=DEFAULT_OUTPUT)
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    b24.require_cpu(args.device)
    if not args.image_root.is_dir(): raise ValueError("accessible --image-root required")

    # Strong parent audit: B2.4 must reconstruct successfully, and TEST must have been closed there.
    b24_scores,b24_audit=b24a.compatibility_audit(args.b24_output,args.b23_output)
    if b24_audit.get("compatible") is not True or b24_audit.get("test")!="CLOSED":
        raise RuntimeError("B2.4 parent audit failed")

    frame,lookup,parent,split_info=b24.load_parent_context(args.manifest,args.b23_output)
    b24.validate_image_root(frame,args.image_root)
    config=json.loads(b24.b23.CONFIG_PATH.read_text()); b24.b23.validate_config(config)
    split=split_info["split"]

    # Validate selectors before any fit.
    probe=b24.b23.b20.make_model("fast",0,torch.device("cpu"),pretrained=False)
    scope_names={s:set_scope(probe,s) for s in SCOPES}
    del probe
    print(json.dumps({"screen_N":50,"fits":40,"trainable_names":scope_names,"test_used":False},indent=2))
    if args.dry_run:
        print("Dry-run successful: B2.4 parent compatible; 40 fits planned; TEST not read.")
        return

    out=args.output_dir; out.mkdir(parents=True,exist_ok=True)
    state_rows=[]; value_rows=[]
    for spec in cases():
        f0,f0rec=b24.parent_checkpoint(parent,f"F0_s{spec.seed}")
        d,drec=b24.parent_checkpoint(parent,f"D_s{spec.seed}")
        opportunity,ophash,_=b24.parent_opportunity(parent,spec)
        schedule=o50_schedule(spec,opportunity["sample_ids"])
        labels={int(r["sample_id"]):int(r["pseudo_label"]) for r in opportunity["samples"]}
        val_ids=tuple(int(x) for x in split.loc[(split.seed==spec.seed)&(split.role=="VALIDATION"),"sample_id"])
        validation=lookup.loc[list(val_ids)].reset_index(drop=True)
        f0scores={d0:float(f0["scores"][d0]) for d0 in b24.DOMAINS}
        dscores={d0:float(d["scores"][d0]) for d0 in b24.DOMAINS}
        for scope in SCOPES:
            model,names,seconds=train(f0["model_state"],schedule,labels,lookup,args.image_root,spec,config,scope)
            scores=b24.score_model(model,validation,args.image_root)
            deltas={k:float(scores[k])-f0scores[k] for k in b24.DOMAINS}
            state_rows.append({"seed":spec.seed,"domain":spec.domain,"N":50,"method":scope,
                "DeltaS_local":deltas[spec.domain],"DeltaS_cross":sum(v for k,v in deltas.items() if k!=spec.domain),
                **{f"DeltaS_{k}":v for k,v in deltas.items()},"evaluation_split":"validation","test_used":False})
            for c in b24.COSTS:
                v0,r0,_=b24a.operational_value(f0scores,dscores,c)
                v,r,_=b24a.operational_value({k:float(scores[k]) for k in b24.DOMAINS},dscores,c)
                value_rows.append({"seed":spec.seed,"domain":spec.domain,"N":50,"method":scope,"c":c,
                    "V_F0":v0,"V":v,"DeltaV":v-v0,"routing_F0":r0,"routing":r,"routing_changed":r!=r0})
            del model

    states=pd.DataFrame(state_rows); values=pd.DataFrame(value_rows)
    states.to_csv(out/"state_metrics.csv",index=False); values.to_csv(out/"method_values.csv",index=False)
    rows=[]; diag=[]
    for scope in SCOPES:
        ss=states[states.method==scope]
        seed_local=ss.groupby("seed").DeltaS_local.mean()
        gl=positive(seed_local.tolist())
        rows.append({"method":scope,"criterion":"global_local","c":np.nan,"domain":"","positive":gl,
                     "favorable_seeds":int((seed_local>0).sum()),"mean":float(seed_local.mean())})
        exact_local={}
        for dom in b24.DOMAINS:
            x=ss[ss.domain==dom].sort_values("seed").DeltaS_local
            exact_local[dom]=positive(x.tolist())
            rows.append({"method":scope,"criterion":"exact_local","c":np.nan,"domain":dom,
                         "positive":exact_local[dom],"favorable_seeds":int((x>0).sum()),"mean":float(x.mean())})
        positive_costs=[]
        vv=values[values.method==scope]
        for c in b24.COSTS:
            x=vv[vv.c==c].groupby("seed").DeltaV.mean()
            p=positive(x.tolist()); positive_costs.append(c) if p else None
            rows.append({"method":scope,"criterion":"global_value","c":c,"domain":"","positive":p,
                         "favorable_seeds":int((x>0).sum()),"mean":float(x.mean())})
        advance=gl and bool(positive_costs) and any(exact_local.values())
        diag.append((scope,advance,positive_costs,[d for d,p in exact_local.items() if p]))
        rows.append({"method":scope,"criterion":"ADVANCE","c":np.nan,"domain":"","positive":advance,
                     "favorable_seeds":np.nan,"mean":np.nan})
    pd.DataFrame(rows).to_csv(out/"screen_classifications.csv",index=False)
    manifest={"header":{"protocol":"SPRINT0-PACS-COMPETENCE-GATE","screen_N":50,"device":"cpu",
              "test_used":False,"b23_manifest_sha256":b24.sha256_file(args.b23_output/"run_manifest.json"),
              "b24_manifest_sha256":b24.sha256_file(args.b24_output/"run_manifest.json"),
              "trainable_parameter_names":scope_names},
              "completed_fits":len(state_rows),"state_metrics_rows":len(state_rows),
              "method_values_rows":len(value_rows),"model_weights_stored":False}
    (out/"run_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    lines=["# Sprint 0 diagnostic","","TEST used: **false**.","",
           "| Method | Decision | Positive global-value costs | Exact domains with positive local learning |",
           "|---|---|---|---|"]
    for scope,adv,pcs,eds in diag:
        lines.append(f"| {scope} | {'ADVANCE' if adv else 'STOP'} | {', '.join(map(str,pcs)) or 'none'} | {', '.join(eds) or 'none'} |")
    lines+=["","This is a vehicle screen, not an RQ0 result. If both methods STOP, do not repair PACS further."]
    (out/"SPRINT0_DIAGNOSTIC.md").write_text("\n".join(lines)+"\n")
    print("\n".join(lines))

if __name__=="__main__": main()
