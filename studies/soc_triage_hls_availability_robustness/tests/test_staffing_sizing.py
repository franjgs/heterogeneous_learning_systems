import json
from pathlib import Path

from studies.soc_triage_hls_availability_robustness.run_staffing_sizing import (
    build_organization, trace_sha256,
)
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario


ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "config"


def test_staffing_profiles_preserve_class_coverage_and_original_analyst_parameters():
    study = json.loads((CONFIG / "SOC_NEW_MODEL_STAFFING_SIZING.json").read_text())
    base = load_scenario(CONFIG / "SOC_NEW_MODEL_CONOPS_REFERENCE.json")
    source = {r.analyst.analyst_id: r for r in base.organization.analysts}
    classes = set(base.demand_profile["class_mix"])

    for config in study["configurations"]:
        l1 = study["roster_profiles"][config["l1_profile"]]["analyst_ids"]
        l2 = study["roster_profiles"][config["l2_profile"]]["analyst_ids"]
        organization = build_organization(base, l1, l2)
        assert set().union(*(set(r.analyst.eligible_classes)
                             for r in organization.resources_for("L1"))) == classes
        assert set().union(*(set(r.analyst.eligible_classes)
                             for r in organization.resources_for("L2"))) == classes
        for resource in organization.analysts:
            original = source[resource.analyst.analyst_id]
            assert resource.analyst == original.analyst
            assert resource.service_by_class == original.service_by_class
            assert resource.forecast_service_by_class == original.forecast_service_by_class
            assert resource.calendar == original.calendar


def test_staffing_seed_block_is_unique_and_trace_generation_is_roster_independent():
    study = json.loads((CONFIG / "SOC_NEW_MODEL_STAFFING_SIZING.json").read_text())
    seeds = study["seed_block"]["seeds"]
    assert len(seeds) == len(set(seeds)) == 12
    base = load_scenario(CONFIG / "SOC_NEW_MODEL_CONOPS_REFERENCE.json")
    trace_a = base.generate_trace(seeds[0])
    trace_b = base.generate_trace(seeds[0])
    assert trace_a == trace_b
    assert trace_sha256(trace_a) == trace_sha256(trace_b)
