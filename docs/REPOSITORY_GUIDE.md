# Repository Guide

Use this guide to locate sources. It is a navigation aid, not a scientific
results ledger. The [scientific registry](registry/hls_scientific_registry.jsonl)
indexes investigations and results; primary reports, formal proofs, frozen
protocols, and result artifacts provide the evidence.

## Authority and programme status

| Need | Canonical entry |
| --- | --- |
| HLS identity and four-level architecture | [HLS Philosophy](HLS_PHILOSOPHY.md) |
| Research methods and claim discipline | [Research Doctrine](../RESEARCH_DOCTRINE.md) |
| Terms and semantic mappings | [HLS Ontology](hls_ontology.md) |
| Registered research questions | [Research Questions](research_questions.md) |
| Present findings, limitations, and authorizations | [HLS Current State](HLS_CURRENT_STATE.md) |
| Dated decisions and milestones | [History](HISTORY.md) |
| Research/result index and validator | [Registry](registry/hls_scientific_registry.jsonl) · [validator](registry/validate_hls_scientific_registry.py) |

Philosophy defines the programme; doctrine governs research practice.
Current State is the current-status summary, History is chronological, and the
registry is an index. For a scientific claim, follow the source cited by the
relevant registry record to its proof, protocol, report, or artifact.

## Navigate by scientific level

| HLS area | Where to start | What to follow for detail |
| --- | --- | --- |
| **Scenarios** | [Experimental foundations](experimental_foundations/) and [experiment index](experiments/README.md) | Scenario specifications, demand/environment definitions, and experiment protocols. |
| **Organizations** | [Ontology](hls_ontology.md) and the [theory index](theory/README.md) | Model-specific definitions of agents, capabilities, compositions, assignments, cooperation, and constraints. |
| **Models** | [Theory index](theory/README.md) and [`src/hls/`](../src/hls/) | Mathematical assumptions and the matching implementation/tests; similarly named models need not be equivalent. |
| **Policies** | [Experiment index](experiments/README.md) and [`src/hls/`](../src/hls/) | Policy contracts, information available at decision time, and model-specific implementation. |
| **Evaluation** | [HLS Performance Evaluation Framework](architecture/HLS_PERFORMANCE_EVALUATION_FRAMEWORK.md) | Study-specific metrics and statistical protocols in the primary report/protocol. |
| **Applications** | [`projects/`](../projects/) | Application mappings and their evidence limits. SOC is an application, not the HLS core; synthetic results do not validate a real SOC. |

The four levels are conceptual, not a required software architecture. A model
may define part of a scenario as well as its decision problem; use the source
model's own semantics rather than forcing one-to-one mappings.

## Navigate implementation and evidence

- [`src/hls/`](../src/hls/): reusable and model-specific HLS implementations.
- [`experiments/`](../experiments/): runnable experiment code and drivers.
- [`tests/`](../tests/): implementation and scientific-contract checks.
- [`results/`](../results/): tracked result artifacts, manifests, and
  provenance. Some large or ignored artifacts are local-only; consult the
  relevant report and manifest before claiming reproducibility from Git.
- [Experiment index](experiments/README.md): protocols and result reports.
- [Theory index](theory/README.md): formal results, assumptions, and scope.
- [Literature index](literature/README.md): bibliography and source provenance.
- [Scientific registry](registry/hls_scientific_registry.jsonl): machine-readable
  links from investigations to results and sources.

Do not infer completed execution from code or protocol presence. Distinguish
proposed, implemented, executed, evaluated, and validated work using the
primary record.

## Validate registry structure and references

From the repository root, run:

```bash
python3 docs/registry/validate_hls_scientific_registry.py
python3 -m unittest discover -s tests -p 'test_hls_scientific_registry_validator.py'
```

The validator checks registry structure and source coverage. Passing it does
not independently confirm a scientific claim.

## History and retained material

[History](HISTORY.md) records project chronology. Older protocols, closed
studies, source notes, and artifacts remain available for their declared
scope and provenance; they do not override the current status or their
referenced primary evidence. Start with [Current State](HLS_CURRENT_STATE.md)
before interpreting historical material.
