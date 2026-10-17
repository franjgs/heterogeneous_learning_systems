"""Small integration checks for the permanent adaptive-capability record."""

import importlib.util
import json
from pathlib import Path

_RUNNER_PATH = Path(__file__).resolve().parents[1] / "experiments/synthetic/hls_lab_v1/adaptive_capability_validation.py"
_SPEC = importlib.util.spec_from_file_location("hls_adaptive_capability_validation", _RUNNER_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_RUNNER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_RUNNER)
build_validation_evidence = _RUNNER.build_validation_evidence


def _scenario(evidence, scenario_id):
    return next(row for row in evidence["scenarios"] if row["scenario_id"] == scenario_id)


def test_bounded_validation_reuses_existing_scenarios_and_executes_generated_paths():
    evidence = build_validation_evidence()
    assert all(value == "PASS" for value in evidence["capability_checks"].values())

    stationary = _scenario(evidence, "S0_stationary_control")
    assert stationary["environment"]["latent_states"] == ("steady",) * 3
    assert len(stationary["trace"]) == 3
    assert stationary["configuration"]["effort_limits"] == (0.75, 1.0)
    assert stationary["configuration"]["MIS_v2_eta"] == ((0.2, 0.05), (0.08, 0.15))
    assert stationary["trace"][0]["actual_competence_after"] != stationary["trace"][0]["actual_competence_before"]

    shifted = _scenario(evidence, "S1_nonstationary_runner_integration")
    assert shifted["environment"]["latent_states"] == ("old", "old", "new", "new")
    assert [row["problem_id"] for row in shifted["trace"]] == ["old", "old", "new", "new"]
    assert shifted["trace"][0]["allocation"] != shifted["trace"][2]["allocation"]

    markov = _scenario(evidence, "S2_markov_runner_integration")
    assert len(markov["environment"]["latent_states"]) == 20
    assert markov["checks"]["same_seed_exact_replay"] is True
    assert [row["problem_id"] for row in markov["trace"]] == [
        row["problem_id"] for row in markov["environment"]["problems"]
    ]


def test_g2_controls_and_existing_imperfect_adaptive_reference_are_preserved():
    evidence = build_validation_evidence()
    g2 = _scenario(evidence, "S3_G2_competence_development_controls")
    assert g2["checks"] == {
        "D0_has_zero_development_value": True,
        "D1_changes_state_but_has_zero_development_value": True,
        "D2_has_positive_conditional_development_value": True,
    }
    assert g2["scope"].startswith("canonical G2 law")

    adaptive = _scenario(evidence, "S4_existing_adaptive_coordination_reference")
    assert adaptive["configuration"]["information"]["mode"] == "imperfect"
    assert adaptive["checks"]["true_and_estimated_competence_separate"] is True
    assert adaptive["checks"]["MIS_and_teaching_transitions_recorded"] is True
    assert adaptive["checks"]["efficacy_memory_recorded"] is True
    assert any(row["estimated_competence_before"] != row["actual_competence_before"]
               for row in adaptive["trace"])
    assert any(row["efficacy_memory_after"] != row["efficacy_memory_before"]
               for row in adaptive["trace"])

    heterogeneous = evidence["heterogeneous_productivity_diagnostic"]
    assert heterogeneous["status"] == "PASS"
    assert heterogeneous["checks"]["different_agent_limits_respected"] is True
    assert heterogeneous["productivity_before"][0][0] != heterogeneous["productivity_before"][1][1]


def test_validation_record_is_exactly_reproducible_in_memory():
    assert build_validation_evidence() == build_validation_evidence()


def test_machine_readable_registry_points_to_existing_evidence():
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "results/analysis/hls_lab_validation/capability_registry.json").read_text())
    assert registry["campaign_executed"] is False
    for item in registry["capabilities"]:
        assert item["validation_test"]
        assert item["result_artifact"]
        for reference in (*item["implementation"], *item["validation_test"]):
            path = reference.split("::", 1)[0]
            assert (root / path).exists(), reference
        artifacts = item["result_artifact"]
        artifacts = artifacts if isinstance(artifacts, list) else [artifacts]
        for reference in (*artifacts, item["documentation"]):
            path = reference.split("#", 1)[0]
            assert (root / path).exists(), reference
