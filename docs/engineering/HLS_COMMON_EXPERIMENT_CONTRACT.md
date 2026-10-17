# HLS Common Experiment Contract

**Schema:** `hls-experiment-run/1.0`
**Status:** implemented as non-destructive adapters for current result types.
**Scope:** execution description, event trace, metric/unit declarations, and
JSON serialization. It is not a common simulator, evaluator, objective, or
scientific comparison protocol.

## 1. Purpose and boundary

`src/hls/experiment_contract.py` wraps existing result objects from:

- HLS N×K/MIS-v2 production, learning, teaching, information, and optional
  generated-environment runs;
- Nembhard Direct explicit, ORACLE, and ADAPTIVE runs;
- the independent contextual quality/cost router.

Public adapters are `adapt_hls_nk_run`, `adapt_nembhard_run`,
`adapt_contextual_run`, and the dispatch helper `adapt_experiment_run`.
`ExperimentRun.to_dict()` and `.to_json()` produce the common envelope. The
adapters do not re-run a model, mutate the source result, replace native
serialization functions, or make one route's state available to another.

**A common format does not imply scientific comparability.** Competence is
not productivity; production is not quality; effort is not monetary cost; an
N×K agent is not a contextual candidate. CES remains the model's gross CES,
not net utility or a universal quality score.

## 2. Run record

`ExperimentRun` carries:

| Field | Meaning |
|---|---|
| `schema_version` | Fixed version string `hls-experiment-run/1.0`. |
| `run_id` | Caller-supplied ID when available; otherwise a deterministic digest ID for N×K/Nembhard results. Contextual runs preserve the source `run_id`. |
| `mechanism_id` | Existing route identifier. Nembhard retains its result ID `nembhard_direct_v0.1_hls_adaptation`; contextual uses `contextual_quality_cost_hls_v0.1`. |
| `policy_id` | P0/P1/P2 name, Nembhard router or `explicit_allocations`, contextual router name; `null` only if no decision/policy can be identified. |
| `configuration` | Caller snapshot if supplied; otherwise configuration reconstructed from existing result fields where possible. `null` means unavailable, not an empty configuration. |
| `initial_conditions` | Caller snapshot or a state explicitly derivable from the first record/initial prior. `null` means unavailable. |
| `random_seeds` | Named `SeedRecord(stream, value, purpose)` values. `null` means unavailable/incomplete; `[]` means the caller/adapter knows no stochastic stream was used. |
| `information_available` | Decision information boundary where known. This describes policy access, not everything retained in diagnostic results. |
| `observation_model` | Source/caller description, or an explicit note that the source result does not retain it. |
| `software_revision` | Only caller-supplied revision. No Git revision is guessed by the adapter. |
| `units` | `UnitDeclaration(quantity, unit, interpretation)` records. |
| `events` | Ordered `ExperimentEvent` records. |
| `metrics` | Separate `MetricValue` records; no combined utility. |
| `mechanism_results` | JSON-compatible copy of the native result data, retaining route-specific fields. |
| `metadata` | Source type and provenance-completeness notes, plus available environment/executor metadata. |

`RunAdapterContext` can supply missing run ID, configuration, initial state,
seed records, information/observation declarations, code revision and
metadata. Missing information is not invented. For example, the current
N×K information result does not retain its observation seed; the adapter
marks that seed provenance unavailable unless supplied by the caller.

## 3. Events

Each event has `sequence_index` (strictly increasing within the run), optional
`time_index` (period/query index where the source has one), `event_type`,
`mechanism_id`, and route-specific `data`. Current event types include:

- `environment_frozen` for a generated N×K demand trajectory;
- `decision` and `execution` for each source period/query;
- `observation` only where the source records an observation;
- `state_update` for MIS-v2, teaching, or Nembhard experience transitions;
- `estimator_update` when the source records an estimator change/snapshot;
- `policy_memory_update` when the source records policy memory changing.

Not every route emits every type. A contextual decision with no eligible
candidate produces a decision event only; no execution or feedback is
fabricated. Contextual outcomes with no quality/cost label still retain their
execution status but do not create an observation event. HLS imperfect
information records observations and estimated-state snapshots; the adapter
labels perfect-mode observations as not available to the decision or used for
estimation. The source trace does not retain every intermediate Bayesian
posterior within a period, so that event is explicitly a post-period estimate
snapshot rather than an invented intermediate state.

Nembhard diagnostic results retain true profile/state fields, but its
`decision` events contain the information used by the decision path. The
common envelope is an experiment record, not a sanitized policy input.

## 4. Metrics and units

Each `MetricValue` declares `name`, finite scalar `value`, `unit`,
`interpretation`, and optional preferred direction (`higher`/`lower`). Only
metrics actually derivable from source results are emitted. Vector-valued
states and detailed records remain in `mechanism_results` and event payloads.

Adapters retain route-specific measures:

- **HLS N×K:** functional-success fraction, gross CES, effort, output by
  dimension, and available competence/estimation detail. `ProblemSpecNK` does
  not declare a physical output or effort unit, so the adapter marks these as
  model units / source-unit-unspecified rather than assigning physical units.
- **Nembhard:** functional success, gross CES, output by skill, effort,
  direct experience, profile and router diagnostics. Declared unit strings
  come from `NembhardOutputUnitContract` and the result; effort remains a
  resource measure, not currency.
- **Contextual router:** observed quality, observed monetary cost, quality
  target and predicted/actual budget compliance, plus selected-execution
  absolute prediction errors where labels exist. Quality uses the declared
  evaluator version; cost uses the run currency/accounting version.

No metric is converted across routes. Preferred direction is descriptive and
does not declare scientific importance. In particular, budget compliance is
not a guarantee of future realized cost.

## 5. Serialization and compatibility

`to_json()` emits UTF-8-compatible JSON with recursively sorted object keys,
compact separators and `allow_nan=False`. Tuples become JSON arrays;
dataclasses/enums are copied to JSON values; non-string-key mappings are
encoded as typed `__mapping_entries__`; NaN/Inf and unsupported Python objects
raise an error. Optional unavailable fields serialize as `null`; this is
documented above and is distinct from empty arrays/objects.

Native serializers remain authoritative and untouched:

- `serialize_nk_production_result`, `serialize_nk_learning_result`,
  `serialize_nk_teaching_result`, `serialize_nk_information_result`, and
  `serialize_nk_nembhard_direct_result` in
  `src/hls/hls_lab_nk_execution.py`;
- `serialize_routing_run` in `src/hls/contextual_router.py`.

The common adapter stores a copied JSON representation and tests verify that
calling it leaves native serialization byte-identical. It does not rewrite
historical result files or change existing serialization contracts.

## 6. Minimal examples

HLS N×K and Nembhard adapters accept their existing run result directly:

```python
from hls.experiment_contract import adapt_experiment_run, RunAdapterContext, SeedRecord

common = adapt_experiment_run(existing_nk_result)
serialized = common.to_json()

common_with_provenance = adapt_experiment_run(
    existing_information_result,
    context=RunAdapterContext(random_seeds=(
        SeedRecord("competence_observation", 31, "N×K observation noise"),
    )),
)
```

The contextual adapter uses the same output envelope but not the N×K runner:

```python
common_contextual = adapt_experiment_run(existing_routing_run_result)
```

Representative JSON shape (values abbreviated):

```json
{
  "schema_version": "hls-experiment-run/1.0",
  "run_id": "ctx-run-1",
  "mechanism_id": "contextual_quality_cost_hls_v0.1",
  "policy_id": "contextual_quality_cost_router",
  "random_seeds": [
    {"stream": "contextual_exploration", "value": 7, "purpose": "epsilon-greedy candidate exploration"}
  ],
  "units": [
    {"quantity": "quality", "unit": "quality [0,1]", "interpretation": "Outcome under the configured evaluator; not CES."},
    {"quantity": "monetary_cost", "unit": "SIM-USD", "interpretation": "Per-query cost under declared accounting version."}
  ],
  "events": [
    {"sequence_index": 0, "time_index": 0, "event_type": "decision", "mechanism_id": "contextual_quality_cost_hls_v0.1", "data": {"selected_candidate_id": "c1"}}
  ],
  "metrics": [],
  "mechanism_results": {}
}
```

The example shows shape only; it is not experimental evidence.

## 7. Tests and limitations

`tests/test_hls_common_experiment_contract.py` checks all three adapters,
environment replay provenance, event ordering/types, metrics and unit
separation, native-serialization preservation, deterministic output, absent
feedback, optional provenance, and NaN/Inf rejection. Existing route tests
remain the authority for the mechanisms themselves.

The envelope does not provide a shared experiment execution engine, common
random-number construction, cross-route evaluator, unit conversion,
confidence intervals, or a scientific comparison protocol. Configuration
and seed completeness depend on what the source result retained and what the
caller supplies. A common format is useful for storage and inspection only;
it does not establish common treatment semantics or causal comparability.
