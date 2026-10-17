# HLS contextual quality–cost router — bounded implementation

**Recorded:** 2026-10-17 (Europe/Madrid)
**Status:** implemented and locally validated as an independent synthetic
capability; HLS Laboratory remains **PARTIAL**.
**Normative contract:** [HLS MixLLM Router Contract v0.1](HLS_MIXLLM_ROUTER_CONTRACT.md)

## Scope and interpretation

This implementation instantiates the approved HLS contract with a small,
self-contained synthetic query-serving environment. It is “MixLLM-inspired”
only in the broad use of contextual quality/cost prediction and feedback from
executed candidates. It is **not** a reproduction of MixLLM: it uses separate
ridge regressions, a quality-threshold/cost-minimization rule, one simulated
monetary cost, no waiting-time model, and no MixLLM predictor training.

It is a separate capability, not an N×K mechanism. A contextual candidate is
not implicitly an agent, skill, HLS competence, or language model. The
implementation does not change MIS-v2, Nembhard Direct, either Nembhard router,
or P0/P1/P2, and it does not run campaigns.

## Modules and contracts

`src/hls/contextual_router.py` defines immutable records:

- `QuerySpec(query_id, context, quality_requirement, cost_budget=None)`;
- `CandidateSpec(candidate_id, eligible_query_ids=None, metadata=())`;
- `CandidatePrior(candidate_id, quality_coefficients, cost_coefficients)`;
- `ContextualRouterConfig(context_dimension, ..., epsilon=0, exploration_seed=0)`;
- `ExecutionOutcome`, decision/forecast/update/trace records.

`ContextualQualityCostRouter.decide(query, eligible_candidate_ids=None)` receives
only the query's preselection numeric context, target, predicted-cost budget,
candidate identifiers and declared eligibility. It does not own an executor
or environment truth. Candidate-specific quality and cost ridge states are
independent. With feature vector `x` (the numeric context and, by default, a
leading intercept), regularization `lambda > 0`, and explicit prior `beta0`,
each model uses

`A = lambda I + sum(x x.T)`, `b = lambda beta0 + sum(x y)`,
`beta = solve(A, b)`.

Only received quality feedback updates the quality model; only received cost
feedback updates the cost model. Predictions are clipped to `[0, 1]` for
quality and floored at zero for cost. Unobserved candidates use declared priors
and are marked `PRIOR_ONLY`; counts, leverage, and residual dispersion are
diagnostics, not confidence guarantees or decision bonuses.

Candidate eligibility is supplied through `eligible_query_ids` and/or the
caller's `eligible_candidate_ids` snapshot. The latter is the seam for
pre-execution resource/availability checks; it must be derived from public
constraints, not outcomes. Cost is one simulated currency per query, default
`SIM-USD`, with explicit accounting/evaluator version tags. A budget filters
on predicted cost only. Actual cost can exceed it; no hard reservation or
spend guarantee is implemented.

The selector is exactly the contract rule: among eligible candidates within
the predicted-cost budget, choose minimum predicted cost among those meeting
the predicted quality target; cost ties prefer greater predicted quality,
then lexical ID. If no candidate reaches the target, choose greatest predicted
quality, then least predicted cost, then lexical ID. If the constraint-filtered
set is empty, do not execute and report either
`no_resource_eligible_candidate` or
`no_predicted_budget_feasible_candidate`. Optional epsilon exploration is
uniform over the budget-feasible set, uses its own seeded PRNG, and may override
the quality target but never declared eligibility or predicted budget. Its
default is off.

`run_contextual_routing(queries, router, executor, run_id=...)` enforces the temporal
sequence decision → execute the selected candidate only → validate and update
from received feedback → next query, and requires unique query IDs within a
run. It does not pass the executor to the
router. Missing quality/cost feedback leaves that predictor unchanged; an
execution may still update one available outcome independently. The synthetic
executor returns only the selected outcome, never counterfactual outcomes.
Failed execution can return status with absent feedback and does not create a
fabricated zero label. Currency, accounting, evaluator, query and candidate
identities are validated before update. The same `(query_id, candidate_id)`
cannot be assimilated twice.

`src/hls/contextual_router_synthetic.py` provides private latent response
functions for tests and demonstrations:

`quality_true = clip(a_i + b_i @ context, 0, 1)`
`cost_true = max(0, d_i + g_i @ context)`.

Configured observation noise is independent, bounded, zero-centered uniform
noise, with its radius reduced near domain boundaries so quality remains in
`[0,1]` and cost nonnegative. Separate deterministic quality/cost streams are
seeded independently of router exploration. These are synthetic functions,
not MixLLM equations or measured HLS quantities. Their parameters are held by
the executor-side response objects and are absent from router state, forecasts
and decision inputs.

The serializer `serialize_routing_run` emits stable sorted-key JSON. The
descriptive `summarize_routing_run` reports quality, cost, target and budget
compliance separately; it forms no net-utility or weighted aggregate.
The serialized result also records a caller-supplied run ID, router seeds and
hyperparameters, candidate eligibility metadata, initial priors, versions, and
non-oracle executor replay metadata (synthetic seed/noise settings). The
synthetic response-function parameters remain outside the router and output
trace; they must be retained separately as part of the synthetic fixture
configuration for exact reconstruction.

## Minimal usage

```python
from hls.contextual_router import (
    CandidatePrior, CandidateSpec, ContextualQualityCostRouter,
    ContextualRouterConfig, QuerySpec, run_contextual_routing,
)
from hls.contextual_router_synthetic import (
    SyntheticCandidateResponse, SyntheticContextualEnvironment,
)

candidates = (CandidateSpec("fast"), CandidateSpec("careful"))
priors = (
    CandidatePrior("fast", (0.65, 0.10), (0.25, 0.02)),
    CandidatePrior("careful", (0.85, 0.05), (0.70, 0.01)),
)
router = ContextualQualityCostRouter(ContextualRouterConfig(1), candidates, priors)
executor = SyntheticContextualEnvironment((
    SyntheticCandidateResponse("fast", .65, (.10,), .25, (.02,)),
    SyntheticCandidateResponse("careful", .85, (.05,), .70, (.01,)),
), seed=41)
run = run_contextual_routing(
    (QuerySpec("q1", (.5,), quality_requirement=.75, cost_budget=1.0),),
    router, executor,
)
```

Coefficient vectors include an intercept because the default feature map does.
All coefficients and observations above are hypothetical. For a real domain,
the feature transform, priors, evaluator, currency and accounting version must
be fixed and justified before evaluation. This implementation supplies no
external evaluator, production cost meter or model-candidate integration.

## Validation evidence and limits

`tests/test_hls_contextual_router.py` independently checks hand-computed ridge
updates and the numerical example from the contract, context- and
candidate-dependent outcomes, threshold/fallback and tie behavior, budget
filtering versus actual overruns, eligibility, epsilon behavior, partial or
missing feedback, selected-only updates, replay/serialization across fresh
Python processes, and synthetic response domains. Run with:

```text
PYTHONPATH=src pytest -q tests/test_hls_contextual_router.py
```

Validation on 2026-10-17: the focused router selection passed 16 tests; related
N×K regressions passed 162 tests. The full suite completed with 1,476 passed
and 5 failed in 595.25s. Those five are the documented provenance/integrity
failures (foundation result inventory, Campaign 2 closure/theory integrity,
Campaign 3 frozen source, and strategy-gate source integrity); none is in the
new router tests. See `docs/HISTORY.md` and the cumulative execution-plan
decision register. This is software validation of the bounded contract,
**not** a scientific campaign or evidence that routing improves quality, cost,
or any real system.

Limitations include linear contextual response approximations, explicit
hand-specified priors, possible clipping/flooring bias, no calibrated
uncertainty, no confidence-aware exploration, no delayed feedback, no query
payload/evaluator integration, and no hard budget reservation. Candidate
availability is caller-supplied rather than dynamically modeled. The
implementation provides no training/evaluation split manager: callers must
freeze preprocessing and priors externally. Cross-run persistence/migration of
predictor state is not an implemented contract beyond deterministic run
serialization. Do not use its simulated monetary units as real money or its
quality target as a guarantee.
