# HLS-CE-01 — Existing-data assessment for sequential deliberation

**Record date:** 24 October 2026. This is a documentary audit of existing
artifacts; no inference, experiment, or historical-result modification was
performed.

## Finding

Existing data support paired analysis of independent fast and deliberative
answers to the same MMLU query, including correctness, option probabilities,
confidence, and measured inference latency. They also support evaluation of
the already recorded confidence-triggered cascade, whose second model answers
the original query independently. They do **not** contain the response from a
deliberative model after it has been shown the fast model's answer. Therefore
they cannot estimate the incremental effect of answer-conditioned review
`D(x,F(x))` against either `F(x)` or independent `D(x)`.

For the corrected MMLU pilot, the designated FAST capability is
`HuggingFaceTB/SmolLM2-360M-Instruct` and the designated DEEP capability is
`HuggingFaceTB/SmolLM2-1.7B-Instruct`; the same score file also includes
`Qwen/Qwen2.5-0.5B-Instruct` as a third independent model. Each stored answer
is an option letter scored from the model's logits, rather than a free-text
generation.

The Campaign 3 META-VOC records are rich decision-level trajectories, but are
synthetic HLS planning decisions: FAST and DEEP are decision operators over a
state and belief, not language-model answers or a reviewer conditioned on a
first answer. They cannot serve as observations of `D(x,F(x))`.

## Artifact inventory and verified fields

| Evidence | File and row unit | Verified contents | Not present |
|---|---|---|---|
| Corrected MMLU pilot | [`test_model_scores.csv.gz`](../../results/experiments/hls_dynamic_capacity_organization_corrected/test_model_scores.csv.gz), one query–model row; 480 rows, 160 query IDs × 3 models | `query_id` (hash key), split, task type, model/revision, predicted and correct option letters, correctness, normalized A–D choice probabilities, confidence, token counts, per-query latency | Query statement/prompt, free-text answer or rationale, answer-conditioned review |
| Corrected MMLU timing repeats | [`test_latency_repetitions.csv`](../../results/experiments/hls_dynamic_capacity_organization_corrected/test_latency_repetitions.csv), one query–model–repeat row; 1,440 rows | Query key, task, model, repetition, latency, whether prediction matched base output | Selection overhead and review conditioned on another model's answer |
| Corrected pilot policy records | [`experiment_runs.json`](../../results/experiments/hls_dynamic_capacity_organization_corrected/experiment_runs.json), [`results.json`](../../results/experiments/hls_dynamic_capacity_organization_corrected/results.json), and [`quality_cost_curve_summary.csv`](../../results/experiments/hls_dynamic_capacity_organization_corrected/quality_cost_curve_summary.csv) | Experiment/policy configuration and per-query routes/events (where recorded), invocation latency and outcomes; aggregate quality–cost results | A conditional second response. Recorded cascade outcomes use the independent DEEP answer to the original query |
| Contextual selection policy results | [`test_policy_results.csv`](../../results/experiments/hls_contextual_capacity_selection/test_policy_results.csv), one row per query; 160 rows | Query key, task, each model's correctness flag, chosen model per policy, oracle choice, inference, selection and total latency | Answer text, probabilities, or a revision after seeing another model answer |
| Contextual selection decisions | [`dcs_test_decisions.csv`](../../results/experiments/hls_contextual_capacity_selection/dcs_test_decisions.csv), one row per query; 160 rows | Query key/task, selected model, and measured context extraction, TF-IDF, feature combination, neighbor search, local competence/selection, and total selection nanoseconds | Raw query text/TF-IDF vector and conditional review response |
| META-VOC aggregate runs | [`runs.csv.gz`](../../results/campaigns/campaign3_meta_voc_confirmatory/runs.csv.gz), one policy per history; 6,944 rows | History/team/kernel/replicate/policy, cumulative true production, compute and selector time, FAST/DEEP time and invocation counts, seeds and exogenous stream hashes, domain | Queries, language-model outputs, confidence, or response review |
| META-VOC trajectories | [`trajectories.csv.gz`](../../results/campaigns/campaign3_meta_voc_confirmatory/trajectories.csv.gz), one synthetic decision; 249,984 rows | History/policy/decision, time/budget state, route, score/predicted benefit/cost, action, true outcome, compute timings, state and belief before/after, domain/replicate | Text inputs or language-model answers; DEEP conditioned on a FAST answer |

The reports provide the interpretation and protocol: [corrected dynamic
capacity pilot](../experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md),
[DCS-LA contextual selection](../experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md),
[META-VOC confirmatory results](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md),
and the [META-VOC scientific record](../paper/META_VOC_SCIENTIFIC_RECORD.md).

## Paired comparisons available now

1. **Independent answer comparison:** for the same 160 queries, compare
   `F(x)` and `D(x)` as independently generated option letters, correctness,
   probability vectors, confidence, and measured latency. Per-query
   correctness overlap can identify fast-only successes, deep-only successes,
   both-correct, and both-wrong cases. This measures diversity/complementarity
   of independent outputs, not review.
2. **Recorded cascade replay:** compare FAST-only, DEEP-only, and the existing
   confidence-triggered FAST→DEEP policy on identical query IDs, charging the
   FAST call and every activated DEEP call. This is the outcome of selecting
   an independent answer from a second call on the original query. Thresholds
   were selected in the documented validation procedure; this is not a new
   inference or a test-time selection rule.
3. **Contextual-policy comparisons:** DCS-LA, fixed global, fixed-by-task, and
   retrospective oracle outcomes are query-paired with the model score file.
   A read-only join verified exact equality of the 160 query-ID sets and zero
   mismatches between the three model correctness columns and the score rows.
   DCS selection cost can be reported separately from inference latency.
4. **META-VOC policy comparisons:** policy outcomes can be paired by synthetic
   history and exogenous stream. At the decision level the trajectories
   record the policy's state, belief, route, action and outcome. Because
   policies can induce different actions, beliefs and visited states, later
   records are not identical-state paired interventions. These results
   concern allocation of computation in the synthetic planning model, not
   answer review.

## Comparisons unavailable from these artifacts

For a fixed query `x`, the existing MMLU score file contains independent
`F(x)` and `D(x)`. It does not contain `D(x,F(x))`: no second-pass input that
includes `F(x)`, no reviewer prompt/context, no revised answer, and no paired
record linking such a review to the independent outcomes. The confidence or
probabilities in the file are model scores over answer options from the
original query; they are not probabilities for a revised answer after review.

Consequently, the data cannot establish whether showing FAST's answer to DEEP
causes DEEP to correct an error, preserve a correct answer, or introduce an
error; cannot measure the latency/resource cost of that review call; and cannot
compare review against independent escalation at equal total cost. META-VOC's
`DEEP` is a Q11 state/belief lookahead operator and does not provide this missing
language-model counterfactual.

## Minimum additional data needed for an answer-conditioned comparison

No new infrastructure is implied. A future authorized evaluation would need,
for the same held-out query IDs:

- the exact query and answer choices (or a verified mapping from the stored
  hash ID to the pinned source row);
- the frozen first response `F(x)` and a record that this exact response was
  included in the second-stage input;
- the actual conditional reviewer output `D(x,F(x))`, its scored outcome, and
  any available reviewer probabilities;
- the independent `D(x)` baseline already present, to separate the effect of
  conditioning from simply calling the second model;
- per-call latency and resource/cost measurements, prompt/configuration and
  model revision, plus query-level provenance and a predeclared scoring rule.

If the question is policy value rather than the effect of conditioning alone,
the evaluation must additionally record the observable trigger and all calls
charged under each policy. Existing selection costs and independent latencies
can inform baselines, but do not substitute for measuring the review call.

## Conclusion for HLS-CE-01

The existing artifacts are sufficient to characterize independent capability
profiles, paired errors, confidence signals, contextual selection, and the
previously evaluated independent-answer cascade. They are insufficient to
measure answer-conditioned sequential deliberation. In notation, the available
records support paired observations of `F(x)` and `D(x)`; the conditional
potential outcome `D(x,F(x))` is absent. Any claim about the incremental value
of *reviewing the first answer* therefore requires additional, paired
conditional-review data. This assessment authorizes no such inference or
campaign.

The query-paired FAST/DEEP correction and interference rates, confidence-signal
analysis, and retrospective best-of-pair bound are reported separately in
[HLS-CE-01 complementarity analysis](HLS_CE_01_COMPLEMENTARITY_ANALYSIS.md).
