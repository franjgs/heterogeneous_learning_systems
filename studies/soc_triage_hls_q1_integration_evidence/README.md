# SOCTRA–HLS JCR-Q1 integration evidence

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

This independent sub-study audits the existing classifier-to-organization evidence and adds a prespecified sensitivity analysis for the service consumed by false-positive escalation recommendations. SOCTRA data, preprocessing, models, published rates, HLS policies and the historical simulation engine are not changed. No individual SOCTRA prediction is reconstructed.

The experimental base is commit `cc0880d8f56cb3aa05ff29f55f493441ec01206a`; the work is isolated on `research/soctra-hls-q1-integration-evidence`. The source tree is a clean Git worktree. Results are synthetic and conditional on stated assumptions, not estimates of GMV-CERT operations.

## Reading order

1. [Audit report](AUDIT_REPORT.md): prior metrics, causal access, trace/denominator checks, and material interpretation limits.
2. [Simulator specification](SIMULATOR_SPECIFICATION.md): source categories and full synthetic model.
3. [Experimental design](EXPERIMENTAL_DESIGN.md): fixed operating points, alpha grid, paired seeds, precision objective and decision rules.
4. [Uncertainty analysis](UNCERTAINTY_ANALYSIS.md): seed-cluster inference and limits on uncertainty in empirical SOCTRA rates.
5. [False-positive workload sensitivity](FP_WORKLOAD_SENSITIVITY.md): hidden-work approximation and its causal semantics.
6. [Experimental results](EXPERIMENTAL_RESULTS.md): complete results, contrasts, figures, negative findings.
7. [Final audit](AUDIT_FINAL.md): units, exact pairing, alpha information boundary, outcome definitions, and seed-bootstrap interactions with familywise intervals.
8. [Paper results summary](PAPER_RESULTS_SUMMARY.md): article-ready bounded claims.
9. [Reproducibility](REPRODUCIBILITY.md): commands, hashes, tests and execution manifest.

Machine-readable results are written to `results/soc_triage_hls_q1_integration_evidence/`. The primary episode table is paired by seed across classifier, alpha, L2 roster and policy; it is not a collection of independent episode rows.

## Frozen evidence used

- Integrated theoretical framing: `studies/soc_triage_hls_integration_synthesis/SOCTRA_HLS_INTEGRATED_THEORY.md`.
- Joint-frontier simulation and traces: `studies/soc_triage_classifier_frontier_campaign/` and `results/soc_triage_classifier_frontier_campaign/` in the source workspace.
- Pooled service frontier reanalysis: `studies/soc_triage_feasibility_frontier/` and its saved CSVs.
- Frozen policy/model baseline: `studies/soc_human_ai_organization/`.

Historical outputs are read-only. New alpha results are a separate dataset and are not merged into old campaigns.
