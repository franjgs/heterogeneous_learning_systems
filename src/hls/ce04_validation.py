"""Run-time CE-04 validation, including effective estimator-update traces.

The simulator's task fields describe when feedback becomes observable. They
are not evidence that an estimator consumed that feedback. This module traces
the actual Beta-array writes and LinUCB update method calls without changing
the simulator or either policy implementation.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
import math
from typing import Iterator

import numpy as np

from hls import ce04


@dataclass
class UpdateTrace:
    beta_updates: list[dict] = field(default_factory=list)
    linucb_updates: list[dict] = field(default_factory=list)


@contextmanager
def capture_effective_updates() -> Iterator[UpdateTrace]:
    """Trace actual updates while preserving all original implementations."""
    trace = UpdateTrace()
    clock: dict = {}
    original_env = ce04.simpy.Environment
    original_observe = ce04.LinUCBDisjoint.observe_delayed
    original_zeros_like = ce04.np.zeros_like
    beta_array_index = 0

    class TrackedEnvironment(original_env):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            clock["env"] = self

    class TrackedArray(np.ndarray):
        def __array_finalize__(self, obj):
            self.beta_kind = getattr(obj, "beta_kind", "unknown")

        def __setitem__(self, key, value):
            super().__setitem__(key, value)
            if self.beta_kind in {"beta_success", "beta_failure"} and "env" in clock:
                trace.beta_updates.append({"kind": self.beta_kind,
                                           "index": tuple(int(x) for x in key),
                                           "time": float(clock["env"].now)})

    def tracked_zeros_like(array, *args, **kwargs):
        nonlocal beta_array_index
        result = original_zeros_like(array, *args, **kwargs).view(TrackedArray)
        result.beta_kind = "beta_success" if beta_array_index == 0 else "beta_failure"
        beta_array_index += 1
        return result

    def tracked_observe(self, arm, context, reward):
        now = float(clock["env"].now)
        trace.linucb_updates.append({"arm": int(arm),
                                     "context": tuple(float(x) for x in context),
                                     "reward": int(reward), "time": now})
        return original_observe(self, arm, context, reward)

    ce04.simpy.Environment = TrackedEnvironment
    ce04.np.zeros_like = tracked_zeros_like
    ce04.LinUCBDisjoint.observe_delayed = tracked_observe
    try:
        yield trace
    finally:
        ce04.simpy.Environment = original_env
        ce04.np.zeros_like = original_zeros_like
        ce04.LinUCBDisjoint.observe_delayed = original_observe


def run_replica_traced(config, tasks):
    """Execute one replica with an independent trace of effective updates."""
    with capture_effective_updates() as trace:
        result = ce04.run_replica(config, tasks)
    return result, trace


def _time_key(value: float) -> float:
    return round(float(value), 12)


def validate_update_trace(result: dict, trace: UpdateTrace) -> None:
    """Assert policy-exclusive updates and that each update follows feedback."""
    policy = result["config"]["policy"]
    records = result["records"]
    admitted = [r for r in records if r["selected_agent"] is not None]

    expected_beta = []
    for record in admitted:
        if policy == "P2":
            expected_beta.append({
                "kind": "beta_success" if record["correct"] else "beta_failure",
                "index": (record["selected_agent"], record["family"]),
                "time": _time_key(record["completion"]),
            })
            if record["p2_label_observed_at"] != record["completion"]:
                raise AssertionError("P2 correctness label was unavailable at estimator update")
        elif record["p2_label_observed_at"] is not None:
            raise AssertionError(f"{policy} recorded a P2 estimator update")
    actual_beta = [{**item, "time": _time_key(item["time"])} for item in trace.beta_updates]
    if Counter((x["kind"], x["index"], x["time"]) for x in actual_beta) != Counter(
            (x["kind"], x["index"], x["time"]) for x in expected_beta):
        raise AssertionError("effective Beta-Bernoulli updates differ from observed P2 labels")

    expected_linucb = []
    if policy == "P3":
        feedback_by_id = {x["task_id"]: x for x in result["p3_feedback_events"]}
        if set(feedback_by_id) != {r["task_id"] for r in admitted}:
            raise AssertionError("P3 reward observations do not cover selected tasks exactly once")
        for record in admitted:
            feedback = feedback_by_id[record["task_id"]]
            if record["completion"] <= record["deadline"]:
                observed_at = record["completion"]
                expected_reward = int(bool(record["correct"]))
                source = "completion"
            else:
                observed_at = record["deadline"]
                expected_reward = 0
                source = "deadline"
            if feedback["time"] != observed_at or feedback["reward"] != expected_reward or feedback["source"] != source:
                raise AssertionError("P3 update does not match the reward observable at that time")
            if record["p3_reward_observed_at"] != observed_at or record["reward_p3"] != expected_reward:
                raise AssertionError("P3 record has inconsistent reward-observation timing")
            context = [0.0] * 4
            context[record["family"]] = record["f_selected"]
            expected_linucb.append((record["selected_agent"], tuple(context), expected_reward,
                                    _time_key(observed_at)))
    # For non-P3 policies, p3_reward fields may be diagnostic event records.
    # Only the captured estimator method call is an effective LinUCB update.
    actual_linucb = [(x["arm"], x["context"], x["reward"], _time_key(x["time"]))
                     for x in trace.linucb_updates]
    if Counter(actual_linucb) != Counter(expected_linucb):
        raise AssertionError("effective LinUCB updates differ from P3-observable rewards")


def validate_replica(result: dict, config, tasks, trace: UpdateTrace) -> None:
    """Validate one completed CE-04 replica before saving it."""
    records = result["records"]
    task_ids = [r["task_id"] for r in records]
    expected_ids = [t.task_id for t in tasks]
    if task_ids != expected_ids or len(task_ids) != len(set(task_ids)):
        raise AssertionError("arrival conservation or task identity failure")
    if result["n_arrivals"] != result["n_admitted"] + result["n_rejected"]:
        raise AssertionError("arrivals != admitted + rejected")
    admitted = [r for r in records if r["selected_agent"] is not None]
    if len(admitted) != result["n_admitted"]:
        raise AssertionError("admitted count differs from assignments")
    for rec in admitted:
        if rec["service_start"] is None or rec["completion"] is None or rec["correct"] is None:
            raise AssertionError("admitted task lacks a final single execution result")
        if rec["f_selected"] < ce04.ADMISSION_THRESHOLD:
            raise AssertionError("assigned agent did not satisfy shared admission cutoff")
        if rec["on_time"] != bool(rec["correct"] and rec["completion"] <= rec["deadline"]):
            raise AssertionError("success does not match correctness and deadline")
    for rec in records:
        if rec["selected_agent"] is None and (rec["completion"] is not None or rec["correct"] is not None):
            raise AssertionError("rejected task was executed or labelled")

    validate_admission_replay(result)

    for agent in range(config.n_agents):
        queue = sorted((r for r in admitted if r["selected_agent"] == agent),
                       key=lambda r: r["arrival"])
        for first, second in zip(queue, queue[1:]):
            if first["task_id"] >= second["task_id"] or first["service_start"] > second["service_start"]:
                raise AssertionError("FCFS ordering violation")
            if first["completion"] > second["service_start"] + 1e-12:
                raise AssertionError("agent capacity exceeded")

    q, _ = ce04.competency_matrix(config.n_agents, config.composition, config.seed)
    if not np.allclose(q.mean(axis=0), .775, rtol=0, atol=1e-12):
        raise AssertionError("task-family competence means differ from 0.775")
    if config.n_agents not in (12, 24, 48) or not math.isclose(
            ce04.ARRIVAL_RATE_PER_AGENT * config.n_agents, .55 * config.n_agents):
        raise AssertionError("load/resource scale differs from protocol")
    if result["simulation_drain_end"] < config.horizon:
        raise AssertionError("simulation stopped before the arrival horizon")
    if not 0 <= result["success_on_time_rate"] <= 1 or not all(
            0 <= value <= 1 for value in result["agent_utilization"]):
        raise AssertionError("metric outside its valid domain")
    if not _finite(result):
        raise AssertionError("non-finite metric or result field")
    validate_update_trace(result, trace)


def validate_admission_replay(result: dict) -> None:
    """Reconstruct each decision-time queue and verify the common F cutoff.

    This is a retrospective audit only. It reads the task log after execution;
    it is never called by a policy or made available to the simulator.
    """
    config = result["config"]
    records = result["records"]
    for current in records:
        now = current["arrival"]
        f_values = []
        for agent in range(config["n_agents"]):
            prior = [r for r in records if r["selected_agent"] == agent and r["arrival"] < now]
            active = [r for r in prior if r["service_start"] <= now < r["completion"]]
            if len(active) > 1:
                raise AssertionError("reconstructed worker state violates single-service capacity")
            waiting = sum(1 for r in prior if r["service_start"] > now)
            age = None if not active else now - active[0]["service_start"]
            if config["probability_method"] == "two_moment":
                f = ce04.deadline_probability_two_moment(age, waiting, current["deadline"] - now)
            else:
                f = ce04.deadline_probability_convolution(
                    age, waiting, current["deadline"] - now, config["convolution_step"])
            f_values.append(f)
        selected = current["selected_agent"]
        if selected is None:
            if any(f >= ce04.ADMISSION_THRESHOLD for f in f_values):
                raise AssertionError("task rejected despite a common-admissible agent")
        else:
            if abs(f_values[selected] - current["f_selected"]) > 1e-10:
                raise AssertionError("selected deadline probability differs from common rule")
            if f_values[selected] < ce04.ADMISSION_THRESHOLD:
                raise AssertionError("selected agent does not satisfy common admission threshold")


def _finite(value) -> bool:
    if isinstance(value, dict):
        return all(_finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(_finite(item) for item in value)
    if isinstance(value, (float, np.floating)):
        return math.isfinite(float(value))
    return True
