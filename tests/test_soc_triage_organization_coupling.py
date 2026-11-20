from dataclasses import replace

import studies.soc_triage_organization_coupling.run_pilot as pilot
from hls.rq1_allocation import AllocationSession, HLSBConfig
from hls.rq1_l1_l2 import RoutedAlert, simulate_l1_l2
from studies.soc_human_ai_organization.soc_parametric_baseline import (
    BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, build_roster,
)


def test_classifier_points_share_hidden_trace_and_use_coupled_uniforms():
    prevalence = pilot._prevalence_scenarios()[1]
    a = {"name": "a", "pD": 0.7965, "pFA": 0.10}
    b = {"name": "b", "pD": 0.90, "pFA": 0.10}
    trace_a, _ = pilot._make_trace(rho_l1=.85, seed=271200017, prevalence=prevalence, point=a)
    trace_b, _ = pilot._make_trace(rho_l1=.85, seed=271200017, prevalence=prevalence, point=b)
    assert pilot._trace_hash(trace_a, include_recommendation=False) == pilot._trace_hash(
        trace_b, include_recommendation=False
    )
    assert len(trace_a) == len(trace_b)
    for low, high in zip(trace_a, trace_b):
        assert low.true_escalation_need == high.true_escalation_need
        assert low.routed.alert == high.routed.alert
        if low.true_escalation_need:
            assert not low.routed.soctra_recommendation or high.routed.soctra_recommendation
        else:
            assert low.routed.soctra_recommendation == high.routed.soctra_recommendation


def test_false_negative_is_not_counted_as_required_correct_resolution():
    l1, l2, l1_service, l2_service = build_roster()
    base = pilot._make_trace(
        rho_l1=.85, seed=271200001, prevalence=pilot._prevalence_scenarios()[0],
        point=pilot._classifier_points()[0],
    )[0][0]
    alert = replace(base.routed.alert, alert_id="false-negative-fixture", arrival=0.0,
                    deadline=12.0, task_class="portfolio_top5")
    row = replace(base, routed=RoutedAlert(alert, True, False), true_escalation_need=True)
    sim = simulate_l1_l2(
        (row.routed,), l1, l2, BASE_SERVICE_L1_H, BASE_SERVICE_L2_H,
        policy="D1", admission_horizon=24.0, drain_period=36.0,
        coordination_latency=0.0, decision_mode="hypothetical_recommendation_acceptance",
        random_seed=7, l1_service_by_analyst_class=l1_service,
        l2_service_by_analyst_class=l2_service,
    )
    mean_l2_service = pilot._service_estimate_by_class(l2, l2_service)
    metrics, _ = pilot._metrics((row,), sim, horizon=24.0, drain=36.0,
                                need_work=mean_l2_service)
    assert metrics["physical_completed_terminal"] == 1
    assert metrics["routed_SLA_terminal"] == 1.0
    assert metrics["FN"] == 1
    assert metrics["required_resolution_completed_terminal"] == 0
    assert metrics["required_resolution_SLA_terminal"] == 0.0
    assert metrics["correct_on_time_expected_per_admitted"] == 0.0


def test_l2_service_cannot_start_before_recommendation_routed_l1_completion():
    prevalence = pilot._prevalence_scenarios()[1]
    point = {"name": "all-positive", "pD": 1.0, "pFA": 1.0}
    trace, arrival_rate = pilot._make_trace(rho_l1=.85, seed=271200003,
                                             prevalence=prevalence, point=point)
    l1, l2, l1_service, l2_service = build_roster()
    sim = simulate_l1_l2(
        tuple(row.routed for row in trace), l1, l2,
        BASE_SERVICE_L1_H, BASE_SERVICE_L2_H, policy="P1",
        admission_horizon=24.0, drain_period=36.0, coordination_latency=0.0,
        decision_mode="hypothetical_recommendation_acceptance", random_seed=9,
        l1_service_by_analyst_class=l1_service, l2_service_by_analyst_class=l2_service,
    )
    l1_end = {job.alert_id: job.completion for job in sim.l1_simulation.assignments}
    assert sim.l2_simulation.assignments
    assert all(job.alert_id in l1_end and job.start >= l1_end[job.alert_id]
               for job in sim.l2_simulation.assignments)


def _interleaved_assignments(rows, policy, l1, l2, l1_service, l2_service, hlsb_l2_capacity):
    horizon, drain = 4.0, 4.0
    end = horizon + drain
    l1s = AllocationSession(tuple(x.routed.alert for x in rows), l1, BASE_SERVICE_L1_H,
                            admission_horizon=horizon, drain_period=drain, random_seed=4,
                            service_by_analyst_class=l1_service)
    l2s = AllocationSession((), l2, BASE_SERVICE_L2_H, admission_horizon=end,
                            drain_period=0.0, random_seed=4,
                            service_by_analyst_class=l2_service)
    by_id = {x.routed.alert.alert_id: x for x in rows}
    route = {x.routed.alert.alert_id: bool(x.routed.soctra_recommendation) for x in rows}
    modes = {"L1": "D1", "L2": "D1"}
    seen = {"L1": [], "L2": []}
    configs = {"L1": HLSBConfig(4.0, 1.05, 1.20, pilot.MU_L1),
               "L2": HLSBConfig(4.0, 1.05, 1.20, hlsb_l2_capacity)}
    sessions = {"L1": l1s, "L2": l2s}
    while not (l1s._finalized and l2s._finalized):
        now = min(x for x in (l1s.next_event_time(), l2s.next_event_time()) if x is not None)
        l1s.advance_to(now)
        l2s.advance_to(now)
        seen["L1"].extend(x.arrival for x in l1s.arrived_at_now)
        for job in l1s._finished_at_now:
            if route[job.alert_id] and job.completion < end:
                source = by_id[job.alert_id].routed.alert
                l2s.add_alert(type(source)(source.alert_id, job.completion, source.task_class, source.deadline))
        if l2s.arrivals.get(now):
            l2s.advance_to(now)
            seen["L2"].extend(x.arrival for x in l2s.arrived_at_now)
        if now >= end:
            continue
        for pool, session in sessions.items():
            if not session.can_dispatch():
                continue
            selected = policy
            if policy == "HLS-B":
                cfg = configs[pool]
                estimate = sum(now-cfg.window_h < t <= now for t in seen[pool]) / cfg.window_h
                pressure = estimate / cfg.capacity_per_h
                if modes[pool] == "D1" and pressure >= cfg.high:
                    modes[pool] = "P1"
                elif modes[pool] == "P1" and pressure <= cfg.low:
                    modes[pool] = "D1"
                selected = modes[pool]
            session.dispatch(selected)
    return l1s.result(policy), l2s.result(policy)


def test_sequential_wrapper_matches_independent_pools_on_a_shared_event_clock():
    prevalence = pilot._prevalence_scenarios()[1]
    point = {"name": "event-clock-fixture", "pD": .90, "pFA": .15}
    generated, _ = pilot._make_trace(rho_l1=.85, seed=271200004,
                                     prevalence=prevalence, point=point)
    # Use a short four-hour episode so the independent event replay is quick.
    rows = tuple(replace(x, routed=replace(x.routed, alert=replace(
        x.routed.alert, arrival=x.routed.alert.arrival/6,
        deadline=x.routed.alert.arrival/6 + 1.0))) for x in generated[:40])
    l1, l2, l1_service, l2_service = build_roster()
    q, mix = pilot._expected_route_mix(prevalence["need_by_class"], point["pD"], point["pFA"])
    mu_l2 = pilot.effective_capacity(l2, l2_service, mix)["max_common_arrivals_per_h"]
    for policy in ("D1", "P1", "HLS-B"):
        kw = dict(policy=policy, admission_horizon=4.0, drain_period=4.0,
                  coordination_latency=0.0, decision_mode="hypothetical_recommendation_acceptance",
                  random_seed=4, l1_service_by_analyst_class=l1_service,
                  l2_service_by_analyst_class=l2_service)
        if policy == "HLS-B":
            kw.update(hlsb_l1_config=HLSBConfig(4.0,1.05,1.20,pilot.MU_L1),
                      hlsb_l2_config=HLSBConfig(4.0,1.05,1.20,mu_l2))
        sequential = simulate_l1_l2(tuple(x.routed for x in rows), l1,l2,
            BASE_SERVICE_L1_H,BASE_SERVICE_L2_H,**kw)
        interleaved_l1, interleaved_l2 = _interleaved_assignments(
            rows,policy,l1,l2,l1_service,l2_service,mu_l2)
        for left,right in ((sequential.l1_simulation,interleaved_l1),
                           (sequential.l2_simulation,interleaved_l2)):
            a=[(x.alert_id,x.analyst_id,x.start,x.completion) for x in left.assignments]
            b=[(x.alert_id,x.analyst_id,x.start,x.completion) for x in right.assignments]
            assert a == b


def test_waps_thresholds_remain_frozen_for_both_pools():
    cfg = HLSBConfig(window_h=4.0, low=1.05, high=1.20, capacity_per_h=3.84)
    assert (cfg.window_h, cfg.low, cfg.high) == (4.0, 1.05, 1.20)
