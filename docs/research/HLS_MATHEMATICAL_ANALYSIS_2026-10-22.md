# HLS mathematical analysis — 22 October 2026

**Scope:** mathematical analysis of the three investigations selected in the
20–21 October synthesis. No experiment, algorithm, implementation, or model
change is authorized by this report. The prior evidence synthesis and
prioritization are [here](HLS_SCIENTIFIC_EVIDENCE_SYNTHESIS_2026-10-20.md)
and [here](HLS_PRIORITIZED_INVESTIGATIONS_2026-10-21.md).

## 1. Executive findings

1. **Joint versus strong SEP:** the basic policy-class result is already
   proved: under common physics, information, feasible actions and reward,
   `Pi_SEP ⊆ Pi_HLS`, hence `J_SEP,max ≤ J_HLS`. Strictness is not implied.
   In finite exact worlds, strictness is equivalent to the absence of an
   HLS-optimal policy that is strong-SEP admissible. RQ0 has both reducible
   and strict-gap exact families. The remaining question is a compact
   structural characterization across opportunity, resource and demand
   effects—not whether a strict case exists.
2. **Knowledge transfer × MIS-v2:** both mechanisms act on the same bounded
   competence matrix, but by different sequential laws and at different
   stages. When they update the same cell, their combined increment is
   subadditive relative to adding isolated increments because both act on the
   remaining competence gap. This proves a state-level overlap identity;
   it does **not** determine the sign of a collective reward interaction.
   The existing N×K action catalog and resource accounting can support a
   clean factorial *mechanism* ablation by retaining the same actions and
   resource charges when a transition is disabled. Closed-loop policy effects
   must be analyzed separately.
3. **Partial information × endogenous development:** the N×K observation,
   posterior-update and MIS-v2 paths can be combined in execution. However,
   the available belief-planning route plans over hidden problem reward type,
   while its actual MIS-v2 state change is not forecast in the Bellman
   recursion. Thus the simulator can test estimate-update contrasts, but it
   does not currently supply an exact finite-horizon reference for the
   partially observed, competence-evolving problem. Nembhard productivity
   (`D,k,p,r`) is a separate state/model and cannot be substituted for MIS-v2
   competence (`c,eta`).

**Recommendation:** investigation 2 is the best prepared for experimental
design, subject to preregistering the transition-ablation versus closed-loop
estimands and verifying identical action feasibility/resource accounting.
It has direct N×K transfer/MIS mechanisms and traceable states. It is not
ready for execution on this analysis alone. Investigation 1 is the strongest
for further exact mathematics; investigation 3 has a more substantial
reference-policy gap.

## 2. Notation and evidence categories

Throughout, `FACT` denotes a verified definition, proof, code behavior, or
recorded result; `INFERENCE` is a mathematical interpretation; `CONJECTURE`
is falsifiable but unproved; `PROPOSAL` is a possible controlled test.

An organizational finite-horizon problem has state `s_t`, action `a_t`,
feasible set `A(s_t)`, transition kernel `P(s'|s,a)`, reward `r(s,a)`, and
policy information `I_t`. For a policy class `Pi`,

\[
J_\pi(s_0)=\mathbb E_\pi\left[\sum_{t=0}^{T-1}r(s_t,a_t)+g(s_T)\mid s_0\right],
\qquad J_\Pi(s_0)=\sup_{\pi\in\Pi}J_\pi(s_0).
\]

The finite-horizon problems below use undiscounted reward unless the selected
canonical instance explicitly defines a terminal term. Physical outputs,
functional success, effort/resource use, competence, estimation error, and
compute cost remain separate quantities; no universal scalarization is
introduced.

## 3. Investigation 1 — joint decisions versus strong SEP

### 3.1 Common-world model

Let the state just before routing be

\[
s_t=(C_t,B_t,W_t,t),
\]

where `C_t` is true competence, `B_t` is remaining development/resource
capacity, and `W_t` is current demand/environment state. At that decision time
the policy receives `I_t` as defined by the experiment; for the canonical
RQ0 exact comparisons the common state and transition law are known, but the
future realized demand and future opportunity draws are not revealed.

The action sequence within a period is not a single simultaneous choice:

\[
A_t\;\longrightarrow\;O_t\;\longrightarrow\;D_t,
\]

where the router chooses assignment/routing `A_t` from the common feasible
set, opportunity `O_t` is observed according to `p(o|s_t,A_t)`, then the
development manager chooses `D_t` from the feasible post-opportunity set.
The next state is

\[
C_{t+1}=F_C(C_t,A_t,O_t,D_t),\quad
B_{t+1}=b(B_t,D_t),\quad W_{t+1}\sim P_W(\cdot|W_t).
\]

Let `A(s)` be the common feasible assignment set and `D(s,a,o)` the
development set after assignment `a` and opportunity `o`. The budget state
is updated by resource debit `c_D(s,a,o,d)`; for a scalar budget, feasible
development satisfies `c_D≤B_t` and `B_{t+1}=B_t-c_D`, while multiple
resources retain a vector state. Write `Phi(s,a,o,d,w')` for the complete
next state assembled from `F_C`, `b`, demand state `w'`, and period `t+1`.
The recursion for this timing is

\[
V_T^H(s)=g(s),\qquad
V_t^H(s)=\max_{a\in A(s)}\left\{r_t(s,a)+
\mathbb E_{o|s,a}\left[\max_{d\in D(s,a,o)}\left(-c_D(s,a,o,d)+
\mathbb E_{W'|W_t}V_{t+1}(\Phi(s,a,o,d,W'))\right)\right]\right\}.
\]

Strong SEP uses the same recursion except the outer maximum is over
`A(s)∩G(s)`. This assumes opportunity is realized before development is
chosen and next demand follows the current transition; the selected RQ0 world
definition controls if timing differs.

The immediate operational reward is `r_t(s_t,A_t)`; development cost, if any,
and terminal value are included exactly as specified by the chosen world.
All compared policies have the same feasible sets, physics, information,
reward and horizon. No policy may condition on future realized `W` or `O`.

Define the current reward-greedy correspondence

\[
G(s)=\arg\max_{a\in A(s)} r(s,a),
\]

where `A(s)` is the common feasible assignment set. The joint class `Pi_HLS`
may select any feasible routing and development rule measurable with respect
to `I_t`. Strong SEP is the restriction

\[
\Pi_{SEP}=\{\pi\in\Pi_{HLS}: A_t\in G(s_t)\text{ at every positive-probability
on-policy history}\},
\]

with development optimized after the actual opportunity is observed.
Routing ties remain admissible choices; report the conservative value
`J_SEP,max`, not a tie-breaking realization chosen to depress SEP.
SEP-Omega is not a third policy class with an arbitrary advantage: it denotes
a separated decision organization whose router is supplied sufficient exact
action-conditioned continuation information.

### 3.2 Established propositions and gap conditions

**FACT — policy inclusion (proved in the canonical RQ0 analysis).** Under
the common-world/common-information contract,

\[
\Pi_{SEP}\subseteq\Pi_{HLS},\qquad J_{SEP,max}(s_0)\le J_{HLS}(s_0).
\]

Proof: an HLS policy can imitate every SEP routing and development choice;
SEP imposes the additional routing restriction `R_t∈G(s_t)`. Maximizing the
same objective over a superset cannot reduce the optimum.

**FACT — exact finite reducibility criterion.** If maxima are attained,

\[
J_{HLS}=J_{SEP,max}
\iff \Pi_H^*(s_0)\cap\Pi_{SEP}\ne\varnothing,
\]

and a strict gap occurs iff every HLS-optimal policy has some
positive-probability history on its own support at which it routes outside
`G`. This is already a complete logical criterion, but not yet a compact
primitive-parameter characterization.

**FACT — local opportunity identity.** In the restricted case where action
`r` affects only opportunity probability `p(r)` and conditional continuation
values `W_0,W_1` are action-independent,

\[
Q(r)=R(r)+(1-p(r))W_0+p(r)W_1.
\]

Against immediate-greedy `g` and alternative `b`,

\[
Q(b)-Q(g)=-\Delta R+\Delta p\,D^*,\quad
D^*=W_1-W_0,\;\Delta R=R(g)-R(b),\;\Delta p=p(b)-p(g).
\]

Thus `Delta p D* > Delta R` is a local condition for choosing a
non-greedy route. It is **not** a root-value theorem when that action also
changes resource depletion, future reachability or later opportunity
distribution.

**FACT — both equality and strictness are realized in existing exact HLS
families.** Initial RQ0 campaign cells were reducible; the exact `C(alpha)`
family includes a bounded strict-gap region and regions where an HLS optimum
is SEP-admissible. HLS-G0-C6 has an exact positive finite-instance gap at
`eta=.75` against BEST_STATIC under both stationary and changing demand
(`.159375` and `.12456` respectively), explained by opportunity-gated A1
development followed by routing flexibility. At low `eta` the policies have
equal value. C6's explicit A1 transition is not MIS-v2; the analysis is
closed and is not being extended here. See the [RQ0 boundaries](../theory/rq0_routing_integration_boundaries.md),
[RQ0 campaign](../experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md),
and [C6 closure](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md).

**FACT — local inversion can fail to imply a root gap.** The RQ0 exact
`eta=.5` diagnostic has a physically reachable local non-greedy Bellman
inversion that is not on any HLS-optimal root policy support. It is a direct
counterexample to using a statewise inversion alone as a strict-gap test.

### 3.3 Small unresolved mathematical question

The smallest genuine unresolved question is:

> Under what additional restrictions on opportunity coupling, resource
> depletion, and future-demand transitions does a reachable local inequality
> `Delta p D* > Delta R` imply that **every** root-optimal HLS policy is
> non-SEP, rather than merely making one local deviation attractive?

This is a theorem/counterexample question, not a broad sweep. A plausible
**CONJECTURE** is that no criterion based only on the local triple
`(Delta R,Delta p,D*)` suffices in general once the action changes future
feasibility or the continuation state. It would be refuted by a general
root-gap characterization from those local quantities under the stated
class. The finite reachable-inversion example already shows that reachability
alone is not enough; optimal support and comparison with all SEP-optimal tie
selections matter.

**Conditions for equality/gap to disappear:** equality follows whenever at
least one HLS optimum is SEP-admissible. It also follows in a given world if
the Bellman-optimal routing choices can be selected from `G(s)` on an
optimal policy's support. In the tested no-learning/no-value controls,
continuation does not reward a non-greedy route. Conversely, SEP-Omega can
match HLS when it receives enough exact continuation information to make
the same Bellman choice. These are sufficient facts in the declared settings,
not a universal classification of dynamic organizations.

**Experimental implication:** the exact RQ0 solver can evaluate the
policy-class criterion, support, and SEP tie interval in its finite
full-information worlds. It cannot be presumed to cover N×K MIS-v2 or
partial observation. Existing G2/G3-H/RQ0 calculations already answer the
existence/null questions; experimental design should target the unresolved
lifting from local incentives to root-optimal policy classes, not re-run C6.

## 4. Investigation 2 — knowledge transfer × MIS-v2 × changing demand

### 4.1 Actual state and transitions

**FACT — competence is a latent acquired capability.** The N×K matrix
`C_t=(c_{ik,t})∈[0,1]^{N×K}` is not experience, output, or success. MIS-v2
uses productive exposure `x_{ik,t}≥0`; with `lambda_{ik}=-log(1-eta_{ik})`,

\[
M_{ik}(c,x)=1-(1-c)e^{-\lambda_{ik}x}.
\]

No exposure is identity; there is no cross-agent/cross-skill effect in MIS-v2.
The standard N×K runner calculates current-period output from pre-transition
competence, then applies MIS-v2 after production.

**Experience semantics:** in MIS-v2, cumulative exposure is the input to the
competence law rather than a separate Markov state needed to compute future
competence; repeated exposures compose through the exponential law. The
legacy dynamic `ExpertState` separately records cumulative effort as
`experience += x` for diagnostics, but N×K `OrganizationStateNK` stores true
and estimated competence, not an additional experience matrix. In the
separate Nembhard Direct branch, accumulated `D_{ik}` is explicitly the state
variable entering productivity. These meanings are not interchangeable.

**FACT — directed teaching/transfer is a different transition on the same
competence state.** A teaching event `tau=(i,j,k,u)` names instructor `i`,
learner `j`, skill `k`, effort `u>0`. With environment efficacy
`T_{ijk}∈[0,1]` and transfer rate `r∈(0,1]`,

\[
H_{ijk}(c,u)=\min\{1,c+r u T_{ijk}(1-c)\}
\]

updates only learner cell `(j,k)`. The implemented law does **not** multiply
by instructor competence; teacher-specific effect resides in `T_{ijk}`.
The executed order is production → MIS-v2 → teaching. The process is
action-dependent, directed and saturating; no forgetting or cross-skill
spillover is included by this transition.

**FACT — resource accounting.** Productive effort consumes `sum_{ik}x_{ik}`.
A lesson charges `2u` collectively and `u` to each of teacher and learner;
thus, for common budget `B` and individual caps `B_i`,

\[
\sum_{ik}x_{ik}+2u\le B,\quad
\sum_kx_{ik}+u\,1\{i\text{ is teacher or learner}\}\le B_i,
\]

with one `u` charge for each of the two distinct participants. These
constraints are validated in `validate_joint_action_resources_nk`. The
competence state does not currently make feasibility depend on competence;
effort caps and the joint action catalog do.

**FACT — demand is exogenous.** N×K reuses C5 stationary, indexed
nonstationary and first-order Markov task-demand processes. The generated
problem trajectory and latent regime labels are environment-side metadata;
the decision view receives the current problem, not future realizations.

**Information.** The environment holds true competence `C_t` and true
efficacy tensor `T`. Policies receive an `NKDecisionView` including current
period/remaining periods, current problem requirements, estimated competence
and feasible actions. P2 receives `OrganizationMemoryNK`, a relation-indexed
running mean updated from a formative efficacy signal. The private efficacy
tensor itself is excluded from the view. This is not a posterior over all
unknown dynamics, and P2 is a relation-selection heuristic, not a
long-horizon optimizer.

In the legacy zero-noise policy execution, observed teaching gain is
normalized by `r u (1-c^+_{jk})`; when `c^+_{jk}<1` and the observation is
noiseless, the resulting signal equals `T_{ijk}` exactly. Thus the tensor is
not passed directly, but that observation channel fully reveals the selected
relation's efficacy in this idealized case. With noisy feedback or an
estimated competence denominator in the information-aware execution, the
signal need not equal truth. “Imperfect efficacy information” must therefore
name the execution path and its noise/denominator semantics; it does not
follow merely from the tensor's absence from `NKDecisionView`.

### 4.2 Exact state-level interaction

Consider one competence cell `c` that receives MIS exposure `x` and is then
the learner cell of a lesson. Set

\[
a=e^{-\lambda x},\qquad h=r u T_{ijk},\qquad 0\le a,h\le1.
\]

Then the actual sequential combined transition is

\[
H(M(c,x),u)=1-(1-c)a(1-h).
\]

The competence increments relative to the initial `c` are:

\[
\Delta_M=(1-c)(1-a),\quad
\Delta_T=(1-c)h,\quad
\Delta_{MT}=(1-c)[1-a(1-h)].
\]

Therefore the factorial transition interaction is the exact identity

\[
\boxed{\Delta_{MT}-\Delta_M-\Delta_T
=-(1-c)(1-a)h=-\Delta_M h\le0.}
\]

Equality occurs when either mechanism produces no increment in that cell;
otherwise their raw same-cell gains are subadditive because both close the
same remaining gap. This is a **proved algebraic property of the current
equations**, not a measured organizational effect. If MIS exposure and
teaching affect different cells, this same-cell overlap term is zero; total
system value can still interact through task allocation and scarce capacity.

### 4.3 Factorial estimand and comparability controls

For a specified scalar outcome `J` and four transition settings, define

\[
J_{00}:\text{neither transition},\quad
J_{10}:\text{MIS only},\quad
J_{01}:\text{transfer only},\quad
J_{11}:\text{both},
\]

and interaction

\[
I_J=(J_{11}-J_{10})-(J_{01}-J_{00})
=J_{11}-J_{10}-J_{01}+J_{00}.
\]

The sign is outcome- and policy-specific: positive is complementarity for
that `J`, negative is redundancy/interference for that `J`, and zero is no
factorial interaction at that scale. Do not combine production, effort and
competence into one unapproved utility. Report `I_J` separately for
cumulative production/CES, functional-success fraction, deficit, final and
per-period competence, plus resource consumption.

**Critical control.** A naive ablation that removes teaching actions when
transfer is “off” changes the feasible action set and frees resources; it
does not isolate transfer physics. Likewise, removing productive actions
when MIS is off changes production and effort. Use two complementary
estimands:

1. **Mechanism/transition factorial:** replay the same predeclared feasible
   joint-action sequence `(X_t,tau_t)` in all four cells. Keep the action
   catalog, effort charges, `u`, `B`, and individual limits identical. Disable
   MIS by the existing `individual_learning=False` switch. Disable transfer
   by setting the environment efficacy tensor to zero while retaining the
   same teaching events and charging the same `2u`/individual effort. This
   isolates transition effects conditional on the chosen action path; it does
   not estimate the value of a policy that adapts its actions.
2. **Closed-loop policy factorial:** execute the same policy code and
   parameters within each cell from the same initial state and paired
   exogenous task/noise streams. Keep teaching enabled and the same feasible
   joint action catalog in every cell; in transfer-off cells use zero
   efficacy, not removal of teaching choices. Keep policies' information
   contract fixed and disclose that their chosen action paths may diverge
   because feedback/state differ. This estimates the combined mechanism plus
   policy-response effect, not a pure transition interaction.

The explicit-action execution path supports per-period `JointActionNK`; the
runner has MIS enable/disable and validates the same resource calculation.
Whether every desired paired noise stream is indexed independently of action
choices must be verified for the chosen runner. If not, the transition
factorial can still use deterministic demand/noise or precomputed compatible
observations, but no unsupported common-random-number claim should be made.

### 4.4 Policies, hypotheses and findings

**Closed-loop comparator set:** P0 production-only/no teaching; P1 fixed
teacher–learner–skill relation with production selected under that relation;
P2 adaptive relation choice from observed efficacy memory. P1 is not
automatically a strong static baseline: for a defensible fixed comparator,
select a relation from the predeclared feasible relation class using only
training/selection instances, or enumerate it under the known scenario law,
then evaluate it on held-out common trajectories. Include no-teaching P0 as a
separate baseline. P2 must not receive the true efficacy tensor. Keep
resource caps equal, and report actual productive versus teaching use.

**Testable hypotheses (not findings):**

* **H2a (state overlap):** when MIS and transfer target the same unsaturated
  cell, their total competence increment is below the sum of the isolated
  increments, by the exact overlap term above.
* **H2b (demand alignment):** collective transfer value depends on whether
  the learner's taught skill is demanded later and whether it changes the
  feasible/efficient allocation; it can be zero despite competence gain.
* **H2c (resource competition):** transfer may reduce current production
  because teaching consumes capacity; future value may or may not compensate.
* **H2d (policy adaptation):** P2's relation memory can select a different
  feasible relation after feedback, but this does not imply greater
  cumulative performance than P1 or P0.

**Meaningful signs:** a positive `I_J` means complementarity for the declared
outcome/scale under the specified fixed actions or closed-loop policy; a
negative value means subadditive/antagonistic performance interaction, which
may arise from same-cell saturation, resource opportunity cost, or demand
mismatch; zero may mean no exposure, zero efficacy, already-mastered cells,
or no effect on relevant assignments. These causes must be distinguished in
traces.

**Limit on “interference”:** the existing transition has nonnegative bounded
efficacy and monotone competence. It cannot represent direct teaching harm,
negative transfer, forgetting, or interference with a different skill cell.
An outcome-level negative interaction is testable; a claim of harmful
competence transfer is not.

### 4.5 Existing results, reusable components and missing evidence

**FACT:** G2 establishes individual learning-by-doing null/positive controls;
G3/G3-H derive allocation-sensitive development value; Campaign 2 addresses
prospective information/development contrasts in a different frozen model.
The 17 October validation executes P2 under S4 and records MIS/teaching
increments, beliefs, efficacy memory and resources; the declared S4 run has
all functional requirements unsatisfied. It verifies execution and tracing,
not that adaptive transfer helps performance.

Reusable modules include `hls_lab_nk_learning.py`, `hls_lab_nk_teaching.py`,
`hls_lab_nk_environment.py`, `hls_lab_nk_policies.py`,
`hls_lab_nk_execution.py`, C5 demand generators and existing N×K tests. The
explicit action path and current transitions permit the matched factorial
mechanism ablation without a new learning law. Missing for strong scientific
claims: a predeclared non-saturated instance/control set; documented paired
trajectory generation for the selected execution path; and a controlled
closed-loop evaluation using a train-selected strong P1 relation. No code or
experiment is proposed in this analysis.

## 5. Investigation 3 — partial information × endogenous development

### 5.1 Hidden-state model and information

Use N×K competence, not Nembhard productivity. Let latent state
`Z_t=(C_t,W_t,B_t)`, where competence `C_t` is not directly observed by a
partial-information policy, current task `W_t` and budgets `B_t` are
observable as declared. A feasible productive action is `X_t`. The physical
transition is

\[
C_{t+1}=M(C_t,X_t)\quad\text{(MIS-v2 enabled)},
\qquad W_{t+1}\sim P_W(\cdot|W_t),
\]

and the existing competence observation is an individual reading based on
productive exposure and actual competence, with declared noise. Abstractly,

\[
Y_{ik,t}=x_{ik,t}c_{ik,t}+\epsilon_{ik,t},\qquad
\epsilon\sim O(0,\sigma),
\]

as implemented for the indexed observation path. Policy history is
`I_t=(W_{0:t}, X_{0:t-1},Y_{0:t-1},B_t)` plus any maintained posterior or
estimate. The evaluator may retain `C_t` for error metrics but cannot pass it
to the policy. A belief `b_t(c)=P(C_t=c|I_t)` updates by the observation
likelihood and is pushed through MIS-v2 when the policy knows the transition
parameter and action. In the current estimator implementation this update is
cellwise and grid-based; it is not a general learned transition model.

The policy chooses from the same action set and resource constraints in all
information arms. State response means choosing from current visible inputs;
belief updating changes the estimate from new feedback; exploration is a
decision to incur an action for information rather than immediate value;
development changes true competence through MIS-v2; planning values future
rewards. These are separate mechanisms.

### 5.2 What is supported and what is not

**FACT:** `SkillPosterior`, `initialize_competence_estimator`,
`update_skill_posterior` and `predict_skill_posterior_after_mis` support
competence estimation and deterministic posterior prediction through
declared MIS-v2. N×K wraps this behavior. `PARTIAL_STATIC` holds an initial
estimate; `PARTIAL_LEARNING` updates from individual production observations.
The dynamic pilot compared these with ORACLE information on paired
trajectories. In that bounded setup, updating a deliberately biased estimate
helped the tested heterogeneous teams; the contrast does not establish a
general value-of-information theorem.

**FACT — planning incompatibility:** `DiscoverBeliefPolicy` invokes the
existing DISCOVER belief solver over hidden reward/problem type and a fixed
capability view. `run_belief_sequence` applies actual MIS-v2 between
decisions, but its docstring and execution show that the Bellman recursion
does not forecast this competence development. Thus it is not an exact
solution to the partially observed MIS-v2 finite-horizon problem. Do not
describe it as such.

P2's “unseen relation first” rule probes a teaching relation; its
running-mean memory changes later relation choice. This is distinct from
`SkillPosterior` updating competence estimates, and both are distinct from
development of true competence. P0 is state-responsive to its current view
but has no efficacy-memory relation probing. These channels must not be
collapsed into one “learning” factor.

**FACT — Nembhard is a separate model.** Nembhard Direct state includes
experience `D_{ik}` and productivity parameters `(k_{ik},p_{ik},r_{ik})`,
with `P_{ik}(D)=k_{ik}(D+p_{ik})/(D+p_{ik}+r_{ik})`; ADAPTIVE estimates
productivity from selected feedback. MIS-v2 instead evolves normalized
competence `c_{ik}` from exposure with `eta/lambda`. There is no identity
mapping between these state equations, feedback likelihoods or units. Any
comparison must choose one physics and must not combine the estimators by
renaming variables.

### 5.3 Estimands, controls and mathematical result

A useful 2×2 diagnostic crosses information update `U∈{frozen, updated}` and
development `L∈{off,on}`. Let `J_{u,l}` be a declared outcome under the same
policy decision rule, feasible action set, demand path and observation
protocol. Then information contrasts at each development level are
`J_updated,l - J_frozen,l`; development contrasts at each information regime
are `J_u,on - J_u,off`; interaction is

\[
I_{UL}=J_{updated,on}-J_{frozen,on}-J_{updated,off}+J_{frozen,off}.
\]

Report these for cumulative output and functional metrics, and separately
report estimator error, competence paths, effort, and compute. `ORACLE` is a
privileged upper-bound diagnostic, not the matched causal contrast for value
of updating. Pair exogenous demand/noise streams where the implementation
actually supports action-independent indexed randomness; the same scalar seed
alone does not guarantee identical realized observations if draw consumption
depends on actions.

There are two distinct estimands:

1. **Fixed-action information/development diagnostic:** replay identical
   feasible actions under all four cells. This isolates the state transition
   and estimator update given the action trace, but does not measure policy
   adaptation.
2. **Closed-loop policy value:** rerun the same policy implementation under
   each cell. Actions may diverge from their own feedback/state histories; the
   contrast includes this endogenous response and development path. It does
   not isolate a direct effect of information from mediated action changes.

Do not mix the two estimates. The current G0 exact solver is not a partial
observation N×K reference. Before claiming optimality or a strict value of
information, either define an exact belief-state problem on a suitably small
state/action set, or limit the estimand to the named heuristic-policy
contrast.

**PROVED generic statement:** if two policy classes face identical physics,
actions, rewards and costs, and every policy using a coarser information
history is also admissible to a richer-information class (it may ignore the
extra signal), then the optimal richer-information value is weakly greater by
policy-class inclusion. For any coarse policy `pi`, define rich policy `pi'`
to apply `pi` to the projection of the rich history onto the coarse history.
The induced action/state/reward law is then identical, so `J_pi'=J_pi`;
taking suprema over the nested classes proves the inequality. This does not
prove that `PARTIAL_LEARNING` beats
`PARTIAL_STATIC`: those are particular update/decision rules, not the
optimized nested policy classes. Nor does it prove that competence
development increases value under partial information.

**CONJECTURE:** the value of competence estimation will depend on whether
the observation history changes allocation-relevant rankings before demand
changes again; if signals are weak/noisy or state development is rapid,
updating may lag or produce harmful reallocation. It is falsifiable by
paired conditions but not established by the four-seed dynamic pilot.

## 6. Cross-investigation comparison

| Investigation | Established | Candidate proposition / conjecture | Counterexample or null | Measurable interaction | Main limitation / reusable support |
|---|---|---|---|---|---|
| **1. Joint vs strong SEP** | Policy inclusion, exact finite reducibility criterion, local opportunity identity; exact reducible and strict-gap examples. | **Open conjecture:** local incentive quantities alone do not determine root strictness when they also alter resource/reachability; characterize added conditions. | No-learning/reducible RQ0 cases; local inversion outside optimal support; SEP-Omega equality. | `Phi=J_HLS-J_SEP,max`, SEP tie interval, HLS-optimal support, routing greediness along support. | G0/RQ0 exact solver and tests; full information/discrete worlds only. C6 closed. |
| **2. Transfer × MIS × demand** | Sequential same-state transitions; exact negative same-cell overlap term; joint resource charge. | The sign of system-output `I_J` depends on demand alignment and resource opportunity cost, not the sign of the local competence interaction alone. | Zero exposure/zero efficacy/mastery; a lesson to a skill never demanded; same-cell saturation yields subadditive gain. | Factorial `I_J` for competency, production, success/deficit and resources, with fixed-action and closed-loop estimands separated. | Existing N×K transitions/P0/P1/P2/C5/runner; validate paired randomness, outcome headroom, baseline selection. No direct harmful transfer/forgetting. |
| **3. Partial info × development** | Cellwise posterior observation/update and MIS prediction; pilot estimate-update contrast; policy inclusion for nested information classes. | Estimation's realized value depends on information relevance and timing relative to demand/development; no guarantee for heuristic updates. | Identical action rankings under all estimates; noiseless/fully observed ORACLE; MIS disabled isolates static hidden state. | 2×2 update × development contrasts and interactions under fixed-action and closed-loop policy regimes. | Dynamic N×K estimator and runner; no exact belief-state optimizer for competence-evolving problem. DISCOVER belief solver does not plan MIS transitions. Nembhard is incompatible physics. |

## 7. Experimental-design readiness assessment

| Criterion | 1. Joint vs strong SEP | 2. Transfer × MIS-v2 | 3. Partial information × development |
|---|---|---|---|
| Mathematical clarity | High: canonical classes and finite exact value available | Medium-high: equations/resource order explicit; interaction estimand needs two layers | Medium: observation/posterior exist, but exact belief-state objective and policy class must be fixed |
| Scientific relevance | High | **High; directly tests knowledge-transfer interaction central to HLS** | High |
| Existing evidence | High for exact boundary cases | Medium: mechanisms and trace path validated; interaction result absent | Medium: descriptive pilot and Campaign 2 address adjacent but nonidentical estimands |
| Feasibility with current components | High for small full-information G0 | **High for factorial transition checks; medium for fair closed-loop comparison** | Medium-low for optimality claims; medium for a bounded heuristic contrast |
| Ability to characterize interaction | High if support/reachability is analyzed | **High if same action path and closed-loop policy effects are separated** | Medium; risk of confounding signal, planning and development |

**Best prepared for experimental design: Investigation 2.** The critical
condition is to write a two-part design: (a) a common-action factorial to
identify the direct transition interaction and (b) a separate closed-loop
policy comparison to measure organizational consequences. The four
mechanism cells must retain the same feasible joint action catalog and
resource charges; zero transfer efficacy must not remove teaching actions.
This recommendation is about readiness, not expected benefit. No execution
is authorized.

**Best prepared for exact theorem work: Investigation 1.** Its definitions
and finite solver are strongest, but the foundational strict-gap existence
claim is already settled; worthwhile work must provide the unresolved
structural characterization.

**Least ready for an optimal-policy experiment: Investigation 3.** The
current partial-estimation execution path is useful, but its available
prospective optimizer does not include MIS-v2 continuation and the G0 exact
solver cannot be carried over by assumption.

## 8. Sources and implementation references

* [RQ0 policy classes, exact criteria and local identity](../theory/rq0_routing_integration_boundaries.md)
* [G2 dynamic ground truth](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md)
* [G3/G3-H analytical ground truth](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md)
* [MIS-v2 model](../theory/HLS_CAPABILITY_DEVELOPMENT.md)
* [N×K learning](../../src/hls/hls_lab_nk_learning.py), [teaching and resource feasibility](../../src/hls/hls_lab_nk_teaching.py), [policy/memory contracts](../../src/hls/hls_lab_nk_policies.py), [environment](../../src/hls/hls_lab_nk_environment.py), [execution](../../src/hls/hls_lab_nk_execution.py), and [competence estimator](../../src/hls/hls_lab_nk_estimation.py)
* [Dynamic partial-information execution](../../src/hls/hls_lab_dynamic.py)
* [Integrated adaptive-capability validation](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md)
* [Dynamic lab characterization](../experiments/HLS_DYNAMIC_LAB_CHARACTERIZATION.md)
* [Campaign 2 results](../experiments/CAMPAIGN_2_RESULTS.md)
* [HLS-G0-C6 closure and claim boundaries](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md)
* [Knowledge-transfer reuse audit](../experiments/HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md)

No new literature claims are introduced in this analysis.
