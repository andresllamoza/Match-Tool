import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src import matcher


class DefinedContributionFilterTests(unittest.TestCase):
    def test_defined_contribution_plan_codes_are_detected(self) -> None:
        self.assertTrue(matcher._has_defined_contribution_pension_code("2J"))
        self.assertTrue(matcher._has_defined_contribution_pension_code("2E2J3D"))
        self.assertTrue(matcher._has_defined_contribution_pension_code(" 2L "))

    def test_non_defined_contribution_plan_codes_are_rejected(self) -> None:
        self.assertFalse(matcher._has_defined_contribution_pension_code("1A"))
        self.assertFalse(matcher._has_defined_contribution_pension_code("3D"))
        self.assertFalse(matcher._has_defined_contribution_pension_code(""))
        self.assertFalse(matcher._has_defined_contribution_pension_code(None))


class BuildMasterTests(unittest.TestCase):
    def test_build_master_filters_out_db_pension_rows_before_ranking(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_path = tmp_path / "F_5500_2023_Latest.csv"
            provider_path = tmp_path / "F_SCH_C_PART1_ITEM2_2023_Latest.csv"
            codes_path = tmp_path / "F_SCH_C_PART1_ITEM2_CODES_2023_Latest.csv"
            cache_path = tmp_path / "recordkeeper_master.csv"

            pd.DataFrame(
                [
                    {
                        "ACK_ID": "db-plan",
                        "SPONSOR_DFE_NAME": "Acme Corp",
                        "SPONS_DFE_EIN": "11-1111111",
                        "PLAN_NAME": "ACME PENSION PLAN",
                        "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                        "TYPE_PENSION_BNFT_CODE": "1A",
                        "TOT_PARTCP_BOY_CNT": "50000",
                    },
                    {
                        "ACK_ID": "dc-plan",
                        "SPONSOR_DFE_NAME": "Acme Corp",
                        "SPONS_DFE_EIN": "11-1111111",
                        "PLAN_NAME": "ACME 401(K) PLAN",
                        "PLAN_YEAR_BEGIN_DATE": "2023-01-01",
                        "TYPE_PENSION_BNFT_CODE": "2J3D",
                        "TOT_PARTCP_BOY_CNT": "500",
                    },
                ]
            ).to_csv(main_path, index=False)
            pd.DataFrame(
                [
                    {
                        "ACK_ID": "db-plan",
                        "ROW_ORDER": "1",
                        "PROVIDER_OTHER_NAME": "Pension Administrator",
                        "PROVIDER_OTHER_RELATION": "Recordkeeper",
                    },
                    {
                        "ACK_ID": "dc-plan",
                        "ROW_ORDER": "1",
                        "PROVIDER_OTHER_NAME": "401k Keeper",
                        "PROVIDER_OTHER_RELATION": "Recordkeeper",
                    },
                ]
            ).to_csv(provider_path, index=False)
            pd.DataFrame(
                [
                    {"ACK_ID": "db-plan", "ROW_ORDER": "1", "SERVICE_CODE": "15"},
                    {"ACK_ID": "dc-plan", "ROW_ORDER": "1", "SERVICE_CODE": "15"},
                ]
            ).to_csv(codes_path, index=False)

            paths = {
                "F_5500_2023_Latest": main_path,
                "F_SCH_C_PART1_ITEM2_2023_Latest": provider_path,
                "F_SCH_C_PART1_ITEM2_CODES_2023_Latest": codes_path,
            }

            def fake_ensure_dol_csv(year: int, stem: str) -> Path:
                self.assertEqual(year, 2023)
                return paths[stem]

            with (
                patch.object(matcher, "_configured_years", return_value=(2023,)),
                patch.object(matcher, "_ensure_dol_csv", side_effect=fake_ensure_dol_csv),
                patch.object(matcher, "MASTER_CACHE_PATH", cache_path),
            ):
                master = matcher._build_master()

        self.assertEqual(len(master), 1)
        row = master.iloc[0]
        self.assertEqual(row["PLAN_NAME"], "ACME 401(K) PLAN")
        self.assertEqual(row["TYPE_PENSION_BNFT_CODE"], "2J3D")
        self.assertEqual(row["RK_RAW"], "401K KEEPER")


if __name__ == "__main__":
    unittest.main()
