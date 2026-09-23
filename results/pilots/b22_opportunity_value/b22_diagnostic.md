# B2.2 diagnostic

## 1. Validation

The independent reconstruction verified 60 unique opportunity updates and 1,200 unique analytical rows: five seeds, four domains, `N={25,50,100}`, `c={0,.02,.05,.10,.15}`, `B={1,2,5,10}`, and `kappa=0`. All incremental artifacts report CPU, direct-from-F0 updates, VALIDATION evaluation, no TEST use, zero teacher queries on the Fast trajectory, and exactly N teacher queries/pseudo-labels on the Deep trajectory. Recomputed `rho`, `V_F0`, `V_Fk`, `DeltaV`, `Omega`, `H`, the strict primary event, and every contribution agree within 1e-12. The decomposition and all 1200/1200 frontier checks pass.

## 2. Frozen classification

**INCONCLUSIVE.** There are 4/1200 observations with `rho>0,H>0`, so the frozen NULL criterion (no such observation anywhere) does not apply. None of the 240 domain/N/c/B cells has favorable results in at least two seeds, so the frozen POSITIVE criterion does not apply. There are 800/1200 observations with `rho>0,H<=0`. “NULL” is the protocol's exact no-favorable-observation outcome; it does not mean “the mechanism is rare.”

## 3. Four favorable cases

| seed | domain | N | c | B | rho | DeltaV | Omega | H | DeltaV_local | DeltaV_cross |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | cartoon | 25 | 0.020000 | 2 | 0.013567 | 0.007488 | 0.014976 | 0.001409 | 0.007488 | 0.000000 |
| 4 | cartoon | 25 | 0.020000 | 5 | 0.013567 | 0.007488 | 0.037440 | 0.023873 | 0.007488 | 0.000000 |
| 4 | cartoon | 25 | 0.020000 | 10 | 0.013567 | 0.007488 | 0.074879 | 0.061312 | 0.007488 | 0.000000 |
| 4 | cartoon | 50 | 0.020000 | 10 | 0.013567 | 0.002631 | 0.026314 | 0.012747 | 0.002631 | 0.000000 |

- `seed=4, cartoon, N=25, c=0.02, B=2`: S(F0)={"art_painting": 0.7301804414795152, "cartoon": 0.7856477012163212, "photo": 0.8854339288551906, "sketch": 0.7648913010753592}; S(F_k)={"art_painting": 0.6863430335433843, "cartoon": 0.8155994660503246, "photo": 0.8565129054959024, "sketch": 0.7603396557664972}; S(D)={"art_painting": 0.7597156143859591, "cartoon": 0.7920807031090078, "photo": 0.9465903157703571, "sketch": 0.8005712619144759}; contributions [photo=0.000000, art_painting=0.000000, cartoon=0.007488, sketch=0.000000]; actions F -> D+learning.
- `seed=4, cartoon, N=25, c=0.02, B=5`: S(F0)={"art_painting": 0.7301804414795152, "cartoon": 0.7856477012163212, "photo": 0.8854339288551906, "sketch": 0.7648913010753592}; S(F_k)={"art_painting": 0.6863430335433843, "cartoon": 0.8155994660503246, "photo": 0.8565129054959024, "sketch": 0.7603396557664972}; S(D)={"art_painting": 0.7597156143859591, "cartoon": 0.7920807031090078, "photo": 0.9465903157703571, "sketch": 0.8005712619144759}; contributions [photo=0.000000, art_painting=0.000000, cartoon=0.007488, sketch=0.000000]; actions F -> D+learning.
- `seed=4, cartoon, N=25, c=0.02, B=10`: S(F0)={"art_painting": 0.7301804414795152, "cartoon": 0.7856477012163212, "photo": 0.8854339288551906, "sketch": 0.7648913010753592}; S(F_k)={"art_painting": 0.6863430335433843, "cartoon": 0.8155994660503246, "photo": 0.8565129054959024, "sketch": 0.7603396557664972}; S(D)={"art_painting": 0.7597156143859591, "cartoon": 0.7920807031090078, "photo": 0.9465903157703571, "sketch": 0.8005712619144759}; contributions [photo=0.000000, art_painting=0.000000, cartoon=0.007488, sketch=0.000000]; actions F -> D+learning.
- `seed=4, cartoon, N=50, c=0.02, B=10`: S(F0)={"art_painting": 0.7301804414795152, "cartoon": 0.7856477012163212, "photo": 0.8854339288551906, "sketch": 0.7648913010753592}; S(F_k)={"art_painting": 0.6401707399250284, "cartoon": 0.7961731032556205, "photo": 0.83220017706749, "sketch": 0.7362427023456236}; S(D)={"art_painting": 0.7597156143859591, "cartoon": 0.7920807031090078, "photo": 0.9465903157703571, "sketch": 0.8005712619144759}; contributions [photo=0.000000, art_painting=0.000000, cartoon=0.002631, sketch=0.000000]; actions F -> D+learning.

All four analytical observations are `seed=4`, intervention `cartoon`, and `c=.02`; they represent only two learned states (`N=25` and `N=50`). The `N=25` state crosses at `B=2,5,10`; the `N=50` state only at `B=10`. Their distances from the exact frontier are their positive H values shown above. They are non-reproduced across seeds; the nearest is marginal (`H=0.001409`), while even the largest margin does not establish robustness.

## 4. DeltaV analysis

The following uses the 300 unique seed/domain/N/c realizations and removes the four identical B copies of each `DeltaV`.

| metric | n | mean | std | median | min | max | fraction_positive | fraction_zero | fraction_negative |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeltaV | 300 | -0.033396 | 0.030537 | -0.024748 | -0.150213 | 0.007488 | 0.023333 | 0.033333 | 0.943333 |
| DeltaV_local | 300 | -0.002686 | 0.007660 | 0.000000 | -0.031140 | 0.013476 | 0.243333 | 0.280000 | 0.476667 |
| DeltaV_cross | 300 | -0.030710 | 0.026911 | -0.022993 | -0.129473 | 0.004266 | 0.013333 | 0.086667 | 0.900000 |

`DeltaV` is negative in 283/300 (94.33%), zero in 10/300, and positive in 7/300. Thus these singleton updates normally reduce future operational value in this grid. Positive `DeltaV` never coincides with a positive cross-domain contribution (0/300 unique realizations; equivalently 0/1200 analytical rows). The full domain-by-N summaries are in `b22_deltaV_summary.csv`.

## 5. Competence-change matrix

Entries pool five seeds and three N values (15 updates per intervention/affected-domain cell).

| intervention_domain | affected_domain | mean | std | n_positive | n_zero | n_negative |
| --- | --- | --- | --- | --- | --- | --- |
| art_painting | photo | 0.004033 | 0.018275 | 9 | 0 | 6 |
| art_painting | art_painting | -0.016958 | 0.032158 | 6 | 0 | 9 |
| art_painting | cartoon | -0.089754 | 0.045513 | 0 | 0 | 15 |
| art_painting | sketch | -0.140788 | 0.058089 | 0 | 0 | 15 |
| cartoon | photo | -0.051802 | 0.030186 | 1 | 0 | 14 |
| cartoon | art_painting | -0.104358 | 0.067769 | 0 | 0 | 15 |
| cartoon | cartoon | -0.021058 | 0.026202 | 3 | 0 | 12 |
| cartoon | sketch | -0.065703 | 0.070498 | 3 | 0 | 12 |
| photo | photo | 0.021545 | 0.025503 | 10 | 0 | 5 |
| photo | art_painting | -0.040233 | 0.039587 | 2 | 0 | 13 |
| photo | cartoon | -0.134493 | 0.055134 | 0 | 0 | 15 |
| photo | sketch | -0.216038 | 0.068149 | 0 | 0 | 15 |
| sketch | photo | -0.318169 | 0.175234 | 0 | 0 | 15 |
| sketch | art_painting | -0.367811 | 0.152966 | 0 | 0 | 15 |
| sketch | cartoon | -0.179232 | 0.113509 | 0 | 0 | 15 |
| sketch | sketch | -0.149336 | 0.090734 | 0 | 0 | 15 |

The updates combine occasional local improvement with broad interference/forgetting. Across all 240 competence changes, 34 are positive and 206 negative. Nonlocal changes are negative in 165/180 cases. Operational routing masks 372/1200 nonzero competence changes at a particular c, but does not rescue the prevalent negative cross-domain changes. The per-N matrix in `b22_competence_changes.csv` reports signs across the five seeds separately for every N.

## 6. Effect of N

| N | mean_DeltaS_local | mean_DeltaS_cross | mean_DeltaV | positive_DeltaV_fraction | mean_H_given_rho_positive | favorable_rows |
| --- | --- | --- | --- | --- | --- | --- |
| 25 | -0.006972 | -0.064352 | -0.021649 | 0.050000 | -0.197491 | 3 |
| 50 | -0.047547 | -0.154787 | -0.036810 | 0.020000 | -0.291887 | 1 |
| 100 | -0.069836 | -0.206948 | -0.041729 | 0.000000 | -0.325950 | 0 |

More pseudo-labels do not increase useful learning in these aggregates. From N=25 to 50 to 100, mean local competence change falls from -0.006972 to -0.047547 to -0.069836; mean nonlocal change per affected domain falls from -0.064352 to -0.154787 to -0.206948; and mean `DeltaV` falls from -0.021649 to -0.036810 to -0.041729. The aggregate deterioration is monotone over the three frozen N values, and favorable rows fall from 3 to 1 to 0.

## 7. Effect of c

| c | rho_positive_updates | mean_DeltaV | DeltaV_positive_updates | favorable_rows |
| --- | --- | --- | --- | --- |
| 0.000000 | 18 | -0.010490 | 3 | 0 |
| 0.020000 | 21 | -0.014629 | 3 | 4 |
| 0.050000 | 42 | -0.024461 | 1 | 0 |
| 0.100000 | 60 | -0.048193 | 0 | 0 |
| 0.150000 | 60 | -0.069206 | 0 | 0 |

Increasing c both increases the number of currently Fast-preferred cases and changes which Fast competencies are exposed by the future max. The first effect raises `rho>0` from 18/60 at c=0 to 60/60 at c=.10 and .15. The second makes mean `DeltaV` progressively more negative, from -0.010490 at c=0 to -0.069206 at c=.15, because more of F's degraded competence enters future value. Favorable events occur only at c=.02.

## 8. Effect of B

| B | rho_positive | favorable |
| --- | --- | --- |
| 1 | 201 | 0 |
| 2 | 201 | 1 |
| 5 | 201 | 1 |
| 10 | 201 | 2 |

B leaves learning and `DeltaV` unchanged and only scales `Omega=B DeltaV`. The four favorable observations occur at B=2 (one), B=5 (one), and B=10 (two); none occurs at B=1. These are repeated valuations of two learned states, not four independent learning outcomes.

## 9. Why B2.2 was inconclusive

| metric | count | denominator | definition |
| --- | --- | --- | --- |
| rho_positive_unique | 201 | 300 | current Fast-preferred seed/domain/N/c realizations |
| DeltaV_positive_unique | 7 | 300 | positive future-value changes; B copies removed |
| rho_positive_and_DeltaV_positive | 5 | 300 | positive opportunity value where current sacrifice exists |
| positive_DeltaV_compensates_at_B10 | 2 | 5 | positive candidates that cross the frozen largest-B frontier |
| cross_domain_DeltaS_negative | 165 | 180 | negative nonlocal competence changes |
| routing_masked_nonzero_DeltaS | 372 | 1200 | nonzero competence changes with zero operational-value contribution |
| favorable_distinct_updates | 2 | 60 | distinct learned states among favorable analytical rows |
| favorable_seeds | 1 | 5 | seeds represented among favorable rows |

The dominant bottleneck is not a shortage of current-sacrifice cases: 201/300 unique c-valuations have `rho>0`. It is the absolute opportunity value: only 7/300 have positive `DeltaV`, only 5/300 combine positive `DeltaV` with `rho>0`, and only 2/5 of those compensate `rho` at the largest frozen B. Broad cross-domain degradation is the main empirical component of negative `DeltaV`; routing additionally masks some competence changes. Favorable outcomes occur in one seed only, so seed reproducibility is also absent.

## 10. Relation to B2.1

B2.1 found positive mean `Gamma_learn` in all 18 N-by-pair cells and measured a second difference between singleton and direct joint updates. B2.2 asks a different question: whether the absolute value of one singleton opportunity is large enough to pay a present operational sacrifice. Strong factorial interaction can coexist with weak or negative absolute singleton value. The results therefore distinguish interaction value from absolute opportunity value and are not contradictory.

## 11. Implications for RQ0

The event required by the proposed mechanism occurs in two learned states and four analytical valuations, but it fails the preregistered reproducibility criterion. B2.2 therefore does not yet provide sufficient support for `operation -> learning opportunity -> competence change -> future operational value`. It neither establishes nor refutes RQ0, does not show HLS superiority, and contains no TEST evidence.

## 12. What remains unresolved

The completed grid does not establish that an ex-ante policy can predict opportunity value, that the favorable event generalizes across seeds, or that its operational association is causal beyond the defined intervention. The relative roles of singleton-update learning dynamics, cross-domain interference, and future routing remain descriptive here.
