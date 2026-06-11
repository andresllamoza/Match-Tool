import type { AssistantResult, JourneyResponse } from "./types";

const API_BASE = "";
const REQUEST_TIMEOUT_MS = 10_000;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      const detail = err.detail || res.statusText || "Request failed";
      const code = err.code ? ` [${err.code}]` : "";
      throw new Error(`${detail}${code}`);
    }
    return res.json();
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error("Request timed out. Check your connection and try again.");
    }
    throw e;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function startJourney(agent = false): Promise<JourneyResponse> {
  return request(`/api/journey/start?agent=${agent}`, { method: "POST" });
}

export async function getJourney(id: string, agent = false): Promise<JourneyResponse> {
  return request(`/api/journey/${id}?agent=${agent}`);
}

export async function journeyAction(
  id: string,
  body: Record<string, unknown>,
  agent = false
): Promise<JourneyResponse & { assistant?: AssistantResult }> {
  return request(`/api/journey/${id}/action?agent=${agent}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export interface FunnelData {
  total_journeys: number;
  by_state: Record<string, number>;
  by_provider: Record<string, number>;
  by_channel: Record<string, number>;
  stall_points: {
    state: string;
    provider: string | null;
    channel: string | null;
    count: number;
  }[];
  completion_rate: number;
}

export async function getFunnel() {
  return request<FunnelData>("/api/funnel");
}

export async function listProviders() {
  return request<{ providers: string[] }>("/api/providers");
}
