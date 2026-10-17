# HLS dynamic laboratory: stress-scenario pilot

## Question and diagnostic

This pilot tests whether existing HLS Laboratory organizations discriminate
under tighter functional requirements, a complementary-team threshold, a
visible demand shift, and a restricted resource budget. No production,
functional-evaluation, MIS-v2, DISCOVER, estimator, or organization policy
implementation was changed. The earlier characterization remains untouched.

The prior pilot often showed Greedy functional success of 1.0. This was not
because its objective is reward-maximizing: `GreedyAdaptive.choose` in
`src/hls/hls_lab_v1.py` ranks actions lexicographically by (i) threshold
success, (ii) lower normalized deficit, (iii) larger functional margin, then
(iv) lower effort, using the competence estimates exposed in `DecisionView`.
The old requirements were commonly well inside the available frontier and the
budget 3.0 left all 64 frozen joint actions feasible. By contrast,
`DiscoverBeliefPolicy.choose_belief` delegates to the existing finite-horizon
solver, which maximizes expected cumulative CES reward over latent CES types
and observation updates. It does not optimize the functional success
indicator. `ExploreThenGreedy` in `hls_lab_v1.py` first visits each feasible
action for a `problem_id`, then exploits its sample-average binary success;
with organizational updates off its empty table is never changed and it
repeats the first legal action. In `run_belief_sequence`, DISCOVER updates an
environmental belief within a problem; capabilities change via MIS-v2 between
decisions when enabled. Partial-learning skill estimates update from
individual production observations and predict MIS-v2 using declared public
rates; this is distinct from real MIS-v2 development and from environmental
belief updating.

## Scenario selection before policy comparison

Requirements were selected by enumerating existing `JOINT_ACTIONS` and
`production_inputs` for the two already-used team matrices. The frontier
criterion is maximum balanced output `max_a min(Y1,Y2)`; no policy's choices or
outcomes enter selection.

| Existing team | 64-action max balanced output | Interpretation |
|---|---:|---|
| Similar `((.55,.45),)*3` | .675 | reference near-balanced frontier |
| Heterogeneous `((.82,.18),(.18,.82),(.50,.50))` | 1.070 | complementary team can jointly supply both dimensions |

The preselected balanced requirement is `(.62,.62)`: 92% of the similar team's
initial balanced frontier and feasible for both teams. The complementary
threshold `(.90,.90)` exceeds the similar team's initial balanced frontier but
is below the heterogeneous team's, establishing an a priori infeasible versus
feasible contrast. Switching requirements are `(1.20,.25)` for four problems,
then `(.25,1.20)` for four; these probe response to a known demand-orientation
change. All these full-catalog scenarios retain budget 3.0 because frozen
DISCOVER requires all 64 actions to be feasible. They therefore stress the
functional frontier, not the resource budget.

A separate tight-budget control uses budget 1.5 and requirement `(.21,.21)`.
Exhaustive enumeration gives 10 feasible actions and between one and nine
successful actions depending on the team, so the context is neither impossible
nor solved by every arm. DISCOVER is excluded from this block: the existing
adapter checks that all 64 actions are feasible and cannot be used under this
constraint without changing its contract. This is a demonstrated laboratory
compatibility limitation, not an outcome-based exclusion.

## Matrix and estimation

The sparse full-catalog design consists of eight condition cells:

- balanced near-frontier: both teams × H=1 and H=3;
- complementary threshold: both teams × H=1;
- switching orientation: both teams × H=3.

Each cell uses seeds 0–7 and six existing arms: Greedy ORACLE/LI off,
DISCOVER ORACLE/LI off, Greedy PARTIAL_STATIC/LI off, Greedy
PARTIAL_LEARNING/LI off, and Greedy ORACLE/LI on at `eta=.03` or `.25`.
This is 384 paired policy runs. The budget control adds 32 train/evaluate runs
(two teams × eight seed labels × LO on/off). The control train sweep is the
10 legal arms; evaluation repeats the task 20 times with organizational state
frozen. Total: 448 run records, 7,104 decision records.

Every full-catalog seed shares problem-generation, hidden CES-type, reward
noise, and coordinate-indexed individual-observation streams across paired
arms. Each policy retains its own evolving team, beliefs, and organizational
state. The environmental theta is independently drawn at problem boundaries;
the explicit regime shift in this pilot is in functional requirement
orientation, not a shift in the theta distribution. H=1 versus H=3 also changes
the number of real decisions per problem and thus the opportunities for
observation/development; it is not a pure planning-horizon intervention.

Paired differences use the eight seed histories as clusters. Intervals are
two-sided 95% percentile bootstrap intervals with B=5,000 and seed 20261016.
Some conditions are deterministic or nearly so, yielding degenerate intervals;
they should not be interpreted as proof of zero uncertainty. The tight-budget
control is deterministic: its repeated seed labels are not independent
stochastic replications, so its point intervals are descriptive only.

## Results

Table entries are mean cumulative `mu_true` / functional-success rate / mean
normalized deficit across the eight seeds. Full seed-level traces and all
paired intervals are in the result CSVs.

| Scenario / team / H | Greedy ORACLE off | DISCOVER ORACLE off | Greedy PARTIAL static | Greedy PARTIAL updated | Greedy LI on slow | Greedy LI on fast |
|---|---:|---:|---:|---:|---:|---:|
| Balanced / similar / 1 | 5.99 / 1 / 0 | 6.02 / 0 / .27 | 5.99 / 1 / 0 | 5.99 / 1 / 0 | 6.49 / 1 / 0 | 8.90 / 1 / 0 |
| Balanced / similar / 3 | 17.97 / 1 / 0 | 21.76 / 0 / .49 | 17.97 / 1 / 0 | 17.97 / 1 / 0 | 22.24 / 1 / 0 | 32.15 / 1 / 0 |
| Balanced / hetero / 1 | 8.56 / 1 / 0 | 8.56 / 1 / 0 | 4.72 / 0 / .10 | 8.07 / .88 / .01 | 8.81 / 1 / 0 | 10.08 / 1 / 0 |
| Balanced / hetero / 3 | 25.68 / 1 / 0 | 27.85 / 1 / 0 | 14.16 / 0 / .10 | 25.19 / .96 / 0 | 27.82 / 1 / 0 | 33.47 / 1 / 0 |
| Complementary / similar / 1 | 5.99 / 0 / .33 | 6.02 / 0 / .50 | 5.99 / 0 / .33 | 5.99 / 0 / .33 | 6.49 / 0 / .20 | 8.90 / .75 / .05 |
| Complementary / hetero / 1 | 8.56 / 1 / 0 | 8.56 / 1 / 0 | 4.72 / 0 / .69 | 8.07 / .75 / .10 | 8.81 / 1 / 0 | 10.08 / 1 / 0 |
| Switching / similar / 3 | 15.19 / 0 / .07 | 21.76 / 0 / .49 | 15.19 / 0 / .07 | 15.19 / 0 / .07 | 18.47 / .83 / .01 | 29.26 / .96 / 0 |
| Switching / hetero / 3 | 18.44 / 1 / 0 | 27.85 / .40 / .19 | 11.43 / .50 / .36 | 21.16 / .96 / .03 | 25.01 / 1 / 0 | 30.60 / 1 / 0 |

Representative paired reward differences (mean [95% interval]):

| Contrast | Cell | Difference |
|---|---|---:|
| DISCOVER − Greedy | Balanced, similar, H=1 | +.027 [−.273, .364] |
| DISCOVER − Greedy | Balanced, similar, H=3 | +3.787 [3.406, 4.254] |
| DISCOVER − Greedy | Switching, heterogeneous, H=3 | +9.412 [8.550, 10.425] |
| PARTIAL_STATIC − ORACLE | Balanced, hetero, H=3 | −11.520 [−11.520, −11.520] |
| PARTIAL_LEARNING − PARTIAL_STATIC | Balanced, hetero, H=3 | +11.026 [10.900, 11.151] |
| LI slow − off | Switching, hetero, H=3 | +6.568 [6.158, 6.957] |

Across all eight cells DISCOVER reward exceeded Greedy in six and tied in
two; it never had lower mean CES in these selected cells. This did not imply
functional superiority: DISCOVER had zero success for the similar team in
balanced and complementary requirements, and 0.40 success after the shift for
the heterogeneous team where Greedy remained at 1.0. This is consistent with
the different optimized objectives, not evidence of a broken success metric.

The complementary case demonstrates the intended feasibility distinction:
the similar team's initial frontier cannot satisfy `(.90,.90)`, while the
heterogeneous team can and Greedy achieves success 1.0. The similar team's
fast-learning arm reaches 0.75 mean success after capability development, so
an initially infeasible task can become resolvable under MIS-v2 in this
specific run design. This is not a causal estimate of a general specialization
benefit: the two initial matrices differ, and the comparison is a designed
structural contrast.

For switching, the second-half success means were 0 for Greedy/ORACLE/LI off
and DISCOVER on the similar team, versus 1.0 for both learning Greedy arms at
slow/fast rates; on the heterogeneous team they were 1.0 for Greedy off, .562
for DISCOVER, .50 for static partial, .96 for updated partial, and 1.0 for
both individual-learning arms. Change response therefore depends on team,
information, and the policy's target objective; it is not uniformly improved
by adaptation.

In the restricted-budget control, ExploreThenGreedy LO ON evaluates at 1.0
success for both teams after sweeping the 10 actions; LO OFF repeats the first
action and has zero success. Training success was .30 (similar) and .10
(heterogeneous). Evaluation effort was 20 versus 0; this is an opportunity
and resource cost, not a free improvement. It confirms table persistence and
use, while remaining confounded by exploration and reward-conditioned updates.

## Findings and limits

1. **Saturation reduced, not eliminated.** The balanced near-frontier case
   still has Greedy success 1.0. Complementarity and switching produce
   non-saturated cells, including zero-success cases and partial-information
   failures.
2. **Discrimination is real but objective-dependent.** Requirements can
   separate teams by feasibility; policies can have distinct CES and success
   rankings. CES-optimal planning can have lower threshold success.
3. **Information/update evidence is strongest in the heterogenous cases.**
   Static biased estimates substantially underperform ORACLE; updated
   estimates recover most of that difference. Similar teams, whose initial
   estimate matches their state, provide a null control.
4. **Individual learning matters in these cases.** Slow/fast MIS-v2 changes
   real capability trajectories and increases production/success in some
   previously difficult conditions. Its effect is policy-state feedback, not
   an isolated additive term.
5. **A clean organizational-learning effect remains unidentified.** Existing
   `ExploreThenGreedy` couples the action sweep, stored outcomes, and greedy
   exploitation. LO OFF is a repeated-first-action control. The minimum
   missing control is a reward-blind sweep using the same action order and
   count, followed by a predeclared fixed action rule; this would separate
   exploration exposure from reward use, but this pilot did not implement a
   new policy or claim this contrast.
6. **Tight-resource DISCOVER comparison is unavailable** under the frozen
   adapter's all-64-actions-feasible contract. Existing dynamic execution also
   has no single unified objective combining CES, threshold success, and
   resource use; this pilot reports them separately.

Thus, the pilot identifies conditions with policy differences and controls
that support interpretations about partial estimates and individual learning.
It does not establish a universal organizational advantage. No changes were
made to any historical Campaign 2/3/4 artifacts.

## Reproduction and provenance

```sh
PYTHONPATH=src:. python experiments/synthetic/hls_lab_dynamic/stress_pilot.py
PYTHONPATH=src:. pytest -q tests/test_hls_lab_dynamic.py tests/test_hls_lab_dynamic_stress_pilot.py
```

The runner refuses to overwrite an existing output directory. Its manifest
records the base HEAD, exact scenario constants/frontier checks, seeds,
bootstrap settings, source hashes, and result hashes. Artifacts:

- `results/experiments/hls_dynamic_stress_pilot/run_summary.csv`
- `results/experiments/hls_dynamic_stress_pilot/decision_traces.csv`
- `results/experiments/hls_dynamic_stress_pilot/paired_contrasts.csv`
- `results/experiments/hls_dynamic_stress_pilot/manifest.json`
