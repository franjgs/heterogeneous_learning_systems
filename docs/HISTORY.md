# HLS Scientific History

This is a compact record of the reasoning that matters for interpreting the
current programme. It is not a replacement for frozen protocols or result
artifacts, and it is not an exhaustive transcript of earlier documents.

## Chronology and date confidence

This file is the canonical chronology for significant project decisions and
milestones. For new entries, event time and documentation time are separate.
Times use Europe/Madrid and the form `YYYY-MM-DD HH:MM ±HH:MM`. A Git
timestamp verifies when a repository record was made; it does not by itself
date the decision that motivated it. Earlier narrative sections below remain
undated where the source material does not establish a defensible event date.

| Event / record | Event date and confidence | Record date and evidence | Scope note |
| --- | --- | --- | --- |
| HLS minimal theoretical model documented | **2026-10-16, documentation event; exact start time not recorded.** | Recorded 2026-10-16 09:56 +02:00 (Europe/Madrid), as stated by the system clock; [model](theory/HLS_MINIMAL_THEORETICAL_MODEL.md). | Domain-independent finite-horizon model and conditional derivations mapped to existing HLS. No code, simulator physics, campaigns, or historical results changed. It makes no novelty claim; multi-task scheduling, externally grounded objective units, and empirical relevance remain open. |
| Campaign 2 experimental sensitivity audit | **2026-10-16 09:07 +02:00, verified audit start; findings recorded 09:08 +02:00.** | Recorded 2026-10-16 09:08 +02:00 (Europe/Madrid); [audit](experiments/HLS_EXPERIMENTAL_SENSITIVITY_AUDIT.md), published Campaign 2 trace and output manifest. | Read-only code/artifact audit: ten noisy seeds produce ten logged observation/estimate paths but one true-competence path and one CES/success path per scenario/condition. P0 estimate perturbations mostly remain within broad score regions; C/MIS-OFF action changes are reward-equivalent. All eight source and six frozen output hashes matched; 16 focused tests passed. No simulator/result changes; known 13 full-suite provenance/integrity failures remain; milestone PARTIAL. |
| HLS Laboratory Campaign 2: directed teaching × MIS × productive assignment | **2026-10-15 20:38:57–20:39:04 +02:00, verified** by execution manifest; design registered at 20:37:57 +02:00 before outcomes. | Documented 2026-10-15 20:44 +02:00, Europe/Madrid; source base `1c902f180d37a12fd9806d0db427b0adf83a0029`; [scientific findings](experiments/HLS_CAMPAIGN2_FINDINGS.md). | CE-authorized experiment COMPLETE: 33 main plus one zero-efficacy quadruple, 136 runs/3,264 periods, common P0 continuation. CES interaction A −1.092473, B +1.561953, C +.339151; teaching opened 23/11 target exposures in B/C. Ten noisy seeds per scenario had identical CES despite varying estimates/selected equivalent actions. Conditional mechanism evidence, no causal mediation or population claim. 123 focused/regression tests passed; 13 historical provenance failures unresolved, laboratory milestone remains PARTIAL. |
| HLS Laboratory behavioral plausibility validation | **2026-10-15 17:42:56 +02:00, verified** by the final result manifest. | Recorded 2026-10-15 17:43 +02:00, Europe/Madrid, with test and artifact hashes. | Six deterministic paired intervention fixtures plus mechanism invariants; confirms conditional response only. No core physics changes; milestone remains PARTIAL. |
| Campaign 1 scientific knowledge consolidation | **2026-10-15 20:31 +02:00, documentation event time verified** by the system clock. | Recorded 2026-10-15 20:31 +02:00, Europe/Madrid; synthesis at [HLS_CAMPAIGN1_FINDINGS.md](experiments/HLS_CAMPAIGN1_FINDINGS.md). | Cross-checked published machine-readable outputs and hashes for the pilot, mechanism diagnostics, 64 counterfactual branches, and behavioral validation. Preserves limitations and separates an untested teaching × MIS hypothesis. No experiments run; HLS Laboratory remains PARTIAL. |
| PI / CE decision to prioritize integrated HLS Laboratory v1 and approve milestone `HLS-LAB-V1-INTEGRATED` | **2026-10-15, date verified; exact time unknown**, from the dated PI/CE instruction. | Documented 2026-10-15 08:40 +02:00, Europe/Madrid, in this entry and the linked current-state/lab documents. | Operational-priority change; it does not change the research questions or retrospectively alter prior decisions. |
| Scientific Campaign 1 pilot: exploitation versus capability development | **2026-10-15 10:22:04 +02:00, verified** by the final output manifest. | Recorded 2026-10-15 10:22 +02:00, Europe/Madrid; source baseline `a179041a1617e250e3fe83065db7dbc8402b0d62`. | 16 configurations × 10 paired seeds × four policies × LI ON/OFF = 1,280 runs, 20,480 episode records. Pilot observations only; no population-level inference. Three earlier designs were excluded: latent-label exposure, oracle skill initialization, and zero-production teaching periods from budget/action granularity. Formatting reruns reused the same seeds and did not add replicates. |
| Campaign 1 conditional counterfactual teaching-value diagnostic | **2026-10-15 15:34:12 +02:00, verified** by the derived-result manifest. | Recorded 2026-10-15 15:34 +02:00 (Europe/Madrid), from published pilot seed `2026101511`; outputs under `results/diagnostics/hls_campaign1_counterfactual_teaching_value/`. | 32 preselected states × two existing directed relations = 64 paired remaining-horizon interventions. Descriptive conditional results only; not a global teaching-policy value or population estimate. |
| Additive B1–B6 integrated teaching-cycle implementation and acceptance run | **2026-10-15, implementation date verified; exact start time unknown.** | Documented 2026-10-15 09:08 +02:00, Europe/Madrid, with implementation and test paths in the scope note. | Focused laboratory tests passed; full suite had 1181 passes and 13 failures on pre-existing local integrity/provenance conditions. Milestone remains PARTIAL; engineering verification is not scientific evidence. |
| Additive exogenous environment/problem trajectory interface and regression run | **2026-10-15, implementation date verified; exact start time unknown.** | Documented 2026-10-15 09:45 +02:00, Europe/Madrid. | Reuses C5 demand processes and dynamic-lab emission; 17 focused tests passed; full suite 1189 passed/13 failed, same 13 named failures as the prior run. Milestone remains PARTIAL. |
| HLS Laboratory v1 candidate-set consolidation and final validation | **2026-10-15 09:57 +02:00, verified execution time.** | Recorded 2026-10-15 09:57 +02:00, Europe/Madrid. | Ten scoped files imported and ran; focused tests 17/17; full suite 1189/13, same pre-existing failures. Milestone remains PARTIAL. |
| HLS Laboratory v1 minimum package published | **2026-10-15 09:58 +02:00, verified push/remote-ref check.** | Recorded 2026-10-15 09:58 +02:00, Europe/Madrid; commit `37a011804f9ea013fc3a5436c00a72eb0b8280da`. | Pushed to `origin/feature/hls-laboratory-v1`; remote ref matches commit. Publication does not close the milestone; 13 full-suite failures remain. |
| HLS Laboratory v1 vertical-slice implementation recorded | Decision/event date **unknown**; repository record timestamp verified. | 2026-10-14 10:32 +02:00; commit `624e249` (full hash in Git). | Commit date establishes when the implementation was recorded, not when CE-23 was authorized. |
| CE-24 validated output manifest created | **2026-10-14 10:50 +02:00, verified** by `created_utc` in `results/experiments/hls_lab_ce24_validated/manifest.json`; exact simulation start/end times are not recorded. | Manifest records `2026-10-14T08:50:09.236416+00:00`; result report was committed at 10:55 +02:00 (`ae78cda`). | Timestamp verifies the manifest/output record, not exact execution duration. The deterministic run is not population-level evidence. |
| CE-24 validation record committed | Decision/event date **unknown**; repository record timestamp verified. | 2026-10-14 10:55 +02:00; commit `ae78cda`. | Commit date records report/code publication in Git, not decision authorization. |
| CE-25 mechanism-decomposition experiment and report | **2026-10-14, approximate only**: the report identifies `ae78cda` as the source-code baseline and is recorded in the same-day `aeea566` commit; no run timestamp appears in its manifest. | Repository report commit 2026-10-14 11:20 +02:00 (`aeea566`); its manifest has no execution timestamp. | Do not infer an exact execution time. Finite deterministic mechanism validation; its FAST/DEEP next-step recommendation is superseded operationally by the 15 October decision, while findings remain historical. |
| C2/C3 results and C4 status documentation consolidation committed | Decision dates **not inferred from commit time**; repository record timestamp verified. | 2026-10-13 08:15 +02:00; commit `931c560`. | The status recorded there is preserved in its scoped sources; it is not the current HLS Laboratory v1 priority. |
| G1 static and G2 dynamic ground-truth consolidations | Original experiment/decision dates **unknown** from the reviewed chronology. | Repository records: G1 consolidation 2026-10-01 07:59 +02:00 (`f8897e7`); G2 validation 2026-10-01 10:57 +02:00 (`5c55a59`). | These are verified artifact-record dates, not dates of the original G1/G2 work or decisions. |
| G0/reference-scenario and G3/G3-H repository milestones | Original event/decision dates **unknown**; repository record timestamps verified. | Relevant records include minimal reference scenario 2026-10-01 18:45 +02:00 (`b4551b7`), G3 ground truth 2026-10-02 13:01 +02:00 (`a3f2a85`), G3-H future-opportunity closure 2026-10-04 22:16 +02:00 (`2eca948`), and C1/C2 boundary closure 2026-10-05 18:03 +02:00 (`8972c3c`). | These dates establish when Git recorded the artifacts, not the underlying decision dates. |
| Initial portfolio framing; H1/M0/CIV; vehicle search; transition to G0; A1; C1–C5/RQ0 narrative (sections 1–9 below) | **DATE UNKNOWN** for the events as described; no direct event timestamps were found in this history entry. | Individual source documents/commits exist, but their record dates are not asserted here as event dates. | Preserve the ordering and conclusions; do not invent dates or infer them from unrelated commit timestamps. |

Dates marked “unknown” are intentionally not reconstructed from commit time.
Dates for which only a bounded period is supported should remain approximate
in future entries rather than being assigned invented day/time precision.

### 2026-10-15 — operational priority change

**Event:** 2026-10-15, exact time not documented. **Recorded:** 2026-10-15
08:40 +02:00 (Europe/Madrid). **Authority:** PI / Chief Engineer. **Type:**
operational-priority decision. **Decision:** prioritize completing HLS
Laboratory v1 as integrated experimental infrastructure, under milestone
`HLS-LAB-V1-INTEGRATED`, status **APPROVED — IMPLEMENTATION PENDING**.

HLS's two research questions and general scientific doctrine are unchanged.
Infrastructure completion comes first; scientific investigations follow on a
causally coherent, reproducible, and verifiable integrated laboratory. The
approved implementation is one milestone with blocks B1–B6: joint actions and
shared resources; teaching transition; observations and elementary
organizational estimation; a minimal adaptive policy; integrated multiperiod
execution; and tests plus reproducible demonstration. Extensive campaigns and
component sophistication are deferred. See [current state](HLS_CURRENT_STATE.md)
and the [v1 implementation reference](experiments/HLS_LAB_V1.md).

**Operational consequence:** development stays focused on meeting the
HLS-LAB-V1-INTEGRATED acceptance criteria; no intermediate audit phases or new
status/roadmap documents are opened. The previous narrower next-step
recommendations (including CE-25's FAST/DEEP recommendation) are superseded as
the immediate priority, not erased or reinterpreted as historical findings.

### 2026-10-15 — integrated teaching-cycle implementation (partial)

**Event:** 2026-10-15, implementation performed during this work session;
exact start time not recorded. **Recorded:** 2026-10-15 09:08 +02:00
(Europe/Madrid). **Authority:** implementation under the PI/CE-approved
HLS-LAB-V1-INTEGRATED decision. **Type:** engineering implementation and
verification.

An additive execution layer, `src/hls/hls_lab_v1_integrated.py`, composes
existing DISCOVER-v0 production actions, MIS-v2 individual learning, existing
competence-posterior helpers, and a bounded directed teaching event. It adds
shared feasibility checks, private heterogeneous teaching efficacy, noisy
public observations, elementary efficacy memory, P0/P1/P2, multiperiod traces,
and deterministic coordinate-indexed innovations. The reproducible demo is
`experiments/synthetic/hls_lab_v1/integrated_demo.py`; focused tests are in
`tests/test_hls_lab_v1_integrated.py`.

The deterministic engineering fixture produced both outcomes: for recurrent
demand, P2 obtained cumulative CES 6.4564 versus P0 5.0728 (33 versus 2
successful periods); for short mismatched demand, P1 obtained 1.5763 versus
P0 2.1997 and P2 declined to teach, matching P0 at 2.1997. These are fixture
outputs, not scientific effect estimates. Focused tests across the integrated
layer and its CE-23/24/25, dynamic, DISCOVER, MIS-v2 and Small Problem World
dependencies passed (87). The complete suite reported 1181 passed, 13 failed;
the reported failures concern local frozen-source hashes, additional local
artifacts, and Campaign 2/B2.3/RQ0 provenance checks outside files changed for
this integration. No historical hashes or results were edited.

**Status:** `HLS-LAB-V1-INTEGRATED` remains **PARTIAL**. The new layer, demo and
scoped tests pass, but the full-suite gate is not clean. Existing discrete
production-action granularity can also leave residual participant effort
unusable during teaching. No campaign or scientific inference was performed.
See [the implementation record](experiments/HLS_LAB_V1.md) and
[current state](HLS_CURRENT_STATE.md).

### 2026-10-15 — exogenous environment/organization boundary (partial)

**Event:** 2026-10-15, implementation and test run; exact start time unknown.
**Recorded:** 2026-10-15 09:45 +02:00 (Europe/Madrid). **Authority:**
PI/CE focalized GO instruction. **Type:** additive engineering integration.

Added `src/hls/hls_lab_v1_environment.py` to compose C5's stationary,
nonstationary, or Markov task process with the existing
`DemandRegime`/`generate_problems` emitter. It produces a frozen exogenous
problem trajectory before any policy is run; environment and emission random
streams are separate, while policies receive only the emitted problems and
not latent environment states. Structural tests cover specialization,
complementarity, recurrence, novelty, regime change, matched policy inputs,
and reproducibility. A small executable regime-switching demo compares P0,
P1, and P2 on a shared trajectory. This is engineering verification, not a
scientific campaign or evidence of policy superiority.

**Implementation:** the integrated organization layer and exogenous environment
adapter, their tests, and demos are included in the minimum package.
**Validation:** focused environment plus integrated tests: 17 passed. Full
suite: 1189 passed, 13 failed in 314.78 seconds. The same 13 test identities from the
preceding full run failed again: a local foundation-result inventory mismatch,
B2.3/RQ0 protocol-provenance mismatches, and frozen Campaign 2/3/Gate hash or
artifact checks. No frozen hashes were refreshed. Source hashes for
`hls_lab_v1.py`, `hls_lab_dynamic.py`, `synthetic/c5.py`, and
`finite_problem_belief.py` were unchanged across this intervention.
**Publication:** commit `37a011804f9ea013fc3a5436c00a72eb0b8280da` was pushed at
2026-10-15 09:58 +02:00 to `origin/feature/hls-laboratory-v1`; the remote ref
was verified to match. Only the ten named package files were committed; other
pre-existing worktree changes were preserved. **Milestone closure:** not
declared; `HLS-LAB-V1-INTEGRATED` remains **PARTIAL** because the full-suite
integrity/provenance failures remain unresolved.

### 2026-10-15 — Scientific Campaign 1 pilot: exploitation vs capability development

**Event:** validated pilot execution completed 2026-10-15 10:22:04 +02:00.
**Recorded:** 2026-10-15 10:22 +02:00 (Europe/Madrid). **Authority:** CE
campaign instruction. **Type:** bounded scientific pilot.

The protocol varied demand (stationary/changing), initial competence deficit
(low/high), teaching effectiveness (0.10/0.85), and horizon (8/24) in 16
predeclared cells, with 10 seeds (`2026101511`–`2026101520`) per cell. It
compared P0 production-only, P1 fixed relation `(2,1,1)`, P2 adaptive teaching
over relations `(2,1,1)` and `(0,1,0)`, and a deterministic
scheduled-teaching/no-feedback control. Each ran with individual MIS-v2
learning OFF and ON. The OFF/ON block is a mechanism control, not an
additional environmental factor. Demand sequences and coordinate-indexed
observation innovations were paired by seed; policies did not receive the
experimenter-only latent regime. Every condition used a shared budget of 2.0,
which permits at least one unit of production alongside a lesson. Requirements
were 0.80/0.90 by competence axis; the common prior predicts at most 0.80
under the frozen catalogue/budget, while low- and high-deficit teams have
different analytical initial frontiers. These choices were fixed by the
catalogue and team geometry, not policy outcomes.

The discrete action catalogue means the teaching opportunity cost is not
only the explicit 0.5 participant-effort charge: with a 2.0 budget, a lesson
leaves 1.5 units, but only one full production unit is assignable, whereas
two units can be productive without a lesson. Residual effort granularity
therefore shapes the results and is a stated limitation.

**Observed results:** relative to P0, P1 had lower CES in 320/320 paired
comparisons. For P2, P0 had higher CES in 241/320, P2 higher in 37/320, and
42 tied; for the scheduled/no-feedback control, P0 was higher in 258/320,
that control higher in 20/320, and 42 tied. In high-deficit/high-efficacy/
long-horizon cells with individual learning OFF, P2 improved both outcomes:
stationary demand ΔCES +0.313 (between-seed SD 0.194), Δsuccess +0.483
(SD 0.074); changing demand ΔCES +0.380 (SD 0.107), Δsuccess +0.537
(SD 0.105). These CES and success gains were not present in the corresponding
LI-ON cells. P2 declined to teach in 4,497 of 5,120 episodes; P1 taught in
every episode. The common partial prior also prompted some unnecessary
teaching in low-deficit cases, demonstrating an information-cost limitation.

This bounded pilot contains conditions where investment in capability
development improved both measured CES and success, and conditions where
fixed or scheduled teaching was harmful. It does not establish a general
teaching advantage: the episode-level policy score is functional success,
deficit, margin, and effort—not the reported CES outcome. Means and
between-seed standard deviations are descriptive; no inferential tests or
population confidence intervals were calculated.

**Validation incidents:** three preceding executions were excluded. The first
exposed the latent regime through `demand_label`; the second initialized
estimated skills from private truth via `make_team`; the third used budget
1.0, under which teaching's 0.5 resource charge left no feasible positive
production action. Their manifests are retained as
`attempt_1_invalid_latent_label.json`,
`attempt_2_invalid_oracle_initialization.json`, and
`attempt_3_invalid_resource_granularity.json`. The validated run passes only
the generic label `observed-demand` and uses `make_dynamic_team` in
PARTIAL_STATIC mode with common initial estimates `((0.40,0.40),)*3`. The
final output uses `NA` for non-applicable CSV metrics. Its manifest is in
`results/experiments/hls_campaign1_pilot/manifest.json`; protocol and paired
machine-readable results are stored beside it. A pre-encoding manifest is
retained as `prior_complete_manifest_pre_na_encoding.json`; its rerun used
the same seeds and was only to make missing-value serialization explicit,
not an additional replicate set.

**Engineering validation:** the focused campaign/laboratory/environment
selection passed 71 tests (including 24 directly scoped campaign/integration
tests). The full repository suite was not run; its previously documented 13
integrity/provenance failures remain unresolved. This campaign neither closes
the laboratory integration milestone nor establishes a general scientific
conclusion.

### 2026-10-15 — Campaign 1 mechanism diagnostics

**Event:** existing-pilot analysis and deterministic targeted teaching-gain
replays completed 2026-10-15 14:28:17 +02:00. **Recorded:** 2026-10-15
14:28 +02:00 (Europe/Madrid). **Authority:** CE mechanism-diagnostics
instruction. **Type:** post-pilot diagnostic; no new policy comparison
campaign.

The published pilot's 20,480 episode records and 1,280 seed summaries were
hash-verified and reused. The P2−P0 CES contrast averaged −0.241 (SD 0.181)
for MIS-v2 ON and −0.126 (SD 0.246) for MIS-v2 OFF across 160 paired
configuration-seed units per condition. Their difference-in-differences was
−0.115 (SD 0.196; 28 positive, 112 negative, 20 ties). This is descriptive
factorial interaction within the frozen simulated design, not an estimate of
population effects or independent mechanism shares.

For 320 P2−P0 cumulative episode trajectories, 278 runs with teaching had a
negative cumulative path at some point; 39 later crossed back to nonnegative
(30 LI-OFF, 9 LI-ON), while 239 never crossed back. P2 finished ahead in 37,
behind in 241, tied in 42; 42 runs had no P2 teaching and tied throughout. In
the high-deficit/high-efficacy/long-horizon cells, the first teaching episode
had lower same-period CES in all 20 runs. With LI OFF, all 20 subsequently
crossed and finished ahead (mean break-even period 8.2 for changing and 17.3
for stationary demand). With LI ON, only 4/20 crossed after the teaching
episode's negative path; 3/20 finished ahead.

The frozen CSV directly supports nominal teaching effort, production effort,
resource use, residual capacity, CES, and real competence before/after each
period. It omits the record's exact `teaching_gain_real` field. A targeted
replay recovered that field from 876 teaching-containing policy/seed blocks
(7,422 events); every replay matched published actions, CES, resources, and
real-competence states. Each lesson used 0.5 participant-effort units and was
paired with 1.0 production effort versus P0's 2.0, leaving 0.5 budget unused
under the discrete catalogue. Exact realized skill gain by teaching was
available from the targeted replay, but LI-ON net competence change in the
published CSV cannot separate teaching from MIS-v2 without it.

P2 versus P0 estimates only the total policy-package contrast under paired
external conditions. The MIS ON/OFF difference-in-differences is interpretable
as the controlled interaction of that toggle and the policy contrast inside
this model. P2 versus scheduled-no-feedback does not isolate organizational
information because policies differ in teaching choices and exposure. Costs
are reported in resource units, not converted into an arbitrary CES utility.
No inferential tests or population confidence intervals were calculated.

Reproducible analysis code is
`experiments/synthetic/hls_campaign1/analyze_mechanisms.py`; summaries,
event-level targeted-replay records, temporal trajectories, SVG figure, and
hash manifest are in `results/diagnostics/hls_campaign1_mechanism_diagnostics/`.
The diagnostic work did not rerun the full 1,280-run pilot or change its
frozen artifacts.

Exact direct gains averaged 0.0352 (high efficacy) and 0.0103 (low) across
P1's teaching events. P2's event-selected means were 0.1031/0.0131 with LI
OFF and 0.1014/0.0128 with LI ON (high/low efficacy). These means condition
on distinct event-selection and competence-state paths and must not be read
as comparative estimates of teaching efficacy. Focused diagnostics, campaign
regressions, and integrated/environment regressions passed 62 tests; no full
repository suite was run. `git diff --cached --check` passed for the scoped
staged changes.

### 2026-10-15 — Campaign 1 counterfactual teaching value

**Event:** bounded paired intervention execution completed 2026-10-15
15:34:12 +02:00. **Recorded:** 2026-10-15 15:34 +02:00 (Europe/Madrid).
**Authority:** CE Campaign 1 counterfactual-teaching instruction. **Type:**
state-conditional counterfactual diagnostic; no adaptive policy was added.

The state-selection rule used all 32 combinations of the published pilot's
long-horizon cells (stationary/changing demand, low/high initial deficit,
0.10/0.85 teaching efficacy, MIS OFF/ON, period 2/16), fixed at the first
published seed `2026101511`. At every selected state, the two already-defined
directed relations `(2,1,1)` and `(0,1,0)` were evaluated: 64 paired branches.
The intervention was either P0's production-only action or a teaching action
for the specified relation with the best feasible production allocation
under the current observable score. Thereafter both branches followed the
same P2 rule, with separately evolving branch states and memories.

The published pilot CSV did not retain the full competence posterior needed
to continue faithfully. The runner was extended additively with a
period-boundary `OrganizationSnapshot` containing true team state, complete
skill posterior, public organization memory, and next period. Deterministic
prefix replays were checked against the pilot before snapshots were used;
the counterfactual branches deep-copy those snapshots and share the same
exogenous problem suffix and coordinate-indexed innovation scheme.

Initial teaching used 0.5 effort, displaced 1.0 production effort, and left
0.5 budget unused in every pair under the fixed discrete action catalog.
Immediate CES difference averaged −0.142 (SD 0.103). Remaining-horizon
`DeltaV_H` averaged −0.074 (SD 0.181; range −0.370 to +0.565), with 19
positive and 45 negative contrasts. The early group (22 decisions remaining)
averaged +0.033 (SD 0.186; 19 positive/13 negative); the late group (8
remaining) averaged −0.181 (SD 0.093; 0 positive/32 negative).

P2 chose no teaching in 22 of 32 selected states and relation `(0,1,0)` in
the other 10. Against only the tested conditional candidate values, 17 states
were correct no-teaching choices, 5 missed a positive candidate, 4 selected
a positive candidate, and 6 selected a candidate with negative conditional
value. These classifications do not establish global policy regret. The
sample has one fixed seed per stratum and supports no population inference;
the estimand is conditional on each state/event/P2 continuation/exogenous
suffix/coupling, not globally optimal teaching value.

Artifacts and SHA-256 manifest are in
`results/diagnostics/hls_campaign1_counterfactual_teaching_value/`; runner:
`experiments/synthetic/hls_campaign1/counterfactual_teaching.py`; tests:
`tests/test_hls_campaign1_counterfactual_teaching.py`. The focused validation
passed 23 tests across the integrated laboratory, published pilot,
mechanism-diagnostic and new snapshot/counterfactual suites. The full suite
was not run. This diagnostic does not close `HLS-LAB-V1-INTEGRATED`.

## 1. Initial portfolio and routing framing

The programme began from heterogeneous agents with changing task allocation,
operational experience, learning, and future competence distribution. The
important surviving insight was that local failure and local improvement do
not determine portfolio value. The abandoned framing around RouteNLP,
frequency-times-quality-gap, and a single teacher/student pair remains a
diagnostic antecedent, not the definition of HLS.

## 2. H1, minimal models, and CIV

H1 asked whether failure frequency and quality gap were sufficient statistics
for competence-improvement decisions. M0/M0.1 and the CR0--CR4 laboratories
provided scoped identities, null cases, thresholds, and microverification.
The CIV branch tested candidate portfolio-investment vocabulary and was
adversarially audited. Its durable lesson is that these models are scoped
diagnostic tools, not the programme-level theory; no novelty or universal
ranking claim follows.

## 3. Cross-domain and two-beam consolidation

The programme consolidated two foundational beams: organization/use of
competences and development/evolution of competences. Cross-domain theory was
retained as imported foundation material, with explicit ontology mappings and
limits on what can be transferred. The doctrine became: identify the missing
HLS object first, then search for theory that actually addresses it.

## 4. Empirical vehicle search

The B1/B2/B12 foundation reproductions established scoped source mechanisms
and executable interfaces. PACS experiments B2.1--B2.4 and subsequent B3--B5
diagnostics produced useful competence-change and interference evidence but did
not establish an end-to-end RQ0 result. The B2.1--B2.2 bridge failed its
counterfactual compatibility audit; B2.3 remained inconclusive under its
rescue criterion; B2.4 provided scoped interference/replay results. The
Office-Home B0 and Sprint0 screens stopped as vehicle gates. These are
negative, null, or inconclusive scientific outcomes, not disposable failed
experiments.

## 5. Transition to synthetic HLS worlds

Because realistic vehicles did not yet identify a clean causal test, the
programme built G0: a policy-neutral, composable world generator with explicit
task, competence, opportunity, development, reward, resource, and information
blocks. G0 passed its architectural and compatibility gates. A1 then froze and
validated the minimal exact world family.

## 6. A1 and exact reducibility structure

A1a--A1c established exact negative, boundary, strict-value, competence-
geometry, and SEP-Omega-reducibility cases within their declared worlds. The
important methodological result was to distinguish local Bellman inversion
from unavoidable on-policy non-greedy routing. A1 is a validated L0 regime,
not a general HLS claim.

## 7. C1--C5 and RQ0 diagnostics

C1--C5 reference gates extended the G0 capability surface for repeated
evolution, portfolio geometry, scarce development resources, competence
interactions, and task demand. The initial RQ0 diagnostics found local routing
inversions that were globally off-path; persistence strengthened local value
but did not remove that barrier. The mean-preserving lambda coupling family
was SEP-reducible at all 21 points.

## 8. Exact constructive geometry result

The preregistered zero-sum T2 redistribution family was executed on its
21-point grid before the analytical derivation. It produced strict integration
only at `.35`, `.40`, and `.45`. The subsequent exact derivation established
the interval `5/16 < alpha < 1/2`, with distinct Bellman-inversion and
greedy-admissibility boundaries. This is an existence result relative to the
exact model and strong-SEP contract, not a prevalence or empirical claim.

## 9. Current position

RQ0 remains open. The current theoretical object is the intersection between
HLS-optimal policies and strong-SEP-admissible policies. SEP-Omega equality
remains the coordination/reducibility boundary. No claim has been established
that HLS is intrinsically superior to sufficiently informed modular control.

## 10. G3-H integration audit: closed shortcuts and the local-information boundary

**Status discipline.** The G3/G3-H closure and C1/C2 boundary in
`HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md` are **CANONICAL
ESTABLISHED** within their stated scope.  The regime map, adversarial search,
structural autopsy, and C-stability files present in the working tree after
baseline `8972c3c` are **POST-BASELINE VERIFIED BUT NON-CANONICAL**: their
code, tests, and retained artifacts have been inspected, but they have not
been promoted to a canonical theory or current-state claim.  A repeated
finite observation is not a theorem, and no result in this section changes
the formal scope of G3-H.

### 10.1 Scientific sequence, not a new theory ladder

| Attempt | Local information retained | Future information omitted | Proposed shortcut | Status and stopping result | Lesson |
| --- | --- | --- | --- | --- | --- |
| G3 organizational-value reduction | Assignment-conditioned learning increments and ordinary assignment gaps | Nothing needed for the one-step `D=V(F(S,x))-V(S)` target | Express `D` through standard assignment sensitivities | **CANONICAL ESTABLISHED.** Exact G3 reduction. | This solves local organization-development value, not continuation choice. |
| G3-H local value `M=R+beta D` | Current reward and one-step organizational development | A further jointly evaluated organization-development opportunity | Rank present actions with `M` | **CANONICAL ESTABLISHED.** The closed G3-H counterexample reverses the `M` ranking under `Q`. | Local development value need not determine a continuation-sensitive action ranking. |
| C1 development-only future term | `M` and `max_y D(F(S,x),y)` | Future operational reward `R(F(S,x),y)` and the joint future `R`--`D` trade-off | Add the best future development increment | **ABANDONED / FALSIFIED.** It preserves the wrong ranking in the closed counterexample. | `max D` is not `max(R+beta D)`. |
| C2 joint future term | `M` and `max_y M(F(S,x),y)` | No relevant future joint opportunity is omitted | Add the future joint maximum | **CANONICAL ESTABLISHED reduction.** At `beta=1` it is the documented G3-H look-ahead; generally it has the same finite-horizon Bellman form. | Restoring exactness explicitly restores standard look-ahead/DP, not an intermediate HLS mechanism. |
| Beam-1 local interface `g,rho,m` | Current assignment gaps, action-induced transition, and successor reward residuals | Second-transition organizational/development value | Use `m=g-rho` and immediate crossings to summarize local organizational sensitivity | **POST-BASELINE VERIFIED BUT NON-CANONICAL.** The identity `m=R(F(S,x),bar a)-R(F(S,x),x)` was checked directly. | It is an exact first-successor diagnostic, not a continuation-value representation. |
| Regime Map v0 | Complete `A_U*`, `A_L*`, and `A_Q*` sets under the frozen evaluator | Nothing in the oracle label; no rule was proposed | Classify USE/local/dynamic sufficiency as R0/R1/R2 | **POST-BASELINE VERIFIED BUT NON-CANONICAL.** The initial coarse grid found only R0 and had many ties. | A coarse grid cannot establish absence of dynamic failure. |
| Adversarial regime search | The same frozen evaluator, with interior state and eta sampling | No continuation information in the tested USE/local rules | Search for positive `regret_U` and `regret_L` | **POST-BASELINE VERIFIED BUT NON-CANONICAL.** Positive regret for both USE and local `M` was found under homogeneous and heterogeneous learning. | The existence question closes against purely local decision rules in sampled G3-H states; it does not establish prevalence or a new theory. |
| Structural autopsy / local-information probe | `R`, `D`, `g`, `rho`, and `m`; Q only as label | Exact future joint opportunity | Seek a low-dimensional local separator or certificate for R0/R1/R2 | **POST-BASELINE VERIFIED BUT NON-CANONICAL.** Algebraic redundancies were removed; shallow probes and close cross-regime pairs did not yield an exact rule. | The observed local-information frontier is evidence of a compression boundary, not a theorem of impossibility. |
| No-immediate-crossing rule | All first-successor residual margins `m` | `V(F(F(S,x),y))` and the resulting continuation head | Infer USE sufficiency from preservation of current operational optimizers after every first transition | **HYPOTHESIS / UNRESOLVED.** Finite audits found no violation. | A regularity is not a certificate. |
| C-stability audit | Strong condition C: every member of `A_U*(S)` remains reward-optimal after every `F(S,x)` | The second-transition term in `H(x)` below | Prove or falsify a conservative USE-sufficiency certificate | **HYPOTHESIS / UNRESOLVED.** No counterexample and no proof. | First-successor organizational stability is not yet known to control continuation stability. |

`POST-BASELINE VERIFIED BUT NON-CANONICAL` above is intentionally not a
promotion: it denotes an auditable local implementation result pending Chief
Engineer review.  The authoritative G3-H scientific boundary remains the
canonical source cited above.

### 10.2 The repeated information pattern

These are not independent routes to a new HLS mechanism.  They instantiate
one recurring sequence:

```text
local policy or local summary loses a ranking
    -> seek a compressed local representation of the omitted future term
    -> retain a promising first-successor regularity
    -> try to turn it into a certificate for avoiding continuation
    -> exact correction needs a future joint opportunity
    -> that correction is explicit look-ahead / DP
    -> a proposal to decide whether that look-ahead is needed risks repeating
       the same omission unless it has genuinely new information.
```

The canonical C1/C2 pair closes the first instance exactly: development-only
future information loses `R`, while the joint future term restores standard
look-ahead.  The post-baseline `g,rho,m`, regime, frontier, and stability
lines test the same boundary from the other direction: whether first-successor
organizational information can certify that the omitted continuation term is
irrelevant.  They have not established such a certificate.

The latest C-stability line makes the residue explicit.  With

$$
Q_S(x)=R(S,x)-V(S)+H(x),
\qquad
H(x)=\max_y\{R(F(S,x),y)+V(F(F(S,x),y))\},
$$

condition C controls current operational optimality at `F(S,x)`, not the
deeper value `V(F(F(S,x),y))`.  For a USE-optimal action `u` to remain
Q-optimal, the missing inequality is

$$
H(x)-H(u)\le R(S,u)-R(S,x)\qquad\text{for every }x.
$$

The audit did not derive that inequality from C and did not find a
counterexample.  Its correct status is therefore **C-STABILITY CONJECTURE
UNRESOLVED**, not falsified and not certified.  The all-optimizer quantifier
in C is stronger than the existential and transition-dependent tie variants;
the tie distinction does not repair the missing second-transition ordering.

### 10.3 Durable negative knowledge

Future work must not relaunch any of the following under a new label without
genuinely new information, assumptions, or a proof:

- treating `M=R+beta D` as an exact substitute for a future joint opportunity;
- replacing `max_y(R+beta D)` by `max_y D` while claiming the same ranking;
- calling explicit future-joint evaluation a novel local representation when
  it is the existing look-ahead/DP calculation;
- treating first-successor organizational stability, an immediate crossing
  flag, or finite no-violation observations as an exact continuation
  certificate; or
- assuming that a rule for deciding whether to escalate reasoning is cheaper
  in information than the continuation quantity it must distinguish.  If that
  rule must estimate the omitted future opportunity, the original recursion
  has merely been moved to a screening or metareasoning layer.

No repository material audited after `8972c3c` implements a continuation
score, selective-continuation policy, value-of-computation rule, or
metareasoning mechanism.  Those names must not be used to repackage the
unresolved C-stability question as a distinct established direction.

The bounded conclusion is: local organizational/development information can
be useful, but the repository has established no exact nontrivial local
certificate of continuation relevance.  Where omitted future opportunities
change the ranking, the exact correction reintroduces explicit
continuation/look-ahead, i.e. standard DP machinery.

### 10.4 Matched-`ΔS` proposal: reduction confirmed — stop

**Status: HISTORICAL REDUCTION / FAILED DIRECTION — REDUCTION CONFIRMED —
STOP.**

The proposed matched-`ΔS` experiment would have held the action-conditioned
physical competence transformation `ΔS(a)` fixed while changing the
organizational placement or value of the acquired competence, then compared
the relative value of JOINT management and strong SEP. Independent adversarial
reductions from the Beam-1/static and Beam-2/dynamic perspectives agree on
its status: it could provide cleaner **causal experimental identification**,
but it does not supply a missing theoretical dependency.

The exact matched-`ΔS` experiment was **not** performed. Related evidence in
MIS, G3, A1c, and `C(α)` must not be retrospectively relabelled as a
matched-`ΔS` control. The reason to stop is logical reduction, not prior
execution of that exact control.

The dependency required for the intended comparison is already represented by
the established construction:

```text
placement sensitivity
  -> G3 / assignment sensitivity
  -> differences in organizational value and opportunity
  -> G3-H + standard dynamic optimization
  -> propagation through future opportunities
  -> policy-class exploitability
  -> Pi_SEP subset Pi_HLS and the strong-SEP strictness criterion
  -> possible differential JOINT-versus-SEP value.
```

This chain has an important non-implication. A difference in organizational
value or opportunity between cases does **not** by itself imply a difference
in `Φ = J_HLS - J_SEP,max`. Nor do G3 and G3-H alone prove a strict
HLS-versus-SEP advantage. Strict advantage additionally requires that the
opportunity difference be differentially exploitable under the relevant
policy-class restriction; that is the required third link supplied by the
existing strong-SEP strictness result.

#### Connection to the repeated integration dead end

This closure joins, but does not collapse into, the sequence in §§10.1–10.3.
Several lines of work have repeatedly attempted either:

1. to replace continuation-dependent information with a cheaper local or
   compressed representation; or
2. to isolate a further small causal distinction after the main dependency
   was already represented by established components.

The first pattern includes the local organizational-development value,
future-opportunity comparison, C1/C2, `(g, rho, m)`, Regime Map, adversarial
search, structural autopsy, no-immediate-crossing, A/B/C and C-stability, and
continuation/selective-reasoning proposals. The second includes the
matched-`ΔS` causal refinement. These are not all mathematically identical;
the narrower lesson is that a new name, representation, regularity, or
cleaner control does not establish a new scientific dependency.

#### Permanent reduction gate for Beam 1 × Beam 2 work

Before opening **any** new Beam-1 × Beam-2 integration subproblem, the Chief
Engineer or responsible expert must answer:

> **What mathematical or causal dependency is missing from the current
> construction?**

The construction against which a proposal must be reduced includes at least:

- Beam 1: organizational value, assignment structure, and placement
  sensitivity;
- Beam 2: endogenous competence evolution `F(S,a)`;
- standard dynamics: continuation, optimization, control, and DP; and
- integration: policy-class restrictions and the established strong-SEP
  strictness results.

The proposer must identify a dependency `X` such that all three conditions
hold **before implementation**:

1. `X` is required for the scientific claim being pursued;
2. `X` is not already implied by the construction above; and
3. the proposed analysis or experiment can falsifiably determine `X`.

If those conditions cannot be stated, **STOP**. The following are not, alone,
sufficient reasons to open a branch: a control not previously made exact; a
cleaner figure; a new representation or name; correlation with continuation
value; separation of synthetic cases; partial avoidance of DP; or a predictor
of selected observations.

#### Guardrail: do not reopen the local-continuation loop

Do not reopen the generic question “can local/current information determine
whether exact continuation would change the decision?” unless new assumptions,
a new information structure, or a theorem-level argument changes the problem.
Renaming it as a continuation score, future opportunity, stability
certificate, regime classifier, selective continuation, reasoning escalation,
metareasoning, value of computation, pruning criterion, continuation
relevance, or organizational screening is insufficient. If exact validation
of the proposed rule reconstructs the continuation value, `Q`, or the
look-ahead it was intended to avoid, classify the proposal as a reduction to
standard dynamic optimization and do not start a new branch from it.

#### Guardrail: missing identification is not missing science

Once a dependency is already established compositionally, do not create a new
experiment merely to isolate every link under increasingly strict controls.
Distinguish **missing experimental identification** from **missing scientific
dependency**. A cleaner causal control is justified only when it can establish
or falsify a scientifically necessary statement not already implied by the
current construction. Otherwise: **REDUCE — DO NOT EXPERIMENT.**

After this stop, the project does not immediately seek another small Beam-1 ×
Beam-2 gap. The current direction remains **CHARACTERIZATION / ASSEMBLY** as
recorded in `HLS_CURRENT_STATE.md`: `R0` (USE sufficient), `R1` (DEVELOP
relevant but separable), and `R2` (joint intertemporal management relevant)
are current characterization directions, not established boundaries or a new
theorem. The search for a new HLS-specific integration equation, score,
certificate, local rule, or dynamic theory is closed unless the PI explicitly
reopens it on genuinely new evidence or assumptions.

## 11. Campaigns 2 and 3; conditional deliberation

This section preserves the results and boundaries of the later finite-problem
campaigns. Their findings are scoped to their frozen simulator, samples,
policies, and endpoints; they do not replace the programme-level theory or
claim a general HLS architecture result.

### 11.1 Campaign 2: policy discrimination and realized consequence

The separate HLS strategy-discrimination gate first established that the
frozen test range changed actions under prospective policy restrictions; it
was not a policy leaderboard. Campaign 2 then evaluated eight fixed
scenarios, four probe configurations, four policy modes, and seeds 10–49. The
Q11-reference bank contained 15,360 eligible nonterminal states. Historical
Q11 regression passed, terminal decisions collapsed as expected, and the
report retained separate paired-state and closed-loop analyses.

The final classification is **CAMPAIGN 2 — ROBUST POSITIVE WITH IMPORTANT
NULL RESULT**. H1 was supported: hypothesis conflict was associated with
Q10 sensitivity, without a causal rule or a claim of value of information.
H2's structural conclusion was supported: global capability headroom alone
did not characterize development sensitivity. H3 was supported at low
prevalence: 71/15,360 coupled states (about 0.46%), interpreted as
non-separability in the prospective continuation landscape, not physical
synergy.

For the preregistered two-real-reward conditional consequence endpoint, Q10
had 19.56% divergence, 74.57% positive return, and mean `DeltaG=0.1623`
[0.1476, 0.1771]; Q11 had 19.91% divergence, 74.53% positive return, and
mean `DeltaG=0.1669` [0.1530, 0.1803]. Q01 diverged in 7.63%; positive return
was 45.99%, and mean `DeltaG=0.0015` [−0.0194, 0.0193]. Its realized utility
was **NOT SUPPORTED** in this estimand. This does not mean development is
generally useless. `DeltaQ>0` did not guarantee positive realized `DeltaG`.
Q11 superiority to Q10 was not established; G07 leading Q11 cumulative
performance in all eight scenarios was a secondary observation, not universal
team superiority. Every state-conditioned conclusion remains conditional on
the Q11-generated reference states and frozen range/physics.

The post-C2 support audit separately found **INSUFFICIENT COVERAGE** for using
Q11 alone as the sole future selector-development source: it missed 14.12%
of non-Q11 states under the preregistered diagnostic, especially Q00/Q01
action-different regions. This did not reopen H1–H4; it was a representation
coverage finding. The Campaign 2 I/O failure was retained as provenance and
the eventual valid rerun was separately committed; the incident is not to be
removed or retroactively obscured.

Sources: [strategy-discrimination gate](experiments/STRATEGY_DISCRIMINATION_GATE.md),
[Campaign 2 preregistration](experiments/CAMPAIGN_2_PREREGISTRATION.md),
[Campaign 2 results](experiments/CAMPAIGN_2_RESULTS.md),
[post-C2 coverage audit](experiments/CAMPAIGN_2_STATE_COVERAGE_AUDIT.md), and
[I/O incident record](experiments/CAMPAIGN_2_IO_INCIDENT.md).

### 11.2 Campaign 3: fixed generator/team families and deliberation

Campaign 3 froze a generator-only calibration and crossed generator split,
and a quotient team-geometry design with development and geometrically
separated held-out team sets. These are design choices inside the same
declared domain, not evidence that held-out teams are random representatives
or outside-domain structures. PGCG characterization histories were kept
separate from subsequent experimental histories.

The J=12 horizon pilot found **PERSISTENT BOUNDARY EVOLUTION**. The CE chose
not to execute J=18/J=24 and pragmatically set `ell=11` for subsequent
development assessment. This is not an optimal, true, or saturation horizon.
Gate 1 classified **PARTIAL LOCAL STRUCTURE — GO CONDITIONED TO C3.2** from
Q11-sourced development states; Q00 and Q11 were contrasting continuation
probes, not bounds. Gate 2 found **SUFFICIENT DEVELOPMENT DIVERSITY** across
the prescribed behavior sources and closed without creating value targets.

C3.2 froze 10,500 factual-state allocations and labels from development
histories, with TRAIN/VALIDATION/DEVELOPMENT_TEST split by replicate. The
target used by the C3.3 Ridge model is a noisy single Monte Carlo realization
of Q11-versus-Q00 forced initial action with Q11 continuation, accumulating
`mu_true` over the current problem remainder plus eleven subsequent physical
problems. Future physical problems are freshly generated conditional on the
realized prefix; branch-shared innovations are standard normals, while
observations, beliefs, and capabilities evolve separately. Beliefs reset at
problem boundaries; capabilities persist. It is not a two-decision target and
not an exact adaptive value-of-computation label.

C3.3 development compared Q00, Q11, and META on 2,100 matched development
histories; the later FAST/DEEP/META and META-VOC development experiments are
also development evidence, not confirmatory generalization. In the frozen
META-VOC confirmatory study, the equal-domain META-VOC-50 minus RANDOM-50
contrast was +0.1167 cumulative `mu_true` per history [0.0310, 0.2013] and
−0.1924 measured seconds [−0.3539, −0.0228]. This joint contrast met the
prespecified rule, but the primary 50% point was selected after reviewing
development results, realized call frequencies differed, G1/G2 showed
positive production intervals while G3/G4 did not demonstrate an advantage,
and the result is not universal efficiency or exact budget equivalence.

The separately authorized local predictor-validity audit now records weak to
limited statewise prediction of the C3.2-matched advantage: pooled equal-domain
AUC 0.624 [0.572,0.667], near-universal positive raw predictions with low
specificity, and a META-VOC-routed versus FAST-routed mean target contrast of
0.0104 [−0.0200,0.0431]. Most statewise Monte Carlo intervals spanned zero.
The audit therefore does not establish reliable identification of useful
DEEP opportunities or cost-adjusted optimality. It does not invalidate the
separate confirmatory sequential policy contrast. This audit report and
artifacts currently reside in the uncommitted worktree and should be treated
as local evidence until integrated.

The paper-facing record and review instructions reject algorithmic novelty
claims for FAST/DEEP choice, conditional computation allocation, supervised
selector learning, benefit prediction, cost use, or benefit-per-cost routing.
The defensible framing is an experimental characterization of conditional
deliberation in a sequential system with endogenous capability change and a
policy-induced state distribution. No informed alternative-selector
comparison is recorded. A standalone written Independent Scientific Reviewer
report is not present in the repository, so reviewer-specific conclusions
remain externally sourced rather than independently traceable here.

Sources: [C3 theory](theory/CAMPAIGN_3_THEORETICAL_SPECIFICATION.md),
[generator split](experiments/CAMPAIGN_3_GENERATOR_SPLIT.md),
[team split](experiments/CAMPAIGN_3_TEAM_SPLIT.md),
[horizon result](experiments/CAMPAIGN_3_HORIZON_PILOT_RESULTS.md),
[Gate 1](experiments/CAMPAIGN_3_GATE1.md),
[Gate 2](experiments/CAMPAIGN_3_GATE2.md),
[C3.2 protocol](experiments/CAMPAIGN_3_C32_DATA.md),
[META-VOC confirmatory results](experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md),
[scientific record](paper/META_VOC_SCIENTIFIC_RECORD.md), and local
[predictor validity report](experiments/META_VOC_PREDICTOR_VALIDITY_REPORT.md).

### 11.3 Campaign 4 preparation and current stop

Campaign 4 remains in preparation. Bounded reconstruction tests verified
frozen C3 streams and real-decision replay, as well as FAST/Q00 and
DEEP/Q11 action equivalence on the tested states. The audit found a material
estimand distinction: C4 H0 is exactly two real decisions, while the C3.2
supervised target uses the longer `ell=11` horizon and fresh conditional
future problems. C4 H2 also follows a different clock/history convention.
The C3.2-matched predictor-validity audit does not turn H0/H1/H2 into the
same estimand, nor does it complete Campaign 4's broader opportunity or
development analysis.

The engineering report's decision is **NO-GO for the planned N=800 C4
execution until the PI/CE accept the estimand distinction and resolve the
remaining design/precision questions**. No C4 scientific counterfactual
outcomes were generated. The protocol's dated status has been corrected in
the local worktree to reflect the present engine/preflight and bounded audit
while preserving the no-execution decision. The protocol, engine and report
remain uncommitted local material; the bounded verification is engineering
evidence, not a scientific C4 result.

Source: [C4 engineering verification](experiments/CAMPAIGN_4_ENGINE_VERIFICATION.md)
and the current local [C4 protocol](experiments/CAMPAIGN_4_COUNTERFACTUAL_PROTOCOL.md).

### 2026-10-15 17:42 +02:00 — behavioral plausibility validation

**Event time:** 2026-10-15 17:42:56 +02:00, verified by
`results/diagnostics/hls_behavioral_plausibility/manifest.json`.
**Recorded:** 2026-10-15 17:43 +02:00 (Europe/Madrid). **Authority:** CE-ordered
engineering/scientific-model validation. **Status:** completed bounded
validation; no implementation defect demonstrated; HLS Laboratory v1 remains
PARTIAL.

The deterministic fixture verified monotone additive production, task-relevant
specialization, requirement-based functional complementarity, resource
accounting, MIS-v2 exposure/saturation/bounds, directed teaching efficacy and
targeting, teaching/MIS separation, P2 abstention when requirements are met,
and exogenous environment contracts. With P0 as common continuation, selected
teaching interventions had both signs: persistent deficit/high efficacy and
long horizon `DeltaCES_H=+0.8825` (break-even period 12); short horizon
`−0.3575`; weak efficacy `−0.9000`; and after regime change `−0.0475`.
Learning-by-doing ON produced `+2.4445` in that fixture, so the hypothesized
reduction of teaching's marginal value was not observed in this configuration.
These are conditional deterministic checks, not policy-ranking or population
claims.

The frozen discrete action catalogue explains the exact budget-2 resource
example: teaching consumes 0.5, permits 1.0 productive effort, and leaves 0.5
unusable; compared with the no-teaching maximum of 2.0, 1.0 productive effort
is displaced. This is an existing granularity assumption, not an accidental
resource-accounting defect. The initial diagnostic threshold 1.8 was above
the selected team's 1.15 frontier and was rejected before the recorded run;
the final 1.0 threshold was fixed from the frontier calculation, not selected
by policy outcome. Specialized fixture CES weights were aligned to the active
skill so an inactive dimension could not zero the reward.

Tests executed: 54 focused integrated/environment/CE-23–25 checks passed; 56
DISCOVER-v0, MIS-v2, dynamic-lab and Campaign 1 regression checks passed (110
total). The full suite was not rerun; the previously recorded 13 provenance
failures remain unresolved and hashes were not changed. `LearningProfile`
inherits MIS-v2's `0<eta<1` contract, so zero MIS learning is represented by
the existing disabled flag; an exact per-competence eta=0 rate is unsupported.

Artifacts: runner
`experiments/synthetic/hls_lab_v1/behavioral_plausibility.py`, tests
`tests/test_hls_behavioral_plausibility.py`, and machine-readable
`scenario_summary.csv`, `scenario_trajectory.csv`, `manifest.json` under
`results/diagnostics/hls_behavioral_plausibility/`. The manifest records seed,
parameters and source/output SHA-256 values. No frozen result or source was
modified.

### 2026-10-16 — HLS laboratory experimental-validity assessment

**Event:** deterministic diagnostic run completed 2026-10-16 10:14:59 +02:00;
**recorded:** 2026-10-16 10:15 +02:00 (Europe/Madrid). **Authority:** PI
priority decision (laboratory consolidation GO; experimental validity priority
1; new scientific campaign HOLD). **Type:** instrument validation and
documentation; no simulator physics, historical result, or policy was changed.

Eight predeclared fixture checks passed: equivalence across seeds under zero
noise; a competence-sensitive output/CES change (`.5→.6`); functional success
below and failure above the enumerated output frontier `1.15`; allocation
sensitivity (`.8` vs `.2` output); isolated MIS-v2 (`.4→.85` skill and `.4→.7`
second-period output with LI ON); budget-2 resource accounting (lesson `.5`,
production 1.0, residual `.5`); zero-efficacy teaching (no direct gain but
resources charged); and common generated demand for P0/P1/P2. Two runs yielded
identical diagnostic JSON SHA-256
`b3778c626f7fad6800fc74d88922f0feb8324858d37da7d8893d08a42fc7bb58`.
Focused tests passed: 26.

The assessment concludes that conditional internal mechanism and matched-path
checks are possible, but ordinary P0/P1/P2 comparisons bundle policy,
teaching and information differences. Gross CES, separately reported cost,
and functional success do not yet define a single net comparison objective;
equal budgets need not mean equal consumption. No external calibration or new
campaign was performed. The full suite was not rerun; the previously reported
13 integrity/provenance failures remain an open repository-level validation
issue. HLS Laboratory v1 remains **PARTIAL**. See
[the assessment](experiments/HLS_LABORATORY_VALIDITY_ASSESSMENT.md) and its
reproducible artifacts in `results/diagnostics/hls_laboratory_validity_assessment/`.

### 2026-10-16 — first scientific campaign design (execution on hold)

**Event/recorded:** 2026-10-16 10:29 +02:00 (Europe/Madrid). **Authority:**
PI/CE request to design, but not execute, the first scientifically
interpretable HLS campaign. **Type:** protocol design only; no simulation,
code or historical result changed.

The recommended primary question is whether redistributing a fixed aggregate
three-agent/two-skill competence endowment changes collective gross
performance under IID versus persistent demand with the same task marginals,
and whether the contrast changes when the same MIS-v2 learning mechanism is
enabled. The proposed experiment holds P0, information, action catalogue,
resources and horizon common; teaching is excluded to avoid mixing the
architecture question with a mechanism already examined in Campaigns 1–2.
The proposal uses frontier-based difficulty strata, matched demand paths,
40 independent demand trajectories per demand process, and an explicit
equivalence control. It estimates 964 organization-trajectories if all
preflight strata pass; it is not a power-certified sample.

Q1 was selected over Q2 (substantial overlap with G2/G3-H and no existing
matched developmental-assignment policy contrast) and Q3 (directly overlaps
Campaigns 1–2 and is one mechanism rather than the general architecture
question). Novelty for Q1 remains unverified because G1/G2 and workforce
allocation literature cover adjacent territory. Recommendation is **GO for
preflight and protocol registration; HOLD execution** pending frontier and
equivalence acceptance, CE selection of a minimum meaningful CES difference
or estimation-only objective, and a novelty review. No new policy or
simulator generalization is currently required. Details: [campaign design](experiments/HLS_FIRST_SCIENTIFIC_CAMPAIGN_DESIGN.md).

### 2026-10-16 — Q1 scientific campaign preflight

**Event/recorded:** 2026-10-16 10:45 +02:00 (Europe/Madrid). **Authority:**
CE authorization for preflight only; main campaign remained on HOLD. **Type:**
preregistered instrument and identifiability diagnostic. The preflight protocol
was registered before samples were generated (document SHA-256
`7fcfb9a900e522356531d02ef1fa65bc619643e798c3373a7031b39bdc4572ce`; JSON
SHA-256 `45cbdd4254ea6353d6ef3dc1a66b8f9c5b900b1ff2fc4a602b7fe00db81e804f`).

Architecture matching, equal-marginal demand specification, IID/Markov
persistence, exact feasibility frontiers, MIS-v2/no-teaching controls,
resource accounting and equivalence controls passed. Demand diagnostics used
200 paths per process; outcome checks used 12 independent paths per process,
288 matched organization trajectories and four equivalence-control runs. The
frontier controls produced both easy shared-feasible tasks, a near-boundary
architecture success contrast, and initially infeasible but MIS-witness-
reachable tasks.

The preregistered primary interaction was structurally null in this design:
with MIS OFF, matched P0 architecture effects were `+2.4` CES over 24 periods
for every paired path; direct one-period checks gave `+.1` for each task type.
IID and Markov have the same stationary task marginals, and the primary block
has no material competence/state transition, so temporal ordering cannot
change the expected mean architecture contrast. The seed-cluster bootstrap
estimate was approximately zero (`−1.33×10⁻¹⁵`, 95% percentile interval
`[−4.00×10⁻¹⁵, 4.44×10⁻¹⁶]`). This is a structural limitation of the
registered estimand, not evidence against the simulator or a scientific
discovery. MIS-ON remained secondary and was not promoted after observing
results.

**Decision:** **NO-GO** for the 960-run campaign as registered; require a
CE-approved redesign and new registration before any campaign execution. The
main campaign was not run. Focused regression tests passed (24), and two
independent output-directory executions were byte-identical. The full suite
was not rerun; the 13 previously documented integrity/provenance failures
remain unresolved and untouched. HLS Laboratory remains **PARTIAL**. Evidence,
runner, tests, results and hashes: [Q1 preflight](experiments/HLS_Q1_PREFLIGHT.md)
and `results/diagnostics/hls_q1_preflight/`.

### 2026-10-16 — Q1-R analytical verification

**Event/recorded:** 2026-10-16 11:05:36 +02:00 (Europe/Madrid). **Authority:**
CE authorization for analytical verification; campaign design and execution
remain on HOLD. **Type:** exact finite-state mathematical/computational check;
no simulator physics, registered Q1 protocol, or historical campaign artifact
was changed.

Under fixed competence, stationary initialization with common demand marginal,
memoryless task-specific P0 decisions, time-invariant actions/constraints,
and per-period resource reset, the expected cumulative reward is
`T * sum_d pi[d] * u_A(d)` for either IID or Markov demand. Hence the
architecture × persistence interaction is zero for MIS OFF under those
conditions, though the realized path distributions need not be equal. The
current runner's competence posterior can update even with MIS OFF; the result
requires that this update not change P0's decision mapping, as in the registered
full-information, zero-observation-noise contract. No universal claim that
Theta(0) must vanish under partial/noisy estimates is made.

An exhaustive two-period enumeration over all four demand paths using the
existing P0/MIS-v2 runner produced `Theta(0)=0` and `Theta(1)=-0.003` gross
CES for matched homogeneous and tilted architectures, with `pi=(.5,.5)`,
Markov persistence `.8`, `B=2`, cap `1`, and `eta=.10`. Architecture effects
were `.200` under MIS OFF for both processes, `.195` under IID/MIS ON, and
`.192` under Markov/MIS ON. This is a negative, design-conditional existence
result: repeated exposure reduces the tilted architecture's relative
remaining-gap learning increment. It demonstrates current-model
expressibility, not general superiority, external validity, or a novel
scientific result. The accounting identity for the factorial interaction
holds; it does not causally separate MIS from its effect on future P0 action
paths.

The mathematical derivation, exact parameters and reproduction command are in
[Q1-R analytical verification](theory/HLS_Q1R_ANALYTICAL_VERIFICATION.md);
the executable enumeration is `tests/test_hls_q1r_analytical.py`. Focused
validation passed (2 tests). The Q1 preflight's 24-period MIS-OFF primary
remains **NO-GO as registered**; no campaign was redesigned or run. The
laboratory remains **PARTIAL**.
