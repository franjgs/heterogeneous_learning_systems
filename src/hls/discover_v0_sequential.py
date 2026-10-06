"""Sequential audit of the unchanged DISCOVER-v0 belief-state DP."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import log

from .discover_v0 import (
    DEFAULT_HORIZON, DEFAULT_PRIOR, DEFAULT_QUADRATURE_ORDER, DEFAULT_SIGMA,
    EXACT_TOL, JOINT_ACTIONS, JointAction, State, THETA_1, THETA_2,
    bayes_update, gaussian_quadrature_nodes, means,
)


def entropy(belief: float) -> float:
    return 0.0 if belief <= 0.0 or belief >= 1.0 else -belief * log(belief) - (1.0 - belief) * log(1.0 - belief)


@dataclass(frozen=True)
class Decision:
    remaining: int
    belief: float
    actions: tuple[JointAction, ...]
    value: float
    immediate: float
    immediate_max: float
    experiment_cost: float
    future: float
    noinfo: float
    voi: float
    bellman_residual: float
    baseline_residual: float


class SequentialDiscoverAudit:
    """Exact numerical audit wrapper using DISCOVER-v0's same quadrature rule."""

    def __init__(self, state: State, *, horizon: int = DEFAULT_HORIZON, prior: float = DEFAULT_PRIOR, sigma: float = DEFAULT_SIGMA, quadrature_order: int = DEFAULT_QUADRATURE_ORDER, theta_1: tuple[float, float] = THETA_1, theta_2: tuple[float, float] = THETA_2):
        self.state, self.horizon, self.prior, self.sigma, self.order = state, horizon, prior, sigma, quadrature_order
        self.theta_1, self.theta_2 = theta_1, theta_2
        self.action_means = {action: means(state, action, theta_1=theta_1, theta_2=theta_2) for action in JOINT_ACTIONS}

    def immediate_values(self, belief: float) -> dict[JointAction, float]:
        return {action: belief * mu_1 + (1.0 - belief) * mu_2 for action, (mu_1, mu_2) in self.action_means.items()}

    @lru_cache(maxsize=None)
    def value(self, remaining: int, belief: float) -> float:
        if remaining == 0:
            return 0.0
        return max(self.action_values(remaining, belief).values())

    def continuation(self, remaining: int, belief: float, action: JointAction) -> float:
        if remaining == 1:
            return 0.0
        mu_1, mu_2 = self.action_means[action]
        total = 0.0
        for mean, mixture_mass in ((mu_1, belief), (mu_2, 1.0 - belief)):
            if mixture_mass == 0.0:
                continue
            for observation, weight in gaussian_quadrature_nodes(mean, self.sigma, self.order):
                total += mixture_mass * weight * self.value(remaining - 1, bayes_update(belief, observation, mu_1, mu_2, self.sigma))
        return total

    def action_values(self, remaining: int, belief: float) -> dict[JointAction, float]:
        immediate = self.immediate_values(belief)
        return {action: reward + self.continuation(remaining, belief, action) for action, reward in immediate.items()}

    def decision(self, remaining: int, belief: float) -> Decision:
        values = self.action_values(remaining, belief)
        value = max(values.values())
        actions = tuple(action for action in JOINT_ACTIONS if value - values[action] <= EXACT_TOL)
        action = actions[0]
        immediate = self.immediate_values(belief)[action]
        immediate_max = max(self.immediate_values(belief).values())
        future = self.continuation(remaining, belief, action)
        noinfo = (remaining - 1) * immediate_max
        cost = immediate_max - immediate
        voi = future - noinfo
        return Decision(remaining, belief, actions, value, immediate, immediate_max, cost, future, noinfo, voi, value - (immediate + future), (value - (immediate_max + noinfo)) - (-cost + voi))

    def child_nodes(self, decision: Decision) -> tuple[tuple[float, float], ...]:
        """Return posterior belief and probability mass under tie-symmetric policy."""
        if decision.remaining == 0:
            return ()
        children: dict[float, float] = {}
        action_mass = 1.0 / len(decision.actions)
        for action in decision.actions:
            mu_1, mu_2 = self.action_means[action]
            for mean, mixture_mass in ((mu_1, decision.belief), (mu_2, 1.0 - decision.belief)):
                if mixture_mass == 0.0:
                    continue
                for observation, weight in gaussian_quadrature_nodes(mean, self.sigma, self.order):
                    posterior = bayes_update(decision.belief, observation, mu_1, mu_2, self.sigma)
                    children[posterior] = children.get(posterior, 0.0) + action_mass * mixture_mass * weight
        return tuple(children.items())

    def audit(self) -> tuple[list[tuple[float, Decision]], list[dict[str, float]]]:
        """Return all visited decision nodes and deterministic pre-action moments."""
        nodes = [(self.prior, 1.0)]
        all_nodes: list[tuple[float, Decision]] = []
        moments: list[dict[str, float]] = []
        for time in range(self.horizon):
            remaining = self.horizon - time
            decisions = [(mass, self.decision(remaining, belief)) for belief, mass in nodes]
            all_nodes.extend(decisions)
            moments.append({
                "time": float(time), "mass": sum(mass for mass, _ in decisions),
                "belief": sum(mass * decision.belief for mass, decision in decisions),
                "entropy": sum(mass * entropy(decision.belief) for mass, decision in decisions),
                "abs_center": sum(mass * abs(decision.belief - 0.5) for mass, decision in decisions),
                "reward": sum(mass * decision.immediate for mass, decision in decisions),
                "experiment_cost": sum(mass * decision.experiment_cost for mass, decision in decisions),
                "voi": sum(mass * decision.voi for mass, decision in decisions),
            })
            next_nodes: dict[float, float] = {}
            for mass, decision in decisions:
                for posterior, child_mass in self.child_nodes(decision):
                    next_nodes[posterior] = next_nodes.get(posterior, 0.0) + mass * child_mass
            nodes = list(next_nodes.items())
        return all_nodes, moments
