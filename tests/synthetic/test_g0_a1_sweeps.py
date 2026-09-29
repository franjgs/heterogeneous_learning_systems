import pytest

from hls import a1b, a1c
from hls.a1a import Learner, solve_hls, solve_strong_sep
from hls.synthetic.adapters.a1 import (
    analytical_regime,
    build_a1_environment,
    evaluate_a1_exact,
    observed_regime,
)


def _development_labels(actions):
    labels = []
    for action in actions:
        if action.is_null:
            labels.append("null")
        else:
            labels.append(f"develop_{action.recipient}_task_{action.competence}")
    return "|".join(sorted(labels))


def _action_labels(actions):
    return "|".join(sorted(str(action) for action in actions))


def _assert_common(old_row, world) -> None:
    new = evaluate_a1_exact(build_a1_environment(world))
    assert new.no_opportunity_value == pytest.approx(old_row["N"], abs=1e-12)
    assert new.opportunity_value == pytest.approx(old_row["D"], abs=1e-12)
    assert new.opportunity_value - new.no_opportunity_value == pytest.approx(old_row["D_minus_N"], abs=1e-12)
    assert new.hls.value == pytest.approx(old_row["J_HLS"], abs=1e-12)
    assert new.strong_sep.value_min == pytest.approx(old_row["J_SEP_min"], abs=1e-12)
    assert new.strong_sep.value_max == pytest.approx(old_row["J_SEP_max"], abs=1e-12)
    assert new.delta_j_cons == pytest.approx(old_row["Delta_J_cons"], abs=1e-12)
    assert new.sep_omega.value == pytest.approx(old_row["J_SEP_Omega"], abs=1e-12)
    assert _action_labels(new.hls.optimal_actions) == old_row["HLS_optimal_actions"]
    assert _action_labels(new.strong_sep.immediate_optimal_actions) == old_row["SEP_immediate_optimal_actions"]
    assert _development_labels(new.optimal_development_actions) == old_row["optimal_development_actions"]
    assert observed_regime(new.delta_j_cons) == old_row["observed_regime"]
    assert abs(new.hls.value - new.sep_omega.value) <= 1e-12


def test_g0_matches_all_1020_a1b_configurations() -> None:
    configurations = a1b.all_configurations()
    assert len(configurations) == 1020
    for configuration in configurations:
        world = a1b._world_for(configuration)
        old_row = a1b.evaluate_configuration(configuration)
        _assert_common(old_row, world)
        new = evaluate_a1_exact(build_a1_environment(world))
        h = next(iter(new.strong_sep.immediate_optimal_actions))
        s = next(action for action in new.operational_rewards if action != h)
        delta_r = new.operational_rewards[h] - new.operational_rewards[s]
        delta_g = new.continuation_values[s] - new.continuation_values[h]
        assert analytical_regime(delta_g - delta_r) == old_row["predicted_regime"]
        assert new.opportunity_probabilities[h] == pytest.approx(old_row["g_h"], abs=1e-12)
        assert new.opportunity_probabilities[s] == pytest.approx(old_row["g_s"], abs=1e-12)


def test_g0_matches_all_458_a1c_configurations_and_relabelings() -> None:
    configurations = a1c.all_configurations()
    assert len(configurations) == 458
    for configuration in configurations:
        world = a1c.world_for(configuration)
        old_row = a1c.evaluate_configuration(configuration)
        _assert_common(old_row, world)
        new = evaluate_a1_exact(build_a1_environment(world))
        if old_row["immediate_tie"]:
            assert len(new.strong_sep.immediate_optimal_actions) > 1
            assert old_row["predicted_regime"] == a1c.IMMEDIATE_TIE
        else:
            h = next(iter(new.strong_sep.immediate_optimal_actions))
            s = next(action for action in new.operational_rewards if action != h)
            delta_r = new.operational_rewards[h] - new.operational_rewards[s]
            delta_g = new.continuation_values[s] - new.continuation_values[h]
            assert analytical_regime(delta_g - delta_r) == old_row["predicted_regime"]

        relabeled = evaluate_a1_exact(build_a1_environment(a1c.relabel_world(world)))
        assert relabeled.hls.value == pytest.approx(new.hls.value, abs=1e-12)
        assert relabeled.strong_sep.value_min == pytest.approx(new.strong_sep.value_min, abs=1e-12)
        assert relabeled.strong_sep.value_max == pytest.approx(new.strong_sep.value_max, abs=1e-12)
        assert relabeled.delta_j_cons == pytest.approx(new.delta_j_cons, abs=1e-12)
        assert relabeled.sep_omega.value == pytest.approx(new.sep_omega.value, abs=1e-12)


def test_gate_covers_exactly_1478_preregistered_worlds() -> None:
    assert len(a1b.all_configurations()) + len(a1c.all_configurations()) == 1478
