# HLS-CE-03 — H3 second campaign results (V2)

**Execution date:** 26 October 2026. **Scope:** the authorized 20-seed
synthetic campaign, seeds 0–19. **Status:** completed; no V3 or follow-up
campaign is proposed here. This report describes only the implemented
synthetic instance and does not claim scientific originality.

## Protocol and C3 preflight

V2 preserves the three tasks, three sklearn architectures, assignment rule,
metrics, paired seed design, and seeds 0–19 from V1. It generates 1,000 new
T3 examples per seed with a separate deterministic split stream, disjoint
from original train/validation/test inputs. The new examples are excluded
from all initial training, validation, and test sets.

Before execution, the implementation and focused tests verified that:

1. C2 and C3 receive the same transfer input matrix and the same frozen A1
   initialization.
2. C3 retains exactly the multiset of A3 probabilities used by C2 and
   permutes their row correspondence.
3. A permutation is generated from a seed-specific deterministic RNG stream;
   both the seed and full permutation are recorded for each run.
4. C1, C2, and C3 use the same architecture, scaler, optimizer settings,
   original inputs, weighted-row encoding, and configured `max_iter` budget.
5. Realized optimizer iterations and elapsed fit time are recorded
   separately. Equality of effective computational cost is not assumed.

The focused V1/V2 suite passed **26 tests** before the campaign. C3 is a
negative control for the input-to-teacher-score correspondence; it is not a
separate positive-transfer claim.

## Treatments and estimands

- **C0:** A1 unchanged.
- **C1:** A1 warm-start refit on new T3 inputs with true labels.
- **C2:** same refit using A3 probabilities on those inputs.
- **C3:** same refit using the C2 probability multiset permuted across inputs.

O0 is selected using only initial validation and remains fixed for C0–C3.
Each updated condition also receives an assignment selected only on its own
validation matrix. The six assignment utilities and full agent×task
validation/test metrics are retained. C0's readapted result aliases O0 and
is not counted twice.

The statistical unit is the seed. Intervals below are paired Student-t 95%
intervals across the 20 seed-level differences (df=19); test examples are
not treated as independent experimental replicates. No test result was used
to choose a condition, parameter, assignment, or seed.

## Individual A1 performance

Mean test accuracy by task (proportion; the full intervals and log-loss
results are in `results.json`):

| Condition | T1 linear | T2 nonlinear | T3 interactions |
|---|---:|---:|---:|
| C0 unchanged | 0.4446 | 0.5001 | 0.5017 |
| C1 direct labels | 0.5760 | 0.4987 | 0.5014 |
| C2 A3 distillation | 0.4428 | 0.4985 | 0.5032 |
| C3 permuted probabilities | 0.4952 | 0.4964 | 0.4973 |

Paired T3 contrasts, with values expressed in percentage points (pp):

| Contrast | Mean pp | SD pp | 95% CI pp | Signs across seeds (+/−/0) |
|---|---:|---:|---:|---:|
| C2 − C1 | +0.18 | 2.66 | [−1.06, +1.42] | 8 / 11 / 1 |
| C2 − C3 | +0.59 | 2.18 | [−0.43, +1.61] | 12 / 8 / 0 |
| C2 − C0 | +0.15 | 1.65 | [−0.62, +0.92] | 11 / 8 / 1 |

C2's point estimates are slightly higher on T3, but none of these intervals
excludes zero. There is no statistically supported T3 accuracy advantage
for distillation over either comparator in this run.

### Retention and non-target behavior

On T1, paired changes from C0 were: C1−C0 **+13.14 pp** (SD 24.18; 95% CI
[+1.82,+24.46], 16 positive / 4 negative seeds); C2−C0 **−0.19 pp** (SD
8.84; CI [−4.32,+3.95], 9 positive / 11 negative); C3−C0 **+5.06 pp**
(SD 18.82; CI [−3.75,+13.86], 12 positive / 8 negative). C1−C2 on T1
was +13.33 pp (SD 23.06; CI [+2.53,+24.12]). Thus direct-label refitting
changed non-target T1 performance in this setup; the distillation and
permuted-control changes were inconclusive. The result is an observed
cross-task effect, not evidence that transfer generally preserves or
damages prior competence.

## Collective performance under fixed O0

Equal-task-weight test accuracy under O0 averaged 0.6726 for C0, 0.7027 for
C1, 0.6692 for C2, and 0.6812 for C3. Paired changes from C0:

| Contrast | Mean pp | SD pp | 95% CI pp | Signs (+/−) |
|---|---:|---:|---:|---:|
| C1 − C0 | +3.00 | 7.23 | [−6.38, +0.38] | 14 / 6 |
| C2 − C0 | −0.34 | 2.72 | [−1.61, +0.93] | 10 / 10 |
| C3 − C0 | +0.86 | 5.73 | [−3.54, +1.82] | 11 / 9 |

C1−C2 was **+3.34 pp** (SD 7.00; 95% CI [+0.07,+6.62], 14 positive / 6
negative seeds), favoring the supervised update in this particular fixed
organization. C2−C3 was −1.20 pp (SD 4.78; CI [−3.44,+1.03], 7 positive /
13 negative), inconclusive.

O0 assigned A1 to T1 in 18/20 seeds. The substantial C1/C2 difference on
T1 is therefore compatible with contributing to the collective C1−C2
difference. This is a decomposition consistent with the observed assignment
and metrics; it is not a separately randomized causal test of that pathway.

## Reorganization

Validation-selected O1 differed from O0 in 3/20 seeds for C1, 3/20 for C2,
and 2/20 for C3. Test accuracy changes O1−O0 were:

| Condition | Mean pp | SD pp | 95% CI pp | Positive / negative / zero seeds |
|---|---:|---:|---:|---:|
| C1 | +1.53 | 6.45 | [−1.48, +4.55] | 2 / 1 / 17 |
| C2 | +0.58 | 2.81 | [−0.74, +1.89] | 2 / 1 / 17 |
| C3 | +1.34 | 4.26 | [−0.66, +3.33] | 2 / 0 / 18 |

None of the readaptation intervals excludes zero. Since O1 is selected on
validation, O1−O0 on test evaluates the validation-based selection procedure;
it is not an oracle comparison.

## Costs and configured versus realized budget

Across seeds, mean initial training time for all three agents was 2.343 s.
Mean A1 update fit time was 2.156 ms (C1), 1.304 ms (C2), and 2.423 ms
(C3). C2 additionally used A3 inference on the new T3 batch (mean 0.934
ms). Mean optimizer iterations were 6.25, 5.60, and 6.40 respectively.
Despite identical configured solver, `C`, initialization, row workload and
iteration cap, realized optimization work and wall time differed; these
figures do **not** establish equal effective compute. They are machine- and
run-condition-dependent measurements. The evaluation inference timings are
recorded per condition, model, and task in each seed record; assignment
enumeration time was not separately timed.

## Interpretation and limits

- **Signs:** C2−C0 on T3 is positive while fixed-O0 C2−C0 is negative, the
  directional pattern in H3. Both effects are small and their intervals
  include zero. The joint H3 pattern is therefore not statistically
  supported.
- **C2−C1:** the T3 individual contrast is inconclusive, while fixed-O0
  collective performance favors C1. C1 uses ground-truth labels and C2 uses
  A3 soft targets, so this contrast alone cannot identify transfer as the
  cause of a benefit or harm.
- **C2−C3:** this preserves the same probability multiset while changing its
  correspondence to inputs. Neither the T3 individual nor fixed-team
  collective contrast is conclusive; the campaign does not establish a
  collective benefit from correctly aligned donor information.
- **Reorganization:** assignments rarely changed and O1−O0 intervals include
  zero; there is no supported recovery claim.
- **Generalization:** conclusions are limited to these three synthetic task
  generators, this transfer direction, this model set, this data budget and
  these 20 seeds. Confidence intervals are unadjusted across multiple
  reported contrasts; the analyses are diagnostic, not a novelty claim.

## Reproducibility and artifacts

Run command: `python experiments/synthetic/hls_ce03_h3_transfer_v2.py --run-campaign`.
The run used Python 3.11.9, NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.2
on `macOS-27.0.1-arm64-arm-64bit`. The manifest records the source commit
present at execution, code hash, artifact hashes and seeds.

- Full raw per-seed records, complete matrices, six assignment utilities,
  permutations, timing and summary: [`results.json`](../../results/experiments/hls_ce03_h3_transfer_v2/results.json).
- Compact team metrics: [`team_metrics_by_seed.csv`](../../results/experiments/hls_ce03_h3_transfer_v2/team_metrics_by_seed.csv).
- Derived seed-level requested contrasts and costs:
  [`paired_contrasts_by_seed.csv`](../../results/experiments/hls_ce03_h3_transfer_v2/paired_contrasts_by_seed.csv).
- Run manifest: [`manifest.json`](../../results/experiments/hls_ce03_h3_transfer_v2/manifest.json).
- V2 runner, frozen config, implementation notes, and focused tests are
  linked from the implementation record:
  [`HLS_CE_03_H3_SECOND_ITERATION_IMPLEMENTATION.md`](HLS_CE_03_H3_SECOND_ITERATION_IMPLEMENTATION.md).

The V1 campaign directory and its `results.json` were left unchanged; its
SHA-256 remains `73f69998bd86f988808bccc5477dfbf4abbde59f772424b90cab9b4d735401bb`.
