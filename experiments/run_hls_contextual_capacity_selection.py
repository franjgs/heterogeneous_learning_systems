"""Evaluate a DCS-LA adaptation on the locked corrected MMLU test sample.

No language-model inference is performed. Model outcomes and repeated
latencies are reused from the corrected pilot; MMLU text is reloaded from its
pinned revision to build contextual features.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "experiments")]

from hls.contextual_capacity_selection import (  # noqa: E402
    DCSLAConfig, DCSLASelector, choose_dcs_config,
)
from hls.experiment_contract import (  # noqa: E402
    SCHEMA_VERSION, ExperimentEvent, ExperimentRun, MetricValue, SeedRecord, UnitDeclaration,
)
from hls.dynamic_capacity_organization import paired_stratified_bootstrap_delta  # noqa: E402
from hls.performance_evaluation import (  # noqa: E402
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator,
)
from run_hls_budgeted_llm_routing_pilot import (  # noqa: E402
    DATASET_ID, DATASET_REVISION, MODEL_IDS, MODEL_REVISIONS,
)
from run_hls_dynamic_capacity_corrected import (  # noqa: E402
    CORRECTED_TEST_SEED, _assert_content_disjoint, _build_train_validation,
    _content_hash, _load_fresh_test,
)

SOURCE = ROOT / "results/experiments/hls_dynamic_capacity_organization_corrected"
OUT = ROOT / "results/experiments/hls_contextual_capacity_selection"
BOOTSTRAPS = 5000
BOOTSTRAP_SEED = 20261023
TEST_TIMING_REPEATS = 7
TASKS = (
    "high_school_biology", "high_school_mathematics",
    "high_school_psychology", "high_school_us_history",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _scores() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_aux, dev, validation = _build_train_validation()
    test = _load_fresh_test()
    train = pd.concat([train_aux, dev], ignore_index=True)
    _assert_content_disjoint({"train": train, "validation": validation, "fresh_test": test})
    cache = pd.read_csv(SOURCE / "train_validation_scores.csv.gz")
    test_cache = pd.read_csv(SOURCE / "test_model_scores.csv.gz")
    repetitions = pd.read_csv(SOURCE / "test_latency_repetitions.csv")
    if set(train.query_id) & set(validation.query_id) or set(train.query_id) & set(test.query_id) or set(validation.query_id) & set(test.query_id):
        raise AssertionError("query IDs overlap across train, validation and test")
    for name, frame in (("train", train), ("validation", validation), ("test", test)):
        observed = set((cache if name != "test" else test_cache).query_id)
        if not set(frame.query_id) <= observed:
            raise AssertionError(f"scores unavailable for some {name} queries")
    if len(test) != 160 or len(repetitions) != 160 * len(MODEL_IDS) * 3:
        raise AssertionError("corrected pilot test or repeated latency artifacts have unexpected size")
    return train, validation, test, cache, test_cache, repetitions


def _aligned_outcomes(frame: pd.DataFrame, scored: pd.DataFrame) -> np.ndarray:
    wide = scored.pivot(index="query_id", columns="model_id", values="correct")
    return wide.loc[frame.query_id, list(MODEL_IDS)].to_numpy(dtype=np.uint8)


def _aligned_predictions(frame: pd.DataFrame, scored: pd.DataFrame) -> np.ndarray:
    wide = scored.pivot(index="query_id", columns="model_id", values="predicted_letter")
    return wide.loc[frame.query_id, list(MODEL_IDS)].to_numpy(dtype=str)


def _latency_matrix(test: pd.DataFrame, scores: pd.DataFrame, repeats: pd.DataFrame) -> np.ndarray:
    medians = repeats.groupby(["query_id", "model_id"], sort=False).latency_seconds.median().unstack()
    return medians.loc[test.query_id, list(MODEL_IDS)].to_numpy(dtype=float)


def _bootstrap_summary(values: np.ndarray, tasks: np.ndarray) -> dict[str, float]:
    from hls.dynamic_capacity_organization import paired_stratified_bootstrap_delta
    mean, low, high = paired_stratified_bootstrap_delta(
        values, np.zeros_like(values), tasks, n_boot=BOOTSTRAPS, seed=BOOTSTRAP_SEED,
    )
    return {"mean": mean, "ci95_low": low, "ci95_high": high}


def _compare(a: np.ndarray, b: np.ndarray, tasks: np.ndarray) -> dict[str, float]:
    mean, low, high = paired_stratified_bootstrap_delta(
        a, b, tasks, n_boot=BOOTSTRAPS, seed=BOOTSTRAP_SEED,
    )
    return {"difference_a_minus_b": mean, "ci95_low": low, "ci95_high": high}


def _run_record(policy_id: str, frame: pd.DataFrame, correct: np.ndarray,
                total_latency: np.ndarray, selected_ids: list[str],
                details: list[dict[str, object]], config: dict[str, object]) -> tuple[dict, ExperimentRun]:
    scenario = "mmlu_contextual_capacity_selection_v1"
    configuration_id = f"{DATASET_REVISION}-fresh-test160-contextual-dcs"
    objective = "select one model maximizing validation-selected/local estimated probability of correct answer; evaluation uses observed test correctness"
    information = "task and question text observable before selection; model outcomes and answer key excluded from operational selection"
    profile = EvaluationProfile(
        profile_id=f"{policy_id}-contextual-pef", scenario_id=scenario,
        configuration_id=configuration_id, application_domain="MMLU model capacity selection",
        organizational_problem="select one heterogeneous model per query using observable context",
        decision_objective={policy_id: objective}, constraints="exactly one model call per query; no cascade",
        primary_metrics=("functional_success_rate",),
        secondary_metrics=("original_reward_cumulative", "resource_usage:inference_latency_seconds"),
        information_regime=information, temporal_horizon=len(frame),
        aggregation_rules="one MMLU query per period; each policy invokes exactly one model",
        demand_distribution_id=f"mmlu-official-four-subject-test160-seed-{CORRECTED_TEST_SEED}",
        resource_units={"inference_latency_seconds": "seconds"},
    )
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    records, events = [], []
    for i, row in enumerate(frame.itertuples()):
        success = bool(correct[i])
        records.append(EvaluationRecord(
            scenario_id=scenario, configuration_id=configuration_id, policy_id=policy_id,
            period=i, demand=row.task_type, success=success, original_reward=float(success),
            resource_usage={"inference_latency_seconds": float(total_latency[i])},
            provenance=f"cais/mmlu@{DATASET_REVISION}#test:{row.query_id}:{policy_id}",
            unit_id=row.query_id, task_type=row.task_type, quality=float(success),
            information_regime=information, decision_objective=objective,
            available_metadata={"selected_model": selected_ids[i], **details[i]},
        ))
        events.append(ExperimentEvent(
            sequence_index=i, time_index=i, event_type="contextual_capacity_decision",
            mechanism_id=policy_id,
            data={"query_id": row.query_id, "task_type": row.task_type,
                  "selected_model": selected_ids[i], "selection_latency_seconds": details[i].get("selection_latency_seconds", 0.0),
                  "inference_latency_seconds": float(total_latency[i] - float(details[i].get("selection_latency_seconds", 0.0))),
                  **{key: value for key, value in details[i].items() if key != "selection_latency_seconds"}},
        ))
    metrics = evaluator.evaluate(profile.profile_id, policy_id, records)
    metric_values = tuple(MetricValue(name=name, value=float(result.value), unit=result.unit,
                                      interpretation=result.definition_id,
                                      preferred_direction="higher" if name != "resource_usage:inference_latency_seconds" else "lower")
                          for name, result in metrics.items() if result.value is not None)
    run = ExperimentRun(
        schema_version=SCHEMA_VERSION, run_id=policy_id, mechanism_id=policy_id, policy_id=policy_id,
        configuration={"scenario": scenario, "dataset": DATASET_ID, "dataset_revision": DATASET_REVISION,
                       "candidate_model_revisions": MODEL_REVISIONS, "dcs_configuration": config,
                       "n_test": len(frame), "selection_cost_included": True},
        initial_conditions={"test_query_ids_sha256": hashlib.sha256("\n".join(frame.query_id).encode()).hexdigest()},
        random_seeds=(SeedRecord("test_sample", CORRECTED_TEST_SEED, "reuse locked corrected-pilot fresh test sample"),
                      SeedRecord("bootstrap", BOOTSTRAP_SEED, "paired query bootstrap")),
        information_available={"question_text": True, "task_type": True, "training_answers": True,
                               "validation_answers": True, "test_answers_for_selection": False},
        observation_model={"mmlu_model_outputs": "reused corrected-pilot direct-choice scores"},
        software_revision=None, units=(UnitDeclaration("latency", "seconds", "measured inference and online selection"),),
        events=tuple(events), metrics=metric_values,
        mechanism_results={"evaluation_profile": profile.profile_id, "evaluation": {
            key: {"value": val.value, "unit": val.unit, "status": val.status.value, "definition": val.definition_id}
            for key, val in metrics.items()}},
        metadata={"provenance": "corrected pilot outcome and latency artifacts; pinned MMLU revision for query text",
                  "policy_parameters": config},
    )
    return {"profile": profile, "records": records, "metrics": metrics}, run


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    train, validation, test, train_score_frame, test_score_frame, latency_repeats = _scores()
    model_ids = tuple(MODEL_IDS)
    train_y = _aligned_outcomes(train, train_score_frame)
    val_y = _aligned_outcomes(validation, train_score_frame)
    test_y = _aligned_outcomes(test, test_score_frame)
    test_pred_letters = _aligned_predictions(test, test_score_frame)
    latency_by_model = _latency_matrix(test, test_score_frame, latency_repeats)

    # Context text is only used as a feature; answer keys/outcomes remain separate.
    train_questions, val_questions, test_questions = train.question.tolist(), validation.question.tolist(), test.question.tolist()
    train_tasks, val_tasks, test_tasks = train.subject.tolist(), validation.subject.tolist(), test.subject.tolist()
    train_ids = train.query_id.astype(str).tolist()

    configs = [DCSLAConfig(k=k, ngram_range=ngram, task_weight=weight)
               for k in (1, 3, 5, 7, 11, 15, 21)
               for ngram in ((1, 1), (1, 2))
               for weight in (0.0, 0.5, 1.0, 2.0, 4.0)]
    val_trials, validation_selection = [], []
    offline_start = time.perf_counter()
    for config in configs:
        selector = DCSLASelector(config, model_ids).fit(train_questions, train_tasks, train_y, train_ids)
        selected = selector.predict(val_questions, val_tasks)
        indices = np.asarray([model_ids.index(model) for model in selected], dtype=int)
        accuracy = float(val_y[np.arange(len(validation)), indices].mean())
        val_trials.append((config, accuracy))
        validation_selection.append({"config": config.__dict__, "accuracy": accuracy,
                                     "selected_model_counts": {m: int(np.sum(indices == i)) for i, m in enumerate(model_ids)}})
    offline_tuning_seconds = time.perf_counter() - offline_start
    config = choose_dcs_config(val_trials)
    selector = DCSLASelector(config, model_ids).fit(train_questions, train_tasks, train_y, train_ids)

    # Select the strongest global fixed baseline on validation; tie by declared model order.
    val_acc_by_model = {m: float(val_y[:, i].mean()) for i, m in enumerate(model_ids)}
    fixed_model = max(model_ids, key=lambda m: (val_acc_by_model[m], -model_ids.index(m)))
    locked = json.loads((SOURCE / "locked_train_validation_configuration.json").read_text())
    static_task_mapping = locked["static_selector"]["task_to_model"]
    if set(static_task_mapping) != set(TASKS):
        raise AssertionError("frozen static-by-task mapping does not cover the four test tasks")

    # Repeat only deterministic CPU-side selection timing; model results/latency are reused.
    for question, task in zip(train_questions[:5], train_tasks[:5]):
        selector.predict_one(question, task)
    selection_rows = []
    dcs_selected, dcs_details = [], []
    for query_index, (question, task) in enumerate(zip(test_questions, test_tasks)):
        reps = [selector.predict_one(question, task) for _ in range(TEST_TIMING_REPEATS)]
        if len({rep["selected_model"] for rep in reps}) != 1:
            raise AssertionError("DCS-LA selection must be deterministic")
        chosen = str(reps[0]["selected_model"])
        dcs_selected.append(chosen)
        timing_keys = tuple(reps[0]["timing_ns"])
        medians = {key: int(np.median([rep["timing_ns"][key] for rep in reps])) for key in timing_keys}
        detail = {"local_accuracy": reps[0]["local_accuracy"],
                  "neighbor_query_ids": reps[0]["neighbor_query_ids"],
                  "neighbor_similarity": reps[0]["neighbor_similarity"],
                  "timing_ns_median": medians,
                  "selection_latency_seconds": medians["total_selection"] / 1e9}
        dcs_details.append(detail)
        selection_rows.append({"query_id": test.iloc[query_index].query_id, "task_type": task,
                               "selected_model": chosen, **{f"{key}_ns": val for key, val in medians.items()}})

    fixed_selected = [fixed_model] * len(test)
    static_selected = [static_task_mapping[task] for task in test_tasks]
    # The retrospective oracle is fastest correct model, or the fastest model if all fail.
    oracle_selected = []
    for i in range(len(test)):
        correct_models = [j for j in range(len(model_ids)) if test_y[i, j] == 1]
        pool = correct_models or list(range(len(model_ids)))
        oracle_selected.append(model_ids[min(pool, key=lambda j: (latency_by_model[i, j], j))])

    def make_policy(policy_id: str, selected: list[str], decision_seconds: np.ndarray,
                    extra: list[dict[str, object]] | None = None):
        model_index = np.asarray([model_ids.index(model) for model in selected], dtype=int)
        correctness = test_y[np.arange(len(test)), model_index].astype(float)
        infer = latency_by_model[np.arange(len(test)), model_index]
        total = infer + decision_seconds
        details = extra if extra is not None else [{"selection_latency_seconds": float(decision_seconds[i])} for i in range(len(test))]
        summary, run = _run_record(policy_id, test, correctness, total, selected, details,
                                   {"selected_model": selected[0] if len(set(selected)) == 1 else "per_query"})
        return {"policy_id": policy_id, "selected": selected, "correct": correctness,
                "inference_latency": infer, "selection_latency": decision_seconds,
                "total_latency": total, "details": details, "summary": summary, "run": run}

    # Measure lookup overhead for the two deployable static selectors separately.
    fixed_selection_times, task_selection_times = [], []
    for task in test_tasks:
        start = time.perf_counter_ns()
        _ = fixed_model
        fixed_selection_times.append(time.perf_counter_ns() - start)
        start = time.perf_counter_ns()
        _ = static_task_mapping[task]
        task_selection_times.append(time.perf_counter_ns() - start)
    fixed_ns = float(np.median(fixed_selection_times))
    static_ns = float(np.median(task_selection_times))
    policies = [
        make_policy("best_fixed_validation", fixed_selected, np.full(len(test), fixed_ns / 1e9)),
        make_policy("static_by_task_training", static_selected, np.full(len(test), static_ns / 1e9)),
        make_policy("dcs_la_tfidf_knn", dcs_selected,
                    np.asarray([d["selection_latency_seconds"] for d in dcs_details]), dcs_details),
        make_policy("retrospective_fastest_correct_oracle", oracle_selected,
                    np.zeros(len(test))),
    ]

    task_array = np.asarray(test_tasks, dtype=str)
    summaries, comparisons = {}, {}
    fixed_policy, static_policy, dcs_policy, oracle_policy = policies
    for item in policies:
        summaries[item["policy_id"]] = {
            "n": len(test), "accuracy": _bootstrap_summary(item["correct"], task_array),
            "mean_inference_latency_seconds": _bootstrap_summary(item["inference_latency"], task_array),
            "mean_selection_latency_seconds": _bootstrap_summary(item["selection_latency"], task_array),
            "mean_total_latency_seconds": _bootstrap_summary(item["total_latency"], task_array),
            "p50_inference_latency_seconds": float(np.median(item["inference_latency"])),
            "p95_inference_latency_seconds": float(np.quantile(item["inference_latency"], 0.95)),
            "p50_selection_latency_seconds": float(np.median(item["selection_latency"])),
            "p95_selection_latency_seconds": float(np.quantile(item["selection_latency"], 0.95)),
            "p50_total_latency_seconds": float(np.median(item["total_latency"])),
            "p95_total_latency_seconds": float(np.quantile(item["total_latency"], 0.95)),
            "accuracy_by_task": {task: float(item["correct"][task_array == task].mean()) for task in TASKS},
            "selected_model_counts": {model: int(item["selected"].count(model)) for model in model_ids},
            "selected_model_frequency": {model: float(item["selected"].count(model) / len(test)) for model in model_ids},
        }
    for other in (fixed_policy, static_policy):
        key = other["policy_id"]
        comparisons[f"dcs_minus_{key}"] = {
            "accuracy": _compare(dcs_policy["correct"], other["correct"], task_array),
            "mean_total_latency_seconds": _compare(dcs_policy["total_latency"], other["total_latency"], task_array),
        }
    comparisons["dcs_distance_to_oracle"] = {
        "accuracy_oracle_minus_dcs": _compare(oracle_policy["correct"], dcs_policy["correct"], task_array),
        "latency_dcs_minus_oracle_seconds": _compare(dcs_policy["total_latency"], oracle_policy["total_latency"], task_array),
    }

    fixed_index = model_ids.index(fixed_model)
    fixed_correct = test_y[:, fixed_index].astype(bool)
    dcs_correct = dcs_policy["correct"].astype(bool)
    corrected = int(np.sum(~fixed_correct & dcs_correct))
    harmed = int(np.sum(fixed_correct & ~dcs_correct))
    static_same = np.asarray(dcs_selected) == np.asarray(static_selected)
    static_correct = static_policy["correct"].astype(bool)
    dcs_fix_static = int(np.sum(~static_correct & dcs_correct))
    dcs_harm_static = int(np.sum(static_correct & ~dcs_correct))
    dcs_same_as_static_accuracy = float(dcs_correct[static_same].mean()) if static_same.any() else None
    dcs_diff_static_accuracy = float(dcs_correct[~static_same].mean()) if (~static_same).any() else None
    dcs_diagnostics = {
        "fixed_model_selected_from_validation": fixed_model,
        "fixed_model_validation_accuracy": val_acc_by_model[fixed_model],
        "static_task_mapping_frozen_from_training": static_task_mapping,
        "dcs_validation_config": config.__dict__,
        "dcs_validation_accuracy": next(score for candidate, score in val_trials if candidate == config),
        "n_validation_configurations": len(configs),
        "selection_matches_static_by_task": int(static_same.sum()),
        "selection_differs_from_static_by_task": int((~static_same).sum()),
        "dcs_accuracy_when_matches_static": dcs_same_as_static_accuracy,
        "dcs_accuracy_when_differs_from_static": dcs_diff_static_accuracy,
        "errors_corrected_vs_best_fixed": corrected,
        "correct_fixed_responses_lost": harmed,
        "fixed_errors_dcs_corrects_fraction": corrected / max(1, int((~fixed_correct).sum())),
        "errors_corrected_vs_static_by_task": dcs_fix_static,
        "correct_static_responses_lost": dcs_harm_static,
        "dcs_static_changed_decisions_same_outcome": int(np.sum((~static_same) & (dcs_correct == static_correct))),
        "dcs_selections": {model: int(dcs_selected.count(model)) for model in model_ids},
        "dcs_selections_by_task": {
            task: {model: int(sum(1 for i, value in enumerate(dcs_selected)
                                  if test_tasks[i] == task and value == model)) for model in model_ids}
            for task in TASKS
        },
        "validation_config_scores": validation_selection,
        "offline_fit_and_validation_tuning_seconds": offline_tuning_seconds,
        "online_timing_repetitions_per_test_query": TEST_TIMING_REPEATS,
        "selection_cost_components_seconds_median_of_query_medians": {
            key: float(np.median([row[f"{key}_ns"] for row in selection_rows]) / 1e9)
            for key in ("context_extraction", "tfidf_transform", "feature_combination_and_normalization",
                        "neighbor_search", "local_competence_and_selection", "total_selection")
        },
    }

    # Complementarity diagnostics: query-level model correctness overlap.
    overlap = {}
    for i, left in enumerate(model_ids):
        for right in model_ids[i + 1:]:
            li, ri = model_ids.index(left), model_ids.index(right)
            overlap[f"{left}__{right}"] = {
                "both_correct": int(np.sum((test_y[:, li] == 1) & (test_y[:, ri] == 1))),
                "left_only": int(np.sum((test_y[:, li] == 1) & (test_y[:, ri] == 0))),
                "right_only": int(np.sum((test_y[:, li] == 0) & (test_y[:, ri] == 1))),
                "both_wrong": int(np.sum((test_y[:, li] == 0) & (test_y[:, ri] == 0))),
            }

    run_payload = [policy["run"].to_dict() for policy in policies]
    for payload in run_payload:
        ExperimentRun.from_json(json.dumps(payload, sort_keys=True))
    result = {
        "status": "completed",
        "experiment": {"name": "HLS contextual capacity selection using DCS-LA adaptation",
                       "question": "Do observable query text and subject permit local-accuracy selection to outperform the best global static model?",
                       "method": "DCS-LA local classifier accuracy over k-nearest training queries; one selected model per query",
                       "adaptation": "Woods et al. local-accuracy selection, with sparse TF-IDF cosine neighborhoods and task one-hot feature; k and representation tuned on validation",
                       "no_test_answers_used_for_selection": True,
                       "no_new_model_inference": True},
        "dataset": {"id": DATASET_ID, "revision": DATASET_REVISION,
                    "train_n": len(train), "validation_n": len(validation), "test_n": len(test),
                    "train_examples_with_observed_subject": int(train.subject.astype(str).str.len().gt(0).sum()),
                    "train_examples_without_recorded_subject": int(train.subject.astype(str).str.len().eq(0).sum()),
                    "test_seed": CORRECTED_TEST_SEED, "test_excludes_prior_pilot_by_question_and_choices": True,
                    "test_task_counts": {task: int(np.sum(task_array == task)) for task in TASKS}},
        "model_ids": model_ids, "model_revisions": MODEL_REVISIONS,
        "configuration": {"dcs": config.__dict__, "fixed_model": fixed_model,
                          "static_by_task": static_task_mapping,
                          "feature_protocol": "question enunciado TF-IDF; observed task one-hot; fit vocabulary and IDF on train only",
                          "neighbor_protocol": "cosine similarity; exact brute-force ranking; ties by query ID",
                          "local_competence": "unweighted fraction of k neighbors correctly classified for each model",
                          "model_tie_break": "MODEL_IDS declaration order",
                          "parameter_grid": {"k": [1, 3, 5, 7, 11, 15, 21], "ngram_range": [[1, 1], [1, 2]], "task_weight": [0.0, 0.5, 1.0, 2.0, 4.0]},
                          "parameter_selection": "maximum validation accuracy; ties prefer larger k, unigram representation, then lower task weight"},
        "results": summaries, "paired_comparisons": comparisons,
        "dcs_diagnostics": dcs_diagnostics,
        "complementarity": overlap,
        "artifacts": {"test_query_ids_sha256": hashlib.sha256("\n".join(test.query_id).encode()).hexdigest(),
                      "train_query_ids_sha256": hashlib.sha256("\n".join(train.query_id).encode()).hexdigest(),
                      "validation_query_ids_sha256": hashlib.sha256("\n".join(validation.query_id).encode()).hexdigest(),
                      "test_model_scores_sha256": _sha256(SOURCE / "test_model_scores.csv.gz"),
                      "test_latency_repetitions_sha256": _sha256(SOURCE / "test_latency_repetitions.csv"),
                      "train_validation_scores_sha256": _sha256(SOURCE / "train_validation_scores.csv.gz")},
        "limitations": ["only four MMLU subjects and 160 test queries", "the auxiliary training subset lacks recorded subject metadata; it is represented as missing, not inferred", "offline logged model outcomes do not capture serving concurrency or queueing", "test oracle uses correctness labels and is not deployable"],
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (OUT / "experiment_runs.json").write_text(json.dumps(run_payload, indent=2, sort_keys=True) + "\n")
    pd.DataFrame(selection_rows).to_csv(OUT / "dcs_test_decisions.csv", index=False)
    pd.DataFrame(validation_selection).to_json(OUT / "validation_grid.json", orient="records", indent=2)
    pd.DataFrame({"query_id": test.query_id, "task_type": test_tasks,
                  **{f"correct_{m}": test_y[:, i] for i, m in enumerate(model_ids)},
                  "best_fixed_model": fixed_model, "static_by_task_model": static_selected,
                  "dcs_model": dcs_selected, "oracle_model": oracle_selected,
                  "dcs_correct": dcs_policy["correct"], "best_fixed_correct": fixed_policy["correct"],
                  "static_correct": static_policy["correct"], "oracle_correct": oracle_policy["correct"],
                  "dcs_inference_latency_seconds": dcs_policy["inference_latency"],
                  "dcs_selection_latency_seconds": dcs_policy["selection_latency"],
                  "dcs_total_latency_seconds": dcs_policy["total_latency"]}).to_csv(OUT / "test_policy_results.csv", index=False)
    curve_rows = []
    for policy in policies:
        stat = summaries[policy["policy_id"]]
        curve_rows.append({"policy_id": policy["policy_id"], "operational": policy["policy_id"] != "retrospective_fastest_correct_oracle",
                           "accuracy": stat["accuracy"]["mean"], "accuracy_ci95_low": stat["accuracy"]["ci95_low"],
                           "accuracy_ci95_high": stat["accuracy"]["ci95_high"],
                           "mean_total_latency_seconds": stat["mean_total_latency_seconds"]["mean"],
                           "latency_ci95_low": stat["mean_total_latency_seconds"]["ci95_low"],
                           "latency_ci95_high": stat["mean_total_latency_seconds"]["ci95_high"]})
    curve = pd.DataFrame(curve_rows)
    curve.to_csv(OUT / "quality_cost_frontier.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for row in curve.itertuples():
        ax.errorbar(row.mean_total_latency_seconds * 1000, row.accuracy * 100,
                    xerr=[[max(0, (row.mean_total_latency_seconds - row.latency_ci95_low) * 1000)],
                          [max(0, (row.latency_ci95_high - row.mean_total_latency_seconds) * 1000)]],
                    yerr=[[max(0, (row.accuracy - row.accuracy_ci95_low) * 100)],
                          [max(0, (row.accuracy_ci95_high - row.accuracy) * 100)]],
                    marker="x" if not row.operational else "o", capsize=3,
                    label=row.policy_id + (" (oracle; no operable selection cost)" if not row.operational else ""))
    ax.set_xlabel("Latencia total medida por consulta (ms)")
    ax.set_ylabel("Exactitud (%)")
    ax.set_title("Selección contextual: calidad frente a latencia")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "quality_cost_frontier.png", dpi=160)
    plt.close(fig)
    # Preserve the fitted feature map needed to reconstruct the local selector.
    fitted_state = {"config": config.__dict__, "task_to_index": selector.task_to_index,
                    "vocabulary": selector.vectorizer.vocabulary_,
                    "idf": selector.vectorizer.idf_.tolist(), "model_ids": model_ids,
                    "train_query_ids": selector.train_ids}
    (OUT / "dcs_fitted_state.json").write_text(json.dumps(fitted_state, sort_keys=True) + "\n")
    (OUT / "artifact_hashes.json").write_text(json.dumps({
        path.name: _sha256(path) for path in OUT.iterdir() if path.is_file() and path.name != "artifact_hashes.json"
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(OUT), "fixed_model": fixed_model,
                      "dcs_config": config.__dict__, "results": summaries,
                      "dcs_diagnostics": {k: v for k, v in dcs_diagnostics.items() if k != "validation_config_scores"}}, indent=2))


if __name__ == "__main__":
    main()
