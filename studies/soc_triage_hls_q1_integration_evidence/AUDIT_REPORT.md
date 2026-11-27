# Audit report: SOCTRA triage × HLS organization

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Scope and status

This audit uses the frozen evidence available at the integration-synthesis reference and the published classifier inventory. It does not alter SOCTRA records, preprocessing, labels, model training, published operating points, D1, P1, WAPS/HLS-B, or the historical engine. The previous 18,720 policy-episode campaign is retained unchanged. New work is isolated in this sub-study.

## Findings that remain supported

1. **Rate-to-load relation.** Under class-invariant published rates and automatic acceptance, the synthetic positive recommendation probability is
   \(q=\pi p_D+(1-\pi)p_{FA}\), so \(\lambda_{L2}=\lambda q\). This is offered routing demand. It is not L2 completion rate, utilization, backlog, or required technical work.
2. **Synthetic routing.** Prior runners construct hidden needs by class from simulator probabilities, then use a keyed uniform variate to draw recommendations from published aggregate \(p_D,p_{FA}\). No individual SOCTRA predictions are used. Need is hidden from dispatchers. Recommendations are accepted automatically.
3. **Separate resource pools.** The frozen two-level wrapper runs L1 and then forms L2 arrivals at the recorded L1 completion times. The pools have separate staff and no cross-pool blocking; thus the sequential implementation preserves each pool's event clock and causal arrival times. WAPS observes only arrivals in its rolling window. This does not represent a shared staff pool or inter-level coordination.
4. **Pairing.** The existing campaign's trace audit checks common exogenous hashes, equal admitted counts and equal confusion counts across paired policies. The feasibility reanalysis verifies \(TP+FN=\) total need, integer timely-need counts, identical denominators between policies, and deadline maturation at H+D. The old 18,720 rows share seed IDs across conditions and are not independent replicates.
5. **Pooled \(S_+\).** `necessary_L2_timely_per_need × true_need_count` reconstructs an integer numerator in all saved episodes; it is bounded by TP. The correct estimate is pooled timely needs divided by pooled total needs. A seed with no need has undefined conditional service, not zero service. In the priority case there were 35 needs over 40 seeds, with 16 zero-need seeds; previously quoted conditional per-seed averages must not be interpreted as \(S_+\).

## Material metric-interpretation issue

The saved field `correct_on_time_expected_per_admitted` is not a strict measure of correct resolution of *true L2 needs*. In the frozen calculation, the route-consistency gate is `not need or recommendation`; therefore false negatives receive no credit, but a false-positive recommendation can receive timely quality credit if its L2 task completes. Likewise, `required_resolution_SLA_terminal` is route-qualified for misses but is not conditioned only on true needs; non-needs on the L1 or L2 route can contribute. These remain reproducible historical metrics, but article text must describe them as global/routed-path quality or SLA proxies, not as \(S_+\).

The primary need-specific measure for this sub-study is:

\[
\widehat S_+=\frac{\sum_j \#\{Y=1,\ recommendation=1,\ L2\ completion\le H+D,\ completion\le deadline\}}{\sum_j \#\{Y=1\}}.
\]

False negatives are in the denominator and never in the numerator. Global routed SLA, expected correct quality per admitted alert, and physical completion remain distinct secondary measures.

## Other limitations or non-errors

- Per-seed realized \(p_D\) and \(p_{FA}\) are stored as zero when their denominator is zero in some historical exports. Those fields are not suitable for unweighted averaging. Counts are used instead.
- HLS workload accounting distinguishes task recommendations, L2 arrivals after L1 completion, L2 assignments, completions, offered work, executed service, utilization and backlog. In historical result fields, nominal FP workload assumes a full L2 investigation; it is an assumption, not an observed work duration.
- Published \(p_D,p_{FA}\) are rounded operating-point estimates. The available inventory and article tables do not provide verified confusion numerators and evaluation denominators for each model/configuration sufficient to construct empirical binomial intervals. In particular, a rounded rate that happens to equal a simple fraction is not proof that this denominator generated it. We therefore hold published rates fixed in the simulator and report this missing uncertainty separately.
- For the standardized test label group, \(19/14,449\) is the article-implied/audited label prevalence used for the synthetic need probability. Historical escalation labels are process proxies and do not establish objective L2 need.

## Engine audit and change-control result

The new FP-duration driver is separate from `src/hls/rq1_allocation.py` and `src/hls/rq1_l1_l2.py`. It imports the frozen D1 and P1 dispatcher functions and implements the existing WAPS window/hysteresis calculation in an experiment-specific event loop only so actual hidden outcome-dependent durations can differ from the ex ante service estimate. Equivalence at \(\alpha=1\) is an explicit gate: L1 and L2 assignments for D1, P1 and WAPS must match the historical wrapper exactly. Tests also verify that the dispatch functions do not receive need labels and that later arrivals do not affect earlier assignments.

The alpha model does not add an explicit verification stage. It approximates total service: a TP receives the full comparable L2 duration, an FP receives fraction \(\alpha\). The planner sees only class-level expected durations computed from published rates, prevalence and alpha, never an alert's hidden need. This makes completion times endogenous to hidden outcomes while revealing the outcome only when work completes. The approximation is causal but does not model an observable verification decision or separate verification/investigation phases.

## Implication for prior conclusions

No prior result or CSV is recalculated here. Existing evidence that high \(p_{FA}\) can create large L2 offered work remains valid under the historic full-investigation assumption. Its operational magnitude and policy interaction cannot be generalized to shorter FP work without the new sensitivity results. The metric audit narrows the interpretation of older “correct/on-time” labels; it does not invalidate the separate pooled \(S_+\) analysis or the old route/SLA and workload counts.
