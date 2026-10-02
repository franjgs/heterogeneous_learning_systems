"""Exact 3-worker x 2-competence ground truth for the documented G3 scenario.

G3 deliberately remains a fixed 3x2 instance.  It supplies two independent
routes to the organizational value of action-induced development: direct
terminal assignment evaluation and the assignment-sensitivity identities
documented in ``HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from random import Random

from .minimal_reference_scenario import EXACT_TOL


G3State = tuple[tuple[float, float], tuple[float, float], tuple[float, float]]
G3aAction = tuple[int, int]  # (A worker, B worker)
G3bAction = int  # B worker; the other workers execute A
G3DualAction = int  # A worker; the other workers execute B

G3A_ASSIGNMENTS: tuple[G3aAction, ...] = (
    (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1),
)
G3B_ASSIGNMENTS: tuple[G3bAction, ...] = (0, 1, 2)
G3DUAL_ASSIGNMENTS: tuple[G3DualAction, ...] = (0, 1, 2)


def _validate_state(state: G3State) -> None:
    if len(state) != 3 or any(len(row) != 2 for row in state):
        raise ValueError("G3 requires a 3x2 competence state")
    if not all(isfinite(value) and 0.0 <= value <= 1.0 for row in state for value in row):
        raise ValueError("competence values must be finite and lie in [0, 1]")


def _validate_scale(learning_scale: float) -> None:
    if not isfinite(learning_scale) or learning_scale < 0.0:
        raise ValueError("learning_scale must be finite and non-negative")


def _validate_g3a_action(action: G3aAction) -> None:
    if action not in G3A_ASSIGNMENTS:
        raise ValueError("G3a action must assign distinct workers to A and B")


def _validate_worker(worker: int) -> None:
    if worker not in G3B_ASSIGNMENTS:
        raise ValueError("worker must be 0, 1, or 2")


def learning_increment(skill: float, learning_scale: float) -> float:
    """Return the MIS diminishing learning-by-doing increment ``d_eta(s)``."""
    if not isfinite(skill) or not 0.0 <= skill <= 1.0:
        raise ValueError("skill must be finite and lie in [0, 1]")
    _validate_scale(learning_scale)
    return min(1.0, skill + learning_scale * (1.0 - skill) ** 2) - skill


def _updated(state: G3State, cells: tuple[tuple[int, int], ...], learning_scale: float) -> G3State:
    _validate_state(state)
    _validate_scale(learning_scale)
    rows = [list(row) for row in state]
    for worker, task in cells:
        rows[worker][task] += learning_increment(rows[worker][task], learning_scale)
    return tuple(tuple(row) for row in rows)  # type: ignore[return-value]


def transition_g3a(state: G3State, action: G3aAction, learning_scale: float) -> G3State:
    """Apply experience to the A and B competences executed in G3a."""
    _validate_g3a_action(action)
    return _updated(state, ((action[0], 0), (action[1], 1)), learning_scale)


def transition_g3b(state: G3State, b_worker: G3bAction, learning_scale: float) -> G3State:
    """Apply experience under load (2,1): one B worker and two A workers."""
    _validate_worker(b_worker)
    cells = tuple((worker, 1 if worker == b_worker else 0) for worker in range(3))
    return _updated(state, cells, learning_scale)


def transition_g3dual(state: G3State, a_worker: G3DualAction, learning_scale: float) -> G3State:
    """Apply experience under the A/B dual load (1,2)."""
    _validate_worker(a_worker)
    cells = tuple((worker, 0 if worker == a_worker else 1) for worker in range(3))
    return _updated(state, cells, learning_scale)


def reward_g3a(state: G3State, action: G3aAction) -> float:
    _validate_state(state)
    _validate_g3a_action(action)
    i, j = action
    return state[i][0] + state[j][1]


def reward_g3b(state: G3State, b_worker: G3bAction) -> float:
    _validate_state(state)
    _validate_worker(b_worker)
    return state[b_worker][1] + sum(state[worker][0] for worker in range(3) if worker != b_worker)


def reward_g3dual(state: G3State, a_worker: G3DualAction) -> float:
    _validate_state(state)
    _validate_worker(a_worker)
    return state[a_worker][0] + sum(state[worker][1] for worker in range(3) if worker != a_worker)


def value_g3a_direct(state: G3State) -> float:
    """Brute-force terminal assignment value for load (1,1)."""
    return max(reward_g3a(state, action) for action in G3A_ASSIGNMENTS)


def value_g3b_direct(state: G3State) -> float:
    """Brute-force terminal assignment value for load (2,1)."""
    return max(reward_g3b(state, worker) for worker in G3B_ASSIGNMENTS)


def value_g3dual_direct(state: G3State) -> float:
    """Brute-force terminal assignment value for load (1,2)."""
    return max(reward_g3dual(state, worker) for worker in G3DUAL_ASSIGNMENTS)


def value_g3a_algebraic(state: G3State) -> float:
    """Evaluate ``max_{r != s}(a_r+b_s)`` independently of action rewards."""
    _validate_state(state)
    return max(state[r][0] + state[s][1] for r in range(3) for s in range(3) if r != s)


def value_g3b_algebraic(state: G3State) -> float:
    """Evaluate ``sum_i a_i + max_j(b_j-a_j)``."""
    _validate_state(state)
    return sum(row[0] for row in state) + max(row[1] - row[0] for row in state)


def value_g3dual_algebraic(state: G3State) -> float:
    """Evaluate the A/B dual ``sum_i b_i + max_j(a_j-b_j)``."""
    _validate_state(state)
    return sum(row[1] for row in state) + max(row[0] - row[1] for row in state)


def development_g3a_direct(state: G3State, action: G3aAction, learning_scale: float) -> float:
    """Return direct ``V(F(S,x))-V(S)`` for G3a."""
    return value_g3a_direct(transition_g3a(state, action, learning_scale)) - value_g3a_direct(state)


def development_g3b_direct(state: G3State, b_worker: G3bAction, learning_scale: float) -> float:
    """Return direct ``V(F(S,x))-V(S)`` for G3b."""
    return value_g3b_direct(transition_g3b(state, b_worker, learning_scale)) - value_g3b_direct(state)


def development_g3dual_direct(state: G3State, a_worker: G3DualAction, learning_scale: float) -> float:
    """Return direct ``V(F(S,x))-V(S)`` for the (1,2) dual."""
    return value_g3dual_direct(transition_g3dual(state, a_worker, learning_scale)) - value_g3dual_direct(state)


def development_g3a_algebraic(state: G3State, action: G3aAction, learning_scale: float) -> float:
    """Evaluate the documented G3a maximum/gap identity independently."""
    _validate_state(state)
    _validate_g3a_action(action)
    i, j = action
    k = next(worker for worker in range(3) if worker not in action)
    alpha_i = learning_increment(state[i][0], learning_scale)
    beta_j = learning_increment(state[j][1], learning_scale)
    value = value_g3a_algebraic(state)
    gap_ij = value - (state[i][0] + state[j][1])
    gap_ik = value - (state[i][0] + state[k][1])
    gap_kj = value - (state[k][0] + state[j][1])
    return max(0.0, alpha_i + beta_j - gap_ij, alpha_i - gap_ik, beta_j - gap_kj)


def development_g3b_algebraic(state: G3State, b_worker: G3bAction, learning_scale: float) -> float:
    """Evaluate the documented comparative-advantage identity for load (2,1)."""
    _validate_state(state)
    _validate_worker(b_worker)
    q = tuple(row[1] - row[0] for row in state)
    alpha = tuple(learning_increment(row[0], learning_scale) for row in state)
    beta_j = learning_increment(state[b_worker][1], learning_scale)
    a_increment = sum(alpha[worker] for worker in range(3) if worker != b_worker)
    adjusted_other = max(q[worker] - alpha[worker] for worker in range(3) if worker != b_worker)
    return a_increment + max(q[b_worker] + beta_j, adjusted_other) - max(q)


def development_g3dual_algebraic(state: G3State, a_worker: G3DualAction, learning_scale: float) -> float:
    """Evaluate the explicit A/B dual comparative-advantage identity."""
    _validate_state(state)
    _validate_worker(a_worker)
    p = tuple(row[0] - row[1] for row in state)
    alpha_i = learning_increment(state[a_worker][0], learning_scale)
    beta = tuple(learning_increment(row[1], learning_scale) for row in state)
    b_increment = sum(beta[worker] for worker in range(3) if worker != a_worker)
    adjusted_other = max(p[worker] - beta[worker] for worker in range(3) if worker != a_worker)
    return b_increment + max(p[a_worker] + alpha_i, adjusted_other) - max(p)


@dataclass(frozen=True)
class G3IdentityAudit:
    """In-memory implementation audit; it deliberately writes no result artefact."""

    states: int
    action_evaluations: int
    max_residual_g3a: float
    max_residual_g3b: float
    max_residual_dual: float


def random_identity_audit(*, states: int = 1_000, seed: int = 20261002) -> G3IdentityAudit:
    """Check direct and algebraic development values on reproducible random states."""
    if states <= 0:
        raise ValueError("states must be positive")
    rng = Random(seed)
    maxima = [0.0, 0.0, 0.0]
    for _ in range(states):
        state: G3State = tuple(tuple(rng.random() for _ in range(2)) for _ in range(3))  # type: ignore[assignment]
        scale = rng.uniform(0.0, 4.0)
        for action in G3A_ASSIGNMENTS:
            maxima[0] = max(maxima[0], abs(development_g3a_direct(state, action, scale) - development_g3a_algebraic(state, action, scale)))
        for worker in G3B_ASSIGNMENTS:
            maxima[1] = max(maxima[1], abs(development_g3b_direct(state, worker, scale) - development_g3b_algebraic(state, worker, scale)))
            maxima[2] = max(maxima[2], abs(development_g3dual_direct(state, worker, scale) - development_g3dual_algebraic(state, worker, scale)))
    return G3IdentityAudit(
        states=states,
        action_evaluations=states * (len(G3A_ASSIGNMENTS) + len(G3B_ASSIGNMENTS) + len(G3DUAL_ASSIGNMENTS)),
        max_residual_g3a=maxima[0],
        max_residual_g3b=maxima[1],
        max_residual_dual=maxima[2],
    )
