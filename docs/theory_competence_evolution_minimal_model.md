# Minimal theory of HLS competence evolution

Date: 2026-09-15

## 1. Scope and relation to RQ0

This note consolidates a deliberately small collection of analytical cases for the Heterogeneous Learning Systems programme. Its purpose is to expose assumptions, null cases, and possible portfolio-level mechanisms before any benchmark or general controller is proposed.

RQ0 remains the sole official research question:

> Can the deliberate evolution of competence allocation in a heterogeneous learning system improve its long-term performance compared with independently optimizing task allocation and knowledge transfer?

The results labelled CR0--CR4 are statements only about the explicit models below. They are not claims about HLS in general, real model portfolios, novelty, or P4.

### Epistemic labels

- **ESTABLISHED-IN-MODEL:** derived under the stated minimal assumptions.
- **NUMERICALLY-VERIFIED:** independently checked by the scripts in `experiments/microverification/`.
- **CANDIDATE/HYPOTHESIS:** an interpretation or extension not demonstrated here.
- **NOT-ESTABLISHED:** in particular novelty, P4, and transfer to realistic HLS.

## 2. Shared assumptions and notation

The operational illustration has learners `A,B` and task regions `1,2`. Effective operational quality is:

```text
q_iz = c_iz - lambda k_iz.
```

For the unit-capacity two-task example, each learner serves one task in either division:

```text
D = (A -> 1, B -> 2)
X = (A -> 2, B -> 1).
```

Their operational values are:

```text
R_D = q_A1 + q_B2
R_X = q_A2 + q_B1
Delta(C) = R_D - R_X.
```

This is not a realistic routing model: it has two learners, two task regions, unit capacity, deterministic assignments, and no queues, abstention, mixed routing, shared training budget, interference, transfer, or uncertainty unless stated. It is a diagnostic state space, not a sufficient representation of HLS competence.

## 3. CR0 — Separability null case

### Statement

**CR0 — Separability null case.** If routing rewards and competence transitions are independent by task, the objective is additive by task, and there are no shared constraints, then the two-task decision problem decomposes into independent per-task problems.

**Status:** ESTABLISHED-IN-MODEL.

### Derivation

Let the state, action, reward, and transition factor by task:

```text
C = (C_1, C_2),       a = (a_1, a_2)
R(C,a) = R_1(C_1,a_1) + R_2(C_2,a_2)
P(C' | C,a) = P_1(C'_1 | C_1,a_1) P_2(C'_2 | C_2,a_2).
```

With no shared budget, capacity, information, or coupling constraint, the Bellman maximisation separates into two maximisations. A product policy is therefore sufficient.

### Assumptions

Additivity and transition factorisation are essential. The conclusion can fail with a shared learner, a budget, an assignment constraint, routing-generated data, interference, a common teacher, demand coupling, or a portfolio-level operational objective.

### Interpretation

CR0 is a useful null case: writing a joint state alone does not create a joint HLS problem.

### What it does not establish

It does not show that real HLS are separable, that coupling is valuable, or that a non-separable formulation proves P4.

## 4. CR1 — Finite competence-threshold and complementary investment effect

### Statement

Assume `Delta_0 > 0`, so `D` is initially preferred. Increase the off-diagonal competences `A2` and `B1` by non-negative amounts `x` and `y`, holding the diagonal entries fixed. Then:

```text
Delta' = Delta_0 - x - y
G(x,y) = [x + y - Delta_0]_+.
```

Here `G` is the operational gain from making the alternative division `X` preferable relative to the original gap.

**Status:** ESTABLISHED-IN-MODEL; NUMERICALLY-VERIFIED.

### Derivation

The changes add `x+y` to `R_X` and leave `R_D` unchanged. Thus the new difference is `R_D-(R_X+x+y)`, giving the displayed expression. If `x<=Delta_0`, `y<=Delta_0`, but `x+y>Delta_0`, then:

```text
G(x,0)=0,     G(0,y)=0,     G(x,y)>0.
```

The microverification uses `Delta_0=1`, `x=y=0.6`, yielding `0`, `0`, and `0.2` respectively.

### Assumptions

Both competence increments are deterministic, local, additive in `R_X`, and free of cost or side effects. The decision changes discretely between only two divisions.

### Interpretation

This is a finite-threshold complementarity effect: two individually insufficient changes can jointly change the operational assignment.

### What it does not establish

It does not establish complementarity in realistic competence acquisition, a learning policy, useful diversity, or a portfolio benefit after learning cost is included.

## 5. CR2 — Endogenous division-of-labour specialization

### Statement

Consider the learning-by-doing dynamics with state order `(A1,B2,A2,B1)`:

```text
r_D = sigma(beta Delta),       r_X = 1-r_D
Delta = c_A1 + c_B2 - c_A2 - c_B1

dot c_A1 = eta r_D (1-c_A1) - delta c_A1
dot c_B2 = eta r_D (1-c_B2) - delta c_B2
dot c_A2 = eta (1-r_D) (1-c_A2) - delta c_A2
dot c_B1 = eta (1-r_D) (1-c_B1) - delta c_B1.
```

For `eta>0` and `delta>0`, the symmetric candidate equilibrium is:

```text
c* = eta / (eta + 2 delta).
```

Its local assignment-asymmetry eigenvalue crosses zero at:

```text
beta_c^(2x2) = (eta + 2 delta)^2 / (4 delta eta).
```

**Status:** ESTABLISHED-IN-MODEL as a local-stability threshold; NUMERICALLY-VERIFIED for the Jacobian, eigenvalue crossing, and one illustrative symmetric parameter setting.

### Derivation and Jacobian audit

At the symmetric state, `Delta=0` and `r_D=1/2`, so setting each derivative to zero gives `c*`. Let:

```text
s = (1,1,-1,-1)^T
L = (eta+2 delta)/2
alpha = eta beta delta / [2(eta+2 delta)].
```

The symbolic Jacobian is equivalently:

```text
J = -L I + alpha s s^T.
```

Since `s^T s=4`, it has three eigenvalues `-L` and one assignment-asymmetry eigenvalue:

```text
lambda_asym = - (eta+2 delta)/2 + 2 eta delta beta/(eta+2 delta).
```

Solving `lambda_asym=0` gives the displayed `beta_c^(2x2)`. SymPy independently reproduces the Jacobian, characteristic polynomial, and threshold in `results/microverification/symbolic_jacobian_audit.txt`.

### Numerical audit

For `eta=0.4`, `delta=0.2`, the formula gives `c*=0.5` and `beta_c=2`.

- At `beta=1`, the maximum eigenvalue is `-0.2`; positive and negative assignment perturbations return to the symmetric state, with final gap magnitude below `7.6e-12` in the fixed-step run.
- At `beta=2`, the assignment eigenvalue is zero. A finite perturbation relaxes slowly over the finite simulation horizon; this is not labelled a specialized branch.
- At `beta=3`, the maximum eigenvalue is `0.2`; opposite perturbations converge in the numerical illustration to opposite polarized assignments with final gaps approximately `+/-1.229`.

The limit `delta -> 0+` sends the local threshold to infinity for fixed `eta`. The formula is not evaluated at `delta=0`, where the positive-depreciation local-stability analysis no longer applies.

### Assumptions

The result uses symmetric learners and tasks, sigmoid routing, a learning-by-doing law with saturation at one, homogeneous learning rate `eta`, homogeneous depreciation `delta`, equal operational costs implicit in `Delta`, and no exogenous demand or training action.

### Interpretation

The model contains a feedback loop in which routing changes experience and experience changes competence. Above the local threshold, this feedback can destabilise symmetric competence under the illustrated assumptions and select one of two operational divisions of labour.

### What it does not establish

It does not prove a global bifurcation classification for every `eta/delta`, stable specialised branches for every parameterisation, real specialization in model portfolios, desirability of specialization, or any P3/P4 advantage.

## 6. CR3 — Deliberate competence rebalancing

### Statement

Let `d_0>0` be the operational gap to a new division of labour. Direct learning closes displacement `x` at cumulative cost:

```text
K_L(x) = a x,       a = kappa / eta_L.
```

If formative routing closes displacement at `dot d=-v` and incurs instantaneous regret `d`, pure routing has:

```text
tau_R = d_0/v
K_R = d_0^2/(2v).
```

With future operational advantage rate `g>0`, the route-only break-even horizon is:

```text
H_R* = d_0/v + d_0^2/(2vg).
```

Pure training has `K_T=a d_0` and `H_T*=a d_0/g`.

**Status:** ESTABLISHED-IN-MODEL; NUMERICALLY-VERIFIED.

### Derivation

For pure routing, `d(t)=d_0-vt` until `tau_R=d_0/v`. Integrating regret gives:

```text
integral_0^tau_R d(t) dt = d_0^2/(2v).
```

The later advantage is delayed by `tau_R`, whose opportunity cost is `g tau_R`; dividing total effective cost by `g` gives `H_R*`. Training has no routing delay in this minimal comparison, so its break-even horizon is its immediate cost divided by `g`.

### Assumptions

`d` and `g` are expressed as operational-value rates, `v` as gap closure per time, and all cumulative costs in common operational-value units. Direct training is instantaneous and linear; formative routing changes only the scalar gap at constant rate; and `g` begins only after rebalancing is complete.

### Interpretation

Two routes can change competence allocation: direct learning and deliberately routed experience. Their trade-off depends on learning cost, experience speed, the gap, and the value of earlier completion.

### What it does not establish

It does not establish that operational routing should deliberately sacrifice current value in realistic HLS, nor that the scalar gap represents a real competence landscape.

## 7. CR4 — Dual-actuator competence evolution

### Statement

Let formative routing cover `y` of the displacement and direct learning cover `x=d_0-y`. The effective cost is:

```text
Q(y) = a(d_0-y) + y^2/(2v) + g y/v,      0 <= y <= d_0.
```

Its minimum is:

```text
y* = clip(a v-g, 0, d_0)
x* = d_0-y*.
```

The resulting regimes are:

```text
TRAIN:  a v <= g
MIXED:  g < a v < g+d_0
ROUTE:  a v >= g+d_0.
```

In the interior:

```text
Q_M = a d_0 - (a v-g)^2/(2v)
H* = Q*/g.
```

**Status:** ESTABLISHED-IN-MODEL; NUMERICALLY-VERIFIED.

### Derivation

`Q` is strictly convex because `Q''(y)=1/v>0`. Its unconstrained stationary point solves:

```text
Q'(y) = -a + y/v + g/v = 0,
```

which yields `y=av-g`; projection onto `[0,d_0]` gives the stated solution and regimes. Substitution of the interior solution yields `Q_M`. At `av=g` it joins the training endpoint, and at `av=g+d_0` it joins the routing endpoint, so the optimum and value are continuous at both boundaries.

### Numerical audit

The independent grid argmin matches the closed form for TRAIN, both boundaries, MIXED, and ROUTE cases, as well as small-gap, fast/slow-routing, cheap/costly-training, and small/large-gain cases. In the committed grid, maximum reported argmin and value error are zero because the analytic optima lie on the selected grid. The interior example `(d_0,a,v,g)=(1,1.5,1,1)` gives `y*=x*=0.5` and `Q_M=1.375`, strictly below `Q_T=Q_R=1.5`.

### Assumptions

The actuators affect one scalar displacement additively. Their costs, speed, and future gain are known, deterministic, time-invariant, and commensurate. There is no uncertainty, endogenous demand, discrete data, transfer, interference, or shared portfolio constraint.

### Interpretation

Within this scalar control problem, a mixed action can be strictly better than either pure endpoint. This is a control identity, not evidence that a mixed HLS policy is generally better.

### What it does not establish

**Mixed optimality != proof of P4.** A fully informed modular controller could possibly reproduce the same solution. CR4 does not establish coupling advantage, novelty, a real routing-training trade-off, or a general theory of competence evolution.

## 8. Null cases and strong adversaries

CR0 is the primary separability null case. Other null or adversarial comparisons include a sufficiently rich frozen heterogeneous portfolio plus strong adaptive router; free competence acquisition; complete future information with an optimal ex-ante portfolio; competence transitions independent of operation; learning unable to alter future operational decisions; and a fully informed modular controller equal to a joint controller.

These cases are scientifically useful: P1, P2, and P3 do not imply P4.

## 9. Microverification design and results

The reproducible implementation is in `src/hls/competence_evolution_minimal.py`; tests are in `tests/test_competence_evolution_minimal.py`; the runner and commands are in `experiments/microverification/README.md`.

It checks: the CR1 threshold; a symbolic and finite-difference Jacobian audit; eigenvalues below, at, and above `beta_c`; positive and negative perturbations; the `delta -> 0+` threshold limit; the two-actuator closed form against a grid argmin; regime boundaries; `Q_M` versus endpoints; `H*=Q*/g`; and selected limit cases.

The numerical findings are **NUMERICALLY-VERIFIED** identities under this code and parameterisation only. They do not add empirical evidence beyond the minimal model.

## 10. Known limitations

The two-task unit-capacity representation removes most HLS structure. The ODE assumes homogeneous learners, symmetric tasks, a chosen sigmoid router, deterministic learning-by-doing, saturation, and depreciation. The rebalancing control problem uses a scalar gap and known deterministic parameters. No component models real data generation, teacher choice, training schedules, finite data, uncertainty, queues, stochastic routing, transfer, forgetting, interference, heterogeneous capacity, demand drift, or a strong decoupled controller.

## 11. Exact next theoretical questions

Without resolving them here, the next questions are:

1. When do task frequencies or demand weights make `p_i Delta_i` ordering differ from portfolio value ordering?
2. Which minimal shared constraint makes CR0 fail while keeping P1--P3 meaningful?
3. Under what conditions can a strong fully informed modular controller match a joint controller?
4. Which physically meaningful competence transformations distinguish specialize, broaden, replicate, and rebalance without inserting a preferred answer?
5. Which null cases or counterexamples rule out a genuine P4 coupling advantage?

These questions remain CANDIDATE research directions. They are not answered by CR0--CR4.
