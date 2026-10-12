"""Frozen META-VOC confirmatory adapter; original development runner is untouched.

Use --freeze before --execute.  The default invocation only shows help.
RANDOM uses pre-execution Bernoulli priorities at nominal probabilities, not
the retrospective frequency matching of the development experiment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_c33 import c33  # noqa: E402
from experiments.synthetic.campaign3_meta_voc import run as voc  # noqa: E402

PROTOCOL = "C3-META-VOC-CONF-v1"
SEED_NAMESPACE = "campaign3_meta_voc_confirmatory_v1"
RANDOM_NAMESPACE = "campaign3_meta_voc_confirmatory_random_v1"
FOUNDATION = ROOT / "results/foundations/campaign3_meta_voc_confirmatory"
OUTPUT = ROOT / "results/campaigns/campaign3_meta_voc_confirmatory"
PROTOCOL_DOC = ROOT / "docs/experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_PROTOCOL.md"
TEAM_TABLE = c33.TEAM_SPLIT
KERNEL_TABLE = c33.KERNEL_SPLIT
MODEL_FILE = c33.OUT / "selector_model.json"
CALIBRATION_FILE = voc.OUT / "sequential_full/calibration.json"
DOMAINS = ("G1", "G2", "G3", "G4")
DOMAIN_PARTITIONS = {
    "G1": ("development", "development"),
    "G2": ("development", "heldout"),
    "G3": ("heldout", "development"),
    "G4": ("heldout", "heldout"),
}
EXPECTED_DOMAIN_COUNTS = {"G1": 420, "G2": 200, "G3": 168, "G4": 80}
EXPECTED_TEAM_IDS = {
    "development": ("G00", "G04", "G05", "G07") + tuple(f"F{i:02d}" for i in range(1, 17)),
    "heldout": tuple(f"F{i:02d}" for i in range(17, 25)),
}
EXPECTED_KERNEL_IDS = {
    "development": ("K01", "K02", "K03", "K05", "K06", "K07", "K10", "K11", "K13", "K15", "K16", "K17", "K20", "K21", "K23", "K25", "K26", "K27", "K31", "K32", "K33"),
    "heldout": ("K00", "K04", "K08", "K09", "K14", "K18", "K19", "K24", "K28", "K30"),
}
POLICIES = ("FAST", "DEEP", "META_VOC_25", "RANDOM_25", "META_VOC_50", "RANDOM_50", "META_VOC_75", "RANDOM_75")
RANDOM_PROBABILITIES = {25: .25, 50: .50, 75: .75}
REPLICATES = (0,)
BATCH_SIZE = 16
SEED_MODULUS = 2**63 - 1
HASHED_INPUTS = (
    "experiments/synthetic/campaign3_meta_voc/run.py",
    "experiments/synthetic/campaign3_meta_voc/confirmatory.py",
    "experiments/synthetic/campaign3_meta_voc/analyze_confirmatory.py",
    "experiments/synthetic/campaign3_fast_deep_meta/run.py",
    "experiments/synthetic/campaign3_c33/c33.py",
    "src/hls/finite_problem_belief.py",
    "src/hls/campaign2_theory.py",
    "src/hls/campaign3_problem_generator.py",
    "src/hls/discover_develop_v2.py",
    "src/hls/small_problem_world.py",
    "src/hls/discover_v0.py",
    "src/hls/campaign1_protocol.py",
    "results/campaigns/campaign3_c33/selector_model.json",
    "results/campaigns/campaign3_meta_voc/sequential_full/calibration.json",
    "results/foundations/campaign3_team_split/team_split.csv",
    "results/foundations/campaign3_generator_split/kernel_split.csv",
    "docs/experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_PROTOCOL.md",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def stable_priority(*parts: object) -> float:
    """PRF priority in [0,1), independent of physical/observation streams."""
    return c33.stable_seed(*parts) / SEED_MODULUS


def partitions() -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    teams = pd.read_csv(TEAM_TABLE, dtype=str).fillna("")
    kernels = pd.read_csv(KERNEL_TABLE, dtype=str).fillna("")
    by_team = {role: teams.loc[teams.partition == role].to_dict("records") for role in EXPECTED_TEAM_IDS}
    by_kernel = {role: kernels.loc[kernels.split_role == role].to_dict("records") for role in EXPECTED_KERNEL_IDS}
    for role, expected in EXPECTED_TEAM_IDS.items():
        if tuple(row["team_id"] for row in by_team[role]) != expected:
            raise RuntimeError(f"frozen {role} team membership/order mismatch")
    for role, expected in EXPECTED_KERNEL_IDS.items():
        if tuple(row["kernel_id"] for row in by_kernel[role]) != expected:
            raise RuntimeError(f"frozen {role} kernel membership/order mismatch")
    if set(teams.team_id) != set(EXPECTED_TEAM_IDS["development"] + EXPECTED_TEAM_IDS["heldout"]):
        raise RuntimeError("team split contains unexpected identity")
    if set(kernels.loc[kernels.split_role != "static_alias", "kernel_id"]) != set(EXPECTED_KERNEL_IDS["development"] + EXPECTED_KERNEL_IDS["heldout"]):
        raise RuntimeError("kernel split contains unexpected executable identity")
    return by_team, by_kernel


def planned_tasks() -> list[dict]:
    team_map, kernel_map = partitions()
    tasks = []
    for domain in DOMAINS:
        team_role, kernel_role = DOMAIN_PARTITIONS[domain]
        for team in team_map[team_role]:
            state = tuple(tuple(float(team[f"s{i}{k}"]) for k in (1, 2)) for i in (1, 2, 3))
            for kernel in kernel_map[kernel_role]:
                params = (float(kernel["alpha_stay"]), float(kernel["alpha_move"]),
                          float(kernel["alpha_return"]), None if kernel["sigma"] == "" else float(kernel["sigma"]))
                for replicate in REPLICATES:
                    identity = (SEED_NAMESPACE, domain, team["team_id"], kernel["kernel_id"], replicate)
                    tasks.append({"domain": domain, "history_id": ":".join(map(str, identity)),
                                  "team_id": team["team_id"], "kernel_id": kernel["kernel_id"],
                                  "replicate": replicate, "team": state, "kernel": params,
                                  "problem_seed": c33.stable_seed(*identity, "problem"),
                                  "noise_seed": c33.stable_seed(*identity, "noise")})
    actual = pd.Series([t["domain"] for t in tasks]).value_counts().to_dict()
    if actual != EXPECTED_DOMAIN_COUNTS or len(tasks) != 868:
        raise RuntimeError(f"confirmatory domain factorial mismatch: {actual}")
    ids = [t["history_id"] for t in tasks]
    seeds = [seed for t in tasks for seed in (t["problem_seed"], t["noise_seed"])]
    if len(ids) != len(set(ids)) or len(seeds) != len(set(seeds)):
        raise RuntimeError("duplicate confirmatory history ID or exogenous seed")
    if 20261008 in seeds or 20261009 in seeds:
        raise RuntimeError("PGCG calibration/characterization seed collision")
    return tasks


def random_routes(task: dict) -> tuple[dict[int, set[tuple[str, int]]], list[dict]]:
    routes = {point: set() for point in RANDOM_PROBABILITIES}
    rows = []
    for clock in range(1, 37):
        if clock % 3 == 0:
            continue
        row = {"history_id": task["history_id"], "domain": task["domain"], "clock": clock}
        for point, probability in RANDOM_PROBABILITIES.items():
            priority = stable_priority(RANDOM_NAMESPACE, task["history_id"], point, clock, "priority")
            invoke = priority < probability
            row[f"priority_{point}"] = priority
            row[f"invoke_{point}"] = int(invoke)
            if invoke:
                routes[point].add((task["history_id"], clock))
        rows.append(row)
    if len(rows) != 24:
        raise RuntimeError("RANDOM schedule not limited to 24 nonterminal decisions")
    return routes, rows


def _prior_history_ids_and_seeds() -> tuple[set[str], set[int]]:
    sources = (
        ROOT / "results/diagnostics/campaign3_gate2/factual_histories.csv.gz",
        c33.OUT / "sequential_full/runs.csv",
        ROOT / "results/campaigns/campaign3_fast_deep_meta/sequential_full/runs.csv",
        voc.OUT / "sequential_full/runs.csv",
        ROOT / "results/foundations/campaign3_horizon_pilot/seed_allocation.csv",
    )
    ids: set[str] = set()
    seeds: set[int] = {20261008, 20261009}
    for path in sources:
        if not path.exists():
            continue
        header = pd.read_csv(path, nrows=0).columns
        selected = [name for name in header if name == "history_id" or name == "seed" or name.endswith("_seed")]
        if not selected:
            continue
        frame = pd.read_csv(path, usecols=selected, dtype={"history_id": str} if "history_id" in selected else None)
        if "history_id" in frame:
            ids.update(frame.history_id.dropna().astype(str))
        for name in selected:
            if name.endswith("_seed") or name == "seed":
                seeds.update(int(x) for x in frame[name].dropna())
    return ids, seeds


def freeze() -> Path:
    if FOUNDATION.exists() or OUTPUT.exists():
        raise RuntimeError("confirmatory freeze/results already exist; refusing to replace them")
    if not PROTOCOL_DOC.is_file():
        raise FileNotFoundError(PROTOCOL_DOC)
    tasks = planned_tasks()
    old_ids, old_seeds = _prior_history_ids_and_seeds()
    new_ids = {t["history_id"] for t in tasks}
    new_seeds = {seed for t in tasks for seed in (t["problem_seed"], t["noise_seed"])}
    if new_ids & old_ids or new_seeds & old_seeds:
        raise RuntimeError("confirmatory identity/seed collision with previous development or PGCG")
    schedule = [row for task in tasks for row in random_routes(task)[1]]
    if len(schedule) != 868 * 24:
        raise RuntimeError("random priority schedule count mismatch")
    FOUNDATION.mkdir(parents=True)
    task_table = pd.DataFrame([{k: v for k, v in task.items() if k not in ("team", "kernel")} for task in tasks])
    task_path = FOUNDATION / "planned_histories.csv"
    schedule_path = FOUNDATION / "random_invocation_schedule.csv"
    task_table.to_csv(task_path, index=False)
    pd.DataFrame(schedule).to_csv(schedule_path, index=False)
    model = json.loads(MODEL_FILE.read_text())
    calibration = json.loads(CALIBRATION_FILE.read_text())
    input_hashes = {name: sha256(ROOT / name) for name in HASHED_INPUTS}
    manifest = {
        "protocol": PROTOCOL, "status": "pre_execution_frozen", "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_git_head": _head(), "input_sha256": input_hashes,
        "planned_histories_sha256": sha256(task_path), "random_schedule_sha256": sha256(schedule_path),
        "predictor": {"features": model["features"], "alpha": model["alpha"],
                      "standardization_mean": model["mean"], "standardization_scale": model["scale"],
                      "intercept_and_coefficients": model["coef"]},
        "cost_seconds_by_remaining": calibration["predicted_extra_cost_seconds_by_remaining"],
        "thresholds": calibration["thresholds"],
        "team_ids": {role: list(ids) for role, ids in EXPECTED_TEAM_IDS.items()},
        "kernel_ids": {role: list(ids) for role, ids in EXPECTED_KERNEL_IDS.items()},
        "domains": EXPECTED_DOMAIN_COUNTS, "histories_total": len(tasks), "replicates": list(REPLICATES),
        "problems_per_history": 12, "decisions_per_problem": 3, "policies": list(POLICIES),
        "random_probabilities": {str(k): v for k, v in RANDOM_PROBABILITIES.items()},
        "random_priority_rule": "SHA256-based stable_seed(namespace, history_id, operating_point, clock, priority)/(2^63-1) < nominal p; independent namespace per operating point",
        "seed_namespace": SEED_NAMESPACE, "random_namespace": RANDOM_NAMESPACE,
        "prior_identity_collision_count": 0, "prior_seed_collision_count": 0,
        "bootstrap": {"unit": "complete matched history", "strata": list(DOMAINS),
                      "domains_equal_weight": True, "replicates": 2000, "seed": 20261016,
                      "interval": "percentile 95%"},
        "batch_size": BATCH_SIZE,
        "crn": "one exogenous 12-problem and 36-normal-innovation stream per history shared by all eight independently evolving policies",
        "terminal_rule": "remaining=1 uses FAST for all eight policies without selector/DEEP",
        "execution_authorized_after_this_manifest_only": True,
    }
    path = FOUNDATION / "pre_execution_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    verify_frozen()
    return path


def _head() -> str:
    import subprocess
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def verify_frozen() -> dict:
    manifest_path = FOUNDATION / "pre_execution_manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("pre-execution manifest absent")
    m = json.loads(manifest_path.read_text())
    if m["protocol"] != PROTOCOL or m["status"] != "pre_execution_frozen":
        raise RuntimeError("unexpected confirmatory protocol status")
    for name, expected in m["input_sha256"].items():
        if sha256(ROOT / name) != expected:
            raise RuntimeError(f"frozen input hash changed: {name}")
    for name, key in (("planned_histories.csv", "planned_histories_sha256"),
                      ("random_invocation_schedule.csv", "random_schedule_sha256")):
        if sha256(FOUNDATION / name) != m[key]:
            raise RuntimeError(f"frozen allocation hash changed: {name}")
    tasks = planned_tasks()
    planned = pd.read_csv(FOUNDATION / "planned_histories.csv")
    if len(planned) != len(tasks) or set(planned.history_id) != {t["history_id"] for t in tasks}:
        raise RuntimeError("frozen planned-history allocation mismatch")
    if planned.groupby("domain").size().to_dict() != EXPECTED_DOMAIN_COUNTS:
        raise RuntimeError("frozen domain allocation mismatch")
    schedule = pd.read_csv(FOUNDATION / "random_invocation_schedule.csv")
    if len(schedule) != 868 * 24 or schedule.history_id.nunique() != 868:
        raise RuntimeError("frozen random-priority schedule mismatch")
    if any(set(schedule[f"invoke_{point}"].unique()) - {0, 1} for point in RANDOM_PROBABILITIES):
        raise RuntimeError("invalid random schedule invocation flag")
    expected_schedule = pd.DataFrame([row for task in tasks for row in random_routes(task)[1]])
    keys = ["history_id", "domain", "clock", *(f"invoke_{point}" for point in RANDOM_PROBABILITIES)]
    if not schedule[keys].equals(expected_schedule[keys]):
        raise RuntimeError("frozen RANDOM decisions differ from independent priority rule")
    for point in RANDOM_PROBABILITIES:
        if not np.allclose(schedule[f"priority_{point}"], expected_schedule[f"priority_{point}"],
                           atol=1e-15, rtol=0):
            raise RuntimeError("frozen RANDOM priority differs from independent rule")
    return m


def _simulate_payload(payload: tuple[dict, dict, dict, dict, dict]):
    task, model, costs, thresholds, routes = payload
    runs, traces = voc.simulate(task, model, costs, thresholds, routes, POLICIES)
    for row in runs:
        row["domain"] = task["domain"]
    for row in traces:
        row["domain"] = task["domain"]
        row["replicate"] = task["replicate"]
    return runs, traces


def _atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def _write_batch(path: Path, rows: list[dict]) -> str:
    if path.exists():
        raise RuntimeError(f"refusing to replace existing batch: {path}")
    temporary = path.with_name(path.name + ".partial.gz")
    pd.DataFrame(rows).to_csv(temporary, index=False, compression="gzip")
    os.replace(temporary, path)
    return sha256(path)


def _validate_batch(runs: list[dict], traces: list[dict], batch_tasks: list[dict]) -> None:
    n = len(batch_tasks)
    if len(runs) != n * 8 or len(traces) != n * 8 * 36:
        raise RuntimeError("batch output count mismatch")
    rf = pd.DataFrame(runs)
    tf = pd.DataFrame(traces)
    if rf.groupby("history_id").policy.nunique().ne(8).any() or tf.groupby(["history_id", "policy"]).size().ne(36).any():
        raise RuntimeError("missing policy trajectory in batch")
    if rf.groupby("history_id")["problem_stream_sha256"].nunique().ne(1).any() or rf.groupby("history_id")["noise_stream_sha256"].nunique().ne(1).any():
        raise RuntimeError("CRN stream mismatch in batch")
    terminal = tf.loc[tf.remaining == 1]
    if not terminal.route.eq("FAST_TERMINAL").all() or terminal.deep_ns.ne(0).any() or terminal.selector_ns.ne(0).any():
        raise RuntimeError("terminal FAST rule violated")
    if tf.loc[tf.route.isin(("FAST_ACCEPT", "FAST_RANDOM")), "deep_ns"].ne(0).any():
        raise RuntimeError("DEEP called on FAST route")
    summed = tf.groupby(["history_id", "policy"]).mu_true.sum()
    observed = rf.set_index(["history_id", "policy"]).cumulative_mu_true
    if not np.allclose(summed.loc[observed.index].to_numpy(), observed.to_numpy(), atol=1e-10, rtol=0):
        raise RuntimeError("cumulative mu_true does not equal trajectory reward sum")
    for _, group in tf.groupby(["history_id", "policy"]):
        ordered = group.sort_values("clock")
        if ordered.clock.tolist() != list(range(1, 37)):
            raise RuntimeError("clock gap or duplicate in trajectory")
        if not np.array_equal(ordered.state_after.to_numpy()[:-1], ordered.state_before.to_numpy()[1:]):
            raise RuntimeError("capability trajectory discontinuity")


def execute(workers: int) -> Path:
    if workers < 1:
        raise ValueError("workers must be positive")
    frozen = verify_frozen()
    tasks = planned_tasks()
    model = json.loads(MODEL_FILE.read_text())
    calibration = json.loads(CALIBRATION_FILE.read_text())
    costs = {int(k): float(v) for k, v in calibration["predicted_extra_cost_seconds_by_remaining"].items()}
    thresholds = calibration["thresholds"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    batch_dir = OUTPUT / "raw_batches"
    batch_dir.mkdir(exist_ok=True)
    progress_file = OUTPUT / "execution_progress.json"
    frozen_hash = sha256(FOUNDATION / "pre_execution_manifest.json")
    if progress_file.exists():
        progress = json.loads(progress_file.read_text())
        if progress["pre_execution_manifest_sha256"] != frozen_hash:
            raise RuntimeError("resume manifest differs from frozen protocol")
        if progress["status"] == "complete":
            raise RuntimeError("confirmatory execution already complete; refusing another run")
    else:
        progress = {"protocol": PROTOCOL, "status": "running", "pre_execution_manifest_sha256": frozen_hash,
                    "started_utc": datetime.now(timezone.utc).isoformat(), "workers": workers,
                    "batches": {}, "hardware": {"platform": platform.platform(), "processor": platform.processor(),
                                              "cpu_count": os.cpu_count(), "python": sys.version,
                                              "numpy": np.__version__, "pandas": pd.__version__}}
        _atomic_json(progress_file, progress)
    started = time.perf_counter()
    try:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for offset in range(0, len(tasks), BATCH_SIZE):
                batch_number = offset // BATCH_SIZE
                key = f"batch_{batch_number:03d}"
                batch_tasks = tasks[offset:offset + BATCH_SIZE]
                run_path = batch_dir / f"{key}_runs.csv.gz"
                trace_path = batch_dir / f"{key}_trajectories.csv.gz"
                if key in progress["batches"]:
                    record = progress["batches"][key]
                    if sha256(run_path) != record["runs_sha256"] or sha256(trace_path) != record["trajectories_sha256"]:
                        raise RuntimeError(f"completed batch hash mismatch: {key}")
                    continue
                if run_path.exists() or trace_path.exists():
                    raise RuntimeError(f"orphaned unregistered batch file: {key}")
                payloads = [(task, model, costs, thresholds, random_routes(task)[0]) for task in batch_tasks]
                pieces = list(pool.map(_simulate_payload, payloads, chunksize=1))
                runs = [row for part, _ in pieces for row in part]
                traces = [row for _, part in pieces for row in part]
                _validate_batch(runs, traces, batch_tasks)
                run_hash = _write_batch(run_path, runs)
                trace_hash = _write_batch(trace_path, traces)
                progress["batches"][key] = {"history_ids": [t["history_id"] for t in batch_tasks],
                                            "runs": len(runs), "trajectories": len(traces),
                                            "runs_sha256": run_hash, "trajectories_sha256": trace_hash}
                _atomic_json(progress_file, progress)
                print(f"{key}: {len(batch_tasks)} histories persisted", flush=True)
        if len(progress["batches"]) != (len(tasks) + BATCH_SIZE - 1) // BATCH_SIZE:
            raise RuntimeError("batch count incomplete")
        run_frames, trace_frames = [], []
        for key in sorted(progress["batches"]):
            run_frames.append(pd.read_csv(batch_dir / f"{key}_runs.csv.gz"))
            trace_frames.append(pd.read_csv(batch_dir / f"{key}_trajectories.csv.gz"))
        runs = pd.concat(run_frames, ignore_index=True).sort_values(["domain", "history_id", "policy"])
        traces = pd.concat(trace_frames, ignore_index=True).sort_values(["domain", "history_id", "policy", "clock"])
        if len(runs) != 868 * 8 or len(traces) != 868 * 8 * 36:
            raise RuntimeError("final count mismatch")
        if runs.groupby("domain").history_id.nunique().to_dict() != EXPECTED_DOMAIN_COUNTS:
            raise RuntimeError("domain run mismatch")
        final_runs = OUTPUT / "runs.csv.gz"
        final_traces = OUTPUT / "trajectories.csv.gz"
        if final_runs.exists() or final_traces.exists():
            raise RuntimeError("refusing to replace final raw output")
        _write_batch(final_runs, runs.to_dict("records"))
        _write_batch(final_traces, traces.to_dict("records"))
        progress["status"] = "complete"
        progress["completed_utc"] = datetime.now(timezone.utc).isoformat()
        progress["elapsed_wall_seconds"] = time.perf_counter() - started
        progress["runs_sha256"] = sha256(final_runs)
        progress["trajectories_sha256"] = sha256(final_traces)
        progress["run_count"] = len(runs)
        progress["trajectory_count"] = len(traces)
        _atomic_json(progress_file, progress)
    except Exception as exc:
        incident = {"protocol": PROTOCOL, "failed_utc": datetime.now(timezone.utc).isoformat(),
                    "error": repr(exc), "traceback": traceback.format_exc(),
                    "completed_batch_count": len(progress["batches"]),
                    "pre_execution_manifest_sha256": frozen_hash}
        failure_path = OUTPUT / "validation_failure.json"
        if not failure_path.exists():
            _atomic_json(failure_path, incident)
        raise
    return progress_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--freeze", action="store_true", help="write protocol allocation without generating histories")
    group.add_argument("--verify", action="store_true", help="check pre-execution freeze hashes and factorial design")
    group.add_argument("--execute", action="store_true", help="execute once; persist and validate resumable batches")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.freeze:
        print(freeze())
    elif args.verify:
        print(json.dumps({"protocol": verify_frozen()["protocol"], "status": "verified"}))
    else:
        print(execute(args.workers))


if __name__ == "__main__":
    main()
