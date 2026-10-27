from hls.static_assignment import (StaticAllocationModel, ResourceConstrainedAllocationModel, REFERENCE_RESOURCE_ALLOCATION_CASES)
from hls.dynamic_development import FRONTIER_NULL_UNDER_LEARNING, DEVELOPMENT_VALUE_REVERSAL
from hls.catalog import load_catalog, validate_catalog
from pathlib import Path
from math import isclose

ROOT = Path(__file__).resolve().parents[1]


def test_static_crossed_specialization_exact_control():
    result = StaticAllocationModel(1.0, .2, .2, 1.0).evaluate(.5)
    assert result.best_same_agent_effectiveness == .6
    assert result.best_taskwise_effectiveness == 1.0
    assert result.allocation_gain == .4


def test_static_homogeneous_null():
    model = StaticAllocationModel(.7, .4, .7, .4)
    assert model.allocation_gain(.37) == 0


def test_static_taskwise_dominance_null():
    model = StaticAllocationModel(.9, .8, .4, .2)
    assert model.allocation_gain(.4) == 0


def test_resource_model_reports_gain_only_on_common_feasible_domain():
    result = REFERENCE_RESOURCE_ALLOCATION_CASES["bounded_gain_budget_window"].maximum_allocation_gain(.5)
    assert result is not None
    assert isclose(result.budget, .4, abs_tol=1e-12)
    assert isclose(result.allocation_gain, .0625, abs_tol=1e-12)


def test_geometric_frontier_expansion_can_have_zero_effectiveness_gain():
    result = REFERENCE_RESOURCE_ALLOCATION_CASES["geometric_expansion_without_gain"].maximum_allocation_gain(.5)
    assert result is not None
    assert isclose(result.allocation_gain, 0.0, abs_tol=1e-12)


def test_learning_can_change_state_without_efficient_terminal_outcomes_or_value_change():
    result = FRONTIER_NULL_UNDER_LEARNING.compare_choices(.5)
    assert result.agent_1_choice.competence_after_action != result.agent_2_choice.competence_after_action
    assert result.agent_1_choice.efficient_terminal_outcomes == result.agent_2_choice.efficient_terminal_outcomes == ((.8,.8),)
    assert result.future_development_value_difference == 0


def test_future_development_value_can_reverse_immediate_preference():
    result = DEVELOPMENT_VALUE_REVERSAL.compare_choices(.75)
    assert isclose(result.immediate_value_difference, -.1, abs_tol=1e-12)
    assert isclose(result.future_development_value_difference, .15, abs_tol=1e-12)
    assert isclose(result.total_value_difference, .05, abs_tol=1e-12)


def test_catalog_references_resolve():
    catalog = load_catalog(ROOT / "registry/catalog.json")
    assert validate_catalog(catalog, ROOT) == []


def test_study_runners_are_end_to_end():
    from studies.static_allocation import run as run_static
    from studies.competence_development import run as run_dynamic
    assert isclose(run_static()["difference"], .4, abs_tol=1e-12)
    dynamic = run_dynamic()
    assert dynamic["efficient_terminal_outcomes_null_under_learning"]["development_value"] == 0
    assert dynamic["development_value_reversal"]["total_difference"] > 0
