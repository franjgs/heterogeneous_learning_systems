# CE-04.2 — Technical review of proposed specification closure

**Assessment date:** 2026-10-26
**Status:** CE decision proposal; protocol remains **NOT FROZEN**.
**Scope:** mathematical and operational evaluation only. No code or experiment was run.

This review evaluates the proposed values and mechanisms against the CE-04
record, the four expert reports and `RESEARCH_DOCTRINE.md`. It does not adopt
them on behalf of the CE. See [the consolidated pre-freeze protocol](06_CE04_CONSOLIDATED_PROTOCOL.md)
for the currently controlling design and its other unresolved semantics.

## A. H0–H2: exact mean-preserving construction

Let the four agent families be balanced, with exactly `N/4` agents in each
primary family. For agent `i` whose primary family is `g(i)`, set

`s_ik = 0.75` when `g(i)=k`, and `s_ik = -0.25` otherwise, and define
`q_ik = 0.775 + α_H s_ik`.

For every task family `k`, one quarter of agents have `s_ik=0.75` and three
quarters have `s_ik=-0.25`. Therefore

`mean_i(s_ik) = (1/4)(0.75) + (3/4)(-0.25) = 0`,

so `mean_i(q_ik)=0.775` exactly for H0, H1 and H2. This holds for every
`N ∈ {12,24,48}`, since all three sizes are divisible by four. No rounding or
truncation is needed.

| Composition | α | Primary-family competence | Other-family competence | Across-agent SD for each task |
|---|---:|---:|---:|---:|
| H0 | 0.00 | 0.775 | 0.775 | 0 |
| H1 | 0.10 | 0.850 | 0.750 | 0.04330 |
| H2 | 0.20 | 0.925 | 0.725 | 0.08660 |

All entries lie in `[0,1]`; the extrema are 0.725 and 0.925. The variance
across agents for a task is `0.1875 α²`, so dispersion increases strictly
from H0 to H2. Each agent's four-task mean is also 0.775. The construction
therefore changes the distribution and specialization while preserving both
the task-wise population mean and the agent-wise mean over an equally weighted
task set. It does not preserve the best specialist's competence, nor should
it: that is a consequence of the proposed heterogeneity treatment, not a
separate benefit imposed by changing the mean.

The “four balanced families” in H0 are labels only: when `α=0`, they do not
distinguish competence. Whether these family labels are observable to P2/P3
must be decided explicitly; exposing them would reveal information correlated
with the generating competence profile.

**Assessment:** the proposed generator is mathematically coherent and closes
the exact-mean and divisibility questions if adopted unchanged. It is a
proposed construction, not an established HLS result.

## B. Service times, offered load and deadlines

For a lognormal service time with mean `m=1.25` and coefficient of variation
`CV=0.30`, the log-space parameters are

`σ² = ln(1+CV²) = ln(1.09) ≈ 0.086178`,
`σ ≈ 0.293560`,
`μ = ln(m) - σ²/2 ≈ 0.180055`.

These times are independent of `q_ik`, so no composition receives a direct
speed advantage. If the stated arrival intensity means total rate
`λ_N=0.55N`, aggregate offered service capacity is `N/m=0.8N` tasks per time
unit. Nominal utilization is therefore

`ρ = λ_N m/N = 0.55 × 1.25 = 0.6875`,

independent of N under proportional scaling. The service-time-only probability
of finishing within three units from an idle server is approximately
`P(τ≤3)=0.99912`; this excludes all waiting.

As a diagnostic only, under stationary Poisson arrivals independently split
uniformly across workers, infinite FCFS queues and identical service laws,
each worker is an M/G/1 queue. Pollaczek–Khinchine gives

`E[W_q] = λ E[τ²]/(2(1-ρ)) ≈ 1.49875`,

because `E[τ²]=(1+CV²)m²=1.703125` and per-worker `λ=0.55`. Mean response
time is then approximately `2.74875`, close to the three-unit deadline. This
is not a prediction for the proposed nonstationary, state-dependent routing
policies: class mix changes over time, and informed policies can concentrate
load. It shows that queueing cannot be ignored and deadline feasibility is
not established by the high service-only probability.

**Assessment:** the times are a clean control for isolating competence
heterogeneity, but the deadline is potentially binding once waiting is
included. The CE must decide whether the intended rate is indeed `0.55N`, and
freeze queue/admission and deadline semantics before this load calculation
can be treated as the experiment's model.

## C. Common P1/P2 decision rule

For task `n` of family `k`, arriving at time `t` with deadline `d_n=t+3`, let
`A_t` be the same feasible-agent set for P1 and P2. The proposed common rule is

`i*_t = argmax_{i∈A_t} q_t(i,k) · F_i(t,d_n)`,

where `q_t(i,k)=q_ik` for P1 and `q_t(i,k)=q̂_ik` for P2, and
`F_i(t,d_n)` is the probability that service completes by the deadline under
the queue state observable at decision time. If correctness and service time
are conditionally independent as proposed, this score is the estimated
probability of a correct, on-time result. Tie-breaking must be fixed and
identical for P1/P2.

For an agent with no active or queued work, `F_i` is the lognormal CDF at
`d_n-t`. With a per-agent FCFS queue, it is the probability that the sum of
the active job's residual time, service times of jobs ahead, and this task's
service time is at most `d_n-t`. If the active service duration is not
observable, its residual distribution must be conditioned on elapsed service
age; using the simulator's hidden sampled completion time would leak future
information. Future service times for queued jobs must be integrated over the
stated service law. A sum of lognormals has no general closed-form CDF, so a
deterministic numerical method and error tolerance must be fixed before use.

This is one common decision rule with different competence inputs, not two
policies. It is an operational proposal, not a published algorithm. It
prioritizes expected on-time correctness; service cost is constant under the
proposed service model, while decision and operating costs remain measured
outcomes rather than an extra score term.

The current documents do not settle whether arrivals join busy agents' queues,
what queue capacity is, when a task is rejected, whether work continues after
its deadline, or whether a late completed answer reveals correctness. These
choices alter `A_t`, `F_i` and the estimator feedback and require CE
disposition. No admission threshold is proposed here.

## D. P2 Beta–Bernoulli estimator

For each agent-task pair, with `s_ik` observed correct outcomes and `f_ik`
observed incorrect outcomes, Beta(1,1) yields

`q̂_ik = (1+s_ik)/(2+s_ik+f_ik)`.

This is compatible with constant competence and selected-action feedback if
each observed correctness label is a Bernoulli draw with fixed probability
`q_ik`, and updates occur only when that label is actually observed. Rejected,
unassigned, or counterfactual outcomes do not update the posterior. A late
task must not be coded as an incorrect competence observation merely because
its on-time reward is zero: lateness and correctness are distinct. If a task is
canceled at the deadline and its correctness is never observed, that sample is
censored and must not update this Beta posterior. If it is allowed to finish,
the later correctness label can update the posterior only after it becomes
available.

Beta(1,1) is a concrete, transparent prior and introduces no use of hidden
competence. It does not pool evidence across agents or tasks; cold-start
coverage may be sparse, especially at N=48. That is a property to measure, not
a reason to change the prior after seeing outcomes. P2's update timing and
the handling of censored/late tasks remain to be frozen.

P2 and P3 should be given the same pre-decision observable state and only
feedback generated by actions each actually selected. Their learning targets
can differ: P2 estimates correctness `q_ik`, while P3 can model the primary
binary reward `Y=1{correct and on time}`. Store the same event record and
availability time for both; never expose a label before it is operationally
observed. The differing targets are an algorithmic distinction, not extra
information for P3.

## E. P3 recommendation: logistic contextual Thompson Sampling

**Recommendation for CE consideration:** use an established logistic
contextual Thompson Sampling method for binary on-time-success reward, rather
than selecting LinUCB because code already exists. A directly relevant
published method is PG-TS, Dumitrascu, Feng and Engelhardt (NeurIPS 2018).
It models binary reward with a logistic link, samples a shared parameter from
its posterior using Pólya–Gamma augmentation, and selects the feasible action
with the largest sampled expected reward. The paper also describes a
one-transition streaming variant (PG-TS-stream); it reports M=100 burn-in for
the fuller sampler as empirically sufficient in its evaluations. These are
published settings, not evidence that either setting is adequate for CE-04.

A concrete starting configuration for CE review is:

- Reward: `Y=1` only if the assigned task is completed correctly by its
  deadline; otherwise `Y=0` once that outcome is observable.
- Action: assign the arriving task to one feasible agent; observe feedback
  only for the selected agent-task pair.
- Context: task-family × agent-identity indicators, plus normalized
  *observable* queued work and normalized time-to-deadline. Do not expose
  latent `q_ik`, future arrivals, future outcomes or simulator-sampled
  completion times. Whether primary-family labels are observable is a CE
  decision; the proposed feature map uses identity and does not require such
  labels.
- Model: shared logistic reward model `P(Y=1|x)=σ(θᵀx)` with an isotropic
  Gaussian prior `θ~N(0,I)` after fixed, predeclared feature scaling.
- Sampling: PG-TS-stream with one Gibbs transition per decision (`M=1`) as a
  computationally modest published variant. Fix the sampler seed stream
  independently from demand, service and outcomes.
- Feasibility: maximize sampled reward only over the same feasible action set
  available to the other policies. Do not use information about future
  availability.

The context uses workload and slack because they affect the on-time reward;
the agent-task indicators allow different competence profiles without
revealing true probabilities. A logistic model is still a modeling
assumption: `q_ik × P(finish on time)` need not be exactly logistic-linear in
these features. Report this as a model limitation, not as a theorem. PG-TS's
posterior updates use only selected-arm binary feedback, consistent with
partial observation. Its exploration randomness and decision computation
must be logged. At minimum record decision CPU/wall time, p50/p95 latency,
posterior draws, memory and the fraction of selections where the sampled
winner differs from the posterior-mean winner. That fraction is descriptive,
not a causal estimate of exploration cost.

**Why not the current LinUCB adapter?** `src/hls/linucb.py` implements the
disjoint linear-payoff UCB score and accepts rewards in `[0,1]`; bounded
Bernoulli rewards are compatible with its noise range only if the conditional
mean is adequately linear in the supplied features. It has no logistic link
and no probability calibration guarantee. The existing
`PairwiseLinUCBAdapterNK` is designed for N×K selected-pair feedback and a
batch of selected pairs; CE-04 is sequential task arrival with queue-state
contexts and would need an adapter and careful information-set checks. It is
technically adaptable, but availability of code alone is not a scientific
reason to prefer it.

E2 cites Agrawal and Goyal (2013), whose published contextual Thompson
Sampling analysis is for linear payoffs with Gaussian prior/likelihood. That
reference establishes the broad mechanism but does not by itself specify a
Bernoulli/logistic reward model. PG-TS is the closer formulation for the
binary on-time outcome. No claim is made that PG-TS is superior for CE-04;
the proposal is based on outcome-model fit and must remain fixed before test
results.

## F. Consistency checks and CE decisions still required

| Check | Assessment |
|---|---|
| H0–H2 task-wise means | Exact at 0.775 for each task and each N, under balanced primary-family counts. |
| H0–H2 probabilities | All lie in [0,1]; strict variance increase is 0, 0.001875, 0.0075. |
| Service-time confounding | None by construction: same lognormal service law, independent of q and family. Queue workload can still differ because policies route differently. |
| P1/P2 rule | Same `q × on-time probability` objective and feasible set; only true vs observed-data competence differs. |
| P2/P3 raw information | Can share task/state/event observables and selected-only feedback; their targets/update delays differ and must be specified. |
| Exploration and decision cost | Record decision CPU/wall time and posterior sampling; exploration rate is descriptive. Its reward opportunity cost is already reflected in collective outcomes; no new policy is added. |
| Metrics and E3 contrasts | Proposed model preserves success-on-time, task/family/phase metrics, factorial cells, pairing and contrast structure. E3's original 27-cell/three-policy design is not the adopted protocol. |
| Queue and deadline semantics | **Unresolved:** queue acceptance/capacity, admission/rejection, cancellation after deadline, residual service observability and feedback availability. These are necessary to define P1/P2 and P3 consistently. |
| Information visibility | **Unresolved:** whether agent-family metadata is observable. The proposed P3 context avoids requiring it, but any implementation must use the same declared observable fields. |

The CE still needs to decide the exact five specifications in §7 of the
consolidated protocol. This review offers concrete candidates for A/B, C, D
and E but does not mark them closed. Queue, deadline, rate interpretation,
phase boundaries, cost accounting, tie-breaking, independent random streams,
and statistical families in §8 also remain open. No pilot or campaign should
start until the CE records those decisions and freezes the protocol.

## References

- Dumitrascu, B., Feng, K., & Engelhardt, B. E. (2018). “PG-TS: Improved
  Thompson Sampling for Logistic Contextual Bandits.” *NeurIPS 2018*.
  [Proceedings paper](https://papers.neurips.cc/paper_files/paper/2018/hash/ce6c92303f38d297e263c7180f03d402-Abstract.html),
  [full text](https://papers.neurips.cc/paper_files/paper/2018/file/ce6c92303f38d297e263c7180f03d402-Paper.pdf).
- Agrawal, S., & Goyal, N. (2013). “Thompson Sampling for Contextual Bandits
  with Linear Payoffs.” *ICML / PMLR 28*, 127–135.
  [Proceedings paper](https://proceedings.mlr.press/v28/agrawal13.html).
- Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010). “A Contextual-Bandit
  Approach to Personalized News Article Recommendation.” *WWW 2010*.
  [Microsoft Research full text](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/p661.pdf).
