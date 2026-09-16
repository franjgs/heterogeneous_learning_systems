# Literature collection

This directory separates the project bibliography, structured synthesis, and
local source documents.

## Bibliography policy

`references.bib` is the master project bibliography.  Entries are added only
after their metadata has been checked against a primary source, publisher
record, proceedings record, or the local source PDF.  A paper or technical note
may keep a smaller local bibliography for portable compilation, but every entry
it uses must agree in citation key and bibliographic metadata with the master
file.  Local bibliographies are curated subsets, not competing authorities.

`literature_map.md` remains the cross-reference map.  Add a note under
`notes/` only for a reference that is active enough to need a source-result,
assumption, mathematical-content, HLS-translation, and limitation record.

## Source-document categories

- `competence_organization/`: sources primarily about distributed knowledge,
  organization, allocation, hierarchy, or comparative advantage.
- `competence_evolution/`: sources primarily about learning from experience,
  training, transfer, depreciation, or dynamic competence development.
- `cross_cutting/`: sources that materially connect both concerns or provide
  learner-aware teaching mechanisms.

These categories describe scientific content, not a claim that every document
is part of the current two-beam theoretical skeleton.

## PDF naming and migration integrity record

Local PDFs use `Author_Year_ShortTitle.pdf`: one surname for a sole author,
both surnames for two authors, and `FirstAuthor_et_al` for three or more.  Names
use ASCII letters, digits, and underscores; venue belongs in BibTeX rather than
the filename.  A suffix such as `a`/`b` or `__Publisher` is used only when its
bibliographic or source-version meaning has been verified.

The following SHA-256 values were computed before the 2026-09-16 migration.
They preserve provenance from the former paths and are also the post-migration
verification targets.

| Former path | SHA-256 | Current path / disposition |
| --- | --- | --- |
| `Argote-OrganizationalLearningExperience-2011.pdf` | `27a7006f4535d79fd1066b95d77f005732227d99e8fadc42e4a05667f3aa19f5` | `competence_evolution/Argote_MironSpektor_2011_Organizational_Learning_Experience_Knowledge.pdf` |
| `Competences Organization/Garicano (2000), Hierarchies and the Organization of Knowledge in Production_317671.link.pdf` | `8af34b8d4b72784befc4e9749696b0d86214a754b14d49bf104b54b95e310426` | `competence_organization/Garicano_2000_Hierarchies_Organization_Knowledge.pdf` |
| `Competences Evolution/Gibbons & Waldman_Theory of Wage and Promotion Dynamics.pdf` | `8c64e9f7a34295f82c5884c78a00c53d5a12d4d116f5adf0a14d5ad1f224b57b` | `competence_evolution/Gibbons_Waldman_1999_Wage_Promotion_Dynamics.pdf` |
| `Competences Evolution/Jovanovic (1995), The transfer of human capital.pdf` | `2a9afac041f572f582c7f3f314c9e1eb73c6f232aad973eb8e47ba6336f07b02` | `competence_evolution/Jovanovic_Nyarko_1995_Transfer_Human_Capital.pdf` |
| `Competences Evolution/Optimal dynamic portfolio selection for projects under a competence development model.pdf` | `50787069b72bfccb05aa07caed2c80d702cf29deff4a9ad0fbc0fcaccdaad673` | `competence_evolution/Gutjahr_2011_Dynamic_Portfolio_Competence_Development.pdf` |
| `Competences Evolution/Selection, grouping, and assignment policies with learning-by-doing and knowledge transfer.pdf` | `84c0404d9b15391fea6e4ea20d896d63935fe300ec1617a8a16b368cc4b82354` | semantic duplicate of the retained copy; removed after exact extracted-text comparison |
| `J Management Studies - 2012 - Argote - Transactive Memory Systems  A Microfoundation of Dynamic Capabilities.pdf` | `7f5a1fb0933abe5b8db5c638a7a6e896250cd3c6ca776643f7bc106a290607cc` | `competence_organization/Argote_Ren_2012_Transactive_Memory_Dynamic_Capabilities.pdf` |
| `Multi-objective decision analysis for competence-oriented project portfolio selection.pdf` | `0419d6d038995687be33a3164afd4e7b40a8106c7a1834192ff7af7fab5253fe` | `competence_evolution/Gutjahr_et_al_2010_Multiobjective_Competence_Portfolio_Selection.pdf` |
| `Selection, grouping, and assignment policies with learning-by-doing and knowledge transfer.pdf` | `30129963aa6b69197140552b9431480b7b976d5c3d521eabbe3ec63478402e81` | `competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf` |
| `Task-Specific Technical Change and Comparative Advantage.pdf` | `4be164ecaf0fb2f5e1548cd49e7c31923ad96cff0c04608db0096efa6a95cb20` | `competence_organization/Althoff_Reichardt_2026_TaskSpecific_Technical_Change_Comparative_Advantage.pdf` |
| `The impact of dynamic learning and training on the personnel staffing decision.pdf` | `3e4fe7976dcbe91b634b2b66b798011168cf42d595b12e73436644b3e1a5d95f` | `competence_evolution/Borgonjon_Maenhout_2024_Dynamic_Learning_Training_Staffing.pdf` |
| `tborck_AAAI-YeoT.3343.pdf` | `bf4a07ca78d961b1c8a6f129a43acb86e312d4e2980ba151ab3ed0824b20ea91` | `cross_cutting/Yeo_et_al_2019_Iterative_Classroom_Teaching.pdf` |

The two Nembhard--Bentefouet copies had different byte hashes but the same
13-page extracted text (SHA-256
`ec71ae4089731b055b5bf75de6df946d652a0be4a2aad307d788ee5c6f361777`).
No publisher/version distinction was evidenced by the PDFs, so one canonical
copy is retained rather than inventing a source-version suffix.
