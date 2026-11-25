# SOCTRA–HLS availability robustness

An isolated synthetic study of how weekly L2 analyst availability changes deadline-based outcomes in SOCTRA-assisted triage. It does not reproduce the GMV-CERT SOC or claim operational service levels. It does not modify SOCTRA, D1/P1/WAPS, historical experiments or the LaTeX manuscript.

## What is included

- `availability_engine.py`: configurable weekly analyst calendars and persistent suspend/resume service.
- `execution_api.py` and `EXECUTION_API.md`: immutable scenario/resource records and continuous/calendar backend adapters.
- `run_full_regression.py`: full comparison against the frozen Q1 integration reference.
- `run_availability_campaign.py`: paired integrated SOCTRA→L1→L2 campaign.
- `merge_campaign_shards.py`: seed-block pairing checks, summaries and bootstrap contrasts.
- `make_campaign_figures.py`: publication-style summary figures.
- `SOC_EXPERT_INPUT_DELTA.md`: boundary between qualitative scenario guidance and evidence.
- `BACKWARD_COMPATIBILITY_REPORT.md`: reference commit and exact regression findings.

L2 weekdays 09:00–17:00 and High/Medium/Low synthetic deadlines of 12/24/72 natural hours are configurable hypotheses. For the campaign, admission lasts 168 hours and accounting closes at 240 hours; no terminal drain is used to turn late work into on-time work. The 24x7 vs 8x5 contrast includes both lower weekly capacity and temporal placement.

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
