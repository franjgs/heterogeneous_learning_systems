"""Training-free preregistered analysis for PACS B2.4."""

from __future__ import annotations

import importlib.util
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RUN_PATH = Path(__file__).with_name("run.py")


def _load_run():
    existing = sys.modules.get("b24_run")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location("b24_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUN_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


b24 = _load_run()


def operational_value(
    scores: dict[str, float], deep: dict[str, float], cost: float
) -> tuple[float, str, dict[str, float]]:
    contributions: dict[str, float] = {}
    routes: list[str] = []
    for domain in b24.DOMAINS:
        fast = float(scores[domain])
        deep_value = float(deep[domain]) - cost
        routes.append("F" if fast >= deep_value else "D")
        contributions[domain] = 0.25 * max(fast, deep_value)
    return float(sum(contributions.values())), ",".join(routes), contributions


def _validated_b24_payload(
    artifacts: dict[str, object], artifact_id: str, expected: dict[str, object]
) -> tuple[dict[str, object], dict[str, object]]:
    record = artifacts.get(artifact_id, {})
    if record.get("status") != "complete" or any(record.get(key) != value for key, value in expected.items()):
        raise RuntimeError(f"missing or incompatible B2.4 artifact {artifact_id}")
    path = Path(str(record.get("path", "")))
    if not path.is_file() or b24.sha256_file(path) != record.get("sha256"):
        raise RuntimeError(f"missing or corrupt B2.4 artifact {artifact_id}")
    payload = b24.b23.load_checkpoint(path)
    if payload.get("test_used") is not False or payload.get("evaluation_split") != "validation":
        raise RuntimeError(f"invalid evaluation provenance {artifact_id}")
    if payload.get("model_fingerprint") != b24.b23.state_dict_fingerprint(payload["model_state"]):
        raise RuntimeError(f"model fingerprint mismatch {artifact_id}")
    return payload, record


def compatibility_audit(
    output_dir: Path, b23_output: Path
) -> tuple[dict[tuple[str, int, int, str], dict[str, float]], dict[str, object]]:
    parent_scores, parent_audit = b24.parent_audit(b23_output)
    if parent_audit.get("compatible") is not True or parent_audit.get("test") != "CLOSED":
        raise RuntimeError("B2.3 parent audit failed")
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("B2.4 results incomplete: run_manifest.json missing")
    manifest = json.loads(manifest_path.read_text())
    header = manifest.get("header", {})
    required_header = {
        "protocol_id": b24.PROTOCOL_ID,
        "frozen_protocol_commit": b24.FROZEN_PROTOCOL_COMMIT,
        "protocol_sha256": b24.sha256_file(b24.PROTOCOL_PATH),
        "implementation_sha256": b24.sha256_file(b24.RUN_PATH if hasattr(b24, "RUN_PATH") else Path(b24.__file__)),
        "analysis_sha256": b24.sha256_file(Path(__file__)),
        "b23_manifest_sha256": b24.sha256_file(b23_output / "run_manifest.json"),
        "dataset_revision": b24.b23.DATASET_REVISION,
        "device": "cpu",
        "test_used": False,
        "seeds": list(b24.SEEDS),
        "domains": list(b24.DOMAINS),
        "N": list(b24.N_VALUES),
        "costs": list(b24.COSTS),
    }
    for key, expected in required_header.items():
        if header.get(key) != expected:
            raise RuntimeError(f"B2.4 run provenance mismatch: {key}")
    parent_manifest = json.loads((b23_output / "run_manifest.json").read_text())
    artifacts = manifest.get("artifacts", {})
    scores: dict[tuple[str, int, int, str], dict[str, float]] = {}
    opportunity_projections = 0
    for spec in b24.plan_cases():
        f0_payload, f0_record = b24.parent_checkpoint(parent_manifest, f"F0_s{spec.seed}")
        d_payload, d_record = b24.parent_checkpoint(parent_manifest, f"D_s{spec.seed}")
        opportunity, opportunity_hash, _ = b24.parent_opportunity(parent_manifest, spec)
        std, std_record = b24.parent_std(parent_manifest, spec)
        if std.get("parent_f0_sha256") != f0_record["sha256"] or std.get("opportunity_sha256") != opportunity_hash:
            raise RuntimeError(f"STD genealogy mismatch {spec.key}")
        scores[("F0", spec.seed, spec.n, spec.domain)] = {
            domain: float(f0_payload["scores"][domain]) for domain in b24.DOMAINS
        }
        scores[("D", spec.seed, spec.n, spec.domain)] = {
            domain: float(d_payload["scores"][domain]) for domain in b24.DOMAINS
        }
        scores[("STD", spec.seed, spec.n, spec.domain)] = {
            domain: float(std["scores"][domain]) for domain in b24.DOMAINS
        }
        replay_record = artifacts.get(spec.replay_id, {})
        replay_path = Path(str(replay_record.get("path", "")))
        if replay_record.get("artifact_type") != "replay" or not replay_path.is_file() or b24.sha256_file(replay_path) != replay_record.get("sha256"):
            raise RuntimeError(f"missing/corrupt replay {spec.replay_id}")
        replay, replay_hash = b24.read_envelope(
            replay_path,
            {
                "artifact_type": "replay", "seed": spec.seed, "domain": spec.domain, "N": spec.n,
                "parent_f0_sha256": f0_record["sha256"], "test_used": False,
            },
        )
        f0_ids = set(int(value) for value in f0_payload["training_ids"])
        replay_ids = tuple(int(value) for value in replay["sample_ids"])
        opportunity_ids = set(int(value) for value in opportunity["sample_ids"])
        if len(replay_ids) != spec.n or len(set(replay_ids)) != spec.n or not set(replay_ids).issubset(f0_ids):
            raise RuntimeError(f"replay membership mismatch {spec.key}")
        if set(replay_ids) & opportunity_ids or any(row["domain"] == spec.domain for row in replay["samples"]):
            raise RuntimeError(f"replay leakage {spec.key}")
        o50_schedule, mixed_schedule = b24.build_schedules(spec, tuple(opportunity["sample_ids"]), replay)
        steps, exposures = b24.dose(spec.n)
        o50_audit = b24.schedule_audit(spec, "O50", o50_schedule, opportunity_hash, None)
        rep_audit = b24.schedule_audit(spec, "REP", mixed_schedule[:steps], opportunity_hash, replay_hash)
        rep2_audit = b24.schedule_audit(spec, "REP2", mixed_schedule, opportunity_hash, replay_hash)
        if o50_audit["opportunity_projection_sha256"] != rep_audit["opportunity_projection_sha256"]:
            raise RuntimeError(f"O50/REP opportunity mismatch {spec.key}")
        expected_doses = {
            "O50": (steps, exposures, exposures // 2, exposures // 2, 0),
            "REP": (steps, exposures, exposures // 2, 0, exposures // 2),
            "REP2": (2 * steps, 2 * exposures, exposures, 0, exposures),
        }
        for method, artifact_id, audit, extra in (
            ("O50", spec.o50_id, o50_audit, {}),
            ("REP", spec.rep_id, rep_audit, {"trajectory_id": f"mixed_s{spec.seed}_{spec.domain}_n{spec.n}", "step": steps}),
            ("REP2", spec.rep2_id, rep2_audit, {"trajectory_id": f"mixed_s{spec.seed}_{spec.domain}_n{spec.n}", "step": 2 * steps}),
        ):
            payload, _ = _validated_b24_payload(
                artifacts,
                artifact_id,
                {
                    "artifact_type": method, "seed": spec.seed, "domain": spec.domain, "N": spec.n,
                    "parent_f0_sha256": f0_record["sha256"], "opportunity_sha256": opportunity_hash,
                    **extra,
                },
            )
            if payload.get("deep_sha256") != d_record["sha256"] or payload.get("validation_ids_sha256") != f0_payload["validation_ids_sha256"]:
                raise RuntimeError(f"parent/evaluation mismatch {artifact_id}")
            expected = expected_doses[method]
            observed = (
                int(payload["steps"]), int(payload["processed_slots"]),
                int(payload["informative_opportunity_exposures"]),
                int(payload["duplicate_opportunity_slots"]), int(payload["replay_exposures"]),
            )
            if observed != expected or payload.get("schedule_sha256") != audit["schedule_sha256"]:
                raise RuntimeError(f"dose/schedule mismatch {artifact_id}")
            if payload.get("opportunity_projection_sha256") != audit["opportunity_projection_sha256"]:
                raise RuntimeError(f"opportunity projection mismatch {artifact_id}")
            scores[(method, spec.seed, spec.n, spec.domain)] = {
                domain: float(payload["scores"][domain]) for domain in b24.DOMAINS
            }
        rep_payload, _ = _validated_b24_payload(artifacts, spec.rep_id, {"artifact_type": "REP"})
        rep2_payload, _ = _validated_b24_payload(artifacts, spec.rep2_id, {"artifact_type": "REP2"})
        if rep_payload.get("trajectory_id") != rep2_payload.get("trajectory_id") or rep2_payload.get("rep_checkpoint_sha256") != artifacts[spec.rep_id]["sha256"]:
            raise RuntimeError(f"REP/REP2 continuation mismatch {spec.key}")
        opportunity_projections += 1
    if len(scores) != b24.TOTAL_CASES * 6:
        raise RuntimeError("state-score cardinality mismatch")
    return scores, {
        "compatible": True,
        "test": "CLOSED",
        "families": b24.TOTAL_CASES,
        "new_fits": b24.TOTAL_NEW_FITS,
        "new_evaluations": b24.TOTAL_NEW_EVALUATIONS,
        "method_states": len(scores),
        "matched_opportunity_projections": opportunity_projections,
    }


def method_tables(
    scores: dict[tuple[str, int, int, str], dict[str, float]]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state_rows: list[dict[str, object]] = []
    value_rows: list[dict[str, object]] = []
    competence_rows: list[dict[str, object]] = []
    for spec in b24.plan_cases():
        f0 = scores[("F0", spec.seed, spec.n, spec.domain)]
        deep = scores[("D", spec.seed, spec.n, spec.domain)]
        methods = {method: scores[(method, spec.seed, spec.n, spec.domain)] for method in ("STD", "O50", "REP", "REP2")}
        metrics: dict[str, dict[str, float]] = {}
        for method, values in methods.items():
            deltas = {domain: float(values[domain]) - float(f0[domain]) for domain in b24.DOMAINS}
            local = deltas[spec.domain]
            cross = sum(value for domain, value in deltas.items() if domain != spec.domain)
            metrics[method] = {"DeltaS_local": local, "DeltaS_cross": cross, "I": -cross}
            row: dict[str, object] = {
                "seed": spec.seed, "domain": spec.domain, "N": spec.n, "method": method,
                "DeltaS_local": local, "DeltaS_cross": cross, "I": -cross,
                "evaluation_split": "validation", "test_used": False,
            }
            for domain in b24.DOMAINS:
                row[f"S_F0_{domain}"] = f0[domain]
                row[f"S_{domain}"] = values[domain]
                row[f"DeltaS_{domain}"] = deltas[domain]
            state_rows.append(row)
            for cost in b24.COSTS:
                v0, route0, contributions0 = operational_value(f0, deep, cost)
                value, route, contributions = operational_value(values, deep, cost)
                value_row: dict[str, object] = {
                    "seed": spec.seed, "domain": spec.domain, "N": spec.n, "method": method,
                    "c": cost, "V_F0": v0, "V": value, "DeltaV": value - v0,
                    "routing_F0": route0, "routing": route,
                }
                for affected in b24.DOMAINS:
                    value_row[f"DeltaV_contribution_{affected}"] = contributions[affected] - contributions0[affected]
                if not np.isclose(
                    value - v0,
                    sum(value_row[f"DeltaV_contribution_{affected}"] for affected in b24.DOMAINS),
                    atol=b24.NUMERIC_TOLERANCE,
                    rtol=0,
                ):
                    raise RuntimeError("DeltaV contribution identity failed")
                value_rows.append(value_row)
        delta_i = metrics["REP"]["I"] - metrics["O50"]["I"]
        delta_l = metrics["REP"]["DeltaS_local"] - metrics["O50"]["DeltaS_local"]
        g = -delta_i
        sacrifice = max(0.0, -delta_l)
        competence_rows.append(
            {
                "seed": spec.seed, "domain": spec.domain, "N": spec.n,
                "DeltaI": delta_i, "DeltaL": delta_l, "G_cross_recovered": g,
                "local_sacrifice": sacrifice,
                "cross_recovery_exceeds_local_sacrifice": bool(delta_l < 0 and g > sacrifice),
                "G_plus_DeltaL": g + delta_l,
            }
        )
    return pd.DataFrame(state_rows), pd.DataFrame(value_rows), pd.DataFrame(competence_rows)


def contrast_table(values: pd.DataFrame, competence: pd.DataFrame) -> pd.DataFrame:
    pivot = values.pivot(index=["seed", "domain", "N", "c"], columns="method", values="DeltaV").reset_index()
    pivot["DeltaQ"] = pivot["REP"] - pivot["O50"]
    pivot["O50_minus_STD"] = pivot["O50"] - pivot["STD"]
    pivot["REP_minus_STD"] = pivot["REP"] - pivot["STD"]
    pivot["REP2_minus_STD"] = pivot["REP2"] - pivot["STD"]
    pivot["REP2_minus_O50"] = pivot["REP2"] - pivot["O50"]
    pivot["REP2_minus_REP"] = pivot["REP2"] - pivot["REP"]
    return pivot.merge(competence, on=["seed", "domain", "N"], validate="many_to_one")


def _zero(value: float) -> float:
    return 0.0 if abs(value) <= b24.NUMERIC_TOLERANCE else float(value)


def classify_values(values: pd.Series) -> tuple[str, int, int, float]:
    adjusted = values.astype(float).map(_zero)
    positive = int((adjusted > 0).sum())
    nonpositive = int((adjusted <= 0).sum())
    mean = float(adjusted.mean())
    if positive >= 4 and mean > 0:
        return "POSITIVE", positive, nonpositive, mean
    if nonpositive >= 4 and mean <= 0:
        return "NULL", positive, nonpositive, mean
    return "INCONCLUSIVE", positive, nonpositive, mean


def classifications(
    competence: pd.DataFrame, contrasts: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    seed_comp = competence.groupby("seed", as_index=False).agg(
        R=("DeltaI", lambda values: float((-values).mean())),
        P=("DeltaL", "mean"),
    )
    seed_value = contrasts.groupby(["seed", "c"], as_index=False).agg(Q=("DeltaQ", "mean"))
    rows: list[dict[str, object]] = []
    for metric, column in (("interference_reduction", "R"), ("local_learning", "P")):
        label, positive, nonpositive, mean = classify_values(seed_comp[column])
        rows.append(
            {"outcome": metric, "c": np.nan, "classification": label, "positive_seeds": positive, "nonpositive_seeds": nonpositive, "mean": mean}
        )
    for cost, group in seed_value.groupby("c"):
        label, positive, nonpositive, mean = classify_values(group.Q)
        rows.append(
            {"outcome": "future_value", "c": cost, "classification": label, "positive_seeds": positive, "nonpositive_seeds": nonpositive, "mean": mean}
        )
    # Exact domain x N regimes are descriptive and cannot replace the globals.
    exact_rows: list[dict[str, object]] = []
    for (domain, n), group in competence.groupby(["domain", "N"]):
        for metric, favorable in (("interference_reduction", -group.DeltaI), ("local_learning", group.DeltaL)):
            label, positive, nonpositive, mean = classify_values(favorable)
            exact_rows.append({"domain": domain, "N": n, "outcome": metric, "c": np.nan, "classification": label, "positive_seeds": positive, "nonpositive_seeds": nonpositive, "mean": mean})
    for (domain, n, cost), group in contrasts.groupby(["domain", "N", "c"]):
        label, positive, nonpositive, mean = classify_values(group.DeltaQ)
        exact_rows.append({"domain": domain, "N": n, "outcome": "future_value", "c": cost, "classification": label, "positive_seeds": positive, "nonpositive_seeds": nonpositive, "mean": mean})
    return pd.DataFrame(rows), pd.DataFrame(exact_rows), seed_comp.merge(
        seed_value.pivot(index="seed", columns="c", values="Q").add_prefix("Q_c").reset_index(), on="seed"
    )


def summary_markdown(audit: dict[str, object], classes: pd.DataFrame) -> str:
    lines = [
        "# PACS B2.4 interference-controlled development", "",
        "## Integrity", "", "- Compatibility: PASS.", "- Device: CPU.", "- TEST: CLOSED.",
        f"- New fits: {audit['new_fits']}/{b24.TOTAL_NEW_FITS}.",
        f"- New validation evaluations: {audit['new_evaluations']}/{b24.TOTAL_NEW_EVALUATIONS}.",
        f"- Method states: {audit['method_states']}/{b24.TOTAL_METHOD_STATES}.", "",
        "## Preregistered classifications", "",
    ]
    for row in classes.itertuples(index=False):
        suffix = "" if pd.isna(row.c) else f" at c={row.c:g}"
        lines.append(f"- {row.outcome}{suffix}: **{row.classification}** ({row.positive_seeds}/5 favorable seed summaries; mean={row.mean:.6f}).")
    lines.extend(
        [
            "", "The primary causal contrast is REP minus O50. STD remains the frozen B2.3 reference and REP2 is the preregistered secondary dose contrast. No pair, Gamma, portfolio-rescue, TEST, or post-hoc analysis is included.", "",
        ]
    )
    return "\n".join(lines)


def write_provenance_views(output_dir: Path) -> None:
    manifest = json.loads((output_dir / "run_manifest.json").read_text())
    replay_rows: list[dict[str, object]] = []
    state_rows: list[dict[str, object]] = []
    excluded = {"model_state", "optimizer_state", "rng_state"}
    for artifact_id, record in sorted(manifest["artifacts"].items()):
        path = Path(record["path"])
        if record["artifact_type"] == "replay":
            payload, payload_hash = b24.read_envelope(path)
            replay_rows.append({"artifact_id": artifact_id, **record, "provenance": payload | {"payload_sha256": payload_hash}})
        elif record["artifact_type"] in {"O50", "REP", "REP2"}:
            payload = b24.b23.load_checkpoint(path)
            state_rows.append(
                {
                    "artifact_id": artifact_id,
                    **record,
                    "provenance": {key: value for key, value in payload.items() if key not in excluded},
                }
            )
    (output_dir / "replay_buffers.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in replay_rows)
    )
    (output_dir / "development_states.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in state_rows)
    )


def final_summary(audit: dict[str, object], classes: pd.DataFrame, output_dir: Path, elapsed: float) -> str:
    lines = [
        "=" * 60, "B2.4 complete", "=" * 60, "TEST: CLOSED", "Compatibility: PASS",
        f"New fits: {audit['new_fits']}/{b24.TOTAL_NEW_FITS}",
        f"New VALIDATION evaluations: {audit['new_evaluations']}/{b24.TOTAL_NEW_EVALUATIONS}",
        f"Method states: {audit['method_states']}/{b24.TOTAL_METHOD_STATES}",
        f"Method-value rows: {b24.TOTAL_METHOD_VALUE_ROWS}/{b24.TOTAL_METHOD_VALUE_ROWS}",
    ]
    for row in classes.itertuples(index=False):
        suffix = "" if pd.isna(row.c) else f" c={row.c:g}"
        lines.append(f"{row.outcome}{suffix}: {row.classification}")
    lines.extend([f"Elapsed analysis: {b24.b23.format_duration(elapsed)}", f"Detailed results: {output_dir / 'summary.md'}", "=" * 60])
    return "\n".join(lines)


def run_analysis(output_dir: Path, b23_output: Path) -> dict[str, object]:
    started = time.perf_counter()
    print("[analysis 1/4] B2.3/B2.4 compatibility audit", flush=True)
    scores, audit = compatibility_audit(output_dir, b23_output)
    print("[analysis 2/4] Frozen state and operational-value expansion", flush=True)
    states, values, competence = method_tables(scores)
    contrasts = contrast_table(values, competence)
    if len(states) != b24.TOTAL_METHOD_STATES or len(values) != b24.TOTAL_METHOD_VALUE_ROWS or len(contrasts) != b24.TOTAL_PRIMARY_CONTRAST_ROWS:
        raise RuntimeError("B2.4 analytical cardinality mismatch")
    if states.isna().any().any() or values.isna().any().any() or contrasts.isna().any().any():
        raise RuntimeError("NaN in B2.4 scientific outputs")
    print("[analysis 3/4] Preregistered classifications", flush=True)
    classes, exact, seed_summaries = classifications(competence, contrasts)
    write_provenance_views(output_dir)
    b24.atomic_csv(output_dir / "state_metrics.csv", states)
    b24.atomic_csv(output_dir / "method_values.csv", values)
    b24.atomic_csv(output_dir / "primary_contrasts.csv", contrasts)
    b24.atomic_csv(output_dir / "competence_contrasts.csv", competence)
    b24.atomic_csv(output_dir / "classifications.csv", classes)
    b24.atomic_csv(output_dir / "exact_regime_classifications.csv", exact)
    b24.atomic_csv(output_dir / "seed_summaries.csv", seed_summaries)
    (output_dir / "summary.md").write_text(summary_markdown(audit, classes))
    print("[analysis 4/4] Validated outputs", flush=True)
    print(final_summary(audit, classes, output_dir, time.perf_counter() - started), flush=True)
    return {
        "audit": audit, "state_metrics": states, "method_values": values,
        "primary_contrasts": contrasts, "competence_contrasts": competence,
        "classifications": classes,
    }


def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=b24.DEFAULT_OUTPUT)
    parser.add_argument("--b23-output", type=Path, default=b24.DEFAULT_B23_OUTPUT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    arguments = parse_args()
    run_analysis(arguments.output_dir, arguments.b23_output)
