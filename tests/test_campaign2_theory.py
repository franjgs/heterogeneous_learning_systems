"""Synthetic unit checks only. No sequence runner, seed or research output."""

from copy import deepcopy
import hashlib
import inspect
import json
from math import log
from pathlib import Path
from unittest.mock import patch

import pytest

import hls.campaign2_theory as theory
import hls.finite_problem_belief as planner
from hls.discover_develop_v2 import mis_v2_transition
from hls.discover_v0 import EXACT_TOL, JOINT_ACTIONS, ces_reward, production_inputs, gaussian_quadrature_nodes
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE as MODEL

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_STATES = (
    (((.1, .6), (.5, .5), (.9, .2)), (.2, .5, .3)),
    (((.2, .2), (.2, .2), (.2, .2)), (1/3,) * 3),
    (((.8, .1), (.3, .7), (.6, .4)), (1., 0., 0.)),
)
MODES = (planner.ProspectivePolicyMode.INFORMATION_ONLY,
         planner.ProspectivePolicyMode.DEVELOPMENT_ONLY,
         planner.ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT)


@pytest.mark.parametrize("b,expected", [((1.,), 0.), ((1., 0., 0.), 0.), ((.5, .5), log(2)), ((1/3,)*3, log(3))])
def test_entropy_edge_cases(b, expected):
    assert theory.belief_entropy(b) == pytest.approx(expected, abs=1e-15)


@pytest.mark.parametrize("b", [(), (.2,.2), (-.1,1.1), (float("nan"),)])
def test_entropy_rejects_invalid_inputs(b):
    with pytest.raises(ValueError):
        theory.belief_entropy(b)


@pytest.mark.parametrize("s,b", SYNTHETIC_STATES)
def test_structural_weights_regret_and_permutation(s, b):
    d = theory.structural_descriptors(s,b)
    assert d == theory.structural_descriptors(s,tuple(reversed(b)),tuple(reversed(MODEL)))
    assert d.myopic_regret >= -EXACT_TOL
    assert d.capability_headroom == sum(1-v for row in s for v in row)
    acts=d.hypothesis_myopic_actions
    expected=sum(b[m]*b[n]*(acts[m]!=acts[n]) for m in range(3) for n in range(m+1,3))
    assert d.disagreement == expected
    denom=sum(b[m]*b[n] for m in range(3) for n in range(m+1,3))
    assert d.disagreement_normalized == (expected/denom if denom else None)
    independent=sum(b[m]*(planner.hypothesis_means(s,acts[m],MODEL)[m]
        -planner.hypothesis_means(s,d.belief_myopic_action,MODEL)[m]) for m in range(3))
    assert d.myopic_regret == independent


def test_zero_regret_common_optimum_and_deterministic_belief():
    zero=((0.,0.),)*3
    for b in ((1/3,)*3,(0.,1.,0.)):
        d=theory.structural_descriptors(zero,b)
        assert d.myopic_regret==d.disagreement==0
    d=theory.structural_descriptors(SYNTHETIC_STATES[0][0],(1.,0.,0.))
    assert d.myopic_regret==d.disagreement==d.entropy==0
    assert d.disagreement_normalized is None


@pytest.mark.parametrize("s,b", SYNTHETIC_STATES)
def test_all_64_opportunity_identities_and_independent_continuations(s,b):
    landscape=theory.opportunity_landscape(s,b)
    assert tuple(row.action for row in landscape.candidates)==JOINT_ACTIONS
    discrepancy=0.
    for row in landscape.candidates:
        assert row.cost>=-EXACT_TOL
        q00,q10,q01,q11=row.operator_values
        v0,g=landscape.baseline_continuation,row.immediate
        reconstructions=(g+v0,g+v0+row.A_I,g+v0+row.A_D,g+v0+row.A_ID)
        discrepancy=max(discrepancy,*(abs(a-bb) for a,bb in zip(row.operator_values,reconstructions)),
            abs(row.A_ID-(row.A_I+row.A_D+row.coupling_residual)))
        next_s=mis_v2_transition(s,row.action,enabled=True,eta=.35)
        vd=planner._best_immediate(next_s,b,MODEL)[1]
        vi=vid=0.
        predicted=planner.hypothesis_means(s,row.action,MODEL)
        for probability,mean in zip(b,predicted):
            if probability==0: continue
            for observation,weight in gaussian_quadrature_nodes(mean,.1,3):
                posterior=planner.finite_bayes_update(b,observation,predicted,.1)
                vi+=probability*weight*planner._best_immediate(s,posterior,MODEL)[1]
                vid+=probability*weight*planner._best_immediate(next_s,posterior,MODEL)[1]
        discrepancy=max(discrepancy,abs(vd-row.V_D),abs(vi-row.V_I),abs(vid-row.V_ID))
    print("C2.0 algebraic/continuation maximum discrepancy:",discrepancy)
    assert discrepancy<=2e-15


@pytest.mark.parametrize("residual", [-.25,.25])
def test_coupling_residual_is_not_sign_clamped(residual):
    def values(s,b,model,mode,remaining=2):
        if remaining==1: value=1.
        elif mode==planner.ProspectivePolicyMode.NONE: value=2.
        elif mode==planner.ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT: value=2.4+residual
        else: value=2.2
        return dict.fromkeys(JOINT_ACTIONS,value)
    with patch.object(theory,"_values",side_effect=values):
        landscape=theory.opportunity_landscape(*SYNTHETIC_STATES[0])
    assert all(r.coupling_residual==pytest.approx(residual,abs=1e-15) for r in landscape.candidates)


@pytest.mark.parametrize("s,b", SYNTHETIC_STATES)
def test_diagnostics_leave_every_frozen_policy_action_and_values_unchanged(s,b):
    def select_all():
        return tuple(planner.choose_prospective_action(s,b,MODEL,remaining=2,policy_mode=m,eta=.35)
            for m in planner.ProspectivePolicyMode)
    before=select_all()
    landscape=theory.opportunity_landscape(s,b)
    theory.structural_descriptors(s,b)
    assert select_all()==before
    for idx,mode in enumerate(planner.ProspectivePolicyMode):
        values=planner.prospective_action_values(s,b,MODEL,remaining=2,eta=.35,
            anticipate_information=mode.value[0],anticipate_development=mode.value[1])
        assert all(row.operator_values[idx]==values[row.action] for row in landscape.candidates)


@pytest.mark.parametrize("mode", MODES)
def test_null_forced_action_invariant(mode):
    s=((1.,1.),)*3
    result=theory.two_decision_counterfactual(s,(1.,0.,0.),(.63,.37),remaining=2,
        policy_mode=mode,innovations=(.25,-.4))
    assert result.prospective==result.baseline
    assert result.delta_production==0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("remaining", [2,3])
def test_branch_order_no_mutation_exact_two_steps_real_transitions_and_same_policy(mode,remaining):
    s,b=SYNTHETIC_STATES[0]
    mutable_s=[list(row) for row in s]; mutable_b=list(b)
    original=deepcopy((mutable_s,mutable_b))
    calls=[]
    chooser=theory.choose_prospective_action
    def record(*args,**kwargs):
        calls.append((args,kwargs))
        return chooser(*args,**kwargs)
    with patch.object(theory,"choose_prospective_action",side_effect=record):
        result=theory.two_decision_counterfactual(mutable_s,mutable_b,(.63,.37),remaining=remaining,
            policy_mode=mode,innovations=(.25,-.4))
    reverse=theory.two_decision_counterfactual(mutable_s,mutable_b,(.63,.37),remaining=remaining,
        policy_mode=mode,innovations=(.25,-.4),branch_order=("baseline","prospective"))
    assert result==reverse
    assert (mutable_s,mutable_b)==original
    assert len(calls)==4
    assert [kw["policy_mode"] for _,kw in calls]==[mode,planner.ProspectivePolicyMode.NONE,mode,mode]
    assert [kw["remaining"] for _,kw in calls]==[remaining,remaining,remaining-1,remaining-1]
    assert all(args[2]==MODEL and "true_problem" not in kw for args,kw in calls)
    for branch in (result.prospective,result.baseline):
        assert branch.continuation_policy==mode and len(branch.steps)==2
        assert branch.production_sum==sum(step.mu_true for step in branch.steps)
        first,second=branch.steps
        assert second.state_before==first.state_after and second.belief_before==first.belief_after
        for step,eps in zip(branch.steps,(.25,-.4)):
            assert step.epsilon==eps
            assert step.mu_true==ces_reward(production_inputs(step.state_before,step.action),(.63,.37))
            assert step.observation==step.mu_true+.1*eps
            assert step.belief_after==planner.finite_bayes_update(step.belief_before,step.observation,
                planner.hypothesis_means(step.state_before,step.action,MODEL),.1)
            assert step.state_after==mis_v2_transition(step.state_before,step.action,enabled=True,eta=.35)
    assert result.delta_production==result.prospective.production_sum-result.baseline.production_sum


def test_shared_innovations_do_not_force_equal_observations_or_transitions():
    s,b=SYNTHETIC_STATES[0]
    chooser=theory.choose_prospective_action
    def force_initial(state,belief,model,**kwargs):
        if state==s and belief==b:
            x=JOINT_ACTIONS[21] if kwargs["policy_mode"]==planner.ProspectivePolicyMode.NONE else JOINT_ACTIONS[63]
            return x,0.
        return chooser(state,belief,model,**kwargs)
    with patch.object(theory,"choose_prospective_action",side_effect=force_initial):
        result=theory.two_decision_counterfactual(s,b,(.63,.37),remaining=2,
            policy_mode=MODES[0],innovations=(.25,-.4))
    a,bb=result.prospective.steps[0],result.baseline.steps[0]
    assert a.epsilon==bb.epsilon and a.mu_true!=bb.mu_true
    assert a.observation!=bb.observation
    assert a.observation-bb.observation==pytest.approx(a.mu_true-bb.mu_true,abs=1e-15)
    assert a.belief_after!=bb.belief_after and a.state_after!=bb.state_after


@pytest.mark.parametrize("remaining", [0,1,4,-1,True,2.5])
def test_terminal_and_invalid_problem_positions_rejected_before_execution(remaining):
    with patch.object(theory,"_real_decision",side_effect=AssertionError):
        with pytest.raises(ValueError):
            theory.two_decision_counterfactual(*SYNTHETIC_STATES[0],(.63,.37),remaining=remaining,
                policy_mode=MODES[0],innovations=(0.,0.))


@pytest.mark.parametrize("innovations", [(),(0.,),(0.,0.,0.),(float("nan"),0.)])
def test_counterfactual_requires_exactly_two_finite_innovations(innovations):
    with pytest.raises(ValueError):
        theory.two_decision_counterfactual(*SYNTHETIC_STATES[0],(.63,.37),remaining=2,
            policy_mode=MODES[0],innovations=innovations)


@pytest.mark.parametrize("invalid_mode", [planner.ProspectivePolicyMode.NONE,"Q10",None])
def test_counterfactual_has_no_silent_policy_fallback(invalid_mode):
    with pytest.raises(ValueError):
        theory.two_decision_counterfactual(*SYNTHETIC_STATES[0],(.63,.37),remaining=2,
            policy_mode=invalid_mode,innovations=(0.,0.))


def test_preexperiment_manifest_and_contamination_boundary():
    manifest=json.loads((ROOT/"results/foundations/campaign2_theory/pre_experiment_campaign2_theory.json").read_text())
    assert manifest["confirmatory_seeds"]==list(range(10,50))
    assert manifest["development_seeds"]==list(range(10))
    assert manifest["campaign2_executed"] is False
    assert manifest["scientific_results_generated"]==0
    from hls.campaign1_protocol import PARAMETERS, SCENARIO_IDS, CONFIGURATION_IDS
    assert manifest["physics"]==PARAMETERS
    assert manifest["scenarios"]==list(SCENARIO_IDS)
    assert manifest["probe_configurations"]==list(CONFIGURATION_IDS)
    assert set(manifest["policy_modes"])=={"Q00","Q10","Q01","Q11"}
    assert manifest["hypotheses"]==[list(z) for z in MODEL]
    assert manifest["common_numerics"]["action_count"]==len(JOINT_ACTIONS)==64
    assert manifest["common_numerics"]["tie_tolerance"]==EXACT_TOL
    assert "seed" not in inspect.signature(theory.two_decision_counterfactual).parameters
    source=inspect.getsource(theory)
    assert "Random(" not in source and "random." not in source
    for path,digest in manifest["source_hashes"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    gate=json.loads((ROOT/"results/diagnostics/strategy_discrimination_gate/execution_manifest.json").read_text())
    for name,digest in gate["output_hashes"].items():
        assert hashlib.sha256((ROOT/"results/diagnostics/strategy_discrimination_gate"/name).read_bytes()).hexdigest()==digest
    # No research output path is provided or created by this module or tests.
    assert not (ROOT/"results/campaigns/campaign2").exists()
    assert sorted(p.name for p in (ROOT/"results/foundations/campaign2_theory").iterdir())==["pre_experiment_campaign2_theory.json"]
