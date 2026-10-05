# Repository Guide

## Purpose and authority

This document is the repository's **authority, provenance, and implementation
map**. It tells a researcher or agent where the relevant material lives, which
source governs a question, and how theory connects to code, tests, experiments,
and retained results. It points to scientific truth; it does not restate,
extend, or redefine scientific truth.

The principal documents have distinct jobs:

| Document | Responsibility |
| --- | --- |
| [README](../README.md) | Programme entry point and navigation. |
| [HLS Philosophy](HLS_PHILOSOPHY.md) | Programme philosophy and scientific compass: WHAT, WHY, and WHAT FOR. |
| [Research Doctrine](../RESEARCH_DOCTRINE.md) | Canonical methodological rules. |
| [HLS Ontology](hls_ontology.md) | Canonical semantic and mapping layer. |
| [Research Questions](research_questions.md) | Official research-question authority. |
| [HLS Current State](HLS_CURRENT_STATE.md) | Canonical current scientific-state authority. |
| [History](HISTORY.md) | Scientific history and durable lessons from prior work. |
| **This guide** | Repository authority, provenance, and implementation map. |

If this guide conflicts with a canonical scientific source, the scientific
source prevails. In particular, consult **HLS Current State** for current
scientific status, **Research Questions** for official questions, and the
identified theory/evidence source for formal claims and numerical results.

## Status vocabulary

The guide uses the following compact labels. A label is quoted from a source
where possible; otherwise it is marked **inferred** and is only a navigation
classification.

- **CANONICAL**: designated source of truth for its stated responsibility.
- **CURRENT**: used by the current programme but not necessarily a sole source
  of truth.
- **CONSOLIDATED**: a stated, scoped foundation or result.
- **SUPPORTING**: useful model, evidence, or interpretation with narrower scope.
- **PROTOCOL**: a frozen or proposed procedure; not a result by itself.
- **FROZEN REFERENCE**: preserved detailed specification or gate record.
- **HISTORICAL**: retained for provenance and lessons, not current status.
- **WORKING / UNTRACKED**: present in the local working tree but not yet fully
  integrated into the canonical authority layer.

## Document authority map

| Path | Role | Status | Authority / use for | Do not use for |
| --- | --- | --- | --- | --- |
| [README.md](../README.md) | Repository front door | CURRENT | Programme orientation and reading path. | Detailed status, theory, or evidence. |
| [RESEARCH_DOCTRINE.md](../RESEARCH_DOCTRINE.md) | Research methodology | CANONICAL | Claim discipline, theory import, `WORLD != POLICY`, and anti-drift rules. | Defining HLS or reporting current results. |
| [HLS_PHILOSOPHY.md](HLS_PHILOSOPHY.md) | HLS compass | CANONICAL | HLS's purpose, collective perspective, and two beams. | RQ0 mechanics, protocols, or current evidence. |
| [hls_ontology.md](hls_ontology.md) | Semantic infrastructure | CANONICAL | Terms, dimensional consistency, and cross-theory mappings. | A closed universal model or current-results ledger. |
| [research_questions.md](research_questions.md) | Official question record | CANONICAL | Active RQ0 and its scope. | Historical questions or theory proofs. |
| [HLS_CURRENT_STATE.md](HLS_CURRENT_STATE.md) | Scientific-status summary | CANONICAL | Established, scoped, open, and deliberately unclaimed results. | Detailed derivations or protocol chronology. |
| [HISTORY.md](HISTORY.md) | Scientific history | HISTORICAL | Negative results, abandoned branches, and reasons for changes of direction. | Current priority without checking Current State. |
| [theory/README.md](theory/README.md) | Theory registry | CURRENT | Locate canonical and supporting theory. | Independent scientific-status authority. |
| [theory/HLS_STATIC_THEORY.md](theory/HLS_STATIC_THEORY.md) | Static theoretical foundation | CONSOLIDATED | T0--T3 and the fixed-competence/static boundary. | Dynamic T4--T6 theory. |
| [theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md](theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md) | Static validation interpretation | CONSOLIDATED | Scope, controls, and non-claims of G1.1/G1.2. | A novelty claim about static OR theory. |
| [theory/HLS_DYNAMIC_THEORY.md](theory/HLS_DYNAMIC_THEORY.md) | Dynamic theoretical foundation | CONSOLIDATED working foundation | T4--T6 scaffold, HLS Relevance Cascade, and stated scope. | A claim of irreducible joint management or validation beyond G2's stated scope. |
| [theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md](theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md) | Dynamic ground-truth specification | CANONICAL minimal constructive ground truth | D0/D1/D2 constructive/null reference and stated non-claims. | A universal dynamic model or validation beyond D0/D1/D2. |
| [theory/minimal_hls_model.md](theory/minimal_hls_model.md) | Reduced dynamic testbed | SUPPORTING | Model-scoped separability, threshold, coordination, and boundary lessons. | General T4--T6 theory. |
| [theory/operational_development_opportunity_value.md](theory/operational_development_opportunity_value.md) | Mechanism-level theory | SUPPORTING | Opportunity-value decomposition under stated assumptions. | General proof that joint management has value. |
| [theory/rq0_routing_integration_boundaries.md](theory/rq0_routing_integration_boundaries.md) | RQ0 formal theory | CANONICAL for stated RQ0 formalization | Policy classes, local/global distinction, C(alpha), and SEP-Omega boundary. | Prevalence, robustness, or empirical relevance. |
| [experiments/README.md](experiments/README.md) | Experimental registry | CURRENT | Locate instruments, protocols, and evidence. | A second current-results ledger. |
| [experiments/G0.md](experiments/G0.md) | Synthetic framework contract | CURRENT | G0 blocks, `WORLD != POLICY`, capability surface, and RQ0 relation. | A universal HLS model or an RQ0 answer. |
| [experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md](experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md) | Minimal adaptive reference-scenario specification | CANONICAL for its declared scenario scope | The 2-worker × 2-task/competence × 2-period reference, its S0--S3 controls, and its deterministic reference evaluator. | A redefinition of G0, a universal HLS model, an experimental campaign, or evidence of policy superiority. |
| [experimental_foundations/HLS_MINIMAL_REFERENCE_INFORMATION_AUDIT.md](experimental_foundations/HLS_MINIMAL_REFERENCE_INFORMATION_AUDIT.md) | Information-audit record | CANONICAL for its declared audit scope | Phase-V information partitions, 2×2×2 algebraic reduction, scalar-decision numerical audit, and stated robustness limit. | General HLS sufficiency, a new mathematical theory, or results beyond the stated model/family. |
| [experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md](experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md) | G3 analytical ground truth | CANONICAL for its declared G3 scope | 3-worker assignment operators, exact organizational development value, standard-sensitivity reduction, the closed G3-H future-opportunity counterexample, and the post-closure C1/C2 boundary: C1 is falsified and C2 reduces to look-ahead/DP. | A general assignment theory, an HLS-specific representation claim, or an intermediate exact mechanism. |
| [experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md) | Detailed synthetic reference | FROZEN REFERENCE | A1/G0/C1--C5 specifications and gate provenance. | Sole current status source; it includes historical material. |
| [experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md) | RQ0 campaign record | SUPPORTING / HISTORICAL | Chronology and evidence pointers for RQ0 work. | Current programme priority if it differs from Current State. |
| [models/model_M0.md](models/model_M0.md) | M0 model record | SUPPORTING | M0 assumptions and reproduction context. | Core HLS theory or active RQ0 authority. |
| [models/model_M0_1_gap_dependent_learning.md](models/model_M0_1_gap_dependent_learning.md) | M0.1 model record | SUPPORTING | M0.1 assumptions and reproduction context. | Core HLS theory or active RQ0 authority. |
| [literature/README.md](literature/README.md) | Literature policy and map | CURRENT | Retained source/audit organization. | Scientific conclusions without consulting source material. |
| [literature/references.bib](literature/references.bib) | Bibliography | CURRENT supporting record | Citation keys and retained references. | Interpretation of a cited source by itself. |
| [experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md](experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md) | Geometry protocol/outcome record | PROTOCOL | Frozen design and result provenance for C(alpha). | The general RQ0 theory. |
| [experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md](experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md) | Coupling protocol/outcome record | PROTOCOL | Frozen routing-to-opportunity intervention provenance. | General statement about all coupling families. |
| [experimental_foundations/RQ0_INTEGRATED_DESIGN.md](experimental_foundations/RQ0_INTEGRATED_DESIGN.md) | Confirmatory design record | PROTOCOL | Declared design and its stated status. | A result statement without reconciling retained artifacts. |

## Scientific architecture map

This is a compact navigation aid, not a restatement of theory.

```text
HLS
├── Beam 1 — organization/use of current competences
│   └── T0–T3 — STATIC HLS (consolidated)
│       └── G1 — canonical static computational ground truth
└── Beam 2 / dynamic interaction
    └── T4–T6 — DYNAMIC HLS (consolidated working foundation)
        └── G2 — canonical minimal constructive/null ground truth
```

T0--T3 are consolidated in [HLS Static Theory](theory/HLS_STATIC_THEORY.md).
T4--T6 form the scoped dynamic working foundation in
[HLS Dynamic Theory](theory/HLS_DYNAMIC_THEORY.md), with G2 as its minimal
constructive/null reference. Its D0/D1/D2 identities have deterministic
computational validation and instantiate the cascade's structural controls.
Neither document claims a universal dynamic model,
irreducible joint management, or validation beyond that scope.

RQ0 is a specific open dynamic research question, not the definition of HLS.
G0 is a policy-neutral synthetic instrument for controlled RQ0 work, not a
universal HLS model. See [Research Questions](research_questions.md),
[RQ0 theory](theory/rq0_routing_integration_boundaries.md), and
[G0](experiments/G0.md).

## Theory → code → test → experiment → result map

### Static T0--T3 / G1

| Layer | Location | Role |
| --- | --- | --- |
| Theory | [theory/HLS_STATIC_THEORY.md](theory/HLS_STATIC_THEORY.md) | Consolidated static T0--T3 foundation. |
| Ground truth | [theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md](theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md) | G1 scope, controls, interpretation, and non-claims. |
| Code | `src/hls/g1_static.py` | G1.1/G1.2 transparent reference model and hull oracle. |
| Tests | `tests/test_g1_static.py` | Exact controls and static geometry/value checks. |
| Runners | `experiments/synthetic/g1/run_g1_1.py`, `run_g1_2.py` | Reproducible static sweeps. |
| Results | `results/foundations/g1_static/` | Tables, figures, summaries, and manifests. |

### Dynamic T4--T6 / G2

| Layer | Location | Role |
| --- | --- | --- |
| Theory | [theory/HLS_DYNAMIC_THEORY.md](theory/HLS_DYNAMIC_THEORY.md) | Consolidated working T4--T6 foundation. |
| Ground truth | [theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md](theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md) | D0/D1/D2 analytical/constructive reference. |
| Code | `src/hls/g2_dynamic.py` | Exact D0/D1/D2 state, frontier, value, and regime evaluation. |
| Tests | `tests/test_g2_dynamic.py` | Analytical identities, nulls, frontiers, regimes, and manifest checks. |
| Runner / results | `experiments/synthetic/g2/run_g2.py`; `results/foundations/g2_dynamic/` | Deterministic sweep, summary, and SHA-256 provenance manifest. |

### A1, G0, C1--C5, and synthetic RQ0

| Line | Theory / contract | Code and tests | Experiments / evidence |
| --- | --- | --- | --- |
| A1 references | [Synthetic Environment](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md) | `src/hls/a1a.py`, `a1b.py`, `a1c.py`; A1 and synthetic tests | `experiments/synthetic/a1a/`, `a1b/`, `a1c/`; `results/foundations/a1b_phase_boundary/`, `a1c_competence_geometry/` |
| G0 and C1--C5 | [G0](experiments/G0.md), frozen detailed record | `src/hls/synthetic/`; `tests/synthetic/`, including C1--C5 tests | Reference-gate evidence and retained foundation results described by the frozen record. |
| RQ0 policy theory | [Routing integration boundaries](theory/rq0_routing_integration_boundaries.md) | Exact synthetic solver and RQ0-related modules/tests under `src/hls/synthetic/`, `tests/synthetic/` | [Campaign record](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md) and retained result artifacts. |
| Routing→opportunity coupling | [Coupling protocol](experimental_foundations/RQ0_ROUTING_OPPORTUNITY_COUPLING_PROTOCOL.md) | `src/hls/synthetic/rq0_opportunity_coupling.py`; `tests/synthetic/test_rq0_opportunity_coupling.py` | `experiments/synthetic/rq0/run_opportunity_coupling.py`; `results/foundations/rq0_routing_opportunity_coupling/` |
| Geometry redistribution / C(alpha) | [Geometry protocol](experimental_foundations/RQ0_GEOMETRY_REDISTRIBUTION_PROTOCOL.md) and RQ0 theory | `src/hls/synthetic/rq0_geometry_redistribution.py`; `tests/synthetic/test_rq0_geometry_redistribution.py` | `experiments/synthetic/rq0/run_geometry_redistribution.py`; `results/foundations/rq0_geometry_redistribution/` |

### Reduced models, mechanism support, and pilot vehicles

| Line | Documentation | Code and tests | Evidence / status |
| --- | --- | --- | --- |
| Minimal dynamic model | [minimal_hls_model.md](theory/minimal_hls_model.md) | No one-to-one implementation is asserted by the theory registry. | Analytical reduced testbed, not general dynamic theory. |
| Operational-development opportunity value | [Opportunity-value theory](theory/operational_development_opportunity_value.md) | `src/hls/development_opportunity_value.py`; `tests/test_development_opportunity_value.py` | `experiments/microverification/` and matching result evidence. |
| M0 / M0.1 | [M0](models/model_M0.md), [M0.1](models/model_M0_1_gap_dependent_learning.md) | `src/hls/m0.py`, `src/hls/m01.py`; `tests/test_m0.py`, `tests/test_m01.py` | `experiments/m0/`, `experiments/m01/`; `results/m0/`, `results/m01/`. Supporting/reproduction-oriented. |
| Empirical/pilot branches | Protocols under [experimental foundations](experimental_foundations/) | `experiments/pilots/` and related tests | `results/pilots/`; treat as vehicle-specific evidence, not current programme truth by directory presence alone. |

## Dynamic material map

| Class | Material | What it establishes | What it does not establish | Current role |
| --- | --- | --- | --- | --- |
| General/current programme | [Current State](HLS_CURRENT_STATE.md), [Research Questions](research_questions.md), [G0](experiments/G0.md) | Official current question, scope, and current synthetic-framework contract. | A universal dynamic model. | Read first for active dynamic work. |
| Minimal adaptive reference scenario | [HLS Minimal Reference Scenario](experimental_foundations/HLS_MINIMAL_REFERENCE_SCENARIO.md) | The documented 2×2×2 scenario, S0--S3 controls, minimality, non-claims, and deterministic reference evaluator. | A G0 redefinition, an experimental campaign, or a claim that HLS policies win. | Canonical scenario specification and first evaluator. |
| Minimal-reference information audit | [HLS Minimal Reference Information Audit](experimental_foundations/HLS_MINIMAL_REFERENCE_INFORMATION_AUDIT.md) | Information partitions, model-scoped `G` reduction, scalar-decision audit, and numerical limits. | General information sufficiency or HLS policy superiority. | Read after the scenario when reconstructing this microscope's completed audit. |
| G3 organizational-value ground truth | [HLS G3 Organizational-Value Ground Truth](experimental_foundations/HLS_G3_ORGANIZATIONAL_VALUE_GROUND_TRUTH.md) | Exact 3-worker assignment formulas, independently checked implementation, finite adversarial audit, and the strong standard-sensitivity reduction. | A general HLS experiment, new HLS theory, or a general reduction beyond G3. | Read after the MIS audit when entering the completed 3×2 analytical reference. |
| Post-baseline G3-H integration audit | [History §10](HISTORY.md#10-g3-h-integration-audit-closed-shortcuts-and-the-local-information-boundary); working-tree `src/hls/g3_h_*`, `experiments/synthetic/g3_h/`, and `results/foundations/g3_h_*` | Auditable post-`8972c3c` regime, local-information, and C-stability diagnostics under frozen G3-H physics. | Canonical theory, an exact local certificate, a new HLS mechanism, or a replacement for the closed G3-H ground truth. | **WORKING / UNTRACKED.** Read History first for status; code/results are supporting evidence pending review. |
| Dynamic foundation and ground truth | [HLS_DYNAMIC_THEORY.md](theory/HLS_DYNAMIC_THEORY.md), [HLS_G2_DYNAMIC_GROUND_TRUTH.md](theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md) | Their stated T4--T6 and D0/D1/D2 scoped analytical boundaries, with deterministic computational validation. | Universal theory, irreducible joint-management result, or validation beyond D0/D1/D2. | Current dynamic analytical/computational baseline. |
| Reduced dynamic testbeds | [minimal_hls_model.md](theory/minimal_hls_model.md), [M0](models/model_M0.md), [M0.1](models/model_M0_1_gap_dependent_learning.md) | Model-scoped separability, threshold, information, and resource-share lessons. | General T4--T6 theory or RQ0 resolution. | Supporting constraints and reproducibility. |
| Exact RQ0 theory | [rq0_routing_integration_boundaries.md](theory/rq0_routing_integration_boundaries.md) | Policy-class criterion, local-versus-root distinction, and scoped C(alpha) construction. | Prevalence, genericity, robustness, or empirical relevance. | Canonical formal reference for the current RQ0 formalization. |
| Mechanism-level support | [operational_development_opportunity_value.md](theory/operational_development_opportunity_value.md) | Conditional opportunity-value decomposition under its assumptions. | That local opportunity value yields global integration value. | Supporting mechanism analysis. |
| Historical diagnostics | [RQ0 campaign record](experimental_foundations/RQ0_EXPERIMENTAL_CAMPAIGN.md), coupling and geometry protocols | Negative diagnostic, persistence, coupling, and frozen-design provenance. | Current priority or conclusions beyond declared worlds. | Evidence and anti-post-hoc traceability. |
| Experimental/vehicle material | Pilot protocols, `experiments/pilots/`, and `results/pilots/` | Vehicle-specific feasibility or scoped results where documented. | Current HLS scientific state. | Supporting/historical evidence. |

## Current sources of truth

For current programme reconstruction, use this order of authority:

1. [HLS Philosophy](HLS_PHILOSOPHY.md) for the programme compass.
2. [Research Doctrine](../RESEARCH_DOCTRINE.md) for methodological discipline.
3. [HLS Ontology](hls_ontology.md) for semantic consistency.
4. [Research Questions](research_questions.md) for official active questions.
5. [HLS Current State](HLS_CURRENT_STATE.md) for established/open current science.
6. [Theory registry](theory/README.md) and the individual cited theory for
   formal, scoped results.
7. [Experiments registry](experiments/README.md), G0, code, tests, and result
   artifacts for implementation and reproducibility.

## Historical, supporting, and provenance material

[History](HISTORY.md), frozen reference records, campaign ledgers, protocols,
model records, pilots, and results preserve assumptions, negative evidence,
reproducibility, and chronology. They do not supersede current sources unless a
canonical document explicitly promotes their claim.

**Rule:** when reconstructing current scientific state, always read
[HLS Current State](HLS_CURRENT_STATE.md) before a historical campaign,
protocol, pilot, or historical section of
[HLS Synthetic Environment](experimental_foundations/HLS_SYNTHETIC_ENVIRONMENT.md).

## Known documentation debt and safe interpretation

| Issue | Risk | Authoritative source / safe interpretation | Action status |
| --- | --- | --- | --- |
| Sections 26--27 of the Synthetic Environment retain historical C1 wording that can appear inconsistent with later gate sections 28--29. | Historical pre-implementation language may be mistaken for current C1 status. | Use the frozen-record status, later gate sections, [G0](experiments/G0.md), and [Current State](HLS_CURRENT_STATE.md). | Documentation debt. |
| The RQ0 campaign record contains an earlier immediate-task framing. | It can be read as current programme priority. | Current State is designated the single current-status summary. | Documentation debt. |
| B23/B24 protocol statuses do not obviously align with existing pilot result directories and historical summaries. | Directory presence may be mistaken for completed or confirmatory protocol execution. | Read protocol status literally; use History and artifacts only for their declared scope. | Provenance clarification needed. |
| `RQ0_INTEGRATED_DESIGN.md` is labelled pre-test while confirmatory artifacts are retained. | The protocol-to-artifact relation is ambiguous. | Treat the protocol as a protocol, not as a result statement, until reconciled. | Provenance clarification needed. |
| B23 names `results/pilots/b22_opportunity_value/b22_diagnostic.md` and `.../portfolio_bridge/portfolio_bridge.md`, which are absent. | Dead-end reproduction/navigation references. | Do not infer missing contents; use retained B22/B23 material. | Unresolved documentation debt. |
| [experiments/README.md](experiments/README.md) does not index G1. | Static ground-truth evidence is harder to discover from the experiment registry. | Navigate through [theory/README.md](theory/README.md) and G1's theory document. | Documentation debt. |
| [HLS Static Theory](theory/HLS_STATIC_THEORY.md) contains raw `{=tex}` rendering artifacts. | Display degradation may obscure notation. | Use source text and linked ground-truth documentation. | Documentation debt. |

## Recommended reading path

### Core

1. [README](../README.md) — entry point and navigation.
2. [HLS Philosophy](HLS_PHILOSOPHY.md) — programme compass and two beams.
3. [Research Doctrine](../RESEARCH_DOCTRINE.md) — claim discipline and method.
4. [HLS Ontology](hls_ontology.md) — semantic mapping discipline.
5. [Research Questions](research_questions.md) — official active question.
6. [HLS Current State](HLS_CURRENT_STATE.md) — established and open science.
7. This guide — locate formal, executable, and evidentiary material.

### Static HLS

8. [HLS Static Theory](theory/HLS_STATIC_THEORY.md).
9. [G1 Static Experimental Ground Truth](theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md).
10. `src/hls/g1_static.py`, `tests/test_g1_static.py`, and
    `experiments/synthetic/g1/` only when implementation or reproduction is needed.

### Dynamic HLS

11. [HLS Dynamic Theoretical Foundation](theory/HLS_DYNAMIC_THEORY.md) and
    [G2 Dynamic Ground Truth](theory/HLS_G2_DYNAMIC_GROUND_TRUTH.md).
12. [Minimal HLS model](theory/minimal_hls_model.md) for reduced boundary lessons.
13. [RQ0 routing integration boundaries](theory/rq0_routing_integration_boundaries.md)
    for the canonical RQ0 formalization.
14. [Operational-development opportunity value](theory/operational_development_opportunity_value.md)
    for supporting mechanism analysis.
15. [G0](experiments/G0.md) only when studying the current RQ0 synthetic instrument.

Read History, frozen protocols, campaign material, and pilots only when a claim
requires provenance or a specific reproduction path.

## Maintenance rule

Update this guide only when a path, authority relationship, implementation
mapping, or explicitly documented documentation-debt item changes. Put new
scientific claims, theory, protocols, or results in their designated source;
then update this guide only if navigation or provenance has changed.
