import unittest

from src.matcher import batch_match_top_results, canonicalize_employer, match


class McDonaldsMatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.matcher import load_dol_data

        load_dol_data()

    def test_apostrophe_canonicalizes_to_mcdonalds_not_mcdonald_s(self):
        self.assertEqual(canonicalize_employer("McDonald's"), "MCDONALDS")
        self.assertEqual(canonicalize_employer("McDonald's Corporation"), "MCDONALDS")

    def test_match_mcdonalds_apostrophe_returns_empower(self):
        results = match("McDonald's", top_n=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].recordkeeper, "Empower")
        self.assertIn("MCDONALDS CORPORATION", results[0].matched_employer_name)
        self.assertEqual(results[0].match_method, "curated_override")

    def test_batch_mcdonalds_returns_empower(self):
        results = batch_match_top_results(["McDonald's", "McDonalds"])
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIsNotNone(result)
            self.assertEqual(result.recordkeeper, "Empower")
            self.assertNotIn("Ameritas", result.recordkeeper)


if __name__ == "__main__":
    unittest.main()
