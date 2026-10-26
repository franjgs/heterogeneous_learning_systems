# HLS — CE-04.3 Operational specification proposal

**Date:** 2026-10-26
**Status:** Proposal for CE disposition; **NOT FROZEN**.
**Execution:** documentation and mathematical review only; no code or
experiment run.

This proposal applies the decisions in the CE-04.3 instruction and the
analysis in [08_SPECIFICATION_CLOSURE_REVIEW.md](08_SPECIFICATION_CLOSURE_REVIEW.md).
It does not silently resolve matters reserved to the CE.

## 1. Common admission rule

For a new task arriving at `t`, calculate for every agent `i` the estimated
probability `F̂_i(t)` that appending the task to that agent's FCFS queue will
finish it within its three-unit deadline. Define the common feasible set

`A_t = { i : F̂_i(t) ≥ 0.50 }`.

If `A_t` is empty, reject the task. Otherwise admit it and let the applicable
policy select an agent only from `A_t`. The same threshold, queue state,
service model and `F̂` calculation apply to P0, P1, P2 and P3. The admission
screen does not use competence, so P1 receives no admission advantage from
knowing true `q_ik`. Rejected tasks remain failures in the primary denominator
and produce no correctness labels.

The `0.50` threshold is a fixed chance constraint (“at least an even chance
of meeting the deadline”), not a value tuned on validation or test results.
It is a proposed operational criterion, not a consequence of the current
scientific evidence. The CE must approve it. It prevents adding a task to a
queue whose estimated on-time probability is below one half; it does not
claim to optimize the externality imposed on future tasks.

## 2. On-time probability from observable queue state

All newly arriving tasks have slack `L = deadline − t = 3`. A busy agent has
one active task with observable elapsed service age `a` and `m` queued tasks
ahead of the new task. The new task is appended at the tail. Its completion
time from now is

`R(a) + S_1 + … + S_(m+1)`,

where `R(a)` is the active task's residual service time conditional on it
having run for age `a`, and the `m+1` full service times include waiting tasks
ahead and the new task. If the agent is idle, completion time is just the new
task's `S`. No sampled future service duration or hidden completion time is
used.

For `S ~ LogNormal(μ,σ²)`, use
`σ²=ln(1+0.30²)` and `μ=ln(1.25)−σ²/2`. For `a>0`, conditional raw moments
are available analytically:

`E[S^r | S>a] = exp(rμ + r²σ²/2) · Φ((μ+rσ²−ln a)/σ) / (1−Φ((ln a−μ)/σ))`,

for `r=1,2`; hence `E[R]=E[S|S>a]−a` and
`E[R²]=E[S²|S>a]−2aE[S|S>a]+a²`. At `a=0`, use the ordinary lognormal
moments. Independent full service times have mean `1.25` and variance
`0.140625`.

### Proposed efficient calculation

Use a **Fenton–Wilkinson-style two-moment lognormal approximation** to the
positive sum. The active residual is not itself lognormal, so this applies
the moment-matching idea to its exact conditional moments plus the full-service
moments; it is an explicit approximation, not the classical all-lognormal
case verbatim. Compute the sum's mean `M` and variance `V` by adding the
independent residual and full-service moments. Approximate the sum by a
lognormal with

`σ_sum² = ln(1 + V/M²)`,
`μ_sum = ln(M) − σ_sum²/2`,

then set `F̂=Φ((ln 3−μ_sum)/σ_sum)`. For an idle server, use the exact
single-lognormal CDF (`F̂≈0.999123` at three time units). This is deterministic,
requires no future-time samples and costs constant work per agent once the
queue moments are known.

Fenton–Wilkinson is an approximation, not an exact CDF; its accuracy can be
weak for sums with few terms and in tail regions. Those conditions matter
here because the threshold is a probability boundary and the queue is often
short. Before protocol freeze, verify it against deterministic numerical
convolution over the service ages and queue lengths that can affect the
`0.50` decision. Proposed acceptance criterion: absolute error no greater
than `0.01` for probabilities in `[0.45,0.55]`; if it fails, use the
deterministic convolution value for policy decisions. Do not recalibrate the
approximation from experiment outcomes. Fenton's original approximation is
identified in the references below.

## 3. P1/P2 operational rule

Within the common feasible set `A_t`, use the same score and tie rule:

`score(i,k,t) = q_est(i,k) · F̂_i(t)`.

P1 supplies true `q_ik`; P2 supplies the Beta(1,1) posterior mean
`(1+s_ik)/(2+s_ik+f_ik)`. The service factor is common. Competence and service
time remain independent by construction. Fix a common tie rule before freeze.

P2 updates `s_ik`/`f_ik` only when the correctness label for that executed task
is observed at completion. If completion is after the deadline, the task has
already produced a primary-metric failure, but its eventual correctness label
still updates competence when it arrives. The on-time failure is not an
incorrectness label. Rejected tasks provide no label.

## 4. P3: use disjoint LinUCB, not PG-TS

PG-TS is not necessary for this model. The operational reward should be

`Y=1{task completed correctly by its deadline}`, otherwise `Y=0`.

For agent `i`, task family `k`, and the common `F̂_i`, define a four-dimensional
context `x_i = F̂_i e_k`, where `e_k` is the one-hot vector for task family
`k`. Give each agent its own parameter `θ_i=(q_i1,…,q_i4)`. Under the approved
independence of correctness and service time,

`E[Y | i,k,queue state] = q_ik · F_i`.

With exact `F_i`, this is a disjoint linear contextual-bandit model; with
`F̂_i`, the approximation error is bounded by the error in `F̂`. The reward
is the exact primary success-on-time indicator. Agent identity is inherent in
the action; no primary-specialty label or true competence is exposed to P3.
Queue load enters through the observable queue-derived `F̂_i`. P3 gets no
feedback for unselected agents or rejected tasks.

Use the established disjoint LinUCB score for each feasible agent:

`UCB_i = x_iᵀ A_i⁻¹b_i + α √(x_iᵀ A_i⁻¹x_i)`,

initialized with `A_i=I_4`, `b_i=0`, and fixed
`α=1+√(ln(2/0.05)/2)≈2.358` from the repository's `alpha_from_delta(0.05)`
helper. Choose the feasible agent with highest UCB. Do not clip UCB scores;
they are ranking indices, not probabilities. Log the sampled contexts,
decision time and updates. P3 uses no competence labels, future state or
counterfactual reward.

This recommendation is justified by the model mapping, not code availability:
binary `Y` is a bounded reward and the expected on-time success is linear in
`x_i` with coefficient `q_i`. It is simpler than fitting a logistic
posterior, and the arm/context dimension is four regardless of N. The
existing `LinUCBDisjoint` implements the disjoint linear-UCB equations and
selected-arm feedback. However, it blocks a new selection until feedback is
observed, while CE-04 can have several assigned tasks awaiting completion.
Implementing P3 will therefore need a thin delayed-feedback adapter: retain
`(agent, task-context)` by task id, permit intervening decisions using the
current `A_i,b_i`, and apply the additive update
`A_i←A_i+x_ix_iᵀ`, `b_i←b_i+Yx_i` once that task's reward becomes observable.
This changes the feedback interface, not the LinUCB decision rule. Tie
breaking must be reproducible and shared in definition across policies.

The reward `Y` becomes observable at task completion if it is on time, or as
zero at its deadline if it is late; the task may continue running and its
later correctness is not a second P3 reward. This is delayed selected-action
feedback with maximum delay three for `Y`. P2 may receive the separate
correctness label later. Both policies must receive the same operational
event stream as each event becomes observable; each may update only its own
declared target. Delayed feedback and state-dependent contexts mean the
standard immediate-feedback regret guarantees should not be claimed for this
adaptation.

PG-TS is a published method for binary logistic contextual rewards, but its
Pólya–Gamma Gibbs posterior sampling is substantially more work than needed
for the exact linear expectation above. A later GLM-bandit comparison reports
PG-TS's high online complexity; its posterior model would also impose an
unnecessary logistic form here. No HLS-specific algorithm is required.

## 5. Costs, validity and remaining freeze gates

- **Exploration cost:** collective success-on-time already captures the
  outcome cost of exploratory assignments. Also log per-decision CPU/wall
  time, p50/p95 decision latency, number of LinUCB updates and the fraction of
  choices where the UCB winner differs from the posterior/least-squares mean
  winner. That fraction is descriptive, not a causal cost estimate.
- **Decision cost:** measure it separately from service time and include it
  in CE-04's declared secondary measures.
- **Queue externalities:** all policies make one-task assignments from the
  current queue state. P1/P2 and P3 optimize/estimate the same immediate
  success-on-time reward, but none is a globally optimal queue-control policy.
  Interpret results at this policy scope.
- **Numerical blocker:** Fenton–Wilkinson accuracy near the admission cutoff
  must meet the stated tolerance or be replaced by deterministic convolution.
- **Policy blocker:** the CE must approve the admission threshold, the P3
  delayed-feedback adapter and a shared tie rule.
- **Other open operational items:** the consolidated protocol §8 still lists
  interpretation of `0.55` arrivals per agent, phase-boundary convention,
  time semantics, endpoint/drain for tasks whose deadlines extend beyond the
  400-unit arrival horizon, cost units, random-stream mapping, and the
  statistical resampling/contrast family. This instruction does not resolve
  those items.

**Recommendation: NO CONGELAR.** The proposed admission, completion-probability
calculation and LinUCB P3 are concrete and compatible with the CE's core
objective. Freeze should wait for CE disposition of the fixed `0.50` chance
constraint, validation of the probability approximation, delayed feedback and
tie semantics, and the still-open §8 operational definitions. No experiment
or implementation is authorized by this assessment.

## References and repository evidence

- Fenton, L. F. (1960). “The Sum of Log-Normal Probability Distributions in
  Scatter Transmission Systems.” *IRE Transactions on Communications
  Systems*, 8(1), 57–67. [DOI: 10.1109/TCOM.1960.1097606](https://doi.org/10.1109/TCOM.1960.1097606).
- Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010). “A Contextual-Bandit
  Approach to Personalized News Article Recommendation.” *WWW 2010*.
  [Full text](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/p661.pdf).
- Dumitrascu, B., Feng, K., & Engelhardt, B. E. (2018). “PG-TS: Improved
  Thompson Sampling for Logistic Contextual Bandits.” *NeurIPS 2018*.
  [Proceedings](https://papers.neurips.cc/paper_files/paper/2018/hash/ce6c92303f38d297e263c7180f03d402-Abstract.html).
- Ding, Q., Hsieh, C.-J., & Sharpnack, J. (2021). “An Efficient Algorithm for
  Generalized Linear Bandit: Online Stochastic Gradient Descent and Thompson
  Sampling.” *AISTATS / PMLR 130*, 1585–1593. Its analysis discusses the
  computational cost of logistic PG-TS and online generalized-linear methods.
  [Proceedings and paper](https://proceedings.mlr.press/v130/ding21a.html).
- Repository implementation inspected: [`src/hls/linucb.py`](../../../src/hls/linucb.py)
  (`LinUCBDisjoint`, `alpha_from_delta`) and
  [`src/hls/hls_lab_nk_linucb_assignment.py`](../../../src/hls/hls_lab_nk_linucb_assignment.py)
  (`PairwiseLinUCBAdapterNK`). The latter is a batch N×K feedback adapter and
  is not directly the sequential delayed-feedback adapter CE-04 needs.
