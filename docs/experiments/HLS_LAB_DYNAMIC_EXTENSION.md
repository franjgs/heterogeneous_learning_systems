# HLS Laboratory v1: dynamic scenario extension

This additive extension reuses `ProblemSpec`, the frozen 64-action catalogue,
`production_inputs`, functional evaluation, v1 episode/run records, and the
MIS-v2 exponential capability-gap law. It does not replace CE-23/24/25, G0,
DISCOVER, or MIS-v2, and it does not claim multi-step DISCOVER/G0 integration.

`DemandRegime` defines a fixed distribution over requirement vectors;
`generate_problems` uses a local seeded pseudo-random stream to materialize a
single exogenous sequence from a declared schedule. Policies compared by
`compare_organizations` receive the same initial team and exact same sequence.
Each run then develops its own capabilities and organization state, so later
experiences and trajectories may differ endogenously.

`LearningProfile` specifies one existing MIS-v2 `eta` per expert and
capability. The implementation converts each eta with the existing
`eta_to_lambda` and applies `capability_after_exposure`; the transition law is
unchanged. Real and estimated capability matrices are evolved separately
as specified by MIS-v2; estimate handling depends on the explicit information
mode documented below. The default team still starts with perfect estimates,
but callers can supply distinct estimates. LI can be disabled independently.
Organizational updates are performed only when requested and supported by the
organization interface.

The additive `UncertainProblem` / `run_belief_sequence` path composes
functional requirements with DISCOVER's existing two-type CES environment,
Gaussian observations, `bayes_update`, and finite-horizon
`unknown_policy_value`. Each problem has one hidden, fixed CES type; beliefs
reset at problem boundaries, while capabilities persist across decisions and
problems. A shared noise seed gives paired policies the same Gaussian
innovations. The latent type is simulator-only metadata; the decision view
does not contain it. This is uncertainty over the CES payoff type, not over the
visible functional requirement vector. H=1 is supported and does not alter
`ProblemSpec` or the CE-23 runner.

DISCOVER's frozen solver enumerates the complete 64-action catalogue, so this
path rejects tasks whose resource constraints make any catalogue action
infeasible. Its belief-state recursion assumes a fixed capability matrix over
its planning horizon, matching DISCOVER-v0; realized MIS-v2 updates still occur
between decisions but are not forecast by that recursion. The existing
Bayesian update infers the CES type, not individual competence. The functional
success observer remains separate from the noisy CES observation and does not
drive the Bayesian update. When supplied estimated competences differ from
real competences, the observation likelihood is evaluated at the estimate
while data are generated from physical truth; this is a misspecified
likelihood, not a Bayesian posterior over competence. The 64-action constraint
and fixed-capability planning approximation are the principal remaining
integration limitations.

Run the focused and CE-23 acceptance tests from the repository root:

```bash
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py tests/test_hls_lab_v1.py
```

Reproduce the bounded H=2 demonstration in a new output directory:

```bash
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/smoke.py \
  --output-dir /tmp/hls_lab_dynamic_smoke_reproduction
```

The frozen local demonstration has 8 task episodes and 16 decisions per
policy. Requirements shift from first-dimension-heavy to second-dimension-heavy
sampling halfway through. Both policies use the same problem/type sequence
and Gaussian innovations; every problem has two decisions and resets its
belief at the boundary. DISCOVER and `GreedyAdaptive` each recorded 16/16
functional successes in this deliberately small smoke fixture. Cumulative
realized CES rewards were 23.974973 and 13.178990, respectively; those values
are an execution check, not comparative scientific evidence. Individual real
and estimated skill trajectories are present in
`results/diagnostics/hls_lab_dynamic_smoke/episode_trace.csv`; its hash and
source hashes are in the adjacent manifest.

The dynamic tests include bounded paired checks for state-responsive
`GreedyAdaptive`, tabular `ExploreThenGreedy`, and the DISCOVER adapter on
pre-generated sequences. They verify environment/noise alignment, belief
updates and resets, H=1 compatibility, and distinct real/estimated states.
These are implementation checks only, not a scientific campaign or evidence
that any organization is generally superior. The source ZIP's `__pycache__`
files are intentionally not installed.

## Individual competence information audit

The laboratory stores `competence_real` and `competence_estimated` separately
in each `ExpertState`. The decision interface, `DecisionView`, exposes only
`estimated_competencies`; it has no real-skill, latent-environment, or outcome
field. The simulator uses real competencies to produce output and `mu_true`.
The organization receives the noisy scalar CES observation and maintains the
existing DISCOVER belief over the two CES environment types. That posterior is
not an estimate of any expert's individual capabilities.

No previous component estimated the six individual capability values.
`finite_problem_belief.py` and DISCOVER's Bayesian updates infer latent
reward/environment type, not individual skills. The new individual signal
therefore has explicit semantics tied to the already recorded per-agent
production:

\[
y_{ikt}=a_{ikt}c_{ikt}+\epsilon_{ikt},\qquad
\epsilon_{ikt}\sim\mathcal N(0,\sigma_{obs}^2).
\]

It is a separate sensor channel, not a change to production or aggregate CES
reward. The simulator creates each reading from the pre-MIS real skill; the
organization receives only the reading and assigned effort. If effort is
zero, the estimator does not update. Sensor innovations are SHA-256 keyed by
seed/problem/decision/expert/capability, so a policy's actions cannot shift
other exogenous draws.

The minimal competence estimator is a bounded, three-support Bayesian model
per scalar skill. For prior mean \(m\) and variance \(v\), support is
\(\{0,m,1\}\), with endpoint mass \(q=v/[m(1-m)]\), weights
\((q(1-m),1-q,qm)\). This gives exactly the configured prior moments and
respects [0,1]. Given positive effort \(a\) and observation \(y\), posterior
weights are proportional to prior weight times
\(\exp[-(y-ac)^2/(2\sigma_{obs}^2)]\). Zero-noise positive-effort observations
collapse to \(y/a\), clipped only to the physical skill domain. Posterior
variance is recorded as the uncertainty summary.

Skills change between observations. In PARTIAL_LEARNING, posterior support
points are advanced using the public `LearningProfile.eta` and assigned effort
through the existing MIS-v2 law
\(f(c,a)=1-(1-c)e^{-\lambda a}\), with
\(\lambda=-\log(1-\eta)\). This is a prediction from declared public
parameters and the estimate—not access to the simulator's private transition.
The posterior variance is pushed through the same deterministic affine map.
If individual learning is disabled, no prediction occurs.

The three modes are `ORACLE` (exact competence known), `PARTIAL_STATIC`
(initial estimates and uncertainty never update), and `PARTIAL_LEARNING`
(individual observations update the estimate). Legacy `PARTIAL` remains an
alias for the earlier static control. The existing DISCOVER belief over CES
environment type remains separate and is updated from noisy aggregate CES
reward; it is not used as the skill posterior.

`experiments/synthetic/hls_lab_dynamic/competence_learning_smoke.py` is a
bounded engineering check using three heterogeneous experts, changing demand,
H=3, unequal MIS-v2 rates and shared exogenous streams. It logs true and
estimated skills, posterior variances, efforts, individual observations,
collective reward and environmental beliefs. In its fixed fixture,
PARTIAL_LEARNING changes some decisions relative to PARTIAL_STATIC. The
resulting performance difference is not evidence that learning generally
improves performance.

Focused verification:

```bash
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/competence_information_smoke.py
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/competence_learning_smoke.py
```

The individual-production observation is an explicit additional measurement
assumption. Its noise distribution and three-point prior are engineering
choices requiring calibration before scientific use. The posterior is exact
for its discrete prior/likelihood, not for an unknown continuous skill prior.
The public-MIS prediction assumes the configured learning rate is known to the
organization. Aggregate CES observations remain non-identifying for individual
skills and are deliberately not fed to this estimator.
