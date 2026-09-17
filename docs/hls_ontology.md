# HLS ontology and cross-theory mapping discipline

Date: 2026-09-17  
Status: canonical semantic, mathematical, and dimensional consistency layer for the Heterogeneous Learning Systems (HLS) programme. It is modeling infrastructure, not a research result, algorithm, or novelty claim.

## 1. Purpose

Cross-domain theories must be mapped independently into a common HLS ontology before their variables or equations are integrated:

```text
Theory A ----\
Theory B ----- > HLS ONTOLOGY
Theory C ----/
```

Similar names, equation forms, normalizations, or numerical ranges do not establish semantic equivalence. If a transformation `y = g(x)` is required, that transformation belongs to the HLS model and must be stated explicitly.

The methodological rule is:

```text
reuse what is established
    -> integrate what is compatible
    -> derive what is HLS-specific
    -> develop new theory only where necessary
```

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

A new source theory must first be mapped into the existing HLS ontology. New HLS variables should be introduced only when a source exposes a phenomenon that the current ontology cannot represent without changing the meaning of an existing variable.

---

## 2. Minimal HLS ontology

### 2.1 Basic entities

Let

```text
M = {1,...,M}
```

denote the set of agents/models,

```text
K = {1,...,K}
```

the set of competences, and

```text
Q
```

the task/problem space.

A task presented at time `t` is denoted by

```text
q_t in Q.
```

The environment may generate tasks according to a time-dependent demand distribution

```text
q_t ~ P_t.
```

No stationarity assumption is imposed by the ontology.

### 2.2 System state

The system state is represented generically as

```text
X_t = (P_t, S_t, b_t, Theta_t),
```

where:

- `P_t` describes current task demand;
- `S_t` contains agent competence states;
- `b_t` contains available agent capacities;
- `Theta_t` contains additional scenario parameters required by a particular model.

This is a generic state representation. A concrete HLS model must specify exactly which components are required.

### 2.3 Competence

The competence state of agent `m` is

```text
S_m,t = (S_m1,t, ..., S_mK,t),
```

with

```text
S_mk,t in S_k,
```

where `S_k` is the declared state space for competence `k`.

`S_mk,t` represents the state or level of competence of agent `m` in competence `k`. The ontology does not require competence to be binary, scalar-normalized, directly observable, or measured in the same units across competences.

Competence is not operational performance:

```text
competence != performance.
```

A source model may represent competence through a set, scalar, vector, function, or another suitable object. Such representations are model-specific realizations of the HLS competence concept.

In particular, binary or set-valued competence coverage is not retained as a separate fundamental HLS state. When useful, coverage can be derived from competence and task requirements.

For example, given a quality threshold `Q_min(q)`, a usable task repertoire can be defined as

```text
K_m,t = {q in Q : Qbar_mq,t >= Q_min(q)}.
```

This is a derived object, not an ontological requirement.

### 2.4 Task requirements and expected quality

A task `q` may involve one or several competences. Its requirements may be represented by a model-specific description such as

```text
r(q),
```

without requiring `r(q)` to have the same units or scale as `S_m,t`.

Expected quality when agent `m` processes task `q` is represented by

```text
Qbar_mq,t = Psi(q, S_m,t, X_t).
```

`Psi` is the competence-to-performance mapping.

The ontology does not impose linearity, additivity, compensability, independence among competences, or any particular functional form for `Psi`.

### 2.5 Observed quality

After processing task `q_t`, agent `m` produces result `r_m,t`.

Observed quality is

```text
Q_m,t = Q(q_t, r_m,t).
```

Therefore:

```text
S != Qbar != Q.
```

`S` is competence state, `Qbar` is expected task performance, and `Q` is observed result quality.

### 2.6 Operational work

Operational work is represented by

```text
W_t = W(X_t, a_t, q_t),
```

or by the corresponding agent/task-specific quantities when needed.

`W` represents work actually performed in executing or supporting operational tasks. It is distinct from result quality, operational value, learning exposure, and resource consumption.

Thus:

```text
work != quality
work != experience
work != operational value.
```

### 2.7 Operational value

For task `q`, operational value is

```text
Y_q,t = V(q, W_q,t, Q_q,t).
```

`Y_q,t` represents the useful operational value obtained from processing the task.

The ontology does not require `Y` to have the same units as `W`.

Possible model-specific realizations include

```text
Y_q,t = v(q) Q_q,t
```

or

```text
Y_q,t = v(q) W_q,t Q_q,t,
```

but neither expression is an ontological identity.

The operational value over a period can be aggregated as

```text
Y_t = A_Y({Y_q,t}),
```

with simple summation as one possible realization when values are additive.

The distinction is therefore:

```text
W = work performed
Q = quality of the result
Y = operational value obtained.
```

Quality is not counted again as an independent objective component when its operational effect is already represented through `Y`.

### 2.8 Resource consumption and capacity

Agent-level physical resource consumption is

```text
r_m,t = R_m(X_t, a_t, d_t),
```

where

```text
r_m,t in R_+^p.
```

Components may represent compute time, energy, memory, tokens, communication capacity, API usage, or other physically or operationally meaningful resources.

Available capacity is

```text
b_m,t in R_+^p,
```

expressed in compatible units and over a compatible time interval.

Physical feasibility requires

```text
r_m,t <= b_m,t
```

componentwise.

System-level resource consumption is

```text
R_t = A_R(r_1,t, ..., r_M,t).
```

When resources are additive,

```text
R_t = sum_m r_m,t,
```

but additivity is not imposed by the ontology.

Economic or scenario-specific cost is derived from resource consumption:

```text
C_t = C(R_t).
```

Therefore:

```text
agent resource consumption
    -> system resource consumption
    -> scenario-specific cost
```

and

```text
resource consumption != capacity != cost.
```

A resource must not be counted both as lost capacity and as an additional cost unless the instantiated model explicitly requires both effects.

### 2.9 Latency

Task latency is defined end-to-end:

```text
L(q) = t_completion(q) - t_arrival(q).
```

Latency is distinct from total resource consumption.

In particular, resource use by agents operating in parallel must not automatically be summed and interpreted as end-to-end latency.

Thus:

```text
resource consumption != latency.
```

### 2.10 Experience

Learning-relevant experience is represented as

```text
E_mk,t = (E_dir_mk,t, E_ind_mk,t),
```

where:

- `E_dir_mk,t` is direct experience obtained through the agent's own activity;
- `E_ind_mk,t` is indirect experience obtained through information, interaction, observation, assistance, teaching, transfer, or another agent-mediated mechanism.

When source identity matters, indirect exposure can retain the form

```text
E_ind_n->m,k,t.
```

Training, observation, teacher interaction, distillation, collaboration, feedback, and related mechanisms are possible generators of experience. They are not assumed to be separate fundamental state variables.

Experience is generated through a model-specific mapping

```text
E_t = E(X_t, a_t, d_t, W_t).
```

Operational allocation can therefore generate both direct and indirect experience. Explicit development actions can also generate experience.

Experience is not competence change:

```text
E != Delta S.
```

The same exposure may produce different competence changes for different agents, competences, states, or learning mechanisms.

### 2.11 Competence evolution

Competence evolves according to

```text
S_t+1 = L(S_t, E_t, Delta t).
```

`L` is a model-specific learning/retention transition.

It may represent:

- learning;
- saturation;
- forgetting or depreciation;
- interference;
- heterogeneous learning rates;
- null change;
- or other justified competence dynamics.

Forgetting belongs to the competence transition `L`; it is not defined as a separate form of negative experience.

A componentwise model

```text
S_mk,t+1 = L_mk(S_mk,t, E_mk,t)
```

is a possible specialization when competence dimensions evolve independently.

### 2.12 Decisions

The complete HLS decision is

```text
u_t = (a_t, d_t).
```

`a_t` is the operational allocation/organization decision.

It determines who participates in executing which tasks and may represent assignment, routing, collaboration, escalation, delegation, ensemble participation, sequential processing, or another operational organization.

The ontology does not require `a_t` to be binary or to assign exactly one agent to each task.

`d_t` is the competence-development decision.

When source, target, and competence are explicitly represented,

```text
d_mnk,t
```

denotes a directed development action from agent `m` to agent `n` concerning competence `k`.

Crucially:

```text
d != E_ind.
```

`d` is a decision or intervention; `E_ind` is resulting learning-relevant exposure.

Operational allocation and competence development are not assumed to correspond to two independent physical channels. Both can affect current operation and future competence.

### 2.13 Feasible decision set

Feasible decisions satisfy

```text
u_t = (a_t, d_t) in U(X_t).
```

A useful generic decomposition is

```text
a_t in A(X_t)
```

and

```text
d_t in D(X_t, a_t),
```

together with resource constraints

```text
r_m,t <= b_m,t
```

for every relevant agent.

The dependence

```text
D(X_t, a_t)
```

allows operational organization to create, modify, or prevent opportunities for interaction and learning.

Additional scenario constraints may include:

```text
Q(q) >= Q_min(q)
L(q) <= L_max(q)
sum_t R_t <= B
sum_t C_t <= C_max
```

or other service, budget, deadline, reliability, or capacity requirements.

The ontology does not impose universally that:

- every task must be served;
- exactly one agent must process each task;
- every learning exposure improves competence;
- only a globally more competent agent can provide useful information to another agent.

### 2.14 System performance

The fundamental physical performance vector is

```text
Z_t = (Y_t, L_t, R_t).
```

The corresponding orientations are

```text
maximize Y
minimize L
minimize R.
```

`Q` and `W` remain important observable or diagnostic quantities, but are not additional independent objective dimensions when their operational contribution is already represented by `Y`.

Cost is not a fundamental physical dimension because it is derived from resources through

```text
C_t = C(R_t).
```

Over a horizon, policy performance is represented as

```text
Z(pi) =
(
    G_Y(Y_1:T),
    G_L(L_1:T),
    G_R(R_1:T)
).
```

The aggregation functions need not be identical.

For example, operational value and resource consumption may be additive, whereas latency may be represented by mean latency, percentiles, deadline violations, or another application-appropriate statistic.

When possible, policies should first be compared through dominance:

```text
Y_A >= Y_B
L_A <= L_B
R_A <= R_B
```

with at least one strict inequality.

When a scalar optimization problem is required, constrained formulations are preferred when they avoid arbitrary trade-off weights. For example:

```text
maximize_pi Y(pi)

subject to

L(pi) <= L_max
R(pi) <= B.
```

A scalar utility may be introduced when scientifically justified:

```text
C_t = C(R_t)

U_t = U(Y_t, L_t, C_t)
```

and

```text
J(pi) = E_pi[sum_t delta^(t-1) U_t].
```

The base finite-horizon case may use

```text
delta = 1
```

unless discounting is scientifically required.

Competence is not rewarded directly by default. Its value should normally appear through future operational performance:

```text
S_t+1
    -> Qbar_t+1
    -> Q_t+1
    -> Y_t+1.
```

A terminal competence value may be introduced only when justified by the modeled horizon or application.

---

## 3. Closed HLS loop

The canonical HLS scaffold is

```text
X_t
    -> pi
(a_t, d_t)
    -> {
         Z_t = (Y_t, L_t, R_t)
         E_t
       }
    -> S_t+1
    -> X_t+1.
```

Equivalently, the decision produces simultaneous present and future consequences:

```text
                       -> W_t -> Q_t -> Y_t
                      /
(a_t, d_t) -----------> R_t, L_t
                      \
                       -> E_t -> S_t+1
```

and future competence affects future expected performance:

```text
S_t+1
    -> Qbar_t+1
    -> Q_t+1
    -> Y_t+1.
```

The central structural property is therefore that operational organization and competence development may affect both present system performance and future competence.

The ontology itself does not assert that these cross-effects are always present or important. Their presence, magnitude, and consequences are properties of an instantiated HLS model.

---

## 4. Current source mappings

These mappings preserve source fidelity. They test whether relevant mechanisms from established theories can be represented by the common HLS ontology without changing the meaning of HLS variables.

They do not imply that any source defines an entire theoretical beam or that combining the sources establishes novelty.

### 4.1 Garicano (2000)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Worker | Agent in the production organization. | Agent/model. | `RELATED` | An HLS model must specify which worker attributes correspond to model properties. | Structural mapping only; a worker is not literally a learning model. |
| Problem `Z` | Draw from problem space `Q` with distribution `F`. | Task/problem and demand distribution `P_t`. | `RELATED` | Define the HLS task space and sampling process. | Source-grounded structural mapping. |
| Knowledge set `A_i` | Set of problems whose solutions worker `i` knows. | Particular extensive representation of competence state `S`. | `RELATED` | Define binary solvability or an explicit mapping between `S` and the task set. | It must not be identified with a generic scalar competence state. |
| `Z in A_i` | Binary ability to solve a problem in the base model. | Competence-dependent task solvability through `Psi`. | `RELATED` | A graded or probabilistic HLS model requires an explicit relaxation. | Does not itself define quality, accuracy, or speed. |
| Production worker / problem solver | Functional roles in a knowledge hierarchy. | Operational roles induced by `a_t`. | `RELATED` | Specify how allocation creates roles. | Does not mandate permanent learner/teacher model types. |
| Asking/referral | A worker unable to solve a problem consults another. | Operational allocation/interaction represented through `a_t`. | `RELATED` | Specify the HLS consultation, delegation, or escalation mechanism. | In the base model it is not learning or knowledge transfer. |
| Help cost `h` | Time/capacity consumed by the consulted worker. | Agent resource consumption `r_m,t`. | `RELATED` | Preserve time/capacity meaning or provide an explicit resource mapping. | It is not an arbitrary scalar utility penalty. |
| Output/problems solved | Production obtained by the organization. | Operational work/value `W`, `Y`. | `RELATED` | Define how solved problems map to HLS operational value. | Requires an explicit value mapping if tasks have heterogeneous value. |

Garicano supplies a primary reference for organization of knowledge, specialization, operational roles, escalation, and capacity consumption.

Its base model does not make communication a learning mechanism. Therefore it does not itself supply the HLS transition

```text
E_t -> S_t+1.
```

Garicano's knowledge set `A_i` and a scalar proficiency state used in another theory are not semantically interchangeable.

### 4.2 Gutjahr (2011)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Fixed team | Resource performing project classes. | Competence-bearing HLS resource/agent. | `RELATED` | Specify whether the HLS resource is one model, a group, or another unit. | Not automatically an individual model. |
| Project class | Class receiving a share of work capacity. | Task/work class in `Q`. | `RELATED` | Define correspondence to the HLS task space. | Does not itself define per-instance routing. |
| Competence score `z_it` | Scalar competence state for class `i` and period `t`. | Competence state `S`. | `RELATED` | Define the HLS competence scale and interpretation. | Must not be silently identified with Garicano's set `A_i`. |
| Efficiency `gamma_it = phi(z_it)` | Nondecreasing mapping from competence to productive efficiency. | Competence-to-expected-performance mapping `Psi`. | `RELATED` | Specify correspondence between efficiency and the HLS performance quantity. | Normalization does not make it an accuracy probability. |
| Real work `x_it` | Share of available work capacity assigned to class `i`. | Operational allocation/work `a`, `W`. | `RELATED` | Preserve capacity units and distinguish decision from realized work where necessary. | It is not ontologically identical to learning exposure. |
| Effective work `gamma_it x_it` | Productive work obtained from real work at current efficiency. | Operational value `Y` in a suitable realization. | `RELATED` | Define the HLS value/output unit. | Cannot be added to unrelated costs without a common value mapping. |
| Learning coefficient `eta_i` | Competence gain per unit of accumulated real work. | Parameter of competence transition `L`. | `RELATED` | If real work and learning exposure differ, introduce the explicit mapping `W -> E`. | Does not imply that all HLS work generates identical exposure. |
| Depreciation `beta_i` | Competence loss per period. | Forgetting/depreciation inside `L`. | `RELATED` | Match time units and competence scale. | Does not determine the appropriate forgetting law for HLS models. |

Gutjahr supplies an explicit realization of

```text
allocation/work
    -> experience
    -> competence evolution
    -> future efficiency.
```

Its competence dynamics are one possible realization of `L`; they do not define the general HLS learning law.

### 4.3 Argote and Miron-Spektor (2011)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Experience | Organizational experience acquired through task performance and other experience streams. | Learning exposure `E`. | `RELATED` | Specify which observed experience events are learning-relevant in the HLS model. | Experience is not identified with competence change. |
| Experience characteristics | Dimensions such as direct/indirect, success/failure, recent/old, and related characteristics. | Structure or attributes of `E`. | `RELATED` | Preserve relevant characteristics when they affect `L`. | The minimal HLS ontology retains direct/indirect exposure but allows richer structure when required. |
| Knowledge | Organizational knowledge produced, retained, or transferred through learning processes. | Competence state `S` or information affecting `S`, depending on the instantiated model. | `RELATED` | Define what part of organizational knowledge corresponds to agent competence. | Organizational knowledge is broader than an individual model's competence state. |
| Learning from experience | Process through which experience changes knowledge. | Competence transition `L(S,E,Delta t)`. | `RELATED` | Specify the learning mechanism quantitatively in an instantiated HLS model. | The source framework does not prescribe a unique mathematical transition law. |
| Knowledge transfer | Movement of knowledge across organizational units. | Mechanism generating indirect exposure `E_ind`. | `RELATED` | Define source, target, transferred information, and resulting exposure. | Transfer activity is not identical to competence gain. |
| Performance | Organizational outcomes affected by experience and knowledge. | Observed performance and operational value `Q`, `Y`. | `RELATED` | Define the HLS performance measure and value mapping. | The source does not define a unique HLS objective. |

Argote and Miron-Spektor support the fundamental HLS distinction

```text
experience != knowledge/competence
```

and the conceptual transition

```text
experience
    -> learning process
    -> changed knowledge/competence.
```

Their framework is broader than the minimal HLS mathematical model and does not impose a particular functional form for `E` or `L`.

### 4.4 Gibbons and Waldman (1999)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Worker | Individual with ability and accumulated human capital. | Agent/model. | `RELATED` | Specify which worker attributes correspond to HLS agent state. | Structural mapping only. |
| Job assignment | Assignment of workers to jobs with different returns to skill. | Operational allocation `a_t`. | `RELATED` | Map jobs to HLS task classes and assignment constraints. | The source setting is an internal labor market, not an HLS architecture. |
| Work experience | Accumulated experience obtained through employment. | Direct learning exposure `E_dir`. | `RELATED` | Define which operational work produces competence-relevant exposure. | Work experience is not automatically equal to competence. |
| Human capital | Productivity-relevant capability that grows with experience. | Competence state `S`. | `RELATED` | Specify the competence representation and transition. | Human capital contains economic interpretation not automatically inherited by HLS. |
| Human-capital acquisition | Increase in human capital through experience. | Competence transition `L`. | `RELATED` | Define the HLS learning law. | Does not prescribe knowledge transfer between HLS agents. |
| Worker output | Productivity of a worker in an assigned job. | Operational performance/value `Q`, `Y`. | `RELATED` | Specify task-specific performance and value. | Wages and promotions are not HLS performance measures. |

The relevant structural precedent is the loop

```text
assignment
    -> experience
    -> human-capital development
    -> future productivity and assignment.
```

This supports the possibility that operational allocation can influence future capability without implying that the source model supplies the HLS controller or objective.

### 4.5 Borgonjon and Maenhout (2024)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Personnel/resource | Worker available for task execution or training. | Agent/model. | `RELATED` | Map personnel properties to HLS agent properties. | Structural mapping only. |
| Task assignment/staffing | Allocation of personnel to operational work. | Operational allocation `a_t`. | `RELATED` | Define HLS task and capacity constraints. | The source solves a staffing problem, not generic model routing. |
| Training decision | Explicit allocation of time/resources to training. | Competence-development decision `d_t`. | `RELATED` | Define the corresponding HLS training/transfer mechanism. | Training action is not identical to resulting exposure or competence gain. |
| Learning through work | Competence improvement associated with task execution. | Direct experience `E_dir` followed by `L`. | `RELATED` | Specify exposure generated by work. | Particular learning law remains source-specific. |
| Training-induced learning | Competence improvement associated with training activity. | `d -> E -> L`. | `RELATED` | Separate the development action from resulting exposure and state change. | Must not identify `d`, `E`, and `Delta S`. |
| Forgetting | Competence loss when practice/training is insufficient. | Forgetting/depreciation within `L`. | `RELATED` | Match time and competence scales. | Particular forgetting dynamics are not universal. |
| Competence-dependent efficiency | Task efficiency affected by competence. | `Psi(q,S,X)`. | `RELATED` | Define the HLS performance interpretation. | Efficiency is not automatically quality probability. |
| Staffing/resource objective | Resources required to satisfy workload under dynamic competence. | `R`, `Y`, and scenario objective. | `RELATED` | Define HLS operational value and resource measures. | The source objective is not the universal HLS objective. |

Borgonjon and Maenhout provide a strong precedent for simultaneously modeling operational assignment, explicit training, learning, forgetting, competence-dependent efficiency, and resource consequences.

The HLS ontology can represent these mechanisms without introducing an additional fundamental variable.

### 4.6 Nembhard and Bentefouet (2015)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Worker | Heterogeneous production resource with learning characteristics. | Agent/model. | `RELATED` | Specify correspondence to HLS agent properties. | Structural mapping only. |
| Worker grouping | Organization of workers into groups enabling work and knowledge transfer. | Operational organization `a_t`. | `RELATED` | Define how HLS grouping/collaboration is represented by `a_t`. | Grouping is not a separate universal HLS state. |
| Worker assignment | Assignment of workers/groups to jobs. | Operational allocation `a_t`. | `RELATED` | Map jobs to HLS tasks. | Source constraints remain model-specific. |
| Direct experience | Experience accumulated through performing work. | `E_dir`. | `RELATED` | Define exposure units and relation to `W`. | Not identical to competence gain. |
| Knowledge transfer | Learning contribution obtained through interaction with other workers. | Indirect exposure `E_ind`. | `RELATED` | Preserve transfer source/target where relevant. | Transfer coefficient or transferred experience is source-specific. |
| Learning curve | Relationship between accumulated experience and productivity. | Competence transition `L` together with `Psi`, depending on representation. | `RELATED` | Separate accumulated exposure, competence state, and resulting productivity in HLS. | The source learning curve is one possible realization, not an ontological identity. |
| Productivity/throughput | Output generated by the workforce. | Operational value `Y`. | `RELATED` | Define task value and aggregation. | Throughput is one possible operational-value measure. |

The relevant HLS structure is

```text
organization/allocation
    -> direct and indirect experience
    -> learning
    -> future productivity.
```

The paper therefore supports representing operational organization as a determinant of both current output and future learning opportunities.

### 4.7 Jin, Hewitt, and Thomas (2018)

| Source concept | Source mathematical type and meaning | HLS concept | Mapping class | Required transformation / assumptions | Status and limits |
| --- | --- | --- | --- | --- | --- |
| Worker | Production resource with heterogeneous learning characteristics. | Agent/model. | `RELATED` | Specify HLS agent correspondence. | Structural mapping only. |
| Grouping and assignment | Decisions determining worker groups and jobs. | Operational organization/allocation `a_t`. | `RELATED` | Define HLS collaboration and task allocation. | Does not itself define an explicit HLS development action `d_t`. |
| Direct experience `D` | Experience accumulated by performing work. | `E_dir`. | `RELATED` | Preserve experience units and accumulation rule. | Not identical to competence. |
| Shared/transfer experience `S` | Experience available through knowledge transfer from other workers. | Source-dependent indirect exposure contributing to `E_ind`. | `RELATED` | Define the transfer mapping and avoid collision with HLS competence notation `S`. | Jin's symbol `S` must not be identified with HLS competence state `S`. |
| Transfer coefficient `theta` | Parameter controlling contribution of shared experience to effective experience. | Parameter of the exposure mapping `E`. | `RELATED` | Define how transferred information produces HLS learning exposure. | Does not define a universal HLS transfer mechanism. |
| Effective experience `c = D + theta S` | Combined direct and transferred experience entering the learning curve. | Model-specific aggregation inside `E`. | `RELATED` | Treat this equation as a particular realization of the HLS exposure function. | It must not be imposed on other HLS models. |
| Learning curve | Hyperbolic relation between experience and productivity. | Particular realization of `L` and/or `Psi`, depending on state representation. | `RELATED` | Explicitly distinguish exposure, competence, and performance in the HLS realization. | The curve is source-specific. |
| Output/throughput | Production obtained under grouping and assignment decisions. | Operational value `Y`. | `RELATED` | Define the corresponding HLS task-value measure. | Throughput is not the universal HLS objective. |

Jin, Hewitt, and Thomas provide an explicit realization in which grouping and assignment determine direct experience and opportunities for knowledge transfer, which then affect future productivity.

Their equation

```text
c = D + theta S
```

is a source-specific exposure aggregation. It does not justify identifying direct experience, transferred experience, competence state, or productivity.

---

## 5. Cross-source validation

The purpose of the reverse validation is to determine whether the HLS ontology can represent the relevant mechanisms of the source theories without changing the meaning of HLS variables.

The current result is:

| Source | Relevant HLS objects | Representable in current ontology? | Main role |
| --- | --- | --- | --- |
| Garicano (2000) | `S, a, W, Y, R` | Yes | Organization of knowledge, specialization, escalation, support cost. |
| Gutjahr (2011) | `S, a, W, E_dir, Y, L` | Yes | Work-dependent competence dynamics and future efficiency. |
| Argote and Miron-Spektor (2011) | `W, E, S, L` | Yes | Experience-to-knowledge distinction, retention, and transfer. |
| Gibbons and Waldman (1999) | `S, a, W, E_dir, Y, L` | Yes | Assignment, experience, capability development, future productivity. |
| Borgonjon and Maenhout (2024) | `S, a, d, E, Y, R, L` | Yes | Assignment, explicit training, learning, forgetting, resource consequences. |
| Nembhard and Bentefouet (2015) | `a, E_dir, E_ind, S, Y, L` | Yes | Grouping/assignment, learning-by-doing, knowledge transfer. |
| Jin, Hewitt, and Thomas (2018) | `a, E_dir, E_ind, S, Y, L` | Yes | Grouping/assignment, direct and transferred experience, throughput. |

No currently relevant mechanism from these seven sources requires a new fundamental HLS variable.

The validation also confirms several mandatory non-identifications:

```text
Garicano A_i != Gutjahr z_it

experience != competence

development action != indirect exposure

work != experience

competence != performance

resource consumption != latency

resource consumption != cost.
```

Each source therefore enters the HLS framework as a particular realization of some subset of the general mappings

```text
Psi
W
E
L
V
R
```

rather than by direct combination of source equations or variables.

The ontology is considered sufficient for the current stage of the programme. It should be modified only if a relevant phenomenon cannot be represented without changing the established meaning of an existing HLS object.

---

## 6. Joint and separate management

The two fundamental HLS decisions are:

```text
who does what
```

and

```text
who learns what and from whom.
```

They are represented by

```text
u_t = (a_t, d_t).
```

### 6.1 Joint management

Joint management selects operational allocation and competence-development actions while considering their coupled present and future consequences:

```text
(a_t, d_t) = pi_J(X_t).
```

The relevant coupled structure is

```text
(a_t, d_t)
    -> current operational performance
    -> experience
    -> future competence
    -> future operational performance.
```

In particular, operational allocation may affect future competence through

```text
a_t
    -> E_t
    -> S_t+1
    -> future performance,
```

while competence-development actions may consume resources or otherwise affect present operation through

```text
d_t
    -> Y_t, L_t, R_t.
```

### 6.2 Separate management

Separate management treats operational allocation and competence development as separate decision problems:

```text
pi_S = (pi_a, pi_d).
```

The separate baseline must use the same physical system, demand, feasible actions, resources, horizon, and evaluation criteria as joint management.

It must not be defined merely as a myopic or otherwise artificially weak policy.

The conceptual distinction is that separate management does not fully internalize the cross-effects between operational organization and competence development when optimizing the two subproblems.

This definition is intentionally general at the ontology level. A concrete theoretical model must specify precisely how the separate policy is constructed.

### 6.3 Central theoretical comparison

The theoretical objective is to characterize conditions under which

```text
J_J* = J_S*
```

and conditions under which

```text
J_J* > J_S*.
```

The existence of cross-effects alone does not establish strict superiority. They must be decision-relevant and sufficiently consequential to alter the optimal system behavior.

Conversely, when the relevant operational and competence-development effects are separable, joint management should not be expected to provide an advantage.

If the joint policy class simply contains the separate class, the weak inequality

```text
J_J* >= J_S*
```

is tautological. The scientific content therefore lies in meaningful policy definitions and in strict-advantage, equality, and no-advantage conditions.

---

## 7. Multiple theories per beam

The two beams are programme questions, not source models.

### Beam 1 — organization and use of competences

How available competences should be organized and used for current work.

Relevant mechanisms include:

```text
task allocation
specialization
collaboration
support
escalation
resource use
operational performance.
```

Garicano (2000) is a primary current reference for this beam, not its complete theory.

### Beam 2 — development and evolution of competences

How experience, learning, retention, training, and transfer affect future capability and cumulative system performance.

Relevant mechanisms include:

```text
direct experience
indirect experience
learning
knowledge transfer
training
retention
forgetting
competence evolution.
```

Gutjahr (2011) is a primary current formal reference for this beam, not its complete theory.

Argote and Miron-Spektor (2011), Gibbons and Waldman (1999), Borgonjon and Maenhout (2024), Nembhard and Bentefouet (2015), and Jin, Hewitt, and Thomas (2018) provide complementary foundations and, in several cases, mechanisms crossing both beams.

The beams are not assumed to be independent. Their interaction is precisely part of the HLS research question.

---

## 8. Anti-drift constraints

- Do not let Garicano dictate the HLS architecture.
- Do not let Gutjahr dictate HLS competence dynamics.
- Do not let any single source theory define an entire beam.
- Do not let B13 dictate RQ0 or the system objective.
- Do not identify variables across theories without an ontology mapping.
- Do not infer semantic compatibility from a shared numerical range, notation, or equation form.
- Do not combine quantities without compatible meaning and units or an explicit value transformation.
- Do not identify work with experience.
- Do not identify experience with competence change.
- Do not identify competence with observed performance.
- Do not identify a development action with the exposure it produces.
- Do not identify resource consumption with latency or economic cost.
- Do not count quality independently in the objective when its operational effect is already represented through `Y`.
- Do not reward competence directly unless the modeled objective explicitly requires terminal competence value.
- Do not claim novelty merely from combining source theories.
- Do not reject the programme because individual components are established.
- Do not define a weak separate-management baseline to manufacture joint superiority.
- Do not introduce a new HLS variable merely because a source uses a different representation.
- Introduce a new HLS variable only when a relevant phenomenon cannot be represented without changing the established semantics of existing variables.
- Map each new source independently into the HLS ontology before integrating its equations or mechanisms.
- Treat source-specific equations as realizations of HLS mappings, not as HLS identities.
- Do not turn this ontology into the research objective; it exists to support a coherent HLS system.

---

## 9. Current status

The ontology has been reverse-validated against the currently active source set:

- Garicano (2000);
- Gutjahr (2011);
- Argote and Miron-Spektor (2011);
- Gibbons and Waldman (1999);
- Borgonjon and Maenhout (2024);
- Nembhard and Bentefouet (2015);
- Jin, Hewitt, and Thomas (2018).

At the current level of abstraction, all relevant mechanisms identified from these sources can be represented without adding a new fundamental HLS variable or changing the semantics of an existing one.

The current canonical loop is therefore:

```text
X_t
    -> (a_t, d_t)
    -> {
         Z_t = (Y_t, L_t, R_t)
         E_t
       }
    -> S_t+1
    -> X_t+1.
```

with

```text
Z_t = (Y_t, L_t, R_t)
```

representing current physical system performance and

```text
S_t+1 = L(S_t, E_t, Delta t)
```

representing competence evolution.

Status of this document:

```text
HLS ONTOLOGY v1: CLOSED FOR THE CURRENT RESEARCH PHASE
```

"Closed" means that the ontology is now the default semantic and notational basis for subsequent HLS modeling. It does not mean that it is immutable. Changes require a concrete representational deficiency, not merely an alternative notation or a source-specific modeling preference.

The next research stage is to formulate the HLS mathematical model on this common basis and study when joint management of operational allocation and competence development improves system performance relative to scientifically meaningful separate management.