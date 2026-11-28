import pytest

from studies.soc_triage_hls_availability_robustness.parametric_soctra_capacity import (
    P_VALUES,
    beta22_survival,
    capacity_result,
    confusion,
    equalize_speeds_within_eligibility,
    expand_organization,
    load_scenario,
    need_distribution,
    q0_for_prevalence,
    route_summary,
    utilization_window,
    CONFIG,
)


@pytest.mark.parametrize("prevalence", P_VALUES)
def test_q0_inverts_beta22_tail(prevalence):
    assert beta22_survival(q0_for_prevalence(prevalence)) == pytest.approx(prevalence)


def test_confusion_partition_and_routed_l2_is_not_need_prevalence():
    p = 570 / 156981
    cells = confusion(p, .8421, .045)
    assert sum(cells.values()) == pytest.approx(1)
    summary = route_summary(p, .8421, .045)
    assert summary["l2_fraction"] == pytest.approx(cells["TP"] + cells["FP"])
    assert summary["l2_fraction"] > p
    assert summary["l1_fraction"] + summary["l2_fraction"] == pytest.approx(1)


def test_q_conditional_moments_recompose_beta22_mean():
    for p in P_VALUES:
        d = need_distribution(p)
        assert p * d.mean_q_need + (1 - p) * d.mean_q_ordinary == pytest.approx(.5)
        assert d.mean_q_need > d.q0 > d.mean_q_ordinary


def test_roster_expansion_preserves_profiles_and_unique_ids():
    base = load_scenario(CONFIG).organization
    expanded = expand_organization(base, 12, 4)
    assert len(expanded.resources_for("L1")) == 12
    assert len(expanded.resources_for("L2")) == 4
    ids = [r.analyst.analyst_id for r in expanded.analysts]
    assert len(ids) == len(set(ids))
    source = base.resources_for("L1")[0]
    replica = next(r for r in expanded.resources_for("L1")
                   if r.analyst.analyst_id.endswith("-rep02"))
    assert replica.analyst.eligible_classes == source.analyst.eligible_classes
    assert replica.analyst.competence == source.analyst.competence
    assert replica.service_by_class == source.service_by_class
    assert replica.forecast_service_by_class == source.forecast_service_by_class


def test_lp_capacity_and_speed_control_keep_eligibility():
    scenario = load_scenario(CONFIG)
    org = expand_organization(scenario.organization, 10, 3)
    equalized = equalize_speeds_within_eligibility(org)
    for a, b in zip(org.analysts, equalized.analysts):
        assert a.analyst.eligible_classes == b.analyst.eligible_classes
    mix = scenario.demand_profile["class_mix"]
    actual = capacity_result(org, mix, .05, .8421, .045, 1)
    control = capacity_result(equalized, mix, .05, .8421, .045, 1)
    assert actual["total_stable_arrival_capacity_per_h"] > 0
    assert control["total_stable_arrival_capacity_per_h"] > 0
    assert utilization_window(actual, 10, 3) is not None

