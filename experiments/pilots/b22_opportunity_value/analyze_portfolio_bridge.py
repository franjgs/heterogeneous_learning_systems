"""Retrospective B2.1/B2.2 portfolio-bridge audit; never trains models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_B21 = ROOT / "results/pilots/b21_pacs_factorial"
DEFAULT_B22 = ROOT / "results/pilots/b22_opportunity_value"
DOMAINS = ("photo", "art_painting", "cartoon", "sketch")
N_VALUES = (25, 50, 100)
COSTS = (0.0, 0.02, 0.05, 0.10, 0.15)
FUTURE_WEIGHTS = (1, 2, 5, 10)
TOLERANCE = 1e-12


def operational_value(scores: dict[str, float], deep: dict[str, float], cost: float) -> float:
    return float(np.mean([max(scores[domain], deep[domain] - cost) for domain in DOMAINS]))


def bridge_quantities(
    f0: dict[str, float], fi: dict[str, float], fj: dict[str, float], fij: dict[str, float],
    deep: dict[str, float], domain_i: str, domain_j: str, cost: float, future_weight: int,
) -> dict[str, float | bool]:
    """Calculate the frozen bridge formulas for one already-learned factorial state."""
    rho_i = f0[domain_i] - (deep[domain_i] - cost)
    rho_j = f0[domain_j] - (deep[domain_j] - cost)
    v0 = operational_value(f0, deep, cost)
    vi = operational_value(fi, deep, cost)
    vj = operational_value(fj, deep, cost)
    vij = operational_value(fij, deep, cost)
    delta_i, delta_j, delta_ij = vi - v0, vj - v0, vij - v0
    gamma = delta_ij - delta_i - delta_j
    h_i = -rho_i + future_weight * delta_i
    h_j = -rho_j + future_weight * delta_j
    h_ij = -(rho_i + rho_j) + future_weight * delta_ij
    identity_rhs = h_i + h_j + future_weight * gamma
    if not np.isclose(h_ij, identity_rhs, atol=TOLERANCE, rtol=0):
        raise RuntimeError("H_ij identity failed")
    rescue = bool(rho_i > 0 and rho_j > 0 and h_i < 0 and h_j < 0 and h_ij > 0)
    interaction_needed = bool(rescue and h_i + h_j < 0 and future_weight * gamma > -(h_i + h_j))
    if rescue != interaction_needed:
        raise RuntimeError("portfolio_rescue and interaction_needed differ")
    return {
        "rho_i": rho_i, "rho_j": rho_j, "V_F0": v0, "V_Fi": vi, "V_Fj": vj, "V_Fij": vij,
        "DeltaV_i": delta_i, "DeltaV_j": delta_j, "DeltaV_ij": delta_ij, "Gamma_oper": gamma,
        "H_i": h_i, "H_j": h_j, "H_ij": h_ij, "B_Gamma": future_weight * gamma,
        "H_j_given_i": h_ij - h_i, "H_i_given_j": h_ij - h_j,
        "portfolio_rescue": rescue, "interaction_needed": interaction_needed,
        "B_star": (rho_i + rho_j) / delta_ij if delta_ij > 0 else np.nan,
        "B_star_i": rho_i / delta_i if delta_i > 0 else np.nan,
        "B_star_j": rho_j / delta_j if delta_j > 0 else np.nan,
    }


def _vector(row: pd.Series, prefix: str) -> dict[str, float]:
    return {domain: float(row[f"{prefix}_ba_{domain}"]) for domain in DOMAINS}


def _b21_singletons(factorial: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for seed in sorted(factorial.seed.unique()):
        for n in N_VALUES:
            subset = factorial[(factorial.seed == seed) & (factorial.N == n)]
            for domain in DOMAINS:
                columns = [f"F_{domain}_ba_{affected}" for affected in DOMAINS]
                found = subset.dropna(subset=columns)
                if len(found) != 3:
                    raise RuntimeError(f"B2.1 singleton {seed}/{n}/{domain} must occur in three pairs")
                values = found[columns].to_numpy(float)
                if np.max(np.ptp(values, axis=0)) > TOLERANCE:
                    raise RuntimeError(f"B2.1 singleton {seed}/{n}/{domain} is internally inconsistent")
                records.append({"seed": seed, "N": n, "domain": domain, **{f"ba_{affected}": values[0, index] for index, affected in enumerate(DOMAINS)}})
    return pd.DataFrame(records)


def audit_compatibility(b21_dir: Path, b22_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    factorial = pd.read_csv(b21_dir / "factorial_results.csv")
    states = pd.read_csv(b21_dir / "state_scores.csv")
    protocol = json.loads((b21_dir / "protocol.json").read_text())
    raw22 = pd.read_csv(b22_dir / "raw_results.csv")
    metadata22 = json.loads((b22_dir / "run_metadata.json").read_text())
    if protocol.get("test_used") is not False or metadata22.get("test_used") is not False:
        raise RuntimeError("TEST closure failed")
    if set(factorial.seed) != set(range(5)) or set(factorial.N) != set(N_VALUES):
        raise RuntimeError("B2.1 grid differs")
    if set(raw22.seed) != set(range(5)) or set(raw22.N) != set(N_VALUES):
        raise RuntimeError("B2.2 grid differs")
    unique22 = raw22.sort_values(["c", "B"]).drop_duplicates(["seed", "domain", "N"])
    singleton21 = _b21_singletons(factorial)

    base_records: list[dict[str, object]] = []
    base_equal: dict[tuple[int, str], bool] = {}
    for seed in range(5):
        row21 = factorial[factorial.seed == seed].iloc[0]
        row22 = unique22[unique22.seed == seed].iloc[0]
        for state in ("F0", "D"):
            if state == "F0":
                left = np.array([row21[f"F0_ba_{domain}"] for domain in DOMAINS], float)
            else:
                stored = states[(states.seed == seed) & (states.state == "D")].iloc[0]
                left = np.array([stored[f"ba_{domain}"] for domain in DOMAINS], float)
            right = np.array([row22[f"{state}_ba_{domain}"] for domain in DOMAINS], float)
            differences = np.abs(left - right)
            equal = bool(np.allclose(left, right, atol=TOLERANCE, rtol=0))
            base_equal[(seed, state)] = equal
            base_records.append({"kind": "base", "seed": seed, "N": "", "domain": state, "equal": equal, "max_abs_difference": differences.max(), **{f"abs_difference_{domain}": differences[index] for index, domain in enumerate(DOMAINS)}})

    singleton_records: list[dict[str, object]] = []
    singleton_equal: dict[tuple[int, int, str], bool] = {}
    for row21 in singleton21.itertuples(index=False):
        row22 = unique22[(unique22.seed == row21.seed) & (unique22.N == row21.N) & (unique22.domain == row21.domain)].iloc[0]
        left = np.array([getattr(row21, f"ba_{domain}") for domain in DOMAINS], float)
        right = np.array([row22[f"Fk_ba_{domain}"] for domain in DOMAINS], float)
        differences = np.abs(left - right)
        equal = bool(np.allclose(left, right, atol=TOLERANCE, rtol=0))
        singleton_equal[(int(row21.seed), int(row21.N), str(row21.domain))] = equal
        singleton_records.append({"kind": "singleton", "seed": row21.seed, "N": row21.N, "domain": row21.domain, "equal": equal, "max_abs_difference": differences.max(), **{f"abs_difference_{domain}": differences[index] for index, domain in enumerate(DOMAINS)}})

    compatibility = pd.DataFrame(base_records + singleton_records)
    cell_records = []
    for row in factorial.itertuples(index=False):
        compatible = (
            base_equal[(int(row.seed), "F0")] and base_equal[(int(row.seed), "D")]
            and singleton_equal[(int(row.seed), int(row.N), str(row.domain_i))]
            and singleton_equal[(int(row.seed), int(row.N), str(row.domain_j))]
        )
        cell_records.append({"seed": row.seed, "N": row.N, "domain_i": row.domain_i, "domain_j": row.domain_j, "compatible": compatible})
    cells = pd.DataFrame(cell_records)
    audit = {
        "candidate_states": len(cells), "candidate_analytical_rows": len(cells) * len(COSTS) * len(FUTURE_WEIGHTS),
        "equal_F0_seeds": sum(base_equal[(seed, "F0")] for seed in range(5)),
        "equal_D_seeds": sum(base_equal[(seed, "D")] for seed in range(5)),
        "equal_singletons": int(sum(singleton_equal.values())), "compatible_states": int(cells.compatible.sum()),
        "compatible_analytical_rows": int(cells.compatible.sum()) * len(COSTS) * len(FUTURE_WEIGHTS),
        "selection_rule_nominally_shared": True, "b21_selected_ids_recorded": False,
        "b21_pseudo_labels_recorded": False, "validation_only": True, "test_closed": True,
    }
    return compatibility, cells, audit


RAW_COLUMNS = [
    "seed", "N", "domain_i", "domain_j", "pair", "c", "B", "rho_i", "rho_j",
    "V_F0", "V_Fi", "V_Fj", "V_Fij", "DeltaV_i", "DeltaV_j", "DeltaV_ij",
    "Gamma_learn", "Gamma_oper", "H_i", "H_j", "H_ij", "B_Gamma", "H_j_given_i",
    "H_i_given_j", "portfolio_rescue", "interaction_needed", "B_star", "B_star_i", "B_star_j",
]


def analyze_compatible(factorial: pd.DataFrame, states: pd.DataFrame, compatible_cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for cell in compatible_cells[compatible_cells.compatible].itertuples(index=False):
        source = factorial[(factorial.seed == cell.seed) & (factorial.N == cell.N) & (factorial.domain_i == cell.domain_i) & (factorial.domain_j == cell.domain_j)].iloc[0]
        deep_row = states[(states.seed == cell.seed) & (states.state == "D")].iloc[0]
        f0 = _vector(source, "F0")
        fi = _vector(source, f"F_{cell.domain_i}")
        fj = _vector(source, f"F_{cell.domain_j}")
        fij = _vector(source, f"F_{cell.domain_i}_{cell.domain_j}")
        deep = {domain: float(deep_row[f"ba_{domain}"]) for domain in DOMAINS}
        for cost in COSTS:
            for weight in FUTURE_WEIGHTS:
                values = bridge_quantities(f0, fi, fj, fij, deep, cell.domain_i, cell.domain_j, cost, weight)
                rows.append({"seed": cell.seed, "N": cell.N, "domain_i": cell.domain_i, "domain_j": cell.domain_j, "pair": f"{cell.domain_i}-{cell.domain_j}", "c": cost, "B": weight, "Gamma_learn": float(source.gamma_learn), **values})
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


def summarize(raw: pd.DataFrame, audit: dict[str, object]) -> pd.DataFrame:
    rows = [
        ("candidate_analytical_observations", audit["candidate_analytical_rows"]),
        ("candidate_learned_states", audit["candidate_states"]),
        ("compatible_analytical_observations", audit["compatible_analytical_rows"]),
        ("compatible_learned_states", audit["compatible_states"]),
        ("portfolio_rescues", int(raw.portfolio_rescue.sum()) if len(raw) else np.nan),
        ("unique_states_with_rescue", raw.loc[raw.portfolio_rescue, ["seed", "N", "pair"]].drop_duplicates().shape[0] if len(raw) else np.nan),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def reproducibility(raw: pd.DataFrame) -> pd.DataFrame:
    columns = ["N", "pair", "c", "B", "n_seeds", "n_rescue", "rescue_ge_2", "rescue_ge_3", "rescue_5_of_5"]
    if raw.empty:
        return pd.DataFrame(columns=columns)
    result = raw.groupby(["N", "pair", "c", "B"], as_index=False).agg(n_seeds=("seed", "nunique"), n_rescue=("portfolio_rescue", "sum"))
    result["rescue_ge_2"] = result.n_rescue >= 2
    result["rescue_ge_3"] = result.n_rescue >= 3
    result["rescue_5_of_5"] = result.n_rescue == 5
    return result[columns]


def representative_cases(raw: pd.DataFrame, reproduction: pd.DataFrame) -> pd.DataFrame:
    if raw.empty or not raw.portfolio_rescue.any():
        return pd.DataFrame(columns=["case", *RAW_COLUMNS])
    rescue = raw[raw.portfolio_rescue].copy()
    choices: list[tuple[str, pd.Series]] = [
        ("largest_H_ij", rescue.sort_values("H_ij", ascending=False).iloc[0]),
        ("nearest_H_ij_zero", rescue.assign(distance=rescue.H_ij.abs()).sort_values("distance").iloc[0]),
        ("largest_B_Gamma", rescue.sort_values("B_Gamma", ascending=False).iloc[0]),
    ]
    best = reproduction.sort_values(["n_rescue", "N", "pair", "c", "B"], ascending=[False, True, True, True, True]).iloc[0]
    group = rescue[(rescue.N == best.N) & (rescue.pair == best.pair) & np.isclose(rescue.c, best.c) & (rescue.B == best.B)]
    if len(group):
        choices.append(("most_seed_reproducible_cell", group.sort_values("H_ij", ascending=False).iloc[0]))
    both_negative = rescue[(rescue.DeltaV_i < 0) & (rescue.DeltaV_j < 0) & (rescue.DeltaV_ij > 0)]
    if len(both_negative):
        choices.append(("negative_singletons_positive_joint", both_negative.sort_values("H_ij", ascending=False).iloc[0]))
    sign_change = rescue[np.sign(rescue.Gamma_oper) != np.sign(rescue.Gamma_learn)]
    if len(sign_change):
        choices.append(("Gamma_oper_sign_differs_from_Gamma_learn", sign_change.sort_values("H_ij", ascending=False).iloc[0]))
    return pd.DataFrame([{"case": label, **row.to_dict()} for label, row in choices])


def report_text(compatibility: pd.DataFrame, audit: dict[str, object]) -> str:
    base = compatibility[compatibility.kind == "base"]
    single = compatibility[compatibility.kind == "singleton"]
    return f"""# Retrospective B2.1–B2.2 portfolio bridge

Status: **HALTED — COUNTERFACTUAL INCOMPATIBILITY**.

This is a retrospective bridge audit, not part of the preregistered B2.2 protocol. It used only stored VALIDATION results and did not train models or access TEST.

## Compatibility gate

The candidate universe contains {audit['candidate_states']} learned `seed × N × pair` states and {audit['candidate_analytical_rows']} possible `seed × N × pair × c × B` valuations. None is admissible for the requested bridge:

- B2.1 and B2.2 `S(F0)` agree in {audit['equal_F0_seeds']}/5 seeds; maximum component differences range from {base[base.domain == 'F0'].max_abs_difference.min():.6f} to {base[base.domain == 'F0'].max_abs_difference.max():.6f}.
- B2.1 and B2.2 `S(D)` agree in {audit['equal_D_seeds']}/5 seeds; maximum component differences range from {base[base.domain == 'D'].max_abs_difference.min():.6f} to {base[base.domain == 'D'].max_abs_difference.max():.6f}.
- Singleton vectors agree in {audit['equal_singletons']}/60 interventions at tolerance `{TOLERANCE:g}`; their maximum component differences range from {single.max_abs_difference.min():.6f} to {single.max_abs_difference.max():.6f}.
- Therefore compatible factorial states: {audit['compatible_states']}/{audit['candidate_states']}; compatible analytical observations: {audit['compatible_analytical_rows']}/{audit['candidate_analytical_rows']}.

Both runners nominally use the same manifest, split routine, selection seed formula, architectures, optimizer parameters, three epochs, and VALIDATION evaluation. B2.2 stores its selected IDs; B2.1 did not store selected IDs, pseudo-labels, model fingerprints, checkpoints, manifest hash, or implementation hash, so equality of its realized inputs cannot be demonstrated from the artifacts.

The concrete training-path difference is that B2.2 calls `seed_everything(training_seed)` before every singleton update, while B2.1 only seeds the DataLoader shuffle generator. Random crop/flip state in B2.1 therefore depends on the preceding execution order. The independently retrained B2.1 and B2.2 base states also differ, and B2.1 lacks the provenance needed to attribute that base divergence further. Because D differs, equality of realized pseudo-labels is not established.

## Scientific stop

Per the declared compatibility rule, `rho_i`, `rho_j`, `DeltaV_i`, `DeltaV_j`, `DeltaV_ij`, `Gamma_oper`, `H_i`, `H_j`, and `H_ij` were not combined across B2.1 and B2.2. `portfolio_bridge_raw.csv`, reproducibility, and representative cases therefore contain zero eligible rows.

This does **not** mean that zero portfolio rescues exist. It means the existing runs cannot identify whether `H_i<0`, `H_j<0`, and `H_ij>0` hold for matched counterfactual states. No claim about accumulated-opportunity portfolio value or RQ0 follows from this retrospective bridge.

## What is observed

- The stored result vectors are numerically incompatible at the base and singleton levels.
- Nominal grids, domain definitions, selection rule, CPU device, VALIDATION evaluation, and TEST closure agree.
- No eligible state remains after the counterfactual compatibility gate.

## Supported interpretation

The B2.1 factorial interaction and B2.2 absolute opportunity values belong to separately trained realizations. Combining their states as though they shared F0, D, pseudo-labels, and singleton updates would create an invalid counterfactual.

## Not demonstrated

- existence or absence of portfolio rescue;
- reproducibility of rescue across seeds;
- sequential accumulation value;
- an ex-ante opportunity-accumulation policy;
- a stronger RQ0 mechanism, TEST generalization, HLS superiority, or novelty.
"""


def run(b21_dir: Path, b22_dir: Path, output_dir: Path) -> dict[str, object]:
    compatibility, cells, audit = audit_compatibility(b21_dir, b22_dir)
    factorial = pd.read_csv(b21_dir / "factorial_results.csv")
    states = pd.read_csv(b21_dir / "state_scores.csv")
    raw = analyze_compatible(factorial, states, cells)
    summary = summarize(raw, audit)
    reproduction = reproducibility(raw)
    cases = representative_cases(raw, reproduction)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw.to_csv(output_dir / "portfolio_bridge_raw.csv", index=False)
    summary.to_csv(output_dir / "portfolio_bridge_summary.csv", index=False)
    reproduction.to_csv(output_dir / "portfolio_bridge_reproducibility.csv", index=False)
    cases.to_csv(output_dir / "portfolio_bridge_cases.csv", index=False)
    (output_dir / "portfolio_bridge.md").write_text(report_text(compatibility, audit))
    compatibility.to_csv(output_dir / "compatibility_audit.csv", index=False)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--b21-dir", type=Path, default=DEFAULT_B21)
    parser.add_argument("--b22-dir", type=Path, default=DEFAULT_B22)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_B22 / "portfolio_bridge")
    args = parser.parse_args()
    audit = run(args.b21_dir, args.b22_dir, args.output_dir)
    print("Retrospective bridge compatibility audit complete.", flush=True)
    print(f"Compatible learned states: {audit['compatible_states']} / {audit['candidate_states']}", flush=True)
    print(f"Eligible analytical observations: {audit['compatible_analytical_rows']} / {audit['candidate_analytical_rows']}", flush=True)
    print("Scientific bridge analysis halted before H_ij; no training and no TEST access.", flush=True)


if __name__ == "__main__":
    main()
