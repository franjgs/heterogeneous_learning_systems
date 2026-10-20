# HLS-E1 — Experimental Validation Design

**Date:** 2026-10-19
**Status:** design only; no implementation or experiment authorized.
**Decision:** **REVISE** before implementation.

> **Identifier warning.** The repository already uses **HLS-E1** for the
> Nembhard Direct 1,016-episode campaign documented under
> `docs/experiments/HLS_NEMBHARD_*`. This proposed study is scientifically
> distinct. Before code or
> preregistration, PI/CE must give it a non-colliding canonical identifier
> (provisional short name below: `E1-ANTICIPATION`). Do not overwrite or
> reinterpret the Nembhard E1 protocol or results.

## A. Formal problem and model choice

### A.1 Smallest useful existing execution surface

Use the **G0/RQ0 synthetic environment**, not the Nembhard campaign and not
the N×K execution runner as a proxy for a future-value policy. G0 already has
heterogeneous competence states, operational actions, stochastic
action-conditioned development opportunities, explicit development actions,
resource models, reward models, and exact finite-horizon solvers. C5 already
defines stationary, time-indexed nonstationary, and Markov task processes.
This keeps the study inside the canonical RQ0 policy classes.

This is not the same physical model as N×K MIS-v2. The G0/C1 A1 development
kernel uses its declared saturating transition; it must not be called
MIS-v2. If the PI instead requires specifically the N×K MIS-v2 equation, the
existing N×K route has C5 demand, effort feasibility, and competence
transitions, but has **no anticipatory policy or exact finite-horizon solver**
for that same route. That is a larger/different design choice, not a silent
substitution.

### A.2 State, action, reward, dynamics and information

For a bounded C1/G0 instance, write the decision-time state as

\[
s_t=(X_t,t,z_t,b_t),
\]

where `X_t` is the real competence matrix, `t` is the period, `z_t` is the
current demand-process state (e.g. the previous task type for C5 Markov
demand), and `b_t` is the remaining C3 development budget. The currently
realized task `q_t` is observed before choice. `z_t` and `b_t` are included
only when required by the chosen task kernel and resource model.

The within-period decision is sequential, not a simultaneous action pair.
First the policy chooses the operational assignment
`u_t ∈ A_O(s_t,q_t)`. After the opportunity outcome `o_t` is observed, it
chooses development action `d_t ∈ A_D(s_t,o_t,b_t)`. Thus the policy specifies
both decision rules, but `d_t` cannot depend on an unobserved opportunity.
In the smallest C1 instance, `u_t` chooses a learner for the current task;
`d_t` is null or develops an admissible learner-skill cell. The C3 budget is
consumed only by a non-null development action.

Use the existing reward/cost separation:

\[
r(s_t,q_t,u_t)=R(X_t,q_t,u_t),\qquad
J_\pi=\mathbb E_\pi\!\left[\sum_{t=0}^{T-1}
  \bigl(r(s_t,q_t,u_t)-c(d_t)\bigr)+V_T(X_T,q_T)\right].
\]

Set `beta=1`, matching the undiscounted G0 reference case. `c(d)` is the
existing objective penalty; resource consumption is separately constrained
by `b_t`. Do not conflate budget units and objective units. The terminal
reward and terminal-task convention must be fixed once in the configuration
and shared by every comparator.

The physical transition is the composition already represented by G0. For
this bounded instance, use the existing A1 saturating development kernel with
one declared target competence (skill 1); the opportunity probability may
depend on current task and selected learner, and an admissible development
decision selects its recipient. This is explicit opportunity-gated
development, not direct learning-by-doing from the same task exposure.

\[
u_t\in A_O(s_t,q_t),\quad
o_t\sim P_O(\cdot\mid X_t,q_t,u_t),\quad
d_t\in A_D(X_t,o_t,b_t),\quad
X_{t+1}=F_D(X_t,o_t,d_t),\quad
b_{t+1}=b_t-\operatorname{consume}(d_t).
\]

Demand evolves exogenously under a declared kernel
`q_{t+1}~P_Q(.|z_t,t)`; it is independent of policy actions. The current
task and current competence are available to all four online comparators in
this bounded full-state validation. All may know the same transition/reward
model and demand **law**. None receives the future realized demand path.
The evaluator alone may access the complete generated path and true state
for paired outcome accounting.

`A(s_t)` is the common set of operational actions satisfying the same
per-period capacity and feasibility rule; development feasibility is
validated by the existing `DevelopmentKernel` and `ResourceModel`. For a
small G0/C1 configuration the operation choice assigns one current task to
one learner, so each learner has at most one operational assignment that
period. The exact solver additionally enumerates only admissible development
choices after each opportunity outcome.

### A.3 Existing implementation mapping

| Mathematical element | Existing implementation | Boundary |
|---|---|---|
| Competence state `X` and time | `src/hls/synthetic/state.py:WorldState` | Arbitrary learner × competence shape, finite numeric competence; time and persistent resources. |
| Environment composition | `src/hls/synthetic/environment.py:SyntheticEnvironment` | Composes task, competence, opportunity, development, reward, resource, information, and randomness components. |
| Task demand | `src/hls/synthetic/c5.py:StationaryTaskDemand`, `NonStationaryTaskDemand`, `MarkovTaskDemand` | Sampling exists; task classes are not directly consumable by current exact recursion. |
| Learning/development | `src/hls/synthetic/components/development.py:A1SaturatingDevelopmentKernel` / `ScheduledSaturatingDevelopmentKernel` | Explicit opportunity-gated saturating development; not MIS-v2 learning-by-doing. |
| Scarce development budget | `src/hls/synthetic/c3.py:BudgetedDevelopmentResources`, `with_development_budget` | Persistent budget and per-development consumption; objective cost separately specified. |
| Opportunity and reward | `components/opportunities.py:A1MixtureOpportunityKernel`; `components/reward.py:CompetenceRewardModel` | Stochastic opportunity can depend on state/task/assigned learner; reward is separate. |
| HLS, strong-SEP, SEP-Omega exact solvers | `src/hls/synthetic/exact.py:solve_exact_hls`, `solve_exact_strong_sep`, `solve_exact_sep_omega` | Exact finite horizon for its supported deterministic `task_at` demand and stochastic opportunity branches; no C5 stochastic demand integration. |
| Common experiment traces | `src/hls/experiment_contract.py` | Can adapt completed results; does not supply a common episode runner. |

## B. Four comparators and canonical policy-class relation

All four must optimize/report the **same** `J`, use the same initial state,
task law, action set, reward, opportunity and development transitions,
resource budget, terminal value, and information model. The comparison
changes only policy restrictions/information use.

| Comparator | Exact rule | Information / horizon | Existing status and changes |
|---|---|---|---|
| **A. STATIC — best stationary task-to-action map** | Choose ex ante a deterministic map `m:q→u`; keep it fixed for the episode and optimize its expected finite-horizon `J_m` under the demand law. The routing map is fixed, but its development subpolicy may condition on current observed state/opportunity and optimize continuation, identically for every map; thus this is a strong static-routing comparator, not a policy with frozen development. Optimize before test paths; never select a map per realized path. | Knows initial state, task law, and model parameters; sees current task to apply `m`; no future realization. Evaluation spans the full horizon. | No such optimizer is in clean `HEAD`. The current dirty C1 diff adds `solve_fixed_best`, but it is limited to C1 deterministic two-task routing and is uncommitted; this design does not treat it as published/canonical support. Implement an experiment-local enumeration of the finite map class, or promote/review the WIP separately. |
| **B. MYOPIC — immediate-value sequential choice** | At each period choose feasible `u` maximizing immediate `R(X,q,u)` with fixed deterministic ties. After observing opportunity `o`, choose feasible `d` maximizing immediate `−c(d)` (normally null when costs are nonnegative). No continuation value enters either decision. | Full current state/task, current opportunity only after it occurs, and same model parameters; one decision period only; no future demand. | No G0 policy object implements this exact rule. `P0ProductionOnlyPolicyNK` is not a substitute: it has N×K actions and a functional lexicographic rank. `solve_exact_strong_sep` is also not this comparator: it restricts operation to immediate reward maximizers but then optimizes future development. Add a small wrapper only if approved. |
| **C. ANTICIPATORY — existing strong-SEP reference** | Use `solve_exact_strong_sep`: operational routing is restricted to current immediate-reward maximizers; conditional development choices use exact continuation value. This explicitly anticipates capability-development consequences while retaining the canonical separated operational restriction. Preserve its tie-value bounds. | Current task/state and exact model/demand law; no realized future path. Finite-horizon continuation is used for development. | **Existing** for deterministic G0/C1 demand via `src/hls/synthetic/exact.py`. Must be extended to expectation over the approved stochastic demand kernel before this dynamic-demand design can use it. Do not describe it as a wholly myopic policy or as a fixed policy. |
| **D. EXACT — nonclairvoyant joint HLS optimum** | `\pi^*` maximizes Bellman value over the full feasible joint `(u,d)` class and known transition kernels. At each decision it conditions on current observed task/state and integrates future demand/opportunity distributions; it does not condition on future sampled outcomes. | Same information and model knowledge as other arms, except its explicit continuation computation; no future realized demand. | **Existing** as `solve_exact_hls` for deterministic `task_at` worlds and stochastic opportunity branches. It is not an executable policy interface for stochastic C5 task transitions yet. A clairvoyant pathwise optimum that receives the sampled future tasks is a different upper-bound diagnostic and must not be the primary exact reference. |

### B.1 Strong-SEP, SEP-Omega and exact-reference relation

Canonical strong-SEP is not “static”: it constrains operational decisions to
the immediate-reward-optimal set, while its development decisions may still
be continuation-aware. That is what `solve_exact_strong_sep` computes in its
current G0 contract. SEP-Omega is a separate continuation-informed separated
policy solved by `solve_exact_sep_omega`; in the audited G0/C1 reference
families it equals HLS within tolerance. Thus it is a valuable modular
sufficiency/equivalence check, not an independent weak baseline. The exact
joint HLS recursion is the main upper reference. These existing equalities
are model-scoped; dynamic C5 extension must be rechecked and not assumed.

The four-arm table above uses strong-SEP for C because it is the extant
anticipatory allocation/development comparator with an explicit restriction.
Run SEP-Omega as a fifth *solver consistency diagnostic* on tiny instances if
the extended recursion supports it; do not silently substitute it for a
different arm. A clairvoyant path optimizer, if shown at all, must be labeled
upper-bound-only and excluded from claims about online adaptation.

## C. One external method

Use **exact-rollout policy improvement** as the single selective external
method, anchored to the myopic policy B. Given a feasible current action `a`,
evaluate current reward plus the exact expected continuation from following
the frozen base policy thereafter:

\[
Q^{roll}_t(s,q,u)=R(s,q,u)+\mathbb E_o\!\left[
  \max_{d\in A_D(s,o,b)}\left\{-c(d)+
    \mathbb E[V^{\pi_B}_{t+1}(S_{t+1})\mid s,q,u,o,d]\right\}
  \right],\qquad
\pi_{roll}(s,q)=\arg\max_{u\in A_O(s,q)}Q^{roll}_t(s,q,u).
\]

Apply the same rule at later decisions (receding one-step improvement).
This is an HLS-specific application of a published rollout method, **not a
reproduction of that paper's machine-maintenance example**. The method is
appropriate here because it uses the same finite MDP, action set, reward and
transition; only its continuation approximation (the base-policy value)
differs from exact HLS. With exact base-policy continuation and a consistent
finite-horizon terminal condition it is a policy-improvement comparator; no
guarantee is claimed if continuation is estimated by uncontrolled Monte
Carlo.

Primary reference: D. P. Bertsekas, J. N. Tsitsiklis, and C. Wu (1997),
“Rollout Algorithms for Combinatorial Optimization,” *Journal of Heuristics*,
3, 245–262, DOI [10.1023/A:1009635226865](https://doi.org/10.1023/A:1009635226865);
[author-hosted paper](https://www.mit.edu/~jnt/Papers/J066-97-rollout.pdf).
The article embeds a heuristic in a dynamic-programming cost-to-go
approximation, gives improvement conditions, and illustrates machine
maintenance. Its experiment is not HLS evidence. HLS compatibility is through
the generic rollout construction over the declared HLS MDP, not by mapping
the paper's maintenance model to HLS.

**Cost:** MEDIUM–HIGH. It needs an exact evaluation of the fixed myopic
continuation under stochastic demand/opportunities and one action lookahead
per feasible current action. Keep it optional: the existing exact HLS solver
is already stronger for these small instances. Do not implement rollout
unless the PI wants an externally grounded approximate anticipatory baseline
or the exact solver proves too costly.

## D. Minimum experimental design

### D.1 Factors and fixed configuration

Use one bounded **2-agent × 2-task/competence** G0/C1 family, one current task
per period, and a preregistered horizon **T=4**. This is a proposed small
extension of the existing finite-horizon C1 fixture, not an existing
published configuration. Reuse the C1 initial competence and action-index
conventions after checking that they avoid reward saturation. Keep agents,
task catalogue, opportunity model, C3 resource model, terminal rule, and
action catalogue identical across all arms.

Only the requested factors vary:

| Factor | Levels | Rationale |
|---|---|---|
| Development intensity `eta` | `0`, `0.10`, `0.75` in the existing C1 saturating kernel; `0` is a null control. | `0.10` appears in canonical G2 D1, and `0.75` in existing C1 reference worlds. These values are anchored to existing fixtures, not selected after seeing comparative outcomes. `0.75` is a stress level, not claimed empirical calibration. |
| Demand | Stationary IID: `Pr(q=1)=Pr(q=2)=0.5` each period. Changing: `Pr(q=1)=0.8` for `t=0,1`, then `0.2` for `t=2,3`. | Both have expected two occurrences of each type over T=4; the second changes the demand distribution while holding expected total composition fixed. Use the existing C5 demand definitions. |

The above is a 3×2 design = **6 scenario cells**. Do not add workforce,
learning-mechanism, exploration, observation-noise, cost, or horizon sweeps.
Use the same initial state and C3 budget in every cell. Set C3 budget to
**one non-null development action per episode** (budget consumption 1.0 per
development; initial budget 1.0), a transparent scarcity control. Keep the
objective penalty `kappa` fixed at zero in the first design so the scarce
resource is the explicit budget, not an arbitrary net-reward conversion.
Report consumed budget separately from reward. If this configuration does
not produce both feasible and infeasible developments or non-saturated
terminal reward, revise the configuration on model-based feasibility grounds
before confirmatory execution; never select on which policy wins.

Use the existing C1 two-learner/two-task heterogeneity and C1 action set where
it is compatible with the selected G0 transition. The current C1 reference
world has a deterministic task sequence and no C5 stochastic task kernel;
using C5 here requires the exact-solver extension below. No future demand
realization may be used to select the static map or policy parameters.

### D.2 Repetitions and random seeds

Separate exploration from confirmation:

1. **Preflight:** hand-check deterministic transitions and run at most 5
   paired seed blocks as a software/interface check. Do not estimate a policy
   effect or tune the model from these outcomes.
2. **Exploratory validation:** 20 paired seed blocks per cell (120 exogenous
   trajectories total), using fixed, published seed IDs selected before any
   run. This is descriptive and diagnostic; no significance claim.
3. **Confirmatory use:** only after the exploratory design is frozen, preregister
   a separate seed list and sample size based on a declared smallest effect of
   interest / precision target. Do not treat the exploratory 20 as confirmatory
   evidence. If no defensible effect-size target exists, report intervals and
   keep the result exploratory rather than inventing a significance threshold.

Within each seed block, generate/store the exogenous demand uniforms/path
before policy execution. Use separate keyed streams for demand and opportunity
innovations. For the same policy comparison and seed, use common random
numbers: the same demand uniforms and opportunity uniforms by period, while
allowing opportunity outcomes and all resulting competence/resource
trajectories to differ endogenously by action. Policies are deterministic in
the minimum design; any rollout simulation RNG, if used, has its own seed and
is not shared with environment streams. A seed match is not evidence of
matched outcomes unless the stored path/innovation keys match.

## E. Exact-reference feasibility and minimum changes

The exact reference must be the **nonclairvoyant expected optimum** under the
known stationary/time-varying demand kernel. Formally, augment the Bellman
state with the sufficient demand-process state and integrate the next-task
kernel:

\[
V_t(s,z,q)=\max_{u\in A_O(s,q)}\left\{
R(s,q,u)+\mathbb E_{o\sim P_O(\cdot\mid s,q,u)}
\left[\max_{d\in A_D(s,o,b)}\left(
-c(d)+\mathbb E_{q'\sim P_Q(\cdot\mid z',t+1)}
V_{t+1}(F(s,o,d),z',q')\right)\right]\right\},
\]

where `q` is the **already observed** current task, `z'` is the sufficient
next demand state determined by the current process state/task, and the
future-task expectation is inside the current action value. For stationary
IID or time-indexed nonstationary demand, `z'` is unnecessary; for Markov
demand it records the current realized task used by the transition kernel.
The terminal condition is the declared terminal reward. This nesting avoids
the clairvoyant error of placing a maximum after observing a future task.

**Current limitation:** `src/hls/synthetic/exact.py` uses
`problem.environment.tasks.task_at(time,state,())`; its own `_task` documents
that stochastic C5 integration is separate. Current `solve_exact_hls`,
`solve_exact_strong_sep`, and `solve_exact_sep_omega` exactly branch over
opportunity outcomes but do not integrate C5 `sample_task` transitions.
Therefore they cannot currently provide the required nonclairvoyant exact
reference for the proposed stochastic demand design. Solving each realized
path with the current deterministic solver would be clairvoyant and is not an
acceptable primary comparator.

**Minimum extension if approved:** add an optional finite demand-kernel
contract to the RQ0 exact solver (or an isolated RQ0 experiment adapter) that
enumerates the small C5 next-task probabilities and carries sufficient demand
state. Return an action/value table keyed by observed state/task so the exact
policy is executable at each period; current `ExactDynamicSolution` returns
only initial action values. Keep deterministic `task_at` behavior unchanged.
For the 2×2, T=4, binary-demand fixture, exhaustively enumerate task and
opportunity branches and cross-check Bellman values against a separate tiny
enumerator. This is an exact-solver extension, not a new simulator
architecture or mechanism.

The G0 `SyntheticEnvironment` currently passes one injected `RandomSource`
to both demand sampling and opportunity sampling. This does not guarantee
policy-independent exogenous streams if call counts differ. The N×K path
solves the paired-demand issue by freezing the demand trajectory first. For
this study, the minimum safe remedy is the pre-generated/keyed exogenous
trajectory and independent policy/environment stream ownership in the
experiment adapter; do not let a policy draw from the environment RNG.

## F. Outcomes, analysis and decision criteria

### F.1 Metrics

Primary:

- **Cumulative reward:** `J` as defined in A.2, in the declared G0 reward
  units, per episode. Keep gross operational reward and objective development
  penalty visible as separate components.
- **Development budget use:** number/amount of C3 resource units consumed and
  remaining; do not add this dimension to reward because `kappa=0` and units
  are not converted.
- **Nonclairvoyant optimality gap:** `J_exact − J_policy` in reward units,
  using exact expected values for each policy where possible. By definition
  it must be nonnegative within numerical tolerance for feasible policies.

Secondary:

- Per-period and pre-/post-demand-change reward, plus task/demand-state
  realization.
- Competence matrix before/after each action and terminal competence.
- Development decisions, opportunities, resource remaining/consumed.
- Action changes relative to each policy's previous decision.
- Solver state count and wall-clock preparation/decision time, recorded
  separately from policy return and measured on the same machine/software.

Do not report an aggregate “adaptivity score.” Reward, resource use,
competence, and computation remain separate. If the question later adds a
development penalty, preregister its units and do not vary it in this first
design.

### F.2 Analysis and uncertainty

For stochastic realized paths, form paired per-seed differences
`J_policy1(seed,cell) − J_policy2(seed,cell)` and report mean, median, standard
deviation, and percentile or studentized 95% interval over independent seed
blocks. Resample whole paired blocks, not individual periods. Report all six
cells and pre/post-change windows; do not pool away the demand × learning
interaction. Exact expected policy values are deterministic model quantities
and should be reported alongside sampled-path summaries. Twenty exploratory
blocks do not establish statistical significance; the confirmatory seed count
requires a separate precision/power decision after exploratory variability is
known, with no tuning of the environment toward an adaptive win.

### F.3 Scientific interpretation controls

- **GO:** exact nonclairvoyant reference, static class optimizer, and myopic
  comparator share the same state, demand law, resources, reward, and
  transitions; preflight verifies unsaturated/nontrivial cases; all paired
  paths and information boundaries are auditable. Results may then characterize
  model-conditional regimes, whether positive, null, or negative.
- **REVISE:** a small implementation gap remains (current stochastic exact
  demand integration, policy action-table extraction, or RNG separation), or
  the unique experiment identifier is unresolved. Resolve these before
  execution.
- **STOP:** exact C5 expectation cannot be validated on the bounded state
  space; existing parameter choices force policy equivalence/saturation across
  all acceptable controls; or the proposed comparison can only be made by
  giving the exact arm future realized demand.

Results beyond the prior HLS evidence would be a controlled mapping of the
**demand-stationarity × development-intensity** interaction under limited
resources, with a best stationary task-conditioned policy, myopic policy,
strong-SEP and exact joint reference evaluated on the same exogenous process.
G2 already establishes constructive development-value reversals in its
two-period deterministic model; G3/G3-H establish specific assignment
sensitivity and future-opportunity boundaries; RQ0 exact worlds establish
model-scoped joint-vs-strong-SEP gaps and SEP-Omega equality; Campaign 2 already
studied prospective development/information contrasts and found mixed
realized consequences for development-only Q01. E1-ANTICIPATION must therefore
answer the missing crossed-factor question, not claim that anticipation itself
is new or universally beneficial.

Further publication-oriented investigation is justified only if a preregistered
interaction or boundary remains interpretable against the static and
strong-SEP results, survives small preregistered parameter perturbations, and
is not reducible to the already established G2/G3/G3-H cases. A null result
showing that stationarity, a strong static map, or limited development budget
makes anticipation unnecessary would be informative and may close this
bounded line. No adaptive-over-static win is required.

## G. Engineering inventory and effort

No code changes are authorized by this design. If the PI later authorizes the
proposed G0/C5 experiment, expected work is:

| Work item | Candidate files | Tests / acceptance | Relative effort | Risk |
|---|---|---|---|---|
| Exact stochastic demand integration and executable action table | `src/hls/synthetic/exact.py` or an isolated `experiments/...` solver adapter | Exact deterministic regression unchanged; binary T≤4 expectation agrees with independent exhaustive enumeration; action table uses only current observed task and transition law. | MEDIUM | Medium: exact solver semantics, tie preservation, information order. |
| Static and myopic evaluators for same G0 environment | New experiment-local module under `experiments/` (avoid changing `c1.py` until its dirty diff is reviewed) | Exhaustive static map count; hand-check immediate greedy decisions; verify same objective/action feasibility. | LOW–MEDIUM | Low if isolated; high scientific risk if baseline accidentally uses future path. |
| Scenario builder, paired seeds and environment replay | New experiment-local scenario/runner module; reuse C5, G0 and existing result adapter | Same exogenous path hashes across arms; stream separation; no policy access to future task list; deterministic replay. | MEDIUM | Medium: current `SyntheticEnvironment` shares its injected RNG between task and opportunity sampling. |
| Metrics and persisted results | New experiment-local analysis/results module; reuse `ExperimentRun` only as output envelope | Reward reconciles with traces; resource and objective cost remain distinct; no overwrite; paired interval resamples seed blocks. | LOW–MEDIUM | Low-to-medium; no historical files touched. |
| Rollout comparator (optional) | Experiment-local module; no solver dependency expected if small exact policy evaluation suffices | Rollout continuation agrees with exact base-policy value on tiny states; no Monte Carlo RNG leakage. | MEDIUM–HIGH | Medium; unnecessary if exact DP is affordable. |

**Dependencies:** no new package is justified for the minimum exact recursion.
The design needs no Gurobi/MILP backend and does not need ADPOL/ADPBF. If
rollout continuation is evaluated by exhaustive finite recursion, it also
needs no solver dependency.

**Do not modify** `src/hls/small_problem_world.py` or
`src/hls/synthetic/c1.py` as part of this design. Both currently have
pre-existing uncommitted changes in the worktree. The latter diff adds a
fixed-routing evaluator and tests; it is potentially relevant but is not
clean-HEAD capability and must be reviewed independently before reuse. The
former adds a functional-requirements layer. Neither local change is required
to establish the design boundary described here.

## H. Scientific risks and limitations

1. **Policy-class naming:** static task maps, strong-SEP, SEP-Omega, and exact
   joint HLS are different classes. A task-dependent map is not a constant
   action; strong-SEP is not static; SEP-Omega is not an ordinary fixed
   baseline.
2. **Demand information:** pathwise exact optimization is clairvoyant. The
   primary exact reference must optimize expected value using current observed
   demand plus known kernel, not sampled future tasks.
3. **External-method scope:** rollout's original numerical evidence concerns
   its own scheduling/maintenance examples. The HLS adaptation is a method
   transfer and requires its own tests; it is not evidence imported from that
   paper.
4. **Opportunity vs learning by doing:** G0 A1/C1 development is opportunity-
   gated explicit development. It is not the direct assignment-driven MIS-v2
   update, and conclusions must be labeled accordingly.
5. **Existing prior results:** G2/G3/G3-H already exhibit model-scoped
   development-value effects. Campaign 2 already compares prospective
   information/development decision rules and reports mixed realized Q01
   consequences. This experiment must not claim first demonstration of
   anticipation or broad superiority.
6. **No real-world inference:** the proposed G0/C5 model is synthetic and
   full-information. It validates model-conditional decision/evaluation
   behavior, not unknown-parameter online learning or empirical prevalence.

## I. Decision and next gate

### Recommendation: **REVISE**

The scientific design is feasible and computationally bounded in principle,
but the current repository cannot execute it faithfully as specified. The
minimum required before any campaign is:

1. Resolve the experiment-ID collision with the already-published Nembhard
   HLS-E1.
2. Add a small, isolated C5 stochastic-demand expectation path and executable
   action extraction to the RQ0 exact solvers, retaining deterministic solver
   behavior unchanged.
3. Add same-model static-map and immediate-myopic evaluation; do not use the
   uncommitted `c1.py` static helper as canonical without review.
4. Pre-generate/key exogenous demand and opportunity innovations separately;
   test that policy randomness cannot perturb them.
5. Run the no-experiment preflight design review of task reward saturation,
   resource scarcity, and expected action-count/state-count before selecting
   any confirmatory sample size.

These are bounded evaluation/policy wrappers and an exact-solver extension,
not a new simulator architecture, learning mechanism, or refactor. If the PI
requires the existing N×K/MIS-v2 mechanism rather than G0/C1, stop this design
and decide that model choice explicitly: that route lacks an anticipatory
policy and exact solver, so it is not a drop-in replacement.

## Sources inspected

- G0 and canonical RQ0 definitions: `docs/experiments/G0.md`,
  `docs/research_questions.md`, `docs/HLS_CURRENT_STATE.md`,
  `docs/theory/HLS_DYNAMIC_THEORY.md`,
  `docs/experimental_foundations/RQ0_INTEGRATED_DESIGN.md`.
- G2 and G3/G3-H ground truths: `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`,
  `docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`.
- RQ0 code: `src/hls/synthetic/{interfaces,state,environment,exact,c5,c3,c1}.py`,
  `src/hls/synthetic/components/{development,opportunities,reward,resources,tasks}.py`.
- N×K alternatives: `src/hls/hls_lab_nk_environment.py`,
  `hls_lab_nk_execution.py`, `hls_lab_nk_learning.py`,
  `hls_lab_nk_policies.py`, `hls_lab_nk_production.py`.
- Campaign 2: `docs/theory/CAMPAIGN_2_THEORETICAL_SPECIFICATION.md`,
  `docs/experiments/CAMPAIGN_2_PREREGISTRATION.md`,
  `docs/experiments/CAMPAIGN_2_RESULTS.md`,
  `src/hls/campaign2_theory.py`, and `experiments/confirmatory/rq0_integrated/`.
- Existing RQ0 solver tests: `tests/synthetic/test_exact_solver.py`,
  `tests/synthetic/test_c5_dynamic_demand.py`,
  `tests/synthetic/test_c3_scarce_resources.py`,
  `tests/synthetic/test_c1_reference_worlds.py`.
- External method: Bertsekas, Tsitsiklis & Wu (1997), DOI
  [10.1023/A:1009635226865](https://doi.org/10.1023/A:1009635226865),
  [author-hosted primary paper](https://www.mit.edu/~jnt/Papers/J066-97-rollout.pdf).
