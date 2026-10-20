# HLS — Chen et al. (2018): full-text mathematical audit and comparison with RQ0

**Date:** 19 October 2026
**Scope:** Primary-source mathematical analysis and documentation only. No code or experiments changed or run.
**Primary source:** Xi Chen, Mike Hewitt, and Barrett W. Thomas, “An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers,” *International Journal of Production Economics* 196 (2018), 122–134, DOI [10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028). The complete local 13-page article is [`Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf`](../literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf), SHA-256 `58320e719bf4d54d76ecb6ae01ba94dc3f18e87af552dfc292138177846412f7`.

**Evidence labels:** **FACT** means directly stated in the inspected article or canonical HLS proof; **INFERENCE** is a consequence under stated assumptions; **HYPOTHESIS** is unresolved; **PROPOSAL** is a suggested next analysis.

## 1. Executive mathematical findings

**FACT.** Chen, Hewitt and Thomas (CHT) formulate a finite-horizon stochastic technician-scheduling MDP. At each day, the current requests are observed, assigned to heterogeneous technicians subject to daily service-time capacity, and each completed assignment deterministically increments that technician’s experience for that task type. Experience lowers that technician-task service time according to a known learning curve. Future requests are exogenous and unknown until their service day. The objective is expected total service time over the horizon (article pp. 123–125, Eqs. (1)–(7)).

**FACT.** Their ADP basis-function method (ADPBF) approximates a time-indexed post-decision cost-to-go using an intercept plus one feature per technician: that technician’s *aggregate* experience across all task types after the current assignment (pp. 125–126, Eqs. (8)–(10)). Coefficients are fitted offline by approximate value iteration and recursive least squares (Appendix B, pp. 132–134, Eqs. (16)–(20)). This is not online learning of unknown productivity: the learning parameters and experience state are known to the scheduler. It is approximate dynamic optimization of assignment decisions under endogenous learning-by-doing.

**FACT.** The comparator ADPOL is not a fixed allocation. It reoptimizes assignments each day using current requests and a forecast of next-day assignments and service times, with exponential smoothing factor α = 0.9 (pp. 126–127, Eqs. (11)–(15)). It is a one-day lookahead heuristic, not a myopic immediate-cost rule and not the canonical HLS strong-SEP class.

**FACT.** CHT report that ADPBF initially incurs higher daily service-time cost than ADPOL, then performs better later: for diversity 5, the article reports ADPOL about 5% better on average in the first 10 days, and ADPBF about 2.5% better consistently in the final 60 days. The average comparison is over workforces and instances; the authors report convergence by month 4 as workers accumulate experience. These are reported computational findings, not a statistical claim with confidence intervals or hypothesis tests (pp. 127–130, Figs. 1–5). The article does not report inferential uncertainty for those averages.

**INFERENCE.** The comparison demonstrates the value, in the tested model and test instances, of a longer-horizon continuation approximation relative to a particular one-day forecasting heuristic. It does **not** establish that ADPBF beats the globally optimal static task-dependent assignment, every immediate-greedy policy, HLS strong-SEP, or an exact optimal policy. Nor does it establish an online learner’s advantage under unknown productivity parameters.

**INFERENCE.** CHT can be represented as a restricted controlled process within the broad mathematical template of HLS-RQ0 if the state, per-day assignment actions, stochastic demand, service-time objective, capacities, and information timing are all carried over exactly. That is a mathematical embedding, not an assertion that the existing HLS N×K/MIS-v2 or Nembhard runner already implements the CHT scheduling model. A restricted mapping of the CHT productivity law to the scalar Nembhard-inspired curve exists after an explicit reciprocal transformation, but the action, objective, and resource semantics still differ.

**CONCLUSION.** CHT does not resolve the central HLS strong-SEP question. Its ADP-versus-ADPOL result compares two continuation-value methods, and ADPOL is not the strong-SEP optimum. The most useful next mathematical step is to instantiate canonical strong-SEP in the CHT MDP (immediate service-time-minimizing assignment each day, with no separate development action) and compare its *globally optimized policy class value* with the unrestricted finite-horizon optimum. This would establish whether the CHT model itself satisfies the HLS strict-gap criterion; the paper’s ADP computational comparison cannot answer that.

## 2. Source verification and scope

The local primary source is the complete published article, not an abstract or preview. Its title page gives DOI, authors, publication information, and journal pagination 122–134. PDF page numbers are cited below as journal printed pages; the file has 13 pages, so PDF page 1 corresponds to printed p. 122. The equation, figure, table, and appendix references below were checked against extracted text from the complete PDF. The PDF text extraction renders some mathematical glyphs imperfectly; equation (1) was cross-checked against the article’s Appendix A numerical examples (pp. 131–132), which reproduce its service-time values.

The article identifies the 2017 formulation paper by Chen, Thomas and Hewitt as the source of the MTSP-ESTSC formulation and repeats it for completeness (p. 124). The audit concerns the 2018 paper’s stated model and experiments; it does not assume that the separate 2017 article or unprovided code/supplement has been independently reproduced. The 2018 article reports Gurobi 5.6, Python 2.7, and an Intel Xeon/CentOS 6.3 environment (p. 126), but the inspected article itself does not supply implementation code, random seeds, or a machine-readable instance archive.

## 3. Chen model in the authors’ notation

### 3.1 Sets, state, and service-time learning curve

**FACT.** The horizon consists of days (t=1,\ldots,T), technicians (k\in K=\{1,\ldots,K\}), and task types (r\in R=\{1,\ldots,R\}). On day (t), the individual request set is (N_t=\{1,\ldots,n_t\}); request (i) has type (r(i)\in R). The number and types of future requests are random. (The article uses (N_t) both for the set and its cardinality in places; (n_t) here disambiguates the count.)

For technician (k), task type (r), and the start of day (t), (q^k_{rt}) is the number of times that technician has performed task type (r). The vector (Q^k_t=(q^k_{1t},\ldots,q^k_{Rt})), with (Q^k_0) the initial experience, is task-specific and cumulative. The technician-task parameters are (D^k_r), the maximum productivity rate, and (L^k_r), the learning rate; both may vary by technician and task (printed p. 124, immediately before Eq. (1)).

The article’s Eq. (1) defines service time as the reciprocal of productivity:

\[
 d^k_{rt}=\left(D^k_r\frac{q^k_{rt}}{q^k_{rt}+L^k_r}\right)^{-1}
 =\frac{q^k_{rt}+L^k_r}{D^k_r q^k_{rt}}.
\tag{CHT-1}
\]

This transcription is consistent with the article’s Appendix A: at (D=1,L=1,q=10), service time is 1.1; at (D=0.5,L=1,q=9), it is (10/(0.5\cdot9)=2.22), the values in Table 3 (printed p. 131). **Domain note:** Eq. (1) is defined only for (D^k_r>0), (q^k_{rt}>0), and (q^k_{rt}+L^k_r\ne0); Appendix A’s numerical states have positive experience. Table 1’s `log I` may relate to initial experience, but its mapping is not explicit in the model text. The inspected formulation does not state a service-time convention at (q=0). A faithful implementation therefore needs positive initial experience or an explicitly sourced extension at zero; setting a value at zero by convention would be an additional modeling decision.

Equivalently, task productivity is (1/d^k_{rt}=D^k_r q^k_{rt}/(q^k_{rt}+L^k_r)). **Dimensional inference:** because (q) and (L) are added, (L) must be in the same experience-count scale; (D) is productivity (requests per unit time if service time is measured in time/request), and (d) is service time per request. The paper does not separately declare physical units. For positive parameters this productivity is increasing in (q), approaches (D^k_r), and has diminishing marginal increments; service time decreases toward (1/D^k_r). There is no forgetting term. Experience is integer-valued, and changes deterministically conditional on assignments. Capability development is not a separately chosen training variable: it occurs as a consequence of performing requests.

### 3.2 Actions, capacity, and state transition

At the start of day (t), the pre-decision state is (s_t=\{N_t,Q_t\}) (printed p. 124). The binary variable (x^k_{it}) equals 1 if request (i) is served by technician (k). A feasible action assigns each request exactly once and keeps each technician’s total service time within daily availability (Y):

\[
\sum_{k\in K}x^k_{it}=1\quad(i\in N_t), \tag{2}
\]
\[
\sum_{i\in N_t}x^k_{it}d^k_{r(i)t}\le Y\quad(k\in K), \tag{3}
\]
\[
x^k_{it}\in\{0,1\}. \tag{4}
\]

Equation (3) is a service-time capacity, not an effort or monetary budget. Every request is served; there is no rejection, deferral, explicit training action, route, transfer, or forgetting mechanism in this model.

The post-decision experience transition is deterministic:

\[
q^k_{r,t+1}(s_t,a_t)=q^k_{rt}+\sum_{i\in N_t:r(i)=r}x^k_{it},\quad k\in K,r\in R. \tag{5}
\]

Thus assignment affects both current service-time cost through the selected technician and future service times through next experience. Future requests (W_{t+1}=(w_{1,t+1},\ldots,w_{N_{t+1},t+1},N_{t+1})) are exogenous; their types and count are not known before day (t+1). Once revealed, experience remains the post-decision value, (Q_{t+1}=Q^a_t) (printed p. 125). The decision-maker observes current demand and tracks its own assignments/experience; the learning parameters are assumed known (pp. 123–124).

### 3.3 Reward/cost and exact dynamic program

The immediate cost is total service time:

\[
C(s_t,a_t)=\sum_{k\in K}\sum_{i\in N_t}x^k_{it}d^k_{r(i)t}. \tag{6}
\]

The objective is to minimize expected undiscounted cumulative cost over the finite horizon:

\[
\min_{\pi\in\Pi}\mathbb E\left[\sum_{t=1}^{T}C(s_t,\delta_t^\pi(s_t))\right],
\]

where δ maps the current state to a feasible daily schedule (p. 125). The exact Bellman equation is

\[
V(s_t)=\min_{a\in A_t(s_t)}\{C(s_t,a)+\mathbb E[V(s_{t+1})\mid s_t,a]\}. \tag{7}
\]

The paper states that the exact state and action spaces are too large for standard backward DP (p. 125). No independent action (D_t) for development appears; all capability evolution is induced by (a_t) through Eq. (5). The cost horizon is finite; no terminal reward is added in the displayed objective/Eq. (7).

### 3.4 ADPBF: what is approximated and how

The authors use post-decision states (s^a_t=\{N_t,Q^a_t\}), replacing the continuation term by an approximation (Eq. (8), printed p. 125). For each time (t), Eq. (9) uses a linear basis expansion. There are (J=K+1) features: an intercept and one feature per technician. Eq. (10) defines technician (k)’s feature as total experience over *all* task types after the day-(t) assignment:

\[
\phi_{1+k,t}(s^a_t)=\sum_{r\in R}q^k_{rt}+\sum_{i\in N_t}x^k_{it}.
\tag{10}
\]

The resulting daily integer program minimizes current service-time cost plus θ-weighted post-assignment aggregate experience (Eq. (9) and formulation (P), printed pp. 125–126). Coefficients are time-specific. This compression discards the distribution of each technician’s experience across task types from the *approximate value features*, though the exact state and current service-time calculation remain task-specific. Appendix A explicitly demonstrates why aggregate total experience need not order future cost monotonically or convexly (Examples A.1–A.3, Tables 2–8, printed pp. 131–132).

Coefficients are learned offline with approximate post-decision value iteration: a forward simulated sample path, backward cost-to-go updates, and recursive regression (Appendix B.1–B.2, pp. 132–134). Initialization was either zero or a regression fit to myopic-policy simulation; the latter gave better solutions (p. 133). Recursive least squares is described in Eqs. (16)–(20), with (B_0=\lambda I); after testing values, the authors use λ = 0.9 (printed p. 134). This is model-based offline approximation training, not online estimation of (D,L) or (q) from noisy execution observations.

## 4. One-day lookahead baseline ADPOL

**FACT.** ADPOL is the solution method in Chen et al. (2017), used as the benchmark (CHT §5.2, printed pp. 126–127). It re-solves a daily assignment problem in rolling-horizon fashion. Its objective is current-day service cost plus forecast next-day service cost, not current cost alone (Eqs. (11)–(15)). It forecasts the number of future task-type assignments by technician using exponential smoothing:

\[
F^k_{rt}=\alpha F^k_{r,t-1}+(1-\alpha)A^k_{r,t-1},\qquad \alpha=0.9,
\]

where (A^k_{r,t-1}) is the preceding day’s number of type-(r) requests assigned to technician (k). Forecast service times use experience after the previous assignments and Eq. (1) (Eqs. (11), (13)–(14)); the two-period objective is Eq. (12). At the first period the forecast is initialized from the current assignment counts as specified below Eq. (13). The exact nonlinear problem is reformulated using methods cited from Hewitt et al. (2015); full reformulation details are referred to Chen et al. (2017), not reproduced in CHT.

ADPOL knows current-day requests and current experience, and uses the smoothed history of assigned demand to forecast the next day; it does not know the future realized requests. It accounts for experience from today’s assignments insofar as they alter forecast next-day service times. It does **not** optimize a continuation over the remaining full horizon. Its policy changes with current demand, experience, and forecast history, so it is neither constant-action nor fixed task-to-technician mapping. It is not “myopic” in the strict immediate-cost sense, though it is short-horizon relative to ADPBF.

## 5. Computational experiments and reported findings

### 5.1 Design

CHT §5, printed pp. 126–127, reports:

| Design element | Published setting |
|---|---|
| Workforce | 30 generated workforces, each with 5 technicians and heterogeneous learning/productivity parameters sampled from a multivariate normal distribution whose mean/covariance are derived from Nembhard & Osothsilp (2005); see CHT Table 1. |
| Availability | (Y\in\{5,6,7,8\}); 5 is stated as the tightest availability ensuring feasibility. |
| Task diversity | (|R|\in\{5,7,10,13,20\}). |
| Instance count | (30\times4\times5=600). |
| Horizon | 120 days. |
| Demand per day | 50 requests. |
| Request type | Each request type sampled independently each day from the discrete uniform distribution over the instance’s task types. |
| Repetitions | 1000 training iterations and 1000 testing trials for ADPBF; ADPBF and ADPOL evaluated on the same test task realizations. |
| Computing environment | Gurobi 5.6, Python 2.7 interface, Intel Xeon, CentOS 6.3. |

Table 1 (printed p. 126) reports the following mean vector and covariance matrix, in the displayed order of variables `log D`, `log I`, `log L`, `F`:

\[
\mu^T=(1.448,\ 1.963,\ 2.0446,\ 2.269),
\]
\[
\Sigma=\begin{pmatrix}
0.0045&0.0167&0.0191&-0.0214\\
0.0167&0.4621&0.2443&-0.2380\\
0.0191&0.2443&0.1905&-0.2326\\
-0.0214&-0.2380&-0.2326&0.3638
\end{pmatrix}.
\]

**Source ambiguity:** Section 3 defines (D^k_r), (L^k_r), and initial experience (Q^k_0), while Eq. (1) depends on (D,L,q). Table 1 additionally labels distribution coordinates `log I` and `F`; the inspected model text does not explicitly map both labels to the Eq. (1) parameters or state initialization, and does not define a forgetting transition. The design text says learning rate and steady-state productivity are sampled, but it does not resolve the role of every Table 1 coordinate. We therefore preserve these table labels as printed rather than conjecturing what (F) means. Reconstructing the exact published workforce draws requires clarification of this mapping.

The article’s instance-generation description also gives no reproducible random seed or truncation/repair rule if a multivariate-normal draw violates parameter domains. Thus the design is specified at the distributional level but the exact 30 workforce draws and 1000 demand paths are not reconstructible from the article text alone. The inspected PDF does not provide a code/data link.

### 5.2 Performance outcome and temporal pattern

The authors record daily total service time for each method. For day (t), their relative gap is

\[
gap^{ol-bf}_t=\frac{Obj^{ol}_t-Obj^{bf}_t}{Obj^{bf}_t},
\]

so positive values mean ADPBF has lower service-time cost. Figure 1 (printed p. 127) plots average daily gaps grouped by task diversity and averaged across workforces and instances. Reported patterns:

- ADPBF ultimately outperforms ADPOL at all diversity levels in the reported experiment.
- At diversity 5, ADPOL is about 5% better on average over the first 10 days; ADPBF is about 2.5% better consistently over the last 60 days.
- The authors say ADPBF becomes better after roughly day 15; the early disadvantage is larger with fewer task types, while later savings are also larger at lower diversity.
- Figure 3 reports that diversity is the instance parameter with a significant association with the gap; the largest diversity effect occurs in the middle two months. The authors explain convergence around month 4 by sufficient experience opportunities for all workers.
- Figures 2a–b show the fitted continuation weights decreasing rapidly and converging: the authors interpret ADPBF as emphasizing workforce positioning early, then becoming effectively myopic after about day 15. The average change in theta is reported as 0.07 by day 5 and zero by day 21.
- Figures 4–5: ADPBF’s technicians are less specialized by the paper’s coefficient-of-variation measure than ADPOL’s, but ADPOL distributes workload more evenly across technicians. The authors interpret high-quality ADPBF schedules as cross-training the workforce.

These statements are the paper’s descriptions of plotted averages and correlations (CHT §6, printed pp. 127–130). No confidence intervals, standard errors, p-values, or formal paired significance tests are reported in the inspected computational results. The term “significant” in the discussion of Figure 3 should therefore not be read here as documented inferential statistical significance. The article establishes a computational advantage on its generated test suite, not a population-level guarantee. It does not report a direct ADPBF-vs-optimized-static comparison.

### 5.3 What explains the performance differences

**FACT.** The objective is total service-time minimization; the policies differ in how they value post-decision consequences. ADPOL includes forecast next-day cost; ADPBF uses a fitted value-function term intended to approximate cost-to-go over the remaining horizon. Both face the same model and test realizations in comparisons (pp. 126–127).

**AUTHORS’ INTERPRETATION.** ADPBF sometimes accepts greater early service time to distribute experience and position multiple technicians to serve a wider variety of future tasks efficiently. After a ramp-up period, marginal learning is small for many workers and the fitted weights approach zero; decisions then become close to immediate-cost scheduling (pp. 127–130).

**LIMIT.** The experiment does not isolate the causal contribution of each feature (longer continuation horizon, basis-function design, training initialization, or offline fitting) through ablations. Nor does it show the optimum dynamic value: ADPBF is approximate. Because the comparison is against ADPOL rather than the optimal one-day-lookahead policy class or best stationary policy, the measured gap is algorithm-relative.

## 6. Formal correspondence with HLS-RQ0

### 6.1 Common-process mapping

The mapping below is an explicit embedding into the *general* finite-horizon controlled-process interpretation of RQ0, not identity with every HLS realization.

| Chen object | Candidate HLS-RQ0 object | Mapping and status |
|---|---|---|
| Day (t), finite (T) | Decision stage (t), horizon (T) | **EXACT** under same indexing and undiscounted finite horizon. |
| Technician (k) | Agent (i) | **EXACT** as a role mapping for this scheduling specialization; no inference that every HLS agent is a technician. |
| Task type (r), request (i) | Competence/task requirement and individual problem | **APPROXIMATE/CONDITIONAL**: task-type skill demand can be represented as a discrete HLS task catalog, but a CHT request is an indivisible job with its own service time. |
| Experience (q^k_{rt}) | Agent-task latent state (X_t) | **EXACT** if HLS state explicitly stores integer per-agent/per-task counts and starts positive. It is not MIS-v2 normalized competence. |
| Assignment (x^k_{it}) | Allocation (A_t) | **EXACT** only if HLS feasible actions assign each request once and preserve daily service-time capacities. |
| Learning transition Eq. (5) | Action-dependent transition (X_{t+1}=F(X_t,A_t)) | **EXACT** under the assignment-count transition; no independent development decision. |
| Random next-day requests | Exogenous environment (W_{t+1}) | **EXACT** if demand law and reveal timing are preserved. |
| (d^k_{rt}) | Service-time/productivity law | **CONDITIONAL**. Reciprocal productivity (1/d=Dq/(q+L)) equals the scalar Nembhard Direct curve with asymptote (k=D), prior experience (p=0), experience-scale (r=L), and exposure (D_{HLS}=q). This curve identity does not by itself map HLS production, work units, resource feasibility, or costs. |
| Daily capacity (Y) | Resource constraint | **NOT EXACT in current N×K semantics** unless the HLS adapter defines the resource as sum of task-specific service times, not current effort/budget semantics. |
| Minimize expected cumulative service time | HLS objective (J) | **EXACT** if reward is defined as (-C), with no extra CES/quality or terminal terms. |
| Current demand + known experience/parameters | Decision information (I_t) | **EXACT** under full tracking and same demand reveal protocol; no unknown parameter estimation. |
| ADPBF / ADPOL decision rules | HLS admissible policies | **EMBEDDABLE** when their fitted coefficients/forecast state are included in policy memory and all actions/information match; approximation quality is not an equivalence of optimal values. |

**Conclusion on Chen → HLS:** Chen’s model is an exact special case of the broad HLS-RQ0 controlled-process template only after that template is instantiated with its own assignment, transition, demand, capacity and cost definitions. It is not an exact reproduction by the currently implemented HLS N×K runner. The scalar Nembhard-inspired productivity curve can represent the inverse CHT service curve with (p=0), (k=D^k_r), (r=L^k_r), but the HLS runner’s output law (y=\sum_i e_{ik}P_{ik}\Delta t), experience increment (e\Delta t), and effort/resource contract are not Eq. (2)–(6). The explicit adapter would need to preserve discrete requests, service-time feasibility, and total service-time reward; simply setting these parameters in the existing runner would not be faithful.

### 6.2 Reverse mapping HLS → Chen

**INFERENCE.** A restricted HLS submodel can be embedded in CHT if it uses: positive integer experience; a separable per-agent/per-task productivity curve that is exactly (Dq/(q+L)); one-unit experience per assigned request; no forgetting, transfer, teaching, or separate training action; indivisible requests; CHT’s daily service-time capacity; known parameters and current-day demand; and negative cumulative service time as the objective. This is a narrow submodel, not generic HLS.

General HLS-RQ0 is not reducible to CHT without changing semantics where it allows non-CHT competence transition laws (including explicit MIS-v2 learning, teaching/development decisions, transfer, or other capability state), different information structures, arbitrary rewards/terminal values, or action/resource spaces not expressible as daily technician schedules. CHT has no independent (D_t) control, no estimated capability state, and no latent unknown learning parameters in its stated optimization model.

## 7. Strong-SEP: exact relation and non-implications

### 7.1 CHT’s strong-SEP restriction, if instantiated

Canonical HLS strong-SEP is defined in `docs/theory/rq0_routing_integration_boundaries.md`, §§1–4: routing must be immediately reward-greedy at every positive-probability on-policy history; conditional on route and realized development opportunity, development is optimized exactly. In CHT, set (R_t=-C_t), and define the current-day greedy assignments

\[
G_{CHT}(s_t)=\arg\min_{a\in A_t(s_t)} C(s_t,a).
\]

Because CHT has no separately controllable development action, experience transition is forced by the assignment. The conditional development subproblem is therefore a singleton/deterministic transition, optimized trivially. This yields a legitimate *CHT-instantiated strong-SEP restriction*:

\[
\Pi^{CHT}_{SEP}=\{\pi:\delta_t(s_t)\in G_{CHT}(s_t)\text{ at each on-policy history}\}.
\]

Its value must optimize the entire expected horizon among all policies satisfying that per-day greediness condition. It is not just the trajectory generated by one tie-breaking greedy heuristic.

### 7.2 ADPOL and ADPBF membership

ADPOL is not, by definition, an element of Π_SEP^CHT: its action minimizes current cost **plus** a forecast next-day term, so it may choose a current-day non-greedy assignment to improve experience/next-day cost. The paper does not prove whether its selected actions happen to be current-cost greedy in any particular state or all test instances. Thus **universal membership is not established; it is not a valid stand-in for optimized strong-SEP**.

ADPBF likewise minimizes current cost plus a nonzero continuation approximation and may choose non-greedy assignments. It is a candidate in the unrestricted joint finite-horizon policy class under the CHT embedding, but it is not the exact optimizer: it is a parameterized approximate policy. It belongs to Π_HLS when the environment, action set, and information are mapped as above; this says only admissibility, not optimality.

### 7.3 What the ADPBF advantage says about RQ0

The paper’s comparison is between ADPBF and ADPOL. Both are dynamic, daily reoptimization methods. ADPOL has one-day continuation; ADPBF estimates longer-horizon continuation. Neither is “best fixed,” and neither is shown to equal the HLS strong-SEP maximum. Thus

\[
J_{ADPBF}<J_{ADPOL}
\]

in expected service-time cost on the reported test design does not imply a strict HLS gap (J_{HLS}>J_{SEP,max}). It does show that a longer-horizon approximate policy can outperform a particular shorter-horizon heuristic in this model and generated demand regime. The canonical HLS set-inclusion theorem and strictness criterion remain exactly as stated in `rq0_routing_integration_boundaries.md`, Theorems 1–2. CHT neither proves nor refutes the intersection condition Π_H^* ∩ Π_SEP ≠ ∅ for its own fully specified instance class.

SEP-Ω could be defined in the CHT world as a separated implementation whose routing component receives exact action-conditioned continuation values from the same Bellman recursion. If it solves Eq. (7) exactly, its value equals the joint optimal value by construction. This is a proposed definition/identity under exact solution, not a result computed in CHT. CHT’s ADPBF is not SEP-Ω; it approximates the value, and it is not a separated immediate-greedy router.

## 8. Relation to existing HLS results

| HLS result | Relationship to CHT | What CHT does not establish |
|---|---|---|
| **RQ0** | Directly related finite-horizon assignment with action-induced experience and continuation value. CHT is an informative model in which to instantiate the HLS policy-class test. | No comparison against globally optimized Π_SEP, hence no direct strong-SEP gap result. |
| **G3** | **Structural analogy:** current assignments alter future skill-specific experience and therefore future assignment cost. Both expose assignment sensitivity. | No proof of G3’s exact MIS-v2 development-value identity; CHT’s rational learning curve, scheduling constraints, and objective differ. |
| **G3-H** | CHT explicitly has future stochastic task opportunities and heterogeneous learning/productivity. It demonstrates computationally that continuation-valued assignment is useful against ADPOL on its test design. | Does not prove G3-H’s exact ranking reversal or general future-opportunity theorem; nor establish that future opportunities are the only causal mechanism. |
| **C1** | CHT uses a cost-to-go approximation rather than only a local development bonus. Appendix A also warns that aggregate experience need not monotonically order value. | Does not test or formally falsify the specific HLS C1 shortcut. Its aggregate-per-technician basis is an approximation choice, not an exact sufficient statistic. |
| **C2** | Eq. (7) is the standard finite-horizon Bellman recursion; ADPBF approximates its continuation term using a post-decision value (Eqs. (8)–(10)). | Does not make approximate CHT coefficients equal to an exact HLS lookahead solution or prove the C2 reduction for other HLS worlds. |
| **E1** | Both feature experience-dependent productivity, but their operational laws and allocation baselines differ. CHT uses (d=(Dq/(q+L))^{-1}), daily indivisible jobs, capacity Y, and known parameters. | E1’s HLS-adapted exposure/output convention is not CHT; E1 does not reproduce CHT’s ADPBF/ADPOL result. |
| **E2.1** | CHT offers a contrast: each technician has task-specific experience, but daily capacity couples assignment choices across tasks; demand has many task types and stochastic realizations. | E2.1’s separable two-skill endpoint argument does not cover CHT’s capacity-coupled, multi-request daily scheduling. CHT’s experiment is not a proof that every coupled model needs dynamic reassignment. |

CHT Appendix A, Examples A.1–A.3 (Tables 2–8, pp. 131–132) specifically demonstrates counterexamples to monotonicity/convexity of the *optimized total service-time value* in aggregate experience summaries at individual, total, and task-aggregate levels. This supports retaining a richer true state than a single pooled experience number; it does not prove that the paper’s (K+1)-feature approximation is invalid, only that its feature map is lossy and must be judged empirically.

## 9. ESTABLISHED / REDUCIBLE / OPEN

### ESTABLISHED

1. **CHT model fact:** known heterogeneous task-specific parameters; positive-count task-specific cumulative experience; deterministic assignment-induced experience transitions; stochastic future customer requests revealed day by day; daily capacity feasibility; finite-horizon expected total service-time minimization (pp. 123–125, Eqs. (1)–(7)).
2. **CHT algorithm fact:** ADPBF uses a time-dependent linear post-decision approximation with per-technician aggregate experience features, trained offline via approximate value iteration/recursive least squares (pp. 125–126, Appendix B, pp. 132–134).
3. **CHT baseline fact:** ADPOL is a rolling daily optimizer with an exponentially smoothed next-day forecast, α=0.9, not a static allocation or purely myopic greedy policy (pp. 126–127, Eqs. (11)–(15)).
4. **CHT computational fact:** across the reported generated test instances, ADPBF eventually beats ADPOL in average daily service time, but loses early; diversity and availability shape the observed gap. Statistical uncertainty is not quantified (pp. 127–130, Figs. 1–5).
5. **HLS fact:** the HLS policy-class inclusion and finite exact strictness criterion are proven for the canonical common-world contract in `rq0_routing_integration_boundaries.md`, Theorems 1–2. They do not depend on CHT.

### REDUCIBLE

1. Under the explicit mapping in §6.1, CHT is a special case of the broad finite-horizon HLS controlled-process formulation; this requires adopting CHT’s service-time resource and objective semantics rather than assuming the existing N×K runner already has them.
2. Under (p=0), asymptote (k=D^k_r), scale (r=L^k_r), and experience variable equal to positive integer (q^k_{rt}), the reciprocal of CHT’s service-time curve is the Nembhard Direct scalar productivity curve. The surrounding assignment, service-time capacity, and cost formulation still require a faithful adapter/model instance.
3. A CHT-specific strong-SEP policy class can be defined by restricting each day’s assignment to the current-service-time minimizers; exact development is vacuous because Eq. (5) is forced by assignment. Its globally optimized value is not reported in CHT.

### OPEN

1. **Does CHT’s scheduling MDP have a strict joint-versus-strong-SEP gap?** Compute or bound the exact value of Eq. (7) and the globally optimized policy value under (a_t\in G_{CHT}(s_t)), under identical initial state, demand law, capacity, and information. Positive gap requires that no unrestricted optimal policy be immediate-cost greedy on its own support (HLS Theorem 2); equality would show strong-SEP suffices for that instance/class. The minimum evidence is one exact finite instance with a proof/certified DP value, plus a null case; broad claims require structural conditions.
2. **How much of the reported ADPBF–ADPOL gap is due to horizon length versus approximation/training choices?** A controlled algorithmic analysis would compare against an exact or certified small-instance Bellman solution and isolate initialization/basis effects. CHT has no such ablation. This is secondary to the RQ0 class question.
3. **Is aggregate technician experience adequate for decisions in relevant regimes?** Appendix A shows it is not a monotone sufficient statistic in general, but does not quantify approximation error of the chosen basis. A minimum answer needs exact small-instance values where states share basis features but have different optimal continuation values, and a bound/measurement of induced policy loss.

## 10. Recommended next scientific action

**PROPOSAL — Derive and solve the CHT strong-SEP restriction on a small, exactly solvable CHT instance class before any reproduction campaign.** Keep the article’s Eq. (1)–(7), discrete assignment, positive experience, daily capacity, demand law, objective, and information timing. Compare:

1. exact unrestricted Bellman optimum;
2. globally optimal policy constrained to choose only current-day cost-minimizing assignments at every visited state (including all greedy ties);
3. ADPBF and ADPOL only as algorithmic references if their exact published procedures can be reconstructed.

This is the closest direct test of the HLS question. It does not require a new learning mechanism or claim ADP is optimal. A positive exact gap would establish one CHT-structured existence case; a zero gap would identify a strong-SEP-sufficient boundary. Neither outcome alone establishes prevalence or generality. The paper’s 120-day/50-request instances are not required for this mathematical reference calculation.

## 11. Final answer to the PI’s question

Mathematically, CHT shows how **current assignment determines future task-specific experience**, and how a finite-horizon scheduler can trade current service time against a continuation value because future demand is stochastic and experience reduces later service times. Their reported ADPBF advantage is over a particular rolling one-day forecast policy, with the gain concentrated after an early workforce-positioning period in their generated 120-day workloads.

What it does **not** show is that any adaptive policy beats the best immediate-greedy/conditional-development strong-SEP policy. CHT’s benchmark already adapts assignments daily and uses one-step continuation; its proposed ADP is an approximate longer-horizon optimizer, not an online learner of unknown productivity. To connect the published result to HLS-RQ0, the mathematically decisive comparison is not ADPBF versus ADPOL but unrestricted optimal value versus the *optimized CHT strong-SEP policy class* under the exact same physical model, information and objective.

## 12. References

1. Chen, X., Hewitt, M., & Thomas, B. W. (2018). “An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers.” *International Journal of Production Economics*, 196, 122–134. DOI: [10.1016/j.ijpe.2017.10.028](https://doi.org/10.1016/j.ijpe.2017.10.028). Equations (1)–(15), printed pp. 124–127; Figs. 1–5, pp. 127–130; Appendix A, Examples A.1–A.3/Tables 2–8, pp. 131–132; Appendix B/Eqs. (16)–(20), pp. 132–134.
2. Chen, X., Thomas, B. W., & Hewitt, M. (2017). “Multi-period technician scheduling with experience-based service times and stochastic customers.” *Computers & Operations Research*, 82, 1–14. DOI: [10.1016/j.cor.2016.12.026](https://doi.org/10.1016/j.cor.2016.12.026). CHT18 cites it as the source of the repeated problem formulation and ADPOL benchmark; this report does not treat that separate paper as independently audited.
3. Nembhard, D. A., & Osothsilp, P. (2005). “Learning and forgetting-based worker selection for tasks of varying complexity.” *Journal of the Operational Research Society*, 56(5), 576–587. CHT18 uses its learning-curve family and empirical parameter data (printed pp. 124, 126; Table 1).
4. HLS, [`research_questions.md`](../research_questions.md), RQ0; [`rq0_routing_integration_boundaries.md`](../theory/rq0_routing_integration_boundaries.md), §§1–10, Theorems 1–2; [`HLS_DYNAMIC_THEORY.md`](../theory/HLS_DYNAMIC_THEORY.md), §§2–7; [`HLS_G2_DYNAMIC_GROUND_TRUTH.md`](../theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md); [`HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`](../experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md), §§1–12; [`HLS_E2_1_PROTOCOL.md`](../experiments/HLS_E2_1_PROTOCOL.md).
