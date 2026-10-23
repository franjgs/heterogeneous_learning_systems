# HLS research note — separability and intertemporal coupling of USE and DEVELOP

**Date:** 23 October 2026
**Status:** **EXPLORATORY — PRELIMINARY SCIENTIFIC ASSESSMENT.** No implementation or experiment was performed for this note.
**Scope:** evidence already in HLS, selected literature, and mathematical implications. This is not a general literature review or a claim of novelty.

## 1. Question and motivation

> Under what conditions can the organization and development of heterogeneous capabilities be managed separately, and when does their intertemporal coupling materially improve collective performance?

In HLS terms, **USE** denotes decisions that deploy current capabilities to current work; **DEVELOP** denotes deliberate decisions that change capabilities, such as training or transfer. Work may also cause unavoidable learning-by-doing. That endogenous transition belongs in the physical model even when there is no deliberate DEVELOP action. The key distinction is between (i) capability state changing, (ii) the feasible collective outcomes changing, (iii) future performance changing, and (iv) a current decision changing because of that future value. These are progressively stronger claims.

The broad phenomenon is established in operations research: assignment can create experience that changes later productivity, and integrated training and scheduling models already exist. HLS therefore should not claim originality for “jointly considering assignment and learning.” The potentially useful question is narrower: characterize when an explicitly defined, modular USE/DEVELOP decision architecture reproduces the joint optimum, and when information or constraints omitted at its interface create a measurable loss.

## 2. What the existing HLS evidence says

The ontology already separates the physical system and its competence transitions (A), organizational decisions and feasible actions (B), and decision mechanisms (C); evaluation is independent through HLS-PEF. See the [unified framework](../architecture/HLS_UNIFIED_FRAMEWORK.md), [ontology](../architecture/HLS_ONTOLOGY_V0_1_2026-10-23.md), and the canonical [current state](../HLS_CURRENT_STATE.md). The following are results of bounded models, not claims about organizations generally.

| Evidence | What is represented and observed | What it supports—and does not support |
|---|---|---|
| **S2b, intertemporal budget** | B3 decisions share a nonrenewable budget across periods. | Exact Bellman value 1.00 versus myopic 0.90 at budget 1; both give 1.90 at budget 3, and both give 0 at budget 0. This shows that shared intertemporal feasibility can make planning valuable in that finite instance. It is not competence development. See the S2b row in the [current state](../HLS_CURRENT_STATE.md) and the [cumulative record](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md). |
| **S4 / MIS-v2** | Production uses pre-update competence, with output `y_k=Σ_i x_{ik}c_{ik}`. Work then changes each agent-skill cell as `c′=1−(1−c)exp(−λ(η_ik)x_ik)`. Optional directed teaching changes only the learner's target cell by `c′=min(1,c+r e T[i,j,k](1−c))`; it consumes participant effort and may displace production. Resources are shared. The implemented transition sources are [MIS-v2](../../src/hls/hls_lab_nk_learning.py), [production](../../src/hls/hls_lab_nk_production.py), and [teaching](../../src/hls/hls_lab_nk_teaching.py). | USE affects future capability through experience. Teaching can change future output, but opportunity, horizon, demand, saturation, resource cost, and subsequent assignment all matter. The exact `T=3, x,y,y` transfer/no-transfer optima both equal 1.9175000000000004; the selected transfer frontier had no positive gain for its tested `x^p y^q` cases. Neither is evidence that teaching never helps. |
| **S7, exact uncertain-demand instance** | MIS-v2 learning, optional transfer, Markov demand, and finite-horizon Bellman decisions. | In the central `T=4` case, CES is 3.1628653621 without transfer and 3.1743777327 with it. Mechanistic audits show policy differences can arise from how tied immediate rewards distribute learning, while a current-demand myopic control matches Bellman in that case. The case exposes future-state value but does not establish that forecasting is necessary in general; CES and functional service also diverge. |
| **S4 Campaign 1 and HLS Campaign 2** | Fixed teaching interventions, MIS-v2 toggles, shared resources, and a common P0 continuation rule; Campaign 2 used three prespecified configurations. | The sign of teaching × MIS interaction varied: Campaign 2 interaction was −1.092473 in the substitution candidate, +1.561953 in the enabling candidate, and +0.339151 under the demand shift. These are conditional on forced period-0 teaching and P0 continuation—not joint-optimal values. Campaign 1 found mean P2−P0 CES −0.184 overall, with positive contrasts in a predeclared high-deficit/high-efficacy/long-horizon/MIS-off cell and no such result with MIS on. The counterfactual teaching analysis averaged −0.074 over selected branches, positive early and negative late. Together these show conditionality and opportunity cost, not a general benefit or a necessary joint-management result. See [Campaign 1 findings](../experiments/HLS_CAMPAIGN1_FINDINGS.md) and [HLS Campaign 2 findings](../experiments/HLS_CAMPAIGN2_FINDINGS.md). |
| **T4–T6, G2 and RQ0** | Analytical separation of action-induced state change, future collective-capability change, future value, and current decision relevance; exact finite routing/development policy classes. | HLS already has null and positive constructions. Its RQ0 analysis proves policy inclusion and an exact finite criterion for strict value relative to **strong SEP**. It also shows SEP-Omega, supplied with exact continuation information, can match the joint policy in audited worlds. This is scoped theory, not a universal irreducibility claim. See [dynamic theory](../theory/HLS_DYNAMIC_THEORY.md), [G2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md), and [RQ0 boundaries](../theory/rq0_routing_integration_boundaries.md). |

**Related but not direct USE/DEVELOP evidence.** The historical Campaign 1–3 records use `TR-*` as demand/problem histories, not scenario families. The old prospective-adaptation Campaign 2 studies DISCOVER/DEVELOP and changing problem histories; its Q01 realized utility was not established (mean 0.0015, 95% interval [−0.0194, 0.0193]) and reported coupling was rare (71/15,360, about 0.46%). Campaign 3 META-VOC concerns adaptive allocation of decision computation: its equal-domain META-VOC-50 minus RANDOM-50 `mu_true` contrast was +0.1167 (95% interval [0.0310, 0.2013]), but the frozen proxy, one stochastic history per cell, post-development designation of the 50% primary point, and held-out-team results limit interpretation. These are evidence about adaptation and information allocation in their respective synthetic settings, not direct evidence that work allocation and durable competence development must be jointly optimized. See [historical Campaign 2](../experiments/CAMPAIGN_2_RESULTS.md) and [Campaign 3 META-VOC](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md). `TR-PR`, `TR-PM`, etc. remain demand histories; none is an S scenario or a canonical S8.

**Evidence distinction.** The S4/S7 and campaign results are computed observations in declared models. The code verifies their transition and accounting contracts; this is not empirical validation of a human workforce. A positive teaching contrast under a fixed continuation policy is not the value of optimal development. Nor does a competence increase imply a change in collective frontier or service value.

## 3. Closest published work

| Work | Formal problem and demonstrated result | Relation to HLS and boundary |
|---|---|---|
| Jin, Hewitt & Thomas (2015), [*Selection, grouping, and assignment policies with learning-by-doing and knowledge transfer*](https://doi.org/10.1016/j.cie.2014.11.006), *Computers & Industrial Engineering* 79, 175–187. | Worker selection, grouping, and task assignment with empirically based learning-by-doing and transfer; compares policy stages in simulated serial/parallel settings. Reports that selection effects tended to exceed grouping or assignment effects, and individual transfer-parameter policies performed well. | Direct antecedent for heterogeneous workforce organization with learning and transfer. Its staged policy analysis is not a theorem that USE and DEVELOP are separable; it makes any claim that simply combining these ingredients is new untenable. Evidence here is the publisher record/abstract and bibliographic metadata, not a verified full-text reanalysis. |
| Jin, Hewitt & Thomas (2018), [*Workforce grouping and assignment with learning-by-doing and knowledge transfer*](https://doi.org/10.1080/00207543.2018.1424366), *International Journal of Production Research* 56(14), 4968–4982. | Workers learn through their own jobs and by observing/interacting with co-located colleagues; grouping and assignment jointly shape learning and output. The article models non-linear learning and studies team and assignment choices. | Strong precedent for cross-agent externalities and USE/learning coupling. Available metadata/abstract supports this scope; do not infer details or quantitative claims beyond it without full text. |
| Valeva, Hewitt, Thomas & Brown (2017), [*Balancing flexibility and inventory in workforce planning with learning*](https://doi.org/10.1016/j.ijpe.2016.10.026), *International Journal of Production Economics* 183, 194–207. | Stochastic workforce planning with learning, cross-training, and inventory. Their computational study reports cross-training increasing with demand uncertainty, practice increasing with inventory holding cost, and more practice for less experienced workers. | Shows that resource opportunity costs and uncertain demand alter workforce development/use choices. It is a two-stage stochastic planning formulation; it does not give a general condition for joint versus modular control. |
| Chen, Hewitt & Thomas (2018), [*An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers*](https://doi.org/10.1016/j.ijpe.2017.10.028), *International Journal of Production Economics* 196, 122–134. | MDP for task assignment where experience reduces later service time and future customer demand is uncertain; approximate dynamic programming values today’s assignments over the horizon. Their computational study outperforms a one-step look-ahead comparator and studies when the gain varies. | Closest direct precedent for USE-induced development and intertemporal assignment value. A planning-versus-myopic advantage in a comparable HLS setting is not itself novel. Their state, service-time objective, known learning rates and approximation are not identical to HLS MIS-v2 or explicit teaching. |
| Su, Zhong & Zhang (2025), [*Integrated training course planning and hierarchical multi-skilled employee scheduling in the workforce skill transformation context*](https://doi.org/10.1016/j.ijpe.2025.109642), *International Journal of Production Economics* 286, 109642. | An integrated integer program jointly plans training courses and multi-skilled employee scheduling under precedence, skill requirements, and course capacities; proposes column-generation-based heuristic and evaluates simulated home-service instances. | Directly covers deliberate training jointly scheduled with work. It makes “joint training and scheduling” alone an especially weak novelty claim. Its course/certification structure and profit objective differ from HLS’s cell-level competence transitions and MIS-v2. |
| Nembhard & Bentefouet (2012), [*Parallel system scheduling with general worker learning and forgetting*](https://doi.org/10.1016/j.ijpe.2012.05.024), *International Journal of Production Economics* 139(2), 533–542. | Parallel task scheduling with worker/task-specific productivity changing through learning and forgetting; derives structure of optimal solutions to permit a MILP formulation, including extensions for dependent/stochastic learning and requirements. | Relevant to exact scheduling structure under dynamic productivity. It does not by itself compare separate and joint deliberate-development managers. |
| Akbarzadeh & Mahajan (2022), [*Conditions for indexability of restless bandits and an O(K³) algorithm to compute Whittle index*](https://doi.org/10.1017/apr.2021.61), *Advances in Applied Probability* 54, 1164–1192. | Sequentially allocates a shared resource among independent controlled Markov projects. Gives sufficient indexability conditions and an index computation algorithm; Whittle policy is a relaxation-based heuristic for the coupled problem, not generally an exact solution. | Relevant if each competence/agent is a separable project and the main coupling is a shared allocation limit. HLS assignment, cross-agent teaching, multi-skill feasibility, and shared task rewards can violate independent-project assumptions; applicability must be proved, not assumed. |

The literature already covers the central ingredients and several integrated formulations. Formal factorization conditions below are elementary Bellman consequences; they should not be claimed as new without a narrower result extending established decomposition/indexability theory.

## 4. Minimal mathematical model

Let `c_t` be the competence state, `z_t` the exogenous demand/environment state, and `b_t` any remaining shared resource state. A decision-maker observes `i_t` (the current state when fully observed, or a belief/observation history when partially observed). At time `t`, choose operational use `u_t` and deliberate development `d_t` from a common feasible joint set

\[
\mathcal A(c_t,z_t,b_t)=\{(u,d): h(u,d,c_t,z_t)\le b_t\}.
\]

The transition and observation laws are

\[
c_{t+1}=F_c(c_t,u_t,d_t,w_t),\quad
z_{t+1}=F_z(z_t,w_t),\quad b_{t+1}=b_t-h(u_t,d_t),
\]
\[
i_{t+1}=H(c_{t+1},z_{t+1},u_t,d_t,\nu_{t+1}),
\]

where `w_t` is exogenous uncertainty and `ν` observation noise. `F_c` must include any unavoidable MIS/learning-by-doing effect of `u_t`, even when `d_t=0`. Let `r(c,z,u,d)` be the declared collective period reward, and `g_T` any terminal value. For common information and physics,

\[
V_t(i_t)=\max_{(u,d)\in\mathcal A(i_t)}\mathbb E\left[r_t+\gamma V_{t+1}(i_{t+1})\mid i_t,u,d\right],\quad
V_T= G_T.
\]

This objective is specific to an instantiated problem; CES, functional success, resources, and competence are not interchangeable. A cost can be a constraint or an explicitly declared reward term, but must not be silently subtracted twice.

### Sufficient separability (not necessary conditions)

Suppose the decision state is a product `(x^U,x^D,z)`; the feasible actions factor as `U(x^U,z) × D(x^D,z)` (no shared resource/feasibility constraint); the one-period reward is additive, `r_U(x^U,z,u)+r_D(x^D,z,d)`; component transitions factor conditional on the common exogenous state and their own controls; the `z` transition is uncontrolled; and the information/belief state preserves that factorization. Then finite-horizon Bellman induction gives

\[
V_t(x^U,x^D,z)=V_t^U(x^U,z)+V_t^D(x^D,z),
\]

and a pair of separate maximizers is jointly optimal because `max_{u,d}(Q_U(u)+Q_D(d))=max_u Q_U(u)+max_d Q_D(d)`. These are strong **sufficient** conditions, not necessary conditions. Shared exogenous demand does not by itself break separation if it enters both additive components but is uncontrolled and observed and transitions remain conditionally factored. Conversely, a shared budget, cross-agent transfer, non-additive output/reward, coupled observation, or a USE-dependent competence transition generally breaks this factorization. Breaking the proof conditions does not prove a positive value gap; accidental equality or an optimal factorized policy may remain.

### Three policy classes and a comparability condition

1. **USE-ONLY:** set deliberate `d_t=0`; retain all physical effects of using skills, including inevitable learning-by-doing. This identifies whether deliberate development adds value, not whether use and development effects are independent.
2. **SEPARATED USE/DEVELOP:** use the same physical joint action set, observations, horizon, and constraints, but produce `u_t` and `d_t` through separately specified decision modules. The modules must state their objectives, shared information, exchange protocol (for example, a predeclared resource price or a common feasibility coordinator), and update frequency. There is no unique “separated” value until this interface is fixed. A module may not be handicapped by hiding available information or actions merely to create a gap.
3. **JOINT USE/DEVELOP:** a nonanticipative policy chooses the same feasible `(u_t,d_t)` using the same `i_t`, optimizing their joint continuation value. It sees no future realization or privileged hidden competence.

If the joint class contains every policy admitted by a defined separated architecture, then `V_joint ≥ V_separated` follows from policy-class inclusion. That inequality is bookkeeping, not a finding. A meaningful result is equality versus strictness and the size/conditions of the gap. If the separated architecture is supplied the exact action-conditioned continuation signal (SEP-Ω in HLS RQ0), it can reproduce the joint choice in the audited finite worlds; this is evidence against equating modular organization with myopia.

## 5. What can be concluded analytically now

### Result A — separability

The factorized MDP conditions above are sufficient for exact decomposition. A second sufficient route is decision equivalence: even with coupled physics, if there exists at least one joint-optimal policy that the declared separated architecture can implement on its positive-probability histories, the optimal values are equal. This second condition is exact but policy-level, not a simple primitive-parameter test. HLS's RQ0 finite theory already proves the corresponding criterion for its strong-SEP class: `J_HLS=J_SEP,max` iff an HLS-optimal policy lies in SEP; strictness iff none does. This theorem is scoped to the stated common-world and information contract.

### Result B — strict coupling

An exact minimal HLS construction already exists in [G2 D2](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md): two agents, two task types, two periods, and assignment-dependent learning-by-doing. Current rewards are 0.7 for assigning agent 1 to task 1 and 0.8 for agent 2. Agent 1's task-1 competence increases by 0.3 if assigned. With future task-1 demand probability `p`, the future collective value after action 1 is `max(0.6+0.4p, 0.8)`; after action 2 it is 0.8. For `p≤0.5`, the future-value difference is zero. For `p>0.5`, it is `0.4p−0.2`; after the current reward loss of 0.1, the joint choice switches to action 1 exactly when `p>0.75` (ties at `p=0.75`). At `p=1`, action 1 therefore improves total value by 0.1 over current-reward-greedy action 2. This verifies a transition → capability → value → decision chain in that model. It does **not** establish a new result relative to the workforce learning/scheduling literature, and its comparator is myopic USE, not a general, well-coordinated separated USE/DEVELOP architecture.

For deliberate training, the S4/HLS Campaign 2 configurations demonstrate conditional effects under fixed P0 continuation, including opposite interaction signs and opportunity-cost controls. They do not compute `V_joint−V_separated` for optimal policy classes. Thus the repository has a strict exact USE/learning example and conditional teaching evidence, but no general proof that deliberate USE and DEVELOP must be managed jointly.

### Result C — value of coordination and bounds

For any *fixed* separated policy `π_S` in the same finite-horizon MDP as an optimal joint policy, define its Bellman residual

\[
\delta_t(s;\pi_S)=V_t^*(s)-\left[r(s,a_t^{S})+\gamma\mathbb E\{V_{t+1}^*(S')\mid s,a_t^S\}\right]\ge0.
\]

Under the same terminal value and transition law, telescoping the Bellman recursion yields the exact performance-difference identity

\[
V_0^*(s_0)-V_0^{\pi_S}(s_0)=\mathbb E_{\pi_S}\sum_{t=0}^{T-1}\gamma^t\delta_t(S_t;\pi_S).
\]

Consequently, the gap is bounded above by `Σ_t γ^t sup_s δ_t(s;π_S)` whenever these suprema are finite. This is a useful diagnostic decomposition into missed continuation value, but not a primitive bound: it requires the joint value function and depends on the separated policy. A nontrivial bound in terms of interpretable coupling magnitudes (learning sensitivity, shared-resource shadow prices, transfer externalities, or information loss) cannot be asserted without regularity/boundedness assumptions and a precise separated interface. No general finite bound exists from the current ontology alone if rewards or horizons are unbounded.

## 6. Originality control and candidate question

| Candidate | Classification now | What would have to be new / evidence still needed |
|---|---|---|
| “Joint scheduling with learning beats myopic scheduling.” | **Known result / adaptation.** Chen et al. directly study and report this; HLS S7/G2 supplies scoped exact constructions. | No standalone novelty. A different HLS transition is not enough unless it reveals a result not covered by the literature. |
| “Integrated training and production scheduling matters.” | **Known result.** Su et al. (2025), Valeva et al. (2017), and Jin et al. study closely related integrated workforce decisions. | No novelty from the integration label or a positive synthetic example. |
| RQ0 policy inclusion, exact finite strict-gap criterion, constructive and null cases, and SEP-Ω reduction | **Already established inside HLS for the declared RQ0/strong-SEP model.** The policy inclusion inequality itself is trivial; exact support criterion and scoped cases are more informative. | Do not relabel this as a new finding. A broader external claim needs direct comparison with dynamic workforce scheduling and decomposition literature. |
| **One candidate only:** “Which local structural conditions make a reachable routing/development inversion produce a root-optimal strict gap, rather than a reducible local inversion?” | **Extension potentially worth testing theoretically; not demonstrated original.** | Falsifiable target: characterize, in a stated finite MDP class, when the local Bellman preference `Δp·D* > ΔR` implies every root-optimal policy violates strong SEP, accounting for action-dependent resource depletion and optimal-policy support. The existing RQ0 note already shows reachability alone is insufficient. Needed: prove a primitive condition or give a sharper counterexample, map it to published dynamic workforce and MDP decomposition results, then show what scope remains. HLS evidence: exact RQ0 constructive/reducible worlds, S2b, G2, and S4/S7 diagnostics. Main risk: the result reduces to standard MDP policy inclusion/support logic or is already covered. **Abandon** if a focused literature check finds the same criterion, or if the only result is the already known set-inclusion inequality. Plausible within one year only as a tightly scoped theoretical paper, contingent on novelty review; not yet a GO for experimentation. |

No second candidate is recommended: a broad factorial on demand, learning, transfer, and resources would restate established dimensions without a differentiated estimand.

## 7. Recommendation

**REFRAME.** The question is scientifically important and HLS has unusually explicit internal distinctions between physical capability change, collective-capability change, future value, and decision relevance. But the core phenomenon—current work developing future productivity and integrated training/scheduling trading current output for future capacity—is already published. HLS also has exact, scoped RQ0 results, including reducible and strict cases relative to strong SEP. The current evidence does not establish that deliberate USE and DEVELOP require joint management, nor that HLS's formulation is novel.

The defensible next claim, if pursued, is a theorem-level characterization of strict value relative to a precisely named modular/separated policy class, extending rather than renaming the existing RQ0 result. The single candidate above has a clear abandonment test and could be completed within a year if a focused literature check supports a genuine gap. No experiment, code change, new scenario, or campaign is recommended by this grounding note. The PI should authorize that narrow theoretical question only after reviewing whether the additional novelty risk is acceptable.

## 8. References and evidence index

### Published work

1. Jin, H., Hewitt, M., & Thomas, B. W. (2015). Selection, grouping, and assignment policies with learning-by-doing and knowledge transfer. *Computers & Industrial Engineering, 79*, 175–187. [https://doi.org/10.1016/j.cie.2014.11.006](https://doi.org/10.1016/j.cie.2014.11.006).
2. Jin, H., Hewitt, M., & Thomas, B. W. (2018). Workforce grouping and assignment with learning-by-doing and knowledge transfer. *International Journal of Production Research, 56*(14), 4968–4982. [https://doi.org/10.1080/00207543.2018.1424366](https://doi.org/10.1080/00207543.2018.1424366).
3. Valeva, S., Hewitt, M., Thomas, B. W., & Brown, K. G. (2017). Balancing flexibility and inventory in workforce planning with learning. *International Journal of Production Economics, 183*, 194–207. [https://doi.org/10.1016/j.ijpe.2016.10.026](https://doi.org/10.1016/j.ijpe.2016.10.026).
4. Chen, X., Hewitt, M., & Thomas, B. W. (2018). An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers. *International Journal of Production Economics, 196*, 122–134. [https://doi.org/10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028).
5. Su, G., Zhong, H., & Zhang, J. (2025). Integrated training course planning and hierarchical multi-skilled employee scheduling in the workforce skill transformation context. *International Journal of Production Economics, 286*, 109642. [https://doi.org/10.1016/j.ijpe.2025.109642](https://doi.org/10.1016/j.ijpe.2025.109642).
6. Nembhard, D. A., & Bentefouet, F. (2012). Parallel system scheduling with general worker learning and forgetting. *International Journal of Production Economics, 139*(2), 533–542. [https://doi.org/10.1016/j.ijpe.2012.05.024](https://doi.org/10.1016/j.ijpe.2012.05.024).
7. Akbarzadeh, N., & Mahajan, A. (2022). Conditions for indexability of restless bandits and an O(K³) algorithm to compute Whittle index. *Advances in Applied Probability, 54*, 1164–1192. [https://doi.org/10.1017/apr.2021.61](https://doi.org/10.1017/apr.2021.61).

### HLS sources

- [HLS current scientific state](../HLS_CURRENT_STATE.md)
- [S4 Campaign 1 findings](../experiments/HLS_CAMPAIGN1_FINDINGS.md)
- [HLS Campaign 2: teaching × MIS-v2 × assignment](../experiments/HLS_CAMPAIGN2_FINDINGS.md)
- [Historical Campaign 2 results](../experiments/CAMPAIGN_2_RESULTS.md)
- [Campaign 3 META-VOC confirmatory results](../experiments/CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md)
- [HLS Dynamic Theoretical Foundation T4–T6](../theory/HLS_DYNAMIC_THEORY.md)
- [G2 dynamic ground truth](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md)
- [RQ0 routing integration boundaries](../theory/rq0_routing_integration_boundaries.md)
- [Mathematical analysis, 22 October 2026](HLS_MATHEMATICAL_ANALYSIS_2026-10-22.md)
- [Cumulative HLS execution plan](../engineering/HLS_LAB_EXECUTION_PLAN_2026-10-17.md)

## 9. Originality and feasibility assessment — 23 October 2026

This addendum completes the focused originality check. It supersedes the
provisional **REFRAME** recommendation above for the decision about an
immediate USE/DEVELOP publication candidate. The earlier reasoning remains
as dated context; no scientific result or historical artifact is changed.

### 9.1 Policy equivalence

Let `Π_J` be the joint policies mapping the information available at a decision
epoch to a feasible joint action `(u_t,d_t)`. Let `Π_S` be modular executions
whose USE and DEVELOP components can exchange messages and coordinate. Policies
are identified by the induced conditional distributions of physical actions at
every admissible history, rather than by their software architecture.

**THEOREM — unrestricted coordination equivalence.** Suppose: (i) both
modules have perfect recall of the same union of decision-relevant observations
and actions; (ii) they can communicate that history and any common random seed
without loss, delay, or cost before each action; (iii) they share decision
epochs, model, horizon, objective, and physical joint feasible-action set;
(iv) a coordinator or agreed protocol can select and execute any feasible
joint action; and (v) computation is sufficient to implement any policy in
`Π_J`. Then

\[
\boxed{\Pi_S=\Pi_J}
\]

in implementable behavior. For `Π_J ⊆ Π_S`, each module can reconstruct the
common history, evaluate the corresponding component of a selected joint
policy, and coordinate execution; a central coordinator can also compute the
whole action and send each module its component. For `Π_S ⊆ Π_J`, any
coordinated modular protocol induces a joint conditional action rule on the
same history and feasible set. Randomized joint rules require shared
randomness or communication of the random draw. Thus unrestricted separation
of internal roles does not reduce the attainable policy class. **This is a
representation equivalence, not an original HLS result.**

The theorem does not apply when “separated” means independent modules with
private information, no communication, incompatible update times, fixed
separate budgets, restricted action rights, a prescribed local objective, or
limited compute. Those are explicit restrictions on information or
implementable behavior; they must be part of `Π_S`, not inferred from module
labels. Different architectures can still have different computational
costs even when their behavior classes are equal.

### 9.2 Where a nonzero gap can come from

| Restriction or mechanism | Coupling type | Can it alone imply `V_J>V_S`? | Closest established theory / classification |
|---|---|---|---|
| Local incomplete information | Informational | It can, if local controllers cannot recover or signal the joint-relevant information; not if the joint policy has the same information restriction. | Decentralized team/control theory studies information structures and signaling. The common-information coordinator reformulation is equivalent to the decentralized problem, not a claim that decentralized implementation is costless. **KNOWN.** [Nayyar et al. (2013)](https://doi.org/10.1109/TAC.2013.2239000); Witsenhausen’s nonclassical information structure is a foundational example, not an HLS-specific result. |
| Limited communication | Informational / organizational | Yes, relative to a class with a specified channel, alphabet, delay, and cost; no universal gap follows from “distributed” alone. | Communication-constrained decentralized control and team decision theory. **KNOWN framework; direct application** to USE/DEVELOP would require an HLS channel and policy class. |
| Different decision frequencies | Temporal / organizational | Only if a module is constrained to hold or defer actions between updates; mere asynchronous implementation with lossless coordination need not reduce behavior. | Hierarchical/multirate and sampled-data control already formalize update constraints. **KNOWN framework; direct application** for a frozen update schedule. |
| Shared resources | Physical feasibility | It couples the joint feasible set, but does not by itself separate `Π_J` from `Π_S` when a common coordinator can enforce the same constraint. | Weakly coupled MDPs decompose independent subproblems through Lagrangian relaxation and provide bounds/heuristics; exactness requires additional conditions. **KNOWN.** [Bertsimas & Mišić (2016)](https://doi.org/10.1287/opre.2016.1531); [Ohlmann & Bean (2009)](https://doi.org/10.1016/j.ejor.2008.11.005). |
| USE-induced learning | Physical state transition | No, not with unrestricted equivalence: both classes can condition on the same transition. It can make present assignments intertemporally consequential. | Workforce scheduling with experience-based productivity and stochastic demand directly studies this effect. **KNOWN.** [Chen et al. (2018)](https://doi.org/10.1016/j.ijpe.2017.10.028). |
| Irreversible or delayed development | Physical / temporal | No, if both classes observe the same state and may plan over the same horizon; it can increase the value of continuation-aware decisions. | Standard multistage stochastic control and training/scheduling models. **KNOWN.** [Su et al. (2025)](https://doi.org/10.1016/j.ijpe.2025.109642). |
| Uncertain future capability | Physical uncertainty, and informational only if beliefs differ | No if both use the same observations/belief and uncertainty law; yes only if information or admissible memory differs. | POMDP/common-information methods and stochastic workforce planning. **KNOWN.** |
| Experience-dependent observation | Informational feedback coupled to USE | It can change the value of policies because decisions determine observations. It does not alone establish a gap between joint and unrestricted coordinated modules. | Partial-feedback online learning, feedback graphs, and multi-agent bandits study action-dependent observation/regret. **KNOWN.** [Alon et al. (2017)](https://doi.org/10.1137/140989455); [Madhushani & Leonard (2020)](https://arxiv.org/abs/2004.03793). |

These categories interact, but are not synonyms. “Physical coupling” concerns
the reward, transition, or feasible set. “Informational coupling” concerns
which observations and histories affect future decisions. “Organizational
coupling” concerns the policy class and authority/communication protocol.
“Temporal coupling” concerns when decisions take effect and how long their
consequences persist. Physical learning may create a planning problem without
creating an architectural separation loss.

### 9.3 Analytic statements and value gap

- **THEOREM (equivalence):** under the five assumptions in §9.1, `Π_S=Π_J`
  and therefore `V_J=V_S` for every common physical instance.
- **THEOREM (policy-class criterion):** for finite problems with attained
  optima, `V_J=V_S` iff at least one joint-optimal policy is implementable in
  `Π_S`; strictness holds iff no joint optimum is. This is the general
  policy-class fact already instantiated for HLS strong-SEP in the
  [RQ0 analysis](../theory/rq0_routing_integration_boundaries.md). It is not
  a primitive-parameter characterization.
- **PROPOSITION (separability):** the product-state, product-action,
  additive-reward and conditionally independent-transition hypotheses in §5
  suffice for Bellman value decomposition. They are sufficient, not necessary.
- **COUNTEREXAMPLE (HLS, existing):** G2 D2 gives strict value of a
  continuation-aware assignment over immediate-greedy assignment through
  use-induced learning. It does not compare against unrestricted coordinated
  USE/DEVELOP modules and is not new relative to workforce scheduling.
- **EMPIRICAL OBSERVATION (HLS):** S4 teaching × MIS-v2 interactions vary by
  initial competence and demand under the declared interventions and P0
  continuation. This is not a theorem about `V_J−V_S`.
- **CONJECTURE (not retained as a claim):** that any one of learning rate,
  training cost, horizon, or resource scarcity predicts a strict gap absent a
  fixed separated policy interface. The current evidence does not establish
  such a universal one-factor rule.

For a fixed separated policy `π_S`, the Bellman-residual identity in §5
expresses its loss as accumulated missed continuation value. A generic bound
requires a reward scale and finite horizon; without those, scaling rewards
alone makes `Δ` arbitrarily large at fixed transition dynamics. A more
interpretable **standard simulation bound** is possible only relative to a
specified separable surrogate `M_0`: if the original and surrogate have the
same state/action/information semantics, per-period rewards differ uniformly
by at most `ε_r`, transition kernels by total variation at most `ε_P`, rewards
lie in `[0,R]`, horizon is `H`, and `M_0` has equivalent joint/separated
classes, then for any fixed policy

\[
E_H=\sum_{t=0}^{H-1}\gamma^t\left[\epsilon_r+
\gamma\epsilon_P R(H-t-1)\right]
\]

is a bound on the absolute value change (a conservative span bound, with no
terminal discrepancy). Using an `M_0`-optimal policy that is implementable in
the original separated class gives `0≤Δ≤2E_H`. This is a direct simulation
lemma, not a novel USE/DEVELOP theorem; it is useful only if the surrogate and
its coupling errors have independently justified meanings. It does not supply
a general bound in terms of a learning rate or “degree of coupling” alone.

### 9.4 Originality decision

| Candidate claim | Classification | Finding |
|---|---|---|
| Unrestricted modular USE/DEVELOP can reproduce a joint policy | **KNOWN / immediate representation result** | Proven in §9.1; not a publication contribution. |
| Current work can improve future productivity and integrated training/assignment can outperform myopic/sequential decisions | **KNOWN** | Already studied in technician scheduling, workforce learning, transfer, and integrated training/scheduling papers cited above. HLS's finite examples are scoped replications/illustrations. |
| Shared constraints can couple MDP subproblems and decomposition can bound/approximate the global value | **KNOWN** | Weakly coupled MDP and Lagrangian decomposition literature directly covers this structure. |
| A specific HLS restriction yields a family-wide strict `Δ>0` theorem or a useful structural bound | **UNSUPPORTED as an original contribution today** | No candidate was found that is both nontrivial and not a direct application of team control, MDP decomposition, or workforce scheduling. Existing HLS exact criteria are scoped to strong-SEP and have already been documented. |
| S3b-E1 insight: decision-dependent observations can make global estimation error misrepresent assignment quality | **POTENTIAL EXTENSION, not established as novel** | This is the strongest HLS alternative for further scientific positioning because it has paired shared-observation and closed-loop evidence. Structured-feedback and multi-agent bandit literatures are close; the closed-loop contrasts were inconclusive. No publication-level novelty or causal claim is yet justified. |

**Decision: NO-GO for USE/DEVELOP as the immediate standalone publication
candidate.** Its broad question is important, but unrestricted equivalence is
straightforward, common restrictions have established formal treatments, and
the HLS-specific exact policy-class results are scoped and not yet a
distinctive family-level contribution. Retain its models, null/positive
controls, and T4–T6/RQ0 theory as HLS foundations; do not open another
USE/DEVELOP campaign or continue reformulating the same broad hypothesis.

### 9.5 Single HLS priority and publication gate

**Priority alternative: S3b-E1 — organization-dependent observability and
decision-relevant learning.** It is preferred over Campaign 2 (teaching/MIS
interactions already closely represented in workforce learning literature)
and META-VOC/Campaign 3 (adaptive computation selection is a crowded adjacent
problem; its primary fraction was selected after development and held-out-team
production contrasts were inconclusive). S3b-E1 already contains 240 UCB1 vs
SW-UCB runs and 360 diagnostic FULL/WINDOW runs, with an observation-shared
control that isolates memory treatment more cleanly and a closed-loop control
that records the organizational feedback problem. Its strongest finding is
bounded: under one preselected rare-change/high-feedback shared-observation
condition, WINDOW reduced regret by 74.59 (95% CI [−89.60, −59.58]); other
shared cells were null/nonconclusive, and all closed-loop paired regret
intervals included zero. See the [S3b result record](../../results/experiments/hls_s3b_memory_replay_diagnostic/results.json)
and [canonical state](../HLS_CURRENT_STATE.md).

This is a **priority for further originality assessment, not authorization to
run a campaign**. A publication claim would need a focused comparison against
action-dependent/structured-feedback bandits, a precise estimand separating
memory from observation policy, complete per-period action/observation traces,
and a novel theorem or an independently defensible result in the closed-loop
regime. The present evidence does not satisfy that gate. If literature review
shows the same controlled-memory/observation feedback distinction is already
covered and the existing data cannot support an identifiable extension,
abandon S3b as the immediate publication candidate too; do not reopen
USE/DEVELOP by default.

### 9.6 Evidence needed and abandonment criteria

Before asserting publication potential for any candidate, require all of:

1. A formal policy-class and information contract with identical physical
   actions, resource constraints, and observability for compared mechanisms.
2. A claim not implied by policy inclusion, Bellman recursion, common
   information, standard decomposition, or an existing workforce-learning
   result.
3. An analytical proof or a prespecified, causally interpretable empirical
   contrast with adequate independent units and preserved decision/feedback
   traces.
4. A literature comparison against the exact mathematical structure, not
   keyword differences.
5. An external-validity statement limited to the studied model/domain.

Abandon the candidate if the closest papers already prove its central result,
if the remaining statement is only `V_J≥V_S` by class inclusion, if strictness
depends on an artificially weak separated policy, or if the existing data
cannot identify the proposed contrast. No new experiment is authorized by
this assessment.

### 9.7 Additional references consulted

8. Nayyar, A., Mahajan, A., & Teneketzis, D. (2013). Decentralized stochastic
   control with partial history sharing: A common information approach.
   *IEEE Transactions on Automatic Control, 58*(7), 1644–1658.
   [https://doi.org/10.1109/TAC.2013.2239000](https://doi.org/10.1109/TAC.2013.2239000).
9. Witsenhausen, H. S. (1971). Separation of estimation and control for
   discrete time systems. *Proceedings of the IEEE, 59*, 1557–1566.
   [https://doi.org/10.1109/PROC.1971.8488](https://doi.org/10.1109/PROC.1971.8488).
10. Bertsimas, D., & Mišić, V. V. (2016). Decomposable Markov decision
    processes: A fluid optimization approach. *Operations Research, 64*(6),
    1537–1555. [https://doi.org/10.1287/opre.2016.1531](https://doi.org/10.1287/opre.2016.1531).
11. Ohlmann, J. W., & Bean, J. C. (2009). Resource-constrained management of
    heterogeneous assets with stochastic deterioration. *European Journal of
    Operational Research, 199*(1), 198–208.
    [https://doi.org/10.1016/j.ejor.2008.11.005](https://doi.org/10.1016/j.ejor.2008.11.005).
12. Alon, N., Cesa-Bianchi, N., Gentile, C., Mannor, S., Mansour, Y., & Shamir,
    O. (2017). Nonstochastic multi-armed bandits with graph-structured
    feedback. *SIAM Journal on Computing, 46*(6), 1785–1826.
