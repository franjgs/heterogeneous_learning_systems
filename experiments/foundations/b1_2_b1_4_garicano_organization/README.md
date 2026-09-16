# B1.2–B1.4 — Garicano organization

**Type:** source reproduction

**Source:** Garicano (2000), *Hierarchies and the Organization of
Knowledge in Production*.

## B1.2 — Specialization

Garicano's Proposition 1 uses the linear structure of the organizational
problem to establish specialization: one class produces while the other
classes specialize in problem solving.

The experiment reproduces the extreme-point mechanism numerically for a
fixed organization. It does not claim to constitute an independent proof
of the full proposition.

## B1.3 — Organization by frequency

Garicano's Proposition 3 orders knowledge by problem frequency: producers
know common problems and successive problem-solving layers deal with
increasingly unusual exceptions.

The experiment does not impose this ordering. It exhaustively enumerates
all permutations of fixed probability-mass blocks and evaluates their
communication load. The frequency-ordered organization must be the unique
minimum when block masses are distinct.

## B1.4 — Pyramidal organization

The experiment evaluates Garicano's relation

    b_i = h b_0 [1 - F(Z_{i-1})]

using the discrete probability-mass fixture produced by B1.3.

It verifies both the relation itself and

    b_{i+1} < b_i.

## Scope

These are reproductions of structural mechanisms in Garicano's model.

No competence evolution, learning, knowledge transfer, routing algorithm,
or HLS-specific mechanism is introduced.

## Audit contract and reproduction

- Citekey: `garicano2000`.
- Assumptions: a fixed linear production fixture for B1.2, distinct fixed probability masses for B1.3, and the discrete hierarchy-size relation for B1.4.
- Parameters: productivities `[0.62,0.71,0.83,0.68]`, blocks `[0.30,0.25,0.20,0.15]`, help cost `0.20`, producer mass `1`.
- Pass criteria: a one-class extreme-point optimum; a unique frequency-ordered minimum over all 24 permutations; and the exact, strictly decreasing hierarchy relation.
- Expected status: `REPRODUCED` within these fixtures.

Run `python experiments/foundations/b1_2_b1_4_garicano_organization/run.py`. The result does not independently prove Garicano's full propositions.
