import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESULT_DIR = ROOT / "results/foundations/b13_joint_value"
TOL = 1e-12


def F(z):
    if not 0.0 <= z <= 1.0:
        raise ValueError(f"Argument outside [0,1]: {z}")
    return 2.0 * z - z * z


def solver_knowledge_length(C, H, structure):
    if structure == "non_overlapping":
        return H - C
    if structure == "nested":
        return H
    raise ValueError(f"Unknown knowledge structure: {structure}")


def autarky_reward(C, c):
    return F(C) - c * C


def hierarchy_reward(C, H, c, h, structure):
    Ls = solver_knowledge_length(C, H, structure)
    return F(H) - c * C - c * h * (1.0 - F(C)) * Ls


def garicano_DG(C, H, c, h, structure):
    RA = autarky_reward(C, c)
    RB = hierarchy_reward(C, H, c, h, structure)
    return RA - RB, RA, RB


def future_states(S, beta, eta):
    SA = S - beta
    SB = S - beta + eta
    if not (0.0 <= SA <= 1.0 and 0.0 <= SB <= 1.0):
        return None
    return SA, SB


def evaluate(structure, C, H, c, h, S, beta, eta):

    states = future_states(S, beta, eta)
    if states is None:
        return None

    SA, SB = states

    DG, RA, RB = garicano_DG(
        C, H, c, h, structure
    )

    # Operationally admissible region.
    if RA < -TOL or RB < -TOL:
        return None

    Ls = solver_knowledge_length(C, H, structure)

    DG_formula = (
        c * h * (1.0 - F(C)) * Ls
        - (F(H) - F(C))
    )

    GG = F(SB) - F(SA)

    GG_closed = (
        eta *
        (2.0 - 2.0 * (S - beta) - eta)
    )

    JA = RA + F(SA)
    JB = RB + F(SB)

    delta_J = GG - DG
    direct_delta_J = JB - JA

    if DG > TOL:
        present_region = "AUTARKY_BETTER_NOW"
    elif DG < -TOL:
        present_region = "HIERARCHY_BETTER_NOW"
    else:
        present_region = "PRESENT_BOUNDARY"

    if delta_J > TOL:
        cumulative_region = "HIERARCHY_BETTER_CUMULATIVE"
    elif delta_J < -TOL:
        cumulative_region = "AUTARKY_BETTER_CUMULATIVE"
    else:
        cumulative_region = "CUMULATIVE_BOUNDARY"

    reversal = (
        DG > TOL
        and delta_J > TOL
    )

    learning_insufficient = (
        eta > TOL
        and DG > TOL
        and delta_J < -TOL
    )

    return {
        "knowledge_structure": structure,
        "C": C,
        "H": H,
        "c": c,
        "h": h,
        "S": S,
        "beta": beta,
        "eta": eta,

        "RA": RA,
        "RB": RB,

        "DG": DG,
        "DG_formula": DG_formula,
        "DG_error": abs(DG - DG_formula),

        "SA": SA,
        "SB": SB,

        "GG": GG,
        "GG_closed": GG_closed,
        "GG_error": abs(GG - GG_closed),

        "JA": JA,
        "JB": JB,

        "delta_J": delta_J,
        "direct_delta_J": direct_delta_J,
        "identity_error": abs(delta_J - direct_delta_J),

        "present_region": present_region,
        "cumulative_region": cumulative_region,

        "reversal": reversal,
        "learning_insufficient": learning_insufficient,
    }


def run_structure(structure):

    C_values = [0.1, 0.3, 0.5, 0.7]
    H_values = [0.4, 0.6, 0.8, 0.9]
    c_values = [0.5, 1.0, 2.0, 4.0]
    h_values = [0.1, 0.25, 0.5, 0.8]

    S_values = [0.2, 0.4, 0.6, 0.8]
    beta_values = [0.0, 0.1, 0.2]

    eta_values = [
        0.0,
        0.01,
        0.025,
        0.05,
        0.1,
        0.3,
        0.5,
    ]

    cases = []

    candidate_cases = 0
    excluded_invalid_CH = 0
    excluded_future_state = 0
    excluded_negative_reward = 0

    for C, H, c, h, S, beta, eta in itertools.product(
        C_values,
        H_values,
        c_values,
        h_values,
        S_values,
        beta_values,
        eta_values,
    ):
        candidate_cases += 1

        if not (0.0 <= C < H <= 1.0):
            excluded_invalid_CH += 1
            continue

        if future_states(S, beta, eta) is None:
            excluded_future_state += 1
            continue

        DG, RA, RB = garicano_DG(
            C, H, c, h, structure
        )

        if RA < -TOL or RB < -TOL:
            excluded_negative_reward += 1
            continue

        case = evaluate(
            structure,
            C,
            H,
            c,
            h,
            S,
            beta,
            eta,
        )

        if case is not None:
            cases.append(case)

    max_DG_error = max(
        (x["DG_error"] for x in cases),
        default=0.0,
    )

    max_GG_error = max(
        (x["GG_error"] for x in cases),
        default=0.0,
    )

    max_identity_error = max(
        (x["identity_error"] for x in cases),
        default=0.0,
    )

    present_counts = {
        name: sum(
            x["present_region"] == name
            for x in cases
        )
        for name in [
            "AUTARKY_BETTER_NOW",
            "HIERARCHY_BETTER_NOW",
            "PRESENT_BOUNDARY",
        ]
    }

    cumulative_counts = {
        name: sum(
            x["cumulative_region"] == name
            for x in cases
        )
        for name in [
            "HIERARCHY_BETTER_CUMULATIVE",
            "AUTARKY_BETTER_CUMULATIVE",
            "CUMULATIVE_BOUNDARY",
        ]
    }

    reversal_cases = [
        x for x in cases
        if x["reversal"]
    ]

    insufficient_cases = [
        x for x in cases
        if x["learning_insufficient"]
    ]

    no_learning_cases = [
        x for x in cases
        if x["eta"] == 0.0
    ]

    numerical_checks = (
        max_DG_error <= TOL
        and max_GG_error <= TOL
        and max_identity_error <= TOL
    )

    admissibility_check = all(
        x["RA"] >= -TOL and x["RB"] >= -TOL
        for x in cases
    )

    no_learning_check = all(
        abs(x["GG"]) <= TOL
        and not x["reversal"]
        for x in no_learning_cases
    )

    # --------------------------------------------------------
    # Structure-specific scientific result
    # --------------------------------------------------------

    if structure == "non_overlapping":

        # Analytical prediction under the present assumptions:
        #
        # RA >= 0  => c <= 2-C.
        #
        # With h <= 1:
        #
        # c*h*(1-C)^2 <= (2-C)(1-C)^2
        #               < 2-H-C
        #
        # for 0<C<H<=1.
        #
        # Therefore DG < 0.
        #
        # Hence an admissible case in which autarky is better
        # now cannot exist, and reversal is impossible.

        structural_prediction = (
            "Under RA>=0, 0<C<H<=1 and h<=1, "
            "DG<0; hierarchy is always operationally better."
        )

        structural_check = (
            present_counts["AUTARKY_BETTER_NOW"] == 0
            and len(reversal_cases) == 0
        )

        scientific_result = (
            "NO_ADMISSIBLE_PRESENT_SACRIFICE"
        )

    elif structure == "nested":

        # Here DG>0 is admissible.
        # We require both sides of the learning threshold:
        #
        # 1. hierarchy worse now but better cumulatively;
        # 2. positive learning but insufficient to compensate
        #    the present sacrifice.

        structural_prediction = (
            "Admissible DG>0 cases exist; depending on eta, "
            "learning can either compensate or fail to "
            "compensate the present hierarchy disadvantage."
        )

        structural_check = (
            present_counts["AUTARKY_BETTER_NOW"] > 0
            and len(reversal_cases) > 0
            and len(insufficient_cases) > 0
        )

        scientific_result = (
            "REVERSAL_AND_THRESHOLD_EXPECTED"
        )

    else:
        raise ValueError(structure)

    passed = (
        len(cases) > 0
        and numerical_checks
        and admissibility_check
        and no_learning_check
        and structural_check
    )

    return {
        "knowledge_structure": structure,

        "scientific_result":
            scientific_result,

        "structural_prediction":
            structural_prediction,

        "candidate_cases":
            candidate_cases,

        "tested_cases":
            len(cases),

        "excluded_invalid_CH":
            excluded_invalid_CH,

        "excluded_future_state":
            excluded_future_state,

        "excluded_negative_reward":
            excluded_negative_reward,

        "present_region_counts":
            present_counts,

        "cumulative_region_counts":
            cumulative_counts,

        "reversal_count":
            len(reversal_cases),

        "learning_insufficient_count":
            len(insufficient_cases),

        "reversal_found":
            len(reversal_cases) > 0,

        "learning_insufficient_found":
            len(insufficient_cases) > 0,

        "max_DG_error":
            max_DG_error,

        "max_GG_error":
            max_GG_error,

        "max_identity_error":
            max_identity_error,

        "numerical_checks_passed":
            numerical_checks,

        "admissibility_check_passed":
            admissibility_check,

        "no_learning_control_passed":
            no_learning_check,

        "structural_prediction_passed":
            structural_check,

        "reversal_examples":
            reversal_cases[:3],

        "learning_insufficient_examples":
            insufficient_cases[:3],

        "passed":
            passed,
    }


def main():

    structures = [
        "non_overlapping",
        "nested",
    ]

    results = {
        structure: run_structure(structure)
        for structure in structures
    }

    overall_passed = all(
        x["passed"]
        for x in results.values()
    )

    output = {
        "experiment_id": "B13",

        "status": (
            "SUPPORTED"
            if overall_passed
            else "FAILED"
        ),

        "admissibility": {
            "present_rewards":
                "RA >= 0 and RB >= 0",

            "future_states":
                "0 <= S-beta <= S-beta+eta <= 1",

            "knowledge":
                "0 <= C < H <= 1",

            "communication_time":
                "0 <= h <= 1",
        },

        "model": {
            "distribution":
                "F(z)=2z-z^2",

            "garicano_DG":
                "c*h*(1-F(C))*Ls - (F(H)-F(C))",

            "Ls_non_overlapping":
                "H-C",

            "Ls_nested":
                "H",

            "gutjahr_GG":
                "eta*[2-2*(S-beta)-eta]",

            "joint_difference":
                "DeltaJ = GG-DG",
        },

        "interpretation": {
            "non_overlapping":
                "No admissible reversal is predicted under "
                "the current assumptions because DG<0 whenever "
                "RA>=0.",

            "nested":
                "Admissible DG>0 cases exist. The sign of "
                "DeltaJ depends on whether future competence "
                "gain GG exceeds present sacrifice DG.",
        },

        "structures": results,

        "passed": overall_passed,
    }

    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = RESULT_DIR / "metrics.json"

    output_file.write_text(
        json.dumps(
            output,
            indent=2,
        )
    )

    print(
        json.dumps(
            output,
            indent=2,
        )
    )

    if not overall_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
