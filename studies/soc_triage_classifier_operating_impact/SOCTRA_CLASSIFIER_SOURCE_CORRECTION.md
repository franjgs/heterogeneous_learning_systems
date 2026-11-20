# SOCTRA classifier inventory: correction from the complete article PDF

## Scope and status

This is a source correction and analytical re-audit of the classifier input to Phase 2. It uses the complete local article PDF supplied by the investigator as the primary source. It does **not** run simulations, infer individual classifier predictions, modify the earlier Phase 2 outputs, or change D1, P1, WAPS/HLS-B, or the simulator. The original Phase 2 report and its outputs remain preserved as published; the present document identifies which of their inputs and interpretations remain applicable.

The audited machine-readable inventory contains all **72 escalation operating configurations** (6 classifiers × 3 feature groups × 2 label definitions × 2 cost regimes). See [`classifier_inventory_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/classifier_inventory_72.csv). Every row records pD, pFA, BA, benefit, cost regime, exact table, and PDF page. The full analytic projections and Pareto classifications are also retained in the results directory.

## Primary source and provenance audit

Primary source: `~/Downloads/SOCTRA_JournalArticle_2026.pdf`, 42 pages, 373,204 bytes, SHA-256 `1053de0ee82e40d4f9990f3f3117fd635db60daffc49555594ae8674256e4f91` at the time of this audit.

| Cost regime | Label definitions | Source table | PDF page | Fields transcribed |
|---|---|---:|---:|---|
| Symmetric | Original and standardized | Table 5 | 39 | BA, pFA, pD |
| Asymmetric, c̄M = 3 × c̄FA | Original and standardized | Table 7 | 41 | Normalized Bayes benefit, BA, pFA, pD |

The article’s Table 5 gives 18 model/feature combinations, with separate original and standardized columns, hence 36 symmetric configurations. Table 7 likewise gives 36 asymmetric configurations. Table 6 (PDF p. 40) concerns **reporting**, and was excluded. No web page, abstract, bibliography, partial version, or recalculated operating point was used to fill the 72 values. `~/Downloads/Alert_Triage_No_Authors.tex` was used only as a secondary transcription check; the PDF remains the cited authority. Neither local source file is copied into the repository; the PDF checksum and exact page/table pointers make the transcription auditable without republishing the article file.

The article defines normalized Bayes benefit as balanced accuracy under equal false-alarm and miss costs. Consequently, symmetric rows carry the published BA as the corresponding benefit, marked as an identity from the paper’s definition (not as an independently printed column in Table 5). The asymmetric benefit values are transcribed directly from Table 7; they have **not** been reconstructed from pD/pFA. The script checks the BA identity `BA = (pD + 1 − pFA)/2` against each printed BA to the precision allowed by four-decimal rounding. All 72 rows pass.

The source contains rates and point estimates, not sampling variances or confidence intervals for the operating points. Therefore the Pareto analysis below is a deterministic comparison of reported points, not a test of statistically significant dominance. “Non-dominated” means only that no other reported point in the same label-definition and cost-regime group has both at least as high pD and at most as high pFA, with one strict improvement.

## Corrected Pareto frontiers

The four frontiers are calculated separately: label definitions are never mixed, and symmetric/asymmetric operating points are never treated as interchangeable.

| Label definition | Cost regime | Non-dominated configurations (pD, pFA; BA; BNB) |
|---|---|---|
| Original | Symmetric, Table 5 | LR A+C (0.8000, 0.2050; 0.7975; 0.7975); Bayesian MLP A+C (0.8500, 0.2056; 0.8222; 0.8222); LSEnsemble A+C (0.7500, 0.1510; 0.7995; 0.7995) |
| Standardized | Symmetric, Table 5 | LR A+C (0.6842, 0.0081; 0.8381; 0.8381); Bayesian MLP A+C (0.7042, 0.0154; 0.8444; 0.8444); LightGBM A+C (0.8421, 0.0450; 0.8986; 0.8986); LightGBM C (0.8947, 0.4051; 0.7448; 0.7448) |
| Original | Asymmetric, Table 7 | Bayesian MLP A+C (0.9250, 0.3632; 0.7809; 0.8530); RF A+C (0.9500, 0.5279; 0.7111; 0.8305); LightGBM C (0.9750, 0.6025; 0.6862; 0.8306); Bayesian MLP C (1.0000, 0.7692; 0.6154; 0.8077) |
| Standardized | Asymmetric, Table 7 | Bayesian MLP A (0.6842, 0.0148; 0.8347; 0.7595); Bayesian MLP A+C (0.7368, 0.1512; 0.7928; 0.7648); RF A+C (0.9474, 0.1938; 0.8768; 0.9121); LSEnsemble A (0.9649, 0.2695; 0.8477; 0.9063); LightGBM A+C (1.0000, 0.3351; 0.8324; 0.9162) |

BA and BNB are included to expose their relationship to the detection/false-alarm trade-off, not to rank one objective as universally preferred. Full pointwise front/non-front labels and equivalent-point counts are in [`statistical_pareto_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/statistical_pareto_72.csv).

## Analytic workload projections

For each point, the audit recomputed `q = pi*pD + (1-pi)*pFA`, expected TP/FP/FN/TN and positive recommendations per 1,000 alerts. Under the existing Phase 2 synthetic assumptions, expected arrivals to L2 are `lambda_L1*q`; the work projections use the existing roster, service map, eligibility, homogeneous class-conditional error assumption, and the same fractional-flow capacity function used by Phase 2. These are **offered-load calculations**, not simulated utilization, queue lengths, SLA rates, or GMV estimates. False-positive work is counted as unnecessary offered L2 work; false-negative work is an omitted need, not an executed job.

Using the frozen 6-L1 roster, effective L1 capacity is 28.4186 alerts/h. With 2/3/4 L2 analysts, the existing capacity routine gives 2.5594 / 3.9232 / 5.3391 routed investigations/h for the reference class mix. Since the current analytical model assumes classifier error rates do not vary by project/class, the positive recommendation mix remains the reference project mix; L2 capacity therefore varies by roster size, not by classifier point. This reproduces the Phase 2 composition assumption rather than asserting that real classifiers have class-independent errors.

For the PDF-implied test prevalences (original: 40/14,449 as implied by Table 1 IR; standardized: 19/14,449 as implied by Table 1 IR), across the 3-L2 roster and `rho_L1 = 0.85/1.25`, the full 18-point groups span the following expected recommendation fractions and offered L2 loads:

| Labels | Costs | q range | Offered ρL2 range |
|---|---|---:|---:|
| Original | Symmetric | 0.1527–0.3527 | 0.940–3.194 |
| Original | Asymmetric | 0.3648–0.9468 | 2.246–8.572 |
| Standardized | Symmetric | 0.0090–0.4057 | 0.055–3.674 |
| Standardized | Asymmetric | 0.0157–0.9676 | 0.097–8.762 |

The very wide ranges principally reflect variation in pFA under rare positive prevalence. A high-pD point may also impose much greater unnecessary work; whether that work is acceptable depends on required detection, class-specific task duration, and L2 capacity. `analytic_load_72.csv` gives each calculation, including per-1,000 confusion expectations, TP/FP/FN work, per-hour offered work, and 2/3/4-L2 roster results. It includes separate original-label prevalence rows for the PDF-implied test prevalence, the previously audited 39/14,449 test count, and the 210/63,410 historical population; standardized projections use only the PDF-implied 19/14,449 test prevalence. None treats historical labels as objective technical need.

### Prevalence discrepancy requiring care

PDF Table 1 (p. 10) reports a test-set original-label imbalance ratio of 360.23 and rounded positive proportion 0.0028. For N=14,449, the IR implies 40 positives and 14,409 negatives. The earlier local SOCTRA data audit reported 39 positive and 14,410 negative original labels. These cannot both describe the same exact partition. The correction therefore does not silently overwrite either source: the PDF-implied 40-count is primary for projections of the article’s published test metrics, while 39/14,449 and 210/63,410 are preserved as explicit sensitivities. Standardized test IR 759.47 implies 19 positives for N=14,449. Exact class counts should be treated as inferred from the article’s rounded table statistics unless the underlying article partition is separately reconciled.

An additional configuration/provenance discrepancy was found while planning reuse of the simulations: the prior `phase2.json` labels its original test prevalence “39/14,449” but stores `pi=0.002699840128036543`, which is **not** `39/14,449` (0.002699148730015918). The previous episode CSVs use the stored decimal. Thus the earlier 25-point rate crosswalk is exact, but the original-label episode prevalence must be cited as that legacy configured synthetic probability, not as an exact 39-count prevalence. The analytical CSV in this audit separately includes exact 39/14,449 and PDF-implied 40/14,449 rows; it does not retroactively alter episode outputs.

## Crosswalk to the earlier 25-point inventory and simulations

All 25 rows in the previous Phase 2 inventory match an operating point in PDF Table 5 by label definition, classifier, feature group, pD, pFA, and BA. Thus the earlier **simulated episodes** remain interpretable for those 25 symmetric-cost operating points (and the nine-point simulation subset remains interpretable for its exact matched points). They are synthetic simulations of those rates, not runs of classifier predictions on SOCTRA alerts.

The previous inventory was nevertheless incomplete and its source/cost interpretation is superseded:

1. It included 25 of the 36 symmetric Table 5 points and omitted 11 symmetric points: the six original-label C-only points, original-label LSEnsemble A and A+C, and standardized-label LSEnsemble A, C, and A+C.
2. It included **none** of the 36 distinct asymmetric Table 7 operating points. The prior report’s asymmetric Bayes-benefit values were calculations on symmetric Table 5 rates; those were not the Table 7 asymmetric classifier configurations.
3. Within original-label symmetric results, the corrected frontier replaces RF A+C with LSEnsemble A+C: RF A+C is dominated there by the same-pD, lower-pFA LSEnsemble A+C point. The earlier frontier omitted that LSEnsemble point. The standardized symmetric frontier is unchanged, although it remains a reported-point frontier without inferential uncertainty.
4. Hence the earlier operational conclusions remain valid only for their simulated subset of Table 5-style symmetric rates and their synthetic workload assumptions. They do not answer whether the distinct asymmetric Table 7 operating points change the operational ranking or classifier-by-organization interaction.

The exact 25-row mapping is in [`prior_25_crosswalk.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/prior_25_crosswalk.csv). This correction leaves all prior report and result files byte-for-byte untouched.

## Points on the corrected frontier not yet simulated

Ten non-dominated operating points are absent from the earlier simulation subset and therefore would need new simulation episodes before making operational claims about them:

| Label definition | Cost regime | Missing frontier configurations |
|---|---|---|
| Original | Symmetric | LSEnsemble A+C |
| Original | Asymmetric | Bayesian MLP A+C; RF A+C; LightGBM C; Bayesian MLP C |
| Standardized | Asymmetric | Bayesian MLP A; Bayesian MLP A+C; RF A+C; LSEnsemble A; LightGBM A+C |

The four standardized symmetric frontier points (LR A+C, Bayesian MLP A+C, LightGBM A+C, LightGBM C) were already simulated. No additional simulation is authorized or performed in this source-correction step. The ten missing frontier points are not a result-selected shortlist: they are exactly the point-estimate Pareto-frontier configurations of the newly authoritative tables that have no corresponding earlier episodes.

## Impact on conclusions

The correction strengthens the empirical input basis from 25 to 72 published operating configurations and changes the scope of what is known. It **does not** invalidate the numerical output for the earlier matched symmetric-point simulations. It does invalidate any implication that those runs covered both cost regimes, and it corrects the original-label symmetric frontier. In particular, no operational conclusion about the distinct asymmetric Table 7 operating points, their congestion consequences, or their interactions with D1/P1/WAPS is currently supported. The old experiments support conditional conclusions for selected Table 5 rate pairs only.

At the analytic level, Table 7 substantially broadens the load envelope: the highest PDF-implied q reaches about 0.947 for original labels and 0.968 for standardized labels, versus maxima about 0.353 and 0.406 among symmetric points. Under rare prevalence, this increase is driven mainly by pFA. This identifies which new frontier points materially change offered L2 load, but it cannot establish that the extra detections compensate operationally for that work. That requires new simulation, which has deliberately not been run here.

All figures remain conditional on: aggregate rounded rates, prevalence proxy, automatic acceptance, exchangeable errors across synthetic classes, frozen synthetic service/eligibility and continuous staffing, and the assumption that historical escalation labels approximate the modeled need state. They are not direct operating recommendations for GMV-CERT.

## Reproducibility and generated files

- Primary transcription/calculation script: [`build_pdf_source_audit.py`](build_pdf_source_audit.py).
- 72-row authoritative inventory: [`classifier_inventory_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/classifier_inventory_72.csv).
- Pointwise Pareto audit: [`statistical_pareto_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/statistical_pareto_72.csv).
- Analytic offered-load projections: [`analytic_load_72.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/analytic_load_72.csv).
- Crosswalk for prior inventory: [`prior_25_crosswalk.csv`](../../results/soc_triage_classifier_operating_impact_source_audit/prior_25_crosswalk.csv).
- Source checksum and audit metadata: [`audit_metadata.json`](../../results/soc_triage_classifier_operating_impact_source_audit/audit_metadata.json).

Rebuild the derived files without running simulation: `python studies/soc_triage_classifier_operating_impact/build_pdf_source_audit.py`.
