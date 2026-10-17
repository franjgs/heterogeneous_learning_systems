"""Replay and arithmetic controls for the Phase 5A diagnostic trace."""

from experiments.synthetic.hls_lab_v1.scientific_model_reference import (
    REFERENCE_SOURCE_COMMIT,
    build_reference_evidence,
)


def test_reference_episode_replays_exactly_and_exercises_declared_mechanisms():
    first = build_reference_evidence()
    second = build_reference_evidence()
    assert first == second
    assert first["software_commit"] == REFERENCE_SOURCE_COMMIT
    assert first["purpose"] == "diagnostic_reference_trace_not_campaign_data"
    assert first["environment_trajectory"]["latent_states"] == ("x", "y", "x", "y")

    execution = first["execution"]
    assert execution["information_mode"] == "imperfect"
    assert len(execution["records"]) == 4
    assert execution["final_policy_memory"]["efficacy"]
    for row in execution["records"]:
        production = row["production"]
        assert row["action"]["teaching"] is not None
        assert row["teaching_observation"] is not None
        assert any(any(value > 0 for value in skill_row)
                   for skill_row in row["mis_increment"])
        assert any(any(value > 0 for value in skill_row)
                   for skill_row in row["teaching_increment"])
        assert production["outputs"] == tuple(
            sum(row["action"]["production"][i][k]
                * row["competence_actual_before"][i][k]
                for i in range(2))
            for k in range(2)
        )
        assert row["total_resource_used"] == (
            row["productive_effort_used"] + row["teaching_resource_used"]
        )
        assert row["teaching_resource_used"] == 0.5
