import unittest

from src import financial_notes
from src.matcher import MatchResult, canonicalize_employer, match


class FinancialNotesRegistryTest(unittest.TestCase):
    def test_registry_entry_for_nike(self):
        entry = financial_notes.registry_entry("Nike")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["recordkeeper"], "Fidelity Workplace Services, LLC")

    def test_default_reason_includes_trustee_clarification(self):
        entry = financial_notes.registry_entry("NIKE")
        reason = financial_notes.default_notes_reason(entry)
        self.assertIn("Notes to Financial Statements", reason)
        self.assertIn("Northern Trust", reason)


class FinancialNotesMatchTest(unittest.TestCase):
    def test_match_nike_uses_notes_registry(self):
        results = match("Nike", top_n=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].recordkeeper, "Fidelity Workplace Services, LLC")
        self.assertEqual(results[0].match_method, "financial_statement_notes")

    def test_weak_tier_detection(self):
        self.assertTrue(financial_notes.dol_tier_is_weak("TIER1_ITEM1"))
        self.assertFalse(financial_notes.dol_tier_is_weak("TIER1"))


class FinancialNotesHintTest(unittest.TestCase):
    def test_large_plan_threshold(self):
        self.assertTrue(financial_notes.is_large_plan_participants(5000))
        self.assertFalse(financial_notes.is_large_plan_participants(4999))

    def test_verification_hint_text(self):
        self.assertIn("Notes to Financial Statements", financial_notes.verification_hint())


if __name__ == "__main__":
    unittest.main()
