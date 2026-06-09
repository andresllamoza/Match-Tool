from __future__ import annotations

import re
from pathlib import Path

import yaml

from .models import (
    EscalationTrigger,
    FailureMode,
    FunnelStage,
    GeneralGuide,
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


def _parse_escalations(data: dict) -> list[GlobalEscalation]:
    return [
        GlobalEscalation(
            id=e["id"],
            flag=e["flag"],
            trigger=e["trigger"],
            action=e["action"],
            owner=_coerce_owner(e["owner"]),
            source_status=_coerce_source(e["source_status"]),
        )
        for e in data.get("global_escalations", [])
    ]


def _parse_global_failures(data: dict) -> list[GlobalFailureMode]:
    return [
        GlobalFailureMode(
            id=f["id"],
            flag=f["flag"],
            symptom=f["symptom"],
            routing_action=f["routing_action"],
            owner=_coerce_owner(f["owner"]),
            source_status=_coerce_source(f["source_status"]),
        )
        for f in data.get("global_failure_modes", [])
    ]


def _parse_general_guide(data: dict) -> GeneralGuide:
    steps = [
        Step(
            text=s["text"],
            owner=_coerce_owner(s["owner"]),
            source_status=_coerce_source(s["source_status"]),
        )
        for s in data.get("general_steps", [])
    ]
    return GeneralGuide(
        destination_name=data["destination_name"],
        mailing_address=data["mailing_address"],
        typical_processing_time=data["typical_processing_time"],
        account_numbers_policy=data["account_numbers_policy"],
        employer_vs_provider_note=data["employer_vs_provider_note"].strip(),
        general_steps=steps,
        portal_menu_aliases=data.get("portal_menu_aliases", []),
        destination_dropdown_aliases=data.get("destination_dropdown_aliases", []),
    )


def _merge_global_rules(matrix_data: dict, general_data: dict) -> GlobalRules:
    tax = matrix_data["tax_routing"]
    escalations = {_e.flag: _e for _e in _parse_escalations(matrix_data)}
    for esc in _parse_escalations(general_data):
        escalations[esc.flag] = esc
    failures = {_f.flag: _f for _f in _parse_global_failures(matrix_data)}
    for fail in _parse_global_failures(general_data):
        failures[fail.flag] = fail
    return GlobalRules(
        tax_routing=TaxRouting(
            pre_tax=tax["pre_tax"],
            roth=tax["roth"],
            automatic_when=tax["automatic_when"],
            conversion_rule=tax["conversion_rule"],
        ),
        global_escalations=list(escalations.values()),
        global_failure_modes=list(failures.values()),
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
    def __init__(
        self,
        knowledge_dir: Path,
        global_rules: GlobalRules,
        providers: dict[str, ProviderPlaybook],
        general_guide: GeneralGuide,
    ):
        self.knowledge_dir = knowledge_dir
        self.global_rules = global_rules
        self.general_guide = general_guide
        self._providers = providers
        self._alias_index: dict[str, str] = {}
        for name, playbook in providers.items():
            self._alias_index[name.lower()] = name
            for alias in playbook.aliases:
                self._alias_index[alias.lower()] = name

    @classmethod
    def from_dir(cls, knowledge_dir: Path | None = None) -> KnowledgeBase:
        root = knowledge_dir or Path(__file__).resolve().parent.parent / "rollover-knowledge-layer"
        matrix_path = root / "Check_Destination_Matrix.md"
        general_path = root / "General_Rollover_Guide.md"
        matrix_data = _parse_front_matter(matrix_path)
        general_data = _parse_front_matter(general_path)
        global_rules = _merge_global_rules(matrix_data, general_data)
        general_guide = _parse_general_guide(general_data)
        providers: dict[str, ProviderPlaybook] = {}
        for path in sorted(root.glob("*_Rollover_Guide.md")):
            if path.name == "General_Rollover_Guide.md":
                continue
            playbook = _parse_provider(_parse_front_matter(path))
            providers[playbook.provider] = playbook
        if not providers:
            raise ValueError(f"No provider guides found in {root}")
        return cls(root, global_rules, providers, general_guide)

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
