# Campaign 2 — pre-experiment preregistration

## 1. Provenance boundary and question

Prerequisite and initial clean HEAD:
`c7071769cc583f3352305363eff2e6ade27de97e` — freeze Campaign 2 theoretical
framework. [C2.0](../theory/CAMPAIGN_2_THEORETICAL_SPECIFICATION.md) and its
`results/foundations/campaign2_theory/pre_experiment_campaign2_theory.json`
remain frozen. This commit specifies analyses **before any confirmatory
simulation, outcome inspection or preview**. It contains no Campaign 2 results.

Question: **when, why, and with what realized consequences does prospective
information and/or development anticipation change adaptive team decisions?**
The chain is structural state/world → internal opportunity landscape → decision
→ realized counterfactual consequence. This is not primarily a leaderboard.
Internal operator decompositions explain ranking algebraically, not as
independent empirical causes. Structural associations are not causal effects.

## 2. Frozen design and data boundary

| Dimension | Frozen specification |
|---|---|
| Scenarios | TR-PR, TR-PM, TR-G, TR-J, TR-R, TR-D, TR-HA, TR-HB |
| Definitions | Load `hls.campaign1_test_range.HISTORIES`, unchanged; six problems each |
| Probes | G00, G04, G05, G07, canonical existing definitions, not competitors |
| Policies | Q00, Q10, Q01, Q11, unchanged common operator |
| Development data | Already-observed seeds 0–9; excluded from confirmatory estimates |
| Confirmatory data | Exactly seeds 10–49 inclusive, 40 independent seed replications |
| Physics | N=3, K=2, rho=.5, sigma=.10, eta=.35, H=3, 64 actions |
| Representation | Z_hat=((.8,.2),(.5,.5),(.2,.8)), uniform prior per problem |
| Persistence | Real S persists; posterior resets each problem |
| Planning | Effective horizons 2,2,1, three-node Gauss–Hermite, frozen 1e-10 tie rule |
| Real transitions | Enabled MIS-v2 and Bayesian updating under ALL four policies |
| Performance | mu_true only; noisy observations drive inference, not performance reporting |

There is no STATIC, eta sweep, new scenario/configuration, policy or inference
change. Future full factorial: 8×4×4×40 = **5,120 closed-loop runs**, 1,280 per
policy; **92,160 real decision steps**. These are planned counts, not executions.
Inherited histories retain Campaign 0/1/Gate prior-observation provenance;
new seeds do not make this a new or out-of-sample world. Generalization is
conditional on this finite, deliberately constructed test range.

## 3. Primary reference population and weighting

**Primary reference rule:** every real pre-decision state of the Q11 closed loop
for every frozen scenario/configuration/confirmatory seed, without outcome
selection. All four operators are evaluated read-only on exactly that state.
This preserves the Gate's reference convention and avoids conflating policies'
different closed-loop state distributions. Other-policy visited states and any
union-of-policy-state analysis are secondary/exploratory, not replacements for
the primary population.

All 23,040 Q11 states are retained; **15,360 nonterminal states** (first and
second real decisions) form the DECISION POPULATION. There are 384 such states
per seed, balanced across 8 scenarios×4 configurations×6 problems×2 positions.
The 7,680 terminal states are collapse/regression controls, never primary
two-decision endpoints. Four eligible-state policy rows imply 61,440 primary
operator evaluations; full 64-candidate landscapes imply 983,040 candidate rows.

For each ab in {10,01,11}, the CONSEQUENCE POPULATION is the subset of these
same primary reference states with exact Xab!=X00. Its size is **unknown before
execution**. States with equal actions remain NULL/REGRESSION CONTROLS, not
members of the conditional consequence population. Evaluate/retain all three
two-decision contrasts, including null controls: 46,080 paired endpoint records,
92,160 branches and 184,320 branch production steps are planned. No terminal
endpoint or end-of-problem/history rollout is added.

The target distribution selects a seed uniformly, then one of its 384 eligible
states uniformly. All states have equal weight in the unconditional population.
Conditional estimands use **ratios of pooled event sums/counts**, not the
unweighted average of per-seed conditional means with varying denominators.
Seeds with no divergent event still belong to the sample and bootstrap. This
conditioning intentionally gives more conditional mass to seeds containing more
eligible divergent states; it does not make those states independent replicates.

## 4. Independence, CRN and retained data

The independent replication unit is **SEED**. Scenarios, configurations,
problems, decisions, overlapping counterfactual windows and policy comparisons
are repeated observations within seed. Confidence intervals must not treat
individual states as independent. The deterministic world/probe grid is not a
random sample of all teams or environments.

Preserve the Gate CRN rule: `Random(simulation_seed)`, one `gauss(0,1)` innovation
per real step; identical innovation stream across scenarios/configurations/
policies sharing that seed. At primary reference position k=3×problem+decision
(zero-based), each contrast uses the same innovations epsilon[k],epsilon[k+1]
from that stream. Since decision is 0 or 1, k+1 is within the same problem.
Both branches and all three contrasts share these innovations by position,
not their observations. No extra outcome-selected draw or rollout replication
is introduced. Planners never receive future innovations or true z.

Retain run/state keys; true z and existing C/N/M; b/S before and after; X;
continuous exposure; mu_true; observed reward and epsilon. On reference states
retain all four chosen actions, candidate Q values, exact equality and existing
reciprocal-regret/mutual-tie diagnostics; all 64 C/A_I/A_D/A_ID/Gamma values;
structural H(b), D_I, D_I_loss, H_S; internal DeltaQ; and complete two-branch
records with continuation policy. Missing C/N at the first problem remain
explicit missing values. No new composite adaptability/heterogeneity score.

## 5. Decision and consequence estimands

For ab in {10,01,11}:

```text
D_ab = 1[Xab != X00]
D_coupled = 1[X11 not in {X10,X01}]
DeltaQ_ab = Qab(b,S,Xab) − Qab(b,S,X00).
```

Use the actual frozen Q00 selection as the decision/counterfactual baseline.
Preserve C2.0's separate immediate-myopic reference for C and D_I_loss, including
the inherited constant-addition tolerance-boundary caveat. Record any mismatch
between these baseline action identities; do not override a frozen policy.
All exact divergences enter primary estimands, including any mutually
tie-equivalent selections. Report their counts and a descriptive non-tie
breakdown without replacing exact identity by a new threshold.

D_coupled is not restricted to the narrower Gate pattern “Q10=Q01=Q00 but
Q11 differs.” Retain the complete frozen taxonomy descriptively, but only D_ab
and D_coupled are confirmatory action outcomes. No Gamma sign restriction.

The primary realized endpoint is the unchanged C2.0 primitive:

```text
DeltaG_(t,2)^(ab|00) = [mu_true(t)+mu_true(t+1)]_force_Xab_then_pi_ab
                      −[mu_true(t)+mu_true(t+1)]_force_X00_then_pi_ab.
```

Both branches use real Bayes and enabled MIS-v2. True z is fixed and evaluated
directly, including unrepresented problems. Observations are mu_branch+sigma×
epsilon, not forced equal. Replanning at the second real decision uses actual
remaining−1: when initially remaining=3 it can anticipate the third decision,
whose reward is **not** counted. DeltaG is not an unbiased estimate of Q_2 or
the global value of a policy.

### Numerical equality fixed before outcomes

In exact mathematics, positive/zero/negative mean >0, =0, <0. Operational
numerical equality uses **EXACT_TOL=1e-10**, inherited unchanged from the frozen
laboratory, absolute on the raw production scale: zero iff |DeltaG|<=EXACT_TOL,
positive iff DeltaG>EXACT_TOL, negative iff DeltaG<−EXACT_TOL. Equality takes
precedence, giving a disjoint partition. This is a numerical-zero convention,
not a tuned scientific effect-size cutoff. Preserve every raw DeltaG and report
strict >0/=0/<0 counts secondarily to expose any near-zero discrepancies.
No empirical variance normalization or alternative optimized tolerance.

For each ab, conditional on D_ab=1, primary consequence estimates are:

1. p_ab_plus: proportion numerically positive.
2. mean_DeltaG_ab: raw sum of DeltaG / divergent count, including numerical zeros.
3. mean_negative_DeltaG_ab: raw mean among numerically negative cases, if present.
4. Numerical zero proportion (also report negative proportion).

Empty denominators yield explicit undefined/null values and zero denominator
counts, never zero effect estimates. Null-action controls must give identical
branches and zero return within precision; report any failure as an integrity
failure, not evidence about usefulness. Median, quantiles and full return
distributions are descriptive secondary statistics. Consequence-population
size is never inferred from or balanced using prior Gate divergence rates.

For divergent states report raw C(b,S;Xab), prevalence of numerically C>0 using
the inherited tolerance, mean C and its distribution. Raw strict-positive counts
are descriptive sensitivity diagnostics. C is expected-production opportunity
cost under belief, not a realized external investment cost. DeltaQ is
nonnegative only up to the frozen selection tolerance; retain raw values.

## 6. Confirmatory families

### H1 — information structure

Primary: D_10 prevalence and the distribution of frozen Hypothesis-Conditioned
Myopic Regret D_I_loss in D_10=1 versus D_10=0. Estimate differences as
divergent minus non-divergent **pooled mean and median** D_I_loss, with
seed-bootstrap intervals. Report complementary H(b) and D_I distributions
against D_10 descriptively. No iff rule, causal claim or A_I-ranking tautology
counts as empirical confirmation. Null/weak relationships must be retained.
The optional logistic model is **not included in this confirmatory plan**;
if fitted later it is exploratory, not a substitute for these direct estimates.

### H2 — development structure

Primary: D_01 prevalence, H_S distributions for D_01=0/1, and their pooled
mean contrast with seed-bootstrap uncertainty. Retain headroom's median and
distribution descriptively. Characterize all-action A_D ranges and the
selected-action differences A_D(X01)−A_D(X00) versus immediate cost, without
calling the algebraic ranking relation an empirical test. Report frozen
scenario/problem-position/configuration stratification as descriptive structural
characterization, not winner comparisons. Strong headroom separation is a valid
finding contrary to the working expectation; no new geometry scalar is allowed.
Observational separation cannot establish headroom's causal sufficiency.

### H3 — prospective coupling

Primary: prevalence of D_coupled among all eligible nonterminal reference
states with seed-bootstrap uncertainty. Characterize Gamma, A_I/A_D/A_ID, C
and frozen structural descriptors without Gamma>0 or Gamma(X11)>C(X11)
requirements. If zero coupled decisions occur, explicitly state that the
development/Gate coupled-only behavior did not replicate in the confirmatory
reference population. Zero prevalence is not rescued by new definitions,
thresholds or different state generators.

### H4 — internal preference versus realized consequence

Central consequence family: the three conditional DeltaG contrasts and their
direct estimands above. Report DeltaQ versus DeltaG scatter/distributions and
pooled Pearson association with seed-bootstrap intervals (undefined if either
variable has zero variance). M is experimenter-only, a **non-directional**
moderator, never an input to a policy. Secondary confirmatory moderation for
each ab is the fixed unstandardized OLS model on D_ab=1:

```text
DeltaG = beta0 + beta1 DeltaQ + beta2 M + beta3 (DeltaQ*M) + residual.
```

Use equal observation weights within the conditional population and the same
seed-bootstrap for coefficient uncertainty, not naive state-level standard
errors or p-values. Fit with `numpy.linalg.lstsq(design, response, rcond=None)`;
the design has four columns in the displayed order. Returned rank below four
or a nonfinite fit is explicitly non-estimable;
do not drop terms, regularize, change transforms or select alternate models to
rescue them. Report undefined resample frequencies. Coefficients are secondary
to paired counterfactual estimates and are not observational causal effects.
Other structural-descriptor moderators are descriptive/exploratory; no outcome-
selected confirmatory regression is permitted.

## 7. Bootstrap, undefined samples and multiplicity

Freeze **10,000 nonparametric seed bootstrap replicates**, analysis RNG seed
**20261007**, `numpy.random.Generator(numpy.random.PCG64(20261007))`. This is
an analysis seed, not a simulation seed; no draws are made in this freeze.
For each replicate select 40 seed IDs with replacement, retaining **every**
observation in every selected seed block with its multiplicity. Use one shared
resampling index matrix for all estimands/contrasts and preserve it with the
future analysis provenance. Recompute pooled conditional ratios, contrasts,
medians, associations and specified secondary coefficients on each resample.

Use percentile 95% intervals at .025/.975 with linear quantile interpolation
(`numpy.quantile(..., method="linear")`). Report counts/fractions of undefined
resamples for every estimand. When some are undefined, compute percentiles on
defined replicates **and label the interval conditional on estimability**; never
silently drop missing resamples. If all are undefined, interval is null. Full-
sample undefined estimands also remain null. Do not introduce a data-dependent
minimum-event rule or switch bootstrap methods.

Primary families are H1, H2, H3 and H4, not dozens of independent significance
tests. Report effects and marginal uncertainty intervals, not unadjusted p-value
fishing or family-wise-confirmation claims. Intervals are not simultaneous or
family-wise adjusted. No binary hypothesis verdict depends solely on a
regression/CI crossing. Detailed scenario×configuration×policy tables and
secondary moderator narratives remain descriptive/exploratory unless explicitly
listed above. State counts do not enlarge the independent sample beyond 40 seeds.

## 8. Secondary outcomes and negative evidence

All four closed-loop cumulative/per-problem mu_true trajectories may be reported
as secondary system-level evidence. They do not replace paired-state analyses.
Retain universal leaders, nulls, near-nulls, negative returns, failed replication,
ties, reconvergence and non-estimable models. No configuration or scenario is
selected for large effects. G00/G04/G05/G07 remain probes; all eight scenarios
remain the small controlled test range, not an exhaustive taxonomy.

Exploratory unless separately preregistered later: DeltaG_problem/history,
detailed team narratives, new/post-hoc descriptors or geometry metrics,
thresholds, nonlinear models, ML importance, scenario-specific regression
searches, alternative reference populations and winner maps. The existing
four scenario contrasts remain structural/descriptive context; PR/PM does not
isolate mismatch and R/D does not isolate recurrence as a causal treatment.

## 9. Falsification and forbidden reinterpretation

- H1 weakens if information divergence lacks a reproducible relationship to
  the frozen pre-decision conflict descriptors; preserve weak/null estimates.
- H2 weakens if no interpretable structural distinction emerges beyond the
  algebraically defined A_D landscape. If headroom strongly separates states,
  report it rather than rescuing the expectation of insufficiency.
- H3 is not confirmed if no coupled decisions recur in seeds 10–49.
- H4 prospective usefulness weakens if divergent decisions yield predominantly
  non-positive realized returns; report event proportions and uncertainty,
  without requiring global Q11 superiority or suppressing policy-specific failures.

Do not require development usefulness, harmful mismatch, universal heterogeneous
superiority or global planning superiority. Gamma is not physical/team synergy,
causal interaction or dual-control value. DeltaG is not an additive mechanism
decomposition. No causal interpretation is assigned to moderator associations.

After execution, do not change hypotheses, estimands, populations, horizon,
continuation policy, CRN, scenarios, probes, policies, eta, physics, inference,
action definitions or bootstrap to improve outcomes. Alternatives must be
explicit exploratory analyses or a later study, never retroactive confirmation.

## 10. Execution boundary and validation

The accompanying machine-readable freeze is
`results/foundations/campaign2_preregistration/pre_experiment_campaign2_preregistration.json`.
Tests in `tests/test_campaign2_preregistration.py` check arithmetic, provenance,
frozen constants, analysis definitions and absence of research artifacts;
they do not execute a campaign, draw simulation innovations or inspect outcomes.
No runner or statistical analysis implementation is added by preregistration.

Before future interpretation require unique/complete run/state keys, CRN
alignment, frozen parameter/fixture hashes, unchanged four-mode semantics,
terminal action collapse, null-counterfactual equality, same continuation policy
in both branches, real Bayes/MIS invariance and valid probability vectors. Any
failure blocks scientific interpretation; do not repair physics or silently
exclude failed seeds/states. Computational retries must reproduce the same
seed and protocol, with provenance, not replace outcomes.

**Seeds 10–49 remain untouched. New Campaign 2 executions, scientific results,
outcome previews, run/trajectory CSVs, summaries and figures: ZERO.** C2.0 and
all historical artifacts remain unchanged. The future execution must reference
this preregistration commit/hash boundary. Stop after this freeze; execution
requires a separate explicit instruction.

Freeze validation: 112 selected tests passed (12 new static preregistration
checks plus 100 existing synthetic-unit, regression and provenance checks).
No selected test runs a confirmatory seed or the Campaign 2 factorial.
JSON/source hashes validate and `git diff --check` is clean. The full historical
suite is deliberately not run because some sequence tests use reserved seed
numbers; no historical test is weakened.
