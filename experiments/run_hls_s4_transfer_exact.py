"""Exact S4 comparison: MIS-v2 alone versus optional transfer."""

from __future__ import annotations

import json
from dataclasses import asdict
from math import isclose, prod
from pathlib import Path
from time import perf_counter

from hls.hls_lab_nk_teaching import TeachingEfficacyNK
from hls.synthetic.hls_s4_transfer_exact import (
    ExactTransferCase,
    _zero_efficacy,
    action_catalogs,
    independent_action_catalogs,
    independent_exhaustive,
    replay_actions,
    result_to_dict,
    solve_bellman,
)
from experiments.run_hls_s4_transfer_opportunities import scenario


RESULT = Path("results/experiments/hls_s4_transfer_exact/results.json")


def make_case() -> ExactTransferCase:
    setup = scenario(0.05)
    x = setup["environment"].emissions["x"].problems[0]
    y = setup["environment"].emissions["y"].problems[0]
    return ExactTransferCase(
        organization=setup["organization"],
        problems=(x, y, y),
        profile=setup["learning"],
        efficacy=setup["efficacy"],
        teaching_parameters=setup["teaching_parameters"],
        teaching_effort=setup["policy_parameters"].effort,
        effort_choices=setup["effort_choices"],
    )


def run() -> dict:
    case = make_case()
    catalogs_a = action_catalogs(case, transfer_available=False)
    catalogs_b = action_catalogs(case, transfer_available=True)
    for transfer, official in ((False, catalogs_a), (True, catalogs_b)):
        rebuilt = independent_action_catalogs(case, transfer_available=transfer)
        for official_period, rebuilt_period in zip(official, rebuilt):
            if set(official_period) != set(rebuilt_period):
                raise AssertionError("independent action construction missed or added a feasible action")
    for actions_a, actions_b in zip(catalogs_a, catalogs_b):
        if not {action for action in actions_a}.issubset(set(actions_b)):
            raise AssertionError("transfer action set must contain every MIS-only action")

    started = perf_counter()
    bellman_a = solve_bellman(case, transfer_available=False)
    bellman_b = solve_bellman(case, transfer_available=True)
    bellman_seconds = perf_counter() - started

    exhaustive_started = perf_counter()
    exhaustive_a, _, _, _ = independent_exhaustive(case, transfer_available=False)
    exhaustive_b, _, best_with_lesson, best_lesson_path = independent_exhaustive(
        case, transfer_available=True,
    )
    exhaustive_seconds = perf_counter() - exhaustive_started
    if not isclose(bellman_a.value, exhaustive_a, rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("MIS-only Bellman differs from independent enumeration")
    if not isclose(bellman_b.value, exhaustive_b, rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("transfer Bellman differs from independent enumeration")
    if bellman_b.value < bellman_a.value - 1e-10:
        raise AssertionError("optional transfer cannot reduce the exact optimum")

    zero = _zero_efficacy(case.efficacy)
    bellman_zero = solve_bellman(case, transfer_available=True, efficacy=zero)
    if not isclose(bellman_zero.value, bellman_a.value,
                   rel_tol=0.0, abs_tol=1e-10):
        raise AssertionError("zero physical transfer must recover the MIS-only optimum")

    result = {
        "experiment": "S4 exact intertemporal reference: MIS-v2 versus optional transfer",
        "design": {
            "agents": case.organization.agent_ids,
            "competencies": case.organization.skill_ids,
            "initial_competence": case.organization.competence_initial,
            "eta": case.profile.eta,
            "demand_sequence": [problem.problem_id for problem in case.problems],
            "requirements": [problem.requirements for problem in case.problems],
            "ces_weights": [problem.ces_weights for problem in case.problems],
            "horizon": len(case.problems),
            "individual_effort_limits": case.organization.effort_limits,
            "collective_budget": case.organization.collective_effort_budget,
            "teaching_effort": case.teaching_effort,
            "transfer_rate": case.teaching_parameters.transfer_rate,
            "efficacy_tensor": case.efficacy.values,
            "production_action_choices": case.effort_choices,
            "action_counts_by_period": {
                "A_mis_only": [len(actions) for actions in catalogs_a],
                "B_transfer_optional": [len(actions) for actions in catalogs_b],
            },
            "demand_information": "deterministic full sequence known to exact reference",
            "competence_information": "exact reference observes true state; deterministic physical model",
            "reward": "existing CES collective production reward before learning and teaching transitions",
            "physical_laws": "existing MIS-v2 then optional teaching transition; no equations modified",
        },
        "verification": {
            "independent_action_catalogs_match_existing_catalog": True,
            "A_actions_subset_of_B_each_period": True,
            "bellman_equals_independent_exhaustive_A": True,
            "bellman_equals_independent_exhaustive_B": True,
            "zero_efficacy_B_equals_A": True,
            "B_optimum_not_below_A": True,
            "independent_path_values": {"A": exhaustive_a, "B": exhaustive_b},
            "best_sequence_with_at_least_one_lesson": {
                "value": best_with_lesson,
                "gap_to_exact_A": (None if best_with_lesson is None
                                   else best_with_lesson - bellman_a.value),
                "actions": [asdict(action) for action in best_lesson_path],
                "periods": [asdict(row) for row in replay_actions(case, best_lesson_path)],
            },
            "zero_efficacy_B_value": bellman_zero.value,
        },
        "runtime_seconds_descriptive": {
            "bellman_both_conditions": bellman_seconds,
            "independent_exhaustive_both_conditions": exhaustive_seconds,
        },
        "A": result_to_dict(bellman_a),
        "B": result_to_dict(bellman_b),
        "transfer_value": bellman_b.value - bellman_a.value,
        "independent_enumerated_paths_upper_bound": {
            "A": prod(len(actions) for actions in catalogs_a),
            "B": prod(len(actions) for actions in catalogs_b),
        },
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    output = run()
    print(json.dumps({
        "J_A": output["A"]["value"],
        "J_B": output["B"]["value"],
        "delta": output["transfer_value"],
        "best_with_lesson": output["verification"]["best_sequence_with_at_least_one_lesson"]["value"],
        "gap_best_with_lesson_to_A": output["verification"]["best_sequence_with_at_least_one_lesson"]["gap_to_exact_A"],
        "actions_A": output["design"]["action_counts_by_period"]["A_mis_only"],
        "actions_B": output["design"]["action_counts_by_period"]["B_transfer_optional"],
        "runtime": output["runtime_seconds_descriptive"],
    }, indent=2))
