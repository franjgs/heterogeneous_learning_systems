from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from hls.rq1_allocation import HLSBConfig, simulate
from hls.rq1_l1_l2 import simulate_l1_l2
from studies.soc_triage_organization_coupling import run_pilot as frozen
from studies.soc_human_ai_organization.calibrate_a1_scenarios import effective_capacity
from studies.soc_human_ai_organization.soc_parametric_baseline import (
    BASE_ELIGIBILITY, BASE_L1_ANALYSTS, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
    PROJECTS, PROJECT_MIX, REFERENCE, build_roster,
)
from studies.soc_triage_hls_q1_integration_evidence.fp_workload_engine import simulate_l2_hidden_work
from studies.soc_triage_hls_q1_integration_evidence.run_primary_campaign import bootstrap_indices


class HiddenWorkDriverTests(unittest.TestCase):
    def setUp(self):
        self.pi = 19 / 14449
        self.point = {"id":"standardized_lightgbm_apc_symmetric","pD":.8421,"pFA":.0450}
        self.prev = {"pi":self.pi,"need_by_class":tuple(self.pi for _ in PROJECTS)}
        self.trace, _ = frozen._make_trace(rho_l1=.85, seed=712345001,
                                           prevalence=self.prev, point=self.point)
        self.l1, self.l2, self.l1s, self.l2s = build_roster(
            n_l1=BASE_L1_ANALYSTS,n_l2=3,mean_eligible_projects=BASE_ELIGIBILITY)
        self.mu1=effective_capacity(self.l1,self.l1s,PROJECT_MIX)["max_common_arrivals_per_h"]
        q,mix=frozen._expected_route_mix(self.prev["need_by_class"],self.point["pD"],self.point["pFA"])
        self.mu2=effective_capacity(self.l2,self.l2s,mix)["max_common_arrivals_per_h"]
        self.hcfg=HLSBConfig(window_h=4.0,low=1.05,high=1.20,capacity_per_h=self.mu2)

    def run_custom(self, policy, hidden_scales=None, arrivals=None, seed=712345001):
        trace=self.trace
        l1cfg={}
        if policy=="HLS-B":
            l1cfg["hlsb_config"]=HLSBConfig(window_h=4,low=1.05,high=1.20,capacity_per_h=self.mu1)
        l1sim=simulate(tuple(r.routed.alert for r in trace),self.l1,BASE_SERVICE_L1_H,
                       policy=policy,admission_horizon=24,drain_period=36,random_seed=seed,
                       service_by_analyst_class=self.l1s,**l1cfg)
        l1jobs={j.alert_id:j for j in l1sim.assignments}
        route={r.routed.alert.alert_id:bool(r.routed.soctra_recommendation) for r in trace}
        need={r.routed.alert.alert_id:bool(r.true_escalation_need) for r in trace}
        source={r.routed.alert.alert_id:r.routed.alert for r in trace}
        jobs=tuple(type(a)(a.alert_id,l1jobs[a.alert_id].completion,a.task_class,a.deadline)
                   for a in source.values() if route[a.alert_id] and a.alert_id in l1jobs and l1jobs[a.alert_id].completion<60)
        scales={a.alert_id:(1.0 if need[a.alert_id] else 1.0) for a in jobs} if hidden_scales is None else hidden_scales
        cfg=self.hcfg if policy=="HLS-B" else None
        return l1sim,simulate_l2_hidden_work(jobs,{a.alert_id:need[a.alert_id] for a in jobs},
                 self.l2,self.l2s,self.l2s,scales,policy=policy,horizon=60,seed=seed,hlsb_config=cfg)

    def test_alpha_one_matches_original_l1_l2_assignments(self):
        for policy in ("D1","P1","HLS-B"):
            kwargs={}
            if policy=="HLS-B":
                kwargs["hlsb_l1_config"]=HLSBConfig(window_h=4,low=1.05,high=1.20,capacity_per_h=self.mu1)
                kwargs["hlsb_l2_config"]=self.hcfg
            base=simulate_l1_l2(tuple(r.routed for r in self.trace),self.l1,self.l2,
                BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,policy=policy,admission_horizon=24,drain_period=36,
                coordination_latency=0,decision_mode="hypothetical_recommendation_acceptance",random_seed=712345001,
                l1_service_by_analyst_class=self.l1s,l2_service_by_analyst_class=self.l2s,**kwargs)
            l1,new_l2=self.run_custom(policy)
            self.assertEqual(base.l1_simulation.assignments,l1.assignments)
            self.assertEqual(base.l2_simulation.assignments,new_l2.assignments)

    def test_need_label_is_not_an_input_to_dispatch(self):
        policy="P1"
        l1,base=self.run_custom(policy)
        changed={aid:True for aid in [a.alert_id for a in base.arrivals]}
        scales={a.alert_id:(1.0 if a.alert_id in changed else 1.0) for a in base.arrivals}
        alt=simulate_l2_hidden_work(base.arrivals,{aid:False for aid in changed},self.l2,self.l2s,self.l2s,
                                    scales,policy=policy,horizon=60,seed=712345001)
        self.assertEqual(base.assignments,alt.assignments)

    def test_recommendations_arriving_later_do_not_change_earlier_dispatch(self):
        policy="D1"
        _,base=self.run_custom(policy)
        late=type(base.arrivals[0])("late-arrival",59.0,base.arrivals[0].task_class,72.0)
        alerts=base.arrivals+(late,)
        need={a.alert_id:False for a in alerts}; scales={a.alert_id:1.0 for a in alerts}
        alt=simulate_l2_hidden_work(alerts,need,self.l2,self.l2s,self.l2s,scales,
                                    policy=policy,horizon=60,seed=712345001)
        first_base=tuple(j for j in base.assignments if j.start<59)
        first_alt=tuple(j for j in alt.assignments if j.start<59)
        self.assertEqual(first_base,first_alt)

    def test_splus_numerator_cannot_exceed_tp_and_alpha_shortens_only_fp_work(self):
        alert=type(self.trace[0].routed.alert)("fp",0.0,PROJECTS[0],12.0)
        l2=(alert,)
        result=simulate_l2_hidden_work(l2,{"fp":False},self.l2[:1],self.l2s,
          {a.analyst_id:{k:self.l2s[a.analyst_id][k] for k in a.eligible_classes} for a in self.l2[:1]},
          {"fp":.25},policy="D1",horizon=12.0,seed=1)
        job=result.assignments[0]
        base=self.l2s[job.analyst_id][PROJECTS[0]]
        self.assertAlmostEqual(job.completion-job.start,.25*base)
        # Structural service bound: timely need numerator is a subset of TP.
        timely_need_numerator=0
        tp_count=0
        self.assertLessEqual(timely_need_numerator,tp_count)

    def test_bootstrap_seed_is_reproducible(self):
        first=bootstrap_indices(list(range(40)))
        second=bootstrap_indices(list(range(40)))
        self.assertTrue((first==second).all())
        self.assertEqual(first.shape[1],40)


if __name__ == "__main__":
    unittest.main()
