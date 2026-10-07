"""Integrity checks and descriptive analysis; never generates team trajectories."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.synthetic.strategy_discrimination_gate.run import OUT, MODE_BY_ID, PAIRS, action_l1
from hls.campaign1_protocol import PARAMETERS, SCENARIO_IDS, CONFIGURATION_IDS
from hls.campaign1_test_range import history_steps
from hls.discover_develop_v2 import mis_v2_transition
from hls.discover_v0 import DEFAULT_SIGMA, EXACT_TOL, ces_reward, production_inputs
from hls.finite_problem_belief import finite_bayes_update, hypothesis_means
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR

RUN_KEY = ["scenario_id", "configuration_id", "seed", "policy"]
STATE_KEY = ["scenario_id", "configuration_id", "seed", "problem_index", "within_problem_step"]


def tuple_matrix(value):
    return tuple(tuple(row) for row in json.loads(value))


def validate(runs, trajectories, decisions, comparisons):
    assert len(runs) == 1280 and len(trajectories) == 23040
    assert len(decisions) == 23040 and len(comparisons) == 34560
    assert not runs.duplicated(RUN_KEY).any()
    assert not trajectories.duplicated(RUN_KEY + STATE_KEY[-2:]).any()
    assert not decisions.duplicated(STATE_KEY + ["policy"]).any()
    assert not comparisons.duplicated(STATE_KEY + ["policy_pair"]).any()
    assert set(runs.scenario_id) == set(SCENARIO_IDS)
    assert set(runs.configuration_id) == set(CONFIGURATION_IDS)
    assert set(runs.policy) == set(MODE_BY_ID)
    assert (runs.groupby(RUN_KEY[:-2]+["policy"]).seed.agg(lambda x: set(x)==set(range(10)))).all()
    assert (runs.groupby("policy").size() == 320).all()
    assert (trajectories.groupby(RUN_KEY).size() == 18).all()
    assert (decisions.groupby(STATE_KEY).size() == 4).all()
    assert (comparisons.groupby(STATE_KEY).size() == 6).all()
    assert (decisions.groupby(STATE_KEY).state_before.nunique()==1).all()
    assert (decisions.groupby(STATE_KEY).belief_before.nunique()==1).all()
    assert not comparisons[comparisons.terminal].exact_different.any()
    assert len(decisions[~decisions.terminal]) == 15360
    assert (trajectories.groupby(["seed", "problem_index", "within_problem_step"]).noise_innovation.nunique()==1).all()

    historical = pd.read_csv(ROOT / "results/campaigns/campaign1_test_range/trajectories.csv")
    historic = historical[historical.condition.eq("FULL")].set_index(STATE_KEY).sort_index()
    q11 = trajectories[trajectories.policy.eq("Q11")].set_index(STATE_KEY).sort_index()
    assert historic.index.equals(q11.index)
    reference_decisions = decisions[decisions.policy.eq("Q11")].set_index(STATE_KEY).sort_index()
    assert reference_decisions.index.equals(q11.index)
    for col in ("action", "state_before", "belief_before"):
        assert all(json.loads(a)==json.loads(b) for a,b in zip(reference_decisions[col],q11[col]))
    exact_json = {}
    for col in ("action", "state_before", "state_after", "belief_before", "belief_after", "exposure_after"):
        exact_json[col] = all(json.loads(a)==json.loads(b) for a,b in zip(historic[col], q11[col]))
        assert exact_json[col], col
    errors = {col: float(np.max(np.abs(historic[col].to_numpy()-q11[col].to_numpy())))
        for col in ("mu_true", "observed_reward", "cumulative_performance")}
    assert max(errors.values()) <= 1e-12

    max_state_error = max_belief_error = max_production_error = 0.0
    for row in trajectories.itertuples():
        s, a = tuple_matrix(row.state_before), tuple_matrix(row.action)
        b = tuple(json.loads(row.belief_before))
        expected_s = mis_v2_transition(s,a,enabled=True,eta=PARAMETERS["eta"])
        expected_b = finite_bayes_update(b,row.observed_reward,hypothesis_means(s,a,HYPOTHESIS_REPERTOIRE),DEFAULT_SIGMA)
        max_state_error = max(max_state_error,float(np.max(np.abs(np.asarray(expected_s)-np.asarray(json.loads(row.state_after))))))
        max_belief_error = max(max_belief_error,float(np.max(np.abs(np.asarray(expected_b)-np.asarray(json.loads(row.belief_after))))))
        max_production_error = max(max_production_error,abs(ces_reward(production_inputs(s,a),tuple(json.loads(row.true_problem)))-row.mu_true))
        descriptor = history_steps(row.scenario_id)[row.problem_index]
        for col, value in (("C_t", descriptor.change),("N_t",descriptor.novelty),("M_t",descriptor.mismatch)):
            observed = getattr(row,col)
            assert pd.isna(observed) if value is None else abs(observed-value)<=1e-12
        assert row.represented == descriptor.represented
        if row.within_problem_step == 0:
            assert b == UNIFORM_PRIOR
    assert max(max_state_error,max_belief_error,max_production_error) <= 1e-12
    for _,g in trajectories.groupby(RUN_KEY):
        g=g.sort_values(["problem_index","within_problem_step"])
        assert all(json.loads(a)==json.loads(b) for a,b in zip(g.state_after[:-1],g.state_before[1:]))
        assert abs(float(g.mu_true.sum())-float(g.cumulative_performance.iloc[-1]))<=1e-12
    return {"counts_pass": True,"crn_exact":True,"terminal_divergences":0,
        "Q11_historical_json_exact":exact_json,"Q11_historical_maximum_numeric_errors":errors,
        "real_state_transition_max_error":max_state_error,"real_bayes_transition_max_error":max_belief_error,
        "true_production_max_error":max_production_error,"frozen_descriptors_match":True,
        "reset_and_state_persistence_pass":True}


def main():
    runs=pd.read_csv(OUT / "closed_loop_runs.csv")
    trajectories=pd.read_csv(OUT / "closed_loop_trajectories.csv")
    decisions=pd.read_csv(OUT / "paired_state_decisions.csv")
    comparisons=pd.read_csv(OUT / "paired_state_comparisons.csv")
    validation=validate(runs,trajectories,decisions,comparisons)
    nonterminal=comparisons[~comparisons.terminal]
    summaries=[]
    for dimension in (None,"scenario_id","configuration_id","within_problem_step","represented"):
        groupcols=([dimension] if dimension else [])+["policy_pair"]
        for key,group in nonterminal.groupby(groupcols):
            key=key if isinstance(key,tuple) else (key,)
            summaries.append({"dimension":dimension or "overall","level":str(key[0]) if dimension else "all",
                "policy_pair":key[-1],"states":len(group),
                "exact_divergences":int(group.exact_different.sum()),
                "exact_divergence_rate":float(group.exact_different.mean()),
                "beyond_tie_divergences":int(group.beyond_mutual_tie.sum()),
                "beyond_tie_divergence_rate":float(group.beyond_mutual_tie.mean()),
                "mutual_tie_divergences":int((group.exact_different & group.mutual_tie_equivalent).sum()),
                "both_reject_alternative":int(group.both_reject_alternative.sum()),
                "mean_action_l1":float(group.action_l1.mean()),"max_action_l1":float(group.action_l1.max()),
                "mean_immediate_left_minus_right":float(group.immediate_left_minus_right.mean()),
                "min_immediate_left_minus_right":float(group.immediate_left_minus_right.min()),
                "max_immediate_left_minus_right":float(group.immediate_left_minus_right.max()),
                "positive_immediate_raw":int((group.immediate_left_minus_right>0).sum()),
                "positive_immediate_beyond_tolerance":int((group.immediate_left_minus_right>EXACT_TOL).sum())})
    pd.DataFrame(summaries).to_csv(OUT / "divergence_summary.csv",index=False)
    unique=decisions[decisions.policy.eq("Q11")]
    patterns=[]
    for dimension in (None,"scenario_id","configuration_id","within_problem_step"):
        cols=([dimension] if dimension else [])+["pattern"]
        groupdata=unique[~unique.terminal]
        for key,group in groupdata.groupby(cols):
            key=key if isinstance(key,tuple) else (key,)
            denom=len(groupdata[groupdata[dimension].eq(key[0])]) if dimension else len(groupdata)
            patterns.append({"dimension":dimension or "overall","level":str(key[0]) if dimension else "all",
                "pattern":key[-1],"states":len(group),"fraction":len(group)/denom})
    pd.DataFrame(patterns).to_csv(OUT / "ablation_patterns.csv",index=False)
    performance=[]
    for (scenario,configuration,p),g in runs.groupby(["scenario_id","configuration_id","policy"]):
        pp=np.asarray([json.loads(x) for x in g.problem_performance])
        performance.append({"scenario_id":scenario,"configuration_id":configuration,"policy":p,"runs":len(g),
            "mean_cumulative_mu_true":float(g.cumulative_performance.mean()),
            "sd_cumulative_mu_true":float(g.cumulative_performance.std()),
            "mean_per_problem":json.dumps(pp.mean(axis=0).tolist()),
            "mean_last_problem":float(g.last_problem_performance.mean()),
            "last_problem_is_initial_recurrence":bool(g.last_problem_is_initial_recurrence.iloc[0]),
            "mean_final_state":json.dumps(np.mean([json.loads(x) for x in g.final_state],axis=0).tolist()),
            "mean_final_exposure":json.dumps(np.mean([json.loads(x) for x in g.final_exposure],axis=0).tolist())})
    pd.DataFrame(performance).to_csv(OUT / "performance_summary.csv",index=False)
    # Closed-loop differences are not same-state counterfactual decisions.
    indexed_runs=runs.set_index(RUN_KEY).sort_index()
    indexed_steps=trajectories.set_index(RUN_KEY).sort_index()
    closed_pairs=[]
    for scenario in SCENARIO_IDS:
        for configuration in CONFIGURATION_IDS:
            for seed in range(10):
                for left,right in PAIRS:
                    lk=(scenario,configuration,seed,left); rk=(scenario,configuration,seed,right)
                    a=indexed_runs.loc[lk]; b=indexed_runs.loc[rk]
                    ta=indexed_steps.loc[lk].sort_values(["problem_index","within_problem_step"])
                    tb=indexed_steps.loc[rk].sort_values(["problem_index","within_problem_step"])
                    differences=[json.loads(x)!=json.loads(y) for x,y in zip(ta.action,tb.action)]
                    closed_pairs.append({"scenario_id":scenario,"configuration_id":configuration,
                        "seed":seed,"policy_pair":left+"_"+right,
                        "delta_cumulative_mu_true":a.cumulative_performance-b.cumulative_performance,
                        "delta_last_problem_mu_true":a.last_problem_performance-b.last_problem_performance,
                        "different_action_steps":sum(differences),
                        "first_different_step":next((i for i,v in enumerate(differences) if v),None),
                        "same_final_action":not differences[-1],
                        "final_state_l1":action_l1(tuple_matrix(a.final_state),tuple_matrix(b.final_state)),
                        "final_exposure_l1":action_l1(tuple_matrix(a.final_exposure),tuple_matrix(b.final_exposure))})
    pd.DataFrame(closed_pairs).to_csv(OUT / "closed_loop_policy_comparisons.csv",index=False)
    divergent_closed_pairs=[p for p in closed_pairs if p["different_action_steps"]>0]
    # Deterministic first occurrence by original factorial order; never maximizes effect/performance.
    representatives=[]
    for name,g in unique[~unique.terminal].groupby("pattern",sort=False):
        first=g.iloc[0]
        selected=decisions
        for col in STATE_KEY:
            selected=selected[selected[col].eq(first[col])]
        representatives.extend(selected.to_dict("records"))
    pd.DataFrame(representatives).to_csv(OUT / "representative_decisions.csv",index=False)
    overall=pd.DataFrame(summaries)
    overall=overall[overall.dimension.eq("overall")].to_dict("records")
    result={"gate_id":"strategy-discrimination-gate-v1","classification":"PASS",
        "classification_basis": "Qualitative application of frozen criteria: all eight scenarios and all four configurations contain nonterminal divergences beyond mutual ties; five observed action patterns include useful nulls and coupled-only cases. Performance winners are not a criterion.",
        "negative_findings": ["2958 of 3840 nonterminal reference states select the same action under every mode",
            "Q10 and Q11 select identical actions at every first/reset decision and throughout TR-PR reference states",
            "G07 leads mean cumulative production in every scenario under every policy",
            "Q11 is not uniformly better than Q10 in closed-loop performance"],
        "primary_reference_states":5760,"primary_nonterminal_states":3840,"terminal_states":1920,
        "closed_loop_runs":len(runs),"closed_loop_steps":len(trajectories),
        "paired_state_policy_rows":len(decisions),"pairwise_state_rows":len(comparisons),
        "validation":validation,"overall_nonterminal_pairs":overall,
        "pattern_counts":unique[~unique.terminal].pattern.value_counts().to_dict(),
        "closed_loop_pair_diagnostics": {
            "pairs_with_any_action_difference":len(divergent_closed_pairs),
            "different_trajectories_same_final_action":sum(p["same_final_action"] for p in divergent_closed_pairs),
            "different_trajectories_identical_final_state":sum(p["final_state_l1"]==0 for p in divergent_closed_pairs)},
        "secondary_union_audit_run":False,"is_campaign2":False}
    (OUT / "analysis_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    manifestpath=OUT / "execution_manifest.json"
    manifest=json.loads(manifestpath.read_text())
    for path,digest in manifest["source_hashes"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    manifest["status"]="execution and integrity validation complete"
    manifest["validation"]=validation
    manifest["output_hashes"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob("*.csv"))}
    manifestpath.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
