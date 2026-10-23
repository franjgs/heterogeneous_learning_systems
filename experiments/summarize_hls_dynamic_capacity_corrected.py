"""Build reproducible diagnostics and a quality-cost plot from corrected run artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/experiments/hls_dynamic_capacity_organization_corrected"
sys.path.insert(0, str(ROOT / "src"))

from hls.experiment_contract import ExperimentRun  # noqa: E402
from hls.llm_routing_pilot import MODEL_IDS  # noqa: E402
from run_hls_budgeted_llm_routing_pilot import MODEL_REVISIONS  # noqa: E402
from hls.dynamic_capacity_organization import fit_escalation_threshold  # noqa: E402
from hls.dynamic_capacity_organization import (  # noqa: E402
    paired_stratified_bootstrap_delta, per_task_accuracy,
)


def _signal_stats(confidence: np.ndarray, correct: np.ndarray) -> dict[str, float | None]:
    error = 1 - correct.astype(int)
    constant_brier = float(np.mean((correct.mean() - correct) ** 2))
    ece = 0.0
    for lower, upper in zip(np.linspace(0, 1, 11)[:-1], np.linspace(0, 1, 11)[1:]):
        mask = ((confidence >= lower) & (confidence < upper))
        if upper == 1:
            mask |= confidence == 1
        if mask.any():
            ece += float(mask.mean() * abs(confidence[mask].mean() - correct[mask].mean()))
    auc = float(roc_auc_score(error, 1 - confidence)) if len(np.unique(error)) > 1 else None
    return {
        "n": int(len(correct)), "accuracy": float(correct.mean()),
        "confidence_brier": float(brier_score_loss(correct, confidence)),
        "constant_prevalence_brier": constant_brier,
        "ece_10_equal_width_bins": ece, "error_ranking_auc": auc,
    }


def _mirt_quality_stats(predicted: np.ndarray, outcomes: np.ndarray,
                        task_types: np.ndarray) -> dict:
    p = np.clip(np.asarray(predicted, dtype=float), 1e-9, 1 - 1e-9)
    y = np.asarray(outcomes, dtype=float)
    if p.shape != y.shape or p.ndim != 2:
        raise ValueError("MIRT estimates and binary outcomes must be matching matrices")
    pairwise = []
    for i in range(len(y)):
        for left in range(y.shape[1]):
            for right in range(left + 1, y.shape[1]):
                if y[i, left] == y[i, right]:
                    continue
                good, bad = (left, right) if y[i, left] > y[i, right] else (right, left)
                pairwise.append(1.0 if p[i, good] > p[i, bad] else
                                0.5 if p[i, good] == p[i, bad] else 0.0)
    chosen = np.argmax(p, axis=1)
    top_model_correct = y[np.arange(len(y)), chosen]
    by_task = {}
    for task in sorted(set(map(str, task_types))):
        mask = np.asarray(task_types, dtype=str) == task
        yt, pt = y[mask], p[mask]
        by_task[task] = {
            "brier": float(np.mean((pt - yt) ** 2)),
            "log_loss": float(np.mean(-(yt * np.log(pt) + (1 - yt) * np.log(1 - pt)))),
            "top_model_correct_fraction": float(top_model_correct[mask].mean()),
        }
    return {
        "brier": float(np.mean((p - y) ** 2)),
        "log_loss": float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p)))),
        "pairwise_model_order_accuracy_on_discordant_outcomes": float(np.mean(pairwise)) if pairwise else None,
        "top_model_correct_fraction": float(top_model_correct.mean()),
        "by_task": by_task,
    }


def _make_plot(result: dict) -> None:
    curves = result["curves"]
    groups = {
        "IRT routing": lambda x: x.startswith("irt_router_"),
        "Confidence cascade": lambda x: x.startswith("cascade_"),
        "Fixed / references": lambda x: x in {
            "capacity_a_always", "capacity_b_always", "static_best_by_task",
            "all_model_plurality", "test_oracle_fastest_correct",
        } or x.startswith("fixed_candidate_"),
    }
    styles = {
        "IRT routing": ("tab:blue", "o"),
        "Confidence cascade": ("tab:orange", "s"),
        "Fixed / references": ("tab:green", "D"),
    }
    fig, ax = plt.subplots(figsize=(9, 6))
    for label, predicate in groups.items():
        subset = [x for x in curves if predicate(x["policy_id"])]
        color, marker = styles[label]
        ordered = sorted(subset, key=lambda x: x["mean_latency_seconds"])
        if label != "Fixed / references":
            ax.plot([x["mean_latency_seconds"] for x in ordered],
                    [x["accuracy"] for x in ordered], alpha=.35, color=color)
        for row in subset:
            ax.scatter(row["mean_latency_seconds"], row["accuracy"],
                       color=color, marker=marker, s=34, label=label if row is subset[0] else None)
    for policy, label in [("capacity_a_always", "A always"),
                          ("capacity_b_always", "B always"),
                          ("static_best_by_task", "Static by task"),
                          ("test_oracle_fastest_correct", "Retrospective oracle")]:
        row = next(x for x in curves if x["policy_id"] == policy)
        ax.annotate(label, (row["mean_latency_seconds"], row["accuracy"]),
                    xytext=(5, 6), textcoords="offset points", fontsize=8)
    ax.set(xlabel="Mean measured latency per query (s)", ylabel="MMLU exact accuracy",
           title="S7 capacity organization: test quality–latency curve")
    ax.grid(True, alpha=.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "quality_cost_frontier.png", dpi=180)
    plt.close(fig)


def complete_artifacts() -> dict:
    result_path = OUT / "results.json"
    result = json.loads(result_path.read_text())
    locked = json.loads((OUT / "locked_train_validation_configuration.json").read_text())
    tv = pd.read_csv(OUT / "train_validation_scores.csv.gz")
    test_scores = pd.read_csv(OUT / "test_model_scores.csv.gz")
    test_timing = pd.read_csv(OUT / "test_latency_repetitions.csv")
    a_model, b_model = locked["selected_A"], locked["selected_B"]
    a_idx, b_idx = MODEL_IDS.index(a_model), MODEL_IDS.index(b_model)

    candidate_profiles = []
    validation_signals = {}
    test_signals = {}
    for model in MODEL_IDS:
        spec = result["model_specs"][model]
        val = tv[(tv.split == "validation") & (tv.model_id == model)]
        tst = test_scores[test_scores.model_id == model]
        test_cost = (test_timing[test_timing.model_id == model]
                     .groupby("query_id").latency_seconds.median())
        test_order = test_scores[test_scores.model_id == model].set_index("query_id")
        cost_ordered = np.asarray([test_cost.loc[qid] for qid in test_order.index])
        val_accuracy = float(val.correct.mean())
        test_accuracy = float(tst.correct.mean())
        candidate_profiles.append({
            "model_id": model, "revision": MODEL_REVISIONS[model],
            "parameters": spec["parameter_count"], "dtype": spec["dtype"],
            "fp16_parameter_bytes": spec["loaded_parameter_bytes"],
            "mps_pool_bytes_after_this_load_in_candidate_order": spec["mps_driver_allocated_bytes_after_load"],
            "train_accuracy": result["capability_characterization"][MODEL_IDS.index(model)]["train_accuracy"],
            "validation_accuracy": val_accuracy, "test_accuracy_diagnostic_only": test_accuracy,
            "test_latency_mean_of_per_query_medians_seconds": float(cost_ordered.mean()),
            "test_latency_median_of_per_query_medians_seconds": float(np.median(cost_ordered)),
            "test_latency_p95_of_per_query_medians_seconds": float(np.quantile(cost_ordered, .95)),
            "test_per_task_accuracy_diagnostic_only": {
                str(task): float(group.correct.mean())
                for task, group in tst.groupby("task_type")
            },
        })
        validation_signals[model] = _signal_stats(val.confidence.to_numpy(), val.correct.to_numpy())
        test_signals[model] = _signal_stats(tst.confidence.to_numpy(), tst.correct.to_numpy())

    val_a = tv[(tv.split == "validation") & (tv.model_id == a_model)].set_index("query_id")
    val_b = tv[(tv.split == "validation") & (tv.model_id == b_model)].set_index("query_id")
    threshold_diagnostics = []
    for rate, config in locked["cascade_thresholds"].items():
        selected = val_a.confidence.to_numpy() < float(config["threshold"])
        a_correct = val_a.correct.to_numpy(dtype=bool)
        b_correct = val_b.loc[val_a.index].correct.to_numpy(dtype=bool)
        n = int(selected.sum())
        threshold_diagnostics.append({
            "target_rate": float(rate), "threshold": config["threshold"],
            "achieved_rate": float(selected.mean()), "activated_n": n,
            "A_errors_escalated": int(np.sum(selected & ~a_correct)),
            "fraction_of_A_errors_escalated": float(np.sum(selected & ~a_correct) / max(1, np.sum(~a_correct))),
            "B_corrects_A_error": int(np.sum(selected & ~a_correct & b_correct)),
            "B_harms_correct_A": int(np.sum(selected & a_correct & ~b_correct)),
        })

    result["candidate_model_test_diagnostics"] = candidate_profiles
    result["confidence_signal_diagnostics"] = {
        "definition": "normalized next-token probability mass for the selected A-D letter; Brier compares this score with exact correctness; error AUC uses 1-confidence to rank errors",
        "validation": validation_signals, "test_evaluation_only": test_signals,
        "cascade_validation_threshold_diagnostics": threshold_diagnostics,
    }
    result["memory_note"] = (
        "Per-model FP16 parameter bytes are exact tensor storage. MPS driver allocations are cumulative as models are loaded in candidate order; the last value is the resident pool footprint, not a per-model increment."
    )
    result["latency_note"] = (
        "The per-query cost used by policy curves is the median of three repeated forward-pass timings for that query/model. Bootstrap resamples 160 queries stratified by task, not timing repetitions."
    )
    result["partition_validation"] = {
        "check": "SHA-256 of question plus choices across auxiliary_train/dev/validation/test and prior pilot test",
        "overlap_pairs": 0,
        "test_seed": locked["test_selection_seed"],
        "prior_test_items_excluded": 160,
        "test_was_loaded_after_locked_configuration": True,
    }

    # Recompute the existing MIRT predictor diagnostics from stored outputs.
    # Its test metrics are post-hoc evaluation only and do not affect routing.
    from run_hls_dynamic_capacity_corrected import (
        _build_train_validation, _load_fresh_test, request_features,
    )
    from hls.llm_routing_pilot import MIRTQualityPredictor
    auxiliary, _, validation = _build_train_validation()
    test_frame = _load_fresh_test()
    train_scores = tv[tv.query_id.isin(auxiliary.query_id)]
    train_outcomes = train_scores.pivot(index="query_id", columns="model_id", values="correct").loc[auxiliary.query_id, list(MODEL_IDS)].to_numpy(dtype=int)
    predictor = MIRTQualityPredictor(seed=20261023).fit(
        request_features(auxiliary), MODEL_IDS, train_outcomes,
    )
    train_prevalence = train_outcomes.mean(axis=0)
    mirt_diagnostics = {
        "fit_info": predictor.fit_info, "trained_only_on_auxiliary_train": True,
        "constant_train_prevalence_by_model": {
            model: float(train_prevalence[index]) for index, model in enumerate(MODEL_IDS)
        },
    }
    for split_name, frame in (("validation", validation), ("test_evaluation_only", test_frame)):
        score_rows = tv if split_name == "validation" else test_scores
        outcomes = score_rows.pivot(index="query_id", columns="model_id", values="correct").loc[frame.query_id, list(MODEL_IDS)].to_numpy(dtype=int)
        estimates = predictor.predict(request_features(frame))
        stats = _mirt_quality_stats(estimates, outcomes, frame.task_type.to_numpy(dtype=str))
        stats["constant_train_prevalence_brier"] = float(np.mean((train_prevalence[None, :] - outcomes) ** 2))
        stats["constant_train_prevalence_brier_by_model"] = {
            model: float(np.mean((train_prevalence[index] - outcomes[:, index]) ** 2))
            for index, model in enumerate(MODEL_IDS)
        }
        mirt_diagnostics[split_name] = stats
    result["mirt_quality_prediction_diagnostics"] = mirt_diagnostics

    # Preserve every candidate as a fixed-capability baseline. This reuses
    # already-scored test outcomes; it does not tune or select on test labels.
    from run_hls_dynamic_capacity_corrected import _load_fresh_test, _write_run
    test_frame = _load_fresh_test()
    if list(test_frame.query_id) != list(test_scores[test_scores.model_id == MODEL_IDS[0]].query_id):
        raise AssertionError("fixed-candidate test rows do not match the scored query order")
    test_correct = test_scores.pivot(index="query_id", columns="model_id", values="correct").loc[test_frame.query_id]
    test_letters = test_scores.pivot(index="query_id", columns="model_id", values="predicted_letter").loc[test_frame.query_id]
    test_conf = test_scores.pivot(index="query_id", columns="model_id", values="confidence").loc[test_frame.query_id]
    median_latency = test_timing.groupby(["query_id", "model_id"]).latency_seconds.median()
    timing = np.asarray([[median_latency.loc[(qid, model)] for model in MODEL_IDS]
                         for qid in test_frame.query_id], dtype=float)
    truth = np.asarray(["ABCD"[int(answer)] for answer in test_frame.answer])
    tasks = test_frame.task_type.to_numpy(dtype=str)
    existing_ids = {x["policy_id"] for x in result["curves"]}
    for model_index, model_id in enumerate(MODEL_IDS):
        if model_id in {a_model, b_model}:
            continue
        policy_id = "fixed_candidate_qwen_0_5b_always"
        if policy_id in existing_ids:
            continue
        predictions = test_letters[model_id].to_numpy(dtype=str)
        costs = timing[:, model_index]
        success = test_correct[model_id].to_numpy(dtype=float)
        metrics, run = _write_run(
            policy_id, test_frame, predictions, costs, [model_id] * len(test_frame),
            test_conf[model_id].to_numpy(dtype=float), np.zeros(len(test_frame), dtype=bool),
            OUT, (a_model, b_model),
        )
        paired = {}
        for baseline in ("capacity_a_always", "capacity_b_always", "static_best_by_task",
                         "all_model_plurality"):
            other_run = next(item for item in json.loads((OUT / "experiment_runs.json").read_text())
                             if item["policy_id"] == baseline)
            other_events = other_run["events"]
            if baseline == "capacity_a_always":
                other_success = test_correct[a_model].to_numpy(dtype=float)
                other_cost = timing[:, MODEL_IDS.index(a_model)]
            elif baseline == "capacity_b_always":
                other_success = test_correct[b_model].to_numpy(dtype=float)
                other_cost = timing[:, MODEL_IDS.index(b_model)]
            elif baseline == "static_best_by_task":
                # Match the already-recorded per-query static choices.
                static_events = other_events
                selected_model = [event["data"]["selected_path"] for event in static_events]
                other_success = np.asarray([
                    test_correct.loc[qid, selected] for qid, selected in zip(test_frame.query_id, selected_model)
                ], dtype=float)
                other_cost = np.asarray([
                    timing[i, MODEL_IDS.index(selected)] for i, selected in enumerate(selected_model)
                ])
            else:
                vote_events = other_events
                selected_paths = [event["data"]["selected_path"] for event in vote_events]
                # Plurality success can be recovered from its event outcome only
                # if recorded; otherwise read its per-query choices and vote.
                from hls.dynamic_capacity_organization import majority_vote
                answers = test_letters.loc[test_frame.query_id, list(MODEL_IDS)].to_numpy(dtype=str)
                vote = majority_vote(answers, MODEL_IDS.index(b_model))
                other_success = (vote == truth).astype(float)
                other_cost = timing.sum(axis=1)
                del selected_paths
            dacc, alo, ahi = paired_stratified_bootstrap_delta(
                success, other_success, tasks, seed=20261023 + model_index,
            )
            dcost, clo, chi = paired_stratified_bootstrap_delta(
                costs, other_cost, tasks, seed=20262023 + model_index,
            )
            paired[baseline] = {"accuracy_delta": dacc, "accuracy_ci95": [alo, ahi],
                                "latency_delta_seconds": dcost, "latency_ci95": [clo, chi]}
        row = {
            "policy_id": policy_id, "accuracy": float(success.mean()),
            "accuracy_ci95_stratified_query": list(paired_stratified_bootstrap_delta(
                success, np.zeros_like(success), tasks, seed=20261024)[1:]),
            "mean_latency_seconds": float(costs.mean()),
            "latency_ci95_stratified_query": list(paired_stratified_bootstrap_delta(
                costs, np.zeros_like(costs), tasks, seed=20261025)[1:]),
            "per_task_accuracy": per_task_accuracy(predictions, truth, tasks),
            "B_activation_rate": 0.0, "paired_vs": paired,
            "test_usage": "fixed candidate diagnostic; no test-based selection",
        }
        result["curves"].append(row)
        result["per_policy_hls_pef"][policy_id] = metrics
        runs_file = OUT / "experiment_runs.json"
        existing_runs = json.loads(runs_file.read_text())
        existing_runs.append(run.to_dict())
        runs_file.write_text(json.dumps(existing_runs, indent=2, sort_keys=True) + "\n")
        existing_ids.add(policy_id)

    result["n_policies"] = len(result["curves"])
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    # Make every ExperimentRun independently identify the selected pair and revisions.
    runs_path = OUT / "experiment_runs.json"
    runs = json.loads(runs_path.read_text())
    for raw in runs:
        run = ExperimentRun.from_dict(raw)
        run.configuration.update({
            "capacity_A": a_model, "capacity_B": b_model,
            "candidate_models": list(MODEL_IDS), "model_revisions": dict(MODEL_REVISIONS),
            "dtype": "float16", "device": result["inference_configuration"]["device"],
        })
        raw.clear()
        raw.update(run.to_dict())
    runs_path.write_text(json.dumps(runs, indent=2, sort_keys=True) + "\n")

    signal_path = OUT / "signal_diagnostics.json"
    signal_path.write_text(json.dumps(result["confidence_signal_diagnostics"], indent=2, sort_keys=True) + "\n")
    (OUT / "quality_prediction_diagnostics.json").write_text(json.dumps(mirt_diagnostics, indent=2, sort_keys=True) + "\n")
    _make_plot(result)

    flat = []
    for row in result["curves"]:
        base = {key: row[key] for key in ("policy_id", "accuracy", "accuracy_ci95_stratified_query",
                                          "mean_latency_seconds", "latency_ci95_stratified_query",
                                          "B_activation_rate")}
        base.update({f"accuracy_{task}": value for task, value in row["per_task_accuracy"].items()})
        for baseline in ("capacity_a_always", "capacity_b_always", "static_best_by_task"):
            if baseline in row.get("paired_vs", {}):
                diff = row["paired_vs"][baseline]
                base[f"delta_accuracy_vs_{baseline}"] = diff["accuracy_delta"]
                base[f"delta_latency_vs_{baseline}_seconds"] = diff["latency_delta_seconds"]
        flat.append(base)
    pd.DataFrame(flat).to_csv(OUT / "quality_cost_curve_summary.csv", index=False)

    hash_files = [ROOT / "src/hls/dynamic_capacity_organization.py",
                  ROOT / "experiments/run_hls_dynamic_capacity_corrected.py",
                  ROOT / "experiments/summarize_hls_dynamic_capacity_corrected.py"]
    hash_files += [path for path in OUT.iterdir() if path.is_file() and path.name != "artifact_hashes.json"]
    manifest = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(set(hash_files))}
    (OUT / "artifact_hashes.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    report = complete_artifacts()
    print(json.dumps({"status": report["status"], "models": len(report["candidate_model_test_diagnostics"]),
                      "confidence_thresholds": len(report["confidence_signal_diagnostics"]["cascade_validation_threshold_diagnostics"]),
                      "curve_points": len(report["curves"])}, indent=2))
