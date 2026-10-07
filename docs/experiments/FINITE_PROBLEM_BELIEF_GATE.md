# Finite Problem Belief Gate

## Scope and scientific status

This gate generalizes only DISCOVER's internal problem representation. The
world, production, Gaussian observation law, action space, assignment
semantics, MPC, problem duration, and MIS-v2 transition are unchanged. The
historical binary implementations remain frozen and executable.

The world problem is a point

```
z* = (p, 1-p),  p in [0,1],
```

of the continuous simplex `Z = Delta^1`. The controller instead has a finite,
ordered hypothesis set

```
Z_hat = {z_hat_1, ..., z_hat_M} subset Z,  M >= 1,
```

and a belief vector `b` over that set. `Z` and `Z_hat` are different objects.
Membership `z* in Z_hat` is exact representation; non-membership is model
misspecification. It is not classified here as novelty or REFRAME failure.

## Equations implemented

For action `X` and state `S`, hypothesis `m` predicts

```
mu_m(S,X) = R_z_hat_m(S,X).
```

The UNKNOWN controller's immediate value is

```
g(S,X,b) = sum_m b_m mu_m(S,X).
```

The true world independently supplies

```
mu_true = R_z*(S,X),
r ~ Normal(mu_true, sigma^2).
```

The likelihoods and stable log-weight update use only the internal family:

```
log w_m = log b_m - (r-mu_m)^2/(2 sigma^2),
b'_m = exp(log w_m - max_j log w_j)
       / sum_j exp(log w_j - max_l log w_l).
```

The finite-horizon continuation expectation is the same deterministic
Gauss--Hermite calculation as DISCOVER-v0, generalized to the predictive
mixture

```
sum_m b_m E_[r ~ Normal(mu_m,sigma^2)] V_(h-1)(b'(r)).
```

The two-step DISCOVER x DEVELOP MPC uses the same mixture after applying the
unchanged MIS-v2 transition to the cells exercised by the candidate action.
Known controls bypass `Z_hat` and evaluate `z*` directly; their belief is
absent rather than a synthetic one-hot vector.

Hypotheses are validated as distinct simplex points and canonically ordered by
decreasing first coordinate. A supplied prior is permuted with its hypothesis.
Inputs that violate the simplex or probability-vector constraints are rejected
and never silently normalized. Every new problem resets UNKNOWN belief to the
declared prior; only `S` persists across problem boundaries.

## Controls and results

The reproducible runner is
`experiments/synthetic/finite_problem_belief_gate/run.py`. Machine-readable
outputs are in `results/foundations/finite_problem_belief_gate/`.

### A. Binary regression

With `Z_hat=((.8,.2),(.2,.8))` and prior `(.5,.5)`, the generalized DP on G06
returned exactly the historical value `2.6751778561721986`, the same optimal
action set, and zero maximum discrepancy across its 64 action values in the
recorded horizon-three diagnostic. DISCOVER_ONLY also matched exactly.

For the historical G00/G06, `eta=.70`, alternating `1212` diagnostic, both
implementations used identical actions, observations, state trajectories, and
cumulative rewards. Maximum first-coordinate belief discrepancies were
`1.36e-20` (G00) and `6.63e-46` (G06), caused only by representing the residual
second probability explicitly rather than scalar complement arithmetic.

### B. Three represented hypotheses

The symmetric set `((.8,.2),(.5,.5),(.2,.8))` runs with a uniform prior and a
true balanced problem. All posterior vectors remain normalized and all three
hypotheses enter expected reward, likelihood, and MPC continuation mixtures.
A controlled observation at a hypothesis-predicted mean moves mass toward the
consistent hypothesis. Permuting hypotheses and the associated prior produces
the identical canonical model, policy, and value.

### C. Unrepresented true problem

With true `z*=(.63,.37)` and the same three-member internal set, the runner
computes production, observation mean, observed reward, and cumulative reward
from `(.63,.37)` exactly. Likelihoods and beliefs remain three-dimensional and
refer only to `Z_hat`; no nearest-point or binary fallback exists. The run is
numerically valid (final probability sum `1.0000000000000002`). The known
DEVELOP oracle also solves the same true problem directly, with no belief, and
returns cumulative reward `3.1353236746643747` in the recorded three-step case.

The posterior in one short noisy run need not concentrate on the geometrically
nearest hypothesis. That behavior is ordinary finite misspecified Bayesian
updating, not recognition or repair of misspecification.

## Interpretation and limits

The gate establishes that the existing continuous production world can be
paired with an arbitrary finite internal hypothesis repertoire, that binary
DISCOVER is recovered at `M=2`, and that world truth may lie outside that
repertoire without changing agent or world physics.

It does not establish continuous Bayesian inference, novelty detection,
misspecification detection, REFRAME, transfer, memory or learned priors across
problems, an optimal discretization of `Z`, or empirical calibration. Historical
novelty and representational mismatch remain distinct. No problem distance is
implemented or used by the controller.

## Output schemas

`control_summary.json` records the model sets, seed, binary discrepancies,
permutation check, represented/unrepresented posterior summaries, and known
oracle control. `control_trajectories.csv` records case, mode, problem and step
indices, exact true problem, beliefs, states, action, true mean, observation,
and cumulative reward.
