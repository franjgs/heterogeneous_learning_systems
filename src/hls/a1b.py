"""Deterministic implementation of the pre-registered A1b phase sweep."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Iterable, Mapping

from .a1a import (
    A1aWorld,
    DevelopmentAction,
    Learner,
    PolicySolution,
    StrongSEPSolution,
    reference_worlds,
    solve_hls,
    solve_sep_omega,
    solve_strong_sep,
)


TOL = 1e-12
PHASE_1 = "A1b.1"
PHASE_2 = "A1b.2"
PHASE_3 = "A1b.3"
EXPECTED_COUNTS = {PHASE_1: 28, PHASE_2: 546, PHASE_3: 446}

LESS = "LESS"
BOUNDARY = "BOUNDARY"
GREATER = "GREATER"
NEGATIVE_UNEXPECTED = "NEGATIVE_UNEXPECTED"
NO_ADVANTAGE = "NO_ADVANTAGE"
STRICT_ADVANTAGE = "STRICT_ADVANTAGE"

RHO_STAR = Fraction(50, 133)
OPPORTUNITY_THRESHOLD = Fraction(20, 57)
BASE_ETA = Fraction(4, 5)
BASE_KAPPA = Fraction(1, 50)
BASE_RHO = Fraction(3, 4)
BASE_E_H = Fraction(1, 5)
BASE_E_S = Fraction(9, 10)
BASE_EBAR = Fraction(1, 2)


@dataclass(frozen=True)
class SweepConfiguration:
    """One pre-registered A1b primitive configuration."""

    phase: str
    configuration_id: str
    source: str
    rho: Fraction
    eta: Fraction
    kappa: Fraction
    e_h: Fraction
    e_s: Fraction


def _fraction_grid(stop_units: int, denominator: int) -> tuple[Fraction, ...]:
    return tuple(Fraction(index, denominator) for index in range(stop_units + 1))


def coupling_configurations() -> tuple[SweepConfiguration, ...]:
    """Return the 21-point rho grid plus seven frozen boundary probes."""
    global_grid = set(_fraction_grid(20, 20))
    probes = {RHO_STAR}
    for distance in (Fraction(1, 100), Fraction(1, 1000), Fraction(1, 10000)):
        probes.add(RHO_STAR - distance)
        probes.add(RHO_STAR + distance)
    values = sorted(global_grid | probes)
    return tuple(
        SweepConfiguration(
            phase=PHASE_1,
            configuration_id=f"A1b.1-{index:04d}",
            source="global_grid" if rho in global_grid else "boundary_probe",
            rho=rho,
            eta=BASE_ETA,
            kappa=BASE_KAPPA,
            e_h=BASE_E_H,
            e_s=BASE_E_S,
        )
        for index, rho in enumerate(values, start=1)
    )


def development_configurations() -> tuple[SweepConfiguration, ...]:
    """Return the frozen eta-by-kappa Cartesian grid."""
    eta_values = _fraction_grid(20, 20)
    kappa_values = _fraction_grid(25, 50)
    configurations = []
    for eta in eta_values:
        for kappa in kappa_values:
            configurations.append(
                SweepConfiguration(
                    phase=PHASE_2,
                    configuration_id=f"A1b.2-{len(configurations) + 1:04d}",
                    source="eta_kappa_grid",
                    rho=BASE_RHO,
                    eta=eta,
                    kappa=kappa,
                    e_h=BASE_E_H,
                    e_s=BASE_E_S,
                )
            )
    return tuple(configurations)


def opportunity_configurations() -> tuple[SweepConfiguration, ...]:
    """Return the full opportunity square plus five frozen anchored probes."""
    grid_values = _fraction_grid(20, 20)
    grid = {(e_h, e_s) for e_h in grid_values for e_s in grid_values}
    anchor = BASE_E_H
    boundary = anchor + OPPORTUNITY_THRESHOLD
    probes = {(anchor, boundary)}
    for distance in (Fraction(1, 100), Fraction(1, 1000)):
        probes.add((anchor, boundary - distance))
        probes.add((anchor, boundary + distance))
    pairs = sorted(grid | probes)
    return tuple(
        SweepConfiguration(
            phase=PHASE_3,
            configuration_id=f"A1b.3-{index:04d}",
            source="cartesian_grid" if pair in grid else "boundary_probe",
            rho=BASE_RHO,
            eta=BASE_ETA,
            kappa=BASE_KAPPA,
            e_h=pair[0],
            e_s=pair[1],
        )
        for index, pair in enumerate(pairs, start=1)
    )


def all_configurations() -> tuple[SweepConfiguration, ...]:
    """Return exactly the 1,020 pre-registered configurations."""
    return (
        coupling_configurations()
        + development_configurations()
        + opportunity_configurations()
    )


def analytical_regime(margin: float, *, tol: float = TOL) -> str:
    """Classify delta_G-delta_R under the frozen absolute tolerance."""
    if margin < -tol:
        return LESS
    if margin > tol:
        return GREATER
    return BOUNDARY


def observed_regime(delta_j_cons: float, *, tol: float = TOL) -> str:
    """Classify conservative observed advantage without truncating negatives."""
    if delta_j_cons < -tol:
        return NEGATIVE_UNEXPECTED
    if delta_j_cons > tol:
        return STRICT_ADVANTAGE
    return NO_ADVANTAGE


def expected_observed_regime(predicted: str) -> str:
    """Map the pre-registered analytical regime to its observed consequence."""
    if predicted in (LESS, BOUNDARY):
        return NO_ADVANTAGE
    if predicted == GREATER:
        return STRICT_ADVANTAGE
    raise ValueError(f"unknown analytical regime: {predicted}")


def conservative_advantage(
    hls: PolicySolution,
    sep: StrongSEPSolution,
) -> float:
    """Return J_HLS-J_SEP_max, including immediate-reward SEP ties."""
    return hls.optimal_value - sep.value_max


def _world_for(configuration: SweepConfiguration) -> A1aWorld:
    base = reference_worlds()["E"]
    return replace(
        base,
        rho=float(configuration.rho),
        eta=float(configuration.eta),
        kappa=float(configuration.kappa),
        opportunity_baseline=(float(BASE_EBAR), None),
        executor_opportunity=(
            (float(configuration.e_h), None),
            (float(configuration.e_s), None),
        ),
    )


def _learner_set(actions: Iterable[Learner]) -> str:
    return "|".join(sorted(action.value for action in actions))


def _development_set(actions: Iterable[DevelopmentAction]) -> str:
    labels = []
    for action in actions:
        if action.is_null:
            labels.append("null")
        else:
            assert action.recipient is not None and action.task is not None
            labels.append(f"develop_{action.recipient.value}_task_{action.task}")
    return "|".join(sorted(labels))


def _negative_controls(
    configuration: SweepConfiguration,
    *,
    d_minus_n: float,
    delta_g: float,
    delta_r: float,
) -> tuple[str, ...]:
    controls = []
    if configuration.rho == 0:
        controls.append("rho_zero")
    if configuration.eta == 0:
        controls.append("eta_zero")
    if abs(d_minus_n) <= TOL:
        controls.append("D_equals_N")
    if configuration.e_s == configuration.e_h:
        controls.append("e_s_equals_e_h")
    if configuration.e_s < configuration.e_h:
        controls.append("e_s_less_than_e_h")
    if (
        configuration.rho > 0
        and configuration.e_s > configuration.e_h
        and d_minus_n > TOL
        and delta_g < delta_r - TOL
    ):
        controls.append("positive_coupling_insufficient_delta_G")
    return tuple(controls)


def evaluate_configuration(configuration: SweepConfiguration) -> dict[str, object]:
    """Evaluate one configuration entirely through A1a world semantics."""
    world = _world_for(configuration)
    hls = solve_hls(world)
    sep = solve_strong_sep(world)
    sep_omega = solve_sep_omega(world)

    if len(sep.immediate_optimal_actions) != 1:
        raise ValueError("A1b fixed C must have one immediate-optimal SEP action")
    immediate_optimum = next(iter(sep.immediate_optimal_actions))
    alternatives = tuple(
        learner for learner in (Learner.M1, Learner.M2) if learner != immediate_optimum
    )
    if len(alternatives) != 1:
        raise ValueError("A1b requires exactly one alternative operational action")
    alternative = alternatives[0]

    n_value = hls.no_opportunity_value
    d_value = hls.opportunity_value
    d_minus_n = d_value - n_value
    delta_r = (
        hls.operational_rewards[immediate_optimum]
        - hls.operational_rewards[alternative]
    )
    delta_g = (
        hls.continuation_values[alternative]
        - hls.continuation_values[immediate_optimum]
    )
    analytical_margin = delta_g - delta_r
    delta_j_cons = conservative_advantage(hls, sep)
    predicted = analytical_regime(analytical_margin)
    observed = observed_regime(delta_j_cons)
    expected_observed = expected_observed_regime(predicted)
    controls = _negative_controls(
        configuration,
        d_minus_n=d_minus_n,
        delta_g=delta_g,
        delta_r=delta_r,
    )
    sep_omega_gap = hls.optimal_value - sep_omega.optimal_value
    negative_control_violation = bool(controls) and observed == STRICT_ADVANTAGE

    return {
        "phase": configuration.phase,
        "configuration_id": configuration.configuration_id,
        "configuration_source": configuration.source,
        "rho": float(configuration.rho),
        "rho_exact": str(configuration.rho),
        "eta": float(configuration.eta),
        "eta_exact": str(configuration.eta),
        "kappa": float(configuration.kappa),
        "kappa_exact": str(configuration.kappa),
        "e_h": float(configuration.e_h),
        "e_h_exact": str(configuration.e_h),
        "e_s": float(configuration.e_s),
        "e_s_exact": str(configuration.e_s),
        "e_s_minus_e_h": float(configuration.e_s - configuration.e_h),
        "ebar": float(BASE_EBAR),
        "beta": world.beta,
        "q0": world.q0,
        "q1": world.q1,
        "c_11": world.competence[0][0],
        "c_12": world.competence[0][1],
        "c_21": world.competence[1][0],
        "c_22": world.competence[1][1],
        "g_h": hls.opportunity_probabilities[immediate_optimum],
        "g_s": hls.opportunity_probabilities[alternative],
        "N": n_value,
        "D": d_value,
        "D_minus_N": d_minus_n,
        "delta_R": delta_r,
        "delta_G": delta_g,
        "analytical_margin": analytical_margin,
        "J_HLS": hls.optimal_value,
        "J_SEP_min": sep.value_min,
        "J_SEP_max": sep.value_max,
        "Delta_J_cons": delta_j_cons,
        "J_SEP_Omega": sep_omega.optimal_value,
        "SEP_Omega_gap": sep_omega_gap,
        "HLS_optimal_actions": _learner_set(hls.optimal_operational_actions),
        "SEP_immediate_optimal_actions": _learner_set(
            sep.immediate_optimal_actions
        ),
        "optimal_development_actions": _development_set(
            hls.optimal_development_actions
        ),
        "predicted_regime": predicted,
        "observed_regime": observed,
        "expected_observed_regime": expected_observed,
        "match": observed == expected_observed,
        "negative_controls": "|".join(controls),
        "negative_control_violation": negative_control_violation,
        "SEP_Omega_violation": abs(sep_omega_gap) > TOL,
    }


def _phase_summary(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    predicted = Counter(str(row["predicted_regime"]) for row in rows)
    observed = Counter(str(row["observed_regime"]) for row in rows)
    mismatches = [str(row["configuration_id"]) for row in rows if not row["match"]]
    negative_violations = [
        str(row["configuration_id"])
        for row in rows
        if row["negative_control_violation"]
    ]
    omega_violations = [
        str(row["configuration_id"])
        for row in rows
        if row["SEP_Omega_violation"]
    ]
    controls = Counter()
    for row in rows:
        for control in str(row["negative_controls"]).split("|"):
            if control:
                controls[control] += 1
    return {
        "n_configurations": len(rows),
        "predicted": {
            LESS: predicted[LESS],
            BOUNDARY: predicted[BOUNDARY],
            GREATER: predicted[GREATER],
        },
        "observed": {
            NEGATIVE_UNEXPECTED: observed[NEGATIVE_UNEXPECTED],
            NO_ADVANTAGE: observed[NO_ADVANTAGE],
            STRICT_ADVANTAGE: observed[STRICT_ADVANTAGE],
        },
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "negative_control_coverage": dict(sorted(controls.items())),
        "negative_control_violation_count": len(negative_violations),
        "negative_control_violations": negative_violations,
        "SEP_Omega_violation_count": len(omega_violations),
        "SEP_Omega_violations": omega_violations,
    }


def aggregate(rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    """Aggregate pre-registered phase and global PASS/FAIL criteria."""
    by_phase = {
        phase: tuple(row for row in rows if row["phase"] == phase)
        for phase in (PHASE_1, PHASE_2, PHASE_3)
    }
    phases = {phase: _phase_summary(phase_rows) for phase, phase_rows in by_phase.items()}
    count_match = {
        phase: len(by_phase[phase]) == expected
        for phase, expected in EXPECTED_COUNTS.items()
    }
    mismatch_count = sum(int(summary["mismatch_count"]) for summary in phases.values())
    negative_violation_count = sum(
        int(summary["negative_control_violation_count"])
        for summary in phases.values()
    )
    omega_violation_count = sum(
        int(summary["SEP_Omega_violation_count"]) for summary in phases.values()
    )
    required_controls = {
        "rho_zero",
        "eta_zero",
        "D_equals_N",
        "e_s_equals_e_h",
        "e_s_less_than_e_h",
        "positive_coupling_insufficient_delta_G",
    }
    covered_controls = {
        control
        for summary in phases.values()
        for control in summary["negative_control_coverage"]
    }
    controls_complete = required_controls <= covered_controls
    passed = (
        len(rows) == sum(EXPECTED_COUNTS.values())
        and all(count_match.values())
        and mismatch_count == 0
        and negative_violation_count == 0
        and omega_violation_count == 0
        and controls_complete
    )
    return {
        "experiment_id": "A1b",
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "deterministic": True,
        "seeds": [],
        "tolerance": TOL,
        "conservative_metric": "J_HLS-J_SEP_max",
        "expected_counts": EXPECTED_COUNTS,
        "effective_counts": {phase: len(values) for phase, values in by_phase.items()},
        "total_configurations": len(rows),
        "count_match": count_match,
        "mandatory_negative_controls": sorted(required_controls),
        "negative_controls_complete": controls_complete,
        "mismatch_count": mismatch_count,
        "negative_control_violation_count": negative_violation_count,
        "SEP_Omega_violation_count": omega_violation_count,
        "phases": phases,
        "interpretation": (
            "Agreement of the exact solver with pre-registered A1a phase "
            "boundaries; not empirical validation of RQ0."
        ),
    }


def run_sweep() -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    """Evaluate all 1,020 configurations deterministically and aggregate them."""
    configurations = all_configurations()
    rows = tuple(evaluate_configuration(configuration) for configuration in configurations)
    return rows, aggregate(rows)


def configuration_key(row: Mapping[str, object]) -> tuple[object, ...]:
    """Return the primitive identity used to detect accidental extra duplicates."""
    return (
        row["phase"],
        row["rho_exact"],
        row["eta_exact"],
        row["kappa_exact"],
        row["e_h_exact"],
        row["e_s_exact"],
    )
