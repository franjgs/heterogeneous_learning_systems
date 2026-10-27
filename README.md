# Heterogeneous Learning Systems

HLS is a research program studying how heterogeneous capabilities are distributed, organized, used, combined, and developed to solve problems under constraints. It is not one algorithm, simulator, or application.

The scientific work links four responsibilities: **scenarios** (problem and environment), **organizations** (entities and access/coordination), **models** (assumptions and outcome/state laws), and **performance evaluation** (metrics, comparisons, and uncertainty). These are conceptual levels, not a mandated software architecture.

- [Theory and normalized concepts](docs/THEORY.md)
- [Research record, evidence and limits](docs/RESEARCH.md)
- [Machine-readable scientific catalog](registry/catalog.json)

The catalog is the single index for scenarios, organizations, models, policies, evaluations, studies, experiments, results, and theoretical results. Historical labels are aliases/provenance only. Source reports and large campaign artifacts from the historical branch are not copied into this compact rebuild; the research record states exactly which historical summaries remain documentary rather than replayable.

## Use the laboratory

Install the small package and test extra with `python -m pip install -e '.[test]'`. Validate/query the catalog with `python -m hls validate` and `python -m hls query --type policy --text deadline`. Run the retained exact finite studies with `python studies/static_allocation.py` and `python studies/competence_development.py`. Run the test suite with `pytest`.

New work follows this sequence: define the question; select or define a scenario; select or define an organization; state the model and policy; define evaluation; check semantic compatibility; reuse or develop only necessary components; execute a registered protocol; preserve negative findings; update the catalog. Applications such as SOC or LLM systems must be modeled and validated as applications; they do not define HLS.
