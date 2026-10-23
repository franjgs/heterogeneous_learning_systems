"""Run a reproducible N×K MIS-v2 organization pilot (no import-time execution)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import statistics
import sys
from time import perf_counter

from hls.hls_lab_nk_environment import (
    DemandRegimeNK,
    ExogenousEnvironmentConfigNK,
    generate_environment_trajectory_nk,
)
from hls.hls_lab_nk_geometry import (
    OrganizationConfigNK,
    ProblemSpecNK,
    ProductiveAllocationNK,
    validate_productive_allocation_nk,
)
from hls.hls_lab_nk_learning import LearningProfileNK, mis_v2_transition_nk
from hls.hls_lab_nk_production import evaluate_problem_nk, productive_outputs_nk
from hls.synthetic.c5 import NonStationaryTaskDemand


OUTPUT = Path("results/experiments/hls_rq1_learning_organization/results.json")
PLOT = Path("results/experiments/hls_rq1_learning_organization/comparison.png")
TASKS = ("diagnostics", "repair", "inspection")
AGENTS = ("A", "B", "C", "D", "E")
SKILLS = TASKS
EFFORTS = (0.5, 1.0)
PLANNING_HORIZON = 2
HORIZON = 100
REQUIREMENT = 0.88
RESOURCE_BUDGET = 1.0

INITIAL_COMPETENCE = (
    (0.78, 0.31, 0.27),
    (0.29, 0.76, 0.34),
    (0.32, 0.37, 0.79),
    (0.60, 0.57, 0.41),
    (0.40, 0.59, 0.62),
)
LEARNING_ETA = (
    (0.09, 0.10, 0.08),
    (0.08, 0.09, 0.10),
    (0.10, 0.08, 0.09),
    (0.13, 0.12, 0.11),
    (0.12, 0.10, 0.14),
)


def problem_requirements(task_index: int) -> tuple[float, ...]:
    return tuple(REQUIREMENT if skill == task_index else 0.0
                 for skill in range(len(TASKS)))


def build_model():
    organization = OrganizationConfigNK(
        AGENTS, SKILLS, INITIAL_COMPETENCE, (1.0,) * len(AGENTS), RESOURCE_BUDGET,
    )
    learning = LearningProfileNK(LEARNING_ETA)
    problems = tuple(
        ProblemSpecNK(task, problem_requirements(index), RESOURCE_BUDGET,
                      tuple(1.0 if skill == index else 0.0 for skill in range(3)))
        for index, task in enumerate(TASKS)
    )
    distributions = {}
    for t in range(HORIZON):
        if t < 30:
            probabilities = (0.70, 0.20, 0.10)
        elif t < 60:
            probabilities = (0.20, 0.60, 0.20)
        else:
            probabilities = (0.15, 0.20, 0.65)
        distributions[t] = dict(zip(TASKS, probabilities))
    process = NonStationaryTaskDemand(distributions)
    environment = ExogenousEnvironmentConfigNK(
        process,
        {task: DemandRegimeNK(task, (problems[index],), (1.0,))
         for index, task in enumerate(TASKS)},
        HORIZON,
        RESOURCE_BUDGET,
    )
    actions = tuple((agent, effort) for agent in range(len(AGENTS))
                    for effort in EFFORTS)
    return organization, learning, problems, environment, actions


def allocation_for(task_index: int, action: tuple[int, float]) -> ProductiveAllocationNK:
    agent, effort = action
    return tuple(tuple(
        effort if i == agent and skill == task_index else 0.0
        for skill in range(len(SKILLS))) for i in range(len(AGENTS)))


def task_score(competence, task_index: int, action, problem: ProblemSpecNK):
    allocation = allocation_for(task_index, action)
    outputs = productive_outputs_nk(competence, allocation)
    ratio = outputs[task_index] / problem.requirements[task_index]
    functional = evaluate_problem_nk(outputs, problem.requirements)
    return min(1.0, ratio), functional.success, allocation


def next_competence(competence, allocation, learning):
    return mis_v2_transition_nk(competence, allocation, learning, enabled=True)


def _action_tie_key(action):
    # Stable tie rule shared by all policies: least effort, then agent order.
    return (action[1], action[0])


def reactive_action(competence, task_index, problem, actions):
    ranked = [(task_score(competence, task_index, action, problem)[0],
               action) for action in actions]
    best_reward = max(score for score, _ in ranked)
    return min((action for score, action in ranked
                if abs(score - best_reward) <= 1e-12), key=_action_tie_key)


def anticipatory_action(competence, task_index, period, problems, actions,
                        learning, demand_probabilities, depth=PLANNING_HORIZON):
    """Exact nonclairvoyant receding-horizon DP over the next ``depth`` periods."""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def value(t, current_task, state, remaining):
        problem = problems[current_task]
        best = float("-inf")
        for action in actions:
            reward, _, allocation = task_score(state, current_task, action, problem)
            after = next_competence(state, allocation, learning)
            continuation = 0.0
            if remaining > 1 and t + 1 < HORIZON:
                for next_index, probability in enumerate(demand_probabilities[t + 1]):
                    if probability:
                        continuation += probability * value(
                            t + 1, next_index, after, remaining - 1,
                        )
            total = reward + continuation
            if total > best:
                best = total
        return best

    candidates = []
    problem = problems[task_index]
    for action in actions:
        reward, _, allocation = task_score(competence, task_index, action, problem)
        after = next_competence(competence, allocation, learning)
        continuation = 0.0
        if depth > 1 and period + 1 < HORIZON:
            for next_index, probability in enumerate(demand_probabilities[period + 1]):
                if probability:
                    continuation += probability * value(
                        period + 1, next_index, after, depth - 1,
                    )
        candidates.append((reward + continuation, action))
    best_value = max(value for value, _ in candidates)
    return min((action for value, action in candidates
                if abs(value - best_value) <= 1e-12), key=_action_tie_key)


def run_episode(tasks, policy_id, mapping, organization, problems, actions, learning,
                demand_probabilities):
    competence = organization.competence_initial
    trace = []
    for period, task in enumerate(tasks):
        task_index = TASKS.index(task)
        problem = problems[task_index]
        if policy_id == "FIXED_OPT":
            action = mapping[task_index]
        elif policy_id == "REACTIVE":
            action = reactive_action(competence, task_index, problem, actions)
        else:
            action = anticipatory_action(
                competence, task_index, period, problems, actions, learning,
                demand_probabilities,
            )
        reward, success, allocation = task_score(competence, task_index, action, problem)
        if not validate_productive_allocation_nk(allocation, organization, problem):
            raise AssertionError("selected action violated shared/individual resources")
        after = next_competence(competence, allocation, learning)
        trace.append({
            "period": period,
            "task": task,
            "assigned_agent": AGENTS[action[0]],
            "task_skill": SKILLS[task_index],
            "effort": action[1],
            "reward": reward,
            "success": success,
            "resource_used": sum(map(sum, allocation)),
            "competence_before": competence,
            "competence_after": after,
        })
        competence = after
    return {
        "cumulative_reward": sum(row["reward"] for row in trace),
        "success_count": sum(row["success"] for row in trace),
        "resource_used": sum(row["resource_used"] for row in trace),
        "final_competence": competence,
        "trace": trace,
    }


def _best_fixed_mapping(train_trajectories, organization, problems, actions, learning):
    best_mapping = None
    best_score = float("-inf")
    best_resource = float("inf")
    # 10 choices per task, so the complete stationary task→agent/effort class
    # contains exactly 10^3 maps and can be exhaustively optimized.
    from itertools import product
    for mapping in product(actions, repeat=len(TASKS)):
        score = resource = 0.0
        for tasks in train_trajectories:
            episode = run_episode(tasks, "FIXED_OPT", mapping, organization,
                                  problems, actions, learning, ())
            score += episode["cumulative_reward"]
            resource += episode["resource_used"]
        score /= len(train_trajectories)
        if (score > best_score + 1e-12
                or (abs(score - best_score) <= 1e-12
                    and resource < best_resource - 1e-12)):
            best_mapping, best_score, best_resource = mapping, score, resource
    return best_mapping, best_score, best_resource, len(actions) ** len(TASKS)


def generate_trajectories(environment, seeds):
    trajectories = []
    for seed in seeds:
        generated = generate_environment_trajectory_nk(environment, seed=seed)
        trajectories.append(tuple(problem.problem_id for problem in generated.problems))
    return tuple(trajectories)


def _summarize(episodes):
    rewards = [episode["cumulative_reward"] for episode in episodes]
    success = [episode["success_count"] / HORIZON for episode in episodes]
    resources = [episode["resource_used"] for episode in episodes]
    return {
        "mean_cumulative_reward": statistics.fmean(rewards),
        "sd_cumulative_reward": statistics.stdev(rewards) if len(rewards) > 1 else 0.0,
        "mean_task_success_rate": statistics.fmean(success),
        "overall_task_success_rate": sum(e["success_count"] for e in episodes) / (len(episodes) * HORIZON),
        "mean_resource_used": statistics.fmean(resources),
        "mean_resource_per_period": statistics.fmean(resources) / HORIZON,
        "mean_final_competence": tuple(
            tuple(statistics.fmean(e["final_competence"][i][k] for e in episodes)
                  for k in range(len(SKILLS))) for i in range(len(AGENTS))
        ),
    }


def evaluate_campaign(train_seeds=tuple(range(1, 11)),
                      evaluation_seeds=tuple(range(101, 121))):
    organization, learning, problems, environment, actions = build_model()
    train_trajectories = generate_trajectories(environment, train_seeds)
    test_trajectories = generate_trajectories(environment, evaluation_seeds)
    mapping, train_score, train_resource, candidate_count = _best_fixed_mapping(
        train_trajectories, organization, problems, actions, learning,
    )
    demand_probabilities = tuple(
        tuple(environment.process.distributions[t][task] for task in TASKS)
        for t in range(HORIZON)
    )
    results = {name: [] for name in ("FIXED_OPT", "REACTIVE", "ANTICIPATORY")}
    for seed, tasks in zip(evaluation_seeds, test_trajectories):
        # All organizations consume the exact same pre-generated C5 trajectory.
        for policy_id in results:
            episode = run_episode(tasks, policy_id, mapping, organization, problems,
                                  actions, learning, demand_probabilities)
            episode["seed"] = seed
            episode["demand_path"] = tasks
            results[policy_id].append(episode)
    summaries = {name: _summarize(episodes) for name, episodes in results.items()}
    return {
        "experiment_id": "HLS-RQ1-MISv2-organization-pilot",
        "status": "EXECUTED_BOUNDED_PAIRED_PILOT",
        "model": {
            "agents": AGENTS,
            "tasks_and_skills": TASKS,
            "horizon": HORIZON,
            "initial_competence": INITIAL_COMPETENCE,
            "mis_v2_eta": LEARNING_ETA,
            "transfer": "disabled; no teaching actions",
            "demand": {
                "process": "C5 NonStationaryTaskDemand",
                "time_blocks": [
                    {"periods": "0-29", "probabilities": (0.70, 0.20, 0.10)},
                    {"periods": "30-59", "probabilities": (0.20, 0.60, 0.20)},
                    {"periods": "60-99", "probabilities": (0.15, 0.20, 0.65)},
                ],
                "problem_requirements": {task: problem_requirements(i)
                                         for i, task in enumerate(TASKS)},
            },
            "resource_constraints": {
                "per_agent_effort_limit_per_period": 1.0,
                "collective_effort_budget_per_period": RESOURCE_BUDGET,
                "task_effort_budget": RESOURCE_BUDGET,
                "action_catalog": [{"agent": AGENTS[i], "effort": effort}
                                   for i, effort in actions],
            },
            "reward": "per-period capped fraction of the active task requirement; success separately counted; resource use reported, not double-subtracted",
            "information": "all policies observe current task and true current competencies; no future realized demand; ANTICIPATORY knows the declared nonstationary demand law and MIS-v2 parameters",
            "anticipatory_planning_horizon": PLANNING_HORIZON,
            "fixed_opt_definition": "exhaustively best stationary task→agent/effort map over the 10 calibration trajectories; evaluation uses disjoint paired seeds",
        },
        "reproducibility": {
            "training_seeds": tuple(train_seeds),
            "evaluation_seeds": tuple(evaluation_seeds),
            "evaluation_trajectories_shared": True,
            "fixed_maps_enumerated": candidate_count,
            "fixed_training_mean_reward": train_score,
            "fixed_training_mean_resource": train_resource,
            "selected_fixed_mapping": tuple(
                {"task": task, "agent": AGENTS[action[0]], "effort": action[1]}
                for task, action in zip(TASKS, mapping)
            ),
            "software": {"python": sys.version.split()[0], "platform": platform.platform()},
        },
        "summary": summaries,
        "paired_differences": {
            f"{left}_minus_{right}": statistics.fmean(
                left_ep["cumulative_reward"] - right_ep["cumulative_reward"]
                for left_ep, right_ep in zip(results[left], results[right])
            )
            for left, right in (("ANTICIPATORY", "FIXED_OPT"),
                                ("ANTICIPATORY", "REACTIVE"),
                                ("REACTIVE", "FIXED_OPT"))
        },
        "episodes": results,
    }


def plot_results(payload, path):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)
    colors = {"FIXED_OPT": "#5277a3", "REACTIVE": "#e09f3e", "ANTICIPATORY": "#6a994e"}
    for policy, episodes in payload["episodes"].items():
        color = colors[policy]
        cumulative = [
            statistics.fmean(sum(row["reward"] for row in episode["trace"][:t + 1])
                             for episode in episodes)
            for t in range(HORIZON)
        ]
        success = [statistics.fmean(episode["trace"][t]["success"] for episode in episodes)
                   for t in range(HORIZON)]
        competence = [statistics.fmean(
            episode["trace"][t]["competence_before"][i][k]
            for episode in episodes for i in range(len(AGENTS)) for k in range(len(SKILLS))
        ) for t in range(HORIZON)]
        resources = [statistics.fmean(
            sum(row["resource_used"] for row in episode["trace"][:t + 1])
            for episode in episodes
        ) for t in range(HORIZON)]
        axes[0, 0].plot(cumulative, label=policy, color=color)
        axes[0, 1].plot(success, label=policy, color=color, alpha=.8)
        axes[1, 0].plot(competence, label=policy, color=color)
        axes[1, 1].plot(resources, label=policy, color=color)
    axes[0, 0].set_title("Cumulative task reward (mean)")
    axes[0, 1].set_title("Per-period task success rate")
    axes[1, 0].set_title("Mean competence across agent-skill cells")
    axes[1, 1].set_title("Cumulative resource use (mean)")
    for ax in axes.flat:
        ax.set_xlabel("Period")
        ax.grid(alpha=.25)
    axes[0, 0].set_ylabel("Reward")
    axes[0, 1].set_ylabel("Success fraction")
    axes[1, 0].set_ylabel("Competence")
    axes[1, 1].set_ylabel("Effort units")
    axes[0, 0].legend()
    fig.suptitle("HLS-RQ1 pilot: MIS-v2 learning under shifting C5 demand")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main(output=OUTPUT, plot=PLOT, train_seed_count=10, evaluation_seed_count=20):
    if output.exists() or plot.exists():
        raise FileExistsError("refusing to overwrite an existing HLS-RQ1 pilot artifact")
    started = perf_counter()
    payload = evaluate_campaign(
        tuple(range(1, train_seed_count + 1)),
        tuple(range(101, 101 + evaluation_seed_count)),
    )
    payload["execution_seconds"] = perf_counter() - started
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    plot_results(payload, plot)
    print(f"results: {output}")
    print(f"plot: {plot}")
    for policy, summary in payload["summary"].items():
        print(policy, json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--plot", type=Path, default=PLOT)
    parser.add_argument("--train-seeds", type=int, default=10)
    parser.add_argument("--evaluation-seeds", type=int, default=20)
    args = parser.parse_args()
    main(args.output, args.plot, args.train_seeds, args.evaluation_seeds)
