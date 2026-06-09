from __future__ import annotations

import re

from .knowledge import KnowledgeBase
from .models import JourneyState


class ScopedAssistant:
    """Constrained Q&A scoped to current state, provider, and knowledge layer only."""

    OUT_OF_SCOPE_REPLY = (
        "I can only answer questions about your current rollover step and what's in "
        "our provider guides. For anything else, a BeeKeeper can help."
    )
    NO_KNOWLEDGE_REPLY = (
        "I don't have verified guidance for that in our knowledge layer. "
        "A BeeKeeper can help with this."
    )

    def __init__(self, knowledge: KnowledgeBase | None = None):
        self.knowledge = knowledge or KnowledgeBase.from_dir()

    def answer(
        self,
        question: str,
        state: JourneyState,
        provider: str | None,
    ) -> dict:
        q = question.strip().lower()
        if self._is_out_of_scope(q):
            return {
                "answer": self.OUT_OF_SCOPE_REPLY,
                "in_scope": False,
                "escalation_suggested": True,
            }

        snippets = self.knowledge.scoped_content(provider, state.value)
        if provider:
            playbook = self.knowledge.get(provider)
            snippets.extend(playbook.edge_cases)

        match = self._find_best_snippet(q, snippets)
        if match:
            return {
                "answer": match,
                "in_scope": True,
                "escalation_suggested": False,
            }

        if "escalat" in q or "human" in q or "beekeeper" in q:
            return {
                "answer": "Tap 'Talk to a BeeKeeper' to connect with a human.",
                "in_scope": True,
                "escalation_suggested": True,
            }

        return {
            "answer": self.NO_KNOWLEDGE_REPLY,
            "in_scope": False,
            "escalation_suggested": True,
        }

    def _is_out_of_scope(self, question: str) -> bool:
        out_of_scope_patterns = [
            r"\bweather\b",
            r"\bstock\b",
            r"\bcrypto\b",
            r"\btax advice\b",
            r"\bhow much should i\b",
            r"\bbalance is\b",
            r"\bmy ssn\b",
            r"\bpassword is\b",
            r"\binvest in\b",
            r"\brecipe\b",
        ]
        return any(re.search(p, question) for p in out_of_scope_patterns)

    def _find_best_snippet(self, question: str, snippets: list[str]) -> str | None:
        keywords = [w for w in re.findall(r"[a-z]{4,}", question)]
        if not keywords:
            return None
        best: str | None = None
        best_score = 0
        for snippet in snippets:
            snippet_lower = snippet.lower()
            score = sum(1 for k in keywords if k in snippet_lower)
            if score > best_score:
                best_score = score
                best = snippet
        return best if best_score > 0 else None
