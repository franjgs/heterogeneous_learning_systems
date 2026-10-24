# HLS-CE-03 — Diagnosis of the First H3 Campaign

- **Scope:** read-only analysis of the 20 completed seeds in the first HLS-CE-03 campaign. No model was trained or invoked.
- **Campaign code commit:** `8a7b5e8212e7e1fb3d2e902af219bd2b45af32ab`
- **Raw results SHA-256:** `73f69998bd86f988808bccc5477dfbf4abbde59f772424b90cab9b4d735401bb`.

## Executive diagnosis

The data show a substantial T3 advantage for the donor A3 over initial A1, but the point estimate for incremental T3 accuracy from distillation over the no-distillation refit is small and uncertain. The recipient was already trained on the same pooled T3 labels later used for transfer; the teacher also produces in-sample probabilities on those examples. Thus this implementation supplies no new labeled T3 cases to A1; it adds a teacher-derived signal over examples already seen.

The main structural reason the collective effect can differ from the individual T3 effect is assignment: O0 assigns A1 to T1 in 18/20 seeds, A2 to T2 in all 20, and A3 to T3 in 18. Re-fitting A1 only on T3 can change its deployed T1 performance while the team continues to use A1 on T1. Fixed-organization C1−C0's per-task mean changes are −2.73 pp on assigned T1, 0 pp on T2, and −0.02 pp on T3, whose equal-weight average is −0.917 pp. These are descriptive observed changes; intervals are wide and include zero. The campaign does not establish that transfer caused a general collective harm.

## 1. Donor advantage and recipient response

Validation matrices contain all agent/task cells. Across seeds, the average validation accuracies were:

| Agent | T1 linear | T2 nonlinear | T3 interactions |
|---|---:|---:|---:|
| A1 logistic | 47.19% | 49.96% | 50.58% |
| A2 random forest | 48.34% | 84.09% | 65.32% |
| A3 MLP | 47.61% | 62.90% | 73.01% |

On validation, A3 exceeded initial A1 on T3 by **22.43 pp** (seed-paired 95% CI [20.60, 24.26]); the difference was positive in all 20 seeds. This is clear evidence of a donor advantage on the recorded validation sets. A3's individual T3 test score was not saved for every seed. It can be recovered from C0 only in the 18 seeds where validation-selected O0 assigned A3 to T3: on that validation-selected subset, donor test accuracy averaged 73.40%, versus 49.99% for initial A1, paired gap **23.41 pp** (95% CI [22.34, 24.48]). This subset is conditional on O0 and is not a complete all-seed donor test matrix.

On T3 test, A1 distillation minus hard-label refit averaged **+0.155 pp** (SD 2.249; 95% CI [−0.897, +1.207]); it was positive in 10 seeds, negative in 9, and zero in 1. Distillation minus initial A1 was +0.115 pp (95% CI [−0.608, +0.838]); the hard-label refit minus initial A1 was −0.040 pp (95% CI [−1.370, +1.290]). These estimates do not establish a positive incremental benefit; the interval also does not establish a zero effect.

### Observed task-specific changes in A1

| Test contrast | T1 | T2 | T3 |
|---|---:|---:|---:|
| Distilled − initial A1, mean pp (95% CI) | −1.47 [−10.89, +7.95] | −0.50 [−1.19, +0.19] | +0.115 [−0.608, +0.838] |
| Distilled − hard-label refit, mean pp (95% CI) | −3.255 [−9.865, +3.355] | −0.600 [−1.486, +0.286] | +0.155 [−0.897, +1.207] |

The direction and scale vary by seed, especially on T1. The result supports a possible transfer-versus-retention tradeoff in this implementation, but not a stable mean loss: all displayed intervals include zero. A plausible explanation is **forgetting from task-only refitting**: initial A1 training used the pooled T1/T2/T3 data, while the transfer refit optimizes on T3 alone. The data do not isolate this explanation causally from seed-specific fitting variability.

## 2. Organization and assignment margins

O0 selected `A1→T1, A2→T2, A3→T3` in 18 seeds. In the other two (seeds 3 and 9), it selected `A3→T1, A2→T2, A1→T3`. O1 selected the first assignment in 19 seeds and the second only in seed 9. Thus O1 differed from O0 in seed 3 only, swapping A1/A3 across T1/T3; two responsibilities changed.

The margin below is the best minus second-best equal-task mean validation accuracy across all six feasible one-to-one assignments:

| Validation matrix | Mean margin | Median | Range |
|---|---:|---:|---:|
| Before transfer | 6.52 pp | 6.47 pp | 0.80–11.07 pp |
| After transfer | 7.23 pp | 7.27 pp | 2.73–10.87 pp |
| Change in margin | +0.71 pp | +0.33 pp | −4.87–+7.60 pp |

The average margin increase is uncertain (95% paired-seed CI [−1.04, +2.46] pp). In seed 3, the pre-transfer margin was only 1.40 pp. After refitting, A1's T1 validation accuracy increased by 23.0 pp and its T3 validation accuracy fell by 2.6 pp; the selected assignment flipped and the post-transfer best-versus-runner-up margin became 7.13 pp. Seed 9 also began with a narrow 1.07 pp margin, but its ordering did not flip; the post-transfer margin was 2.73 pp. Elsewhere the same assignment remained best, even where the relative scores moved.

**Observed explanation for the 19 unchanged O1 assignments:** A2 has a large validation advantage on T2 (84.09% mean), and A3 has an advantage on T3 (73.01%); the one-agent-per-task constraint makes these assignments valuable together. A1 is usually allocated to T1 by the remaining permutation. Transfer changes only A1, and for 19 seeds the changes do not reverse the best permutation. This is a property of this measured matrix and constraint, not a general claim about assignment stability.

The post-transfer regret of retaining O0 versus O1 on validation is zero in 19 seeds and 7.13 pp in seed 3; its mean is 0.357 pp (95% CI [−0.390, +1.103]). The test C2−C1 improvement is likewise concentrated in seed 3: +8.37 pp there and zero in 19 seeds, giving +0.418 pp overall (95% CI [−0.457, +1.294]). Reorganization therefore has a small average effect because it is selected only once, though it matters substantially in that seed.

## 3. Variables limiting observable effects

These are features of the executed setup, not proposed changes to its results:

1. **No new receiver data:** all models initially train on the same 6,000 pooled labeled examples, including the exact 2,000 T3 training examples reused for the transfer refit. Transfer does not expose A1 to new labeled T3 cases.
2. **In-sample teacher outputs:** A3 supplies probabilities on the T3 training examples on which it was trained. This may make the teacher signal less informative about held-out cases.
3. **Receiver hypothesis class:** A1 is logistic regression, while T3 is defined by interactions. Distillation cannot expand A1's feature representation; it only changes fitted logistic parameters.
4. **Task-only refit and retention:** the transferred A1 is refit on T3 only, despite being initially trained on the pooled tasks. This can change non-target T1/T2 competence relevant to O0.
5. **Assignment discreteness and specialization:** only six permutations are feasible, A2 is strongly associated with T2, and A3 is strongest on T3. A1 changes must overcome the joint permutation tradeoff to move O1.
6. **Objective and measurement:** assignment selection minimizes equal-task validation error (equivalently maximizes mean validation accuracy); it does not account for uncertainty or margins. Test scoring is exact on the saved query set, but seed-level effects vary considerably.
7. **Task identity:** agents train on pooled examples from three different label-generating tasks without an explicit task-ID input. This can blur task-specific mappings; the campaign does not isolate its effect.

## 4. Evidence limits

- The complete A3 test matrix by task was not retained. A3's T3 test performance is directly available only for the 18 seeds in which O0 selected A3 for T3; do not generalize that subset result to all 20 without qualification.
- Per-agent validation matrices are saved, but full per-agent test matrices are not. The fixed-team C0/C1 task scores expose only the assigned agent's test performance.
- In-sample probabilities, a single donor/receiver direction, three synthetic tasks, 20 seeds, and one model configuration limit interpretation.
- The margins are computed from saved validation error matrices; no per-assignment utility table was stored in the original run. The accompanying derived table reconstructs all six utilities without fitting models.
- Timing records are wall-clock and machine-dependent; they cannot explain model quality and do not measure energy or monetary cost.

## 5. Technical recommendations for a separately approved iteration

These are recommendations only; this diagnostic does not amend the protocol or authorize another campaign.

1. Preserve a complete individual agent × task test matrix, all six validation assignment utilities, and per-seed decision margins before interpreting organizational stability.
2. If the scientific target is incremental knowledge transfer, distinguish new recipient information from reusing the recipient's existing labeled examples; produce teacher predictions out-of-fold or on a disjoint transfer set, while keeping test sealed.
3. Keep the no-distillation refit as the primary individual baseline and report transfer-minus-refit alongside transfer-minus-initial. If retention is part of the question, specify in advance how prior task data enter the refit rather than attributing forgetting to transfer alone.
4. Estimate uncertainty/power for the collective contrast using the observed seed-level variance before deciding whether a later experiment can resolve effects of the observed scale. Do not tune to the observed seed-3 effect.
5. Record actual per-agent test matrices and convergence work in any future run; the current campaign only permits task-specific donor test inference for a validation-selected subset.

## Reproducible derived artifacts

All following artifacts are calculated from the preserved campaign records; no model fitting or inference occurs:

- [Read-only diagnostic analyzer](../../experiments/synthetic/analyze_hls_ce03_h3_diagnostic.py)
- [Diagnostic summary and per-seed values](../../results/experiments/hls_ce03_h3_transfer/diagnostic_analysis.json)
- [Per-seed assignments, margins, A1 changes and available donor test values](../../results/experiments/hls_ce03_h3_transfer/diagnostic_by_seed.csv)
- [All six assignment validation utilities by seed](../../results/experiments/hls_ce03_h3_transfer/assignment_utilities_by_seed.csv)

Reproduce with: `python experiments/synthetic/analyze_hls_ce03_h3_diagnostic.py`.
