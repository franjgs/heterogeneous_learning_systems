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
`learning -> competence changes -> V(S) -> routing -> Gamma_oper`. B2.2
instantiated the `operation -> learning opportunity` link, but its frozen
classification was `INCONCLUSIVE`; it does not yet support that link with the
preregistered seed reproducibility.

## B2.2 preregistration and completed result

[B22_PROTOCOL.md](B22_PROTOCOL.md) freezes the PACS B2.2 operational
opportunity-value experiment before execution. It makes the learning
opportunity genuinely action-dependent, retains the B2.1 models, splits,
seeds, training rule, CPU device, and validation-only evaluation, and keeps
TEST closed. Its primary event is `rho_k(c)>0` and `H_k(c,B,kappa)>0`, with the
exact frontier `B DeltaV_k(c)>rho_k(c)+kappa`. The predeclared grid is
`N={25,50,100}`, `c={0,0.02,0.05,0.10,0.15}`, `B={1,2,5,10}`, and primary
`kappa=0`.

The valid CPU execution completed 60/60 opportunity updates and 1,200/1,200
analytical rows in 08:10:14 with TEST closed. It found four observations with
`rho>0,H>0`, 800 with `rho>0,H<=0`, and zero of 240 cells with favorable
results in at least two seeds. The preregistered result is therefore
`INCONCLUSIVE`: it is not `NULL` because favorable observations exist, and it
is not `POSITIVE` because they do not meet the frozen reproducibility rule.
The independent audit and diagnosis are in
[b22_diagnostic.md](../../results/pilots/b22_opportunity_value/b22_diagnostic.md).
This result is not a policy result, RQ0 conclusion, TEST result, novelty claim,
or B2.3 design.

## Retrospective B2.1–B2.2 portfolio bridge

A post hoc analysis asked whether B2.1 joint states could be combined with
B2.2 opportunity costs to test `H_i<0`, `H_j<0`, and `H_ij>0`. The mandatory
counterfactual compatibility gate failed: stored F0 and D scores differed for
all five seeds, and B2.1/B2.2 singleton vectors differed for all 60
seed-domain-N interventions. No one of the 90 pair states was eligible, so the
analysis stopped before calculating scientific bridge outcomes. The result is
documented in
[portfolio_bridge.md](../../results/pilots/b22_opportunity_value/portfolio_bridge/portfolio_bridge.md).
It is a `RETROSPECTIVE BRIDGE ANALYSIS`, not an amendment to B2.2 and not
evidence for or against the existence of accumulated-opportunity rescue.

## B2.3 accumulated-opportunity portfolio preregistration

[B23_PROTOCOL.md](B23_PROTOCOL.md) freezes a self-contained PACS experiment for
the question: can two operation-generated learning opportunities that are
individually unprofitable become jointly profitable when accumulated and used
for matched joint development? It does not combine B2.1 and B2.2 states. Every
singleton and joint state shares the same seed-specific F0, D, immutable sample
IDs and teacher outputs. Primary joint development preserves each
opportunity's singleton exposure; an exact midpoint of that trajectory matches
the singleton total compute and measures dose sensitivity without another fit.

The primary event is strictly `rho_i>0`, `rho_j>0`, `H_i<0`, `H_j<0`, and
`H_ij>0`, with the identity `H_ij=H_i+H_j+B Gamma_oper`. The frozen design has
five seeds, `N={25,50,100}`, six pairs, five c values, four B values, 160 fits,
250 validation evaluations, 1,800 primary rows, and 450 secondary midpoint
valuations. `POSITIVE` requires the event in at least 3/5 seeds
for one exact `N × pair × c × B` cell; `NULL` requires no event anywhere; any
other valid nonempty result is `INCONCLUSIVE`.

Status: **B2.3 IMPLEMENTED — NOT RUN**. The CPU-only runner, immutable
opportunity store, restart/provenance checks, compatibility-first analyzer,
and synthetic tests are in
[`experiments/pilots/b23_portfolio_opportunity/`](../../experiments/pilots/b23_portfolio_opportunity/).
No B2.3 training, teacher inference, or scientific result has been produced;
TEST remains closed.
