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

## 20. A1a frozen primitive specification and analytical reference worlds

**Status: FROZEN FOR IMPLEMENTATION**

Worlds A--F are exact reference worlds and future solver acceptance tests. They
are not experimental evidence for RQ0. Their parameters must not be retuned
after solver implementation to improve outcomes. World E is a constructive,
numerically robust positive case, not evidence of robustness or prevalence. Any
later scientific sweep must be specified independently over primitive world
parameters before comparative outcomes are inspected.

### 20.1 Frozen dimensions, task sequence, and competence state

The primitive A1a world has

\[
M=2,\qquad K=2,\qquad T=2,
\]

with competence state

\[
C=\begin{bmatrix}c_{11}&c_{12}\\c_{21}&c_{22}\end{bmatrix},
\qquad c_{ik}\in[0,1].
\]

Here `c_ik` is learner `i`'s expected operational success probability, or
competence, on task type `k`. Reference worlds use the deterministic sequence

\[
q_0=1,\qquad q_1=2
\]

and initial state

\[
C_0=\begin{bmatrix}0.80&0.50\\0.70&0.20\end{bmatrix}.
\]

There are no operational costs in A1a: `s_ik=0`, hence

\[
r(S,k,i)=c_{ik}.
\]

For `q_0=1`, the unique immediate optimum is `h=M1` and the alternative is
`s=M2`, giving

\[
\delta_R=r(h)-r(s)=0.80-0.70=0.10.
\]

### 20.2 Frozen opportunity-generation family

Opportunity propensity is a separate primitive

\[
E=[e_{ik}],\qquad e_{ik}\in[0,1].
\]

`E` is not competence. `e_ik` is the base capacity/probability associated with
execution by learner `i` on task `k` generating a useful development
opportunity. No monotone relation between `C` and `E` is assumed; in particular,
`e_ik=1-c_ik` is not canonical.

Freeze the A1a family

\[
g_{ik}(\rho)=(1-\rho)\bar e_k+\rho e_{ik},
\qquad \rho\in[0,1],
\]

followed after execution by

\[
Z\sim\operatorname{Bernoulli}(g_{ik}(\rho)).
\]

At `rho=0`, opportunity generation is independent of the operational learner;
at `rho=1`, it is fully executor-specific. `rho` controls coupling strength and
is not an HLS bonus.

Only task type 1 is used for opportunity generation in these worlds:

\[
\bar e_1=0.50,\qquad e_{11}=0.20,\qquad e_{21}=0.90.
\]

Thus

\[
g_h(\rho)=0.50-0.30\rho,
\qquad
g_s(\rho)=0.50+0.40\rho,
\]

and

\[
g_s(\rho)-g_h(\rho)=0.70\rho.
\]

Entries of `E` for task type 2 are **unused / not identified by A1a**. An
implementation schema may represent that status explicitly but must not invent
scientific values for them.

### 20.3 Development action, cost, and transition

If `Z=1`, the admissible development actions are

```text
null
develop M1 on task type 2
develop M2 on task type 2
```

The opportunity may be assigned to either learner. Operational actor and
development recipient are distinct variables, so `a != d` is permitted and
`a=d` must not be imposed. If `Z=0`, no non-null development action is
available.

The frozen development cost is

\[
\kappa(d)=0.02
\]

for either non-null action and `kappa(null)=0`. Developing learner `j` on task
type 2 gives

\[
c'_{j2}=c_{j2}+\eta(1-c_{j2}),
\qquad \eta\in[0,1],
\]

with every other entry unchanged.

A1a excludes transfer, interference, forgetting, representation learning,
additional competence capacity, stochastic competence updates beyond
opportunity generation, replay, adapters, and neural-network training.

### 20.4 Terminal value and derived development value

Reference worlds fix `beta=1`. There is no development after `t=1`, and because
`q_1=2` deterministically,

\[
V_1(S_1)=\max_i c_{i2,1}.
\]

The broader contract retains

\[
V_1(S_1)=\sum_k p_k\max_i c_{ik,1}
\]

for a future random terminal task, but A--F use `P(q_1=2)=1`.

Define, with the null action always available,

\[
N(S)=\beta V_1(S),
\]

\[
D(S,k)=\max_d\{-\kappa(d)+\beta V_1(F(S,k,d))\}.
\]

For the base world with `eta=0.80`,

\[
N=\max\{0.50,0.20\}=0.50.
\]

Developing M1 yields

\[
c'_{12}=0.50+0.80(1-0.50)=0.90,
\qquad 0.90-0.02=0.88,
\]

while developing M2 yields

\[
c'_{22}=0.20+0.80(1-0.20)=0.84,
\qquad 0.84-0.02=0.82.
\]

Therefore

\[
D=\max\{0.50,0.88,0.82\}=0.88,
\qquad d^*=\text{develop M1},
\qquad D-N=0.38.
\]

In positive World E, M2 executes but M1 is the optimal development recipient:
`who acts` and `who learns` are concretely separated.

### 20.5 Derived continuation value and phase boundary

For operational action `i`,

\[
G(i)=g_i(\rho)D+[1-g_i(\rho)]N
=N+g_i(\rho)(D-N).
\]

`G(i)` is derived and cannot be a configurable world parameter. For `h=M1`
and `s=M2`,

\[
\delta_G=G(s)-G(h)
=[g_s(\rho)-g_h(\rho)](D-N)
=0.70\rho\times0.38
=0.266\rho.
\]

The switch condition becomes

\[
0.266\rho>0.10.
\]

Its exact phase boundary is

\[
\rho^*=\frac{0.10}{0.266}=\frac{50}{133}
\approx0.3759398496.
\]

For this family generally,

\[
\delta_G=\rho(e_s-e_h)(D-N),
\]

and, when the denominator is positive,

\[
\rho^*=\frac{\delta_R}{(e_s-e_h)(D-N)}.
\]

These are exact A1a properties under the frozen parametrization, not general
HLS theorems.

### 20.6 Frozen policy values

HLS solves

\[
J_{HLS}=\max_i\{r(i)+G(i)\}.
\]

Strong SEP chooses `a_SEP` from `argmax_i r(i)` and then optimizes development
exactly using the opportunity it actually obtains. For unique immediate optimum
`h`,

\[
J_{SEP}=r(h)+G(h).
\]

SEP is not heuristic or deliberately weak. SEP-Omega is a separated
architecture whose operational module receives sufficient exact continuation
information. It must be solved independently of HLS; under the A1a
reducibility conditions, the acceptance target is

\[
J_{SEP\text{-}Omega}=J_{HLS}.
\]

### 20.7 Reference World A — no learning

Freeze `eta=0`, `rho=1`. Development cannot change competence and costs 0.02,
so `d*=null` and

\[
D=N=0.50,\qquad\delta_G=0.
\]

Although `g_h=0.20` and `g_s=0.90`, opportunity has no development value:

\[
J(h)=0.80+0.50=1.30,
\qquad
J(s)=0.70+0.50=1.20.
\]

Expected acceptance result:

\[
a_{HLS}=a_{SEP}=h,
\qquad J_{HLS}=J_{SEP}=1.30.
\]

Purpose: no-learning negative control.

### 20.8 Reference World B — learning, no coupling

Freeze `eta=0.80`, `rho=0`. Then `D=0.88`, `N=0.50`, and

\[
g_h=g_s=0.50,
\qquad G(h)=G(s)=0.50+0.50(0.38)=0.69.
\]

Hence

\[
J(h)=1.49,
\qquad J(s)=1.39,
\]

and

\[
a_{HLS}=a_{SEP}=h,
\qquad J_{HLS}=J_{SEP}=1.49.
\]

Purpose: learning alone is insufficient when opportunity is independent of the
operational learner.

### 20.9 Reference World C — insufficient coupling

Freeze `eta=0.80`, `rho=0.25`. Then

\[
g_h=0.425,
\qquad g_s=0.600,
\]

\[
G(h)=0.6615,
\qquad G(s)=0.728,
\qquad \delta_G=0.0665<\delta_R=0.10.
\]

Thus

\[
J(h)=1.4615,
\qquad J(s)=1.428,
\]

and

\[
a_{HLS}=a_{SEP}=h,
\qquad J_{HLS}=J_{SEP}=1.4615.
\]

Purpose: coupling is not sufficient for strict joint advantage.

### 20.10 Reference World D — exact boundary

Freeze `eta=0.80` and

\[
\rho=\rho^*=\frac{50}{133}.
\]

The exact values are

\[
g_h=\frac{103}{266}\approx0.3872180451,
\qquad
g_s=\frac{173}{266}\approx0.6503759398,
\]

\[
G(h)=\frac{453}{700}\approx0.6471428571,
\qquad
G(s)=\frac{523}{700}\approx0.7471428571,
\]

and

\[
\delta_G=\delta_R=0.10.
\]

Therefore

\[
J(h)=J(s)=\frac{1013}{700}\approx1.4471428571.
\]

The expected HLS optimal-action set is `{h,s}`. The solver may use an explicit,
deterministic output tie rule, but the mathematical acceptance test compares
the optimal-action set and value, not arbitrary `argmax` order. No strict HLS
advantage may be claimed.

Purpose: exact phase-boundary test.

### 20.11 Reference World E — strict joint advantage

Freeze `eta=0.80`, `rho=0.75`. Then

\[
g_h=0.275,
\qquad g_s=0.800,
\]

\[
G(h)=0.6045,
\qquad G(s)=0.804,
\qquad \delta_G=0.1995>0.10.
\]

Strong SEP chooses `h=M1`:

\[
J_{SEP}=0.80+0.6045=1.4045.
\]

HLS chooses `s=M2`:

\[
J_{HLS}=0.70+0.804=1.504.
\]

Thus

\[
\Delta_{joint}=J_{HLS}-J_{SEP}=0.0995>0.
\]

The causal chain is

```text
M2 executes
    -> higher probability of useful opportunity
    -> optimal development assigns the opportunity to M1
    -> M1 competence on the future task increases
    -> future operational value increases
```

Thus `a_0=M2`, while, conditional on opportunity, `d_0=develop M1`.

Purpose: constructive existence test for strict joint advantage. This is not
evidence that HLS generally improves over SEP. The deliberately large
`e_s-e_h=0.70` gives a robust solver test; its magnitude is neither realistic
nor empirically supported. Scientific support would require a predefined,
non-zero parameter region rather than this single point.

### 20.12 Reference World F — SEP-Omega reducibility

World F uses exactly World E: identical `C`, `E`, `eta`, `rho`, `kappa`,
`beta`, `q_0`, and `q_1`. Only the separated operational architecture's
information/coordination changes.

Strong SEP sees immediate operational value and chooses `h=M1`. SEP-Omega
receives exact sufficient continuation values and independently computes

\[
Q_{SEP\text{-}Omega}(h)=0.80+0.6045=1.4045,
\]

\[
Q_{SEP\text{-}Omega}(s)=0.70+0.804=1.504.
\]

It therefore chooses `s=M2`, giving

\[
J_{HLS}=J_{SEP\text{-}Omega}=1.504>J_{SEP}=1.4045.
\]

Purpose: exact reducibility/equivalence acceptance test. SEP-Omega must not call
or alias HLS; both policies must be solved independently and equality must
emerge as a test result.

### 20.13 Reference-world acceptance summary

| World | `eta` | `rho` | `delta_G` | `delta_R` | Exact acceptance result |
| --- | ---: | ---: | ---: | ---: | --- |
| A | `0` | `1` | `0` | `0.10` | `HLS = SEP = 1.30` |
| B | `0.8` | `0` | `0` | `0.10` | `HLS = SEP = 1.49` |
| C | `0.8` | `0.25` | `0.0665` | `0.10` | `HLS = SEP = 1.4615` |
| D | `0.8` | `50/133` | `0.10` | `0.10` | boundary; `{h,s}` optimal; value `1013/700` |
| E | `0.8` | `0.75` | `0.1995` | `0.10` | `HLS=1.504 > SEP=1.4045` |
| F | same as E | same as E | same as E | same as E | `HLS = SEP-Omega = 1.504 > SEP` |

A--F are acceptance tests, not the empirical study. Together they require the
implementation to reproduce no learning, no coupling, insufficient coupling,
the exact boundary, strict joint advantage, and exact reducibility.

### 20.14 Frozen primitive tuple

The first implementation must represent

\[
\Theta_{A1a}=(\Theta_Q,\Theta_C,\Theta_O,\Theta_D,
\Theta_R,\Theta_K,\Theta_I)
\]

with:

- `Theta_Q`: deterministic `q_0=1`, `q_1=2`;
- `Theta_C`: the frozen `C_0` matrix above;
- `Theta_O`: `ebar_1=0.50`, `e_11=0.20`, `e_21=0.90`, Bernoulli opportunity,
  and world-specific `rho`;
- `Theta_D`: bounded task-2 transition with world-specific `eta`, no transfer
  or interference;
- `Theta_R`: `r(S,k,i)=c_ik` and terminal maximum competence for task 2;
- `Theta_K`: `kappa=0.02`, `beta=1`, no operational cost or extra constraints;
- `Theta_I`: separate contracts for HLS, strong SEP, and independently solved
  SEP-Omega.

`G`, `delta_G`, policy values, and preferred actions are derived outputs, not
members of `Theta_A1a`.

### 20.15 Anti-cherry-picking and later sweeps

The eventual scientific experiment must use predefined sweeps over primitives,
never over `delta_G` or a desired outcome. Relevant future dimensions include
`rho`, `eta`, `kappa`, competence geometry `C`, opportunity geometry `E`,
`e_s-e_h`, task distribution `P_Q`, and `beta`; no sweep ranges are frozen here.

For the World E family, the exact opportunity-contrast threshold is

\[
(e_s-e_h)^*=\frac{\delta_R}{\rho(D-N)}.
\]

At `rho=0.75`, `delta_R=0.10`, and `D-N=0.38`,

\[
(e_s-e_h)^*=\frac{20}{57}\approx0.350877193.
\]

World E uses `e_s-e_h=0.70`, intentionally well inside the positive region.
That is desirable for a solver acceptance test and is not scientific evidence
of robustness.

### 20.16 Freeze rule and next step

**A1a primitive specification and reference worlds A--F are FROZEN for the
first implementation.** After implementation begins:

- do not change A--F because an acceptance test fails;
- treat a mismatch first as an implementation/specification problem;
- document and version any scientifically motivated revision explicitly;
- keep reference worlds distinct from later experimental sweep configurations.

Status:

```text
A1a primitive specification = FROZEN
A1a reference worlds A–F = FROZEN
A1a implementation = NOT STARTED
```

Next step: implement the exact A1a solver and require A--F acceptance tests to
pass before any parameter sweep.

## 21. A1b predefined primitive-parameter phase-boundary sweep

**Status: PRE-REGISTERED / NOT RUN**

A1b is a deterministic, predefined sweep of the frozen `T=2` A1a world family.
It does not seek to maximize HLS-minus-SEP value or search for favorable
examples. It asks:

> For the frozen T=2 A1a world family, in which regions of primitive-parameter
> space does joint management obtain strict value over strong SEP, and do the
> observed regions coincide with the analytical phase boundaries implied by
> A1a?

The primary conservative advantage quantity is

\[
\Delta J_{cons}=J_{HLS}-J_{SEP,max},
\]

where

\[
J_{SEP,max}=\max_{a\in A_{SEP}}\{r(a)+G(a)\},
\qquad
A_{SEP}=\arg\max_a r(a).
\]

The corresponding lower endpoint is

\[
J_{SEP,min}=\min_{a\in A_{SEP}}\{r(a)+G(a)\}.
\]

With a unique immediate optimum,
`J_SEP_min=J_SEP_max=J_SEP`. Strict conservative joint advantage requires
`Delta_J_cons>0` outside the frozen numerical tolerance. Equality and broad
no-advantage regions are valid expected outcomes, not failures. A1b tests phase
boundaries rather than effect-size maximization. No primitive, grid point,
probe, metric, or tolerance may be changed after observing results merely to
enlarge a positive region.

### 21.1 Fixed base world

Unless a phase below explicitly sweeps a primitive, freeze

\[
M=2,\qquad K=2,\qquad T=2,
\]

\[
q_0=1,\qquad q_1=2,
\]

and

\[
C=\begin{bmatrix}0.80&0.50\\0.70&0.20\end{bmatrix}.
\]

Therefore `h=M1`, `s=M2`, and `delta_R=0.10`. Also freeze:

- `ebar_1=0.50`;
- `beta=1`;
- no operational costs;
- base `eta=0.80` and `kappa=0.02` when development parameters are not swept;
- base `e_h=e_11=0.20` and `e_s=e_21=0.90` when opportunity parameters are
  not swept.

**A1b does not vary `C`.** Competence geometry belongs to the separate A1c
boundary stated below. Because `C` is fixed, strong SEP has the unique immediate
optimum `M1` throughout A1b; nevertheless every row must retain both
`J_SEP_min` and `J_SEP_max` under the general strong-SEP contract.

### 21.2 Analytical reference

At the base `eta=0.80`, `kappa=0.02`,

\[
N=0.50,\qquad D=0.88,\qquad D-N=0.38=\frac{19}{50}.
\]

For this family,

\[
\delta_G=\rho(e_s-e_h)(D-N),
\]

and the strict switch condition is

\[
\rho(e_s-e_h)(D-N)>\delta_R.
\]

With `e_h=0.20` and `e_s=0.90`,

\[
\delta_G=0.266\rho,
\qquad
\rho^*=\frac{50}{133}\approx0.37593984962406015.
\]

More generally, when its denominator is positive,

\[
\rho^*=\frac{\delta_R}{(e_s-e_h)(D-N)},
\]

and the opportunity-geometry threshold is

\[
(e_s-e_h)^*=\frac{\delta_R}{\rho(D-N)}.
\]

Development phases must use the actual `D(eta,kappa)` returned by exact
development enumeration, including the null action. No unverified hard-coded
development formula may replace that calculation.

### 21.3 A1b.1 — coupling sweep

**Purpose.** Test the `rho` phase boundary with all other primitives fixed:
`eta=0.80`, `kappa=0.02`, `e_h=0.20`, `e_s=0.90`, `ebar=0.50`, `beta=1`, and
the base `C`.

The frozen global grid is

```text
rho = 0.00, 0.05, 0.10, ..., 1.00
```

inclusive with step `0.05`. Add exactly these analytical probes:

```text
rho* = 50/133
rho* ± 0.01
rho* ± 0.001
rho* ± 0.0001
```

Duplicates, if any, are removed before evaluation; no later points may be
added. None of these probes duplicates the global grid, so the frozen unique
count is `21+7=28` configurations.

Expected classification:

- `rho<rho*`: no strict HLS advantage;
- `rho=rho*`: boundary and equal total optimum;
- `rho>rho*`: strict HLS advantage;
- `rho=0`: mandatory negative control.

Each row must contain `rho`, `g_h`, `g_s`, `N`, `D`, `delta_R`, `delta_G`,
`J_HLS`, `J_SEP_min`, `J_SEP_max`, `Delta_J_cons`, HLS optimal-action set,
SEP immediate-optimal-action set, `J_SEP_Omega`, analytical predicted regime,
observed regime, and match/mismatch.

A1b.1 passes iff every point agrees with the analytical regime outside the
frozen tolerance, `rho=0` has no strict advantage, exact `rho*` is a boundary,
and `J_SEP_Omega=J_HLS` at every point. A mismatch is reported and investigated;
it is not repaired by moving probes or changing tolerance.

### 21.4 A1b.2 — development effectiveness/cost sweep

**Purpose.** Test that coupling alone is insufficient and that a positive
region appears only when development creates enough continuation value.

Freeze `rho=0.75`, `e_h=0.20`, `e_s=0.90`, `ebar=0.50`, `beta=1`, and base
`C`. Use the complete frozen grids

```text
eta   = 0.00, 0.05, 0.10, ..., 1.00
kappa = 0.00, 0.02, 0.04, ..., 0.50
```

giving exactly `21*26=546` configurations. The grid must not be optimized or
adapted after results.

For every configuration derive exactly `N`, `D`, `D-N`, `delta_R`,

\[
\delta_G=\rho(e_s-e_h)(D-N),
\]

`J_HLS`, `J_SEP_min`, `J_SEP_max`, `Delta_J_cons`, optimal development-action
set, HLS optimal-action set, and SEP-Omega value.

Classify by comparing `rho(e_s-e_h)(D-N)` with `delta_R=0.10`:

- `LESS`: no strict advantage;
- `BOUNDARY`: equality within the frozen tolerance;
- `GREATER`: strict advantage.

Because `D` includes null development, ineffective or sufficiently expensive
development produces `D=N`, not negative development value. This is a
mandatory negative-control region.

A1b.2 passes iff every configuration matches its analytical
`LESS/BOUNDARY/GREATER` regime, all `D=N` configurations show no strict
advantage, no `delta_G<delta_R` configuration shows strict advantage, every
`delta_G>delta_R` configuration does, and SEP-Omega equals HLS throughout. The
coarse grid need not contain an exact equality point; absence of one is not a
failure.

### 21.5 A1b.3 — opportunity-geometry sweep

**Purpose.** Attack directly the possible artificiality of World E by varying
the action-conditioned opportunity geometry over its full admissible square.

Freeze `rho=0.75`, `eta=0.80`, `kappa=0.02`, `ebar=0.50`, `beta=1`, and base
`C`. Use

```text
e_h = 0.00, 0.05, 0.10, ..., 1.00
e_s = 0.00, 0.05, 0.10, ..., 1.00
```

as a full Cartesian `21*21=441` grid. The sweep must not be restricted to
`e_s>e_h`.

For this phase,

\[
D-N=0.38,
\qquad
\delta_G=0.75(e_s-e_h)(0.38)=0.285(e_s-e_h),
\]

and

\[
(e_s-e_h)^*=\frac{0.10}{0.285}=\frac{20}{57}
\approx0.3508771929824561.
\]

Expected regimes are:

- `e_s-e_h<=0`: no positive A1a mechanism;
- `0<e_s-e_h<20/57`: opportunity asymmetry exists but is insufficient;
- `e_s-e_h=20/57`: boundary;
- `e_s-e_h>20/57`: strict HLS advantage.

The `0.05` grid need not contain the exact boundary. Add exactly five probes
with fixed `e_h=0.20`:

```text
e_s = 0.20 + 20/57
e_s = 0.20 + 20/57 ± 0.01
e_s = 0.20 + 20/57 ± 0.001
```

Their `e_s` values range from approximately `0.5408771929824562` to
`0.5608771929824561`, so every probe lies in `[0,1]`. None duplicates the
Cartesian grid. The frozen unique count is therefore `441+5=446`
configurations. No additional probe may be added after observing results.

Every row records `e_h`, `e_s`, `e_s-e_h`, `g_h`, `g_s`, `D-N`, `delta_G`,
`delta_R`, `J_HLS`, `J_SEP_min`, `J_SEP_max`, `Delta_J_cons`, HLS action set,
SEP immediate action set, SEP-Omega value, predicted regime, observed regime,
and match/mismatch.

A1b.3 passes iff the full grid and probes agree with analytical classification,
there is no strict advantage for `e_s<=e_h` or below threshold, strict advantage
occurs above threshold, the exact boundary probe gives equality, and SEP-Omega
equals HLS throughout.

### 21.6 Frozen numerical classification

All classifications use unrounded internal values and the A1a absolute
tolerance

\[
tol=10^{-12}.
\]

For

\[
x=\delta_G-\delta_R,
\]

classify:

```text
x < -tol       -> LESS
abs(x) <= tol  -> BOUNDARY
x > tol        -> GREATER
```

Apply equivalent logic to `Delta_J_cons`. Record any analytical/observed
difference attributable only to tolerance. Printed rounding must never define
a scientific region, and tolerance must not be enlarged after results.

### 21.7 Mandatory negative and reducibility controls

The frozen phases explicitly cover:

1. `rho=0` in A1b.1;
2. `eta=0` in A1b.2;
3. `D=N` through ineffective or expensive development in A1b.2;
4. `e_s=e_h` along the A1b.3 diagonal;
5. `e_s<e_h` in the lower opportunity-contrast half of A1b.3;
6. positive coupling with `delta_G<delta_R` in all three phases.

Every case must have no strict conservative joint advantage.

At every A1b point, compute SEP-Omega and require

\[
J_{HLS}=J_{SEP\text{-}Omega}
\]

within `tol`. This is a mathematical reducibility consistency check under the
A1a assumptions, not an independent algorithmic benchmark. Any violation is a
failure and investigation trigger.

### 21.8 Required row and aggregate outputs

An eventual implementation must emit machine-readable rows with at least:

- phase and configuration identifier;
- all primitive parameters varied or fixed for that row;
- `N`, `D`, `D_minus_N`, `delta_R`, and `delta_G`;
- `J_HLS`, `J_SEP_min`, `J_SEP_max`, `Delta_J_cons`, and `J_SEP_Omega`;
- HLS optimal-action set, SEP immediate-optimal-action set, and optimal
  development-action set;
- predicted regime, observed regime, and match indicator.

A1b is exact and deterministic: it uses no seeds and needs no stochastic
confidence intervals.

For each phase, aggregate:

- number of configurations;
- predicted and observed counts for `LESS`, `BOUNDARY`, and `GREATER`;
- mismatches;
- negative-control violations;
- SEP-Omega equivalence violations.

Do not report only the percentage of HLS wins. Phase-boundary agreement is the
scientific object.

### 21.9 Pre-registered visualizations

No visualization is generated at design time. A later A1b run may produce only
the following pre-registered views:

- **A1b.1:** `Delta_J_cons` versus `rho`, with analytical `rho*` marked;
- **A1b.2:** two-dimensional `eta` by `kappa` regime map based on
  `Delta_J_cons`, with the analytical boundary overlaid where defined;
- **A1b.3:** two-dimensional `e_h` by `e_s` regime map with
  `e_s-e_h=20/57` overlaid.

Plots must show equality/no-advantage regions as prominently as positive
regions. No cosmetic parameter selection is permitted after results.

### 21.10 A1b success, failure, and interpretation

**A1b PASS** requires every one of the `28+546+446=1020` frozen configurations
and probes to reproduce its analytical regime, all mandatory negative controls
to hold, and SEP-Omega equivalence to hold throughout.

**A1b FAIL** means one or more genuine mismatches remain after excluding only
demonstrated implementation or numerical bugs. Failure is scientifically
informative and must not be repaired by tuning parameters.

PASS does not empirically validate RQ0. It establishes only that the exact
solver and analytical A1a theory agree over predefined primitive-parameter
regions, recovering the controlled phase structure of this minimal modeled
mechanism.

### 21.11 Anti-cherry-picking freeze

Once this section is accepted, the following are frozen:

- `rho`, `eta`, `kappa`, `e_h`, and `e_s` grids;
- every boundary probe;
- `tol=1e-12`;
- row and aggregate metrics;
- regime definitions and PASS/FAIL criteria.

Any later additional sweep is exploratory, must be labelled as such, and must
remain separate from A1b confirmatory results.

### 21.12 A1c boundary

A1b does not vary competence geometry `C`. Varying `C` simultaneously changes
the immediate operational gap `delta_R`, terminal competence geometry, `D-N`,
the possible optimal development recipient, and the identity or multiplicity
of immediate-optimal SEP actions. Those coupled changes require a separate
experiment, **A1c competence-geometry sweep**. A1c is not designed here.

## 22. Current decision boundary

PACS and B0 are closed vehicle screens and are not evidence against RQ0. The
methodological priority is controlled synthetic analysis before another
real-data vehicle. Candidate A/iWildCam remains parked, not rejected. The A1a
exact solver and reference worlds A--F are validated. A1b is pre-registered but
has not been implemented or run; its frozen primitive sweep is the next
experimental task.
