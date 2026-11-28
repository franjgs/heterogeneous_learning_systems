#!/usr/bin/env python3
"""Reproduce the SOCTRA pre-encoding preprocessing pipeline in HLS."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
CONFIG_PATH = REPO_ROOT / "config/soctra_preprocessing.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data/soctra/processed"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def distribution(values: pd.Series) -> dict[str, int]:
    return {str(json_value(k)): int(v) for k, v in values.value_counts(dropna=False).items()}


def label_stats(values: pd.Series) -> dict[str, Any]:
    positives = int((values == True).sum())  # noqa: E712 - mirrors boolean label semantics
    negatives = int((values == False).sum())  # noqa: E712
    n = len(values)
    return {
        "count": n,
        "distribution": distribution(values),
        "positive": positives,
        "negative": negatives,
        "missing_or_nonbinary": n - positives - negatives,
        "prevalence": positives / n if n else None,
        "imbalance_ratio_negative_over_positive": negatives / positives if positives else None,
    }


def transition(before: pd.Series, after: pd.Series) -> dict[str, int]:
    common_ids = before.index.intersection(after.index)
    paired = pd.DataFrame(
        {"before": before.loc[common_ids], "after": after.loc[common_ids]}
    ).dropna()
    return {
        "false_to_true": int(((paired.before == False) & (paired.after == True)).sum()),  # noqa: E712
        "true_to_false": int(((paired.before == True) & (paired.after == False)).sum()),  # noqa: E712
        "unchanged": int((paired.before == paired.after).sum()),
        "rows_not_in_both_stages": int(len(before.index.union(after.index)) - len(common_ids)),
        "missing_values_within_matched_ids": int(len(common_ids) - len(paired)),
        "matrix_before_false_after_false": int(((paired.before == False) & (paired.after == False)).sum()),  # noqa: E712
        "matrix_before_false_after_true": int(((paired.before == False) & (paired.after == True)).sum()),  # noqa: E712
        "matrix_before_true_after_false": int(((paired.before == True) & (paired.after == False)).sum()),  # noqa: E712
        "matrix_before_true_after_true": int(((paired.before == True) & (paired.after == True)).sum()),  # noqa: E712
    }


def load_original_module(path: Path | None):
    if path is None:
        from hls.soctra import original_pipeline

        return original_pipeline
    spec = importlib.util.spec_from_file_location("soctra_original_source", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load original SOCTRA module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def feature_columns(config: dict[str, Any]) -> tuple[list[str], list[str]]:
    cfg = config["preprocessing"]
    features = list(cfg["uniform_columns"])
    lower = list(cfg["lower_columns"])
    return features, lower


def run_label_pipeline(path: Path, label: str, config: dict[str, Any], module):
    data_cfg = config["data"]
    prep_cfg = config["preprocessing"]
    loaded = module.func_load_data(
        data_path=str(path),
        weight_path=data_cfg["weight_column"],
        alarms_get_labels_colname=[label],
        feats2drop=[],  # HLS retains raw fields that the old loader discarded.
    )
    loaded = loaded.copy()
    loaded["__source_row"] = np.arange(len(loaded), dtype=np.int64)
    preprocessed = module.func_preprocessing(
        df_alarms=loaded,
        drop_titulo=prep_cfg["drop_title_contains"],
        projects2drop=prep_cfg["drop_projects"],
        get_top=None,
        project_start_date=None,
        feats2lower=prep_cfg["lower_columns"],
    )
    preprocessed = preprocessed.sort_values(
        by=data_cfg["timestamp_column"], kind="mergesort"
    ).reset_index(drop=True)
    uniform = module.func_uniform(
        df=preprocessed.copy(),
        columns_uni=prep_cfg["uniform_columns"],
        mode=prep_cfg["uniform"]["mode"],
        weight_positive=prep_cfg["uniform"]["weight_positive"],
    )
    # The source training pipeline sorts after preprocess() returns, while
    # uniformization itself sees the source CSV order.
    uniform = uniform.sort_values(
        by=data_cfg["timestamp_column"], kind="mergesort"
    ).reset_index(drop=True)
    return loaded, preprocessed, uniform


def split_masks(frame: pd.DataFrame, config: dict[str, Any]) -> dict[str, pd.Series]:
    split = config["temporal_split"]
    time_col = config["data"]["timestamp_column"]
    latest = frame[time_col].max()
    test_start = latest - pd.DateOffset(months=split["months_test"])
    train_start = test_start - pd.DateOffset(months=split["months_train"])
    train_end = test_start - pd.Timedelta(seconds=1)
    test_end = latest.normalize() + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    return {
        "train": (frame[time_col] >= train_start) & (frame[time_col] <= train_end),
        "test": (frame[time_col] >= test_start) & (frame[time_col] <= test_end),
    }


def prevalences_by(frame: pd.DataFrame, label_col: str, group_col: str) -> dict[str, Any]:
    rows = {}
    for key, group in frame.groupby(group_col, dropna=False, sort=True):
        rows[str(json_value(key))] = label_stats(group[label_col])
    return rows


def run_diagnostic_preprocessing(path: Path, raw_ids: pd.Series, config: dict, module):
    """Run the original cleanup with title/project filters disabled to count drops."""
    prep_cfg = config["preprocessing"]
    loaded = module.func_load_data(
        data_path=str(path),
        weight_path=config["data"]["weight_column"],
        alarms_get_labels_colname=["escalada"],
        feats2drop=[],
    )
    loaded["__source_row"] = np.arange(len(loaded), dtype=np.int64)
    without_title_project = module.func_preprocessing(
        df_alarms=loaded,
        drop_titulo=[],
        projects2drop=[],
        get_top=None,
        project_start_date=None,
        feats2lower=prep_cfg["lower_columns"],
    )
    kept_without_title_project = set(without_title_project["id_alerta"].tolist())
    all_ids = set(raw_ids.tolist())
    mailbox_ids = all_ids - kept_without_title_project
    candidates = without_title_project[~without_title_project["id_alerta"].isin(mailbox_ids)]

    title_drop_mask = pd.Series(False, index=candidates.index)
    for term in prep_cfg["drop_title_contains"]:
        title_drop_mask |= candidates["titulo_investigacion"].str.contains(term, na=False)
    title_ids = set(candidates.loc[title_drop_mask, "id_alerta"].tolist())
    after_titles = candidates[~candidates["id_alerta"].isin(title_ids)]
    project_ids = set(
        after_titles.loc[after_titles["proyecto"].isin(prep_cfg["drop_projects"]), "id_alerta"]
    )
    expected = all_ids - mailbox_ids - title_ids - project_ids
    return {
        "mailbox_title": len(mailbox_ids),
        "configured_title_terms": len(title_ids),
        "configured_projects": len(project_ids),
        "total_excluded": len(all_ids - expected),
    }


def process_dataset(path: Path, output_path: Path, config: dict, compare_module=None):
    raw = pd.read_csv(path, low_memory=False)
    if "id_alerta" not in raw or raw["id_alerta"].isna().any():
        raise ValueError(f"Missing/null id_alerta in {path}")
    if raw["id_alerta"].duplicated().any():
        raise ValueError(f"id_alerta is not unique in {path}; cannot one-to-one join label runs")
    timestamp_col = config["data"]["timestamp_column"]
    raw_timestamps = pd.to_datetime(raw[timestamp_col], format=config["data"]["timestamp_format"], errors="raise")
    if raw_timestamps.isna().any():
        raise ValueError(f"Null timestamps in {path}")
    if list(raw.columns) != list(pd.read_csv(path, nrows=0).columns):
        raise AssertionError("CSV header is not stable")

    module = load_original_module(None)
    runs: dict[str, tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]] = {}
    equivalence = {}
    for label in config["data"]["labels"]:
        local_run = run_label_pipeline(path, label, config, module)
        runs[label] = local_run
        if compare_module is not None:
            ref_run = run_label_pipeline(path, label, config, compare_module)
            stage_names = ["loaded", "preprocessed", "uniform"]
            stage_equal = {}
            for stage, ours, reference in zip(stage_names, local_run, ref_run):
                try:
                    pd.testing.assert_frame_equal(ours, reference, check_dtype=True, check_exact=True)
                    stage_equal[stage] = True
                except AssertionError as exc:
                    raise AssertionError(f"Original SoC_WP4 mismatch: {path.name} / {label} / {stage}: {exc}") from exc
            equivalence[label] = stage_equal

    esc_loaded, esc_pre, esc_uniform = runs["escalada"]
    rep_loaded, rep_pre, rep_uniform = runs["reportado"]
    if not esc_pre["id_alerta"].reset_index(drop=True).equals(rep_pre["id_alerta"].reset_index(drop=True)):
        raise AssertionError("Escalada and reportado row populations/order differ after preprocessing")
    if not esc_uniform["id_alerta"].reset_index(drop=True).equals(rep_uniform["id_alerta"].reset_index(drop=True)):
        raise AssertionError("Escalada and reportado row populations/order differ after uniformization")

    masks = split_masks(esc_uniform, config)
    source_ordered = raw.copy()
    source_ordered[timestamp_col] = raw_timestamps
    source_ordered["__source_row"] = np.arange(len(raw), dtype=np.int64)
    processed_index = esc_uniform[["__source_row"]].copy()
    base = source_ordered.merge(processed_index, on="__source_row", how="inner", validate="one_to_one")
    # Keep every supplied field as-is, then add a full preprocessed view.
    result = base.drop(columns="__source_row").copy()
    result["id_alerta_original"] = result["id_alerta"]
    result["timestamp_original"] = result[timestamp_col]
    result[timestamp_col] = pd.to_datetime(result[timestamp_col], format=config["data"]["timestamp_format"], errors="raise")
    result["escalada_L2_original"] = result["escalada_L2"]
    result["escalada_procedimiento_original"] = result["escalada_procedimiento"]

    # Use identifier-based one-to-one joins for all transformed fields.
    esc_join = esc_uniform.set_index("id_alerta", verify_integrity=True)
    rep_join = rep_uniform.set_index("id_alerta", verify_integrity=True)
    raw_by_id = raw.set_index("id_alerta", verify_integrity=True)
    corrected_by_id = esc_loaded.set_index("id_alerta", verify_integrity=True)
    ids = result["id_alerta"]
    result["escalada_procedimiento_corregida"] = ids.map(esc_join["escalada_procedimiento"])
    result["escalada_combinada_antes_estandarizacion"] = ids.map(
        corrected_by_id["Label0"]
    )
    result["escalada_estandarizada"] = ids.map(esc_join["Label0"])
    result["reportado_original"] = result["reportado"]
    result["reportado_estandarizado"] = ids.map(rep_join["Label0"])
    result["escalada_ordinal_label"] = ids.map(esc_join["OrdinalLabel"])
    result["escalada_ambigua"] = ids.map(esc_join["Ambiguous"])
    result["reportado_ordinal_label"] = ids.map(rep_join["OrdinalLabel"])
    result["reportado_ambigua"] = ids.map(rep_join["Ambiguous"])
    correction_by_id = corrected_by_id["escalada_procedimiento"].ne(
        raw_by_id["escalada_procedimiento"]
    )
    result["escalada_8x5_correccion_aplicada"] = ids.map(correction_by_id)
    # Preserve the complete cleaned frame, including generated schedule/weight/label auxiliaries.
    for col in esc_uniform.columns:
        if col in {"id_alerta", "__source_row", "Label0", "OrdinalLabel", "Ambiguous"}:
            continue
        result[f"preprocessed__{col}"] = ids.map(esc_join[col])
    result["preprocessed__Label0_escalada"] = ids.map(esc_join["Label0"])
    result["preprocessed__OrdinalLabel_escalada"] = ids.map(esc_join["OrdinalLabel"])
    result["preprocessed__Ambiguous_escalada"] = ids.map(esc_join["Ambiguous"])
    result["preprocessed__Label0_reportado"] = ids.map(rep_join["Label0"])
    result["preprocessed__OrdinalLabel_reportado"] = ids.map(rep_join["OrdinalLabel"])
    result["preprocessed__Ambiguous_reportado"] = ids.map(rep_join["Ambiguous"])

    if len(result) != len(esc_uniform) or result["id_alerta"].duplicated().any():
        raise AssertionError("Identifier cardinality changed while combining target pipelines")
    if set(result["id_alerta"]) != set(esc_uniform["id_alerta"]):
        raise AssertionError("Identifier correspondence failed while combining target pipelines")

    # Derive partition masks by identifier after preserving raw CSV order in result.
    mask_by_id = dict(zip(esc_uniform["id_alerta"], masks["train"].to_numpy()))
    test_by_id = dict(zip(esc_uniform["id_alerta"], masks["test"].to_numpy()))
    result["partition_train"] = result["id_alerta"].map(mask_by_id).fillna(False).astype(bool)
    result["partition_test"] = result["id_alerta"].map(test_by_id).fillna(False).astype(bool)

    # Label statistics at each requested semantic stage.
    escalada_original = raw_by_id["escalada_L2"]
    procedure_original = raw_by_id["escalada_procedimiento"]
    procedure_corrected = corrected_by_id["escalada_procedimiento"]
    combined = esc_loaded.set_index("id_alerta", verify_integrity=True)["Label0"]
    esc_pre_label = esc_pre.set_index("id_alerta", verify_integrity=True)["Label0"]
    esc_final = esc_join["Label0"]
    reportado_original = raw_by_id["reportado"]
    reportado_pre = rep_pre.set_index("id_alerta", verify_integrity=True)["Label0"]
    reportado_final = rep_join["Label0"]
    label_stages = {
        "escalada_L2_original": escalada_original,
        "escalada_procedimiento_original": procedure_original,
        "escalada_procedimiento_corregida": procedure_corrected,
        "escalada_combinada_pre_uniform": combined,
        "escalada_after_preprocessing_before_uniform": esc_pre_label,
        "escalada_estandarizada": esc_final,
        "reportado_original": reportado_original,
        "reportado_after_preprocessing_before_uniform": reportado_pre,
        "reportado_estandarizado": reportado_final,
    }
    stats = {name: label_stats(values) for name, values in label_stages.items()}
    stats["transitions"] = {
        "escalada_combined_to_standardized": transition(combined, esc_final),
        "escalada_combined_to_after_preprocessing": transition(combined, esc_pre_label),
        "escalada_pre_uniform_to_standardized": transition(esc_pre_label, esc_final),
        "escalada_procedure_original_to_corrected": transition(procedure_original, procedure_corrected),
        "reportado_original_to_standardized": transition(reportado_original, reportado_final),
        "reportado_original_to_after_preprocessing": transition(reportado_original, reportado_pre),
        "reportado_pre_uniform_to_standardized": transition(reportado_pre, reportado_final),
    }
    stats["by_partition"] = {}
    for partition, mask in [("train", masks["train"]), ("test", masks["test"])]:
        partition_ids = esc_uniform.loc[mask, "id_alerta"].tolist()
        stats["by_partition"][partition] = {
            "rows": len(partition_ids),
            "labels": {
                "escalada_L2_original": label_stats(raw_by_id.loc[partition_ids, "escalada_L2"]),
                "escalada_procedimiento_original": label_stats(raw_by_id.loc[partition_ids, "escalada_procedimiento"]),
                "escalada_procedimiento_corregida": label_stats(corrected_by_id.loc[partition_ids, "escalada_procedimiento"]),
                "escalada_combined_pre_uniform": label_stats(combined.loc[partition_ids]),
                "escalada_after_preprocessing_before_uniform": label_stats(esc_pre_label.loc[partition_ids]),
                "escalada_standardized": label_stats(esc_final.loc[partition_ids]),
                "reportado_original": label_stats(reportado_original.loc[partition_ids]),
                "reportado_standardized": label_stats(reportado_final.loc[partition_ids]),
            },
        }
    stats["temporal_partition_bounds"] = {
        name: {
            "count": int(mask.sum()),
            "start": esc_uniform.loc[mask, timestamp_col].min(),
            "end": esc_uniform.loc[mask, timestamp_col].max(),
        }
        for name, mask in masks.items()
    }

    by_group = {}
    for group_col in ["proyecto", "severidad", "@timestamp0", "tramitador"]:
        if group_col == "@timestamp0":
            monthly = esc_uniform.copy()
            monthly["periodo"] = monthly[timestamp_col].dt.to_period("M").astype(str)
            by_group["periodo"] = prevalences_by(monthly, "Label0", "periodo")
            by_group["periodo_reportado"] = prevalences_by(
                rep_uniform.assign(periodo=rep_uniform[timestamp_col].dt.to_period("M").astype(str)),
                "Label0", "periodo"
            )
        elif group_col == "tramitador":
            by_group["tramitador_activity"] = esc_uniform[group_col].value_counts(dropna=False).to_dict()
        else:
            by_group[f"{group_col}_escalada"] = prevalences_by(esc_uniform, "Label0", group_col)
            by_group[f"{group_col}_reportado"] = prevalences_by(rep_uniform, "Label0", group_col)

    ambiguous = {}
    for label, uniform in [("escalada", esc_uniform), ("reportado", rep_uniform)]:
        ambiguous[label] = {
            "ambiguous_patterns": int(
                uniform.loc[uniform["Ambiguous"], config["preprocessing"]["uniform_columns"]]
                .drop_duplicates()
                .shape[0]
            ),
            "affected_alerts": int(uniform["Ambiguous"].sum()),
            "ordinal_label_distribution": distribution(uniform["OrdinalLabel"]),
        }

    exclusions = run_diagnostic_preprocessing(path, raw["id_alerta"], config, module)
    original_sorted = raw_timestamps.is_monotonic_increasing
    counts = {
        "original": len(raw),
        "after_load": len(esc_loaded),
        "after_preprocessing": len(esc_pre),
        "after_uniform": len(esc_uniform),
        "excluded": len(raw) - len(esc_pre),
        "excluded_reasons": exclusions,
        "timestamp_sorted_in_source": bool(original_sorted),
        "n_columns_output": len(result.columns),
    }
    if counts["excluded"] != exclusions["total_excluded"]:
        raise AssertionError(f"Exclusion reason counts do not reconcile: {counts}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path, index=False)
    schema = {str(name): str(dtype) for name, dtype in result.dtypes.items()}
    metadata = {
        "source_dataset": path.name,
        "source_path": str(path),
        "source_sha256": sha256(path),
        "source_rows": len(raw),
        "source_columns": list(raw.columns),
        "timestamp_coverage": {"start": raw_timestamps.min(), "end": raw_timestamps.max()},
        "pipeline_source_commit": config["pipeline_source"]["commit"],
        "configuration": config,
        "versions": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "pyarrow": __import__("pyarrow").__version__,
            "pyyaml": yaml.__version__,
        },
        "counts": counts,
        "labels": stats,
        "by_group": by_group,
        "ambiguity": ambiguous,
        "schema": schema,
        "processed_sha256": sha256(output_path),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_level_equivalence": equivalence or "not run against external source checkout",
    }
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--february-csv", required=True, type=Path)
    parser.add_argument("--september-csv", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--original-library",
        type=Path,
        help="Path to SoC_WP4/libraries/uc3mprep2.py for record-level comparison.",
    )
    args = parser.parse_args()
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    compare_module = load_original_module(args.original_library)
    reports = {}
    for key, path, filename in [
        ("february_reference", args.february_csv, "soctra_february_reference.parquet"),
        ("september_canonical", args.september_csv, "soctra_preprocessed.parquet"),
    ]:
        if not path.is_file():
            raise FileNotFoundError(path)
        reports[key] = process_dataset(path, args.output_dir / filename, config, compare_module)
    (args.output_dir / "metadata.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2, default=json_value) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: {"counts": value["counts"], "labels": value["labels"], "processed_sha256": value["processed_sha256"]} for key, value in reports.items()}, ensure_ascii=False, indent=2, default=json_value))


if __name__ == "__main__":
    main()
