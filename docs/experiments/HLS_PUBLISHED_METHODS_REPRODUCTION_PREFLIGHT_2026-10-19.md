# HLS Published-Methods Reproduction Preflight

**Date:** 2026-10-19
**Scope:** bounded engineering preflight; no training, model download, or campaign was run.
**Decision:** **GO — with artifact and source-faithfulness gates.** This is not a claim that either method has been reproduced.

## 1. Executive decision

System-1.x has an official MIT-licensed implementation and included Maze/Blocksworld data, but the visible repository does not distribute trained checkpoints. The paper’s Maze result is therefore not inference-only reproducible from the checked-in artifacts: at least the source training recipe must be run, or the authors must provide compatible checkpoints. Its evaluation code also hard-codes CUDA, so local Apple Silicon execution requires a narrowly scoped device-portability adapter. The M2 Max is capable hardware in principle, but the published training setup is not verified on MPS.

For MixLLM, the paper is available from ACL and specifies the core algorithm and evaluation. A targeted search did not locate an official implementation of the *MixLLM routing paper*. The original RouterBench base data/code exist independently, but the paper additionally uses its own Llama 3.1 response/length extension, tag/domain processing, and routing pipeline. Until the paper-specific response tables/split and tag artifacts (or a source-faithful way to regenerate them) are obtained, the published numbers are not directly reproducible. Reconstructing the method from equations is possible as new implementation work, not a ready-made reproduction.

Accordingly:

- **A — MixLLM alone:** proceed to a bounded artifact/data gate, then a source-faithful replay if the inputs are released. Do not substitute `src/hls/contextual_router.py`.
- **B — System-1.x alone:** proceed with a Maze reproduction using author code/data, first resolving model checkpoints and the CUDA-only evaluator. Training is required unless author checkpoints can be obtained.
- **C — composition:** defer until both individual validations pass. The proposed 2×2 is an HLS composition/adaptation on shared maze tasks, not a reproduction of the original MixLLM RouterBench experiment. The two published decision mechanisms operate at different levels and are not interchangeable.

No HLS code, model, test, result, or experiment was changed or executed during this preflight. No large download was attempted.

## 2. MixLLM preflight

### Source and verified method

Wang et al., “MixLLM: Dynamic Routing in Mixed Large Language Models,” NAACL-HLT 2025, pp. 10912–10922, DOI [10.18653/v1/2025.naacl-long.545](https://doi.org/10.18653/v1/2025.naacl-long.545). The primary ACL PDF was inspected, especially §§3–4, equations (1)–(22), Figures 2–7, and Tables 1–3.

The algorithm routes each arriving query to one candidate LLM. It (i) creates tag-enhanced query embeddings using InsTag-generated tags, manually grouped into domains, and an unsupervised fine-tuned BERT encoder; (ii) predicts candidate-specific answer quality and response length/cost; (iii) scores candidates using quality-cost trade-off, an uncertainty bonus, and a waiting-time penalty, then selects the maximum score; and (iv) updates after selected-only feedback. The refined-feedback path trains the quality/length predictors; the binary path uses a shared three-layer MLP and policy-gradient update. This is not just a quality-threshold/minimum-cost rule.

**Inputs/outputs.** Input is a query stream, candidate model set, query features/tags, candidate-specific historical response outcomes, price/length information, and waiting-time state. Output is a selected model per query, with predicted score/quality/cost/uncertainty and subsequent selected-model feedback updates. The paper also evaluates an offline oracle using outcomes for every candidate; this is an evaluator upper bound, not a deployable router.

### Artifacts, requirements, and fidelity

| Requirement | Preflight finding |
|---|---|
| Official implementation | Not located in the ACL record, paper text, or targeted search for the paper-specific router. This is a bounded search finding, not proof that no private/unindexed code exists. Do not confuse Microsoft’s unrelated mixed-precision “MixLLM” repository with this paper. |
| Dataset | Paper §4.1 reports RouterBench: 36,497 queries from eight NLP datasets, responses and quality/cost for 11 models, extended with Llama 3.1 8B/70B, prompt/response lengths, and 80/20 train/test split. Public RouterBench artifacts are a potential input; availability and exact identity of the paper’s extended data, labels, tags, and split remain a blocker to matching its results. |
| Models | InsTag backed by Llama-2 13B is used to generate tags; BERT encoder is fine-tuned for embeddings. Candidate LLM inference can be avoided for a replay only if the exact per-query candidate-response/quality/length table is available. Otherwise models, model versions, evaluators, and price/latency metadata are needed. |
| Training | Offline refined feedback trains per-candidate quality/length prediction; online refined feedback updates selected-candidate predictors. Binary feedback uses a shared 3-layer MLP with policy-gradient updates. The paper reports RF for quality and candidate-dependent MLP/RF/KNN for response length. Exact source code, feature processing, artifact versions and every training detail are not packaged with the paper. |
| Published evaluation | §4 uses quality in [0,1], dollar cost, and a waiting-time constraint; late queries receive quality 0. It tests budgets via λ, uses a stream of 100 queries/10 s, τ=30 s, waiting-state update every 10 s, seed 42; most runs used Python 3.12, PyTorch 2.0, CUDA 12.1 / Ubuntu 18.04 and a 12GB Titan V. Llama dataset extension/tag extraction used two 80GB H100s. See paper §4.1, pp. 10916–10917. |
| Licensing/dependencies | The paper itself does not provide an implementation license or dependency lock. Reuse licenses for RouterBench, each model, InsTag, and any response data must be checked separately before use. No MixLLM requirements file was found. |
| Compute | Router predictor fitting/replay is lightweight relative to candidate LLM generation. Re-generating paper data and InsTag outputs is expensive and requires substantial GPU resources per the authors’ setup. CPU-only execution is credible for method replay on stored outcomes, not for regenerating all model outputs/tag annotations at paper scale. No runtime was measured here. |

### Smallest meaningful experiment

First target the paper’s §4.3, Table 1, 80:20 split only: compare offline-only, offline + refined selected feedback, and offline + binary selected feedback on the held-out query stream, holding candidate outcomes, query order, split, and cost regime fixed. Report mean response quality, total dollars, and late-query treatment exactly as specified. The reference values are 75.54%, 76.45% (+1.21% as tabulated), and 75.93% (+0.52%), respectively. These are paper-reported values, not HLS results. The source states online user satisfaction is simulated using quality >0.7 and waiting time <15 s (§4.3).

This bounded replay avoids downloading/running the candidate LLMs only if exact source response, quality, cost, length, tags/features, and split artifacts are available. If any are not available, one can implement and test the equations on a smaller or reconstructed dataset, but that is **approximate reproduction** and must not be presented as reproducing Table 1. No synthetic replacement is authorized by this preflight.

**Fidelity today:** full reproduction **blocked pending artifact/source details**; reduced-scale faithful replay **conditionally feasible** if source-identical inputs are supplied; algorithmic smoke test **feasible after implementation**, but is not reproduction; HLS contextual-router comparison is a distinct adaptation.

## 3. System-1.x preflight

### Official implementation and procedure

Saha et al., “System-1.x: Learning to Balance Fast and Slow Planning with Language Models,” ICLR 2025. The [official repository](https://github.com/swarnaHub/System-1.x) describes PyTorch code, includes Maze and Blocksworld datasets, and exposes training/evaluation scripts. The repository README says Python 3.9.16; pinned requirements are `datasets==2.16.0`, `numpy==1.24.2`, `peft==0.7.1`, `torch==2.1.0`, `transformers==4.42.4`, `trl==0.8.1` ([requirements](https://raw.githubusercontent.com/swarnaHub/System-1.x/main/requirements.txt)). Repository license is MIT.

The method learns a meta-planner that decomposes a plan into subgoals and assigns them to fast direct generation or slower explicit search; subplans are composed and evaluated. It is a learned planning/deliberation mechanism, not HLS staffing, N×K allocation, or learning-by-doing.

Official entry points include `src_maze/train.py` and `src_maze/test.py`; scripts under `scripts/maze/` include `train_sys1.sh`, `eval_sys1.sh`, `train_sys1.5_sg.sh`, and `eval_sys1.5_sg.sh`. Training defaults to `mistralai/Mistral-7B-Instruct-v0.2`, LoRA rank 8, max sequence length 5000, batch size 2, gradient accumulation 2, 3 epochs, and learning rate 5e-4 (`train.py`). The System-1.5 subgoal script uses one epoch and requires separate System-1 and System-2 models at evaluation. The README says data are included and each JSON record contains start/goal and System-1/System-2 traces. The task-level paper setup uses 3,200 training and 400 validation / 400 test examples per 4,000 generated 5×5 maze tasks (paper §3; see existing HLS assessment for the prior extracted configuration).

### Model availability and execution feasibility

The public repo has no GitHub release/checkpoint artifact visible; `models/` and `output/` are gitignored, and evaluation scripts point to locally trained directories. Therefore there is no verified author checkpoint for immediate inference-only reproduction. Inference-only is possible **only after** checkpoints are trained locally or obtained from the authors with matching provenance. The evaluation script explicitly sends tokenized inputs to `.to('cuda')`; source code therefore does not run unchanged on CPU/MPS. Training uses `device_map='auto'` and `paged_adamw_32bit`, which is not an established Apple-MPS path; any device/optimizer portability patch must be isolated, documented, and checked not to change training semantics.

The inspected machine is Apple M2 Max, 64 GiB unified memory, Metal 4. Local Python has PyTorch 2.4.1 with MPS available, but does not have `peft`, `trl`, `datasets`, or `mlx`; the official environment is pinned to a different Python/PyTorch stack. No Mistral checkpoint was found in the local Hugging Face cache or HLS model/checkpoint directories. Thus no local smoke execution was possible without environment installation/model download, neither of which was attempted. CPU-only inference is conceptually possible but likely impractical at 7B and is not the tested path. Apple MPS is a plausible bounded engineering target for inference after a device adapter, but not yet validated for the training recipe. External CUDA GPU is the lowest-risk path to reproduce the authors’ scripts; their cited high-end H100 setup was for Llama data extension in MixLLM, not a System-1.x hardware requirement. Do not transfer that requirement across papers.

### Smallest meaningful experiment

Use Maze task-level evaluation and the paper’s published train/validation/test split and System-1, System-2, and System-1.x/System-1.5 conditions. Train the source models using the official scripts/parameters (and source-generated instances), then evaluate on the 400 held-out tasks with plan validity as primary metric and optimality/search states as reported diagnostics. The paper’s Table 3 / Appendix E reports, among its configurations, System-1.5 with subgoal decomposition at 70.4% valid plans and 13.6 states visited, System-1 at 48.7% and 3.1, and System-2 at 93.7% and 24.4; controlled test-time System-1.5 reports 96.7% and 27.3. These correspond to distinct conditions, so the reproduction must use the exact paper table row/configuration, not combine values across settings.

**Fidelity today:** full paper reproduction **not ready**; a source-faithful Maze reproduction is feasible after obtaining/training checkpoints and pinning repository/data versions. Reduced-scale faithful reproduction can use a declared subset of the official train/test split and unchanged model/policy; it validates function but cannot claim the published aggregate. A trivial import or one-example run is only a smoke test.

## 4. Computational and engineering assessment

| Work | Minimum engineering | Cost / blockers | Evidence level |
|---|---|---|---|
| MixLLM replay | Isolated paper-faithful router module, source-schema dataset adapter, exact feature/predictor/score/update implementation, table-metric evaluator, provenance manifest. Do not change HLS router. | **High** because implementation/data lineage are missing; stored outcomes could keep compute low. Main blocker is complete source-specific data/tags/split and ambiguous implementation details, not simulator capacity. CPU is suitable for small predictor fitting/replay; GPU is needed only to regenerate heavy model/tag data. | Could reach reduced-scale faithful replay if source inputs are released; otherwise conceptual adaptation only. |
| System-1.x Maze | Isolated wrapper around pinned upstream source, environment/data manifest, checkpoint training/evaluation commands, device-selection patch only if local MPS/CPU is chosen, result parser. Keep upstream algorithm intact. | **Medium** with external CUDA and official data/scripts; **High** for M2-only due device/optimizer compatibility and 7B LoRA training uncertainty. Model downloads and training are deliberately not attempted. | Faithful training/evaluation possible after dependencies and checkpoints; inference-only requires matching checkpoint artifact. |
| Composition | Frozen shared Maze queries and output contract; candidate-level wrapper; evaluate all four cells with independent artifacts; record quality and each resource measure separately. | **High / conditional**. No common original benchmark: MixLLM was designed/evaluated on LLM query-response/RouterBench, System-1.x on planning tasks. Reusing its decision semantics on Maze requires refitting MixLLM to Maze-derived expert outcomes and thus is an HLS adaptation. Matched “budget” needs an explicitly common meter; dollars, wall-clock, generated tokens and search states cannot be equated by assertion. | HLS interaction experiment, not a reproduction of the two papers jointly. |

Effort labels are relative engineering judgments, not calendar or runtime predictions. The next milestone should deliver working methods and measured, saved results; no additional broad review is needed.

## 5. Compatibility and proposed experiments

### Common task and outcomes

For A and B, preserve each original task distribution and evaluation separately. They do not share task representation: MixLLM receives NLP queries with response-level quality/cost/latency data; System-1.x receives maze start/goal states and returns plans evaluated for validity/optimality/search. HLS abstractions may carry opaque task IDs, context, selected candidate, outcome feedback, and method-specific resource diagnostics, but must not translate query quality into plan competence or search states into monetary cost.

For C, use a frozen Maze split and fixed candidate outputs/configurations. An outer selection adapter can select among complete planning systems, while System-1.x may internally route subgoals. The outer method must be identified as **MixLLM-inspired HLS adaptation**, unless its original training/feature/outcome assumptions can be honored exactly. The same tasks, held-out partition, candidate pool, evaluators, and predeclared computational budget must apply to all cells. Only outcomes of actually executed candidates may be made available online; all-candidate outputs may be used for offline training only if the original protocol permits and must be flagged as such.

### Required 2×2 interaction pilot

| Expert selection | Fixed deliberation | Adaptive deliberation |
|---|---|---|
| Static selection | Select one complete solver on training/validation data, then lock it; execute its fixed deliberation configuration on every held-out task. | Lock the expert/model family before testing; use the trained System-1.x policy to allocate subgoals between fast and slow planning. |
| Adaptive selection | Use a contextual router fitted on training data and selected-task feedback to choose among the frozen fixed-deliberation solver candidates. | Use the same adaptive outer selector over frozen solver candidates whose deliberation is handled by System-1.x; preserve each method internally. |

The selection factor’s static choice is made without test outcomes. “Fixed deliberation” means a source-defined fixed System-1-only or System-2-only planner selected on validation data, not an arbitrary weaker budget. “Adaptive deliberation” is the source System-1.x controller/checkpoint, not a newly invented policy. The four cells are executable only if all candidates can produce the same plan interface and the shared resource budget is made operational. Since outer query routing and inner subgoal routing can overlap, report the factorial interaction as a descriptive interaction of these *composed systems*, not an isolated causal effect of abstract mechanisms. Use held-out paired task-level differences and a two-factor model (selection, deliberation, interaction); retain plan validity, optimality, search states, wall time, and any actual monetary cost as separate outcomes.

This composition does not reproduce original MixLLM: it transfers its routing logic to a maze-query setting and requires new training labels/features. Likewise, it does not modify System-1.x; its internal policy remains the authors’ trained method. If no common resource meter can be defined without changing either method, compare quality-resource Pareto profiles rather than forcing a single matched scalar budget.

## 6. Minimal execution sequence and stop gates

1. **Artifact lock (first executable milestone):** obtain exact MixLLM response/quality/cost/length/tag/split artifacts or document the missing subset; pin System-1.x full commit SHA, data hashes, environment, base model revision, and trained checkpoint hashes. This is an engineering gate, not another literature review.
2. **System-1.x bounded Maze run:** set up isolated environment; train/retrieve source-required checkpoints; resolve CUDA versus MPS device path; run a small official held-out slice as smoke, then the paper’s 400-task evaluation only after exact configuration validation. Save raw per-task output and metrics.
3. **MixLLM Table 1 replay:** implement equations and selected-feedback sequence independently of HLS contextual router; run the 80:20 Table-1 protocol only when source artifacts and licenses are confirmed. If unavailable, stop calling it reproduction; seek author artifacts rather than silently replacing them.
4. **Interaction pilot C:** only after A and B pass their individual fidelity checks, freeze Maze candidates and train/validation/test separation, then run all four paired cells with predeclared resource measures. This is explicitly an HLS adaptation and may show positive, zero, or negative interaction.

**Stop conditions:** no MixLLM Table 1 claim without matching paper inputs and data split; no System-1.x reproduction claim without pinned author source, matching training/evaluation configuration, and model/checkpoint provenance; no joint-mechanism causal claim if the 2×2 factor definitions or compute budget alter either source algorithm. Smoke tests never satisfy these gates.

## 7. HLS integration boundary

Reusable HLS infrastructure includes the common run/trace envelope, selected-feedback patterns, deterministic task manifests/replay, and independent method records. The current [contextual-router implementation](../engineering/HLS_MIXLLM_ROUTER_IMPLEMENTATION.md) is not a MixLLM implementation and must remain unchanged. Campaign 3 FAST/DEEP/META is not System-1.x. Add isolated wrappers only; do not generalize N×K action types or modify MIS-v2, Nembhard, G0/RQ0, P0/P1/P2, or existing scientific result contracts.

## 8. Preflight decision

**GO — bounded engineering validation, gated by artifacts.** System-1.x has an actionable official route through its data, scripts, and source training, though not immediate inference-only execution. MixLLM can be implemented from the paper and potentially evaluated from stored benchmark responses, but the exact extended data and paper-specific pipeline artifacts must first be verified. The interaction pilot is valuable as an explicit composition study but is an HLS adaptation, not a joint reproduction. No method should be changed to manufacture agreement, and no policy is presumed to win.

### Local checks performed

- Verified current branch is `feature/hls-laboratory-v1` and origin tracking is present. Numerous unrelated pre-existing tracked and untracked changes exist; none were modified for this report.
- Read the official MixLLM ACL paper and System-1.x repository README, pinned requirements, training/evaluation scripts, evaluator and license through their public primary-source URLs.
- Read-only machine check: Apple M2 Max, 64 GiB unified memory, Metal 4; Python 3.11.9, PyTorch 2.4.1, MPS available, CUDA unavailable; `peft`, `trl`, `datasets`, and `mlx` absent. No local Mistral checkpoint found. No installs, model/data downloads, smoke execution, or campaigns were run.

## References

- Wang, X. et al. (2025). “MixLLM: Dynamic Routing in Mixed Large Language Models.” NAACL-HLT 2025, pp. 10912–10922. [ACL Anthology paper](https://aclanthology.org/2025.naacl-long.545/); [PDF](https://aclanthology.org/2025.naacl-long.545.pdf); [DOI](https://doi.org/10.18653/v1/2025.naacl-long.545).
- Saha, S. et al. (2025). “System-1.x: Learning to Balance Fast and Slow Planning with Language Models.” ICLR 2025. [Proceedings paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/605e59e78284907aa4fce5280838def3-Paper-Conference.pdf); [official source/data repository](https://github.com/swarnaHub/System-1.x); [requirements](https://raw.githubusercontent.com/swarnaHub/System-1.x/main/requirements.txt); [Maze training](https://raw.githubusercontent.com/swarnaHub/System-1.x/main/src_maze/train.py); [Maze evaluation](https://raw.githubusercontent.com/swarnaHub/System-1.x/main/src_maze/test.py); [repository license](https://raw.githubusercontent.com/swarnaHub/System-1.x/main/LICENSE).
- Hu, Q. J. et al. (2024). “RouterBench: A Benchmark for Multi-LLM Routing System.” [Paper and metadata](https://arxiv.org/abs/2403.12031); [official benchmark code](https://github.com/withmartian/routerbench). This is a data/benchmark resource, not an official MixLLM implementation.
- Existing HLS decision record: [HLS Laboratory Capability Assessment and Published-Method Selection](../research/HLS_LABORATORY_CAPABILITY_ASSESSMENT_2026-10-19.md).
