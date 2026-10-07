# Campaign 1 — frozen test-range characterisation

## Status and provenance

Campaign 1 executed the pre-results protocol frozen at `bcc3ad8` against the test range frozen at `05b86cb`. It characterises the laboratory; it is not a competition between configurations, a strategy search, a test of C/N/M as predictors, or the main evidential campaign. No scenario, configuration, seed, condition, parameter, assessment criterion, or mechanism was changed after results were observed.

Campaign 0 provenance remains explicit. TR-PR is identical to H2 and is prior-diagnostic/not out-of-sample; TR-R is structurally related to H3; TR-G, TR-J, TR-HA, and TR-HB reorder problem content already used in Campaign 0; only TR-PM and TR-D are pre-performance Campaign 1 scenarios in the narrower sense recorded by the gate.

## Pre-specified execution

The exact factorial was eight frozen scenarios × four probes (G00, G04, G05, G07) × ten seeds (`0..9`) × three conditions (FULL, NO-DEVELOP, KNOWN-Z): 960 runs and 17,280 within-problem steps. Every problem lasted H=3; eta=.35, rho=.5, and sigma=.10. The same standard-normal innovation stream was used for a given seed and temporal position throughout the factorial.

- FULL uses the existing finite-belief dynamic MPC with development enabled.
- NO-DEVELOP uses the same `finite_choose_dynamic_action_v2` primitive with `develop=False`; it is not historical DISCOVER_ONLY.
- KNOWN-Z uses the frozen DEVELOP_KNOWN oracle.

Performance is exclusively `mu_true`. Noisy observed reward is retained because it drives Bayesian updating in unknown conditions, but it is not a performance outcome. FULL−NO-DEVELOP and FULL−KNOWN-Z are diagnostic comparisons, not an additive causal decomposition.

## Observed configuration × scenario range

Mean cumulative `mu_true` under FULL (ten seeds) was:

| Scenario | G00 | G04 | G05 | G07 | Configuration spread |
|---|---:|---:|---:|---:|---:|
| TR-PR | 29.537 | 30.101 | 29.524 | 30.824 | 1.299 |
| TR-PM | 26.317 | 28.305 | 27.685 | 29.031 | 2.714 |
| TR-G | 25.882 | 26.469 | 26.995 | 27.360 | 1.478 |
| TR-J | 25.336 | 26.344 | 26.536 | 27.294 | 1.958 |
| TR-R | 28.444 | 29.483 | 28.922 | 30.207 | 1.763 |
| TR-D | 25.424 | 25.916 | 26.509 | 26.645 | 1.220 |
| TR-HA | 25.854 | 26.467 | 26.971 | 27.392 | 1.538 |
| TR-HB | 25.578 | 26.408 | 26.717 | 27.315 | 1.737 |

G07 is the mean cumulative leader in all eight scenarios. This negative result is retained: the range does not generate multiple cumulative winners among these probes. It does not by itself determine the Campaign 1 assessment, which concerns the diversity of adaptive situations rather than winners.

Scenario sensitivity is not ordered by one change scalar. Both persistent scenarios have zero change after their first problem, yet TR-PM has the largest FULL configuration spread (2.714), while TR-PR has a spread of 1.299. TR-D has the smallest spread (1.220) despite continued displacement. Mean end-of-problem belief entropy under FULL ranges from .031 in TR-PR to .189 in TR-PM, and mean assignment changes range from 3.125 in TR-R to 7.25 in TR-J.

## Frozen controlled contrasts

The entries below are paired mean differences in cumulative `mu_true` under FULL, left scenario minus right scenario. Ranges over seeds remain available in `controlled_contrasts.csv`; no significance claim is made.

| Contrast | G00 | G04 | G05 | G07 |
|---|---:|---:|---:|---:|
| TR-PR − TR-PM | 3.220 | 1.796 | 1.839 | 1.793 |
| TR-G − TR-J | .546 | .126 | .459 | .066 |
| TR-R − TR-D | 3.020 | 3.567 | 2.413 | 3.562 |
| TR-HA − TR-HB | .276 | .059 | .254 | .077 |

### Represented versus mismatched persistence

TR-PR and TR-PM remain behaviorally simple for G04 and G07: their FULL actions and final capability totals coincide across the two scenarios, and FULL coincides with KNOWN-Z. Their performance differs because the true persistent production problems A and U differ; therefore the contrast must not be described as a pure causal effect of representational mismatch. G00 and G05 also show seed-dependent action and capability differences induced by observations under the unrepresented problem.

### Same content, different order

TR-G/TR-J produces clear history sensitivity for G00 and G05 but near-null mean cumulative differences for G04 and G07. For seed 0, G00 follows the same initial A policy, then the different U/B problem changes assignment and exposure. Later B/V allocations differ, producing different cell-level S even when aggregate capability sums nearly reconverge; the final-A action differs and final-problem performance is 5.455 under TR-G versus 4.884 under TR-J. G07 also changes intermediate assignments, but returns to the same final-A action and exactly the same seed-0 final-A performance (5.316). This is a useful negative trajectory: a distinct path need not remain performance-relevant.

### Recurrence versus continued displacement

TR-R/TR-D diverges after their common A→U prefix. For seed-0 G04, recurrence continues the established A/U allocation, whereas C/V/B induces later reassignment toward capability 2 and a different exposure matrix. The scenarios also end at different problems (A versus B) and are not content- or total-change-matched, so their positive cumulative difference is descriptive of different adaptive challenges, not a causal recurrence benefit.

### Familiar return after different histories

TR-HA/TR-HB starts and ends at A with matched content and transition-distance multiset. The mean cumulative order response is visible for G00/G05 and near-null for G04/G07. For seed-0 G05, the B/V-first path changes which agents exercise capability 2, later changes the first action at final A, and yields final-A performance 4.669 rather than 5.307. The same contrast can reconverge behaviorally for other configurations and seeds.

## Mechanistic controls

Across configurations, mean cumulative FULL−NO-DEVELOP ranges by scenario from 6.375 (TR-D) to 9.121 (TR-PR). Every one of the 32 scenario × configuration means is positive, but its size is highly configuration-dependent (for example, TR-D ranges from 2.929 for G05 to 10.416 for G00). The frozen range therefore contains different developmental consequences, but no development-liability case under this control.

Mean FULL−KNOWN-Z by scenario ranges from −.806 (TR-PM) to −1.909 (TR-D). Imperfect problem knowledge is consequential in several changing histories, while FULL and KNOWN-Z coincide for G04 and G07 in TR-PR, TR-PM, and TR-R. These exact/near-null controls help distinguish situations in which inference changes the trajectory from those in which the frozen controller selects the same actions despite uncertainty.

The retained causal record supports the intended reading:

```text
true problem
  -> belief and dynamic-MPC decision
  -> assignment
  -> continuous cell exposure
  -> MIS-v2 capability state
  -> later assignment
  -> mu_true.
```

This does not establish that development and imperfect knowledge have separable additive effects.

## Negative and null results

- G07 leads cumulative FULL performance in every frozen scenario.
- FULL−NO-DEVELOP is positive in every scenario × configuration mean; no capability-development liability is observed by that control.
- G04/G07 show near-null FULL order effects for TR-G/TR-J and TR-HA/TR-HB, despite nonidentical intermediate problems.
- FULL and KNOWN-Z are identical for G04/G07 in three scenarios.
- Some paths diverge in assignment or S and subsequently reconverge in behavior/performance; state difference alone is not an adaptive consequence.
- TR-PR and several problem contents are prior-diagnostic rather than wholly out-of-sample.

## Assessment: PASS

The frozen criteria yield **PASS**. The eight scenarios produce multiple interpretable demands: represented and mismatched persistence, content-matched order effects, recurrence versus continued displacement, and familiar return after different developmental histories. Development and imperfect-knowledge diagnostics vary across scenarios and configurations; clear divergences coexist with meaningful near-null controls. The results do not collapse to “more change is harder” or any other single scalar ordering.

PASS does not mean that every intended phenomenon appears. In particular, no development-liability case is identified, and the cumulative leader is universal. It means the compact range contains distinguishable causal trajectories and negative controls that are plausibly useful for later strategy comparison.

## Campaign 2 range recommendation

Retain all eight histories as the frozen Campaign 2 range unless a later pre-results design decision changes scope. This recommendation is based on structural coverage rather than effect size: PR/PM retain persistence and representation; G/J and HA/HB retain two controlled order/familiar-return questions plus near-null cases; R/D retain recurrence/displacement. Dropping the near-null pairs would select on observed effect and reduce the controls needed to detect strategy insensitivity.

## Artifacts and limitations

Raw authority is `runs.csv` and `trajectories.csv`; derived tables, five seed-0 representative contrast traces, three compact figures, the execution manifest, and `analysis_summary.json` are colocated in `results/campaigns/campaign1_test_range/`. Seed 0 was used uniformly for readable traces and was not selected by performance.

Campaign 1 characterises this frozen synthetic laboratory only. It does not demonstrate a generally superior team geometry, ecological validity, novelty detection, transfer, REFRAME, or future strategy discrimination. It does not estimate causal effects of C/N/M, and it does not establish additive contributions of DISCOVER and DEVELOP.

## Documentary closure

Campaign 1 is closed as a **test-range characterisation**, not as a comparison
of adaptive strategies. The bounded supported conclusion is: under the frozen
HLS laboratory, the pre-specified small controlled range produces multiple
interpretable adaptive trajectory patterns and different degrees of history
and configuration sensitivity. That makes it a suitable controlled range for
a later strategy comparison.

The conclusion does **not** rest on different configurations winning different
scenarios: G07 is the mean cumulative FULL leader in all eight. It rests on
observed differences in assignment, continuous exposure, capability state,
later action, and performance response, including informative reconvergence
and near-null cases. It does not establish universal team superiority, a
universal causal relation from C/N/M to performance, a pure mismatch effect
in PR/PM, a pure recurrence effect in R/D, a development liability, an
additive DISCOVER/DEVELOP decomposition, or a pure cost of DISCOVER.

All eight histories — TR-PR, TR-PM, TR-G, TR-J, TR-R, TR-D, TR-HA, and TR-HB
— are carried forward as the current small controlled HLS test range. They are
retained for structural coverage and for preservation of both positive and
negative controls, rather than selected by effect magnitude. The range is not
exhaustive. Campaign 2 has not been designed: no strategy family, comparator,
hypothesis, or execution protocol is implied by this closure.

`closure_provenance.json` records frozen design/result commits, the status of
each claim category, and SHA-256 values for authoritative Campaign 1 artifacts.
