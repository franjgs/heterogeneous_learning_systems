from dataclasses import replace

import pytest

from experiments.run_hls_s7_anticipatory_selection_audit import run
from experiments.run_hls_s7_preparation_characterization import make_characterization_case
from hls.synthetic.hls_s7_uncertain_demand import (
    solve_current_demand_myopic,
)


def test_current_demand_myopic_is_reactive_and_deterministic():
    base = make_characterization_case("opportunity")
    current_y = replace(base, initial_probabilities=(0.0, 1.0))
    alternative_future = replace(
        current_y,
        transition_probabilities=((1.0, 0.0), (1.0, 0.0)),
    )
    first = solve_current_demand_myopic(current_y, transfer_available=False)
    second = solve_current_demand_myopic(current_y, transfer_available=False)
    changed_future = solve_current_demand_myopic(alternative_future,
                                                  transfer_available=False)
    initial = (0, base.physical_case.organization.competence_initial, 1)
    assert first.actions_by_state[initial] == second.actions_by_state[initial]
    assert first.actions_by_state[initial] == changed_future.actions_by_state[initial]
    assert first.value == pytest.approx(second.value)


def test_anticipatory_audit_values_q_learning_and_performance_identity():
    result = run()
    assert result["validation"]["historical_A_MA_BMA_reproduced"]
    assert result["validation"]["branch_probabilities_sum_to_one"]
    assert result["validation"]["occupancy_sums_to_one_each_period"]
    assert result["validation"]["bellman_unpruned_value_matches_historical"]
    assert result["validation"]["performance_difference_identity_holds"]
    assert result["validation"]["PEF_provenance_and_units_present"]
    values = {key: row["ces_cumulative"]["value"]
              for key, row in result["policies"].items()}
    assert values == pytest.approx({
        "A": 3.1628653621,
        "MA": 3.0346209871,
        "BMA": 3.0444737839,
        "CDM": 3.1628653621,
    })
    assert result["design"]["positive_probability_reachable_branches"] == 8
    assert result["design"]["full_path_combinations"] == 16
    assert result["pairwise_CES_differences"] == pytest.approx({
        "A_minus_BMA": 0.1183915782,
        "A_minus_CDM": 0.0,
        "BMA_minus_CDM": -0.1183915782,
    })
    for identity in result["bellman_performance_difference_identity"].values():
        assert identity["J_Bellman_minus_policy"] == pytest.approx(
            identity["occupancy_weighted_advantage_sum"], abs=1e-10)
    first_divergence = result["first_divergences_on_shared_trajectories"]["A_vs_BMA"][0]
    assert (first_divergence["period"], first_divergence["demand"]) == (1, "task-y")
    assert first_divergence["first_divergence_probability_mass"] == pytest.approx(0.9)
    assert first_divergence["learning"]["A_Bellman"]["net_delta_total"] == pytest.approx(0.065)
    assert first_divergence["learning"]["BMA_BEST_MYOPIC"]["net_delta_total"] == pytest.approx(0.08892)
    assert first_divergence["Q_B"]["Q_difference_left_minus_right"] == pytest.approx(0.085086302)


def test_common_reachable_state_table_has_per_policy_occupancies_and_cdm_metrics():
    result = run()
    state = next(row for row in result["state_occupancy_and_decisions"]
                 if row["period"] == 1 and row["demand_state"] == "task-y")
    assert state["reachable_under_policies"] == ["A", "MA", "BMA", "CDM"]
    assert state["occupancy_probability_by_policy"]["A"] == pytest.approx(0.9)
    delta = state["policies"]["A"]["delta_competence_matrix"]
    assert delta[0] == pytest.approx([0.0, 0.015])
    assert delta[1] == pytest.approx([0.0, 0.05])
    assert result["policies"]["CDM"]["functional_success_rate"]["value"] == pytest.approx(0.75025)
