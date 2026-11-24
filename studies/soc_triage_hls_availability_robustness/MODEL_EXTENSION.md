# Model extension

## Reuse audit

- `src/hls/rq1_allocation.py`: reuse immutable `Alert`, `Analyst`, `Assignment` data and unchanged D1/P1 dispatch functions. Its event loop assumes uninterrupted jobs, so it cannot model shift suspension directly.
- `src/hls/rq1_l1_l2.py`: useful routing and stage metric conventions; its L1/L2 runs are independent continuous simulations and do not retain suspended analyst-job ownership.
- `fp_workload_engine.py`: useful hidden-need boundary and realized-work pattern; its L2 event loop likewise runs uninterrupted service.
- `run_primary_campaign.py`: reusable trace, classifier rate, alpha, and clustered-summary conventions. The historical campaign configuration/output are read-only inputs; this study uses its own configuration/output path.

The new event loop accumulates service only while the assigned analyst's calendar is open. At closure, remaining effective work is frozen; the same analyst resumes it on the next open interval before receiving new work. Alerts stay queued until a suitable available analyst can start them. Work is never automatically reassigned.

Calendar time uses a location-free weekly clock (Monday 00:00 origin). L1 stays 24x7 in both comparison arms. L2 is either 24x7 or weekdays 09:00–17:00. A duty boundary suspends service as an availability event, not a policy priority decision. The Assignment record spans original start to final completion; Episode.suspension_h separately counts elapsed unavailable time while a task is owned.

The dispatcher receives only the alert, analyst competence, and configured service forecast. Hidden need must not enter dispatch inputs. Deadlines use unmodified arrival-relative natural time. Classification labels and recommendations are exogenous, fixed, and shared between paired arms.

## Status semantics

`queued`: no analyst has started the task. `suspended`: assigned task has unfinished work and its owner is unavailable at cutoff. `running`: unfinished assigned task with owner available at cutoff. `completed` and `completed_late`: completed by cutoff, classified against its original natural-time deadline. Work remaining at cutoff is never credited as completed, and a terminal drain is not included in the primary endpoint.
