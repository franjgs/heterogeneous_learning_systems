# HLS External Mechanism Integration 0.1 — Nembhard Direct

**Status:** implemented as an explicit N×K execution alternative; HLS
Laboratory remains **PARTIAL**. This is a bounded HLS adaptation of the
Nembhard-inspired direct-experience productivity curve, not a reproduction of
Nembhard and Bentefouet (2015).

## Architecture and public contracts

The integration keeps the existing N×K task type (`ProblemSpecNK`), agent and
skill identifiers, effort limits, collective budget, and functional/CES
evaluators. The existing execution entry point gains an opt-in selector:

```python
run_nk_production_sequence(
    organization, problems, max_candidates=...,
    mechanism_id="nembhard_direct",
    nembhard_execution=NembhardDirectExecutionNK(...),
)
```

`mechanism_id="mis_v2"` is the default and follows the existing runner path.
Explicit MIS-v2 selection is tested for byte-identical serialized results to
the default for both frozen production and MIS-v2 learning episodes.

The Nembhard-specific contracts in
[`hls_lab_nk_nembhard.py`](../../src/hls/hls_lab_nk_nembhard.py) are:

- `NembhardDirectProfileNK`: `k[N,K]`, `p[N,K]`, and `r[N,K]` matrices;
- `NembhardDirectStateNK`: separate direct-experience state `D[N,K]`, with
  `zeros(N,K)` available for an explicit zero-experience initialization;
- `NembhardOutputUnitContract`: caller declaration for effort-intensity,
  duration, exposure, output and task-requirement units; it fails if output
  and requirement labels differ;
- `NembhardDirectExecutionNK`: profile, one explicit allocation per problem,
  unit declaration, optional initial `D`, and positive period duration.

`run_nk_production_sequence` dispatches to the separate Nembhard execution
path, returning `NKNembhardDirectRunResult`. The result has a stable mechanism
identifier and a dedicated serializer,
`serialize_nk_nembhard_direct_result`.

The shared `OrganizationConfigNK` supplies ordered agent/skill identifiers,
effort limits and resource budgets. Its competence matrices are deliberately
not read by the Nembhard branch. They are not productivity parameters. This
choice preserves existing task/resource configuration without representing
Nembhard productivity as HLS competence.

## Adaptation equations and units

For each agent `i` and skill/task dimension `k`, the standalone law is

\[
P_{ik}(D_{ik}) = k_{ik}\frac{D_{ik}+p_{ik}}
                               {D_{ik}+p_{ik}+r_{ik}}.
\]

The first HLS adaptation defines effective work during a period as

\[
\Delta D_{ik}=e_{ik}\,\Delta t,\qquad
D_{ik,t+1}=D_{ik,t}+\Delta D_{ik},
\]

and period output using beginning-of-period productivity:

\[
y_{k,t}=\sum_i e_{ik,t}P_{ik}(D_{ik,t})\Delta t.
\]

Consequently, current exposure changes only the next period's productivity;
there is no within-period integration of the curve. This effort-to-exposure
mapping, use of a fixed beginning-of-period rate, and output bridge are HLS
adaptation conventions, not claims about the source article's ambiguous
duration/output timing.

`NembhardOutputUnitContract` is a required explicit caller declaration:
`e*Δt` is in the declared exposure unit, `k` is calibrated as task-output
units per exposure unit, and output and `ProblemSpecNK.requirements` share the
declared requirement/output unit. It also records the effort-intensity and
duration unit labels; the caller attests that their product has the exposure
unit. No scaling or normalization is silently applied. The code checks that
the output and requirement labels match; scientific calibration remains the
caller's responsibility. If it is not defensible, this route must not be used
for functional/CES comparison.

The existing HLS budget semantics are preserved: effort limits and collective
and problem budgets constrain the period's intensity `e`. They do not scale
with `Δt`; `effective_work_used = Σ e * Δt` is separately traced as exposure.
Thus changing duration changes experience and output but does not create an
additional resource charge. That is an explicit duration convention, not a
claim that exposure and resource cost are interchangeable.

## Decision, transition and trace boundary

Nembhard execution requires one caller-supplied allocation per problem.
Every allocation is checked with the existing N×K feasibility contract
against individual effort limits and the minimum of the organization and
problem budgets. No production allocation is silently reduced.

P0/P1/P2 are not offered for this mechanism: their decision view ranks HLS
competence, whereas Nembhard productivity is determined by `D` and its own
`k,p,r`. The API rejects those policies, teaching actions, MIS-v2 learning and
competence-estimation modes in the Nembhard branch. Automatic assignment is
now available through separate `nembhard_oracle` (perfect information) and
`nembhard_adaptive` (observation-based productivity estimates) routers; neither
reuses HLS competence. See the [ORACLE contract](HLS_NEMBHARD_ORACLE_ROUTER.md)
and [adaptive-router contract](HLS_NEMBHARD_ADAPTIVE_ROUTER.md). The explicit
allocation path remains available.

Per-period records identify the mechanism, task, allocation, duration,
beginning `D`, beginning productivity, per-agent output contribution,
aggregate output, functional evaluation, CES, experience increment and end
`D`, plus the unchanged effort/budget accounting. MIS-v2 record dataclasses
and serialization are not changed.

## Minimal example

```python
from hls.hls_lab_nk_execution import run_nk_production_sequence
from hls.hls_lab_nk_nembhard import (
    NembhardDirectExecutionNK, NembhardDirectProfileNK,
    NembhardOutputUnitContract,
)

profile = NembhardDirectProfileNK(
    asymptotic_productivity=((2.0, 1.5), (1.0, 2.0)),
    prior_experience=((0.0, 0.0), (0.0, 0.0)),
    experience_scale=((4.0, 4.0), (4.0, 4.0)),
)
contract = NembhardOutputUnitContract(
    effort_intensity_unit="work_per_period",
    duration_unit="period",
    exposure_unit="effective_work",
    output_unit="task_output",
    requirement_unit="task_output",
)
execution = NembhardDirectExecutionNK(
    profile=profile,
    allocations=(((0.5, 0.0), (0.0, 0.5)),),
    unit_contract=contract,
)
# Pass a valid OrganizationConfigNK and one K=2 ProblemSpecNK as usual,
# then opt in with mechanism_id="nembhard_direct".
```

## Validation and limits

Focused tests cover scalar law and N×K path behavior, hand calculations,
pre-transition output timing, direct-experience update, independent cells,
unit mismatch rejection, infeasible allocations, N×K sizes through 4×3,
deterministic traces, and byte-identical explicit/default MIS-v2 execution.
The mechanism does not include indirect transfer, worker grouping/selection,
continuous-time production, or a source-paper objective. The estimate-based
router is myopic and its observations/estimator are HLS instrumentation
conventions rather than mechanisms attributed to the source paper. Task
requirements and CES are used only through the existing HLS evaluation
contract after the caller declares compatible output units.

No campaign was run. The new route is suitable for controlled explicit
allocation validation. Automatic decision-making is now authorized only in
the explicit ORACLE and adaptive routes described above; this does not
authorize campaigns or imply policy superiority.
