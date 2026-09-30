"""Compare the normal B2.0 teacher path with the isolated seed diagnostic.

This diagnostic runs only the ResNet-50 teacher for the requested seed, uses
the configured protocol unchanged, evaluates VALIDATION only, and writes its
report under results/pilots/b2_pacs_calibration/diagnostics/.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.models import ResNet50_Weights

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def load_runner():
    runner_path = ROOT / "experiments/pilots/b2_pacs_calibration/run.py"
    spec = importlib.util.spec_from_file_location("b2_pacs_runner_for_diagnostics", runner_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import runner from {runner_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tensor_hash(tensor: torch.Tensor) -> str:
    value = tensor.detach().to("cpu").contiguous()
    return sha256_bytes(value.numpy().tobytes())


def state_hash(state: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name in sorted(state):
        value = state[name].detach().to("cpu").contiguous()
        digest.update(name.encode())
        digest.update(str(value.dtype).encode())
        digest.update(str(tuple(value.shape)).encode())
        digest.update(value.numpy().tobytes())
    return digest.hexdigest()


def rng_fingerprints() -> dict[str, str | None]:
    np_state = np.random.get_state()
    np_digest = hashlib.sha256()
    np_digest.update(np_state[0].encode())
    np_digest.update(np_state[1].tobytes())
    np_digest.update(str(np_state[2:]).encode())
    mps_state = None
    if torch.backends.mps.is_built() and hasattr(torch.mps, "get_rng_state"):
        mps_state = tensor_hash(torch.mps.get_rng_state())
    return {
        "python": sha256_bytes(repr(random.getstate()).encode()),
        "numpy": np_digest.hexdigest(),
        "torch_cpu": tensor_hash(torch.get_rng_state()),
        "torch_mps": mps_state,
    }


def image_sha(image: torch.Tensor) -> str:
    return tensor_hash(image)


class TraceStop(RuntimeError):
    pass


class FitTrace:
    def __init__(self, name: str, expected_steps_per_epoch: int, snapshot_dir: Path, max_steps: int | None = None):
        self.name = name
        self.expected_steps_per_epoch = expected_steps_per_epoch
        self.snapshot_dir = snapshot_dir
        self.max_steps = max_steps
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.model: nn.Module | None = None
        self.model_init: dict[str, Any] = {}
        self.constructor: dict[str, Any] = {}
        self.seed_calls: list[dict[str, Any]] = []
        self.optimizer: dict[str, Any] = {}
        self.first_batch: dict[str, Any] = {}
        self.first_step: dict[str, Any] = {}
        self.train_ids: list[int] = []
        self.train_labels: list[int] = []
        self.train_domains: list[str] = []
        self.transformed_images: list[str] = []
        self.current_batch: list[dict[str, Any]] = []
        self.batch_events: list[dict[str, Any]] = []
        self.step_events: list[dict[str, Any]] = []
        self.losses: list[tuple[torch.Tensor, int]] = []
        self.predictions: list[torch.Tensor] = []
        self.labels: list[torch.Tensor] = []
        self.snapshots: list[Path] = []
        self.step_count = 0
        self.batches = 0

    def record_model(self, model: nn.Module, weights: str) -> None:
        self.model = model
        parameters = list(model.parameters())
        trainable = [parameter for parameter in parameters if parameter.requires_grad]
        fc = model.fc
        self.model_init = {
            "weights": weights,
            "state_dict_sha256": state_hash(model.state_dict()),
            "fc_weight_sha256": tensor_hash(fc.weight),
            "fc_bias_sha256": tensor_hash(fc.bias),
            "fc_weight_stats": {
                "mean": float(fc.weight.detach().mean().cpu()),
                "std": float(fc.weight.detach().std().cpu()),
                "min": float(fc.weight.detach().min().cpu()),
                "max": float(fc.weight.detach().max().cpu()),
            },
            "fc_shape": list(fc.weight.shape),
            "parameters_total": sum(parameter.numel() for parameter in parameters),
            "parameters_trainable": sum(parameter.numel() for parameter in trainable),
            "parameters_requires_grad": len(trainable),
            "parameters_frozen": len(parameters) - len(trainable),
            "parameter_device": str(parameters[0].device),
        }

    def record_sample(self, image: torch.Tensor, label: int, domain: str, sample_id: int) -> None:
        sample = {
            "sample_id": int(sample_id),
            "label": int(label),
            "domain": str(domain),
            "transformed_tensor_sha256": image_sha(image),
        }
        self.current_batch.append(sample)
        if len(self.train_ids) < 16:
            self.train_ids.append(int(sample_id))
            self.train_labels.append(int(label))
            self.train_domains.append(str(domain))
            self.transformed_images.append(image_sha(image))

    def record_loss_call(self, logits: torch.Tensor, labels: torch.Tensor, loss: torch.Tensor) -> None:
        count = int(labels.numel())
        self.losses.append((loss.detach(), count))
        self.predictions.append(logits.detach().argmax(1))
        self.labels.append(labels.detach())
        self.batches += 1
        if self.batches <= 8:
            values = logits.detach().to("cpu")
            event = {
                "batch": self.batches,
                "samples": self.current_batch,
                "logits_shape": list(logits.shape),
                "logits_sha256": tensor_hash(logits),
                "logits_mean": float(values.mean()),
                "logits_std": float(values.std()),
                "logits_min": float(values.min()),
                "logits_max": float(values.max()),
                "loss": float(loss.detach().cpu()),
                "labels": labels.detach().cpu().tolist(),
                "labels_sha256": tensor_hash(labels),
                "logits_finite": bool(torch.isfinite(logits).all().cpu()),
                "loss_finite": bool(torch.isfinite(loss).all().cpu()),
            }
            self.batch_events.append(event)
            if self.batches == 1:
                self.first_batch = event
        self.current_batch = []

    def record_optimizer(self, optimizer: torch.optim.Optimizer) -> None:
        model_params = {id(parameter) for parameter in self.model.parameters()} if self.model else set()
        included = {id(parameter) for group in optimizer.param_groups for parameter in group["params"]}
        self.optimizer = {
            "class": f"{optimizer.__class__.__module__}.{optimizer.__class__.__name__}",
            "parameter_groups": len(optimizer.param_groups),
            "parameters_in_optimizer": sum(len(group["params"]) for group in optimizer.param_groups),
            "parameters_included": len(included),
            "contains_exact_model_parameters": included == model_params,
            "groups": [
                {
                    "lr": group["lr"],
                    "momentum": group.get("momentum"),
                    "weight_decay": group.get("weight_decay"),
                    "nesterov": group.get("nesterov"),
                }
                for group in optimizer.param_groups
            ],
        }

    def before_first_step(self, optimizer: torch.optim.Optimizer) -> None:
        if self.step_count >= 8:
            return
        assert self.model is not None
        fc_grad = self.model.fc.weight.grad
        grads = [parameter.grad.detach() for parameter in self.model.parameters() if parameter.grad is not None]
        squared = (
            sum(float(gradient.float().pow(2).sum().cpu()) for gradient in grads)
            if self.step_count == 0
            else float(fc_grad.detach().float().pow(2).sum().cpu())
        )
        event = {
            "step": self.step_count + 1,
            "gradient_tensors": len(grads) if self.step_count == 0 else None,
            "gradient_global_norm": math.sqrt(squared),
            "fc_weight_gradient_norm": float(fc_grad.detach().norm().cpu()) if fc_grad is not None else None,
            "gradients_finite": (
                all(bool(torch.isfinite(gradient).all().cpu()) for gradient in grads)
                if self.step_count == 0
                else bool(torch.isfinite(fc_grad).all().cpu())
            ),
            "fc_weight_sha256_before": tensor_hash(self.model.fc.weight),
            "fc_gradient_sha256": tensor_hash(fc_grad) if fc_grad is not None else None,
            "weight_decay": optimizer.param_groups[0].get("weight_decay"),
        }
        self._fc_step_before = self.model.fc.weight.detach().to("cpu").clone()
        self.step_events.append(event)
        if self.step_count == 0:
            self.first_step = event

    def after_step(self) -> None:
        assert self.model is not None
        self.step_count += 1
        if self.step_count <= 8:
            event = self.step_events[self.step_count - 1]
            before_hash = event["fc_weight_sha256_before"]
            after = self.model.fc.weight.detach()
            event.update(
                {
                    "fc_weight_sha256_after": tensor_hash(after),
                    "fc_weight_delta_norm": float((after - self._fc_step_before.to(after.device)).norm().cpu()),
                    "fc_weight_changed": before_hash != tensor_hash(after),
                    "parameters_finite_after_step": (
                        all(bool(torch.isfinite(parameter).all().cpu()) for parameter in self.model.parameters())
                        if self.step_count == 1
                        else bool(torch.isfinite(after).all().cpu())
                    ),
                }
            )
        if self.step_count % self.expected_steps_per_epoch == 0:
            epoch = self.step_count // self.expected_steps_per_epoch
            snapshot = self.snapshot_dir / f"{self.name}_epoch_{epoch}.pt"
            torch.save(
                {key: value.detach().to("cpu").clone() for key, value in self.model.state_dict().items()},
                snapshot,
            )
            self.snapshots.append(snapshot)
        if self.max_steps is not None and self.step_count >= self.max_steps:
            raise TraceStop(f"diagnostic stopped after {self.step_count} optimizer step(s)")

    def set_fc_before(self) -> None:
        assert self.model is not None
        self._first_fc_before = self.model.fc.weight.detach().to("cpu").clone()

    def train_by_epoch(self, epochs: int) -> list[dict[str, Any]]:
        rows = []
        steps = self.expected_steps_per_epoch
        for epoch in range(epochs):
            losses = self.losses[epoch * steps : (epoch + 1) * steps]
            preds = torch.cat(self.predictions[epoch * steps : (epoch + 1) * steps]).to("cpu")
            labels = torch.cat(self.labels[epoch * steps : (epoch + 1) * steps]).to("cpu")
            denom = sum(count for _, count in losses)
            loss = sum(float(value.cpu()) * count for value, count in losses) / denom
            rows.append(
                {
                    "epoch": epoch + 1,
                    "train_loss": loss,
                    "train_accuracy": float((preds == labels).float().mean()),
                    "train_samples": int(labels.numel()),
                }
            )
        return rows


def install_tracing(runner, trace: FitTrace):
    originals = {
        "make_model": runner.make_model,
        "seed_everything": runner.seed_everything,
        "getitem": runner.PACSImages.__getitem__,
        "cross_entropy": torch.nn.functional.cross_entropy,
        "sgd": torch.optim.SGD,
        "resnet50": runner.resnet50,
    }

    def traced_seed(seed: int) -> None:
        originals["seed_everything"](seed)
        trace.seed_calls.append({"seed": int(seed), "rng_after_seed": rng_fingerprints()})

    def traced_resnet50(*args, **kwargs):
        weights = kwargs.get("weights", args[0] if args else None)
        trace.constructor["rng_before_resnet_constructor"] = rng_fingerprints()
        trace.constructor["weights_arg"] = str(weights)
        trace.constructor["weights_url"] = getattr(weights, "url", None)
        model = originals["resnet50"](*args, **kwargs)
        trace.constructor["rng_after_resnet_constructor"] = rng_fingerprints()
        trace.constructor["pre_head_state_dict_sha256"] = state_hash(model.state_dict())
        return model

    def traced_make_model(kind: str, seed: int, device: torch.device, pretrained: bool = True):
        model = originals["make_model"](kind, seed, device, pretrained)
        trace.record_model(
            model,
            str(ResNet50_Weights.DEFAULT if pretrained else None),
        )
        return model

    def traced_getitem(dataset, index):
        result = originals["getitem"](dataset, index)
        image, label, domain, sample_id = result
        if "RandomResizedCrop" in repr(dataset.transform):
            trace.record_sample(image, label, domain, sample_id)
        return result

    def traced_cross_entropy(logits, labels, *args, **kwargs):
        loss = originals["cross_entropy"](logits, labels, *args, **kwargs)
        trace.record_loss_call(logits, labels, loss)
        return loss

    def traced_sgd(params, *args, **kwargs):
        optimizer = originals["sgd"](params, *args, **kwargs)
        trace.record_optimizer(optimizer)
        trace.set_fc_before()
        original_step = optimizer.step

        def step(*step_args, **step_kwargs):
            if trace.step_count < 8:
                trace.before_first_step(optimizer)
            result = original_step(*step_args, **step_kwargs)
            trace.after_step()
            return result

        optimizer.step = step
        return optimizer

    runner.seed_everything = traced_seed
    runner.resnet50 = traced_resnet50
    runner.make_model = traced_make_model
    runner.PACSImages.__getitem__ = traced_getitem
    torch.nn.functional.cross_entropy = traced_cross_entropy
    torch.optim.SGD = traced_sgd
    return originals


def restore_tracing(runner, originals) -> None:
    runner.make_model = originals["make_model"]
    runner.seed_everything = originals["seed_everything"]
    runner.PACSImages.__getitem__ = originals["getitem"]
    runner.resnet50 = originals["resnet50"]
    torch.nn.functional.cross_entropy = originals["cross_entropy"]
    torch.optim.SGD = originals["sgd"]


def validation_by_epoch(runner, trace: FitTrace, validation: pd.DataFrame, image_root: Path, device, batch_size, epochs):
    model = runner.make_model("deep", 0, device, pretrained=False)
    rows = []
    for epoch, snapshot in enumerate(trace.snapshots, start=1):
        state = torch.load(snapshot, map_location="cpu", weights_only=True)
        model.load_state_dict(state)
        model.eval()
        loader = DataLoader(
            runner.PACSImages(validation, image_root, training=False),
            batch_size=batch_size,
            shuffle=False,
            num_workers=0,
            generator=torch.Generator().manual_seed(9000 + epoch),
        )
        labels, predictions, domains, losses = [], [], [], []
        with torch.inference_mode():
            for images, target, domain, _ in loader:
                output = model(images.to(device))
                losses.append(float(nn.functional.cross_entropy(output, target.to(device)).cpu()) * len(target))
                labels.extend(target.tolist())
                predictions.extend(output.argmax(1).cpu().tolist())
                domains.extend(domain)
        y = np.asarray(labels)
        pred = np.asarray(predictions)
        hist = np.bincount(pred, minlength=len(runner.CLASSES)).tolist()
        rows.append(
            {
                "epoch": epoch,
                "validation_loss": sum(losses) / len(labels),
                "validation_accuracy": float((y == pred).mean()),
                "validation_balanced_accuracy": float(runner.balanced_accuracy_score(y, pred)),
                "predicted_class_histogram": hist,
                "label_histogram": np.bincount(y, minlength=len(runner.CLASSES)).tolist(),
                "validation_ba_by_domain": {
                    domain: runner.domain_metrics(y, pred, np.asarray(domains))[domain]["balanced_accuracy"]
                    for domain in runner.DOMAINS
                },
            }
        )
    del model
    return rows


def run_normal_path(runner, trace, seed, train_seed, image_root, manifest_path, output_dir, config, device):
    originals = install_tracing(runner, trace)
    old_argv = sys.argv
    original_read_text = Path.read_text
    original_choose_fraction = runner.choose_fraction
    original_mps_available = torch.backends.mps.is_available
    config_path = (ROOT / "experiments/pilots/b2_pacs_calibration/config.json").resolve()
    limited = dict(config)
    limited["split_seeds"] = [seed]
    limited["base_fractions_for_fast"] = []

    def limited_read_text(path, *args, **kwargs):
        if path.resolve() == config_path:
            return json.dumps(limited)
        return original_read_text(path, *args, **kwargs)

    try:
        Path.read_text = limited_read_text
        runner.choose_fraction = lambda _: None
        sys.argv = [
            "run.py",
            "--manifest",
            str(manifest_path),
            "--image-root",
            str(image_root),
            "--output-dir",
            str(output_dir),
        ]
        if device.type == "cpu":
            torch.backends.mps.is_available = lambda: False
            sys.argv.append("--allow-cpu")
        try:
            runner.main()
        except TraceStop:
            pass
    finally:
        sys.argv = old_argv
        Path.read_text = original_read_text
        runner.choose_fraction = original_choose_fraction
        torch.backends.mps.is_available = original_mps_available
        restore_tracing(runner, originals)


def run_isolated_path(runner, trace, seed, train_seed, training, validation, image_root, device, config):
    originals = install_tracing(runner, trace)
    try:
        # This follows the standalone seed diagnostic: seed directly, construct
        # the pretrained model, verify the official backbone, then replace fc.
        runner.seed_everything(train_seed)
        weights = ResNet50_Weights.DEFAULT
        model = runner.resnet50(weights=weights)
        official = weights.get_state_dict(progress=False, check_hash=True)
        trace.constructor["official_backbone_checks_equal"] = {
            name: bool(torch.equal(model.state_dict()[name].cpu(), official[name].cpu()))
            for name in ("conv1.weight", "layer4.2.conv3.weight")
        }
        trace.constructor["rng_after_official_weight_check"] = rng_fingerprints()
        model.fc = nn.Linear(model.fc.in_features, len(runner.CLASSES))
        model = model.to(device)
        trace.record_model(model, str(weights))
        optimizer = torch.optim.SGD(
            model.parameters(),
            lr=float(config["deep"]["learning_rate"]),
            momentum=float(config["deep"]["momentum"]),
        )
        dataset = runner.PACSImages(training, image_root, training=True)
        generator = torch.Generator().manual_seed(train_seed)
        loader = DataLoader(
            dataset,
            batch_size=int(config["training"]["batch_size"]),
            shuffle=True,
            num_workers=int(config["training"]["workers"]),
            generator=generator,
            pin_memory=device.type == "cuda",
        )
        # The prior isolated diagnostic also constructed its VALIDATION loader
        # before training. Its private generator leaves the train RNG untouched.
        validation_loader = DataLoader(
            runner.PACSImages(validation, image_root, training=False),
            batch_size=int(config["training"]["batch_size"]),
            shuffle=False,
            num_workers=0,
            generator=torch.Generator().manual_seed(9981),
        )
        for _ in range(int(config["training"]["epochs"])):
            model.train()
            for images, labels, _, _ in loader:
                # The earlier isolated diagnostic used blocking Tensor.to().
                images = images.to(device)
                labels = labels.to(device)
                optimizer.zero_grad(set_to_none=True)
                logits = model(images)
                loss = nn.functional.cross_entropy(logits, labels)
                loss.backward()
                optimizer.step()
                # The prior isolated path materialized loss and accuracy on CPU
                # after every step, synchronizing MPS before the next DataLoader batch.
                _ = float(loss.detach().cpu())
                _ = int((logits.detach().argmax(1) == labels).sum().cpu())
            model.eval()
            with torch.inference_mode():
                for images, labels, _, _ in validation_loader:
                    output = model(images.to(device))
                    _ = float(originals["cross_entropy"](output, labels.to(device)).cpu())
                    _ = output.argmax(1).cpu()
        del model
    except TraceStop:
        pass
    finally:
        restore_tracing(runner, originals)


def compare_values(a, b) -> bool:
    return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", choices=("mps", "cpu", "auto"), default="auto")
    parser.add_argument("--max-steps", type=int, default=None, help="stop each path after N steps (for first-divergence CPU checks)")
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv")
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/pilots/b2_pacs_calibration/diagnostics/teacher_path_comparison_seed0.json",
    )
    args = parser.parse_args()
    runner = load_runner()
    config = json.loads((ROOT / "experiments/pilots/b2_pacs_calibration/config.json").read_text())
    frame = pd.read_csv(args.manifest)
    splits = runner.stratified_splits(frame, args.seed)
    lookup = frame.set_index("sample_id", drop=False)
    training = lookup.loc[np.concatenate([splits["base"], splits["transfer"]])].reset_index(drop=True)
    validation = lookup.loc[splits["validation"]].reset_index(drop=True)
    if args.device == "auto":
        device = torch.device(
            "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        )
    else:
        device = torch.device(args.device)
    if device.type == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS was requested but is unavailable; refusing a silent device change")
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable; refusing a silent device change")

    seed = args.seed
    train_seed = seed + 30000
    steps = math.ceil(len(training) / int(config["training"]["batch_size"]))
    snapshot_root = Path(tempfile.mkdtemp(prefix="b2_teacher_path_compare_"))
    trace_a = FitTrace("A", steps, snapshot_root / "A", args.max_steps)
    trace_b = FitTrace("B", steps, snapshot_root / "B", args.max_steps)
    output_dir = snapshot_root / "normal_runner_output"
    started = time.perf_counter()
    run_normal_path(
        runner,
        trace_a,
        seed,
        train_seed,
        args.image_root,
        args.manifest,
        output_dir,
        config,
        device,
    )
    run_isolated_path(
        runner,
        trace_b,
        seed,
        train_seed,
        training,
        validation,
        args.image_root,
        device,
        config,
    )

    epochs = int(config["training"]["epochs"])
    if args.max_steps is None:
        train_a = trace_a.train_by_epoch(epochs)
        train_b = trace_b.train_by_epoch(epochs)
        validation_a = validation_by_epoch(
            runner, trace_a, validation, args.image_root, device, config["training"]["batch_size"], epochs
        )
        validation_b = validation_by_epoch(
            runner, trace_b, validation, args.image_root, device, config["training"]["batch_size"], epochs
        )
        for train_row, val_row in zip(train_a, validation_a, strict=True):
            train_row.update(val_row)
        for train_row, val_row in zip(train_b, validation_b, strict=True):
            train_row.update(val_row)
    else:
        train_a, train_b = [], []

    training_fingerprint = sha256_bytes(
        "\n".join(
            f"{int(row.sample_id)}|{row.domain}|{int(row.label)}|{row.class_name}|{row.relative_path}|{row.sha256}"
            for row in training.itertuples()
        ).encode()
    )
    data_summary = {
        "n_train": len(training),
        "training_sample_ids_sha256": sha256_bytes(",".join(map(str, training.sample_id.tolist())).encode()),
        "training_rows_and_image_hashes_sha256": training_fingerprint,
        "domain_class_counts": {
            f"{domain}|{class_name}": int(count)
            for (domain, class_name), count in training.groupby(["domain", "class_name"]).size().items()
        },
    }
    env = {
        "python": sys.version,
        "torch": torch.__version__,
        "device": str(device),
        "mps_built": bool(torch.backends.mps.is_built()),
        "mps_available": bool(torch.backends.mps.is_available()),
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
        "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
        "mps_fallback_env": os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK"),
        "configured_seed": seed,
        "model_train_seed": train_seed,
    }
    comparisons = {
        "data_fingerprint_equal": True,
        "seed_calls_equal": compare_values(trace_a.seed_calls[-1]["rng_after_seed"], trace_b.seed_calls[-1]["rng_after_seed"]),
        "constructor_rng_equal": compare_values(
            trace_a.constructor.get("rng_before_resnet_constructor"),
            trace_b.constructor.get("rng_before_resnet_constructor"),
        ),
        "pre_head_state_equal": trace_a.constructor.get("pre_head_state_dict_sha256")
        == trace_b.constructor.get("pre_head_state_dict_sha256"),
        "initial_state_dict_equal": trace_a.model_init.get("state_dict_sha256")
        == trace_b.model_init.get("state_dict_sha256"),
        "initial_fc_weight_equal": trace_a.model_init.get("fc_weight_sha256")
        == trace_b.model_init.get("fc_weight_sha256"),
        "initial_fc_bias_equal": trace_a.model_init.get("fc_bias_sha256")
        == trace_b.model_init.get("fc_bias_sha256"),
        "first_batch_ids_equal": trace_a.train_ids == trace_b.train_ids,
        "first_batch_labels_equal": trace_a.train_labels == trace_b.train_labels,
        "first_batch_transformed_tensors_equal": trace_a.transformed_images == trace_b.transformed_images,
        "optimizer_equal": compare_values(trace_a.optimizer, trace_b.optimizer),
        "first_batch_cpu_samples_equal": trace_a.first_batch.get("samples") == trace_b.first_batch.get("samples"),
        "first_batch_targets_at_cross_entropy_equal": trace_a.first_batch.get("labels") == trace_b.first_batch.get("labels"),
        "first_batch_logits_equal": trace_a.first_batch.get("logits_sha256") == trace_b.first_batch.get("logits_sha256"),
        "first_batch_loss_equal": trace_a.first_batch.get("loss") == trace_b.first_batch.get("loss"),
        "first_step_equal": compare_values(trace_a.first_step, trace_b.first_step),
        "first_8_batches_equal": compare_values(trace_a.batch_events, trace_b.batch_events),
        "first_8_steps_equal": compare_values(trace_a.step_events, trace_b.step_events),
        "epoch_metrics_equal": compare_values(train_a, train_b),
    }
    first_divergence = next((name for name, equal in comparisons.items() if not equal), None)
    report = {
        "diagnostic": "B2.0 normal runner vs isolated ResNet-50 teacher path",
        "seed": seed,
        "device": str(device),
        "test_opened": False,
        "mobile_net_run": False,
        "elapsed_seconds": time.perf_counter() - started,
        "max_steps": args.max_steps,
        "environment": env,
        "dataset": data_summary,
        "paths": {
            "A_normal_runner": {
                "entry_point": "run.py main() limited diagnostically to the seed teacher fit",
                "host_to_device_transfer": "Tensor.to(device, non_blocking=True)",
                "rng_seed_calls": trace_a.seed_calls,
                "model_constructor": trace_a.constructor,
                "initial_model": trace_a.model_init,
                "optimizer": trace_a.optimizer,
                "first_batch": trace_a.first_batch,
                "first_batch_sample_ids": trace_a.train_ids,
                "first_batch_labels": trace_a.train_labels,
                "first_batch_domains": trace_a.train_domains,
                "first_step": trace_a.first_step,
                "first_batches": trace_a.batch_events,
                "first_steps": trace_a.step_events,
                "epoch_metrics": train_a,
            },
            "B_isolated_diagnostic": {
                "entry_point": "standalone constructor and fit loop used by the earlier diagnostic",
                "host_to_device_transfer": "Tensor.to(device), blocking default",
                "per_batch_cpu_synchronization": "loss.cpu() and training_accuracy.cpu() after every optimizer step",
                "rng_seed_calls": trace_b.seed_calls,
                "model_constructor": trace_b.constructor,
                "initial_model": trace_b.model_init,
                "optimizer": trace_b.optimizer,
                "first_batch": trace_b.first_batch,
                "first_batch_sample_ids": trace_b.train_ids,
                "first_batch_labels": trace_b.train_labels,
                "first_batch_domains": trace_b.train_domains,
                "first_step": trace_b.first_step,
                "first_batches": trace_b.batch_events,
                "first_steps": trace_b.step_events,
                "epoch_metrics": train_b,
            },
        },
        "comparisons": comparisons,
        "first_divergence": first_divergence,
        "interpretation": (
            "No A/B divergence measured through epoch 3."
            if first_divergence is None
            else f"First unequal checkpoint: {first_divergence}."
        ),
        "temporary_snapshots": str(snapshot_root),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(json.dumps({"output": str(args.output), "first_divergence": first_divergence, "comparisons": comparisons}, indent=2))


if __name__ == "__main__":
    main()
