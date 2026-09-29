# Heterogeneous Learning Systems — Handover

Last updated: 2026-09-28

## Handover entry protocol

This file is the **single canonical operational entry point** for continuing
the HLS research programme across sessions, agents, or collaborators.

There must be no second active `HANDOVER.md`. The canonical path is:

`docs/HANDOVER.md`

Before proposing new theory, algorithms, experiments, datasets, literature
directions, or candidate environments, recover the programme state from the
essential documents below. Historical protocols and branch-specific records
are consulted only when the task requires their provenance.

### Current scientific checkpoint

[HLS_checkpoint_after_B5.md](checkpoints/HLS_checkpoint_after_B5.md)

The PACS B2.1--B5 sequence and the subsequent Office-Home B0 vehicle screen
are closed. The current programme priority is the **HLS Synthetic
Environment**. A1a--A1c are **CLOSED / PASS**. RQ0 remains **OPEN**.

## Current focus — mandatory anti-drift anchor

The current work is **not** to choose the chronologically next experiment.

We are designing and progressively validating a **configurable, falsifiable
synthetic data/scenario generation framework for Heterogeneous Learning
Systems (HLS)**. Its purpose is to provide a controlled experimental testbed
for determining:

- when dynamic joint management of competence allocation/use and competence
  development/evolution can improve long-term system performance;
- why such an advantage can arise;
- when it does not arise;
- the capabilities and limitations of HLS;
- the boundaries and equivalence regimes in which separated management is
  sufficient.

The framework must not encode `HLS > SEP` by construction. It must support
positive, null, boundary, adverse, and reducible regimes.

**A1 is not the framework.** A1 is its first minimal analytical
validation/use. A1 established controlled L0 phase structure and exact
boundaries under its frozen assumptions; it did not validate RQ0 generally.

Before recommending any next step, ask:

> **What capability does the synthetic framework still need in order to test
> a scientifically important capability, limitation, mechanism, or boundary
> of HLS that A1 cannot test?**

Only after answering that question should a new experimental protocol be
designed.

Do not replace this question with “what experiment comes after A1?” and do
not assume in advance that the answer is longer horizon, `T>2`, more agents,
more tasks, transfer, interference, nonstationarity, real data, or any other
particular mechanism. Such additions require a scientific reason tied to the
framework and RQ0.

The detailed scientific contract for the generator is
[HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md).

## Mandatory first reads

Before substantive HLS work, read this **essential core**, in this order:

1. **This `docs/HANDOVER.md`**, especially the Current focus section above.
2. [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md) — programme-level
   methodology, evidence discipline, and anti-drift rules.
3. [checkpoints/HLS_scientific_continuity.md](checkpoints/HLS_scientific_continuity.md)
   — continuity document connecting RQ0, the two theoretical beams, ontology,
   cross-domain foundations, retained theory, accumulated evidence, closed
   paths, and the scientific point from which work continues.
4. [experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md)
   — current configurable/falsifiable synthetic framework and detailed A1
   record.
5. [research_questions.md](research_questions.md) — canonical wording and
   interpretation of RQ0.
6. [theoretical_foundations_cross_domain.md](theoretical_foundations_cross_domain.md)
   — established theoretical foundations and their HLS mappings.
7. [theory/two_beam/README.md](theory/two_beam/README.md) — technical
   skeleton connecting organization/use with competence development/evolution.
8. [hls_ontology.md](hls_ontology.md) — canonical HLS concepts and mapping
   discipline.
9. [general_research_model.md](general_research_model.md) — canonical HLS
   scientific object and architecture.
10. **Current scientific checkpoint**, presently
    [HLS_checkpoint_after_B5.md](checkpoints/HLS_checkpoint_after_B5.md),
    when detailed pre-synthetic empirical provenance is needed.

These files define the minimum context for deciding programme direction.
`README.md`, historical experimental protocols, earlier checkpoints,
microverification records, landscape files, literature records, paper drafts,
and supporting strategy documents are **supporting material**, not mandatory
first reads. Consult them when the current task requires their detailed
provenance.

Whenever a new scientific checkpoint supersedes the current one, update the
checkpoint pointer here and in `HLS_scientific_continuity.md`. Do not create
another handover file.

## Anti-drift rules for the current phase

Unless explicitly required by development or validation of the synthetic
framework, do not drift into:

- designing a paper instead of the framework;
- searching for novelty for every individual mechanism;
- reopening PACS or Office-Home repair branches;
- choosing a real dataset prematurely;
- adding complexity merely for realism;
- trying to prove universal `HLS > SEP`;
- weakening SEP to manufacture an advantage;
- treating SEP-Omega as an ordinary weak baseline;
- redefining RQ0 around A1;
- treating the A1 opportunity kernel as the definition of HLS;
- adding a mechanism without stating which HLS capability, limitation, or
  boundary it allows the framework to test.

Established theoretical mechanisms may and should be reused when they provide
a sound foundation, with explicit mapping to the HLS ontology. The programme
does not require novelty in every component; the scientific object is the
system-level integration and its consequences.

## Current experimental strategy after PACS/B0

PACS is closed as the current RQ0 vehicle; this is not evidence against RQ0.
Do not reopen it for N=25/100, replay variants, adapters, learning-rate or epoch
tuning, gradient protection, or other incremental repairs. Its historical
results and statuses below remain unchanged.

The Office-Home screen concluded **B0 = STOP B**. Its frozen-representation
transitions were more predictable than PACS, but its dominated portfolio and
limited reproducibly positive development did not supply the complementary,
non-dominated RQ0 vehicle sought. This is not evidence against RQ0. Do not
repair B0 by changing architectures, N, learning rate, epochs, adapters,
replay, protection mechanisms, or hyperparameters.

The methodological priority is now the **HLS Synthetic Environment**: controlled,
configurable, and falsifiable study of RQ0 mechanisms, limits, and equivalence
boundaries before returning to real datasets. This pivot does not modify RQ0.
Candidate A/iWildCam is **PARKED**, not rejected.

The exact L0 sequence is now **A1 CLOSED / PASS**: A1a established the
hand-solvable `M=2`, `K=2`, `T=2` worlds and exact solver; A1b reproduced the
primitive-parameter phase boundary in 1,020 preregistered configurations; and
A1c reproduced the competence-geometry boundary in 458 preregistered
configurations. Both sweeps had zero analytical mismatches and zero SEP-Omega
violations; A1c also had zero physical-relabeling and future-pair invariance
violations.

For a unique immediate optimum `h` and alternative `s`, the model-scoped A1
condition is

```text
delta_G = [g(s)-g(h)](D-N) > delta_R = r(h)-r(s),
```

or `rho(e_s-e_h)(D-N) > delta_R` under the frozen opportunity family. Strong
SEP routes by immediate reward and then optimizes development exactly; ties
retain the complete immediate-optimal set and use `J_SEP_max` for conservative
comparison. `HLS = SEP-Omega` at every A1b/A1c configuration: SEP-Omega is the
reducibility boundary with sufficient exact continuation information, not an
independent algorithmic benchmark.

A1 establishes controlled phase structure for the minimal mechanism, not
empirical validation of RQ0. It does not establish realistic-data performance,
trainable-model learning, long-horizon feedback, partial-observation
robustness, multi-step transfer/interference, or superiority over SEP-Omega.
The detailed post-run record is
[HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md).
RQ0 remains **OPEN**.

**Current decision boundary:** further sweeps of the same `T=2` L0 world are
low-value unless a specific theoretical ambiguity requires them. The next
scientific action must be selected by auditing which capability the synthetic
framework needs in order to test an HLS capability, limitation, mechanism, or
boundary not resolved by A1. The completed capability audit selected C1.

**G0+C1--C5 reference gates:** C1 provides repeated endogenous competence
evolution; C2 derived collective portfolio geometry; C3 persistent scarce
development resources; C4 signed transfer/interference physics; and C5
stationary, time-indexed, and Markov task demand. All current gates pass on
the same policy-neutral G0 framework; they are capabilities and controls, not
evidence that RQ0 holds. C6--C8 remain unimplemented.

**RQ0 causal state:** the initial RQ0-B campaign and the frozen 21-point
routing--opportunity `lambda` family are **SEP-REDUCIBLE**. The original
`eta=.5` diagnostic nevertheless established physically reachable local
routing inversions, while constrained reachability and demand persistence
`L=0..3` showed that those diagnostic inversions remain off every HLS-optimal
root continuation. These negative results remain evidence about their stated
families, not global reducibility.

A separate frozen zero-sum T2 geometry family now establishes a model-scoped
positive existence result relative to strong SEP:

```text
5/16 < alpha < 1/2  =>  J_HLS > J_SEP,max.
```

In that interval every HLS-optimal policy requires an on-policy non-greedy
routing action; SEP-Omega still equals HLS as the coordination/reducibility
boundary. Thus RQ0 status is: **existence YES under the exact model and
strong-SEP contract; structural characterization IN PROGRESS; robustness and
empirical relevance NOT ESTABLISHED.** RQ0 remains **OPEN**.

Do not run new experiments or tune the diagnostic/persistence/lambda/geometry
families. Current priority is **structural characterization theory**, using
[RQ0_EXPERIMENTAL_CAMPAIGN.md](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md),
[RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md),
and [rq0_routing_integration_boundaries.md](theory/rq0_routing_integration_boundaries.md).

## Central programme

The project studies heterogeneous portfolios in which routing and learning can alter each other over time:

```text
heterogeneous learners
    -> dynamic task allocation
    -> operational experience
    -> learning / knowledge transfer
    -> competence redistribution
    -> future task allocation
```

The central problem is the dynamic allocation and development of competences at system level. Operational allocation determines who performs work; learning and transfer decisions determine who learns what and from whom; present use may change future competence and performance.

Do not reduce the programme to:

- `frequency * quality_gap`;
- RouteNLP;
- a single teacher/student pair;
- "distillation causes homogenization";
- generic diversity preservation;
- Label Switching;
- M0/M0.1;
- a particular fast/slow cognitive analogy.

Those are possible components, adversaries, mechanisms, or historical steps.

## Official research question

RQ0 remains the sole promoted repository research question:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

H1 about failure frequency/quality gap is subordinate. It is a useful diagnostic problem, not the central hypothesis.

## Population-level correction

The relevant object is the competence distribution across a portfolio, conceptually:

```text
C_t = [c_iz(t)]
```

This matrix is provisional. The canonical ontology distinguishes competence coverage from competence proficiency and does not assume both fit one scalar entry.

The system may contain multiple learners and multiple teachers.

Two current structural principles are:

```text
individual failure != portfolio competence deficit
individual improvement != portfolio improvement
```

A model can fail on a region that another model already covers well. Teaching the failing model may create no system value, may create useful redundancy, may waste scarce learning capacity, or may alter specialization and future routing. The decision must be portfolio-conditional.

## Current proposition scaffolding

### P1 — Collective competence

Local failure/improvement must be valued against the whole portfolio. Structural foundation; not expected to be novel in isolation.

### P2 — Local-collective misalignment

A locally preferred learning action can be inferior in downstream portfolio value. Possible mechanisms include redundancy, coverage gaps, budget, learnability, specialization/interference, future demand, teacher heterogeneity, and future routing.

### P3 — Evolution can beat frozen routing

Direct adversary: a frozen heterogeneous portfolio with a strong adaptive router. P3 asks whether competence evolution can still improve long-term operational value under non-trivial conditions.

### P4 — Coupling advantage

Candidate subordinate comparison:

```text
J(pi_joint) > J(pi_separate)
```

The separate-management baseline must itself be strong and use comparable routing, learning/transfer machinery, compute, data, and budget. It must not be reduced to weak myopia. P4 is not an official RQ or established result, and weak dominance is tautological if the joint policy class simply contains the separate class.

## Scientific priority

Current order:

1. preserve the whole-system view of HLS as an evolving distribution of usable competences;
2. build theoretical foundations by extracting assumptions, mathematical content, limits, and HLS translations from strong cross-domain results;
3. reproduce important mechanisms minimally when useful;
4. map every source independently into the common ontology before translation or integration;
5. integrate supported components only when their role in the whole HLS, null cases, compatible units, and fair comparisons are explicit.

Do not let CR0--CR4, reachability, P4, or another tractable mechanism replace this programme-level priority.

## Constructive methodology and retained boundaries

The programme no longer treats a reduction to established theory as an automatic
reason to discard an HLS phenomenon. The working sequence is: identify an HLS
phenomenon; use the strongest applicable established theory constructively;
integrate compatible results through the ontology; derive HLS-specific
consequences; and then audit the resulting claims adversarially.

The central principle is: **do not ask whether HLS escapes existing theory; ask
what structure HLS induces, which established theories exploit that structure,
how those results can be integrated, and what useful HLS-specific consequences
follow.**

The minimal-model record retains the following boundaries: simple
operation-development competition can be separable; simple
operation-transfer coupling can be decentralized by prices; complementary
competences make development value portfolio-dependent but sufficiently
informed coordination can recover the optimum; routing boundaries can defeat a
specific marginal price while a continuation value or rich nonlinear contract
can coordinate the system; and central/joint management has no intrinsic
advantage over a perfectly coordinated modular architecture. The results also
show that development value is a continuation value, potentially dependent on
the portfolio and future choices, and that information, computation, and
communication are distinct coordination requirements.

M0 supplies the model-scoped reduced margin
\(g(q)=N_q[\lambda_q-m(q)]_+-\kappa_q\), making explicit the roles of operational
margin, future use, learnability, and learning cost. With competence
generalization, development value can become portfolio-dependent and
interventions can be complementary. Static formulations can sometimes reduce to
known combinatorial optimization. These are useful boundaries and potential
method sources, not automatic reasons to abandon the phenomena.

Constructive candidate paths, none yet an established HLS result or novelty
claim, include routing-as-teaching with limited expensive-model capacity,
index/RMAB/Whittle policies where their assumptions fit, competence-portfolio
valuation, competence complementarity, routing-generated learning
opportunities, transfer and generalization, and principled integration of
several established theories. A contribution may identify a tractable HLS
subclass, derive an interpretable scalable index, obtain a guarantee against
global control, characterize a sufficient operational signal, formulate
portfolio-development rules, integrate compatible theory, or map when standard
tools already suffice.

## Policy on existing pieces

Do not discard components because they have prior art. A strong paper can use known routing, KD, Machine Teaching, active learning, submodular allocation, continual learning, drift detection, or diversity mechanisms with proper citation.

The desired contribution may be:

```text
known components
+ one or more genuinely new pieces
+ a new coupling/objective
+ a demonstrable system-level property
```

At the same time, a mere unexplored combination is insufficient. The coupling should resolve a real limitation, expose an emergent property, or beat strong decoupled systems built from comparable pieces.

Potential locations for original pieces include competence-state representation, portfolio-gap analysis, intervention value, teacher/recipient selection, competence-redistribution policy, useful-complementarity measures, or controlled differentiation. None is yet claimed novel.

## Literature state

K0 established that several component claims already have strong precedent:

- online KD can homogenize peers;
- diversity-preserving online KD exists;
- ensemble diversity can contain information lost by ordinary ensemble distillation;
- expert diversity/selective expert training exists in continual learning;
- diversity can help under concept drift;
- KD can be weak under distribution shift;
- continual-learning KD can also preserve knowledge, so KD is not intrinsically destructive.

Recent routing precedents include RouteNLP, System-1.x, MixLLM, CONCUR and RouteLMT.

Budgeted learning/resource allocation and heterogeneous Machine Teaching are known areas. Their existence is not grounds to discard them as components and is not programme-level novelty by itself.

## Experimental epistemology — non-negotiable

A poorly designed experiment neither proves nor refutes the hypothesis.

Always separate **experimental outcome** from **experimental validity**.

Before treating a negative experiment as evidence against P2/P3/P4, establish that the benchmark actually instantiates the proposed mechanism, the intervention can affect it, the horizon makes the benefit observable, capacity is not a trivial confound, and strong baselines are correctly implemented.

Before treating a positive result as support, rule out weak baselines, extra compute/data/capacity, tuning asymmetry, leakage, favourable shift selection, and post-hoc benchmark construction.

Every experiment must explicitly audit:

1. construct validity;
2. causal identification;
3. comparison validity;
4. external validity.

Synthetic experiments provide controlled causal tests; real benchmarks provide realism. Neither alone is decisive.

## Methodological discipline

For every important paper ask:

- What exact decision problem is solved?
- What is the state and action?
- What is optimized?
- What is assumed known?
- Which components are fixed and which evolve?
- Is heterogeneity nominal or operationally important?
- What actually changes after learning?
- Is the evidence synthetic, benchmarked, deployed, or only theoretical?
- What strong baseline is beaten?
- What failure modes, hidden assumptions, favourable regimes, or cherry-picking remain?
- What does the paper **not** establish?

A recent related paper is evidence of an active area, not automatically evidence that the programme is closed.

## Consolidated theoretical state

### Retained v1 result

The minimal model uses two agents, one competence, `T=2`, a shared capacity constraint for operational allocation and competence development, and no terminal reward for competence. Under normalized capacities, demand sufficient to operate both agents, and a period-2 opportunity with probability `p`, it defines

```text
V_m^A = S_m,1 + p eta_m
V_m^D = p lambda_m.
```

For the fixed-priority sequential baselines, the exact gaps are

```text
J_J - J_A->D = sum_m [V_m^D - V_m^A]_+
J_J - J_D->A = sum_m [V_m^A - V_m^D]_+.
```

Thus operation-first is strictly suboptimal when `V_m^D > V_m^A` for at least one agent; development-first is strictly suboptimal when the reverse inequality holds for at least one agent. The orders fail in complementary regions, so neither fixed priority is universally optimal in this model. Equality holds when the corresponding positive-part summands all vanish.

This is an existence result only for the two explicitly defined fixed-priority separated architectures. A separated architecture with sufficient coordination can reproduce the joint solution; it is not a proof against every separated architecture, a general answer to RQ0, or a novelty claim. See [minimal_hls_model.md](theory/minimal_hls_model.md).

### Proposition 1 — Additive equivalence boundary

For the reduced block `J=C+V^A a+V^D d`, with the v1 nonnegative marginal values and `a,d>=0, a+d<=1`, a stronger separated architecture chooses an optimal prior share `rho in [0,1]` and executes `(a,d)=(rho,1-rho)`. It obtains `J_S^*=J_J^*=C+max{V^A,V^D}`. Additive contributions and competition for capacity therefore permit equivalence through appropriate resource allocation. This boundary does not constitute a negative result for HLS. Separate execution here includes coordination of the resource decision.

### Proposition 2 — Coordination/selection with operation-dependent development

The only physical extension is `E_ind=ad` in place of v1's `E_ind=d`. With all other physical assumptions retained, the reduced block is `J=C+Va+Lad`, with `V,L>0` and the same capacity constraint.

An intermediate definition in which both managers optimized global `J` with respect to their own variable is discarded as a definition of strict separate management. The corrected decision criteria are `J_A=Va` and `J_D=Lad`: the development manager knows the physical technology, but neither manager optimizes global `J`. They are managers of the two decisions, not the two physical agents. Performance is still evaluated using the common physical objective `J`.

Their best responses are `BR_A(d)=1-d` and, for `a>0`, `BR_D(a)=1-a`. The positive-activity separated equilibria are all `(a,1-a)` with `0<a<=1`. For `0<V<L`, the unique joint optimum is

```text
a_J^* = (V+L)/(2L)
d_J^* = (L-V)/(2L)
J_J^* = C+(V+L)^2/(4L)
J_J^* - J_S(a) = L(a-a_J^*)^2.
```

Only `a=a_J^*` achieves the joint optimum, and that allocation itself is a separated equilibrium. Consequently, `max_{(a,d) in E_S} J(a,d)=J_J^*`; there is no strict advantage over the best separated equilibrium. The local decision criteria do not select an equilibrium by themselves. No selection dynamics or probability of a loss has been established.

At `V=L>0`, the joint optimum remains unique at `(1,0)` and the gap is `L(1-a)^2`. At `a=0`, development is indifferent over `[0,1]`; only `(0,1)` also satisfies the operational best response, adding a degenerate equilibrium with value `C`.

Both propositions are DERIVED-IN-MODEL. The numerical coincidence of best responses under the discarded and corrected formulations does not identify their decision criteria. Nor does the interaction rule out an optimally coordinated prior split. Separation of execution must not be confused with separation of decision objectives.

### Proposition 3 — Nonlocal information boundary

For complementary competences, the reduced period-2 value is `V_2(S1,S2)=p R S1 S2`. Developing `S1` at period 1 has the joint threshold `S2^*=V/(p R lambda)`. If admissible values lie on opposite sides of that threshold, the two joint choices differ. A development incentive that is constant across `S2` cannot implement both choices, while the state-dependent price `tau^*(S2)=p R lambda S2` does so exactly. This is the development increment times the marginal value `dV_2/dS1=p R S2`; complementarity has cross derivative `pR>0`.

The result requires information about a different competence for this pricing rule. It does not show that decentralized coordination is impossible, that joint management is strictly superior, or that `S2` must be transmitted directly in every architecture.

### T=3 continuation-policy boundary

With terminal value `R S1,3 S2,3` and period-2 development of `S2`, the continuation value is `V_2(S1,S2)=p R S1 S2+max{K,p R mu S1}`. The continuation action changes at `S1^dagger=K/(p R mu)`. Away from that indifference point, the period-1 price is `tau_1^*=lambda p R [S2+mu x^*(S1,2)]`; at the threshold it is set-valued because the value function has a kink.

The price therefore depends on the optimal continuation policy, but that policy is a single explicit threshold. T>2 does not establish a need for joint management, irreducible complexity, or a requirement to communicate a full Bellman value function. A sufficient representation of the relevant gradient can be enough.

### Operational-development opportunity-value checkpoint

The companion note [operational_development_opportunity_value.md](theory/operational_development_opportunity_value.md) records further **DERIVED-IN-MODEL** identities without changing the ontology, RQ0, or the minimal-model boundaries. It keeps the decisions distinct: an operational action `a` selects current execution and may make a development action `d` feasible, but it does not itself use the opportunity or change competence. Its exact decomposition is

```text
Q(S,q,a) = R(S,q,a) + beta V(S) + Omega(S,q,a),
```

where `Omega` is the nonnegative incremental value of the development opportunities remaining after `a`, under the explicit no-use action. The note separates two structural axes: whether `Omega(S,q,a)` changes the present routing ranking, and whether development-set values are additive or coupled by the future competence portfolio.

For two independent competence improvements, future routing can itself create portfolio geometry. A single future backup capacity shared by two classes gives the exact finite-difference result `Gamma_SUB <= 0` (substitution); a future task whose fast model is limited by `min{s1,s2}` gives `Gamma_COMP >= 0` (complementarity). Their workload mixture has `Gamma(p)=p Gamma_SUB+(1-p) Gamma_COMP`, so its sign can reverse. These are exact reduced-model results: neither requires non-additive learning dynamics, establishes novelty, proves HLS/joint-management superiority, nor excludes sufficiently coordinated modular architectures.

The same note now closes the two-policy selection result. If two fixed future policies are individually additive and `V=max{V^A,V^B}`, their entire routing-induced interaction is `Gamma(z,x,y)=[z+x+y]_+-[z+x]_+-[z+y]_++[z]_+`: it is nonnegative when `xy>0`, nonpositive when `xy<0`, and zero if either increment vanishes or one policy remains optimal at all four vertices. With `c=beta Gamma`, additive development costs give the exact joint value `g12=g1+g2+c`. The note exhaustively identifies the strict regions in which portfolio valuation changes the individual-sign decision and gives the exact associated value loss. These DERIVED-IN-MODEL results concern two policies and two interventions only; they show that future routing can induce development interaction, not that routing and learning must always be jointly managed.

The first integrated `Omega + Gamma` Fast/Deep checkpoint is also recorded there. In the symmetric complementary continuation-value regime `s1=s2=s>h`, each individual choice to route a current task to Deep, create, and use its opportunity has `H_i=-(s-h)-kappa_i<0`, while the paired choice has `H12=-2(s-h)-kappa1-kappa2+beta Delta`. It is strictly beneficial exactly when `beta Delta > 2(s-h)+kappa1+kappa2`, and satisfies `H12=H1+H2+beta Gamma12` with `Gamma12=Delta`. This result combines operation-dependent opportunity availability with future portfolio complementarity inside one Fast/Deep model. The complementarity is induced by the fixed `min{s1,s2}` continuation bottleneck, not necessarily by a policy boundary. It remains DERIVED-IN-MODEL and does not establish general joint-management superiority or a universal need to jointly solve routing and learning.

Proposition 7 now has a structural finite-set generalization. For `H(D)=-K(D)+beta[V(S_D)-V(S)]`, the exact decomposition is `H(D)=sum_i H_i+beta Xi_V(D)-Xi_K(D)`. Under independent development and additive costs, modular continuation value rules out joint rescue from individually non-beneficial opportunities. Quantitative increasing differences provide a sufficient rescue condition: the uniform smooth bound is `Xi_V(D)>=sum_{i<j} mu_ij Delta_i Delta_j`, with a parallel finite-difference formulation for non-smooth values. Weak supermodularity fixes only the sign of interaction, not its decision effect; the bound must exceed accumulated individual deficits. The record explicitly retains the higher-order-interaction caution for `n>2`.

### B1 exploratory empirical interaction pilot

The first empirical pilot, [B1 README](../experiments/pilots/b1_empirical_interaction/README.md), has now been executed on `sklearn.datasets.load_digits`. It uses the preregistered split roles, LogisticRegression as Fast, RandomForestClassifier as Deep, validation-only confusion-profile competencies (`K=4`), hard pseudo-label transfer as the primary condition, and true-label/random-group controls. Across 10 seeds and budgets `B in {5,10,20,40}`, the run completed 1,620 fits. Fast/Deep test balanced accuracies averaged `0.9533/0.9652`; competence clustering stability was low and variable (ARI mean `0.133`, range `-0.164` to `0.683`). Primary Gamma means were `0.00032`, `-0.00039`, `-0.00083`, and `-0.00046` for the four budgets, with both signs observed and variability larger than the means. The pilot is therefore classified **OBSERVED — WEAK / UNSTABLE INTERACTION**. These are exploratory observations only: they do not alter the theory, RQ0, or any claim about novelty or architectural superiority.

### PACS B2.0/B2.1 status

The initial B2.0 CPU-feasibility stop recorded below in the research log was
superseded by a completed 25-fit CPU calibration. MPS was excluded after a
diagnostic found label corruption on its non-blocking transfer path. The stored
B2.0 automatic rule selected 10% and then evaluated TEST; the later B2.1 design
decision fixed F0 at 25% and did not use TEST. This provenance distinction must
be preserved.

B2.1 completed 160 CPU fits over five seeds, N in {25,50,100}, and six PACS
domain pairs. All 18 N-by-pair mean Gamma_learn values were positive; every
pair was positive in 5/5 seeds at N=50 and 100. Fast/Deep operational valuation
substantially absorbed those interactions at low Deep cost and approached the
learning interaction as Deep cost increased. Routing changed in 420/450
observations, but that association is descriptive rather than causal.

Use [the B2.1 checkpoint](checkpoints/HLS_checkpoint_after_B21.md) for the
current consolidated scientific position and exact evidence paths. No result
establishes TEST generalization, a complete HLS policy, or joint-management
superiority.

### B2.2 completed status

[B22_PROTOCOL.md](experimental_foundations/B22_PROTOCOL.md) froze the completed
empirical checkpoint. For the same PACS F0/D system, the recorded operational
action gates the learning opportunity:
`D(F)={0}` and `D(D)={0,1}`. The primary event is `rho_k(c)>0` and
`H_k(c,B,kappa)>0`, equivalently
`B DeltaV_k(c)>rho_k(c)+kappa`. The primary grid fixes
`N={25,50,100}`, `c={0,0.02,0.05,0.10,0.15}`, `B={1,2,5,10}`, five seeds,
four domains, and `kappa=0`. The valid CPU run completed 60 updates and 1,200
analytical rows with TEST closed. Four rows were favorable, but zero of 240
cells reproduced favorability in at least two seeds, so the frozen result is
`INCONCLUSIVE`. See [the B2.2 diagnostic](../results/pilots/b22_opportunity_value/b22_diagnostic.md).
This is not an end-to-end HLS-policy or RQ0 claim.

### Retrospective B2.1–B2.2 bridge

The retrospective portfolio analysis in
[portfolio_bridge.md](../results/pilots/b22_opportunity_value/portfolio_bridge/portfolio_bridge.md)
was stopped at its compatibility gate. B2.1 and B2.2 had matching nominal
grids and procedures, but their stored F0 and D vectors differed in every seed
and their singleton vectors differed in all 60 interventions. Consequently
zero of 90 learned pair states were counterfactually compatible and no
`H_i<0, H_j<0, H_ij>0` test was validly performed. This is missing
identification, not evidence that portfolio rescues are absent.

### B2.3 completed status

[B23_PROTOCOL.md](experimental_foundations/B23_PROTOCOL.md) freezes a
self-contained test of whether two operation-generated opportunities that are
individually unprofitable become profitable when accumulated and developed
jointly. One F0 and D per seed, immutable nested opportunity streams, exact
parent/opportunity hashes, and opportunity-matched updates make singleton and
joint states counterfactually compatible. Each joint fit stores a
fixed-total-compute midpoint before continuing to the dose-matched endpoint.
The frozen design contains 160 fits, 250 validation evaluations, 1,800 primary
analytical rows, and 450 secondary midpoint dose-control valuations. `POSITIVE`
requires rescue in at least 3/5 seeds within one
exact `N × pair × c × B` cell; `NULL` means no rescue anywhere; remaining valid
nonempty cases are `INCONCLUSIVE`.

Status: **B2.3 COMPLETE — INCONCLUSIVE**. The CPU-only implementation is in
[`experiments/pilots/b23_portfolio_opportunity/`](../experiments/pilots/b23_portfolio_opportunity/).
The compatibility audit passed all 250 VALIDATION vectors; TEST remained
closed. The run completed 160/160 fits and 1,800/1,800 primary rows. Three rows
met the rescue event, but no exact cell reproduced it in at least 3/5 seeds.
Learning interaction was positive in 89/90 states. The main bottleneck was
magnitude: 917 rows reached the positive-operational-interaction stage, but
only three interactions overcame both singleton deficits. Singleton value was
negative in 273/300 deduplicated valuations. All three rescues disappeared at
the secondary fixed-total-compute midpoint, so B2.3 does not establish rescue
under equal total training compute. See the current
[B2.3 checkpoint](checkpoints/HLS_checkpoint_after_B23.md).

**POST-HOC MECHANISM DIAGNOSIS COMPLETE.** All 60 singleton states had
negative cross-domain competence sums. Thirty-three improved their target,
but all 33 harmed the remaining domains in aggregate and in 31/33 that loss
exceeded the local gain. The mean `DeltaV` decomposition was local -0.005234,
cross-domain -0.092481, and routing +0.066657, giving -0.031059. Cross-domain
loss was the dominant negative term in 271/273 negative valuations. This
localizes the bottleneck to development-induced cross-domain interference;
the data do not identify its underlying learning mechanism.

### B2.4 completed status

[B24_PROTOCOL.md](experimental_foundations/B24_PROTOCOL.md) froze a paired
test of the specific replay substitution relative to O50, with equal compute
and exactly matched effective opportunity exposure. The CPU run completed
120/120 new fits, 180/180 new VALIDATION evaluations, and 1,200/1,200 value
rows in 04:57:04. Compatibility passed and TEST remained closed.

All preregistered global outcomes were **POSITIVE**: interference reduction,
local learning, and future value at each `c={0,.02,.05,.10,.15}`. Mean
cross-domain recovery was +0.336271, favorable in 59/60 states; all 12 exact
domain-by-N regimes reached at least 4/5 favorable seeds. Mean `DeltaL` was
+0.032682. Mean future-value improvement across c was +0.025107, of which
+0.022300 (88.8%) came from non-target competences. REP2 did not improve REP
when full opportunity exposure was restored by adding compute, although REP2
remained better than STD.

The scientific method-state count is 240: 60 each for STD, O50, REP, and REP2.
The generated `360/240` summary label included 120 repeated F0/D lookup views
in its numerator and is not a scientific discrepancy. See the current
[B2.4 checkpoint](checkpoints/HLS_checkpoint_after_B24.md) and
[result audit map](../results/pilots/b24_interference_controlled/AUDIT_README.md).
Subsequent B3, integrated RQ0, B4, and B5 work is consolidated in the current
[B5 checkpoint](checkpoints/HLS_checkpoint_after_B5.md).

## General theory audit retained for later work

Use the [minimal model](theory/minimal_hls_model.md), [operational-development opportunity-value note](theory/operational_development_opportunity_value.md), closed [ontology](hls_ontology.md), [research questions](research_questions.md), and [research doctrine](../RESEARCH_DOCTRINE.md) as anchors. A later adversarial audit, not started here, may test whether any previously excluded mechanism creates a dependency that does not reduce immediately to a simple price or threshold: (A) changing or uncertain future demand; (B) several agents with alternative competences, where development changes subsequent use, development, or knowledge-source choices; and (C) learning by doing, where operational allocation generates direct experience and changes future competences. This record neither specifies nor analyses A/B/C. HLS is not claimed to be the only way to select the optimum.

Do not start a large experiment until the proposition, competence transformation, adversaries, matched information and resources, and validity conditions are explicit.

## Independent prior project

`adaptive_routing` remains an independent prior project and must not be silently imported as HLS evidence.
