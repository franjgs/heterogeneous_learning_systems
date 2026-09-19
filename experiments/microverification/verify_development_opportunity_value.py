"""Grid verification for development-opportunity value identities.

This is a numerical audit of exact, documented DERIVED-IN-MODEL identities.
It writes no result artifacts and is not empirical HLS evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from hls.development_opportunity_value import (
    cross_difference,
    gamma_comp_closed,
    gamma_sub_closed,
    mixed_gamma,
    value_comp,
    value_sub,
)


GRID = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
TOLERANCE = 1e-12


def audit() -> dict[str, float | int]:
    """Exhaustively check signs and closed forms over the declared small grid."""
    checked = 0
    strict_both = 0
    for h in GRID:
        for s1 in GRID:
            for s2 in GRID:
                for delta1 in GRID:
                    for delta2 in GRID:
                        gamma_sub = cross_difference(value_sub, s1, s2, delta1, delta2, h)
                        gamma_comp = cross_difference(value_comp, s1, s2, delta1, delta2, h)
                        assert gamma_sub <= TOLERANCE
                        assert gamma_comp >= -TOLERANCE
                        assert abs(gamma_sub - gamma_sub_closed(s1, s2, delta1, delta2, h)) <= TOLERANCE
                        assert abs(gamma_comp - gamma_comp_closed(s1, s2, delta1, delta2, h)) <= TOLERANCE
                        checked += 1
                        if gamma_sub < -TOLERANCE and gamma_comp > TOLERANCE:
                            p_star = gamma_comp / (gamma_comp + abs(gamma_sub))
                            assert mixed_gamma(gamma_sub, gamma_comp, p_star - 0.01) > TOLERANCE
                            assert abs(mixed_gamma(gamma_sub, gamma_comp, p_star)) <= TOLERANCE
                            assert mixed_gamma(gamma_sub, gamma_comp, p_star + 0.01) < -TOLERANCE
                            strict_both += 1
    return {
        "grid_cases": checked,
        "mixed_sign_reversal_cases": strict_both,
        "tolerance": TOLERANCE,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
