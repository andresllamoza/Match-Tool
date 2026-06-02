import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.lookup_log import append_lookup_attempt, read_lookup_attempts
from src.matcher import MatchResult


class LookupLogTest(unittest.TestCase):
    def test_append_lookup_attempt_records_top_result_reason(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "attempts.csv"
            result = MatchResult(
                employer_query="Acme",
                matched_employer_name="ACME INC",
                recordkeeper="Fidelity Investments",
                confidence=1.0,
                plan_name="ACME 401K PLAN",
                plan_year=2023,
                plan_participants=1000,
                ein="12-3456789",
                match_method="exact_normalized",
                match_reason="The normalized input exactly matched the normalized DOL employer name.",
            )

            append_lookup_attempt("Acme", [result], log_path=log_path)
            attempts = read_lookup_attempts(log_path=log_path)

            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts.loc[0, "input_name"], "Acme")
            self.assertEqual(attempts.loc[0, "matched_employer"], "ACME INC")
            self.assertEqual(attempts.loc[0, "match_method"], "exact_normalized")
            self.assertIn("exactly matched", attempts.loc[0, "match_reason"])

    def test_append_lookup_attempt_records_no_match_reason(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "attempts.csv"

            append_lookup_attempt("Unknown Employer", [], log_path=log_path)
            attempts = read_lookup_attempts(log_path=log_path)

            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts.loc[0, "found"], "False")
            self.assertEqual(attempts.loc[0, "match_method"], "no_match")
            self.assertIn("No candidate cleared", attempts.loc[0, "match_reason"])


class MatcherReasonTest(unittest.TestCase):
    def setUp(self):
        from src import matcher

        self.matcher = matcher
        self.original_cache = matcher._DATAFRAME_CACHE
        employer_norm = matcher.canonicalize_employer("Acme Inc")
        matcher._DATAFRAME_CACHE = pd.DataFrame(
            [
                {
                    "EMPLOYER": "ACME INC",
                    "EMPLOYER_NORM": employer_norm,
                    "EMPLOYER_COLLAPSED": employer_norm.replace(" ", ""),
                    "RK_RAW": "FIDELITY INVESTMENTS",
                    "RK_CANON": "Fidelity Investments",
                    "TIER": "TIER1",
                    "YEAR": "2023",
                    "_n": 1000,
                    "_tier_rank": 1,
                    "PLAN_NAME": "ACME 401K PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                    "TOT_PARTCP_BOY_CNT": "1000",
                    "SPONS_DFE_EIN": "12-3456789",
                }
            ]
        )

    def tearDown(self):
        self.matcher._DATAFRAME_CACHE = self.original_cache

    def test_match_includes_reason_for_selected_candidate(self):
        results = self.matcher.match("Acme Inc", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].match_method, "exact_normalized")
        self.assertIn("exactly matched", results[0].match_reason)


if __name__ == "__main__":
    unittest.main()
