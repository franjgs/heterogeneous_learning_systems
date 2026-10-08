"""Controls for the pre-history Campaign 3 crossed generator split."""

import csv
import json
from pathlib import Path

from hls.campaign3_generator_split import derive_crossed_split


ROOT = Path(__file__).parents[1]
PGCG_TABLE = ROOT / "results" / "foundations" / "campaign3_pgcg" / "nominal_kernels.csv"
EXPECTED_HELDOUT = ("K00", "K04", "K08", "K09", "K14", "K18", "K19", "K24", "K28", "K30")
EXPECTED_DEV_POSITIVE = (
    "K01", "K02", "K03", "K05", "K06", "K07", "K10", "K11", "K13", "K15",
    "K16", "K17", "K20", "K21", "K23", "K25", "K26", "K27", "K31", "K32",
)


def load_split():
    with PGCG_TABLE.open(newline="", encoding="utf-8") as handle:
        return derive_crossed_split(list(csv.DictReader(handle)))


def test_crossed_rule_derives_exact_ids_and_counts():
    split = load_split()
    assert len(split.compositions) == 10
    assert split.heldout_positive_move == EXPECTED_HELDOUT
    assert split.development_positive_move == EXPECTED_DEV_POSITIVE
    assert len(split.development_positive_move) == 20
    assert len(split.development_regimes) == 21
    assert len(split.heldout_regimes) == 10
    assert set(split.development_regimes).isdisjoint(split.heldout_regimes)


def test_static_quotient_is_canonical_and_aliases_are_not_regimes():
    split = load_split()
    assert split.canonical_static == "K33"
    assert split.static_aliases == ("K12", "K22", "K29")
    assert "K33" in split.development_regimes
    assert not set(split.static_aliases) & (set(split.development_regimes) | set(split.heldout_regimes))


def test_every_composition_retains_two_development_scales_and_scale_coverage():
    with PGCG_TABLE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    split = load_split()
    by_id = {row["kernel_id"]: row for row in rows}
    assert {float(by_id[k]["sigma"]) for k in split.heldout_regimes} == {0.01, 0.04, 0.32}
    assert {float(by_id[k]["sigma"]) for k in split.development_positive_move} == {0.01, 0.04, 0.32}
    for composition in split.compositions:
        members = [
            kernel_id for kernel_id in split.development_positive_move
            if tuple(float(by_id[kernel_id][name]) for name in ("alpha_stay", "alpha_move", "alpha_return")) == composition
        ]
        assert len(members) == 2


def test_manifest_freezes_no_history_reuse_or_generation():
    path = ROOT / "results" / "foundations" / "campaign3_generator_split" / "pre_history_generator_split.json"
    manifest = json.loads(path.read_text())
    assert manifest["phi_dev"] == [*EXPECTED_DEV_POSITIVE, "K33"]
    assert manifest["phi_heldout"] == list(EXPECTED_HELDOUT)
    assert manifest["data_separation"]["pgcg_histories_eligible"] is False
    assert manifest["data_separation"]["future_histories_generated"] is False
    assert manifest["data_separation"]["fresh_independent_seeds_required"] is True
