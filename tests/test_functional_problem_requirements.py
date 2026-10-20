import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiments.synthetic.campaign0_discriminative_capacity.run import (  # noqa: E402
    ETA, HISTORIES, TEAMS,
)
from hls.discover_develop_v0 import DISCOVER_DEVELOP  # noqa: E402
from hls.discover_v0 import production_inputs  # noqa: E402
from hls.finite_problem_belief import run_finite_problem_sequence  # noqa: E402
from hls.functional_problem import (  # noqa: E402
    REFERENCE_REQUIREMENTS, REFERENCE_TEAM, assigned_effort, evaluate_requirements,
    observe_trajectory_requirements,
)
from hls.small_problem_world import (  # noqa: E402
    HYPOTHESIS_REPERTOIRE, UNIFORM_PRIOR, REQUIREMENT_LEVEL, WORLD,
    requirements_for_problem,
)


def test_reference_rule_is_maximum_jointly_balanced_output_and_comparable():
    assert REFERENCE_REQUIREMENTS == pytest.approx((0.75, 0.75), abs=1e-15)
    assert production_inputs(REFERENCE_TEAM, ((0.5, 0.5),) * 3) == REFERENCE_REQUIREMENTS
    # Every frozen Campaign-0 team has the same column totals and can meet the
    # same threshold with the same admissible balanced action.
    action = ((0.5, 0.5),) * 3
    for team in TEAMS.values():
        assert production_inputs(team, action) == REFERENCE_REQUIREMENTS


def test_functional_pass_fail_deficits_and_monotonicity():
    requirements = REFERENCE_REQUIREMENTS
    assert evaluate_requirements(requirements, requirements).met
    assert evaluate_requirements(requirements, requirements).deficits == (0.0, 0.0)
    assert evaluate_requirements((0.0, 0.0), requirements).normalized_total_deficit == 1.0
    low = evaluate_requirements((0.5, 0.7), requirements)
    high = evaluate_requirements((0.6, 0.8), requirements)
    assert high.normalized_total_deficit <= low.normalized_total_deficit
    assert int(high.met) >= int(low.met)
    assert not evaluate_requirements((0.0, 0.0), requirements).met


def test_weights_are_not_requirement_inputs_and_effort_is_separate():
    result = evaluate_requirements((0.5, 1.0), REFERENCE_REQUIREMENTS)
    assert result.met is False
    assert result.deficits == pytest.approx((0.25, 0.0))
    assert assigned_effort(((0.0, 1.0), (0.0, 1.0), (1.0, 0.0))) == 3.0


def test_observer_does_not_change_frozen_campaign0_trajectory():
    plain = run_finite_problem_sequence(
        TEAMS["G00"], HISTORIES["H0"], HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=3, seed=0,
    )
    observed = run_finite_problem_sequence(
        TEAMS["G00"], HISTORIES["H0"], HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=3, seed=0,
    )
    annotations = observe_trajectory_requirements(
        observed, {problem: REFERENCE_REQUIREMENTS for problem in set(HISTORIES["H0"])}
    )
    assert len(plain) == len(observed) == 18
    for before, after, annotation in zip(plain, observed, annotations):
        assert (before.action, before.state_before, before.state_after,
                before.belief_before, before.belief_after, before.true_mean,
                before.observed_reward, before.cumulative_reward) == (
                    after.action, after.state_before, after.state_after,
                    after.belief_before, after.belief_after, after.true_mean,
                    after.observed_reward, after.cumulative_reward,
                )
        assert annotation.outputs == production_inputs(after.state_before, after.action)
        assert annotation.requirements == REFERENCE_REQUIREMENTS
        assert annotation.evaluation is not None
        assert annotation.effort == assigned_effort(after.action)


def test_single_historical_reference_replays_and_adds_functional_records():
    result_dir = ROOT / "results/diagnostics/campaign0_discriminative_capacity"
    with (result_dir / "runs.csv").open(newline="", encoding="utf-8") as handle:
        frozen_run = next(row for row in csv.DictReader(handle)
                          if row["history"] == "H0" and row["team"] == "G00" and row["seed"] == "0")
    with (result_dir / "trajectories.csv").open(newline="", encoding="utf-8") as handle:
        frozen_rows = [row for row in csv.DictReader(handle)
                       if row["history"] == "H0" and row["team"] == "G00" and row["seed"] == "0"]
    replay = run_finite_problem_sequence(
        TEAMS["G00"], HISTORIES["H0"], HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=3, seed=0,
    )
    annotations = observe_trajectory_requirements(
        replay, {problem: REFERENCE_REQUIREMENTS for problem in set(HISTORIES["H0"])}
    )
    assert len(replay) == len(frozen_rows) == 18
    for step, row, annotation in zip(replay, frozen_rows, annotations):
        assert step.true_problem == tuple(json.loads(row["true_problem"]))
        assert [list(pair) for pair in step.action] == json.loads(row["action"])
        expected_state = json.loads(row["S_after"])
        assert [value for pair in step.state_after for value in pair] == pytest.approx(
            [value for pair in expected_state for value in pair], abs=1e-12
        )
        assert step.belief_after == pytest.approx(json.loads(row["belief_after"]))
        assert step.true_mean == pytest.approx(float(row["mu_true"]), abs=1e-12)
        assert step.observed_reward == pytest.approx(float(row["observed_reward"]), abs=1e-12)
        assert annotation.evaluation is not None
    assert replay[-1].cumulative_reward == pytest.approx(
        float(frozen_run["cumulative_performance"]), abs=1e-12
    )


def test_differentiated_world_requirements_and_recurrence():
    expected = {
        "A": (1.0, 0.25),
        "A_prime": (0.875, 0.375),
        "B": (0.375, 0.875),
        "B_prime": (0.25, 1.0),
        "C": (0.625, 0.625),
    }
    assert REQUIREMENT_LEVEL == pytest.approx(1.25)
    by_label = {stage.label: stage.requirements for stage in WORLD[:5]}
    for label, requirements in expected.items():
        world_label = "A'" if label == "A_prime" else "B'" if label == "B_prime" else label
        assert by_label[world_label] == pytest.approx(requirements)
    assert WORLD[5].requirements == WORLD[0].requirements
    assert len(set(stage.requirements for stage in WORLD[:5])) == 5


def test_all_requirements_are_identical_across_teams_and_factibility_is_explicit():
    from hls.discover_v0 import JOINT_ACTIONS

    expected_counts = {
        "G00": (9, 6, 6, 9, 7),
        "G04": (4, 9, 7, 5, 11),
        "G05": (14, 12, 12, 14, 9),
        "G07": (12, 10, 11, 14, 8),
    }
    problem_types = tuple(stage.problem for stage in WORLD[:5])
    for team_id, team in TEAMS.items():
        counts = []
        for problem in problem_types:
            requirements = requirements_for_problem(problem)
            outputs = [production_inputs(team, action) for action in JOINT_ACTIONS]
            satisfying = [all(y[k] + 1e-12 >= requirements[k] for k in range(2)) for y in outputs]
            counts.append(sum(satisfying))
            assert any(satisfying)
        assert tuple(counts) == expected_counts[team_id]


def test_problem_specific_observer_is_trajectory_invariant_and_repeats_requirements():
    problems = tuple(stage.problem for stage in WORLD)
    requirement_map = {stage.problem: stage.requirements for stage in WORLD[:5]}
    plain = run_finite_problem_sequence(
        TEAMS["G00"], problems, HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=3, seed=0,
    )
    observed = run_finite_problem_sequence(
        TEAMS["G00"], problems, HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=3, seed=0,
    )
    annotations = observe_trajectory_requirements(observed, requirement_map)
    integrated = run_finite_problem_sequence(
        TEAMS["G00"], problems, HYPOTHESIS_REPERTOIRE,
        prior=UNIFORM_PRIOR, mode=DISCOVER_DEVELOP, eta=ETA,
        horizon=3, seed=0, requirements_by_problem=requirement_map,
    )
    for before, after, annotation, recorded in zip(plain, observed, annotations, integrated):
        assert (before.action, before.state_after, before.belief_after,
                before.true_mean, before.observed_reward, before.cumulative_reward) == (
                    after.action, after.state_after, after.belief_after,
                    after.true_mean, after.observed_reward, after.cumulative_reward,
                )
        assert annotation.requirements == requirement_map[after.true_problem]
        assert (recorded.action, recorded.state_after, recorded.belief_after,
                recorded.true_mean, recorded.observed_reward, recorded.cumulative_reward) == (
                    before.action, before.state_after, before.belief_after,
                    before.true_mean, before.observed_reward, before.cumulative_reward,
                )
        assert recorded.functional_requirements == requirement_map[recorded.true_problem]
        assert recorded.functional_outputs == production_inputs(recorded.state_before, recorded.action)
        assert recorded.functional_evaluation == annotation.evaluation
        assert recorded.assigned_effort == assigned_effort(recorded.action)
