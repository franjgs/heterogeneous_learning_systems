"""Protocol-faithful preparation, execution, and analysis for Nembhard E1.

Importing this module never runs an episode. Full campaign execution requires
an explicit CLI command and a confirmation token.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass, replace
from itertools import permutations
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable, Mapping, Sequence

from .experiment_contract import MetricValue, RunAdapterContext, SeedRecord, adapt_nembhard_run
from .hls_lab_nk_execution import NKNembhardDirectRunResult, run_nk_production_sequence
from .hls_lab_nk_geometry import (
    OrganizationConfigNK, ProblemSpecNK, ProductiveAllocationNK,
    validate_productive_allocation_nk,
)
from .hls_lab_nk_nembhard import (
    NembhardDirectExecutionNK, NembhardDirectProfileNK,
    NembhardDirectStateNK, NembhardOutputUnitContract,
)
from .hls_lab_nk_nembhard_adaptive import NembhardAdaptiveRouterConfigNK

MASTER_SEED = 20261017
HORIZON = 120
MAX_CANDIDATES = 64
RESULTS_DIRECTORY = Path("results/experiments/hls_nembhard_adaptive_allocation")
CONFIRM_ALL_TOKEN = "HLS-EXECUTE-1016"
MECHANISM_ID = "nembhard_direct"
UNIT_CONTRACT = NembhardOutputUnitContract(
    "effort-unit/period", "period", "work-exposure-unit",
    "task-output-unit", "task-output-unit",
)
ROLE_IDS = ("skill1_role", "skill2_role", "generalist_role")
PROFILE_K: Mapping[str, tuple[tuple[float, ...], ...]] = {
    "homogeneous": ((1.2, 1.2), (1.2, 1.2), (1.2, 1.2)),
    "mixed": ((1.8, 0.6), (0.6, 1.8), (1.2, 1.2)),
    "specialists": ((2.2, 0.0), (0.0, 2.2), (1.4, 1.4)),
}
LEARNING_SCALES = {"fast": 1.0, "slow": 4.0}
PROBLEM_CATALOGUE = {
    "skill1": ((1.4, 0.0), 2.0),
    "skill2": ((0.0, 1.4), 2.0),
    "joint": ((0.7, 0.7), 2.0),
}
ARMS = ("fixed", "oracle", "adaptive_sigma_0", "adaptive_sigma_005")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _problem_record(problem: ProblemSpecNK) -> dict[str, Any]:
    return {
        "problem_id": problem.problem_id,
        "requirements": list(problem.requirements),
        "resource_budget": problem.resource_budget,
        "ces_weights": list(problem.ces_weights or ()),
    }


def _sha(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def ordered_demand_hash(problems: Sequence[ProblemSpecNK]) -> str:
    """Hash protocol-canonical JSON for the ordered problem sequence."""
    return _sha([_problem_record(problem) for problem in problems])


def demand_multiset_hash(problems: Sequence[ProblemSpecNK]) -> str:
    """Hash canonical records in sorted order, retaining repeated counts."""
    rows = [_problem_record(problem) for problem in problems]
    rows.sort(key=canonical_json)
    return _sha(rows)


def _problem(problem_id: str) -> ProblemSpecNK:
    requirements, budget = PROBLEM_CATALOGUE[problem_id]
    return ProblemSpecNK(problem_id, requirements, budget, (0.5, 0.5))


def _valid_block_orders() -> tuple[tuple[str, ...], ...]:
    values = set(permutations(("skill1", "skill1", "skill2", "skill2", "joint", "joint")))
    return tuple(sorted(order for order in values
                        if all(order[i] != order[i + 1] for i in range(len(order) - 1))))


@dataclass(frozen=True)
class DemandSequence:
    order: str
    seed: int
    problems: tuple[ProblemSpecNK, ...]
    ordered_hash: str
    multiset_hash: str
    maximum_run: int


def build_demand_sequence(order: str, seed: int) -> DemandSequence:
    if order not in {"interleaved", "clustered"}:
        raise ValueError("order must be interleaved or clustered")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)
    if order == "interleaved":
        problem_ids: list[str] = []
        for _ in range(40):
            triple = ["skill1", "skill2", "joint"]
            rng.shuffle(triple)
            problem_ids.extend(triple)
    else:
        valid_orders = _valid_block_orders()
        block_order = valid_orders[rng.randrange(len(valid_orders))]
        problem_ids = [problem_id for problem_id in block_order for _ in range(20)]
    problems = tuple(_problem(problem_id) for problem_id in problem_ids)
    counts = {name: problem_ids.count(name) for name in PROBLEM_CATALOGUE}
    if len(problems) != HORIZON or counts != {name: 40 for name in PROBLEM_CATALOGUE}:
        raise AssertionError("demand builder violated the 40/40/40 design")
    runs: list[int] = []
    previous = None
    for problem_id in problem_ids:
        if problem_id == previous:
            runs[-1] += 1
        else:
            runs.append(1)
            previous = problem_id
    maximum_run = max(runs)
    if order == "interleaved" and maximum_run > 2:
        raise AssertionError("interleaved sequence violates maximum run length 2")
    return DemandSequence(order, seed, problems, ordered_demand_hash(problems),
                          demand_multiset_hash(problems), maximum_run)


@dataclass(frozen=True)
class SeedBundle:
    replicate: int
    interleaved_demand: int
    clustered_demand: int
    observations: int
    exploration: int


def seed_bundle(replicate: int) -> SeedBundle:
    if not isinstance(replicate, int) or isinstance(replicate, bool) or not 0 <= replicate < 20:
        raise ValueError("replicate must be an integer in 0..19")
    base = MASTER_SEED + 10000 * replicate
    return SeedBundle(replicate, base + 1, base + 2, base + 3, base + 4)


def _profile(profile_id: str, learning_id: str,
             permutation: tuple[int, ...]) -> NembhardDirectProfileNK:
    if profile_id not in PROFILE_K or learning_id not in LEARNING_SCALES:
        raise ValueError("unknown profile or learning scale")
    k = tuple(PROFILE_K[profile_id][i] for i in permutation)
    scale = LEARNING_SCALES[learning_id]
    p = tuple((scale, scale) for _ in range(3))
    return NembhardDirectProfileNK(k, p, p)


def _role_ids(permutation: tuple[int, ...]) -> tuple[str, ...]:
    return tuple(ROLE_IDS[index] for index in permutation)


@dataclass(frozen=True)
class EpisodeConfig:
    episode_id: str
    profile_id: str
    learning_scale_id: str
    demand_order: str
    arm: str
    replicate: int
    permutation: tuple[int, ...]
    agent_ids: tuple[str, ...]
    sequence_seed: int
    sequence_id: str
    multiset_id: str
    observation_seed: int
    exploration_seed: int
    epsilon: float | None
    observation_noise_stddev: float | None
    initial_estimate: float | None
    horizon: int = HORIZON
    duration: float = 1.0
    effort_limits: tuple[float, ...] = (1.0, 1.0, 1.0)
    collective_budget: float = 2.0
    max_candidates: int = MAX_CANDIDATES
    design_component: str = "primary"

    def semantic_identity(self) -> str:
        data = asdict(self)
        data.pop("episode_id")
        data.pop("design_component")
        return _sha(data)


@dataclass(frozen=True)
class DesignRegistry:
    episodes: tuple[EpisodeConfig, ...]
    diagnostic_aliases: Mapping[str, str]
    nominal_diagnostic_count: int
    duplicate_diagnostic_count: int


def _episode(profile_id: str, learning_id: str, order: str, arm: str,
             replicate: int, permutation: tuple[int, ...],
             component: str) -> EpisodeConfig:
    bundle = seed_bundle(replicate)
    sequence_seed = bundle.interleaved_demand if order == "interleaved" else bundle.clustered_demand
    sequence = build_demand_sequence(order, sequence_seed)
    epsilon = noise = initial = None
    if arm.startswith("adaptive"):
        epsilon = 0.05 if component != "epsilon_zero" else 0.0
        noise = 0.05 if arm == "adaptive_sigma_005" else 0.0
        initial = 0.6
    candidate = EpisodeConfig(
        "pending", profile_id, learning_id, order, arm, replicate, permutation,
        _role_ids(permutation), sequence_seed, sequence.ordered_hash,
        sequence.multiset_hash, bundle.observations, bundle.exploration,
        epsilon, noise, initial, design_component=component,
    )
    return replace(candidate, episode_id=f"nembhard-e1-{candidate.semantic_identity()[:20]}")


def build_design_registry() -> DesignRegistry:
    """Construct the 1,016 unique run configurations, without executing."""
    unique: dict[str, EpisodeConfig] = {}
    aliases: dict[str, str] = {}
    for profile in PROFILE_K:
        for learning in LEARNING_SCALES:
            for order in ("interleaved", "clustered"):
                for replicate in range(20):
                    for arm in ARMS:
                        config = _episode(profile, learning, order, arm, replicate,
                                          (0, 1, 2), "primary")
                        unique.setdefault(config.semantic_identity(), config)
    if len(unique) != 960:
        raise AssertionError(f"expected 960 primary runs, got {len(unique)}")
    for replicate in range(20):
        for arm in ("adaptive_sigma_0", "adaptive_sigma_005"):
            config = _episode("mixed", "fast", "clustered", arm, replicate,
                              (0, 1, 2), "epsilon_zero")
            unique.setdefault(config.semantic_identity(), config)
    if len(unique) != 1000:
        raise AssertionError(f"expected 1,000 runs after epsilon slice, got {len(unique)}")
    nominal = duplicates = 0
    for permutation in permutations(range(3)):
        for arm in ("fixed", "oracle", "adaptive_sigma_0"):
            nominal += 1
            config = _episode("mixed", "fast", "interleaved", arm, 0,
                              permutation, "permutation_diagnostic")
            if arm == "adaptive_sigma_0":
                config = replace(config, epsilon=0.0)
                config = replace(config,
                                 episode_id=f"nembhard-e1-{config.semantic_identity()[:20]}")
            key = config.semantic_identity()
            if permutation == (0, 1, 2) and arm in {"fixed", "oracle"}:
                existing = unique.get(key)
                if existing is None:
                    raise AssertionError("expected diagnostic identity cell in primary matrix")
                aliases[f"permutation_identity_{arm}"] = existing.episode_id
                duplicates += 1
            else:
                unique.setdefault(key, config)
    if (nominal, duplicates, len(unique)) != (18, 2, 1016):
        raise AssertionError("protocol count reconciliation failed")
    episodes = tuple(sorted(unique.values(), key=lambda item: item.episode_id))
    if len({item.episode_id for item in episodes}) != 1016:
        raise AssertionError("run identifiers are not unique")
    return DesignRegistry(episodes, aliases, nominal, duplicates)


def list_configurations(registry: DesignRegistry | None = None) -> tuple[EpisodeConfig, ...]:
    return (registry or build_design_registry()).episodes


def validate_configuration(config: EpisodeConfig) -> None:
    if config.profile_id not in PROFILE_K or config.learning_scale_id not in LEARNING_SCALES:
        raise ValueError("unknown profile or learning scale")
    if config.demand_order not in {"interleaved", "clustered"} or config.arm not in ARMS:
        raise ValueError("unknown order or arm")
    if config.design_component not in {"primary", "epsilon_zero", "permutation_diagnostic"}:
        raise ValueError("unknown design component")
    if (len(config.permutation) != 3
            or any(not isinstance(value, int) or isinstance(value, bool)
                   for value in config.permutation)
            or tuple(sorted(config.permutation)) != (0, 1, 2)):
        raise ValueError("agent row permutation must contain indices 0, 1, 2 exactly once")
    bundle = seed_bundle(config.replicate)
    expected_sequence_seed = (bundle.interleaved_demand if config.demand_order == "interleaved"
                              else bundle.clustered_demand)
    if (config.sequence_seed != expected_sequence_seed
            or config.observation_seed != bundle.observations
            or config.exploration_seed != bundle.exploration):
        raise ValueError("seed values do not match the protocol seed bundle")
    sequence = build_demand_sequence(config.demand_order, config.sequence_seed)
    if (sequence.ordered_hash, sequence.multiset_hash) != (config.sequence_id, config.multiset_id):
        raise ValueError("demand identifiers do not match generated sequence")
    if config.horizon != HORIZON or config.duration != 1.0:
        raise ValueError("protocol requires horizon 120 and duration 1")
    if config.agent_ids != _role_ids(config.permutation):
        raise ValueError("role identifiers must be permuted with profile rows")
    if config.design_component == "primary" and config.permutation != (0, 1, 2):
        raise ValueError("primary matrix requires identity agent ordering")
    if config.design_component == "epsilon_zero" and (
            config.profile_id, config.learning_scale_id, config.demand_order) != (
                "mixed", "fast", "clustered"):
        raise ValueError("epsilon sensitivity must use mixed/fast/clustered")
    if config.design_component == "epsilon_zero" and not config.arm.startswith("adaptive"):
        raise ValueError("epsilon-zero sensitivity applies only to ADAPTIVE")
    if config.design_component == "permutation_diagnostic" and (
            config.profile_id, config.learning_scale_id, config.demand_order, config.replicate) != (
                "mixed", "fast", "interleaved", 0):
        raise ValueError("permutation diagnostic must use the declared seed bundle")
    if config.design_component == "permutation_diagnostic" and config.arm not in {
            "fixed", "oracle", "adaptive_sigma_0"}:
        raise ValueError("permutation diagnostic has an unsupported arm")
    if config.arm.startswith("adaptive"):
        expected_noise = 0.05 if config.arm == "adaptive_sigma_005" else 0.0
        expected_epsilon = 0.0 if config.design_component in {
            "epsilon_zero", "permutation_diagnostic"} else 0.05
        if (config.initial_estimate != 0.6 or config.observation_noise_stddev != expected_noise
                or config.epsilon != expected_epsilon):
            raise ValueError("adaptive parameters differ from the protocol")
    elif any(value is not None for value in
             (config.epsilon, config.observation_noise_stddev, config.initial_estimate)):
        raise ValueError("non-adaptive arm cannot contain adaptive parameters")
    profile = _profile(config.profile_id, config.learning_scale_id, config.permutation)
    if any(not math.isclose(sum(row[k] for row in profile.asymptotic_productivity), 3.6)
           for k in range(2)):
        raise ValueError("per-skill aggregate productivity differs from protocol")
    if config.effort_limits != (1.0, 1.0, 1.0) or config.collective_budget != 2.0:
        raise ValueError("resource constraints differ from the protocol")
    if config.max_candidates < MAX_CANDIDATES:
        raise ValueError("candidate catalogue must not be truncated below 64")
    if config.episode_id != f"nembhard-e1-{config.semantic_identity()[:20]}":
        raise ValueError("episode ID does not match semantic configuration identity")


def validate_design(registry: DesignRegistry | None = None) -> dict[str, Any]:
    """Validate counts, condition matching, demand identity, and FIXED feasibility."""
    registry = registry or build_design_registry()
    if len(registry.episodes) != 1016:
        raise ValueError("unique design must contain exactly 1,016 episodes")
    components = Counter(config.design_component for config in registry.episodes)
    if components != {"primary": 960, "epsilon_zero": 40,
                      "permutation_diagnostic": 16}:
        raise ValueError("design components do not match the approved protocol counts")
    primary_arms = Counter(config.arm for config in registry.episodes
                           if config.design_component == "primary")
    if primary_arms != {arm: 240 for arm in ARMS}:
        raise ValueError("primary arm counts do not match the factorial")
    epsilon_arms = Counter(config.arm for config in registry.episodes
                           if config.design_component == "epsilon_zero")
    if epsilon_arms != {"adaptive_sigma_0": 20, "adaptive_sigma_005": 20}:
        raise ValueError("epsilon-zero sensitivity needs 20 runs per noise level")
    diagnostic_permutations = {config.permutation for config in registry.episodes
                                if config.design_component == "permutation_diagnostic"}
    if diagnostic_permutations != set(permutations(range(3))):
        raise ValueError("permutation diagnostic does not include all six row orders")
    if (registry.nominal_diagnostic_count != 18
            or registry.duplicate_diagnostic_count != 2
            or len(registry.diagnostic_aliases) != 2):
        raise ValueError("permutation identity aliases do not match protocol de-duplication")
    for config in registry.episodes:
        validate_configuration(config)
    sequences: dict[tuple[str, int], set[str]] = {}
    multisets: dict[int, set[str]] = {}
    for config in registry.episodes:
        if config.design_component == "primary":
            sequences.setdefault((config.demand_order, config.replicate), set()).add(config.sequence_id)
            multisets.setdefault(config.replicate, set()).add(config.multiset_id)
        if config.arm == "fixed":
            sequence = build_demand_sequence(config.demand_order, config.sequence_seed)
            organization = OrganizationConfigNK(
                config.agent_ids, ("skill1", "skill2"), ((0.0, 0.0),) * 3,
                config.effort_limits, config.collective_budget,
            )
            for problem in sequence.problems:
                if not validate_productive_allocation_nk(
                        _fixed_allocation(problem, config.agent_ids), organization, problem):
                    raise ValueError(f"FIXED infeasible for {config.episode_id}/{problem.problem_id}")
    if any(len(ids) != 1 for ids in sequences.values()):
        raise ValueError("policy/profile conditions do not share frozen ordered demand")
    if any(len(ids) != 1 for ids in multisets.values()):
        raise ValueError("interleaved and clustered demand do not share a problem multiset")
    for replicate in range(20):
        interleaved = next(config.sequence_id for config in registry.episodes
                           if config.design_component == "primary" and config.profile_id == "mixed"
                           and config.learning_scale_id == "fast" and config.replicate == replicate
                           and config.demand_order == "interleaved" and config.arm == "fixed")
        clustered = next(config.sequence_id for config in registry.episodes
                         if config.design_component == "primary" and config.profile_id == "mixed"
                         and config.learning_scale_id == "fast" and config.replicate == replicate
                         and config.demand_order == "clustered" and config.arm == "fixed")
        if interleaved == clustered:
            raise ValueError("interleaved and clustered ordered demand hashes unexpectedly match")
    return {"unique_episodes": len(registry.episodes), "primary_episodes": components["primary"],
            "epsilon_zero_episodes": components["epsilon_zero"],
            "permutation_diagnostic_nominal": registry.nominal_diagnostic_count,
            "permutation_duplicates_reused": registry.duplicate_diagnostic_count,
            "permutation_diagnostic_unique": components["permutation_diagnostic"],
            "demand_seed_bundles": 20, "episodes_executed": 0}


def _fixed_allocation(problem: ProblemSpecNK,
                      agent_ids: tuple[str, ...]) -> ProductiveAllocationNK:
    """Static task-type/role map; no state, outcome, or future-task input."""
    mapping = {
        "skill1": {"skill1_role": (1.0, 0.0), "skill2_role": (0.0, 0.0),
                   "generalist_role": (1.0, 0.0)},
        "skill2": {"skill1_role": (0.0, 0.0), "skill2_role": (0.0, 1.0),
                   "generalist_role": (0.0, 1.0)},
        "joint": {"skill1_role": (1.0, 0.0), "skill2_role": (0.0, 1.0),
                  "generalist_role": (0.0, 0.0)},
    }
    if problem.problem_id not in mapping:
        raise ValueError(f"unsupported protocol problem {problem.problem_id!r}")
    return tuple(mapping[problem.problem_id][agent_id] for agent_id in agent_ids)


def _run_configuration(
    config: EpisodeConfig,
    *,
    problems_override: Sequence[ProblemSpecNK] | None = None,
) -> tuple[NKNembhardDirectRunResult, tuple[ProblemSpecNK, ...]]:
    validate_configuration(config)
    sequence = build_demand_sequence(config.demand_order, config.sequence_seed)
    problems = sequence.problems if problems_override is None else tuple(problems_override)
    if not problems or any(len(problem.requirements) != 2 for problem in problems):
        raise ValueError("execution problem sequence must be non-empty and K=2")
    profile = _profile(config.profile_id, config.learning_scale_id, config.permutation)
    organization = OrganizationConfigNK(
        config.agent_ids, ("skill1", "skill2"), ((0.0, 0.0),) * 3,
        config.effort_limits, config.collective_budget,
    )
    router_id = None
    adaptive_config = None
    allocations: tuple[ProductiveAllocationNK, ...] = ()
    if config.arm == "fixed":
        allocations = tuple(_fixed_allocation(problem, config.agent_ids) for problem in problems)
        if not all(validate_productive_allocation_nk(action, organization, problem)
                   for action, problem in zip(allocations, problems)):
            raise ValueError("protocol FIXED allocation violates a resource constraint")
    elif config.arm == "oracle":
        router_id = "nembhard_oracle"
    else:
        router_id = "nembhard_adaptive"
        adaptive_config = NembhardAdaptiveRouterConfigNK(
            epsilon=float(config.epsilon), exploration_seed=config.exploration_seed,
            observation_noise_stddev=float(config.observation_noise_stddev),
            observation_seed=config.observation_seed,
            initial_productivity_estimate=float(config.initial_estimate),
        )
    execution = NembhardDirectExecutionNK(
        profile, allocations, UNIT_CONTRACT, NembhardDirectStateNK.zeros(3, 2),
        config.duration,
    )
    result = run_nk_production_sequence(
        organization, problems, max_candidates=config.max_candidates,
        mechanism_id=MECHANISM_ID, nembhard_execution=execution,
        router_id=router_id, adaptive_router_config=adaptive_config,
    )
    if not isinstance(result, NKNembhardDirectRunResult):
        raise TypeError("runner returned a non-Nembhard result")
    return result, problems


def _campaign_metrics(result: NKNembhardDirectRunResult) -> dict[str, Any]:
    records = result.records
    task_output = sum(record.outputs[k] for record in records
                      for k, requirement in enumerate(record.requirements) if requirement > 0)
    success_count = sum(record.functional_result.success for record in records)
    deficit = sum(record.functional_result.normalized_deficit for record in records)
    metrics = [
        {"name": "cumulative_task_relevant_production", "value": task_output,
         "unit": result.output_unit, "aggregation": "sum over required skills and periods",
         "interpretation": "Output only on dimensions with positive current requirement."},
        {"name": "functional_success_proportion", "value": success_count / len(records),
         "unit": "fraction", "aggregation": "successful periods / periods",
         "interpretation": "Fraction of periods meeting all active requirements."},
        {"name": "cumulative_normalized_deficit", "value": deficit,
         "unit": "dimensionless", "aggregation": "sum over periods",
         "interpretation": "Sum of normalized active-dimension shortfalls."},
        {"name": "productive_effort_total",
         "value": sum(record.productive_effort_used for record in records),
         "unit": result.effort_intensity_unit, "aggregation": "sum of period effort",
         "interpretation": "Effort resource consumption, not monetary cost."},
        {"name": "effective_work_exposure_total",
         "value": sum(record.effective_work_used for record in records),
         "unit": result.exposure_unit, "aggregation": "sum of exposure",
         "interpretation": "Experience exposure, kept distinct from effort."},
    ]
    by_problem: dict[str, Any] = {}
    for problem_id in PROBLEM_CATALOGUE:
        selected = [record for record in records if record.problem_id == problem_id]
        by_problem[problem_id] = ({
            "periods": len(selected),
            "success_proportion": sum(r.functional_result.success for r in selected) / len(selected),
            "cumulative_normalized_deficit": sum(r.functional_result.normalized_deficit for r in selected),
            "output_by_skill": [sum(r.outputs[k] for r in selected) for k in range(2)],
        } if selected else {
            "periods": 0, "success_proportion": None,
            "cumulative_normalized_deficit": None, "output_by_skill": None,
        })
    role_totals = [sum(record.individual_effort_used[i] for record in records)
                   for i in range(len(result.agent_ids))]
    allocation_by_problem: dict[str, Any] = {}
    for problem_id in PROBLEM_CATALOGUE:
        selected = [record for record in records if record.problem_id == problem_id]
        group_effort = sum(r.productive_effort_used for r in selected)
        allocation_by_problem[problem_id] = {
            "agent_effort_totals": [sum(r.individual_effort_used[i] for r in selected)
                                     for i in range(len(result.agent_ids))],
            "agent_effort_shares": [
                sum(r.individual_effort_used[i] for r in selected)
                / group_effort if group_effort > 0 else 0.0
                for i in range(len(result.agent_ids))],
            "agent_skill_effort_totals": [
                [sum(r.allocation[i][k] for r in selected) for k in range(2)]
                for i in range(len(result.agent_ids))],
            "agent_skill_effort_shares": [
                [sum(r.allocation[i][k] for r in selected)
                 / sum(r.allocation[j][k] for r in selected for j in range(len(result.agent_ids)))
                 if sum(r.allocation[j][k] for r in selected for j in range(len(result.agent_ids))) > 0
                 else 0.0
                 for k in range(len(result.skill_ids))]
                for i in range(len(result.agent_ids))],
        }
    for index, role in enumerate(result.agent_ids):
        metrics.append({"name": f"effort_total_by_agent[{role}]", "value": role_totals[index],
                        "unit": result.effort_intensity_unit, "aggregation": "sum over periods",
                        "interpretation": "Agent-level effort; not monetary cost."})
    if result.router_id == "nembhard_adaptive":
        exploratory = [record.router_exploratory for record in records
                       if record.router_exploratory is not None]
        metrics.append({"name": "exploratory_decision_proportion",
                        "value": sum(bool(value) for value in exploratory) / len(exploratory),
                        "unit": "fraction", "aggregation": "exploratory decisions / periods",
                        "interpretation": "Observed epsilon-greedy exploration frequency."})
    prediction_errors: list[dict[str, Any]] = []
    for skill in range(2):
        errors = [record.outputs[skill] - record.router_predicted_outputs[skill]
                  for record in records if record.router_predicted_outputs is not None]
        if errors:
            label = "adaptive" if result.router_id == "nembhard_adaptive" else "oracle"
            prediction_errors.append({"skill_index": skill, "signed_mean": mean(errors),
                                      "absolute_mean": mean(abs(value) for value in errors),
                                      "unit": result.output_unit})
            metrics.extend((
                {"name": f"{label}_prediction_error_mean[skill{skill + 1}]",
                 "value": mean(errors), "unit": result.output_unit,
                 "aggregation": "mean observed minus predicted skill output",
                 "interpretation": "Signed current-period output prediction error."},
                {"name": f"{label}_prediction_absolute_error_mean[skill{skill + 1}]",
                 "value": mean(abs(value) for value in errors), "unit": result.output_unit,
                 "aggregation": "mean absolute skill-output error",
                 "interpretation": "Absolute current-period output prediction error."},
            ))
    period_metrics = []
    for record in records:
        active = [k for k, requirement in enumerate(record.requirements) if requirement > 0]
        period_metrics.append({
            "period": record.period, "problem_id": record.problem_id,
            "task_relevant_output": sum(record.outputs[k] for k in active),
            "all_skill_output": record.outputs,
            "functional_success": record.functional_result.success,
            "normalized_deficit": record.functional_result.normalized_deficit,
            "effort": record.productive_effort_used,
            "exposure": record.effective_work_used,
            "productivity_at_period_start": record.productivity_before,
            "experience_after": record.experience_after,
            "allocation": record.allocation,
            "predicted_output": record.router_predicted_outputs,
            "prediction_error": (None if record.router_predicted_outputs is None else
                                 tuple(record.outputs[k] - record.router_predicted_outputs[k]
                                       for k in range(2))),
        })
    return {
        "schema": "hls-nembhard-campaign-metrics/1.0", "metrics": metrics,
        "all_dimension_output_by_skill": [
            sum(record.outputs[k] for record in records) for k in range(2)],
        "by_problem_type": by_problem,
        "allocation_by_problem_type": allocation_by_problem,
        "prediction_errors": prediction_errors,
        "summary_field_units": {
            "all_dimension_output_by_skill": result.output_unit,
            "agent_effort_totals": result.effort_intensity_unit,
            "agent_effort_shares": "fraction of realized effort within problem type",
            "agent_skill_effort_totals": result.effort_intensity_unit,
            "agent_skill_effort_shares": "fraction of realized skill-specific effort within problem type",
        },
        "field_units": {
            "task_relevant_output": result.output_unit,
            "all_skill_output": result.output_unit,
            "functional_success": "boolean",
            "normalized_deficit": "dimensionless",
            "effort": result.effort_intensity_unit,
            "exposure": result.exposure_unit,
            "productivity_at_period_start": f"{result.output_unit}/{result.exposure_unit}",
            "experience_after": result.exposure_unit,
            "allocation": result.effort_intensity_unit,
            "predicted_output": result.output_unit,
            "prediction_error": result.output_unit,
        },
        "period_metrics": period_metrics,
        "period_trajectories": {
            "experience": [record.experience_after for record in records],
            "productivity_at_period_start": [record.productivity_before for record in records],
            "allocation": [record.allocation for record in records],
            "output_by_skill": [record.outputs for record in records],
            "success": [record.functional_result.success for record in records],
            "normalized_deficit": [record.functional_result.normalized_deficit for record in records],
            "adaptive_prediction_error_by_skill": [
                None if record.router_predicted_outputs is None else
                [record.outputs[k] - record.router_predicted_outputs[k] for k in range(2)]
                for record in records],
        },
    }


def _build_result_payload(
    config: EpisodeConfig,
    result: NKNembhardDirectRunResult,
    problems: Sequence[ProblemSpecNK],
    *,
    software_revision: str | None = None,
) -> dict[str, Any]:
    seeds = [SeedRecord("demand", config.sequence_seed, "frozen explicit problem order")]
    if config.arm.startswith("adaptive"):
        seeds.extend((
            SeedRecord("adaptive_observation", config.observation_seed, "Nembhard feedback noise"),
            SeedRecord("adaptive_exploration", config.exploration_seed, "epsilon-greedy decisions"),
        ))
    decision_info = {
        "fixed": "current problem and predeclared role map",
        "oracle": "current problem, resources, true experience and true Nembhard profile",
        "adaptive": "current problem, resources, estimated productivity and reconstructed experience; no true k,p,r or productivity",
    }[config.arm.split("_sigma")[0]]
    observation_model = None if not config.arm.startswith("adaptive") else {
        "kind": "individual agent-skill output observations",
        "noise": "Gaussian additive on work output",
        "stddev": config.observation_noise_stddev,
        "selected_cells_only": True,
    }
    context = RunAdapterContext(
        run_id=config.episode_id,
        configuration=asdict(config) | {
            "ordered_demand_hash": config.sequence_id,
            "demand_multiset_hash": config.multiset_id,
            "profile_k": _profile(config.profile_id, config.learning_scale_id,
                                  config.permutation).asymptotic_productivity,
            "profile_p": _profile(config.profile_id, config.learning_scale_id,
                                  config.permutation).prior_experience,
            "profile_r": _profile(config.profile_id, config.learning_scale_id,
                                  config.permutation).experience_scale,
            "problem_catalogue": [_problem_record(_problem(name))
                                  for name in sorted(PROBLEM_CATALOGUE)],
            "horizon": config.horizon, "duration": config.duration,
            "effort_limits": config.effort_limits,
            "collective_budget": config.collective_budget,
            "max_candidates": config.max_candidates,
        },
        initial_conditions={"experience": result.initial_experience,
                            "agent_ids": result.agent_ids, "skill_ids": result.skill_ids,
                            "hls_competence_placeholder": ((0.0, 0.0),) * 3,
                            "competence_placeholder_used_by_physics": False},
        random_seeds=tuple(seeds), information_available={"decision_input": decision_info},
        observation_model=observation_model, software_revision=software_revision,
        metadata={"campaign_protocol": "HLS_NEMBHARD_ADAPTIVE_ALLOCATION_PROTOCOL"},
    )
    common = adapt_nembhard_run(result, context=context)
    campaign_policy_id = {
        "fixed": "fixed_role_map", "oracle": "nembhard_oracle",
        "adaptive_sigma_0": "nembhard_adaptive",
        "adaptive_sigma_005": "nembhard_adaptive",
    }[config.arm]
    common = replace(common, policy_id=campaign_policy_id)
    campaign_metrics = _campaign_metrics(result)
    additions = tuple(MetricValue(
        item["name"], item["value"], item["unit"], item["interpretation"],
        "higher" if item["name"] in {
            "cumulative_task_relevant_production", "functional_success_proportion"
        } else "lower",
    ) for item in campaign_metrics["metrics"])
    existing_metric_names = {metric.name for metric in common.metrics}
    additions = tuple(metric for metric in additions if metric.name not in existing_metric_names)
    common = replace(common, metrics=common.metrics + additions)
    demand = {"ordered_hash": config.sequence_id, "multiset_hash": config.multiset_id,
              "problems": [_problem_record(problem) for problem in problems]}
    payload = {"experiment_run": common.to_dict(), "campaign_metrics": campaign_metrics,
               "native_nembhard_result": asdict(result), "demand": demand}
    return payload


def _persist_result_payload(config: EpisodeConfig, payload: Mapping[str, Any],
                            output_root: Path | str) -> Path:
    target = Path(output_root) / config.episode_id
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(exist_ok=False)
    (target / "run.json").write_text(
        canonical_json(payload["experiment_run"]) + "\n", encoding="utf-8")
    (target / "campaign_metrics.json").write_text(
        canonical_json({"campaign_metrics": payload["campaign_metrics"],
                        "demand": payload["demand"]}) + "\n", encoding="utf-8")
    (target / "native_nembhard_result.json").write_text(
        canonical_json(payload["native_nembhard_result"]) + "\n", encoding="utf-8")
    return target


def execute_episode(config: EpisodeConfig, output_root: Path | str = RESULTS_DIRECTORY,
                    *, persist: bool = True, software_revision: str | None = None) -> dict[str, Any]:
    """Run exactly one selected episode; output directories are never overwritten."""
    result, problems = _run_configuration(config)
    payload = _build_result_payload(config, result, problems,
                                    software_revision=software_revision)
    if persist:
        _persist_result_payload(config, payload, output_root)
    return payload


def _metric_lookup(payload: Mapping[str, Any]) -> dict[str, float]:
    return {row["name"]: float(row["value"])
            for row in payload.get("campaign_metrics", {}).get("metrics", [])}


def policy_condition_id(config: EpisodeConfig) -> str:
    if not config.arm.startswith("adaptive"):
        return config.arm
    return f"{config.arm}_eps_{float(config.epsilon):.2f}"


def paired_differences(rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
                       policy_a: str, policy_b: str, metric: str, *,
                       components: tuple[str, ...] = ("primary",)) -> tuple[dict[str, Any], ...]:
    """Return A−B contrasts paired on replicate and frozen demand path.

    Selectors are FIXED/ORACLE arm IDs or adaptive condition IDs such as
    adaptive_sigma_0_eps_0.05. This distinguishes the epsilon-zero control
    from its primary epsilon=.05 arm.
    """
    indexed: dict[tuple[Any, ...], dict[str, float]] = {}
    for config, payload in rows:
        if config.design_component not in components:
            continue
        condition = policy_condition_id(config)
        if condition not in {policy_a, policy_b}:
            continue
        key = (config.profile_id, config.learning_scale_id, config.demand_order,
               config.replicate, config.permutation, config.sequence_id)
        bucket = indexed.setdefault(key, {})
        if condition in bucket:
            raise ValueError(f"duplicate result for condition {condition} in pair {key}")
        bucket[condition] = _metric_lookup(payload)[metric]
    incomplete = [key for key, values in indexed.items() if set(values) != {policy_a, policy_b}]
    if incomplete:
        raise ValueError(f"paired contrast has {len(incomplete)} unmatched cells")
    return tuple({"pair": key, "difference": values[policy_a] - values[policy_b]}
                 for key, values in sorted(indexed.items(), key=lambda item: item[0]))


def _policy_delta_map(rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
                      policy_a: str, policy_b: str, metric: str) -> dict[tuple[Any, ...], float]:
    pairs = paired_differences(rows, policy_a, policy_b, metric, components=("primary",))
    return {tuple(pair["pair"]): float(pair["difference"]) for pair in pairs}


def protocol_interaction_contrasts(
    rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
    policy_a: str, policy_b: str, metric: str,
) -> dict[str, dict[str, tuple[float, ...]]]:
    """Compute the predeclared H1–H3 difference-in-differences by replicate.

    Returns bundle-level contrasts separated by all remaining factorial
    conditions. This prevents scenario heterogeneity being treated as seed
    uncertainty.
    """
    rows = tuple(rows)
    base = _policy_delta_map(rows, policy_a, policy_b, metric)
    output: dict[str, dict[str, list[float]]] = {
        "H1_mixed_minus_homogeneous": {},
        "H1_specialists_minus_homogeneous": {},
        "H2_fast_minus_slow": {},
        "H3_clustered_minus_interleaved": {},
    }
    # The policy contrast itself is ADAPTIVE minus FIXED for H1–H3.
    for profile, other_profile in (("mixed", "homogeneous"),
                                   ("specialists", "homogeneous")):
        keys = sorted(key for key in base if key[0] == profile)
        for key in keys:
            counterpart = (other_profile,) + key[1:]
            if counterpart in base:
                label = ("H1_mixed_minus_homogeneous" if profile == "mixed"
                         else "H1_specialists_minus_homogeneous")
                stratum = f"learning={key[1]}|order={key[2]}"
                output[label].setdefault(stratum, []).append(base[key] - base[counterpart])
    for key in sorted(base):
        # Conditions are keyed (profile, learning, order, replicate, rows, sequence).
        profile, learning, order, replicate, permutation, seq_hash = key
        if learning == "fast":
            other = (profile, "slow", order, replicate, permutation, seq_hash)
            if other in base:
                stratum = f"profile={profile}|order={order}"
                output["H2_fast_minus_slow"].setdefault(stratum, []).append(
                    base[key] - base[other])
    # Demand order intentionally changes the ordered hash, but not its multiset.
    config_by_key: dict[tuple[Any, ...], EpisodeConfig] = {}
    for config, _ in rows:
        if config.design_component != "primary":
            continue
        condition = policy_condition_id(config)
        if condition in {policy_a, policy_b}:
            key = (config.profile_id, config.learning_scale_id, config.demand_order,
                   config.replicate, config.permutation, config.sequence_id)
            config_by_key[key] = config
    for key in sorted(base):
        profile, learning, order, replicate, permutation, seq_hash = key
        if order != "clustered":
            continue
        clustered_config = config_by_key[key]
        other = next((candidate_key for candidate_key, candidate_config in config_by_key.items()
                      if candidate_key[0] == profile and candidate_key[1] == learning
                      and candidate_key[2] == "interleaved" and candidate_key[3] == replicate
                      and candidate_key[4] == permutation
                      and candidate_config.multiset_id == clustered_config.multiset_id), None)
        if other is not None and other in base:
            stratum = f"profile={profile}|learning={learning}"
            output["H3_clustered_minus_interleaved"].setdefault(stratum, []).append(
                base[key] - base[other])
    return {name: {stratum: tuple(values) for stratum, values in strata.items()}
            for name, strata in output.items()}


def summarize_pairs_by_stratum(
    pairs: Sequence[Mapping[str, Any]],
    *,
    dimensions: int,
    seed: int = MASTER_SEED,
    resamples: int = 10000,
    expected_pairs: int = 20,
) -> tuple[dict[str, Any], ...]:
    """Summarize separately within predeclared factorial strata."""
    grouped: dict[tuple[Any, ...], list[float]] = {}
    for pair in pairs:
        key = tuple(pair["pair"][:dimensions])
        grouped.setdefault(key, []).append(float(pair["difference"]))
    if not grouped or any(len(values) != expected_pairs for values in grouped.values()):
        raise ValueError(f"each scenario stratum must contain exactly {expected_pairs} seed bundles")
    return tuple({"stratum": key,
                  **summarize_paired_contrast(
                      tuple({"difference": value} for value in values),
                      seed=seed + index, resamples=resamples)}
                 for index, (key, values) in enumerate(sorted(grouped.items())))


def analyze_campaign(rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]], *,
                     bootstrap_seed: int = MASTER_SEED,
                     resamples: int = 10000) -> dict[str, Any]:
    """Calculate protocol contrasts over supplied completed episode results."""
    rows = tuple(rows)
    expected_ids = {config.episode_id for config in build_design_registry().episodes}
    actual_ids = [config.episode_id for config, _ in rows]
    if len(set(actual_ids)) != len(actual_ids):
        raise ValueError("duplicate episode result IDs supplied to analysis")
    missing = expected_ids - set(actual_ids)
    unexpected = set(actual_ids) - expected_ids
    if missing or unexpected:
        raise ValueError(f"analysis requires the complete 1,016-run design; missing={len(missing)}, unexpected={len(unexpected)}")
    comparisons = (
        ("adaptive_sigma_0_eps_0.05", "fixed"),
        ("adaptive_sigma_005_eps_0.05", "fixed"),
        ("oracle", "fixed"),
        ("adaptive_sigma_005_eps_0.05", "adaptive_sigma_0_eps_0.05"),
    )
    results: dict[str, Any] = {}
    for metric in ("cumulative_task_relevant_production",
                   "functional_success_proportion", "cumulative_normalized_deficit"):
        results[metric] = {}
        for left, right in comparisons:
            pairs = paired_differences(rows, left, right, metric)
            results[metric][f"{left}_minus_{right}"] = summarize_pairs_by_stratum(
                pairs, dimensions=3, seed=bootstrap_seed, resamples=resamples)
        interaction = protocol_interaction_contrasts(
            rows, "adaptive_sigma_0_eps_0.05", "fixed", metric)
        results[metric]["predeclared_interactions"] = {
            hypothesis: {
                stratum: summarize_paired_contrast(
                    tuple({"difference": value} for value in values),
                    seed=bootstrap_seed + index, resamples=resamples,
                )
                for index, (stratum, values) in enumerate(sorted(strata.items()))
            }
            for hypothesis, strata in interaction.items()
        }
    results["first_period_policy_contrasts"] = {}
    for metric in ("cumulative_task_relevant_production",
                   "functional_success_proportion", "cumulative_normalized_deficit"):
        results["first_period_policy_contrasts"][metric] = {}
        for left, right in comparisons:
            pairs = paired_period_differences(rows, left, right, 0, metric)
            results["first_period_policy_contrasts"][metric][f"{left}_minus_{right}"] = \
                summarize_pairs_by_stratum(pairs, dimensions=3, seed=bootstrap_seed + 31,
                                           resamples=resamples)
    epsilon_rows = tuple((config, payload) for config, payload in rows
                         if config.profile_id == "mixed" and config.learning_scale_id == "fast"
                         and config.demand_order == "clustered"
                         and config.arm.startswith("adaptive"))
    results["epsilon_zero_sensitivity"] = {}
    for metric in ("cumulative_task_relevant_production",
                   "functional_success_proportion", "cumulative_normalized_deficit"):
        for arm in ("adaptive_sigma_0", "adaptive_sigma_005"):
            pairs = paired_differences(
                epsilon_rows, f"{arm}_eps_0.00", f"{arm}_eps_0.05", metric,
                components=("primary", "epsilon_zero"),
            )
            results["epsilon_zero_sensitivity"].setdefault(metric, {})[arm] = \
                summarize_pairs_by_stratum(pairs, dimensions=3, seed=bootstrap_seed + 17,
                                           resamples=resamples)
    results["demand_order_contrasts"] = {}
    order_conditions = ("fixed", "oracle", "adaptive_sigma_0_eps_0.05",
                       "adaptive_sigma_005_eps_0.05")
    for metric in ("cumulative_task_relevant_production",
                   "functional_success_proportion", "cumulative_normalized_deficit"):
        results["demand_order_contrasts"][metric] = {
            condition: summarize_pairs_by_stratum(
                paired_order_differences(rows, condition, metric),
                dimensions=2, seed=bootstrap_seed + 47 + index, resamples=resamples,
            )
            for index, condition in enumerate(order_conditions)
        }
    return {"schema": "hls-nembhard-campaign-analysis/1.0",
            "resampling_unit": "replicate seed bundle", "results": results}


def grouped_descriptives(
    rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
    group_fields: tuple[str, ...] = (
        "profile_id", "learning_scale_id", "demand_order", "arm",
        "design_component", "permutation",
    ),
) -> tuple[dict[str, Any], ...]:
    """Scenario-wise descriptive summaries; no cross-metric score is formed."""
    grouped: dict[tuple[Any, ...], dict[str, list[float]]] = {}
    for config, payload in rows:
        group_values = tuple(
            policy_condition_id(config) if field == "arm" else getattr(config, field)
            for field in group_fields
        )
        metrics = _metric_lookup(payload)
        bucket = grouped.setdefault(group_values, {})
        for name, value in metrics.items():
            bucket.setdefault(name, []).append(value)
    output = []
    for key, metrics in sorted(grouped.items(), key=lambda item: item[0]):
        output.append({
            "group": dict(zip(group_fields, key)),
            "metrics": {name: {"n_episodes": len(values), "mean": mean(values),
                               "median": median(values), "minimum": min(values),
                               "maximum": max(values)}
                        for name, values in sorted(metrics.items())},
        })
    return tuple(output)


def paired_period_differences(
    rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
    policy_a: str, policy_b: str, period_index: int, measure: str,
) -> tuple[dict[str, Any], ...]:
    """Paired first-period or period-specific outcomes, never treating periods as replicates."""
    measure_fields = {
        "cumulative_task_relevant_production": "task_relevant_output",
        "functional_success_proportion": "functional_success",
        "cumulative_normalized_deficit": "normalized_deficit",
    }
    if measure not in measure_fields or period_index < 0:
        raise ValueError("unsupported period measure or negative period index")
    indexed: dict[tuple[Any, ...], dict[str, float]] = {}
    field = measure_fields[measure]
    for config, payload in rows:
        if config.design_component != "primary":
            continue
        condition = policy_condition_id(config)
        if condition not in {policy_a, policy_b}:
            continue
        periods = payload.get("campaign_metrics", {}).get("period_metrics", [])
        if period_index >= len(periods):
            raise ValueError(f"period {period_index} missing from {config.episode_id}")
        key = (config.profile_id, config.learning_scale_id, config.demand_order,
               config.replicate, config.permutation, config.sequence_id)
        indexed.setdefault(key, {})[condition] = float(periods[period_index][field])
    if any(set(values) != {policy_a, policy_b} for values in indexed.values()):
        raise ValueError("period comparison has unmatched condition cells")
    return tuple({"pair": key, "difference": values[policy_a] - values[policy_b]}
                 for key, values in sorted(indexed.items()))


def paired_order_differences(
    rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
    condition: str,
    metric: str,
) -> tuple[dict[str, Any], ...]:
    """Return clustered-minus-interleaved outcomes paired by bundle/multiset."""
    indexed: dict[tuple[Any, ...], dict[str, float]] = {}
    for config, payload in rows:
        if config.design_component != "primary" or policy_condition_id(config) != condition:
            continue
        key = (config.profile_id, config.learning_scale_id, config.replicate,
               config.permutation, config.multiset_id)
        indexed.setdefault(key, {})[config.demand_order] = _metric_lookup(payload)[metric]
    if any(set(values) != {"interleaved", "clustered"} for values in indexed.values()):
        raise ValueError("demand-order comparison has unmatched same-multiset pairs")
    return tuple({"pair": key, "difference": values["clustered"] - values["interleaved"]}
                 for key, values in sorted(indexed.items()))


def temporal_summary(
    rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
) -> tuple[dict[str, Any], ...]:
    """Mean period trajectories grouped by scenario and decision condition."""
    grouped: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    for config, payload in rows:
        key = (config.profile_id, config.learning_scale_id, config.demand_order,
               policy_condition_id(config), config.design_component, config.permutation)
        for period in payload.get("campaign_metrics", {}).get("period_metrics", []):
            grouped.setdefault(key + (int(period["period"]),), []).append(period)
    output = []
    for key, periods in sorted(grouped.items(), key=lambda item: item[0]):
        output.append({
            "profile_id": key[0], "learning_scale_id": key[1],
            "demand_order": key[2], "condition_id": key[3],
            "design_component": key[4], "permutation": key[5], "period": key[6],
            "n_episodes": len(periods),
            "mean_task_relevant_output": mean(float(p["task_relevant_output"]) for p in periods),
            "functional_success_proportion": mean(float(bool(p["functional_success"])) for p in periods),
            "mean_normalized_deficit": mean(float(p["normalized_deficit"]) for p in periods),
            "mean_experience_after": _matrix_mean([p["experience_after"] for p in periods]),
            "mean_productivity_at_period_start": _matrix_mean(
                [p["productivity_at_period_start"] for p in periods]),
            "mean_effort_allocation": _matrix_mean([p["allocation"] for p in periods]),
        })
    return tuple(output)


def _matrix_mean(matrices: Sequence[Sequence[Sequence[float]]]) -> tuple[tuple[float, ...], ...]:
    if not matrices:
        return ()
    n_rows, n_cols = len(matrices[0]), len(matrices[0][0])
    return tuple(tuple(mean(float(matrix[i][k]) for matrix in matrices)
                         for k in range(n_cols)) for i in range(n_rows))


def allocation_share_summary(
    rows: Iterable[tuple[EpisodeConfig, Mapping[str, Any]]],
) -> tuple[dict[str, Any], ...]:
    """Descriptive mean effort shares by agent, skill, problem, and condition.

    Shares use total realized effort for the corresponding problem type within
    each episode as denominator. No concentration index is introduced.
    """
    grouped: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    for config, payload in rows:
        for problem_id, values in payload.get("campaign_metrics", {}).get(
                "allocation_by_problem_type", {}).items():
            key = (config.profile_id, config.learning_scale_id, config.demand_order,
                   policy_condition_id(config), config.design_component,
                   config.permutation, problem_id)
            grouped.setdefault(key, []).append(values)
    output = []
    for key, values in sorted(grouped.items(), key=lambda item: item[0]):
        n_agents = len(values[0]["agent_effort_shares"])
        n_skills = len(values[0]["agent_skill_effort_shares"][0])
        output.append({
            "profile_id": key[0], "learning_scale_id": key[1],
            "demand_order": key[2], "condition_id": key[3],
            "design_component": key[4], "permutation": key[5],
            "problem_id": key[6], "n_episodes": len(values),
            "mean_agent_effort_shares": [
                mean(float(item["agent_effort_shares"][i]) for item in values)
                for i in range(n_agents)],
            "mean_agent_skill_effort_shares": [
                [mean(float(item["agent_skill_effort_shares"][i][k]) for item in values)
                 for k in range(n_skills)] for i in range(n_agents)],
            "interpretation": "Descriptive allocation shares, not causal contributions or a concentration index.",
        })
    return tuple(output)


def load_completed_results(
    root: Path | str = RESULTS_DIRECTORY,
    registry: DesignRegistry | None = None,
    *,
    episode_ids: Iterable[str] | None = None,
) -> tuple[tuple[EpisodeConfig, Mapping[str, Any]], ...]:
    """Load saved run/metric envelopes without executing or modifying runs."""
    registry = registry or build_design_registry()
    by_id = {config.episode_id: config for config in registry.episodes}
    selected = set(by_id) if episode_ids is None else set(episode_ids)
    unknown = selected - set(by_id)
    if unknown:
        raise ValueError(f"unknown episode IDs: {sorted(unknown)[:3]}")
    rows = []
    for episode_id in sorted(selected):
        directory = Path(root) / episode_id
        run_path = directory / "run.json"
        metrics_path = directory / "campaign_metrics.json"
        native_path = directory / "native_nembhard_result.json"
        if not run_path.exists() and not metrics_path.exists():
            continue
        if not run_path.is_file() or not metrics_path.is_file() or not native_path.is_file():
            raise ValueError(f"incomplete result artifacts for {episode_id}")
        run = json.loads(run_path.read_text(encoding="utf-8"))
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        native = json.loads(native_path.read_text(encoding="utf-8"))
        if run.get("run_id") != episode_id:
            raise ValueError(f"run ID mismatch for {episode_id}")
        config = by_id[episode_id]
        demand = metrics.get("demand", {})
        if (demand.get("ordered_hash") != config.sequence_id
                or demand.get("multiset_hash") != config.multiset_id
                or run.get("configuration", {}).get("ordered_demand_hash") != config.sequence_id
                or native.get("router_id") != (None if config.arm == "fixed" else
                                                  "nembhard_oracle" if config.arm == "oracle"
                                                  else "nembhard_adaptive")):
            raise ValueError(f"result provenance/configuration mismatch for {episode_id}")
        stored_problems = tuple(ProblemSpecNK(
            row["problem_id"], tuple(row["requirements"]), row["resource_budget"],
            tuple(row["ces_weights"]),
        ) for row in demand.get("problems", ()))
        expected_sequence = build_demand_sequence(config.demand_order, config.sequence_seed)
        native_problem_ids = tuple(record["problem_id"] for record in native.get("records", ()))
        if (ordered_demand_hash(stored_problems) != config.sequence_id
                or demand_multiset_hash(stored_problems) != config.multiset_id
                or stored_problems != expected_sequence.problems
                or native_problem_ids != tuple(problem.problem_id for problem in stored_problems)):
            raise ValueError(f"saved demand/trajectory integrity mismatch for {episode_id}")
        rows.append((by_id[episode_id], metrics))
    return tuple(rows)


def bootstrap_interval(values: Sequence[float], *, seed: int = MASTER_SEED,
                       resamples: int = 10000) -> tuple[float, float]:
    if not values or resamples < 1:
        raise ValueError("values and positive resamples are required")
    if any(not math.isfinite(float(value)) for value in values):
        raise ValueError("bootstrap values must be finite")
    rng = random.Random(seed)
    n = len(values)
    means = sorted(mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(resamples))
    return means[int(0.025 * (resamples - 1))], means[int(0.975 * (resamples - 1))]


def summarize_paired_contrast(pairs: Sequence[Mapping[str, Any]], *,
                              seed: int = MASTER_SEED,
                              resamples: int = 10000) -> dict[str, Any]:
    values = tuple(float(pair["difference"]) for pair in pairs)
    if not values:
        raise ValueError("cannot summarize an empty contrast")
    return {
        "n_pairs": len(values), "paired_values": values, "mean": mean(values),
        "median": median(values),
        "bootstrap_95_percentile_interval": bootstrap_interval(
            values, seed=seed, resamples=resamples),
        "proportion_positive": sum(value > 0 for value in values) / len(values),
        "proportion_negative": sum(value < 0 for value in values) / len(values),
        "proportion_zero": sum(value == 0 for value in values) / len(values),
    }


def _cli() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--limit", type=int, default=20)
    list_parser.add_argument("--all", action="store_true")
    subparsers.add_parser("validate")
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("--input-root", type=Path, default=RESULTS_DIRECTORY)
    analyze_parser.add_argument("--output", type=Path)
    run_parser = subparsers.add_parser("run")
    group = run_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--episode-id")
    group.add_argument("--episode-ids", nargs="+")
    group.add_argument("--all", action="store_true")
    run_parser.add_argument("--confirm-campaign")
    run_parser.add_argument("--output-root", type=Path, default=RESULTS_DIRECTORY)
    run_parser.add_argument("--software-revision")
    args = parser.parse_args()
    registry = build_design_registry()
    if args.command == "list":
        selected = registry.episodes if args.all else registry.episodes[:args.limit]
        print(canonical_json([asdict(config) for config in selected]))
        print(canonical_json({"unique": len(registry.episodes),
                              "diagnostic_aliases": registry.diagnostic_aliases}))
    elif args.command == "validate":
        print(canonical_json(validate_design(registry)))
    elif args.command == "analyze":
        rows = load_completed_results(args.input_root, registry)
        analysis = analyze_campaign(rows)
        analysis["grouped_descriptives"] = grouped_descriptives(rows)
        analysis["temporal_summary"] = temporal_summary(rows)
        analysis["allocation_share_summary"] = allocation_share_summary(rows)
        rendered = canonical_json(analysis) + "\n"
        if args.output is None:
            print(rendered, end="")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(rendered)
    else:
        if args.all:
            if args.confirm_campaign != CONFIRM_ALL_TOKEN:
                parser.error(f"--all requires --confirm-campaign {CONFIRM_ALL_TOKEN}")
            selected = registry.episodes
        elif args.episode_id:
            selected = tuple(c for c in registry.episodes if c.episode_id == args.episode_id)
        else:
            wanted = set(args.episode_ids)
            selected = tuple(c for c in registry.episodes if c.episode_id in wanted)
            if {c.episode_id for c in selected} != wanted:
                parser.error("one or more selected episode IDs are unknown")
        if not selected:
            parser.error("no episodes selected")
        for config in selected:
            execute_episode(config, args.output_root,
                            software_revision=args.software_revision)
            print(config.episode_id)


if __name__ == "__main__":
    _cli()
