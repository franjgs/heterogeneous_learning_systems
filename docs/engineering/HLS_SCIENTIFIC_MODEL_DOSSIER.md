# HLS Laboratory — Scientific Model and Evidence Dossier

**Audit source commit:** `e8e115030e064df23f07f1b5824264f97513099a`\
**Dossier record:** 2026-10-16 20:44 +02:00 (Europe/Madrid).\
**Scope:** source-to-equation audit of the original 3×2 laboratory and its current N×K path; one deterministic diagnostic trace. No scientific model or frozen result was changed.\
**Status:** evidence dossier, not a claim of scientific validity; HLS Laboratory remains **PARTIAL**.

## 1. Executive summary

The current laboratory is a deterministic, finite-horizon simulator of organizations that allocate discrete productive effort across competencies, can apply MIS-v2 learning by doing, can direct at most one lesson per period, receive imperfect scalar observations, update bounded competence posteriors and teaching-efficacy memory, and face exogenous task demand. N×K modules generalize the containers and reuse historical scalar rules; the historical 3×2 modules remain the principal compatibility reference.

Its physical production is additive. Multidimensional functional requirements can make capabilities complementary for task feasibility, but no production synergy is present. CES is gross output aggregation, not net utility. P0/P1/P2 are specific deterministic heuristics, not optimizers of cumulative CES or globally optimal organization policies. The model supports controlled conditional comparisons inside its declared action catalog and transition rules; it does not alone validate the constructs against real organizations.

One semantic distinction needs expert attention: the historical G3/G3-H record calls its one-unit law `s + η(1-s)^2` the MIS diminishing law, whereas the current DISCOVER-v2 MIS-v2 law at unit effort is `s + η(1-s)`. The equations and code are explicit; this dossier preserves both rather than treating them as interchangeable. G3/G3-H are separate analytical scenarios, not the current N×K transition.

## 2. Scope, evidence labels, and notation

Labels used below:

- **FACT FROM SOURCE:** directly implemented or explicitly frozen in a cited artifact.
- **MATHEMATICAL DEDUCTION:** follows algebraically from the stated equation and domains.
- **INTERPRETATION:** a scientific reading of a formal variable or rule.
- **UNVERIFIED ASSUMPTION:** accepted by the simulator but not empirically calibrated here.
- **OPEN SCIENTIFIC QUESTION:** cannot be resolved from source inspection or current tests.

Let `i∈{1,…,N}` index agents, `k∈{1,…,K}` competencies, and `t` periods. `c_ik(t)∈[0,1]` is actual competence; `ĉ_ik(t)∈[0,1]` is the organization’s estimated competence. `e_ik(t)≥0` is productive effort. Problem `p_t` has requirement `r_k≥0`, evaluation weight `w_k≥0`, and `Σ_k w_k=1`. Unless stated otherwise, all source references below are pinned to audit commit `e8e115030e064df23f07f1b5824264f97513099a`.

## 3. Production, functional success, CES, and resources

### Production

**FACT FROM SOURCE.** The current production equation is

\[
y_k(t)=\sum_{i=1}^{N} e_{ik}(t)c_{ik}(t),\qquad
y_{ik}(t)=e_{ik}(t)c_{ik}(t).
\]

`y_ik` is an agent–competence contribution; `y_k` is aggregate output in competence dimension `k`. Production uses actual, pre-transition competence, never estimates. Effort is dimensionless/resource-normalized in the implementation; competence is normalized to `[0,1]`; output inherits effort units. This is a model convention, not an empirically calibrated production unit.

**MATHEMATICAL DEDUCTION.** For fixed nonnegative efforts, output is linear and nondecreasing in each actual competence. Holding competence fixed, it is linear and nondecreasing in each effort. There are no cross-products `c_ik c_jk`, task complementarities, congestion, quality interactions, or stochastic output shocks.

### Functional evaluation

For each active dimension `A={k:r_k>0}`, the implementation defines

\[
d_k=\max(0,r_k-y_k),\quad
D=\sum_{k\in A}\frac{d_k}{r_k},\quad
m=\min_{k\in A}(y_k-r_k),
\]

\[
\operatorname{success}=\mathbf 1\{y_k+10^{-12}\ge r_k\;\forall k\in A\}.
\]

Zero-requirement dimensions are excluded from `D` and `m`. Success is a hard threshold; `D` and `m` are separate descriptive rankings. It is mathematically monotone in output in the sense that increasing any output cannot turn success into failure and cannot increase normalized deficit.

### CES performance

The registered aggregation is

\[
CES(y;w,\rho)=\left(\sum_{k=1}^{K}w_k y_k^{\rho}\right)^{1/\rho},
\qquad \rho=0.5 \text{ by default},
\]

with finite nonnegative output, nonnegative weights summing to one, and finite nonzero `ρ`. At the default `ρ=.5`, this is `(Σ_k w_k√y_k)^2`. It is gross functional reward. No resource price is subtracted; consumption and unused capacity are reported separately. Zero-weight dimensions do not affect CES. This is neither profit, welfare, nor net utility.

`P0` ranks actions lexicographically by `(success, −D, m, −productive effort)`, not by CES. Consequently policy choice and the reported gross outcome measure are not the same objective.

### Resource contract

The effective collective budget is `B_eff=min(B_org,B_problem)`. For a teaching event of effort `q`, the teacher and learner each incur `q`, so

\[
R_{used}=\sum_{i,k}e_{ik}+2q\le B_{eff};\quad
\sum_k e_{ik}+q\mathbf 1\{i\text{ is teacher or learner}\}\le L_i.
\]

Without teaching, set `q=0`. Unused collective capacity is `max(0,B_eff−R_used)`. This is effort accounting, not an economic cost conversion. Discrete action catalogs can leave capacity unused.

**Source mapping:** historical production/CES: [`discover_v0.py`, `production_inputs`, `ces_reward`, lines 27–48 and 95–115](../../src/hls/discover_v0.py); historical functional evaluator and frozen feasible set: [`hls_lab_v1.py`, `ProblemSpec`, `evaluate_problem`, `feasible_actions`, lines 33–69, 135–164](../../src/hls/hls_lab_v1.py); current dimensional production/CES/P0 score: [`hls_lab_nk_production.py`, functions `productive_outputs_nk`, `evaluate_problem_nk`, `ces_reward_nk`, `p0_rank_nk`, lines 22–105](../../src/hls/hls_lab_nk_production.py); dimensions/resources: [`hls_lab_nk_geometry.py`, `OrganizationConfigNK`, `ProblemSpecNK`, `validate_productive_allocation_nk`, lines 47–184](../../src/hls/hls_lab_nk_geometry.py); joint-resource validation: [`hls_lab_nk_teaching.py`, `validate_joint_action_resources_nk`, lines 183–229). The N×K tests independently recompute production, CES, success and resources in [`test_hls_research_readiness.py`](../../tests/test_hls_research_readiness.py).

### Complementarity and emergence

**FACT FROM SOURCE / INTERPRETATION.** Multiple output requirements can require combining contributions from different agents. This is functional feasibility complementarity (coverage under an additive production equation). It is not superadditivity, synergy, or an interaction term in production. The historical `complementarity_class` explicitly compares team feasibility to single-agent feasibility under the same catalog/caps; its labels are operational feasibility labels.

**OPEN SCIENTIFIC QUESTION.** The simulator defines no baseline-relative, invariant, or otherwise independent criterion for “collective emergence.” It therefore supports statements about measured collective outcomes under specified organization/action constraints, but not a claim that emergent collective intelligence or synergy has been established.

## 4. MIS-v2 learning by doing

The authoritative current MIS-v2 implementation is DISCOVER-v2. For declared one-unit gap-closure parameter `η∈(0,1)`,

\[
\lambda(\eta)=-\ln(1-\eta),\qquad
c'_{ik}=1-(1-c_{ik})\exp[-\lambda(\eta_{ik})e_{ik}].
\]

Equivalently, the gain is

\[
\Delta c_{ik}=(1-c_{ik})[1-\exp(-\lambda(\eta_{ik})e_{ik})]
=(1-c_{ik})[1-(1-\eta_{ik})^{e_{ik}}].
\]

Parameters are per agent–competence in the N×K adapter. The mechanism is cellwise: the required trigger is positive productive effort for that same cell. It does not depend on task success, demand label, other agents’ effort, teaching efficacy, or other skills. Production and reward use the pre-learning state; learning affects subsequent decisions/periods.

**MATHEMATICAL DEDUCTIONS, for `η∈(0,1)`, `e≥0`, `c∈[0,1]`:**

- `e=0` or disabled mechanism gives `c'=c`; `η=0` is not a legal profile, so the zero-learning control is MIS OFF.
- `c'∈[c,1]⊆[0,1]`; gain is zero at `c=1` and positive for `c<1,e>0`.
- Gain is nondecreasing in effort and eta, and nonincreasing in current competence. For fixed η,e, `∂c'/∂c=exp(−λe)∈(0,1]`.
- Repeated exposures with rates `λ_j` and efforts `e_j` compose exactly as `c_n=1−(1−c_0)exp(−Σ_j λ_j e_j)`. With fixed positive exposure, competence approaches 1 asymptotically; it reaches 1 in finite computation only from the boundary or through floating-point rounding.
- No cross-agent or cross-skill update follows from the equation.

The original scalar functions are `eta_to_lambda` and `capability_after_exposure`; the N×K adapter applies them cellwise. See [`discover_develop_v2.py`, lines 33–71](../../src/hls/discover_develop_v2.py), [`hls_lab_nk_learning.py`, `LearningProfileNK` and `mis_v2_transition_nk`, lines 16–91](../../src/hls/hls_lab_nk_learning.py), and runner ordering in [`hls_lab_nk_execution.py`, lines 502–584](../../src/hls/hls_lab_nk_execution.py). Independent transition tests: [`test_hls_lab_nk_learning_transition.py`](../../tests/test_hls_lab_nk_learning_transition.py).

### Historical-law discrepancy: MIS/G3 versus current MIS-v2

The G3/G3-H source uses `min(1,s+η(1−s)^2)` per exposed cell at its unit/binary assignment, and the minimal reference scenario calls this a diminishing rule. The DISCOVER-v2 law above at effort `e=1` is `s+η(1−s)` (algebraically below 1). These are not the same transition. G3 documentation states that it retains the MIS saturating law; G3’s own source and equation are reproducible, but the documentation does not explain the equation change relative to DISCOVER-v2. **This is an unresolved cross-model naming/lineage discrepancy, not silently treated as a current N×K defect.** A reviewer should decide whether “MIS” denotes a family of historical laws or whether the G3 equivalence statement needs a separately authorized correction.

References: [`discover_develop_v0.py`, `mis_v0_transition`, lines 14–35](../../src/hls/discover_develop_v0.py); [`discover_develop_v2.py`, lines 33–71](../../src/hls/discover_develop_v2.py); [`g3_organizational_value.py`, `learning_increment`, lines 52–66](../../src/hls/g3_organizational_value.py); [G3/G3-H ground truth, §§2, 11](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md); [minimal reference scenario, §§1, 4–6](../experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md).

## 5. Directed teaching

For directed event `a=(i,j,k,q)` (teacher `i`, distinct learner `j`, target skill `k`, effort `q`), teaching efficacy `T_{ijk}∈[0,1]`, and scalar transfer rate `r∈(0,1]`, the source applies after MIS-v2:

\[
g_{ijk}=r q T_{ijk}(1-c^{MIS}_{jk}),\qquad
c^{teach}_{jk}=\min(1,c^{MIS}_{jk}+g_{ijk}).
\]

All other cells are unchanged. Teacher competence is absent directly from the equation. Since `rqT∈[0,1]`, the algebraic update already lies in `[c,1]`; `min` is a guard. Direct gain is zero if `T=0`, `q=0`, `r=0` (although `r=0` is disallowed), or learner is at 1. At positive remaining gap, gain is nondecreasing in `r`, `q`, and `T` holding the rest fixed. It need not increase team output or CES: the taught cell may not be assigned or demand may not use it.

The legacy implementation computes teacher/learner/skill indices, uses `transfer_rate*effort*efficacy*(1-real_skill)`, changes only the learner cell, and charges effort to both parties. The N×K function preserves it. Runner order is production and outcome → MIS-v2 → teaching; the lesson uses post-MIS learner competence. See [`hls_lab_v1_integrated.py`, `TeachingEvent`/`TeachingEfficacy`/parameters, lines 43–133; transition body, lines 493–546](../../src/hls/hls_lab_v1_integrated.py), [`hls_lab_nk_teaching.py`, efficacy/action/transition, lines 28–179](../../src/hls/hls_lab_nk_teaching.py), and [`hls_lab_nk_execution.py`, lines 519–576](../../src/hls/hls_lab_nk_execution.py).

Two interpretations are compatible with the code but imply different scientific scope:

1. **Pedagogical capability interpretation:** `T[i,j,k]` is an independent dyadic/skill-specific teaching capability; an instructor need not have high productive competence in `k`. This allows low-competence instructors to transfer skill when the configured T is high, but requires independent interpretation/calibration of T.
2. **Expertise proxy interpretation:** T is intended to proxy subject expertise plus pedagogy. Then the configuration must encode a defensible relationship between teacher competence and T, or the model omits an intended dependency. That relationship is not imposed by current physics.

No change is made here. The distinction matters for teacher eligibility, comparative advantage, the meaning of teaching efficacy, and claims about knowledge transfer.

## 6. Organization, action geometry, and policies

`OrganizationConfigNK` carries ordered unique agent/skill IDs, an N×K actual competence matrix, optional separate initial estimates, per-agent limits, and collective budget. `ProblemSpecNK` carries problem ID, K requirements, budget, and K evaluation weights. Current `OrganizationStateNK` stores actual and estimated matrices. No network/organizational hierarchy beyond directed efficacy relations is represented.

Productive actions are the Cartesian product of ordered per-agent effort vectors. For K=2 the historical default is `((0,0),(0,1),(.5,.5),(1,0))`; for K other than 2 caller supplies ordered catalogs. The full candidate count is the product of catalog lengths and is rejected above `max_candidates`, never silently truncated. Feasibility filtering preserves full-catalog IDs and order. Default 3×2 production catalog has 4³=64 entries. Joint candidates iterate each feasible production allocation, then no-teaching, then directed teacher/learner/skill order; at most one lesson is represented. The historical 508 integrated-action fixture is specific to its frozen budget/action conditions, not a universal formula for all configurations. The raw upper bound with teaching is `M[1+N(N−1)K]`, where `M` is full production candidate count; resource feasibility can remove many.

Distinctions: a **candidate** belongs to the full Cartesian catalog; a **feasible** candidate passes resource checks; a **policy-selected** action is returned by P0/P1/P2; an **executed** action is validated by the runner. They should not be interchanged in reports.

P0: selects the first catalogue action maximizing `(success,−D,margin,−effort)`, with production only. P1: for a configured directed relation, selects its best feasible lesson action by the same production score, falling back to best production-only if no such lesson is feasible. P2: selects best production-only if it currently succeeds; otherwise considers configured relations whose target skill is required and learner estimate is below target; first unseen eligible relation is explored in configured order, else the relation with highest observed running-mean efficacy is used only if it meets threshold; otherwise fallback to production-only. Within candidate class, ties retain the first catalog action. P2's evidence is a running mean of normalized noisy formative signals. No policy evaluates future return, optimizes cumulative CES, or solves a global assignment/development problem.

The policy decision view carries estimates, requirements, feasible actions, and public efficacy memory—not actual competence, private T, observations or latent environmental states in imperfect mode. P0/P1/P2 comparison identifies these distinct policy packages under a matched setup; it does not isolate architecture effects unless architecture is separately varied with appropriate matching. Numeric-index relation and catalog tie-breaking mean policy decisions need not be permutation-invariant even though physical equations are equivariant under consistent relabeling.

References: [`hls_lab_nk_geometry.py`, lines 47–256](../../src/hls/hls_lab_nk_geometry.py); [`hls_lab_v1_integrated.py`, policies and 3×2 catalog, lines 204–323](../../src/hls/hls_lab_v1_integrated.py); [`hls_lab_nk_policies.py`, P0/P1/P2 and action enumeration, lines 105–327](../../src/hls/hls_lab_nk_policies.py); tests pin 64/508 and legacy decisions in [`test_hls_lab_v1_integrated.py`](../../tests/test_hls_lab_v1_integrated.py), [`test_hls_lab_nk_policies.py`](../../tests/test_hls_lab_nk_policies.py).

## 7. Observation, estimation, and efficacy memory

In the historical 3×2 dynamic estimator, one bounded scalar posterior is maintained per agent–skill cell. Its support is either `{0,m,1}` or a uniform grid (default 101 points); initialization constructs endpoint masses to match declared prior mean/variance and adds a `10⁻¹²` uniform grid floor in grid mode. These are declared priors, not fitted empirical priors.

Individual production observation for a cell is

\[
o_{ik}=e_{ik}c_{ik}+\sigma_p Z_{t,i,k},\quad Z\sim N(0,1),
\]

with coordinate-indexed deterministic innovations. For positive effort and `σ_p>0`, likelihood is proportional to `exp[−.5((o−e c)/σ_p)^2]` on each posterior support point. With zero effort, the posterior is unchanged. In the legacy code, `σ_p=0` and positive exposure collapse the posterior to the clipped ratio `o/e`; this is a special noiseless-observation rule, not the general default. Current trace code does not clip generated noisy observations to `[0,1]`; noise can yield negative observations, while the latent competence and posterior support remain bounded.

Temporal sequence in imperfect mode: (1) policy sees current posterior means/memory; (2) production and reward use actual pre-transition competence; (3) production observations are generated from pre-transition contribution; (4) actual MIS-v2 is applied; (5) observations update the posterior; (6) posterior is pushed through public MIS-v2 parameters if MIS is enabled; (7) teaching is applied to actual post-MIS learner skill; (8) noisy formative teaching outcome is observed; (9) efficacy memory is updated if organizational learning is on; (10) posterior competence support is pushed by the memory-based teaching estimate. This is the implemented composition, even though the conceptual statement “production → MIS → teaching” alone omits the estimator substeps.

Formative teaching signal is `o^T/[r q(1−ĉ_afterMIS)]` when denominator exceeds tolerance; otherwise efficacy prior mean is used. The running mean is clipped to `[0,1]`. This is separate from competence posterior and P2 memory.

Perfect mode bypasses the estimator and sets decision estimate equal to actual competence after transitions. Imperfect mode is initialized from declared estimates, actual truth stays private, and policy views exclude actual state and true efficacy. Estimates may nevertheless be inaccurate due prior, grid, observation/action path, and model assumptions. No empirical bias, identifiability or leakage incidence is claimed. The N×K wrappers preserve the scalar update. Refs: [`hls_lab_dynamic.py`, posterior/initialization/update/noise, lines 58–215](../../src/hls/hls_lab_dynamic.py); [`hls_lab_nk_estimation.py`, lines 24–114](../../src/hls/hls_lab_nk_estimation.py); [`hls_lab_nk_policies.py`, `NKDecisionView`/`OrganizationMemoryNK`, lines 58–127](../../src/hls/hls_lab_nk_policies.py); [`hls_lab_nk_execution.py`, decision boundary and transitions, lines 438–619](../../src/hls/hls_lab_nk_execution.py). Equivalence/regression evidence: [`test_hls_lab_nk_estimation.py`](../../tests/test_hls_lab_nk_estimation.py).

## 8. Environment and demand

The environment uses existing C5 processes: fixed sequences through the environment wrapper, stationary categorical/IID demand, time-indexed nonstationary categorical distributions, and first-order Markov task state. A finite problem/emission catalog maps each environmental task label to one or more `ProblemSpecNK` objects with fixed K requirements and weights. The number of problem types is independent of K. Markov transitions depend on prior task, not organization. Nonstationary probabilities are keyed by time. There is one problem per period; no task queues, concurrent projects, unknown latent demand beliefs, or performance feedback into demand.

The N×K generator samples the process before execution using a local `Random(seed)`. Per-period emission uses SHA-256 keyed seed/period in the extended K case; exact K=2/equal-weight path delegates to the historical emitter. The trajectory records seed, config, emitted problems, latent states and regime labels. The runner returns this frozen trajectory separately; policy decision views do not include latent labels. Same frozen problem sequence gives identical IDs/requirements/weights/order across runs, but does not imply identical observations or organizational paths. Exact source: [`c5.py`, `StationaryTaskDemand`, `NonStationaryTaskDemand`, `MarkovTaskDemand`, lines 56–162](../../src/hls/synthetic/c5.py); [`hls_lab_nk_environment.py`, config, emission, trajectory, lines 31–198](../../src/hls/hls_lab_nk_environment.py); environment replay tests in [`test_hls_lab_nk_environment.py`](../../tests/test_hls_lab_nk_environment.py).

## 9. Construct-validity inventory

| Construct | Model representation / direct variables | Assumptions and limitation | Unsupported interpretation |
|---|---|---|---|
| Heterogeneity | Variation in rows/cells of `C_actual`; matrices are direct. | Chosen finite-dimensional profiles. | Heterogeneity automatically valuable. |
| Specialization | Agent-specific competence profiles relative to task requirement vectors. | A profile difference is not itself task specialization; demand/catalog/action structure must make it relevant. | Heterogeneity = specialization. |
| Complementarity | Joint contributions jointly meet multiple requirements. | Additive production; feasibility coverage only. | Functional complementarity = productive synergy. |
| Coordination | Policy maps decision view and memory to a feasible joint action. | Only three fixed algorithms; centralized full-action selection. | P0/P1/P2 represent all organizational coordination. |
| Individual competence | Bounded normalized `c_ik`. | Abstract scalar per task dimension; no multidimensional within-skill or calibration. | Psychological ability/intelligence without external validation. |
| Collective performance | Gross CES, success, deficit, margin, output vector. | Different non-equivalent outcomes; no net utility. | CES = welfare/profit. |
| Learning by doing | MIS gain on exposed agent-skill cells. | Deterministic, separable exponential transition, eta supplied. | All experience changes real competence or learned ability is calibrated. |
| Teaching | Directed efficacy plus learner remaining-gap transfer. | T independent of teacher competence; one event and no teacher loss. | Real knowledge communication or pedagogy is validated. |
| Information uncertainty | Finite scalar posterior, production and teaching observations. | Specific likelihood/prior/grid and fixed observation channels. | General organizational inference or calibrated uncertainty. |
| Adaptation | P2 relation choice uses current success, learner estimate, efficacy memory. | Threshold/exploration heuristic; current observed problem only. | Planning, optimal adaptation, latent regime learning. |
| Organizational learning | Efficacy memory and posterior state can change. | No higher-order model of organizational knowledge beyond these states. | Competence growth alone = collective/organizational learning. |
| Resource efficiency | Effort used/unused and participant load traces. | Discrete catalog, no carry-over, no empirically grounded conversion to value. | Lower use necessarily more efficient at equivalent output or economic profit. |

Individual contribution `e_ik c_ik` is an accounting decomposition, not an independently identified causal contribution to collective success: marginal effects depend on action feasibility, other contributions, threshold success, requirements, and CES weights.

## 10. Mathematical property register

| Property | Classification | Basis / qualification |
|---|---|---|
| Actual/estimated competence bounds | **PROVEN FROM EQUATIONS** for transitions; **SUPPORTED BY TESTS** for configured runner paths | Initial validators bound cells; MIS and teaching maps `[0,1]` to `[0,1]`; posterior support constrained to `[0,1]`. |
| Production additivity | **PROVEN FROM EQUATIONS** | `Y_k=Σ_i e_ik c_ik`; no interaction terms. |
| Output monotonicity in actual competence for fixed action | **PROVEN FROM EQUATIONS** | Each coefficient `e_ik≥0`. |
| Functional success/deficit monotonicity in output | **PROVEN FROM EQUATIONS** | Threshold and `max(0,r−y)` definitions. |
| CES monotonicity | **PROVEN FROM EQUATIONS** for default positive `ρ=.5`; nondecreasing generally under nonnegative weights and positive rho | Zero weights make a dimension irrelevant. Negative rho is accepted by validator but zero output with negative rho can be numerically/domain problematic; no scientific interpretation here. |
| MIS zero exposure, bounds, saturation and monotonicity | **PROVEN FROM EQUATIONS**; **SUPPORTED BY TESTS** | Derivations in §4; floating-point roundoff remains implementation-level. |
| Teaching direct target/bounds/resource charge | **PROVEN FROM EQUATIONS**; **SUPPORTED BY TESTS** | One learner cell changes; both parties charged. Teacher competence independence is a model property, not a validated premise. |
| Resource conservation | **PROVEN FROM ACTION FEASIBILITY**; **SUPPORTED BY TESTS** | Feasible enumerated actions enforce all limits; traces reconcile used and unused effort. Does not imply equal realized consumption across policies. |
| Physical permutation equivariance | **PROVEN CONDITIONAL** on consistently permuting IDs, matrices, parameters, actions | Additive equations and cellwise mechanisms commute with relabeling. |
| Policy permutation invariance | **CONTRADICTED as universal claim** | Ordered catalogs, configured relation sequences and numeric tie-breaking can choose differently after relabeling. |
| Exogenous-demand independence | **SUPPORTED BY CODE/TESTS**; logically true for frozen path | Trajectory is generated before organization runner; no organization input is passed to generator. |
| Posterior unbiasedness/calibration/identifiability | **PLAUSIBLE BUT UNVERIFIED / OPEN** | Finite grid, declared prior, action-dependent exposure and noisy observations; tests validate code, not statistical calibration. |
| Teaching improves collective performance | **NOT A THEOREM; CONTRADICTED as universal statement** | Immediate displacement, unused capacity, unmet requirements and future assignments can offset gain; Campaign 1/2 document both signs conditionally. |
| “Emergence” | **NOT APPLICABLE / UNDEFINED** | No formal emergence metric or null comparison in the simulator. |

## 11. Historical research evidence (not new findings)

| Record | Scope and reported result | Boundary / relation to current lab |
|---|---|---|
| **G1** | Static two-agent/two-task ground truth; holds competence, demand, budgets and policy class explicit. Symmetric crossed specialization gives `ΔY(p)=.8 min(p,1−p)`, maximum `.4` at `p=.5`; homogeneous/dominance nulls are included. | Static organization/use evidence only; no learning. See [G1 ground truth](../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md), numerical artifacts there linked to foundations. |
| **G2** | Two agents, two tasks, two periods. Constructively separates competence growth, frontier change, development value and decision reversal; a future value can reverse current reward ranking in the minimal case. | Deterministic reference model, not general superiority, prevalence or RQ0 answer. See [G2 ground truth](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md). |
| **MIS / Minimal Reference Scenario** | A two-worker/two-skill short-horizon scenario makes present reward loss `L` and future organizational value `G` explicit; its diminishing rule uses `s+q(1−s)^2` with cap. | A model fixture, not empirical calibration. Its law is not identical to current DISCOVER-v2 MIS-v2 (see §4). See [MIS reference](../experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md). |
| **G3-H** | Three-worker/two-competence/two-period assignment setting; exact development value reduces to standard assignment sensitivities; a finite example shows including a future organization-development opportunity reverses local ranking by `.0685656`. | Analytical finite-scenario result, not new general theory or current laboratory policy behavior. G3-H retains G3 law and varies worker-specific learning scales. See [G3/G3-H](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md). |
| **RQ0** | Integrated-versus-separated management is the open overarching question; the campaign guide states initial RQ0-B closure and causal follow-ups, while RQ0 remains OPEN. G0+C1–C5 were the historical campaign substrate. | It is not equivalent to P0/P1/P2 comparisons in the present laboratory. Campaign documents and their time-specific source/result manifests are authoritative; see [RQ0 campaign guide](../experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md). |
| **DISCOVER/MIS-v2 gate** | 945 main runs across 7 eta × 9 configurations × 5 environments × 3 seeds (2,205 including controls) reported environment/rate-dependent winners; matched G00/G06 crossover changed sign at eta `.90`. | Conditional on the fixed state, action set, CES, Bayesian demand belief and controller; not empirical learning validation. See [MIS-v2 gate](../experiments/CAPABILITY_GEOMETRY_GATE_MIS_V2.md). |
| **HLS Laboratory Campaign 1** | Published pilot/mechanism/counterfactual/plausibility synthesis records 1,280 pilot policy runs; P1 lower CES in 320/320 P1–P0 pairs; P2 mixed; conditional teaching benefits and harms; 64 counterfactual branches. | Descriptive/conditional, finite seeds, continuation-dependent, no broad significance/causal mediation claim. See [Campaign 1 synthesis](../experiments/HLS_CAMPAIGN1_FINDINGS.md) and its artifact links. |
| **HLS Laboratory Campaign 2** | Four-cell teaching×MIS controlled design, 34 paired quadruples including zero-efficacy control and P0 continuation; interactions differ by scenario (A −1.092473, B +1.561953, C +.339151). | Conditional to selected scenarios, fixed continuation and modeled transitions; no assignment-mediated causal decomposition. See [Campaign 2 findings](../experiments/HLS_CAMPAIGN2_FINDINGS.md). |

Historical results are not re-executed or treated as validation of real-world constructs.

## 12. Diagnostic reference episode

The exact configuration and full per-period trace are machine-readable at [`reference_trace.json`](../../results/diagnostics/hls_scientific_model_dossier/reference_trace.json), produced by [`scientific_model_reference.py`](../../experiments/synthetic/hls_lab_v1/scientific_model_reference.py). It records source commit `e8e115030e064df23f07f1b5824264f97513099a`, environment seed `24016`, information seed `24017`, and two agents × two competencies. It is a hand-configured diagnostic trace, not a sampled scientific campaign.

Initial actual competencies are `((.85,.15),(.20,.20))`; estimates are `((.75,.25),(.30,.30))`. Budget and individual limits are 2 and `(1,1)`. Demand follows deterministic first-order Markov `x→y→x→y` over four periods, with requirements `(1.10,.10)` for x and `(.10,1.20)` for y. P2 is configured with relations `A→B:y`, `B→A:x`, target `.95`, efficacy threshold `.35`. MIS-v2 eta is `((.20,.15),(.12,.18))`; T values for those relations are `.80` and `.70`; transfer rate `.40`; lesson effort `.25`. Imperfect mode uses a 101-point posterior, prior variance `.04`, production observation SD `.02`, outcome noise zero. Effort catalogs explicitly add feasible half-unit single-skill actions alongside the historical K=2 catalog; the complete joint catalog guard is 216.

| t | Demand / P2 lesson | Production output | Success | CES | Prod effort / teaching charge | MIS gain `B,y` | Teaching gain (target) | P2 efficacy memory after |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 0 | x / `A→B:y` | (.425,.100) | no | .234328 | 1.00 / .50 | .075569 | .057954 | `A→B:y` .914286 |
| 1 | y / `B→A:x` | (.432918,.166762) | no | .284265 | 1.00 / .50 | .062956 | .008400 | plus `B→A:x` .508281 |
| 2 | x / `A→B:y` | (.444200,.198240) | no | .308983 | 1.00 / .50 | .057009 | .043721 | `A→B:y` .920036 (count 2) |
| 3 | y / `A→B:y` | (.450091,.248605) | no | .341928 | 1.00 / .50 | .047494 | .036424 | `A→B:y` .926032 (count 3) |

The trace contains actual and estimated pre/post matrices, per-cell production observations, posterior variance, estimation error, selected action, output, CES, success, resource ledger, separate MIS/teaching increments and efficacy observations/memory. Final actual competence is `((.91072,.15),(.20,.58112815104))`; final posterior-mean estimates are `((.848296,.25),(.30,.647657))`. These values demonstrate that the code path records the declared mechanisms; they do not demonstrate teaching benefit. All four tasks fail their functional requirements by construction of this fixture.

Replay test computes the trace twice in-process, checks the fixed trajectory, positive MIS/teaching increments, additive output and resource reconciliation. The generated JSON SHA-256 is `d852887c723ae0d2573e358d15c0d708430bee7d22519a777283eb0014885784`; deterministic output was checked by rerunning the script.

## 13. Scientific limitations and open questions

- No empirical calibration of competence, effort, eta, transfer rate, efficacy, priors, noise, requirements or CES weights.
- One current problem is received per period; multiple pending/concurrent jobs and scheduling queues are unsupported.
- Productive actions are discrete and exhaustive; feasible behavior depends on caller-supplied catalogs and max-candidate guard.
- Teaching transfers through a fixed configured relation and learner gap, with no direct teacher-skill dependence, teacher depletion, recipient competition, or repeated simultaneous network.
- MIS-v2 and teaching are deterministic latent transitions; only observations are noisy. The posterior may be misspecified relative to those transitions.
- P0/P1/P2 are heuristic policy packages with different teaching behavior and memory; no family-wide architecture or coordination superiority follows.
- Functional success, gross CES, output, competence, effort and unused capacity remain distinct outcomes. No net utility is authorized.
- A deterministic reference trace and passing invariant tests establish implementation behavior only.
- The final current-worktree full suite reported 1,397 passed and 5 failed in 634.58s. The failures match the previously documented provenance/integrity set: `tests/foundations/test_result_manifests.py::test_every_foundation_result_has_consistent_manifest` (an additional pre-existing result directory makes the inventory 12 instead of the frozen 11); `tests/test_campaign2_state_coverage_audit.py::test_frozen_inputs_and_completed_artifacts` (closure document digest mismatch); `tests/test_campaign2_theory.py::test_preexperiment_manifest_and_contamination_boundary` (frozen `finite_problem_belief.py` digest); `tests/test_campaign3_meta_voc_confirmatory.py::test_pre_execution_manifest_and_raw_integrity_when_present` (same frozen source digest); and `tests/test_strategy_discrimination_gate.py::test_source_hashes_and_raw_output_hashes` (same source digest). No manifest, expected hash, closure file, or historical artifact was changed in this audit. The suite was run on a worktree containing unrelated pre-existing changes; those were preserved.

## 14. Questions for independent expert review

Please evaluate:

1. Is additive output plus CES a coherent operationalization for the intended problem domain?
2. Is “functional complementarity” appropriately distinguished from productive synergy?
3. Is current MIS-v2 a defensible learning-by-doing law, and how should its relation to the earlier quadratic-gap MIS/G3 law be described?
4. What does the teaching-efficacy tensor represent scientifically?
5. Is teacher-competence independence appropriate, or should efficacy be constrained/calibrated by expertise in a future authorized model?
6. How much do P0/P1/P2 comparisons confound coordination rules with teaching exposure, information and memory?
7. Are the production observation likelihood, noise scale, prior and grid adequate for the intended inference questions?
8. Under what conditions is competence identifiable from action-dependent contribution observations?
9. Do the current metrics have construct validity, particularly gross CES and effort use?
10. What is the smallest falsification test for production, learning, teaching and information assumptions?
11. What domain of applicability is defensible before external calibration?
12. What evidence would be required to move from implementation readiness to scientific research readiness?

Questions 1–12 require domain/scientific judgment and, for calibration or external validity, evidence beyond code inspection. The equation lineage discrepancy in question 3 is verifiable from source, but its intended conceptual resolution requires PI/CE and expert decision.

## 15. Source and evidence index

All source references in §§3–8 identify repository-relative path, function/class and line range, and are pinned to audit commit `e8e115030e064df23f07f1b5824264f97513099a`. Principal sources are:

- `src/hls/discover_v0.py` — original fixed 3×2 additive output, action catalog and CES.
- `src/hls/discover_develop_v0.py` and `discover_develop_v2.py` — historical prior MIS law and current MIS-v2 law.
- `src/hls/hls_lab_v1.py` / `hls_lab_v1_integrated.py` — functional evaluation, legacy policies, teaching, information and transition order.
- `src/hls/hls_lab_dynamic.py` — scalar Bayesian observation/posterior and indexed innovations.
- `src/hls/hls_lab_nk_geometry.py`, `_production.py`, `_learning.py`, `_teaching.py`, `_policies.py`, `_estimation.py`, `_environment.py`, `_execution.py` — current dimension-general adapters and runner.
- Tests cited at corresponding sections; tests support implementation claims but do not establish empirical validity.
- Historical ground truths and result syntheses linked in §11; they retain their own original source commits and historical scopes.
