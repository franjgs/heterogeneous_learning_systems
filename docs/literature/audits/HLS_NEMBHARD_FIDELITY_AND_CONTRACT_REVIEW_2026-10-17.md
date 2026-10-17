# Nembhard fidelity and External Mechanism Contract review

**Audit date:** 2026-10-17 (Europe/Madrid)
**Repository / branch:** `heterogeneous_learning_systems`, `feature/hls-laboratory-v1`
**Audited repository commit:** `57f4ebfe7c51e7762a6a1d0a2cef3e18011b5501`
**Scope:** source-PDF equation audit and read-only comparison with the current HLS N×K path. No simulator, algorithm, campaign result or frozen artifact was changed.
**Decision:** **REFRAME** — a separate direct-curve reference evaluator can be specified, but faithful implementation of the complete Nembhard model is **HOLD** pending source and PI decisions listed below.

## 1. Sources and versions checked

| Evidence | Version / identity | Use and status |
|---|---|---|
| Nembhard & Bentefouet, “Selection, Grouping, and Assignment Policies with Learning-by-doing and Knowledge Transfer,” *Computers & Industrial Engineering* 79 (2015), 175–187 | DOI `10.1016/j.cie.2014.11.006`; local 13-page PDF; SHA-256 `30129963aa6b69197140552b9431480b7b976d5c3d521eabbe3ec63478402e81` | Original source inspected directly with page-preserving PDF text extraction. Printed page numbers below are journal pages. |
| HLS source | Commit `57f4ebfe7c51e7762a6a1d0a2cef3e18011b5501` | Code paths and named functions in §7 were inspected at this revision. |
| HLS External Mechanism Contract v0.1 | `docs/literature/audits/HLS_EXTERNAL_MECHANISM_CONTRACT_V0_1_2026-10-17.md` in the audited worktree | Actual draft reviewed and amended in place; version stays v0.1, design-only. |
| HLS cross-model/code-reuse audits | `HLS_CROSS_MODEL_COMPARABILITY_MATRIX_2026-10-17.md`; `HLS_CODE_REUSE_AND_INTEGRATION_AUDIT_2026-10-17.md` | Secondary context only; not treated as a substitute for the original PDF or current source. |

The PDF metadata/content check confirmed a readable PDF and the hash above. BibTeX key: `nembhardbentefouet2015` in `docs/literature/references.bib`. The local PDF path is `docs/literature/competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf`.

## 2. Published equations and domain

### 2.1 Direct productivity curve — Eq. (1), printed p. 176

The article prints

\[
y=k\frac{x+p}{x+p+r},\qquad y,k,p,x\geq 0,\quad p+r>0.
\]

The source calls `y` work performance, `x` cumulative work in time or trials, `p` prior expertise in the same units, `k` the asymptotic performance level, and `r` cumulative production required for performance `k/2`. In the scheduling appendix, `P_ijt` is explicitly called a productivity rate; thus `k` has the same units as the modeled performance/rate, while `x,p,r` must share exposure units for the ratio to be dimensionless. The article does not state physical units beyond time/trials and does not specify an output-unit calibration in the equation itself.

The printed mathematical domain is wider than the usual positive-learning interpretation: `p+r>0` does not imply `r>0`. The paper's empirical simulation parameterization samples `log r` and exponentiates it, so sampled `r` is positive; this does not rewrite the domain printed next to Eq. (1).

For fixed parameters, write `D=x` and `z=D+p`. Where `D+p+r>0`,

\[
\frac{\partial y}{\partial D}=\frac{kr}{(D+p+r)^2},\qquad
\frac{\partial^2 y}{\partial D^2}=-\frac{2kr}{(D+p+r)^3}.
\]

Therefore, under the narrower conditions `k>0`, `p≥0`, `r>0`, `D≥0`, productivity is increasing and concave in direct exposure, starts at `kp/(p+r)`, and tends to `k` as `D→∞`. With `r=0` and the printed domain (which then requires `p>0`), the curve is constant at `k`. If `r<0` is allowed while `p+r>0`, the derivative is negative and the curve approaches `k` from above; monotone learning is not implied by the full printed domain.

Solving the equation gives

\[
y=k/2 \iff D+p=r.
\]

Thus `r` is the **total effective-exposure threshold** `D+p`; additional exposure from the current state is `r-p` only if `r-p≥0`. The article's prose description of `r` as production required to reach `k/2` is not generally an incremental-exposure statement when prior experience `p>0`. The contract and extraction now preserve this algebraic distinction; they do not alter the published equation.

### 2.2 Direct plus indirect experience — Eq. (2), printed p. 176

\[
y=k\frac{hT+x+p}{hT+x+p+r}.
\]

The text calls `T` the pool of other operators' cumulative work/knowledge and `h` an individual transfer factor. It says `h` may represent positive or negative transfer generally and notes that restricting `h` to `[0,1]` gives positive transfer only. The displayed Eq. (1) admissibility statement is not restated for Eq. (2); the paper supplies no complete domain guaranteeing a positive denominator under arbitrary negative transfer. `h` is described as a percentage, but the operational Appendix A-3 definition of `T` raises a dimensional question (§4.2).

### 2.3 Worker-task-period curve — Eq. (3), printed p. 177

\[
y_{ijt}=k_{ij}\frac{\theta_{ij}T_{ijt}+\sum_{k=1}^{t}x_{ijk}+p_{ij}}
{\theta_{ij}T_{ijt}+\sum_{k=1}^{t}x_{ijk}+p_{ij}+r_{ij}}.
\]

The paper identifies worker `i`, task `j`, and production period `t`; the direct term counts assignments through and including the current period. This equation omits period duration `L`. Parameter symbols are indexed by worker and task here, while the simulation text says workers on a machine type share learning and transfer parameter values; individual experience and performance are still accounted for. This is a stated simulation restriction, not a general HLS identity.

## 3. Temporal convention: Eq. (3) versus Appendix A-4

Appendix A-4, printed p. 185, gives

\[
P_{ijt}=k_{ij}\frac{\theta_{ij}T_{ijt}+\sum_{k\leq t}Lx_{ijk}+p_{ij}}
{\theta_{ij}T_{ijt}+\sum_{k\leq t}Lx_{ijk}+p_{ij}+r_{ij}}.
\]

The appendix makes `L`, period duration, explicit in direct exposure, unlike Eq. (3). Both include the assignment at period `t`; the paper does not say whether productivity/output for period `t` is evaluated before or after that period's work exposure. It also does not state that `L=1` is the normalization intended in Eq. (3). Consequently there is no single source-established convention for exposure units and current-period timing. A reproduction may not silently choose one; any adapter convention is a new, labelled modeling decision.

## 4. Indirect transfer, production and objective

### 4.1 Appendix A-3: peer exposure

Appendix A-3, printed p. 185, defines (with source indices retained)

\[
T_{ijt}=\sum_{q=1,\,q\ne j}^{9} y_{qj}
\left[\sum_{p=1,\,p\ne i}^{45}\left(\sum_{k\leq t}x_{pqk}P_{pqk}\right)\right],
\]

where the printed text describes `y_qj` as an indicator for tasks of the same type. The formula:

- excludes the focal worker `i` in the worker sum;
- excludes the focal task `j` in the task sum;
- includes only other tasks `q` of the same type as `j`;
- weights other workers' assignments by productivity `P_pqk`;
- includes periods through and including `t`.

It is therefore not merely a count of exposure or a directed lesson. It is endogenous, same-type, productivity-weighted peer experience.

Because A-3 includes `k=t` and current-period `P_pqt`, while Eq. (3)/A-4 defines current-period `P_ijt` from `T_ijt`, a literal simultaneous reading produces contemporaneous dependencies among peer productivities. The paper neither specifies a sequential causal order nor formulates/solves an implicit fixed-point system, nor supplies conditions for existence or uniqueness. This is an **unresolved source ambiguity**. A lagged transfer rule or a same-period fixed-point algorithm would each be an implementation choice, not a verified author convention.

### 4.2 Output, dimensional consistency and objective

Appendix A-1 defines `S_jt=Σ_i O_ijt`. A-2 prints `O_ijt=Σ_{k≤t}x_ijk P_ijk` (printed p. 185). The prose calls `O_ijt` worker output “at time t,” A-1 calls `S_jt` task output “in period t,” but A-2 is cumulative over all periods through `t`. A-2 contains no explicit `L`, although A-4 includes `L` in experience and calls `P` a productivity rate. The parallel objective maximizes `Σ_j Σ_t S_jt`; if `S_jt` literally includes cumulative past output, this objective counts prior output again in later periods. The article does not reconcile those statements. It is therefore unsafe to replace A-2 by a period flow, insert `L`, difference cumulative output, or call the printed objective a conventional one-time sum of period production without identifying that as an alternative interpretation.

There is also a unit question in A-3/A-4. A-4 adds `Lx` (time exposure) to `θT`; A-3 constructs `T` from assignment indicators multiplied by productivity rates. If `P` is output/time, `T` does not transparently have the same units as `Lx`; the paper does not give a unit for `θ` that resolves this, despite describing transfer as a percentage. A-2 likewise multiplies a binary assignment by a rate and sums it without an explicit period duration. These are dimensional/notation ambiguities in the published formulation, not corrected equations.

For the serial system, A-7–A-9 replace the parallel aggregate-output objective with the sum of three line throughputs, each the minimum of the cumulative outputs for its three sequential stations. The paper says this is equivalent, in objective value, to omitting buffer constraints and maximizing the least productive task on each line, citing earlier work. The distinction between parallel total output and serial bottleneck throughput is essential; neither is HLS CES.

## 5. Organizational constraints, heuristics and reproduction conditions

The article's simulation has three machine types with three identical instances each (nine tasks), a sampled pool of 45 workers, nine selected workers, and three teams of three associated with machine types (printed pp. 177–179). Workers can transfer knowledge while staffing tasks of the same machine type, not across types (p. 178). Its three consecutive stages are:

1. **Selection:** retain nine from 45 using MaxiMax or MaxiMin for each of five criteria `k`, `p`, `1/r`, `h`, and expected output `O` (ten criteria).
2. **Grouping:** partition the selected workers into three teams of three using maximum or minimum within-team variance for the criteria (ten alternatives).
3. **Assignment:** assign teams to task types by MaxiMax or MaxiMin for the same five criteria (ten alternatives).

The combinations yield 1,000 treatment combinations; stages are also analyzed separately. The random baseline samples nine, groups them arbitrarily into threes, and randomly assigns the teams. The article uses 25 replications, each with a new population of 45, and describes a horizon equivalent to one year (pp. 179, 182). The source does not fully fix tie-breaking and all operational details needed for exact algorithm replay.

Appendix constraints A-5/A-6 require exactly one worker on each of nine tasks per period and at most one task per worker per period; assignments are binary. These are not the HLS fractional/discrete effort constraints. The printed MINLP does not specify an HLS-like shared effort budget or resource cost.

Empirical fitting uses timestamps for 176,000 items inspected by 75 workers; Eq. (3) fits have mean `R²=.96`, SD `.02` (pp. 177–178). `log(k), log(p), log(r)` are jointly normal with Table 1 means `(1.448, 1.963, 2.0446)` and covariance matrix

\[
\begin{bmatrix}.0045&.0167&.0191\\.0167&.4621&.2443\\.0191&.2443&.1905\end{bmatrix}.
\]

The transfer parameter is normal with mean `.664`, variance `.409`, untransformed; the conclusion states it is sampled independently of learning parameters. No truncation/bounds for that normal draw are stated. Reported outputs (including Table 6/7) are source results and have not been rerun in this audit. Raw fitted worker-level data, RNG/seed conventions, full solver settings and complete tie rules are not available in the paper extraction; exact numerical reproduction is not established.

## 6. HLS compatibility audit

Evidence below is from the audited commit; function and class references are authoritative even where prose in older state documents is stale.

| HLS interface | Verified implementation | Compatibility and minimum safe treatment |
|---|---|---|
| Organization state | `OrganizationStateNK` and `OrganizationConfigNK`, `src/hls/hls_lab_nk_geometry.py:47–126`; actual and estimated `N×K` competence in `[0,1]` | **Not an Nembhard productivity state.** Keep `k,p,r`, exposure and productivity separate; do not store them as competence. |
| Task/problem | `ProblemSpecNK`, same file `:129–165`; K-vector requirements, CES weights, shared per-problem effort budget | Nembhard task/machine **type** is not an HLS skill coordinate. A type-to-problem/skill map would be an explicit HLS adaptation; source type has three classes and nine replicated tasks, independently of K. |
| Production and outcome | `productive_outputs_nk`, `evaluate_problem_nk`, `ces_reward_nk`, `p0_rank_nk`, `src/hls/hls_lab_nk_production.py:22–105` | HLS production is `y_k=Σ_i e_ik C_ik`; source productivity is a nonlinear worker-task experience rate. HLS functional success and weighted CES are not source throughput. No source-to-CES equivalence exists. |
| Action/resources | `ProductiveAllocationNK`, `validate_productive_allocation_nk`, and catalogue enumeration, `src/hls/hls_lab_nk_geometry.py:14–20,168–175` and below | HLS action is N×K effort, with individual and shared budgets and discrete effort catalogues. Nembhard uses binary worker-task-period assignment and exclusivity. Reuse of HLS effort as duration/exposure is unsupported; require a separate unit-bearing exposure/duration and native feasibility contract. |
| MIS-v2 | `mis_v2_transition_nk`, `src/hls/hls_lab_nk_learning.py:53–93`, delegates scalar law to `discover_develop_v2.py:17–80` | MIS-v2 updates bounded competence as `1-(1-c)exp(-λe)`; it is not Nembhard's productivity curve. It may remain a separately named comparator, never be rewritten or substituted for source `P`. |
| Teaching | `teaching_transition_nk`, `src/hls/hls_lab_nk_teaching.py:139–180`; resources at `:183–220` | Explicit one-learner transfer uses HLS relation efficacy and `min(1,c+r e T(1-c))`; it is not A-3's endogenous same-type peer exposure. Do not reuse as Nembhard transfer. |
| Policy boundary | `NKDecisionView`, `NKCoordinationPolicy.choose`, P0/P1/P2 classes, `src/hls/hls_lab_nk_policies.py:109–230` | Policies receive estimates and feasible joint actions; they do not implement Nembhard's three-stage selection/grouping/assignment heuristics. A future adapter must implement source decision variables and information explicitly, not relabel P0/P1/P2. |
| Environment/execution | `generate_environment_trajectory_nk`, `src/hls/hls_lab_nk_environment.py:170–198`; runner `_run_nk_information_sequence`, `src/hls/hls_lab_nk_execution.py:384–620` | HLS can freeze/replay exogenous demand and record policy-dependent execution. Nembhard's fixed nine-machine scheduling design is not an exogenous demand generator. Common demand does not make actions or exposure paths equal. |
| Observation/estimation | `CompetencePosteriorNK`, `initialize_competence_posterior_nk`, `assimilate_production_observations_nk`, `src/hls/hls_lab_nk_estimation.py:21–114` | HLS posterior estimates normalized competence, not Nembhard curve parameters or productivity. Parameter uncertainty/fitting needs a distinct observation/state contract; do not infer exact `k,p,r` from HLS competence posterior. |

The existing API offers useful scaffolding (immutable N×K state, explicit problem/action contracts, resource validation, deterministic exogenous paths, traces), but not a general external-model plugin. A safe first direct-law evaluator could be pure and separate; it need not accept `OrganizationStateNK` directly. Any adapter to HLS must declare task-class mapping, state dimensions, exposure units/timing, productivity units, feasibility and output mapping. Such choices are **new HLS modeling decisions**, not source facts.

## 7. Corrections made to Contract v0.1

The contract was reviewed in place without changing its version, design-only status, scope or authorization. Corrections/clarifications added:

1. Revision provenance now records this source-PDF/code review rather than describing all source facts as inherited only from an earlier audit.
2. The `k/2` property is solved explicitly: `D+p=r`; `r` is not generally remaining exposure when `p>0`.
3. The equation's printed domain is distinguished from the positive-`r` empirical sampling convention.
4. Appendix A-3/A-4 contemporaneous peer dependence is named as an unresolved implicit-dependence issue; no causal sequence or fixed-point rule is attributed to the authors.
5. The cumulative A-2 expression, A-1 period-output wording/objective, missing explicit duration, and units of `θT` are recorded as source ambiguities; no repaired equation is substituted.
6. Contract stop gates now require resolving or explicitly scoping these points before a full source reproduction claim.

Corrections 1–5 are source-backed clarifications. Any later choice of a lagged transfer, fixed-point solve, `L` convention, period-flow interpretation, type mapping, or output bridge would be a **new HLS decision** requiring review.

## 8. Ambiguities that remain open

| Open issue | What the paper establishes | What it does not establish | Disposition |
|---|---|---|---|
| Eq. (3) vs A-4 duration | Main equation uses assignment count; appendix uses `Lx` | Whether Eq. (3) assumes unit-duration periods | Keep separate; no full reproduction claim. |
| Current-period learning/exposure | Both direct terms include `t` | Whether period-t output uses pre- or post-exposure productivity | Requires PI-approved convention or source clarification. |
| A-3/A-4 simultaneity | A-3 uses productivity-weighted peers through `t`; A-4 depends on `T_ijt` | Sequential causal order vs simultaneous fixed point, and fixed-point conditions | Do not implement peer transfer yet. |
| A-2 output | Printed cumulative sum `Σ_{k≤t}xP` | Whether `O,S` mean cumulative or per-period flow and whether `L` multiplies rate | Do not alter the published expression; reproduction is blocked on interpretation. |
| Dimensional consistency | P called rate; A-4 uses duration in exposure; A-3 sums assignment×P | Units for `T`, `θ`, A-2 and the objective | Record units if an adapter is proposed; source does not settle them. |
| Transfer-factor distribution | Mean/variance and untransformed normal stated | Whether sampled values are truncated or bounded | No silent clipping or `[0,1]` assumption. |
| Exact policies/reproduction | Ten candidate heuristics per stage and 1,000 combinations described | All tie rules, exact solver details, raw fitted data and RNG conventions | Do not claim exact policy or numerical reproduction from source description alone. |

The original source does identify the worker/task assignment constraints, grouping structure, broad heuristic criteria, data-fitting origin and replication scale. It is not enough to recover a bitwise/numerically exact source simulation.

## 9. Minimum tests before any later implementation

These are recommendations, not tests run in this documentation phase.

**Pure Eq. (1) evaluator:** independent hand calculations for `D=0`, `D+p=r`, `p>r`, `r=0` within the printed domain, positive-`r` monotonicity/concavity, asymptote, and valid/invalid denominator. Test dimensions and units in the adapter contract; do not use HLS production as oracle.

**Exposure bookkeeping:** verify both explicitly labelled Eq. (3) and A-4 conventions on fixed assignments with `L≠1`; do not assert equality. Test current-period inclusion as a chosen adapter rule, not as settled source timing.

**Transfer (only after source/PI decision):** independently verify A-3 exclusions (`p≠i`, `q≠j`), same-type indicator, productivity weighting, periods, and teacher/learner effects. If retaining simultaneous terms, establish and test the actual numerical solution and conditions; otherwise record a model adaptation. Never use `teaching_transition_nk` as the source transfer oracle.

**Output/objective:** independently test A-1/A-2 literally and a separately named interpretation only if approved. Verify rate/time/output dimensions and whether objective accumulation double-counts. Test parallel and serial objectives separately.

**Organization/reproduction:** binary exclusivity, exactly-one-worker coverage, three machine types × three instances, worker selection 45→9, teams of three, all documented criterion combinations, random baseline, and published tables where source data/settings suffice. Failure to access missing raw parameters/solver details must be reported as non-reproduction, not repaired from HLS defaults.

## 10. Decision

**REFRAME** the proposed work as a source-specific, fidelity-gated direct-productivity-law evaluator, isolated from HLS competence and CES. This limited mathematical evaluator is tractable and testable. **HOLD** any implementation of indirect transfer, full Nembhard reproduction, integration into HLS P0/P1/P2 or a scientific campaign until PI resolves the timing/output/dimensional ambiguities or explicitly authorizes a labelled interpretation. No claim of newness or superiority follows from this review.

## Source and code reference index

- Nembhard & Bentefouet (2015), original PDF, printed pp. 176–179, 182, 184–185; local SHA above. Equations (1)–(3), Tables 1–2, Appendix A equations (A-1)–(A-9).
- `docs/literature/audits/Nembhard_Bentefouet_2015_Mathematical_Extraction.md`, especially §§1–6 and source page map; corrected alongside this report for the `r` interpretation and Appendix ambiguities.
- `src/hls/hls_lab_nk_geometry.py`: `OrganizationStateNK` (47–80), `OrganizationConfigNK` (84–126), `ProblemSpecNK` (129–165), `validate_productive_allocation_nk` (168 onward), catalogue enumeration (`enumerate_productive_action_entries_nk`).
- `src/hls/hls_lab_nk_production.py`: `productive_outputs_nk` (22–40), `evaluate_problem_nk` (43–59), `ces_reward_nk` (62–78), `p0_rank_nk` (81–90).
- `src/hls/hls_lab_nk_learning.py`: `LearningProfileNK` and `mis_v2_transition_nk` (16–93); `src/hls/discover_develop_v2.py`: `eta_to_lambda` (17–21), `capability_after_exposure` (24–39), `mis_v2_transition` (53–73).
- `src/hls/hls_lab_nk_teaching.py`: `TeachingActionNK`, `TeachingEfficacyNK`, `TeachingParametersNK`, `teaching_transition_nk` (28–180), `validate_joint_action_resources_nk` (183 onward).
- `src/hls/hls_lab_nk_policies.py`: `NKDecisionView`, `NKCoordinationPolicy`, P0/P1/P2 (`109–230`).
- `src/hls/hls_lab_nk_environment.py`: `DemandRegimeNK`, `ExogenousEnvironmentConfigNK`, `EnvironmentTrajectoryNK`, `_emission_seed`, `generate_environment_trajectory_nk` (35–198).
- `src/hls/hls_lab_nk_execution.py`: `_run_nk_information_sequence` (384–620), including policy view, actual-state production, MIS-v2, teaching and estimator update order.
- Focused HLS tests previously recorded in `HLS_CODE_REUSE_AND_INTEGRATION_AUDIT_2026-10-17.md` passed 184 tests at the audited revision; they validate HLS contracts, not Nembhard fidelity. No scientific campaign was run here.
