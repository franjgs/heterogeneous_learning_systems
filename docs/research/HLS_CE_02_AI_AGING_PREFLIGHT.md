# HLS-CE-02 — AI Aging Refutatory Pilot: Exact Control and Yearbook Preflight

**Record date:** 2026-10-24
**Status:** **PARTIAL — exact synthetic control implemented; real-model inference blocked**
**Branch reviewed:** `feature/hls-laboratory-v1`
**Initial preflight HEAD:** `5d307bb0423c40a6e58a1f013eb73e687f8ba2f0`
**Initial integration HEAD:** `6fc68a9203e56e44991cb2ec44cf8e3afa5b9ded`
**Pre-existing CE governance commit on branch:** `10e74c080d44283bd5318ea59eb0d873a03a39a5`

## 1. Scope and decision

This bounded pilot tests whether collective majority-error risk can change
when the joint dependence structure changes while all individual error rates
remain fixed. The initial repository audit did not locate E2's distribution
parameters, so that audit correctly recorded a blocker. The subsequent CE
instruction supplied the exact two probability masses and authorized their
implementation. The control is now implemented with exact rational
arithmetic; no E2 source code was available or claimed to be integrated.

The Wild-Time Yearbook preflight now uses the publicly advertised processed
pickle, downloaded to temporary storage and inspected with a restricted
NumPy-only unpickler. It verified per-year record counts, labels, partition
alignment by image-content hash, and duplicate counts. The public baseline
checkpoint folder was also inspected and contains no Yearbook checkpoint.
Consequently no model inference was run. Yearbook could support observational
paired analyses of temporal errors but cannot alone identify a causal effect
of dependence while marginal risks remain fixed.

## 2. Repository inspection and exact missing input

The worktree was clean at initial integration inspection on
`feature/hls-laboratory-v1` at `6fc68a9`. The already-published follow-on
commit `10e74c0` formalized research governance and was preserved; this task's
changes are layered on top of it. The initial AI-aging preflight had been
recorded earlier at `5d307bb`. Targeted searches
covered tracked research/experiment documentation, source, experiment
scripts, and tests for AI-aging/Wild-Time specifications and joint error
probabilities. No E2 distribution source file or original implementation was
found. The exact probability masses were then supplied directly in the CE
task and implemented as specified below; no original E2 code was integrated.

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

The exact control uses three error bits `e1e2e3`, where 1 means error, and
the CE-supplied distributions:

- `P_A(000)=7/10`, `P_A(110)=P_A(101)=P_A(011)=1/10`, all other atoms zero.
- `P_B(000)=4/5`, `P_B(111)=1/5`, all other atoms zero.
- `P_lambda=(1-lambda)P_A + lambda P_B`, `lambda∈[0,1]`.

These endpoint distributions are exact and normalized. Each classifier has
error probability `1/5`. Every pair has joint-error probability `1/10` and
covariance `3/50` under A, versus `1/5` and `4/25` under B. Their
corresponding correlations are `3/8` and `1`. Majority-error risks are `3/10`
and `1/5`; under the declared interpolation, covariance is
`3/50 + lambda/10` and majority-error risk is `3/10 - lambda/10`. The exact
artifact and tests are linked below.

## 3. Wild-Time preflight

### 3.1 Candidate task and labels

The best candidate identified is **Yearbook**: binary classification of the
dataset's recorded male/female label from a 32×32 grayscale portrait. This is
a classification task with a chronological year field and common test
examples on which multiple frozen checkpoints could be evaluated. The label
is the benchmark's binary annotation; it should not be described as a
validated measure of a person's gender identity or as a general face-analysis
capability.

The downloaded official processed file contains 84 years (1930–2013),
37,189 full image records, and binary labels. The file is 1,828,532,864 bytes
(1.70 GiB) with SHA-256
`dc59f02d63c0ef6a5d0444f6237fe3bfed76ca82ab043b0235cf15388b04da6c`.
Using the official Eval-Fix `split_time=1970` and the inspected loader logic,
the actual split counts are: ID training mode 0, 14,901 examples for
1930–1970; ID test mode 1, 1,677 for 1930–1970; and OOD test mode 2, 20,611
for 1971–2013. They sum to 37,189.

The project page's 33,431 is the mode-0 count summed over **all** years, not
the number of all portraits. The appendix's stated OOD total 21,439 exceeds
the downloaded/code-defined OOD count by 828, exactly the 1970 record count;
the official code treats 1970 as the ID boundary and evaluates OOD only for
timestamps greater than 1970. The source materials therefore contain a
boundary/count inconsistency. The local counts below are from the downloaded
file and official implementation semantics, not from inference.

| Period | Full records | Mode 0 | Mode 1 | Eval-Fix ID train | Eval-Fix ID test | Eval-Fix OOD test |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1930–1934 | 1,171 | 1,051 | 120 | 1,051 | 120 | 0 |
| 1935–1939 | 1,515 | 1,361 | 154 | 1,361 | 154 | 0 |
| 1940–1944 | 2,277 | 2,047 | 230 | 2,047 | 230 | 0 |
| 1945–1949 | 2,201 | 1,979 | 222 | 1,979 | 222 | 0 |
| 1950–1954 | 1,785 | 1,604 | 181 | 1,604 | 181 | 0 |
| 1955–1959 | 2,025 | 1,820 | 205 | 1,820 | 205 | 0 |
| 1960–1964 | 1,649 | 1,482 | 167 | 1,482 | 167 | 0 |
| 1965–1969 | 3,127 | 2,812 | 315 | 2,812 | 315 | 0 |
| 1970–1974 | 2,586 | 2,326 | 260 | 745 | 83 | 1,758 |
| 1975–1979 | 2,590 | 2,329 | 261 | 0 | 0 | 2,590 |
| 1980–1984 | 2,952 | 2,654 | 298 | 0 | 0 | 2,952 |
| 1985–1989 | 2,490 | 2,239 | 251 | 0 | 0 | 2,490 |
| 1990–1994 | 2,456 | 2,207 | 249 | 0 | 0 | 2,456 |
| 1995–1999 | 2,851 | 2,564 | 287 | 0 | 0 | 2,851 |
| 2000–2004 | 2,721 | 2,447 | 274 | 0 | 0 | 2,721 |
| 2005–2009 | 1,566 | 1,407 | 159 | 0 | 0 | 1,566 |
| 2010–2013 | 1,227 | 1,102 | 125 | 0 | 0 | 1,227 |
| **Total** | **37,189** | **33,431** | **3,758** | **14,901** | **1,677** | **20,611** |

The 1970–1974 row is split internally at 1970: 1970 contributes 745 mode-0,
83 mode-1 ID examples; 1971–1974 contribute 1,758 OOD examples. Annual
counts were extracted from the actual pickle; the table groups them into the
benchmark's five-year reporting periods.

### 3.2 Partitions, identifiers, and alignment

The prospective chronological split is fixed before any model outputs:

- Official Eval-Fix ID: 1930–1970; this is model training/ID evaluation, not
  the confirmatory temporal contrast.
- Development: OOD years 1971–1994, 12,246 examples.
- Confirmation: OOD years 1995–2013, 8,365 examples.

This boundary is calendar-defined and outcomes were not inspected. The
confirmation labels/counts were inspected solely for dataset integrity; no
model predictions exist and no parameter or model selection used these
years. The split is now a proposed preflight protocol, not a registered
scientific analysis.

The distributed pickle stores year, images, and labels but not original
portrait filenames. A content-derived ID was therefore tested in memory as
SHA-256 of the normalized image-array bytes, scoped to the downloaded
dataset-version hash. All 37,189 full records had unique pixel hashes (zero
duplicate groups, zero duplicate excess rows, zero cross-year duplicates).
For every year, the mode-0 and mode-1 arrays formed a disjoint exact
image-and-label partition of mode 2. Thus content-hash IDs can align model
outputs reproducibly for this exact artifact, although they are not source
identifiers and may change if preprocessing changes. Hashes were not written
to the repository.

### 3.3 Access, license, models, and hardware

The official Wild-Time repository states MIT licensing for its code and
Yearbook data; the supplement attributes MIT to the underlying Portraits
data. The processed file was publicly downloadable from the official loader's
Google Drive ID. Its byte count and SHA-256 are recorded above. No dataset
was added to Git.

The public checkpoint folder linked by the official README was directly
listed on 2026-10-24: **50 compressed archives, zero Yearbook checkpoints**.
All listed files are FMoW checkpoints: 39 A-GEM (13 timestamps × 3 seeds),
3 DeepCORAL, 3 ERM-LISA, 3 ERM-Mixup, and 2 ERM. No Yearbook checkpoint was
available in that folder, and no checkpoint file was downloaded. Therefore
there is currently no compatible frozen model to produce a Yearbook
prediction-output correspondence without training, which is prohibited here.

Labels are stored as integers: the official preprocessing maps `M→0` and
`F→1`. The Yearbook network has a two-logit classifier; `base_trainer.py`
converts logits to class predictions via `softmax(...).argmax(dim=1)` and
compares them with labels. The semantic output mapping is therefore direct.
Actual model outputs, score files, and checkpoint-to-label alignment remain
unavailable because no Yearbook checkpoint exists in the advertised folder.

The repository lists Yearbook ERM, CORAL, GroupDRO, IRM, LISA, Mixup, A-GEM,
EWC, fine-tuning, SI, SimCLR, SwaV, and SWA configurations. The Yearbook
network is a small four-block convolutional network with a two-class
classifier; these methods are not necessarily distinct architectures or
independent capability families. The published appendix says experiments
were averaged over three seeds, used cross-validation/grid search, and ran on
a GPU cluster with six GPU nodes. The official package asks users to install
PyTorch >1.7.1 and its code selects a GPU device; a smaller compatible setup
may be feasible but was not benchmarked. No latency, memory, or inference-cost
estimate is claimed here. A forward pass of the official Yearbook network is
approximately 3,981,376 multiply-accumulates (MACs) per image, including its
32→2 classifier, and has 28,706 parameters. On the verified 20,611 OOD rows,
three model instances would require 61,833 image–model evaluations and about
246.18 billion MACs (492.35 GFLOPs if one MAC is counted as two FLOPs). The
preprocessed arrays occupy about 1.83 GB in serialized form; model weights
are about 115 kB each in FP32, excluding runtime/activation overhead. These
are architecture-based resource projections, not measured runtime.

Wall-clock inference time is **BLOCKED / not estimable**: no Yearbook
checkpoint is available in the advertised folder, no hardware/runtime target
was selected for this preflight, and no inference was run. The paper's six-GPU
cluster is a training setup and is not a defensible inference timing proxy.

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
No confirmatory years were selected based on model performance.

## 4. Exact control implementation and tests

Files added:

- `experiments/synthetic/ai_aging_control.py`: exact PMFs A/B, probability
  validation, `P_lambda`, marginal/joint risks, covariances/correlations,
  majority risk, and exact result serialization.
- `tests/test_hls_ce02_ai_aging_control.py`: 15 focused tests for
  normalization, non-negativity, all marginals, all pairwise quantities,
  majority risk, transition invariants/endpoints, and invalid inputs.
- `results/experiments/hls_ce02_ai_aging/synthetic_control.json`: generated
  exact result artifact.

Command executed:

```sh
PYTHONPATH=. pytest -q tests/test_hls_ce02_ai_aging_control.py
PYTHONPATH=. python experiments/synthetic/ai_aging_control.py
```

Result: **15 passed**. The artifact uses rational strings, so no rounding is
introduced. It labels the source as the exact probabilities in the CE task;
it does not claim integration of original E2 code. The control has no model
inference and is a mathematical falsification instrument, not evidence that
real systems exhibit AI aging.

The Yearbook file was downloaded only to `/tmp`, inspected with a restricted
unpickler allowing NumPy array constructors, counted and hashed in memory;
the temporary file was removed after the audit. No dataset or image-derived
identifier is stored in Git. No checkpoint/model was downloaded; no model was
trained or run. Historical campaign artifacts were unchanged.

`git diff --check` passed after the documentation and code changes.

## 5. Acceptance and scientific conclusion

| Requirement | Status | Evidence / limit |
| --- | --- | --- |
| Exact A/B distributions from CE-supplied E2 values | **PASS** | Exact PMFs in source and JSON; no original E2 code was available. |
| Marginals 0.20 | **PASS** | Each of three classifiers in A, B, and every tested `P_lambda`. |
| Covariances A=.06, B=.16 | **PASS** | Exact pairwise values for all three pairs. |
| Majority risks A=.30, B=.20 | **PASS** | Exact enumeration over all eight atoms. |
| `P_lambda` and dependence intervention | **PASS** | Linear mixture, exact marginal invariance and covariance/risk interpolation. |
| Tests for synthetic control | **PASS** | 15 focused tests passed. |
| Actual per-period Yearbook counts | **PASS** | Downloaded, hashed artifact: 84 annual slices, grouped above into five-year bins. |
| Stable IDs and duplicate audit | **PASS with scope** | Content hashes uniquely identify records in this exact version; 0 duplicates; source IDs absent. |
| Checkpoint availability for Yearbook | **BLOCKED** | Official public folder has 50 checkpoints, all FMoW; 0 Yearbook. |
| Label/output semantic mapping | **PASS (contract)** | `M→0`, `F→1`; network emits two logits; evaluator uses softmax/argmax. No actual predictions to check. |
| Development/confirmation separation | **PASS (predeclared)** | 1971–1994 development; 1995–2013 confirmation. No prediction-driven selection. |
| Inference resource estimate | **PARTIAL** | 61,833 forward evaluations / 246.18 GMAC for 3 model copies; not measured. |
| Wall-clock inference time | **BLOCKED** | No compatible checkpoint or measured hardware throughput; no inference run. |

**Overall: PARTIAL.** The exact synthetic control and its tests are complete.
The Yearbook data/partition/ID preflight is substantially complete, but a
model-based temporal analysis is blocked by the absence of compatible
checkpoints. The observational benchmark cannot replace the exact control or
support a causal claim that dependence alone changes collective risk.
Recommendation: **GO for the exact synthetic falsification control; HOLD
Wild-Time inference** until a compatible, legally usable Yearbook checkpoint
is identified without training or confirmatory-data selection.

## 6. Sources

Repository references:

- Existing, distinct complementarity model: `experiments/validate_hls_expert_complementarity_math.py`.
- Existing tests for that model: `tests/test_hls_expert_complementarity_math.py`.
- Existing result artifact: `results/experiments/hls_expert_complementarity_math_validation/results.json`.

Primary Wild-Time sources:

- Yao et al., *Wild-Time: A Benchmark of in-the-Wild Distribution Shift over Time*, NeurIPS 2022, [paper/project page](https://papers.nips.cc/paper/2022/hash/43119db5d59f07cc08fca7ba6820179a-Abstract-Datasets_and_Benchmarks.html).
- Official [Wild-Time repository and README](https://github.com/huaxiuyao/Wild-Time), including installation, data access, Eval-Fix/Eval-Stream, checkpoint and license statements.
- Official [paper appendix](https://proceedings.neurips.cc/paper_files/paper/2022/file/43119db5d59f07cc08fca7ba6820179a-Supplemental-Datasets_and_Benchmarks.pdf), especially §A.1 and Table 1 for Yearbook, §C for experimental details, and §D for dataset licensing.
- Official implementation files inspected at the pinned source revision: [`yearbook.py`](https://github.com/huaxiuyao/Wild-Time/blob/23b0696dc82479a0689d678f44328153a19527e1/wildtime/data/yearbook.py), [`base_trainer.py`](https://github.com/huaxiuyao/Wild-Time/blob/23b0696dc82479a0689d678f44328153a19527e1/wildtime/methods/base_trainer.py), [`configs_yearbook.py`](https://github.com/huaxiuyao/Wild-Time/blob/23b0696dc82479a0689d678f44328153a19527e1/wildtime/configs/eval_fix/configs_yearbook.py), and [`yearbook.py` network](https://github.com/huaxiuyao/Wild-Time/blob/23b0696dc82479a0689d678f44328153a19527e1/wildtime/networks/yearbook.py).
- Public data object inspected: [Yearbook processed pickle](https://drive.google.com/uc?export=download&id=1mPpxoX2y2oijOvW1ymiHEYd7oMu2vVRb). Public checkpoint folder linked from the README: [Google Drive folder](https://drive.google.com/drive/folders/1h_pvX4mhzVEddxenP-RkFl8yjKbl8FUN?usp=sharing). Both inspected 2026-10-24; only aggregate counts/hash results are retained here.
- The inspected Wild-Time `main` source revision was `23b0696dc82479a0689d678f44328153a19527e1` (upstream commit date 2022-12-18).

The Yearbook artifact and official implementation disagree with the published
OOD aggregate by the boundary-year count (828); this remains a documented
source inconsistency. Checkpoint absence and wall-clock latency remain
unresolved; they were not filled with assumptions.
