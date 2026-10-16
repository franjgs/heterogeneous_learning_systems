# HLS Laboratory configurable N×K geometry — technical design

**Design started:** 2026-10-16 11:26 +02:00. **Recorded:** 2026-10-16 11:37 +02:00 (Europe/Madrid).
**Design repository baseline:** `feature/hls-laboratory-v1`, `4940d4b22d7ea67e49b0f55f9e8afac37c4850da`.
**Phase 1 implementation baseline:** `feature/hls-laboratory-v1`, `bca73727e8719e2ec27d180dfa9ecbaf6cd5b9cd`.
**Status:** Phase 1 implemented additively; execution/generalized learning and policies remain held.

## 1. Decision summary

The current laboratory is not dimension-generic: it is a fixed three-agent,
two-competence implementation in the DISCOVER-v0-compatible path. The
minimum safe extension is an additive, dimension-aware integrated path whose
legacy `N=3, K=2` route delegates to the existing catalog, production,
evaluation, MIS-v2, estimator, tie-breaking, and serialization behavior. Do
not modify frozen DISCOVER-v0 / MIS-v2 contracts to make them generic.

**Implementation outcome:** dimension-independent organization/configuration
and problem contracts plus explicit productive-allocation enumeration are
implemented in Phase 1. The 3×2 route remains delegated to DISCOVER-v0 and the
existing integrated runner. N×K execution, policies, MIS-v2/teaching
transitions, estimation and environment emission are not generalized. The
pre-existing full-suite provenance failures remain separate; no historical
artifact or expected hash was modified.

## 2. Current assumptions found in code

| Layer | Fixed assumptions and evidence | Generalization needed |
|---|---|---|
| Canonical production state/catalog | `discover_v0.py`: `N_AGENTS=3`, `N_CAPABILITIES=2`; `State` is a three-row/two-column tuple; `INDIVIDUAL_ACTIONS` is exactly `(0,0)`, `(0,1)`, `(.5,.5)`, `(1,0)`; `JOINT_ACTIONS` is their Cartesian product, 64 ordered actions. `validate_state/action`, `production_inputs`, and `ces_reward` enforce this shape. | Keep these public definitions frozen. Add dynamic integrated types and helpers for other geometries, with a strict legacy delegation for 3×2. |
| Problem and team | `hls_lab_v1.py`: `ProblemSpec.requirements` and `ExpertState` vectors are length 2; `TeamState` requires exactly 3 distinct experts; `evaluate_problem` has two-vector outputs; `complementarity_class` loops over three experts. A single scalar `max_effort_per_expert` applies to all agents. | Shape-check `N≥1`, `K≥1`; ordered stable agent/skill IDs; optional per-agent limits with legacy scalar shorthand; requirements length K. |
| Integrated action / teaching | `hls_lab_v1_integrated.py`: `TeachingEvent` validates indices in `range(3)` and skills in `range(2)`; `TeachingEfficacy` is 3×3×2 and zeros the diagonal; action production aliases the fixed `JointAction`. The enumerator loops over 3×3×2 directed relations and charges both participants. | General `N×N×K` relation efficacy and dynamic indices; retain distinct instructor/learner and one event maximum. In N=1 no directed teaching action exists. |
| Learning / estimation | `hls_lab_dynamic.py`: `LearningProfile.eta` is 3×2; `make_dynamic_team`, state validation and `advance_team` use fixed dimensions. Posterior matrix initialization/extraction and integrated observation loops also use 3×2. `discover_develop_v2.mis_v2_transition` accepts only fixed DISCOVER state/action types; scalar `capability_after_exposure` implements the underlying MIS-v2 cell law. | Dynamic N×K parameter and posterior matrices; call the existing scalar MIS-v2 transition law per exposed cell in the additive path. Preserve transition order, bounds, observation update and noise coordinates. |
| Production / metrics | Current production is additive by skill: `Y_k=Σ_i x_ik c_ik`; functional success, normalized deficit and margin use the active requirement coordinates. CES implementation in `discover_v0.ces_reward` explicitly accepts two outputs/weights. | Dimension-loop versions of output and functional metrics; a K-weight CES with the same `rho=0.5` contract. K=2 must call the legacy function or be proven numerically identical. Do not add team synergy. |
| Policies / memory | P0/P1/P2 share `IntegratedPolicy`/`IntegratedDecisionView`, but view requirement/competence annotations, loops and action keys assume two skills/three agents. P2 memory relations use integer indices and can extend naturally when dimensions are runtime supplied. | Keep the policy protocol; make its views dimension-generic. Maintain old candidate ordering so `max`/first-tie choices are preserved. Validate every policy action against the run’s generated feasible catalog. |
| Exogenous demand | `hls_lab_v1_environment.py` reuses C5 processes but emits via fixed two-skill `DemandRegime` and `generate_problems` in `hls_lab_dynamic.py`; latent process itself accepts hashable task states. | Reuse C5 transitions and random streams; make only the state-to-problem emission map K-dimensional. Avoid a second demand-process implementation. |
| Trace / serialization | `IntegratedEpisodeRecord` stores fixed-size typed tuples; `production_action_id` is `JOINT_ACTIONS.index(action)`; serialization writes array order and fixed action IDs. Noise seeds use integer agent/skill indices. | Stable ordered IDs and dimension-shaped arrays. Preserve old schema and action IDs for exact 3×2 path; new geometry can use the same record fields with variable-length arrays, with a schema version only if a necessary new field is introduced. |

These are structural dependencies, not just defaults: static type aliases are
not the principal blocker; validation, enumeration, arithmetic loops,
estimators and identifiers actively reject or iterate fixed dimensions.

## 3. Target data contract

Use immutable, ordered configuration and state objects (nested tuples are
sufficient; no array library is needed):

```text
OrganizationConfig:
  agent_ids: tuple[str, ...]                 # N unique ordered identifiers
  skill_ids: tuple[str, ...]                  # K unique ordered identifiers
  competence_initial: tuple[tuple[float,...],...]  # N×K, each in [0,1]
  estimates_initial: optional N×K matrix
  effort_limits: tuple[float,...]             # N, nonnegative
  learning_rates: tuple[tuple[float,...],...] # N×K; MIS-v2 eta contract
  teaching_efficacy: tuple[N][N][K]           # private truth; diagonal zero

ProblemSpecNK:
  requirements: tuple[float,...]               # K nonnegative values; at least one >0
  resource_budget: float                       # one shared nonnegative budget
  effort_limits: tuple[float,...]              # N; or legacy scalar expanded to N

Allocation:
  tuple[tuple[float,...],...]                  # N×K, selected from configured catalog

TeachingEvent:
  instructor_index, learner_index, skill_index, effort
```

Keep real state, estimates/posteriors, observation noise, private teaching
efficacy, and policy memory separate. The public decision view contains only
the current problem, public budgets/limits, estimated competencies and
posterior uncertainty, memory-derived efficacy estimates, and feasible
actions. It must not contain real competence, true efficacy, future problems,
or latent environment state.

Per-agent effort loads are `sum_k x[i,k]` plus teaching effort for each
participating instructor/learner. The shared-period resource constraint is
`sum_i,k x[i,k] + 2e·1(teaching) ≤ B`. This preserves the existing assumption
that both parties consume teaching time and can still contribute production
within their residual per-agent caps. No extra opportunity penalty is added.

## 4. General action catalog and complexity

Represent each productive allocation as an explicit N×K effort matrix drawn
from a declared per-agent allocation catalog. Keep the existing action
templates and ordering as the default **only for K=2**. For other K, require
an explicit catalog in configuration (or a separately documented neutral
default); do not extrapolate the two-skill half/half option into an
undocumented arbitrary simplex/grid. Each joint productive action is the
ordered Cartesian product of one permitted per-agent vector, filtered by
individual limits and shared budget.

Let `M(K)` be the number of configured per-agent effort vectors. Exhaustive
production enumeration has at most `M(K)^N` joint allocations. With at most
one directed teaching event, there are `N(N−1)K` candidate relationships, so
the unfiltered integrated candidate bound is
`M(K)^N × [1 + N(N−1)K]`. With per-action production loads computed once in
O(NK), each lesson relation can be checked in O(1) and attached to the shared
production allocation; generation time is O(`M(K)^N × [NK + N²K]`) and stored
catalog size is O(`M(K)^N × [1 + N²K]`). Recomputing loads or copying each
N×K allocation for every relation adds avoidable factors; the exact simple
enumerator can precompute loads without changing action order. Feasibility
filtering usually reduces the catalog, but does not change the worst case.
For the legacy catalog, N=3,
K=2, M=4: 64 productive actions and at most 832 production-plus-lesson
candidates before resource filtering.

This is exponential in N and catalog size. That is acceptable for a small
exact laboratory and keeps policy comparison transparent. Do not silently
truncate or replace exhaustive enumeration. An explicit user-configured
catalog-size guard may fail early with the estimated count; scalable/lazy
action generation is future work and is not part of this design.

## 5. Exact 3×2 compatibility contract

Treat compatibility as a regression obligation, not merely equality of mean
outcomes. For the existing fixtures/configuration, preserve:

1. Ordered agent IDs and row order; ordered skill coordinates and all
   competence/learning/effectiveness values.
2. Per-agent catalog order, then `itertools.product` joint action order;
   the exact 64 DISCOVER actions, action IDs, feasible integrated action order,
   and first-in-catalog tie breaks.
3. The additive production sum order, threshold tolerance, normalized-deficit
   denominator, margin definition, CES `rho`, and weights.
4. P0/P1/P2 selected actions for identical views/memory; MIS-v2 scalar law,
   per-period transition order (production → MIS-v2 → teaching), teaching
   efficacy indexing, saturation/bounds, posterior updates, observations,
   and resource totals.
5. Noise key strings/version and coordinates `(seed, period, stream, agent,
   skill)`; adding dimensions must not change draw assignment in 3×2.
6. Exact serialized trace bytes for fixed historical fixtures, if the output
   serializer itself is unchanged. Also pin key JSON/CSV outputs and hashes
   for the integrated demos/tests where these are already contractually
   frozen.

Byte-for-byte compatibility is achievable if the legacy 3×2 path retains the
current serialization schema, field ordering, action IDs, float formatting,
and random-key derivation. It is not achievable if the implementation
unconditionally adds N/K metadata or changes scalar-vs-vector serialization;
such metadata would require a versioned schema and explicit approval, while
numerical and decision equivalence must remain exact. Prefer the compatibility
fast path to avoid that break.

## 6. Smallest file-level implementation plan

| Step | Files | Minimum change | Acceptance / stopping point |
|---|---|---|---|
| 1. Add generic geometry contracts | `hls_lab_v1.py` | Add dimension-aware organization/problem/allocation types and validators alongside frozen 3×2 aliases/functions. Optional per-agent effort limits expand from the existing scalar default. | Shape/bounds/ID failures are explicit; old constructors and tests remain valid. Stop if the required backwards-compatible API cannot be kept additive. |
| 2. Generalize catalog/evaluation helpers | `hls_lab_v1.py`, `hls_lab_v1_integrated.py` | Add dimension-generic production aggregation, functional evaluation and configured catalog filtering. Keep `discover_v0` helpers for legacy route and delegate at N=3,K=2. | Exact equality to legacy 3×2 values/actions/order on fixtures; generic N=1,K=1 and N=2,K=2 evaluate correctly. |
| 3. Generalize organization and transitions | `hls_lab_dynamic.py`, `hls_lab_v1_integrated.py` | Add N×K `LearningProfile`, agent/team validation, estimator matrices and per-cell production observation loops. Apply existing scalar MIS-v2 cell transition; preserve direct teaching equation/ordering. | Every skill cell updates only under its declared exposure; zero exposure and disabled mechanisms preserve state; no access to private truth by policies. |
| 4. Generalize teaching feasibility and memory | `hls_lab_v1_integrated.py` | Generate all `N(N−1)K` one-lesson relations and account both participant loads plus shared budget. Validate efficacy tensor N×N×K. | N=1 admits no lesson; N=2 permits directed relations; all action ledgers balance, diagonal efficacy is zero. |
| 5. Adapt policies and environment emission | `hls_lab_v1_integrated.py`, `hls_lab_v1_environment.py`, minimal runner/test adaptations | Generalize P0 score dimensions; P1/P2 relation indices and memory; map reused C5 task states to K-requirement emissions without passing latent state. | Existing P0/P1/P2 behavior exact in 3×2; same frozen environment path delivered to each policy; new K path reproducible. |
| 6. Serialization and explicit regression gate | integrated serialization module/function, tests and scoped demo only | Preserve legacy schema/IDs for 3×2; allow rectangular nested arrays for other geometries; pin deterministic trace comparisons. | Exact legacy trace bytes and full specified N×K test matrix; no frozen historical artifact is regenerated. |

Indispensable: dimensioned state/config, effort-vector catalog, generic
feasibility/production/evaluation, MIS/estimator loops, dynamic teaching
relations, policy views, and dimension-preserving serialization. Optional:
moving old public aliases into a new module, typed catalog classes, and
performance optimizations. Avoid plugin frameworks, multi-task queues,
non-additive production, new policies, and scalable optimizers.

## 7. Test matrix

| Case | Required checks |
|---|---|
| N=1, K=1 | Initial/estimate bounds; allocation and production; no directed teaching candidates; shared/per-agent budgets. |
| N=2, K=2 | Distinct agent IDs; catalog Cartesian product; both directed instructor–learner relations per skill; correct resource accounting. |
| N=3, K=2 | Exact historical 64 production actions and order; integrated candidate order; P0/P1/P2 decisions/ties; MIS-v2, teaching, estimator, CES, functional result, noise, resource and serialized trace regression. |
| N=4, K=3 | Rectangular states; three-dimensional requirements and CES weights; relation tensor; deterministic action and trace reproduction. |
| Unequal effort limits | Each actor’s production + teaching load checked against their own limit; shared total checked independently. |
| Competence boundaries 0 and 1 | Validation; MIS-v2/teaching saturation; no value outside [0,1]; posterior moments finite. |
| Invalid dimensions/configs | N=0/K=0, ragged matrices, duplicate IDs, wrong rates/weights/catalog shape, NaN/negative values, invalid relations rejected. |
| Action/resource conservation | Every returned action belongs to declared catalog; production + two-party teaching ≤ budget; individual loads ≤ limits; unused capacity is nonnegative and reported. |
| Deterministic reproduction | Same config, environment seed, and indexed innovation keys produce byte-identical outputs; different organization states cannot alter frozen demand. |

P0’s current functional ranking and P1/P2 relation/memory rules can
generalize structurally. MIS-v2’s *scalar cell update* and the teaching
transition formula can be reused without new learning semantics. The current
state/action wrapper `mis_v2_transition`, DISCOVER-v0 action validator, and
current CES/functional evaluators cannot directly accept arbitrary N×K.
Teaching generalizes only if relationship efficacy is supplied as a complete
N×N×K private tensor and public estimates/memory use the same index mapping;
no alternative relation/transfer semantics is proposed.

## 8. Risks and authorization boundary

- **Action ordering/ties:** a single catalog-order difference can alter P0/P2
  choices. Highest technical compatibility risk.
- **Exponential enumeration:** exact all-actions views eventually become
  impractical. Do not mask this with undocumented truncation.
- **Dimension-mismatched demand:** emitting only K=2 problems would make the
  generic organization path superficial; environment emission must validate
  K explicitly.
- **Physical scope:** the extension retains additive output and the existing
  discrete effort semantics; it does not add synergy, task queues, or a new
  objective.
- **Provenance (design-time status):** the earlier audit reproduced 13
  failures. Two authorized validator fixes reduced that baseline to five; the
  Phase 1 final suite still has those same five (B13 inventory, pre-existing
  `finite_problem_belief.py` hash differences and Campaign 2 closure-document
  hashes). No such evidence was edited for N×K work.
- **Data format:** existing result rows are a historical contract. Avoid
  unconditional metadata/schema changes for the legacy path.

No maximum N/K is scientifically justified here. Practical applicability is
bounded by exact catalog enumeration, not by a hidden agent/skill restriction.
Any runtime/catalog guard should be based on the computed number of actions
and fail transparently; it must not silently reduce the feasible set.

## 9. Phase 1 implementation record

**Implementation date:** 2026-10-16; the verified completion timestamp and
validation are recorded in `HISTORY.md`. **Scope:** dimensioned state,
problem, resource configuration and productive action geometry only.

Implemented additively in `src/hls/hls_lab_nk_geometry.py`. This is a
documented deviation from the initial file-level suggestion: historical
Campaign 1 and diagnostics manifests hash `hls_lab_v1.py` and
`hls_lab_v1_integrated.py`; editing either module creates unrelated integrity
failures even if runtime behavior is unchanged. The separate module preserves
both source files byte-for-byte and keeps the Phase 1 boundary explicit.

- `OrganizationConfigNK`, `OrganizationStateNK`, and `ProblemSpecNK` validate
  non-empty unique ordered identifiers, N×K competence/estimate shapes,
  competence bounds `[0,1]`, K-dimensional non-negative requirements,
  per-agent limits, and non-negative shared budgets.
- Real competence and organizational estimates are stored separately. If an
  estimate is omitted, it follows the existing v1 perfect-information
  convention; no N×K policy currently consumes this state.
- `enumerate_productive_allocations_nk` enumerates a caller-declared ordered
  per-agent effort catalog, filters by each actor's effort limit and the
  minimum of organization/problem shared budgets, and returns catalog order
  (tuple index is the action identifier). K=2 defaults to DISCOVER-v0's
  individual action choices; other K requires an explicit catalog. The 3×2
  default path reads `JOINT_ACTIONS` directly.
- The caller must set `max_candidates`. The complete Cartesian size is
  calculated before enumeration; if it exceeds the guard, enumeration raises
  an explicit `ValueError` with the candidate count and does not truncate.
  Complexity is `M_1 × … × M_N` candidates and O(NK) feasibility work per
  candidate; worst-case time O(NK·∏M_i), with only feasible actions returned.

The new N×K types are separate from the 3×2 runner contracts and are not
accepted by `run_sequence` or `run_integrated_sequence`. Those runner modules
remain byte-for-byte unchanged. Existing `TeamState`, P0/P1/P2,
production/evaluation execution, MIS-v2, teaching, posterior updates, demand
emission and serialization remain 3×2; no transition equations or historical
contracts changed. N×K episode execution is unsupported in this phase and
must not be inferred from the geometry API.

**Compatibility evidence:** before editing, the frozen 64-action catalog,
the first-problem 508-action integrated catalog and deterministic three-step
P0/P1/P2 serialized traces were hashed and then pinned in
`tests/test_hls_lab_v1_integrated.py`. Their catalog hashes are
`b219314c…f2f5381` and `9ebc8196…b957e277d`; the trace SHA-256 values and
selected action IDs, teaching decisions, success, CES and resource totals are
asserted by the test. The full serialized bytes match those pre-change hashes.
Focused N×K geometry plus HLS v1/CE-23/24/25/environment tests passed 50/50
after implementation. Full-suite results are recorded in the dated history
entry and final validation record.

**Supported Phase 1 geometries:** any positive N and K for state/configuration
contracts; exact action enumeration for K=2 using the legacy effort choices,
and for arbitrary K when an explicit effort catalog is supplied. This is not
a claim of end-to-end N×K simulation. No arbitrary maximum N or K is imposed;
the explicit candidate guard lets callers fail before exponential enumeration.

**Phase 1 status at that record:** N×K episode execution was unsupported.
The later Phase 2 authorization and implementation are recorded below.

## 10. Phase 2 — production-only execution and dimension-independent P0

**Implementation/final validation:** 2026-10-16, recorded at 14:55 +02:00
(Europe/Madrid). **Scope:** frozen-competence N×K execution on an explicitly
supplied problem sequence, with perfect-information P0. MIS-v2, learning,
teaching, P1/P2, competence estimation and environment generation remain
unsupported for N×K.

Implemented additively in `src/hls/hls_lab_nk_production.py` and
`src/hls/hls_lab_nk_execution.py`; Phase 1
`OrganizationConfigNK`, `OrganizationStateNK`, `ProblemSpecNK`, validation
and enumeration remain the common geometry contracts. `ProblemSpecNK` now
also carries K normalized CES weights (uniform weights by default, preserving
the legacy 3×2 default). Stable catalog IDs are the indices in the full
unfiltered declared catalogue, including when a problem budget filters
candidates.

- Production is exactly additive: `y[k] = Σ_i allocation[i][k] ×
  competence[i][k]`. No synergy, stochasticity or resource conversion was
  added.
- `P0ProductionOnlyNK` uses the legacy lexicographic score
  `(success, −normalized_deficit, margin, −effort)` and first-in-catalog tie
  resolution. It does not rank by CES. In this Phase 2 path the estimate is
  explicitly set equal to the fixed real competence matrix, matching the
  legacy perfect-information control; configured alternative estimates are
  not consulted.
- The runner consumes a pre-generated ordered tuple of `ProblemSpecNK`; it
  makes no environment draws. Competencies and estimates stay fixed, and no
  learning/teaching/observation updates occur.
- Every period records gross CES, functional result, outputs, chosen
  allocation and stable action ID, per-agent effort, effective collective
  budget `min(organization budget, problem budget)`, unused collective
  capacity, limits, and equal before/after competence matrices. No net utility
  is formed.
- CES is the dimension-generic DISCOVER-v0 formula
  `(Σ_k weight[k] × output[k]^0.5)^2`; tests establish exact equality with the
  legacy two-skill function on representative values.
- The stable JSON serializer supports byte-identical replay for the same
  configuration and sequence. Legacy 3×2 serializer and source modules were
  not modified.

### Phase 2 compatibility and tests

The N×K runner was directly compared with legacy P0 on matched 3×2 states,
budgets and problems: selected catalog action, additive output, functional
success, normalized deficit, margin, CES, and productive effort matched
exactly. The pre-existing integrated regression continues to assert the
historical 64-production-action catalogue, 508-action integrated catalogue,
P0/P1/P2 decisions and serialized trace SHA-256 values. Focused laboratory
and CE-24/25 regressions passed **99 tests**; a broader run including DISCOVER
and RQ0 regressions passed **143 tests** before the final source-module
separation. After that separation, the focused suite passed **99 tests** and
the full suite passed 1,288 with the same five known provenance failures; see
`HISTORY.md` for their identities.

### Enumeration performance observation

On Python 3.11.9, macOS 27.0.1 arm64, one local non-scientific engineering
measurement used 1,000 timing repetitions per geometry and a separate
`tracemalloc` peak-allocation pass. The action catalogs were 2, 16, 64 and
256 candidates respectively. Average enumeration / P0 scoring time per run
was approximately 0.0054/0.0069 ms (1×1), 0.0509/0.0920 ms (2×2),
0.2011/0.2334 ms (3×2), and 1.0144/1.1329 ms (4×3); peak traced temporary
allocation was 2,344 / 6,312 / 21,640 / 89,672 bytes. These are local
implementation timings, not portable performance claims. Exhaustive work
remains O(NK × ∏M_i) for `M_i` configured per-agent effort choices; explicit
`max_candidates` rejects oversized catalogs before enumeration without
truncation.

**Supported now:** production-only N×K episodes and P0 for every positive N/K
whose complete declared action catalog fits `max_candidates`; K≠2 requires
explicit effort vectors per agent. The default K=2 choices and 3×2 catalog
ordering remain the Phase 1 DISCOVER contract.

**Still unsupported:** N×K MIS-v2 or any competence changes, teaching,
organizational estimation/partial-information policies, P1/P2, latent-state
environment generation, and stochastic production. The integrated historical
3×2 simulator continues to provide those mechanisms only in its original
geometry. HLS Laboratory remains **PARTIAL**.

## 11. Phase 3A — N×K MIS-v2 learning-by-doing

**Recorded:** 2026-10-16 15:50 +02:00 (Europe/Madrid). **Status:** implemented
additively; no historical module, fixture, result, manifest or expected hash
was changed. The statements above document the Phase 2 state and are
superseded for the specific N×K MIS-v2 capability by this Phase 3A record.

### Authoritative transition and dimensional mapping

The transition reuses `discover_develop_v2.capability_after_exposure` and
`eta_to_lambda`; the scalar scientific model was not copied or changed. For
agent `i` and competence `k`, given competence `c[i,k]`, productive effort
`e[i,k]`, and the existing one-unit gap-closure parameter `eta[i,k]`:

```text
lambda[i,k] = -ln(1 - eta[i,k])
c_next[i,k] = 1 - (1 - c[i,k]) * exp(-lambda[i,k] * e[i,k])
```

`eta` remains strictly inside `(0,1)`; zero learning is represented by
disabling MIS-v2, not by inventing `eta=0`. The transition is cellwise, has no
cross-agent/skill transfer or stochastic term, is the identity at zero effort,
and retains the original asymptotic competence saturation without clipping.
Its N×K parameter profile is one eta per agent × competence cell, exactly the
structure implied by legacy `LearningProfile.eta` (3×2). The legacy profile
and transition modules remain unchanged.

### Timing, information and runner contract

`run_nk_production_sequence` keeps its default MIS-OFF path and
`NKProductionRunResult` serialization unchanged. `individual_learning=True`
requires `LearningProfileNK` of matching shape and returns an
`NKLearningRunResult`. Each period uses current competence as the perfect-
information P0 estimate, then computes additive outputs, functional success,
gross CES and resource use from the pre-learning state. MIS-v2 is applied
after those outcomes to the selected productive allocation; the resulting
state is used by the next period. Learning does not consume extra effort and
does not retroactively affect same-period production. The trace nests the
Phase 2 production record and adds cellwise competence increments and eta.

This is explicitly a perfect-information condition, not a general HLS
assumption. Teaching, P1/P2, partial-information estimation, experience and
performance ledgers, and demand generation remain unsupported in the N×K
runner. MIS-OFF and MIS-ON on the same frozen sequence are a mechanism control,
not evidence of comparative scientific superiority.

### Validation and local engineering performance

At the final implementation check, 87 focused tests passed, including Phase 1
geometry, Phase 2 production, dynamic/integrated regressions, legacy teaching
and MIS-v2 tests, and new N×K transition/runner tests. Direct 3×2 transition
outputs agree exactly with legacy `advance_team`; a one-period P0/MIS-ON run
matches legacy action, production, success, CES, effort and competence update.
MIS-OFF result equality and serialized output are tested against the Phase 2
call contract. A paired OFF/ON regression also verifies a shared initial state
and sequence, identical first decision/outcome, and only subsequent divergence
after learning. The full suite result and identities of the five pre-existing
provenance failures are recorded in `HISTORY.md`; those failures are outside
this change.

Non-scientific local timings (Python 3.11, 20 periods, 100 episodes per size;
3,000 standalone transition repetitions per size) used, for each agent, a
small explicit catalogue containing zero effort plus one 0.25 effort vector
per skill. Candidate counts are the resulting full Cartesian catalogs before
feasibility filtering; they are not the canonical 3×2 64-action catalogue.
Measurements were:

| N×K | Enumerated catalog candidates | MIS transition / call (ms) | Episode / 20 periods (ms) | Traced peak memory (bytes) | Serialized trace (bytes) |
|---|---:|---:|---:|---:|---:|
| 1×1 | 2 | 0.003588 | 0.8209 | 27,512 | 14,424 |
| 2×2 | 9 | 0.007593 | 1.6784 | 43,288 | 19,384 |
| 3×2 | 27 | 0.005082 | 4.4684 | 65,568 | 22,932 |
| 4×3 | 256 | 0.007717 | 49.7467 | 244,544 | 31,232 |

These are local microbenchmarks, not portable performance guarantees. Episode
time includes full action enumeration and P0 ranking. The 4×3 increase is
consistent with the existing exhaustive catalog growth; no truncation or
optimizer was introduced.

**Supported after Phase 3A:** deterministic N×K production-only episodes
under P0 with MIS-v2 explicitly ON or OFF, positive N/K, and fully enumerated
catalogs within the declared candidate bound. K≠2 still needs explicit effort
vectors; all runs use perfect information. Legacy 3×2 P0/P1/P2, teaching,
estimation, and historical serialization remain on their original code path.
HLS Laboratory remains **PARTIAL**.

## Phase 4 — N×K environment and demand generation

**Status:** implemented additively; scientific campaigns remain held.

### Existing process contract retained

The authoritative environment is the C5 task-demand layer in
`src/hls/synthetic/c5.py`:

* `StationaryTaskDemand` samples IID task labels from its one validated
  distribution. “Stationary” is a process property, not a second generator.
* `NonStationaryTaskDemand` samples from the distribution indexed by the
  current integer period. It has no separate change-point estimator or
  endogenous trigger.
* `MarkovTaskDemand` samples the initial task from `initial_distribution`, then
  uses the row keyed by the previously realized task. It is first-order and
  its state depends only on the task history passed by the environment.
* The existing fixed-sequence path is an already-materialized sequence passed
  directly to the episode runner; it is not another stochastic process.

Every C5 process receives a seeded `random.Random` source from the v1
environment. Its `WorldState` argument is a constant environmental placeholder
and is independent of organizational competence, outcomes and policy. The C5
history contains only previous latent task identifiers. The old v1 emitter
uses `DemandRegime` with a finite distribution over 2-D requirement vectors,
and generates each emission with the coordinate-derived seed
`SHA256("hls-lab-v1-emission-v1|seed|period")[:8]`; problem IDs are stable
requirement-vector keys. The environment maps each latent task to an emission
regime. It does not define a second stationarity or Markov process.

### N×K emission and replay

`src/hls/hls_lab_nk_environment.py` adds `DemandRegimeNK`, a finite catalogue
of existing `ProblemSpecNK` contracts with a categorical emission
distribution, plus `ExogenousEnvironmentConfigNK` and immutable
`EnvironmentTrajectoryNK`. Catalogue size is independent of K. The process
classes, their probability semantics, transition rules, first-state rule and
time indexing are reused unchanged. The N×K layer validates a common K across
emissions and maps each sampled latent task to a regime and then a K-vector
problem. The config stores the process, full emission catalogue, horizon and
effective problem resource budget; the trajectory stores its seed, generated
problem IDs/requirements/CES weights/budgets, sampled latent task states and
emission regime labels. The sampled initial environment state is `latent_states[0]`;
the process configuration separately records its initial distribution.

For equal-weight 3×2 emission the old `generate_problems` routine is invoked
directly, preserving the historical emission draw, requirement-derived ID,
equal CES weights and budget. For other K (or an explicitly non-equal weight
catalogue), the same categorical inverse-CDF convention is applied with the
same coordinate-derived per-period seed. Fixed problem sequences continue to
work through the pre-existing runner contract.

The runner in `hls_lab_nk_execution.py` accepts either `problems=(...)` as
before or `environment=config, environment_seed=...`. The generated path is
fully frozen before execution and then passed to the same explicit-sequence
path. `NKEnvironmentRunResult` returns the frozen `trajectory` alongside the
ordinary run result. Latent states/regime labels are held in that wrapper and
never added to `NKDecisionView`; policy and observation random draws cannot
consume environment randomness. Replaying one trajectory object across
organizations, P0/P1/P2, MIS/teaching switches, or perfect/imperfect
information preserves all problem IDs, vectors, weights and ordering.
Different organizational observations and competence paths are not expected
to match.

### Scope and validation

The following are supported: explicit fixed sequences; C5 IID/stationary
demand; C5 time-indexed nonstationary demand; C5 first-order Markov demand;
K-dimensional finite problem catalogues; optional generation within the N×K
runner; and environment-state/regime metadata separate from policy traces.
No demand adaptation, new process family, requirement mutation within a type,
multi-task arrivals, or environmental response to organizational performance
was added. Environment and organization still run one problem per period.

`tests/test_hls_lab_nk_environment.py` verifies dimensions 1×1, 2×2, 3×2 and
4×3, catalogue size independent of K, process replay, deterministic Markov
state transitions, time-indexed regime change, configuration errors,
historical 3×2 equivalence, and generated-demand replay across P0/P1/P2 × MIS
ON/OFF × teaching ON/OFF × perfect/imperfect information. It also checks that
the generated path returned by the runner corresponds exactly to its episode
problem IDs. The targeted environment/C5/dynamic/Phase 1–3D selection passed
154 tests. `PYTHONPATH=src:. python -m pytest -q` completed with 1,390 passed
and five failed in 515.55 s. The five are the documented provenance/integrity
failures: foundation result inventory count; Campaign 2 state-coverage closure
digest; Campaign 2 theory source digest; Campaign 3 frozen
`finite_problem_belief.py` digest; and strategy-discrimination source digest.
The full-suite command ran before the final test-only seed-variation case; the
updated environment test module then passed 34/34. No new functional regression
was observed. These repository-level failures and pre-existing unrelated
worktree changes were not repaired or staged. Detailed names and reproduction
context are in the Phase 4 history entry.

Local microbenchmark: macOS 27.0.1 arm64, Python 3.11.9; 3-period stationary
sequence, three problem types, P0, no learning/teaching, identical small
competence profiles. K=2 used the default legacy effort catalogue; K=1/3 used
explicit zero plus one 0.5 single-skill effort vector per agent. Times are
single local observations, not performance guarantees. Candidate count is the
feasible P0 catalogue for the first problem; trace bytes are JSON `asdict`
serialization of the three production records, and memory is peak `tracemalloc`
for execution.

| N×K | Environment init ms | Demand generation ms | Feasible P0 candidates | Episode ms | Peak traced bytes | 3-period trace bytes |
|---|---:|---:|---:|---:|---:|---:|
| 1×1 | 0.0199 | 0.1046 | 2 | 1.028 | 9,392 | 1,927 |
| 2×2 | 0.0077 | 0.1202 | 16 | 3.209 | 35,744 | 2,103 |
| 3×2 | 0.0051 | 0.0624 | 37 | 8.217 | 100,840 | 2,275 |
| 4×3 | 0.0057 | 0.0533 | 256 | 47.159 | 291,688 | 3,008 |

These figures reflect the selected P0 configurations; the more expensive
P1/P2 joint-action catalogue and imperfect-information estimator are measured
in their respective phase records. No action catalogues are truncated; the
existing `max_candidates` guard remains authoritative.

N×K production, learning, teaching, estimation and P0/P1/P2 remain as
implemented in Phases 2–3D. HLS Laboratory remains **PARTIAL**. The environment
addition is functional infrastructure validation and not a scientific result.

## Phase 3D — competence estimation and imperfect observation (current addendum)

**Recorded:** 2026-10-16 19:10 +02:00 (Europe/Madrid). This is an additive
N×K execution mode; historical 3×2 source, fixtures, manifests, hashes and
default runner serialization are unchanged.

### Reused estimator and observation rules

`src/hls/hls_lab_nk_estimation.py` wraps the existing `SkillPosterior`,
`update_skill_posterior`, and `predict_skill_posterior_after_mis` from
`hls_lab_dynamic.py`. It changes only the container from the fixed 3×2 shape
to N×K. For each cell the prior is the historical 101-point grid projection
of the three-point distribution on `{0, m, 1}`; its declared variance is
`min(v_prior, m(1−m))`, with the same `1e-12` support floor. Production
observations use `o_ik = e_ik c_ik + Normal(0, σ_prod²)` and the same keyed
normal innovation `(seed, period, component=0, agent-index, skill-index)`.
The scalar likelihood is proportional to
`prior(c) exp(−(o−e c)²/(2 σ_prod²))`; zero effort leaves the posterior
unchanged, and zero noise uses the existing clipped `o/e` identification
rule for positive effort.

After production assimilation, each posterior support value is propagated
through the existing scalar MIS-v2 capability law using the cell's eta when
MIS is enabled. The private competence transition is separately calculated
from actual state. Actual MIS increments are never copied into the estimate.
This preserves the historical order: production/evaluation and noisy
individual observations → actual MIS-v2 plus posterior MIS prediction →
actual directed teaching → noisy formative efficacy observation and running
efficacy-memory update → competence-posterior teaching prediction when
organizational learning is enabled.

The teaching observation remains the legacy direct gain plus keyed normal
noise. Its normalized signal uses the organization’s estimated post-MIS
learner competence, the legacy denominator `r e (1−ĉ)`, and the efficacy
prior when that denominator is at most `1e-12`. The running-mean efficacy
memory is not conflated with the competence posterior. When
`organizational_learning=False`, actual teaching still occurs but neither the
efficacy memory nor the estimated competence posterior is advanced for that
teaching event, matching the historical toggle.

### Information modes and trace boundary

The established Phase 1–3C runner path remains the default
(`information_mode=None`) and its previous record/serialization contracts
remain unchanged. Explicit `information_mode="perfect"` uses actual
competence as the policy estimate at every decision and after MIS/teaching;
it does not construct or update a competence posterior. Explicit
`information_mode="imperfect"` initializes the N×K grid posterior around
`OrganizationConfigNK.competence_estimated_initial` (or the existing default
estimate), then uses its means for policy decisions. Both modes preserve
production from actual competence. Imperfect mode never puts actual
competence, observation residuals, true teaching efficacy, or realized
competence increments into `NKDecisionView`; the additional diagnostic truth
and observation fields exist only in the returned episode trace.

Observations and traces are reproducible under `information_seed`, using the
legacy coordinate-keyed streams. Zero observation noise is not synonymous
with perfect information: it only identifies a competence cell after
positive effort and the historical likelihood update. Perfect information
is a separate reference mode. `P0`, `P1`, and `P2` use their existing rules;
P0 remains production-only, and P1/P2 keep the independent formative efficacy
memory.

### Verification status and limits

Focused Phase 3D tests cover 1×1, 2×2, 3×2, 4×3, replay, imperfect initial
estimates, zero-effort/nonzero-prior-uncertainty, authorized decision views,
production from actual state, and matched 3×2 trajectories against the
authoritative legacy runner for noisy production observations, MIS-v2,
directed teaching, P1/P2 choices, formative observation noise, estimator
updates, and efficacy memory. The final focused/regression selection passed
**86 tests**. Full suite: **1,357 passed, 5 failed** in 483.40 seconds. The five
failures exactly match the established worktree provenance baseline:
foundation result inventory count; Campaign 2 closure document digest;
Campaign 2 theory source digest; Campaign 3 frozen
`finite_problem_belief.py` digest; and strategy-discrimination source digest.
No new functional regression appeared. No campaign was run.

This phase still uses the existing perfect-information state for the old
default runner. Imperfect mode is opt-in and operates on frozen caller-supplied
problem sequences. It does not generalize environmental generation, add an
estimator, change P0/P1/P2, or infer unknown competence-transition parameters.
Exact enumeration cost remains dominated by the existing action catalog;
posterior storage is O(NK G) for G grid points. HLS Laboratory remains
**PARTIAL**.

Engineering microbenchmarks ran on Python 3.11.9 / macOS 27.0.1 / arm64 with
three-period, P0, production-only imperfect-information episodes, 101
posterior support points, production observation SD .02, and complete action
catalogues. K=2 uses the legacy catalog; other K uses zero plus one unit
effort vector per skill. Observation generation and posterior-update times
are per call averaged over 100 and 50 calls; P0 selection is per call averaged
over 100 selections from a fixed view. Episode, memory and trace measurements
are local diagnostics, not performance guarantees.

| N×K | Candidates | Observation ms | Estimator update ms | P0 select ms | Episode ms | Peak traced bytes | Trace bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1×1 | 2 | 0.0087 | 0.0826 | 0.0113 | 3.349 | 32,072 | 6,456 |
| 2×2 | 16 | 0.0327 | 0.0733 | 0.1538 | 10.196 | 52,120 | 16,820 |
| 3×2 | 64 | 0.0493 | 0.1027 | 0.4187 | 29.599 | 166,040 | 23,850 |
| 4×3 | 256 | 0.0843 | 0.1391 | 1.9170 | 106.304 | 478,960 | 42,393 |

Policy-only selection timings were also measured separately with teaching
enabled, default teaching effort 0.25, all off-diagonal efficacies 0.5,
competence .4, requirements .8, per-agent limit 1, collective/problem budget
N, and complete feasible joint catalogues. Each timing is the mean of 10
`choose` calls on one fixed view. N=1 has no valid P1/P2 relation.

| N×K | Feasible joint actions | P0 select ms | P1 select ms | P2 select ms |
|---|---:|---:|---:|---:|
| 1×1 | 2 | 0.0147 | N/A | N/A |
| 2×2 | 20 | 0.1021 | 0.0080 | 0.1466 |
| 3×2 | 112 | 0.7789 | 0.0894 | 0.8202 |
| 4×3 | 832 | 3.4573 | 0.1624 | 2.9663 |

## 12. Phase 3B — N×K directed teaching

**Recorded:** 2026-10-16 16:04 +02:00 (Europe/Madrid). **Status:** additive
N×K teaching transition and explicit joint-action episode path implemented;
P1/P2, teacher selection, estimation and campaigns remain on HOLD. Historical
modules and frozen results were not edited.

### Authoritative legacy teaching contract

The source of truth is `run_integrated_sequence` in
`src/hls/hls_lab_v1_integrated.py`. A `TeachingEvent` is directed
`(instructor, learner, capability, effort)`, indices are zero-based, agents
must differ, and event effort is finite and positive. The private efficacy
tensor is indexed instructor × learner × capability, lies in `[0,1]`, and
has a zero diagonal. `TeachingParameters.transfer_rate` lies in `(0,1]`.
The gain equation is:

```text
g[j,k] = transfer_rate * effort * T[i,j,k] * (1 - c_after_MIS[j,k])
c_after_teaching[j,k] = min(1, c_after_MIS[j,k] + g[j,k])
```

Only the learner's targeted cell changes; the teacher's competence is not
depleted. Importantly, current teacher competence is **not a direct factor**
in this historical equation. Instructor heterogeneity enters through the
relation-specific `T[i,j,k]`; adding a competence multiplier would change the
scientific model and was not done. Teaching can therefore increase learner
competence even when the teacher's current value for that skill is low, if the
configured relation efficacy is positive. This is a limitation of the
existing model's interpretation, not a new assumption introduced by the N×K
adapter.

Each participant is charged `effort` individually and the collective charge
is `2*effort`. The existing v1 contract permits the participants to retain
other productive effort within their remaining individual caps. Production
and reward use pre-transition competence; update order is production/outcome,
MIS-v2, then teaching. Thus teaching uses the post-MIS learner competence and
the two increments are sequentially composed, not added as independent
increments. The production function and MIS-v2 law are unchanged.

### N×K action, efficacy and runner contract

`src/hls/hls_lab_nk_teaching.py` adds `TeachingActionNK` (stable teacher,
learner and skill identifiers plus event effort), `TeachingEfficacyNK` with
shape `N×N×K`, and scalar `TeachingParametersNK.transfer_rate`. Efficacy
remains relation-specific and bounded `[0,1]`; diagonal entries must be zero,
so `N=1` has zero valid directed teaching actions. The number of possible
directed relations is `N(N−1)K`: 0, 4, 12 and 36 for 1×1, 2×2, 3×2 and 4×3.
The shape-general transition updates only the learner/skill cell and preserves
the equation above, including zero-efficacy and competence-one saturation.

`JointActionNK` supplies a complete productive allocation and optional
teaching action. When teaching is enabled, the caller must supply one complete
action per period and the efficacy tensor; no policy selects a teacher,
learner, skill, or whether to teach. A teaching event while the mechanism is
disabled is rejected. The supplied production allocation must be a member of
the declared feasible catalog; the runner never edits a P0 choice to make
space. Joint feasibility enforces:

```text
sum(production) + 2*teaching_effort <= min(organization budget, task budget)
agent production load + its teaching participation load <= individual limit
```

The episode runner reuses N×K production, evaluation and MIS-v2 modules.
Current-period output/success/CES use competence before updates; then the
optional MIS-v2 transition runs, followed by the optional teaching transition.
The trace separately stores productive effort, teaching resource, total
resource, individual loads, unused capacity, competence after MIS, MIS cell
increments, teaching cell increments and resolved private efficacy. The N×K
runner remains perfect-information; no estimation or observation process is
added. The previous default MIS-OFF path and MIS-only return/serialization
contracts remain unchanged when no explicit joint actions are supplied.

### Verification and local engineering timing

Focused verification: 95 tests passed across the new teaching tests plus Phase
1 geometry, Phase 2 production, Phase 3A MIS and historical 3×2 integrated
regressions. A forced 3×2 joint action was executed through both the generic
runner and historical integrated simulator; production output, functional
success, CES, post-MIS state, final competence, teaching effort and total
resources agreed. Existing historical tests continue to pin the 64-action
production catalog, 508-action integrated catalog and P0/P1/P2/serialized
trace behavior. The test also confirms that teacher competence is not part of
the legacy teaching equation.

Non-scientific local measurements used a 20-period explicit-action episode,
zero productive allocation for timing the episode runner, and per-agent
catalogs containing zero plus one 0.5 effort vector per skill. Catalog count
is `(K+1)^N` before feasibility filtering. Transition time is a 10,000-call
mean where a valid directed relation exists; 1×1 has no transition/action.
Enumeration and episode time are single local observations; serialized JSON
bytes report retained trace scale, while `tracemalloc` peak is a single-run
Python allocation observation. Environment: Python 3.11.9, macOS arm64.

| N×K | Valid directed relations | Candidates | Enumeration ms | Teaching transition ms/call | 20-period episode ms | Trace peak bytes | JSON bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1×1 | 0 | 2 | 0.015 | N/A | 0.585 | 54,240 | 16,754 |
| 2×2 | 4 | 9 | 0.030 | 0.003703 | 1.075 | 133,560 | 21,586 |
| 3×2 | 12 | 27 | 0.096 | 0.004979 | 2.425 | 147,608 | 23,251 |
| 4×3 | 36 | 256 | 2.943 | 0.007208 | 57.106 | 413,824 | 27,433 |

These are local implementation checks, not performance guarantees. Episode
time includes repeated feasible-catalog enumeration. Exact action generation
remains exponential in the configured per-agent choices and guarded by
`max_candidates`; no truncation/optimizer was introduced.

The complete repository suite after Phase 3B completed with **1320 passed and
5 failed in 479.80 s**. The failures are the known historical provenance /
integrity cases enumerated in `docs/HISTORY.md`; no new functional regression
was observed. `git diff --check` was also run after documentation updates.

**Supported after Phase 3B:** explicit-action N×K production episodes with
MIS-v2 OFF/ON and teaching OFF/ON in all four combinations; directed relation
tensor and one event maximum per period; positive N/K and complete catalogs
within `max_candidates`; perfect-information P0 remains only the policy for
non-explicit episodes, while explicit-action execution follows supplied
actions. **Still unsupported:** generalized P1/P2, automatic teaching action
selection, competence estimation/partial information, environment emission,
multi-recipient lessons, simultaneous lessons, and mechanisms beyond the
historical equations. HLS Laboratory remains **PARTIAL**.

## 13. Phase 3C — N×K P0/P1/P2 coordination

The Phase 3C adapter is in `src/hls/hls_lab_nk_policies.py`; policy execution
is additive in `src/hls/hls_lab_nk_execution.py`. The original 3×2 module and
its frozen serialized traces remain unchanged.

P0/P1/P2 expose one `choose(view, memory, parameters)` contract through
`NKCoordinationPolicy`; the existing low-level P0 action selector remains
available for the Phase 2 production-only API.

### Historical policy definitions retained

All three policies rank production using the legacy lexicographic tuple
`(functional_success, -normalized_deficit, productive_margin, -productive_effort)`;
gross CES is measured but is not substituted into this ranking. Ties select
the first action in catalogue order.

* **P0** selects the first best-ranked production-only allocation and never
  teaches, even when teaching is available.
* **P1** has one configured directed `(teacher, learner, skill)` relation. It
  chooses the best-ranked feasible joint action with that exact lesson; if no
  such action is feasible or teaching is disabled, it falls back to its best
  production-only action. P1 does not inspect requirements, efficacy or memory
  to decide whether to try that relation.
* **P2** first returns the best production-only action if it already succeeds.
  Otherwise it retains configured relations whose skill is required and
  whose learner's estimated competence is below the configured target. It
  selects the first eligible relation with no formative observation yet; once
  all eligible relations have observations, it selects the highest running
  mean efficacy estimate, breaking ties by the smallest legacy numeric
  `(teacher_index, learner_index, skill_index)`. It teaches only when that
  estimate is at least the configured efficacy threshold. If teaching is
  unavailable or the chosen lesson is infeasible, it falls back to P0.
  P2 is not a return optimizer and uses no future state.

The N×K action uses stable IDs, while tie-breaking and candidate order use the
organization's declared index order. The generalized joint catalogue loops
through production actions in their existing order, appends the no-lesson
action first, and then visits teacher, learner (skipping self), and skill in
ascending index order. This reproduces the historical 3×2 508-action order.
At most one lesson is possible in a period. For `M` raw production candidates,
the guarded joint search space is `M × (1 + N(N−1)K)` when teaching is enabled;
the implementation fails explicitly if that bound exceeds `max_candidates`
and never truncates. The production-only path keeps its original `M` bound.

### Information, memory and transition timing

As required for this phase, the policy decision view uses perfect competence
information (`estimated = actual` at each period). It contains no private
efficacy tensor or organization configuration. P2's efficacy memory contains
only a running mean of the existing formative response signal. With the
current N×K runner's deterministic, zero-observation-noise condition, the
legacy normalization is
`signal = observed_gain / (transfer_rate × effort × (1 − competence_after_MIS))`;
when the denominator is at most `1e-12`, the legacy efficacy prior is used.
Signals are clipped to `[0,1]` in the existing running-mean update. Setting
`organizational_learning=False` preserves the legacy no-memory-update mode.
No competence estimator or observation noise is added.

Each period remains production and CES from pre-transition competence, then
MIS-v2 if enabled, then directed teaching if selected, then the efficacy-memory
update if organizational learning is enabled. Teaching and production are
jointly validated against both participants' effort limits and the shared
effective budget. The runner does not revise the policy's productive
allocation to make room for a lesson. When teaching is disabled, P1/P2's
available catalog has no lesson actions and the historical fallback applies.
For `N=1`, P0 remains usable; P1/P2 cannot be configured with a valid relation
because self-teaching is prohibited and the historical P2 requires a
non-empty relation list.

### Verification and engineering timing

`tests/test_hls_lab_nk_policies.py` checks the P0/P1/P2 rules independently,
the 64-production/508-integrated 3×2 catalogs and their ordering, deterministic
zero-noise 3×2 decisions/outcomes against the legacy policies with MIS OFF/ON,
relation-order ties, policy information boundaries, teaching-off fallbacks,
N×K dimensions, and resource feasibility. Existing Phase 1–3B regressions
remain in force. The measured 3×2 policy comparisons are exact under matched
initial competencies, deterministic zero-noise observations, matching policy
parameters and the perfect-information condition; they do not claim equivalence
to legacy Bayesian competence estimates under noisy observations.

The following local measurements used a three-period episode, a 3×2 default
production catalog, and for other dimensions per-agent catalogs containing
zero plus one 0.5-effort vector per skill. Each timing row is the mean of three
joint-enumeration runs; P1/P2 selection is the mean of 100 calls on one fixed
view; episode and `tracemalloc` peak are single local runs. Candidate count is
the raw joint upper bound / resulting feasible joint count. Environment was
Python 3.11.9 on macOS arm64. These are engineering microbenchmarks, not
performance guarantees.

| N×K | Joint upper bound / feasible | Enumeration ms | P1 select ms | P2 select ms | 3-period episode ms | Peak traced bytes | Serialized trace bytes |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1×1 | 2 / 2 | 0.021 | N/A | N/A | 2.301 | 16,880 | 3,247 |
| 2×2 | 45 / 45 | 0.174 | 0.0799 | 0.1196 | 15.289 | 28,056 | 4,518 |
| 3×2 | 832 / 508 | 3.113 | 0.3989 | 1.0671 | 95.621 | 169,272 | 5,288 |
| 4×3 | 9,472 / 9,472 | 37.222 | 2.247 | 4.2286 | 1,064.505 | 2,453,208 | 6,538 |

The Phase 3C focused suite passed 93 tests, including all Phase 1–3B checks
and the historical integrated-policy suite. After finalizing the common P0/P1/P2
policy interface, the complete suite passed 1,337
tests and retained the same five documented provenance/integrity failures;
the names are recorded in `HISTORY.md`.
Competence estimation, imperfect information, environment generation and
scientific campaigns remain unsupported/in scope-HOLD. HLS Laboratory remains
**PARTIAL**.
