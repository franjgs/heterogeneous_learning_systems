from dataclasses import FrozenInstanceError, replace
import inspect

import pytest

from hls.a1a import reference_worlds
from hls.a1c import relabel_world
from hls.synthetic import (
    DevelopmentDecision,
    InformationContract,
    NULL_DEVELOPMENT,
    Opportunity,
    WorldState,
)
from hls.synthetic.adapters.a1 import (
    a1_information_contracts,
    build_a1_environment,
    evaluate_a1_exact,
)
from hls.synthetic.components import (
    A1MixtureOpportunityKernel,
    A1ResourceModel,
    A1SaturatingDevelopmentKernel,
    BoundedMatrixCompetence,
    CompetenceRewardModel,
    ContractInformationModel,
    FiniteTaskSequence,
)
from hls.synthetic.environment import SyntheticEnvironment
from hls.synthetic.interfaces import (
    CompetenceModel,
    DevelopmentKernel,
    InformationModel,
    OpportunityKernel,
    ResourceModel,
    RewardModel,
    TaskProcess,
)
from hls.synthetic.randomness import SeededRandomSource


def _generic_environment() -> SyntheticEnvironment:
    learners = {"L1": 0, "L2": 1, "L3": 2}
    tasks = {"q1": 0, "q2": 1, "q3": 2, "q4": 3}
    return SyntheticEnvironment(
        tasks=FiniteTaskSequence(("q1", "q2", "q3")),
        competence=BoundedMatrixCompetence(
            ((0.1, 0.2, 0.3, 0.4), (0.4, 0.3, 0.2, 0.1), (0.5, 0.5, 0.5, 0.5))
        ),
        opportunities=A1MixtureOpportunityKernel(
            {"q1": 0.5},
            {(learner, "q1"): 0.5 for learner in learners},
            0.0,
        ),
        development=A1SaturatingDevelopmentKernel(learners, tasks, "q3", 0.5),
        reward=CompetenceRewardModel(learners, tasks),
        resources=A1ResourceModel(0.1, 1.0),
        information=ContractInformationModel(),
        randomness=SeededRandomSource(0),
    )


def test_seven_theta_blocks_are_distinct_components() -> None:
    environment = _generic_environment()
    assert isinstance(environment.tasks, TaskProcess)
    assert isinstance(environment.competence, CompetenceModel)
    assert isinstance(environment.opportunities, OpportunityKernel)
    assert isinstance(environment.development, DevelopmentKernel)
    assert isinstance(environment.reward, RewardModel)
    assert isinstance(environment.resources, ResourceModel)
    assert isinstance(environment.information, InformationModel)
    assert len({id(component) for component in (
        environment.tasks,
        environment.competence,
        environment.opportunities,
        environment.development,
        environment.reward,
        environment.resources,
        environment.information,
    )}) == 7


def test_replacing_one_component_does_not_mutate_the_others() -> None:
    environment = _generic_environment()
    replacement = FiniteTaskSequence(("q2",))
    changed = replace(environment, tasks=replacement)
    assert changed.tasks is replacement
    for field in ("competence", "opportunities", "development", "reward", "resources", "information"):
        assert getattr(changed, field) is getattr(environment, field)


def test_policy_cannot_mutate_world_state_directly() -> None:
    state = _generic_environment().initial_state()
    with pytest.raises(FrozenInstanceError):
        state.time = 4  # type: ignore[misc]
    with pytest.raises(TypeError):
        state.competence[0][0] = 1.0  # type: ignore[index]


def test_development_kernel_owns_competence_transition() -> None:
    environment = _generic_environment()
    state = environment.initial_state()
    action = DevelopmentDecision("L2", "q3")
    changed = environment.development.transition(state, Opportunity(True), action)
    assert changed.competence[1][2] == pytest.approx(0.6)
    assert state.competence[1][2] == 0.2
    assert changed.time == state.time + 1


def test_operational_actor_and_development_recipient_are_separate() -> None:
    evaluation = evaluate_a1_exact(build_a1_environment(reference_worlds()["E"]))
    assert evaluation.hls.optimal_actions == frozenset({"M2"})
    assert evaluation.optimal_development_actions == frozenset(
        {DevelopmentDecision("M1", 2)}
    )


def test_null_development_preserves_competence() -> None:
    environment = _generic_environment()
    state = environment.initial_state()
    changed = environment.development.transition(state, Opportunity(True), NULL_DEVELOPMENT)
    assert changed.competence == state.competence


def test_world_core_has_no_a1_policy_solver_dependency() -> None:
    import hls.synthetic.environment as environment_module
    import hls.synthetic.interfaces as interfaces_module

    source = inspect.getsource(environment_module) + inspect.getsource(interfaces_module)
    assert "solve_hls" not in source
    assert "solve_strong_sep" not in source
    assert "solve_sep_omega" not in source
    assert "if policy" not in source


def test_policies_receive_same_physical_world_with_different_information_contracts() -> None:
    environment = build_a1_environment(reference_worlds()["E"])
    state = environment.initial_state()
    rewards = {"M1": 0.8, "M2": 0.7}
    continuations = {"M1": 0.6045, "M2": 0.804}
    views = [
        environment.information.view(contract, state, 1, rewards, continuations)
        for contract in a1_information_contracts()
    ]
    assert all(view.state is state for view in views)
    assert all(view.task == 1 for view in views)
    assert views[0].continuations() == continuations
    assert views[1].continuations() == {}
    assert views[2].continuations() == continuations


def test_physical_relabeling_preserves_scalars_and_transforms_action_labels() -> None:
    world = reference_worlds()["E"]
    original = evaluate_a1_exact(build_a1_environment(world))
    relabeled = evaluate_a1_exact(build_a1_environment(relabel_world(world)))
    swap = {"M1": "M2", "M2": "M1"}
    assert relabeled.hls.value == pytest.approx(original.hls.value, abs=1e-12)
    assert relabeled.strong_sep.value_min == pytest.approx(original.strong_sep.value_min, abs=1e-12)
    assert relabeled.strong_sep.value_max == pytest.approx(original.strong_sep.value_max, abs=1e-12)
    assert relabeled.sep_omega.value == pytest.approx(original.sep_omega.value, abs=1e-12)
    assert relabeled.hls.optimal_actions == frozenset(swap[a] for a in original.hls.optimal_actions)
    assert relabeled.strong_sep.immediate_optimal_actions == frozenset(
        swap[a] for a in original.strong_sep.immediate_optimal_actions
    )


def test_general_objects_support_m_not_two_and_k_not_two() -> None:
    environment = _generic_environment()
    state = environment.initial_state()
    assert (state.n_learners, state.n_competences) == (3, 4)
    assert environment.reward.operational_reward(state, "q4", "L3") == 0.5


def test_a1_adapter_construction_has_no_policy_name_branch() -> None:
    source = inspect.getsource(build_a1_environment)
    assert "policy" not in source.lower()
    environment = build_a1_environment(reference_worlds()["E"])
    assert isinstance(environment.information, ContractInformationModel)


def test_information_contract_is_not_a_world_parameter() -> None:
    environment = _generic_environment()
    assert not hasattr(environment, "policy")
    contract = InformationContract("test")
    assert contract.name == "test"
