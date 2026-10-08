"""Integrity gate before any Campaign 2 scientific interpretation."""
import json
from random import Random
import numpy as np
import pandas as pd
from . import run


def read(name):
    return pd.read_csv(run.OUT / run.FILENAMES[name],float_precision="round_trip")


def validate():
    run.preflight()
    completion=json.loads((run.OUT/"raw_completion.json").read_text())
    for name, expected in completion["sha256"].items():
        assert run.digest(run.OUT/name)==expected, name
    frames={name:read(name) for name in ("runs","trajectories","reference_states","policy_evaluations","counterfactuals")}
    counts={name:len(f) for name,f in frames.items()}
    expected=dict(runs=5120,trajectories=92160,reference_states=23040,policy_evaluations=61440,counterfactuals=46080)
    assert counts==expected, counts
    r,t,s,p,c=(frames[n] for n in frames)
    keys=["scenario","configuration","seed","policy"]
    assert not r.duplicated(keys).any()
    assert set(r.seed)==set(run.SEEDS)
    assert set(r.scenario)==set(run.HISTORIES)
    assert set(r.configuration)==set(run.CONFIG_BY_ID)
    assert set(r.policy)==set(run.MODE_BY_ID)
    assert (r.groupby(keys[:-2]+["policy"]).size()==40).all()
    assert not t.duplicated(keys+["problem_index","decision"]).any()
    assert (t.groupby(keys).size()==18).all()
    assert set(t.problem_index)==set(range(6)) and set(t.decision)=={0,1,2}
    assert (t.groupby(keys+["problem_index"]).size()==3).all()
    assert not s.state_id.duplicated().any()
    assert set(s.state_id)==set(range(23040))
    eligible=s[s.remaining>1].copy(); terminal=s[s.remaining==1]
    assert len(eligible)==15360 and (eligible.groupby("seed").size()==384).all()
    terminal_divergences=int((terminal[["Q00","Q10","Q01","Q11"]].nunique(axis=1)!=1).sum())
    assert terminal_divergences==0
    assert not p.duplicated(["state_id","policy"]).any() and (p.groupby("state_id").size()==4).all()
    assert set(p.state_id)==set(eligible.state_id)
    assert not c.duplicated(["state_id","policy"]).any() and (c.groupby("state_id").size()==3).all()
    assert set(c.state_id)==set(eligible.state_id)
    state=eligible.set_index("state_id")
    for pid in ("Q10","Q01","Q11"):
        exact=state[pid]!=state.Q00
        assert np.array_equal(state[f"D_{pid[1:]}"]==True,exact)
        cp=c[c.policy==pid].set_index("state_id").loc[state.index]
        assert np.array_equal(cp.divergent,exact)
    assert np.array_equal(state.D_coupled==True,(state.Q11!=state.Q10)&(state.Q11!=state.Q01))
    for row in p.itertuples():
        assert row.action_id==state.loc[row.state_id,row.policy]
        assert row.max_Q-row.selected_Q<=run.EXACT_TOL
        assert row.DeltaQ>=-run.EXACT_TOL
        assert row.C>=-run.EXACT_TOL
        assert row.mutual_tie==(row.own_regret_of_Q00<=run.EXACT_TOL and row.Q00_regret_of_action<=run.EXACT_TOL)
    q11=t[t.policy=="Q11"].merge(s,on=["scenario","configuration","seed","problem_index","decision"],validate="one_to_one")
    assert len(q11)==23040 and (q11.action_id==q11.Q11).all()
    assert (q11.S_before==q11.S).all() and (q11.b_before==q11.b).all()
    streams={}
    for seed in run.SEEDS:
        rng=Random(seed); streams[seed]=[rng.gauss(0,1) for _ in range(18)]
    errors={"observation":0.,"MIS_composition":0.,"branch_transition":0.,"branch_sum":0.,"operator_identity":0.}
    model,prior=run.planner.canonical_model(run.HYPOTHESIS_REPERTOIRE,run.UNIFORM_PRIOR)
    previous={}
    for row in t.itertuples():
        k=3*row.problem_index+row.decision
        assert row.epsilon==streams[row.seed][k] or abs(row.epsilon-streams[row.seed][k])<1e-15
        errors["observation"]=max(errors["observation"],abs(row.observation-row.mu_true-.1*row.epsilon))
        z=run.HISTORIES[row.scenario][row.problem_index]; d=run.history_steps(row.scenario)[row.problem_index]
        assert tuple(json.loads(row.true_theta))==z and row.represented==d.represented
        for field,actual in (("C",d.change),("N",d.novelty),("M",d.mismatch)):
            val=getattr(row,field)
            assert (pd.isna(val) and actual is None) or abs(val-actual)<1e-14
        before=np.array(json.loads(row.S_before)); after=np.array(json.loads(row.S_after))
        e0=np.array(json.loads(row.E_before)); e1=np.array(json.loads(row.E_after))
        x=np.array(run.JOINT_ACTIONS[row.action_id]); initial=np.array(run.CONFIG_BY_ID[row.configuration])
        assert np.array_equal(e1,e0+x)
        reconstructed=1-(1-initial)*np.power(.65,e1)
        errors["MIS_composition"]=max(errors["MIS_composition"],float(np.max(np.abs(after-reconstructed))))
        key=(row.scenario,row.configuration,row.seed,row.policy)
        if k==0:
            assert np.array_equal(before,initial)
        else:
            assert row.S_before==previous[key]
        previous[key]=row.S_after
        if row.decision==0:
            assert tuple(json.loads(row.b_before))==prior
    totals=t.groupby(keys).mu_true.sum()
    merged=r.set_index(keys).cumulative_mu_true-totals
    assert merged.abs().max()<1e-12
    null_error=float(c.loc[~c.divergent,"DeltaG"].abs().max())
    assert null_error==0.
    assert np.max(np.abs(c.DeltaG-(c.G_prospective-c.G_baseline)))<1e-12
    # Large raw tables streamed; all real branch transitions independently checked.
    branch_count=0; pending={}; sums={}
    for chunk in pd.read_csv(run.OUT/run.FILENAMES["branches"],chunksize=10000,float_precision="round_trip"):
        for row in chunk.itertuples():
            branch_count+=1
            ref=state.loc[row.state_id]
            assert row.continuation_policy==row.policy and row.branch_step in (0,1)
            assert ref.remaining in (2,3)
            s0=tuple(tuple(v) for v in json.loads(row.S_before)); b0=tuple(json.loads(row.b_before))
            expected_epsilon=ref.epsilon0 if row.branch_step==0 else ref.epsilon1
            assert abs(row.epsilon-expected_epsilon)<1e-15
            key=(row.state_id,row.policy,row.branch)
            if row.branch_step==0:
                expected_action=ref[row.policy] if row.branch=="prospective" else ref.Q00
                assert row.action_id==expected_action and row.S_before==ref.S and row.b_before==ref.b
                pending[key]=(row.S_after,row.b_after)
                sums[key]=row.mu_true
            else:
                assert (row.S_before,row.b_before)==pending.pop(key)
                sums[key]+=row.mu_true
            real=run.theory._real_decision(s0,b0,run.JOINT_ACTIONS[row.action_id],
                run.HISTORIES[ref.scenario][int(ref.problem_index)],row.epsilon,model)
            errors["branch_transition"]=max(errors["branch_transition"],
                abs(real.mu_true-row.mu_true),abs(real.observation-row.observation),
                float(np.max(np.abs(np.array(real.state_after)-json.loads(row.S_after)))),
                float(np.max(np.abs(np.array(real.belief_after)-json.loads(row.b_after)))))
    assert branch_count==184320 and not pending
    for row in c.itertuples():
        for name,total in (("prospective",row.G_prospective),("baseline",row.G_baseline)):
            errors["branch_sum"]=max(errors["branch_sum"],abs(sums[(row.state_id,row.policy,name)]-total))
    landscape_count=0; action_counts={}
    evaluation_index=p.set_index(["state_id","policy"])
    for chunk in pd.read_csv(run.OUT/run.FILENAMES["landscapes"],chunksize=65536,float_precision="round_trip"):
        landscape_count+=len(chunk)
        assert not chunk.duplicated(["state_id","action_id"]).any()
        for sid,group in chunk.groupby("state_id",sort=False):
            ids=action_counts.setdefault(sid,set())
            assert not ids.intersection(group.action_id)
            ids.update(group.action_id)
            assert len(group)==64
            group=group.sort_values("action_id")
            qs=group[list(run.MODE_BY_ID)].to_numpy()
            maxima=qs.max(axis=0)
            selected_indices=np.argmax(np.abs(qs-maxima)<=run.EXACT_TOL,axis=0)
            assert np.array_equal(group.action_id.to_numpy()[selected_indices],state.loc[sid,list(run.MODE_BY_ID)].to_numpy())
            myopic=int(state.loc[sid,"immediate_myopic_id"])
            errors["operator_identity"]=max(errors["operator_identity"],float(np.max(np.abs(
                group.C.to_numpy()-(group.g.iloc[myopic]-group.g.to_numpy())))))
            for j,pid in enumerate(run.MODE_BY_ID):
                selected=evaluation_index.loc[(sid,pid)]
                errors["operator_identity"]=max(errors["operator_identity"],
                    abs(selected.selected_Q-qs[selected_indices[j],j]),abs(selected.max_Q-maxima[j]),
                    abs(selected.DeltaQ-(qs[selected_indices[j],j]-qs[int(state.loc[sid,"Q00"]),j])))
        v0=chunk.state_id.map(state.V0)
        residuals=[chunk.Q00-chunk.g-v0,chunk.Q10-chunk.g-v0-chunk.A_I,
            chunk.Q01-chunk.g-v0-chunk.A_D,chunk.Q11-chunk.g-v0-chunk.A_ID,
            chunk.A_ID-chunk.A_I-chunk.A_D-chunk.Gamma]
        errors["operator_identity"]=max(errors["operator_identity"],*(float(x.abs().max()) for x in residuals))
    assert landscape_count==983040 and set(action_counts)==set(state.index)
    assert all(ids==set(range(64)) for ids in action_counts.values())
    assert max(errors.values())<1e-12,errors
    counts.update(landscapes=landscape_count,branches=branch_count)
    summary=dict(passed=True,counts=counts,eligible_reference_states=len(eligible),
        terminal_divergences=terminal_divergences,max_null_return_error=null_error,max_errors=errors,
        Q11_regression="all Q11 real selected actions match unchanged frozen Q11 candidate operator on every visited state; historical CURRENT candidate regression covered by unchanged unit tests",
        null_controls=int((~c.divergent).sum()),raw_sha256=completion["sha256"],
        source_hashes_valid=True,CRN_valid=True,primary_counterfactual_reward_count=2,
        continuation_policy="same pi_ab in both branches; authoritative C2.0 primitive unchanged")
    run.dump(run.OUT/"validation_summary.json",summary)
    print(json.dumps(summary["counts"]),flush=True)
    return summary


if __name__=="__main__":
    validate()
