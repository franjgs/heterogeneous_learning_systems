"""Frozen seed-cluster analysis. No models/features beyond preregistration."""
from __future__ import annotations
import json
from itertools import combinations
import numpy as np
import pandas as pd
from . import run
from .validate import read

BOOTSTRAP_SEED=20261007
REPLICATES=10000


def bootstrap_indices():
    return np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED)).integers(0,40,size=(REPLICATES,40),dtype=np.int64)


def weights_for(draw):
    return np.bincount(draw,minlength=40)


def weighted_median(x, w):
    """Exact median of repeated integer-weighted rows, including even sample mean."""
    if not len(x) or w.sum()==0:
        return np.nan
    order=np.argsort(x,kind="stable"); xx=x[order]; cumulative=np.cumsum(w[order])
    n=int(cumulative[-1])
    return float((xx[np.searchsorted(cumulative,(n-1)//2+1)]+xx[np.searchsorted(cumulative,n//2+1)])/2)


def weighted_mean(x,w):
    return float(np.dot(x,w)/w.sum()) if w.sum() else np.nan


def correlation(x,y,w):
    if w.sum()<2:
        return np.nan
    mx,my=weighted_mean(x,w),weighted_mean(y,w)
    a,b=x-mx,y-my
    denominator=np.sqrt(np.dot(w,a*a)*np.dot(w,b*b))
    return float(np.dot(w,a*b)/denominator) if denominator>0 else np.nan


def ols_from_clusters(blocks,draw):
    """Literal frozen lstsq on full resampled rows; no normal-equation substitute."""
    selected=[blocks[int(i)] for i in draw if len(blocks[int(i)][0])]
    if not selected:
        return np.full(4,np.nan)
    x=np.concatenate([b[0] for b in selected]); y=np.concatenate([b[1] for b in selected])
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        return np.full(4,np.nan)
    coef,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    return coef if rank==4 else np.full(4,np.nan)


def distribution(x):
    x=np.asarray(x,dtype=float)
    total=len(x); missing=int((~np.isfinite(x)).sum())
    x=x[np.isfinite(x)]
    if not len(x):
        return dict(n=0,n_total=total,n_missing=missing,mean=None,median=None,min=None,q25=None,q75=None,max=None)
    return dict(n=len(x),n_total=total,n_missing=missing,mean=float(x.mean()),median=float(np.median(x)),min=float(x.min()),
                q25=float(np.quantile(x,.25)),q75=float(np.quantile(x,.75)),max=float(x.max()))


def interval(name,estimate,values):
    defined=np.isfinite(values); n=int((~defined).sum())
    ci=np.quantile(values[defined],[.025,.975],method="linear").tolist() if defined.any() else [None,None]
    return dict(estimand=name,estimate=float(estimate) if np.isfinite(estimate) else None,
        lower=ci[0],upper=ci[1],undefined_resamples=n,undefined_fraction=n/len(values),
        interval_scope="conditional on estimability" if n else "all seed resamples")


def write_csv(name,rows):
    pd.DataFrame(rows).to_csv(run.OUT/name,index=False,float_format="%.17g")


def main():
    validation=json.loads((run.OUT/"validation_summary.json").read_text())
    assert validation["passed"]
    s=read("reference_states"); s=s[s.remaining>1].copy()
    # CSV boolean columns include terminal missing values; comparison is explicit.
    for col in ("D_10","D_01","D_11","D_coupled"):
        s[col]=s[col]==True
    s["cluster"]=s.seed-10
    p=read("policy_evaluations")
    c=read("counterfactuals").merge(s,on="state_id",validate="many_to_one")
    c=c.merge(p,on=["state_id","policy"],validate="one_to_one",suffixes=("_world","_action"))
    # C_world is environmental change; C_action is immediate opportunity cost.
    indices=bootstrap_indices()
    np.save(run.OUT/"bootstrap_seed_indices.npy",indices,allow_pickle=False)
    registries={}; models={}; model_info={}; distributions=[]
    cluster=s.cluster.to_numpy(dtype=int)
    def register(name,x,mask=None,kind="mean",level="confirmatory"):
        mask=np.ones(len(s),dtype=bool) if mask is None else np.asarray(mask,dtype=bool)
        registries[name]=(np.asarray(x,dtype=float)[mask],cluster[mask],kind,level)
    for ab in ("10","01","11"):
        register(f"D_{ab}_prevalence",s[f"D_{ab}"])
    register("D_coupled_prevalence",s.D_coupled)
    for field,outcome,prefix in (("D_I_loss","D_10","H1_regret"),("H_S","D_01","H2_headroom")):
        for group in (False,True):
            mask=s[outcome]==group
            distributions.append(dict(quantity=field,group=f"{outcome}={int(group)}",status="confirmatory location; descriptive quantiles",**distribution(s.loc[mask,field])))
            register(f"{prefix}_mean_D{int(group)}",s[field],mask)
            register(f"{prefix}_median_D{int(group)}",s[field],mask,kind="median",
                     level="confirmatory" if field=="D_I_loss" else "descriptive secondary")
    for field in ("H","D_I","D_I_norm"):
        for group in (False,True):
            distributions.append(dict(quantity=field,group=f"D_10={int(group)}",status="preregistered complementary description",**distribution(s.loc[s.D_10==group,field])))
    coupled_selected=p[p.policy=="Q11"].merge(s[s.D_coupled],on="state_id",validate="one_to_one",suffixes=("_action","_world"))
    for field in ("Gamma","A_I","A_D","A_ID","C_action","H","D_I","D_I_loss","H_S"):
        distributions.append(dict(quantity=field,group="coupled states, Q11 selected action",
            status="preregistered H3 characterization; descriptive",**distribution(coupled_selected[field])))
    # Other registered quantities use their own divergent state populations.
    conditional={}
    for pid in ("Q10","Q01","Q11"):
        data=c[(c.policy==pid)&c.divergent].copy()
        conditional[pid]=data
        cl=data.cluster.to_numpy(dtype=int)
        y=data.DeltaG.to_numpy(); cost=data.C_action.to_numpy()
        specs={"p_plus":(y>run.EXACT_TOL,np.ones(len(y),bool)),
            "p_zero":(abs(y)<=run.EXACT_TOL,np.ones(len(y),bool)),
            "p_negative":(y<-run.EXACT_TOL,np.ones(len(y),bool)),
            "mean_DeltaG":(y,np.ones(len(y),bool)),
            "mean_negative_DeltaG":(y,y<-run.EXACT_TOL),
            "opportunity_cost_positive":(cost>run.EXACT_TOL,np.ones(len(y),bool)),
            "mean_opportunity_cost":(cost,np.ones(len(y),bool))}
        for name,(x,mask) in specs.items():
            registries[f"{pid}_{name}"]=(np.asarray(x,dtype=float)[mask],cl[mask],"mean","confirmatory")
        registries[f"{pid}_DeltaQ_DeltaG_Pearson"]=(np.column_stack((data.DeltaQ,y)),cl,"correlation","secondary confirmatory")
        for field in ("DeltaG","DeltaQ","C_action"):
            distributions.append(dict(quantity=field,group=pid+" divergent",status="descriptive secondary distribution",**distribution(data[field])))
        x=np.column_stack((np.ones(len(data)),data.DeltaQ,data.M,data.DeltaQ*data.M))
        models[pid]=[(x[cl==i],y[cl==i]) for i in range(40)]
        rank=int(np.linalg.lstsq(x,y,rcond=None)[2]) if len(y) else 0
        model_info[pid]=dict(n=len(y),rank=rank,required_rank=4,
            estimable=rank==4,formula="DeltaG ~ 1 + DeltaQ + M + DeltaQ:M",standardized=False)
    names=list(registries)
    estimates=np.full((REPLICATES,len(names)+12),np.nan)
    point=[]
    def statistic(entry,counts):
        x,cl,kind,_=entry; w=counts[cl]
        if kind=="median": return weighted_median(x,w)
        if kind=="correlation": return correlation(x[:,0],x[:,1],w)
        return weighted_mean(x,w)
    for name in names:
        point.append(statistic(registries[name],np.ones(40,dtype=int)))
    for pid in models:
        point.extend(ols_from_clusters(models[pid],np.arange(40)))
        names.extend(f"{pid}_OLS_{term}" for term in ("intercept","DeltaQ","M","DeltaQ_x_M"))
    base_names=list(registries)
    for rep,draw in enumerate(indices):
        counts=weights_for(draw)
        for j,name in enumerate(base_names):
            estimates[rep,j]=statistic(registries[name],counts)
        for j,pid in enumerate(models):
            estimates[rep,len(base_names)+4*j:len(base_names)+4*j+4]=ols_from_clusters(models[pid],draw)
        if (rep+1)%1000==0:
            print(f"Seed bootstrap {rep+1}/{REPLICATES}",flush=True)
    intervals=[dict(interval(name,point[j],estimates[:,j]),
        status=registries[name][3] if name in registries else "secondary confirmatory") for j,name in enumerate(names)]
    for prefix in ("H1_regret","H2_headroom"):
        for kind in ("mean","median"):
            a=names.index(f"{prefix}_{kind}_D1"); b=names.index(f"{prefix}_{kind}_D0")
            intervals.append(dict(interval(f"{prefix}_{kind}_difference",point[a]-point[b],estimates[:,a]-estimates[:,b]),
                status="descriptive secondary" if prefix=="H2_headroom" and kind=="median" else "confirmatory"))
    write_csv("bootstrap_intervals.csv",intervals)
    pd.DataFrame(estimates,columns=names).to_csv(run.OUT/"bootstrap_estimates.csv.gz",index=False,
        compression={"method":"gzip","mtime":0},float_format="%.17g")
    write_csv("distributions.csv",distributions)
    # Mechanistic descriptions are algebra, not empirical causes.
    selected=p.merge(s,on="state_id",validate="many_to_one",suffixes=("_action","_world"))
    selected[selected.policy!="Q00"].groupby(["scenario","configuration","policy"]).agg(
        n=("state_id","size"),DeltaQ_mean=("DeltaQ","mean"),cost_mean=("C_action","mean"),
        A_I_mean=("A_I","mean"),A_D_mean=("A_D","mean"),A_ID_mean=("A_ID","mean"),Gamma_mean=("Gamma","mean")
    ).to_csv(run.OUT/"opportunity_selected_summary.csv",float_format="%.17g")
    # All-action differential landscape spread, already frozen quantity, not a new state feature.
    landscape_spreads=[]; pair_diagnostics=[]
    state_index=s.set_index("state_id")
    for chunk in pd.read_csv(run.OUT/run.FILENAMES["landscapes"],chunksize=65536,float_precision="round_trip"):
        for sid,group in chunk.groupby("state_id",sort=False):
            assert len(group)==64
            baseline=group[group.action_id==int(state_index.loc[sid,"Q00"])].iloc[0]
            chosen=group[group.action_id==int(state_index.loc[sid,"Q01"])].iloc[0]
            landscape_spreads.append(dict(state_id=sid,A_D_min=group.A_D.min(),A_D_max=group.A_D.max(),
                A_D_selected_minus_baseline=chosen.A_D-baseline.A_D,
                C_Q01=chosen.C,Gamma_min=group.Gamma.min(),Gamma_max=group.Gamma.max()))
            indexed=group.set_index("action_id")
            for left,right in combinations(run.MODE_BY_ID,2):
                la,ra=int(state_index.loc[sid,left]),int(state_index.loc[sid,right])
                lr=float(group[left].max()-indexed.loc[ra,left])
                rr=float(group[right].max()-indexed.loc[la,right])
                pair_diagnostics.append(dict(state_id=sid,pair=left+"_"+right,exact_different=la!=ra,
                    left_regret_of_right=lr,right_regret_of_left=rr,
                    mutual_tie=lr<=run.EXACT_TOL and rr<=run.EXACT_TOL))
    write_csv("opportunity_landscape_summaries.csv",landscape_spreads)
    pd.DataFrame(pair_diagnostics).to_csv(run.OUT/"decision_pair_diagnostics.csv.gz",index=False,
        compression={"method":"gzip","mtime":0},float_format="%.17g")
    s.groupby(["scenario","configuration","problem_index","decision"]).agg(
        n=("state_id","size"),D_10=("D_10","mean"),D_01=("D_01","mean"),D_11=("D_11","mean"),
        D_coupled=("D_coupled","mean"),H_S=("H_S","mean"),D_I_loss=("D_I_loss","mean")
    ).to_csv(run.OUT/"descriptive_structural_strata.csv",float_format="%.17g")
    s.groupby(["scenario","configuration","pattern"]).size().rename("n").to_csv(run.OUT/"policy_patterns.csv")
    s.groupby(["scenario","configuration"])[["D_10","D_01","D_11","D_coupled"]].mean().to_csv(run.OUT/"decision_summary.csv")
    runs=read("runs")
    runs.groupby(["scenario","configuration","policy"]).cumulative_mu_true.agg(["count","mean","std","min","max"]).to_csv(run.OUT/"secondary_closed_loop_summary.csv",float_format="%.17g")
    descriptive=[]
    for pid,data in conditional.items():
        for mismatch,group in data.groupby("M"):
            descriptive.append(dict(policy=pid,M=mismatch,n=len(group),mean_DeltaG=group.DeltaG.mean(),
                p_plus=(group.DeltaG>run.EXACT_TOL).mean(),status="descriptive non-directional moderator strata"))
    write_csv("mismatch_strata.csv",descriptive)
    by={x["estimand"]:x for x in intervals}
    summary=dict(preregistered=True,primary_reference="Q11 only",independent_unit="seed",
        bootstrap=dict(replicates=REPLICATES,seed=BOOTSTRAP_SEED,method="whole-seed percentile 95%; shared resampling indices",undefined_resamples_reported=True),
        estimates=by,divergent_counts={p:len(d) for p,d in conditional.items()},
        raw_strict_sign_counts={p:dict(positive=int((d.DeltaG>0).sum()),zero=int((d.DeltaG==0).sum()),negative=int((d.DeltaG<0).sum())) for p,d in conditional.items()},
        raw_strict_positive_cost_counts={p:int((d.C_action>0).sum()) for p,d in conditional.items()},
        coupled_count=int(s.D_coupled.sum()),null_control_count=int((~c.divergent).sum()),
        secondary_OLS_design=model_info,
        immediate_myopic_vs_Q00_action_mismatches=int((s.immediate_myopic_id!=s.Q00).sum()),
        exact_divergences_mutual_tie={p:int(((selected.policy==p)&(selected[p]!=selected.Q00)&selected.mutual_tie).sum()) for p in ("Q10","Q01","Q11")},
        registry=dict(confirmatory=["H1","H2","H3","H4","conditional consequence estimands","opportunity costs"],
            secondary_confirmatory=["Pearson DeltaQ/DeltaG","OLS DeltaG~DeltaQ+M+DeltaQ:M"],
            secondary=["closed-loop performance","quantiles","full distributions"],
            descriptive_exploratory=["scenario/configuration/position strata","policy patterns","opportunity landscape characterization"],
            not_run=["logistic regression (not frozen in final preregistration)","new predictors","problem/history counterfactuals","nonlinear models"]),
        interpretation="opportunity landscapes reconstruct operator algebra; moderator associations are not causal")
    run.dump(run.OUT/"analysis_summary.json",summary)
    print(json.dumps({k:summary[k] for k in ("divergent_counts","coupled_count","null_control_count")}),flush=True)


if __name__=="__main__":
    main()
