# Execution API: minimum usage

`execution_api.py` adds immutable configuration values and adapters around the existing engines. It is optional; historical scripts can continue calling their current functions directly.

## Configure resources and a request

```python
from hls.rq1_allocation import Alert, Analyst
from studies.soc_triage_hls_availability_robustness.availability_engine import (
    TimeScale, WEEKDAY_9_TO_17,
)
from studies.soc_triage_hls_availability_robustness.execution_api import (
    AnalystResource, CalendarBackend, DeadlineConfig, OrganizationConfig,
    PolicyConfig, SimulationRequest, SimulationSettings, TeamConfig,
)

analyst = Analyst("L2-01", frozenset({"class_a"}), {"class_a": 0.8})
resource = AnalystResource(
    analyst,
    service_by_class={"class_a": 1.25},
    forecast_service_by_class={"class_a": 1.25},
    calendar=WEEKDAY_9_TO_17,
)
organization = OrganizationConfig(
    analysts=(resource,), teams=(TeamConfig("L2", ("L2-01",)),)
)
request = SimulationRequest(
    alerts=(Alert("alert-1", 16.0, "class_a", 28.0),),
    organization=organization,
    level="L2",
    policy=PolicyConfig("D1"),
    settings=SimulationSettings(
        admission_horizon=168.0,
        evaluation_horizon=240.0,
        seed=123,
        time_scale=TimeScale(1.0),
        deadlines=DeadlineConfig({"High": 12.0, "Medium": 24.0, "Low": 72.0}),
    ),
)
result = CalendarBackend().run(request)
```

`Alert.deadline` remains an absolute natural-time instant; the offsets in `DeadlineConfig` document the scenario but never rewrite alert records. `admission_horizon` determines which alerts enter the episode. `evaluation_horizon` is the execution/accounting cutoff and may equal the admission horizon for a zero-drain stage. `TimeScale` multiplies arrival/deadline instants, service, calendars, horizons and WAPS window/capacity consistently; result times remain in the scaled units. A historical downstream stage may receive an alert after its original deadline; that absolute deadline is preserved so late completion remains measurable.

`OrganizationConfig` supports any positive team sizes and one calendar, competence map, eligibility set, actual service map and optional forecast service map per analyst. Every configured analyst belongs to exactly one L1 or L2 team. `CalendarBackend` requires a calendar for every member of the selected team; `ContinuousBackend` ignores calendars and delegates to the historical continuous engine.

## Choose a backend

```python
from studies.soc_triage_hls_availability_robustness.execution_api import ContinuousBackend

continuous_result = ContinuousBackend().run(request)
calendar_result = CalendarBackend().run(request)
```

Both return `ExecutionResult` with the native engine result, native assignment records, per-alert `TaskExecution` records, optional work segments and optional WAPS mode decisions. A field is `None` when that engine does not expose it at task level; the adapter does not fabricate states, work segments, or remaining-work values. The calendar engine exposes its lifecycle states/work segments. The continuous allocation engine does not expose a task-level work ledger, so its task-state fields other than native assignment identity/times are unavailable. Inspect `native_result` for the exact source contract.

## Hidden environment data

`EnvironmentRealization` is an optional sidecar for environment-only values. `service_scale_by_alert` carries a positive multiplier, including alpha for FP L2 or gamma for FN L1; `difficulty_by_alert` plus `difficulty_service_beta` optionally derives the difficulty multiplier. The adapter composes them once as `m_a * [1 + beta * (q_a - 0.5)]` and passes the resulting per-alert scale to the selected engine. Beta defaults to zero. In the new triage flow, alpha affects only FP routed to L2 and gamma only FN routed to L1. Alpha remains `0 < alpha <= 1`; gamma is `>=1` and defaults to 1.

`AnalystResource.forecast_service_by_class` is the dispatch-time service estimate. The continuous allocation engine and calendar engine receive this forecast for policy decisions, while actual nominal service and the composed realization are used only when calculating completion/work. The hidden-work continuous route receives its hidden need labels and composite service realization as separate environment inputs; the calendar engine never receives hidden-need labels. Neither dispatcher receives difficulty, true L2 need, or TP/FP status. The simulation request validates that provided sidecars cover exactly the admitted alert IDs.

All dataclasses copy and freeze their mapping inputs. Their validation is deterministic and runs before engine invocation. Existing configuration files, engine signatures, policies, recommendations and metrics are unchanged.

## Explicit triage and investigation orchestration

`triage_execution.run_triage_flow` reuses the existing backends and requires
an explicit `flow_mode`. Pass one backend for both levels or a mapping with
separate `L1`/`L2` backends (for example, continuous L1 and calendar L2):

- `triage_single_investigation`: routes each admitted alert immediately by its
  supplied recommendation; L2 recommendations never enter L1 first. Every
  alert starts at most one investigation stage.
- `historical_l1_then_l2`: sends all admitted alerts to L1, then sends positive
  recommendations to L2 only after L1 completion, preserving the original
  deadline. This is a compatibility path and is not the new organizational
  model.

`TriageScenario` takes the already generated alerts, hidden reference labels,
recommendations, and difficulty trace, plus organization, per-level policies,
alpha, beta, and gamma. It does not generate recommendations or draw additional
random values. Defaults are beta=0 and gamma=1; alpha is explicit and required.
Hidden labels and the realized scale are held by the environment realization.
Dispatchers receive `Alert` metadata, analyst/forecast maps and the selected
level pool only. The new API returns per-alert `completed_within_sla`,
`completed_late`, or `pending` at the accounting cutoff, while retaining stage
results. Completion after the deadline is not censored. These status fractions
are separate from any historical quality proxy/R/N endpoint.

This orchestration API is not yet wired into `scenario_loader` JSON or the
historical campaign runners. Their defaults and saved results therefore remain
unchanged. See [SOC_ORGANIZATIONAL_MODEL.md](SOC_ORGANIZATIONAL_MODEL.md) for
the scientific definitions and implementation boundary.

## Load a complete external scenario

`scenario_loader.load_scenario(path)` is an optional JSON entry point. It
resolves the existing Q1 classifier operating-point and prevalence references,
constructs `AnalystResource`, `OrganizationConfig`, policy and time values, and
returns a frozen `LoadedScenario`. Use `scenario.request_for("L2", alerts,
seed=..., policy=...)` to construct the existing `SimulationRequest` type. The
caller supplies the alerts generated by the referenced existing trace flow;
the loader intentionally does not invoke a campaign module or mutate its
globals. See [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) and the three
examples under `config/`.

Calendar windows are weekly and analyst-specific. `Alert.deadline` remains
absolute; a severity-to-deadline mapping is applied only from a separate
`severity_by_alert` sidecar passed to `request_for`. Neither the Alert model nor
any execution engine is changed by this loader. It adds no priority interruption,
task reassignment, early/late escalation, or new organizational policy.
