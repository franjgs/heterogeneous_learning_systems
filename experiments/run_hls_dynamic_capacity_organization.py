"""Reproducible MMLU pilot of static, selective-cascade and ensemble routing."""

from __future__ import annotations

import csv
import gc
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from huggingface_hub import hf_hub_download
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from hls.dynamic_capacity_organization import (  # noqa: E402
    cascade_predictions, fit_escalation_threshold, fit_router_price, irt_route,
    majority_vote, paired_stratified_bootstrap_delta, per_task_accuracy,
    static_model_by_task,
)
from hls.experiment_contract import (  # noqa: E402
    SCHEMA_VERSION, ExperimentEvent, ExperimentRun, MetricValue, SeedRecord,
    UnitDeclaration,
)
from hls.llm_routing_pilot import (  # noqa: E402
    MODEL_IDS, MIRTQualityPredictor, apply_latency, predict_latency,
)
from hls.performance_evaluation import (  # noqa: E402
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator,
)
from run_hls_budgeted_llm_routing_pilot import (  # noqa: E402
    DATASET_ID, DATASET_REVISION, MODEL_REVISIONS, TEST_SEED, TEST_SUBJECTS,
    TRAIN_SEED, _device, _qid, make_prompt, parse_answer, request_features,
)

OUT = ROOT / "results/experiments/hls_dynamic_capacity_organization"
TARGET_RATES = tuple(float(x) for x in np.linspace(0, 1, 11))
BOOTSTRAPS = 5000
RNG_SEED = 20261023


def _load_split(path: str, split: str) -> pd.DataFrame:
    local = hf_hub_download(DATASET_ID, path, repo_type="dataset", revision=DATASET_REVISION)
    frame = pd.read_parquet(local).reset_index(drop=False).rename(columns={"index": "source_index"})
    frame = frame[frame.subject.isin(TEST_SUBJECTS)].copy().reset_index(drop=True)
    frame["split"] = split
    frame["task_type"] = frame.subject
    frame["query_id"] = [
        _qid(split, row.subject, row.source_index, row.question, list(row.choices))
        for row in frame.itertuples()
    ]
    return frame


def _load_pilot_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    from run_hls_budgeted_llm_routing_pilot import load_pilot_data

    train, test = load_pilot_data()
    return train, test.reset_index(drop=True)


def build_partitions() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Train=official MMLU dev; val=official validation; test=pilot's fixed test."""
    auxiliary_train, test = _load_pilot_frames()
    dev = _load_split("all/dev-00000-of-00001.parquet", "train")
    validation = _load_split("all/validation-00000-of-00001.parquet", "validation")
    # Dev is the task-labelled training partition (five questions per task).
    dev = dev.groupby("task_type", sort=True, group_keys=False).head(5).reset_index(drop=True)
    # Equal, deterministic threshold-calibration sample from all four subjects.
    validation = (validation.groupby("task_type", group_keys=False)
                  .sample(n=22, random_state=RNG_SEED).sort_values(["task_type", "source_index"])
                  .reset_index(drop=True))
    test["split"] = "test"
    if any(set(left.query_id) & set(right.query_id)
           for left, right in ((dev, validation), (dev, test), (validation, test))):
        raise AssertionError("train, validation and test query IDs overlap")
    return auxiliary_train, dev, validation, test


def _letter_token_ids(tokenizer: Any) -> dict[str, tuple[int, ...]]:
    result = {}
    for letter in "ABCD":
        ids = set()
        for value in (letter, " " + letter):
            encoded = tokenizer.encode(value, add_special_tokens=False)
            if len(encoded) != 1:
                raise ValueError(f"{tokenizer.name_or_path}: {value!r} is not one token")
            ids.add(int(encoded[0]))
        result[letter] = tuple(sorted(ids))
    return result


def _encode_prompt(tokenizer: Any, row: Any, device: str) -> dict[str, torch.Tensor]:
    prompt = make_prompt(row.question, list(row.choices))
    messages = [{"role": "user", "content": prompt}]
    if getattr(tokenizer, "chat_template", None):
        encoded = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True,
            return_tensors="pt", return_dict=True,
        )
    else:
        encoded = tokenizer(prompt, return_tensors="pt")
    return {key: value.to(device) for key, value in encoded.items()}


def collect_model_outputs(
    partitions: tuple[pd.DataFrame, ...], out_dir: Path = OUT,
) -> pd.DataFrame:
    """Collect generated answer, first-step choice-token mass and latency.

    One append-only JSONL cache allows a stopped run to resume. Existing pilot
    artifacts are read-only and never used as the new output cache.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = out_dir / "model_scoring_cache.jsonl"
    queries = pd.concat(partitions, ignore_index=True)
    records: dict[tuple[str, str], dict[str, Any]] = {}
    if cache.exists():
        with cache.open() as stream:
            for line in stream:
                row = json.loads(line)
                records[(row["query_id"], row["model_id"])] = row
    device = _device()
    for model_id in MODEL_IDS:
        revision = MODEL_REVISIONS[model_id]
        missing = [row for row in queries.itertuples()
                   if (row.query_id, model_id) not in records]
        if not missing:
            continue
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=revision, torch_dtype=torch.float16,
            low_cpu_mem_usage=False,
        ).to(device)
        model.eval()
        letter_tokens = _letter_token_ids(tokenizer)
        # Warm-up is excluded from request latency; the experiment assumes a
        # resident model pool and reports weight loading separately.
        for row in missing[:2]:
            encoded = _encode_prompt(tokenizer, row, device)
            with torch.inference_mode():
                model.generate(**encoded, do_sample=False, max_new_tokens=1,
                               pad_token_id=tokenizer.eos_token_id)
        if device == "mps":
            torch.mps.synchronize()
        for index, row in enumerate(missing):
            encoded = _encode_prompt(tokenizer, row, device)
            if device == "mps":
                torch.mps.synchronize()
            start = time.perf_counter()
            with torch.inference_mode():
                generated = model.generate(
                    **encoded, do_sample=False, max_new_tokens=8,
                    pad_token_id=tokenizer.eos_token_id, return_dict_in_generate=True,
                    output_scores=True,
                )
                logits = generated.scores[0][0].float()
                probs = torch.softmax(logits, dim=-1)
                masses = {
                    letter: float(sum(probs[token_id].item() for token_id in ids))
                    for letter, ids in letter_tokens.items()
                }
                total_mass = sum(masses.values())
                normalized = {key: (value / total_mass if total_mass > 0 else 0.25)
                              for key, value in masses.items()}
                token_ids = generated.sequences[0, encoded["input_ids"].shape[1]:]
                response = tokenizer.decode(token_ids, skip_special_tokens=True).strip()
            if device == "mps":
                torch.mps.synchronize()
            elapsed = time.perf_counter() - start
            letter = parse_answer(response) or ""
            answer_letter = "ABCD"[int(row.answer)]
            confidence = normalized.get(letter, 0.0)
            record = {
                "query_id": row.query_id, "split": row.split, "task_type": row.task_type,
                "model_id": model_id, "model_revision": revision,
                "predicted_letter": letter, "correct_letter": answer_letter,
                "correct": int(letter == answer_letter), "response_text": response,
                "choice_token_mass": normalized, "confidence": float(confidence),
                "input_tokens": int(encoded["input_ids"].shape[1]),
                "output_tokens": int(len(token_ids)), "latency_seconds": float(elapsed),
            }
            records[(row.query_id, model_id)] = record
            with cache.open("a") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        del model, tokenizer
        gc.collect()
        if device == "mps":
            torch.mps.empty_cache()
    expected = len(queries) * len(MODEL_IDS)
    frame = pd.DataFrame(records.values())
    frame = frame[frame.query_id.isin(queries.query_id)].copy()
    frame.to_csv(out_dir / "model_outputs_and_confidence.csv.gz", index=False, compression="gzip")
    if len(frame) != expected or frame.duplicated(["query_id", "model_id"]).any():
        raise AssertionError(f"expected {expected} unique query/model outputs, found {len(frame)}")
    return frame


def _matrix(frame: pd.DataFrame, outputs: pd.DataFrame, column: str) -> np.ndarray:
    pivot = outputs.pivot(index="query_id", columns="model_id", values=column)
    return pivot.loc[frame.query_id, list(MODEL_IDS)].to_numpy()


def _fit_original_irt(auxiliary_train: pd.DataFrame) -> tuple[MIRTQualityPredictor, tuple[np.ndarray, np.ndarray]]:
    old = pd.read_csv(OUT.parent / "hls_budgeted_llm_routing_pilot" / "model_outcomes.csv")
    fit_n = int(len(auxiliary_train) * 0.8)
    order = np.random.default_rng(TRAIN_SEED + 1).permutation(len(auxiliary_train))
    fit = auxiliary_train.iloc[order[:fit_n]].reset_index(drop=True)
    lookup = old[old.query_id.isin(fit.query_id)].pivot(index="query_id", columns="model_id", values="correct")
    y = lookup.loc[fit.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    predictor = MIRTQualityPredictor(seed=TRAIN_SEED).fit(request_features(fit), MODEL_IDS, y)
    tokens = old[old.query_id.isin(fit.query_id)].pivot(index="query_id", columns="model_id", values="input_tokens")
    latency = old[old.query_id.isin(fit.query_id)].pivot(index="query_id", columns="model_id", values="latency_seconds")
    token_matrix = tokens.loc[fit.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    latency_matrix = latency.loc[fit.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    return predictor, predict_latency(token_matrix, latency_matrix)


def _pef_policy(
    policy_id: str, test: pd.DataFrame, predicted: np.ndarray,
    costs: np.ndarray, confidence: np.ndarray, escalated: np.ndarray,
    selected_models: list[str], output_dir: Path,
) -> tuple[dict[str, Any], ExperimentRun]:
    scenario = "mmlu_dynamic_capacity_v1"
    config = f"{DATASET_REVISION}-four-subject-test-160"
    info = "test query and task observed; FAST answer-token mass observable before escalation; correctness hidden until evaluation"
    if policy_id.startswith("irt_router_"):
        decision_objective = "select per query by validation-fitted argmax(predicted correctness - price × predicted latency)"
    elif policy_id.startswith("cascade_"):
        target = policy_id.rsplit("_", 1)[-1]
        decision_objective = f"accept FAST unless observable confidence is below validation threshold targeting {target} DEEP activations; then return DEEP"
    elif policy_id == "static_best_by_task":
        decision_objective = "fixed model per task with highest observed exact accuracy on official dev train only"
    elif policy_id == "fast_always":
        decision_objective = "always use the train-selected lowest-latency model"
    elif policy_id == "deep_always":
        decision_objective = "always use the train-selected highest-accuracy model"
    elif policy_id == "all_model_plurality":
        decision_objective = "plurality vote over all three model letters; ties use the train-selected DEEP output"
    else:
        decision_objective = "retrospective test oracle: fastest correct model, or fastest model if none is correct"
    profile = EvaluationProfile(
        profile_id=f"{policy_id}-profile", scenario_id=scenario,
        configuration_id=config, application_domain="local open-weight language models",
        organizational_problem="static selection, confidence-triggered escalation or output combination",
        decision_objective={policy_id: decision_objective},
        constraints="one final answer per query; cascade cost includes FAST and any DEEP call",
        primary_metrics=("functional_success_rate",),
        secondary_metrics=("original_reward_cumulative", "resource_usage:inference_latency_seconds"),
        information_regime=info, temporal_horizon=len(test),
        aggregation_rules="one MMLU question per period; exact answer-letter match; costs sum actual invoked model latency",
        demand_distribution_id="cais-mmlu-four-subject-test-fixed-sample",
        resource_units={"inference_latency_seconds": "seconds"},
    )
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    records = []
    events = []
    for period, row in enumerate(test.itertuples()):
        records.append(EvaluationRecord(
            scenario_id=scenario, configuration_id=config, policy_id=policy_id,
            period=period, demand=row.task_type, success=bool(predicted[period] == "ABCD"[int(row.answer)]),
            original_reward=float(predicted[period] == "ABCD"[int(row.answer)]),
            resource_usage={"inference_latency_seconds": float(costs[period])},
            provenance=f"cais/mmlu@{DATASET_REVISION}#test:{row.query_id}:{policy_id}",
            unit_id=row.query_id, task_type=row.task_type, quality=float(predicted[period] == "ABCD"[int(row.answer)]),
            information_regime=info,
            decision_objective=profile.decision_objective[policy_id],
            available_metadata={"selected_model_or_path": selected_models[period],
                                "fast_confidence": float(confidence[period]),
                                "escalated": bool(escalated[period])},
        ))
        events.append(ExperimentEvent(
            sequence_index=period, event_type="query_routed", mechanism_id=policy_id,
            time_index=period,
            data={"query_id": row.query_id, "task_type": row.task_type,
                  "selected_model_or_path": selected_models[period],
                  "observable_fast_confidence": float(confidence[period]),
                  "escalated": bool(escalated[period]), "cost_seconds": float(costs[period])},
        ))
    evaluation = evaluator.evaluate(profile.profile_id, policy_id, records)
    metrics = {key: {"value": value.value, "unit": value.unit, "status": value.status.value,
                     "aggregation": value.aggregation}
               for key, value in evaluation.items()}
    run = ExperimentRun(
        schema_version=SCHEMA_VERSION, run_id=policy_id, mechanism_id=policy_id,
        policy_id=policy_id,
        configuration={"scenario": scenario, "dataset_revision": DATASET_REVISION,
                       "models": list(MODEL_IDS), "n_test": len(test)},
        initial_conditions={"test_query_ids_sha256": hashlib.sha256("\n".join(test.query_id).encode()).hexdigest()},
        random_seeds=(SeedRecord(stream="dataset_sampling", value=TEST_SEED, purpose="fixed test query sample"),),
        information_available={"test_answer_key": "evaluation-only", "fast_confidence": "available to cascade after FAST"},
        observation_model={"answer_generation": "greedy max_new_tokens=8", "confidence": "normalized first-step mass over A-D token variants"},
        software_revision=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                         capture_output=True, text=True).stdout.strip() or None,
        units=(UnitDeclaration("quality", "fraction", "exact answer-letter accuracy"),
               UnitDeclaration("inference_latency", "seconds", "sum of invoked model request latencies")),
        events=tuple(events),
        metrics=(MetricValue("functional_success_rate", metrics["functional_success_rate"]["value"],
                             "fraction", "exact MMLU answer-letter accuracy", "higher"),
                 MetricValue("total_latency_seconds", metrics["resource_usage:inference_latency_seconds"]["value"],
                             "seconds", "sum of latency for all invoked model calls", "lower")),
        mechanism_results={"hls_pef_metrics": metrics},
        metadata={"profile_id": profile.profile_id, "source": "new MMLU inference; model outputs and labels kept in separate audit table",
                  "policy_uses_test_labels": False},
    )
    return metrics, run


def run_experiment(out_dir: Path = OUT) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    auxiliary, train, validation, test = build_partitions()
    all_outputs = collect_model_outputs((train, validation, test), out_dir)
    # Ensure the fixed test re-inference reproduces the archived generations.
    old = pd.read_csv(out_dir.parent / "hls_budgeted_llm_routing_pilot" / "model_outcomes.csv")
    new_test = all_outputs[all_outputs.split == "test"]
    old_test = old[old.split == "test"]
    merge = new_test.merge(old_test[["query_id", "model_id", "predicted_letter"]],
                           on=["query_id", "model_id"], suffixes=("_new", "_old"), validate="one_to_one")
    exact_reproduction = float(np.mean(merge.predicted_letter_new.fillna("") == merge.predicted_letter_old.fillna("")))

    train_letters = _matrix(train, all_outputs, "predicted_letter").astype(str)
    train_y = _matrix(train, all_outputs, "correct").astype(int)
    test_letters = _matrix(test, all_outputs, "predicted_letter").astype(str)
    test_y = _matrix(test, all_outputs, "correct").astype(int)
    val_letters = _matrix(validation, all_outputs, "predicted_letter").astype(str)
    val_y = _matrix(validation, all_outputs, "correct").astype(int)
    val_conf = _matrix(validation, all_outputs, "confidence").astype(float)
    test_conf_matrix = _matrix(test, all_outputs, "confidence").astype(float)
    val_latency = _matrix(validation, all_outputs, "latency_seconds").astype(float)
    test_latency = _matrix(test, all_outputs, "latency_seconds").astype(float)
    tasks = test.task_type.to_numpy(dtype=str)
    truth = np.asarray(["ABCD"[int(answer)] for answer in test.answer], dtype=str)

    # FAST/DEEP roles are fixed from the archived train-only pilot fit, not test.
    pilot_train = auxiliary
    old_train = old[old.split == "auxiliary_train"]
    fit_n = int(len(pilot_train) * 0.8)
    fit_order = np.random.default_rng(TRAIN_SEED + 1).permutation(len(pilot_train))[:fit_n]
    fit_ids = set(pilot_train.iloc[fit_order].query_id)
    fit_old = old_train[old_train.query_id.isin(fit_ids)]
    train_acc = fit_old.groupby("model_id").correct.mean().reindex(MODEL_IDS)
    train_latency = fit_old.groupby("model_id").latency_seconds.mean().reindex(MODEL_IDS)
    fast_idx = int(np.argmin(train_latency.to_numpy()))
    quality_order = np.argsort(-train_acc.to_numpy())
    deep_idx = next((int(i) for i in quality_order if int(i) != fast_idx), int(quality_order[0]))
    if fast_idx == deep_idx:
        raise AssertionError("FAST and DEEP must be distinct capacities")

    # Published item-response routing adaptation: fit only on archived train.
    irt, cost_coeff = _fit_original_irt(auxiliary)
    val_q = irt.predict(request_features(validation))
    test_q = irt.predict(request_features(test))
    val_cost = apply_latency(_matrix(validation, all_outputs, "input_tokens").astype(float), cost_coeff)
    test_cost = apply_latency(_matrix(test, all_outputs, "input_tokens").astype(float), cost_coeff)

    static_choice, static_by_task = static_model_by_task(
        train.task_type, train_y, test.task_type, MODEL_IDS,
    )
    policies: dict[str, dict[str, Any]] = {}
    def add(policy_id: str, prediction: np.ndarray, cost: np.ndarray, selected: list[str],
            confidence: np.ndarray | None = None, escalated: np.ndarray | None = None) -> None:
        confidence = np.zeros(len(test)) if confidence is None else np.asarray(confidence, dtype=float)
        escalated = np.zeros(len(test), dtype=bool) if escalated is None else np.asarray(escalated, dtype=bool)
        metrics, run = _pef_policy(policy_id, test, prediction, cost, confidence, escalated, selected, out_dir)
        policies[policy_id] = {"prediction": np.asarray(prediction, dtype=str),
                               "cost": np.asarray(cost, dtype=float), "selected": selected,
                               "metrics": metrics, "run": run}

    def add_single(policy_id: str, indices: np.ndarray) -> None:
        idx = np.asarray(indices, dtype=int)
        add(policy_id, test_letters[np.arange(len(test)), idx],
            test_latency[np.arange(len(test)), idx], [MODEL_IDS[x] for x in idx])

    fast_answer = test_letters[:, fast_idx]
    deep_answer = test_letters[:, deep_idx]
    fast_conf = test_conf_matrix[:, fast_idx]
    add_single("fast_always", np.full(len(test), fast_idx))
    add_single("deep_always", np.full(len(test), deep_idx))
    add_single("static_best_by_task", static_choice)

    # Validation-fitted cost-price curve for IRT-Router; no test labels enter.
    for fraction in np.linspace(0, 1, 11):
        price, val_mean_cost = fit_router_price(val_q, val_cost, float(fraction))
        selected = irt_route(test_q, test_cost, price)
        add(f"irt_router_cost_fraction_{fraction:.1f}",
            test_letters[np.arange(len(test)), selected],
            test_latency[np.arange(len(test)), selected], [MODEL_IDS[x] for x in selected])
        policies[f"irt_router_cost_fraction_{fraction:.1f}"]["validation"] = {
            "price": price, "target_cost_fraction": float(fraction),
            "predicted_mean_cost_seconds": val_mean_cost,
        }

    # Selective-classification confidence threshold adapted to escalation.
    deep_idx_arr = np.full(len(test), deep_idx, dtype=int)
    for target_rate in TARGET_RATES:
        threshold = fit_escalation_threshold(val_conf[:, fast_idx], target_rate)
        prediction, escalated = cascade_predictions(fast_answer, fast_conf, deep_answer, threshold.threshold)
        cost = test_latency[:, fast_idx] + escalated.astype(float) * test_latency[:, deep_idx]
        path = [f"{MODEL_IDS[fast_idx]}>{MODEL_IDS[deep_idx]}" if e else MODEL_IDS[fast_idx]
                for e in escalated]
        policy_id = f"cascade_target_deep_rate_{target_rate:.1f}"
        add(policy_id, prediction, cost, path, fast_conf, escalated)
        policies[policy_id]["validation"] = {
            "target_deep_rate": threshold.target_escalation_rate,
            "validation_deep_rate": threshold.validation_escalation_rate,
            "threshold": threshold.threshold,
        }

    # All-model plurality is an explicit output-combination comparator.
    vote = majority_vote(test_letters, deep_idx)
    add("all_model_plurality", vote, test_latency.sum(axis=1),
        ["+".join(MODEL_IDS)] * len(test))

    # Retrospective upper bound: answer correctly if any candidate does,
    # otherwise choose the fastest available model. It is non-deployable.
    oracle_idx = np.asarray([
        min(np.flatnonzero(test_y[i]), key=lambda j: (test_latency[i, j], int(j)))
        if test_y[i].any() else int(np.argmin(test_latency[i]))
        for i in range(len(test))
    ], dtype=int)
    add("test_oracle_fastest_correct", test_letters[np.arange(len(test)), oracle_idx],
        test_latency[np.arange(len(test)), oracle_idx], [MODEL_IDS[x] for x in oracle_idx])

    # Accuracy and cost curves, per-task results, and paired query bootstrap CIs.
    baseline_ids = ["fast_always", "deep_always", "static_best_by_task", "all_model_plurality"]
    fast_correct = test_y[:, fast_idx].astype(bool)
    deep_correct = test_y[:, deep_idx].astype(bool)
    curve_rows = []
    for policy_id, row in policies.items():
        pred = row["prediction"]
        correct = (pred == truth).astype(float)
        if policy_id.startswith("cascade_"):
            rate = float(np.mean([">" in item for item in row["selected"]]))
        elif policy_id == "all_model_plurality":
            rate = 1.0
        else:
            rate = float(np.mean([item == MODEL_IDS[deep_idx] for item in row["selected"]]))
        escalated = np.asarray([">" in item for item in row["selected"]], dtype=bool)
        deep_by_task = {task: (float(np.mean(escalated[tasks == task]))
                               if policy_id.startswith("cascade_") else 1.0
                               if policy_id == "all_model_plurality" else
                               float(np.mean([item == MODEL_IDS[deep_idx]
                                              for item, same_task in zip(row["selected"], tasks)
                                              if same_task == task])))
                        for task in sorted(set(tasks.tolist()))}
        call_counts = {model: 0 for model in MODEL_IDS}
        for choice in row["selected"]:
            if "+" in choice:
                for model in MODEL_IDS:
                    call_counts[model] += 1
            elif ">" in choice:
                for model in choice.split(">"):
                    call_counts[model] += 1
            else:
                call_counts[choice] += 1
        record = {
            "policy_id": policy_id, "accuracy": float(correct.mean()),
            "mean_latency_seconds": float(row["cost"].mean()),
            "total_latency_seconds": float(row["cost"].sum()),
            "deep_activation_rate": rate,
            "deep_activation_by_task": deep_by_task,
            "model_call_counts": call_counts,
            "per_task_accuracy": per_task_accuracy(pred, truth, tasks),
        }
        if policy_id.startswith("cascade_"):
            record["escalated_outcome_partition"] = {
                "queries_escalated": int(escalated.sum()),
                "deep_corrects_fast_error": int(np.sum(escalated & ~fast_correct & deep_correct)),
                "deep_harms_fast_correct": int(np.sum(escalated & fast_correct & ~deep_correct)),
                "both_correct": int(np.sum(escalated & fast_correct & deep_correct)),
                "neither_correct": int(np.sum(escalated & ~fast_correct & ~deep_correct)),
            }
        record["accuracy_ci95_stratified_query"] = list(
            paired_stratified_bootstrap_delta(correct, np.zeros_like(correct), tasks,
                                               n_boot=BOOTSTRAPS, seed=RNG_SEED + 1)
        )[1:]
        record["latency_ci95_stratified_query"] = list(
            paired_stratified_bootstrap_delta(row["cost"], np.zeros_like(row["cost"]), tasks,
                                               n_boot=BOOTSTRAPS, seed=RNG_SEED + 2)
        )[1:]
        for baseline_id in baseline_ids:
            bcorrect = (policies[baseline_id]["prediction"] == truth).astype(float)
            mean, low, high = paired_stratified_bootstrap_delta(
                correct, bcorrect, tasks, n_boot=BOOTSTRAPS,
                seed=RNG_SEED + sum(ord(c) for c in policy_id + baseline_id),
            )
            record.setdefault("paired_accuracy_delta_vs_baselines", {})[baseline_id] = {
                "mean": mean, "ci95": [low, high],
            }
            mean_cost, low_cost, high_cost = paired_stratified_bootstrap_delta(
                row["cost"], policies[baseline_id]["cost"], tasks,
                n_boot=BOOTSTRAPS,
                seed=RNG_SEED + 500 + sum(ord(c) for c in policy_id + baseline_id),
            )
            record.setdefault("paired_latency_delta_seconds_vs_baselines", {})[baseline_id] = {
                "mean": mean_cost, "ci95": [low_cost, high_cost],
            }
        curve_rows.append(record)

    # Capacity complementarity, paired at the query level.
    complementarity = {
        "both_correct": int(np.sum(fast_correct & deep_correct)),
        "fast_only_correct": int(np.sum(fast_correct & ~deep_correct)),
        "deep_only_correct": int(np.sum(~fast_correct & deep_correct)),
        "neither_correct": int(np.sum(~fast_correct & ~deep_correct)),
        "fast_accuracy": float(fast_correct.mean()),
        "deep_accuracy": float(deep_correct.mean()),
        "by_task": {},
    }
    for task in sorted(set(tasks.tolist())):
        mask = tasks == task
        complementarity["by_task"][task] = {
            "n": int(mask.sum()), "fast_accuracy": float(fast_correct[mask].mean()),
            "deep_accuracy": float(deep_correct[mask].mean()),
            "fast_only_correct": int(np.sum(fast_correct[mask] & ~deep_correct[mask])),
            "deep_only_correct": int(np.sum(~fast_correct[mask] & deep_correct[mask])),
            "deep_harms_fast": int(np.sum(fast_correct[mask] & ~deep_correct[mask])),
        }
    complementarity["deep_minus_fast_accuracy_ci95"] = list(
        paired_stratified_bootstrap_delta(deep_correct, fast_correct, tasks,
                                          n_boot=BOOTSTRAPS, seed=RNG_SEED + 3)
    )

    result = {
        "experiment": "HLS dynamic capacity organization pilot",
        "status": "completed",
        "dataset": {"id": DATASET_ID, "revision": DATASET_REVISION,
                    "splits": {"task_train": "official all/dev, 5 per task",
                               "threshold_validation": "official all/validation, deterministic 22 per task",
                               "test": "same 160 fixed official test queries from prior pilot"},
                    "n_train_task": len(train), "n_validation": len(validation), "n_test": len(test)},
        "models": list(MODEL_IDS),
        "roles_fixed_from_original_train_only": {
            "fast_model": MODEL_IDS[fast_idx], "deep_model": MODEL_IDS[deep_idx],
            "train_fit_mean_latency_seconds": train_latency.to_dict(),
            "train_fit_accuracy": train_acc.to_dict(),
            "static_model_by_task_from_dev_train": static_by_task,
            "test_mean_latency_seconds_by_model_and_task": {
                task: {MODEL_IDS[j]: float(test_latency[tasks == task, j].mean())
                       for j in range(len(MODEL_IDS))}
                for task in sorted(set(tasks.tolist()))
            },
        },
        "old_test_generation_letter_match_rate": exact_reproduction,
        "confidence_signal": "normalized sum of first-generation-step softmax masses for A/space-A through D/space-D token variants; observable, uncalibrated proxy; cascade thresholds fitted only to validation confidence",
        "mechanisms": {
            "selection": "IRT-Router published MIRT response form adapted from existing pilot; quality-cost price selected on validation, routes by argmax(q_hat - lambda*c_hat)",
            "sequential": "selective-classification confidence threshold (Geifman & El-Yaniv 2017) adapted from reject to escalation FAST then DEEP; validation thresholds set target activation rates, no test-label use",
            "combination": "plurality vote over three generated answer letters; ties use DEEP answer; executes all three models",
        },
        "complementarity": complementarity,
        "fast_confidence_diagnostics": {
            "validation": {
                "n": len(validation),
                "brier_as_correctness_probability": float(np.mean((val_conf[:, fast_idx] - val_y[:, fast_idx]) ** 2)),
                "auc_error_ranking": float(roc_auc_score(1 - val_y[:, fast_idx], 1 - val_conf[:, fast_idx])),
            },
            "test_evaluation_only": {
                "n": len(test),
                "brier_as_correctness_probability": float(np.mean((test_conf_matrix[:, fast_idx] - test_y[:, fast_idx]) ** 2)),
                "auc_error_ranking": float(roc_auc_score(1 - test_y[:, fast_idx], 1 - test_conf_matrix[:, fast_idx])),
            },
        },
        "curves": curve_rows,
        "per_policy_hls_pef": {key: value["metrics"] for key, value in policies.items()},
        "validation_parameters": {
            "cascade": {key: value["validation"] for key, value in policies.items() if key.startswith("cascade_")},
            "irt_router": {key: value["validation"] for key, value in policies.items() if key.startswith("irt_router_")},
        },
        "caveats": [
            "MMLU dev provides only five task-specific training examples per selected subject; static per-task choice is noisy.",
            "Confidence is an uncalibrated next-token choice-mass proxy, not a model-provided calibrated probability.",
            "The FAST->DEEP cascade charges both measured inference calls; model loading is excluded under a resident-model-pool assumption.",
            "Latency is local sequential MPS inference and not cloud price or concurrent serving latency.",
            "Test query bootstraps are conditional on this fixed four-task sample and do not establish external validity.",
            "The plurality mechanism requires all three responses and is an ensemble reference, not a low-cost cascade.",
            "Test oracle uses ground truth retrospectively and is not deployable.",
        ],
        "provenance": {"runner": "experiments/run_hls_dynamic_capacity_organization.py",
                       "device": _device(), "inference": "greedy, max_new_tokens=8, identical prompt template",
                       "test_outcome_reproduction_rate": exact_reproduction},
    }
    (out_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    flat_curve_rows = []
    for row in curve_rows:
        flat = {key: row[key] for key in (
            "policy_id", "accuracy", "accuracy_ci95_stratified_query",
            "mean_latency_seconds", "latency_ci95_stratified_query",
            "total_latency_seconds", "deep_activation_rate",
        )}
        flat.update({f"accuracy_{task}": value for task, value in row["per_task_accuracy"].items()})
        deep_delta = row["paired_accuracy_delta_vs_baselines"]["deep_always"]
        flat["accuracy_delta_vs_deep"] = deep_delta["mean"]
        flat["accuracy_delta_vs_deep_ci95"] = deep_delta["ci95"]
        latency_delta = row["paired_latency_delta_seconds_vs_baselines"]["deep_always"]
        flat["latency_delta_seconds_vs_deep"] = latency_delta["mean"]
        flat["latency_delta_seconds_vs_deep_ci95"] = latency_delta["ci95"]
        if "validation" in policies[row["policy_id"]]:
            flat.update({f"validation_{key}": value for key, value in
                         policies[row["policy_id"]]["validation"].items()})
        flat_curve_rows.append(flat)
    pd.DataFrame(flat_curve_rows).to_csv(out_dir / "quality_cost_curve_summary.csv", index=False)
    (out_dir / "experiment_runs.json").write_text(
        json.dumps([value["run"].to_dict() for value in policies.values()],
                   indent=2, sort_keys=True) + "\n"
    )
    source_inputs = [
        OUT.parent / "hls_budgeted_llm_routing_pilot" / "model_outcomes.csv",
        OUT.parent / "hls_budgeted_llm_routing_pilot" / "quality_cost_predictions.csv",
        ROOT / "src/hls/dynamic_capacity_organization.py",
        ROOT / "experiments/run_hls_dynamic_capacity_organization.py",
    ]
    output_files = [
        out_dir / "model_scoring_cache.jsonl",
        out_dir / "model_outputs_and_confidence.csv.gz",
        out_dir / "results.json",
        out_dir / "quality_cost_curve_summary.csv",
        out_dir / "experiment_runs.json",
    ]
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in source_inputs + output_files}
    (out_dir / "artifact_hashes.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    summary = run_experiment()
    print(json.dumps({"experiment": summary["experiment"], "status": summary["status"],
                      "output_dir": str(OUT), "n_test": summary["dataset"]["n_test"],
                      "n_policies": len(summary["curves"])}, indent=2))
