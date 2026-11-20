# SOCTRA classifier operating points and SOC operational impact — Phase 2

> **Source-correction notice (2026-11-20):** the complete SOCTRA journal PDF supersedes the source inventory and Pareto interpretation in this report. All 25 operating-point rate pairs used here crosswalk exactly to symmetric-cost points in the article’s Table 5; the prior simulations remain unchanged and apply only to those matched synthetic rate pairs. The distinct asymmetric-cost Table 7 points were not simulated in this phase. See [the source correction and 72-point audit](SOCTRA_CLASSIFIER_SOURCE_CORRECTION.md) for the complete inventory, corrected frontiers, analytic load projections, and impact assessment. No prior numerical result file was modified.

## Executive summary

This independent, exploratory study evaluates whether published escalation-classifier operating points can yield different operational outcomes once recommendations induce L2 work. The classifier scores are empirical aggregate values, but the recommendations used here are synthetic Bernoulli draws; there are no alert-level SOCTRA predictions in this study. The need-for-L2 variable, automatic acceptance, project-independent error rates, service times, and continuous analyst availability are modeling assumptions. Results therefore describe a controlled simulator, not GMV-CERT performance.

The analysis covers all 25 published operating points for statistical Pareto and fluid offered-load calculations, and a predeclared subset of nine points for the organizational simulation. The phase-2 campaign uses 40 new paired seeds, two L1 loads, three L2 team sizes, and D1/P1/WAPS. This produces 1,040 paired synthetic classifier traces and 9,360 policy episodes. Full results and hashes are linked below.

## 1. Pilot audit and frozen boundary

The previous coupling pilot is preserved at [`SOC_TRIAGE_ORGANIZATION_COUPLING_PILOT.md`](../soc_triage_organization_coupling/SOC_TRIAGE_ORGANIZATION_COUPLING_PILOT.md), with its frozen configuration at [`pilot.json`](../soc_triage_organization_coupling/config/pilot.json). This study does not overwrite or reinterpret its results.

The pilot's primary metric, `correct_on_time_expected_per_admitted`, gives no correct-resolution credit to a synthetic alert whose hidden need requires L2 when the recommendation is negative, even if L1 physically finishes. The score uses the frozen expected quality `competence × (1 − 0.35 × difficulty)` for correctly routed on-time resolutions. This avoids an arbitrary large FN penalty; false negatives, omitted nominal L2 work, and necessary-resolution SLA are also reported separately. False-positive recommendations create L2 work and are measured as unnecessary work; they are not directly subtracted from a scalar score. Thus operational damage from FPs appears through service demand, backlog, and late or incomplete work, not an imposed penalty.

The pilot separates offered recommendations, L1-completion-triggered L2 arrivals, L2 assignments/completions, utilization, and backlog. Its interaction contrasts compare paired synthetic points and do not represent movement along a real ROC curve. No pilot finding establishes that a particular SOCTRA model's individual recommendations would cause the observed queues. The two pools have separate staff and no cross-pool resource feedback; WAPS receives causal queue/load state only. The pilot already tested its two-stage L1-then-L2 event clock against an interleaved implementation for D1/P1/HLS-B under these assumptions, and required no engine changes.

Potential artefacts retained as explicit limits are: exchangeable classifier errors across synthetic task classes; synthetic, hidden escalation need; automatic acceptance; no rework or shared-resource coupling; modeled class/analyst service times; and finite drain. Published aggregate pD/pFA cannot reveal whether errors concentrate in unusually costly classes. This phase adds no task-stratified claims.

## 2. Source data, labels, and operating points

All published operating points are transcribed in [`all_published_operating_points.csv`](../../results/soc_triage_classifier_operating_impact/all_published_operating_points.csv), including algorithm, features, label definition, pD, pFA, published/recomputed balanced accuracy, derived normalized Bayes benefit, and table provenance. The source is Lazaro et al., *AI-Driven Alert Triage in Security Operations Centers: Imbalanced Learning with Human-in-the-Loop Contextual Bias Modeling*, AIAI 2026, Tables 3, 5, and 7 ([publisher DOI](https://doi.org/10.1007/978-3-032-30805-4_11)). Table 3 supplies ten original-label points; Tables 5 and 7 supply fifteen standardized-label points. Table 4's contextual-window balanced accuracies do not provide a distinct pD/pFA operating point and are not treated as one.

The published operating-point tables do not give separate classifier configurations for symmetric and asymmetric escalation costs. The CSV therefore records the reported point once and derives normalized benefits for equal costs and `c_M=3 c_FA` from pD/pFA. For the latter, the derived benefit is `1 − [0.25 pFA + 0.75(1−pD)]`. These are cost-sensitivity calculations, not additional trained or measured classifiers. Points from different algorithms/configurations are not assumed to form a common ROC curve.

The two label definitions are analyzed separately. For original labels, the phase-2 primary prevalence is the audited exact chronological-test count, 39/14,449. The published Table 2 rounded imbalance ratio (360.23) implies 40/14,449; this one-alert conflict is disclosed rather than silently resolved in favor of a rounded inference. A second original-label sensitivity uses the full historical population count 210/63,410. For standardized labels, the primary test prevalence is 19/14,449, inferred from the published rounded ratio 759.47 and test size; it is not replaced with original-label prevalence. These label frequencies remain proxies and are not claims about objective L2 need.

Statistical Pareto dominance is computed separately within each label definition: maximize pD and minimize pFA; one point dominates another if it is no worse in both and strictly better in at least one. The computed frontiers are:

| Label definition | Non-dominated published points |
|---|---|
| Original | LR A+C; RF A+C; Bayesian MLP A+C |
| Standardized | LR A+C; Bayesian MLP A+C; LightGBM A+C; LightGBM C |

The complete pointwise classification, including dominated points, is in [`statistical_pareto.csv`](../../results/soc_triage_classifier_operating_impact/statistical_pareto.csv). No claim is made that statistical Pareto dominance alone guarantees operational dominance: the missing class-stratified errors could change induced work composition.

## 3. Analytic load model and scenario selection

For need prevalence `pi`, sensitivity `pD`, and false-positive rate `pFA`, expected recommendation fraction is

`q = pi pD + (1 − pi) pFA`.

Per 1,000 alerts the expected TP/FP/FN/TN counts are respectively `1000 pi pD`, `1000 (1−pi) pFA`, `1000 pi(1−pD)`, and `1000(1−pi)(1−pFA)`. Under automatic acceptance, `lambda_L2 = lambda_L1 q`. Necessary recommended work, unnecessary FP work, and omitted FN work are separately estimated using task-class service means. L2 effective capacity is recomputed by fractional-flow allocation under the induced positive-recommendation class mixture and frozen eligibility/service maps; the capacity is not treated as universal. Full point-by-point values are in [`analytic_load_by_point.csv`](../../results/soc_triage_classifier_operating_impact/analytic_load_by_point.csv), with offered-load boundaries `rho_L2=0.5, 0.8, 1.0, 1.2` in [`analytic_l2_frontiers.csv`](../../results/soc_triage_classifier_operating_impact/analytic_l2_frontiers.csv).

The reference roster's calculated L1 capacity is 28.4186 alerts/h; the tested rates are 24.1558/h (`rho_L1=.85`) and 35.5232/h (`rho_L1=1.25`). L2 configurations contain 2, 3, or 4 analysts, with demand held absolutely constant while L2 staffing changes. The frozen roster builder reuses/cycles declared profiles for a four-person team; this means the 4-L2 comparison changes composition as well as headcount and is not a pure homogeneous capacity multiplier.

Selection preceded simulation outcomes. We simulated every statistical-frontier point and one dominated, detection-comparable/high-FP control in each label group: Bayesian MLP A for original labels and RF A+C for standardized labels. This yields four original and five standardized classifier points. The other sixteen published points remain in the complete statistical/analytic tables and are excluded from organizational simulation to keep the matrix compact. The control points test the interpretation of aggregate dominance; no point was selected because of an observed WAPS result.

## 4. Simulation protocol and statistical method

The fixed configuration is [`phase2.json`](config/phase2.json); point definitions are [`classifier_points.json`](config/classifier_points.json). Each selected point is crossed with its valid prevalence scenario, `rho_L1=.85/1.25`, L2 staffing `2/3/4`, 40 seeds `272600000–272600039`, and D1/P1/HLS-B. The pilot seed range `271200000–271200009` is not reused. Admission is 24 h with a 36 h drain; terminal deadlines are 1/4/12 h. HLS-B/WAPS remains at 4 h and thresholds 1.05/1.20. Recommendations are automatically accepted as an experimental assumption. No REPORTADO classifier is simulated.

For every prevalence/load/seed, arrival, class, severity, difficulty, and hidden need are shared across classifier points. A keyed per-alert uniform generates recommendations so thresholds use common random numbers; a policy does not consume a shared sequential RNG stream. Every organizational policy and L2 capacity in a matched cell receives the same trace, confusion outcomes, and denominator. WAPS never receives hidden need or future information. L1 and L2 have distinct capacities and queues.

Each trace admitted 498–917 alerts; the number of hidden need-positive alerts ranged from 0 to 7 per seed. Consequently, empirical pD is noisy at the seed level. `triage_confusion_pooled.csv` reports pooled counts and rates, while the operating-point target pD/pFA remain the classifier inputs. Across 40 seeds at high load/reference L2 staffing, for example, the original RF A+C pooled 64 TP/23 FN and Bayesian MLP A+C pooled 72 TP/15 FN; standardized LightGBM A+C pooled 32 TP/3 FN and LightGBM C pooled 33 TP/2 FN. Pooled values are stochastic realizations and should not replace the published target rates.

The primary comparison is expected correct-and-on-time resolution per admitted alert; secondary outcomes include legacy R/N, required-resolution SLA, routed SLA, physical completion, confusion counts, nominal FP/TP/FN work, service consumed, L1/L2 backlog and utilization, and WAPS P1-mode and switch traces. `rho_L2` is offered load; utilization, generated arrivals and backlog are separately measured.

Paired policy and classifier differences use per-seed contrasts and two-sided Student-t 95% intervals with df=39. For classifier-by-organization interactions, the unit is the seed-level difference-in-differences. Empirical pD/pFA are pooled over confusion counts; uncertainty for detection is estimated with a deterministic SHA-256-keyed percentile bootstrap that resamples 40 seed clusters and recomputes pooled TP/need (1,000 replicates). Intervals are exploratory and unadjusted across the many classifiers, outcomes, capacities, loads, and interactions; operational Pareto labels are descriptive comparisons of means, not inferential dominance. Seed identifiers are reused across conditions, so the analysis does not pool condition×seed rows as independent replicates. Uncertainty in actual operating conditions/prevalence is not estimated.

## 5. Results

### Analytic load and congestion

The analytic and simulated outcomes show that at these rare prevalences recommendation volume is driven mainly by `pFA`, because almost all arrivals are negatives. At `rho_L1=1.25` with three L2 analysts, standardized LightGBM A+C yields an expected `q=.0460`, 1.636 L2 recommendations/h, and offered `rho_L2=.417`; standardized LightGBM C-only yields `q=.4057`, 14.413 recommendations/h, and `rho_L2=3.674`. Expected FP counts are 44.94 versus 404.57 per 1,000 alerts, while TP counts change only from 1.107 to 1.177 per 1,000 under the low standardized prevalence. This is a synthetic composition-level projection, not evidence about errors on specific real alerts. C-only crosses fluid saturation under both L1 loads; A+C remains below offered-load saturation in expectation. The same pattern is visible in [`analytic_load_by_false_alarm.png`](../../results/soc_triage_classifier_operating_impact/analytic_load_by_false_alarm.png).

L1 is below its calculated capacity at `rho=.85` and above it at `rho=1.25`. L2 can nevertheless be the binding pool at nominal L1 load when false-positive routing is high. Fluid `rho_L2=1` is only a workload marker: it is not a measured SLA threshold. Actual overload response is evaluated in the finite event simulation.

### Policy outcomes and interactions

The per-condition policy means and intervals are in [`summary_by_condition.csv`](../../results/soc_triage_classifier_operating_impact/summary_by_condition.csv); paired WAPS−D1 and WAPS−P1 contrasts are in [`paired_policy_contrasts.csv`](../../results/soc_triage_classifier_operating_impact/paired_policy_contrasts.csv). The phase-2 operational outcomes demonstrate that classifier configuration matters under the assumed routing/need/service model: changing `pFA` changes recommendation volume, L2 work, backlog and timely correct completion. At high L1 load, the high-FP standardized C-only point has sharply poorer timely-correct performance than low-FP A+C points because L2 receives much more work. That is a conditional simulation result, not an empirical impact estimate for those trained models. Paired classifier contrasts against matched seed traces are in [`paired_classifier_contrasts.csv`](../../results/soc_triage_classifier_operating_impact/paired_classifier_contrasts.csv).

Illustrative means for the reference three-person L2 roster under `rho_L1=1.25` are below. The integrated outcome is expected correct/on-time resolutions per admitted alert; SLA and legacy R/N are separate metrics. The table is descriptive and does not constitute a multiple-comparison-adjusted ranking.

| Label group / classifier | Policy | Correct & on-time | Required SLA | Legacy R/N | L2 backlog at H | L2 utilization at H | WAPS P1-mode fraction |
|---|---|---:|---:|---:|---:|---:|---:|
| Original RF A+C | D1 | .4967 | .7219 | .6013 | 17.10 | .9539 | — |
| Original RF A+C | P1 | .5623 | .8792 | .6811 | 21.35 | .9577 | — |
| Original RF A+C | WAPS | .5778 | .8763 | .6997 | 19.18 | .9555 | .359 |
| Original Bayesian MLP A+C | D1 | .4598 | .6681 | .5565 | 41.78 | .9729 | — |
| Original Bayesian MLP A+C | P1 | .5230 | .8179 | .6331 | 48.05 | .9725 | — |
| Original Bayesian MLP A+C | WAPS | .5343 | .8114 | .6468 | 46.65 | .9729 | .526 |
| Standardized LightGBM A+C | D1 | .5405 | .7874 | .6542 | 1.30 | .3288 | — |
| Standardized LightGBM A+C | P1 | .6209 | .9712 | .7516 | 1.15 | .3317 | — |
| Standardized LightGBM A+C | WAPS | .6328 | .9618 | .7659 | 1.13 | .3339 | .000 |
| Standardized LightGBM C | D1 | .3315 | .4825 | .4014 | 166.20 | .9835 | — |
| Standardized LightGBM C | P1 | .3770 | .5903 | .4564 | 174.45 | .9834 | — |
| Standardized LightGBM C | WAPS | .3851 | .5856 | .4663 | 174.40 | .9835 | .523 |

For original-label RF A+C, WAPS minus D1 is `+.0811` (paired 95% CI `[+.0677,+.0945]`) and WAPS minus P1 is `+.0154` (`[+.0108,+.0200]`). For original Bayesian MLP A+C the contrasts are `+.0746` (`[+.0621,+.0871]`) and `+.0114` (`[+.0075,+.0153]`). For standardized LightGBM A+C they are `+.0923` (`[+.0771,+.1074]`) and `+.0119` (`[+.0071,+.0168]`); for LightGBM C they are `+.0537` (`[+.0445,+.0629]`) and `+.0082` (`[+.0050,+.0113]`). These selected examples illustrate that WAPS may balance quality and timeliness, but they were not selected as confirmatory cases.

Across the 78 simulated classifier/prevalence/load/L2-size cells, WAPS's primary mean exceeded D1 in 50 and was lower in 19; 45 unadjusted paired intervals were positive-separated, 10 negative-separated, and 23 included zero. WAPS's mean exceeded P1 in all 78, with all 78 unadjusted intervals positive-separated. These broad exploratory counts are exposed to multiplicity and should not be read as confirmatory familywise evidence. There are 132 paired difference-in-differences per fixed-policy contrast across classifier pairs and operating strata: 65 WAPS-vs-D1 and 87 WAPS-vs-P1 intervals exclude zero, with signs in both directions. Interaction magnitude ranges from `−.0394` to `+.0440` for WAPS-vs-D1 and `−.0073` to `+.0078` for WAPS-vs-P1. Thus classifier-by-organization interaction is conditional rather than a single consistent shift.

The data show a concrete change in classifier ordering by the operational metric. Under original labels at `rho_L1=1.25`, three L2 analysts and WAPS, RF A+C (published BA=.7941) exceeds Bayesian MLP A+C (BA=.8222) by `+.04344` correct/on-time per admitted alert (paired CI `[+.03917,+.04771]`). For standardized labels in the same load/roster, Bayesian MLP A+C (BA=.8444) exceeds the higher-BA LightGBM A+C point (BA=.8986) by only `+.00244` (`[+.00187,+.00301]`) on the primary outcome. These are selected exploratory strata, not global rankings. The former illustrates that lower false-positive load can outweigh a detection/BA advantage under L2 congestion; the latter difference is small in absolute terms and its direction is sensitive to modeling assumptions.

Holding the absolute arrival rate fixed, increasing the L2 roster from two to four analysts under high load raises WAPS correct/on-time output from `.5468` to `.6169` for original RF A+C, while the L2 backlog at H falls from 46.98 to 5.55. For standardized LightGBM C-only, the same roster change raises the outcome from `.3809` to `.3949`, but leaves an H backlog of 145.25. The four-analyst roster cycles existing analyst profiles, so these contrasts combine headcount and composition changes; they do not support a staffing-cost recommendation.

The paired difference-in-differences file [`classifier_organization_interactions.csv`](../../results/soc_triage_classifier_operating_impact/classifier_organization_interactions.csv) shows where the WAPS-vs-fixed gap changes across classifier points. Interactions vary with load and L2 size; they must not be summarized as universal WAPS superiority. WAPS's own fraction of P1 dispatch epochs and transitions is available in `summary_by_condition.csv` and [`waps_switches.csv`](../../results/soc_triage_classifier_operating_impact/waps_switches.csv). The figure [`paired_policy_effects.png`](../../results/soc_triage_classifier_operating_impact/paired_policy_effects.png) plots paired WAPS contrasts; [`operational_outcome_vs_false_alarm.png`](../../results/soc_triage_classifier_operating_impact/operational_outcome_vs_false_alarm.png) displays primary outcome by pFA for the reference roster under elevated load; and [`operational_tradeoff_reference_roster.png`](../../results/soc_triage_classifier_operating_impact/operational_tradeoff_reference_roster.png) plots unnecessary FP work against correct/on-time output without imposing a weighted scalar winner.

Operational non-dominance is reported as a six-objective descriptive mean comparison (detection, correct/on-time, required SLA, FP work, FN omitted work, L2 backlog) by label definition, prevalence, load, L2 size, and organization in [`operational_pareto_descriptive.csv`](../../results/soc_triage_classifier_operating_impact/operational_pareto_descriptive.csv). It deliberately does not collapse trade-offs into an arbitrary utility score. A mean-vector non-dominated point is not evidence of statistically separated superiority.

### Interpretation against the hypotheses

1. **Does BA alone select the best operational point?** No general equivalence is established. BA weights sensitivity and specificity equally, while rare prevalence makes false-positive volume physically important to L2 load. The simulation can therefore rank trade-offs differently from BA. No single operational winner is justified without an explicit operational constraint/utility.
2. **Can higher detection increase congestion?** Yes, when it comes with higher pFA: positive recommendations and necessary TP work rise, but so does FP work. The extent depends on prevalence and L2 capacity. This does not mean higher detection is inherently harmful.
3. **Does L2 capacity shift the comparison?** The 2/3/4-person analyses are conditional on the frozen roster builder and show different offered loads, backlogs and timeliness; demand remains fixed. Four L2 analysts also alter the composition of repeated profiles, so interpret the change as a roster configuration, not a cost-free capacity scalar.
4. **Does organization modify classifier effects?** Paired interaction contrasts are nonzero in some selected cells, but not uniformly. The output supports conditional classifier×organization interaction in this simulator, not a broad causal claim about real SOCs.
5. **Can WAPS compensate for high-FP routing?** No universal compensation is shown. WAPS changes dispatch mode in response to queue pressure, but it cannot create L2 capacity or remove unnecessary jobs. Its relative effect depends on L1 load, L2 team and classifier point.

Balanced accuracy and normalized Bayes benefit remain useful statistical summaries, but they do not include prevalence-weighted induced work, backlog, service times, deadlines, or staffing. They are insufficient as stand-alone operational selection criteria in this model. Conversely, these simulations do not validate a replacement metric or a real-world classifier ranking.

## 6. Validation and reproducibility

[`validation_checks.json`](../../results/soc_triage_classifier_operating_impact/validation_checks.json) records counts and checks for all 25 points, episode totals, paired traces, denominators, confusion counts, false-negative gating, published-BA reconstruction, and deadline maturity. [`triage_by_seed.csv`](../../results/soc_triage_classifier_operating_impact/triage_by_seed.csv) preserves generated TP/FP/FN/TN and empirical rates; [`triage_confusion_pooled.csv`](../../results/soc_triage_classifier_operating_impact/triage_confusion_pooled.csv) gives pooled realized rates with rare-positive denominators; [`episodes.csv`](../../results/soc_triage_classifier_operating_impact/episodes.csv) preserves policy outcomes; [`metadata.json`](../../results/soc_triage_classifier_operating_impact/metadata.json) records the config and seeds; [`reproducibility_manifest.json`](../../results/soc_triage_classifier_operating_impact/reproducibility_manifest.json) records SHA-256 checksums and runtime/worktree provenance.

The phase-2-specific unit tests verify the published point count, BA reconstruction, Pareto rule and frontier. The frozen pilot's targeted tests cover false-negative gating, L2 starts after L1 completion, and two-stage/interleaved event-clock equivalence. The output audit verifies admitted counts equal trace counts, TP+FP+FN+TN equals the denominator, TP+FN equals synthetic need, L2 assignment count does not exceed L1 assignments, and all deadlines mature before H+D. The runner verifies paired trace hashes, denominators, confusion outcomes, and false-negative gating. No policies, engine, or historical result files were changed for this phase. Pre-existing local edits in `src/hls/rq1_allocation.py` and `src/hls/rq1_l1_l2.py` are outside the phase and are not included in the study commit; the manifest records their content hashes for audit.

## 7. Limitations and scientific conclusion

The experiments establish a **model-based mechanism**: aggregate `pD/pFA` points, when interpreted as synthetic exchangeable recommendation probabilities under automatic acceptance, can materially change offered L2 work and can alter correct/on-time service and the relative D1/P1/WAPS outcomes. The strong physical effect of pFA under rare prevalence follows directly from the mixture equation. The operational rankings are conditional on synthetic need prevalence, class-independent error allocation, analyst service/eligibility, continuous staffing, deadlines, acceptance, and independent L1/L2 pools. Because no individual test predictions are available, the experiment does not replay SOCTRA classifier decisions, estimate GMV impact, or establish empirical classifier×policy interactions.

The evidence supports a bounded exploratory contribution: classifier selection for a SOC should consider workload, capacity, and service outcomes in addition to statistical discrimination metrics. It does **not** support declaring one classifier or WAPS universally best, nor making a deployment recommendation for GMV-CERT. The results are not confirmatory and are not corrected for the extensive exploratory comparisons. Reported Pareto fronts and confidence intervals should be read with that limitation.

## Reproduction files

- [Configuration](config/phase2.json) and [all published points](config/classifier_points.json)
- [Runner](run_phase2.py), [summary and figures](summarize_phase2.py), [tests](test_phase2.py), [manifest writer](write_manifest.py)
- Synthetic outputs: [episode CSV](../../results/soc_triage_classifier_operating_impact/episodes.csv), [triage by seed](../../results/soc_triage_classifier_operating_impact/triage_by_seed.csv), [summaries and contrasts](../../results/soc_triage_classifier_operating_impact/)

Recreate with `python -m unittest studies.soc_triage_classifier_operating_impact.test_phase2 -v`, `python studies/soc_triage_classifier_operating_impact/run_phase2.py`, `python studies/soc_triage_classifier_operating_impact/summarize_phase2.py`, then `python studies/soc_triage_classifier_operating_impact/write_manifest.py`.
