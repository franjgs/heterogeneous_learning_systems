# B12.4 — Effective coupling

**Type:** HLS translation

This experiment tests whether the connection between allocation and
competence evolution is dynamically effective rather than merely
notational.

For each parameter configuration, two trajectories start from the same
state and problem distribution. They differ only in the allocation
imposed in the first period.

After the first period, both trajectories use the same routing rule.

Effective coupling is recorded only when:

1. the different initial allocations produce different next competence
   states; and
2. those state differences subsequently produce different routing
   decisions.

The test is performed over a grid of problem distributions, initial
competence states, forgetting rates, and learning rates.

A decoupled control repeats the interventions with eta = 0. In that
case, allocation must not affect competence evolution or subsequent
routing.

The purpose is not to demonstrate superiority of the coupled system.
It establishes only that the feedback

    allocation -> experience -> competence -> future allocation

has a real dynamical effect over a non-singleton parameter region.

## Audit contract and reproduction

- Citekeys: `garicano2000`, `gutjahr2011`.
- Assumptions: both trajectories share state, environment, parameters, and routing rule; only the first allocation differs. From period two onward both use the same deterministic rule.
- Parameters: the Cartesian grid in `config.json`, containing 96 cases.
- Effective-coupling criterion: the first allocations create different next states and those states subsequently create different routing decisions.
- Pass criterion: independently audited counts of `36/96` coupled cases and `0/96` effects when `eta=0`, with the intervention design verified and no coupled case depending on a future routing tie.
- Expected status: `SUPPORTED`.

Run `python experiments/foundations/b12_4_effective_coupling/run.py`. The fraction `0.375` is grid geometry, not a probability, performance measure, prevalence estimate, or evidence of superiority.
