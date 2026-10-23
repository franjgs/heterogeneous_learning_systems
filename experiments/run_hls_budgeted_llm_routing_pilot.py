"""Reproducible, offline MMLU pilot for shared-budget LLM routing.

The xRouteBench license could not be established from its published metadata,
so this pilot uses MIT-licensed MMLU questions and Apache-2.0 model weights.
It generates candidate outcomes locally; inference wall time is the resource
cost proxy. Outputs are test-only diagnostics, not deployed service costs.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import os
import platform
import re
import sys
import subprocess
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import transformers
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hls.experiment_contract import (  # noqa: E402
    ExperimentEvent, ExperimentRun, MetricValue, SeedRecord, UnitDeclaration,
)
from hls.llm_routing_pilot import (  # noqa: E402
    MODEL_IDS, MIRTQualityPredictor, apply_latency, budget_between_extremes,
    fixed_model, greedy_feasible, independent_with_repair,
    predict_latency, retrospective_oracle, score_assignment, solve_batch_ilp,
)
from hls.performance_evaluation import (  # noqa: E402
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator,
)


DATASET_ID = "cais/mmlu"
DATASET_REVISION = "c30699e8356da336a370243923dbaf21066bb9fe"
MODEL_REVISIONS = {
    "HuggingFaceTB/SmolLM2-360M-Instruct": "a10cc1512eabd3dde888204e902eca88bddb4951",
    "Qwen/Qwen2.5-0.5B-Instruct": "7ae557604adf67be50417f59c2c2f167def9a775",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct": "31b70e2e869a7173562077fd711b654946d38674",
}
TRAIN_SEED = 20261023
TEST_SEED = 20261024
PACKING_SEEDS = tuple(range(20261101, 20261121))
TEST_SUBJECTS = (
    "high_school_biology",
    "high_school_mathematics",
    "high_school_us_history",
    "high_school_psychology",
)
TRAIN_QUERIES = 200
TEST_PER_SUBJECT = 40
BATCH_SIZE = 10
BUDGET_FRACTIONS = (0.35, 0.70)
POLICY_IDS = (
    "independent_repaired", "greedy_feasible", "batch_ilp",
    "fixed_economic", "fixed_quality", "test_oracle",
)
OUT = ROOT / "results/experiments/hls_budgeted_llm_routing_pilot"


def _qid(split: str, subject: str, row_index: int, question: str, choices: list[str]) -> str:
    source = json.dumps([split, subject, int(row_index), question, choices], ensure_ascii=False)
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:20]


def _download_frame(path: str) -> pd.DataFrame:
    local = hf_hub_download(DATASET_ID, path, repo_type="dataset", revision=DATASET_REVISION)
    return pd.read_parquet(local)


def load_pilot_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = _download_frame("all/auxiliary_train-00000-of-00001.parquet")
    test = _download_frame("all/test-00000-of-00001.parquet")
    train = train.sample(n=TRAIN_QUERIES, random_state=TRAIN_SEED).reset_index(drop=False)
    train = train.rename(columns={"index": "source_index"})
    train["split"] = "auxiliary_train"
    train["query_id"] = [
        _qid("auxiliary_train", "mixed", row.source_index, row.question, list(row.choices))
        for row in train.itertuples()
    ]
    train["task_type"] = "mmlu_auxiliary_mixed"
    test_rows = []
    for subject in TEST_SUBJECTS:
        group = test[test.subject == subject]
        if len(group) < TEST_PER_SUBJECT:
            raise ValueError(f"official MMLU test subject too small: {subject}")
        group = group.sample(n=TEST_PER_SUBJECT, random_state=TEST_SEED).reset_index(drop=False)
        group = group.rename(columns={"index": "source_index"})
        group["split"] = "test"
        group["query_id"] = [
            _qid("test", subject, row.source_index, row.question, list(row.choices))
            for row in group.itertuples()
        ]
        group["task_type"] = subject
        test_rows.append(group)
    return train, pd.concat(test_rows, ignore_index=True)


def make_prompt(question: str, choices: list[str]) -> str:
    letters = "ABCD"
    options = "\n".join(f"{letters[i]}. {choice}" for i, choice in enumerate(choices[:4]))
    user = f"Choose the single best answer. Reply with its letter only.\nQuestion: {question}\n{options}"
    return user


def request_features(frame: pd.DataFrame) -> list[str]:
    return [make_prompt(row.question, list(row.choices))
            for row in frame.itertuples()]


def parse_answer(text: str) -> str | None:
    match = re.match(r"^\s*(?:the\s+)?(?:answer\s*(?:is|:)?\s*)?[\[(]?([ABCD])\b", text, re.I)
    if match:
        return match.group(1).upper()
    match = re.search(r"\b(?:answer\s*(?:is|:)|option)\s*[\[(]?([ABCD])\b", text, re.I)
    return match.group(1).upper() if match else None


def _device() -> str:
    return "mps" if torch.backends.mps.is_available() else "cpu"


def generate_outcomes(train: pd.DataFrame, test: pd.DataFrame, out_dir: Path) -> pd.DataFrame:
    cache_path = out_dir / "model_outcomes.csv"
    required = {"query_id", "model_id", "model_revision", "predicted_letter", "correct",
                "input_tokens", "output_tokens", "latency_seconds", "split", "task_type"}
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        if required.issubset(cached.columns) and set(cached.model_id.unique()) == set(MODEL_IDS):
            expected = len(MODEL_IDS) * (len(train) + len(test))
            if len(cached) == expected and set(cached.model_revision.unique()) == set(MODEL_REVISIONS.values()):
                return cached
    device = _device()
    records: list[dict[str, Any]] = []
    cached_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    if cache_path.exists():
        for record in pd.read_csv(cache_path).to_dict("records"):
            if record.get("model_revision") in MODEL_REVISIONS.values():
                cached_lookup[(record["query_id"], record["model_id"])] = record
    all_queries = pd.concat([train, test], ignore_index=True)
    for model_id in MODEL_IDS:
        revision = MODEL_REVISIONS[model_id]
        missing = [row for row in all_queries.itertuples()
                   if (row.query_id, model_id) not in cached_lookup]
        if missing:
            tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
            model = AutoModelForCausalLM.from_pretrained(
                model_id, revision=revision, torch_dtype=torch.float16,
                low_cpu_mem_usage=False,
            ).to(device)
            model.eval()
            for index, row in enumerate(missing):
                prompt = make_prompt(row.question, list(row.choices))
                messages = [{"role": "user", "content": prompt}]
                if getattr(tokenizer, "chat_template", None):
                    encoded = tokenizer.apply_chat_template(
                        messages, tokenize=True, add_generation_prompt=True,
                        return_tensors="pt", return_dict=True,
                    )
                else:
                    encoded = tokenizer(prompt, return_tensors="pt")
                encoded = {key: value.to(device) for key, value in encoded.items()}
                start = time.perf_counter()
                with torch.inference_mode():
                    generated = model.generate(
                        **encoded, do_sample=False, max_new_tokens=8,
                        pad_token_id=tokenizer.eos_token_id,
                        temperature=1.0, top_p=1.0, top_k=50,
                    )
                    if device == "mps":
                        torch.mps.synchronize()
                latency = time.perf_counter() - start
                new_tokens = generated[0, encoded["input_ids"].shape[1]:]
                text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                letter = parse_answer(text)
                answer = int(row.answer)
                correct = letter == "ABCD"[answer]
                record = {
                    "query_id": row.query_id, "model_id": model_id,
                    "model_revision": revision, "predicted_letter": letter or "",
                    "correct": int(correct), "input_tokens": int(encoded["input_ids"].shape[1]),
                    "output_tokens": int(len(new_tokens)), "latency_seconds": latency,
                    "split": row.split, "task_type": row.task_type,
                }
                cached_lookup[(row.query_id, model_id)] = record
                if index % 25 == 0:
                    pd.DataFrame(cached_lookup.values()).to_csv(cache_path, index=False)
            del model, tokenizer
            gc.collect()
            if device == "mps":
                torch.mps.empty_cache()
        records.extend(cached_lookup[(row.query_id, model_id)] for row in all_queries.itertuples())
        pd.DataFrame(records).drop_duplicates(["query_id", "model_id"]).to_csv(cache_path, index=False)
    return pd.read_csv(cache_path)


def matrix_for(frame: pd.DataFrame, outcomes: pd.DataFrame, column: str) -> np.ndarray:
    lookup = outcomes.pivot(index="query_id", columns="model_id", values=column)
    return lookup.loc[frame.query_id, list(MODEL_IDS)].to_numpy(dtype=float)


def make_batchings(test: pd.DataFrame, seed: int) -> dict[str, list[np.ndarray]]:
    rng = np.random.default_rng(seed)
    homogeneous: list[np.ndarray] = []
    pools = {}
    for subject in TEST_SUBJECTS:
        ids = test.index[test.task_type == subject].to_numpy()
        ids = rng.permutation(ids)
        pools[subject] = [ids[i:i + BATCH_SIZE] for i in range(0, len(ids), BATCH_SIZE)]
        homogeneous.extend(pools[subject])
    # Each mixed batch gets 2 queries from every task and 2 balanced extras.
    per_subject = {subject: rng.permutation(test.index[test.task_type == subject].to_numpy())
                   for subject in TEST_SUBJECTS}
    positions = {subject: 0 for subject in TEST_SUBJECTS}
    extra_counts = {subject: 0 for subject in TEST_SUBJECTS}
    heterogeneous: list[np.ndarray] = []
    for _ in range(len(test) // BATCH_SIZE):
        extras = sorted(TEST_SUBJECTS, key=lambda subject: (extra_counts[subject], rng.random()))[:2]
        batch = []
        for subject in TEST_SUBJECTS:
            count = 2 + int(subject in extras)
            extra_counts[subject] += int(subject in extras)
            start = positions[subject]
            batch.extend(per_subject[subject][start:start + count].tolist())
            positions[subject] += count
        heterogeneous.append(np.asarray(batch, dtype=int))
    if any(position != TEST_PER_SUBJECT for position in positions.values()):
        raise AssertionError("heterogeneous batching did not use each test query exactly once")
    return {"homogeneous": homogeneous, "heterogeneous": heterogeneous}


def _lambda_for_budget(q: np.ndarray, c: np.ndarray, fraction: float) -> float:
    target = float(np.mean(c.min(axis=1) + fraction * (c.max(axis=1) - c.min(axis=1))))
    grid = np.r_[0.0, np.geomspace(1e-4, 1e5, 160)]
    best = (float("inf"), 0.0)
    for price in grid:
        choice = np.argmax(q - price * c, axis=1)
        spend = float(c[np.arange(len(choice)), choice].mean())
        candidate = (abs(spend - target), float(price))
        if candidate < best:
            best = candidate
    return best[1]


def _policy_choices(qhat: np.ndarray, costs: np.ndarray,
                    budget: float, lam: float, fixed_economic: int,
                    fixed_quality: int) -> dict[str, np.ndarray]:
    return {
        "independent_repaired": independent_with_repair(qhat, costs, budget, lam),
        "greedy_feasible": greedy_feasible(qhat, costs, budget),
        "batch_ilp": solve_batch_ilp(qhat, costs, budget),
        "fixed_economic": fixed_model(qhat, costs, fixed_economic),
        "fixed_quality": fixed_model(qhat, costs, fixed_quality),
    }


def _make_profile(profile_id: str, condition: str, budget_fraction: float,
                  policy_ids: tuple[str, ...], n: int) -> EvaluationProfile:
    objectives = {
        "independent_repaired": "per-query MIRT quality-cost score; repair to shared budget",
        "greedy_feasible": "greedy predicted-quality upgrades under shared budget",
        "batch_ilp": "maximize summed MIRT predicted correctness under shared budget",
        "fixed_economic": "use cheapest model selected on training inference times",
        "fixed_quality": "use highest-training-accuracy model for every query",
        "test_oracle": "maximize realized held-out correctness retrospectively; not deployable",
    }
    return EvaluationProfile(
        profile_id=profile_id, scenario_id="mmlu_mit_pilot_v1",
        configuration_id=f"{condition}-n{n}-budget-frac{budget_fraction:.2f}",
        application_domain="local open-weight language models",
        organizational_problem="single-model query assignment under shared batch inference-time budget",
        decision_objective={p: objectives[p] for p in policy_ids},
        constraints="one model per query; sum predicted local inference seconds <= batch budget",
        primary_metrics=("functional_success_rate", "original_reward_cumulative"),
        secondary_metrics=("resource_usage:inference_latency_seconds",),
        information_regime="MMLU auxiliary_train fit/calibration; test query text and subject observed; test outcomes hidden except retrospective oracle",
        temporal_horizon=n, aggregation_rules="one MMLU test query per period; correctness is exact answer-letter match",
        demand_distribution_id=f"mmlu-four-subjects-{condition}-seeded",
        resource_units={"inference_latency_seconds": "seconds"},
    )


def run_pilot(out_dir: Path = OUT) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(TRAIN_SEED)
    try:
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                  check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_head = None
    source_paths = (
        ROOT / "experiments/run_hls_budgeted_llm_routing_pilot.py",
        ROOT / "src/hls/llm_routing_pilot.py",
        ROOT / "src/hls/experiment_contract.py",
        ROOT / "src/hls/performance_evaluation.py",
    )
    source_hashes = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }
    try:
        working_tree_dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        working_tree_dirty = None
    train, test = load_pilot_data()
    outcomes = generate_outcomes(train, test, out_dir)
    fit_n = int(len(train) * 0.8)
    rng = np.random.default_rng(TRAIN_SEED + 1)
    train_order = rng.permutation(len(train))
    fit_frame = train.iloc[train_order[:fit_n]].reset_index(drop=True)
    calibration_frame = train.iloc[train_order[fit_n:]].reset_index(drop=True)
    fit_y = matrix_for(fit_frame, outcomes, "correct")
    predictor = MIRTQualityPredictor(seed=TRAIN_SEED).fit(
        request_features(fit_frame), MODEL_IDS, fit_y,
    )
    qhat_test = predictor.predict(request_features(test))
    qhat_cal = predictor.predict(request_features(calibration_frame))
    qtrue_test = matrix_for(test, outcomes, "correct")
    tokens_fit = matrix_for(fit_frame, outcomes, "input_tokens")
    latency_fit = matrix_for(fit_frame, outcomes, "latency_seconds")
    latency_coeff = predict_latency(tokens_fit, latency_fit)
    cost_cal = apply_latency(matrix_for(calibration_frame, outcomes, "input_tokens"), latency_coeff)
    fixed_economic = int(np.argmin(latency_fit.mean(axis=0)))
    fixed_quality = int(np.argmax(fit_y.mean(axis=0)))
    lambda_by_fraction = {fraction: _lambda_for_budget(qhat_cal, cost_cal, fraction)
                          for fraction in BUDGET_FRACTIONS}
    latency_test = matrix_for(test, outcomes, "latency_seconds")
    costs_test = apply_latency(matrix_for(test, outcomes, "input_tokens"), latency_coeff)
    pd.DataFrame([
        {"query_id": test.iloc[i].query_id, "task_type": test.iloc[i].task_type,
         "model_id": model, "predicted_quality": float(qhat_test[i, m]),
         "predicted_cost_seconds": float(costs_test[i, m])}
        for i in range(len(test)) for m, model in enumerate(MODEL_IDS)
    ]).to_csv(out_dir / "quality_cost_predictions.csv", index=False)
    evaluator = PerformanceEvaluator()
    run_objects: list[ExperimentRun] = []
    assignment_rows: list[dict[str, Any]] = []
    seed_summary_rows: list[dict[str, Any]] = []

    for seed in PACKING_SEEDS:
        for condition, batches in make_batchings(test, seed).items():
            for fraction in BUDGET_FRACTIONS:
                profile_id = f"mmlu-{condition}-{fraction:.2f}-seed{seed}"
                profile = _make_profile(profile_id, condition, fraction, POLICY_IDS, len(test))
                evaluator.register_profile(profile)
                query_records: dict[str, list[EvaluationRecord]] = {policy: [] for policy in POLICY_IDS}
                policy_batch_metrics: dict[str, list[dict[str, float]]] = {policy: [] for policy in POLICY_IDS}
                sequence = 0
                for batch_num, indices in enumerate(batches):
                    q = qhat_test[indices]
                    qt = qtrue_test[indices]
                    c = costs_test[indices]
                    actual_latency = latency_test[indices]
                    budget = budget_between_extremes(c, fraction)
                    choices = _policy_choices(q, c, budget, lambda_by_fraction[fraction],
                                              fixed_economic, fixed_quality)
                    # Held-out outcomes enter only this retrospective bound.
                    choices["test_oracle"] = retrospective_oracle(qt, c, budget)
                    for policy_id, selected in choices.items():
                        metric = score_assignment(selected, qt, c, actual_latency, budget)
                        if policy_id != "fixed_quality" and not metric.budget_compliant_estimated:
                            raise AssertionError(f"{policy_id} exceeded predicted batch budget")
                        policy_batch_metrics[policy_id].append({
                            "accuracy": metric.accuracy,
                            "estimated_cost_seconds": metric.cost_estimated_seconds,
                            "observed_latency_seconds": metric.latency_observed_seconds,
                            "budget_seconds": metric.budget_seconds,
                            "estimated_compliant": float(metric.budget_compliant_estimated),
                            "observed_compliant": float(metric.budget_compliant_observed),
                        })
                        for local_i, query_index in enumerate(indices):
                            model_index = int(selected[local_i])
                            correct = int(qt[local_i, model_index])
                            latency = float(actual_latency[local_i, model_index])
                            record = EvaluationRecord(
                                scenario_id=profile.scenario_id,
                                configuration_id=profile.configuration_id,
                                policy_id=policy_id, period=sequence + local_i,
                                demand=str(test.iloc[query_index].task_type),
                                success=bool(correct), original_reward=float(correct),
                                resource_usage={"inference_latency_seconds": latency},
                                quality=float(correct), task_type=str(test.iloc[query_index].task_type),
                                provenance=f"cais/mmlu@{DATASET_REVISION}#test:{test.iloc[query_index].query_id}:{MODEL_IDS[model_index]}:{seed}",
                                unit_id=str(test.iloc[query_index].query_id),
                                information_regime=profile.information_regime,
                                decision_objective=profile.decision_objective[policy_id],
                                available_metadata={
                                    "model_id": MODEL_IDS[model_index], "batch_index": batch_num,
                                    "predicted_quality": float(q[local_i, model_index]),
                                    "predicted_cost_seconds": float(c[local_i, model_index]),
                                    "budget_seconds": budget,
                                },
                            )
                            query_records[policy_id].append(record)
                            assignment_rows.append({
                                "packing_seed": seed, "condition": condition,
                                "budget_fraction": fraction, "batch_index": batch_num,
                                "query_id": test.iloc[query_index].query_id,
                                "task_type": test.iloc[query_index].task_type,
                                "policy_id": policy_id, "model_id": MODEL_IDS[model_index],
                                "correct": correct,
                                "predicted_quality": float(q[local_i, model_index]),
                                "predicted_cost_seconds": float(c[local_i, model_index]),
                                "observed_latency_seconds": latency,
                                "batch_budget_seconds": budget,
                            })
                    sequence += len(indices)
                for policy_id in POLICY_IDS:
                    eval_results = evaluator.evaluate(profile_id, policy_id, query_records[policy_id])
                    batch_metrics = policy_batch_metrics[policy_id]
                    acc = float(np.mean([x["accuracy"] for x in batch_metrics]))
                    estimated_cost = float(np.mean([x["estimated_cost_seconds"] for x in batch_metrics]))
                    observed_latency_total = float(np.mean([x["observed_latency_seconds"] for x in batch_metrics]))
                    budget_avg = float(np.mean([x["budget_seconds"] for x in batch_metrics]))
                    compliant_est = float(np.mean([x["estimated_compliant"] for x in batch_metrics]))
                    compliant_obs = float(np.mean([x["observed_compliant"] for x in batch_metrics]))
                    by_task = {}
                    for task in TEST_SUBJECTS:
                        values = [r.success for r in query_records[policy_id] if r.task_type == task]
                        by_task[task] = float(np.mean(values))
                    seed_summary_rows.append({
                        "packing_seed": seed, "condition": condition,
                        "budget_fraction": fraction, "policy_id": policy_id,
                        "accuracy": acc, "estimated_cost_seconds": estimated_cost,
                        "observed_latency_seconds": observed_latency_total,
                        "budget_seconds": budget_avg,
                        "estimated_budget_compliance": compliant_est,
                        "observed_latency_budget_compliance": compliant_obs,
                        **{f"accuracy:{task}": value for task, value in by_task.items()},
                    })
                    events = tuple(
                        ExperimentEvent(
                            sequence_index=i, event_type="batch_assignment_summary",
                            mechanism_id=policy_id, time_index=i,
                            data={"batch_index": i, **metrics},
                        ) for i, metrics in enumerate(batch_metrics)
                    )
                    metrics = tuple(MetricValue(
                        name=name, value=float(result.value), unit=result.unit,
                        interpretation=result.definition_id,
                        preferred_direction="higher" if name != "resource_usage:inference_latency_seconds" else "lower",
                    ) for name, result in eval_results.items() if result.value is not None)
                    run_objects.append(ExperimentRun(
                        schema_version="hls-experiment-run/1.0",
                        run_id=f"mmlu-{condition}-b{fraction:.2f}-{policy_id}-seed{seed}",
                        mechanism_id=policy_id, policy_id=policy_id,
                        configuration={
                            "scenario_id": profile.scenario_id,
                            "configuration_id": profile.configuration_id,
                            "problem": "one model per query with shared batch latency budget",
                            "model_ids": list(MODEL_IDS), "batch_size": BATCH_SIZE,
                            "batch_condition": condition, "budget_fraction": fraction,
                            "quality_predictor": "MIRT content-conditioned Bernoulli response model",
                            "cost_predictor": "per-model affine input-token to local latency regression",
                            "dataset_split": "official MMLU test subset",
                        },
                        initial_conditions={"test_queries": len(test), "test_subjects": list(TEST_SUBJECTS)},
                        random_seeds=(
                            SeedRecord("train_sample", TRAIN_SEED, "select auxiliary_train queries"),
                            SeedRecord("test_sample", TEST_SEED, "select official test queries"),
                            SeedRecord("packing", seed, "paired batch packing"),
                        ),
                        information_available={
                            "query_text": "available", "task_type": "available",
                            "training_outcomes": "auxiliary_train only",
                            "test_outcomes": "hidden except retrospective oracle",
                        },
                        observation_model={"stochastic_generation": False,
                                           "decoding": "greedy; max_new_tokens=8",
                                           "device": _device()},
                        software_revision=git_head,
                        units=(
                            UnitDeclaration("accuracy", "fraction", "MMLU exact answer-letter match"),
                            UnitDeclaration("inference_latency", "seconds", "observed local per-query wall time"),
                        ),
                        events=events, metrics=metrics,
                        mechanism_results={
                            "profile_evaluation": {k: v.to_dict() if hasattr(v, "to_dict") else {
                                "value": v.value, "unit": v.unit, "status": v.status.value,
                                "definition_id": v.definition_id, "aggregation": v.aggregation,
                            } for k, v in eval_results.items()},
                            "per_task_accuracy": by_task,
                            "accuracy_mirt_brier_test": float(np.mean((qhat_test - qtrue_test) ** 2)),
                        },
                        metadata={
                            "evaluation_profile_id": profile_id,
                            "data_provenance": f"{DATASET_ID}@{DATASET_REVISION}",
                            "model_revisions": MODEL_REVISIONS,
                            "git_head": git_head,
                            "working_tree_dirty_at_run": working_tree_dirty,
                            "source_hashes_sha256": source_hashes,
                            "policy_role": "executable policy" if policy_id != "test_oracle" else "retrospective upper bound",
                            "license": "MMLU MIT; model weights Apache-2.0",
                            "cost_semantics": "local measured inference seconds; not monetary cloud cost",
                        },
                    ))
    assignment_frame = pd.DataFrame(assignment_rows)
    summary_frame = pd.DataFrame(seed_summary_rows)
    expected_assignment_count = (len(PACKING_SEEDS) * 2 * len(BUDGET_FRACTIONS)
                                 * len(POLICY_IDS) * len(test))
    if len(assignment_frame) != expected_assignment_count:
        raise AssertionError("assignment trace row count does not match declared design")
    counts = assignment_frame.groupby(
        ["packing_seed", "condition", "budget_fraction", "policy_id"], sort=False
    ).query_id.agg(["size", "nunique"])
    if not ((counts["size"] == len(test)) & (counts["nunique"] == len(test))).all():
        raise AssertionError("a policy/batch-packing did not route every test query exactly once")
    assignment_frame.to_csv(out_dir / "test_assignments.csv", index=False)
    summary_frame.to_csv(out_dir / "seed_level_metrics.csv", index=False)
    run_payload = [json.loads(run.to_json()) for run in run_objects]
    if len(run_payload) != len(PACKING_SEEDS) * 2 * len(BUDGET_FRACTIONS) * len(POLICY_IDS):
        raise AssertionError("ExperimentRun count differs from declared design")
    ExperimentRun.from_json(json.dumps(run_payload[0]))
    (out_dir / "experiment_runs.json").write_text(json.dumps(run_payload, indent=2, sort_keys=True))
    cost_rmse = float(np.sqrt(np.mean((costs_test - latency_test) ** 2)))
    result = summarize_results(summary_frame, assignment_frame, qhat_test, qtrue_test, fit_y,
                               costs_test, latency_test, predictor, lambda_by_fraction, cost_rmse)
    result["provenance"] = {
        "dataset": DATASET_ID, "dataset_revision": DATASET_REVISION,
        "dataset_license": "MIT", "models": MODEL_REVISIONS,
        "model_licenses": {model: "Apache-2.0" for model in MODEL_IDS},
        "train_queries": TRAIN_QUERIES, "test_per_subject": TEST_PER_SUBJECT,
        "test_subjects": list(TEST_SUBJECTS), "batch_size": BATCH_SIZE,
        "packing_seeds": list(PACKING_SEEDS), "budget_fractions": list(BUDGET_FRACTIONS),
        "device": _device(), "test_metrics_use_official_test_only": True,
        "python_version": sys.version.split()[0], "torch_version": torch.__version__,
        "transformers_version": transformers.__version__, "platform": platform.platform(),
        "generation": {"do_sample": False, "max_new_tokens": 8, "dtype": "float16"},
        "git_head": git_head, "source_hashes_sha256": source_hashes,
        "working_tree_dirty_at_run": working_tree_dirty,
    }
    (out_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True))
    artifact_hashes = {}
    for name in ("model_outcomes.csv", "quality_cost_predictions.csv", "test_assignments.csv",
                 "seed_level_metrics.csv", "experiment_runs.json", "results.json"):
        artifact = out_dir / name
        artifact_hashes[name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (out_dir / "artifact_hashes.json").write_text(json.dumps(artifact_hashes, indent=2, sort_keys=True))
    return result


def _paired_interval(values: np.ndarray, seed: int) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(10000, len(values)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def _query_interval(values: np.ndarray, seed: int) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(10000, len(values)), replace=True).mean(axis=1)
    return [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]


def _stratified_query_interval(frame: pd.DataFrame, value_column: str, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    by_task = [frame.loc[frame.task_type == task, value_column].to_numpy(dtype=float)
               for task in TEST_SUBJECTS]
    if any(len(values) == 0 for values in by_task):
        raise ValueError("query bootstrap requires every declared task")
    draws = np.zeros(10000, dtype=float)
    for values in by_task:
        draws += rng.choice(values, size=(10000, len(values)), replace=True).mean(axis=1) / len(by_task)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def summarize_results(summary: pd.DataFrame, assignments: pd.DataFrame,
                      qhat: np.ndarray, qtrue: np.ndarray,
                      training_outcomes: np.ndarray,
                      costs_test: np.ndarray, latency_test: np.ndarray,
                      predictor: MIRTQualityPredictor,
                      lambda_by_fraction: dict[float, float], cost_rmse: float) -> dict[str, Any]:
    groups = summary.groupby(["condition", "budget_fraction", "policy_id"], sort=True)
    metrics = {}
    for key, frame in groups:
        metrics["|".join(map(str, key))] = {
            column: {"mean": float(frame[column].mean()), "sd_across_packing_seeds": float(frame[column].std(ddof=1)),
                     "ci95_repacking": _paired_interval(frame[column].to_numpy(), TRAIN_SEED)}
            for column in ["accuracy", "estimated_cost_seconds", "observed_latency_seconds",
                           "estimated_budget_compliance", "observed_latency_budget_compliance"]
        }
    contrasts = {}
    query_means = assignments.groupby(
        ["condition", "budget_fraction", "policy_id", "task_type", "query_id"],
        as_index=False, sort=True,
    ).correct.mean()
    for key in metrics:
        condition, fraction, policy = key.split("|")
        queries = query_means[
            (query_means.condition == condition)
            & (query_means.budget_fraction == float(fraction))
            & (query_means.policy_id == policy)
        ]
        metrics[key]["accuracy"]["ci95_stratified_query_bootstrap"] = _stratified_query_interval(
            queries, "correct", TRAIN_SEED + 20,
        )
    for condition in summary.condition.unique():
        for fraction in BUDGET_FRACTIONS:
            subset = summary[(summary.condition == condition) & (summary.budget_fraction == fraction)]
            for reference in ("independent_repaired", "greedy_feasible", "fixed_economic",
                              "fixed_quality", "test_oracle"):
                pivot = subset.pivot(index="packing_seed", columns="policy_id", values="accuracy")
                differences = pivot["batch_ilp"] - pivot[reference]
                paired_queries = query_means[
                    (query_means.condition == condition)
                    & (query_means.budget_fraction == fraction)
                ].pivot(index=["task_type", "query_id"], columns="policy_id", values="correct").reset_index()
                paired_queries["paired_difference"] = paired_queries["batch_ilp"] - paired_queries[reference]
                contrasts[f"{condition}|{fraction:.2f}|ILP-minus-{reference}"] = {
                    "mean": float(differences.mean()),
                    "ci95_repacking": _paired_interval(differences.to_numpy(), TRAIN_SEED + 2),
                    "ci95_stratified_query_bootstrap": _stratified_query_interval(
                        paired_queries.rename(columns={"paired_difference": "query_difference"}),
                        "query_difference", TRAIN_SEED + 5,
                    ),
                    "interpretation": "paired variation across batch packings of a fixed test subset",
                }
    task_metrics = {}
    task_columns = [f"accuracy:{task}" for task in TEST_SUBJECTS]
    for key, frame in summary.groupby(["condition", "budget_fraction", "policy_id"], sort=True):
        group_key = "|".join(map(str, key))
        task_metrics[group_key] = {
            task: {
                "mean_accuracy": float(frame[column].mean()),
                "ci95_repacking": _paired_interval(frame[column].to_numpy(), TRAIN_SEED + 3),
            }
            for task, column in zip(TEST_SUBJECTS, task_columns)
        }
    for key, frame in query_means.groupby(["condition", "budget_fraction", "policy_id"], sort=True):
        group_key = "|".join(map(str, key))
        for task in TEST_SUBJECTS:
            values = frame.loc[frame.task_type == task, "correct"].to_numpy(dtype=float)
            task_metrics[group_key][task]["ci95_query_bootstrap"] = _query_interval(values, TRAIN_SEED + 4)
    model_share = {}
    resource_by_task = {}
    latency_quantiles = {}
    for key, frame in assignments.groupby(
            ["condition", "budget_fraction", "policy_id"], sort=True):
        group_key = "|".join(map(str, key))
        model_share[group_key] = {
            model: float((frame.model_id == model).mean()) for model in MODEL_IDS
        }
        resource_by_task[group_key] = {
            task: {
                "model_assignment_share": {
                    model: float((frame.loc[frame.task_type == task, "model_id"] == model).mean())
                    for model in MODEL_IDS
                },
                "mean_predicted_cost_seconds": float(
                    frame.loc[frame.task_type == task, "predicted_cost_seconds"].mean()),
                "mean_observed_latency_seconds": float(
                    frame.loc[frame.task_type == task, "observed_latency_seconds"].mean()),
            }
            for task in TEST_SUBJECTS
        }
        latency_quantiles[group_key] = {
            "p50_seconds": float(frame.observed_latency_seconds.quantile(0.50)),
            "p95_seconds": float(frame.observed_latency_seconds.quantile(0.95)),
        }
    return {
        "metrics_by_condition_budget_policy": metrics,
        "paired_accuracy_contrasts": contrasts,
        "per_task_accuracy_by_condition_budget_policy": task_metrics,
        "assignment_share_by_model": model_share,
        "resource_distribution_by_task": resource_by_task,
        "selected_latency_quantiles": latency_quantiles,
        "predictor": {
            "method": "MIRT-style logistic item-feature/model-ability response model",
            "fit": predictor.fit_info,
            "test_brier_score": float(np.mean((qhat - qtrue) ** 2)),
            "test_mean_predicted_quality": float(np.mean(qhat)),
            "test_mean_observed_quality": float(np.mean(qtrue)),
            "test_brier_score_binary_per_query_model": float(np.mean((qhat - qtrue) ** 2)),
            "test_brier_score_train_prevalence_baseline": float(np.mean((
                np.broadcast_to(np.asarray(training_outcomes, dtype=float).mean(axis=0), qtrue.shape)
                - qtrue
            ) ** 2)),
            "latency_prediction_rmse_seconds_on_test_candidates": cost_rmse,
            "candidate_models": {
                model: {
                    "test_exact_match_accuracy": float(qtrue[:, i].mean()),
                    "mean_predicted_latency_seconds": float(costs_test[:, i].mean()),
                    "mean_observed_latency_seconds": float(latency_test[:, i].mean()),
                }
                for i, model in enumerate(MODEL_IDS)
            },
            "price_lambda_by_budget_fraction": {f"{k:.2f}": v for k, v in lambda_by_fraction.items()},
        },
        "caveats": [
            "MMLU is one benchmark family; task types are four selected official subjects.",
            "Cost is local single-query inference wall time, not monetary API cost or concurrent batch latency.",
            "Repacking-seed confidence intervals condition on the fixed sampled test queries and generated outcomes.",
            "The test oracle sees held-out outcomes and is only a retrospective upper bound.",
            "Small open models may answer outside the expected format; those responses count incorrect under exact-match scoring.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    result = run_pilot(args.output)
    print(json.dumps({"output": str(args.output), "policy_groups": len(result["metrics_by_condition_budget_policy"]),
                      "paired_contrasts": result["paired_accuracy_contrasts"]}, indent=2))


if __name__ == "__main__":
    main()
