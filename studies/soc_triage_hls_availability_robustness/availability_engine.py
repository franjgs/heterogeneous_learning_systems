"""Isolated preempt-resume availability simulator for the SOCTRA-HLS study.

Time is elapsed hours from Monday 00:00. Analyst availability is deterministic
and location-free. Dispatchers see only pending alerts and ex ante service.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
import random
from typing import Mapping, Sequence

from hls.rq1_allocation import Alert, Analyst, Assignment, HLSBConfig, HLSADecision, _dispatch_d1, _dispatch_local_priority


@dataclass(frozen=True)
class Calendar:
    windows: tuple[tuple[int, float, float], ...]  # weekday 0=Mon; end <= start means overnight
    hours_per_day: float = 24.0

    def __post_init__(self):
        for day, start, end in self.windows:
            if day not in range(7) or not (0 <= start < self.hours_per_day) or not (0 <= end <= self.hours_per_day):
                raise ValueError("calendar window outside weekday or day-hour bounds")
            if start == end:
                raise ValueError("zero-length shifts are not valid")

    def available(self, t: float) -> bool:
        week = 7 * self.hours_per_day
        week_hour = t % week
        for day, start, end in self.windows:
            begin = day * self.hours_per_day + start
            finish = day * self.hours_per_day + end
            if end <= start:
                finish += self.hours_per_day
            if finish <= week:
                if begin <= week_hour < finish:
                    return True
            elif week_hour >= begin or week_hour < finish - week:
                return True
        return False

    def next_change(self, t: float) -> float:
        # All boundaries repeat weekly; advance to the next boundary (or a daily
        # boundary for all-day schedules).
        week = 7 * self.hours_per_day
        base = int(t // week) * week
        points_set = {0, week}
        for d, a, b in self.windows:
            points_set.add((d * self.hours_per_day + a) % week)
            points_set.add((d * self.hours_per_day + b + (self.hours_per_day if b <= a else 0)) % week)
        points = sorted(points_set)
        candidates = sorted(base + cycle * week + p for cycle in (0, 1) for p in points
                           if base + cycle * week + p > t + 1e-10)
        for boundary in candidates:
            eps = min(1e-7, max(1e-10, (boundary - t) / 4))
            if self.available(boundary - eps) != self.available(boundary + eps):
                return boundary
        return base + week

    def scaled(self, factor: float) -> "Calendar":
        return Calendar(tuple((d, a * factor, b * factor) for d, a, b in self.windows),
                        self.hours_per_day * factor)


CONTINUOUS = Calendar(tuple((d, 0.0, 24.0) for d in range(7)))
WEEKDAY_9_TO_17 = Calendar(tuple((d, 9.0, 17.0) for d in range(5)))


@dataclass(frozen=True)
class TimeScale:
    """Uniform multiplier for all time quantities passed to the simulator."""
    factor: float = 1.0

    def __post_init__(self):
        if self.factor <= 0:
            raise ValueError("time scale factor must be positive")


def deadline_from_arrival(arrival: float, severity: object, *,
                          explicit_hours: float | None = None,
                          by_severity: Mapping[object, float] | None = None) -> float:
    """Return absolute natural-time deadline; explicit offset is severity-independent."""
    offset = explicit_hours if explicit_hours is not None else (by_severity or {})[severity]
    if offset < 0:
        raise ValueError("deadline offset must be nonnegative")
    return arrival + offset


@dataclass(frozen=True)
class Episode:
    alert_id: str
    status: str
    analyst_id: str | None
    remaining_service_h: float
    completion: float | None
    deadline: float
    suspension_h: float
    start: float | None = None


@dataclass(frozen=True)
class Outcome:
    assignments: tuple[Assignment, ...]
    episodes: tuple[Episode, ...]
    statuses: tuple[tuple[str, str], ...]
    work_done_by_alert: tuple[tuple[str, float], ...] = ()
    work_segments: tuple[tuple[str, str, float, float], ...] = ()
    dispatch_epochs: int = 0
    p1_dispatch_epochs: int = 0
    switches: tuple[HLSADecision, ...] = ()


def simulate(arrivals: Sequence[Alert], analysts: Sequence[Analyst],
             service: Mapping[str, Mapping[object, float]], calendars: Mapping[str, Calendar],
             *, horizon: float, policy: str = "D1", seed: int = 0,
             waps_config: HLSBConfig | None = None,
             actual_service: Mapping[str, Mapping[object, float]] | None = None,
             realized_scale_by_alert: Mapping[str, float] | None = None) -> Outcome:
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
    actual_map = actual_service or service
    scales = dict(realized_scale_by_alert or {a.alert_id: 1.0 for a in rows})
    if set(scales) != set(by_id) or any(not isfinite(float(v)) or v <= 0 for v in scales.values()):
        raise ValueError("realized service scales must cover admitted tasks and be finite and positive")
    pending = {a.alert_id for a in rows}
    remaining = {a.alert_id: None for a in rows}
    owner: dict[str, str] = {}
    start_time: dict[str, float] = {}
    completion: dict[str, float] = {}
    planned_completion: dict[str, float] = {}
    suspension = {a.alert_id: 0.0 for a in rows}
    work_done = {a.alert_id: 0.0 for a in rows}
    segments: list[tuple[str, str, float, float]] = []
    open_segment: dict[str, float] = {}
    jobs: list[Assignment] = []
    rng = random.Random(seed)
    observed_arrivals: list[float] = []
    mode = "D1"
    switches: list[HLSADecision] = []
    dispatch_epochs = p1_epochs = 0
    t = 0.0

    analyst_by_id = {a.analyst_id: a for a in analysts}
    while t < horizon:
        observed_arrivals.extend(a.arrival for a in rows if a.arrival == t)
        for aid, who in owner.items():
            if calendars[who].available(t) and aid not in open_segment:
                open_segment[aid] = t
                planned_completion[aid] = t + remaining[aid]
        # Dispatch only to free, available analysts. Owned suspended work is
        # reserved and resumes without entering a new policy decision.
        owned_analysts = set(owner.values())
        free = [a for a in analysts if a.analyst_id not in owned_analysts
                and calendars[a.analyst_id].available(t)]
        queue = {aid: by_id[aid] for aid in pending if by_id[aid].arrival <= t}
        if free and queue:
            selected_policy = policy
            if policy in {"WAPS", "HLS-B"}:
                cfg = waps_config
                assert cfg is not None
                rate = sum(t - cfg.window_h < arrival <= t for arrival in observed_arrivals) / cfg.window_h
                pressure = rate / cfg.capacity_per_h
                previous_mode = mode
                if mode == "D1" and pressure >= cfg.high:
                    mode = "P1"
                elif mode == "P1" and pressure <= cfg.low:
                    mode = "D1"
                if mode != previous_mode:
                    switches.append(HLSADecision(t, mode, pressure, len(queue), len(owned_analysts), True))
                selected_policy = mode
            service_forecast = lambda analyst, alert: float(service[analyst.analyst_id][alert.task_class])
            chosen = (_dispatch_d1(free, queue, t, service_forecast, rng)
                      if selected_policy == "D1" else _dispatch_local_priority(free, queue, t, service_forecast))
            dispatch_epochs += 1
            p1_epochs += int(selected_policy == "P1")
            for analyst, alert in chosen:
                pending.remove(alert.alert_id)
                owner[alert.alert_id] = analyst.analyst_id
                remaining[alert.alert_id] = (float(actual_map[analyst.analyst_id][alert.task_class])
                                              * scales[alert.alert_id])
                start_time[alert.alert_id] = t
                if calendars[analyst.analyst_id].available(t):
                    open_segment[alert.alert_id] = t
                    planned_completion[alert.alert_id] = t + remaining[alert.alert_id]

        events = [horizon]
        events.extend(a.arrival for a in rows if a.alert_id in pending and a.arrival > t + 1e-10)
        events.extend(cal.next_change(t) for cal in calendars.values())
        for aid, who in owner.items():
            if calendars[who].available(t):
                events.append(min(calendars[who].next_change(t), planned_completion[aid]))
        nt = min(x for x in events if x > t + 1e-10)
        dt = nt - t
        for aid, who in list(owner.items()):
            if calendars[who].available(t):
                if nt >= planned_completion[aid] - 1e-12:
                    work_done[aid] += remaining[aid]
                    remaining[aid] = 0.0
                    completion[aid] = nt
                    task = by_id[aid]
                    segments.append((aid, who, open_segment.pop(aid), nt))
                    jobs.append(Assignment(aid, who, start_time[aid], nt,
                                           analyst_by_id[who].competence[task.task_class]))
                    del owner[aid]
                    planned_completion.pop(aid, None)
                else:
                    work_done[aid] += dt
                    remaining[aid] -= dt
            else:
                suspension[aid] += dt
                if aid in open_segment:
                    segments.append((aid, who, open_segment.pop(aid), t))
                planned_completion.pop(aid, None)
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
        episodes.append(Episode(aid, status, owner.get(aid), float(remaining[aid] or 0),
                                completion.get(aid), a.deadline, suspension[aid], start_time.get(aid)))
    for aid, who in owner.items():
        if aid in open_segment:
            segments.append((aid, who, open_segment[aid], horizon))
    return Outcome(tuple(sorted(jobs, key=lambda j: (j.start, j.analyst_id, j.alert_id))),
                   tuple(episodes), tuple((e.alert_id, e.status) for e in episodes),
                   tuple(sorted(work_done.items())), tuple(sorted(segments)),
                   dispatch_epochs, p1_epochs, tuple(switches))


def simulate_scaled(arrivals: Sequence[Alert], analysts: Sequence[Analyst],
                    service: Mapping[str, Mapping[object, float]], calendars: Mapping[str, Calendar],
                    *, horizon: float, scale: TimeScale = TimeScale(), policy: str = "D1",
                    seed: int = 0, waps_config: HLSBConfig | None = None) -> Outcome:
    """Run an otherwise identical scenario with every time quantity multiplied.

    Returned times, deadlines, work, and durations use the scaled units.
    """
    f = scale.factor
    alerts_scaled = tuple(Alert(a.alert_id, a.arrival * f, a.task_class, a.deadline * f) for a in arrivals)
    service_scaled = {aid: {k: v * f for k, v in values.items()} for aid, values in service.items()}
    calendar_scaled = {aid: cal.scaled(f) for aid, cal in calendars.items()}
    cfg = None if waps_config is None else HLSBConfig(
        window_h=waps_config.window_h * f, low=waps_config.low, high=waps_config.high,
        capacity_per_h=waps_config.capacity_per_h / f)
    return simulate(alerts_scaled, analysts, service_scaled, calendar_scaled, horizon=horizon * f,
                    policy=policy, seed=seed, waps_config=cfg)
