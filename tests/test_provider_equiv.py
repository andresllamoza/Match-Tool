import unittest

from src.provider_equiv import (
    compare_providers,
    normalize_for_playbook,
    playbook_provider_hint,
    providers_equivalent,
)


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

    def test_playbook_hint_fidelity_investments(self):
        self.assertEqual(playbook_provider_hint("Fidelity Investments"), "Fidelity")

    def test_playbook_hint_empower_retirement(self):
        self.assertEqual(playbook_provider_hint("Empower Retirement"), "Empower")

    def test_playbook_hint_alight_not_in_playbook(self):
        self.assertIsNone(playbook_provider_hint("Alight Solutions"))

    def test_normalize_for_playbook_prefers_canonical(self):
        self.assertEqual(normalize_for_playbook("Fidelity Workplace Services, LLC"), "Fidelity")
        self.assertEqual(normalize_for_playbook("Alight Solutions"), "Alight Solutions")


if __name__ == "__main__":
    unittest.main()
