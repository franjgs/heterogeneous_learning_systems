# Experimental foundations: audited status

Status: B1, B2, and B12 foundation block implemented and audited on 2026-09-16; B13 retained as a subsequent diagnostic, not a proof of joint-management advantage.

This block reproduces selected mechanisms from Garicano (2000) and Gutjahr
(2011), then checks their minimal executable interface. It is not the HLS method,
does not demonstrate benefit from coupling, and does not establish novelty, RQ0,
or P4.

| Experiment | Kind | Status | Audited meaning |
| --- | --- | --- | --- |
| B1.1 | `source_reproduction` | `REPRODUCED` | Autarky fixture recovers `f(z*)=c`. |
| B1.2--B1.4 | `source_reproduction` | `REPRODUCED` | The stated finite organization fixtures recover their scoped Garicano mechanisms; they are not proofs of the full propositions. |
| B2.1 | `source_reproduction` | `REPRODUCED` | Recursive and closed-form competence dynamics agree. |
| B2.2 | `source_reproduction` | `REPRODUCED` | The extremal optimum matches the complete configured grid in a convex-region instance. |
| B2.3 | `source_reproduction` | `REPRODUCED` | Gutjahr Example 2 and its mixed optimum are recovered exactly. |
| B2.4 | `source_reproduction` | `REPRODUCED` | A finite instance of Theorem 3's persistence result is recovered. |
| B2.5 | `source_reproduction` | `FAILED_SOURCE_REPRODUCTION` | Literal published equations give objectives `2.0, 1.5, 0.5, 1.5`; the claimed switching optimum is not recovered. |
| B12.1 | `hls_translation` | `SUPPORTED` | The configured special case in which allocation determines real work/exposure and then competence executes consistently. It is not the general ontology interface. |
| B12.2 | `limiting_case` | `REPRODUCED` | Setting `beta=eta=0` recovers the static allocation component. |
| B12.3 | `limiting_case` | `REPRODUCED` | Removing routing and supplying allocations recovers Beam 2 dynamics. |
| B12.4 | `hls_translation` | `SUPPORTED` | 36 of 96 configured cases show the defined dynamic effect; `eta=0` gives 0 of 96. |
| B13 | `diagnostic_model` | `SUPPORTED` internally; not a programme result | The configured diagnostic separates present operational consequence `D_G` from future experience-mediated value `G_G`; it does not establish `J(pi_joint) > J(pi_separate)`. |

The B12.4 fraction is grid geometry, not performance or prevalence. The two
counterfactual trajectories differ only in their first allocation and use the
same routing rule thereafter.

The canonical ontology now distinguishes allocation, real work, learning
exposure, competence, and performance. B12 uses Gutjahr's special-case
identification of normalized assigned work with the exposure entering its
competence equation; it must not be generalized silently. B13 exposed why a
common operational value and explicit source mappings are required before a
joint/separate comparison.

## Reproduction

Run `python -m pytest -q`, then execute each `run.py` under
`experiments/foundations/`. Each result directory contains `metrics.json` and a
uniform `manifest.json` linking the experiment ID, exact configuration, code
hashes, citation keys, Git state, command, and result hash.

The frozen pre-implementation specification remains in
`EXPERIMENTAL_SPEC_V0.md`; the executed sequence is preserved in
`EXECUTION_PLAN.md`.

## Subsequent empirical interaction checkpoints

The later programme pilots are not source-reproduction foundations and should
not be conflated with B1.1--B13 above. Their consolidated status is recorded in
[HLS Scientific Checkpoint after B2.1](../checkpoints/HLS_checkpoint_after_B21.md).

- The digits B1 factorial was `OBSERVED — WEAK / UNSTABLE INTERACTION`: models
  were near ceiling, learned competence clusters were unstable, and mean
  interactions were small relative to seed variation.
- PACS B2.0 established four fixed domain competences and heterogeneous
  MobileNetV2/ResNet-50 validation profiles in a valid CPU run. The initial
  compute-blocked status was superseded; MPS was excluded after a transfer-path
  diagnostic. The stored automatic B2.0 selection and the later B2.1 choice of
  25%-BASE F0 have distinct provenance.
- PACS B2.1 observed strong positive learning interactions across the fixed
  domains and showed that domain-level Fast/Deep operational valuation can
  substantially transform them. B2.1 used VALIDATION only and did not test
  operation-dependent opportunity generation, Omega, H(D), or a complete HLS
  policy.

The theory-to-experiment frontier is therefore explicit: B2.1 supports
`learning -> competence changes -> V(S) -> routing -> Gamma_oper`, while the
`operation -> learning opportunity` link remains experimentally untested.
