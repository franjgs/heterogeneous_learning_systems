# CE-04 — Chief Engineer Decisions

**Decision record date:** 2026-10-26
**Current status:** CE-04.4 operational specifications approved; implementation
and focused validation complete; no pilot/campaign authorized or executed.
The earlier entries below preserve their status at the time they were made.

The following decisions are adopted by the CE as stated in the instruction
received on 2026-10-26. They are distinct from the expert reports, whose
original texts are preserved verbatim in files 01–04; incorporation does not
imply that the technical design is complete.

1. **First dimension:** capability heterogeneity and its interaction with
   organization.
2. **Cooperation:** explicit cooperation is disabled; each task is executed
   by one agent.
3. **Learning:** individual learning and competence transfer are disabled;
   competence is constant.
4. **Organization sizes:** N = 12, 24 and 48 agents.
5. **Task types:** four task families.
6. **Composition conditions:** H0 homogeneous, H1 moderate heterogeneity,
   H2 high heterogeneity. Mean competence by task type is identical across
   the three; heterogeneity changes dispersion and specialization. Exact
   generation equations and parameter values remain open.
7. **Policies:** P0 minimizes expected load; P1 uses true competence, expected
   service time and deadline; P2 uses the same decision function as P1 with
   estimated competence; P3 is an adaptive contextual policy using an
   established method. P1 is a full-information reference, not a global
   optimum. The common objective and P3 method/configuration remain open.
8. **Scaling:** resources and demand scale proportionally with N; nominal
   relative load is held constant. The exact resource scaling rule remains
   open.
9. **Design:** scenarios are paired; random seeds are independent and
   comparisons are paired.
10. **Algorithms:** no new algorithm will be developed without express CE
    authorization.
11. **Execution:** no pilot before protocol freeze; the full campaign requires
    later CE authorization.

The separate initial-dimension proposal in
[`HLS_INITIAL_DIMENSION_EXPERIMENT_PROPOSAL.md`](../HLS_INITIAL_DIMENSION_EXPERIMENT_PROPOSAL.md)
is not silently substituted for CE-04 and is not incorporated as its protocol.


## Historical proposal discrepancies and CE dispositions

The four expert texts are preserved verbatim in files 01–04. The following
distinctions record how their proposals relate to the CE decisions; they do not
rewrite or retroactively amend the expert originals.

### Heterogeneity construction

- E1 proposed preserving mean competence separately for each task family:
  (1/N) Σ_i q_ik(H) = μ_k, while varying dispersion/specialization. Its
  q_ik(H)=μ_k+α_H s_ik expression is a possible parameterization, not a
  complete generator or a set of fixed parameter values.
- E3's initial H0/H1/H2 used primary-family proportions and match/mismatch
  success probabilities 0.90/0.65. Those profiles do not equalize mean
  competence by task family across H0/H1/H2. For example, at N=12 their means
  for T1 are H0=.90, H1=.775, H2=.7125; for T2 they are H0=.65, H1=.691666..., H2=.7125. Thus the initial E3 composition treatment mixes heterogeneity with task-specific mean competence.
- The CE adopted E1's equal-mean-per-task criterion. E3's later addendum
  explicitly refers to E1's generator and requires numerical mean checks.
  Exact H0/H1/H2 profiles and parameters remain pending; E1 did not supply
  them as a finished generator.

### Policy set

- E3 initially proposed three policies: random feasible assignment, maximum
  competence, and maximizing P(correct) × P(finish before deadline).
- E2 proposed a policy family with P0 expected workload, P1 Min-Min plus a
  strong success/load/deadline baseline, P2 contextual Thompson Sampling, and
  an estimated-competence P1 comparison.
- The CE adopted four policy roles: P0 least expected load; P1 true competence,
  expected service time and deadline; P2 the same decision function with
  estimated competence; P3 an established contextual adaptive method. This
  is the CE decision, not a verbatim adoption of E2's named algorithms.
- E3's addendum reflects the CE's four roles. The original E3 protocol and
  E2 report remain unchanged. P3's actual established method and the common
  P1/P2 decision function remain pending.

### Factorial, cooperation and timing

- E3's initial 3×3×3 design has 27 conditions, 810 full-campaign simulations,
  and a proposed 24-agent initial run under non-saturated load. E2 separately
  suggested beginning at N=24. The CE instead adopted all three scales,
  four policy roles, a 36-condition factorial, a 108-simulation technical
  pilot after freeze, and a separately authorized 1,080-simulation campaign.
- E1 defines κ as operational cooperative advantage for a task executed by a
  pair. E2 recommends disabling cooperation; the CE adopted one agent per task
  and no explicit cooperation for this first study. Consequently CE-04 does
  not directly estimate κ and cannot support claims about cooperative
  complementarity.
- E3's initial P1 uses competence only and its P2 uses expected completion
  probability. The CE's P1/P2 instead share one function over competence,
  expected service time, workload and deadline; P2 substitutes observed-data
  estimates for true competence. E3's addendum records this CE disposition.

These are resolved differences in experimental direction, not evidence that
the expert originals were internally identical. The CE-approved conditions
and pending specifications are recorded separately in
[06_CE04_CONSOLIDATED_PROTOCOL.md](06_CE04_CONSOLIDATED_PROTOCOL.md).

## CE-04.4 operational disposition — 2026-10-26

This disposition supersedes the earlier statements above that the five
specifications or operational semantics remained open. It records the CE's
later approvals; it does not alter the verbatim expert originals.

- **Heterogeneity:** `q_ik=0.775+α_H s_ik`; primary `s=+0.75`, other
  families `s=−0.25`; `α={0,0.10,0.20}` for H0/H1/H2; four equally sized
  primary groups. Task-family means are 0.775.
- **Service and queues:** lognormal mean 1.25/CV 0.30, independent of
  competence and composition; one FCFS queue and one service per agent, no
  preemption.
- **Arrivals and horizon:** continuous Poisson total rate `0.55N` on
  `[0,400)`, three half-open demand phases, deadlines at arrival+3; drain
  admitted work after the final arrival without new requests.
- **Admission:** common competence-blind set `A={i:F_i≥0.50}`; reject when
  empty. Fenton–Wilkinson includes the conditional active-service residual
  and passed deterministic convolution validation (2 near-threshold cases;
  maximum absolute error 0.003856 ≤ 0.01).
- **Policies:** P0 least expected pending workload; P1/P2 share `q×F` with
  true versus Beta(1,1) estimated competence; P3 is disjoint LinUCB with
  context `F e_k`, `α=alpha_from_delta(0.05)` and delayed binary on-time
  reward. A zero logged at deadline is not revised by later correctness.
  Tie priority is deterministic per replicate and independent of policy and
  composition.
- **Analysis:** seed-level replica is the independent unit; paired bootstrap
  10,000 resamples, Holm correction and paired TOST ±2 percentage points.
- **Implementation:** CE-04-specific SimPy runner uses the existing
  `ExperimentRun` contract. No contract or HLS-PEF metric definition was
  changed. Focused tests pass; no factorial replica was run.

Protocol approval and implementation validation are not experimental
evidence. The pilot (108 replicas) and full campaign (1,080 replicas) remain
unexecuted and require later CE authorization. See the [consolidated
protocol](06_CE04_CONSOLIDATED_PROTOCOL.md) and [technical readiness
report](07_TECHNICAL_READINESS.md).
