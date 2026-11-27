# SOCTRA-HLS model generations / Generaciones del modelo

This is the short index that separates the two organizational generations. The [organizational model](SOC_ORGANIZATIONAL_MODEL.md) is the detailed specification of the active generation; historical study reports retain their original contents and results.

## OLD MODEL / MODELO VIEJO

The **OLD MODEL / MODELO VIEJO** is the organizational model used for the historical campaigns and for the complete scientific contents of the existing LaTeX manuscript. Its workflow investigates every alert in L1 first; recommended escalations can then receive a second investigation in L2. Thus some alerts consume two investigations. The original studies commonly assumed individual continuous 24x7 availability, while later availability campaigns also examined restricted-calendar variants. Analysts were heterogeneous in competence, eligibility, and service efficiency. Historical policies include D1, P1, HLS-A, HLS-B/WAPS, and other experimental rules.

The historical research record includes confirmatory campaigns, adaptive-policy validation and development, load/operating maps, overload-duration analyses, staffing and sensitivity studies. It remains valid evidence about the OLD MODEL and its documented synthetic conditions. It does not validate the NEW MODEL automatically.

Primary locations:

- [`EXPERIMENTAL_RESULTS.md`](EXPERIMENTAL_RESULTS.md), [`EXPERIMENTAL_DESIGN.md`](EXPERIMENTAL_DESIGN.md), [`SCIENTIFIC_IMPLICATIONS.md`](SCIENTIFIC_IMPLICATIONS.md), [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md), and [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md): historical campaign, protocol, interpretation and replay provenance.
- `results/soc_triage_hls_availability_robustness/campaign/` and `results/soc_triage_hls_availability_robustness/regression/`: retained campaign and compatibility outputs.
- [`studies/soc_human_ai_organization/`](../soc_human_ai_organization/): confirmatory and adaptive-policy studies, load maps, duration and sensitivity work. Its local `results/` artifacts are ignored by Git; use its versioned manifests/evidence guides for provenance.
- [`studies/soc_triage_hls_q1_integration_evidence/`](../soc_triage_hls_q1_integration_evidence/): source integration evidence and historical SOCTRA-related workload studies.
- The existing LaTeX manuscript: **all current experimental and scientific content belongs to the OLD MODEL**. It contains no validated NEW MODEL results.

The source campaign, original protocols/configurations, results, figures, seeds and manuscript must remain unchanged. Do not recalculate, rewrite or relabel those results as NEW MODEL evidence.

## NEW MODEL / MODELO NUEVO

The **NEW MODEL / MODELO NUEVO** is the active research line on branch `research/soctra-hls-new-model`. It uses practically instantaneous automated triage; the accepted recommendation selects the investigation level. TP/FP are investigated directly in L2, TN/FN directly in L1, with exactly one investigation per alert. It retains individual analyst eligibility, competence and efficiency; expected and effective service; alpha for FP effort, gamma for FN effort and beta for difficulty; absolute natural-time deadlines; and D1, P1 and HLS-B/WAPS as unchanged assignment policies.

The current experimental base is individually continuous 24x7 availability as a simplifying assumption, not a claim about a real staffing schedule. Its configuration is [`SOC_REFERENCE_ORGANIZATION_V2_24X7.json`](config/SOC_REFERENCE_ORGANIZATION_V2_24X7.json); the ordinary/pulse/recovery profile is [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`](config/SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json). Results and diagnostics are documented in [`SOC_REFERENCE_V2_24X7_VALIDATION.md`](SOC_REFERENCE_V2_24X7_VALIDATION.md), [`SOC_REFERENCE_V2_24X7_LOAD_REGIMES_VALIDATION.md`](SOC_REFERENCE_V2_24X7_LOAD_REGIMES_VALIDATION.md), and the ten-seed [`SOC_REFERENCE_V2_24X7_POLICY_PILOT.md`](SOC_REFERENCE_V2_24X7_POLICY_PILOT.md), with its execution-level records in [`SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json`](SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json).

In the current load-regime/policy-pilot configuration, `alpha=0.50`, `beta=0`, and `gamma=1`. Alpha actively scales false-positive L2 service. Beta is neutral, so difficulty does not change realized duration; gamma is neutral, so FN has no extra L1 duration. The beta and gamma mechanisms exist in code but are not activated in these results and have not been experimentally validated. The pilot reports D1 R/N 0.7844 and SLA 97.56%; P1 0.7753 and 100%; HLS-B 0.7821 and 99.69%. These are exploratory NEW MODEL outcomes, not confirmatory evidence.

## Experimental status and comparability

The OLD MODEL has the repository's established historical and confirmatory evidence and the manuscript. The NEW MODEL has executable single-investigation configurations, technical diagnostics, and one paired ten-seed exploratory D1/P1/HLS-B pilot. It does not yet have confirmatory multi-seed evidence for its organizational workflow, difficulty effect, or FN effort effect.

Do not infer a causal policy difference across generations. The workflow, roster, service assumptions, workload, horizons, and in some studies metric estimands differ. In particular, historical `S_plus` and the NEW MODEL pilot's `R/N` must not be treated as interchangeable endpoints. The old evidence remains scientifically meaningful within its own model; it is not transferred to or used as validation of the new one.

## Open scientific questions and handoff boundary

- Which NEW MODEL confirmatory workloads, estimands, and seed-block count should be pre-registered after review of the exploratory pilot?
- What external evidence, if any, can support non-neutral beta/gamma or validate the competence-based quality proxy?
- How sensitive are NEW MODEL findings to classifier prevalence/error assumptions, alpha, team sizing, and demand composition?
- Which operational details remain deliberately abstract, especially handoff, recommendation review, and the interpretation of historical escalation labels?

Transfer of NEW MODEL evidence to the LaTeX manuscript is deferred until its experiments are designed, executed, and reviewed. No current manuscript statement or figure is to be replaced with pilot results. This index and all documents linked here preserve the distinction; it does not itself add scientific results.
