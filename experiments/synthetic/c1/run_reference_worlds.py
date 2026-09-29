#!/usr/bin/env python
"""Print the exact C1 reference-world acceptance table."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from hls.synthetic.c1 import evaluate_world, reference_worlds


def main() -> None:
    print("world\ti\tii\tiii\tgenuine\tJ_HLS\tJ_SEP_min\tJ_SEP_max\tDelta_cons\tJ_SEP_Omega")
    for name, world in reference_worlds().items():
        result = evaluate_world(world)
        print(
            f"{name}\t{result.links.state_effect}\t{result.links.decision_effect}\t"
            f"{result.links.second_order_effect}\t{result.links.genuine}\t"
            f"{result.hls.value:.12g}\t{result.sep.value_min:.12g}\t"
            f"{result.sep.value_max:.12g}\t{result.delta_j_cons:.12g}\t"
            f"{result.sep_omega.value:.12g}"
        )


if __name__ == "__main__":
    main()
