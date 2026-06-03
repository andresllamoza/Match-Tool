import os
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
        disney_norm = matcher.canonicalize_employer("TWDC Enterprises 18 Corp.")
        disney_plan_norm = matcher.canonicalize_employer("Disney Retirement Savings Plan")
        disney_hourly_plan_norm = matcher.canonicalize_employer(
            "Disney Hourly Savings and Investment Plan"
        )
        citigroup_norm = matcher.canonicalize_employer("Citigroup Inc")
        citi_trends_norm = matcher.canonicalize_employer("Citi Trends Inc")
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
                    "PLAN_YEAR_BEGIN_DATE": None,
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
                    "EMPLOYER": "TWDC ENTERPRISES 18 CORP.",
                    "EMPLOYER_NORM": disney_norm,
                    "EMPLOYER_COLLAPSED": disney_norm.replace(" ", ""),
                    "PLAN_NORM": disney_plan_norm,
                    "PLAN_COLLAPSED": disney_plan_norm.replace(" ", ""),
                    "RK_RAW": "FIDELITY INVESTMENTS INSTITUTIONAL",
                    "RK_CANON": "Fidelity Investments",
                    "TIER": "TIER1",
                    "YEAR": "2024",
                    "_n": 44099,
                    "_tier_rank": 1,
                    "PLAN_NAME": "DISNEY RETIREMENT SAVINGS PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2024-01-01",
                    "TOT_PARTCP_BOY_CNT": "44099",
                    "SPONS_DFE_EIN": "95-4545390",
                },
                {
                    "EMPLOYER": "TWDC ENTERPRISES 18 CORP.",
                    "EMPLOYER_NORM": disney_norm,
                    "EMPLOYER_COLLAPSED": disney_norm.replace(" ", ""),
                    "PLAN_NORM": disney_hourly_plan_norm,
                    "PLAN_COLLAPSED": disney_hourly_plan_norm.replace(" ", ""),
                    "RK_RAW": "FIDELITY INVESTMENTS INSTITUTIONAL",
                    "RK_CANON": "Fidelity Investments",
                    "TIER": "TIER1",
                    "YEAR": "2024",
                    "_n": 111954,
                    "_tier_rank": 1,
                    "PLAN_NAME": "DISNEY HOURLY SAVINGS AND INVESTMENT PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2024-01-01",
                    "TOT_PARTCP_BOY_CNT": "111954",
                    "SPONS_DFE_EIN": "95-4545390",
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
                },
                {
                    "EMPLOYER": "CITIGROUP INC",
                    "EMPLOYER_NORM": citigroup_norm,
                    "EMPLOYER_COLLAPSED": citigroup_norm.replace(" ", ""),
                    "RK_RAW": "EMPOWER",
                    "RK_CANON": "Empower Retirement",
                    "TIER": "TIER1",
                    "YEAR": "2024",
                    "_n": 210000,
                    "_tier_rank": 1,
                    "PLAN_NAME": "CITIGROUP 401(K) PLAN",
                    "PLAN_NORM": matcher.canonicalize_employer("Citigroup 401(k) Plan"),
                    "PLAN_COLLAPSED": matcher.canonicalize_employer(
                        "Citigroup 401(k) Plan"
                    ).replace(" ", ""),
                    "PLAN_YEAR_BEGIN_DATE": "2024-01-01",
                    "TOT_PARTCP_BOY_CNT": "210000",
                    "SPONS_DFE_EIN": "13-3214963",
                },
                {
                    "EMPLOYER": "CITI TRENDS INC",
                    "EMPLOYER_NORM": citi_trends_norm,
                    "EMPLOYER_COLLAPSED": citi_trends_norm.replace(" ", ""),
                    "RK_RAW": "VOYA",
                    "RK_CANON": "Voya",
                    "TIER": "TIER1",
                    "YEAR": "2024",
                    "_n": 2500,
                    "_tier_rank": 1,
                    "PLAN_NAME": "CITI TRENDS 401(K) PLAN",
                    "PLAN_NORM": matcher.canonicalize_employer("Citi Trends 401(k) Plan"),
                    "PLAN_COLLAPSED": matcher.canonicalize_employer(
                        "Citi Trends 401(k) Plan"
                    ).replace(" ", ""),
                    "PLAN_YEAR_BEGIN_DATE": "2024-01-01",
                    "TOT_PARTCP_BOY_CNT": "2500",
                    "SPONS_DFE_EIN": "52-2150697",
                },
                {
                    "EMPLOYER": "ALPHA RETAIL LLC",
                    "EMPLOYER_NORM": matcher.canonicalize_employer("Alpha Retail LLC"),
                    "EMPLOYER_COLLAPSED": matcher.canonicalize_employer(
                        "Alpha Retail LLC"
                    ).replace(" ", ""),
                    "RK_RAW": "VOYA",
                    "RK_CANON": "Voya",
                    "TIER": "TIER1",
                    "YEAR": "2023",
                    "_n": 500,
                    "_tier_rank": 1,
                    "PLAN_NAME": "ALPHA RETAIL 401K PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                    "TOT_PARTCP_BOY_CNT": "500",
                    "SPONS_DFE_EIN": "11-1111111",
                },
                {
                    "EMPLOYER": "OMEGA ALPHA LLC",
                    "EMPLOYER_NORM": matcher.canonicalize_employer("Omega Alpha LLC"),
                    "EMPLOYER_COLLAPSED": matcher.canonicalize_employer(
                        "Omega Alpha LLC"
                    ).replace(" ", ""),
                    "RK_RAW": "EMPOWER",
                    "RK_CANON": "Empower Retirement",
                    "TIER": "TIER1",
                    "YEAR": "2023",
                    "_n": 750,
                    "_tier_rank": 1,
                    "PLAN_NAME": "OMEGA ALPHA 401K PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                    "TOT_PARTCP_BOY_CNT": "750",
                    "SPONS_DFE_EIN": "22-2222222",
                },
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

    def test_match_finds_disney_query_in_plan_name(self):
        results = self.matcher.match("disney", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "TWDC ENTERPRISES 18 CORP.")
        self.assertEqual(results[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(results[0].plan_name, "DISNEY RETIREMENT SAVINGS PLAN")
        self.assertEqual(results[0].ein, "95-4545390")
        self.assertEqual(results[0].match_method, "curated_override")

    def test_match_overrides_walt_disney_company_alias(self):
        results = self.matcher.match("The Walt Disney Company", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "TWDC ENTERPRISES 18 CORP.")
        self.assertEqual(results[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(results[0].plan_name, "DISNEY RETIREMENT SAVINGS PLAN")
        self.assertEqual(results[0].match_method, "curated_override")

    def test_match_finds_specific_disney_plan_query(self):
        results = self.matcher.match("Disney Retirement Savings Plan", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "TWDC ENTERPRISES 18 CORP.")
        self.assertEqual(results[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(results[0].plan_name, "DISNEY RETIREMENT SAVINGS PLAN")
        self.assertEqual(results[0].match_method, "plan_word_boundary")

    def test_match_uses_year_when_plan_begin_date_is_missing(self):
        results = self.matcher.match("Acme Inc", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].plan_year, "2023")

    def test_suggest_employers_returns_existing_partial_matches(self):
        suggestions = self.matcher.suggest_employers("ama", limit=3)

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].employer_name, "AMAZON.COM SERVICES, LLC")
        self.assertEqual(suggestions[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(suggestions[0].match_method, "prefix")

    def test_suggest_employers_includes_secondary_details(self):
        suggestions = self.matcher.suggest_employers("ama", limit=3)

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].ein, "91-1986545")
        self.assertEqual(suggestions[0].plan_participants, 1214063)

    def test_suggest_employers_ranks_prefix_before_substring(self):
        suggestions = self.matcher.suggest_employers("alpha", limit=2)

        self.assertEqual(
            [suggestion.match_method for suggestion in suggestions],
            ["prefix", "contains"],
        )
        self.assertEqual(suggestions[0].employer_name, "ALPHA RETAIL LLC")
        self.assertEqual(suggestions[1].employer_name, "OMEGA ALPHA LLC")

    def test_suggest_employers_skips_short_queries(self):
        suggestions = self.matcher.suggest_employers("am", limit=3)

        self.assertEqual(suggestions, [])

    def test_suggest_employers_skips_single_character_queries(self):
        suggestions = self.matcher.suggest_employers("a", limit=3)

        self.assertEqual(suggestions, [])

    def test_suggest_employers_skips_generic_business_terms(self):
        suggestions = self.matcher.suggest_employers("services", limit=3)

        self.assertEqual(suggestions, [])

    def test_suggest_employers_returns_related_token_matches(self):
        suggestions = self.matcher.suggest_employers("america", limit=3)

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].employer_name, "BANK OF AMERICA CORPORATION")
        self.assertEqual(suggestions[0].match_method, "contains")

    def test_suggest_employers_returns_plan_name_matches(self):
        suggestions = self.matcher.suggest_employers("disney", limit=3)

        self.assertGreaterEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0].employer_name, "TWDC ENTERPRISES 18 CORP.")
        self.assertEqual(suggestions[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(suggestions[0].match_method, "plan_contains")

    def test_match_uses_citi_brand_alias_for_citigroup(self):
        results = self.matcher.match("Citi", top_n=2)

        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "CITIGROUP INC")
        self.assertEqual(results[0].recordkeeper, "Empower Retirement")
        self.assertEqual(results[0].match_method, "brand_alias")

    def test_suggest_employers_ranks_citigroup_before_citi_trends_for_citi(self):
        suggestions = self.matcher.suggest_employers("Citi", limit=2)

        self.assertGreaterEqual(len(suggestions), 2)
        self.assertEqual(suggestions[0].employer_name, "CITIGROUP INC")
        self.assertEqual(suggestions[0].match_method, "brand_alias")
        self.assertEqual(suggestions[1].employer_name, "CITI TRENDS INC")

    def test_match_overrides_bank_of_america_pension_row_to_merrill(self):
        results = self.matcher.match("bank of america", top_n=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "BANK OF AMERICA CORPORATION")
        self.assertEqual(results[0].recordkeeper, "Merrill Lynch")
        self.assertEqual(results[0].plan_name, "THE BANK OF AMERICA 401(K) PLAN")
        self.assertEqual(results[0].ein, "560906609")
        self.assertEqual(results[0].match_method, "curated_override")


class MatcherBuildTest(unittest.TestCase):
    def test_configured_years_defaults_to_2020_through_2024(self):
        from src import matcher

        original_years = os.environ.get("DOL_YEARS")
        try:
            os.environ.pop("DOL_YEARS", None)

            self.assertEqual(matcher._configured_years(), (2024, 2023, 2022, 2021, 2020))
        finally:
            if original_years is None:
                os.environ.pop("DOL_YEARS", None)
            else:
                os.environ["DOL_YEARS"] = original_years

    def test_build_master_preserves_plan_level_rows_for_plan_name_matching(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = matcher.DATA_DIR
            original_years = os.environ.get("DOL_YEARS")
            matcher.DATA_DIR = Path(temp_dir)
            os.environ["DOL_YEARS"] = "2023"
            try:
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "DISNEY-RETIREMENT-ACK",
                            "SPONSOR_DFE_NAME": "TWDC ENTERPRISES 18 CORP.",
                            "SPONS_DFE_EIN": "954545390",
                            "PLAN_NAME": "DISNEY RETIREMENT SAVINGS PLAN",
                            "PLAN_YEAR_BEGIN_DATE": "2024-01-01",
                            "TYPE_PENSION_BNFT_CODE": "2A2E2F2G2T3F3H",
                            "TOT_PARTCP_BOY_CNT": "44099",
                        },
                        {
                            "ACK_ID": "DISNEY-HOURLY-ACK",
                            "SPONSOR_DFE_NAME": "TWDC ENTERPRISES 18 CORP.",
                            "SPONS_DFE_EIN": "954545390",
                            "PLAN_NAME": "DISNEY HOURLY SAVINGS AND INVESTMENT PLAN",
                            "PLAN_YEAR_BEGIN_DATE": "2024-01-01",
                            "TYPE_PENSION_BNFT_CODE": "2E2F2G2J2K2O2T3F3H",
                            "TOT_PARTCP_BOY_CNT": "111954",
                        },
                    ]
                ).to_csv(Path(temp_dir) / "F_5500_2023_Latest.csv", index=False)
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "DISNEY-RETIREMENT-ACK",
                            "ROW_ORDER": "1",
                            "PROVIDER_OTHER_NAME": "FIDELITY INVESTMENTS INSTITUTIONAL",
                            "PROVIDER_OTHER_RELATION": "NONE",
                        },
                        {
                            "ACK_ID": "DISNEY-HOURLY-ACK",
                            "ROW_ORDER": "1",
                            "PROVIDER_OTHER_NAME": "FIDELITY INVESTMENTS INSTITUTIONAL",
                            "PROVIDER_OTHER_RELATION": "NONE",
                        },
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_2023_Latest.csv",
                    index=False,
                )
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "DISNEY-RETIREMENT-ACK",
                            "ROW_ORDER": "1",
                            "SERVICE_CODE": "64",
                        },
                        {
                            "ACK_ID": "DISNEY-HOURLY-ACK",
                            "ROW_ORDER": "1",
                            "SERVICE_CODE": "64",
                        },
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_CODES_2023_Latest.csv",
                    index=False,
                )

                master = matcher._build_master()
            finally:
                matcher.DATA_DIR = original_data_dir
                if original_years is None:
                    os.environ.pop("DOL_YEARS", None)
                else:
                    os.environ["DOL_YEARS"] = original_years

        self.assertEqual(len(master), 2)
        self.assertEqual(
            sorted(master["PLAN_NORM"].tolist()),
            [
                "DISNEY HOURLY SAVINGS INVESTMENT PLAN",
                "DISNEY RETIREMENT SAVINGS PLAN",
            ],
        )

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

    def test_build_master_includes_no_code_401k_master_trust_rows(self):
        from src import matcher

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data_dir = matcher.DATA_DIR
            matcher.DATA_DIR = Path(temp_dir)
            try:
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "TARGET-TRUST-ACK",
                            "SPONSOR_DFE_NAME": "TARGET CORPORATION",
                            "SPONS_DFE_EIN": "410215170",
                            "PLAN_NAME": "TARGET CORPORATION 401(K) MASTER TRUST",
                            "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                            "TYPE_PENSION_BNFT_CODE": "",
                            "TOT_PARTCP_BOY_CNT": "",
                        }
                    ]
                ).to_csv(Path(temp_dir) / "F_5500_2023_Latest.csv", index=False)
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "TARGET-TRUST-ACK",
                            "ROW_ORDER": "1",
                            "PROVIDER_OTHER_NAME": "ALIGHT SOLUTIONS LLC",
                            "PROVIDER_OTHER_RELATION": "CONTRACT ADMINISTRATOR",
                        }
                    ]
                ).to_csv(
                    Path(temp_dir) / "F_SCH_C_PART1_ITEM2_2023_Latest.csv",
                    index=False,
                )
                pd.DataFrame(
                    [
                        {
                            "ACK_ID": "TARGET-TRUST-ACK",
                            "ROW_ORDER": "1",
                            "SERVICE_CODE": "13",
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
        self.assertEqual(master.loc[0, "EMPLOYER_NORM"], "TARGET")
        self.assertEqual(master.loc[0, "PLAN_NAME"], "TARGET CORPORATION 401(K) MASTER TRUST")
        self.assertEqual(master.loc[0, "RK_CANON"], "Alight Solutions")


if __name__ == "__main__":
    unittest.main()
