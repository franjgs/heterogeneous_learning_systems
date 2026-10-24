# HLS-CE-01 — Dynamic Organization of Fast and Deliberative Capabilities

**Document status:** feasibility-planning mission; not an experimental protocol or campaign authorization.
**Strategic proposal date:** 24 October 2026.
**Document record date:** 24 October 2026. The Git commit date records publication, not the date of the PI proposal or CE interpretation.

## A. Context and status of the proposal

On 24 October 2026, the PI proposed this order of strategic priorities:

1. Dynamic organization of fast and deliberative capabilities.
2. Selective cooperation among heterogeneous capabilities.
3. Organizational learning and emergent specialization.

The stated objective is to assess a first publishable scientific contribution within twelve months, with moderate compute, by investigating a concrete problem rather than requiring a universal theory first. These priorities are a **proposal pending PI ratification**. The CE considers the direction suitable for a feasibility assessment. This mission does not redefine HLS, replace the existing laboratory plan, authorize an experiment, or approve an algorithm or manuscript.

## B. Research question

**When does activating additional deliberative capability add value compared with accepting a fast decision?**

The problem must be specified in terms of the task/system, the fast and deliberative capabilities, information available at each decision, feasible actions, resource and latency constraints, and the collective objective. Those details are to be resolved in the feasibility assessment, not assumed here.

## C. Initial hypothesis — untested

The incremental value of deliberation may differ substantially from what confidence, estimated difficulty, or individual capability performance predicts. This is a working hypothesis only. It is neither established nor claimed as original.

## D. Prior work to compare

The assessment must locate the closest formulations and state what each actually solves, including assumptions, information, objectives, costs and baselines:

- model/query routing;
- cascades and sequential classification;
- value of computation;
- metareasoning;
- adaptive computation;
- decision-focused learning;
- budgeted allocation.

Names or superficial similarity are not evidence of equivalence or novelty.

## E. Bounded HLS evidence to reuse

The following studies are closed or scoped evidence. Reuse their data, conclusions and limits without reopening campaigns or recasting them as proof of originality:

- [Campaign 3 / META-VOC confirmatory results](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md) and [META-VOC scientific record](../paper/META_VOC_SCIENTIFIC_RECORD.md).
- [Consolidated budgeted routing report](../experiments/HLS_BUDGETED_LLM_ROUTING_CONSOLIDATED_REPORT.md).
- [Corrected dynamic-capacity MMLU pilot](../experiments/HLS_DYNAMIC_CAPACITY_ORGANIZATION_CORRECTED.md) and its initial pilot, preserved separately.
- [Contextual capacity selection / DCS-LA](../experiments/HLS_CONTEXTUAL_CAPACITY_SELECTION.md).
- [Current scientific state](../HLS_CURRENT_STATE.md), including evidence on partial information, S3b and collective decisions.

These results motivate questions about incremental benefit, signal quality, costs and collective allocation. They do not establish that deliberation is novel or generally beneficial.

The repository-data check is recorded in [HLS-CE-01 existing-data assessment](HLS_CE_01_EXISTING_DATA_ASSESSMENT.md). Existing MMLU artifacts permit paired analysis of independent `F(x)` and `D(x)` outputs and of the already evaluated independent-answer cascade, but contain no answer-conditioned `D(x,F(x))` response. META-VOC decision trajectories have different synthetic semantics and do not fill that data gap.

The follow-up [interaction-hypotheses assessment](HLS_CE_01_INTERACTION_HYPOTHESES.md) distinguishes candidate-answer correction, anchoring, and information transfer. It prioritizes information transfer as a potentially broader HLS question while recommending **REVISE** before any publication-level claim, given close prior work on answer visibility, self-revision, and multi-agent debate. The four-arm design is a proposal only; no inference or campaign is authorized.

## F. Minimum experiment concept — design only

The feasibility work may specify a comparison of fast and deliberative capabilities on common problems. The design should measure:

- initial output quality and quality after deliberation;
- realized incremental benefit of deliberation;
- compute/resource cost and latency, including all activations;
- predictive value of observable decision signals;
- collective performance at matched budgets.

It should compare static and strong adaptive policies under matched information, actions and costs. Retrospective oracles must be labelled as non-deployable bounds and separated from policies using information available at decision time. Data, task population, capability pair, signal definitions and inference protocol remain to be justified. **No execution is authorized by this document.**

## G. Viability decision criteria

- **GO:** the review identifies a concrete, falsifiable question not already resolved by the closest literature; a feasible, fair comparison can isolate the proposed decision value; and available or reasonably obtainable data support a reproducible test within the stated time and compute limits.
- **REVISE:** the question is relevant but a specific gap in formulation, evidence, comparator strength or measurement can be repaired without expanding scope materially.
- **NO-GO:** the claimed effect is already covered, cannot be separated from information/cost advantages, depends on unavailable evidence, or offers no defensible contribution within the constraints.

The 30 October intermediate report is a feasibility decision, not permission to execute a campaign.

## H. Scientific and reproducibility risks

- Prior work may already cover the proposed trigger or sequential allocation rule.
- Confidence or difficulty may not measure counterfactual benefit from deliberation.
- Capability comparisons can be confounded by model, prompt, hardware, generation and measurement differences.
- Latency, compute, memory and monetary cost are distinct quantities.
- A retrospectively selected trigger, budget or task population would bias conclusions.
- Historical HLS studies are bounded and do not by themselves demonstrate external validity.
- Small or reused test sets may not support the uncertainty claims needed for publication.

The assessment should preserve provenance and distinguish proposed claims, derived results and experimental observations.

## I. Deliverables and responsibilities

The mission deliverable is a concise feasibility report: problem definition, falsifiable hypothesis, HLS evidence map, prior-art comparison, minimal experiment design, strong comparators, metrics, stopping criteria, risks, and GO / REVISE / NO-GO recommendation.

The CE leads and integrates the scientific assessment. Codex provides technical/documentary support and verifies repository evidence under CE instructions. Strategic ratification remains with the PI. This document does not assign personal tasks to E1, E2 or E3 or imply their formal acceptance of roles.

## Proposed work schedule

The following October dates are mission-planning targets, not replacements for the original laboratory calendar:

| Date | Proposed work |
|---|---|
| 26 Oct | Delimit the scientific problem, falsifiable hypothesis, and reusable HLS results. |
| 27 Oct | Compare relevant routing, cascades, metareasoning, and adaptive-deliberation prior work. |
| 28 Oct | Characterize incremental deliberation value, predictive signals, uncertainty, and costs. |
| 29 Oct | Specify a decisive minimum experiment, strong comparators, controls, metrics, data, and stopping criteria. Design only; no execution. |
| 30 Oct | Deliver an interim feasibility report and GO / REVISE / NO-GO recommendation. |
| 2–6 Nov | **Proposed, not ratified:** resolve only concrete remaining uncertainties and prepare the final HLS-CE-01 report for the PI. |
| 9–13 Nov | **Optional proposal, not ratified:** extend only for a specific justified check still outstanding. |
