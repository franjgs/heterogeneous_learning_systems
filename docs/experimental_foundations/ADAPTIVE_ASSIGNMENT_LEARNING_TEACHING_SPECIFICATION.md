# Minimal scientific specification: adaptive assignment, learning, and teaching

**Status:** documentary preparation only. No teaching mechanism is implemented and no experiment is authorized. This is a hypothesis scaffold, not a novelty claim.

## Scientific question

When future task demand is uncertain and productive resources are scarce, can a team improve future collective capability by learning which instructor–learner–skill relationships are effective, while paying the present production opportunity cost of teaching?

Existing work already studies assignment with learning-by-doing, transfer/observation among workers, training schedules, and uncertain multi-period workforce demand. HLS must not claim novelty for those ingredients or their simple combination. The unverified candidate is decision-relevant online inference of relation-specific teaching efficacy, coupled to prospective work/training allocation under a shared resource budget. See the [reference register](../literature/ADAPTIVE_TRAINING_REFERENCE_REGISTER.md) and [comparative evidence analysis](../literature/ADAPTIVE_TRAINING_COMPARATIVE_ANALYSIS.md).

## Minimal model contract

Let agents be `i ∈ I`, skills `k ∈ K`, and periods `t = 1, …, T`. The real system state is `z[t] = (c[t], θ, d[t], b[t])`, where `c[i,k,t] ∈ [0,1]` is agent `i`'s real competence in skill `k`; `θ[i,j,k]` is the real efficacy of agent `i` teaching agent `j` skill `k`; `d[t]` is current demand; and `b[t]` is available common resource. The unknown `θ` is part of the world, not information supplied to the operational policy.

The organization observes only `o[t] = (estimated c[t], estimated θ[t], public history H[t], demand belief q[t], b[t])`. Estimates must be generated from declared priors and observations; they cannot read private `c`, `θ`, or future demand.

An admissible joint action chooses productive effort `x[i,k,t]`, and optionally one teaching tuple `(instructor i, learner j, skill k, teaching effort u[t])`, or no teaching. Compatibility, time, and resource constraints define the feasible set `A(o[t])`. Teaching consumes the same finite time/resource budget as production; it creates no extra worker-time. Whether teacher and learner are unavailable for production during instruction must be specified in the action constraints.

Observed production is `yP[k,t] = f_k(c[t], x[t], d[t]) + εP[k,t]`. Functional production `f` must have a common interpretation and remain separate from observation noise. Under teaching, a candidate training observation is `yT[t] = g(u[t], c[i,k,t], c[j,k,t], θ[i,j,k]) + εT[t]`. A candidate competence transition is:

```text
c[j,k,t+1] = min(1, M_k(c[j,k,t], x[j,k,t])
                      + Δ_k(u[t], c[i,k,t], c[j,k,t], θ[i,j,k]))
```

`M_k` denotes the existing individual learning-by-doing law if its semantics apply. `Δ_k` is a separate teaching effect. This is a placeholder contract, not an approved transition: its form, bounds, monotonicity, noise, and resource accounting require prior scientific approval. Do not silently equate it with or add it to MIS-v2. The posterior for `θ[i,j,k]` may update only from the corresponding teaching exposure and noisy outcome, accounting for learner baseline and concurrent work experience.

## Objective and cost accounting

Use cumulative functional production under one externally fixed metric as the primary physical outcome. Report effort, teaching time, resource consumption, functional success, and deficit separately. Do not subtract unlike units or invent a weighted net utility. A clean initial formulation is constrained:

```text
maximize over policy π: E[sum(t=1..T) functional_reward[t]
subject to:             sum(t) resource[t] ≤ common budget B
```

Teaching draws from that same budget. If production and resource units cannot be made commensurate, retain the vector outcome (production, teaching/resource cost) and report its Pareto trade-off rather than scalarizing it.

## Reuse audit and boundary

- `src/hls/discover_v0.py`: three-agent/two-skill state validation, frozen joint-action catalogue, additive capability production inputs, and CES reward. CES is not itself a functional requirement or a teaching outcome.
- `src/hls/discover_develop_v2.py`: MIS-v2 individual capability transition. Reuse only for the individual learning component; do not alter its law.
- `src/hls/hls_lab_v1.py`: `ProblemSpec`, `TeamState`, `DecisionView`, organizational state/protocol, feasibility accounting, and functional observer. It currently enforces one decision per problem and its action type has no instructor–learner action.
- `src/hls/hls_lab_dynamic.py`: dynamic demand/regime execution, information modes, partial competence estimation, indexed noise, and competence persistence. It has no relation-efficacy state or training action.
- `src/hls/finite_problem_belief.py`: patterns for beliefs/planning under uncertain problem type; it is not an instructor-efficacy posterior or teacher scheduler.
- `src/hls/synthetic/c5.py`: stationary, nonstationary, and Markov demand generators; reuse only where demand semantics match.

Historical scope to preserve: G1 covers static organization/demand/resource interactions; G2 and MIS establish individual learning-by-doing and its present/future trade-off; G3-H treats heterogeneous learning rates and assignment continuation; RQ0 addresses policy-class opportunity and demand dynamics. None should be relabeled as teaching evidence. RQ0-D already makes stationary, regime-change, and Markov demand part of the historical question, so demand dynamics alone cannot distinguish the proposed contribution. Consult `docs/HLS_HISTORICAL_MEMORY_AND_NOVELTY_GUARD.md`, `docs/theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md`, `docs/theory/HLS_CAPABILITY_DEVELOPMENT.md`, `docs/experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md`, and `docs/experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md` before scope approval.

The current lab lacks a teaching action, relation-specific efficacy state, training-outcome observation model, and shared production/training allocator. These are scientific/model contracts, not documentation-only gaps.

## Minimal policy contrasts (not implemented)

Use identical planner, action set, demand forecast, horizon, compute limit, and tie-breaking:

1. **P1 — no teaching:** prospective production assignment and individual learning only.
2. **P2 — fixed-efficacy teaching:** same joint planner with efficacy estimates frozen before evaluation.
3. **P3 — online-efficacy teaching:** exactly P2's planner and limits; only efficacy beliefs update from observed teaching outcomes.
4. **Oracle diagnostic:** same planner given real `θ`, explicitly privileged, not an operational baseline.
5. **Small-instance optimum:** exact enumeration/DP as a verification bound where tractable.

P2 versus P3 is the key online-information contrast. It is invalid if P3 receives more planning depth, observations, actions, or compute. P1 versus P3 measures the package effect of allowing teaching and efficacy learning, not the isolated value of learning the relation. Exact small-instance optimization checks whether findings arise from optimizer quality.

## Identification requirements

Hold initial competencies, demand sequence/distribution, observed demand information, time/resource budgets, training opportunities, planner, and computational budget fixed. Use paired exogenous demand and noise streams while allowing each policy to create its own observations and competence path. Predefine which teaching assignments yield efficacy observations. Separate development from task exposure, or their effects are confounded. Expose enough instructor–learner–skill combinations to identify relation parameters; a single noisy outcome generally cannot distinguish low efficacy, observation noise, and learner baseline.

Use a strong no-online-update counterfactual, not merely a greedy baseline: P2 must optimize over the same prospective production/training actions as P3 and differ only in fixed versus updated efficacy beliefs. If assignment without teaching can create the same experience and final competence distribution within the same budget, the result concerns decision quality under uncertainty, not expansion of reachable capability.
