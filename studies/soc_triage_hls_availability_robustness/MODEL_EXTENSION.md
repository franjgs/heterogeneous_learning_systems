# Model extension

> **Versión histórica de arquitectura:** describe el flujo y alcance implementados en la etapa de disponibilidad/calendarios. La investigación L1 seguida de L2 para recomendaciones positivas no es el modelo organizativo actualmente acordado. La ruta vigente y sus límites de implementación están en [modelo organizativo canónico](SOC_ORGANIZATIONAL_MODEL.md). Se conserva esta descripción como registro técnico, sin cambiar la metodología histórica.

## Reuse audit

- `src/hls/rq1_allocation.py`: reuse immutable `Alert`, `Analyst`, `Assignment` data and unchanged D1/P1 dispatch functions. Its event loop assumes uninterrupted jobs, so it cannot model shift suspension directly.
- `src/hls/rq1_l1_l2.py`: useful routing and stage metric conventions; its L1/L2 runs are independent continuous simulations and do not retain suspended analyst-job ownership.
- `fp_workload_engine.py`: useful hidden-need boundary and realized-work pattern; its L2 event loop likewise runs uninterrupted service.
- `run_primary_campaign.py`: reusable trace, classifier rate, alpha, and clustered-summary conventions. The historical campaign configuration/output are read-only inputs; this study uses its own configuration/output path.

The new event loop accumulates service only while the assigned analyst's calendar is open. At closure, remaining effective work is frozen; the same analyst resumes it on the next open interval before receiving new work. Alerts stay queued until a suitable available analyst can start them. Work is never automatically reassigned.

Calendar time uses a location-free weekly clock (Monday 00:00 origin). Each analyst calendar is a sequence of (weekday, start, end) windows; end earlier than or equal to start represents a window crossing midnight. The day length and every input time can be uniformly scaled using the opt-in wrapper. L1 stays 24x7 in both comparison arms. L2 is either 24x7 or a configurable five-day schedule. A duty boundary suspends service as an availability event, not a policy priority decision. The Assignment record spans original start to final completion; Episode.suspension_h separately counts elapsed unavailable time while a task is owned. Work segments and cumulative executed service are separately exposed.

Severity is a technical alert class; operational priority remains a D1/P1/WAPS selection result; deadline is a separately configurable natural-time objective. The historical alert object already carries an absolute deadline and is not transformed by default. New scenarios can derive deadlines independently of severity or use an explicit severity mapping. The dispatcher receives only alerts, analyst competence, and configured expected service. Hidden need/TP/FP must not enter dispatch inputs. Recommendations are fixed exogenous inputs shared between paired arms.

## Status semantics

`queued`: no analyst has started the task. `suspended`: assigned task has unfinished work and its owner is unavailable at cutoff. `running`: unfinished assigned task with owner available at cutoff. `completed` and `completed_late`: completed by cutoff, classified against its original natural-time deadline. Work remaining at cutoff is never credited as completed, and a terminal drain is not included in the primary endpoint.
