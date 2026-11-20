import unittest

import numpy as np

from studies.soc_triage_feasibility_frontier.analyze_feasibility import (
    aggregate_splus,
    paired_bootstrap_splus,
    point_admissible,
    reconstruct_timely_numerator,
    status_for,
    supported_admissible,
)


def episode(needs, timely_rate, tp, fn):
    return {"true_need_count": str(needs),
            "necessary_L2_timely_per_need": str(timely_rate),
            "TP_count": str(tp), "FN_count": str(fn)}


class FeasibilityMetricTests(unittest.TestCase):
    def test_zero_positive_seed_does_not_receive_mean_zero_weight(self):
        rows = [episode(0, 0.0, 0, 0), episode(4, 0.5, 3, 1)]
        result = aggregate_splus(rows)
        self.assertEqual(result["timely_need_numerator"], 2)
        self.assertEqual(result["total_need_denominator"], 4)
        self.assertEqual(result["S_plus"], 0.5)
        self.assertNotEqual(result["S_plus"], np.mean([0.0, 0.5]))

    def test_reconstruct_count_and_include_false_negatives_in_denominator(self):
        row = episode(10, 0.3, 5, 5)
        self.assertEqual(reconstruct_timely_numerator(row), 3)
        result = aggregate_splus([row])
        self.assertEqual(result["total_need_denominator"], 10)
        self.assertEqual(result["FN_count"], 5)
        self.assertEqual(result["S_plus"], 0.3)
        self.assertEqual(result["pD_empirical_pooled"], 0.5)
        self.assertLessEqual(result["S_plus"], result["pD_empirical_pooled"])

    def test_inconsistent_denominator_and_timely_greater_than_tp_fail(self):
        with self.assertRaises(ValueError):
            aggregate_splus([episode(10, 0.6, 5, 5)])
        with self.assertRaises(ValueError):
            aggregate_splus([episode(10, 0.2, 5, 4)])

    def test_policy_bootstrap_is_paired_and_reproducible(self):
        den = np.array([0, 2, 3, 1], dtype=np.int64)
        nums = {"D1": np.array([0, 1, 1, 0]),
                "P1": np.array([0, 1, 2, 1]),
                "HLS-B": np.array([0, 2, 2, 1])}
        dens = {policy: den.copy() for policy in nums}
        draws = np.random.default_rng(17).integers(0, 4, size=(500, 4))
        a = paired_bootstrap_splus(nums, dens, draws)
        b = paired_bootstrap_splus(nums, dens, draws.copy())
        self.assertEqual(a[2], b[2])
        for policy in nums:
            np.testing.assert_array_equal(a[0][policy], b[0][policy])
        for contrast in ("WAPS-D1", "P1-D1", "WAPS-P1"):
            np.testing.assert_array_equal(a[1][contrast], b[1][contrast])
        self.assertGreaterEqual(a[2], 0)

    def test_paired_bootstrap_rejects_policy_denominator_mismatch(self):
        nums = {"D1": np.array([1, 1]), "P1": np.array([1, 1]), "HLS-B": np.array([1, 1])}
        dens = {"D1": np.array([1, 2]), "P1": np.array([1, 2]), "HLS-B": np.array([1, 3])}
        with self.assertRaises(ValueError):
            paired_bootstrap_splus(nums, dens, np.array([[0, 1]]))

    def test_constraint_tightening_cannot_enlarge_point_or_supported_set(self):
        grid = [(d, rho, s) for d in (0.6, 0.8, 1.0)
                for rho in (0.5, 0.8, 1.2) for s in (0.4, 0.7, 0.95)]
        for d_loose, rho_loose, s_loose in grid:
            loose_point = point_admissible(.85,.75,.74,d_loose,rho_loose,s_loose)
            loose_supported = supported_admissible(.85,.75,.72,d_loose,rho_loose,s_loose)
            for d_tight, rho_tight, s_tight in grid:
                if d_tight >= d_loose and rho_tight <= rho_loose and s_tight >= s_loose:
                    tight_point = point_admissible(.85,.75,.74,d_tight,rho_tight,s_tight)
                    tight_supported = supported_admissible(.85,.75,.72,d_tight,rho_tight,s_tight)
                    self.assertFalse(tight_point and not loose_point)
                    self.assertFalse(tight_supported and not loose_supported)
        self.assertEqual(status_for(True, True, .72, .69, .74, .70), "point_admissible_uncertain")
        self.assertEqual(status_for(True, False, .9, .8, .95, .7), "inadmissible_capacity")


if __name__ == "__main__":
    unittest.main()
