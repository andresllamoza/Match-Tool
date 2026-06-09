from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class FunnelStage(str, Enum):
    PROVIDER_IDENTIFIED = "provider_identified"
    ROLLOVER_INITIATED = "rollover_initiated"
    IN_FLIGHT = "in_flight"
    COMPLETED = "completed"


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


class Step(BaseModel):
    text: str
    owner: Owner
    source_status: SourceStatus


class NextAction(BaseModel):
    action: str
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


class TriggeredAction(BaseModel):
    id: str
    flag: str
    action: str
    owner: Owner
    source_status: SourceStatus
    scope: str  # "global" | "provider"


class RecommendationResponse(BaseModel):
    provider: str
    funnel_stage: FunnelStage
    next_action: NextAction
    preferred_path: str
    mechanism: Mechanism
    check_destination: str
    forward_step_required: bool
    tax_routing_note: str
    sla_days: Optional[int]
    sla_note: Optional[str]
    sla_gap: bool
    steps: list[Step]
    edge_cases: list[str]
    active_escalations: list[TriggeredAction]
    active_failure_modes: list[TriggeredAction]
    has_reconstructed_content: bool
    provenance_warning: Optional[str] = None
