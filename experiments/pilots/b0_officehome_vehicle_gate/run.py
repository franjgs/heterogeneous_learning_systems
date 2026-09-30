#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms

SEEDS = [0, 1, 2, 3, 4]
DOMAINS = ["art", "clipart", "product", "real_world"]
MODEL_NAMES = ["resnet18", "mobilenet_v2"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
PROTOCOL_REL = "docs/experimental_foundations/B0_OFFICEHOME_VEHICLE_GATE.md"
N_DEVELOP = 50
BASE_PER_CLASS = 3
VAL_FRACTION = 0.25
BASE_EPOCHS = 25
DEVELOP_EPOCHS = 10
LEARNING_RATE = 0.05
WEIGHT_DECAY = 1e-4


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


DOMAIN_ALIASES = {
    "art": {"art"},
    "clipart": {"clipart"},
    "product": {"product"},
    "real_world": {"realworld"},
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def discover_domains(image_root: Path) -> dict[str, Path]:
    if not image_root.is_dir():
        raise RuntimeError(f"Office-Home image root is not a directory: {image_root}")
    candidates = [image_root]
    candidates += [p for p in image_root.iterdir() if p.is_dir()]
    for root in candidates:
        children = [p for p in root.iterdir() if p.is_dir()]
        by_norm = {norm(p.name): p for p in children}
        found = {}
        for canonical, aliases in DOMAIN_ALIASES.items():
            for alias in aliases:
                if alias in by_norm:
                    found[canonical] = by_norm[alias]
                    break
        if len(found) == 4:
            return found
    raise RuntimeError(
        "Could not discover Art, Clipart, Product and Real World domain directories "
        f"under {image_root}"
    )


def inventory(domain_paths: dict[str, Path]):
    rows = []
    classes_by_domain = {}
    for domain in DOMAINS:
        dpath = domain_paths[domain]
        class_dirs = sorted([p for p in dpath.iterdir() if p.is_dir()])
        classes = [p.name for p in class_dirs]
        classes_by_domain[domain] = set(classes)
        for cdir in class_dirs:
            for p in sorted(cdir.rglob("*")):
                if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
                    rows.append({
                        "sample_id": f"{domain}/{cdir.name}/{p.relative_to(cdir).as_posix()}",
                        "domain": domain,
                        "class_name": cdir.name,
                        "path": str(p.resolve()),
                    })
    if not rows:
        raise RuntimeError("No images found")
    ref = classes_by_domain[DOMAINS[0]]
    for d in DOMAINS[1:]:
        if classes_by_domain[d] != ref:
            raise RuntimeError(f"Class set mismatch: {DOMAINS[0]} vs {d}")
    classes = sorted(ref)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    for r in rows:
        r["label"] = class_to_idx[r["class_name"]]
    if len({r["sample_id"] for r in rows}) != len(rows):
        raise RuntimeError("Office-Home inventory has duplicate sample IDs")
    return rows, classes


def inventory_fingerprint(rows) -> str:
    h = hashlib.sha256()
    for r in rows:
        p = Path(r["path"])
        h.update(f"{r['sample_id']}\0{p.stat().st_size}\n".encode())
    return h.hexdigest()


def make_splits(rows, seed, base_per_class, val_fraction, n_develop):
    rng = random.Random(seed)
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["domain"], r["class_name"])].append(r)
    out = []
    for (domain, cls), items in sorted(grouped.items()):
        items = list(items)
        rng.shuffle(items)
        if len(items) < base_per_class + 2:
            raise RuntimeError(
                f"Too few images for domain={domain} class={cls}: {len(items)}"
            )
        base = items[:base_per_class]
        rem = items[base_per_class:]
        n_val = max(1, int(round(len(rem) * val_fraction)))
        if n_val >= len(rem):
            n_val = len(rem) - 1
        val = rem[-n_val:]
        dev = rem[:-n_val]
        for split, seq in [("base", base), ("development", dev), ("validation", val)]:
            for r in seq:
                out.append({**r, "seed": seed, "split": split})
    # Verify each domain can supply N development examples stratified.
    for d in DOMAINS:
        dev = [r for r in out if r["domain"] == d and r["split"] == "development"]
        if len(dev) < n_develop:
            raise RuntimeError(f"{d}: only {len(dev)} development images, need {n_develop}")
    return out


def stratified_opportunity(split_rows, domain, n, seed):
    by_class = defaultdict(list)
    for r in split_rows:
        if r["domain"] == domain and r["split"] == "development":
            by_class[r["class_name"]].append(r)
    rng = random.Random(100000 + seed * 100 + DOMAINS.index(domain))
    for v in by_class.values():
        rng.shuffle(v)
    classes = sorted(by_class)
    rng.shuffle(classes)
    chosen = []
    cursor = {c: 0 for c in classes}
    while len(chosen) < n:
        progressed = False
        for c in classes:
            j = cursor[c]
            if j < len(by_class[c]) and len(chosen) < n:
                chosen.append(by_class[c][j])
                cursor[c] += 1
                progressed = True
        if not progressed:
            break
    if len(chosen) != n:
        raise RuntimeError(f"Could not draw N={n} stratified opportunity for {domain}")
    return chosen


class ImageRows(Dataset):
    def __init__(self, rows, tfm):
        self.rows = rows
        self.tfm = tfm
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, idx):
        r = self.rows[idx]
        with Image.open(r["path"]) as im:
            x = self.tfm(im.convert("RGB"))
        return x, int(r["label"]), r["path"]


def build_backbone(name, device):
    if name == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT
        net = models.resnet18(weights=weights)
        dim = net.fc.in_features
        net.fc = nn.Identity()
        tfm = weights.transforms()
    elif name == "mobilenet_v2":
        weights = models.MobileNet_V2_Weights.DEFAULT
        net = models.mobilenet_v2(weights=weights)
        dim = net.classifier[1].in_features
        net.classifier = nn.Identity()
        tfm = weights.transforms()
    else:
        raise ValueError(name)
    net.eval()
    for p in net.parameters():
        p.requires_grad_(False)
    return net.to(device), dim, tfm


def validate_frozen_representation(name, device, n_classes):
    net, dim, tfm = build_backbone(name, device)
    if any(p.requires_grad for p in net.parameters()):
        raise RuntimeError(f"{name} backbone is not fully frozen")
    head = nn.Linear(dim, n_classes)
    trainable = [n for n, p in head.named_parameters() if p.requires_grad]
    if trainable != ["weight", "bias"]:
        raise RuntimeError(f"{name} does not expose exactly one trainable linear head")
    return net, dim, tfm, trainable


@torch.inference_mode()
def embed_rows(net, tfm, rows, device, batch_size):
    ds = ImageRows(rows, tfm)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)
    feats, labels, paths = [], [], []
    for x, y, p in dl:
        z = net(x.to(device)).detach().cpu()
        if z.ndim > 2:
            z = torch.flatten(z, 1)
        feats.append(z)
        labels.append(y.clone())
        paths.extend(list(p))
    return torch.cat(feats), torch.cat(labels).long(), paths


def load_or_compute_embeddings(name, rows, inventory_sha256, cache, device, batch_size):
    path = cache / f"{name}_embeddings.pt"
    expected_ids = [r["sample_id"] for r in rows]
    expected_labels = torch.tensor([int(r["label"]) for r in rows], dtype=torch.long)
    if path.exists():
        payload = torch.load(path, map_location="cpu", weights_only=False)
        cached_labels = payload.get("labels")
        valid = (
            payload.get("model") == name
            and payload.get("inventory_sha256") == inventory_sha256
            and payload.get("sample_ids") == expected_ids
            and isinstance(cached_labels, torch.Tensor)
            and torch.equal(cached_labels, expected_labels)
            and isinstance(payload.get("features"), torch.Tensor)
            and len(payload["features"]) == len(rows)
        )
        if valid:
            return payload["features"], payload["labels"], expected_ids, path, True

    net, dim, tfm, _ = validate_frozen_representation(name, device, len(set(expected_labels.tolist())))
    features, labels, paths = embed_rows(net, tfm, rows, device, batch_size)
    del net
    if paths != [r["path"] for r in rows] or not torch.equal(labels, expected_labels):
        raise RuntimeError(f"{name} embedding order does not match the inventory")
    payload = {
        "model": name,
        "inventory_sha256": inventory_sha256,
        "sample_ids": expected_ids,
        "labels": labels,
        "features": features,
        "embedding_dim": dim,
    }
    torch.save(payload, path)
    return features, labels, expected_ids, path, False


def balanced_accuracy(y_true, y_pred, n_classes):
    recalls = []
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    for c in range(n_classes):
        mask = yt == c
        if mask.any():
            recalls.append(float((yp[mask] == c).mean()))
    return float(np.mean(recalls)) if recalls else float("nan")


def train_head(X, y, dim, n_classes, seed, epochs, lr, weight_decay):
    torch.manual_seed(seed)
    head = nn.Linear(dim, n_classes)
    opt = torch.optim.SGD(head.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        order = torch.randperm(len(y), generator=g)
        for idx in order.split(min(64, len(y))):
            logits = head(X[idx])
            loss = loss_fn(logits, y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
    return head


def continue_head(head, X, y, seed, epochs, lr, weight_decay):
    h = nn.Linear(head.in_features, head.out_features)
    h.load_state_dict({k: v.detach().clone() for k, v in head.state_dict().items()})
    opt = torch.optim.SGD(h.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.CrossEntropyLoss()
    g = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        order = torch.randperm(len(y), generator=g)
        for idx in order.split(min(64, len(y))):
            logits = h(X[idx])
            loss = loss_fn(logits, y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
    return h


@torch.inference_mode()
def score(head, X, y, n_classes):
    pred = head(X).argmax(1).numpy()
    return balanced_accuracy(y.numpy(), pred, n_classes)


def sign_label(x):
    if x > 0: return "positive"
    if x < 0: return "negative"
    return "zero"


def write_csv(path, rows, fieldnames=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image-root", required=True)
    ap.add_argument("--output-dir", default="results/pilots/b0_officehome_vehicle_gate")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--batch-size", type=int, default=128)
    args = ap.parse_args()

    rr = repo_root()
    protocol = rr / PROTOCOL_REL
    if not protocol.exists():
        raise RuntimeError(f"Missing frozen protocol: {protocol}")
    image_root = Path(args.image_root).expanduser().resolve()
    domain_paths = discover_domains(image_root)
    rows, classes = inventory(domain_paths)
    inventory_sha256 = inventory_fingerprint(rows)

    all_splits = []
    for seed in SEEDS:
        all_splits.extend(make_splits(rows, seed, BASE_PER_CLASS,
                                      VAL_FRACTION, N_DEVELOP))
    opportunities = {}
    for seed in SEEDS:
        seed_rows = [r for r in all_splits if r["seed"] == seed]
        for domain in DOMAINS:
            selected = stratified_opportunity(seed_rows, domain, N_DEVELOP, seed)
            opportunities[(seed, domain)] = selected
    opportunity_ids = {
        (seed, domain): {r["sample_id"] for r in selected}
        for (seed, domain), selected in opportunities.items()
    }
    for r in all_splits:
        r["opportunity_n50"] = int(
            r["split"] == "development"
            and r["sample_id"] in opportunity_ids[(r["seed"], r["domain"])]
        )
    planned = {
        "dataset_images": len(rows),
        "classes": len(classes),
        "domains": DOMAINS,
        "models": MODEL_NAMES,
        "seeds": SEEDS,
        "n_develop": N_DEVELOP,
        "interventions": len(MODEL_NAMES) * len(SEEDS) * len(DOMAINS),
        "test_surface": False,
        "protocol_sha256": sha256_file(protocol),
        "runner_sha256": sha256_file(Path(__file__)),
        "inventory_sha256": inventory_sha256,
    }
    if planned["interventions"] != 40 or len(opportunities) != 20:
        raise RuntimeError("B0 must contain exactly 40 interventions and 20 shared opportunities")

    # Construction verifies torchvision weights/model definitions. It may fetch
    # pretrained weights if they are not already in the local torch cache.
    dims = {}
    for m in MODEL_NAMES:
        net, dim, _, trainable = validate_frozen_representation(
            m, args.device, len(classes)
        )
        dims[m] = dim
        planned.setdefault("trainable_parameters", {})[m] = trainable
        del net
    planned["embedding_dims"] = dims

    if args.dry_run:
        print(json.dumps(planned, indent=2))
        print("Dry-run successful: dataset/splits/models valid; 40 interventions planned; TEST absent.")
        return

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    cache = outdir / ".cache"
    cache.mkdir(exist_ok=True)

    manifest = {
        **planned,
        "image_root": str(image_root),
        "domain_paths": {k: str(v) for k, v in domain_paths.items()},
        "base_per_class": BASE_PER_CLASS,
        "val_fraction": VAL_FRACTION,
        "base_epochs": BASE_EPOCHS,
        "develop_epochs": DEVELOP_EPOCHS,
        "lr": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "device": args.device,
        "torch_version": torch.__version__,
        "torchvision_version": __import__("torchvision").__version__,
        "started_unix": time.time(),
    }
    (outdir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_csv(outdir / "split_manifest.csv", all_splits)
    manifest["split_manifest_sha256"] = sha256_file(outdir / "split_manifest.csv")

    base_rows_out = []
    state_rows = []

    # For each model, embeddings are deterministic functions of images and
    # frozen ImageNet weights, so compute the complete inventory once.
    for model_name in MODEL_NAMES:
        print(f"Embedding all images with {model_name}...", flush=True)
        dim = dims[model_name]
        Xall, yall, sample_ids, cache_path, cache_reused = load_or_compute_embeddings(
            model_name, rows, inventory_sha256, cache, args.device, args.batch_size
        )
        sample_to_idx = {sample_id: i for i, sample_id in enumerate(sample_ids)}
        manifest.setdefault("embedding_cache", {})[model_name] = {
            "path": str(cache_path.resolve()),
            "sha256": sha256_file(cache_path),
            "reused": cache_reused,
            "rows": len(Xall),
            "dimension": int(Xall.shape[1]),
        }

        def tensors(selected):
            idx = torch.tensor(
                [sample_to_idx[r["sample_id"]] for r in selected], dtype=torch.long
            )
            return Xall[idx], yall[idx]

        for seed in SEEDS:
            sr = [r for r in all_splits if r["seed"] == seed]
            base = [r for r in sr if r["split"] == "base"]
            Xb, yb = tensors(base)
            base_head = train_head(Xb, yb, dim, len(classes), seed,
                                   BASE_EPOCHS, LEARNING_RATE, WEIGHT_DECAY)

            base_scores = {}
            for measured_domain in DOMAINS:
                val = [r for r in sr if r["split"] == "validation"
                       and r["domain"] == measured_domain]
                Xv, yv = tensors(val)
                sc = score(base_head, Xv, yv, len(classes))
                base_scores[measured_domain] = sc
                base_rows_out.append({
                    "model": model_name, "seed": seed,
                    "measured_domain": measured_domain,
                    "balanced_accuracy": sc,
                })

            for target_domain in DOMAINS:
                opp = opportunities[(seed, target_domain)]
                Xo, yo = tensors(opp)
                dseed = 10000 + seed * 100 + DOMAINS.index(target_domain)
                developed = continue_head(base_head, Xo, yo, dseed,
                                          DEVELOP_EPOCHS, LEARNING_RATE,
                                          WEIGHT_DECAY)
                for measured_domain in DOMAINS:
                    val = [r for r in sr if r["split"] == "validation"
                           and r["domain"] == measured_domain]
                    Xv, yv = tensors(val)
                    after = score(developed, Xv, yv, len(classes))
                    before = base_scores[measured_domain]
                    delta = after - before
                    state_rows.append({
                        "model": model_name,
                        "seed": seed,
                        "target_domain": target_domain,
                        "measured_domain": measured_domain,
                        "base_balanced_accuracy": before,
                        "after_balanced_accuracy": after,
                        "delta_competence": delta,
                        "is_local": int(target_domain == measured_domain),
                    })
                print(f"{model_name} seed={seed} target={target_domain} done", flush=True)

    write_csv(outdir / "base_competences.csv", base_rows_out)
    write_csv(outdir / "state_metrics.csv", state_rows)

    # Heterogeneity summary
    base_lookup = {(r["model"], int(r["seed"]), r["measured_domain"]):
                   float(r["balanced_accuracy"]) for r in base_rows_out}
    hetero = []
    identical_all = True
    for d in DOMAINS:
        diffs = []
        for s in SEEDS:
            a = base_lookup[("resnet18", s, d)]
            b = base_lookup[("mobilenet_v2", s, d)]
            diffs.append(a - b)
            hetero.append({
                "row_type": "seed_domain",
                "seed": s,
                "domain": d,
                "resnet18_base": a,
                "mobilenet_v2_base": b,
                "resnet_minus_mobilenet": a - b,
                "resnet18_mean": "",
                "mobilenet_v2_mean": "",
                "mean_resnet_minus_mobilenet": "",
                "resnet_better_seeds": "",
                "mobilenet_better_seeds": "",
                "equal_seeds": "",
                "numerically_identical_all_seeds": "",
                "resnet_dominates_all_cells": "",
                "mobilenet_dominates_all_cells": "",
                "all_cells_numerically_identical": "",
            })
        identical = all(x == 0 for x in diffs)
        identical_all &= identical
        hetero.append({
            "row_type": "domain_summary",
            "seed": "",
            "domain": d,
            "resnet18_base": "",
            "mobilenet_v2_base": "",
            "resnet_minus_mobilenet": "",
            "resnet18_mean": np.mean([base_lookup[("resnet18", s, d)] for s in SEEDS]),
            "mobilenet_v2_mean": np.mean([base_lookup[("mobilenet_v2", s, d)] for s in SEEDS]),
            "mean_resnet_minus_mobilenet": np.mean(diffs),
            "resnet_better_seeds": sum(x > 0 for x in diffs),
            "mobilenet_better_seeds": sum(x < 0 for x in diffs),
            "equal_seeds": sum(x == 0 for x in diffs),
            "numerically_identical_all_seeds": int(identical),
            "resnet_dominates_all_cells": "",
            "mobilenet_dominates_all_cells": "",
            "all_cells_numerically_identical": "",
        })
    all_diffs = [
        base_lookup[("resnet18", s, d)] - base_lookup[("mobilenet_v2", s, d)]
        for s in SEEDS for d in DOMAINS
    ]
    resnet_dominates_all = all(x >= 0 for x in all_diffs) and any(x > 0 for x in all_diffs)
    mobile_dominates_all = all(x <= 0 for x in all_diffs) and any(x < 0 for x in all_diffs)
    hetero.append({
        "row_type": "global_summary",
        "seed": "",
        "domain": "",
        "resnet18_base": "",
        "mobilenet_v2_base": "",
        "resnet_minus_mobilenet": "",
        "resnet18_mean": "",
        "mobilenet_v2_mean": "",
        "mean_resnet_minus_mobilenet": "",
        "resnet_better_seeds": "",
        "mobilenet_better_seeds": "",
        "equal_seeds": "",
        "numerically_identical_all_seeds": "",
        "resnet_dominates_all_cells": int(resnet_dominates_all),
        "mobilenet_dominates_all_cells": int(mobile_dominates_all),
        "all_cells_numerically_identical": int(identical_all),
    })
    write_csv(outdir / "heterogeneity_summary.csv", hetero)

    # Transition summaries and local effectiveness
    trans = []
    local = []
    for m in MODEL_NAMES:
        for td in DOMAINS:
            for md in DOMAINS:
                vals = [float(r["delta_competence"]) for r in state_rows
                        if r["model"] == m and r["target_domain"] == td
                        and r["measured_domain"] == md]
                signs = [sign_label(v) for v in vals]
                cnt = Counter(signs)
                majority_n = max(cnt.values())
                leaders = [sign for sign in ("positive", "negative", "zero")
                           if cnt[sign] == majority_n]
                majority_sign = leaders[0] if len(leaders) == 1 else "tie"
                stable = majority_sign != "tie" and majority_n >= 4
                row = {
                    "model": m, "target_domain": td, "measured_domain": md,
                    "mean_delta": float(np.mean(vals)),
                    "std_delta": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                    "positive_seeds": cnt["positive"],
                    "negative_seeds": cnt["negative"],
                    "zero_seeds": cnt["zero"],
                    "majority_sign": majority_sign,
                    "majority_n": majority_n,
                    "sign_agreement_4of5": int(stable),
                }
                trans.append(row)
                if td == md:
                    positive = cnt["positive"] >= 4 and np.mean(vals) > 0
                    local.append({
                        **row,
                        "local_positive_4of5_and_mean": int(positive),
                    })
    write_csv(outdir / "transition_summary.csv", trans)
    write_csv(outdir / "local_effectiveness.csv", local)

    positive_local = sum(int(r["local_positive_4of5_and_mean"]) for r in local)
    stable_components = sum(int(r["sign_agreement_4of5"]) for r in trans)
    total_components = len(trans)

    diagnostic = f"""# B0 diagnostic

TEST surface: **absent**.

## G1 — base heterogeneity

- Numerically identical across all seed/domain cells: **{str(identical_all).lower()}**
- ResNet-18 weakly dominates MobileNetV2 in every seed/domain cell: **{str(resnet_dominates_all).lower()}**
- MobileNetV2 weakly dominates ResNet-18 in every seed/domain cell: **{str(mobile_dominates_all).lower()}**

See `heterogeneity_summary.csv` for domain-level paired summaries.

## G2 — development effectiveness

- Locally positive learner x target-domain cells: **{positive_local}/8**

A local cell is positive only with >0 local Delta C in at least 4/5 seeds and
positive five-seed mean.

## G3 — transition predictability

- Transition components with 4/5 sign agreement: **{stable_components}/{total_components}**

See `transition_summary.csv` for the complete vectors.

## Decision

**NO AUTOMATIC ADVANCE/STOP IS EMITTED.**

The frozen protocol intentionally avoids inventing post-hoc numerical thresholds
for portfolio usefulness or whole-vector predictability. Inspect G1-G3 together.
If the structural requirements fail, STOP B rather than tuning B0.
"""
    (outdir / "B0_DIAGNOSTIC.md").write_text(diagnostic)
    manifest["finished_unix"] = time.time()
    manifest["test_surface"] = False
    manifest["rows"] = {
        "base_competences": len(base_rows_out),
        "state_metrics": len(state_rows),
        "transition_summary": len(trans),
        "local_effectiveness": len(local),
    }
    (outdir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(diagnostic)


if __name__ == "__main__":
    main()
