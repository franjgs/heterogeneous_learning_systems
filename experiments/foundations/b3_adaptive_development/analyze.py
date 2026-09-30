"""Retrospective B3 adaptive-development viability analysis.

Only frozen B2.4 VALIDATION scores are consumed.  This module has no dataset,
model, inference, optimizer, or TEST API.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Mapping

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
B24_ANALYZE_PATH = ROOT / "experiments/pilots/b24_interference_controlled/analyze.py"
B23_OUTPUT = ROOT / "results/pilots/b23_portfolio_opportunity"
B24_OUTPUT = ROOT / "results/pilots/b24_interference_controlled"
DEFAULT_OUTPUT = ROOT / "results/foundations/b3_adaptive_development"

DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
SEEDS = (0, 1, 2, 3, 4)
N_VALUES = (25, 50, 100)
COSTS = (0.0, 0.02, 0.05, 0.10, 0.15)
HORIZONS = (1, 2, 5, 10)
ACTIONS = ("0", "STD", "O50", "REP")
# Literal conservative tie rule requested for B3.
TIE_PRIORITY = ("0", "REP", "O50", "STD")
TOLERANCE = 1e-12
TEST_STATUS = "PREVIOUSLY_OPENED_NOT_USED_IN_B3"
STATES_REQUIRED = 5 + 5 + 60 + 60 + 60


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def operational_value(
    scores: Mapping[str, float], deep: Mapping[str, float], cost: float
) -> float:
    return float(sum(max(float(scores[d]), float(deep[d]) - cost) for d in DOMAINS) / 4.0)


def select_action(delta_values: Mapping[str, float]) -> str:
    """Argmax DeltaV with the literal tie rule 0 > REP > O50 > STD."""
    if set(delta_values) != set(ACTIONS):
        raise ValueError("adaptive selection requires exactly 0, STD, O50, REP")
    best = max(float(value) for value in delta_values.values())
    for action in TIE_PRIORITY:
        if abs(float(delta_values[action]) - best) <= TOLERANCE:
            return action
    raise AssertionError("unreachable tie selection")


def kappa_star(delta_v: float, rho: float, horizon: float) -> float:
    return float(horizon * delta_v - max(rho, 0.0))


def audit_and_load() -> tuple[dict[tuple, dict[str, float]], dict[str, object]]:
    b24_analyze = _load_module("b3_b24_analyze", B24_ANALYZE_PATH)
    scores, audit = b24_analyze.compatibility_audit(B24_OUTPUT, B23_OUTPUT)
    if audit.get("compatible") is not True or audit.get("test") != "CLOSED":
        raise RuntimeError("B2.4 VALIDATION compatibility audit failed")

    b23_manifest = json.loads((B23_OUTPUT / "run_manifest.json").read_text())
    b24_manifest = json.loads((B24_OUTPUT / "run_manifest.json").read_text())
    if b23_manifest["header"].get("test_used") is not False or b24_manifest["header"].get("test_used") is not False:
        raise RuntimeError("historical artifact provenance is not VALIDATION-only")
    artifacts23 = b23_manifest["artifacts"]
    artifacts24 = b24_manifest["artifacts"]
    found = 0
    for seed in SEEDS:
        for state in ("F0", "D"):
            record = artifacts23.get(f"{state}_s{seed}", {})
            path = Path(str(record.get("path", "")))
            if record.get("status") != "complete" or record.get("artifact_type") != state or not path.is_file() or sha256_file(path) != record.get("sha256"):
                raise RuntimeError(f"missing/corrupt required state {state}_s{seed}")
            found += 1
        for domain in DOMAINS:
            for n in N_VALUES:
                required = (
                    (artifacts23, f"Fi_s{seed}_{domain}_n{n}", "singleton"),
                    (artifacts24, f"O50_s{seed}_{domain}_n{n}", "O50"),
                    (artifacts24, f"REP_s{seed}_{domain}_n{n}", "REP"),
                )
                for artifacts, artifact_id, artifact_type in required:
                    record = artifacts.get(artifact_id, {})
                    path = Path(str(record.get("path", "")))
                    if record.get("status") != "complete" or record.get("artifact_type") != artifact_type or not path.is_file() or sha256_file(path) != record.get("sha256"):
                        raise RuntimeError(f"missing/corrupt required state {artifact_id}")
                    found += 1
    if found != STATES_REQUIRED:
        raise RuntimeError(f"state inventory mismatch: {found}/{STATES_REQUIRED}")
    return scores, {
        "states_required": STATES_REQUIRED,
        "states_found": found,
        "provenance_mismatches": 0,
        "compatibility_families": audit["families"],
    }


def action_value_table(scores: dict[tuple, dict[str, float]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        for domain in DOMAINS:
            for n in N_VALUES:
                f0 = scores[("F0", seed, n, domain)]
                deep = scores[("D", seed, n, domain)]
                state_scores = {
                    "0": f0,
                    "STD": scores[("STD", seed, n, domain)],
                    "O50": scores[("O50", seed, n, domain)],
                    "REP": scores[("REP", seed, n, domain)],
                }
                for cost in COSTS:
                    v0 = operational_value(f0, deep, cost)
                    for action in ACTIONS:
                        value = operational_value(state_scores[action], deep, cost)
                        delta = 0.0 if action == "0" else value - v0
                        rows.append({
                            "seed": seed, "target_domain": domain, "N": n, "c": cost,
                            "action": action, "V0": v0, "V_action": value,
                            "DeltaV": delta, "evaluation_split": "validation",
                            "test_metrics_used": False,
                        })
    frame = pd.DataFrame(rows)
    if len(frame) != 60 * 5 * 4 or frame.isna().any().any():
        raise RuntimeError("action-value expansion failed")
    if frame.loc[frame.action == "0", "DeltaV"].abs().max() > TOLERANCE:
        raise RuntimeError("DeltaV(0) identity failed")
    return frame


def adaptive_choice_table(values: pd.DataFrame, scores: dict[tuple, dict[str, float]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (seed, domain, n, cost), group in values.groupby(["seed", "target_domain", "N", "c"], sort=True):
        delta = dict(zip(group.action, group.DeltaV, strict=True))
        chosen = select_action(delta)
        f0 = scores[("F0", int(seed), int(n), str(domain))]
        deep = scores[("D", int(seed), int(n), str(domain))]
        rho = float(f0[str(domain)] - (deep[str(domain)] - float(cost)))
        rows.append({
            "seed": int(seed), "target_domain": domain, "N": int(n), "c": float(cost),
            "chosen_action": chosen, "DeltaV_adaptive": float(delta[chosen]),
            "DeltaV_REP": float(delta["REP"]), "rho": rho,
            "adaptive_positive": bool(delta[chosen] > 0),
            "rep_positive": bool(delta["REP"] > 0),
            "tie_rule": "0 > REP > O50 > STD",
        })
    frame = pd.DataFrame(rows)
    if len(frame) != 300 or frame.isna().any().any():
        raise RuntimeError("adaptive-choice expansion failed")
    return frame


def adaptive_surface(choices: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for choice in choices.itertuples(index=False):
        for horizon in HORIZONS:
            adaptive_star = kappa_star(choice.DeltaV_adaptive, choice.rho, horizon)
            rep_star = kappa_star(choice.DeltaV_REP, choice.rho, horizon)
            rows.append({
                "seed": choice.seed, "target_domain": choice.target_domain, "N": choice.N,
                "c": choice.c, "h": horizon, "chosen_action": choice.chosen_action,
                "rho": choice.rho, "DeltaV_adaptive": choice.DeltaV_adaptive,
                "DeltaV_REP": choice.DeltaV_REP,
                "kappa_star_adaptive": adaptive_star, "kappa_star_REP": rep_star,
                "adaptive_divergence_positive_width": bool(choice.rho >= 0 and adaptive_star > 0),
                "rep_divergence_positive_width": bool(choice.rho >= 0 and rep_star > 0),
                "adaptive_divergence_interval": f"[0,{adaptive_star:.17g})" if choice.rho >= 0 and adaptive_star > 0 else "empty",
                "rep_divergence_interval": f"[0,{rep_star:.17g})" if choice.rho >= 0 and rep_star > 0 else "empty",
            })
    frame = pd.DataFrame(rows)
    if len(frame) != 1200 or frame.isna().any().any():
        raise RuntimeError("adaptive kappa surface expansion failed")
    identity = frame.kappa_star_adaptive - (
        frame.h * frame.DeltaV_adaptive - frame.rho.clip(lower=0)
    )
    if identity.abs().max() > TOLERANCE:
        raise RuntimeError("kappa_star identity failed")
    return frame


def seed_summary(choices: pd.DataFrame, surface: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groupings: list[tuple[str, object, pd.Series, pd.Series]] = [
        ("global", "all", pd.Series(True, index=choices.index), pd.Series(True, index=surface.index))
    ]
    groupings.extend(
        ("seed", seed, choices.seed == seed, surface.seed == seed) for seed in SEEDS
    )
    groupings.extend(
        ("target_domain", domain, choices.target_domain == domain, surface.target_domain == domain)
        for domain in DOMAINS
    )
    groupings.extend(
        ("N", n, choices.N == n, surface.N == n) for n in N_VALUES
    )
    for group_type, group_value, choice_mask, surface_mask in groupings:
        for policy, delta_column, star_column in (
            ("REP", "DeltaV_REP", "kappa_star_REP"),
            ("ADAPTIVE", "DeltaV_adaptive", "kappa_star_adaptive"),
        ):
            selected_choices = choices[choice_mask]
            selected_surface = surface[surface_mask]
            rows.append({
                "group_type": group_type, "group_value": group_value, "policy": policy,
                "DeltaV_observations": len(selected_choices),
                "DeltaV_positive": int((selected_choices[delta_column] > 0).sum()),
                "DeltaV_zero": int((selected_choices[delta_column].abs() <= TOLERANCE).sum()),
                "DeltaV_mean": float(selected_choices[delta_column].mean()),
                "DeltaV_median": float(selected_choices[delta_column].median()),
                "kappa_observations": len(selected_surface),
                "kappa_star_positive": int((selected_surface[star_column] > 0).sum()),
            })
    return pd.DataFrame(rows)


def support_and_viability(
    choices: pd.DataFrame, surface: pd.DataFrame
) -> tuple[list[dict[str, object]], list[dict[str, object]], bool]:
    delta_support: list[dict[str, object]] = []
    for (domain, n, cost), group in choices.groupby(["target_domain", "N", "c"]):
        count = int((group.DeltaV_adaptive > 0).sum())
        delta_support.append({
            "target_domain": domain, "N": int(n), "c": float(cost),
            "positive_seeds": count, "supported_4of5": count >= 4,
        })

    cell_support: list[dict[str, object]] = []
    for (cost, horizon), group in surface.groupby(["c", "h"]):
        eligible = group.assign(
            eligible_star=group.kappa_star_adaptive.where(group.rho >= 0, float("-inf"))
        )
        per_seed_max = eligible.groupby("seed").eligible_star.max().reindex(SEEDS)
        positive_seed_count = int((per_seed_max > 0).sum())
        sorted_stars = sorted((float(value) for value in per_seed_max), reverse=True)
        common_4of5_upper = max(0.0, sorted_stars[3])
        exact = group.groupby(["target_domain", "N"]).adaptive_divergence_positive_width.sum()
        exact_supported = int((exact >= 4).sum())
        cell_support.append({
            "c": float(cost), "h": int(horizon),
            "seeds_with_any_positive_kappa_region": positive_seed_count,
            "common_4of5_kappa_lower": 0.0,
            "common_4of5_kappa_upper": common_4of5_upper,
            "common_4of5_positive_width": bool(common_4of5_upper > 0),
            "exact_domain_N_structures_supported_4of5": exact_supported,
        })
    delta_ok = any(row["supported_4of5"] for row in delta_support)
    kappa_ok = any(row["common_4of5_positive_width"] for row in cell_support)
    return delta_support, cell_support, bool(delta_ok and kappa_ok)


def run(output_dir: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    scores, audit = audit_and_load()
    values = action_value_table(scores)
    choices = adaptive_choice_table(values, scores)
    surface = adaptive_surface(choices)
    delta_support, cell_support, viable = support_and_viability(choices, surface)

    delta_support_frame = pd.DataFrame(delta_support).rename(
        columns={"positive_seeds": "adaptive_DeltaV_positive_seeds"}
    )
    choices = choices.merge(
        delta_support_frame[["target_domain", "N", "c", "adaptive_DeltaV_positive_seeds", "supported_4of5"]],
        on=["target_domain", "N", "c"], validate="many_to_one",
    )
    cell_support_frame = pd.DataFrame(cell_support)
    exact_support = surface.groupby(["target_domain", "N", "c", "h"], as_index=False).agg(
        exact_adaptive_divergence_seeds=("adaptive_divergence_positive_width", "sum")
    )
    surface = surface.merge(cell_support_frame, on=["c", "h"], validate="many_to_one")
    surface = surface.merge(exact_support, on=["target_domain", "N", "c", "h"], validate="many_to_one")
    seeds = seed_summary(choices, surface)

    action_counts = {action: int((choices.chosen_action == action).sum()) for action in TIE_PRIORITY}
    action_counts_by_seed = {
        str(seed): {action: int(((choices.seed == seed) & (choices.chosen_action == action)).sum()) for action in TIE_PRIORITY}
        for seed in SEEDS
    }
    action_counts_seed_groups = {
        "seeds_0_1_3": {
            action: int((choices[choices.seed.isin([0, 1, 3])].chosen_action == action).sum())
            for action in TIE_PRIORITY
        },
        "seeds_2_4": {
            action: int((choices[choices.seed.isin([2, 4])].chosen_action == action).sum())
            for action in TIE_PRIORITY
        },
    }
    positive_rep = {
        str(seed): int(((choices.seed == seed) & choices.rep_positive).sum()) for seed in SEEDS
    }
    positive_adaptive = {
        str(seed): int(((choices.seed == seed) & choices.adaptive_positive).sum()) for seed in SEEDS
    }
    kappa_rep = {
        str(seed): int(((surface.seed == seed) & (surface.kappa_star_REP > 0)).sum()) for seed in SEEDS
    }
    kappa_adaptive = {
        str(seed): int(((surface.seed == seed) & (surface.kappa_star_adaptive > 0)).sum()) for seed in SEEDS
    }
    divergence_rep = {
        str(seed): int(((surface.seed == seed) & surface.rep_divergence_positive_width).sum()) for seed in SEEDS
    }
    divergence_adaptive = {
        str(seed): int(((surface.seed == seed) & surface.adaptive_divergence_positive_width).sum()) for seed in SEEDS
    }
    supported_cells = [row for row in cell_support if row["common_4of5_positive_width"]]
    summary = {
        **audit,
        "technical_status": "PASS",
        "TEST_STATUS": TEST_STATUS,
        "test_metrics_used": False,
        "training_performed": False,
        "checkpoints_created": 0,
        "tie_breaking": "0 > REP > O50 > STD",
        "action_counts": action_counts,
        "action_counts_by_seed": action_counts_by_seed,
        "action_counts_seed_groups": action_counts_seed_groups,
        "DeltaV_positive_by_seed_REP": positive_rep,
        "DeltaV_positive_by_seed_ADAPTIVE": positive_adaptive,
        "kappa_positive_by_seed_REP": kappa_rep,
        "kappa_positive_by_seed_ADAPTIVE": kappa_adaptive,
        "divergence_positive_by_seed_REP": divergence_rep,
        "divergence_positive_by_seed_ADAPTIVE": divergence_adaptive,
        "DeltaV_structures_supported_4of5": [row for row in delta_support if row["supported_4of5"]],
        "cells_supported_4of5": supported_cells,
        "cell_support_all": cell_support,
        "total_cells": len(COSTS) * len(HORIZONS),
        "viability": "YES" if viable else "NO",
    }
    atomic_csv(output_dir / "action_values.csv", values)
    atomic_csv(output_dir / "adaptive_choices.csv", choices)
    atomic_csv(output_dir / "adaptive_surface.csv", surface)
    atomic_csv(output_dir / "seed_summary.csv", seeds)
    atomic_json(output_dir / "summary.json", summary)
    readme = f"""# B3 adaptive-development retrospective viability

Technical status: **PASS**. Viability: **{summary['viability']}**.

This analysis uses only frozen B2.4 VALIDATION scores and performs no training
or inference. TEST status is `{TEST_STATUS}`: TEST was previously opened by the
separate confirmatory program and no TEST artifact or metric is read here.

The available development actions are `0`, `STD`, `O50`, and `REP`. Selection
maximizes `DeltaV(c)`. The tie-breaking rule is literally **0 > REP > O50 >
STD**: no development is selected first on a tie, followed by REP, O50, and
STD in that order.

For each exact `domain × N × c × h` structure, the adaptive HLS/SEP divergence
region is `[0, kappa_star_adaptive)` when `rho >= 0` and
`kappa_star_adaptive > 0`; otherwise it is empty. The reported B3 viability is
retrospective and is not the frozen RQ0 confirmatory classification.
"""
    (output_dir / "README.md").write_text(readme)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    arguments = parse_args()
    print(json.dumps(run(arguments.output_dir), indent=2, sort_keys=True))
