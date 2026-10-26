"""CE-04 event-driven assignment simulation.

This is a study-specific implementation of the frozen CE-04 protocol, not a
general HLS simulator. Counterfactual service and correctness variates are
keyed by replicate, scale, task and agent, so policy decisions cannot shift
another policy's random stream.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import os
import resource
import subprocess
import sys
import time
from typing import Iterable

import numpy as np
import simpy
from scipy.special import ndtr

from hls.linucb import LinUCBDisjoint, alpha_from_delta


HORIZON = 400.0
ARRIVAL_RATE_PER_AGENT = 0.55
DEADLINE_SLACK = 3.0
ADMISSION_THRESHOLD = 0.50
SERVICE_MEAN = 1.25
SERVICE_CV = 0.30
PHASES = ((0.0, 150.0, (0.4, 0.2, 0.2, 0.2)),
          (150.0, 300.0, (0.1, 0.4, 0.4, 0.1)),
          (300.0, 400.0, (0.25, 0.25, 0.25, 0.25)))
ALPHAS = {"H0": 0.0, "H1": 0.10, "H2": 0.20}
POLICIES = ("P0", "P1", "P2", "P3")

_SIGMA2 = math.log1p(SERVICE_CV**2)
_SIGMA = math.sqrt(_SIGMA2)
_MU = math.log(SERVICE_MEAN) - _SIGMA2 / 2.0
_SERVICE_VARIANCE = (SERVICE_CV * SERVICE_MEAN) ** 2
_LINUCB_ALPHA = alpha_from_delta(0.05)


@dataclass(frozen=True)
class Task:
    task_id: int
    arrival: float
    family: int
    phase: int
    deadline: float


@dataclass
class TaskRecord:
    task_id: int
    arrival: float
    family: int
    phase: int
    deadline: float
    policy: str
    admitted_agent: int | None
    selected_agent: int | None
    f_selected: float | None
    completion: float | None = None
    service_start: float | None = None
    correct: bool | None = None
    on_time: bool = False
    reward_p3: int | None = None
    p2_label_observed_at: float | None = None
    p3_reward_observed_at: float | None = None
    rejection_reason: str | None = None
    service_time: float = 0.0


@dataclass(frozen=True)
class RunConfig:
    seed: int
    n_agents: int
    composition: str
    policy: str
    horizon: float = HORIZON
    decision_alpha: float = _LINUCB_ALPHA
    probability_method: str = "two_moment"
    convolution_step: float = 0.002


def competency_matrix(n_agents: int, composition: str, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Return task-wise mean-preserving Q and hidden primary-family labels."""
    if n_agents not in (12, 24, 48) or n_agents % 4:
        raise ValueError("CE-04 requires N in {12,24,48}, divisible by four")
    if composition not in ALPHAS:
        raise ValueError("composition must be H0, H1, or H2")
    primary = np.repeat(np.arange(4), n_agents // 4)
    np.random.default_rng(_seed(seed, n_agents, 1)).shuffle(primary)
    s = np.where(primary[:, None] == np.arange(4)[None, :], 0.75, -0.25)
    q = 0.775 + ALPHAS[composition] * s
    return q, primary


def generate_workload(seed: int, n_agents: int, horizon: float = HORIZON) -> tuple[Task, ...]:
    """Generate one policy-independent continuous-time Poisson trajectory."""
    rng = np.random.default_rng(_seed(seed, n_agents, 2))
    result: list[Task] = []
    t = 0.0
    rate = ARRIVAL_RATE_PER_AGENT * n_agents
    while True:
        t += float(rng.exponential(1.0 / rate))
        if t >= horizon:
            break
        phase = 0 if t < 150.0 else 1 if t < 300.0 else 2
        probs = PHASES[phase][2]
        family = int(rng.choice(4, p=probs))
        task_id = len(result)
        result.append(Task(task_id, t, family, phase, t + DEADLINE_SLACK))
    return tuple(result)


def potential_service(seed: int, n_agents: int, task_id: int, agent_id: int) -> float:
    rng = np.random.default_rng(_seed(seed, n_agents, task_id, agent_id, 3))
    return float(rng.lognormal(_MU, _SIGMA))


def potential_correct(seed: int, n_agents: int, task_id: int, agent_id: int, q: float) -> bool:
    rng = np.random.default_rng(_seed(seed, n_agents, task_id, agent_id, 4))
    return bool(rng.random() < q)


def _seed(*parts: int) -> np.random.SeedSequence:
    return np.random.SeedSequence([int(x) & 0xFFFFFFFF for x in parts])


def _lognormal_cdf(x: float) -> float:
    if x <= 0:
        return 0.0
    return float(ndtr((math.log(x) - _MU) / _SIGMA))


def _residual_moments(age: float) -> tuple[float, float]:
    """Mean and variance of S-age conditional on S>age."""
    if age <= 0:
        return SERVICE_MEAN, _SERVICE_VARIANCE
    survival = max(1e-300, float(ndtr(-((math.log(age) - _MU) / _SIGMA))))
    raw = []
    for r in (1, 2):
        numerator = math.exp(r * _MU + 0.5 * r * r * _SIGMA2) * float(
            ndtr((r * _SIGMA2 + _MU - math.log(age)) / _SIGMA)
        )
        raw.append(numerator / survival)
    mean = raw[0] - age
    second = raw[1] - 2.0 * age * raw[0] + age * age
    return mean, max(0.0, second - mean * mean)


def deadline_probability_two_moment(age: float | None, queued_ahead: int,
                                    slack: float = DEADLINE_SLACK) -> float:
    """Two-moment lognormal sum approximation; no realized future service."""
    if queued_ahead < 0:
        raise ValueError("queued_ahead must be non-negative")
    full_count = queued_ahead + 1
    mean = full_count * SERVICE_MEAN
    variance = full_count * _SERVICE_VARIANCE
    if age is not None:
        rm, rv = _residual_moments(age)
        mean += rm
        variance += rv
    if mean <= 0 or slack <= 0:
        return 0.0
    sigma2 = math.log1p(variance / (mean * mean))
    sigma = math.sqrt(sigma2)
    mu = math.log(mean) - sigma2 / 2.0
    return float(ndtr((math.log(slack) - mu) / sigma))


def deadline_probability_convolution(age: float | None, queued_ahead: int,
                                     slack: float = DEADLINE_SLACK,
                                     step: float = 0.002) -> float:
    """Deterministic discretized convolution reference for service sums.

    Each bin stores exact lognormal probability mass; convolution adds the
    independent service terms. The active residual uses the exact conditional
    residual CDF. The final bin convention is conservative at the boundary.
    """
    if queued_ahead < 0 or step <= 0 or slack <= 0:
        raise ValueError("invalid queue, step, or slack")
    n_bins = int(math.ceil(slack / step))
    # Include one extra tail bin so the discretized PMF sums to one.
    full_edges = np.arange(n_bins + 2, dtype=float) * step
    full_cdf = np.array([_lognormal_cdf(x) for x in full_edges])
    pmf_full = np.diff(full_cdf)
    pmf_full = np.maximum(pmf_full, 0.0)
    pmf_full = np.append(pmf_full, max(0.0, 1.0 - float(pmf_full.sum())))
    pmf_full /= pmf_full.sum()
    pmf = pmf_full
    if age is not None:
        fa = _lognormal_cdf(age)
        denom = max(1e-300, 1.0 - fa)
        residual_cdf = np.array([max(0.0, min(1.0, (_lognormal_cdf(age + x) - fa) / denom))
                                 for x in full_edges])
        residual_pmf = np.maximum(np.diff(residual_cdf), 0.0)
        residual_pmf = np.append(residual_pmf, max(0.0, 1.0 - float(residual_pmf.sum())))
        residual_pmf /= residual_pmf.sum()
        pmf = np.convolve(pmf, residual_pmf)
    for _ in range(queued_ahead):
        pmf = np.convolve(pmf, pmf_full)
    # New task is already the first full service term.
    # Probability mass in bins 0..floor(slack/step)-1 has upper edge <= slack.
    # At exact-grid slack, include the boundary bin as a measure-zero endpoint.
    limit = int(math.floor(slack / step + 1e-12))
    return float(np.clip(pmf[:limit].sum(), 0.0, 1.0))


def validate_probability_approximation(step: float = 0.001) -> dict:
    """Predeclared queue-state battery; reports errors near the .50 cutoff."""
    # Fixed grid includes the predeclared boundary state (age=.70, one
    # waiting job), whose exact probability is close to the .50 admission cut.
    cases = [(None, q) for q in range(4)] + [(age, q) for age in (0.25, 0.50, 0.70, 0.75, 1.0, 2.0, 2.75)
                                             for q in range(3)]
    rows = []
    for age, queued in cases:
        approx = deadline_probability_two_moment(age, queued)
        reference = deadline_probability_convolution(age, queued, step=step)
        rows.append({"age": age, "queued_ahead": queued, "two_moment": approx,
                     "convolution": reference, "absolute_error": abs(approx - reference)})
    near = [r for r in rows if 0.45 <= r["convolution"] <= 0.55]
    return {"method": "two_moment", "step": step, "cases": rows,
            "near_threshold_cases": len(near),
            "max_near_threshold_error": max((r["absolute_error"] for r in near), default=0.0),
            "passes_tolerance": all(r["absolute_error"] <= 0.01 for r in near)}


def factorial_configs(stage: str = "pilot") -> tuple[RunConfig, ...]:
    """Return the frozen CE-04 factorial; constructing configs runs nothing."""
    seeds = (0, 1, 2) if stage == "pilot" else tuple(range(1000, 1030)) if stage == "campaign" else None
    if seeds is None:
        raise ValueError("stage must be pilot or campaign")
    return tuple(RunConfig(seed, n, h, p) for seed in seeds for n in (12, 24, 48)
                 for h in ("H0", "H1", "H2") for p in POLICIES)


@dataclass
class _Agent:
    resource: simpy.Resource
    waiting: list[int]
    active_started: float | None = None
    active_task: int | None = None


class _DelayedDisjointLinUCB:
    """Thin CE-04 adapter around the repository's disjoint LinUCB class."""
    def __init__(self, n_agents: int, alpha: float):
        self.model = LinUCBDisjoint(n_agents, 4, alpha)

    def scores(self, contexts: list[np.ndarray]) -> list[float]:
        return list(self.model.scores(contexts))

    def observe(self, arm: int, context: np.ndarray, reward: int) -> None:
        self.model.observe_delayed(arm, context, reward)


def _choose_with_tie(scores: Iterable[float], admissible: list[int], tie_rank: np.ndarray) -> int:
    scores = list(scores)
    return min(admissible, key=lambda i: (-scores[i], int(tie_rank[i])))


def run_replica(config: RunConfig, tasks: tuple[Task, ...] | None = None) -> dict:
    """Run one policy/composition/scale/seed; not invoked by unit tests as a campaign."""
    if config.policy not in POLICIES:
        raise ValueError(f"unknown policy {config.policy}")
    if config.probability_method not in ("two_moment", "convolution"):
        raise ValueError("unknown probability method")
    q, _primary_hidden = competency_matrix(config.n_agents, config.composition, config.seed)
    tasks = generate_workload(config.seed, config.n_agents, config.horizon) if tasks is None else tasks
    env = simpy.Environment()
    agents = [_Agent(simpy.Resource(env, capacity=1), []) for _ in range(config.n_agents)]
    rank = np.arange(config.n_agents)
    np.random.default_rng(_seed(config.seed, config.n_agents, 5)).shuffle(rank)
    p2_s = np.zeros_like(q, dtype=int)
    p2_f = np.zeros_like(q, dtype=int)
    p3 = _DelayedDisjointLinUCB(config.n_agents, config.decision_alpha)
    records: list[TaskRecord] = []
    feedback_events: list[dict] = []
    decision_seconds = 0.0
    decision_cpu_seconds = 0.0
    decision_latencies: list[float] = []
    started_cpu = time.process_time()
    started_wall = time.perf_counter()
    scheduled = 0.0

    def prob(agent_id: int, now: float, deadline: float) -> float:
        state = agents[agent_id]
        age = None if state.active_started is None else max(0.0, now - state.active_started)
        queued = len(state.waiting)
        slack = deadline - now
        if config.probability_method == "two_moment":
            return deadline_probability_two_moment(age, queued, slack)
        return deadline_probability_convolution(age, queued, slack, config.convolution_step)

    def log_p3_reward(rec: TaskRecord, reward: int, observed_at: float, source: str) -> None:
        if rec.reward_p3 is not None:
            return
        rec.reward_p3 = int(reward)
        rec.p3_reward_observed_at = float(observed_at)
        feedback_events.append({"task_id": rec.task_id, "time": float(observed_at),
                                "reward": int(reward), "source": source})
        if config.policy == "P3" and rec.selected_agent is not None:
            context = np.zeros(4)
            context[rec.family] = float(rec.f_selected)
            p3.observe(rec.selected_agent, context, int(reward))

    def deadline_watch(task: Task, rec: TaskRecord):
        yield env.timeout(max(0.0, task.deadline - env.now))
        # Let an exact-deadline completion event resolve first; service times
        # are continuous, but the boundary rule is still explicit.
        yield env.timeout(0)
        if rec.completion is None or rec.completion > task.deadline:
            log_p3_reward(rec, 0, env.now, "deadline")
            rec.on_time = False

    def serve(task: Task, rec: TaskRecord, agent_id: int):
        state = agents[agent_id]
        with state.resource.request() as request:
            yield request
            if task.task_id in state.waiting:
                state.waiting.remove(task.task_id)
            state.active_started = env.now
            state.active_task = task.task_id
            rec.service_start = env.now
            duration = potential_service(config.seed, config.n_agents, task.task_id, agent_id)
            rec.service_time = duration
            yield env.timeout(duration)
            rec.completion = env.now
            rec.correct = potential_correct(config.seed, config.n_agents, task.task_id,
                                            agent_id, float(q[agent_id, task.family]))
            rec.on_time = bool(rec.correct and rec.completion <= task.deadline)
            if config.policy in ("P2",):
                rec.p2_label_observed_at = float(env.now)
                if rec.correct:
                    p2_s[agent_id, task.family] += 1
                else:
                    p2_f[agent_id, task.family] += 1
            if config.policy == "P3" and rec.reward_p3 is None:
                # If the completion is on-time, the binary reward is observable now.
                if rec.completion <= task.deadline:
                    log_p3_reward(rec, int(bool(rec.correct)), env.now, "completion")
            state.active_started = None
            state.active_task = None

    def arrival_process():
        nonlocal decision_seconds, decision_cpu_seconds, scheduled
        for task in tasks:
            if task.arrival > env.now:
                yield env.timeout(task.arrival - env.now)
            decision_start = time.perf_counter()
            decision_cpu_start = time.process_time()
            f_values = [prob(i, env.now, task.deadline) for i in range(config.n_agents)]
            admissible = [i for i, f in enumerate(f_values) if f >= ADMISSION_THRESHOLD]
            rec = TaskRecord(task.task_id, task.arrival, task.family, task.phase, task.deadline,
                             config.policy, None, None, None)
            records.append(rec)
            if not admissible:
                rec.rejection_reason = "no_agent_meets_common_deadline_probability_threshold"
                decision_elapsed = time.perf_counter() - decision_start
                decision_seconds += decision_elapsed
                decision_latencies.append(decision_elapsed)
                decision_cpu_seconds += time.process_time() - decision_cpu_start
                continue
            if config.policy == "P0":
                loads = []
                for i in range(config.n_agents):
                    state = agents[i]
                    residual = (0.0 if state.active_started is None else
                                _residual_moments(max(0.0, env.now - state.active_started))[0])
                    loads.append(residual + SERVICE_MEAN * len(state.waiting))
                selected = _choose_with_tie([-float(x) for x in loads], admissible, rank)
            elif config.policy in ("P1", "P2"):
                scores = [float((q[i, task.family] if config.policy == "P1" else
                                 (1 + p2_s[i, task.family]) / (2 + p2_s[i, task.family] + p2_f[i, task.family]))
                                 * f_values[i]) for i in range(config.n_agents)]
                selected = _choose_with_tie(scores, admissible, rank)
            else:
                contexts = []
                for i in range(config.n_agents):
                    x = np.zeros(4); x[task.family] = f_values[i]; contexts.append(x)
                scores = p3.scores(contexts)
                selected = _choose_with_tie(scores, admissible, rank)
            decision_elapsed = time.perf_counter() - decision_start
            decision_seconds += decision_elapsed
            decision_latencies.append(decision_elapsed)
            decision_cpu_seconds += time.process_time() - decision_cpu_start
            rec.admitted_agent = rec.selected_agent = selected
            rec.f_selected = f_values[selected]
            agents[selected].waiting.append(task.task_id)
            env.process(serve(task, rec, selected))
            env.process(deadline_watch(task, rec))
            scheduled += 1

    env.process(arrival_process())
    env.run()
    # Drain admitted tasks; no new arrivals are generated after horizon.
    if any(a.active_task is not None or a.waiting for a in agents):
        env.run()
    elapsed_wall = time.perf_counter() - started_wall
    elapsed_cpu = time.process_time() - started_cpu
    successful = sum(int(r.on_time and bool(r.correct)) for r in records)
    all_arrivals = len(tasks)
    service_total = float(sum(r.service_time for r in records))
    success_by_task = [sum(1 for r in records if r.family == k and r.on_time and r.correct)
                       for k in range(4)]
    arrivals_by_task = [sum(1 for t in tasks if t.family == k) for k in range(4)]
    completed = [r for r in records if r.completion is not None]
    latencies = np.asarray([r.completion - r.arrival for r in completed], dtype=float)
    end_time = max([config.horizon, *(r.completion or 0.0 for r in completed)])
    per_agent_service = [sum(r.service_time for r in records if r.selected_agent == i)
                         for i in range(config.n_agents)]
    by_phase = [sum(1 for r in records if r.phase == phase and r.on_time and r.correct)
                for phase in range(3)]
    arrivals_by_phase = [sum(1 for t in tasks if t.phase == phase) for phase in range(3)]
    return {
        "config": asdict(config), "n_arrivals": all_arrivals,
        "n_rejected": all_arrivals - scheduled,
        "simulation_drain_end": float(env.now),
        "n_admitted": scheduled, "n_success_on_time": successful,
        "success_on_time_rate": successful / all_arrivals if all_arrivals else 0.0,
        "success_by_task": success_by_task, "arrivals_by_task": arrivals_by_task,
        "success_by_phase": by_phase, "arrivals_by_phase": arrivals_by_phase,
        "n_incorrect": sum(1 for r in completed if r.correct is False),
        "n_late": sum(1 for r in completed if r.completion is not None and r.completion > r.deadline),
        "latency_mean": float(latencies.mean()) if latencies.size else None,
        "latency_p50": float(np.quantile(latencies, .50)) if latencies.size else None,
        "latency_p95": float(np.quantile(latencies, .95)) if latencies.size else None,
        "agent_service_time": per_agent_service,
        "agent_utilization": [x / end_time if end_time else 0.0 for x in per_agent_service],
        "assignment_counts": [sum(1 for r in records if r.selected_agent == i)
                              for i in range(config.n_agents)],
        "service_time_total": service_total,
        "service_time_per_success": service_total / successful if successful else None,
        "decision_seconds": decision_seconds, "decision_cpu_seconds": decision_cpu_seconds,
        "decision_latency_mean_seconds": float(np.mean(decision_latencies)) if decision_latencies else None,
        "decision_latency_p50_seconds": float(np.quantile(decision_latencies, .50)) if decision_latencies else None,
        "decision_latency_p95_seconds": float(np.quantile(decision_latencies, .95)) if decision_latencies else None,
        "cpu_seconds": elapsed_cpu,
        "wall_seconds": elapsed_wall, "peak_rss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_rss_unit": "platform-native resource.getrusage ru_maxrss",
        "records": [asdict(r) for r in sorted(records, key=lambda x: x.task_id)],
        "p3_feedback_events": feedback_events,
        "task_ids": [t.task_id for t in tasks],
    }


def to_experiment_run(result: dict):
    """Serialize one replica through the existing HLS ExperimentRun contract."""
    from hls.experiment_contract import (
        ExperimentEvent, ExperimentRun, MetricValue, SeedRecord, UnitDeclaration,
    )
    config = result["config"]
    seeds = tuple(SeedRecord(name, int(config["seed"]), purpose) for name, purpose in (
        ("demand", "Poisson arrivals and task-family marks"),
        ("composition", "balanced hidden primary-family permutation"),
        ("service", "potential service variates keyed by task and agent"),
        ("correctness", "potential correctness variates keyed by task and agent"),
        ("tie_break", "policy/composition-independent agent priority"),
        ("p3_exploration", "reserved stream; LinUCB exploration is deterministic"),
    ))
    events = tuple(ExperimentEvent(i, "task_record", config["policy"], record,
                                   time_index=max(0, int(record["arrival"])))
                   for i, record in enumerate(result["records"]))
    metric_specs = (
        ("success_on_time_rate", result["success_on_time_rate"], "fraction", "higher"),
        ("n_arrivals", result["n_arrivals"], "tasks", None),
        ("n_admitted", result["n_admitted"], "tasks", None),
        ("n_rejected", result["n_rejected"], "tasks", None),
        ("service_time_total", result["service_time_total"], "time units", "lower"),
        ("service_time_per_success", result["service_time_per_success"], "time units/success", "lower"),
        ("latency_mean", result["latency_mean"], "time units", "lower"),
        ("decision_seconds", result["decision_seconds"], "seconds", "lower"),
        ("decision_latency_p95_seconds", result["decision_latency_p95_seconds"], "seconds/decision", "lower"),
        ("cpu_seconds", result["cpu_seconds"], "seconds", "lower"),
    )
    metrics = tuple(MetricValue(name, float(value), unit, "CE-04 replica-level recorded metric", direction)
                    for name, value, unit, direction in metric_specs
                    if value is not None)
    revision = result.get("provenance", {}).get("git_revision")
    return ExperimentRun(
        schema_version="hls-experiment-run/1.0", run_id=f"ce04-{config['seed']}-N{config['n_agents']}-{config['composition']}-{config['policy']}",
        mechanism_id="CE04-discrete-event-assignment-v1", policy_id=config["policy"],
        configuration=config, initial_conditions={"composition": config["composition"], "n_agents": config["n_agents"]},
        random_seeds=seeds,
        information_available={"P1": "true q, current queue state, service law", "P2": "observed correctness labels, current queue state",
                              "P3": "past selected-action binary rewards, current queue state", "P0": "current queue state"},
        observation_model={"P2": "Beta(1,1) correctness posterior; labels at task completion",
                           "P3": "binary on-time success; delayed update at completion/deadline"},
        software_revision=revision,
        units=(UnitDeclaration("simulation_time", "protocol time units", "continuous event time"),),
        events=events, metrics=metrics,
        mechanism_results={k: v for k, v in result.items() if k not in {"records", "task_ids"}},
        metadata={"study": "HLS-CE-04", "records_included_in_events": True,
                  "potential_outcomes_keyed_by": "replicate seed, N, task id, agent id",
                  "seed_derivation": "NumPy SeedSequence([replicate_seed, N, task_id, agent_id, stream_id]); demand/composition/ties use independent stream ids"},
    )


def run_factorial(stage: str, output_path: str | os.PathLike[str]) -> int:
    """Execute a CE-04 design and append immutable JSONL replica records.

    This function is deliberately not called during implementation or unit
    testing. Pilot/campaign execution remains separately CE-authorized.
    """
    configs = factorial_configs(stage)
    workload_cache: dict[tuple[int, int], tuple[Task, ...]] = {}
    revision = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=False).stdout.strip() or "unknown"
    target = os.fspath(output_path)
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "x", encoding="utf-8") as handle:
        for config in configs:
            key = (config.seed, config.n_agents)
            workload_cache.setdefault(key, generate_workload(*key))
            result = run_replica(config, workload_cache[key])
            result["provenance"] = {"git_revision": revision, "python": sys.version,
                                    "numpy": np.__version__, "scipy": __import__("scipy").__version__,
                                    "simpy": simpy.__version__}
            handle.write(to_experiment_run(result).to_json() + "\n")
            handle.flush()
    return len(configs)


def paired_bootstrap(differences: Iterable[float], *, seed: int = 20261026,
                     n_resamples: int = 10_000) -> dict:
    """Percentile CI over independent paired replicate differences."""
    values = np.asarray(tuple(differences), dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError("provide at least two finite replicate-level differences")
    rng = np.random.default_rng(seed)
    means = np.mean(values[rng.integers(0, len(values), size=(n_resamples, len(values)))], axis=1)
    return {"mean": float(values.mean()), "sd": float(values.std(ddof=1)),
            "ci95": [float(np.quantile(means, .025)), float(np.quantile(means, .975))],
            "n_replicates": int(values.size), "bootstrap_resamples": n_resamples}


def paired_contrast(differences: Iterable[float], *, bootstrap_seed: int = 20261026) -> dict:
    """Replicate-level paired estimate, percentile bootstrap CI and paired t p-value."""
    from scipy.stats import ttest_1samp
    values = np.asarray(tuple(differences), dtype=float)
    summary = paired_bootstrap(values, seed=bootstrap_seed, n_resamples=10_000)
    if np.all(values == values[0]):
        p_value = 1.0 if values[0] == 0.0 else 0.0
    else:
        p_value = float(ttest_1samp(values, popmean=0.0).pvalue)
    summary["p_value_paired_t_two_sided"] = p_value
    return summary


def analyze_factorial(rows: Iterable[dict], *, bootstrap_seed: int = 20261026) -> dict:
    """Summarize E3 and CE addendum contrasts over paired replicate records."""
    data = list(rows)
    normalized = []
    for row in data:
        if "mechanism_results" in row:  # serialized ExperimentRun
            normalized.append({"config": row["configuration"],
                               "success_on_time_rate": row["mechanism_results"]["success_on_time_rate"]})
        else:
            normalized.append(row)
    indexed = {(r["config"]["seed"], r["config"]["n_agents"],
                r["config"]["composition"], r["config"]["policy"]): r["success_on_time_rate"]
               for r in normalized}
    seeds = sorted({key[0] for key in indexed})
    scales = (12, 24, 48)
    raw: dict[str, list[float]] = {}
    def get(seed, n, h, p): return indexed[(seed, n, h, p)]
    # E3's prespecified composition and policy contrasts, plus CE's five
    # confirmatory contrasts, kept as named paired replicate-level vectors.
    for n in scales:
        for policy in POLICIES:
            for h in ("H1", "H2"):
                raw[f"E3:H:{h}-H0:{policy}:N{n}"] = [get(s,n,h,policy)-get(s,n,"H0",policy) for s in seeds]
        for h in ("H0", "H1", "H2"):
            for policy in ("P1", "P2"):
                raw[f"E3:P:{policy}-P0:{h}:N{n}"] = [get(s,n,h,policy)-get(s,n,h,"P0") for s in seeds]
        raw[f"CE:C3:P2-P1:H2:N{n}"] = [get(s,n,"H2","P2")-get(s,n,"H2","P1") for s in seeds]
        raw[f"CE:C4:P3-P2:H2:N{n}"] = [get(s,n,"H2","P3")-get(s,n,"H2","P2") for s in seeds]
        raw[f"CE:C5:interaction:H2-H0:P3-v-P0:N{n}"] = [
            (get(s,n,"H2","P3")-get(s,n,"H0","P3")) -
            (get(s,n,"H2","P0")-get(s,n,"H0","P0")) for s in seeds]
        for h in ("H1", "H2"):
            for policy in ("P1", "P2", "P3"):
                raw[f"E3:interaction:{h}-H0:{policy}-P0:N{n}"] = [
                    (get(s,n,h,policy)-get(s,n,"H0",policy)) -
                    (get(s,n,h,"P0")-get(s,n,"H0","P0")) for s in seeds]
    for h in ("H0", "H1", "H2"):
        for policy in POLICIES:
            for first, second in ((24, 12), (48, 24)):
                raw[f"E3:scale:N{first}-N{second}:{h}:{policy}"] = [
                    get(s, first, h, policy)-get(s, second, h, policy) for s in seeds]
    summaries = {name: paired_contrast(values, bootstrap_seed=bootstrap_seed + j)
                 for j, (name, values) in enumerate(raw.items())}
    for values, item in zip(raw.values(), summaries.values()):
        tost = tost_equivalence(values, margin=0.02)
        item["tost_pm_2pp"] = tost
        item["tost_p_value"] = max(tost["p_lower"], tost["p_upper"])
    # Holm family is the complete prespecified set returned here; no filtering
    # by observed significance occurs.
    adjusted = holm_adjust([v["p_value_paired_t_two_sided"] for v in summaries.values()])
    tost_adjusted = holm_adjust([v["tost_p_value"] for v in summaries.values()])
    for item, p_adj, tost_p_adj in zip(summaries.values(), adjusted, tost_adjusted):
        item["p_value_holm_all_confirmatory"] = p_adj
        item["tost_p_holm_all_confirmatory"] = tost_p_adj
        item["tost_equivalent_holm_0_05"] = tost_p_adj < 0.05
    return {"unit": "independent paired replicate seed", "contrasts": summaries,
            "CE_contrast_aliases": {"C1": "E3:H:H2-H0:P1:N12/N24/N48",
                                    "C2": "E3:P:P1-P0:H2:N12/N24/N48"},
            "holm_family": "all E3 and CE confirmatory contrasts returned by this analysis"}


def holm_adjust(p_values: Iterable[float]) -> list[float]:
    """Holm step-down adjusted p-values, returned in original order."""
    p = np.asarray(tuple(p_values), dtype=float)
    if np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("p-values must be finite and in [0,1]")
    order = np.argsort(p); m = len(p); adjusted = np.empty(m); running = 0.0
    for rank_idx, idx in enumerate(order):
        running = max(running, min(1.0, (m - rank_idx) * p[idx]))
        adjusted[idx] = running
    return adjusted.tolist()


def tost_equivalence(differences: Iterable[float], margin: float = 0.02) -> dict:
    """Paired one-sample TOST against ±margin; unit is independent replicate."""
    from scipy.stats import t
    x = np.asarray(tuple(differences), dtype=float)
    if x.size < 2 or margin <= 0 or np.any(~np.isfinite(x)):
        raise ValueError("invalid TOST input")
    n = x.size; mean = float(x.mean()); se = float(x.std(ddof=1) / math.sqrt(n))
    if se == 0:
        p_lower = 0.0 if mean > -margin else 1.0
        p_upper = 0.0 if mean < margin else 1.0
    else:
        p_lower = float(1 - t.cdf((mean + margin) / se, n - 1))
        p_upper = float(t.cdf((mean - margin) / se, n - 1))
    return {"mean": mean, "margin": margin, "p_lower": p_lower,
            "p_upper": p_upper, "equivalent_at_0_05": max(p_lower, p_upper) < .05}
