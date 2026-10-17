# HLS Experimental Sensitivity Audit

**Audit window began:** 2026-10-16 09:07 +02:00; **recorded:** 09:08 +02:00 (Europe/Madrid).
**Scope:** read-only analysis of the published Campaign 2 artifacts, source inspection and small deterministic decision/reward probes. No campaign or simulator physics was changed. The laboratory milestone remains **PARTIAL**.

## 1. Executive findings

**VERIFIED — exact cause of replicate-level CES degeneracy.** The ten seeds per Campaign 2 scenario change production-observation and (in teaching branches) formative-observation paths and competence-estimate paths. They do not change the exogenous demand path. In A and B, each scenario/condition has one productive-action path across seeds. In C, the two MIS-OFF conditions have seven paths, but differences occur after the regime change among assignments with identical skill-1 output: E0 and E1 both have skill-1 competence 0.20, while E2 supplies 0.80. Thus those swaps leave output and CES unchanged. Every scenario/condition has one true-competence path, one CES trajectory/total and one functional-success trajectory across its ten noisy seeds.

Noise is not production noise. It perturbs observations; the deterministic posterior update may then affect later estimated competencies and assignments. For the recorded .02 SD, estimate variation does not cross an outcome-relevant action boundary in A/B, and does not change the reward-equivalent decisions in C. Fixed one-hot demand, deterministic MIS-v2/teaching transitions and broad lexicographic score regions complete the explanation. This is not evidence that the simulator ignores noise in general.

Campaign 2 is discriminative across interventions: CES means differ across the four teaching × MIS conditions, and functional success falls from 24/24 to 23/24 in teaching branches due to the forced first-period production displacement. It is not discriminative across replicate seeds for these outcomes. Success is saturated in all no-teaching branches and near-saturated in teaching branches; it cannot reveal the later output gains. CES is gross production, not net resource value.

## 2. Verified dependency map

| Quantity / innovation | Source and entry point | Can alter decisions? | Can alter real production / CES? | Can alter future learning? |
| --- | --- | --- | --- | --- |
| Demand process randomness | C5 process sampled in `hls_lab_v1_environment.generate_environment_trajectory` (`src/hls/hls_lab_v1_environment.py:87–117`); each emitted problem is frozen before policy runs. | Only through the observed problem/requisites supplied to policy. | Yes, through changed requirements, assignments and CES weights. | Yes indirectly if demand changes assignments and hence effort exposure. |
| Campaign 2 demand | `environment()` uses stationary one-hot `s0` for A/B and deterministic nonstationary `s0→s1` at t=12 for C (`experiments/synthetic/hls_campaign2/teaching_mis_assignment.py:116–136`). | Same problem stream in all four branches. | Yes across regimes/scenarios. | Yes via assigned competence exposure. But seed has no effect: each distribution places probability 1 on its sole task. |
| Production observation innovation | Coordinate-indexed Gaussian in `indexed_normal_innovation` (`src/hls/hls_lab_dynamic.py:209–215`); enters `individual_observations = effort × real skill + sd × innovation` (`src/hls/hls_lab_v1_integrated.py:488–504`). | Indirectly, through posterior/estimated skill used by P0; only if score ranking changes. | Not directly: actual `outputs` and CES are computed before this observation (`integrated.py:478–482`). Indirectly, only if a changed estimate changes assignment. | Only through that assignment route; private MIS transition itself is deterministic given competence, effort and eta. |
| Competence estimate/posterior | Initialized in runner snapshot; updated from individual observations, then predicted through MIS when LI is enabled (`integrated.py:497–509`). | Yes. P0 consumes estimated competencies through `IntegratedDecisionView`; no direct private-state access. | Not by itself; if choice changes, actual output/CES can change. | It can change future assignment and therefore which skill experiences MIS. |
| MIS-v2 transition | `advance_team` applies `capability_after_exposure` to real competencies only for the assigned expert-skill cells (`hls_lab_dynamic.py:316–359`; law in `discover_develop_v2.py:40–50`). | The real-state transition is not exposed. Its public posterior prediction can influence later P0 choices. | Yes: real competencies affect subsequent `production_inputs` and CES. | It is the modeled experience-learning transition itself; it is deterministic. |
| Directed-teaching transition | In `run_integrated_sequence`, direct gain is `transfer_rate × effort × efficacy × (1 − post-MIS skill)`, capped at 1 (`integrated.py:513–527`). | Direct gain is private; the policy sees only declared observable estimates/memory. | Yes later, through the learner’s real competence and production. It does not alter current CES except through productive effort displaced by the event. | Yes, by changing later real and estimated states. |
| Formative observation innovation | `_training_noise` enters `training_observation` after direct gain (`integrated.py:529–539`); the organizational running-mean efficacy memory and skill posterior are updated when enabled. | Potentially, via later estimates; P0 itself ignores efficacy memory. | Only if updated estimates change a future P0 assignment. | It can affect future estimated competence, not the real teaching increment. |
| Functional success | `evaluate_problem`: every active output must meet its requirement (`src/hls/hls_lab_v1.py:135–153`). | Yes indirectly: it is the first component of P0’s score. | No direct physical effect. It is a diagnostic outcome, not a production input. | No direct effect; only a later decision change could alter exposure. |
| CES | `production_inputs` is additive, `Y_k=Σ_i x_ik s_ik` (`src/hls/discover_v0.py:95–102`); `ces_reward` evaluates weighted CES (`discover_v0.py:105–115`). Campaign 2 computes it from realized deterministic outputs (`integrated.py:478–482`). | No: P0 does not use CES in its ranking. | It measures gross output quality and changes with output. | No direct effect on MIS/teaching transitions. |

The resource cost is recorded as `(productive + teaching effort) × unit price` (`integrated.py:483–486`) but is not subtracted from CES and is not used in P0’s score. The policy score is lexicographic **(success, −normalized deficit, margin, −productive effort)** (`integrated.py:204–215`), not CES, cost or an intertemporal objective.

## 3. Why noisy seeds have identical CES

The published manifest (`results/experiments/hls_campaign2_teaching_mis_assignment/manifest.json`) reports 30 noisy quadruples, three scenarios, ten seeds per scenario, four conditions and 3,264 total trace records including deterministic/negative-control runs. The audit re-read `mechanism_traces.csv.gz` and grouped the ten noisy runs in each scenario × condition by complete 24-period paths:

| Scenario / condition | Demand paths | Individual-observation paths | Estimate paths | Productive-action paths | True-competence paths | CES paths and totals | Success paths |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A / C00, C10, C01, C11 | 1 each | 10 each | 10 each | 1 each | 1 each | 1 each | 1 each |
| B / C00, C10, C01, C11 | 1 each | 10 each | 10 each | 1 each | 1 each | 1 each | 1 each |
| C / C00, C10 (MIS OFF) | 1 each | 10 each | 10 each | 7 each | 1 each | 1 each | 1 each |
| C / C01, C11 (MIS ON) | 1 each | 10 each | 10 each | 1 each | 1 each | 1 each | 1 each |

Counts are distinct complete paths, not independent-sample counts. The 10 logged observation and estimate paths verify that noise was realized and information states differed. Logged observation paths include noise values at zero effort; `update_skill_posterior` explicitly returns the unchanged posterior when effort is zero (`hls_lab_dynamic.py:167–180`), so not every differing logged value is informative. In C/MIS-OFF, action paths differ only after the skill-1 regime begins, with equivalent choices among E0/E1; their true skill-1 competence is exactly tied and their total skill-1 output with E2 is unchanged. Under C/MIS-ON, E0/E1 skill-1 estimates may differ slightly, but the same output-equivalent preference is not broken in the recorded seeds.

The four condition means remain different (A: R00/R10/R01/R11 = 32.400000/33.316094/38.122766/37.946387; B: 27.600000/28.482500/32.302596/34.747049; C: 25.800000/25.752500/30.891515/31.183167). Those are treatment-condition contrasts, not replicate variation. Demand is seed-invariant; observation noise is the only seed-varying exogenous input in this design. The manifest’s output SHA-256 values for all six frozen outputs were recomputed and matched.

The process is therefore: observation noise changes posterior values → in most paths it does not change the maximizing action because the score gap remains on one side of a boundary → the fixed action keeps realized output and deterministic MIS exposure identical. In C, occasional selection among equivalent agents changes the action path but not output, CES or true competence. Identical CES is not explained by noise being absent; it is an outcome plateau induced by the model/design combination.

## 4. P0 decision boundaries

P0 ignores `OrganizationMemory` and `TeachingParameters` (`P0ProductionOnly.choose`, `integrated.py:225–231`). It scores each feasible action from **estimated**, not real, competencies. First it prefers success; then smaller normalized deficit; then greater minimum margin over active requirements; then less productive effort. It neither maximizes CES nor prices resource costs. Catalogue ordering resolves exact ties because Python `max` returns the first equal maximum.

For the period-0 skill-0 task, the relevant competition is `E0+E1` versus `E0+E2`; E0 contributes 0.90 in both. Initial score margins:

| Scenario | Estimated extra-agent skill values | Score margin E0+E1 | Score margin E0+E2 | Gap and selected assignment |
| --- | --- | ---: | ---: | --- |
| A | E1 .45, E2 .25 | .35 | .15 | .20; E0+E1 |
| B | E1 .20, E2 .25 | .10 | .15 | .05; E0+E2 |
| C, before t=12 | E1 .20, E2 .25 | .10 | .15 | .05; E0+E2 |

All alternatives succeed at requirement 1, so success and deficit tie; the score difference is just the difference in active-skill output/margin. Holding all else fixed in the controlled B estimate probe, E1=.249999 selects E0+E2, E1=.25 ties and catalogue order selects E0+E2, while E1=.250001 selects E0+E1. This establishes the exact estimate rank boundary `ŝ(E1,skill0)=ŝ(E2,skill0)=.25`; no production rule or threshold was tuned.

The noisy traces show the decision relevance of that margin. In B, no-teaching MIS-OFF maintains the estimated gap E1−E2 at −.05 for all 24 periods. With the forced lesson, all ten branches switch to E0+E1 at period 1: the observed score gap is .045–.10 in C10 and .03–.085 in C11, and no seed changes the action path. The estimate changes are real but remain in the same action region. In A, E1 begins .20 above E2 and stays selected. In C after t=12, the relevant skill-1 estimates for E0 and E1 are effectively tied at .20 (MIS OFF) while E2 is .80; noise can change which tied low-skill agent is paired with E2, but not active output. These broad/flat regions explain why noisy estimates do not imply variable outcomes.

## 5. Reward, success and sensitivity probes

`evaluate_problem` has a discontinuous binary success indicator at each requirement, but its deficits/margin vary continuously. CES is continuous in non-negative output for the implemented `rho=0.5`; Campaign 2 uses one-hot CES weights, so CES equals the output in the demanded skill exactly. Consequences verified from code and trace:

* **CES changes while success does not:** for requirement 1, output 1.10→1.20 keeps success true while CES changes 1.10→1.20. The campaign’s MIS paths routinely improve gross CES while retaining 24/24 success.
* **Success changes while CES is fixed:** with output 1.15 fixed, changing requirement from 1.14 to 1.16 flips success but leaves CES at 1.15. This is a controlled threshold calculation, not a new episode.
* **Different actions, identical CES:** in C after the shift, assigning the second skill-1 unit to E0 or E1 gives `.20+.80=1.00` either way, hence CES 1.00 under `(0,1)` weights. The action can vary with noisy estimates while CES does not.
* **Estimates change while CES does not:** every scenario/condition has ten estimate paths but one CES path among seeds. Estimates are decision information, not the reward state.
* **Observation noise has no direct reward effect:** changing only observation SD from 0 to the registered .02 changes observations/estimates (deterministic versus noisy artifacts) but not realized output at a fixed action. It can affect reward only through a changed assignment.

At the exact decision boundary in B, changing the estimate from .249999 to .250001 reverses the assignment. With the *same true state* (`E1=.20`, `E2=.25`), realized demanded output moves 1.15→1.10, CES moves 1.15→1.10, both choices still satisfy requirement 1, and the assigned learner differs. If MIS is enabled, that assignment also changes which agent receives the deterministic MIS increment (E1 eta .04 versus E2 eta .02). Conversely, changing a private true skill while freezing the estimate and assignment does not directly change P0’s decision; if the changed agent is unassigned, current output/CES need not change.

## 6. Productive capability frontiers and saturation

At t=0, enumerate the 37 feasible production-only actions under budget 2 and per-expert cap 1. Values below are the maximum output in the active skill; success counts are actions satisfying the campaign’s requirement 1:

| Scenario / demanded skill | Initial max output | Best margin above requirement | Success-feasible actions | Binary success status |
| --- | ---: | ---: | ---: | --- |
| A / skill 0 | 1.35 | .35 | 4/37 | Feasible, saturated under P0 |
| B / skill 0 | 1.15 | .15 | 4/37 | Feasible, saturated under P0 |
| C / skill 0 before shift | 1.15 | .15 | 4/37 | Feasible, saturated under P0 |
| C / skill 1 after t=12 | 1.00 | 0 | 2/37 | Feasible exactly at the boundary |

All declared tasks are feasible without teaching, but C's post-change skill-1 task lies exactly at the frontier and is therefore genuinely near the threshold. In the actual campaign, all no-teaching branches succeed 24/24; teaching branches succeed 23/24 because the forced first teaching action leaves only E2 to produce, yielding .25 in skill 0 rather than the requirement 1. Teaching-period output is not a stochastic production realization.

At each final state, the two-highest-competence production frontier can be calculated from recorded final matrices. For skill 0, max attainable outputs by C00/C10/C01/C11 were A 1.350/1.438/1.771/1.795; B 1.150/1.228/1.516/1.713; C 1.150/1.228/1.364/1.520. These are state-conditional capability frontiers, not additional realized outcomes or policy-free causal effects: the states themselves arose under each arm’s MIS/teaching/assignment history. Campaign 2’s fixed requirement 1 was already solvable without teaching, so it shows no expansion of the *observed campaign success set*. A higher future requirement could lie between conditional frontiers, but no such requirement was executed; that possibility is not an observed campaign result.

## 7. Controlled sensitivity results

| One-factor probe | Change | Action | Realized production / CES | Success | Later learning |
| --- | --- | --- | --- | --- | --- |
| Initial B estimate around choice boundary | E1 skill-0 estimate `.249999 → .250001`, other estimates fixed | Switches E0+E2 → E0+E1 | With same real skills, 1.15→1.10, CES follows | Both succeed at r=1 | MIS exposure moves from E2 to E1 if enabled; deterministic gains differ by eta and current skill. |
| True skill with fixed information | E1 real skill `.20 → .26`; estimate held `.20` | No change: P0 still selects E0+E2 | Current output/CES unchanged because E1 is unassigned | Unchanged | Future real capacity changes; policy can use it only after informative observation/estimate change. |
| Requirement threshold | At fixed output 1.15, r `.1.14 → 1.16` | No change to maximal-output action | CES remains 1.15 | Success flips true→false | No direct transition change. |
| Observation SD | Registered zero-noise fixture → .02 noisy traces | A/B actions unchanged; C/MIS-OFF has equivalent swaps | Same CES path in all seed replicates | Same success path by arm | Estimate paths vary; assignment-sensitive learning changes only if a different effective exposure is selected. |

These are one-factor calculations against fixed states/actions or a comparison already present in the published deterministic/noisy artifacts. They are not a parameter search, a new campaign or a claim that the chosen alternatives are optimal policies.

## 8. Identifiability assessment

| Mechanism | Status | What Campaign 2 supports / what remains confounded |
| --- | --- | --- |
| Direct teaching gain | **Directly observed, conditional** | Trace records log the exact private direct increment; the four-arm toggle and zero-efficacy negative control verify the transition. Not an external empirical estimate of teaching efficacy. |
| MIS-v2 gain | **Directly observed, conditional** | Per-period MIS increments are reconstructed with the existing transition and checked against next true state plus direct gain; MIS-OFF is zero. Factorial interaction is conditional on these scenarios and P0 continuation. |
| Productive assignment changes | **Observed; mediation confounded** | Teaching causes a rank crossing in B/C under the recorded initial state and shifts 23/11 subsequent exposures. This co-occurs with direct gains, displaced initial output and estimate updates; no assignment intervention isolates mediation. |
| Organizational information effect | **Not identified as a causal contrast** | Observations and estimates are logged and seed-varying, but all arms use organizational learning/update enabled and P0 uses the same estimate-driven rule. Need an otherwise matched information-update/use intervention to isolate it. |
| Exogenous demand effect | **Conditionally identified only as B-vs-C package** | B/C share team and first 12 problems; after that, both requirement vector and CES orientation switch with demand. One deterministic change path cannot separate distribution dynamics from task/reward orientation or support variability across demand trajectories. |
| Resource displacement | **Direct accounting; causal value confounded** | Efforts and unused capacity are exact: teaching uses .5, production uses 1.0 instead of 2.0, and .5 remains unused. Its productivity consequence is combined with action-catalogue discreteness and loss of productive MIS exposure. |
| P0 action-ranking criterion | **Mechanism directly inspected; comparative effect not identified** | Score and boundary are exact, but no matched alternative ranking objective was part of Campaign 2. Cannot attribute P0-versus-CES gaps to the score alone from these arms. |

The factorial contrast estimates the **total effect of the assigned teaching intervention conditional on the MIS toggle, shared indexed innovations, fixed demand, and common P0 continuation**. The difference-in-differences is descriptive/causal within this deterministic simulator assignment, but does not decompose mediated shares. It cannot identify general population effects.

## 9. Requirements for future campaigns

These are measurable design-acceptance criteria, not a Campaign 3 design:

1. **Feasibility, not success saturation:** before execution enumerate the actual action frontier; every primary condition must include at least one feasible, one infeasible and one near-boundary demand level, and the planned policy arms must not all have 100% success at every primary level.
2. **Demand diversity:** publish unique trajectories and regime occupancy. If demand is intended stochastic, at least two distinct generated demand trajectories must occur across the prespecified seed set; keep environment innovations separately indexed from observation noise.
3. **Boundary sensitivity:** publish the top-two decision-score gap distribution before outcomes. Include prespecified controlled perturbations on both sides of a real decision boundary; verify that estimates/conditions can change action where that mechanism is intended to be tested. Report equivalence classes where changed actions have identical output.
4. **Trajectory diversity:** report distinct observations, estimates, actions, true-competence paths, reward paths and success paths separately. If competence learning is an outcome, at least one intervention must produce different productive exposures/true competence paths under matched exogenous demand, or explicitly state that this mechanism was not activated.
5. **CES versus success:** include prespecified observations with output changes that leave threshold success unchanged and requirement-boundary observations where success changes independently of CES. Never use binary success alone when it is saturated.
6. **Randomness separation:** key or pre-generate environment, production-observation and teaching-observation innovations independently. Use paired seeds for policy contrasts and report which random stream changes each replicate; do not count seeds as distinct environmental cases when demand is deterministic.
7. **Mechanism identification:** each causal claim must have a matched intervention that toggles that mechanism alone, an observable mediator trace, identical continuation/resources, and an explicit contrast. Assignment mediation requires an assignment/exposure intervention; information effects require a matched information-update/use control; resource-opportunity costs require an accounting/control that distinguishes displacement from unused catalog residual.
8. **Objective alignment:** state that CES is gross performance and keep resource cost separate unless a justified common-unit objective is specified. Record the policy’s actual ranking criterion and do not label a CES difference a decision-quality advantage without a matched objective comparison.

## 10. Open limitations and reproducibility

Campaign 2 used single-skill, one-hot-reward tasks, a fixed 24-period horizon, calibrated initial estimates, a 101-point discrete posterior, deterministic competence/learning dynamics, one predetermined teaching event, and P0 continuation. Demand seed variation was absent. It therefore verifies model mechanisms and boundary behavior, not ecological realism or general policy ranking. The initial success thresholds were too easy to discriminate later productive gains; the one-hot demand/reward pairing makes CES a direct active-output measure. Additive production does not imply superadditive complementarity. No production noise is currently implemented in realized output.

Reproducible audit inputs are the published [Campaign 2 protocol](../../results/experiments/hls_campaign2_teaching_mis_assignment/protocol.json), [manifest and hashes](../../results/experiments/hls_campaign2_teaching_mis_assignment/manifest.json), [paired outcomes](../../results/experiments/hls_campaign2_teaching_mis_assignment/paired_outcomes.csv), [mechanism traces](../../results/experiments/hls_campaign2_teaching_mis_assignment/mechanism_traces.csv.gz), [runner](../../experiments/synthetic/hls_campaign2/teaching_mis_assignment.py), and [analysis/validation code](../../experiments/synthetic/hls_campaign2/analyze_teaching_mis.py). All eight source hashes and six output hashes enumerated in `manifest.json` were verified during this audit. The focused Campaign 2 suite was rerun: **16 passed**. The full repository suite was not rerun; its previously documented **13 provenance/integrity failures remain unresolved**. No production simulator or frozen results were modified.
