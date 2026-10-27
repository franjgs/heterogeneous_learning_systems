# Heterogeneous Learning Systems (HLS)

HLS is a general research programme studying how heterogeneous capabilities are distributed, organized, accessed, used, combined and developed to solve problems under constraints. Its central question is how individual properties and organizational choices jointly shape attainable and realized collective performance.

HLS is not a particular algorithm, simulator, application or agent architecture. Its four scientific responsibilities are **scenarios** (problem, environment and constraints), **organizations** (entities, roles and coordination), **models** (assumptions and outcome/state laws), and **performance evaluation** (estimands, metrics and comparisons). They are connected concepts, not a requirement for four software packages. Human teams, industrial systems, software agents, AI systems and hybrid organizations are possible applications; none defines HLS.

## What this laboratory contains

The active core is deliberately small: two exact finite mathematical models with executable checks, a structured catalog and validator, and a record that distinguishes current runnable evidence from findings documented only in the historical archive. The finite constructions demonstrate model-scoped results: task-wise allocation can improve attainable outcomes in a crossed-specialization case, while state change need not change the efficient frontier and future value can reverse an immediate choice. Historical synthetic studies include both positive and inconclusive findings, but most campaign traces and runners are not in this branch.

**Not demonstrated:** a universal benefit of heterogeneity, a general HLS algorithm, real-world SOC performance, general transfer or learning benefits, or the originality of the programme's broad framing. Read [the research record](docs/RESEARCH.md) for scope, evidence quality and limits.

## Repository map

| Path | Purpose |
|---|---|
| [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) | Scientific identity and motivating questions. |
| [docs/RESEARCH_DOCTRINE.md](docs/RESEARCH_DOCTRINE.md) | Operational standards for designing and closing research. |
| [docs/ONTOLOGY.md](docs/ONTOLOGY.md) | Concepts, relationships, compatibility rules and notation. |
| [docs/THEORY.md](docs/THEORY.md) | Scoped definitions, finite results, proofs and open theory. |
| [docs/LITERATURE.md](docs/LITERATURE.md) | Critical literature synthesis and source limits. |
| [docs/RESEARCH.md](docs/RESEARCH.md) | Evidence-oriented account of completed and unresolved studies. |
| [docs/HISTORY.md](docs/HISTORY.md) | Chronology of scientific decisions and milestones. |
| [registry/catalog.json](registry/catalog.json) | Machine-readable index of components, studies and results. |
| [references/hls.bib](references/hls.bib) | Canonical BibTeX bibliography. |
| [src/hls/](src/hls/) and [studies/](studies/) | Active finite model implementations and runners. |

The archive branch [feature/hls-laboratory-v1](https://github.com/franjgs/heterogeneous_learning_systems/tree/feature/hls-laboratory-v1) retains the broader historical source repository. This active branch does not claim that archived results can be replayed here. Historical provenance cites the source commit and path; summary evidence is explicitly labeled where raw data are absent.

## Install and validate

Requires Python 3.10 or later.

~~~sh
python -m pip install -e '.[test]'
hls validate
hls query --type model --text allocation
pytest
python studies/static_allocation.py
python studies/competence_development.py
~~~

The two study commands run small deterministic finite constructions, not historical campaigns. The catalog validator checks identifiers, typed relations, bibliography keys, statuses and local references; it does not validate scientific truth or prove semantic compatibility.

## Starting research

Formulate a question and competing explanations; review the literature and catalog; select or specify a scenario, organization, model and evaluation; check that their meanings, units, information and constraints are compatible; implement only what is missing; validate; then run a bounded, authorized experiment or derive the result. Record configurations, evidence, uncertainty and negative findings. Update the study record and catalog, and record consequential decisions in the chronology. The [doctrine](docs/RESEARCH_DOCTRINE.md) gives the full lightweight procedure.

To contribute, use descriptive scientific names and add a component only with a definition, scope, assumptions, relationships, validation status and owner study or general role. Keep historical identifiers as provenance aliases. Do not change historical claims or imply reproducibility without retained evidence.

## Citation and maturity

This repository is an evolving research laboratory, not a released universal framework. Cite the specific model, study and version used, not HLS as a general validation claim. The current branch's finite code and tests are directly inspectable; the historical findings in [RESEARCH.md](docs/RESEARCH.md) are documented from the archive, with raw-data and replay limitations stated there. Bibliographic records are in BibTeX; verify any reference again before publication use.
