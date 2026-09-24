"""Compatibility-first, training-free analysis for PACS B2.3."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RUN_PATH = Path(__file__).with_name("run.py")


def _load_run():
    existing = sys.modules.get("b23_run")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location("b23_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {RUN_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


b23 = _load_run()


def operational_value(scores: dict[str, float], deep: dict[str, float], cost: float) -> tuple[float, str, dict[str, float]]:
    choices: list[str] = []
    contributions: dict[str, float] = {}
    for domain in b23.DOMAINS:
        fast = float(scores[domain])
        deep_value = float(deep[domain]) - cost
        choices.append("F" if fast >= deep_value else "D")  # frozen tie convention
        contributions[domain] = 0.25 * max(fast, deep_value)
    return float(sum(contributions.values())), ",".join(choices), contributions


def learning_value(scores: dict[str, float]) -> float:
    return float(np.mean([scores[domain] for domain in b23.DOMAINS]))


def primary_row(
    seed: int, n: int, domain_i: str, domain_j: str, cost: float, future_weight: int,
    f0: dict[str, float], deep: dict[str, float], fi: dict[str, float], fj: dict[str, float], fij: dict[str, float],
) -> dict[str, object]:
    v0, r0, contrib0 = operational_value(f0, deep, cost)
    vi, ri, contrib_i = operational_value(fi, deep, cost)
    vj, rj, contrib_j = operational_value(fj, deep, cost)
    vij, rij, contrib_ij = operational_value(fij, deep, cost)
    delta_i, delta_j, delta_ij = vi - v0, vj - v0, vij - v0
    gamma_oper = delta_ij - delta_i - delta_j
    gamma_four = vij - vi - vj + v0
    if not np.isclose(gamma_oper, gamma_four, atol=b23.NUMERIC_TOLERANCE, rtol=0):
        raise RuntimeError("Gamma_oper identities differ")
    rho_i = float(f0[domain_i]) - (float(deep[domain_i]) - cost)
    rho_j = float(f0[domain_j]) - (float(deep[domain_j]) - cost)
    h_i = -rho_i + future_weight * delta_i
    h_j = -rho_j + future_weight * delta_j
    h_ij = -(rho_i + rho_j) + future_weight * delta_ij
    identity = h_i + h_j + future_weight * gamma_oper
    if not np.isclose(h_ij, identity, atol=b23.NUMERIC_TOLERANCE, rtol=0):
        raise RuntimeError("H identity fails")
    rescue = bool(rho_i > 0 and rho_j > 0 and h_i < 0 and h_j < 0 and h_ij > 0)
    interaction_needed = bool(rescue and h_i + h_j < 0 and future_weight * gamma_oper > -(h_i + h_j))
    if interaction_needed != rescue:
        raise RuntimeError("interaction-needed identity fails")
    row: dict[str, object] = {
        "seed": seed, "N": n, "domain_i": domain_i, "domain_j": domain_j, "pair": f"{domain_i}__{domain_j}",
        "c": cost, "B": future_weight, "kappa": b23.KAPPA, "rho_i": rho_i, "rho_j": rho_j,
        "V_F0": v0, "V_Fi": vi, "V_Fj": vj, "V_Fij": vij,
        "DeltaV_i": delta_i, "DeltaV_j": delta_j, "DeltaV_ij": delta_ij,
        "Gamma_oper": gamma_oper,
        "Gamma_learn": learning_value(fij) - learning_value(fi) - learning_value(fj) + learning_value(f0),
        "H_i": h_i, "H_j": h_j, "H_ij": h_ij, "B_Gamma_oper": future_weight * gamma_oper,
        "H_j_given_i": h_ij - h_i, "H_i_given_j": h_ij - h_j,
        "M_j_given_stored_i": h_ij + rho_i, "M_i_given_stored_j": h_ij + rho_j,
        "portfolio_rescue": rescue, "interaction_needed": interaction_needed,
        "routing_F0": r0, "routing_Fi": ri, "routing_Fj": rj, "routing_Fij": rij,
    }
    for domain in b23.DOMAINS:
        row[f"F0_ba_{domain}"] = f0[domain]
        row[f"D_ba_{domain}"] = deep[domain]
        row[f"Fi_ba_{domain}"] = fi[domain]
        row[f"Fj_ba_{domain}"] = fj[domain]
        row[f"Fij_ba_{domain}"] = fij[domain]
        row[f"DeltaS_i_{domain}"] = fi[domain] - f0[domain]
        row[f"DeltaS_j_{domain}"] = fj[domain] - f0[domain]
        row[f"DeltaS_ij_{domain}"] = fij[domain] - f0[domain]
        row[f"interaction_S_{domain}"] = fij[domain] - fi[domain] - fj[domain] + f0[domain]
        row[f"V_contribution_F0_{domain}"] = contrib0[domain]
        row[f"V_contribution_Fi_{domain}"] = contrib_i[domain]
        row[f"V_contribution_Fj_{domain}"] = contrib_j[domain]
        row[f"V_contribution_Fij_{domain}"] = contrib_ij[domain]
        row[f"Gamma_oper_contribution_{domain}"] = contrib_ij[domain] - contrib_i[domain] - contrib_j[domain] + contrib0[domain]
        route_values = [int(route.split(",")[b23.DOMAINS.index(domain)] == "D") for route in (r0, ri, rj, rij)]
        row[f"Gamma_route_{domain}"] = route_values[3] - route_values[1] - route_values[2] + route_values[0]
    return row


def dose_row(seed: int, n: int, domain_i: str, domain_j: str, cost: float, f0: dict[str, float], deep: dict[str, float], fij: dict[str, float], fij_cm: dict[str, float]) -> dict[str, object]:
    v0, _, _ = operational_value(f0, deep, cost)
    vij, _, _ = operational_value(fij, deep, cost)
    vcm, rcm, _ = operational_value(fij_cm, deep, cost)
    return {
        "seed": seed, "N": n, "domain_i": domain_i, "domain_j": domain_j, "pair": f"{domain_i}__{domain_j}", "c": cost,
        "V_F0": v0, "V_Fij": vij, "V_Fij_CM": vcm, "DeltaV_ij": vij - v0,
        "DeltaV_ij_CM": vcm - v0, "D_dose": vij - vcm, "routing_Fij_CM": rcm,
    }


def classify(primary: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    keys = ["N", "pair", "c", "B"]
    grouped = primary.groupby(keys, as_index=False).agg(n_seeds=("seed", "nunique"), rescue_seeds=("portfolio_rescue", "sum"))
    if len(primary) != b23.TOTAL_PRIMARY_ROWS or len(grouped) != 3 * 6 * 5 * 4 or not (grouped.n_seeds == 5).all():
        raise RuntimeError("classification requires the complete frozen grid")
    if (grouped.rescue_seeds >= 3).any():
        return "POSITIVE", grouped
    if not primary.portfolio_rescue.any():
        return "NULL", grouped
    return "INCONCLUSIVE", grouped


def validate_checkpoint_record(record: dict[str, object], artifact_id: str, expected_type: str) -> dict[str, object]:
    if record.get("artifact_type") != expected_type or record.get("status") != "complete":
        raise RuntimeError(f"incompatible manifest record {artifact_id}")
    path = Path(str(record.get("path", "")))
    if not path.is_file() or b23.sha256_file(path) != record.get("sha256"):
        raise RuntimeError(f"missing or corrupt artifact {artifact_id}")
    payload = b23.load_checkpoint(path)
    if "model_state" in payload and payload.get("model_fingerprint") != b23.state_dict_fingerprint(payload["model_state"]):
        raise RuntimeError(f"model-state fingerprint mismatch {artifact_id}")
    return payload


def compatibility_audit(output_dir: Path) -> tuple[dict[tuple, dict[str, float]], dict[str, object]]:
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("B2.3 artifacts are incomplete: run_manifest.json is missing")
    manifest = json.loads(manifest_path.read_text())
    header = manifest.get("header", {})
    if header.get("protocol_id") != b23.PROTOCOL_ID or header.get("device") != "cpu" or header.get("test_used") is not False or header.get("deterministic_algorithms") is not True:
        raise RuntimeError("run-level provenance is incompatible")
    frozen_hashes = {
        "protocol_sha256": b23.sha256_file(b23.PROTOCOL_PATH),
        "config_sha256": b23.sha256_file(b23.CONFIG_PATH),
        "implementation_sha256": b23.SCIENTIFIC_IMPLEMENTATION_SHA256,
        "analysis_sha256": b23.SCIENTIFIC_ANALYSIS_SHA256,
        "b20_runner_sha256": b23.SCIENTIFIC_B20_RUNNER_SHA256,
        "split_library_sha256": b23.sha256_file(b23.B20_LIBRARY_PATH),
        "dataset_revision": b23.DATASET_REVISION,
        "dataset_sha256": b23.DATASET_SHA256,
    }
    for key, expected in frozen_hashes.items():
        if header.get(key) != expected:
            raise RuntimeError(f"run-level provenance mismatch: {key}")
    artifacts = manifest.get("artifacts", {})
    if b23.deterministic_fixture() != b23.deterministic_fixture():
        raise RuntimeError("deterministic CPU fixture did not reproduce")
    split_path = output_dir / "split_manifest.csv"
    if not split_path.is_file():
        raise RuntimeError("split_manifest.csv is missing")
    split_frame = pd.read_csv(split_path)
    if set(split_frame.role) != {"BASE", "TRANSFER", "VALIDATION"} or split_frame.duplicated(["seed", "sample_id"]).any():
        raise RuntimeError("visible split manifest is incomplete or duplicated")
    split_ids = {
        (seed, role): set(split_frame.loc[(split_frame.seed == seed) & (split_frame.role == role), "sample_id"].astype(int))
        for seed in b23.SEEDS for role in ("BASE", "TRANSFER", "VALIDATION")
    }
    scores: dict[tuple, dict[str, float]] = {}
    base_payloads: dict[tuple[str, int], dict[str, object]] = {}
    maximum_ids: dict[tuple[int, str], tuple[int, ...]] = {}
    for seed in b23.SEEDS:
        for name in ("F0", "D"):
            artifact_id = f"{name}_s{seed}"
            payload = validate_checkpoint_record(artifacts.get(artifact_id, {}), artifact_id, name)
            if payload.get("evaluation_split") != "validation" or payload.get("test_used") is not False:
                raise RuntimeError(f"invalid evaluation provenance in {artifact_id}")
            training_ids = [int(value) for value in payload.get("training_ids", [])]
            if payload.get("training_ids_sha256") != b23.sha256_json(training_ids):
                raise RuntimeError(f"base training ID hash mismatch {artifact_id}")
            allowed = split_ids[(seed, "BASE")] if name == "F0" else split_ids[(seed, "BASE")] | split_ids[(seed, "TRANSFER")]
            if not set(training_ids).issubset(allowed) or (name == "D" and set(training_ids) != allowed):
                raise RuntimeError(f"base split provenance mismatch {artifact_id}")
            base_payloads[(name, seed)] = payload
            scores[(name, seed)] = {domain: float(payload["scores"][domain]) for domain in b23.DOMAINS}

    opportunity_hashes: dict[tuple[int, str, int], str] = {}
    opportunity_ids: dict[tuple[int, str, int], tuple[int, ...]] = {}
    for seed in b23.SEEDS:
        for domain in b23.DOMAINS:
            maximum_id = f"opmax_s{seed}_{domain}"
            maximum_record = artifacts.get(maximum_id, {})
            if maximum_record.get("artifact_type") != "opportunity_max" or maximum_record.get("status") != "complete":
                raise RuntimeError(f"missing maximum opportunity stream {maximum_id}")
            maximum_path = Path(str(maximum_record.get("path", "")))
            if not maximum_path.is_file() or b23.sha256_file(maximum_path) != maximum_record.get("sha256"):
                raise RuntimeError(f"corrupt maximum opportunity stream {maximum_id}")
            maximum, _ = b23.read_envelope(maximum_path, {"protocol_id": b23.PROTOCOL_ID, "dataset_revision": b23.DATASET_REVISION, "seed": seed, "domain": domain, "N": 100, "teacher_query_count": 100, "pseudo_label_count": 100, "creation_action": "D", "test_used": False})
            if len(maximum["sample_ids"]) != 100 or not set(map(int, maximum["sample_ids"])).issubset(split_ids[(seed, "TRANSFER")]):
                raise RuntimeError(f"maximum opportunity is not a 100-example TRANSFER stream {maximum_id}")
            maximum_ids[(seed, domain)] = tuple(map(int, maximum["sample_ids"]))
        previous: list[int] = []
        for domain in b23.DOMAINS:
            previous = []
            for n in b23.N_VALUES:
                artifact_id = f"op_s{seed}_{domain}_n{n}"
                record = artifacts.get(artifact_id, {})
                if record.get("artifact_type") != "opportunity" or record.get("status") != "complete":
                    raise RuntimeError(f"missing opportunity {artifact_id}")
                path = Path(str(record.get("path", "")))
                if not path.is_file() or b23.sha256_file(path) != record.get("sha256"):
                    raise RuntimeError(f"corrupt opportunity {artifact_id}")
                payload, digest = b23.read_envelope(path, {"protocol_id": b23.PROTOCOL_ID, "dataset_revision": b23.DATASET_REVISION, "seed": seed, "domain": domain, "N": n, "creation_action": "D", "test_used": False})
                ids = [int(value) for value in payload["sample_ids"]]
                if len(ids) != n or ids[: len(previous)] != previous or payload["teacher_query_count"] != 0 or payload["source_stream_teacher_query_count"] != 100 or payload["pseudo_label_count"] != n:
                    raise RuntimeError(f"opportunity prefix/query mismatch {artifact_id}")
                if not set(ids).issubset(split_ids[(seed, "TRANSFER")]):
                    raise RuntimeError(f"opportunity contains a non-TRANSFER sample {artifact_id}")
                if tuple(ids) != maximum_ids[(seed, domain)][:n]:
                    raise RuntimeError(f"opportunity is not the immutable maximum-stream prefix {artifact_id}")
                gate = payload.get("action_gate", {})
                if gate.get("F") != {"teacher_query_count": 0, "pseudo_label_count": 0, "student_updated": False}:
                    raise RuntimeError(f"action-F gate queried or updated in {artifact_id}")
                if gate.get("D") != {"opportunity_example_count": n, "pseudo_label_count": n}:
                    raise RuntimeError(f"action-D gate mismatch in {artifact_id}")
                if payload["deep_checkpoint_sha256"] != artifacts[f"D_s{seed}"]["sha256"]:
                    raise RuntimeError(f"opportunity D parent mismatch {artifact_id}")
                opportunity_hashes[(seed, domain, n)] = digest
                opportunity_ids[(seed, domain, n)] = tuple(ids)
                previous = ids

    singletons, joints = b23.plan_specs()
    for spec in singletons:
        artifact_id = spec.artifact_id
        record = artifacts.get(artifact_id, {})
        payload = validate_checkpoint_record(record, artifact_id, "singleton")
        steps, exposures = b23.dose(spec.n)
        expected = {
            "parent_f0_sha256": artifacts[f"F0_s{spec.seed}"]["sha256"],
            "deep_sha256": artifacts[f"D_s{spec.seed}"]["sha256"],
            "opportunity_sha256": opportunity_hashes[(spec.seed, spec.domain, spec.n)],
            "steps": steps, "batch_size": 16, "total_exposures": exposures,
            "validation_ids_sha256": base_payloads[("F0", spec.seed)]["validation_ids_sha256"],
            "evaluation_split": "validation", "test_used": False,
        }
        schedule = b23.singleton_schedule(spec.seed, spec.n, spec.domain, opportunity_ids[(spec.seed, spec.domain, spec.n)])
        expected["schedule_sha256"] = b23.sha256_json(schedule)
        if any(payload.get(key) != value for key, value in expected.items()):
            raise RuntimeError(f"singleton genealogy/dose mismatch {artifact_id}")
        scores[("Fi", spec.seed, spec.n, spec.domain)] = {domain: float(payload["scores"][domain]) for domain in b23.DOMAINS}

    for spec in joints:
        artifact_id = spec.artifact_id
        record = artifacts.get(artifact_id, {})
        payload = validate_checkpoint_record(record, artifact_id, "joint")
        cm_id = artifact_id + "_CM"
        cm = validate_checkpoint_record(artifacts.get(cm_id, {}), cm_id, "joint_cm")
        steps, exposures = b23.dose(spec.n)
        common = {
            "parent_f0_sha256": artifacts[f"F0_s{spec.seed}"]["sha256"],
            "opportunity_i_sha256": opportunity_hashes[(spec.seed, spec.domain_i, spec.n)],
            "opportunity_j_sha256": opportunity_hashes[(spec.seed, spec.domain_j, spec.n)],
            "trajectory_id": artifact_id,
        }
        if any(payload.get(key) != value or cm.get(key) != value for key, value in common.items()):
            raise RuntimeError(f"joint genealogy mismatch {artifact_id}")
        if (payload.get("steps"), payload.get("batch_size"), payload.get("exposures_i"), payload.get("exposures_j")) != (2 * steps, 16, exposures, exposures):
            raise RuntimeError(f"joint dose mismatch {artifact_id}")
        if (cm.get("step"), cm.get("exposures_i"), cm.get("exposures_j")) != (steps, exposures // 2, exposures // 2):
            raise RuntimeError(f"midpoint dose mismatch {artifact_id}")
        if cm.get("optimizer_state_sha256") != b23.sha256_torch_object(cm.get("optimizer_state")) or cm.get("rng_state_sha256") != b23.sha256_torch_object(cm.get("rng_state")):
            raise RuntimeError(f"midpoint continuation-state hash mismatch {artifact_id}")
        schedule = b23.joint_schedule(
            spec,
            opportunity_ids[(spec.seed, spec.domain_i, spec.n)],
            opportunity_ids[(spec.seed, spec.domain_j, spec.n)],
        )
        schedule_hash = b23.sha256_json(schedule)
        if payload.get("schedule_sha256") != schedule_hash or cm.get("schedule_sha256") != schedule_hash:
            raise RuntimeError(f"joint schedule mismatch {artifact_id}")
        if payload.get("deep_sha256") != artifacts[f"D_s{spec.seed}"]["sha256"]:
            raise RuntimeError(f"joint D provenance mismatch {artifact_id}")
        if payload.get("midpoint_sha256") != artifacts[cm_id]["sha256"]:
            raise RuntimeError(f"midpoint trajectory hash mismatch {artifact_id}")
        for endpoint, endpoint_payload in (("Fij", payload), ("Fij_CM", cm)):
            if endpoint_payload.get("evaluation_split") != "validation" or endpoint_payload.get("test_used") is not False:
                raise RuntimeError(f"joint evaluation provenance mismatch {artifact_id}")
            scores[(endpoint, spec.seed, spec.n, spec.domain_i, spec.domain_j)] = {
                domain: float(endpoint_payload["scores"][domain]) for domain in b23.DOMAINS
            }
    if len(scores) != b23.TOTAL_EVALUATIONS:
        raise RuntimeError(f"expected {b23.TOTAL_EVALUATIONS} compatible validation score vectors, got {len(scores)}")
    if not all(np.isfinite(value) for vector in scores.values() for value in vector.values()):
        raise RuntimeError("non-finite validation metric")
    return scores, {"compatible": True, "evaluations": len(scores), "test": "CLOSED"}


def expand(scores: dict[tuple, dict[str, float]]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    primary: list[dict[str, object]] = []
    dose_rows: list[dict[str, object]] = []
    changes: list[dict[str, object]] = []
    for spec in b23.plan_specs()[1]:
        f0 = scores[("F0", spec.seed)]
        deep = scores[("D", spec.seed)]
        fi = scores[("Fi", spec.seed, spec.n, spec.domain_i)]
        fj = scores[("Fi", spec.seed, spec.n, spec.domain_j)]
        fij = scores[("Fij", spec.seed, spec.n, spec.domain_i, spec.domain_j)]
        cm = scores[("Fij_CM", spec.seed, spec.n, spec.domain_i, spec.domain_j)]
        for cost in b23.COSTS:
            dose_rows.append(dose_row(spec.seed, spec.n, spec.domain_i, spec.domain_j, cost, f0, deep, fij, cm))
            for future_weight in b23.FUTURE_WEIGHTS:
                primary.append(primary_row(spec.seed, spec.n, spec.domain_i, spec.domain_j, cost, future_weight, f0, deep, fi, fj, fij))
        change = {"seed": spec.seed, "N": spec.n, "domain_i": spec.domain_i, "domain_j": spec.domain_j, "pair": spec.pair}
        for domain in b23.DOMAINS:
            change[f"DeltaS_i_{domain}"] = fi[domain] - f0[domain]
            change[f"DeltaS_j_{domain}"] = fj[domain] - f0[domain]
            change[f"DeltaS_ij_{domain}"] = fij[domain] - f0[domain]
            change[f"DeltaS_ij_CM_{domain}"] = cm[domain] - f0[domain]
            change[f"interaction_S_{domain}"] = fij[domain] - fi[domain] - fj[domain] + f0[domain]
        changes.append(change)
    frames = pd.DataFrame(primary), pd.DataFrame(dose_rows), pd.DataFrame(changes)
    if len(frames[0]) != b23.TOTAL_PRIMARY_ROWS or len(frames[1]) != b23.TOTAL_DOSE_ROWS or len(frames[2]) != b23.TOTAL_JOINT_FITS:
        raise RuntimeError("analytical expansion count mismatch")
    if any(frame.isna().any().any() for frame in frames):
        raise RuntimeError("NaN in B2.3 analysis")
    return frames


def representative_cases(primary: pd.DataFrame) -> pd.DataFrame:
    rescues = primary[primary.portfolio_rescue].copy()
    cases: list[pd.Series] = []
    labels: list[str] = []
    selectors: list[tuple[str, pd.Series]] = []
    if not rescues.empty:
        cell_counts = rescues.groupby(["N", "pair", "c", "B"]).seed.transform("nunique")
        rescues = rescues.assign(cell_rescue_seeds=cell_counts)
        selectors.extend(
            [
                ("largest_H_ij", rescues.sort_values(["H_ij", "seed"], ascending=[False, True]).iloc[0]),
                ("nearest_rescue_boundary", rescues.assign(distance=rescues.H_ij.abs()).sort_values(["distance", "seed"]).iloc[0]),
                ("largest_interaction", rescues.sort_values(["B_Gamma_oper", "seed"], ascending=[False, True]).iloc[0]),
                ("most_seed_reproducible", rescues.sort_values(["cell_rescue_seeds", "H_ij", "seed"], ascending=[False, False, True]).iloc[0]),
                ("negative_singletons_positive_joint", rescues.sort_values(["H_ij", "seed"], ascending=[False, True]).iloc[0]),
            ]
        )
    sign_change = primary[(primary.Gamma_learn * primary.Gamma_oper < 0)]
    if not sign_change.empty:
        selectors.append(("learning_operational_sign_change", sign_change.assign(magnitude=(sign_change.Gamma_oper - sign_change.Gamma_learn).abs()).sort_values(["magnitude", "seed"], ascending=[False, True]).iloc[0]))
    nonfavorable = primary[(primary.rho_i > 0) & (primary.rho_j > 0) & ~primary.portfolio_rescue]
    if not nonfavorable.empty:
        selectors.append(("nearest_nonrescue_boundary", nonfavorable.assign(distance=nonfavorable.H_ij.abs()).sort_values(["distance", "seed"]).iloc[0]))
    for label, row in selectors:
        labels.append(label)
        cases.append(row)
    result = pd.DataFrame(cases)
    result.insert(0, "case", labels)
    return result.drop_duplicates(["case"])


def threshold_table(primary: pd.DataFrame) -> pd.DataFrame:
    base = primary.drop_duplicates(["seed", "N", "pair", "c"])
    rows: list[dict[str, object]] = []
    for row in base.itertuples(index=False):
        for label, numerator, denominator in (
            ("B_star_joint", row.rho_i + row.rho_j, row.DeltaV_ij),
            ("B_star_i", row.rho_i, row.DeltaV_i),
            ("B_star_j", row.rho_j, row.DeltaV_j),
        ):
            if denominator > 0:
                rows.append({"seed": row.seed, "N": row.N, "pair": row.pair, "c": row.c, "threshold": label, "value": numerator / denominator})
    return pd.DataFrame(rows, columns=["seed", "N", "pair", "c", "threshold", "value"])


def aggregate_table(primary: pd.DataFrame) -> pd.DataFrame:
    columns = ["DeltaV_i", "DeltaV_j", "DeltaV_ij", "Gamma_learn", "Gamma_oper", "H_i", "H_j", "H_ij"]
    rows: list[dict[str, object]] = []
    for (n, pair), group in primary.groupby(["N", "pair"]):
        for metric in columns:
            values = group[metric].astype(float)
            rows.append(
                {
                    "N": n, "pair": pair, "metric": metric, "count": len(values), "mean": values.mean(), "std": values.std(ddof=1),
                    "min": values.min(), "max": values.max(), "n_positive": int((values > 0).sum()), "n_negative": int((values < 0).sum()), "n_zero": int((values == 0).sum()),
                }
            )
    return pd.DataFrame(rows)


def write_provenance_views(output_dir: Path, scores: dict[tuple, dict[str, float]]) -> None:
    """Materialize the protocol's auditable JSONL views from the canonical manifest."""
    manifest = json.loads((output_dir / "run_manifest.json").read_text())
    artifacts = manifest["artifacts"]
    groups = {"base_states.jsonl": {"F0", "D"}, "opportunities.jsonl": {"opportunity_max", "opportunity"}, "development_states.jsonl": {"singleton", "joint_cm", "joint"}}
    for filename, types in groups.items():
        records: list[dict[str, object]] = []
        for artifact_id, record in sorted(artifacts.items()):
            if record.get("artifact_type") not in types:
                continue
            path = Path(record["path"])
            if record["artifact_type"].startswith("opportunity"):
                payload, payload_hash = b23.read_envelope(path)
                detail = payload | {"payload_sha256": payload_hash}
            else:
                payload = b23.load_checkpoint(path)
                excluded = {"model_state", "optimizer_state", "rng_state"}
                detail = {key: value for key, value in payload.items() if key not in excluded}
            records.append({"artifact_id": artifact_id, **record, "provenance": detail})
        (output_dir / filename).write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records))

    rows: list[dict[str, object]] = []
    for key, value in sorted(scores.items(), key=lambda item: tuple(str(part) for part in item[0])):
        row: dict[str, object] = {"state_type": key[0], "seed": key[1], "evaluation_split": "validation", "test_used": False}
        if key[0] in {"Fi"}:
            row.update({"N": key[2], "domain": key[3]})
        elif key[0] in {"Fij", "Fij_CM"}:
            row.update({"N": key[2], "domain_i": key[3], "domain_j": key[4]})
        row.update({f"ba_{domain}": value[domain] for domain in b23.DOMAINS})
        rows.append(row)
    b23.atomic_csv(output_dir / "state_metrics.csv", pd.DataFrame(rows))


def final_summary(classification: str, audit: dict[str, object], primary: pd.DataFrame, reproducibility: pd.DataFrame, output_dir: Path, elapsed: float) -> str:
    rescues = int(primary.portfolio_rescue.sum())
    unique = int(primary.loc[primary.portfolio_rescue, ["seed", "N", "pair"]].drop_duplicates().shape[0])
    return "\n".join(
        [
            "=" * 60, "B2.3 complete", "=" * 60,
            f"TEST: {audit['test']}", f"Compatibility: {'PASS' if audit['compatible'] else 'FAIL'}",
            f"Fits: {b23.TOTAL_FITS}/{b23.TOTAL_FITS}", f"VALIDATION evaluations: {audit['evaluations']}/{b23.TOTAL_EVALUATIONS}",
            f"Primary rows: {len(primary)}/{b23.TOTAL_PRIMARY_ROWS}", f"Portfolio rescues: {rescues}/{len(primary)}",
            f"Unique learned pair states with rescue: {unique}/{b23.TOTAL_JOINT_FITS}",
            f">=3/5 reproducible cells: {int((reproducibility.rescue_seeds >= 3).sum())}/{len(reproducibility)}",
            f"Classification: {classification}", f"Elapsed: {b23.format_duration(elapsed)}",
            f"Detailed results: {output_dir / 'summary.md'}", "=" * 60,
        ]
    )


def summary_markdown(classification: str, audit: dict[str, object], primary: pd.DataFrame, reproducibility: pd.DataFrame, dose: pd.DataFrame) -> str:
    rescue_count = int(primary.portfolio_rescue.sum())
    return "\n".join(
        [
            "# PACS B2.3 portfolio-opportunity result", "", f"Classification: **{classification}**", "",
            "## Integrity", "", f"- Counterfactual compatibility: PASS ({audit['evaluations']}/250 validation vectors).",
            "- Device: CPU.", "- TEST: CLOSED.", f"- Primary rows: {len(primary)}/1800.", f"- Compute-dose rows: {len(dose)}/450.", "",
            "## Frozen primary event", "", f"Portfolio rescues: {rescue_count}/{len(primary)}.",
            f"Exact cells with rescue in >=2/5, >=3/5, and 5/5 seeds: {int((reproducibility.rescue_seeds >= 2).sum())}, {int((reproducibility.rescue_seeds >= 3).sum())}, {int((reproducibility.rescue_seeds == 5).sum())}.", "",
            "The decomposition tables report learning interaction, operational interaction, absolute singleton/joint value, routing, competence changes, and the frozen midpoint dose sensitivity. No TEST result or universal HLS claim is made.", "",
        ]
    )


def run_analysis(output_dir: Path, started: float | None = None) -> dict[str, object]:
    started = time.perf_counter() if started is None else started
    print("[analysis 1/4] Counterfactual compatibility audit", flush=True)
    try:
        scores, audit = compatibility_audit(output_dir)
    except RuntimeError as error:
        print(f"B2.3 analysis unavailable/INVALID: {error}", flush=True)
        raise
    print("[analysis 2/4] Frozen analytical expansion", flush=True)
    write_provenance_views(output_dir, scores)
    primary, dose, changes = expand(scores)
    classification, reproducibility = classify(primary)
    print("[analysis 3/4] Decomposition and representative cases", flush=True)
    cases = representative_cases(primary)
    thresholds = threshold_table(primary)
    aggregates = aggregate_table(primary)
    b23.atomic_csv(output_dir / "primary_results.csv", primary)
    b23.atomic_csv(output_dir / "reproducibility.csv", reproducibility)
    b23.atomic_csv(output_dir / "compute_dose.csv", dose)
    b23.atomic_csv(output_dir / "competence_changes.csv", changes)
    b23.atomic_csv(output_dir / "representative_cases.csv", cases)
    b23.atomic_csv(output_dir / "continuation_thresholds.csv", thresholds)
    b23.atomic_csv(output_dir / "analysis_aggregates.csv", aggregates)
    (output_dir / "summary.md").write_text(summary_markdown(classification, audit, primary, reproducibility, dose))
    print("[analysis 4/4] Validated outputs", flush=True)
    print(final_summary(classification, audit, primary, reproducibility, output_dir, time.perf_counter() - started), flush=True)
    return {"classification": classification, "audit": audit, "primary": primary, "dose": dose, "reproducibility": reproducibility}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=b23.DEFAULT_OUTPUT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    run_analysis(parse_args().output_dir)
