"""Quantify the value barrier to physically reachable routing inversions.

Diagnostic world:
    H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5.

No parameters are searched and world physics are not modified.

For every physically reachable ROUTING_INVERTED state:
1. enumerate all positive-probability paths from S0;
2. compute the probability of each path's opportunity sequence;
3. compute exact routing and conditional-development regret along the path;
4. identify the minimum conditional path loss;
5. identify the minimum probability-weighted entry cost;
6. compare those quantities with the local routing-inversion gain.

Important:
The probability-weighted entry cost is a diagnostic quantity, not yet a
constrained-MDP value J^{->S}.  It measures the expected contribution of the
forced deviations along one particular branch.  The distinction is printed
explicitly to avoid over-interpreting it.
"""

from __future__ import annotations

from dataclasses import dataclass

import audit_inversion_avoidance as aia

from hls.synthetic.exact import (
    EXACT_TOL,
    _task,
    solve_exact_hls,
)


@dataclass(frozen=True)
class StepRegret:
    time: int
    routing_regret: float
    development_regret: float
    reach_probability_before: float
    branch_probability: float

    @property
    def conditional_regret(self):
        return self.routing_regret + self.development_regret

    @property
    def expected_contribution(self):
        return (
            self.reach_probability_before
            * self.conditional_regret
        )


@dataclass(frozen=True)
class PathAudit:
    path_number: int
    path_probability: float
    conditional_loss: float
    expected_entry_cost: float
    step_regrets: tuple[StepRegret, ...]


def opportunity_branch_probability(world, step):
    problem = world.problem
    environment = problem.environment
    task = _task(problem, step.state)

    p = environment.opportunities.probability(
        step.state,
        task,
        step.operational_action,
        (),
    )

    return p if step.opportunity else 1.0 - p


def audit_path(world, path_number, path):
    problem = world.problem

    reach_probability = 1.0
    conditional_loss = 0.0
    expected_entry_cost = 0.0
    records = []

    for step in path:
        # --------------------------------------------------------
        # Routing regret
        # --------------------------------------------------------
        solution = solve_exact_hls(
            problem,
            initial_state=step.state,
        )

        q_values = solution.action_values
        optimal_q = max(q_values.values())
        chosen_q = q_values[step.operational_action]

        routing_regret = max(
            0.0,
            optimal_q - chosen_q,
        )

        # --------------------------------------------------------
        # Development regret conditional on realized opportunity
        # --------------------------------------------------------
        d_values = aia.development_values(
            problem,
            step.state,
            step.opportunity,
        )

        optimal_d = max(d_values.values())
        chosen_d = d_values[step.development_action]

        development_regret = max(
            0.0,
            optimal_d - chosen_d,
        )

        branch_probability = opportunity_branch_probability(
            world,
            step,
        )

        record = StepRegret(
            time=step.state.time,
            routing_regret=routing_regret,
            development_regret=development_regret,
            reach_probability_before=reach_probability,
            branch_probability=branch_probability,
        )

        records.append(record)

        conditional_loss += record.conditional_regret
        expected_entry_cost += record.expected_contribution

        reach_probability *= branch_probability

    return PathAudit(
        path_number=path_number,
        path_probability=reach_probability,
        conditional_loss=conditional_loss,
        expected_entry_cost=expected_entry_cost,
        step_regrets=tuple(records),
    )


def inversion_gain(world, state):
    """Best exact HLS advantage over every immediate-reward-optimal action."""
    problem = world.problem
    environment = problem.environment
    task = _task(problem, state)

    solution = solve_exact_hls(
        problem,
        initial_state=state,
    )

    rewards = {
        action: environment.reward.operational_reward(
            state,
            task,
            action,
        )
        for action in problem.operational_actions
    }

    best_reward = max(rewards.values())

    greedy = tuple(
        action
        for action, reward in rewards.items()
        if abs(reward - best_reward) <= EXACT_TOL
    )

    best_hls = max(solution.action_values.values())
    best_greedy_q = max(
        solution.action_values[action]
        for action in greedy
    )

    return best_hls - best_greedy_q


def print_path_audit(path, audit):
    for step, record in zip(path, audit.step_regrets):
        print(
            f"    t={record.time}: "
            f"a={step.operational_action}, "
            f"O={int(step.opportunity)}, "
            f"d={step.development_action}"
        )
        print(
            f"       P(reach before)={record.reach_probability_before:.12f} "
            f"P(O branch)={record.branch_probability:.12f}"
        )
        print(
            f"       routing_regret={record.routing_regret:.12f} "
            f"development_regret={record.development_regret:.12f}"
        )


def main():
    world = aia.build_world()
    problem = world.problem

    levels, paths_to = aia.physically_reachable_paths(world)

    inverted_states = []

    for time in range(problem.horizon):
        for state in levels[time].values():
            if aia.routing_inverted(world, state):
                inverted_states.append(state)

    print("RQ0 routing-inversion reachability-cost diagnostic")
    print("--------------------------------------------------")
    print("H=3, B=2, s=0.5, gamma=0, rho=0.5, eta=0.5")
    print()
    print(
        "NOTE: expected_entry_cost below is a path diagnostic, "
        "not yet the exact constrained value J^{->S}."
    )
    print()

    global_rows = []

    for index, target in enumerate(inverted_states, 1):
        paths = paths_to[aia.state_key(target)]

        audits = tuple(
            audit_path(world, n, path)
            for n, path in enumerate(paths, 1)
        )

        min_conditional = min(
            audits,
            key=lambda x: x.conditional_loss,
        )

        min_expected = min(
            audits,
            key=lambda x: x.expected_entry_cost,
        )

        gain = inversion_gain(world, target)

        print("=" * 78)
        print(
            f"INVERTED STATE {index}/{len(inverted_states)} "
            f"(t={target.time})"
        )
        print(f"competence={target.competence}")
        print(f"resources={target.resources}")
        print(f"physical paths={len(paths)}")
        print()
        print(f"local inversion gain = {gain:.12f}")
        print()

        print("Minimum conditional-loss path")
        print("-----------------------------")
        print(
            f"path #{min_conditional.path_number}: "
            f"conditional_loss="
            f"{min_conditional.conditional_loss:.12f}, "
            f"path_probability="
            f"{min_conditional.path_probability:.12f}, "
            f"expected_entry_cost="
            f"{min_conditional.expected_entry_cost:.12f}"
        )

        print_path_audit(
            paths[min_conditional.path_number - 1],
            min_conditional,
        )

        print()
        print("Minimum probability-weighted entry-cost path")
        print("--------------------------------------------")
        print(
            f"path #{min_expected.path_number}: "
            f"conditional_loss="
            f"{min_expected.conditional_loss:.12f}, "
            f"path_probability="
            f"{min_expected.path_probability:.12f}, "
            f"expected_entry_cost="
            f"{min_expected.expected_entry_cost:.12f}"
        )

        print_path_audit(
            paths[min_expected.path_number - 1],
            min_expected,
        )

        print()

        ratio_conditional = (
            gain / min_conditional.conditional_loss
            if min_conditional.conditional_loss > EXACT_TOL
            else float("inf")
        )

        ratio_expected = (
            gain / min_expected.expected_entry_cost
            if min_expected.expected_entry_cost > EXACT_TOL
            else float("inf")
        )

        print(
            "gain / min conditional loss = "
            f"{ratio_conditional:.12f}"
        )
        print(
            "gain / min expected entry cost = "
            f"{ratio_expected:.12f}"
        )
        print()

        global_rows.append(
            (
                index,
                gain,
                min_conditional.conditional_loss,
                min_expected.expected_entry_cost,
                ratio_conditional,
                ratio_expected,
            )
        )

    print("=" * 78)
    print("SUMMARY")
    print("-------")
    print(
        f"{'state':>5} "
        f"{'gain':>14} "
        f"{'min_cond_loss':>16} "
        f"{'min_exp_cost':>16} "
        f"{'gain/cond':>14} "
        f"{'gain/exp':>14}"
    )
    print("-" * 88)

    for row in global_rows:
        (
            index,
            gain,
            cond,
            exp,
            ratio_cond,
            ratio_exp,
        ) = row

        print(
            f"{index:>5} "
            f"{gain:>14.10f} "
            f"{cond:>16.10f} "
            f"{exp:>16.10f} "
            f"{ratio_cond:>14.10f} "
            f"{ratio_exp:>14.10f}"
        )

    print()
    print("Interpretation guard")
    print("--------------------")
    print(
        "These costs diagnose how expensive the physical paths to the "
        "inverted states are relative to exact HLS choices."
    )
    print(
        "They must NOT yet be called the exact constrained reachability "
        "cost C_reach(S)=J_HLS-J^{->S}."
    )
    print(
        "If this diagnostic confirms a large barrier, the next step is "
        "to formulate and solve that constrained dynamic program exactly."
    )


if __name__ == "__main__":
    main()
