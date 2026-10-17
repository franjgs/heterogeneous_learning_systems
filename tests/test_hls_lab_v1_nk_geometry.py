"""Phase 1 acceptance tests for dimension-independent HLS state/action geometry."""

import pytest

from hls.discover_v0 import JOINT_ACTIONS
from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    OrganizationStateNK,
    ProblemSpecNK,
    enumerate_productive_allocations_nk,
    validate_productive_allocation_nk,
)


def _config(n, k, *, limits=None, budget=4.0, estimate=None):
    return OrganizationConfigNK(
        agent_ids=tuple(f"A{i}" for i in range(n)),
        skill_ids=tuple(f"S{i}" for i in range(k)),
        competence_initial=tuple(tuple((i + j) / (n + k + 1) for j in range(k)) for i in range(n)),
        effort_limits=tuple(limits if limits is not None else (1.0,) * n),
        collective_effort_budget=budget,
        competence_estimated_initial=estimate,
    )


def test_nk_state_is_rectangular_and_keeps_real_and_estimated_values_separate():
    config = OrganizationConfigNK(
        ("engineer", "trainee"), ("analysis", "design"),
        ((0.9, 0.2), (0.1, 0.8)), (1.0, 0.5), 1.25,
        ((0.8, 0.3), (0.4, 0.4)),
    )
    state = config.initial_state()
    assert state == OrganizationStateNK(
        ("engineer", "trainee"), ("analysis", "design"),
        ((0.9, 0.2), (0.1, 0.8)), ((0.8, 0.3), (0.4, 0.4)),
    )
    assert (state.n_agents, state.n_skills) == (2, 2)
    assert state.competence_real != state.competence_estimated


def test_competence_boundaries_zero_and_one_are_valid_and_preserved():
    state = OrganizationStateNK(
        ("boundary-agent",), ("zero-skill", "unit-skill"), ((0.0, 1.0),)
    )
    assert state.competence_real == ((0.0, 1.0),)
    assert state.competence_estimated == ((0.0, 1.0),)


@pytest.mark.parametrize("n,k", [(1, 1), (2, 2), (4, 3)])
def test_supported_nk_shapes_and_deterministic_catalog_enumeration(n, k):
    config = _config(n, k)
    problem = ProblemSpecNK("shape", tuple(0.1 for _ in range(k)), 2.0)
    zero = tuple(0.0 for _ in range(k))
    first_skill = (1.0,) + (0.0,) * (k - 1)
    catalogs = tuple((zero, first_skill) for _ in range(n))
    a = enumerate_productive_allocations_nk(
        config, problem, max_candidates=2**n, per_agent_effort_choices=catalogs
    )
    b = enumerate_productive_allocations_nk(
        config, problem, max_candidates=2**n, per_agent_effort_choices=catalogs
    )
    assert a == b
    assert a
    assert all(validate_productive_allocation_nk(action, config, problem) for action in a)
    assert all(len(action) == n and all(len(row) == k for row in action) for action in a)


def test_legacy_3x2_geometry_is_exactly_the_frozen_ordered_64_catalog():
    config = OrganizationConfigNK(
        ("E0", "E1", "E2"), ("skill0", "skill1"),
        ((0.2, 0.4), (0.1, 0.05), (0.95, 0.1)), (1.25,) * 3, 3.0,
    )
    problem = ProblemSpecNK("legacy-catalog", (0.2, 0.2), 3.0)
    catalog = enumerate_productive_allocations_nk(config, problem, max_candidates=64)
    assert len(catalog) == 64
    assert catalog == tuple(JOINT_ACTIONS)
    assert catalog[21] == JOINT_ACTIONS[21]


def test_individual_limits_shared_budget_and_problem_budget_are_all_enforced():
    config = _config(2, 2, limits=(0.5, 1.0), budget=1.25)
    problem = ProblemSpecNK("resources", (0.2, 0.3), 1.0)
    choices = (
        ((0.0, 0.0), (0.5, 0.0), (0.5, 0.5)),
        ((0.0, 0.0), (1.0, 0.0), (0.5, 0.5)),
    )
    actions = enumerate_productive_allocations_nk(
        config, problem, max_candidates=9, per_agent_effort_choices=choices
    )
    assert all(sum(row) <= config.effort_limits[i] + 1e-12 for action in actions
               for i, row in enumerate(action))
    assert all(sum(map(sum, action)) <= min(config.collective_effort_budget,
                                            problem.resource_budget) + 1e-12 for action in actions)
    assert ((0.5, 0.5), (0.0, 0.0)) not in actions


def test_catalog_limit_fails_explicitly_without_silent_truncation():
    config = _config(4, 3)
    problem = ProblemSpecNK("guard", (0.2, 0.2, 0.2), 4.0)
    choices = tuple(((0.0, 0.0, 0.0), (0.2, 0.0, 0.0)) for _ in range(4))
    with pytest.raises(ValueError, match=r"requires 16 candidates.*no actions were truncated"):
        enumerate_productive_allocations_nk(
            config, problem, max_candidates=15, per_agent_effort_choices=choices
        )


@pytest.mark.parametrize("build", [
    lambda: OrganizationConfigNK((), ("s",), (), (), 1.0),
    lambda: OrganizationConfigNK(("a",), (), ((0.2,),), (1.0,), 1.0),
    lambda: OrganizationConfigNK(("a", "a"), ("s",), ((0.2,), (0.3,)), (1, 1), 1),
    lambda: OrganizationConfigNK(("a",), ("s",), ((0.2, 0.3),), (1,), 1),
    lambda: OrganizationConfigNK(("a",), ("s",), ((1.1,),), (1,), 1),
    lambda: OrganizationConfigNK(("a",), ("s",), ((0.2,),), (-1,), 1),
    lambda: OrganizationConfigNK(("a",), ("s",), ((0.2,),), (1,), float("nan")),
    lambda: ProblemSpecNK("bad", (0.0, 0.0), 1.0),
    lambda: ProblemSpecNK("bad", (0.2,), -1.0),
])
def test_invalid_nk_configurations_are_rejected(build):
    with pytest.raises(ValueError):
        build()


def test_effort_catalog_shapes_and_problem_skill_dimension_are_validated():
    config = _config(2, 3)
    problem = ProblemSpecNK("bad-K", (0.2, 0.3), 1.0)
    with pytest.raises(ValueError, match="organization has K=3"):
        enumerate_productive_allocations_nk(
            config, problem, max_candidates=4,
            per_agent_effort_choices=(((0.0, 0.0, 0.0),),) * 2,
        )
    problem3 = ProblemSpecNK("bad-choice", (0.2, 0.3, 0.4), 1.0)
    with pytest.raises(ValueError, match="vectors must have K=3"):
        enumerate_productive_allocations_nk(
            config, problem3, max_candidates=1,
            per_agent_effort_choices=(((0.0, 0.0),),) * 2,
        )


def test_non_2_skill_geometry_requires_explicit_catalog_and_valid_ids():
    config = _config(1, 1)
    problem = ProblemSpecNK("explicit", (0.2,), 1.0)
    with pytest.raises(ValueError, match="requires an explicit"):
        enumerate_productive_allocations_nk(config, problem, max_candidates=1)
    with pytest.raises(ValueError, match="agent_ids must be unique"):
        OrganizationStateNK(("same", "same"), ("s",), ((0.2,), (0.4,)))


def test_invalid_budget_and_effort_choice_values_never_emit_infeasible_actions():
    config = _config(1, 1, limits=(0.25,), budget=0.25)
    problem = ProblemSpecNK("bounded", (0.3,), 0.25)
    actions = enumerate_productive_allocations_nk(
        config, problem, max_candidates=2,
        per_agent_effort_choices=(((0.0,), (0.25,)),),
    )
    assert actions == (((0.0,),), ((0.25,),))
    assert not validate_productive_allocation_nk(((0.5,),), config, problem)
    with pytest.raises(ValueError, match=r"finite values in \[0, 1\]"):
        enumerate_productive_allocations_nk(
            config, problem, max_candidates=1,
            per_agent_effort_choices=(((float("nan"),),),),
        )
