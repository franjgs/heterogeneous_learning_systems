# SOCTRA classifier operating impact: Phase 2

This is an independent synthetic evaluation; it does not modify the
organization-coupling pilot, D1, P1, WAPS/HLS-B, or the historical simulator.
Published aggregate operating points are converted into keyed Bernoulli
recommendations. No individual SOCTRA predictions or alert records are used.

The complete article-PDF source correction and 72-point escalation inventory
are documented in [SOCTRA_CLASSIFIER_SOURCE_CORRECTION.md](SOCTRA_CLASSIFIER_SOURCE_CORRECTION.md).
It supersedes this phase's incomplete classifier-source inventory and
Pareto interpretation while preserving all earlier simulation outputs.
The joint symmetric/asymmetric frontier and campaign selection are in
[SOCTRA_CLASSIFIER_JOINT_PARETO_CAMPAIGN_SELECTION.md](SOCTRA_CLASSIFIER_JOINT_PARETO_CAMPAIGN_SELECTION.md).

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
