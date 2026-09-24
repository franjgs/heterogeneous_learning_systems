"""Dependency-free timing and progress logging for long experiments.

Timing state is operational metadata. It must be stored separately from model
or data provenance hashes. Durations use ``time.perf_counter``; wall-clock
timestamps use ``datetime`` only for readable records.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable, TextIO


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "--:--:--"
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class ExperimentTimingLogger:
    """Persist completed work timings and print homogeneous progress.

    ``planned_counts`` maps natural categories to the number of planned items.
    ``resume=True`` continues the current plan generation. ``resume=False``
    starts a new generation while retaining old durations as timing history.
    Dry-runs must use ``persist=False``.
    """

    VERSION = 1

    def __init__(
        self,
        experiment_name: str,
        total_items: int,
        planned_counts: dict[str, int],
        *,
        state_path: Path | None,
        resume: bool,
        persist: bool = True,
        stream: TextIO | None = None,
        clock: Callable[[], float] = time.perf_counter,
        wall_clock: Callable[[], datetime] = datetime.now,
    ):
        if sum(planned_counts.values()) != total_items:
            raise ValueError("planned category counts must sum to total_items")
        self.experiment_name = experiment_name
        self.total_items = total_items
        self.planned_counts = dict(planned_counts)
        self.state_path = state_path
        self.persist = persist
        self.stream = stream or sys.stdout
        self.clock = clock
        self.wall_clock = wall_clock
        self.session_started_perf = clock()
        self.session_started_at = self._timestamp()
        self.session_id = uuid.uuid4().hex
        self.active: dict[str, object] | None = None
        self.historical_timing_available = bool(state_path and state_path.is_file())
        self.state = self._load_state()
        previous_session_complete = self.state.get("last_session", {}).get("status") == "complete"
        if not resume or previous_session_complete:
            self.state["generation"] = int(self.state.get("generation", 0)) + 1
        self.generation = int(self.state.get("generation", 1))
        self._mark_stale_running_interrupted()
        self.state["last_session"] = {"id": self.session_id, "started_at": self.session_started_at, "status": "running"}
        self._save()

    def _timestamp(self) -> str:
        return self.wall_clock().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")

    def _load_state(self) -> dict[str, object]:
        if self.persist and self.state_path and self.state_path.is_file():
            value = json.loads(self.state_path.read_text())
            if value.get("version") != self.VERSION or value.get("experiment_name") != self.experiment_name:
                raise RuntimeError(f"incompatible timing metadata: {self.state_path}")
            return value
        return {
            "version": self.VERSION,
            "experiment_name": self.experiment_name,
            "generation": 1,
            "first_started_at": self.session_started_at,
            "records": [],
            "last_session": {},
        }

    def _mark_stale_running_interrupted(self) -> None:
        for record in self.state["records"]:
            if record.get("status") == "running":
                record["status"] = "interrupted"
                record["finished_at"] = None
                record["duration_seconds"] = None

    def _save(self) -> None:
        if not self.persist or self.state_path is None:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.state, indent=2, sort_keys=True) + "\n")
        temporary.replace(self.state_path)

    def _print(self, message: str = "") -> None:
        print(message, file=self.stream, flush=True)

    @property
    def session_elapsed(self) -> float:
        return self.clock() - self.session_started_perf

    @property
    def accumulated_seconds(self) -> float:
        completed = sum(float(record["duration_seconds"]) for record in self.state["records"] if record.get("status") == "complete" and record.get("duration_seconds") is not None)
        active = self.clock() - float(self.active["started_perf"]) if self.active else 0.0
        return completed + active

    def header(self, lines: list[str]) -> None:
        self._print("=" * 60)
        self._print(self.experiment_name)
        self._print(f"Started: {self.session_started_at}")
        for line in lines:
            self._print(line)
        if not self.historical_timing_available:
            self._print("Historical timing: unavailable (validated artifact timings may be adopted)")
        self._print("=" * 60)

    def phase(self, current: int, total: int, name: str) -> None:
        self._print(f"[{current}/{total}] {name}")

    def _records(self, *, category: str | None = None, current_generation: bool = False) -> list[dict[str, object]]:
        records = [record for record in self.state["records"] if record.get("status") == "complete" and record.get("duration_seconds") is not None]
        if category is not None:
            records = [record for record in records if record.get("category") == category]
        if current_generation:
            records = [record for record in records if int(record.get("generation", -1)) == self.generation]
        return records

    def _completed_ids(self, category: str) -> set[str]:
        return {str(record["item_id"]) for record in self._records(category=category, current_generation=True)}

    def eta(self) -> tuple[float | None, bool]:
        global_durations = [float(record["duration_seconds"]) for record in self._records()]
        if not global_durations:
            return None, False
        total = 0.0
        provisional = False
        global_mean = statistics.fmean(global_durations)
        for category, planned in self.planned_counts.items():
            remaining = max(0, planned - len(self._completed_ids(category)))
            durations = [float(record["duration_seconds"]) for record in self._records(category=category)]
            if durations:
                estimate = statistics.fmean(durations)
            else:
                estimate = global_mean
                provisional = True
            total += remaining * estimate
        return total, provisional

    def start_item(self, item_id: str, category: str, current: int, description: str) -> None:
        if self.active is not None:
            raise RuntimeError("cannot start a timing item while another is active")
        if category not in self.planned_counts:
            raise ValueError(f"unplanned timing category: {category}")
        now_perf = self.clock()
        record = {
            "item_id": item_id,
            "category": category,
            "description": description,
            "generation": self.generation,
            "session_id": self.session_id,
            "started_at": self._timestamp(),
            "finished_at": None,
            "duration_seconds": None,
            "status": "running",
        }
        self.state["records"].append(record)
        self.active = {"record": record, "started_perf": now_perf, "current": current}
        self._save()
        eta, provisional = self.eta()
        suffix = " provisional" if provisional and eta is not None else ""
        self._print(f"[fit {current:>3}/{self.total_items}] {description}")
        self._print(
            f"              elapsed {format_duration(self.session_elapsed)} | "
            f"accumulated {format_duration(self.accumulated_seconds)} | ETA {format_duration(eta)}{suffix}"
        )

    def item_progress(self, label: str, unit_seconds: float, item_elapsed: float | None = None) -> None:
        if self.active is None:
            raise RuntimeError("no active timing item")
        if item_elapsed is None:
            item_elapsed = self.clock() - float(self.active["started_perf"])
        self._print(f"              {label} | unit {format_duration(unit_seconds)} | fit {format_duration(item_elapsed)}")

    def finish_item(self, *, duration_seconds: float | None = None, description: str | None = None) -> float:
        if self.active is None:
            raise RuntimeError("no active timing item")
        record = self.active["record"]
        measured = self.clock() - float(self.active["started_perf"])
        duration = measured if duration_seconds is None else float(duration_seconds)
        record["finished_at"] = self._timestamp()
        record["duration_seconds"] = duration
        record["status"] = "complete"
        current = int(self.active["current"])
        self.active = None
        self._save()
        durations = [float(value["duration_seconds"]) for value in self._records(category=str(record["category"]))]
        eta, provisional = self.eta()
        suffix = " provisional" if provisional and eta is not None else ""
        shown = description or str(record["description"])
        self._print(f"[fit {current:>3}/{self.total_items}] DONE {shown}")
        self._print(
            f"              last {format_duration(duration)} | elapsed {format_duration(self.session_elapsed)} | "
            f"avg {format_duration(statistics.fmean(durations))} | ETA {format_duration(eta)}{suffix}"
        )
        return duration

    def adopt_completed(self, item_id: str, category: str, duration_seconds: float | None, description: str) -> None:
        """Import valid artifact timing once; absent durations stay unavailable."""
        if duration_seconds is None or duration_seconds < 0:
            self._print(f"reuse {item_id} | historical timing unavailable")
            return
        existing = [record for record in self._records(current_generation=True) if record.get("item_id") == item_id]
        if not existing:
            self.state["records"].append(
                {
                    "item_id": item_id, "category": category, "description": description,
                    "generation": self.generation, "session_id": "artifact-history", "started_at": None,
                    "finished_at": None, "duration_seconds": float(duration_seconds), "status": "complete",
                    "source": "validated-artifact",
                }
            )
            self.historical_timing_available = True
            self._save()
        self._print(f"reuse {item_id} | historical {format_duration(duration_seconds)} | session cost 00:00:00")

    def record_auxiliary(self, item_id: str, category: str, duration_seconds: float, *, started_at: str | None = None, finished_at: str | None = None) -> None:
        """Persist non-fit work such as analysis without changing fit counts."""
        self.state["records"].append(
            {
                "item_id": item_id, "category": category, "description": category,
                "generation": self.generation, "session_id": self.session_id,
                "started_at": started_at, "finished_at": finished_at or self._timestamp(),
                "duration_seconds": float(duration_seconds), "status": "complete",
            }
        )
        self._save()

    def category_summary(self) -> dict[str, dict[str, float | int | None]]:
        result: dict[str, dict[str, float | int | None]] = {}
        categories = list(self.planned_counts)
        for extra in sorted({str(record.get("category")) for record in self._records()} - set(categories)):
            categories.append(extra)
        for category in categories:
            values = [float(record["duration_seconds"]) for record in self._records(category=category)]
            result[category] = {
                "count": len(values), "total_seconds": sum(values),
                "mean_seconds": statistics.fmean(values) if values else None,
                "median_seconds": statistics.median(values) if values else None,
                "min_seconds": min(values) if values else None,
                "max_seconds": max(values) if values else None,
            }
        return result

    def finish(self, *, title: str = "COMPLETE", extra_lines: list[str] | None = None) -> None:
        if self.active is not None:
            raise RuntimeError("cannot finish with an active timing item")
        finished_at = self._timestamp()
        self.state["last_session"].update({"finished_at": finished_at, "status": "complete", "session_elapsed_seconds": self.session_elapsed})
        self.state["last_summary"] = self.category_summary()
        self._save()
        self._print("=" * 60)
        self._print(title)
        self._print("Timing")
        for category, values in self.category_summary().items():
            self._print(
                f"  {category:<12} {values['count']:>3} items   total {format_duration(values['total_seconds'])}   "
                f"mean {format_duration(values['mean_seconds'])}"
            )
        if not self.historical_timing_available and not self._records():
            self._print("  historical timing: unavailable")
        self._print(f"Session elapsed:         {format_duration(self.session_elapsed)}")
        self._print(f"Experiment accumulated: {format_duration(self.accumulated_seconds)}")
        self._print(f"Started: {self.session_started_at}")
        self._print(f"Finished: {finished_at}")
        for line in extra_lines or []:
            self._print(line)
        self._print("=" * 60)

    def interrupt(self, restart_command: str, error: BaseException | None = None) -> None:
        if self.active is not None:
            record = self.active["record"]
            record["status"] = "interrupted"
            record["finished_at"] = self._timestamp()
            record["duration_seconds"] = None
            self.active = None
        self.state["last_session"].update({"finished_at": self._timestamp(), "status": "interrupted", "session_elapsed_seconds": self.session_elapsed})
        self._save()
        completed_ids = {str(record["item_id"]) for record in self._records(current_generation=True)}
        completed = min(len(completed_ids), self.total_items)
        records = self._records(current_generation=True)
        last = records[-1]["item_id"] if records else "none"
        self._print("=" * 60)
        self._print(f"{self.experiment_name} INTERRUPTED")
        self._print(f"completed fits: {completed}/{self.total_items}")
        self._print(f"session elapsed: {format_duration(self.session_elapsed)}")
        self._print(f"experiment accumulated: {format_duration(self.accumulated_seconds)}")
        self._print(f"last completed artifact: {last}")
        self._print(f"restart command: {restart_command}")
        if error is not None:
            self._print(f"exception: {type(error).__name__}: {error}")
        self._print("=" * 60)
