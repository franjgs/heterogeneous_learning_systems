# Reproducibility record

> **AVISO DE VERSIÓN HISTÓRICA:** este documento conserva el diseño, metodología o resultados de una versión anterior, en la que las alertas podían recibir servicio L1 antes de pasar a L2. No describe el modelo organizativo vigente ni debe reinterpretarse como evidencia de la ruta de investigación única tras triaje. Se conserva íntegro para reproducibilidad. Decisiones actuales y estado de implementación: [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## Source state and change control

- Repository: `franjgs/heterogeneous_learning_systems`.
- Base reference: `cc0880d8f56cb3aa05ff29f55f493441ec01206a`.
- Work branch: `research/soctra-hls-q1-integration-evidence`.
- Worktree: `/private/tmp/soctra_hls_q1`.
- SOCTRA, D1, P1, WAPS, the historical engine, prior campaign files and prior outputs were not modified.
- No model training, new SOCTRA inference, or historical campaign rerun occurred.
- This branch is to be committed independently; no push is authorized by the current task.

## Reproduction commands

From the repository root:

```bash
python studies/soc_triage_hls_q1_integration_evidence/analyze_analytical.py
python studies/soc_triage_hls_q1_integration_evidence/run_primary_campaign.py
python studies/soc_triage_hls_q1_integration_evidence/reanalyze_saved_episodes.py
python studies/soc_triage_hls_q1_integration_evidence/make_figures.py
python studies/soc_triage_hls_q1_integration_evidence/audit_saved_campaign.py
pytest -q tests/test_soc_triage_hls_q1_fp_workload.py tests/test_soc_triage_organization_coupling.py
```

The main campaign writes to `results/soc_triage_hls_q1_integration_evidence/`. It uses only synthetic alert data. Configuration is frozen in `config/primary_campaign.json`. Bootstrap: 10,000 paired seed-cluster resamples, seed 711202611. New simulation seeds: 711000000–711000399. Runtime on the recorded environment was 355.26 seconds. An initial run was interrupted before producing result files because repeated identical L1 computation was unnecessarily expensive; the runner was optimized to reuse identical L1 paths and the full run then completed. This optimization did not change the design or policy logic.

## Tests and validation

The two test files above passed: 10 tests total. The new suite checks:

- α=1 assignment equivalence with the frozen simulator for D1, P1 and WAPS on a deterministic fixture.
- Hidden need and TP/FP identity are not inputs to dispatch decisions.
- Future arrivals do not affect earlier dispatch.
- FP duration changes realized workload as configured.
- Bootstrap calculations are deterministic under a fixed seed.

The saved-campaign audit is a reanalysis only. It verified 43,200 complete factor rows with no duplicates, 400 seed blocks, 474 needs distributed across 267 positive-bearing seeds, exact exogenous-hash pairing across classifier points, invariant confusion counts across downstream conditions, correct S+ denominators, and all deadlines maturing before cutoff. It computes 108 classifier-by-policy interaction contrasts from saved integer counts with paired seed-cluster bootstrap and a familywise max-|z| sensitivity.

`validation_checks.json` records 43,200 rows, 400 paired seeds, 474 unique needs, 133 zero-need seeds, identical need counts across classifier configurations, identical confusion counts across policies, no deadline truncation, and a successful deterministic replay of WAPS L1 backlog. The trace audit and episode CSV are retained for independent verification.

## Artifact inventory

Tracked study code, configuration, tests and reports reside in `studies/soc_triage_hls_q1_integration_evidence/` and `tests/test_soc_triage_hls_q1_fp_workload.py`. Synthetic result outputs are present locally in the Git-ignored `results/soc_triage_hls_q1_integration_evidence/` directory:

```text
episodes.csv
summary_by_condition.csv
paired_policy_contrasts.csv
paired_classifier_contrasts.csv
classifier_organization_interactions.csv
alpha_paired_contrasts.csv
analytic_workload_by_alpha.csv
trace_audit.csv
l1_waps_mode_summary.csv
l1_waps_modes_by_seed.csv
l1_waps_switches.csv
validation_checks.json
execution_manifest.json
audit_checks.json
audit_need_distribution.csv
audit_interaction_contrasts.csv
figures/splus_alpha_capacity.png
figures/rho_l2_alpha.png
figures/policy_contrasts_alpha.png
```

Do not infer independence from the number of episode rows: confidence intervals resample seed clusters and preserve all corresponding conditions together. The 400 seeds characterize Monte Carlo variation under the synthetic generator only.

## Current artifact hashes

SHA-256 digests for study source, configuration, test and generated result files are recorded in `results/soc_triage_hls_q1_integration_evidence/file_manifest.json`. Regenerate after any change to those artifacts using:

```bash
python studies/soc_triage_hls_q1_integration_evidence/write_file_manifest.py
```

The manifest itself is excluded from its own digest set. Result files may be ignored by Git; hashes establish local integrity but do not mean they have been published.
