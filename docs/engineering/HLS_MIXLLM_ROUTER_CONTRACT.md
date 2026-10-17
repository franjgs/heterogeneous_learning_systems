# HLS contextual quality–cost router contract

**Version:** HLS adaptation specification 0.1

**Status:** specified; not implemented; no campaign authorized

**Recorded:** 2026-10-17 (Europe/Madrid)
**Scope:** one query, a finite set of feasible execution candidates, contextual predictions of expected quality and monetary cost, and updates from the selected candidate's observed outcome.

This is an implementable HLS mechanism inspired by selected components of MixLLM. It is **not a reproduction** of MixLLM: the selection objective below, the simple predictor, the quality/cost contract, and omitted queue term differ from the article's trained router and experimental setting.

### Original mechanism versus HLS proposal

The local source audit transcribes MixLLM's selection score (paper equations 7–11) as

\[
s_i(q)=\frac{\lambda}{\lambda+1}\widehat p_i(q)
-\frac{1}{\lambda+1}\widehat c_i(q)
+\alpha\,\phi(q)^\top A_i^{-1}\phi(q)
-\beta\exp\{\gamma(w_i-\xi\tau)\},
\qquad i^*=\arg\max_i s_i(q).
\]

There, predicted quality and token expenditure, an uncertainty term, and a model waiting-time penalty contribute to a weighted score; the paper also describes trained predictors and online updates. The HLS contract instead uses a quality target and minimizes predicted monetary cost, with a maximum-quality fallback. It does not import the MixLLM score, token-cost equation, waiting penalty, or predictor training procedure. The source basis is Wang et al. (2025), NAACL proceedings version, BibTeX key `wang2025mixllm`, DOI `10.18653/v1/2025.naacl-long.545`; local PDF `docs/literature/cross_cutting/Wang_et_al_2025_MixLLM_Dynamic_Routing.pdf`, SHA-256 `b0881cf583c83a84566b85584d1a2f57f3c356b891a952b657aa0f8140473659`. The equation transcription and scope are also recorded in `docs/literature/audits/HLS_ROUTING_AUDIT_2026-10-17.md`.

## 1. Scientific separation

At query time, the environment has candidate-specific outcome distributions that are not available to the router. For candidate (i) and query (q), let the latent expected outcome be

\[
Q_i(q)=\mathbb E[Y_i\mid q,i]\in[0,1],\qquad
C_i(q)=\mathbb E[Z_i\mid q,i]\geq 0,
\]

where (Y_i) is observed quality and (Z_i) is observed monetary expenditure. These latent expectations are environment quantities. The router has estimates \(\widehat Q_i(q),\widehat C_i(q)\), obtained from declared priors and outcomes it has actually received. An unselected candidate's counterfactual outcomes are never supplied to the router.

Quality is an outcome rating under a versioned evaluator/rubric, not competence, productivity, CES, or utility. Cost is **direct monetary operating expenditure per query**, measured in one declared currency (for the first implementation, a run must use exactly one currency and a frozen price/accounting version). It is not latency, energy, HLS effort, resource capacity, or a weighted combination of them. A domain without a defensible monetary meter cannot use this cost contract without an explicit later revision.

## 2. Query and candidate contracts

### `QuerySpec`

- `query_id: str`: unique within the replay/evaluation dataset.
- `context: tuple[float, ...]`: finite vector under a versioned feature schema and fixed preprocessing transform. Every component must be available before selection and independent of candidate outcomes. It must not encode the best candidate, a future label, or post-execution information.
- `quality_requirement: float`: target \(Q_{\min}(q)\in[0,1]\). In v0.1 it is a **selection target**, not a guaranteed lower bound on realized quality; observed quality is stochastic and the fallback rule can choose below it.
- `cost_budget: float | None`: optional maximum predicted monetary cost in the run's declared currency. It filters candidates using predicted cost; it does not guarantee the realized invoice is below budget. A hard spend cap requires a candidate-side reservation/maximum-cost guarantee before execution.

The context feature dimension and transform are fixed for a run. Query IDs are provenance keys only and must not be model features.

### `CandidateSpec`

- `candidate_id: str`: unique stable identifier; lexical order is the final tie-break.
- `resource_constraints`: optional declared pre-execution feasibility/availability constraints. These may filter a candidate but contain no outcome labels.
- `metadata`: optional descriptive, decision-visible metadata with a versioned schema.

It must not contain true or predicted quality/cost as candidate facts. Priors and predictor state are separate router-owned objects. At decision time, the caller supplies a public availability/resource snapshot; a deterministic feasibility check `(candidate, query, snapshot) -> feasible/infeasible` filters candidates before score-based routing. This check may use declared capacity/reservation constraints but no outcome information. A candidate is a query-serving system; it is not inherently an HLS agent, an HLS competence, or an LLM. A particular application may map an HLS agent to a candidate only if the query, outcome, constraints, and cost meanings are explicitly aligned. No such mapping is made by this contract.

At each decision the router receives a finite ordered candidate set and a feasibility result based only on declared, pre-execution constraints. An empty feasible set returns `NO_FEASIBLE_CANDIDATE` without execution.

## 3. Environment execution and feedback

Conceptual interface:

```text
execute(candidate_id, query_id, query_payload)
    -> ExecutionOutcome
```

`ExecutionOutcome` contains:

- matching `query_id` and `candidate_id`;
- `observed_quality: float | None`, in [0,1], if the declared evaluator returned a valid rating;
- `observed_cost: float | None`, finite and nonnegative, in the declared currency, if the billing/accounting meter reported it;
- optional diagnostic metadata and an execution status.

The environment may internally know true conditional distributions, but it exposes only the selected execution outcome after the call. It must not provide outcomes for unselected candidates. A failed run can still report cost. Missing quality is **not** silently converted to zero: it updates neither quality model nor its quality count. If domain rules define failure as quality zero, that rule and evaluator version must explicitly emit `observed_quality=0`. Cost and quality feedback update independently. If cost is absent, the cost model is unchanged. Delayed feedback, if later supported, updates when received and is timestamped; v0.1 assumes immediate feedback for the current query before the next decision.

## 4. Contextual prediction and online update

Use a fixed feature map \(\phi(q)=\operatorname{FeatureMap}(q.context)\), whose schema, normalization, and version are frozen before evaluating held-out queries. It includes an intercept for general numeric features; a fully one-hot categorical representation may omit a redundant intercept. For each candidate \(i\), maintain separate quality and cost ridge-regression states. For outcome type \(r\in\{Q,C\}\), state is sufficient statistics \((A_i^r,b_i^r,n_i^r)\), with positive regularizer \(\lambda_r>0\) and a declared prior coefficient vector \(\beta_{0,i}^r\):

\[
A_i^r=\lambda_r I+\sum_{s\in\mathcal H_i^r}\phi_s\phi_s^\top,
\quad
b_i^r=\lambda_r\beta_{0,i}^r+\sum_{s\in\mathcal H_i^r}\phi_s y_s^r,
\quad
\widehat\beta_i^r=(A_i^r)^{-1}b_i^r.
\]

\(\mathcal H_i^Q\) and \(\mathcal H_i^C\) contain only observed feedback for actual executions of candidate \(i\). The prediction and update are:

\[
\widehat Q_i(q)=\operatorname{clip}_{[0,1]}(\phi(q)^\top\widehat\beta_i^Q),
\qquad
\widehat C_i(q)=\max(0,\phi(q)^\top\widehat\beta_i^C).
\]

An observed quality adds \((\phi,Y)\) to the quality sufficient statistics; observed cost adds \((\phi,Z)\) to cost statistics. No other model is updated. This is an online regularized linear predictor, not MixLLM's trained predictor architecture or its published update procedure. Clipping and linearity can bias predictions; report this as a model limitation and validate predictions separately from routing outcomes.

**Initialization:** each candidate must have explicit prior vectors \(\beta_{0,i}^Q,\beta_{0,i}^C\) of the correct dimension and a declared source (for example, a training split or a deliberately common uninformative prior). A candidate with no observations uses its prior prediction and reports count zero / `PRIOR_ONLY`. Do not silently infer priors from true candidate performance or held-out outcomes. Training data, preprocessing fit, and evaluation queries must be separated by a frozen split; online updates during an episode use only earlier selected-candidate feedback.

**Uncertainty/evidence:** expose per-candidate counts separately for quality and cost. A basic leverage diagnostic \(\phi^\top A^{-1}\phi\) and residual dispersion may be reported when defined; they are not asserted to be calibrated confidence intervals and do not enter the v0.1 decision score. Unobserved candidates are explicitly marked `PRIOR_ONLY`. MixLLM's uncertainty bonus is therefore not implemented by this contract.

## 5. Selection rule

First filter the supplied candidates by their pre-execution feasibility constraints. If a query has budget \(B(q)\), further retain candidates satisfying \(\widehat C_i(q)\leq B(q)\). If none remain, return `NO_PREDICTED_BUDGET_FEASIBLE_CANDIDATE`; do not execute an over-budget candidate by fallback.

Let \(F(q)\) be this feasible set and \(E(q)=\{i\in F(q):\widehat Q_i(q)\geq Q_{\min}(q)\}\). With exploration disabled, choose:

\[
i^*(q)=
\begin{cases}
\arg\min_{i\in E(q)}(\widehat C_i(q),-\widehat Q_i(q),\texttt{candidate\_id}_i), & E(q)\ne\varnothing,\\
\arg\min_{i\in F(q)}(-\widehat Q_i(q),\widehat C_i(q),\texttt{candidate\_id}_i), & E(q)=\varnothing.
\end{cases}
\]

Thus the target is **minimum predicted cost subject to predicted quality target**; if no candidate reaches the target, fallback is **maximum predicted quality, then minimum predicted cost**. Candidate ID resolves remaining ties deterministically. This is not P0's functional production rank, CES maximization, nor MixLLM's weighted quality–cost + uncertainty + wait score. The budget is a feasibility filter; minimizing cost remains the objective among quality-eligible candidates.

The query target is not a safety guarantee. Optional \(\epsilon\)-exploration may select uniformly among \(F(q)\), using an independent recorded seed, with probability \(\epsilon\in[0,1]\); this explicitly may select below \(Q_{\min}\), while it never overrides resource feasibility or the predicted budget filter. Decision output must mark `exploratory=true` and the threshold override. Default is \(\epsilon=0\). Exploration is not required for a deterministic router to operate, but selected-only feedback can leave candidates/context regions unobserved and estimates unidentified. If coverage is an experimental requirement, predeclare \(\epsilon\), seed, and whether target overrides are acceptable; do not add an uncertainty bonus implicitly.

## 6. Decision and update sequence

For each query, in order:

1. Validate query schema and candidate IDs; derive \(\phi(q)\) using the frozen transform.
2. Filter pre-execution unavailable/infeasible candidates.
3. Predict quality and cost from current router state; emit the prediction snapshot and evidence counts.
4. Apply predicted budget filter and the rule above; return a structured no-selection status if the feasible set is empty.
5. Execute exactly the selected candidate. The router has no access to counterfactual results.
6. Validate feedback IDs, units, ranges, evaluator/pricing versions; append received observations to history and update only their corresponding predictor.
7. Record post-update state version for the next query.

The state transition is \(\Theta_{t+1}=U(\Theta_t,q_t,i_t,o_t)\), where \(o_t\) contains only feedback actually received. Predictions for period \(t\) are computed from \(\Theta_t\), never from \(o_t\) or outcomes of that execution.

## 7. Minimal numerical example (hypothetical)

Use a full one-hot context feature map (no separate intercept), `X=(1,0)`, `Y=(0,1)`, two candidates A/B, ridge \(\lambda=1\), and the following **hypothetical prior coefficient vectors**:

| Candidate | \(\beta_0^Q=(X,Y)\) | \(\beta_0^C=(X,Y)\), currency/query |
|---|---:|---:|
| A | (0.80, 0.90) | (1.00, 0.90) |
| B | (0.90, 0.70) | (0.70, 0.50) |

For query X with \(Q_{\min}=0.75\), both are predicted to qualify; A costs 1.00 and B 0.70, so select B. Suppose B actually returns observed quality 0.50 and observed cost 0.90. For the X coordinate, the ridge update is \((\lambda\beta_0+y)/(\lambda+1)\): B's quality prediction becomes `(0.90+0.50)/2=0.70`; cost becomes `(0.70+0.90)/2=0.80`. For the next X query with the same target, B no longer qualifies, A still predicts 0.80 and is selected. The observation of B's outcome changes the later routing decision; no A outcome was observed or used.

For context Y, the prior predictions differ: A predicts quality 0.90/cost 0.90, B predicts 0.70/cost 0.50. At \(Q_{\min}=0.65\), both qualify and B is selected. These values are solely a hand-checkable contract example, not HLS measurements or MixLLM results.

## 8. Integration boundary with HLS

**Reusable patterns:** immutable configuration/state objects, explicit decision views and memory, deterministic candidate ordering, independent random streams, replayed exogenous inputs, trace separation, and focused tests. Relevant code is `src/hls/hls_lab_nk_policies.py` (`NKCoordinationPolicy.choose(view, memory, parameters)`), `src/hls/hls_lab_nk_execution.py` (`run_nk_production_sequence`), and `src/hls/hls_lab_nk_nembhard_adaptive.py` (selected-only observation/update sequencing and reproducibility patterns).

**Keep independent:** `ProblemSpecNK` remains a competence-requirement/functional-evaluation object, not a query-quality label; N×K production and CES; MIS-v2 learning; Nembhard state `D`, parameters `k,p,r`, production and ORACLE; `nembhard_adaptive` productivity observations/estimator; HLS agent competence; teaching, P1/P2, and P2 efficacy memory. No existing contract needs to be changed to specify this router. Implementation should use new query/candidate/outcome/state/decision records and a routing-specific runner or adapter, calling no HLS competence or Nembhard productivity in its prediction path.

**Trace fields:** query/context-schema ID, candidate-set/version, selected ID, selection/fallback/exploration reason, \(Q_{min}\), predicted quality/cost and evidence counts for every feasible candidate, budget/currency/pricing version, chosen outcome's observed quality/cost or missingness/failure status, evaluator version, prediction-model version before/after update, seed(s), and run ID. Diagnostic truth or synthetic counterfactuals, if a test environment has them, must be stored in a separate oracle-only channel never passed to the router.

## 9. Acceptance checklist and unresolved decisions

An implementation conforming to this document must test: input validation and candidate identity; quality/cost ranges and currency consistency; all-ineligible and no-budget-feasible cases; target satisfaction and fallback ranking; deterministic ID tie-break; prior-only candidates; independent quality/cost updates; no update on missing feedback; selected-only information boundary; prediction-before-feedback ordering; ridge updates against hand calculations; context-dependent choice; optional exploration/replay; actual budget overrun reporting; and serialization/replay across fresh processes. Tests must use independent expected values, not call the implementation as its own oracle.

The following decisions are **required before a domain instance/implementation**, not blockers to this abstract contract:

1. Actual candidate roster and query/context feature schema, including fixed preprocessing and how schema-version changes invalidate or migrate model state.
2. A blinded/frozen quality evaluator and source of evaluation when no automatic metric exists.
3. The single run currency, price/accounting version, treatment of fixed fees, retries, and failed-run expenditure.
4. Candidate-specific prior vectors, regularization values, and source split; these cannot be estimated from evaluation outcomes.
5. Whether the cost budget is merely a predicted-selection constraint or must be hard-enforced by execution reservation.
6. Whether controlled exploration may override the quality target; default is off.

No scientific-model change, code, test, experiment, or capacity claim is made here. HLS Laboratory remains **PARTIAL**. The original article and equations are documented in the local source audit and reference register; this contract chooses a simpler constrained selector and linear online update, so the label remains “MixLLM-inspired,” never “MixLLM implementation/reproduction.”
