# HLS — Baccara–Lee–Yariv / Chen–Hewitt–Thomas / RQ0: formal mathematical comparison

**Date:** 19 October 2026
**Scope:** theoretical and bibliographic analysis only; no code, simulations, or changes to canonical scientific claims.
**Evidence labels:** **FACT** = directly stated in an inspected source or canonical HLS proof; **INFERENCE** = implication of those facts; **HYPOTHESIS** = unresolved proposition; **PROPOSAL** = recommended next work.

> **Source update — 19 October 2026:** The complete 13-page published CHT18 article has now been checked directly. Its full equation-level reconstruction, computational design, strong-SEP analysis and limitations are in the [full-text mathematical audit](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). That audit supersedes the provisional CHT statements in this report. The BLY analysis is unchanged.

## 1. Executive mathematical findings

1. **FACT — Baccara, Lee and Yariv (BLY) study dynamic assignment with endogenous training in a stationary queueing environment.** Client arrivals are Poisson; a junior/senior allocation share affects both senior-queue congestion and the rate at which juniors are trained into senior service. Their central planner is compared with clients' discretionary equilibrium, not with HLS strong-SEP. The key centralization result (Corollary 2, pp. 24–25) follows from congestion and foregone-training externalities. It is not a theorem that joint HLS allocation/development beats a strong separated policy.

2. **FACT — CHT study a finite-horizon stochastic technician-scheduling MDP.** Daily requests are assigned to heterogeneous technicians under per-day service-time capacity; task-specific experience increments deterministically with assignment and reduces service time under Eq. (1). They minimize expected cumulative service time (printed pp. 124–125, Eqs. (1)–(7)). ADPBF is compared with the rolling one-day-lookahead ADPOL (pp. 126–127, Eqs. (11)–(15)).

3. **FACT — Neither published comparison is the HLS strong-SEP comparison.** BLY compare a planner with discretionary client equilibrium. CHT compare two dynamic scheduling methods, ADPBF and ADPOL; ADPOL includes a forecast next-day cost and is not a fixed assignment or purely immediate-greedy rule. Neither paper reports the globally optimized immediate-greedy/conditional-development policy-class value required by canonical strong-SEP. See the full-text audit, §§4 and 7.

4. **FACT — the HLS policy-class inclusion result is a generic set-inclusion theorem under the stated common-world contract.** It does not establish strict superiority. Strictness in the finite exact formalization is equivalent to every HLS-optimal policy violating strong-SEP on its own positive-probability support. This is proven in `docs/theory/rq0_routing_integration_boundaries.md`, Theorems 1–2. It is not a result established by BLY or CHT under equivalent policy classes.

5. **INFERENCE —** CHT is structurally close to assignment-induced task-specific experience and finite-horizon continuation in HLS. Its inverse service-time curve maps to a restricted Nembhard Direct curve with explicit parameters, but CHT's indivisible assignment, service-time capacity and cost semantics differ from the existing N×K runner. This is a broad controlled-process embedding, not an executable exact reproduction claim.

6. **PROPOSAL —** before any reproduction campaign, compare the exact CHT Bellman optimum with the globally optimized CHT strong-SEP restriction on a small exact instance class. ADPBF–ADPOL does not establish the RQ0 strict-gap condition. No experiment is authorized by this report.

## 2. Source verification and limitations

### Baccara–Lee–Yariv

The inspected primary source is the authors' 44-page accepted manuscript, *Task Allocation and On-the-job Training*, dated 24 November 2022, available at [lyariv.com/papers/TaskAllocation.pdf](https://www.lyariv.com/papers/TaskAllocation.pdf). It is the full manuscript associated with the 2023 *Journal of Economic Theory* article, volume 207, article 105587, DOI [10.1016/j.jet.2022.105587](https://doi.org/10.1016/j.jet.2022.105587). The final journal pagination may differ; page citations below refer to the manuscript PDF. Its online appendix is included in that PDF (appendix begins after the main conclusion); the manuscript itself refers to an Online Appendix for some queueing derivations.

The model and theorems cited below were read in the full manuscript: §§2–3, pp. 6–16; perfect-monitoring Proposition 1, manuscript pp. 12–13; limited-monitoring Proposition 2, pp. 14–15; Proposition 3, pp. 16–17; monitoring results, §§5–6, pp. 20–25; conclusions, §7, pp. 25–26. The relevant queueing steady-state definitions and derivations are in Lemmas 1–3 and equations (2)–(11). No computational experiment or reported sample estimate is used as evidence for BLY's analytical claims.

### Chen–Hewitt–Thomas

The bibliographic record is in the master file under key `chenhewitthomas2018adptechnician`, with DOI [10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028), *International Journal of Production Economics* 196 (2018), 122–134. The complete 13-page article supplied as `~/Downloads/1-s2.0-S0925527317303432-main.pdf` is locally stored at [`docs/literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf`](../literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf). Embedded title, author, DOI and issue/page metadata match the citation; SHA-256 is `58320e719bf4d54d76ecb6ae01ba94dc3f18e87af552dfc292138177846412f7`.

**Review status:** The complete article has been verified; see [`HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md`](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). It supplies the model, ADP/ADPOL definitions and computational design, but not seeds, exact sampled instances, an article-linked code archive, or inferential uncertainty. Table 1 includes `log I` and `F` coordinates whose mapping into the model’s initial-state/parameter notation is not made explicit in the inspected article text; this is recorded as a source-level reproducibility ambiguity, not resolved by conjecture. The separate 2017 formulation/ADPOL paper has not been independently audited. The unresolved CHT question is mathematical: the paper does not report the globally optimized strong-SEP class value.

## 3. Common mathematical notation

Use a finite-horizon controlled process as a comparison template, not as a claim that either paper has this exact representation:

- (X_t): true agent/worker capabilities or experience state.
- (W_t): exogenous demand/environment state.
- (Z_t): other endogenous state, such as queue length or remaining resources.
- (S_t=(X_t,W_t,Z_t)): full physical state.
- (A_t): assignment/scheduling decision.
- (D_t): explicit development decision, if the model has one.
- (I_t): decision maker's information at the decision time.
- (R_t): period reward, or negative cost under a cost-minimization convention.
- (P): state transition law; (T): horizon.

For a fully observed finite model one may write

\[
V_0(s)=\sup_{\pi\in\Pi} E_\pi\!\left[\sum_{t=0}^{T-1}\gamma^t R(S_t,A_t,D_t)+\gamma^T G(S_T)\mid S_0=s\right].
\]

This is only a notational umbrella. BLY analyze stationary continuous-time queueing steady states and average client payoff; CHT minimize expected finite-horizon service-time cost; HLS RQ0 uses finite exact common-world instances and does not impose one universal reward, terminal value, discount factor, or state transition. Set γ=1 only when an instantiated finite-horizon HLS world specifies undiscounted additive reward.

## 4. Canonical HLS-RQ0 reconstruction

### 4.1 Physical problem and information

**FACT.** The canonical RQ0 question is whether dynamic competence allocation and development can improve long-run system performance relative to architectures managing allocation and transfer separately (`docs/research_questions.md`, RQ0). It is a programme-level question; the current exact routing/development model is one narrower instantiation (`docs/HLS_CURRENT_STATE.md`, §§5–8).

In the canonical finite-exact routing formalization, a history (h_t) identifies physical state (S_t), feasible actions and available information. Under its common-world contract, evaluated policies share state physics, available operational/development actions, rewards, opportunities, resources, and authorized information. A policy label does not alter the transition. Write (A_t) for the operational routing action and (D_t) for any development action/opportunity decision included in the particular world. Then the world has a transition (P(S_{t+1}\mid S_t,A_t,D_t,W_t)); some worlds are deterministic. (W_t) may represent demand/opportunity. Information (I_t) must be common across compared policies unless a stated benchmark is explicitly full-information.

The HLS objective is the value induced by the instantiated reward and horizon, for example (J_\pi(s)=E_\pi[\sum_t\gamma^tR_t+\gamma^TG(S_T)\mid s]). There is no universal HLS scalar objective asserted by the project. A fixed or changing state alone does not imply endogenous learning: the dynamic theory requires the action-to-state link (A_t\to S_{t+1}=F(S_t,A_t)) for endogenous development (`docs/theory/HLS_DYNAMIC_THEORY.md`, §§2–6).

### 4.2 What “strong-SEP” actually restricts

Define the immediate reward greedy correspondence at history (h):

\[
G(h)=\arg\max_{a\in\mathcal A(h)}R(h,a).
\]

The canonical classes are:

\[
\Pi_{\rm HLS}=\{\text{all policies admissible under the common-world/information contract}\},
\]
\[
\Pi_{\rm SEP}=\{\pi\in\Pi_{\rm HLS}:A_\pi(h)\in G(h)\text{ at every positive-probability on-policy history}\}.
\]

Conditional on its actual route and realized development opportunity, strong-SEP's development manager optimizes development exactly. Ties remain sets; the project reports the best and worst tie-consistent SEP values where relevant. SEP-Ω is different: it gives the separated router sufficient exact action-conditioned continuation information so that it can make the Bellman choice (`docs/theory/rq0_routing_integration_boundaries.md`, §§2, 9).

Thus strong-SEP does **not**, by definition, mean all possible forms of “separation.” The five meanings must not be collapsed:

| Separation notion | Is it imposed by canonical strong-SEP? | Clarification |
|---|---|---|
| Decision-variable separation | **Specific restriction only** | Operational routing must be immediately greedy; development remains exactly optimized conditional on the realized route/opportunity. It is not arbitrary decomposition of all variables. |
| Optimization-objective separation | **No general factorization asserted** | The routing restriction is based on immediate (R), while development conditional optimization may use its declared objective; the formal world must state the objective. |
| Decision-time separation | **No** | The definition does not require route and development decisions to be made at different times. |
| Information-set separation | **No** | The common-information contract gives the compared policies the same authorized information. A separate-information comparison is a different experiment. |
| Optimization-procedure separation | **No** | It is a policy-class restriction, not a required software/process architecture. |

### 4.3 Proven results

**FACT — Theorem 1:** Under the common-world and common-information contract, ΠSEP ⊆ ΠHLS, hence (J_{SEP,max}(s)\le J_{HLS}(s)). This is set inclusion, not a substantive strict-advantage finding.

**FACT — Theorem 2:** In the finite exact setting with attained maxima,

\[
J_{HLS}(s)>J_{SEP,max}(s)\iff\Pi_H^*(s)\cap\Pi_{SEP}=\varnothing.
\]

So strictness requires that **every** HLS-optimal policy violate the strong-SEP restriction on its own positive-probability support. A local non-greedy Bellman choice is insufficient. These statements and proofs are in `docs/theory/rq0_routing_integration_boundaries.md`, §§3–6.

**FACT — SEP-Ω boundary:** In the audited exact A1/C1/λ/competence-geometry families, giving the separated router sufficient exact continuation information recovers HLS value. This shows that the documented gap is relative to the strong-SEP routing rule, not proof that modular architecture is intrinsically inferior (`docs/HLS_CURRENT_STATE.md`, §§6–8).

## 5. BLY mathematical model

### 5.1 State, flow, and training

**FACT.** In §§2–3, manuscript pp. 6–15, clients arrive in continuous time as a Poisson process of rate λ. There are two provider types: juniors deliver value (l), seniors value (h), with (h>l>0). There is an infinite pool of juniors, so junior service is immediate. Senior clients join a FIFO queue; the senior service-completion rate is μ, interpreted as a proxy for senior mass/capacity. A client choosing senior service receives (h-cW), where (W) is waiting time and (c>0); service-time costs are already included in (h,l).

Training is tied to the time-average flow served by juniors. If that flow is (x), the induced senior service capacity is

\[
\mu=f(x),\qquad x=(1-q)\lambda,
\]

where (q) is the fraction of clients assigned to seniors. (f:\mathbb R_+\to\mathbb R_+) is differentiable, weakly increasing and weakly concave, (f(0)=0); a linear case (f(x)=ax), (a>0), is often used. This is an equilibrium/steady-state flow relationship, not a per-worker experience transition (X_{t+1}=F(X_t,A_t)).

The senior-queue arrival rate is (q\lambda); feasibility requires stable senior service (in limited monitoring the paper states (q\lambda/\mu\in(0,1))). Under perfect monitoring, the allocation can condition on queue length via threshold (k): direct an arrival to junior when the senior queue reaches the threshold. This creates an M/M/1/k continuous-time Markov chain; the stationary queue distribution is in Lemma 1 and queue fraction relation in Lemma 2, equation (3), manuscript pp. 9–10. Under limited monitoring, allocation is stationary and queue-state independent; decisions boil down to (q).

### 5.2 Central planner and discretionary equilibrium

With limited monitoring, the planner chooses ((q,\mu)) subject to μ=f((1-q)λ), maximizing average client payoff:

\[
\max_{(q,\mu)\in\mathcal C}\;q\bigl(h-cE[W]\bigr)+(1-q)l,
\quad \mathcal C=\{(q,\mu):\mu=f((1-q)\lambda),\;q\lambda<\mu\}.
\]

Equivalently, with (\theta=(h-l)/c), its objective can be expressed up to positive scaling/additive constants as (q\lambda\theta-E[Q]), using Little's law (E[Q]=q\lambda E[W]). These are equations (8)–(10), Proposition 2, pp. 14–15. In the discretionary regime each arriving client individually chooses senior versus junior; equilibrium requires indifference, subject to the same induced training relation. This is a strategic equilibrium, not a planner's restricted policy class.

With perfect monitoring, the decision maker observes the senior queue length and uses threshold policies. Proposition 1 (p. 12–13) characterizes the discretionary equilibrium via

\[
k(q,\mu,\lambda)=\mu\theta+1,\qquad \mu=f((1-q)\lambda),
\]

and for linear (f(x)=ax), an interior centralized optimum satisfies

\[
\lambda\theta=\frac{dE[Q]}{dq},\qquad \mu=a(1-q)\lambda.
\]

Here (k(q,\mu,\lambda)) is the inverse of the stationary queue fraction relation from equation (3). The source considers stationary policies, including threshold policies optimal within the queue-state policy set specified in §3.1.1; it does not optimize arbitrary finite-horizon sequences of individual allocations.

### 5.3 Results relevant to HLS

**FACT — Proposition 1, perfect monitoring:** characterizes equilibrium and planner thresholds; the planner condition internalizes the marginal effect on expected queue length. It is not a strong-SEP theorem.

**FACT — Proposition 2, limited monitoring:** gives the equilibrium indifference condition and planner's unique optimum under the stated model/feasibility conditions. The planner accounts for congestion and the reduction in training when more clients are assigned to seniors.

**FACT — Proposition 3, perfect monitoring, linear training:** comparative statics in λ and (a) for thresholds, senior capacity, senior share and expected wait (pp. 16–17).

**FACT — Corollary 2, centralization (pp. 24–25):** for monitoring regime (X\in\{L,P\}), (q_X^*\le q_X^e) and μ(_X^*\ge\mu_X^e), strict when monitoring is limited or when the perfect-monitoring optimal threshold (k_P^*>1). Central assignment sends weakly fewer clients to seniors, creating more training capacity and lower queues/wait, albeit lower average service quality. Authors attribute the wedge to two externalities: clients' diversion from junior service reduces training and joining the senior queue imposes waiting on other clients.

This is a meaningful published comparison of a planner and decentralized discretionary behavior in a genuinely dynamic queue/training system. It does not compare to an optimized fixed mapping; in fact, the paper's basic environment is stationary in primitive arrival rate and solves steady-state policies.

## 6. CHT mathematical model — verified from the complete article

CHT’s service-time law, state, assignment constraints, experience transition, objective, Bellman equation, ADPBF value approximation, ADPOL benchmark, experimental design and reported temporal effects are reconstructed with article equations in the [full-text audit, §§3–5](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). In brief, (d^k_{rt}=(D^k_r q^k_{rt}/(q^k_{rt}+L^k_r))^{-1}) (Eq. (1)); assignments increment integer experience by same-type requests assigned (Eq. (5)); daily service-time capacity is Eq. (3); expected finite-horizon service-time cost is minimized using Eq. (7).

The published comparison is ADPBF against ADPOL on matched test task realizations, not best static or strong-SEP. The experiment uses 600 instance settings (30 generated five-technician workforces × four availability levels × five task-diversity levels), 120-day horizons, 50 requests/day, and 1000 training iterations plus 1000 testing trials (pp. 126–127). At diversity 5, the authors report ADPOL about 5% better in the first 10 days and ADPBF about 2.5% better in the final 60 days (Fig. 1, p. 127). They report no confidence intervals or formal significance tests. Exact sampled workforces/demand paths cannot be reconstructed from the article because it gives no seeds or linked code/data archive.

## 7. Formal model mappings

“Partial structural correspondence” means shared mathematical ingredients, not preservation of the entire optimization problem. None of the following is certified as an exact reduction.

| Direction | State mapping | Actions / constraints | Transitions | Objective | Policies / information / horizon | Classification |
|---|---|---|---|---|---|---|
| BLY → HLS | Could encode a queue state plus senior capacity μ; HLS competence matrix would need a representation of aggregate junior/senior mass. | BLY action is flow share (q), or queue threshold (k); HLS routing/development actions are finite organizational choices in current RQ0. Queue stability and FIFO service constraints have no direct current RQ0 counterpart. | BLY's steady-state μ=f((1-q)λ) is an endogenous flow fixed-point; not the same as HLS's periodwise (X_{t+1}=F(X_t,A_t,D_t)). | Average client utility with waiting penalty; HLS has no universal scalar objective and often finite-horizon system reward. | BLY is continuous-time, stationary/steady-state with either planner or client equilibrium; HLS RQ0 is finite exact, common-world policy optimization. | **PARTIAL STRUCTURAL CORRESPONDENCE; NOT EXACT** |
| HLS → BLY | A two-tier state might map only if all agents/tasks collapse to junior/senior capacity and the only operational memory is queue length. | HLS allocation would have to collapse to a senior share/threshold; arbitrary task types, multi-skill matrices, effort/resource budgets, or explicit teaching do not map. | HLS development must be represented by BLY's μ=f(junior flow) steady-state relation; arbitrary action-specific skill-vector updates are excluded. | HLS reward must reduce to value h/l less queue waiting cost, averaged per client. | HLS information and policy class would have to match BLY's observable queue / unobserved queue regimes and equilibrium/planner role. HLS finite horizon must be replaced or restricted to stationary steady state. | **SPECIAL CASE POSSIBLE ONLY UNDER RESTRICTIVE REFORMULATION; GENERIC HLS INCOMPATIBLE** |
| CHT → HLS | Map (q^k_{rt}) to per-agent/task state; requests to task instances; binary (x^k_{it}) to allocation; future requests to exogenous (W_t). | Must preserve exactly-once assignment and (sum_i x^k_{it}d^k_{r(i)t}\le Y), not current N×K effort budget by analogy. | Eq. (5) is deterministic task-specific experience from assignment. | Must use (-C) for reward, where C is total service time Eq. (6); no extra CES/output reward. | Same current-day reveal, known parameters, finite horizon. ADPBF and ADPOL are admissible dynamic rules under this embedding. | **EXACT SPECIAL CASE OF BROAD HLS CONTROL TEMPLATE; NOT CURRENT RUNNER** |
| HLS → CHT | Only if HLS state is positive integer task-specific experience. | Only if actions are indivisible daily assignments and service-time capacity is the resource constraint. | Only assignment-induced one-count updates; no independent development, MIS-v2, transfer, teaching or forgetting. | Must reduce to negative cumulative service time. | Must match known parameters, current demand reveal, and CHT horizon/information. | **RESTRICTED SUBMODEL ONLY; GENERAL HLS NOT EQUIVALENT** |

### Why no exact reduction is presently established

An exact reduction must preserve state sufficiency, feasible decisions, transition probabilities, objective, horizon and information. The broad CHT-to-HLS controlled-process embedding is available when these components are instantiated as in CHT; it does not establish identity with the current N×K runner or a general reverse reduction:

- BLY's single stationary rate μ induced by long-run junior flow is not a vector of periodwise agent/task experience. BLY's queue congestion and waiting disutility are essential to the theorem; dropping them changes the planner's trade-off.
- BLY's decentralized clients choose individually and create externalities; this is not equivalent to a centralized separated manager with an immediate-greedy rule.
- CHT has discrete job assignments and a technician-specific service-time capacity constraint; the existing N×K runner has its own effort/output/resource semantics. A mathematical state/action embedding is possible, but exact reproduction requires a CHT-specific adapter or formulation that preserves Eq. (3) and (6).
- CHT's inverse productivity curve is a restricted instance of the scalar Nembhard Direct equation ((p=0,k=D^k_r,r=L^k_r)); this does not identify CHT service-time cost with HLS output or effort.
- HLS worlds with separate development decisions, MIS-v2, teaching, transfer, or different competence transitions are outside CHT unless restricted away. CHT's development is endogenous to assignment, with no independent training action.

## 8. Strong-SEP comparison

### BLY

BLY's planner centrally maximizes a population payoff over (q) (or threshold (k)); discretionary clients choose providers and reach a strategic equilibrium. Centralization internalizes the waiting imposed on other queue users and the training opportunity lost when a client avoids junior service. This comparison changes **who optimizes** and whether externalities are internalized. Strong-SEP instead compares two policy classes in one common physical world and information structure: the restricted class forces route choices into the immediate reward-greedy set, while development remains exactly optimized conditional on the route. BLY's discretionary equilibrium is not that class: it is individually payoff-maximizing, not constrained to immediate system-reward greedy routing, and its private payoff depends on expected queueing. BLY's planner is not unconstrained HLS by policy-class definition either; it is a stationary threshold/flow optimization in BLY's queue model.

No BLY proposition establishes (J_{HLS}>J_{SEP,max}) under an equivalent mapping. Corollary 2's strict result concerns planner versus discretionary outcomes under BLY assumptions, not the HLS Theorem 2 criterion.

### CHT

CHT's ADPBF and ADPOL are computational decision methods for the same MTSP-ESTSC objective. ADPBF approximates longer-horizon value; ADPOL adds a forecast next-day service-cost term. This is a comparison of continuation-value horizon/approximation, not separation of allocation from development. ADPOL is not established as belonging to the **globally optimized** class that chooses only current-service-time minimizers and then optimizes the full horizon. Its next-day term may select a current non-greedy assignment. See the [full-text audit, §7](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md).

### Policy inclusion and SEP-Ω

The HLS inequality (J_{SEP,max}\le J_{HLS}) follows directly from Π_SEP⊆Π_HLS in its common world. BLY's classes are not HLS classes under the verified definitions. CHT does not define strong-SEP, but its model admits a well-defined instantiation: set (R=-C), constrain daily actions to current-cost minimizers, and optimize the horizon over that restricted policy class. Conditional development is forced by assignment in CHT, so its conditional optimization is trivial. CHT reports neither this restricted value nor its comparison with the unrestricted Bellman optimum. An exact continuation-aware SEP-Ω could be defined in the CHT world, but it would solve Eq. (7) by construction; ADPBF is approximate and is not SEP-Ω. Details are in the [full-text audit, §7](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md).

## 9. Existing HLS results versus the publications

| HLS result | Verified mathematical content | Closest relation to BLY / CHT | What is not established by the comparison |
|---|---|---|---|
| **RQ0** | Policy-class inclusion; finite-exact strictness iff no HLS optimum is strong-SEP-admissible; local Bellman inversion alone insufficient (`rq0_routing_integration_boundaries.md`, Theorems 1–2, §§5–9). | BLY shows planner vs discretionary equilibrium. CHT is a finite-horizon assignment/experience MDP; ADPBF vs ADPOL does not compare the optimized strong-SEP class. | Whether CHT has a strict strong-SEP gap remains uncomputed; the article neither proves nor refutes one. |
| **G3** | In 3 workers × 2 types, the MIS learning increment's collective development value reduces exactly to ordinary assignment sensitivity/gaps (`HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`, §§1–10). | Structural analogy: assignment changes task-specific experience and future service cost. | No proof of G3's exact MIS-v2 identity; CHT uses a different learning law, feasibility set and objective. |
| **G3-H** | Heterogeneous fixed learning scales and future opportunity can reverse a local ranking; exact scenario and values in G3 ground truth §11. | CHT has future stochastic requests and reports longer-continuation ADPBF advantage over ADPOL in generated cases. | Does not prove G3-H's exact ranking reversal or a general future-opportunity theorem. |
| **C1** | The candidate (M+\beta^2\max_yD) is falsified on a closed counterexample because it drops future operational reward and the joint future (R-D) trade-off (G3 ground truth §12). | CHT uses a cost-to-go approximation; Appendix A gives counterexamples to monotonicity/convexity in aggregate experience summaries. | Does not test the specific C1 shortcut or prove exact HLS continuation sufficiency. |
| **C2** | Restoring “max future (R+\beta D)” reduces to standard one-step lookahead/finite-horizon DP (G3 ground truth §12). | CHT Eq. (7) is standard Bellman recursion; ADPBF approximates its post-decision continuation. | ADPBF remains approximate; no exact reduction for other HLS worlds follows. |
| **E1** | Local protocol/audit reports a Nembhard-inspired direct-experience adaptation; FIXED and ORACLE were profile-aligned and nearly coincident; ADAPTIVE underperformed FIXED in its own configuration. The local audit notes this is not a full reproduction of BLY or Nembhard's full model (`docs/experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md`). | BLY motivates training/queue externalities, but E1 has no queue/wait mechanism; CHT motivates stochastic future task allocation, but E1 used its own Nembhard direct productivity and policy design. | E1 does not test BLY's planner-vs-equilibrium theorem or CHT's ADP-vs-ADPOL result. Do not infer a general failure of adaptive allocation. The cited E1 protocol/review are local experiment records, not the BLY/CHT primary studies. |
| **E2.1** | In its 2×2 separable model, nondecreasing Nembhard productivity makes cumulative single-skill returns discretely convex; the maximum over assignment counts lies at an endpoint, which BEST-STATIC task mapping represents. The protocol documents this structural scope and 33 deterministic cases (`docs/experiments/HLS_E2_1_PROTOCOL.md`). | It is a valid null/control for separable skill returns, not a reproduction of CHT's stochastic technician scheduling or BLY's queue model. | E2.1 does not establish static optimality outside its uncoupled one-task-per-period structure, nor test online estimation. |

The E1 and E2.1 specifications/results exist in the current local worktree; their status and reproducibility should be treated according to the repository's own provenance records. This report does not modify or promote those results.

## 10. Established / reducible / open

### ESTABLISHED

- BLY establish, for their queueing/training model, planner and discretionary characterizations, comparative statics and a weak/strict centralization result under Corollary 2's exact conditions. The mechanism is externality internalization over congestion and training, not generic “jointness.”
- CHT's MDP, ADPBF/ADPOL methods, and computational comparison are established from the complete article, with scope and evidence limits documented in the full-text audit.
- HLS's Theorem 1 policy inclusion and Theorem 2 strictness criterion are established for their explicit finite-exact common-world formalization. Constructive strict examples and SEP-Ω equalities are bounded to their stated families (`docs/HLS_CURRENT_STATE.md`, §§6–8; routing boundaries §§10–11).
- G3's assignment-sensitivity identity and the closed G3-H/C1/C2 calculations are established only in their documented synthetic assumptions.

### REDUCIBLE

- HLS's class-inclusion inequality is reducible to the elementary theorem that maximizing over a superset weakly increases the optimum. It carries no strict-advantage implication.
- G3's development-value calculation reduces to standard assignment sensitivity in its 3×2 assignment setting, as its canonical ground truth explicitly states.
- C2's exact continuation evaluation is standard look-ahead/DP by its algebraic identity; CHT Eq. (7) independently uses standard Bellman recursion while ADPBF approximates it. No exact mapping to G3-H is asserted.
- BLY's centralization result can be understood as a model-specific planner-versus-equilibrium result with two externalities; it cannot be renamed HLS joint-versus-strong-SEP.

### OPEN

- Whether CHT's restricted strong-SEP value equals its unrestricted Bellman value or has a strict gap; the article does not calculate this comparison. Exact mapping to the current N×K runner's resource/output semantics would require a CHT-faithful adapter.
- Whether any BLY submodel can be represented exactly in an expanded HLS state/action space **without** replacing its continuous-time stationary queue/training relation by a different finite-period learning law. The current RQ0 model does not provide that mapping.
- CHT does not name strong-SEP, but a precise instance of the policy restriction can be defined as in the full-text audit. Whether that restricted class is economically meaningful beyond the CHT objective remains an interpretation, not a published result.
- Whether strict HLS joint-vs-strong-SEP value results generalize beyond the current finite exact families. They do not follow from BLY Corollary 2 or the CHT ADP comparison.

## 11. Open mathematical questions (maximum three)

### Q1 — Does the CHT MDP have a strict gap against optimized strong-SEP?

**Formulation.** Compare exact Bellman value (V^*(s_1)) with (V_{SEP}(s_1)), the minimum expected total service-time cost over policies constrained to select only (a_t\in\arg\min_{a\in A_t(s_t)}C(s_t,a)) at every on-policy state. CHT has no independent development action; the experience transition is forced by Eq. (5).

**Closest results:** HLS Theorem 2 gives the necessary-and-sufficient policy-support criterion; CHT supplies a finite-horizon assignment/experience MDP but does not report the constrained class value. **Positive:** one exact finite instance with certified (V^*<V_{SEP}) in cost minimization. **Negative:** equality proof for a declared instance family or certified equality on an instance. **Difficulty:** high due to task-specific experience and demand states. **Minimum evidence:** exact finite DP for unrestricted and greedy-constrained policies with identical feasibility, demand law, information and tie treatment.

### Q2 — How accurately does CHT's aggregate-experience basis preserve continuation value?

**Formulation.** CHT maps task-specific (Q^k_t=(q^k_{1t},...,q^k_{Rt})) to the per-technician aggregate (sum_rq^k_{rt}) in its ADPBF features. Determine the value/policy loss induced by states with identical aggregate features but different task-wise experience allocations.

**Closest result:** Appendix A, Examples A.1–A.3, already shows non-monotonicity/non-convexity of optimized service-time value in several aggregate experience summaries. **Positive:** certify an instance where same-feature states have distinct optimal continuations and quantify approximation loss. **Negative:** prove a useful bound or exactness condition for a specified demand/parameter class. **Difficulty:** medium-high. **Minimum evidence:** exact finite-horizon values and the ADP feature collision; no campaign-scale replication is needed.

### Q3 — When does stationary-flow training approximate assignment-dependent learning without changing the allocation ranking?

**Formulation.** Compare BLY-style stationary capacity μ=f(x) with a finite-horizon individual experience state (X_{t+1}=F(X_t,A_t)). Identify conditions under which the induced capacity/queue objective and optimal allocation share coincide (or a counterexample where they differ), including arrival rate, training concavity, congestion cost and horizon.

**Closest result:** BLY's flow/training constraint and centralization characterization; HLS G2/G3 experience transitions. **Positive:** a limit/reduction theorem under an explicit scaling/stationarity regime. **Negative:** a counterexample showing ranking changes even under a candidate aggregation. **Difficulty:** high, because steady-state and finite-horizon state dynamics differ. **Minimum evidence:** define a common queueing reward and derive a limit or exact finite mapping; arbitrary curve analogy is insufficient.

## 12. Recommended next scientific action

**PROPOSAL — analyze the exact CHT strong-SEP restriction against its unrestricted Bellman optimum on a bounded finite instance class before authorizing a reproduction campaign.** The full-text equation/mapping audit is complete; article-specific stochastic draws and exact reproduction remain unavailable without seeds or an associated data/code archive.

This isolates the unresolved policy-class question rather than rechecking source access: CHT's assignment-dependent task-specific experience and finite-horizon demand are now reconstructed, but its published ADPBF–ADPOL comparison does not include optimized strong-SEP. BLY remains a distinct steady-state queueing/externality model and cannot resolve that gap.

## 13. References and pinpoint citations

1. **Baccara, M., Lee, S., & Yariv, L. (2023).** “Task Allocation and On-the-job Training.” *Journal of Economic Theory*, 207, 105587. DOI: [10.1016/j.jet.2022.105587](https://doi.org/10.1016/j.jet.2022.105587). Full accepted manuscript: [author PDF](https://www.lyariv.com/papers/TaskAllocation.pdf). Model: §2, manuscript pp. 6–8; threshold Markov queue and stationary mapping: §3.1.1, pp. 9–12, equations (2)–(6), Lemmas 1–3, Proposition 1; limited monitoring/planner and equilibrium: §3.2, pp. 13–16, equations (8)–(11), Proposition 2; comparative statics: Proposition 3, pp. 16–17; monitoring: §5, pp. 20–24, Lemma 4/Propositions 5A–5B; planner versus discretion: Corollary 2, §6, pp. 24–25; scope/conclusions: §7, pp. 25–26. Page labels refer to manuscript pagination and may differ from final journal pages.

2. **Chen, X., Hewitt, M., & Thomas, B. W. (2018).** “An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers.” *International Journal of Production Economics*, 196, 122–134. DOI: [10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028). Complete 13-page published article: [`local PDF`](../literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf), SHA-256 `58320e719bf4d54d76ecb6ae01ba94dc3f18e87af552dfc292138177846412f7`. Its full equation-level analysis is documented in [`HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md`](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). The separate 2017 formulation paper and any external code/data archive were not independently verified.

3. **HLS canonical documents:** [`docs/research_questions.md`](../research_questions.md); [`docs/theory/rq0_routing_integration_boundaries.md`](../theory/rq0_routing_integration_boundaries.md), especially §§1–9 and Theorems 1–2; [`docs/HLS_CURRENT_STATE.md`](../HLS_CURRENT_STATE.md), §§5–8 and G3-H discussion; [`docs/theory/HLS_DYNAMIC_THEORY.md`](../theory/HLS_DYNAMIC_THEORY.md), §§2–7; [`docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md); [`docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), §§1–12; [`docs/experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md`](../experiments/HLS_NEMBHARD_PROTOCOL_REVIEW.md); [`docs/experiments/HLS_E2_1_PROTOCOL.md`](../experiments/HLS_E2_1_PROTOCOL.md).
