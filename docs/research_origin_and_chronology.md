# Research origin and chronology

Date: 2026-09-14  
Status: orientation document. Read this before narrowing the programme to a subproblem.

## Why this file exists

The programme has repeatedly risked confusing an intermediate mechanism with the central scientific idea. This file records the chronological origin of the project and the corrections made during the first research cycle. It is not a replacement for `README.md`, which remains the stable repository-level framing.

The central programme is **not** RouteNLP, `frequency * quality_gap`, distillation, homogenization, diversity, Label Switching, or any particular mathematical model. Those are possible pieces, adversaries, mechanisms, or diagnostic tools.

## 1. Original intuition: heterogeneous multi-level learning system

The starting idea is a system with two or more heterogeneous learners/models with deliberately different operating profiles. Early levels may be fast, cheap, shallow, or highly responsive; later levels may be slower, more expensive, deeper, or more capable. The division of labour is dynamic rather than fixed.

The intended loop is:

```text
heterogeneous learners
    -> dynamic task allocation
    -> operational experience
    -> learning / knowledge transfer
    -> competence redistribution
    -> future task allocation
```

The original intuition also included deliberate preservation or creation of useful heterogeneity as a possible source of protection, specialization, redundancy, and adaptation. The programme does not assume that diversity is always beneficial.

## 2. Umbrella formulation

The project was formalized as **Heterogeneous Learning Systems**. A provisional competence landscape was introduced:

```text
C_t = [c_iz(t)]
```

where `c_iz(t)` denotes the effective competence of learner/model `i` on task region or family `z` at time `t`.

At that stage, the following formulation was promoted as the sole repository-level research question:

> Can the deliberate evolution of competence allocation in a heterogeneous learning system improve its long-term performance compared with independently optimizing task allocation and knowledge transfer?

At that historical stage, the phrase **deliberate evolution of competence allocation** was treated as central. The wording was superseded on 2026-09-17; it is preserved here only to reconstruct the programme's development.

## 3. Horizontal audit and RouteNLP

The initial landscape audit found mature components in routing, cascades, Machine Teaching, active learning, resource allocation, continual learning, decision-focused learning, Quality-Diversity, and related areas.

RouteNLP became the strongest direct operational precedent because it already closes a loop from routing failures to targeted distillation and then back to routing. Therefore, `routing -> learning -> rerouting` cannot be claimed as novel by itself.

This led to the narrower working hypothesis H1 around whether failure frequency and quality gap are sufficient statistics for selecting competence-improvement actions.

## 4. M0 and M0.1

M0 and M0.1 were built deliberately as diagnostic models for H1. They separated observed failure severity, learnability, training cost, and downstream operational value. They showed that a `frequency * quality_gap` ordering can differ from an intervention-value ordering under plausible model assumptions.

The critical lesson from M0.1 was that this behaviour depends on the actual learning response. More algebra around `p * delta` without empirical or mechanistic grounding was judged unproductive. H1 remains useful as a subordinate diagnostic hypothesis, not as the centre of the programme.

## 5. Return to the original programme

The programme then corrected a drift toward treating RouteNLP selection as the whole research problem. The original focus was recovered: heterogeneous learners, dynamic task allocation, competence evolution, and deliberate management of specialization/complementarity.

At this stage diversity was still only a broad intuition and had not yet been converted into a concrete scientific mechanism.

## 6. Adversarial expert and candidate failure mode

An adversarial expert proposed a possible failure mode: repeated competence transfer or distillation toward currently successful models may homogenize a portfolio and destroy complementary competences that later become useful under distribution shift. This was labelled the **Homogenization Trap**.

The expert proposal was not accepted as fact. It was treated as a falsifiable candidate mechanism. The principal adversarial objections were that capacity may dominate diversity and that a frozen diverse portfolio with an adaptive router may already capture most of the benefit.

The resulting working priority was:

1. useful complementarity versus competence transfer under shift;
2. frozen heterogeneous portfolio versus evolving portfolio as a direct adversary;
3. value-driven choice of what/who to train only if the first mechanism survives;
4. RouteNLP `frequency * gap` as a baseline/subproblem;
5. fast/slow architecture as a strong setting but weak novelty claim by itself;
6. no further M0/M0.1 mathematics without evidence.

## 7. K0 vertical audit

K0 audited the exact mechanism:

```text
knowledge transfer / distillation
    -> loss of functional diversity or complementarity
    -> loss of robustness or adaptability under shift
```

The audit found strong precedents for individual pieces:

- online KD can homogenize peers;
- diversity-preserving KD exists;
- ensemble diversity can carry uncertainty/robustness information;
- diversity can help concept-drift adaptation;
- KD can behave poorly under distribution shift;
- continual-learning KD can also preserve knowledge, so distillation is not generically destructive.

K0 did **not** establish that the full operational portfolio mechanism is solved. It narrowed the interesting question to how competence-changing actions alter the portfolio structure and its future operational value.

## 8. Population-level correction

A further correction was essential: the problem is not a single weak learner receiving knowledge from a single teacher.

The system may contain multiple learners and multiple teachers:

```text
M = {M_1, ..., M_N}
T = {T_1, ..., T_K}
```

A learner can fail on a domain without creating a system deficit if another learner already covers it well. Therefore:

```text
individual failure != portfolio competence deficit
individual improvement != portfolio improvement
```

This makes the distribution of competences across the population the relevant object. A useful learning action may create a missing competence, create useful redundancy, create useless redundancy, reduce specialization, consume scarce learning capacity, change routing, or alter future adaptability.

## 9. Reassessment of P1, P2, P3 and P4

### P1 — Collective competence

A local failure or local competence gain must be evaluated relative to the whole portfolio. If another learner already dominates the same region at comparable operational cost, improving the failing learner can have zero marginal system value.

P1 is a structural foundation and is not expected to be novel in isolation.

### P2 — Local-collective misalignment

There can be actions `u_1`, `u_2` such that a local learning criterion prefers `u_1` while downstream portfolio value prefers `u_2`:

```text
J_local(u_1) > J_local(u_2)
V_portfolio(u_1) < V_portfolio(u_2)
```

Mechanisms may include redundant competence, missing coverage, scarce learning budget, interference, loss of specialization, useful redundancy, future demand change, teacher/recipient heterogeneity, learnability, and future routing effects. No single mechanism is assumed necessary.

P2 is considered a high-value pillar if non-trivial mechanisms and strong baselines can be identified.

### P3 — Evolution can outperform frozen routing

A strong adversary is a frozen heterogeneous portfolio with a high-quality adaptive router. P3 asks whether there are realistic conditions under which deliberately changing the competence landscape provides higher long-term system value than routing alone.

P3 should not rely only on the trivial case of a completely unseen competence that no current learner can solve. A stronger case is one in which all regions have reasonable initial coverage but the optimal competence distribution changes with workload, costs, constraints, or future conditions.

P3 is considered a critical proposition for RQ0.

### P4 — Coupling advantage

P4 is not yet an official hypothesis but is the strongest candidate system-level claim:

```text
V_coupled > V_route-opt + learn-opt-separately
```

The decoupled baseline should be strong: good router, good learning allocator, good teacher/transfer mechanism, same compute, same training budget. The difference should be the use of cross-information between routing and competence evolution.

P4 would isolate the value of the system coupling rather than the value of a weak baseline or a single new component.

## 10. Known pieces are allowed

This programme does **not** require every component to be novel. Known routing, distillation, active-learning, submodular/resource-allocation, continual-learning, diversity-preservation, or drift-detection methods may be reused and cited.

A credible contribution may consist of:

```text
known components
+ one or more genuinely new pieces
+ a new coupling or objective
+ a demonstrable system-level property
```

The novelty requirement applies to the scientific contribution of the complete system and should ideally also include one or more non-trivial components, representations, objectives, or policies. The programme must avoid both extremes: rejecting useful pieces because they have antecedents, and claiming novelty merely because a particular collection of known blocks has not previously appeared together.

Possible locations for novel pieces include portfolio competence representation, competence-gap analysis, downstream intervention value, teacher/recipient selection, competence-redistribution policy, useful-complementarity measures, and controlled differentiation mechanisms. None is yet claimed novel.

## 11. Experimental epistemology — mandatory caution

A poorly designed experiment neither proves nor refutes the research hypothesis.

Negative evidence is meaningful only if the experiment actually gives the hypothesized mechanism a fair opportunity to operate and the comparison class is strong and correctly implemented. Positive evidence is meaningful only if alternative explanations, leakage, favourable benchmark construction, weak baselines, tuning asymmetry, capacity confounds, and cherry-picked shifts are controlled.

Therefore every experiment must separate at least four questions:

1. **Construct validity:** does the benchmark instantiate the competence-allocation phenomenon being claimed?
2. **Causal identification:** does the intervention manipulate the proposed mechanism rather than a confound such as raw model capacity?
3. **Comparison validity:** are frozen-routing, decoupled-learning, and other strong adversaries implemented and tuned fairly?
4. **External validity:** is the effect robust beyond a deliberately favourable synthetic construction?

An experiment that fails one of these checks must not be used to kill or confirm RQ0/P2/P3/P4. A synthetic experiment is useful for causal isolation; it is not by itself evidence of practical relevance. A real benchmark is useful for realism; it is not by itself evidence that the intended mechanism caused the result.

The project should record **experiment validity separately from experimental outcome**.

## 12. Current state

The programme is after K0 and after the population-level correction. No new official RQ has replaced RQ0. H1 is subordinate. P1-P4 are current analytical scaffolding, not established theorems or novelty claims.

The next scientific task is to construct the smallest coherent system in which P1, P2 and P3 are simultaneously relevant, then ask whether P4 can arise against a genuinely strong decoupled baseline. Formalisation should be used to expose assumptions and counterexamples, not to force a result. Experimental design should begin only after the mechanism and falsification logic are explicit.

## 13. Cross-domain mathematical consolidation

The programme next adopted a corrective methodological position: other fields are sources of apparatus, not replacements for the HLS problem. Portfolio management, Operations Research, economics, control, organizational science, human competence management, Machine Teaching, and machine learning provide useful state concepts, transitions, constraints, theorem patterns, and experimental designs.

The managed material was made explicit: usable knowledge or competence is distributed across heterogeneous learners; learning transforms that distribution; operation gives it value; and time makes acquisition an investment. This enabled competence trajectories, marginal value, opportunity cost, specialization, redundancy, rebalancing, depreciation, and option value to be considered as candidate apparatus without redefining HLS as another domain. The strategy labels SPECIALIZE, BROADEN, REPLICATE, and REBALANCE remained provisional analytical families rather than results.

## 14. Minimal competence-evolution theory and microverification

The population-level programme then received a deliberately small theoretical laboratory. It was built to test coherence, identify null cases, and permit early falsification before larger experiments. The resulting CR0--CR4 record strict separability, a finite complementary threshold, a local specialization stability threshold, scalar rebalancing identities, and a dual-actuator optimum under explicit minimal assumptions.

Microverification checked the stated identities and limited behaviours. This was not a transition from programme hypothesis to general result: CR0--CR4 remain model-scoped consistency/falsification evidence. They do not establish general HLS behaviour, broad strategy value, RQ0, P4, novelty, or superiority of a coupled controller.

## 15. Adversarial reassessment and paper skeleton

The minimal-theory direction was reassessed adversarially. The issue was not that its results were incorrect, but that mathematically tractable results can become too small to stand in for the original scientific object. A compilable paper skeleton was created as a theory nucleus and communication test. It showed that the minimal theory could be organized coherently, not that it was a sufficient HLS paper or that it should be expanded by inertia.

This reassessment required another return to the whole-system perspective: the paper and minimal theory are instruments for a broader question, not the programme itself.

## 16. General HLS research model

The programme now records a stronger synthesis in `general_research_model.md`. The chronology is therefore:

```text
initial intuition
    -> decomposition and literature confrontation
    -> diagnostic branches
    -> corrections
    -> minimal formalization
    -> adversarial limits
    -> stronger programme-level synthesis.
```

This was not a linear sequence of successes. Corrections of focus are part of the scientific knowledge acquired. The final return to the general view did not reject CR0--CR4; it recognized that they are too small to replace the original HLS problem.

## 17. Directed structural prior-work audit

The programme moved from searching for analogies to testing structural equivalence. The first directed audit found stronger precedents than expected in dynamic workforce competence allocation, transactive memory and dynamic capabilities, and heterogeneous classroom Machine Teaching.

The novelty space narrowed, but RQ0 was not reduced by nominal or partial overlap. The next literature and theory work must attempt formal reductions and identify the exact residual assumptions, endogenous quantities, or comparison classes that prevent equivalence.

## 18. Paper reframing: architecture, theory, and validation

The paper skeleton was then reframed so that the minimal 2x2 theory no longer determines the main narrative. Its working order is architecture/problem, integration theory, and experimental validation. The A1--A5 functional architecture distinguishes distributed heterogeneous competence, collaborative division of labour, selective knowledge allocation, portfolio evolution, and system-level orchestration.

This is a documentation and communication correction, not a new theory result. The integration theory remains a scaffold and the general validation programme remains prospective. CR0--CR4 are retained as preliminary model-scoped evidence.

## 19. Integrated competence-investment scaffold

The architecture-level theory then acquired a single candidate competence-investment value language. Rather than creating separate theories for whether, where, and organization, R1--R3 were recorded as three resolutions of one CIV comparison against a no-investment counterfactual. A minimal two-student/one-teacher/two-region specialization derives only its stated thresholds, reversals, boundaries, and null result.

This advances the integration scaffold without resolving the programme. Teacher buffering remains conditional, and the model does not establish practical value, novelty, RQ0, or P4.

## 20. Adversarial CIV stress test

The initial candidate strategy families were then subjected to an adversarial opening of the CIV exposure term. The resulting sequence was:

```text
initial candidate strategy families
    -> integrated CIV formulation
    -> analytical opening of L_a
    -> adversarial stress test
    -> rejection of nominal three-regime framing
    -> shift toward portfolio exposure and transformation value.
```

This did not show that named transformations are impossible. It showed that persistence values regime alignment rather than an action name, that dominance and null cases can remove actions, and that the minimal system gives REPLICATE and REBALANCE conditional mechanisms while leaving SPECIALIZE without a distinct system-level basis. SPECIALIZE was therefore parked as a fundamental regime rather than rejected as vocabulary. The return to portfolio exposure preserves the broader HLS object and records why the active theory no longer begins from a fixed strategy taxonomy.

## 21. Cross-domain foundation doctrine

The subsequent documentary consolidation made the research method explicit. The programme does not require novelty in every component, and adjacent work is not “occupied territory” merely because it contains a mechanism, equation, or terminology relevant to HLS. Established theory is an asset: understand it, reproduce it when useful, translate it to learning models, adapt it only where necessary, and seek system-level HLS consequences only where the translation requires them.

This corrected the immediate priority again. CIV and portfolio exposure remain model-scoped tools and historical audit outcomes, not the next central problem. The active work now proceeds through two parallel foundation lines: cross-domain theoretical extraction and minimal experimental reproduction of important transferable mechanisms. The programme-level object remains unchanged.

## 22. Pre-ontology position

The programme-level object remained HLS as an evolving distribution of competences: competence allocation could be a candidate system-level decision variable; operation determined current division of labour and could allocate formative experience; learning and transfer could change future competence allocation; and system value was conditioned on environment and horizon.

P1--P4, strategy families, cross-domain apparatus, minimal models, and CR0--CR4 were retained as subordinate layers. There was still no general HLS algorithm, realistic empirical validation, novelty claim, established P4, or general superiority result.

## 23. Two-beam reproduction, B13, and semantic correction

The foundation programme then organized current work around two questions: organization and use of available competences, and development/evolution of competence through experience. Garicano (2000) and Gutjahr (2011) supplied primary current references, while Arrow, Gibbons--Waldman, Argote--Miron-Spektor, and other verified lines supplied complementary foundations.

The B1/B2/B12 block reproduced selected source mechanisms and checked a minimal executable feedback. It did not establish benefit. B2.5 remained a failed source reproduction because Gutjahr's published Example 3 conclusion does not follow from its published parameters and equations. B12.4 supported only that allocation-induced experience can alter future allocation in the configured grid.

B13 subsequently combined source-shaped present and future terms and exposed a useful diagnostic distinction between present operational consequence and future experience-mediated value. It did not define scientifically strong joint and separate policy classes and did not prove RQ0. More importantly, it exposed that source variables with similar scalar forms could not be combined safely without semantic and dimensional mappings.

This led to the common HLS ontology and the methodological sequence:

```text
FOUNDATIONS -> REPRODUCTION -> ONTOLOGY -> TRANSFER -> ADAPTATION
    -> INTEGRATION -> SYSTEM -> DEMONSTRATED IMPROVEMENT.
```

Garicano and Gutjahr are therefore primary current references, not the theories of their beams. Allocation, real work, learning exposure, competence coverage, competence proficiency, and operational performance are kept distinct unless an explicit mapping relates them.

## 24. Current position

RQ0 remains the sole official research question in its current formulation:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

The central test is whether a meaningfully defined joint policy can strictly improve `J` relative to a scientifically strong separate-management policy, together with equality and no-advantage conditions. Weak dominance caused only by nesting the policy classes is not a scientific result.

The common ontology is modeling infrastructure, not the research objective. P1--P4, strategy families, cross-domain apparatus, CIV, B13, minimal models, CR0--CR4, controlled experiments, and realistic validation remain subordinate layers for understanding, testing, or refuting RQ0. There is no general HLS algorithm, realistic empirical validation, established novelty claim, established P4, or demonstrated superiority of joint management.
