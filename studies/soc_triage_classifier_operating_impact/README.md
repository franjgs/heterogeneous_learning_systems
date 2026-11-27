# SOCTRA classifier operating impact: Phase 2

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

This is an independent synthetic evaluation; it does not modify the
organization-coupling pilot, D1, P1, WAPS/HLS-B, or the historical simulator.
Published aggregate operating points are converted into keyed Bernoulli
recommendations. No individual SOCTRA predictions or alert records are used.

## Reproduction

From the repository root:

```sh
python -m unittest studies.soc_triage_classifier_operating_impact.test_phase2 -v
python studies/soc_triage_classifier_operating_impact/run_phase2.py
python studies/soc_triage_classifier_operating_impact/summarize_phase2.py
```

The fixed experiment and point tables are in `config/`. The runner writes
synthetic episode-level results and validation metadata to
`results/soc_triage_classifier_operating_impact/`. Seeds are in
`phase2.json`; the seed range does not overlap the 10 development seeds from
the published coupling pilot.
