"""Run exactly the nine preregistered RQ0-A/B configurations.

No parameter search, refinement, plotting, or interpretation is performed.
"""

from __future__ import annotations

from dataclasses import dataclass

from hls.synthetic.exact import (
    solve_exact_hls,
    solve_exact_sep_omega,
    solve_exact_strong_sep,
)
from hls.synthetic.rq0_campaign import worlds


@dataclass(frozen=True)
class CampaignResult:
    name: str
    j_hls: float
    j_sep_min: float
    j_sep_max: float
    j_sep_omega: float
    delta_j_cons: float
    delta_omega: float


def evaluate_world(world) -> CampaignResult:
    hls = solve_exact_hls(
        world.problem,
        initial_state=world.initial_state,
    )
    sep = solve_exact_strong_sep(
        world.problem,
        initial_state=world.initial_state,
    )
    omega = solve_exact_sep_omega(
        world.problem,
        initial_state=world.initial_state,
    )

    return CampaignResult(
        name=world.configuration.name,
        j_hls=hls.value,
        j_sep_min=sep.value_min,
        j_sep_max=sep.value_max,
        j_sep_omega=omega.value,
        delta_j_cons=hls.value - sep.value_max,
        delta_omega=hls.value - omega.value,
    )


def run_campaign() -> tuple[CampaignResult, ...]:
    return tuple(evaluate_world(world) for world in worlds())


def main() -> None:
    results = run_campaign()

    header = (
        f"{'configuration':<16}"
        f"{'J_HLS':>12}"
        f"{'J_SEP_min':>12}"
        f"{'J_SEP_max':>12}"
        f"{'J_SEP-Omega':>14}"
        f"{'Delta_J_cons':>14}"
        f"{'Delta_Omega':>14}"
    )
    print(header)
    print("-" * len(header))

    for r in results:
        print(
            f"{r.name:<16}"
            f"{r.j_hls:12.8f}"
            f"{r.j_sep_min:12.8f}"
            f"{r.j_sep_max:12.8f}"
            f"{r.j_sep_omega:14.8f}"
            f"{r.delta_j_cons:14.8f}"
            f"{r.delta_omega:14.8f}"
        )


if __name__ == "__main__":
    main()
