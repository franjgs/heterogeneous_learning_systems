# Experimental design

> **OLD MODEL / MODELO VIEJO — diseño histórico:** el protocolo describe el flujo anterior con L1 para todas las alertas y posible L2 posterior. Se conserva como registro del experimento ejecutado y no define la organización actualmente acordada. Véase [modelo organizativo canónico](SOC_ORGANIZATIONAL_MODEL.md).

Paired arms differ only in L2 calendar: continuous 24x7 versus weekday 09:00–17:00. Keep alert stream, classifiers, label/recommendation draws, synthetic need, service realization, analyst identities and competencies, deadlines, alpha, and dispatch policy common by seed. L1 remains continuous. A calendar change also changes weekly L2 capacity; therefore the estimand is the complete calendar proposal effect, not a pure redistribution-of-hours effect.

Begin at rho_L1=0.85 to avoid making upstream saturation the sole explanation; follow with rho_L1=1.25 as sensitivity. Keep the standardized LightGBM A+C, LSEnsemble A+C, Bayesian MLP A+C classifiers; symmetric costs; D1, P1 and WAPS; and alpha 0.25 and 1.00. Do not tune policies on observed outcomes or add fast/late escalations.

Use a 168 h admission horizon and 240 h accounting cutoff: all admissions occur in the first week, and the maximum 72 h natural deadline matures by cutoff, including weekend crossings. Primary deadline metrics use only events observed by the fixed accounting cutoff; do not call a task a deadline miss merely because admission stops. Report queue, suspended, running, completed on time, and completed late separately. Split explanatory analyses into availability exposure, congestion, and selection/priority effects; these mechanisms can overlap.

Statistical unit is the seed block. The full campaign uses the same 400 independent seed blocks as the historical reference, giving 400 paired blocks across each calendar contrast. For S_plus and paired calendar/factorial differences, resample complete seed blocks 10,000 times with common indices, preserving every condition within a seed. The campaign exports seed-block bootstrap confidence intervals and paired contrasts. Do not use condition-episode rows as independent observations or select conditions for significance. The eight-seed configuration is a technical pilot only and cannot support inferential claims.

There are 216 conditions per seed: 3 classifiers × 3 policies × 2 L1 loads × 2 alpha values × 3 L2 rosters × 2 calendars, for 86,400 condition-seed rows. The L2 roster sizes (2/3/4) are the relevant prior campaign values. No outcomes were used to select conditions or tune policies.
