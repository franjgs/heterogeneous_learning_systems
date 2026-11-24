"""Isolated preempt-resume availability simulator for the SOCTRA-HLS study.

Time is elapsed hours from Monday 00:00. Analyst availability is deterministic
and location-free. Dispatchers see only pending alerts and ex ante service.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Mapping, Sequence

from hls.rq1_allocation import Alert, Analyst, Assignment, HLSBConfig, _dispatch_d1, _dispatch_local_priority


@dataclass(frozen=True)
class Calendar:
    windows: tuple[tuple[int, float, float], ...]  # weekday 0=Mon, [start,end) hour

    def available(self, t: float) -> bool:
        day = int(t // 24) % 7
        hour = t % 24
        return any(d == day and start <= hour < end for d, start, end in self.windows)

    def next_change(self, t: float) -> float:
        # All boundaries repeat weekly; advance to the next boundary (or a daily
        # boundary for all-day schedules).
        base = int(t // 168) * 168
        points = sorted({d * 24 + x for d, a, b in self.windows for x in (a, b)}
                        | {d * 24 for d in range(7)} | {168})
        candidates = [base + p for p in points if base + p > t + 1e-10]
        return min(candidates) if candidates else base + 168


CONTINUOUS = Calendar(tuple((d, 0.0, 24.0) for d in range(7)))
WEEKDAY_9_TO_17 = Calendar(tuple((d, 9.0, 17.0) for d in range(5)))


@dataclass(frozen=True)
class Episode:
    alert_id: str
    status: str
    analyst_id: str | None
    remaining_service_h: float
    completion: float | None
    deadline: float
    suspension_h: float


@dataclass(frozen=True)
class Outcome:
    assignments: tuple[Assignment, ...]
    episodes: tuple[Episode, ...]
    statuses: tuple[tuple[str, str], ...]


def simulate(arrivals: Sequence[Alert], analysts: Sequence[Analyst],
             service: Mapping[str, Mapping[object, float]], calendars: Mapping[str, Calendar],
             *, horizon: float, policy: str = "D1", seed: int = 0,
             waps_config: HLSBConfig | None = None) -> Outcome:
    """Run until cutoff. In-progress jobs pause at shift end and resume on same analyst.

    ``Alert.deadline`` is interpreted as absolute natural time from arrival, as in
    the source engine. No terminal drain is included in on-time accounting.
    """
    if policy not in {"D1", "P1", "WAPS", "HLS-B"}:
        raise ValueError("policy must be D1, P1 or WAPS")
    if policy in {"WAPS", "HLS-B"} and waps_config is None:
        raise ValueError("WAPS requires the frozen window, hysteresis and capacity configuration")
    analysts = tuple(sorted(analysts, key=lambda x: x.analyst_id))
    if set(calendars) != {a.analyst_id for a in analysts}:
        raise ValueError("provide exactly one calendar per analyst")
    rows = tuple(sorted((a for a in arrivals if a.arrival < horizon), key=lambda a: (a.arrival, a.alert_id)))
    if len({a.alert_id for a in rows}) != len(rows):
        raise ValueError("duplicate alert id")
    by_id = {a.alert_id: a for a in rows}
    pending = {a.alert_id for a in rows}
    remaining = {a.alert_id: None for a in rows}
    owner: dict[str, str] = {}
    start_time: dict[str, float] = {}
    completion: dict[str, float] = {}
    suspension = {a.alert_id: 0.0 for a in rows}
    jobs: list[Assignment] = []
    rng = random.Random(seed)
    observed_arrivals: list[float] = []
    mode = "D1"
    t = 0.0

    while t < horizon:
        observed_arrivals.extend(a.arrival for a in rows if a.arrival == t)
        # Resume owned work before dispatching new work; it remains with its analyst.
        for aid, analyst_id in list(owner.items()):
            if aid not in completion and calendars[analyst_id].available(t):
                start_time.setdefault(aid, t)
        busy = {owner[aid] for aid in owner if aid not in completion and start_time.get(aid) == t}
        for analyst in analysts:
            if analyst.analyst_id in busy or not calendars[analyst.analyst_id].available(t):
                continue
            owned = next((aid for aid, who in owner.items() if who == analyst.analyst_id and aid not in completion), None)
            if owned is not None:
                continue
            eligible_pending = {aid: by_id[aid] for aid in pending if by_id[aid].arrival <= t
                                if by_id[aid].task_class in analyst.eligible_classes}
            if not eligible_pending:
                continue
            selected_policy = policy
            if policy in {"WAPS", "HLS-B"}:
                cfg = waps_config
                assert cfg is not None
                rate = sum(t - cfg.window_h < arrival <= t for arrival in observed_arrivals) / cfg.window_h
                pressure = rate / cfg.capacity_per_h
                if mode == "D1" and pressure >= cfg.high:
                    mode = "P1"
                elif mode == "P1" and pressure <= cfg.low:
                    mode = "D1"
                selected_policy = mode
            if selected_policy == "D1":
                chosen = _dispatch_d1([analyst], eligible_pending, t,
                    lambda a, x: float(service[a.analyst_id][x.task_class]), rng)
            else:
                chosen = _dispatch_local_priority([analyst], eligible_pending, t,
                    lambda a, x: float(service[a.analyst_id][x.task_class]))
            if chosen:
                _, alert = chosen[0]
                pending.remove(alert.alert_id)
                owner[alert.alert_id] = analyst.analyst_id
                remaining[alert.alert_id] = float(service[analyst.analyst_id][alert.task_class])
                start_time.setdefault(alert.alert_id, t)

        events = [horizon]
        events.extend(a.arrival for a in rows if a.alert_id in pending and a.arrival > t + 1e-10)
        events.extend(cal.next_change(t) for cal in calendars.values())
        for aid, who in owner.items():
            if aid in completion:
                continue
            cal = calendars[who]
            boundary = cal.next_change(t)
            if cal.available(t):
                events.append(min(boundary, t + remaining[aid]))
            else:
                events.append(boundary)
        nt = min(x for x in events if x > t + 1e-10)
        dt = nt - t
        for aid, who in list(owner.items()):
            if aid in completion:
                continue
            if calendars[who].available(t):
                remaining[aid] -= dt
                if remaining[aid] <= 1e-9:
                    completion[aid] = nt
                    task = by_id[aid]
                    jobs.append(Assignment(aid, who, start_time[aid], nt,
                                           analysts[[a.analyst_id for a in analysts].index(who)].competence[task.task_class]))
                    del owner[aid]
            else:
                suspension[aid] += dt
        t = nt

    episodes = []
    for a in rows:
        aid = a.alert_id
        if aid in completion:
            status = "completed_late" if completion[aid] > a.deadline else "completed"
        elif aid in owner:
            status = "suspended" if not calendars[owner[aid]].available(horizon - 1e-9) else "running"
        else:
            status = "queued"
        episodes.append(Episode(aid, status, owner.get(aid), float(remaining[aid] or 0), completion.get(aid), a.deadline, suspension[aid]))
    return Outcome(tuple(sorted(jobs, key=lambda j: (j.start, j.analyst_id, j.alert_id))),
                   tuple(episodes), tuple((e.alert_id, e.status) for e in episodes))
