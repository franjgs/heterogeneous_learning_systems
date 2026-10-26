"""CE-07 technical pilot adapter; delegates all execution and P1 choices to CE-04."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import struct

import numpy as np

from hls import ce04
from hls.ce04_validation import run_replica_traced, validate_update_trace
from hls.ce07_structure import competence_matrices, validate_structures


PERMUTATION_STREAM = 707


def agent_permutation(seed: int, n_agents: int = 12) -> tuple[int, ...]:
    """Independent reproducible new-slot -> original profile permutation."""
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), int(n_agents), PERMUTATION_STREAM]))
    p = np.arange(n_agents)
    rng.shuffle(p)
    return tuple(int(x) for x in p)


def canonical_sha256(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def matched_potential_digest(seed: int, tasks, q_a: np.ndarray, q_b: np.ndarray) -> str:
    """Hash CE-04 service potentials and paired correctness potentials for all task-agent pairs."""
    digest = hashlib.sha256()
    for task in tasks:
        for agent in range(12):
            service = ce04.potential_service(seed, 12, task.task_id, agent)
            qa = float(q_a[agent, task.family])
            qb = float(q_b[agent, task.family])
            correct_a = ce04.potential_correct(seed, 12, task.task_id, agent, qa)
            correct_b = ce04.potential_correct(seed, 12, task.task_id, agent, qb)
            if qa == qb and correct_a != correct_b:
                raise AssertionError("equal competence failed shared correctness draw")
            if qa > qb and int(correct_a) < int(correct_b):
                raise AssertionError("shared correctness stream violates monotone threshold coupling")
            if qb > qa and int(correct_b) < int(correct_a):
                raise AssertionError("shared correctness stream violates monotone threshold coupling")
            digest.update(struct.pack(">QIdBB", int(task.task_id), agent, service,
                                     int(correct_a), int(correct_b)))
    return digest.hexdigest()


@contextmanager
def _ce07_runtime(q_by_name: dict[str, np.ndarray], tie_events: list[dict]):
    """Supply CE-07 Q and observe exact CE-04 tie decisions, then restore globals."""
    original_competency = ce04.competency_matrix
    original_choose = ce04._choose_with_tie

    def competency_matrix(_n, composition, _seed):
        if composition not in q_by_name:
            raise ValueError(f"unexpected CE-07 organization {composition}")
        return q_by_name[composition].copy(), np.zeros(12, dtype=int)

    def choose_with_tie(scores, admissible, tie_rank):
        score_list = list(scores)
        eligible = list(admissible)
        best = max(float(score_list[i]) for i in eligible)
        exact_ties = [int(i) for i in eligible if float(score_list[i]) == best]
        selected = original_choose(score_list, eligible, tie_rank)
        tie_events.append({"decision_index": len(tie_events),
            "admissible_count": len(eligible), "best_score": best,
            "exact_tie_candidates": exact_ties, "selected_agent_slot": int(selected),
            "selected_priority_rank": int(tie_rank[selected])})
        return selected

    ce04.competency_matrix = competency_matrix
    ce04._choose_with_tie = choose_with_tie
    try:
        yield
    finally:
        ce04.competency_matrix = original_competency
        ce04._choose_with_tie = original_choose


def validate_ce07_run(result: dict, config, tasks, q: np.ndarray, trace, tie_events: list[dict]) -> dict:
    records = result["records"]
    if [r["task_id"] for r in records] != [t.task_id for t in tasks]:
        raise AssertionError("task IDs missing, reordered or duplicated")
    if result["n_arrivals"] != result["n_admitted"] + result["n_rejected"]:
        raise AssertionError("arrival conservation failed")
    if not np.allclose(q.mean(axis=0), .675, rtol=0, atol=1e-14):
        raise AssertionError("CE-07 marginal competence is not 0.675")
    admitted = [r for r in records if r["selected_agent"] is not None]
    if len(admitted) != result["n_admitted"] or len(tie_events) != len(admitted):
        raise AssertionError("assignment/tie trace does not cover admitted tasks")
    for record, tie in zip(admitted, tie_events):
        if tie["selected_agent_slot"] != record["selected_agent"]:
            raise AssertionError("instrumented tie helper changed or misreported P1 choice")
        i, k = int(record["selected_agent"]), int(record["family"])
        if record["service_time"] != ce04.potential_service(config.seed, 12, record["task_id"], i):
            raise AssertionError("service potential does not match CE-04 keyed stream")
        expected_correct = ce04.potential_correct(config.seed, 12, record["task_id"], i, float(q[i, k]))
        if record["correct"] != expected_correct:
            raise AssertionError("correctness result does not match CE-04 keyed potential")
        if record["on_time"] != bool(record["correct"] and record["completion"] <= record["deadline"]):
            raise AssertionError("success-on-time outcome is inconsistent")
    for r in records:
        if r["selected_agent"] is None and (r["completion"] is not None or r["correct"] is not None):
            raise AssertionError("rejected task was executed or labelled")
    for i in range(12):
        queue = sorted((r for r in admitted if r["selected_agent"] == i), key=lambda r: r["arrival"])
        for x, y in zip(queue, queue[1:]):
            if x["task_id"] >= y["task_id"] or x["service_start"] > y["service_start"]:
                raise AssertionError("FCFS order invalid")
            if x["completion"] > y["service_start"] + 1e-12:
                raise AssertionError("agent capacity exceeded")
    validate_update_trace(result, trace)
    return {"arrivals_conserved": True, "exact_marginals": True,
            "assignments_validated": len(admitted), "potential_outcomes_validated": len(admitted),
            "p1_tie_calls": len(tie_events), "exact_tie_calls": sum(len(t["exact_tie_candidates"]) > 1 for t in tie_events),
            "p1_updates": 0}


def run_ce07_replica(seed: int, organization: str, tasks=None) -> tuple[dict, dict, tuple[int, ...]]:
    if organization not in ("A", "B"):
        raise ValueError("organization must be A or B")
    q_a, q_b = competence_matrices()
    validate_structures(q_a, q_b)
    permutation = agent_permutation(seed)
    q = (q_a if organization == "A" else q_b)[list(permutation)].copy()
    config = ce04.RunConfig(seed=seed, n_agents=12, composition=f"CE07_{organization}", policy="P1")
    if tasks is None:
        tasks = ce04.generate_workload(seed, 12, horizon=400.0)
    ties=[]
    with _ce07_runtime({f"CE07_{organization}": q}, ties):
        result, trace = run_replica_traced(config, tasks)
    validation = validate_ce07_run(result, config, tasks, q, trace, ties)
    return result, {"validation": validation, "tie_events": ties}, permutation

