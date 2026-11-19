from studies.soc_human_ai_organization.run_a0_baseline_congestion import (
    _all_busy_duration,
    _queue_profile,
)
from hls.rq1_allocation import Alert, AllocationSession, Analyst


def test_queue_profile_processes_same_time_arrival_before_immediate_dispatch():
    result = _queue_profile([0.0, 1.0], [0.0, 1.0], 2.0)
    assert result == {
        "queue_peak": 1,
        "queue_mean_time_weighted": 0.0,
        "queue_waiting_at_cutoff": 0,
    }


def test_queue_profile_conserves_waiting_jobs_through_drain_boundary():
    result = _queue_profile([0.0, 1.0, 1.5], [0.0, 2.0], 3.0)
    assert result["queue_peak"] == 2
    assert result["queue_waiting_at_cutoff"] == 1
    assert result["queue_mean_time_weighted"] == 2.5 / 3.0


def test_all_eligible_busy_duration_is_intersection_of_busy_intervals():
    busy = {"a": [(1.0, 4.0)], "b": [(2.0, 3.0)]}
    assert _all_busy_duration(["a", "b"], busy, 0.0, 5.0) == 1.0


def test_d1_dispatch_leaves_no_free_analyst_with_an_eligible_pending_alert():
    alerts = [Alert("x1", 0.0, "x", 5.0), Alert("x2", 0.0, "x", 5.0),
              Alert("y", 0.0, "y", 5.0)]
    analysts = [Analyst("a", frozenset({"x"}), {"x": .8}),
                Analyst("b", frozenset({"x", "y"}), {"x": .7, "y": .8})]
    session = AllocationSession(alerts, analysts, {"x": 1.0, "y": 1.0},
                                admission_horizon=2.0, random_seed=7)
    session.advance_to(0.0)
    session.dispatch("D1")
    assert not any(alert.task_class in analyst.eligible_classes
                   for alert in session.pending.values()
                   for analyst in session.available_analysts())
