from dataclasses import replace

from experiments.run_hls_s4_transfer_exact import make_case
from hls.synthetic.hls_s4_transfer_exact import (
    _zero_efficacy,
    action_catalogs,
    independent_action_catalogs,
    independent_exhaustive,
    replay_actions,
    solve_bellman,
)


def test_optional_transfer_catalog_contains_all_mis_only_actions():
    case = make_case()
    catalogs_a = action_catalogs(case, transfer_available=False)
    catalogs_b = action_catalogs(case, transfer_available=True)
    rebuilt_a = independent_action_catalogs(case, transfer_available=False)
    rebuilt_b = independent_action_catalogs(case, transfer_available=True)
    assert [len(row) for row in catalogs_a] == [36, 36, 36]
    assert [len(row) for row in catalogs_b] == [72, 72, 72]
    for actions_a, actions_b in zip(catalogs_a, catalogs_b):
        assert set(actions_a).issubset(set(actions_b))
    assert [set(row) for row in catalogs_a] == [set(row) for row in rebuilt_a]
    assert [set(row) for row in catalogs_b] == [set(row) for row in rebuilt_b]


def test_bellman_matches_independent_sequence_enumeration_on_minimal_case():
    full_case = make_case()
    case = replace(full_case, problems=full_case.problems[:1])
    for transfer in (False, True):
        exact = solve_bellman(case, transfer_available=transfer)
        exhaustive, path, _, _ = independent_exhaustive(
            case, transfer_available=transfer,
        )
        assert abs(exact.value - exhaustive) < 1e-12
        assert len(path) == 1
        assert len(exact.periods) == 1
        assert exact.periods[0].total_resource <= case.organization.collective_effort_budget


def test_zero_physical_transfer_recovers_mis_only_optimum():
    case = make_case()
    mis_only = solve_bellman(case, transfer_available=False)
    zero_transfer = solve_bellman(
        case, transfer_available=True, efficacy=_zero_efficacy(case.efficacy),
    )
    assert abs(mis_only.value - zero_transfer.value) < 1e-12


def test_replay_records_existing_mis_then_transfer_transitions_and_resource_cost():
    case = make_case()
    action = next(
        action for action in action_catalogs(case, transfer_available=True)[0]
        if action.teaching is not None and sum(map(sum, action.production)) > 0
    )
    rows = replay_actions(case, (action, *(
        action_catalogs(case, transfer_available=False)[period][0]
        for period in (1, 2)
    )))
    row = rows[0]
    assert row.competence_after_mis != row.competence_before
    assert row.competence_after != row.competence_after_mis
    assert row.total_resource == row.productive_effort + row.teaching_resource
    assert row.total_resource <= min(
        case.organization.collective_effort_budget,
        case.problems[0].resource_budget,
    ) + 1e-12
