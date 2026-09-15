# Cross-domain mathematical strategy for Heterogeneous Learning Systems

Date: 2026-09-15
Status: methodological orientation. This document imports possible apparatus and preserves the programme focus; it does not state a theorem, result, novelty claim, or new official research question.

## 1. Programme anchor

RQ0 remains the sole official research question:

> Can the deliberate evolution of competence allocation in a heterogeneous learning system improve its long-term performance compared with independently optimizing task allocation and knowledge transfer?

The scientific object is the complete Heterogeneous Learning System (HLS), not H1, P4, dual control, homogenization, routing-generated data, Label Switching, distillation, a teacher-student pair, or any other partial mechanism. Those may be diagnostic devices, adversaries, candidate mechanisms, or components of a later formulation.

The stable conceptual cycle is:

```text
heterogeneous learners
    -> task allocation / operation
    -> operational experience
    -> learning / knowledge transfer
    -> competence redistribution
    -> future task allocation / operation
```

The managed material is usable knowledge or competence distributed among heterogeneous learners. Learning is the mechanism that transforms that distribution. Operation gives it value.

## 2. Fundamental methodological correction

**Rule:** import mechanisms and mathematical tools; do not import or replace the HLS research problem.

Operations Research, portfolio management, economics, optimal and stochastic control, organizational science, sociology, human competence management, Machine Teaching, and continual learning are sources of mathematical machinery, mechanisms, hypotheses, theorem structures, and experimental designs. They are not alternative names for HLS.

Mathematical similarity does not imply scientific equivalence. The fact that another domain uses dynamic programming, marginal returns, competence states, resource constraints, specialization, learning-by-doing, depreciation, portfolio optimization, option value, or capacity planning does not establish that the corresponding HLS problem is solved.

Later novelty assessment must concern a concrete HLS proposition:

> Has substantially the same phenomenon or proposition already been established for the same, or a genuinely equivalent, class of learning systems under comparable assumptions?

The converse precaution is equally important: “A+B+C has not previously been combined” is not novelty by itself. Integration must produce a scientifically meaningful HLS property, explanation, capability, theoretical result, or empirical result.

## 3. System abstraction

The competence landscape remains a conceptual representation:

```text
C_t = [c_iz(t)].
```

Competence must not automatically be identified with accuracy. One possible later separation is:

```text
K_iz,t -> Q_iz,t = f_z(K_iz,t; theta_i).
```

Here `K` denotes knowledge or competence state and `Q` denotes operational capability. This can express heterogeneous learning curves, saturation, capacity ceilings, and different operational returns from similar competence increments.

A generic system sequence is:

```text
(C_t, D_t)
    -> operational decision r_t
    -> outcome + experience X_t
    -> learning decision a_t
    -> C_(t+1).
```

One conceptual transition form is:

```text
C_(t+1) ~ P_C(C_(t+1) | C_t, r_t, X_t, a_t, D_t).
```

One horizon objective form is:

```text
J^pi(C_0) = E^pi [ sum_t gamma^t (R(C_t, r_t, D_t) - K(a_t)) ].
```

Writing an MDP, Bellman equation, or constrained optimization problem is not a contribution. The science must be in the HLS structure, strategies, conditions, properties, and observed behaviour those expressions help analyse.

## 4. Importable apparatus by domain

### Portfolio management and finance

Useful apparatus includes diversification versus concentration, marginal return, risk, rebalancing, option value, portfolio interactions, and investing now for future return. In HLS, learning is an investment that changes the future competence portfolio.

### Operations Research

Useful apparatus includes scarce-resource allocation, capacity planning and expansion, scheduling, dynamic allocation, marginal values or shadow prices, decomposition, and Pareto optimization. These can clarify constraints and comparison classes without redefining HLS as a scheduling problem.

### Optimal and stochastic control

Useful apparatus includes state, action, value, dynamic programming, feedback, uncertainty, anticipatory control, path dependence, and separation conditions. Their role is to formulate when future consequences create a genuine coupling, not to make a generic control formulation look like an HLS result.

### Economics

Useful apparatus includes investment and return, opportunity cost, marginal utility, depreciation, option value, complementarity and substitutability, comparative advantage, and specialization. These can provide interpretable candidate conditions for competence allocation.

### Organizational science, sociology, and human competence management

Useful apparatus includes division of labour, specialization, organizational competence, redundancy, knowledge diffusion, individual versus collective capability, learning-by-doing, and competence depreciation. These are potentially useful analogies and mechanisms, not evidence about artificial learning systems.

### Machine learning

Useful apparatus includes heterogeneous learning curves, generalization, model capacity, transfer, distillation, Machine Teaching, continual learning, forgetting and interference, positive and negative transfer, teacher-recipient asymmetry, and endogenous experience or data generation. These specify physically meaningful competence transformations for HLS.

## 5. Gutjahr and related work as methodological sources

The Gutjahr line is a methodological source, not a prohibition against studying related structures in HLS.

**Gutjahr et al. (2010), “Multi-objective decision analysis for competence-oriented project portfolio selection,”** supplies candidate apparatus: explicit competence state, nonlinear competence-to-operational-efficiency mapping, learning-by-doing, knowledge depreciation, heterogeneous agents, resource and capacity constraints, competence trajectories, strategic competence development, and Pareto analysis.

**Gutjahr (2011), “Optimal dynamic portfolio selection for projects under a competence development model,”** is relevant for dynamic competence investment, specialization, mixed portfolios, and temporal trajectories.

**Heimerl–Kolisch** is relevant for work assignment, qualification of multi-skilled resources, and the relation between individual specialization and organization-level competence. **Loch–Kavadias** is relevant for dynamic portfolio allocation, marginal returns, and resource investment over time.

The purpose of studying these lines is valid HLS machinery, transferable theorem patterns, and HLS hypotheses to test. It is not to redefine HLS as project management, human-resource management, finance, or Operations Research.

## 6. Candidate mathematical apparatus

The following are candidate analytical tools, not validated HLS metrics or novelty claims.

### Marginal competence investment

```text
MR_iz(C) = (partial V / partial c_iz) * (partial c_iz / partial b_iz).
```

This separates system value of competence from the ability and cost of acquiring it.

### Portfolio-conditional marginal value

```text
MV_iz = V(C) - V(C without c_iz).
```

This directs attention to whether competence has value conditional on what the rest of the portfolio already provides.

### Candidate interaction measure

```text
I_ij,z = V(C + Delta_i + Delta_j) - V(C + Delta_i) - V(C + Delta_j) + V(C).
```

Such a quantity could help study complementarity, substitutability, or redundancy, subject to a defensible HLS value representation.

## 7. Competence trajectories and option value

The relevant object may be a trajectory rather than only a final state:

```text
C_0 -> C_1 -> ... -> C_T.
```

Learning costs occur now while operational benefit can occur later. This makes transient trajectories scientifically relevant.

A candidate option-value decomposition is:

```text
V_competence = V_current_exploitation + V_future_option.
```

A competence that is presently redundant or lightly used may nevertheless provide fallback capacity, lower future inference cost, latency, availability, robustness, value under uncertain demand, a prerequisite for later learning, or future transfer opportunities.

The candidate mechanism `C_t -> A(C_t)` states that current knowledge may change the space of future learning actions. It is a hypothesis or mechanism candidate, not an established result.

## 8. Candidate evolution strategies

The following initial families are neither exhaustive nor claimed novel.

| Strategy | Candidate transformation | Question to analyse |
| --- | --- | --- |
| **SPECIALIZE** | Concentrate learning to produce specialists. | When do concentration and comparative advantage outweigh lost breadth? |
| **BROADEN** | Increase breadth or coverage of one or more learners. | When does broader coverage create operational value rather than diluted competence? |
| **REPLICATE** | Create a competence in another learner despite existing coverage. | When is redundancy useful for cost, latency, availability, robustness, or option value? |
| **REBALANCE** | Change who holds which competences. | When should demand, costs, availability, opportunities, or objectives alter the distribution? |

## 9. Provisional management philosophies

These are future comparison categories, not benchmarks or algorithms.

| Label | Philosophy |
| --- | --- |
| S0 | No competence evolution. |
| S1 | Reactive learning: repair or adapt after observed operational need or failure. |
| S2 | Local learner improvement: select learning actions by individual or local benefit. |
| S3 | Greedy portfolio-value evolution: select changes by current system-level value. |
| S4 | Long-horizon deliberate competence evolution: reshape the landscape by expected future system utility. |

## 10. Families of theoretical results to seek

The agenda includes specialization conditions; breadth or collective-coverage conditions; replication or useful-redundancy conditions; transfer conditions; rebalancing conditions; anticipatory-learning conditions; path-dependence conditions; and separation or coupling conditions.

Separation and coupling remain subordinate to RQ0. P4 is not the programme. Results should explain HLS behaviour, not restate tautologies such as “learning is useful when benefit exceeds cost.”

## 11. Null cases and adversaries

Deliberate competence evolution may add no value when competence acquisition is free or has no trade-offs; future information is complete and the portfolio can be chosen optimally ex ante; competence transitions are independent of operation; learning cannot change future operational decisions; a frozen portfolio is sufficiently rich; or a fully informed modular controller equals a joint controller.

These null cases delimit when the HLS problem genuinely appears. In particular:

```text
P1 + P2 + P3 does NOT imply P4.
```

## 12. Literature protocol

Each important paper must yield two distinct products.

### A. Reusable apparatus

Extract the state representation, transition law, objective, constraints, marginal or optimality conditions, decomposition, theorem structure, uncertainty treatment, experimental design, and metrics. Then ask how each item translates to HLS.

### B. Scientific constraint

Record the exact phenomenon established, domain or system class, assumptions, evidence, what is actually demonstrated, and what the paper does not establish for HLS.

Reusable apparatus is not a novelty barrier.

## 13. Epistemic and experimental discipline

Maintain the categories **ESTABLISHED**, **SUPPORTED / INFERENCE**, and **HYPOTHESIS**. A cross-domain analogy or mathematical resemblance does not turn an HLS hypothesis into a fact.

Before programming an experiment, specify:

1. the HLS proposition being tested;
2. what outcome supports it;
3. what outcome weakens it;
4. what is inconclusive;
5. the strongest adversarial baseline;
6. resource and information matching;
7. confounds; and
8. why the system exposes the mechanism.

Always separate experimental outcome from experimental validity. When appropriate, prefer:

```text
minimal theory
    -> controlled synthetic falsification
    -> realistic HLS benchmark
    -> robustness / ablation / adversarial tests.
```

This sequence is not mechanical: theory or counterexamples can kill a hypothesis earlier.

## 14. Anti-drift rules

- RQ0 remains the anchor.
- Think at system level.
- Do not over-focus on small pieces because they are mathematically tractable.
- Use other domains aggressively.
- Import mechanisms, not problems.
- Mature mathematics is an asset, not a threat.
- Do not demand novelty of every component.
- Do not claim novelty from mere combination.
- Do not equate mathematical similarity with scientific equivalence.
- Do not invent mathematics by inertia.
- Do not program prematurely.
- Adversarial reviewers attack claims; they do not choose the programme.
- Preserve whole-system HLS focus.

## 15. Immediate research direction

The methodological sequence is:

1. Define a minimal HLS competence landscape and operational value.
2. Define a small set of physically meaningful learning transformations.
3. Import appropriate marginal-value and dynamic-investment mathematics.
4. Analyse specialize, broaden, replicate, and rebalance regimes.
5. Search for non-trivial conditions, null cases, and counterexamples.
6. Compare deliberate long-horizon evolution with strong frozen, reactive, and local alternatives.
7. Only then ask which coupling, information, or algorithmic machinery is required.

The desired outcome is not a generic resource-allocation model with ML labels. It is theory and an experimental programme explaining how the distribution of usable knowledge in a heterogeneous learning system should evolve, why, and with what consequences for future system performance.

## 16. Final principle

```text
knowledge / competence is the managed material
learning is the transformation mechanism
heterogeneity defines the portfolio
operation gives competence value
time makes competence investment meaningful
the whole HLS determines the scientific objective
```

Use any mathematics that helps answer the HLS question. Do not confuse the origin of a mathematical tool with the domain of the scientific contribution.
