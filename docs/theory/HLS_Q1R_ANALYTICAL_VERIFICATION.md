# Q1-R: analytical verification of MIS-v2 × demand persistence

**Recorded:** 2026-10-16 11:03 +02:00 (Europe/Madrid)
**Status:** analytical verification; no campaign design was changed and no
campaign was run. The 960-trajectory Q1 campaign remains on HOLD/NO-GO as
registered. HLS Laboratory v1 remains **PARTIAL**.

## 1. Question and scope

This note asks whether the current MIS-v2 transition and current P0 assignment
can generate an architecture × temporal-demand interaction, not whether
heterogeneity or learning is generally beneficial. The registered Q1 protocol
and its preflight results remain unchanged. A two-period exhaustive diagnostic
uses the production and learning implementation as-is and enumerates all four
possible task paths under IID and Markov probabilities. It is a constructive
existence check, not a campaign, estimate of population effects, or evidence of
superiority.

Sources inspected: [minimal theoretical model](HLS_MINIMAL_THEORETICAL_MODEL.md),
[Q1 design](../experiments/HLS_FIRST_SCIENTIFIC_CAMPAIGN_DESIGN.md),
[Q1 preflight](../experiments/HLS_Q1_PREFLIGHT.md), `src/hls/discover_v0.py`,
`src/hls/discover_develop_v2.py`, `src/hls/hls_lab_dynamic.py`,
`src/hls/hls_lab_v1.py`, `src/hls/hls_lab_v1_integrated.py`,
`src/hls/hls_lab_v1_environment.py`, and `src/hls/synthetic/c5.py`.

## 2. Exact implemented model

The reused simulator has exactly three experts and two skills. A real
competence matrix is $C_t=(c_{ik,t})\in[0,1]^{3\times2}$. A frozen joint
production action $X_t=(x_{ik,t})$ is one of 64 DISCOVER actions, with each
expert's effort chosen from \((0,0),(0,1),(.5,.5),(1,0)\). The problem
feasible set filters this catalogue by

\[
\sum_{i,k}x_{ik,t}\le B_t,\qquad \sum_kx_{ik,t}\le h_t
\quad\text{for each expert }i.
\]

At the registered Q1 budget $B=2$ and individual cap $h=1$, the preflight
enumerated 37 feasible actions. Effort budgets reset each problem; unused
capacity does not carry forward. There is one problem and one decision per
period.

`production_inputs` uses additive output (no cross-agent synergy):

\[
 Y_{k,t}=\sum_{i=1}^{3}x_{ik,t}c_{ik,t}.
\]

The policy's predecision estimate is the mean of the organization's discrete
competence posterior, not private truth. Current P0 (`P0ProductionOnly`)
chooses the feasible production-only action maximizing, lexicographically,

\[
\left(\mathbf1[\text{functional success}],\
 -\text{normalized deficit},\
 \text{minimum active-dimension margin},\
 -\text{total productive effort}\right).
\]

Thus P0 is a current-problem functional heuristic; it does not maximize CES
and does not plan over future learning. The catalog order breaks exact ties.
The realized per-period score is instead DISCOVER CES,

\[
R_t=\left(\sum_{k=1}^{2}\alpha_{k,t}Y_{k,t}^{\rho}\right)^{1/\rho},
\qquad \rho=0.5,
\]

with task-specific normalized nonnegative weights. Functional success is the
separate threshold test `Y_k >= requirement_k` for every active skill.

With MIS enabled, `advance_team` applies independently to each expert-skill
cell after current production and before the next decision:

\[
 c_{ik,t+1}=1-(1-c_{ik,t})\exp(-\lambda_{ik}x_{ik,t}),\qquad
 \lambda_{ik}=-\log(1-\eta_{ik}).
\]

For unit effort this is $c_{t+1}=c_t+\eta(1-c_t)$. With MIS disabled,
the real competence matrix is unchanged. The runner does not advance the
real-state estimate from private transitions; it updates the posterior from
individual production observations $y_{ik,t}=x_{ik,t}c_{ik,t}+\epsilon$,
then, when MIS is on, pushes its support through the public MIS transition.
There is no teaching in Q1.

The environment is generated before policy evaluation. C5 IID demand samples
from a stationary categorical distribution. C5 Markov demand samples the
initial task from its initial distribution and each later task from the prior
task's transition row. The HLS environment wrapper freezes emitted problems;
latent task state is not passed to P0. Demand does not depend on organization
state or actions.

The general theoretical model allows multiple pending tasks, parallel work,
queues and generic resource coefficients. Those are **not** in this v1
execution contract: it has one task per period, a fixed discrete action set,
per-period budget/cap constraints and additive production. Results below are
for the latter, not the broader abstract model.

## 3. MIS OFF: when persistence cancels in expectation

Let $D_t\in\mathcal D$ denote a task type. Suppose both processes have
the same stationary marginal $\pi$, including the Markov initial
distribution. With fixed competence and information, memoryless P0 induces a
time-invariant task-specific reward $u_A(d)$ for architecture $A$.
Then for horizon $T$,

\[
V(A,D,0)=\mathbb E\left[\sum_{t=0}^{T-1}u_A(D_t)\right]
=\sum_t\sum_d\pi_d u_A(d)
=T\sum_d\pi_d u_A(d),
\]

under either IID or stationary Markov demand. This proves equality of expected
cumulative CES for each architecture, and hence \(\Theta(0)=0\), under
the stated conditions. It does **not** prove equal realized trajectory
distributions: Markov demand changes serial correlation, run lengths, and the
variance/distribution of cumulative path rewards. Finite empirical task
frequencies also need not match.

The cancellation requires: (i) fixed real competence; (ii) an action/reward
mapping depending only on current task and fixed architecture, not history or
time; (iii) a time-invariant catalog and constraints; (iv) no resource,
queue, inventory, or unfinished-task carryover; (v) no state-dependent reward
or terminal value; and (vi) stationary initialization with the common task
marginal. It is not a statement that demand persistence is unimportant in
general.

These conditions mostly match the registered MIS-OFF Q1 block: real skills
are frozen; P0 has no internal action memory; each problem resets the budget;
the catalog and CES mapping are fixed; and C5 Markov is initialized at
\(\pi\). One qualification matters: the runner still updates the
organizational competence posterior from observations even when MIS is off.
In the registered block, estimates start at truth, observation noise is zero,
and P0 ignores posterior variance. Positive-effort observations recover the
same competence means, while zero-effort cells retain their correct means.
Thus this belief update does not change the P0 action mapping in that setup.
With noisy or misspecified estimates, the policy may become history-dependent;
then equal marginal demand alone does not guarantee \(\Theta(0)=0\).
The preflight's exact per-task architecture gap (+0.1 for each of its three
task orientations) and 12 path checks are consistent with the stationary
expectation argument. Its registered 24-period primary contrast remains a
structural null under its tested P0/task mapping; do not reinterpret the
secondary MIS-ON results as a revised primary campaign.

## 4. MIS ON: demand history enters through exposure and feedback

For demand $D_t=d$, requirements and CES weights are those emitted for
that task. The coupled actual runner is

\[
 A_t=\operatorname{P0}(\widehat C_t,r(D_t),\mathcal A(B,h)),\quad
 Y_t=\sum_i A_{i,t}\odot C_{i,t},\quad
 R_t=\operatorname{CES}(Y_t,\alpha(D_t)),
\]

\[
 C_{i,k,t+1}=1-(1-C_{i,k,t})e^{-\lambda_{ik}A_{i,k,t}},
 \quad
 \widehat C_{t+1}=\operatorname{beliefUpdate}(\widehat C_t,A_t,Y_t,\epsilon_t),
\]

where \(\mathcal A(B,h)\) is the catalog filtered by the common
budget and per-expert caps. Demand affects the assignment, assignment
determines productive exposure, exposure changes competence, and competence
and its estimate affect later assignment. Under Markov demand, the distribution
of future $D$ depends on current and prior demand; therefore exposure and
competence paths can depend on demand history even when each period's
marginal is stationary.

For a single cell with fixed cumulative effort $E_{ik}=\sum_t x_{ik,t}$,
the exact MIS transition gives

\[
1-c_{ik,T}=(1-c_{ik,0})e^{-\lambda_{ik}E_{ik}}.
\]

Thus the final skill is order-independent **conditional on the same total
cell-specific exposure**. A nonzero persistence effect needs more than
saturation alone: persistence must change relevant exposure totals or the
timing of exposure relative to rewarded future tasks. That can happen because
P0 reallocates effort by task, because architecture-specific skill rankings
cross discrete action/assignment boundaries, or because temporal reward
opportunities differ. If exposures are demand-independent and the same total
effort goes to every cell, or if \(\eta=0\), or if action/reward is
insensitive to the changed state, the effect is zero. Full saturation can
also make later exposure differences immaterial. Finite horizons matter
because a gain only affects periods after the exposure and may arrive too late
to be used.

The log remaining-gap state $z_{ik,t}=-\log(1-c_{ik,t})$ accumulates
\(\lambda_{ik}x_{ik,t}\). Saturating competence increments are larger
when initial remaining headroom is larger, while P0's discrete thresholds
can cause non-smooth changes in exposure. Learning monopolization is possible
if P0 repeatedly selects the currently best agent; it is not automatic in
this Q1 example. These properties make a nonzero interaction contingent on
the exact profiles, catalog, tie-breaking, P0 objective, CES weights and
horizon.

## 5. Exact effect decomposition

For $A\in\{H,G\}$, demand process $D\in\{M,I\}$ (Markov/IID),
and MIS toggle $m\in\{0,1\}$, define the expected cumulative gross CES
under the fixed protocol as $V(A,D,m)$. Let

\[
\Delta(D,m)=V(H,D,m)-V(G,D,m),\qquad
\Theta(m)=\Delta(M,m)-\Delta(I,m),
\]

and

\[
L(A,D)=V(A,D,1)-V(A,D,0).
\]

Since \(V(A,D,1)=V(A,D,0)+L(A,D)\), substitution and regrouping gives
the exact identity

\[
\Theta(1)=\Theta(0)+[L(H,M)-L(G,M)]-[L(H,I)-L(G,I)].
\]

This is accounting, not a causal mediation decomposition. If \(\Theta(0)=0\),
then the total architecture-by-persistence contrast under MIS ON equals the
difference across demand processes in the MIS ON-minus-OFF contribution to
the architecture contrast. In the controlled simulator the MIS toggle is an
intervention, so this is a total factorial interaction conditional on P0 and
the registered information/environment contract. It does **not** separate
MIS's direct competence transition from its coupling to P0 assignments:
MIS changes competence/estimates, which may change later actions and
exposures.

## 6. Constructive exact existence result

The test `tests/test_hls_q1r_analytical.py` calls the current
`run_integrated_sequence`, P0, production, posterior update and MIS-v2 code.
It enumerates the complete two-period path space, so these are exact finite
expectations, not Monte Carlo estimates.

| Setting | Homogeneous $G$ | Tilted $H$ | Architecture effect $\Delta$ |
| --- | ---: | ---: | ---: |
| MIS OFF, IID | 2.000 | 2.200 | 0.200 |
| MIS OFF, Markov | 2.000 | 2.200 | 0.200 |
| MIS ON, IID | 2.050 | 2.245 | 0.195 |
| MIS ON, Markov | 2.080 | 2.272 | 0.192 |

**Parameters.** $G=((.5,.5),(.5,.5),(.5,.5))$;
$H=((.6,.4),(.4,.6),(.5,.5))$. Both have per-skill totals
\((1.5,1.5)\), row totals \((1,1,1)\), and the same
$\eta_{ik}=.10$. At each period the task is either skill 0 or skill 1,
each with stationary marginal \(\pi=(.5,.5)\). IID draws are
independent. Markov begins at \(\pi\) and has
\(P=[[.8,.2],[.2,.8]]\), also stationary with marginal \(\pi\).
Horizon is 2; every problem has budget $B=2$, cap $h=1$, an active
requirement of .1 for its skill and zero for the other, and CES weight 1 on
the active skill. No teaching, noise, resource carryover or terminal reward
is used. All 4 paths are evaluated per architecture/MIS arm.

Under MIS OFF, P0 produces 1.0 each period for $G$ and 1.1 for $H$,
so both demand processes give the same \(\Delta=.2\) and
\(\Theta(0)=0\). Under unit effort and MIS ON, one repeated skill
updates the exposed G cells from .5 to .55, giving second-period output
1.10; H's relevant .6/.5 cells update to .64/.55, giving 1.19. Thus the
two-period architecture gap for a repeated task is .19. If the second task
switches skill, that skill has not yet been exposed and the gap remains .20.
The probability of repetition is .5 under IID and .8 under Markov. Therefore

\[
\Delta(I,1)=.5(.19)+.5(.20)=.195,\quad
\Delta(M,1)=.8(.19)+.2(.20)=.192,\quad
\Theta(1)=-.003.
\]

The learning contributions are $L(G,I)=.050$, $L(G,M)=.080$,
$L(H,I)=.045$, and $L(H,M)=.072$. The decomposition verifies
\(0+(.072-.080)-(.045-.050)=-.003\).

This is a negative interaction. It occurs because the tilted architecture's
larger initial frontier has less remaining MIS headroom on a skill it has
already exercised; persistence increases the chance of repeating that skill.
For switched tasks both architectures retain the same .1 initial gap on the
as-yet-unexposed skill. It proves **expressibility/existence** in current HLS,
not that the effect is large, robust to other profiles, general beyond P0, or
representative of real teams. The 2-period, 2-task-state setup is minimal for
serial dependence to affect a post-learning reward. Demand persistence here
is stationary autocorrelation, not a regime shift.

## 7. Initial architecture advantage and preflight consistency

Matched aggregate competence does not imply matched functional capability.
Under $B=2,h=1$, the preflight action enumeration found frontiers
\((1.0,1.0,.5)\) for (G) and \((1.1,1.1,.6)\) for (H),
for skill 0, skill 1 and joint requirements respectively. The tilted roster
therefore has an initial +.1 CES frontier advantage for each registered
orientation under P0. This comes from redistributing the same skill totals
across agents, so the discrete allocation can select the stronger
skill-relevant experts. Production remains additive: this is not
superadditivity or emergent synergy.

For fixed competence and stateless P0, the per-task initial architecture
reward difference is constant at +.1 in the preflight checks; it averages
under the common task marginal and cancels from the Markov-minus-IID contrast.
If per-task gaps differ, their weighted sum still cancels between stationary
processes as long as P0's mapping remains fixed; it is task-history-dependent
gaps/action responses, not an initial advantage by itself, that can make
\(\Theta\ne0\). The exact two-state witness likewise starts with +.1
per period. Learning changes the second-period gap only on repeated task
paths, producing the interaction.

## 8. Controls required before any Q1-R campaign

| Control | Expected behavior | Failure means |
| --- | --- | --- |
| MIS OFF and zero learning-rate arm | Real skills stay fixed; with exact initialization and zero observation noise, P0's mean estimates/actions are unchanged; stationary equal-marginal expected reward yields \(\Theta(0)=0\). | Hidden state transition, history-dependent decisions, information leakage, or unmatched task marginals. |
| Architecture-equivalence control | Identical competence matrices under both labels produce identical actions, state and outcome on each frozen path. | Label leakage, implementation/order mismatch, or unpaired conditions. |
| Matched competence redistribution | Preserve agent count, every per-skill total, every agent total, learning rates and information regime; enumerate frontiers before outcomes. | Architecture effect is confounded by aggregate capacity, learning parameter, or capabilities were assumed matched when not. |
| Demand-marginal control | IID and Markov begin from the same \(\pi\), with \(\pi P=\pi\); validate persistence separately. | A demand mean difference is misattributed to persistence. |
| Frozen paired exogenous paths | Every architecture/MIS arm receives the same per-replicate task trajectory, requirements, CES weights and budgets. | Environment contamination or comparison of unpaired scenarios. |
| Resource/action control | Equal budget and per-agent cap; log actual effort and residual capacity; no cross-period carryover. | Budget equality is misreported as equal use or catalog granularity changes opportunity cost. |
| Information and indexed-noise control | Same initialization/information contract; separate indexed demand, observation and any physical innovations. P0 sees estimates/public task only. | Demand ordering changes through RNG consumption or private competence is leaked. |
| Decision-margin/tie-break control **(additional indispensable)** | Record P0 score vectors, selected action, top-score gap and catalog order near boundaries; include fixed-profile/noise-free reproduction. | A putative learning mechanism is actually a tie-break/catalog artifact, or tiny estimate noise flips a discrete action without being noticed. |
| Zero-learning-rate validation | Use the implementation's legal limiting control (or MIS OFF, since `eta` validation requires (0<\eta<1)); skills and outcomes match frozen-competence arm. | The MIS contrast contains an undeclared transition. |

The current Q1 preflight already has matched initial states, common budgets,
frozen demand paths, exact frontier enumeration, MIS OFF, and zero observation
noise. The new existence check shows that adding MIS-ON analysis can be
structurally informative in some deliberately minimal cases. It does not
authorize changing the preregistered primary, scenario set, seeds, or sample
size. In a future registration, include an explicit `eta→0`/MIS-OFF negative
control and the equivalence and decision-boundary controls above.

## 9. Interpretation and decision

A nonzero \(\Theta(1)\) in this simulator is a genuine property of the
specified coupled P0–MIS dynamics: task persistence changes exposure history;
MIS changes subsequent competences; architecture-specific headroom changes
the resulting reward gap. Its magnitude and sign are also contingent on the
chosen competence profiles, saturating MIS transition, task-specific skill
weights, finite horizon, discrete action catalogue and P0's functional
lexicographic objective. These are not mutually exclusive explanations.
The witness uses additive production and therefore does not demonstrate
social synergy. Beyond this simulator, only the general accounting identity
and conditional stationary-marginal result follow from their assumptions;
the numerical sign/value and architecture pattern do not generalize without
external evidence.

**Recommendation: GO for the analytical existence/consistency claim; HOLD for
campaign design and execution.** The exact result establishes that the
current simulator can express \(\Theta(0)=0\) with
\(\Theta(1)\ne0\), so the mechanism is not structurally impossible.
However, the existing registered 24-period near-boundary MIS-OFF primary is
still a structural null and remains **NO-GO as registered**, as stated in
the preflight. No campaign redesign or execution follows from this note.
No novelty claim is made.

## 10. Reproduction

Run only the focused exact tests:

```bash
PYTHONPATH=src pytest -q tests/test_hls_q1r_analytical.py
```

The test enumerates all (2^2=4) paths and uses the same zero-noise
observation setting and frozen P0/MIS implementation. It asserts the four
expected values, the decomposition, matched skill/agent totals, and frozen
competence with MIS OFF. It does not write or update any campaign artifact or
historical hash.
