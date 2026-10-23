import pytest

from experiments.run_hls_s7_myopic_tiebreak_audit import run
from experiments.run_hls_s7_preparation_characterization import make_characterization_case
from hls.synthetic.hls_s4_transfer_exact import _step, action_catalogs
from hls.synthetic.hls_s7_uncertain_demand import (
    TOL,
    _state_cases,
    audit_myopic_tiebreaks,
    select_best_myopic_action,
    solve_best_myopic,
    solve_reactive_greedy,
)


def test_best_myopic_is_immediately_optimal_and_catalog_order_independent():
    case = make_characterization_case("opportunity")
    best = solve_best_myopic(case, transfer_available=False)
    state_cases = _state_cases(case, transfer_available=False, efficacy=None)
    saw_different_secondary_gains = False
    for state, selected in best.actions_by_state.items():
        time, competence, demand_index = state
        if time >= case.horizon:
            continue
        physical, actions = state_cases[demand_index]
        demand = case.demand_states[demand_index]
        evaluated = []
        for action in actions:
            reward, successor = _step(physical, competence, demand, action)
            evaluated.append((action, reward, successor))
        maximum = max(reward for _, reward, _ in evaluated)
        selected_reward = next(reward for action, reward, _ in evaluated if action == selected)
        assert maximum - selected_reward <= TOL
        assert select_best_myopic_action(competence, evaluated)[0] == selected
        gains = [select_best_myopic_action(competence, [entry])[3]
                 for entry in evaluated if maximum - entry[1] <= TOL]
        saw_different_secondary_gains |= len(set(gains)) > 1
        chosen_forward = select_best_myopic_action(competence, evaluated)[0]
        chosen_reverse = select_best_myopic_action(competence, tuple(reversed(evaluated)))[0]
        if len(set(gains)) > 1:
            assert chosen_forward == chosen_reverse
    assert saw_different_secondary_gains


def test_tie_audit_identifies_learning_and_preserves_legacy_results():
    case = make_characterization_case("opportunity")
    for transfer in (False, True):
        legacy = solve_reactive_greedy(case, transfer_available=transfer)
        best = solve_best_myopic(case, transfer_available=transfer)
        audit = audit_myopic_tiebreaks(case, legacy, best,
                                       transfer_available=transfer)
        assert len(audit) == 32
        assert sum(row["tied_action_count"] > 1 for row in audit) == 16
        assert sum(row["selected_actions_differ"] for row in audit) == 16
        assert all("B_different_competence_successors" in row["tie_classes"]
                   for row in audit if row["tied_action_count"] > 1)
        assert all("C_other_physical_or_resource_differences" in row["tie_classes"]
                   for row in audit if row["tied_action_count"] > 1)
        assert all("A_equivalent_physical_consequences" not in row["tie_classes"]
                   for row in audit if row["tied_action_count"] > 1)
        assert legacy.value == pytest.approx(3.0346209871)
        assert best.value == pytest.approx(3.0444737839)


def test_six_policy_runner_reproduces_values_decompositions_and_sacrifice():
    result = run()
    assert result["validation"]["all_16_branch_probabilities_sum_to_one"]
    assert result["validation"]["legacy_four_values_reproduced"]
    assert result["validation"]["decomposition_identities_hold"]
    values = {key: row["ces_cumulative"]["value"] for key, row in result["policies"].items()}
    assert values == pytest.approx({
        "A": 3.1628653621,
        "B": 3.1743777327,
        "MA": 3.0346209871,
        "MB": 3.0346209871,
        "BMA": 3.0444737839,
        "BMB": 3.0444737839,
    })
    d0 = result["decomposition_CES"]["without_transfer"]
    assert d0["D0_historical_Bellman_minus_legacy_myopic"] == pytest.approx(0.128244375)
    assert d0["D1_Bellman_minus_BEST_MYOPIC"] == pytest.approx(0.1183915782)
    assert d0["T0_BEST_MYOPIC_minus_legacy_myopic"] == pytest.approx(0.0098527968)
    assert d0["identity_residual"] == pytest.approx(0.0)
    d0t = result["decomposition_CES"]["with_transfer"]
    assert d0t["D0T_historical_Bellman_minus_legacy_myopic"] == pytest.approx(0.1397567456)
    assert d0t["D1T_Bellman_minus_BEST_MYOPIC"] == pytest.approx(0.1299039488)
    assert d0t["TT_BEST_MYOPIC_minus_legacy_myopic"] == pytest.approx(0.0098527968)
    assert result["bellman_strict_immediate_sacrifice"]["A_without_transfer"][
        "strict_immediate_sacrifice_state_count"] == 0
    transfer = result["bellman_strict_immediate_sacrifice"]["B_with_transfer"]
    assert transfer["strict_immediate_sacrifice_state_count"] == 1
    sacrifice = transfer["states"][0]
    assert sacrifice["immediate_CES_sacrifice"] == pytest.approx(0.175)
    assert sacrifice["local_Q_advantage_of_Bellman_action"] == pytest.approx(0.0115123706)
    assert result["myopic_tie_audit"]["MA"]["tie_class_counts_nonexclusive"][
        "C_other_physical_or_resource_differences"] == 16
    assert result["myopic_tie_audit"]["MA"]["tie_class_counts_nonexclusive"][
        "B_different_competence_successors"] == 16
