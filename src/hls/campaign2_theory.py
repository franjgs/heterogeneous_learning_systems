"""C2.0 pure diagnostics, not a campaign runner or a new decision policy.

No RNG, seeds, file output, cross-problem loop or statistical analysis lives here.
The frozen operator supplies every prospective value and selected action.
"""

from dataclasses import dataclass
from math import isfinite, log

from .campaign1_protocol import PARAMETERS
from .discover_develop_v2 import mis_v2_transition
from .discover_v0 import (
    DEFAULT_SIGMA, EXACT_TOL, JOINT_ACTIONS, JointAction, State,
    ces_reward, production_inputs, validate_state,
)
from .finite_problem_belief import (
    BeliefVector, ProspectivePolicyMode, canonical_model, choose_prospective_action,
    finite_bayes_update, hypothesis_means, prospective_action_values, validate_belief,
)
from .problem_geometry import Problem, validate_problem
from .small_problem_world import HYPOTHESIS_REPERTOIRE


def belief_entropy(belief: BeliefVector) -> float:
    """Unnormalized Shannon entropy in nats; 0 log 0 is zero."""
    b = validate_belief(belief, len(belief))
    return -sum(p * log(p) for p in b if p > 0.0)


def _snapshot(state, belief, hypotheses):
    # Deep immutable copies prevent branch writes and mutable-caller aliasing.
    s = tuple(tuple(row) for row in state)
    validate_state(s)
    model, b = canonical_model(hypotheses, belief)
    return s, b, model


def _values(state, belief, model, mode, remaining=2):
    information, development = mode.value
    return prospective_action_values(
        state, belief, model, remaining=remaining, eta=PARAMETERS["eta"],
        anticipate_information=information, anticipate_development=development,
    )


def _first(values):
    maximum = max(values.values())
    return next(x for x in JOINT_ACTIONS if abs(values[x] - maximum) <= EXACT_TOL)


@dataclass(frozen=True)
class StructuralDescriptors:
    entropy: float
    disagreement: float
    disagreement_normalized: float | None
    myopic_regret: float
    capability_headroom: float
    belief_myopic_action: JointAction
    hypothesis_myopic_actions: tuple[JointAction, ...]


def structural_descriptors(state, belief, hypotheses=HYPOTHESIS_REPERTOIRE):
    """Agent-model structural diagnostics; no true problem or realized regret."""
    s, b, model = _snapshot(state, belief, hypotheses)
    immediate = _values(s, b, model, ProspectivePolicyMode.NONE, remaining=1)
    myopic = _first(immediate)
    hypothesis_actions = tuple(
        _first(_values(s, tuple(float(j == m) for j in range(len(b))), model,
                       ProspectivePolicyMode.NONE, remaining=1))
        for m in range(len(b))
    )
    denominator = sum(b[m] * b[n] for m in range(len(b)) for n in range(m + 1, len(b)))
    disagreement = sum(
        b[m] * b[n] for m in range(len(b)) for n in range(m + 1, len(b))
        if hypothesis_actions[m] != hypothesis_actions[n]
    )
    regret = sum(
        b[m] * (hypothesis_means(s, hypothesis_actions[m], model)[m]
                - hypothesis_means(s, myopic, model)[m])
        for m in range(len(b))
    )
    return StructuralDescriptors(
        belief_entropy(b), disagreement,
        disagreement / denominator if denominator > 0.0 else None,
        regret, sum(1.0 - value for row in s for value in row), myopic, hypothesis_actions,
    )


@dataclass(frozen=True)
class Opportunity:
    action: JointAction
    immediate: float
    cost: float
    V_D: float
    V_I: float
    V_ID: float
    A_D: float
    A_I: float
    A_ID: float
    coupling_residual: float
    # Explicit field order Q00,Q10,Q01,Q11, not enum/index inference.
    operator_values: tuple[float, float, float, float]


@dataclass(frozen=True)
class OpportunityLandscape:
    baseline_continuation: float
    belief_myopic_action: JointAction
    candidates: tuple[Opportunity, ...]


def opportunity_landscape(state, belief, hypotheses=HYPOTHESIS_REPERTOIRE):
    """Two-stage internal decomposition over all 64 frozen actions.

    Continuations are Q-g from the authoritative operator, not a second
    quadrature implementation. Subtraction/reconstruction can round by ulps.
    This diagnostic is explicitly two-stage, not a terminal Q_1 decomposition.
    """
    s, b, model = _snapshot(state, belief, hypotheses)
    g = _values(s, b, model, ProspectivePolicyMode.NONE, remaining=1)
    x00 = _first(g)
    v0 = max(g.values())
    modes = (ProspectivePolicyMode.NONE, ProspectivePolicyMode.INFORMATION_ONLY,
             ProspectivePolicyMode.DEVELOPMENT_ONLY, ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT)
    q00, q10, q01, q11 = (_values(s, b, model, mode) for mode in modes)
    rows = []
    for x in JOINT_ACTIONS:
        vd, vi, vid = q01[x] - g[x], q10[x] - g[x], q11[x] - g[x]
        ad, ai, aid = vd - v0, vi - v0, vid - v0
        rows.append(Opportunity(x, g[x], g[x00] - g[x], vd, vi, vid, ad, ai, aid,
                                aid - ai - ad, (q00[x], q10[x], q01[x], q11[x])))
    return OpportunityLandscape(v0, x00, tuple(rows))


@dataclass(frozen=True)
class RealDecision:
    state_before: State
    belief_before: BeliefVector
    action: JointAction
    epsilon: float
    mu_true: float
    observation: float
    belief_after: BeliefVector
    state_after: State


@dataclass(frozen=True)
class CounterfactualBranch:
    continuation_policy: ProspectivePolicyMode
    steps: tuple[RealDecision, RealDecision]
    production_sum: float


@dataclass(frozen=True)
class TwoDecisionCounterfactual:
    prospective: CounterfactualBranch
    baseline: CounterfactualBranch
    delta_production: float


def _real_decision(state, belief, action, true_problem, epsilon, model):
    mu_true = ces_reward(production_inputs(state, action), true_problem)
    observation = mu_true + DEFAULT_SIGMA * epsilon
    posterior = finite_bayes_update(belief, observation, hypothesis_means(state, action, model), DEFAULT_SIGMA)
    next_state = mis_v2_transition(state, action, enabled=True, eta=PARAMETERS["eta"])
    return RealDecision(state, belief, action, epsilon, mu_true, observation, posterior, next_state)


def two_decision_counterfactual(
    state, belief, true_problem: Problem, *, remaining: int,
    policy_mode: ProspectivePolicyMode, innovations: tuple[float, float],
    branch_order: tuple[str, str] = ("prospective", "baseline"),
) -> TwoDecisionCounterfactual:
    """Force pi_ab versus pi_00 once; BOTH then replan using pi_ab.

    Exactly two real rewards at fixed true z, with real Bayes and MIS-v2 on
    both steps. Caller supplies innovations (not observations or seeds).
    Rejects terminal states; no new problem/reset or cross-boundary rollout.
    """
    if type(remaining) is not int or remaining not in (2, 3):
        raise ValueError("two real decisions must remain within the same H=3 problem")
    if policy_mode not in (ProspectivePolicyMode.INFORMATION_ONLY,
                           ProspectivePolicyMode.DEVELOPMENT_ONLY,
                           ProspectivePolicyMode.INFORMATION_AND_DEVELOPMENT):
        raise ValueError("counterfactual policy must be Q10, Q01 or Q11")
    eps = tuple(innovations)
    if len(eps) != 2 or any(not isfinite(x) for x in eps):
        raise ValueError("exactly two finite standard-normal innovations are required")
    if tuple(branch_order) not in (("prospective", "baseline"), ("baseline", "prospective")):
        raise ValueError("evaluate each branch exactly once")
    s, b, model = _snapshot(state, belief, HYPOTHESIS_REPERTOIRE)
    problem = validate_problem(true_problem)
    forced = {
        "prospective": choose_prospective_action(s, b, model, remaining=remaining,
            policy_mode=policy_mode, eta=PARAMETERS["eta"])[0],
        "baseline": choose_prospective_action(s, b, model, remaining=remaining,
            policy_mode=ProspectivePolicyMode.NONE, eta=PARAMETERS["eta"])[0],
    }
    branches = {}
    for name in branch_order:
        first = _real_decision(s, b, forced[name], problem, eps[0], model)
        second_action = choose_prospective_action(
            first.state_after, first.belief_after, model, remaining=remaining - 1,
            policy_mode=policy_mode, eta=PARAMETERS["eta"],
        )[0]
        second = _real_decision(first.state_after, first.belief_after, second_action,
                                problem, eps[1], model)
        branches[name] = CounterfactualBranch(policy_mode, (first, second), first.mu_true + second.mu_true)
    a, baseline = branches["prospective"], branches["baseline"]
    return TwoDecisionCounterfactual(a, baseline, a.production_sum - baseline.production_sum)
