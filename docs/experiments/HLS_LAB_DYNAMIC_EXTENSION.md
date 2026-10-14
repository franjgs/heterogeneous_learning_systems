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
using the same exposure law; the default team still starts with perfect
estimates, but callers can supply a distinct estimate. LI can be disabled
independently. Organizational updates are performed only when requested and
supported by the organization interface.

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

No existing repository component estimates the six individual capability
values from observations. In particular, `finite_problem_belief.py` and the
DISCOVER Bayesian updates infer the latent reward/environment type, not
individual skills. A noisy team-level CES observation combines multiple
capabilities and action assignments, so it does not by itself identify each
expert's skills. The functional success observer is also aggregate and binary.
Treating either as an individual skill observation would add an unsupported
measurement model. Therefore this change deliberately does **not** implement
or claim a competence estimator.

`CompetenceInformationMode.ORACLE` is the explicit perfect-information
control: construction copies real capabilities into the decision estimate and
the runner rejects mismatched matrices. `PARTIAL` requires a separately
supplied estimate. During its run, real capabilities still evolve through the
unchanged MIS-v2 transition, but the supplied estimate is held fixed because
no identifiable skill observation is available to update it. This makes
misspecification visible instead of projecting the simulator's private
competence transition into organizational knowledge. Existing legacy and
ORACLE runs retain their earlier estimate-transition behavior.

Organizations can affect both performance and *environmental* information:
actions change production and thus the noisy CES observation, which is passed
through the existing `bayes_update`. They cannot thereby be said to acquire
individual skill information. The bounded reproducible check in
`experiments/synthetic/hls_lab_dynamic/competence_information_smoke.py` uses
initially incorrect estimates, shared task/type/noise streams, and existing
`GreedyAdaptive` and DISCOVER policies. Its outputs are engineering
diagnostics, not comparative scientific evidence.

Focused verification:

```bash
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/competence_information_smoke.py
```

The remaining scientific limitation is explicit: competence estimates cannot
currently improve from experience under partial information. Doing so requires
an authorized, observable individual-level signal and validated measurement
semantics; aggregate rewards are insufficient grounds to invent one.
