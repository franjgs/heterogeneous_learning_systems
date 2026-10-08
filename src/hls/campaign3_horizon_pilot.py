"""Pure pre-execution definitions for the Campaign 3 horizon pilot.

This module allocates identifiers and random streams only.  It does not
generate problem histories or invoke an HLS policy, agent, or production
function.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


PROTOCOL_ID = "campaign3_horizon_pilot_v1"
S_PILOT = ("G00", "G04", "G05", "G07", "F01", "F02", "F03", "F04")
J_PILOT = 12
NESTED_WINDOWS = (2, 5, 11)
INITIAL_REPLICATES = tuple(range(5))
RESERVED_REPLICATES = tuple(range(5, 10))
INTERVENTION_MODES = ("Q00", "Q10", "Q01", "Q11")
CONTINUATION_PROBES = ("Q00", "Q11")
FACTUAL_STATE_SOURCE = "Q11"
BOOTSTRAP_REPLICATES = 2_000
BOOTSTRAP_SEED = 20261013
TEMPORAL_EXTENSION_SEQUENCE = (12, 18, 24)
TERMINAL_OUTCOME = "HORIZON UNRESOLVED"
SEED_DOMAIN = "uint32"
KNOWN_PRIOR_C3_SEEDS = frozenset({20261008, 20261009, 20261010, 20261011, 20261012})
EXOGENOUS_STREAMS = ("physical_problem", "observation_noise", "other_exogenous")


def _digest(parts: tuple[object, ...]) -> bytes:
    """Return a stable digest of a typed, unambiguous JSON payload."""

    payload = json.dumps(parts, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).digest()


def base_history_identity(team_id: str, kernel_id: str, replicate: int) -> str:
    """Content identity for one future base history without generating it."""

    return hashlib.sha256(
        json.dumps(
            (PROTOCOL_ID, "base_history", team_id, kernel_id, replicate),
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def simulation_seed(team_id: str, kernel_id: str, replicate: int) -> int:
    """Map a pilot tuple deterministically into NumPy's uint32 seed domain."""

    if replicate not in INITIAL_REPLICATES + RESERVED_REPLICATES:
        raise ValueError("replicate must be one of the frozen indices 0..9")
    return int.from_bytes(
        _digest((PROTOCOL_ID, "simulation_seed", team_id, kernel_id, replicate))[:4],
        byteorder="big",
        signed=False,
    )


def exogenous_stream_seed(base_seed: int, stream: str) -> int:
    """Derive a mode-independent CRN substream seed from a base-history seed."""

    if stream not in EXOGENOUS_STREAMS:
        raise ValueError(f"unknown exogenous stream: {stream}")
    return int.from_bytes(
        _digest((PROTOCOL_ID, "exogenous_stream", int(base_seed), stream))[:4],
        byteorder="big",
        signed=False,
    )


def eligible_for_horizon(problem_index: int, ell: int, *, total_problems: int = J_PILOT) -> bool:
    """Return the frozen one-indexed censoring rule j(t)+ell <= J."""

    if not 1 <= problem_index <= total_problems:
        raise ValueError("problem_index must be one-indexed within the history")
    if ell < 0:
        raise ValueError("ell must be nonnegative")
    return problem_index + ell <= total_problems


def common_support_problem_indices(window: int, *, total_problems: int = J_PILOT) -> tuple[int, ...]:
    """Problem indices eligible for every ell in 0..window."""

    if window < 0:
        raise ValueError("window must be nonnegative")
    return tuple(j for j in range(1, total_problems + 1) if eligible_for_horizon(j, window, total_problems=total_problems))


@dataclass(frozen=True)
class SeedAllocation:
    team_id: str
    kernel_id: str
    replicate: int
    allocation: str
    base_history_id: str
    simulator_seed: int
    physical_problem_seed: int
    observation_noise_seed: int
    other_exogenous_seed: int


def allocate_seed(team_id: str, kernel_id: str, replicate: int) -> SeedAllocation:
    """Construct one declarative seed record; no random draw is made."""

    seed = simulation_seed(team_id, kernel_id, replicate)
    allocation = "initial" if replicate in INITIAL_REPLICATES else "reserved_5_to_10"
    return SeedAllocation(
        team_id=team_id,
        kernel_id=kernel_id,
        replicate=replicate,
        allocation=allocation,
        base_history_id=base_history_identity(team_id, kernel_id, replicate),
        simulator_seed=seed,
        physical_problem_seed=exogenous_stream_seed(seed, "physical_problem"),
        observation_noise_seed=exogenous_stream_seed(seed, "observation_noise"),
        other_exogenous_seed=exogenous_stream_seed(seed, "other_exogenous"),
    )
