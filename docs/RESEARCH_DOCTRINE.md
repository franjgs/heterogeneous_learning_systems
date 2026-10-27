# Research doctrine

This doctrine defines a practical standard for producing and interpreting HLS knowledge. It applies to theoretical, computational, empirical and integrative work, with methods chosen to fit the question rather than imposed mechanically.

## 1. Start with a scientific question

State the phenomenon, the unresolved uncertainty, the plausible competing explanations and the intended contribution. Separate the question from the application, implementation and experiment. Identify the target population, system, time horizon and conditions where these affect the claim.

Before work begins, search the ontology, catalog, theory, research record and literature. Compare semantic objects and assumptions, not just names. Explain whether the work is theoretical, methodological, empirical or integrative. A new implementation, combination of known methods or application is not automatically novel.

## 2. Novelty and prior work

A novelty claim requires relevant, direct comparison with established theory, methods and studies. Identify what those sources establish, their assumptions, and what the proposed work adds. If this comparison is incomplete, describe novelty as unresolved. Do not make absence of a repository match stand in for a literature review.

## 3. Hypotheses and research modes

Make hypotheses falsifiable when possible and specify observable consequences. Label work exploratory or confirmatory. Exploratory observations may motivate hypotheses but must not be retrospectively called preregistered. A null result is not evidence of equivalence unless the design and uncertainty analysis support an equivalence claim.

## 4. Model contract

Every model states its scope and assumptions; entities and variables; state and time; decisions and feasible actions; transition and outcome laws; information available at each decision; constraints and resource units; outputs; and known limitations. Declare which quantities are observed, estimated, latent, stochastic or counterfactual. Do not silently change definitions when translating a model.

## 5. Design and evaluation

When relevant to the question, specify estimands, comparators, baselines, controls, ablations, sensitivity analyses, uncertainty, sampling units, configuration, seeds, data provenance, stopping criteria and leakage checks. Compare systems under matched conditions when the causal or comparative claim requires it. Record operational, organizational and computational costs separately when they have different meanings.

No checklist is universal: for example, a proof may need no experimental baseline, while a randomized experiment may need allocation concealment and a preregistered analysis. Explain why a method is appropriate and what inference it permits.

## 6. Validity and evidence

Report separately:

- **Mathematical correctness:** whether a derivation follows from stated assumptions.
- **Implementation correctness:** whether code realizes the declared model.
- **Internal validity:** whether the design supports the comparison or causal interpretation.
- **Construct validity:** whether operational measures represent the intended concepts.
- **External validity:** which other settings the evidence can reasonably inform.
- **Reproducibility:** whether another researcher can regenerate the analysis from retained materials.
- **Generalizability:** which broader population or model class is supported.

Classify claims as formal proof, exact computation, numerical experiment, simulation, empirical observation, literature-supported, expert interpretation, hypothesis or conjecture. A literature citation supports only claims warranted by that source; a reference is not a proof.

## 7. Negative and uncertain findings

Preserve scientifically informative positive, negative, null, ambiguous and inconclusive findings. Distinguish a well-executed experiment with an unfavorable result from an invalid experiment. An invalid experiment cannot support the intended conclusion, though the failure may identify a methodological issue. Report uncertainty, effect magnitude and practical relevance, not significance alone.

## 8. Reuse and development

Reuse a component when its semantics, assumptions, units, information structure and validation match the new use. Adapt it only with an explicit mapping and tests. Keep components separate when equivalence is uncertain or false. Develop the minimum missing mechanism needed to answer the question; complexity requires a scientific justification.

## 9. Closing a study

A study record states the question and whether it was answered; supported and unsupported claims; limitations; reusable knowledge; unresolved questions; execution status; evidence status; provenance; and whether the work is closed, continuing, suspended or invalidated. Closure is a project status, not a claim that results are universally true.

## 10. Publication readiness

Code completion, a working demo, or a simulation with a favorable result is insufficient. A defensible submission needs a precise contribution, justified relation to prior work, sound theory or design, credible comparators, transparent uncertainty, reproducible evidence proportionate to the claim, and conclusions within the demonstrated scope. If originality or external relevance is unresolved, say so and narrow the claim.

## 11. Lightweight workflow

1. Formulate the question and competing explanations.
2. Review the literature and existing HLS components.
3. Select or define a scenario, organization, model and evaluation.
4. Check semantic and mathematical compatibility.
5. Specify hypotheses, baselines, estimands and validity risks.
6. Implement or derive only what is missing.
7. Validate the implementation or proof.
8. Execute only the authorized and appropriately scoped study.
9. Preserve configurations, evidence, uncertainty and negative findings.
10. Draw bounded conclusions and update the research record and catalog.
11. Record consequential scientific decisions in the chronology.

The [catalog](../registry/catalog.json) is the component index. The [research record](RESEARCH.md) is the evidence-oriented account; [history](HISTORY.md) is the chronology.
