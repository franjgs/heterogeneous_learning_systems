# META-VOC: allocation of prospective computation in HLS

Scientific record for a potential journal manuscript, including completed
confirmatory results. See the separate
[`C3-META-VOC-CONF-v1` protocol](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_PROTOCOL.md)
for the choices fixed before confirmatory histories were generated.

## 1. Research motivation

An adaptive team can spend computation to anticipate how a current assignment
changes future information and capability. That computation may be useful at
some states and unnecessary at others. The experiment asks whether information
available before a decision can route computation toward states where the
additional deliberation has better realized sequential consequences than
state-independent invocation at a similar measured computational cost.

## 2. Hypothesis and provenance

For a team capability state `S`, belief `b` and known remaining clock `tau`,
the existing supervised predictor may rank decisions by prospective
Q11-minus-Q00 advantage. Dividing its positive prediction by the measured
incremental computation estimate gives a simple routing score. The scientific
test compares this ex-ante ranking with independent random routing.

The **primary** contrast is `META-VOC-50 − RANDOM-50`, selected after
development results were inspected. The fresh-history evaluation was frozen
before confirmatory outcomes, but the primary operating point is not a fully
prospectively selected hypothesis. The 25% and 75% points are reported as
secondary fixed comparisons.

## 3. HLS laboratory

The frozen laboratory has three agents and two capability dimensions. A
current assignment `X` allocates exposure through the existing 64-action
space. The true physical problem `z=(p,1−p)` maps capability-weighted outputs
to latent expected production `mu_true` through CES production with
`rho=0.5`. The agent represents the problem using the finite hypothesis
repertoire `{(.8,.2),(.5,.5),(.2,.8)}` and updates its belief with the
existing Gaussian likelihood after a noisy observation with `sigma=0.10`.

Capability development follows MIS-v2 for the selected exposure:

`F(S,X)[i,k] = 1 − (1−S[i,k]) exp(−lambda X[i,k])`,
where `lambda=−log(1−eta)` and `eta=0.35`. Within each history, capabilities
persist between problems while beliefs reset to the uniform prior. The
Campaign 3 generator supplies a 12-problem sequence from the frozen
STAY/MOVE/RETURN kernel. The physical generator domain is an experimental
subset of the broader frozen physical problem domain. All policy comparisons
use the same physical problem and standard-normal observation innovations
per matched base history. The policies nonetheless experience different
observations and subsequent states when their actions differ.

The internal planner's immediate target is expected latent production under
its belief, which can differ from external production under the true problem.
The sequential outcome reported here accumulates `mu_true`, not noisy
observations.

## 4. FAST and DEEP decision operators

Let `A` be the 64 frozen assignments, `R_z_hat_m(S,X)` predicted CES
production under internal hypothesis `m`, and

`g(b,S,X) = sum_m b_m R_z_hat_m(S,X)`.

FAST returns the first action in the frozen enumeration within the existing
`EXACT_TOL=1e−10` tie rule of `max_X g(b,S,X)`. This is action-equivalent to
the Q00 prospective policy because its two-stage continuation does not
depend on the current candidate action. FAST computes the immediate optimum
directly; it does not run prospective Bayesian branches, capability
transitions or terminal action searches.

DEEP is the unchanged Q11 `INFORMATION_AND_DEVELOPMENT` operator. For a
nonterminal current decision it evaluates

`Q11_2(b,S,X) = g(b,S,X) + sum_m b_m sum_{j=1}^3 omega_j
                 max_U g(B(b,S,X,r_mj), F(S,X), U)`.

The `r_mj` use the frozen three-node Gauss–Hermite construction for the
current predicted observation. The posterior likelihood uses current,
pre-development `S`; `F` is the prospective MIS-v2 transition. DEEP chooses
with the same action space and tolerance. The planner has effective decision
windows 2,2,1 within each three-decision problem and does not look across a
problem boundary. On the terminal decision all policies execute FAST, since
the operators select the same action there.

## 5. Frozen META-VOC operator

The existing standardized linear Ridge predictor uses only the six entries
of `S`, three belief masses and `tau/36`, in frozen feature order
`s11,s12,s21,s22,s31,s32,b0,b1,b2,tau`. Its fitted alpha is `10.0`.
The model predicts a C3.2 single-rollout Monte Carlo Q11-minus-Q00
production advantage under Q11 continuation. It is a *proxy*, not an
unbiased estimate of the realized recursively adaptive sequential value of
invoking DEEP.

META-VOC routes by

`score(S,b,tau) = max(0, predicted_advantage(S,b,tau)) /
                  estimated_extra_seconds(remaining)`.

The denominator is the frozen median DEEP-minus-FAST timing from a small
hash-fixed VALIDATION state sample: `0.209201959 s` at remaining 2 and
`0.20978829100000002 s` at remaining 3. It captures clock-stratum cost,
not finer dependence on `S` or `b`; machine timing is noisy. The three
score thresholds were selected once on 1,400 nonterminal VALIDATION states:
25% `0.22917335372443143`, 50% `0.16708983036248765`, 75%
`0.11085071239096865`; exact feature-hash tie cutoffs are retained in the
freeze manifest. Once META-VOC chooses FAST, it does not compute DEEP.
No computational cost is converted into production units.

## 6. Confirmatory methodology

The original frozen partitions define four crossed generalization domains:
G1 development teams × development kernels, G2 development teams ×
held-out kernels, G3 held-out teams × development kernels, and G4 held-out
teams × held-out kernels. Their complete factorial sizes are 420, 200, 168
and 80. One new independent exogenous history is generated per cell, for 868
matched histories. No held-out identifier was used in fitting or
calibration. The G2 kernel combination tests compositional/interpolative
generalization; G3 is a geometric team-space stress test within the same
team domain. G4 combines these two frozen held-out axes.

Eight policies independently evolve `S`, `b`, assignments and visited states:
FAST, DEEP, and META-VOC/RANDOM at 25%, 50% and 75%. All receive the same
exogenous physical and noise-innovation streams within each base history.
Confirmatory RANDOM has a separate pre-execution adapter: independent,
stored SHA-256 priorities invoke DEEP with fixed nominal probabilities
`.25`, `.50`, `.75`. The development RANDOM policy instead retrospectively
matched META-VOC's call count. The development algorithm and its artifacts
remain intact; the confirmatory RANDOM probabilities are fixed without
looking at confirmatory META routes or rewards.

The primary paired outcomes are cumulative `mu_true` and measured seconds of
decision computation per history for META-VOC-50 minus RANDOM-50. Each
history is resampled as one unit. The global contrast averages G1–G4 with
equal weight, and 2,000 domain-stratified paired bootstrap resamples with
seed `20261016` give percentile 95% intervals. Domain-specific contrasts,
other points, constant baselines, latency and invocation rates are fixed
secondary outputs. One history/cell limits precision and cannot isolate
within-cell stochastic variability from variation across the fixed grid.

Timing uses uncached `perf_counter_ns` around the chosen FAST/DEEP operator
and predictor inference; it excludes physical simulation and file I/O.
Parallel execution can affect wall time. There is no predefined equivalence
margin, so similar measured costs cannot establish equivalence.

## 7. Development evidence (separate from confirmation)

C3.3 fitted the Ridge model using 6,300 TRAIN states, selected alpha using
VALIDATION, and evaluated DEVELOPMENT_TEST once. On fresh development
histories the first selector routed overwhelmingly to Q11. The subsequent
FAST/DEEP/META prototype measured META invoking DEEP in 97.07% of its
nonterminal decisions, a negative result for substantial computation
avoidance under that routing rule.

The development META-VOC comparison then used 420 fresh development-only
team × kernel histories. At exact *retrospectively frequency-matched*
RANDOM call counts, the paired mean cumulative production differences
META-VOC minus RANDOM were `+0.1281` (95% interval `[-0.0522,+0.2979]`)
at 25%, `+0.2337` (`[+0.1030,+0.3686]`) at 50%, and `+0.1163`
(`[+0.0090,+0.2307]`) at 75%. These observations motivated this new
evaluation, including the post-development designation of 50% as primary.
They do not form part of its confirmatory bootstrap or verdict.

## 8. Confirmatory results

The frozen design completed 868 new matched histories across G1/G2/G3/G4
(`420/200/168/80`), producing 6,944 policy runs and 249,984 decisions.
The primary equal-domain paired contrast, META-VOC-50 minus RANDOM-50, is
`+0.1167` cumulative `mu_true` per history (95% percentile interval
`[+0.0310,+0.2013]`) and `−0.1924` measured computation seconds per history
(`[-0.3539,−0.0228]`). The corresponding absolute equal-domain means are
`54.1445 mu_true / 2.5660 s` for META-VOC-50 and
`54.0278 mu_true / 2.7584 s` for RANDOM-50.

| Domain | Histories | META-VOC-50 − RANDOM-50 `mu_true` [95% interval] | Measured seconds [95% interval] |
|---|---:|---:|---:|
| G1 | 420 | +0.2053 [+0.0712,+0.3394] | +0.0354 [−0.1576,+0.2345] |
| G2 | 200 | +0.3101 [+0.1158,+0.5030] | −0.0038 [−0.2836,+0.2912] |
| G3 | 168 | −0.0267 [−0.1643,+0.1015] | −0.4461 [−0.7695,−0.1394] |
| G4 | 80 | −0.0218 [−0.2372,+0.1968] | −0.3552 [−0.8217,+0.1027] |

The fixed secondary global production contrasts at 25% and 75% are
`+0.0448 [−0.0437,+0.1388]` and `+0.0310 [−0.0297,+0.0942]`;
neither interval excludes zero. Their measured-computation contrasts are
`−0.1865 [−0.2983,−0.0684] s` and
`−0.2361 [−0.3878,−0.0872] s`. At the 25% point, G4's secondary
production contrast is negative, `−0.1152 [−0.2233,−0.0012]`.

| Policy | Equal-domain cumulative `mu_true` | Measured s/history | Equal-domain nonterminal DEEP rate |
|---|---:|---:|---:|
| FAST | 53.1911 | 0.0143 | 0% |
| DEEP | 54.5308 | 5.5785 | 100% |
| META-VOC-25 | 53.6839 | 1.1831 | 21.27% |
| RANDOM-25 | 53.6391 | 1.3696 | 24.50% |
| META-VOC-50 | 54.1445 | 2.5660 | 46.43% |
| RANDOM-50 | 54.0278 | 2.7584 | 49.80% |
| META-VOC-75 | 54.3427 | 3.8584 | 70.53% |
| RANDOM-75 | 54.3117 | 4.0945 | 74.79% |

The primary rates are not exactly frequency-matched: pooling all
nonterminal decisions, META-VOC-50 invoked DEEP 10,062/20,832 times
(48.30%), RANDOM-50 10,408/20,832 times (49.80%). The displayed rates
average the four domains equally; the pooled ratios weight histories by
domain size. Selector inference is included in META timing (mean 0.000766
s/history at 50%); the fixed-route RANDOM baseline has no predictor cost.
The equal-domain median decision latencies are 0.414 ms and 0.398 ms,
respectively; Q95 latencies are 233.34 ms and 234.39 ms. All domain and
policy latency distributions, paired FAST/DEEP contrasts and complete
secondary operating-point tables are in the separate
[confirmatory results report](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md)
and its linked machine tables.

Four reproducible vector figures show the [routing architecture](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure1_architecture.svg),
the [performance–cost curve](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure2_performance_cost.svg),
the [primary domain contrasts](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure3_primary_domain_effects.svg),
and [invocation rates](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis/figure4_invocation_rates.svg).

## 9. Interpretation

**Demonstrated within this fixed laboratory:** the primary global
equal-domain contrast meets the pre-execution joint rule for
**CONFIRMATORY EVIDENCE FAVORABLE**: its paired production interval is
positive and its measured-computation interval is negative. The policy uses
only ex-ante `(S,b,tau)` to route decisions; RANDOM priorities were fixed
independently of future META routes and outcomes. G1 and G2 show positive
production contrasts; G3 and G4 intervals include zero. This is a measured
joint contrast between two frozen rules, not proof that the benefit per
individual DEEP invocation is higher under an exactly equal call budget.

**Plausible but unproven explanation:** state information may help place
costly Q11 computations where they matter for sequential production in the
represented development-team domains. The held-out-team findings do not
establish transport of this advantage to all team geometries. Lower META
invocation rates in G3/G4 could contribute to measured cost differences.

**Unsupported:** universal META-VOC superiority, exact performance or cost
equivalence at any point, optimality of the Ridge score, or a causal account
of which state dimensions produce the observed contrast. The 50% primary
designation followed development inspection; this limits a fully
prospective confirmatory interpretation even though these histories and the
analysis rule were frozen before execution. No result was used to
recalibrate the algorithm.

## 10. Limitations and unsupported inferences

The Ridge target is a single Monte Carlo counterfactual under a fixed Q11
continuation, whereas the sequential selector subsequently changes its own
state distribution. Its predicted advantage is not an exact adaptive value
of computation. The cost denominator is a clock-stratified timing estimate,
not a full state-conditional cost model. This experiment tests frozen CES,
Bayes, MIS-v2 and generator assumptions, a finite team/kernel design, one
replicate per cell and machine-dependent wall time. The primary 50% point was
chosen after development inspection. Paired bootstrap intervals describe
uncertainty over these fresh histories within frozen domains; they do not
make the teams, kernels or physical assumptions a random sample of real
organizations.

Unsupported claims include universal metacontroller superiority,
equivalence to DEEP or RANDOM without a margin, an exact causal decomposition
of information and development, extrapolation outside the frozen team or
generator domains, and empirical realism of the model parameters.

## 11. Reproducibility

The [pre-execution manifest](../../results/foundations/campaign3_meta_voc_confirmatory/pre_execution_manifest.json)
stores SHA-256 hashes of the model, calibration,
policy implementations, simulator, generator, split CSVs, protocol and
analysis code; exact coefficients, feature order, thresholds, costs,
histories and RANDOM priorities; and the analysis/bootstrap seed. After
execution, the [execution record](../../results/campaigns/campaign3_meta_voc_confirmatory/execution_progress.json)
and [analysis manifest](../../results/campaigns/campaign3_meta_voc_confirmatory/analysis_manifest.json)
store raw and derived artifact hashes, worker count, software versions,
platform and processor. The pre-execution manifest SHA-256 is
`782c84f1cd454dc121ef5f6ff4f83d28565d6edd98f00bff1350032e55bce335`;
the raw runs/trajectories SHA-256 values are
`3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28`
and `b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498`.
The exact exogenous seeds and independent RANDOM priorities are in the
foundation allocation CSVs. Execution used 8 workers on macOS arm64,
Python 3.11.9, NumPy 1.26.4 and pandas 2.2.3; analysis used matplotlib
3.9.2. End-to-end execution took 2,719.5 s; timings within histories
were uncached `perf_counter_ns` measurements under parallel machine load.
The exact commands are:

```sh
python -m experiments.synthetic.campaign3_meta_voc.confirmatory --freeze
python -m experiments.synthetic.campaign3_meta_voc.confirmatory --verify
python -m experiments.synthetic.campaign3_meta_voc.confirmatory --execute --workers 8
python -m experiments.synthetic.campaign3_meta_voc.analyze_confirmatory --run
```

The first command refuses an existing freeze or output; the execution command
verifies frozen hashes and may resume only hashed completed batches of the
same run. Reproduction on a clean checkout should retain these namespaces
and source contents. Machine tables, PDF/SVG figures and both raw manifests
are kept under `results/campaigns/campaign3_meta_voc_confirmatory/`.

## 12. Publication positioning

A defensible contribution is the controlled evaluation of **where to spend
prospective decision computation** in this HLS laboratory: a frozen
state-based routing rule, an explicit computational baseline with nominal
invocation probabilities, paired independently evolving trajectories, four
predefined generalization conditions and actual computation measurements.
The contribution is the measurable allocation test and its limits, not the
mere existence or assumed novelty of a metacontroller.
