# G1 static organizational ground truth

G1 is the synthetic ground truth for Beam 1: organization and use of fixed
competences. It supports the static T0--T3 scaffold without claiming novel
static Operations Research theory.

The canonical theory-to-evidence interpretation, static null conditions, and
non-claims are recorded in
[`docs/theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md`](../../../docs/theory/HLS_G1_STATIC_EXPERIMENTAL_GROUND_TRUTH.md).
G1 holds `S` fixed: it has no learning, competence evolution, development,
knowledge transfer, dynamic state, queue, or Beam-2 mechanism.

## G1.1 — equal-resource specialization baseline

G1.1 implements the equal-resource two-agent/two-task proposition. It
compares the best single-agent organization (`ONE`) with task-dependent routing
(`ROUTE`) as demand `p=P(q=1)` changes. There is no competence evolution,
learning, development action, dynamic state, queue, or Beam-2 mechanism.

Its fixed controls include homogeneous and dominance nulls plus symmetric and
asymmetric crossed specialization. The stored symmetric result is
`Delta_Y(p)=0.8 min(p,1-p)`, with `p*=0.5` and `Delta_Y_max=0.4`; the stored
asymmetric result has `A1=0.6`, `A2=0.4`, `p*=0.4`, and
`Delta_Y_max=0.24`.

Run from the repository root:

```text
python -m pytest -q tests/test_g1_static.py
python experiments/synthetic/g1/run_g1_1.py
```

The deterministic runner writes machine-readable sweeps, a summary and
provenance manifest, and one diagnostic figure to
`results/foundations/g1_static/`.

## G1.2 — bicriterion effectiveness-resource ground truth

G1.2 retains the same fixed two-agent/two-task static setting, but represents
each assignment by an attainable point `Z=(R,Y)`, where effectiveness `Y` is
maximized and resource consumption `R` is minimized. `ONE` and `ROUTE` are
compared through their admissible time-sharing convex hulls under a common
budget `B`.

The six fixed scenarios cover homogeneous and Pareto-dominance nulls, the
equal-resource G1.1 embedding, a bicriterion trade-off, geometric expansion
without efficient gain, and a bounded budget window of organizational value.
The runner executes a diagnostic `p=0.5` budget sweep for all six, plus a
sampled `(p,B)` operating map for S2--S5. The fixed budget range is `[0,1]`,
which exceeds every canonical saturation resource (at most `0.8`); the
diagnostic grid has 1,001 budget points and the operating map has 101 demand
by 201 budget points. Hull calculations and breakpoints, not the grid,
establish the exact value functions and maxima.

```text
python -m pytest -q tests/test_g1_static.py
python experiments/synthetic/g1/run_g1_2.py
```

Outputs are prefixed `g1_2_` in `results/foundations/g1_static/`. G1.2 is
static Beam-1 support for T0--T3, not a claim of novel Operations Research
theory. It contains no learning, competence evolution, dynamics, queue, or
Beam-2 mechanism.

At diagnostic `p=0.5`, S0 and S1 are null controls; S2 embeds G1.1 with
`Delta_Y_max=0.4` and `D=0`; S3 has `Delta_Y_max=0.3` at `B=0.8`; S4 has
nonzero attainable-set area but zero efficient gain; and S5 has the exact
bounded gain window `(0.25,0.65)` with `B*=0.40` and
`Delta_Y_max=0.0625`. The hull oracle, rather than grid resolution,
determines these breakpoints and maxima.
