# HLS Nembhard Oracle Router

**Status:** implemented as a deterministic, perfect-information assignment
baseline for the Nembhard Direct HLS adaptation. It is not a learned router,
does not forecast future value, and is not a reproduction of MixLLM.

## Interface and information boundary

Select it with:

```python
run_nk_production_sequence(
    organization,
    problems,
    max_candidates=...,
    mechanism_id="nembhard_direct",
    router_id="nembhard_oracle",
    nembhard_execution=NembhardDirectExecutionNK(
        profile=profile,
        allocations=(),  # router supplies one allocation per period
        unit_contract=units,
        initial_state=initial_experience,
        period_duration=1.0,
    ),
    per_agent_effort_choices=effort_catalog,  # required when K != 2
)
```

The router contract is implemented by `NembhardOracleDecisionViewNK`,
`NembhardOracleRouterNK.choose`, and `NembhardOracleDecisionNK` in
`src/hls/hls_lab_nk_nembhard_router.py`. The decision view contains only
`OrganizationResourcesNK` (agent/skill identifiers, individual limits and
collective budget), the current `ProblemSpecNK`, true Nembhard experience
`D[N,K]`, the Nembhard `k,p,r` profile, and period duration. It contains no
HLS actual or estimated competence matrix. The router has perfect knowledge of
the Nembhard state and productivity parameters; this is an oracle reference,
not an observation-based information condition.

The runner accepts either the existing explicit-allocation route (omit
`router_id`, provide one allocation per problem) or this automatic route
(set `router_id="nembhard_oracle"` and provide an empty allocation tuple).
When a generated environment is supplied, it is frozen first and passed to
the same router execution path. P0/P1/P2, MIS-v2, teaching, HLS competence
estimation, and explicit joint actions remain unsupported in Nembhard mode.
The default MIS-v2 route and its result serializers are unchanged.

## Candidate generation and decision rule

The router enumerates the existing feasible productive-allocation catalogue
through `enumerate_productive_action_entries_nk`, including individual effort
limits and the minimum of organization and problem budgets. Candidate counts
are guarded by `max_candidates`; the catalogue is never silently truncated.
For `K=2`, the existing ordered effort catalogue is used by default. Other K
values require caller-supplied per-agent effort vectors.

For each feasible allocation `e`, current-period output is predicted by the
same function used by Nembhard execution:

\[
P_{ik}(D)=k_{ik}\frac{D_{ik}+p_{ik}}{D_{ik}+p_{ik}+r_{ik}},\qquad
y_k=\sum_i e_{ik}P_{ik}(D_{current})\Delta t.
\]

P0's existing exact functional ranking is factored into
`functional_effort_rank_nk` in `src/hls/hls_lab_nk_production.py` and shared
without changing its ordering:

1. functional success (`1` before `0`);
2. lower summed normalized deficit;
3. larger minimum functional margin across positive requirements;
4. lower total productive effort.

The rank tuple is `(int(success), -normalized_deficit, margin, -effort)`.
CES is not in the decision score. Python's stable `max` retains the first
feasible candidate in the existing catalogue order on an exact tie. The
router only optimizes this current-period ordering; it does not value the
experience gained for later periods.

The geometry module adds `OrganizationResourcesNK` so the router can enumerate
actions from resource restrictions without receiving organization competence
fields. This is an interface separation, not a change to resource semantics.

## Trace and diagnostics

The router returns the chosen allocation, original catalogue action ID,
predicted output, predicted functional result, rank tuple, and feasible
candidate count. Nembhard episode records include these diagnostics alongside
the independently recomputed executed output. The transition still evaluates
output at beginning-of-period experience and only then advances experience by
the configured `e * delta_t` convention.

## Minimal example and verification

The tests in `tests/test_hls_lab_nk_nembhard_oracle.py` check hand-calculated
rankings, experience-dependent assignment switches, catalogue-order ties,
resource feasibility, 1×1/2×2/4×3 execution, repeated-period transitions,
generated-demand replay, competence independence, predicted-versus-executed
output equality, and a case where the oracle differs from an explicit fixed
assignment. The combined focused selection also includes prior Nembhard and
Phase 1–4 N×K tests.

## Limitations

- The policy is perfect-information over true experience and the true profile;
  it does not learn from observations.
- It ranks only immediate functional performance and effort; it does not plan
  for future learning or optimize cumulative CES.
- It relies on the existing discrete effort catalogue and exhaustive
  enumeration; `max_candidates` fails closed rather than pruning.
- It inherits the caller's Nembhard output/requirement unit calibration.
- It is a validation baseline for a later estimate-based router, not evidence
  that routing improves organizational performance and not a MixLLM
  implementation.
