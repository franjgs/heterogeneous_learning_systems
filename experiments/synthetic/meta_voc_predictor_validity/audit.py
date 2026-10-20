"""Reproduce C3.2-horizon labels for an outcome-blind META-VOC validity audit.

Safe by default: ``--prepare`` freezes/verifies a sample, ``--execute`` runs
only explicitly missing batches, and ``--analyze`` uses those audit outputs.
No Campaign 3 artifact is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_c32_data import targets as c32  # noqa: E402
from experiments.synthetic.campaign3_c33 import c33  # noqa: E402
from experiments.synthetic.campaign3_fast_deep_meta import run as fastdeep  # noqa: E402
from experiments.synthetic.campaign3_meta_voc import run as voc  # noqa: E402
from experiments.synthetic.campaign3_meta_voc import confirmatory  # noqa: E402
from experiments.synthetic.campaign4_counterfactual_deliberation import sampling  # noqa: E402
from experiments.synthetic.strategy_discrimination_gate.run import MODE_BY_ID  # noqa: E402
from hls import campaign2_theory as theory  # noqa: E402
from hls import finite_problem_belief as planner  # noqa: E402
from hls.campaign1_protocol import PARAMETERS  # noqa: E402
from hls.discover_v0 import JOINT_ACTIONS  # noqa: E402
from hls.small_problem_world import HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR  # noqa: E402

OUT = ROOT / "results/diagnostics/meta_voc_predictor_validity"
TRAJECTORIES = ROOT / "results/campaigns/campaign3_meta_voc_confirmatory/trajectories.csv.gz"
RUNS = ROOT / "results/campaigns/campaign3_meta_voc_confirmatory/runs.csv.gz"
MODEL = ROOT / "results/campaigns/campaign3_c33/selector_model.json"
CALIBRATION = ROOT / "results/campaigns/campaign3_meta_voc/sequential_full/calibration.json"
TRAIN_TARGETS = ROOT / "results/campaigns/campaign3_c32_incremental/train/raw_mc_targets.csv"
AUDIT_PROTOCOL = "HLS-META-VOC-PREDICTOR-VALIDITY-v1"
MC_REPLICATES = 32  # C4 pre-execution protocol's declared M=32.
BOOTSTRAP_B = 2000
BOOTSTRAP_SEED = 20261012
AUDIT_RANDOM_NAMESPACE = "HLS-META-VOC-PREDICTOR-VALIDITY-v1-independent-mc"
EXPECTED_HASHES = {
    "runs.csv.gz": "3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28",
    "trajectories.csv.gz": "b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498",
    "selector_model.json": "1874b1f06a7122361677f5bb617132bd2eff3976fd1aa890d7152436fb59ba1d",
    "calibration.json": "bf329147e4e62a98bbfc9ae48c75cbe1066c1ff73b87c6fce6b63cf4f796e94a",
}
SOURCE_FILES = (
    "experiments/synthetic/campaign3_c32_data/targets.py",
    "experiments/synthetic/campaign3_c33/c33.py",
    "experiments/synthetic/campaign3_meta_voc/run.py",
    "experiments/synthetic/campaign3_meta_voc/confirmatory.py",
    "experiments/synthetic/campaign3_fast_deep_meta/run.py",
    "src/hls/campaign2_theory.py",
    "src/hls/finite_problem_belief.py",
    "src/hls/campaign3_problem_generator.py",
    "experiments/synthetic/campaign4_counterfactual_deliberation/sampling.py",
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def packed(value) -> str:
    return json.dumps(value, separators=(",", ":"))


def stable_seed(*parts: object) -> int:
    payload = json.dumps(parts, separators=(",", ":"), ensure_ascii=True).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**63 - 1)


def verify_frozen_inputs() -> dict:
    paths = {"runs.csv.gz": RUNS, "trajectories.csv.gz": TRAJECTORIES,
             "selector_model.json": MODEL, "calibration.json": CALIBRATION}
    actual = {name: sha(path) for name, path in paths.items()}
    if actual != EXPECTED_HASHES:
        raise RuntimeError(f"frozen input hash mismatch: {actual}")
    if not TRAIN_TARGETS.is_file():
        raise FileNotFoundError(TRAIN_TARGETS)
    calibration = json.loads(CALIBRATION.read_text())
    if calibration.get("C3.3_model_sha256") != actual["selector_model.json"]:
        raise RuntimeError("frozen calibration does not reference the supplied frozen Ridge model")
    if calibration.get("C3.2_train_sha256") != sha(TRAIN_TARGETS):
        raise RuntimeError("frozen calibration does not reference the supplied C3.2 training data")
    return {
        "frozen_data_model_hashes": actual,
        "c32_train_raw_targets_sha256": sha(TRAIN_TARGETS),
        "source_sha256": {name: sha(ROOT / name) for name in SOURCE_FILES},
        "git_head": os.popen("git rev-parse HEAD").read().strip(),
    }


def _close(a, b, atol=1e-12, rtol=1e-12):
    return bool(np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float), atol=atol, rtol=rtol))


def verify_reconstruction(selected: pd.DataFrame) -> dict:
    """Verify streams and replay selected factual pre/post states from logs."""
    runs = pd.read_csv(RUNS, dtype={"history_id": str})
    tasks = {task["history_id"]: task for task in confirmatory.planned_tasks()}
    run_unique = runs.drop_duplicates("history_id").set_index("history_id")
    if not set(selected.history_id.astype(str)).issubset(tasks):
        raise RuntimeError("selected history missing from frozen confirmatory task list")
    if not set(selected.domain.astype(str)).issubset(set(confirmatory.DOMAINS)):
        raise RuntimeError("unexpected domain")
    if len(selected) != 800 or selected.domain.value_counts().to_dict() != {d: 200 for d in confirmatory.DOMAINS}:
        raise RuntimeError("frozen sample must contain 800 states, 200/domain")

    streams = {}
    for history_id in sorted(set(selected.history_id.astype(str))):
        task = tasks[history_id]
        rows = runs[runs.history_id.astype(str) == history_id]
        if rows.empty or rows.domain.nunique() != 1 or rows.team_id.nunique() != 1 or rows.kernel_id.nunique() != 1:
            raise RuntimeError(f"invalid run metadata for {history_id}")
        if rows.problem_seed.nunique() != 1 or rows.noise_seed.nunique() != 1:
            raise RuntimeError(f"exogenous seeds vary by policy for {history_id}")
        problems, eps = voc.make_exogenous(task)
        expected = rows.iloc[0]
        p_hash = hashlib.sha256(packed(problems).encode()).hexdigest()
        e_hash = hashlib.sha256(packed(eps).encode()).hexdigest()
        if p_hash != expected.problem_stream_sha256 or e_hash != expected.noise_stream_sha256:
            raise RuntimeError(f"frozen exogenous stream hash mismatch for {history_id}")
        streams[history_id] = (task, problems, eps)

    trace = pd.read_csv(TRAJECTORIES, compression="gzip", dtype={"history_id": str})
    picked = selected[["history_id", "policy", "clock", "state_id"]].drop_duplicates()
    checked = 0
    max_errors = {key: 0.0 for key in ("state_before", "belief_before", "mu_true", "state_after", "belief_after")}
    model, prior = planner.canonical_model(HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR)
    inverse_actions = {c33.ACTION_IDS[action]: action for action in JOINT_ACTIONS}
    for row in picked.itertuples(index=False):
        task, problems, eps = streams[str(row.history_id)]
        factual = trace[(trace.history_id == str(row.history_id)) & (trace.policy == row.policy)].sort_values("clock")
        if len(factual) != 36:
            raise RuntimeError(f"factual trajectory length mismatch for {row.history_id}/{row.policy}")
        state, belief = task["team"], prior
        for actual in factual.itertuples(index=False):
            clock = int(actual.clock)
            if clock > 1 and (clock - 1) % 3 == 0:
                belief = prior
            if clock == int(row.clock):
                logged_s = json.loads(actual.state_before)
                logged_b = json.loads(actual.belief_before)
                err_s = float(np.max(np.abs(np.asarray(state) - np.asarray(logged_s))))
                err_b = float(np.max(np.abs(np.asarray(belief) - np.asarray(logged_b))))
                max_errors["state_before"] = max(max_errors["state_before"], err_s)
                max_errors["belief_before"] = max(max_errors["belief_before"], err_b)
                if not _close(state, logged_s) or not _close(belief, logged_b):
                    raise RuntimeError(f"pre-state replay mismatch at {row.history_id}/{row.policy}/{clock}")
                break
            action = inverse_actions[int(actual.action_id)]
            real = theory._real_decision(state, belief, action,
                                         (problems[(clock - 1) // 3], 1.0 - problems[(clock - 1) // 3]),
                                         float(eps[clock - 1]), model)
            for key, x, y in (("mu_true", real.mu_true, actual.mu_true),
                              ("state_after", real.state_after, json.loads(actual.state_after)),
                              ("belief_after", real.belief_after, json.loads(actual.belief_after))):
                err = float(np.max(np.abs(np.asarray(x, dtype=float) - np.asarray(y, dtype=float))))
                max_errors[key] = max(max_errors[key], err)
                if not _close(x, y):
                    raise RuntimeError(f"real transition replay mismatch {key} at {row.history_id}/{row.policy}/{clock}")
            state, belief = real.state_after, real.belief_after
        checked += 1

    action_equal = 0
    action_rows = []
    for row in selected.itertuples(index=False):
        state = tuple(tuple(float(x) for x in r) for r in json.loads(row.state_before))
        belief = tuple(float(x) for x in json.loads(row.belief_before))
        remaining = int(row.remaining)
        af = fastdeep.choose_fast_action(state, belief, remaining)[0]
        ad = fastdeep.choose_deep_action(state, belief, remaining)[0]
        q00 = planner.choose_prospective_action(state, belief, HYPOTHESIS_REPERTOIRE,
              remaining=remaining, policy_mode=MODE_BY_ID["Q00"], eta=PARAMETERS["eta"])[0]
        q11 = planner.choose_prospective_action(state, belief, HYPOTHESIS_REPERTOIRE,
              remaining=remaining, policy_mode=MODE_BY_ID["Q11"], eta=PARAMETERS["eta"])[0]
        if af != q00 or ad != q11:
            raise RuntimeError(f"FAST/Q00 or DEEP/Q11 action mismatch: {row.state_id}")
        action_equal += int(af == ad)
        action_rows.append({"state_id": row.state_id, "fast_action_id": c33.ACTION_IDS[af],
                            "deep_action_id": c33.ACTION_IDS[ad], "actions_equal": af == ad})
    pd.DataFrame(action_rows).to_csv(OUT / "action_equivalence.csv", index=False)
    return {"selected_states": len(selected), "unique_history_policy_replays": checked,
            "unique_physical_histories_stream_verified": len(streams), "tolerance_atol_rtol": 1e-12,
            "max_abs_replay_errors": max_errors, "fast_q00_deep_q11_actions_verified": len(selected),
            "initial_actions_equal_count": action_equal,
            "action_equivalence_table_sha256": sha(OUT / "action_equivalence.csv")}


def prepare() -> None:
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite existing audit output: {OUT}")
    provenance = verify_frozen_inputs()
    OUT.mkdir(parents=True)
    sample_dir = OUT / "sampling"
    sampling.select(TRAJECTORIES, sample_dir)
    selected = pd.read_csv(sample_dir / "selected_states.csv.gz", compression="gzip")
    # Freeze before target outcomes: exact C4 sampling rule, source hash and 32 MC replicates.
    reconstruction = verify_reconstruction(selected)
    manifest = {
        "protocol": AUDIT_PROTOCOL,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "provenance": provenance,
        "sampling_protocol": "HLS-C4-SAMPLE-v1 reused unchanged; 50 states/domain/block, 4 blocks, 800 total; nonterminal rows only; equal domain sample counts",
        "sampling_manifest_sha256": sha(sample_dir / "sampling_manifest.json"),
        "selected_states_sha256": sha(sample_dir / "selected_states.csv.gz"),
        "sampling_unit": "state sampled by frozen C4 rule; history_id is inference cluster",
        "domains": list(confirmatory.DOMAINS), "states_per_domain": 200, "total_states": 800,
        "monte_carlo_replicates_per_state": MC_REPLICATES,
        "monte_carlo_seed_namespace": AUDIT_RANDOM_NAMESPACE,
        "monte_carlo_seeds": "SHA-256-derived from audit namespace, state_id, replicate, and stream label; separate future-problem and observation streams; disjoint namespace from C3.2 label generation",
        "estimand": "C3.2 Q11 initial action minus Q00 initial action, Q11 continuation in both branches, current problem remainder plus 11 subsequent complete problems; paired raw Monte Carlo delta",
        "counterfactual_semantics": "fresh conditional generator continuation from reconstructed realized prefix; paired same future p sequence and standard-normal epsilon within replicate; observations recomputed from branch-specific mu_true",
        "statistical_plan": {"cluster": "history_id; retain all sampled states within a resampled history", "nested_mc_resampling": "resample M=32 paired replicate deltas within each sampled state", "bootstrap_replicates": BOOTSTRAP_B, "bootstrap_seed": BOOTSTRAP_SEED, "interval": "percentile 95%"},
        "pre_target_validation": reconstruction,
        "execution_command": "python -m experiments.synthetic.meta_voc_predictor_validity.audit --execute --workers 12",
    }
    (OUT / "frozen_sampling_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (OUT / "audit_manifest.sha256").write_text(sha(OUT / "frozen_sampling_manifest.json") + "  frozen_sampling_manifest.json\n")
    print(json.dumps({"prepared": True, "states": len(selected), "domains": selected.domain.value_counts().sort_index().to_dict(),
                      "reconstruction": reconstruction, "manifest_sha256": sha(OUT / "frozen_sampling_manifest.json")}, sort_keys=True))


def _state_inputs(row: dict, model_spec: dict, calibration: dict) -> dict:
    state = tuple(tuple(float(x) for x in r) for r in json.loads(row["state_before"]))
    belief = tuple(float(x) for x in json.loads(row["belief_before"]))
    clock, remaining = int(row["clock"]), int(row["remaining"])
    if remaining not in (2, 3):
        raise ValueError("audit sample must contain nonterminal states only")
    tau = 37 - clock
    costs = {int(k): float(v) for k, v in calibration["predicted_extra_cost_seconds_by_remaining"].items()}
    score, prediction, cost = voc.ex_ante_score(state, belief, tau, model_spec, costs)
    key = voc.feature_tie_key(c33.feature_vector(state, belief, tau))
    invoke = voc.threshold_route(score, key, calibration["thresholds"]["50"])
    return {"state": state, "belief": belief, "clock": clock, "remaining": remaining, "tau": tau,
            "prediction": prediction, "score": score, "predicted_cost": cost, "meta_voc50_deep": bool(invoke)}


def _evaluate_state(payload: dict) -> list[dict]:
    row = payload["row"]
    inp = _state_inputs(row, payload["model"], payload["calibration"])
    task = payload["task"]
    kernel = task["kernel"]
    prefix = c32.realized_prefix(int(task["problem_seed"]), kernel, int(row["problem_index"]) - 1)
    if len(prefix) != int(row["problem_index"]):
        raise RuntimeError("C3.2 physical prefix reconstruction failed")
    actions = {
        "Q00": fastdeep.choose_fast_action(inp["state"], inp["belief"], inp["remaining"])[0],
        "Q11": fastdeep.choose_deep_action(inp["state"], inp["belief"], inp["remaining"])[0],
    }
    output = []
    for rep in range(MC_REPLICATES):
        future_seed = stable_seed(AUDIT_RANDOM_NAMESPACE, row["state_id"], rep, "future")
        noise_seed = stable_seed(AUDIT_RANDOM_NAMESPACE, row["state_id"], rep, "observation")
        future = c32.conditional_future(prefix, kernel, future_seed)
        step = int(row["decision"]) - 1
        eps = tuple(float(x) for x in np.random.default_rng(noise_seed).standard_normal((3 - step) + 3 * c32.ELL))
        if actions["Q00"] == actions["Q11"]:
            q00 = c32.rollout(inp["state"], inp["belief"], prefix[-1], future, eps, step=step,
                              forced_action=actions["Q00"], continuation="Q11")
            q11 = q00
        else:
            q00 = c32.rollout(inp["state"], inp["belief"], prefix[-1], future, eps, step=step,
                              forced_action=actions["Q00"], continuation="Q11")
            q11 = c32.rollout(inp["state"], inp["belief"], prefix[-1], future, eps, step=step,
                              forced_action=actions["Q11"], continuation="Q11")
        output.append({
            "state_id": row["state_id"], "history_id": row["history_id"], "domain": row["domain"],
            "team_id": row["team_id"], "kernel_id": row["kernel_id"], "source_policy": row["policy"],
            "block": int(row["block"]), "clock": inp["clock"], "remaining": inp["remaining"], "tau": inp["tau"],
            "inclusion_probability": float(row["inclusion_probability"]), "sampling_weight": float(row["sampling_weight"]),
            "replicate": rep, "future_seed": future_seed, "noise_seed": noise_seed,
            "future_sha256": hashlib.sha256(packed(future).encode()).hexdigest(),
            "noise_sha256": hashlib.sha256(packed(eps).encode()).hexdigest(),
            "fast_action_id": c33.ACTION_IDS[actions["Q00"]], "deep_action_id": c33.ACTION_IDS[actions["Q11"]],
            "initial_actions_equal": actions["Q00"] == actions["Q11"],
            "prediction_raw_advantage": inp["prediction"], "meta_voc_score": inp["score"],
            "meta_voc50_invokes_deep": inp["meta_voc50_deep"], "predicted_extra_cost": inp["predicted_cost"],
            "raw_mc_G_Q00": q00[0], "raw_mc_G_Q11": q11[0], "delta_Q11_minus_Q00": q11[0] - q00[0],
        })
    return output


def execute(workers: int, batch_size: int) -> None:
    manifest_path = OUT / "frozen_sampling_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("run --prepare before counterfactual execution")
    manifest = json.loads(manifest_path.read_text())
    if manifest["selected_states_sha256"] != sha(OUT / "sampling/selected_states.csv.gz"):
        raise RuntimeError("frozen selected-state file hash mismatch")
    selected = pd.read_csv(OUT / "sampling/selected_states.csv.gz", compression="gzip").sort_values("state_id")
    tasks = {t["history_id"]: t for t in confirmatory.planned_tasks()}
    model_spec = json.loads(MODEL.read_text())
    calibration = json.loads(CALIBRATION.read_text())
    allrows = selected.to_dict("records")
    n_batches = math.ceil(len(allrows) / batch_size)
    pool_context = ProcessPoolExecutor(max_workers=workers) if workers > 1 else None
    try:
        for bi in range(n_batches):
            path = OUT / "raw_batches" / f"batch_{bi:03d}.csv.gz"
            if path.exists():
                continue
            batch = allrows[bi * batch_size:(bi + 1) * batch_size]
            payloads = [{"row": row, "task": tasks[str(row["history_id"])], "model": model_spec,
                         "calibration": calibration} for row in batch]
            start = time.perf_counter()
            if workers == 1:
                generated = [_evaluate_state(p) for p in payloads]
            else:
                generated = list(pool_context.map(_evaluate_state, payloads, chunksize=1))
            flat = [item for group in generated for item in group]
            frame = pd.DataFrame(flat)
            OUT.joinpath("raw_batches").mkdir(exist_ok=True)
            frame.to_csv(path, index=False, compression="gzip")
            print(json.dumps({"batch": bi + 1, "batches": n_batches, "states": len(batch),
                              "mc_rows": len(frame), "elapsed_seconds": round(time.perf_counter() - start, 1),
                              "file_sha256": sha(path)}, sort_keys=True), flush=True)
    finally:
        if pool_context is not None:
            pool_context.shutdown()
    finalize_execution_manifest(workers, batch_size)


def finalize_execution_manifest(workers: int, batch_size: int) -> None:
    files = sorted((OUT / "raw_batches").glob("batch_*.csv.gz"))
    manifest = json.loads((OUT / "frozen_sampling_manifest.json").read_text())
    expected_batches = math.ceil(800 / batch_size)
    if len(files) != expected_batches:
        raise RuntimeError(f"expected {expected_batches} raw batches, found {len(files)}")
    rows = sum(sum(len(chunk) for chunk in pd.read_csv(f, compression="gzip", chunksize=2000)) for f in files)
    if rows != 800 * MC_REPLICATES:
        raise RuntimeError(f"expected {800 * MC_REPLICATES} Monte Carlo pairs, found {rows}")
    result = {"protocol": AUDIT_PROTOCOL, "frozen_sampling_manifest_sha256": sha(OUT / "frozen_sampling_manifest.json"),
              "workers": workers, "batch_size_states": batch_size, "states": 800,
              "paired_mc_replicates_per_state": MC_REPLICATES, "paired_mc_rows": rows,
              "raw_batch_sha256": {p.name: sha(p) for p in files},
              "action_equivalence_sha256": sha(OUT / "action_equivalence.csv"),
              "audit_implementation_sha256": sha(ROOT / "experiments/synthetic/meta_voc_predictor_validity/audit.py"),
              "incident_record_sha256": sha(OUT / "execution_incident.json"),
              "environment": {"python": platform.python_version(), "numpy": np.__version__,
                              "pandas": pd.__version__, "platform": platform.platform(), "cpu_count": os.cpu_count()},
              "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (OUT / "execution_manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


def _weighted_corr(x, y, w):
    x, y, w = np.asarray(x), np.asarray(y), np.asarray(w)
    if len(x) < 2 or w.sum() <= 0:
        return float("nan")
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    cov = np.average((x - mx) * (y - my), weights=w)
    return float(cov / math.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w)))


def _weighted_auc(y, score, w):
    y, score, w = np.asarray(y, dtype=bool), np.asarray(score), np.asarray(w)
    pos, neg = w[y].sum(), w[~y].sum()
    if pos == 0 or neg == 0:
        return float("nan")
    order = np.argsort(score, kind="mergesort")
    y, w = y[order], w[order]
    neg_before = 0.0; concordant = 0.0
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and score[order[j]] == score[order[i]]:
            j += 1
        group_pos, group_neg = w[i:j][y[i:j]].sum(), w[i:j][~y[i:j]].sum()
        concordant += group_pos * (neg_before + 0.5 * group_neg)
        neg_before += group_neg; i = j
    return float(concordant / (pos * neg))


def _metrics(df: pd.DataFrame, target_override=None) -> dict:
    y = np.asarray(df.delta_mean if target_override is None else target_override, dtype=float)
    pred = df.prediction_raw_advantage.to_numpy(float)
    w = df.sampling_weight.to_numpy(float)
    w = w / w.sum()
    positive = y > 0
    predicted_positive = pred >= 0
    invoke = df.meta_voc50_invokes_deep.to_numpy(bool)
    tp = float(w[positive & predicted_positive].sum()); fp = float(w[~positive & predicted_positive].sum())
    fn = float(w[positive & ~predicted_positive].sum()); tn = float(w[~positive & ~predicted_positive].sum())
    sens = tp / (tp + fn) if tp + fn else float("nan")
    spec = tn / (tn + fp) if tn + fp else float("nan")
    precision = tp / (tp + fp) if tp + fp else float("nan")
    route_adv = np.where(invoke, y, 0.0)
    oracle = np.maximum(0.0, y)
    positive_mass = float(w[positive].sum())
    deep_mass = float(w[invoke].sum())
    fast_mass = 1.0 - deep_mass
    return {
        "n_states": int(len(df)), "n_positive_mc_mean": int(positive.sum()),
        "positive_rate_weighted": positive_mass,
        "raw_predictor_positive_rate": float(np.sum(w * predicted_positive)),
        "prediction_bias_pred_minus_mc": float(np.sum(w * (pred - y))),
        "mae": float(np.sum(w * np.abs(pred - y))),
        "rmse": float(np.sqrt(np.sum(w * (pred - y) ** 2))),
        "pearson_weighted": _weighted_corr(pred, y, w),
        "spearman_weighted": _weighted_corr(pd.Series(pred).rank(method="average").to_numpy(), pd.Series(y).rank(method="average").to_numpy(), w),
        "sensitivity": sens, "specificity": spec, "precision": precision,
        "balanced_accuracy": float((sens + spec) / 2) if np.isfinite(sens) and np.isfinite(spec) else float("nan"),
        "roc_auc": _weighted_auc(positive, pred, w),
        "meta_voc50_invocation_rate_weighted": deep_mass,
        "mean_delta_if_meta_invokes_deep": float(np.average(y[invoke], weights=w[invoke])) if invoke.any() else float("nan"),
        "mean_delta_if_meta_accepts_fast": float(np.average(y[~invoke], weights=w[~invoke])) if (~invoke).any() else float("nan"),
        "missed_positive_state_rate_of_positive": float(w[positive & ~invoke].sum() / positive_mass) if positive_mass else float("nan"),
        "missed_positive_advantage_weighted": float(np.sum(w[positive & ~invoke] * y[positive & ~invoke])),
        "unproductive_deep_rate_of_deep": float(w[invoke & ~positive].sum() / deep_mass) if deep_mass else float("nan"),
        "mean_policy_advantage_vs_fast": float(np.sum(w * route_adv)),
        "mean_performance_oracle_advantage_vs_fast": float(np.sum(w * oracle)),
        "performance_only_oracle_regret": float(np.sum(w * (oracle - route_adv))),
        "mean_mc_standard_error": float(np.average(df.mc_se.to_numpy(float), weights=w)),
        "fraction_state_mc_ci_spans_zero": float(np.average(df.mc_ci_spans_zero.to_numpy(float), weights=w)),
        "fraction_state_mc_ci_positive": float(np.average((y - 1.96 * df.mc_se.to_numpy(float) > 0).astype(float), weights=w)),
        "fraction_state_mc_ci_negative": float(np.average((y + 1.96 * df.mc_se.to_numpy(float) < 0).astype(float), weights=w)),
    }


def analyze() -> None:
    execution_path = OUT / "execution_manifest.json"
    if not execution_path.is_file():
        raise RuntimeError("complete execution required before analysis")
    files = sorted((OUT / "raw_batches").glob("batch_*.csv.gz"))
    raw = pd.concat([pd.read_csv(p, compression="gzip") for p in files], ignore_index=True)
    if len(raw) != 800 * MC_REPLICATES or raw.groupby("state_id").size().ne(MC_REPLICATES).any():
        raise RuntimeError("raw Monte Carlo output incomplete or duplicated")
    selected_ids = set(pd.read_csv(OUT / "sampling/selected_states.csv.gz", compression="gzip").state_id.astype(str))
    if set(raw.state_id.astype(str)) != selected_ids or raw.duplicated(["state_id", "replicate"]).any():
        raise RuntimeError("raw state/replicate keys do not exactly match the frozen allocation")
    if any(set(g.replicate.astype(int)) != set(range(MC_REPLICATES)) for _, g in raw.groupby("state_id")):
        raise RuntimeError("replicate indices are incomplete or duplicated")
    state = raw.groupby("state_id", sort=False).agg(
        history_id=("history_id", "first"), domain=("domain", "first"), team_id=("team_id", "first"),
        kernel_id=("kernel_id", "first"), source_policy=("source_policy", "first"), block=("block", "first"),
        clock=("clock", "first"), remaining=("remaining", "first"), tau=("tau", "first"),
        inclusion_probability=("inclusion_probability", "first"), sampling_weight=("sampling_weight", "first"),
        prediction_raw_advantage=("prediction_raw_advantage", "first"), meta_voc_score=("meta_voc_score", "first"),
        meta_voc50_invokes_deep=("meta_voc50_invokes_deep", "first"), predicted_extra_cost=("predicted_extra_cost", "first"),
        fast_action_id=("fast_action_id", "first"), deep_action_id=("deep_action_id", "first"),
        initial_actions_equal=("initial_actions_equal", "first"),
    ).reset_index()
    means = raw.groupby("state_id").delta_Q11_minus_Q00.mean()
    sds = raw.groupby("state_id").delta_Q11_minus_Q00.std(ddof=1)
    state["delta_mean"] = state.state_id.map(means)
    state["delta_mc_sd"] = state.state_id.map(sds)
    state["mc_se"] = state.delta_mc_sd / np.sqrt(MC_REPLICATES)
    state["mc_ci_lower"] = state.delta_mean - 1.96 * state.mc_se
    state["mc_ci_upper"] = state.delta_mean + 1.96 * state.mc_se
    state["mc_ci_spans_zero"] = ((state.delta_mean - 1.96 * state.mc_se <= 0) & (state.delta_mean + 1.96 * state.mc_se >= 0)).astype(int)
    state.to_csv(OUT / "state_estimates.csv", index=False)
    raw.to_csv(OUT / "paired_mc_replicates.csv.gz", index=False, compression="gzip")

    summary = {"pooled_equal_domain_macro": _metrics(pd.concat([
        state[state.domain == d].assign(sampling_weight=lambda x: x.sampling_weight / x.sampling_weight.sum() / 4)
        for d in confirmatory.DOMAINS], ignore_index=True))}
    for domain in confirmatory.DOMAINS:
        summary[domain] = _metrics(state[state.domain == domain])

    # Weighted calibration bins: ten equal-weight bins of the predictor, per domain and macro-pool.
    bins = []
    for domain in (*confirmatory.DOMAINS, "POOLED_EQUAL_DOMAIN"):
        frame = state if domain == "POOLED_EQUAL_DOMAIN" else state[state.domain == domain]
        weights = frame.sampling_weight.to_numpy(float)
        order = np.argsort(frame.prediction_raw_advantage.to_numpy(float), kind="mergesort")
        cumulative = np.cumsum(weights[order]) / weights.sum()
        labels = np.minimum((cumulative * 10).astype(int), 9)
        tmp = frame.iloc[order].copy(); tmp["bin"] = labels
        for b, part in tmp.groupby("bin"):
            bins.append({"domain": domain, "bin": int(b) + 1, "n": len(part),
                         "mean_prediction": float(np.average(part.prediction_raw_advantage, weights=part.sampling_weight)),
                         "mean_mc_advantage": float(np.average(part.delta_mean, weights=part.sampling_weight)),
                         "mean_mc_se": float(np.average(part.mc_se, weights=part.sampling_weight))})
    pd.DataFrame(bins).to_csv(OUT / "calibration_bins.csv", index=False)

    # History-cluster bootstrap, stratified by domain; MC replicates resampled inside each state.
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    boot_rows = []
    by_domain = {d: state[state.domain == d].copy() for d in confirmatory.DOMAINS}
    hist_frames = {d: {h: f for h, f in part.groupby("history_id", sort=False)} for d, part in by_domain.items()}
    raw_by_state = {s: g.delta_Q11_minus_Q00.to_numpy(float) for s, g in raw.groupby("state_id", sort=False)}
    def resampled_domain(d):
        hmap = hist_frames[d]
        ids = list(hmap)
        chosen = rng.choice(ids, size=len(ids), replace=True)
        chunks = []
        for h in chosen:
            f = hmap[h].copy()
            # A selected history contributes every sampled state; resample MC rows within each state.
            vals = []
            for sid in f.state_id:
                a = raw_by_state[sid]
                vals.append(float(np.mean(a[rng.integers(0, len(a), size=len(a))])))
            f["delta_mean"] = vals
            chunks.append(f)
        return pd.concat(chunks, ignore_index=True)
    for b in range(BOOTSTRAP_B):
        boot_domains = {d: resampled_domain(d) for d in confirmatory.DOMAINS}
        for d, frame in boot_domains.items():
            boot_rows.append({"bootstrap": b, "domain": d, **_metrics(frame)})
        macro = pd.concat([frame.assign(sampling_weight=lambda x: x.sampling_weight / x.sampling_weight.sum() / 4)
                           for frame in boot_domains.values()], ignore_index=True)
        boot_rows.append({"bootstrap": b, "domain": "POOLED_EQUAL_DOMAIN", **_metrics(macro)})
    boot = pd.DataFrame(boot_rows)
    boot.to_csv(OUT / "bootstrap_metrics.csv.gz", index=False, compression="gzip")
    ci_rows = []
    metric_names = [c for c in boot.columns if c not in ("bootstrap", "domain", "n_states", "n_positive_mc_mean")]
    for (domain, metric), group in boot.melt(id_vars=["bootstrap", "domain"], value_vars=metric_names,
                                             var_name="metric", value_name="value").groupby(["domain", "metric"]):
        values = group.value.dropna().to_numpy(float)
        ci_rows.append({"domain": domain, "metric": metric, "defined_bootstrap_replicates": int(len(values)),
                        "undefined_bootstrap_replicates": int(BOOTSTRAP_B - len(values)),
                        "ci95_low": float(np.quantile(values, .025)) if len(values) else None,
                        "ci95_high": float(np.quantile(values, .975)) if len(values) else None})
    pd.DataFrame(ci_rows).to_csv(OUT / "bootstrap_intervals.csv", index=False)
    paired_routes = []
    for domain in (*confirmatory.DOMAINS, "POOLED_EQUAL_DOMAIN"):
        point = summary["pooled_equal_domain_macro"] if domain == "POOLED_EQUAL_DOMAIN" else summary[domain]
        draws = boot[boot.domain == domain].pivot(index="bootstrap", columns="domain") if False else None
        subset = boot[boot.domain == domain].set_index("bootstrap")
        contrast = (subset["mean_delta_if_meta_invokes_deep"] - subset["mean_delta_if_meta_accepts_fast"]).dropna()
        paired_routes.append({
            "domain": domain,
            "point_mean_deep_routed_minus_fast_routed_advantage": point["mean_delta_if_meta_invokes_deep"] - point["mean_delta_if_meta_accepts_fast"],
            "ci95_low": float(contrast.quantile(.025)), "ci95_high": float(contrast.quantile(.975)),
            "defined_bootstrap_replicates": int(len(contrast)),
        })
    pd.DataFrame(paired_routes).to_csv(OUT / "route_selection_contrast.csv", index=False)
    (OUT / "validity_summary.json").write_text(json.dumps({
        "protocol": AUDIT_PROTOCOL, "estimand": "C3.2-matched paired MC advantage under Q11 continuation",
        "point_estimates": summary, "bootstrap": {"B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                       "cluster": "history_id, stratified by domain; all states retained", "nested_mc": "resample 32 paired deltas within each state"},
        "classification_definition": "predictor positivity uses frozen raw Ridge prediction >=0; target positivity uses per-state M=32 Monte Carlo mean >0; META routing uses unchanged frozen score, cost, threshold, and SHA tie rule",
        "oracle_definition": "nondeployable performance-only oracle chooses DEEP iff estimated expected production advantage >0; does not account for computation cost",
        "limitations": ["single sampled state per source/history/block design; finite confirmatory histories", "32 Monte Carlo replicates estimate a noisy conditional mean", "state labels are Monte Carlo estimates, not ground-truth oracle values", "cost-adjusted routing utility is not inferred from positive physical advantage"],
    }, indent=2, sort_keys=True) + "\n")
    (OUT / "analysis_manifest.json").write_text(json.dumps({
        "protocol": AUDIT_PROTOCOL, "analysis_source_sha256": sha(ROOT / "experiments/synthetic/meta_voc_predictor_validity/audit.py"),
        "execution_manifest_sha256": sha(execution_path), "state_estimates_sha256": sha(OUT / "state_estimates.csv"),
        "paired_mc_replicates_sha256": sha(OUT / "paired_mc_replicates.csv.gz"),
        "bootstrap_metrics_sha256": sha(OUT / "bootstrap_metrics.csv.gz"), "bootstrap_intervals_sha256": sha(OUT / "bootstrap_intervals.csv"),
        "route_selection_contrast_sha256": sha(OUT / "route_selection_contrast.csv"),
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=2, sort_keys=True) + "\n")
    outputs = [p for p in OUT.rglob("*") if p.is_file() and p.name not in ("derived_hashes.json",)]
    (OUT / "derived_hashes.json").write_text(json.dumps({str(p.relative_to(OUT)): sha(p) for p in sorted(outputs)}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"analysis_complete": True, "summary": summary, "outputs_hashed": len(outputs)}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    if sum((args.prepare, args.execute, args.analyze)) != 1:
        parser.error("choose exactly one of --prepare, --execute, --analyze")
    if args.prepare:
        prepare()
    elif args.execute:
        if args.workers < 1 or args.batch_size < 1:
            parser.error("workers and batch-size must be positive")
        execute(args.workers, args.batch_size)
    else:
        analyze()


if __name__ == "__main__":
    main()
