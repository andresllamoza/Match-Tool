import time
import unittest
from pathlib import Path

import pandas as pd

from src.matcher import batch_match_top_results, load_dol_data, match

FORTUNE_CSV = Path(
    "/home/ubuntu/.cursor/projects/workspace/uploads/Fortune1000__1__a7a9.csv"
)
from src.batch_columns import detect_employer_column


class BatchMatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dol_data()

    def test_batch_match_fortune_style_names(self):
        names = [
            "Microsoft",
            "Walmart",
            "Amazon",
            "Apple",
            "Nike",
            "Target",
            "Bank of America",
            "Citi",
        ]
        results = batch_match_top_results(names)
        self.assertEqual(len(results), len(names))
        nike_index = names.index("Nike")
        self.assertIsNotNone(results[nike_index])
        self.assertEqual(
            results[nike_index].recordkeeper,
            "Fidelity Workplace Services, LLC",
        )

    def test_fortune_brand_aliases_and_jpm_override(self):
        """Five demo employers: aliases to DOL rows + JPMC Empower override."""
        cases = [
            ("Alphabet", "Vanguard", "GOOGLE"),
            ("JP Morgan Chase", "Empower", "JPMORGAN CHASE BANK"),
            ("Fannie Mae", "Fidelity Investments", "FEDERAL NATIONAL MORTGAGE"),
            ("State Farm Insurance Cos.", "Alight", "STATE FARM MUTUAL"),
            ("Express Scripts Holding", "Empower", "CIGNA"),
            ("McDonald's", "Empower", "MCDONALDS CORPORATION"),
            ("McDonalds", "Empower", "MCDONALDS CORPORATION"),
            ("McDonald's Corporation", "Empower", "MCDONALDS CORPORATION"),
            ("Subway", "Newport", "FRANCHISE WORLD HEADQUARTERS"),
        ]
        for query, expected_rk, employer_fragment in cases:
            results = match(query, top_n=1)
            self.assertGreaterEqual(len(results), 1, msg=query)
            top = results[0]
            self.assertIn(expected_rk, top.recordkeeper, msg=query)
            self.assertIn(
                employer_fragment.upper(),
                top.matched_employer_name.upper(),
                msg=query,
            )

    def test_batch_match_100_rows_under_30_seconds(self):
        names = [
            "Microsoft",
            "Walmart",
            "Amazon",
            "Apple",
            "Google",
            "Nike",
            "Target",
            "Disney",
            "Bank of America",
            "Citi",
        ] * 10
        started = time.perf_counter()
        results = batch_match_top_results(names)
        elapsed = time.perf_counter() - started
        self.assertEqual(len(results), 100)
        self.assertLess(elapsed, 30.0, f"batch took {elapsed:.1f}s")

    def test_single_match_still_skips_fuzzy_on_exact(self):
        started = time.perf_counter()
        results = match("Microsoft", top_n=1)
        elapsed = time.perf_counter() - started
        self.assertEqual(len(results), 1)
        self.assertLess(elapsed, 0.25, f"exact match took {elapsed:.2f}s")

    @unittest.skipUnless(FORTUNE_CSV.exists(), "Fortune 1000 sample CSV not available")
    def test_fortune_1000_batch_under_90_seconds(self):
        uploaded = pd.read_csv(FORTUNE_CSV, dtype=str).fillna("")
        employer_column = detect_employer_column(list(uploaded.columns))
        self.assertEqual(employer_column.lower(), "name")
        names = uploaded[employer_column].astype(str).tolist()
        self.assertEqual(len(names), 1000)

        started = time.perf_counter()
        results = batch_match_top_results(names)
        elapsed = time.perf_counter() - started
        matched = sum(1 for result in results if result and result.recordkeeper)
        self.assertEqual(len(results), 1000)
        self.assertGreater(matched, 700)
        self.assertLess(elapsed, 90.0, f"1000-row batch took {elapsed:.1f}s")


if __name__ == "__main__":
    unittest.main()
