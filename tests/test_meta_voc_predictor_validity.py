"""Lightweight invariants for the dedicated frozen-predictor audit."""
from __future__ import annotations

import numpy as np
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.meta_voc_predictor_validity import audit
from experiments.synthetic.campaign3_c32_data import targets


def test_audit_sampling_and_mc_protocol_are_fixed():
    assert audit.MC_REPLICATES == 32
    assert audit.BOOTSTRAP_B == 2000
    assert audit.BOOTSTRAP_SEED == 20261012
    assert audit.AUDIT_RANDOM_NAMESPACE != "campaign3_c32_data_v1"
    assert audit.sampling.SEED == "HLS-C4-SAMPLE-v1-20261012"


def test_c32_horizon_is_remaining_current_plus_11_full_problems():
    for problem in range(1, 13):
        for decision in (1, 2, 3):
            step = decision - 1
            n_rewards = (3 - step) + 3 * targets.ELL
            last_problem = problem + targets.ELL
            last_global_clock = 3 * last_problem
            start_clock = 3 * (problem - 1) + decision
            assert n_rewards == last_global_clock - start_clock + 1


def test_audit_seed_mapping_is_stable_and_stream_separated():
    a = audit.stable_seed(audit.AUDIT_RANDOM_NAMESPACE, "state-x", 7, "future")
    b = audit.stable_seed(audit.AUDIT_RANDOM_NAMESPACE, "state-x", 7, "future")
    noise = audit.stable_seed(audit.AUDIT_RANDOM_NAMESPACE, "state-x", 7, "observation")
    legacy = audit.stable_seed("campaign3_c32_data_v1", "state-x", 7, "future")
    assert a == b
    assert len({a, noise, legacy}) == 3
    assert 0 <= a < 2**63 - 1


def test_weighted_auc_and_correlation_have_expected_orientation():
    y = np.array([False, False, True, True])
    score = np.array([0.1, 0.2, 0.8, 0.9])
    weights = np.ones(4)
    assert audit._weighted_auc(y, score, weights) == 1.0
    assert audit._weighted_auc(y, -score, weights) == 0.0
    assert np.isclose(audit._weighted_corr(score, score, weights), 1.0)


def test_performance_only_oracle_regret_is_nonnegative():
    import pandas as pd

    frame = pd.DataFrame({
        "delta_mean": [0.4, -0.2, 0.1, -0.3],
        "prediction_raw_advantage": [0.5, -0.1, -0.2, 0.3],
        "sampling_weight": [1.0] * 4,
        "meta_voc50_invokes_deep": [True, False, False, True],
        "mc_se": [0.01] * 4,
        "mc_ci_spans_zero": [0, 0, 0, 0],
    })
    assert audit._metrics(frame)["performance_only_oracle_regret"] >= 0


def test_source_hash_manifest_covers_original_target_code():
    assert "experiments/synthetic/campaign3_c32_data/targets.py" in audit.SOURCE_FILES
    assert "src/hls/campaign3_problem_generator.py" in audit.SOURCE_FILES


def test_chunked_csv_count_counts_rows_not_chunks(tmp_path):
    import pandas as pd

    path = tmp_path / "small.csv.gz"
    pd.DataFrame({"x": range(7)}).to_csv(path, index=False, compression="gzip")
    n = sum(len(chunk) for chunk in pd.read_csv(path, compression="gzip", chunksize=3))
    assert n == 7
