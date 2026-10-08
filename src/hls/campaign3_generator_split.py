"""Pure derivation of the frozen Campaign 3 crossed generator split."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


SCALE_CYCLE = (0.01, 0.04, 0.32, 0.01, 0.04, 0.32, 0.01, 0.04, 0.32, 0.01)
CANONICAL_STATIC_ID = "K33"
STATIC_ALIAS_IDS = ("K12", "K22", "K29")


@dataclass(frozen=True)
class GeneratorSplit:
    compositions: tuple[tuple[float, float, float], ...]
    heldout_positive_move: tuple[str, ...]
    development_positive_move: tuple[str, ...]
    development_regimes: tuple[str, ...]
    heldout_regimes: tuple[str, ...]
    canonical_static: str
    static_aliases: tuple[str, ...]


def derive_crossed_split(rows: Iterable[Mapping[str, object]]) -> GeneratorSplit:
    """Derive IDs from the PGCG table; the cyclic rule is authoritative."""
    records = tuple(rows)
    positive = tuple(record for record in records if float(record["alpha_move"]) > 0.0)
    compositions = tuple(
        sorted(
            {
                (float(record["alpha_stay"]), float(record["alpha_move"]), float(record["alpha_return"]))
                for record in positive
            }
        )
    )
    if len(compositions) != 10:
        raise ValueError(f"expected 10 positive-MOVE compositions, found {len(compositions)}")
    heldout = []
    for composition, sigma in zip(compositions, SCALE_CYCLE, strict=True):
        matches = [
            str(record["kernel_id"])
            for record in positive
            if (float(record["alpha_stay"]), float(record["alpha_move"]), float(record["alpha_return"]))
            == composition
            and float(record["sigma"]) == sigma
        ]
        if len(matches) != 1:
            raise ValueError(f"composition {composition}, sigma {sigma} has matches {matches}")
        heldout.append(matches[0])
    positive_ids = tuple(str(record["kernel_id"]) for record in positive)
    development = tuple(kernel_id for kernel_id in positive_ids if kernel_id not in heldout)
    static = {str(record["kernel_id"]): record for record in records if float(record["alpha_move"]) == 0.0}
    if set(static) != {CANONICAL_STATIC_ID, *STATIC_ALIAS_IDS}:
        raise ValueError(f"unexpected MOVE-free kernel set: {sorted(static)}")
    canonical = static[CANONICAL_STATIC_ID]
    if (float(canonical["alpha_stay"]), float(canonical["alpha_return"])) != (1.0, 0.0):
        raise ValueError("K33 is not the pure-STAY canonical static kernel")
    return GeneratorSplit(
        compositions=compositions,
        heldout_positive_move=tuple(heldout),
        development_positive_move=development,
        development_regimes=development + (CANONICAL_STATIC_ID,),
        heldout_regimes=tuple(heldout),
        canonical_static=CANONICAL_STATIC_ID,
        static_aliases=STATIC_ALIAS_IDS,
    )
