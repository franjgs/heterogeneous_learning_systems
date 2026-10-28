# Research chronology and decision record

This project log distinguishes instruction/decision dates from commit dates. The initial project request was received on **2026-10-27**. No earlier SOC/AIAI project events are inferred from file dates or Git history.

## 2026-10-27 — project preparation initiated

- **Event:** request to create an independent SOC/AIAI research space on branch `research/soc-human-ai-organization`, based on the HLS scientific core.
- **Scope received:** study heterogeneous cyberanalyst competence, task assignment/specialization, training and learning costs/opportunity costs, constrained capacity/service/deadlines, changing clients/threats, resilience/adaptation and AI assistance.
- **Decision status:** preparatory organization and documentation authorized by the task instruction; no experiment, simulator, algorithm or results authorized. Questions and mechanisms in the project documents remain proposals until scientifically reviewed.
- **Editorial target received:** *Electronics*, Special Issue “Timely AI Advancements and Interdisciplinary Synergies for Intelligent Modeling”; deadline described by the instruction as March 2027. Official flyer checked on 2026-10-27 gives 15 March 2027 and minimum 50% expansion for extended AIAI/EAAAI 2026 contributions. Editorial fit and eligibility are not established.
- **Baseline:** core branch at `319098d585d8a7f32cd1f8d978807366b581a21b`; new branch created from it. HLS core sources and the historical source archive were consulted.
- **Governance qualification:** the historical [team handover protocol](https://github.com/franjgs/heterogeneous_learning_systems/blob/c81def3b5280b0f59d6dcbfd3e25df8805f5013c/docs/team/HLS_TEAM_HANDOVER_PROTOCOL.md), [role register](https://github.com/franjgs/heterogeneous_learning_systems/blob/c81def3b5280b0f59d6dcbfd3e25df8805f5013c/docs/team/HLS_ROLE_REGISTER.md) and [PI handover record](https://github.com/franjgs/heterogeneous_learning_systems/blob/c81def3b5280b0f59d6dcbfd3e25df8805f5013c/docs/team/handovers/2026-10-24_replace_pi.md) in archive commit `c81def3b5280b0f59d6dcbfd3e25df8805f5013c` record PI identity as uninitialized and a PI handover as pending. This project records the received instruction's scope without inferring a named PI identity. Further scientific decisions require PI review.
- **AIAI provenance:** exact base article not identified in the accessible core or historical [scientific audit](https://github.com/franjgs/heterogeneous_learning_systems/blob/c81def3b5280b0f59d6dcbfd3e25df8805f5013c/docs/research/HLS_COMPREHENSIVE_SCIENTIFIC_AUDIT_2026-10-26.md). This was the status at initial project setup; source recovery and the overlap review were later completed on 2026-10-27 (see the dated entry below).
- **Tracking:** [Issue #2](https://github.com/franjgs/heterogeneous_learning_systems/issues/2) created to track article identification, PI review, data/ethics permissions and future protocol readiness; [draft PR #3](https://github.com/franjgs/heterogeneous_learning_systems/pull/3) opened against the core branch for PI review and left unmerged.

## 2026-10-27 — AIAI/SOCTRA sources recovered and analyzed

- **Event:** reviewed the Springer proceedings chapter, author versions, requested conference deck, selected SOCTRA technical deliverables, internal triage manuscript and LSE implementation snapshots.
- **Published record:** identified the AIAI chapter by DOI `10.1007/978-3-032-30805-4_11`; it reports retrospective L1 escalation/reporting classifier evaluation. Its results are not findings of this HLS project.
- **Separate SOCTRA evidence:** internal manuscript/code sources contain LSEnsemble experiments absent from the AIAI chapter. They are classified as unpublished/internal, and configuration/provenance discrepancies remain. No experiment was run.
- **Operational context:** project materials describe L1 triage and L2 deep analysis and changing monitoring availability; these inform a proposed scenario but require permission and validation for the intended target setting.
- **Capacity claim:** the PI clarified that SOCTRA demonstrated a reduction in operational triage burden. This is distinguished from a quantified reduction in analyst minutes, queue capacity or staffing, which was not located in the reviewed sources. Classification metrics alone do not quantify labor savings. Numerical capacity release in future simulation remains a separate explicit assumption unless measured.
- **Research positioning:** separate (1) triage classifiers, (2) the operational effect of the tool, and (3) team organization using capacity made available or assumed. The candidate main HLS contribution is level 3. LSEnsemble is an imbalanced-classification method, not an organizational policy.
- **Publication caveat:** a separate internal journal-manuscript package exists; current editorial status is unknown. Check author/editor permissions and overlap before preparing an Electronics submission.
- **Evidence record:** [AIAI 2026 source analysis](AIAI_2026_ANALYSIS.md), based on local source files and hashes listed there. No source file was copied, modified, or redistributed by this work.

## 2026-10-28 — Empirical alert-demand characterization prepared

- **Event:** read-only characterization of the local SOCTRA/GMV-CERT alert CSV snapshots for HLS scenario dimensioning.
- **Method:** used the latest dated snapshot only after verifying that the exports are cumulative, that earlier alert-ID sets are nested within it, and that the two latest files are identical. Aggregated temporal volumes, project concentration, category cardinalities and historical escalation/report labels; no row or identifier was copied.
- **Finding:** the extract supports an empirical demand trace and a historical count of 27 project labels, but not analyst headcount, L1/L2 staffing, service-time or shift estimates. The PI-confirmed SOCTRA triage-burden reduction is kept distinct from any numerical capacity-release input in future simulation.
- **Status:** local report prepared for PI review only; aggregate disclosure authorization remains required before commit or external sharing. No simulator, model training, or experiment was run.
- **Evidence record:** [Demand characterization and HLS sizing proposal](DEMAND_CHARACTERIZATION.md). The source dataset remains at its restricted local location and is not included in Git.

## 2026-10-28 — Analyst and experience-field verification

- **Event:** audited the consolidated alert snapshot against SOCTRA preprocessing and contextual-feature code.
- **Finding:** the snapshot has 91 distinct non-empty `tramitador` values, but this does not establish 91 people or prove decision authorship. Expertise-named fields are precomputed sample weights; their reproducible derivation as experience/competence measures was not found. Handler/project/timestamp can reconstruct alert associations, not complete labor histories. Rolling per-handler counts in code measure prior alert-record intensity, not active workload or service hours.
- **Status:** local aggregate-only report prepared for PI review; no identifiers reproduced and no data copied. Disclosure permission is still required before publication. No model or simulation was run.
- **Evidence record:** [Analyst identifier, experience and workload audit](ANALYST_EXPERIENCE_AUDIT.md).

## 2026-10-28 — Deep audit of handler experience and weight provenance

- **Event:** extended the prior audit with the SOCTRA Stage 3 deliverable, the Stage 3 design document, the Stage 2 data schema, all cumulative alert snapshots, `weight_matrix.csv`, and the available preprocessing/model runner code. This is a same-day evidential supplement, not a new experiment.
- **Correction/qualification to the earlier entry:** a static tier proposal is documented in `WP4_SOCTRA_Entregable_Etapa3_v1.docx` §4.2 (project/global activity thresholds and a CERT expert-list override). It is not a reproducible implementation: thresholds overlap, counting units are inconsistent in the prose, the expert list and as-of dates are unavailable, and no code/data lineage proves that it generated the current matrix. The dynamic expertise-weight narrative still has no exact update formula. The earlier statement that no formula was found applies to a reproducible generator; the static proposal itself is now located and recorded accurately.
- **Findings:** the final snapshot contains 214,739 unique alert IDs, 91 distinct handler-label values, 27 project labels and 1,341 active handler–project pairs. Activity is concentrated (operator-label Gini 0.554; top ten labels account for 33.1% of rows). These describe recorded associations, not verified people, competence or labor capacity. Expertise weights rise monotonically within most timestamp-collapsed pairs and associate with strictly prior activity, but this is compatible with a count-based weight rule and does not establish learning. Old snapshots recode the handler field; March has many-to-many label mappings. Same-timestamp weight conflicts covary with counters, while the two decision labels remain constant in those groups.
- **Methodological risk:** the available training runner applies dynamic label uniformization to the full loaded dataset before its date split (`flag_uniform=True`, `mode_uniform='dynamic'`). The uniformization procedure uses labels across matching feature patterns, so future/validation/test labels can influence transformed labels when patterns overlap. This is a pipeline leakage risk separate from the provenance of the experience weights; it is not evidence that published SOCTRA outcomes were affected without checking the exact run/configuration artifacts.
- **Status:** aggregate-only findings and three identifier-free figures are local for PI review. No raw data, individual identifiers or per-person tables were added; no HLS model or simulation was run; no commit or push was made. Disclosure authorization remains pending.
- **Evidence record:** [expanded analyst experience audit](ANALYST_EXPERIENCE_AUDIT.md); aggregate figures in `restricted_local_figures/`.

## 2026-10-28 — PI clarified the empirical role of SOCTRA and the provisional competence state

- **Decision received:** the study will not reconstruct GMV-CERT's actual organization, historical individual assignments, staffing or analyst careers. The alert dataset is for aggregate anchoring of problem scale, temporal demand and project/task-label structure; its operator and weight fields are not a target organizational history.
- **Modeling decision:** record `C(t) ∈ ℝ^(N×P)` as a provisional competence-state hypothesis, where `N` and `P` are parameters of a future model. The 91 handler labels and 27 historical project labels do not set `N` or `P`; SOCTRA weights and exposure are not competence measurements. No competence distributions, update law, service times, availability or AI capacity-release values were selected.
- **Documentation:** consolidated the study framing, observed/derived quantities, assumptions, limits and next milestone in the existing [scientific synthesis](MODEL_AND_SCENARIO.md); the demand and experience audits remain detailed supporting records. No new core/catalog entity was warranted because no model, experiment or result was added.
- **Authorization boundary:** the next milestone is model design only (state, decisions, constraints, dynamics, evaluation and comparisons). This record does not authorize implementation, simulation or model training. No data were copied, and the changes remain local for PI review.
- **Timestamp:** recorded at 2026-10-28 20:28:21 CET (+0100). This is the documentation time; the PI decision's exact adoption time is not independently known.
- **Evidence:** PI instruction received 2026-10-28; aggregate sources and qualifications are linked from the [scientific synthesis](MODEL_AND_SCENARIO.md). No experiment occurred.

## 2026-10-28 — Aggregate documentation approved for repository closure

- **Event:** the PI authorized committing and pushing the SOC study documentation prepared in this phase, including the SOCTRA demand characterization, handler/experience audit and anonymous aggregate figures, AIAI/SOCTRA source analysis, scientific synthesis, and related study-document updates.
- **Scope and exclusions:** source CSVs, row-level data, project labels, personal identifiers and individual profiles are excluded. No HLS core files were changed. The authorization is for this repository and its review PR; it does not establish data-owner clearance for other uses or permission to reuse internal SOCTRA material in a manuscript.
- **Status:** documentation-only closure; no experiment, model implementation or training was performed. PR #3 remains open and in draft; no merge is authorized.
- **Timestamp:** 2026-10-28 20:33:15 CET (+0100), documentation time. The exact time of the PI's authorization is not independently known.
- **Evidence:** PI closure instruction received 2026-10-28; included files and commit recorded in Git.

## Decision ledger

| ID | Date | Record | Status / scope |
|---|---|---|---|
| D-01 | 2026-10-27 | Establish this independent SOC human–AI organization research space. | Preparatory scope received; does not alter HLS core or scientific philosophy. |
| D-02 | 2026-10-27 | Use the stated *Electronics* Special Issue as an editorial target; deadline March 2027. | Target only. Officially observed deadline: 15 March 2027; no fit/acceptance guarantee. |
| D-03 | 2026-10-27 | Treat proposed extension of an AIAI 2026 article as a goal to investigate. | Baseline later identified; extension/eligibility and internal manuscript overlap remain subject to author/editor review. |
| D-04 | 2026-10-27 | Keep work within documentation and preparation. | No implementation, simulator, algorithm or experiment authorized. |

## Future entries

Record a later event only with its actual date and source. Required milestones include: PI disposition/review; exact AIAI article and overlap map; data-access/ethics decisions; protocol approval; implementation commit; experiment authorization/execution; result and analysis status; and any publication submission decision. Never infer scientific event dates from commit timestamps.
