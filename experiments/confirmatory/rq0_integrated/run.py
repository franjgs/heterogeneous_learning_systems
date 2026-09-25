"""RQ0 integrated confirmatory runner.

PRETEST is the default and never resolves or loads PACS TEST.  The one-shot
confirmatory evaluation is available only through ``--confirmatory-test`` and
must not be invoked until the implementation has been frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_COMMIT = "8b16394"
PROTOCOL_PATH = ROOT / "docs/experimental_foundations/RQ0_INTEGRATED_DESIGN.md"
B23_OUTPUT = ROOT / "results/pilots/b23_portfolio_opportunity"
B24_OUTPUT = ROOT / "results/pilots/b24_interference_controlled"
DEFAULT_OUTPUT = ROOT / "results/confirmatory/rq0_integrated"
B24_ANALYZE_PATH = ROOT / "experiments/pilots/b24_interference_controlled/analyze.py"
ANALYZE_PATH = Path(__file__).with_name("analyze.py")
RUN_PATH = Path(__file__)
SEEDS = (0, 1, 2, 3, 4)
DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
N_VALUES = (25, 50, 100)
COSTS = (0.0, 0.02, 0.05, 0.10, 0.15)
HORIZONS = (1, 2, 5, 10)
TOLERANCE = 1e-12
EXPECTED_STATES = 70
TEST_SPLIT_IDENTIFIER = "PACS_TEST_FROZEN_UNOPENED"


class TestAccessError(RuntimeError):
    """Raised whenever PRETEST code attempts to cross the TEST boundary."""


@dataclass(frozen=True)
class ModeGuard:
    confirmatory_test: bool = False

    def require_test_access(self, operation: str) -> None:
        if not self.confirmatory_test:
            raise TestAccessError(f"TEST access blocked in PRETEST: {operation}")


def _load_module(name: str, path: Path):
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


analysis = _load_module("rq0_integrated_analysis", ANALYZE_PATH)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def atomic_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    pd.DataFrame(rows).to_csv(temporary, index=False)
    os.replace(temporary, path)


def read_manifest(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"missing manifest: {path}")
    return json.loads(path.read_text())


def valid_cached_evaluation(
    prior: object, result_path: Path, checkpoint_sha256: str
) -> dict[str, object] | None:
    """Return a verified restart payload, otherwise require reevaluation."""
    if not isinstance(prior, dict) or prior.get("status") != "complete" or not result_path.is_file():
        return None
    if sha256_file(result_path) != prior.get("sha256"):
        return None
    payload = json.loads(result_path.read_text())
    if payload.get("checkpoint_sha256") != checkpoint_sha256 or payload.get("evaluation_split") != "test":
        return None
    return payload


def _record_checked(
    artifacts: dict[str, object], artifact_id: str, artifact_type: str
) -> dict[str, object]:
    record = artifacts.get(artifact_id)
    if not isinstance(record, dict) or record.get("status") != "complete":
        raise RuntimeError(f"missing/incomplete artifact {artifact_id}")
    if record.get("artifact_type") != artifact_type:
        raise RuntimeError(f"artifact type mismatch {artifact_id}")
    path = Path(str(record.get("path", "")))
    if not path.is_file():
        raise RuntimeError(f"artifact file missing {artifact_id}")
    if sha256_file(path) != record.get("sha256"):
        raise RuntimeError(f"artifact hash mismatch {artifact_id}")
    return record


def _b24_compatibility() -> tuple[dict[tuple, dict[str, float]], dict[str, object]]:
    # This audit is explicitly VALIDATION-only and rejects payloads whose
    # evaluation_split/test_used provenance differs.
    b24_analyze = _load_module("rq0_b24_analyze", B24_ANALYZE_PATH)
    return b24_analyze.compatibility_audit(B24_OUTPUT, B23_OUTPUT)


def build_inventory() -> tuple[list[dict[str, object]], dict[tuple, dict[str, float]], dict[str, object]]:
    scores, compatibility = _b24_compatibility()
    if compatibility.get("compatible") is not True or compatibility.get("test") != "CLOSED":
        raise RuntimeError("B2.3/B2.4 compatibility audit failed")
    b23 = read_manifest(B23_OUTPUT / "run_manifest.json")
    b24 = read_manifest(B24_OUTPUT / "run_manifest.json")
    if b23["header"].get("test_used") is not False or b24["header"].get("test_used") is not False:
        raise RuntimeError("historical TEST provenance is not closed")
    a23, a24 = b23["artifacts"], b24["artifacts"]
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        for state_type in ("F0", "D"):
            artifact_id = f"{state_type}_s{seed}"
            rec = _record_checked(a23, artifact_id, state_type)
            rows.append({
                "evaluation_id": artifact_id,
                "seed": seed,
                "state_type": state_type,
                "domain": None,
                "N": None,
                "artifact_path": rec["path"],
                "checkpoint_sha256": rec["sha256"],
                "model_fingerprint": rec.get("model_fingerprint"),
                "split_identifier": f"{TEST_SPLIT_IDENTIFIER}|seed={seed}",
                "split_recipe_sha256": b23["header"]["split_library_sha256"],
                "dataset_revision": b23["header"]["dataset_revision"],
                "expected_evaluation_role": "frozen_test_state",
            })
    opportunity_count = replay_count = 0
    for seed in SEEDS:
        for domain in DOMAINS:
            for n in N_VALUES:
                op_id = f"op_s{seed}_{domain}_n{n}"
                rep_id = f"REP_s{seed}_{domain}_n{n}"
                replay_id = f"replay_s{seed}_{domain}_n{n}"
                op = _record_checked(a23, op_id, "opportunity")
                replay = _record_checked(a24, replay_id, "replay")
                rep = _record_checked(a24, rep_id, "REP")
                f0 = a23[f"F0_s{seed}"]
                if rep.get("parent_f0_sha256") != f0.get("sha256"):
                    raise RuntimeError(f"REP F0 genealogy mismatch {rep_id}")
                if rep.get("opportunity_sha256") != op.get("payload_sha256"):
                    raise RuntimeError(f"REP opportunity genealogy mismatch {rep_id}")
                if rep.get("replay_sha256") != replay.get("payload_sha256"):
                    raise RuntimeError(f"REP replay genealogy mismatch {rep_id}")
                opportunity_count += 1
                replay_count += 1
                rows.append({
                    "evaluation_id": rep_id,
                    "seed": seed,
                    "state_type": "REP",
                    "domain": domain,
                    "N": n,
                    "artifact_path": rep["path"],
                    "checkpoint_sha256": rep["sha256"],
                    "model_fingerprint": rep.get("model_fingerprint"),
                    "parent_f0_sha256": rep["parent_f0_sha256"],
                    "opportunity_sha256": rep["opportunity_sha256"],
                    "replay_sha256": rep["replay_sha256"],
                    "split_identifier": f"{TEST_SPLIT_IDENTIFIER}|seed={seed}",
                    "split_recipe_sha256": b23["header"]["split_library_sha256"],
                    "dataset_revision": b23["header"]["dataset_revision"],
                    "expected_evaluation_role": "frozen_test_state",
                })
    counts = pd.Series([row["state_type"] for row in rows]).value_counts().to_dict()
    if len(rows) != EXPECTED_STATES or counts != {"REP": 60, "F0": 5, "D": 5}:
        raise RuntimeError(f"evaluation inventory mismatch: {counts}")
    if opportunity_count != 60 or replay_count != 60:
        raise RuntimeError("opportunity/replay inventory mismatch")
    return rows, scores, compatibility


def _score(scores: dict[tuple, dict[str, float]], kind: str, seed: int, n: int, domain: str) -> dict[str, float]:
    if kind in {"F0", "D"}:
        return scores[(kind, seed, n, domain)]
    return scores[(kind, seed, n, domain)]


def validation_reconstruction(
    inventory: list[dict[str, object]], scores: dict[tuple, dict[str, float]]
) -> tuple[list[dict[str, object]], float]:
    frozen = pd.read_csv(B24_OUTPUT / "state_metrics.csv")
    frozen_b23 = pd.read_csv(B23_OUTPUT / "state_metrics.csv")
    if frozen.evaluation_split.ne("validation").any() or frozen.test_used.ne(False).any():
        raise RuntimeError("B2.4 frozen metrics are not VALIDATION-only")
    rows: list[dict[str, object]] = []
    errors: list[float] = []
    # Physical F0/D are repeated analytically by case; emit each physical state once.
    for item in inventory:
        seed = int(item["seed"])
        domain = item.get("domain")
        n = item.get("N")
        kind = str(item["state_type"])
        if kind == "REP":
            vector = scores[("REP", seed, int(n), str(domain))]
            match = frozen[(frozen.seed == seed) & (frozen.domain == domain) & (frozen.N == n) & (frozen.method == "REP")]
            if len(match) != 1:
                raise RuntimeError(f"frozen REP metric cardinality mismatch {item['evaluation_id']}")
            expected = {d: float(match.iloc[0][f"S_{d}"]) for d in DOMAINS}
        else:
            vector = scores[(kind, seed, 25, "photo")]
            match = frozen_b23[(frozen_b23.seed == seed) & (frozen_b23.state_type == kind)]
            if len(match) != 1 or match.evaluation_split.ne("validation").any() or match.test_used.ne(False).any():
                raise RuntimeError(f"frozen B2.3 base metric cardinality mismatch {item['evaluation_id']}")
            expected = {d: float(match.iloc[0][f"ba_{d}"]) for d in DOMAINS}
        row = {"evaluation_id": item["evaluation_id"], "seed": seed, "state_type": kind, "domain": domain, "N": n}
        for d in DOMAINS:
            observed = float(vector[d])
            error = abs(observed - float(expected[d]))
            errors.append(error)
            row[f"ba_{d}"] = observed
            row[f"frozen_error_{d}"] = error
        rows.append(row)
    return rows, max(errors, default=float("inf"))


def policy_checks(scores: dict[tuple, dict[str, float]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    max_identity = 0.0
    max_frozen_value_error = 0.0
    mismatches = 0
    frozen_values = pd.read_csv(B24_OUTPUT / "method_values.csv")
    for seed in SEEDS:
        for domain in DOMAINS:
            for n in N_VALUES:
                f0 = scores[("F0", seed, n, domain)]
                deep = scores[("D", seed, n, domain)]
                rep = scores[("REP", seed, n, domain)]
                for c in COSTS:
                    q = analysis.quantities(domain, c, f0, deep, rep)
                    match = frozen_values[
                        (frozen_values.seed == seed) & (frozen_values.domain == domain)
                        & (frozen_values.N == n) & (frozen_values.method == "REP")
                        & np.isclose(frozen_values.c, c, atol=0.0, rtol=0.0)
                    ]
                    if len(match) != 1:
                        raise RuntimeError("frozen B2.4 method-value cardinality mismatch")
                    max_frozen_value_error = max(
                        max_frozen_value_error,
                        abs(q.v0 - float(match.iloc[0].V_F0)),
                        abs(q.v_rep - float(match.iloc[0].V)),
                        abs(q.delta_v - float(match.iloc[0].DeltaV)),
                    )
                    for h in HORIZONS:
                        expected_star = h * q.delta_v - max(q.rho, 0.0)
                        identity_error = abs(analysis.kappa_star(q, h) - expected_star)
                        max_identity = max(max_identity, identity_error)
                        for kappa in analysis.diagnostic_kappas(q, h):
                            result = analysis.policy_row(q, q, h, kappa)
                            action_match = result["hls_action"] == result["sepomega_action"]
                            coord_error = abs(float(result["Delta_coord"]))
                            if not action_match or coord_error > TOLERANCE:
                                mismatches += 1
                            rows.append({
                                "seed": seed, "domain": domain, "N": n, "c": c, "h": h,
                                "kappa": kappa, "rho": q.rho, "DeltaV": q.delta_v,
                                "Omega": analysis.omega(q, h, kappa),
                                "kappa_star": expected_star, "kappa_star_error": identity_error,
                                **result, "action_match": action_match, "coord_error": coord_error,
                            })
    values = [float(row[key]) for row in rows for key in ("rho", "DeltaV", "Omega", "J_SEP", "J_HLS", "J_SEP_Omega", "DeltaJ", "Delta_coord")]
    analysis.assert_finite(values)
    return rows, {
        "policy_rows": len(rows),
        "hls_sepomega_mismatches": mismatches,
        "max_identity_error": max_identity,
        "max_frozen_value_error": max_frozen_value_error,
        "nan_count": int(np.isnan(np.asarray(values)).sum()),
    }


def _read_git_ancestor() -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", PROTOCOL_COMMIT, "HEAD"],
        cwd=ROOT, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def run_pretest(output_dir: Path, tests_passed: bool = False) -> dict[str, object]:
    print("RQ0 integrated confirmation | mode=PRETEST | TEST_STATUS=CLOSED", flush=True)
    guard = ModeGuard(False)
    try:
        guard.require_test_access("pretest self-check")
    except TestAccessError:
        barrier_pass = True
    else:
        barrier_pass = False
    inventory, scores, compatibility = build_inventory()
    reconstruction, max_error = validation_reconstruction(inventory, scores)
    checks, policy = policy_checks(scores)
    hash_mismatches = 0
    provenance_mismatches = 0 if compatibility.get("compatible") is True else 1
    status = "PASS" if all((
        barrier_pass, len(inventory) == 70, max_error <= TOLERANCE,
        policy["hls_sepomega_mismatches"] == 0, policy["max_identity_error"] <= TOLERANCE,
        policy["max_frozen_value_error"] <= TOLERANCE,
        policy["nan_count"] == 0, hash_mismatches == 0, provenance_mismatches == 0,
        tests_passed, _read_git_ancestor(),
    )) else "FAIL"
    evaluation_manifest = {
        "protocol_commit": PROTOCOL_COMMIT,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "implementation_sha256": sha256_file(RUN_PATH),
        "analysis_sha256": sha256_file(ANALYZE_PATH),
        "TEST_STATUS": "CLOSED",
        "states": inventory,
        "manifest_sha256": sha256_json(inventory),
    }
    atomic_json(output_dir / "evaluation_manifest.json", evaluation_manifest)
    atomic_csv(output_dir / "validation_reconstruction.csv", reconstruction)
    atomic_csv(output_dir / "policy_checks.csv", checks)
    pretest_manifest = {
        "protocol_commit": PROTOCOL_COMMIT,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "TEST_STATUS": "CLOSED",
        "grids": {"seeds": list(SEEDS), "domains": list(DOMAINS), "N": list(N_VALUES), "c": list(COSTS), "h": list(HORIZONS)},
        "evaluation_manifest_sha256": sha256_file(output_dir / "evaluation_manifest.json"),
        "validation_scores_sha256": sha256_json(reconstruction),
        "policy_checks_sha256": sha256_json(checks),
    }
    atomic_json(output_dir / "pretest_manifest.json", pretest_manifest)
    summary = {
        "protocol_commit": PROTOCOL_COMMIT,
        "TEST_STATUS": "CLOSED",
        "states_expected": 70,
        "states_verified": len(inventory),
        "validation_max_error": max_error,
        "hls_sepomega_mismatches": policy["hls_sepomega_mismatches"],
        "max_identity_error": policy["max_identity_error"],
        "max_frozen_value_error": policy["max_frozen_value_error"],
        "hash_mismatches": hash_mismatches,
        "provenance_mismatches": provenance_mismatches,
        "nan_count": policy["nan_count"],
        "tests_passed": bool(tests_passed),
        "test_barrier_passed": barrier_pass,
        "pretest_status": status,
    }
    atomic_json(output_dir / "pretest_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return summary


def _confirmatory_evaluator(*args, guard: ModeGuard, **kwargs) -> None:
    """Future one-shot evaluator; unreachable without the explicit mode gate.

    The implementation is deliberately imported lazily so PRETEST cannot even
    resolve a TEST split.  See ``run_confirmatory_test`` below.
    """
    guard.require_test_access("resolve/load/evaluate PACS TEST")
    namespace = args[0]
    import torch
    from sklearn.metrics import balanced_accuracy_score
    from torch import nn
    from torchvision.models import mobilenet_v2, resnet50

    b20_path = ROOT / "experiments/pilots/b2_pacs_calibration/run.py"
    b20 = _load_module("rq0_b20_run", b20_path)
    evaluation_manifest = read_manifest(namespace.output_dir / "evaluation_manifest.json")
    states = evaluation_manifest.get("states", [])
    if len(states) != EXPECTED_STATES:
        raise RuntimeError("frozen evaluation manifest is not 70 states")
    for item in states:
        path = Path(str(item["artifact_path"]))
        if sha256_file(path) != item["checkpoint_sha256"]:
            raise RuntimeError(f"checkpoint changed after freeze: {item['evaluation_id']}")

    b23_manifest = read_manifest(B23_OUTPUT / "run_manifest.json")
    if sha256_file(namespace.dataset_manifest) != b23_manifest["header"].get("manifest_sha256"):
        raise RuntimeError("frozen PACS dataset manifest hash mismatch")
    frame = pd.read_csv(namespace.dataset_manifest)
    b20.validate_manifest(frame)
    lookup = frame.set_index("sample_id", drop=False)
    splits = {seed: b20.stratified_splits(frame, seed) for seed in SEEDS}
    confirm_dir = namespace.output_dir / "confirmatory_test"
    marker = confirm_dir / "COMPLETE.json"
    raw_dir = confirm_dir / "raw_evaluations"
    raw_dir.mkdir(parents=True, exist_ok=True)
    index_path = confirm_dir / "progress.json"
    progress = read_manifest(index_path) if index_path.exists() else {"evaluations": {}}

    def restore(kind: str, checkpoint: Path):
        model = resnet50(weights=None) if kind == "D" else mobilenet_v2(weights=None)
        if kind == "D":
            model.fc = nn.Linear(model.fc.in_features, 7)
        else:
            model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 7)
        payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
        model.load_state_dict(payload["model_state"], strict=True)
        model.eval()
        return model

    completed = reused = 0
    session_started = time.perf_counter()
    rows = []
    for number, item in enumerate(states, start=1):
        eval_id = str(item["evaluation_id"])
        result_path = raw_dir / f"{eval_id}.json"
        prior = progress["evaluations"].get(eval_id)
        cached = valid_cached_evaluation(prior, result_path, str(item["checkpoint_sha256"]))
        if cached is not None:
            reused += 1
            rows.append(cached)
            continue
        print(f"[evaluation {number:2d}/70] {eval_id}", flush=True)
        evaluation_started = time.perf_counter()
        seed = int(item["seed"])
        test_ids = splits[seed]["test"]
        test_frame = lookup.loc[test_ids].reset_index(drop=True)
        model = restore(str(item["state_type"]), Path(str(item["artifact_path"])))
        labels, predictions, domains, sample_ids = b20.evaluate(model, test_frame, namespace.image_root, torch.device("cpu"), 16)
        scores = {}
        for domain in DOMAINS:
            mask = domains == domain
            scores[domain] = float(balanced_accuracy_score(labels[mask], predictions[mask]))
        payload = {
            "evaluation_id": eval_id, "seed": seed, "state_type": item["state_type"],
            "domain": item.get("domain"), "N": item.get("N"),
            "checkpoint_sha256": item["checkpoint_sha256"],
            "test_ids_sha256": sha256_json([int(x) for x in sample_ids]),
            "scores": scores, "sample_ids": [int(x) for x in sample_ids],
            "labels": [int(x) for x in labels], "predictions": [int(x) for x in predictions],
            "domains": [str(x) for x in domains], "evaluation_split": "test",
            "trained": False, "duration_seconds": time.perf_counter() - evaluation_started,
        }
        atomic_json(result_path, payload)
        progress["evaluations"][eval_id] = {
            "status": "complete", "sha256": sha256_file(result_path),
            "checkpoint_sha256": item["checkpoint_sha256"],
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        atomic_json(index_path, progress)
        completed += 1
        rows.append(payload)

    if len(rows) != 70:
        raise RuntimeError("confirmatory evaluation count mismatch")
    validation_scores, _ = _b24_compatibility()
    test_scores: dict[tuple, dict[str, float]] = {}
    by_id = {row["evaluation_id"]: row for row in rows}
    for seed in SEEDS:
        for domain in DOMAINS:
            for n in N_VALUES:
                for kind, eval_id in (
                    ("F0", f"F0_s{seed}"), ("D", f"D_s{seed}"),
                    ("REP", f"REP_s{seed}_{domain}_n{n}"),
                ):
                    test_scores[(kind, seed, n, domain)] = by_id[eval_id]["scores"]
    surface, classification = analysis.confirmatory_surface(validation_scores, test_scores)
    if classification["max_delta_coord"] > TOLERANCE:
        raise RuntimeError("SEP-Omega/HLS confirmatory equivalence failed")
    surface.to_csv(confirm_dir / "kappa_surface.csv", index=False)
    coefficient_rows = []
    for seed in SEEDS:
        for domain in DOMAINS:
            for n in N_VALUES:
                for c in COSTS:
                    q_hat = analysis.quantities(
                        domain, c, validation_scores[("F0", seed, n, domain)],
                        validation_scores[("D", seed, n, domain)],
                        validation_scores[("REP", seed, n, domain)],
                    )
                    q_test = analysis.quantities(
                        domain, c, test_scores[("F0", seed, n, domain)],
                        test_scores[("D", seed, n, domain)],
                        test_scores[("REP", seed, n, domain)],
                    )
                    for h in HORIZONS:
                        coefficient_rows.append({
                            "seed": seed, "domain": domain, "N": n, "c": c, "h": h,
                            "rho_validation": q_hat.rho, "DeltaV_validation": q_hat.delta_v,
                            "kappa_star_validation": analysis.kappa_star(q_hat, h),
                            "rho_test": q_test.rho, "DeltaV_test": q_test.delta_v,
                            "kappa_star_test": analysis.kappa_star(q_test, h),
                            "policies_diverge_on_positive_interval": bool(
                                q_hat.rho >= 0 and analysis.kappa_star(q_hat, h) > 0
                            ),
                            "DeltaJ_intercept_when_divergent": -q_test.rho + h * q_test.delta_v,
                            "DeltaJ_kappa_slope_when_divergent": -1.0,
                        })
    pd.DataFrame(coefficient_rows).to_csv(confirm_dir / "case_policy_surface.csv", index=False)
    pd.DataFrame([
        {k: v for k, v in row.items() if k not in {"sample_ids", "labels", "predictions", "domains", "scores"}}
        | {f"ba_{d}": row["scores"][d] for d in DOMAINS}
        for row in rows
    ]).to_csv(confirm_dir / "raw_state_metrics.csv", index=False)
    final = {
        **classification, "TEST_STATUS": "OPENED_ONCE_AND_EVALUATED",
        "evaluations": 70, "completed_this_session": completed,
        "reused_after_restart": reused, "failed": 0, "pending": 0,
        "session_duration_seconds": time.perf_counter() - session_started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    atomic_json(confirm_dir / "summary.json", final)
    atomic_json(marker, {"summary_sha256": sha256_file(confirm_dir / "summary.json"), **final})
    print(json.dumps(final, indent=2, sort_keys=True), flush=True)


def run_confirmatory_test(args: argparse.Namespace) -> None:
    guard = ModeGuard(True)
    evaluation_manifest_path = args.output_dir / "evaluation_manifest.json"
    freeze = read_manifest(evaluation_manifest_path)
    pretest_manifest = read_manifest(args.output_dir / "pretest_manifest.json")
    summary = read_manifest(args.output_dir / "pretest_summary.json")
    if summary.get("pretest_status") != "PASS" or summary.get("TEST_STATUS") != "CLOSED":
        raise RuntimeError("refusing TEST: PRETEST PASS freeze is absent")
    if freeze.get("protocol_commit") != PROTOCOL_COMMIT:
        raise RuntimeError("refusing TEST: protocol commit mismatch")
    if freeze.get("protocol_sha256") != sha256_file(PROTOCOL_PATH):
        raise RuntimeError("refusing TEST: protocol document changed after freeze")
    if pretest_manifest.get("evaluation_manifest_sha256") != sha256_file(evaluation_manifest_path):
        raise RuntimeError("refusing TEST: evaluation manifest changed after freeze")
    if freeze.get("implementation_sha256") != sha256_file(RUN_PATH) or freeze.get("analysis_sha256") != sha256_file(ANALYZE_PATH):
        raise RuntimeError("refusing TEST: implementation changed after PRETEST freeze")
    marker = args.output_dir / "confirmatory_test" / "COMPLETE.json"
    if marker.exists() and not args.audit_existing:
        raise RuntimeError("confirmation output already complete; use --audit-existing for read-only audit")
    if args.audit_existing:
        if not marker.is_file():
            raise RuntimeError("no completed confirmation output to audit")
        complete = read_manifest(marker)
        summary_path = args.output_dir / "confirmatory_test" / "summary.json"
        if not summary_path.is_file() or sha256_file(summary_path) != complete.get("summary_sha256"):
            raise RuntimeError("completed confirmation summary is missing or corrupt")
        progress = read_manifest(args.output_dir / "confirmatory_test" / "progress.json")
        if len(progress.get("evaluations", {})) != 70:
            raise RuntimeError("completed confirmation does not contain 70 evaluations")
        print(json.dumps(read_manifest(summary_path), indent=2, sort_keys=True), flush=True)
        return
    # This call is the sole TEST boundary. It is intentionally impossible in
    # PRETEST and will be completed only after the code itself is frozen.
    _confirmatory_evaluator(args, guard=guard)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirmatory-test", action="store_true", help="explicitly open the frozen TEST endpoint")
    parser.add_argument("--audit-existing", action="store_true", help="read-only audit of completed confirmation output")
    parser.add_argument("--tests-passed", action="store_true", help="record that the frozen pretest test suite passed")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--image-root", type=Path, help="required only for future confirmatory TEST inference")
    parser.add_argument(
        "--dataset-manifest", type=Path,
        default=ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv",
        help="frozen PACS manifest; read only in explicit confirmatory mode",
    )
    parser.add_argument("--device", choices=("cpu",), default="cpu")
    args = parser.parse_args(argv)
    if args.audit_existing and not args.confirmatory_test:
        parser.error("--audit-existing requires --confirmatory-test")
    if args.confirmatory_test and args.image_root is None and not args.audit_existing:
        parser.error("--image-root is required with --confirmatory-test")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.confirmatory_test:
        run_confirmatory_test(args)
    else:
        run_pretest(args.output_dir, tests_passed=args.tests_passed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
