import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from hls.rq1_allocation import Alert, Analyst
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    CONTINUOUS, WEEKDAY_9_TO_17, simulate,
)


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


def test_deadline_uses_natural_time_from_original_arrival():
    a = roster()
    result = simulate([Alert("a", 16, "x", 24)], a, {"L2-A": {"x": 3}},
                      {"L2-A": WEEKDAY_9_TO_17}, horizon=40)
    assert result.assignments[0].completion == 35
    assert result.episodes[0].status == "completed_late"
