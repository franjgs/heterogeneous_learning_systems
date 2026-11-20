# SOCTRA–HLS joint frontier campaign

This separate exploratory extension evaluates the eight previously unsimulated points on the joint pD/pFA frontier and reuses compatible Phase 2 episodes. It preserves the Phase 2 pilot at `df80a78e413c88f7cf22b807e8ee27f4e556a726`; the phase 2 source snapshot used by the runner is recorded in `config/campaign.json`.

Read the [campaign report](SOCTRA_TRIAGE_CLASSIFIER_FRONTIER_CAMPAIGN.md) for the prevalence audit, exact trace-based reuse decisions, paired results, operational Pareto analysis, uncertainty, and limitations.

The classifier inventory and selected frontier are aggregate transcriptions of the SOCTRA article tables: [72-point inventory](../../results/soc_triage_classifier_operating_impact_source_audit/classifier_inventory_72.csv) and [13-point joint frontier](../../results/soc_triage_classifier_operating_impact_source_audit/joint_pareto_frontier_13.csv). They are not alert-level predictions.

## Reproduction

From the repository root, run:

```sh
python studies/soc_triage_classifier_frontier_campaign/run_campaign.py
python studies/soc_triage_classifier_frontier_campaign/summarize_campaign.py
```

The campaign runner uses the hash-audited Phase 2 episode subset published as `results/soc_triage_classifier_frontier_campaign/phase2_reuse_source_episodes.csv`. It verifies regenerated exogenous and recommendation hashes before reuse and writes a new result directory without overwriting Phase 2 files. The summarizer performs no simulations.

All CSVs and the figure under `results/soc_triage_classifier_frontier_campaign/` contain synthetic episode-level outputs and aggregate article operating points only. No restricted SOCTRA or GMV records are included.
