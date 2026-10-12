from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from experiments.synthetic.campaign3_c33 import c33  # noqa: E402


def test_features_are_only_state_belief_clock_and_tau_is_scaled():
    state = ((0.2, 0.8), (0.5, 0.5), (0.8, 0.2))
    belief = (0.2, 0.3, 0.5)
    x = c33.feature_vector(state, belief, 18)
    assert len(x) == 10
    assert c33.FEATURES == ("s11", "s12", "s21", "s22", "s31", "s32", "b0", "b1", "b2", "tau")
    assert x[-1] == 0.5


def test_linear_selector_tie_and_advantage_rule_are_deterministic():
    x = np.zeros((4, len(c33.FEATURES)))
    y = np.array([-2.0, -1.0, 1.0, 2.0])
    model = c33.fit_ridge(x, y, 1.0)
    pred = c33.predict(model, x)
    assert np.isfinite(pred).all()
    assert np.array_equal(pred, c33.predict(model, x))
    assert c33.validation_regret({**model, "coef": [0.0] * 11}, x, y)[0] == 0.75


def test_fresh_sequential_design_is_development_only_and_reproducible():
    first = c33.make_tasks(replicates=1)
    second = c33.make_tasks(replicates=1)
    assert len(first) == 20 * 21
    assert [(x["history_id"], x["problem_seed"], x["noise_seed"]) for x in first] == [
        (x["history_id"], x["problem_seed"], x["noise_seed"]) for x in second
    ]
    assert all(x["history_id"].startswith("campaign3_c33_sequential_v1:") for x in first)
    heldout_teams = set(__import__("pandas").read_csv(c33.TEAM_SPLIT).query("partition == 'held-out'").team_id)
    heldout_kernels = set(__import__("pandas").read_csv(c33.KERNEL_SPLIT).query("split_role == 'heldout'").kernel_id)
    assert not heldout_teams.intersection(x["team_id"] for x in first)
    assert not heldout_kernels.intersection(x["kernel_id"] for x in first)


def test_crn_problem_and_observation_streams_are_fixed_per_history():
    task = c33.make_tasks(replicates=1)[0]
    problems_a, eps_a = c33.make_exogenous(task)
    problems_b, eps_b = c33.make_exogenous(task)
    assert problems_a == problems_b and eps_a == eps_b
    assert len(problems_a) == 12 and len(eps_a) == 36


def test_cli_safe_default_is_helpful_without_launching_full_campaign():
    # Parser-level contract is verified from source: full execution requires an explicit flag.
    source = (ROOT / "experiments/synthetic/campaign3_c33/c33.py").read_text()
    assert 'parser.add_argument("--full"' in source
    assert 'parser.add_argument("--limit-histories", type=int, default=3' in source

