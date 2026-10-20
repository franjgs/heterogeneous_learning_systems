# HLS prioritized investigations — 21 October 2026

**Purpose:** select a bounded set of research questions from the evidence
consolidated in [HLS scientific evidence synthesis](HLS_SCIENTIFIC_EVIDENCE_SYNTHESIS_2026-10-20.md).
This is a prioritization and mathematical handover, not a replacement roadmap,
new literature selection, implementation authorization, or campaign
authorization. The recovered plan and historical status remain in the
[original plan](../project/HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md) and
[activity audit](../project/HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md).

## 1. Decision summary

Three investigations are prioritized. They test interactions that matter to
HLS while reusing different parts of its scientific base. The ordering favors
mathematical tractability and reusable evidence, not a prediction about which
policy will perform best.

| Rank | Investigation | Interaction | Existing basis | Main gap |
|---|---|---|---|---|
| **1** | Boundary of joint allocation–development value against strong SEP | Heterogeneous capability × learning opportunity × resource constraints × future task value | RQ0 exact policy definitions/solver, G2/G3-H controls, RQ0 `C(alpha)` family | General structural conditions beyond the already solved finite families; support/reachability and constrained resource effects |
| **2** | Directed knowledge transfer interacting with individual MIS learning under changing demand | Heterogeneous agent/skill states × individual learning × transfer × teaching/production resource competition × task change | N×K `JointActionNK`, MIS-v2, teaching transition, P0/P1/P2, C5 trajectories and S4 traces | Whether transfer and individual learning are complementary, redundant, or interfering in collective outcomes under fair resource accounting; P2's limits under a controlled discriminating comparison |
| **3** | Partial information and competence adaptation with endogenous development | Hidden heterogeneous competence × observations/estimation × changing demand × action-dependent development | N×K competence posterior, dynamic runner, Campaign 2 and paired pilot evidence | Which information/estimation conditions preserve or remove an integration/adaptation value gap under a common information set; an exact partial-information reference is not established |

| Criterion | #1 Joint allocation / development boundary | #2 Transfer × MIS-v2 | #3 Partial information × development |
|---|---|---|---|
| Scientific relevance | High | High | High |
| Interaction characterization | High | High | High |
| Comparator strength now | High: exact policy classes | Medium-high: P0/P1/P2 plus MIS ablations | Medium: oracle/static/update exist, but estimands need tightening |
| Existing component reuse | High | High | Medium-high |
| Mathematical tractability | High in finite exact worlds | Medium; transition is explicit, interaction accounting needed | Medium-low; belief state/action-dependent transition |
| Reproducibility readiness | High for existing RQ0 families | Medium-high for controlled small N×K instances | Medium-low until exact information-matched reference is defined |

The second investigation makes knowledge transfer a priority because it is a
central HLS mechanism and the N×K implementation already has a concrete
directed teaching action and adaptive relation memory. It is not included to
meet a quota. The evidence supports bounded engineering readiness, not a
claim that teaching improves performance.

## 2. Investigation 1 — structural boundary against strong SEP

### Research question

For which finite common-world structures is the optimal joint allocation and
development policy irreducible to canonical strong SEP, and which features of
heterogeneity, opportunity, remaining development resources, and future task
demand determine that boundary?

This is narrower than asking whether `Pi_HLS` can outperform `Pi_SEP`: the
policy-class inclusion and exact finite reducibility criterion are already
proved. The target is a useful structural characterization of when an
HLS-optimal policy must route outside the immediate-reward greedy set on its
own positive-probability support.

### Mathematical handover for 22 October

Use the RQ0 notation. Let

* `S_t=(X_t,B_t)` denote capability and remaining development resources;
* `W_t` be the current task/demand state;
* `A_t` be operational assignment/routing;
* `O_t` be the opportunity observed **after** routing;
* `D_t` be feasible development selected after observing `O_t`;
* `R(S_t,W_t,A_t)` be common operational reward, with development costs
  and any terminal term retained exactly as defined by the chosen RQ0 world;
* `S_{t+1}=F(S_t,A_t,O_t,D_t)` with exogenous demand transition
  `P(W_{t+1}|W_t)`.

The HLS objective is the finite-horizon expected cumulative reward under
policies measurable with respect to the authorized history and no future
realized demand. The feasible set `A(S_t,W_t)` includes the same operational
and development resource restrictions for all policies. Define
`G(S_t,W_t)=argmax_a R(S_t,W_t,a)`. Strong SEP restricts routing to `G` and
optimizes development after actual opportunity; ties remain a set and its
upper value `J_SEP,max` is the conservative comparison. Compare
`Phi=J_HLS-J_SEP,max`, not an arbitrary SEP tie resolution.

**Baselines:** exact HLS; exact strong SEP including its upper tie value;
SEP-Omega only as the continuation-information/reducibility boundary; and
null controls with zero learning, no decision-relevant opportunity, or
assignment-independent opportunity. Do not reopen HLS-G0-C6: its finite
result is closed and preserved. Use existing RQ0 families and theory unless
the analysis identifies a specifically approved missing case.

**October 22 must establish:** (i) the exact Bellman recursion under
`routing → opportunity observation → development`; (ii) what existing RQ0
results already imply for each resource/opportunity case; (iii) whether a
local inversion condition such as `Delta p · D* > Delta R` can be lifted to
a root-value condition when actions also affect reachability and resource
depletion; and (iv) a minimal sufficient structural statement or a precise
counterexample to such a statement. A local routing-as-teaching inversion is
not by itself a global strict gap.

**Existing positive/null evidence:** RQ0 proves `Pi_SEP ⊂ Pi_HLS` and the
finite exact equivalence: equality iff an HLS-optimal policy is SEP-admissible.
The exact `C(alpha)` family has a bounded strict-gap region and a reducibility
region. Initial preregistered cells were reducible. G2/G3-H show development
value depends on future assignment opportunity. C6 quantified one closed
finite case but added no new theorem.

**Open issue:** a compact condition based on heterogeneity, opportunity
contrast, capability-development value, budget and future demand that
predicts global irreducibility across more than the existing constructed
families. Any claim must account for optimal-policy support, not only
statewise action rankings.

**Required laboratory capability:** already adequate for the finite exact,
full-information, discrete G0/RQ0 scope (`src/hls/synthetic/exact.py`,
`src/hls/synthetic/e1_minimum.py` and associated tests). It is not a generic
N×K solver and does not cover partial observation. No new campaign or C6
expansion follows from this prioritization.

**Feasible test, if separately authorized:** exact evaluation of the existing
frozen RQ0 `C(alpha)` values and null controls, reporting the full
`[J_SEP,min,J_SEP,max]` interval and HLS-optimal support. A narrowly chosen
one-factor exact counterexample could test a proposed boundary condition; it
must not become an unbounded parameter search or a continuation of closed C6.

## 3. Investigation 2 — transfer × individual learning × changing demand

### Research question

Under a fixed N×K world with heterogeneous initial competence and directed
teacher–learner–skill efficacy, when does transfer complement, duplicate, or
interfere with individual MIS-v2 learning as task requirements change and
productive effort competes with teaching effort for the same resource
capacity?

This question concerns interaction effects, not the isolated existence of
learning or teaching. It asks whether observed gains in a learner's skill
remain useful under the later task mix, and whether the opportunity cost of
teaching is offset by future collective production. No policy is presumed to
win.

### Mathematical handover for 22 October

For N agents and K skills, let `C_t∈[0,1]^(N×K)` be true competence,
`W_t` the observed current task requirement, `B_t` remaining effort capacity,
and `M_t` the policy-visible relation-efficacy memory. At a period choose
joint action `(X_t, tau_t)`, where `X_t` is divisible productive effort and
`tau_t` is either no lesson or one directed relation `(i,j,k,u)`.
Feasibility must be the existing joint constraint: total productive effort
plus teaching resource, with relevant individual limits, does not exceed
capacity. The implemented order is production from pre-transition competence,
MIS-v2 transition on exposed productive effort, then directed transfer:

`C_t^+ = MIS(C_t,X_t)` and
`C_{t+1}=Teaching(C_t^+,tau_t,T,r)` where the existing transition is
`c'_{jk}=min(1,c_{jk}+r u T_{ijk}(1-c_{jk}))` for the selected learner/skill.
Other competence coordinates remain unchanged by that lesson. Demand follows
an existing C5 stationary, scheduled nonstationary, or Markov process. The
objective is cumulative functional/production performance over the horizon;
effort, teaching use, success, deficit, competence and memory are reported
separately. Do not subtract effort from production unless a scientifically
approved common utility explicitly defines that conversion.

The environment knows the true efficacy tensor `T`; a policy sees only its
declared decision view, estimated competence, current requirement, feasible
actions and its own memory. It must not receive `T` unless the arm is
explicitly a full-information reference. Exogenous demand and policy
randomness must be paired/separated as the runner permits.

**Baselines already available:** P0 production-only/no lesson; P1 configured
fixed relation; P2 adaptive relation choice using relation-specific
formative-efficacy memory; MIS-v2 OFF/ON as a controlled individual-learning
factor. Same initial state, demand sequence, feasible-action catalog and
total resource cap are required. This is not a comparison against an
intentionally weak “no adaptation” arm: P1's fixed relation and the full
catalog must be chosen before outcomes and reported with resource use.

**October 22 must establish:** (i) the exact transition and observation
semantics already implemented, including whether the formative signal
identifies the true relation effect under noiseless/noisy feedback; (ii) the
within-period order and combined budget constraints; (iii) how to separate
transfer's contribution from MIS-v2's contribution and their interaction in
a factorial contrast without changing either transition; and (iv) whether
the existing P0/P1/P2 policy information is comparable enough for the
planned estimand. The existing S4 path alone is not adequate: it verifies
execution but its requirements all remain unsatisfied and it does not isolate
the interaction.

**Existing evidence:** N×K code provides `JointActionNK`,
`TeachingEfficacyNK`, `teaching_transition_nk`, joint resource validation,
`P1FixedTeachingNK`, `P2AdaptiveTeachingNK`, `OrganizationMemoryNK`, and
an execution trace containing MIS and teaching increments. The bounded
capability validation exercises P2 under an existing four-period scenario.
Thus this is not a proposal to invent a teaching mechanism. What is missing
is a controlled, discriminating result about transfer × individual learning
× task change under competitive baselines and clear resource accounting.

**Open issue:** whether transfer's marginal value is preserved, amplified,
made redundant, or reversed by individual exposure learning and by later
changes in which skills are demanded, and whether the relation-memory policy
responds usefully under those conditions. A negative interaction or no gain
would also be informative about the model's transfer law and demand geometry.

**Required laboratory capability:** the core transitions and policies are
implemented. Reuse `src/hls/hls_lab_nk_teaching.py`,
`src/hls/hls_lab_nk_learning.py`, `src/hls/hls_lab_nk_policies.py`,
`src/hls/hls_lab_nk_environment.py` and
`src/hls/hls_lab_nk_execution.py`, plus C5 generators and existing tests.
Before any execution, confirm current tests cover the exact cross-factor
contract, matched exogenous realization, trace separation and non-saturated
outcomes. Do not assume Campaign 2 answers this question: it studies
prospective decision restrictions/counterfactuals in its frozen model, not
this P0/P1/P2 transfer comparison.

**Feasible test, if separately authorized:** a small paired `2 × 3 × 2`
factorial: MIS-v2 off/on × no teaching/P1/P2 × stationary/one scheduled task
mix change, with identical initial teams, task realization and total effort
caps within each pair. Use the existing observation/noise contract and only
enough repetitions to report paired outcomes descriptively; no superiority
or significance criterion is implied. The primary contrast is the
transfer-by-MIS interaction in functional output/deficit and competence
trajectories, with teaching effort and production effort reported separately.
If the exact P2 policy uses a different feasible-action set or information
than P1, that mismatch must be resolved in the estimand, not hidden by
weighting metrics.

## 4. Investigation 3 — partial information × development × adaptation

### Research question

When competence is only partially observed and productive actions change the
true competence state, under what information conditions can a
state-responsive or prospective policy improve finite-horizon decisions
relative to a policy using the same observation history but a non-updating
competence estimate, especially when task demand changes?

This extends existing evidence about updating biased competence estimates
without conflating hidden-state estimation, online policy learning, and
environmental nonstationarity. It is not a claim that posterior updating
necessarily improves realized output.

### Mathematical handover for 22 October

Let true state be `Z_t=(C_t,W_t,B_t)`, with `C_t` hidden, current demand
`W_t` visible or partially visible as declared, and `B_t` resources. Action
`A_t` is a feasible productive allocation; MIS-v2 gives
`C_{t+1}=M(C_t,A_t)`. The environment evolves `W_{t+1}~P(·|W_t)` and produces
an observation `Y_t~O(·|C_t,A_t)` under the existing observation model. The
policy's information is history `I_t=(W_{0:t},A_{0:t-1},Y_{0:t-1},B_t)` or its
documented posterior/estimate summary; it never includes the evaluator's
true hidden `C_t` except in a separately labeled oracle arm. Objective is
expected cumulative production and separately reported functional success,
deficit, effort, estimation error and any compute cost.

**Existing comparator evidence:** ORACLE versus PARTIAL estimates and
PARTIAL_STATIC versus PARTIAL_LEARNING were exercised in the dynamic pilot;
updating helped tested heterogeneous teams with a deliberately biased prior
but not similar teams. Campaign 2 separately studies information and
prospective restrictions under its frozen information model. Existing
`SkillPosterior`, initialization/update functions and N×K execution support
the observation/update path.

**October 22 must establish:** (i) what it means for two policies to share an
information set when one updates a posterior and another freezes a prior;
(ii) the correct belief-state transition under action-dependent MIS-v2 and
stochastic observations; (iii) a fair policy-class comparator that does not
give an oracle future demand or hidden competence; (iv) whether available
belief/planning code actually optimizes over the competence belief or only
over problem-type beliefs; and (v) a minimal null/positive control pair. The
first result may be a mathematical comparison/identifiability statement,
not an algorithm-performance claim.

**Open issue:** separate the value of better state estimation from value of
planning, model knowledge, and current-state response, while demand and
capability both evolve. Existing pilot arms bundled some of these factors;
Campaign 2's state-conditioned counterfactuals are not whole-policy value
estimates.

**Required laboratory capability:** N×K supports the competence observation
and posterior update, C5 demand processes, paired traces, and current
state-responsive policies. A small exact belief-state reference or a
predeclared matched policy contrast may be needed; the existing exact G0
solver cannot be assumed to solve the partially observed N×K model. This
scope should not be implemented until the October 22 mathematical review
confirms an estimand that existing policies can answer without semantic
changes.

**Feasible test, if separately authorized:** first use a small paired
stationary/scheduled-shift replay with heterogeneous and similar initial
teams, comparing the same greedy rule with frozen versus updated competence
estimates, and an explicitly labeled ORACLE bound. A belief-aware planning
arm is admissible only after verifying that its posterior is over competence
and that its objective/information match the claim. Existing pilot evidence
can serve as the diagnostic reference; it must not be redescribed as a
confirmatory result.

## 5. Why these three, and not a broader list

The selection balances:

* **Scientific relevance:** all concern how heterogeneous capabilities are
  organized or developed under resource and information constraints.
* **Interaction value:** #1 isolates organization × development value; #2
  couples transfer × individual learning × demand/resource use; #3 couples
  hidden capability × estimation × endogenous change.
* **Comparator strength:** #1 has exact HLS/strong-SEP/SEP-Omega; #2 has
  production-only, fixed-relation, adaptive-relation, and MIS ablations; #3
  has oracle and static/update arms but needs more careful information
  matching.
* **Reuse and tractability:** #1 is mathematically mature and exact in small
  worlds; #2 is closest to existing N×K execution and teaching interfaces;
  #3 is relevant but has the largest exact-reference gap.

Not prioritized as new work: further G1 static cases, extension of G3, another
E2.x separable allocation study, Nembhard E1 replay/expansion, HLS-G0-C6
expansion (closed), or additional contextual-router mechanism work. Existing
nulls and exact results should be reused as controls. Chen/MixLLM/System-1.x
selection is not restarted; prior executable-method selection remains REVISE
and no new method is chosen here.

## 6. October 22 mathematical handover checklist

For each candidate, the analysis should return:

1. One explicit state/action/transition/reward model and timing diagram.
2. A policy-information table separating true state, observations, estimate,
   memory, model knowledge and future realization.
3. Feasible-set and resource equations shared by the compared policies.
4. An exact definition of the estimand and comparator policy classes.
5. Reused null and positive controls, with a statement of what they already
   resolve.
6. A mathematical issue that remains genuinely open, and what result would
   count as resolving it in either direction.
7. A go/no-go on whether existing software answers the question without a
   scientific-model change. No execution follows from this handover.

## 7. Interpretation boundary

An adaptive policy need not outperform a strong fixed policy for an
investigation to be informative. The target is a validated account of the
conditions and mechanisms governing outcomes. Conversely, policy-class
inclusion, a finite positive example, a successful software trace, or a
published mechanism alone is not sufficient evidence for a general HLS claim.
