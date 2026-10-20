# HLS: unified scientific formulation

**Status:** research framework proposal, consolidated 2026-10-21 from the
existing S1–S4 evidence. It is not a new theorem, a universal simulator
specification, or evidence that one organizational architecture is generally
superior.

This document supplies a common mathematical vocabulary for the completed
scenario studies. It preserves their differing action spaces, reward models,
information contracts, and evidence limits. The existing three-level
ontology—scenario, mechanisms, organization—remains the conceptual index; this
formulation does not prescribe a software refactor.

## 1. What HLS is, and is not

The evidence supports treating HLS as **a parameterized family of heterogeneous
organization problems and an experimental methodology for matching decision
architectures to problem structure**. It is not one organizational algorithm.
Its common object is a system with heterogeneous agents and task-relevant
capabilities, an environment that supplies work and constraints, mechanisms
that may change capabilities or beliefs, and one or more organizations that
choose feasible actions using specified information.

This positions HLS in relation to, rather than in place of, established
formalisms:

- Static assignment and matching are special feasible-action models for
  one-period allocation.
- A finite-horizon MDP is an appropriate full-state formulation when state,
  transition law and reward are known. S2b and S4 use small deterministic
  instances of this type.
- A POMDP or belief-state control problem is appropriate when latent state
  affects reward or transitions and decisions depend on observations/history.
  The S3a noisy-competence variant and S3b have partial-information aspects,
  but neither result alone validates a general POMDP solution.
- Bandits model learning from selectively observed outcomes. S3b combines
  per-pair bandit estimates with a matching oracle; this is an HLS combinatorial
  adaptation and does not inherit single-play guarantees automatically.
- Adaptive task allocation names a broad class of organizations, not a single
  mathematical model. Whether adaptation is useful depends on what changes,
  what is observed, how actions couple across time, and what an action changes
  in the future.

Potential HLS contribution is therefore not ownership of matching, MDPs,
bandits, or adaptive allocation. It could lie in a carefully specified,
reproducible comparative methodology that jointly characterizes problem
structure, capability mechanisms, information, organizations, and their
performance/cost interactions. The present finite synthetic cases are
foundational evidence for that program, not validation of a new general theory.

Against four candidate descriptions: **(A)** a common representation is
supported conceptually; **(B)** a parameterized family is the most accurate
formal characterization; **(C)** architecture selection by structural
diagnosis is a useful, partially evidenced methodological principle, but not
yet a validated general selection procedure; **(D)** a unique HLS organization
is not the project claim and is inconsistent with the scenario-specific
policies studied.

## 2. Common system model

Let agents be `i ∈ I={1,…,N}`, task types be `k ∈ K={1,…,K}`, and decision
periods be `t=0,…,T−1`. The general notation below is deliberately modular:
components absent from a scenario are omitted or fixed, rather than presumed
to exist in every HLS model.

### 2.1 Real system state and exogenous inputs

Write the evaluator's real state as

\[
X_t=(C_t,H_t,B_t,Q_t,Z_t,\Theta_t),
\]

where:

- `C_t[i,k]` is real task-relevant competence/capability; it is not itself an
  observed reward.
- `H_t` contains any additional mechanism state needed for a Markov
  transition (for example, an experience stock if the selected law requires
  one). It is absent where competence alone suffices, including the S4
  implementation of MIS-v2.
- `B_t` is any persistent resource inventory or budget; it is absent in
  S1/S2a/S3a/S3b/S4 and present in S2b.
- `Q_t` is optional backlog, setup, or other intertemporal operational state.
  It is not present in the six canonical scenarios.
- `Z_t` is an exogenous environment/demand regime or latent state.
- `Θ_t` represents unknown reward/transition parameters where useful; it is
  evaluator state, not automatically policy knowledge.

Demand `D_t` may be an exogenous input or a component of `Z_t`. Exogenous
disturbances `W_{t+1}` evolve independently of policy actions when the scenario
declares them exogenous. The current scenario determines whether future demand
or future disturbances are known, unknown, or random.

### 2.2 Actions and constraints

An organization chooses a feasible joint action `A_t ∈ 𝒜(X_t,D_t)`. In the
canonical matching cases this can be represented by binary assignment
variables `x[i,k,t]` with agent capacity

\[
\sum_k x_{ikt}\leq 1,
\]

and task-unit availability

\[
\sum_i x_{ikt}\leq D_{kt},\qquad x_{ikt}\in\{0,1\}.
\]

When each task type is available at most once, `D_{kt}∈{0,1}` gives the usual
one-to-one matching. Multiple units of a task type are distinct demand units
with the same type-specific reward column. The general N×K laboratory also
contains divisible productive effort and separate teaching actions; those are
different feasible-action contracts and must not be silently equated with
binary matching.

Additional constraints are scenario-specific, for example the S2b shared
budget

\[
\sum_{t,i,k}x_{ikt}\leq B_0,
\]

or per-period capacity, effort, eligibility, and task coverage constraints.
The set `𝒜` states whether assignments may be partial; one must not infer
mandatory coverage from a solver's name.

### 2.3 Reward, competence, and observations

Let the realized collective outcome be `Y_t` with conditional law

\[
Y_t\sim P(\cdot\mid X_t,D_t,A_t,\Theta_t),\qquad
R_t=\rho(X_t,D_t,A_t,Y_t)-g(X_t,A_t).
\]

Here `g` is included only if that scenario explicitly values a cost in the
objective. Resource feasibility and a cost penalty are distinct: consuming a
unit under a hard budget does not imply subtracting an additional monetary
cost. For additive matching scenarios, the expected reward is
`Σ_{i,k} C_t[i,k] x[i,k,t]`; for S4 it is pre-transition competence summed
over executed pairs. Functional success, partial satisfaction, CES, realized
output, reward, and effort/cost are different measurements unless a model
explicitly defines an aggregation.

The organization receives observations `O_{t+1}` from a declared observation
kernel

\[
O_{t+1}\sim G(\cdot\mid X_t,D_t,A_t,Y_t,X_{t+1}).
\]

Its information is a filtration `𝓘_t^π` generated by permitted current inputs,
past actions and observations, plus any declared prior/model knowledge. A
policy must be measurable with respect to that information and select only
`𝒜(X_t,D_t)`-feasible actions. Real state, policy observation, estimate/belief,
and evaluator-only diagnostics must remain distinct. In particular, no policy
gets future realized demand, unselected-pair outcomes, or oracle assignments
unless the comparison explicitly labels a full-information reference.

### 2.4 Dynamics and objective

The general state transition can be factored as

\[
X_{t+1}=F(X_t,D_t,A_t,W_{t+1};\,\mathcal M),
\]

where mechanism bundle `𝓜` specifies the applicable transition laws. For
competence, distinguish at least:

\[
C_{t+1}=F_C^{exo}(C_t,W_{t+1})\quad\text{(exogenous; action-independent)},
\]

from

\[
C_{t+1}=F_C^{endo}(C_t,H_t,A_t,W_{t+1})\quad\text{(endogenous; action-dependent)}.
\]

A model may combine both only if explicitly defined; none of S1–S4 combines
them. Belief/estimator state is updated separately, e.g.
`M_{t+1}=U(M_t,A_t,O_{t+1})`; this is learning about state/reward or a policy,
not physical competence learning. The six canonical scenarios do not all
contain a belief process.

For a finite-horizon organization `π`, the collective objective is

\[
J(π\mid X_0,\mathcal I_0)=
\mathbb E_π\!\left[\sum_{t=0}^{T-1}R_t+R_T^{term}\right],
\]

with optional terminal reward only where defined. The admissible policy class,
model knowledge, observations, and randomization must accompany any value
comparison. An exact full-information dynamic program is a reference for its
specified model and policy class, not evidence that a practical policy knows
the model or can scale to a large state space.

## 3. Structural properties and implications

These properties explain why the six scenarios require different
organizational machinery. The first three implications below are mathematical
identities under stated assumptions; results for particular algorithms or
instances remain instance evidence.

### 3.1 Temporal separability

If `𝒜(X_t,D_t)=𝒜_t` is independent across periods, state/reward do not depend
on prior actions, there is no shared intertemporal resource, and total reward
is additive, then

\[
\max_{a_0\in 𝒜_0,\ldots,a_{T-1}\in 𝒜_{T-1}}\sum_t R_t(a_t)
=\sum_t\max_{a_t\in 𝒜_t}R_t(a_t).
\]

This proves why S2a needs no temporal planner. It does not apply when actions
share budget, alter later state, or affect pending work.

### 3.2 Shared resources and endogenous consequences

When `B_{t+1}=B_t−m(A_t)+b_t^{replenish}` couples periods, or when
`C_{t+1}` depends on `A_t`, the action at `t` changes the continuation problem.
For a known finite-state model the Bellman equation is

\[
V_t(X)=\max_{a\in𝒜(X,D_t)}\{r(X,D_t,a)+\mathbb E[V_{t+1}(X')\mid X,D_t,a]\}.
\]

S2b and S4 each verify a strict planning gap in a constructed small instance,
but through different state couplings. This establishes existence in those
instances, not that planning always has strict value or that a particular
architecture is generally superior.

### 3.3 Observability and nonstationarity

If current reward means are known and the state that determines them is
observed, period-wise exact optimization can immediately select the current
optimum; S3a demonstrates this for its public synthetic mapping. If the state
is latent and only selected outcomes are observed, estimation/exploration is
needed to improve decisions in general, but the best policy depends on the
observation and change model. S3b is precisely a partial-feedback problem.
Its index-plus-matching construction is not equivalent to a published
single-play bandit, and its finite experimental ranking is not an algorithmic
guarantee.

### 3.4 Evidence status

- **Mathematically proved within assumptions:** S2a separability; exact
  optimality of the specified linear assignment solution; Bellman recursion
  as finite-model optimum; and the MIS-v2 competence formula and restricted
  sufficient condition recorded for S4.
- **Independently computationally verified:** S1/S2a/S2b assignment values
  against enumeration; S4 Bellman and best-myopic values against independent
  sequence enumeration in the reported bounded instances.
- **Empirical within synthetic configurations:** D0/D1/D2, observation-noise
  outcomes, S3b policy comparisons and S4's strict-gap family. These do not
  establish external validity, frequency of the phenomenon, or general
  superiority.
- **Open hypotheses:** which general structural conditions make information,
  adaptation, endogenous learning, transfer, or joint optimization worth
  their computational and resource costs; and how conclusions scale beyond
  the small exact models.

## 4. Six scenarios as specializations

The following are reductions of the common model, not six claims of one
uniform implementation. `C` denotes known expected reward/competence where
that is the scenario's declared reward model.

### S1 — static assignment

Set `T=1`, `C_t=C` known and constant, fixed demand with one unit per task,
no state transition affecting reward, and one-to-one constraints. The action
is `x∈{0,1}^{N×K}` and

\[
\max_x\sum_{i,k}C_{ik}x_{ik},\quad
\sum_kx_{ik}\le1,\quad\sum_ix_{ik}\le1.
\]

The optional-cardinality bipartite solver uses SciPy
`linear_sum_assignment` (modified Jonker–Volgenant backend); the historical
Hungarian method of Kuhn (1955) is not reimplemented. The tested hypothesis is
that exact assignment reaches the stated finite optimum and greedy need not.
The canonical 3×3 matrix has exact and enumerated reward `2.60`, versus greedy
`1.80`; the test checks feasibility, repeatability and solver/enumeration
agreement. This verifies the instance and solver contract, not a new algorithm
or a scale result.

### S2a — variable demand, separable periods

Keep `C` known/constant and no state transition; let integer task-unit demand
`D_{kt}` vary. Expand each unit into an individual task column of type `k`,
with reward `C_{ik}`. Each agent works at most once per period and each
demand-unit is served at most once. Resources renew, and there is no backlog,
switching cost, or intertemporal constraint. Thus each `𝒜_t` is independent
and the separability identity applies. In the deterministic four-period
instance, exact period optimization and global enumeration both yield `8.00`,
greedy `7.20` (exact per-period rewards `2.60,2.70,2.70,0`). The tested
hypothesis is that demand-unit expansion preserves feasibility and that the
period-wise optima equal the full-horizon optimum. The runner/tests check unit
counts, capacities, fixed competence and deterministic replay. This validates
demand handling and separability, not a need for planning.

### S2b — shared nonrenewing budget

S2a is augmented only by a global nonrenewing assignment budget `B`. Competence
and reward remain known/constant and demand is known for the entire horizon.
The dynamic-programming state is `(t,b)`:

\[
V_t(b)=\max_{a\in𝒜_t:m(a)\le b}\{R_t(a)+V_{t+1}(b-m(a))\},\quad V_T(b)=0.
\]

With sufficient budget `B=3`, exact myopic, Bellman and enumeration equal
`1.90`; with binding `B=1`, exact myopic is `.90`, Bellman and independent
global enumeration are `1.00`; `B=0` gives zero for all. The tested hypothesis
is that a binding shared budget can make immediate consumption suboptimal for
the horizon; runner assertions/tests verify immediate optimality, budget
conservation, Bellman/enumeration agreement and the equality control. This is
a constructive example, not strict advantage in every instance.

### S3a — exogenous changing, observable competence

Competence/reward mean follows a seeded exogenous trajectory independent of
assignments; the environment supplies current competence observation, and
`E[Y_{ikt}]=C_{ikt}` is publicly known in this synthetic instance. The
organization sees the current matrix, not future changes, and solves the
one-to-one matching each period. D0/D1/D2 vary both amplitude and persistence
in the base sensitivity design, so those effects are not separately
identified. At zero observation noise, P0 reactive matching equals the
period-wise oracle at `634.150`, `614.450`, and `679.150`; the initial LinUCB
campaign yielded `611.950`, `604.250`, `676.800` and fixed training map
`634.150`, `581.900`, `584.550` for D0/D1/D2. The evidence shows that
observable-state reorganization can capture the dynamic opportunity in this
scenario without learning selector parameters. With noisy observations
`C_obs=clip(C_true+ε,0,1)`, sigma `.10/.20`, P0 beat LinUCB in all nine
dynamism-noise cells; this is specific to this observation/reward mapping and
20-seed protocol. LinUCB is the contextual-bandit method of Li et al. (2010),
but this HLS use is not a reproduction of its personalized-news benchmark; it
is an adapter evaluated on the synthetic assignment scenario. The question
tested was whether changing observable competencies make online reallocation
useful relative to a trained fixed map, and whether selector learning adds
value beyond a reactive rule. Paired potential outcomes, a shared
solver/constraint contract and training/evaluation seed separation were
checked by the runner and focused tests; the noise result is empirical over
the declared 20 seeds.

### S3b — exogenous unknown, nonstationary rewards and partial feedback

Use `N=K=3`, one simultaneous unit of each task, horizon 300, means
`C_{ikt}∈{.2,.8}` changing exogenously in stationary, single abrupt, or
recurrent regimes. Selected pair outcomes are Bernoulli and only selected
edges are observed; means, future changes and unselected outcomes are hidden.
Each action is a matching; expected reward is additive and the evaluator's
dynamic matching oracle is reference-only. Nine common calibration periods
provide three observations per pair; 291 periods are evaluated on 30 paired
seeds. Per-pair UCB1, SW-UCB, recent/global means and GLR-CUCB are combined
with matching; this is an adaptation to multiple simultaneous assignments.
The cited method references are Auer, Cesa-Bianchi & Fischer (2002) for UCB1,
Garivier & Moulines (2011) for sliding-window UCB, and Zhou et al. (2020) for
GLR-CUCB. Their original single-play/semi-bandit formulations and the HLS
multiple-play composition are distinguished in the cumulative record.
Original expected rewards: UCB1 `644.24/623.30/591.10`, SW-UCB
`644.24/575.16/524.24`, recent mean `690.56/577.75/477.82` for stationary,
abrupt, recurrent. The factorial ablation showed large history×bonus
interactions. GLR-CUCB returned `617.66/583.44/524.92`, with no detections in
the evaluated runs and costly forced exploration; it did not offer a clear
overall advantage. The S3b evaluation campaigns are complete; **the scientific
line remains open** because the matching composition, feedback sparsity,
exploration, and detection behavior are not generally characterized. No
specific follow-on campaign is authorized by this framework. The question
was whether history retention, confidence bonuses and change detection help
with hidden nonstationary pair rewards under semi-bandit feedback. Tests check
feedback only on selected edges, feasibility, repeatability and estimator
updates. Paired replays validate these instance comparisons, not guarantees
for the multiple-play composition; post-calibration feedback histories diverge
by policy, limiting causal interpretation of the factorial contrasts.

### S4 — endogenous competence learning

Use known deterministic demand and initial competence, no exogenous competence
changes, and action-dependent MIS-v2 learning. In the tested binary-exposure
model,

\[
C_{i,k,t+1}=1-(1-C_{i,k,t})(1-\eta_{ik})^{x_{ikt}},
\quad x_{ikt}\in\{0,1\},\quad 0<\eta_{ik}<1.
\]

Reward is pre-transition `Σ C_{ikt}x_{ikt}`; an assignment's production reward
is not additionally charged as a development cost. Full-state, known-model
Bellman is compared to periodwise exact immediate maximization. `BEST-MYOPIC`
is the strongest tie-aware comparator: it is restricted at every state to
immediate-reward maximizers but plans over ties. The original 2-agent/2-task
case B gave `REACTIVE=2.661353125`, while `BEST-MYOPIC=Bellman=enumeration=
2.876171875`; thus the original gap was tie-break dependent. A bounded
one-task family with `a=.525`, `b=.500`, `η_A=.15`, `η_B=.25`, horizon
`T=1,2,3,4` yielded Bellman-minus-BEST-MYOPIC `0,.00375,.0656875,.146459375`.
At `T=4`, Bellman sacrifices `.025` immediate reward and recovers `.171459375`
later; an `enabled=False` frozen-competence control removes the gap
(`2.10` for all four references). Independent enumeration validates the
finite calculations. The question tested was whether endogenous exposure can
make a strictly suboptimal immediate action worthwhile against BEST-MYOPIC,
not merely against one fixed tie break. The exact solver, tie-aware DP and
independent sequence enumerator agree in the tested family; focused tests also
check that only executed pairs develop. This supports existence and a narrow
controlled regime, not general prevalence, realism, scalability, or universal
necessity of MIS-v2.

## 5. Decision architecture as a function of structure

The scenarios support a conditional selection principle, not a single HLS
policy:

| Problem property | Mathematical consequence | Architecture class relevant to evaluate | Evidence boundary |
|---|---|---|---|
| Independent periods, known current reward | Period-wise maximization is globally sufficient | Exact assignment/matching | S1/S2a; no temporal planner needed under assumptions |
| Shared persistent budget/state | Actions compete across periods | Dynamic programming/MDP for tractable known models | Constructive S2b instance; not all budgets give a strict gap |
| Current state observable, reward mapping known | React to current state and optimize current feasible action | Reactive exact assignment | S3a P0 reaches evaluator oracle for the declared mapping |
| Hidden reward, selected-action feedback | Estimate from feedback; combinatorial action oracle handles feasibility | Bandit/online estimation plus matching | S3b tested compositions; guarantees require separate proof |
| Actions change future competence | Development exposure changes continuation state | Full-state DP as small exact reference; other approximations require separate evidence | S4 constructive finite family; exact DP is not scalable by implication |

Information and action catalog must be held fair when comparing organizations.
An apparent gain may instead arise from better information, a more permissive
action set, a stronger tie-break, or evaluation access to truth. Conversely,
negative results are informative: S3a's selector learning added no value
against a correct reactive model in the zero-noise case; GLR-CUCB detection
did not activate in the evaluated S3b trajectories; S4's first purported
anticipatory gap disappeared against BEST-MYOPIC.

## 6. Evidence and source traceability

This synthesis treats the cumulative engineering record as the chronological
index and inspects source artifacts rather than converting its summaries into
new claims. Principal implementation/evidence paths:

| Scenario | Implementation / runner | Tests | Saved evidence |
|---|---|---|---|
| S1 | `src/hls/hls_lab_nk_assignment.py`; `experiments/run_hls_hungarian_assignment.py` | `tests/test_hls_lab_nk_assignment.py` | `results/experiments/hls_hungarian_assignment/results.json` |
| S2a | same assignment solver; `experiments/run_hls_s2a_static_demand.py` | `tests/test_hls_lab_nk_assignment.py` | `results/experiments/hls_s2a_static_demand/results.json` |
| S2b | `experiments/run_hls_s2b_intertemporal_budget.py` | `tests/test_hls_s2b_intertemporal_budget.py` | `results/experiments/hls_s2b_intertemporal_budget/results.json` |
| S3a base | `experiments/run_hls_dynamicity_sensitivity.py` | `tests/test_hls_dynamicity_sensitivity.py`, `tests/test_hls_lab_nk_assignment.py`, `tests/test_hls_lab_nk_linucb_assignment.py`, `tests/test_linucb.py` | `results/experiments/hls_dynamicity_sensitivity/results.json` |
| S3a information/noise | `experiments/run_hls_dynamicity_information_ablation.py`; `experiments/run_hls_dynamicity_observation_uncertainty.py` | corresponding `tests/test_hls_dynamicity_*.py` | matching result directories under `results/experiments/` |
| S3b | `src/hls/nonstationary_assignment.py`, `src/hls/glr_cucb.py`; three S3b runners | `tests/test_hls_s3b_nonstationary_assignment.py`, `tests/test_hls_s3b_glr_cucb.py`, `tests/test_hls_lab_nk_assignment.py` | `hls_s3b_nonstationary_unknown_assignment`, `hls_s3b_factorial_ablation`, `hls_s3b_glr_cucb` result directories |
| S4 | `src/hls/synthetic/hls_s4.py`; `experiments/run_hls_s4.py`; `experiments/run_hls_s4_validation.py` | `tests/synthetic/test_hls_s4.py`, `tests/test_hls_lab_nk_learning_transition.py` | `hls_s4/results.json`; `hls_s4_validation/results.json` |

The full decisions, parameters, traces, earlier interpretation and corrections
are retained in the [cumulative execution plan](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md).
The prior vocabulary and N×K-specific boundaries are in
[HLS Ontology v0.1](HLS_ONTOLOGY_V0_1_2026-10-23.md). Tests establish code
contracts and enumeration checks establish values for finite instances; neither
alone establishes external validity.

Method references used by these scenario studies: Kuhn (1955), *The Hungarian
Method for the Assignment Problem* (historical formulation; not the SciPy
backend implementation); Li et al. (2010), *A Contextual-Bandit Approach to
Personalized News Article Recommendation*, [arXiv:1003.0146](https://arxiv.org/abs/1003.0146);
Auer, Cesa-Bianchi & Fischer (2002), [DOI 10.1023/A:1013689704352](https://doi.org/10.1023/A:1013689704352);
Garivier & Moulines (2011), [DOI 10.1007/978-3-642-24412-4_16](https://doi.org/10.1007/978-3-642-24412-4_16);
Zhou et al. (2020), [arXiv:1908.10402](https://arxiv.org/abs/1908.10402).
S4 uses the existing HLS MIS-v2 definition documented in
[`HLS_CAPABILITY_DEVELOPMENT.md`](../theory/HLS_CAPABILITY_DEVELOPMENT.md);
it does not claim that this formulation is a reproduction of a separate
published learning law.

## 7. Research state and open questions

**Completed evidence:** deterministic assignment and separability references
(S1/S2a); shared-budget coupling example (S2b); exogenous observable dynamics
with information/noise ablations (S3a); hidden nonstationary reward campaigns,
factorial history×bonus ablation, and one GLR-CUCB evaluation (S3b); exact
endogenous MIS-v2 comparisons, tie-aware myopic reference, bounded strict-gap
family and frozen-learning control (S4).

**Disconfirmed or narrowed interpretations:** variable demand alone does not
require planning (S2a); a shared resource can, but does not always, create a
strict planning gap (S2b); observable current competence explains dynamic
reorganization in the declared S3a mapping without selector learning; the
initial S4 gap was not strict against all myopic policies; GLR-CUCB's evaluated
recovery cannot be credited to detection when no alarms fired.

**Still open:**

1. **S3b scientific line:** how partial feedback, history retention,
   exploration and combinatorial matching jointly determine performance;
   whether any applicable guarantees can be established for the exact
   multiple-assignment adaptation; why detector behavior and reward differ
   under broader, scientifically justified conditions. The completed GLR-CUCB
   evaluation is not closure of this line.
2. **S4 generalization:** how broad the MIS-v2 strict-gap regime is beyond the
   narrow one-task horizon family; robustness to heterogeneous demand,
   action constraints, observation limits, and alternative established
   capability mechanisms. The present existence result is not a prevalence
   estimate.
3. **Scalability:** computational and memory growth of exact assignment,
   Bellman state enumeration and independent sequence enumeration beyond the
   tiny instances. No scalability conclusion is established by the local
   smoke/timing data.
4. **Scenario validity:** whether any of the synthetic task/reward structures
   represent a practical application with defensible empirical parameters.
5. **Mechanism/organization interaction:** how to distinguish mechanical
   transition effects from policy-mediated value, resource competition and
   information effects under common action catalogs and objectives.

No new experimental campaign is scheduled here. A subsequent decision should
first state the unresolved claim, its evidence requirement, and why existing
artifacts do not answer it; this is a research-state record, not authorization
to implement.

## 8. Provenance and unresolved metadata

The event entries in the execution register date the S1–S4 scenario work and
the S3b reviews to **2026-10-20**. This consolidation is dated **2026-10-21**.
The ontology file supplied for review has a title/date of **2026-10-23**, which
is later than the current consolidation date. Its contents are preserved and
used as a semantic source; repository evidence available here does not
establish whether that label is a future planned date, a metadata error, or a
later-file timestamp. This inconsistency is not silently resolved by
backdating or rewriting prior entries.
