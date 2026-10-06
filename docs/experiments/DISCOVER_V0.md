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
