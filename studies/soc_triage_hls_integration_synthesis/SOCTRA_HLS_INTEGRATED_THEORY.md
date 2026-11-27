# Integrated theory: classifier triage and heterogeneous SOC organization

> **Formulación de campaña anterior:** las ecuaciones de carga y `S_+` abajo se refieren a estudios con ruta L1 seguida de L2 tras completar L1 para recomendaciones positivas. Se preservan como teoría/estimando de esa evidencia y no como descripción del flujo organizativo vigente. Véase [modelo organizativo canónico](../soc_triage_hls_availability_robustness/SOC_ORGANIZATIONAL_MODEL.md).

## System and estimand

The system combines two modules:

- SOCTRA triage supplies an escalation operating point \(\theta\), summarized by sensitivity (p_D(\theta)) and false-alarm probability (p_{FA}(\theta)).
- HLS organization supplies a staffing/resource configuration (C) and work-allocation policy (P\in\{D1,P1,WAPS\}), with heterogeneous skills, eligibility, service times, queues, and deadlines.

Let (\lambda_k(t)) be incoming alert intensity by task class (k), \(\pi_k\) the synthetic probability that a class-(k) alert needs L2, and \(Y\) the hidden need indicator. Under automatic acceptance and class-invariant classifier rates, the positive recommendation fraction is

\[
q(\theta)=\pi p_D(\theta)+(1-\pi)p_{FA}(\theta),\qquad
\lambda_{L2}(t)=\lambda(t)q(\theta).
\]

When class composition or rates vary, use \(q_k=\pi_kp_{D,k}+(1-\pi_k)p_{FA,k}\) and class-specific flows \(\lambda_{L2,k}=\lambda_kq_k\). These flows represent **offered routing demand**. L2 pool arrivals occur after L1 work is completed; service completions, utilization, and backlog are separate quantities.

The triage-to-organization transformation is

\[
\theta\to(p_D,p_{FA})\to\text{recommendations}\to\text{routed workload}\to
\text{policy assignments/queues/service}\to\text{timely correct outcomes}.
\]

The reverse relation is a constraint on selection, not a deployed feedback loop: known resources and chosen service requirements restrict which classifier points could be admissible, but no real-time mechanism has been implemented to change \(\theta\) as operational state changes.

## Joint operating region

For \(u=(\theta,P,C)\), demand \(\lambda\), minimum detection \(d_{min}\), maximum offered L2 load \(\rho_{max}\), and minimum correct/on-time service \(s_{min}\), define

\[
\mathcal F(\lambda,C)=\{(\theta,P):p_D(\theta)\ge d_{min},
\rho_{L2}(\theta,\lambda,C)\le\rho_{max},
S_+(\theta,P,\lambda,C)\ge s_{min}\}.
\]

The three constraints are not interchangeable:

1. **Detection frontier:** (p_D\ge d_{min}) constrains classifier misses.
2. **Capacity frontier:** \(\rho_{L2}\le\rho_{max}\) constrains offered work relative to effective resources.
3. **Service frontier:** (S_+\ge s_{min}) constrains the fraction of all true synthetic needs that are correctly routed and completed by deadline under the selected policy.

For homogeneous prevalence and a fixed effective capacity \(\mu_{L2}\), the fluid load is \(\rho_{L2}=\lambda q/\mu_{L2}\). The corresponding false-alarm bound is

\[
p_{FA,max}=\frac{\rho_{max}\mu_{L2}/\lambda-\pi p_D}{1-\pi},\quad \pi<1,
\]

interpreted only after checking whether its untruncated value is below zero, in [0,1], or above one. It is an offered-load boundary under the stated assumptions, not an empirical SLA boundary.

## Heterogeneous capacity

For classes (k), analysts (a), class-specific service means (s_{ak}), and eligible set (E_a), let (x_{ak}\ge0) denote assigned flow. A fluid capacity check at margin \(\rho_{max}\) asks whether

\[
\sum_{a:k\in E_a}x_{ak}=\lambda_kq_k(\theta)\quad\forall k,
\qquad \sum_k s_{ak}x_{ak}\le\rho_{max}\quad\forall a.
\]

This assignment problem recognizes skill and eligibility bottlenecks. Feasible average flow does not ensure stable transient queues or deadline compliance: variability, the dispatch policy, initial backlog, and burst structure still matter. Conversely, if offered sustained work exceeds feasible capacity, organization alone cannot remove that work deficit.

## Service outcome

Let (Y=1) indicate a synthetic need for L2. Under the pilot's automatic acceptance, no downstream rescue of false negatives, and route definitions,

\[
S_+(\theta,P,\lambda,C)=P(\text{correctly routed and completed before deadline}\mid Y=1)
=p_D(\theta)G(P,\lambda,C),
\]

where (G=P(\text{L2 timely completion}\mid Y=1,\text{positive recommendation})). Hence theoretically (S_+\le p_D\). A false negative may physically finish L1 but receives no credit in (S_+\). This differs from global SLA, routed-path SLA, physical completion, and aggregate R/N, which remain separately reported outcomes.

For two policies, \(\Delta(P_1,P_2)=S_+(\theta,P_1,\lambda,C)-S_+(\theta,P_2,\lambda,C)\) is meaningful only on matched classifier/need/alert traces and the same denominator. The frontier validation reconstructs pooled (S_+\) from integer timely-needs counts over all needs; zero-positive seeds are undefined, not zero-performance observations.

## Evidential status of the arrows

| Link | Status in this research |
|---|---|
| Published (p_D,p_{FA}\) to expected recommendation fraction | Analytically derived under explicit prevalence and class-invariance assumptions. |
| Recommendation to L1/L2 workload | Implemented and simulated with automatic acceptance and synthetic recommendations; trace outcomes are not individual SOCTRA predictions. |
| Workload to queues, utilization, deadlines and outcomes | Implemented and evaluated in the frozen HLS simulator under its roster, services, eligibility, continuous capacity, and deadlines. |
| Policy differences conditional on classifier point | Evaluated through paired, exploratory simulations; interaction signs vary by operating stratum. |
| Resources/SLA to classifier feasibility set | Formulated analytically and evaluated post hoc on saved simulation outcomes. |
| Operational state changing the live classifier/threshold | Conceptual only; not implemented or validated. |
| Real analyst acceptance and real L2 need | Not measured; remain unvalidated assumptions/unknowns. |

The formulation is a useful bookkeeping and selection framework, not a claim of a new theorem or an operational closed-loop controller.
