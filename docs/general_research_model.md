# General research model for Heterogeneous Learning Systems

Date: 2026-09-15
Status: programme-level orientation. This document consolidates the general HLS research model above any particular minimal model, mechanism, or experiment. It does not introduce an official research question, theorem, empirical result, or novelty claim.

## 1. Programme anchors

> “An HLS should be viewed not only as a heterogeneous portfolio to be exploited, but as an evolving distribution of competences.”

> “Operational decisions determine not only who performs current tasks, but potentially who gains the experience that shapes future competence; learning and knowledge-transfer decisions provide additional mechanisms for changing that distribution.”

> “The central question is therefore whether deliberately shaping who will be competent at what can create greater long-term system value than simply optimizing the use and local improvement of the competences available today.”

These anchors identify the scientific object as the whole **Heterogeneous Learning System (HLS)**. They do not elevate a routing heuristic, teacher--recipient pair, knowledge-transfer method, control formulation, or mathematical mechanism to the centre of the programme.

## 2. RQ0 and scope

RQ0 remains the sole official research question:

> Can the deliberate evolution of competence allocation in a heterogeneous learning system improve its long-term performance compared with independently optimizing task allocation and knowledge transfer?

This document does not change RQ0 or promote H1, P1--P4, or any other proposition to official-question status. It provides a programme-level interpretation of deliberate evolution of competence allocation.

An HLS contains heterogeneous learners, models, agents, or other operational units. Their heterogeneity can concern capability, cost, latency, specialization, learnability, availability, or roles in learning and knowledge transfer. The programme is concerned with the distribution of usable competence over this heterogeneous population, rather than only with an isolated learner.

## 3. General system model

The competence landscape remains a provisional conceptual representation:

```text
C_t = [c_iz(t)].
```

Here `c_iz(t)` denotes effective competence of learner `i` in task region or family `z` at time `t`. It need not be directly observable and must not automatically be identified with a single accuracy measure. It is a way to reason about a distributed system state, not a final sufficient-state claim.

**Competence allocation** is the distribution of usable competences across learners. It is a possible system-level decision variable: an HLS may affect it through operational allocation, learning, knowledge transfer, retention, or other physically meaningful competence transformations. Whether and when it should be treated as controllable is part of the research problem.

The stable conceptual cycle is:

```text
competence allocation
    -> operational division of labour
    -> operational experience
    -> learning / knowledge transfer
    -> future competence allocation.
```

The corresponding generic sequence is:

```text
(C_t, D_t)
    -> operational decision r_t
    -> outcome + experience X_t
    -> learning / transfer decision a_t
    -> C_(t+1).
```

The environment, demand process, available resources, and horizon condition system value. A competence distribution has no programme-level value in isolation: its value depends on how it supports future operation in a specified environment and over a specified horizon. Generic state-transition or control notation can clarify this dependency, but writing an MDP, Bellman equation, or optimisation problem is not a scientific contribution by itself.

## 4. Collective competence and learning as transformation

The relevant object is **collective competence**: what the portfolio can achieve, at what operational cost and under what constraints, given how competences are distributed. This entails:

```text
individual failure        != portfolio competence deficit
individual improvement    != collective system improvement.
```

A learner can gain a competence that the portfolio already has at lower cost elsewhere; alternatively, the same gain can create useful coverage, redundancy, specialization, or an option for later operation. The system value of local learning is therefore conditional on the rest of the portfolio, its environment, and its future use.

Learning is the transformation mechanism for distributed competence. Operational experience can shape learning opportunities; explicit transfer, training, or teaching can provide additional means to change who becomes competent at what. This does not assume that every operational decision changes competence, that every learning action succeeds, or that any particular transfer mechanism is universally relevant.

## 5. From exploitation to deliberate evolution

An HLS may simply exploit the competences available today: route each task to a currently preferred learner and improve learners by local criteria when an opportunity arises. Deliberate competence evolution asks a different, longer-horizon question: should current operation and learning choices be selected partly because they alter a future division of labour with greater system value?

This is not a presumption that evolution is beneficial. A sufficiently rich frozen portfolio, a strong adaptive router, free competence acquisition, complete information, or a controller that captures all relevant cross-information can remove its advantage. Such null cases and strong adversaries are part of the programme, not exceptions to be hidden.

## 6. Candidate strategy families

The following initial families are neither exhaustive nor claims that each is independently useful in HLS.

| Family | Programme-level meaning | Question to be tested later |
| --- | --- | --- |
| **SPECIALIZE** | Concentrate learning so a learner becomes relatively strong in selected regions. | When does concentration improve collective operation rather than merely redistribute local performance? |
| **BROADEN** | Extend a learner's or group's coverage across regions. | When does broader coverage create value under the relevant demand and constraints? |
| **REPLICATE** | Create competence in an additional learner despite existing coverage. | When does redundancy yield value through cost, latency, availability, robustness, or future options? |
| **REBALANCE** | Change which learners hold which competences as conditions change. | When do demand, costs, availability, opportunities, or objectives justify a different distribution? |

These families are a vocabulary for possible trajectories, not a benchmark suite or a prescribed policy taxonomy.

## 7. P1--P4 as subordinate scaffolding

P1--P4 are provisional scaffolding for making RQ0 testable. They are not a replacement programme and none is promoted here.

- **P1 — Collective competence:** local failures and learning gains must be evaluated relative to the whole portfolio.
- **P2 — Local--collective misalignment:** a locally preferred learning action can differ from the action with greater downstream portfolio value.
- **P3 — Evolution versus frozen routing:** deliberate competence evolution may be compared with a strong frozen heterogeneous portfolio and adaptive routing.
- **P4 — Coupling advantage:** a candidate, stronger question about whether a coupled controller can exceed a comparably informed modular alternative.

P4 is expressly not established by this programme-level model. A result showing that a mixed or coupled action is optimal in a restricted model does not show that a fully informed modular controller cannot reproduce it.

## 8. Role of the minimal theory and CR0--CR4

[`theory_competence_evolution_minimal_model.md`](theory_competence_evolution_minimal_model.md) and its CR0--CR4 statements are **consistency and falsification evidence** for the plausibility of parts of the programme. They expose explicit null cases, threshold effects, specialization dynamics, and simple rebalancing identities under deliberately restrictive assumptions.

They are not the centre of HLS, a definition of the general model, or claims about general HLS behaviour. Their statuses remain those recorded in that audited document: established only in the stated model and, where indicated, numerically verified as implementation checks. They do not establish novelty, P4, practical value, or transfer to real learning-system portfolios.

## 9. Experimental programme and falsification

Any future experiment should begin with a proposition about the whole HLS, rather than with an available implementation mechanism. Before programming, specify:

1. the HLS proposition being tested;
2. what outcome supports it, weakens it, or is inconclusive;
3. the strongest adversarial baseline;
4. matched resources and information;
5. plausible confounds; and
6. why the chosen system exposes the proposed mechanism.

When appropriate, the preferred sequence is:

```text
minimal theory
    -> controlled synthetic falsification
    -> realistic HLS benchmark
    -> robustness, ablation, and adversarial tests.
```

The sequence is not mechanical: a null case, counterexample, or literature result can redirect or stop a line earlier. Experimental outcome and experimental validity must remain distinct.

The programme should be substantially redirected if fair comparisons show no meaningful conditions in which changing the competence distribution improves long-horizon system value beyond strong frozen, reactive, local-improvement, or fully informed modular alternatives. It should also be redirected if the needed competence state, transitions, or value comparison cannot be specified without assumptions that make the question vacuous or operationally irrelevant.

## 10. Programme discipline

- Keep RQ0 as the anchor and reason at the level of the whole HLS.
- Treat mature mathematics and adjacent fields as apparatus to import, not as territory that removes the HLS question.
- Do not infer novelty from a combination of known components, and do not infer problem closure from mathematical or terminological resemblance.
- Do not elevate a tractable mechanism, including CR0--CR4, reachability, routing-generated data, or a teacher--student pair, into the programme objective.
- Do not programme before the proposition, adversary, information comparison, and falsification conditions are explicit.

## 11. Current direction

The immediate direction is to preserve a system-level account of how the distribution of usable knowledge can evolve and to identify small, physically meaningful competence transformations and environments in which that evolution has testable consequences. The focus is on conditions, null cases, and strong comparisons for deliberate evolution as a whole, not on expanding one mechanism by inertia.

The current integration scaffold is the [integrated competence-investment model](theory_integrated_competence_investment_model.md). It uses CIV as a candidate common value language for whether to invest, where to intervene, and what competing portfolio transformation to select. Its thresholds, ranking-reversal construction, and pairwise boundaries are derived only under its stated specialization; they do not promote CIV to a programme-level result or a final controller.

The intended scientific outcome is not a generic resource-allocation model with machine-learning labels. It is a theory and experimental programme that can explain how the distribution of usable knowledge in a heterogeneous learning system should evolve, why, and with what consequences for future system performance.

## 12. Final principle

```text
knowledge / competence is the managed material
learning is the transformation mechanism
heterogeneity defines the portfolio
operation gives competence value
time makes competence investment meaningful
the whole HLS determines the scientific objective.
```

Use any mathematics that helps answer the HLS question. Do not confuse the origin of a mathematical tool with the domain of the scientific contribution.
