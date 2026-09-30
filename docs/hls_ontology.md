# HLS ontology and cross-theory mapping discipline

**Status:** canonical semantic, mathematical, and dimensional consistency layer for the Heterogeneous Learning Systems (HLS) programme. It is modeling infrastructure, not a research result, algorithm, architecture, or novelty claim.

## 1. Purpose

The HLS ontology provides a common semantic language for representing HLS phenomena and for translating theories, models, and mechanisms from different domains without silently changing their meaning.

Its role is downstream from the HLS philosophy:

```text
HLS PHILOSOPHY
      |
      v
HLS ONTOLOGY
      |
      v
RESEARCH QUESTIONS
      |
      v
THEORY / MODELS / EXPERIMENTS
```

The philosophy determines which phenomena matter to HLS. The ontology provides a consistent language in which those phenomena can be represented. It must not define the research programme through the variables required by a particular research question, model, experiment, or source theory.

Cross-domain theories must be mapped independently into the common HLS ontology before their variables or equations are integrated:

```text
Theory A ----\
Theory B ----- > HLS ONTOLOGY
Theory C ----/
```

Similar names, equation forms, normalizations, or numerical ranges do not establish semantic equivalence.

If a transformation `y = g(x)` is required to connect a source quantity to an HLS quantity, that transformation belongs to the instantiated HLS model and must be stated explicitly.

The methodological rule is:

```text
reuse what is established
    -> map it into the HLS ontology
    -> integrate what is compatible
    -> derive what is HLS-specific
    -> develop new theory only where necessary
```

### 1.1 Mapping record

For every relevant cross-domain mapping, record:

| Field | Required content |
| --- | --- |
| Source concept | Name used by the source theory. |
| Source definition | Meaning in the source model, not an HLS paraphrase. |
| Mathematical type | Set, scalar, vector, function, decision, random variable, resource flow, etc. |
| Units/range | Physical units or explicit normalization and admissible domain. |
| HLS concept | Target concept in this ontology, if any. |
| Mapping class | `EQUIVALENT`, `RELATED`, `INCOMPATIBLE`, or `UNRESOLVED`. |
| Required transformation | Explicit map needed when concepts are related but not identical. |
| Assumptions | Conditions under which the mapping is defensible. |
| Status | Appropriate epistemic label. |
| Notes/limitations | Inferences that the mapping does not support. |

Mapping classes mean:

- **EQUIVALENT** — the source and HLS objects represent the same kind of quantity under the stated assumptions and can legitimately be identified;
- **RELATED** — they are different objects connected by an explicit mapping or model;
- **INCOMPATIBLE** — they must not be identified;
- **UNRESOLVED** — the relationship has not yet been established.

A new source theory should first be mapped into the existing HLS ontology. New HLS concepts should be introduced only when a scientifically relevant HLS phenomenon cannot be represented faithfully without changing the established meaning of an existing concept.

---

## 2. Core HLS semantic objects

The ontology defines semantic objects, not a mandatory state vector or universal mathematical model.

A particular HLS model may use only a subset of these objects and may introduce additional state variables when scientifically necessary.

### 2.1 Agents and models

Let `M = {1, ..., M}` denote the set of agents or models participating in the HLS.

Agents may differ in competence, specialization, cost, latency, capacity, learnability, plasticity, reliability, role, access to information, or other properties relevant to the instantiated system.

The ontology does not assume that agents are interchangeable or that every agent can acquire every competence.

### 2.2 Tasks, problems, and demand

Let `Q` denote the task or problem space. A task presented at time `t` is denoted by `q_t in Q`.

The environment may generate tasks according to a time-dependent demand process such as `q_t ~ P_t`, where `P_t` represents current demand when a probabilistic representation is appropriate.

No stationarity assumption is imposed by the ontology. Tasks may change in frequency, importance, difficulty, composition, or type; new task classes may appear and old ones may disappear.

### 2.3 Competences

Let `K = {1, ..., K}` denote a set of competences when a discrete competence representation is appropriate.

The competence state of agent `m` may be represented as `S_m,t = (S_m1,t, ..., S_mK,t)`, with `S_mk,t in S_k`.

This is a useful representation, not a requirement that competence always be a scalar vector. A source or instantiated HLS model may represent competence through sets, scalars, vectors, latent variables, functions, distributions, structured objects, or another suitable representation.

The ontology does not require competence to be binary, scalar-normalized, directly observable, stationary, comparable across all competence dimensions, or measured in the same units across competences.

Most importantly:

```text
competence != performance.
```

Competence describes capability state. Performance describes what happens when that capability is used in a particular context.

### 2.4 Task requirements

A task `q` may require one or several competences. Its requirements may be represented by a model-specific object such as `r(q)`.

The ontology does not require task requirements and competence states to share the same mathematical representation or units. The relation between task requirements and agent competences must therefore be supplied by the instantiated model.

### 2.5 Expected operational performance

Expected performance when agent `m` participates in task `q` may be represented by

```text
Qbar_mq,t = Psi(q, S_m,t, X_t),
```

where `Psi` is a model-specific competence-to-performance mapping and `X_t` contains any additional relevant context.

The ontology does not impose linearity, additivity, independence, compensability, or any particular functional form for `Psi`.

### 2.6 Observed performance and quality

After processing a task, an agent or group of agents produces an observable outcome. Its quality may be represented by `Q_m,t = Q(q_t, result_m,t)`.

Therefore:

```text
S != Qbar != Q.
```

`S` is competence state, `Qbar` is expected performance under stated conditions, and `Q` is observed performance or quality.

### 2.7 Operational work

Operational work may be represented generically by `W_t`. It denotes work actually performed in executing or supporting operational tasks.

Depending on the instantiated system, it may be decomposed by agent, task, team, role, or activity.

Operational work is distinct from result quality, learning-relevant experience, operational value, and resource consumption:

```text
work != quality
work != experience
work != operational value
work != resource consumption.
```

### 2.8 Operational value

Operational outcomes may have different usefulness to the system. Operational value may therefore be represented generically by `Y_t`, with a model-specific mapping such as

```text
Y_q,t = V(q, W_q,t, Q_q,t, X_t).
```

The ontology does not impose a universal functional form for `V`.

Thus:

```text
quality != operational value.
```

### 2.9 Resources, capacity, and cost

Agent-level resource consumption may be represented by `r_m,t in R_+^p`. Components may represent compute time, energy, memory, tokens, communication, API usage, human intervention, or other physically or operationally meaningful resources.

Available capacity may be represented by `b_m,t in R_+^p` when such a representation is appropriate.

System-level resource consumption may be obtained through a model-specific aggregation `R_t = A_R(r_1,t, ..., r_M,t)`. Economic or scenario-specific cost may then be derived through a mapping such as `C_t = C(R_t, X_t)`.

Therefore:

```text
resource consumption != capacity != cost.
```

### 2.10 Latency and time

End-to-end task latency may be represented by

```text
L(q) = t_completion(q) - t_arrival(q).
```

Latency is distinct from total resource consumption. Thus:

```text
resource consumption != latency.
```

Other temporal quantities—deadlines, waiting time, service time, training time, synchronization delay, or horizon—may be represented separately when required.

### 2.11 Experience

Learning-relevant experience may be represented by `E_mk,t`.

When useful, it may be decomposed into direct and indirect experience:

```text
E_mk,t = (E_dir_mk,t, E_ind_mk,t).
```

`E_dir_mk,t` is experience obtained through the agent's own activity; `E_ind_mk,t` is experience obtained through information, interaction, observation, assistance, teaching, transfer, or another agent-mediated mechanism.

When source identity matters, indirect exposure may retain the form `E_ind_n->m,k,t`.

Crucially:

```text
experience != competence change.
```

The same experience may produce different competence changes for different agents, competences, states, or learning mechanisms. Some experience may produce no competence change at all.

### 2.12 Competence evolution

Competence may evolve according to a generic transition

```text
S_t+1 = L(S_t, E_t, X_t, Delta t),
```

where `L` is a model-specific competence-evolution mechanism.

It may represent learning, learning by doing, explicit training, knowledge transfer, saturation, retention, forgetting or depreciation, interference, heterogeneous learning rates, limited learnability, inability to acquire a competence, null change, or other justified competence dynamics.

The ontology therefore permits deliberate competence development as well as competence evolution that occurs as a consequence of operation.

---

## 3. Organization, use, and development decisions

The HLS philosophy distinguishes two foundational questions:

```text
Who should do what?
Who should learn what, how, and from whom?
```

The ontology must represent these questions without forcing every HLS into one particular controller architecture.

### 3.1 Organization and use

Let `a_t` denote, when useful, the decision describing how currently available capabilities are organized and used.

Depending on the instantiated HLS, `a_t` may represent or include task allocation, routing, collaboration, delegation, escalation, ensemble participation, team formation, assignment of roles, sequencing, supervision, redundancy, backup, resource allocation, or another form of operational organization.

`a_t` is therefore broader than routing.

The ontology does not require exactly one agent per task, a flat portfolio, a central omniscient router, permanent roles, or a particular organizational topology.

### 3.2 Development interventions

Let `d_t` denote, when useful, an explicit intervention intended to influence competence development.

Depending on the instantiated HLS, it may represent training, teaching, knowledge transfer, distillation, mentoring, deliberate exposure, rehearsal, competence replication, retention activity, or another justified development action.

Crucially:

```text
development action != experience
development action != competence change.
```

### 3.3 Generic decision representation

When both organization/use and explicit development interventions are decision variables, a useful decomposition is

```text
u_t = (a_t, d_t).
```

This is a generic modeling convenience, not a universal requirement or definition of HLS.

Some HLS models may have only organization decisions, with competence evolution arising through experience. Others may include explicit development decisions. Still others may require additional organizational, informational, or control decisions.

### 3.4 Feasibility

Feasible decisions depend on the instantiated system and its state. Generically:

```text
u_t in U(X_t).
```

When useful, this may be decomposed as `a_t in A(X_t)` and `d_t in D(X_t, a_t)`.

The dependence `D(X_t, a_t)` can represent the fact that organization creates, modifies, or prevents learning and interaction opportunities.

No universal feasibility structure is imposed by the ontology.

---

## 4. Generic HLS state and dynamics

The ontology does not prescribe one universal sufficient state representation.

Let `X_t` denote whatever state is required by a particular HLS model.

Depending on the problem, `X_t` may include objects such as `P_t`, `S_t`, `b_t`, `Theta_t` and, when relevant, organizational structure, roles, relationships, information state, history, resource state, environmental state, or other variables.

Thus a representation such as

```text
X_t = (P_t, S_t, b_t, Theta_t)
```

is one possible realization, not the ontological definition of HLS state.

The generic HLS causal structure is:

```text
changing needs / environment
            |
            v
           X_t
            |
            v
organization and use
+ possible development interventions
            |
            +--------------------------+
            |                          |
            v                          v
current operation              learning-relevant
and consequences                  experience
            |                          |
            |                          v
            |                 competence evolution
            |                          |
            +-------------+------------+
                          |
                          v
                        X_t+1
```

The ontology does **not** assert that every instantiated HLS contains strong cross-effects among these objects. Whether those effects exist, matter, or require joint optimization is a scientific question belonging to particular models and research questions.

---

## 5. Performance and objectives

HLS concerns effective and efficient collective problem solving under constraints, but the ontology does not prescribe one universal objective function.

Relevant performance quantities may include operational value, quality, latency, resource consumption, capacity utilization, economic cost, reliability, robustness, adaptability, deadline satisfaction, learning cost, or other application-dependent quantities.

For current models, a useful physical performance representation may be

```text
Z_t = (Y_t, L_t, R_t),
```

with orientations such as maximizing `Y` and minimizing `L` and `R`. This is a modeling choice, not a universal HLS identity.

When scalar optimization is required, constrained formulations can avoid arbitrary trade-off weights. A scalar utility may instead be introduced when scientifically justified. No particular scalarization is imposed by the ontology.

Competence should not normally be rewarded merely because more competence appears desirable. Its value generally arises from how it affects present or future system performance. A terminal competence value may nevertheless be appropriate when the modeled application or horizon explicitly gives residual capability intrinsic value.

---

## 6. Mandatory semantic distinctions

The following distinctions are foundational to the current HLS ontology:

```text
competence != expected performance
expected performance != observed performance

work != experience
experience != competence change

development action != experience
development action != competence change

quality != operational value

resource consumption != capacity
resource consumption != cost
resource consumption != latency

organization/use decision != competence-development decision
```

These are semantic distinctions, not claims that the corresponding quantities can never be related.

An instantiated model may define explicit mappings such as:

```text
competence -> expected performance
work -> experience
development action -> experience
experience -> competence change
quality -> operational value
resources -> cost
```

but those mappings must be stated rather than assumed.

In particular, a shared numerical range does not establish semantic equivalence. Two quantities normalized to `[0,1]` remain different quantities unless their meanings and admissible identification have been justified.

---

## 7. Cross-theory mapping discipline

External theories enter HLS as possible realizations of subsets of the ontology.

They must not be integrated by directly equating source-specific variables merely because the variables appear mathematically similar.

The required procedure is:

```text
source theory
      |
      v
independent semantic mapping
      |
      v
HLS ontology
      |
      v
compatible HLS realization
```

When several theories are combined:

```text
Theory A ----\
Theory B ----- > HLS ONTOLOGY -> instantiated HLS model
Theory C ----/
```

Each theory must first be mapped independently. Only then may compatible mechanisms be integrated.

Source-specific equations should normally be interpreted as realizations of generic HLS mappings such as:

```text
Psi   competence -> expected performance
E     operation/intervention -> learning-relevant experience
L     competence + experience -> future competence
V     operational outcome -> operational value
R     activity -> resource consumption
```

Detailed mappings of individual source theories belong in the cross-domain theoretical-foundations documentation rather than in the core ontology.

---

## 8. Ontology extension rule

The ontology is intended to be stable but not immutable.

A new HLS concept or variable should **not** be introduced merely because a source paper uses different notation, a source model separates a quantity that HLS can already represent, a new mathematical formulation is convenient, a normalized quantity appears different, or a particular experiment uses an implementation-specific state variable.

Extension is justified when all of the following hold:

1. the phenomenon is genuinely relevant to the HLS philosophy;
2. the phenomenon cannot be represented faithfully with the existing semantic objects;
3. forcing it into an existing object would change that object's established meaning;
4. the new concept has a clear definition and relationship to existing ontology objects.

Ontology growth should follow scientific need, not source vocabulary.

---

## 9. Relationship to the two HLS beams

The ontology supports the two foundational beams defined by the HLS philosophy.

### Beam 1 — Organization / use of competences

The ontology provides objects for representing tasks, competences, organization, roles, work, performance, value, resources, capacity, and latency without prescribing one particular organizational mechanism.

### Beam 2 — Development / evolution of competences

The ontology provides objects for representing experience, development interventions, learning, transfer, retention, forgetting, interference, and competence evolution without prescribing one particular learning mechanism.

The ontology also permits the two beams to interact:

```text
organization/use
      -> experience
      -> competence evolution
      -> future organization/use
```

Whether those interactions require integrated management is not an ontological assumption. It is a scientific question.

---

## 10. Status

The current ontology is sufficient for the current research phase.

Detailed source-by-source validation belongs in the cross-domain theoretical-foundations documentation.

The canonical semantic scaffold is:

```text
changing needs / environment
            |
            v
           X_t
            |
            v
organization / use
+ optional development interventions
            |
       +----+----+
       |         |
       v         v
 current       experience
 operation       |
       |         v
       |     competence
       |      evolution
       |         |
       +----+----+
            |
            v
           X_t+1
```

This scaffold is intentionally more general than any current RQ0 model, G0 implementation, or imported theory.

**Status: canonical and stable.**

The ontology should be extended only when a scientifically relevant HLS phenomenon cannot be represented faithfully with its existing semantic objects.

It should not be changed merely to accommodate alternative notation, source-specific modeling preferences, or the needs of a single experiment.
