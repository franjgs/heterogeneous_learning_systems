# Heterogeneous Learning Systems

Heterogeneous Learning Systems (HLS) is a general scientific programme for
studying, designing, and evaluating how systems organize, use, combine, and
develop heterogeneous capabilities. It seeks findings that generalize within
stated classes and assumptions, and solutions grounded in relevant scientific
knowledge. HLS does not presume that heterogeneity, cooperation, learning,
adaptation, or organizational complexity is always beneficial.

## Conceptual architecture

HLS organizes inquiry across four related levels:

1. **Scenarios** describe systems, tasks, environments, information, resources,
   uncertainty, and dynamics.
2. **Organizations** describe how capabilities and responsibilities are
   arranged and used.
3. **Models** represent and analyze the problem and may include mathematical
   models, policies, estimators, algorithms, or integrated mechanisms.
4. **Performance measures** evaluate outcomes against relevant criteria.

These are conceptual and experimental categories, not required software
modules or a rigid execution sequence. See [HLS Philosophy](docs/HLS_PHILOSOPHY.md)
for the programme's scientific identity and [HLS Ontology](docs/hls_ontology.md)
for its semantic vocabulary.

## Find research and evidence

- [Current scientific state](docs/HLS_CURRENT_STATE.md): current findings,
  limitations, closures, and pending decisions.
- [Scientific registry](docs/registry/hls_scientific_registry.jsonl):
  structured index of investigations and results; follow its sources for
  evidence and do not treat registry entries as independent evidence.
- [Scenario and domain catalogue](docs/registry/hls_scenario_catalog.json):
  cross-links scenarios, research domains, investigations, models,
  organizations, results, and source files. Query it with
  `python3 docs/registry/query_hls_catalog.py --help`.
- [History](docs/HISTORY.md): dated decisions and project chronology.
- [Research questions](docs/research_questions.md): registered questions.
- [Theory index](docs/theory/README.md): formal results and model-scoped
  derivations.
- [Experiment index](docs/experiments/README.md): protocols and primary
  experiment reports.
- [Literature index](docs/literature/README.md): bibliography and source
  provenance.

The [repository guide](docs/REPOSITORY_GUIDE.md) maps scenarios, organizations,
models, policies, evaluation, code, experiments, results, and applications.
Primary reports, proofs, protocols, and result artifacts remain the evidence
sources; navigation pages and the registry point to them.

## Research method and applications

[Research Doctrine](RESEARCH_DOCTRINE.md) describes methodological principles.
HLS reuses established theories and components where appropriate, compares
solutions against relevant alternatives, and states the conditions and limits
of each claim. The [Security Operations Center (SOC)](projects/README.md) is a
priority application area; it does not define HLS, and synthetic results are
not evidence about real SOC operations.

## Validate the scientific registry

Using Python 3 and the standard library:

```bash
python3 docs/registry/validate_hls_scientific_registry.py
python3 -m unittest discover -s tests -p 'test_hls_scientific_registry_validator.py'
```

The validator checks record structure, links, and coverage against the
forensic-audit ledgers. Its generated summary describes registry coverage; it
does not validate the scientific truth of the underlying claims.
