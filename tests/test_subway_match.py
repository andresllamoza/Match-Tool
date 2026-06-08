import unittest

from src.matcher import batch_match_top_results, match


class SubwayMatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.matcher import load_dol_data

        load_dol_data()

    def test_match_subway_returns_corporate_plan_not_development(self):
        results = match("Subway", top_n=3)
        self.assertGreaterEqual(len(results), 1)
        top = results[0]
        self.assertEqual(top.match_method, "brand_alias")
        self.assertIn("FRANCHISE WORLD HEADQUARTERS", top.matched_employer_name)
        self.assertIn("SUBWAY 401", top.plan_name.upper())
        self.assertNotIn("DEVELOPMENT", top.matched_employer_name.upper())

    def test_batch_subway_returns_corporate_plan(self):
        results = batch_match_top_results(["Subway"])
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertIsNotNone(result)
        self.assertIn("FRANCHISE WORLD HEADQUARTERS", result.matched_employer_name)
        self.assertNotIn("DEVELOPMENT", result.matched_employer_name.upper())


if __name__ == "__main__":
    unittest.main()
