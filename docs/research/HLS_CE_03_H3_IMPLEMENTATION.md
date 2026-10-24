# HLS-CE-03 — H3 Pilot Implementation

**Status: IMPLEMENTED; 20-SEED CAMPAIGN EXECUTED**

This document records the executable implementation of E3's proposed refutatory H3 protocol. The campaign results and interpretation are in the [campaign report](HLS_CE_03_H3_CAMPAIGN_RESULTS.md); the raw records and hashes are retained in the linked result directory.

## Hypothesis and primary contrasts

H3 requires both an individual benefit to A1 on T3 **versus the hard-label refit without distillation** and a collective accuracy loss under the unchanged initial organization O0. The comparison with the original A1 is retained as a separate descriptive contrast. Reorganization is a secondary contrast: the post-transfer validation-selected organization O1 is evaluated on the same reserved test sets. Effects are summarized across seeds; the seed, not each query, is the independent unit for the specified seed-level confidence interval.

## Reproducible implementation

- Implementation: [`experiments/synthetic/hls_ce03_h3_transfer.py`](../../experiments/synthetic/hls_ce03_h3_transfer.py)
- Frozen parameters and execution convention: [`experiments/configs/hls_ce03_h3_transfer.json`](../../experiments/configs/hls_ce03_h3_transfer.json)
- Functional tests: [`tests/test_hls_ce03_h3_transfer.py`](../../tests/test_hls_ce03_h3_transfer.py)

The three tasks use a shared ten-dimensional input and independently derived random streams. T1 uses a linear `make_classification` task; T2 uses `make_circles` with eight nuisance features; T3 uses an interaction label based on `X0*X1 + X2*X3`. The stated label noise, task sizes, estimator settings, distillation weight, temperature, tie break, and seed range are frozen in the JSON configuration.

Because E3 specified equal initial example budgets but no task-to-agent specialization, all three agents are trained on the same pooled 6,000 labeled examples (2,000 per task). This avoids assigning an initial task-specific data advantage. The scaler is also fitted once on the shared pooled inputs. The transfer then warm-starts A1 and fits it on T3 using a 50/50 mixture of true labels and A3's soft probabilities. For the binary logistic model, soft Bernoulli targets are represented by two copies of each feature vector with complementary sample weights. This is an implementation of the specified distillation operation, not a modification of any success probability.

## Protocol equivalences recorded without adding conditions

Two pairs in the supplied protocol do not define distinct operations:

1. **Controls 1 and 2** both say to retrain A1 on the same examples with true labels and the same optimization budget, without donor probabilities. The implementation performs that operation once and labels it as satisfying both controls. It does not invent a cold-start or other comparison.
2. **C2 and C3** both choose the minimum-error one-to-one assignment among the same six permutations using the same post-transfer validation matrix. They are therefore exactly identical under the supplied definitions. Results store C2 once and identify C3 as its alias; no second observation or CSV row is emitted.

These identities are structural consequences of the written protocol; they are not empirical findings. If E3 intended distinct controls, their operational distinction would need a protocol amendment before the campaign, not a post-test adjustment.

## Selection, evaluation, and statistics

O0 is selected exclusively from pre-transfer validation accuracy and then held fixed for C0 and C1. O1 is selected exclusively from post-transfer validation accuracy. Both enumerate all six one-agent-per-task permutations and use a deterministic lexicographic tie break. Test data are only scored after assignments are fixed. Test-only best-permutation gaps are labeled retrospective diagnostics and never guide selection. The validation assignment gap is computed against the best of the six feasible assignments, not against an unconstrained per-task choice.

For each seed the output schema records the individual A1 T3 contrast against the no-distillation refit, the descriptive contrast against initial A1, C1−C0, C2−C1, task-level accuracy/log-loss, validation matrices, assignments, changed responsibilities, fitted A1 parameters, training losses, transfer/reorganization/inference times, and specified controls. The summary reports mean, median, sample standard deviation, 95% paired-seed Student-t intervals, and sign counts. Point estimates satisfying both directions are reported separately from statistical support. H3 is supported by the prespecified rule only when the interval for the individual transfer-versus-control effect is wholly positive and the interval for the fixed-organization collective effect is wholly negative. This is not proof of causality or broad generality.

## Functional verification and current limits

The focused tests exercise deterministic task construction, shapes and binary labels, weighted soft-target encoding, assignment enumeration and tie-breaking, invalid-input handling, a small fit/control fixture, paired-seed summaries, and the guard that fixes campaign seeds to 0–19. The separate campaign was run only after explicit CE authorization.

The implementation uses in-sample A3 probabilities on T3 training examples, as the protocol requests probabilities on T3 training examples. This can transmit teacher overfit and must be acknowledged when interpreting the observed outcomes. The synthetic tasks and equal-task-weight objective establish an executable controlled instance, not external validity. Wall-clock measurements are machine-dependent; the output records them but does not equate time with monetary or energy cost. The observed point signs match H3, but the paired 95% intervals do not support either required effect conclusively; see the [campaign report](HLS_CE_03_H3_CAMPAIGN_RESULTS.md).
