import type { JourneyResponse } from "@/lib/types";
import { DEMO_PROVIDERS, resolveProvider } from "./constants";
import { channelStepCount, type DemoChannel } from "./playbook";
import { buildDemoResponse } from "./buildResponse";
import {
  createInitialDemoState,
  decodeDemoId,
  encodeDemoId,
  snapshotOf,
  type DemoState,
} from "./state";

function commit(state: DemoState): JourneyResponse {
  state.journeyId = encodeDemoId(state);
  return buildDemoResponse(state);
}

function pushHistory(state: DemoState): void {
  state.history = [...(state.history || []), snapshotOf(state)].slice(-24);
}

export function demoHealth() {
  return { status: "ok", mode: "demo" };
}

export function demoProviders() {
  return { providers: [...DEMO_PROVIDERS] };
}

export function demoFunnel() {
  return {
    total_journeys: 128,
    by_state: { provider_unknown: 12, provider_identified: 18, phone_in_progress: 22, complete: 41, in_flight: 15 },
    by_provider: { Fidelity: 52, Vanguard: 24, "Merrill Lynch": 18, Empower: 14 },
    by_channel: { phone: 48, online: 56, forms: 12 },
    stall_points: [{ state: "phone_in_progress", provider: "Fidelity", channel: "phone", count: 6 }],
    completion_rate: 0.32,
  };
}

export function demoStart(): JourneyResponse {
  return commit(createInitialDemoState());
}

export function demoGet(journeyId: string): JourneyResponse | null {
  const state = decodeDemoId(journeyId);
  if (!state) return null;
  return buildDemoResponse(state);
}

export function demoAction(journeyId: string, body: Record<string, unknown>): JourneyResponse | { assistant: unknown } | null {
  const state = decodeDemoId(journeyId);
  if (!state) return null;

  const type = String(body.type || "");

  if (type === "lookup" && typeof body.employer === "string") {
    pushHistory(state);
    state.employer = body.employer.trim();
    state.provider = resolveProvider(state.employer);
    state.state = "provider_identified";
    state.taxType = null;
    return commit(state);
  }

  if (type === "provider_direct" && typeof body.provider === "string") {
    pushHistory(state);
    state.provider = body.provider;
    state.state = "provider_identified";
    state.taxType = "pre_tax";
    return commit(state);
  }

  if (type === "tax_type" && typeof body.tax_type === "string") {
    pushHistory(state);
    state.taxType = body.tax_type;
    state.state = "access_recovered";
    return commit(state);
  }

  if (type === "access" && typeof body.can_login === "boolean") {
    pushHistory(state);
    state.state = body.can_login ? "access_recovered" : "access_blocked";
    return commit(state);
  }

  if (type === "access_recovered") {
    pushHistory(state);
    state.state = "access_recovered";
    return commit(state);
  }

  if (type === "channel" && typeof body.channel === "string") {
    pushHistory(state);
    const ch = body.channel as DemoChannel;
    state.channel = ch;
    state.stepIndex = 0;
    state.totalSteps = channelStepCount(state.provider, ch);
    state.state =
      ch === "phone" ? "phone_in_progress" : ch === "forms" ? "forms_in_progress" : "online_in_progress";
    return commit(state);
  }

  if (type === "step") {
    if (body.outcome === "stuck") {
      state.state = "stuck";
      return commit(state);
    }
    if (state.stepIndex < state.totalSteps - 1) {
      state.stepIndex += 1;
      return commit(state);
    }
    state.state = "initiated";
    state.stepIndex = 0;
    state.totalSteps = 0;
    return commit(state);
  }

  if (type === "confirm_in_flight") {
    state.state = "in_flight";
    return commit(state);
  }

  if (type === "mark_complete") {
    state.state = "complete";
    return commit(state);
  }

  if (type === "resume") {
    if (state.state === "stuck") {
      state.state =
        state.channel === "phone"
          ? "phone_in_progress"
          : state.channel === "forms"
            ? "forms_in_progress"
            : "online_in_progress";
    }
    return commit(state);
  }

  if (type === "go_back" && state.history.length > 0) {
    const prev = state.history[state.history.length - 1];
    state.history = state.history.slice(0, -1);
    state.state = prev.state;
    state.provider = prev.provider;
    state.channel = prev.channel as DemoState["channel"];
    state.stepIndex = prev.step_index;
    state.taxType = prev.tax_fund_type || null;
    return commit(state);
  }

  if (type === "escalate" || type === "handoff") {
    state.state = "escalated";
    return commit(state);
  }

  if (type === "ask" && typeof body.question === "string") {
    const q = body.question.toLowerCase();
    const inScope = ["rollover", "401", "check", "mail", "pensionbee", "ira", "fbo", "payable"].some((w) =>
      q.includes(w)
    );
    return {
      assistant: {
        answer: inScope
          ? "For this rollover, use the verified routing on screen — payee must read PensionBee FBO [your name] with our mailing address. A BeeKeeper can confirm any provider-specific detail."
          : "I can only help with your PensionBee rollover steps and routing on this screen.",
        in_scope: inScope,
        escalation_suggested: !inScope,
      },
    };
  }

  return commit(state);
}
