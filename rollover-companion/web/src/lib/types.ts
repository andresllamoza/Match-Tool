export type JourneyPhase = "find" | "access" | "rollover" | "track";

export type JourneyState =
  | "provider_unknown"
  | "provider_identified"
  | "access_blocked"
  | "access_recovered"
  | "online_in_progress"
  | "phone_in_progress"
  | "forms_in_progress"
  | "initiated"
  | "in_flight"
  | "complete"
  | "stuck"
  | "escalated";

export interface GuidanceItem {
  text: string;
  owner: string;
  source_status: string;
  reconstructed: boolean;
}

export interface JourneyScreen {
  journey_id: string;
  state: JourneyState;
  phase: JourneyPhase;
  provider: string | null;
  channel: string | null;
  headline: string;
  body: string;
  primary_action: string;
  secondary_actions: string[];
  guidance: GuidanceItem[];
  edge_cases: string[];
  active_escalations: unknown[];
  disambiguation_question: string | null;
  disambiguation_options: string[];
  confidence_tier: string | null;
  provenance_warning: string | null;
  has_reconstructed_content: boolean;
  agent_notes: string[];
  next_beekeeper_script: string | null;
  sla_note: string | null;
}

export interface JourneyContext {
  journey_id: string;
  state: JourneyState;
  provider: string | null;
  channel: string | null;
  step_index: number;
  flags: Record<string, boolean>;
  employer_query: string | null;
  disambiguation_question: string | null;
  disambiguation_options: string[];
}

export interface JourneyResponse {
  context: JourneyContext;
  screen: JourneyScreen;
  step_index: number;
  total_steps: number;
  provider_intel: Record<string, unknown>;
}

export interface AssistantResult {
  answer: string;
  in_scope: boolean;
  escalation_suggested: boolean;
}
