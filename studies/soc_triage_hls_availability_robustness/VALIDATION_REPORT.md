# Validation report

> **OLD MODEL / MODELO VIEJO — AVISO DE VERSIÓN HISTÓRICA:** este informe o protocolo documenta la campaña de disponibilidad ejecutada con servicio L1 previo para todas las alertas y posible L2 posterior. Se preserva para reproducibilidad; no describe ni valida el flujo organizativo vigente. Véase [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Historical regression

The reference is branch `research/soctra-hls-q1-integration-evidence`, commit `9772abae1bfcd2c810760e68ecd8fba107d320f0`. The complete 400-block × 108-condition replay compared 43,200 episodes and 1,681,848 L2 assignment records, including arrivals/recommendation trace hashes, needs, assignments, analyst IDs, starts, service, completions, final states, backlog, utilization, S_plus and policy contrasts. It found zero divergences under exact ID/hash comparison and absolute numeric tolerance `1e-10`. See `BACKWARD_COMPATIBILITY_REPORT.md` and compressed row-level evidence in the regression results.

## Automated and technical tests

`pytest -q studies/soc_triage_hls_availability_robustness/tests`: 17 passed. Tests include calendar patterns (24x7, configurable 8x5, 6x7, Sunday and week rollover), suspension and repeated resumption, exact work/owner persistence, deadlines independent of severity and historical deadline reproduction, uniform time scaling, hidden-label isolation, D1/P1/WAPS frozen fixtures, fast-D1 decision/trace/RNG parity, historical aggregate regression fixture and continuous-mode exact comparison.

The final integrated pilot completed with 1,728 condition-seed episodes (8 technical seed blocks), 48 trace audits, identical calendar-paired upstream traces and L1 assignments, all admitted deadlines mature by the fixed cutoff, and zero terminal drain. The pilot is a technical check, not scientific inference.

## Full campaign technical gates

The 400-block campaign produced 86,400 episodes and 2,400 trace audit rows. The merger verified disjoint seed ranges, two matched calendar arms per condition-seed, identical exogenous/recommendation/need traces within calendar pairs, invariant L1 assignments across classifier/alpha/L2-roster/calendar, matched confusion counts across the two calendar arms, and deadlines mature by the 240-hour accounting cutoff. Ten thousand block-bootstrap replicates use seed `711202611`; episode rows are not treated as independent.

During merger bring-up an overstrict check incorrectly required classifier outcomes to be identical across classifiers. That check was removed: classifier differences are intended, and exogenous trace/need hashes are independently verified by the trace audit. The merger then passed all intended pairing gates. Figure generation exposed that alpha contrast rows lacked the policy identifier; this was added and the merged contrasts and figures regenerated from the already completed shards. Neither correction changes simulated episodes or historical files.

## Known interpretation limits

The full run did not save task-by-task detail rows (`task_rows=0`); it retains each condition-seed episode and final task-state counts/metrics. The 24x7 arm uses the frozen continuous backend to preserve historical event-order behavior; the new calendar event engine is exercised in noncontinuous scenarios and explicit lifecycle tests. The system remains synthetic and assumes recommendation acceptance; no operational conclusions about GMV-CERT follow.
