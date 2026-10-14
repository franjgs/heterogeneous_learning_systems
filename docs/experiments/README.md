# Experimental Documentation Registry

Executable experiments and results remain in the repository-level
`experiments/`, `results/`, and `tests/` directories. This page is the compact
conceptual index; it is not a second results ledger.

## Current synthetic framework

- [HLS Laboratory v1 implementation and limitations](HLS_LAB_V1.md)
- [HLS Laboratory v1 scientific contracts (CE-22 reference)](HLS_LAB_V1_SCIENTIFIC_CONTRACTS.md)
- [HLS Laboratory v1 CE-24 deterministic train/evaluate validation](HLS_LAB_CE24.md): local organizational-learning effect, order sensitivity, and HOLD on general claims
- [HLS Laboratory v1 CE-25 mechanism decomposition](HLS_LAB_CE25.md): paired reward-blind exploration versus reward-informed learning, memory controls, and deterministic order/horizon checks
- [HLS Laboratory v1 dynamic DISCOVER extension](HLS_LAB_DYNAMIC_EXTENSION.md): latent CES-type beliefs, repeated decisions, separate real/estimated skills, and persistent MIS-v2
- [HLS competence estimator validation](HLS_COMPETENCE_ESTIMATOR_VALIDATION.md): bounded one-skill numerical checks of the three-support Bayesian estimate and MIS-v2 temporal prediction
- [HLS dynamic laboratory characterization pilot](HLS_DYNAMIC_LAB_CHARACTERIZATION.md): paired bounded characterization of information, partial competence estimates, individual learning, planning horizon, and the existing tabular organizational update
- [HLS dynamic stress-scenario pilot](HLS_DYNAMIC_STRESS_PILOT.md): pre-policy frontier-calibrated requirements, a restricted-budget compatible subset, and paired stress tests of existing organizations
- [G0 current instrument](G0.md)
- [G2 D0/D1/D2 dynamic ground truth runner](../../experiments/synthetic/g2/)
- [A1 reference specification](../experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md)
- [RQ0 campaign ledger](../experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md)
- [Geometry redistribution protocol/outcome](../experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md)
- [Routing--opportunity coupling protocol/outcome](../experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md)
- [Configuration × Environment → Performance v0.1](CONFIGURATION_ENVIRONMENT_PERFORMANCE_V01.md)
- [Campaign 1 frozen protocol](CAMPAIGN_1_PROTOCOL.md)
- [Campaign 1 test-range characterisation](CAMPAIGN_1_RESULTS.md)
- [Campaign 3 Problem-Generator Calibration Gate](CAMPAIGN_3_PGCG.md)
- [Campaign 3 crossed generator split](CAMPAIGN_3_GENERATOR_SPLIT.md)
- [Campaign 3 team-space geometry characterization](CAMPAIGN_3_TEAM_GEOMETRY.md)
- [Campaign 3 frozen team development/held-out split](CAMPAIGN_3_TEAM_SPLIT.md)
- [Campaign 3 frozen horizon-pilot protocol](CAMPAIGN_3_HORIZON_PILOT.md)
- [Campaign 3 initial J=12 horizon-pilot result](CAMPAIGN_3_HORIZON_PILOT_RESULTS.md)
- [Campaign 3 Gate 1](CAMPAIGN_3_GATE1.md): development-only continuation
  sensitivity; **PARTIAL LOCAL STRUCTURE**, conditional on `h ~ d_Q11`
- [Campaign 3 Gate 2](CAMPAIGN_3_GATE2.md): minimal hybrid development-state
  coverage audit; **SUFFICIENT DEVELOPMENT DIVERSITY**
- [Campaign 3 C3.2-DATA](CAMPAIGN_3_C32_DATA.md): frozen allocation and raw
  counterfactual target-generation protocol; no predictor training
- [Campaign 3 C3.3](CAMPAIGN_3_C33.md): first Q00/Q11 supervised selector and
  matched development-only sequential comparison
- [Campaign 3 C3.3 results](CAMPAIGN_3_C33_RESULTS.md): development
  comparison, paired performance and computational-cost diagnostics
- [Campaign 3 FAST/DEEP/META](CAMPAIGN_3_FAST_DEEP_META.md): conditional
  deliberation prototype using the closed C3.3 selector
- [Campaign 3 META-VOC](CAMPAIGN_3_META_VOC.md): benefit-per-computation
  routing versus frequency-matched RANDOM on fresh development histories
- [Campaign 3 META-VOC confirmatory protocol](CAMPAIGN_3_META_VOC_CONFIRMATORY_PROTOCOL.md):
  frozen four-domain design and independent nominal-probability RANDOM baseline
- [Campaign 3 META-VOC confirmatory results](CAMPAIGN_3_META_VOC_CONFIRMATORY_RESULTS.md):
  paired performance–computation evidence; 50% primary point designated after
  development review
- [META-VOC predictor-validity audit](META_VOC_PREDICTOR_VALIDITY_REPORT.md):
  bounded C3.2-matched counterfactual audit of the frozen Ridge/router;
  local uncommitted evidence, not a change to C3 confirmatory outcomes
- [Campaign 4 counterfactual protocol](CAMPAIGN_4_COUNTERFACTUAL_PROTOCOL.md)
  and [engineering verification](CAMPAIGN_4_ENGINE_VERIFICATION.md):
  preparation only; H0 is not the C3.2 `ell=11` target and full C4 execution
  remains NO-GO pending scientific/design resolution
- [Synthetic runners](../../experiments/synthetic/)

## Foundation and empirical evidence

- [Foundation reproductions](../../experiments/foundations/)
- [Pilot implementations](../../experiments/pilots/)
- [Versioned result artifacts](../../results/)
- [G2 result artifacts](../../results/foundations/g2_dynamic/)

Frozen protocols remain authoritative for their declared designs. Result
directories remain authoritative for numerical evidence and provenance.
Neither is a substitute for [HLS Current State](../HLS_CURRENT_STATE.md).
