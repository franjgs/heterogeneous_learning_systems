import importlib.util
import itertools
import json
import runpy
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
EXP_DIR = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "foundations" / "b12_4_effective_coupling"
write_result_bundle = runpy.run_path(
    str(ROOT / "experiments" / "foundations" / "_provenance.py")
)["write_result_bundle"]

B12_1_PATH = (
    ROOT / "experiments" / "foundations"
    / "b12_1_closed_feedback" / "run.py"
)

spec = importlib.util.spec_from_file_location("b12_1", B12_1_PATH)
b12_1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b12_1)


def simulate_with_initial_intervention(
    p,
    z_initial,
    beta,
    eta,
    periods,
    initial_choice,
):
    z = np.asarray(z_initial, dtype=float)
    beta = np.asarray(beta, dtype=float)
    eta = np.asarray(eta, dtype=float)

    history = []

    for t in range(periods):
        z_before = z.copy()

        natural_choice, natural_allocation, scores = b12_1.routing(
            p, z_before
        )

        if t == 0:
            choice = int(initial_choice)
            allocation = np.zeros(len(z), dtype=float)
            allocation[choice] = 1.0
        else:
            choice = natural_choice
            allocation = natural_allocation

        z_after = b12_1.learning_step(
            z_before,
            allocation,
            beta,
            eta,
        )

        history.append({
            "period": t + 1,
            "natural_choice": int(natural_choice),
            "choice": int(choice),
            "allocation": allocation.tolist(),
            "z_before": z_before.tolist(),
            "z_after": z_after.tolist(),
            "scores": scores.tolist(),
        })

        z = z_after

    return history


def decisions_after_intervention(history):
    return tuple(row["choice"] for row in history[1:])


def evaluate_case(p, z_initial, beta_value, eta_value, periods, tol):
    beta = np.full(2, beta_value, dtype=float)
    eta = np.full(2, eta_value, dtype=float)

    h0 = simulate_with_initial_intervention(
        p, z_initial, beta, eta, periods, 0
    )
    h1 = simulate_with_initial_intervention(
        p, z_initial, beta, eta, periods, 1
    )

    state_changed = not np.allclose(
        h0[0]["z_after"],
        h1[0]["z_after"],
        atol=tol,
        rtol=0.0,
    )

    future_decisions_changed = (
        decisions_after_intervention(h0)
        != decisions_after_intervention(h1)
    )
    future_score_margins = [
        abs(row["scores"][0] - row["scores"][1])
        for history in (h0, h1)
        for row in history[1:]
    ]
    minimum_future_score_margin = min(future_score_margins)
    future_routing_tie = minimum_future_score_margin <= tol

    initial_intervention_only_difference = (
        np.allclose(h0[0]["z_before"], h1[0]["z_before"], atol=tol)
        and np.allclose(h0[0]["scores"], h1[0]["scores"], atol=tol)
        and h0[0]["natural_choice"] == h1[0]["natural_choice"]
        and h0[0]["allocation"] != h1[0]["allocation"]
    )
    shared_rule_after_intervention = all(
        row["choice"] == row["natural_choice"]
        for history in (h0, h1)
        for row in history[1:]
    )

    coupled = (
        initial_intervention_only_difference
        and shared_rule_after_intervention
        and state_changed
        and future_decisions_changed
    )

    # Decoupled control: identical intervention, but eta = 0.
    eta_zero = np.zeros(2, dtype=float)

    c0 = simulate_with_initial_intervention(
        p, z_initial, beta, eta_zero, periods, 0
    )
    c1 = simulate_with_initial_intervention(
        p, z_initial, beta, eta_zero, periods, 1
    )

    control_state_changed = not np.allclose(
        c0[0]["z_after"],
        c1[0]["z_after"],
        atol=tol,
        rtol=0.0,
    )

    control_future_decisions_changed = (
        decisions_after_intervention(c0)
        != decisions_after_intervention(c1)
    )

    return {
        "p": list(p),
        "z_initial": list(z_initial),
        "beta": beta_value,
        "eta": eta_value,
        "state_changed": state_changed,
        "future_decisions_changed": future_decisions_changed,
        "minimum_future_score_margin": minimum_future_score_margin,
        "future_routing_tie": future_routing_tie,
        "initial_intervention_only_difference": (
            initial_intervention_only_difference
        ),
        "shared_rule_after_intervention": shared_rule_after_intervention,
        "effective_coupling": coupled,
        "choices_if_initial_0": [r["choice"] for r in h0],
        "choices_if_initial_1": [r["choice"] for r in h1],
        "control_state_changed": control_state_changed,
        "control_future_decisions_changed":
            control_future_decisions_changed,
    }


def sweep(config):
    cases = []

    for p, z0, beta, eta in itertools.product(
        config["problem_probability_grid"],
        config["z_initial_grid"],
        config["beta_grid"],
        config["eta_grid"],
    ):
        cases.append(
            evaluate_case(
                p,
                z0,
                beta,
                eta,
                int(config["periods"]),
                float(config["tolerance"]),
            )
        )

    return cases


def main():
    config = json.loads(
        (EXP_DIR / "config.json").read_text()
    )

    cases = sweep(config)

    coupled = [c for c in cases if c["effective_coupling"]]

    controls_with_effect = [
        c for c in cases
        if c["control_state_changed"]
        or c["control_future_decisions_changed"]
    ]
    coupled_with_future_routing_ties = [
        c for c in coupled if c["future_routing_tie"]
    ]
    minimum_coupled_future_score_margin = min(
        (
            c["minimum_future_score_margin"]
            for c in coupled
        ),
        default=None,
    )

    intervention_design_verified = all(
        case["initial_intervention_only_difference"]
        and case["shared_rule_after_intervention"]
        for case in cases
    )
    expected_counts_verified = (
        len(cases) == config["expected_total_parameter_cases"]
        and len(coupled) == config["expected_effective_coupling_cases"]
        and len(controls_with_effect)
        == config["expected_decoupled_control_effect_cases"]
        and len(coupled_with_future_routing_ties)
        == config["expected_coupled_cases_with_future_routing_ties"]
    )
    supported = (
        intervention_design_verified
        and expected_counts_verified
        and len(coupled) > 1
        and len(controls_with_effect) == 0
    )

    output = {
        "experiment_id": "B12.4",
        "kind": "hls_translation",
        "source_citekeys": config["source_citekeys"],
        "total_parameter_cases": len(cases),
        "effective_coupling_cases": len(coupled),
        "effective_coupling_fraction": len(coupled) / len(cases),
        "decoupled_control_effect_cases": len(controls_with_effect),
        "coupled_cases_with_future_routing_ties": len(
            coupled_with_future_routing_ties
        ),
        "minimum_coupled_future_score_margin": (
            minimum_coupled_future_score_margin
        ),
        "nondegenerate_region_found": len(coupled) > 1,
        "control_verified": len(controls_with_effect) == 0,
        "intervention_design_verified": intervention_design_verified,
        "expected_counts_verified": expected_counts_verified,
        "status": "SUPPORTED" if supported else "NOT_SUPPORTED",
        "coupled_examples": coupled[:10],
        "cases": cases,
    }

    write_result_bundle(
        root=ROOT,
        experiment_dir=EXP_DIR,
        result_dir=RESULT_DIR,
        run_file=Path(__file__).resolve(),
        output=output,
    )

    print(json.dumps(output, indent=2))

    if not supported:
        raise SystemExit("B12.4 FAILED")


if __name__ == "__main__":
    main()
