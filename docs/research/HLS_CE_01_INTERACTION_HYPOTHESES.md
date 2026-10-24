# HLS-CE-01 — Interaction hypotheses between heterogeneous capabilities

**Status:** focused conceptual assessment and experiment proposal only. No
inference, model execution, campaign, or algorithm development was performed.
This note does not authorize an experiment or make a novelty claim.

## 1. Question and distinctions

The narrow question is whether communication from a fast capability changes a
deliberative capability's decision, and whether any change comes from a
candidate answer, harmful anchoring, or additional decision-relevant
information. Let `x` be the original task, `F(x)` the frozen FAST output, and
`J_F(x)` a separately recorded justification/evidence packet from FAST.

- `D(x)`: DEEP solves the original task independently, without seeing FAST's
  answer or message.
- `D(x,F(x))`: DEEP receives the original task and FAST's answer as a proposed
  answer to inspect. It is answer-conditioned review; it is not the same
  treatment as solving `x` independently.
- `D(x,F(x),J_F(x))`: DEEP receives both the proposed answer and FAST's
  justification/evidence.
- To isolate the contribution of the justification, the experiment also needs
  `D(x,J_F(x))`: DEEP receives the justification/evidence with the answer
  string withheld. This fourth arm is a control, not a new target mechanism.

The existing MMLU records contain independent option answers and confidence,
not `J_F(x)` or conditional review. Their paired error results are summarized
in the [existing-data assessment](HLS_CE_01_EXISTING_DATA_ASSESSMENT.md) and
[complementarity analysis](HLS_CE_01_COMPLEMENTARITY_ANALYSIS.md). They cannot
test the hypotheses below.

## 2. Candidate mechanisms and falsifiable hypotheses

### A. Verification and correction

**Mechanism.** FAST supplies a candidate answer that DEEP can independently
check, accept, or reject. The candidate may focus DEEP's inspection, but may
also distract it.

**Hypothesis A.** Relative to `D(x)`, showing the actual FAST candidate in
`D(x,F(x))` increases the rate of correct final answers on a preregistered
query population, with a positive rate of wrong-to-correct transitions and
without an offsetting increase in correct-to-wrong transitions. Analyze these
transitions separately when FAST is correct and when it is wrong; gold labels
are used only after generation, never as review-time input.

**Observables.** Final correctness and answer, whether DEEP changes or adopts
FAST's answer, confidence before/after where elicitable, token/compute cost,
and latency. The main estimand is the paired accuracy difference between
randomized answer-visible and answer-hidden DEEP conditions; transition rates
are diagnostic outcomes.

**Alternatives.** Prompt repetition, extra tokens, answer-option priming,
stochastic variation, source attribution, difficulty differences, or a
generic benefit of being asked to verify may explain a change. The design must
hold wording and budget constant and include a neutral/hidden-answer control.

**Prior art.** Self-refinement and feedback-based correction are established
lines. The literature distinguishes finding an error from correcting one
once its location is known. The 2026 risk-aware intrinsic-revision study
reports both recoveries and harmful flips and compares keep/revise/gated
policies. Those results make aggregate accuracy alone insufficient and make
the simple claim “a second pass can correct errors” non-original.

### B. Anchoring or inappropriate adherence

**Mechanism.** The visible FAST answer may bias DEEP toward that answer even
when it is wrong, or change confidence without adding reliable evidence. This
must be distinguished from rationally following a reliable candidate.

**Hypothesis B.** On queries where the frozen FAST answer is wrong, randomized
exposure to that answer increases DEEP's probability of adopting the wrong
FAST answer, or lowers final accuracy, relative to the answer-hidden condition.
The direction and magnitude may differ when FAST is correct. This is an
operational hypothesis about erroneous influence, not a claim that every
answer-following event is irrational.

**Observables.** Adoption of FAST's option, final correctness, answer-change
rate, confidence update, and effects conditional on FAST's independently
scored correctness. The key comparison is the randomized effect of showing
versus hiding the same frozen FAST response, not a raw correlation between
FAST correctness and DEEP output.

**Alternatives.** A correct Bayesian response to a reliable peer, source-label
effects, model-family familiarity, answer copying, instruction differences,
or prompt-position effects. Attribute FAST consistently as a distinct peer
capability; if source trust is itself a target, it needs a separate randomized
factor.

**Prior art.** A 2026 *Nature Machine Intelligence* study directly manipulates
visibility of an initial answer and advice conditions, finding choice-supportive
bias and asymmetric response to contrary advice. Its principal visibility
manipulation concerns the answering model's own initial answer; it also
examines advice from another model and source attribution. It is therefore
close prior art, while not automatically establishing the effect of a
heterogeneous FAST recommendation in every HLS task. A contribution cannot be
claimed merely by demonstrating answer visibility or answer adherence again.

### C. Complementary information transfer

**Mechanism.** FAST communicates a justification or evidence item that
contains task-relevant information DEEP does not exploit as effectively when
working from `x` alone. The answer label itself is not evidence that the
justification contributes information.

**Hypothesis C — priority.** At matched DEEP inference budget, providing a
predefined, independently auditable FAST evidence/justification packet
increases decision quality relative to `D(x)`. Its marginal benefit remains
positive when the answer label is withheld (`D(x,J_F(x))`) or yields a
measurable answer-by-evidence interaction when supplied with the candidate
(`D(x,F(x),J_F(x))`). The effect should vary with the packet's verified
relevance/reliability and the receiving capability's baseline uncertainty.

**Observables.** Final task utility/correctness, which evidence claims DEEP
uses, whether the final answer is supported by the evidence, evidence
reliability, answer adoption/change, confidence, total tokens, latency, and
communication/inference cost. The evidence packet must be independently
scorable and must not contain the gold answer as a label.

**Alternatives.** Longer prompts, answer leakage through the rationale,
unverified or hallucinated claims, generic chain-of-thought prompting, extra
inference budget, or a prompt-format effect. Use a fixed template, matched
token/compute budgets, an answer-redacted evidence-only arm, and an independent
evidence-quality audit. `J_F` should represent information with traceable
content, not merely an unverified explanation.

**Prior art.** Multi-agent debate already studies proposal, critique, and
exchange among model instances; feedback/refinement work studies how feedback
changes outputs. These establish that interaction can help in some settings,
not that a FAST-generated evidence packet adds information beyond a strong
independent DEEP solve, nor that such benefit generalizes across capability
profiles and organizational constraints. The latter is the candidate gap to
test against closest work, not an originality claim.

## 3. Which phenomenon could support a generalizable HLS contribution?

**C is the strongest candidate, conditionally.** A generalizable result would
characterize the marginal decision value of information communicated by one
heterogeneous capability to another, after separating answer suggestion,
evidence content, reliability, receiver capability, and communication/compute
cost. The target would be a conditional relation or boundary—when shared
information improves collective decisions, when it is redundant, and when it
causes harm—not simply a higher accuracy number on one benchmark.

A and B are important mechanisms and necessary controls, but their broad
claims are already close to published work on self-correction, harmful
revision, answer visibility, and advice integration. C is also adjacent to
multi-agent debate and value-of-information research. It is therefore only a
potentially differentiating question; a focused prior-art comparison must
establish whether the proposed decomposition and conditions are already
covered. No novelty is established here.

## 4. One minimal experiment to distinguish A, B, and C

Use one fresh held-out query set with objectively scored outcomes and
independently auditable evidence. Do not reuse the 160-question MMLU test for
policy selection or claim confirmation. Freeze one FAST/DEEP pair, prompts,
decoding, and cost accounting before evaluation. Generate and freeze
`F(x), J_F(x)` once per query. Randomize condition order and, where sampling
is stochastic, use matched repetitions/seed blocks. DEEP must not receive gold
labels. Give all arms the same original `x`, DEEP token/compute budget, and
response format; use matched placeholders/templates so prompt length alone
does not define treatment. Run all four arms as a blocked within-query
comparison, randomizing arm order per query/replicate and preventing one arm's
output from entering another arm's context. Stratify diagnostic results by
whether frozen FAST was correct, with this status computed only after scoring.
Charge the FAST message-generation and communication costs to every arm that
uses `F` or `J_F`; do not treat precomputation as free.

| Arm | DEEP input | Identifies |
|---|---|---|
| 0 | `x` | Independent baseline `D(x)` |
| 1 | `x + F(x)` | Answer-exposure effect: `D(x,F(x)) − D(x)`; correction and erroneous adherence are separated by frozen FAST correctness and outcome transitions |
| 2 | `x + J_F(x)` with the answer withheld | Evidence/justification effect without the proposed answer |
| 3 | `x + F(x) + J_F(x)` | Combined effect and answer–evidence interaction |

Predefine three contrasts on query-paired outcomes: (i) Arm 1 versus 0 for
recovery and harmful-flip rates, reported separately; (ii) erroneous adoption
of FAST's answer in Arm 1 versus 0 on the subset where FAST is wrong, as the
anchoring diagnostic; and (iii) Arm 2 versus 0 plus the factorial interaction
`(Arm 3 − Arm 1) − (Arm 2 − Arm 0)` for evidence contribution/synergy. Report
accuracy or task utility and all-in inference/communication cost. Estimate
uncertainty by query-level paired intervals; do not count repeated generations
as independent queries. Any policy-level value claim additionally requires
comparison at matched total cost with strong static and adaptive baselines.

This is one controlled interaction experiment, not a campaign authorization.
The archived HLS test artifacts lack `J_F`, query prompts for replay, and all
conditional outputs, so they cannot implement these arms. A suitable fresh
dataset and sample-size/power plan remain design prerequisites. A one-pair
pilot can distinguish mechanisms in that setting; a generalizable publication
would need a preregistered replication across multiple task and capability
profiles, not extrapolation from one model pair.

## 5. Recommendation

**REVISE.** Prioritize C as the scientific question, with A and B as
mechanistic contrasts. Do not frame correction, answer visibility, or generic
debate as the contribution. The published 2026 answer-visibility study and
revision-risk literature make those standalone claims insufficiently
differentiated. The proposed factorial experiment can distinguish the three
mechanisms, but a publication-level **GO** requires a closer comparison with
multi-agent information exchange and decision-focused value-of-information
work, plus a defensible operational definition of FAST's independently
auditable information. This note authorizes neither inference nor experiment.

## 6. Verified antecedents

- Kumaran, D. et al. (2026). “Competing Biases underlie Overconfidence and
  Underconfidence in LLMs.” *Nature Machine Intelligence* 8, 614–627.
  [DOI: 10.1038/s42256-026-01217-9](https://doi.org/10.1038/s42256-026-01217-9).
  Manipulates answer visibility/advice and studies answer changes, confidence,
  and advice accuracy; close prior art for B.
- Zhang, T. (2026). “When Should LLMs Trust Their Own Revisions? A Risk-Aware
  Study of Intrinsic Self-Correction.” [arXiv:2609.35832](https://arxiv.org/abs/2609.35832).
  Preprint; evaluates correctness transitions and keep/revise/gating choices
  for same-model revision without external evidence; close prior art for A and
  revision-risk accounting, but not heterogeneous peer information transfer.
- Madaan, A. et al. (2023). “Self-Refine: Iterative Refinement with
  Self-Feedback.” *NeurIPS 36*.
  [Proceedings paper](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html).
  Same-model iterative feedback/refinement.
- Tyen, G. et al. (2024). “LLMs cannot find reasoning errors, but can correct
  them given the error location.” *Findings of ACL 2024*, 13894–13908.
  [DOI: 10.18653/v1/2024.findings-acl.826](https://doi.org/10.18653/v1/2024.findings-acl.826).
  Separates error detection from correction with supplied error location.
- Du, Y. et al. (2024). “Improving Factuality and Reasoning in Language Models
  through Multiagent Debate.” *ICML 2024*.
  [Paper and code](https://composable-models.github.io/llm_debate/).
  Multiple instances propose, critique, and debate; adjacent prior art for C.
- Kamoi, R. et al. (2024). “When Can LLMs Actually Correct Their Own
  Mistakes? A Critical Survey of Self-Correction of LLMs.” *TACL* 12,
  1417–1440. [DOI: 10.1162/tacl_a_00713](https://doi.org/10.1162/tacl_a_00713).
  Critical review of feedback conditions and evaluation limitations.

These references are a focused, non-exhaustive check, not a complete
originality audit.
