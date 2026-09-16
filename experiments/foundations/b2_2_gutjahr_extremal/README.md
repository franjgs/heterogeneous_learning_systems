# B2.2 — Extremal policy under convex learning

**Type:** source reproduction

**Source:** Gutjahr (2011), *Optimal dynamic portfolio selection for
projects under a competence development model*.

## Result

Gutjahr establishes that, when the efficiency function phi is convex
on the relevant competence region, there exists an optimal policy that
is extremal in each period.

For two project classes, an extremal allocation is therefore either

    (1, 0)

or

    (0, 1)

in every period.

## Experimental test

The experiment uses the logistic efficiency function

    phi(z) = 1 / (1 + exp(-z)).

Its second derivative is positive for z < 0. Parameters are selected so
that every competence state reachable during the experiment remains
strictly negative. Thus the entire feasible state region used by the
experiment lies inside the convex part of phi.

Two optimizations are compared:

1. exhaustive enumeration of all 2^T extremal policies;
2. exhaustive enumeration of a discretized simplex containing both
   extremal and mixed allocations.

The best value over the full grid must equal the best value among
extremal policies.

## Interpretation

Passing B2.2 reproduces a numerical instance of Gutjahr's extremal-policy
result. It does not constitute a new proof of the theorem.

No HLS-specific mechanism is introduced.

## Audit contract and reproduction

- Citekey: `gutjahr2011`.
- Assumptions: four periods, two classes, `beta=0`, positive weights, and all reachable states inside the convex part of logistic `phi`.
- Parameters: the fixture in `config.json`, including a `0.05` allocation grid.
- Pass criterion: the best extremal value equals the best value on the complete discretized grid within `1e-12`, with convex-region checks passing.
- Expected status: `REPRODUCED` for this numerical instance.

Run `python experiments/foundations/b2_2_gutjahr_extremal/run.py`. The finite grid is a consistency reproduction, not a numerical proof over the continuous policy space.
