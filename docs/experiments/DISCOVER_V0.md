# DISCOVER-v0 — Fixed-Repertoire Discovery Cost

**Status:** Technical, reproducible prototype. It does not establish an HLS
mechanism, adaptation result, learning result, or HLS advantage.

**Implementation:** `src/hls/discover_v0.py`
**Runner:** `experiments/synthetic/discover_v0/run_discover_v0.py`
**Outputs:** `results/foundations/discover_v0/`

## Scope

DISCOVER-v0 isolates a fixed-repertoire question: whether the geometry of a
known collective capability matrix changes the cost of discovering which of two
functional structures governs production. The competence matrix is constant:
there is no MIS, learning-by-doing, transfer, role, score, or capability
transition.

CES production is a purchased physical layer. A discrete prior, Gaussian
likelihood, Bayes updating, and belief-state dynamic programming are purchased
standard inference/control tools. The UNKNOWN value is calculated by
finite-horizon belief-state DP with deterministic Gauss--Hermite numerical
integration; it is **not** called an exact symbolic DP.

## Frozen model

There are three agents and two capabilities. Each agent selects exactly one
member of the finite allocation set

```text
(0,0), (1,0), (0,1), (0.5,0.5),
```

so the joint action space has `4^3 = 64` allocations and each agent obeys
`sum_k x_ik <= 1`. For fixed `S`, an action produces

```text
Y_k = sum_i x_ik s_ik
R_theta(Y) = (sum_k alpha_theta,k Y_k^rho)^(1/rho)
```

with `rho=0.5`, `alpha_theta1=(.8,.2)`, `alpha_theta2=(.2,.8)`, equal prior
probability `.5`, Gaussian observation noise `sigma=.10`, and horizon `H=3`.

The state universe is exhaustive over `s_ik in {0,.5,1}` subject to total
budget `sum_ik s_ik=3`. Equivalent worker-label permutations are represented
once by lexicographically sorted rows. This yields 141 labelled states and the
canonical representatives recorded in the output.

## Values and interpretation boundary

For each representative,

```text
V_K = .5 V*(S,theta1) + .5 V*(S,theta2)
V_U = V*(S,b0)
C_D = V_K - V_U.
```

The complete pair ledger records `(|Delta V_K|, |Delta C_D|)` without an
invented materiality threshold. Expert/CE interpretation, not this prototype,
determines whether any comparison is scientifically meaningful.

The experiment asks only whether productive repertoires with comparable known
value can carry different costs of DISCOVER. It does not demonstrate adaptive
performance, competence learning, transfer, or an HLS-specific policy.

## Numerical control

The production ledger uses order 31. The runner reports orders 15, 23, and 31
for three fixed canonical representatives (first, middle, and last in the
canonical enumeration); the final successive-order difference is a numerical
convergence diagnostic, not a theorem. Tests separately
check Bayes identities, uninformative observations, revealed-theta control,
one-period absence of future information value, type identity, low-noise
identification, symmetries, numerical reproducibility, nonnegative discovery
cost, and independent brute-force controls.

## Post-closure mechanistic audit: production--information geometry

The derived audit retains exactly the frozen 31 canonical capability states
and 64 joint actions.  It changes no CES parameter, prior, noise, horizon,
action repertoire, capability state, or DP.  For every `(S,X)`,
`action_information_geometry.csv` records

```text
mu_theta1, mu_theta2,
reward_prior = .5 (mu_theta1 + mu_theta2),
d = |mu_theta1 - mu_theta2| / sigma,
KL = d^2 / 2,
production_gap = max_X reward_prior(X) - reward_prior(X).
```

It also marks the complete production--discriminability Pareto frontier and
records continuous retention ratios relative to the maximum available
production and discriminability.  These ratios retain the question of whether
an action is simultaneously productive and informative without introducing a
binary threshold.

`configuration_information_geometry.csv` records, for every configuration,
the full frontier's production gaps, `max_d`, the discriminability of
immediately production-optimal actions, the UNKNOWN-DP initial actions and
their four geometry quantities, and the known-theta initial actions.
`pair_diagnostics.csv` contains every one of the 465 configuration pairs;
there is no chosen closeness cutoff for `V_K`.

### Reproduction and S001/S002 diagnostic

The fixed runner reproduces the existing values:

| configuration | `V_K` | `C_D` |
| --- | ---: | ---: |
| S001 | 2.966656 | 0.291478 |
| S002 | 2.963939 | 0.197085 |

Thus `Delta V_K=0.002718` and `Delta C_D=0.094394`.  Their initial
opportunity geometry differs materially.  S001 has `max_d=9`, four unique
Pareto points, and zero discriminability at immediate production optimum.  Its
UNKNOWN first actions have `reward_prior=0.736274`, `d=3`, `KL=4.5`, and
`production_gap=0.013726`; the maximum-discriminability actions have gap
`0.24`.  S002 has `max_d=12`, two unique Pareto points, and immediate
production-optimal actions already at `d=7.5` and `KL=28.125`.  Its UNKNOWN
first actions have `reward_prior=0.790959`, `d=7.5`, `KL=28.125`, and zero
production gap; its maximum-discriminability actions have gap `0.110959`.
The complete tied action identities, including the known-theta choices, are in
the action ledger rather than being reduced to an arbitrary representative.

### Cross-configuration descriptive result

Across all 31 configurations, descriptive Pearson/Spearman correlations with
`C_D` are respectively: `max_d` (-0.634/-0.596), discriminability at immediate
production optimum (-0.648/-0.705), UNKNOWN initial `d` (-0.440/-0.331),
UNKNOWN initial production gap (+0.564/+0.684), and unique Pareto-point count
(+0.511/+0.520).  These are associations only: no causal or inferential claim
is made.

The geometry is not a sufficient scalar explanation.  For example, configurations
with `max_d=12` range from `C_D=0` (S016/S021) to `C_D=0.214566`
(S019/S028); S001 and S003 share `max_d=9` but have `C_D=0.291478` and
`0.218947`.  The complete pair ledger preserves these and all other
counterexamples to a one-dimensional account.

**Classification: B — MECANISMO PARCIAL.**  The frozen capability geometry is
coherently associated with discovery cost through the productive and
discriminative opportunities it makes available, including the S001/S002
comparison.  The static geometry summaries do not, by themselves, determine
the three-period belief-state control value.

### Novelty guard

CES is a purchased physical layer.  Bayes updating and belief-state control
are standard.  Discriminability, Gaussian KL, and a production--information
Pareto frontier are standard tools.  DISCOVER-v0 remains adaptation within a
known frame: `theta` belongs to a known two-member family and Bayes only
identifies which member governs production.  It does not demonstrate adaptive
reframing.  The specific question isolated here is whether collective
capability structure conditions what evidence the collective can produce
through its own actions.

## Sequential DP dissection

The final derived audit reuses the unchanged order-31 Gauss--Hermite
belief-state DP.  For every visited belief node and every tied optimal action,
`discover_sequential_decomposition.csv` records

```text
g          = b mu1 + (1-b) mu2
g_max      = max_X g(b,X)
c_exp      = g_max - g
Q_future   = E[V_(h-1)(b')]
Q_noinfo   = (h-1) max_X g(b,X)
VOI        = Q_future - Q_noinfo.
```

Here *frozen belief* means that the posterior is held at the current `b` for
all remaining periods while the immediately best production action is used.
It is a comparison baseline only; the UNKNOWN policy is unchanged.  The full
audit has 114,874 node--optimal-action rows.  Its maximum absolute Bellman
residual is `8.88e-16`, and the maximum residual of

```text
Q(X*) - [g_max + Q_noinfo] = -c_exp + VOI
```

is `4.44e-16`.

`discover_belief_trajectories.csv` gives, at every decision time, deterministic
mixture-quadrature expectations and 5/50/95% posterior-belief quantiles.  It
reports expected belief, entropy, distance from `.5`, action-selection mass
(splitting exact ties symmetrically), reward, experimentation cost, and local
VOI.  No representative continuous-observation trajectory is selected.

### Sequential evidence

S001 has expected cumulative experimentation cost `0.014091`, local-VOI sum
`0.476941`, entropy reduction `0.692975`, and reward recovered after posterior
updating `0.438904`.  S002 pays zero expected experimentation cost, with
local-VOI sum `0.394001`, entropy reduction `0.693086`, and recovered reward
`0.393976`.  Thus both learn rapidly, but S001 has a costly initial compromise
and a larger continuation opportunity; this is the dynamic route behind their
different discovery costs, not a new scalar score.

The static counterexamples are also resolved more specifically.  S001 and
S003 share `max_d=9`, but S003's UNKNOWN policy stays at belief `.5`: its
entropy reduction, local VOI, and recovered reward are numerically zero,
despite `C_D=0.218947`.  Its discovery cost is therefore the unrecovered cost
of acting under a known unresolved model family.  By contrast S001 learns and
subsequently recovers reward.  Among the `max_d=12` cases, S016/S021 attain
near-complete posterior concentration but have zero VOI and zero `C_D`: their
information has no operational value because it does not improve later
decisions.  S019/S028 instead have local-VOI sum `0.341185`, recovered reward
`0.340796`, expected experimentation cost `0.042872`, and `C_D=0.214566`.

Across 31 configurations, descriptive Pearson correlations of `C_D` with
expected cumulative experimentation cost, local-VOI sum, entropy reduction,
recovered reward, and final expected distance from `.5` are respectively
`+0.566`, `+0.886`, `-0.151`, `+0.880`, and `-0.153`.  Local VOI terms overlap
across decision nodes and are diagnostic rather than additive welfare
components.  These remain descriptive associations without causal or
inferential claims.

**Final classification: B — MECANISMO PARCIAL.**  The sequential
belief--action--belief audit explains why static diagnosticity alone fails:
information must be obtainable at an acceptable immediate cost and must change
later exploitable action choices.  It improves the account of the observed
regimes, but a non-learning unresolved-policy regime such as S003 retains a
substantial discovery cost; the audit does not justify a universal scalar or
an adaptive-reframing claim.  At `H=1`, operational future VOI is zero.  With
identical theta types, posterior updating, VOI, and discovery cost vanish.
