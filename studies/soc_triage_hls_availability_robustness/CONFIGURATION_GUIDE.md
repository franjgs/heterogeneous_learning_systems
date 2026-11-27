# External scenario configuration (JSON)

> **Frontera de versión:** los JSON históricos siguen construyendo solicitudes por nivel y sus ejecutores conservan el flujo anterior. El JSON V2 además declara el modo de triaje y puede ejecutarse por `run_scenario.py`. Para valores y diagnósticos vigentes, véase [modelo organizativo canónico](SOC_ORGANIZATIONAL_MODEL.md).

`scenario_loader.load_scenario(path)` reads a version 1 JSON scenario and
returns a frozen `LoadedScenario` built on the existing `execution_api.py`
types. For legacy JSON the caller still supplies alerts to `request_for` and
selects a backend. For V2, `generate_trace(seed)` adapts the existing
`hls.ia_l1_l2_simulation.generate_alerts`; `triage_scenario_for(seed)` builds
the input consumed by `triage_execution.py`. The one-episode runner is
`python studies/soc_triage_hls_availability_robustness/run_scenario.py`.

## Top-level sections

- `scenario_id`, `description`, `schema_version`: identity and schema (`1`).
- `flow_mode`: optional `triage_single_investigation` or
  `historical_l1_then_l2`; absent values default to the historical flow.
- `generation`: `generator.reference` accepts
  `run_primary_campaign._primary_trace` for legacy provenance or
  `ia_l1_l2_simulation.generate_alerts` for the V2 seeded trace adapter;
  `classifier.reference` must be
  `q1_primary_campaign.classifiers`, with a default and allowed historical
  classifier IDs; `prevalence.reference` must be
  `q1_primary_campaign.prevalence.pi` or `demand_profile.prevalence_by_class`.
  Q1 references resolve from the checked-in primary campaign JSON; V2 uses
  synthetic class-conditional prevalence in its demand profile. Parameters
  include alpha, beta, gamma and the existing difficulty-distribution shape.
  `need_reference` describes the hidden reference and is never passed to
  dispatchers.
- `organization`: `analysts` declares each `id`, `level` (`L1` or `L2`),
  `eligible_classes`, competence values in `[0,1]`, positive `service_h` values,
  optional positive `forecast_service_h`, and an individual calendar. `teams`
  lists the exact analyst IDs for each represented level. Team sizes are
  arbitrary and independent; an analyst must have a competence value and
  actual/forecast service for every eligible class.
- `policies`: per level, `default` and `available` values from `D1`, `P1`,
  `WAPS`. If WAPS is available, `waps` requires `window_h`, `low`, `high`, and
  `capacity_per_h`, validated by the existing `HLSBConfig`.
- `deadlines`: `severity_map` with nonnegative
  `offsets_by_severity_h`, `provided_absolute` to preserve generated Alert
  deadlines, or `explicit_by_alert` with an `absolute_by_alert` mapping.
  In `severity_map` mode, `request_for` requires a separate `severity_by_alert`
  map covering exactly the supplied alert IDs, with only configured severity
  labels. `provided_absolute` preserves deadlines already present in generated
  Alerts. No new alert fields are introduced. Deadlines in `Alert` remain
  absolute natural-time instants.
- `time`: positive `admission_horizon`, later `evaluation_horizon`, and a
  positive uniform `scale`.
- `experiment`: integer `seed_start`, positive `seed_count`, plus optional
  experiment-grid metadata such as alpha, policies, or load values.

## Calendars

`{"kind":"continuous"}` is permanent availability. A weekly calendar uses
`{"kind":"weekly","windows":[{"day":"Mon","start_h":9,"end_h":17}]}`.
Days accept Mon–Sun (or integer 0–6, Monday=0); hours are within 0–24. An end
at or before the start denotes an overnight window. Multiple windows can
represent 6x7, 8x5 on any selected days, split shifts, or rotating coverage.
Calendars belong to analysts, not teams. The available engine has no holidays,
leave, or absence model.

## Historical references and examples

The loader resolves the three published classifier operating points from
`../soc_triage_hls_q1_integration_evidence/config/primary_campaign.json`.
Prevalence is Q1-referenced in legacy configurations and is an explicitly
synthetic class-conditional input in V2.
`config/HISTORICAL_REFERENCE.json` is an explicit resource snapshot for a
representative six-L1/three-L2 historical roster and references the original
generator/configuration provenance. It is a validation aid, not a replacement
for historical campaign scripts, and it does not redefine or regenerate saved
results. The two `SYNTHETIC_SOC_*.json` examples demonstrate continuous and
mixed schedules; they are generic hypotheses and do not describe GMV-CERT.

## Minimal use

```python
from studies.soc_triage_hls_availability_robustness.scenario_loader import load_scenario
from studies.soc_triage_hls_availability_robustness.execution_api import CalendarBackend

scenario = load_scenario("studies/soc_triage_hls_availability_robustness/config/SYNTHETIC_SOC_MIXED_SHIFTS.json")
# alerts = existing_generator(...); preserve the original paired seed/draw logic
severity = {alert.alert_id: "medium" for alert in alerts}
request = scenario.request_for("L2", alerts, seed=920000, policy="WAPS",
                               severity_by_alert=severity)
result = CalendarBackend().run(request)
```

The legacy per-level `request_for` path does not execute a generator. For V2,
the dedicated `generate_trace` adapter invokes only the recognized existing
generator reference and `triage_scenario_for` keeps need, recommendation and
difficulty sidecars separate from the dispatcher. WAPS remains implemented by
the existing backend.

## Validation and limits

Load-time checks cover schema version and references, analyst IDs/team
membership, level consistency, eligibility/competence/service coherence,
calendar windows, policy names and WAPS parameters, time horizons, deadlines,
and seeds. Values are frozen after loading. The loader accepts only listed
generator/classifier/prevalence references; it does not load Python plugins or
arbitrary modules. The existing generator adapter supports schedules it can
represent (one rate shift or one bounded pulse plus recovery, fixed class mix).
New policies, priority interruptions, reassignment, and early/late escalation
are not implemented.
