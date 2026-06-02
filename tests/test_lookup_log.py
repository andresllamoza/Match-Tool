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
        amazon_norm = matcher.canonicalize_employer("Amazon.com Services, LLC")
        bofa_norm = matcher.canonicalize_employer("Bank of America Corporation")
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
                },
                {
                    "EMPLOYER": "AMAZON.COM SERVICES, LLC",
                    "EMPLOYER_NORM": amazon_norm,
                    "EMPLOYER_COLLAPSED": amazon_norm.replace(" ", ""),
                    "RK_RAW": "FIDELITY INVESTMENTS INSTITUTIONAL",
                    "RK_CANON": "Fidelity Investments",
                    "TIER": "TIER1",
                    "YEAR": "2023",
                    "_n": 1214063,
                    "_tier_rank": 1,
                    "PLAN_NAME": "A SINGLE-EMPLOYER PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                    "TOT_PARTCP_BOY_CNT": "1214063",
                    "SPONS_DFE_EIN": "91-1986545",
                },
                {
                    "EMPLOYER": "BANK OF AMERICA CORPORATION",
                    "EMPLOYER_NORM": bofa_norm,
                    "EMPLOYER_COLLAPSED": bofa_norm.replace(" ", ""),
                    "RK_RAW": "FIDELITY INVESTMENTS INST. OPS. CO.",
                    "RK_CANON": "Fidelity Investments",
                    "TIER": "TIER1",
                    "YEAR": "2023",
                    "_n": 200581,
                    "_tier_rank": 1,
                    "PLAN_NAME": "THE BANK OF AMERICA PENSION PLAN",
                    "TYPE_PENSION_BNFT_CODE": "1A1C1I3H",
                    "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                    "TOT_PARTCP_BOY_CNT": "200581",
                    "SPONS_DFE_EIN": "560906609",
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

    def test_match_finds_amazon_brand_query_in_legal_employer_name(self):
        results = self.matcher.match("amazon", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "AMAZON.COM SERVICES, LLC")
        self.assertEqual(results[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(results[0].match_method, "word_boundary")

    def test_suggest_employers_returns_existing_partial_matches(self):
        suggestions = self.matcher.suggest_employers("ama", limit=3)

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].employer_name, "AMAZON.COM SERVICES, LLC")
        self.assertEqual(suggestions[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(suggestions[0].match_method, "prefix")

    def test_suggest_employers_skips_short_queries(self):
        suggestions = self.matcher.suggest_employers("am", limit=3)

        self.assertEqual(suggestions, [])

    def test_suggest_employers_returns_related_token_matches(self):
        suggestions = self.matcher.suggest_employers("america", limit=3)

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].employer_name, "BANK OF AMERICA CORPORATION")
        self.assertEqual(suggestions[0].match_method, "contains")

    def test_match_overrides_bank_of_america_pension_row_to_merrill(self):
        results = self.matcher.match("bank of america", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "BANK OF AMERICA CORPORATION")
        self.assertEqual(results[0].recordkeeper, "Merrill Lynch")
        self.assertEqual(results[0].plan_name, "THE BANK OF AMERICA 401(K) PLAN")
        self.assertEqual(results[0].ein, "560906609")
        self.assertEqual(results[0].match_method, "curated_override")


class MatcherBuildTest(unittest.TestCase):
    def test_build_master_uses_relation_tier_when_service_code_is_not_recordkeeper_code(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = matcher.DATA_DIR
            matcher.DATA_DIR = Path(temp_dir)
            try:
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "20250101203230NAL0000631587001",
                            "SPONSOR_DFE_NAME": "AMAZON.COM SERVICES,LLC",
                            "SPONS_DFE_EIN": "911986545",
                            "PLAN_NAME": "A SINGLE-EMPLOYER PLAN",
                            "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                            "TYPE_PENSION_BNFT_CODE": "2G",
                            "TOT_PARTCP_BOY_CNT": "1214063",
                        }
                    ]
                ).to_csv(Path(temp_dir) / "F_5500_2023_Latest.csv", index=False)
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "20250101203230NAL0000631587001",
                            "ROW_ORDER": "1",
                            "PROVIDER_OTHER_NAME": "FIDELITY INVESTMENTS INSTITUTIONAL",
                            "PROVIDER_OTHER_RELATION": "RECORDKEEPER",
                        }
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_2023_Latest.csv",
                    index=False,
                )
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "20250101203230NAL0000631587001",
                            "ROW_ORDER": "1",
                            "SERVICE_CODE": "37",
                        }
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_CODES_2023_Latest.csv",
                    index=False,
                )

                master = matcher._build_year_master(2023)
            finally:
                matcher.DATA_DIR = original_data_dir

        self.assertEqual(len(master), 1)
        self.assertEqual(master.loc[0, "EMPLOYER_NORM"], "AMAZON COM SERVICES")
        self.assertEqual(master.loc[0, "TIER"], "TIER1")

    def test_build_master_excludes_defined_benefit_pension_rows(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = matcher.DATA_DIR
            matcher.DATA_DIR = Path(temp_dir)
            try:
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "DB-ACK",
                            "SPONSOR_DFE_NAME": "BANK OF AMERICA CORPORATION",
                            "SPONS_DFE_EIN": "560906609",
                            "PLAN_NAME": "THE BANK OF AMERICA PENSION PLAN",
                            "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                            "TYPE_PENSION_BNFT_CODE": "1A1C1I3H",
                            "TOT_PARTCP_BOY_CNT": "200581",
                        },
                        {
                            "ACK_ID": "DC-ACK",
                            "SPONSOR_DFE_NAME": "BANK OF AMERICA CORPORATION",
                            "SPONS_DFE_EIN": "560906609",
                            "PLAN_NAME": "THE BANK OF AMERICA 401(K) PLAN",
                            "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                            "TYPE_PENSION_BNFT_CODE": "2E2F2G2J",
                            "TOT_PARTCP_BOY_CNT": "263860",
                        },
                    ]
                ).to_csv(Path(temp_dir) / "F_5500_2023_Latest.csv", index=False)
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "DB-ACK",
                            "ROW_ORDER": "1",
                            "PROVIDER_OTHER_NAME": "FIDELITY INVESTMENTS INSTITUTIONAL",
                            "PROVIDER_OTHER_RELATION": "RECORDKEEPER",
                        },
                        {
                            "ACK_ID": "DC-ACK",
                            "ROW_ORDER": "1",
                            "PROVIDER_OTHER_NAME": "MERRILL LYNCH",
                            "PROVIDER_OTHER_RELATION": "RECORDKEEPER",
                        },
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_2023_Latest.csv",
                    index=False,
                )
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "DB-ACK",
                            "ROW_ORDER": "1",
                            "SERVICE_CODE": "64",
                        },
                        {
                            "ACK_ID": "DC-ACK",
                            "ROW_ORDER": "1",
                            "SERVICE_CODE": "64",
                        },
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_CODES_2023_Latest.csv",
                    index=False,
                )

                master = matcher._build_year_master(2023)
            finally:
                matcher.DATA_DIR = original_data_dir

        self.assertEqual(len(master), 1)
        self.assertEqual(master.loc[0, "ACK_ID"], "DC-ACK")
        self.assertEqual(master.loc[0, "PLAN_NAME"], "THE BANK OF AMERICA 401(K) PLAN")
        self.assertEqual(master.loc[0, "RK_CANON"], "Merrill Lynch")


if __name__ == "__main__":
    unittest.main()
