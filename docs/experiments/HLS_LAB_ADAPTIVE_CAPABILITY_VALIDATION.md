# HLS Laboratory adaptive-capability validation

**Status:** bounded integration validation, 2026-10-17. HLS Laboratory remains
**PARTIAL**. This is a diagnostic validation, not a scientific campaign.

## 1. Purpose and scope

This record verifies that selected adaptive capabilities already present in
HLS can be composed and observed through their existing execution paths. It
does not test whether an adaptive policy is generally superior, establish
prevalence, or reproduce a complete external paper. The guiding distinction
is:

* a dynamic environment changes exogenously;
* a state-responsive policy can change its decision when its current inputs
  change;
* online estimation changes an estimate from received observations;
* online policy learning changes a decision rule or memory from feedback;
* experience-dependent development changes the modeled agent state after
  actions.

These properties can coexist but are not synonyms. The work reuses C5, the
N×K environment/execution runner, MIS-v2, the competence posterior, P0/P2,
Nembhard Direct, and the canonical G2 controls. It adds one small integration
runner and regression tests; it does not change scientific equations,
policies, environment mechanisms, E1/E2 definitions, or their result files.

The exact compact output is
[`integrated_validation_results.json`](../../results/analysis/hls_lab_validation/integrated_validation_results.json),
with a navigable [machine-readable capability registry](../../results/analysis/hls_lab_validation/capability_registry.json).
The executable is
[`adaptive_capability_validation.py`](../../experiments/synthetic/hls_lab_v1/adaptive_capability_validation.py).

## 2. Existing components and models exercised

| Capability | Existing implementation | Evidence used here |
|---|---|---|
| Stationary/IID, time-indexed nonstationary, and first-order Markov demand | `src/hls/synthetic/c5.py`: `StationaryTaskDemand`, `NonStationaryTaskDemand`, `MarkovTaskDemand` | Existing C5 and N×K environment tests, plus S0–S2 runner integration traces |
| Frozen exogenous N×K demand with regime metadata | `src/hls/hls_lab_nk_environment.py`: `ExogenousEnvironmentConfigNK`, `generate_environment_trajectory_nk`; `src/hls/hls_lab_nk_execution.py::run_nk_production_sequence` | Generated trajectory states/problem IDs are checked against the records actually executed |
| Heterogeneous competence/resources and MIS-v2 | `OrganizationConfigNK`, `LearningProfileNK`, `mis_v2_transition_nk` | S0 uses unequal initial competencies, eta values, and per-agent effort limits; learning tests verify transition order and controls |
| Separate true and estimated competence | `src/hls/hls_lab_nk_estimation.py`, information-aware runner | S4 records actual, estimated, observed, and posterior quantities separately; information-boundary tests verify policies do not receive actual state |
| P0 state response | `src/hls/hls_lab_nk_policies.py::P0ProductionOnlyPolicyNK` | The S1 policy receives only current problem and declared estimate; its chosen allocation differs across the predeclared problem-regime change |
| P2 teaching-efficacy memory | `P2AdaptiveTeachingNK`, `OrganizationMemoryNK` | S4 reuses the existing four-period P2 reference, imperfect observation, MIS-v2, teaching and efficacy memory |
| Nembhard Direct heterogeneous productivity | `src/hls/hls_lab_nk_nembhard.py` | A single feasible explicit allocation records distinct cell-specific productivity and output, with unequal effort limits |
| Action-dependent development and organizational future value | `src/hls/g2_dynamic.py` (`D0`, `D1`, `D2`) | Existing canonical analytical/computational null and positive controls, not reinterpreted as MIS-v2 |
| Individual/collective evaluation and resource trace | N×K result records in `src/hls/hls_lab_nk_execution.py` | Period trace stores allocation, per-agent output, total output, success, deficit, CES, competence states, observations, transitions and resource use |

HLS N×K production is additive in actual competence. MIS-v2 has its own
exposure transition. Nembhard Direct instead uses separate experience `D` and
productivity parameters `(k,p,r)`. Neither productivity nor G2 competence is
identified with normalized HLS competence. CES is gross performance, not net
utility. Effort is not monetary cost.

## 3. Validation scenarios and configurations

The bounded runner emits five named checks. S0–S2 reuse the corresponding
small fixtures/contracts already present in the N×K/C5 tests; S3 invokes the
existing G2 analytical fixtures; S4 invokes the saved Phase 5A reference
scenario builder. S4 is not a new mechanism or a new policy configuration.

### Scenario S0 — stationary control

Three periods, N=2, K=2, stationary regime state `steady`, two existing
problem types with probabilities 0.6/0.4, P0, perfect information, MIS-v2 ON.
Initial actual and estimated competence differ; eta is cell-specific
`((0.20, 0.05), (0.08, 0.15))`; effort limits are `(0.75, 1.0)` and shared
budget is 1.5. The environment and execution records replay exactly and actual
competence changes after exposed work. All three periods fail functional
requirements in this particular diagnostic. This is retained as an observed
fixture outcome, not tuned away; production, CES, deficit, effort and state
traces are still present. It is not evidence that stationary demand causes
failure.

### Scenario S1 — nonstationary demand

Four periods, N=2, K=3, using the existing indexed fixture: old, old, new,
new with the distribution changing at period 2. The trajectory labels and
problem IDs are exactly the four problem IDs passed to the runner. Under P0,
the selected allocation before and after the regime change differs. This
demonstrates that the current problem is delivered to a state-responsive
policy and that the existing rule can respond in this fixture. It does not
show change-point inference: the demand state is exogenous and not latent to
the policy. Nor does a changed task imply that the optimal allocation must
always change.

### Scenario S2 — Markov environment

Twenty periods, N=2, K=2, C5 initial distribution `(0.5,0.5)` and existing
sticky transition rows `(0.9,0.1)` and `(0.1,0.9)`, seed 17. P0 receives each
current problem and the runner executes the frozen path. Re-running with the
same environment and information seeds yields exact equality of trajectory
and run result. The record is one seeded path; it does not estimate transition
frequencies or constitute statistical validation of the stochastic law.

### Scenario S3 — competence-development controls

The canonical G2 D0/D1/D2 fixtures are evaluated at their existing
formulation's future-demand weight `p=0.75`:

* D0 has zero development value when no learning occurs.
* D1 changes the competence state but leaves the efficient frontier and
  future collective value unchanged (development-value null).
* D2 has positive development value and a positive total action-value
  difference at this declared `p`.

This is an analytical/computational existence result in G2's additive
saturating learning model. It is not an N×K episode, not MIS-v2, and not a
claim that action-dependent learning generally improves performance. The
separate N×K MIS-v2 tests verify exact transition behavior, no-learning
controls, order, and replay.

### Scenario S4 — existing adaptive coordination reference

The existing four-period reference at
`experiments/synthetic/hls_lab_v1/scientific_model_reference.py` is replayed:
N=2, K=2, deterministic alternating Markov regime, P2, imperfect competence
observations, MIS-v2 ON, directed teaching ON, and fixed seed pair 24016/24017.
The trace contains actual and estimated competence, observations, MIS and
teaching increments, relation-efficacy memory before/after, actions, output,
functional evaluation and resource use. The run shows that the code path
executes and those states evolve; all four requirements happen to remain
unsatisfied. P2's memory update concerns teaching efficacy, not a learned
task-allocation value function. P2 is a state- and memory-responsive teaching
heuristic, not a general online allocation learner or long-horizon optimizer.

### Heterogeneity and resource diagnostic

A separate one-period, explicit Nembhard Direct allocation uses different
cell-specific `k,p,r`, different agent effort limits `(0.5,1.0)`, shared
budget 1.5, and records productivity, per-agent output and experience
increment. It confirms operation of the declared Nembhard adaptation under
heterogeneous parameters and resource checks. It does not reproduce the full
Nembhard–Bentefouet organization/transfer model.

## 4. Decision policies and information boundaries

| Rule | Classification supported by code | Information/state used | Not implied |
|---|---|---|---|
| P0 | State-responsive, not learning-based | Current requirements, feasible actions, estimated competence in the policy view | No learned policy parameters, exploration, or future planning |
| P1 | Configured teaching rule with production fallback | Current problem/view and predeclared directed relation | No learning of relation choice |
| P2 | State-responsive teaching rule with online efficacy memory | Current estimated competence, feasible actions, observed relation efficacy/memory | No generic allocation learning or explicit planning over future competence |
| Nembhard ORACLE | Full-information, current-period reference | True `D,k,p,r`, current problem/resources | Not deployable imperfect-information policy or long-horizon optimum |
| Nembhard ADAPTIVE | Observation-based productivity estimate plus optional exploration | Selected-work observations, reconstructed experience and current resources | Not MIS competence estimation, not fitting the Nembhard curve, and not validated as generally effective by E1 |
| Contextual quality-cost router | Feedback-updated contextual candidate predictor | Query context and selected-candidate quality/cost feedback | Not connected to N×K; not evidence about agent allocation |

The S1 action change comes from P0 applying its unchanged current-state rule
to changed problem requirements. It is state response, not policy learning.
In S4, the policy cannot see actual competence or unobserved efficacy truth;
actual state is retained for evaluator diagnostics only. Competence
development (MIS-v2), statistical state estimation, environment transition,
and P2 efficacy-memory update are distinct trace fields.

### Other implemented routes not exercised here

The Nembhard ORACLE and Nembhard ADAPTIVE routers are not executed by S0–S4.
Their implementation contracts and information boundaries are covered by
their existing dedicated tests, and E1 provides a separate scoped comparison;
in this worktree, however, E1's 1,016 episode results are local and
unpublished. The independent contextual quality–cost router is also not
exercised here and is not integrated into N×K. Registry status records these
capabilities as not validated by this bounded run rather than inferring
validation from their existence or test pass status.

## 5. Validation method and executed checks

The new runner is a small deterministic orchestrator over existing APIs. It
checks that generated problem IDs equal executed IDs, repeated seeds reproduce
the complete result, actual competence is the physical production state,
resource feasibility is preserved, and the canonical G2 controls keep their
null/positive interpretations. It makes no calls to the E1 or E2 campaign
runners. The compact JSON contains configurations, seed values, generated
environment states/problems, period-level decisions/outcomes/state traces,
checks and interpretation metadata.

The following tests are the validation suite for this record:

```bash
PYTHONPATH=src pytest -q \
  tests/test_hls_lab_adaptive_capability_validation.py \
  tests/test_hls_lab_nk_environment.py \
  tests/test_hls_lab_nk_learning.py \
  tests/test_hls_lab_nk_estimation.py \
  tests/test_hls_lab_nk_policies.py \
  tests/test_hls_lab_nk_nembhard.py \
  tests/test_g2_dynamic.py \
  tests/synthetic/test_c5_dynamic_demand.py
```

The focused run completed with **135 passed**. The canonical compact record is
reproducible with:

```bash
PYTHONPATH=src python experiments/synthetic/hls_lab_v1/adaptive_capability_validation.py
```

The command refuses to replace a different existing result unless the
explicit `--replace-generated-record` flag is used. No full test suite was
run for this validation transaction; the previously reported full-suite
result remains 1,512 passed and five known historical integrity/inventory
failures. Those failures are not represented as resolved here. No large
campaign was run.

## 6. Results and claim boundaries

### Established by this validation

1. Existing stationary, indexed nonstationary and Markov C5 processes can be
   generated, frozen, and executed through the N×K runner without losing
   temporal ordering or regime labels.
2. Same-seed environment and observation settings reproduce these compact
   trajectories exactly.
3. In the declared S1 case, P0 receives the changed current problem and
   changes its selected allocation; this validates a state-responsive path,
   not a learned policy.
4. N×K traces preserve actual competence, estimates, observations, MIS-v2,
   teaching, memory, output, functional outcomes and resource fields for the
   reused S4 path.
5. The G2 no-development, development-without-frontier-value, and
   development-with-positive-future-value controls execute as documented.
6. Heterogeneous cell-specific Nembhard productivity and unequal resource
   limits are supported by the direct-mechanism route.

### Not established

* General superiority or optimality of P0/P1/P2, Nembhard ADAPTIVE, or any
  contextual router.
* Online inference of a hidden demand regime in N×K; environment regimes are
  experimenter-side metadata and current problems are visible.
* Broad prevalence or statistical properties of Markov transitions from a
  single seeded path.
* Causal attribution among estimation, policy rule, exploration, teaching,
  and learning in bundled experiments.
* Empirical calibration or construct validity of synthetic competence,
  productivity, observations, CES, or transfer parameters.
* Full reproduction of Nembhard–Bentefouet, Baccara–Lee–Yariv, MixLLM,
  System-1.x, or any other complete paper protocol.
* Universal organizational learning or a single integrated router spanning
  HLS, Nembhard and contextual quality–cost routes.

## 7. E1/E2 relationship and historical evidence

HLS-E1 tested one declared Nembhard adaptation and a role-aligned FIXED
reference; the Nembhard protocol review records that FIXED and immediate
ORACLE allocations nearly coincided in the mixed and specialist strata,
while the adaptive estimator tracked a changing productivity signal with a
running mean. Its negative ADAPTIVE-vs-FIXED result remains valid for that design,
but it is not a general stress test of the HLS N×K environment, MIS-v2,
competence posterior, P0/P1/P2, or legacy learning policies. At the current
worktree, a read-only registry inspection reports 1,016 valid local E1
episodes and zero pending; the results directory and E1 analysis are
untracked/unpublished here. The older tracked Current State records the
previously observed interrupted count (29 completed/987 pending). This
validation does not alter or publish those E1 results; reconcile provenance
before treating them as repository-tracked evidence.

HLS-E2.0/E2.1 use separate, self-contained direct-productivity optimization
models. E2.1's 33 deterministic no-gap cases are scoped to two independent
skills, separable reward, discrete one-agent assignments, and globally
optimized task-dependent stationary mappings. The result is a useful
negative boundary under those assumptions; it bypasses MIS-v2, N×K P0/P1/P2,
competence estimation, teaching and generated C5 episodes. Neither E1 nor E2
answers whether the broader lab can generate changing environments and
execute its existing information/learning policies.

## 8. Literature boundary and future reuse

| Reference family | Existing reusable mechanism | Evidence boundary / missing work for reproduction |
|---|---|---|
| Nembhard & Bentefouet (2015) | HLS Nembhard Direct curve adaptation and heterogeneous direct productivity parameters | The article's transfer, selection/grouping, production topology, and full parameterized experimental protocol are not reproduced. See the primary-source extraction and fidelity review. |
| Baccara, Lee & Yariv (2023) | Generic agent/problem/resource representation only | Queue arrivals, waiting, congestion, endogenous service capacity, and decentralized equilibrium are missing; no faithful reproduction. |
| MixLLM (Wang et al., 2025) | Separate contextual quality/cost router with selected-candidate feedback | Its LLM candidates/data/metrics and full protocol are not reproduced; contextual router is not connected to the N×K runner. |
| System-1.x (Saha et al., 2025) | Bounded FAST/DEEP/META experiments exist in another fixed synthetic task model | This validation does not test them; the original decomposition/controller protocol and task datasets are not reproduced. |

For future paper work, first reuse and validate an already implemented
mechanism; then match the paper's domain, parameters, information, baselines,
metrics and protocol. An implemented equation alone is not a reproduction.

## 9. Reproduction, code, and future extension points

From repository root:

```bash
PYTHONPATH=src python experiments/synthetic/hls_lab_v1/adaptive_capability_validation.py
PYTHONPATH=src pytest -q tests/test_hls_lab_adaptive_capability_validation.py
```

Key locations:

* Validation orchestrator: `experiments/synthetic/hls_lab_v1/adaptive_capability_validation.py`
* Regression tests: `tests/test_hls_lab_adaptive_capability_validation.py`
* Detailed result: `results/analysis/hls_lab_validation/integrated_validation_results.json`
* Registry: `results/analysis/hls_lab_validation/capability_registry.json`
* Environment/process tests: `tests/test_hls_lab_nk_environment.py`, `tests/synthetic/test_c5_dynamic_demand.py`
* MIS and estimator tests: `tests/test_hls_lab_nk_learning.py`, `tests/test_hls_lab_nk_estimation.py`
* Policy tests: `tests/test_hls_lab_nk_policies.py`
* Nembhard Direct tests: `tests/test_hls_lab_nk_nembhard.py`
* G2 ground truth and tests: `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`, `tests/test_g2_dynamic.py`
* Existing imperfect-info reference: `experiments/synthetic/hls_lab_v1/scientific_model_reference.py` and `results/diagnostics/hls_scientific_model_dossier/reference_trace.json`
* Prior implementation and literature reuse boundaries: `docs/literature/audits/HLS_CODE_REUSE_AND_INTEGRATION_AUDIT_2026-10-17.md`; Nembhard comparison design limits: `docs/experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md`

The reusable extension points are the frozen environment trajectory,
`run_nk_production_sequence`, the `NKCoordinationPolicy`/decision-view seam,
the competence-posterior helpers, and mechanism-specific result traces.
They should be reused before adding new scenario runners or adaptive
mechanisms. P0/P1/P2, Nembhard routers and contextual routing remain separate
decision systems, with distinct information and metric semantics.
