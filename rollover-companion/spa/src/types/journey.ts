export type JourneyPhase = "find" | "access" | "rollover" | "track";

export type ScreenId =
  | "find"
  | "find_success"
  | "find_disambiguate"
  | "find_not_covered"
  | "access"
  | "access_recovery"
  | "name"
  | "tax"
  | "channel"
  | "channel_step"
  | "stuck"
  | "escalated"
  | "track"
  | "complete";

export type Channel = "online" | "phone" | "forms";
export type TaxType = "pre_tax" | "roth" | "both";

export interface JourneyContext {
  screen: ScreenId;
  phase: JourneyPhase;
  employerQuery: string;
  matchedEmployer?: string;
  providerId?: string;
  providerName?: string;
  channel?: Channel;
  stepIndex: number;
  stuckCount: number;
  stuckOnStep: number | null;
  firstName: string;
  lastName: string;
  taxType?: TaxType;
  notCovered: boolean;
  disambiguation?: { question: string; options: [string, string] };
  welcomeBack: boolean;
  reconstructed: boolean;
  escalated: boolean;
}

export type JourneyAction =
  | { type: "lookup"; employer: string }
  | { type: "disambiguate"; answer: string }
  | { type: "access"; canLogin: boolean }
  | { type: "recovery_path"; path: "forgot" | "never" }
  | { type: "set_name"; firstName: string; lastName: string }
  | { type: "set_tax"; taxType: TaxType }
  | { type: "set_channel"; channel: Channel }
  | { type: "step_done" }
  | { type: "step_stuck" }
  | { type: "escalate"; reason?: string }
  | { type: "track_continue" }
  | { type: "complete" }
  | { type: "restart" }
  | { type: "dismiss_welcome" }
  | { type: "continue" };

export interface ProviderMock {
  id: string;
  name: string;
  onlineSteps: string[];
  phoneScript: { opening: string; qa: { theyAsk: string; youSay: string }[] };
  formSteps: string[];
  onlineDays: string;
  checkDays: string;
  mailToUser: boolean;
  notaryEdgeCase?: string;
  phoneVerificationNote?: string;
  expressRollover?: boolean;
}

export interface PersistedJourney {
  version: 1;
  savedAt: string;
  ctx: JourneyContext;
}
