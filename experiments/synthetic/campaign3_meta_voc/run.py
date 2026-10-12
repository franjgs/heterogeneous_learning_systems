"""C3 META-VOC versus frequency-matched RANDOM sequential evaluation.

The existing C3.3 model is read-only. Default execution is a two-cell
diagnostic; ``--full`` runs one fresh matched history in each of 420 dev cells.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_c33 import c33  # noqa: E402
from experiments.synthetic.campaign3_fast_deep_meta.run import (  # noqa: E402
    choose_deep_action,
    choose_fast_action,
)
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.campaign3_problem_generator import generator_transition  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

OUT = ROOT / "results/campaigns/campaign3_meta_voc"
OPERATING_POINTS = (25, 50, 75)
RATES = {p: p / 100.0 for p in OPERATING_POINTS}
TARGET_CONTINUATION = "Q11"
CALIBRATION_PROTOCOL = "meta_voc_cost_calibration_v1"
SEQUENTIAL_NAMESPACE = "campaign3_meta_voc_sequential_v1"
RANDOM_NAMESPACE = "campaign3_meta_voc_random_priority_v1"
CALIBRATION_N_PER_REMAINING = 48
BOOTSTRAP_B = 2000
BOOTSTRAP_SEED = 20261014
N_CELLS = 420


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def feature_tie_key(vector: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(vector, dtype="<f8").tobytes()).hexdigest()


def ex_ante_score(state, belief, tau: int, model_spec: dict, extra_cost_seconds: dict) -> tuple[float, float, float]:
    """Return (VOC ratio, predicted benefit, predicted extra seconds)."""
    x = c33.feature_vector(state, belief, tau)
    predicted_benefit = float(c33.predict(model_spec, x.reshape(1, -1))[0])
    predicted_extra = float(extra_cost_seconds[(tau - 1) % 3 + 1])
    # Positive finite cost is required; the floor is numerical only, not a
    # benefit threshold or economics/materiality parameter.
    cost = max(predicted_extra, float(np.finfo(float).tiny))
    score = max(0.0, predicted_benefit) / cost
    if not np.isfinite(score):
        score = float(np.finfo(float).max)
    return score, predicted_benefit, cost


def threshold_route(score: float, key: str, threshold: dict) -> bool:
    cutoff = float(threshold["score_cutoff"])
    tie_cutoff = threshold["tie_key_cutoff"]
    return score > cutoff or (score == cutoff and key <= tie_cutoff)


def calibrate_thresholds(scores: list[tuple[float, str]], rates: dict[int, float] = RATES) -> dict:
    """Top-rank score thresholds from validation only; ties use ex-ante hash."""
    if not scores:
        raise ValueError("threshold calibration requires validation scores")
    ordered = sorted(scores, key=lambda pair: (-pair[0], pair[1]))
    result = {}
    for point, rate in rates.items():
        count = int(round(rate * len(ordered)))
        count = min(max(count, 1), len(ordered))
        cutoff_score, cutoff_key = ordered[count - 1]
        result[str(point)] = {"target_validation_invocations": count,
                              "validation_nonterminal_n": len(ordered),
                              "score_cutoff": cutoff_score, "tie_key_cutoff": cutoff_key,
                              "tie_rule": "score descending, SHA-256 of ex-ante feature vector ascending"}
    return result


def validation_cost_sample() -> tuple[list[dict], dict]:
    """Measure operator costs on a hash-fixed sample of validation states only."""
    val = c33._partition_frame("validation")
    # One row per selected factual state; labels themselves do not enter timing.
    state_rows = val[(val.continuation == TARGET_CONTINUATION) & (val.initial_mode == "Q00")]
    state_rows = state_rows.drop_duplicates("history_id")
    lookup = c33._state_lookup()
    candidates = []
    for row in state_rows.itertuples(index=False):
        state_record = lookup[str(row.history_id)]
        remaining = 4 - int(state_record["decision"])
        if remaining not in (2, 3):
            continue
        rank = hashlib.sha256(f"{CALIBRATION_PROTOCOL}|{row.history_id}".encode()).hexdigest()
        candidates.append((remaining, rank, str(row.history_id), state_record))
    chosen = []
    for remaining in (2, 3):
        subgroup = sorted((x for x in candidates if x[0] == remaining), key=lambda x: (x[1], x[2]))
        if len(subgroup) < CALIBRATION_N_PER_REMAINING:
            raise RuntimeError("validation cost calibration stratum too small")
        chosen.extend(subgroup[:CALIBRATION_N_PER_REMAINING])

    by_remaining: dict[int, list[float]] = {2: [], 3: []}
    rows = []
    hypotheses, _ = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    for index, (remaining, _, history_id, record) in enumerate(chosen):
        state = tuple(tuple(float(v) for v in r) for r in json.loads(record["state_before"]))
        belief = tuple(float(v) for v in json.loads(record["belief_before"]))
        # Alternate call order to reduce systematic timing-order effects.
        order = ("DEEP", "FAST") if index % 2 == 0 else ("FAST", "DEEP")
        elapsed = {}
        for op in order:
            started = time.perf_counter_ns()
            if op == "DEEP":
                choose_deep_action(state, belief, remaining)
            else:
                choose_fast_action(state, belief, remaining)
            elapsed[op] = time.perf_counter_ns() - started
        extra = (elapsed["DEEP"] - elapsed["FAST"]) / 1e9
        by_remaining[remaining].append(extra)
        rows.append({"history_id": history_id, "remaining": remaining,
                     "call_order": ">".join(order), "fast_ns": elapsed["FAST"],
                     "deep_ns": elapsed["DEEP"], "paired_extra_seconds": extra})
    estimates = {}
    for remaining, values in by_remaining.items():
        positive = [value for value in values if value > 0.0]
        median = float(np.median(values))
        if median <= 0.0:
            if not positive:
                raise RuntimeError("calibration did not measure positive incremental DEEP cost")
            median = float(np.median(positive))
        estimates[remaining] = median
    return rows, {str(k): v for k, v in estimates.items()}


def calibrate(model_spec: dict) -> tuple[dict, dict, list[dict]]:
    cost_rows, costs = validation_cost_sample()
    val = c33._partition_frame("validation")
    state_rows = val[(val.continuation == TARGET_CONTINUATION) & (val.initial_mode == "Q00")].drop_duplicates("history_id")
    lookup = c33._state_lookup()
    scores = []
    score_by_point = {point: [] for point in OPERATING_POINTS}
    for row in state_rows.itertuples(index=False):
        rec = lookup[str(row.history_id)]
        remaining = 4 - int(rec["decision"])
        if remaining == 1:
            continue
        state = tuple(tuple(float(v) for v in r) for r in json.loads(rec["state_before"]))
        belief = tuple(float(v) for v in json.loads(rec["belief_before"]))
        score, _, _ = ex_ante_score(state, belief, int(rec["tau"]), model_spec,
                                    {int(k): v for k, v in costs.items()})
        key = feature_tie_key(c33.feature_vector(state, belief, int(rec["tau"])))
        scores.append((score, key))
        for point in OPERATING_POINTS:
            score_by_point[point].append(score)
    thresholds = calibrate_thresholds(scores)
    validation_routes = {}
    for point in OPERATING_POINTS:
        cfg = thresholds[str(point)]
        validation_routes[str(point)] = sum(threshold_route(score, key, cfg) for score, key in scores)
    calibration = {"protocol": "META-VOC-CAL-v1", "threshold_source": "VALIDATION only",
                   "benefit_model": "frozen C3.3 Ridge predicting Q11-continuation raw Monte Carlo Q11-Q00 production advantage",
                   "cost_sample_source": "VALIDATION only, hash-ranked history IDs, 48 states at remaining=2 and 48 at remaining=3",
                   "cost_estimator": "median paired uncached DEEP minus FAST wall time by remaining decision count; operators called in alternating order",
                   "predicted_extra_cost_seconds_by_remaining": costs,
                   "cost_sample_rows": cost_rows,
                   "validation_nonterminal_states": len(scores),
                   "thresholds": thresholds, "validation_realized_invocation_counts": validation_routes,
                   "operating_targets": {str(k): RATES[k] for k in OPERATING_POINTS},
                   "C3.3_model_sha256": c33.sha256(c33.OUT / "selector_model.json"),
                   "C3.2_validation_sha256": c33.sha256(c33.C32 / "validation/raw_mc_targets.csv"),
                   "C3.2_train_sha256": c33.sha256(c33.C32 / "train/raw_mc_targets.csv")}
    return calibration, {int(k): float(v) for k, v in costs.items()}, scores


def tasks() -> list[dict]:
    teams, kernels = c33.team_kernel_maps()
    result = []
    for team in teams:
        matrix = tuple(tuple(float(team[f"s{i}{k}"]) for k in (1, 2)) for i in (1, 2, 3))
        for kernel in kernels:
            params = (float(kernel["alpha_stay"]), float(kernel["alpha_move"]),
                      float(kernel["alpha_return"]), None if kernel["sigma"] == "" else float(kernel["sigma"]))
            namespace = (SEQUENTIAL_NAMESPACE, team["team_id"], kernel["kernel_id"], 0)
            result.append({"history_id": ":".join(map(str, namespace)), "team_id": team["team_id"],
                           "kernel_id": kernel["kernel_id"], "replicate": 0, "team": matrix,
                           "kernel": params, "problem_seed": c33.stable_seed(*namespace, "problem"),
                           "noise_seed": c33.stable_seed(*namespace, "noise")})
    if len(result) != N_CELLS:
        raise RuntimeError("development team/kernel design mismatch")
    return result


def make_exogenous(task: dict) -> tuple[tuple[float, ...], tuple[float, ...]]:
    prng = np.random.default_rng(task["problem_seed"])
    nrng = np.random.default_rng(task["noise_seed"])
    problems = [float(prng.uniform(0.2, 0.8))]
    for _ in range(11):
        problems.append(generator_transition(problems, task["kernel"], prng).p_next)
    return tuple(problems), tuple(float(x) for x in nrng.standard_normal(36))


def simulate(task: dict, model_spec: dict, costs: dict[int, float], thresholds: dict,
             random_routes: dict[int, set[tuple[str, int]]] | None = None,
             policy_names: tuple[str, ...] = ("FAST", "DEEP", "META_VOC_25", "META_VOC_50", "META_VOC_75")) -> tuple[list[dict], list[dict]]:
    problems, eps = make_exogenous(task)
    hypotheses, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    run_rows, trace_rows = [], []
    for policy in policy_names:
        state, belief = task["team"], prior
        cumulative = 0.0
        total_ns = fast_ns_total = deep_ns_total = selector_ns_total = 0
        deep_count = accepted_fast = terminal_fast = 0
        for j, p in enumerate(problems):
            if j:
                belief = prior
            for step in range(3):
                remaining = 3 - step
                clock = 3 * j + step + 1
                tau = 36 - (clock - 1)
                before_state, before_belief = state, belief
                score = predicted_benefit = predicted_cost = ""
                selector_ns = fast_ns = deep_ns = 0
                if remaining == 1:
                    # Common terminal rule: no selector and no DEEP call for
                    # FAST, DEEP, RANDOM, or META-VOC.
                    route = "FAST_TERMINAL"
                    start = time.perf_counter_ns()
                    action, _ = choose_fast_action(state, belief, remaining)
                    fast_ns = time.perf_counter_ns() - start
                    if policy.startswith("META_VOC_"):
                        terminal_fast += 1
                elif policy == "FAST":
                    route = "FAST"
                    start = time.perf_counter_ns(); action, _ = choose_fast_action(state, belief, remaining)
                    fast_ns = time.perf_counter_ns() - start
                elif policy == "DEEP":
                    route = "DEEP"
                    start = time.perf_counter_ns(); action, _ = choose_deep_action(state, belief, remaining)
                    deep_ns = time.perf_counter_ns() - start
                    deep_count += 1
                elif policy.startswith("META_VOC_"):
                    point = int(policy.rsplit("_", 1)[1])
                    start = time.perf_counter_ns()
                    score, predicted_benefit, predicted_cost = ex_ante_score(state, belief, tau, model_spec, costs)
                    tie_key = feature_tie_key(c33.feature_vector(state, belief, tau))
                    selector_ns = time.perf_counter_ns() - start
                    invoke = threshold_route(float(score), tie_key, thresholds[str(point)])
                    if invoke:
                        route = "DEEP_INVOKE"
                        start = time.perf_counter_ns(); action, _ = choose_deep_action(state, belief, remaining)
                        deep_ns = time.perf_counter_ns() - start
                        deep_count += 1
                    else:
                        route = "FAST_ACCEPT"
                        start = time.perf_counter_ns(); action, _ = choose_fast_action(state, belief, remaining)
                        fast_ns = time.perf_counter_ns() - start
                        accepted_fast += 1
                else:
                    point = int(policy.rsplit("_", 1)[1])
                    invoke = (random_routes or {}).get(point, set())
                    if (task["history_id"], clock) in invoke:
                        route = "DEEP_RANDOM"
                        start = time.perf_counter_ns(); action, _ = choose_deep_action(state, belief, remaining)
                        deep_ns = time.perf_counter_ns() - start
                        deep_count += 1
                    else:
                        route = "FAST_RANDOM"
                        start = time.perf_counter_ns(); action, _ = choose_fast_action(state, belief, remaining)
                        fast_ns = time.perf_counter_ns() - start
                decision_ns = selector_ns + fast_ns + deep_ns
                total_ns += decision_ns; fast_ns_total += fast_ns; deep_ns_total += deep_ns
                selector_ns_total += selector_ns
                real = theory._real_decision(state, belief, action, (p, 1.0 - p), eps[clock - 1], hypotheses)
                cumulative += real.mu_true
                trace_rows.append({"history_id": task["history_id"], "team_id": task["team_id"],
                                   "kernel_id": task["kernel_id"], "policy": policy,
                                   "problem_index": j + 1, "decision": step + 1, "clock": clock,
                                   "remaining": remaining, "tau": tau, "route": route,
                                   "score": score, "predicted_benefit": predicted_benefit,
                                   "predicted_extra_cost_seconds": predicted_cost,
                                   "action_id": c33.ACTION_IDS[action], "mu_true": real.mu_true,
                                   "decision_compute_ns": decision_ns, "selector_ns": selector_ns,
                                   "fast_ns": fast_ns, "deep_ns": deep_ns,
                                   "state_before": packed(before_state), "belief_before": packed(before_belief),
                                   "state_after": packed(real.state_after), "belief_after": packed(real.belief_after)})
                state, belief = real.state_after, real.belief_after
        run_rows.append({"history_id": task["history_id"], "team_id": task["team_id"],
                         "kernel_id": task["kernel_id"], "replicate": task["replicate"],
                         "policy": policy, "cumulative_mu_true": cumulative, "decision_compute_ns": total_ns,
                         "selector_ns": selector_ns_total, "fast_ns": fast_ns_total, "deep_ns": deep_ns_total,
                         "deep_invocations_nonterminal": deep_count, "fast_acceptances_nonterminal": accepted_fast,
                         "terminal_fast_decisions": terminal_fast,
                         "problem_seed": task["problem_seed"], "noise_seed": task["noise_seed"],
                         "problem_stream_sha256": hashlib.sha256(packed(problems).encode()).hexdigest(),
                         "noise_stream_sha256": hashlib.sha256(packed(eps).encode()).hexdigest()})
    return run_rows, trace_rows


def make_random_routes(meta_counts: dict[int, int], task_list: list[dict]) -> tuple[dict[int, set[tuple[str, int]]], pd.DataFrame]:
    """Choose independent random clock slots; meta counts set only total K."""
    slots = []
    for task in task_list:
        for clock in range(1, 37):
            if (clock - 1) % 3 == 2:
                continue  # terminal step: always FAST in every policy
            rank_seed = c33.stable_seed(RANDOM_NAMESPACE, task["history_id"], clock, "priority")
            priority = float(rank_seed) / float(2**63 - 1)
            slots.append((priority, task["history_id"], clock))
    if len(slots) != len(task_list) * 24:
        raise RuntimeError("random schedule must cover exactly 24 nonterminal decisions/history")
    ordered = sorted(slots)
    routes: dict[int, set[tuple[str, int]]] = {}
    records = []
    for point, count in meta_counts.items():
        if count < 0 or count > len(ordered):
            raise ValueError("invalid retrospective invocation budget")
        selected = ordered[:count]
        routes[point] = {(history_id, clock) for _, history_id, clock in selected}
    # A single independent random priority order yields nested random baselines.
    for priority, history_id, clock in slots:
        records.append({"history_id": history_id, "clock": clock, "priority": priority,
                        **{f"invoke_random_{p}": (history_id, clock) in routes[p] for p in OPERATING_POINTS}})
    return routes, pd.DataFrame(records)


def bootstrap_mean(values: np.ndarray, rng: np.random.Generator) -> dict:
    draws = np.empty(BOOTSTRAP_B)
    for i in range(BOOTSTRAP_B):
        draws[i] = rng.choice(values, size=len(values), replace=True).mean()
    return {"mean": float(values.mean()), "median": float(np.median(values)),
            "ci95": [float(np.quantile(draws, .025)), float(np.quantile(draws, .975))],
            "q05": float(np.quantile(values, .05)), "q95": float(np.quantile(values, .95))}


def summarize(run_frame: pd.DataFrame, trace_frame: pd.DataFrame, matched_counts: dict[int, int]) -> dict:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    perf = run_frame.pivot(index="history_id", columns="policy", values="cumulative_mu_true")
    cost = run_frame.pivot(index="history_id", columns="policy", values="decision_compute_ns")
    voc_policies = [f"META_VOC_{p}" for p in OPERATING_POINTS]
    random_policies = [f"RANDOM_{p}" for p in OPERATING_POINTS]
    differences = {}
    pairs = [(f"META_VOC_{p}", f"RANDOM_{p}") for p in OPERATING_POINTS]
    pairs += [(f"META_VOC_{p}", baseline) for p in OPERATING_POINTS for baseline in ("FAST", "DEEP")]
    for a, b in pairs:
        differences[f"performance_{a}-{b}"] = bootstrap_mean((perf[a] - perf[b]).to_numpy(), rng)
        differences[f"compute_ns_{a}-{b}"] = bootstrap_mean((cost[a] - cost[b]).to_numpy(dtype=float), rng)
    policy_stats = {}
    for policy, group in run_frame.groupby("policy"):
        t = trace_frame[trace_frame.policy == policy]
        decisions = len(t)
        nonterminal = int((t.remaining > 1).sum())
        invocations = int(t.route.isin(("DEEP", "DEEP_INVOKE", "DEEP_RANDOM")).sum())
        policy_stats[policy] = {
            "histories": int(group.history_id.nunique()),
            "mean_cumulative_mu_true": float(group.cumulative_mu_true.mean()),
            "sd_cumulative_mu_true": float(group.cumulative_mu_true.std()),
            "total_decision_compute_seconds": float(group.decision_compute_ns.sum() / 1e9),
            "mean_compute_seconds_per_history": float(group.decision_compute_ns.mean() / 1e9),
            "latency_ms": {"mean": float(t.decision_compute_ns.mean() / 1e6),
                           "median": float(t.decision_compute_ns.median() / 1e6),
                           "q90": float(t.decision_compute_ns.quantile(.9) / 1e6),
                           "q95": float(t.decision_compute_ns.quantile(.95) / 1e6)},
            "selector_inference_total_seconds": float(group.selector_ns.sum() / 1e9),
            "nonterminal_deep_invocations": invocations,
            "nonterminal_deep_fraction": invocations / nonterminal if nonterminal else 0.0,
        }
    actual_counts = {p: int(run_frame.loc[run_frame.policy == f"META_VOC_{p}", "deep_invocations_nonterminal"].sum()) for p in OPERATING_POINTS}
    random_counts = {p: int(run_frame.loc[run_frame.policy == f"RANDOM_{p}", "deep_invocations_nonterminal"].sum()) for p in OPERATING_POINTS}
    return {"base_histories": int(run_frame.history_id.nunique()), "policy_runs": len(run_frame),
            "trajectory_rows": len(trace_frame), "policies": policy_stats,
            "meta_voc_actual_invocation_counts": actual_counts,
            "random_actual_invocation_counts": random_counts,
            "frequency_match_exact": actual_counts == random_counts == matched_counts,
            "paired_differences": differences,
            "bootstrap": {"unit": "complete matched base history", "replicates": BOOTSTRAP_B,
                          "seed": BOOTSTRAP_SEED, "interval": "two-sided percentile 95%"}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="run 420 cells, one fresh history per dev team x kernel")
    parser.add_argument("--limit-cells", type=int, default=2, help="diagnostic-only prefix; safe default")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    model_path = c33.OUT / "selector_model.json"
    if not model_path.is_file():
        parser.error("existing frozen C3.3 Ridge model missing; do not retrain here")
    model_spec = json.loads(model_path.read_text())
    calibration, costs, val_scores = calibrate(model_spec)
    task_list = tasks()
    count = len(task_list) if args.full else args.limit_cells
    if not 1 <= count <= len(task_list):
        parser.error("invalid --limit-cells")
    task_list = task_list[:count]
    output = OUT / ("sequential_full" if args.full else f"diagnostic_{count}_cells")
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing output {output}")
    output.mkdir(parents=True)
    (output / "calibration.json").write_text(json.dumps(calibration, indent=2, sort_keys=True) + "\n")
    start_manifest = {"artifact_type": "campaign3_meta_voc_sequential", "status": "running phase 1",
                      "model_sha256": sha256(model_path), "calibration_sha256": sha256(output / "calibration.json"),
                      "base_history_count": count, "full_design_base_histories": 420,
                      "seed_namespace": SEQUENTIAL_NAMESPACE, "heldout_used": False}
    (output / "execution_manifest.json").write_text(json.dumps(start_manifest, indent=2, sort_keys=True) + "\n")
    payloads = [(task, model_spec, costs, calibration["thresholds"], None,
                 ("FAST", "DEEP", "META_VOC_25", "META_VOC_50", "META_VOC_75")) for task in task_list]
    started = time.perf_counter()
    if args.workers == 1:
        first_phase = [simulate(*payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            first_phase = list(pool.map(_simulate_payload, payloads, chunksize=1))
    phase1_runs = pd.DataFrame([row for pair, _ in first_phase for row in pair])
    phase1_traces = pd.DataFrame([row for _, records in first_phase for row in records])
    phase1_runs.to_csv(output / "phase1_runs.csv", index=False)
    phase1_traces.to_csv(output / "phase1_trajectories.csv.gz", index=False, compression="gzip")
    meta_counts = {p: int(phase1_runs.loc[phase1_runs.policy == f"META_VOC_{p}", "deep_invocations_nonterminal"].sum()) for p in OPERATING_POINTS}
    random_routes, random_schedule = make_random_routes(meta_counts, task_list)
    random_schedule.to_csv(output / "random_invocation_schedule.csv", index=False)
    random_payloads = [(task, model_spec, costs, calibration["thresholds"], random_routes,
                        tuple(f"RANDOM_{p}" for p in OPERATING_POINTS)) for task in task_list]
    if args.workers == 1:
        second_phase = [simulate(*payload) for payload in random_payloads]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            second_phase = list(pool.map(_simulate_payload, random_payloads, chunksize=1))
    random_runs = pd.DataFrame([row for pair, _ in second_phase for row in pair])
    random_traces = pd.DataFrame([row for _, records in second_phase for row in records])
    random_runs.to_csv(output / "phase2_random_runs.csv", index=False)
    random_traces.to_csv(output / "phase2_random_trajectories.csv.gz", index=False, compression="gzip")
    run_frame = pd.concat([phase1_runs, random_runs], ignore_index=True).sort_values(["history_id", "policy"]).reset_index(drop=True)
    trace_frame = pd.concat([phase1_traces, random_traces], ignore_index=True).sort_values(["history_id", "policy", "clock"]).reset_index(drop=True)
    expected_runs, expected_traces = count * 8, count * 8 * 36
    if len(run_frame) != expected_runs or len(trace_frame) != expected_traces:
        raise RuntimeError("META-VOC factorial output count mismatch")
    if not run_frame.groupby("history_id").problem_stream_sha256.nunique().eq(1).all() or not run_frame.groupby("history_id").noise_stream_sha256.nunique().eq(1).all():
        raise RuntimeError("CRN alignment failed")
    for point in OPERATING_POINTS:
        meta_n = int(run_frame.loc[run_frame.policy == f"META_VOC_{point}", "deep_invocations_nonterminal"].sum())
        rand_n = int(run_frame.loc[run_frame.policy == f"RANDOM_{point}", "deep_invocations_nonterminal"].sum())
        if meta_n != rand_n or rand_n != meta_counts[point]:
            raise RuntimeError("RANDOM frequency failed exact META-VOC matching")
        if rand_n != meta_counts[point]:
            raise RuntimeError("RANDOM budget count mismatch")
    summary = summarize(run_frame, trace_frame, meta_counts)
    summary["nominal_operating_points"] = {str(p): RATES[p] for p in OPERATING_POINTS}
    summary["random_matching"] = "K is the final META-VOC DEEP invocation count for that point; independent hash-derived random priorities select exactly K of all 24 nonterminal clock slots/history. K affects only random budget, never selected locations; schedule frozen before RANDOM trajectories execute."
    summary["elapsed_wall_seconds"] = time.perf_counter() - started
    run_frame.to_csv(output / "runs.csv", index=False)
    trace_frame.to_csv(output / "trajectories.csv.gz", index=False, compression="gzip")
    (output / "analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    manifest = {"artifact_type": "campaign3_meta_voc_sequential", "status": "complete" if args.full else "bounded diagnostic only",
                "base_histories": count, "policy_runs": len(run_frame), "trajectory_rows": len(trace_frame),
                "teams": sorted(run_frame.team_id.unique().tolist()), "kernels": sorted(run_frame.kernel_id.unique().tolist()),
                "policies": ["FAST", "DEEP", "RANDOM-25", "RANDOM-50", "RANDOM-75", "META-VOC-25", "META-VOC-50", "META-VOC-75"],
                "replicates_per_team_kernel_cell": 1, "seed_namespace": SEQUENTIAL_NAMESPACE,
                "random_namespace": RANDOM_NAMESPACE, "random_exact_matched_counts": meta_counts,
                "model_sha256": sha256(model_path), "calibration_sha256": sha256(output / "calibration.json"),
                "runs_sha256": sha256(output / "runs.csv"), "trajectories_sha256": sha256(output / "trajectories.csv.gz"),
                "random_schedule_sha256": sha256(output / "random_invocation_schedule.csv"),
                "analysis_summary_sha256": sha256(output / "analysis_summary.json"),
                "heldout_used": False, "previous_campaign_artifacts_modified": False,
                "elapsed_wall_seconds": summary["elapsed_wall_seconds"]}
    (output / "execution_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"manifest": manifest, "summary": summary}, sort_keys=True))


def _simulate_payload(payload):
    return simulate(*payload)


if __name__ == "__main__":
    main()
