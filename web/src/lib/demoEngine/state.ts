import type { HistorySnapshot, JourneyState } from "@/lib/types";

export interface DemoState {
  v: 1;
  journeyId: string;
  state: JourneyState;
  employer: string | null;
  provider: string | null;
  channel: "online" | "phone" | "forms" | null;
  stepIndex: number;
  totalSteps: number;
  taxType: string | null;
  history: HistorySnapshot[];
}

const PREFIX = "demo_v1_";

export function isDemoJourneyId(id: string): boolean {
  return id.startsWith(PREFIX);
}

export function encodeDemoId(state: DemoState): string {
  const payload = Buffer.from(JSON.stringify(state), "utf8").toString("base64url");
  return `${PREFIX}${payload}`;
}

export function decodeDemoId(id: string): DemoState | null {
  if (!id.startsWith(PREFIX)) return null;
  try {
    const raw = Buffer.from(id.slice(PREFIX.length), "base64url").toString("utf8");
    const parsed = JSON.parse(raw) as DemoState;
    if (parsed.v !== 1) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function createInitialDemoState(): DemoState {
  const base: DemoState = {
    v: 1,
    journeyId: "",
    state: "provider_unknown",
    employer: null,
    provider: null,
    channel: null,
    stepIndex: 0,
    totalSteps: 0,
    taxType: null,
    history: [],
  };
  base.journeyId = encodeDemoId(base);
  return base;
}

export function snapshotOf(s: DemoState): HistorySnapshot {
  return {
    state: s.state,
    provider: s.provider,
    channel: s.channel,
    step_index: s.stepIndex,
    flags: {},
    tax_fund_type: s.taxType,
  };
}
