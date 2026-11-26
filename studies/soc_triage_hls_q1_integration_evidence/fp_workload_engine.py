"""Experiment-only L2 event loop for hidden, outcome-dependent realized work.

The dispatchers are imported unchanged from the frozen HLS engine. A dispatcher
receives only alerts, the roster, and an ex ante expected service map. Hidden
need controls the realized service duration inside the environment and is never
passed to a policy callback.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from hls.rq1_allocation import (
    Alert, Analyst, Assignment, HLSBConfig, HLSADecision,
    _dispatch_d1, _dispatch_local_priority,
)


@dataclass(frozen=True)
class L2Outcome:
    assignments: tuple[Assignment, ...]
    arrivals: tuple[Alert, ...]
    switches: tuple[HLSADecision, ...]
    dispatch_epochs: int
    p1_dispatch_epochs: int
    pending_at_cutoff: tuple[str, ...]
    realized_service_hours: float
    realized_offered_hours: float


def simulate_l2_hidden_work(
    arrivals: Sequence[Alert],
    need_by_id: Mapping[str, bool],
    analysts: Sequence[Analyst],
    base_service_by_analyst_class: Mapping[str, Mapping[object, float]],
    forecast_service_by_analyst_class: Mapping[str, Mapping[object, float]],
    realized_scale_by_id: Mapping[str, float],
    *, policy: str, horizon: float, seed: int,
    hlsb_config: HLSBConfig | None = None,
) -> L2Outcome:
    """Run D1/P1/WAPS with hidden variable service duration and fixed horizon.

    ``horizon`` is the terminal cutoff for this pool. All routed arrivals must
    occur strictly before it. The dispatcher sees forecast service, while
    completion events use the hidden realized scale. This encodes an aggregate
    verification-work approximation without giving the dispatcher the label.
    """
    if policy not in {"D1", "P1", "HLS-B"}:
        raise ValueError("policy must be D1, P1 or HLS-B")
    if policy == "HLS-B" and hlsb_config is None:
        raise ValueError("HLS-B requires a capacity configuration")
    rows = tuple(sorted((a for a in arrivals if a.arrival < horizon),
                        key=lambda a: (a.arrival, a.alert_id)))
    if len({a.alert_id for a in rows}) != len(rows):
        raise ValueError("duplicate L2 alert id")
    ids = {a.alert_id for a in rows}
    if ids != set(need_by_id) or ids != set(realized_scale_by_id):
        raise ValueError("hidden outcome/scale mapping must cover routed arrivals exactly")
    if any(not isfinite(float(realized_scale_by_id[aid])) or realized_scale_by_id[aid] <= 0
           for aid in ids):
        raise ValueError("realized scales must be finite and positive")
    analysts = tuple(sorted(analysts, key=lambda a: a.analyst_id))
    analyst_by_id = {a.analyst_id: a for a in analysts}
    arrivals_by_time: dict[float, list[Alert]] = {}
    for a in rows:
        arrivals_by_time.setdefault(a.arrival, []).append(a)
    arrived_times = sorted(arrivals_by_time)
    cursor = 0
    pending: dict[str, Alert] = {}
    running: dict[str, Assignment] = {}
    jobs: list[Assignment] = []
    observed_arrivals: list[float] = []
    rng = random.Random(seed)
    mode_holder = ["D1"]
    now = 0.0
    switches: list[HLSADecision] = []
    p1_epochs = epochs = 0

    def forecast(a: Analyst, x: Alert) -> float:
        return float(forecast_service_by_analyst_class[a.analyst_id][x.task_class])

    def actual(a: Analyst, x: Alert) -> float:
        return float(base_service_by_analyst_class[a.analyst_id][x.task_class]) * float(realized_scale_by_id[x.alert_id])

    while True:
        next_arrival = arrived_times[cursor] if cursor < len(arrived_times) else None
        next_completion = min((job.completion for job in running.values()), default=None)
        candidates = [t for t in (next_arrival, next_completion) if t is not None]
        if now < horizon:
            candidates.append(horizon)
        if not candidates:
            break
        now = min(candidates)
        if cursor < len(arrived_times) and arrived_times[cursor] == now:
            for a in arrivals_by_time[now]:
                pending[a.alert_id] = a
                observed_arrivals.append(now)
            cursor += 1
        for aid in [aid for aid, job in running.items() if job.completion == now]:
            del running[aid]
        if now >= horizon:
            break
        free = [a for a in analysts if a.analyst_id not in running]
        if not free or not pending:
            continue
        strategy = policy
        if policy == "HLS-B":
            assert hlsb_config is not None
            rate = sum(now - hlsb_config.window_h < t <= now for t in observed_arrivals) / hlsb_config.window_h
            pressure = rate / hlsb_config.capacity_per_h
            previous = mode_holder[0]
            if previous == "D1" and pressure >= hlsb_config.high:
                strategy = "P1"
            elif previous == "P1" and pressure <= hlsb_config.low:
                strategy = "D1"
            else:
                strategy = previous
            if strategy != previous:
                switches.append(HLSADecision(now, strategy, pressure, len(pending), len(running), True))
            mode_holder[0] = strategy
        if strategy == "D1":
            selected = _dispatch_d1(free, pending, now, forecast, rng)
        else:
            selected = _dispatch_local_priority(free, pending, now, forecast)
        epochs += 1
        p1_epochs += int(strategy == "P1")
        for analyst, alert in selected:
            del pending[alert.alert_id]
            duration = actual(analyst, alert)
            jobs.append(Assignment(alert.alert_id, analyst.analyst_id, now,
                                   now + duration, analyst.competence[alert.task_class]))
            running[analyst.analyst_id] = jobs[-1]

    completed_hours = sum(max(0.0, min(j.completion, horizon) - j.start) for j in jobs)
    offered_hours = sum(
        sum(float(base_service_by_analyst_class[a.analyst_id][x.task_class])
            for a in analysts if x.task_class in a.eligible_classes)
        / sum(x.task_class in a.eligible_classes for a in analysts)
        * float(realized_scale_by_id[x.alert_id])
        for x in rows
    )
    unfinished = set(pending)
    unfinished.update(aid for aid, job in running.items() if job.completion > horizon)
    # Assignments completed after the cutoff are no longer in ``running``; include them.
    unfinished.update(j.alert_id for j in jobs if j.completion > horizon)
    return L2Outcome(tuple(sorted(jobs, key=lambda j: (j.start, j.analyst_id, j.alert_id))), rows,
                     tuple(switches), epochs, p1_epochs, tuple(sorted(unfinished)),
                     completed_hours, offered_hours)
