# HLS Laboratory — Research Framework

**Recorded:** 2026-10-16 11:14:43 +02:00 (Europe/Madrid)
**Purpose:** consolidate the conceptual and experimental framework for
multiple HLS investigations. This is an audit and roadmap, not a claim of
scientific novelty, not a campaign registration, and not implementation
authorization. HLS Laboratory v1 remains **PARTIAL**.

> **Scope note (2026-10-24):** this dated framework records a particular
> laboratory design and its research framing. Its questions about current
> organization/use and competence development are scoped research questions,
> not defining pillars of HLS. The programme-level identity and four-level
> conceptual architecture are set out in [HLS Philosophy](HLS_PHILOSOPHY.md).

## 1. Scope and design principle

HLS studies how heterogeneous collectives organize, coordinate, and develop
capabilities while responding to changing problems. Its central questions
remain **WHO SHOULD DO WHAT?** and **WHO SHOULD LEARN WHAT, HOW, AND FROM
WHOM?** The laboratory is an experimental instrument: conclusions are
conditional on its declared entities, transition laws, information, feasible
actions, and evaluation measures. A model fixture can validate an instrument
property; it is not by itself evidence about real organizations.

The laboratory should keep five components replaceable and make their
dependencies explicit:

| Component | Contract | Inputs and outputs | Current dependency boundary |
|---|---|---|---|
| **Organization** | Agent roster, real capability state, public/estimated state, learning parameters and optional relationships. | Initial state/configuration; evolves only through declared mechanisms. | `ExpertState`, `TeamState`, `LearningProfile`, and `TeachingEfficacy` provide a fixed 3-agent × 2-skill representation. Teaching efficacy is directed and relationship-indexed; no general organization/network object exists. |
| **Decision policies** | Select a feasible joint action from public information and policy memory. | `IntegratedDecisionView` + organizational memory → `IntegratedAction`. | `IntegratedPolicy` is a real interface. Current P0/P1/P2 and action validation are implemented in `hls_lab_v1_integrated.py`; P0 is myopic functional ranking, not CES optimization. |
| **Learning mechanisms** | Transform private capability after declared production/teaching exposure; produce observations separately. | Prior real state + action + configured parameters → next real state and observable signals. | MIS-v2 is reused through `advance_team`; directed teaching is a separate transition in the same runner. Order is production → MIS-v2 → teaching. No general mechanism plug-in API exists. |
| **Environment** | Generate exogenous problem arrivals, requirements, and resource constraints. | Config + seed → frozen `EnvironmentTrajectory`; latent states are experimenter-only. | `ExogenousEnvironmentConfig` composes C5 stationary, nonstationary, and Markov demand with `DemandRegime`/`generate_problems`; policy runs do not alter future demand. |
| **Evaluation** | Compute outcomes from realized production/actions and retain a complete trace. | Problem, true output, action and resource use → functional result, gross CES, effort/cost, competence/information trace. | `evaluate_problem`, DISCOVER `ces_reward`, and integrated episode records are executable. Metrics are separate; no agreed scalar net utility or generic evaluator plug-in is supplied. |

Required causal flow: **environment emits public problem → policy sees only
declared observations and chooses a feasible action → mechanisms update private
capabilities and generate observations → organization updates its information
→ evaluator records outcomes → next exogenous problem arrives**. The
environment must not read organizational state; policies must not read private
competence, teaching efficacy, future demand, or latent regime labels.

Architecture (roster/capability distribution), policy (decision rule),
mechanism (state transition/information update), scenario (demand/problems/
resources), and evaluation (outcome contract) are distinct experimental
factors. A comparison must state which factor changes and match the others.

## 2. Current implementation map and limits

Evidence below refers to executable code, not planned descriptions.

| Area | Implemented now | Hard-coded or coupled assumptions | Scientific consequence |
|---|---|---|---|
| Agents and competencies | Real and estimated competence, experience, and performance are represented separately; information modes and bounded discrete posteriors exist in `hls_lab_dynamic.py`. | `TeamState`, `LearningProfile`, estimator state, production kernel and teaching efficacy all require exactly 3 agents × 2 skills. | Architecture comparisons are possible inside this geometry; claims about team-size/skill-count effects are blocked. |
| Production/tasks | Additive `Y_k=Σ_i x_ik c_ik`; explicit two-skill requirements, CES weights, functional success/deficit/margin; frozen discrete `JOINT_ACTIONS`. | One problem and one decision per period; one additive production kernel; fixed 64-action catalog. No queue of concurrent tasks or nonlinear interaction. | Specialization and multidimensional coverage can be tested, not superadditive synergy, concurrent project coordination, or alternative production technologies. |
| Assignment/policies | P0 chooses a feasible action by success, deficit, margin, effort; P1 applies a specified teaching relation; P2 explores configured teaching relations and uses observed efficacy estimates. Common `IntegratedPolicy` protocol; policies cannot access private truth through the view. | One central policy selects a full joint action. P0's objective differs from gross CES and has no intertemporal value. P1/P2 combine production and teaching choices; no distinct task-development assignment policy is implemented. | P0/P1/P2 are not interchangeable tests of “coordination”; comparisons identify specified policy packages only. |
| Learning/teaching | MIS-v2 individual learning by productive exposure; directed learner gain indexed by instructor × learner × skill; configurable independent observation noise; competence and efficacy information can update. | MIS-v2 rates are configured; efficacy is fixed private truth; one lesson maximum per period; transitions are composed inside the runner. No learned teaching efficacy ground truth or general transfer topology beyond the dense indexed relation table. | MIS × teaching toggles and conditional relation experiments are expressible. General peer learning, multiple modalities, and empirical calibration are absent. |
| Environment | C5 stationary IID, nonstationary, and first-order Markov task processes; fixed exogenous trajectories; separately keyed emission stream. | Current problem requirements are public. Environment beliefs/latent-regime inference are not integrated into the policy view; environment innovations are limited to demand/emission (real production is deterministic). | Can test response to known current problems and exogenous temporal structure. Cannot yet test organization learning an unknown demand regime or robustness to noisy realized production. |
| Resources | Per-problem shared effort budget, per-agent cap, production plus instructor/learner teaching charges; consumed and unused effort recorded; explicit cost-per-unit field. | Frozen discrete catalog can strand capacity; cost is not subtracted from gross CES; no carryover, inventory, deadlines, or common calibrated utility unit. | Fairness of available constraints can be enforced, but equal budget is not equal consumption and resource-normalized CES is descriptive rather than welfare. |
| Evaluation/traces | Functional success, normalized deficit, margin, gross CES, resource use/cost, competence estimates/variance, true skill diagnostics, action and teaching traces; deterministic serialization and snapshots. | Evaluator is composed into the runner; policy ranking is not the primary outcome; no universal aggregate performance score. Some true-state fields are privileged diagnostics, never decision inputs. | Outcome vectors and paired contrasts are possible; resource trade-offs must remain separate absent justified conversion. |
| Reproducibility | Frozen problem sequences, coordinate-indexed observation innovations, deterministic runner/serialization, snapshot branching, manifests/hashes in campaign tooling. | Seeds do not automatically create variation in every mechanism; deterministic replicates are not independent. Campaign scripts and schemas are study-specific. | Paired instrument checks are strong; independent replication must be defined by exogenous trajectories/declared random streams, not seed count alone. |

## 3. Experimental capability matrix

| Capability | Status | Evidence and boundary |
|---|---|---|
| Compare organizational architectures | **PARTIAL** | `make_team` accepts different competence matrices, but only 3×2. Q1 preflight exactly matched homogeneous/tilted skill and agent totals and enumerated frontiers. No generic roster/relationship topology. |
| Compare task-assignment policies | **PARTIAL** | `IntegratedPolicy` allows policies to be swapped; current integrated set primarily contrasts production-only and teaching rules, not a family of matched assignment/development policies. P0 uses a fixed functional lexicographic score. |
| Compare learning policies | **PARTIAL** | MIS ON/OFF and teaching interventions are configurable; learning rates are per cell. The mechanism family is narrow and transition choices are runner-coupled. |
| Isolate learning mechanisms | **PARTIAL** | Campaign 2's C00/C10/C01/C11 factorial toggled teaching and MIS with common demand and P0 continuation. It identifies conditional total factorial contrasts, not mediated shares; Campaign 1 traces expose resource displacement and gains. |
| Evaluate changing environments | **IMPLEMENTED** | C5 stationary, nonstationary and Markov processes plus environment freezing support controlled exogenous changes. Inference about an unknown environment is not implemented in the integrated policy. |
| Measure organizational adaptation | **PARTIAL** | P2 changes relation choices using observations; traces record estimates and choices. Adaptation is a particular heuristic, not evidence that the organization infers a general strategy or latent demand. |
| Reproduce paired experiments | **IMPLEMENTED** | Frozen trajectories, indexed random innovations, stable serializers and source/result manifests are used in CE24/25, Campaigns 1–2 and Q1 preflight. Must still distinguish demand-path replication from noise replicates. |
| Negative/equivalence controls | **IMPLEMENTED** | Acceptance tests, behavior-plausibility fixtures, Campaign 2 zero-efficacy/no-MIS controls, and Q1 preflight equivalence/frontier controls exist. Controls are study-specific and should be registered per claim. |

Evidence cautions: Campaign 2's ten observation-noise replicates had distinct
observation/estimate traces but generally identical action and CES paths,
because estimate perturbations did not cross P0 decision boundaries; action
ties in one condition were output-equivalent. Q1 preflight found the registered
24-period MIS-OFF architecture × persistence estimand structurally null.
Q1-R's separate exact two-period fixture established that current P0/MIS can
express a nonzero interaction (−.003 CES) under another explicit configuration;
it is an existence check, not a campaign result. Campaign 1/2 findings and
validity documents remain authoritative for their results and limitations.

## 4. Generalization requirements and boundaries

These are requirements for a research laboratory that serves multiple
questions, not a demand to implement every feature immediately.

| Change | Classification | Minimum bounded change and reason |
|---|---|---|
| Configurable agent count and competence dimension | **ESSENTIAL** for broad HLS comparisons; not needed to reproduce the existing 3×2 studies | Generalize state/action/learning shapes together, retaining a strict 3×2 compatibility path and exact regression fixtures. This is the main current structural ceiling on architecture research. |
| Pluggable assignment/coordination policy | **ESSENTIAL** | Preserve the existing `IntegratedPolicy` pattern but separate policy state from environment/mechanism parameters; compare policies on the same public view, feasible set and objective contract. Avoid importing a policy's privileged information as an apparent advantage. |
| Pluggable learning mechanisms | **ESSENTIAL** for comparing development mechanisms; not an excuse for a generic framework | Define a narrow transition contract over private state/action/parameters plus separately declared observations. Keep MIS-v2 and teaching adapters byte/behavior compatible. The current runner composes transitions internally. |
| Configurable task structures | **USEFUL**, with task batching essential only for studies of concurrent coordination | Retain one-task-per-period as a supported baseline. Add queues, deadlines, split/merge or nonlinear task structure only when a question requires them and resources can be accounted consistently. |
| Configurable demand processes | **IMPLEMENTED** for known exogenous IID/nonstationary/Markov cases | Reuse C5; do not duplicate generators. Unknown-regime inference is a separate useful capability, not required for known-demand studies. |
| Consistent resource accounting | **ESSENTIAL and substantially implemented** | Preserve shared/per-agent feasibility and report available, consumed, displaced, and stranded resources separately. Do not subtract arbitrary cost coefficients from CES. Carryover/monetary cost needs application-specific evidence. |
| Separate evaluator/outcome contract | **USEFUL / near-term** | Extract only if needed to reuse common trace metrics across runners; keep success, CES, resource use, and development as separate outcomes. Avoid a universal scalar objective. |
| Generic relationship/network structure | **DEFER** until a specific relational-coordination question | Current directed efficacy table supports relation-indexed teaching only. Add network constraints or changing ties only with a defined application/question. |
| Concurrent multi-task queues | **DEFER** for sequential demand questions; **ESSENTIAL** for portfolio/scheduling questions | Current one-problem-per-period model cannot represent backlog, deadlines, or parallel coordination. A queue and task-level assignment action are the minimum for those studies. |
| Realized stochastic production / forgetting | **DEFER** | Current production and MIS are deterministic. Add only if robustness or volatility is the target; otherwise it creates extra random streams and confounding. |
| Optimization frameworks, deep RL, universal APIs | **DEFER** | No present scientific question requires them; they would increase validation and reproducibility burden. |

The essential near-term direction is bounded generalization of **state/action
geometry, policy substitution, and mechanism composition**, not broader
realism. A compatibility suite must show that the existing 3×2 actions,
production, outcomes, MIS and historical experiment artifacts remain unchanged.

## 5. Research question portfolio

Each question is a possible study family, not a campaign registration.

| Question | Objective and factors | Minimum controls/outcomes | Current support | Remaining capability |
|---|---|---|---|---|
| **Q1 — Organization and competence distribution** | How do capability distributions with matched aggregates affect collective outcomes under task mixes/persistence? Vary architecture × demand structure; hold policy/mechanisms fixed. | Equal agent/skill totals, budgets, learning rates, information and frozen task paths; report frontiers, gross CES, success, resources, development. | 3×2 roster comparisons, P0, C5 and frontier enumeration. Q1 preflight and Q1-R show the registered MIS-OFF primary is null while a different short MIS-on interaction is expressible. | Variable team/skill sizes; architecture equivalence/relabeling and scalable action generation. No campaign should proceed from a fixture alone. |
| **Q2 — Assignment and capability development** | When is current production assignment versus development-oriented assignment better over a finite horizon? Vary assignment rule × MIS, not the mechanism and policy together. | Same architecture, information, resources, demand and terminal horizon; report current production and later capability separately. | MIS-v2 exposure transition, P0 and full traces; theoretical conditional comparisons in the minimal model. | A matched non-greedy development assignment baseline or exact small-instance benchmark with the same objective/information. Current P0 is not a causal control for an unimplemented policy. |
| **Q3 — Teaching and knowledge transfer** | When does directed transfer add value beyond work experience? Vary teaching × MIS × efficacy/demand only as justified. | Matched intervention, no-teaching arm, zero-efficacy control, indexed innovations, direct teaching/MIS gains, displaced production, residual effort and later assignments. | Teaching event, private relation efficacy, observations/memory, P0/P1/P2; Campaigns 1–2 and counterfactual checks. | Empirical efficacy calibration and broader relation structure; assignment mediation needs a separate controlled intervention. Avoid another wide factorial without a specific gap. |
| **Q4 — Adaptation to changing demand** | When does responding to a known/current or inferred demand change preserve performance? Vary demand persistence/change and information regime. | Frozen paired trajectories; explicit before/after regime windows; stationary/equivalence controls; distinct demand vs observation streams. | C5 IID/nonstationary/Markov generation, frozen exogenous path, dynamic and integrated runners. | Integrated latent-demand beliefs/adaptation are absent; current `IntegratedDecisionView` receives current requirements but no inferred regime state. |
| **Q5 — Coordination and resource allocation** | How do shared limits and joint assignments shape task completion and capability growth? Vary resource budget/action feasibility and coordination rule. | Same total available resources, actual use and stranded capacity separately reported; preserve production-only control; compare action-level feasibility and outcome vectors. | Central joint action selection, budget/per-agent caps, production+teaching accounting, discrete catalog. | No concurrent tasks, decentralized coordination, divisible-resource control or calibrated cost scale. Add only the subset demanded by the question. |

## 6. Common research protocol

Every future study should preregister and archive:

1. **Question and estimand:** a falsifiable statement, primary outcome and
   exact contrast; state which conclusions are simulation-conditional.
2. **Factorization:** architecture, policy, mechanism, scenario and evaluation
   values; identify all hard-coded defaults and interactions intentionally
   allowed to vary.
3. **Controls:** matched initial real/estimated states, agent identities,
   information, budgets/caps, policy input, and any mechanism toggles;
   include negative/equivalence controls that can falsify the instrument.
4. **Environment:** generate and freeze exogenous demand before policy runs.
   Use common random numbers for paired arms where meaningful, while keeping
   demand, realized-production, observation and learning innovations in
   separate indexed streams. A shared seed does not guarantee shared random
   realizations if stream consumption differs.
5. **Resources and outcomes:** record available, consumed, displaced and
   unused resources; report gross CES, functional success, costs, competence
   development and adaptation separately. Do not create a net utility without
   an externally justified common unit or explicit constraint.
6. **Replication and uncertainty:** define the independent unit from the
   exogenous process (typically a demand trajectory); pair within it and
   cluster uncertainty at that unit. Do not count deterministic reruns,
   episodes within one path, or observation-noise draws as independent demand
   scenarios. Report effect sizes and uncertainty; allow null and negative
   effects.
7. **Preflight and traceability:** verify action frontiers, decision margins,
   resource accounting, information leakage, reproducibility, and expected
   negative-control behavior before campaign-scale runs. Store config, code
   revision, manifests, seeds and artifact hashes in campaign-specific paths.
8. **Interpretation:** distinguish mechanism state transitions from policy
   choice and mediator correlations. Do not infer real-world external validity
   from internal behavioral plausibility.

Do not tune requirements or choose seeds after inspecting which policy wins.
If a preflight is insensitive, report a structural null or redesign only with
new approval/registration—never silently replace the primary contrast.

## 7. Minimal development roadmap

| Priority / step | Scientific capability | Current limitation and minimum implementation | Acceptance test | Reproducibility risk |
|---|---|---|---|---|
| **0 — Validation debt** | Trustworthy regression claims across research components. | Disposition the 13 documented historical integrity/provenance failures without rewriting frozen hashes; define which legacy checks are baseline failures. | Re-run and classify each known failure; unchanged frozen source/artifact hashes; clean focused tests. | High if “fix” updates expected hashes or rewrites scientific artifacts. |
| **1 — General state/action geometry** | Architecture comparisons beyond one team size/skill count. | Parameterize competence vectors, agent roster, effort vectors and learning profiles; retain exact 3×2 adapter/catalog behavior. Avoid generic scheduling. | For 3×2, exact action IDs, outputs, decisions, transitions and traces match fixtures; additional small n/k cases validate bounds and budgets. | High: action ordering/ties and serialized identifiers can alter historical paths. |
| **2 — Narrow component seams** | Matched policy and mechanism comparisons. | Keep the existing policy protocol; separate pure mechanism transition/observation calls from the sequence orchestrator behind small typed contracts. Do not add new algorithms. | Existing P0/P1/P2 plus MIS/teaching tests unchanged; mechanism toggles affect only declared state; policies receive only public view; resource ledger balances. | Medium-high: transition ordering or random-stream consumption can change outcomes. |
| **3 — Shared experiment/evaluation contract** | Reuse paired controls and outcome vectors across questions. | Standardize immutable scenario/config, frozen exogenous path, per-episode trace and metric aggregation; preserve gross CES/success/resources as separate fields. | Byte-stable rerun; paired arms share environment hash; metric calculations reconcile to episode records; no historical artifact overwrite. | Medium: schema migration and hash/provenance conventions. |
| **4 — Question-driven scenario extensions** | Concurrent assignment (Q5) or uncertain-regime adaptation (Q4). | Add either a pending-task queue/parallel action or a public demand-belief view only when an approved question requires it; never both as generic infrastructure by default. | Small exact fixtures demonstrate queue/latent-state transitions and no environment leakage; existing single-task behavior is invariant. | High: new state, queues, deadline semantics and random paths. |
| **5 — External calibration, as needed** | Interpret parameters in an application domain. | Obtain defensible empirical support for task requirements, learning rates, teaching efficacy and resource units. | Document provenance/uncertainty and sensitivity ranges; no parameter selected by policy ranking. | High scientific validity risk if calibration is omitted or outcome-tuned. |

**Recommended first implementation after separate authorization:** Step 1,
the narrowly bounded n-agent/k-skill state/action generalization with an
exact 3×2 compatibility gate. It addresses the principal structural ceiling
on cross-architecture research without presuming a new policy or teaching
mechanism. First resolve Step 0 as a validation gate in parallel; do not
change code or run a campaign under this document.

## 8. Explicit laboratory boundaries

The current laboratory is a small, deterministic-production, discrete-action
instrument for conditional mechanism and policy comparisons. It does not yet
represent concurrent project portfolios, negotiated/distributed coordination,
general organization networks, unknown-demand inference, empirical teaching
efficacy, noisy realized output, forgetting, or a calibrated welfare function.
Its additive production supports functional coverage across skills, not
superadditive team synergy. Gross CES, success and resource use are distinct
outcomes. Campaign 1/2, validity and Q1 documents must be read as bounded
evidence under their configurations; they do not validate the lab against
real organizations.

This framework does not resolve novelty. It defines a modular research
instrument and the tests needed to make future comparisons interpretable.
No implementation or campaign is authorized by this document.

## 9. Internal evidence and authority

- [Current project state](HLS_CURRENT_STATE.md)
- [HLS Laboratory v1 technical contract](experiments/HLS_LAB_V1.md)
- [Campaign 1 consolidated findings](experiments/HLS_CAMPAIGN1_FINDINGS.md)
- [Campaign 2 findings](experiments/HLS_CAMPAIGN2_FINDINGS.md)
- [Experimental sensitivity audit](experiments/HLS_EXPERIMENTAL_SENSITIVITY_AUDIT.md)
- [Laboratory validity assessment](experiments/HLS_LABORATORY_VALIDITY_ASSESSMENT.md)
- [First campaign design](experiments/HLS_FIRST_SCIENTIFIC_CAMPAIGN_DESIGN.md)
- [Q1 preflight](experiments/HLS_Q1_PREFLIGHT.md)
- [Q1-R analytical verification](theory/HLS_Q1R_ANALYTICAL_VERIFICATION.md)

Executable anchors: `src/hls/hls_lab_v1.py`,
`src/hls/hls_lab_v1_integrated.py`, `src/hls/hls_lab_dynamic.py`,
`src/hls/hls_lab_v1_environment.py`, `src/hls/discover_v0.py`,
`src/hls/discover_develop_v2.py`, and `src/hls/synthetic/c5.py`.
