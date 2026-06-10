import type { PathHistoryEntry } from "./pathHistory";
import type { JourneyResponse } from "./types";

const STORAGE_KEY = "pb_rollover_journey_v1";
const MAX_PATH_ENTRIES = 24;

export interface PersistedJourneySession {
  version: 1;
  savedAt: string;
  journeyId: string;
  snapshot: JourneyResponse;
  employerInput: string;
  showProviderPicker: boolean;
  pathHistory?: PathHistoryEntry[];
}

export { MAX_PATH_ENTRIES };

const TERMINAL_STATES = new Set(["complete", "escalated"]);

export function isResumableSession(data: JourneyResponse): boolean {
  return !TERMINAL_STATES.has(data.screen.state);
}

export function saveJourneySession(session: Omit<PersistedJourneySession, "version" | "savedAt">) {
  if (typeof window === "undefined") return;
  const payload: PersistedJourneySession = {
    version: 1,
    savedAt: new Date().toISOString(),
    ...session,
  };
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch {
    /* storage full or private mode */
  }
}

export function loadJourneySession(): PersistedJourneySession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as PersistedJourneySession;
    if (parsed.version !== 1 || !parsed.snapshot?.context?.journey_id) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function clearJourneySession() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

export function resumeProviderLabel(data: JourneyResponse): string {
  return (
    data.screen.provider ||
    data.context.uncovered_provider ||
    data.context.employer_query ||
    "your"
  );
}
