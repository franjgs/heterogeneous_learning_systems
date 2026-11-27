# Evidence synthesis: SOCTRA triage × HLS organization

> **Evidencia histórica:** las cifras y contrastes sintetizados provienen de campañas con sus respectivos flujos anteriores, incluidos estudios de servicio L1 antes de L2. No se reescriben ni se atribuyen al modelo organizativo vigente, que aún no está implementado. Véase [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Evidence base and status

This synthesis joins distinct evidence layers without treating them as one experiment. Source reports and outputs remain authoritative for detailed methods and tables.

| Evidence layer | What it contains | Status and traceability |
|---|---|---|
| HLS organization | D1/P1 confirmatory stationary comparisons; independent frozen HLS-B validation; dynamic operating-region studies | Confirmatory only for the prespecified synthetic estimands. See [confirmatory results](../soc_human_ai_organization/SOC_CONFIRMATORY_RESULTS.md), [HLS-B validation](../soc_human_ai_organization/SOC_HLSB_VALIDATION_RESULTS.md), and [scientific synthesis](../soc_human_ai_organization/SOC_HLS_FINAL_SCIENTIFIC_SYNTHESIS.md). |
| First SOCTRA–HLS pilot | 11 synthetic operating points, two need prevalences, two L1 loads, 10 paired seeds; 1,320 policy episodes | Development pilot, 10 seeds. Ref `df80a78e413c88f7cf22b807e8ee27f4e556a726`; [report](../soc_triage_organization_coupling/SOC_TRIAGE_ORGANIZATION_COUPLING_PILOT.md). |
| Classifier operating-impact phase 2 | 25 symmetric-cost published points characterized; selected points simulated; 40 paired seeds; 2 L1 loads, 3 L2 rosters and 3 policies | Exploratory. Ref `218dc7ba4616b26f7051d7548e6fbcecfd8bc5b8`; [report](../soc_triage_classifier_operating_impact/SOCTRA_CLASSIFIER_OPERATIONAL_IMPACT_PHASE2.md). Its old inventory is superseded for source coverage by the complete audit, while compatible simulated symmetric-rate rows remain conditional evidence. |
| Complete source audit | 72 SOCTRA escalation operating configurations from the article PDF; four separate label × cost Pareto sets | Deterministic transcription/source audit, not operational test evidence. For the linked classifier phase-2 report, see [operational impact study](../soc_triage_classifier_operating_impact/SOCTRA_CLASSIFIER_OPERATIONAL_IMPACT_PHASE2.md); source is the complete paper’s Tables 5 and 7. |
| Joint-frontier campaign | 13 joint statistical-frontier configurations plus four controls; 18,720 episode rows after exact reuse and justified repairs; 40 paired seed IDs; 3 policies | Exploratory, no correction for the many contrasts. Ref `3a199faf9cce6ef95e74258e4e282c456de0f0a6`; [campaign report](../soc_triage_classifier_frontier_campaign/SOCTRA_TRIAGE_CLASSIFIER_FRONTIER_CAMPAIGN.md). |
| Feasibility validation | Pooled (S_+\), paired seed-cluster bootstrap, heterogeneous capacity LP and 91,728 threshold rows from saved episodes | Reanalysis only, no new simulations. Commit `0e086e7a59f36110b8299ed3d8d143b459ada4a8`; [validation](../soc_triage_feasibility_frontier/SOC_TRIAGE_FEASIBILITY_VALIDATION.md). |

The joint campaign’s manifest traces the campaign configuration and output hashes, records phase-2 and pilot references, and documents compatible episode reuse. The feasibility manifest/configuration record 10,000 paired bootstrap draws with seed 20261121. Episode rows sharing a seed across conditions are dependent; the 18,720 rows must not be treated as independent replicates.

## What the combined evidence supports

### 1. Triage rates can alter workload in the model

Given prevalence π and class-invariant rates, (q=\pi p_D+(1-\pi)p_{FA}\). When π is small, the false-alarm term acts on most arrivals. The pilot’s old point had recommendation fractions 28.76% under its historical-evaluation prevalence and 30.80% under its synthetic prevalence; under ρL1=.85 the implied L2 offered-load ratios were 1.77 and 1.90. In the phase-2 reference roster at high L1 demand, standardized LightGBM A+C ((p_D=.8421,p_{FA}=.0450)) implied (q=.0460), 1.636 recommendations/h and offered ρL2=.417; standardized LightGBM C-only ((.8947,.4051)) implied (q=.4057), 14.413/h and ρL2=3.674. These are model-based workload projections conditional on synthetic prevalence, automatic acceptance, class-independent rates, and service mix.

The joint campaign showed why detection and induced work must be read together. At high L1 load, 3 L2 analysts, WAPS, and original labels, LSEnsemble A+C symmetric ((p_D=.75,p_{FA}=.151)) had mean correct/on-time score .5902 per admitted alert; Bayesian MLP A+C asymmetric ((.925,.3632)) had .4130. The latter increased synthetic detection of need (.666 to .805) but nearly doubled FP service offered per 1,000 alerts (123.9 to 297.4 h), reduced need SLA (.895 to .628), and had 88.7 mean terminal L2 backlog versus zero. The paired difference for the lower-FP point was +.1772 [+.1700,+.1844] over 40 seeds. This is a selected exploratory contrast, not evidence that the empirical models would cause those outcomes on real alerts.

### 2. Statistical metrics do not uniquely order operational trade-offs

In the joint campaign’s sampled grid, the largest mean correct/on-time result was LSEnsemble A+C symmetric for all 36 original-label combinations and LR A+C symmetric for all 18 standardized-label combinations. In none of the 54 combinations was the highest-BA point also the highest-mean correct/on-time point. This is descriptive over sampled points, prevalence/load/roster/policy conditions; it does not establish inferential dominance or a universal classifier. The operational Pareto analysis retains multiple trade-offs and does not impose an arbitrary scalar utility.

The audited 72-point inventory consists of four distinct Pareto groups (original/standardized labels × symmetric/asymmetric cost). The asymmetric points are not extra locations on one common ROC curve, and deterministic Pareto non-dominance of published rates is not statistical dominance: the source gives rounded point estimates without sampling covariance. The 13-point joint frontier is therefore a design reduction, not a winner declaration.

### 3. Organization can condition simulated outcomes; the interaction is not uniform

The 10-seed first pilot found that under its old high-FP point and ρL1=1.25 WAPS−D1 on the integrated correct/on-time score was +.09890 [+.08646,+.11133] under historical-evaluation prevalence and +.09549 [+.08351,+.10748] under synthetic prevalence; WAPS was only about +.0053 over P1. At low L1 load its contrast to D1 was approximately zero. The later phase-2 matrix found WAPS−D1 positive-separated in 45, negative-separated in 10 and inconclusive in 23 of 78 unadjusted condition contrasts, while WAPS−P1 was positive-separated in all 78. Difference-in-differences across classifier points had both signs; the report gives ranges −.0394 to +.0440 for WAPS-vs-D1 and −.0073 to +.0078 for WAPS-vs-P1. These broad counts are multiplicity-sensitive exploratory summaries, not corrected familywise findings.

In the joint campaign, classifier ordering and policy gaps depended on condition. A selected WAPS stratum had an interaction (change in WAPS−D1 between two classifier points) of +.0282 [+.0239,+.0325]. Across the campaign’s selected contrast families, interactions changed sign and were not multiplicity-adjusted. They support conditional classifier × organization interaction inside the model, not a single general WAPS advantage.

### 4. Feasibility is three constraints, not one score

The formal region jointly constrains detection, heterogeneous offered L2 load, and (S_+\). In the priority case (standardized LightGBM A+C symmetric; ρL1=1.25; 3 L2 analysts), the load LP gives ρL2=.41695, below .80. Across 40 seeds only 35 synthetic needs occur and 16 seeds have none. Pooled service is D1 19/35=.543 (IC95 [.368,.720]), P1 27/35=.771 ([.593,.914]), WAPS 25/35=.714 ([.542,.875]). P1−D1 is +.229 ([+.029,+.423]) in this exploratory paired bootstrap; WAPS−D1 is +.171 ([0,.361]) and WAPS−P1 −.057 ([−.194,+.069]). At illustrative thresholds (d_{min}=.80,\rho_{max}=.80,s_{min}=.70), P1 and WAPS pass the point estimate, but no policy’s lower confidence bound reaches .70. This does not establish a robust policy-dependent admissibility change.

The 91,728-row grid gives point and uncertainty states over thresholds, label groups, demands, rosters and policies. At the illustrative (.8,.8,.7) slice, 21 standardized condition-policy cells have point (S_+\ge.70), but none has a lower 95% bound at or above .70; the original-label cells are excluded by earlier detection/capacity requirements. Grid counts are not operational frequencies. In general, the simulation bootstrap conditions on published classifier rates and synthetic prevalence; it does not propagate their empirical estimation uncertainty.

### 5. Complementarity and adaptation are separate claims

The organizational studies establish that D1/P1 performance depends on the synthetic regime. Confirmatory stationary evidence found P1−D1 R/N +.0982 [+.0891,+.1073] at ρ=1.25 and disadvantages at lower loads. Frozen HLS-B improved on D1 by +.02820 [+.02526,+.03115] in a separately prespecified, equal-weight mixture of four synthetic conditions (100 seeds), concentrated in stationary overload; it did not show a conclusive D1 advantage in the two variable-regime conditions. This confirms a particular aggregate adaptation contrast, not universal superiority and not a classifier × organization integration result.

The later triage-coupling studies use different integrated outcomes and smaller/exploratory campaigns. Their WAPS contrasts cannot be substituted for that confirmatory R/N estimand. Nor does the confirmatory adaptation result establish that a particular SOCTRA classifier point is operationally preferred.

## Negative findings and boundaries

- No classifier is preferred universally across detection, false-positive work, omission risk, service, backlog, and deadlines without an externally justified requirement/utility.
- The sampled campaign’s maximum mean correct/on-time classifier did not change across the tested load/roster/policy regimes within each label definition. Descriptive changes in Pareto/admissibility status are sensitive to the selected objectives and thresholds.
- WAPS has not been shown to robustly shift the statistical or service-feasibility frontier. In the priority (S_+\) case, no policy clears the illustrative service threshold with a 95% lower bound.
- The 40-seed campaign contains few synthetic needs; there are 341 needs among 170,040 admitted alerts in its 240 unique trace conditions and 66 condition-seed cells have zero needs. Priority case has 35 total needs.
- A high false-positive recommendation is modeled as full L2 investigation. A real false alarm might need only a brief check. False negatives omit necessary work and are not equivalent to saved workload.

## Evidence needed for external interpretation

No assertion here attributes analyst practice, acceptance behavior, service times, or true L2 need to GMV-CERT. Stronger external interpretation would require, at minimum, an adjudicated definition/label for true L2 need; individual predictions on the relevant independent alerts with class/project error composition; observed acceptance and override behavior; time/service distributions and eligible-resource roster; operational deadline meaning; and enough positive cases to estimate conditional timeliness. These are evidence gaps, not a proposal for a new experimental campaign in this document.
