# HLS-CE-04.10 — Feasibility assessment for a P2 2×2 diagnostic

**Assessment date:** 2026-10-26
**Status:** Technical/scientific design assessment only — **not approved for
implementation or execution**.
**Basis:** Frozen CE-04 protocol, existing campaign artifacts, and the
post-campaign diagnostic in [12](12_MECHANISM_DIAGNOSTICS.md).

## Proposal received from E3

The following is the proposal as supplied in the CE instruction. Its presence
here records the proposal; it does not make it a CE-approved design.

```text
Experimento 2×2 sobre P2:
B00: P2 original.
B10: P2 con calibración externa previa:
     20 observaciones Bernoulli por agente y tarea.
B01: P2 con restricción de carga:
     excluir agentes con carga superior a
     mediana + 1,25 unidades.
B11: ambas intervenciones.

N=48 principal; N=12 secundario.
30 semillas nuevas por escala.
Misma demanda y resultados potenciales por semilla.
```

## 1. Feasibility of the four cells

**B00 is directly available** as the CE-04 P2 baseline: independent
Beta(1,1) prior for each agent×family cell, correctness updates at completion,
and selection by posterior mean times the common deadline probability. The
implementation initializes zero success/failure counts and leaves the
posterior at 0.5 (`src/hls/ce04.py`, `run_replica` and `arrival_process`).
Preserve this path exactly when both intervention factors are off; verify it
against the existing P2 implementation on fixed inputs.

**B10 and B11 are implementable as initial-information interventions.** For
each agent×family cell, 20 Bernoulli observations would initialize the
Beta(1,1) posterior to `Beta(1+s, 1+20−s)`, where `s` is the observed success
count. The true `q_ik` may generate these synthetic observations but must
remain hidden from the policy. B10 and B11 must share the same calibration
draws for a given seed and scale. The main factorial effect would be the
effect of this calibration package under the proposed simulation, not a
general effect of “better information” independent of its sample cost.

**B01 and B11 require a decision about the load cap and admission interaction.**
The CE-04 rule first forms the shared admissible set `A={i:F_i≥0.50}` and
selects from it whenever it is nonempty ([protocol §5–6](06_CE04_CONSOLIDATED_PROTOCOL.md)).
If the cap removes every member of A, the proposed exclusion leaves no agent
that P2 may select. Rejecting then adds a policy-specific rejection despite
common admissibility; falling back to an excluded agent violates the hard cap;
removing the cap changes the treatment. These alternatives have different
estimands. Therefore B01/B11 are **not operationally compatible with the
frozen admission semantics until the CE resolves this empty-set case**.

The cap itself also needs an operational definition before freezing: use the
existing expected pending service workload (active-service residual
expectation plus 1.25 per queued task), or another measure; compute the
median over all agents or over A; and define whether comparison is strict
`>` as proposed. It must use only decision-time observable state and no
realized future service. These are specification choices, not choices to make
after seeing outcomes.

## 2. What existing logs can answer

The full CE-04 per-task records contain task arrivals/families, selected
agents, `F` for the selected agent, service start/completion, correctness,
deadline, and P2 label-observation time. The existing P2 trajectory therefore
supports retrospective reconstruction of the Beta posterior on the labels
actually observed, including its coverage and estimation error. On that
**fixed historical observation path**, one can also add a hypothetical
20-sample prior and recompute posterior estimates without running the
simulator. This answers an estimator question conditional on the old P2
assignments; it does not estimate B10's policy-level outcome.

The logs do not record the full decision-time candidate vector, every
agent's score, or counterfactual selected-agent outcomes. Some queue state
can be reconstructed from the task records, but once a different agent is
selected, downstream queues, `F_i`, service completion order and which P2
labels become observed change. Consequently, fixed-trajectory replay cannot
identify the B01/B10/B11 success-on-time effects or their interaction. The
keyed potential-outcome functions in `src/hls/ce04.py` can preserve outcomes
for a new assignment when run under a fresh simulation, but the existing
selected-action log is not a substitute for executing those changed
trajectories. No new simulation was run for this assessment.

The raw task-level campaign log is local-only (its SHA-256 is in the
[campaign artifact manifest](../../../results/experiments/hls_ce04_campaign/artifact_manifest.json));
the tracked replica CSV does not contain per-agent posterior trajectories.
Retrospective analyses using only GitHub-tracked files cannot reproduce the
per-task diagnostics without access to that log.

## 3. Calibration sample and cost accounting

Twenty observations for each of `N×4` cells means `80N` Bernoulli labels per
organization: **3,840 at N=48** and **960 at N=12**. This is 80 calibration
labels per agent. For 30 seeds per scale, that is 115,200 labels at N=48 and
28,800 at N=12 if each seed gets an independently generated calibration
dataset. B10 and B11 should reuse the same dataset within a seed/scale pair,
so a shared acquisition is counted once rather than charged twice; report
both per-policy-replica benefit and once-per-paired-seed acquisition cost.

The calibration observations are not CE-04 task arrivals and have no defined
service-time, money, or compute cost in the frozen protocol. The study can
always report their count, successes/failures by agent×family cell, and
generation/processing time. A cost-adjusted comparison is not defined until
the CE specifies what acquiring one external label consumes. Do not treat
these observations as free or silently convert them into task-service units.
Use an independent, namespaced random stream for calibration; never consume
or shift the existing demand/service/correctness/tie streams. Record its seed,
sample IDs and cell-level counts so B10/B11 share identical calibration data.

## 4. Paired potential outcomes

The existing CE-04 generator keys demand by `(seed,N)` and service/correctness
potential outcomes by `(seed,N,task_id,agent_id,stream)`. This supports the
proposed common demand and outcome basis if all four cells at a given
seed/scale use exactly the same new seed, generated task list, competence
matrix, service keys, correctness keys and tie-priority permutation. Changed
choices then select among the same potential outcomes rather than shifting
random streams. B10/B11 additionally share calibration samples from a
separate stream. New seed IDs must not overlap the pilot or campaign seeds;
the exact IDs and whether seed numbers are shared across N=12 and N=48 remain
to be specified. No seed set is selected here.

## 5. Minimum changes and checks if later authorized

No generic HLS policy or contract is needed. The minimal CE-04-specific work
would be:

1. Represent the calibration and cap as two explicit factors in the
   replicate configuration, with B00 routed through the unchanged P2 path.
2. Initialize P2 success/failure counts from the shared calibration sample
   only when calibration is on; retain ordinary completion-only online
   updates and do not label rejected tasks.
3. Apply any approved cap only to the policy's candidate selection after
   calculating the unmodified common `F_i`/`A`; implement the CE-approved
   empty-set rule explicitly.
4. Log calibration stream/seed, every cell's sample counts, posterior start,
   cap threshold, decision-time workload, excluded agents, fallback/rejection
   status, and normal task outcomes/costs.
5. Add focused tests for exact B00 parity; 20 observations per cell; shared
   B10/B11 calibration draws; independent calibration versus task streams;
   completion-only online updates; cap arithmetic/strictness; empty-set and
   common-admission semantics; and identical workload/potential outcomes
   across the four cells.

The design has four conditions, two scales, and 30 paired seeds per scale:
**240 replica runs** if each cell is run once per seed/scale. Calibration
cost should not be counted as four independent acquisitions when the same
dataset is shared by B10/B11.

## 6. Assessment and unresolved decisions

**Technical viability: conditional.** The factors can be added locally to
P2 while preserving B00 and CE-04's keyed outcome streams. Existing logs can
diagnose estimator accuracy on the original P2 observation path, but cannot
identify the 2×2 effects on actual performance without changed-trajectory
simulation.

**Not ready to freeze.** The hard load exclusion conflicts with guaranteed
selection from the common admissible set when its intersection with the
load-filtered set is empty. The load measure/median population and external
calibration acquisition cost/sharing must also be fixed. Exact new seed IDs
remain unspecified. These are protocol decisions for the CE; this assessment
does not resolve them.

The 2×2 above remains an E3 **proposal**, not an approved experiment. No code
was modified, no simulation was run, and no protocol was frozen.
