# HLS — Benchmark value and implementation investment assessment

**Date:** 2026-10-19

**Question:** Is Chen, Hewitt and Thomas (2018; CHT18) sufficiently established and reusable to justify a separate HLS scheduler and reproduction of its algorithms?

## Executive decision

**Recommendation: DEFER IMPLEMENTATION.** CHT18 is a relevant, peer-reviewed operations-research study, and its scientific problem is close to HLS’s interest in assignment-dependent capability evolution. But the evidence does not support calling it an established, independently reused benchmark. The publisher lists 17 citations at the time checked (another index lists 19); verified subsequent work cites or extends the model family, but no independent reproduction of CHT18’s ADPBF/ADPOL comparison, original instances, or figures was found. The paper’s own text states that its mathematical problem was first formulated in Chen et al. (2017); the distinctive 2018 contribution is ADPBF’s longer-horizon approximate value-function method and its computational comparison with ADPOL.

Full reproduction therefore means substantial work: a new job-level simulator, ADPOL, ADPBF, optimization backend, and experimental pipeline. The existing HLS N×K simulator cannot be configured to do this faithfully; the compatibility audit documents why. There is no verified public code, generated instance set, or seed archive to reduce that burden. A limited environment-only implementation would not reproduce CHT18’s principal algorithmic contribution and should not be represented as a paper reproduction.

The nearest alternative worth considering later is Chen et al. (2024), which continues the experience-dependent technician-routing line and adds implicit cross-training. It is even broader (routing and service costs) and has no verified code/data package in this search, so it is not an immediate low-cost substitute. If the immediate objective is a benchmark of dynamic multi-skilled assignment without endogenous learning, Annear et al. (2023) has a stronger industrial comparison, but its worker availability/skill model is not a capability-development benchmark. Neither alternative warrants implementation without a focused protocol choice.

This is an investment recommendation, not a novelty judgment. No code or experiments were changed or run.

## 1. Method and evidence limits

The search checked the local primary article and the compatibility audit, then searched publisher and institutional records, citation displays, exact-title/DOI searches for code, repositories, datasets and instances, and subsequent literature specifically describing reuse. Search date: 2026-10-19. Primary-source claims below are linked to publisher or institutional records where accessible. Secondary indexes are used only for discovery and cross-checking, not to establish an algorithmic reproduction.

The article is available locally at [`Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf`](../literature/competence_evolution/Chen_et_al_2018_Approximate_Dynamic_Technician_Scheduling.pdf); the mathematical reconstruction and unambiguous-versus-unresolved source details are in [`HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md`](HLS_CHEN_FULL_TEXT_MATHEMATICAL_AUDIT_2026-10-19.md). The engineering comparison is in [`HLS_CHEN_SIMULATOR_COMPATIBILITY_AUDIT_2026-10-19.md`](../experiments/HLS_CHEN_SIMULATOR_COMPATIBILITY_AUDIT_2026-10-19.md).

Citation counts vary by index and are time-sensitive. They indicate discoverability/citation, not use as a reproducible benchmark. Search engines did not expose a verified year-by-year citation series for this article; therefore this report does **not** claim a citation growth or decline curve.

## 2. Scientific impact and benchmark adoption

### Bibliographic impact

* **FACT:** ScienceDirect’s CHT18 record displayed “Cited by (17)” when checked. SciSpace displayed 19 citations for the same DOI. Those counts differ by index and should be quoted with source and date, not treated as a canonical count. [ScienceDirect article record](https://www.sciencedirect.com/science/article/pii/S0925527317303432), [SciSpace record](https://scispace.com/institutions/beijing-foreign-studies-university-2b4lb76i/2018).
* **FACT:** The paper appears in the literature discussion of independent work on dynamic multi-skilled workforce assignment and in later surveys of technician scheduling. Annear, Akhavan-Tabatabaei and Schmid (2023) cite CHT18 in a different job-shop model; Cordeau, Iori and Vezzali’s 2024 survey discusses CHT17/18 as multi-period technician scheduling that isolates assignment from routing; a 2026 model-based survey also cites the line. [Annear et al. publisher record](https://www.sciencedirect.com/science/article/pii/S0377221722006920), [Cordeau et al. survey](https://doi.org/10.1007/s10479-024-06241-9), [2026 survey record](https://link.springer.com/article/10.1007/s00291-026-00865-y).
* **FACT:** The most direct subsequent research is Chen et al. (2024), from overlapping authors, on multi-period technician routing and scheduling with experience-based service times and an implicit cross-training strategy. Its abstract explicitly situates the work in the Chen et al. technician routing/scheduling line and reports an ADP cost-function approximation compared with a myopic policy. This is meaningful continuation of the research model, but not independent implementation or validation of CHT18’s ADPBF/ADPOL result. [Chen et al. 2024 publisher record](https://www.sciencedirect.com/science/article/pii/S0925527324000653).
* **INFERENCE:** The demonstrated citation pattern is specialist relevance and continued development, not broad benchmark standardization. A current count in the teens and related surveys do not establish that other researchers use CHT18’s generated experiments as a reusable benchmark suite.

### Verified reuse, not just citation

| Subsequent source | Evidence and form of reuse | What it does **not** establish |
|---|---|---|
| Chen, Thomas & Hewitt (2017), “Multi-period technician scheduling with experience-based service times and stochastic customers,” *Computers & Operations Research* 82, 1–14, DOI [10.1016/j.cor.2016.12.026](https://doi.org/10.1016/j.cor.2016.12.026) | CHT18 §3 explicitly says the formulation first appeared in this 2017 paper and is repeated in 2018; CHT18 uses the earlier paper’s one-day-lookahead ADPOL solution method as its comparator. This is same-line model/policy continuity, not independent adoption. [2017 publisher record](https://www.sciencedirect.com/science/article/pii/S0305054816303410). | It does not provide independent validation of ADPBF versus ADPOL. |
| Annear, Akhavan-Tabatabaei & Schmid (2023), “Dynamic assignment of a multi-skilled workforce in job shops,” *EJOR* 306(3), 1109–1125, DOI [10.1016/j.ejor.2022.08.049](https://doi.org/10.1016/j.ejor.2022.08.049) | CHT18 is cited in the article’s literature framing. The authors build a different MDP/ADP for a multi-station automotive-glass job shop with stochastic orders/processing and variable worker availability, report real-company data and average 15% improvement against their own benchmark assignment policies. This is independent adjacent research, not reuse of CHT18’s technician experience equation, ADPBF/ADPOL, or instances. [Publisher record](https://www.sciencedirect.com/science/article/pii/S0377221722006920). | No evidence that the result replicates CHT18; its dynamic skill/availability structure is not CHT’s endogenous task-specific learning state. |
| Chen, Li, Lin & Ding (2024), “Technician routing and scheduling with employees’ learning through implicit cross-training strategy,” *IJPE* 271, 109208, DOI [10.1016/j.ijpe.2024.109208](https://doi.org/10.1016/j.ijpe.2024.109208) | Direct continuation/reuse of the experience-based service-time technician-routing model family. Adds travel/routing cost and ICT cross-training through assignment to less-familiar task/customer types; tests against a myopic baseline. [Publisher record](https://www.sciencedirect.com/science/article/pii/S0925527324000653). | It is not an independent reproduction of CHT18; it changes the problem and comparator, and does not expose CHT18’s original instances/code. |
| Cordeau, Iori & Vezzali (2024), “An updated survey of attended home delivery and service problems…” | Review use: places Chen et al. 2017/2018 in multi-period technician scheduling and differentiates those assignment-only studies from later routing work. [Survey DOI](https://doi.org/10.1007/s10479-024-06241-9). | A review citation is not benchmark reuse. |

No verified later paper was found to reuse CHT18’s 30 sampled workforces, 600 configurations, request paths, ADPBF coefficients/training data, or to report a direct numerical reproduction of Figures 1–5. Nor was an independent paper found implementing both ADPBF and ADPOL as CHT18 defines them.

### Classification

**CHT18: RELEVANT INDIVIDUAL STUDY.** Its model family is reused by its own 2017 precursor and subsequent same-line work, but evidence is insufficient to classify the 2018 computational experiment as an established benchmark. It is more than an isolated mathematical curiosity: the experience-dependent technician assignment problem has clear follow-on literature. That is not the same as independent benchmark adoption.

## 3. Reproducibility resources

| Resource searched | Finding | Verification status |
|---|---|---|
| Publisher article, author/university portals, exact DOI/title web queries | Full article and metadata are accessible; publisher page offers article/open manuscript access. No code/data link was identified in the article record or inspected full text. | Article verified; no linked implementation verified. |
| Exact-title/DOI GitHub and repository searches | No official CHT18 repository or independent implementation that demonstrably implements Eqs. (1)–(20), ADPOL and ADPBF was found. | Negative search result, not proof that no private/unindexed code exists. |
| Supplementary files, benchmark instances, request traces | No public generated workforce set, exact 1,000 training/testing paths, or original seeds found. | Not located. The paper’s design is distributional, not a published benchmark archive. |
| Dissertation/materials and related 2017 paper | Public descriptions and a dissertation chapter discuss the model and ADP, but no verified downloadable package reproducing CHT18’s experiments was identified. | Relevant documentation, not a runnable reproduction artifact. |
| CHT 2024 and Annear 2023 | Publisher/institutional records establish follow-on/adjacent papers and describe computational studies. No author-maintained solver/data bundle was verified in the search. | Papers are evidence of follow-on science, not code/data availability. |

An unrelated technician scheduling package, generic job-shop dataset, or tool that uses a learning curve would not count as CHT18 reproduction unless it implements the request assignment constraints, experience transition, service-time objective, and the target ADPOL/ADPBF decision procedures. The HLS compatibility audit found no such implementation in this repository.

## 4. Candidate alternatives

At most three alternatives are considered; none is treated as a drop-in HLS model.

### Candidate A — Chen et al. (2024), implicit cross-training (closest model family)

**FACT:** A multi-period technician routing/scheduling MDP has heterogeneous technician experience and learning rates, stochastic daily customer requests, and experience-based service times; objective combines routing and service-time cost. ICT approximates future value and intentionally assigns unfamiliar tasks to accumulate experience; the reported comparator is a myopic strategy. Publisher metadata reports 11 cited-by entries at the time searched. [Publisher article](https://www.sciencedirect.com/science/article/pii/S0925527324000653).

**Fit:** strongest topical extension of CHT for endogenous task-specific experience and allocation; adds assignment/capability interaction and routing. **Cost:** high—the HLS runner would need routes, travel/service costs and a different state/action contract; a new CFA/ICT policy and evaluation trace are needed. Code/data not verified. This is the most defensible *scientific successor to examine* if the requirement is explicitly experience-coupled allocation, but it is not a cheaper or more reproducible benchmark than CHT18.

### Candidate B — Annear et al. (2023), dynamic multi-skilled job-shop assignment

**FACT:** Dynamic technician-to-station assignment under uncertain customer orders, stochastic processing times and variable workforce availability; worker skills define eligible stations; MDP solved with ADP and hill-climbing action selection. The publisher reports a real automotive-glass application and average 15% productivity improvement over its best benchmark policy. [Publisher article](https://www.sciencedirect.com/science/article/pii/S0377221722006920).

**Fit:** comparatively clear dynamic assignment baseline and real operational use. **Mismatch:** no assignment-dependent learning/capability development established in the article’s abstracted model; heterogeneity is skill eligibility/availability, not CHT-style evolving experience. Real company data are described, but public raw data/code were not verified. HLS would need the job-shop station/process/productivity model, processing-time/order processes, and algorithm/baselines, likely high environment and policy cost. Useful only if HLS wants to validate dynamic allocation under exogenous uncertainty, not learning-induced capability evolution.

### Candidate C — Borgonjon & Maenhout (2024), dynamic learning/training and staffing

**FACT:** Integrates personnel staffing/task assignment with on-/off-job training and dynamic skill evolution including learning and forgetting; solution uses branch-and-price and evaluates training variants. An accepted manuscript is openly available from Ghent University. [Institutional record and manuscript](https://biblio.ugent.be/publication/01HGGHV3X0Y4DY4M4RHV1NG5QS), [DOI](https://doi.org/10.1016/j.cie.2023.109784).

**Fit:** closest alternative for explicit training and skill evolution; more diversified learning/forgetting mechanisms than CHT. **Mismatch:** primary decision is integrated staffing/scheduling and training over a planning horizon, not the same online stochastic technician assignment MDP; HLS would need days-off, task windows/resource requirements, forgetting, off-job training and branch-and-price/staffing objective. The author archive has a manuscript, but no verified runnable code or public instance set. Likely very high implementation cost.

The 2026 warehouse picker-capability paper (Wang, Xiang & Chen, DOI [10.1016/j.tre.2026.105040](https://doi.org/10.1016/j.tre.2026.105040)) is noted but not ranked: it is a newly published data-driven capability/online-assignment study with warehouse data, and available evidence does not establish capability as an endogenous consequence of assignments; raw data/code availability is not verified. It is not yet a stable, independently reused benchmark.

## 5. Comparative investment matrix

Effort is relative implementation/validation burden, not calendar time. It reflects the existing interfaces and actual algorithms required.

| Benchmark | Scientific recognition | Independent reuse | Available code/data | Mathematical fit to HLS | Implementation cost | Value as comparator |
|---|---|---|---|---|---|---|
| **CHT18 full reproduction** | Peer-reviewed IJPE; 17 citations on publisher display (index counts vary) | Limited: direct same-line development and citations; no verified independent ADPBF/ADPOL reproduction | Paper only; no verified official code, data, seeds or instances; Table 1 mapping ambiguities remain | High topical fit for task-specific experience; low direct fit to N×K action/resource/objective contracts | Environment **HIGH**; ADPOL **HIGH**; ADPBF **HIGH**; experiment **HIGH**; maintenance/validation **HIGH** | Strong comparison of ADPBF against its one-day-lookahead ADPOL, but not against optimized strong-SEP/best static; reproducibility limitations diminish exact benchmark value |
| **CHT18 limited environment only** | Same source, but not the algorithmic result | Same | Same | Tests service-time/experience dynamics, not the claimed ADPBF result | Environment **MEDIUM–HIGH**; policy **LOW** if omitted; experiment **MEDIUM**; validation **MEDIUM** | Useful as a mathematical fixture, weak as a benchmark; should not be called reproduction of CHT18 |
| **CHT24 ICT** | Peer-reviewed IJPE; cited-by display 11 at search time | Follow-on citations emerging; independent replication not established | Article accessible; no verified code, dataset or exact instance archive | Very high thematic fit, but routing/service-cost semantics exceed HLS N×K | Environment **HIGH**; baseline **MEDIUM–HIGH**; ICT **HIGH**; experiment **HIGH**; maintenance **HIGH** | Potentially stronger learning/cross-training comparison but broader, more expensive and not a reproducibility shortcut |
| **Annear et al. 2023** | Peer-reviewed EJOR; reports real company case and 15% average improvement over its benchmark | Cited in adjacent job-shop literature; independent reproduction not verified | Real company data used, but public dataset/code not verified | Moderate for adaptive allocation; weak for endogenous capability evolution | Environment **HIGH**; policies **HIGH**; experiments **HIGH**; maintenance **HIGH** | Strong dynamic-allocation benchmark in its own industrial model; weak direct comparator for HLS learning-by-doing question |
| **Borgonjon & Maenhout 2024** | Peer-reviewed C&IE; institutional manuscript accessible | Literature citations; independent replication not verified | Accepted manuscript available; no verified runnable code/instances | Strong for skill evolution/training, weaker for online dynamic assignment | Environment **HIGH**; baselines/branch-price **HIGH**; experiment **HIGH**; maintenance **HIGH** | Useful if HLS’s question shifts toward explicit training/staffing; not a low-cost replacement for CHT |

### Why cost is high despite reusable HLS primitives

The compatibility audit shows that `OrganizationConfigNK`, `ProblemSpecNK`, `run_nk_production_sequence`, and `NembhardDirectProfileNK` are not a CHT substrate: they encode N×K competence/effort vectors, divisible work, and effort budgets. CHT needs per-request binary assignment, integer task-specific experience, service-time capacity, batched daily demand, and total service-time objective. Existing C5 processes emit a problem per period, not 50 individually typed requests; P0/P1/P2 and Nembhard routers are not ADPOL/ADPBF. `synthetic/exact.py` solves a separate small HLS world and does not add a CHT optimizer. `pyproject.toml` has no MILP solver dependency. These are separate environment/policy implementations, not adapter glue.

## 6. Recommendation

### Selected option: **4. DEFER IMPLEMENTATION**

Do not authorize a full CHT18 reproduction or begin a limited simulator now. The expected investment is high and the project would have to recreate both scientific software and a nontrivial experimental pipeline without public original instances, seed paths or code. The 2018 paper remains a useful **reference model and algorithmic comparator**, but current evidence does not show it has benchmark adoption strong enough to justify this cost by itself.

### Most defensible alternative to evaluate next

If the PI’s central near-term need remains **allocation coupled to endogenous experience**, inspect CHT24 ICT first as the closest successor, while acknowledging it is a same-line extension and not a reproduced benchmark. If the PI instead needs an independent benchmark for **dynamic allocation under uncertainty**, Annear et al. (2023) is the clearer alternate study, but it does not test capability growth. Neither should be implemented before obtaining their full-source/instance/code status and fixing the exact HLS validation question.

### Low-cost next action (documentary only)

Before any code investment, request from CHT18 authors (or locate supplementary material) clarification of Table 1’s `log I` and `F` coordinates, initial-experience mapping, draw-domain treatment, and whether the original 30 workforces/test paths/ADPBF initial coefficients are recoverable. Also obtain the Chen et al. (2017) source/formulation details required for ADPOL. If these materials are unavailable, the PI can make an informed decision whether an explicitly approximate reproduction is still worth the high engineering cost.

## 7. Evidence classifications and limits

**FACT:** CHT18 is peer-reviewed and mathematically specifies technician-specific experience-dependent service times, stochastic daily requests, finite-horizon assignment, ADPBF, and ADPOL. Its source reports an ADPBF-vs-ADPOL computational comparison and not an optimized static/strong-SEP comparison. The exact source and unresolved parameter/data limitations are documented in the local full-text audit.

**FACT:** publisher citation display is 17; another index gives 19. Verified follow-on sources cite or extend the model family. No public official CHT18 code/data/instance set or independent ADPBF/ADPOL numerical reproduction was verified in this search.

**INFERENCE:** CHT18 is a relevant individual study and a plausible high-effort replication target, but not currently a sufficiently reusable benchmark to warrant a new HLS simulator on benchmark value alone.

**PROPOSAL:** defer implementation; assess CHT24 for endogenous experience-coupled allocation or Annear et al. for independent dynamic assignment, depending on the exact research question.

## References

1. Chen, X., Hewitt, M., & Thomas, B. W. (2018). *An approximate dynamic programming method for the multi-period technician scheduling problem with experience-based service times and stochastic customers*. IJPE 196, 122–134. [DOI](https://doi.org/10.1016/j.ijpe.2017.10.028) · [Publisher record](https://www.sciencedirect.com/science/article/pii/S0925527317303432).
2. Chen, X., Thomas, B. W., & Hewitt, M. (2017). *Multi-period technician scheduling with experience-based service times and stochastic customers*. COR 82, 1–14. [DOI](https://doi.org/10.1016/j.cor.2016.12.026).
3. Annear, L. M., Akhavan-Tabatabaei, R., & Schmid, V. (2023). *Dynamic assignment of a multi-skilled workforce in job shops: An approximate dynamic programming approach*. EJOR 306(3), 1109–1125. [DOI](https://doi.org/10.1016/j.ejor.2022.08.049).
4. Chen, X., Li, K., Lin, S., & Ding, X. (2024). *Technician routing and scheduling with employees’ learning through implicit cross-training strategy*. IJPE 271, 109208. [DOI](https://doi.org/10.1016/j.ijpe.2024.109208).
5. Borgonjon, T., & Maenhout, B. (2024). *The impact of dynamic learning and training on the personnel staffing decision*. C&IE 187, 109784. [DOI](https://doi.org/10.1016/j.cie.2023.109784).
6. Cordeau, J.-F., Iori, M., & Vezzali, D. (2024). *An updated survey of attended home delivery and service problems with a focus on applications*. [DOI](https://doi.org/10.1007/s10479-024-06241-9).
