# Critical review: Nembhard adaptive-allocation protocol

**Reviewed revision:** `62a08df08adcf85822cb0dfa3e7e027cba9c5ddc`
**Review date:** 2026-10-17
**Decision:** **ADJUST for the reviewed baseline; the corrected documentary draft still requires PI/CE review and separate execution authorization.**
**Scope:** static/documentary review only. No simulation, campaign, code, or test was run or changed.

## 1. Executive assessment

The protocol has a scientifically interpretable core and is executable through
the existing Nembhard route plus deterministic preparation of explicit
`ProblemSpecNK` sequences. Its fixed profile, resource, problem and horizon
definitions are internally coherent; ORACLE and ADAPTIVE use the intended
physical model and differ in decision-time information. The primary measures
are available from existing period records or deterministic post-processing.

The published draft should not be run unchanged for four bounded reasons:

1. The 18-run catalogue-order diagnostic reruns two deterministic identity
   cases (FIXED and ORACLE) already present in the primary matrix. Reuse those
   records and execute 16 new diagnostic episodes; the unique total is **1,016**,
   not 1,018.
2. The protocol's statement that Gaussian draw order can diverge with selected
   cells contradicts the implemented observation function: at positive noise
   it draws once for every agent-skill coordinate, including zero-work cells.
   This makes positive-noise draws coordinate-aligned for equal dimensions,
   horizons and seed, although sigma-zero runs have no Gaussian draws and
   realized observation/update paths still diverge.
3. H1-H3 are moderation hypotheses, but the draft does not name their
   difference-in-differences estimands. Those contrasts should be stated
   explicitly and computed within replicate bundle before the campaign.
4. The sequence digest is requested but its canonical serialization is not
   specified, preventing independent reproduction of the hash.

These are documentary corrections, not reasons to change the simulator or
scientific mechanisms. They are incorporated in the accompanying protocol
update in this review transaction. The proposed study is a reasonable
small exploratory comparison. It remains conditional on the declared
synthetic Nembhard adaptation, task catalogue, role map and seed-generation
rules; it cannot identify the effect of adaptation in isolation from the
policies' different decision rules, information and candidate use.

## 2. Repository state and evidence examined

The active branch is `feature/hls-laboratory-v1`; HEAD at review was the
specified commit. Pre-existing unrelated modifications and untracked files
were present in the worktree and were left untouched. The protocol and current
state, philosophy, ontology, operational plan, architecture review, and common
experiment contract were read alongside the source implementation below.

Evidence references use repository-relative paths and line ranges from the
reviewed source revision:

- Direct curve, beginning-of-period output and exposure update:
  `src/hls/hls_lab_nk_nembhard.py`, `nembhard_productive_outputs_nk`
  (lines 175–210) and `advance_nembhard_experience_nk` (213–237).
- ORACLE information boundary and action selection:
  `src/hls/hls_lab_nk_nembhard_router.py`,
  `NembhardOracleDecisionViewNK` and `NembhardOracleRouterNK.choose`
  (lines 20–62, 76–120).
- Adaptive observation, estimator and policy:
  `src/hls/hls_lab_nk_nembhard_adaptive.py`,
  `observe_nembhard_work_outputs_nk` (180–205),
  `update_productivity_estimator_nk` (208–256),
  `NembhardAdaptiveDecisionViewNK` (259–289), and
  `NembhardAdaptiveRouterNK.choose` (303–359).
- Episode ordering, feasibility, trace fields and named RNG streams:
  `src/hls/hls_lab_nk_execution.py`,
  `_run_nk_nembhard_direct_sequence` (1098–1250; configuration dispatch at
  274–390). Serialization is
  `serialize_nk_nembhard_direct_result` (1317–1319).
- Organization/problem/resource contracts and catalogue enumeration:
  `src/hls/hls_lab_nk_geometry.py`, `OrganizationConfigNK` (85–126),
  `OrganizationResourcesNK` (129–162), `ProblemSpecNK` (165–201), allocation
  feasibility (204–220), and `enumerate_productive_action_entries_nk`
  (237–270 onward).
- Functional outcome and ranking:
  `src/hls/hls_lab_nk_production.py`, `evaluate_problem_nk` (45–59) and
  `functional_effort_rank_nk` (93–107).
- Native Nembhard result adapter and explicit provenance limits:
  `src/hls/experiment_contract.py`, `adapt_nembhard_run` and adapter context;
  `docs/engineering/HLS_COMMON_EXPERIMENT_CONTRACT.md`, sections 2–5.
- Existing regression evidence is in
  `tests/test_hls_lab_nk_nembhard.py`,
  `tests/test_hls_lab_nk_nembhard_oracle.py`,
  `tests/test_hls_lab_nk_nembhard_adaptive.py`, and
  `tests/test_hls_common_experiment_contract.py`. Tests were not rerun as part
  of this review.

## 3. Reconstruction of the proposed 1,018 runs

The primary factorial is arithmetically correct:

| Component | Calculation | Episodes | Role in design |
|---|---:|---:|---|
| Primary matrix | 3 profiles × 2 `p=r` scales × 2 demand orders × 4 arms × 20 replicate bundles | 960 | Main paired comparisons |
| Primary FIXED | 3 × 2 × 2 × 20 | 240 | One per profile/scale/order/bundle |
| Primary ORACLE | 3 × 2 × 2 × 20 | 240 | Same cells and demand paths as FIXED |
| Primary ADAPTIVE, σ=0 | 3 × 2 × 2 × 20 | 240 | Same cells and paths |
| Primary ADAPTIVE, σ=.05 | 3 × 2 × 2 × 20 | 240 | Same cells and paths |
| Exploration sensitivity | 2 noise levels × 20 bundles, mixed/fast/clustered, epsilon=0 | 40 | Paired against primary epsilon=.05 arms |
| Catalogue-order diagnostic, as written | 6 row permutations × 3 policies | 18 | One selected mixed/fast/interleaved bundle |
| Draft total | 960 + 40 + 18 | **1,018** | Includes two repeated identity runs |
| Unique total after reuse | 960 + 40 + (18 − 2) | **1,016** | Reuses primary identity FIXED and ORACLE records |

At 120 periods per episode, the unique total is **121,920 period records**.
For the candidate-scoring upper bound, the primary ORACLE+ADAPTIVE arms
contribute 5,529,600 candidate evaluations (720 episodes × 120 × 64), the
exploration slice contributes 307,200 (40 × 120 × 64), and the non-identity
permutation diagnostic contributes at most 84,480 (11 router episodes × 120
× 64: five new ORACLE plus six ADAPTIVE). The corrected upper count is
**5,921,280**, before feasibility filtering. FIXED executes a supplied action
and does not enumerate/score the catalogue. This is a count, not a runtime
estimate; no execution-time claim is made.

The 20 replicate bundles yield 20 paired values per cell-level contrast. This
is acceptable for exploratory characterization, not confirmatory power. The
bounded epsilon slice and row-order diagnostic answer identifiable
methodological sensitivities and do not turn the design into an unbounded
factorial. No accidental reruns are needed: the identity permutation is
already the primary indexing condition. Reuse its FIXED/ORACLE records; retain
the identity-permutation ADAPTIVE epsilon-zero run because it is not in the
primary matrix.

### Seed interpretation

The seed formula in the protocol is deterministic and uses separate integer
seeds for interleaved schedule construction, clustered schedule construction,
observation, and exploration. Same demand objects are replayed across policies
within each order. A common replicate index pairs the two schedule regimes,
but the schedules are generated by separate seeded procedures; this is not a
claim that their random draws are common.

For positive observation noise, `observe_nembhard_work_outputs_nk` consumes a
Gaussian draw for every `(agent, skill)` cell, even if work is zero, discarding
the draw when no observation is emitted. Thus, with equal N, K, horizon, and
observation seed, positive-noise trajectories have coordinate/time-aligned
Gaussian innovations despite different allocations. Only worked cells
assimilate them, so resulting estimates/actions can diverge. At sigma zero,
the code consumes no Gaussian draws; sigma-zero versus sigma-positive is not
a common-noise-draw contrast. The protocol draft's statement that draw count
and order can diverge by selected cells is inaccurate and must be corrected.

The exploration generator is independent from observation noise. Given equal
seed, epsilon, feasible-catalogue size and problem path, its per-period
exploration gate/index draws remain aligned. It does not make the resulting
actions or states identical.

## 4. FIXED reference

FIXED is a predeclared task-type-to-role table, not a single action reused on
incompatible tasks. It reads the current problem type and the fixed role IDs;
it does not read `D`, `k,p,r`, productivity, outputs, outcomes, or future
problems. The same rule is applied to all three profiles and is not selected
from outcomes. At the chosen allocations, each active agent uses effort 1,
within its limit 1; total effort is 2, within both the organizational and
problem budget 2. Its actions are representable by the existing K=2 action
catalogue and explicit allocation route.

It is a reasonable, deliberately role-aligned baseline, not a random or
intentionally weak allocation. The mapping does incorporate a design choice:
the role IDs encode skill-1/skill-2/generalist roles, and those same rows align
with the specialist profiles. Therefore results compare ADAPTIVE against this
particular competent static dispatch rule; they do not establish advantage
over every possible fixed map. The fixed map also reacts to the observed
current task type, so “fixed” means no state/outcome-based reassignment, not
ignorance of the current task. This definition is acceptable if that boundary
is stated and the mapping is frozen before outcomes.

The protocol's hand calculations are consistent with `P(0)=k/2` under
`p=r`: homogeneous FIXED gives 1.2 on a single-skill task and (.6,.6) on
joint; mixed gives 1.5 and (.9,.9); specialists give 1.8 and (1.1,1.1).
These checks also show that the map does not make every starting task succeed
or fail. Equal aggregate `k` is not equal task-specific FIXED output; the
protocol correctly acknowledges this.

## 5. ORACLE and ADAPTIVE audit

### ORACLE

The ORACLE decision view contains only resources, the current problem, true
Nembhard `D[N,K]`, true `k,p,r`, and duration. It enumerates the declared
feasible catalogue (default ordered 64 actions for K=2), constrained by
individual effort limits and the lesser of organization/problem budgets.
It predicts current-period output with `nembhard_productive_outputs_nk` and
maximizes `(success, -normalized_deficit, margin, -effort)`. Stable maximum
selection retains the earliest catalogue entry on exact ties. It uses no CES
or future-value term. Its horizon is one decision period, repeatedly applied;
it is not a long-horizon oracle or upper bound. Comparisons involving it
include privileged true-state/profile access and the myopic functional rank.

### ADAPTIVE

Its decision view contains current resources/problem, the per-cell running
estimate and count/dispersion, executed allocation history, reconstructed
experience, and duration. It does not receive true `k,p,r` or true
productivity. In this protocol `D` starts at zero and is reconstructed from
executed work; the code would not expose caller-supplied latent initial `D` as
observable history, so nonzero initial D is rightly excluded.

After current-period production/evaluation, each positive-work cell can yield
individual output `z_obs = e*delta_t*P(D_t) + epsilon`; zero-work cells yield
no observation. For work above the minimum threshold, the estimator updates
its Welford mean using `max(0,z_obs/work)`. The initial .6 estimate is not a
pseudo-observation: the first valid observation replaces it. Its chooser uses
the estimate for current-period functional ranking; epsilon-greedy selects
among feasible entries, including the greedy candidate. It does not estimate
curve parameters and does not see future output.

Two distinct processes operate: actual productivity changes with exposure
under the Nembhard curve, while the statistical estimate changes from noisy or
noiseless observed output. The proposed traces preserve both true state for
external evaluation and estimate state for audit; only the latter enters
ADAPTIVE decisions. Allocation determines exposure, so experience is an
endogenous mediator rather than a held-constant nuisance variable.

The design can characterize the joint deployed bundle (estimated state,
epsilon exploration, and Nembhard experience dynamics). It cannot assign a
causal share to estimator quality versus exploration versus experience
without additional controls. The existing epsilon-zero sensitivity is a
useful bounded control, but no additional estimator ablation is required for
this first policy-comparison question.

## 6. Conditions, metrics, and hypothesis identifiability

The three `k` matrices are distinct but have equal per-skill sums (3.6), equal
initial aggregate productivity (1.8 per skill under `p=r,D=0`), and equal
asymptotes. Faster versus slower `p=r` preserves initial fraction and
asymptote while changing the initial slope fourfold. This is an interpretable
parameter contrast, not an off/on learning comparison. The 120-period
interleaved and clustered sequences have the exact same 40/40/40 problem
multiset per bundle. Requirements, per-problem budgets, organization limits,
initial experience, profile, duration, and horizon are matched across policy
arms. Endogenous action, observation, and experience trajectories are
appropriately allowed to differ.

The trace exposes allocation, per-agent outputs, aggregate outputs,
`productivity_before`, experience before/after/increment, functional result,
effort and router diagnostics. Adaptive traces add predictions, estimator
before/after, observations and exploration flags. Thus the listed metrics are
directly recorded or exactly derivable. True productivity and experience are
diagnostic/evaluation fields and do not enter ADAPTIVE's decision view.
Functional success is the fraction of periods successful; normalized deficit
is summed over positive-requirement dimensions by the evaluator. Task-relevant
output is derivable by summing output only on the current problem's active
dimensions; all-skill output should remain separately reported. Effort and
exposure are distinct units, though numerically equal at duration 1. CES is
available but is correctly secondary and not substituted for functional
ranking.

The primary policy contrasts estimate performance differences between
complete strategy bundles, not the isolated causal effect of an abstract
“adaptation switch.” FIXED is a task-conditioned static map; ORACLE/ADAPTIVE
search the same larger catalogue using different information. FIXED versus
ADAPTIVE is valid for the declared policy comparison. ORACLE versus ADAPTIVE
combines information, estimator, and exploration differences; FIXED versus
ORACLE compares static dispatch with a perfect-information myopic optimizer.
The protocol correctly should not label either contrast as a pure information
effect or future-planning effect.

To make the moderation claims in H1–H3 answerable, predeclare within-bundle
interaction contrasts, not just inspect separate cell means:

- H1: `(ADAPTIVE−FIXED)_profile − (ADAPTIVE−FIXED)_homogeneous` for mixed and
  specialists, separately by primary outcome, learning level, demand order,
  and observation-noise arm.
- H2: `(ADAPTIVE−FIXED)_fast − (ADAPTIVE−FIXED)_slow`, separately by profile,
  order, noise arm, and primary outcome.
- H3: `(ADAPTIVE−FIXED)_clustered − (ADAPTIVE−FIXED)_interleaved`, by profile,
  learning level, noise arm, and primary outcome.
- H4: `ADAPTIVE(σ=.05) − ADAPTIVE(σ=0)` under the common problem path and
  replicate seed bundle.

Construct each difference-in-differences per replicate bundle, then summarize
its 20 values and uncertainty. Keep the proposed paired t/bootstrap
descriptions exploratory; use the replicate bundle as resampling unit. H5
remains a descriptive comparison of first-period and full-horizon rankings,
not a test that policies plan ahead. No significance or universal superiority
claim follows.

## 7. Technical feasibility

| Capability | Status | Existing contract / limitation |
|---|---|---|
| N=3,K=2 state identifiers, effort and shared budget | Supported directly | `OrganizationConfigNK`; Nembhard path uses IDs/resources and ignores HLS competence as physical state. |
| K=2 problem vectors, task-specific active dimensions, problem budget | Supported directly | `ProblemSpecNK`; explicit problem sequences accepted by `run_nk_production_sequence`. |
| Nembhard profile and initial D | Supported directly | `NembhardDirectProfileNK`, `NembhardDirectExecutionNK`; `D=0` default. |
| Direct production and post-output exposure transition | Supported directly | `nembhard_productive_outputs_nk`, `advance_nembhard_experience_nk`. |
| ORACLE/ADAPTIVE action enumeration and feasibility | Supported directly | `router_id` dispatch; catalogue bound via `max_candidates`; no truncation. |
| FIXED rule | Preparation adapter | Materialize one of three allocations from current `problem_id` per period; supply via `NembhardDirectExecutionNK.allocations`. This does not alter model equations. |
| Exact-composition order sequences and stable digest | Preparation adapter | Existing environment does not guarantee 40/40/40 with these order constraints; materialize and freeze explicit problems before runs. Canonical JSON and SHA-256 are specified in the revised protocol. |
| Shared paired outputs and descriptive/interaction analysis | Post-processing | Native serializer and common run adapter can retain records/provenance; statistical summaries are not supplied by the simulator. |
| Perfect-information Nembhard ORACLE vs imperfect ADAPTIVE | Supported with limitation | ADAPTIVE has individual selected-cell feedback; this is an instrumentation assumption, not aggregate-only observation. |
| Nembhard with MIS-v2, teaching, P0/P1/P2 or competence estimation | Not supported | Not needed by this protocol and not to be added for it. |

No item requires a scientific-model change. A small sequence/FIXED
orchestration and post-processing script is sufficient. The output/requirement
unit relation is an explicit caller calibration, not enforced dimensional
conversion; verify it before any run.

## 8. Corrections identified at the reviewed baseline

The following corrections were necessary in the version at commit `62a08df`.
They have been incorporated into
`HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL.md` alongside this review. They
remain conditions for any future campaign authorization to verify against
the revised document:

1. **Run count/reuse:** identify one of the 20 primary mixed/fast/interleaved
   bundles for the permutation diagnostic. Reuse its existing identity FIXED
   and ORACLE outputs. Execute the identity ADAPTIVE epsilon-zero diagnostic
   plus the five non-identity permutations under each of three policies: 16
   new episodes. Update total to 1,016 and period records to 121,920. Update
   the candidate-scoring upper bound to 5,921,280.
2. **Noise-stream statement:** replace the claim that draw count/order can
   diverge with the actual per-coordinate draw contract. State that positive
   sigma aligns Gaussian innovations by `(period,agent,skill)` for equal
   geometry/horizon and seed; sigma zero consumes none, and shared innovations
   do not imply shared observations or trajectories.
3. **Hypothesis estimands:** list the H1–H3 within-bundle difference-in-
   differences above and make their replicate-level uncertainty summaries
   explicit. No new conditions or mechanism controls are required.
4. **Sequence digest:** define the canonical serialization before hashing,
   rather than saying only “serialized sequence digest.” Use UTF-8 compact
   JSON with sorted object keys, `allow_nan=False`, and ordered problem records
   containing ID, requirements, problem budget and CES weights; compute SHA-256
   over those bytes. This ensures the digest covers all exogenous fields while
   preserving sequence order.

These are mandatory reproducibility/estimand clarifications. An optional
future improvement would compare against another independently predeclared
fixed map, but it is not required here and should not expand this first study.

## 9. Decision

**ADJUST** for the reviewed commit `62a08df`. The scientific core is defensible
for an exploratory comparison, and the existing code supports its execution
without changing mechanisms. The four documentary corrections above are now
incorporated in the revised protocol; PI/CE must review that revision and
issue separate explicit campaign authorization before execution. Accepted limitations:
the reference is one role-aligned static dispatch rule; policy contrasts are
strategy-bundle comparisons; ORACLE is myopic and privileged; ADAPTIVE couples
statistical estimation, epsilon exploration and experience-driven productivity;
the individual-observation model is a stated instrumentation assumption; and
20 bundles are exploratory, not confirmatory. This review itself does not
authorize campaign execution.
