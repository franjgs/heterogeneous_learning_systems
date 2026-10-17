import json

import pytest

from hls.contextual_router import (
    CandidatePrior, CandidateSpec, ContextualQualityCostRouter,
    ContextualRouterConfig, QuerySpec, run_contextual_routing,
    serialize_routing_run,
)
from hls.contextual_router_synthetic import (
    SyntheticCandidateResponse, SyntheticContextualEnvironment,
)
from hls.experiment_contract import (
    ExperimentEvent, ExperimentRun, MetricValue, RunAdapterContext,
    SeedRecord, adapt_contextual_run, adapt_experiment_run, adapt_hls_nk_run,
    adapt_nembhard_run,
)
from hls.hls_lab_nk_environment import DemandRegimeNK, ExogenousEnvironmentConfigNK
from hls.hls_lab_nk_execution import (
    NKEnvironmentRunResult, NKNembhardDirectRunResult,
    run_nk_production_sequence, serialize_nk_learning_result,
    serialize_nk_nembhard_direct_result, serialize_nk_production_result,
)
from hls.hls_lab_nk_geometry import OrganizationConfigNK, ProblemSpecNK
from hls.hls_lab_nk_learning import LearningProfileNK
from hls.hls_lab_nk_policies import P1FixedTeachingNK
from hls.hls_lab_nk_nembhard import (
    NembhardDirectExecutionNK, NembhardDirectProfileNK,
    NembhardOutputUnitContract,
)
from hls.hls_lab_nk_nembhard_adaptive import NembhardAdaptiveRouterConfigNK
from hls.hls_lab_nk_teaching import TeachingEfficacyNK
from hls.synthetic.c5 import StationaryTaskDemand


def _org(competence=((0.4, 0.2),), budget=1.0):
    n, k = len(competence), len(competence[0])
    return OrganizationConfigNK(tuple(f"A{i}" for i in range(n)),
                                tuple(f"S{j}" for j in range(k)), competence,
                                (1.0,) * n, budget)


def _problem(problem_id="p", requirements=(0.2, 0.1), budget=1.0):
    return ProblemSpecNK(problem_id, requirements, budget)


def _nembhard_config(*, allocations, router_config=None):
    profile = NembhardDirectProfileNK(((2.0, 2.0),), ((0.0, 0.0),), ((2.0, 2.0),))
    units = NembhardOutputUnitContract(
        effort_intensity_unit="work/period", duration_unit="period",
        exposure_unit="work", output_unit="task-output",
        requirement_unit="task-output",
    )
    return NembhardDirectExecutionNK(profile, allocations, units), router_config


def _contextual_run(*, eligible=True):
    candidates = (CandidateSpec("c1"),)
    router = ContextualQualityCostRouter(
        ContextualRouterConfig(1, include_intercept=False, exploration_seed=11),
        candidates, (CandidatePrior("c1", (0.7,), (0.3,)),),
    )
    executor = SyntheticContextualEnvironment(
        (SyntheticCandidateResponse("c1", 0.8, (0.0,), 0.2, (0.0,)),), seed=17,
    )
    query = QuerySpec("q1", (0.5,), 0.6)
    return run_contextual_routing(
        (query,), router, executor,
        eligibility_by_query={"q1": ("c1",) if eligible else ()}, run_id="ctx-test",
    )


def test_hls_mis_v2_adapter_preserves_original_result_and_stable_json():
    org = _org()
    result = run_nk_production_sequence(org, (_problem(),), max_candidates=4)
    legacy_json = serialize_nk_production_result(result)
    first = adapt_hls_nk_run(result)
    replay = adapt_hls_nk_run(result)

    assert serialize_nk_production_result(result) == legacy_json
    assert first.to_json() == replay.to_json()
    assert first.schema_version == "hls-experiment-run/1.0"
    assert first.mechanism_id == "mis_v2" and first.policy_id == "p0"
    assert [event.event_type for event in first.events] == ["decision", "execution"]
    assert {metric.name for metric in first.metrics} >= {
        "functional_success_rate", "gross_ces_mean", "productive_effort_total"
    }
    assert all(metric.unit != "currency" for metric in first.metrics)
    decoded = json.loads(first.to_json())
    assert decoded["mechanism_results"]["records"][0]["outputs"] == list(result.records[0].outputs)


def test_hls_learning_adaptation_records_transition_and_does_not_change_legacy_serialization():
    org = _org()
    result = run_nk_production_sequence(
        org, (_problem(),), max_candidates=4, individual_learning=True,
        learning_profile=LearningProfileNK(((0.2, 0.3),)),
    )
    before = serialize_nk_learning_result(result)
    run = adapt_experiment_run(result)
    assert serialize_nk_learning_result(result) == before
    updates = [event for event in run.events if event.event_type == "state_update"]
    assert len(updates) == 1 and updates[0].data["update_kind"] == "mis_v2_competence"
    assert "learning_eta" in updates[0].data
    assert run.random_seeds == ()


def test_hls_teaching_and_imperfect_information_keep_event_kinds_and_period_order():
    org = OrganizationConfigNK(
        ("A0", "A1"), ("S0", "S1"), ((0.8, 0.2), (0.2, 0.1)),
        (1.0, 1.0), 2.0,
    )
    tensor = (
        ((0.0, 0.0), (0.8, 0.8)),
        ((0.8, 0.8), (0.0, 0.0)),
    )
    efficacy = TeachingEfficacyNK(org.agent_ids, org.skill_ids, tensor)
    p1 = P1FixedTeachingNK(("A0", "A1", "S0"))
    result = run_nk_production_sequence(
        org, (_problem(budget=2.0),), max_candidates=80,
        individual_learning=True, learning_profile=LearningProfileNK(((0.2, 0.2), (0.2, 0.2))),
        teaching_enabled=True, teaching_efficacy=efficacy, policy=p1,
        information_mode="imperfect", information_seed=37,
    )
    run = adapt_hls_nk_run(result)
    kinds = [event.event_type for event in run.events]
    assert kinds[0:2] == ["decision", "execution"]
    assert "observation" in kinds and "state_update" in kinds and "estimator_update" in kinds
    assert kinds.index("observation") < kinds.index("state_update")
    assert kinds.index("state_update") < kinds.index("estimator_update")
    decision = next(event for event in run.events if event.event_type == "decision")
    assert decision.data["teaching_action"] is not None
    assert run.information_available["mode"] == "imperfect"


def test_nembhard_explicit_adapter_keeps_experience_and_declares_units():
    execution, _ = _nembhard_config(allocations=(((0.5, 0.0),),))
    result = run_nk_production_sequence(
        _org(), (_problem(),), max_candidates=4,
        mechanism_id="nembhard_direct", nembhard_execution=execution,
    )
    assert isinstance(result, NKNembhardDirectRunResult)
    legacy_json = serialize_nk_nembhard_direct_result(result)
    run = adapt_nembhard_run(result)
    assert serialize_nk_nembhard_direct_result(result) == legacy_json
    assert run.mechanism_id == result.mechanism_id
    assert run.policy_id == "explicit_allocations"
    assert {unit.unit for unit in run.units} >= {"work/period", "period", "work", "task-output"}
    assert [event.event_type for event in run.events] == ["decision", "execution", "state_update"]
    assert run.events[-1].data["experience_after"] == [list(row) for row in result.final_experience]
    assert all("monetary" not in metric.unit for metric in run.metrics)


def test_nembhard_adaptive_events_separate_observation_estimator_and_experience():
    router_config = NembhardAdaptiveRouterConfigNK(
        epsilon=0.0, initial_productivity_estimate=0.2,
        observation_noise_stddev=0.0, observation_seed=19, exploration_seed=23,
    )
    execution, _ = _nembhard_config(allocations=(), router_config=router_config)
    result = run_nk_production_sequence(
        _org(((0.0, 0.0),)), (_problem(),), max_candidates=3,
        per_agent_effort_choices=(((0.0, 0.0), (0.5, 0.0), (0.0, 0.5)),),
        mechanism_id="nembhard_direct",
        nembhard_execution=execution, router_id="nembhard_adaptive",
        adaptive_router_config=router_config,
    )
    run = adapt_nembhard_run(result)
    kinds = [event.event_type for event in run.events]
    assert kinds.index("execution") < kinds.index("state_update")
    assert kinds.index("state_update") < kinds.index("observation")
    assert kinds.index("observation") < kinds.index("estimator_update")
    assert {seed.stream for seed in run.random_seeds} >= {
        "nembhard_observation", "nembhard_exploration"
    }
    assert run.events[0].data["policy_id"] == "nembhard_adaptive"


def test_contextual_adapter_keeps_quality_cost_and_feedback_separate():
    result = _contextual_run()
    old_json = serialize_routing_run(result)
    run = adapt_contextual_run(result)
    assert serialize_routing_run(result) == old_json
    assert run.mechanism_id == "contextual_quality_cost_hls_v0.1"
    assert run.policy_id == "contextual_quality_cost_router"
    assert [event.event_type for event in run.events] == [
        "decision", "execution", "observation", "estimator_update"
    ]
    names = {metric.name for metric in run.metrics}
    assert "mean_observed_quality" in names and "mean_observed_cost" in names
    assert "mean_absolute_quality_prediction_error" in names
    assert "mean_absolute_cost_prediction_error" in names
    units = {unit.quantity: unit.unit for unit in run.units}
    assert units["quality"] == "quality [0,1]"
    assert units["monetary_cost"] == result.currency
    assert {seed.stream for seed in run.random_seeds} == {
        "contextual_exploration", "contextual_executor"
    }


def test_no_selection_does_not_fabricate_execution_or_feedback_events():
    run = adapt_contextual_run(_contextual_run(eligible=False))
    assert [event.event_type for event in run.events] == ["decision"]
    assert not any(metric.name.startswith("mean_observed") for metric in run.metrics)


def test_contextual_and_environment_provenance_are_captured_without_guessing():
    contextual = adapt_contextual_run(
        _contextual_run(),
        context=RunAdapterContext(software_revision="abc123", configuration={"fixture": "test"}),
    )
    assert contextual.software_revision == "abc123"
    assert contextual.configuration == {"fixture": "test"}
    assert contextual.initial_conditions["predictor_initial_priors"]

    problem = _problem()
    environment = ExogenousEnvironmentConfigNK(
        StationaryTaskDemand({"task": 1.0}),
        {"task": DemandRegimeNK("fixed", (problem,), (1.0,))},
        horizon=1, resource_budget=1.0,
    )
    result = run_nk_production_sequence(_org(), None, max_candidates=4,
                                        environment=environment, environment_seed=29)
    common = adapt_hls_nk_run(result)
    assert common.run_id.startswith("hls-nk-")
    assert common.random_seeds[0] == SeedRecord("environment", 29, "exogenous demand generation")
    assert common.events[0].event_type == "environment_frozen"
    assert "environment_trajectory" in common.mechanism_results
    assert common.to_json() == adapt_hls_nk_run(result).to_json()


def test_optional_provenance_and_json_nonfinite_validation():
    run = ExperimentRun(
        "hls-experiment-run/1.0", "minimal", "test", None,
        None, None, None, None, None, None, (),
        (ExperimentEvent(0, "execution", "test", {"value": 1.0}),),
        (MetricValue("count", 1, "items", "A count."),),
        {"result": True}, {"provenance": "not supplied"},
    )
    payload = json.loads(run.to_json())
    assert payload["configuration"] is None
    assert payload["random_seeds"] is None
    with pytest.raises(ValueError, match="NaN or infinity"):
        ExperimentRun(
            "hls-experiment-run/1.0", "bad", "test", None,
            None, None, None, None, None, None, (), (), (),
            {"bad": float("nan")}, {},
        ).to_json()


def test_context_seeds_are_not_inferred_or_confused():
    result = run_nk_production_sequence(
        _org(), (_problem(),), max_candidates=4, information_mode="imperfect",
        information_seed=31,
    )
    common = adapt_hls_nk_run(result)
    assert common.random_seeds is None
    assert "not captured" in common.metadata["seed_status"]
    supplied = adapt_hls_nk_run(
        result, context=RunAdapterContext(random_seeds=(
            SeedRecord("competence_observation", 31, "N×K observation stream"),
        ))
    )
    assert supplied.random_seeds[0].stream == "competence_observation"


def test_unsupported_result_type_fails_clearly():
    with pytest.raises(TypeError, match="unsupported result type"):
        adapt_experiment_run(object())
