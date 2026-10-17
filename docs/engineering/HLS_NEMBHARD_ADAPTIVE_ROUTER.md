# Nembhard Direct adaptive router

**Status:** implemented and focused-tested on 2026-10-17. This is a small
online, estimate-based HLS router for `mechanism_id="nembhard_direct"`; it is
not a MixLLM reproduction, a campaign result, or a model of learned routing in
general.

## Interface and information boundary

Use `router_id="nembhard_adaptive"` and provide
`NembhardAdaptiveRouterConfigNK` to `run_nk_production_sequence`. As with the
ORACLE router, `NembhardDirectExecutionNK.allocations` must be empty because
the router selects one feasible allocation each period. The same runner
continues to support explicit allocations and `router_id="nembhard_oracle"`;
MIS-v2 remains the default mechanism.

The adaptive decision view contains resource limits, the current problem,
estimated cell productivities, allocations executed so far, experience
reconstructed from those allocations, and period duration. It contains no
true `k,p,r`, true productivity, or HLS competence. A caller-provided latent
initial Nembhard experience is used by physical production but is not exposed
to the router; decision-visible experience starts at zero and is accumulated
from the current episode's executed effort. HLS does not yet infer a prior
experience history.

## Observation and estimator

For cell `(i,k)`, work is `w[i,k] = e[i,k] * delta_t`. The observation is

`z_obs[i,k] = z[i,k] + epsilon[i,k]`, where
`z[i,k] = w[i,k] * P[i,k](D_current)` and epsilon is an independently seeded,
zero-mean Gaussian draw with configured standard deviation. Zero-work cells
produce no observation (`None`); their noise draw, when noise is enabled, is
discarded to retain coordinate-aligned random-stream consumption. Observation
noise and exploration use independent seeds.

The initial productivity estimate is a configurable nonnegative scalar or
N×K matrix (default zero). For `w > minimum_observation_work`, the observed
rate `z_obs/w` updates a per-cell Welford running mean, count and sample
variance. Negative rates caused by observation noise are clipped to zero.
Positive work at or below the threshold is recorded but does not update the
estimator, avoiding division by a very small denominator. The initial estimate
is a decision-time starting value, not a pseudo-observation: the first valid
observation replaces it in the running mean. Because true productivity
changes with experience, the historical running mean may lag the current rate.
No `k,p,r` curve parameters are estimated.

This version assumes individual output observations per agent and skill.
That is an instrumentation hypothesis for this laboratory; other settings may
only expose aggregate output and would need a separately justified estimator.

## Selection and temporal order

For each feasible allocation the router predicts current-period output using
the estimated productivity matrix:

`y_hat[k] = sum_i e[i,k] * P_hat[i,k] * delta_t`.

It applies the shared P0 functional/effort rank, not CES:
`(success, -normalized_deficit, margin, -effort)`. The existing ordered action
catalogue resolves exact ties in favor of the first candidate. Candidate
enumeration is exhaustive and respects `max_candidates`; no pruning is done.

With probability `epsilon`, the router selects uniformly from feasible
catalogue entries (including the current greedy choice) using a dedicated
seeded stream; otherwise it selects the best estimated rank. `epsilon=0`
disables exploration. In particular, the default zero estimate with epsilon
zero can prefer zero effort under ties and may never collect informative
observations. Researchers should specify an initial estimate and/or nonzero
exploration deliberately; these are experimental controls, not learned facts.

Each period follows: estimate-based decision → true Nembhard production at
beginning-of-period experience → functional/CES evaluation → observation
generation → productivity-estimator update → experience update for next
period. The current allocation's true productivity/output is not used by the
router before the action. The physical production function is the existing
`nembhard_productive_outputs_nk`; the adaptive route does not reimplement it.

## Example

```python
run_nk_production_sequence(
    organization,
    frozen_problems,
    max_candidates=4096,
    per_agent_effort_choices=effort_choices,
    mechanism_id="nembhard_direct",
    router_id="nembhard_adaptive",
    nembhard_execution=NembhardDirectExecutionNK(
        profile=profile,
        allocations=(),
        unit_contract=unit_contract,
    ),
    adaptive_router_config=NembhardAdaptiveRouterConfigNK(
        initial_productivity_estimate=0.1,
        epsilon=0.1,
        exploration_seed=71,
        observation_noise_stddev=0.02,
        observation_seed=19,
    ),
)
```

For generated demand, pass `environment` and `environment_seed` instead of a
problem sequence; the environment is frozen first and then replayed through
the same runner. Per-period diagnostics include selected action/rank/predicted
output, exploratory flag, decision-visible experience, estimator before and
after, observations, true production, and physical experience before/after.
The diagnostic trace contains truth, but those fields are not in the decision
view.

## Validation and limitations

`tests/test_hls_lab_nk_nembhard_adaptive.py` verifies estimator statistics,
noise/replay, no true-profile or HLS-competence decision inputs, switching
decisions after observations, a divergence from ORACLE under imperfect
information, epsilon behavior, generated-demand replay, feasibility and
1×1/2×2/3×2/4×3 geometry. Nembhard ORACLE and standalone direct-mechanism
regressions remain required.

The router is myopic: it does not value future experience, quantify decision
uncertainty, or implement a principled exploration objective. Epsilon-greedy
is only a minimal configurable safeguard against never observing unused
cells. The estimator assumes individual noisy observations and a stationary
rate over its running-mean history despite experience-dependent productivity.
It does not use competence, MIS-v2, teaching, transfer, P0/P1/P2, or a learned
model of the Nembhard curve. HLS Laboratory remains **PARTIAL**.
