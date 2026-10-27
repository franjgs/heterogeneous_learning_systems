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
| Cross-links among components and evidence | [Component graph](registry/hls_component_catalog.json) · [query tool](registry/query_hls_catalog.py) |

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

- [`src/hls/`](../src/hls/): scientific implementations. Shared run metadata
  and validation live in `experiment_contract.py`; common evaluation records
  live in `performance_evaluation.py`; timing instrumentation lives in
  `experiment_timing.py`. The model modules remain separate where their
  assumptions, state transitions, or objectives differ. `synthetic/` contains
  model-specific components and downstream PEF adapters; an adapter translates
  evidence and does not make the underlying models equivalent.
- [`experiments/`](../experiments/): experiment-specific drivers and analyses,
  grouped by foundation, confirmation, pilot, or synthetic campaign. A runner
  is part of its experiment's provenance, not a disposable wrapper.
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

The registry separates the investigation lifecycle (`research_status`) from
evidence types (`evidence_status`) and result-level classification
(`result_kind`, `outcome_class`, and claim scope). A closed investigation can
contain valid results; a proposed or active investigation does not imply
evaluated evidence. The registry does not currently assert a separate
execution-stage value for every investigation; consult its dated primary
record when that distinction matters.

## Add an application or research component

1. Define the application and its real problem setting; do not infer the
   setting from a synthetic benchmark.
2. Identify or specify the scenario, including agents, tasks, demand,
   environment, information, resources, uncertainty, and constraints that
   matter to the question.
3. Query the [component graph](registry/hls_component_catalog.json) and
   follow source records for candidate scenarios, organizations, models,
   policies, protocols, and evaluation tools.
4. Check semantic compatibility and record mappings as equivalent, related,
   incompatible, or unresolved. Similar labels do not establish equivalence.
5. Select or define organizations and models, with assumptions and the
   information each decision rule can access.
6. Specify performance measures, comparators, costs, statistical unit, and
   protocol before execution.
7. Identify missing components; reuse or adapt published methods first, and
   develop a new component only for a stated scientific need.
8. Validate implementations and protocol controls separately from scientific
   evaluation; execute only under the relevant authorization.
9. Register the investigation and each distinguishable result, linking exact
   source files, configurations, code versions, artifacts, and limitations.
10. Record closure, suspension, or continuation in the current-status and
    chronology sources without changing prior evidence.

SOC and LLM work can be used to test whether this process is usable across
applications, but neither defines the general HLS architecture.

### Historical and active implementation boundary

Treat an implementation as frozen when a primary result, manifest, protocol,
or test binds it to a source/configuration hash or requires its historical
command. Do not edit that source to share helpers, refresh its hash, or move
its path. First check the relevant result manifest, runner, tests, and Git
history. Put a justified new implementation in an independent active module
only when an actual current consumer needs it; historical experiments continue
to use their original source. This boundary is determined by provenance and
consumers, not by a blanket directory split or by filenames alone.

Reusable infrastructure must remain semantic-neutral. The run envelope,
evaluation records, and timing logger provide traceability and common
measurement plumbing; scenario generation, policies, transition rules, and
scientific estimands remain owned by each model or experiment. Share a helper
only when its behavior is equivalent and tests can establish that equivalence.

## Validate registry structure and references

From the repository root, run:

```bash
python3 docs/registry/validate_hls_scientific_registry.py
python3 -m unittest discover -s tests -p 'test_hls_scientific_registry_validator.py'
```

The validator checks registry structure and source coverage. Passing it does
not independently confirm a scientific claim.

The [scenario/domain catalogue](registry/hls_scenario_catalog.json) links
scenario records to investigations, results, models, organizations, and
source references. Scenario records are distinct from research investigations,
experiment-family labels, and parameterized conditions. Validate its
cross-links, the component graph, and the underlying registry with:

```bash
python3 docs/registry/query_hls_catalog.py --validate
```

Query by domain, scenario, model, investigation, or result, for example:

```bash
python3 docs/registry/query_hls_catalog.py --domain organization_and_assignment
python3 docs/registry/query_hls_catalog.py --scenario CE-04
python3 docs/registry/query_hls_catalog.py --model "CE-04 discrete-event model"
python3 docs/registry/query_hls_catalog.py --experiment CE07
python3 docs/registry/query_hls_catalog.py --result CE07_CONFIRMATORY_EFFECT
python3 docs/registry/query_hls_catalog.py --organization "fixed"
python3 docs/registry/query_hls_catalog.py --component "CE-07"
```

Use `--help` for the complete filter syntax. Scenario records preserve the
registry's original scenario references. An investigation without a verified
scenario remains in the research registry and component graph; it is not
represented by a placeholder scenario.

## History and retained material

[History](HISTORY.md) records project chronology. Older protocols, closed
studies, source notes, and artifacts remain available for their declared
scope and provenance; they do not override the current status or their
referenced primary evidence. Start with [Current State](HLS_CURRENT_STATE.md)
before interpreting historical material.
