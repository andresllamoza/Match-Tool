export type JourneyPhase = "find" | "access" | "rollover" | "track";

export type JourneyState =
  | "provider_unknown"
  | "provider_identified"
  | "provider_not_covered"
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

export interface RepQuestionView {
  question: string;
  answer: string;
}

export interface ChannelContext {
  channel: string;
  say_this: string;
  phone?: string | null;
  intro?: string | null;
  check_payable?: string | null;
  mailing_address?: string | null;
  form_field_label?: string | null;
  rep_questions: RepQuestionView[];
  step_label?: string | null;
  portal_menu_hints?: string[];
  destination_hints?: string[];
}

export interface TrackContext {
  typical_timeline: string;
  check_destination: string;
  follow_up_days: number;
  nothing_arrived_message: string;
  mechanism_note?: string | null;
}

export interface LookupContext {
  employer_query: string;
  matched_provider: string;
}

export interface ScreenEnrichment {
  mailing_address: string;
  destination_name: string;
  mechanism?: string | null;
  check_destination?: string | null;
  forward_step_required: boolean;
  general_path?: boolean;
  requires_tax_selection: boolean;
  tax_options: { id: string; label: string; hint: string }[];
  channel_context?: ChannelContext | null;
  track?: TrackContext | null;
  lookup?: LookupContext | null;
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
  tax_fund_type?: string | null;
  lookup_confidence_tier?: string | null;
  uncovered_provider?: string | null;
}

export interface JourneyResponse {
  context: JourneyContext;
  screen: JourneyScreen;
  step_index: number;
  total_steps: number;
  enrichment: ScreenEnrichment;
  provider_intel: Record<string, unknown>;
}

export interface AssistantResult {
  answer: string;
  in_scope: boolean;
  escalation_suggested: boolean;
}
