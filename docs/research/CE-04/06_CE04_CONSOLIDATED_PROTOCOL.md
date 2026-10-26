# HLS-CE-04 — Consolidated protocol

**Status:** CE-approved operational protocol; implementation validated by focused tests. **No pilot or campaign has been run.**
**Decision date:** 2026-10-26. **Implementation record:** see `07_TECHNICAL_READINESS.md` and the corresponding entry in `docs/HISTORY.md`.

This document records the CE-approved protocol. The expert originals in files 01–04 remain verbatim and retain their original proposal status; the discrepancies and dispositions are summarized in §12. This protocol does not claim that CE-04 results establish general properties of HLS.

## 1. Scientific question and scope

Study how mean-preserving heterogeneity in task competence and assignment organization affect collective success under changing demand and deadlines, at three organization sizes. There is no explicit cooperation, individual learning or transfer. Competences are fixed. Each task is assigned to one agent.

## 2. Factorial conditions

- Organization sizes: `N ∈ {12, 24, 48}`.
- Four task families and four balanced primary-capability labels.
- Compositions `H0`, `H1`, `H2`; each task-family mean is exactly 0.775.
- Policies `P0`, `P1`, `P2`, `P3` as defined in §6.
- Factorial: 3 compositions × 4 policies × 3 scales = 36 conditions.
- Pilot design, when separately authorized: seeds 0, 1, 2; 108 replicas.
- Full campaign, requiring separate CE authorization: seeds 1000–1029; 1,080 replicas.

No pilot or campaign is authorized by this implementation order.

## 3. Competence composition

For agent `i`, task family `k`, primary family `p_i`:

```text
q_ik = 0.775 + α_H s_ik
s_ik = +0.75 if k = p_i; −0.25 otherwise
α_H0 = 0; α_H1 = 0.10; α_H2 = 0.20
```

There are exactly `N/4` agents for each primary family. Thus, for every task family, the mean is `0.775` under all three compositions. The competence values are in `[0.725, 0.925]` for H2 and within `[0,1]` for every condition. Primary-family labels are scenario construction metadata and are not exposed to P0, P2 or P3. P1 receives the true `q_ik` matrix as its declared full-information reference.

## 4. Demand, time and service

- Continuous-time Poisson arrivals with total intensity `λ = 0.55N`.
- Arrivals are generated only in `[0,400)`.
- Task-family proportions are observed only at the phase in which a task arrives: `[0,150)`: 40/20/20/20%; `[150,300)`: 10/40/40/10%; `[300,400)`: 25/25/25/25%.
- A task's deadline is `arrival + 3` time units. Success requires correct completion at or before this deadline.
- After the last arrival, the simulation drains all admitted work to completion. There are no arrivals after time 400; original deadlines do not move during the drain.
- Service times are lognormal with mean 1.25 and CV 0.30, independent of competence, task family and composition.
- Each agent has one FCFS queue, at most one service in progress and no preemption. Policies may append work to a busy agent's queue.

## 5. Common admission screen

At each arrival, every policy computes the same `F_i`: estimated probability that appending the task to agent `i`'s FCFS queue completes by the task's deadline. The admissible set is `A = {i : F_i ≥ 0.50}`. Reject if `A` is empty; otherwise select only from `A`. Admission uses observable queue state, service distribution, elapsed active-service age and deadline slack. It does not use true or estimated competence. Rejections count as failures in the primary denominator and yield no correctness label.

For an active service of age `a`, the remaining service is conditioned on `S > a`. Its first two residual moments are calculated from the approved lognormal law. Add those moments to the moments of the queued full service times and the arriving task. Match the sum to a two-moment lognormal (Fenton–Wilkinson) and evaluate its CDF at the remaining slack. If idle, use the exact single-service lognormal CDF.

The deterministic convolution reference discretizes exact lognormal and conditional-residual probability masses at step 0.001. A fixed 25-state validation battery has two reference probabilities in `[0.45,0.55]`; maximum absolute approximation error is `0.003856`, below the CE tolerance `0.01`. Therefore the approved two-moment method is retained. This check is numerical validation of the probability calculation, not a pilot or HLS performance experiment.

## 6. Assignment policies

All policies use the same admissible set and common `F_i` values. Ties are resolved by a deterministic agent priority permutation drawn once per replicate, independently of policy and composition.

- **P0:** select the admissible agent with the least expected pending service workload: expected residual service for an active task plus 1.25 per queued task. It does not use competence.
- **P1:** maximize `q_ik × F_i`, using true competence.
- **P2:** maximize `q̂_ik × F_i`. For every agent/task family, `q̂` is the Beta(1,1) posterior mean `(1 + successes)/(2 + successes + failures)`. Update only when correctness of an executed task is observed at completion, including a completion after the deadline. Rejected tasks yield no label.
- **P3:** published disjoint LinUCB equations, with a four-dimensional context `x_i = F_i e_k`, one parameter model per agent, `A_i=I₄`, `b_i=0`, and `α = alpha_from_delta(0.05) ≈ 2.358`. Choose the feasible agent with greatest UCB score. No primary-family label, true competence, future state or counterfactual outcome is exposed.

P3 reward is `Y=1` exactly for correct on-time completion, and otherwise `Y=0`. A correct/incorrect on-time completion reports reward at completion; if the deadline passes without completion, report zero at the deadline. Later correctness does not revise that reward. A delayed-feedback adapter stores the selected `(agent, context)` by task and applies the existing disjoint LinUCB additive update only when that reward is observable. LinUCB uses deterministic UCB exploration; the P3 exploration seed stream is reserved and recorded but consumes no random draw.

## 7. Reproducibility and paired potential outcomes

Replicate seeds are the unit of independent replication. Independent random stream namespaces are used for demand, composition, service, correctness, tie priority and the reserved P3 exploration stream. Service and correctness potential outcomes are deterministic functions of `(replicate seed, N, task id, agent id, stream id)`, so changing a policy cannot consume or shift another policy's random draws. Demand task trajectories are common across composition/policy conditions at a given seed and N. Competence composition and tie priority are generated independently of policy. Configurations, software versions, commit revision, task-level events and replica-level metrics are serialized through the existing `ExperimentRun` contract.

## 8. Outcomes and costs

- **Primary:** correct tasks completed by deadline divided by all tasks arriving during `[0,400)`. Rejected, incorrect and late tasks are failures.
- **Secondary:** latency from arrival through completion (mean, median, p95), decision latency (mean, median, p95), task-family/phase success, rejections, incorrect and late completions, per-agent service utilization, service time, assignments, and success per task family and phase.
- **Primary operating cost:** total service time consumed by admitted tasks, including service continuing after a deadline. Also report service time per correct on-time completion; undefined if there are no successes.
- **Computational cost, kept separate:** total CPU time, decision wall time, decision CPU time and peak resident memory (raw platform-native `getrusage` unit). These are simulator/policy measurement costs, not organizational service cost.

## 9. Confirmatory analysis

Each complete seed-level replica is one independent observation. Contrasts are paired by seed and condition; do not resample individual tasks as replicates. Preserve E3's composition contrasts (`H1−H0`, `H2−H0` by policy and scale), policy contrasts (`P1−P0`, `P2−P0` by composition and scale), composition × policy differences-in-differences, and adjacent-scale contrasts. The CE addendum's `C1` is the same contrast as `H2−H0` under P1; `C2` is the same as `P1−P0` under H2. They are aliases, not duplicated tests. Also report CE `C3` (`P2−P1` under H2), `C4` (`P3−P2` under H2), and `C5` (H2−H0 interaction for P3 versus P0).

For each paired contrast, report the mean, sample SD and percentile bootstrap 95% CI with 10,000 resamples over replicate-level differences. Apply Holm to the complete contrast family returned by the preregistered analysis code. Report paired TOST for equivalence margin ±0.02 (±2 percentage points), with Holm adjustment. Failure to reject a difference is not evidence of equivalence. The implementation uses paired t-test p-values for difference tests; no inferential result is produced until a separately authorized experiment is run.

## 10. Implementation and validation gate

The CE-04-specific SimPy runner is in `src/hls/ce04.py`; SimPy is an explicit runtime dependency. It reuses the repository's LinUCB equations and `ExperimentRun` serialization without changing their contract. HLS-PEF's current metric registry does not define this event-level success-on-time estimand; CE-04 is not coerced into a mismatched metric definition.

Automated tests check exact task-wise means and value bounds, continuous phase-partitioned demand, keyed potential outcomes, Fenton–Wilkinson against deterministic convolution near the threshold, FCFS/non-overlap/capacity, arrival conservation and drain, common admission, delayed P3 reward, reproducibility, `ExperimentRun` round-trip, factorial size and statistical helpers. Passing these tests validates implementation checks only; it does not validate scientific effects or authorize a pilot.

## 11. Execution authorization

This order authorizes implementation and focused tests only. It explicitly does **not** authorize the 108-replica pilot or the 1,080-replica campaign. No CE-04 performance results exist as of this protocol update. Do not execute `factorial_configs` or `run_factorial` without a later CE instruction.

## 12. Expert originals and decision trace

The reports in [01 E1](01_E1_MATHEMATICAL_MODEL.md), [02 E2](02_E2_ASSIGNMENT_POLICIES.md), [03 E3](03_E3_EXPERIMENTAL_PROTOCOL.md) and [04 E3 addendum](04_E3_PROTOCOL_ADDENDUM.md) are retained verbatim. E1's mean-preserving criterion was adopted. E3's original 0.90/0.65 primary-family construction does not preserve means by task family and was not adopted. E3 initially proposed three policies; the CE adopted four policy roles based on E2 and the later E3 addendum. Cooperation, learning and transfer remain disabled. The original expert texts are not silently edited to match this consolidated protocol.
