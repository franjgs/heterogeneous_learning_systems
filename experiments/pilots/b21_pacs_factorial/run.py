"""B2.1 PACS domain-development factorial (validation only, CPU)."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/pilots/b2_pacs_calibration"))
import run as b20  # noqa: E402

DOMAINS = tuple(b20.DOMAINS)
N_VALUES = (25, 50, 100)
COSTS = (0.00, 0.02, 0.05, 0.10, 0.15)


def gamma_learn(vij: float, vi: float, vj: float, v0: float) -> float:
    return vij - vi - vj + v0


def operational_value(scores: dict[str, float], deep: dict[str, float], cost: float) -> tuple[float, dict[str, str]]:
    selected = {domain: ("F" if scores[domain] >= deep[domain] - cost else "D") for domain in DOMAINS}
    value = float(np.mean([max(scores[domain], deep[domain] - cost) for domain in DOMAINS]))
    return value, selected


def fit_from_f0(model, frame: pd.DataFrame, seed: int, config: dict, image_root: Path, device: torch.device):
    """Apply the unchanged B2.0 SGD rule to a model initialized from F0."""
    params = config["fast"]
    optimizer = torch.optim.SGD(model.parameters(), lr=float(params["learning_rate"]), momentum=float(params["momentum"]))
    loader = DataLoader(
        b20.PACSImages(frame, image_root, training=True),
        batch_size=int(config["training"]["batch_size"]), shuffle=True,
        num_workers=int(config["training"]["workers"]), generator=torch.Generator().manual_seed(seed), pin_memory=False,
    )
    model.train()
    for _ in range(int(config["training"]["epochs"])):
        for images, labels, _, _ in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = torch.nn.functional.cross_entropy(model(images), labels)
            loss.backward()
            optimizer.step()
    return model


def score(model, frame, image_root, device, batch_size):
    y, pred, domains, _ = b20.evaluate(model, frame, image_root, device, batch_size)
    return {domain: float(b20.domain_metrics(y, pred, domains)[domain]["balanced_accuracy"]) for domain in DOMAINS}


def select_examples(frame: pd.DataFrame, domain: str, n: int, seed: int) -> pd.DataFrame:
    subset = frame[frame.domain == domain].sort_values("sample_id")
    if len(subset) < n:
        raise ValueError(f"domain {domain} has only {len(subset)} TRANSFER examples; N={n} is infeasible")
    return subset.sample(n=n, random_state=seed).sort_values("sample_id").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "results/pilots/b2_pacs_calibration/dataset_manifest.csv")
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/pilots/b21_pacs_factorial")
    parser.add_argument("--device", choices=("cpu",), default="cpu")
    args = parser.parse_args()
    config = json.loads((ROOT / "experiments/pilots/b2_pacs_calibration/config.json").read_text())
    frame = pd.read_csv(args.manifest)
    b20.validate_manifest(frame)
    if args.device != "cpu":
        raise SystemExit("B2.1 is defined for CPU execution only")
    device = torch.device("cpu")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, state_rows = [], []
    started = time.perf_counter()
    for seed in config["split_seeds"]:
        splits = b20.stratified_splits(frame, seed)
        lookup = frame.set_index("sample_id", drop=False)
        base = lookup.loc[splits["base"]].reset_index(drop=True)
        transfer = lookup.loc[splits["transfer"]].reset_index(drop=True)
        validation = lookup.loc[splits["validation"]].reset_index(drop=True)
        f0_ids = b20.select_base_fraction(frame, base.sample_id, 0.25, seed + 250)
        f0_frame = lookup.loc[f0_ids].reset_index(drop=True)
        teacher_frame = lookup.loc[np.concatenate([splits["base"], splits["transfer"]])].reset_index(drop=True)
        deep, _ = b20.fit_model("deep", seed + 30000, teacher_frame, args.image_root, device, config, 0, 1.0, started)
        f0, _ = b20.fit_model("fast", seed + 2500, f0_frame, args.image_root, device, config, 0, 0.25, started)
        deep_scores, f0_scores = score(deep, validation, args.image_root, device, config["training"]["batch_size"]), score(f0, validation, args.image_root, device, config["training"]["batch_size"])
        state_rows += [{"seed": seed, "state": "D", "N": None, "domain": None, **{f"ba_{d}": deep_scores[d] for d in DOMAINS}}, {"seed": seed, "state": "F0", "N": 0, "domain": None, **{f"ba_{d}": f0_scores[d] for d in DOMAINS}}]
        for n in N_VALUES:
            interventions = {}
            for domain in DOMAINS:
                chosen = select_examples(transfer, domain, n, seed * 10000 + n * 100 + DOMAINS.index(domain))
                interventions[domain] = chosen
                interventions[domain]["label"] = [int(x) for x in predict_labels(deep, chosen, args.image_root, device, config["training"]["batch_size"])]
            states = {"F0": (f0_scores, f0)}
            for domain in DOMAINS:
                model = copy.deepcopy(f0)
                scores = score(fit_from_f0(model, interventions[domain], seed + n + DOMAINS.index(domain), config, args.image_root, device), validation, args.image_root, device, config["training"]["batch_size"])
                states[f"F_{domain}"] = (scores, model)
            for i, left in enumerate(DOMAINS):
                for right in DOMAINS[i + 1:]:
                    model = copy.deepcopy(f0)
                    mixed = pd.concat([interventions[left], interventions[right]], ignore_index=True)
                    scores = score(fit_from_f0(model, mixed, seed + n + 100 + i, config, args.image_root, device), validation, args.image_root, device, config["training"]["batch_size"])
                    states[f"F_{left}_{right}"] = (scores, model)
                    vals = {name: float(np.mean(list(scoreset.values()))) for name, (scoreset, _) in states.items()}
                    rec = {"seed": seed, "N": n, "domain_i": left, "domain_j": right, "gamma_learn": gamma_learn(vals[f"F_{left}_{right}"], vals[f"F_{left}"], vals[f"F_{right}"], vals["F0"]), "v_learn_F0": vals["F0"], "v_learn_Fi": vals[f"F_{left}"], "v_learn_Fj": vals[f"F_{right}"], "v_learn_Fij": vals[f"F_{left}_{right}"]}
                    for name in ("F0", f"F_{left}", f"F_{right}", f"F_{left}_{right}"):
                        rec.update({f"{name}_ba_{d}": states[name][0][d] for d in DOMAINS})
                        for cost in COSTS:
                            value, routing = operational_value(states[name][0], deep_scores, cost)
                            rec[f"{name}_v_oper_c{cost:.2f}"] = value
                            rec[f"{name}_routing_c{cost:.2f}"] = json.dumps(routing, sort_keys=True)
                    for d in DOMAINS:
                        rec[f"delta_{left}_ba_{d}"] = states[f"F_{left}"][0][d] - states["F0"][0][d]
                        rec[f"delta_{right}_ba_{d}"] = states[f"F_{right}"][0][d] - states["F0"][0][d]
                    for cost in COSTS:
                        rec[f"gamma_oper_c{cost:.2f}"] = rec[f"F_{left}_{right}_v_oper_c{cost:.2f}"] - rec[f"F_{left}_v_oper_c{cost:.2f}"] - rec[f"F_{right}_v_oper_c{cost:.2f}"] + rec[f"F0_v_oper_c{cost:.2f}"]
                    rows.append(rec)
    pd.DataFrame(rows).to_csv(args.output_dir / "factorial_results.csv", index=False)
    pd.DataFrame(state_rows).to_csv(args.output_dir / "state_scores.csv", index=False)
    if rows:
        pd.DataFrame(rows).groupby("N").agg({"gamma_learn": ["mean", "std"], **{f"gamma_oper_c{c:.2f}": ["mean", "std"] for c in COSTS}}).reset_index().to_csv(args.output_dir / "aggregates.csv", index=False)
    (args.output_dir / "protocol.json").write_text(json.dumps({"pilot": "B2.1 PACS domain-development factorial", "device": "cpu", "N": list(N_VALUES), "costs": list(COSTS), "domains": list(DOMAINS), "fits": 160, "test_used": False, "p_k": 0.25, "formulas": {"gamma_learn": "V(Fij)-V(Fi)-V(Fj)+V(F0)", "operational": "mean_k max(S_F(k), S_D(k)-c)"}}, indent=2) + "\n")


def predict_labels(model, frame, image_root, device, batch_size):
    y, pred, _, _ = b20.evaluate(model, frame, image_root, device, batch_size)
    return pred.tolist()


if __name__ == "__main__":
    main()
