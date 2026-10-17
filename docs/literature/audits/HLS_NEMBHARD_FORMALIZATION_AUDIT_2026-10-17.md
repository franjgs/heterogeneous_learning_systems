# HLS — Nembhard & Bentefouet (2015): mathematical source audit

**Date:** 2026-10-17
**Status:** PARTIALLY FORMALIZED; original PDF binary not read in this execution.
**No simulation, implementation, or new algorithm was executed.**

**Status update (2026-10-17, later source audit):** The original local PDF was
subsequently read directly and its equations/appendix checked in
[`HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md`](HLS_NEMBHARD_FIDELITY_AND_CONTRACT_REVIEW_2026-10-17.md).
That review supersedes this document only on primary-source availability and
the equation/output/temporal details it directly verifies; this audit remains
an accurate record of its earlier execution scope. The PDF is retained in the
local bibliography but has since been removed from the current Git index by
the local-PDF protection commit; historical commits are not rewritten. The
verified SHA-256 is
`30129963aa6b69197140552b9431480b7b976d5c3d521eabbe3ec63478402e81`.

## Provenance

- Original: David A. Nembhard and Frank Bentefouet, *Selection, grouping, and assignment policies with learning-by-doing and knowledge transfer*, *Computers & Industrial Engineering* 79 (2015), 175–187, DOI: 10.1016/j.cie.2014.11.006. Publisher: https://www.sciencedirect.com/science/article/pii/S0360835214003672
- Master BibTeX entry confirmed on repository branch `feature/hls-laboratory-v1`: `docs/literature/references.bib`, key `nembhardbentefouet2015`.
- Existing PDF path in GitHub repository: `docs/literature/competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf`. Binary is not accessible via the GitHub text connector; **do not treat its presence as proof that its content was reviewed here**.
- Repository `docs/literature/README.md` records SHA-256 `30129963aa6b69197140552b9431480b7b976d5c3d521eab63478402e81` (check hash against local file before relying on it).
- Later source with explicit methodological reconstruction: *Workforce grouping and assignment with learning-by-doing and knowledge transfer*, International Journal of Production Research (2018), Appendix 3, https://www.researchgate.net/publication/322638546_Workforce_grouping_and_assignment_with_learning-by-doing_and_knowledge_transfer . Its authors state that they contacted the 2015 authors because the original did not explain exactly how each heuristic was computed.

## Source-supported model components

### Learning / productivity

A subsequent thesis explicitly attributes a hyperbolic learning function with direct experience `D`, indirect experience `S`, individual transfer efficiency `theta`, prior experience `p`, learning-shape parameter `r`, and asymptotic productivity `K` to Nembhard & Bentefouet. The reconstructed functional form is:

`phi(D,S) = K * (D + theta*S + p)/(D + theta*S + p + r)`.

**Provenance restriction:** secondary-source reconstruction, **not checked against original Eq. (3)**. Do not call the equation primary-verified. For `K>0,r>0,z=D+theta*S+p>=0`, `d phi/dz=K*r/(z+r)^2>0`, `d² phi/dz²=-2*K*r/(z+r)^3<0`, `lim(z→∞)phi=K`. These derivatives are our algebra, not claimed theorems of the authors.

### Decision structure

The original publisher page explicitly states three stages: (i) select workers from a pool; (ii) group selected workers by individual characteristics; (iii) assign groups to tasks. It evaluates heuristics for **parallel and serial** systems against a baseline and an upper bound from a **nonlinear mathematical program**. The publisher's summary does **not** expose that program's objective, decision variables, or constraints. Therefore none is invented here.

### Heuristic definitions documented in later study

The 2018 follow-up Appendix 3 states that the original example uses **nine selected workers**, **three machine types**, **three identical jobs per type**, and worker/task-type parameters `K_{i,a}`, `K_{i,b}`, `K_{i,c}`. It defines per-worker average `Kbar_i=(K_{i,a}+K_{i,b}+K_{i,c})/3`. `Min variance K` groups the nine workers into three groups of three to minimize the **sum of within-group variances** of `Kbar_i`, with `Var(G)=(1/3)Σ_{i∈G}(Kbar_i - mean_{j∈G} Kbar_j)^2`. `Maximax K` assigns task types to groups by maximal group-level `K` on that job type. **The exact collision resolution and group-level maximax matching algorithm are not fully specified in the excerpt; do not invent them.** Source: follow-up Appendix 3, not directly original.

The follow-up lists top parallel-system combinations, including `Min variance K / Maximax K` and `Min variance p / Maximax theta`. Rankings are **experiment-specific**, not universal optimality results.

## What cannot yet be responsibly formalized

1. Exact Eq. (3) as printed in the 2015 original and its variable indices, time or task dependencies.
2. Exact definition of indirect experience: which teammates contribute, whether job-type dependent, whether time-discounted, and whether simultaneous or accumulated.
3. Complete nonlinear upper-bound optimization model: objective, constraints, feasible selection/grouping/assignment set, time horizon, treatment of transfer and parallel/serial aggregation.
4. Original baseline and full selection/grouping/assignment heuristic algorithms, including tie-breaking.
5. Experimental distributions, parameter fitting and full factorial design, random seeds and statistical analysis.
6. Evidence of reproducibility or fair comparability with HLS; these statuses remain unestablished.

## HLS ontology mapping (provisional)

| Source quantity | HLS object | Mapping | Caveat |
|---|---|---|---|
| Worker and task type | Agent, task | RELATED | Original manufacturing assumptions are specific. |
| `K`, `p`, `r`, `theta` | Agent-specific capability/learning parameters | RELATED | Parameters are not all competence states. |
| `D` | Direct experience `E_dir` | RELATED | Check units and accumulation. |
| `S` | Indirect experience `E_ind` | RELATED | Check source identity and task specificity. |
| `phi` | Expected operational productivity | RELATED | Not a probability of success or generic quality. |
| Selection/grouping/assignment | Organization/use decision `a_t` | RELATED | Selection changes agent set; grouping creates transfer opportunities. |
| Throughput | Operational value/performance | RELATED | Parallel and serial system aggregation differ. |

## Benchmarking requirements before implementation

- First reproduce original results under original parameterizations; do not substitute HLS MIS-v2.
- Then define a separate common-setting benchmark with equal demand/task instances, agent information, horizon, resources, permitted actions, and outcome metrics; explicitly report irreducible differences.
- Preserve original baseline, original heuristic definitions and upper-bound comparison; do not compare a heuristic with an omniscient policy without labeling the information advantage.
- No claim of **REPRODUCIBLE**, **REPRODUCED**, **INTEGRABLE** or **COMPARABLE** until corresponding evidence exists.

## Immediate blocker and action

Read the retained local PDF with `pdftotext -layout` or equivalent through local Codex, extract and transcribe original Eq. (3), Section 3 nonlinear program, Tables 1–3 and methodology, and record exact page numbers. The PDF is **not present in this execution's mounted `/mnt/data`**, and the GitHub connector cannot deliver binary contents. A full primary-source mathematical audit is therefore **blocked**, not completed.
