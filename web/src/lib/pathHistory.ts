import type { JourneyResponse } from "./types";

export interface PathHistoryEntry {
  at: string;
  action: string;
  state: string;
  stepIndex: number;
  provider: string | null;
  employer: string | null;
  channel: string | null;
  headline: string;
}

export function buildPathEntry(
  data: JourneyResponse,
  action: string
): PathHistoryEntry {
  return {
    at: new Date().toISOString(),
    action,
    state: data.screen.state,
    stepIndex: data.step_index,
    provider: data.screen.provider || data.context.uncovered_provider || null,
    employer: data.context.employer_query ?? null,
    channel: data.screen.channel ?? null,
    headline: data.screen.headline,
  };
}
