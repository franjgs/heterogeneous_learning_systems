# Experimental results: SOCTRA triage × human organization

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Scope and status

This is a new, exploratory simulation campaign on the independent branch `research/soctra-hls-q1-integration-evidence`, based on reference commit `cc0880d8f56cb3aa05ff29f55f493441ec01206a`. It uses three published standardized-label A+C operating points at fixed reported (p_D,p_{FA}), not individual SOCTRA predictions. The 400 seed IDs are new. D1, P1 and WAPS are frozen. There is no claim of operational validation at GMV-CERT.

The design contains 43,200 policy-episode rows (3 classifier points × 4 FP-work assumptions × 3 L2 rosters × 3 policies × 400 paired seeds). It fixes elevated L1 load at ρL1=1.25, 6 L1 staff, 24 h admission and 36 h drain. The key assumption α scales realized total L2 service for a false positive; α is not measured operational data. The complete specification is in [EXPERIMENTAL_DESIGN.md](EXPERIMENTAL_DESIGN.md) and [SIMULATOR_SPECIFICATION.md](SIMULATOR_SPECIFICATION.md).

## Primary endpoint and audit distinction

The primary endpoint is pooled need-specific service:

\[
\widehat S_+=\frac{\text{synthetic L2 needs recommended and completed by deadline}}{\text{all synthetic L2 needs, including false negatives}}.
\]

The strict numerator is counted directly; false negatives remain in the denominator and receive no service credit. A zero-need seed is undefined for a per-seed ratio, not an observed zero. The campaign has 474 needs across 400 independent seed blocks; 133 seed blocks have no need. In contrast, `routed_task_SLA_terminal` is an all-alert route-completion proportion and is **not** (S_+). Older global/routed “correct and on-time” proxies likewise must not be described as conditional timely service of true L2 needs. Full metric audit: [AUDIT_REPORT.md](AUDIT_REPORT.md).

Uncertainty intervals below are paired, seed-cluster bootstrap percentile intervals, 10,000 replicates, bootstrap RNG seed 711202611. They quantify simulation variation conditional on fixed published classifier rates and the synthetic need process. They do not cover empirical uncertainty of SOCTRA rates, uncertainty about real SOC scenario frequencies, or uncertainty about α. Comparisons are exploratory, pointwise and unadjusted for multiplicity.

## Main quantitative pattern

At α=1 and two L2 analysts, pooled (S_+) (count / 474 needs; 95% bootstrap CI) is:

| Published point | D1 | P1 | WAPS |
|---|---:|---:|---:|
| LightGBM A+C, standardized, symmetric | 245/474 = .517 [.475,.560] | 340/474 = .717 [.675,.758] | 331/474 = .698 [.656,.739] |
| LSEnsemble A+C, standardized, symmetric | 220/474 = .464 [.420,.509] | 295/474 = .622 [.574,.672] | 292/474 = .616 [.569,.663] |
| Bayesian MLP A+C, standardized, symmetric | 208/474 = .439 [.395,.482] | 301/474 = .635 [.591,.678] | 290/474 = .612 [.567,.655] |

These are results at one elevated-L1 operating condition, not universal policy rankings. At this same capacity, direct paired (S_+) contrasts WAPS−D1, P1−D1 and WAPS−P1 (difference [95% CI]) are: for LightGBM +.1814 [+.1384,+.2245], +.2004 [+.1564,+.2447], −.0190 [−.0418,+.0042]; for LSEnsemble +.1519 [+.1111,+.1962], +.1582 [+.1140,+.2059], −.0063 [−.0261,+.0138]; for MLP +.1730 [+.1342,+.2127], +.1962 [+.1569,+.2369], −.0232 [−.0405,−.0067]. Exact results across all cells are in `results/soc_triage_hls_q1_integration_evidence/paired_policy_contrasts.csv`.

Across all 36 classifier × α × L2-roster cells, WAPS−D1 is positive with an unadjusted pointwise interval above zero in 36/36, and P1−D1 likewise in 36/36. WAPS−P1 is negative in all 36 point estimates; 27/36 intervals are wholly below zero and 9/36 include zero. The average point contrasts are +.1847, +.2116 and −.02684, respectively. This broad within-design consistency is exploratory; the many intervals are not multiplicity-adjusted and do not validate universal superiority.

Increasing L2 roster size does not guarantee monotonic improvement in this heterogeneous simulation. At α=1, L1 remains highly loaded: mean utilization at admission end is about .994–.995 and mean L1 backlog is about 219–225 alerts, while terminal L1 backlog drains to zero. L2 backlog at admission end is about 0.10–3.33 alerts across conditions and terminal L2 backlog is zero. The corresponding offered-load, actual utilization, backlog and workload measures must be read separately from the condition summary CSV; none is interchangeable with another.

## False-positive work assumption changes operational trade-offs

The analytical per-1,000-alert projections (synthetic π=19/14,449) show how much work is mechanically induced. For LightGBM, expected recommendations are 46.048/1,000 (1.107 TP, 44.941 FP, 0.208 FN); for LSEnsemble, 75.310 (1.107 TP, 74.202 FP, 0.208 FN); for MLP, 16.306 (0.926 TP, 15.380 FP, 0.389 FN). Thus the dominated LSEnsemble control adds false-positive workload without adding expected detections relative to LightGBM in this operating point. At α=1, expected unnecessary L2 work is 36.88, 60.89 and 12.62 service-hours per 1,000 alerts, respectively; at α=.25 it is one quarter of those values. The exact class-weighted figures and effective capacity ratios are in `analytic_workload_by_alpha.csv`.

The operational ranking can depend on this workload assumption. At two L2 analysts and P1, LSEnsemble−MLP (S_+) is +.1139 [+.0825,+.1470] at α=.25, but −.0127 [−.0574,+.0333] at α=1. This is a descriptive rank reversal within the stated model and a single capacity/policy subset, not evidence that either published model would have that performance on real alerts. For LightGBM at two L2 analysts, P1's S_+ gain over α=1 is +.0401 [+.0227,+.0589] at α=.25; the corresponding WAPS difference is +.0148 [−.0044,+.0351]. LightGBM versus LSEnsemble also illustrates the expected dominance mechanism: equal published detection with higher LSEnsemble false-alarm rate produces more L2 work; its downstream service can be lower under capacity pressure. Alpha contrasts for every policy and capacity are in `alpha_paired_contrasts.csv`.

The pattern is not simply “more detection is better” or “fewer false alarms is better.” The three points trade synthetic detection and induced work, while L2 capacity and service organization determine how many needed investigations finish on time. The operating-point rates remain fixed at their article values; realized finite-sample confusion proportions in this campaign are Monte Carlo outcomes, not new SOCTRA estimates.

## WAPS behavior and limits of mechanism claims

WAPS's frozen state machine is retained. In the shared L1 replay over 400 seeds, it spends a mean 0.5888 of dispatch epochs in P1, switches 1,148 times total (2.87 per seed), ends the admission period with mean L1 backlog 218.53 and drains it to zero; mean L1 utilization at admission end is .99445 and at the terminal observation .53105. L2 WAPS mode is usually D1, with switching concentrated in higher-work conditions. These summaries are diagnostic; they do not establish that mode switching caused the policy contrast. See `l1_waps_mode_summary.csv`, `l1_waps_modes_by_seed.csv`, and `l1_waps_switches.csv`.

The event-loop extension has an explicit α=1 equivalence test against the frozen engine on deterministic fixtures for D1, P1 and WAPS. Its α<1 rule is a causal aggregate-duration approximation: a dispatcher sees ex-ante expected service by class, never hidden need or TP/FP identity; the environment realizes duration according to hidden status, and only the eventual completion time can affect later scheduling. This is not a two-stage verification workflow. It cannot support claims about real verification effort or analyst behavior.

## Interpretation

Within this synthetic operating condition, the organization changes the timely service of synthetic L2 needs, and the operational effect of a classifier is sensitive to how much L2 service false positives consume. P1 and WAPS improve (S_+) over D1 in the tested cells, while WAPS does not outperform P1 in the observed point estimates and is often slightly below it. The campaign therefore supports an interaction between classifier-induced work, available L2 capacity, service times and organization inside the simulator, but not a universal benefit of adaptive organization.

The campaign does not estimate a preferred classifier for GMV-CERT. Need is synthetic, the prevalence is a process-label proxy used as a probability, acceptance is automatic, staff/service/deadlines are model assumptions, the classifier predictions are synthesized from aggregate published rates, and FP verification is represented only by α. The 400-seed intervals do not account for these structural uncertainties. Conclusions are conditional model evidence, not deployment recommendations.

## Reproducible result files and figures

All result artifacts are under `results/soc_triage_hls_q1_integration_evidence/` and are reproducible from saved per-seed episodes:

- `episodes.csv`: full 43,200 policy-episode records.
- `summary_by_condition.csv`: pooled metrics, integer numerator/denominator, bootstrap intervals.
- `paired_policy_contrasts.csv`, `paired_classifier_contrasts.csv`, `classifier_organization_interactions.csv`, `alpha_paired_contrasts.csv`.
- `analytic_workload_by_alpha.csv`, `trace_audit.csv`, WAPS L1 mode/switch files.
- `validation_checks.json`, `execution_manifest.json`.
- Figures: `figures/splus_alpha_capacity.png`, `figures/rho_l2_alpha.png`, `figures/policy_contrasts_alpha.png`.

These CSVs are locally generated synthetic outputs and may be Git-ignored by repository policy. Their presence and paths are recorded in [REPRODUCIBILITY.md](REPRODUCIBILITY.md); no commit or push was made.
