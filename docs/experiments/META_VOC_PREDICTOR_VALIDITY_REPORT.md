# META-VOC Predictor Validity Audit

**Status:** completed, bounded audit of the frozen predictor. This is not a new campaign or a reanalysis of Campaign 3's sequential policy outcomes.

## 1. Scientific question

Does the frozen C3.3 Ridge predictor identify states in which DEEP (Q11) has positive counterfactual production advantage over FAST (Q00), when that advantage is evaluated with the same horizon, conditional physical-history generation, and Q11 continuation used to construct the C3.2 training labels?

The audit distinguishes three questions: (i) whether the raw Ridge prediction tracks counterfactual advantage; (ii) whether the frozen META-VOC-50 routing rule preferentially selects states with larger positive advantage; and (iii) whether the previously observed sequential META-VOC results remain valid. These are not interchangeable. Positive production advantage is not, by itself, a cost-adjusted optimal routing decision.

## 2. Original C3.2 estimand and exact matching

The executable source of truth is [`targets.py`](../../experiments/synthetic/campaign3_c32_data/targets.py). It fixes `ELL = 11` (line 33), reconstructs the realized physical prefix in `realized_prefix()` (74–80), draws eleven further physical problems conditionally on that prefix in `conditional_future()` (83–92), and evaluates branches in `rollout()` (95–124) and `target_rows()` (127–168).

For a selected nonterminal pre-action state `h_t = (b_t, S_t, p_1..p_j, within-problem position)`, let `X00(h_t)` and `X11(h_t)` be the frozen Q00 and Q11 actions. Conditional on the realized physical prefix, each audit replicate draws future problems and observation innovations. Its paired label is:

```text
Delta_C3.2^(r)(h_t)
  = G^(r)(force X11 first; continue with Q11)
  - G^(r)(force X00 first; continue with Q11)
```

Here `G` sums `mu_true` from the current decision through the remaining decisions of the current physical problem and all decisions in the next eleven physical problems. There is no discounting. Both arms use the same conditional future problem sequence and standard-normal observation innovations; observations are recomputed from each branch's own `mu_true`. Capabilities and beliefs evolve independently by branch, and belief resets to the prior at each new physical problem. A C3.2 row is one stochastic paired realization, not the exact conditional expectation.

The audit matches this estimand. It does not substitute C4 H0, H1, or H2. At 800 selected states it also verified the frozen implementation equivalences FAST = Q00 and DEEP = Q11 exactly at the selected states. In 472 of 800 states the two initial actions were identical; these paired branches were reused, implying zero branch difference for those replicates by construction.

## 3. Data, source verification, and sampling

The source population was the already frozen Campaign 3 confirmatory state record, comprising 868 histories and 249,984 decision records across the existing G1–G4 domains. The audit reused the pre-existing, outcome-blind `HLS-C4-SAMPLE-v1` rule from [`sampling.py`](../../experiments/synthetic/campaign4_counterfactual_deliberation/sampling.py) unchanged: 50 states per domain in each of four nine-clock blocks, 800 total, with the existing policy/remaining quotas, hash-based choices, inclusion probabilities, and inverse-probability weights. It samples the finite recorded confirmatory state population; it is not a sample of all possible HLS states.

The frozen sample has equal domain counts (200 each). The sampling unit is a selected state; the inference cluster is `history_id`, retaining every sampled state from a resampled history. Inclusion probability is the frozen quota divided by three times the number of eligible histories in its domain/block. Pooled metrics give equal weight to the four domains, rather than allowing domain sample sizes to determine the aggregate. No state was selected using target outcomes or action disagreement.

Before target evaluation, SHA-256 checks passed for the frozen inputs:

| Artifact | SHA-256 |
|---|---|
| Confirmatory `runs.csv.gz` | `3c2d7310a510deed03264b9a6df30ffc09a0af5915cc76dba233d29eadfd9e28` |
| Confirmatory `trajectories.csv.gz` | `b4022b7a76c2aece607138d6d740ae854517fa171e889d09c557350c8da2e498` |
| Frozen Ridge `selector_model.json` | `1874b1f06a7122361677f5bb617132bd2eff3976fd1aa890d7152436fb59ba1d` |
| Frozen META-VOC `calibration.json` | `bf329147e4e62a98bbfc9ae48c75cbe1066c1ff73b87c6fce6b63cf4f796e94a` |
| C3.2 training `raw_mc_targets.csv` | `1891e5c7f32b70ff5628a5dd1055aca751e30363b5a783593ff07238daf287c9` |

The calibration manifest's model and training-data references matched these hashes. The audit recorded hashes for all source files used, including the C3.2 target code, C3.3 model/feature code, frozen META-VOC route, simulator, generator, and sampling implementation. The recorded repository HEAD at preparation was `cec804b00482c5a121bae5434893bc069208484c`; the full source-hash map is in [`frozen_sampling_manifest.json`](../../results/diagnostics/meta_voc_predictor_validity/frozen_sampling_manifest.json).

Reconstruction passed for all 800 selected states: 505 unique physical problem streams were checked against frozen stream hashes, and all 800 selected history-policy trajectories were replayed. Maximum absolute discrepancy was 0 for state/belief before and after; `mu_true` discrepancy was `2.22e-16`. Tolerances were `atol=rtol=1e-12`. The sampled states span clocks and include transitions whose reconstruction crosses problem boundaries and resets belief.

## 4. Counterfactual execution

For each sampled state, the audit reconstructed the prefix from the original `problem_seed` and frozen kernel, then generated eleven conditional future problems and matched observation innovations for Q00 and Q11. The future and observation streams were generated from an audit-only SHA-256 seed namespace, independent of the C3.2 training-label Monte Carlo streams. Each state used 32 paired Monte Carlo replicates (25,600 paired records total). Per-state estimates and their Monte Carlo uncertainty are therefore noisy estimates, not ground-truth oracle labels.

The exact frozen fitted Ridge model and calibration were loaded without fitting, coefficient changes, cost changes, threshold changes, or tie-rule changes. META-VOC-50 routing used the original ex-ante feature vector (the six entries of `S`, three belief entries `b`, and `tau/36`), Ridge standardization/prediction, calibrated predicted extra cost by remaining decisions, nonnegative-benefit clipping, score threshold, and SHA-256 feature-key tie break. No future values or labels entered routing. The raw predictor's positive classification is separately defined as predicted benefit `>= 0`; it is not the thresholded META-VOC route.

Uncertainty intervals are 2,000 percentile bootstrap replicates, seed `20261012`, stratified by domain and resampled at the `history_id` cluster level. Within each resampled state, its 32 paired Monte Carlo differences were resampled to propagate target Monte Carlo uncertainty. No individual Monte Carlo replicate was treated as a sampled state.

## 5. Predictor validity: pooled equal-domain results

Positive target states are defined by the state-level mean of 32 paired Monte Carlo differences being greater than zero. The same threshold is applied to the frozen raw Ridge prediction. These are empirical classifications against an uncertain Monte Carlo estimate.

| Metric | Estimate | 95% history-cluster / nested-MC interval |
|---|---:|---:|
| Positive target prevalence | 23.29% | — |
| Prediction bias (prediction − MC mean) | −0.0159 | [−0.0335, −0.0002] |
| MAE | 0.0987 | [0.0876, 0.1188] |
| RMSE | 0.2172 | [0.1783, 0.2699] |
| Weighted Pearson correlation | 0.0762 | [0.0076, 0.1437] |
| Weighted Spearman correlation | 0.0373 | point estimate |
| ROC-AUC | 0.6237 | [0.5724, 0.6666] |
| Sensitivity | 100.0% | [100.0%, 100.0%] |
| Specificity | 4.58% | [2.87%, 6.45%] |
| Precision | 24.14% | [20.66%, 27.48%] |
| Balanced accuracy | 52.29% | [51.44%, 53.22%] |

The raw Ridge prediction was nonnegative for 96.48% of weighted states. Thus high sensitivity is obtained with very poor specificity; it is not evidence of a useful binary opportunity detector. AUC indicates modest ranking discrimination, not close calibration. Weighted decile calibration is available in `calibration_bins.csv`; it is noisy and should be read alongside the large prediction error and Monte Carlo uncertainty.

## 6. Frozen META-VOC-50 routing results

The frozen router invoked DEEP on 50.71% of the weighted audit states. Among routed states, mean paired advantage was 0.0552 production units; among states routed to FAST it was also positive, 0.0448. The paired history-bootstrap difference between those conditional means was only 0.0104, with 95% interval [−0.0200, 0.0431]. Therefore this audit does not establish that routing identifies distinctly more valuable opportunities, even though the point estimate favors the DEEP-routed group.

Using the noisy state Monte Carlo mean as the positive/negative reference, 71.50% of DEEP invocations were “unproductive” (mean estimated advantage `<= 0`; 95% interval 67.09%–76.43%). The route missed 37.94% of estimated-positive states (95% interval 30.53%–46.16%). This definition ignores the uncertainty of individual state estimates; 71.60% of state-level normal-approximation MC intervals span zero. Hence these are diagnostics of the frozen target estimates, not certain labels.

The route's estimated mean advantage over always FAST was 0.0280 per sampled state [0.0157, 0.0422]. A nondeployable performance-only oracle that invokes DEEP exactly when the estimated mean is positive had estimated advantage 0.0656 [0.0523, 0.0844], leaving estimated regret 0.0376 [0.0291, 0.0501]. This oracle is not cost-adjusted and is not a feasible policy guarantee. The results do not establish that META-VOC is cost-optimal, or that its positive production advantages justify its computational expense.

## 7. Domain-specific findings

Each domain contains 200 states; point estimates use the frozen design weights. Intervals are the same history-clustered/nested-MC procedure. `Route Δ` is the paired difference between mean target advantage among META-VOC-routed DEEP states and FAST-routed states, not a causal treatment effect.

| Domain | AUC [95% interval] | MAE [95% interval] | DEEP route rate | Mean Δ if routed DEEP | Mean Δ if routed FAST | Route Δ [95% interval] |
|---|---|---|---:|---:|---:|---|
| G1 | 0.621 [0.526, 0.709] | 0.102 [0.082, 0.134] | 50.74% | 0.0773 | 0.0381 | 0.0392 [−0.0162, 0.0978] |
| G2 | 0.596 [0.499, 0.684] | 0.114 [0.085, 0.154] | 53.27% | 0.0621 | 0.0516 | 0.0105 [−0.0509, 0.0736] |
| G3 | 0.664 [0.565, 0.757] | 0.075 [0.062, 0.097] | 48.59% | 0.0311 | 0.0175 | 0.0136 [−0.0274, 0.0526] |
| G4 | 0.610 [0.497, 0.701] | 0.104 [0.071, 0.151] | 50.22% | 0.0488 | 0.0731 | −0.0243 [−0.1001, 0.0621] |
| Equal-domain pooled | 0.624 [0.572, 0.667] | 0.099 [0.088, 0.119] | 50.71% | 0.0552 | 0.0448 | 0.0104 [−0.0200, 0.0431] |

Sensitivity was 100% in each domain, while point specificity ranged from 1.94% to 7.52%. Route-conditioned differences are uncertain in every domain; G4 reverses the pooled point pattern. No causal effect of team geometry, capability maturation, or environment is identified by these observational domain comparisons.

## 8. Comparison with frozen Campaign 3 conclusions

| Existing conclusion | Audit classification | Basis and boundary |
|---|---|---|
| The C3 sequential META-VOC-50 comparison favored META-VOC over RANDOM-50 in G1/G2, with no advantage demonstrated in G3/G4. | **MAINTAINED** | The sequential confirmatory outcomes were not changed or re-estimated here. See [`CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md`](CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md). This audit addresses a different, state-conditional counterfactual target. |
| The frozen Ridge/META-VOC mechanism identifies states with positive C3.2-matched DEEP value. | **WEAKENED** | Discrimination is modest (pooled AUC 0.624); raw positivity is nearly universal and specificity is 4.6%; routed versus FAST-routed target means differ by 0.0104 with interval spanning zero. |
| C3 sequential results establish the Ridge proxy as the mechanism producing any META-VOC/RANDOM performance difference. | **REQUIRES REINTERPRETATION** | The audit does not show that the frozen predictor reliably targets the C3.2-matched opportunities. The sequential result remains a result of the whole policy comparison, but this mechanism is not established by it. |
| META-VOC is superior to informed alternative selectors. | **NOT EVALUATED BY THIS AUDIT** | This audit compares the frozen predictor/router with its own C3.2-matched counterfactual values; it introduces no alternative selector baseline. |
| Capability geometry or maturation causally explains domain differences in selector validity. | **NOT EVALUATED BY THIS AUDIT** | G1–G4 are frozen domains and observational strata here. No matched causal decomposition is performed. |

## 9. Limitations

- The 800 sampled states are a weighted subset of recorded confirmatory histories, selected under the existing C4 audit protocol; state-level conclusions are conditional on that finite source distribution.
- Each conditional value is estimated from 32 independent audit Monte Carlo replicates. Many state estimates remain too noisy to determine the sign; positive/negative classification is not ground truth.
- The estimand is specific to an initial Q11-versus-Q00 intervention with Q11 continuation, the C3.2 horizon, frozen physics, and the C3 confirmatory state distribution. It is not the recursively adaptive sequential value of computation under every future policy.
- META-VOC's cost estimate and score are unchanged, but this audit does not validate their calibration or establish a reward-to-computation utility tradeoff.
- Correlation/AUC uncertainty and route contrasts reflect finite histories and nested simulation uncertainty; the domain samples are not independent draws from a universal population of teams or environments.
- This is not a causal analysis of team geometry, maturation, or environmental dynamics, and does not evaluate informed alternative baselines.

## 10. Final validity verdict

**Ridge prediction of counterfactual advantage: LIMITED / WEAK.** The model has modest positive pooled rank discrimination, but small correlations, substantial prediction error, near-universal positive predictions, very low specificity, and uncertain domain-level behavior. It is not a well-supported calibrated statewise estimator of C3.2-matched advantage.

**META-VOC identification of useful DEEP opportunities: NOT ESTABLISHED.** The frozen route's DEEP-routed states have a slightly larger mean estimated advantage than FAST-routed states in the equal-domain pool, but the paired interval includes zero; FAST-routed states also have positive average advantage; many routed calls have nonpositive noisy estimated value; and G4's point contrast reverses. The audit neither proves the route useless nor validates it as a cost-adjusted selector.

**Existing Campaign 3 sequential evidence: MAINTAINED, with mechanistic interpretation narrowed.** The previously reported sequential META-VOC-50 versus RANDOM-50 results are untouched. The audit weakens any claim that those results demonstrate reliable identification of C3.2-defined positive opportunities. It does not invalidate the sequential comparison itself.

## 11. Incident and reproducibility

The first post-generation finalization attempt incorrectly counted one CSV read chunk per batch as one row, reported 50 instead of 25,600, and stopped before writing its execution manifest. This persistence/I/O incident is preserved in [`execution_incident.json`](../../results/diagnostics/meta_voc_predictor_validity/execution_incident.json). All 50 raw batches (512 rows each) were intact. A regression test was added for row-count finalization; the corrected finalizer counted rows, validated all state/replicate keys, and finalized the existing outputs without rerunning counterfactual rollouts. No target rows were overwritten, discarded, or changed because of the incident.

Reproduction/verification commands (execution uses resumable existing batches; do not rerun unless explicitly authorized):

```bash
pytest -q tests/test_meta_voc_predictor_validity.py
python -m experiments.synthetic.meta_voc_predictor_validity.audit --prepare
python -m experiments.synthetic.meta_voc_predictor_validity.audit --execute --workers 12 --batch-size 16
python -m experiments.synthetic.meta_voc_predictor_validity.audit --analyze
```

The execution used Python 3.11.9, NumPy 1.26.4, pandas 2.2.3, macOS 27.0.1 arm64, and 12 workers. Monte Carlo seed derivation and the 2,000-replicate bootstrap are in the manifests. Results and machine-readable outputs are isolated under [`results/diagnostics/meta_voc_predictor_validity/`](../../results/diagnostics/meta_voc_predictor_validity/). `derived_hashes.json` covers all generated artifacts except itself; `analysis_manifest.json` records the principal analysis-output hashes. The complete output directory and retained incident are intended to accompany this report.

## 12. Audit scope

No Campaign 4 horizon or broader analysis was executed. C3 source code, C3 frozen artifacts, Ridge coefficients, calibration, and manuscript were not modified. This report records the authorized predictor-validity audit only.
