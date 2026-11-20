# SOCTRA–HLS integrated evidence synthesis

This independent synthesis brings together existing SOCTRA classifier evidence and the HLS organization simulator. It creates no new policy, controller, or simulation result. Its central distinction is between the evaluated **triage-to-organization** path and a formalized, but not implemented, **organization-to-triage** feasibility relation.

## Documents

- [Integrated theory and assumptions](SOCTRA_HLS_INTEGRATED_THEORY.md)
- [Evidence synthesis](SOCTRA_HLS_EVIDENCE_SYNTHESIS.md)
- [Defensible research contribution](SOCTRA_HLS_RESEARCH_CONTRIBUTION.md)
- [Article outline](SOCTRA_HLS_PAPER_OUTLINE.md)

## Provenance

The synthesis branch is based on feasibility-frontier commit `0e086e7a59f36110b8299ed3d8d143b459ada4a8` (classifier-impact study commit `3a199faf9cce6ef95e74258e4e282c456de0f0a6`; joint campaign manifest records phase-2 commit `218dc7ba4616b26f7051d7548e6fbcecfd8bc5b8` and pilot reference `df80a78e413c88f7cf22b807e8ee27f4e556a726`). The original organizational research remains separately documented in `studies/soc_human_ai_organization/`; the first coupling pilot remains in `studies/soc_triage_organization_coupling/`.

Read each source report for complete methods, episode tables, configurations, validation checks, and caveats. This synthesis points to source evidence instead of replacing it. The local changes present before this work were preserved and are not part of this sub-study.

## Scope

Published classifier operating points are applied as synthetic Bernoulli recommendations using their aggregate rates. They are not individual predictions over the SOCTRA chronological test alerts. Need for L2, analyst services and deadlines, continuous capacity, and automatic recommendation acceptance are simulation assumptions. Nothing here validates operational impact at GMV-CERT.
