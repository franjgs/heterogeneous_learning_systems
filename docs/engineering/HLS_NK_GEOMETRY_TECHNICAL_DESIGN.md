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

**Next authorized increment:** none in this task. Learning transition and
policy generalization remain on hold pending separate authorization; this
implementation does not itself close `HLS-LAB-V1-INTEGRATED`, which remains
**PARTIAL**.
