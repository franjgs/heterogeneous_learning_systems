"""Structural diagnostics over the frozen G3-H evaluator.

This module derives only reward differences, G3-H transitions, and the
existing local development quantity.  Dynamic value is retained exclusively
as an oracle label; it is never part of a diagnostic feature vector.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from random import Random
from typing import Iterable, Literal

from .g3_h_organizational_value import G3HLearningProfile
from .g3_h_regime_map import G3HPointEvaluation, REGIME_TOL, evaluate_point
from .g3_h_regime_search import INTERIOR_EPSILON, _eta, _interior_state, _learning_profile
from .g3_organizational_value import G3A_ASSIGNMENTS, G3aAction, reward_g3a


Condition = Literal["homogeneous", "heterogeneous"]
MAIN_REGIMES = (
    "R0_USE_SUFFICIENT",
    "R1_LOCAL_NECESSARY_SUFFICIENT",
    "R2_LOCAL_INSUFFICIENT",
)


def action_name(action: G3aAction) -> str:
    """Human-readable, 1-based assignment label."""
    return f"({action[0] + 1},{action[1] + 1})"


def flat_state(state: tuple[tuple[float, float], ...]) -> tuple[float, ...]:
    return tuple(value for worker in state for value in worker)


def action_diagnostics(evaluation: G3HPointEvaluation) -> list[dict[str, object]]:
    """Return exact Beam-1 × Beam-2 local diagnostics for every action pair.

    For a current-use optimizer ``bar`` and action ``x``, the quantities are
    ``g=R(S,bar)-R(S,x)``, ``rho=(R(S',x)-R(S,x))-(R(S',bar)-R(S,bar))`` and
    ``m=g-rho=R(S',bar)-R(S',x)``.  The final equality is checked directly
    here rather than assumed.
    """
    by_action = {record.action: record for record in evaluation.actions}
    rows: list[dict[str, object]] = []
    for record in evaluation.actions:
        successor = record.successor
        for reference in sorted(evaluation.optimal_use):
            ref_record = by_action[reference]
            g = ref_record.reward - record.reward
            rho = (
                reward_g3a(successor, record.action) - record.reward
                - (reward_g3a(successor, reference) - ref_record.reward)
            )
            residual = g - rho
            successor_residual = reward_g3a(successor, reference) - reward_g3a(successor, record.action)
            if abs(residual - successor_residual) > REGIME_TOL:
                raise AssertionError("residual-margin identity failed")
            rows.append(
                {
                    "action": action_name(record.action),
                    "reference_use_action": action_name(reference),
                    "R": record.reward,
                    "D": record.development,
                    "M": record.local_value,
                    "Q_oracle_label": record.dynamic_value,
                    "successor": json.dumps(flat_state(successor)),
                    "g": g,
                    "rho": rho,
                    "m": residual,
                    "successor_reward_residual": successor_residual,
                    "immediate_crossing": residual < -REGIME_TOL,
                    "is_use_optimal": record.action in evaluation.optimal_use,
                    "is_local_optimal": record.action in evaluation.optimal_local,
                    "is_oracle_optimal": record.action in evaluation.optimal_dynamic,
                }
            )
    return rows


def local_feature_row(evaluation: G3HPointEvaluation) -> dict[str, object]:
    """Return point-level local quantities; intentionally exclude Q values."""
    diagnostics = action_diagnostics(evaluation)
    by_action: dict[str, list[dict[str, object]]] = {}
    for row in diagnostics:
        by_action.setdefault(str(row["action"]), []).append(row)
    row: dict[str, object] = {
        "state": json.dumps(flat_state(evaluation.state)),
        "eta": json.dumps(tuple(evaluation.learning_profile)),
        "A_U": json.dumps(sorted(action_name(a) for a in evaluation.optimal_use)),
        "A_L": json.dumps(sorted(action_name(a) for a in evaluation.optimal_local)),
        "A_Q_oracle_label": json.dumps(sorted(action_name(a) for a in evaluation.optimal_dynamic)),
        "regime_oracle_label": evaluation.regime,
        "R2_REVERSION": evaluation.r2_reversion,
        "regret_U_oracle_label": evaluation.regret_use,
        "regret_L_oracle_label": evaluation.regret_local,
        "any_immediate_crossing": any(bool(item["immediate_crossing"]) for item in diagnostics),
        "crossing_pair_count": sum(bool(item["immediate_crossing"]) for item in diagnostics),
    }
    for action in G3A_ASSIGNMENTS:
        name = action_name(action)
        record = next(item for item in evaluation.actions if item.action == action)
        matching = by_action[name]
        row[f"R_{name}"] = record.reward
        row[f"D_{name}"] = record.development
        row[f"M_{name}"] = record.local_value
        row[f"g_{name}"] = record.operational_gap
        row[f"rho_min_{name}"] = min(float(item["rho"]) for item in matching)
        row[f"m_min_{name}"] = min(float(item["m"]) for item in matching)
    return row


@dataclass(frozen=True)
class Population:
    condition: Condition
    seed: int
    generated: int
    regime_counts: dict[str, int]
    reversion_count: int
    retained: tuple[G3HPointEvaluation, ...]


def generate_population(
    *,
    condition: Condition,
    seed: int,
    quota_per_regime: int,
    maximum_samples: int,
) -> Population:
    """Sample first, then retain equal regime quotas for diagnosis only."""
    if quota_per_regime <= 0 or maximum_samples <= 0:
        raise ValueError("quotas and maximum_samples must be positive")
    rng = Random(seed)
    retained: dict[str, list[G3HPointEvaluation]] = {regime: [] for regime in MAIN_REGIMES}
    counts = {regime: 0 for regime in MAIN_REGIMES}
    reversion_count = 0
    for generated in range(1, maximum_samples + 1):
        evaluation = evaluate_point(_interior_state(rng), _learning_profile(rng, condition))
        counts[evaluation.regime] += 1
        reversion_count += evaluation.r2_reversion
        if len(retained[evaluation.regime]) < quota_per_regime:
            retained[evaluation.regime].append(evaluation)
        if all(len(retained[regime]) == quota_per_regime for regime in MAIN_REGIMES):
            break
    return Population(
        condition=condition,
        seed=seed,
        generated=generated,
        regime_counts=counts,
        reversion_count=reversion_count,
        retained=tuple(item for regime in MAIN_REGIMES for item in retained[regime]),
    )


def exact_identity_certificate(evaluation: G3HPointEvaluation) -> bool:
    """Exact boundary certificate: every action leaves the state unchanged."""
    return all(record.successor == evaluation.state for record in evaluation.actions)


def local_rule_flags(evaluation: G3HPointEvaluation) -> dict[str, bool]:
    """Auditable candidate rules, all formed without oracle quantities."""
    diagnostics = action_diagnostics(evaluation)
    no_crossing = not any(bool(row["immediate_crossing"]) for row in diagnostics)
    use_local_overlap = bool(evaluation.optimal_use & evaluation.optimal_local)
    unique_use = len(evaluation.optimal_use) == 1
    return {
        "all_action_transitions_identity": exact_identity_certificate(evaluation),
        "no_immediate_crossing": no_crossing,
        "unique_use_and_no_immediate_crossing": unique_use and no_crossing,
        "use_local_optimal_overlap": use_local_overlap,
        "unique_local_and_no_immediate_crossing": len(evaluation.optimal_local) == 1 and no_crossing,
    }


def feature_columns() -> tuple[str, ...]:
    """Minimal nonredundant local vector used in the shallow diagnostic probe."""
    columns: list[str] = []
    for action in G3A_ASSIGNMENTS:
        name = action_name(action)
        # g and M are omitted: g=max(R)-R and M=R+D exactly.
        columns.extend((f"R_{name}", f"D_{name}", f"rho_min_{name}"))
    return tuple(columns)


def iter_action_rows(population: Population) -> Iterable[dict[str, object]]:
    for point_id, evaluation in enumerate(population.retained):
        for row in action_diagnostics(evaluation):
            yield {"point_id": point_id, "condition": population.condition, **row}
