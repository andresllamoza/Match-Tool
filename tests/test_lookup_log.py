import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.lookup_log import append_lookup_attempt, read_lookup_attempts
from src.matcher import MatchResult


def write_amazon_dol_fixture(data_dir: Path) -> None:
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
    ).to_csv(data_dir / "F_5500_2023_Latest.csv", index=False)
    pd.DataFrame(
        [
            {
                "ACK_ID": "20250101203230NAL0000631587001",
                "ROW_ORDER": "1",
                "PROVIDER_OTHER_NAME": "FIDELITY INVESTMENTS INSTITUTIONAL",
                "PROVIDER_OTHER_RELATION": "RECORDKEEPER",
            }
        ]
    ).to_csv(data_dir / "F_SCH_C_PART1_ITEM2_2023_Latest.csv", index=False)
    pd.DataFrame(
        [
            {
                "ACK_ID": "20250101203230NAL0000631587001",
                "ROW_ORDER": "1",
                "SERVICE_CODE": "37",
            }
        ]
    ).to_csv(data_dir / "F_SCH_C_PART1_ITEM2_CODES_2023_Latest.csv", index=False)


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


class MatcherBuildTest(unittest.TestCase):
    def test_build_master_uses_relation_tier_when_service_code_is_not_recordkeeper_code(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = matcher.DATA_DIR
            matcher.DATA_DIR = Path(temp_dir)
            try:
                write_amazon_dol_fixture(Path(temp_dir))

                master = matcher._build_year_master(2023)
            finally:
                matcher.DATA_DIR = original_data_dir

        self.assertEqual(len(master), 1)
        self.assertEqual(master.loc[0, "EMPLOYER_NORM"], "AMAZON COM SERVICES")
        self.assertEqual(master.loc[0, "TIER"], "TIER1")

    def test_load_dol_data_rebuilds_stale_unversioned_cache(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            original_data_dir = matcher.DATA_DIR
            original_cache = matcher._DATAFRAME_CACHE
            matcher.DATA_DIR = data_dir
            matcher._DATAFRAME_CACHE = None
            try:
                pd.DataFrame(
                    [
                        {
                            "EMPLOYER": "STALE INC",
                            "EMPLOYER_NORM": "STALE",
                            "EMPLOYER_COLLAPSED": "STALE",
                            "RK_RAW": "OLD RECORDKEEPER",
                            "RK_CANON": "Old Recordkeeper",
                            "TIER": "TIER1",
                            "YEAR": "2023",
                            "_n": 1,
                            "_tier_rank": 1,
                            "PLAN_NAME": "STALE PLAN",
                            "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                            "TOT_PARTCP_BOY_CNT": "1",
                            "SPONS_DFE_EIN": "00-0000000",
                        }
                    ]
                ).to_csv(data_dir / matcher.MASTER_CACHE_FILENAME, index=False)
                write_amazon_dol_fixture(data_dir)

                loaded = matcher.load_dol_data()
                version_file_exists = (
                    data_dir / matcher.MASTER_CACHE_VERSION_FILENAME
                ).exists()
            finally:
                matcher.DATA_DIR = original_data_dir
                matcher._DATAFRAME_CACHE = original_cache

        self.assertEqual(loaded.loc[0, "EMPLOYER"], "AMAZON.COM SERVICES,LLC")
        self.assertTrue(version_file_exists)

    def test_match_finds_literal_amazon_after_building_data_files(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = matcher.DATA_DIR
            original_cache = matcher._DATAFRAME_CACHE
            matcher.DATA_DIR = Path(temp_dir)
            matcher._DATAFRAME_CACHE = None
            try:
                write_amazon_dol_fixture(Path(temp_dir))

                results = matcher.match("amazon", top_n=1)
            finally:
                matcher.DATA_DIR = original_data_dir
                matcher._DATAFRAME_CACHE = original_cache

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "AMAZON.COM SERVICES,LLC")
        self.assertEqual(results[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(results[0].match_method, "word_boundary")


if __name__ == "__main__":
    unittest.main()
