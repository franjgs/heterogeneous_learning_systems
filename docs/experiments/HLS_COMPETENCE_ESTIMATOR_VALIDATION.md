# HLS dynamic laboratory: competence estimator validation

## Scope and reproducibility

This is a bounded numerical validation of the existing one-skill,
three-support Bayesian estimator. It does not compare organizations and is not
a scientific campaign. It exercises six prespecified cases (A–F), with 128
fixed-seed replicates for the noisy cases. No CES, DISCOVER, MIS-v2, policy,
or historical result was changed.

Reproduce from the repository root:

```bash
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/validate_competence_estimator.py
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py
```

The run writes `results/diagnostics/hls_competence_estimator_validation/validation.json`;
it refuses to overwrite that directory. The artifact records exact scenario
parameters, replicate seed ranges via the seed base, convergence summaries,
Python/platform, source hashes, and the Git HEAD at execution. The script
prints the artifact SHA-256. The fixture uses `seed_base=20261014`; replicate
streams are `base + [0,127]` for B, `base + 1000 + [0,127]` for C,
`base + 2000 + [0,127]` for E, and `base + 3000 + [0,127]` for F.

## Mathematical audit

For a scalar competence, the current prior is discrete on
\(x=(0,m,1)\). Given requested prior variance \(v\), the endpoint mass is
\(q=v/[m(1-m)]\) and prior probabilities are
\((q(1-m),1-q,qm)\); this has mean \(m\) and variance \(v\). For a positive
effort \(a\), observation \(y\), and sensor standard deviation \(\sigma\),
the implementation applies

\[
w'_j = \frac{w_j\exp(-(y-a x_j)^2/(2\sigma^2))}
             {\sum_l w_l\exp(-(y-a x_l)^2/(2\sigma^2))}.
\]

The normalizing Gaussian constant cancels across support points. At zero
effort, weights are unchanged. At zero noise and positive effort, the
posterior collapses to \(y/a\), bounded to the physical domain.

The MIS-v2 map for known public \(\eta\) and effort \(a\) is
\(f(x)=1-(1-x)e^{-\lambda a}=1-e^{-\lambda a}+e^{-\lambda a}x\), where
\(\lambda=-\log(1-\eta)\). It is affine. Pushing all support points through
\(f\) and preserving their weights therefore gives exactly
\(E[f(X)]=f(E[X])\) and
\(Var(f(X))=e^{-2\lambda a}Var(X)\). The tests verify support, mean and
variance against these identities. Observation updates occur at pre-learning
competence; prediction follows the observation and the real MIS transition.

The implementation does not define credible intervals; interval coverage is
therefore **not applicable / not evaluated**. Reported posterior variance is
not an interval-coverage substitute.

## Controlled cases and results

Metrics are final-state summaries. For B, C, E and F they average 128
deterministic-seed realizations; A and D are exact single-path checks. Bias is
estimate minus truth. No population inference is intended.

| Case | Conditions | N | MAE | Bias | RMSE | Mean posterior variance | Final mean estimate / truth |
|---|---|---:|---:|---:|---:|---:|---:|
| A: constant, noiseless | truth .72; prior mean .40, variance .04; effort .50; one observation, sigma 0 | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | .7200 / .7200 |
| B: constant, noisy | truth .72; prior .40/.04; effort 1; sigma .10; 60 observations | 128 | .2812 | +.2613 | .2812 | .000056 | .9813 / .7200 |
| C: MIS-v2 growth | initial truth .25; prior .40/.04; effort .40; eta .20; sigma .03; 30 observe/predict steps | 128 | .0102 | +.0091 | .0103 | .000008 | .9576 / .9485 |
| D: no observations | truth/prior .60/.04; effort .10; eta .15; 30 public MIS predictions | 1 | <1e-15 | <1e-15 | <1e-15 | .015086 | .75435 / .75435 |
| E: badly wrong initial estimate | truth .95; prior .05/.002; effort 1; sigma .05; 20 observations | 128 | .0500 | +.0500 | .0500 | 0.000000 | 1.0000 / .9500 |
| F: small effort | truth .72; prior .40/.04; effort .05; sigma .05; 50 observations | 128 | .2533 | −.1361 | .2650 | .024856 | .5839 / .7200 |

Convergence summaries clarify the cases where more observations help versus
where support limits dominate:

| Case/checkpoint | MAE | Bias | RMSE | Mean variance | Mean estimate |
|---|---:|---:|---:|---:|---:|
| B, 1 observation | .2483 | −.0667 | .2616 | .02386 | .6533 |
| B, 20 observations | .2769 | +.1823 | .2801 | .00385 | .9023 |
| B, 60 observations | .2812 | +.2613 | .2812 | .000056 | .9813 |
| C, 1 step | .1272 | +.0910 | .1319 | .00563 | .4051 |
| C, 10 steps | .0623 | +.0522 | .0630 | .00019 | .7450 |
| C, 30 steps | .0102 | +.0091 | .0103 | .000008 | .9576 |
| F, 1 observation | .3102 | −.3102 | .3133 | .04040 | .4098 |
| F, 10 observations | .2511 | −.2288 | .2680 | .03879 | .4912 |
| F, 50 observations | .2533 | −.1361 | .2650 | .02486 | .5839 |

## Findings by requested condition

- **A — constant, noiseless:** the exact sensor equation recovers the truth
  from one positive-effort reading, regardless of whether truth was in the
  prior support. Posterior variance becomes zero.
- **B — constant, noisy:** the truth .72 is absent from \(\{0,.4,1\}\). The
  likelihood increasingly favors 1 (closer to .72 than .4). After 60 readings,
  mean error is .261 and variance is almost zero. This is a clear
  support-misspecification / overconfidence failure, not a mismatch in the
  coded likelihood.
- **C — growing competence:** the implementation observes before learning,
  then transforms posterior support using the public MIS-v2 profile. In this
  fixture, repeated observations reduce RMSE from .132 to .0103. This depends
  on the declared eta being correct and does not establish robustness to an
  unknown learning rate.
- **D — long observation gap:** with the exact initial competence represented
  by the prior mean and a known deterministic MIS-v2 law, 30 prediction steps
  retain a correct mean to floating-point precision. Variance contracts by
  the exact affine factor. This result fails as soon as the public transition
  model is wrong or contains unmodelled process noise.
- **E — badly wrong initial estimate:** the truth .95 is not in prior support
  \(\{0,.05,1\}\). Strong readings select endpoint 1, leaving .05 error and
  zero reported variance. The estimator improves greatly from the .90 initial
  error but is still overconfident because its support cannot represent .95.
- **F — small effort:** information scales with \(a^2/\sigma^2\). At effort
  .05 and sigma .05, 50 samples leave MAE .253 and posterior variance .0249;
  convergence is slow and the support still prevents representing .72.

## Audit verdict and limitations

No implementation defect was found in Bayesian reweighting or MIS support
transformation; no estimator change was made. Unit tests cover zero effort,
zero-noise recovery, bounded estimates, affine MIS moment propagation,
coordinate-keyed reproducibility, and the documented finite-support failure.

The estimator works exactly for noiseless positive-effort observations and
predicts competence exactly across unobserved intervals **conditional on** a
correct deterministic public MIS-v2 profile and a correctly represented
posterior. With noisy data, its posterior is only as plausible as its fixed
three-point support. It can assign almost zero uncertainty while remaining
substantially wrong whenever the real skill lies between support points. Small
effort weakens information. Unknown eta, stochastic competence transitions,
sensor bias, and interval calibration were not evaluated. The discrete prior
must not be treated as validated for scientific inference without further
authorization and calibration.

## Three-point versus configurable grid estimator

The historical `three_point` implementation remains the default. An explicit
`competence_estimator="grid"` option in `run_belief_sequence` uses a uniform
mesh (default 101 points) and the same Gaussian likelihood and MIS-v2 push-
forward. The prior's three masses are linearly projected onto adjacent mesh
points; this preserves its mean and approximates its variance. A uniform mass
of $10^{-12}$ is mixed in so every mesh point has positive prior probability.
This avoids structural exclusion of an interior truth while changing prior
moments by less than $10^{-12}$. This tiny floor is not protection against a
severely misspecified/narrow prior.

Reproduce the paired-seed A–F comparison:

```bash
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/compare_competence_estimators.py
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py
```

The comparison writes a new, non-overwriting artifact to
`results/diagnostics/hls_competence_estimator_grid_comparison/comparison.json`.
Both estimators receive identical scenarios and Gaussian innovations. The
90% intervals are equal-tailed discrete posterior intervals; coverage is
empirical over the fixed scenario replicates, not a population confidence
statement. Timings are single-process wall-clock diagnostics, not a benchmark.

| Case | Estimator | MAE | Bias | RMSE | Posterior variance | 90% coverage | Time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| A | Three-point | 0.0000 | 0.0000 | 0.0000 | 0.000000 | 1.000 | 0.00003 |
| A | Grid-101 | 0.0000 | 0.0000 | 0.0000 | 0.000000 | 1.000 | 0.00011 |
| B | Three-point | 0.2812 | +0.2613 | 0.2812 | 0.000056 | 0.000 | 0.028 |
| B | Grid-101 | 0.0098 | +0.0004 | 0.0123 | 0.000167 | 0.961 | 0.304 |
| C | Three-point | 0.0102 | +0.0091 | 0.0103 | 0.000008 | 0.055 | 0.017 |
| C | Grid-101 | 0.0102 | +0.0091 | 0.0103 | 0.000008 | 0.055 | 0.217 |
| D | Three-point | <1e-15 | <1e-15 | <1e-15 | 0.015086 | 1.000 | 0.00006 |
| D | Grid-101 | <1e-12 | <1e-12 | <1e-12 | 0.015086 | 1.000 | 0.00068 |
| E | Three-point | 0.0500 | +0.0500 | 0.0500 | 0.000000 | 0.000 | 0.008 |
| E | Grid-101 | 0.0498 | +0.0498 | 0.0498 | 0.000014 | 0.023 | 0.085 |
| F | Three-point | 0.2533 | −0.1361 | 0.2650 | 0.024856 | 0.445 | 0.017 |
| F | Grid-101 | 0.2533 | −0.1361 | 0.2650 | 0.024856 | 0.445 | 0.215 |

The grid resolves the specific support misspecification in B: truth .72 is
represented, and both error and interval coverage improve substantially. It
does not improve cases whose data are weak relative to the prior (F), where
the posterior remains near its prior. In E, the highly concentrated prior
near .05 assigns only the tiny floor to .95; 20 observations do not overcome
the resulting prior odds, and the posterior remains overconfident. In C,
frequent updating under the same deterministic transition law has very low
fixed-truth interval coverage; this shows that correct mean tracking in one
scenario does not establish calibrated uncertainty. The grid costs roughly
7–13× more in these small runs and is not uniformly superior. Unknown
transition rates, process noise, and prior-model calibration remain unresolved.

## Full-suite failures observed during follow-up

`PYTHONPATH=src:. pytest -q` produced 1163 passes and 13 failures in 314.33 s.
These failures are outside the dynamic-estimator integration and must not be
masked by refreshing frozen hashes:

| Tests | Classification | Evidence |
|---|---|---|
| `test_every_foundation_result_has_consistent_manifest` | Stale inventory expectation / extra existing result artifact | The test expects 11 `metrics.json` directories; 12 exist, including `b2_5_gutjahr_switching`. |
| B3, B4, B5 provenance tests; RQ0's two provenance tests | Stale parent hash/manifest | All fail at B2.3 `protocol_sha256` comparison between the frozen run header and current protocol source. |
| Campaign2 execution, preregistration source, theory source, C3 confirmatory integrity, strategy-discrimination source tests | Pre-existing worktree source-hash drift | Each reports `src/hls/finite_problem_belief.py`; it was locally modified before this task and was not changed here. |
| Campaign2 preregistration contamination test | Existing artifact contamination | The guard expects no campaign2 result files beyond preregistration, but the completed Campaign2 result tree is present. |
| Campaign2 state-coverage audit | Stale closure provenance | Frozen closure hashes for Campaign 2 documents/source no longer match the present files; the mismatch is not from this estimator change. |

No runner in this task writes to those historical result locations. The two
estimator-validation runners use separate diagnostic output directories and
refuse to overwrite them.
