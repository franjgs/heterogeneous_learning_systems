import sys
import json
import inspect
import random
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from hls.rq1_allocation import Alert, Analyst, HLSBConfig
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17, Calendar, TimeScale, deadline_from_arrival,
    simulate, simulate_scaled,
)
from studies.soc_triage_hls_q1_integration_evidence.fp_workload_engine import simulate_l2_hidden_work
from hls.rq1_allocation import _dispatch_d1
from studies.soc_triage_hls_availability_robustness.fast_dispatch import dispatch_d1_fast


def roster():
    return [Analyst("L2-A", frozenset({"x"}), {"x": .9})]


def test_continuous_calendar_preserves_assignment():
    a = roster()
    alerts = [Alert("a", 2, "x", 20), Alert("b", 4, "x", 20)]
    result = simulate(alerts, a, {"L2-A": {"x": 3}}, {"L2-A": CONTINUOUS}, horizon=24)
    assert [(x.alert_id, x.analyst_id, x.start, x.completion) for x in result.assignments] == [
        ("a", "L2-A", 2, 5), ("b", "L2-A", 5, 8)]
    assert all(e.status == "completed" for e in result.episodes)


def test_shift_end_suspends_and_resumes_same_analyst():
    a = roster()
    result = simulate([Alert("a", 16, "x", 72)], a, {"L2-A": {"x": 3}},
                      {"L2-A": WEEKDAY_9_TO_17}, horizon=40)
    job = result.assignments[0]
    assert (job.start, job.completion, job.analyst_id) == (16, 35, "L2-A")
    assert result.episodes[0].suspension_h == 16


def test_weekend_work_resumes_monday():
    a = roster()
    result = simulate([Alert("a", 95, "x", 200)], a, {"L2-A": {"x": 10}},
                      {"L2-A": WEEKDAY_9_TO_17}, horizon=190)
    assert result.assignments[0].completion == 179
    assert result.episodes[0].status == "completed"


def test_no_service_outside_available_windows():
    a = roster()
    result = simulate([Alert("a", 0, "x", 72)], a, {"L2-A": {"x": 2}},
                      {"L2-A": WEEKDAY_9_TO_17}, horizon=30)
    assert result.assignments[0].start == 9
    assert result.assignments[0].completion == 11


def test_weekend_cutoff_retains_suspended_task_state():
    a = roster()
    out = simulate([Alert("fri", 112, "x", 140)], a, {"L2-A": {"x": 5}},
                   {"L2-A": WEEKDAY_9_TO_17}, horizon=144)
    task = out.episodes[0]
    assert task.status == "suspended"
    assert task.analyst_id == "L2-A"
    assert task.remaining_service_h == 4
    assert task.suspension_h == 31
    assert dict(out.work_done_by_alert)["fri"] == 1


def test_executed_segments_never_cross_unavailable_time():
    cal = WEEKDAY_9_TO_17
    a = roster()
    out = simulate([Alert("overnight", 16, "x", 100)], a, {"L2-A": {"x": 3}},
                   {"L2-A": cal}, horizon=40)
    assert out.assignments[0].completion == 35
    for _aid, _analyst, start, end in out.work_segments:
        cursor = start
        while cursor < end:
            assert cal.available(cursor + min(.25, (end-cursor)/2))
            cursor += .25


def test_deadline_uses_natural_time_from_original_arrival():
    a = roster()
    result = simulate([Alert("a", 16, "x", 24)], a, {"L2-A": {"x": 3}},
                      {"L2-A": WEEKDAY_9_TO_17}, horizon=40)
    assert result.assignments[0].completion == 35
    assert result.episodes[0].status == "completed_late"


def test_weekday_8x5_6x7_sunday_and_week_rollover():
    weekday = Calendar(tuple((d, 9, 17) for d in (0, 2, 5, 6, 1)))
    assert sum(weekday.available(h + 0.5) for h in range(0, 168)) == 40
    six_by_seven = Calendar(tuple((d, 10, 16) for d in range(7)))
    assert sum(six_by_seven.available(h + 0.5) for h in range(168)) == 42
    sunday_overnight = Calendar(((6, 22, 4),))
    assert sunday_overnight.available(166) and sunday_overnight.available(1)
    assert sunday_overnight.next_change(166) == 172
    assert sunday_overnight.available(168) is True
    assert sunday_overnight.available(172) is False


def test_multiple_suspensions_retain_owner_and_effective_work():
    a = roster()
    cal = Calendar(((0, 9, 10), (2, 9, 10), (4, 9, 10)))
    out = simulate([Alert("long", 9, "x", 500)], a, {"L2-A": {"x": 2.5}},
                   {"L2-A": cal}, horizon=300)
    job = out.assignments[0]
    assert job.analyst_id == "L2-A"
    assert out.work_done_by_alert == (("long", 2.5),)
    assert len(out.work_segments) == 3
    assert job.completion == 105.5


def test_deadline_independent_of_severity_and_historical_offsets():
    assert deadline_from_arrival(5, "high", explicit_hours=72) == 77
    old = {"high": 1.0, "medium": 4.0, "low": 12.0}
    assert [deadline_from_arrival(5, s, by_severity=old) for s in old] == [6, 9, 17]


def test_uniform_time_scale_preserves_schedule_and_scales_outputs():
    a = roster()
    alerts = [Alert("a", 16, "x", 72)]
    base = simulate(alerts, a, {"L2-A": {"x": 3}}, {"L2-A": WEEKDAY_9_TO_17}, horizon=40)
    scaled = simulate_scaled(alerts, a, {"L2-A": {"x": 3}}, {"L2-A": WEEKDAY_9_TO_17},
                             horizon=40, scale=TimeScale(60))
    assert [(j.start / 60, j.completion / 60) for j in scaled.assignments] == [
        (j.start, j.completion) for j in base.assignments]
    assert scaled.work_done_by_alert[0][1] == base.work_done_by_alert[0][1] * 60


@pytest.mark.parametrize("policy", ["D1", "P1", "WAPS"])
def test_continuous_engine_matches_historical_assignments_and_completion(policy):
    analysts = [Analyst("L2-A", frozenset({"x"}), {"x": .9}),
                Analyst("L2-B", frozenset({"x"}), {"x": .8})]
    arrivals = [Alert("a", 0, "x", 40), Alert("b", 1, "x", 40), Alert("c", 4, "x", 40)]
    service = {a.analyst_id: {"x": 3.0} for a in analysts}
    waps = HLSBConfig(window_h=4, low=1.05, high=1.2, capacity_per_h=.4)
    ours = simulate(arrivals, analysts, service,
                    {a.analyst_id: CONTINUOUS for a in analysts}, horizon=24,
                    policy=policy, seed=17, waps_config=waps if policy == "WAPS" else None)
    historical = simulate_l2_hidden_work(
        arrivals, {a.alert_id: True for a in arrivals}, analysts, service, service,
        {a.alert_id: 1.0 for a in arrivals}, policy="HLS-B" if policy == "WAPS" else policy,
        horizon=24, seed=17, hlsb_config=waps if policy == "WAPS" else None)
    project = lambda jobs: [(j.alert_id, j.analyst_id, j.start, j.completion, j.competence) for j in jobs]
    assert project(ours.assignments) == project(historical.assignments)
    assert dict(ours.work_done_by_alert) == {j.alert_id: 3.0 for j in historical.assignments}
    timely_new = sum(j.completion <= next(a.deadline for a in arrivals if a.alert_id == j.alert_id)
                     for j in ours.assignments)
    timely_old = sum(j.completion <= next(a.deadline for a in arrivals if a.alert_id == j.alert_id)
                     for j in historical.assignments)
    assert timely_new == timely_old
    util_new = {a.analyst_id: sum(j.completion-j.start for j in ours.assignments if j.analyst_id == a.analyst_id) / 24
                for a in analysts}
    util_old = {a.analyst_id: sum(j.completion-j.start for j in historical.assignments if j.analyst_id == a.analyst_id) / 24
                for a in analysts}
    assert util_new == util_old


def test_dispatcher_cannot_receive_hidden_need_or_fp_labels():
    params = set(inspect.signature(simulate).parameters)
    assert not ({"need_by_id", "true_escalation_need", "is_fp", "is_tp"} & params)


def test_fast_d1_matches_frozen_dispatch_and_rng_exactly():
    analysts = [Analyst("A", frozenset({"x", "y"}), {"x": .7, "y": .8}),
                Analyst("B", frozenset({"x"}), {"x": .9}),
                Analyst("C", frozenset({"y"}), {"y": .6})]
    alerts = {f"a{i}": Alert(f"a{i}", i/10, "x" if i % 2 else "y", 3 + i/3)
              for i in range(40)}
    service = lambda analyst, alert: .5 + .05 * ((ord(analyst.analyst_id)-65) + (1 if alert.task_class == "x" else 2))
    for seed in range(40):
        r1, r2 = random.Random(seed), random.Random(seed)
        t1, t2 = [], []
        old = _dispatch_d1(analysts, alerts, 1.25, service, r1, trace=t1)
        new = dispatch_d1_fast(analysts, alerts, 1.25, service, r2, trace=t2)
        assert [(a.analyst_id,x.alert_id) for a,x in old] == [(a.analyst_id,x.alert_id) for a,x in new]
        assert t1 == t2
        assert r1.random() == r2.random()


def test_historical_campaign_reference_metric_is_recorded():
    path = Path(__file__).resolve().parents[1] / "config" / "historical_reference_summary.json"
    ref = json.loads(path.read_text())
    assert ref["source_commit"] == "9772abae1bfcd2c810760e68ecd8fba107d320f0"
    m = ref["aggregate_reference"]
    assert m["timely_needs"] == 340 and m["total_needs"] == 474
    assert m["S_plus_pooled"] == m["timely_needs"] / m["total_needs"]
    assert m["L1_backlog_H_mean"] == 219.755
    assert m["L2_backlog_H_mean"] == 1.2075
    assert m["utilization_L1_mean_H_mean"] == 0.994798829497767
