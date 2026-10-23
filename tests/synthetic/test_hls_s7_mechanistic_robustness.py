from dataclasses import replace

import pytest

from experiments.run_hls_s7_mechanistic_robustness import (
    _solve_configuration,
    sensitivity_configurations,
)
from experiments.run_hls_s7_preparation_characterization import make_characterization_case


def test_sensitivity_design_is_reproducible_and_one_factor_at_a_time():
    first = sensitivity_configurations()
    second = sensitivity_configurations()
    assert first == second
    assert len(first) == 9
    center = first[0][1]
    for name, case, description in first[1:]:
        assert case.horizon == center.horizon
        assert case.initial_probabilities == center.initial_probabilities
        assert case.physical_case.organization == center.physical_case.organization
        assert case.demand_states == center.demand_states
        factor = description["changed_factor"]
        if factor == "P(y|x)":
            assert case.transition_probabilities[1] == center.transition_probabilities[1]
            assert case.physical_case.profile == center.physical_case.profile
            assert case.physical_case.efficacy == center.physical_case.efficacy
        elif factor == "P(y|y)":
            assert case.transition_probabilities[0] == center.transition_probabilities[0]
            assert case.physical_case.profile == center.physical_case.profile
            assert case.physical_case.efficacy == center.physical_case.efficacy
        elif factor == "MIS-v2 eta(B,y)":
            assert case.transition_probabilities == center.transition_probabilities
            assert case.physical_case.efficacy == center.physical_case.efficacy
            assert case.physical_case.profile.eta[1][1] != center.physical_case.profile.eta[1][1]
        else:
            assert factor == "transfer efficacy A→B/y"
            assert case.transition_probabilities == center.transition_probabilities
            assert case.physical_case.profile == center.physical_case.profile
            assert case.physical_case.efficacy.values[0][1][1] != center.physical_case.efficacy.values[0][1][1]


def test_four_policy_decomposition_and_functional_metrics_are_coherent():
    case = replace(make_characterization_case("opportunity"), horizon=2)
    row = _solve_configuration("test", case, {})
    values = row["exact_values"]
    d = row["decomposition"]
    ja, jb = values["J_A_bellman_no_transfer"], values["J_B_bellman_transfer_optional"]
    jma, jmb = values["J_MA_reactive_no_transfer"], values["J_MB_reactive_transfer_optional"]
    assert d["planning_without_transfer_JA_minus_JMA"] == pytest.approx(ja - jma)
    assert d["planning_with_transfer_JB_minus_JMB"] == pytest.approx(jb - jmb)
    assert d["transfer_with_planning_JB_minus_JA"] == pytest.approx(jb - ja)
    assert d["transfer_without_planning_JMB_minus_JMA"] == pytest.approx(jmb - jma)
    assert d["interaction_I"] == pytest.approx((jb - ja) - (jmb - jma))
    assert d["interaction_I"] == pytest.approx(d["interaction_identity_check"])

    metrics = row["expected_functional_and_resource_metrics"]
    for policy, policy_metrics in metrics.items():
        assert policy_metrics["expected_cumulative_CES"] == pytest.approx(values[policy])
        assert policy_metrics["expected_services_completed"] + policy_metrics[
            "expected_functional_failures"] == pytest.approx(case.horizon)
        assert policy_metrics["expected_total_resource_consumption"] == pytest.approx(
            policy_metrics["expected_productive_effort"]
            + policy_metrics["expected_teaching_resource_consumption"]
        )
    for policy in ("J_A_bellman_no_transfer", "J_MA_reactive_no_transfer"):
        assert metrics[policy]["expected_teaching_actions"] == 0.0
        assert metrics[policy]["expected_teaching_resource_consumption"] == 0.0


def test_center_records_ex_ante_fixed_demand_branches_and_actions():
    case = make_characterization_case("opportunity")
    row = _solve_configuration("center", case, {})
    branches = row["mechanistic_demand_branches"]
    bellman_transfer = branches["J_B_bellman_transfer_optional"]["x_y_y_y"]
    reactive_transfer = branches["J_MB_reactive_transfer_optional"]["x_y_y_y"]
    assert bellman_transfer["demand_path"] == ["task-x", "task-y", "task-y", "task-y"]
    assert bellman_transfer["path_probability"] == pytest.approx(
        case.initial_probabilities[0]
        * case.transition_probabilities[0][1]
        * case.transition_probabilities[1][1] ** 2
    )
    initial_bellman_action = bellman_transfer["periods"][0]["action"]
    initial_reactive_action = reactive_transfer["periods"][0]["action"]
    assert initial_bellman_action["teaching"] is not None
    assert initial_reactive_action["teaching"] is None
    assert initial_bellman_action["production"] != initial_reactive_action["production"]
    assert bellman_transfer["periods"][0]["immediate_CES"] < reactive_transfer[
        "periods"
    ][0]["immediate_CES"]
    for policy in ("J_A_bellman_no_transfer", "J_MA_reactive_no_transfer"):
        for period in branches[policy]["x_y_y_y"]["periods"]:
            assert period["action"]["teaching"] is None

