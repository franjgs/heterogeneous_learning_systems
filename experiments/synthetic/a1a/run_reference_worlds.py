"""Print exact A1a reference-world acceptance diagnostics without artifacts."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.a1a import (  # noqa: E402
    DevelopmentAction,
    Learner,
    reference_diagnostics,
    reference_worlds,
    solve_hls,
    solve_sep_omega,
    solve_strong_sep,
)


def _actions(actions: frozenset[Learner]) -> str:
    return ",".join(sorted(action.value for action in actions))


def _development(actions: frozenset[DevelopmentAction]) -> str:
    labels = []
    for action in actions:
        if action.is_null:
            labels.append("null")
        else:
            labels.append(f"develop {action.recipient.value}/task{action.task}")
    return ",".join(sorted(labels))


def main() -> None:
    headers = (
        "world",
        "rho",
        "eta",
        "N",
        "D",
        "delta_R",
        "delta_G",
        "J_SEP",
        "J_HLS",
        "J_SEP_Omega",
        "HLS actions",
        "development actions",
    )
    rows = []
    for name, world in reference_worlds().items():
        hls = solve_hls(world)
        sep = solve_strong_sep(world)
        diagnostics = reference_diagnostics(world)
        sep_omega = solve_sep_omega(world) if name == "F" else None
        sep_value = (
            f"{sep.value:.12g}"
            if sep.value is not None
            else f"[{sep.value_min:.12g},{sep.value_max:.12g}]"
        )
        rows.append(
            (
                name,
                f"{world.rho:.12g}",
                f"{world.eta:.12g}",
                f"{hls.no_opportunity_value:.12g}",
                f"{hls.opportunity_value:.12g}",
                f"{diagnostics['delta_R']:.12g}",
                f"{diagnostics['delta_G']:.12g}",
                sep_value,
                f"{hls.optimal_value:.12g}",
                "" if sep_omega is None else f"{sep_omega.optimal_value:.12g}",
                _actions(hls.optimal_operational_actions),
                _development(hls.optimal_development_actions),
            )
        )

    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    print("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


if __name__ == "__main__":
    main()
