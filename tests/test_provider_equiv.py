import unittest

from src.provider_equiv import compare_providers, providers_equivalent


class ProviderEquivTest(unittest.TestCase):
    def test_schwab_and_charles_schwab_equivalent(self):
        self.assertTrue(providers_equivalent("SCHWAB RETIREMENT PLAN SERVICES", "Charles Schwab"))

    def test_prudential_and_empower_equivalent(self):
        self.assertTrue(providers_equivalent("PRUDENTIAL", "Empower Retirement"))
        self.assertTrue(providers_equivalent("PRUDENTIAL", "Empower"))

    def test_fidelity_still_equivalent(self):
        self.assertTrue(providers_equivalent("FIDELITY", "Fidelity Investments"))

    def test_true_mismatch(self):
        self.assertFalse(providers_equivalent("ADP", "Vanguard"))

    def test_compare_no_match(self):
        agree, note = compare_providers("Fidelity", "No match found")
        self.assertFalse(agree)
        self.assertEqual(note, "our_no_match")

    def test_compare_blank_theirs(self):
        agree, note = compare_providers("Not sure", "Fidelity")
        self.assertIsNone(agree)
        self.assertEqual(note, "their_blank")


if __name__ == "__main__":
    unittest.main()
