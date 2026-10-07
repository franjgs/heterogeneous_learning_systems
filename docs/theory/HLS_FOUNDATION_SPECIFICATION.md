# HLS Pre-Experiment Foundation Specification

**Status:** consolidated executable/model specification before any G00--G08
team is run in the frozen Small Problem World.  The authoritative source-model
HEAD is `a315143`; this document changes no physics, algorithm, or fixture.

## 1. Scope and scientific question

The present HLS laboratory asks how the interpersonal geometry of acquired
capabilities interacts with a changing problem world when work simultaneously
produces output, evidence about the current problem, and capability exposure.
It is designed to test conditional relationships, not to prove that
heterogeneity, specialization, or adaptive management is universally better.

This specification fixes the current model boundary and provenance before the
next experimental protocol is written.  It is not that protocol and contains
no main-campaign outcome.

## 2. System boundary

The executable system contains three agents (`N=3`), two capability/output
dimensions (`K=2`), a centralized controller with direct access to the complete
capability matrix and belief, a finite action set, a continuous true problem
space, Gaussian production observations, finite Bayesian inference, and an
exposure-driven capability transition.

The controller is not decentralized.  Agent identity matters through the
matching of each allocation `x_ik` with that agent's capability `s_ik`, but
agents do not locate expertise, communicate, refer work, or maintain beliefs
about one another.

## 3. State variables and exact causal loop

At a decision step the controller state is at least `(S_t,b_t,h_t)`, where:

- `S_t=(s_ik)` is the `3 x 2` latent capability matrix;
- `b_t` is an UNKNOWN controller's finite belief over `Z_hat` (absent in KNOWN
  oracle modes);
- `h_t` is the number of decisions remaining in the current problem;
- `z*` is the fixed true world problem for that problem episode, not an agent
  state or input to an UNKNOWN policy.

The code executes the following order at each step:

```text
(S_t, b_t, h_t, Z_hat) --controller--> X_t
(S_t, X_t) --------------------------> Y_t
(z*, Y_t) ---------------------------> mu_true,t
mu_true,t + Gaussian noise ----------> r_t
(b_t, Z_hat, S_t, X_t, r_t) --------> b_(t+1)
(S_t, X_t, eta) ---------------------> S_(t+1)
mu_true,t ---------------------------> cumulative scored performance
```

The implementation computes the posterior before calling the capability
transition, but both updates use the same pre-transition `S_t` and chosen
`X_t`; MIS-v2 does not depend on `r_t`.  The next decision uses both updated
objects.  The noisy `r_t` is the observation used by Bayes.  Despite the legacy
field name `observed_reward`, scored cumulative performance is the sum of true
production means `mu_true`, not the sum of noisy observations.  This naming
distinction is important for later analysis.

## 4. Capability representation

`s_ik(t) in [0,1]` is the effective acquired capability of individual `i` for
function `k`.  It is a latent normalized state used by production.  It is not
accumulated experience, observed performance, probability of success, or a
belief.  The modeled chain is:

```text
exercised effort -> latent capability s_ik -> aggregate output -> performance.
```

Validation enforces a `3 x 2` finite matrix with every entry in `[0,1]`.

## 5. Team configurations

The existing Capability Geometry gates define nine candidate matrices G00--G08
with exact column totals `sum_i s_i1=sum_i s_i2=1.5`, after removing
agent-permutation equivalents.  Their design labels and transparent geometric
descriptors never enter a controller.  The executable state validator itself
does not impose these column budgets; they are experimental restrictions.

Those candidates have **not** been executed in the frozen Small Problem World.
The future selection of eta, seeds, hypotheses, outcomes, and campaign protocol
is not frozen here.

## 6. Action and allocation representation

Each agent selects one of four allocations:

```text
(0,0), (0,1), (.5,.5), (1,0).
```

The joint action is their Cartesian product: `4^3=64` actions.  An entry
`x_ik` is both productive effort applied to capability `k` and MIS-v2 exposure
of that individual-capability cell when development is enabled.  Per-agent
effort is zero or one in the declared set.  Tie-breaking is deterministic in
the frozen controllers; it is an implementation convention, not a scientific
mechanism.

## 7. Production physics

For state `S` and joint allocation `X`, aggregate capability outputs are

```text
Y_k(S,X) = sum_i x_ik s_ik.
```

For problem `z=theta`, production is CES:

```text
R_z(S,X) = (sum_k theta_k Y_k(S,X)^rho)^(1/rho),
rho = .5.
```

`theta_k` is the relative relevance/weight of capability output `k` in the
current production problem.  It is nonnegative and normalized to sum to one.
In this model it is not an agent capability, task arrival probability,
environmental transition probability, difficulty scalar, cognitive frame, or
learning rate.  CES and its parameterization are purchased production
machinery; choosing this particular normalized two-output world is an HLS
modeling decision.

## 8. Continuous true problem space

The true production-level problem world is

```text
Z = Delta^1 = {z(p)=(p,1-p): p in [0,1]}.
```

Every valid point is a legitimate true problem under current physics,
including endpoints and interior points.  Historical `theta1=(.8,.2)` and
`theta2=(.2,.8)` are two points, not the ontology of the world.

## 9. Intrinsic problem geometry

The neutral physically admissible aggregate-output envelope is

```text
Y1>=0, Y2>=0, Y1+Y2<=3.
```

The team-independent production-surface distance is

```text
d_R(p,q) = (1/3) sup_Y |R_p(Y)-R_q(Y)|.
```

For `rho=.5`, the derived and independently validated closed form is

```text
d_R(p,q) = |p-q|[1+|p+q-1|].
```

The supremum for `p!=q` occurs at `(3,0)` or `(0,3)`.  The mapping from `p` to
its production surface is injective; the normalized sup distance is therefore
a metric.  Nonnegativity, identity, symmetry, triangle inequality, endpoint
location, normalization, and capability-exchange symmetry were checked by the
Problem Distance Gate.  Maximum closed-form/numerical discrepancy was
`3.33e-16`.

This is intrinsic only under the declared HLS production physics and neutral
envelope.  It is team- and policy-independent.  It is not cognitive or
empirical task similarity, expected loss, realized difficulty, transfer
probability, or adaptation probability.  As a supremum it emphasizes maximum
potential production-surface distinction at pure-output endpoints.

## 10. Agent problem representation

True world and agent representation are distinct:

```text
TRUE WORLD:  z* in Z
AGENT MODEL: Z_hat={z_hat_1,...,z_hat_M} subset Z, M>=1
b_m>=0, sum_m b_m=1.
```

`b_m` is the controller's posterior probability on represented hypothesis
`z_hat_m`.  Hypotheses are distinct, validated simplex points in deterministic
canonical order; a supplied prior is permuted consistently and invalid inputs
are rejected rather than silently normalized.

The true `z*` need not belong to `Z_hat`.  In that case the likelihood family
is misspecified operationally, but the agent has no misspecification detector,
unknown-model hypothesis, or repair mechanism.

## 11. DISCOVER

For candidate action `X`, represented hypothesis `m` predicts

```text
mu_m = R_z_hat_m(S,X).
```

The true world independently determines

```text
mu_true = R_z*(S,X),
r ~ Normal(mu_true, sigma^2),
sigma = .10.
```

The finite Bayesian update is

```text
L_m(r) = Normal(r;mu_m,sigma^2),
b'_m = b_m L_m(r) / sum_j b_j L_j(r).
```

It is implemented with shifted log weights for numerical stability.  UNKNOWN
immediate expected production is

```text
g(S,X,b) = sum_m b_m mu_m.
```

The finite continuation integrates observations under the predictive mixture

```text
sum_m b_m E_[r~Normal(mu_m,sigma^2)] V(b'(r)).
```

The `M=2` vector implementation reproduces historical scalar DISCOVER within
floating-point tolerance.  Tests also validate `M=1`, `M=3`, hypothesis-order
invariance, represented truth, unrepresented truth, and absence of true-z
leakage into UNKNOWN action selection.

DISCOVER does not perform continuous Bayesian inference, detect novelty or
misspecification, learn an environmental transition, carry posteriors across
problems, transfer knowledge, or reframe the hypothesis family.

## 12. DEVELOP / MIS-v2

For exposure `x>=0`, the current capability transition is

```text
s+ = 1-(1-s)exp(-lambda x), lambda>0.
```

For one standard exposure,

```text
eta = 1-exp(-lambda), 0<eta<1,
s+ = s+eta(1-s).
```

In executable joint actions, `x_ik` is `0`, `.5`, or `1`; each objectively
exercised cell receives its own fractional exposure.  With development off,
`S` is unchanged.  Valid inputs require no clipping.

MIS-v2 satisfies boundedness, no change without exposure, positive development
below mastery, mastery as a fixed point, diminishing absolute gain with prior
capability, no finite instantaneous mastery, and exposure-composition
consistency.  The qualitative premise that practice can develop capability is
literature-motivated.  The exponential latent-state equation, common rate,
normalization, fixed ceiling, and composition condition are HLS modeling
assumptions.  Eta is not empirically calibrated and is deliberately not frozen
for the future campaign in this specification.

MIS-v1 remains historical only.  Its clipped rule could send `s=0` to mastery
in one exposure and its winner map is not current development evidence.

## 13. Sequential action selection and MPC

There are two distinct UNKNOWN evaluators:

1. `DISCOVER_ONLY` uses the finite-horizon belief-state DP with fixed `S`, the
   remaining problem horizon, and 31-node Gauss--Hermite integration.
2. `DISCOVER_DEVELOP` uses the frozen standard two-step receding-horizon MPC.
   For every candidate action it adds immediate belief-weighted production to
   the three-node quadrature expectation of the best immediate action on the
   action-induced MIS-v2 next state; it replans after every observation.  At
   the last step it uses immediate value only.

The dynamic controller is an approximation, not an exact full three-step
belief/continuous-`S` DP and not a new HLS score.  DISCOVER and DEVELOP couple
because the same selected action determines current output and evidence while
also determining which cells are exercised and hence the next `S`.

## 14. Within-problem dynamics

The true `z*` remains fixed for `H=3` decisions.  Each decision selects an
action from the same 64-action space, generates a Gaussian observation, updates
UNKNOWN belief, optionally updates capability through MIS-v2, and replans.
There is no discount factor in this prototype controller or performance sum.

## 15. Between-problem dynamics

At a problem boundary:

- the true problem may change according to an externally supplied sequence;
- developed `S` persists unchanged into the next problem;
- UNKNOWN belief is discarded and reset to the declared prior over `Z_hat`;
- the previous posterior is not used to predict the next problem;
- there is no learned transition model, familiarity prior, or environmental
  state inferred by the agent.

Thus history can affect later actions through `S`, but not through posterior
memory.  Recurrent behavior changes must not be described as remembering a
problem.

## 16. Oracle and control conditions

Four modes isolate mechanisms:

| Mode | Problem knowledge | Development |
|---|---|---|
| DISCOVER + DEVELOP | finite `Z_hat` and belief | MIS-v2 on |
| DISCOVER only | finite `Z_hat` and belief | off |
| DEVELOP, theta known | true `z*` directly | MIS-v2 on |
| static known theta | true `z*` directly | off |

Known modes do not approximate `z*` by a nearest hypothesis or require a
one-hot finite belief.  They are oracle controls, not realistic information
structures.

## 17. Problem-world descriptors

For true problems `z_1,...,z_T`:

```text
C_t = d_R(z_t,z_(t-1)),                 t>1
N_t = min_(j<t) d_R(z_t,z_j),           t>1
M_t = min_(z_hat in Z_hat) d_R(z_t,z_hat).
```

`C_t` measures current environmental movement, `N_t` distance from historical
true experience, and `M_t` distance from the current representational
repertoire.  They are not interchangeable: recurrence can follow nonzero
change, and a historically novel problem can be exactly represented. `C_1`
and `N_1` are explicitly missing (`None`); `M_1` is defined. No qualitative
thresholds or combined score exist.

## 18. Frozen Small Problem World

The frozen repertoire and prior are

```text
Z_hat=((.8,.2),(.5,.5),(.2,.8)),
b_0=(1/3,1/3,1/3).
```

The true sequence is `A -> A' -> B -> B' -> C -> A`, or
`p=(.8,.7,.3,.2,.5,.8)`.

| Stage | p | C | N | M | Represented |
|---|---:|---:|---:|---:|---|
| A | .8 | -- | -- | 0 | yes |
| A' | .7 | .15 | .15 | .15 | no |
| B | .3 | .40 | .40 | .15 | no |
| B' | .2 | .15 | .15 | 0 | yes |
| C | .5 | .39 | .24 | 0 | yes |
| A | .8 | .39 | 0 | 0 | yes |

The validated pairwise matrix for unique problems is:

| | A | A' | B | B' | C |
|---|---:|---:|---:|---:|---:|
| A | 0 | .15 | .55 | .60 | .39 |
| A' | .15 | 0 | .40 | .55 | .24 |
| B | .55 | .40 | 0 | .15 | .24 |
| B' | .60 | .55 | .15 | 0 | .39 |
| C | .39 | .24 | .24 | .39 | 0 |

This deliberately constructed fixture is not an empirical problem
distribution.  It was frozen before any G00--G08 team execution.  Its artifact
records `team_executions=0`.

## 19. Experimental observables

The sequence runner can record problem/step identity, true problem for
evaluation, beliefs before/after, `S` before/after, joint action, true
production mean, noisy observation, MIS increment, cumulative expected
production, and final `S`.  Geometry experiments additionally record initial
known value, configuration descriptors, assignment changes, early/late
performance, and control-mode comparisons.  Future primary outcomes and
statistical analyses are not selected here.

## 20. Scientific-status ledger

| Component | Formal source | Status | Validation | Claim allowed | Claim not allowed |
|---|---|---|---|---|---|
| CES production | standard CES family | STANDARD / PURCHASED | unit and gate regressions | declared production mapping | empirical realism or novelty |
| `theta=(p,1-p)` | HLS world definition | HLS MODELING ASSUMPTION | simplex validation | relative output relevance | universal task ontology |
| `Z=Delta^1` | extension already admitted by CES | HLS DEFINITION | finite-belief controls | continuous true problem world | continuous agent inference |
| Gaussian observation, `sigma=.10` | standard likelihood model | STANDARD machinery + HLS parameter choice | Bayes regressions | declared observation process | empirical noise calibration |
| Bayesian update | Bayes rule | STANDARD / PURCHASED | M=1/2/3 tests | finite posterior update | novelty detection |
| finite `Z_hat` | HLS representation choice | HLS MODELING ASSUMPTION | validation/permutation tests | arbitrary finite repertoire | optimal representation |
| world/model separation | HLS architecture | VALIDATED IMPLEMENTATION PROPERTY | represented/unrepresented controls | `z*` may lie outside `Z_hat` | recognition of mismatch |
| fixed-`S` belief DP | standard finite-horizon DP | STANDARD / PURCHASED | binary and brute-force controls | DISCOVER-only policy evaluator | new HLS optimization method |
| two-step dynamic MPC | standard receding-horizon look-ahead | STANDARD / PURCHASED approximation | trajectory regressions | frozen controller | exact full-horizon optimum |
| MIS-v2 | exponential capability-gap law | HLS MODELING FORMULATION | R1--R7 and sensitivity gate | coherent latent development | empirically established law |
| `d_R` sup distance | sup-norm construction on HLS envelope | HLS MODELING CHOICE | numerical grid | intrinsic declared distance | cognitive similarity |
| closed-form `d_R` | algebra under `rho=.5` | HLS DERIVED RESULT | analytic/numerical agreement | formula under current physics | novel general theorem |
| `C_t` | distance between consecutive truths | HLS DESCRIPTOR | sequence controls | change magnitude | transition model |
| `N_t` | distance to prior truths | HLS DESCRIPTOR | sequence controls | historical novelty descriptor | agent novelty recognition |
| `M_t` | distance to `Z_hat` | HLS DESCRIPTOR | sequence controls | representational mismatch | detected misspecification |
| Small Problem World | frozen designed sequence | EXPERIMENTAL FIXTURE | fixture/artifact tests | controlled future world | ecological validity |
| persistence of `S` | runner temporal convention | HLS MODELING ASSUMPTION | trajectory regressions | capability history persists | memory of problem identity |
| reset of belief | runner temporal convention | HLS MODELING ASSUMPTION | reset test | independent prior each problem | learned environmental process |
| geometry-performance relationship | prior MIS-v2 diagnostic | PREVIOUS DIAGNOSTIC RESULT | nine-geometry sensitivity gate | scoped WHO-HAS-WHAT effects | universal diversity advantage |
| performance in frozen world | not yet run | EMPIRICALLY UNSUPPORTED / TO BE TESTED | none | hypothesis only | result or winner claim |

## 21. Explicitly absent mechanisms

The frozen foundation contains no transactive memory system, explicit
inter-agent communication, expertise search, knowledge transfer or spillover,
REFRAME, learned environmental transition, cross-problem posterior memory,
forgetting, continuous Bayesian problem inference, novelty detector,
misspecification detector, or cognitive problem representation beyond finite
hypotheses.  It also has no empirically calibrated eta or noise model.

Later results cannot constitute evidence about mechanisms not represented.

## 22. Known limitations

- The world has only two capability dimensions and three centrally observed
  agents.
- The action set is discrete and small; ties follow fixed implementation order.
- CES `rho=.5`, Gaussian `sigma=.10`, problem horizon three, and the output
  envelope are modeling choices, not calibrated facts.
- Dynamic action selection is two-step MPC rather than exact full-horizon DP.
- MIS-v2 uses a common rate, fixed ceiling, no forgetting, and no transfer.
- Belief resets eliminate environmental learning and familiarity priors.
- `d_R` emphasizes a maximum endpoint discrepancy rather than typical usage.
- Existing geometry results are synthetic diagnostics; exact winner maps vary
  with eta/environment and MIS-v1 results were not robust.
- The Small Problem World is deliberately constructed and has not been tested
  with candidate teams.

## 23. Validated invariants and gates

### Capability Geometry / MIS-v2

Under equal capability totals, interpersonal placement changed assignments,
development, and performance in the prior synthetic gate.  Environment-specific
geometry crossovers occurred across the preregistered eta grid, while exact
winners were eta-sensitive.  No universal heterogeneous winner emerged.  The
MIS-v1 winner map did not survive unchanged; G08 was the clearest lost winner.
This is scoped diagnostic evidence, not the frozen-world campaign result.

### Finite Problem Belief

The gate recovered binary M=2 values and trajectories, exercised represented
M>2 truth, preserved continuous true truth outside `Z_hat`, validated known
oracles outside `Z_hat`, and established hypothesis-order invariance.

### Problem Distance

Closed form and independent triangular-grid supremum agreed within `3.33e-16`;
metric, endpoint, normalization, and capability-exchange controls passed.

### Small Problem World

The exact sequence, repertoire, prior, descriptor trajectory, pairwise matrix,
symmetries, recurrence, and temporal conventions are validated.  No team was
executed.

## 24. Documentation/code reconciliation

No scientific contradiction was found among current code, tests, and gate
artifacts.  Two scope/terminology cautions are recorded rather than silently
harmonized:

1. Historical Capability Geometry/MIS-v1 documents correctly describe a
   two-theta world and clipped MIS-v1 in their own frozen scope; they are not
   descriptions of the current continuous-world/MIS-v2 foundation.
2. The sequence data field `observed_reward` is the noisy Gaussian observation,
   whereas scored `cumulative_expected_reward`/`cumulative_reward` sums
   `mu_true`.  Future prose must not conflate them.

The historical finite-belief gate statement that no distance was implemented
was true at that gate; `d_R` was added later and remains outside the controller.

## 25. Frozen pre-experimental state and provenance

The machine-readable authority is
`results/foundations/HLS_PRE_EXPERIMENT_FOUNDATION.json`, identifier
`hls-pre-experiment-foundation-v1`.  Its source model HEAD is `a315143`, after
commits `116a6f2`, `3e2dbea`, and `a315143`.  Git history supplies the later
documentation commit without creating a self-referential hash inside its own
contents.

The intended publication provenance chain is:

```text
model/foundation commit
-> future protocol commit
-> experiment run identifier and immutable raw artifacts
-> versioned analysis code
-> generated table/figure plus machine-readable source data
-> manuscript commit/version.
```

The current foundation commit is not the experimental-protocol commit.  No
future paper table should depend only on manually copied numbers, and no
reproducible figure should exist only as an opaque image.

Negative and null results are retained.  Environments, eta values,
configurations, or outcomes must not be selected after the fact to preserve a
preferred hypothesis.

## 26. Open scientific questions

The next work must preregister, rather than answer here:

- which eta values, seeds, candidate geometries, control modes, outcomes, and
  comparisons constitute the frozen G00--G08 protocol;
- whether WHO-HAS-WHAT changes adaptive trajectories in this same frozen world;
- whether configuration-by-problem-dynamics crossovers survive;
- which differences are initial, discovery-driven, development-driven, or
  generated by their sequential coupling;
- how robust any result is to mechanisms held fixed here;
- what empirical systems and literature can justify or delimit external
  interpretation.

No result about these questions is established by this specification.
