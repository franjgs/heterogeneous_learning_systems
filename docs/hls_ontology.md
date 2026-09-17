# HLS ontology and cross-theory mapping discipline

Date: 2026-09-17  
Status: canonical semantic and dimensional consistency layer for the Heterogeneous Learning Systems (HLS) programme. It is modeling infrastructure, not a research result, algorithm, or novelty claim.

## 1. Purpose

Cross-domain theories must be mapped independently into a common HLS ontology before their variables or equations are integrated:

```text
Theory A ----\
Theory B ----- > HLS ONTOLOGY
Theory C ----/
```

Similar names, equation forms, normalizations, or numerical ranges do not establish semantic equivalence. If a transformation `y = g(x)` is required, that transformation belongs to the HLS model and must be stated explicitly.

For every mapping, record:

| Field | Required content |
| --- | --- |
| Source concept | Name used by the source theory. |
| Source definition | Meaning in the source model, not an HLS paraphrase. |
| Mathematical type | Set, scalar, vector, function, decision, random variable, resource flow, and so on. |
| Units/range | Physical units or explicit normalization and admissible domain. |
| HLS concept | Target concept in this ontology, if any. |
| Mapping class | `EQUIVALENT`, `RELATED`, `INCOMPATIBLE`, or `UNRESOLVED`. |
| Required transformation | Explicit map needed when concepts are related but not identical. |
| Assumptions | Conditions under which the mapping is defensible. |
| Status | Appropriate epistemic label. |
| Notes/limitations | Inferences that the mapping does not support. |

Mapping classes mean:

- **EQUIVALENT:** the source and HLS objects are the same kind of quantity under the stated assumptions and can legitimately be identified;
- **RELATED:** they are different objects linked by an explicit mapping or model;
- **INCOMPATIBLE:** they must not be identified;
- **UNRESOLVED:** available evidence does not yet determine the relationship.

## 2. Minimal HLS ontology

| HLS concept | Definition | Mathematical nature/type | Unit or normalization | Admissible domain/range | Operational interpretation |
| --- | --- | --- | --- | --- | --- |
| **Agent / model** | A resource capable of processing tasks and potentially learning. | Indexed entity with state and attributes. | Not applicable. | A finite or otherwise specified population. | A participant that can perform, support, teach, or learn according to the model. |
| **Task / problem** | A unit or type of work presented to the system. | Instance or element of a task space; may be random. | Application-specific. | An explicitly defined task space. | Work whose execution contributes to current operation. |
| **Competence** | A capability relevant to performing some tasks. | General state component; representation remains model-specific. | Must be declared by each model. | Must be declared by each model. | What an agent can potentially bring to task execution. |
| **Competence coverage** | The tasks or problem types an agent is capable of solving. | Set, indicator function, or other extensive representation. | Task-space membership or measure. | Subset of the task space or an explicitly defined relaxation. | Which problems lie within an agent's usable repertoire. It is not automatically scalar. |
| **Competence proficiency** | How effectively an agent exercises a competence. | Scalar, vector, or function over tasks. | Accuracy, efficiency, quality, speed, or another declared scale. | Model-specific and explicitly bounded where normalized. | Intensive effectiveness conditional on relevant coverage. |
| **Operational performance** | Observable outcome when an agent executes a task. | Random variable or performance vector. | Quality, success, latency, cost, or application-specific measures. | Model-specific. | Realized execution outcome; it may depend on coverage, proficiency, task, and conditions. |
| **Real work** | Operational resources actually consumed performing or supporting work. | Non-negative resource flow or allocation. | Time, compute, money, or normalized capacity. | Resource-feasible set. | Productive or support effort actually expended. |
| **Learning exposure** | The part and type of experience relevant to changing competence. | Non-negative exposure flow, event set, or structured data. | Examples, tokens, task time, feedback events, or another declared unit. | Model-specific. | Input to a learning or retention transition. It may differ from real work. |
| **Allocation / organization** | Decision determining who performs what and, where relevant, who supports whom. | Decision variable, assignment, routing, or organizational relation. | Usually dimensionless; feasibility carries resource units. | Explicit feasible action set. | Determines current division of labour and can influence work and exposure. |
| **Interaction / help / escalation** | Operational communication, delegation, or support among agents. | Relation, event, or resource-consuming action. | Time, compute, messages, or capacity. | Explicitly constrained by the model. | Access to competence held elsewhere in the system. |
| **Learning / knowledge transfer** | Mechanisms by which exposure or information changes competence. | Transition operator or intervention. | Depends on the state and exposure definitions. | Explicit transition domain. | Changes competence coverage, proficiency, or both. |
| **Resource cost** | A relevant resource sacrificed by operation or learning. | Non-negative scalar or vector. | Time, compute, money, capacity, or another declared unit. | Model-specific. | Constrains feasible actions or reduces system value. |
| **Effective / useful work** | Useful output obtained from real work after competence-dependent effectiveness is applied. | Output flow or valued outcome. | Completed work, effective capacity, or an explicitly defined measure. | Model-specific. | Operational contribution rather than raw resource consumption. |
| **Operational value `U_t`** | Common value produced in period `t` after consistent accounting for useful output and relevant costs. | Scalar utility/reward. | One declared value unit. | Model-specific. | Basis for comparing operational consequences without adding incompatible quantities. |
| **System objective `J`** | Cumulative system-level performance over a horizon. | Expected discounted or undiscounted scalar functional of a policy. | Same value unit as `U_t`, accumulated over time. | Policies and horizons explicitly specified. | Criterion for fair system-level comparison. |

The following distinctions are mandatory unless a model supplies and justifies a mapping:

```text
competence != performance != experience != work
competence coverage != competence proficiency
```

## 3. Current source mappings

These tables preserve source fidelity. They do not imply that either source defines an entire theoretical beam.

### 3.1 Garicano (2000)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Worker | Agent in the production organization. | Agent/model. | `RELATED` | An HLS model must specify which worker attributes correspond to model properties. | Structural analogy only; a worker is not literally a learning model. |
| Problem `Z` | Draw from problem space `Q` with distribution `F`. | Task/problem and task/environment distribution. | `RELATED` | Define the HLS task space and sampling process. | Source-grounded structural mapping. |
| Knowledge set `A_i` | Set of problems whose solutions worker `i` knows. | Competence coverage. | `RELATED` | Specify whether HLS solvability is binary and how it is measured. | It is not Gutjahr's scalar competence score or general proficiency. |
| `Z in A_i` | Binary ability to solve a problem in the base model. | Coverage-conditioned solvability. | `RELATED` | A probabilistic or graded HLS model requires an explicit relaxation. | Does not define quality, accuracy, or speed. |
| Production worker / problem solver | Operational roles in a hierarchy. | Operational roles. | `RELATED` | Roles are functional and need not be permanent model types. | Does not mandate a fixed learner/teacher architecture. |
| Asking/referral | A worker unable to solve a problem consults another. | Interaction/help/escalation. | `RELATED` | Specify the HLS communication or delegation mechanism. | Not automatically knowledge transfer or learning. |
| Help cost `h` | Time/capacity consumed by the consulted worker. | Real-work or capacity cost of support. | `RELATED` | Preserve its resource meaning or define a justified value conversion. | It is not an arbitrary scalar penalty. |

Garicano currently supplies a primary reference for organization of knowledge, operational roles, routing/escalation, and time/capacity consumption. Its base model explicitly does not make communication a learning mechanism, so it does not supply HLS competence dynamics.

### 3.2 Gutjahr (2011)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Fixed team | Resource performing a project class. | Competence-bearing operational resource. | `RELATED` | An HLS mapping must specify whether the resource is one model, a group, or another unit. | Not automatically an individual HLS model. |
| Project class | Class receiving a share of work capacity. | Task/work class. | `RELATED` | Define correspondence to the HLS task space. | Does not itself define per-instance routing. |
| Competence score `z_it` | Scalar state for class `i` and period `t`. | Competence proficiency/state. | `RELATED` | Define how an HLS competence is observed or represented. | Incompatible with silently identifying it with Garicano's set `A_i`. |
| Efficiency `gamma_it = phi(z_it)` | Nondecreasing mapping from competence score to productive efficiency. | Competence-to-operational-performance map. | `RELATED` | `phi` must be specified and validated for the HLS setting. | Normalization to `[0,1]` does not make it an accuracy measure. |
| Real work `x_it` | Share of available real-work capacity assigned to class `i`. | Real work. | `RELATED` | Preserve capacity units/normalization and feasibility. | It is not automatically learning exposure. |
| Effective work `gamma_it x_it` | Useful work produced from real work at current efficiency. | Effective/useful work. | `RELATED` | Define the HLS output unit and performance map. | It cannot be added directly to unrelated costs without a value mapping. |
| Learning coefficient `eta_i` | Competence gain per unit of accumulated real work in the source model. | Gain per unit learning exposure. | `RELATED` | If work and exposure differ, introduce an explicit exposure mapping before applying `eta_i`. | `eta_i` need not be a function of routing. |
| Depreciation `beta_i` | Competence loss per period. | Competence depreciation/forgetting. | `RELATED` | Match time units and competence scale. | Does not determine realistic forgetting in learning models. |

Gutjahr currently supplies a primary formal reference for explicit work-dependent competence dynamics. It does not define HLS routing, teacher-to-learner transfer, or a general heterogeneous-model controller.

## 4. Candidate interface between organization and competence evolution

The current semantically defensible scaffold is:

```text
a_t --W--> w_t --E--> e_t --L--> C_(t+1)
```

where:

- `a_t` is an organization/allocation decision;
- `w_t` is real operational work;
- `e_t` is learning-relevant exposure;
- `C_t` is the competence state, potentially containing both coverage and proficiency;
- `W` maps organization and execution conditions to real work;
- `E` maps real work and outcomes to learning exposure; and
- `L` maps prior competence and exposure to the next competence state.

The mappings `W`, `E`, and `L` must be explicit in any instantiated model. The scaffold does not claim that work always creates exposure, that exposure always changes competence, or that the source theories have already been unified mathematically. Its status is **CANDIDATE / HYPOTHESIS**.

## 5. Operational value and cumulative objective

Quantities from different theories must not be added merely because they are scalar or normalized. First define a common operational value, for example:

```text
U_t = V_t(Y_t) - Cost_t
```

where `Y_t` is useful/effective operational output, `V_t` maps it to the declared value unit, and `Cost_t` contains relevant costs not already represented as consumed capacity or lost output. A resource must not be counted both as lost capacity and as an extra cost unless the model explicitly requires both effects.

A generic cumulative scaffold is:

```text
J(pi) = E_pi[sum_t delta^(t-1) U_t],
```

with `delta = 1` a valid base case unless discounting is scientifically required. This is not the final HLS objective.

The central programme comparison is between a scientifically specified joint policy and a strong separate-management baseline:

```text
J(pi_joint) > J(pi_separate),
```

together with equality and no-advantage conditions. `pi_joint` internalizes how present organization/use affects experience, competence evolution, and future performance. `pi_separate` manages task organization and competence development separately without correctly internalizing that cross-effect, but must not be defined as an artificially weak or merely myopic policy. If the joint class simply contains the separate class, weak inequality is tautological; the scientific content lies in meaningful policy definitions and strict, equality, and no-advantage conditions.

## 6. Multiple theories per beam

The two beams are programme questions, not source models:

- **Beam 1 — organization and use of competences:** how available competences should be organized and used for current work;
- **Beam 2 — development and evolution of competences:** how experience, learning, retention, and transfer should be managed for future capability and cumulative performance.

Garicano (2000) is a primary current reference for Beam 1, not its complete theory. Gutjahr (2011) is a primary current formal reference for Beam 2, not its complete theory. Each beam requires multiple independent theoretical lines that may corroborate, generalize, restrict, complement, or contradict a current source model. Candidate support must be classified from repository-verified literature; missing support remains **OPEN**, not guessed.

## 7. Anti-drift constraints

- Do not let Garicano dictate the HLS architecture.
- Do not let Gutjahr dictate HLS competence dynamics.
- Do not let B13 dictate RQ0 or the system objective.
- Do not identify variables across theories without an ontology mapping.
- Do not infer semantic compatibility from a shared numerical range or notation.
- Do not claim novelty merely from combining source theories.
- Do not reject the programme because individual components are established.
- Do not define a weak separate-management baseline to manufacture joint superiority.
- Do not turn this ontology into the research objective; it exists to support a coherent HLS system.
