# HLS-CE-03 — H3 Refutatory Campaign Results

- **Execution date:** 2026-10-24
- **Campaign:** 20 paired seeds (0–19), 2,000 train / 500 validation / 1,000 test examples per task and seed
- **Code commit used:** `8a7b5e8212e7e1fb3d2e902af219bd2b45af32ab`
- **Status:** campaign executed; H3 not statistically supported.

## Result and interpretation

Both primary point estimates have the directions stated in H3: the distilled receiver has a slightly higher mean T3 accuracy than the hard-label refit control, while the collective mean under fixed O0 is lower after transfer. Neither paired-seed 95% confidence interval excludes zero. Therefore the run does **not** provide statistically sufficient evidence for H3. This is an inconclusive result for the specified synthetic design, not evidence that the effect is absent in general.

The adaptive reassignment changes O0 in only one seed (seed 3; two task responsibilities change). Its C2−C1 collective accuracy difference is positive in that seed and zero in the other 19. The mean recovery is small and its interval includes zero. Reorganization did not establish a reliable collective recovery in this campaign.

## Paired test-set contrasts

Accuracy differences are reported in percentage points (pp). Standard deviation and 95% intervals are across the 20 paired **seed-level** differences, using Student's t interval with 19 degrees of freedom. The query examples are not treated as independent replications.

| Contrast | Mean (pp) | SD (pp) | 95% CI (pp) | Positive / negative / zero seeds |
|---|---:|---:|---:|---:|
| A. A1 distilled − hard-label refit, T3 | +0.155 | 2.249 | [−0.897, +1.207] | 10 / 9 / 1 |
| B. A1 distilled − A1 initial, T3 (descriptive) | +0.115 | 1.544 | [−0.608, +0.838] | 10 / 10 / 0 |
| C. Fixed organization C1 − C0, same O0 | −0.917 | 6.497 | [−3.958, +2.124] | 8 / 12 / 0 |
| D. Reorganization C2 − C1 | +0.418 | 1.871 | [−0.457, +1.294] | 1 / 0 / 19 |
| E. Total collective change C2 − C0 | −0.498 | 6.825 | [−3.693, +2.696] | 8 / 12 / 0 |

H3's two point-sign conditions are both met, but statistical support requires A's interval to be wholly above zero and C's interval to be wholly below zero. Neither requirement is met. H3 is therefore **not confirmed**. The intervals are broad relative to the observed point effects.

## Training and transfer costs

Times are measured wall-clock seconds on the recorded local environment. They are descriptive, machine-dependent measurements; no equivalence of effective compute is claimed.

| Operation | Mean time | SD | Paired-seed 95% CI |
|---|---:|---:|---:|
| Initial training of all three models | 2.346 s | 0.034 s | [2.330, 2.362] s |
| Distillation student fit | 2.428 ms | 2.658 ms | [1.184, 3.672] ms |
| No-distillation hard-label refit | 1.047 ms | 0.443 ms | [0.840, 1.255] ms |
| Student-fit time minus refit time | +1.381 ms | 2.675 ms | [+0.129, +2.633] ms |
| Donor inference for transfer | 0.752 ms | 1.065 ms | [0.254, 1.251] ms |
| Full transfer (donor inference + student fit) | 3.180 ms | 2.925 ms | [1.812, 4.549] ms |

The A1 optimizer used 5–7 iterations in each condition: distillation mean 5.80 (SD 0.52), hard-label refit mean 5.95 (SD 0.60); paired difference −0.15 iterations (95% CI [−0.464, +0.164]). The distillation fit took longer in 19 seeds and shorter in one. The distillation representation processes two weighted rows per original example, so equal `max_iter` settings do not imply equal effective computational work. Initial fit time by model averaged 0.0025 s for A1, 1.070 s for A2, and 1.273 s for A3.

## Reproducibility and integrity

- Campaign command: `python experiments/synthetic/hls_ce03_h3_transfer.py --run-campaign`
- Analysis-only command: `python experiments/synthetic/analyze_hls_ce03_h3_results.py`
- Analysis uses the existing result artifact only; it does not train or infer with models.
- Runtime: Python 3.11.9; scikit-learn 1.5.2; NumPy 1.26.4; SciPy 1.13.1; macOS 27.0.1, arm64.
- All seeds 0–19 are present exactly once. C3 is stored as an alias of C2 and is not counted or exported as another observation.
- Raw `results.json` SHA-256: `73f69998bd86f988808bccc5477dfbf4abbde59f772424b90cab9b4d735401bb`.
- The run manifest records code commit, configuration hash, environment and raw result hash. Raw per-seed metrics and fitted parameters remain preserved in the result artifact.
- The pre-campaign JSON configuration is preserved unchanged from the run commit. Its status and prose `H3_rule` fields are pre-run metadata and lag the executable code's corrected contrast; the run used the code at the recorded commit, whose output summary records the operative rule and whose raw results record the serialized parameter values. This documentation discrepancy did not alter execution; it is retained here for traceability rather than silently rewriting the pre-run artifact.

## Artifacts

- [Raw campaign results, including all per-seed records and configuration](../../results/experiments/hls_ce03_h3_transfer/results.json)
- [Per-seed conditions](../../results/experiments/hls_ce03_h3_transfer/condition_metrics_by_seed.csv)
- [Five requested paired contrasts and per-seed costs](../../results/experiments/hls_ce03_h3_transfer/paired_contrasts_by_seed.csv)
- [Derived statistical summary and provenance](../../results/experiments/hls_ce03_h3_transfer/derived_analysis.json)
- [Derived-analysis hashes](../../results/experiments/hls_ce03_h3_transfer/analysis_manifest.json)
- [Frozen protocol parameters](../../experiments/configs/hls_ce03_h3_transfer.json)

## Limitations and execution notes

This is one synthetic three-task design with one transfer direction and one fixed initial organization. A3's teacher probabilities are generated in-sample on T3 training examples, as specified; teacher overfit may affect transfer. Timing is noisy at millisecond scale and does not measure energy or monetary cost. Only validation selects O0/O1; test results are used for evaluation. The run answers the prespecified contrasts for this design but does not establish general transfer harms, benefits, or reorganization value.

No task, model, seed, data-generation parameter, hyperparameter or transfer operation was changed after observing outcomes. No follow-up campaign was run.
