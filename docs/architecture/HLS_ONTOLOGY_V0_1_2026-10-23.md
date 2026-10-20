# HLS ontology v0.1 — 23 October 2026

**Status:** consolidated semantic reference; not a simulator redesign.
**Scope:** concepts and distinctions already used in HLS theory and code, with
particular attention to N×K/MIS-v2, directed teaching, demand, observation and
decision policies. This document describes current semantics; it does not
authorize model changes or an experiment.

Evidence labels: **FACT** means an equation, code path, test contract, or
recorded result was inspected; **INTERPRETATION** means a consequence or
classification of those facts; **OPEN** means the repository does not settle
the issue. Tests establish software contracts, not scientific validity.

## 1. Ontological definitions

The ontology remains plural: an HLS is not required to use every concept below
or to implement one universal state/action interface. The canonical
[ontology](../hls_ontology.md) separates organization/use from
development/evolution and does not equate source-specific quantities by
terminology alone.

| Concept | v0.1 definition | N×K / related realization and boundary |
|---|---|---|
| Agent | An identifiable actor that can hold capabilities and participate in work or development. | `agent_ids` in `OrganizationConfigNK`; the Nembhard router's candidates are not thereby N×K agents. |
| Task / problem | A work requirement presented for execution. | `ProblemSpecNK(problem_id, requirements, resource_budget, ces_weights)`; an emitted task is current-period input. |
| Competence | A bounded state representing capacity to perform relevant work; it is not itself realized output. | N×K `competence_real[i][k] ∈ [0,1]`; production uses current true competence. |
| Experience | A record/exposure accumulated through activity; it is not competence or competence change. | N×K MIS-v2 receives productive effort as exposure but has no persistent experience matrix in `OrganizationStateNK`. Legacy dynamic `ExpertState.experience` is cumulative effort. Nembhard `D[i,k]` is a distinct persistent state entering its productivity curve. |
| Productivity | A model-specific mapping from state/parameters to output per work input. | N×K production is competence-based; Nembhard Direct uses `P_ik(D)=k_ik(D+p_ik)/(D+p_ik+r_ik)`. Neither is an alias for competence. |
| Learning | A transition in competence or another declared capability state as a function of exposure/action. | MIS-v2 is cellwise learning-by-doing. “Learning” does not imply that a policy parameter is learned. |
| Knowledge transfer / teaching | A directed development event from a teacher to a learner for a skill. | `TeachingActionNK(teacher_id, learner_id, skill_id, effort)`; it is explicit and separate from production. |
| Transfer effectiveness | The relation- and skill-specific efficacy governing the teaching transition. | Private `TeachingEfficacyNK.values[i,j,k]=T[i,j,k]∈[0,1]`; teacher competence is not a direct multiplier in the implemented law. |
| Assignment / organization | A decision about how agents' capabilities/work are allocated. | `ProductiveAllocationNK[i,k]` is divisible nonnegative effort, not an indivisible task assignment. Broader ontology `a_t` may cover routing, teams, sequencing, etc. |
| Coordination | Rules/processes coupling agent decisions, information, tasks, or resources. | P0/P1/P2 share a period-level joint-action interface; this is not evidence of a universal coordination architecture. |
| Resource / effort | A constrained quantity consumed by an action. | N×K records productive effort, teaching effort, individual effort loads, collective budget and unused capacity. The quantities are effort units, not money. |
| Cost | A model-specific penalty or resource valuation, requiring explicit units and accounting. | Effort constraints are implemented; they do not by themselves define monetary cost or a universal scalar cost objective. |
| Demand / environment | Exogenous task process and its realized current task. | C5 stationary, indexed nonstationary and first-order Markov generators; trajectories are frozen before N×K execution. Latent regime metadata is evaluator-side. |
| State | Sufficient variables needed to determine transitions and reward for an instantiated model. | N×K physical competence plus current exogenous problem and period context; the run record also holds evaluator and estimator state. No universal HLS state is prescribed. |
| Observation | Information actually delivered to a decision-maker after a defined event. | `NKDecisionView` includes period, remaining periods, current problem, estimated competence, and feasible actions; outcomes/teaching signals are delivered according to the information runner. |
| Estimate / belief | A statistic or distribution representing uncertain state, distinct from the true state. | `CompetencePosteriorNK` wraps cellwise `SkillPosterior`; posterior means/variances are separate from `competence_real`. |
| Policy | A decision rule mapping available information (and possibly memory) to a feasible action. | `NKCoordinationPolicy.choose(view, memory, parameters) -> JointActionNK`. The actual policy class determines whether it is fixed, state-responsive, memory-updating, or planning. |
| Collective performance | System-level measured outcome under an explicitly defined aggregation. | Period outputs, functional success/deficit, margin and CES are recorded separately; CES/output is not automatically net utility. Individual outputs remain available in traces. |

**Semantic guardrails.** Competence ≠ productivity; competence ≠ observed
performance; production ≠ quality; effort ≠ monetary cost; experience ≠
competence transition; agent ≠ contextual-router candidate; environment
realization ≠ policy observation; estimate ≠ true state; policy action changes
≠ online learning by themselves.

## 2. State, decisions, observations, and exogenous quantities

For N×K, write true competence before period `t` as `C_t[i,k]`; initial
competence comes from `OrganizationConfigNK`. Current demand/problem `W_t`
and its requirements are produced by the environment. Productive action
`A_t[i,k]` is a divisible effort allocation. Optional teaching action `Q_t`
specifies one directed teacher–learner–skill event and effort. The policy
receives a decision view `I_t` (including current task and estimated, not
necessarily true, competence) plus its permitted memory. The runner/evaluator
can retain true competence and mechanism parameters, but these are not thereby
policy-visible.

The N×K sequence with both transitions is ordered:

```text
current task and permitted view
    → joint action (production allocation, optional teaching)
    → production and current-period outcome recorded from pre-update C_t
    → MIS-v2 transition on productive effort
    → teaching transition on its target cell
    → permitted observations/posterior and policy memory updates
    → next period
```

The exact placement of observation/posterior updates is runner-mode-specific;
the `NKInformationEpisodeRecord` preserves actual, estimated, observed and
post-transition quantities rather than collapsing them into one state.
Demand is exogenous to organization actions in the C5/N×K environment.
Current task is policy-observable; future realized demand and latent regime
labels are not in `NKDecisionView`.

N×K `OrganizationStateNK` has `competence_real` and
`competence_estimated`, but **not** experience. MIS-v2 effort is the exposure
argument to a competence transition; do not describe it as a stored
experience stock. Nembhard Direct instead stores cumulative direct experience
`D`, and productivity explicitly depends on `D` and profile parameters
`(k,p,r)`. This is a different model/state semantics.

## 3. Implemented competence and transfer transitions

### 3.1 MIS-v2 learning-by-doing

`LearningProfileNK.eta[i,k]∈(0,1)` is converted by the authoritative
`eta_to_lambda` mapping. For productive effort `e_t[i,k]≥0`, the existing
cellwise transition is

\[
C^{M}_{t+1}[i,k]=1-(1-C_t[i,k])\exp(-\lambda(\eta_{ik})e_t[i,k]).
\]

Equivalently, using `capability_after_exposure`,
`F(c,e)=1-(1-c)e^{-λe}`. Zero exposure is identity. The transition is
applied after current production, is saturating, and does not transfer across
agents or skills. `enabled=False` disables this transition; the no-learning
control is not represented by an invalid `eta=0` (MIS-v2 requires `eta∈(0,1)`).

### 3.2 Directed teaching / knowledge transfer

For a teaching event with learner `j`, skill `k`, effort `u>0`, relation
efficacy `T[i,j,k]∈[0,1]`, and rate `r∈(0,1]`, the implemented transition is

\[
C^{T}_{t+1}[j,k]=\min\{1,C_t[j,k]+r u T[i,j,k](1-C_t[j,k])\},
\]

with all other competence cells unchanged. Current teacher competence is
absent from the formula: relation-specific effectiveness is encoded in `T`.
Efficacy is private configuration/evaluator state; the policy view excludes
the tensor itself, but it may receive formative feedback and maintain a
relation-specific estimate.

### 3.3 Composition and exact interaction identity

For an uncapped single cell updated first by MIS-v2 exposure `e`, then by
teaching with `h=ruT`, define `a=exp(-λe)`, `Δ_M=(1-c)(1-a)`,
`Δ_T=(1-c)h`, and `Δ_MT=(1-c)[1-a(1-h)]`. Then the exact identity reported
in the 22 October mathematical analysis is

\[
\boxed{\Delta_{MT}-\Delta_M-\Delta_T
=-(1-c)(1-a)h=-\Delta_M h\le0.}
\]

This is a **mechanical, same-cell transition identity**: both mechanisms act
on the remaining competence gap. It is zero if either mechanism's gain is
zero. It does not establish the sign of an interaction in output, collective
reward, or policy value. When the updates target different cells, this
same-cell overlap term is absent. The `min(1,·)` teaching cap must be retained
for boundary cases; the displayed identity is valid for the stated
uncapped/interior composition (and the teaching increment is capped in code).

## 4. Interaction taxonomy

These are analytical lenses, not claims that causal effects are separately
identified without controls.

1. **Mechanical interaction:** effect of composing transition mechanisms on
   the same state under identical fixed actions. The boxed overlap identity
   is the current exact result. It says nothing alone about which policy is
   preferred.
2. **Organizational interaction:** policies can respond to the competencies,
   observations, demand and memory generated along their histories. Actions
   may therefore diverge, changing both current reward and future transition
   exposure. Measure separately from a fixed-action transition comparison.
3. **Resource interaction:** production and teaching consume a shared
   collective budget and participant-specific effort limits. Teaching effort
   `u` is charged `2u` collectively and `u` to each teacher and learner in
   `validate_joint_action_resources_nk`. Thus enabling/disabling a transition
   without removing the action must not silently remove its resource charge
   when constructing a mechanism control.
4. **Information interaction:** current observations and posterior/memory
   updates can change later decisions. This is distinct from physical
   competence development and from exogenous demand evolution. A comparison
   must state which signals each policy receives and when.

## 5. Implemented behavior and policy classes

| Mechanism/rule | Classification supported by implementation | What it does not establish |
|---|---|---|
| `P0ProductionOnlyPolicyNK` | Current-view responsive production-only rule; selects the best feasible action under estimated competence. | No learning of policy parameters, exploration, teaching, or long-horizon value. |
| `P1FixedTeachingNK` | Preconfigured directed relation; among matching feasible joint actions selects by current production rank, otherwise falls back to production-only. | “Fixed” describes the configured relation, not a fixed effort matrix or an optimized global policy. |
| `P2AdaptiveTeachingNK` | State- and memory-responsive teaching heuristic. Probes unseen eligible relations, then ranks by observed normalized efficacy estimate subject to threshold/target rules. | Not a finite-horizon optimizer or general learned allocation policy; memory estimates teaching efficacy, not task-routing value. |
| Nembhard ORACLE | Full-information current-period router using true Nembhard experience/profile under its own direct-productivity model. | Not MIS-v2 competence and not long-horizon oracle planning. |
| Nembhard ADAPTIVE | Observation-based productivity estimator/router with its own seeds/exploration semantics. | Not P2, not a MIS competence posterior, not the same adaptation mechanism. |

The classifications are about actual decision rule and information, not
whether action traces happen to vary. Code references are in §6.

## 6. Implementation traceability

| Ontological concept | Mathematical definition | Implemented variable/function | Existing tests/evidence | Known limitation |
|---|---|---|---|---|
| Agent, skill, competence | Identified `(i,k)` cell, `C∈[0,1]` | `OrganizationConfigNK`, `OrganizationStateNK` in `src/hls/hls_lab_nk_geometry.py` | `tests/test_hls_lab_nk_execution.py`; adaptive validation S0/S4 | State container is N×K-specific; omitted estimated initial state defaults to true initial competence (perfect-information convention). |
| Task/demand | Exogenous problem process; current `W_t` | `ProblemSpecNK`; `StationaryTaskDemand`, `NonStationaryTaskDemand`, `MarkovTaskDemand`; `generate_environment_trajectory_nk` | `tests/test_hls_lab_nk_environment.py`, `tests/synthetic/test_c5_dynamic_demand.py`; S0–S2 validation | Environment states/labels are evaluator metadata; runner supports current demand, not policy access to latent regime. |
| Divisible assignment | `A_t[i,k]≥0` satisfying shared and per-agent effort constraints | `ProductiveAllocationNK`, `validate_productive_allocation_nk`, action enumeration | `tests/test_hls_lab_nk_execution.py` | Not indivisible request assignment; “assignment” here means effort. |
| Production/productivity | Output from current competence and effort; Nembhard uses `P(D;k,p,r)` | `productive_outputs_nk` / `evaluate_problem_nk`; separately `nembhard_productive_outputs_nk` | production and Nembhard test modules; validation heterogeneity diagnostic | Production, functional success, CES and productivity are distinct quantities. |
| Experience / MIS learning | MIS transition above, exposure is effort | `LearningProfileNK`, `mis_v2_transition_nk` | `tests/test_hls_lab_nk_learning_transition.py`, `tests/test_hls_lab_nk_learning.py` | No experience stock in N×K state; no forgetting, cross-skill transfer or cross-agent transfer in MIS-v2. |
| Nembhard experience | `D' = D + effort×duration`; productivity depends on `D` | `NembhardDirectStateNK`, `advance_nembhard_experience_nk` | `tests/test_hls_lab_nk_nembhard.py` | Separate mechanism and units; cannot be identified with MIS-v2 competence. |
| Teaching action/effectiveness | Directed event and `T[i,j,k]` transition | `TeachingActionNK`, `TeachingEfficacyNK`, `TeachingParametersNK`, `teaching_transition_nk` | `tests/test_hls_lab_nk_teaching.py` | One lesson/event per joint action; teacher competence does not directly enter efficacy law; efficacy need not be identifiable from noisy formative signal. |
| Resources | Production effort plus `2u` teaching; per-agent participant loads | `validate_joint_action_resources_nk`, `enumerate_feasible_joint_actions_nk` | teaching resource tests; `tests/test_hls_lab_nk_execution.py` | Effort units are not money; no heterogeneous task-specific consumption law. |
| True/estimated/observed competence | Physical `C`, posterior `B`, observation `Y` | `CompetencePosteriorNK`, `assimilate_production_observations_nk`, `predict_mis_v2_nk`; information execution records | `tests/test_hls_lab_nk_estimation.py` | Posterior accuracy under a target scientific observation model is not established merely by contract tests. |
| Policy view and memory | `π(I_t,M_t)→(A_t,Q_t)` | `NKDecisionView`, `OrganizationMemoryNK`, `NKCoordinationPolicy`, P0/P1/P2 | `tests/test_hls_lab_nk_policies.py` | Current policy set is narrow; P2's memory is heuristic relation efficacy, not a learned long-horizon policy. |
| Episode trace and collective outcomes | Period-level action, transition, resource, individual and system measures | `NKTeachingEpisodeRecord`, `NKInformationEpisodeRecord`, `run_nk_*_sequence` in `src/hls/hls_lab_nk_execution.py` | `tests/test_hls_lab_nk_execution.py`, `tests/test_hls_lab_nk_teaching.py`, validation S0–S4 | Not every run mode records every field; compare records by mode and do not assume an unrecorded signal exists. |

The information-mode tests verify actual-state/policy-view separation and
MIS/teaching switches. The bounded integrated validation document
[`HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md`](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md)
records reproducible S0–S4 execution and its claim limits. This is evidence
of scoped integration/execution, not a general demonstration of adaptive
policy superiority or literature reproduction.

## 7. Ambiguities and known limits

1. **Experience in N×K:** productive effort is MIS exposure, while the
   ontology's generic “experience” is broader. Avoid describing N×K's
   competence matrix as an experience state. Nembhard's `D` has different
   explicit semantics.
2. **Teaching-effect observation:** the policy does not receive the private
   `T` tensor, but may infer it from a normalized teaching-gain signal. In
   the zero-noise legacy signal, when the denominator is positive, the
   normalization can reveal the selected relation's efficacy exactly; near
   saturation the denominator safeguard falls back to a prior. Noisy,
   information-aware paths need their own identifiability assessment. Thus
   “private parameter” does not alone imply “unidentifiable.”
3. **Factorial disable controls:** `mis_v2_transition_nk(enabled=False)` and
   teaching controls can disable physical transitions, but action catalogs
   may be changed by `teaching_enabled`. To isolate transition effects,
   keep the action catalog, feasible set, and resource accounting invariant
   where the estimand requires it; to isolate organizational availability,
   explicitly treat changed feasible actions as part of the intervention.
4. **Different policy objectives:** P0/P1/P2 rank production using current
   estimated competence and do not optimize a common long-horizon scalar
   reward. A factorial mechanism study must not infer the physical
   transition interaction from their closed-loop value alone.
5. **Performance and cost:** the implementation reports effort and CES,
   but effort is not automatically a cost penalty and CES is not a universal
   collective utility. Any objective combining them needs an explicit
   scientific definition.
6. **Observation timing and leakage:** records intentionally contain
   evaluator truth alongside policy information. Consumers must pass only
   the declared view to policies. Formative signals, posterior prediction
   through MIS and memory updates should be audited at their exact update
   points before treating “information interaction” as a clean factor.

## 8. Observability needed for the prioritized investigation

Priority under the 22 October analysis is *knowledge transfer × MIS-v2
learning × changing demand*. This section states what an interpretable
validation would need to control or observe; it is not a campaign design.

### Control / declare

- Initial true competence and initial estimates/posteriors separately.
- Per-cell MIS `eta` (or disabled transition), teaching rate `r`, relation
  efficacy tensor `T`, teaching effort, eligible relations and target rules.
- Same frozen exogenous demand trajectory, horizon, initial state, effort
  choices, individual limits, collective/problem budgets, reward definition,
  tie order, policy parameters and policy information for matched comparisons.
- Whether ablation removes a transition only or removes the teaching action
  and its resource charge too; these are different questions.
- Environment seed/trajectory separately from observation and policy
  randomness. Generated path must be reused rather than regenerated from
  policy-consumed random draws.

### Measure / trace per period

- Period, current problem ID/requirements, environment regime as
  evaluator-only metadata, and the exact policy decision view.
- Production allocation by agent and skill; teaching teacher, learner, skill
  and effort; feasible action catalog or its stable identifier.
- True competence immediately before production, after MIS, and after
  teaching; the two transition increments separately.
- Current production/individual outputs, functional outcome, CES/margin/
  deficit, productive effort, teaching charge, per-agent load, collective
  usage and unused capacity.
- Observations delivered to policy, posterior mean/variance before and
  after update, policy memory before/after, and relation efficacy signal.
- True efficacy and true competence only in evaluator-side diagnostics,
  never as policy input unless a declared full-information control.

Existing N×K teaching/information records provide much of this. Before
October 26 reuse assessment, verify that the selected runner mode can retain
all required fields together, that actual noisy observation/update ordering
matches the chosen estimand, and that disabled-mechanism comparisons preserve
the intended action/resource contract. No campaign should infer these from
the mere existence of fields in a different result type.

## 9. Open issues for the 26 October laboratory-reuse assessment

- Decide which result-record mode is authoritative for combined demand,
  MIS, teaching, imperfect information and policy memory; verify trace field
  completeness against the actual runner path.
- Establish whether and when the formative signal identifies relation
  efficacy, particularly under observation noise and competence saturation.
- State the intended factorial estimands: fixed-action mechanical
  transition interaction versus closed-loop organizational/value
  interaction, plus whether resource/action availability is held fixed.
- Confirm which policy information contract applies in every arm and that
  future demand/regime labels remain evaluator-only.
- Preserve mechanism-specific meanings: Nembhard productivity/experience,
  G0 development and MIS-v2 competence are not interchangeable.

These are reuse/observability questions, not a replacement roadmap and not
authorization to modify code or conduct experiments.

## 10. Source map

- Ontological scaffold: [`docs/hls_ontology.md`](../hls_ontology.md).
- MIS-v2 foundation: [`docs/theory/HLS_CAPABILITY_DEVELOPMENT.md`](../theory/HLS_CAPABILITY_DEVELOPMENT.md),
  `src/hls/hls_lab_nk_learning.py`.
- Competence and effort state: `src/hls/hls_lab_nk_geometry.py`.
- Production: `src/hls/hls_lab_nk_production.py`.
- Teaching and resources: `src/hls/hls_lab_nk_teaching.py`.
- Policies and decision view: `src/hls/hls_lab_nk_policies.py`.
- Demand: `src/hls/hls_lab_nk_environment.py`, `src/hls/synthetic/c5.py`.
- Estimation: `src/hls/hls_lab_nk_estimation.py`, `src/hls/hls_lab_dynamic.py`.
- Execution and traces: `src/hls/hls_lab_nk_execution.py`.
- Nembhard Direct: `src/hls/hls_lab_nk_nembhard.py`.
- Exact interaction identity and three mathematical investigations:
  [`HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md`](../research/HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md).
- Contract tests: `tests/test_hls_lab_nk_learning_transition.py`,
  `tests/test_hls_lab_nk_learning.py`, `tests/test_hls_lab_nk_teaching.py`,
  `tests/test_hls_lab_nk_policies.py`, `tests/test_hls_lab_nk_estimation.py`,
  `tests/test_hls_lab_nk_environment.py`, `tests/test_hls_lab_nk_execution.py`.

## 11. Cross-scenario formulation and boundary (consolidation note)

This section connects the existing A/B/C ontology to the S1–S4 scientific
scenarios; it does not replace the N×K definitions above. For the detailed
common state/action/observation model, scenario reductions, evidence status,
and research questions, see the [HLS unified scientific formulation](HLS_UNIFIED_FRAMEWORK.md).

The scenario portfolio uses one conceptual decomposition but **not one
homogeneous implementation contract**:

- **A — Scenario/system:** agent/task sets, demand, true capability state,
  exogenous environment, reward law, resources and feasible action set.
- **B — Mechanisms:** transitions in physical capabilities (e.g. MIS-v2),
  exogenous capability changes, and/or updates to estimates from feedback.
  These are distinct: S3a/S3b capability/reward changes are exogenous; S4
  MIS-v2 changes competence only through executed assignments; S3b estimators
  learn reward estimates without changing agent competence.
- **C — Organization:** a policy using its permitted observations and memory
  to select a feasible action. Matching, period-wise optimization, fixed
  policies, bandit-plus-matching adaptations, and finite-horizon planning are
  different decision rules, not interchangeable labels.

The canonical assignment scenarios use discrete one-to-one task units, while
the general N×K execution ontology also models divisible effort and optional
directed teaching. Thus `ProductiveAllocationNK` must not be assumed to be the
binary `x[i,k,t]` used by S1–S4. A scenario's reward, capacity, observation
timing and transition determine the action contract.

**Evidence boundary.** S1–S4 and the corresponding source/results are recorded
in the cumulative [engineering plan](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).
The exact finite-state claims are limited to their enumerated models. The
existence of shared ontology terms does not establish a universal HLS state,
algorithm, theorem, practical validity, or scalability. In particular, S3b's
evaluated GLR-CUCB iteration is complete, while the broader scientific line
on nonstationary combinatorial partial feedback remains open; S4's initial
tie-sensitive gap was later narrowed using BEST-MYOPIC before a separate
strict-gap family was verified.

**Temporal metadata note.** This source remains titled/versioned 2026-10-23,
while the consolidation note is recorded on 2026-10-21. That ordering is
retained rather than silently corrected; available repository evidence does
not establish whether the original date is prospective metadata or an error.
