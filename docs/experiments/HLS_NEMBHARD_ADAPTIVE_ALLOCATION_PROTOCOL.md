# Exploratory protocol: fixed and adaptive Nembhard allocation

**Status:** protocol design completed as a documentary deliverable; not a
frozen confirmatory registration and not authorization to execute a campaign.
No experiment was run to prepare this document. HLS Laboratory remains
**PARTIAL**.

## 1. Research question and scope

**Main question.** Under what conditions does an adaptive work-allocation
policy outperform a predeclared fixed allocation when agents have heterogeneous,
complementary productivity profiles and productivity changes with accumulated
direct experience?

The comparison uses one mechanism throughout: the existing HLS adaptation of
Nembhard Direct. It compares a fixed role-to-task-type map, the current-period
perfect-information `nembhard_oracle`, and the observation-based
`nembhard_adaptive`. It does not compare Nembhard to MIS-v2, the contextual
quality–cost router, or historical HLS P0/P1/P2.

“Outperform” is evaluated separately for production, functional success, and
deficit. No universal score combines them. ORACLE ranks current-period actions
with true current productivity; it is not an optimal controller for cumulative
performance and is not expected to dominate every policy over a horizon.

## 2. Exploratory hypotheses

All hypotheses are nondirectional or conditional; ADAPTIVE superiority is not
assumed.

- **H1 — Heterogeneity moderation:** the paired ADAPTIVE-minus-FIXED contrasts
  in the three primary outcomes differ across homogeneous, mixed, and
  specialized productivity distributions, despite matched initial aggregate
  productivity by skill.
- **H2 — Learning-rate moderation:** those policy contrasts differ between
  faster and slower direct-experience curves when initial productivity and
  asymptotic productivity are held equal.
- **H3 — Temporal-order moderation:** the contrasts differ between
  interleaved and clustered orders of the same per-replicate problem
  collection. This estimates sensitivity to ordering, not to demand
  composition or average task frequency.
- **H4 — Observation-noise sensitivity:** within ADAPTIVE, decision and outcome
  summaries differ between zero and nonzero observation-noise conditions.
  Zero noise is not perfect information: only worked cells are observed and
  the online historical-mean estimator can lag a changing productivity rate.
- **H5 — Immediate versus cumulative criterion:** a policy ranking on the first
  period need not match its ranking on accumulated production, success, or
  deficit. This is descriptive and does not assert that any policy plans ahead.

The contrasts can be null or reverse direction. A positive ADAPTIVE-minus-FIXED
production contrast does not establish an advantage on success, deficit,
resource use, or other organizations and environments.

## 3. Organization and productivity profiles

Use **N=3, K=2** with stable role identifiers
`("skill1_role", "skill2_role", "generalist_role")`. Matrices below are
Nembhard asymptotic productivities `k[i,k]`, not HLS competence values.
Rows use that role order; columns are skill 1 and skill 2.

| Organization | `k[N,K]` |
|---|---|
| Homogeneous/generalist | `((1.2, 1.2), (1.2, 1.2), (1.2, 1.2))` |
| Mixed | `((1.8, 0.6), (0.6, 1.8), (1.2, 1.2))` |
| Complementary specialists | `((2.2, 0.0), (0.0, 2.2), (1.4, 1.4))` |

Every profile has `sum_i k[i,1] = sum_i k[i,2] = 3.6`. For both learning
conditions below, `p[i,k] = r[i,k]`, so at `D=0`,
`P[i,k](0)=k[i,k]/2`. Thus each organization also has the same initial
aggregate productivity, 1.8 output/work units per skill, as well as the same
aggregate asymptote. The distribution across agents differs by design. These
equalities do not imply equal output under a particular allocation.

For the predeclared FIXED map below, beginning-period output at `D=0` is:

| Profile | `skill1` / `skill2` single-skill output | `joint` output `(skill 1, skill 2)` | Initial functional outcome |
|---|---:|---:|---|
| Homogeneous | 1.2 / 1.2 | `(0.6, 0.6)` | Fails all three requirement types at the start. |
| Mixed | 1.5 / 1.5 | `(0.9, 0.9)` | Meets all three types at the start. |
| Specialists | 1.8 / 1.8 | `(1.1, 1.1)` | Meets all three types at the start. |

This deliberate distributional contrast is not an equal-allocation outcome:
aggregate productivity is matched, but the static task-to-role map places
different productivities on the executed cells. Later outcomes also depend on
the resulting exposure paths.

The Nembhard runner receives `OrganizationConfigNK` for identifiers and
resource constraints but does not use its HLS competence matrix as physical
state. If that API requires a competence placeholder, hold it fixed across all
conditions and exclude it from analyses. The physical state is `D[N,K]`,
initially all zero.

## 4. Learning dynamics and units

Use the implemented direct-experience law
`P[i,k](D) = k[i,k] * (D[i,k] + p[i,k]) / (D[i,k] + p[i,k] + r[i,k])`.
Production uses beginning-of-period productivity:
`y[k] = sum_i e[i,k] * P[i,k](D_t) * delta_t`.

Use period duration `delta_t=1 period` and exposure
`delta_D[i,k] = e[i,k] * delta_t`, as defined by the HLS adaptation.
`D`, `p`, and `r` use work-exposure units; `k` is output per work unit; task
requirements and output use the same declared output unit. The unit contract
is explicitly declared in every run. Resource limits constrain effort
intensity per period; experience exposure is recorded separately, even though
their numerical values coincide at `delta_t=1`.

| Learning condition | `p[i,k]` | `r[i,k]` | Interpretation |
|---|---:|---:|---|
| Faster curve | 1 | 1 | Same initial fraction and asymptote, faster increase per exposure. |
| Slower curve | 4 | 4 | Same initial fraction and asymptote, slower increase per exposure. |

These values apply to every cell. Since `p=r`, both curves begin at `k/2`
and approach the same `k`. From the implemented equation,
`dP/dD = k*r/(D+p+r)^2`; at `D=0,p=r`, this is `k/(4r)`, so the faster
condition has four times the initial slope of the slower one. This is a
mathematical consequence of the chosen parameters, not a new learning law.
There is no exact “learning off” level in the current Nembhard mechanism;
calling a very large `r` a no-learning control would only approximate one.

The execution contract evaluates output using productivity at the beginning
of each period, then updates experience. No within-period integral or
retroactive output is used.

## 5. Problems, demand, resources, and horizon

Each run has **120 periods** and three problem types. All use CES weights
`(0.5, 0.5)` for trace compatibility; CES is not a policy objective or a
primary protocol outcome.

| Problem ID | Requirements `(skill 1, skill 2)` | Resource budget |
|---|---:|---:|
| `skill1` | `(1.4, 0.0)` | 2.0 effort units/period |
| `skill2` | `(0.0, 1.4)` | 2.0 effort units/period |
| `joint` | `(0.7, 0.7)` | 2.0 effort units/period |

The organization-wide budget is 2.0 effort units per period and each agent's
limit is 1.0. Use the existing 3×2 default discrete catalogue: four
individual effort vectors and **64 ordered joint catalogue actions**; the
feasible subset is checked for each problem under both budgets. Set
`max_candidates=64` or greater; no pruning or truncation is allowed. Use
`delta_t=1`.

Two temporal-order conditions contain exactly 40 problems of each type in
every replicate:

1. **Interleaved / low persistence:** form 40 triples, each containing one
   `skill1`, one `skill2`, and one `joint` problem; independently permute each
   triple with one `random.Random(seed)` instance (shuffle a fresh triple 40
   times) and concatenate. The maximum same-type run is two across triple
   boundaries.
2. **Clustered / high persistence:** create six blocks, each 20 periods long,
   with each problem type appearing in exactly two blocks. Use a seeded
   choice from the lexicographically sorted set of unique permutations of
   `(skill1, skill1, skill2, skill2, joint, joint)` subject to adjacent blocks
   having different types. This finite set is constructed before selection;
   `random.Random(seed).randrange(len(valid_orders))` chooses the order. The
   result has long runs while retaining the exact same 40/40/40 collection.

The sequence builder is a small protocol-level preparation step, not a new
demand mechanism. It must deterministically materialize the 120
`ProblemSpecNK` objects, preserve IDs/requirements/weights/budgets, record the
seed and serialized sequence digest, and assert the counts and run-length
condition before any model run. Pass the frozen list through the runner's
existing explicit-`problems` interface. Do not use policy-specific demand
generation. This is preferable to IID/Markov sampling here because those
generators do not guarantee exact per-replicate counts.

The two sequences in each paired replicate use the same task catalogue and
same counts, but different order. All three policies receive byte-identical
sequences within each order condition. No organizational outcome feeds back
into task generation.

## 6. Policy definitions

### FIXED — predeclared static role-to-task-type assignment

The assignment table is frozen before outcomes and used unchanged across all
profiles, learning conditions, demand seeds, and periods. It uses only the
current task type, never experience, productivity, observations, results,
future tasks, or a fitted parameter:

| Problem type | Allocation `(skill 1, skill 2)` by role | Total effort |
|---|---|---:|
| `skill1` | `skill1_role=(1,0)`, `skill2_role=(0,0)`, `generalist_role=(1,0)` | 2 |
| `skill2` | `skill1_role=(0,0)`, `skill2_role=(0,1)`, `generalist_role=(0,1)` | 2 |
| `joint` | `skill1_role=(1,0)`, `skill2_role=(0,1)`, `generalist_role=(0,0)` | 2 |

This is a static, task-type-to-role map, not a single allocation repeated for
incompatible task types. It is deliberately the same rule for every profile
and is not selected after inspecting results. It has no router, no observation
stream, and no policy memory. Its role labels are part of the predeclared
design.

### ORACLE — `nembhard_oracle`

Enumerates the same feasible 64-action catalogue and selects with the shared
functional-effort lexicographic rank: success, lower normalized deficit,
larger functional margin, lower effort; stable catalogue order breaks exact
ties. It sees true current `D` and true `k,p,r` and predicts only current
period production. It does not value future experience. This is a
perfect-information current-period reference, not a long-horizon upper bound.

### ADAPTIVE — `nembhard_adaptive`

Uses its per-cell online productivity estimates, reconstructed experience,
current problem, and resources; true `k,p,r` and true productivity remain
hidden from its decision view. Set the same initial estimate `0.6` for every
cell in both observation conditions. This is the initial mean productivity
per agent implied by the matched aggregate profile totals, not an estimate
derived from an agent's true profile. Set `epsilon=0.05` in both conditions;
exploration is uniform over feasible catalogue entries (including the greedy
action), using its independent seeded stream.

| Adaptive observation condition | `observation_noise_stddev` | Meaning |
|---|---:|---|
| Noiseless selected-cell feedback | 0.00 output units | No added measurement noise; only worked cells are observed and estimates remain history-dependent. |
| Noisy selected-cell feedback | 0.05 output units | Gaussian noise on individual work outputs; this is not noise on productivity directly. |

With minimum feasible positive work 0.5, the latter corresponds to a
per-observation productivity-noise SD of 0.1 when work is 0.5 (and 0.05 when
work is 1.0), before the running-mean update. The estimator is the implemented
Welford historical mean, not a curve estimator; it may lag as `P(D)` rises.
`epsilon` is held constant to separate observation-noise sensitivity from
exploration-rate changes. Noiseless feedback is still imperfect information,
and `nembhard_oracle` versus ADAPTIVE confounds policy rule with information
access; that comparison is an algorithmic reference contrast, not a pure
information treatment.

## 7. Design matrix, pairing, and execution count

The crossed factors are:

| Factor | Levels |
|---|---|
| Initial productivity distribution | Homogeneous, mixed, complementary specialists (3) |
| Direct-experience scale | Faster (`p=r=1`), slower (`p=r=4`) (2) |
| Demand temporal order | Interleaved, clustered; exact same task counts within replicate (2) |
| Decision condition | FIXED, ORACLE, ADAPTIVE-noiseless, ADAPTIVE-noisy (4 arms; noise applies only to ADAPTIVE) |
| Replication | 20 paired seed bundles (exploratory) |

This gives `3 × 2 × 2 × 4 × 20 = 960` primary episodes, each 120 periods
(115,200 period records). Add a bounded exploration sensitivity slice for
the mixed profile, faster curve, clustered order: compare `epsilon=0` with
the primary `epsilon=.05` for both observation-noise levels over the same 20
replicate bundles (**40 additional episodes**). Also run a bounded catalogue-
order diagnostic: one mixed/fast/interleaved seed bundle, all six permutations
of agent rows/IDs with profiles, resource limits, and FIXED role allocation
permuted together, FIXED/ORACLE/ADAPTIVE (`epsilon=0`, `sigma=0`) (**18
episodes**). This is a tie/order diagnostic, not another replicate or basis
for population inference. The proposed total is 1,018 episodes (122,160
period records). Each paired replicate creates the
interleaved and clustered sequence from its demand-seed bundle. For the same
profile, learning level, replicate, and order, all four primary arms receive
the exact same frozen demand path. Adaptive noise conditions share the
replicate's exploration seed; all adaptive arms share the initial estimate
and epsilon unless the exploration sensitivity slice sets epsilon to zero.
ORACLE and FIXED are deterministic conditional on frozen inputs and need not
be rerun to create fake independent replicates.

Use 20 independently numbered seed bundles `r=0,...,19` with master seed
`20261017`. Derive the input seeds exactly as `master + 10000*r + 1` for the
interleaved-order builder, `master + 10000*r + 2` for the clustered-order
builder, `master + 10000*r + 3` for adaptive observations, and
`master + 10000*r + 4` for adaptive exploration. Store the actual integer
seeds, not only the master seed. Demand construction, observation noise, and
exploration are separate streams. The
same demand path is replayed across policies; the same observation and
exploration seed values are used for paired adaptive noise conditions. The
noise-free implementation consumes no Gaussian draws, so this is not a
shared-noise-draw comparison at `sigma=0`; exploration remains aligned because
it has an independent stream. Do not claim equal seed values alone guarantee
comparable random draws across different code paths.

Twenty replicates are an exploratory compromise, not a power calculation or
confirmatory sample-size justification. The randomized schedule builder gives
some demand-path variation while preserving exact composition. The estimand
is conditional on the declared profile, task, budget, sequence-builder, and
seed distributions; it does not represent a population of organizations.
The design entails at most 5,928,960 catalogue-candidate scoring operations
across ORACLE and ADAPTIVE (64-candidate upper bound, before per-problem
feasibility filtering), and 122,160 period records. This is a count-based
feasibility estimate, not a runtime benchmark or permission to execute.

## 8. Metrics and aggregation

Retain period-level Nembhard traces, and derive the following without
redefining production, functional success, or CES:

### Primary outcomes

1. **Cumulative task-relevant production:**
   `sum_t sum_{k: requirement[t,k] > 0} output[t,k]`, in task-output units.
   Also report skill- and problem-type-specific totals. Report all-dimension
   physical output separately so output on a non-required skill is not
   mistaken for task-relevant production.
2. **Functional success proportion:**
   `sum_t 1(success[t]) / 120`, a fraction in `[0,1]`.
3. **Cumulative normalized functional deficit:**
   `sum_t FunctionalResult.normalized_deficit[t]`, dimensionless; also show
   its per-period mean. The implementation sums normalized shortfalls only
   over positive requirement dimensions.

### Secondary descriptive outcomes

- Cumulative per-period effort consumption `sum_t sum_i,k e[t,i,k]`, reported
  as a sum of the runner's declared per-period effort amounts; report
  effective work exposure `sum e*delta_t` separately in exposure units. They
  have the same numeric value at `delta_t=1` but remain distinct quantities;
  neither is monetary cost.
- Actual `D[i,k]` trajectories and final experience by agent/skill, in work
  exposure units; report cell values and descriptive means/ranges/variances,
  not a new concentration index.
- True `P[i,k](D_t)` trajectories from `productivity_before`, in output/work
  units; show per-cell curves and end-minus-start values.
- Allocation shares by agent, skill, and problem type; include unused
  collective capacity. Do not interpret contribution shares as causal
  contribution to collective success.
- Period/block-wise production, success, and deficit, especially the first
  periods after each demand-type transition. This separates immediate
  performance from cumulative outcomes and describes recovery without
  treating a block boundary as an endogenous adaptation event.
- For ADAPTIVE, predicted output versus realized output by skill, signed and
  absolute errors in output units, estimator means/counts/dispersion, and
  exploratory-decision frequency. For ORACLE, predicted-versus-realized
  current output should agree under its declared perfect-information model;
  this is an implementation check, not a policy outcome. FIXED has no
  predicted-output metric.
- Gross CES may be retained as a secondary legacy diagnostic with its own
  formula and weights. It is not a decision criterion, not net utility, and
  not a substitute for the three primary measures.

## 9. Planned contrasts and analysis

The experimental unit is a complete 120-period episode; pairing/blocking is
by replicate bundle and frozen demand path. For every profile × learning
level × demand-order × replicate, compute:

- `ADAPTIVE(σ=0) − FIXED` and `ADAPTIVE(σ=.05) − FIXED` for each primary
  outcome;
- `ORACLE − FIXED` as a current-period-perfect-information policy reference;
- `ADAPTIVE(σ=.05) − ADAPTIVE(σ=0)` using common demand and the same
  replicate-level observation/exploration seed values. These are paired seed
  conditions, not guaranteed common-random-number trajectories: selected
  cells and the number/order of Gaussian draws can diverge after decisions
  diverge, so do not describe the normal draws themselves as aligned;
- clustered-minus-interleaved contrasts within the same seed bundle and
  policy arm.

Then examine moderation of ADAPTIVE-minus-FIXED by organization profile,
learning scale, order, and observation noise. Report first-period contrasts
separately from full-horizon contrasts. Do not interpret ORACLE-minus-FIXED
as the value of perfect information alone because policy and information
access differ.

For each contrast/outcome report all paired values, mean and median paired
difference, and a 95% uncertainty interval. A paired t interval for the mean
may be shown with its assumptions; with 20 blocks, also show a paired bootstrap
interval (10,000 resamples of replicate bundles) and do not rely on it as a
confirmatory test. Report the proportion of pairs in each direction. These
intervals quantify uncertainty under the declared seed/schedule sampling,
not variability across all possible organizations or worlds. Do not collapse
between-scenario spread into a standard error.

This is exploratory: no confirmatory alpha, power claim, or winner selection
is registered here. If p-values are later requested, apply Holm adjustment
within each primary-outcome family across the predeclared policy and
moderation contrasts, disclose the full family, and treat adjusted
significance as insufficient evidence of scientific importance. A result
must be described outcome-by-outcome. Do not call a policy globally superior
when the primary measures trade off.

## 10. Controls, risks, and sensitivity checks

| Risk | Control / interpretation boundary |
|---|---|
| ORACLE's artificial information advantage | Report its true profile/experience access explicitly; use it as a myopic benchmark only, not as a fair same-information policy or long-run optimum. |
| FIXED chosen to favor a result | Freeze the role-to-task map above before execution; use the same map/profile role ordering in every condition; never tune after observing outcomes. |
| Numeric-index tie-breaking | Preserve the current stable catalogue ordering. As a sensitivity check, relabel all three agent rows/IDs under all six permutations for a prespecified subset, permuting profiles, resources and fixed roles together; report any decision/result dependence rather than averaging it away. |
| Horizon dependence | Predeclare 120 periods as the primary horizon; report first-period and blockwise traces. A different horizon is a sensitivity run, not a post-hoc replacement. |
| Epsilon exploration | Hold epsilon at .05 in both noisy/noiseless ADAPTIVE arms; report exploratory selections and resource/output effects. Do not attribute their effects solely to observation noise. |
| Running-mean lag and zero-work cells | Report counts, estimator errors and unobserved cells; do not use the true profile to initialize estimates. Noiseless output does not remove partial-observation or estimator lag. |
| Learning induced by allocation | Treat experience paths as endogenous mediators/outcomes. Do not force paths to match: the allocation is the treatment and changes exposure under the existing law. |
| Different trajectories after same start | Hold initial state, profile parameters and exogenous problem sequence fixed within each policy contrast; allow action, observation, experience, and estimate paths to differ. |
| Initial architecture advantage | Aggregate initial and asymptotic `k` are matched per skill, but cell-level distribution and role alignment differ intentionally. Report period-1 outcomes separately; do not call equal sums full equivalence. |
| Demand process / temporal order | Use frozen explicit sequences with exactly 40 of each problem type; hash them and verify counts/order constraints before all runs. No policy can change demand. |
| Output vs utility and effort vs cost | Keep output, functional evaluation, gross CES, effort, exposure, and any economic cost distinct. This protocol has no monetary cost variable. |

## 11. Feasibility with current code

### Supported without simulator changes

- N=3, K=2 organization/resource geometry and `ProblemSpecNK` with the
  requirements and budgets above.
- Nembhard Direct profiles `k,p,r`, `D=0`, duration 1 and unit contract.
- Explicit fixed allocations and automatic ORACLE/ADAPTIVE via
  `run_nk_production_sequence(..., mechanism_id="nembhard_direct", ...)`.
- Existing K=2, N=3 ordered 64-action catalogue and `max_candidates=64`.
- ADAPTIVE initial scalar productivity estimate, epsilon, independent
  observation/exploration seeds, noise, estimator and diagnostics.
- Frozen explicit `ProblemSpecNK` sequences replayed identically across
  policies. `NKNembhardDirectRunResult` records output, success/deficit,
  effort, exposure, true experience/productivity, router predictions and
  observations as applicable.
- Common result envelope adapter `adapt_nembhard_run` /
  `adapt_experiment_run`, with caller-supplied sequence, seeds, configuration,
  and software-revision provenance where absent from the native result.

### Preparation adapter / limitations

- No existing N×K generator guarantees exact 40/40/40 composition with both
  requested order constraints. A small deterministic sequence-materializing
  script or checked-in input manifest is needed; it must only prepare frozen
  explicit `ProblemSpecNK` data and must not alter simulator physics.
- The runner's adaptive observation model supports individual agent-skill
  output observations, not only aggregate observations. Results apply to this
  instrumentation condition.
- The current ADAPTIVE mean estimator does not estimate curve parameters and
  is not a formal uncertainty-aware learner. Epsilon-greedy exploration is
  heuristic and not optimized.
- The runner does not support Nembhard plus MIS-v2, teaching, historical
  P0/P1/P2, or imperfectly observed Nembhard profile parameters. They are not
  needed for this protocol.
- `ProblemSpecNK`/Nembhard functional evaluation admits task-specific active
  dimensions; inactive dimensions have zero requirements. Output-unit
  calibration remains a caller-attested contract and must be checked before
  launch.

No simulator code, estimator, router, equation, historical result, or frozen
artifact needs to change. The protocol is implementable with a sequence
preparation adapter and the existing execution/tracing API. Before campaign
execution, the PI/CE must separately review/freeze this document, validate the
unit calibration and sequence builder, and issue explicit execution
authorization. This document itself grants no such authorization.

## 12. Interpretation and limitations

Supported conclusions are conditional statements about the three declared
profiles, two Nembhard exposure scales, three problem types, two frozen order
classes, given resource/catalogue constraints, and selected-observation
assumptions. The design can reveal whether policy contrasts change with
heterogeneity, experience timing, demand order, or observation noise in this
simulator.

It cannot establish universal superiority of adaptive assignment, optimality
of ORACLE over a horizon, a real-world causal effect, general organizational
learning, teaching effects, monetary efficiency, cross-route comparability,
or reproduction of the complete Nembhard–Bentefouet model. Its small
exploratory replication count is not a confirmatory evidentiary standard.

## 13. Source and contract references

- Nembhard mechanism and output-unit convention:
  `src/hls/hls_lab_nk_nembhard.py`;
  `docs/engineering/HLS_EXTERNAL_MECHANISM_INTEGRATION_01.md`.
- ORACLE information/rank/action contract:
  `src/hls/hls_lab_nk_nembhard_router.py`;
  `docs/engineering/HLS_NEMBHARD_ORACLE_ROUTER.md`.
- ADAPTIVE observation, Welford estimator and decision boundary:
  `src/hls/hls_lab_nk_nembhard_adaptive.py`;
  `docs/engineering/HLS_NEMBHARD_ADAPTIVE_ROUTER.md`.
- Runner, records, direct/exogenous sequence routes:
  `src/hls/hls_lab_nk_execution.py`.
- Problem/resource geometry and 64-action catalogue:
  `src/hls/hls_lab_nk_geometry.py`.
- Existing environment generator and its limits:
  `src/hls/hls_lab_nk_environment.py`.
- Common result/tracing envelope:
  `src/hls/experiment_contract.py`;
  `docs/engineering/HLS_COMMON_EXPERIMENT_CONTRACT.md`.
- Nembhard regressions:
  `tests/test_hls_lab_nk_nembhard.py`,
  `tests/test_hls_lab_nk_nembhard_oracle.py`,
  `tests/test_hls_lab_nk_nembhard_adaptive.py`.
