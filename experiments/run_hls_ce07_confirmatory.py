"""Run the pre-authorized 60-replica CE-07 confirmatory comparison."""
from __future__ import annotations

import gzip
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy
import simpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hls import ce04
from hls.ce07_pilot import (agent_permutation, canonical_sha256,
                            matched_potential_digest, run_ce07_replica)
from hls.ce07_structure import competence_matrices, rename_agent_rows, validate_structures

OUT = ROOT / "results/experiments/hls_ce07_confirmatory"
SEEDS = tuple(range(30100, 30130))
FROZEN_CONFIG_SHA256 = "b5ab97c31e937e590ded4c99e861345c60dfd18d850edb8788c283752f6c2907"


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def task_digest(tasks) -> str:
    return canonical_sha256([t.__dict__ for t in tasks])


def generate_ce07_stationary_workload(seed: int, n_agents: int = 12, horizon: float = 400.0):
    """Reuse CE-04's keyed Poisson stream but mark every arrival uniformly across families."""
    rng = np.random.default_rng(ce04._seed(seed, n_agents, 2))
    tasks = []
    t = 0.0
    rate = ce04.ARRIVAL_RATE_PER_AGENT * n_agents
    family_probabilities = (0.25, 0.25, 0.25, 0.25)
    while True:
        t += float(rng.exponential(1.0 / rate))
        if t >= horizon:
            break
        # phase is metadata for temporal summaries only; it does not change
        # the stationary family-mark distribution.
        phase = 0 if t < 150.0 else 1 if t < 300.0 else 2
        family = int(rng.choice(4, p=family_probabilities))
        task_id = len(tasks)
        tasks.append(ce04.Task(task_id, t, family, phase, t + ce04.DEADLINE_SLACK))
    return tuple(tasks)


def gini(values) -> float:
    x = np.asarray(values, dtype=float)
    if x.size == 0 or np.all(x == 0):
        return 0.0
    if np.any(x < 0):
        raise ValueError("Gini requires nonnegative values")
    x = np.sort(x)
    n = x.size
    return float((2 * np.dot(np.arange(1, n + 1), x) / (n * x.sum())) - (n + 1) / n)


def tie_priority(seed: int) -> np.ndarray:
    rank = np.arange(12)
    np.random.default_rng(ce04._seed(seed, 12, 5)).shuffle(rank)
    return rank


def summarize(seed, org, result, audit, permutation, task_rows):
    records = result["records"]
    admitted = [r for r in records if r["selected_agent"] is not None]
    q_matrix = rename_agent_rows(competence_matrices()[0 if org == "A" else 1], permutation)
    selected_q = [float(q_matrix[r["selected_agent"], r["family"]]) for r in admitted]
    waits = [float(r["service_start"] - r["arrival"]) for r in admitted]
    assignments = result["assignment_counts"]
    util = np.asarray(result["agent_utilization"], dtype=float)
    family = []
    for k in range(4):
        rs = [r for r in records if r["family"] == k]
        adm_k = [r for r in rs if r["selected_agent"] is not None]
        suc = sum(bool(r["correct"] and r["on_time"]) for r in rs)
        family.append({"family": k, "arrivals": len(rs), "admitted": len(adm_k),
            "rejected": len(rs) - len(adm_k), "successes_on_time": suc,
            "success_on_time_rate": suc / len(rs) if rs else None,
            "incorrect_completed": sum(r["correct"] is False for r in rs),
            "late_completed": sum(r["completion"] is not None and r["completion"] > r["deadline"] for r in rs),
            "selected_competence_mean": float(np.mean([q_matrix[r["selected_agent"], k] for r in adm_k])) if adm_k else None})
    phases = []
    for phase in range(3):
        rs = [r for r in records if r["phase"] == phase]
        phases.append({"phase": phase, "arrivals": len(rs),
            "success_on_time": sum(bool(r["correct"] and r["on_time"]) for r in rs),
            "success_on_time_rate": (sum(bool(r["correct"] and r["on_time"]) for r in rs) / len(rs)) if rs else None})
    ties = audit["tie_events"]
    tie_rows = [t for t in ties if len(t["exact_tie_candidates"]) > 1]
    priority = tie_priority(seed)
    tie_types = {"all_low_q_0.6": 0, "all_high_q_0.9": 0, "mixed_q": 0}
    exact_tie_trace = []
    admitted_iter = iter(admitted)
    for t in ties:
        rec = next(admitted_iter)
        candidates = t["exact_tie_candidates"]
        if len(candidates) <= 1:
            continue
        qvals = [float(q_matrix[i, rec["family"]]) for i in candidates]
        kind = "all_high_q_0.9" if all(q == .9 for q in qvals) else (
            "all_low_q_0.6" if all(q == .6 for q in qvals) else "mixed_q")
        tie_types[kind] += 1
        selected = int(t["selected_agent_slot"])
        implied_f = float(t["best_score"]) / qvals[0]
        exact_tie_trace.append({"seed": seed, "organization": org,
            "task_id": int(rec["task_id"]), "family": int(rec["family"]),
            "candidate_slots": [int(i) for i in candidates],
            "candidate_profile_ids": [int(permutation[i]) for i in candidates],
            "candidate_q_current_family": qvals,
            "candidate_priority_ranks": [int(priority[i]) for i in candidates],
            "best_score": float(t["best_score"]),
            "implied_F_i": implied_f,
            "selected_slot": selected,
            "selected_profile_id": int(permutation[selected]),
            "selected_priority_rank": int(priority[selected]),
            "selected_is_minimum_rank": selected == min(candidates, key=lambda i: int(priority[i]))})
    return ({"seed": seed, "organization": org, "n_agents": 12, "n_functions": 4,
        "policy": "P1", "arrivals": result["n_arrivals"], "admitted": result["n_admitted"],
        "rejected": result["n_rejected"], "successes_on_time": result["n_success_on_time"],
        "success_on_time_rate": result["success_on_time_rate"],
        "incorrect_completed": result["n_incorrect"], "late_completed": result["n_late"],
        "selected_competence_mean": float(np.mean(selected_q)),
        "selected_competence_gap_to_h": .9 - float(np.mean(selected_q)),
        "utilization_mean": float(util.mean()), "utilization_sd_agents": float(util.std(ddof=1)),
        "utilization_p95_agents": float(np.quantile(util, .95)),
        "assignment_gini": gini(assignments), "assignment_counts": assignments,
        "wait_mean_admitted": float(np.mean(waits)) if waits else None,
        "wait_p95_admitted": float(np.quantile(waits, .95)) if waits else None,
        "latency_mean_completed": result["latency_mean"], "latency_p95_completed": result["latency_p95"],
        "exact_ties": len(tie_rows), "tie_decisions": len(ties),
        "tie_candidate_types": tie_types,
        "permutation_new_slot_to_profile_id": list(permutation),
        "permutation_seed_sequence": [seed, 12, 707],
        "demand_sha256": task_digest(task_rows),
        "record_sha256": canonical_sha256(records),
        "wall_seconds": result["wall_seconds"], "cpu_seconds": result["cpu_seconds"],
        "decision_seconds": result["decision_seconds"],
        "decision_cpu_seconds": result["decision_cpu_seconds"],
        "peak_rss": result["peak_rss"], "peak_rss_unit": result["peak_rss_unit"],
        "by_family": family, "by_phase": phases}, exact_tie_trace)


def main():
    if SEEDS != tuple(range(30100, 30130)) or len(set(SEEDS)) != 30:
        raise AssertionError("confirmatory seed registry changed")
    base_a, base_b = competence_matrices()
    structure_check = validate_structures(base_a, base_b)
    # Exact equality of rational marginals and maxima is part of the pre-run gate.
    if structure_check["marginal_exact"] != "27/40" or structure_check["maxima"] != [.9] * 4:
        raise AssertionError("structure invariant failed")
    permutations = {seed: agent_permutation(seed, 12) for seed in SEEDS}
    if len(set(permutations.values())) != len(SEEDS):
        raise AssertionError("identifier permutations did not vary across all 30 seeds")
    common = {"N": 12, "K": 4, "h": .9, "l": .6, "marginal_exact": "27/40",
        "organization_A": "3 all-high; 9 all-low", "organization_B": "3 specialists per family",
        "horizon": 400, "arrival_rate_per_agent": .55, "family_probabilities": [.25] * 4,
        "demand_stationary": True,
        "demand_generator": "CE-04 keyed Poisson arrivals; iid uniform task-family marks in every time segment; phase is metadata only",
        "service": {"distribution": "CE-04 lognormal", "mean": 1.25, "CV": .30},
        "deadline_slack": 3.0, "queue": "one FCFS queue; one active task per agent",
        "policy": "unchanged CE-04 P1; q_ik * F_i", "learning": False, "cooperation": False,
        "seeds": list(SEEDS), "organizations": ["A", "B"], "simulations": 60,
        "permutation_stream": [12, 707], "same_permutation_A_B_per_seed": True,
        "permutation_must_vary_each_seed": True}
    config_hash = canonical_sha256(common)
    OUT.mkdir(parents=True, exist_ok=True)
    if config_hash != FROZEN_CONFIG_SHA256:
        raise AssertionError("scientific configuration differs from the pre-registered hash")
    config_path = OUT / "configuration.json"
    frozen_payload = {**common, "scientific_config_sha256": config_hash}
    if not config_path.exists() or json.loads(config_path.read_text()) != frozen_payload:
        raise AssertionError("frozen configuration artifact missing or does not match")
    summaries, pairs, tie_trace = [], [], []
    campaign_started = time.perf_counter()
    campaign_cpu_started = time.process_time()
    for idx, seed in enumerate(SEEDS, 1):
        permutation = permutations[seed]
        tasks = generate_ce07_stationary_workload(seed, 12, horizon=400.0)
        demand_hash = task_digest(tasks)
        qa = rename_agent_rows(base_a, permutation)
        qb = rename_agent_rows(base_b, permutation)
        potential_hash = matched_potential_digest(seed, tasks, qa, qb)
        org_results = {}
        for org in ("A", "B"):
            result, audit, used_perm = run_ce07_replica(seed, org, tasks)
            if tuple(used_perm) != tuple(permutation):
                raise AssertionError(f"permutation mismatch for seed={seed}, org={org}")
            if result["n_arrivals"] != len(tasks) or result["n_arrivals"] != result["n_admitted"] + result["n_rejected"]:
                raise AssertionError(f"task conservation failed for seed={seed}, org={org}")
            if result["config"]["policy"] != "P1" or result["config"]["n_agents"] != 12:
                raise AssertionError("scientific configuration drift")
            if any(r["selected_agent"] is not None and r["correct"] is None for r in result["records"]):
                raise AssertionError("admitted task lacks final outcome")
            summary, ties = summarize(seed, org, result, audit, permutation, tasks)
            if summary["demand_sha256"] != demand_hash:
                raise AssertionError("demand digest mismatch")
            if any(not t["selected_is_minimum_rank"] for t in ties):
                raise AssertionError("tie winner differs from unchanged CE-04 rank rule")
            summary["matched_potential_sha256"] = potential_hash
            summaries.append(summary)
            tie_trace.extend(ties)
            org_results[org] = result
        a, b = org_results["A"], org_results["B"]
        task_a = [(x["task_id"], x["arrival"], x["family"], x["deadline"]) for x in a["records"]]
        task_b = [(x["task_id"], x["arrival"], x["family"], x["deadline"]) for x in b["records"]]
        if task_a != task_b:
            raise AssertionError(f"A/B demand mismatch at seed={seed}")
        pairs.append({"seed": seed, "same_permutation": True, "same_demand": True,
            "same_service_and_common_correctness_potential_table": True,
            "demand_sha256": demand_hash, "matched_potential_sha256": potential_hash,
            "A_arrivals": a["n_arrivals"], "B_arrivals": b["n_arrivals"],
            "A_admitted": a["n_admitted"], "B_admitted": b["n_admitted"],
            "delta_B_minus_A": b["success_on_time_rate"] - a["success_on_time_rate"]})
        print(f"completed seed pair {idx}/30: {seed}", flush=True)
    elapsed_wall = time.perf_counter() - campaign_started
    elapsed_cpu = time.process_time() - campaign_cpu_started
    if len(summaries) != 60 or len(pairs) != 30 or len({x["seed"] for x in pairs}) != 30:
        raise AssertionError("campaign registry incomplete or contaminated")
    delta = [x["delta_B_minus_A"] for x in pairs]
    # Seed-level bootstrap; task records are never treated as independent units.
    rng = np.random.default_rng(np.random.SeedSequence([30100, 30129, 707, 95]))
    d = np.asarray(delta, dtype=float)
    boot = np.mean(rng.choice(d, size=(10000, len(d)), replace=True), axis=1)
    from scipy import stats
    ttest = stats.ttest_1samp(d, 0.0, alternative="two-sided")
    tost_lower = stats.ttest_1samp(d, -0.02, alternative="greater")
    tost_upper = stats.ttest_1samp(d, 0.02, alternative="less")
    summary_stats = {"unit": "matched seed pair", "n_pairs": 30,
        "mean_delta_B_minus_A_pp": float(d.mean() * 100),
        "sd_delta_pp": float(d.std(ddof=1) * 100),
        "median_delta_pp": float(np.median(d) * 100),
        "bootstrap_percentile_95_ci_pp": [float(np.quantile(boot, .025) * 100), float(np.quantile(boot, .975) * 100)],
        "two_sided_one_sample_t_test": {"t": float(ttest.statistic), "df": 29, "p": float(ttest.pvalue)},
        "tost_margin_pp": 2.0,
        "tost_lower_test_mean_gt_minus_margin_p": float(tost_lower.pvalue),
        "tost_upper_test_mean_lt_plus_margin_p": float(tost_upper.pvalue),
        "tost_p_value": float(max(tost_lower.pvalue, tost_upper.pvalue)),
        "equivalent_within_margin_alpha_0_05": bool(tost_lower.pvalue < .05 and tost_upper.pvalue < .05),
        "positive_seed_differences": int(np.sum(d > 0)), "negative_seed_differences": int(np.sum(d < 0)),
        "zero_seed_differences": int(np.sum(d == 0)), "seed_differences_pp": [float(x * 100) for x in d]}
    OUT.joinpath("replica_results.json").write_text(json.dumps(summaries, indent=2, sort_keys=True, allow_nan=False) + "\n")
    OUT.joinpath("paired_validation.json").write_text(json.dumps({"all_60_validated": True,
        "simulations": 60, "pairs": pairs, "structure_validation": structure_check,
        "unique_permutations": len(set(permutations.values())),
        "permutations_vary_across_seeds": True}, indent=2, sort_keys=True, allow_nan=False) + "\n")
    tie_path = OUT / "exact_tie_decisions.json.gz"
    with tie_path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as gz:
            gz.write((json.dumps(tie_trace, indent=2, sort_keys=True, allow_nan=False) + "\n").encode())
    OUT.joinpath("confirmatory_analysis.json").write_text(json.dumps(summary_stats, indent=2, sort_keys=True, allow_nan=False) + "\n")
    outputs = [OUT / x for x in ("configuration.json", "replica_results.json", "paired_validation.json", "exact_tie_decisions.json.gz", "confirmatory_analysis.json")]
    source_files = ["src/hls/ce04.py", "src/hls/ce07_structure.py", "src/hls/ce07_pilot.py", "experiments/run_hls_ce07_confirmatory.py"]
    manifest = {"study": "HLS-CE-07.5 confirmatory campaign", "base_commit": "6be35daa0ad9db25104ff739706eeba86bf7dcf5",
        "execution_head_before_campaign": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "configuration_sha256": config_hash, "source_sha256": {x: sha_bytes((ROOT / x).read_bytes()) for x in source_files},
        "ce04_source_unchanged": True, "environment": {"python": sys.version, "platform": platform.platform(),
            "numpy": np.__version__, "scipy": scipy.__version__, "simpy": simpy.__version__},
        "replicas": 60, "seed_pairs": 30, "unique_permutations": len(set(permutations.values())),
        "campaign_wall_seconds": elapsed_wall, "campaign_process_cpu_seconds": elapsed_cpu,
        "process_peak_rss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_rss_unit": "platform-native resource.getrusage ru_maxrss",
        "tie_records": len(tie_trace), "artifact_sha256": {x.name: sha_bytes(x.read_bytes()) for x in outputs},
        "status": "60/60 validated; confirmatory analysis completed"}
    OUT.joinpath("manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"replicas": 60, "config_sha256": config_hash,
        "tie_records": len(tie_trace), "analysis": summary_stats,
        "wall_seconds": elapsed_wall, "cpu_seconds": elapsed_cpu}, indent=2), flush=True)


if __name__ == "__main__":
    main()
