# HLS Synthetic Environment — Generative Experimental Framework for RQ0

**Status: DESIGN / NOT YET IMPLEMENTED**

## 1. Purpose and scientific role

The HLS Synthetic Environment is a configurable, falsifiable family of worlds
for studying mechanisms, boundaries, and limitations relevant to RQ0. It is not
a theory, an HLS policy, evidence, or a claim that joint management is useful.
Its purpose is to make causal structure manipulable before returning to more
realistic synthetic systems and real datasets.

RQ0 remains exactly:

> Can the dynamic allocation and development of competences in a heterogeneous learning system improve long-term system performance compared with architectures that manage task allocation and knowledge transfer separately?

The experimental objects are strictly separated:

| Object | Role |
| --- | --- |
| RQ0 | Canonical research question; unchanged by this design. |
| Current theory | Supplies definitions, derived boundaries, and predictions to test. |
| World generator | Produces valid environments from declared parameters. It is not theory by definition. |
| Policies | Act in a common generated world under declared information and coordination contracts. |
| Results | Future derived or observed comparisons; none exist yet for this framework. |

The intended progression is:

```text
controlled synthetic HLS environment
    -> exact/minimal experiments
    -> phase/boundary experiments
    -> adversarial capability/limit experiments
    -> realistic synthetic instantiation
    -> real datasets
```

This is a conditional scientific ladder, not a commitment to complete every
stage. The generator must not encode `HLS > SEP`, and no parameter point may be
chosen merely to make HLS win.

## 2. Canonical anchors and scope

The environment is intended to test, not redefine:

- P1 (collective competence) and P2 (local--collective misalignment) from the
  [general research model](../general_research_model.md);
- the two beams and their mappings in the [HLS ontology](../hls_ontology.md)
  and [two-beam theory](../theory/two_beam/README.md);
- the equivalence and reducibility boundaries in the
  [minimal HLS model](../theory/minimal_hls_model.md);
- canonical opportunity value `Omega` and portfolio interaction `Gamma` from
  [operational-development opportunity value](../theory/operational_development_opportunity_value.md);
- strong separated management and sufficiently coordinated separated
  architectures, including the experimental `SEP-Omega` comparison.

These definitions remain authoritative. Any future protocol must state its
exact mapping to them rather than silently changing their meaning. This design
makes no novelty claim and does not promote P1 or P2 to official research
questions.

## 3. Parametric world family

Define an environment family

\[
\mathcal E(\Theta),
\qquad
\Theta=(\Theta_Q,\Theta_C,\Theta_O,\Theta_D,
        \Theta_R,\Theta_K,\Theta_I),
\]

where:

| Block | Controls |
| --- | --- |
| `Theta_Q` | task-arrival process |
| `Theta_C` | competence structure and initial geometry |
| `Theta_O` | experience/opportunity-generation mechanism |
| `Theta_D` | competence-development dynamics |
| `Theta_R` | operational reward/performance |
| `Theta_K` | costs, capacities, and budgets |
| `Theta_I` | information and coordination available to policies |

The blocks must be independently manipulable whenever their combination
defines a mathematically valid world. Validity constraints, admissible ranges,
and dependencies must be explicit in each future protocol. No block may contain
a hidden policy-specific reward, dataset, or transition advantage.

`WORLD` and `POLICY` are separate objects. `Theta` defines the former; a policy
contract defines how an architecture may observe and act in it.

## 4. System and competence state

The basic family has `M` learners/resources and `K` competence/task dimensions:

\[
S_t=[c_{ik,t}]\in[0,1]^{M\times K}.
\]

`S_t` represents the collective distribution of competences, not a list of
independent scalar rewards. The basic bounded matrix is an initial realization,
not a claim that competence is always directly observed or sufficiently
represented by one scalar per learner and task. Later levels may replace or
augment it with structured, latent, uncertain, capacity-dependent, or
history-dependent state while preserving an explicit mapping to the canonical
ontology.

The generator must support initial geometries including:

- homogeneous;
- redundant;
- complementary;
- specialist;
- generalist;
- mixed;
- dominated portfolios;
- non-dominated portfolios.

Heterogeneity is not defined as numerical variance alone. Equal variance can
hide different coverage, dominance, complementarity, specialization, cost, or
capacity structures. A future experimental question is which properties of
competence geometry—not merely competence magnitude—matter for RQ0.

## 5. Task process

Tasks arrive according to

\[
q_t\sim P_Q(\cdot\mid h_t;\Theta_Q),
\]

where `h_t` is the declared world history available to the process. The minimal
family may use discrete types

\[
k_t\in\{1,\ldots,K\},
\qquad k_t\sim p(k)
\]

for the initial analytical configuration. The contract must later admit:

- stationary arrivals;
- non-stationary arrivals;
- Markov or context-dependent arrivals;
- fixed finite task sequences;
- feature-bearing tasks `x_t` generated by task-specific distributions.

Task realizations are part of the world, not selected separately for each
policy.

## 6. Two distinct actions and two beams

Every environment realization must distinguish:

\[
a_t=\text{operational allocation/use decision},
\qquad
d_t=\text{competence-development decision}.
\]

It must be possible that `a_t != d_t`. The framework must not automatically
make the task executor the learner, recipient, or teacher. Any equality between
the actions must be an explicit special-case assumption.

- **Beam 1 — organization/use/allocation of existing competences:** who does
  what.
- **Beam 2 — development/evolution of competences:** who learns what and from
  whom.

Opportunity generation and the interface between these beams do not constitute
a third beam.

## 7. Opportunity kernel

Operational decisions may produce development resources through

\[
O_t\sim P_O(\cdot\mid S_t,q_t,a_t,h_t;\Theta_O).
\]

`O_t` may contain experience, information, labels, feedback, teaching
opportunities, or other declared development resources. Opportunity is not
development: observing `O_t` neither changes competence nor obliges a policy to
use it. The no-use development action must remain available when required by
the mapped theory.

Introduce a conceptual coupling family indexed by `rho`, without fixing one
artificial formula. In a decoupled limit `rho=0`, the family must be able to
satisfy

\[
P(O_t\mid S_t,q_t,a_t)=P(O_t\mid S_t,q_t).
\]

For `rho>0`, opportunity availability, content, timing, or value may depend on
`a_t`. The meaning and range of `rho` must be declared before comparative
outcomes are observed.

## 8. Development and transition kernel

Competence evolves only through an explicit transition contract:

\[
S_{t+1}\sim P_D(\cdot\mid S_t,O_t,d_t;\Theta_D).
\]

The family should progressively admit:

- no learning;
- independent learning;
- diminishing returns and saturation;
- heterogeneous learning rates;
- positive transfer;
- negative transfer/interference;
- forgetting/depreciation;
- finite competence capacity;
- stochastic development;
- asymmetric transfer.

Some configurations may use an interaction/transfer matrix
`L=[lambda_kl]`, but `L` is not a universal requirement. The explicit negative
control `eta=0` must produce no competence change from development.

## 9. Reward, cost, and constraints

For finite or discounted horizon, evaluate a policy `pi` through

\[
J(\pi)=\mathbb E_\pi\left[
  \sum_{t=0}^{T} \beta^t R(S_t,q_t,a_t,d_t)
\right].
\]

The implementation contract must separately expose:

- operational utility/performance;
- operational cost;
- development cost;
- capacity/resource cost.

`beta`, development cost `kappa`, operational costs, development budgets, and
capacity constraints must be controllable without redefining competence.
Future protocols must state whether costs enter `R`, constraints, or both and
must prevent double counting.

## 10. Information and coordination structure

`Theta_I` is a first-level experimental dimension. Different architectures must
operate on exactly the same generated world while receiving only the
information and coordination authorized by their contracts. At minimum the
framework must later support:

- `HLS`;
- strong `SEP`;
- `SEP-Omega`;
- an oracle/reference optimum when exact computation is possible.

This document specifies interfaces only; it does not implement or finalize
these policies.

### HLS contract

`pi_HLS` jointly evaluates the long-horizon consequences of `a_t` and `d_t`
under its declared information set. This does not guarantee that a tested HLS
policy is optimal or superior.

### Strong SEP contract

\[
\pi_{SEP}=(\pi_A,\pi_D)
\]

uses separate operational and development modules. SEP must not be made weak by
construction. Relative to HLS it receives the same learners, task realization,
costs, capacities, development mechanisms, and relevant compute budget, plus
the observable state authorized by its architecture. The comparison concerns
separation of management, objectives, or information—not artificial resource
or data handicaps.

### SEP-Omega contract

SEP-Omega is a separated architecture whose operational module receives
sufficient continuation-value information `Omega(S,q,a)` when that object is
well-defined under the mapped canonical model. The framework must test, rather
than hard-code, conditions under which

\[
J_{HLS}=J_{SEP\text{-}Omega}.
\]

Policy definitions and tie rules must be frozen before outcomes are inspected.

## 11. Common world and common randomness

Policies must be evaluated on the same generative world. When mathematically
valid, comparisons use paired realizations/common random numbers:

- identical initial states;
- identical task arrivals;
- identical policy-independent stochastic shocks;
- identical `world_seed`.

The implementation must distinguish policy-independent exogenous randomness
from policy-dependent endogenous transitions. Pairing does not mean forcing
endogenous trajectories to coincide after policies choose different actions;
it means coupling their exogenous randomness under an explicit counterfactual
construction. A policy may not receive a more favorable dataset or shock
sequence.

## 12. Required generative regimes

### Regime I — Irrelevant development

Set `eta=0`. Expected diagnostic: development cannot create competence value.
Any apparent gain must come from another declared channel or indicates an
implementation/semantic error.

### Regime II — Separable learning

Learning exists, but operational choices do not materially alter future
development opportunities and the required additivity/independence assumptions
hold. The theoretical target is

\[
J_{HLS}=J_{SEP}.
\]

This equality is conditional on those assumptions, not a universal property of
all worlds with `rho=0`.

### Regime III — Coupled allocation/development

Operational choices affect future development opportunities or their value. A
possible outcome is `J_HLS > J_SEP`, but this is not guaranteed by generator
construction. The family must also admit equality, no advantage, and cases in
which a tested HLS policy loses to strong SEP.

### Regime IV — Coordinable coupling

Coupling exists, but a separated architecture receives sufficient continuation
value or coordination information. Under the corresponding derived
reducibility conditions, the target boundary is

\[
J_{HLS}=J_{SEP\text{-}Omega}.
\]

The equality must emerge from the world and policy contracts, not an assertion
in code.

## 13. Adversarial capability and limits

Without making them mandatory A1a mechanisms, the architecture should later be
extensible to:

- non-stationary demand;
- partial observation and noisy estimates of competence;
- perishable opportunities;
- shared resource constraints;
- learner downtime during development;
- transfer and interference;
- competence depreciation and finite capacity;
- portfolio interaction;
- stochastic development;
- delayed feedback;
- history-dependent opportunities.

These capabilities exist to attack assumptions and delimit the theory, not to
decorate a favorable example.

## 14. Omega and Gamma diagnostics

When mathematically meaningful under the canonical definitions, the environment
should permit derivation or measurement of

\[
\Omega(S,q,a)
\]

as the incremental continuation value associated with development
opportunities available after an operational action, and portfolio interaction

\[
\Gamma_{ij}(S)=
V(S+\Delta_i e_i+\Delta_j e_j)
-V(S+\Delta_i e_i)
-V(S+\Delta_j e_j)
+V(S).
\]

Neither quantity is an artificial reward inserted into the world. `Gamma` may
be positive, zero, or negative. There is one important canonical constraint:
the current opportunity-value note defines `Omega` using a maximization that
includes a no-use action and therefore derives `Omega >= 0`. This environment
does not redefine canonical `Omega` as signed. A signed action-specific
continuation increment may be recorded under a different explicit name; it must
not silently be called `Omega`. Operational actions can nevertheless differ in
`Omega`, and those differences may favor or disfavor a route relative to its
immediate operational reward.

## 15. Conditional complexity ladder

| Level | Intended scope |
| --- | --- |
| **L0 — Analytical** | `M=2`, `K=2`, `T=2/3`; exact enumeration or dynamic programming. |
| **L1 — Controlled portfolio** | Approximately `M=3`, `K=3`; longer horizon, heterogeneity, development, coupling, and phase maps. |
| **L2 — Interaction** | Transfer/interference, `Gamma`, capacity, and forgetting. |
| **L3 — Dynamic/adversarial world** | Nonstationarity, partial information, stochastic development, perishable opportunities, and delays. |
| **L4 — Synthetic-realistic** | Feature-generating distributions `P_k(x)` and actual incremental classifiers/regressors. |

Real datasets follow only after the ladder identifies mechanisms worth testing.
Progression is conditional on scientific value; a null result, reduction, or
invalid mechanism may stop or redirect it.

## 16. Future experimental outputs

Future runs should be able to record:

\[
J_{HLS},\quad J_{SEP},\quad J_{SEP\text{-}Omega},\quad
\Delta_{joint}=J_{HLS}-J_{SEP},
\]

with trajectories

\[
(S_0,\ldots,S_T),\quad(a_0,\ldots,a_T),\quad
(d_0,\ldots,d_T),\quad(O_0,\ldots,O_T).
\]

Declared output components should include operational reward, development cost,
total cost, competence evolution, routing distribution, development allocation,
`Omega` and `Gamma` when computable, and regret/reference gap when an exact
oracle exists.

The principal scientific object should become phase and boundary maps, for
example

\[
\Delta_{joint}(\rho,\eta),\qquad
\Delta_{joint}(H_C,\rho),\qquad
\Delta_{joint}(\kappa,\beta),
\]

where `H_C` must receive a protocol-specific, non-ambiguous definition of
competence geometry. A single favorable performance table is insufficient.

## 17. FALSIFICATION AND ANTI-CONFIRMATION RULES

1. Never choose one parameter point because HLS wins there.
2. Define parameter families and ranges before observing comparative outcomes.
3. Include negative controls.
4. Include separable regimes.
5. Include dominated and non-dominated competence portfolios.
6. Report equality and no-advantage regions.
7. Report cases where tested HLS policies lose.
8. Do not alter the world generator after seeing HLS-versus-SEP results without
   declaring a new protocol/version.
9. Distinguish `DERIVED-IN-MODEL`, `OBSERVED`, `REPRODUCED`, `NULL`, and
   `INCONCLUSIVE`.
10. Synthetic evidence establishes existence, mechanism, and boundaries only
    inside the modeled family; it does not establish prevalence in real systems.
11. A positive synthetic result is meaningful only if the positive region has
    non-zero, robust extent and is not a single constructed point.
12. Negative controls predicted by theory must behave correctly before a
    positive result is interpreted as support.

The same frozen world family must expose positive, equality, negative, and
failure regions when its declared structure permits them.

## 18. Initial A1a contract — DO NOT IMPLEMENT

The first intended configuration is A1a:

- `M=2`, `K=2`;
- `T=2` initially, then `T=3` only if scientifically warranted;
- a `2 x 2` competence matrix;
- discrete task types;
- exact finite-horizon solution;
- a simple bounded learning transition;
- no transfer;
- no forgetting;
- no partial observation;
- no neural networks;
- no real features.

A1a will compare exact HLS, strong SEP, and SEP-Omega policies. Its purposes are
to verify mathematical semantics, policy definitions, negative controls, and
the mechanism producing or removing `Delta_joint`, and to test agreement
between analytical reasoning and eventual code. It is not final empirical
evidence.

The required hand-solvable `T=2` audit is recorded below. It authorizes the
next implementation-design step only; it does not authorize code or experiments.

## 19. A1a pre-implementation mathematical audit

**Status: AUDITED FOR IMPLEMENTATION / NOT YET IMPLEMENTED**

This section records model-scoped requirements for A1a. They are not general
claims about HLS, SEP, or RQ0 outside the stated `T=2` model.

### 19.1 Minimal T=2 model and causal construction

A1a begins with two learners (`M=2`), two competence/task dimensions (`K=2`),
and two decision periods (`T=2`). Given initial state `S_0` and first task
`q_0`, the operational action is

\[
a_0\in\{1,2\}.
\]

Let `r(a)` be the immediate operational value of action `a`. After operation,
the world generates an opportunity `O(a)` through the opportunity kernel. A
development action `d` may use or decline that opportunity, producing `S_1`
through the development kernel. The final value is `V_1(S_1)`.

Define the optimally exploitable future/development value after action `a` as

\[
G(a)=
\max_{d\in\mathcal D(O(a))}
\mathbb E\!\left[
  -\kappa(d)+\beta V_1(S_1)
  \mid S_0,q_0,a,d
\right].
\]

`G(a)` is **DERIVED-IN-MODEL** from primitive kernels, costs, and continuation
value. It is not a configurable bonus. The only admissible causal chain is

```text
a -> O -> d -> S' -> V(S')
```

and never `a -> manually specified HLS bonus`.

### 19.2 Joint HLS and strong SEP

The exact joint choice is

\[
a_{HLS}\in\arg\max_a\{r(a)+G(a)\}.
\]

Let `h` be an operationally optimal action:

\[
h\in\arg\max_a r(a).
\]

Strong SEP selects its operational action from the immediate operational
objective,

\[
a_{SEP}\in\arg\max_a r(a),
\]

then, after its actual opportunity is generated, solves the development
subproblem optimally. SEP development is therefore neither heuristic nor made
weak by construction. If the immediate operational optimum `h` is unique,

\[
J_{SEP}=r(h)+G(h),
\qquad
J_{HLS}=\max_a\{r(a)+G(a)\}.
\]

Operational ties must be exposed and handled by a rule frozen before outcomes
are inspected. The eventual specification must either compare all admissible
SEP tie resolutions or predeclare one; it must not inherit arbitrary iteration
or `argmax` ordering. If continuation information is used to resolve a SEP
operational tie, that coordination must be declared explicitly.

### 19.3 Exact T=2 switch condition

For an alternative operational action `s` relative to immediate optimum `h`,
define

\[
\delta_R=r(h)-r(s)\geq0,
\qquad
\delta_G=G(s)-G(h).
\]

Then HLS strictly prefers `s` over `h` exactly when

\[
\boxed{\delta_G>\delta_R},
\]

or equivalently

\[
G(s)-G(h)>r(h)-r(s).
\]

The future/development advantage must exceed the present operational sacrifice.
At `delta_G=delta_R`, the actions are value-equivalent for HLS; no strict
advantage may be claimed. This is the minimal finite-horizon form of the
present-sacrifice/future-value condition already bounded by the
[canonical minimal model](../theory/minimal_hls_model.md) and the
[operational-development opportunity-value theory](../theory/operational_development_opportunity_value.md).
It does not replace either result.

### 19.4 Analytical negative control: operation-independent opportunities

**A1a proposition — operation-independent opportunity equivalence.** Assume

\[
P_O(O\mid S,q,a)=P_O(O\mid S,q),
\]

and, once `S,q,O,d` are fixed, the development/transition mechanism and
continuation value have no additional direct dependence on `a`. Then the
feasible development problem has the same conditional distribution for every
operational action, so

\[
G(a)=G\quad\text{for all }a.
\]

Therefore

\[
\arg\max_a\{r(a)+G\}=\arg\max_a r(a)
\]

and, subject to the stated assumptions and explicit tie handling,

\[
\boxed{J_{HLS}=J_{SEP}}.
\]

This is an analytical **NEGATIVE CONTROL**, not evidence against RQ0. It must
become a mandatory implementation test.

### 19.5 Analytical negative control: no learning

If `eta=0`, or more generally no admissible development action can change
future competence or value, development creates no differential continuation
value. Provided there is no other action-dependent continuation channel in the
A1a world,

\[
\boxed{J_{HLS}=J_{SEP}}.
\]

This is also a mandatory implementation test.

### 19.6 Coupled positive, equality, and no-advantage regions

A strict HLS-versus-SEP advantage is **possible** when operational actions
generate different optimally exploitable future/development values and
`delta_G>delta_R`. Coupling is necessary for this minimal switching mechanism,
but it is not sufficient for strict advantage. Primitive world parameters must
be able to produce, rather than directly configure,

\[
\delta_G<\delta_R,
\qquad
\delta_G=\delta_R,
\qquad
\delta_G>\delta_R.
\]

The first region retains the immediate operational optimum; the second is a
value boundary; only the third supports the strict switch. A coupled world may
therefore yield equality or no joint advantage.

### 19.7 Canonical Omega constraint

This audit does not redefine `Omega`. The canonical theory includes a no-use
action and derives

\[
\Omega(S,q,a)\geq0
\]

under its stated definition. `Omega` is derived from continuation/development
value and is not an artificial environmental reward. It must not be used as a
generic signed difference between operational actions. Signed comparisons must
instead use an explicitly distinct quantity, such as
`Delta_V(a,s)`, or the audit quantity

\[
\delta_G=G(s)-G(h).
\]

### 19.8 SEP-Omega consistency target

If a separated operational module receives the exact sufficient continuation
value associated with each operational action, then under the corresponding
reducibility assumptions it should make the same operational choice as the
joint solution. A1a must therefore permit HLS and SEP-Omega to be solved
independently and test the target condition

\[
\boxed{J_{HLS}=J_{SEP\text{-}Omega}}
\]

when those assumptions hold. SEP-Omega must not be implemented as an alias or
shared return path for HLS; equality is an outcome to verify.

### 19.9 Required analytical test matrix

These are model-derived expectations, not fitted empirical hypotheses:

| Case | Construction | Required expectation |
| --- | --- | --- |
| A — No learning | `eta=0` | `HLS = SEP`. |
| B — Operation-independent opportunity | `O` conditionally independent of `a` under the assumptions above | `HLS = SEP`. |
| C — Coupled, insufficient future value | `delta_G < delta_R` | HLS retains the immediate operational optimum; no strict switching advantage. |
| D — Boundary | `delta_G = delta_R` | HLS is indifferent between the relevant actions; no strict advantage claim. |
| E — Coupled, sufficient future value | `delta_G > delta_R` | The joint optimum may sacrifice immediate value and can strictly exceed strong SEP. |
| F — Exact sufficient continuation information | independently solved SEP-Omega | `HLS = SEP-Omega` under the reducibility assumptions. |

All six cases must pass before a positive A1a result is interpreted.

### 19.10 A1a anti-triviality rules

1. `G(a)` cannot be configured directly.
2. `delta_G` cannot be configured directly.
3. HLS advantage cannot be injected as a reward bonus.
4. Opportunity generation is policy-independent world structure.
5. HLS and SEP receive the same world realization under paired/common
   randomness whenever valid.
6. SEP development is solved optimally after receiving its actual opportunity.
7. Do not choose `S_0` or opportunity parameters after inspecting
   `Delta_joint` to manufacture a positive example.
8. Parameter sweeps must include equality and no-advantage regions.
9. A positive point is insufficient; later evidence requires a non-zero,
   robust parameter region.
10. Coupling must act through `a -> O -> d -> S' -> V`, never through a direct
    reward for joint control.

### 19.11 Competence geometries

A1a must eventually test multiple `S_0` families:

- homogeneous;
- dominated;
- complementary;
- specialist;
- generalist.

Complementarity or specialization is not assumed in advance. The purpose is to
determine whether competence geometry is necessary, sufficient, irrelevant, or
interactive with opportunity/development coupling inside A1a.

### 19.12 Opportunity-kernel caution

No opportunity formula may become canonical because it makes HLS win. In
particular, a form such as

\[
g(a,k)=1-c_{ak}
\]

cannot be assumed merely because weaker execution would then generate a larger
learning opportunity. Any concrete kernel requires independent semantics and a
frozen protocol. The modular `P_O` interface must support:

- action-independent opportunity;
- weak action dependence;
- strong action dependence;
- transferable opportunity;
- non-transferable opportunity.

The scientific object is how coupling changes the result, not one privileged
formula for coupling.

### 19.13 Audit verdict

**A1a survives the pre-implementation audit.** In the `T=2` model, a strict
joint-control advantage over strong SEP requires an operational action to alter
the optimally exploitable future development value enough to exceed its
immediate operational sacrifice. This is a conditional mechanism, not a
guaranteed HLS advantage.

Implementation is scientifically admissible only if differential future value
emerges through `a -> O -> d -> S' -> V` and the negative/equivalence controls
above are reproduced.

**Status after audit: A1a = READY FOR IMPLEMENTATION DESIGN.** This does not
mean `A1a = POSITIVE`, `A1a = VALIDATED`, or `RQ0 = SUPPORTED`.

## 20. Current decision boundary

PACS and B0 are closed vehicle screens and are not evidence against RQ0. The
methodological priority is now controlled synthetic analysis before another
real-data vehicle. Candidate A/iWildCam remains parked, not rejected. A1a is
ready for implementation design, but no implementation has started. The next
task is to freeze the concrete A1a primitive world specification and exact
solver tests before coding.
