# HLS-CE-03 — Second Information-Protocol Iteration

- **Phase:** implementation and functional tests only. **Campaign status:** NOT RUN.
- **Scope:** a new executable V2 route; V1 code and results remain unchanged.

## Protocol implementation

V2 preserves T1–T3, the three original model architectures, pooled initial training data, the one-agent-per-task permutation policy, accuracy/log-loss evaluation, seeds 0–19, and the paired seed as the statistical unit. It adds a separate 1,000-example T3 transfer split for each seed using a distinct deterministic split stream. The data generator and a row-overlap check keep that split separate from all original train, validation, and test inputs.

The four treatments are:

- **C0:** unchanged initial models.
- **C1:** A1 warm-start refit on new T3 examples using true labels.
- **C2:** same A1 initialization and inputs, refit using only A3's soft probabilities on those new inputs.
- **C3:** same update with A3 probabilities permuted across inputs.

The distillation teacher is evaluated on new T3 inputs excluded from its initial training. No true label is used to create C2 or C3 student targets. C1/C2/C3 all use a common weighted-row encoding: two rows per original input, complementary class weights summing to one. They therefore have the same original examples, input rows per optimization pass, A1 initialization, scaler, logistic solver, regularization and `max_iter` cap. Actual convergence iterations and wall time are recorded and may differ; the implementation does not claim identical realized compute.

O0 is selected from initial validation and held fixed for all conditions. Each updated condition has a separate validation-selected readapted organization. C0's readapted case aliases O0 rather than recording the same test result twice. Every condition retains full agent×task validation and test matrices, all six validation assignment utilities, fixed-O0 team outcomes, and readapted outcomes.

The summary is designed to produce all pairwise treatment contrasts for individual A1 performance by task and collective fixed/readapted outcomes, with paired Student-t intervals across the 20 seeds. **C2−C1 alone does not identify positive or negative transfer:** C1 learns from ground-truth labels, while C2 learns from donor-derived soft probabilities. The two treatments receive different information.

## Files

- Runner: [`experiments/synthetic/hls_ce03_h3_transfer_v2.py`](../../experiments/synthetic/hls_ce03_h3_transfer_v2.py)
- Frozen protocol parameters: [`experiments/configs/hls_ce03_h3_transfer_v2.json`](../../experiments/configs/hls_ce03_h3_transfer_v2.json)
- Focused functional tests: [`tests/test_hls_ce03_h3_transfer_v2.py`](../../tests/test_hls_ce03_h3_transfer_v2.py)
- Results destination if separately authorized: `results/experiments/hls_ce03_h3_transfer_v2/`

The tests use reduced fixture sizes to check data separation, target encoding, shared optimizer budget, assignment enumeration, complete matrices, paired-summary behavior and the campaign guard. They do not run seeds 0–19. This implementation makes no claim about H3 outcomes or scientific originality.

## Subsequent execution

The implementation-only status above records the phase when this note was
written. After the CE's separate C3 verification authorization, the full
20-seed campaign ran on 26 October 2026. See the [V2 campaign report](HLS_CE_03_H3_V2_CAMPAIGN_RESULTS.md)
and its linked raw per-seed artifacts for outcomes; this note's original
implementation-stage record and the V1 campaign remain unchanged.
