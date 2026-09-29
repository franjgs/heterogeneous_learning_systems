"""Exact reachability diagnostics for the preregistered central RQ0 world."""

from hls.synthetic.diagnostics import audit_optimal_hls_reachability
from hls.synthetic.rq0_campaign import world_by_name


def test_bstar_every_optimal_hls_reachable_state_has_greedy_hls_action():
    """The preregistered B* world has no unavoidable routing sacrifice."""
    world = world_by_name("B*")

    audit = audit_optimal_hls_reachability(
        world.problem,
        initial_state=world.initial_state,
    )

    assert audit.states
    assert audit.intersection_property_holds, [
        {
            "time": item.state.time,
            "competence": item.state.competence,
            "resources": item.state.resources,
            "task": item.task,
            "greedy": item.greedy_actions,
            "hls": item.hls_actions,
            "rewards": item.immediate_rewards,
            "q_values": item.hls_action_values,
        }
        for item in audit.states
        if not item.has_greedy_hls_action
    ]


def test_bstar_report_stronger_subset_property():
    """Record whether every optimal HLS routing action is also greedy."""
    world = world_by_name("B*")

    audit = audit_optimal_hls_reachability(
        world.problem,
        initial_state=world.initial_state,
    )

    # This is deliberately a gate: if it fails, inspect the counterexample
    # rather than weakening the scientific statement.
    assert audit.subset_property_holds, [
        {
            "time": item.state.time,
            "competence": item.state.competence,
            "resources": item.state.resources,
            "task": item.task,
            "greedy": item.greedy_actions,
            "hls": item.hls_actions,
            "common": item.common_actions,
            "rewards": item.immediate_rewards,
            "q_values": item.hls_action_values,
        }
        for item in audit.states
        if not item.all_hls_actions_are_greedy
    ]


def test_all_preregistered_worlds_optimal_reachability_properties():
    """Audit routing/development reducibility over all nine frozen worlds."""
    from hls.synthetic.rq0_campaign import worlds

    failures = []

    for world in worlds():
        audit = audit_optimal_hls_reachability(
            world.problem,
            initial_state=world.initial_state,
        )

        if (
            not audit.intersection_property_holds
            or not audit.subset_property_holds
        ):
            failures.append(
                {
                    "configuration": world.configuration.name,
                    "n_states": len(audit.states),
                    "intersection": audit.intersection_property_holds,
                    "subset": audit.subset_property_holds,
                    "counterexamples": [
                        {
                            "time": item.state.time,
                            "competence": item.state.competence,
                            "resources": item.state.resources,
                            "task": item.task,
                            "greedy": item.greedy_actions,
                            "hls": item.hls_actions,
                            "common": item.common_actions,
                            "rewards": item.immediate_rewards,
                            "q_values": item.hls_action_values,
                        }
                        for item in audit.states
                        if (
                            not item.has_greedy_hls_action
                            or not item.all_hls_actions_are_greedy
                        )
                    ],
                }
            )

    assert not failures, failures
