# HLS laboratory functional-completeness audit and integration plan

**Audit date:** 2026-10-15  
**Repository:** `franjgs/heterogeneous_learning_systems`  
**Branch / HEAD:** `feature/hls-laboratory-v1` / `f421270351b2dd4ae43f0d134d379c7d97c9000a`  
**Mode:** source/document audit only. No functional code, results, or historical artifacts changed; no simulations or campaigns run.

## Executive finding

The repository contains a useful, executable production-and-individual-development core, plus demand, information, and policy experiments. It does **not** yet execute the full HLS cycle in the Chief Engineer's definition. The cycle stops at the point where teaching should compete with productive work: there is no teaching/supervision action, no instructor–learner–skill efficacy state, no training outcome observation, and no common constraint charging teaching against production resources. Consequently, the current lab can study “who produces what while individual capability changes,” but cannot study “who learns what, how, and from whom” as an integrated decision.

The minimum next implementation is not a replacement simulator. It is one additive integration layer using existing team, production, MIS-v2, demand, observation, and trace components. That layer needs (1) a joint production/training action under a shared per-period resource constraint; (2) a bounded teaching-induced competence transition with relation-specific efficacy; (3) an observable training outcome and simple efficacy estimate; and (4) a runner that closes the loop through multiple problems. Until those pieces pass the end-to-end tests below, the laboratory is functionally incomplete for the stated HLS questions.

This audit complements [the adaptive-training reuse audit](HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md), [the minimal specification](../experimental_foundations/ADAPTIVE_ASSIGNMENT_LEARNING_TEACHING_SPECIFICATION.md), [the reference register](../literature/ADAPTIVE_TRAINING_REFERENCE_REGISTER.md), and [the campaign proposal](HLS_ADAPTIVE_TRAINING_MINIMAL_PROPOSAL.md). It is a completeness/integration assessment, not another novelty review.

## Status vocabulary

- **IMPLEMENTED AND FUNCTIONAL:** executable path and observable behavior exist.
- **IMPLEMENTED PARTIALLY:** only a bounded version or separate component exists; an end-to-end contract is missing.
- **CONCEPTUAL ONLY:** described in scientific documents but not represented by an executable mechanism.
- **ABSENT:** no mechanism was found in the audited implementation.
- **NOT VERIFIED:** source evidence did not permit a reliable conclusion.

Priority **A** is needed to close the first integrated HLS cycle; **B** is important but can follow; **C** is application/question-specific. “A” does not mean a complex or optimal model is required.

## Functional completeness matrix

External evidence below establishes that the phenomenon is relevant in operational settings; it does not validate a particular HLS equation. HLS evidence points to executable source unless a document is explicitly named.

| Dimension; real phenomenon / application; external relevance | Repository state and evidence | If absent/incomplete | Minimum sufficient representation; dependencies | Priority |
|---|---|---|---|---|
| **1. Heterogeneous agents** — technicians and expert teams differ in skill profiles. [Jin et al. (2018)](https://doi.org/10.1080/00207543.2018.1424366) model workforce grouping with individual transfer characteristics. | **IMPLEMENTED AND FUNCTIONAL.** `discover_v0.py::State`, `validate_state`; `hls_lab_v1.py::ExpertState`, `TeamState`; dynamic initial matrices. | Cannot test specialization or expertise placement. | Preserve per-agent capability rows and identities. Already available. | **A — present** |
| **2. Multidimensional competencies** — work requires distinct skills; technician scheduling uses task-specific experience. [Chen et al. (2017)](https://doi.org/10.1016/j.cor.2016.12.026). | **IMPLEMENTED AND FUNCTIONAL** for two skills: `discover_v0.py::State`, `production_inputs`; HLS team fixed at 3×2. | A one-skill model would erase skill mix and complementary assignment. | Reuse the two-dimensional cells; changing dimension count is not needed for first integration. | **A — present, bounded** |
| **3. Different problem requirements** — service/task classes make distinct skill demands. [Chen et al. (2017)](https://doi.org/10.1016/j.cor.2016.12.026). | **IMPLEMENTED AND FUNCTIONAL** for visible functional requirements: `hls_lab_v1.py::ProblemSpec`, `evaluate_problem`; `hls_lab_dynamic.py::DemandRegime`, `generate_problems`. Hidden CES type is separate in `UncertainProblem`. | Without multiple requirement vectors, future skill changes may not affect later output. | Reuse existing requirement vectors and problem IDs. | **A — present** |
| **4. Assign participants to work** — daily tasks must be assigned to workers. [Chen et al. (2017)](https://doi.org/10.1016/j.cor.2016.12.026). | **IMPLEMENTED AND FUNCTIONAL** in the existing action catalogue and policies: `discover_v0.py::JOINT_ACTIONS`; `FixedRouting`, `GreedyAdaptive`, `ExploreThenGreedy`; `run_dynamic_sequence`, `run_belief_sequence`. | No organizational allocation question. | Keep the current production allocation as one part of a larger joint action. | **A — present** |
| **5. Production and quality** — output must be measurable against operational objectives. Workforce models report service/productivity outcomes; HLS also has functional thresholds. [Chen et al. (2017)](https://doi.org/10.1016/j.cor.2016.12.026). | **IMPLEMENTED AND FUNCTIONAL, with distinct metrics.** `production_inputs` gives additive outputs; `ces_reward` gives scalar CES; `evaluate_problem` reports success, deficit, margin. | CES reward alone cannot establish whether explicit requirements were met; binary success alone can saturate. | Preserve CES and functional outputs separately; report output, success, deficit, effort. | **A — present** |
| **6. Learning by experience** — doing work changes later productivity. [Chen et al. (2017)](https://doi.org/10.1016/j.cor.2016.12.026) explicitly models experience-based service times. | **IMPLEMENTED AND FUNCTIONAL.** `discover_develop_v2.py::capability_after_exposure`, `mis_v2_transition`; dynamic `advance_team`. | Future capabilities would not depend on assigned work. | Reuse MIS-v2 unchanged for the individual-learning channel. | **A — present** |
| **7. Learning from another participant** — peer observation, coaching, or instruction can transfer knowledge. [Jin et al. (2018)](https://doi.org/10.1080/00207543.2018.1424366) model learning from observing/interacting with colleagues; [Govaerts & Dochy (2014)](https://doi.org/10.1016/j.edurev.2014.05.002) review supervisor behaviours related to training transfer. | **ABSENT.** No executable teacher/learner action or social competence transition in `hls_lab_dynamic.py` or the audited DISCOVER paths. | The second HLS question—who should learn from whom—cannot be posed. | Add one explicit instruction/coaching event that changes a learner's target skill, separate from MIS-v2. | **A — absent** |
| **8. Choose instructor and learner** — training assignment must identify who gives and receives instruction. Training/supervisor behavior is operationally distinct from merely placing workers together. [Govaerts & Dochy (2014)](https://doi.org/10.1016/j.edurev.2014.05.002). | **ABSENT.** No ordered pair or recipient skill appears in the action/state contract. | Cannot compare alternative teaching relationships. | Add a no-teaching option plus a single directed tuple `(instructor, learner, skill, effort)` initially; define whether simultaneous teaching is excluded. Depends on resource model. | **A — absent** |
| **9. Heterogeneous teaching efficacy** — transfer may depend on teacher behavior, trainee characteristics, and context; the precise HLS relation is a hypothesis, not an established scalar. Review evidence reports many distinct supervisor support behaviors and inconsistent operational definitions. [Govaerts & Dochy (2014)](https://doi.org/10.1016/j.edurev.2014.05.002). | **ABSENT.** `LearningProfile.eta` is individual MIS-v2 rate by expert/skill, not efficacy of an instructor–learner relationship. | A universal teaching effect would make teacher selection vacuous; an arbitrary relation parameter could manufacture value. | Minimal bounded efficacy parameter `θ[i,j,k]` with declared prior and a simple monotone, bounded transfer law; retain as replaceable module. Must be separately justified and tested. | **A — absent for the teaching question** |
| **10. Shared time/resource use** — service and training compete for scarce staff capacity. Integrated staffing/training models explicitly include training costs/capacity. [Borgonjon & Maenhout (2024)](https://doi.org/10.1016/j.cie.2023.109784); [Su et al. (2025)](https://doi.org/10.1016/j.ijpe.2025.109642). | **IMPLEMENTED PARTIALLY.** `ProblemSpec.resource_budget`, `feasible_actions`, per-expert effort caps; cost recorded as `effort × resource_cost_per_unit`. In current dynamic execution the cost parameter is an observer, not a combined work+training budget or priced decision. | Teaching could be free or violate capacity, invalidating the opportunity-cost question. | One shared per-period budget/capacity constraint over productive effort and teaching effort; report used and unused budget. | **A — partial** |
| **11. Opportunity cost of teaching** — instruction displaces current productive capacity. [Borgonjon & Maenhout (2024)](https://doi.org/10.1016/j.cie.2023.109784) integrate training with staffing; [Su et al. (2025)](https://doi.org/10.1016/j.ijpe.2025.109642) account for training fees/capacity. | **ABSENT as a trade-off.** Cost fields do not create a teaching action or reduce production resources. | Cannot ask whether lost current output is repaid by future capability. | Teaching effort must consume the same constrained time/resource as production. Do not combine unlike units into arbitrary net utility. | **A — absent** |
| **12. Observe outcomes** — organizations receive imperfect measures of production/training. | **IMPLEMENTED PARTIALLY.** `run_belief_sequence` adds noisy aggregate CES observations and separate indexed individual production observations. No teaching outcome channel exists. | Cannot update teaching efficacy or test noisy identification. | Add a training outcome signal tied to the chosen teaching event; use indexed exogenous noise so policies share external draws. | **A — partial** |
| **13. Uncertain competencies** — managers may not know workers' actual skill. | **IMPLEMENTED AND FUNCTIONAL, bounded.** `CompetenceInformationMode` ORACLE/PARTIAL_STATIC/PARTIAL_LEARNING; `SkillPosterior`, `update_skill_posterior`, MIS prediction. | Partial-information allocation cannot be studied. | Reuse existing separation of private real state and estimate; do not expose real state to policy. | **A — present** |
| **14. Uncertain teaching efficacy** — a manager may need to learn which relationship works. | **ABSENT.** No `θ` state, prior, likelihood, or efficacy update. | The proposed candidate question has no experimental treatment variable. | Maintain private true efficacy in world state; expose only prior/posterior and public outcome history. Begins with simple estimator, not necessarily advanced Bayes. | **A — absent** |
| **15. Changing demand** — future task mix is not always stationary. Technician scheduling studies stochastic arrivals and future demand. [Chen et al. (2017)](https://doi.org/10.1016/j.cor.2016.12.026); [Valeva et al. (2017)](https://doi.org/10.1016/j.ijpe.2016.10.026). | **IMPLEMENTED PARTIALLY.** `DemandRegime` plus scheduled regime sequence and stochastic draw; `synthetic/c5.py` has stationary, nonstationary, Markov generators. Dynamic runner uses scheduled within-regime draws; not every C5 process is integrated into it. | Cannot evaluate whether learned skills/effectiveness are useful after demand changes. | Reuse scheduled regimes first; add a thin adapter to an existing Markov generator only if the first question needs it. | **A — partial** |
| **16. Organizational decisions and persistent policy state** — organizations retain information and adapt allocations. | **IMPLEMENTED PARTIALLY.** `FixedRouting`, `GreedyAdaptive`, `ExploreThenGreedy`, `OrganizationState`; optional observe/update path. `DiscoverBeliefPolicy` plans over finite horizon. | Cannot compare non-adaptive/adaptive organizations or persistent evidence use. | Reuse policies as baselines; add training decisions to the policy interface. Do not treat current `ExploreThenGreedy` as isolated learning: prior characterization documents exploration/update bundling. | **A — partial** |
| **17. Intertemporal consequences** — today's assignments change future capability and value. [Baccara et al. (2023)](https://doi.org/10.1016/j.jet.2022.105587); [Chen et al. (2018)](https://doi.org/10.1016/j.ijpe.2017.10.028). | **IMPLEMENTED PARTIALLY.** Dynamic `H` decisions and persistent MIS-v2 skills; finite-horizon DISCOVER planner. Its documented recursion plans with fixed skill state; realized MIS-v2 development occurs after actions and is not forecast inside that recursion. | A planner can miss the very future value of development under study. | Keep environment horizon and state persistence; for integration smoke a simple predeclared policy suffices, then expose a replaceable planning interface. Do not claim optimality. | **A — partial** |
| **18. Collective performance measurement** — compare accumulated service/output and skill consequences. | **IMPLEMENTED AND FUNCTIONAL for current world.** `EpisodeRecord`, cumulative true reward, functional success/deficit, competence/exposure traces, costs. | Mechanisms cannot be compared or audited. | Extend records with instructor, learner, taught skill, training resource, efficacy estimate, observation, and phase labels. | **A — present, schema extension needed** |
| **19. Policy comparison** — paired policies should face common external conditions. | **IMPLEMENTED AND FUNCTIONAL for existing dynamic experiments.** Seeded generators, separate reward and coordinate-indexed individual noise, `compare_organizations` / `compare_belief_policies`; experiment scripts emit manifests. | Outcome differences may be confounded by different worlds/noise. | Preserve common exogenous streams while letting endogenous experiences/competences diverge by policy. Add training-noise stream with fixed coordinates. | **A — present, extend** |
| **20. Reproducibility and artifact integrity** — simulations need traceable random seeds/configuration/results. | **IMPLEMENTED PARTIALLY to FUNCTIONAL** across experiment runners: deterministic seeds, hashes/manifests in characterization/stress experiments. No single general run contract covers proposed joint training actions. | Cannot reproduce comparisons or distinguish execution errors. | Reuse runner/manifest patterns; dedicated output namespace and deterministic serialization. | **A — present, extend** |
| **21. Mechanism replaceability** — test alternate learning/teaching/demand models without rewriting the system. | **IMPLEMENTED PARTIALLY.** `Organization` protocol and dataclasses offer seams, but `run_belief_sequence` directly sequences production, Bayes, observations, and MIS-v2. | Mechanism swaps may require changing frozen paths or risk leakage. | Add a small additive training/action/result interface; do not refactor legacy runner. Keep transitions and observation models as injected components. | **B — partial** |

## External relevance: what is established and what remains a hypothesis

- **Verified external evidence:** technicians are assigned to task classes while experience changes later service productivity under stochastic customers ([Chen et al. 2017](https://doi.org/10.1016/j.cor.2016.12.026)); workforce grouping can generate learning through observing/interacting with coworkers ([Jin et al. 2018](https://doi.org/10.1080/00207543.2018.1424366)); dynamic task allocation and on-the-job training can jointly shape future expertise ([Baccara et al. 2023](https://doi.org/10.1016/j.jet.2022.105587)); staffing/training planning represents capacity and training cost ([Borgonjon & Maenhout 2024](https://doi.org/10.1016/j.cie.2023.109784); [Su et al. 2025](https://doi.org/10.1016/j.ijpe.2025.109642)). Govaerts & Dochy's review describes 24 supervisor support behaviors and notes variation in how the construct is defined ([2014 article](https://doi.org/10.1016/j.edurev.2014.05.002)).
- **Repository evidence:** the executable sources in the matrix establish individual skill, productive assignment, MIS-v2, partial competence estimates, finite-horizon belief planning, demand variation and traceable evaluation.
- **Inference:** these systems motivate a shared production/training resource constraint and observation of teaching outcomes. That is a modeling requirement for the stated question, not proof that a particular efficacy equation is realistic.
- **Unverified hypothesis:** a compact, decision-relevant instructor–learner–skill efficacy parameter can be identified online and can change optimal resource allocation enough to affect later collective performance. The cited evidence does not establish that exact claim.

## Closed-cycle test

| Cycle stage | Current execution support | Status / interruption |
|---|---|---|
| 1. Problem arrives | `generate_problems`, `generate_uncertain_problems`; `DemandRegime` | **Supported**, with scheduled regime and draw semantics |
| 2. Organization observes problem/resources | `_view`/`DecisionView`; demand requirement visible; real vs estimated skill separated in partial modes | **Supported**, but no efficacy belief/resource state exists |
| 3. Select who works | frozen `JOINT_ACTIONS` and organization policies | **Supported** |
| 4. Select who learns/teaches or decline | No such action in `Organization.choose` or dynamic runner | **Stops here** |
| 5. Enforce shared production/training resources | production effort feasibility exists; no training effort to charge | **Missing** |
| 6. Produce and evaluate output | `production_inputs`, `ces_reward`, `evaluate_problem` | **Supported** |
| 7. Update individual skill from experience | MIS-v2 `advance_team` | **Supported** |
| 8. Update learner skill by instruction | No teaching transition | **Missing** |
| 9. Observe production/training results | noisy CES and per-cell production observations; no training outcome | **Partial** |
| 10. Update relevant organization knowledge | environmental Bayesian belief and competence posterior exist; efficacy posterior absent | **Partial** |
| 11. Feed future capability into later allocations | persistent skills and repeated decisions | **Supported for work/MIS; missing for instruction** |
| 12. Measure cumulative collective outcome | current reward/success/deficit/cost traces | **Supported; extend training trace schema** |

The cycle does **not** run end-to-end: it is interrupted before instruction is an action, and again at the missing instruction-induced state/observation updates. The main gap is not lack of a sophisticated optimizer; it is absence of the entities, action, shared constraint and transition/observation links needed to represent teaching.

## Minimal integrated model proposal

Keep three agents and two skills for compatibility with DISCOVER's production state. Add to the dynamic-world state a directed relation table `theta[i,j,k]` (instructor `i`, learner `j`, skill `k`) held private by the environment; expose only an estimate and the public observation history. The team continues to use existing real/estimated competencies, experience, demand regime and budget.

Extend the period action to a pair `(productive_allocation x, teaching_action q)`, where `q` is either no teaching or one directed instructor/learner/skill with effort `u`. The same declared period capacity constrains production effort plus teaching effort; per-agent capacity prevents one participant from teaching and working beyond available time. The first implementation can permit at most one teaching event per period, avoiding scheduling complexity while preserving the choice of whom to teach.

Reuse MIS-v2 for the work-exposure component. A replaceable, bounded teaching transition is still a scientific decision. A minimal candidate for engineering acceptance testing—not a validated human-learning law—is:

```text
post_work_skill = MIS_v2(pre_skill, learner_work_effort)
post_teaching_skill = min(1, post_work_skill + theta[instructor,learner,skill] * teaching_effort)
```

with `theta ∈ [0, θ_max]`, zero gain when teaching effort is zero, and identical units/limits across instructors. It makes transfer effect explicit and easy to replace; it must be approved and sensitivity-checked before any scientific execution. If the observation is a noisy post-session skill assessment, record the realized pre/post competence (privileged audit output) separately from the organization-visible noisy result. The organization estimator may use only exposure and observation—not the private competence or theta.

An alternative observation could be a directly scored trainee demonstration on the taught skill. Its mapping to competence and the likelihood need to be specified; do not treat CES aggregate reward as a dyad-level teaching observation. Keep environmental belief, skill estimates, efficacy estimates, and real simulator state in separate fields.

No policy needs to be optimal to close the integration loop. Initial policies can be `NO_TEACH` (production-only), a predeclared fixed teaching route, and a transparent rule that can choose either production or a teaching event using visible requirements, estimates, and remaining budget. The scientific P2/P3 comparison remains future work: identical planner/action set/compute, fixed efficacy estimates versus efficacy updating. An oracle is diagnostic only.

## End-to-end integration acceptance scenario

Use two heterogeneous experts (or the existing three-agent/two-skill state with the third held inactive) and two task types. One expert begins stronger in skill 1; a second is the designated learner with a lower skill-2 level. First demand is skill-1 oriented, then changes to a recurring skill-2-oriented task. The action set includes:

1. production-only allocation;
2. instructor–learner teaching in skill 2;
3. no teaching.

Set a shared per-period capacity so teaching displaces positive productive effort. Run a favorable relation with nonzero efficacy, a zero-efficacy negative control, and a case where the skill-2 task does not recur. Use the exact same sequence, initial state, budget and indexed noise for matched policy arms. Do not optimize parameters based on who wins.

Acceptance requires a single uninterrupted runner to produce a trace proving:

- teaching consumes budget and reduces currently available production;
- nonzero teaching changes the learner's future real skill through the declared transition, while zero effort/zero efficacy does not;
- MIS-v2 work exposure and teaching gains are separately recorded;
- the organization sees only noisy/public training outcomes and may update an efficacy estimate;
- a later skill-2 task uses the learner's changed capability in output;
- one policy chooses no teaching when its declared rule says so;
- production and teaching actions remain feasible under the common budget;
- demand change, estimates, beliefs, all action components, costs and cumulative output are serialized reproducibly;
- alternate policy choices can yield either higher or lower cumulative outcome depending on demand/efficacy, without asserting general superiority.

This verifies a working mechanism chain, not external realism, novelty, or a scientific effect.

## Minimum implementation plan, ordered by dependencies

Effort: **S** = small additive change; **M** = moderate integration; **L** = substantial. No work below is authorized by this audit itself.

| Stage | Objective / minimal change | Candidate files | Dependencies | Acceptance test | Regression risk | Effort |
|---|---|---|---|---|---|---|
| 0. Freeze extension contract | Define skill units, common time/resource budget, teach event semantics, efficacy truth/prior, and training observation before code. | New `docs/experiments/` protocol; link this audit and adaptive-training spec | PI/CE scientific approval; focused full-text follow-up | Contract states state/action/transition/likelihood/budget and no-leak rules; no edits to frozen contracts | Low | S |
| 1. Add composable state/action types | Represent directed efficacy truth/estimate separately; joint production+optional teaching action; common capacity validator. | New `src/hls/hls_lab_training.py` (preferred additive module); reuse `hls_lab_v1.py` value types | Stage 0 | Unit tests: directed tuple, no-teach, per-agent/global feasibility; legacy imports unchanged | Medium at integration boundary | M |
| 2. Add teaching transition and observation | Reuse MIS-v2 first, apply approved bounded teaching transition second; generate coordinate-indexed training noise; update efficacy estimate from public observation only. | New training module and tests; use `discover_develop_v2.py` unchanged | Stage 1; approved equation and identifiable observation design | Zero-effort/zero-effect controls; bounds; estimator cannot access private theta/competence; matched noise independent of call order | Medium | M |
| 3. Add integrated multi-period runner and traces | For each problem: observe, choose joint action, validate budget, generate production/training outcomes, update MIS/teaching, update beliefs/estimates, carry state forward, record all channels. | New runner module under `src/hls/`; new experiment smoke script; reuse `hls_lab_dynamic.py` generators/manifest pattern | Stages 1–2 | End-to-end scenario above; same seed reproduces exact trace; H=1/no-teach matches existing production and MIS outputs | Highest | M/L |
| 4. Add simple policy controls | Implement only no-teach, fixed teaching route, and transparent work-vs-teach rule; policy receives observable state only. | New policy classes in additive module; tests | Stage 3 | Feasibility/no-leak and action logging; no claim of optimizer optimality | Low–medium | S/M |
| 5. Regression and freeze readiness | Run legacy HLS Lab/CE-23/24/25 relevant tests and one smoke only; publish no broad result. | New tests, docs index | Stages 1–4 | Regression passes, artifacts separate, manifest includes code/input/config hashes | Medium | S |

Do not build first: neural/predictive models, advanced Bayesian machinery, multiple instruction modalities, negotiation, social networks, a universal optimizer, a new simulator, or a broad factorial. These do not close a missing link more directly than the stages above.

## Key risks and limits

1. **Identifiability:** noisy training outcomes can confound relation efficacy with learner baseline, individual MIS-v2 gains, and assessment noise. Record and separate exposures; show identifiability before campaign use.
2. **Invented teaching law:** a simple `theta × effort` transition is a testable engineering placeholder, not established psychology or a validated workplace learning curve. External supervisor-transfer evidence does not uniquely justify this formula.
3. **Resource comparability:** effort, CES output, and functional success are not automatically commensurate. Use a shared constraint and report outcomes separately before any scalar utility.
4. **Scope overlap:** assignment + experience + training + uncertain demand are established literatures. The unknown relation-efficacy learning component must be checked against full papers and targeted work on adaptive training/mentoring assignment.
5. **Policy confounding:** current `ExploreThenGreedy` bundles exploration and reward-based updates; it is not by itself a fair test of efficacy learning. Equal planning/compute is necessary for P2/P3.
6. **Legacy compatibility:** `run_belief_sequence` requires the full 64-action set and plans with fixed capabilities. It should not be silently modified to absorb teaching or tight-budget actions.

## Recommendation

**Operational recommendation: AUTHORIZE A LIMITED INTEGRATION IMPLEMENTATION, but do not authorize a scientific campaign.** The system's principal incompleteness is concrete and bounded: the shared-budget joint work/teaching action, teaching-induced skill transition, efficacy observation/update, and integrated runner. Reuse production, MIS-v2, partial-information, demand, and trace infrastructure; implement these as an additive layer and leave G1, G2, MIS, G3-H, RQ0, CE-23–25, and historical results frozen.

The first implementation should close and test the end-to-end cycle only. Scientific execution should wait for CE approval of the teaching transition and observation model, and a completed prior-art review. Do not claim that relation-specific adaptive teaching is novel or that the first smoke demonstrates its value.
