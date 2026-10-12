"""Fit a transparent C3.3 selector and compare it on fresh sequential runs.

The only predictor inputs are the six entries of S, the frozen belief vector,
and remaining decision clock tau. No C3.2 files are written or modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_gate2.run import stable_seed  # noqa: E402
from experiments.synthetic.strategy_discrimination_gate.run import MODE_BY_ID  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.campaign1_protocol import PARAMETERS  # noqa: E402
from hls.campaign3_problem_generator import generator_transition  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

TEAM_SPLIT = ROOT / "results/foundations/campaign3_team_split/team_split.csv"
KERNEL_SPLIT = ROOT / "results/foundations/campaign3_generator_split/kernel_split.csv"
GATE2 = ROOT / "results/diagnostics/campaign3_gate2"
ALLOCATION = ROOT / "results/foundations/campaign3_c32_data/history_clock_assignment.csv"
C32 = ROOT / "results/campaigns/campaign3_c32_incremental"
OUT = ROOT / "results/campaigns/campaign3_c33"
MODES = ("Q00", "Q11")
ACTION_IDS = {action: i for i, action in enumerate(JOINT_ACTIONS)}
ALPHAS = (0.001, 0.01, 0.1, 1.0, 10.0)
FEATURES = tuple([f"s{i}{k}" for i in (1, 2, 3) for k in (1, 2)] + ["b0", "b1", "b2", "tau"])
TRAIN_TARGET_CONTINUATION = "Q11"
SEQ_REPLICATES = 5
BOOTSTRAP_SEED = 20261011
BOOTSTRAP_B = 2000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def feature_vector(state, belief, tau: int) -> np.ndarray:
    values = [float(value) for row in state for value in row]
    values.extend(float(value) for value in belief)
    values.append(float(tau) / 36.0)
    if len(values) != len(FEATURES) or not np.isfinite(values).all():
        raise ValueError("invalid ex-ante feature vector")
    return np.asarray(values, dtype=float)


def _matrix(state_json: str, belief_json: str, tau: int) -> np.ndarray:
    return feature_vector(json.loads(state_json), json.loads(belief_json), tau)


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> dict:
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0] = 1.0
    z = (x - mean) / scale
    x_aug = np.column_stack([np.ones(len(z)), z])
    penalty = np.eye(x_aug.shape[1]) * alpha
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(x_aug.T @ x_aug + penalty, x_aug.T @ y)
    return {"mean": mean.tolist(), "scale": scale.tolist(), "coef": coef.tolist(), "alpha": alpha}


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    z = (x - np.asarray(model["mean"])) / np.asarray(model["scale"])
    return np.column_stack([np.ones(len(z)), z]) @ np.asarray(model["coef"])


def _partition_frame(partition: str) -> pd.DataFrame:
    path = C32 / partition.lower() / "raw_mc_targets.csv"
    expected_hash = C32 / partition.lower() / "consolidation_manifest.json"
    if not path.is_file() or not expected_hash.is_file():
        raise FileNotFoundError(f"C3.2 {partition} frozen target table/manifest missing")
    manifest = json.loads(expected_hash.read_text())
    if sha256(path) != manifest["targets_sha256"]:
        raise RuntimeError(f"C3.2 {partition} hash mismatch")
    targets = pd.read_csv(path)
    if set(targets.partition.astype(str)) != {partition.upper()}:
        raise RuntimeError(f"C3.2 {partition} table has mixed partition rows")
    return targets


def _state_lookup() -> dict[str, dict]:
    assignment = pd.read_csv(ALLOCATION, dtype={"history_id": str})
    selected = assignment[["history_id", "selected_clock", "selected_state_id", "partition"]]
    states = pd.read_csv(GATE2 / "factual_states.csv.gz", dtype={"history_id": str})
    states = states.merge(selected, on="history_id", validate="many_to_one")
    states = states[(states.clock == states.selected_clock) & (states.state_id == states.selected_state_id)]
    if len(states) != 10_500 or states.history_id.nunique() != 10_500:
        raise RuntimeError("C3.2 selected state source mismatch")
    return {str(row.history_id): row._asdict() for row in states.itertuples(index=False)}


def supervised_table(partition: str, state_lookup: dict[str, dict]) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    raw = _partition_frame(partition)
    chosen = raw[(raw.continuation == TRAIN_TARGET_CONTINUATION) & raw.initial_mode.isin(MODES)]
    wide = chosen.pivot(index="history_id", columns="initial_mode", values="raw_mc_G").reset_index()
    if len(wide) != (6300 if partition == "train" else 2100) or wide[["Q00", "Q11"]].isna().any().any():
        raise RuntimeError(f"unexpected C3.2 {partition} Q00/Q11 labels")
    records, targets = [], []
    for row in wide.itertuples(index=False):
        state = state_lookup[str(row.history_id)]
        records.append(_matrix(state["state_before"], state["belief_before"], int(state["tau"])))
        targets.append(float(row.Q11) - float(row.Q00))
    meta = wide[["history_id"]].copy()
    meta["observed_advantage"] = targets
    return np.asarray(records), np.asarray(targets), meta


def validation_regret(model: dict, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    prediction = predict(model, x)
    select_11 = prediction >= 0.0
    regret = np.where(select_11, np.maximum(-y, 0.0), np.maximum(y, 0.0))
    return float(regret.mean()), float(np.mean((prediction - y) ** 2))


def train_selector() -> tuple[dict, dict]:
    lookup = _state_lookup()
    x_train, y_train, _ = supervised_table("train", lookup)
    x_val, y_val, val_meta = supervised_table("validation", lookup)
    candidates = []
    for alpha in ALPHAS:
        candidate = fit_ridge(x_train, y_train, alpha)
        regret, mse = validation_regret(candidate, x_val, y_val)
        candidates.append((regret, mse, alpha, candidate))
    # Deterministic validation selection: lower policy regret, then MSE, then alpha.
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    best_regret, best_mse, alpha, model = candidates[0]
    x_test, y_test, test_meta = supervised_table("development_test", lookup)
    test_regret, test_mse = validation_regret(model, x_test, y_test)
    test_meta["predicted_advantage"] = predict(model, x_test)
    test_meta["selected_mode"] = np.where(test_meta.predicted_advantage >= 0, "Q11", "Q00")
    test_meta["paired_regret"] = np.where(
        test_meta.selected_mode == "Q11", np.maximum(-y_test, 0.0), np.maximum(y_test, 0.0)
    )
    report = {
        "method": "standardized linear Ridge regression predicting Q11-continuation raw Monte Carlo advantage Y_Q11^Q11 - Y_Q00^Q11; META selects Q11 for prediction >= 0, otherwise Q00",
        "predictor_features": list(FEATURES),
        "continuation_target": TRAIN_TARGET_CONTINUATION,
        "continuation_choice_rationale": "fixed before fitting: Q11 is the continuation proxy for a selector intended to persist; Q00 continuation data are preserved but not averaged or used to select the target continuation",
        "alpha_candidates": list(ALPHAS), "selected_alpha": alpha,
        "validation_mean_policy_regret": best_regret, "validation_mse": best_mse,
        "validation_candidate_metrics": [
            {"alpha": item[2], "mean_policy_regret": item[0], "mse": item[1]} for item in candidates
        ],
        "development_test_once": {"n": len(y_test), "mean_policy_regret": test_regret, "mse": test_mse,
                                  "sign_accuracy": float(np.mean((predict(model, x_test) >= 0) == (y_test >= 0)))},
        "training_rows": len(y_train), "validation_rows": len(y_val),
        "development_test_rows": len(y_test),
        "c32_training_hash": sha256(C32 / "train/raw_mc_targets.csv"),
        "c32_validation_hash": sha256(C32 / "validation/raw_mc_targets.csv"),
        "c32_development_test_hash": sha256(C32 / "development_test/raw_mc_targets.csv"),
        "c32_allocation_hash": sha256(ALLOCATION),
    }
    return {**model, "features": list(FEATURES), "decision_rule": "prediction >= 0 => Q11; else Q00"}, report


def team_kernel_maps() -> tuple[list[dict], list[dict]]:
    teams = pd.read_csv(TEAM_SPLIT, dtype=str)
    kernels = pd.read_csv(KERNEL_SPLIT, dtype=str)
    teams = teams[teams.partition == "development"].to_dict("records")
    kernels = kernels[kernels.split_role == "development"].to_dict("records")
    if len(teams) != 20 or len(kernels) != 21:
        raise RuntimeError("frozen C3 development team/kernel split mismatch")
    return teams, kernels


def make_tasks(replicates: int = SEQ_REPLICATES) -> list[dict]:
    teams, kernels = team_kernel_maps()
    tasks = []
    for team in teams:
        matrix = tuple(tuple(float(team[f"s{i}{k}"]) for k in (1, 2)) for i in (1, 2, 3))
        for kernel in kernels:
            params = (float(kernel["alpha_stay"]), float(kernel["alpha_move"]), float(kernel["alpha_return"]),
                      None if kernel["sigma"] == "" else float(kernel["sigma"]))
            for replicate in range(replicates):
                namespace = ("campaign3_c33_sequential_v1", team["team_id"], kernel["kernel_id"], replicate)
                tasks.append({"history_id": ":".join(map(str, namespace)), "team_id": team["team_id"],
                              "kernel_id": kernel["kernel_id"], "replicate": replicate,
                              "problem_seed": stable_seed(*namespace, "problem"),
                              "noise_seed": stable_seed(*namespace, "noise"), "team": matrix, "kernel": params})
    return tasks


def make_exogenous(task: dict) -> tuple[tuple[float, ...], tuple[float, ...]]:
    problem_rng = np.random.default_rng(task["problem_seed"])
    noise_rng = np.random.default_rng(task["noise_seed"])
    problems = [float(problem_rng.uniform(0.2, 0.8))]
    for _ in range(11):
        problems.append(generator_transition(problems, task["kernel"], problem_rng).p_next)
    eps = tuple(float(v) for v in noise_rng.standard_normal(36))
    return tuple(problems), eps


@lru_cache(maxsize=300_000)
def select_action(state, belief, remaining: int, mode: str):
    return planner.choose_prospective_action(state, belief, HYPOTHESIS_REPERTOIRE,
                                            remaining=remaining, policy_mode=MODE_BY_ID[mode],
                                            eta=PARAMETERS["eta"])[0]


def sequential_history(payload: tuple[dict, dict]) -> tuple[list[dict], list[dict]]:
    task, model_spec = payload
    problems, eps = make_exogenous(task)
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    outcomes, traces = [], []
    for policy in ("Q00", "Q11", "META"):
        state = task["team"]
        belief = prior
        cumulative = 0.0
        elapsed = 0
        for j, p in enumerate(problems):
            if j:
                belief = prior
            for step in range(3):
                tau = 36 - (3 * j + step)
                x = feature_vector(state, belief, tau)
                start = time.perf_counter_ns()
                if policy == "META":
                    score = float(predict(model_spec, x.reshape(1, -1))[0])
                    selected_mode = "Q11" if score >= 0.0 else "Q00"
                else:
                    selected_mode = policy
                action = select_action(state, belief, 3 - step, selected_mode)
                decision_ns = time.perf_counter_ns() - start
                real = theory._real_decision(state, belief, action, (p, 1.0 - p), eps[3 * j + step], model)
                cumulative += real.mu_true
                traces.append({"history_id": task["history_id"], "team_id": task["team_id"],
                               "kernel_id": task["kernel_id"], "replicate": task["replicate"],
                               "policy": policy, "problem_index": j + 1, "decision": step + 1,
                               "tau": tau, "selected_mode": selected_mode, "action_id": ACTION_IDS[action],
                               "mu_true": real.mu_true, "decision_wall_ns": decision_ns,
                               "state_before": packed(state), "belief_before": packed(belief)})
                state, belief = real.state_after, real.belief_after
                elapsed += decision_ns
        outcomes.append({"history_id": task["history_id"], "team_id": task["team_id"],
                         "kernel_id": task["kernel_id"], "replicate": task["replicate"],
                         "policy": policy, "cumulative_mu_true": cumulative,
                         "decision_wall_ns": elapsed, "problem_seed": task["problem_seed"],
                         "noise_seed": task["noise_seed"],
                         "problem_stream_sha256": hashlib.sha256(packed(problems).encode()).hexdigest(),
                         "noise_stream_sha256": hashlib.sha256(packed(eps).encode()).hexdigest()})
    return outcomes, traces


def paired_summary(run_frame: pd.DataFrame) -> dict:
    wide = run_frame.pivot(index=["team_id", "kernel_id", "replicate"], columns="policy", values="cumulative_mu_true")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    contrasts = {}
    cells = [group for _, group in wide.groupby(level=[0, 1], sort=True)]
    for policy, reference in (("Q11", "Q00"), ("META", "Q00"), ("META", "Q11")):
        differences = [(group[policy] - group[reference]).to_numpy() for group in cells]
        delta = np.concatenate(differences)
        draws = np.empty(BOOTSTRAP_B)
        for i in range(BOOTSTRAP_B):
            draws[i] = np.mean(np.concatenate([
                values[rng.integers(0, len(values), len(values))] for values in differences
            ]))
        contrasts[f"{policy}-{reference}"] = {"mean": float(delta.mean()), "median": float(np.median(delta)),
                                       "q025": float(np.quantile(draws, .025)), "q975": float(np.quantile(draws, .975)),
                                       "q05": float(np.quantile(delta, .05)), "q95": float(np.quantile(delta, .95)),
                                       "positive_fraction": float(np.mean(delta > 0)),
                                       "negative_fraction": float(np.mean(delta < 0)),
                                       "zero_fraction": float(np.mean(delta == 0)),
                                       "paired_histories": len(delta), "bootstrap_unit": "replicate history, resampled within team/kernel cell"}
    return contrasts


def benchmark_isolated(model_spec: dict, trajectory_path: Path, sample_size: int = 64) -> dict:
    """Measure uncached policy computation on a fixed existing state sample."""
    frame = pd.read_csv(trajectory_path, usecols=["state_before", "belief_before", "tau"])
    frame = frame.iloc[np.linspace(0, len(frame) - 1, min(sample_size, len(frame)), dtype=int)]
    elapsed = {"Q00": [], "Q11": [], "META": []}
    for row in frame.itertuples(index=False):
        state = tuple(tuple(float(v) for v in x) for x in json.loads(row.state_before))
        belief = tuple(float(v) for v in json.loads(row.belief_before))
        x = feature_vector(state, belief, int(row.tau))
        for policy in ("Q00", "Q11", "META"):
            start = time.perf_counter_ns()
            if policy == "META":
                score = float(predict(model_spec, x.reshape(1, -1))[0])
                selected = "Q11" if score >= 0 else "Q00"
            else:
                selected = policy
            planner.choose_prospective_action(state, belief, HYPOTHESIS_REPERTOIRE,
                                               remaining=(int(row.tau) - 1) % 3 + 1,
                                               policy_mode=MODE_BY_ID[selected], eta=PARAMETERS["eta"])
            elapsed[policy].append(time.perf_counter_ns() - start)
    return {"sampled_existing_predecision_states": len(frame), "cache": "bypassed; no policy result reused",
            "mean_ms": {k: float(np.mean(v) / 1e6) for k, v in elapsed.items()},
            "median_ms": {k: float(np.median(v) / 1e6) for k, v in elapsed.items()},
            "q90_ms": {k: float(np.quantile(v, .90) / 1e6) for k, v in elapsed.items()},
            "timing_scope": "decision operator only; hardware/runtime dependent; not a deliberation-performance scalarization"}


def summarize_existing() -> dict:
    output = OUT / "sequential_full"
    run_path = output / "runs.csv"
    trajectory_path = output / "trajectories.csv.gz"
    if not run_path.is_file() or not trajectory_path.is_file():
        raise FileNotFoundError("complete sequential outputs are required")
    runs = pd.read_csv(run_path)
    trajectories = pd.read_csv(trajectory_path)
    expected_ids = {task["history_id"] for task in make_tasks()}
    if runs.history_id.nunique() != 2100 or set(runs.history_id) != expected_ids:
        raise RuntimeError("sequential design history count/key mismatch")
    if len(runs) != 6300 or len(trajectories) != 226800:
        raise RuntimeError("sequential run/trajectory row count mismatch")
    if not runs.groupby("history_id").problem_stream_sha256.nunique().eq(1).all() or not runs.groupby("history_id").noise_stream_sha256.nunique().eq(1).all():
        raise RuntimeError("paired exogenous streams are not aligned")
    return {"artifact_type": "campaign3_c33_postrun_summary", "histories": 2100,
            "policy_runs": 6300, "policy_decision_rows": 226800,
            "mean_cumulative_mu_true": {k: float(v) for k, v in runs.groupby("policy").cumulative_mu_true.mean().items()},
            "sd_cumulative_mu_true": {k: float(v) for k, v in runs.groupby("policy").cumulative_mu_true.std().items()},
            "paired_differences": paired_summary(runs),
            "isolated_decision_cost": benchmark_isolated(json.loads((OUT / "selector_model.json").read_text()), trajectory_path),
            "bootstrap_B": BOOTSTRAP_B, "bootstrap_seed": BOOTSTRAP_SEED,
            "raw_runs_sha256": sha256(run_path), "raw_trajectories_sha256": sha256(trajectory_path)}


def run_sequential(model_spec: dict, limit: int | None = None, workers: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    tasks = make_tasks()
    if limit is not None:
        tasks = tasks[:limit]
    payloads = [(task, model_spec) for task in tasks]
    if workers == 1:
        results = [sequential_history(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(sequential_history, payloads, chunksize=1))
    runs = pd.DataFrame([row for result, _ in results for row in result])
    trajectories = pd.DataFrame([row for _, trace in results for row in trace])
    return runs, trajectories


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", action="store_true", help="fit selector and write TRAIN/VALIDATION/DEVELOPMENT_TEST report")
    parser.add_argument("--sequential", action="store_true", help="run fresh sequential evaluation; bounded unless --full")
    parser.add_argument("--summarize", action="store_true", help="validate/summarize completed full sequential outputs")
    parser.add_argument("--full", action="store_true", help="run all frozen 2,100 fresh histories (420 cells x 5 reps)")
    parser.add_argument("--limit-histories", type=int, default=3, help="bounded fresh histories; default is a small smoke comparison")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if sum((args.train, args.sequential, args.summarize)) != 1:
        parser.error("choose exactly one of --train, --sequential, or --summarize")
    if args.full and not args.sequential:
        parser.error("--full requires --sequential")
    if args.train:
        model_spec, report = train_selector()
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "selector_model.json").write_text(json.dumps(model_spec, indent=2, sort_keys=True) + "\n")
        report["model_sha256"] = sha256(OUT / "selector_model.json")
        (OUT / "training_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps(report, sort_keys=True))
        return
    if args.summarize:
        summary = summarize_existing()
        (OUT / "sequential_full/analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, sort_keys=True))
        return
    model_path = OUT / "selector_model.json"
    if not model_path.is_file():
        parser.error("train the selector first with --train")
    model_spec = json.loads(model_path.read_text())
    tasks = make_tasks()
    count = len(tasks) if args.full else args.limit_histories
    if count < 1 or count > len(tasks):
        parser.error("invalid history count")
    output = OUT / ("sequential_full" if args.full else f"sequential_smoke_{count}")
    if output.exists():
        raise RuntimeError(f"refusing to overwrite existing results: {output}")
    started = time.perf_counter()
    runs, traces = run_sequential(model_spec, None if args.full else count, args.workers)
    elapsed = time.perf_counter() - started
    output.mkdir(parents=True)
    runs.to_csv(output / "runs.csv", index=False)
    traces.to_csv(output / "trajectories.csv.gz", index=False, compression="gzip")
    summary = {
        "artifact_type": "campaign3_c33_sequential_comparison",
        "scope": "full development design" if args.full else "bounded diagnostic only; not scientific evaluation",
        "histories": int(runs.history_id.nunique()), "policy_runs": len(runs),
        "decision_states_per_policy": int(len(traces) / 3), "policy_decision_rows": len(traces),
        "elapsed_seconds": elapsed, "seconds_per_base_history_three_policies": elapsed / runs.history_id.nunique(),
        "mean_decision_wall_ms": float(traces.decision_wall_ns.mean() / 1e6),
        "paired_performance": paired_summary(runs) if args.full else {},
        "paired_exogenous_streams": bool(runs.groupby("history_id")["problem_stream_sha256"].nunique().eq(1).all()
                                          and runs.groupby("history_id")["noise_stream_sha256"].nunique().eq(1).all()),
        "training_model_sha256": sha256(model_path), "bootstrap_B": BOOTSTRAP_B,
        "bootstrap_seed": BOOTSTRAP_SEED if args.full else None,
        "development_only": True, "heldout_used": False,
    }
    summary["runs_sha256"] = sha256(output / "runs.csv")
    summary["trajectories_sha256"] = sha256(output / "trajectories.csv.gz")
    (output / "execution_manifest.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
