# Experimental results

## Campaign and analysis

The completed campaign contains 400 paired seed blocks (`711000000`–`711000399`), 216 conditions per block and 86,400 condition-seed episodes. The factorial design combines three frozen SOCTRA classifier operating points, D1/P1/WAPS, `rho_L1` 0.85/1.25, alpha 0.25/1.00, L2 team sizes 2/3/4, and L2 24x7/weekday 09:00–17:00 calendars. L1 remains 24x7. Each episode admits alerts for 168 natural hours and is evaluated through hour 240, with no terminal drain; thus the maximum 72-hour deadline of every admitted alert matures.

The paired calendar contrast is `8x5 − 24x7`; 95% intervals use 10,000 bootstrap replicates resampling seed blocks, with shared indices for paired arms. The unit is the seed block, not an episode row. Condition summaries and contrasts are in the campaign result directory described in `REPRODUCIBILITY.md`.

## Main finding: deadline completion

At the prespecified principal load (`rho_L1=0.85`), alpha 0.25 and three L2 analysts under D1, pooled `S_plus` was:

| Classifier | L2 24x7 | L2 weekday 8x5 | Paired change (8x5 − 24x7) |
|---|---:|---:|---:|
| LightGBM A+C | 0.850 (95% CI 0.836–0.864) | 0.720 (0.702–0.738) | −0.129 (paired CI −0.144 to −0.115) |
| LSEnsemble A+C | 0.850 (0.836–0.864) | 0.716 (0.698–0.734) | −0.134 (−0.148 to −0.119) |
| Bayesian MLP A+C | 0.724 (0.706–0.742) | 0.614 (0.595–0.632) | −0.110 (−0.123 to −0.097) |

These are synthetic task-completion-before-deadline outcomes, not verified incident resolution. With alpha 0.25 and `rho_L1=0.85`, the mean calendar contrast across the 27 classifier × policy × team-size cells was −0.126; all 27 point estimates were negative (range −0.146 to −0.109). This descriptive range is not a pooled estimand; the paired cellwise intervals are provided in the CSV.

The reduced calendar also increased L2 mean wait at the principal `n_L2=3` cells from effectively zero to about 15–17 natural hours, and the fraction of completed L2 tasks late was about 0.149–0.158. This is consistent with both fewer available hours and the placement of waits across nights/weekends. The contrast cannot isolate those two mechanisms because 8x5 has lower weekly capacity as well as discontinuous service.

## Alpha, classifier and policy patterns

At `rho_L1=0.85`, `n_L2=3`, and 8x5, lowering alpha from 1 to 0.25 generally improved `S_plus`; for example, the pooled D1 gain was about 0.077 for LightGBM, 0.335 for LSEnsemble, and 0.0028 for Bayesian MLP. At 24x7, the same paired alpha contrast was zero for these cells. These are model-specific effects: alpha scales false-positive service effort, so its deadline consequences become prominent when work competes across limited availability windows. The condition-level paired intervals in `paired_factor_contrasts.csv` should be consulted; these subgroup contrasts are exploratory within the prespecified factorial design.

The classifier ranking was not invariant across calendars. Under alpha 0.25, 24x7 LightGBM and LSEnsemble had identical pooled `S_plus` in the reported cell, while the 8x5 values differed slightly (0.720 and 0.716). Bayesian MLP remained lower. Classifier × calendar difference-in-differences are exported for every matched condition; they show that calendar penalties can vary by classifier. They do not establish that the classifiers have different real-world effectiveness.

Policy contrasts were zero or very small at the principal load. P1 differed from D1 by at most approximately 0.0005 in the displayed `n_L2=3`, alpha 0.25 cells; WAPS and D1 were identical in these outcomes. WAPS never switched to its P1 regime in the campaign (`WAPS_switch_count` is zero). Therefore this campaign provides little empirical separation among policies under this chosen traffic/capacity configuration; it does not show that these policies are generally equivalent. The result also means no policy winner is supported.

## Sensitivity and limits

At `rho_L1=1.25`, mean calendar penalties were more negative in most paired cells than at 0.85; the bootstrap difference-in-differences and confidence intervals are in `paired_factor_contrasts.csv`. Higher L1 load therefore compounds the calendar effect in this synthetic setup. The exact magnitude depends on classifier, alpha and L2 roster size.

The campaign reports late work, outstanding states at cutoff, waits, backlog, effective work, suspension and utilization over available time. Full row-level task audit files were not saved in this 400-block run; task lifecycle state is captured through per-episode counts/metrics, with detailed task records available only in pilot outputs where enabled. No terminal drain converts late completion to on-time completion. Detailed diagnosis of individual deadline misses would require a separately planned task-level audit rerun.

The 8x5 calendar is a configurable synthetic scenario (Monday–Friday 09:00–17:00), not information about GMV-CERT. The simulator assumes systematic acceptance of SOCTRA recommendations, synthetic needs and service durations, persistent assignment and suspension/resumption. It does not model incident resolution quality, customer reporting, handoffs, leave, external waits or operational outcomes.
