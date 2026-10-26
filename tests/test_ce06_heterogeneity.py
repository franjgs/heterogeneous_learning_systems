import numpy as np

from hls.ce04 import RunConfig, generate_workload, run_replica
from hls.ce06_heterogeneity import diagnose_replica, gini


def test_gini_boundaries_and_known_values():
    assert gini([0, 0, 0]) == 0
    assert gini([1, 1, 1, 1]) == 0
    assert np.isclose(gini([0, 0, 2]), 2/3)


def test_diagnostics_preserve_mean_and_compute_selected_competence():
    config = RunConfig(seed=7, n_agents=12, composition="H2", policy="P1", horizon=2.0)
    tasks = generate_workload(7, 12, horizon=2.0)
    result = run_replica(config, tasks)
    summary, cells = diagnose_replica(result["config"], result["records"],
        end_time=result["simulation_drain_end"], assignment_counts=result["assignment_counts"],
        agent_service_time=result["agent_service_time"])
    assert np.isclose(summary["q_mean_min"], .775, rtol=0, atol=1e-12)
    assert np.isclose(summary["q_mean_max"], .775, rtol=0, atol=1e-12)
    assert 0 <= summary["assignment_gini"] <= 1
    assert summary["admitted"] + summary["rejected"] == summary["arrivals"]
    assert len(cells) <= 12
    assert summary["gap_to_family_max_mean"] is None or summary["gap_to_family_max_mean"] >= 0


def test_p1_reproducible_on_same_scenario_and_metrics_consistent():
    config = RunConfig(seed=19, n_agents=12, composition="H1", policy="P1", horizon=3.0)
    tasks = generate_workload(19, 12, horizon=3.0)
    first = run_replica(config, tasks)
    second = run_replica(config, tasks)
    assert first["records"] == second["records"]
    assert first["assignment_counts"] == second["assignment_counts"]
    assert first["n_arrivals"] == first["n_admitted"] + first["n_rejected"]
    assert first["n_success_on_time"] <= first["n_admitted"]
