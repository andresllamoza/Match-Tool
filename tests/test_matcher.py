import math
import unittest
from unittest.mock import patch

import pandas as pd

from src import matcher


class MatcherTest(unittest.TestCase):
    def test_first_non_null_skips_pandas_nulls(self) -> None:
        self.assertEqual(matcher._first_non_null(math.nan, "TIER1"), "TIER1")
        self.assertEqual(matcher._first_non_null(pd.NA, "TIER2"), "TIER2")

    def test_match_returns_word_boundary_company_name_match(self) -> None:
        data = pd.DataFrame(
            [
                {
                    "EMPLOYER": "AMAZON.COM SERVICES,LLC",
                    "EMPLOYER_NORM": "AMAZON COM SERVICES",
                    "EMPLOYER_COLLAPSED": "AMAZONCOMSERVICES",
                    "RK_RAW": "FIDELITY INVESTMENTS INSTITUTIONAL",
                    "RK_CANON": "Fidelity Investments",
                    "TIER": "TIER1",
                    "YEAR": "2023",
                    "_n": 1_214_063,
                    "_tier_rank": 1,
                    "PLAN_NAME": "A SINGLE-EMPLOYER PLAN",
                    "PLAN_YEAR_BEGIN_DATE": "2023",
                    "TOT_PARTCP_BOY_CNT": "1214063",
                    "SPONS_DFE_EIN": "911986545",
                }
            ]
        )

        with patch.object(matcher, "load_dol_data", return_value=data):
            results = matcher.match("Amazon")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_employer_name, "AMAZON.COM SERVICES,LLC")
        self.assertEqual(results[0].recordkeeper, "Fidelity Investments")
        self.assertEqual(results[0].confidence, 0.96)


if __name__ == "__main__":
    unittest.main()
