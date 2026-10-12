"""Matched sequential FAST/DEEP/META development comparison.

Safe by default: runs only a two-cell smoke test. ``--full`` executes one fresh
history in every frozen S_dev x Phi_dev cell (420 matched histories).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_c33 import c33  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.campaign1_protocol import PARAMETERS  # noqa: E402
from hls.campaign3_problem_generator import generator_transition  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

OUT = ROOT / "results/campaigns/campaign3_fast_deep_meta"
DEEP_MODE = planner.ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT
BOOTSTRAP_B = 2000
BOOTSTRAP_SEED = 20261012
N_CELLS = 20 * 21


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def new_tasks(replicates: int = 1) -> list[dict]:
    teams, kernels = c33.team_kernel_maps()
    tasks = []
    for team in teams:
        state = tuple(tuple(float(team[f"s{i}{k}"]) for k in (1, 2)) for i in (1, 2, 3))
        for kernel in kernels:
            params = (float(kernel["alpha_stay"]), float(kernel["alpha_move"]),
                      float(kernel["alpha_return"]), None if kernel["sigma"] == "" else float(kernel["sigma"]))
            for rep in range(replicates):
                namespace = ("campaign3_fast_deep_meta_v1", team["team_id"], kernel["kernel_id"], rep)
                tasks.append({"history_id": ":".join(map(str, namespace)), "team_id": team["team_id"],
                              "kernel_id": kernel["kernel_id"], "replicate": rep, "team": state,
                              "kernel": params, "problem_seed": c33.stable_seed(*namespace, "problem"),
                              "noise_seed": c33.stable_seed(*namespace, "noise")})
    if len(tasks) != N_CELLS * replicates:
        raise RuntimeError("development factorial count mismatch")
    if any(task["team_id"].startswith("F") and int(task["team_id"][1:]) > 16 for task in tasks):
        raise RuntimeError("held-out team entered execution")
    return tasks


def exogenous(task: dict) -> tuple[tuple[float, ...], tuple[float, ...]]:
    prng = np.random.default_rng(task["problem_seed"])
    nrng = np.random.default_rng(task["noise_seed"])
    problems = [float(prng.uniform(0.2, 0.8))]
    for _ in range(11):
        problems.append(generator_transition(problems, task["kernel"], prng).p_next)
    eps = tuple(float(x) for x in nrng.standard_normal(36))
    return tuple(problems), eps


def choose_fast_action(state, belief, remaining: int):
    if remaining < 1:
        raise ValueError("remaining must be positive")
    return planner.choose_fast_action(state, belief, HYPOTHESIS_REPERTOIRE)


def choose_deep_action(state, belief, remaining: int):
    if remaining < 1:
        raise ValueError("remaining must be positive")
    return planner.choose_prospective_action(state, belief, HYPOTHESIS_REPERTOIRE,
                                             remaining=remaining, policy_mode=DEEP_MODE,
                                             eta=PARAMETERS["eta"])


def choose_meta_action(state, belief, remaining: int, tau: int, model_spec: dict):
    """Return selected action and measured selector/solver costs.

    Remaining=1 is resolved directly by FAST; otherwise only the selected
    operator is called. In particular, a FAST acceptance never calls DEEP.
    """
    if remaining == 1:
        start = time.perf_counter_ns()
        action, value = choose_fast_action(state, belief, remaining)
        return action, {"route": "FAST_TERMINAL", "score": "", "selector_ns": 0,
                        "fast_ns": time.perf_counter_ns() - start, "deep_ns": 0}
    started = time.perf_counter_ns()
    score = float(c33.predict(model_spec, c33.feature_vector(state, belief, tau).reshape(1, -1))[0])
    selector_ns = time.perf_counter_ns() - started
    if score < 0.0:
        started = time.perf_counter_ns()
        action, _ = choose_fast_action(state, belief, remaining)
        return action, {"route": "FAST_ACCEPT", "score": score, "selector_ns": selector_ns,
                        "fast_ns": time.perf_counter_ns() - started, "deep_ns": 0}
    started = time.perf_counter_ns()
    action, _ = choose_deep_action(state, belief, remaining)
    return action, {"route": "DEEP_INVOKE", "score": score, "selector_ns": selector_ns,
                    "fast_ns": 0, "deep_ns": time.perf_counter_ns() - started}


def simulate_history(payload: tuple[dict, dict]) -> tuple[list[dict], list[dict]]:
    task, model_spec = payload
    problems, eps = exogenous(task)
    hypotheses, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    runs, trajectory = [], []
    for policy in ("FAST", "DEEP", "META"):
        state = task["team"]
        belief = prior
        cumulative = 0.0
        compute_ns = selector_ns_total = fast_ns_total = deep_ns_total = 0
        deep_count = fast_count = terminal_fast_count = 0
        for j, p in enumerate(problems):
            if j:
                belief = prior
            for step in range(3):
                remaining = 3 - step
                tau = 36 - (3 * j + step)
                before_state, before_belief = state, belief
                if policy == "FAST":
                    started = time.perf_counter_ns()
                    action, _ = choose_fast_action(state, belief, remaining)
                    cost = {"route": "FAST", "score": "", "selector_ns": 0,
                            "fast_ns": time.perf_counter_ns() - started, "deep_ns": 0}
                elif policy == "DEEP":
                    started = time.perf_counter_ns()
                    action, _ = choose_deep_action(state, belief, remaining)
                    cost = {"route": "DEEP", "score": "", "selector_ns": 0,
                            "fast_ns": 0, "deep_ns": time.perf_counter_ns() - started}
                else:
                    action, cost = choose_meta_action(state, belief, remaining, tau, model_spec)
                route = cost["route"]
                selector_ns_total += cost["selector_ns"]
                fast_ns_total += cost["fast_ns"]
                deep_ns_total += cost["deep_ns"]
                compute_ns += cost["selector_ns"] + cost["fast_ns"] + cost["deep_ns"]
                if policy == "META":
                    deep_count += route == "DEEP_INVOKE"
                    fast_count += route == "FAST_ACCEPT"
                    terminal_fast_count += route == "FAST_TERMINAL"
                real = theory._real_decision(state, belief, action, (p, 1.0 - p), eps[3 * j + step], hypotheses)
                cumulative += real.mu_true
                trajectory.append({"history_id": task["history_id"], "team_id": task["team_id"],
                                   "kernel_id": task["kernel_id"], "replicate": task["replicate"],
                                   "policy": policy, "problem_index": j + 1, "decision": step + 1,
                                   "remaining": remaining, "tau": tau, "route": route,
                                   "selector_score": cost["score"], "action_id": JOINT_ACTIONS.index(action),
                                   "decision_compute_ns": cost["selector_ns"] + cost["fast_ns"] + cost["deep_ns"],
                                   "selector_ns": cost["selector_ns"], "fast_ns": cost["fast_ns"],
                                   "deep_ns": cost["deep_ns"], "mu_true": real.mu_true,
                                   "state_before": packed(before_state), "belief_before": packed(before_belief),
                                   "state_after": packed(real.state_after), "belief_after": packed(real.belief_after)})
                state, belief = real.state_after, real.belief_after
        runs.append({"history_id": task["history_id"], "team_id": task["team_id"],
                     "kernel_id": task["kernel_id"], "replicate": task["replicate"],
                     "policy": policy, "cumulative_mu_true": cumulative, "decision_compute_ns": compute_ns,
                     "selector_ns": selector_ns_total, "fast_ns": fast_ns_total, "deep_ns": deep_ns_total,
                     "deep_invocations": deep_count, "fast_acceptances": fast_count,
                     "terminal_fast_decisions": terminal_fast_count,
                     "problem_seed": task["problem_seed"], "noise_seed": task["noise_seed"],
                     "problem_stream_sha256": hashlib.sha256(packed(problems).encode()).hexdigest(),
                     "noise_stream_sha256": hashlib.sha256(packed(eps).encode()).hexdigest()})
    return runs, trajectory


def bootstrap_difference(values: np.ndarray, rng: np.random.Generator) -> dict:
    draws = np.empty(BOOTSTRAP_B)
    for i in range(BOOTSTRAP_B):
        draws[i] = rng.choice(values, size=len(values), replace=True).mean()
    return {"mean": float(values.mean()), "median": float(np.median(values)),
            "ci95": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))],
            "q05": float(np.quantile(values, .05)), "q95": float(np.quantile(values, .95))}


def summarize(runs: pd.DataFrame, traces: pd.DataFrame) -> dict:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    wide_perf = runs.pivot(index="history_id", columns="policy", values="cumulative_mu_true")
    wide_cost = runs.pivot(index="history_id", columns="policy", values="decision_compute_ns")
    contrasts = {}
    for a, b in (("DEEP", "FAST"), ("META", "FAST"), ("META", "DEEP")):
        contrasts[f"performance_{a}-{b}"] = bootstrap_difference((wide_perf[a] - wide_perf[b]).to_numpy(), rng)
        contrasts[f"compute_ns_{a}-{b}"] = bootstrap_difference((wide_cost[a] - wide_cost[b]).to_numpy(dtype=float), rng)
    meta = traces[traces.policy == "META"]
    n = len(meta)
    deep = int(meta.route.eq("DEEP_INVOKE").sum())
    fast = int(meta.route.eq("FAST_ACCEPT").sum())
    terminal = int(meta.route.eq("FAST_TERMINAL").sum())
    latency = {policy: {"mean_ms": float(group.decision_compute_ns.mean() / 1e6),
                        "median_ms": float(group.decision_compute_ns.median() / 1e6),
                        "q90_ms": float(group.decision_compute_ns.quantile(.9) / 1e6),
                        "q95_ms": float(group.decision_compute_ns.quantile(.95) / 1e6),
                        "total_seconds": float(group.decision_compute_ns.sum() / 1e9)}
               for policy, group in traces.groupby("policy")}
    return {"design": {"teams": 20, "kernels": 21, "replicates_per_cell": 1,
                       "base_histories": int(runs.history_id.nunique()), "policy_runs": len(runs),
                       "decisions_per_policy": int(len(traces) / 3)},
            "mean_cumulative_mu_true": {k: float(v) for k, v in runs.groupby("policy").cumulative_mu_true.mean().items()},
            "latency_uncached_measured": latency,
            "meta_routing": {"decisions": n, "deep_invocations": deep, "deep_fraction_all_decisions": deep / n,
                             "fast_acceptances": fast, "fast_acceptance_fraction_all_decisions": fast / n,
                             "terminal_fast_decisions": terminal, "terminal_fraction": terminal / n,
                             "deep_fraction_nonterminal": deep / max(1, n - terminal)},
            "paired_bootstrap_differences": contrasts,
            "bootstrap": {"unit": "matched complete base history", "replicates": BOOTSTRAP_B,
                          "seed": BOOTSTRAP_SEED, "interval": "two-sided percentile 95%"}}


def cached_cost_benchmark(model_spec: dict, trajectory: pd.DataFrame, count: int = 64) -> dict:
    """Compare cold operator cost with warm exact-action-cache lookups."""
    source = trajectory[trajectory.policy == "DEEP"]
    per_remaining = max(1, count // 3)
    chosen = pd.concat([
        group.iloc[np.linspace(0, len(group) - 1, per_remaining, dtype=int)]
        for _, group in source.groupby("remaining", sort=True)
    ], ignore_index=True)
    cold = {name: [] for name in ("FAST", "DEEP", "META")}
    warm = {name: [] for name in cold}

    @lru_cache(maxsize=None)
    def fast_cached(s, b, r):
        return choose_fast_action(s, b, r)[0]

    @lru_cache(maxsize=None)
    def deep_cached(s, b, r):
        return choose_deep_action(s, b, r)[0]

    for row in chosen.itertuples(index=False):
        s = tuple(tuple(float(v) for v in sr) for sr in json.loads(row.state_before))
        b = tuple(float(v) for v in json.loads(row.belief_before))
        r = int(row.remaining)
        x = c33.feature_vector(s, b, int(row.tau))
        def meta_call(cached: bool = False):
            score = float(c33.predict(model_spec, x.reshape(1, -1))[0])
            if cached:
                return deep_cached(s, b, r) if score >= 0 else fast_cached(s, b, r)
            return choose_deep_action(s, b, r)[0] if score >= 0 else choose_fast_action(s, b, r)[0]
        calls = {"FAST": lambda: choose_fast_action(s, b, r)[0],
                 "DEEP": lambda: choose_deep_action(s, b, r)[0], "META": meta_call}
        cache_calls = {"FAST": lambda: fast_cached(s, b, r), "DEEP": lambda: deep_cached(s, b, r),
                       "META": lambda: meta_call(cached=True)}
        for policy in cold:
            start = time.perf_counter_ns(); calls[policy](); cold[policy].append(time.perf_counter_ns() - start)
            cache_calls[policy]()
            start = time.perf_counter_ns(); cache_calls[policy](); warm[policy].append(time.perf_counter_ns() - start)
    return {"sampled_existing_states": len(chosen), "sampled_states_by_remaining": chosen.remaining.value_counts().sort_index().to_dict(),
            "cache_method": "exact S,b,remaining memoization; warm lookup; META inference still charged",
            "cold_median_ms": {k: float(np.median(v) / 1e6) for k, v in cold.items()},
            "cold_q90_ms": {k: float(np.quantile(v, .9) / 1e6) for k, v in cold.items()},
            "warm_cached_median_ms": {k: float(np.median(v) / 1e6) for k, v in warm.items()},
            "warm_cached_q90_ms": {k: float(np.quantile(v, .9) / 1e6) for k, v in warm.items()}}


def finalize_persisted_full() -> dict:
    """Recover provenance/analysis after raw full tables were safely written."""
    output = OUT / "sequential_full"
    runs_path, traces_path = output / "runs.csv", output / "trajectories.csv.gz"
    manifest_path = output / "execution_manifest.json"
    if manifest_path.exists() or not runs_path.is_file() or not traces_path.is_file():
        raise RuntimeError("recovery requires both raw tables and no existing manifest")
    runs = pd.read_csv(runs_path)
    traces = pd.read_csv(traces_path)
    expected = {task["history_id"] for task in new_tasks()}
    if runs.history_id.nunique() != 420 or set(runs.history_id) != expected or len(runs) != 1260 or len(traces) != 45_360:
        raise RuntimeError("persisted full outputs failed exact design validation")
    if not runs.groupby("history_id").problem_stream_sha256.nunique().eq(1).all() or not runs.groupby("history_id").noise_stream_sha256.nunique().eq(1).all():
        raise RuntimeError("persisted full outputs failed CRN validation")
    model_path = c33.OUT / "selector_model.json"
    model_spec = json.loads(model_path.read_text())
    summary = summarize(runs, traces)
    summary["cached_vs_uncached_benchmark"] = cached_cost_benchmark(model_spec, traces)
    summary["total_measured_decision_compute_seconds"] = {
        policy: float(value / 1e9) for policy, value in runs.groupby("policy").decision_compute_ns.sum().items()
    }
    summary["raw_runs_sha256"] = sha256(runs_path)
    summary["raw_trajectories_sha256"] = sha256(traces_path)
    (output / "analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    incident = {"event": "post-simulation manifest serialization failure",
                "cause": "seed-design serialization indexed (task, model) payload tuples as dictionaries",
                "scientific_data_status": "complete raw runs.csv and trajectories.csv.gz were persisted before the exception",
                "recovery": "counts, CRN, summary, compute diagnostics, and manifest reconstructed from persisted tables; no simulation rerun",
                "raw_runs_sha256": summary["raw_runs_sha256"], "raw_trajectories_sha256": summary["raw_trajectories_sha256"]}
    (output / "execution_failure.json").write_text(json.dumps(incident, indent=2, sort_keys=True) + "\n")
    manifest = {"artifact_type": "campaign3_fast_deep_meta_sequential", "status": "full development comparison",
                "base_histories": 420, "policy_runs": 1260, "policy_decision_rows": 45_360,
                "replicates_per_team_kernel_cell": 1,
                "fresh_seed_namespace": "campaign3_fast_deep_meta_v1/team/kernel/replicate/stream",
                "CRN": "same 12 generated problem values and 36 normal observation innovations for FAST/DEEP/META in each base history",
                "heldout_teams_or_kernels_used": False, "c32_c33_artifacts_modified": False,
                "selector_model_sha256": sha256(model_path),
                "seed_design": [{k: task[k] for k in ("history_id", "team_id", "kernel_id", "replicate", "problem_seed", "noise_seed")} for task in new_tasks()],
                "elapsed_wall_seconds": None, "elapsed_wall_time_note": "not recoverable after post-run manifest exception; summed decision computation time is retained in analysis summary",
                "runs_sha256": sha256(runs_path), "trajectories_sha256": sha256(traces_path),
                "analysis_summary_sha256": sha256(output / "analysis_summary.json"),
                "execution_failure_sha256": sha256(output / "execution_failure.json"),
                "recovered_without_simulation": True}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return {"manifest": manifest, "summary": summary}


def refresh_derived_summary() -> dict:
    """Recompute only derived summary/benchmark; never rerun or rewrite raw tables."""
    output = OUT / "sequential_full"
    runs = pd.read_csv(output / "runs.csv")
    traces = pd.read_csv(output / "trajectories.csv.gz")
    if len(runs) != 1260 or len(traces) != 45_360:
        raise RuntimeError("full raw tables failed counts; refusing derived refresh")
    summary = summarize(runs, traces)
    summary["cached_vs_uncached_benchmark"] = cached_cost_benchmark(
        json.loads((c33.OUT / "selector_model.json").read_text()), traces, count=60
    )
    summary["total_measured_decision_compute_seconds"] = {
        policy: float(value / 1e9) for policy, value in runs.groupby("policy").decision_compute_ns.sum().items()
    }
    summary["raw_runs_sha256"] = sha256(output / "runs.csv")
    summary["raw_trajectories_sha256"] = sha256(output / "trajectories.csv.gz")
    (output / "analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest_path = output / "execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["analysis_summary_sha256"] = sha256(output / "analysis_summary.json")
    manifest["raw_tables_unchanged_on_summary_refresh"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="run all 420 dev team x kernel cells, one fresh history/cell")
    parser.add_argument("--finalize-existing", action="store_true", help="recover summaries/manifests from complete persisted full tables; performs no simulations")
    parser.add_argument("--refresh-summary", action="store_true", help="refresh derived summaries from persisted outputs only; performs no simulations")
    parser.add_argument("--limit-cells", type=int, default=2, help="bounded diagnostic cells; safe default")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.finalize_existing:
        print(json.dumps(finalize_persisted_full(), sort_keys=True))
        return
    if args.refresh_summary:
        print(json.dumps(refresh_derived_summary(), sort_keys=True))
        return
    model_path = c33.OUT / "selector_model.json"
    if not model_path.is_file():
        parser.error("existing C3.3 fitted selector is required; it will not be refitted")
    tasks = new_tasks(replicates=1)
    count = len(tasks) if args.full else args.limit_cells
    if not 1 <= count <= len(tasks):
        parser.error("invalid --limit-cells")
    output = OUT / ("sequential_full" if args.full else f"diagnostic_{count}_cells")
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing output: {output}")
    model_spec = json.loads(model_path.read_text())
    payloads = [(task, model_spec) for task in tasks[:count]]
    started = time.perf_counter()
    if args.workers == 1:
        results = [simulate_history(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            results = list(pool.map(simulate_history, payloads, chunksize=1))
    elapsed = time.perf_counter() - started
    runs = pd.DataFrame([row for pair, _ in results for row in pair])
    traces = pd.DataFrame([row for _, rows in results for row in rows])
    expected_runs, expected_states = count * 3, count * 36 * 3
    if len(runs) != expected_runs or len(traces) != expected_states:
        raise RuntimeError("FAST/DEEP/META sequential count mismatch")
    if not runs.groupby("history_id").problem_stream_sha256.nunique().eq(1).all() or not runs.groupby("history_id").noise_stream_sha256.nunique().eq(1).all():
        raise RuntimeError("CRN streams diverged across policies")
    if (traces.loc[(traces.policy == "META") & traces.route.isin(("FAST_ACCEPT", "FAST_TERMINAL")), "deep_ns"] != 0).any():
        raise RuntimeError("META invoked DEEP on a FAST route")
    output.mkdir(parents=True)
    runs.to_csv(output / "runs.csv", index=False)
    traces.to_csv(output / "trajectories.csv.gz", index=False, compression="gzip")
    manifest = {"artifact_type": "campaign3_fast_deep_meta_sequential", "status": "full development comparison" if args.full else "bounded diagnostic only",
                "base_histories": count, "policy_runs": len(runs), "policy_decision_rows": len(traces),
                "replicates_per_team_kernel_cell": 1, "fresh_seed_namespace": "campaign3_fast_deep_meta_v1/team/kernel/replicate/stream",
                "CRN": "same 12 generated problem values and 36 normal observation innovations for FAST/DEEP/META in each base history",
                "heldout_teams_or_kernels_used": False, "c32_c33_artifacts_modified": False,
                "selector_model_sha256": sha256(model_path), "seed_design": [{k: task[k] for k in ("history_id", "team_id", "kernel_id", "replicate", "problem_seed", "noise_seed")} for task in tasks[:count]],
                "elapsed_wall_seconds": elapsed, "runs_sha256": sha256(output / "runs.csv"),
                "trajectories_sha256": sha256(output / "trajectories.csv.gz")}
    if args.full:
        summary = summarize(runs, traces)
        summary["elapsed_wall_seconds"] = elapsed
        summary["cached_vs_uncached_benchmark"] = cached_cost_benchmark(model_spec, traces)
        (output / "analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        manifest["analysis_summary_sha256"] = sha256(output / "analysis_summary.json")
    (output / "execution_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"manifest": manifest, "summary": summary if args.full else {}}, sort_keys=True))


if __name__ == "__main__":
    main()
