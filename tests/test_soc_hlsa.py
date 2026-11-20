from hls.rq1_allocation import Alert, Analyst, HLSAConfig, HLSBConfig, hlsa_pressure, simulate
from hls.rq1_l1_l2 import RoutedAlert, simulate_l1_l2


def fixture():
    analysts = (Analyst("a", frozenset({"x"}), {"x": .8}),
                Analyst("b", frozenset({"x"}), {"x": .7}))
    alerts = tuple(Alert(str(i), i * .05, "x", i * .05 + .5) for i in range(12))
    return alerts, analysts


def run(policy, config=HLSAConfig()):
    alerts, analysts = fixture()
    return simulate(alerts, analysts, {"x": .3}, policy=policy,
                    admission_horizon=1., drain_period=2., random_seed=7,
                    hlsa_config=config)


def test_forced_modes_reproduce_original_assignments_and_metrics():
    d1 = run("D1")
    p1 = run("P1")
    forced_d1 = run("HLS-A", HLSAConfig(low=100., high=101.))
    forced_p1 = run("HLS-A", HLSAConfig(low=0., high=100., initial_mode="P1"))
    assert forced_d1.assignments == d1.assignments
    assert forced_p1.assignments == p1.assignments
    assert forced_d1.after_drain == d1.after_drain
    assert forced_p1.after_drain == p1.after_drain


def test_hysteresis_reproducibility_and_feasibility():
    result = run("HLS-A", HLSAConfig(low=.5, high=1.2))
    assert result == run("HLS-A", HLSAConfig(low=.5, high=1.2))
    assert {x.mode for x in result.hlsa_history} == {"D1", "P1"}
    assert any(x.switched for x in result.hlsa_history)
    ids = [x.alert_id for x in result.assignments]
    assert len(ids) == len(set(ids))
    assert all(x.analyst_id in {"a", "b"} for x in result.assignments)
    for earlier, later in zip(result.hlsa_history, result.hlsa_history[1:]):
        assert earlier.time <= later.time
        if later.switched:
            assert (later.mode == "P1" and later.pressure >= 1.2) or (later.mode == "D1" and later.pressure <= .5)


def test_pressure_observes_only_current_state_and_restricted_eligibility():
    a = Analyst("a", frozenset({"x"}), {"x": .8})
    b = Analyst("b", frozenset({"y"}), {"y": .8})
    x = Alert("now", 0., "x", 1.)
    service = lambda analyst, alert: .2
    assert hlsa_pressure({}, (a, b), {}, {}, service) == 0.
    assert hlsa_pressure({"now": x}, (a, b), {}, {}, service) == 1.
    assert hlsa_pressure({"now": x}, (a, b), {"a": object()}, {}, service) == 2.


def test_l1_l2_forced_mode_matches_fixed_policy():
    alerts, analysts = fixture()
    routed = tuple(RoutedAlert(alert, False, int(alert.alert_id) % 3 == 0) for alert in alerts)
    def run_two(policy, config):
        return simulate_l1_l2(routed, analysts, analysts, {"x": .3}, {"x": .3},
                              policy=policy, admission_horizon=1., drain_period=2.,
                              coordination_latency=0., decision_mode="hypothetical_recommendation_acceptance",
                              random_seed=7, hlsa_config=config)
    for policy, config in (("D1", HLSAConfig(low=100., high=101.)),
                           ("P1", HLSAConfig(low=0., high=100., initial_mode="P1"))):
        fixed = run_two(policy, HLSAConfig())
        adaptive = run_two("HLS-A", config)
        assert adaptive.l1_simulation.assignments == fixed.l1_simulation.assignments
        assert adaptive.l2_simulation.assignments == fixed.l2_simulation.assignments
        assert adaptive.after_drain == fixed.after_drain


def test_direct_diagnostics_do_not_change_trajectory_or_rng():
    alerts, analysts = fixture()
    routed = tuple(RoutedAlert(alert, False, int(alert.alert_id) % 3 == 0) for alert in alerts)
    def run_traced(l1_trace=None, l2_trace=None):
        return simulate_l1_l2(routed, analysts, analysts, {"x": .3}, {"x": .3},
                              policy="HLS-A", admission_horizon=1., drain_period=2.,
                              coordination_latency=0., decision_mode="hypothetical_recommendation_acceptance",
                              random_seed=7, hlsa_config=HLSAConfig(.5, 1.2),
                              l1_diagnostic_trace=l1_trace, l2_diagnostic_trace=l2_trace)
    original = run_traced()
    l1_trace, l2_trace = [], []
    traced = run_traced(l1_trace, l2_trace)
    assert traced == original
    assert len(l1_trace) == len(traced.l1_simulation.hlsa_history)
    assert len(l2_trace) == len(traced.l2_simulation.hlsa_history)
    assert all(row["executed"] in (row["d1"], row["p1"]) for row in l1_trace+l2_trace)


def test_hlsb_uses_only_arrivals_seen_and_is_reproducible():
    alerts, analysts = fixture()
    config = HLSBConfig(0.25, 0.8, 1.2, 4.0)
    def run_with(rows):
        return simulate(rows, analysts, {"x": .3}, policy="HLS-B", admission_horizon=1.,
                        drain_period=2., random_seed=7, hlsb_config=config)
    full = run_with(alerts)
    assert full == run_with(alerts)
    earlier = tuple(a for a in alerts if a.arrival <= 0.25)
    prefix = run_with(earlier)
    a = [(x.time, x.mode, x.pressure) for x in full.hlsa_history if x.time < 0.25]
    b = [(x.time, x.mode, x.pressure) for x in prefix.hlsa_history if x.time < 0.25]
    assert a == b
    assert {x.mode for x in full.hlsa_history} == {"D1", "P1"}
