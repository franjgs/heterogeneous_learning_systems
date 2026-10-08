"""Freeze the crossed C3 generator split without generating histories."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.campaign3_generator_split import SCALE_CYCLE, derive_crossed_split  # noqa: E402


PGCG = ROOT / "results" / "foundations" / "campaign3_pgcg"
OUT = ROOT / "results" / "foundations" / "campaign3_generator_split"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = PGCG / "nominal_kernels.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    split = derive_crossed_split(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    heldout = set(split.heldout_regimes)
    development = set(split.development_regimes)
    aliases = set(split.static_aliases)
    output_rows = []
    for record in rows:
        kernel_id = record["kernel_id"]
        role = "development" if kernel_id in development else "heldout" if kernel_id in heldout else "static_alias"
        output_rows.append({**record, "split_role": role, "counts_as_dynamic_regime": kernel_id not in aliases,
                            "canonical_static_representative": split.canonical_static if kernel_id in aliases | {split.canonical_static} else ""})
    split_csv = OUT / "kernel_split.csv"
    with split_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(output_rows)
    manifest = {
        "artifact_type": "pre_history_campaign3_generator_split",
        "authoritative_c3_commit": "3c282f4",
        "pgcg_kernel_table": str(source.relative_to(ROOT)),
        "pgcg_kernel_table_sha256": digest(source),
        "derivation": {
            "composition_order": "ascending lexicographic (alpha_stay,alpha_move,alpha_return)",
            "heldout_scale_cycle": list(SCALE_CYCLE),
            "kernel_ids_derived_programmatically": True,
        },
        "positive_move_compositions": [list(value) for value in split.compositions],
        "phi_dev_positive_move": list(split.development_positive_move),
        "phi_dev": list(split.development_regimes),
        "phi_heldout": list(split.heldout_regimes),
        "counts": {"positive_move_compositions": 10, "phi_dev": 21, "phi_heldout": 10},
        "static_quotient": {"canonical": split.canonical_static, "aliases_retained_in_pgcg_provenance": list(split.static_aliases),
                            "aliases_are_independent_regimes": False},
        "interpretation": {
            "phi_dev": "unseen-history generalization from fresh histories of represented kernels",
            "phi_heldout": "compositional/interpolative generalization to unseen composition-by-sigma kernels",
            "not_claimed": ["extrapolation", "wholly unseen structural region", "out-of-region generalization"],
        },
        "data_separation": {
            "pgcg_histories_eligible": False,
            "future_histories_generated": False,
            "fresh_independent_seeds_required": True,
            "split_may_change_from_outcomes": False,
        },
        "agent_or_performance_execution": False,
    }
    manifest["kernel_split_sha256"] = digest(split_csv)
    with (OUT / "pre_history_generator_split.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True); handle.write("\n")


if __name__ == "__main__":
    main()
