"""Pre-results Campaign 1 execution protocol constants.

This module references the frozen test-range fixture and contains no execution
loop.  Importing it cannot run a team or create performance artifacts.
"""

from __future__ import annotations

from .campaign1_test_range import (
    CONTAMINATION_STATUS,
    FUTURE_ETA,
    HISTORIES,
    INTENDED_CONTRASTS,
)
from .discover_v0 import DEFAULT_HORIZON, DEFAULT_SIGMA, N_AGENTS, N_CAPABILITIES, RHO


PROTOCOL_ID = "campaign1-execution-protocol-v1"
SOURCE_TEST_RANGE_COMMIT = "05b86cb"
SCENARIO_IDS = tuple(HISTORIES)
CONFIGURATION_IDS = ("G00", "G04", "G05", "G07")
SEEDS = tuple(range(10))
CONDITIONS = ("FULL", "NO-DEVELOP", "KNOWN-Z")

PARAMETERS = {
    "N": N_AGENTS,
    "K": N_CAPABILITIES,
    "rho": RHO,
    "sigma": DEFAULT_SIGMA,
    "eta": FUTURE_ETA,
    "horizon_per_problem": DEFAULT_HORIZON,
}

CONDITION_SEMANTICS = {
    "FULL": {
        "problem_knowledge": "finite Bayesian DISCOVER",
        "development": True,
        "selector": "finite_choose_dynamic_action_v2(develop=True)",
        "existing_control": "DISCOVER_DEVELOP",
    },
    "NO-DEVELOP": {
        "problem_knowledge": "finite Bayesian DISCOVER",
        "development": False,
        "selector": "finite_choose_dynamic_action_v2(develop=False)",
        "existing_control": "existing dynamic-MPC primitive; execution adapter required",
        "warning": "do not substitute historical DISCOVER_ONLY, which uses the fixed-state DP controller",
    },
    "KNOWN-Z": {
        "problem_knowledge": "true z supplied directly to the existing known oracle",
        "development": True,
        "selector": "_known_dynamic_action_v2(develop=True)",
        "existing_control": "DEVELOP_KNOWN",
    },
}

CRN_POLICY = (
    "Use the same seed for every matched scenario x configuration x condition. "
    "The Gaussian standard-normal draw stream is shared by run key; true means "
    "may differ, and observations are irrelevant to KNOWN-Z decisions."
)

RETAINED_TRAJECTORY_VARIABLES = (
    "true problem z_t",
    "problem descriptors C_t/N_t/M_t",
    "belief before/after where applicable",
    "assignment/action X_t",
    "cumulative continuous exposure E_t",
    "capability state S_t before/after",
    "true expected production mu_true",
    "observed noisy reward",
)

PRIMARY_OUTPUTS = (
    "performance trajectory",
    "cumulative performance",
    "assignment trajectory",
    "exposure trajectory",
    "capability trajectory",
    "response to recurrence/familiar return",
    "configuration sensitivity/insensitivity",
    "FULL versus NO-DEVELOP diagnostic",
    "FULL versus KNOWN-Z diagnostic",
)

EMPIRICALLY_UNKNOWN = (
    "which configuration performs best",
    "whether rankings change",
    "whether adaptation is valuable in any particular scenario",
    "whether adaptation matters little",
    "whether previous development helps",
    "whether previous development becomes a liability",
    "whether a scenario is configuration-sensitive",
    "whether a scenario is configuration-insensitive",
    "whether TR-G is harder than TR-J",
    "whether TR-R is harder than TR-D",
    "whether TR-HA or TR-HB is preferable",
    "whether any history produces path dependence",
    "whether any scenario discriminates future strategies",
)

ASSESSMENT_CRITERIA = {
    "PASS": (
        "The predefined range generates multiple qualitatively different, interpretable adaptive demands "
        "that plausibly provide a useful range for later strategy discrimination, without collapsing to a "
        "single scalar ordering such as more change equals harder. Coverage is assessed across the range; "
        "neither universal cumulative leadership nor multiple scenario winners determines PASS alone."
    ),
    "PARTIAL": (
        "Meaningful and interpretable variation is present, but important predefined scenario classes "
        "collapse onto essentially the same adaptive challenge. Preserve the result and identify what is "
        "missing before Campaign 2; do not add physics to rescue it."
    ),
    "FAIL": (
        "The supposedly different scenarios generate essentially the same adaptive problem, or observed "
        "differences are dominated by artifacts of the frozen implementation rather than problem/environment "
        "structure. Preserve the negative result and do not modify the model to rescue it."
    ),
}

PERFORMANCE_DEFINITION = (
    "Performance is true expected/latent production mu_true. Observed noisy reward drives Bayesian inference "
    "where applicable and is retained, but is not substituted for performance."
)

RUNS_PER_CONDITION = len(SCENARIO_IDS) * len(CONFIGURATION_IDS) * len(SEEDS)
TOTAL_RUNS = RUNS_PER_CONDITION * len(CONDITIONS)
TEAM_EXECUTIONS = 0
PERFORMANCE_ARTIFACTS = 0
TRAJECTORY_ARTIFACTS = 0


def validate_protocol() -> None:
    if SOURCE_TEST_RANGE_COMMIT != "05b86cb":
        raise AssertionError("test-range provenance changed")
    if SCENARIO_IDS != tuple(HISTORIES) or len(SCENARIO_IDS) != 8:
        raise AssertionError("protocol must reference exactly the frozen eight scenarios")
    if CONFIGURATION_IDS != ("G00", "G04", "G05", "G07"):
        raise AssertionError("probe configurations changed")
    if SEEDS != tuple(range(10)) or CONDITIONS != ("FULL", "NO-DEVELOP", "KNOWN-Z"):
        raise AssertionError("seeds or conditions changed")
    if PARAMETERS != {"N": 3, "K": 2, "rho": 0.5, "sigma": 0.10, "eta": 0.35, "horizon_per_problem": 3}:
        raise AssertionError("frozen parameters changed")
    if RUNS_PER_CONDITION != 320 or TOTAL_RUNS != 960:
        raise AssertionError("run matrix changed")
    if set(INTENDED_CONTRASTS) != {
        "persistence_representation", "ordered_displacement",
        "recurrence_displacement", "developmental_history_return",
    }:
        raise AssertionError("controlled contrasts changed")
    if TEAM_EXECUTIONS or PERFORMANCE_ARTIFACTS or TRAJECTORY_ARTIFACTS:
        raise AssertionError("protocol freeze must contain no execution/results")
