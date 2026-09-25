"""B5 Gradient-Protected Development (GREP), CPU and VALIDATION only.

The default mode is a training-free dry run.  The 60-fit scientific execution
requires the explicit ``--run-full`` flag.  Phase A may run only the fixed
``--smoke-case`` seed=0/domain=photo/N=25 outside scientific results.
"""

from __future__ import annotations

import argparse
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
DEFAULT_OUTPUT = ROOT / "results/foundations/b5_gradient_protected"

PROTOCOL_ID = "B5-PACS-gradient-protected-v1"
TEST_STATUS = "PREVIOUSLY_OPENED_NOT_USED_IN_B5"
SEEDS = (0, 1, 2, 3, 4)
DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
N_VALUES = (25, 50, 100)
COSTS = (0.0, 0.02, 0.05, 0.10, 0.15)
HORIZONS = (1, 2, 5, 10)
PROJECTION_EPS = 1e-12
PROJECTION_TOLERANCE = 1e-7
TOTAL_FITS = 60
TOTAL_VALIDATION_EVALUATIONS = 60
TOTAL_STEPS = sum(20 * (3 * int(np.ceil(n / 16))) for n in N_VALUES)


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


b24 = _load_module("b5_b24_run", B24_RUN_PATH)


def sha256_file(path: Path) -> str:
    return b24.sha256_file(path)


def sha256_json(value: object) -> str:
    return b24.sha256_json(value)


def atomic_json(path: Path, value: object) -> None:
    b24.atomic_json(path, value)


def require_cpu(device: str) -> None:
    if device != "cpu":
        raise ValueError("B5 is CPU-only; MPS/CUDA are prohibited")


def audit_parent_artifacts(b23_output: Path, b24_output: Path) -> dict[str, object]:
    analyzer = _load_module("b5_b24_analysis", B24_ANALYZE_PATH)
    _, audit = analyzer.compatibility_audit(b24_output, b23_output)
    if audit.get("compatible") is not True or audit.get("test") != "CLOSED":
        raise RuntimeError("B2.4 parent compatibility failed")
    b23_manifest = json.loads((b23_output / "run_manifest.json").read_text())
    b24_manifest = json.loads((b24_output / "run_manifest.json").read_text())
    found = 0
    for spec in b24.plan_cases():
        for artifact_id, manifest, expected_type in (
            (f"F0_s{spec.seed}", b23_manifest, "F0"),
            (f"op_s{spec.seed}_{spec.domain}_n{spec.n}", b23_manifest, "opportunity"),
            (spec.replay_id, b24_manifest, "replay"),
            (spec.rep_id, b24_manifest, "REP"),
        ):
            record = manifest["artifacts"].get(artifact_id, {})
            path = Path(str(record.get("path", "")))
            if record.get("artifact_type") != expected_type or record.get("status") != "complete" or not path.is_file() or sha256_file(path) != record.get("sha256"):
                raise RuntimeError(f"missing/corrupt parent artifact {artifact_id}")
        found += 1
    return {
        "families": found, "provenance": "PASS",
        "b23_manifest_sha256": sha256_file(b23_output / "run_manifest.json"),
        "b24_manifest_sha256": sha256_file(b24_output / "run_manifest.json"),
    }


def preregistration(parent_audit: dict[str, object]) -> dict[str, object]:
    return {
        "protocol_id": PROTOCOL_ID, "status": "FROZEN_BEFORE_FULL_RUN",
        "TEST_STATUS": TEST_STATUS, "device": "cpu",
        "implementation_sha256": sha256_file(Path(__file__)),
        "analysis_sha256": sha256_file(ANALYZE_PATH),
        "parent_audit": parent_audit,
        "seeds": list(SEEDS), "domains": list(DOMAINS), "N": list(N_VALUES),
        "c": list(COSTS), "h": list(HORIZONS),
        "baseline": "frozen B2.4 REP reused without retraining",
        "method": "GREP",
        "steps_by_N": {str(n): b24.dose(n)[0] for n in N_VALUES},
        "total_steps": TOTAL_STEPS,
        "batch": "exact B2.4 REP: 8 opportunity + 8 replay",
        "optimizer": "SGD, same B2.4 learning rate/momentum/weight decay",
        "gradient_rule": "if dot>=0: g=g_opp+g_mem; else g=g_opp-(dot/(norm_mem_sq+1e-12))*g_mem+g_mem",
        "projection_eps": PROJECTION_EPS,
        "projection_tolerance": PROJECTION_TOLERANCE,
        "criteria": {
            "A_cross": "mean GREP cross_change >=0 in >=4/5 seeds",
            "B_local": "mean GREP local_change >=0 in >=4/5 seeds",
            "C_value": "at least one domain x N has DeltaV_GREP(c)>0 in >=4/5 seeds for every c",
            "D_integration": "at least one c x h cell has kappa_star>0 in >=4/5 seeds",
            "POSITIVE": "A_cross AND B_local AND C_value AND D_integration",
            "NULL": "C_value false AND D_integration false AND GREP does not improve mean cross_change versus REP in >=4/5 seeds",
            "INCONCLUSIVE": "all other valid outcomes",
        },
        "training_performed_in_phase_A_outputs": False,
    }


def write_phase_a(output_dir: Path, prereg: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(output_dir / "preregistration.json", prereg)
    (output_dir / "README.md").write_text(
        "# B5 Gradient-Protected Development\n\n"
        "Status: **IMPLEMENTED — FULL RUN NOT EXECUTED**.\n\n"
        f"TEST status: `{TEST_STATUS}`. GREP uses exactly the frozen B2.4 F0, "
        "opportunity, replay, schedule and optimizer. VALIDATION is evaluated "
        "once after each completed fit and never participates in training. "
        "The default command is a training-free dry run; `--run-full` is explicit.\n"
    )


def project_gradients(
    grad_opp: tuple[torch.Tensor, ...], grad_mem: tuple[torch.Tensor, ...]
) -> tuple[tuple[torch.Tensor, ...], dict[str, float | bool]]:
    if len(grad_opp) != len(grad_mem):
        raise ValueError("gradient tuples differ")
    dot = sum((go.double() * gm.double()).sum() for go, gm in zip(grad_opp, grad_mem, strict=True))
    norm_opp_sq = sum((go.double() ** 2).sum() for go in grad_opp)
    norm_mem_sq = sum((gm.double() ** 2).sum() for gm in grad_mem)
    projected = bool(dot.item() < 0)
    if projected:
        coefficient = dot / (norm_mem_sq + PROJECTION_EPS)
        opp_projected = tuple(go - coefficient.to(go.dtype) * gm for go, gm in zip(grad_opp, grad_mem, strict=True))
    else:
        opp_projected = tuple(go.clone() for go in grad_opp)
    dot_after = sum((gp.double() * gm.double()).sum() for gp, gm in zip(opp_projected, grad_mem, strict=True))
    norm_projected_sq = sum((gp.double() ** 2).sum() for gp in opp_projected)
    if projected and dot_after.item() < -PROJECTION_TOLERANCE:
        raise RuntimeError(f"projected gradient constraint failed: {dot_after.item()}")
    combined = tuple(gp + gm for gp, gm in zip(opp_projected, grad_mem, strict=True))
    return combined, {
        "dot_before": float(dot), "dot_after": float(dot_after),
        "norm_opp": float(torch.sqrt(norm_opp_sq)),
        "norm_mem": float(torch.sqrt(norm_mem_sq)),
        "norm_opp_projected": float(torch.sqrt(norm_projected_sq)),
        "projected": projected,
    }


def train_grep(
    f0_state: dict[str, torch.Tensor], schedule: list[list[dict[str, object]]],
    labels: dict[int, int], lookup: pd.DataFrame, image_root: Path,
    seed: int, n: int, domain: str, config: dict[str, object],
) -> tuple[nn.Module, dict[str, object]]:
    training_seed = b24.b23.derived_training_seed(seed, n)
    b24.seed_everything(training_seed)
    model = b24.b23.b20.make_model("fast", training_seed, torch.device("cpu"), pretrained=False)
    model.load_state_dict(f0_state)
    if b24.b23.state_dict_fingerprint(model) != b24.b23.state_dict_fingerprint(f0_state):
        raise RuntimeError("loaded GREP starting state differs from frozen F0")
    parameters = tuple(parameter for parameter in model.parameters() if parameter.requires_grad)
    optimizer = torch.optim.SGD(
        parameters, lr=float(config["fast"]["learning_rate"]),
        momentum=float(config["fast"]["momentum"]), weight_decay=0,
    )
    batches = b24.ScheduledBatchBuilder(lookup, labels, image_root, seed, n)
    step_rows = []
    started = time.perf_counter()
    for index, entries in enumerate(schedule):
        opportunity_positions = [i for i, entry in enumerate(entries) if entry["role"] == "opportunity"]
        memory_positions = [i for i, entry in enumerate(entries) if entry["role"] == "replay"]
        if len(opportunity_positions) != 8 or len(memory_positions) != 8:
            raise RuntimeError("GREP requires exact 8 opportunity + 8 replay batches")
        torch.manual_seed(b24.b23.step_seed(seed, n, index + 1))
        images, targets = batches.batch(entries)
        model.train()
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss_opp = nn.functional.cross_entropy(logits[opportunity_positions], targets[opportunity_positions])
        loss_mem = nn.functional.cross_entropy(logits[memory_positions], targets[memory_positions])
        grad_opp = torch.autograd.grad(loss_opp, parameters, retain_graph=True)
        grad_mem = torch.autograd.grad(loss_mem, parameters)
        combined, mechanism = project_gradients(grad_opp, grad_mem)
        for parameter, gradient in zip(parameters, combined, strict=True):
            parameter.grad = gradient.detach().clone()
        optimizer.step()
        step_rows.append({
            "seed": seed, "domain": domain, "N": n, "step": index + 1,
            "loss_opp": float(loss_opp.detach()), "loss_mem": float(loss_mem.detach()),
            **mechanism,
        })
    elapsed = time.perf_counter() - started
    projected_steps = sum(bool(row["projected"]) for row in step_rows)
    return model, {
        "steps": step_rows, "projected_steps": projected_steps,
        "total_steps": len(step_rows), "projection_rate": projected_steps / len(step_rows),
        "training_time": elapsed,
    }


def load_context(args: argparse.Namespace):
    require_cpu(args.device)
    parent_audit = audit_parent_artifacts(args.b23_output, args.b24_output)
    prereg = preregistration(parent_audit)
    parent = json.loads((args.b23_output / "run_manifest.json").read_text())
    b24_manifest = json.loads((args.b24_output / "run_manifest.json").read_text())
    frame = pd.read_csv(args.manifest)
    lookup = frame.set_index("sample_id", drop=False)
    config = json.loads(b24.b23.CONFIG_PATH.read_text())
    return prereg, parent, b24_manifest, lookup, config


def case_inputs(seed: int, domain: str, n: int, parent, b24_manifest, lookup):
    spec = next(x for x in b24.plan_cases() if x.seed == seed and x.domain == domain and x.n == n)
    f0, f0_record = b24.parent_checkpoint(parent, f"F0_s{seed}")
    opportunity, opportunity_hash, _ = b24.parent_opportunity(parent, spec)
    replay_record = b24_manifest["artifacts"].get(spec.replay_id, {})
    replay_path = Path(str(replay_record.get("path", "")))
    if not replay_path.is_file() or sha256_file(replay_path) != replay_record.get("sha256"):
        raise RuntimeError(f"missing/corrupt replay {spec.replay_id}")
    replay, replay_hash = b24.read_envelope(replay_path)
    _, mixed = b24.build_schedules(spec, tuple(int(x) for x in opportunity["sample_ids"]), replay)
    schedule = mixed[: b24.dose(n)[0]]
    rep_record = b24_manifest["artifacts"].get(spec.rep_id, {})
    if (
        rep_record.get("parent_f0_sha256") != f0_record["sha256"]
        or rep_record.get("opportunity_sha256") != opportunity_hash
        or rep_record.get("replay_sha256") != replay_hash
    ):
        raise RuntimeError("REP/GREP parent provenance differs")
    labels = {int(row["sample_id"]): int(row["pseudo_label"]) for row in opportunity["samples"]}
    labels.update({int(row["sample_id"]): int(row["label"]) for row in replay["samples"]})
    return spec, f0, f0_record, opportunity_hash, replay_hash, schedule, labels


def dry_run(args: argparse.Namespace) -> dict[str, object]:
    prereg, parent, b24_manifest, lookup, _ = load_context(args)
    write_phase_a(args.output_dir, prereg)
    for spec in b24.plan_cases():
        _, _, _, _, _, schedule, _ = case_inputs(spec.seed, spec.domain, spec.n, parent, b24_manifest, lookup)
        if len(schedule) != b24.dose(spec.n)[0]:
            raise RuntimeError("GREP/REP step count mismatch")
        if any(
            sum(entry["role"] == "opportunity" for entry in batch) != 8
            or sum(entry["role"] == "replay" for entry in batch) != 8
            for batch in schedule
        ):
            raise RuntimeError("GREP/REP batch composition mismatch")
    result = {
        "technical_status": "PASS", "fits_planned": 60,
        "validation_evaluations_planned": 60, "steps_planned": TOTAL_STEPS,
        "steps_by_N": {str(n): b24.dose(n)[0] for n in N_VALUES},
        "TEST_STATUS": TEST_STATUS, "training_performed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def smoke_case(args: argparse.Namespace) -> dict[str, object]:
    _, parent, b24_manifest, lookup, config = load_context(args)
    spec, f0, _, _, _, schedule, labels = case_inputs(0, "photo", 25, parent, b24_manifest, lookup)
    model, metrics = train_grep(
        f0["model_state"], schedule, labels, lookup, args.image_root,
        spec.seed, spec.n, spec.domain, config,
    )
    projected = [row for row in metrics["steps"] if row["projected"]]
    result = {
        "technical_only": True, "excluded_from_B5": True,
        "seed": 0, "domain": "photo", "N": 25,
        "total_steps": metrics["total_steps"], "projected_steps": metrics["projected_steps"],
        "projection_rate": metrics["projection_rate"],
        "min_dot_before": min(row["dot_before"] for row in metrics["steps"]),
        "min_dot_after_projected": min((row["dot_after"] for row in projected), default=None),
        "training_time": metrics["training_time"], "TEST_STATUS": TEST_STATUS,
        "steps": metrics["steps"],
    }
    args.smoke_output.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(args.smoke_output, result)
    del model
    print(json.dumps({key: value for key, value in result.items() if key != "steps"}, indent=2, sort_keys=True), flush=True)
    return result


def run_full(args: argparse.Namespace) -> None:
    prereg, parent, b24_manifest, lookup, config = load_context(args)
    write_phase_a(args.output_dir, prereg)
    cache = args.output_dir / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.json"
    prereg_hash = sha256_json(prereg)
    progress = json.loads(progress_path.read_text()) if progress_path.is_file() else {
        "header": {"protocol_id": PROTOCOL_ID, "preregistration_sha256": prereg_hash, "TEST_STATUS": TEST_STATUS},
        "fits": {},
    }
    if progress["header"].get("preregistration_sha256") != prereg_hash:
        raise RuntimeError("restart preregistration mismatch")
    timing = ExperimentTimingLogger(
        "B5 Gradient-Protected Development", TOTAL_FITS, {"GREP": TOTAL_FITS},
        state_path=cache / "experiment_timing.json", resume=True, persist=True,
    )
    timing.header(["Device: CPU", f"TEST: {TEST_STATUS}", "Fits: 60 GREP", "VALIDATION evaluations: 60"])
    step_rows = []
    split = pd.read_csv(args.b23_output / "split_manifest.csv")
    for spec in b24.plan_cases():
        artifact_id = f"GREP_s{spec.seed}_{spec.domain}_n{spec.n}"
        _, f0, f0_record, opportunity_hash, replay_hash, schedule, labels = case_inputs(
            spec.seed, spec.domain, spec.n, parent, b24_manifest, lookup
        )
        expected = {
            "parent_f0_sha256": f0_record["sha256"], "opportunity_sha256": opportunity_hash,
            "replay_sha256": replay_hash, "schedule_sha256": sha256_json(schedule),
            "preregistration_sha256": prereg_hash,
        }
        path = cache / "states" / f"{artifact_id}.pt"
        prior = progress["fits"].get(artifact_id, {})
        if prior.get("status") == "complete" and path.is_file() and sha256_file(path) == prior.get("sha256"):
            payload = b24.b23.load_checkpoint(path)
            if all(payload.get(key) == value for key, value in expected.items()):
                timing.adopt_completed(artifact_id, "GREP", float(payload["training_time"]), artifact_id)
                step_rows.extend(payload["step_metrics"])
                continue
        description = f"seed={spec.seed} domain={spec.domain} N={spec.n}"
        timing.start_item(artifact_id, "GREP", spec.number, description)
        model, metrics = train_grep(
            f0["model_state"], schedule, labels, lookup, args.image_root,
            spec.seed, spec.n, spec.domain, config,
        )
        validation_ids = tuple(int(x) for x in split.loc[(split.seed == spec.seed) & (split.role == "VALIDATION"), "sample_id"])
        validation = lookup.loc[list(validation_ids)].reset_index(drop=True)
        scores = b24.score_model(model, validation, args.image_root)
        payload = {
            "artifact_type": "GREP", "seed": spec.seed, "domain": spec.domain, "N": spec.n,
            "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()},
            "model_fingerprint": b24.b23.state_dict_fingerprint(model), "scores": scores,
            **expected, "steps": metrics["total_steps"], "projected_steps": metrics["projected_steps"],
            "projection_rate": metrics["projection_rate"], "training_time": metrics["training_time"],
            "step_metrics": metrics["steps"], "evaluation_split": "validation",
            "validation_ids_sha256": sha256_json(list(validation_ids)), "TEST_STATUS": TEST_STATUS,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        b24.save_checkpoint(path, payload)
        progress["fits"][artifact_id] = {
            "status": "complete", "path": str(path.resolve()), "sha256": sha256_file(path),
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        atomic_json(progress_path, progress)
        step_rows.extend(metrics["steps"])
        timing.finish_item(description=description)
        del model
    b24.atomic_csv(args.output_dir / "gradient_steps.csv", pd.DataFrame(step_rows))
    analyzer = _load_module("b5_analysis", ANALYZE_PATH)
    analyzer.run_analysis(args.output_dir, args.b23_output, args.b24_output)
    atomic_json(args.output_dir / "COMPLETE.json", {"status": "complete", "fits": 60, "TEST_STATUS": TEST_STATUS})
    timing.finish(title="B5 COMPLETE", extra_lines=[f"TEST: {TEST_STATUS}", "Fits: 60/60"])


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
    parser.add_argument("--smoke-output", type=Path, default=Path("/tmp/b5_gradient_protected_smoke.json"))
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
