# B2.4 — Persistence without forgetting

**Type:** source reproduction

**Source:** Gutjahr (2011), Theorem 3.

The experiment tests a numerical instance of the persistence result for
extremal policies under:

- no forgetting,
- positive learning,
- positive project values,
- a strictly increasing efficiency function.

All extremal policies are enumerated exhaustively.

For n = 3 and T = 6 this gives

    3^6 = 729

policies.

The global optimum over those policies is compared with the three
persistent policies

    (1,1,1,1,1,1)
    (2,2,2,2,2,2)
    (3,3,3,3,3,3).

Passing requires that at least one persistent policy is globally optimal
and that the best persistent objective equals the unrestricted extremal
optimum.

This reproduces a numerical instance of Gutjahr's persistence result. It
does not constitute a new proof of Theorem 3.

## Audit contract and reproduction

- Citekey: `gutjahr2011`; source detail: Theorem 3.
- Assumptions: no forgetting, positive learning coefficients and weights, strictly increasing logistic efficiency, and extremal decisions.
- Parameters: six periods and three classes as specified in `config.json`.
- Pass criterion: a persistent policy is globally optimal among all `3^6` extremal policies, with persistent/global gap at most `1e-12`.
- Expected status: `REPRODUCED` for this theorem instance.

Run `python experiments/foundations/b2_4_gutjahr_persistence/run.py`. Passing is not an independent proof of the theorem.
