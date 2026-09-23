"""Run the preregistered B2.2 PACS operational opportunity-value experiment."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = ROOT / "docs/experimental_foundations/B22_PROTOCOL.md"
CONFIG_PATH = ROOT / "experiments/pilots/b2_pacs_calibration/config.json"
B20_RUN_PATH = ROOT / "experiments/pilots/b2_pacs_calibration/run.py"
DEFAULT_MANIFEST = ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv"
DEFAULT_OUTPUT = ROOT / "results/pilots/b22_opportunity_value"


def _load_b20():
    spec = importlib.util.spec_from_file_location("hls_b20_pacs_run", B20_RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the B2.0 PACS runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


b20 = _load_b20()

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
SEEDS = (0, 1, 2, 3, 4)
N_VALUES = (25, 50, 100)
COSTS = (0.00, 0.02, 0.05, 0.10, 0.15)
FUTURE_WEIGHTS = (1, 2, 5, 10)
KAPPA = 0.0
F0_FRACTION = 0.25
TOTAL_UPDATES = len(SEEDS) * len(DOMAINS) * len(N_VALUES)
TOTAL_GRID_ROWS = TOTAL_UPDATES * len(COSTS) * len(FUTURE_WEIGHTS)
NUMERIC_TOLERANCE = 1e-12
PROTOCOL_ID = "B2.2-PACS-opportunity-value-v1"
OUTPUT_FILES = (
    "raw_results.csv",
    "aggregate_results.csv",
    "decision_regions.csv",
    "representative_cases.csv",
    "analysis_summary.md",
    "run_metadata.json",
)


@dataclass(frozen=True)
class DevelopmentSplits:
    """B2.2-visible split IDs. TEST has no field and cannot be requested."""

    base: tuple[int, ...]
    transfer: tuple[int, ...]
    validation: tuple[int, ...]


@dataclass(frozen=True)
class UpdateSpec:
    number: int
    seed: int
    domain: str
    n: int
    selected_ids: tuple[int, ...]
    training_seed: int

    @property
    def update_id(self) -> str:
        return f"seed{self.seed}_{self.domain}_N{self.n}"


@dataclass(frozen=True)
class RunSignatures:
    protocol_sha256: str
    config_sha256: str
    manifest_sha256: str
    implementation_sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def state_dict_fingerprint(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        array = tensor.detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(array.dtype).encode())
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.numpy().tobytes())
    return digest.hexdigest()


def ids_fingerprint(ids: tuple[int, ...] | list[int]) -> str:
    return sha256_json([int(value) for value in ids])


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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


def print_header() -> None:
    print("=" * 60, flush=True)
    print("B2.2 PACS opportunity-value experiment", flush=True)
    print("Device: CPU", flush=True)
    print(f"Seeds: {len(SEEDS)}", flush=True)
    print(f"Domains: {len(DOMAINS)}", flush=True)
    print(f"N: {list(N_VALUES)}", flush=True)
    print(f"Opportunity updates: {TOTAL_UPDATES}", flush=True)
    print(f"Analytical grid rows: {TOTAL_GRID_ROWS}", flush=True)
    print("TEST: CLOSED", flush=True)
    print("=" * 60, flush=True)


def phase(number: int, label: str, started: float) -> None:
    print(f"[{number}/7] {label} | elapsed {format_duration(time.perf_counter() - started)}", flush=True)


def require_cpu(requested: str) -> torch.device:
    if requested != "cpu":
        raise ValueError("B2.2 is CPU ONLY; --device must be cpu")
    return torch.device("cpu")


def validate_protocol_and_config(config: dict) -> None:
    protocol = PROTOCOL_PATH.read_text()
    required_fragments = (
        "N\\in\\{25,50,100\\}",
        "c\\in\\{0,0.02,0.05,0.10,0.15\\}",
        "B\\in\\{1,2,5,10\\}",
        "\\qquad \\kappa=0",
        "\\rho_k(c)>0\\quad\\text{and}\\quad H_k(c,B,\\kappa)>0",
        "TEST remains closed and inaccessible",
    )
    missing = [fragment for fragment in required_fragments if fragment not in protocol]
    if missing:
        raise RuntimeError(f"B22_PROTOCOL.md no longer matches the implementation: {missing}")
    if tuple(config["split_seeds"]) != SEEDS:
        raise RuntimeError("B2.0/B2.1 seed configuration does not match B2.2")
    if tuple(config["competence_domains"]) != DOMAINS:
        raise RuntimeError("PACS domains do not match B2.2")
    if int(config["training"]["epochs"]) != 3:
        raise RuntimeError("B2.2 requires the unchanged three-epoch update")
    if config["fast"]["architecture"] != "torchvision.models.mobilenet_v2":
        raise RuntimeError("Fast model does not match B2.2")
    if config["deep"]["architecture"] != "torchvision.models.resnet50":
        raise RuntimeError("Deep model does not match B2.2")
    if TOTAL_UPDATES != 60 or TOTAL_GRID_ROWS != 1200 or KAPPA != 0.0:
        raise RuntimeError("frozen B2.2 grid cardinality changed")


def development_splits(frame: pd.DataFrame, seed: int) -> DevelopmentSplits:
    """Create the exact B2.1 split, exposing only development-visible roles."""
    all_splits = b20.stratified_splits(frame, seed)
    visible = DevelopmentSplits(
        base=tuple(int(x) for x in all_splits["base"]),
        transfer=tuple(int(x) for x in all_splits["transfer"]),
        validation=tuple(int(x) for x in all_splits["validation"]),
    )
    arrays = [np.asarray(getattr(visible, name), dtype=int) for name in ("base", "transfer", "validation")]
    for index, left in enumerate(arrays):
        for right in arrays[index + 1 :]:
            if np.intersect1d(left, right).size:
                raise RuntimeError("BASE/TRANSFER/VALIDATION overlap")
    return visible


def select_examples(frame: pd.DataFrame, domain: str, n: int, seed: int) -> pd.DataFrame:
    subset = frame[frame.domain == domain].sort_values("sample_id")
    if len(subset) < n:
        raise ValueError(f"domain {domain} has only {len(subset)} TRANSFER examples; N={n} is infeasible")
    selected = subset.sample(n=n, random_state=seed).sort_values("sample_id").reset_index(drop=True)
    if len(selected) != n or set(selected.domain) != {domain}:
        raise RuntimeError("opportunity selection violated domain or N")
    return selected


def build_plan(frame: pd.DataFrame, splits: dict[int, DevelopmentSplits]) -> list[UpdateSpec]:
    lookup = frame.set_index("sample_id", drop=False)
    plan: list[UpdateSpec] = []
    number = 0
    for seed in SEEDS:
        transfer = lookup.loc[list(splits[seed].transfer)].reset_index(drop=True)
        for n in N_VALUES:
            for domain_index, domain in enumerate(DOMAINS):
                number += 1
                selection_seed = seed * 10000 + n * 100 + domain_index
                chosen = select_examples(transfer, domain, n, selection_seed)
                plan.append(
                    UpdateSpec(
                        number=number,
                        seed=seed,
                        domain=domain,
                        n=n,
                        selected_ids=tuple(int(x) for x in chosen.sample_id),
                        training_seed=seed + n + domain_index,
                    )
                )
    if len(plan) != TOTAL_UPDATES or len({spec.update_id for spec in plan}) != TOTAL_UPDATES:
        raise RuntimeError("B2.2 plan must contain exactly 60 unique updates")
    return plan


def fast_trajectory_record(spec: UpdateSpec, f0_fingerprint: str, operational_example_count: int) -> dict[str, object]:
    """Record a=F without accepting a teacher or a teacher-query callback."""
    if operational_example_count != spec.n:
        raise RuntimeError(f"Fast processed {operational_example_count} examples; expected {spec.n}")
    return {
        "action": "F",
        "development_actions": [0],
        "selected_ids": list(spec.selected_ids),
        "operational_example_count": operational_example_count,
        "teacher_query_count": 0,
        "pseudo_label_count": 0,
        "student_updated": False,
        "initial_f0_fingerprint": f0_fingerprint,
        "final_fingerprint": f0_fingerprint,
    }


def deep_opportunity_record(
    spec: UpdateSpec,
    selected: pd.DataFrame,
    query_teacher: Callable[[pd.DataFrame], list[int]],
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Create the a=D,d=1 opportunity using exactly the selected N examples."""
    if tuple(int(x) for x in selected.sample_id) != spec.selected_ids:
        raise RuntimeError("teacher query frame does not match the preregistered selected IDs")
    pseudo_labels = [int(value) for value in query_teacher(selected)]
    if len(pseudo_labels) != spec.n:
        raise RuntimeError(f"Deep returned {len(pseudo_labels)} pseudo-labels; expected {spec.n}")
    opportunity = selected.copy()
    opportunity["label"] = pseudo_labels
    record = {
        "action": "D",
        "development_action": 1,
        "selected_ids": list(spec.selected_ids),
        "selected_ids_sha256": ids_fingerprint(spec.selected_ids),
        "teacher_query_count": spec.n,
        "pseudo_label_count": len(pseudo_labels),
        "student_updated": True,
        "parent_state": "F0",
    }
    return opportunity, record


def score_model(model: nn.Module, frame: pd.DataFrame, image_root: Path, device: torch.device, batch_size: int) -> dict[str, float]:
    labels, predictions, domains, _ = b20.evaluate(model, frame, image_root, device, batch_size)
    metrics = b20.domain_metrics(labels, predictions, domains)
    return {domain: float(metrics[domain]["balanced_accuracy"]) for domain in DOMAINS}


def predict_labels(model: nn.Module, frame: pd.DataFrame, image_root: Path, device: torch.device, batch_size: int) -> list[int]:
    _, predictions, _, sample_ids = b20.evaluate(model, frame, image_root, device, batch_size)
    if sample_ids.tolist() != frame.sample_id.astype(int).tolist():
        raise RuntimeError("teacher prediction order differs from selected opportunity IDs")
    return [int(value) for value in predictions]


def process_fast_batch(model: nn.Module, frame: pd.DataFrame, image_root: Path, device: torch.device, batch_size: int) -> int:
    """Execute a=F on the selected batch without creating a transfer label."""
    _, _, _, sample_ids = b20.evaluate(model, frame, image_root, device, batch_size)
    if sample_ids.tolist() != frame.sample_id.astype(int).tolist():
        raise RuntimeError("Fast operational order differs from selected task IDs")
    return len(sample_ids)


def train_model(
    model: nn.Module,
    frame: pd.DataFrame,
    training_seed: int,
    learning_rate: float,
    momentum: float,
    config: dict,
    image_root: Path,
    device: torch.device,
    label: str,
) -> tuple[nn.Module, list[dict[str, float]], float]:
    b20.seed_everything(training_seed)
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)
    loader = DataLoader(
        b20.PACSImages(frame, image_root, training=True),
        batch_size=int(config["training"]["batch_size"]),
        shuffle=True,
        num_workers=int(config["training"]["workers"]),
        generator=torch.Generator().manual_seed(training_seed),
        pin_memory=False,
    )
    epochs = int(config["training"]["epochs"])
    started = time.perf_counter()
    history: list[dict[str, float]] = []
    model.train()
    for epoch in range(1, epochs + 1):
        epoch_started = time.perf_counter()
        loss_sum = 0.0
        examples = 0
        for images, labels, _, _ in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = nn.functional.cross_entropy(model(images), labels)
            loss.backward()
            optimizer.step()
            loss_sum += float(loss.detach()) * len(labels)
            examples += len(labels)
        epoch_seconds = time.perf_counter() - epoch_started
        mean_loss = loss_sum / examples
        history.append({"epoch": epoch, "loss": mean_loss, "seconds": epoch_seconds})
        print(
            f"epoch {epoch}/{epochs} | loss={mean_loss:.6f} | epoch time={format_duration(epoch_seconds)} "
            f"| update elapsed={format_duration(time.perf_counter() - started)} | {label}",
            flush=True,
        )
    return model, history, time.perf_counter() - started


def train_base(
    kind: str,
    seed: int,
    frame: pd.DataFrame,
    config: dict,
    image_root: Path,
    device: torch.device,
) -> tuple[nn.Module, list[dict[str, float]], float]:
    model_seed = seed + 30000 if kind == "deep" else seed + 2500
    model = b20.make_model(kind, model_seed, device)
    learning_rate = float(config[kind]["learning_rate"])
    return train_model(
        model,
        frame,
        model_seed,
        learning_rate,
        float(config[kind]["momentum"]),
        config,
        image_root,
        device,
        f"base {kind} seed={seed}",
    )


def train_from_f0(
    f0: nn.Module,
    opportunity: pd.DataFrame,
    spec: UpdateSpec,
    config: dict,
    image_root: Path,
    device: torch.device,
) -> tuple[nn.Module, list[dict[str, float]], float, str]:
    initial_fingerprint = state_dict_fingerprint(f0)
    model = copy.deepcopy(f0)
    if state_dict_fingerprint(model) != initial_fingerprint:
        raise RuntimeError("F_k did not start from an exact copy of F0")
    model, history, seconds = train_model(
        model,
        opportunity,
        spec.training_seed,
        float(config["fast"]["learning_rate"]),
        float(config["fast"]["momentum"]),
        config,
        image_root,
        device,
        spec.update_id,
    )
    return model, history, seconds, initial_fingerprint


def _base_metadata(kind: str, seed: int, signatures: RunSignatures) -> dict[str, object]:
    return {
        "protocol_id": PROTOCOL_ID,
        "kind": kind,
        "seed": seed,
        "device": "cpu",
        "f0_fraction": F0_FRACTION,
        **asdict(signatures),
    }


def save_base_checkpoint(path: Path, model: nn.Module, scores: dict[str, float], metadata: dict[str, object], seconds: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": metadata,
        "scores": scores,
        "seconds": float(seconds),
        "state_dict_fingerprint": state_dict_fingerprint(model),
        "state_dict": {name: value.detach().cpu() for name, value in model.state_dict().items()},
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, temporary)
    os.replace(temporary, path)


def load_base_checkpoint(path: Path, kind: str, seed: int, signatures: RunSignatures, device: torch.device) -> tuple[nn.Module, dict[str, float], float]:
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if payload.get("metadata") != _base_metadata(kind, seed, signatures):
        raise RuntimeError(f"incompatible restart checkpoint: {path}; use --force")
    model_seed = seed + 30000 if kind == "deep" else seed + 2500
    model = b20.make_model(kind, model_seed, device, pretrained=False)
    model.load_state_dict(payload["state_dict"])
    if state_dict_fingerprint(model) != payload.get("state_dict_fingerprint"):
        raise RuntimeError(f"corrupt restart checkpoint: {path}; use --force")
    scores = {domain: float(payload["scores"][domain]) for domain in DOMAINS}
    return model, scores, float(payload.get("seconds", 0.0))


def expected_update_metadata(spec: UpdateSpec, signatures: RunSignatures) -> dict[str, object]:
    return {
        "protocol_id": PROTOCOL_ID,
        "update_id": spec.update_id,
        "seed": spec.seed,
        "domain": spec.domain,
        "N": spec.n,
        "training_seed": spec.training_seed,
        "selected_ids": list(spec.selected_ids),
        "selected_ids_sha256": ids_fingerprint(spec.selected_ids),
        "parent_state": "F0",
        "device": "cpu",
        **asdict(signatures),
    }


def validate_update_artifact(record: dict[str, object], spec: UpdateSpec, signatures: RunSignatures) -> None:
    if record.get("metadata") != expected_update_metadata(spec, signatures):
        raise RuntimeError(f"incompatible restart artifact for {spec.update_id}; use --force")
    fast = record.get("fast_trajectory", {})
    deep = record.get("deep_trajectory", {})
    if fast.get("operational_example_count") != spec.n:
        raise RuntimeError(f"Fast did not process exactly N operational examples for {spec.update_id}")
    if fast.get("teacher_query_count") != 0 or fast.get("pseudo_label_count") != 0 or fast.get("student_updated") is not False:
        raise RuntimeError(f"invalid Fast trajectory artifact for {spec.update_id}")
    if fast.get("selected_ids") != list(spec.selected_ids) or fast.get("final_fingerprint") != record.get("initial_f0_fingerprint"):
        raise RuntimeError(f"invalid Fast trajectory provenance for {spec.update_id}")
    if deep.get("teacher_query_count") != spec.n or deep.get("pseudo_label_count") != spec.n:
        raise RuntimeError(f"invalid Deep opportunity artifact for {spec.update_id}")
    if deep.get("selected_ids") != list(spec.selected_ids) or deep.get("selected_ids_sha256") != ids_fingerprint(spec.selected_ids):
        raise RuntimeError(f"invalid Deep opportunity provenance for {spec.update_id}")
    if deep.get("parent_state") != "F0" or record.get("parent_state") != "F0":
        raise RuntimeError(f"sequential update detected for {spec.update_id}")
    for name in ("F0_scores", "Fk_scores", "D_scores"):
        scores = record.get(name, {})
        if set(scores) != set(DOMAINS) or not all(np.isfinite(float(value)) for value in scores.values()):
            raise RuntimeError(f"invalid {name} in {spec.update_id}")
    if record.get("initial_f0_fingerprint") != record.get("fast_trajectory", {}).get("initial_f0_fingerprint"):
        raise RuntimeError(f"F and D trajectories did not reference the same F0 for {spec.update_id}")
    if record.get("test_used") is not False or record.get("evaluated_split") != "validation":
        raise RuntimeError(f"TEST closure or evaluation split invalid for {spec.update_id}")


def load_completed_updates(cache_dir: Path, plan: list[UpdateSpec], signatures: RunSignatures, force: bool) -> dict[str, dict[str, object]]:
    if force:
        return {}
    records: dict[str, dict[str, object]] = {}
    update_dir = cache_dir / "updates"
    for spec in plan:
        path = update_dir / f"{spec.update_id}.json"
        if path.exists():
            record = json.loads(path.read_text())
            validate_update_artifact(record, spec, signatures)
            records[spec.update_id] = record
    return records


def write_restart_state(cache_dir: Path, records: dict[str, dict[str, object]], signatures: RunSignatures) -> None:
    atomic_json(
        cache_dir / "restart_state.json",
        {
            "protocol_id": PROTOCOL_ID,
            "completed_updates": sorted(records),
            "completed_count": len(records),
            "update_seconds": {key: float(value["update_seconds"]) for key, value in records.items()},
            **asdict(signatures),
        },
    )


def reset_outputs(output_dir: Path, cache_dir: Path) -> None:
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            path.unlink()
    figures = output_dir / "figures"
    if figures.exists():
        shutil.rmtree(figures)


def execute_training_phase(dry_run: bool, callback: Callable[[], object]) -> object | None:
    """Single guard used by tests to prove that dry-run cannot train."""
    if dry_run:
        return None
    return callback()


def operational_value(scores: dict[str, float], deep: dict[str, float], cost: float) -> float:
    return float(np.mean([max(float(scores[domain]), float(deep[domain]) - cost) for domain in DOMAINS]))


def analytical_row(record: dict[str, object], cost: float, future_weight: int) -> dict[str, object]:
    metadata = record["metadata"]
    domain = str(metadata["domain"])
    f0 = {key: float(value) for key, value in record["F0_scores"].items()}
    fk = {key: float(value) for key, value in record["Fk_scores"].items()}
    deep = {key: float(value) for key, value in record["D_scores"].items()}
    u_f = f0[domain]
    u_d = deep[domain] - cost
    rho = u_f - u_d
    contributions = {
        key: 0.25 * (max(fk[key], deep[key] - cost) - max(f0[key], deep[key] - cost)) for key in DOMAINS
    }
    v_f0 = operational_value(f0, deep, cost)
    v_fk = operational_value(fk, deep, cost)
    delta_v = v_fk - v_f0
    if not np.isclose(delta_v, sum(contributions.values()), atol=NUMERIC_TOLERANCE, rtol=0):
        raise RuntimeError(f"DeltaV decomposition failed for {metadata['update_id']}")
    delta_local = contributions[domain]
    delta_cross = sum(value for key, value in contributions.items() if key != domain)
    if not np.isclose(delta_local + delta_cross, delta_v, atol=NUMERIC_TOLERANCE, rtol=0):
        raise RuntimeError(f"local/cross decomposition failed for {metadata['update_id']}")
    omega = -KAPPA + future_weight * delta_v
    h_value = -rho + omega
    integration = bool(rho > 0.0 and h_value > 0.0)
    frontier_equivalent = bool(rho > 0.0 and future_weight * delta_v > rho + KAPPA)
    if integration != frontier_equivalent:
        raise RuntimeError(f"strict primary-test equivalence failed for {metadata['update_id']}")
    current_action = "F" if rho > 0 else "D" if rho < 0 else "TIE"
    total_action = "D+learning" if h_value > 0 else "F" if h_value < 0 else "TIE"
    row: dict[str, object] = {
        "update_id": metadata["update_id"],
        "seed": int(metadata["seed"]),
        "domain": domain,
        "N": int(metadata["N"]),
        "c": float(cost),
        "B": int(future_weight),
        "kappa": KAPPA,
        "selected_ids_sha256": metadata["selected_ids_sha256"],
        "selected_ids": json.dumps(metadata["selected_ids"]),
        "initial_f0_fingerprint": record["initial_f0_fingerprint"],
        "Fk_fingerprint": record["Fk_fingerprint"],
        "S_F0": json.dumps(f0, sort_keys=True),
        "S_Fk": json.dumps(fk, sort_keys=True),
        "S_D": json.dumps(deep, sort_keys=True),
        "fast_teacher_query_count": int(record["fast_trajectory"]["teacher_query_count"]),
        "fast_pseudo_label_count": int(record["fast_trajectory"]["pseudo_label_count"]),
        "fast_operational_example_count": int(record["fast_trajectory"]["operational_example_count"]),
        "deep_teacher_query_count": int(record["deep_trajectory"]["teacher_query_count"]),
        "deep_pseudo_label_count": int(record["deep_trajectory"]["pseudo_label_count"]),
        "parent_state": record["parent_state"],
        "U_F": u_f,
        "U_D": u_d,
        "rho": rho,
        "V_F0": v_f0,
        "V_Fk": v_fk,
        "DeltaV": delta_v,
        "Omega": omega,
        "H": h_value,
        "DeltaV_local": delta_local,
        "DeltaV_cross": delta_cross,
        "current_preferred_action": current_action,
        "total_value_preferred_action": total_action,
        "integration_changes_decision": integration,
        "frontier_equivalent": frontier_equivalent,
    }
    for key in DOMAINS:
        row[f"F0_ba_{key}"] = f0[key]
        row[f"Fk_ba_{key}"] = fk[key]
        row[f"D_ba_{key}"] = deep[key]
        row[f"DeltaV_contribution_{key}"] = contributions[key]
    return row


def expand_grid(records: dict[str, dict[str, object]]) -> pd.DataFrame:
    rows = [
        analytical_row(record, cost, future_weight)
        for record in records.values()
        for cost in COSTS
        for future_weight in FUTURE_WEIGHTS
    ]
    result = pd.DataFrame(rows).sort_values(["seed", "N", "domain", "c", "B"]).reset_index(drop=True)
    if len(result) != TOTAL_GRID_ROWS or result.duplicated(["seed", "domain", "N", "c", "B"]).any():
        raise RuntimeError("analytical grid must contain exactly 1,200 unique observations")
    if not (result.integration_changes_decision == result.frontier_equivalent).all():
        raise RuntimeError("primary test and exact frontier differ")
    return result


def aggregate_results(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched = raw.assign(noncompensating=(raw.rho > 0) & (raw.H <= 0))
    grouped = enriched.groupby(["domain", "N", "c", "B"], as_index=False)
    aggregate = grouped.agg(
        n_seeds=("seed", "nunique"),
        n_integration_changes=("integration_changes_decision", "sum"),
        n_current_fast=("rho", lambda values: int((values > 0).sum())),
        n_noncompensating=("noncompensating", "sum"),
        mean_rho=("rho", "mean"),
        std_rho=("rho", "std"),
        mean_DeltaV=("DeltaV", "mean"),
        std_DeltaV=("DeltaV", "std"),
        mean_H=("H", "mean"),
        std_H=("H", "std"),
        mean_DeltaV_local=("DeltaV_local", "mean"),
        mean_DeltaV_cross=("DeltaV_cross", "mean"),
    )
    if not (aggregate.n_seeds == len(SEEDS)).all():
        raise RuntimeError("aggregate cells must contain exactly five seeds")
    regions = aggregate.copy()
    regions["integration_reproducible"] = regions.n_integration_changes >= 2
    regions["noncompensating_reproducible"] = regions.n_noncompensating >= 2
    regions["region"] = np.select(
        [regions.integration_reproducible, regions.noncompensating_reproducible],
        ["INTEGRATION_CHANGES_DECISION", "CURRENT_SACRIFICE_NOT_COMPENSATED"],
        default="NO_REPRODUCIBLE_PRIMARY_REGION",
    )
    return aggregate, regions


def classify_outcome(raw: pd.DataFrame, decision_regions: pd.DataFrame) -> str:
    any_favorable = bool(raw.integration_changes_decision.any())
    favorable_reproducible = bool(decision_regions.integration_reproducible.any())
    noncomp_reproducible = bool(decision_regions.noncompensating_reproducible.any())
    if favorable_reproducible and noncomp_reproducible:
        return "POSITIVE"
    if not any_favorable:
        return "NULL"
    return "INCONCLUSIVE"


def representative_cases(raw: pd.DataFrame) -> pd.DataFrame:
    eligible = raw[raw.rho > 0].copy()
    cases: list[dict[str, object]] = []

    def add(label: str, row: pd.Series) -> None:
        record = row.to_dict()
        record["case"] = label
        cases.append(record)

    if len(eligible):
        add("largest_H_with_rho_positive", eligible.sort_values(["H", "seed", "domain", "N", "c", "B"], ascending=[False, True, True, True, True, True]).iloc[0])
        add("smallest_H_with_rho_positive", eligible.sort_values(["H", "seed", "domain", "N", "c", "B"]).iloc[0])
        positive = eligible[eligible.H > 0].assign(distance=lambda x: x.H.abs())
        if len(positive):
            add("positive_nearest_frontier", positive.sort_values(["distance", "seed", "domain", "N", "c", "B"]).iloc[0])
        nonpositive = eligible[eligible.H <= 0].assign(distance=lambda x: x.H.abs())
        if len(nonpositive):
            add("nonpositive_nearest_frontier", nonpositive.sort_values(["distance", "seed", "domain", "N", "c", "B"]).iloc[0])
        crossing_groups = []
        for key, group in eligible.groupby(["seed", "domain", "N", "c"]):
            if group.integration_changes_decision.nunique() > 1:
                crossing_groups.append((float(group.H.abs().min()), key, group))
        if crossing_groups:
            _, _, group = sorted(crossing_groups, key=lambda item: (item[0], item[1]))[0]
            for _, row in group.sort_values("B").iterrows():
                add("B_crosses_frontier", row)
        essential = eligible[(eligible.DeltaV > 0) & (eligible.DeltaV_local <= 0) & (eligible.DeltaV_cross > 0)]
        if len(essential):
            add("cross_domain_essential_for_positive_DeltaV", essential.sort_values(["DeltaV_cross", "seed", "domain", "N", "c", "B"], ascending=[False, True, True, True, True, True]).iloc[0])
    return pd.DataFrame(cases)


def generate_figures(raw: pd.DataFrame, cases: pd.DataFrame, output_dir: Path) -> None:
    import matplotlib.pyplot as plt

    figures = output_dir / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, len(N_VALUES), figsize=(12, 3.5), sharey=True)
    for axis, n in zip(axes, N_VALUES, strict=True):
        table = raw[raw.N == n].groupby(["B", "c"]).integration_changes_decision.mean().unstack("c")
        image = axis.imshow(table.to_numpy(), aspect="auto", origin="lower", vmin=0, vmax=1, cmap="viridis")
        axis.set_title(f"N={n}")
        axis.set_xticks(range(len(table.columns)), [f"{x:.2f}" for x in table.columns])
        axis.set_yticks(range(len(table.index)), [str(x) for x in table.index])
        axis.set_xlabel("c")
    axes[0].set_ylabel("B")
    figure.colorbar(image, ax=axes, label="fraction decision changes")
    figure.subplots_adjust(wspace=0.25, right=0.88)
    figure.savefig(figures / "decision_region_by_N.png", dpi=160, bbox_inches="tight")
    plt.close(figure)

    if len(cases):
        keys = cases[["seed", "domain", "N", "c"]].drop_duplicates().head(4)
        figure, axis = plt.subplots(figsize=(6, 4))
        for row in keys.itertuples(index=False):
            subset = raw[(raw.seed == row.seed) & (raw.domain == row.domain) & (raw.N == row.N) & np.isclose(raw.c, row.c)].sort_values("B")
            axis.plot(subset.B, subset.H, marker="o", label=f"s{row.seed} {row.domain} N={row.N} c={row.c:.2f}")
        axis.axhline(0, color="black", linewidth=0.7)
        axis.set_xlabel("B")
        axis.set_ylabel("H")
        axis.legend(fontsize=7)
        figure.tight_layout()
        figure.savefig(figures / "H_vs_B_representative.png", dpi=160)
        plt.close(figure)

    contribution = raw.groupby("N")[["DeltaV_local", "DeltaV_cross"]].mean()
    figure, axis = plt.subplots(figsize=(5, 3.5))
    contribution.plot(kind="bar", ax=axis)
    axis.axhline(0, color="black", linewidth=0.7)
    axis.set_ylabel("mean DeltaV contribution")
    figure.tight_layout()
    figure.savefig(figures / "deltaV_local_cross.png", dpi=160)
    plt.close(figure)


def analysis_summary(raw: pd.DataFrame, aggregate: pd.DataFrame, classification: str) -> str:
    favorable = raw[raw.integration_changes_decision]
    noncomp = raw[(raw.rho > 0) & (raw.H <= 0)]
    cross_positive = raw[(raw.DeltaV > 0) & (raw.DeltaV_cross > 0)]
    return "\n".join(
        [
            "# B2.2 PACS opportunity-value analysis",
            "",
            "Status: generated only after all 60 validated opportunity updates completed.",
            "TEST remained closed.",
            "",
            "## Frozen classification",
            "",
            f"{classification}",
            "",
            "## Q1-Q7 factual outputs",
            "",
            f"- Q1 rho>0 and H>0 observations: {len(favorable)}/{len(raw)}.",
            f"- Q2 exact cells with >=2 favorable seeds: {int((aggregate.n_integration_changes >= 2).sum())}/{len(aggregate)}.",
            f"- Q3 rho>0 and H<=0 observations: {len(noncomp)}/{len(raw)}.",
            f"- Q4 strict-frontier equivalence checks: {int(raw.frontier_equivalent.eq(raw.integration_changes_decision).sum())}/{len(raw)}.",
            "- Q5 complete N/c/B cell results are in aggregate_results.csv and decision_regions.csv.",
            f"- Q6 DeltaV>0 observations with positive cross-domain contribution: {len(cross_positive)}/{len(raw)}.",
            f"- Q7 decisions changed after opportunity value: {len(favorable)}/{len(raw)}.",
            "",
            "This output applies only the preregistered B2.2 definitions. It does not report TEST, an ex-ante policy, universal HLS superiority, novelty, or B2.3.",
        ]
    ) + "\n"


def ensure_base_models(
    frame: pd.DataFrame,
    splits: dict[int, DevelopmentSplits],
    config: dict,
    image_root: Path,
    device: torch.device,
    cache_dir: Path,
    signatures: RunSignatures,
) -> None:
    lookup = frame.set_index("sample_id", drop=False)
    batch_size = int(config["training"]["batch_size"])
    for seed in SEEDS:
        base_ids = splits[seed].base
        transfer_ids = splits[seed].transfer
        validation = lookup.loc[list(splits[seed].validation)].reset_index(drop=True)
        teacher_frame = lookup.loc[list(base_ids + transfer_ids)].reset_index(drop=True)
        selected_f0_ids = b20.select_base_fraction(frame, base_ids, F0_FRACTION, seed + 250)
        f0_frame = lookup.loc[selected_f0_ids].reset_index(drop=True)
        for kind, training_frame in (("deep", teacher_frame), ("fast", f0_frame)):
            path = cache_dir / "base" / f"{kind}_seed{seed}.pt"
            if path.exists():
                load_base_checkpoint(path, kind, seed, signatures, device)
                print(f"base {kind} seed={seed}: compatible checkpoint found", flush=True)
                continue
            print(f"training base {kind} seed={seed} on CPU", flush=True)
            model, _, seconds = train_base(kind, seed, training_frame, config, image_root, device)
            scores = score_model(model, validation, image_root, device, batch_size)
            save_base_checkpoint(path, model, scores, _base_metadata(kind, seed, signatures), seconds)
            del model


def run_one_update(
    spec: UpdateSpec,
    frame: pd.DataFrame,
    splits: dict[int, DevelopmentSplits],
    config: dict,
    image_root: Path,
    device: torch.device,
    cache_dir: Path,
    signatures: RunSignatures,
) -> dict[str, object]:
    update_started = time.perf_counter()
    lookup = frame.set_index("sample_id", drop=False)
    validation = lookup.loc[list(splits[spec.seed].validation)].reset_index(drop=True)
    selected = lookup.loc[list(spec.selected_ids)].reset_index(drop=True)
    deep, deep_scores, _ = load_base_checkpoint(cache_dir / "base" / f"deep_seed{spec.seed}.pt", "deep", spec.seed, signatures, device)
    f0, f0_scores, _ = load_base_checkpoint(cache_dir / "base" / f"fast_seed{spec.seed}.pt", "fast", spec.seed, signatures, device)
    f0_fingerprint = state_dict_fingerprint(f0)
    fast_processed = process_fast_batch(f0, selected, image_root, device, int(config["training"]["batch_size"]))
    fast_record = fast_trajectory_record(spec, f0_fingerprint, fast_processed)
    opportunity, deep_record = deep_opportunity_record(
        spec,
        selected,
        lambda selected_frame: predict_labels(deep, selected_frame, image_root, device, int(config["training"]["batch_size"])),
    )
    fk, history, training_seconds, initial_fingerprint = train_from_f0(f0, opportunity, spec, config, image_root, device)
    if initial_fingerprint != f0_fingerprint:
        raise RuntimeError("opportunity update did not start from the recorded F0")
    fk_scores = score_model(fk, validation, image_root, device, int(config["training"]["batch_size"]))
    record: dict[str, object] = {
        "metadata": expected_update_metadata(spec, signatures),
        "parent_state": "F0",
        "initial_f0_fingerprint": f0_fingerprint,
        "Fk_fingerprint": state_dict_fingerprint(fk),
        "F0_scores": f0_scores,
        "Fk_scores": fk_scores,
        "D_scores": deep_scores,
        "fast_trajectory": fast_record,
        "deep_trajectory": deep_record,
        "training_history": history,
        "training_seconds": training_seconds,
        "update_seconds": time.perf_counter() - update_started,
        "test_used": False,
        "evaluated_split": "validation",
    }
    validate_update_artifact(record, spec, signatures)
    del deep, f0, fk
    return record


def print_update_progress(records: dict[str, dict[str, object]], session_started: float, update_number: int) -> None:
    completed = len(records)
    times = [float(record["update_seconds"]) for record in records.values()]
    mean_time = float(np.mean(times))
    eta = mean_time * (TOTAL_UPDATES - completed)
    print(f"completed update {update_number}/{TOTAL_UPDATES}", flush=True)
    print(f"update time: {format_duration(times[-1])}", flush=True)
    print(f"total elapsed: {format_duration(time.perf_counter() - session_started)}", flush=True)
    print(f"mean time/update: {format_duration(mean_time)}", flush=True)
    print(f"global ETA: {format_duration(eta)}", flush=True)
    if completed % 5 == 0:
        print(f"Progress: {completed}/{TOTAL_UPDATES} ({100 * completed / TOTAL_UPDATES:.1f}%)", flush=True)
        print(f"Elapsed: {format_duration(time.perf_counter() - session_started)}", flush=True)
        print(f"Mean completed update time: {format_duration(mean_time)}", flush=True)
        print(f"Estimated remaining: {format_duration(eta)}", flush=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", choices=("cpu",), default="cpu")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="discard compatible restart state and repeat all work")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    started = time.perf_counter()
    print_header()
    phase(1, "Protocol and consistency checks", started)
    device = require_cpu(args.device)
    config = json.loads(CONFIG_PATH.read_text())
    validate_protocol_and_config(config)
    if not args.manifest.is_file():
        raise FileNotFoundError(args.manifest)
    if not args.image_root.is_dir():
        raise FileNotFoundError(args.image_root)
    if not args.output_dir.is_dir():
        raise FileNotFoundError(f"output directory must already exist: {args.output_dir}")
    frame = pd.read_csv(args.manifest)
    b20.validate_manifest(frame)
    splits = {seed: development_splits(frame, seed) for seed in SEEDS}
    visible_ids = {
        sample_id
        for split in splits.values()
        for role in (split.base, split.transfer, split.validation)
        for sample_id in role
    }
    visible_frame = frame[frame.sample_id.isin(visible_ids)]
    missing_images = [path for path in visible_frame.relative_path if not (args.image_root / path).is_file()]
    if missing_images:
        raise FileNotFoundError(f"{len(missing_images)} development-visible PACS images are missing from --image-root")
    plan = build_plan(frame, splits)
    signatures = RunSignatures(
        protocol_sha256=sha256_file(PROTOCOL_PATH),
        config_sha256=sha256_file(CONFIG_PATH),
        manifest_sha256=sha256_file(args.manifest),
        implementation_sha256=sha256_file(Path(__file__)),
    )
    cache_dir = args.output_dir / ".cache"
    completed = load_completed_updates(cache_dir, plan, signatures, args.force)
    print(f"Resuming B2.2: {len(completed)}/{TOTAL_UPDATES} updates already complete.", flush=True)

    if args.dry_run:
        phase(2, "Loading/reconstructing F0 and D (configuration check only)", started)
        print("F0 configuration: MobileNetV2, 25% BASE, three epochs.", flush=True)
        print("D configuration: ResNet-50, BASE+TRANSFER, three epochs.", flush=True)
        print("Dry-run successful.", flush=True)
        print(f"{TOTAL_UPDATES} opportunity updates planned.", flush=True)
        print(f"{TOTAL_GRID_ROWS} analytical observations planned.", flush=True)
        print("TEST remains closed.", flush=True)
        print("No training executed.", flush=True)
        return

    if args.force:
        reset_outputs(args.output_dir, cache_dir)
        completed = {}
    cache_dir.mkdir(parents=True, exist_ok=True)
    phase(2, "Loading/reconstructing F0 and D", started)
    execute_training_phase(False, lambda: ensure_base_models(frame, splits, config, args.image_root, device, cache_dir, signatures))

    phase(3, "Training opportunity updates", started)
    for spec in plan:
        if spec.update_id in completed:
            continue
        print("-" * 60, flush=True)
        print(f"[update {spec.number}/{TOTAL_UPDATES}]", flush=True)
        print(f"seed={spec.seed} | domain={spec.domain} | N={spec.n}", flush=True)
        print("-" * 60, flush=True)
        record = run_one_update(spec, frame, splits, config, args.image_root, device, cache_dir, signatures)
        atomic_json(cache_dir / "updates" / f"{spec.update_id}.json", record)
        completed[spec.update_id] = record
        write_restart_state(cache_dir, completed, signatures)
        print_update_progress(completed, started, spec.number)

    phase(4, "Validation competence evaluation", started)
    if len(completed) != TOTAL_UPDATES:
        raise RuntimeError("all 60 validated opportunity updates are required before analysis")
    for spec in plan:
        validate_update_artifact(completed[spec.update_id], spec, signatures)

    phase(5, "Expanding pre-registered c x B grid", started)
    raw = expand_grid(completed)

    phase(6, "Analysis and classification", started)
    aggregate, regions = aggregate_results(raw)
    classification = classify_outcome(raw, regions)
    cases = representative_cases(raw)

    phase(7, "Validation and outputs", started)
    atomic_csv(args.output_dir / "raw_results.csv", raw)
    atomic_csv(args.output_dir / "aggregate_results.csv", aggregate)
    atomic_csv(args.output_dir / "decision_regions.csv", regions)
    atomic_csv(args.output_dir / "representative_cases.csv", cases)
    (args.output_dir / "analysis_summary.md").write_text(analysis_summary(raw, aggregate, classification))
    generate_figures(raw, cases, args.output_dir)
    atomic_json(
        args.output_dir / "run_metadata.json",
        {
            "protocol_id": PROTOCOL_ID,
            "device": "cpu",
            "seeds": list(SEEDS),
            "domains": list(DOMAINS),
            "N": list(N_VALUES),
            "costs": list(COSTS),
            "B": list(FUTURE_WEIGHTS),
            "kappa": KAPPA,
            "opportunity_updates": TOTAL_UPDATES,
            "analytical_rows": TOTAL_GRID_ROWS,
            "test_used": False,
            "classification": classification,
            **asdict(signatures),
        },
    )
    print(f"B2.2 complete: {TOTAL_UPDATES} updates and {TOTAL_GRID_ROWS} analytical rows.", flush=True)
    print("TEST remained closed.", flush=True)


if __name__ == "__main__":
    main()
