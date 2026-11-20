# SOCTRA–HLS feasibility frontier

This aggregate-only sub-study validates a statistical estimator for the operational feasibility set of escalation classifiers under the already published organizational campaign. It does **not** execute the simulator, alter any policy, or modify source campaign results.

## Contents

- [Theory and definitions](SOC_TRIAGE_FEASIBILITY_THEORY.md)
- [Validation, estimates, and interpretation](SOC_TRIAGE_FEASIBILITY_VALIDATION.md)
- [Analysis configuration](config/analysis.json)
- [Analysis and tests](analyze_feasibility.py), [tests](test_feasibility.py)
- Generated tables, maps, checks, and hashes: `results/soc_triage_feasibility_frontier/`

Run from the repository root:

```sh
python studies/soc_triage_feasibility_frontier/analyze_feasibility.py
python -m unittest studies.soc_triage_feasibility_frontier.test_feasibility
```

The analysis reads the frozen 18,720-episode campaign at `results/soc_triage_classifier_frontier_campaign/episodes.csv`, the audited classifier inventory, and the original HLS roster/capacity functions. `simulation_executed` is false in the configuration and validation manifest. Bootstrap resampling is clustered by seed and paired across policies and classifier/roster conditions.

Generated CSV files retain episode-derived numerators and denominators, pooled estimates, bootstrap intervals, capacity calculations, and the full threshold grid. The validation manifest records input hashes and consistency checks. The underlying campaign has 40 seed IDs (272600000–272600039); scenarios reuse seed IDs and are not independent across conditions.

## Scope and limitations

The need for L2 is synthetic, classifier recommendations are generated from published aggregate (p_D,p_{FA}), and per-seed counts of true needs are small. Estimates quantify simulation uncertainty conditional on those inputs; they do not add uncertainty in published classifier rates, the real operational prevalence, or external validity to GMV-CERT.
