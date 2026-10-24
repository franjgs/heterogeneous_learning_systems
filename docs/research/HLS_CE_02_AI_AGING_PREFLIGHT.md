# HLS-CE-02 — AI Aging Refutatory Pilot: Preflight and Blocker

**Record date:** 2026-10-24
**Status:** **PARTIAL — synthetic control BLOCKED; no pilot implementation or model inference**
**Branch reviewed:** `feature/hls-laboratory-v1`
**Reviewed HEAD:** `5d307bb0423c40a6e58a1f013eb73e687f8ba2f0`

## 1. Scope and decision

This is a bounded preflight for the CE-02 request to test whether collective
error risk can change when the dependence structure of individual classifier
errors changes while marginal error rates stay fixed. The task requested exact
reproduction of two distributions specified by E2. The repository does not
contain that specification. The synthetic-control phase is therefore
**BLOCKED** under the instruction not to reconstruct or invent the
distributions. No replacement distribution was created, and the existing
expert-complementarity pilot was not relabeled as the E2 control.

The independent Wild-Time metadata audit identifies Yearbook as a possible
descriptive temporal benchmark for paired model errors, subject to resolving
the data-version/count discrepancy and creating stable example identifiers.
Wild-Time does not by itself identify a causal effect of dependence holding
marginal error rates constant. It can support a future observational analysis
of temporal changes in marginal and joint error behavior. No data were
downloaded, no model was run, and no inference campaign was performed.

Because the exact synthetic contract is missing and the real-data contrast is
not a substitute for it, no experiment-analysis package or general-purpose
infrastructure was added. Doing so before the estimands, data schema, and
distribution contract are available would risk encoding an unapproved
analysis. The implementation acceptance criterion is not met.

## 2. Repository inspection and exact missing input

The worktree was clean at the reviewed branch and commit. Targeted searches
covered tracked research/experiment documentation, source, experiment
scripts, and tests for AI-aging/Wild-Time specifications and joint error
probabilities. No E2 specification for the two requested distributions was
found.

The repository does contain a different, completed exact classifier
complementarity exercise:

- `experiments/validate_hls_expert_complementarity_math.py`
- `tests/test_hls_expert_complementarity_math.py`
- `results/experiments/hls_expert_complementarity_math_validation/results.json`

That exercise has **three** experts, task-specific accuracy vectors, and a
mixture between independent errors and a shared-uniform coupling. Its `rho`
is a mixture weight, not a pairwise correlation. It was built for exact
Kittler-sum fusion and coalition comparisons. Its distributions are not
identified in the repo as E2's AI-aging distributions, use a different task
and aggregation question, and cannot safely be substituted for the requested
two-classifier aging control.

To unblock the exact control, E2 must supply or identify a source containing,
for each of the two distributions: classifier count; complete probability
mass over every error pattern (or a fully specified generative law); the
bit-to-error convention; exact marginal rates; intended dependency
intervention/parameter values; and predicted pairwise and collective-risk
quantities. A pairwise correlation target alone is insufficient to specify a
joint distribution when higher-order dependence can vary.

## 3. Wild-Time preflight

### 3.1 Candidate task and labels

The best candidate identified is **Yearbook**: binary classification of the
dataset's recorded male/female label from a 32×32 grayscale portrait. This is
a classification task with a chronological year field and common test
examples on which multiple frozen checkpoints could be evaluated. The label
is the benchmark's binary annotation; it should not be described as a
validated measure of a person's gender identity or as a general face-analysis
capability.

The Wild-Time appendix specifies Eval-Fix as 1930–1970 ID and 1971–2013 OOD,
with years as timestamps. Its table reports five-year bin totals of 14,901
ID-train, 1,677 ID-test, and 21,439 OOD-test examples. The Wild-Time project
page separately reports 33,431 examples for 1930–2013. The appendix table
totals sum to 38,017, not 33,431. This is a material source/version
discrepancy; exact annual counts and the actual downloadable release must be
verified before freezing a protocol. The appendix reports counts in
five-year bins, not a full per-year count manifest.

### 3.2 Partitions, identifiers, and alignment

The official Eval-Fix chronological boundary is explicit and suitable as a
starting point. A future development/confirmation boundary within OOD must be
fixed by chronology before inspecting model outcomes—for example, divide the
official OOD years at a predeclared calendar-year midpoint, with earlier OOD
years used only for development and later OOD years held confirmatory. This
is a proposed protocol rule, not an executed or registered split.

The public Yearbook preprocessing source groups examples by year and stores
image arrays and labels in a pickle, but the shown preprocessing does not
retain portrait filenames or another stable per-example identifier. Raw
filenames could potentially be used to construct a manifest, but this has not
been verified against the distributed release or checkpoint evaluation
order. Therefore, paired alignment across independently generated prediction
files is **not yet established**. A future pipeline must build and hash an
explicit `(year, portrait_id)` manifest and reject duplicate, missing, or
misaligned IDs; positional joins alone are not adequate evidence.

### 3.3 Access, license, models, and hardware

The official Wild-Time repository states MIT licensing for its code and
Yearbook data. The Wild-Time supplement attributes MIT to the underlying
Portraits data. No dataset was downloaded in this preflight, so practical
download accessibility, archive checksum, and current release integrity have
not been verified. The repository advertises Eval-Fix baseline checkpoints
through a Google Drive folder; the individual checkpoint inventory, hashes,
availability, and license terms were not independently verified.

The repository lists Yearbook ERM, CORAL, GroupDRO, IRM, LISA, Mixup, A-GEM,
EWC, fine-tuning, SI, SimCLR, SwaV, and SWA configurations. The Yearbook
network is a small four-block convolutional network with a two-class
classifier; these methods are not necessarily distinct architectures or
independent capability families. The published appendix says experiments
were averaged over three seeds, used cross-validation/grid search, and ran on
a GPU cluster with six GPU nodes. The official package asks users to install
PyTorch >1.7.1 and its code selects a GPU device; a smaller compatible setup
may be feasible but was not benchmarked. No latency, memory, or inference-cost
estimate is claimed here.

For scale only, if the appendix's 21,439 OOD-test total is correct, one
forward pass over three frozen checkpoints would require 64,317
example–model evaluations (21,439 × 3); four checkpoints would require
85,756. These are arithmetic workload projections, not verified dataset
sizes, runtime estimates, or monetary costs. The conflicting published count,
unknown checkpoint inventory, and unmeasured hardware throughput prevent a
defensible wall-time or compute-cost estimate.

### 3.4 What the benchmark can and cannot answer

With stable IDs, frozen models, common examples, and predictions, Yearbook
could support per-year paired estimates of:

- Each model's error rate.
- Pairwise joint-error probabilities, covariance, and correlations when
  defined.
- The complete error-pattern distribution for a fixed small model set.
- Majority-vote risk and its paired temporal change.
- Per-year and pooled paired model comparisons.

These would be **observational temporal results**. Changes in error
dependence could coincide with changes in individual error rates, class
prevalence, image composition, or other distribution properties. The
benchmark therefore cannot establish that dependence changes caused
collective degradation while marginal risks remained constant. Exact
marginal-preserving causal claims require the missing controlled synthetic
distributions/intervention or a separately justified identification design.
No confirmatory years can be selected based on observed performance.

## 4. Implementation and validation status

No code or test was added or run. In particular, there is no implementation
of the E2 distributions, marginal-preserving intervention, dependence
statistics, TOST, bootstrap, prediction-record schema, or temporal split
guard. Their unit tests cannot honestly be marked passed. No dataset or
checkpoint was downloaded; no model inference was performed. Historical
campaign artifacts were not changed.

`git diff --check` is to be run on the documentary changes before publication.

## 5. Scientific conclusion and next prerequisite

**Phase 1: BLOCKED. Phase 2: bounded preflight complete, with a conditional
Yearbook candidate. Phases 3–5: not implemented/executed. Overall: PARTIAL.**

The blocker is specific and resolvable: the exact E2 distributions and
intervention contract must be supplied or located. Until then, the required
synthetic validation, comparison of exact risks, and tests of marginal
preservation cannot be performed faithfully. Wild-Time may later add
descriptive ecological evidence, but it is not a substitute for the
marginal-controlled contrast. Recommendation: **REVISE / HOLD** the pilot
implementation pending E2's specification; do not start real inference.

## 6. Sources

Repository references:

- Existing, distinct complementarity model: `experiments/validate_hls_expert_complementarity_math.py`.
- Existing tests for that model: `tests/test_hls_expert_complementarity_math.py`.
- Existing result artifact: `results/experiments/hls_expert_complementarity_math_validation/results.json`.

Primary Wild-Time sources:

- Yao et al., *Wild-Time: A Benchmark of in-the-Wild Distribution Shift over Time*, NeurIPS 2022, [paper/project page](https://papers.nips.cc/paper/2022/hash/43119db5d59f07cc08fca7ba6820179a-Abstract-Datasets_and_Benchmarks.html).
- Official [Wild-Time repository and README](https://github.com/huaxiuyao/Wild-Time), including installation, data access, Eval-Fix/Eval-Stream, checkpoint and license statements.
- Official [paper appendix](https://proceedings.neurips.cc/paper_files/paper/2022/file/43119db5d59f07cc08fca7ba6820179a-Supplemental-Datasets_and_Benchmarks.pdf), especially §A.1 and Table 1 for Yearbook, §C for experimental details, and §D for dataset licensing.
- Official implementation files inspected: [`yearbook.py`](https://github.com/huaxiuyao/Wild-Time/blob/main/wildtime/data/yearbook.py), [`configs_yearbook.py`](https://github.com/huaxiuyao/Wild-Time/blob/main/wildtime/configs/eval_fix/configs_yearbook.py), and [`yearbook.py` network](https://github.com/huaxiuyao/Wild-Time/blob/main/wildtime/networks/yearbook.py).

The appendix/page count discrepancy and the checkpoint contents remain open
verification items; neither is resolved by this documentary review.
