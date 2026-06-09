from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


class JourneyState(str, Enum):
    PROVIDER_UNKNOWN = "provider_unknown"
    PROVIDER_IDENTIFIED = "provider_identified"
    ACCESS_BLOCKED = "access_blocked"
    ACCESS_RECOVERED = "access_recovered"
    ONLINE_IN_PROGRESS = "online_in_progress"
    PHONE_IN_PROGRESS = "phone_in_progress"
    FORMS_IN_PROGRESS = "forms_in_progress"
    INITIATED = "initiated"
    IN_FLIGHT = "in_flight"
    COMPLETE = "complete"
    STUCK = "stuck"
    ESCALATED = "escalated"


class JourneyPhase(str, Enum):
    FIND = "find"
    ACCESS = "access"
    ROLLOVER = "rollover"
    TRACK = "track"


class JourneyChannel(str, Enum):
    ONLINE = "online"
    PHONE = "phone"
    FORMS = "forms"


class ConfidenceTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Owner(str, Enum):
    USER = "user"
    BEEKEEPER = "beekeeper"
    SYSTEM = "system"


class SourceStatus(str, Enum):
    VERIFIED = "verified"
    RECONSTRUCTED = "reconstructed"


class Mechanism(str, Enum):
    TWO_HOP_ACAT = "two_hop_acat"
    CHECK_TO_PARTICIPANT = "check_to_participant"
    CHECK_TO_PROVIDER = "check_to_provider"


class FunnelStage(str, Enum):
    PROVIDER_IDENTIFIED = "provider_identified"
    ROLLOVER_INITIATED = "rollover_initiated"
    IN_FLIGHT = "in_flight"
    COMPLETED = "completed"


class Step(BaseModel):
    text: str
    owner: Owner
    source_status: SourceStatus


class NextAction(BaseModel):
    action: str
    customer_message: str
    owner: Owner
    source_status: SourceStatus


class EscalationTrigger(BaseModel):
    id: str
    flag: str
    trigger: str
    action: str
    owner: Owner
    source_status: SourceStatus


class FailureMode(BaseModel):
    id: str
    flag: str
    symptom: str
    routing_action: str
    owner: Owner
    source_status: SourceStatus


class LockoutFallback(BaseModel):
    phone: str
    what_to_say: str
    owner: Owner = Owner.USER
    source_status: SourceStatus = SourceStatus.VERIFIED


class AccessRecovery(BaseModel):
    portal_name: str
    info_needed: list[str] = Field(default_factory=list)
    reset_steps: list[Step] = Field(default_factory=list)
    first_time_setup_steps: list[Step] = Field(default_factory=list)
    lockout_fallback: LockoutFallback


class RepQuestion(BaseModel):
    question: str
    answer: str
    source_status: SourceStatus


class CallScript(BaseModel):
    phone: str
    intro: str
    steps: list[Step]
    rep_questions: list[RepQuestion] = Field(default_factory=list)
    check_payable: str
    mailing_address: str


class FormField(BaseModel):
    label: str
    instruction: str
    source_status: SourceStatus


class FormGuidance(BaseModel):
    fields: list[FormField]


class ProviderPlaybook(BaseModel):
    provider: str
    aliases: list[str] = Field(default_factory=list)
    mechanism: Mechanism
    check_destination: str
    forward_step_required: bool
    preferred_path: str
    portal: Optional[str] = None
    sla_days: Optional[int] = None
    sla_source_status: Optional[SourceStatus] = None
    sla_note: Optional[str] = None
    tax_routing_note: str
    next_actions: dict[FunnelStage, NextAction]
    steps: list[Step]
    edge_cases: list[str] = Field(default_factory=list)
    escalation_triggers: list[EscalationTrigger] = Field(default_factory=list)
    failure_modes: list[FailureMode] = Field(default_factory=list)
    access_recovery: AccessRecovery
    call_script: CallScript
    form_guidance: FormGuidance

    @model_validator(mode="after")
    def validate_mechanism_forward_step(self) -> ProviderPlaybook:
        if self.mechanism == Mechanism.CHECK_TO_PARTICIPANT and not self.forward_step_required:
            raise ValueError(
                f"{self.provider}: check_to_participant requires forward_step_required=true"
            )
        if self.mechanism != Mechanism.CHECK_TO_PARTICIPANT and self.forward_step_required:
            raise ValueError(
                f"{self.provider}: only check_to_participant may set forward_step_required=true"
            )
        missing = {s for s in FunnelStage} - set(self.next_actions)
        if missing:
            raise ValueError(f"{self.provider}: missing next_actions for {missing}")
        return self


class TaxRouting(BaseModel):
    pre_tax: str
    roth: str
    automatic_when: str
    conversion_rule: str


class GlobalEscalation(BaseModel):
    id: str
    flag: str
    trigger: str
    action: str
    owner: Owner
    source_status: SourceStatus


class GlobalFailureMode(BaseModel):
    id: str
    flag: str
    symptom: str
    routing_action: str
    owner: Owner
    source_status: SourceStatus


class GlobalRules(BaseModel):
    tax_routing: TaxRouting
    global_escalations: list[GlobalEscalation] = Field(default_factory=list)
    global_failure_modes: list[GlobalFailureMode] = Field(default_factory=list)


class GeneralGuide(BaseModel):
    destination_name: str
    mailing_address: str
    typical_processing_time: str
    account_numbers_policy: str
    employer_vs_provider_note: str
    general_steps: list[Step]
    portal_menu_aliases: list[str] = Field(default_factory=list)
    destination_dropdown_aliases: list[str] = Field(default_factory=list)


class TriggeredAction(BaseModel):
    id: str
    flag: str
    action: str
    owner: Owner
    source_status: SourceStatus
    scope: str


class LookupResult(BaseModel):
    source: str
    provider: Optional[str] = None
    confidence: float = 0.0
    matched_employer_name: Optional[str] = None
    raw_confidence_label: Optional[str] = None


class ComparisonEvent(BaseModel):
    event_type: str = "comparison"
    timestamp: str
    input: str
    matcher_result: Optional[str]
    advizorpro_result: Optional[str]
    agreement: bool
    confidence_tier: ConfidenceTier
    channel: str = "lookup"


class JourneyEvent(BaseModel):
    event_type: str = "journey"
    timestamp: str
    state: JourneyState
    provider: Optional[str]
    channel: Optional[JourneyChannel]
    action: str
    outcome: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class JourneyContext(BaseModel):
    journey_id: str
    state: JourneyState = JourneyState.PROVIDER_UNKNOWN
    provider: Optional[str] = None
    channel: Optional[JourneyChannel] = None
    step_index: int = 0
    flags: dict[str, bool] = Field(default_factory=dict)
    employer_query: Optional[str] = None
    disambiguation_question: Optional[str] = None
    disambiguation_options: list[str] = Field(default_factory=list)


class GuidanceItem(BaseModel):
    text: str
    owner: Owner
    source_status: SourceStatus
    reconstructed: bool = False


class JourneyScreen(BaseModel):
    journey_id: str
    state: JourneyState
    phase: JourneyPhase
    provider: Optional[str]
    channel: Optional[JourneyChannel]
    headline: str
    body: str
    primary_action: str
    secondary_actions: list[str] = Field(default_factory=list)
    guidance: list[GuidanceItem] = Field(default_factory=list)
    edge_cases: list[str] = Field(default_factory=list)
    active_escalations: list[TriggeredAction] = Field(default_factory=list)
    disambiguation_question: Optional[str] = None
    disambiguation_options: list[str] = Field(default_factory=list)
    confidence_tier: Optional[ConfidenceTier] = None
    provenance_warning: Optional[str] = None
    has_reconstructed_content: bool = False
    agent_notes: list[str] = Field(default_factory=list)
    next_beekeeper_script: Optional[str] = None
    sla_note: Optional[str] = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
