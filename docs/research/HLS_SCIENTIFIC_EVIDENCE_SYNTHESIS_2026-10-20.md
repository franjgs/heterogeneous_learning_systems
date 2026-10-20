# HLS scientific evidence synthesis — 20 October 2026

**Purpose:** consolidate established HLS results and preserve their claim
boundaries for prioritizing investigations. This is a synthesis of existing
project evidence, not a new experiment, literature review, or replacement
roadmap. The recovered original plan and activity audit are treated as
historical inputs: [original plan through 30 October](../project/HLS_ORIGINAL_WORK_PLAN_TO_2026-10-30.md)
and [activity audit, 17–19 October](../project/HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md).

## 1. Executive synthesis

HLS already has evidence at several distinct levels: exact static
organization results (G1); minimal action-dependent competence development
(G2); analytical reductions of development value to assignment sensitivity
(G3/G3-H); finite exact policy-class results for joint versus strong-separated
decisions (RQ0); an implemented N×K model with MIS-v2, partial competence
estimation, dynamic demand, and directed teaching; bounded tests and
integration validation; and selected exploratory or exact computational
studies. These are not one interchangeable model. In particular, G0/A1,
MIS-v2, Nembhard productivity, and teaching-efficacy transitions have
different state variables and semantics.

Three conclusions should guide further work:

1. **Heterogeneity or environmental change alone does not imply adaptation
   value.** G1 exhibits both organizational nulls and positive windows;
   E1's fixed route was aligned with its productivity profile; E2.1's
   separable model has no dynamic-over-optimized-static gap in its 33 tested
   cases; and C6's exact gap appears even under stationary demand.
2. **Action-dependent development can change future organization value, but
   this is conditional.** G2 has null and positive controls; G3 identifies
   ordinary assignment gaps as sufficient to calculate development value in
   its model; RQ0 has exact finite-world conditions for strict separation
   failure. None supports universal superiority of a joint or adaptive
   policy.
3. **Knowledge transfer is implemented in the N×K route but is less
   scientifically validated than individual MIS-v2 learning.** The code has
   a directed teaching transition, shared-resource feasibility, fixed and
   adaptive teaching policies, and efficacy memory. Existing bounded S4
   execution verifies a trace path, not the value or robustness of transfer
   under a discriminating controlled comparison. The mathematical and
   experimental question is therefore not whether HLS has any transfer code,
   but when it interacts with individual learning, task demand, and scarce
   resources.

HLS Laboratory remains **PARTIAL**. Test passage validates software contracts
   only within their tested scope; it does not substitute for scientific
   evidence.

## 2. Evidence ledger

| Investigation | Question and mechanism | Assumptions and comparator | Established positive / null evidence | Limitations and unresolved issue |
|---|---|---|---|---|
| **G1 / static organization** | When does organizing existing heterogeneous capabilities enlarge useful collective performance? No learning. | Fixed capability matrix, demand mixture, feasibility/resource constraints; ONE versus ROUTE and attainable frontiers. Two agents, two tasks in reference controls. | Exact analytical controls and executable artifacts establish homogeneous and dominance nulls, crossed-specialization gains, and bounded budget/demand regions. Heterogeneity is not sufficient; demand and constraints mediate value. | Static results do not address capability development, online estimation, or adaptation. See [G1 ground truth](../theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md). |
| **G2 / T4–T6** | Can action-induced learning change future capability and reverse a present allocation preference? | Two agents × two skills × two periods; deterministic learning-by-doing, terminal task-dependent routing and future demand; D0/D1 nulls and D2 positive case. | Exact controls establish: no learning has no development value; learning can change a state without changing the efficient collective frontier; and a specified D2 case has positive future development value and decision reversal. | Existence in a minimal model, not a general allocation policy comparison or population result. See [G2 ground truth](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md). |
| **G3 / G3-H** | How does organization mediate value of competence development? | Three workers × two skills × two periods, assignment feasibility and MIS saturating learning; exact terminal assignment value. G3-H substitutes worker-specific learning rates. | Algebra reduces development value exactly to learning increments and assignment sensitivities/gaps in the specified regimes. G3-H provides an exact counterexample to a local immediate ranking: continuation over the two-period assignment can change the choice. C1's local continuation shortcut fails; C2 reduces to ordinary look-ahead/DP. | Exact formulas are model-scoped; they do not establish general minimal sufficient statistics or require a new mechanism. See [G3/G3-H ground truth](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md). |
| **RQ0 / exact integration boundaries** | When can joint allocation and competence development beat a credible separated policy? | Common world/information/action semantics; HLS may choose admissible routing and development; strong SEP restricts routing to immediate-reward maximizers, optimizes development after realized opportunity; SEP-Omega supplies exact continuation information. | Policy inclusion proves `J_SEP,max ≤ J_HLS`, not strictness. Equality iff some HLS-optimal policy is SEP-admissible in finite exact worlds. The exact `C(alpha)` family contains a model-specific nonempty strict-gap region and a later reducibility region. Initial preregistered A/B cells were reducible; later exact family establishes constructive existence. | No universal phase boundary over all environments; local routing inversion alone is not root value; robustness/prevalence and imperfect-information extension remain open. See [RQ0 boundaries](../theory/rq0_routing_integration_boundaries.md) and [RQ0 campaign record](../experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md). |
| **MIS-v2 / N×K** | How do agent competencies evolve through productive exposure, and how do estimates/policies respond? | Competence in `[0,1]`, exposure-conditioned saturating MIS-v2 transition; divisible effort, resource limits, task requirements; actual state separated from estimates. | Existing tests verify transition, order, controls, estimation, demand generation and traces. The 17 Oct integrated validation reused stationary, scheduled nonstationary and Markov environments, P0/P2 and competence estimation; 135 focused tests passed. This verifies bounded execution and information boundaries, not adaptive superiority. | MIS-v2 is not Nembhard experience/productivity or G0 explicit A1. No forgetting in the canonical transition. P0 is state-responsive; P2 adapts teaching via efficacy memory, not a general long-horizon task-allocation learner. See [capability validation](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md) and [MIS theory](../theory/HLS_CAPABILITY_DEVELOPMENT.md). |
| **Nembhard Direct / Nembhard HLS-E1** | How do heterogeneous experience-productivity profiles and allocation rules behave? | Direct productivity curve `P_ik(D)=k_ik(D+p_ik)/(D+p_ik+r_ik)`; explicit allocation, ORACLE current-period full truth, ADAPTIVE selected-feedback estimates/exploration, and a fixed map. | Nembhard Direct, ORACLE and ADAPTIVE are implemented and tested. The E1 protocol/review found the chosen FIXED map strongly aligned to heterogeneous profiles and near-identical to ORACLE in mixed/specialist cases; ADAPTIVE performed worse in that design. | HLS route adapts the productivity equation, not the complete paper. This E1 is not G0-C6. Local episode/result artifacts conflict with the contemporaneous interruption record in the audit and are not to be treated as newly canonical evidence here. The experiment did not isolate estimator error from exploration or test a sufficiently discriminating fixed baseline. See [protocol review](../experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md) and the [activity audit](../project/HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md). |
| **E2.0 / E2.1** | Does exact dynamic optimization beat static task assignment with Nembhard productivity? | Standalone deterministic models, not the N×K runner. E2.0: one skill/two agents, horizons 20/60/120; exact DP versus greedy and a “best initial agent” fixed comparator. E2.1: two independent skills/two task types; exact DP versus a globally optimized stationary task→agent mapping. | E2.0's saved local output supports the one-agent specialization structure for its specified scalar model. E2.1 reports zero dynamic-over-best-static gaps in 33 tested cases and gives a separability/convexity explanation. These are useful null/boundary cases. | E2.0 fixed comparator was not globally optimized over the horizon. E2.1's conclusion applies only to independent skill dynamics and the tested family; both are standalone worktree artifacts in the historical audit, not general proof that dynamic allocation is unnecessary. See [E2.1 protocol](../experiments/HLS_E2_1_PROTOCOL.md) and [activity audit](../project/HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md). |
| **HLS-G0-C6** | Does anticipating opportunity-gated capability development beat a best stationary routing map in a small stochastic finite horizon? | Two agents, two tasks, horizon four, explicit A1 development, opportunity observed after routing, stationary/changing task demand; exact HLS, BEST_STATIC, MYOPIC and STRONG_SEP. | At `eta=.75`, exact HLS−BEST_STATIC is `.159375` stationary and `.12456` changing. Accounting differences are operational plus `.10625` / `.07232`, terminal plus `.053125` / `.05224`, development-cost difference zero. At `eta=0,.1`, all policies equal 4. The Bellman calculation identifies sacrifice for an opportunity followed by flexible routing. | Gap also occurs under stationary demand; it is not caused by nonstationarity. Opportunity probabilities are degenerate 0/1, cost is zero, 20 pairs/cell are exploratory. The exact analysis is a quantitative instance of G2/G3-H/RQ0 mechanisms; C6 is formally **CLOSED—STOP**, while its result is preserved. It is not MIS-v2. See [C6 closure](../experiments/HLS_G0_C6_CLOSURE_2026-10-19.md). |
| **Contextual quality–cost router** | Can the router predict selected candidate quality/cost from query context and use selected-candidate feedback? | Independent contextual candidate/query route; ridge predictors and quality threshold/cost choice, synthetic environment. | Implementation and focused tests validate prediction/selection/update contracts. | It is not integrated with N×K agents or MIS competence, is not a MixLLM reproduction, and has no scientific evidence about organizational task allocation. See [router contract](../engineering/HLS_MIXLLM_ROUTER_CONTRACT.md) and [architecture](../engineering/HLS_LAB_ARCHITECTURE_2026-10-17.md). |
| **Campaign 2 / prospective adaptation** | How do information and development anticipation affect decisions and their two-step realized consequences? | Frozen C2.0 model, N=3/K=2, MIS-v2, Bayesian problem beliefs, Q00/Q10/Q01/Q11 restrictions, common-seed counterfactual branches; eight scenarios and four probes. | The preregistered reconstruction has 5,120 runs and exact retained-data analysis. Q10/Q11 divergent first decisions have positive mean conditional two-reward consequences in the declared reference-state population; Q01 is mixed/weak. `DeltaQ>0` does not guarantee positive realized `DeltaG`; Q11 > Q10 is not established. | State-conditioned counterfactual estimands over Q11-reference states, not global policy values or general causal benefit. See [Campaign 2 results](../experiments/CAMPAIGN_2_RESULTS.md). |
| **Dynamic lab characterization pilot** | How do existing state, belief, horizon, estimate updates and MIS settings behave under stationary/switching demand? | Existing N×K route, paired seeds, H=1/H=3, four conditions and seven arms, plus a separate organizational table-update block. | 256 runs/5,632 decisions. Descriptive differences show estimated-state updating can help the tested heterogeneous teams and DISCOVER reward can rise with horizon, with functional success moving differently. | Four seeds and bundled policy contrasts; organizational OFF is particularly weak. This pilot is diagnostic, not clean attribution or a confirmatory adaptive-policy result. See [pilot report](../experiments/HLS_DYNAMIC_LAB_CHARACTERIZATION.md). |
| **Knowledge transfer / teaching** | How does directed teacher→learner→skill transfer compete with or complement individual learning and current production? | N×K has `JointActionNK`, `TeachingEfficacyNK`, `teaching_transition_nk`, joint feasibility, MIS-then-teaching order, P1 fixed relation, P2 relation-specific running-mean memory and S4 trace. | Code and focused tests verify bounded transition/resource/information contracts; S4 in the integrated validation exercises the four-period imperfect-observation P2 path. | Existing efficacy tensor is environment truth; P2 uses a formative signal/memory and is heuristic, not exact long-horizon optimization. S4's requirements all fail and it is not a discriminating transfer-benefit experiment. The additional claim “adaptive transfer benefits collective performance” remains unestablished. See [`hls_lab_nk_teaching.py`](../../src/hls/hls_lab_nk_teaching.py), [P2 policy](../../src/hls/hls_lab_nk_policies.py), and [reuse audit](../experiments/HLS_ADAPTIVE_TRAINING_REUSE_AUDIT.md). |

**Provenance note:** the activity audit reports that the C6 closure and result
artifacts were local untracked worktree evidence at its cut-off. The STOP
decision and exact values are retained here as documented local evidence, not
misrepresented as a result newly published on the tracked branch.

### 2.1 Interpretation of positive and negative evidence

- **Positive finite-instance evidence** is meaningful when tied to a declared
  model: G1 frontier gains, G2 D2, RQ0 `C(alpha)`, C6, and specific Campaign 2
  conditional returns. These do not support universal adaptive superiority.
- **Null results** are equally informative: G1's dominance/homogeneity cases,
  G2 D0/D1, initial RQ0 reducible cells, E2.1's separable family, and C6 at
  low development intensity identify structures where extra decision freedom
  is not valuable or is not exercised.
- **Execution validation** (the 135 focused tests and compact S0–S4 checks)
  establishes that existing paths run and traces expose state, estimates,
  demand and decisions within scope. It does not establish that a policy
  dominates a strong comparator.
- **Documentary proposals and WIP** (including method-selection preflights,
  Campaign 4 verification preparation, adaptive-training specifications and
  other current uncommitted material) are not scientific findings or approved
  changes to canonical models. The [activity audit](../project/HLS_ACTIVITY_AUDIT_2026-10-17_TO_19.md)
  preserves these provenance distinctions.

## 3. Reusable scientific assets and limits

| Asset | Reuse justified for | Do not silently reuse as |
|---|---|---|
| G0/RQ0 exact finite-world solver and policy classes | Full-information finite exact comparisons, opportunity timing, strong-SEP and SEP-Omega boundaries | General N×K/MIS-v2 runner, partial-observation solver, or online learner |
| N×K/C5 environment and runner | Divisible effort allocation, functional evaluation, stationary/nonstationary/Markov task paths, resource and trace records | G0 A1 opportunity model or Nembhard productivity model |
| MIS-v2, competence posterior, P0/P1/P2 | Individual exposure learning, estimated competence views, fixed/adaptive teaching trace and limited relation memory | Proof of optimal allocation, unknown capability law, or broad teaching value |
| Nembhard Direct/ORACLE/ADAPTIVE | Experience-dependent productivity, current-period full-information and selected-feedback contrasts | MIS-v2, published Nembhard allocation algorithm, or complete paper reproduction |
| Campaign 2 counterfactual/replay artifacts | State-conditioned prospective decision/reward analysis under its frozen model | Unbiased estimates of whole-policy values or general information value |
| Contextual router + common experiment record | Independent query/candidate contextual prediction and portable run/event records | Shared policy architecture or scientific equivalence among HLS mechanisms |

The exact implementation inventory and bounded validation status are in the
[canonical adaptive-capability validation](../experiments/HLS_LAB_ADAPTIVE_CAPABILITY_VALIDATION.md).

## 4. Handover boundary

The next report prioritizes investigations using this evidence. It does not
reopen closed G1/G2/G3/C6 work, select a new published method, prescribe an
architecture, or authorize implementation/campaign execution. The 22 October
mathematical handover should formalize policy classes, information, transitions
and comparison quantities before any design is promoted to an experiment.
