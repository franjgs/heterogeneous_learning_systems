# Heterogeneous Learning Systems — Handover

Last updated: 2026-09-26

**Current checkpoint:** [HLS_checkpoint_after_B5.md](checkpoints/HLS_checkpoint_after_B5.md).
Any new work must begin with that checkpoint and
[RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md).

Repository state: the PACS B2.1--B5 sequence is closed. The one-shot,
70-state integrated RQ0 TEST evaluation was **INCONCLUSIVE** and verified
`HLS = SEP-Omega`; B3 viability was **NO**; B4 was **INCONCLUSIVE**; and B5
GREP was **NULL**. B2.4's replay result remains positive for its declared
VALIDATION contrast, but it did not eliminate seed dependence. Do not start a
B6-style PACS continual-learning variant automatically; the next decision is
whether another minimal, non-artificial environment can test RQ0 directly.

## Mandatory first reads

Before proposing new theory, algorithms, or experiments, read in this order:

1. [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md) — general methodology and anti-drift rules above any individual HLS mechanism.
2. `README.md` — short project entry point. **Do not rewrite it to follow every intermediate hypothesis.**
3. [general_research_model.md](general_research_model.md) — canonical HLS scientific object and architecture.
4. [research_questions.md](research_questions.md) — canonical wording of official RQ0 and subordinate H1.
5. [hls_ontology.md](hls_ontology.md) — canonical HLS concepts, units/ranges, mapping classes, and source-to-HLS mapping discipline.
6. [theory/minimal_hls_model.md](theory/minimal_hls_model.md) — v1; Propositions 1–3 on additive equivalence, selection, and nonlocal information; and the T=3 continuation-policy boundary.
7. [theoretical_foundations_cross_domain.md](theoretical_foundations_cross_domain.md) — canonical map of established principles to understand, map, translate, and test.
8. [theory/two_beam/README.md](theory/two_beam/README.md) — current technical skeleton connecting organization/use with competence development/evolution; not a complete HLS model.
9. [experimental_foundations/README.md](experimental_foundations/README.md) and [experimental_foundations/EXPERIMENTAL_SPEC_V0.md](experimental_foundations/EXPERIMENTAL_SPEC_V0.md) — audited Beam 1, Beam 2, and interface-reproduction block; B2.5 remains `FAILED_SOURCE_REPRODUCTION`, and B13 is diagnostic only.
10. `research_origin_and_chronology.md` — historical provenance and superseded directions.
11. [research_program_checkpoint_004.md](research_program_checkpoint_004.md) — historical pre-ontology checkpoint, not the current RQ0 source.
12. `research_strategy_cross_domain_toolkit.md` — supporting protocol for importing mathematics without replacing the HLS problem.
13. `landscape/landscape_001_consolidated.md` and `literature/references.bib`.
14. [theory_integrated_competence_investment_model.md](theory_integrated_competence_investment_model.md) and [theory_civ_adversarial_stress_test.md](theory_civ_adversarial_stress_test.md) — subordinate CIV model and its branch register; portfolio exposure is not a current programme priority.
15. `models/model_M0.md` and `models/model_M0_1_gap_dependent_learning.md` only as diagnostic history, not as the current centre.
16. [theory_competence_evolution_minimal_model.md](theory_competence_evolution_minimal_model.md) and [experiments/microverification/](../experiments/microverification/) — CR0--CR4 minimal-model audit; not a general HLS result.
17. [paper/](../paper/) — working draft with a stale RQ0 formulation; do not let it set programme direction and do not update it without a dedicated paper task.
18. [checkpoints/HLS_checkpoint_after_B21.md](checkpoints/HLS_checkpoint_after_B21.md) — concise scientific checkpoint linking the established theory, negative boundaries, B1, B2.0, B2.1, and the remaining empirical gap.
19. [experimental_foundations/B22_PROTOCOL.md](experimental_foundations/B22_PROTOCOL.md) — frozen protocol for the completed PACS opportunity-value experiment; see [the B2.2 diagnostic](../results/pilots/b22_opportunity_value/b22_diagnostic.md) for the audited result.
20. [experimental_foundations/B23_PROTOCOL.md](experimental_foundations/B23_PROTOCOL.md) — frozen protocol for the completed PACS accumulated-opportunity portfolio experiment.
21. [checkpoints/HLS_checkpoint_after_B23.md](checkpoints/HLS_checkpoint_after_B23.md) — prior scientific checkpoint, including the B2.3 autopsy, compute-dose sensitivity, and evidence map.
22. [experimental_foundations/B24_PROTOCOL.md](experimental_foundations/B24_PROTOCOL.md) — frozen protocol for the completed interference-controlled development experiment.
23. [checkpoints/HLS_checkpoint_after_B24.md](checkpoints/HLS_checkpoint_after_B24.md) — historical B2.4 checkpoint.
24. [checkpoints/HLS_checkpoint_after_B5.md](checkpoints/HLS_checkpoint_after_B5.md) — current checkpoint: B3, integrated RQ0, B4, B5, and the post-B5 strategic decision.

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
