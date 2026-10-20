# HLS–Chen (2018): simulator compatibility and reproduction audit

**Date:** 2026-10-19

**Scope:** read-only engineering and reproducibility assessment; no implementation or experiment was performed.

## Executive assessment

**Recommendation: GO WITH CONDITIONS.** The broad HLS research codebase contains reusable representations of agents, experience-dependent productivity, stochastic demand, policies, and reproducible traces. The existing *N×K Laboratory runner*, however, cannot represent Chen, Hewitt and Thomas’s (CHT) scheduling problem by configuration alone. It assigns divisible effort over a skill vector under effort budgets; CHT assigns each discrete request exactly once and constrains each technician’s sum of task-specific service times by daily availability. It also minimizes service-time cost, rather than HLS functional success/CES.

The minimum faithful route is an isolated CHT-specific scheduling environment and action/resource contract, with new CHT-specific policies. This can be implemented alongside the canonical HLS simulator; changing MIS-v2, Nembhard Direct, or the existing N×K runner is neither necessary nor justified. The scalar CHT productivity law is algebraically representable by the existing Nembhard curve under a restricted parameter mapping, but that identity does not preserve job assignment, service-time capacity, objective, or policy semantics.

The full mathematical model is sufficiently specified for a bounded implementation **except for material experimental-reconstruction details**: Table 1’s `log I` and `F` coordinates are not unambiguously mapped to initial experience and the stated model parameters; the article does not provide the original random seeds, exact workforce draws, code/data, or a complete draw-domain repair convention. Thus a transparent approximate reproduction of the reported study is feasible after resolving or explicitly bounding those source ambiguities. Exact reproduction of the published numerical figures is not presently supportable from the article alone.

No simulation was run, and this report makes no claim that HLS has reproduced CHT.

## 1. Evidence and inspected source

The primary source is the complete 13-page article, Xi Chen, Mike Hewitt and Barrett W. Thomas, “An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers,” *International Journal of Production Economics* 196 (2018), 122–134, DOI [10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028), stored at [`docs/literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf`](../literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf). Its SHA-256 is `58320e719bf4d54d76ecb6ae01ba94dc3f18e87af552dfc292138177846412f7`.

The source equations, algorithm reconstruction, experimental settings, figure interpretation, and unresolved source ambiguities are transcribed with printed page and equation references in [`HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md`](../research/HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). This compatibility audit uses that full-text review and checks the actual repository implementation; it does not treat an equation-level resemblance as simulator compatibility.

### Actual HLS components and contracts inspected

| Concern | Implemented interface | What the code actually provides | Relevant tests |
|---|---|---|---|
| Organization, state, tasks, effort constraints | `src/hls/hls_lab_nk_geometry.py`: `OrganizationConfigNK`, `OrganizationStateNK`, `OrganizationResourcesNK`, `ProblemSpecNK`, `validate_productive_allocation_nk`, `enumerate_productive_allocations_nk` | Fixed N×K competence/skill geometry; tasks are K-vectors of requirements with a shared resource budget; actions are nonnegative effort matrices; feasibility checks per-agent effort and collective/problem effort budgets. Not per-request binary assignment or duration capacity. | `tests/test_hls_lab_v1_nk_geometry.py`, `tests/test_hls_lab_nk_execution.py` |
| Output, functional score and objective-like diagnostics | `src/hls/hls_lab_nk_production.py`: `productive_outputs_nk`, `evaluate_problem_nk`, `ces_reward_nk`, `functional_effort_rank_nk` | Additive skill output, requirement deficits/success/margin and CES. These do not implement total service-time minimization. | `tests/test_hls_lab_nk_execution.py`, `tests/test_hls_lab_nk_policies.py` |
| MIS-v2 capability evolution | `src/hls/hls_lab_nk_learning.py`: `LearningProfileNK`, `mis_v2_transition_nk`; underlying `src/hls/discover_develop_v2.py` | Bounded normalized competence state updated after production by the MIS-v2 exposure law. This is not CHT integer task-count experience or CHT service time. | `tests/test_hls_lab_nk_learning.py`, `tests/test_hls_lab_nk_learning_transition.py` |
| CHT-adjacent productivity / cumulative experience | `src/hls/mechanisms/nembhard_direct.py`: `DirectExperienceParameters`, `direct_productivity`, `advance_direct_experience`; N×K wrapper in `src/hls/hls_lab_nk_nembhard.py`: `NembhardDirectProfileNK`, `NembhardDirectStateNK`, `nembhard_productive_outputs_nk`, `advance_nembhard_experience_nk` | Independent real-valued D[N,K], cell-specific k,p,r, production evaluated at pre-period experience, then exposure update `D += e·Δt`. It is an explicit HLS operational adaptation, not CHT’s job-level service-time system. | `tests/test_nembhard_direct.py`, `tests/test_hls_lab_nk_nembhard.py` |
| N×K sequence execution and policy dispatch | `src/hls/hls_lab_nk_execution.py`: `run_nk_production_sequence`; internal `_run_nk_nembhard_direct_sequence`, `_run_nk_learning_sequence`, `_run_nk_policy_sequence`; result records `NKProductionEpisodeRecord`, `NKNembhardDirectEpisodeRecord` | Executes explicit sequences or pre-generated environments, validates effort allocations, records output/state transitions and serializes results. Policies are invoked at the N×K effort-action level. It has no CHT request set, integer assignment vector or daily service-time knapsack. | `tests/test_hls_lab_nk_execution.py`, `tests/test_hls_lab_nk_nembhard.py`, `tests/test_hls_lab_nk_policies.py` |
| C5 task-demand processes | `src/hls/synthetic/c5.py`: `StationaryTaskDemand`, `NonStationaryTaskDemand`, `MarkovTaskDemand`; N×K bridge `src/hls/hls_lab_nk_environment.py`: `DemandRegimeNK`, `ExogenousEnvironmentConfigNK`, `generate_environment_trajectory_nk` | Emits a finite sequence of `ProblemSpecNK` task types from stationary, time-varying, or Markov laws. N×K runner freezes the exogenous path before decisions. No daily batch of 50 independently sampled requests is represented by one emitted problem without an added batch environment. | `tests/synthetic/test_c5_dynamic_demand.py`, `tests/test_hls_lab_nk_environment.py` |
| Decision policies | `src/hls/hls_lab_nk_policies.py`: `NKCoordinationPolicy.choose(view, memory, parameters)`, `P0ProductionOnlyPolicyNK`, `P1FixedTeachingNK`, `P2AdaptiveTeachingNK`; Nembhard routers in `hls_lab_nk_nembhard_router.py` and `hls_lab_nk_nembhard_adaptive.py` | P0/P1/P2 choose feasible N×K effort/teaching actions. Nembhard ORACLE ranks current assignments using true current Nembhard productivity; ADAPTIVE uses observed work-output estimates, plus configurable exploration. None is ADPOL or ADPBF. | `tests/test_hls_lab_nk_policies.py`, `tests/test_hls_lab_nk_nembhard_oracle.py`, `tests/test_hls_lab_nk_nembhard_adaptive.py` |
| Estimation and information | `src/hls/hls_lab_nk_estimation.py`: `initialize_competence_posterior_nk`, `assimilate_production_observations_nk`, `predict_mis_v2_nk`; legacy scalar posterior in `src/hls/hls_lab_dynamic.py`: `SkillPosterior`, `initialize_competence_estimator`, `update_skill_posterior` | Bayesian/grid estimation of normalized competence from HLS production observations. CHT’s scheduling model knows experience and learning/productivity parameters; it does not estimate unknown parameters from feedback. These estimators are not ADP value-function fitting. | `tests/test_hls_lab_nk_estimation.py`, `tests/test_hls_lab_dynamic.py` |
| Experiment contract and provenance | `src/hls/experiment_contract.py`: `ExperimentRun`, `ExperimentEvent`, `MetricValue`, `RunAdapterContext`, `adapt_hls_nk_run`, `adapt_nembhard_run` | Adapts existing run results to common JSON events, units, metrics, seeds and metadata. It does not supply a simulator, optimization model, or unrecorded CHT provenance. | `tests/test_hls_common_experiment_contract.py` |
| Exact finite-horizon optimization | `src/hls/synthetic/exact.py`: `ExactProblem`, `solve_hls`, `solve_strong_sep`, `solve_sep_omega` | Exact recursion for the separate synthetic HLS `SyntheticEnvironment`; its documented task contract is `task_at(time, state, history)`. It explicitly defers stochastic C5 integration. Not a CHT technician assignment/ADP solver. | `tests/synthetic/test_exact_solver.py` |

The research code includes dynamic demand and exact small-world solvers, but neither interface is a plug-in for arbitrary scheduling physics. There is no current CHT implementation or ADPOL/ADPBF code among the inspected modules/tests.

## 2. Chen simulation requirements

The following is the published problem, not a proposed HLS reinterpretation. Printed page numbers refer to the journal pagination.

### 2.1 Agents, work, and learning

There are technicians (k\in K), task types (r\in R), and daily request sets (N_t); request (i) has type (r(i)). Technician (k)'s integer experience with type (r), (q^k_{rt}), is task-specific and cumulative. With technician/task parameters (D^k_r>0), (L^k_r), and positive experience (q^k_{rt}>0), the service time in Eq. (1), p. 124, is

\[
d^k_{rt}=\left(D^k_r\frac{q^k_{rt}}{q^k_{rt}+L^k_r}\right)^{-1}
=\frac{q^k_{rt}+L^k_r}{D^k_rq^k_{rt}}.
\]

Thus (1/d^k_{rt}) increases with same-type experience toward (D^k_r). The update is assignment-induced, deterministic, and given by Eq. (5), p. 125:

\[
q^k_{r,t+1}=q^k_{rt}+\sum_{i\in N_t:r(i)=r}x^k_{it}.
\]

There is no separate training action, forgetting, or cross-task transfer in this formulation. Initial experience must be positive for Eq. (1) as printed; the article does not specify a q=0 service-time convention. Table 1’s `log I`/`F` mapping to the model variables needs resolution before claiming exact sampling of the original workforce distribution.

### 2.2 Feasibility, cost and horizon

Each request is assigned exactly once, and each technician’s total assigned service time must fit daily availability (Y): Eqs. (2)–(4), p. 124.

\[
\sum_k x^k_{it}=1\ (i\in N_t),\qquad
\sum_{i\in N_t}x^k_{it}d^k_{r(i)t}\leq Y\ (k\in K),\qquad x^k_{it}\in\{0,1\}.
\]

Daily cost (C_t) is total assigned service time (Eq. (6), p. 125). Their objective is to minimize expected undiscounted accumulated daily service-time cost over finite horizon (T), with current day’s demand known and future requests stochastic. The Bellman equation (7), p. 125, minimizes current service cost plus expected optimal future cost over the next demand and experience transition. This is not HLS’s functional pass/deficit/CES objective.

### 2.3 Policies and published study

* **ADPOL:** rolling daily assignment optimizer with current service time plus forecast next-day service time; forecast uses exponential smoothing α=0.9 (Eqs. (11)–(15), pp. 126–127). It is a state-responsive one-day lookahead, not a fixed assignment and not simply immediate greedy. Its detailed reformulation relies on a cited earlier paper, which must be sourced for faithful reproduction.
* **ADPBF:** approximate dynamic programming with a time-dependent post-decision linear continuation value. Eqs. (8)–(10), pp. 125–126, use an intercept plus technician-level aggregate experience features; Appendix B, pp. 132–134, describes offline approximate value iteration and recursive least squares. It learns continuation coefficients offline, not unknown productivity parameters online.

Section 5, pp. 126–127, reports 30 heterogeneous five-technician workforces; availability (Y\in\{5,6,7,8\}); task diversity |R| in {5,7,10,13,20}; 600 workforce/availability/diversity configurations; 120 days; 50 task requests/day, task types independently drawn uniformly; 1,000 ADPBF training iterations and 1,000 testing trajectories, with ADPOL evaluated on the same test demand paths. Table 1 p. 126 gives a multivariate-normal parameter summary, but the variable labels and initialization mapping are ambiguous as noted above. The article reports Gurobi 5.6, Python 2.7 and an Intel Xeon/CentOS 6.3 setup; it supplies no source code, seed list or generated instance archive.

Figure 1 p. 127 reports average day-wise ADPBF–ADPOL service-cost gaps; for diversity 5, ADPOL is about 5% better during the first ten days, while ADPBF is about 2.5% better during the last sixty days. Figures 2a–b p. 128 plot continuation coefficients; Figure 4 p. 129 compares specialization by coefficient of variation; Figure 5 p. 130 compares workload share. The paper does not provide confidence intervals or inferential tests for the plotted comparisons. Figure 3 also examines diversity and availability effects (p. 128). These are computational findings on the authors’ generated test suite, not a general theorem.

## 3. Compatibility matrix

Complexity is relative implementation effort: **S** small, **M** moderate, **L** substantial, **XL** substantial algorithmic work plus experimental reconstruction. It is not a runtime estimate.

| Chen requirement | Mathematical reference | Existing HLS implementation | Status | Required change | Complexity |
|---|---|---|---|---|---|
| Five distinct technicians and technician/task parameters | (k\in K;D^k_r,L^k_r), Eq. (1), p. 124 | `OrganizationConfigNK` holds N IDs and bounded competence matrix; `NembhardDirectProfileNK` holds N×K k,p,r matrices | SUPPORTED WITH CONFIGURATION for identifiers/parameters only | Separate CHT workforce type to avoid pretending normalized competence is CHT capability | S–M |
| Positive integer task-specific experience (q^k_{rt}) | Definition before Eq. (1), p. 124 | `NembhardDirectStateNK.experience` is nonnegative real N×K | REQUIRES EXTENSION | CHT state must store integer per-tech/per-task counts and validate the source domain | M |
| Service time (d=(q+L)/(Dq)) | Eq. (1), p. 124 | `direct_productivity` plus `nembhard_productive_outputs_nk` use productivity times divisible effort and duration | REQUIRES EXTENSION | New CHT service-time function in a distinct namespace; p=0 Nembhard curve identity may be reused only as a tested formula helper | S–M |
| Every discrete request assigned exactly once | Eq. (2), p. 124 | `ProductiveAllocationNK` assigns divisible effort by skill; `validate_productive_allocation_nk` checks effort budgets | REQUIRES NEW COMPONENT | Request-level binary assignment/action representation | M |
| Daily technician availability in service-time units | Eq. (3), p. 124 | `effort_limits`, collective/problem effort budgets | INCOMPATIBLE by direct configuration | CHT-specific capacity feasibility `sum assigned d <= Y`; do not repurpose effort limits | M |
| Assignment-dependent deterministic experience transition | Eq. (5), p. 125 | `advance_nembhard_experience_nk` adds real (e\Delta t); MIS-v2 changes normalized competence | REQUIRES EXTENSION | Integer transition derived from assigned counts; reusable pattern only, not state type | S–M |
| Daily and cumulative service-time objective | Eqs. (6)–(7), p. 125 | HLS functional evaluation and CES; common contract can represent declared metrics | REQUIRES NEW COMPONENT | CHT cost/reward and finite-horizon evaluation; keep separate from CES | M |
| Stochastic daily batch of 50 requests, task types uniform | §5, pp. 126–127 | C5 samples one task/problem per time from stationary/nonstationary/Markov process; `ExogenousEnvironmentConfigNK` emits one `ProblemSpecNK` per period | REQUIRES EXTENSION | CHT batch-demand environment returning request set (N_t), preserving same demand path across policies | M |
| Current demand known; future demand uncertain | State definition p. 124; Bellman Eq. (7) | N×K environment trajectory is generated/frozen in advance and not passed as a policy information set | REQUIRES EXTENSION for CHT policy interface | Provide current-day request batch and history/state allowed by each CHT policy, while hiding future realized path | M |
| Immediate feasible day assignment | Eqs. (2)–(6) | `NKCoordinationPolicy` and routers operate over N×K effort-action catalogs | REQUIRES NEW COMPONENT | CHT policy protocol over request assignments and service-time capacities | M |
| ADPOL one-day lookahead | Eqs. (11)–(15), pp. 126–127 | No matching policy found; P0/P1/P2 and Nembhard routers have different action/reward contracts | REQUIRES NEW COMPONENT | Implement forecast state, smoothing and source-consistent daily optimization; obtain referenced reformulation details | L |
| ADPBF basis-function value approximation | Eqs. (8)–(10), Appendix B Eqs. (16)–(20) | No post-decision ADP / recursive least-squares policy in the scheduling runner; generic exact synthetic solver is a different world | REQUIRES NEW COMPONENT | Implement training, coefficient initialization, backward updates/RLS and action optimization | XL |
| 30 workforces, 600 cells, 1,000 train/test paths | §5, pp. 126–127 | `nembhard_campaign.py` has reproducible design registry and paired run orchestration for a different E1 study | SUPPORTED WITH CONFIGURATION only as orchestration pattern | New CHT design/configuration; source ambiguity and absent original seeds/data prevent exact original draws | M–L |
| Figs. 1, 2, 4, 5 and service-cost summaries | §§5–6, Figs. 1–5, pp. 127–130 | `experiment_contract.py` and JSON result adapters; HLS traces are not CHT policy internals or per-request schedules | REQUIRES EXTENSION | CHT-specific trace schema/metrics and plotting/analysis functions; record fitted coefficients and assignment history | M |
| Mixed-integer optimization backend | §5 reports Gurobi 5.6 | No solver dependency in `pyproject.toml`; deps include NumPy, pandas, matplotlib, SymPy, scikit-learn, PyTorch and other packages | REQUIRES NEW COMPONENT / dependency decision | Add and test MILP backend adapter; exact ADPOL formulation may require external cited derivation | M–L |

### Extension boundary

The suitable seam is a separate CHT package/module containing its own request-batch, workforce/experience state, feasibility/action model, service-time objective, policy interface, and result records. It may reuse the general experiment contract (`ExperimentRun` and `ExperimentEvent`) as a non-invasive serialization adapter, deterministic seed conventions as patterns, and generic numerical utilities. It should not reuse `ProblemSpecNK` as a direct task object or map (Y) to HLS effort budgets. Nothing inspected requires altering the canonical N×K simulator core.

## 4. Feasibility by reproduction level

| Level | Assessment | Reason |
|---|---|---|
| **A — mathematical model** | **Implementable with an isolated new environment; not supported by configuration alone.** | The state and service law are straightforward to implement; assignment, service-time capacity, daily batch demand and cost need CHT-specific contracts. Exact original workforce sampling remains blocked by Table 1 mapping/domain details. |
| **B — algorithms** | **Not implemented; both require new policies.** | ADPOL needs daily rolling optimization with its published forecast objective and cited reformulation. ADPBF requires offline approximate value iteration, time-dependent linear basis weights, RLS and training/testing separation. Existing P0/P1/P2/ORACLE/ADAPTIVE are not substitutes. |
| **C — published numerical results** | **Approximate/qualitative reproduction is plausible after the ambiguities are resolved or explicitly bounded. Exact reproduction is not currently reproducible.** | No original code, seeds, workforce draws or request trajectories are supplied by the inspected article; Table 1’s labels leave parameter/init mapping uncertain. Fig. 2 additionally requires internal coefficients and training initialization; Figs. 4–5 require assignment-level traces and exact aggregation definitions. |

### Figure-level minimum evidence

* **Figure 1 (daily performance gap):** implement both ADPOL and ADPBF; train ADPBF on disjoint generated paths; evaluate both on identical test paths per workforce/availability/diversity cell; report daily mean ( (Obj^{ol}_t-Obj^{bf}_t)/Obj^{bf}_t ) with dispersion and reproducibility metadata. A representative subset can be a diagnostic, but not the whole Figure 1 replication.
* **Figure 2 (continuation coefficients):** ADPBF only, with the paper’s coefficient-initialization method, RLS updates, basis features, training iterations and coefficient averaging. A substitute value function or an online estimate is not Figure 2 reproduction.
* **Figure 4 (specialization):** retain each technician’s task assignments and compute the source-defined across-task coefficient-of-variation summary with the same averaging/order convention. A final capability matrix alone is insufficient.
* **Figure 5 (workload):** retain daily per-technician assigned service workload and derive the paper’s per-tech workload shares and ranking/aggregation. Total HLS effort cannot substitute for service-time workload.

The figures depend on different implementation layers: Figures 1/4/5 require the environment, both policies, common test paths and assignment traces; Figure 2 additionally requires faithful ADPBF training internals.

## 5. Computational feasibility

### Optimization backend

`pyproject.toml` declares no Gurobi, PuLP, OR-Tools, HiGHS, SciPy MILP, or other optimization-solver dependency. The installed scientific stack is not evidence that an appropriate solver is available. The reported implementation uses Gurobi 5.6 with Python 2.7. A future implementation therefore needs an explicit solver choice and formulation validation.

Open-source MILP solvers may be candidates for daily assignment optimization, but sufficiency cannot be certified from source inspection alone. In particular, the article refers to earlier work for ADPOL’s exact nonlinear reformulation, and solver equivalence/tolerances would need validation against the stated model. ADPBF’s daily action problem also needs its exact linearized formulation and solver behavior checked.

### Complexity and Apple Silicon

For a single day with (m=|N_t|) requests and five technicians, the raw assignment space has (5^m) choices; the published (m=50) makes enumeration inappropriate. The daily integer model has up to (5m=250) binary assignment variables before presolve, with coverage and technician capacity constraints. This is a conventional MILP scale, but feasibility/time cannot be promised without the exact formulation and target solver.

An exact finite-horizon Bellman solution is not a reasonable route to the 120-day, 30-workforce study: the experience vector has (5|R|) integer coordinates and stochastic daily request batches, so its state space grows combinatorially with horizon and number of task types. The paper’s ADP is specifically intended to avoid exact full-state dynamic programming. ADPBF training and 1,000 test trajectories across 600 configurations may be computationally substantial, but no runtime estimate is offered because no benchmark was run and solver timing depends on formulation, solver, hardware, and stopping tolerances.

The PI’s Apple Silicon Mac is a plausible target for a bounded subset once a compatible solver is selected and measured. Native support, wheel availability, parallelism, memory use, and run time remain an engineering preflight, not established facts in this audit. A small exact/reference model for Stage 1–3 is feasible as an engineering validation target; it is not a substitute for the reported study.

## 6. Staged minimum viable reproduction

These are dependencies and acceptance gates, not authorization to begin implementation or run a campaign.

| Stage | Required components | Acceptance criteria and validation | Dependencies / scientific risks |
|---|---|---|---|
| **1. CHT environment** | Isolated technician/task parameters; integer experience state; Eq. (1) service-time function; request batch; assignment feasibility; Eq. (5) transition; Eq. (6) cost; seeded demand generator. | Hand-calculated service-time fixtures; every request assigned once; daily capacity respected; assignment increments exactly the matching task experience; reproducible demand replay; no HLS competence/CES leakage. | Resolve Table 1 `I`/`F`/initial q mapping and draw-domain convention before claiming original sampling. Do not invent (q=0) semantics. |
| **2. Immediate-cost assignment baseline** | CHT-day assignment model minimizing current total service time under current requests/capacities. | Compare MILP output with exhaustive enumeration on tiny request sets; verify objective and feasibility; deterministic tie rules. | This is a diagnostic/control baseline only; do not label it ADPOL or the paper’s principal comparator. |
| **3. ADPOL** | Its request forecast state, α=.9 smoothing, next-day service-time objective, and source-compatible daily optimization/reformulation. | Hand-check forecast updates and two-day objective; tiny-instance comparison with a direct formulation; same-day inputs only; no future realized-demand leakage. | Full formulation is deferred to cited Chen et al. (2017)/associated reformulation, not wholly restated in CHT18. Obtain and audit that source before exact ADPOL claim. |
| **4. ADPBF** | Post-decision feature vector, time-dependent coefficients, training initializer, approximate value iteration, recursive least-squares updates, action optimizer. | Unit tests for features, backward target, RLS, coefficient timing and no train/test leakage; deterministic miniature training replay; check policy costs against exact DP on tiny horizons. | Appendix B algorithm details must be translated carefully; basis is approximate and aggregates task experience by technician. Training convergence is not guaranteed by a passing unit test. |
| **5. Selected published figures** | CHT traces plus separate analysis scripts for Fig. 1/2/4/5. | Recompute metrics from saved policy-level records; common held-out test paths for ADPOL/ADPBF; show uncertainty where generated replications allow; reproduce axes/aggregation before comparing plotted values. | Original seeds/data unavailable; Figures 2/4/5 rely on details that must be transcribed exactly. Results likely approximate, not exact reproduction. |
| **6. Scale-up to full design** | Full 30×4×5=600 configuration design, 120 days, 50 requests/day, 1000 training iterations and 1000 paired testing paths; robust result persistence and restart. | Validate configuration counts and pair identities; pilot solver/runtime/memory; recover all generated config/seed provenance; pre-register acceptance tolerances justified by original reported precision and sampling uncertainty. | Do not scale until parameter ambiguity, ADPOL source, solver, runtime and result-integrity gates pass. No runtime is estimated here. |

## 7. Decision and first milestone

### Answers to the PI’s questions

1. **Can existing HLS represent Chen’s mathematical environment?** Not in the current N×K simulator by configuration. The broader code has useful primitives, but the request-level action, integer skill-specific experience, per-technician service-time capacity, batch demand and service-time objective are absent.
2. **Minimum necessary extension?** A separate CHT job-shop environment and result/action contracts, plus CHT’s service-time and experience transition. Preserve the N×K simulator and model identifiers unchanged.
3. **Can the algorithms be implemented without changing simulator core?** Yes, architecturally, as policies/solvers over the isolated CHT state/action interface. Neither ADPOL nor ADPBF currently exists. ADPOL also depends on an earlier cited reformulation source; ADPBF is a substantial new offline ADP implementation.
4. **Realistic reproduction level?** Mathematical model: exact equation-level implementation for a resolved parameter subset, with an isolated environment. Algorithms: potentially faithful after source completion and validation. Published numerical figures: approximate/qualitative only unless original data, draws, randomization and solver details become available. Exact numerical replication is not currently justified.
5. **First implementation milestone?** Stage 1 only: formalize and test a CHT-specific deterministic state transition, service-time and feasibility environment on hand-checkable tiny examples, after resolving (q_0) and Table 1 parameter mapping. No policy-performance claim belongs in this milestone.
6. **Should the project proceed?** **GO WITH CONDITIONS** for an isolated model implementation, subject to source ambiguities being resolved before claiming a faithful instance-generation reproduction. Do not start ADPOL/ADPBF or the 600-cell experiment until Stage 1 passes and the additional cited ADPOL source and solver choice are reviewed.

### Conditions before claiming reproduction

* Resolve from primary sources or authors’ materials the Table 1 coordinates and their mapping to (D,L,Q_0), and any (F) parameter; verify parameter transforms and admissible draw handling.
* Obtain and inspect the referenced Chen et al. (2017) ADPOL formulation/reformulation; do not reconstruct missing steps by guesswork.
* Choose a MILP backend and validate it against exhaustive small instances and the published constraints/objectives.
* Keep CHT’s task, time, cost and policy semantics isolated from HLS competence, CES, effort budgets, and Nembhard Direct exposure conventions.
* Label any study using newly sampled seeds/workforces as an approximate computational reproduction, and report its deviations from CHT’s original computational study.

## 8. Reproducibility boundary

**Supported by code inspection:** HLS currently has N×K agents/skills, normalized competence and MIS-v2, optional Nembhard direct productivity and experience, explicit or automatic Nembhard assignment, C5 exogenous problem-demand processes, deterministic execution traces, and a generic experiment-record adapter. Tests cover those contracts, including N×K execution, environment replay, and mechanism-specific transitions.

**Not supported by existing HLS tests or code:** the CHT equations as a job-level service-time scheduler; CHT’s exact feasibility polytope; ADPOL; ADPBF; the 600-configuration CHT experiment; or Figures 1–5. No Chen test file was present in the inspected test tree. Existing unit tests demonstrate code behavior for existing HLS contracts, not scientific reproduction of CHT.

**Do not infer:** that Nembhard Direct integration already reproduces CHT because its curve can be reparameterized; that HLS’s `nembhard_oracle` is equivalent to ADPOL; that `nembhard_adaptive` is equivalent to ADPBF; or that a common JSON result schema makes the models scientifically comparable.

## References

1. Chen, X., Hewitt, M., & Thomas, B. W. (2018). “An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers.” *International Journal of Production Economics*, 196, 122–134. DOI: [10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028). Local primary source linked above. Model: Eqs. (1)–(7), printed pp. 124–125; ADPBF: Eqs. (8)–(10), pp. 125–126 and Appendix B Eqs. (16)–(20), pp. 132–134; ADPOL: Eqs. (11)–(15), pp. 126–127; experiments and results: §5–6, pp. 126–130, Figs. 1–5; Table 1, p. 126.
2. Chen, X., Thomas, B. W., & Hewitt, M. (2017). “Multi-period technician scheduling with experience-based service times and stochastic customers.” *Computers & Operations Research*, 82, 1–14. DOI: [10.1016/j.cor.2016.12.026](https://doi.org/10.1016/j.cor.2016.12.026). CHT18 cites this as the ADPOL/source formulation; its complete mathematical details were not audited for this report and are a prerequisite for exact ADPOL reproduction.
3. HLS prior full-text mathematical review: [`HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md`](../research/HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md).
