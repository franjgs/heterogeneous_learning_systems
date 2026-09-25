"""Run the frozen CPU-only PACS B2.4 interference-controlled experiment.

Scientific authority: docs/experimental_foundations/B24_PROTOCOL.md at commit
491659c. Dry-run and analyze-only never train models or query the teacher.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch import nn
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from hls.experiment_timing import ExperimentTimingLogger  # noqa: E402

PROTOCOL_PATH = ROOT / "docs/experimental_foundations/B24_PROTOCOL.md"
B23_RUN_PATH = ROOT / "experiments/pilots/b23_portfolio_opportunity/run.py"
B23_ANALYZE_PATH = ROOT / "experiments/pilots/b23_portfolio_opportunity/analyze.py"
ANALYZE_PATH = Path(__file__).with_name("analyze.py")
DEFAULT_B23_OUTPUT = ROOT / "results/pilots/b23_portfolio_opportunity"
DEFAULT_OUTPUT = ROOT / "results/pilots/b24_interference_controlled"
DEFAULT_MANIFEST = ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv"


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


b23 = _load_module("b24_b23_run", B23_RUN_PATH)

PROTOCOL_ID = "B2.4-PACS-interference-v1"
FROZEN_PROTOCOL_COMMIT = "491659c"
DOMAINS = b23.DOMAINS
SEEDS = b23.SEEDS
N_VALUES = b23.N_VALUES
COSTS = b23.COSTS
BATCH_SIZE = 16
HALF_BATCH = 8
TOTAL_CASES = 60
TOTAL_STD_REUSED = 60
TOTAL_O50_FITS = 60
TOTAL_MIXED_FITS = 60
TOTAL_NEW_FITS = 120
TOTAL_NEW_EVALUATIONS = 180
TOTAL_METHOD_STATES = 240
TOTAL_METHOD_VALUE_ROWS = 1200
TOTAL_PRIMARY_CONTRAST_ROWS = 300
NUMERIC_TOLERANCE = 1e-12
ACTIVE_TIMING: ExperimentTimingLogger | None = None
RESTART_COMMAND = (
    "python experiments/pilots/b24_interference_controlled/run.py "
    "--device cpu --image-root <PACS_IMAGE_ROOT>"
)


@dataclass(frozen=True)
class CaseSpec:
    number: int
    seed: int
    domain: str
    n: int

    @property
    def key(self) -> tuple[int, str, int]:
        return self.seed, self.domain, self.n

    @property
    def o50_id(self) -> str:
        return f"O50_s{self.seed}_{self.domain}_n{self.n}"

    @property
    def rep_id(self) -> str:
        return f"REP_s{self.seed}_{self.domain}_n{self.n}"

    @property
    def rep2_id(self) -> str:
        return f"REP2_s{self.seed}_{self.domain}_n{self.n}"

    @property
    def replay_id(self) -> str:
        return f"replay_s{self.seed}_{self.domain}_n{self.n}"


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


def seed64(*parts: object) -> int:
    text = PROTOCOL_ID + "|" + "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big") & ((1 << 63) - 1)


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


def write_envelope(path: Path, payload: dict[str, object]) -> str:
    digest = sha256_json(payload)
    atomic_json(path, {"payload": payload, "sha256": digest})
    return digest


def read_envelope(path: Path, expected: dict[str, object] | None = None) -> tuple[dict[str, object], str]:
    envelope = json.loads(path.read_text())
    payload, digest = envelope.get("payload"), envelope.get("sha256")
    if not isinstance(payload, dict) or digest != sha256_json(payload):
        raise RuntimeError(f"corrupt artifact envelope: {path}")
    for key, value in (expected or {}).items():
        if payload.get(key) != value:
            raise RuntimeError(f"incompatible {path.name}: {key}")
    return payload, str(digest)


def require_cpu(device: str) -> torch.device:
    if device != "cpu":
        raise ValueError(f"B2.4 is CPU ONLY; requested device={device!r}")
    return torch.device("cpu")


def plan_cases() -> list[CaseSpec]:
    result: list[CaseSpec] = []
    for seed in SEEDS:
        for n in N_VALUES:
            for domain in DOMAINS:
                result.append(CaseSpec(len(result) + 1, seed, domain, n))
    return result


def dose(n: int) -> tuple[int, int]:
    if n not in N_VALUES:
        raise ValueError(f"unregistered N={n}")
    steps = 3 * math.ceil(n / BATCH_SIZE)
    return steps, BATCH_SIZE * steps


def validate_counts() -> None:
    cases = plan_cases()
    checks = {
        "seeds": len(SEEDS) == 5,
        "domains": len(DOMAINS) == 4,
        "N": N_VALUES == (25, 50, 100),
        "cases": len(cases) == TOTAL_CASES,
        "STD": len(cases) == TOTAL_STD_REUSED,
        "O50": len(cases) == TOTAL_O50_FITS,
        "mixed": len(cases) == TOTAL_MIXED_FITS,
        "new_fits": TOTAL_O50_FITS + TOTAL_MIXED_FITS == TOTAL_NEW_FITS,
        "evaluations": len(cases) * 3 == TOTAL_NEW_EVALUATIONS,
        "method_states": len(cases) * 4 == TOTAL_METHOD_STATES,
        "method_values": len(cases) * 4 * len(COSTS) == TOTAL_METHOD_VALUE_ROWS,
        "primary_contrasts": len(cases) * len(COSTS) == TOTAL_PRIMARY_CONTRAST_ROWS,
    }
    failed = [key for key, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"frozen B2.4 count mismatch: {failed}")


def replay_domain_order(seed: int, intervention_domain: str) -> tuple[str, ...]:
    eligible = [domain for domain in DOMAINS if domain != intervention_domain]
    return tuple(
        sorted(
            eligible,
            key=lambda domain: hashlib.sha256(
                f"{PROTOCOL_ID}|replay-domain-order|{seed}|{intervention_domain}|{domain}".encode()
            ).digest(),
        )
    )


def replay_quotas(seed: int, intervention_domain: str, n: int) -> dict[str, int]:
    order = replay_domain_order(seed, intervention_domain)
    base, remainder = divmod(n, len(order))
    return {domain: base + int(index < remainder) for index, domain in enumerate(order)}


def replay_ids(
    f0_training_ids: tuple[int, ...], lookup: pd.DataFrame, seed: int, intervention_domain: str, n: int
) -> tuple[int, ...]:
    quotas = replay_quotas(seed, intervention_domain, n)
    selected: list[int] = []
    for domain in replay_domain_order(seed, intervention_domain):
        eligible = [sample_id for sample_id in f0_training_ids if str(lookup.loc[sample_id, "domain"]) == domain]
        ordered = sorted(
            eligible,
            key=lambda sample_id: hashlib.sha256(
                f"{PROTOCOL_ID}|replay|{seed}|{intervention_domain}|{domain}|{sample_id}".encode()
            ).digest(),
        )
        quota = quotas[domain]
        if len(ordered) < quota:
            raise RuntimeError(f"insufficient F0 replay pool: seed={seed} domain={domain} N={n}")
        selected.extend(ordered[:quota])
    if len(selected) != n or len(set(selected)) != n:
        raise RuntimeError("invalid replay buffer cardinality")
    return tuple(selected)


def replay_payload(
    spec: CaseSpec,
    ids: tuple[int, ...],
    lookup: pd.DataFrame,
    parent_f0_sha256: str,
    split_manifest_sha256: str,
) -> dict[str, object]:
    samples = [
        {
            "sample_id": sample_id,
            "relative_path": str(lookup.loc[sample_id, "relative_path"]),
            "domain": str(lookup.loc[sample_id, "domain"]),
            "label": int(lookup.loc[sample_id, "label"]),
            "label_provenance": "F0_observed_ground_truth",
        }
        for sample_id in ids
    ]
    return {
        "protocol_id": PROTOCOL_ID,
        "artifact_type": "replay",
        "seed": spec.seed,
        "domain": spec.domain,
        "N": spec.n,
        "sample_ids": list(ids),
        "samples": samples,
        "source_domain_order": list(replay_domain_order(spec.seed, spec.domain)),
        "source_domain_quotas": replay_quotas(spec.seed, spec.domain, spec.n),
        "parent_f0_sha256": parent_f0_sha256,
        "split_manifest_sha256": split_manifest_sha256,
        "selection_uses_labels": False,
        "test_used": False,
    }


def _cycled_domain_exposures(
    ids: tuple[int, ...], count: int, seed: int, intervention_domain: str, n: int, source_domain: str
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    exposure_counts = {sample_id: 0 for sample_id in ids}
    cycle = 0
    while len(output) < count:
        ordered = sorted(
            ids,
            key=lambda sample_id: hashlib.sha256(
                f"{PROTOCOL_ID}|replay-schedule|{seed}|{intervention_domain}|{n}|{source_domain}|{cycle}|{sample_id}".encode()
            ).digest(),
        )
        for sample_id in ordered:
            if len(output) == count:
                break
            exposure_counts[sample_id] += 1
            output.append(
                {
                    "sample_id": sample_id,
                    "exposure": exposure_counts[sample_id],
                    "domain": source_domain,
                    "role": "replay",
                }
            )
        cycle += 1
    return output


def replay_exposure_sequence(spec: CaseSpec, replay: dict[str, object], count: int) -> list[dict[str, object]]:
    order = tuple(str(value) for value in replay["source_domain_order"])
    ids_by_domain = {
        domain: tuple(int(row["sample_id"]) for row in replay["samples"] if row["domain"] == domain)
        for domain in order
    }
    per_domain = math.ceil(count / len(order))
    streams = {
        domain: _cycled_domain_exposures(
            ids_by_domain[domain], per_domain, spec.seed, spec.domain, spec.n, domain
        )
        for domain in order
    }
    positions = {domain: 0 for domain in order}
    output: list[dict[str, object]] = []
    while len(output) < count:
        for domain in order:
            if len(output) == count:
                break
            output.append(streams[domain][positions[domain]])
            positions[domain] += 1
    return output


def opportunity_exposure_sequence(spec: CaseSpec, opportunity_ids: tuple[int, ...], count: int) -> list[dict[str, object]]:
    return [
        {**entry, "domain": spec.domain, "role": "opportunity"}
        for entry in b23.cyclic_exposures(opportunity_ids, count, spec.seed, spec.n, spec.domain)
    ]


def build_schedules(
    spec: CaseSpec, opportunity_ids: tuple[int, ...], replay: dict[str, object]
) -> tuple[list[list[dict[str, object]]], list[list[dict[str, object]]]]:
    steps, exposures = dose(spec.n)
    opportunity = opportunity_exposure_sequence(spec, opportunity_ids, exposures)
    replay_sequence = replay_exposure_sequence(spec, replay, exposures)
    o50: list[list[dict[str, object]]] = []
    mixed: list[list[dict[str, object]]] = []
    for step in range(2 * steps):
        opportunity_half = opportunity[step * HALF_BATCH : (step + 1) * HALF_BATCH]
        replay_half = replay_sequence[step * HALF_BATCH : (step + 1) * HALF_BATCH]
        originals = [dict(entry) for entry in opportunity_half]
        duplicates = [{**entry, "role": "opportunity_duplicate"} for entry in opportunity_half]
        if step < steps:
            o50.append(originals + duplicates if step % 2 == 0 else duplicates + originals)
        mixed.append(originals + replay_half if step % 2 == 0 else replay_half + originals)
    if len(o50) != steps or len(mixed) != 2 * steps:
        raise RuntimeError("invalid B2.4 schedule length")
    if any(len(batch) != BATCH_SIZE for batch in o50 + mixed):
        raise RuntimeError("invalid B2.4 batch size")
    validate_matched_opportunity(o50, mixed[:steps])
    return o50, mixed


def informative_opportunity_entries(schedule: list[list[dict[str, object]]]) -> list[tuple[int, int, int]]:
    result: list[tuple[int, int, int]] = []
    for batch in schedule:
        for position, entry in enumerate(batch):
            if entry["role"] == "opportunity":
                result.append((int(entry["sample_id"]), int(entry["exposure"]), position))
    return result


def validate_matched_opportunity(
    o50: list[list[dict[str, object]]], rep: list[list[dict[str, object]]]
) -> None:
    if len(o50) != len(rep):
        raise RuntimeError("O50/REP step mismatch")
    if informative_opportunity_entries(o50) != informative_opportunity_entries(rep):
        raise RuntimeError("O50/REP opportunity exposure mismatch")
    for left, right in zip(o50, rep, strict=True):
        left_info = [entry for entry in left if entry["role"] == "opportunity"]
        duplicates = [entry for entry in left if entry["role"] == "opportunity_duplicate"]
        replay = [entry for entry in right if entry["role"] == "replay"]
        if len(left_info) != HALF_BATCH or len(duplicates) != HALF_BATCH or len(replay) != HALF_BATCH:
            raise RuntimeError("invalid O50/REP half-batch")
        if [(x["sample_id"], x["exposure"]) for x in left_info] != [
            (x["sample_id"], x["exposure"]) for x in duplicates
        ]:
            raise RuntimeError("O50 duplicates do not match informative entries")


def schedule_audit(
    spec: CaseSpec,
    method: str,
    schedule: list[list[dict[str, object]]],
    opportunity_hash: str,
    replay_hash: str | None,
) -> dict[str, object]:
    flat = [entry for batch in schedule for entry in batch]
    informative = [entry for entry in flat if entry["role"] == "opportunity"]
    duplicate = [entry for entry in flat if entry["role"] == "opportunity_duplicate"]
    replay = [entry for entry in flat if entry["role"] == "replay"]
    return {
        "method": method,
        "steps": len(schedule),
        "batch_size": BATCH_SIZE,
        "processed_slots": len(flat),
        "informative_opportunity_exposures": len(informative),
        "duplicate_opportunity_slots": len(duplicate),
        "replay_exposures": len(replay),
        "opportunity_projection_sha256": sha256_json(informative_opportunity_entries(schedule)),
        "schedule_sha256": sha256_json(schedule),
        "opportunity_sha256": opportunity_hash,
        "replay_sha256": replay_hash,
        "N": spec.n,
    }


def replay_augmentation_seed(seed: int, n: int, sample_id: int, exposure: int) -> int:
    return seed64("augmentation", seed, n, sample_id, exposure)


class ScheduledBatchBuilder:
    def __init__(
        self,
        lookup: pd.DataFrame,
        labels: dict[int, int],
        image_root: Path,
        seed: int,
        n: int,
    ):
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

    def _tensor(self, entry: dict[str, object]) -> torch.Tensor:
        sample_id = int(entry["sample_id"])
        row = self.lookup.loc[sample_id]
        with Image.open(self.image_root / row.relative_path) as source:
            image = source.convert("RGB")
        role = str(entry["role"])
        rng_seed = (
            b23.augmentation_seed(self.seed, self.n, sample_id, int(entry["exposure"]))
            if role.startswith("opportunity")
            else replay_augmentation_seed(self.seed, self.n, sample_id, int(entry["exposure"]))
        )
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(rng_seed)
            return self.transform(image)

    def batch(self, entries: list[dict[str, object]]) -> tuple[torch.Tensor, torch.Tensor]:
        tensors: dict[tuple[int, int], torch.Tensor] = {}
        for entry in entries:
            if entry["role"] == "opportunity_duplicate":
                continue
            key = int(entry["sample_id"]), int(entry["exposure"])
            tensors[key] = self._tensor(entry)
        images: list[torch.Tensor] = []
        targets: list[int] = []
        for entry in entries:
            key = int(entry["sample_id"]), int(entry["exposure"])
            images.append(tensors[key].clone())
            targets.append(int(self.labels[int(entry["sample_id"])]))
        return torch.stack(images), torch.tensor(targets, dtype=torch.long)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(b23.b20.numpy_compatible_seed(seed))
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def capture_rng() -> dict[str, object]:
    return {"python": random.getstate(), "numpy": np.random.get_state(), "torch": torch.get_rng_state()}


def restore_rng(state: dict[str, object]) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])


def train_scheduled(
    f0_state: dict[str, torch.Tensor],
    schedule: list[list[dict[str, object]]],
    labels: dict[int, int],
    lookup: pd.DataFrame,
    image_root: Path,
    seed: int,
    n: int,
    config: dict[str, object],
    *,
    resume: dict[str, object] | None = None,
    midpoint_step: int | None = None,
    midpoint_callback: Callable[[nn.Module, torch.optim.Optimizer, dict[str, object], int], None] | None = None,
) -> tuple[nn.Module, float]:
    training_seed = b23.derived_training_seed(seed, n)
    seed_everything(training_seed)
    model = b23.b20.make_model("fast", training_seed, torch.device("cpu"), pretrained=False)
    model.load_state_dict(f0_state)
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=float(config["fast"]["learning_rate"]),
        momentum=float(config["fast"]["momentum"]),
        weight_decay=0,
    )
    start_step = 0
    if resume is not None:
        model.load_state_dict(resume["model_state"])
        optimizer.load_state_dict(resume["optimizer_state"])
        restore_rng(resume["rng_state"])
        start_step = int(resume["step"])
    batches = ScheduledBatchBuilder(lookup, labels, image_root, seed, n)
    started = time.perf_counter()
    model.train()
    for index in range(start_step, len(schedule)):
        step_started = time.perf_counter()
        torch.manual_seed(b23.step_seed(seed, n, index + 1))
        images, targets = batches.batch(schedule[index])
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(images), targets)
        loss.backward()
        optimizer.step()
        label = f"step {index + 1}/{len(schedule)} loss={float(loss):.6f}"
        if ACTIVE_TIMING is not None:
            ACTIVE_TIMING.item_progress(label, time.perf_counter() - step_started, time.perf_counter() - started)
        else:
            print(label, flush=True)
        if midpoint_step is not None and index + 1 == midpoint_step and midpoint_callback is not None:
            midpoint_callback(model, optimizer, capture_rng(), index + 1)
    return model, time.perf_counter() - started


class ArtifactStore:
    def __init__(self, path: Path, header: dict[str, object]):
        self.path = path
        if path.is_file():
            self.data = json.loads(path.read_text())
            existing = self.data.get("header", {})
            operational = {"command", "git_commit"}
            if {k: v for k, v in existing.items() if k not in operational} != {
                k: v for k, v in header.items() if k not in operational
            }:
                raise RuntimeError("B2.4 manifest scientific provenance differs; use --force only for an explicit full restart")
            self.data["header"].update({key: value for key, value in header.items() if key in operational})
        else:
            self.data = {"header": header, "artifacts": {}}
        self.save()

    def save(self) -> None:
        atomic_json(self.path, self.data)

    def record(self, artifact_id: str, record: dict[str, object]) -> None:
        self.data["artifacts"][artifact_id] = record
        self.save()

    def valid_file(self, artifact_id: str, expected: dict[str, object]) -> Path | None:
        record = self.data.get("artifacts", {}).get(artifact_id)
        if not isinstance(record, dict) or record.get("status") != "complete":
            return None
        if any(record.get(key) != value for key, value in expected.items()):
            return None
        path = Path(str(record.get("path", "")))
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            return None
        return path


def artifact_record(path: Path, artifact_type: str, provenance: dict[str, object], seconds: float = 0.0) -> dict[str, object]:
    return {
        "artifact_type": artifact_type,
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "seconds": float(seconds),
        "status": "complete",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **provenance,
    }


def parent_audit(b23_output: Path) -> tuple[dict[tuple, dict[str, float]], dict[str, object]]:
    analysis = _load_module("b24_b23_analysis", B23_ANALYZE_PATH)
    scores, audit = analysis.compatibility_audit(b23_output)
    if audit.get("compatible") is not True or audit.get("test") != "CLOSED":
        raise RuntimeError("B2.3 parent compatibility or TEST closure failed")
    return scores, audit


def load_parent_context(
    manifest_path: Path, b23_output: Path
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object], dict[str, object]]:
    frame = pd.read_csv(manifest_path)
    b23.b20.validate_manifest(frame)
    lookup = frame.set_index("sample_id", drop=False)
    split = pd.read_csv(b23_output / "split_manifest.csv")
    if set(split.role) != {"BASE", "TRANSFER", "VALIDATION"} or split.duplicated(["seed", "sample_id"]).any():
        raise RuntimeError("B2.3 visible split manifest is invalid")
    manifest = json.loads((b23_output / "run_manifest.json").read_text())
    if manifest.get("header", {}).get("test_used") is not False:
        raise RuntimeError("B2.3 TEST closure failed")
    return frame, lookup, manifest, {"split": split, "sha256": sha256_file(b23_output / "split_manifest.csv")}


def validate_image_root(frame: pd.DataFrame, image_root: Path) -> None:
    missing = [str(path) for path in frame.relative_path if not (image_root / str(path)).is_file()]
    if missing:
        preview = ", ".join(missing[:3])
        raise RuntimeError(f"PACS image root is incomplete: {len(missing)} missing files; first: {preview}")


def parent_checkpoint(manifest: dict[str, object], artifact_id: str) -> tuple[dict[str, object], dict[str, object]]:
    record = manifest["artifacts"].get(artifact_id, {})
    path = Path(str(record.get("path", "")))
    if record.get("status") != "complete" or not path.is_file() or sha256_file(path) != record.get("sha256"):
        raise RuntimeError(f"missing or corrupt B2.3 parent {artifact_id}")
    payload = b23.load_checkpoint(path)
    return payload, record


def parent_opportunity(
    manifest: dict[str, object], spec: CaseSpec
) -> tuple[dict[str, object], str, dict[str, object]]:
    artifact_id = f"op_s{spec.seed}_{spec.domain}_n{spec.n}"
    record = manifest["artifacts"].get(artifact_id, {})
    path = Path(str(record.get("path", "")))
    if record.get("status") != "complete" or not path.is_file() or sha256_file(path) != record.get("sha256"):
        raise RuntimeError(f"missing or corrupt B2.3 opportunity {artifact_id}")
    payload, digest = b23.read_envelope(path, {"seed": spec.seed, "domain": spec.domain, "N": spec.n, "test_used": False})
    return payload, digest, record


def parent_std(manifest: dict[str, object], spec: CaseSpec) -> tuple[dict[str, object], dict[str, object]]:
    artifact_id = f"Fi_s{spec.seed}_{spec.domain}_n{spec.n}"
    payload, record = parent_checkpoint(manifest, artifact_id)
    if payload.get("artifact_type") != "singleton" or payload.get("test_used") is not False:
        raise RuntimeError(f"incompatible B2.3 STD {artifact_id}")
    return payload, record


def build_replay_artifact(
    spec: CaseSpec,
    store: ArtifactStore,
    cache: Path,
    lookup: pd.DataFrame,
    f0_payload: dict[str, object],
    f0_record: dict[str, object],
    split_info: dict[str, object],
    seed_opportunity_ids: set[int],
) -> tuple[dict[str, object], str]:
    expected = {
        "artifact_type": "replay",
        "seed": spec.seed,
        "domain": spec.domain,
        "N": spec.n,
        "parent_f0_sha256": f0_record["sha256"],
    }
    path = store.valid_file(spec.replay_id, expected)
    if path:
        return read_envelope(path, expected)
    ids = replay_ids(tuple(int(x) for x in f0_payload["training_ids"]), lookup, spec.seed, spec.domain, spec.n)
    split = split_info["split"]
    roles = {
        int(row.sample_id): str(row.role)
        for row in split.loc[split.seed == spec.seed].itertuples(index=False)
    }
    if any(roles.get(sample_id) != "BASE" for sample_id in ids):
        raise RuntimeError("replay leakage outside BASE")
    if set(ids) & seed_opportunity_ids:
        raise RuntimeError("replay overlaps an opportunity")
    payload = replay_payload(spec, ids, lookup, str(f0_record["sha256"]), str(split_info["sha256"]))
    path = cache / "replay" / f"{spec.replay_id}.json"
    digest = write_envelope(path, payload)
    store.record(spec.replay_id, artifact_record(path, "replay", expected | {"payload_sha256": digest}))
    return payload, digest


def save_checkpoint(path: Path, payload: dict[str, object]) -> None:
    b23.save_checkpoint(path, payload)


def score_model(model: nn.Module, validation: pd.DataFrame, image_root: Path) -> dict[str, float]:
    return b23.score_model(model, validation, image_root, torch.device("cpu"))


def training_payload(
    model: nn.Module,
    spec: CaseSpec,
    method: str,
    scores: dict[str, float],
    f0_record: dict[str, object],
    d_record: dict[str, object],
    opportunity_hash: str,
    replay_hash: str | None,
    audit: dict[str, object],
    validation_ids_sha256: str,
) -> dict[str, object]:
    return {
        "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()},
        "model_fingerprint": b23.state_dict_fingerprint(model),
        "scores": scores,
        "artifact_type": method,
        "seed": spec.seed,
        "domain": spec.domain,
        "N": spec.n,
        "parent_f0_sha256": f0_record["sha256"],
        "deep_sha256": d_record["sha256"],
        "opportunity_sha256": opportunity_hash,
        "replay_sha256": replay_hash,
        "training_seed": b23.derived_training_seed(spec.seed, spec.n),
        "rng_seeds": b23.derived_rng_seeds(spec.seed, spec.n),
        **audit,
        "optimizer": {"class": "SGD", "learning_rate": 0.001, "momentum": 0.9, "weight_decay": 0.0},
        "validation_ids_sha256": validation_ids_sha256,
        "evaluation_split": "validation",
        "device": "cpu",
        "test_used": False,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--image-root", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--b23-output", type=Path, default=DEFAULT_B23_OUTPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def dry_run(args: argparse.Namespace) -> None:
    require_cpu(args.device)
    validate_counts()
    if args.force:
        raise ValueError("--force is incompatible with --dry-run")
    if args.image_root is None or not args.image_root.is_dir():
        raise ValueError("--dry-run requires an accessible --image-root")
    parent_audit(args.b23_output)
    frame, lookup, manifest, split_info = load_parent_context(args.manifest, args.b23_output)
    validate_image_root(frame, args.image_root)
    for spec in plan_cases():
        f0, f0_record = parent_checkpoint(manifest, f"F0_s{spec.seed}")
        opportunity, opportunity_hash, _ = parent_opportunity(manifest, spec)
        parent_std(manifest, spec)
        ids = replay_ids(tuple(int(x) for x in f0["training_ids"]), lookup, spec.seed, spec.domain, spec.n)
        replay = replay_payload(spec, ids, lookup, str(f0_record["sha256"]), str(split_info["sha256"]))
        o50, mixed = build_schedules(spec, tuple(int(x) for x in opportunity["sample_ids"]), replay)
        schedule_audit(spec, "O50", o50, opportunity_hash, None)
        schedule_audit(spec, "REP", mixed[: dose(spec.n)[0]], opportunity_hash, sha256_json(replay))
        schedule_audit(spec, "REP2", mixed, opportunity_hash, sha256_json(replay))
    timing = ExperimentTimingLogger(
        "B2.4 PACS interference-controlled development",
        TOTAL_NEW_FITS,
        {"O50": TOTAL_O50_FITS, "mixed": TOTAL_MIXED_FITS},
        state_path=None,
        resume=False,
        persist=False,
    )
    timing.header(
        [
            "Device: CPU",
            "TEST: CLOSED",
            "B2.3 STD states reused: 60",
            "New fits: 120 (60 O50 + 60 mixed REP->REP2)",
            "New VALIDATION evaluations: 180",
            "Method states: 240 | analytical rows: 1200",
        ]
    )
    print("Dry-run successful.", flush=True)
    print("60 B2.3 STD states compatible and reusable.", flush=True)
    print("60 replay buffers and 60 matched O50/REP schedule pairs planned.", flush=True)
    print("120 new fits planned; REP2 is a continuation, not an extra fit.", flush=True)
    print("180 new VALIDATION evaluations and 1200 method-value rows planned.", flush=True)
    print("TEST remains closed. No training or teacher inference executed.", flush=True)


def run(args: argparse.Namespace) -> None:
    require_cpu(args.device)
    validate_counts()
    if args.dry_run:
        dry_run(args)
        return
    if args.analyze_only:
        analysis = _load_module("b24_analysis", ANALYZE_PATH)
        analysis.run_analysis(args.output_dir, args.b23_output)
        return
    if args.image_root is None or not args.image_root.is_dir():
        raise ValueError("full execution requires an accessible --image-root")
    if args.force and args.output_dir.exists():
        shutil.rmtree(args.output_dir / ".cache", ignore_errors=True)
        for name in (
            "run_manifest.json", "state_metrics.csv", "method_values.csv", "primary_contrasts.csv",
            "competence_contrasts.csv", "classifications.csv", "summary.md", "replay_buffers.jsonl",
            "development_states.jsonl", "exact_regime_classifications.csv", "seed_summaries.csv",
        ):
            (args.output_dir / name).unlink(missing_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache = args.output_dir / ".cache"
    print("[1/6] B2.3 parent compatibility and TEST-closure audit", flush=True)
    parent_audit(args.b23_output)
    frame, lookup, parent_manifest, split_info = load_parent_context(args.manifest, args.b23_output)
    validate_image_root(frame, args.image_root)
    config = json.loads(b23.CONFIG_PATH.read_text())
    b23.validate_config(config)
    header = {
        "protocol_id": PROTOCOL_ID,
        "frozen_protocol_commit": FROZEN_PROTOCOL_COMMIT,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "implementation_sha256": sha256_file(Path(__file__)),
        "analysis_sha256": sha256_file(ANALYZE_PATH),
        "b23_protocol_id": b23.PROTOCOL_ID,
        "b23_manifest_sha256": sha256_file(args.b23_output / "run_manifest.json"),
        "b23_split_manifest_sha256": split_info["sha256"],
        "dataset_revision": b23.DATASET_REVISION,
        "device": "cpu",
        "test_used": False,
        "seeds": list(SEEDS),
        "domains": list(DOMAINS),
        "N": list(N_VALUES),
        "costs": list(COSTS),
        "command": " ".join(sys.argv),
    }
    store = ArtifactStore(args.output_dir / "run_manifest.json", header)
    timing = ExperimentTimingLogger(
        "B2.4 PACS interference-controlled development",
        TOTAL_NEW_FITS,
        {"O50": TOTAL_O50_FITS, "mixed": TOTAL_MIXED_FITS},
        state_path=cache / "experiment_timing.json",
        resume=not args.force,
    )
    global ACTIVE_TIMING
    ACTIVE_TIMING = timing
    timing.header(
        [
            "Device: CPU", "TEST: CLOSED", "B2.3 STD reused: 60",
            "New fits: 120 | new VALIDATION evaluations: 180", "Method-value rows: 1200",
        ]
    )
    opportunity_ids_by_seed = {
        seed: {
            int(value)
            for spec in plan_cases()
            if spec.seed == seed
            for value in parent_opportunity(parent_manifest, spec)[0]["sample_ids"]
        }
        for seed in SEEDS
    }
    print("[2/6] Deterministic replay buffers", flush=True)
    replay_records: dict[tuple[int, str, int], tuple[dict[str, object], str]] = {}
    for spec in plan_cases():
        f0, f0_record = parent_checkpoint(parent_manifest, f"F0_s{spec.seed}")
        replay_records[spec.key] = build_replay_artifact(
            spec, store, cache, lookup, f0, f0_record, split_info, opportunity_ids_by_seed[spec.seed]
        )

    split = split_info["split"]
    print("[3/6] O50 equal-compute controls", flush=True)
    for spec in plan_cases():
        f0, f0_record = parent_checkpoint(parent_manifest, f"F0_s{spec.seed}")
        _, d_record = parent_checkpoint(parent_manifest, f"D_s{spec.seed}")
        opportunity, opportunity_hash, _ = parent_opportunity(parent_manifest, spec)
        parent_std(parent_manifest, spec)
        replay, replay_hash = replay_records[spec.key]
        o50_schedule, mixed_schedule = build_schedules(
            spec, tuple(int(x) for x in opportunity["sample_ids"]), replay
        )
        o50_audit = schedule_audit(spec, "O50", o50_schedule, opportunity_hash, None)
        rep_audit = schedule_audit(spec, "REP", mixed_schedule[: dose(spec.n)[0]], opportunity_hash, replay_hash)
        if o50_audit["opportunity_projection_sha256"] != rep_audit["opportunity_projection_sha256"]:
            raise RuntimeError("O50/REP opportunity projection hash differs")
        expected = {
            "artifact_type": "O50", "seed": spec.seed, "domain": spec.domain, "N": spec.n,
            "parent_f0_sha256": f0_record["sha256"], "opportunity_sha256": opportunity_hash,
            "opportunity_projection_sha256": o50_audit["opportunity_projection_sha256"],
        }
        if store.valid_file(spec.o50_id, expected):
            record = store.data["artifacts"][spec.o50_id]
            timing.adopt_completed(spec.o50_id, "O50", float(record.get("seconds", 0.0)), spec.o50_id)
            continue
        labels = {int(row["sample_id"]): int(row["pseudo_label"]) for row in opportunity["samples"]}
        validation_ids = tuple(
            int(x) for x in split.loc[(split.seed == spec.seed) & (split.role == "VALIDATION"), "sample_id"]
        )
        validation = lookup.loc[list(validation_ids)].reset_index(drop=True)
        description = f"seed={spec.seed} method=O50 domain={spec.domain} N={spec.n}"
        timing.start_item(spec.o50_id, "O50", spec.number, description)
        model, seconds = train_scheduled(
            f0["model_state"], o50_schedule, labels, lookup, args.image_root, spec.seed, spec.n, config
        )
        scores = score_model(model, validation, args.image_root)
        payload = training_payload(
            model, spec, "O50", scores, f0_record, d_record, opportunity_hash, None,
            o50_audit, sha256_json(list(validation_ids)),
        )
        path = cache / "states" / f"{spec.o50_id}.pt"
        save_checkpoint(path, payload)
        store.record(spec.o50_id, artifact_record(path, "O50", expected | {"model_fingerprint": payload["model_fingerprint"]}, seconds))
        timing.finish_item(description=description)
        del model

    print("[4/6] REP and continuing REP2 trajectories", flush=True)
    for spec in plan_cases():
        f0, f0_record = parent_checkpoint(parent_manifest, f"F0_s{spec.seed}")
        _, d_record = parent_checkpoint(parent_manifest, f"D_s{spec.seed}")
        opportunity, opportunity_hash, _ = parent_opportunity(parent_manifest, spec)
        replay, replay_hash = replay_records[spec.key]
        o50_schedule, mixed_schedule = build_schedules(
            spec, tuple(int(x) for x in opportunity["sample_ids"]), replay
        )
        steps, _ = dose(spec.n)
        rep_audit = schedule_audit(spec, "REP", mixed_schedule[:steps], opportunity_hash, replay_hash)
        rep2_audit = schedule_audit(spec, "REP2", mixed_schedule, opportunity_hash, replay_hash)
        trajectory_id = f"mixed_s{spec.seed}_{spec.domain}_n{spec.n}"
        common = {
            "seed": spec.seed, "domain": spec.domain, "N": spec.n,
            "parent_f0_sha256": f0_record["sha256"], "opportunity_sha256": opportunity_hash,
            "replay_sha256": replay_hash, "trajectory_id": trajectory_id,
        }
        rep_expected = {"artifact_type": "REP", **common, "step": steps}
        rep2_expected = {"artifact_type": "REP2", **common, "step": 2 * steps}
        rep_path = store.valid_file(spec.rep_id, rep_expected)
        rep2_path = store.valid_file(spec.rep2_id, rep2_expected)
        if rep_path and rep2_path:
            record = store.data["artifacts"][spec.rep2_id]
            timing.adopt_completed(trajectory_id, "mixed", float(record.get("seconds", 0.0)), trajectory_id)
            continue
        resume = b23.load_checkpoint(rep_path) if rep_path else None
        labels = {int(row["sample_id"]): int(row["pseudo_label"]) for row in opportunity["samples"]}
        labels.update({int(row["sample_id"]): int(row["label"]) for row in replay["samples"]})
        validation_ids = tuple(
            int(x) for x in split.loc[(split.seed == spec.seed) & (split.role == "VALIDATION"), "sample_id"]
        )
        validation = lookup.loc[list(validation_ids)].reset_index(drop=True)
        rep_checkpoint = cache / "states" / f"{spec.rep_id}.pt"

        def save_rep(model, optimizer, rng_state, step):
            optimizer_state = optimizer.state_dict()
            payload = {
                "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()},
                "optimizer_state": optimizer_state, "rng_state": rng_state, "step": step,
                "model_fingerprint": b23.state_dict_fingerprint(model), "artifact_type": "REP",
                **common, **rep_audit, "training_seed": b23.derived_training_seed(spec.seed, spec.n),
                "optimizer_state_sha256": b23.sha256_torch_object(optimizer_state),
                "rng_state_sha256": b23.sha256_torch_object(rng_state), "test_used": False,
            }
            save_checkpoint(rep_checkpoint, payload)
            store.record(spec.rep_id, artifact_record(rep_checkpoint, "REP", rep_expected | {"model_fingerprint": payload["model_fingerprint"]}))

        description = f"seed={spec.seed} method=REP->REP2 domain={spec.domain} N={spec.n}"
        timing.start_item(trajectory_id, "mixed", TOTAL_O50_FITS + spec.number, description)
        model, seconds = train_scheduled(
            f0["model_state"], mixed_schedule, labels, lookup, args.image_root, spec.seed, spec.n, config,
            resume=resume, midpoint_step=steps, midpoint_callback=save_rep,
        )
        if not rep_checkpoint.is_file():
            raise RuntimeError("REP midpoint was not saved")
        rep_payload = b23.load_checkpoint(rep_checkpoint)
        rep_model = b23.b20.make_model("fast", b23.derived_training_seed(spec.seed, spec.n), torch.device("cpu"), pretrained=False)
        rep_model.load_state_dict(rep_payload["model_state"])
        rep_scores = score_model(rep_model, validation, args.image_root)
        rep_payload.update(
            {
                "scores": rep_scores, "deep_sha256": d_record["sha256"],
                "validation_ids_sha256": sha256_json(list(validation_ids)), "evaluation_split": "validation",
                "device": "cpu", "test_used": False,
            }
        )
        save_checkpoint(rep_checkpoint, rep_payload)
        store.record(spec.rep_id, artifact_record(rep_checkpoint, "REP", rep_expected | {"model_fingerprint": rep_payload["model_fingerprint"]}))
        rep2_scores = score_model(model, validation, args.image_root)
        rep2_payload = training_payload(
            model, spec, "REP2", rep2_scores, f0_record, d_record, opportunity_hash, replay_hash,
            rep2_audit, sha256_json(list(validation_ids)),
        )
        rep2_payload.update({"step": 2 * steps, "trajectory_id": trajectory_id, "rep_checkpoint_sha256": sha256_file(rep_checkpoint)})
        rep2_checkpoint = cache / "states" / f"{spec.rep2_id}.pt"
        save_checkpoint(rep2_checkpoint, rep2_payload)
        store.record(spec.rep2_id, artifact_record(rep2_checkpoint, "REP2", rep2_expected | {"model_fingerprint": rep2_payload["model_fingerprint"]}, seconds))
        timing.finish_item(description=description)
        del model, rep_model

    print("[5/6] Preregistered analysis", flush=True)
    analysis = _load_module("b24_analysis", ANALYZE_PATH)
    analysis_started = time.perf_counter()
    result = analysis.run_analysis(args.output_dir, args.b23_output)
    timing.record_auxiliary("analysis", "analysis", time.perf_counter() - analysis_started)
    print("[6/6] Validated outputs", flush=True)
    timing.finish(
        title="B2.4 COMPLETE",
        extra_lines=[
            "TEST: CLOSED", "Compatibility: PASS", f"New fits: {TOTAL_NEW_FITS}/{TOTAL_NEW_FITS}",
            f"New VALIDATION evaluations: {TOTAL_NEW_EVALUATIONS}/{TOTAL_NEW_EVALUATIONS}",
            f"Method-value rows: {len(result['method_values'])}/{TOTAL_METHOD_VALUE_ROWS}",
            f"Detailed results: {args.output_dir / 'summary.md'}",
        ],
    )
    ACTIVE_TIMING = None


if __name__ == "__main__":
    try:
        run(parse_args())
    except BaseException as error:
        if ACTIVE_TIMING is not None:
            ACTIVE_TIMING.interrupt(RESTART_COMMAND, error)
        raise
