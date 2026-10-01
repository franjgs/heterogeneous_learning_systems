import pytest

from hls.g1_static import (
    CANONICAL_G12_SCENARIOS,
    EXACT_TOL,
    G11Model,
    ResourceEffectivenessPoint,
    demand_sweep,
    upper_efficient_hull,
    upper_hull_value,
)


def test_e1_homogeneous_agents_have_zero_gain_over_dense_sweep() -> None:
    model = G11Model(y11=.7, y12=.4, y21=.7, y22=.4)
    assert not model.strict_crossed_advantage
    for evaluation in demand_sweep(model, points=1001):
        assert evaluation.delta_y == pytest.approx(0.0, abs=EXACT_TOL)
        assert evaluation.delta_y_closed_form is None


@pytest.mark.parametrize(
    "model",
    (
        G11Model(y11=.9, y12=.8, y21=.4, y22=.2),
        G11Model(y11=.4, y12=.2, y21=.9, y22=.8),
    ),
)
def test_e2_dominance_has_zero_gain(model: G11Model) -> None:
    assert not model.strict_crossed_advantage
    for evaluation in demand_sweep(model, points=1001):
        assert evaluation.delta_y == pytest.approx(0.0, abs=EXACT_TOL)


def test_e3_symmetric_crossed_specialization_matches_closed_form() -> None:
    model = G11Model(y11=1.0, y12=.2, y21=.2, y22=1.0)
    assert model.strict_crossed_advantage
    assert model.advantage_gaps == pytest.approx((.8, .8))
    assert model.switching_probability() == pytest.approx(.5)
    assert model.maximum_gain() == pytest.approx(.4)
    sweep = demand_sweep(model, points=1001)
    for evaluation in sweep:
        assert evaluation.delta_y == pytest.approx(
            min(.8 * evaluation.p, .8 * (1.0 - evaluation.p)), abs=EXACT_TOL
        )
        assert evaluation.delta_y == pytest.approx(
            evaluation.delta_y_closed_form, abs=EXACT_TOL
        )
    maximum = max(sweep, key=lambda item: item.delta_y)
    assert maximum.p == pytest.approx(.5)
    assert maximum.delta_y == pytest.approx(.4)


def test_e4_asymmetric_crossed_specialization_matches_exact_formula() -> None:
    model = G11Model(y11=.9, y12=.5, y21=.3, y22=.9)
    assert model.advantage_gaps == pytest.approx((.6, .4))
    assert model.switching_probability() == pytest.approx(.4)
    assert model.maximum_gain() == pytest.approx(.24)
    sweep = demand_sweep(model, points=1001)
    assert max(item.delta_y for item in sweep) == pytest.approx(.24)
    for evaluation in sweep:
        assert evaluation.delta_y == pytest.approx(
            evaluation.delta_y_closed_form, abs=EXACT_TOL
        )


def test_e5_boundary_demand_has_zero_gain_under_crossed_specialization() -> None:
    model = G11Model(y11=1.0, y12=.2, y21=.2, y22=1.0)
    assert model.delta_y(0.0) == pytest.approx(0.0, abs=EXACT_TOL)
    assert model.delta_y(1.0) == pytest.approx(0.0, abs=EXACT_TOL)


@pytest.mark.parametrize("p", (0.0, .125, .5, .875, 1.0))
@pytest.mark.parametrize("weight", (0.0, .1, .5, .9, 1.0))
def test_e6_time_sharing_between_one_endpoints_cannot_improve_scalar_value(
    p: float, weight: float
) -> None:
    model = G11Model(y11=1.0, y12=.2, y21=.2, y22=1.0)
    assert model.one_time_sharing_value(p, weight) <= model.y_one(p) + EXACT_TOL


def test_all_policy_values_and_route_identity_are_explicit() -> None:
    model = G11Model(y11=1.0, y12=.2, y21=.2, y22=1.0)
    values = model.policy_values(.25)
    assert values == pytest.approx({"11": .4, "12": 1.0, "21": .2, "22": .8})
    assert model.y_route(.25) == pytest.approx(
        .25 * max(1.0, .2) + .75 * max(.2, 1.0)
    )


@pytest.mark.parametrize("invalid", (-.01, 1.01, float("inf")))
def test_demand_probability_is_bounded(invalid: float) -> None:
    with pytest.raises(ValueError):
        G11Model(1.0, .2, .2, 1.0).evaluate(invalid)


def _points(*pairs: tuple[float, float]) -> tuple[ResourceEffectivenessPoint, ...]:
    return tuple(ResourceEffectivenessPoint(*pair) for pair in pairs)


def _assert_points(
    actual: tuple[ResourceEffectivenessPoint, ...], expected: tuple[ResourceEffectivenessPoint, ...]
) -> None:
    assert len(actual) == len(expected)
    for observed, target in zip(actual, expected):
        assert observed.resource == pytest.approx(target.resource, abs=EXACT_TOL)
        assert observed.effectiveness == pytest.approx(target.effectiveness, abs=EXACT_TOL)


def _assert_intervals(
    actual: tuple[tuple[float, float | None], ...], expected: tuple[tuple[float, float | None], ...]
) -> None:
    assert len(actual) == len(expected)
    for (observed_start, observed_end), (target_start, target_end) in zip(actual, expected):
        assert observed_start == pytest.approx(target_start, abs=EXACT_TOL)
        if target_end is None:
            assert observed_end is None
        else:
            assert observed_end == pytest.approx(target_end, abs=EXACT_TOL)


def test_g12_upper_hull_deduplicates_and_removes_dominated_points() -> None:
    hull = upper_efficient_hull(
        _points((.2, .5), (.2, .5), (.2, .4), (.3, .45), (.4, .7))
    )
    assert hull == _points((.2, .5), (.4, .7))


def test_g12_upper_hull_removes_collinear_middle_vertex() -> None:
    assert upper_efficient_hull(_points((.1, .2), (.2, .4), (.3, .6))) == _points(
        (.1, .2), (.3, .6)
    )


def test_g12_single_point_equal_resource_hull_and_value() -> None:
    hull = upper_efficient_hull(_points((.5, .8), (.5, .8)))
    assert hull == _points((.5, .8))
    assert upper_hull_value(hull, .49) is None
    assert upper_hull_value(hull, .5) == pytest.approx(.8)
    assert upper_hull_value(hull, 2.0) == pytest.approx(.8)


def test_g12_value_interpolation_and_saturation() -> None:
    hull = upper_efficient_hull(_points((.2, .4), (.6, .8), (.8, .9)))
    assert upper_hull_value(hull, .1) is None
    assert upper_hull_value(hull, .4) == pytest.approx(.6)
    assert upper_hull_value(hull, .7) == pytest.approx(.85)
    assert upper_hull_value(hull, 1.0) == pytest.approx(.9)


def test_g12_deterministic_points_and_parallelogram_identity() -> None:
    model = CANONICAL_G12_SCENARIOS["S5_bounded_gain_window"]
    points = model.policy_points(.5)
    _assert_points((points["11"],), _points((.65, .8)))
    _assert_points((points["12"],), _points((.4, .8)))
    _assert_points((points["21"],), _points((.5, .7)))
    _assert_points((points["22"],), _points((.25, .7)))
    assert points["11"].resource + points["22"].resource == pytest.approx(
        points["12"].resource + points["21"].resource
    )
    assert points["11"].effectiveness + points["22"].effectiveness == pytest.approx(
        points["12"].effectiveness + points["21"].effectiveness
    )


@pytest.mark.parametrize("name", tuple(CANONICAL_G12_SCENARIOS))
@pytest.mark.parametrize("p", (0.0, .25, .5, .75, 1.0))
def test_g12_parallelogram_area_matches_closed_form(name: str, p: float) -> None:
    model = CANONICAL_G12_SCENARIOS[name]
    assert model.parallelogram_identity_error(p) <= EXACT_TOL
    assert model.parallelogram_area(p) == pytest.approx(
        model.parallelogram_area_closed_form(p), abs=EXACT_TOL
    )


@pytest.mark.parametrize("name", tuple(CANONICAL_G12_SCENARIOS))
@pytest.mark.parametrize("p", (0.0, .25, .5, .75, 1.0))
def test_g12_organizational_monotonicity_on_common_feasible_domain(
    name: str, p: float
) -> None:
    model = CANONICAL_G12_SCENARIOS[name]
    one = model.one_hull(p)
    route = model.route_hull(p)
    lower = max(one[0].resource, route[0].resource)
    upper = max(one[-1].resource, route[-1].resource)
    for index in range(101):
        evaluation = model.evaluate(p, lower + (upper - lower) * index / 100.0)
        assert evaluation.delta_y is not None
        assert evaluation.delta_y >= -EXACT_TOL


@pytest.mark.parametrize("name", ("S0_homogeneous_null", "S1_pareto_dominance_null"))
def test_g12_s0_s1_have_no_efficient_organizational_gain(name: str) -> None:
    model = CANONICAL_G12_SCENARIOS[name]
    for p in (0.0, .25, .5, .75, 1.0):
        assert model.positive_gain_intervals(p) == ()
        one = model.one_hull(p)
        for budget in (one[0].resource, one[-1].resource, one[-1].resource + 1.0):
            assert model.evaluate(p, budget).delta_y == pytest.approx(0.0, abs=EXACT_TOL)


def test_g12_s2_recovers_g11_and_has_zero_determinant() -> None:
    g12 = CANONICAL_G12_SCENARIOS["S2_g11_embedded_equal_resource"]
    g11 = G11Model(y11=1.0, y12=.2, y21=.2, y22=1.0)
    assert g12.determinant_d == pytest.approx(0.0)
    for p in (0.0, .25, .5, .75, 1.0):
        evaluation = g12.evaluate(p, .5)
        assert evaluation.y_one == pytest.approx(g11.y_one(p))
        assert evaluation.y_route == pytest.approx(g11.y_route(p))
        assert evaluation.delta_y == pytest.approx(g11.delta_y(p))
    at_half = g12.evaluate(.5, .5)
    assert at_half.y_one == pytest.approx(.6)
    assert at_half.y_route == pytest.approx(1.0)
    assert at_half.delta_y == pytest.approx(.4)


def test_g12_s3_bicriterion_hulls_are_constructed_generically() -> None:
    model = CANONICAL_G12_SCENARIOS["S3_bicriterion_tradeoff"]
    _assert_points(model.one_hull(.5), _points((.6, .65)))
    _assert_points(model.route_hull(.5), _points((.4, .35), (.8, .95)))
    assert model.evaluate(.5, .6).delta_y == pytest.approx(0.0)
    assert model.evaluate(.5, .7).delta_y == pytest.approx(.15)
    _assert_intervals(model.positive_gain_intervals(.5), ((.6, None),))


def test_g12_s4_area_expansion_does_not_imply_efficient_gain() -> None:
    model = CANONICAL_G12_SCENARIOS["S4_geometric_expansion_null"]
    assert model.determinant_d == pytest.approx(-.18)
    assert model.parallelogram_area(.5) == pytest.approx(.045)
    assert model.positive_gain_intervals(.5) == ()
    for budget in (.4, .5, .6, .7, 1.0):
        assert model.evaluate(.5, budget).delta_y == pytest.approx(0.0, abs=EXACT_TOL)


def test_g12_s5_exact_hulls_window_and_piecewise_gain() -> None:
    model = CANONICAL_G12_SCENARIOS["S5_bounded_gain_window"]
    _assert_points(model.one_hull(.5), _points((.25, .7), (.65, .8)))
    _assert_points(model.route_hull(.5), _points((.25, .7), (.4, .8)))
    assert model.evaluate(.5, .24).delta_y is None
    assert model.evaluate(.5, .25).delta_y == pytest.approx(0.0)
    for budget in (.3, .35, .4):
        expected = 5.0 / 12.0 * (budget - .25)
        assert model.evaluate(.5, budget).delta_y == pytest.approx(expected)
    for budget in (.45, .55, .65):
        expected = .25 * (.65 - budget)
        assert model.evaluate(.5, budget).delta_y == pytest.approx(expected)
    assert model.evaluate(.5, .8).delta_y == pytest.approx(0.0)
    _assert_intervals(model.positive_gain_intervals(.5), ((.25, .65),))


def test_g12_s5_breakpoint_maximum_agrees_with_dense_sweep() -> None:
    model = CANONICAL_G12_SCENARIOS["S5_bounded_gain_window"]
    exact = model.maximum_gain(.5)
    assert exact is not None
    assert exact.budget == pytest.approx(.4)
    assert exact.delta_y == pytest.approx(.0625)
    dense = [model.evaluate(.5, index / 1000.0) for index in range(701)]
    observed = max(
        (item for item in dense if item.delta_y is not None),
        key=lambda item: item.delta_y,
    )
    assert observed.budget == pytest.approx(exact.budget)
    assert observed.delta_y == pytest.approx(exact.delta_y)
