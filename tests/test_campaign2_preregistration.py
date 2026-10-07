"""Static pre-experiment checks; no policy calls, RNG draws or simulations."""

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from hls.campaign1_protocol import CONFIGURATION_IDS, PARAMETERS, SCENARIO_IDS
from hls.campaign1_test_range import HISTORIES
from hls.discover_v0 import EXACT_TOL, JOINT_ACTIONS
from hls.finite_problem_belief import ProspectivePolicyMode
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results/foundations/campaign2_preregistration/pre_experiment_campaign2_preregistration.json"
PREREQUISITE = "c7071769cc583f3352305363eff2e6ade27de97e"


@pytest.fixture(scope="module")
def prereg():
    return json.loads(MANIFEST.read_text())


def test_prerequisite_and_source_hashes_are_frozen(prereg):
    assert prereg["prerequisite_C2_commit"] == PREREQUISITE
    subprocess.run(["git","merge-base","--is-ancestor",PREREQUISITE,"HEAD"],cwd=ROOT,check=True)
    for path,digest in prereg["source_hashes"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    theory=json.loads((ROOT/"results/foundations/campaign2_theory/pre_experiment_campaign2_theory.json").read_text())
    for path,digest in theory["source_hashes"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path


def test_exact_design_and_disjoint_seed_reservation(prereg):
    design=prereg["design"]
    assert design["scenario_ids"]==list(SCENARIO_IDS)==list(HISTORIES)
    assert design["configuration_ids"]==list(CONFIGURATION_IDS)
    assert prereg["confirmatory_seeds"]==list(range(10,50))
    assert prereg["development_seeds"]==list(range(10))
    assert set(prereg["confirmatory_seeds"]).isdisjoint(prereg["development_seeds"])
    assert len(set(prereg["confirmatory_seeds"]))==40
    assert design["policies"]==dict(zip(("Q00","Q10","Q01","Q11"),(m.name for m in ProspectivePolicyMode)))
    assert design["physics"]==PARAMETERS
    assert design["action_count"]==len(JOINT_ACTIONS)==64
    assert design["tie_tolerance"]==EXACT_TOL
    assert design["hypotheses"]==[list(z) for z in HYPOTHESIS_REPERTOIRE]
    assert design["problem_prior"]==list(UNIFORM_PRIOR)
    assert design["real_Bayes_and_MIS_enabled_for_every_policy"]
    assert design["belief_resets"] and design["capability_persists"]
    assert not design["STATIC_included"] and not design["parameter_sweep"]


def test_planned_counts_come_from_factorial_not_outcomes(prereg):
    d=prereg["design"]; n=prereg["planned_counts_not_executions"]
    seeds=len(prereg["confirmatory_seeds"])
    contexts=len(d["scenario_ids"])*len(d["configuration_ids"])
    assert all(len(h)==d["problems_per_history"]==6 for h in HISTORIES.values())
    h=d["physics"]["horizon_per_problem"]
    ref=contexts*seeds*6*h
    eligible=contexts*seeds*6*(h-1)
    assert n["closed_loop_runs"]==contexts*seeds*4==5120
    assert n["closed_loop_runs_per_policy"]==contexts*seeds==1280
    assert n["closed_loop_real_steps"]==4*ref==92160
    assert n["Q11_reference_states"]==ref==23040
    assert n["eligible_nonterminal_reference_states"]==eligible==15360
    assert n["eligible_states_per_seed"]==eligible//seeds==384
    assert n["terminal_control_states"]==ref-eligible==7680
    assert n["primary_paired_policy_rows"]==eligible*4==61440
    assert n["primary_candidate_landscape_rows"]==eligible*64==983040
    assert n["counterfactual_pairs_including_null_controls"]==eligible*3==46080
    assert n["counterfactual_branches"]==eligible*3*2==92160
    assert n["counterfactual_real_production_steps"]==eligible*3*2*2==184320
    assert n["divergent_consequence_population_sizes"] is None


def test_primary_reference_populations_null_controls_and_weights(prereg):
    p=prereg["populations"]
    assert p["primary_reference_policy"]=="Q11"
    assert p["independent_replication_unit"]=="SEED"
    assert "remaining in {3,2}" in p["decision"]
    assert "exact Xab != X00" in p["consequence"]
    assert "excluded" in p["null_controls"]
    assert "no primary" in p["terminal_controls"]
    assert "NOT unweighted average" in p["conditional_estimator"]
    assert p["retain_seeds_without_events"]
    assert "secondary/exploratory" in p["other_policy_states"]
    # Pure arithmetic illustration of cluster multiplicities, NOT simulated outcomes.
    toy_blocks=((1,1),(3,9))  # (event count, event sum), symbolic clusters A/B
    pooled=sum(v for _,v in toy_blocks)/sum(n for n,_ in toy_blocks)
    assert pooled==2.5 and pooled!=sum(v/n for n,v in toy_blocks)/2
    repeated=(toy_blocks[0],toy_blocks[0],toy_blocks[1])
    assert sum(v for _,v in repeated)/sum(n for n,_ in repeated)==2.2


def test_primary_decision_and_conditional_consequence_definitions(prereg):
    outcomes=prereg["decision_outcomes"]
    for ab in ("10","01","11"):
        assert outcomes["D_"+ab]==f"1[X{ab} != X00]"
    assert outcomes["D_coupled"]=="1[X11 not in {X10,X01}]"
    estimands=prereg["primary_consequence_estimands"]
    assert estimands["policies"]==["Q10","Q01","Q11"]
    assert "structural null-action zeros excluded" in estimands["conditioning"]
    assert "sum(D_ab)" in estimands["p_plus"]
    assert "raw_DeltaG" in estimands["mean_DeltaG"]
    assert "DeltaG<-tolerance" in estimands["mean_negative_DeltaG"]
    assert "abs(DeltaG)<=tolerance" in estimands["p_zero"]
    assert "undefined/null" in estimands["empty_denominator"]


def test_numerical_zero_partition_inherits_tolerance_without_outcome_tuning(prereg):
    rule=prereg["numerical_sign_convention"]
    tol=rule["absolute_tolerance"]
    assert tol==EXACT_TOL
    assert rule["positive"]=="DeltaG > tolerance"
    assert rule["negative"]=="DeltaG < -tolerance"
    assert rule["zero"]=="abs(DeltaG) <= tolerance"
    assert rule["raw_values_preserved"] and not rule["outcome_variance_normalization"]
    for value in (-2*tol,-tol,-tol/2,0,tol/2,tol,2*tol):
        assert sum((value>tol,abs(value)<=tol,value<-tol))==1


def test_counterfactual_and_crn_semantics_are_unchanged(prereg):
    cf=prereg["counterfactual"]; crn=prereg["CRN"]
    assert cf["reward_count"]==2 and cf["remaining_allowed"]==[2,3]
    assert not cf["cross_problem_boundary"]
    assert "SAME pi_ab in BOTH branches" in cf["continuation"]
    assert "remaining-1" in cf["continuation"]
    assert "third reward excluded" in cf["endpoint_caveat"]
    assert "enabled MIS-v2" in cf["real_transitions"]
    assert "epsilon[k],epsilon[k+1]" in crn["counterfactual_innovations"]
    assert not crn["new_counterfactual_draws"]
    assert crn["extra_rollout_replications"]==0
    assert not crn["future_innovations_or_true_z_supplied_to_unknown_planner"]


def test_seed_bootstrap_and_undefined_resample_policy_are_frozen(prereg):
    b=prereg["bootstrap"]
    assert b["unit"]=="SEED" and b["replicates"]==10000
    assert b["draws_per_replicate"]==40 and b["replace"]
    assert b["analysis_seed"]==20261007
    assert b["analysis_seed"] not in prereg["confirmatory_seeds"]+prereg["development_seeds"]
    assert b["RNG"]=="numpy.random.Generator(numpy.random.PCG64(20261007))"
    assert b["interval"]=="percentile 95%"
    assert b["quantiles"]==[.025,.975] and b["quantile_method"]=="linear"
    assert "ALL rows" in b["cluster_rule"] and "multiplicity" in b["cluster_rule"]
    assert "counts/fractions" in b["undefined_resamples"]
    assert "conditional on estimability" in b["undefined_resamples"]
    assert "all undefined => null" in b["undefined_resamples"]
    assert not b["state_independent_resampling_allowed"]
    assert b["draws_executed_during_preregistration"]==0


def test_hypotheses_secondary_model_and_exploratory_boundary(prereg):
    hypotheses=prereg["hypotheses"]
    assert set(hypotheses)=={"H1","H2","H3","H4"}
    assert any("mean D_I_loss difference" in s for s in hypotheses["H1"]["primary"])
    assert any("median D_I_loss difference" in s for s in hypotheses["H1"]["primary"])
    assert not hypotheses["H1"]["logistic_model_confirmatory"]
    assert "D_01 prevalence" in hypotheses["H2"]["primary"]
    assert not hypotheses["H3"]["Gamma_positive_required"]
    assert not hypotheses["H3"]["Gamma_greater_than_C_required"]
    assert hypotheses["H4"]["mismatch_direction"]=="NON-DIRECTIONAL"
    model=hypotheses["H4"]["secondary_confirmatory_model"]
    assert model["terms"]==["intercept","DeltaQ","M","DeltaQ:M"]
    assert model["response"]=="raw DeltaG" and "D_ab=1" in model["type"]
    assert "rank deficiency" in model["non_estimable"] and "do not drop terms" in model["non_estimable"]
    assert not hypotheses["H4"]["causal_moderator_claims_allowed"]
    assert {"DeltaG_problem","DeltaG_history","policy winner maps"}<=set(prereg["exploratory"])
    assert prereg["multiplicity"]["families"]==["H1","H2","H3","H4"]
    assert not prereg["multiplicity"]["subgroup_promotion_allowed"]


def test_falsification_rules_and_postexecution_adaptation_prohibition(prereg):
    assert set(prereg["falsification_rules"])=={"H1","H2","H3","H4"}
    assert "not confirmed" in prereg["falsification_rules"]["H3"]
    assert "non-positive" in prereg["falsification_rules"]["H4"]
    assert {"global Q11 superiority","development usefulness","harmful mismatch"}<=set(prereg["not_required"])
    assert {"hypotheses","primary estimands","eligible-state definitions","counterfactual horizon",
        "continuation policy","CRN","bootstrap method","policies","eta","outcome-dependent exclusions"}<=set(prereg["prohibited_post_execution_adaptations"])


def test_no_confirmatory_execution_result_artifacts_or_frozen_file_changes(prereg):
    audit=prereg["preregistration_contamination_audit"]
    assert all(value==0 or value is False for value in audit.values())
    allowed_results={
        "results/foundations/campaign2_theory/pre_experiment_campaign2_theory.json",
        "results/foundations/campaign2_preregistration/pre_experiment_campaign2_preregistration.json",
    }
    # Existence/name inspection ONLY: never open a possible confirmatory output.
    for directory in (ROOT/"results").glob("**/*campaign2*"):
        if directory.is_dir():
            assert all(str(p.relative_to(ROOT)) in allowed_results for p in directory.rglob("*") if p.is_file())
    allowed_changes={str(MANIFEST.relative_to(ROOT)),
        "docs/experiments/CAMPAIGN_2_PREREGISTRATION.md","tests/test_campaign2_preregistration.py"}
    changed=subprocess.check_output(["git","diff","--name-only",PREREQUISITE,"--"],cwd=ROOT,text=True).splitlines()
    assert set(changed)<=allowed_changes


def test_document_manifest_surface_matches_without_execution(prereg):
    doc=(ROOT/"docs/experiments/CAMPAIGN_2_PREREGISTRATION.md").read_text()
    assert PREREQUISITE in doc
    assert all(s in doc for s in prereg["design"]["scenario_ids"])
    assert all(s in doc for s in prereg["design"]["configuration_ids"])
    assert "5,120 closed-loop runs" in doc and "15,360 nonterminal states" in doc
    assert "10,000 nonparametric seed bootstrap replicates" in doc and "20261007" in doc
    assert "**Seeds 10–49 remain untouched." in doc
