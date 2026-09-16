# Execution plan

Status: executed and audited on 2026-09-16. This file preserves the planned
order; current results and epistemic statuses are summarized in `README.md`.

## Stage 0 — Mathematical fixtures
Before implementing optimization, encode exact source-model functions and fixed parameter fixtures.

### Garicano fixture
Start with a simple continuous decreasing density f on a bounded problem domain for which:
- F and f are analytic;
- the autarky optimum has a closed-form solution;
- knowledge intervals and escalation probabilities are directly computable.

First target: B1.1.
Only after B1.1 passes, implement multi-class organization for B1.2–B1.4.

### Gutjahr fixture
Implement the source equations directly:
- competence score z_it;
- efficiency gamma_it = phi(z_it);
- simplex-constrained work allocation x_it;
- objective sum_i w_i sum_t gamma_it x_it.

First target: B2.1.
Then reproduce source theorem/counterexample cases B2.2–B2.5 using source parameters wherever explicitly available.

## Stage 1 — Independent validation
Run Beam 1 and Beam 2 independently.
No shared HLS state class yet.
The objective is source reproduction, not software reuse.

## Stage 2 — Define the executable interface
Only after both beams pass:
- a_t: operational allocation/escalation decision;
- x_t: realized task-dependent work/experience;
- S_t: state required by the two beams.

Do not identify Garicano knowledge set A_t with Gutjahr competence z_it unless an explicit modeling assumption is introduced and tested.

## Stage 3 — Limiting-case tests
Run B12.2 and B12.3 before B12.4.
The combined model is rejected/revised if it cannot recover the independent beams.

## Stage 4 — Effective-coupling test
Search a modest parameter grid for B12.4.
Report the fraction/region of settings where:
a_t changes experience,
experience changes future competence,
and future competence changes the next organizational decision.

A single constructed example is insufficient.

## Stop condition
Do not proceed to heterogeneous ML models until:
- B1.1–B1.4 pass,
- B2.1–B2.5 pass or any discrepancy is scientifically explained,
- B12.2–B12.3 pass,
- B12.4 is characterized rather than merely illustrated.
