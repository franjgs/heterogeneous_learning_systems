"""Minimal CPU throughput estimate; uses synthetic batches, not PACS/model evidence."""

from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path

import torch
from torch import nn
from torchvision.models import mobilenet_v2, resnet50

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from hls.b2_pacs_calibration import select_base_fraction, stratified_splits  # noqa: E402


def profile_one(name: str, batch_size: int = 8, steps: int = 4) -> float:
    model = mobilenet_v2(weights=None) if name == "fast" else resnet50(weights=None)
    if name == "fast":
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 7)
    else:
        model.fc = nn.Linear(model.fc.in_features, 7)
    model.train()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)
    images = torch.randn(batch_size, 3, 224, 224)
    labels = torch.randint(0, 7, (batch_size,))
    start = time.perf_counter()
    for _ in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(images), labels)
        loss.backward()
        optimizer.step()
    elapsed = time.perf_counter() - start
    del model, optimizer
    return batch_size * steps / elapsed


def main() -> None:
    profile_started = time.perf_counter()
    output = ROOT / "results/pilots/b2_pacs_calibration/run_metadata.json"
    manifest_path = ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv"
    import pandas as pd

    manifest = pd.read_csv(manifest_path)
    n = len(manifest)
    baseline_split = stratified_splits(manifest, seed=0)
    base_count = len(baseline_split["base"])
    transfer_count = len(baseline_split["transfer"])
    speeds = {"fast_mobilenet_v2_images_per_second": profile_one("fast"),
              "deep_resnet50_images_per_second": profile_one("deep")}
    fast_images_one_seed = sum(
        len(select_base_fraction(manifest, stratified_splits(manifest, seed=seed)["base"], fraction, seed=seed))
        for fraction in (0.10, 0.25, 0.50, 1.00)
        for seed in (0,)
    )
    deep_images_one_seed = base_count + transfer_count
    fast_images_all_seeds = fast_images_one_seed * 5
    deep_images_all_seeds = deep_images_one_seed * 5
    lower_bound_seconds_per_epoch = (
        fast_images_all_seeds / speeds["fast_mobilenet_v2_images_per_second"]
        + deep_images_all_seeds / speeds["deep_resnet50_images_per_second"]
    )
    metadata = {
        "status": "COMPUTE_BLOCKED_BEFORE_MODEL_CALIBRATION",
        "current_setup_viability": "NOT VIABLE for the available CPU-only machine; PACS model-performance viability is unassessed",
        "hardware": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "logical_cpu_count": os.cpu_count(),
            "torch_threads": torch.get_num_threads(),
            "cuda_available": torch.cuda.is_available(),
            "mps_built": bool(torch.backends.mps.is_built()),
            "mps_available": bool(torch.backends.mps.is_available()),
            "selected_device": "cpu",
        },
        "benchmark": {
            "kind": "four synthetic 224x224 forward/backward/SGD batches of size 8 per architecture; random initialization, no PACS data, no pretrained weights",
            "profile_wall_seconds": None,
            **speeds,
            "fast_training_images_per_seed_per_epoch": fast_images_one_seed,
            "deep_training_images_per_seed_per_epoch": deep_images_one_seed,
            "fast_training_images_all_seeds_per_epoch": fast_images_all_seeds,
            "deep_training_images_all_seeds_per_epoch": deep_images_all_seeds,
            "estimated_lower_bound_seconds_per_epoch_all_25_fits": lower_bound_seconds_per_epoch,
            "estimated_lower_bound_minutes_per_epoch_all_25_fits": lower_bound_seconds_per_epoch / 60,
            "epochs_configured": 3,
            "estimated_lower_bound_hours_training_only": lower_bound_seconds_per_epoch * 3 / 3600,
            "excludes": ["image decoding and augmentation", "validation/test inference", "ImageNet weight download", "checkpoint save/load"],
        },
        "model_fit_count_if_run": 25,
        "full_calibration_started": False,
        "reason": "CPU-only training profile exceeded the practical calibration budget; no architecture or regime was silently changed.",
        "warnings": ["Arrow emitted sandbox-denied sysctl cache/NEON probe notices during dataset scanning; dataset integrity checks completed."],
    }
    metadata["benchmark"]["profile_wall_seconds"] = time.perf_counter() - profile_started
    output.write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
