# Literature relevant to HLS

This is a critical map of established work that informs HLS, not a claim that HLS has already integrated or extended every field listed. BibTeX metadata are maintained once in [hls.bib](../references/hls.bib). DOI and publisher metadata for the key sources below were checked against publisher, proceedings or DOI-registration records on 2026-10-27; the bibliography records identifiers and source URLs. References inherited from the historical repository should be rechecked before being used as support for a new claim.

## Decision theory, information and sequential decisions

Decision theory supplies the basic connection among information, beliefs, actions and consequences. Blackwell's comparison of experiments characterizes when one statistical experiment is at least as useful as another across decision problems under its formal conditions [@blackwell1951comparison; @blackwell1953equivalent]. It informs HLS questions about what information is sufficient for decisions; it does not establish that an individual capability summary is sufficient for an organizational policy. Goel and DeGroot connect experiment comparison to information measures [@goel1979comparison]. Howard's value-of-information formulation makes the action-dependent value of a signal explicit [@howard1966information]. An HLS application must still state the decision problem, prior/model, observation cost and available actions.

Dynamic programming and Markov decision processes formalize sequential state, action, transition and return [@puterman1994mdp; @bertsekas2017dynamic]. The HLS finite two-period value decompositions reduce to continuation-value reasoning under their stated assumptions; their notation does not create a new general dynamic theory. Stationarity, Markov state sufficiency, reward structure and known transition laws are substantive assumptions, not defaults.

Bandit methods study sequential allocation when outcomes are uncertain and feedback is limited. Finite-time UCB analysis [@auer2002finite], contextual bandits [@li2010contextual], and allocation indices [@gittins1979bandit] offer methods for exploration and assignment. Their regret or reward guarantees depend on reward, feedback and stationarity assumptions. They do not automatically apply when actions alter competence, queues, or the future feasible organization.

## Operations research, assignment, scheduling and queues

Assignment and scheduling theory formalize feasibility, precedence, capacity, objective functions and resource allocation. Multi-skill workforce scheduling explicitly links skills to resource-constrained tasks; alternative mathematical formulations can encode different semantics [@almeida2019multiskill]. This is directly relevant to HLS, but a skill requirement, competence probability and task success model must not be conflated.

Queueing theory describes arrival/service processes, waiting and load-dependent performance. Little's relation connects long-run average number in system, throughput and time under its stability and measurement conditions [@little1961proof]. A deadline-aware system also needs its own admission, service, deadline and outcome rules; a utilization metric alone does not specify success-on-time. Scheduling or queueing models can be reused only after aligning units, horizon, job requirements and objective.

Decision-focused learning studies predictions trained for downstream optimization rather than predictive loss alone [@elmachtoub2021smart; @mandi2024decisionfocused]. It is relevant where competence estimates feed assignment. The distinction between prediction error and decision loss is established; HLS-specific claims require a declared downstream problem and competitive baselines.

## Coordination and organization

Coordination theory treats dependencies among tasks/resources and mechanisms for managing them [@malone1987coordination; @crowston1997coordination]. It helps describe why organizational structure and policy are separate: structure determines possible dependencies and access; a mechanism or policy manages decisions. These theories do not imply one structure is universally optimal.

Formal work on knowledge hierarchies models how problem-solving knowledge and communication costs shape organizational allocation [@garicano2000hierarchies]. Multi-skilled scheduling studies operational skill coverage [@almeida2019multiskill]. HLS overlaps with both, but its broad concern with capabilities does not yet supply a unified theory of expertise, hierarchy or labor design. Any application to people requires constructs and evidence appropriate to that domain.

Multi-agent systems provide models and methods for interacting decision-makers, coordination and joint action [@weiss2016multiagent]. The field is broad; a system with multiple agents is not automatically an HLS contribution. The relevant comparison is the exact interaction model, information, objective and coordination mechanism.

## Organizational learning and competence development

Organizational learning research distinguishes experience, knowledge creation, retention and transfer, and emphasizes context [@argote2011organizational]. March's exploration/exploitation analysis identifies a durable tension in organizational learning [@march1991exploration]. Reinforcement learning formalizes learning to act from reward and interaction [@sutton2018reinforcement]. These traditions are not interchangeable: individual parameter updates, organizational knowledge transfer, policy adaptation and competence development have distinct state and causal mechanisms.

HLS historical finite models show that a competence-state change need not expand an efficient collective frontier and that a development action can have negative immediate but positive continuation value in a constructed case. These results are compatible with established dynamic decision theory; they do not show that training generally improves collective outcomes. The open issue is how to identify and measure transitions, costs, transfer and organization-mediated use in a particular system.

Direct work on workforce learning and allocation already studies selection, grouping and task assignment with learning-by-doing and knowledge transfer [@nembhard2015selection]. A related dynamic matching model makes provider expertise endogenous to task allocation and on-the-job training, and compares centralized protocols with discretionary choice [@baccara2023task]. These papers make broad claims that assignment and learning interact unsuitable as novelty claims by themselves. Their worker/productivity and matching assumptions are not automatically the same as HLS competence or organization; a faithful comparison must map those objects and objectives.

## Heterogeneous human-AI and model routing

Recent mixed-language-model routing work optimizes query-specific quality, cost and latency using contextual prediction and routing [@wang2025mixllm]. It is a close application-level overlap with capability allocation: models have heterogeneous observed strengths and a selector assigns queries. Its assumptions about candidate pool, feedback labels, latency constraints and evaluation define its scope. HLS should not claim novelty for routing heterogeneous models without a precise result beyond such work.

Fast/slow computation also has direct precedent in hybrid planning systems. System-1.x learns a controller to split planning into subgoals handled by fast and search-based planners, using one base language model and a search budget [@saha2025systemone]. This overlaps with deliberation-budget allocation, but its modes are not independent heterogeneous agents, and its planning benchmarks and training protocol differ from HLS organizational settings. It is a relevant comparator for a deliberation question, not evidence that an HLS mechanism is new.

Human organization and AI routing are not semantically equivalent merely because both assign tasks to heterogeneous workers/models. Human learning, workload, accountability, job quality, privacy and social welfare may require additional constructs and evidence. The HLS framework permits these applications but provides no empirical validation of any real SOC or human organization in the current branch.

### SOC alert work and the proposed HLS testbed

Two primary studies help delimit, rather than validate, the proposed SOC application. Kersten et al. studied Tier-1 alert investigations with think-aloud work in one collaborating commercial SOC; their small cohorts showed that investigation processes varied across analysts and alert types, and evaluated a support tool in that setting [@kersten2025tier1]. Yang et al. analyzed four years of alert logs and attack ground truth from one real SOC, documenting that alert labels and operational outcomes are not reducible to a simple “true/false alert” distinction [@yang2024socalerts]. These are setting-specific studies; neither supplies the present testbed's client data, competence matrix, L1 decision semantics, L2 handoff, or outcome model.

Candidate mechanisms can be drawn from established work on organizational learning and task allocation with training or transfer [@argote2011organizational; @baccara2023task; @nembhard2015selection]. For this application, they motivate separately testable constructs: experience-based updating, deliberate development, cross-analyst transfer, and assignment to tasks under workload constraints. The literature does not establish that any of these mechanisms occurs in the target SOC or improves its collective performance. A study must measure individual competence separately from experience and evaluate effects and costs at both individual and collective levels.

## What is established, and what remains open for HLS

The literature already contains mature theories for information comparison, sequential decisions, resource allocation, queues, coordination, learning and contextual routing. HLS's current distinctive role is integrative and question-forming: requiring explicit links among scenario, organization, model and evaluation, and preserving distinctions between attainable capability and realized performance. That semantic organization is useful, but is not by itself a scientific discovery.

Potential contributions would need to identify a nontrivial, generalizable property under explicit assumptions—for example, a theorem about when a capability representation preserves decision value across a defined policy class, or a replicated empirical mechanism showing when organizational constraints change the value of specialization. The repository's current exact finite cases and synthetic experiments do not establish those broader results. Originality must be assessed against the directly relevant literature for each question.

## Annotated core references

| Key | Contribution and assumptions | HLS connection and limitation |
|---|---|---|
| [@blackwell1951comparison; @blackwell1953equivalent] | Formal comparison of statistical experiments by decision value. | Relevant to information sufficiency; does not directly solve organizational assignment with endogenous states/costs. |
| [@puterman1994mdp; @bertsekas2017dynamic] | Sequential optimization under state, action, transition and reward specifications. | Grounds continuation value; Markov/transition assumptions must be justified. |
| [@auer2002finite; @li2010contextual] | Regret-based allocation under bandit feedback, with contextual extensions. | Useful for partial-feedback policies; guarantees may fail under nonstationarity or action-dependent competence. |
| [@almeida2019multiskill] | Compares formulations for multi-skill resource-constrained scheduling. | Closely informs skill/task feasibility; formulation choices alter semantics. |
| [@little1961proof] | Queueing identity under long-run stable-system conditions. | Helps interpret load and waiting; does not replace deadline-specific evaluation. |
| [@malone1987coordination; @crowston1997coordination] | Formal coordination structures and task/resource dependencies. | Informs organization/policy distinctions; no universal organizational ranking. |
| [@garicano2000hierarchies] | Knowledge and problem-solving allocation through hierarchy. | Relevant to specialization and organizational design; model-specific economic assumptions. |
| [@argote2011organizational; @march1991exploration] | Organizational experience/knowledge and exploration–exploitation trade-offs. | Informs learning and development; not interchangeable with individual competence updates. |
| [@nembhard2015selection; @baccara2023task] | Workforce selection/grouping/assignment with learning and transfer; dynamic task allocation with endogenous training. | Direct prior art for allocation-learning interactions; constructs and objectives require explicit mapping. |
| [@wang2025mixllm] | Contextual routing among mixed LLMs under quality/cost/latency trade-offs. | Direct prior art for model routing; not evidence about human teams or general HLS. |
| [@saha2025systemone] | Learned fast/slow planning controller under a search budget. | Relevant to computation allocation; not an organizational heterogeneity study. |

## Bibliographic verification limits

Publisher/official proceedings pages were consulted for the Blackwell experiment-comparison entries, organizational coordination and learning, multi-skill scheduling, workforce learning/allocation, dynamic task allocation with training, mixed-LLM routing, and fast/slow planning. Other cited standard books and papers were cross-checked against DOI or publisher records where identifiers are given. No claim is made that this is an exhaustive systematic review. Older historical bibliography entries not carried into this core remain discoverable in the source branch and require individual verification before reuse.
