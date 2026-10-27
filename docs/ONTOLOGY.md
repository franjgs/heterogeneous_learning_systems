# HLS scientific ontology

This ontology is an operational semantic contract for describing studies and checking whether components can be combined. It is not a universal theory of organizations and does not require every model to instantiate every concept. A source model may use different terms or richer objects; its mapping must be recorded rather than assumed.

## 1. Four scientific responsibilities

| Class | Scientific object | Identity criterion |
|---|---|---|
| **Scenario** | A problem setting: task population, environment or demand law, and relevant constraints. | Two scenarios are identical only if their scientifically relevant task, environment, information and constraint contracts match. Parameter variants may be grouped as one scenario family only when the varying parameters and invariant structure are explicit. |
| **Organization** | A set of agents or other work-bearing entities plus roles, access, capacity and coordination structure. | Equality requires the same member/role structure and feasible collective actions, not merely the same number of members or skill marginals. |
| **Model** | A formal or computational representation with variables, assumptions, outcome/transition laws and a scope. | Models are equivalent only if there is a semantics-preserving mapping between their states, feasible decisions, outcomes and evaluated quantities over the claimed domain. |
| **Performance evaluation** | A specification of outcomes, population, horizon, estimand, metric, aggregation and comparison/inference procedure. | A metric name alone does not establish evaluation equivalence; denominator, unit, horizon and sampling unit must also match. |
| **Implementation** | Executable code realizing some declared model, policy or evaluation procedure. | It is evidence about a model only after conformance is checked; code is not itself the mathematical model or scientific result. |

These are not mandatory software packages. An experiment instantiates a model for a scenario and organization under an evaluation contract; a study may contain multiple experiments.

## 2. Entity definitions and boundaries

| Concept | Operational definition in HLS | Important boundary |
|---|---|---|
| **System** | The entities and processes inside a declared boundary, interacting with an environment through specified inputs and outputs. | Boundary is model-dependent; do not infer it from a software repository. |
| **Agent** | An entity that may observe, decide, receive work, act or contribute to an outcome. | Does not imply human-like cognition or independent autonomy. |
| **Capability** | A relation or set of outcomes attainable by an entity or organization under declared tasks, policies, resources, information and constraints. | Not a scalar measurement by default. |
| **Competence** | A modeled disposition, parameter or state associated with performance on a specified task under stated conditions. | May be latent, stochastic, multidimensional or non-comparable across tasks. It is not capability, productivity, accuracy or an individual outcome without an explicit mapping. |
| **Skill** | A domain-specific learned or possessed ability as defined by a source model or application. | Related to competence; not identified with it unless operational definitions and measurement agree. |
| **Task** | A demand instance requiring an outcome, possibly with type, arrival, deadline, resource need and reward. | A task class groups instances; a problem is the broader decision/optimization question. |
| **Problem** | A question about feasible decisions or system behavior under a scenario and objective/evaluation. | Not itself a scenario or model. |
| **Environment** | Exogenous or partially exogenous conditions and stochastic mechanisms affecting demand, observations, transitions and outcomes. | Exogenous is relative to the model boundary. |
| **State** | A representation sufficient for the model's declared transition or decision semantics. | State sufficiency is model-specific; hidden variables may remain. |
| **Resource** | A quantity with unit, availability rule and consumption/accounting boundary. | Time, money, compute and human effort cannot be added without a conversion model. |
| **Constraint** | A predicate restricting admissible state, action, outcome or resource use. | A deadline, capacity, budget and information restriction are distinct. |
| **Organization** | Arrangement of entities, roles, access and coordination rules defining feasible collective action. | Organization is not the policy that chooses among feasible actions. |
| **Role** | A relation assigning responsibilities, authority or access to an entity in an organization. | Role labels do not themselves guarantee competence or performance. |
| **Coordination** | Management of dependencies among actions, tasks or resources. | May be explicit or embedded in a policy; it has no presumed benefit. |
| **Cooperation** | Joint contribution by multiple agents to one task or shared outcome under a specified protocol. | Assignment of separate tasks to different agents is not cooperation. |
| **Specialization** | Structured variation in capability/competence across task dimensions relative to a declared reference. | Heterogeneity is broader; heterogeneity need not be specialization. |
| **Policy** | A mapping from an allowed observation/history and state to a decision or action distribution. | A policy is not an organizational structure, and its information set is part of its semantics. |
| **Decision / action** | A choice at a decision point; an action is its modeled execution or intervention. | Neither is the resulting observation or outcome. |
| **Observation** | A signal available to an agent or policy under a declared observation process and time. | An observation may be noisy, delayed, selective or missing. |
| **Information** | A decision-relevant signal or information structure, including what is available and when. | True state, a posterior belief and observed data are different objects. |
| **Belief** | A probability distribution or other uncertainty representation over unknown states/parameters, conditional on information. | It is not the unknown state itself. |
| **Dynamics** | A rule governing state, environment or system evolution over time. | Time variation alone is not learning. |
| **Experience** | An event or observation generated by participation, exposure or action. | Experience does not entail competence change. |
| **Learning** | A specified update of knowledge, competence or another learning state driven by observations/experience or intervention. | Updating a policy/belief can be learning in some source theories; HLS records which state changes. It is not synonymous with adaptation. |
| **Development** | An intervention intended to change a capability/competence state, with costs and transition law specified. | Training is not assumed to succeed or transfer. |
| **Adaptation** | A change in policy, parameters or organization in response to observations or context. | Can occur with fixed competence and need not improve performance. |
| **Performance** | An outcome or vector of outcomes under a task, environment, organization, policy, horizon and population. | Collective attainable capability is not realized collective performance. |
| **Utility** | A declared preference/aggregation over consequences, when the model needs one. | Utility is not automatically accuracy or social welfare. |
| **Cost** | A measured or modeled burden with unit and accounting boundary. | Operational resource use and compute consumed by analysis/simulation are separate. |
| **Risk** | A declared probability, loss, tail measure or other adverse-outcome functional. | The exact functional and population must be stated. |
| **Uncertainty** | Aleatory variability, epistemic uncertainty, partial observability or parameter uncertainty, named separately. | A confidence interval does not itself define the underlying uncertainty source. |
| **Evaluation** | Protocol specifying estimand, metrics, population, horizon, comparator, sampling unit and inference. | Not interchangeable with an experiment. |
| **Metric** | A function of observations or outcomes with declared scale and unit. | Does not alone define the scientific estimand. |
| **Estimand** | The precise target quantity answering the study question, including population, conditions and contrast. | Must be defined before interpreting an estimate. |
| **Experiment** | A configured execution or intervention protocol intended to estimate or test a claim. | Experiment is not result; a simulation is not empirical evidence about real settings by default. |
| **Study** | A bounded scientific inquiry, potentially containing theory, experiments and multiple results. | Execution status differs from scientific outcome. |
| **Scientific result** | A claim with a derivation or evidence basis, scope and uncertainty/limitations. | A reported number without provenance is not an established result. |
| **Evidence** | Proof steps, exact computation, data, observation or literature source supporting or challenging a claim. | Evidence and conclusion are distinct; evidence can be insufficient or contradictory. |

## 3. Canonical relations and constraints

The catalog uses typed edges. Current canonical relation names and their domain/range are:

| Relation | Domain → range | Meaning and constraint |
|---|---|---|
| uses | study → scenario, organization or model; model → scenario; experiment → policy | The source is instantiated with or uses the target. Does not assert compatibility beyond the recorded study. |
| evaluated_by | study → evaluation | The study declares the target evaluation. |
| evaluated_in | organization → scenario | The organization is assessed in that scenario. |
| compares | study → policy | The policy is a comparator in the study; no performance ranking implied. |
| study | experiment/result/theoretical_result → study | The target study owns or contextualizes this record. |
| from | result → experiment | The result was derived from this experiment. |
| from_study | result → study | Result provenance points to the study; it does not substitute for primary evidence. |
| belongs_to | theoretical_result → study | The theory record is scoped to that study. |
| supports | experiment → theoretical_result | The experiment provides evidence relevant to the theory record, not necessarily a proof. |
| informed_by | scenario → study/result/theoretical_result; study → study/result/theoretical_result/model | A prior source motivates or constrains the design. It does not assert direct evidence for the target scenario, implementation reuse, equivalence, or validation. |

Edges must target existing identifiers, must not self-reference, and must respect the domain/range table. Stronger claims such as equivalence, causation or generalization require explicit evidence and cannot be inferred from an edge called uses.

The table specifies only cardinalities justified by this repository's representation: every edge has one source and one target; entities may have zero or more typed edges. The ontology does not impose that a study use exactly one model/scenario or that a model have exactly one implementation. An experimental protocol may impose stricter cardinalities for its own design.

Scientific claims in prose/catalog entries should identify the relevant source, evidence type and scope. An entity may lack implementation or evidence; the absence must remain explicit rather than filled with a guessed link.

## 4. Semantic compatibility, equivalence and transformation

Two components may be composed only after checking:

1. **Type and role:** the output object of one is a valid input to the other.
2. **Meaning:** variables denote the same kind of quantity, or an explicit map is supplied.
3. **Units and scales:** units, normalization, time step and aggregation are compatible.
4. **Information:** a policy uses only signals available at its decision time; no true-state or future leakage is introduced.
5. **State and dynamics:** transition assumptions and observation timing agree or are translated with a justified model.
6. **Feasibility:** resource and organizational constraints remain satisfied after composition.
7. **Evaluation:** estimand, denominator, population, horizon and cost boundary are preserved.
8. **Validation:** tests or derivations verify any transformation and its edge cases.

Use mapping labels EQUIVALENT, RELATED, INCOMPATIBLE or UNRESOLVED. Equivalence requires a semantics-preserving mapping over the declared domain, not matching names or similar equations. Related objects need an explicit transformation. Incompatible objects remain separate. Unresolved mappings cannot support a combined scientific claim.

For example, a deterministic finite allocation's scalar effectiveness is not interchangeable with a queue model's probability of correctness before deadline. A transformation would need to represent service time, arrivals, queues, admission, deadlines and the evaluation denominator. Without it, the components are related at a broad allocation-question level but mathematically incompatible as direct outcome quantities.

## 5. Common notation (translation shell, not universal model)

For models that admit it:

- agents: \(i\in\mathcal A\);
- task instances: \(x\in\mathcal X\), task class \(k\in\mathcal K\);
- time: \(t\in\mathcal T\), with model-declared units;
- scenario: \(\sigma\), organization: \(o\), model: \(m\), policy: \(\pi\);
- state: \(s_t\), observation/history available to a policy: \(h_t\);
- action: \(a_t\in\mathcal F(o,s_t,\sigma)\);
- outcome: \(Y_t\sim P_m(\cdot\mid s_t,a_t,\sigma)\);
- resources: vector \(r_t\), with component-specific units;
- transition, when present: \(s_{t+1}\sim T_m(\cdot\mid s_t,a_t,\xi_t)\);
- evaluation target: \(J_{m,\sigma,o,\pi,\theta}\), where \(\theta\) states population, horizon and aggregation.

Competence may be a task- and state-conditional map, e.g. \(q_i(k,s_t,\sigma)=P(Y=1\mid i,k,s_t,\sigma)\), only when the outcome is binary and that interpretation is justified. A deterministic score, latent skill vector or feasible-outcome set must retain its own type. HLS does not impose Markovianity, stationarity, scalar utility or probabilistic competence universally.

## 6. Worked example: deadline-constrained assignment

Consider a scenario with incoming tasks from four classes, a finite horizon, a task deadline and stochastic service/correctness. Its contract states arrival law, task labels, service law, deadline, queue discipline and rejection rule. An organization consists of agents with fixed task-conditioned competence, one service slot each and one FCFS queue per agent. A model defines service completion and correctness distributions and the state transitions when tasks arrive, start and finish. A policy sees current task class and observable queue/load information, then selects an eligible agent; it must not see future service times or outcomes. Evaluation estimates the fraction of all arrived tasks completed correctly by their original deadlines and separately reports waiting, rejection, tardiness and service cost.

The four levels connect as: scenario defines tasks and constraints; organization defines feasible service structure; model predicts transitions/outcomes; evaluation maps the resulting trace to estimands. Changing the policy does not change the organization unless the feasible roles/access change. This example illustrates how the CE-04 family is represented; its synthetic results do not validate a real workplace.

## 7. Link to scientific theories

The ontology is a crosswalk, not a claim of theoretical novelty. Assignment and scheduling formalize feasibility and resource allocation; MDPs formalize state, action, transition and return; bandit theory handles sequential decisions with partial feedback; Blackwell's comparison of experiments concerns information quality; organization and coordination theory explain dependencies and structures; queueing theory models arrival/service load; organizational-learning theories study experience, retention and transfer. These connections and their assumptions are discussed in [Literature](LITERATURE.md) and keyed in [the bibliography](../references/hls.bib).

## 8. Catalog enforcement

registry/catalog.json records entity classes, typed relations, assumptions, historical aliases, source provenance and selected ontology classes. hls validate checks unique IDs, relation domains/ranges, targets, local paths, bibliography keys and evidence/status fields. This is a consistency check, not a proof that a semantic mapping is scientifically correct. The responsible study must justify substantive mappings.
