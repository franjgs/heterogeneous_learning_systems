# Literature and publication positioning

This project reuses the core bibliography at [`references/hls.bib`](../../references/hls.bib) and the HLS synthesis in [`docs/LITERATURE.md`](../../docs/LITERATURE.md). Citation keys below resolve there. References motivate candidate constructs; they do not prove that a mechanism operates in the target SOC.

## Established mechanisms relevant to the study

1. **Multi-skill assignment and resource-constrained scheduling.** Multi-skill scheduling formalizes matching skill requirements, workers, tasks and capacity; model choices change the feasible problem and objective [@almeida2019multiskill]. Candidate use: compare assignment under competence and workload constraints. It does not supply SOC task taxonomies or competence values.
2. **Organizational learning and transfer.** Organizational-learning work distinguishes experience, knowledge retention and transfer [@argote2011organizational]. Candidate use: represent where knowledge resides, how it persists and who can access it. Experience alone is not a learning outcome.
3. **Workforce allocation with learning/training.** Prior work studies selection/grouping with learning-by-doing and knowledge transfer [@nembhard2015selection], and dynamic task allocation with endogenous training [@baccara2023task]. Candidate use: account for training and mentor opportunity cost as well as service output. These models' mechanisms and populations must be mapped before reuse.
4. **Human investigation workflow and alert evidence.** Kersten et al. report a field study and support tool for Tier-1 alert investigations in one commercial SOC [@kersten2025tier1]. Yang et al. analyze multi-year alert logs and attack ground truth from a different SOC [@yang2024socalerts]. They provide empirical context that investigation varies and alert labels/outcomes are nuanced; they do not identify the workflow, data or competence structure of this project's client.

AI assistance is a treatment/context candidate, not one mechanism with a guaranteed positive effect. A future study must distinguish AI availability from actual use, recommendation quality, reliance, override, time saved, learning effects and downstream error costs.

## AIAI 2026 baseline and intended extension

The exact published baseline has now been identified: Lázaro et al., “AI-Driven Alert Triage in Security Operations Centers: Imbalanced Learning with Human-in-the-Loop Contextual Bias Modeling,” Springer AIAI 2026 chapter, pp. 150–164, DOI [10.1007/978-3-032-30805-4_11](https://doi.org/10.1007/978-3-032-30805-4_11). The [source analysis](AIAI_2026_ANALYSIS.md) records the inventory and separates published results from additional internal SOCTRA experiments and operational descriptions.

The article evaluates L1 escalation/reporting classification. It does not test workforce allocation, training, organizational adaptation, or a controlled human–AI intervention. A separate internal SOCTRA manuscript/code snapshot includes Label Switching Ensemble (LSEnsemble) and asymmetric-cost experiments not in the AIAI chapter. Those are not AIAI-published evidence; parameter/provenance differences remain unresolved, and current editorial status of the separate manuscript must be confirmed before overlap with an Electronics submission is decided. LSE is a classifier, not an organizational mechanism.

The presentation and SOCTRA technical deliverables provide richer project-specific L1/L2 and operational-context descriptions than the paper. They are internal sources and do not establish that every described process is valid for a target client or that analyst labor/time was reduced. The paper’s retrospective classification metrics are not measured workload savings. See the source analysis for scope and limitations.

| Intended addition | Difference required relative to the identified AIAI baseline |
|---|---|
| Organization and task allocation across L1/L2 | Determine whether the paper already models analyst assignment, roles, handoffs or capacity. |
| Competence development and training | Compare competence state, learning law, mentor time, direct training cost and displaced work. |
| Client/threat/technology change and adaptation | Compare populations, temporal dynamics, generalization tests and evaluation horizon. |
| Cost and opportunity-cost accounting | Identify whether analyst/mentor capacity and operational trade-offs were measured. |
| Human–AI assistance effects | Compare the AI role, human decision rights, baselines, assistance exposure and error evaluation. |

Before using “extended version,” make a section/table/figure/result overlap map against the published Springer chapter and the separate internal journal-manuscript snapshot; confirm that manuscript’s current status and permissions with its authors/editors. Cite the Springer chapter and document substantive new evidence. The Special Issue flyer says expanded AIAI/EAAAI 2026 contributions need at least a 50% increase. The rule's application to a particular manuscript and the conference's own publication terms must still be checked with the editors/authors.

## Editorial target: verified status on 2026-10-27

- **Journal:** *Electronics* (MDPI), open access. Its scope includes Artificial Intelligence, Computer Science & Engineering, Networks and Systems & Control Engineering; this makes topical alignment plausible but does not guarantee fit. The work must present a clear electronics/AI/intelligent-modeling contribution, not only a generic workforce management study. [Aims & Scope](https://www.mdpi.com/journal/electronics/about)
- **Special Issue:** “Timely AI Advancements and Interdisciplinary Synergies for Intelligent Modeling.” The official flyer describes AI theory, engineering/environmental applications including cyber security, interdisciplinary synergies and methodological evaluation/scaling; it welcomes expanded EAAAI/AIAI 2026 papers with a minimum 50% increase. [Special Issue page](https://www.mdpi.com/journal/electronics/special_issues/MET7IZ3S8B) · [official flyer](https://www.mdpi.com/journal/electronics/special_issue_flyer_pdf_v2/MET7IZ3S8B)
- **Submission deadline:** 15 March 2027 according to the flyer. The project order also states March 2027. Recheck the live page before submission.
- **Fit assessment:** possible, not established. A team-organization contribution may fit only if it makes a clear intelligent-modeling contribution and is distinguished from the AIAI chapter, the internal triage manuscript and SOC/workforce literature. Editor confirmation is not available.

## Requirements to carry into any submission

The current [Electronics author instructions](https://www.mdpi.com/journal/Electronics/instructions) call for research articles to include title/authors/affiliations, abstract and keywords, Introduction, Materials and Methods, Results, Discussion and optional Conclusions, plus supplementary material, author contributions, funding, a Data Availability Statement, acknowledgements, conflicts and references. They require sufficient experimental/method detail, software/version disclosure and a Data Availability Statement; data should be deposited where possible. If privacy, legal or ethical restrictions prevent release, explain them specifically and provide the required access statement. The instructions recommend repositories with persistent identifiers and note external hosting for large datasets. Confirm current rules and article type at submission.

For this study, reproducibility planning must cover de-identification and data rights, approved access and retention, dataset/code/configuration versions and hashes, baseline article provenance, preregistration where used, model/tool versions, prompts or AI settings where relevant, random seeds, complete evaluation definitions, all controls and adverse/negative results. No data are currently acquired or approved for sharing. Do not promise public release before permissions are known.

## Unresolved bibliography/positioning tasks

- Confirm which deck version was actually presented and obtain permission before reuse of internal presentation material.
- Review related SOC workforce assignment, analyst competence measurement, training, workload/well-being and human–AI decision support literature against the proposed questions.
- Reassess Special Issue scope and deadline near submission; no suitability or acceptance is presumed.
