"""Run the frozen CPU-only PACS B2.3 portfolio-opportunity experiment.

Scientific authority: docs/experimental_foundations/B23_PROTOCOL.md.
Dry-run and analyze-only never train models or query the teacher.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import importlib.util
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch
import torchvision
from PIL import Image
from torch import nn
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = ROOT / "docs/experimental_foundations/B23_PROTOCOL.md"
CONFIG_PATH = ROOT / "experiments/pilots/b2_pacs_calibration/config.json"
B20_PATH = ROOT / "experiments/pilots/b2_pacs_calibration/run.py"
B20_LIBRARY_PATH = ROOT / "src/hls/b2_pacs_calibration.py"
ANALYZE_PATH = Path(__file__).with_name("analyze.py")
DEFAULT_MANIFEST = ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv"
DEFAULT_OUTPUT = ROOT / "results/pilots/b23_portfolio_opportunity"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b20 = _load_module("b23_b20", B20_PATH)

PROTOCOL_ID = "B2.3-PACS-portfolio-v2"
DATASET_REVISION = "394113073258ead631f617d2e13bb377c0715c4b"
DATASET_FILE = "data/train-00000-of-00001.parquet"
DATASET_SHA256 = "4fc041ee92eec6043fe6e2859e8bdd138e5f958bc621afd153879812cbe65ff5"
DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
SEEDS = (0, 1, 2, 3, 4)
N_VALUES = (25, 50, 100)
COSTS = (0.00, 0.02, 0.05, 0.10, 0.15)
FUTURE_WEIGHTS = (1, 2, 5, 10)
KAPPA = 0.0
BATCH_SIZE = 16
JOINT_PER_DOMAIN = 8
F0_FRACTION = 0.25
TOTAL_BASE_FITS = 10
TOTAL_OPPORTUNITIES = 60
TOTAL_SINGLETON_FITS = 60
TOTAL_JOINT_FITS = 90
TOTAL_FITS = 160
TOTAL_EVALUATIONS = 250
TOTAL_PRIMARY_ROWS = 1800
TOTAL_DOSE_ROWS = 450
NUMERIC_TOLERANCE = 1e-12


@dataclass(frozen=True)
class DevelopmentSplits:
    """Only scientifically visible split roles; TEST has no API surface."""

    base: tuple[int, ...]
    transfer: tuple[int, ...]
    validation: tuple[int, ...]


@dataclass(frozen=True)
class OpportunitySpec:
    seed: int
    domain: str
    n: int
    sample_ids: tuple[int, ...]

    @property
    def artifact_id(self) -> str:
        return f"op_s{self.seed}_{self.domain}_n{self.n}"


@dataclass(frozen=True)
class SingletonSpec:
    number: int
    seed: int
    domain: str
    n: int

    @property
    def artifact_id(self) -> str:
        return f"Fi_s{self.seed}_{self.domain}_n{self.n}"


@dataclass(frozen=True)
class JointSpec:
    number: int
    seed: int
    n: int
    domain_i: str
    domain_j: str

    @property
    def pair(self) -> str:
        return f"{self.domain_i}__{self.domain_j}"

    @property
    def artifact_id(self) -> str:
        return f"Fij_s{self.seed}_{self.pair}_n{self.n}"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_torch_object(value: object) -> str:
    buffer = io.BytesIO()
    torch.save(value, buffer)
    return sha256_bytes(buffer.getvalue())


def state_dict_fingerprint(state_or_model: object) -> str:
    state = state_or_model.state_dict() if hasattr(state_or_model, "state_dict") else state_or_model
    digest = hashlib.sha256()
    for key in sorted(state):
        tensor = state[key].detach().cpu().contiguous()
        digest.update(key.encode("utf-8"))
        digest.update(str(tensor.dtype).encode("utf-8"))
        digest.update(str(tuple(tensor.shape)).encode("utf-8"))
        digest.update(tensor.numpy().tobytes())
    return digest.hexdigest()


def seed64(*parts: object) -> int:
    payload = PROTOCOL_ID + "|" + "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big") & ((1 << 63) - 1)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def require_cpu(requested: str) -> torch.device:
    if requested != "cpu":
        raise ValueError(f"B2.3 is CPU ONLY; requested device={requested!r}")
    return torch.device("cpu")


def dose(n: int) -> tuple[int, int]:
    if n not in N_VALUES:
        raise ValueError(f"unregistered N={n}")
    steps = 3 * math.ceil(n / BATCH_SIZE)
    return steps, BATCH_SIZE * steps


def domain_pairs() -> tuple[tuple[str, str], ...]:
    return tuple((left, right) for index, left in enumerate(DOMAINS) for right in DOMAINS[index + 1 :])


def plan_specs() -> tuple[list[SingletonSpec], list[JointSpec]]:
    singletons: list[SingletonSpec] = []
    joints: list[JointSpec] = []
    for seed in SEEDS:
        for n in N_VALUES:
            for domain in DOMAINS:
                singletons.append(SingletonSpec(len(singletons) + 1, seed, domain, n))
            for domain_i, domain_j in domain_pairs():
                joints.append(JointSpec(len(joints) + 1, seed, n, domain_i, domain_j))
    return singletons, joints


def validate_counts() -> None:
    singletons, joints = plan_specs()
    checks = {
        "seeds": len(SEEDS) == 5,
        "domains": len(DOMAINS) == 4,
        "N": N_VALUES == (25, 50, 100),
        "pairs": len(domain_pairs()) == 6,
        "opportunities": len(SEEDS) * len(DOMAINS) * len(N_VALUES) == TOTAL_OPPORTUNITIES,
        "singletons": len(singletons) == TOTAL_SINGLETON_FITS,
        "joints": len(joints) == TOTAL_JOINT_FITS,
        "fits": TOTAL_BASE_FITS + len(singletons) + len(joints) == TOTAL_FITS,
        "primary": len(joints) * len(COSTS) * len(FUTURE_WEIGHTS) == TOTAL_PRIMARY_ROWS,
        "dose": len(joints) * len(COSTS) == TOTAL_DOSE_ROWS,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"frozen design count mismatch: {failed}")


def validate_config(config: dict) -> None:
    expected = {
        "dataset_revision": DATASET_REVISION,
        "dataset_file": DATASET_FILE,
        "dataset_file_sha256": DATASET_SHA256,
        "split_seeds": list(SEEDS),
        "competence_domains": list(DOMAINS),
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise RuntimeError(f"B2.0 config drift for {key}")
    training = config["training"]
    if (training["epochs"], training["batch_size"], training["workers"]) != (3, 16, 0):
        raise RuntimeError("training configuration drift")
    for kind, lr in (("fast", 0.001), ("deep", 0.0001)):
        section = config[kind]
        if section["optimizer"] != "SGD" or float(section["learning_rate"]) != lr or float(section["momentum"]) != 0.9:
            raise RuntimeError(f"{kind} optimizer configuration drift")


def development_splits(frame: pd.DataFrame, seed: int) -> DevelopmentSplits:
    split_map = b20.stratified_splits(frame, seed)
    return DevelopmentSplits(
        tuple(int(value) for value in split_map["base"]),
        tuple(int(value) for value in split_map["transfer"]),
        tuple(int(value) for value in split_map["validation"]),
    )


def opportunity_order(transfer: pd.DataFrame, seed: int, domain: str) -> tuple[int, ...]:
    eligible = [int(value) for value in transfer.loc[transfer.domain == domain, "sample_id"]]
    if len(eligible) < 100:
        raise RuntimeError(f"seed={seed} domain={domain} has fewer than 100 TRANSFER examples")
    ordered = sorted(
        eligible,
        key=lambda sample_id: hashlib.sha256(
            f"{PROTOCOL_ID}|opportunity|{seed}|{domain}|{sample_id}".encode("utf-8")
        ).digest(),
    )
    return tuple(ordered[:100])


def build_opportunity_plan(frame: pd.DataFrame, splits: dict[int, DevelopmentSplits]) -> list[OpportunitySpec]:
    lookup = frame.set_index("sample_id", drop=False)
    plan: list[OpportunitySpec] = []
    for seed in SEEDS:
        transfer = lookup.loc[list(splits[seed].transfer)].reset_index(drop=True)
        for domain in DOMAINS:
            maximum = opportunity_order(transfer, seed, domain)
            for n in N_VALUES:
                plan.append(OpportunitySpec(seed, domain, n, maximum[:n]))
    if len(plan) != TOTAL_OPPORTUNITIES:
        raise RuntimeError("opportunity plan cardinality mismatch")
    return plan


def opportunity_payload(spec: OpportunitySpec, maximum_ids: tuple[int, ...], rows: list[dict[str, object]], deep_sha256: str) -> dict[str, object]:
    if tuple(int(row["sample_id"]) for row in rows) != spec.sample_ids:
        raise RuntimeError("opportunity rows do not match immutable prefix")
    if len(rows) != spec.n or any(str(row["domain"]) != spec.domain for row in rows):
        raise RuntimeError("opportunity composition mismatch")
    return {
        "protocol_id": PROTOCOL_ID,
        "dataset_revision": DATASET_REVISION,
        "seed": spec.seed,
        "domain": spec.domain,
        "N": spec.n,
        "maximum_ids_sha256": sha256_json(list(maximum_ids)),
        "sample_ids": list(spec.sample_ids),
        "samples": rows,
        "deep_checkpoint_sha256": deep_sha256,
        "teacher_query_count": 0,
        "source_stream_teacher_query_count": 100,
        "pseudo_label_count": spec.n,
        "creation_action": "D",
        "action_gate": {
            "F": {"teacher_query_count": 0, "pseudo_label_count": 0, "student_updated": False},
            "D": {"opportunity_example_count": spec.n, "pseudo_label_count": spec.n},
        },
        "rng_seed": seed64("opportunity", spec.seed, spec.domain),
        "test_used": False,
    }


def write_envelope(path: Path, payload: dict[str, object]) -> str:
    digest = sha256_json(payload)
    atomic_json(path, {"payload": payload, "sha256": digest})
    return digest


def read_envelope(path: Path, expected: dict[str, object] | None = None) -> tuple[dict[str, object], str]:
    envelope = json.loads(path.read_text())
    payload, digest = envelope.get("payload"), envelope.get("sha256")
    if not isinstance(payload, dict) or digest != sha256_json(payload):
        raise RuntimeError(f"corrupt artifact envelope: {path}")
    if expected:
        for key, value in expected.items():
            if payload.get(key) != value:
                raise RuntimeError(f"incompatible {path.name}: {key}")
    return payload, str(digest)


def cyclic_exposures(sample_ids: tuple[int, ...], count: int, seed: int, n: int, domain: str) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    exposure_counts = {sample_id: 0 for sample_id in sample_ids}
    cycle = 0
    while len(result) < count:
        ordered = sorted(
            sample_ids,
            key=lambda sample_id: hashlib.sha256(
                f"{PROTOCOL_ID}|schedule|{seed}|{n}|{domain}|{cycle}|{sample_id}".encode("utf-8")
            ).digest(),
        )
        for sample_id in ordered:
            if len(result) == count:
                break
            exposure_counts[sample_id] += 1
            result.append({"sample_id": sample_id, "exposure": exposure_counts[sample_id]})
        cycle += 1
    return result


def singleton_schedule(seed: int, n: int, domain: str, sample_ids: tuple[int, ...]) -> list[list[dict[str, object]]]:
    steps, exposures = dose(n)
    sequence = cyclic_exposures(sample_ids, exposures, seed, n, domain)
    batches = [[{**item, "domain": domain} for item in sequence[offset : offset + BATCH_SIZE]] for offset in range(0, exposures, BATCH_SIZE)]
    if len(batches) != steps or any(len(batch) != BATCH_SIZE for batch in batches):
        raise RuntimeError("invalid singleton schedule")
    return batches


def joint_schedule(spec: JointSpec, ids_i: tuple[int, ...], ids_j: tuple[int, ...]) -> list[list[dict[str, object]]]:
    steps, exposures = dose(spec.n)
    seq_i = cyclic_exposures(ids_i, exposures, spec.seed, spec.n, spec.domain_i)
    seq_j = cyclic_exposures(ids_j, exposures, spec.seed, spec.n, spec.domain_j)
    batches: list[list[dict[str, object]]] = []
    for step in range(2 * steps):
        left = [{**item, "domain": spec.domain_i} for item in seq_i[step * 8 : (step + 1) * 8]]
        right = [{**item, "domain": spec.domain_j} for item in seq_j[step * 8 : (step + 1) * 8]]
        batches.append(left + right if step % 2 == 0 else right + left)
    if any(len(batch) != BATCH_SIZE for batch in batches):
        raise RuntimeError("invalid joint schedule")
    return batches


def schedule_audit(schedule: list[list[dict[str, object]]], n: int, domains: tuple[str, ...]) -> dict[str, object]:
    flat = [item for batch in schedule for item in batch]
    return {
        "steps": len(schedule),
        "batch_size": BATCH_SIZE,
        "total_exposures": len(flat),
        "exposures": {domain: sum(item["domain"] == domain for item in flat) for domain in domains},
        "schedule_sha256": sha256_json(schedule),
        "N": n,
    }


def augmentation_seed(seed: int, n: int, sample_id: int, exposure: int) -> int:
    return seed64("augmentation", seed, n, sample_id, exposure)


def step_seed(seed: int, n: int, step: int) -> int:
    return seed64("step", seed, n, step)


class ScheduledImages:
    def __init__(self, lookup: pd.DataFrame, labels: dict[int, int], image_root: Path, seed: int, n: int):
        self.lookup = lookup
        self.labels = labels
        self.image_root = image_root
        self.seed = seed
        self.n = n
        self.transform = transforms.Compose(
            [
                transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ToTensor(),
                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
            ]
        )

    def batch(self, entries: list[dict[str, object]]) -> tuple[torch.Tensor, torch.Tensor]:
        images: list[torch.Tensor] = []
        targets: list[int] = []
        for entry in entries:
            sample_id = int(entry["sample_id"])
            row = self.lookup.loc[sample_id]
            with Image.open(self.image_root / row.relative_path) as source:
                image = source.convert("RGB")
            with torch.random.fork_rng(devices=[]):
                torch.manual_seed(augmentation_seed(self.seed, self.n, sample_id, int(entry["exposure"])))
                images.append(self.transform(image))
            targets.append(int(self.labels[sample_id]))
        return torch.stack(images), torch.tensor(targets, dtype=torch.long)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def score_model(model: nn.Module, validation: pd.DataFrame, image_root: Path, device: torch.device) -> dict[str, float]:
    labels, predictions, domains, _ = b20.evaluate(model, validation, image_root, device, BATCH_SIZE)
    result: dict[str, float] = {}
    for domain in DOMAINS:
        mask = domains == domain
        result[domain] = float(b20.balanced_accuracy_score(labels[mask], predictions[mask]))
    return result


@torch.inference_mode()
def teacher_labels(model: nn.Module, selected: pd.DataFrame, image_root: Path, device: torch.device) -> list[int]:
    loader = torch.utils.data.DataLoader(b20.PACSImages(selected, image_root, training=False), batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    model.eval()
    output: list[int] = []
    for images, _, _, _ in loader:
        output.extend(model(images.to(device)).argmax(1).cpu().tolist())
    if len(output) != len(selected):
        raise RuntimeError("teacher query count mismatch")
    return output


def train_base(kind: str, seed: int, frame: pd.DataFrame, config: dict, image_root: Path, device: torch.device) -> tuple[nn.Module, float]:
    training_seed = seed + (2500 if kind == "fast" else 30000)
    seed_everything(training_seed)
    model = b20.make_model(kind, training_seed, device)
    params = config[kind]
    optimizer = torch.optim.SGD(model.parameters(), lr=float(params["learning_rate"]), momentum=float(params["momentum"]), weight_decay=0)
    loader = torch.utils.data.DataLoader(
        b20.PACSImages(frame, image_root, training=True), batch_size=BATCH_SIZE, shuffle=True, num_workers=0,
        generator=torch.Generator().manual_seed(training_seed),
    )
    started = time.perf_counter()
    for epoch in range(3):
        model.train()
        for images, labels, _, _ in loader:
            optimizer.zero_grad(set_to_none=True)
            loss = nn.functional.cross_entropy(model(images.to(device)), labels.to(device))
            loss.backward()
            optimizer.step()
        print(f"base {kind} seed={seed} epoch {epoch + 1}/3", flush=True)
    return model, time.perf_counter() - started


def capture_rng() -> dict[str, object]:
    return {"python": random.getstate(), "numpy": np.random.get_state(), "torch": torch.get_rng_state()}


def restore_rng(state: dict[str, object]) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])


def train_scheduled(
    f0_state: dict[str, torch.Tensor], schedule: list[list[dict[str, object]]], labels: dict[int, int], lookup: pd.DataFrame,
    image_root: Path, seed: int, n: int, config: dict, *, resume: dict[str, object] | None = None,
    midpoint_step: int | None = None, midpoint_callback: Callable[[nn.Module, torch.optim.Optimizer, dict[str, object], int], None] | None = None,
) -> tuple[nn.Module, float]:
    device = torch.device("cpu")
    training_seed = seed64("training", seed, n)
    seed_everything(training_seed)
    model = b20.make_model("fast", training_seed, device, pretrained=False)
    model.load_state_dict(f0_state)
    optimizer = torch.optim.SGD(model.parameters(), lr=float(config["fast"]["learning_rate"]), momentum=float(config["fast"]["momentum"]), weight_decay=0)
    start_step = 0
    if resume is not None:
        model.load_state_dict(resume["model_state"])
        optimizer.load_state_dict(resume["optimizer_state"])
        restore_rng(resume["rng_state"])
        start_step = int(resume["step"])
    dataset = ScheduledImages(lookup, labels, image_root, seed, n)
    started = time.perf_counter()
    model.train()
    for index in range(start_step, len(schedule)):
        torch.manual_seed(step_seed(seed, n, index + 1))
        images, targets = dataset.batch(schedule[index])
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(images), targets)
        loss.backward()
        optimizer.step()
        print(f"step {index + 1}/{len(schedule)} | loss={float(loss):.6f}", flush=True)
        if midpoint_step is not None and index + 1 == midpoint_step and midpoint_callback is not None:
            midpoint_callback(model, optimizer, capture_rng(), index + 1)
    return model, time.perf_counter() - started


class ArtifactManifest:
    def __init__(self, path: Path, header: dict[str, object]):
        self.path = path
        if path.exists():
            self.data = json.loads(path.read_text())
            if self.data.get("header") != header:
                raise RuntimeError("restart manifest provenance differs; use --force")
        else:
            self.data = {"header": header, "artifacts": {}}

    def record(self, artifact_id: str, record: dict[str, object]) -> None:
        self.data["artifacts"][artifact_id] = record
        atomic_json(self.path, self.data)

    def valid_file(self, artifact_id: str, expected: dict[str, object]) -> Path | None:
        record = self.data["artifacts"].get(artifact_id)
        if not isinstance(record, dict) or record.get("status") != "complete":
            return None
        if any(record.get(key) != value for key, value in expected.items()):
            return None
        path = Path(record.get("path", ""))
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            return None
        return path


def artifact_record(path: Path, artifact_type: str, metadata: dict[str, object], seconds: float = 0.0) -> dict[str, object]:
    return {
        "artifact_type": artifact_type, "path": str(path), "sha256": sha256_file(path), "status": "complete",
        "seconds": seconds, "timestamp_utc": datetime.now(timezone.utc).isoformat(), **metadata,
    }


def save_checkpoint(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def load_checkpoint(path: Path) -> dict[str, object]:
    return torch.load(path, map_location="cpu", weights_only=False)


def run_header() -> None:
    print("=" * 60, flush=True)
    print("B2.3 PACS portfolio-opportunity experiment", flush=True)
    print("Device: CPU", flush=True)
    print("TEST: CLOSED", flush=True)
    print(f"Fits: {TOTAL_FITS} | evaluations: {TOTAL_EVALUATIONS}", flush=True)
    print(f"Primary rows: {TOTAL_PRIMARY_ROWS} | dose rows: {TOTAL_DOSE_ROWS}", flush=True)
    print("=" * 60, flush=True)


def dry_run(frame: pd.DataFrame, splits: dict[int, DevelopmentSplits], image_root: Path | None, output_dir: Path) -> None:
    validate_counts()
    if image_root is not None and not image_root.is_dir():
        raise FileNotFoundError(image_root)
    plan = build_opportunity_plan(frame, splits)
    singletons, joints = plan_specs()
    output_dir.mkdir(parents=True, exist_ok=True)
    print("Dry-run successful.", flush=True)
    print("5 F0", flush=True)
    print("5 D", flush=True)
    print(f"{len(plan)} opportunities", flush=True)
    print(f"{len(singletons)} singleton fits", flush=True)
    print(f"{len(joints)} joint fits", flush=True)
    print(f"{TOTAL_FITS} total fits", flush=True)
    print(f"{TOTAL_EVALUATIONS} VALIDATION evaluations", flush=True)
    print(f"{TOTAL_PRIMARY_ROWS} primary analytical rows", flush=True)
    print(f"{TOTAL_DOSE_ROWS} compute-dose valuations", flush=True)
    print("F_ij^CM: 90 intermediate checkpoints inside joint fits; 0 additional fits.", flush=True)
    print("TEST remains closed. No training or teacher inference executed.", flush=True)


def run_manifest_header(args: argparse.Namespace, config: dict) -> dict[str, object]:
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        git_commit = "unknown"
    return {
        "protocol_id": PROTOCOL_ID, "protocol_sha256": sha256_file(PROTOCOL_PATH), "config_sha256": sha256_file(CONFIG_PATH),
        "implementation_sha256": sha256_file(Path(__file__)), "analysis_sha256": sha256_file(ANALYZE_PATH),
        "b20_runner_sha256": sha256_file(B20_PATH), "split_library_sha256": sha256_file(B20_LIBRARY_PATH),
        "dataset_revision": DATASET_REVISION, "dataset_sha256": DATASET_SHA256, "manifest_sha256": sha256_file(args.manifest),
        "git_commit": git_commit, "device": "cpu", "torch": torch.__version__, "python": sys.version,
        "torchvision": torchvision.__version__, "numpy": np.__version__, "pandas": pd.__version__, "command": sys.argv,
        "threads": torch.get_num_threads(), "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(), "test_used": False,
        "seeds": list(SEEDS), "N": list(N_VALUES), "costs": list(COSTS), "B": list(FUTURE_WEIGHTS), "kappa": KAPPA,
        "visible_config": {
            "split_fractions": {key: config["split_fractions"][key] for key in ("base", "transfer", "validation")},
            "fast": config["fast"], "deep": config["deep"], "training": config["training"],
        },
    }


def reset_generated(output_dir: Path) -> None:
    for name in (".cache", "run_manifest.json", "split_manifest.csv", "base_states.jsonl", "opportunities.jsonl", "development_states.jsonl", "state_metrics.csv", "primary_results.csv", "reproducibility.csv", "compute_dose.csv", "competence_changes.csv", "summary.md"):
        path = output_dir / name
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def execute_training(enabled: bool, callback: Callable[[], object]) -> object | None:
    """Guard used by dry-run/analyze-only and their regression tests."""
    if not enabled:
        return None
    return callback()


def deterministic_fixture() -> tuple[str, float]:
    """Small CPU fixture used to verify deterministic model/update behavior."""
    seed_everything(seed64("deterministic-fixture"))
    model = nn.Linear(3, 2)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
    features = torch.tensor([[1.0, -1.0, 0.5], [0.0, 0.25, -0.5]])
    targets = torch.tensor([1, 0])
    loss = torch.tensor(0.0)
    for _ in range(3):
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(features), targets)
        loss.backward()
        optimizer.step()
    return state_dict_fingerprint(model), float(loss.detach())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--image-root", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    started = time.perf_counter()
    run_header()
    require_cpu(args.device)
    if args.dry_run and args.analyze_only:
        raise ValueError("--dry-run and --analyze-only are mutually exclusive")
    if args.force and (args.dry_run or args.analyze_only):
        raise ValueError("--force applies only to a full execution")
    if args.analyze_only:
        analyzer = _load_module("b23_analyze", ANALYZE_PATH)
        analyzer.run_analysis(args.output_dir, started=started)
        return
    config = json.loads(CONFIG_PATH.read_text())
    validate_config(config)
    validate_counts()
    if not args.manifest.is_file():
        raise FileNotFoundError(args.manifest)
    frame = pd.read_csv(args.manifest)
    b20.validate_manifest(frame)
    splits = {seed: development_splits(frame, seed) for seed in SEEDS}
    if args.dry_run:
        dry_run(frame, splits, args.image_root, args.output_dir)
        return
    if args.image_root is None or not args.image_root.is_dir():
        raise FileNotFoundError("full execution requires a valid --image-root")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.force:
        reset_generated(args.output_dir)
    # The full execution is deliberately isolated here; no dry-run or analysis path can enter it.
    execute_training(True, lambda: execute_full(args, frame, splits, config, started))


def execute_full(args: argparse.Namespace, frame: pd.DataFrame, splits: dict[int, DevelopmentSplits], config: dict, started: float) -> None:
    """Execute the frozen 160-fit pipeline. Never called by tests or dry-run."""
    torch.use_deterministic_algorithms(True)
    output_dir = args.output_dir
    cache = output_dir / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    header = run_manifest_header(args, config)
    artifacts = ArtifactManifest(output_dir / "run_manifest.json", header)
    lookup = frame.set_index("sample_id", drop=False)

    split_rows: list[dict[str, object]] = []
    for seed, split in splits.items():
        for role, ids in (("BASE", split.base), ("TRANSFER", split.transfer), ("VALIDATION", split.validation)):
            split_rows.extend(
                {
                    "seed": seed, "sample_id": sample_id, "role": role,
                    "domain": str(lookup.loc[sample_id].domain), "label": int(lookup.loc[sample_id].label),
                    "relative_path": str(lookup.loc[sample_id].relative_path),
                }
                for sample_id in ids
            )
    atomic_csv(output_dir / "split_manifest.csv", pd.DataFrame(split_rows))

    print("[1/6] Base states", flush=True)
    for seed in SEEDS:
        validation = lookup.loc[list(splits[seed].validation)].reset_index(drop=True)
        f0_ids = b20.select_base_fraction(frame, splits[seed].base, F0_FRACTION, seed + 250)
        base_frames = {
            "F0": lookup.loc[list(f0_ids)].reset_index(drop=True),
            "D": lookup.loc[list(splits[seed].base + splits[seed].transfer)].reset_index(drop=True),
        }
        for state_name, kind in (("F0", "fast"), ("D", "deep")):
            artifact_id = f"{state_name}_s{seed}"
            expected = {"artifact_type": state_name, "seed": seed}
            if artifacts.valid_file(artifact_id, expected):
                print(f"reuse {artifact_id}", flush=True)
                continue
            print(f"[fit {seed * 2 + (1 if state_name == 'F0' else 2)}/{TOTAL_FITS}] seed={seed} state={state_name}", flush=True)
            model, seconds = train_base(kind, seed, base_frames[state_name], config, args.image_root, torch.device("cpu"))
            scores = score_model(model, validation, args.image_root, torch.device("cpu"))
            payload = {
                "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                "model_fingerprint": state_dict_fingerprint(model), "scores": scores, "seed": seed, "state": state_name,
                "training_seed": seed + (2500 if state_name == "F0" else 30000),
                "training_ids": base_frames[state_name].sample_id.astype(int).tolist(),
                "training_ids_sha256": sha256_json(base_frames[state_name].sample_id.astype(int).tolist()),
                "validation_ids_sha256": sha256_json(list(splits[seed].validation)), "evaluation_split": "validation", "test_used": False,
            }
            path = cache / "base" / f"{artifact_id}.pt"
            save_checkpoint(path, payload)
            artifacts.record(artifact_id, artifact_record(path, state_name, {"seed": seed, "model_fingerprint": payload["model_fingerprint"]}, seconds))
            del model

    print("[2/6] Immutable opportunities", flush=True)
    opportunity_plan = build_opportunity_plan(frame, splits)
    opportunity_hashes: dict[tuple[int, str, int], str] = {}
    completed_streams = 0
    for seed in SEEDS:
        d_payload = load_checkpoint(Path(artifacts.data["artifacts"][f"D_s{seed}"]["path"]))
        deep = b20.make_model("deep", seed + 30000, torch.device("cpu"), pretrained=False)
        deep.load_state_dict(d_payload["model_state"])
        for domain in DOMAINS:
            specs = [spec for spec in opportunity_plan if spec.seed == seed and spec.domain == domain]
            maximum_ids = specs[-1].sample_ids
            maximum_id = f"opmax_s{seed}_{domain}"
            maximum_expected = {"artifact_type": "opportunity_max", "seed": seed, "domain": domain}
            max_path = artifacts.valid_file(maximum_id, maximum_expected)
            if max_path:
                max_payload, _ = read_envelope(max_path)
            else:
                selected = lookup.loc[list(maximum_ids)].reset_index(drop=True)
                labels = teacher_labels(deep, selected, args.image_root, torch.device("cpu"))
                samples = [
                    {"sample_id": int(row.sample_id), "relative_path": str(row.relative_path), "domain": domain, "pseudo_label": int(label)}
                    for row, label in zip(selected.itertuples(index=False), labels, strict=True)
                ]
                max_payload = opportunity_payload(specs[-1], maximum_ids, samples, artifacts.data["artifacts"][f"D_s{seed}"]["sha256"])
                max_payload["N"] = 100
                max_payload["teacher_query_count"] = 100
                max_payload["pseudo_label_count"] = 100
                max_path = cache / "opportunities" / f"{maximum_id}.json"
                write_envelope(max_path, max_payload)
                artifacts.record(maximum_id, artifact_record(max_path, "opportunity_max", {"seed": seed, "domain": domain}))
            for spec in specs:
                expected = {"artifact_type": "opportunity", "seed": seed, "domain": domain, "N": spec.n}
                path = artifacts.valid_file(spec.artifact_id, expected)
                if path:
                    _, opportunity_hashes[(seed, domain, spec.n)] = read_envelope(path)
                    continue
                rows = list(max_payload["samples"][: spec.n])
                payload = opportunity_payload(spec, maximum_ids, rows, artifacts.data["artifacts"][f"D_s{seed}"]["sha256"])
                path = cache / "opportunities" / f"{spec.artifact_id}.json"
                digest = write_envelope(path, payload)
                artifacts.record(spec.artifact_id, artifact_record(path, "opportunity", {"seed": seed, "domain": domain, "N": spec.n, "payload_sha256": digest}))
                opportunity_hashes[(seed, domain, spec.n)] = digest
            completed_streams += 1
            print(f"opportunity streams {completed_streams}/20 | views {completed_streams * 3}/{TOTAL_OPPORTUNITIES}", flush=True)
        del deep

    print("[3/6] Singleton development", flush=True)
    singletons, joints = plan_specs()
    completed_fit_times = [float(record.get("seconds", 0)) for record in artifacts.data["artifacts"].values() if record.get("artifact_type") in {"F0", "D", "singleton", "joint"} and float(record.get("seconds", 0)) > 0]
    for spec in singletons:
        f0_record = artifacts.data["artifacts"][f"F0_s{spec.seed}"]
        op_path = Path(artifacts.data["artifacts"][f"op_s{spec.seed}_{spec.domain}_n{spec.n}"]["path"])
        op, op_hash = read_envelope(op_path)
        expected = {
            "artifact_type": "singleton", "seed": spec.seed, "domain": spec.domain, "N": spec.n,
            "parent_f0_sha256": f0_record["sha256"], "opportunity_sha256": op_hash,
        }
        if artifacts.valid_file(spec.artifact_id, expected):
            print(f"reuse singleton {spec.number}/{TOTAL_SINGLETON_FITS}: {spec.artifact_id}", flush=True)
            continue
        f0 = load_checkpoint(Path(f0_record["path"]))
        ids = tuple(int(value) for value in op["sample_ids"])
        labels = {int(row["sample_id"]): int(row["pseudo_label"]) for row in op["samples"]}
        schedule = singleton_schedule(spec.seed, spec.n, spec.domain, ids)
        audit = schedule_audit(schedule, spec.n, (spec.domain,))
        print(f"[fit {TOTAL_BASE_FITS + spec.number}/{TOTAL_FITS}] seed={spec.seed} state=Fi domain={spec.domain} N={spec.n}", flush=True)
        model, seconds = train_scheduled(f0["model_state"], schedule, labels, lookup, args.image_root, spec.seed, spec.n, config)
        validation = lookup.loc[list(splits[spec.seed].validation)].reset_index(drop=True)
        scores = score_model(model, validation, args.image_root, torch.device("cpu"))
        payload = {
            "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()}, "model_fingerprint": state_dict_fingerprint(model),
            "scores": scores, "artifact_type": "singleton", "seed": spec.seed, "domain": spec.domain, "N": spec.n,
            "parent_f0_sha256": f0_record["sha256"], "deep_sha256": artifacts.data["artifacts"][f"D_s{spec.seed}"]["sha256"],
            "opportunity_sha256": op_hash, "training_seed": seed64("training", spec.seed, spec.n), **audit,
            "optimizer": {"class": "SGD", "learning_rate": float(config["fast"]["learning_rate"]), "momentum": float(config["fast"]["momentum"]), "weight_decay": 0.0},
            "validation_ids_sha256": f0["validation_ids_sha256"], "evaluation_split": "validation", "test_used": False,
        }
        path = cache / "singletons" / f"{spec.artifact_id}.pt"
        save_checkpoint(path, payload)
        artifacts.record(spec.artifact_id, artifact_record(path, "singleton", expected | {"parent_f0_sha256": f0_record["sha256"], "opportunity_sha256": op_hash}, seconds))
        completed_fit_times.append(seconds)
        completed = sum(record.get("artifact_type") in {"F0", "D", "singleton", "joint"} for record in artifacts.data["artifacts"].values())
        eta = float(np.mean(completed_fit_times)) * (TOTAL_FITS - completed) if completed_fit_times else 0.0
        print(f"completed singleton {spec.number}/{TOTAL_SINGLETON_FITS} | total fits {completed}/{TOTAL_FITS} | elapsed {format_duration(time.perf_counter()-started)} | ETA {format_duration(eta)}", flush=True)
        del model

    print("[4/6] Joint development with in-trajectory CM checkpoints", flush=True)
    for spec in joints:
        f0_record = artifacts.data["artifacts"][f"F0_s{spec.seed}"]
        ops, hashes, ids, labels = {}, {}, {}, {}
        for domain in (spec.domain_i, spec.domain_j):
            payload, digest = read_envelope(Path(artifacts.data["artifacts"][f"op_s{spec.seed}_{domain}_n{spec.n}"]["path"]))
            ops[domain], hashes[domain] = payload, digest
            ids[domain] = tuple(int(value) for value in payload["sample_ids"])
            labels.update({int(row["sample_id"]): int(row["pseudo_label"]) for row in payload["samples"]})
        expected = {
            "artifact_type": "joint", "seed": spec.seed, "N": spec.n, "domain_i": spec.domain_i, "domain_j": spec.domain_j,
            "parent_f0_sha256": f0_record["sha256"], "opportunity_i_sha256": hashes[spec.domain_i], "opportunity_j_sha256": hashes[spec.domain_j],
        }
        cm_expected = {
            "artifact_type": "joint_cm", "seed": spec.seed, "N": spec.n, "domain_i": spec.domain_i,
            "domain_j": spec.domain_j, "trajectory_id": spec.artifact_id, "parent_f0_sha256": f0_record["sha256"],
        }
        final_valid = artifacts.valid_file(spec.artifact_id, expected)
        cm_valid = artifacts.valid_file(spec.artifact_id + "_CM", cm_expected)
        if final_valid and cm_valid:
            print(f"reuse joint {spec.number}/{TOTAL_JOINT_FITS}: {spec.artifact_id}", flush=True)
            continue
        f0 = load_checkpoint(Path(f0_record["path"]))
        schedule = joint_schedule(spec, ids[spec.domain_i], ids[spec.domain_j])
        steps, exposures = dose(spec.n)
        cm_path = cache / "joints" / f"{spec.artifact_id}_CM.pt"
        resume = None
        valid_cm = artifacts.valid_file(spec.artifact_id + "_CM", cm_expected)
        if valid_cm:
            resume = load_checkpoint(valid_cm)

        def save_midpoint(model, optimizer, rng_state, step):
            optimizer_state = optimizer.state_dict()
            payload = {
                "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()}, "optimizer_state": optimizer_state,
                "rng_state": rng_state, "step": step, "model_fingerprint": state_dict_fingerprint(model), "trajectory_id": spec.artifact_id,
                "parent_f0_sha256": f0_record["sha256"], "opportunity_i_sha256": hashes[spec.domain_i], "opportunity_j_sha256": hashes[spec.domain_j],
                "schedule_sha256": sha256_json(schedule), "exposures_i": exposures // 2, "exposures_j": exposures // 2, "test_used": False,
                "optimizer_state_sha256": sha256_torch_object(optimizer_state), "rng_state_sha256": sha256_torch_object(rng_state),
                "training_seed": seed64("training", spec.seed, spec.n),
                "optimizer": {"class": "SGD", "learning_rate": float(config["fast"]["learning_rate"]), "momentum": float(config["fast"]["momentum"]), "weight_decay": 0.0},
            }
            save_checkpoint(cm_path, payload)
            artifacts.record(spec.artifact_id + "_CM", artifact_record(cm_path, "joint_cm", cm_expected | {"parent_f0_sha256": f0_record["sha256"]}))

        print(f"[fit {TOTAL_BASE_FITS + TOTAL_SINGLETON_FITS + spec.number}/{TOTAL_FITS}] seed={spec.seed} state=Fij pair={spec.pair} N={spec.n}", flush=True)
        model, seconds = train_scheduled(
            f0["model_state"], schedule, labels, lookup, args.image_root, spec.seed, spec.n, config,
            resume=resume, midpoint_step=steps, midpoint_callback=None if resume else save_midpoint,
        )
        cm_payload = load_checkpoint(cm_path)
        validation = lookup.loc[list(splits[spec.seed].validation)].reset_index(drop=True)
        cm_model = b20.make_model("fast", seed64("training", spec.seed, spec.n), torch.device("cpu"), pretrained=False)
        cm_model.load_state_dict(cm_payload["model_state"])
        cm_scores = score_model(cm_model, validation, args.image_root, torch.device("cpu"))
        final_scores = score_model(model, validation, args.image_root, torch.device("cpu"))
        cm_payload["scores"] = cm_scores
        cm_payload["validation_ids_sha256"] = f0["validation_ids_sha256"]
        cm_payload["evaluation_split"] = "validation"
        save_checkpoint(cm_path, cm_payload)
        artifacts.record(spec.artifact_id + "_CM", artifact_record(cm_path, "joint_cm", cm_expected | {"parent_f0_sha256": f0_record["sha256"]}))
        payload = {
            "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()}, "model_fingerprint": state_dict_fingerprint(model),
            "scores": final_scores, "artifact_type": "joint", "seed": spec.seed, "N": spec.n, "domain_i": spec.domain_i, "domain_j": spec.domain_j,
            "trajectory_id": spec.artifact_id, "midpoint_sha256": artifacts.data["artifacts"][spec.artifact_id + "_CM"]["sha256"],
            "parent_f0_sha256": f0_record["sha256"], "deep_sha256": artifacts.data["artifacts"][f"D_s{spec.seed}"]["sha256"],
            "opportunity_i_sha256": hashes[spec.domain_i], "opportunity_j_sha256": hashes[spec.domain_j],
            "training_seed": seed64("training", spec.seed, spec.n), "steps": 2 * steps, "batch_size": BATCH_SIZE,
            "optimizer": {"class": "SGD", "learning_rate": float(config["fast"]["learning_rate"]), "momentum": float(config["fast"]["momentum"]), "weight_decay": 0.0},
            "exposures_i": exposures, "exposures_j": exposures, "schedule_sha256": sha256_json(schedule),
            "validation_ids_sha256": f0["validation_ids_sha256"], "evaluation_split": "validation", "test_used": False,
        }
        path = cache / "joints" / f"{spec.artifact_id}.pt"
        save_checkpoint(path, payload)
        artifacts.record(spec.artifact_id, artifact_record(path, "joint", expected | {"parent_f0_sha256": f0_record["sha256"], "opportunity_i_sha256": hashes[spec.domain_i], "opportunity_j_sha256": hashes[spec.domain_j]}, seconds))
        completed_fit_times.append(seconds)
        remaining = TOTAL_FITS - sum(record.get("artifact_type") in {"F0", "D", "singleton", "joint"} for record in artifacts.data["artifacts"].values())
        eta = float(np.mean(completed_fit_times)) * remaining if completed_fit_times else 0.0
        print(f"completed {spec.artifact_id} | elapsed {format_duration(time.perf_counter()-started)} | ETA {format_duration(eta)}", flush=True)
        del model, cm_model

    print("[5/6] Compatibility audit and analysis", flush=True)
    analyzer = _load_module("b23_analyze", ANALYZE_PATH)
    analyzer.run_analysis(output_dir, started=started)


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    main()
