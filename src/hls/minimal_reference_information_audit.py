"""Information-partition audit for the fixed Phase-V minimal-reference family.

This module does not alter the reference scenario or its validation grid.  It
asks a finite-family question: after the current operational information
(``S0``, ``P0``, and ``beta``) is held common, which additional representation
of action-induced competence evolution permits an information-constrained rule
to match the oracle evaluated by the existing scenario?

``phi0``--``phi3`` and the algebraic features are constructed without calling ``evaluate``,
``terminal_value``, or using ``G``/``V1``.  ``phi_oracle`` is an explicitly
separate control whose sole extra feature is the evaluated ``G`` target.
Results are finite-grid audits, never general sufficiency-statistic claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from math import fsum, log10
from random import Random
from statistics import mean
from typing import Iterable

from .minimal_reference_scenario import Action, EXACT_TOL, LearningRule, MinimalReferenceScenario
from .minimal_reference_validation import CLASS_TOL, ValidationRow, evaluate_primitives, primary_primitives


RepresentationName = str
FEATURE_REPRESENTATIONS: tuple[RepresentationName, ...] = ("phi0", "phi1", "phi2", "phi3")
ALGEBRAIC_REPRESENTATIONS: tuple[RepresentationName, ...] = (
    "phi_alg", "alg_h", "alg_u", "alg_v", "alg_hu", "alg_hv", "alg_uv",
    "alg_h_v_minus_u", "alg_v_minus_u", "alg_h_plus_u",
)
ALL_REPRESENTATIONS: tuple[RepresentationName, ...] = (
    FEATURE_REPRESENTATIONS + ALGEBRAIC_REPRESENTATIONS + ("phi_oracle",)
)
KEY_DIGITS = 12
SCALAR_SEED = 20261002
CONTINUOUS_SAMPLE_SIZES = {"uniform": 50_000, "edge_and_saturation": 30_000, "demand_and_beta_extremes": 20_000}
ADVERSARIAL_TARGET_PER_REGION = 1_000
ADVERSARIAL_TARGET_PER_BOUNDARY = 100


def _number(value: float) -> float:
    """Use a stable finite-grid key without merging distinct grid values."""
    return round(value, KEY_DIGITS)


def _flat_state(state: tuple[tuple[float, float], tuple[float, float]]) -> tuple[float, ...]:
    return tuple(_number(value) for worker in state for value in worker)


def _delta_state(scenario: MinimalReferenceScenario, action: Action) -> tuple[float, ...]:
    """Return F(S,a)-S directly from the scenario transition, never from V1."""
    next_state = scenario.transition(action)
    return tuple(
        _number(next_state[worker][task] - scenario.state_0[worker][task])
        for worker in range(2)
        for task in range(2)
    )


@dataclass(frozen=True)
class AlgebraicPrimitives:
    """Non-circular primitive reconstruction inputs for the 2x2x2 terminal value.

    No value function, terminal optimization, or ``G`` is used here.  The four
    increments are read directly from the two existing transitions.
    """

    h: float
    u: float
    v: float
    alpha: float
    epsilon: float
    gamma: float
    delta: float

    @property
    def g_alg(self) -> float:
        return max(self.h, self.v) - max(self.h + self.u, 0.0)


def algebraic_primitives(scenario: MinimalReferenceScenario) -> AlgebraicPrimitives:
    """Derive h, u, v solely from S0, P1, and F(S,a)-S."""
    (a, b), (c, d) = scenario.state_0
    p = scenario.demand_1[0]
    state_e = scenario.transition("E")
    state_d = scenario.transition("D")
    alpha = state_e[0][0] - a
    epsilon = state_e[1][1] - d
    gamma = state_d[0][1] - b
    delta = state_d[1][0] - c
    x = p * a + (1.0 - p) * d
    y = (1.0 - p) * b + p * c
    return AlgebraicPrimitives(
        h=x - y,
        u=p * alpha + (1.0 - p) * epsilon,
        v=(1.0 - p) * gamma + p * delta,
        alpha=alpha,
        epsilon=epsilon,
        gamma=gamma,
        delta=delta,
    )


def algebraic_region(values: AlgebraicPrimitives) -> str:
    """Classify A/B/C, retaining either algebraic boundary at canonical tolerance."""
    h, u, v = values.h, values.u, values.v
    on_h_v = abs(h - v) <= CLASS_TOL
    on_h_neg_u = abs(h + u) <= CLASS_TOL
    if on_h_v and on_h_neg_u:
        return "boundary_h_equals_v_and_negative_u"
    if on_h_v:
        return "boundary_h_equals_v"
    if on_h_neg_u:
        return "boundary_h_equals_negative_u"
    if h > v:
        return "A_h_ge_v"
    if h < -u:
        return "B_h_le_negative_u"
    return "C_negative_u_lt_h_lt_v"


def scalar_m(h: float, u: float, v: float) -> float:
    """Return the candidate scalar decision compression from h, u, and v only."""
    return min(v, v - u - h)


def scalar_delta_j(loss: float, beta: float, h: float, u: float, v: float) -> float:
    """Return -L+beta*m without consulting any value function or oracle result."""
    return -loss + beta * scalar_m(h, u, v)


def sign_tol(value: float) -> int:
    """Canonical three-way decision sign used for the audit."""
    if value > CLASS_TOL:
        return 1
    if value < -CLASS_TOL:
        return -1
    return 0


def common_decision_information(scenario: MinimalReferenceScenario) -> tuple[float, ...]:
    """Operational information shared by every audit representation.

    It contains what is required to evaluate the present loss L at decision
    time.  It is deliberately not counted as future information in phi.
    """
    return _flat_state(scenario.state_0) + tuple(_number(value) for value in scenario.demand_0) + (_number(scenario.beta),)


def future_feature(scenario: MinimalReferenceScenario, representation: RepresentationName) -> tuple[float, ...]:
    """Construct the requested future-information feature.

    ``phi0``--``phi3`` intentionally never call the oracle evaluator.  The
    oracle control is the only representation allowed to derive G.
    """
    if representation == "phi0":
        return ()
    delta_e = _delta_state(scenario, "E")
    delta_d = _delta_state(scenario, "D")
    if representation == "phi1":
        return (_number(sum(delta_e)), _number(sum(delta_d)))
    if representation == "phi2":
        return delta_e + delta_d
    if representation == "phi3":
        return delta_e + delta_d + tuple(_number(value) for value in scenario.demand_1)
    algebra = algebraic_primitives(scenario)
    if representation == "phi_alg":
        return (_number(algebra.h), _number(algebra.u), _number(algebra.v))
    if representation == "alg_h":
        return (_number(algebra.h),)
    if representation == "alg_u":
        return (_number(algebra.u),)
    if representation == "alg_v":
        return (_number(algebra.v),)
    if representation == "alg_hu":
        return (_number(algebra.h), _number(algebra.u))
    if representation == "alg_hv":
        return (_number(algebra.h), _number(algebra.v))
    if representation == "alg_uv":
        return (_number(algebra.u), _number(algebra.v))
    if representation == "alg_h_v_minus_u":
        return (_number(algebra.h), _number(algebra.v - algebra.u))
    if representation == "alg_v_minus_u":
        return (_number(algebra.v - algebra.u),)
    if representation == "alg_h_plus_u":
        return (_number(algebra.h + algebra.u),)
    if representation == "phi_oracle":
        evaluation = scenario.evaluate()
        return (_number(evaluation.gain),)
    raise ValueError(f"unknown representation: {representation}")


def representation_key(scenario: MinimalReferenceScenario, representation: RepresentationName) -> tuple[float, ...]:
    """Return common decision information plus one future-information feature."""
    return common_decision_information(scenario) + future_feature(scenario, representation)


def _canonical_action(values: tuple[float, float]) -> Action:
    """Resolve an exact tie to E only for deterministic reporting."""
    return "E" if values[0] >= values[1] - EXACT_TOL else "D"


@dataclass(frozen=True)
class AuditWorld:
    """Existing Phase-V world with oracle and myopic controls derived once."""

    row: ValidationRow
    reward_e: float
    reward_d: float
    total_e: float
    total_d: float
    oracle_actions: tuple[Action, ...]
    oracle_action: Action
    myopic_action: Action

    @property
    def oracle_value(self) -> float:
        return max(self.total_e, self.total_d)

    @property
    def myopic_value(self) -> float:
        return self.total_e if self.myopic_action == "E" else self.total_d

    def value(self, action: Action) -> float:
        return self.total_e if action == "E" else self.total_d

    def regret(self, action: Action) -> float:
        difference = self.oracle_value - self.value(action)
        return 0.0 if difference <= EXACT_TOL else difference

    def as_example(self) -> dict[str, object]:
        primitive = self.row.primitive
        return {
            "primitive": {
                "a1": primitive.a1, "a2": primitive.a2, "b1": primitive.b1, "b2": primitive.b2,
                "present_A": primitive.present_a, "future_A": primitive.future_a,
                "learning_scale": primitive.learning_scale, "beta": primitive.beta,
            },
            "regime": self.row.regime,
            "oracle_action": self.oracle_action,
            "oracle_actions": list(self.oracle_actions),
            "myopic_action": self.myopic_action,
            "L": self.row.loss,
            "G": self.row.gain,
            "total_E": self.total_e,
            "total_D": self.total_d,
        }


def _audit_world(row: ValidationRow) -> AuditWorld:
    scenario = row.primitive.scenario()
    evaluation = scenario.evaluate()
    return AuditWorld(
        row=row,
        reward_e=evaluation.reward_e,
        reward_d=evaluation.reward_d,
        total_e=evaluation.total_e,
        total_d=evaluation.total_d,
        oracle_actions=evaluation.optimal_actions(),
        oracle_action=_canonical_action((evaluation.total_e, evaluation.total_d)),
        myopic_action=_canonical_action((evaluation.reward_e, evaluation.reward_d)),
    )


def audit_worlds(rows: Iterable[ValidationRow]) -> tuple[AuditWorld, ...]:
    return tuple(_audit_world(row) for row in rows)


def _choose_class_action(worlds: tuple[AuditWorld, ...]) -> Action:
    """Empirical information-constrained optimum; no predictor is trained."""
    total_e = sum(world.total_e for world in worlds)
    total_d = sum(world.total_d for world in worlds)
    return _canonical_action((total_e, total_d))


def _histogram(values: Iterable[float]) -> dict[str, int]:
    return dict(sorted(Counter(f"{value:.12g}" for value in values).items(), key=lambda item: float(item[0])))


def _metrics(worlds: tuple[AuditWorld, ...], action_for_key: dict[tuple[float, ...], Action], keys: dict[int, tuple[float, ...]]) -> dict[str, object]:
    selected = tuple(action_for_key[keys[id(world)]] for world in worlds)
    return _metrics_for_actions(worlds, selected)


def _metrics_for_actions(worlds: tuple[AuditWorld, ...], selected: tuple[Action, ...]) -> dict[str, object]:
    """Evaluate supplied actions against the existing oracle and myopic controls."""
    regrets = tuple(world.regret(action) for world, action in zip(worlds, selected))
    oracle_total = sum(world.oracle_value for world in worlds)
    myopic_total = sum(world.myopic_value for world in worlds)
    selected_total = sum(world.value(action) for world, action in zip(worlds, selected))
    available_gain = oracle_total - myopic_total
    recovered_gain = selected_total - myopic_total
    return {
        "worlds": len(worlds),
        "oracle_agreement": sum(action in world.oracle_actions for world, action in zip(worlds, selected)) / len(worlds) if worlds else None,
        "regret_total": sum(regrets),
        "regret_mean": mean(regrets) if regrets else 0.0,
        "worst_case_regret": max(regrets, default=0.0),
        "positive_regret_worlds": sum(regret > CLASS_TOL for regret in regrets),
        "regret_distribution": _histogram(regrets),
        "oracle_total_value": oracle_total,
        "myopic_total_value": myopic_total,
        "rule_total_value": selected_total,
        "oracle_gain_over_myopic": available_gain,
        "rule_gain_over_myopic": recovered_gain,
        "oracle_value_fraction_recovered_over_myopic": (
            recovered_gain / available_gain if available_gain > CLASS_TOL else None
        ),
    }


def algebraic_action(scenario: MinimalReferenceScenario) -> Action:
    """Choose by -L+beta*G_alg; no terminal V1 evaluation is performed."""
    values = algebraic_primitives(scenario)
    loss = scenario.present_reward("E") - scenario.present_reward("D")
    delta_j_alg = -loss + scenario.beta * values.g_alg
    return "D" if delta_j_alg > EXACT_TOL else "E"


def _algebraic_rule_metrics(worlds: tuple[AuditWorld, ...]) -> dict[str, object]:
    actions = tuple(algebraic_action(world.row.primitive.scenario()) for world in worlds)
    report = _metrics_for_actions(worlds, actions)
    report["rule"] = "D iff -L+beta*(max(h,v)-max(h+u,0)) > 0; ties resolve to E"
    return report


def algebraic_validation(worlds: tuple[AuditWorld, ...]) -> dict[str, object]:
    """Compare the non-circular algebraic reconstruction to existing exact controls."""
    region_counts: Counter[str] = Counter()
    max_g_residual = 0.0
    max_delta_j_residual = 0.0
    max_branch_residual: dict[str, float] = defaultdict(float)
    counterexamples: list[dict[str, object]] = []
    for world in worlds:
        scenario = world.row.primitive.scenario()
        values = algebraic_primitives(scenario)
        region = algebraic_region(values)
        region_counts[region] += 1
        g_residual = values.g_alg - world.row.gain
        loss = scenario.present_reward("E") - scenario.present_reward("D")
        delta_j_alg = -loss + scenario.beta * values.g_alg
        delta_j_residual = delta_j_alg - world.row.delta_j
        max_g_residual = max(max_g_residual, abs(g_residual))
        max_delta_j_residual = max(max_delta_j_residual, abs(delta_j_residual))
        if region == "A_h_ge_v":
            branch = -values.u
        elif region == "B_h_le_negative_u":
            branch = values.v
        elif region == "C_negative_u_lt_h_lt_v":
            branch = values.v - values.u - values.h
        else:
            branch = values.g_alg
        max_branch_residual[region] = max(max_branch_residual[region], abs(values.g_alg - branch))
        if (abs(g_residual) > CLASS_TOL or abs(delta_j_residual) > CLASS_TOL) and len(counterexamples) < 5:
            example = world.as_example()
            example.update({"h": values.h, "u": values.u, "v": values.v, "G_alg": values.g_alg,
                            "G_residual": g_residual, "DeltaJ_alg": delta_j_alg,
                            "DeltaJ_residual": delta_j_residual, "region": region})
            counterexamples.append(example)
    return {
        "G_alg": "max(h,v)-max(h+u,0)",
        "DeltaJ_alg": "-L+beta*G_alg",
        "maximum_absolute_G_residual": max_g_residual,
        "maximum_absolute_DeltaJ_residual": max_delta_j_residual,
        "region_counts": dict(sorted(region_counts.items())),
        "maximum_branch_formula_residual_by_region": dict(sorted(max_branch_residual.items())),
        "counterexamples": counterexamples,
        "interpretation": "Validated numerically only for the defined 2x2x2 scenario and audited Phase-V grid.",
    }


def _decision_observation(scenario: MinimalReferenceScenario, *, source: str) -> dict[str, object]:
    """Build scalar quantities first, then query the existing evaluator as oracle."""
    values = algebraic_primitives(scenario)
    loss = scenario.present_reward("E") - scenario.present_reward("D")
    margin = scalar_m(values.h, values.u, values.v)
    delta_m = -loss + scenario.beta * margin
    evaluation = scenario.evaluate()
    # The evaluator's pre-summed totals can lose a small L when beta is very
    # large.  This compensated regrouping is the same J(D)-J(E), evaluated
    # from the existing reward/value outputs only; it is not used by m.
    exact = fsum((evaluation.reward_d, -evaluation.reward_e,
                  scenario.beta * evaluation.value_d, -scenario.beta * evaluation.value_e))
    naive_total_difference = evaluation.total_difference
    return {
        "source": source,
        "state_0": scenario.state_0,
        "demand_0": scenario.demand_0,
        "demand_1": scenario.demand_1,
        "beta": scenario.beta,
        "learning_scale": scenario.learning_scale,
        "L": loss,
        "h": values.h,
        "u": values.u,
        "v": values.v,
        "m": margin,
        "region": algebraic_region(values),
        "DeltaJ_m": delta_m,
        "DeltaJ_exact": exact,
        "DeltaJ_naive_total_difference": naive_total_difference,
        "scalar_sign": sign_tol(delta_m),
        "exact_sign": sign_tol(exact),
        "naive_exact_sign_disagrees": sign_tol(naive_total_difference) != sign_tol(exact),
    }


def _empty_decision_summary() -> dict[str, object]:
    return {
        "worlds": 0, "E_agreements": 0, "D_agreements": 0, "tie_agreements": 0,
        "disagreements": 0, "maximum_absolute_delta_difference": 0.0,
        "naive_oracle_sign_disagreements": 0,
        "by_algebraic_region": defaultdict(lambda: {"worlds": 0, "disagreements": 0}),
        "by_phase_regime": defaultdict(lambda: {"worlds": 0, "disagreements": 0}),
        "counterexamples": [],
    }


def _add_decision_observation(summary: dict[str, object], observation: dict[str, object], phase_regime: str | None = None) -> None:
    summary["worlds"] = int(summary["worlds"]) + 1
    matches = observation["scalar_sign"] == observation["exact_sign"]
    if matches:
        if observation["exact_sign"] < 0:
            summary["E_agreements"] = int(summary["E_agreements"]) + 1
        elif observation["exact_sign"] > 0:
            summary["D_agreements"] = int(summary["D_agreements"]) + 1
        else:
            summary["tie_agreements"] = int(summary["tie_agreements"]) + 1
    else:
        summary["disagreements"] = int(summary["disagreements"]) + 1
        counterexamples = summary["counterexamples"]
        if len(counterexamples) < 5:
            counterexamples.append(observation)
    summary["naive_oracle_sign_disagreements"] = int(summary["naive_oracle_sign_disagreements"]) + int(observation["naive_exact_sign_disagrees"])
    summary["maximum_absolute_delta_difference"] = max(
        float(summary["maximum_absolute_delta_difference"]),
        abs(float(observation["DeltaJ_m"]) - float(observation["DeltaJ_exact"])),
    )
    region_record = summary["by_algebraic_region"][observation["region"]]
    region_record["worlds"] += 1
    region_record["disagreements"] += 0 if matches else 1
    if phase_regime is not None:
        phase_record = summary["by_phase_regime"][phase_regime]
        phase_record["worlds"] += 1
        phase_record["disagreements"] += 0 if matches else 1


def _finalize_decision_summary(summary: dict[str, object]) -> dict[str, object]:
    result = dict(summary)
    result["by_algebraic_region"] = dict(sorted(summary["by_algebraic_region"].items()))
    result["by_phase_regime"] = dict(sorted(summary["by_phase_regime"].items()))
    return result


def scalar_grid_validation(worlds: tuple[AuditWorld, ...]) -> dict[str, object]:
    """Test scalar decision signs on all Phase-V worlds and its formal domain."""
    all_worlds = _empty_decision_summary()
    formal_domain = _empty_decision_summary()
    for world in worlds:
        scenario = world.row.primitive.scenario()
        observation = _decision_observation(scenario, source="phase_v_grid")
        _add_decision_observation(all_worlds, observation, world.row.regime)
        if observation["L"] > CLASS_TOL and scenario.beta > CLASS_TOL:
            _add_decision_observation(formal_domain, observation, world.row.regime)
    return {
        "all_221184_worlds_observational_control": _finalize_decision_summary(all_worlds),
        "formal_domain_L_gt_0_beta_gt_0": _finalize_decision_summary(formal_domain),
        "tolerance": CLASS_TOL,
        "note": "Only the L>0, beta>0 report tests the stated scalar decision hypothesis.",
    }


def _log_uniform(rng: Random, low: float, high: float) -> float:
    return 10.0 ** rng.uniform(log10(low), log10(high))


def _continuous_scenario(rng: Random, mode: str) -> MinimalReferenceScenario:
    if mode == "uniform":
        state = tuple(tuple(rng.random() for _ in range(2)) for _ in range(2))
        p0, p1 = rng.random(), rng.random()
        scale = rng.uniform(0.0, 5.0)
        beta = _log_uniform(rng, 1e-8, 1e3)
    elif mode == "edge_and_saturation":
        def edge() -> float:
            return rng.uniform(0.0, 1e-9) if rng.random() < 0.5 else rng.uniform(1.0 - 1e-9, 1.0)
        state = tuple(tuple(edge() for _ in range(2)) for _ in range(2))
        p0 = rng.choice((0.0, 1e-12, 0.5, 1.0 - 1e-12, 1.0))
        p1 = rng.choice((0.0, 1e-12, 0.5, 1.0 - 1e-12, 1.0))
        scale = rng.choice((0.0, 1e-12, 1e-6, 0.01, 0.5, 1.0, 2.0, 10.0))
        beta = rng.choice((1e-12, 1e-8, 1e-4, 0.01, 1.0, 100.0, 1e6))
    elif mode == "demand_and_beta_extremes":
        state = tuple(tuple(rng.random() for _ in range(2)) for _ in range(2))
        p0 = rng.choice((0.0, 1e-15, 1e-8, 0.5 - 1e-12, 0.5, 0.5 + 1e-12, 1.0 - 1e-8, 1.0))
        p1 = rng.choice((0.0, 1e-15, 1e-8, 0.5 - 1e-12, 0.5, 0.5 + 1e-12, 1.0 - 1e-8, 1.0))
        scale = rng.choice((1e-12, 1e-6, 0.1, 1.0, 3.0, 10.0))
        beta = _log_uniform(rng, 1e-12, 1e6)
    else:
        raise ValueError(f"unknown continuous sampling mode: {mode}")
    return MinimalReferenceScenario(state, (p0, 1.0 - p0), (p1, 1.0 - p1), beta, LearningRule.DIMINISHING, scale)


def continuous_validation() -> dict[str, object]:
    """Falsification-oriented reproducible continuous sample in the same model."""
    rng = Random(SCALAR_SEED)
    all_samples = _empty_decision_summary()
    formal_domain = _empty_decision_summary()
    by_mode: dict[str, dict[str, object]] = {}
    for mode, size in CONTINUOUS_SAMPLE_SIZES.items():
        report = _empty_decision_summary()
        for _ in range(size):
            scenario = _continuous_scenario(rng, mode)
            observation = _decision_observation(scenario, source=f"continuous:{mode}")
            _add_decision_observation(all_samples, observation)
            _add_decision_observation(report, observation)
            if observation["L"] > CLASS_TOL and scenario.beta > CLASS_TOL:
                _add_decision_observation(formal_domain, observation)
        by_mode[mode] = _finalize_decision_summary(report)
    return {
        "seed": SCALAR_SEED,
        "sampling": dict(CONTINUOUS_SAMPLE_SIZES),
        "all_samples_observational_control": _finalize_decision_summary(all_samples),
        "formal_domain_L_gt_0_beta_gt_0": _finalize_decision_summary(formal_domain),
        "by_mode": by_mode,
        "tolerance": CLASS_TOL,
    }


def _root_for_boundary(scenario: MinimalReferenceScenario, boundary: str) -> float | None:
    """Solve the p1-linear h=v or h=-u condition without calling the oracle."""
    def residual(p: float) -> float:
        candidate = MinimalReferenceScenario(
            scenario.state_0, scenario.demand_0, (p, 1.0 - p), scenario.beta,
            scenario.learning_rule, scenario.learning_scale,
        )
        values = algebraic_primitives(candidate)
        return values.h - values.v if boundary == "h_equals_v" else values.h + values.u
    f0, f1 = residual(0.0), residual(1.0)
    if abs(f0) <= CLASS_TOL:
        return 0.0
    if abs(f1) <= CLASS_TOL:
        return 1.0
    if f0 * f1 > 0.0:
        return None
    denominator = f1 - f0
    if abs(denominator) <= CLASS_TOL:
        return None
    root = -f0 / denominator
    return root if 0.0 < root < 1.0 else None


def adversarial_validation() -> dict[str, object]:
    """Target interiors, algebraic boundaries, and decision boundaries adversarially."""
    rng = Random(SCALAR_SEED + 1)
    interiors: dict[str, dict[str, object]] = {name: _empty_decision_summary() for name in (
        "A_h_ge_v", "B_h_le_negative_u", "C_negative_u_lt_h_lt_v"
    )}
    attempts = 0
    while any(report["worlds"] < ADVERSARIAL_TARGET_PER_REGION for report in interiors.values()):
        attempts += 1
        if attempts > 2_000_000:
            raise RuntimeError("could not obtain requested adversarial region coverage")
        scenario = _continuous_scenario(rng, "uniform")
        observation = _decision_observation(scenario, source="adversarial:interior")
        if observation["L"] <= CLASS_TOL or scenario.beta <= CLASS_TOL:
            continue
        region = observation["region"]
        if region in interiors and interiors[region]["worlds"] < ADVERSARIAL_TARGET_PER_REGION:
            _add_decision_observation(interiors[region], observation)

    boundary_reports: dict[str, dict[str, object]] = {}
    for boundary in ("h_equals_v", "h_equals_negative_u"):
        report = _empty_decision_summary()
        roots = 0
        attempts = 0
        while roots < ADVERSARIAL_TARGET_PER_BOUNDARY:
            attempts += 1
            if attempts > 2_000_000:
                raise RuntimeError(f"could not obtain requested {boundary} roots")
            base = _continuous_scenario(rng, "uniform")
            root = _root_for_boundary(base, boundary)
            if root is None or root < 1e-4 or root > 1.0 - 1e-4:
                continue
            roots += 1
            for epsilon in (0.0, -1e-4, 1e-4, -1e-8, 1e-8, -1e-12, 1e-12):
                p = min(1.0, max(0.0, root + epsilon))
                scenario = MinimalReferenceScenario(
                    base.state_0, base.demand_0, (p, 1.0 - p), base.beta,
                    base.learning_rule, base.learning_scale,
                )
                observation = _decision_observation(scenario, source=f"adversarial:{boundary}:eps={epsilon}")
                if observation["L"] > CLASS_TOL and scenario.beta > CLASS_TOL:
                    _add_decision_observation(report, observation)
        boundary_reports[boundary] = _finalize_decision_summary(report)

    decision_boundary = _empty_decision_summary()
    roots = 0
    attempts = 0
    while roots < ADVERSARIAL_TARGET_PER_BOUNDARY:
        attempts += 1
        if attempts > 2_000_000:
            raise RuntimeError("could not obtain requested decision-boundary worlds")
        base = _continuous_scenario(rng, "uniform")
        base = MinimalReferenceScenario(base.state_0, base.demand_0, base.demand_1, 1.0, base.learning_rule, base.learning_scale)
        values = algebraic_primitives(base)
        loss = base.present_reward("E") - base.present_reward("D")
        margin = scalar_m(values.h, values.u, values.v)
        if loss <= 1e-6 or margin <= 1e-6:
            continue
        beta_boundary = loss / margin
        roots += 1
        for relative in (-1e-4, -1e-8, -1e-12, 0.0, 1e-12, 1e-8, 1e-4):
            beta = beta_boundary * (1.0 + relative)
            scenario = MinimalReferenceScenario(base.state_0, base.demand_0, base.demand_1, beta, base.learning_rule, base.learning_scale)
            observation = _decision_observation(scenario, source=f"adversarial:decision_boundary:relative={relative}")
            _add_decision_observation(decision_boundary, observation)
    return {
        "interior_regions": {name: _finalize_decision_summary(report) for name, report in interiors.items()},
        "algebraic_boundary_perturbations": boundary_reports,
        "decision_boundary_beta_equals_L_over_m": _finalize_decision_summary(decision_boundary),
        "boundary_perturbations": [0.0, -1e-4, 1e-4, -1e-8, 1e-8, -1e-12, 1e-12],
        "decision_beta_relative_perturbations": [-1e-4, -1e-8, -1e-12, 0.0, 1e-12, 1e-8, 1e-4],
    }


def limit_case_validation() -> dict[str, object]:
    """Explicit same-model edge controls; L<=0 and beta=0 remain non-claims."""
    common = dict(demand_0=(0.50000001, 0.49999999), learning_rule=LearningRule.DIMINISHING)
    cases = {
        "u_zero_learning_scale_zero": MinimalReferenceScenario(((.7, .2), (.4, .6)), (.6, .4), (.5, .5), .5, LearningRule.DIMINISHING, 0.0),
        "v_zero_saturated_D_recipients": MinimalReferenceScenario(((.2, 1.0), (1.0, .3)), (.6, .4), (.0, 1.0), .5, LearningRule.DIMINISHING, 10.0),
        "h_zero": MinimalReferenceScenario(((.4, .4), (.4, .4)), (.6, .4), (.5, .5), .5, LearningRule.DIMINISHING, 1.0),
        "one_saturated_competence": MinimalReferenceScenario(((1.0, .2), (.3, .4)), (.6, .4), (.0, 1.0), .5, LearningRule.DIMINISHING, 10.0),
        "multiple_saturated_competences": MinimalReferenceScenario(((.99, .99), (.99, .99)), (.6, .4), (.5, .5), .5, LearningRule.DIMINISHING, 10.0),
        "P1_A_only": MinimalReferenceScenario(((.7, .2), (.4, .6)), (.6, .4), (1.0, .0), .5, LearningRule.DIMINISHING, 1.0),
        "P1_B_only": MinimalReferenceScenario(((.7, .2), (.4, .6)), (.6, .4), (.0, 1.0), .5, LearningRule.DIMINISHING, 1.0),
        "P1_balanced": MinimalReferenceScenario(((.7, .2), (.4, .6)), (.6, .4), (.5, .5), .5, LearningRule.DIMINISHING, 1.0),
        "L_small_positive": MinimalReferenceScenario(((.50000002, .5), (.5, .5)), (.5, .5), (.5, .5), .5, LearningRule.DIMINISHING, 1.0),
        "beta_small_positive": MinimalReferenceScenario(((.7, .2), (.4, .6)), (.6, .4), (.0, 1.0), 1e-12, LearningRule.DIMINISHING, 1.0),
        "beta_large": MinimalReferenceScenario(((.7, .2), (.4, .6)), (.6, .4), (.0, 1.0), 1e6, LearningRule.DIMINISHING, 1.0),
    }
    records = {name: _decision_observation(scenario, source=f"limit:{name}") for name, scenario in cases.items()}
    return {
        "controls": records,
        "all_sign_agree": all(record["scalar_sign"] == record["exact_sign"] for record in records.values()),
        "note": "Controls outside L>0,beta>0 are descriptive only and do not expand the formal claim.",
    }


def _collision_examples(groups: dict[tuple[float, ...], tuple[AuditWorld, ...]]) -> list[dict[str, object]]:
    examples = []
    for key, worlds in groups.items():
        labels = {world.oracle_action for world in worlds}
        common_actions = set.intersection(*(set(world.oracle_actions) for world in worlds))
        if len(labels) > 1 or not common_actions:
            ordered = sorted(worlds, key=lambda world: (world.oracle_action, world.row.regime, world.as_example()["primitive"]["future_A"], world.as_example()["primitive"]["learning_scale"]))
            first = ordered[0]
            second = next((world for world in ordered[1:] if world.oracle_action != first.oracle_action), ordered[1])
            examples.append({
                "class_size": len(worlds),
                "oracle_labels": sorted(labels),
                "common_oracle_actions": sorted(common_actions),
                "world_a": first.as_example(),
                "world_b": second.as_example(),
            })
    return examples


def _g_reconstruction_audit(groups: dict[tuple[float, ...], tuple[AuditWorld, ...]]) -> dict[str, object]:
    """Test whether a representation determines G on this finite family.

    This is a post-construction comparison to exact G, never an input to a
    representation.  Constant G within classes supports only a grid-scoped
    reconstruction claim.
    """
    mixed: list[tuple[float, tuple[AuditWorld, ...]]] = []
    maximum_span = 0.0
    for group in groups.values():
        gains = tuple(world.row.gain for world in group)
        span = max(gains) - min(gains)
        maximum_span = max(maximum_span, span)
        if span > CLASS_TOL:
            mixed.append((span, group))
    examples = []
    for span, group in sorted(mixed, key=lambda item: (-item[0], len(item[1])))[:5]:
        low = min(group, key=lambda world: world.row.gain)
        high = max(group, key=lambda world: world.row.gain)
        examples.append({"class_size": len(group), "G_span": span, "low_G_world": low.as_example(), "high_G_world": high.as_example()})
    return {
        "G_mixed_classes": len(mixed),
        "maximum_G_span_within_class": maximum_span,
        "determines_G_on_audited_grid": not mixed,
        "examples": examples,
    }


def audit_representation(worlds: tuple[AuditWorld, ...], representation: RepresentationName) -> dict[str, object]:
    """Run collision and recoverable-value audits for one representation."""
    grouped: dict[tuple[float, ...], list[AuditWorld]] = defaultdict(list)
    keys: dict[int, tuple[float, ...]] = {}
    for world in worlds:
        key = representation_key(world.row.primitive.scenario(), representation)
        grouped[key].append(world)
        keys[id(world)] = key
    groups = {key: tuple(value) for key, value in grouped.items()}
    action_for_key = {key: _choose_class_action(group) for key, group in groups.items()}
    label_mixed = {key: group for key, group in groups.items() if len({world.oracle_action for world in group}) > 1}
    incompatible = {
        key: group
        for key, group in groups.items()
        if not set.intersection(*(set(world.oracle_actions) for world in group))
    }
    class_regrets = {
        key: sum(world.regret(action_for_key[key]) for world in group)
        for key, group in groups.items()
    }
    unavoidable = {key: value for key, value in class_regrets.items() if value > CLASS_TOL}
    strata = {
        name: _metrics(tuple(world for world in worlds if world.row.regime == name), action_for_key, keys)
        for name in ("S2_positive_G_no_reversal", "S3_decision_relevant", "boundary")
    }
    examples = _collision_examples(incompatible)
    definitions = {
        "phi0": "no future information",
        "phi1": "total learning induced by E and D, derived from F(S,a)-S",
        "phi2": "localized DeltaS(E) and DeltaS(D)",
        "phi3": "localized DeltaS(E), DeltaS(D), and P1; no V1 or terminal assignment is evaluated in feature construction",
        "phi_alg": "(h,u,v), each derived from S0, P1, and the E/D transitions",
        "alg_h": "h only",
        "alg_u": "u only",
        "alg_v": "v only",
        "alg_hu": "(h,u)",
        "alg_hv": "(h,v)",
        "alg_uv": "(u,v)",
        "alg_h_v_minus_u": "(h,v-u), a requested lower-dimensional algebraic candidate",
        "alg_v_minus_u": "v-u, the C-region expression without h",
        "alg_h_plus_u": "h+u, the argument of the second max in G_alg",
        "phi_oracle": "control only: G=V1(S1(D))-V1(S1(E))",
    }
    report = {
        "representation": representation,
        "feature_definition": definitions[representation],
        "classes": len(groups),
        "largest_class": max((len(group) for group in groups.values()), default=0),
        "collision_audit": {
            "multiworld_classes": sum(len(group) > 1 for group in groups.values()),
            "innocuous_classes": sum(len(group) > 1 and key not in incompatible for key, group in groups.items()),
            "different_canonical_oracle_label_classes": len(label_mixed),
            "incompatible_oracle_decision_classes": len(incompatible),
            "unavoidable_positive_regret_classes": len(unavoidable),
            "unavoidable_regret_total": sum(unavoidable.values()),
            "unavoidable_regret_maximum_class": max(unavoidable.values(), default=0.0),
            "unavoidable_regret_distribution_by_class": _histogram(unavoidable.values()),
            "minimal_incompatible_examples": examples[:5],
        },
        "G_reconstruction_audit": _g_reconstruction_audit(groups),
        "recoverable_value": _metrics(worlds, action_for_key, keys),
        "strata_under_global_information_rule": strata,
        "finite_family_interpretation": (
            "Collision-free or full recovery applies only to the audited Phase-V grid; "
            "it is not a general HLS sufficiency theorem."
        ),
    }
    if representation == "phi_alg":
        report["analytic_rule"] = _algebraic_rule_metrics(worlds)
        report["analytic_rule_strata"] = {
            name: _algebraic_rule_metrics(tuple(world for world in worlds if world.row.regime == name))
            for name in ("S2_positive_G_no_reversal", "S3_decision_relevant", "boundary")
        }
    return report


@lru_cache(maxsize=1)
def run_information_audit() -> dict[str, object]:
    """Audit all existing primary Phase-V worlds without changing their grid."""
    worlds = audit_worlds(evaluate_primitives(primary_primitives()))
    return {
        "audited_family": "existing fixed Phase-V primary grid",
        "worlds": len(worlds),
        "common_decision_information": "S0, P0, beta (used for L; excluded from phi complexity)",
        "no_training": True,
        "algebraic_validation": algebraic_validation(worlds),
        "scalar_decision_validation": {
            "grid": scalar_grid_validation(worlds),
            "continuous": continuous_validation(),
            "adversarial": adversarial_validation(),
            "limit_cases": limit_case_validation(),
            "scope": (
                "The scalar decision hypothesis is tested only for L>0 and beta>0; "
                "controls outside that domain are descriptive."
            ),
        },
        "representations": {name: audit_representation(worlds, name) for name in ALL_REPRESENTATIONS},
    }
