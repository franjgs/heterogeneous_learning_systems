# SOCTRA–HLS: triage–organization coupling pilot

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Executive result

This separate, synthetic development pilot asks whether escalation-classifier
operating characteristics can change L2 work enough to alter the relative
outcomes of frozen D1, P1 and HLS-B (WAPS). It did **not** use individual
SOCTRA records or classifier predictions, train a classifier, or change the
historical SOC engine or policies. Recommendations are accepted automatically
as a controlled modeling assumption, not as a claim about GMV-CERT analysts.

The result is conditional rather than universally favorable to adaptation.
False-positive routing can dominate L2 offered work when need prevalence is
low: at the old empirical point, the expected recommendation fraction is
28.76% under the historical-evaluation prevalence and 30.80% under the
simulator's synthetic prevalence. At `rho_L1=0.85`, the implied L2 offered
load is already 1.77 and 1.90 respectively. Reducing `pFA` to 0.01 makes the
historical-prevalence case lightly loaded at L2, while the same `pFA` with
synthetic prevalence gives `rho_L2` about 0.33. In the tested overloaded L1
regime (`rho_L1=1.25`), the controller usually spends a material fraction of
L2 dispatch epochs in P1. On the primary integrated outcome, HLS-B is
indistinguishable from D1 at `rho_L1=0.85` in the old-point comparison, but
exceeds D1 in the overloaded old-point cells; it is only modestly above P1
there. These are exploratory, synthetic scenario results (10 paired seeds),
not evidence for a deployed SOCTRA model or operational GMV performance.

## Scope and provenance

- Frozen organizational reference: `20cffed6b7a325cb44b7e73b7295ad946be46982`.
- Source state from which this pilot branch was created: `642af6b6e7ffd3e076258a1f4c87722566919dc6`.
- Policies: D1, P1 and HLS-B/WAPS, unchanged. HLS-B remains at a 4 h window
  and 1.05/1.20 hysteresis thresholds.
- Triage: escalation only. The report classifier is outside scope.
- The old empirical classifier point (`274/344`, `29210/102182`) came from an
  older 102,526-alert evaluation. It is not the article-selected SOCTRA/AIAI
  classifier result and is not paired test-set prediction data for the
  independent chronological set of 14,449 alerts. Historical escalation
  labels are not asserted to be objective L2 need.
- The synthetic hidden need variable is generated from the specified
  prevalence model and is never observed by the dispatch policies.

## Analytical model and capacity check

For prevalence `pi`, sensitivity `pD` and false-positive rate `pFA`, the
expected positive recommendation fraction is

`q = pi*pD + (1-pi)*pFA`.

With L1 admission rate `lambda`, automatic acceptance gives the expected
recommendation flow `lambda_L2 = lambda*q`. For class-dependent prevalence,
the runner evaluates this by class and derives the recommendation-positive
class mixture. It then recalculates effective L2 capacity using the frozen
L2 roster, eligibility and analyst-by-class service map. Thus the reported
`rho_L2 = lambda_L2 / mu_L2` is mix-specific; `mu_L2` is not treated as a
universal constant. The calculation is a fractional-flow capacity LP and
describes offered load, not a demonstrated SLA threshold.

The frozen reference simulator gives an effective L1 capacity of **28.4186
alerts/h** for six L1 analysts. This implies `lambda_L1=24.1558/h` at
`rho_L1=0.85` and `35.5232/h` at `rho_L1=1.25`. For the base synthetic
recommendation mix, L2 capacity is **3.8350 investigations/h**, matching the
prior approximate 3.84/h value. At the old empirical operating point, the
composition-specific L2 capacity is 3.9232/h for the homogeneous historical
prevalence case; it varies slightly with the synthetic class-conditional
prevalence and operating point.

For `pD=0.7965`, the pFA values at which the fluid offered-load ratio reaches
selected boundaries are below. They are analytical load markers only.

| Need prevalence | `rho_L1` | pFA at `rho_L2=.5` | pFA at `.8` | pFA at `1.0` | pFA at `1.2` |
|---|---:|---:|---:|---:|---:|
| Historical-evaluation, 0.003355 | .85 | .07880 | .12769 | .16028 | .19287 |
| Historical-evaluation, 0.003355 | 1.25 | .05273 | .08597 | .10813 | .13030 |
| Original synthetic, 0.04332 | .85 | .04784 | .09883 | .13283 | .16683 |
| Original synthetic, 0.04332 | 1.25 | .02064 | .05532 | .07843 | .10155 |

Exact roots, class-mixture capacity and all classifier settings are in
[`analytic_l2_frontiers.csv`](../../results/soc_triage_organization_coupling/analytic_l2_frontiers.csv)
and [`analytic_workload.csv`](../../results/soc_triage_organization_coupling/analytic_workload.csv).
The model separates expected TP, FP and FN counts per hour and their nominal
L2 service work. TP work is necessary recommended work; FP work is unnecessary
executed work; FN work is necessary work omitted by the route. These are not
interchangeable with actual completed tasks or queue utilization.

## Pilot design

The fixed matrix crosses two prevalence scenarios, 11 classifier operating
points, two L1 load levels and 10 paired seeds. The 11 points are one exact
old empirical point plus a controlled sensitivity grid with `pD=.7965` or
`.90` and `pFA=.01,.05,.10,.15,.2859`. The grid is not asserted to be a
single feasible ROC curve. Each configuration is run under D1, P1 and HLS-B:
**44 conditions, 1,320 policy episodes, 440 trace/triage rows**.

The prevalence cases are (A) `344/102526` applied homogeneously across task
classes, explicitly as an old-evaluation scenario, and (B) the frozen
simulator's class-conditional synthetic prevalence
`.592*.03 + .236*.05 + .172*.08 = .04332`. Neither represents a measured
GMV-CERT need rate. The roster is 6 L1 / 3 L2, with frozen heterogeneous
eligibility, skill and analyst-class service, severity deadlines of 1/4/12 h,
24 h admission and 36 h drain. The admission arrival rate is held common
across policies within a condition.

Seeds `271200000–271200009` are new paired development seeds. For every
prevalence/load/seed, the same arrival times, class, priority, difficulty and
hidden need trace are reused across classifier points and policies. A
per-alert keyed uniform couples recommendation outcomes across classifier
points. Randomness is keyed independently of policy execution order. All
policies have the same admitted-alert denominator for a matched trace.

### Outcome definitions

The primary integrated measure is expected correct-and-on-time terminal
resolution per admitted alert. An alert whose hidden need requires L2 but is
given a negative recommendation receives zero primary credit even if its L1
service physically finishes on time. For correctly routed cases the score
uses the frozen modeled quality probability `competence*(1 - .35*difficulty)`.
This adds no large arbitrary penalty: false negatives are separately counted
and excluded from correct completion credit. Reported alongside it are the
historical routed-path `legacy_RN`, routed SLA, required-resolution SLA,
routing accuracy, confusion counts, L1/L2 service and queue measures.

Physical completion, deadline compliance and correct routing are distinct.
`required_resolution_SLA_terminal` counts timely completion only for alerts
that were routed consistently with the hidden need. L1 arrivals, L2 tasks
generated after L1 completion, L2 pool arrivals and L2 completions are
separately represented. In particular, an L2 recommendation does not become
an L2 pool arrival until its L1 task completes; completion rate is not arrival
rate.

## Engine audit and controls

The historical wrapper processes the L1 pool and then passes L1 completion
times as L2 arrivals. Because the pools have separate analysts and no
cross-pool resource feedback, the within-pool event clocks remain causal. An
independent interleaved event-loop comparison was added as a test: for D1, P1
and HLS-B, its assignments and completion times agree with the historical
two-stage wrapper under the pilot's separated-pool assumptions. No engine
change was necessary or made. The runner supplies WAPS with separate L1 and
mix-specific L2 capacity values; policies see only their causal task state,
not hidden need or future events. Drain is 36 hours and the validation checks
that deadlines mature by the terminal cutoff.

The targeted audit reports: one common trace hash per policy cell; identical
exogenous realizations across classifier operating points; equal denominators
across policies; no duplicate L1 or L2 assignments; no L2 task without a
positive recommendation; zero correct-and-on-time credit for false negatives;
and agreement between recomputed and wrapper legacy R/N. `policies_and_engine_source_unchanged`
is true for the published reference sources. Current local pre-existing edits
to unrelated SOC source files were preserved and are not included in this
branch's study artifacts.

The runner records actual confusion rates, which can depart materially from
their targets when prevalence is very low. For example, in the old prevalence
scenario and old operating point at `rho_L1=.85`, only 17 need-positive cases
occurred across the 10 traces; pooled realized `pD` is therefore noisy. The
run is a conditional sensitivity pilot, not a calibration test of classifier
performance.

## Results

### Old empirical point, by load and prevalence

Values below are means over 10 matched seeds. `Integrated` is the primary
correct-and-on-time expected score per admitted alert; `SLA*` is
required-resolution SLA. `Q2(H)` is L2 backlog at the 24 h admission cutoff;
`U2(H)` is mean analyst utilization over that period. `P1 mode` is the
fraction of WAPS dispatch epochs assigned P1.

| Prevalence | rhoL1 | Policy | Legacy R/N | Integrated | SLA* | Q2(H) | U2(H) | WAPS P1 mode L2 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Historical | .85 | D1 | .6178 | .5098 | .7618 | 82.7 | .9754 | — |
| Historical | .85 | P1 | .5949 | .4906 | .7666 | 87.9 | .9755 | — |
| Historical | .85 | HLS-B | .6183 | .5101 | .7658 | 87.3 | .9754 | .467 |
| Historical | 1.25 | D1 | .4301 | .3547 | .5119 | 90.4 | .9804 | — |
| Historical | 1.25 | P1 | .5437 | .4483 | .7036 | 97.9 | .9800 | — |
| Historical | 1.25 | HLS-B | .5501 | .4536 | .6940 | 97.5 | .9804 | .517 |
| Synthetic | .85 | D1 | .5988 | .4881 | .7294 | 94.0 | .9783 | — |
| Synthetic | .85 | P1 | .5734 | .4671 | .7299 | 99.5 | .9785 | — |
| Synthetic | .85 | HLS-B | .5975 | .4871 | .7314 | 99.0 | .9783 | .448 |
| Synthetic | 1.25 | D1 | .4171 | .3398 | .4904 | 103.9 | .9822 | — |
| Synthetic | 1.25 | P1 | .5278 | .4299 | .6750 | 110.7 | .9815 | — |
| Synthetic | 1.25 | HLS-B | .5342 | .4352 | .6662 | 110.4 | .9822 | .529 |

At `rho_L1=.85`, HLS-B's primary contrast with D1 is near zero (historical
prevalence: +.00029, paired 95% CI [-.00325,.00382]; synthetic: -.00102,
[-.00428,.00223]). It is above P1 in these cells (historical +.01941,
[.01539,.02342]; synthetic +.01994, [.01635,.02352]). At `rho_L1=1.25`,
HLS-B exceeds D1 (historical +.09890, [.08646,.11133]; synthetic +.09549,
[.08351,.10748]) and is only modestly above P1 (historical +.00530,
[.00096,.00965]; synthetic +.00535, [.00062,.01008]). It does not achieve
the highest `SLA*` in these overloaded old-point cells: P1 is higher by
about 0.010–0.009, while HLS-B's modeled quality/legacy R/N is higher. This
shows the quality–timeliness trade-off; it does not show that HLS-B is best on
every outcome.

The false-positive load mechanism is direct in the analytical accounting. At
the old point, historical prevalence gives approximately 6.882 FP
recommendations per hour at `rho_L1=.85` (versus .0646 TP/h); with synthetic
prevalence, about 6.606 FP/h versus .8335 TP/h. At `rho_L1=1.25`, rates rise
to 10.121 FP/h and .0949 TP/h (historical) and 9.715 FP/h and 1.226 TP/h
(synthetic). More prevalence increases necessary escalations, but the high
false-positive rate remains a major source of offered L2 work.

### Changes across classifier points and interaction

At `pFA=.01,pD=.7965,rho_L1=1.25`, L2 utilization at H is approximately .087
under historical prevalence and .330 under synthetic prevalence, and HLS-B
uses no P1 L2 dispatch epochs on average. At the old point the corresponding
utilization is about .980/.982 and P1 mode is .517/.529. With lower offered
L2 pressure HLS-B therefore stays in D1 at L2; under the old high-pFA point
it often switches to P1. These are evidence that WAPS responds to pressure
generated by routing, not evidence that switching itself caused the
cross-scenario performance changes.

A pre-specified difference-in-differences compares the old-like grid point
(`pD=.7965,pFA=.2859`) with a low-pFA/high-pD sensitivity point
(`pD=.90,pFA=.01`). At `rho_L1=1.25`, the change in HLS-B-minus-D1 integrated
performance is +.03798 (paired 95% CI [.03247,.04349]) under historical
prevalence and +.04020 ([.03442,.04597]) under synthetic prevalence. The
analogous HLS-B-minus-P1 changes are small and uncertain: -.00156
([-.00432,.00120]) and -.00157 ([-.00370,.00056]). At `rho_L1=.85`,
HLS-B-minus-D1 interaction intervals include zero in both prevalence cases.
These are interactions between two controlled synthetic operating points;
they are not a causal estimate along a real classifier ROC curve and do not
establish HLS-B superiority.

The two figures show the controlled sensitivity grid; the old exact empirical
point is retained in the CSV tables but omitted from the plotted curves
because it nearly coincides with the rounded `pD=.7965,pFA=.2859` endpoint.

Across all 44 condition means, HLS-B's primary score is numerically above D1
in 27 and P1 in 44; it is numerically above both in 27. This count is
descriptive only. In unadjusted paired t intervals for the 44 per-condition
contrasts, HLS-B–D1 excludes zero positively in 22, includes zero in 20, and
is negative-separated in 2; HLS-B–P1 is positive-separated in 32 and includes
zero in 12. No multiple-comparison correction was applied. The grid is
exploratory, and these counts must not be read as familywise-confirmed wins.

## Statistical analysis

The summary reports means and standard deviations over 10 seed values.
Differences are formed within matched seed and condition, then summarized
with two-sided 95% Student-t intervals (`df=9`). The four components
(prevalence, load, classifier point and seed) are not 440 independent
replicates: seeds are reused across classifier points, and the classifier
points share keyed exogenous traces within each prevalence/load/seed. The
interaction is paired at seed level. These are exploratory intervals; no
familywise correction was applied across the many operating points and
metrics. In particular, a positive mean or an unadjusted interval excluding
zero is not independent confirmation.

## Interpretation and limits

1. **Does L2 offered work follow the analytical model?** Yes by construction
   in expectation: the rate is `lambda*q`, and the class mix is used to
   recalculate L2 capacity. Finite traces yield stochastic confusion counts;
   actual L2 pool arrivals occur later, when L1 completes.
2. **When does L2 congestion appear?** At the old operating point it is already
   overloaded analytically at both L1 loads; the pilot shows L2 utilization
   near .98 and large cutoff backlog. At pFA=.01 it is lightly loaded under
   historical prevalence and moderately loaded under synthetic prevalence.
3. **pFA versus pD?** With rare need, pFA is influential because it acts on
   nearly all alerts; pD determines capture of scarce necessary escalations.
   A high pFA can produce a large volume of unnecessary work even while
   sensitivity is useful. Neither metric alone describes utility.
4. **Does L2 saturation change L1?** The pools have distinct staff and no
   feedback path in this model. The work demand created at L1 changes via
   routing only through whether a task is escalated; L2 congestion does not
   consume L1 capacity. A real SOC may have coordination, rework or shared
   resources absent here.
5. **Does the preferred organization change?** In these synthetic runs,
   D1 has a higher modeled-quality primary score at low `rho_L1` and HLS-B is
   near it; under high `rho_L1`, P1 and HLS-B exceed D1 substantially. HLS-B's
   edge over P1 is small in the old high-pFA cells. Other classifier points
   shift the relative gaps, most clearly against D1 in the overloaded load
   setting.
6. **Does WAPS respond?** Yes: its P1-mode fraction at L2 rises from zero at
   low pressure to roughly .45–.53 at the old point. This is a descriptive
   controller trace; causal attribution of outcomes to this mechanism would
   require an intervention not included here.
7. **How robust are conclusions?** The broad physical link between pFA,
   recommendation load and L2 offered work follows analytically. The
   organizational effects depend on assumed prevalence, service mixture,
   SLA, continuous-capacity model and policy dynamics. The low prevalence
   scenario has few positive cases per seed, making realized `pD` unstable.

The pilot supports a narrow scientific statement: under the model's automatic
acceptance assumption, classifier routing characteristics can materially
change offered L2 load, congestion and the relative modeled outcome of
organization policies, especially when L1 demand is already high. It does not
establish that a particular classifier's deployed recommendations would
produce these rates, that the hidden synthetic need matches operational
escalation need, or that HLS-B is generally preferable. Real acceptance,
objective need labels, the classifier's individual independent-test
predictions, composition-specific operational service times, staffing
schedules, shared-resource effects and calibrated deadline semantics remain
unknown. No real SOCTRA alert records or identifiers are included.

### Recommendation on this line

Continue only as a bounded synthetic coupling result for the article or as a
basis for later data-informed validation; do not claim operational impact or
classifier–organization benefit from this pilot alone. The evidence is enough
to show that coupling is technically consequential in the model, but not
enough to decide a deployment policy or generalize the numerical effect to
GMV-CERT.

## Reproducibility files

- [Configuration](config/pilot.json)
- [Runner](run_pilot.py)
- [Summary/plots script](summarize_pilot.py)
- [Targeted tests](../../tests/test_soc_triage_organization_coupling.py)
- [`episodes.csv`](../../results/soc_triage_organization_coupling/episodes.csv)
- [`triage_by_seed.csv`](../../results/soc_triage_organization_coupling/triage_by_seed.csv)
- [`triage_summary.csv`](../../results/soc_triage_organization_coupling/triage_summary.csv)
- [`summary_by_config_policy.csv`](../../results/soc_triage_organization_coupling/summary_by_config_policy.csv)
- [`paired_contrasts.csv`](../../results/soc_triage_organization_coupling/paired_contrasts.csv)
- [`interaction_contrasts.csv`](../../results/soc_triage_organization_coupling/interaction_contrasts.csv)
- [`analytic_workload.csv`](../../results/soc_triage_organization_coupling/analytic_workload.csv)
- [`analytic_l2_frontiers.csv`](../../results/soc_triage_organization_coupling/analytic_l2_frontiers.csv)
- [`waps_switches.csv`](../../results/soc_triage_organization_coupling/waps_switches.csv)
- [`validation_checks.json`](../../results/soc_triage_organization_coupling/validation_checks.json)
- [`metadata.json`](../../results/soc_triage_organization_coupling/metadata.json)
- [Analytical offered L2 load figure](figures/l2_offered_load.png)
- [Paired organizational effect figure](figures/organizational_effect_by_classifier.png)

Run `python studies/soc_triage_organization_coupling/run_pilot.py`, then
`python studies/soc_triage_organization_coupling/summarize_pilot.py` to
recreate the synthetic tables and figures; run
`python -m pytest tests/test_soc_triage_organization_coupling.py -q` for the
targeted coupling tests. The targeted suite and the original allocation and
L1/L2 simulation suites pass (67 tests total).
