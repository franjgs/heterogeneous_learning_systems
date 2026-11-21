# Simulator specification and parameter provenance

## System boundary

The synthetic experiment accepts alert arrivals at L1, generates a hidden binary need for L2, draws a synthetic escalation recommendation from a fixed published operating point, runs every alert through L1, and sends accepted positive recommendations to an independent L2 queue after L1 completion. No report classifier is included. The decision rule is automatic acceptance, solely to isolate the workload effect; it is not an observed GMV-CERT behavior.

## Parameter provenance

| Parameter | Value | Provenance / use |
|---|---|---|
| SOCTRA rates | Three standardized, symmetric-cost A+C points in `config/primary_campaign.json` | Published article Table 5, PDF p.39; held fixed. Synthetic recommendations only. |
| Need prevalence | \(19/14,449=0.001314969894110319\) | Standardized test-label prevalence verified in source audit; used as a synthetic need probability, not objective truth. |
| Project mix | 0.592 / 0.236 / 0.172 | Anonymized aggregate workload strata from the existing HLS reference model. |
| Alert arrival process | Poisson arrivals, 24 h admission, \(\lambda=1.25\mu_{L1}\) | Existing generator; 6 L1 roster and capacity function. |
| Severity mix | 0.50 low / 0.35 medium / 0.15 high | Synthetic model assumption. |
| Deadlines | 12 h low / 4 h medium / 1 h high | Synthetic terminal-resolution assumptions. |
| Need across classes | Same \(\pi\) for all three project strata | Exchangeability assumption; class-specific need is hidden. |
| Recommendation generation | Per-alert keyed common uniform; TP if U<pD; FP if U<pFA | Synthetic Bernoulli mechanism; common random number across points. |
| Acceptance | 100% recommendation acceptance | Controlled assumption, not measured behavior. |
| Staffing | 6 L1; L2 roster 2, 3, or 4 | Existing frozen heterogeneous roster. Demand rate is fixed across L2 sizes. |
| Eligibility | L1 mean eligible projects 2.5; exact patterns from existing roster builder; L2 all three classes | Existing synthetic roster, not a measured GMV staffing map. |
| Base L1 service | 0.20 / 0.25 / 0.30 h by class, multiplied by analyst speed | Synthetic model assumption. |
| Base L2 service | 0.75 / 0.90 / 1.00 h by class, multiplied by analyst speed | Synthetic model assumption; full-task benchmark. |
| Competence | Existing fixed analyst × class profiles | Synthetic model assumption; quality proxy uses competence and difficulty. |
| Difficulty | Beta(2,2) | Synthetic assumption, used in quality proxy. |
| FP total work | \(\alpha\times\) comparable full L2 service; alpha=.25,.50,.75,1 | Sensitivity only, not GMV measurement. |
| WAPS | 4 h window, lower/upper hysteresis 1.05/1.20 | Frozen configuration. Capacity denominator is recalculated for the expected class/work mixture at each alpha. |
| Drain | 36 h after admission | Existing terminal follow-up; maximum generated deadline is <=36 h after arrival; cutoff at 60 h. |

## Event and information semantics

Arrivals and classes are generated before the episode, but dispatchers receive only current pending alerts, their observed class/deadline/arrival metadata, the roster, and service estimates. The truth of synthetic need and its recommendation confusion status are environment-only fields. L1 dispatch never receives these fields. At L1 completion, positive recommendations create L2 arrivals at that timestamp. The L2 event loop processes arrivals, completions, then dispatch, matching the frozen engine's order.

For \(\alpha<1\), a false-positive L2 job has a shorter realized total duration, but dispatch decisions use an *ex ante* expected service map. This map is conditioned only on published \(p_D,p_{FA}\), \(\pi\), project class and alpha. It does not use that alert's hidden label. A job's completion can affect later dispatch only after the event occurs. This aggregate duration model is the minimum causal approximation supported by the current task representation; it is not a two-stage human verification workflow.

## Capacity and workload quantities

For class \(k\), \(q_k=\pi_k p_D+(1-\pi_k)p_{FA}\). Among recommendations in class k, the expected TP fraction is \(\pi_kp_D/q_k\), and expected FP fraction is \((1-\pi_k)p_{FA}/q_k\). The ex ante service estimate at alpha is the base class/analyst duration multiplied by

\[
f_k(\alpha)=\frac{\pi_kp_D+\alpha(1-\pi_k)p_{FA}}{q_k}.
\]

The fractional-flow LP recomputes effective L2 capacity from the same roster and expected class mix. \(\rho_{L2}\) is an offered-arrival/capacity marker; it is not realized utilization and does not guarantee SLA. Work generated, executed service, work still pending, FP work and FN-omitted necessary work are output separately.

## Outcomes

- **Detection:** synthetic TP / all synthetic needs.
- **Need service \(S_+\):** TP alerts completing by both terminal cutoff and individual deadline / all synthetic needs.
- **Global/routed SLA:** all admitted alerts whose physical route completion meets the deadline / admitted alerts; does not equal \(S_+\).
- **Need-correct timely per admitted:** timely TP count / admitted alerts.
- **Need quality timely per admitted:** for timely TPs only, \(competence\times(1-.35\,difficulty)\), summed and divided by admitted.
- **Load:** TP, FP, FN, TN; L2 arrivals, assignments, completions; nominal offered hours, executed hours, utilization and backlog.

No utility combines these dimensions.
