from hls.g3_h_organizational_value import G3HLearningProfile
from hls.g3_h_regime_map import evaluate_point
from hls.g3_h_structural_autopsy import action_diagnostics, feature_columns, local_feature_row


def test_residual_margin_is_exact_successor_reward_gap() -> None:
    evaluation = evaluate_point(
        ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8)),
        G3HLearningProfile((0.4, 0.6, 0.4)),
    )
    for row in action_diagnostics(evaluation):
        assert abs(float(row["m"]) - float(row["successor_reward_residual"])) < 1e-12


def test_probe_features_exclude_oracle_values_and_exact_redundancies() -> None:
    evaluation = evaluate_point(
        ((0.5, 0.7), (0.3, 0.2), (0.5, 0.8)),
        G3HLearningProfile((0.4, 0.6, 0.4)),
    )
    row = local_feature_row(evaluation)
    assert all("Q" not in column and not column.startswith("M_") and not column.startswith("g_") for column in feature_columns())
    assert all("Q" not in column for column in feature_columns())
    assert row["regime_oracle_label"] == evaluation.regime
