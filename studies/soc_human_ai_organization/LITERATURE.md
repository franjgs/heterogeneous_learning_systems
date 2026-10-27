# Literature and publication positioning

This project reuses the core bibliography at [`references/hls.bib`](../../references/hls.bib) and the HLS synthesis in [`docs/LITERATURE.md`](../../docs/LITERATURE.md). Citation keys below resolve there. References motivate candidate constructs; they do not prove that a mechanism operates in the target SOC.

## Established mechanisms relevant to the study

1. **Multi-skill assignment and resource-constrained scheduling.** Multi-skill scheduling formalizes matching skill requirements, workers, tasks and capacity; model choices change the feasible problem and objective [@almeida2019multiskill]. Candidate use: compare assignment under competence and workload constraints. It does not supply SOC task taxonomies or competence values.
2. **Organizational learning and transfer.** Organizational-learning work distinguishes experience, knowledge retention and transfer [@argote2011organizational]. Candidate use: represent where knowledge resides, how it persists and who can access it. Experience alone is not a learning outcome.
3. **Workforce allocation with learning/training.** Prior work studies selection/grouping with learning-by-doing and knowledge transfer [@nembhard2015selection], and dynamic task allocation with endogenous training [@baccara2023task]. Candidate use: account for training and mentor opportunity cost as well as service output. These models' mechanisms and populations must be mapped before reuse.
4. **Human investigation workflow and alert evidence.** Kersten et al. report a field study and support tool for Tier-1 alert investigations in one commercial SOC [@kersten2025tier1]. Yang et al. analyze multi-year alert logs and attack ground truth from a different SOC [@yang2024socalerts]. They provide empirical context that investigation varies and alert labels/outcomes are nuanced; they do not identify the workflow, data or competence structure of this project's client.

AI assistance is a treatment/context candidate, not one mechanism with a guaranteed positive effect. A future study must distinguish AI availability from actual use, recommendation quality, reliance, override, time saved, learning effects and downstream error costs.

## AIAI 2026 baseline and intended extension

The instruction states that this work is intended to extend an AIAI 2026 article. Searches of the active core and the accessible historical source branch did not identify that article's title, authors, DOI, full text, tables, methods, data or code. The archive audit mentions SOCTRA only to warn that no verified schema supports attributing analyst competence, alert routes, service times or training history to it. No AIAI 2026 organizational-learning benefit was found in the accessible record.

Consequently, the following are **proposed extension axes**, not verified differences from the article:

| Intended addition | Comparison needed once the AIAI paper is identified |
|---|---|
| Organization and task allocation across L1/L2 | Determine whether the paper already models analyst assignment, roles, handoffs or capacity. |
| Competence development and training | Compare competence state, learning law, mentor time, direct training cost and displaced work. |
| Client/threat/technology change and adaptation | Compare populations, temporal dynamics, generalization tests and evaluation horizon. |
| Cost and opportunity-cost accounting | Identify whether analyst/mentor capacity and operational trade-offs were measured. |
| Human–AI assistance effects | Compare the AI role, human decision rights, baselines, assistance exposure and error evaluation. |

Before using “extended version,” retrieve the exact accepted/published AIAI paper and conference rules, make a section/table/figure/result overlap map, cite the conference paper, and document substantive additions. The Special Issue flyer says expanded AIAI/EAAAI 2026 contributions need at least a 50% increase. The rule's application to a particular manuscript and the conference's own publication terms must still be checked with the editors/authors.

## Editorial target: verified status on 2026-10-27

- **Journal:** *Electronics* (MDPI), open access. Its scope includes Artificial Intelligence, Computer Science & Engineering, Networks and Systems & Control Engineering; this makes topical alignment plausible but does not guarantee fit. The work must present a clear electronics/AI/intelligent-modeling contribution, not only a generic workforce management study. [Aims & Scope](https://www.mdpi.com/journal/electronics/about)
- **Special Issue:** “Timely AI Advancements and Interdisciplinary Synergies for Intelligent Modeling.” The official flyer describes AI theory, engineering/environmental applications including cyber security, interdisciplinary synergies and methodological evaluation/scaling; it welcomes expanded EAAAI/AIAI 2026 papers with a minimum 50% increase. [Special Issue page](https://www.mdpi.com/journal/electronics/special_issues/MET7IZ3S8B) · [official flyer](https://www.mdpi.com/journal/electronics/special_issue_flyer_pdf_v2/MET7IZ3S8B)
- **Submission deadline:** 15 March 2027 according to the flyer. The project order also states March 2027. Recheck the live page before submission.
- **Fit assessment:** possible, not established. The proposed human–AI SOC application intersects cyber security and AI, but a paper must make a substantive intelligent-modeling/AI contribution and distinguish itself from the AIAI source paper and relevant SOC/workforce literature. Editor confirmation is not available.

## Requirements to carry into any submission

The current [Electronics author instructions](https://www.mdpi.com/journal/Electronics/instructions) call for research articles to include title/authors/affiliations, abstract and keywords, Introduction, Materials and Methods, Results, Discussion and optional Conclusions, plus supplementary material, author contributions, funding, a Data Availability Statement, acknowledgements, conflicts and references. They require sufficient experimental/method detail, software/version disclosure and a Data Availability Statement; data should be deposited where possible. If privacy, legal or ethical restrictions prevent release, explain them specifically and provide the required access statement. The instructions recommend repositories with persistent identifiers and note external hosting for large datasets. Confirm current rules and article type at submission.

For this study, reproducibility planning must cover de-identification and data rights, approved access and retention, dataset/code/configuration versions and hashes, baseline article provenance, preregistration where used, model/tool versions, prompts or AI settings where relevant, random seeds, complete evaluation definitions, all controls and adverse/negative results. No data are currently acquired or approved for sharing. Do not promise public release before permissions are known.

## Unresolved bibliography/positioning tasks

- Identify and verify the exact AIAI 2026 article and its publication/licensing terms.
- Review related SOC workforce assignment, analyst competence measurement, training, workload/well-being and human–AI decision support literature against the proposed questions.
- Reassess Special Issue scope and deadline near submission; no suitability or acceptance is presumed.
