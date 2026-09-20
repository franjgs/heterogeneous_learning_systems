"""Run the B2.0 PACS Fast/Deep validation calibration on an accelerator."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import (
    MobileNet_V2_Weights,
    ResNet50_Weights,
    mobilenet_v2,
    resnet50,
)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from hls.b2_pacs_calibration import (  # noqa: E402
    CLASSES,
    DOMAINS,
    domain_gaps,
    domain_metrics,
    select_base_fraction,
    stratified_splits,
    validate_manifest,
)


class PACSImages(Dataset):
    def __init__(self, frame: pd.DataFrame, image_root: Path, training: bool):
        self.frame = frame.reset_index(drop=True)
        self.image_root = image_root
        mean = (0.485, 0.456, 0.406)
        std = (0.229, 0.224, 0.225)
        if training:
            self.transform = transforms.Compose(
                [
                    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.ToTensor(),
                    transforms.Normalize(mean, std),
                ]
            )
        else:
            self.transform = transforms.Compose(
                [
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean, std),
                ]
            )

    def __len__(self) -> int:
        return len(self.frame)

    def __getitem__(self, index: int):
        row = self.frame.iloc[index]
        with Image.open(self.image_root / row.relative_path) as source:
            image = source.convert("RGB")
        return self.transform(image), int(row.label), str(row.domain), int(row.sample_id)


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:d}:{minutes:02d}:{seconds:02d}"


def print_validation_metrics(kind: str, seed: int, fraction: float, by_domain: dict) -> None:
    print(
        f"Validation {kind} / seed {seed} / fraction {fraction:.2f}: "
        + "; ".join(
            f"{domain} BA={by_domain[domain]['balanced_accuracy']:.3f}, "
            f"acc={by_domain[domain]['accuracy']:.3f}"
            for domain in DOMAINS
        ),
        flush=True,
    )


def make_model(kind: str, seed: int, device: torch.device, pretrained: bool = True) -> nn.Module:
    seed_everything(seed)
    if kind == "fast":
        model = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT if pretrained else None)
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, len(CLASSES))
    elif kind == "deep":
        model = resnet50(weights=ResNet50_Weights.DEFAULT if pretrained else None)
        model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    else:
        raise ValueError(kind)
    return model.to(device)


def fit_model(
    kind: str,
    seed: int,
    frame: pd.DataFrame,
    image_root: Path,
    device: torch.device,
    config: dict,
    fit_number: int,
    fraction: float,
    run_started: float,
) -> tuple[nn.Module, float]:
    seed_everything(seed)
    model = make_model(kind, seed, device)
    params = config[kind]
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=float(params["learning_rate"]),
        momentum=float(params["momentum"]),
    )
    dataset = PACSImages(frame, image_root, training=True)
    generator = torch.Generator().manual_seed(seed)
    loader = DataLoader(
        dataset,
        batch_size=int(config["training"]["batch_size"]),
        shuffle=True,
        num_workers=int(config["training"]["workers"]),
        generator=generator,
        pin_memory=device.type == "cuda",
    )
    start = time.perf_counter()
    model.train()
    epochs = int(config["training"]["epochs"])
    for epoch in range(1, epochs + 1):
        epoch_started = time.perf_counter()
        for images, labels, _, _ in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            loss = nn.functional.cross_entropy(model(images), labels)
            loss.backward()
            optimizer.step()
        epoch_seconds = time.perf_counter() - epoch_started
        elapsed = time.perf_counter() - run_started
        progress = (fit_number - 1) + epoch / epochs
        eta = elapsed / progress * (25 - progress)
        print(
            f"[epoch {epoch}/{epochs}] {epoch_seconds:.1f}s | "
            f"total {format_duration(elapsed)} | ETA B2.0 {format_duration(eta)}",
            flush=True,
        )
    return model, time.perf_counter() - start


@torch.inference_mode()
def evaluate(model: nn.Module, frame: pd.DataFrame, image_root: Path, device: torch.device, batch_size: int):
    loader = DataLoader(
        PACSImages(frame, image_root, training=False),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    model.eval()
    labels, predictions, domains, ids = [], [], [], []
    for images, target, domain, sample_ids in loader:
        output = model(images.to(device))
        labels.extend(target.numpy().tolist())
        predictions.extend(output.argmax(1).cpu().numpy().tolist())
        domains.extend(list(domain))
        ids.extend(sample_ids.numpy().tolist())
    return np.asarray(labels), np.asarray(predictions), np.asarray(domains), np.asarray(ids)


def bootstrap_interval(values: list[float], seed: int, repetitions: int = 5000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    sample = np.asarray(values, dtype=float)
    means = np.mean(rng.choice(sample, (repetitions, len(sample)), replace=True), axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def choose_fraction(validation: pd.DataFrame, chance: float = 1 / 7) -> float | None:
    """Choose the smallest fraction meeting the predeclared validation criteria."""
    for fraction in (0.10, 0.25, 0.50, 1.00):
        frows = validation[(validation.model == "fast") & (validation.fraction == fraction)]
        drows = validation[validation.model == "deep"]
        lower = {}
        upper = {}
        gap_lower = {}
        for domain in DOMAINS:
            vals = frows[f"ba_{domain}"].astype(float).tolist()
            dvals = drows[f"ba_{domain}"].astype(float).tolist()
            lower[domain], upper[domain] = bootstrap_interval(vals, int(fraction * 10000) + len(domain))
            gap_lower[domain] = bootstrap_interval(
                [d - f for d, f in zip(dvals, vals, strict=True)],
                int(fraction * 10000) + len(domain) + 111,
            )[0]
        above_chance = all(lower[domain] > chance for domain in DOMAINS)
        not_ceiling = sum(upper[domain] < 1.0 for domain in DOMAINS) >= 2
        teacher_advantage = sum(gap_lower[domain] > 0.0 for domain in DOMAINS) >= 2
        if above_chance and not_ceiling and teacher_advantage:
            return fraction
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv")
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/pilots/b2_pacs_calibration")
    parser.add_argument("--allow-cpu", action="store_true", help="explicit override; expected full run is hours")
    args = parser.parse_args()
    config = json.loads((ROOT / "experiments/pilots/b2_pacs_calibration/config.json").read_text())
    frame = pd.read_csv(args.manifest)
    validate_manifest(frame)
    if set(frame.class_name) != set(CLASSES) or set(frame.domain) != set(DOMAINS):
        raise RuntimeError("dataset manifest does not match expected PACS domains/classes")
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    if device.type == "cpu" and not args.allow_cpu:
        raise SystemExit(
            "B2.0 calibration is compute-blocked by CPU-only hardware: the measured pilot profile "
            "estimates >70 minutes per epoch for all 25 fits before validation. Use an accelerator, "
            "or explicitly pass --allow-cpu after reviewing the estimate."
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    temporary_checkpoints = tempfile.TemporaryDirectory(prefix="hls_b2_pacs_checkpoints_")
    checkpoint_dir = Path(temporary_checkpoints.name)
    run_started = time.perf_counter()
    metrics: list[dict[str, object]] = []
    split_rows: list[dict[str, object]] = []
    confusion_rows: list[dict[str, object]] = []
    fit_times: list[dict[str, object]] = []
    splits_by_seed = {seed: stratified_splits(frame, seed) for seed in config["split_seeds"]}
    lookup = frame.set_index("sample_id", drop=False)

    fit_number = 0
    total_fits = len(splits_by_seed) * (1 + len(config["base_fractions_for_fast"]))
    for seed, splits in splits_by_seed.items():
        for split, ids in splits.items():
            split_rows.extend({"seed": seed, "sample_id": int(i), "split": split} for i in ids)
        base = lookup.loc[splits["base"]].reset_index(drop=True)
        teacher_frame = lookup.loc[np.concatenate([splits["base"], splits["transfer"]])].reset_index(drop=True)
        validation_frame = lookup.loc[splits["validation"]].reset_index(drop=True)

        fit_number += 1
        print(f"[fit {fit_number}/{total_fits}] deep / seed {seed} / fraction 1.00", flush=True)
        teacher, elapsed = fit_model("deep", seed + 30000, teacher_frame, args.image_root, device, config, fit_number, 1.0, run_started)
        torch.save({key: value.detach().cpu() for key, value in teacher.state_dict().items()}, checkpoint_dir / f"deep_seed{seed}.pt")
        fit_times.append({"seed": seed, "model": "deep", "fraction": 1.0, "seconds": elapsed, "n_train": len(teacher_frame)})
        for splitname, splitframe in (("validation", validation_frame),):
            y, pred, domains, ids = evaluate(teacher, splitframe, args.image_root, device, config["training"]["batch_size"])
            by_domain = domain_metrics(y, pred, domains)
            print_validation_metrics("deep", seed, 1.0, by_domain)
            row = {"seed": seed, "model": "deep", "fraction": 1.0, "split": splitname, "n": len(y), "accuracy": float(accuracy_score(y, pred)), "balanced_accuracy": float(balanced_accuracy_score(y, pred))}
            row.update({f"ba_{d}": by_domain[d]["balanced_accuracy"] for d in DOMAINS})
            row.update({f"acc_{d}": by_domain[d]["accuracy"] for d in DOMAINS})
            row.update({f"n_{d}": by_domain[d]["n"] for d in DOMAINS})
            metrics.append(row)
            for domain in DOMAINS:
                mask = domains == domain
                confusion_rows.append({"seed": seed, "model": "deep", "fraction": 1.0, "split": splitname, "domain": domain, "matrix": json.dumps(confusion_matrix(y[mask], pred[mask], labels=list(range(len(CLASSES)))).tolist())})
        del teacher
        if device.type == "cuda":
            torch.cuda.empty_cache()

        for fraction in config["base_fractions_for_fast"]:
            subset_ids = select_base_fraction(frame, base.sample_id, fraction, seed + int(fraction * 1000))
            train_frame = lookup.loc[subset_ids].reset_index(drop=True)
            fit_number += 1
            print(f"[fit {fit_number}/{total_fits}] fast / seed {seed} / fraction {fraction:.2f}", flush=True)
            model, elapsed = fit_model("fast", seed + int(fraction * 10000), train_frame, args.image_root, device, config, fit_number, fraction, run_started)
            torch.save({key: value.detach().cpu() for key, value in model.state_dict().items()}, checkpoint_dir / f"fast_seed{seed}_fraction{fraction:.2f}.pt")
            fit_times.append({"seed": seed, "model": "fast", "fraction": fraction, "seconds": elapsed, "n_train": len(train_frame)})
            y, pred, domains, ids = evaluate(model, validation_frame, args.image_root, device, config["training"]["batch_size"])
            by_domain = domain_metrics(y, pred, domains)
            print_validation_metrics("fast", seed, fraction, by_domain)
            row = {"seed": seed, "model": "fast", "fraction": fraction, "split": "validation", "n": len(y), "accuracy": float(accuracy_score(y, pred)), "balanced_accuracy": float(balanced_accuracy_score(y, pred))}
            row.update({f"ba_{d}": by_domain[d]["balanced_accuracy"] for d in DOMAINS})
            row.update({f"acc_{d}": by_domain[d]["accuracy"] for d in DOMAINS})
            row.update({f"n_{d}": by_domain[d]["n"] for d in DOMAINS})
            metrics.append(row)
            for domain in DOMAINS:
                mask = domains == domain
                confusion_rows.append({"seed": seed, "model": "fast", "fraction": fraction, "split": "validation", "domain": domain, "matrix": json.dumps(confusion_matrix(y[mask], pred[mask], labels=list(range(len(CLASSES)))).tolist())})
            del model

        del base
        if device.type == "cuda":
            torch.cuda.empty_cache()

    validation_metrics = pd.DataFrame(metrics)
    validation_metrics.to_csv(args.output_dir / "validation_metrics.csv", index=False)
    pd.DataFrame(split_rows).to_csv(args.output_dir / "split_manifest.csv", index=False)
    pd.DataFrame(fit_times).to_csv(args.output_dir / "fit_times.csv", index=False)
    selected = choose_fraction(validation_metrics)
    final_rows = []
    if selected is not None:
        # Load the validation-calibration checkpoints and evaluate TEST once.
        for seed, splits in splits_by_seed.items():
            for kind in ("fast", "deep"):
                model = make_model(kind, seed, device, pretrained=False)
                ckpt = f"fast_seed{seed}_fraction{selected:.2f}.pt" if kind == "fast" else f"deep_seed{seed}.pt"
                model.load_state_dict(torch.load(checkpoint_dir / ckpt, map_location="cpu", weights_only=True))
                y, pred, domains, sample_ids = evaluate(model, lookup.loc[splits["test"]].reset_index(drop=True), args.image_root, device, config["training"]["batch_size"])
                metrics_by_domain = domain_metrics(y, pred, domains)
                row = {"seed": seed, "model": kind, "fraction": selected, "split": "test", "n": len(y), "accuracy": float(accuracy_score(y, pred)), "balanced_accuracy": float(balanced_accuracy_score(y, pred))}
                row.update({f"ba_{d}": metrics_by_domain[d]["balanced_accuracy"] for d in DOMAINS})
                row.update({f"acc_{d}": metrics_by_domain[d]["accuracy"] for d in DOMAINS})
                row.update({f"n_{d}": metrics_by_domain[d]["n"] for d in DOMAINS})
                final_rows.append(row)
                for domain in DOMAINS:
                    mask = domains == domain
                    matrix = confusion_matrix(y[mask], pred[mask], labels=list(range(len(CLASSES))))
                    confusion_rows.append({"seed": seed, "model": kind, "fraction": selected, "split": "test", "domain": domain, "matrix": json.dumps(matrix.tolist())})
                del model
        pd.DataFrame(final_rows).to_csv(args.output_dir / "test_metrics.csv", index=False)
        test_frame = pd.DataFrame(final_rows)
        gap_rows = []
        for seed in config["split_seeds"]:
            fast_row = test_frame[(test_frame.seed == seed) & (test_frame.model == "fast")].iloc[0]
            deep_row = test_frame[(test_frame.seed == seed) & (test_frame.model == "deep")].iloc[0]
            gap_rows.append({"seed": seed, **domain_gaps(
                {domain: float(deep_row[f"ba_{domain}"]) for domain in DOMAINS},
                {domain: float(fast_row[f"ba_{domain}"]) for domain in DOMAINS},
            )})
        pd.DataFrame(gap_rows).to_csv(args.output_dir / "gaps.csv", index=False)

    pd.DataFrame(metrics).to_csv(args.output_dir / "metrics.csv", index=False)
    domain_rows = [
        {"seed": row["seed"], "model": row["model"], "fraction": row["fraction"], "split": row["split"], "domain": domain, "balanced_accuracy": row[f"ba_{domain}"], "accuracy": row[f"acc_{domain}"], "n": row[f"n_{domain}"]}
        for row in metrics + final_rows
        for domain in DOMAINS
    ]
    pd.DataFrame(domain_rows).to_csv(args.output_dir / "domain_metrics.csv", index=False)
    pd.DataFrame(confusion_rows).to_csv(args.output_dir / "confusion_matrices.csv", index=False)

    (args.output_dir / "summary.json").write_text(json.dumps({
        "status": "OBSERVED" if selected is not None else "VALIDATION_NO_REGIME_SELECTED",
        "selected_base_fraction_validation_only": selected,
        "test_evaluated": selected is not None,
        "rule": "smallest fraction with bootstrap lower CI above 1/7 in every domain, bootstrap upper CI below 1 in >=2 domains, and teacher-minus-student gap lower CI above zero in >=2 domains",
        "device": str(device),
        "note": "B2.0 only; no Gamma, routing, costs, or factorial development comparisons.",
    }, indent=2) + "\n")
    (args.output_dir / "run_metadata.json").write_text(json.dumps({
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "mps_available": bool(torch.backends.mps.is_available()),
        "torch_threads": torch.get_num_threads(),
        "total_fits": len(fit_times),
        "total_seconds": time.perf_counter() - run_started,
        "fit_times": fit_times,
        "warnings": [],
    }, indent=2) + "\n")
    temporary_checkpoints.cleanup()


if __name__ == "__main__":
    main()
