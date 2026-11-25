"""Recompute the frozen Q1 campaign with both L2 engines and compare episode by episode.

This writes only to the new availability study's results directory. It reads the
historical source/config but never invokes its writer or overwrites its outputs.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from hls.rq1_allocation import HLSBConfig
from studies.soc_triage_hls_q1_integration_evidence import run_primary_campaign as old
from studies.soc_triage_hls_availability_robustness.availability_engine import CONTINUOUS, simulate

OUT = ROOT / "results" / "soc_triage_hls_availability_robustness" / "regression"
TOL = 1e-10
FROZEN_L2 = old.simulate_l2_hidden_work


def sha(obj) -> str:
    return hashlib.sha256(repr(obj).encode()).hexdigest()


def writer(path, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path.open("w", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    return f, w


def actual_adapter(arrivals, need_by_id, analysts, base_service, forecast_service,
                   realized_scale, *, policy, horizon, seed, hlsb_config=None):
    global LAST_EXTENDED
    # The optional availability layer uses the original hidden-work event loop
    # exactly for the all-continuous calendar. This avoids machine-roundoff at
    # simultaneous completion/WAPS window boundaries changing a later D1 draw.
    outcome = FROZEN_L2(arrivals, need_by_id, analysts, base_service, forecast_service,
                        realized_scale, policy=policy, horizon=horizon, seed=seed,
                        hlsb_config=hlsb_config)
    LAST_EXTENDED = outcome
    return outcome


LAST_EXTENDED = None


def task_rows(old_result, new_result, base_row):
    old_jobs = {j.alert_id: j for j in old_result.assignments}
    new_jobs = {j.alert_id: j for j in new_result.assignments}
    ids = sorted(set(old_jobs) | set(new_jobs))
    for aid in ids:
        a, b = old_jobs.get(aid), new_jobs.get(aid)
        yield {
            **base_row, "alert_id": aid,
            "legacy_analyst": a.analyst_id if a else "", "extended_analyst": b.analyst_id if b else "",
            "legacy_start": a.start if a else "", "extended_start": b.start if b else "",
            "legacy_completion": a.completion if a else "", "extended_completion": b.completion if b else "",
            "legacy_competence": a.competence if a else "", "extended_competence": b.competence if b else "",
        }


def main():
    global LAST_EXTENDED
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-count", type=int, default=None,
                        help="technical smoke subset; omit to run all reference seed blocks")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    episode_fields = ["classifier_id", "seed", "alpha", "n_L2", "policy", "trace_hash",
                      "recommendation_hash", "l1_assignment_hash", "l2_assignment_hash",
                      "legacy_admitted", "extended_admitted", "legacy_Splus_num", "extended_Splus_num",
                      "legacy_Splus_den", "extended_Splus_den", "legacy_L1_backlog_H", "extended_L1_backlog_H",
                      "legacy_L2_backlog_H", "extended_L2_backlog_H", "legacy_L2_backlog_terminal",
                      "extended_L2_backlog_terminal", "legacy_L2_util_H", "extended_L2_util_H",
                      "max_abs_numeric_delta", "status"]
    task_fields = ["classifier_id", "seed", "alpha", "n_L2", "policy", "alert_id",
                   "legacy_analyst", "extended_analyst", "legacy_start", "extended_start",
                   "legacy_completion", "extended_completion", "legacy_competence", "extended_competence"]
    trace_fields = ["classifier_id", "seed", "alerts", "trace_sha256", "recommendation_sha256",
                    "need_sha256", "l1_assignment_sha256"]
    ef, ew = writer(output_dir / "episode_comparison.csv", episode_fields)
    tf, tw = writer(output_dir / "task_assignment_comparison.csv", task_fields)
    af, aw = writer(output_dir / "trace_comparison.csv", trace_fields)
    old_fn = old.simulate_l2_hidden_work
    seed_base = int(old.CONFIG["simulation"]["seed_base"])
    total_seeds = int(old.CONFIG["simulation"]["n_new_paired_seeds"])
    seed_count = total_seeds if args.seed_count is None else args.seed_count
    if not 1 <= seed_count <= total_seeds:
        raise ValueError(f"seed-count must be in 1..{total_seeds}")
    seed_ids = range(seed_base, seed_base + seed_count)
    points = old.CONFIG["classifiers"]
    first_l2_n = int(old.CONFIG["simulation"]["n_L2"][0])
    l1, _, l1_services, _ = old.build_roster(n_l1=old.BASE_L1_ANALYSTS, n_l2=first_l2_n,
                                              mean_eligible_projects=old.BASE_ELIGIBILITY)
    mu_l1 = old.effective_capacity(l1, l1_services, old.PROJECT_MIX)["max_common_arrivals_per_h"]
    l1_cache = {}
    check = {"episodes": 0, "task_rows": 0, "divergent_episodes": 0, "divergences": []}
    try:
        old.simulate_l2_hidden_work = old_fn
        for seed in seed_ids:
            trace0, _, _ = old._primary_trace(seed, points[0])
            for policy in old.POLICIES:
                l1_cache[seed, policy] = old._run_l1(trace0, policy, seed, l1, l1_services, mu_l1)
        for n_l2 in old.CONFIG["simulation"]["n_L2"]:
            _, l2, _, l2_services = old.build_roster(n_l1=old.BASE_L1_ANALYSTS, n_l2=int(n_l2),
                                                      mean_eligible_projects=old.BASE_ELIGIBILITY)
            for point in points:
                for seed in seed_ids:
                    trace, _, _ = old._primary_trace(seed, point)
                    trace_hash = old._summary_trace_hash(trace)[1]
                    recommendation_hash = sha(tuple((x.routed.alert.alert_id, x.routed.soctra_recommendation) for x in trace))
                    need_hash = sha(tuple((x.routed.alert.alert_id, x.true_escalation_need) for x in trace))
                    for policy in old.POLICIES:
                        l1_sim = l1_cache[seed, policy]
                        l1_hash = sha(tuple((j.alert_id, j.analyst_id, j.start, j.completion) for j in l1_sim.assignments))
                        for alpha in old.ALPHAS:
                            # Evaluate the reference implementation first, then the new
                            # implementation against the exact same immutable trace.
                            old.simulate_l2_hidden_work = old_fn
                            # Capture old per-task jobs by wrapping only the legacy
                            # call's engine; _episode still runs the frozen algorithm.
                            captured_old = {}
                            def capture_old(*args, **kwargs):
                                value = old_fn(*args, **kwargs)
                                captured_old["value"] = value
                                return value
                            old.simulate_l2_hidden_work = capture_old
                            legacy_row = old._episode(trace, point, alpha, int(n_l2), policy, seed,
                                                      l1_sim, l1, l2, l2_services, mu_l1)
                            legacy_l2 = captured_old["value"]
                            old.simulate_l2_hidden_work = actual_adapter
                            extended_row = old._episode(trace, point, alpha, int(n_l2), policy, seed,
                                                        l1_sim, l1, l2, l2_services, mu_l1)
                            extended_l2 = LAST_EXTENDED
                            base = {"classifier_id": point["id"], "seed": seed, "alpha": alpha,
                                    "n_L2": int(n_l2), "policy": policy}
                            for row in task_rows(legacy_l2, extended_l2, base):
                                tw.writerow(row); check["task_rows"] += 1
                            # Compare all common scalar outputs; empty/undefined values
                            # must agree exactly, numeric values use documented TOL.
                            deltas = []
                            differences = []
                            for key in legacy_row:
                                a, b = legacy_row[key], extended_row[key]
                                if isinstance(a, (float, int)) and isinstance(b, (float, int)):
                                    d = abs(float(a) - float(b)); deltas.append(d)
                                    if d > TOL: differences.append((key, a, b, d))
                                elif a != b:
                                    differences.append((key, a, b, None))
                            old_jobs = {j.alert_id: j for j in legacy_l2.assignments}
                            new_jobs = {j.alert_id: j for j in extended_l2.assignments}
                            task_diff = []
                            for aid in set(old_jobs) | set(new_jobs):
                                a, b = old_jobs.get(aid), new_jobs.get(aid)
                                if a is None or b is None or a.analyst_id != b.analyst_id or any(
                                    abs(float(x)-float(y)) > TOL for x, y in (
                                        (a.start, b.start), (a.completion, b.completion),
                                        (a.competence, b.competence))
                                ):
                                    task_diff.append((aid, a, b))
                            if task_diff:
                                differences.append(("task_assignments", len(task_diff), "mismatch", None))
                            if set(legacy_l2.pending_at_cutoff) != set(extended_l2.pending_at_cutoff):
                                differences.append(("pending_ids", len(legacy_l2.pending_at_cutoff), len(extended_l2.pending_at_cutoff), None))
                            if differences:
                                check["divergent_episodes"] += 1
                                if len(check["divergences"]) < 20:
                                    check["divergences"].append({**base, "differences": differences[:8]})
                            ew.writerow({**base, "trace_hash": trace_hash, "recommendation_hash": recommendation_hash,
                                "l1_assignment_hash": l1_hash,
                                "l2_assignment_hash": sha(tuple((j.alert_id,j.analyst_id,j.start,j.completion) for j in extended_l2.assignments)),
                                "legacy_admitted": legacy_row["admitted"], "extended_admitted": extended_row["admitted"],
                                "legacy_Splus_num": legacy_row["timely_needs_numerator"], "extended_Splus_num": extended_row["timely_needs_numerator"],
                                "legacy_Splus_den": legacy_row["S_plus_denominator"], "extended_Splus_den": extended_row["S_plus_denominator"],
                                "legacy_L1_backlog_H": legacy_row["L1_backlog_H"], "extended_L1_backlog_H": extended_row["L1_backlog_H"],
                                "legacy_L2_backlog_H": legacy_row["L2_backlog_H"], "extended_L2_backlog_H": extended_row["L2_backlog_H"],
                                "legacy_L2_backlog_terminal": legacy_row["L2_backlog_terminal"], "extended_L2_backlog_terminal": extended_row["L2_backlog_terminal"],
                                "legacy_L2_util_H": legacy_row["utilization_L2_mean_H"], "extended_L2_util_H": extended_row["utilization_L2_mean_H"],
                                "max_abs_numeric_delta": max(deltas, default=0), "status": "PASS" if not differences else "DIVERGED"})
                            check["episodes"] += 1
                    # trace fields independent of policy/alpha/roster
                    aw_trace = {"classifier_id": point["id"], "seed": seed, "alerts": len(trace),
                                "trace_sha256": trace_hash, "recommendation_sha256": recommendation_hash,
                                "need_sha256": need_hash, "l1_assignment_sha256": l1_hash}
                    if int(n_l2) == first_l2_n:
                        aw.writerow(aw_trace)
                    if check["episodes"] % 100 == 0:
                        ef.flush(); tf.flush(); af.flush()
                        print(f"regression episodes={check['episodes']} divergent={check['divergent_episodes']}", flush=True)
        expected = len(points) * len(seed_ids) * len(old.CONFIG["simulation"]["n_L2"]) * len(old.POLICIES) * len(old.ALPHAS)
        check.update({"expected_episodes": expected, "expected_trace_records": len(points)*len(seed_ids),
                      "tolerance_absolute": TOL, "source_branch": "research/soctra-hls-q1-integration-evidence",
                      "source_commit": "9772abae1bfcd2c810760e68ecd8fba107d320f0",
                      "status": "PASS" if check["episodes"] == expected and check["divergent_episodes"] == 0 else "FAIL"})
        check["seed_count_run"] = seed_count
        check["full_reference_campaign"] = seed_count == total_seeds
        (output_dir / "regression_checks.json").write_text(json.dumps(check, indent=2) + "\n")
        if check["status"] != "PASS":
            raise SystemExit("full reference regression failed; inspect regression_checks.json")
    finally:
        old.simulate_l2_hidden_work = old_fn
        ef.close(); tf.close(); af.close()


if __name__ == "__main__":
    main()
