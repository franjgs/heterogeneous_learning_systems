"""Pure functions for the CR0--CR4 minimal competence-evolution audit.

The functions implement only the explicitly documented two-learner/two-task
analytical cases. They are not a general HLS controller, benchmark, or M1.
"""

from __future__ import annotations

from math import exp

import numpy as np


def division_values(competence: np.ndarray, lambda_cost: float = 0.0, costs: np.ndarray | None = None) -> tuple[float, float]:
    """Return ``(R_D, R_X)`` for ``[[A1, A2], [B1, B2]]`` competence."""
    if competence.shape != (2, 2):
        raise ValueError("competence must have shape (2, 2): rows A,B; columns 1,2.")
    effective = competence if costs is None else competence - lambda_cost * costs
    return float(effective[0, 0] + effective[1, 1]), float(effective[0, 1] + effective[1, 0])


def division_gap(competence: np.ndarray, lambda_cost: float = 0.0, costs: np.ndarray | None = None) -> float:
    """Return ``Delta = R_D - R_X``."""
    r_d, r_x = division_values(competence, lambda_cost, costs)
    return r_d - r_x


def complementary_switch_gain(delta_0: float, x: float, y: float) -> float:
    """Return ``G(x,y) = [x+y-delta_0]_+`` for off-diagonal investments."""
    if delta_0 <= 0 or x < 0 or y < 0:
        raise ValueError("delta_0 must be positive and investments must be non-negative.")
    return max(x + y - delta_0, 0.0)


def sigmoid(value: float) -> float:
    """Numerically stable logistic function."""
    if value >= 0:
        return 1.0 / (1.0 + exp(-value))
    exp_value = exp(value)
    return exp_value / (1.0 + exp_value)


def symmetric_equilibrium(eta: float, depreciation: float) -> float:
    """Return ``c* = eta / (eta + 2 delta)`` for positive parameters."""
    if eta <= 0 or depreciation <= 0:
        raise ValueError("eta and depreciation must be strictly positive.")
    return eta / (eta + 2.0 * depreciation)


def beta_critical(eta: float, depreciation: float) -> float:
    """Return the local-stability threshold ``(eta+2delta)^2/(4delta eta)``."""
    if eta <= 0 or depreciation <= 0:
        raise ValueError("eta and depreciation must be strictly positive.")
    return (eta + 2.0 * depreciation) ** 2 / (4.0 * depreciation * eta)


def specialization_rhs(state: np.ndarray, eta: float, depreciation: float, beta: float) -> np.ndarray:
    """Return the 2x2 learning-by-doing dynamics in order ``A1,B2,A2,B1``."""
    if state.shape != (4,):
        raise ValueError("state must be ordered as (A1, B2, A2, B1).")
    a1, b2, a2, b1 = state
    delta = a1 + b2 - a2 - b1
    r_d = sigmoid(beta * delta)
    return np.array(
        [
            eta * r_d * (1.0 - a1) - depreciation * a1,
            eta * r_d * (1.0 - b2) - depreciation * b2,
            eta * (1.0 - r_d) * (1.0 - a2) - depreciation * a2,
            eta * (1.0 - r_d) * (1.0 - b1) - depreciation * b1,
        ],
        dtype=float,
    )


def specialization_jacobian_at_symmetric(eta: float, depreciation: float, beta: float) -> np.ndarray:
    """Return the analytic 4x4 Jacobian at the symmetric equilibrium."""
    c_star = symmetric_equilibrium(eta, depreciation)
    loss = eta / 2.0 + depreciation
    direction = np.array([1.0, 1.0, -1.0, -1.0])
    gain = eta * beta * (1.0 - c_star) / 4.0
    return -loss * np.eye(4) + gain * np.outer(direction, direction)


def specialization_eigenvalues(eta: float, depreciation: float, beta: float) -> np.ndarray:
    """Return sorted Jacobian eigenvalues at the symmetric equilibrium."""
    return np.linalg.eigvalsh(specialization_jacobian_at_symmetric(eta, depreciation, beta))


def rk4_specialization(initial: np.ndarray, eta: float, depreciation: float, beta: float, dt: float, steps: int) -> np.ndarray:
    """Integrate the minimal ODE with fixed-step RK4 and return all states."""
    if dt <= 0 or steps <= 0:
        raise ValueError("dt and steps must be positive.")
    trajectory = np.empty((steps + 1, 4), dtype=float)
    trajectory[0] = initial
    for index in range(steps):
        current = trajectory[index]
        k1 = specialization_rhs(current, eta, depreciation, beta)
        k2 = specialization_rhs(current + dt * k1 / 2.0, eta, depreciation, beta)
        k3 = specialization_rhs(current + dt * k2 / 2.0, eta, depreciation, beta)
        k4 = specialization_rhs(current + dt * k3, eta, depreciation, beta)
        trajectory[index + 1] = current + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    return trajectory


def rebalancing_effective_cost(y: float, d_0: float, a: float, v: float, g: float) -> float:
    """Return ``Q(y)=a(d0-y)+y^2/(2v)+g y/v`` for ``0<=y<=d0``."""
    if not 0 <= y <= d_0:
        raise ValueError("y must lie in [0, d_0].")
    if d_0 < 0 or a < 0 or v <= 0 or g <= 0:
        raise ValueError("require d_0,a >= 0 and v,g > 0.")
    return a * (d_0 - y) + y**2 / (2.0 * v) + g * y / v


def rebalancing_solution(d_0: float, a: float, v: float, g: float) -> tuple[float, float, str, float, float]:
    """Return ``(x*,y*,regime,Q*,H*)`` for the two-actuator minimum."""
    if d_0 < 0 or a < 0 or v <= 0 or g <= 0:
        raise ValueError("require d_0,a >= 0 and v,g > 0.")
    y_star = min(max(a * v - g, 0.0), d_0)
    x_star = d_0 - y_star
    if y_star == 0.0:
        regime = "TRAIN"
    elif y_star == d_0:
        regime = "ROUTE"
    else:
        regime = "MIXED"
    q_star = rebalancing_effective_cost(y_star, d_0, a, v, g)
    return x_star, y_star, regime, q_star, q_star / g


def numeric_rebalancing_argmin(d_0: float, a: float, v: float, g: float, resolution: int = 10001) -> tuple[float, float]:
    """Return a grid argmin of Q for independent numerical verification."""
    if resolution < 3:
        raise ValueError("resolution must be at least 3.")
    grid = np.linspace(0.0, d_0, resolution)
    values = a * (d_0 - grid) + grid**2 / (2.0 * v) + g * grid / v
    index = int(np.argmin(values))
    return float(grid[index]), float(values[index])
