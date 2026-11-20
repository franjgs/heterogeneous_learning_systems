import unittest

from studies.soc_triage_classifier_operating_impact.run_phase2 import (
    _is_dominated, _points, _statistical_pareto,
)


class Phase2AnalysisTests(unittest.TestCase):
    def test_published_operating_points_and_ba(self):
        points = _points()
        self.assertEqual(len(points), 25)
        self.assertEqual(sum(p["label_definition"] == "original" for p in points), 10)
        self.assertEqual(sum(p["label_definition"] == "standardized" for p in points), 15)
        for point in points:
            expected = (1 - point["pFA"] + point["pD"]) / 2
            self.assertAlmostEqual(point["BA_recomputed"], expected, places=12)

    def test_pareto_frontier_keeps_label_definitions_separate(self):
        rows = _statistical_pareto(_points())
        frontier = {(r["label_definition"], r["id"]) for r in rows if not r["dominated"]}
        self.assertEqual(frontier, {
            ("original", "orig_lr_ac"),
            ("original", "orig_rf_ac"),
            ("original", "orig_bayesian_mlp_ac"),
            ("standardized", "std_lr_ac"),
            ("standardized", "std_bayesian_mlp_ac"),
            ("standardized", "std_lightgbm_ac"),
            ("standardized", "std_lightgbm_c"),
        })

    def test_dominance_requires_nonworse_rates_and_one_strict_rate(self):
        a = {"id": "a", "pD": .9, "pFA": .1}
        same = {"id": "b", "pD": .9, "pFA": .1}
        worse = {"id": "c", "pD": .8, "pFA": .2}
        self.assertFalse(_is_dominated(a, [a, same]))
        self.assertTrue(_is_dominated(worse, [a, worse]))
        self.assertFalse(_is_dominated(a, [a, worse]))


if __name__ == "__main__":
    unittest.main()
