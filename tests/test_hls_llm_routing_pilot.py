import itertools

import numpy as np

from hls.experiment_contract import ExperimentEvent, ExperimentRun, UnitDeclaration
from hls.llm_routing_pilot import (
    ContextualLogisticQualityPredictor, MIRTQualityPredictor,
    budget_between_extremes, greedy_feasible,
    independent_with_repair, solve_batch_ilp,
)
from hls.performance_evaluation import (
    EvaluationProfile, EvaluationRecord, PerformanceEvaluator,
)


def test_mirt_fit_predict_is_finite_and_bounded():
    questions = [f"question about topic {i % 3} option A option B" for i in range(30)]
    y = np.asarray([[int((i + m) % 3 != 0) for m in range(3)] for i in range(30)])
    predictor = MIRTQualityPredictor(n_features=32).fit(questions, ("m0", "m1", "m2"), y)
    assert predictor.fit_info["success"] is True
    pred = predictor.predict(["question about topic 1 option A option B"])
    assert pred.shape == (1, 3)
    assert np.isfinite(pred).all()
    assert ((pred >= 0) & (pred <= 1)).all()


def test_contextual_logistic_uses_text_task_model_and_grouped_cv():
    queries = [f"question {i} with subject clue topic {i % 2}" for i in range(30)]
    tasks = ["biology" if i % 2 else "math" for i in range(30)]
    y = np.asarray([[int((i + m + (i % 2)) % 3 != 0) for m in range(3)] for i in range(30)])
    predictor = ContextualLogisticQualityPredictor(c_grid=(0.1, 1.0), n_features=64)
    predictor.fit(queries, tasks, ("m0", "m1", "m2"), y, [f"q{i}" for i in range(30)])
    pred = predictor.predict([queries[0], queries[1]], [tasks[0], tasks[1]])
    assert pred.shape == (2, 3)
    assert np.isfinite(pred).all()
    assert ((pred >= 0) & (pred <= 1)).all()
    assert predictor.fit_info["n_grouped_folds"] == 5
    assert predictor.fit_info["n_training_queries"] == 30
    assert predictor.fit_info["selected_C"] in (0.1, 1.0)


def test_batch_ilp_matches_brute_force_and_respects_budget():
    quality = np.asarray([[0.2, 0.8, 0.9], [0.9, 0.6, 0.7], [0.3, 0.8, 0.95]])
    costs = np.asarray([[1.0, 2.0, 4.0], [1.0, 2.5, 4.0], [1.0, 2.0, 4.0]])
    budget = 7.0
    selected = solve_batch_ilp(quality, costs, budget)
    actual = float(quality[np.arange(3), selected].sum())
    expected = max(
        float(quality[np.arange(3), choice].sum())
        for choice in itertools.product(range(3), repeat=3)
        if float(costs[np.arange(3), choice].sum()) <= budget + 1e-9
    )
    assert abs(actual - expected) < 1e-8
    assert costs[np.arange(3), selected].sum() <= budget + 1e-8


def test_greedy_and_repaired_independent_are_budget_feasible():
    quality = np.asarray([[0.2, 0.8, 0.9], [0.9, 0.6, 0.7], [0.3, 0.8, 0.95]])
    costs = np.asarray([[1.0, 2.0, 4.0], [1.0, 2.5, 4.0], [1.0, 2.0, 4.0]])
    budget = 6.0
    for choice in (greedy_feasible(quality, costs, budget),
                   independent_with_repair(quality, costs, budget, price=0.0)):
        assert costs[np.arange(3), choice].sum() <= budget + 1e-8


def test_budget_fraction_is_between_cheapest_and_most_expensive():
    costs = np.asarray([[1, 2, 4], [2, 3, 6]], dtype=float)
    low = budget_between_extremes(costs, 0.0)
    high = budget_between_extremes(costs, 1.0)
    middle = budget_between_extremes(costs, 0.5)
    assert low == 3
    assert high == 10
    assert middle == 6.5


def test_hls_pef_evaluates_correctness_and_local_inference_resource():
    profile = EvaluationProfile(
        profile_id="mmlu-pilot-test", scenario_id="mmlu", configuration_id="test",
        application_domain="local LLM", organizational_problem="budgeted query assignment",
        decision_objective={"ilp": "maximize exact answer correctness"},
        constraints="one model per query; total inference seconds bounded",
        primary_metrics=("functional_success_rate", "original_reward_cumulative"),
        secondary_metrics=("resource_usage:inference_latency_seconds",),
        information_regime="test outcomes hidden except retrospective evaluation",
        temporal_horizon=2, aggregation_rules="one MMLU query per period",
        demand_distribution_id="two-fixed-queries",
        resource_units={"inference_latency_seconds": "seconds"},
    )
    records = [
        EvaluationRecord(
            scenario_id="mmlu", configuration_id="test", policy_id="ilp", period=i,
            demand="subject", success=bool(success), original_reward=float(success),
            resource_usage={"inference_latency_seconds": latency},
            provenance=f"test:{i}", information_regime=profile.information_regime,
            decision_objective="maximize exact answer correctness",
        )
        for i, (success, latency) in enumerate(((1, 0.2), (0, 0.3)))
    ]
    evaluator = PerformanceEvaluator()
    evaluator.register_profile(profile)
    result = evaluator.evaluate(profile.profile_id, "ilp", records)
    assert result["functional_success_rate"].value == 0.5
    assert result["original_reward_cumulative"].value == 1.0
    assert abs(result["resource_usage:inference_latency_seconds"].value - 0.5) < 1e-12

    run = ExperimentRun(
        schema_version="hls-experiment-run/1.0", run_id="mmlu-test", mechanism_id="ilp",
        policy_id="ilp", configuration={"scenario_id": "mmlu"}, initial_conditions={},
        random_seeds=(), information_available={"test_labels": "hidden"},
        observation_model={"generation": "greedy"}, software_revision=None,
        units=(UnitDeclaration("latency", "seconds", "local request time"),),
        events=(ExperimentEvent(0, "assignment", "ilp", {"query": 0, "model": "m0"}),),
        metrics=(), mechanism_results={"correct": 1}, metadata={"profile": profile.profile_id},
    )
    restored = ExperimentRun.from_json(run.to_json())
    assert restored.run_id == run.run_id
    assert restored.events[0].data["model"] == "m0"
