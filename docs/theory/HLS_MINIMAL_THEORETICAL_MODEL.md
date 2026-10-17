# HLS Minimal Theoretical Model

**Status:** analytical reference model; no simulator changes or experiments were made for this document. The propositions below are scoped to their stated assumptions. They do not establish a new general theory of assignment, training, or dynamic programming.

## 1. Purpose and scope

This document gives a domain-independent finite-horizon model for allocating heterogeneous agents across concurrent tasks while competence changes through work and directed teaching. It includes partial organizational information and exogenous demand. Its purpose is to make conditional predictions precise and to map them onto the current HLS implementation. It does not define Campaign 3.

The model keeps four objects distinct: competence is current productive capability; learning ability governs how capability changes after exposure; teaching ability governs the effect of a directed lesson; and organizational knowledge is a belief or estimate used to choose actions. Demand is generated independently of organizational actions.

## 2. General model

Let agents be \(i\in\mathcal I=\{1,\ldots,n\}\), skills \(k\in\mathcal K=\{1,\ldots,K\}\), and periods \(t=0,\ldots,T-1\). The latent environmental state is \(z_t\), pending work is a multiset \(Q_t\), and each task \(j\in Q_t\) has requirements \(r_{jk}\), a deadline or age, and a task-specific outcome map. New demand \(\xi_t\) is drawn from \(P(\xi_t\mid z_t)\), while \(z_{t+1}\sim P(z_{t+1}\mid z_t)\). Neither transition depends on the organization, its actions, or its competence state. The queue evolves as \(Q_{t+1}=(Q_t\setminus C_t)\cup A(\xi_t)\), where \(C_t\) is the set of tasks completed by the joint action and \(A(\xi_t)\) is the batch of new arrivals; this permits uncompleted tasks to remain pending.

The real competence state is \(c_t=(c_{ik,t})\in[0,1]^{n\times K}\). Learning parameters \(\ell_{ik}\geq0\) describe agent-specific acquisition from experience; they are not competence. Directed teaching efficacy \(\tau_{uvk}\in[0,1]\), for instructor \(u\), learner \(v\ne u\), and skill \(k\), is a separate parameter; it is neither competence nor the learner's learning ability. These parameters may be known or latent. A general model may also include decay, forgetting, prerequisites, or transfer across skills, but none is required for the minimum model.

### 2.1 Actions, parallel work, and shared resources

At time \(t\), a joint action contains productive allocations \(x_{ijkt}\geq0\) (effort by agent \(i\) on task \(j\), skill \(k\)), optional self-directed learning effort \(u_{ik,t}\geq0\), and directed teaching effort \(q_{uvk,t}\geq0\). The no-teaching decision is \(q=0\). Binary assignment variables may be added when a task requires an agent's presence or when task splits are disallowed. Several tasks can be pending and worked on in the same period; an agent may work on a task while acquiring experience from it. Agents are not assumed idle. Whether teaching and production can overlap is an explicit compatibility rule, not an implicit assumption.

For example, with capacity \(h_{it}\) per agent and shared budget \(B_t\), feasible actions satisfy

\[
\sum_{j,k}x_{ijkt}+\sum_k u_{ik,t}
+\sum_{v\ne i,k}q_{ivk,t}+\sum_{u\ne i,k}q_{uik,t}\le h_{it}\quad(i\in\mathcal I),
\]

\[
\sum_{i,j,k}a^P_{ijkt}x_{ijkt}
+\sum_{i,k}a^L_{ik}u_{ik,t}
+\sum_{u\ne v,k}a^T_{uvk}q_{uvk,t}\le B_t.
\]

The coefficients \(a\) convert effort into the declared shared resource units. If a lesson consumes both instructor and learner time, that is represented in both individual capacity constraints; its shared-budget charge is defined once according to the resource accounting convention. Compatibility, exclusivity, qualifications, and task completion rules further restrict the feasible set \(\mathcal A(Q_t,h_t,B_t)\). Unused resources are allowed and recorded.

For a simple additive production technology,

\[
Y_{jk,t}=\sum_i x_{ijkt}c_{ik,t},\qquad
R_{j,t}=g_j(Y_{j,t},r_j),
\]

where \(g_j\) evaluates functional quality or task completion. A domain may replace the additive map with interactions, reliability, or complementarities when evidence and the scientific question require them. Those changes are not implied by heterogeneous skills. If output and resource use have no common value scale, retain a constrained or multi-objective problem, such as maximizing expected functional output subject to \(B_t\), rather than subtracting an arbitrary resource penalty.

### 2.2 Competence transitions

Let \(e_{ik,t}=\sum_jx_{ijkt}\). A minimal individual development transition allowing both work experience and optional self-study is

\[
L_{ik}(c,e,u;\ell,\kappa)=1-(1-c)\exp(-\ell_{ik}e-\kappa_{ik}u),
\]

where \(\ell_{ik}\geq0\) and \(\kappa_{ik}\geq0\) are agent-skill-specific acquisition rates for work and self-study. Setting \(u=0\) gives the MIS-v2 form; \(\ell_{ik}=0\) removes learning-by-doing, and \(\kappa_{ik}=0\) removes self-study. The transition is increasing in either exposure when its rate is positive, bounded by one, and has diminishing remaining-gap increments. Self-study is a generic decision variable and is not implemented in the current integrated laboratory.

For a directed lesson, write \(T(c',q;\tau)\) for the learner's post-lesson competence. A minimal remaining-gap form is

\[
T(c',q;\tau)=c'+\tau q(1-c'),\qquad 0\leq\tau q\leq1.
\]

The instructor's skill changes only if a separate mechanism specifies it. A period transition can compose work, self-study, and teaching, for example \(c_{t+1}=T(L(c_t,e_t,u_t;\ell,\kappa),q_t;\tau)\) for learners after production. Reversing this order generally changes the result; the order is part of the model contract. Learning by doing, optional self-study, and teaching are distinct transitions even if they all close a competence gap.

### 2.3 Observations and organizational knowledge

The organization does not act on the private state \((c_t,\ell,\tau,z_t)\) unless the information regime explicitly makes a component observable. It receives observations \(o_{t+1}\) generated from outcomes, effort, task context, and a specified noise model. Its information is the history \(\mathcal F_t^O=\sigma(o_{0:t},\text{public actions and demand data})\), summarized by a belief \(b_t\) over the unobserved state. Bayesian updating is one option; a point estimate with uncertainty is another, but the update must use only observations available under the contract.

The policy is measurable with respect to this information: \(a_t=\pi_t(b_t,Q_t,h_t,B_t)\). The belief transition follows Bayes' rule (or the declared estimator) after observing the next public data. Environment state and competence estimates remain separate: a demand belief concerns \(z_t\), while a competence belief concerns \(c_t\) and possibly \(\ell,\tau\).

### 2.4 Objective and dynamic program

When task outcomes are commensurable, let \(r_t(s_t,Q_t,a_t)\) denote the declared period reward, and let \(\beta\in(0,1]\) be the discount factor. A constrained objective is

\[
\max_{\pi}\;\mathbb E^\pi\!\left[\sum_{t=0}^{T-1}\beta^t r_t+\beta^T\Phi(s_T,Q_T)\right]
\quad\text{subject to the shared resource and feasibility constraints.}
\]

If productivity, quality, and resource cost are not in a justified common unit, report a vector of outcomes or optimize one subject to constraints on the others. A scalarization requires an explicit exchange rate; it is not supplied by this model.

For a partially observed system, augment the state with public queues/resources and the organizational belief. The finite-horizon Bellman recursion is

\[
V_t(b,Q,h,B)=\max_{a\in\mathcal A(Q,h,B)}\left\{
\mathbb E_{s\sim b}[r_t(s,Q,a)]
+\beta\mathbb E[V_{t+1}(b',Q',h',B')\mid b,Q,h,B,a]
\right\},
\]

with declared terminal value \(V_T=\Phi\). The transition of environmental state and new demand is exogenous conditional on \(z_t\); the competence transition depends on production and teaching actions. This formulation supports multiple pending tasks, parallel assignments, partial information, and finite resource competition without prescribing an optimizer.

## 3. Conditional results

### Proposition 1 — When the currently best agent is optimal

Consider two feasible alternatives that differ only in assigning one current task to agent \(H\) or agent \(L\). Let \(H\) have the larger immediate reward, \(r_H\geq r_L\). Let \(W_H\) and \(W_L\) be the continuation values after the respective assignments, discounted to the current period and including resulting competence changes and all later feasible decisions. Then assigning \(H\) is optimal if and only if

\[
r_H-r_L\;\geq\; W_L-W_H.
\]

**Proof.** The two action values are \(Q_H=r_H+W_H\) and \(Q_L=r_L+W_L\). Thus \(Q_H\geq Q_L\) exactly when the displayed inequality holds. If both assignments induce the same continuation state/value, then \(W_L=W_H\), so the immediate best agent is optimal. More generally, if the less-skilled assignment has no larger future value, it is optimal to choose \(H\). \(\square\)

This is a Bellman comparison identity, not a new general theorem. It says why a greedy assignment can be justified when there is no action-induced learning, or when learning cannot compensate for the immediate loss. It also identifies the missing comparison needed when future competence matters.

### Proposition 2 — A less competent agent can be preferable

Suppose current reward is \(r(c_i)\), increasing in the assigned agent's skill \(c_i\), and the assignment creates exposure \(e\). Under MIS-v2, let the post-work skill be \(c_i^+=c_i+\eta_i(e)(1-c_i)\), where \(\eta_i(e)=1-\exp(-\ell_i e)\). Suppose one later task has continuation value \(A+w c_i^+\), with \(w\geq0\), for the agent receiving this exposure, and all other continuation terms are common across the two choices. Assign the currently weaker agent \(L\) exactly when

\[
\beta w\left[c_L+\eta_L(e)(1-c_L)-c_H-\eta_H(e)(1-c_H)\right]
> r(c_H)-r(c_L).
\]

At equality both choices tie. This follows by comparing \(r(c_i)+\beta w c_i^+\) for the two assignments. The left side includes both the learner's lower starting skill and the skill increment; the increment must compensate for that deficit and the current reward gap. With no LBD, \(c_L<c_H\) and increasing \(r\), the condition cannot hold.

### Proposition 3 — Teaching versus learning-by-doing

Compare a feasible production-only action \(D\) and a teaching action \(T\), under the same continuation rule. Let their immediate rewards be \(r_D,r_T\), and their next competence states be \(c_D',c_T'\). If \(V\) is the continuation value from the next period, teaching is strictly preferred exactly when

\[
\beta\mathbb E[V(c_T')-V(c_D')]>r_D-r_T,
\]

and any resource costs not already reflected in feasibility or reward must be included only through an explicitly justified common-unit valuation. Under locally linear continuation \(V(c)=A+wc\), one target skill, and increments \(\delta_T,\delta_D\), this reduces to \(\beta w(\delta_T-\delta_D)>r_D-r_T\).

The equation gives conditional break-even, not a blanket ranking. Strict inequality makes teaching uniquely preferable; equality is a tie. Teaching is more attractive when it produces a sufficiently valuable skill increase, the horizon leaves time to use it, and the work it displaces has low value. If the resources do not permit both actions, the displaced production is part of \(r_D-r_T\) or a separate constrained outcome; do not count it again as an arbitrary penalty.

### Proposition 4 — Same-skill learning can substitute; access to work can create complementarity

First suppose a learner starts at \(c<1\), and one period of work closes fraction \(d\in[0,1]\) of the remaining gap while one lesson closes fraction \(q\in[0,1]\). With both mechanisms applied sequentially,

\[
c_{11}=1-(1-c)(1-d)(1-q),\quad c_{10}=1-(1-c)(1-d),\quad
c_{01}=1-(1-c)(1-q),\quad c_{00}=c.
\]

The competence-scale difference-in-differences is

\[
c_{11}-c_{10}-c_{01}+c_{00}=-(1-c)dq\leq0.
\]

Thus the two mechanisms are substitutive on this same-skill, fixed-exposure, linear-terminal-value scale: each uses some of the same remaining competence gap. If terminal value is affine in competence and all assignments/exposures and resource consumption are held fixed (or resource cost is additive across the two toggles), its interaction has the same nonpositive sign. This is a consequence of the assumed saturating transition, not an empirical universal.

Positive interaction is possible when teaching changes access to future work and work creates further experience. A minimal three-stage construction demonstrates the possibility. At stage 0, teaching raises learner \(L\)'s skill from \(x\) to \(x+u\), at a fixed immediate opportunity cost, while a reserve agent has skill \(r\), with \(x<r<x+u\). At stage 1, a task is assigned to the higher-skilled agent; only \(L\) can acquire a positive LBD increment \(d\) from this task. At stage 2, a task can use \(L\)'s resulting skill, with reward equal to that skill; without teaching, the reserve skill \(r\) remains the best available. Let teaching and LBD toggles be \(T,D\in\{0,1\}\). The teaching toggle changes stage-1 assignment from the reserve to \(L\); LBD therefore increases \(L\)'s stage-2 skill only in cell \((T,D)=(1,1)\). The stage-2 difference-in-differences is \(\beta^2 d>0\) (if the teaching gain leaves enough headroom and the learner remains the stage-2 best agent). The fixed teaching opportunity cost cancels in the interaction. This proves possibility under the stated threshold assignment and payoff assumptions, not a general positive interaction result.

### Proposition 5 — Greedy assignment can concentrate learning opportunities

Consider one repeatedly arriving task, two agents with scalar skills \(c_H>c_L\), equal immediate productivity per unit skill, a fixed tie-break, and a greedy rule that always assigns the task to the currently more productive agent. Only the assigned agent receives MIS-style exposure; the other receives none. If exposure updates skill by \(c_i'=1-(1-c_i)e^{-\ell_i e}\) with \(\ell_i\geq0\), then \(c_H'\geq c_H>c_L\). By induction, the same agent is selected every period and the other agent's skill remains fixed. If \(\ell_H e>0\), the selected skill converges to one as repetitions grow.

**Proof.** The transition is monotone and never lowers skill. Since the initial gap is strict and the unassigned agent does not change, the ranking remains strict after every update. The greedy rule therefore repeats the assignment. Iterating the exponential transition gives \(c_H^{(m)}=1-(1-c_H^{(0)})e^{-m\ell_H e}\to1\) when \(\ell_H e>0\). \(\square\)

This is an absorbing concentration result for a deliberately narrow repeated-task model. Rotating demand, exploration, forgetting, multi-skill requirements, or a policy that values future skill can break it. It is not a claim that concentration is generally optimal.

## 4. Falsifiable predictions

The model yields tests with explicit conditions, rather than unconditional expectations:

1. When competence is fixed or the continuation value is assignment-invariant, a policy maximizing immediate reward over the same feasible set selects a current best-reward assignment (Proposition 1).
2. With positive LBD and a later task that values the target skill, a weaker agent can be selected when its discounted incremental continuation value exceeds its immediate reward gap (Proposition 2). Varying that gap across the derived threshold should switch the optimal assignment.
3. Under fixed exposure and diminishing-gap learning, teaching and LBD on the same skill have a nonpositive competence-scale interaction. A positive performance interaction requires a nonlinearity such as crossing an assignment/eligibility threshold, or another explicit state-dependent pathway (Proposition 4).
4. In a recurring single-task setting with strict skill ranking and no rotation, greedy allocation concentrates exposure as stated in Proposition 5; adding rotation or a demand shift can end that pattern.
5. An action can improve gross CES or functional success without improving the other measure; resource use can increase without reducing gross CES. These are separate outputs in the current HLS contracts and should remain separate observables.

Predictions 1–4 are model implications under their assumptions. They are not claims about real organizations. Prediction 5 is also consistent with the Campaign 1/2 findings and existing reward contract; it does not identify a welfare ranking.

## 5. Mapping to HLS and known limits

| Theoretical quantity | Existing implementation | Missing or limited capability | Evidence/intervention needed to test the quantity |
| --- | --- | --- | --- |
| Heterogeneous \(c_{ik}\), productive allocation \(x\), additive \(Y_k\) | `src/hls/discover_v0.py:production_inputs`; `src/hls/hls_lab_v1.py` problem/action contracts; integrated runner | Fixed three-agent/two-skill production kernel and discrete action catalogue; simultaneous pending-task scheduling is not in the integrated episode contract | Use the existing world to test its stated allocation set; a multiple-pending-task claim requires a task queue/action extension and tests. |
| LBD parameter \(\ell_{ik}\), exposure transition | `src/hls/discover_develop_v2.py:capability_after_exposure`, `mis_v2_transition`; `src/hls/hls_lab_dynamic.py:advance_team` | MIS parameters are configured, not inferred as individual learning ability; experience is tied to assigned exposure in a small fixed team | Matched LI ON/OFF and agent-skill exposure contrasts; distinguish real transition from estimated update. |
| Directed \(\tau_{uvk}\), lesson \(q\), direct transfer | `src/hls/hls_lab_v1_integrated.py:TeachingEfficacy`, `TeachingEvent`, integrated teaching transition | Relation efficacy is private fixed truth; one lesson maximum per period; the implementation's three-agent/two-skill shape is not generic | Toggle a specified relation/skill lesson while logging direct gain separately from MIS. |
| Pending set \(Q_t\), concurrent assignments and shared capacities | Integrated action validation combines production and one teaching event under team/budget/individual caps | No general queue of multiple simultaneous pending tasks; catalog discreteness can strand resources | Multiple-task scheduling needs explicit queue arrivals, deadlines, assignment variables and a shared-capacity acceptance test. |
| Exogenous \(z_t,\xi_t\) | `src/hls/hls_lab_v1_environment.py:generate_environment_trajectory`, built from existing C5 demand and dynamic problem emission | The current generator is a small finite family, not a validated empirical demand model | Verify the frozen trajectory is policy-independent; test recurring, shifted and novel problem structures separately. |
| Private state vs organizational information \(b_t\) | `IntegratedDecisionView`; competence posterior in `hls_lab_dynamic.py`; `OrganizationMemory` stores noisy efficacy observations | Competence and efficacy estimates are elementary; available observation semantics and missingness constrain identification | Controlled observation perturbations that cross actual decision boundaries; preserve no-leak tests. |
| Reward, continuation \(W\), resource constraints | `P0ProductionOnly` uses success/deficit/margin/effort ranking; integrated runner reports gross CES and resource use | P0 does not maximize CES or optimize long-horizon value; there is no general scalar net-value objective | Either compare under the actual P0 objective or define/justify a common-unit objective before optimality claims. |

Historical results reinforce these boundaries. Campaign 1 found mixed conditional teaching effects and a cost of discrete production displacement; its 64 counterfactuals are conditional on a continuation policy. Campaign 2 found interactions \(I_R=-1.092473,+1.561953,+0.339151\) in scenarios A/B/C respectively, with the positive B pathway consistent with teaching opening later target-skill assignments and LBD experience. The analysis explicitly did not identify assignment mediation. The sensitivity audit found seed-varying observation/estimate paths but identical CES paths within every Campaign 2 scenario/condition; outcome sensitivity requires perturbations that cross consequential decision or reward boundaries. See [Campaign 1 findings](../experiments/HLS_CAMPAIGN1_FINDINGS.md), [Campaign 2 findings](../experiments/HLS_CAMPAIGN2_FINDINGS.md), and [the sensitivity audit](../experiments/HLS_EXPERIMENTAL_SENSITIVITY_AUDIT.md).

The sensitivity audit also bounds what the current instrument can support: production is additive; its action catalogue is discrete and can leave shared capacity unused; CES is gross output and resource use is separate; and P0 ranks functional success, deficit, margin, then effort rather than maximizing CES. Observation noise changes estimates but not realized production directly, and the published Campaign 2 seeds do not vary demand. In that design, estimates sometimes changed without changing outcome-relevant assignments or CES. These are model and design limits, not evidence that uncertainty or noise is irrelevant in general. The full repository suite has 13 known historical provenance/integrity failures; the laboratory remains PARTIAL.

### Relationship to prior HLS theory

G1 supplies static capability/organization distinctions under fixed competence. G2 supplies minimal dynamic competence-development and organization-development coupling cases. MIS/G0 provides the individual experience transition and its exact synthetic decision setting. G3/G3-H analyzes assignment and future development value in small exact settings; RQ0 studies when separated routing/development decisions reproduce joint decisions within its specified problem. The canonical sources are [G1](HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md), [G2](HLS_G2_DYNAMIC_GROUND_TRUTH.md), [T4–T6](HLS_DYNAMIC_THEORY.md), [G3](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), and [RQ0](rq0_routing_integration_boundaries.md). Those works establish important scoped pieces; they do not make the present model a new theory. In particular, the Bellman recursion, finite-horizon control under partial information, diminishing-gap learning, and allocation-induced learning concentration are standard model structures. This document assembles them as a common HLS reference notation and derives the conditional inequalities above.

## 6. Literature and novelty boundary

- Arrow, K. J. (1962). “The Economic Implications of Learning by Doing.” *Review of Economic Studies*, 29(3), 155–173. [DOI: 10.2307/2295952](https://doi.org/10.2307/2295952). Foundational account of experience-dependent productivity and knowledge spillovers; it is not the finite-team assignment model here.
- Nembhard, D. A., & Bentefouet, F. (2015). “Selection, grouping, and assignment policies with learning-by-doing and knowledge transfer.” *Computers & Industrial Engineering*, 79, 175–187. [DOI: 10.1016/j.cie.2014.11.006](https://doi.org/10.1016/j.cie.2014.11.006). Directly relevant prior work combines workforce selection/grouping/assignment with learning-by-doing and knowledge transfer.
- Jin, H., Hewitt, M., & Thomas, B. W. (2018). “Workforce grouping and assignment with learning-by-doing and knowledge transfer.” *International Journal of Production Research*, 56(14), 4968–4982. [DOI: 10.1080/00207543.2018.1424366](https://doi.org/10.1080/00207543.2018.1424366). Considers learning through job performance and through observing/interacting with co-located colleagues.
- Baccara, M., Lee, S. M., & Yariv, L. (2023). “Task allocation and on-the-job training.” *Journal of Economic Theory*, 207, Article 105587. [DOI: 10.1016/j.jet.2022.105587](https://doi.org/10.1016/j.jet.2022.105587). Studies dynamic assignment as expertise evolves endogenously through training.

These references establish that assignment, experience-based learning, knowledge transfer, and dynamic on-the-job training already have substantial antecedents. The present synthesis makes no novelty claim. Any future contribution involving unknown, relation-specific teaching efficacy under uncertain demand would require a focused literature review and comparison of information structures, training technology, decisions, and objectives—not merely a different notation.

## 7. Open questions

1. Which real application supports the proposed distinction between effort, productive output, teaching outcome, and shared resource units, and what outcome metric is externally defensible?
2. Does teaching efficacy vary by instructor–learner–skill in an empirically meaningful way, and what observations identify it without leakage?
3. Under what technologies can peer interaction change a learner's access to productive work, rather than simply add a second learning transition?
4. When several tasks are pending, how should quality, deadlines, fairness, and competence development enter the organization's objective and constraints?
5. Which of the derived threshold predictions remain useful with noisy learning, uncertain demand, endogenous queues, and approximate policies?
6. Do the G1/G2/G3-H/RQ0 constructs reduce the general belief-state model to informative exact special cases, or do additional state variables materially change the questions?

The immediate theoretical conclusion is modest: short-horizon assignment and development decisions are governed by the current reward gap versus the continuation-value difference. Teaching and experience are substitutive under a fixed, same-skill remaining-gap law, but can interact positively when teaching changes later productive exposure. Whether that pathway is important or novel is open.
