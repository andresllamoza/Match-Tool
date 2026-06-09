from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import (
    EscalationTrigger,
    FailureMode,
    FunnelStage,
    GlobalEscalation,
    GlobalFailureMode,
    GlobalRules,
    Mechanism,
    NextAction,
    Owner,
    ProviderPlaybook,
    SourceStatus,
    Step,
    TaxRouting,
)

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _parse_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        raise ValueError(f"No YAML front matter in {path}")
    return yaml.safe_load(match.group(1)) or {}


def _coerce_owner(value: str) -> Owner:
    return Owner(value.lower())


def _coerce_source(value: str) -> SourceStatus:
    return SourceStatus(value.lower())


def _coerce_mechanism(value: str) -> Mechanism:
    return Mechanism(value.lower())


def _parse_provider(data: dict) -> ProviderPlaybook:
    next_actions = {
        FunnelStage(stage): NextAction(
            action=action["action"],
            owner=_coerce_owner(action["owner"]),
            source_status=_coerce_source(action["source_status"]),
        )
        for stage, action in data["next_actions"].items()
    }
    steps = [
        Step(
            text=s["text"],
            owner=_coerce_owner(s["owner"]),
            source_status=_coerce_source(s["source_status"]),
        )
        for s in data.get("steps", [])
    ]
    escalations = [
        EscalationTrigger(
            id=e["id"],
            flag=e["flag"],
            trigger=e["trigger"],
            action=e["action"],
            owner=_coerce_owner(e["owner"]),
            source_status=_coerce_source(e["source_status"]),
        )
        for e in data.get("escalation_triggers", [])
    ]
    failures = [
        FailureMode(
            id=f["id"],
            flag=f["flag"],
            symptom=f["symptom"],
            routing_action=f["routing_action"],
            owner=_coerce_owner(f["owner"]),
            source_status=_coerce_source(f["source_status"]),
        )
        for f in data.get("failure_modes", [])
    ]
    sla_status = data.get("sla_source_status")
    return ProviderPlaybook(
        provider=data["provider"],
        aliases=data.get("aliases", []),
        mechanism=_coerce_mechanism(data["mechanism"]),
        check_destination=data["check_destination"],
        forward_step_required=bool(data["forward_step_required"]),
        preferred_path=data["preferred_path"],
        portal=data.get("portal"),
        sla_days=data.get("sla_days"),
        sla_source_status=_coerce_source(sla_status) if sla_status else None,
        sla_note=data.get("sla_note"),
        tax_routing_note=data["tax_routing_note"],
        next_actions=next_actions,
        steps=steps,
        edge_cases=data.get("edge_cases", []),
        escalation_triggers=escalations,
        failure_modes=failures,
    )


def _parse_global(data: dict) -> GlobalRules:
    tax = data["tax_routing"]
    return GlobalRules(
        tax_routing=TaxRouting(
            pre_tax=tax["pre_tax"],
            roth=tax["roth"],
            automatic_when=tax["automatic_when"],
            conversion_rule=tax["conversion_rule"],
        ),
        global_escalations=[
            GlobalEscalation(
                id=e["id"],
                flag=e["flag"],
                trigger=e["trigger"],
                action=e["action"],
                owner=_coerce_owner(e["owner"]),
                source_status=_coerce_source(e["source_status"]),
            )
            for e in data.get("global_escalations", [])
        ],
        global_failure_modes=[
            GlobalFailureMode(
                id=f["id"],
                flag=f["flag"],
                symptom=f["symptom"],
                routing_action=f["routing_action"],
                owner=_coerce_owner(f["owner"]),
                source_status=_coerce_source(f["source_status"]),
            )
            for f in data.get("global_failure_modes", [])
        ],
    )


class KnowledgeBase:
    def __init__(self, knowledge_dir: Path, global_rules: GlobalRules, providers: dict[str, ProviderPlaybook]):
        self.knowledge_dir = knowledge_dir
        self.global_rules = global_rules
        self._providers = providers
        self._alias_index: dict[str, str] = {}
        for name, playbook in providers.items():
            self._alias_index[name.lower()] = name
            for alias in playbook.aliases:
                self._alias_index[alias.lower()] = name

    @classmethod
    def from_dir(cls, knowledge_dir: Path | None = None) -> KnowledgeBase:
        root = knowledge_dir or Path(__file__).resolve().parent.parent / "rollover-knowledge-layer"
        global_path = root / "Check_Destination_Matrix.md"
        global_rules = _parse_global(_parse_front_matter(global_path))
        providers: dict[str, ProviderPlaybook] = {}
        for path in sorted(root.glob("*_Rollover_Guide.md")):
            playbook = _parse_provider(_parse_front_matter(path))
            providers[playbook.provider] = playbook
        if not providers:
            raise ValueError(f"No provider guides found in {root}")
        return cls(root, global_rules, providers)

    def resolve_provider(self, name: str) -> str:
        key = name.strip().lower()
        if key not in self._alias_index:
            raise KeyError(f"Unknown provider: {name!r}")
        return self._alias_index[key]

    def get(self, name: str) -> ProviderPlaybook:
        canonical = self.resolve_provider(name)
        return self._providers[canonical]

    def list_providers(self) -> list[str]:
        return sorted(self._providers)

    def available_flags(self, provider: str | None = None) -> list[dict]:
        """Escalation and failure-mode flags for UI/CLI (global + optional provider)."""
        flags: list[dict] = []
        for esc in self.global_rules.global_escalations:
            flags.append(
                {
                    "flag": esc.flag,
                    "kind": "escalation",
                    "scope": "global",
                    "provider": None,
                    "description": esc.trigger,
                }
            )
        for fail in self.global_rules.global_failure_modes:
            flags.append(
                {
                    "flag": fail.flag,
                    "kind": "failure_mode",
                    "scope": "global",
                    "provider": None,
                    "description": fail.symptom,
                }
            )
        if provider:
            playbook = self.get(provider)
            for esc in playbook.escalation_triggers:
                flags.append(
                    {
                        "flag": esc.flag,
                        "kind": "escalation",
                        "scope": "provider",
                        "provider": playbook.provider,
                        "description": esc.trigger,
                    }
                )
            for fail in playbook.failure_modes:
                flags.append(
                    {
                        "flag": fail.flag,
                        "kind": "failure_mode",
                        "scope": "provider",
                        "provider": playbook.provider,
                        "description": fail.symptom,
                    }
                )
        return flags
