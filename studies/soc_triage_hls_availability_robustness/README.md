# SOCTRA–HLS availability robustness

> **Generaciones:** esta rama desarrolla el **NEW MODEL / MODELO NUEVO** (triaje automático y una investigación directa por alerta). Las campañas históricas y el manuscrito LaTeX actual pertenecen íntegramente al **OLD MODEL / MODELO VIEJO** (investigación inicial L1 y posible segunda investigación L2). Consulta el índice [MODEL_GENERATIONS.md](MODEL_GENERATIONS.md) antes de interpretar o citar resultados de cualquiera de las dos generaciones. No son evidencia intercambiable.

> **Estado de versiones:** OLD MODEL, campañas e informes históricos conservan el flujo L1→L2 y sus resultados no se reinterpretan. V2 y sus pilotos pertenecen a una configuración anterior del NEW MODEL, también preservada. La referencia CONOPS actual está documentada en el [modelo organizativo canónico](SOC_ORGANIZATIONAL_MODEL.md), y se configura en `config/SOC_NEW_MODEL_CONOPS_REFERENCE.json`.

An isolated synthetic study of professional heterogeneity, workload and deadline outcomes under configurable availability in SOCTRA-assisted triage. It does not reproduce the GMV-CERT SOC or claim operational service levels. It does not modify SOCTRA, D1/P1/WAPS, historical experiments or the LaTeX manuscript.

The canonical organizational decisions, SLA rule, CONOPS configuration, synthetic demand assumptions and policy-independent diagnostics are consolidated in [modelo organizativo canónico](SOC_ORGANIZATIONAL_MODEL.md). The CONOPS reference uses 5 L1 (D1) and 3 L2 (P1), continuous individual availability as an idealization, and a synthetic difficulty threshold matched to the standardized process-label prevalence. It does not represent a realistic work schedule. Prior V2 profiles remain available to reproduce their original experiments:

```sh
python studies/soc_triage_hls_availability_robustness/diagnose_new_model_conops.py --seed 2026112801
```

This is the one-seed technical diagnostic described in the canonical document, not a policy comparison or campaign. Its JSON preserves the trace and metrics. It found expected pressure of ρ≈0.50 at L1 and ρ≈0.03 at L2; under the selected label prevalence and classifier false-positive rate, L2 is underused. Poisson timing, roster, class/severity mixes, service and competence profiles, and quality proxy remain synthetic assumptions.

`analyze_reference_organization.py --config <scenario.json>` calculates ex-ante capacity and temporal feasibility for the corresponding scenario. The paired seed-998001 control is reported in [V2_24X7 validation](SOC_REFERENCE_V2_24X7_VALIDATION.md). A separate [ordinary/pulse/recovery demand profile](SOC_REFERENCE_V2_24X7_LOAD_REGIMES_VALIDATION.md) keeps its prior V2_24X7 organization fixed and is runnable with `SOC_REFERENCE_V2_24X7_LOAD_REGIMES.json`.

The exploratory ten-seed D1/P1/HLS-B policy pilot on that exact load profile is documented in [SOC_REFERENCE_V2_24X7_POLICY_PILOT.md](SOC_REFERENCE_V2_24X7_POLICY_PILOT.md), with per-run hashes and metrics in [the results JSON](SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json). Reproduce it with `python studies/soc_triage_hls_availability_robustness/run_policy_pilot.py --output studies/soc_triage_hls_availability_robustness/SOC_REFERENCE_V2_24X7_POLICY_PILOT_RESULTS.json`. It is exploratory and does not establish a policy winner.

The selected overload profile D was subsequently tested with a pre-registered independent block of 60 paired seeds (180 confirmatory episodes). Mean R/N was D1=0.63200, P1=0.63583 and HLS-B=0.64049; the pre-specified joint intersection-union test supported HLS-B over both controls in this synthetic profile. See the [confirmatory protocol](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_PROTOCOL.md), [validation report](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_VALIDATION.md), [statistical analysis](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_ANALYSIS.json) and [episode records](SOC_NEW_MODEL_PROFILE_D_CONFIRMATORY_RESULTS.json). The conclusion is limited to profile D and does not validate operational SOC outcomes or the empirical quality/service assumptions. `alpha=0.50`, `beta=0`, `gamma=1`; beta and gamma remain neutral in the experiments. This evidence is separate from all OLD MODEL results.

## What is included

- `availability_engine.py`: configurable weekly analyst calendars and persistent suspend/resume service.
- `execution_api.py` and `EXECUTION_API.md`: immutable scenario/resource records and continuous/calendar backend adapters.
- `triage_execution.py`, `scenario_loader.py`, `run_scenario.py`: explicit flow selection, JSON-to-trace integration and one seeded scenario execution.
- `scenario_diagnostics.py` and `SCENARIO_FEASIBILITY_DIAGNOSTICS.md`: policy-independent deadline, class-constrained capacity and sampled queue-recovery diagnostics.
- `run_full_regression.py`: full comparison against the frozen Q1 integration reference.
- `run_availability_campaign.py`: paired integrated SOCTRA→L1→L2 campaign.
- `run_policy_pilot.py`: fixed-seed paired exploratory comparison on the new triage single-investigation load profile.
- `merge_campaign_shards.py`: seed-block pairing checks, summaries and bootstrap contrasts.
- `make_campaign_figures.py`: publication-style summary figures.
- `SOC_EXPERT_INPUT_DELTA.md`: boundary between qualitative scenario guidance and evidence.
- `BACKWARD_COMPATIBILITY_REPORT.md`: reference commit and exact regression findings.

**Historical availability-campaign profile:** L2 weekdays 09:00–17:00 and High/Medium/Low synthetic deadlines of 12/24/72 natural hours were configurable hypotheses. For that campaign, admission lasts 168 hours and accounting closes at 240 hours; no terminal drain is used to turn late work into on-time work. The 24x7/8x5 V2 availability contrast changes available capacity as well as temporal placement; it is not a calendar-only effect at fixed capacity. This paragraph documents the old campaign only; see the canonical model document for the current CONOPS reference.

## Reproduce

From the repository root, run tests:

```bash
pytest -q studies/soc_triage_hls_availability_robustness/tests
```

The historical regression requires the original Q1 integration study and reference files. Its full invocation and exact fields are documented in `REPRODUCIBILITY.md`.

The completed scientific run used 400 paired seed blocks (86,400 condition-seed episodes) in four disjoint 100-seed shards. To reproduce on a sufficiently provisioned host, run `run_availability_campaign.py` with seed offsets `0`, `100`, `200`, and `300`, then pass the four output folders to `merge_campaign_shards.py`. Exact commands, seed base, code revision, bootstrap settings, result inventory and hashes are in `REPRODUCIBILITY.md` and the result manifests.

## Results

`EXPERIMENTAL_RESULTS.md` reports the main results and limits. Merged episode-level results, condition summaries, paired contrasts, trace audits and figures are stored under `results/soc_triage_hls_availability_robustness/campaign/`. Historical regression tables are stored separately under `results/soc_triage_hls_availability_robustness/regression/`. Generated results are not written into or over the Q1 reference directory.

The L2 task stays assigned to the same analyst over calendar suspensions. Calendar unavailability pauses effective work; it does not trigger policy re-selection or automatic handoff. `S_plus` is synthetic recommended-need task completion by deadline, not incident resolution. See `MODEL_EXTENSION.md`, `EXPERIMENTAL_DESIGN.md`, `VALIDATION_REPORT.md` and `SCIENTIFIC_IMPLICATIONS.md` for model and interpretation details.
