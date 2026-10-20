# HLS Executable Published-Method Selection

**Date:** 2026-10-19
**Decision:** **REVISE — no two-method pair currently satisfies scientific fit and faithful execution within the requested bounded effort.**
**Scope:** incremental selection using existing HLS literature and implementation audits; no code or experiments changed or run.

## Executive decision

The prior selection of MixLLM and System-1.x remains scientifically interesting, but the preflight found unresolved data/checkpoint and hardware barriers. Replacing them with a superficially compatible pair would be worse: reviewed candidates divide into (i) adaptive assignment methods with robotics/workforce state and action semantics absent from HLS, and (ii) executable nonstationary bandit/learning methods that do not allocate heterogeneous HLS agents or model their capability development.

No two published algorithms are selected for faithful composition now. This follows the explicit “do not force an artificial composition” criterion. The most executable **single-method** validation is Cavenaghi et al.’s f-dsw nonstationary bandit on its own published synthetic scenario. It can be run without large models and has author code, but it is not an HLS heterogeneous-agent allocator. The closest assignment method is Emam et al.; its mathematical allocation/controller depends on robot state dynamics and safety constraints that a faithful implementation cannot fit into the existing N×K categorical allocator within a one-week bounded change.

This is not rejection of either mechanism or of HLS interaction research. It means revise the milestone to either (a) one source-faithful method first, followed by a separate integration decision, or (b) authorize a new robot/task environment for Emam. This report authorizes neither implementation.

## 1. Recovered candidates and prior decisions

This selection relies on, and does not repeat, the prior work:

- [Literature reproduction selection](HLS_LITERATURE_REPRODUCTION_SELECTION_2026-10-19.md) considered Nembhard, Borgonjon–Maenhout, Baccara–Lee–Yariv, MixLLM, System-1.x and Iterative Machine Teaching; it separated source models from HLS adaptations.
- [Targeted adaptive-advantage search](HLS_TARGETED_ADAPTIVE_ADVANTAGE_LITERATURE_SEARCH_2026-10-19.md) compared Cavenaghi et al., Mettler et al. and Cheung et al. It found positive source-specific results but no direct precedent for adaptive organizational allocation against a globally optimized fixed HLS organization.
- [Adaptive training comparison](../literature/ADAPTIVE_TRAINING_COMPARATIVE_ANALYSIS.md) records workforce learning, teaching, transfer and resource-cost antecedents, with access limitations.
- [Adaptive-training reuse audit](HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md) establishes that HLS has production, MIS-v2, demand, estimation and trace components, but no joint work/teaching action, shared work/training capacity or teaching-efficacy observation model.
- [Published-method preflight](HLS_PUBLISHED_METHODS_REPRODUCTION_PREFLIGHT_2026-10-19.md) found MixLLM’s source-specific artifacts unresolved and System-1.x without verified checkpoints, with CUDA hard-coded in evaluation.

Effort below is a relative engineering estimate, not measured development time. “Faithful method implementation” is distinct from reproducing a paper’s complete experimental results.

| Candidate | Published formulation / method | Code and data | HLS fit and minimum changes | Assessment |
|---|---|---|---|---|
| **Emam et al. (2020), adaptive multi-robot allocation** | Robot dynamics xdot_i=f(x_i)+g(x_i)u_i; agent/task costs V_ij(x_i), specialization state s_ij, and allocation/control with task priorities, slack and control-barrier constraints (Eqs. 1–8). Specialization uses expected-versus-realized progress: s_ij[k+1]=s_ij[k]+β₁α_ij[k]ΔV_ij[k], with a separate recovery term. | Full primary arXiv paper and Robotarium/simulation scenarios were inspected in the existing novelty audit. No official runnable implementation was verified there; no fixed external dataset is required for the mathematical simulation, but robot dynamics, task-cost functions and controller parameters must be instantiated. | Strongest fit for adaptive organization, but not a drop-in N×K policy: the action is continuous robot control/allocation subject to barrier constraints; HLS actions allocate divisible effort by competence or discrete G0 actions, without robot pose/control dynamics. A faithful reproduction needs an isolated robotics environment, QP/control-barrier solver, progress model and source scenario—not merely a policy adapter. **High effort; unlikely to fit one week with tests and validation.** | Retain as the best scientific allocation candidate. Do not map its suitability estimate directly to competence or call an N×K allocation a reproduction. |
| **Cavenaghi et al. (2021), f-dsw Thompson Sampling** | Four-arm Bernoulli bandit with time-varying means. Per arm, discounted historical evidence and a recent sliding-window posterior are combined by min/max/mean to select an arm; feedback is from the selected arm only (Algorithm 1; custom-decreasing Fig. 9). | Author [code](https://github.com/CavenaghiEmanuele/Multi-armed-bandit) and synthetic environment described in the paper; no external dataset needed for Fig. 9. Code commit and hyperparameters still need freezing. Published custom setting: 4 arms, horizon 1,000, 100 replications; paper reports qualitative figure comparisons, not inferential intervals. | Easy to reproduce separately; does not encode agent/task feasibility, multi-agent allocations, capability learning, or HLS effort constraints. Treating assignments as Bernoulli arms or replacing an HLS allocator with f-dsw changes the original action/reward model and is an adaptation. **Low-to-medium standalone effort; high conceptual cost for faithful integration.** | Best executable individual method; not selected as a partner for artificial HLS composition. |
| **Nembhard–Bentefouet productivity / Nembhard Direct** | Published direct/indirect experience production model; HLS Nembhard Direct adapts the direct curve P_ik(D)=k_ik(D+p_ik)/(D+p_ik+r_ik). Assignment affects experience/productivity. | HLS implementation, Nembhard Direct, ORACLE and ADAPTIVE routes, tests and traces already exist. The source audit cautions that Nembhard Direct is not a full reproduction of the paper’s group-transfer/three-stage experiments. | Excellent fit as an endogenous capability mechanism and already executable; not itself the published adaptive allocation algorithm. HLS ORACLE/ADAPTIVE are project policies, not Nembhard-published decision rules. Pairing it with Emam needs a new meaning for robot progress and is an HLS cross-model adaptation, not a faithful combined paper reproduction. **Low incremental effort for curve reuse; medium/high for controlled integration.** | Retain as HLS environment mechanism, not as a second externally published adaptive policy. |
| **Chen et al. (2018), ADP technician scheduling** | Multi-period stochastic technician scheduling with task-specific experience/service times; ADPBF versus one-day lookahead ADPOL. | Full paper local; no verified code/instance archive in prior audit. | Requires a separate indivisible-task/service-time/capacity environment and ADP implementation. Not compatible with current N×K action/reward semantics. **High effort.** | Defer; prior compatibility and investment audits remain applicable. |
| **Borgonjon–Maenhout (2024)** | Integrated workforce staffing, task scheduling, training, learning and forgetting, solved with branch-and-price/heuristics. | Full paper available; instances “available on request”; no verified code. | Requires scheduling windows, staffing/hiring, training, forgetting and source instance generation. **High effort.** | Defer; not a bounded extension. |
| **MixLLM (2025)** | Contextual query-to-LLM selection with query tags, per-model quality/cost prediction, latency penalty and selected-outcome updates. | Official router code and paper-specific extended data not verified; RouterBench is not the MixLLM code/data bundle. | Existing contextual router is not MixLLM; source-faithful work requires its predictor/feedback/latency path. **High effort and artifact-gated.** | Retain; defer until artifacts are resolved. |
| **System-1.x (2025)** | Learned subgoal decomposition and fast/slow planning control. | Author code and task data exist; trained checkpoints were not verified, Mistral 7B training is required, and evaluator hard-codes CUDA. | Maze/planning environment and plan metrics are absent from current HLS N×K. **Medium/high effort**; local Apple training path unvalidated. | Retain; defer until checkpoint/device issues are resolved. |
| **Liu et al. (2017), Iterative Machine Teaching** | Teacher selects supervised examples for an iterative learner using learner state/feedback. | Primary paper available; source data/code were not verified in prior review. | Teaching examples for SGD are not the same action as HLS agent/skill allocation or directed competence transfer. Requires a learner/task/example-pool environment. **High semantic integration effort.** | Do not compose with an allocator as if decision units matched. |

## 2. Why there is no acceptable pair yet

The requested pair must support faithful individual tests and an interpretable interaction experiment on a shared task stream with common resource constraints. The candidate similarities are not yet a shared mathematical contract:

1. **Emam + Cavenaghi:** Emam chooses continuous robot controls/allocations and updates specialization from progress mismatch; f-dsw selects one bandit arm from Bernoulli reward feedback under drifting means. Mapping a robot/task assignment to a Bernoulli arm and using f-dsw to replace or wrap Emam changes original action, feedback or update semantics. That could be a declared HLS adaptation, but not faithful composition of the published algorithms.
2. **Emam + Nembhard Direct:** Emam’s s_ij is estimated suitability from control progress; Nembhard productivity is true experience-dependent output. Substituting one for the other would redefine both. A future HLS adaptation could preserve separate states, but the robot/task progress observation model and cross-model reward mapping are not specified.
3. **Cavenaghi + Nembhard Direct:** HLS production is continuous and agent-skill-task dependent; f-dsw’s source algorithm is a Bernoulli arm posterior/window method. Bernoulliizing production or treating each cell as an arm changes the environment, and would need explicit scientific approval.
4. **MixLLM + System-1.x:** original task domains and decision levels differ; MixLLM artifacts and System-1.x checkpoints/device path remain unresolved. The previous preflight already classifies maze routing as an HLS adaptation.

There is therefore no defensible claim that two selected published methods can be integrated faithfully within a week using current HLS interfaces. Choosing a pair anyway would violate the compatibility constraint.

## 3. Smallest experiment and what can be learned

### Executable published-method result available now: Cavenaghi Fig. 9 only

This is the smallest near-term method validation, but it is explicitly **not** the requested two-mechanism HLS experiment.

- **Environment:** source’s four Bernoulli arms; means start at (0.9, 0.7, 0.1, 0.3), arm 1 drops at round 250 and arm 2 at round 500; horizon 1,000.
- **Policies:** author implementation’s min-dsw, max-dsw and mean-dsw; standard TS, discounted TS and sliding-window TS controls as specified by the source.
- **Repetitions/uncertainty:** reproduce 100 runs and source randomization; report paired seed differences and uncertainty intervals as additional HLS analysis, while distinguishing them from the paper’s published figure. Do not tune on test paths.
- **Resources:** same arm count/horizon; no model inference; log algorithm runtime separately. No invented compute budget is needed for this four-arm benchmark.
- **Interesting outcomes:** recovering the source’s decreasing-drift ranking, showing a negative stationary/no-drift control, or finding that a comparator wins on a different segment are all informative. None is evidence about HLS organization or Nembhard learning.
- **Reproduction criterion:** freeze author-code commit and parameterization; match the reward-mean schedule; run source-defined policies and seeds; save trajectories and aggregate reward/regret. The paper supplies no tabulated Fig. 9 estimate or inferential interval, so no exact-number match can be claimed.

### HLS mechanism integration: not specified as an approved experiment

The existing Nembhard runner can exercise static allocations, ORACLE and ADAPTIVE against Nembhard productivity and dynamic demand. Its evidence is preserved in E1 and the Nembhard reports. Adding Emam or f-dsw to that runner requires an explicit cross-model adapter and source-preserving test plan. This report does **not** invent an interaction hypothesis or hypothetical metrics for a fabricated composition.

If a later HLS adaptation is authorized, minimum common design requirements are:

- two agents and two task/skill types, with fixed initial heterogeneity and a short preregistered horizon;
- one stationary and one regime-changing task sequence, paired across policies;
- the same per-period resource feasibility and outcome accounting;
- static optimized allocation, each published mechanism individually, and a combined policy only if its composition is formally defined;
- method-native outcomes and a common measure only where units permit; report production/quality, resource use and latency separately;
- paired scenario-level differences with uncertainty intervals, plus trace checks for information sets, selected-only feedback and transition timing;
- include stationary/no-learning negative controls and at least one scenario where the allocation preference can actually change.

Useful outcomes may be null or negative: no policy effect, benefit only under regime change, antagonistic interaction, or static specialization remaining sufficient. The combined mechanism need not win.

## 4. Implementation readiness and effort

| Candidate action | Equations / pseudocode source | Required work and tests | Relative effort / first measurable result |
|---|---|---|---|
| Cavenaghi f-dsw standalone reproduction | Paper Algorithm 1, custom-decreasing means in Fig. 2a, evaluation in Fig. 9; author repository. Pseudocode: maintain per-arm discounted and recent-window posterior; sample/score arms; combine scores by min/max/mean; select one arm, observe only its reward, update that arm’s state. | Pin repository commit/environment; run author scenario; test stationary and two-change schedules, selected-arm-only updates, seed replay, policy outputs, aggregate metrics. No HLS simulator changes. | **Low–Medium**, plausibly within one engineering week. First measurable result: saved source Fig. 9 trajectories and seeded aggregate summary. Does not satisfy the integrated HLS pair objective. |
| Emam allocator faithful standalone port | Paper Eqs. 1–8, task-priority/control objective Eq. 6, specialization updates Eqs. 7–8 and source simulation figures. | Recreate agent dynamics, task costs/progress, QP/control-barrier constraints and task allocation; test feasibility, update timing/sign, known/unknown suitability, environment-change traces and deterministic replay. Requires a solver choice and source-matched scenario. | **High**; a one-week estimate is not defensible before checking the control/QP implementation and source parameter availability. First result: source-scenario trace with feasible controls and specialization updates. Not a current N×K extension. |
| Nembhard Direct mechanism validation | Published direct productivity curve; HLS implementation in src/hls/hls_lab_nk_nembhard.py and existing Nembhard tests/protocols. | Reuse existing code; curve and assignment/exposure semantics are already covered by Nembhard tests. A new Emam combination needs separately specified state and reward bridge. | **Low** for standalone checks; **High/undefined** for faithful coupling to Emam. This is a model mechanism, not a new published allocator. |
| MixLLM / System-1.x | MixLLM Eqs. 1–22 / System-1.x official source scripts and paper protocol. | Resolve MixLLM artifacts; train/retrieve System-1.x checkpoints and solve CUDA/MPS portability. Earlier preflight remains current. | **High / artifact-gated**; do not start expensive work now. |

No simulator refactor is justified. If Emam is selected later, implement it in an isolated robotics benchmark package. If Cavenaghi is selected, keep it as an external method-validation module first; do not translate its arms into HLS workers without a separately approved adaptation.

## 5. Recommendation

**REVISE.** Do not select a pair or start a combined experiment yet. No candidate pair both preserves its published decision semantics and fits the existing laboratory plus the approximately one-week bound. The immediate decision is between:

1. Authorize Cavenaghi Fig. 9 as a single executable published-method reproduction (the fastest evidence-producing step, but outside HLS organization semantics); or
2. Authorize Emam as a separate robotics-environment implementation (stronger adaptive-allocation fit, but higher effort and isolated from N×K).

After one individual method is implemented and measured, select a second mechanism only with an explicit shared state/action/outcome mapping. Nembhard Direct can be part of a later HLS adaptation but should not be called the second published adaptive policy. MixLLM and System-1.x remain scientifically retained but deferred for artifact/hardware barriers. No mechanism is rejected for lacking novelty, and no adaptive or combined method is presumed to outperform a strong fixed policy.

## References and HLS evidence

- Emam, Y. et al. (2020). “Adaptive Task Allocation for Heterogeneous Multi-Robot Teams with Evolving and Unknown Robot Capabilities.” ICRA 2020. [DOI](https://doi.org/10.1109/ICRA40945.2020.9197283); full-source/equation summary in [HLS Scientific Novelty Audit](../research/HLS_SCIENTIFIC_NOVELTY_AUDIT_2026-10-19.md), §4.2.
- Cavenaghi, E., Sottocornola, G., Stella, F., & Zanker, M. (2021). “Non Stationary Multi-Armed Bandit: Empirical Evaluation of a New Concept Drift-Aware Algorithm.” *Entropy* 23(3):380. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8004723/); [author code](https://github.com/CavenaghiEmanuele/Multi-armed-bandit).
- Nembhard, D. A., & Bentefouet, A. (2015). “Selection, Grouping, and Assignment Policies with Learning-by-doing and Knowledge Transfer.” *Computers & Industrial Engineering* 79, 175–187. [DOI](https://doi.org/10.1016/j.cie.2014.11.006). HLS scope and source-fidelity boundary: [mathematical extraction](../literature/audits/Nembhard_Bentefouet_2015_Mathematical_Extraction.md) and src/hls/hls_lab_nk_nembhard.py.
- MixLLM/System-1.x decision: [published-method preflight](HLS_PUBLISHED_METHODS_REPRODUCTION_PREFLIGHT_2026-10-19.md).
- HLS environment and assignment support: [capability assessment](../research/HLS_LABORATORY_CAPABILITY_ASSESSMENT_2026-10-19.md); teaching/resource limitation: [adaptive-training reuse audit](HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md).
