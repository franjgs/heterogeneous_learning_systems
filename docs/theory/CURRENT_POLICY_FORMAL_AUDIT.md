# Formal audit of the CURRENT HLS decision operator

## 1. Executive conclusion and inspection boundary

Audited repository HEAD: `10f81b7`, with a clean worktree before this task.
Campaign 1 execution is `ac9d421`; its protocol is `bcc3ad8` and its test range
is `05b86cb`. This document records code inspection, not a new experiment.
No controller, physics, protocol, scenario, or historical artifact was changed.

CURRENT, meaning the decision rule used by Campaign 1 FULL, is a two-stage,
receding-horizon belief-state look-ahead. It prospectively propagates **both**
capability state and belief. Future actions are optimized separately for each
quadrature observation's posterior, on the candidate action's developed state.
It uses three-node Gauss–Hermite integration per positive-probability hypothesis.
It does not recurse over the full three-decision problem horizon.

Accordingly CURRENT is information-aware and development-aware within its
two-stage approximation. Those descriptions refer to prospective computation,
not merely real Bayesian updates or real learning. No experimental claim that
a particular action actually sacrifices current reward for information or
development is made here.

## 2. Actual Campaign 1 FULL call graph

Source anchors below are line numbers at the audited HEAD.

```text
experiments/synthetic/campaign1/run.py
  main (176–225) -> _task (118–163) -> run_condition (100–115)
    FULL -> run_finite_problem_sequence(mode=DISCOVER_DEVELOP)
src/hls/finite_problem_belief.py
  run_finite_problem_sequence (257–314)
    remaining = horizon - step_id
    finite_choose_dynamic_action_v2 (194–222)
      canonical_model -> ordered hypotheses and aligned belief
      for each of 64 JOINT_ACTIONS:
        hypothesis_means -> production_inputs -> ces_reward
        expected_reward
        if remaining == 1: immediate only
        otherwise:
          mis_v2_transition -> candidate next S
          for each hypothesis and its three quadrature observations:
            finite_bayes_update using current S/action predictions
            _best_immediate(next S, posterior) -> maximize over 64 actions
      choose first tolerance-optimal action in JOINT_ACTIONS order
    generate true mean and noisy observation at pre-development S
    update real belief -> update real S -> retain step -> repeat
```

No class implements an additional planner: `FiniteBeliefStep` (241–254) is a
record. The UNKNOWN selector receives S, b, hypothesis family, remaining,
develop, and eta; it does not receive true z, the next problem, history labels,
C/N/M, cumulative exposure, or future observations from the actual RNG.

## 3. Immediate objective and reward semantics

Let the finite internal hypotheses be `z_hat_m`, with aligned belief `b_m`.
For the declared action set A, define

```text
Y_k(S,X) = sum_i X[i,k] S[i,k]
mu_m(S,X) = R_z_hat_m(S,X)
g(b,S,X) = sum_m b_m mu_m(S,X).
```

`hypothesis_means` (80–82) and `expected_reward` (85–89) implement this exact
finite weighted sum. CES is `(sum_k z_k Y_k^rho)^(1/rho)` with rho=.5
(`discover_v0.py:95–115`). KNOWN-Z instead uses `R_z*(S,X)` directly.

The planner optimizes predicted expected latent production summed over its
planning window. It does not optimize a sampled noisy reward or directly
access the external `mu_true` in UNKNOWN mode. The real simulator subsequently
computes `mu_true=R_z*(S,X)` and `r=mu_true+.10 epsilon`, then accumulates
`mu_true` (`finite_problem_belief.py:298–306`). In a misspecified problem,
`g` need not equal `mu_true`. Noise is zero-mean and contributes no immediate
utility term; sigma enters the predictive information transition and thereby
can affect continuation value and current action ranking.

## 4. Exact continuation specification

For valid invocation `remaining=r>=1`, define `L(r)=min(2,r)`. Define a
development switch d and transition

```text
F_d(S,X)[i,k] = 1-(1-S[i,k]) exp(-lambda X[i,k])  if d=True
             = S[i,k]                                   if d=False
lambda = -log(1-eta), eta=.35 in Campaign 1.

B_m(b,S,X,u) = b_m exp(-(u-mu_m(S,X))^2/(2 sigma^2))
              / sum_j b_j exp(-(u-mu_j(S,X))^2/(2 sigma^2)).

G(b,S) = max_{U in A} g(b,S,U).
```

The implemented Bayes operator uses shifted log weights, preserves zero-prior
components, returns `(1,)` for M=1, and returns the prior unchanged when the
predicted mean spread is at most `1e-10` (92–118). Call this numerical operator
`B_num`, to distinguish it from the ideal expression above.

With Hermite nodes `xi_j` and weights `w_j`, j=1,2,3:

```text
u_mj = mu_m(S,X) + sqrt(2) sigma xi_j
omega_j = w_j / sqrt(pi)

Q_1(b,S,X) = g(b,S,X)
Q_2(b,S,X) = g(b,S,X)
            + sum_{m:b_m>0} b_m sum_j omega_j
                G(B_num(b,S,X,u_mj), F_d(S,X)).

V_0 = 0
V_1 = G
V_2 = max_X Q_2
CURRENT(b,S,r) = first X in A with
                |Q_L(r)(b,S,X)-max_U Q_L(r)(b,S,U)| <= 1e-10.
```

This is a two-stage Bellman form with numerical observation integration,
not a recursion `V_(r-1)` for arbitrary remaining r. The returned scalar is
the numerical maximum, which may exceed the selected tolerance-optimal action's
value by up to `1e-10`. The continuation uses the maximum scalar G, not the
value of a potentially tolerance-suboptimal leaf action.

## 5. Prospective capability propagation

`mis_v2_transition` is called once for every current candidate when r>1,
before calculating the continuation production (`194–220`). Exposure is the
action entry `X[i,k]`, including fractional `.5`, and not a binary count.
`discover_develop_v2.py:33–71` validates eta, S, and X and applies the exact
exponential formula; there is no normalization, clipping, stochastic capability
transition, or worker relabeling. With `develop=False`, it returns the original
state exactly, after validation.

No second prospective development update is used for the leaf action: its
production is earned on `F_d(S,X)`, and there is no value after that leaf.
At the last real step the selector computes no candidate transition, although
the runner still develops the executed action afterward. That real state
persists into the next problem, but the selector does not value that benefit
prospectively across the problem boundary.

## 6. Prospective belief propagation

For each simulated observation, `finite_bayes_update` computes a posterior
using **pre-transition** S and the current candidate X. The predictions passed
to Bayes are computed at line 207, before the MIS-v2 transition at 212.
Observation therefore concerns current production, not production by the
already developed team. The candidate next S is the same across observation
branches; the posterior generally differs across them.

Posterior b enters `_best_immediate(next_state, posterior, model)`, which
evaluates every future action. Thus the next action can depend on the simulated
observation. No posterior after the leaf action is simulated, because there
is no further reward in the two-stage evaluation. The real runner updates
belief after each actual observation and resets it at every new problem;
only S persists (275–313).

## 7. Observation integration

The subjective predictive distribution is

```text
p_I(u | b,S,X) = sum_m b_m Normal(u; mu_m(S,X), sigma^2).
```

It is integrated conditionally on each positive-probability hypothesis using
three-node Gauss–Hermite quadrature, not Monte Carlo or a single expected
observation. `gaussian_quadrature_nodes` (`discover_v0.py:157–163`) calls
`numpy.polynomial.hermite.hermgauss(order)`. For order 3, standardized nodes
are `(-sqrt(3),0,sqrt(3))` and normalized weights `(1/6,2/3,1/6)` after the
Gaussian transformation. Thus the observations are `mu_m+sigma*(-sqrt(3),0,
sqrt(3))`. With M=3 and positive beliefs, each current action has nine branches.

The helper caches full node/weight tuples by `(mean,sigma,order)`; identical
arguments reuse tuples. Each mixture component has shifted observations;
it is not a single quadrature around the mixture mean. Order 3 is hard-coded
in CURRENT, independent of remaining r>1. There is only one observation layer.
The imported default order 31 belongs to `finite_unknown_policy_value`, not
CURRENT. No quadrature convergence claim is established by this audit.

## 8. Future-action optimization

`_best_immediate` (179–185) exhaustively evaluates all 64 actions at each
posterior and transitioned S. This is an observation-contingent leaf maximum,
not a fixed open-loop action sequence. It is greedy at the terminal planning
stage because only its immediate reward is retained; this is exact for a
one-stage terminal subproblem, and a truncation relative to longer horizons.

## 9. Horizon, terminal value, and discounting

There are three real decisions per problem. The runner passes remaining 3, 2,
and 1, while CURRENT evaluates effective windows 2, 2, and 1. Values for any
remaining>1 use the same two-stage calculation; no configurable nominal MPC
horizon parameter exists. Invalid remaining<=0 is not explicitly rejected by
the selector and would enter the two-stage branch; the audited runner never
supplies such values.

The terminal value after the planning window is zero. No future problem is
planned. There is no discount multiplication: gamma=1 implicitly, an
undiscounted sum within the evaluated window. Replanning after real updates
does not restore the omitted third-stage term in the initial calculation.

## 10. One-stage equivalence

When remaining==1, lines 209–211 set every candidate value to g and bypass
both MIS-v2 and predictive Bayes integration. Analytically the ideal decision
is `argmax_X sum_m b_m R_z_hat_m(S,X)`; operationally it is the first action
within `1e-10` of that maximum. The known branch (231–238) gives the analogous
first tolerance-optimal action for `R_z*(S,X)`. There is no development bonus,
information bonus, terminal proxy, or residual continuation term at r=1.
This is an equivalence of existing code, not implementation of a new policy.

## 11. Information-value computational chain

All required links exist: X determines the hypothesis-specific current means;
those means determine predictive observation nodes and likelihoods; each node
generates B_num; the posterior changes the leaf action values and their maximum;
the weighted maximum enters Q_2 and hence the current action ranking.

Therefore CURRENT **can** select an action partly for its effect on future
beliefs and decisions. This is a structural possibility, not proof that it
occurs in every state. Uninformative predictions, degenerate beliefs, r=1,
or posterior-invariant future optima can eliminate decision value of information.

## 12. Development-value computational chain

All required links also exist: candidate X changes F_d(S,X); leaf production
is recomputed at that next S for every action; the best leaf value enters Q_2.
CURRENT **can** favor present exercise for its future productive consequence.
That consequence is absent at r=1 or d=False. The controller values only the
next stage's consequence of development, not all later problems that may use S.

## 13. Approximation and numerical inventory

| Item | Location | Mathematical consequence and action-selection relevance |
|---|---|---|
| Two-stage truncation | finite selector 209–220 | Omits stage 3 at the first real decision and all later problems; can change rankings relative to full-horizon DP. |
| Three-node observation quadrature | finite selector 217; Gaussian helper 157–163 | Approximates a nonlinear posterior-dependent maximum; exact Gaussian polynomial quadrature does not make this integrand exact. Can change rankings; no error bound is asserted. |
| Finite internal hypotheses | canonical model 58–77; predictions 80–82 | Representation I can be misspecified relative to continuous true z. This is a declared information model, not a solver approximation to a fixed finite-model DP. |
| 64 discrete allocations | discover_v0 42–48 | Exhaustive within the declared action space. Restriction relative to a hypothetical continuous allocation problem is world/action design, not pruning by CURRENT. |
| Tolerance-optimal first action | finite selector 221–222; leaf 184–185 | Uses first Cartesian-enumeration action within 1e-10 of maximum; can select a slightly lower-valued action. Leaf value itself remains the maximum. |
| Equal-mean Bayes shortcut | finite Bayes 106–107 | Treats mean spreads <=1e-10 as uninformative; can differ from exact Bayes at tiny nonzero separations. |
| Floating-point likelihoods/sums | finite Bayes 108–118 and Q accumulation | Log shifting avoids overflow; extreme posterior components may underflow to zero. Rounding can affect close rankings. |
| Deterministic MIS-v2 and Gaussian observation | transition and likelihood | Exact declared M/I assumptions, not approximations introduced by the planner. |
| Canonical hypothesis ordering and cached nodes | canonical model; Gaussian helper | Deterministic ordering/cache does not intentionally approximate the operator; canonical ordering fixes summation order. |

There is no candidate pruning, heuristic score, fitted terminal value, belief
grid/interpolation, approximate search over actions, Monte Carlo rollout, or
deterministic-mean observation substitution on this route. Exhaustive search
and numerical integration implement pi; they are not a separate scientific
mechanism beside M, I, and pi.

## 14. Conservative classification

CURRENT is a finite-hypothesis, belief-state, information-aware and
development-aware two-stage MPC approximation. It is not myopic except at
its one-stage boundary (or in degenerate states). It approximates a
Bayes-adaptive finite-horizon decision problem **under its internal finite
model** because posterior beliefs enter prospective conditional optimization.
It is not an exact three-stage Bayes-adaptive DP and is not guaranteed optimal
for true problems outside that model. “Dual-control-like” is at most a scoped
analogy to the action→information→future-decision loop; this audit does not
establish a classical dual-control formulation or a novel algorithm.

## 15. KNOWN-Z mathematical operator

```text
Q^known_1(S,X;z*) = R_z*(S,X)
Q^known_2(S,X;z*) = R_z*(S,X) + max_U R_z*(F_d(S,X),U).
```

The same L(r) and first-within-tolerance rule apply. There is no belief or
observation integral. Its next-stage action is optimized directly at true z*.

## 16. Code ↔ equation traceability

| Term / operation | Source file | Function and lines | Interpretation |
|---|---|---|---|
| Campaign condition entry | experiments/synthetic/campaign1/run.py | run_condition 100–115 | Dispatch FULL, NO-DEVELOP, KNOWN-Z. |
| S,b,r at a real decision | src/hls/finite_problem_belief.py | run_finite_problem_sequence 275–297 | Reset b, preserve S, decrement remaining, replan. |
| A | src/hls/discover_v0.py | INDIVIDUAL_ACTIONS / JOINT_ACTIONS 42–48 | 4^3 allocations, fixed Cartesian order. |
| Y and R | src/hls/discover_v0.py | production_inputs / ces_reward 95–115 | Production at pre-development S. |
| mu_m and g | src/hls/finite_problem_belief.py | hypothesis_means / expected_reward 80–89 | Finite-model immediate prediction. |
| B_num | src/hls/finite_problem_belief.py | finite_bayes_update 92–118 | Gaussian posterior, numerical shortcuts. |
| F_d | src/hls/discover_develop_v2.py | eta_to_lambda / capability_after_exposure / mis_v2_transition 33–71 | Continuous cell exposure; exact freeze when disabled. |
| u_mj, omega_j | src/hls/discover_v0.py | gaussian_quadrature_nodes 157–163 | Cached transformed Hermite quadrature. |
| G | src/hls/finite_problem_belief.py | _best_immediate 179–185 | Posterior-contingent exhaustive leaf maximum. |
| Q_1,Q_2, pi | src/hls/finite_problem_belief.py | finite_choose_dynamic_action_v2 194–222 | One-step boundary / two-step predictive value / tie rule. |
| Known Q | src/hls/finite_problem_belief.py | _known_dynamic_action_v2 225–238; _best_true_immediate 188–191 | Direct true-z two-stage maximization. |
| Real mu_true,r,b+,S+ | src/hls/finite_problem_belief.py | run_finite_problem_sequence 298–313 | Real observation first, posterior and development afterward. |
| NO-DEVELOP route | experiments/synthetic/campaign1/run.py | run_no_develop 70–97 | Same finite MPC with F_d identity prospectively and in reality. |
| Separate fixed-S DP | src/hls/finite_problem_belief.py | finite_unknown_policy_value 130–176 | Not Campaign 1 NO-DEVELOP; full remaining recursion, default 31 nodes. |

## 17. Exact FULL / NO-DEVELOP / KNOWN-Z relationship

FULL and NO-DEVELOP use the same finite selector, actions, posterior integration,
horizon truncation, and tie rule. Their direct switch is F_d: it changes both
prospective evaluation and real state updating. The resulting S, observations,
beliefs and later actions can consequently differ. Immediate g is the same
function at a given S,b; the real trajectories need not visit the same S,b.

KNOWN-Z invokes a separate implementation, `_known_dynamic_action_v2`, rather
than the finite selector. It shares actions, deterministic development,
two-stage truncation, leaf maximization and tolerance/order tie selection.
It removes uncertainty by evaluating true z directly, and so requires no
observation quadrature. Mathematically it is the known-problem counterpart of
the same two-stage structure; code paths differ. There is no evidence here
of an additional horizon/search approximation mismatch between these specific
Campaign 1 controls. This does not make their performance differences additive.

Historical `DISCOVER_ONLY` is different: it calls the fixed-S finite-horizon
belief DP with default 31-node integration and the entire remaining problem
horizon. Substituting it for NO-DEVELOP would change both development and the
planning approximation. Campaign 1's adapter avoids that substitution.

## 18. Future four-mode restriction: YES WITH CAVEATS

The operator is cleanly restrictable in principle by choosing whether F_d is
identity and whether the posterior passed to G is B_num or the current b.
Actions, immediate g, horizon, candidate enumeration, quadrature nodes/weights,
and tie rule can be held constant. The capability switch already exists; the
prospective belief-freeze switch does not. No modes are implemented here.

A prospective belief freeze must be distinguished from disabling real
inference: an unchanged information model can still update b after actual
observations while the planner holds it fixed inside its counterfactual
window. Retaining the same numerical integral when b is frozen makes identical
leaf values repeat across branches; normalized weights collapse this sum up
to floating-point error. No new labels or isolated causal-effect interpretation
follow from this architectural feasibility statement.

## 19. Documentation consistency and open qualifications

The foundation specification §13 accurately describes two-step MPC and
three-node integration; §14 correctly states undiscounted real dynamics.
The finite-belief gate's general mixture expression (lines 56–65) describes
both its fixed-S DP and dynamic MPC at different horizons/orders. It must not
be read as saying CURRENT uses full remaining-horizon recursion or order 31.
Its phrase “after applying” development concerns the continuation S; the
likelihood predictions still use current S. No contradictory equation was
found in the inspected foundation/protocol sources.

The foundation §16 phrase “four modes isolate mechanisms” must be read with
the later Campaign 1 protocol's explicit qualification: historical DISCOVER_ONLY
and FULL have different planners. This audit flags that interpretive hazard
without rewriting historical documentation or results. Claim-evidence ledger
C17 already disallows global optimality. No historical outcome is reclassified.

Open issues are quantitative quadrature error and agreement with a full
three-stage dynamic-S belief DP; neither is answered by static inspection.
The selector's unchecked nonpositive remaining values are outside its valid
runner contract. Extreme floating-point saturation/underflow is a numerical
qualification, not a hidden development clamp. No scientific inconsistency
requiring a physics or policy change was found.

## 20. Validation record

Inspection covered the Campaign 1 runner/protocol; finite-belief predictions,
Bayes, fixed-S DP, dynamic UNKNOWN and known selectors and sequence runner;
MIS-v2 and historical binary dynamic selector; CES/action/quadrature helpers;
foundation and finite-belief gate documents; claim/equation ledgers; and
existing finite-belief, MIS-v2, Campaign 1 protocol/execution/closure tests.

Validation for this task is restricted to static checks and existing
documentation/provenance tests that do not invoke team execution. Existing
trajectory-regression tests were inspected rather than executed. Frozen
result/protocol/scenario and model-source equality against the starting HEAD
is checked before commit, along with `git diff --check`. No campaign, new
policy, parameter sweep, or new scientific simulation output is part of this
audit.

Executed checks: `python -m pytest -q tests/test_campaign1_closure.py
tests/test_campaign1_protocol.py` — **11 passed**. These selected tests read
artifacts, inspect signatures, and validate protocol constants; they do not
call a sequence runner or dynamic action selector. `git diff --exit-code
10f81b7 -- src experiments results docs/experiments/CAMPAIGN_1_PROTOCOL.md
docs/experiments/CAMPAIGN_1_TEST_RANGE.md` passed; `git diff --check` passed.
The only added file is this audit. New team executions and new simulation
outputs for this task are zero.
