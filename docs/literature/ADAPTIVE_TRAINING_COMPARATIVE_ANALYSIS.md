# Adaptive assignment, learning, and training: evidence comparison

**Status:** targeted literature consolidation; not a systematic review and not
a novelty determination. **Evidence cut-off:** 2026-10-14. Use the reference
register for the source, full-text, and access status of each paper. “Not found
in evidence consulted” is not a claim that a mechanism is absent from the full
article.

## Evidence matrix

Legend: **C** = confirmed in full text or publisher abstract; **N** = not
found in evidence consulted (absence not established); **P** = pending full-text
verification. “Online efficacy learning” means that the decision-maker
updates an estimate of the instructor–learner–skill transfer relation from
observed teaching outcomes, not merely that workers improve over time.

| Work | Assignment / grouping | Individual learning | Teaching / transfer and dyad selection | Teaching opportunity cost | Efficacy initially unknown and learned online | Demand uncertainty / horizon | Optimization and reported result | HLS relevance / remaining uncertainty |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nembhard & Bentefouet (2015) | **C:** worker selection, grouping, and group-to-task assignment. | **C:** learning by doing. | **C:** productivity includes a transfer term derived from other workers’ experience; **N:** explicit choice of a named instructor–learner–skill triple. | **P:** production throughput is optimized, but the consulted evidence does not isolate a teaching-time decision cost. | **N:** paper uses worker learning/transfer characteristics; online posterior learning of a relation is not established by the text consulted. | **P:** parallel/serial production settings; stochastic future demand not established in consulted evidence. | **C:** heuristic policies compared with baseline and nonlinear-programming upper bound; simulations report selection/grouping/assignment effects. | Closest evidence that transfer and grouping/assignment jointly affect output. Read its full model and data calibration before claiming that online relation learning differs. |
| Jin, Hewitt & Thomas (2018) | **C:** joint worker grouping, group-to-job-group assignment, and individual job assignment; paper establishes a horizon-constant optimum under its assumptions. | **C:** experience from performing jobs. | **C:** learning from observing/interacting with co-located colleagues; worker grouping controls exposure. Transfer uses group experience and individual transfer ability. **N:** explicit per-dyad instructor selection. | **P:** grouping affects production/learning, but a separate priced teaching action is not established by consulted evidence. | **N:** transfer characteristics are model inputs; no online estimation of dyad-specific efficacy found in the full text examined. | **N:** the reported core model is a production/grouping horizon; broad stochastic future-demand integration was not established from consulted material. | **C:** nonlinear optimization reformulated as a mixed-integer program; computational study gives higher-quality solutions than prior heuristics and managerial grouping insights. | Strongest prior-art warning: interpersonal observation/transfer is already coupled to assignment. The possible distinction is learning unknown relation efficacy online, not “adding knowledge transfer.” |
| Baccara, Lee & Yariv (2023) | **C:** dynamic centralized task allocation versus discretionary provider selection. | **C:** provider expertise evolves endogenously through on-the-job training. | **N:** explicit instructor–learner–skill teaching relation not reported in the abstract/metadata consulted. | **P:** training affects service/welfare, but a distinct teaching labor cost is not established from abstract. | **N:** unknown pairwise teaching effectiveness and online inference not reported in the abstract. | **C:** dynamic arrivals and training; abstract reports arrival intensity/training technology affect centralization gains. | **C:** theoretical dynamic matching/queueing analysis; optimal protocols characterized. | Strong comparator for task allocation with endogenous expertise and future consequences; full-text comparison still required. |
| Chen, Hewitt & Thomas (2017) | **C:** daily technician-to-task assignment. | **C:** task-specific experience reduces service time; the paper states technicians learn independently on each task. | **N:** interpersonal teaching/transfer not part of the model evidence consulted. | **C:** assignments consume service capacity/time; training is not a separate teaching assignment in the core model. | **N:** technician learning rates/experience are model parameters; online inference of pair efficacy not reported. | **C:** stochastic customers, multi-period horizon, future demand revealed over time. | **C:** MDP/approximate DP and MIP; reports higher solution quality than myopic assignment. | Near-direct precedent for assignment, individual learning, and uncertain future demand; useful control domain but not evidence of teaching efficacy learning. |
| Chen, Hewitt & Thomas (2018) | **C:** daily technician assignment. | **C:** experience-based service times and individual learning. | **N:** interpersonal teaching not reported in consulted abstract. | **C:** operational service time is the capacity cost; distinct instruction action not reported. | **N:** no relation-specific online efficacy inference reported in abstract. | **C:** current jobs known, future customer/tasks uncertain, multi-period. | **C:** approximate dynamic programming with a parameterized value function; benchmarked against next-day lookahead. | Strong precedent for prospective scheduling under uncertain future demand. Full open manuscript must be inspected before stronger negative claims. |
| Valeva et al. (2017) | **C:** workforce planning/task assignment with inventory and practice/cross-training decisions. | **C:** learning through experience. | **N:** dyadic instructor–learner transfer not reported in abstract. | **C:** practice competes with production/inventory decisions; specific teacher time is not established. | **N:** online learning of training efficacy not reported in abstract. | **C:** stochastic demand and workforce planning. | **C:** stochastic integer program / matheuristic; abstract reports cross-training rises with demand uncertainty and practice responds to inventory costs/experience. | Important overlap for training/practice opportunity cost under uncertain demand; read full text to distinguish training from relational teaching. |
| Borgonjon & Maenhout (2024) | **C:** integrated staffing, days-off, and task scheduling. | **C:** learning and forgetting, including learning from regular work. | **C:** on-the-job and off-the-job training activities; **N:** selecting a particular instructor for a particular learner/skill is not established in the abstract or current source note. | **C:** training/staffing affects workforce availability and staffing budget. | **N:** online learning of instructor–learner efficacy not reported in consulted abstract. | **C:** dynamic skill mix over a planning horizon; stochastic demand remains **P** for this paper’s exact model. | **C:** constructive heuristic and branch-and-price; studies effects of learning/training on staffing. | Close overlap on explicit training cost and evolving workforce mix; full-text review needed for the teaching relation. |
| Su, Zhong & Zhang (2025) | **C:** integrated course planning and hierarchical multi-skilled employee scheduling. | **C:** workers acquire required qualifications through training courses. | **C:** course-based training; **N:** instructor–learner matching and relation-specific efficacy not reported in publisher abstract. | **C:** training fees/costs, course capacity, and precedence constraints are included. | **N:** online learning of course/instructor efficacy not reported in abstract. | **C:** changing task skill requirements motivate skill transformation; stochastic demand not established in abstract. | **C:** integer program and column-generation-based heuristic, tested on 18 instance sets. | Very recent close prior art for joint training schedule and work schedule. It may absorb broad claims about integrated training/allocation; obtain and read full text before scoping novelty. |

| Govaerts & Dochy (2014) | **P:** not an allocation-optimization paper. | **C:** review addresses application/transfer of training to work. | **C:** supervisor support comprises multiple behaviours relevant to transfer; **N:** a specific dyadic instructor–learner–skill efficacy parameter is not established by the abstract. | **P:** no shared operational production budget examined in the abstract. | **N:** online efficacy estimation not reported in the abstract. | **P:** not a stochastic workforce-demand model in the abstract. | **C:** systematic review identifies 24 supervisor support behaviours; abstract notes the construct varies across studies. | Evidence that supervision/context matters, but a caution against treating “teaching efficacy” as a validated single scalar. Read full text before operationalizing a relation parameter. |

## What the consulted evidence already establishes

1. Allocation and individual development are already jointly optimized in
   workforce scheduling. Chen et al. and Baccara et al. make the dynamic
   present/future connection explicit; Valeva et al. integrate practice with
   inventory and stochastic demand.
2. Knowledge transfer from colleagues is already modelled alongside work
   grouping and assignment. Jin et al. explicitly describe learning through
   observing/interacting with co-located colleagues; Nembhard and Bentefouet
   include a transfer term in productivity/experience.
3. Explicit training scheduling and training costs are established. Borgonjon
   and Maenhout model on- and off-the-job training with staffing consequences;
   Su et al. integrate training courses and multi-skilled scheduling.
4. Therefore, “jointly decide who works and who trains, with future skill
   consequences” is **not** an adequate novelty statement by itself.

## Potential residual question—and immediate novelty risk

A narrower candidate is: **under uncertain future task demand and a common
production/training resource budget, does online learning of the
instructor–learner–competency-specific effectiveness parameter improve
prospective joint assignment/training decisions relative to an otherwise
identical planner with fixed efficacy estimates?** The cited abstracts and the
Jin full text inspected establish transfer mechanisms and planning, but do not
establish that this exact unknown relation is inferred online. That is only a
gap in the evidence consulted, not evidence of novelty.

The proposal is at immediate risk of overlap with: (i) Jin et al.’s group-level
transfer generated by observation and interaction; (ii) Nembhard–Bentefouet’s
worker transfer parameters; (iii) stochastic workforce planning with
learning/training costs; and (iv) integrated training-course scheduling. A
broader search is required for Bayesian/adaptive training assignment,
experimental design for learning transfer rates, dyadic mentoring allocation,
and stochastic control with unknown transition parameters. Until that search
and complete-paper reading are done, no novelty or priority claim is warranted.

## Decision discipline

The next review should determine whether an online unknown θ relation adds a
scientifically consequential information state beyond known-parameter
assignment/training optimization, or merely applies standard Bayesian
adaptive control/dual control to an established workforce model. The project
must state the intended distinction and attempt reduction to these models
before proposing a new HLS mechanism.
