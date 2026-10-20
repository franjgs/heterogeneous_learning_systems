# HLS-E2.1 — Dynamic Allocation under Experience-Dependent Productivity

## Purpose and question

E2.1 is a small deterministic diagnostic experiment asking whether a changing
allocation can outperform the globally best stationary mapping from task type
to agent when productivity increases with direct experience. It is not an
online-learning study, a campaign, or a reproduction of the full Nembhard and
Bentefouet model. OPT-DYNAMIC is an offline planning upper benchmark: it knows
the parameters, current state, and complete demand path.

## Model

There are two agents, two skills, two task types (`taskA` uses skill 0 and
`taskB` uses skill 1), and a finite horizon `T=12`. Each period contains one
unit-effort task. Either agent may perform its required skill; these two
choices are the complete feasible action set. Per-agent effort is at most one
per period and collective effort is exactly one, so both resource limits are
respected by construction.

For each agent-skill cell, productivity is the existing scalar Nembhard Direct
curve:

\[
P_{ik}(D_{ik})=k_{ik}\frac{D_{ik}+p_{ik}}{D_{ik}+p_{ik}+r_{ik}}.
\]

If agent `i` receives the current task requiring skill `k`, period reward is
`P_ik(D_ik,t)` evaluated before the transition, and experience then advances
by exactly one: `D_ik,t+1 = D_ik,t + 1`. All other cells are unchanged. The
experiment therefore treats productivity as output from one unit of work and
that work as one unit of direct experience. This is an explicit E2.1
operational convention, not a unit claim about the article. Reward is linear
task-skill output: there is no CES, threshold, monetized utility, cost, or
cross-skill aggregation.

Initial experience is a nonnegative integer matrix. `k >= 0`, `p >= 0`, and
`r > 0` follow the domain of the reused HLS scalar mechanism. All parameter
sets and profiles are embedded in `experiments/hls_e2/hls_e2_1.py`.

## Policies and optimization

* **OPT-DYNAMIC:** memoized exact dynamic programming over `(period,
  integer exposure increments for all four agent-skill cells)`. It evaluates
  the same two feasible actions available to other policies, with perfect
  knowledge including future demand. Ties retain action catalogue order
  (agent 0, then agent 1). It is not an online policy or deployable learner.
* **BEST-STATIC:** enumerates all four deterministic maps
  `(taskA→agent, taskB→agent)`, evaluates each over the complete demand path,
  and chooses the highest cumulative reward. Enumeration order is
  lexicographic and ties retain the first mapping. It has full-horizon model
  and demand knowledge solely to make the stationary benchmark strong.
* **MYOPIC:** at each period, chooses the agent with the greater true current
  productivity for the task in hand; ties go to agent 0. It does not value
  future experience.

Each policy uses the same start state, task path, actions, productivity law,
reward, and transition. There is no unknown parameter learning, observation
noise, exploration, switching cost, teaching, or MIS-v2.

The DP state uses integer exposure increments rather than floating-point
experience keys. An independent exhaustive enumerator checks optimal value
for horizons up to six. Per-case output records the memoized state count and
elapsed DP time; time is machine- and load-dependent, while choices and
rewards are deterministic.

## Small deterministic design

The script evaluates eleven parameter profiles across three `T=12` paths (33
cases): homogeneous agents; stable skill specialization; asymmetric learning
curves; different initial experience; a mixed profile; and ±2% one-factor
perturbations of `k`, `p`, or `r` around the asymmetric-learning profile.
Demand paths are alternating (6 A/6 B), clustered (6 A followed by 6 B), and
changing frequency (8 A followed by 4 B). Alternating and clustered have the
same multiset and different order. The changing-frequency path intentionally
has a different composition. No random seeds are used: the study is
deterministic.

The script writes `results/analysis/hls_e2/e2_1_results.json`. The JSON
contains complete parameter matrices, demand sequences and canonical hashes
for both multiset and ordered sequence, every policy's reward/action path,
experience and productivity trajectories, validation checks, state counts,
timings, tolerance, interpreter version, and source revision when Git makes
it available. Runtime measurements are not expected to be byte-identical.
The result is a compact diagnostic parameter study, not a broad campaign or
population estimate.

## Structural limitation and interpretation

For one skill with `n` occurrences, let

\[
F_i(m)=\sum_{j=0}^{m-1}P_i(D_{i,0}+j).
\]

Because the Nembhard curve is nondecreasing in `D` on the configured domain,
the increments `F_i(m+1)-F_i(m)` are nondecreasing, so `F_i` is discretely
convex. If `m` occurrences go to agent 0 and `n-m` to agent 1, total reward is
`F_0(m)+F_1(n-m)`, a convex function of `m`; a convex function on this finite
interval attains a maximum at an endpoint. Thus one agent receives all
occurrences of that skill in at least one optimum. Since the two skills have
independent experience and rewards and each task type maps to one skill, the
two endpoint choices can be represented by BEST-STATIC's task-dependent map.
The task order does not change this result when the multiset is held fixed.

This deduction predicts no positive `OPT-DYNAMIC - BEST-STATIC` gap for this
precisely scoped model, including parameter perturbations in the admissible
domain. In these results, OPT-DYNAMIC's chosen agent is stationary within
each task type; changes caused only by the sequence alternating between
taskA and taskB are represented by the static task-dependent mapping and are
not genuine reassignment. A zero gap does not mean dynamic planning has no value in all HLS
organizations. It says this setup lacks the coupling needed for reassignment
to improve on a task-dependent stationary mapping. Shared per-period capacity
across concurrent tasks, cross-skill production, task complementarity, costs,
or other state coupling would change the question and are deliberately not
introduced here. The experiment must not be expanded with such mechanisms
without a separately justified model specification.

## Reproduction and validation

From the repository root:

```sh
PYTHONPATH=. python experiments/hls_e2/hls_e2_1.py
PYTHONPATH=. pytest -q tests/test_hls_e2_1.py
```

The first command runs only the 21 small deterministic cases and writes the
JSON artifact; it is not an E1/E2 campaign. The tests check the independent
exhaustive validator, static enumeration, demand identities, pre-transition
production, endogenous experience, validation metadata, and the absence of a
dynamic-over-static gap within `1e-10` in this design.

## Status and limitations

E2.1 is an isolated minimal model. It does not change E1, the HLS simulator,
MIS-v2, or Nembhard integration. No conclusion is made about online adaptive
policies, noisy estimation, multi-skill tasks, simultaneous task portfolios,
resource contention across tasks, or real organizational performance.
