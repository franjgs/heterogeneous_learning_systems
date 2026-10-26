"""Post-hoc heterogeneity diagnostics for the frozen CE-04 P1 design.

This module derives diagnostics from CE-04 task records. It does not alter
the CE-04 simulator or the P1 decision rule.
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from hls.ce04 import competency_matrix


def gini(values) -> float:
    """Gini coefficient for a finite, non-negative population vector."""
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or not np.all(np.isfinite(x)) or np.any(x < 0):
        raise ValueError("Gini requires a finite, non-negative vector")
    if x.size == 0 or float(x.sum()) == 0:
        return 0.0
    x = np.sort(x)
    n = x.size
    return float((2 * np.dot(np.arange(1, n + 1), x) / (n * x.sum())) - (n + 1) / n)


def diagnose_replica(config: dict, records: list[dict], *, end_time: float,
                     assignment_counts=None, agent_service_time=None) -> tuple[dict, list[dict]]:
    """Return one replica summary and family/phase cell summaries."""
    n, seed, composition = int(config["n_agents"]), int(config["seed"]), config["composition"]
    q, _ = competency_matrix(n, composition, seed)
    if not np.allclose(q.mean(axis=0), .775, rtol=0, atol=1e-12):
        raise AssertionError("CE-04 competence means are not preserved")
    if assignment_counts is None:
        assignment_counts = np.zeros(n, dtype=int)
        for r in records:
            if r.get("selected_agent") is not None:
                assignment_counts[int(r["selected_agent"])] += 1
    counts = np.asarray(assignment_counts, dtype=float)
    if agent_service_time is None:
        agent_service_time = np.zeros(n, dtype=float)
        for r in records:
            if r.get("selected_agent") is not None:
                agent_service_time[int(r["selected_agent"])] += float(r.get("service_time", 0))
    service = np.asarray(agent_service_time, dtype=float)
    if counts.shape != (n,) or service.shape != (n,):
        raise ValueError("agent vectors must have length N")

    max_q = q.max(axis=0)
    admitted = [r for r in records if r.get("selected_agent") is not None]
    selected_q, gaps, waits = [], [], []
    cells = defaultdict(lambda: {"arrivals": 0, "admitted": 0, "rejected": 0,
                                 "success": 0, "incorrect": 0, "late": 0,
                                 "waits": [], "selected_q": [], "gap": []})
    for r in records:
        k, phase = int(r["family"]), int(r["phase"])
        cell = cells[(k, phase)]
        cell["arrivals"] += 1
        if r.get("selected_agent") is None:
            cell["rejected"] += 1
            continue
        cell["admitted"] += 1
        i = int(r["selected_agent"])
        qi = float(q[i, k]); gap = float(max_q[k] - qi)
        wait = float(r["service_start"] - r["arrival"])
        selected_q.append(qi); gaps.append(gap); waits.append(wait)
        cell["selected_q"].append(qi); cell["gap"].append(gap); cell["waits"].append(wait)
        cell["success"] += int(bool(r.get("correct") and r.get("on_time")))
        cell["incorrect"] += int(r.get("correct") is False)
        cell["late"] += int(r.get("completion") is not None and
                             float(r["completion"]) > float(r["deadline"]))

    max_comp = [float(x) for x in max_q]
    selected = np.asarray(selected_q, dtype=float)
    gap_arr = np.asarray(gaps, dtype=float)
    wait_arr = np.asarray(waits, dtype=float)
    total = len(records)
    summary = {
        "seed": seed, "n_agents": n, "composition": composition, "policy": config["policy"],
        "arrivals": total, "admitted": len(admitted), "rejected": total-len(admitted),
        "success_on_time": sum(int(bool(r.get("correct") and r.get("on_time"))) for r in admitted),
        "success_on_time_rate": (sum(int(bool(r.get("correct") and r.get("on_time"))) for r in admitted)/total if total else 0),
        "q_mean_min": float(q.mean(axis=0).min()), "q_mean_max": float(q.mean(axis=0).max()),
        "q_max_f1": max_comp[0], "q_max_f2": max_comp[1], "q_max_f3": max_comp[2], "q_max_f4": max_comp[3],
        "selected_q_mean": float(selected.mean()) if selected.size else None,
        "selected_q_median": float(np.median(selected)) if selected.size else None,
        "gap_to_family_max_mean": float(gap_arr.mean()) if gap_arr.size else None,
        "gap_to_family_max_median": float(np.median(gap_arr)) if gap_arr.size else None,
        "assignment_gini": gini(counts), "assignment_hhi": float(np.square(counts/counts.sum()).sum()) if counts.sum() else 0,
        "assignment_effective_agents": float(1/np.square(counts/counts.sum()).sum()) if counts.sum() else 0,
        "assignment_count_min": int(counts.min()), "assignment_count_max": int(counts.max()),
        "service_time_gini": gini(service),
        "utilization_mean": float(np.mean(service/end_time)) if end_time else 0,
        "utilization_median": float(np.median(service/end_time)) if end_time else 0,
        "utilization_p95": float(np.quantile(service/end_time, .95)) if end_time else 0,
        "utilization_max": float(np.max(service/end_time)) if end_time else 0,
        "wait_mean": float(wait_arr.mean()) if wait_arr.size else None,
        "wait_p95": float(np.quantile(wait_arr,.95)) if wait_arr.size else None,
        "late_admitted": sum(int(r.get("completion") is not None and float(r["completion"])>float(r["deadline"])) for r in admitted),
    }
    rows=[]
    for (k,phase), c in sorted(cells.items()):
        n_adm=c["admitted"]
        rows.append({"seed":seed,"n_agents":n,"composition":composition,"policy":config["policy"],
            "family":k,"phase":phase,"arrivals":c["arrivals"],"admitted":n_adm,"rejected":c["rejected"],
            "success_on_time":c["success"],"success_on_time_rate":c["success"]/c["arrivals"] if c["arrivals"] else None,
            "incorrect":c["incorrect"],"late":c["late"],
            "selected_q_mean":float(np.mean(c["selected_q"])) if n_adm else None,
            "gap_to_family_max_mean":float(np.mean(c["gap"])) if n_adm else None,
            "wait_mean":float(np.mean(c["waits"])) if n_adm else None})
    return summary, rows
