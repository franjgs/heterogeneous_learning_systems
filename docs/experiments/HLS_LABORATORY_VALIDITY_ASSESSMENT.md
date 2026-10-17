# HLS Laboratory Experimental Validity Assessment

**Recorded:** 2026-10-16 10:15 +02:00 (Europe/Madrid)

**Scope:** inspection and deterministic instrument-validation fixtures only.

**Laboratory status:** PARTIAL. No new scientific campaign or simulator-physics change.

## Executive assessment

The current laboratory can compare a restricted set of three-agent, two-skill organizations and existing strategy packages on the same frozen demand path, with matched initial state and coordinate-indexed observation innovations. It can distinguish competence-sensitive production, functional feasibility, action allocation, MIS-v2 learning, directed teaching, and resource use in controlled fixtures. It is therefore useful for bounded mechanism and engineering comparisons.

It does **not** yet support an unqualified claim that one organizational architecture or policy is generally superior. `P0`, `P1`, and `P2` differ in more than a single decision rule; P1 attempts its configured lesson when feasible, while P2 explores/uses organizational efficacy estimates and abstains when its current functional production score already succeeds. Production ranking maximizes success, negative normalized deficit, margin, then lower effort—not CES or a common net resource-valued objective. Equal budgets do not imply equal use. These diagnostics validate instruments, not external validity or general superiority.

## 1. Experimental factorization

| Dimension | Configurable now | Hard-coded / dependencies | Existing controls | Missing controls / validity implication |
| --- | --- | --- | --- | --- |
| **Architecture** | Initial true and estimated competence matrices through `make_team`/`TeamState`; individual MIS-v2 rates; three indexed experts; two skills. | Fixed team cardinality and skill dimensionality; additive production; teaching relation is an ordered expert pair × skill. Competence, learning-rate, and teaching-efficacy heterogeneity can be changed independently in fixtures, but no validated architecture schema enforces aggregate matching. | Manually matched initial matrices; skill totals can be held constant while redistributing skills across agents. | No general agent-count/capability-graph/role interface. Specialist/generalist contrasts need explicit matching of total competence and learning potential. |
| **Policy** | Existing `P0ProductionOnly`, `P1FixedTeaching(relation)`, `P2AdaptiveTeaching(relations)`; first-action override for one-period diagnostics. | P0 ranks by functional success → deficit → margin → lower effort. P1 and P2 add distinct teaching rules. P2 explores unseen configured relations only when best production does not already succeed, then applies an efficacy threshold. Policies receive observable `IntegratedDecisionView`, not private truth. | Frozen problems and same initial team through `compare_integrated_policies`; action-level override in diagnostic runner. | No one-factor policy contrast varying only assignment while holding teaching and information/update rules fixed. P0/P1/P2 contrasts are strategy-package comparisons, not isolated “adaptivity” effects. |
| **Mechanisms** | MIS-v2 profile and LI toggle; teaching efficacy table, effort/transfer parameters; observation noise; competence prior/grid; organizational efficacy-memory update toggle. | Production additive; direct teaching follows production and MIS-v2; at most one lesson per period; teaching consumes both participants’ effort; observed individual output depends on allocated effort and true skill. Organizational learning updates teaching-efficacy estimates, not a general organization model. | LI ON/OFF; zero-efficacy teaching control; fixed-action control; configurable coordinate-indexed observation noise. | No general handoff/transfer, divisible production, or independently randomized realized-production noise. Parameters are experimenter-configurable but not externally calibrated. |
| **Scenario** | Frozen `IntegratedProblem` sequence; requirements, CES weights, budget, per-expert effort cap, resource unit cost; C5 stationary/nonstationary/Markov demand and `DemandRegime` emissions; horizon. | Two output dimensions; three-expert action catalogue; requirements determine functional success; legacy `difficulty` is not an independent calibrated difficulty variable. Environment is exogenous. | `generate_environment_trajectory` freezes a policy-independent trajectory; same tuple can be passed to every policy. | No calibrated mapping from task requirements/resource levels to real-world difficulty. Arbitrary scenarios establish internal behavior only. |

Code anchors: `src/hls/hls_lab_v1_integrated.py` (`IntegratedDecisionView`, `_outputs_score`, P0/P1/P2, `run_integrated_sequence`, `compare_integrated_policies`, `enumerate_feasible_integrated_actions`); `src/hls/hls_lab_v1_environment.py` (`ExogenousEnvironmentConfig`, `generate_environment_trajectory`); `src/hls/hls_lab_v1.py` (`TeamState`, `ProblemSpec`, `make_team`, `feasible_actions`); `src/hls/discover_v0.py` (`JOINT_ACTIONS`, `production_inputs`); `src/hls/discover_develop_v2.py` (MIS-v2); `src/hls/hls_lab_dynamic.py` (`LearningProfile`, `DemandRegime`); `src/hls/synthetic/c5.py` (demand processes).

## 2. Comparison-validity audit

- **Demand:** valid common exogenous paths are available. Generate once and reuse the immutable problem tuple. The environment generator does not receive organization state or actions. A seed alone is not a matched scenario unless the emitted trajectory is shared.
- **Initial conditions:** same initial team and problems can be passed to comparisons; the runner branches state. `make_team` defaults estimates to true skills, so that default is oracle initialization. Partial information requires explicitly independent estimates.
- **Randomness:** environment/emission paths are generated before policy runs; observation innovations are coordinate-indexed by seed/period/expert/skill, so action-dependent random-number consumption does not shift later shocks. Observed values can still differ because effort and true output differ. There is no realized production noise: production-observation noise changes information, not physical output or CES.
- **Resources:** common budget and per-expert caps are enforceable. Production effort, teaching effort, total use, residual and nominal resource cost are logged. Equal constraints do not imply equal consumption. Teaching can strand capacity because the production catalogue is discrete.
- **Outcomes:** CES is gross reward. Resource cost is reported separately and not subtracted; no arbitrary exchange rate is imposed. Functional success is separately measured. Neither CES nor success alone is a net economic objective.
- **Information:** real competence, estimates, observations, actions, teaching gains and outcomes are traceable. Policies see estimates, requirements, resource limits and efficacy estimates, but not real competence, true efficacy or latent environment state. Private trace fields must not be fed back to policies.
- **Interpretation:** P0/P1/P2 contrasts are total strategy-package effects. They do not isolate policy, memory, teaching, or information. CES/success can rank actions differently from `_outputs_score`.

## 3. Predeclared diagnostics and results

Expected behavior and falsifiers were declared from the implementation before execution. Runner and machine-readable results/manifest: `experiments/synthetic/hls_lab_v1/laboratory_validity_diagnostics.py` and `results/diagnostics/hls_laboratory_validity_assessment/`. Reproduce with:

```sh
PYTHONPATH=src python experiments/synthetic/hls_lab_v1/laboratory_validity_diagnostics.py
```

Seed `2026101607` keys indexed innovations; the fixtures are deterministic and are not population replicates.

| Diagnostic | Predeclared expectation / falsifier | Observation | Status |
| --- | --- | --- | --- |
| A. Equivalence / negative control | Same team, sequence and zero noise with different seeds yields identical traces; any difference falsifies reproducibility. | Full signatures identical; CES `2.2, 2.2`; 2/2 success in both. | PASS |
| B. Competence-sensitive | Same fixed one-unit allocation; relevant skill `.5→.6` adds `.1` output/CES, both successful at requirement `.4`. | Output/CES `.5→.6`; success true in both. | PASS |
| C. Feasibility boundary | Enumerate feasible frontier first; `frontier−.01` succeeds and `frontier+.01` fails. | Frontier `1.15` (maximizer action index 51); output `1.15`; requirements `1.14/1.16`; success true/false. | PASS |
| D. Assignment-sensitive | Same team/problem/resources; allocate one unit to expert at `.8` versus `.2`, requirement `.5`. | Outputs `.8/.2`; success true/false. This is an action intervention, not policy-quality evidence. | PASS |
| E. MIS-v2 mechanism | Singleton repeated action: first output equal; only LI ON raises exercised skill and second output. | LI OFF `.4,.4`, final skill `.4`; LI ON `.4,.7`, final skill `.85`. | PASS |
| F. Resource accounting | Budget 2; no-lesson catalogue admits production effort 2; lesson consumes `.5`, max production 1, total 1.5, residual `.5`. | As predicted; gross CES `1.15` without lesson, `.25` with; nominal resource costs `.4/.3`, reported separately. | PASS |
| Negative: zero teaching efficacy | Direct gain zero, but lesson effort still charged. | Gain `0`; teaching effort `.5`; total use `1.5`. | PASS |
| Matched P0/P1/P2 path | Same frozen generated problems, budget, initial team and seed. | Three-period stationary C5 path reproduced exactly. P0: CES `.825`, 3/3 success, effort 6, no teaching. P1: CES `.15`, 0/3, production 3, teaching 1.5, total use 4.5. P2: CES `.825`, 3/3, no teaching; matches P0 in this fixture. | PASS for matching only |

Two executions produced identical `diagnostics.json` SHA-256: `b3778c626f7fad6800fc74d88922f0feb8324858d37da7d8893d08a42fc7bb58`. The manifest records source hashes and run timestamp. Focused tests: `PYTHONPATH=.:src pytest -q tests/test_hls_lab_v1_integrated.py tests/test_hls_lab_v1_environment.py tests/test_hls_behavioral_plausibility.py` — **26 passed**.

In the resource fixture, the `.5` teaching charge reduces maximum available production effort from 2 to 1: 1 unit is displaced and `.5` budget is stranded. This is a catalogue-specific result, not a universal teaching cost.

## 4. Testability and confounding

**Testable internally:** whether an action meets specified functional requirements; additive output response to skills and assignments; controlled MIS-v2/teaching transitions; equality of a frozen demand path; and resource accounting. These are conditional on supplied team, problem, mechanism parameters and continuation rule.

**Not isolated by ordinary P0/P1/P2 comparisons:** assignment rule versus teaching availability; efficacy memory versus exploration/abstention; architecture versus learning potential unless matched; gross reward versus resource value; information gain versus changed action; and MIS-v2 versus teaching when both alter later competence. P0 optimizes functional ordering, not CES. A common budget is not equal realized use. Deterministic seeds are not independent scenarios.

**External validity needs:** calibrated meanings for skill, task requirement, production, teaching efficacy, resource unit, demand frequency and observation error. The lab does not establish that its additive production or simple teaching transition predicts real teams.

## 5. Minimal development backlog (not implemented)

| Priority | Question enabled | Limitation | Smallest next step | Acceptance test | Confounding risk | Necessary now? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | When does one strategy outperform another under a common meaningful objective? | CES is gross, resource cost separate, and P0 optimizes another ordering. No justified common scale exists. | PI/CE selects fixed-budget gross-CES comparison with costs separate, a constrained objective, or an externally calibrated net value; no scalarization by default. | Declared rule reproduces from traces without hidden coefficients. | Scalar objective embeds preferences and can reverse ranks. | Yes before overall/net superiority claims; no implementation yet. |
| 2 | What is architecture effect apart from aggregate capability? | Architecture labels can bundle total competence, estimates, learning rates or efficacy. | Define matched fixtures using existing `TeamState`: equal skill totals and learning-rate totals, redistribute profiles. | Assert aggregate matches and identical demand/resources; report component dimensions. | Mismatched estimates or agent-specific learning potential. | Only for architecture claims. |
| 3 | Does a decision rule add value apart from teaching/information? | P0/P1/P2 are bundles. | First specify a causal contrast; if justified, expose a controlled use of existing assignment rule, not new physics. | Pair differs only in declared decision factor. | A control policy may be artificially weak/strong. | No new policy justified now. |
| 4 | Does physical uncertainty alter outcomes? | Production noise is absent; observation noise does not affect realized output. | If an application requires it, add a separate indexed physical innovation, preserving zero-noise behavior. | Zero noise recovers exact outcomes; nonzero alters realized outcomes reproducibly. | Confusing environment randomness with measurement error. | No for current validity checks. |
| 5 | Do findings extend to larger concurrent teams/tasks? | v1 fixed at 3 experts, 2 skills, one problem per period. | Extend only for a specific queueing/concurrency question. | Preserve resource and H=1 invariants. | Scaling changes feasible actions and policies together. | No. |

## 6. Decision and limitations

**Validity decision:** PASS for the enumerated internal instrument diagnostics; **not sufficient for general architecture/policy superiority claims**. Matched, conditional mechanism comparisons are possible. External calibration and an outcome contract are absent. No new campaign or architecture is recommended.

Minimum next step: PI/CE chooses the comparison estimand—fixed budget with gross CES and resource use separately, a constrained objective, or calibrated net value. Then prepare matched architecture fixtures only if architecture is the next approved question. This is not a Campaign 3 design.

These deterministic checks do not validate population effects, field realism, stochastic realized production, teams larger than three, dimensions beyond two, concurrent tasks, or transfer beyond the specified teaching relation. The previously recorded 13 repository integrity/provenance failures were not rerun or concealed. Laboratory status remains **PARTIAL**.
