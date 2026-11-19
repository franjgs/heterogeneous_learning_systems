"""Small deterministic mechanism checks for a proposed organizational B4.

This is a standalone matched-state design probe. It does not modify B0--B3,
run episodes, use SOCTRA records, or train a controller.
Run: python studies/soc_human_ai_organization/b4_organizational_control_mechanisms.py
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from hls.rq1_allocation import Alert, Analyst  # noqa: E402


@dataclass(frozen=True)
class Action:
    coordination: int  # 0 local, 1 urgent-only coordination, 2 global matching
    priority: str       # "deadline" or "balanced"

    @property
    def name(self) -> str:
        return f"C{self.coordination}-{self.priority}"


def _service(a: Analyst, x: Alert, base: dict[str, float], individual: dict[str, dict[str, float]]) -> float:
    return individual.get(a.analyst_id, {}).get(str(x.task_class), base[str(x.task_class)])


def _feasible(a: Analyst, x: Alert) -> bool:
    return x.task_class in a.eligible_classes


def _slack(a: Analyst, x: Alert, now: float, base: dict[str, float], individual: dict[str, dict[str, float]]) -> float:
    return x.deadline - now - _service(a, x, base, individual)


def _edge_utility(a: Analyst, x: Alert, now: float, base: dict[str, float], individual: dict[str, dict[str, float]], max_service: float) -> tuple[float, float, float]:
    service = _service(a, x, base, individual)
    ontime = float(now + service <= x.deadline)
    speed = 1.0 - service / max_service
    competence = float(a.competence[str(x.task_class)])
    return ontime, competence, speed


def _score_assignment(pairs, action, now, base, individual, max_service):
    if action.priority == "deadline":
        ontime = sum(now + _service(a, x, base, individual) <= x.deadline for a, x in pairs)
        ranks = {x.alert_id: i for i, x in enumerate(sorted({x for _, x in pairs}, key=lambda x: (x.deadline, x.arrival, x.alert_id)))}
        return (ontime, len(pairs), -sum(ranks[x.alert_id] for _, x in pairs))
    return (sum(0.60 * s + 0.25 * q + 0.15 * v
                for a, x in pairs
                for q, s, v in [_edge_utility(a, x, now, base, individual, max_service)]), len(pairs))


def _matching(analysts, alerts, action, now, base, individual):
    """Exact one-to-one matching for tiny diagnostic states (<=4x6)."""
    max_service = max(_service(a, x, base, individual) for a in analysts for x in alerts if _feasible(a, x))
    best, best_score = (), None

    def visit(ix, used, pairs):
        nonlocal best, best_score
        if ix == len(analysts):
            score = _score_assignment(pairs, action, now, base, individual, max_service)
            tie = tuple(sorted((a.analyst_id, x.alert_id) for a, x in pairs))
            key = (score, tuple((-ord(c) for c in repr(tie))))
            if best_score is None or key > best_score:
                best_score, best = key, tuple(pairs)
            return
        visit(ix + 1, used, pairs)
        a = analysts[ix]
        for x in alerts:
            if x.alert_id not in used and _feasible(a, x):
                visit(ix + 1, used | {x.alert_id}, pairs + [(a, x)])

    visit(0, set(), [])
    return list(best)


def _local(analysts, alerts, action, now, base, individual):
    remaining = list(alerts)
    result = []
    max_service = max((base[str(x.task_class)] for x in alerts), default=1.0)
    for a in sorted(analysts, key=lambda z: z.analyst_id):
        candidates = [x for x in remaining if _feasible(a, x)]
        if not candidates:
            continue
        if action.priority == "deadline":
            x = min(candidates, key=lambda z: (z.deadline, z.arrival, z.alert_id))
        else:
            x = max(candidates, key=lambda z: (
                sum(w * v for w, v in zip((0.15, 0.60, 0.25), _edge_utility(a, z, now, base, individual, max_service))),
                -z.deadline, z.alert_id,
            ))
        result.append((a, x))
        remaining.remove(x)
    return result


def dispatch(analysts, alerts, action, now, base, individual, coordination_edge_cost, screening_cost):
    analysts = tuple(sorted(analysts, key=lambda a: a.analyst_id))
    alerts = tuple(sorted(alerts, key=lambda x: (x.deadline, x.arrival, x.alert_id)))
    if action.coordination == 0:
        chosen = _local(analysts, alerts, action, now, base, individual)
        inspected = 0
        screened = 0
    else:
        if action.coordination == 1:
            # A coordinator intervenes only for alerts with <= one mean service
            # time of slack; ordinary work remains locally selected.
            feasible_services = [_service(a, x, base, individual)
                                 for a in analysts for x in alerts if _feasible(a, x)]
            mean_service = sum(feasible_services) / max(1, len(feasible_services))
            urgent = tuple(x for x in alerts if min(
                (_slack(a, x, now, base, individual) for a in analysts if _feasible(a, x)),
                default=float("inf"),
            ) <= mean_service)
            coordinated = _matching(analysts, urgent, action, now, base, individual) if urgent else []
            used_a = {a.analyst_id for a, _ in coordinated}
            used_x = {x.alert_id for _, x in coordinated}
            rest = _local([a for a in analysts if a.analyst_id not in used_a],
                          [x for x in alerts if x.alert_id not in used_x], action, now, base, individual)
            chosen = coordinated + rest
            inspected = sum(_feasible(a, x) for a in analysts for x in urgent)
            screened = len(alerts)
        else:
            chosen = _matching(analysts, alerts, action, now, base, individual)
            inspected = sum(_feasible(a, x) for a in analysts for x in alerts)
            screened = 0
    # Coordination effort is a dedicated-coordinator effort proxy, expressed
    # in service-time units; assigned staff wait equally long for the decision.
    if action.coordination == 0:
        screened = 0
    cost = coordination_edge_cost * inspected + screening_cost * screened
    latency = cost / len(chosen) if chosen else 0.0
    return chosen, inspected, cost, latency


def scenarios():
    """Predeclared paired snapshots spanning utilization and heterogeneity."""
    cls = ("A", "B")
    def roster(hetero=False, speed=False, restricted=False):
        a = Analyst("a", frozenset(cls if not restricted else ("A",)),
                    {"A": .95 if hetero else .70, "B": .45 if hetero else .70})
        b = Analyst("b", frozenset(cls), {"A": .45 if hetero else .70, "B": .95 if hetero else .70})
        base = {"A": 4.0, "B": 4.0}
        indiv = {"a": {"A": 2.0 if speed else 4.0, "B": 6.0 if speed else 4.0},
                 "b": {"A": 6.0 if speed else 4.0, "B": 2.0 if speed else 4.0}}
        return (a, b), base, indiv
    out = []
    for name, hetero, speed, restricted, n, slacks in [
        ("low_homogeneous", False, False, False, 1, (12,)),
        ("near_capacity_skill_speed", True, True, False, 2, (2.3, 2.5)),
        ("overload_heterogeneous", True, True, False, 4, (3.0, 4.0, 7.0, 10.0)),
        ("restricted_eligibility", True, True, True, 4, (3.0, 4.0, 7.0, 10.0)),
    ]:
        agents, base, indiv = roster(hetero, speed, restricted)
        class_order = ("B", "A", "B", "A") if name == "near_capacity_skill_speed" else cls
        alerts = tuple(Alert(f"{name}-{i}", 0.0, class_order[i % len(class_order)], slacks[i]) for i in range(n))
        out.append((name, agents, alerts, base, indiv))
    # A within-episode regime shift is represented by two successive observed
    # states with identical roster/parameters and a larger post-shift queue.
    agents, base, indiv = roster(True, True, False)
    out.extend([
        ("shift_before", agents, tuple(Alert(f"shift0-{i}", 0.0, cls[i % 2], 5.0 + i) for i in range(2)), base, indiv),
        ("shift_after", agents, tuple(Alert(f"shift1-{i}", 0.9, "B" if i < 4 else "A", 4.0 + i) for i in range(5)), base, indiv),
    ])
    # Isolates the quality/SLA tradeoff: a fast lower-skill analyst can meet
    # the deadline, while the higher-skill analyst is slower and misses it.
    tradeoff_roster = (
        Analyst("a_fast", frozenset(("A",)), {"A": 0.10}),
        Analyst("b_skilled", frozenset(("A",)), {"A": 0.99}),
    )
    out.append(("skill_vs_deadline_tradeoff", tradeoff_roster,
                (Alert("tradeoff-A", 0.0, "A", 3.0),), {"A": 4.0},
                {"a_fast": {"A": 2.0}, "b_skilled": {"A": 6.0}}))
    return out


def main():
    actions = [Action(c, p) for c in range(3) for p in ("deadline", "balanced")]
    cost_per_edge = 0.02  # ASSUMED effort per feasible pair; not SOCTRA-derived
    cost_per_screen = 0.002  # ASSUMED per-alert urgency screen; not SOCTRA-derived
    rows = []
    for name, agents, alerts, base, individual in scenarios():
        now = 1.0 if name == "shift_after" else 0.0
        for action in actions:
            chosen, edges, cost, delay = dispatch(agents, alerts, action, now, base, individual, cost_per_edge, cost_per_screen)
            assert len({a.analyst_id for a, _ in chosen}) == len(chosen), "analyst assigned twice"
            assert len({x.alert_id for _, x in chosen}) == len(chosen), "alert assigned twice"
            assert all(_feasible(a, x) for a, x in chosen), "ineligible assignment"
            ontime = sum(now + delay + _service(a, x, base, individual) <= x.deadline for a, x in chosen)
            qual = sum(a.competence[str(x.task_class)] for a, x in chosen
                       if now + delay + _service(a, x, base, individual) <= x.deadline)
            rows.append({
                "scenario": name, "action": action.name,
                "assignment": ";".join(f"{a.analyst_id}->{x.alert_id}" for a, x in sorted(chosen, key=lambda z: z[0].analyst_id)),
                "assigned": len(chosen), "on_time": ontime,
                "assigned_competence_sum": round(sum(a.competence[str(x.task_class)] for a, x in chosen), 3),
                "modeled_on_time_competence": round(qual, 3),
                "service_work": round(sum(_service(a, x, base, individual) for a, x in chosen), 3),
                "edges_examined": edges, "alerts_screened": len(alerts) if action.coordination == 1 else 0,
                "coord_effort": round(cost, 3), "dispatch_delay": round(delay, 3),
            })
    by_key = {(r["scenario"], r["action"]): r for r in rows}
    assert by_key[("near_capacity_skill_speed", "C0-deadline")]["on_time"] < by_key[("near_capacity_skill_speed", "C2-deadline")]["on_time"]
    assert by_key[("skill_vs_deadline_tradeoff", "C2-deadline")]["on_time"] > by_key[("skill_vs_deadline_tradeoff", "C2-balanced")]["on_time"]
    assert by_key[("skill_vs_deadline_tradeoff", "C2-balanced")]["assigned_competence_sum"] > by_key[("skill_vs_deadline_tradeoff", "C2-deadline")]["assigned_competence_sum"]
    print(json.dumps({"cost_per_edge": cost_per_edge, "cost_per_alert_screen": cost_per_screen, "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
