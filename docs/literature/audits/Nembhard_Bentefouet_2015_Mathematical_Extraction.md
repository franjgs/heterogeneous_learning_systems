# Mathematical extraction — Nembhard & Bentefouet (2015)

Source: David A. Nembhard and Frank Bentefouet, “Selection, Grouping, and
Assignment Policies with Learning-by-doing and Knowledge Transfer,”
*Computers & Industrial Engineering* 79 (2015), 175–187,
doi:[10.1016/j.cie.2014.11.006](https://doi.org/10.1016/j.cie.2014.11.006).

The local source is
[`Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf`](../competence_evolution/Nembhard_Bentefouet_2015_Selection_Grouping_Assignment.pdf),
a 13-page PDF whose printed journal pages are 175–187. Equations and
specifications below were transcribed from that PDF; page references use the
printed page numbers, not the zero-based PDF viewer page index. This is an
extraction, not a reconstruction of details that are absent from the paper.

## 1. Productivity and learning equations

### Equation (1), printed p. 176: direct learning-by-doing curve

\[
y = k\left(\frac{x+p}{x+p+r}\right),
\qquad y,k,p,x\geq 0,\quad p+r>0.
\tag{1}
\]

Here \(y\) is work performance; \(x\) is cumulative work in units of time or
trials; \(p\) is prior expertise in the same units; \(k\) is the asymptotic
performance limit; and \(r\) is the learning-scale parameter. The prose calls
it cumulative production required for output to reach \(k/2\), but solving the
displayed equation gives \(x+p=r\), hence additional exposure \(x=r-p\) when
that value is nonnegative. The prose interpretation as *additional* required
production is therefore not generally true when \(p>0\); \(r\) is the total
effective-exposure threshold. The paper says smaller \(r\) and larger values
of the other parameters are generally preferred. The paper does not provide
physical units beyond the stated work/time/trial scale.

### Equation (2), printed p. 176: direct plus indirect experience

\[
y = k\left(\frac{hT+x+p}{hT+x+p+r}\right).
\tag{2}
\]

\(T\) is the pool of cumulative work/experience of other operators; \(h\) is
an individual transfer factor, described as the percentage of learning
transferred from others. The text says \(h\) can represent negative or
positive transfer generally; if bounded between zero and one, the model
represents positive transfer only. The displayed admissibility statement
following (1) is not repeated for (2); no additional formal parameter domain
for \(h\) is imposed there.

### Equation (3), printed p. 177: worker–task–period productivity

\[
y_{ijt}=k_{ij}\left(
\frac{\theta_{ij}T_{ijt}+\displaystyle\sum_{k=1}^{t}x_{ijk}+p_{ij}}
     {\theta_{ij}T_{ijt}+\displaystyle\sum_{k=1}^{t}x_{ijk}+p_{ij}+r_{ij}}
\right).
\tag{3}
\]

The paper uses \(i\) for worker, \(j\) for task, and \(t\) for production
period. The transfer parameter is printed as \(\theta_{ij}\) in (3) (and
appears as \(h\) in the preceding generic discussion). The cumulative direct
experience term is the sum of assignments of worker \(i\) to task \(j\) up to
and including period \(t\). The paper says \(T_{ijt}\) estimates, at time
\(t\), productivity/experience of other workers on tasks similar to \(j\),
and refers to Appendix A for its formal definition. The exact distinction
between “pool of knowledge” and a productivity-weighted quantity is fixed by
Appendix equation (A-3) below.

## 2. Direct and indirect experience

The text at printed pp. 176–177 defines:

- **Direct experience:** cumulative work by worker \(i\) on task \(j\), through
  the current period. In the scheduling formulation, each period has duration
  \(L\), and this experience is accumulated as \(\sum_{k\leq t}Lx_{ijk}\).
- **Indirect/team experience:** experience contributed by other workers
  assigned to tasks of the same type as \(j\), with the worker’s transfer
  parameter scaling its effect in the productivity equation. Workers on
  different machine types do not transfer experience in the described setup
  (printed p. 178).

Appendix A, printed p. 185, defines the team term as:

\[
T_{ijt}=\sum_{q=1,\,q\ne j}^{9} y_{qj}
  \left(\sum_{p=1,\,p\ne i}^{45}
    \left(\sum_{k\leq t}x_{pqk}P_{pqk}\right)\right).
\tag{A-3}
\]

The printed text calls \(y_{qj}\) an indicator equal to 1 when tasks \(q\) and
\(j\) are of the same type and 0 otherwise (the notation is also described as
an alias of the task index). \(P_{pqk}\) is worker \(p\)’s productivity rate
on task \(q\) at period \(k\). Thus the displayed definition weights other
workers’ assignment exposure by their productivity rates and excludes worker
\(i\). The paper’s prose calls \(T\) “total pool of knowledge”; the equation
specifies the operational calculation used here.

Appendix A gives the rate equation (A-4), with period duration explicit:

\[
P_{ijt}=k_{ij}\left(
\frac{\theta_{ij}T_{ijt}+\displaystyle\sum_{k\leq t}Lx_{ijk}+p_{ij}}
     {\theta_{ij}T_{ijt}+\displaystyle\sum_{k\leq t}Lx_{ijk}+p_{ij}+r_{ij}}
\right).
\tag{A-4}
\]

The main-text Eq. (3) omits \(L\), while Appendix (A-4) includes it. The
appendix is the explicit scheduling formulation and defines \(L\) as period
duration. The paper does not explain whether Eq. (3) implicitly normalizes
period duration to one; reproductions should report which convention is used.

## 3. Decision variables, production, objective, and constraints

Appendix A, printed p. 185, defines \(x_{ijt}=1\) when worker \(i\) is
assigned to task \(j\) at time \(t\), and zero otherwise. \(O_{ijt}\) is
worker output, \(P_{ijt}\) productivity rate, and \(S_{jt}\) output of task
\(j\) in period \(t\).

For the **parallel system**, the MINLP is:

\[
\text{Maximize }\sum_{j=1}^{9}\sum_{t=1}^{T}S_{jt}
\]

subject to

\[
S_{jt}=\sum_{i=1}^{45}O_{ijt},
\qquad j=1,\ldots,9,\quad t=1,\ldots,T, \tag{A-1}
\]
\[
O_{ijt}=\sum_{k\leq t}x_{ijk}P_{ijk},
\qquad i=1,\ldots,45,\quad j=1,\ldots,9,\quad t=1,\ldots,T, \tag{A-2}
\]
\[
\sum_{i=1}^{45}x_{ijt}=1,
\qquad j=1,\ldots,9,\quad t=1,\ldots,T, \tag{A-5}
\]
\[
\sum_{j=1}^{9}x_{ijt}\leq 1,
\qquad i=1,\ldots,45,\quad t=1,\ldots,T. \tag{A-6}
\]

Equations (A-3) and (A-4) above define transfer and productivity. The paper
describes (A-5)–(A-6) as exactly one worker per task and at most one task per
worker at each period. The formulation is binary through the assignment
definition. No separate assignment cost or resource budget appears in this
MINLP.

For the **serial system**, printed p. 185, the objective is changed to
\(\text{Maximize }Line_1+Line_2+Line_3\), with

\[
Line_1=\min\left(\sum_{t=1}^T S_{1t},\sum_{t=1}^T S_{4t},\sum_{t=1}^T S_{7t}\right),
\tag{A-7}
\]
\[
Line_2=\min\left(\sum_{t=1}^T S_{2t},\sum_{t=1}^T S_{5t},\sum_{t=1}^T S_{8t}\right),
\tag{A-8}
\]
\[
Line_3=\min\left(\sum_{t=1}^T S_{3t},\sum_{t=1}^T S_{6t},\sum_{t=1}^T S_{9t}\right).
\tag{A-9}
\]

The text says this is equivalent in objective value to ignoring buffer
constraints and maximizing the least productive task on each flow line,
citing Bentefouet and Nembhard (2013). It retains (A-1)–(A-6). The source
does not give solver tolerances or enough solver implementation detail here
to reproduce the reported MINLP upper bound exactly.

## 4. Selection, grouping, and assignment policies

Printed pp. 177–179 and Table 2 (p. 179) define three consecutive decision
stages. Each stage considers ten heuristics formed from five criteria:
\(O,k,p,1/r,\theta\). For each criterion, maximize/minimize is used in
selection and assignment; maximize/minimize within-group variance is used in
grouping. The paper describes all criteria as “more is better” after using
\(1/r\). \(O\) is a worker’s expected output under Eq. (1) over the same
duration as the experiment.

1. **Selection — who:** rank a pool of 45 workers and retain the top nine by
   either MaxiMax or MaxiMin for one criterion across the three task types.
2. **Grouping — who works together:** partition the nine selected workers into
   three teams of three, associated with three machine types. For one criterion,
   use maximum or minimum within-team variance. The paper defines the variance
   criterion for parameter \(r\) as the sum of squared deviations among
   workers in a team; it does not fully spell out tie-breaking in the text.
3. **Assignment — which team to which task class:** assign teams to replicated
   tasks using MaxiMax or MaxiMin of one criterion. Teams only perform tasks in
   their assigned class.

Combining the ten options at each stage gives 1,000 treatment combinations.
The study evaluates these stages separately and in combination; it does not
claim that every heuristic is globally optimal. The upper bound is the separate
MINLP comparator with relaxed grouping and task-type exclusivity.

## 5. Empirical inputs and simulation design

Printed pp. 177–179:

- Parameter data were fitted to timestamps for 176,000 items inspected by 75
  workers at a final test/inspection station on car-radio production lines
  (Shafer et al., 2001). Nonlinear least-squares fits of Eq. (3) had mean
  \(R^2=0.96\), standard deviation 0.02.
- Each fitted worker tuple is \((k,p,r,\theta)\). The first three parameters
  are log-transformed to obtain normal marginals; \(\theta\) is untransformed.
- Table 1 (printed p. 177) gives means for \((\log k,\log p,\log r)\):
  \(\mu=(1.448,1.963,2.0446)\), and covariance matrix
  \[
  \Sigma=\begin{bmatrix}
  0.0045&0.0167&0.0191\\
  0.0167&0.4621&0.2443\\
  0.0191&0.2443&0.1905
  \end{bmatrix}.
  \]
- \(\theta\) is normally distributed without transformation with mean 0.664
  and variance 0.409. The paper states that this parameterization forms a
  multivariate normal distribution “used throughout the simulations.” The
  conclusion (printed p. 184) also explicitly says the learning parameters are
  sampled independently of the transfer parameter. Thus the text specifies
  independence between \((k,p,r)\) and \(\theta\), alongside the Table 1
  covariance among log parameters. It does not state whether the normal draw
  for \(\theta\) is truncated or bounded; do not assume such truncation.
- Each simulation draws 45 workers, selects nine, then groups and assigns them
  to nine tasks across three machine types. Three identical instances exist
  for each of the three machine types. Transfer is within a shared machine
  type, not across types. Parallel and serial system structures are both
  studied (Figs. 1–2, printed p. 178).
- The horizon is described as an experiment-duration equivalent to one year,
  long enough for some workers to reach steady-state productivity (printed
  p. 182). Twenty-five replications use a newly sampled pool of 45 workers.
  A random baseline samples nine, groups them arbitrarily in teams of three,
  and randomly assigns teams to task types (printed p. 179).
- Appendix B/Table 6 reports the best parallel policy mean throughput 808.89
  (SD 3.681), mean upper-bound gap 1.15% (SD 1.03); Table 7 reports the best
  serial policy mean throughput 259.07 (SD 7.670), gap 6.22% (SD 3.14).
  The text reports random-policy means 752 and 192 for parallel and serial,
  respectively (printed pp. 180–186). These are the paper’s observations,
  not independently reproduced results.

## 6. Limits and unresolved transcription points

- The source presents no time-varying external demand process: it studies a
  fixed worker-pool scheduling problem with task/machine-type structure.
- The joint specification states independence between the learning-parameter
  block and transfer parameter, but does not say whether the normally
  distributed transfer parameter is truncated to \([0,1]\). An exact
  reproduction should make this omission explicit rather than silently
  clipping draws.
- “Same task type” is represented by the indicator \(y_{qj}\), but the exact
  construction of this indicator is implicit in the machine/task layout in
  Figs. 1–2 rather than separately parameterized.
- The body’s Eq. (3) and Appendix Eq. (A-4) differ in whether period length
  \(L\) appears explicitly in direct experience. Preserve that distinction
  when implementing or replicating; do not silently normalize one to the
  other.
- Appendix A-3 sums through the current period and uses productivity terms
  \(P_{pqk}\), while A-4 makes current productivity depend on the resulting
  transfer term \(T_{ijt}\). The source does not specify an intraperiod causal
  order or an implicit-system solution, so contemporaneous peer-transfer
  dependence is unresolved. Appendix A-2 also defines worker output with a
  cumulative sum of assignment times productivity but calls it output at
  period \(t\); A-1 then labels \(S_{jt}\) period output and maximizes its sum
  over periods. The relationship between rate, duration \(L\), period output,
  cumulative output and the objective is not fully reconciled in the printed
  formulation. These are source ambiguities, not permission to alter the
  equations.
- Tie-breaking, random-number generator/seed, complete MINLP solver settings,
  and full worker-level fitted data are not supplied in the extracted
  specification. Exact numerical replication is therefore not established by
  this article alone.

## Source page map

| Content | Printed pages |
| --- | --- |
| Eq. (1), Eq. (2), variable explanations | 176 |
| Eq. (3), Table 1, fitted-data and selection design | 177 |
| Parallel/serial layouts; grouping and assignment | 178–179 |
| Simulation factorial, replication, upper-bound description | 179–180 |
| Main results and interpretation | 180–184 |
| MINLP, Eqs. (A-1)–(A-9) | 185 |
| Full bibliography | 186–187 |
