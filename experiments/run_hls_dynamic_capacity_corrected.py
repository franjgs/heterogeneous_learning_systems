"""Controlled corrected MMLU evaluation for dynamic capacity organization.

The benchmark is a four-choice task. Each model makes one forward pass over
the same prompt and its next-token mass over A-D is scored. No free-form
generation or artificial latency is used. Train/validation are processed and
the pair/policy parameters are frozen before test rows are loaded.
"""

from __future__ import annotations

import gc
import hashlib
import json
import os
import platform
import random
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
    select_train_validation_tradeoff_pair, sequential_cascade_cost, static_model_by_task,
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
from run_hls_dynamic_capacity_organization import (  # noqa: E402
    _encode_prompt, _load_split,
)

OUT = ROOT / "results/experiments/hls_dynamic_capacity_organization_corrected"
TARGET_RATES = tuple(float(x) for x in np.linspace(0, 1, 11))
COST_FRACTIONS = tuple(float(x) for x in np.linspace(0, 1, 11))
LATENCY_REPETITIONS = 3
TEST_LATENCY_REPETITIONS = 3
BOOTSTRAPS = 5000
SEED = 20261023
CORRECTED_TEST_SEED = 20261025


def _load_train_auxiliary() -> pd.DataFrame:
    local = hf_hub_download(DATASET_ID, "all/auxiliary_train-00000-of-00001.parquet",
                            repo_type="dataset", revision=DATASET_REVISION)
    frame = pd.read_parquet(local)
    frame = frame.sample(n=200, random_state=TRAIN_SEED).reset_index(drop=False)
    frame = frame.rename(columns={"index": "source_index"})
    frame["split"] = "auxiliary_train"
    frame["task_type"] = "mmlu_auxiliary_mixed"
    frame["query_id"] = [
        _qid("auxiliary_train", "mixed", row.source_index, row.question, list(row.choices))
        for row in frame.itertuples()
    ]
    return frame


def _build_train_validation() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    auxiliary = _load_train_auxiliary()
    dev = _load_split("all/dev-00000-of-00001.parquet", "train")
    validation = _load_split("all/validation-00000-of-00001.parquet", "validation")
    dev = dev.groupby("task_type", sort=True, group_keys=False).head(5).reset_index(drop=True)
    validation = (validation.groupby("task_type", group_keys=False)
                  .sample(n=22, random_state=SEED)
                  .sort_values(["task_type", "source_index"]).reset_index(drop=True))
    _assert_content_disjoint({"auxiliary_train": auxiliary, "dev": dev, "validation": validation})
    return auxiliary, dev, validation


def _assert_content_disjoint(partitions: dict[str, pd.DataFrame]) -> None:
    """Check actual question/options content; query IDs include split names."""
    content = {}
    for name, frame in partitions.items():
        content[name] = {
            hashlib.sha256(json.dumps([str(row.question), list(row.choices)], ensure_ascii=False)
                           .encode("utf-8")).hexdigest()
            for row in frame.itertuples()
        }
    names = sorted(content)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1:]:
            if content[left] & content[right]:
                raise AssertionError(f"content overlap between {left} and {right}")


def _content_hash(question: str, choices: list[str]) -> str:
    return hashlib.sha256(json.dumps([str(question), list(choices)], ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def _load_fresh_test() -> pd.DataFrame:
    """Sample official test queries not used in the earlier MMLU pilot."""
    from run_hls_budgeted_llm_routing_pilot import load_pilot_data

    _, previous_test = load_pilot_data()
    previous_content = {_content_hash(row.question, row.choices)
                        for row in previous_test.itertuples()}
    official_test = _load_split("all/test-00000-of-00001.parquet", "test")
    eligible = official_test[
        ~official_test.apply(lambda row: _content_hash(row.question, row.choices)
                             in previous_content, axis=1)
    ].copy()
    fresh = (eligible.groupby("task_type", group_keys=False)
             .sample(n=40, random_state=CORRECTED_TEST_SEED)
             .sort_values(["task_type", "source_index"]).reset_index(drop=True))
    if len(fresh) != 160:
        raise AssertionError(f"expected 160 fresh test questions, found {len(fresh)}")
    return fresh


def _candidate_tokens(tokenizer: Any) -> dict[str, tuple[int, ...]]:
    tokens: dict[str, tuple[int, ...]] = {}
    for letter in "ABCD":
        ids = set()
        for text in (letter, " " + letter):
            candidate = tokenizer.encode(text, add_special_tokens=False)
            if len(candidate) != 1:
                raise ValueError(f"{tokenizer.name_or_path}: {text!r} must be exactly one token")
            ids.add(int(candidate[0]))
        tokens[letter] = tuple(sorted(ids))
    return tokens


def _sync(device: str) -> None:
    if device == "mps":
        torch.mps.synchronize()


def _score_one(model_id: str, model: Any, tokenizer: Any,
               letter_tokens: dict[str, tuple[int, ...]], row: Any,
               device: str) -> dict[str, Any]:
    encoded = _encode_prompt(tokenizer, row, device)
    _sync(device)
    start = time.perf_counter()
    with torch.inference_mode():
        logits = model(**encoded, use_cache=False).logits[0, -1].float()
        token_ids = sorted({token for values in letter_tokens.values() for token in values})
        candidate_probs = torch.softmax(logits[token_ids], dim=-1)
        by_token = {token: float(candidate_probs[i].item()) for i, token in enumerate(token_ids)}
        masses = {letter: float(sum(by_token[token] for token in ids))
                  for letter, ids in letter_tokens.items()}
        denominator = sum(masses.values())
        probabilities = {letter: value / denominator for letter, value in masses.items()}
        prediction = max("ABCD", key=lambda letter: (probabilities[letter], -ord(letter)))
        confidence = probabilities[prediction]
    _sync(device)
    elapsed = time.perf_counter() - start
    return {
        "query_id": row.query_id, "split": row.split, "task_type": row.task_type,
        "model_id": model_id, "model_revision": MODEL_REVISIONS[model_id],
        "predicted_letter": prediction, "correct_letter": "ABCD"[int(row.answer)],
        "correct": int(prediction == "ABCD"[int(row.answer)]),
        "choice_probabilities": probabilities, "confidence": confidence,
        "input_tokens": int(encoded["input_ids"].shape[1]), "scored_answer_tokens": 1,
        "latency_seconds": float(elapsed),
    }


def _load_model_pool(device: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, tuple[int, ...]]], dict[str, dict[str, float]]]:
    models, tokenizers, choice_tokens, specs = {}, {}, {}, {}
    memory_before = int(torch.mps.driver_allocated_memory()) if device == "mps" else None
    for model_id in MODEL_IDS:
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=MODEL_REVISIONS[model_id])
        load_start = time.perf_counter()
        model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=MODEL_REVISIONS[model_id], torch_dtype=torch.float16,
            low_cpu_mem_usage=False,
        ).to(device)
        model.eval()
        _sync(device)
        load_seconds = time.perf_counter() - load_start
        param_count = sum(int(p.numel()) for p in model.parameters())
        weight_bytes = sum(int(p.numel() * p.element_size()) for p in model.parameters())
        models[model_id] = model
        tokenizers[model_id] = tokenizer
        choice_tokens[model_id] = _candidate_tokens(tokenizer)
        driver_bytes = int(torch.mps.driver_allocated_memory()) if device == "mps" else None
        specs[model_id] = {
            "model_revision": MODEL_REVISIONS[model_id], "parameter_count": param_count,
            "loaded_parameter_bytes": weight_bytes, "dtype": "float16",
            "backend": "Transformers eager forward", "device": device,
            "load_seconds_excluded_from_request_latency": float(load_seconds),
            "mps_driver_allocated_bytes_after_load": driver_bytes,
        }
    if device == "mps":
        specs["pool"] = {"driver_memory_before_bytes": memory_before,
                         "driver_memory_after_pool_bytes": int(torch.mps.driver_allocated_memory())}
    return models, tokenizers, choice_tokens, specs


def _append_cache(path: Path, rows: dict[tuple[str, str], dict[str, Any]]) -> None:
    with path.open("w") as stream:
        for row in rows.values():
            stream.write(json.dumps(row, sort_keys=True) + "\n")


def _score_train_validation(
    auxiliary: pd.DataFrame, dev: pd.DataFrame, validation: pd.DataFrame,
    models: dict[str, Any], tokenizers: dict[str, Any],
    choice_tokens: dict[str, dict[str, tuple[int, ...]]], device: str, out_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_frame = pd.concat([auxiliary, dev, validation], ignore_index=True)
    cache_path = out_dir / "train_validation_scores.jsonl"
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    if cache_path.exists():
        for line in cache_path.read_text().splitlines():
            row = json.loads(line)
            cache[(row["query_id"], row["model_id"])] = row
    model_index = {mid: i for i, mid in enumerate(MODEL_IDS)}
    # Three warm-up calls per model, before any characterized measurements.
    for model_id in MODEL_IDS:
        warmups = []
        model_rows = auxiliary.iloc[:3]
        for row in model_rows.itertuples():
            warmups.append(_score_one(model_id, models[model_id], tokenizers[model_id],
                                      choice_tokens[model_id], row, device))
        _sync(device)
    # One timed score per train/validation query. Model order rotates by query.
    for row_index, row in enumerate(all_frame.itertuples()):
        rotation = row_index % len(MODEL_IDS)
        order = MODEL_IDS[rotation:] + MODEL_IDS[:rotation]
        for model_id in order:
            key = (row.query_id, model_id)
            if key not in cache:
                cache[key] = _score_one(model_id, models[model_id], tokenizers[model_id],
                                        choice_tokens[model_id], row, device)
        if row_index % 50 == 0:
            _append_cache(cache_path, cache)
    _append_cache(cache_path, cache)

    # Counterbalanced, repeated validation timings; query labels are not used.
    repeat_path = out_dir / "validation_latency_repetitions.csv"
    repeats = pd.read_csv(repeat_path) if repeat_path.exists() else pd.DataFrame()
    expected_repeats = len(validation) * len(MODEL_IDS) * LATENCY_REPETITIONS
    if (len(repeats) != expected_repeats
            or set(repeats.query_id) != set(validation.query_id)
            or not repeats.prediction_match_base.astype(bool).all()):
        repeated_rows = []
        rng = np.random.default_rng(SEED)
        for repetition in range(LATENCY_REPETITIONS):
            query_order = rng.permutation(len(validation))
            for ordinal, query_idx in enumerate(query_order):
                row = next(validation.iloc[[int(query_idx)]].itertuples())
                rotation = (ordinal + repetition) % len(MODEL_IDS)
                order = MODEL_IDS[rotation:] + MODEL_IDS[:rotation]
                for model_id in order:
                    result = _score_one(model_id, models[model_id], tokenizers[model_id],
                                        choice_tokens[model_id], row, device)
                    repeated_rows.append({"query_id": row.query_id, "task_type": row.task_type,
                                          "model_id": model_id, "repetition": repetition,
                                          "latency_seconds": result["latency_seconds"],
                                          "prediction_match_base": result["predicted_letter"] == cache[(row.query_id, model_id)]["predicted_letter"]})
        repeats = pd.DataFrame(repeated_rows)
        repeats.to_csv(repeat_path, index=False)
    score_frame = pd.DataFrame(cache.values())
    score_frame.to_csv(out_dir / "train_validation_scores.csv.gz", index=False, compression="gzip")
    return score_frame, repeats


def _pivot(frame: pd.DataFrame, rows: pd.DataFrame, column: str) -> np.ndarray:
    pivot = frame.pivot(index="query_id", columns="model_id", values=column)
    return pivot.loc[rows.query_id, list(MODEL_IDS)].to_numpy()


def _write_run(policy_id: str, test: pd.DataFrame, predictions: np.ndarray,
               costs: np.ndarray, selected_paths: list[str], confidence: np.ndarray,
               escalated: np.ndarray, output_dir: Path,
               selected_pair: tuple[str, str]) -> tuple[dict[str, Any], ExperimentRun]:
    scenario = "mmlu_dynamic_capacity_corrected_v2"
    config_id = f"{DATASET_REVISION}-direct-choice-score-test160"
    if policy_id.startswith("irt_router_"):
        objective = "argmax MIRT-predicted correctness minus validation-fitted price times train-predicted latency"
    elif policy_id.startswith("cascade_"):
        objective = "accept A unless observable A confidence is below validation-fitted threshold; then execute B and return B"
    elif policy_id == "static_best_by_task":
        objective = "fixed model per task with highest train accuracy on official dev partition"
    elif policy_id == "capacity_a_always":
        objective = "always execute selected lower-cost capability A"
    elif policy_id == "capacity_b_always":
        objective = "always execute selected higher-quality capability B"
    elif policy_id.startswith("fixed_candidate_"):
        objective = "always execute a fixed candidate model; descriptive capacity baseline"
    elif policy_id == "all_model_plurality":
        objective = "plurality vote over all model choices; ties use B; execute all candidates"
    else:
        objective = "retrospective oracle chooses fastest correct candidate, or fastest when all fail"
    information = "test task and question observed; model logits available only after invoked capacity; answer key evaluation-only"
    profile = EvaluationProfile(
        profile_id=f"{policy_id}-corrected-profile", scenario_id=scenario,
        configuration_id=config_id, application_domain="local open-weight LLM multiple-choice inference",
        organizational_problem="select, escalate or combine heterogeneous model capabilities per query",
        decision_objective={policy_id: objective},
        constraints="one final MMLU answer; sequential escalation pays for initial A and invoked B",
        primary_metrics=("functional_success_rate",),
        secondary_metrics=("original_reward_cumulative", "resource_usage:inference_latency_seconds"),
        information_regime=information, temporal_horizon=len(test),
        aggregation_rules="one MMLU question per period; direct next-token A-D score; costs sum invoked forward-pass times",
            demand_distribution_id=f"mmlu-official-four-subject-test160-seed-{CORRECTED_TEST_SEED}",
        resource_units={"inference_latency_seconds": "seconds"},
    )
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    records, events = [], []
    for i, row in enumerate(test.itertuples()):
        ok = bool(predictions[i] == "ABCD"[int(row.answer)])
        score_metadata = ({"A_confidence": float(confidence[i])}
                          if policy_id.startswith("cascade_") else {})
        records.append(EvaluationRecord(
            scenario_id=scenario, configuration_id=config_id, policy_id=policy_id,
            period=i, demand=row.task_type, success=ok, original_reward=float(ok),
            resource_usage={"inference_latency_seconds": float(costs[i])},
            provenance=f"cais/mmlu@{DATASET_REVISION}#test:{row.query_id}:{policy_id}",
            unit_id=row.query_id, task_type=row.task_type, quality=float(ok),
            information_regime=information, decision_objective=objective,
            available_metadata={"selected_path": selected_paths[i],
                                "B_activated": bool(escalated[i]), **score_metadata},
        ))
        events.append(ExperimentEvent(
            sequence_index=i, time_index=i, event_type="capacity_decision",
            mechanism_id=policy_id,
            data={"query_id": row.query_id, "task_type": row.task_type,
                  "selected_path": selected_paths[i], "B_activated": bool(escalated[i]),
                  "invoked_latency_seconds": float(costs[i]), **score_metadata},
        ))
    evaluated = evaluator.evaluate(profile.profile_id, policy_id, records)
    metrics = {k: {"value": v.value, "unit": v.unit, "status": v.status.value,
                   "aggregation": v.aggregation} for k, v in evaluated.items()}
    run = ExperimentRun(
        schema_version=SCHEMA_VERSION, run_id=policy_id, mechanism_id=policy_id, policy_id=policy_id,
        configuration={"scenario": scenario, "dataset_revision": DATASET_REVISION,
                       "capacity_A": selected_pair[0], "capacity_B": selected_pair[1],
                       "candidate_models": list(MODEL_IDS),
                       "model_revisions": dict(MODEL_REVISIONS),
                       "dtype": "float16", "device": _device(), "test_n": len(test),
                       "inference_protocol": "single forward pass, normalized A-D next-token masses"},
        initial_conditions={"test_query_ids_sha256": hashlib.sha256("\n".join(test.query_id).encode()).hexdigest()},
        random_seeds=(SeedRecord(stream="test_selection", value=CORRECTED_TEST_SEED,
                                 purpose="fresh official test sample excluding earlier pilot items"),),
        information_available={"test_answer_key": "evaluation-only", "A_logits": "available after A call", "B_logits": "available only if escalated"},
        observation_model={"inference": "causal-LM forward pass; no autoregressive generation",
                           "confidence": "conditional A-D mass from A logits"},
        software_revision=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                         capture_output=True, text=True).stdout.strip() or None,
        units=(UnitDeclaration("accuracy", "fraction", "MMLU exact answer-letter match"),
               UnitDeclaration("latency", "seconds", "sum of measured invoked model forward passes")),
        events=tuple(events),
        metrics=(MetricValue("functional_success_rate", metrics["functional_success_rate"]["value"],
                             "fraction", "exact answer-letter match", "higher"),
                 MetricValue("total_latency_seconds", metrics["resource_usage:inference_latency_seconds"]["value"],
                             "seconds", "sum of costs for invoked model calls", "lower")),
        mechanism_results={"hls_pef_metrics": metrics},
        metadata={"profile_id": profile.profile_id, "policy_uses_test_labels": False,
                  "answer_key_used_only_after_selection": True},
    )
    return metrics, run


def run_experiment(out_dir: Path = OUT) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    device = _device()
    auxiliary, dev, validation = _build_train_validation()
    # Only train and validation are loaded/scored before freezing the pair and policies.
    models, tokenizers, choice_tokens, model_specs = _load_model_pool(device)
    scores_train_val, repeated_times = _score_train_validation(
        auxiliary, dev, validation, models, tokenizers, choice_tokens, device, out_dir,
    )
    train_out = scores_train_val[scores_train_val.query_id.isin(auxiliary.query_id)]
    dev_out = scores_train_val[scores_train_val.query_id.isin(dev.query_id)]
    val_out = scores_train_val[scores_train_val.query_id.isin(validation.query_id)]

    train_correct = train_out.pivot(index="query_id", columns="model_id", values="correct").loc[auxiliary.query_id, list(MODEL_IDS)].to_numpy(dtype=int)
    train_time = train_out.pivot(index="query_id", columns="model_id", values="latency_seconds").loc[auxiliary.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    val_correct = val_out.pivot(index="query_id", columns="model_id", values="correct").loc[validation.query_id, list(MODEL_IDS)].to_numpy(dtype=int)
    val_repeated_mean = repeated_times.groupby("model_id").latency_seconds.mean().reindex(MODEL_IDS)
    train_accuracy_by_model = {m: float(train_correct[:, j].mean()) for j, m in enumerate(MODEL_IDS)}
    train_latency_by_model = {m: float(train_time[:, j].mean()) for j, m in enumerate(MODEL_IDS)}
    validation_accuracy_by_model = {m: float(val_correct[:, j].mean()) for j, m in enumerate(MODEL_IDS)}
    validation_latency_by_model = {m: float(val_repeated_mean[m]) for m in MODEL_IDS}
    pair = select_train_validation_tradeoff_pair(
        MODEL_IDS, train_accuracy_by_model, train_latency_by_model,
        validation_accuracy_by_model, validation_latency_by_model,
    )
    capability_table = []
    for j, model_id in enumerate(MODEL_IDS):
        one = repeated_times[repeated_times.model_id == model_id].latency_seconds.to_numpy()
        capability_table.append({
            "model_id": model_id, "parameters": model_specs[model_id]["parameter_count"],
            "train_accuracy": train_accuracy_by_model[model_id],
            "train_mean_latency_seconds": train_latency_by_model[model_id],
            "validation_accuracy": validation_accuracy_by_model[model_id],
            "validation_latency_mean_seconds": float(np.mean(one)),
            "validation_latency_median_seconds": float(np.median(one)),
            "validation_latency_p95_seconds": float(np.quantile(one, 0.95)),
            "validation_latency_sd_seconds": float(np.std(one, ddof=1)),
            "validation_memory_parameter_bytes": model_specs[model_id]["loaded_parameter_bytes"],
        })
    if pair is None:
        result = {
            "status": "no_train_validation_tradeoff_pair",
            "dataset_revision": DATASET_REVISION,
            "train_n": len(auxiliary), "validation_n": len(validation),
            "capability_characterization": capability_table,
            "model_specs": model_specs,
            "inference_protocol": "one causal-LM forward pass; normalized A-D next-token mass; no autoregressive generation",
            "interpretation": "No candidate pair has B more accurate and slower than A on both train and validation; no test was loaded or executed.",
        }
        (out_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        raise RuntimeError("no capacity pair satisfies the predeclared train/validation tradeoff; characterization saved")

    a_model, b_model = pair
    # Freeze model pair, static selector, quality/cost predictors and thresholds before test is loaded.
    dev_y = dev_out.pivot(index="query_id", columns="model_id", values="correct").loc[dev.query_id, list(MODEL_IDS)].to_numpy(dtype=int)
    static_choice_validation_template, static_mapping = static_model_by_task(
        dev.task_type, dev_y, validation.task_type, MODEL_IDS,
    )
    static_train_choices = static_mapping
    mirt = MIRTQualityPredictor(seed=TRAIN_SEED).fit(
        request_features(auxiliary), MODEL_IDS, train_correct,
    )
    val_qhat = mirt.predict(request_features(validation))
    train_tokens = train_out.pivot(index="query_id", columns="model_id", values="input_tokens").loc[auxiliary.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    latency_coefficients = predict_latency(train_tokens, train_time)
    val_tokens = val_out.pivot(index="query_id", columns="model_id", values="input_tokens").loc[validation.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    val_costhat = apply_latency(val_tokens, latency_coefficients)
    router_parameters = {}
    for fraction in COST_FRACTIONS:
        price, val_cost = fit_router_price(val_qhat, val_costhat, fraction)
        router_parameters[f"{fraction:.1f}"] = {"lambda": price, "validation_predicted_mean_cost": val_cost}
    val_conf_matrix = val_out.pivot(index="query_id", columns="model_id", values="confidence").loc[validation.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    a_idx, b_idx = MODEL_IDS.index(a_model), MODEL_IDS.index(b_model)
    cascade_thresholds = {}
    for rate in TARGET_RATES:
        threshold = fit_escalation_threshold(val_conf_matrix[:, a_idx], rate)
        cascade_thresholds[f"{rate:.1f}"] = {"threshold": threshold.threshold,
                                               "target_validation_rate": rate,
                                               "achieved_validation_rate": threshold.validation_escalation_rate}
    static_cfg = {"task_to_model": static_train_choices,
                  "train_examples_by_task": {str(task): int((dev.task_type == task).sum())
                                             for task in sorted(set(dev.task_type))}}
    locked = {
        "dataset_revision": DATASET_REVISION, "selected_A": a_model, "selected_B": b_model,
        "test_selection_seed": CORRECTED_TEST_SEED,
        "test_selection_rule": "40 official test items per subject; exclude prior pilot questions by content",
        "pair_selection": "B is more accurate and slower than A on both train and validation; eligible pair ranked by highest train accuracy of B, then B latency, then A latency",
        "train_accuracy": train_accuracy_by_model, "train_latency_mean": train_latency_by_model,
        "validation_accuracy": validation_accuracy_by_model,
        "validation_latency_mean_repeated": validation_latency_by_model,
        "static_selector": static_cfg, "router_parameters": router_parameters,
        "cascade_thresholds": cascade_thresholds,
        "irt_fit_info": mirt.fit_info,
        "cost_model_coefficients": {"slope": latency_coefficients[0].tolist(),
                                     "intercept": latency_coefficients[1].tolist()},
        "locked_before_test_loaded": True,
    }
    (out_dir / "locked_train_validation_configuration.json").write_text(json.dumps(locked, indent=2, sort_keys=True) + "\n")
    for model in models.values():
        del model
    models.clear()
    tokenizers.clear()
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    # Test is loaded only after the pair and all tunable parameters are frozen.
    test = _load_fresh_test()
    _assert_content_disjoint({"auxiliary_train": auxiliary, "dev": dev,
                              "validation": validation, "test": test})
    models, tokenizers, choice_tokens, test_specs = _load_model_pool(device)
    # Warm-up before test timing. It uses already-seen train queries, never test labels.
    for model_id in MODEL_IDS:
        for row in auxiliary.iloc[:3].itertuples():
            _score_one(model_id, models[model_id], tokenizers[model_id],
                       choice_tokens[model_id], row, device)
    test_rows = []
    for i, row in enumerate(test.itertuples()):
        rotation = i % len(MODEL_IDS)
        order = MODEL_IDS[rotation:] + MODEL_IDS[:rotation]
        for model_id in order:
            test_rows.append(_score_one(model_id, models[model_id], tokenizers[model_id],
                                        choice_tokens[model_id], row, device))
    test_out = pd.DataFrame(test_rows)
    test_out.to_csv(out_dir / "test_model_scores.csv.gz", index=False, compression="gzip")
    test_letters = test_out.pivot(index="query_id", columns="model_id", values="predicted_letter").loc[test.query_id, list(MODEL_IDS)].to_numpy(dtype=str)
    test_y = test_out.pivot(index="query_id", columns="model_id", values="correct").loc[test.query_id, list(MODEL_IDS)].to_numpy(dtype=int)
    test_conf = test_out.pivot(index="query_id", columns="model_id", values="confidence").loc[test.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    # Repeated test timing uses test inputs only as workload, never answer labels.
    # Per-query medians reduce sensitivity to transient device/OS stalls while
    # keeping the latency estimate matched to the exact queries being evaluated.
    timing_rows = []
    timing_rng = np.random.default_rng(SEED + 17)
    base_predictions = test_out.pivot(index="query_id", columns="model_id", values="predicted_letter").loc[test.query_id, list(MODEL_IDS)]
    for repetition in range(TEST_LATENCY_REPETITIONS):
        query_order = timing_rng.permutation(len(test))
        for ordinal, query_idx in enumerate(query_order):
            row = next(test.iloc[[int(query_idx)]].itertuples())
            rotation = (ordinal + repetition) % len(MODEL_IDS)
            order = MODEL_IDS[rotation:] + MODEL_IDS[:rotation]
            for model_id in order:
                scored = _score_one(model_id, models[model_id], tokenizers[model_id],
                                    choice_tokens[model_id], row, device)
                expected = base_predictions.loc[row.query_id, model_id]
                if scored["predicted_letter"] != expected:
                    raise AssertionError("repeated deterministic test score changed prediction")
                timing_rows.append({"query_id": row.query_id, "task_type": row.task_type,
                                    "model_id": model_id, "repetition": repetition,
                                    "latency_seconds": scored["latency_seconds"],
                                    "prediction_match_base": True})
    test_repeats = pd.DataFrame(timing_rows)
    test_repeats.to_csv(out_dir / "test_latency_repetitions.csv", index=False)
    test_median_latency = test_repeats.groupby(["query_id", "model_id"]).latency_seconds.median()
    test_time = np.asarray([[test_median_latency.loc[(qid, model_id)] for model_id in MODEL_IDS]
                            for qid in test.query_id], dtype=float)
    test_tokens = test_out.pivot(index="query_id", columns="model_id", values="input_tokens").loc[test.query_id, list(MODEL_IDS)].to_numpy(dtype=float)
    test_qhat = mirt.predict(request_features(test))
    test_costhat = apply_latency(test_tokens, latency_coefficients)
    tasks = test.task_type.to_numpy(dtype=str)
    truth = np.asarray(["ABCD"[int(answer)] for answer in test.answer], dtype=str)

    outputs: dict[str, dict[str, Any]] = {}
    def add_policy(policy_id: str, prediction: np.ndarray, cost: np.ndarray,
                   paths: list[str], conf: np.ndarray | None = None,
                   escalated: np.ndarray | None = None) -> None:
        conf = np.zeros(len(test)) if conf is None else np.asarray(conf, dtype=float)
        escalated = np.zeros(len(test), dtype=bool) if escalated is None else np.asarray(escalated, dtype=bool)
        metrics, run = _write_run(policy_id, test, prediction, cost, paths, conf,
                                  escalated, out_dir, (a_model, b_model))
        outputs[policy_id] = {"prediction": np.asarray(prediction, dtype=str), "cost": np.asarray(cost, dtype=float),
                              "paths": paths, "metrics": metrics, "run": run, "escalated": escalated}

    a_pred, b_pred = test_letters[:, a_idx], test_letters[:, b_idx]
    a_conf = test_conf[:, a_idx]
    a_time, b_time = test_time[:, a_idx], test_time[:, b_idx]
    add_policy("capacity_a_always", a_pred, a_time, [a_model] * len(test))
    add_policy("capacity_b_always", b_pred, b_time, [b_model] * len(test))
    for model_index, model_id in enumerate(MODEL_IDS):
        if model_id not in {a_model, b_model}:
            add_policy("fixed_candidate_qwen_0_5b_always",
                       test_letters[:, model_index], test_time[:, model_index],
                       [model_id] * len(test), test_conf[:, model_index])
    static_idx, _ = static_model_by_task(dev.task_type, dev_y, test.task_type, MODEL_IDS)
    add_policy("static_best_by_task", test_letters[np.arange(len(test)), static_idx],
               test_time[np.arange(len(test)), static_idx], [MODEL_IDS[j] for j in static_idx])

    for fraction in COST_FRACTIONS:
        cfg = router_parameters[f"{fraction:.1f}"]
        chosen = irt_route(test_qhat, test_costhat, float(cfg["lambda"]))
        add_policy(f"irt_router_cost_fraction_{fraction:.1f}",
                   test_letters[np.arange(len(test)), chosen],
                   test_time[np.arange(len(test)), chosen], [MODEL_IDS[j] for j in chosen])
        outputs[f"irt_router_cost_fraction_{fraction:.1f}"]["validation_parameters"] = cfg

    for rate in TARGET_RATES:
        cfg = cascade_thresholds[f"{rate:.1f}"]
        prediction, escalated = cascade_predictions(a_pred, a_conf, b_pred, cfg["threshold"])
        actual_cost = sequential_cascade_cost(a_time, b_time, escalated)
        paths = [f"{a_model}>{b_model}" if flag else a_model for flag in escalated]
        policy_id = f"cascade_target_rate_{rate:.1f}"
        add_policy(policy_id, prediction, actual_cost, paths, a_conf, escalated)
        outputs[policy_id]["validation_parameters"] = cfg

    majority = majority_vote(test_letters, b_idx)
    add_policy("all_model_plurality", majority, test_time.sum(axis=1),
               ["+".join(MODEL_IDS)] * len(test))
    oracle_indices = np.asarray([
        min(np.flatnonzero(test_y[i]), key=lambda j: (test_time[i, j], j))
        if test_y[i].any() else int(np.argmin(test_time[i])) for i in range(len(test))
    ], dtype=int)
    add_policy("test_oracle_fastest_correct", test_letters[np.arange(len(test)), oracle_indices],
               test_time[np.arange(len(test)), oracle_indices], [MODEL_IDS[j] for j in oracle_indices])

    # Pairwise outcome and latency comparisons are query-paired and stratified by task.
    baseline_ids = ["capacity_a_always", "capacity_b_always", "static_best_by_task", "all_model_plurality"]
    curve = []
    a_correct, b_correct = test_y[:, a_idx].astype(bool), test_y[:, b_idx].astype(bool)
    for policy_id, policy in outputs.items():
        pred = policy["prediction"]
        ok = (pred == truth).astype(float)
        casc = policy_id.startswith("cascade_")
        escalated = policy["escalated"]
        row = {
            "policy_id": policy_id, "accuracy": float(ok.mean()),
            "accuracy_ci95_stratified_query": list(paired_stratified_bootstrap_delta(
                ok, np.zeros_like(ok), tasks, n_boot=BOOTSTRAPS, seed=SEED + 1)[1:]),
            "mean_latency_seconds": float(policy["cost"].mean()),
            "latency_ci95_stratified_query": list(paired_stratified_bootstrap_delta(
                policy["cost"], np.zeros_like(policy["cost"]), tasks, n_boot=BOOTSTRAPS, seed=SEED + 2)[1:]),
            "per_task_accuracy": per_task_accuracy(pred, truth, tasks),
            "B_activation_rate": float(escalated.mean()) if casc else
                                  1.0 if policy_id in {"capacity_b_always", "all_model_plurality"} else
                                  float(np.mean([p == b_model for p in policy["paths"]])),
        }
        if casc:
            row["escalated_outcomes"] = {
                "activated": int(escalated.sum()),
                "B_corrects_A_error": int(np.sum(escalated & ~a_correct & b_correct)),
                "A_correct_B_also_correct": int(np.sum(escalated & a_correct & b_correct)),
                "B_harms_correct_A": int(np.sum(escalated & a_correct & ~b_correct)),
                "both_wrong": int(np.sum(escalated & ~a_correct & ~b_correct)),
            }
        row["paired_vs"] = {}
        for baseline in baseline_ids:
            base = outputs[baseline]
            delta, low, high = paired_stratified_bootstrap_delta(
                ok, (base["prediction"] == truth).astype(float), tasks,
                n_boot=BOOTSTRAPS, seed=SEED + sum(map(ord, policy_id + baseline)),
            )
            dcost, clow, chigh = paired_stratified_bootstrap_delta(
                policy["cost"], base["cost"], tasks,
                n_boot=BOOTSTRAPS, seed=SEED + 300 + sum(map(ord, policy_id + baseline)),
            )
            row["paired_vs"][baseline] = {"accuracy_delta": delta, "accuracy_ci95": [low, high],
                                            "latency_delta_seconds": dcost,
                                            "latency_ci95": [clow, chigh]}
        curve.append(row)

    # FAST/B errors are evaluated only after decisions and thresholds are frozen.
    complement = {
        "both_correct": int(np.sum(a_correct & b_correct)),
        "A_only_correct": int(np.sum(a_correct & ~b_correct)),
        "B_only_correct": int(np.sum(~a_correct & b_correct)),
        "neither_correct": int(np.sum(~a_correct & ~b_correct)),
        "A_accuracy": float(a_correct.mean()), "B_accuracy": float(b_correct.mean()),
        "B_minus_A_accuracy_ci95": list(paired_stratified_bootstrap_delta(
            b_correct, a_correct, tasks, n_boot=BOOTSTRAPS, seed=SEED + 4)),
        "by_task": {},
    }
    for task in sorted(set(tasks.tolist())):
        mask = tasks == task
        complement["by_task"][task] = {"n": int(mask.sum()),
            "A_accuracy": float(a_correct[mask].mean()), "B_accuracy": float(b_correct[mask].mean()),
            "A_only_correct": int(np.sum(a_correct[mask] & ~b_correct[mask])),
            "B_only_correct": int(np.sum(~a_correct[mask] & b_correct[mask]))}
    a_validation_conf = val_out.pivot(index="query_id", columns="model_id", values="confidence").loc[validation.query_id, list(MODEL_IDS)].to_numpy(float)[:, a_idx]
    a_validation_y = val_correct[:, a_idx]
    test_confidence_diagnostics = {
        "validation_brier": float(np.mean((a_validation_conf - a_validation_y) ** 2)),
        "validation_error_auc": float(roc_auc_score(1 - a_validation_y, 1 - a_validation_conf)),
        "test_brier_evaluation_only": float(np.mean((test_conf[:, a_idx] - test_y[:, a_idx]) ** 2)),
        "test_error_auc_evaluation_only": float(roc_auc_score(1 - test_y[:, a_idx], 1 - test_conf[:, a_idx])),
    }
    old_models_specs = {
        model: model_specs[model] for model in MODEL_IDS
    }
    result = {
        "status": "completed", "experiment": "HLS dynamic capacity corrected evaluation",
        "dataset": {"id": DATASET_ID, "revision": DATASET_REVISION,
                    "train": {"auxiliary_n": len(auxiliary), "task_dev_n": len(dev)},
                    "validation_n": len(validation), "test_n": len(test),
                    "test_subjects": list(TEST_SUBJECTS), "test_seed": CORRECTED_TEST_SEED,
                    "excluded_previous_test_items": 160},
        "inference_configuration": {
            "method": "one causal language model forward pass per query; score A-D next-token masses",
            "autoregressive_generation": False, "scored_answer_tokens": 1,
            "prompt": "same MMLU instruction prompt as prior pilot",
            "dtype": "float16", "device": device, "backend": "Transformers eager forward",
            "warmup_calls_per_model": 3, "validation_latency_repetitions": LATENCY_REPETITIONS,
            "test_latency_repetitions_per_query_model": TEST_LATENCY_REPETITIONS,
            "counterbalanced_model_order": True,
            "request_latency_excludes": ["model loading", "prompt tokenization"],
            "policy_latency_cost": "per-query median of three repeated measured forward-pass times; cascade sums A and activated B serially",
        },
        "hardware": {"platform": platform.platform(), "machine": platform.machine(),
                     "processor": platform.processor(), "cpu_count": os.cpu_count(),
                     "torch_threads": torch.get_num_threads(), "torch_version": torch.__version__,
                     "transformers_version": __import__("transformers").__version__,
                     "mps_available": torch.backends.mps.is_available()},
        "model_specs": old_models_specs,
        "capability_characterization": capability_table,
        "test_latency_characterization": {
            model_id: {
                "mean_of_per_query_medians_seconds": float(np.mean(test_time[:, j])),
                "median_of_per_query_medians_seconds": float(np.median(test_time[:, j])),
                "p95_of_per_query_medians_seconds": float(np.quantile(test_time[:, j], 0.95)),
                "repeat_sd_seconds": float(test_repeats[test_repeats.model_id == model_id].latency_seconds.std(ddof=1)),
            } for j, model_id in enumerate(MODEL_IDS)
        },
        "selected_pair": {"A_lower_cost": a_model, "B_higher_quality": b_model,
                           "selected_on_train_and_validation": True, "locked_configuration": locked},
        "confidence_signal": "normalized softmax mass for the model's selected A-D letter from first next-token logits; observable, uncalibrated",
        "confidence_diagnostics": test_confidence_diagnostics,
        "complementarity": complement,
        "curves": curve,
        "per_policy_hls_pef": {k: v["metrics"] for k, v in outputs.items()},
        "validation_thresholds": cascade_thresholds,
        "validation_router_prices": router_parameters,
        "caveats": [
            "Quality is MMLU exact multiple-choice letter accuracy under direct choice-token scoring, not free-form generation quality.",
            "MMLU dev has five per-task examples for the static selector; that selector is high variance.",
            "Latency is local MPS forward-pass time, excluding loading and tokenization; no energy meter or concurrent serving benchmark was available.",
            "Three validation timing repetitions quantify within-hardware variation; test call times are one measurement per model/query.",
            "Query bootstrap uncertainty is conditional on one fixed 160-query official test subset and does not represent model/dataset/hardware variation.",
            "Test oracle uses the answer key retrospectively and is not deployable.",
        ],
        "provenance": {"runner": "experiments/run_hls_dynamic_capacity_corrected.py",
                       "original_test_outcomes": "read-only; all prior result directories remain unchanged",
                       "locked_before_test": True},
    }
    (out_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    flat = []
    for row in curve:
        base = {k: row[k] for k in ("policy_id", "accuracy", "accuracy_ci95_stratified_query",
                                    "mean_latency_seconds", "latency_ci95_stratified_query", "B_activation_rate")}
        base.update({f"accuracy_{task}": value for task, value in row["per_task_accuracy"].items()})
        for baseline in ("capacity_a_always", "capacity_b_always", "static_best_by_task"):
            pair_delta = row["paired_vs"][baseline]
            base[f"delta_accuracy_vs_{baseline}"] = pair_delta["accuracy_delta"]
            base[f"delta_latency_vs_{baseline}_seconds"] = pair_delta["latency_delta_seconds"]
        if row["policy_id"].startswith("cascade_"):
            base.update({f"escalated_{k}": v for k, v in row["escalated_outcomes"].items()})
        flat.append(base)
    pd.DataFrame(flat).to_csv(out_dir / "quality_cost_curve_summary.csv", index=False)
    (out_dir / "experiment_runs.json").write_text(json.dumps(
        [v["run"].to_dict() for v in outputs.values()], indent=2, sort_keys=True) + "\n")
    # Store exact test predictions after policy definitions are frozen.
    test_out.to_csv(out_dir / "test_model_scores.csv.gz", index=False, compression="gzip")
    source_files = [ROOT / "src/hls/dynamic_capacity_organization.py",
                    ROOT / "experiments/run_hls_dynamic_capacity_corrected.py"]
    output_files = [out_dir / name for name in (
        "train_validation_scores.jsonl", "train_validation_scores.csv.gz",
        "validation_latency_repetitions.csv", "locked_train_validation_configuration.json",
        "test_model_scores.csv.gz", "test_latency_repetitions.csv", "results.json", "quality_cost_curve_summary.csv",
        "experiment_runs.json")]
    manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in source_files + output_files}
    (out_dir / "artifact_hashes.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    summary = run_experiment()
    print(json.dumps({"status": summary["status"], "selected_pair": summary.get("selected_pair"),
                      "n_test": summary.get("dataset", {}).get("test_n"),
                      "n_policies": len(summary.get("curves", [])), "output_dir": str(OUT)}, indent=2))
