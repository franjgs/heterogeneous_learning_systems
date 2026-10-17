from dataclasses import fields
import os
import subprocess
import sys

import pytest

from hls.contextual_router import (
    CandidatePrior,
    CandidateSpec,
    ContextualQualityCostRouter,
    ContextualRouterConfig,
    ExecutionOutcome,
    QuerySpec,
    run_contextual_routing,
    serialize_routing_run,
    summarize_routing_run,
)
from hls.contextual_router_synthetic import (
    SyntheticCandidateResponse,
    SyntheticContextualEnvironment,
)


def _router(priors, *, candidates=("A", "B"), epsilon=0.0, seed=17,
            regularization=1.0, include_intercept=False):
    config = ContextualRouterConfig(
        context_dimension=2,
        include_intercept=include_intercept,
        quality_regularization=regularization,
        cost_regularization=regularization,
        currency="SIM-USD",
        accounting_version="sim-v1",
        evaluator_version="rubric-v1",
        epsilon=epsilon,
        exploration_seed=seed,
    )
    specs = tuple(CandidateSpec(name) for name in candidates)
    return ContextualQualityCostRouter(config, specs, tuple(
        CandidatePrior(name, priors[name][0], priors[name][1]) for name in candidates
    ))


def _contract_priors():
    return {
        "A": ((0.80, 0.90), (1.00, 0.90)),
        "B": ((0.90, 0.70), (0.70, 0.50)),
    }


def test_ridge_update_matches_contract_hand_calculation_and_example_reroutes():
    router = _router(_contract_priors())
    qx = QuerySpec("x0", (1.0, 0.0), 0.75)
    before = router.decide(qx)
    assert before.selected_candidate_id == "B"
    forecast = next(item for item in before.forecasts if item.candidate_id == "B")
    assert (forecast.predicted_quality, forecast.predicted_cost) == (0.9, 0.7)

    receipt = router.observe(qx, ExecutionOutcome(
        "x0", "B", 0.5, 0.9, "SIM-USD", "sim-v1", "rubric-v1"
    ))
    assert receipt.quality_updated and receipt.cost_updated
    assert receipt.quality_count_after == receipt.cost_count_after == 1
    next_decision = router.decide(QuerySpec("x1", (1.0, 0.0), 0.75))
    assert next_decision.selected_candidate_id == "A"
    b_after = next(item for item in next_decision.forecasts if item.candidate_id == "B")
    assert b_after.predicted_quality == pytest.approx(0.7)
    assert b_after.predicted_cost == pytest.approx(0.8)
    y_decision = router.decide(QuerySpec("y0", (0.0, 1.0), 0.65))
    assert y_decision.selected_candidate_id == "B"


def test_contextual_quality_and_cost_are_candidate_specific():
    router = _router({
        "A": ((0.2, 0.8), (0.1, 1.0)),
        "B": ((0.8, 0.2), (1.0, 0.1)),
    })
    x = router.decide(QuerySpec("x", (1.0, 0.0), 0.5))
    y = router.decide(QuerySpec("y", (0.0, 1.0), 0.5))
    assert {f.candidate_id: f.predicted_quality for f in x.forecasts} == {"A": 0.2, "B": 0.8}
    assert {f.candidate_id: f.predicted_quality for f in y.forecasts} == {"A": 0.8, "B": 0.2}
    assert {f.candidate_id: f.predicted_cost for f in x.forecasts} == {"A": 0.1, "B": 1.0}
    assert {f.candidate_id: f.predicted_cost for f in y.forecasts} == {"A": 1.0, "B": 0.1}


def test_quality_threshold_uses_min_cost_then_higher_quality():
    router = _router({
        "A": ((0.8, 0.0), (0.9, 0.0)),
        "B": ((0.9, 0.0), (0.4, 0.0)),
    })
    decision = router.decide(QuerySpec("q", (1.0, 0.0), 0.75))
    assert decision.selected_candidate_id == "B"
    assert decision.reason == "minimum_predicted_cost_meeting_quality_target"

    tied = _router({
        "z": ((0.8, 0.0), (0.4, 0.0)),
        "a": ((0.8, 0.0), (0.4, 0.0)),
    }, candidates=("z", "a"))
    assert tied.decide(QuerySpec("tie", (1.0, 0.0), 0.75)).selected_candidate_id == "a"


def test_fallback_uses_maximum_quality_then_cost_then_id():
    router = _router({
        "A": ((0.6, 0.0), (0.8, 0.0)),
        "B": ((0.6, 0.0), (0.3, 0.0)),
    })
    result = router.decide(QuerySpec("fallback", (1.0, 0.0), 0.9))
    assert result.selected_candidate_id == "B"
    assert result.reason == "maximum_predicted_quality_fallback"


def test_predicted_budget_filters_candidates_but_actual_budget_is_separate():
    router = _router({
        "A": ((0.9, 0.0), (1.5, 0.0)),
        "B": ((0.8, 0.0), (0.4, 0.0)),
    })

    class Executor:
        def execute(self, candidate, query):
            return ExecutionOutcome(query.query_id, candidate.candidate_id,
                                    0.85, 0.8, "SIM-USD", "sim-v1", "rubric-v1")

    result = run_contextual_routing(
        (QuerySpec("budget", (1.0, 0.0), 0.7, cost_budget=0.6),), router, Executor()
    )
    trace = result.traces[0]
    assert trace.decision.selected_candidate_id == "B"
    assert trace.predicted_budget_compliant is True
    assert trace.actual_budget_compliant is False
    assert summarize_routing_run(result)["predicted_budget_compliance_rate"] == 1.0
    assert summarize_routing_run(result)["actual_budget_compliance_rate"] == 0.0


def test_no_budget_feasible_or_no_resource_eligible_candidate_means_no_execution():
    router = _router({
        "A": ((0.9, 0.0), (1.5, 0.0)),
        "B": ((0.8, 0.0), (0.9, 0.0)),
    })

    class NeverExecutor:
        def execute(self, candidate, query):
            raise AssertionError("infeasible query must not execute")

    over_budget = run_contextual_routing(
        (QuerySpec("q1", (1.0, 0.0), 0.2, 0.1),), router, NeverExecutor()
    ).traces[0]
    assert over_budget.decision.selected_candidate_id is None
    assert over_budget.decision.reason == "no_predicted_budget_feasible_candidate"

    unavailable = router.decide(QuerySpec("q2", (1.0, 0.0), 0.2), ())
    assert unavailable.selected_candidate_id is None
    assert unavailable.reason == "no_resource_eligible_candidate"


def test_static_query_eligibility_is_respected():
    candidates = (CandidateSpec("A", eligible_query_ids=("other",)), CandidateSpec("B"))
    priors = (CandidatePrior("A", (0.9,), (0.1,)),
              CandidatePrior("B", (0.8,), (0.8,)))
    router = ContextualQualityCostRouter(ContextualRouterConfig(
        1, include_intercept=False, accounting_version="sim-v1",
        evaluator_version="rubric-v1"), candidates, priors)
    assert router.decide(QuerySpec("q", (1.0,), 0.5)).selected_candidate_id == "B"


def test_exploration_is_optional_seeded_and_never_overrides_predicted_budget():
    priors = {
        "A": ((0.9, 0.0), (0.1, 0.0)),
        "B": ((0.1, 0.0), (0.2, 0.0)),
    }
    greedy = _router(priors, epsilon=0.0)
    assert greedy.decide(QuerySpec("g", (1.0, 0.0), 0.8)).selected_candidate_id == "A"
    first = _router(priors, epsilon=1.0, seed=44)
    second = _router(priors, epsilon=1.0, seed=44)
    queries = tuple(QuerySpec(f"e{i}", (1.0, 0.0), 0.8, cost_budget=0.15) for i in range(4))
    for query in queries:
        left, right = first.decide(query), second.decide(query)
        assert left == right
        assert left.exploratory
        assert left.selected_candidate_id == "A"
        assert not left.quality_threshold_overridden

    override = _router(priors, epsilon=1.0, seed=2)
    # A is unavailable so exploration may explicitly choose B below Q_min.
    decision = override.decide(QuerySpec("low", (1.0, 0.0), 0.8), ("B",))
    assert decision.selected_candidate_id == "B"
    assert decision.quality_threshold_overridden


def test_missing_feedback_and_failed_execution_do_not_create_fake_labels():
    router = _router(_contract_priors())
    query = QuerySpec("fail", (1.0, 0.0), 0.2)

    class FailedExecutor:
        def execute(self, candidate, query):
            return ExecutionOutcome(query.query_id, candidate.candidate_id, None, None,
                                    "SIM-USD", "sim-v1", "rubric-v1", status="failed")

    trace = run_contextual_routing((query,), router, FailedExecutor()).traces[0]
    assert trace.outcome is not None and trace.outcome.status == "failed"
    assert not trace.update.quality_updated and not trace.update.cost_updated
    assert trace.update.state_version_after == trace.update.state_version_before == 0
    assert all(f.quality_count == f.cost_count == 0 for f in trace.decision.forecasts)


def test_quality_and_cost_feedback_update_independently_and_candidates_do_not_leak():
    router = _router(_contract_priors())
    query = QuerySpec("partial", (1.0, 0.0), 0.1)
    before_b = next(f for f in router.decide(query).forecasts if f.candidate_id == "B")
    receipt = router.observe(query, ExecutionOutcome(
        "partial", "B", None, 0.95, "SIM-USD", "sim-v1", "rubric-v1"
    ))
    after = router.decide(QuerySpec("next", (1.0, 0.0), 0.1))
    b = next(f for f in after.forecasts if f.candidate_id == "B")
    a = next(f for f in after.forecasts if f.candidate_id == "A")
    assert receipt.quality_count_after == 0 and receipt.cost_count_after == 1
    assert b.predicted_quality == before_b.predicted_quality
    assert b.predicted_cost != before_b.predicted_cost
    assert a.quality_count == a.cost_count == 0


def test_execution_is_selected_only_and_router_has_no_environment_truth():
    responses = (
        SyntheticCandidateResponse("A", 0.9, (0.0, 0.0), 0.2, (0.0, 0.0)),
        SyntheticCandidateResponse("B", 0.2, (0.0, 0.0), 0.1, (0.0, 0.0)),
    )
    env = SyntheticContextualEnvironment(
        responses, seed=5, accounting_version="sim-v1", evaluator_version="rubric-v1"
    )
    router = _router(_contract_priors())

    class SpyExecutor:
        calls = []

        @property
        def replay_metadata(self):
            return env.replay_metadata

        def execute(self, candidate, query):
            self.calls.append(candidate.candidate_id)
            return env.execute(candidate, query)

    executor = SpyExecutor()
    q = QuerySpec("only", (1.0, 0.0), 0.75)
    run = run_contextual_routing((q,), router, executor, run_id="selected-only")
    trace = run.traces[0]
    assert executor.calls == [trace.decision.selected_candidate_id]
    assert not hasattr(router, "_responses")
    assert not hasattr(trace.decision, "quality_true")
    assert not hasattr(trace.outcome, "counterfactuals")
    assert "quality_intercept" not in {item.name for item in fields(trace.decision)}
    assert run.run_id == "selected-only"
    assert dict(run.executor_replay_metadata)["executor_seed"] == "5"
    assert "quality_intercept" not in serialize_routing_run(run)
    assert run.initial_priors == tuple(CandidatePrior(
        candidate_id, *_contract_priors()[candidate_id]
    ) for candidate_id in ("A", "B"))


def test_synthetic_truth_functions_are_context_and_candidate_dependent():
    responses = (
        SyntheticCandidateResponse("A", 0.2, (0.6, 0.0), 0.1, (0.9, 0.0)),
        SyntheticCandidateResponse("B", 0.7, (-0.4, 0.0), 0.8, (-0.5, 0.0)),
    )
    env1 = SyntheticContextualEnvironment(responses, seed=7)
    env2 = SyntheticContextualEnvironment(responses, seed=7)
    a_x = env1.execute(CandidateSpec("A"), QuerySpec("x", (1.0, 0.0), 0.0))
    a_y = env2.execute(CandidateSpec("A"), QuerySpec("y", (0.0, 1.0), 0.0))
    b_x = SyntheticContextualEnvironment(responses, seed=7).execute(
        CandidateSpec("B"), QuerySpec("x", (1.0, 0.0), 0.0)
    )
    assert a_x.observed_quality == pytest.approx(0.8)
    assert a_y.observed_quality == pytest.approx(0.2)
    assert b_x.observed_quality == pytest.approx(0.3)
    assert a_x.observed_cost == pytest.approx(1.0)
    assert b_x.observed_cost == pytest.approx(0.3)


def test_synthetic_noise_and_router_replay_are_reproducible():
    responses = (
        SyntheticCandidateResponse("A", 0.6, (0.1, 0.2), 0.7, (0.1, 0.2)),
        SyntheticCandidateResponse("B", 0.7, (0.0, 0.1), 0.5, (0.2, 0.0)),
    )

    def run():
        router = _router(_contract_priors(), epsilon=0.4, seed=99)
        environment = SyntheticContextualEnvironment(
            responses, quality_noise_radius=0.1, cost_noise_radius=0.1, seed=23,
            accounting_version="sim-v1", evaluator_version="rubric-v1"
        )
        queries = (QuerySpec("q0", (1.0, 0.0), 0.6),
                   QuerySpec("q1", (0.0, 1.0), 0.6))
        return run_contextual_routing(queries, router, environment)

    first, second = run(), run()
    assert first == second
    assert serialize_routing_run(first) == serialize_routing_run(second)


def test_serialized_replay_matches_in_a_fresh_python_process():
    script = r'''
from hls.contextual_router import *
from hls.contextual_router_synthetic import *
candidates = (CandidateSpec("A"), CandidateSpec("B"))
priors = (CandidatePrior("A", (0.7, 0.1), (0.4, 0.0)),
          CandidatePrior("B", (0.6, 0.2), (0.3, 0.1)))
config = ContextualRouterConfig(1, epsilon=0.25, exploration_seed=13)
router = ContextualQualityCostRouter(config, candidates, priors)
environment = SyntheticContextualEnvironment((
    SyntheticCandidateResponse("A", 0.7, (0.1,), 0.4, (0.1,)),
    SyntheticCandidateResponse("B", 0.6, (0.2,), 0.3, (0.0,)),
), seed=29, quality_noise_radius=0.03, cost_noise_radius=0.02)
queries = (QuerySpec("q1", (0.0,), 0.6), QuerySpec("q2", (1.0,), 0.5))
print(serialize_routing_run(run_contextual_routing(queries, router, environment)))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, ("src", env.get("PYTHONPATH", ""))))
    first = subprocess.run([sys.executable, "-c", script], check=True, capture_output=True,
                           text=True, env=env).stdout
    second = subprocess.run([sys.executable, "-c", script], check=True, capture_output=True,
                            text=True, env=env).stdout
    assert first == second


def test_invalid_dimensions_domains_versions_and_duplicate_feedback_fail_clearly():
    with pytest.raises(ValueError):
        QuerySpec("q", (float("nan"),), 0.5)
    with pytest.raises(ValueError):
        QuerySpec("q", (1.0,), 1.1)
    with pytest.raises(ValueError):
        ExecutionOutcome("q", "A", 1.2, 0.0, "SIM-USD", "sim-v1", "rubric-v1")
    router = _router(_contract_priors())
    query = QuerySpec("q", (1.0, 0.0), 0.1)
    outcome = ExecutionOutcome("q", "A", 0.5, 0.2, "SIM-USD", "sim-v1", "rubric-v1")
    router.observe(query, outcome)
    with pytest.raises(ValueError, match="duplicate feedback"):
        router.observe(query, outcome)
    query_currency = QuerySpec("q2", (1.0, 0.0), 0.1)
    with pytest.raises(ValueError, match="currency"):
        router.observe(query_currency, ExecutionOutcome(
            "q2", "B", 0.5, 0.2, "EUR", "sim-v1", "rubric-v1"
        ))


def test_query_ids_must_be_unique_in_a_run():
    router = _router(_contract_priors())

    class Executor:
        def execute(self, candidate, query):
            return ExecutionOutcome(query.query_id, candidate.candidate_id, None, None,
                                    "SIM-USD", "sim-v1", "rubric-v1", status="failed")

    repeated = (QuerySpec("same", (1.0, 0.0), 0.5),
                QuerySpec("same", (0.0, 1.0), 0.5))
    with pytest.raises(ValueError, match="unique"):
        run_contextual_routing(repeated, router, Executor())


def test_summary_keeps_quality_cost_and_resource_measures_separate():
    router = _router({
        "A": ((0.8, 0.0), (0.4, 0.0)),
        "B": ((0.7, 0.0), (0.2, 0.0)),
    })
    env = SyntheticContextualEnvironment((
        SyntheticCandidateResponse("A", 0.8, (0.0, 0.0), 0.4, (0.0, 0.0)),
        SyntheticCandidateResponse("B", 0.7, (0.0, 0.0), 0.2, (0.0, 0.0)),
    ), accounting_version="sim-v1", evaluator_version="rubric-v1")
    run = run_contextual_routing((QuerySpec("q", (1.0, 0.0), 0.5),), router, env)
    summary = summarize_routing_run(run)
    assert summary["executed"] == 1
    assert summary["mean_observed_quality"] == pytest.approx(0.7)
    assert summary["mean_observed_cost"] == pytest.approx(0.2)
    assert "net_utility" not in summary
