# False-positive workload sensitivity

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Target mechanism

Existing coupling studies assume a recommended positive creates an L2 investigation with service comparable to a true positive. This is a useful conservative workload scenario, but an operational false alarm may be dismissed after less work. The sensitivity parameter is

\[
\alpha=\frac{E[T_{L2}\mid FP]}{E[T_{L2}\mid TP]},\quad \alpha\in\{.25,.50,.75,1.00\}.
\]

These values are design scenarios, not GMV measurements.

## Causal information constraint

The historical allocation engine uses one analyst/class service-duration function both to evaluate dispatch choices and to schedule completion. Passing hidden FP-specific durations directly to that function would disclose the latent classification to D1/P1 and could change their decisions with information unavailable at dispatch.

This study instead uses an experiment-only L2 event loop. It imports the frozen D1 and P1 dispatchers unchanged. Each dispatcher sees class-specific *expected* service duration based on \(\pi,p_D,p_{FA},\alpha\), plus current alert/roster/deadline state. It never receives the alert's hidden need or whether its recommendation is TP/FP. The environment alone uses the latent status to determine the realized total service duration: full benchmark duration for a TP and alpha times the benchmark for an FP. The policy learns only through ordinary event timing, after a job completes. WAPS retains its 4 h arrival-rate window and 1.05/1.20 thresholds; its capacity denominator is recalculated from the ex ante expected work mixture.

This is an aggregate total-work approximation. It does not assume that the analyst or dispatcher knows in advance which recommendation is false, and it does not explicitly represent a verification stage followed by an investigation. A richer staged process is not in the present evidence and is not claimed.

## Equivalence gate

At alpha=1, the realized and forecast service maps equal the existing service maps. The custom event loop must reproduce assignments for each of D1, P1 and WAPS under the original separated-pool inputs. The specific test passes on a deterministic fixture. Further tests cover hidden-label separation and no future-arrival influence. If this equivalence check does not pass in the run environment, alpha results must not be interpreted.

## Expected work calculation

For class k, the mean ex ante service factor among positive recommendations is

\[
f_k(\alpha)=\frac{\pi_kp_D+\alpha(1-\pi_k)p_{FA}}{\pi_kp_D+(1-\pi_k)p_{FA}}.
\]

Thus TP work is necessary recommended work; FP work is unnecessary work scaled by alpha; FN work is a necessary need omitted by the route, not saved correct work. Output columns separately identify offered L2 arrivals, nominal class-average work offered, actual assigned service executed, backlog and utilization. The fluid capacity LP uses the alpha-adjusted expected service matrix. A lower offered-load ratio does not imply an SLA guarantee.

## Interpretation boundary

If classifier rank or policy contrasts change with alpha, that demonstrates sensitivity inside this explicit hidden-duration model. It does not validate the alpha values, human verification time, human acceptance, or real SOC response. An FP that consumes less simulated service remains an unnecessary recommendation; an FN remains an unserved synthetic need and receives no \(S_+\) credit.
