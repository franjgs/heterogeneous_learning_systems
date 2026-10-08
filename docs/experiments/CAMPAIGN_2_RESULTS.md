# Campaign 2 — prospective adaptation study

**Attempt 1: execution integrity failure. Attempt 2: deterministic reconstruction
validated; preregistered analysis completed.**
The first execution attempt computed its planned factorial, but all seven raw
data tables were empty on disk at completion. The integrity gate failed with
`pandas.errors.EmptyDataError` before scientific analysis. In-memory counts
cannot validate retained runs or the required Q11-reference bank. No bootstrap,
H1–H4 estimate, result figure, or scientific classification was produced from
that attempt.
The user subsequently authorized diagnosis, I/O correction and an identical
reconstruction. See [the immutable incident and I/O diagnosis](CAMPAIGN_2_IO_INCIDENT.md).
The original `validation_failure.json` and failed output files are not overwritten.

## Scope and pre-results boundary

This is execution of [the frozen preregistration](CAMPAIGN_2_PREREGISTRATION.md),
commit `9cfb6891e73536a63694041711de56cbd147eed1`, using
[C2.0](../theory/CAMPAIGN_2_THEORETICAL_SPECIFICATION.md), commit
`c7071769cc583f3352305363eff2e6ade27de97e`.
Neither freeze is rewritten by this report. The scientific question is when,
why and with what realized consequences prospective information and/or
development anticipation changes decisions, not which policy wins.

The epistemic chain remains structural state/world → internal opportunity
landscape → decision → realized counterfactual consequence. Internal
opportunities reconstruct the planner by definition; their relationship to
its ranking is not independent empirical evidence or an external cause.

## Preregistered execution and estimands

Eight unchanged scenarios (TR-PR, TR-PM, TR-G, TR-J, TR-R, TR-D, TR-HA, TR-HB),
four probes (G00, G04, G05, G07), four frozen prospective restrictions
(Q00, Q10, Q01, Q11) and seeds 10–49 define 5,120 closed-loop runs.
Each run contains six problems × three real decisions. Every policy receives
real Bayesian updates and real enabled MIS-v2 development. N=3, K=2, rho=.5,
sigma=.10, eta=.35, 64 actions, the existing quadrature and tie rule are unchanged.
Belief resets uniformly at each problem; capabilities persist.

Primary state-conditioned results refer **only to Q11-reference states**:
23,040 states including 7,680 terminal collapse controls; 15,360 nonterminal
states (384 per seed) enter the decision population. Every eligible state has
four policy evaluations and the complete 64-action opportunity landscape.
The state bank is not a sample of the complete possible state space.

Exact selected-action identity defines D10/D01/D11 relative to Q00, and
D_coupled means X11 is neither X10 nor X01. Mutual tolerance-optimality is
reported separately, never used to exclude primary exact divergences.

For each of Q10/Q01/Q11, both branches force its first action versus Q00's,
then use that same prospective policy for continuation. Exactly two real
mu_true rewards within one problem are summed. Each branch uses its own
real belief and capability transition. CRN shares epsilon[k], epsilon[k+1]
from `Random(seed)` across branches, not realized observations. At a first
decision, the second decision can anticipate a third reward, but that third
reward is excluded from the primary two-reward endpoint.

All 46,080 pairs are retained. Equal-action null controls are excluded from
conditional consequence estimands, not deleted. Positive/zero/negative uses
the inherited absolute tolerance 1e-10; raw strict signs are also preserved.
Performance always means latent production mu_true, not noisy reward.

Uncertainty uses 10,000 whole-seed bootstrap draws, PCG64 seed 20261007,
shared across all estimates, with percentile 95% intervals (linear quantiles).
Each selected seed retains every relevant observation with its multiplicity.
Conditional estimates are pooled ratios, not averages of per-seed ratios.
Undefined resamples are counted; any interval on defined resamples is explicitly
conditional on estimability. Intervals are marginal, not simultaneous.

H1 compares hypothesis-conditioned myopic regret between Q10-divergent and
non-divergent states (means and medians); entropy/disagreement are complementary.
H2 characterizes headroom and structural strata alongside the algebraic A_D
landscape. H3 estimates coupled-action prevalence without Gamma sign assumptions.
H4 estimates conditional positive/zero/negative return rates, mean raw return
and mean negative return. Immediate cost is under belief, not an external
realized investment cost. Pearson DeltaQ/DeltaG and the unchanged OLS formula
DeltaG ~ 1 + DeltaQ + M + DeltaQ:M are secondary confirmatory analyses with
seed-respecting uncertainty. Rank-deficient fits remain undefined. No logistic
regression is included in the final frozen preregistration and none is added.

## Artifact and implementation provenance

The parent incident artifacts are under
`results/campaigns/campaign2_prospective_adaptation/`; reconstructed campaign
artifacts are separately under its `attempt_02/` subdirectory.
`execution_manifest.json` records the execution base commit and exact new
runner SHA256: the runner and results enter one local commit after validation,
so no intermediate unregistered execution commit is invented. The unchanged
frozen source manifests supply physics/inference/policy hashes.

`closed_loop_runs.csv`, `closed_loop_trajectories.csv.gz`, `reference_states.csv`,
`policy_evaluations.csv`, `counterfactual_results.csv`, and
`counterfactual_branches.csv.gz` preserve raw records distributed with the
repository. The large `opportunity_landscapes.csv.gz` raw artifact is retained
outside Git to avoid repository bloat; its exact SHA256 remains recorded in
`raw_completion.json`, `provenance.json`, and `validation_summary.json`.
`actions.csv` maps action IDs to exact canonical allocations. Missing
first-problem C/N and terminal-only diagnostics are explicit empty CSV fields.
`raw_completion.json` binds raw tables by SHA256; final provenance binds derived
outputs and source files. Compression is lossless, with deterministic gzip time.

The runner calls frozen C2.0/operator primitives. Scoped memoization uses
complete immutable arguments without rounding and copies cached dictionaries;
tests compare all candidate values and actions exactly against uncached calls.
No source under `src/hls/` is modified. Counterfactual transitions reuse the
authoritative C2.0 engine, not a duplicate physics implementation. The I/O-only
reconstruction privately stages and verifies tables before atomic publication.
Its closed-loop count gate precedes the deferred, unchanged counterfactual
calculations. An AST regression verifies that closed-loop generation has no
other change from the archived original runner.

Reproduction from the execution-source tree (output directory must not already
exist; never overwrite an archived run):

```sh
python experiments/synthetic/campaign2_prospective_adaptation/run.py --workers 8
python -m experiments.synthetic.campaign2_prospective_adaptation.validate
python -m experiments.synthetic.campaign2_prospective_adaptation.analyze
python -m experiments.synthetic.campaign2_prospective_adaptation.figures
```

For byte-level figure reproduction, strip trailing blanks from each generated
SVG line (the Matplotlib path serializer emits them). This postprocessing was
checked to leave both XML trees identical modulo nonsemantic path/text
whitespace. CSV action-table CRLF terminators are preserved, including the
failed-attempt evidence; narrowly scoped whitespace attributes recognize them
without rewriting archived bytes. These are serialization conventions, not
analysis or graphical-data transformations.

Validation precedes scientific interpretation. It checks the exact factorial,
unique keys, seed range, CRN, complete candidate/state coverage, real branch
transitions, two-reward endpoint, nulls, terminal collapse and unchanged source
hashes. The historical preregistration test requiring *no* Campaign 2 output
is deliberately not applicable after authorized execution; it remains unchanged.

## Confirmatory results

All quantities below use the validated reconstruction, not the failed attempt's
in-memory counters. Scientific interpretation began only after the count gate
and full retained-data validation passed. The same seeds 10–49 were replayed;
they are not described as untouched or as a new independent sample.

### Retained-data integrity

| Record | Validated count |
|---|---:|
| Closed-loop runs | 5,120 (1,280 per policy) |
| Real closed-loop decisions | 92,160 |
| Q11 reference states | 23,040 |
| Eligible nonterminal reference states | 15,360 (384 per seed) |
| Terminal collapse controls | 7,680 |
| Eligible-state policy evaluations | 61,440 |
| Complete candidate-action records | 983,040 |
| Counterfactual pairs, including nulls | 46,080 |
| Counterfactual branches / real branch decisions | 92,160 / 184,320 |

No duplicate/missing factorial cells, terminal divergences or CRN failures were
found. All 38,846 equal-action counterfactual controls returned exactly zero.
Independent branch-transition and branch-sum checks had zero discrepancy;
operator reconstruction and observation checks had maximum absolute error
2.220446049250313e-16; the cumulative MIS-v2 identity error was
1.1102230246251565e-16. Frozen source hashes passed. Q11's selected actions
match the frozen operator at every visited state; unchanged historical CURRENT
regression tests establish the operator's provenance. No immediate-myopic/Q00
baseline mismatch occurred. None of the exact divergences below was mutually
tie-equivalent to Q00 under the inherited diagnostics.

All intervals below are the preregistered whole-seed percentile 95% intervals.
There were **zero undefined resamples for every registered estimand**, including
the secondary Pearson associations and all four-column OLS fits. The full
precision estimates, distributions and intervals remain machine-readable.

### H1 — information structure

Q10 diverged from Q00 at 3,004/15,360 states: **19.557% [18.737, 20.365]**.
Mean hypothesis-conditioned myopic regret was .165062 in divergent versus
.048623 in non-divergent states. The pooled mean difference was
**.116439 [.113325, .119503]**; the median difference was
**.144449 [.140711, .147828]** (medians .174099 versus .029650).
Complementary descriptive means were H(b)=1.026391 versus .644723 and
D_I=.311867 versus .133767, divergent versus non-divergent.

**Interpretation:** H1 is supported within the Q11-reference population:
information-sensitive decisions were reproducibly associated with greater
hypothesis-conditioned decision conflict. Distributions still overlap; neither
an iff condition nor a causal effect of regret/entropy/disagreement is established.
The A_I ranking identity is not counted as evidence for H1.

### H2 — development structure

Q01 diverged at 1,172/15,360 states: **7.630% [7.214, 8.047]**.
Mean headroom was 2.453846 versus 2.026534, with pooled difference
**.427312 [.384810, .471392]**. Median headroom was 3 versus 2.178506
(descriptive). The distributions overlap: headroom ranges were
[.537834, 3] in divergent and [.423009, 3] in non-divergent states.

A direct descriptive structural control is available at the initial decision:
all four configurations have H_S=3 and the same uniform belief. Q01 diverges
from Q00 for G00/G05 in all such initial states, but not for G04/G07. This is
not a newly constructed geometry score or a subgroup promoted to a primary
estimand. It shows why global headroom alone cannot determine these decisions.
The all-action A_D ranges and A_D(X01)−A_D(X00) versus C are retained as
**algebraic mechanistic reconstruction**, not independent empirical causes.

**Interpretation:** H2 receives bounded support: higher headroom is associated
with development sensitivity, but equal headroom can coexist with opposite
decision outcomes across the frozen capability configurations. This does not
identify a causal sufficient set of state variables or show that development
anticipation pays off; that separate question is addressed by H4.

### H3 — prospective coupling

X11 was neither X10 nor X01 in **71/15,360 states**, prevalence
**.462% [.319, .618]**. Coupled decision behavior therefore replicated under
the frozen confirmatory definition. The narrower descriptive COUPLED_ONLY
pattern occurred 41 times; these two definitions are not interchangeable.

At the selected Q11 actions in the 71 coupled states, mean Gamma=.005478,
with range **−.008898 to .022394**. Mean A_I=.048507, A_D=.077928,
A_ID=.131913 and C=.035070. Coupling is non-separability of the planner's
continuation landscape, not physical/team synergy or a causal interaction.
No positive-Gamma restriction was imposed.

### H4 — internal preference versus realized two-reward consequence

All following estimates condition on the corresponding exact D_ab=1;
equal-action nulls are not mixed into these denominators.

| Policy | Divergent states | Positive return % [95% CI] | Mean DeltaG [95% CI] | Mean negative DeltaG [95% CI] |
|---|---:|---|---|---|
| Q10 | 3,004 | 74.567 [71.336, 77.811] | .162293 [.147572, .177096] | −.139327 [−.151007, −.127438] |
| Q01 | 1,172 | 45.990 [41.047, 50.598] | .001451 [−.019392, .019311] | −.120689 [−.139005, −.103993] |
| Q11 | 3,058 | 74.526 [71.294, 77.812] | .166874 [.153030, .180323] | −.145299 [−.157054, −.133306] |

Numerical-zero return prevalence was 0 for each divergent population. Negative
return rates were respectively 25.433%, **54.010%**, and 25.474%. Strict raw
sign counts coincide with the numerical partition: positive/negative counts
were 2,240/764, 539/633 and 2,279/779. The 38,846 separate null-action controls
remained exactly zero.

**Interpretation:** prospective information and coupled anticipation had
positive average realized two-reward consequences in their divergent reference
states, but roughly one quarter of these decisions had negative returns.
Q01's average was near zero with an interval spanning both signs, and a majority
of its observed divergent cases were negative. Thus prospective usefulness is
**mixed and weakened for development-only anticipation**, not guaranteed by
positive internal DeltaQ. This is not evidence that real MIS-v2 development
itself is harmful: every branch develops, and only the first selected action
is counterfactually changed. No global policy-value claim follows.

### Immediate opportunity cost and secondary confirmatory moderators

All divergent decisions incurred numerically positive immediate opportunity
cost under belief. Mean C was **.012978 [.012466, .013517]** for Q10,
**.008995 [.008652, .009371]** for Q01, and
**.013392 [.012863, .013934]** for Q11. This is not automatically an external
realized investment cost.

Pearson DeltaQ/DeltaG associations were .220585 [.167431, .278289],
.059936 [−.036773, .155943] and .198251 [.149960, .251384], respectively.
The weak Q01 association is retained, not rescued by another model.

The preregistered unstandardized OLS models were rank four. The M coefficients
and DeltaQ:M coefficients (secondary confirmatory, not causal) were:

| Policy | M coefficient [95% CI] | DeltaQ:M coefficient [95% CI] |
|---|---|---|
| Q10 | −.171630 [−.589475, .256873] | −3.005765 [−5.521977, −.506066] |
| Q01 | .929055 [.730688, 1.129274] | −23.095868 [−39.183755, −6.180162] |
| Q11 | −.137105 [−.628623, .337245] | −3.111181 [−6.184251, .050681] |

Mismatch does not support a blanket “larger M means worse return” conclusion:
the fitted association depends on policy and DeltaQ, and some intervals span
zero. Full coefficients, including intercepts and DeltaQ, are in
`bootstrap_intervals.csv`. These observational associations are conditional on
selected divergent Q11 states in the finite frozen range. No new predictors,
logistic model, thresholds or causal interpretation were added.

## Secondary system-level results

Cumulative closed-loop performance is secondary. Across the balanced design,
mean cumulative mu_true was Q00=26.233287, Q01=26.960274, Q10=27.468229 and
Q11=27.491069. The full scenario × probe × policy means and dispersion are
retained in `secondary_closed_loop_summary.csv`, not used as the primary
Campaign 2 endpoint. G07 remained the mean cumulative Q11 leader in all eight
scenarios; this continued dominance is preserved without a superiority claim.

The two figures, `decision_structure.svg` and `counterfactual_consequences.svg`,
are generated from machine-readable analysis outputs. They show structural
associations/decision prevalence and conditional return signs/means, not a
winner map. Source data, bootstrap draws and estimates remain available for
regeneration.

## Null, negative and exploratory boundary

Important retained null/negative findings are the 38,846 exact null controls;
Q01's near-zero average return and majority-negative divergent outcomes;
negative returns under Q10/Q11 despite positive internal advantage; and the
weak Q01 DeltaQ/DeltaG association. Descriptively, G04 and G07 in TR-PR have
zero divergence for all three prospective policies; G04 in TR-R also has zero
divergence. G07 in TR-R has zero Q10/Q11 divergence and one Q01 divergence.
These are useful insensitive regimes, not omitted failures. No divergent
numerical-zero returns or mutually tie-equivalent divergences were observed.

Descriptive policy patterns were ALL_SAME=12,190,
INFORMATION_SENSITIVE=1,957, DEVELOPMENT_SENSITIVE=125,
BOTH_SINGLE_ABLATIONS_CHANGE=1,047 and COUPLED_ONLY=41. These categories
describe actions, not additive causal contributions.
Detailed subgroup interpretations and policy patterns are descriptive or
exploratory, not promoted to confirmatory evidence. No end-of-problem/history
counterfactual, new state feature, nonlinear model or new threshold is added.

## Bounded scientific conclusion

**CAMPAIGN 2 — ROBUST POSITIVE WITH IMPORTANT NULL RESULT.** Campaign 2 is a
completed, integrity-validated mechanism-characterization study, not a policy
leaderboard. H1 is **SUPPORTED**: hypothesis conflict is associated with Q10
sensitivity, without constituting information value or a causal rule. Structural
H2 is **SUPPORTED**: global headroom alone does not characterize prospective-
development sensitivity. H3 is **SUPPORTED, LOW PREVALENCE**: coupled decisions
occurred in 71/15,360 states and mean prospective non-separability, not physical
synergy.

For realized consequences, Q10 and Q11 show **ROBUST POSITIVE conditional
realized benefit** under their preregistered two-reward contrasts. Q01's
realized usefulness is **NOT SUPPORTED**: its mean DeltaG is near zero, its
interval spans both signs, and only 45.99% of divergent decisions have positive
return. This does not imply that development generally has no value, that real
MIS-v2 development is harmful, or that information is intrinsically more
valuable than development. The policies differ only in prospective evaluation
and all branches retain real Bayes and real development.

Positive internal DeltaQ did not guarantee positive realized DeltaG; the
implication `DeltaQ>0 => DeltaG>0` is false in these data. Q11 superiority over
Q10 is **NOT ESTABLISHED**: their aggregates are close and no Q10-versus-Q11
superiority or equivalence test was preregistered. G07 leading mean cumulative
Q11 performance in all eight scenarios is a **REPLICATED SECONDARY OBSERVATION**,
not universal team superiority.

Conceptually: **prospective anticipation can have realized adaptive value, but
internal prospective preference does not guarantee realized benefit.** Every
state-conditioned conclusion is limited to the 15,360 Q11-generated reference
states and the frozen test range and physics. No single global PASS/PARTIAL/FAIL
criterion was preregistered, so the closure classification summarizes the
evidence without inventing a new gate or altering any result.

## Limitations

Inference is conditional on the frozen test range, four probes, Q11-generated
states, and this CES/Bayes/MPC/MIS-v2 architecture. The scenarios retain their
Campaign 0/1/Gate prior-observation classifications; new seeds do not make the
world itself out-of-sample. State moderators are observational, non-directional
for mismatch, and not causal. Gamma is an algebraic prospective coupling
residual, not physical/team synergy. Two-reward consequences are neither global
policy values nor unbiased estimates of the planner's subjective objective.
No universal superiority, optimal policy, empirical eta calibration, exhaustive
state-space characterization, or general causal value of information/development
is established. Campaign 3 and new policies are outside this task.
