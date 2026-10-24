# HLS-CE-01 — Existing FAST/DEEP complementarity analysis

**Record date:** 24 October 2026. **Data:** the archived corrected MMLU test
scores only. This is a read-only reanalysis; no model inference, policy
selection, experiment, or historical-result modification was performed.

## Data and estimand

FAST is `HuggingFaceTB/SmolLM2-360M-Instruct`; DEEP is
`HuggingFaceTB/SmolLM2-1.7B-Instruct`. We joined the 160 test queries by
`query_id` in [`test_model_scores.csv.gz`](../../results/experiments/hls_dynamic_capacity_organization_corrected/test_model_scores.csv.gz).
Each model independently scored the original MMLU query and its four options;
the stored answer is the highest-scoring option letter. Confidence is the
normalized probability mass of that predicted option. These are independent
answers to `x`, not a DEEP response conditioned on FAST's answer.

For each query let `F=1` and `D=1` denote correct FAST and DEEP responses.
The paired table is:

| FAST | DEEP | Count | Probability | 95% CI |
|---|---|---:|---:|---:|
| Correct | Correct | 21 | 13.13% | 8.13–18.75% |
| Incorrect | Incorrect | 70 | 43.75% | 36.25–51.25% |
| Incorrect | Correct | 51 | 31.88% | 25.00–38.75% |
| Correct | Incorrect | 18 | 11.25% | 6.88–16.25% |

FAST accuracy is 24.38% (39/160) and DEEP accuracy is 45.00% (72/160).
Among the 121 FAST errors, DEEP is independently correct on 51 (42.15%).
These paired outcomes show complementary independent error patterns in this
test sample; they do not measure review or causal correction.

## Results by subject

Each subject has 40 queries. Intervals below are 95% Wilson intervals for
each cell proportion within that subject.

| Subject | Both correct | Both wrong | FAST wrong / DEEP correct | FAST correct / DEEP wrong |
|---|---:|---:|---:|---:|
| Biology | 6/40, 15.0% [7.1, 29.1] | 19/40, 47.5% [32.9, 62.5] | 11/40, 27.5% [16.1, 42.8] | 4/40, 10.0% [4.0, 23.1] |
| Mathematics | 4/40, 10.0% [4.0, 23.1] | 25/40, 62.5% [47.0, 75.8] | 4/40, 10.0% [4.0, 23.1] | 7/40, 17.5% [8.7, 31.9] |
| Psychology | 6/40, 15.0% [7.1, 29.1] | 15/40, 37.5% [24.2, 53.0] | 17/40, 42.5% [28.5, 57.8] | 2/40, 5.0% [1.4, 16.5] |
| US history | 5/40, 12.5% [5.5, 26.1] | 11/40, 27.5% [16.1, 42.8] | 19/40, 47.5% [32.9, 62.5] | 5/40, 12.5% [5.5, 26.1] |

The independent correction opportunity is most frequent in this sample in
psychology and US history, and least frequent in mathematics. Potential harm
from replacing a correct FAST option with the independent DEEP option is
highest in mathematics among these four small subject samples. These
descriptive differences have wide intervals and should not be generalized
beyond this test set.

## Does FAST confidence identify the events?

We evaluated confidence as a ranking signal, without choosing a threshold or
changing a policy. “Opportunity” is the event FAST is wrong and independent
DEEP is correct; lower FAST confidence is the positive ranking score
(`1 − confidence`). “Potential interference” is FAST correct and independent
DEEP wrong; higher FAST confidence is the score, since this marks a case where
blindly replacing FAST could discard its correct answer. AUC 0.5 corresponds
to chance ranking. 95% intervals are percentile intervals from 20,000
query-level bootstrap resamples, stratified to preserve 40 queries per
subject (seed 2401024).

| Event being ranked | Positive cases | FAST-confidence score | AUC [95% CI] | Assessment |
|---|---:|---|---:|---|
| Potential correction: FAST wrong, DEEP correct | 51/160 | `1 − confidence` | 0.586 [0.490, 0.680] | Weak and inconclusive discrimination; CI includes chance |
| Potential interference: FAST correct, DEEP wrong | 18/160 | `confidence` | 0.478 [0.341, 0.617] | No demonstrated discrimination; CI is broad and includes chance |

Subject-specific AUCs are highly variable and based on only 2–19 positive
events: correction opportunity 0.433 (biology), 0.604 (mathematics), 0.581
(psychology), 0.677 (US history); potential interference 0.354, 0.532, 0.553,
and 0.463 respectively. These are descriptive point estimates, not evidence
of reliable subject-specific triggers. FAST confidence values in this sample
are concentrated between 0.25 and 0.50 (158/160), further limiting useful
threshold resolution. The confidence is a normalized next-option score, not
a calibrated probability that FAST is correct.

## Retrospective margin and implementability

A retrospective best-of-pair oracle that knows both true labels would choose
the correct independent answer whenever either model is correct. It succeeds
on 90/160 queries: **56.25% accuracy** (stratified bootstrap 95% CI
48.75–63.75%). This is +31.88 percentage points over FAST (95% CI
25.00–38.75) and +11.25 points over DEEP (95% CI 6.88–16.25). The pointwise
oracle margin over the better fixed model, DEEP, is therefore 11.25 points in
this sample.

This is not an implementable policy: choosing between the two answers using
their correctness requires the hidden gold label. It is an upper bound for
these two independent outputs, not an estimate of the value of a confidence
trigger, answer review, or an operational selector. The archived cascade and
contextual-selection results remain the relevant executable-policy evidence;
this report does not retune them on test data.

## Limits and conclusion

- The test contains 160 queries from four MMLU subjects and one fixed pair of
  model revisions. The subject-level counts are small.
- Probabilities are paired query outcomes from independent single-pass option
  scoring. They cannot reveal how DEEP would respond if FAST's answer were
  shown to it.
- The confidence analysis is descriptive. Its overall AUC intervals do not
  show that FAST confidence reliably ranks either useful independent
  correction opportunities or potential replacement harms.
- Error complementarity and the best-of-pair oracle margin do not establish
  that sequential review would improve accuracy or quality-cost performance.
- No test outcomes were used to select a policy, threshold, or model. The
  bootstrap quantifies uncertainty in these archived query-level estimates;
  it does not create an independent replication.

The existing data establish that independent FAST and DEEP answers differ on
69/160 queries (51 FAST-only errors corrected by DEEP, 18 FAST-correct cases
where DEEP is wrong). They support a descriptive complementarity analysis and
a retrospective upper bound. They provide no evidence on the conditional
response `D(x,F(x))`; conclusions about answer-conditioned deliberation require
observations of that conditional response. This report authorizes no follow-up
inference, model execution, or campaign.

## Traceability

- Data and schemas: [existing-data assessment](HLS_CE_01_EXISTING_DATA_ASSESSMENT.md).
- Corrected MMLU protocol and historical policy results:
  [experiment report](../experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md).
- Contextual selection results and costs:
  [DCS-LA report](../experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md).
- Historical records remain unchanged in
  [`test_model_scores.csv.gz`](../../results/experiments/hls_dynamic_capacity_organization_corrected/test_model_scores.csv.gz).
