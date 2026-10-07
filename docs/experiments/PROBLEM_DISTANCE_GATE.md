# Problem Distance Gate

## Motivation and scope

This gate defines an operational, team-independent distance between problems
in the continuous HLS world. It validates geometry for later world design; it
does not run team configurations or add an adaptive mechanism. CES, DISCOVER,
finite beliefs, MPC, MIS-v2, assignments, and historical experiments remain
unchanged.

A problem is

```text
z(p) = (p,1-p),  p in [0,1].
```

For `rho=.5`, its production surface over aggregate capability outputs is

```text
R_p(Y1,Y2) = (p sqrt(Y1) + (1-p) sqrt(Y2))^2.
```

## Neutral output envelope and distance

The declared envelope is

```text
Y1 >= 0,  Y2 >= 0,  Y1+Y2 <= 3.
```

It follows from three agents, at most one unit of productive effort per agent,
and normalized capabilities bounded by one. It is deliberately independent of
any realized team state, assignment, belief, policy, development path, or
hypothesis repertoire.

The normalized production-surface distance is

```text
d_R(p,q) = (1/3) sup_Y |R_p(Y)-R_q(Y)|.
```

Write `a=sqrt(Y1)`, `b=sqrt(Y2)`, `A=p+q`, and `B=2-p-q`. Then

```text
R_p-R_q = (p-q)(a-b)(A a+B b).
```

Since `A,B>=0`, with `M=max(A,B)`,

```text
|(a-b)(A a+B b)|
    <= M |a-b|(a+b)
    =  M |a^2-b^2|
    <= M (a^2+b^2).
```

The envelope gives `a^2+b^2<=3`, and the bound is attained at `(3,0)`
or `(0,3)`. Therefore

```text
d_R(p,q) = |p-q| max{p+q,2-p-q}
           = |p-q|[1+|p+q-1|].
```

This is a derived consequence of this HLS special case, not a claim to a new
mathematical theorem.

## Independent numerical validation

The validator does not call the closed-form function. For every `(p,q)` it
directly evaluates both original CES surfaces on the full deterministic
triangular lattice satisfying the envelope. The gate used 196 pairs, including
boundaries, equality, `p+q=1`, and points around `.5`; each pair used 31,626
output points at resolution 250.

The maximum analytic-versus-numerical discrepancy was
`3.3306690738754696e-16`. Every nonidentical pair attained its recorded maximum
at `(3,0)` or `(0,3)`; there were zero interior-location failures. When `p=q`,
the surfaces agree everywhere, so every output is a zero-valued maximizer and
endpoint location is not unique.

## Metric properties

`d_R` is non-negative and symmetric because it is a normalized sup-norm
distance. The map from `p` to `R_p` is injective: at `(3,0)`,
`R_p=3p^2`, which is strictly increasing on `[0,1]`. Thus zero distance implies
`p=q`. Triangle inequality is inherited from the sup norm; the deterministic
41-point-per-axis test over 68,921 triples found maximum numerical excess
`2.7755575615628914e-16`, a floating-point residue rather than a mathematical
violation. Numerical tests are controls, not the proof.

Capability-label exchange sends `(p,q)` to `(1-p,1-q)`. The closed form and
production envelope are invariant under this transformation. Maximum observed
floating-point discrepancy was `2.220446049250313e-16`.

The validation grid covered the normalized range `[0,1]`. In particular,
`d_R(0,1)=1`.

## More than parameter displacement

Equal movements in `p` need not have equal maximum operational consequences:

```text
|.8-.7| = |.5-.4| = .1,
d_R(.8,.7) = .15,
d_R(.5,.4) = .11.
```

The difference reflects how location in parameter space changes the maximum
discrepancy between production surfaces. It is not psychological or cognitive
distance. Grouping the deterministic validation grid by equal parameter gaps
found 14 gap groups with nonconstant production distance; the largest
within-group distance spread was `.24`.

## Sequential world descriptors

For a sequence of true problems, the pure functions implement

```text
C_t = d_R(z_t,z_(t-1)),              t>1
N_t = min_(j<t) d_R(z_t,z_j),        t>1
M_t = min_(z_hat in Z_hat) d_R(z_t,z_hat).
```

`C_1` and `N_1` are explicitly `None`; they are not silently assigned zero.
`M_1` is defined whenever `Z_hat` is nonempty. The code and artifacts retain
the distinct names change magnitude, historical novelty, and representational
mismatch.

The controls show:

- Exact recurrence `.8 -> .2 -> .8`: final `N_t=0` but
  `C_t=.6000000000000001`.
- Historically novel but represented `.8 -> .5`: final `N_t=.39`, `M_t=0`.
- Historically novel and unrepresented `.8 -> .63`: final `N_t=.2431`,
  `M_t=.1469`.
- Recurrent but unrepresented `.63 -> .8 -> .63`: final `N_t=0`,
  `C_t=.2431`, and `M_t=.1469`.

No threshold or qualitative close/far category is introduced.

## Scientific status

Purchased/standard mathematics comprises the existing CES family, sup norm,
and metric concepts. HLS modeling choices are the problem representation
`(p,1-p)`, the neutral `Y1+Y2<=3` envelope, normalized production-surface sup
distance, and the separation of `C_t`, `N_t`, and `M_t`. The closed form is a
derived result for `rho=.5` under those choices.

## Limitations and unsupported interpretations

The distance is maximum normalized production-surface discrepancy over a
neutral envelope. Because its supremum is attained at pure-output endpoints,
it emphasizes maximum potential distinction. It is not average or expected
discrepancy, an empirical frequency-weighted quantity, team-specific
difficulty, cognitive similarity, transfer probability, adaptation
probability, or realized performance.

The gate does not establish thresholds, environmental categories, historical
memory in an agent, novelty detection, misspecification recognition, REFRAME,
transfer, or a Small Problem World. Those remain unsupported and unimplemented.

## Reproduction and artifacts

Run `python experiments/synthetic/problem_distance_gate/run.py`. Outputs are:

- `control_summary.json`: validation design and maximum discrepancies;
- `distance_grid.csv`: all analytic/numerical pair comparisons and argmax;
- `sequence_controls.csv`: numerical `C_t`, `N_t`, and `M_t` controls.
