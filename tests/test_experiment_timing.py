import hashlib
import io
import json
from datetime import datetime, timedelta, timezone

import pytest

from hls.experiment_timing import ExperimentTimingLogger, format_duration


class FakeTime:
    def __init__(self):
        self.seconds = 0.0
        self.origin = datetime(2026, 9, 24, 9, 20, 14, tzinfo=timezone.utc)

    def perf(self):
        return self.seconds

    def wall(self):
        return self.origin + timedelta(seconds=self.seconds)

    def advance(self, seconds):
        self.seconds += seconds


def logger(tmp_path, fake, stream=None, *, resume=True, persist=True):
    return ExperimentTimingLogger(
        "Fixture experiment", 3, {"fast": 2, "deep": 1},
        state_path=tmp_path / "timing.json", resume=resume, persist=persist,
        stream=stream or io.StringIO(), clock=fake.perf, wall_clock=fake.wall,
    )


def test_basic_format_elapsed_item_duration_and_eta(tmp_path):
    fake, output = FakeTime(), io.StringIO()
    timing = logger(tmp_path, fake, output)
    timing.header(["Device: CPU", "TEST: CLOSED"])
    timing.phase(1, 2, "Training")
    timing.start_item("f0", "fast", 1, "seed=0 state=F0")
    fake.advance(12)
    timing.item_progress("epoch 1/3", 12)
    timing.finish_item()
    eta, provisional = timing.eta()
    assert eta == pytest.approx(24)
    assert provisional is True
    text = output.getvalue()
    assert "Started: 2026-09-24 11:20:14 +0200" in text
    assert "[fit   1/3] seed=0 state=F0" in text
    assert "unit 00:00:12 | fit 00:00:12" in text
    assert "last 00:00:12" in text
    assert format_duration(None) == "--:--:--"


def test_category_eta_uses_observed_category_means(tmp_path):
    fake = FakeTime()
    timing = logger(tmp_path, fake)
    timing.start_item("f0", "fast", 1, "f0")
    fake.advance(10)
    timing.finish_item()
    timing.start_item("d0", "deep", 2, "d0")
    fake.advance(30)
    timing.finish_item()
    eta, provisional = timing.eta()
    assert eta == pytest.approx(10)
    assert provisional is False


def test_persistence_restart_session_vs_accumulated(tmp_path):
    fake = FakeTime()
    first = logger(tmp_path, fake)
    first.start_item("f0", "fast", 1, "f0")
    fake.advance(20)
    first.finish_item()
    assert first.session_elapsed == 20
    assert first.accumulated_seconds == 20

    second = logger(tmp_path, fake, resume=True)
    assert second.session_elapsed == 0
    assert second.accumulated_seconds == 20
    second.start_item("d0", "deep", 2, "d0")
    fake.advance(30)
    second.finish_item()
    assert second.session_elapsed == 30
    assert second.accumulated_seconds == 50
    persisted = json.loads((tmp_path / "timing.json").read_text())
    assert [record["duration_seconds"] for record in persisted["records"] if record["status"] == "complete"] == [20, 30]


def test_adopt_reused_artifact_does_not_consume_session(tmp_path):
    fake = FakeTime()
    timing = logger(tmp_path, fake)
    timing.adopt_completed("f0", "fast", 42.5, "reused F0")
    timing.adopt_completed("f0", "fast", 42.5, "reused F0")
    assert timing.session_elapsed == 0
    assert timing.accumulated_seconds == 42.5
    assert timing.category_summary()["fast"]["count"] == 1


def test_summary_statistics_and_final_output(tmp_path):
    fake, output = FakeTime(), io.StringIO()
    timing = logger(tmp_path, fake, output)
    for index, duration in enumerate((10, 20), 1):
        timing.start_item(f"f{index}", "fast", index, f"fast {index}")
        fake.advance(duration)
        timing.finish_item()
    summary = timing.category_summary()["fast"]
    assert summary == {
        "count": 2, "total_seconds": 30.0, "mean_seconds": 15.0,
        "median_seconds": 15.0, "min_seconds": 10.0, "max_seconds": 20.0,
    }
    timing.finish(extra_lines=["Compatibility: PASS"])
    assert "Experiment accumulated: 00:00:30" in output.getvalue()
    assert "Compatibility: PASS" in output.getvalue()


def test_interruption_persists_completed_only_and_shows_restart(tmp_path):
    fake, output = FakeTime(), io.StringIO()
    timing = logger(tmp_path, fake, output)
    timing.start_item("f0", "fast", 1, "f0")
    fake.advance(5)
    timing.finish_item()
    timing.start_item("f1", "fast", 2, "f1")
    fake.advance(3)
    timing.interrupt("python run.py", KeyboardInterrupt())
    records = json.loads((tmp_path / "timing.json").read_text())["records"]
    assert records[0]["duration_seconds"] == 5
    assert records[1]["status"] == "interrupted"
    assert records[1]["duration_seconds"] is None
    assert "completed fits: 1/3" in output.getvalue()
    assert "restart command: python run.py" in output.getvalue()


def test_dry_run_mode_does_not_persist(tmp_path):
    fake = FakeTime()
    timing = logger(tmp_path, fake, persist=False)
    timing.header(["DRY RUN"])
    assert not (tmp_path / "timing.json").exists()


def test_timing_metadata_does_not_change_scientific_hash(tmp_path):
    scientific = tmp_path / "checkpoint.bin"
    scientific.write_bytes(b"scientific-state")
    before = hashlib.sha256(scientific.read_bytes()).hexdigest()
    fake = FakeTime()
    timing = logger(tmp_path, fake)
    timing.start_item("f0", "fast", 1, "f0")
    fake.advance(1)
    timing.finish_item()
    after = hashlib.sha256(scientific.read_bytes()).hexdigest()
    assert before == after
    assert timing.state_path != scientific


def test_invalid_plan_is_rejected(tmp_path):
    fake = FakeTime()
    with pytest.raises(ValueError, match="sum"):
        ExperimentTimingLogger("bad", 2, {"fit": 1}, state_path=tmp_path / "x", resume=True, clock=fake.perf, wall_clock=fake.wall)
