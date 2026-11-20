# Joint SOCTRA escalation Pareto frontier and minimal campaign selection

## Decision scope

This note selects classifier operating points for a possible next simulation campaign. It uses the audited 72-point inventory and the frozen Phase 2 episodes only. **No simulations were run.** D1, P1, WAPS/HLS-B, the event engine, and the previous results remain unchanged.

The frontier is computed jointly across the symmetric Table 5 and asymmetric Table 7 points, separately for original and standardized label definitions. A point is dominated only if another point in the same label group has at least as high pD and at most as high pFA, with one strict inequality. Cost regime is retained as point metadata; it is not used as a third objective. The frontier therefore exposes the aggregate detection–false-alarm trade-off across operating configurations, not the classifier's Bayes-benefit preference and not a common ROC curve.

## Joint frontier and expected L2 load

The load columns use the article Table 1 test prevalence for the proposed harmonized campaign: original labels `pi=40/14449=0.002768357671811198` (implied by the published test IR) and standardized labels `pi=19/14449=0.001314969894110319`. The previous phase used a different stored original-label probability, despite describing it as 39/14,449; that discrepancy is documented in the source correction. All displayed L2 rates below assume the reference 6-L1/3-L2 roster and class-independent pD/pFA across synthetic task classes. They are expected offered recommendation rates, not actual L2 completions or utilization.

| Label definition | Configuration | Cost regime | pD | pFA | BA | Normalized Bayes benefit | pi for proposed campaign | Recommendations / 1,000 | L2 offers/h at rhoL1=.85 → 1.25 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Original | LSEnsemble A+C | Symmetric | .7500 | .1510 | .7995 | .7995 | .0027683577 | 152.66 | 3.688 → 5.423 |
| Original | LR A+C | Symmetric | .8000 | .2050 | .7975 | .7975 | .0027683577 | 206.65 | 4.992 → 7.341 |
| Original | Bayesian MLP A+C | Symmetric | .8500 | .2056 | .8222 | .8222 | .0027683577 | 207.38 | 5.010 → 7.367 |
| Original | Bayesian MLP A+C | Asymmetric, c̄M=3c̄FA | .9250 | .3632 | .7809 | .8530 | .0027683577 | 364.76 | 8.811 → 12.957 |
| Original | RF A+C | Asymmetric, c̄M=3c̄FA | .9500 | .5279 | .7111 | .8305 | .0027683577 | 529.07 | 12.780 → 18.794 |
| Original | LightGBM C | Asymmetric, c̄M=3c̄FA | .9750 | .6025 | .6862 | .8306 | .0027683577 | 603.53 | 14.579 → 21.439 |
| Original | Bayesian MLP C | Asymmetric, c̄M=3c̄FA | 1.0000 | .7692 | .6154 | .8077 | .0027683577 | 769.84 | 18.596 → 27.347 |
| Standardized | LR A+C | Symmetric | .6842 | .0081 | .8381 | .8381 | .0013149699 | 8.99 | .217 → .319 |
| Standardized | Bayesian MLP A+C | Symmetric | .7042 | .0154 | .8444 | .8444 | .0013149699 | 16.31 | .394 → .579 |
| Standardized | LightGBM A+C | Symmetric | .8421 | .0450 | .8986 | .8986 | .0013149699 | 46.05 | 1.112 → 1.636 |
| Standardized | RF A+C | Asymmetric, c̄M=3c̄FA | .9474 | .1938 | .8768 | .9121 | .0013149699 | 194.79 | 4.705 → 6.920 |
| Standardized | LSEnsemble A | Asymmetric, c̄M=3c̄FA | .9649 | .2695 | .8477 | .9063 | .0013149699 | 270.41 | 6.532 → 9.606 |
| Standardized | LightGBM A+C | Asymmetric, c̄M=3c̄FA | 1.0000 | .3351 | .8324 | .9162 | .0013149699 | 335.97 | 8.116 → 11.935 |

The data-backed source for all 13 rows, including Table 5/7 and PDF page, the PDF-implied prevalence alternative, offered `rho_L2`, and load fields, is [`joint_pareto_frontier_13.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/joint_pareto_frontier_13.csv). Rates for all 72 operating points are in [`analytic_load_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/analytic_load_72.csv).

## Comparison with the nine Phase 2 simulated points

Five of the nine previously simulated points lie on the joint frontier: original LR A+C and Bayesian MLP A+C (symmetric), and standardized LR A+C, Bayesian MLP A+C, and LightGBM A+C (symmetric). The other four are retained as useful dominated controls:

- Original RF A+C, symmetric: source-correction control; the expanded Table 5 frontier replaces it with lower-pFA LSEnsemble A+C at the same pD.
- Original Bayesian MLP A, symmetric: single-feature, detection-comparable control.
- Standardized RF A+C, symmetric: same pD as standardized LightGBM A+C but higher pFA, a useful load control.
- Standardized LightGBM C, symmetric: high-pFA, high-detection stress point, now dominated in the joint frontier by asymmetric LightGBM A+C.

The eight joint-frontier points absent from the previous simulations and selected for new episodes are:

1. Original, symmetric: LSEnsemble A+C.
2. Original, asymmetric: Bayesian MLP A+C; RF A+C; LightGBM C; Bayesian MLP C.
3. Standardized, asymmetric: RF A+C; LSEnsemble A; LightGBM A+C.

For a campaign aligned with the article Table 1, use the PDF-implied pi=40/14,449 for original labels and regenerate the original-label traces under that value. Four old original-label points (two frontier points and two controls) must therefore be rerun; their old episodes remain preserved as a separate legacy-prevalence analysis. The standardized-label Phase 2 probability already equals the Table 1 implied 19/14,449, so its five previous points can be reused after checking trace hashes and all other configuration fields. The article-implied original count is inferred from a rounded imbalance ratio and must be labeled accordingly.

## Minimal campaign proposal

For a single harmonized primary comparison at the article-implied test prevalence, simulate the eight missing frontier points, rerun the four original-label prior points (two frontier points plus two useful dominated controls) at pi=40/14,449, and reuse the five standardized-label prior points at pi=19/14,449 after verifying exact exogenous trace hashes and configuration. The resulting unique point set is the 13-point joint frontier plus four prior dominated controls. Use seed IDs `272600000–272600039`, the same two L1 loads (`rho_L1=.85, 1.25`), the existing 2/3/4 L2 rosters with absolute demand unchanged, and D1/P1/WAPS. Use keyed common random numbers so arrivals, task classes, severity, difficulty, hidden need, and per-alert recommendation uniforms are identical across classifier points and policies within each prevalence/load/roster/seed condition.

Each point contributes `2 demands × 3 L2 roster sizes × 3 policies × 40 seeds = 720` policy episodes. Twelve operating points are simulated or rerun for the harmonized primary cohort, requiring **8,640 policy episodes**. Five standardized points are reused (3 frontier points plus 2 controls), contributing 3,600 existing eligible episodes after validation. The resulting primary joined comparison covers 17 points (13 joint-frontier points plus four controls), or 12,240 point-policy episodes. The previous original-label episodes remain intact but are not merged into this primary cohort because their stored pi differs.

This is an exploratory harmonized extension, not an independent confirmation: the 40 seed identifiers have already been used in Phase 2. Keep the prior 210/63,410 original-label prevalence sensitivity separate; do not imply it was crossed with the asymmetric points. Preserve the legacy original-label episode results as a separate analysis and never describe their stored pi as exactly 39/14,449.

### Outcomes to compare

For each classifier point × L1 demand × L2 roster, compare D1, P1, and WAPS using paired seed contrasts on the existing primary outcome and the disaggregated metrics already collected: correct-and-on-time resolution, necessary-resolution SLA, routed SLA, FP work, FN omitted work, L2 backlog, utilization, and WAPS mode/switch summaries. Report pD/pFA targets alongside realized confusion totals. Do not create a weighted scalar classifier score or describe this aggregate-rate simulation as replaying the trained models on individual SOCTRA alerts.

## What this selection can answer—and limits

The frontier deliberately covers a broad range of expected L2 load. At the PDF-implied original-label prevalence and a three-analyst L2 pool, the original-label frontier spans about 5.4–27.3 L2 recommendations/hour at elevated L1 demand, while the standardized frontier spans about 0.32–11.9/hour. The L2 team-size factor remains an additional controlled condition. These calculations motivate the capacity and demand contrasts; they do not predict deadlines or queueing outcomes by themselves.

The planned extension can show whether the simulated operating preference changes across the joint pD/pFA frontier as load and L2 staffing vary, and whether WAPS shifts those conditional outcomes. It cannot identify a universally best classifier, prove a real-world operating point, or establish actual human acceptance. The error distribution remains exchangeable across synthetic classes, and the original-label prevalence inconsistency is unresolved. Since points from the two cost regimes are separate published model operating configurations, the frontier is a descriptive cross-configuration trade-off, not a single trained model’s ROC curve.

## Reproducibility

Rebuild the frontier/selection table without simulation with:

```sh
python studies/soc_triage_classifier_operating_impact/select_joint_frontier.py
```

The selected point IDs and their campaign status are in [`joint_pareto_frontier_13.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/joint_pareto_frontier_13.csv). The complete source inventory and its audit are in [`SOCTRA_CLASSIFIER_SOURCE_CORRECTION.md`](SOCTRA_CLASSIFIER_SOURCE_CORRECTION.md).
