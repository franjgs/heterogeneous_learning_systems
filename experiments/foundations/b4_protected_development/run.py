"""B4 Protected Portfolio Development (CPU, VALIDATION only).

Default execution is a training-free dry run.  The 60-family scientific run
requires the explicit ``--run-full`` flag.  ``--smoke-case`` executes only the
fixed technical case seed=0/domain=photo/N=25 in a temporary output directory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from hls.experiment_timing import ExperimentTimingLogger  # noqa: E402

B24_RUN_PATH = ROOT / "experiments/pilots/b24_interference_controlled/run.py"
B24_ANALYZE_PATH = ROOT / "experiments/pilots/b24_interference_controlled/analyze.py"
ANALYZE_PATH = Path(__file__).with_name("analyze.py")
DEFAULT_MANIFEST = ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv"
DEFAULT_B23_OUTPUT = ROOT / "results/pilots/b23_portfolio_opportunity"
DEFAULT_B24_OUTPUT = ROOT / "results/pilots/b24_interference_controlled"
DEFAULT_OUTPUT = ROOT / "results/foundations/b4_protected_development"

PROTOCOL_ID = "B4-PACS-protected-development-v1"
TEST_STATUS = "PREVIOUSLY_OPENED_NOT_USED_IN_B4"
DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
SEEDS = (0, 1, 2, 3, 4)
N_VALUES = (25, 50, 100)
COSTS = (0.0, 0.02, 0.05, 0.10, 0.15)
HORIZONS = (1, 2, 5, 10)
PROTECTION_PER_CLASS = 4
PROTECTION_PER_DOMAIN = 7 * PROTECTION_PER_CLASS
PROTECTION_TOTAL = 4 * PROTECTION_PER_DOMAIN
EPSILON_LOCAL = 0.0
EPSILON_CROSS = 0.0
TOTAL_FITS = 60
TOTAL_VALIDATION_EVALUATIONS = 60
TOTAL_CANDIDATE_BLOCKS = sum(20 * (3 * int(np.ceil(n / 16))) for n in N_VALUES)


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


b24 = _load_module("b4_b24_run", B24_RUN_PATH)


def sha256_file(path: Path) -> str:
    return b24.sha256_file(path)


def sha256_json(value: object) -> str:
    return b24.sha256_json(value)


def atomic_json(path: Path, value: object) -> None:
    b24.atomic_json(path, value)


def require_cpu(device: str) -> None:
    if device != "cpu":
        raise ValueError("B4 is CPU-only; MPS/CUDA are prohibited")


def protection_seed(seed: int, domain: str, label: int, sample_id: int) -> bytes:
    return hashlib.sha256(
        f"{PROTOCOL_ID}|protection|{seed}|{domain}|{label}|{sample_id}".encode()
    ).digest()


def build_protection_manifest(
    dataset_manifest: Path, b23_output: Path, b24_output: Path
) -> dict[str, object]:
    # The compatibility audit verifies every B2.4 opportunity/replay/state
    # before B4 freezes protection IDs.
    b24_analysis = _load_module("b4_b24_analysis", B24_ANALYZE_PATH)
    _, audit = b24_analysis.compatibility_audit(b24_output, b23_output)
    if audit.get("compatible") is not True:
        raise RuntimeError("B2.4 provenance audit failed")
    parent = json.loads((b23_output / "run_manifest.json").read_text())
    if parent["header"].get("test_used") is not False:
        raise RuntimeError("B2.3 provenance is not TEST-closed")
    frame = pd.read_csv(dataset_manifest).set_index("sample_id", drop=False)
    sets: dict[str, object] = {}
    for seed in SEEDS:
        f0, f0_record = b24.parent_checkpoint(parent, f"F0_s{seed}")
        training_ids = tuple(int(x) for x in f0["training_ids"])
        train = frame.loc[list(training_ids)]
        samples: list[dict[str, object]] = []
        for domain in DOMAINS:
            for label in range(7):
                cell = train[(train.domain == domain) & (train.label == label)]
                ordered = sorted(
                    (int(x) for x in cell.sample_id),
                    key=lambda sample_id: protection_seed(seed, domain, label, sample_id),
                )
                if len(ordered) < PROTECTION_PER_CLASS:
                    raise RuntimeError(f"insufficient F0 training examples seed={seed} {domain} class={label}")
                for sample_id in ordered[:PROTECTION_PER_CLASS]:
                    row = frame.loc[sample_id]
                    samples.append({
                        "sample_id": sample_id, "domain": domain, "label": int(label),
                        "relative_path": str(row.relative_path), "image_sha256": str(row.sha256),
                    })
        if len(samples) != PROTECTION_TOTAL or len({x["sample_id"] for x in samples}) != PROTECTION_TOTAL:
            raise RuntimeError("invalid protection-set cardinality")
        sets[str(seed)] = {
            "seed": seed, "parent_f0_sha256": f0_record["sha256"],
            "source_training_ids_sha256": f0["training_ids_sha256"],
            "samples": samples, "sample_ids_sha256": sha256_json([x["sample_id"] for x in samples]),
        }
    body = {
        "protocol_id": PROTOCOL_ID,
        "TEST_STATUS": TEST_STATUS,
        "source": "exact F0 training IDs (BASE subset) only",
        "sampling": "SHA-256 ordering within seed x domain x class",
        "examples_per_class": PROTECTION_PER_CLASS,
        "examples_per_domain": PROTECTION_PER_DOMAIN,
        "total_per_seed": PROTECTION_TOTAL,
        "dataset_revision": b24.b23.DATASET_REVISION,
        "dataset_manifest_sha256": sha256_file(dataset_manifest),
        "b23_manifest_sha256": sha256_file(b23_output / "run_manifest.json"),
        "b24_manifest_sha256": sha256_file(b24_output / "run_manifest.json"),
        "sets": sets,
    }
    body["manifest_sha256"] = sha256_json(body)
    return body


def preregistration(protection_manifest: dict[str, object]) -> dict[str, object]:
    blocks = {str(n): b24.dose(n)[0] for n in N_VALUES}
    return {
        "protocol_id": PROTOCOL_ID,
        "implementation_sha256": sha256_file(Path(__file__)),
        "analysis_sha256": sha256_file(ANALYZE_PATH),
        "status": "FROZEN_BEFORE_FULL_RUN",
        "TEST_STATUS": TEST_STATUS,
        "device": "cpu",
        "seeds": list(SEEDS), "domains": list(DOMAINS), "N": list(N_VALUES),
        "c": list(COSTS), "h": list(HORIZONS),
        "baseline": "B2.4 REP reused without retraining",
        "method": "PREP",
        "block_unit": "one B2.4 REP optimizer step",
        "candidate_blocks_by_N": blocks,
        "total_candidate_blocks": TOTAL_CANDIDATE_BLOCKS,
        "epsilon_local": EPSILON_LOCAL, "epsilon_cross": EPSILON_CROSS,
        "reference": "F0 protection-set scores (never previous block)",
        "rollback": "model and optimizer restored exactly; scheduled RNG advances; no retry",
        "candidate_schedule": "exact B2.4 REP schedule, data, labels, optimizer, LR and batch construction",
        "protection_manifest_sha256": protection_manifest["manifest_sha256"],
        "criteria": {
            "A_protection": "mean cross-domain PREP-F0 change >= 0 in >=4/5 seeds",
            "B_learning": "mean local PREP-F0 change >= 0 in >=4/5 seeds",
            "C_value": "at least one exact domain x N structure has DeltaV_PREP(c) > 0 in >=4/5 seeds for every frozen c",
            "D_integration": "at least one frozen c x h cell has kappa_star > 0 in >=4/5 seeds",
            "POSITIVE": "A_protection AND B_learning AND C_value AND D_integration",
            "NULL": "C_value is false AND D_integration is false",
            "INCONCLUSIVE": "all other valid outcomes",
        },
        "training_performed_in_phase_A_outputs": False,
    }


def snapshot_training_state(model: nn.Module, optimizer: torch.optim.Optimizer) -> tuple[dict, dict]:
    return copy.deepcopy(model.state_dict()), copy.deepcopy(optimizer.state_dict())


def restore_training_state(
    model: nn.Module, optimizer: torch.optim.Optimizer, snapshot: tuple[dict, dict]
) -> None:
    model.load_state_dict(snapshot[0], strict=True)
    optimizer.load_state_dict(snapshot[1])


def nested_equal(left: object, right: object) -> bool:
    if isinstance(left, torch.Tensor) and isinstance(right, torch.Tensor):
        return bool(torch.equal(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(nested_equal(left[k], right[k]) for k in left)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(nested_equal(a, b) for a, b in zip(left, right, strict=True))
    return left == right


def protection_scores(model: nn.Module, protection: pd.DataFrame, image_root: Path) -> dict[str, float]:
    return b24.b23.score_model(model, protection, image_root, torch.device("cpu"))


def accept_block(reference: dict[str, float], candidate: dict[str, float], target: str) -> bool:
    for domain in DOMAINS:
        epsilon = EPSILON_LOCAL if domain == target else EPSILON_CROSS
        if candidate[domain] < reference[domain] - epsilon:
            return False
    return True


def train_prep(
    f0_state: dict[str, torch.Tensor],
    schedule: list[list[dict[str, object]]],
    labels: dict[int, int],
    lookup: pd.DataFrame,
    protection: pd.DataFrame,
    image_root: Path,
    seed: int,
    n: int,
    target: str,
    config: dict[str, object],
) -> tuple[nn.Module, dict[str, object]]:
    protection_ids = set(int(x) for x in protection.sample_id)
    opportunity_ids = {
        int(entry["sample_id"])
        for batch in schedule for entry in batch
        if str(entry["role"]).startswith("opportunity")
    }
    if protection_ids & opportunity_ids:
        raise RuntimeError("protection set overlaps the current opportunity")
    training_seed = b24.b23.derived_training_seed(seed, n)
    b24.seed_everything(training_seed)
    model = b24.b23.b20.make_model("fast", training_seed, torch.device("cpu"), pretrained=False)
    model.load_state_dict(f0_state)
    optimizer = torch.optim.SGD(
        model.parameters(), lr=float(config["fast"]["learning_rate"]),
        momentum=float(config["fast"]["momentum"]), weight_decay=0,
    )
    batches = b24.ScheduledBatchBuilder(lookup, labels, image_root, seed, n)
    evaluation_started = time.perf_counter()
    reference = protection_scores(model, protection, image_root)
    protection_seconds = time.perf_counter() - evaluation_started
    decisions: list[dict[str, object]] = []
    training_seconds = 0.0
    for index, entries in enumerate(schedule):
        snapshot = snapshot_training_state(model, optimizer)
        step_started = time.perf_counter()
        torch.manual_seed(b24.b23.step_seed(seed, n, index + 1))
        images, targets = batches.batch(entries)
        model.train()
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(images), targets)
        loss.backward()
        optimizer.step()
        training_seconds += time.perf_counter() - step_started
        check_started = time.perf_counter()
        candidate = protection_scores(model, protection, image_root)
        protection_seconds += time.perf_counter() - check_started
        accepted = accept_block(reference, candidate, target)
        if not accepted:
            restore_training_state(model, optimizer, snapshot)
            if not nested_equal(model.state_dict(), snapshot[0]) or not nested_equal(optimizer.state_dict(), snapshot[1]):
                raise RuntimeError("rejected block rollback is not bitwise exact")
        decisions.append({
            "block": index + 1, "accepted": accepted, "loss": float(loss.detach()),
            **{f"S_ref_{d}": reference[d] for d in DOMAINS},
            **{f"S_candidate_{d}": candidate[d] for d in DOMAINS},
        })
    return model, {
        "reference_scores": reference, "block_decisions": decisions,
        "accepted_blocks": sum(bool(x["accepted"]) for x in decisions),
        "rejected_blocks": sum(not bool(x["accepted"]) for x in decisions),
        "candidate_training_time": training_seconds,
        "protection_evaluation_time": protection_seconds,
        "total_time": training_seconds + protection_seconds,
    }


def load_context(args: argparse.Namespace):
    require_cpu(args.device)
    protection_manifest = build_protection_manifest(args.manifest, args.b23_output, args.b24_output)
    parent_manifest = json.loads((args.b23_output / "run_manifest.json").read_text())
    b24_manifest = json.loads((args.b24_output / "run_manifest.json").read_text())
    frame = pd.read_csv(args.manifest)
    lookup = frame.set_index("sample_id", drop=False)
    config = json.loads(b24.b23.CONFIG_PATH.read_text())
    return protection_manifest, parent_manifest, b24_manifest, frame, lookup, config


def case_inputs(seed: int, domain: str, n: int, parent_manifest, b24_manifest, lookup):
    spec = next(x for x in b24.plan_cases() if x.seed == seed and x.domain == domain and x.n == n)
    f0, f0_record = b24.parent_checkpoint(parent_manifest, f"F0_s{seed}")
    opportunity, opportunity_hash, _ = b24.parent_opportunity(parent_manifest, spec)
    replay_record = b24_manifest["artifacts"].get(spec.replay_id, {})
    replay_path = Path(str(replay_record.get("path", "")))
    if not replay_path.is_file() or sha256_file(replay_path) != replay_record.get("sha256"):
        raise RuntimeError(f"missing/corrupt frozen replay {spec.replay_id}")
    replay, replay_hash = b24.read_envelope(replay_path)
    _, mixed = b24.build_schedules(spec, tuple(int(x) for x in opportunity["sample_ids"]), replay)
    schedule = mixed[: b24.dose(n)[0]]
    labels = {int(row["sample_id"]): int(row["pseudo_label"]) for row in opportunity["samples"]}
    labels.update({int(row["sample_id"]): int(row["label"]) for row in replay["samples"]})
    return spec, f0, f0_record, opportunity_hash, replay_hash, schedule, labels


def protection_frame(manifest: dict[str, object], seed: int, lookup: pd.DataFrame) -> pd.DataFrame:
    ids = [int(x["sample_id"]) for x in manifest["sets"][str(seed)]["samples"]]
    frame = lookup.loc[ids].reset_index(drop=True)
    if len(frame) != PROTECTION_TOTAL or set(frame.domain) != set(DOMAINS):
        raise RuntimeError("invalid protection frame")
    return frame


def write_phase_a(output_dir: Path, protection: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(output_dir / "protection_manifest.json", protection)
    atomic_json(output_dir / "preregistration.json", preregistration(protection))
    readme = f"""# B4 Protected Portfolio Development

Status: **IMPLEMENTED — FULL RUN NOT EXECUTED**.

- Device: CPU only.
- TEST status: `{TEST_STATUS}`.
- Baseline: frozen B2.4 REP, reused without retraining.
- PREP: one candidate block per B2.4 REP optimizer step; zero-tolerance
  protection against the fixed F0 reference.
- Protection set: {PROTECTION_PER_DOMAIN} F0-training examples per domain
  ({PROTECTION_PER_CLASS} per class), {PROTECTION_TOTAL} per seed, chosen by
  deterministic SHA-256 ordering.
- Rejected blocks restore model and optimizer exactly, advance the scheduled
  RNG stream, and are not retried.

The future full run requires explicit `--run-full`; default execution is a
training-free dry run. Restart reuses only hash-valid completed PREP fits.
"""
    (output_dir / "README.md").write_text(readme)


def dry_run(args: argparse.Namespace) -> dict[str, object]:
    protection, parent, b24_manifest, _, lookup, _ = load_context(args)
    write_phase_a(args.output_dir, protection)
    for spec in b24.plan_cases():
        _, f0, f0_record, opportunity_hash, replay_hash, schedule, _ = case_inputs(
            spec.seed, spec.domain, spec.n, parent, b24_manifest, lookup
        )
        if f0_record["sha256"] != protection["sets"][str(spec.seed)]["parent_f0_sha256"]:
            raise RuntimeError("protection/F0 parent mismatch")
        rep_record = b24_manifest["artifacts"].get(spec.rep_id, {})
        if rep_record.get("opportunity_sha256") != opportunity_hash or rep_record.get("replay_sha256") != replay_hash:
            raise RuntimeError("B2.4 REP provenance mismatch")
        if len(schedule) != b24.dose(spec.n)[0]:
            raise RuntimeError("PREP/REP block-count mismatch")
        protection_ids = {int(x["sample_id"]) for x in protection["sets"][str(spec.seed)]["samples"]}
        opportunity_ids = {
            int(entry["sample_id"])
            for batch in schedule for entry in batch
            if str(entry["role"]).startswith("opportunity")
        }
        if protection_ids & opportunity_ids:
            raise RuntimeError("protection set overlaps current opportunity")
        del f0
    result = {
        "technical_status": "PASS", "fits_planned": TOTAL_FITS,
        "validation_evaluations_planned": TOTAL_VALIDATION_EVALUATIONS,
        "candidate_blocks": TOTAL_CANDIDATE_BLOCKS,
        "blocks_by_N": {str(n): b24.dose(n)[0] for n in N_VALUES},
        "protection_examples_per_domain": PROTECTION_PER_DOMAIN,
        "protection_examples_per_seed": PROTECTION_TOTAL,
        "TEST_STATUS": TEST_STATUS, "training_performed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def smoke_case(args: argparse.Namespace) -> dict[str, object]:
    protection, parent, b24_manifest, _, lookup, config = load_context(args)
    spec, f0, _, _, _, schedule, labels = case_inputs(0, "photo", 25, parent, b24_manifest, lookup)
    selected = protection_frame(protection, 0, lookup)
    started = time.perf_counter()
    model, metrics = train_prep(
        f0["model_state"], schedule, labels, lookup, selected, args.image_root,
        spec.seed, spec.n, spec.domain, config,
    )
    result = {
        "technical_only": True, "excluded_from_B4": True,
        "seed": 0, "domain": "photo", "N": 25, "blocks": len(schedule),
        "accepted_blocks": metrics["accepted_blocks"], "rejected_blocks": metrics["rejected_blocks"],
        "candidate_training_time": metrics["candidate_training_time"],
        "protection_evaluation_time": metrics["protection_evaluation_time"],
        "wall_seconds": time.perf_counter() - started, "TEST_STATUS": TEST_STATUS,
    }
    args.smoke_output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.smoke_output, result)
    del model
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def run_full(args: argparse.Namespace) -> None:
    protection, parent, b24_manifest, _, lookup, config = load_context(args)
    write_phase_a(args.output_dir, protection)
    cache = args.output_dir / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.json"
    preregistration_hash = sha256_json(preregistration(protection))
    progress = json.loads(progress_path.read_text()) if progress_path.is_file() else {
        "header": {
            "protocol_id": PROTOCOL_ID,
            "protection_manifest_sha256": protection["manifest_sha256"],
            "preregistration_sha256": preregistration_hash,
            "TEST_STATUS": TEST_STATUS,
        },
        "fits": {},
    }
    if (
        progress["header"].get("protection_manifest_sha256") != protection["manifest_sha256"]
        or progress["header"].get("preregistration_sha256") != preregistration_hash
    ):
        raise RuntimeError("restart preregistration/protection mismatch")
    timing = ExperimentTimingLogger(
        "B4 Protected Portfolio Development", TOTAL_FITS, {"PREP": TOTAL_FITS},
        state_path=cache / "experiment_timing.json", resume=True, persist=True,
    )
    timing.header(["Device: CPU", f"TEST: {TEST_STATUS}", "Fits: 60 PREP", "VALIDATION evaluations: 60"])
    decisions: list[dict[str, object]] = []
    for spec in b24.plan_cases():
        artifact_id = f"PREP_s{spec.seed}_{spec.domain}_n{spec.n}"
        _, f0, f0_record, opportunity_hash, replay_hash, schedule, labels = case_inputs(
            spec.seed, spec.domain, spec.n, parent, b24_manifest, lookup
        )
        expected = {
            "parent_f0_sha256": f0_record["sha256"],
            "opportunity_sha256": opportunity_hash,
            "replay_sha256": replay_hash,
            "schedule_sha256": sha256_json(schedule),
            "protection_manifest_sha256": protection["manifest_sha256"],
            "protection_set_sha256": protection["sets"][str(spec.seed)]["sample_ids_sha256"],
        }
        prior = progress["fits"].get(artifact_id, {})
        path = cache / "states" / f"{artifact_id}.pt"
        if prior.get("status") == "complete" and path.is_file() and sha256_file(path) == prior.get("sha256"):
            payload = b24.b23.load_checkpoint(path)
            if all(payload.get(key) == value for key, value in expected.items()):
                timing.adopt_completed(artifact_id, "PREP", float(payload["timing"]["total_time"]), artifact_id)
                decisions.extend(payload["block_decisions"])
                continue
        selected = protection_frame(protection, spec.seed, lookup)
        description = f"seed={spec.seed} domain={spec.domain} N={spec.n}"
        timing.start_item(artifact_id, "PREP", spec.number, description)
        model, metrics = train_prep(
            f0["model_state"], schedule, labels, lookup, selected, args.image_root,
            spec.seed, spec.n, spec.domain, config,
        )
        validation_ids = tuple(
            int(x) for x in pd.read_csv(args.b23_output / "split_manifest.csv").loc[
                lambda x: (x.seed == spec.seed) & (x.role == "VALIDATION"), "sample_id"
            ]
        )
        validation = lookup.loc[list(validation_ids)].reset_index(drop=True)
        scores = b24.score_model(model, validation, args.image_root)
        payload = {
            "artifact_type": "PREP", "seed": spec.seed, "domain": spec.domain, "N": spec.n,
            "model_state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
            "model_fingerprint": b24.b23.state_dict_fingerprint(model), "scores": scores,
            **expected,
            "steps": len(schedule), "epsilon_local": 0.0, "epsilon_cross": 0.0,
            "accepted_blocks": metrics["accepted_blocks"], "rejected_blocks": metrics["rejected_blocks"],
            "block_decisions": [{"seed": spec.seed, "domain": spec.domain, "N": spec.n, **row} for row in metrics["block_decisions"]],
            "timing": {k: metrics[k] for k in ("candidate_training_time", "protection_evaluation_time", "total_time")},
            "evaluation_split": "validation", "validation_ids_sha256": sha256_json(list(validation_ids)),
            "TEST_STATUS": TEST_STATUS,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        b24.save_checkpoint(path, payload)
        progress["fits"][artifact_id] = {
            "status": "complete", "path": str(path.resolve()), "sha256": sha256_file(path),
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        atomic_json(progress_path, progress)
        decisions.extend(payload["block_decisions"])
        timing.finish_item(description=description)
        del model
    b24.atomic_csv(args.output_dir / "block_decisions.csv", pd.DataFrame(decisions))
    analysis = _load_module("b4_analysis", ANALYZE_PATH)
    analysis.run_analysis(args.output_dir, args.b23_output, args.b24_output)
    atomic_json(args.output_dir / "COMPLETE.json", {"status": "complete", "fits": 60, "TEST_STATUS": TEST_STATUS})
    timing.finish(title="B4 COMPLETE", extra_lines=[f"TEST: {TEST_STATUS}", "Fits: 60/60"])


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--smoke-case", action="store_true")
    mode.add_argument("--run-full", action="store_true")
    parser.add_argument("--device", choices=("cpu",), default="cpu")
    parser.add_argument("--image-root", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--b23-output", type=Path, default=DEFAULT_B23_OUTPUT)
    parser.add_argument("--b24-output", type=Path, default=DEFAULT_B24_OUTPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--smoke-output", type=Path, default=Path("/tmp/b4_protected_development_smoke.json"))
    args = parser.parse_args(argv)
    if (args.smoke_case or args.run_full) and (args.image_root is None or not args.image_root.is_dir()):
        parser.error("--image-root is required for smoke/full execution")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.run_full:
        run_full(args)
    elif args.smoke_case:
        smoke_case(args)
    else:
        dry_run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
